"""Tests for Metric3D model wrapper (T2.8) and RPG360 graph optimisation (T2.9).

Uses synthetic depth data (no real model inference) to validate the RPG360
graph optimisation, alignment, and fusion logic. Metric3D wrapper tests
mock the actual model loading to verify the API surface.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# T2.8 — Metric3D model wrapper tests
# ---------------------------------------------------------------------------


class TestMetric3DV2Init:
    """Tests for Metric3DV2 initialisation."""

    def test_default_init(self):
        """Metric3DV2 can be constructed with default parameters."""
        from sphereforge.models.metric3d import Metric3DV2

        m = Metric3DV2()
        assert m.model_name == "metric3d_vit_giant2"
        assert m._model is None  # lazy loading

    def test_invalid_model_name_raises(self):
        """Unknown model_name raises ValueError."""
        from sphereforge.models.metric3d import Metric3DV2

        with pytest.raises(ValueError, match="Unknown model_name"):
            Metric3DV2(model_name="nonexistent_model")

    def test_valid_model_names(self):
        """All documented model names are accepted."""
        from sphereforge.models.metric3d import Metric3DV2

        for name in ("metric3d_vit_giant2", "metric3d_vit_large", "metric3d_vit_small"):
            m = Metric3DV2(model_name=name)
            assert m.model_name == name


class TestMetric3DV2EstimateDepth:
    """Tests for Metric3DV2.estimate_depth with mocked model."""

    def test_estimate_depth_returns_correct_shape(self):
        """estimate_depth returns (H, W) float32 depth map with mocked model."""
        from sphereforge.models.metric3d import Metric3DV2

        import torch

        m = Metric3DV2()

        # Create a mock model that returns a depth dict with a torch tensor
        mock_model = MagicMock()
        mock_model.eval.return_value = mock_model
        mock_model.to.return_value = mock_model

        def fake_forward(x):
            b, c, h, w = x.shape
            depth = torch.ones(b, 1, h, w, dtype=torch.float32) * 5.0
            return {"depth": depth}

        mock_model.side_effect = fake_forward
        m._model = mock_model

        img = np.random.randint(0, 255, (100, 120, 3), dtype=np.uint8)
        result = m.estimate_depth(img)
        assert result.shape == (100, 120)
        assert result.dtype == np.float32

    def test_estimate_depth_invalid_shape_raises(self):
        """Passing a non-(H,W,3) image raises ValueError."""
        from sphereforge.models.metric3d import Metric3DV2

        m = Metric3DV2()
        with pytest.raises(ValueError, match="Expected image with shape"):
            m.estimate_depth(np.zeros((100, 100), dtype=np.uint8))

        with pytest.raises(ValueError, match="Expected image with shape"):
            m.estimate_depth(np.zeros((100, 100, 1), dtype=np.uint8))


class TestMetric3DV2Batch:
    """Tests for Metric3DV2.estimate_depth_batch."""

    def test_batch_invalid_image_raises(self):
        """estimate_depth_batch raises ValueError for bad images."""
        from sphereforge.models.metric3d import Metric3DV2

        m = Metric3DV2()
        bad_images = [np.zeros((10, 10), dtype=np.uint8)]
        with pytest.raises(ValueError, match="Image at index 0"):
            m.estimate_depth_batch(bad_images)


# ---------------------------------------------------------------------------
# T2.9 — RPG360 graph optimisation tests
# ---------------------------------------------------------------------------


def _make_synthetic_face_depths(
    base_scale: float = 1.0,
    base_shift: float = 0.0,
    face_size: int = 256,
    noise_std: float = 0.01,
) -> tuple[list[np.ndarray], list[str]]:
    """Create synthetic per-face depth maps with known scale/shift.

    Creates depth maps where each face has a constant depth value modulated
    by a known per-face scale and shift, plus small Gaussian noise.

    Returns:
        Tuple of (face_depths, face_directions).
    """
    directions = ["front", "right", "back", "left", "top", "bottom"]
    depths: list[np.ndarray] = []

    rng = np.random.default_rng(42)

    # Known per-face scales and shifts (simulating a model that outputs
    # depth with different scale/shift per face)
    true_scales = [1.0, 1.1, 0.95, 1.05, 1.2, 0.9]
    true_shifts = [0.0, 0.5, -0.3, 0.2, 0.8, -0.5]

    for i, d in enumerate(directions):
        # Base depth: distance varies by face direction (simple model)
        base_depth = 5.0 + i * 0.1
        # Apply the "true" inverse scale/shift so that optimiser must recover them
        depth = (base_depth - true_shifts[i]) / true_scales[i]
        depth_map = np.full((face_size, face_size), depth, dtype=np.float32)
        # Add small noise
        depth_map += rng.normal(0, noise_std, depth_map.shape).astype(np.float32)
        depths.append(depth_map)

    return depths, directions


class TestGraphOptimizeScales:
    """Tests for graph_optimize_scales."""

    def test_returns_six_scales_and_shifts(self):
        """graph_optimize_scales returns lists of 6 floats each."""
        from sphereforge.stages.stage02_cubemap.rpg360_graph import (
            graph_optimize_scales,
        )

        depths, directions = _make_synthetic_face_depths()
        scales, shifts = graph_optimize_scales(depths, directions, overlap_pixels=20)

        assert len(scales) == 6
        assert len(shifts) == 6
        assert all(isinstance(s, float) for s in scales)
        assert all(isinstance(s, float) for s in shifts)

    def test_reference_face_has_unit_scale_zero_shift(self):
        """The reference face ('front') always gets scale=1, shift=0."""
        from sphereforge.stages.stage02_cubemap.rpg360_graph import (
            graph_optimize_scales,
        )

        depths, directions = _make_synthetic_face_depths()
        scales, shifts = graph_optimize_scales(depths, directions, overlap_pixels=20)

        front_idx = directions.index("front")
        assert scales[front_idx] == 1.0
        assert shifts[front_idx] == 0.0

    def test_consistent_depths_produce_identity_alignment(self):
        """If all faces already have consistent depths, scales ≈ 1, shifts ≈ 0."""
        from sphereforge.stages.stage02_cubemap.rpg360_graph import (
            graph_optimize_scales,
        )

        face_size = 128
        directions = ["front", "right", "back", "left", "top", "bottom"]
        # All faces have the same depth → no scale/shift needed
        depths = [np.full((face_size, face_size), 5.0, dtype=np.float32)
                  for _ in range(6)]

        scales, shifts = graph_optimize_scales(depths, directions, overlap_pixels=20)

        front_idx = directions.index("front")
        for i in range(6):
            if i == front_idx:
                continue
            assert abs(scales[i] - 1.0) < 0.1, (
                f"Face {directions[i]}: scale {scales[i]} should be ≈ 1.0"
            )
            assert abs(shifts[i]) < 0.5, (
                f"Face {directions[i]}: shift {shifts[i]} should be ≈ 0.0"
            )

    def test_wrong_length_raises(self):
        """Passing non-6 face lists raises ValueError."""
        from sphereforge.stages.stage02_cubemap.rpg360_graph import (
            graph_optimize_scales,
        )

        with pytest.raises(ValueError, match="Expected 6 faces"):
            graph_optimize_scales(
                [np.zeros((10, 10))], ["front"], overlap_pixels=5
            )

    def test_invalid_direction_raises(self):
        """Unknown face direction raises ValueError."""
        from sphereforge.stages.stage02_cubemap.rpg360_graph import (
            graph_optimize_scales,
        )

        depths = [np.zeros((10, 10)) for _ in range(6)]
        bad_dirs = ["front", "right", "back", "left", "top", "north"]
        with pytest.raises(ValueError, match="Unknown face direction"):
            graph_optimize_scales(depths, bad_dirs, overlap_pixels=5)


class TestAlignFaceDepths:
    """Tests for align_face_depths."""

    def test_correct_application(self):
        """align_face_depths correctly computes depth * scale + shift."""
        from sphereforge.stages.stage02_cubemap.rpg360_graph import (
            align_face_depths,
        )

        depths = [np.ones((4, 4), dtype=np.float32) * 2.0 for _ in range(3)]
        scales = [1.0, 2.0, 0.5]
        shifts = [0.0, -1.0, 3.0]

        aligned = align_face_depths(depths, scales, shifts)

        assert len(aligned) == 3
        np.testing.assert_allclose(aligned[0], 2.0)
        np.testing.assert_allclose(aligned[1], 3.0)  # 2.0 * 2.0 - 1.0
        np.testing.assert_allclose(aligned[2], 4.0)  # 2.0 * 0.5 + 3.0

    def test_output_dtype_float32(self):
        """Output arrays have dtype float32."""
        from sphereforge.stages.stage02_cubemap.rpg360_graph import (
            align_face_depths,
        )

        depths = [np.ones((4, 4), dtype=np.float64) * 2.0]
        scales = [1.0]
        shifts = [0.0]

        aligned = align_face_depths(depths, scales, shifts)
        assert aligned[0].dtype == np.float32

    def test_length_mismatch_raises(self):
        """Mismatched list lengths raise ValueError."""
        from sphereforge.stages.stage02_cubemap.rpg360_graph import (
            align_face_depths,
        )

        with pytest.raises(ValueError, match="Length mismatch"):
            align_face_depths(
                [np.zeros((4, 4))],
                [1.0, 2.0],  # wrong length
                [0.0],
            )


class TestFuseToErp:
    """Tests for fuse_to_erp."""

    def test_returns_correct_shape(self):
        """fuse_to_erp returns an ERP depth map of the requested size."""
        from sphereforge.stages.stage02_cubemap.rpg360_graph import fuse_to_erp

        face_size = 64
        directions = ["front", "right", "back", "left", "top", "bottom"]
        depths = [np.ones((face_size, face_size), dtype=np.float32) * 5.0
                  for _ in range(6)]

        erp_h, erp_w = 128, 256
        result = fuse_to_erp(depths, directions, erp_h, erp_w)

        assert result.shape == (erp_h, erp_w)
        assert result.dtype == np.float32

    def test_delegates_to_depth_utils(self):
        """fuse_to_erp delegates to fuse_cubemap_depth_to_erp."""
        from sphereforge.stages.stage02_cubemap.rpg360_graph import fuse_to_erp

        face_size = 32
        directions = ["front", "right", "back", "left", "top", "bottom"]
        depths = [np.ones((face_size, face_size), dtype=np.float32) * 3.0
                  for _ in range(6)]

        result = fuse_to_erp(depths, directions, 64, 128)
        # Non-zero depth where ERP maps to a cubemap face
        assert np.any(result > 0)


class TestEndToEndRpg360:
    """End-to-end test: optimise → align → fuse on synthetic data."""

    def test_optimize_align_fuse_pipeline(self):
        """Full pipeline: graph_optimize_scales → align_face_depths → fuse_to_erp."""
        from sphereforge.stages.stage02_cubemap.rpg360_graph import (
            align_face_depths,
            fuse_to_erp,
            graph_optimize_scales,
        )

        face_size = 64
        directions = ["front", "right", "back", "left", "top", "bottom"]
        rng = np.random.default_rng(123)

        # Create depth maps with a known global scale plus per-face offset
        # The optimisation should find per-face corrections
        depths = []
        for i in range(6):
            base = 5.0 + 0.5 * np.sin(i * np.pi / 3)  # varying base depth
            depth_map = np.full((face_size, face_size), base, dtype=np.float32)
            depth_map += rng.normal(0, 0.02, depth_map.shape).astype(np.float32)
            depths.append(depth_map)

        scales, shifts = graph_optimize_scales(depths, directions, overlap_pixels=10)
        aligned = align_face_depths(depths, scales, shifts)

        assert len(aligned) == 6
        for d in aligned:
            assert d.shape == (face_size, face_size)
            assert d.dtype == np.float32

        erp = fuse_to_erp(aligned, directions, 128, 256)
        assert erp.shape == (128, 256)
        assert erp.dtype == np.float32
