"""Tests for the real depth backends (``sphereforge.models``).

These tests exercise the ERP-native ``dap`` backend and the Depth Anything V2
wrapper **without** downloading weights or touching the GPU:

- the panorama-rig renderer and ERP fusion are checked against an analytic
  plane-depth field,
- the wrappers are checked for input validation, lazy loading, and the
  ``estimate_depth``/``estimate_depth_batch`` contract using a mocked model.
"""

from __future__ import annotations

import math
from unittest.mock import MagicMock

import numpy as np
import pytest

from sphereforge.models.dap_model import (
    DAPModel,
    _fuse_disparity_views_to_erp,
    _fuse_views_to_erp,
    _render_rig_views,
)
from sphereforge.models.depth_anything_v2 import DepthAnythingV2Model, disparity_to_depth
from sphereforge.stages.stage02_cubemap.cubemap import _make_rotation_matrix

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _erp_directions(height: int, width: int) -> np.ndarray:
    """World direction for every ERP pixel centre (Stage 2 convention)."""
    phi = (np.arange(width) + 0.5) / width * 2.0 * math.pi - math.pi
    theta = math.pi / 2.0 - (np.arange(height) + 0.5) / height * math.pi
    phi_grid, theta_grid = np.meshgrid(phi, theta)
    cos_theta = np.cos(theta_grid)
    return np.stack(
        [
            np.sin(phi_grid) * cos_theta,
            np.sin(theta_grid),
            -np.cos(phi_grid) * cos_theta,
        ],
        axis=-1,
    )


def _view_perspective_depths(
    angles: list[tuple[float, float]], res: int, fov: float, plane_y: float = -1.5
) -> list[np.ndarray]:
    """Exact ground-plane depth, as perspective depth, for each rig view.

    The plane is horizontal (a floor at ``y = plane_y``), which is what a 360
    camera in a room actually sees: every downward ray hits it at a finite
    distance, so there is no grazing-angle singularity.
    """
    focal = res / (2.0 * math.tan(math.radians(fov) / 2.0))
    center = res / 2.0
    uu, vv = np.meshgrid(np.arange(res, dtype=np.float64), np.arange(res, dtype=np.float64))
    dx = (uu - center) / focal
    dy = (vv - center) / focal
    dz = np.ones_like(dx)
    norms = np.sqrt(dx * dx + dy * dy + dz * dz)
    dirs_cam = np.stack([dx / norms, dy / norms, dz / norms], axis=-1)

    depths = []
    for yaw_deg, pitch_deg in angles:
        rotation = _make_rotation_matrix(yaw_deg, pitch_deg)
        dirs_world = np.einsum("ij,...j->...i", rotation.T, dirs_cam)
        y = dirs_world[..., 1]
        radial = np.zeros(dirs_world.shape[:-1], dtype=np.float64)
        down = y < -1e-6
        radial[down] = abs(plane_y) / (-y[down])
        perspective = radial / np.sqrt(1.0 + dx**2 + dy**2)
        depths.append(perspective.astype(np.float32))
    return depths


def _ground_plane_radial_depth(directions: np.ndarray, plane_y: float = -1.5) -> np.ndarray:
    """Radial distance to a floor plane; NaN where the ray points upward."""
    y = directions[..., 1]
    out = np.full(directions.shape[:-1], np.nan, dtype=np.float64)
    down = y < -1e-6
    out[down] = abs(plane_y) / (-y[down])
    return out


# ---------------------------------------------------------------------------
# ERP fusion
# ---------------------------------------------------------------------------


class TestErpFusion:
    """Geometry tests for the panorama-rig → ERP fusion."""

    def test_render_rig_view_count_and_shape(self) -> None:
        """The rig renders yaw_steps * len(pitches) square views."""
        erp = np.zeros((64, 128, 3), dtype=np.uint8)
        views, angles = _render_rig_views(
            erp, yaw_steps=8, pitches=(-45.0, 0.0, 45.0), fov_deg=90.0, view_res=32
        )
        assert len(views) == 24
        assert len(angles) == 24
        assert all(v.shape == (32, 32, 3) for v in views)

    def test_render_rig_center_pixel_matches_erp(self) -> None:
        """The centre pixel of a view samples the ERP pixel at its yaw/pitch."""
        h, w = 64, 128
        uu, vv = np.meshgrid(np.arange(w), np.arange(h))
        erp = np.stack([uu, vv, np.zeros_like(uu)], axis=-1).astype(np.uint8)

        views, angles = _render_rig_views(
            erp, yaw_steps=4, pitches=(0.0,), fov_deg=90.0, view_res=33
        )
        for view, (yaw_deg, _pitch) in zip(views, angles, strict=True):
            center = view.shape[0] // 2
            u = int(view[center, center, 0])
            expected_u = round(yaw_deg / 360.0 * w) % w
            assert abs(u - expected_u) <= 1

    def test_fusion_recovers_plane_depth(self) -> None:
        """Fusing exact view depths reproduces the analytic ground-plane depth."""
        h, w = 64, 128
        angles = [(360.0 * s / 8, p) for p in (-45.0, 0.0, 45.0) for s in range(8)]
        view_depths = _view_perspective_depths(angles, res=48, fov=90.0)
        fused = _fuse_views_to_erp(view_depths, angles, fov_deg=90.0, erp_height=h, erp_width=w)

        truth = _ground_plane_radial_depth(_erp_directions(h, w))
        valid = (fused > 0) & np.isfinite(truth)
        # Every downward ERP ray must be covered by the rig.
        assert valid.sum() >= np.isfinite(truth).sum() - 1
        rel_err = np.abs(fused[valid] - truth[valid]) / truth[valid]
        assert float(np.median(rel_err)) < 0.02

    def test_fusion_has_no_seams_at_yaw_boundaries(self) -> None:
        """Neighbouring ERP columns must not jump where views meet."""
        h, w = 64, 256
        angles = [(360.0 * s / 8, -45.0) for s in range(8)]
        view_depths = _view_perspective_depths(angles, res=48, fov=90.0)
        fused = _fuse_views_to_erp(view_depths, angles, fov_deg=90.0, erp_height=h, erp_width=w)
        # Row near the bottom of the ERP image: floor straight below the camera.
        row = fused[int(h * 0.85)]
        valid = row > 0
        assert valid.all()
        diffs = np.abs(np.diff(row))
        assert float(np.max(diffs)) < 0.1 * float(np.median(row))

    def test_fusion_rejects_empty_input(self) -> None:
        """Fusing nothing is an error, not a silent zero map."""
        with pytest.raises(ValueError, match="empty"):
            _fuse_views_to_erp([], [], fov_deg=90.0, erp_height=8, erp_width=16)


# ---------------------------------------------------------------------------
# DAPModel
# ---------------------------------------------------------------------------


class TestDAPModel:
    """Contract tests for the ERP-native DAP backend."""

    def test_defaults(self) -> None:
        """Defaults describe a rig-fusion backend."""
        model = DAPModel()
        assert model.backend_kind == "rig_fusion"
        assert model.yaw_steps == 8
        # The pole rings are required: without them the nadir and zenith are
        # only seen at grazing angles and come out ~3x too far.
        assert model.pitches == (-90.0, -45.0, 0.0, 45.0, 90.0)
        assert model.is_stub is False

    def test_erp_native_backend_kind(self, tmp_path) -> None:
        """Supplying ERP weights switches the backend kind."""
        model = DAPModel(erp_weights=tmp_path)
        assert model.backend_kind == "erp_native"

    def test_invalid_rig_params_raise(self) -> None:
        """Rig parameters are validated eagerly."""
        with pytest.raises(ValueError, match="yaw_steps"):
            DAPModel(yaw_steps=0)
        with pytest.raises(ValueError, match="pitches"):
            DAPModel(pitches=())
        with pytest.raises(ValueError, match="view_res"):
            DAPModel(view_res=4)

    def test_missing_erp_weights_raise(self, tmp_path) -> None:
        """A weights directory without config.json fails loudly on load."""
        model = DAPModel(erp_weights=tmp_path)
        with pytest.raises(RuntimeError, match=r"config\.json"):
            model.estimate_depth(np.zeros((16, 32, 3), dtype=np.uint8))

    def test_estimate_depth_uses_fusion(self) -> None:
        """estimate_depth fuses mocked per-view depths back to ERP shape."""
        model = DAPModel(yaw_steps=4, pitches=(-45.0, 0.0, 45.0), view_res=16, view_fov=90.0)
        fake = MagicMock()
        # A metric perspective model: its output is already depth.
        fake.outputs_metric_depth = True
        fake.estimate_depth_batch.side_effect = lambda views: [
            np.full(v.shape[:2], 2.0, dtype=np.float32) for v in views
        ]
        model._perspective = fake

        image = np.zeros((32, 64, 3), dtype=np.uint8)
        depth = model.estimate_depth(image)

        assert depth.shape == (32, 64)
        assert depth.dtype == np.float32
        # A constant perspective depth of 2.0 means every ERP pixel sees the
        # same distance along its view axis; the fused radial depth is that
        # distance times the pixel's ray norm, so it is >= 2.0 where a view
        # covers the pixel and exactly 2.0 at a view centre.
        covered = depth > 0
        assert covered.mean() > 0.9
        assert float(depth[covered].min()) >= 2.0 - 1e-4
        assert float(depth.max()) < 2.0 * math.sqrt(3.0)
        assert fake.estimate_depth_batch.call_count == 1

    def test_max_depth_zeroes_far_pixels(self) -> None:
        """dap_max_depth clips far geometry to zero (treated as invalid)."""
        model = DAPModel(yaw_steps=4, pitches=(0.0,), view_res=16, max_depth=1.5)
        fake = MagicMock()
        # A metric perspective model: its output is already depth.
        fake.outputs_metric_depth = True
        fake.estimate_depth_batch.side_effect = lambda views: [
            np.full(v.shape[:2], 2.0, dtype=np.float32) for v in views
        ]
        model._perspective = fake
        depth = model.estimate_depth(np.zeros((32, 64, 3), dtype=np.uint8))
        assert float(depth.max()) == 0.0

    def test_invalid_image_shape_raises(self) -> None:
        """Non-(H, W, 3) inputs are rejected."""
        model = DAPModel()
        with pytest.raises(ValueError, match=r"\(H, W, 3\)"):
            model.estimate_depth(np.zeros((16, 32), dtype=np.uint8))


# ---------------------------------------------------------------------------
# DepthAnythingV2Model
# ---------------------------------------------------------------------------


class TestDepthAnythingV2Model:
    """Contract tests for the Depth Anything V2 wrapper."""

    def test_size_aliases(self) -> None:
        """Friendly size names map to ViT variants and repo ids."""
        assert DepthAnythingV2Model("small").model_size == "vits"
        assert DepthAnythingV2Model("base").model_size == "vitb"
        assert DepthAnythingV2Model("large").model_size == "vitl"
        assert "Small" in DepthAnythingV2Model("small").repo_id

    def test_unknown_size_raises(self) -> None:
        """Unknown sizes are rejected."""
        with pytest.raises(ValueError, match="Unknown Depth Anything V2 model size"):
            DepthAnythingV2Model("gigantic")

    def test_is_not_stub(self) -> None:
        """The wrapper is a real backend."""
        assert DepthAnythingV2Model().is_stub is False

    def test_estimate_depth_resizes_to_input(self) -> None:
        """Model output is resized back to the input resolution."""
        torch = pytest.importorskip("torch")

        model = DepthAnythingV2Model("small", device="cpu")
        model._processor = lambda images, return_tensors: {
            "pixel_values": torch.zeros(1, 3, 32, 48)
        }
        fake = MagicMock()
        fake.return_value = MagicMock(predicted_depth=torch.ones(1, 32, 48))
        model._model = fake

        image = np.zeros((100, 120, 3), dtype=np.uint8)
        depth = model.estimate_depth(image)

        assert depth.shape == (100, 120)
        assert depth.dtype == np.float32
        assert np.allclose(depth, 1.0)

    def test_batch_validation(self) -> None:
        """Bad shapes are rejected before any model work happens."""
        model = DepthAnythingV2Model("small", device="cpu")
        with pytest.raises(ValueError, match="Image at index 0"):
            model.estimate_depth_batch([np.zeros((8, 8), dtype=np.uint8)])

    def test_empty_batch(self) -> None:
        """An empty batch returns an empty list without loading the model."""
        assert DepthAnythingV2Model("small", device="cpu").estimate_depth_batch([]) == []


class TestViewHarmonization:
    """Relative-depth views must be put on a common scale before fusion."""

    def test_affine_ambiguity_is_removed(self) -> None:
        """Views differing by a*x+b should converge to the same map."""
        from sphereforge.models.dap_model import _harmonize_view_scales

        rng = np.random.RandomState(0)
        base = rng.uniform(1.0, 3.0, (32, 32)).astype(np.float32)
        views = [(base * a + b).astype(np.float32) for a, b in [(1, 0), (0.5, 0.4), (2.0, -0.3)]]

        out = _harmonize_view_scales(views)

        # After harmonization every view should agree with every other one.
        for i in range(1, len(out)):
            ratio = np.median(out[i] / np.maximum(out[0], 1e-6))
            assert ratio == pytest.approx(1.0, abs=0.05)

    def test_pure_scale_difference_is_removed(self) -> None:
        """A constant-scale difference is the simplest case."""
        from sphereforge.models.dap_model import _harmonize_view_scales

        base = np.full((16, 16), 2.0, dtype=np.float32)
        out = _harmonize_view_scales([base, base * 3.0, base * 0.5])
        medians = [float(np.median(o)) for o in out]
        assert all(m == pytest.approx(medians[0], rel=0.05) for m in medians)

    def test_empty_and_degenerate_inputs(self) -> None:
        """Empty lists and all-zero maps are handled without crashing."""
        from sphereforge.models.dap_model import _harmonize_view_scales

        assert _harmonize_view_scales([]) == []
        zeros = [np.zeros((8, 8), dtype=np.float32)]
        out = _harmonize_view_scales(zeros)
        assert len(out) == 1
        assert np.allclose(out[0], 0.0)

    def test_output_shapes_preserved(self) -> None:
        """Harmonization must not change array shapes."""
        from sphereforge.models.dap_model import _harmonize_view_scales

        views = [np.ones((12, 12), dtype=np.float32) * s for s in (1.0, 1.5, 0.8)]
        out = _harmonize_view_scales(views)
        assert [o.shape for o in out] == [v.shape for v in views]


# ---------------------------------------------------------------------------
# Disparity handling (Depth Anything V2 relative checkpoints)
# ---------------------------------------------------------------------------


def _box_radial_depth(directions: np.ndarray, half_extents=(2.5, 1.5, 2.0)) -> np.ndarray:
    """Radial distance from the origin to the inside of an axis-aligned box."""
    ext = np.asarray(half_extents, dtype=np.float64)
    with np.errstate(divide="ignore"):
        t = np.where(np.abs(directions) > 1e-12, ext / np.abs(directions), np.inf)
    return np.min(t, axis=-1)


def _view_box_perspective_depths(
    angles: list[tuple[float, float]], res: int, fov: float
) -> list[np.ndarray]:
    """Exact perspective (z) depth of the box room for each rig view."""
    focal = res / (2.0 * math.tan(math.radians(fov) / 2.0))
    center = res / 2.0
    uu, vv = np.meshgrid(np.arange(res, dtype=np.float64), np.arange(res, dtype=np.float64))
    dx = (uu - center) / focal
    dy = (vv - center) / focal
    norms = np.sqrt(dx * dx + dy * dy + 1.0)
    dirs_cam = np.stack([dx / norms, dy / norms, 1.0 / norms], axis=-1)
    out = []
    for yaw_deg, pitch_deg in angles:
        rotation = _make_rotation_matrix(yaw_deg, pitch_deg)
        dirs_world = np.einsum("ij,...j->...i", rotation.T, dirs_cam)
        out.append((_box_radial_depth(dirs_world) / norms).astype(np.float32))
    return out


class TestDisparityHandling:
    """Relative DA-V2 output is disparity (larger = closer) and must be inverted."""

    def test_disparity_to_depth_inverts_and_marks_far_invalid(self) -> None:
        """1/disparity, with zero/negative and too-far pixels set to 0."""
        disp = np.array([[2.0, 0.5], [0.0, -1.0]], dtype=np.float32)
        depth = disparity_to_depth(disp, max_range_ratio=100.0)
        assert depth[0, 0] == pytest.approx(0.5)
        assert depth[0, 1] == pytest.approx(2.0)
        assert depth[1, 0] == 0.0 and depth[1, 1] == 0.0
        # A disparity below max/ratio is "too far to trust".
        far = disparity_to_depth(np.array([10.0, 0.05], dtype=np.float32), max_range_ratio=100.0)
        assert far[1] == 0.0

    def test_relative_model_output_is_inverted(self) -> None:
        """estimate_depth returns depth: the larger raw output is the nearer pixel."""
        torch = pytest.importorskip("torch")
        model = DepthAnythingV2Model("small", device="cpu")
        model._processor = lambda images, return_tensors: {
            "pixel_values": torch.zeros(1, 3, 4, 4)
        }
        raw = torch.ones(1, 4, 4)
        raw[0, :, :2] = 4.0  # left half has 4x the disparity -> 4x closer
        model._model = MagicMock(return_value=MagicMock(predicted_depth=raw))
        image = np.zeros((4, 4, 3), dtype=np.uint8)

        disparity = model.estimate_disparity_batch([image])[0]
        depth = model.estimate_depth(image)

        assert float(disparity[:, 0].mean()) > float(disparity[:, 3].mean())
        assert float(depth[:, 0].mean()) < float(depth[:, 3].mean())
        assert depth[0, 3] == pytest.approx(1.0, rel=1e-3)
        assert depth[0, 0] == pytest.approx(0.25, rel=1e-3)

    def test_metric_checkpoint_is_passed_through(self) -> None:
        """Metric checkpoints already output depth, so nothing is inverted."""
        model = DepthAnythingV2Model(
            "small", device="cpu", repo_id="depth-anything/Depth-Anything-V2-Metric-Indoor-Small-hf"
        )
        assert model.outputs_metric_depth is True
        assert DepthAnythingV2Model("small", device="cpu").outputs_metric_depth is False

    def test_fusion_removes_per_view_affine_and_recovers_room(self) -> None:
        """Per-view disparity scale *and* shift are resolved from view overlap."""
        h, w = 48, 96
        angles = [(360.0 * s / 8, p) for p in (-45.0, 0.0, 45.0) for s in range(8)]
        angles += [(0.0, -90.0), (0.0, 90.0)]
        z_depths = _view_box_perspective_depths(angles, res=40, fov=90.0)
        rng = np.random.default_rng(0)
        disparities = []
        for z in z_depths:
            a = rng.uniform(0.5, 2.0)
            b = rng.uniform(0.0, 0.2)
            disparities.append((a / z + b).astype(np.float32))

        fused = _fuse_disparity_views_to_erp(
            disparities, angles, fov_deg=90.0, erp_height=h, erp_width=w
        )
        truth = _box_radial_depth(_erp_directions(h, w))
        valid = fused > 0
        assert valid.mean() > 0.99
        ratio = fused[valid] / truth[valid]
        ratio = ratio / np.median(ratio)  # depth is relative: compare up to scale
        assert float(np.median(np.abs(ratio - 1.0))) < 0.01
        # Depth must increase with true distance (the old bug inverted this).
        corr = np.corrcoef(fused[valid], truth[valid])[0, 1]
        assert corr > 0.95

    def test_dap_rig_path_uses_disparity_fusion(self) -> None:
        """For a relative perspective model, DAP fuses disparity, not depth."""
        model = DAPModel(yaw_steps=4, pitches=(-45.0, 0.0, 45.0), view_res=16, view_fov=90.0)
        fake = MagicMock()
        fake.outputs_metric_depth = False
        fake.estimate_disparity_batch.side_effect = lambda views: [
            np.full(v.shape[:2], 0.5, dtype=np.float32) for v in views
        ]
        model._perspective = fake
        depth = model.estimate_depth(np.zeros((32, 64, 3), dtype=np.uint8))
        assert depth.shape == (32, 64)
        assert fake.estimate_disparity_batch.call_count == 1
        assert fake.estimate_depth_batch.call_count == 0
        assert float(np.mean(depth > 0)) > 0.9
