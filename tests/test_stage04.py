"""Tests for Stage 4: Dense Depth Estimation (T4.1-T4.7).

All model inference is mocked - no GPU required.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


def _bilinear_sample(image: np.ndarray, rows: np.ndarray, cols: np.ndarray) -> np.ndarray:
    """Bilinear sample of *image* at fractional (row, col) coordinates."""
    h, w = image.shape
    r0 = np.floor(rows).astype(int)
    c0 = np.floor(cols).astype(int)
    fr = rows - r0
    fc = cols - c0
    r0 = np.clip(r0, 0, h - 1)
    r1 = np.clip(r0 + 1, 0, h - 1)
    c0 = np.clip(c0, 0, w - 1)
    c1 = np.clip(c0 + 1, 0, w - 1)
    return (
        image[r0, c0] * (1 - fr) * (1 - fc)
        + image[r0, c1] * (1 - fr) * fc
        + image[r1, c0] * fr * (1 - fc)
        + image[r1, c1] * fr * fc
    )

# ---------------------------------------------------------------------------
# T4.2 — Scene Analysis
# ---------------------------------------------------------------------------


class TestAnalyzeDepthScene:
    """Tests for scene_analysis.analyze_depth_scene."""

    def test_basic_analysis(self, synthetic_depth_map: np.ndarray) -> None:
        """Scene analysis on known synthetic depth map."""
        from sphereforge.stages.stage04_depth.scene_analysis import (
            analyze_depth_scene,
        )

        result = analyze_depth_scene(synthetic_depth_map)

        # Check all required keys exist
        assert "depth_range" in result
        assert "sky_depth" in result
        assert "orbit_radius" in result
        assert "sky_mask" in result
        assert "near_clip" in result
        assert "far_clip" in result

        # depth_range dict structure
        dr = result["depth_range"]
        assert "min" in dr
        assert "max" in dr
        assert "p1" in dr
        assert "p99" in dr

        # Values should be positive and consistent
        assert dr["min"] > 0
        assert dr["max"] > 0
        assert dr["p1"] >= dr["min"]
        assert dr["p99"] <= dr["max"]

        # orbit_radius (median) should be between p1 and p99
        assert result["orbit_radius"] >= dr["p1"]
        assert result["orbit_radius"] <= dr["p99"]

        # sky_depth = 95th percentile > median
        assert result["sky_depth"] > result["orbit_radius"]

        # sky_mask should have same shape as input
        assert result["sky_mask"].shape == synthetic_depth_map.shape
        assert result["sky_mask"].dtype == bool

        # near_clip == p1, far_clip == p99
        assert result["near_clip"] == dr["p1"]
        assert result["far_clip"] == dr["p99"]

    def test_uniform_depth(self) -> None:
        """Uniform depth map should produce consistent results."""
        from sphereforge.stages.stage04_depth.scene_analysis import (
            analyze_depth_scene,
        )

        depth = np.full((100, 200), 5.0, dtype=np.float32)
        result = analyze_depth_scene(depth)

        # All percentiles should be ~5.0
        assert abs(result["depth_range"]["min"] - 5.0) < 1e-6
        assert abs(result["orbit_radius"] - 5.0) < 1e-6
        assert abs(result["near_clip"] - 5.0) < 1e-6
        assert abs(result["far_clip"] - 5.0) < 1e-6

    def test_invalid_depth_raises(self) -> None:
        """All-zero depth map should raise ValueError."""
        from sphereforge.stages.stage04_depth.scene_analysis import (
            analyze_depth_scene,
        )

        depth = np.zeros((64, 128), dtype=np.float32)
        with pytest.raises(ValueError, match="no valid"):
            analyze_depth_scene(depth)

    def test_wrong_ndim_raises(self) -> None:
        """3D depth map should raise ValueError."""
        from sphereforge.stages.stage04_depth.scene_analysis import (
            analyze_depth_scene,
        )

        depth = np.zeros((64, 128, 3), dtype=np.float32)
        with pytest.raises(ValueError, match="2D"):
            analyze_depth_scene(depth)

    def test_sky_mask_consistency(self) -> None:
        """Sky mask should flag pixels above sky_depth."""
        from sphereforge.stages.stage04_depth.scene_analysis import (
            analyze_depth_scene,
        )

        depth = np.arange(100, dtype=np.float32).reshape(10, 10) + 1.0
        result = analyze_depth_scene(depth)
        sky_depth = result["sky_depth"]
        sky_mask = result["sky_mask"]
        # All pixels > sky_depth should be True
        assert np.all(sky_mask[depth > sky_depth])
        # All pixels <= sky_depth should be False
        assert not np.any(sky_mask[depth <= sky_depth])


# ---------------------------------------------------------------------------
# T4.3 — Depth Alignment
# ---------------------------------------------------------------------------


class TestAlignDepthToColmap:
    """Tests for depth_alignment.align_depth_to_colmap."""

    def test_alignment_accuracy(self) -> None:
        """Create synthetic sparse model + depth; verify scale and shift."""
        from sphereforge.stages.stage04_depth.depth_alignment import (
            align_depth_to_colmap,
        )

        h, w = 64, 128
        # True metric depth (known scale)
        true_scale = 2.5
        true_shift = 0.3
        metric_depth = np.random.uniform(1.0, 10.0, (h, w)).astype(np.float32)
        # Monocular depth = metric / scale - shift/scale (simplified)
        mono_depth = (metric_depth - true_shift) / true_scale
        mono_depth = mono_depth.astype(np.float32)

        # Build a synthetic sparse model
        # Points at known locations in world coordinates, matching the depth
        # Camera: identity pose at origin, looking along +Z
        fx, fy, cx, cy = 100.0, 100.0, w / 2.0, h / 2.0

        # Create sparse points in front of the camera
        n_pts = 20
        rng = np.random.RandomState(42)
        x_cam = rng.uniform(-1, 1, n_pts)
        y_cam = rng.uniform(-1, 1, n_pts)
        z_cam = rng.uniform(2.0, 8.0, n_pts)  # metric depth values

        # Project to pixel coordinates
        u_px = fx * x_cam / z_cam + cx
        v_px = fy * y_cam / z_cam + cy

        # Only keep points that project inside image
        valid = (u_px >= 0) & (u_px < w) & (v_px >= 0) & (v_px < h)
        x_cam = x_cam[valid]
        y_cam = y_cam[valid]
        z_cam = z_cam[valid]
        u_px = u_px[valid]
        v_px = v_px[valid]

        # Set mono depth at projected points to match expected values
        u_idx = np.clip(np.round(u_px).astype(int), 0, w - 1)
        v_idx = np.clip(np.round(v_px).astype(int), 0, h - 1)
        for j in range(len(u_idx)):
            mono_depth[v_idx[j], u_idx[j]] = (z_cam[j] - true_shift) / true_scale

        # World coordinates = camera coordinates (identity pose)
        # COLMAP convention: world-to-cam = [R|t], with R=I, t=0
        sparse_model = {
            "cameras": {
                1: {
                    "model": "PINHOLE",
                    "width": w,
                    "height": h,
                    "params": [fx, fy, cx, cy],
                }
            },
            "images": {
                1: {
                    "name": "test_frame.png",
                    "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                    "tx": 0.0, "ty": 0.0, "tz": 0.0,
                    "camera_id": 1,
                    "point3D_ids": list(range(1, len(x_cam) + 1)),
                }
            },
            "points3D": {
                i + 1: {"x": float(x_cam[i]), "y": float(y_cam[i]), "z": float(z_cam[i])}
                for i in range(len(x_cam))
            },
        }

        aligned_depth, scale, shift = align_depth_to_colmap(
            depth_map=mono_depth,
            sparse_model=sparse_model,
            image_name="test_frame.png",
        )

        # Scale and shift should be close to true values
        assert abs(scale - true_scale) < 0.5, f"Scale {scale} vs expected {true_scale}"
        assert abs(shift - true_shift) < 1.0, f"Shift {shift} vs expected {true_shift}"

        # Aligned depth should have the correct shape
        assert aligned_depth.shape == (h, w)
        assert aligned_depth.dtype == np.float32

    def test_image_not_found_raises(self) -> None:
        """Missing image name should raise ValueError."""
        from sphereforge.stages.stage04_depth.depth_alignment import (
            align_depth_to_colmap,
        )

        depth = np.ones((64, 128), dtype=np.float32)
        sparse_model = {
            "cameras": {1: {"model": "PINHOLE", "width": 128, "height": 64, "params": [100, 100, 64, 32]}},
            "images": {},
            "points3D": {},
        }

        with pytest.raises(ValueError, match="not found"):
            align_depth_to_colmap(depth, sparse_model, "nonexistent.png")

    def test_no_sparse_points_raises(self) -> None:
        """Image with no sparse point observations should raise ValueError."""
        from sphereforge.stages.stage04_depth.depth_alignment import (
            align_depth_to_colmap,
        )

        depth = np.ones((64, 128), dtype=np.float32)
        sparse_model = {
            "cameras": {1: {"model": "PINHOLE", "width": 128, "height": 64, "params": [100, 100, 64, 32]}},
            "images": {
                1: {
                    "name": "frame.png",
                    "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                    "tx": 0.0, "ty": 0.0, "tz": 0.0,
                    "camera_id": 1,
                    "point3D_ids": [],  # No points!
                }
            },
            "points3D": {},
        }

        with pytest.raises(ValueError, match="No sparse 3D points"):
            align_depth_to_colmap(depth, sparse_model, "frame.png")

    def test_with_rpg360_anchor(self) -> None:
        """Alignment with RPG360 anchor should not crash."""
        from sphereforge.stages.stage04_depth.depth_alignment import (
            align_depth_to_colmap,
        )

        h, w = 64, 128
        fx, fy, cx, cy = 100.0, 100.0, w / 2.0, h / 2.0
        depth = np.ones((h, w), dtype=np.float32) * 3.0
        anchor = np.ones((h, w), dtype=np.float32) * 3.1

        n_pts = 10
        rng = np.random.RandomState(123)
        z_cam = rng.uniform(2.0, 5.0, n_pts)
        x_cam = rng.uniform(-0.5, 0.5, n_pts)
        y_cam = rng.uniform(-0.5, 0.5, n_pts)

        sparse_model = {
            "cameras": {1: {"model": "PINHOLE", "width": w, "height": h, "params": [fx, fy, cx, cy]}},
            "images": {
                1: {
                    "name": "test.png",
                    "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                    "tx": 0.0, "ty": 0.0, "tz": 0.0,
                    "camera_id": 1,
                    "point3D_ids": list(range(1, n_pts + 1)),
                }
            },
            "points3D": {
                i + 1: {"x": float(x_cam[i]), "y": float(y_cam[i]), "z": float(z_cam[i])}
                for i in range(n_pts)
            },
        }

        aligned, scale, _shift = align_depth_to_colmap(
            depth, sparse_model, "test.png", rpg360_anchor=anchor
        )
        assert aligned.shape == (h, w)
        assert scale > 0

    def test_panorama_rig_frame_name_uses_erp_alignment(self, tmp_path: Path) -> None:
        """Panorama-rig sparse models should align ERP depths by frame stem."""
        from sphereforge.stages.stage04_depth.depth_alignment import align_depth_to_colmap

        h, w = 64, 128
        true_scale = 3.0
        true_shift = 0.2
        # A smooth depth field: the sparse points below are drawn from the same
        # field, so the sparse/mono ratio is constant. (An i.i.d. random field
        # would make the ratio drift with depth even for a perfect fit.)
        yy, xx = np.mgrid[0:h, 0:w]
        metric_depth = (
            2.0 + 3.0 * (xx / w) + 2.0 * (yy / h) + 0.5 * np.sin(xx / 8.0)
        ).astype(np.float32)
        mono_depth = ((metric_depth - true_shift) / true_scale).astype(np.float32)

        rng = np.random.RandomState(7)
        points_world = rng.normal(size=(24, 3)).astype(np.float64)
        points_world[:, 2] += 3.0
        metric_range = np.linalg.norm(points_world, axis=1)
        # Draw each sparse point's depth from the same field as the ERP depth map,
        # looked up at the pixel the point projects to (so the ratio is constant).
        # The lookup is *bilinear*, matching how the alignment code samples the
        # depth map; nearest-pixel sampling would put points on either side of a
        # depth step and make the ratio drift with depth.
        point_dirs = points_world / np.linalg.norm(points_world, axis=1, keepdims=True)
        p_phi = np.arctan2(point_dirs[:, 0], -point_dirs[:, 2])
        p_theta = np.arcsin(np.clip(point_dirs[:, 1], -1.0, 1.0))
        p_u = (p_phi + np.pi) / (2.0 * np.pi) * w - 0.5
        p_v = (np.pi / 2.0 - p_theta) / np.pi * h - 0.5
        metric_range = _bilinear_sample(metric_depth, p_v, p_u).astype(np.float64)
        points_world = point_dirs * metric_range[:, None]

        dataset_dir = tmp_path / "dataset"
        dataset_dir.mkdir()
        (dataset_dir / "panorama_rig.json").write_text(
            '{"projection_layout":"panorama_rig","fov":90,"overlap":15,'
            '"cameras":[{"name":"pano_camera00","yaw_deg":0.0,"pitch_deg":0.0,"camera_id":1}]}',
            encoding="utf-8",
        )

        sparse_model = {
            "cameras": {
                1: {
                    "model": "PINHOLE",
                    "width": 32,
                    "height": 32,
                    "params": [20.0, 20.0, 16.0, 16.0],
                }
            },
            "images": {
                1: {
                    "name": "pano_camera00/frame_000.png",
                    "qw": 1.0,
                    "qx": 0.0,
                    "qy": 0.0,
                    "qz": 0.0,
                    "tx": 0.0,
                    "ty": 0.0,
                    "tz": 0.0,
                    "camera_id": 1,
                    "point3D_ids": list(range(1, len(points_world) + 1)),
                }
            },
            "points3D": {
                idx + 1: {
                    "x": float(points_world[idx, 0]),
                    "y": float(points_world[idx, 1]),
                    "z": float(points_world[idx, 2]),
                }
                for idx in range(len(points_world))
            },
        }

        aligned_depth, scale, shift = align_depth_to_colmap(
            depth_map=mono_depth,
            sparse_model=sparse_model,
            image_name="frame_000.png",
            colmap_dataset_dir=dataset_dir,
        )

        assert aligned_depth.shape == (h, w)
        assert abs(scale - true_scale) < 0.5
        assert abs(shift - true_shift) < 1.0


# ---------------------------------------------------------------------------
# T4.5 — Model Factory
# ---------------------------------------------------------------------------


class TestModelFactory:
    """Tests for model_factory.get_depth_estimator."""

    def test_stub_backend_detection(self) -> None:
        """Only unimplemented backends should be flagged as stubs."""
        from sphereforge.stages.stage04_depth.model_factory import is_stub_depth_model

        assert is_stub_depth_model("dap") is False
        assert is_stub_depth_model("panda") is False
        assert is_stub_depth_model("depth_anything_v2") is False
        assert is_stub_depth_model("rpg360") is False
        assert is_stub_depth_model("da360") is True

    def test_panda_returns_dap_alias(self) -> None:
        """Deprecated 'panda' should resolve to the DAP alias path."""
        from sphereforge.models.dap_model import DAPModel
        from sphereforge.stages.stage04_depth.model_factory import (
            get_depth_estimator,
        )

        model = get_depth_estimator("panda")
        assert isinstance(model, DAPModel)

    def test_rpg360_returns_correct_type(self) -> None:
        """Factory should return Metric3DV2 for 'rpg360'."""
        from sphereforge.models.metric3d import Metric3DV2
        from sphereforge.stages.stage04_depth.model_factory import (
            get_depth_estimator,
        )

        model = get_depth_estimator("rpg360")
        assert isinstance(model, Metric3DV2)

    def test_da360_raises_not_implemented(self) -> None:
        """Factory should raise NotImplementedError for 'da360'."""
        from sphereforge.stages.stage04_depth.model_factory import (
            get_depth_estimator,
        )

        with pytest.raises(NotImplementedError, match="da360"):
            get_depth_estimator("da360")

    def test_unknown_model_raises_value_error(self) -> None:
        """Factory should raise ValueError for unknown model names."""
        from sphereforge.stages.stage04_depth.model_factory import (
            get_depth_estimator,
        )

        with pytest.raises(ValueError, match="Unknown depth model"):
            get_depth_estimator("nonexistent_model")


# ---------------------------------------------------------------------------
# T4.4 — RPG360 Pipeline
# ---------------------------------------------------------------------------


class TestRPG360Pipeline:
    """Tests for rpg360_pipeline.rpg360_depth_pipeline (mocked)."""

    @patch("sphereforge.stages.stage04_depth.rpg360_pipeline.Metric3DV2")
    @patch("sphereforge.stages.stage04_depth.rpg360_pipeline.graph_optimize_scales")
    @patch("sphereforge.stages.stage04_depth.rpg360_pipeline.align_face_depths")
    @patch("sphereforge.stages.stage04_depth.rpg360_pipeline.fuse_to_erp")
    def test_pipeline_calls_graph_optimization(
        self,
        mock_fuse: MagicMock,
        mock_align: MagicMock,
        mock_graph: MagicMock,
        mock_metric3d_cls: MagicMock,
    ) -> None:
        """Verify graph_optimize_scales is called in the pipeline."""
        from sphereforge.stages.stage04_depth.rpg360_pipeline import (
            rpg360_depth_pipeline,
        )

        # Setup mocks
        fake_depth = np.ones((256, 256), dtype=np.float32) * 5.0
        mock_model_instance = MagicMock()
        mock_model_instance.estimate_depth_batch.return_value = [
            fake_depth.copy() for _ in range(6)
        ]
        mock_metric3d_cls.return_value = mock_model_instance

        mock_graph.return_value = ([1.0] * 6, [0.0] * 6)
        mock_align.return_value = [fake_depth.copy() for _ in range(6)]

        erp_depth = np.ones((512, 1024), dtype=np.float32) * 5.0
        mock_fuse.return_value = erp_depth

        # Prepare inputs
        images = [np.zeros((256, 256, 3), dtype=np.uint8) for _ in range(6)]
        face_directions = ["front", "right", "back", "left", "top", "bottom"]

        result = rpg360_depth_pipeline(
            images=images,
            face_directions=face_directions,
            erp_height=512,
            erp_width=1024,
        )

        # Verify graph optimization was called
        mock_graph.assert_called_once()
        call_args = mock_graph.call_args
        assert len(call_args[0][0]) == 6  # 6 face depths
        assert call_args[0][1] == face_directions

        # Verify alignment was applied
        mock_align.assert_called_once()

        # Verify fusion was called
        mock_fuse.assert_called_once()

        # Result shape
        assert result.shape == (512, 1024)

    def test_invalid_num_faces_raises(self) -> None:
        """Wrong number of faces should raise ValueError."""
        from sphereforge.stages.stage04_depth.rpg360_pipeline import (
            rpg360_depth_pipeline,
        )

        with pytest.raises(ValueError, match="6 cubemap faces"):
            rpg360_depth_pipeline(
                images=[np.zeros((64, 64, 3), dtype=np.uint8)] * 3,
                face_directions=["front", "right", "back"],
                erp_height=256,
                erp_width=512,
            )


# ---------------------------------------------------------------------------
# T4.6 — Pipeline Orchestration
# ---------------------------------------------------------------------------


class TestRunStage04:
    """Tests for pipeline.run_stage04 (mocked heavy ops)."""

    @patch("sphereforge.stages.stage04_depth.pipeline.analyze_depth_scene")
    @patch("sphereforge.stages.stage04_depth.pipeline.align_depth_to_colmap")
    @patch("sphereforge.stages.stage04_depth.pipeline.get_depth_estimator")
    @patch("sphereforge.stages.stage04_depth.pipeline.log_task_completion")
    @patch("sphereforge.stages.stage04_depth.pipeline.read_depth")
    @patch("sphereforge.stages.stage04_depth.pipeline.write_depth")
    @patch("sphereforge.stages.stage04_depth.pipeline.read_image")
    def test_pipeline_flow(
        self,
        mock_read_image: MagicMock,
        mock_write_depth: MagicMock,
        mock_read_depth: MagicMock,
        mock_log_task: MagicMock,
        mock_get_estimator: MagicMock,
        mock_align: MagicMock,
        mock_analyze: MagicMock,
    ) -> None:
        """Verify pipeline flow: estimate → align → write → analyze."""
        from sphereforge.config import Stage04Config
        from sphereforge.stages.stage04_depth.pipeline import run_stage04

        # Setup
        h, w = 64, 128
        fake_image = np.zeros((h, w, 3), dtype=np.uint8)
        fake_depth = np.ones((h, w), dtype=np.float32) * 3.0
        mock_read_image.return_value = fake_image

        # Mock estimator
        mock_estimator = MagicMock()
        mock_estimator.estimate_depth.return_value = fake_depth
        mock_get_estimator.return_value = mock_estimator

        # Mock alignment
        mock_align.return_value = (fake_depth, 1.0, 0.0)

        # Mock read_depth (used by clipping step)
        mock_read_depth.return_value = fake_depth

        # Mock scene analysis
        mock_analyze.return_value = {
            "depth_range": {"min": 1.0, "max": 5.0, "p1": 1.2, "p99": 4.8},
            "sky_depth": 4.5,
            "orbit_radius": 3.0,
            "sky_mask": np.zeros((h, w), dtype=bool),
            "near_clip": 1.2,
            "far_clip": 4.8,
        }

        # Create fake frame paths
        with tempfile.TemporaryDirectory() as tmpdir:
            frame_dir = Path(tmpdir) / "frames"
            frame_dir.mkdir()
            frame_paths = []
            for i in range(3):
                p = frame_dir / f"frame_{i:03d}.png"
                # Create minimal file so read_image mock will be used
                frame_paths.append(p)

            output_dir = Path(tmpdir) / "depth"
            cubemap_dir = Path(tmpdir) / "cubemaps"
            cubemap_dir.mkdir()

            sparse_model = {
                "cameras": {1: {"model": "PINHOLE", "width": w, "height": h, "params": [100.0, 100.0, 64.0, 32.0]}},
                "images": {
                    1: {"name": "frame_000.png", "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                        "tx": 0.0, "ty": 0.0, "tz": 0.0, "camera_id": 1, "point3D_ids": [1]},
                    2: {"name": "frame_001.png", "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                        "tx": 0.0, "ty": 0.0, "tz": 0.0, "camera_id": 1, "point3D_ids": [1]},
                    3: {"name": "frame_002.png", "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                        "tx": 0.0, "ty": 0.0, "tz": 0.0, "camera_id": 1, "point3D_ids": [1]},
                },
                "points3D": {1: {"x": 0.0, "y": 0.0, "z": 3.0}},
            }

            config = Stage04Config(
                depth_model="panda",
                scale_alignment="median_ratio",
            )

            result = run_stage04(
                config=config,
                frame_paths=frame_paths,
                cubemap_dir=cubemap_dir,
                sparse_model=sparse_model,
                output_dir=output_dir,
            )

            # Verify the estimator is built once and reused across frames (model
            # loading dominates runtime, so per-frame construction is wasteful).
            assert mock_get_estimator.call_count == 1

            # Verify depth was estimated for each frame
            assert mock_estimator.estimate_depth.call_count == 3

            # Verify alignment was called for each frame
            assert mock_align.call_count == 3
            for call in mock_align.call_args_list:
                assert call.kwargs["colmap_dataset_dir"] == cubemap_dir

            # Verify depth was written for each frame
            assert mock_write_depth.call_count >= 3

            # Verify scene analysis was called
            mock_analyze.assert_called_once()

            # Verify return structure. 'panda' resolves to the real 'dap'
            # backend, so the run is no longer flagged as diagnostic-only.
            assert "depth_paths" in result
            assert "scene_params" in result
            assert result["diagnostics"]["stub_depth_backend"] is False
            assert result["diagnostics"]["aligned_frames"] == 3
            assert len(result["depth_paths"]) == 3
            diagnostics_text = (output_dir / "depth_diagnostics.json").read_text(encoding="utf-8")
            assert '"stub_depth_backend": false' in diagnostics_text

    @patch("sphereforge.stages.stage04_depth.pipeline.analyze_depth_scene")
    @patch("sphereforge.stages.stage04_depth.pipeline.align_depth_to_colmap")
    @patch("sphereforge.stages.stage04_depth.pipeline.get_depth_estimator")
    @patch("sphereforge.stages.stage04_depth.pipeline.log_task_completion")
    @patch("sphereforge.stages.stage04_depth.pipeline.write_depth")
    @patch("sphereforge.stages.stage04_depth.pipeline.read_image")
    def test_pipeline_fail_fast_on_not_implemented(
        self,
        mock_read_image: MagicMock,
        mock_write_depth: MagicMock,
        mock_log_task: MagicMock,
        mock_get_estimator: MagicMock,
        mock_align: MagicMock,
        mock_analyze: MagicMock,
    ) -> None:
        """Pipeline should raise RuntimeError when estimator raises NotImplementedError."""
        from sphereforge.config import Stage04Config
        from sphereforge.stages.stage04_depth.pipeline import run_stage04

        h, w = 64, 128
        fake_image = np.zeros((h, w, 3), dtype=np.uint8)
        mock_read_image.return_value = fake_image

        # Mock estimator that raises NotImplementedError (like PanDA without weights)
        mock_estimator = MagicMock()
        mock_estimator.estimate_depth.side_effect = NotImplementedError("No weights")
        mock_get_estimator.return_value = mock_estimator

        mock_align.return_value = (np.zeros((h, w), dtype=np.float32), 1.0, 0.0)
        mock_analyze.return_value = {
            "depth_range": {"min": 0.0, "max": 0.0, "p1": 0.0, "p99": 0.0},
            "sky_depth": 0.0,
            "orbit_radius": 0.0,
            "sky_mask": np.zeros((h, w), dtype=bool),
            "near_clip": 0.0,
            "far_clip": 0.0,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            frame_dir = Path(tmpdir) / "frames"
            frame_dir.mkdir()
            frame_path = frame_dir / "frame_000.png"

            config = Stage04Config(depth_model="panda", scale_alignment="median_ratio")

            with pytest.raises(RuntimeError, match="Depth estimation failed"):
                run_stage04(
                    config=config,
                    frame_paths=[frame_path],
                    cubemap_dir=Path(tmpdir) / "cubemaps",
                    sparse_model={
                        "cameras": {1: {"model": "PINHOLE", "width": w, "height": h, "params": [100, 100, 64, 32]}},
                        "images": {
                            1: {"name": "frame_000.png", "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                                "tx": 0.0, "ty": 0.0, "tz": 0.0, "camera_id": 1, "point3D_ids": [1]},
                        },
                        "points3D": {1: {"x": 0.0, "y": 0.0, "z": 3.0}},
                    },
                    output_dir=Path(tmpdir) / "depth",
                )


# ---------------------------------------------------------------------------
# T4.1 — PanDA Model
# ---------------------------------------------------------------------------


class TestPanDAModel:
    """Tests for panda_model.PanDAModel."""

    def test_init_without_weights(self) -> None:
        """PanDAModel should initialise but flag weights as missing."""
        from sphereforge.stages.stage04_depth.panda_model import PanDAModel

        model = PanDAModel()
        assert not model._weights_loaded

    def test_estimate_depth_raises_without_weights(self) -> None:
        """estimate_depth should raise NotImplementedError without weights."""
        from sphereforge.stages.stage04_depth.panda_model import PanDAModel

        model = PanDAModel()
        image = np.zeros((512, 1024, 3), dtype=np.uint8)

        with pytest.raises(NotImplementedError, match="PanDA"):
            model.estimate_depth(image)

    def test_estimate_depth_invalid_shape_raises(self) -> None:
        """estimate_depth should raise ValueError for wrong shape."""
        from sphereforge.stages.stage04_depth.panda_model import PanDAModel

        model = PanDAModel()
        bad_image = np.zeros((512, 1024), dtype=np.uint8)  # Missing channels

        # Shape validation happens before weight check
        with pytest.raises(ValueError, match="H, W, 3"):
            model.estimate_depth(bad_image)

    def test_batch_raises_without_weights(self) -> None:
        """estimate_depth_batch should raise NotImplementedError."""
        from sphereforge.stages.stage04_depth.panda_model import PanDAModel

        model = PanDAModel()
        images = [np.zeros((256, 512, 3), dtype=np.uint8)]

        with pytest.raises(NotImplementedError):
            model.estimate_depth_batch(images)

    def test_preprocess_shape(self) -> None:
        """Preprocessing should produce (3, 384, 768) output."""
        from sphereforge.stages.stage04_depth.panda_model import PanDAModel

        model = PanDAModel()
        image = np.zeros((512, 1024, 3), dtype=np.uint8)
        result = model._preprocess(image)
        assert result.shape == (3, 384, 768)
        assert result.dtype == np.float32

    def test_postprocess_shape(self) -> None:
        """Postprocessing should restore original resolution."""
        from sphereforge.stages.stage04_depth.panda_model import PanDAModel

        model = PanDAModel()
        raw_depth = np.ones((384, 768), dtype=np.float32) * 2.5
        result = model._postprocess(raw_depth, orig_h=512, orig_w=1024)
        assert result.shape == (512, 1024)
        assert result.dtype == np.float32

    def test_device_auto_selection(self) -> None:
        """Device 'auto' should resolve to 'cuda' or 'cpu'."""
        from sphereforge.stages.stage04_depth.panda_model import PanDAModel

        model = PanDAModel(device="auto")
        assert model._device_str in ("cuda", "cpu")

    def test_device_explicit(self) -> None:
        """Explicit device should be set as-is."""
        from sphereforge.stages.stage04_depth.panda_model import PanDAModel

        model = PanDAModel(device="cpu")
        assert model._device_str == "cpu"


class TestDepthAlignmentGuard:
    """The ERP/sparse scale fit must reject inconsistent geometry."""

    def test_constant_ratio_is_accepted(self) -> None:
        """A perfect correspondence yields the exact scale."""
        from sphereforge.stages.stage04_depth.depth_alignment import (
            _align_erp_depth_to_panorama_sparse_points,
        )

        h, w = 64, 128
        mono = np.full((h, w), 2.0, dtype=np.float32)
        # Points along -Z at radius 6 -> ratio 3.0 everywhere.
        dirs = np.stack(
            [
                np.linspace(-0.5, 0.5, 40),
                np.linspace(-0.3, 0.3, 40),
                -np.ones(40),
            ],
            axis=1,
        )
        dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
        points = dirs * 6.0
        aligned, scale, _shift = _align_erp_depth_to_panorama_sparse_points(
            mono, points, np.eye(4)
        )
        assert scale == pytest.approx(3.0, rel=1e-3)
        assert aligned.shape == (h, w)

    def test_drifting_ratio_is_rejected(self) -> None:
        """A ratio that drifts with depth indicates wrong correspondences."""
        from sphereforge.stages.stage04_depth.depth_alignment import (
            _align_erp_depth_to_panorama_sparse_points,
        )

        h, w = 64, 128
        # Monocular depth varies smoothly with ERP row.
        mono = np.tile(np.linspace(1.0, 5.0, h, dtype=np.float32)[:, None], (1, w))
        # Sparse points whose radius grows much faster than the mono depth:
        # the ratio then depends systematically on depth.
        rows = np.linspace(0, h - 1, 60)
        theta = np.pi / 2.0 - (rows + 0.5) / h * np.pi
        dirs = np.stack([np.zeros_like(theta), np.sin(theta), -np.cos(theta)], axis=1)
        radius = 2.0 + 40.0 * (rows / h) ** 2
        points = dirs * radius[:, None]

        with pytest.raises(ValueError, match="inconsistent"):
            _align_erp_depth_to_panorama_sparse_points(mono, points, np.eye(4))

    def test_ratio_trend_ignores_constant_ratio(self) -> None:
        """A perfectly constant ratio has no trend by definition."""
        from sphereforge.stages.stage04_depth.depth_alignment import _ratio_trend

        mono = np.linspace(1.0, 5.0, 50)
        assert _ratio_trend(np.full(50, 3.0), mono) == 0.0

    def test_ratio_trend_detects_drift(self) -> None:
        """A ratio that tracks depth has a large trend."""
        from sphereforge.stages.stage04_depth.depth_alignment import _ratio_trend

        mono = np.linspace(1.0, 5.0, 50)
        assert _ratio_trend(mono * 2.0, mono) > 0.9


class TestMetricRescaling:
    """Monocular SfM is scale-free; metric depth must pin the scale down."""

    def test_rescale_scales_points_and_translations(self) -> None:
        """Points and camera translations scale; rotations do not."""
        from sphereforge.stages.stage04_depth.depth_alignment import rescale_sparse_model

        model = {
            "cameras": {1: {"model": "PINHOLE", "width": 8, "height": 8, "params": [4, 4, 4, 4]}},
            "images": {
                1: {
                    "name": "a.png",
                    "qw": 1.0,
                    "qx": 0.0,
                    "qy": 0.0,
                    "qz": 0.0,
                    "tx": 2.0,
                    "ty": -4.0,
                    "tz": 6.0,
                    "camera_id": 1,
                    "point3D_ids": [1],
                }
            },
            "points3D": {1: {"x": 1.0, "y": 2.0, "z": 3.0}},
        }

        out = rescale_sparse_model(model, 0.5)

        assert out["points3D"][1]["x"] == pytest.approx(0.5)
        assert out["points3D"][1]["y"] == pytest.approx(1.0)
        assert out["points3D"][1]["z"] == pytest.approx(1.5)
        assert out["images"][1]["tx"] == pytest.approx(1.0)
        assert out["images"][1]["ty"] == pytest.approx(-2.0)
        assert out["images"][1]["tz"] == pytest.approx(3.0)
        # Quaternion is untouched, and the input model is not mutated.
        assert out["images"][1]["qw"] == 1.0
        assert model["points3D"][1]["x"] == 1.0

    def test_rescale_rejects_bad_scale(self) -> None:
        """A non-positive or non-finite scale is a programming error."""
        from sphereforge.stages.stage04_depth.depth_alignment import rescale_sparse_model

        with pytest.raises(ValueError, match="positive"):
            rescale_sparse_model({"points3D": {}, "images": {}}, 0.0)
        with pytest.raises(ValueError, match="positive"):
            rescale_sparse_model({"points3D": {}, "images": {}}, float("nan"))

    def test_estimate_scale_recovers_known_factor(self) -> None:
        """A reconstruction scaled by k is rescaled back by 1/k."""
        from sphereforge.stages.stage04_depth.depth_alignment import (
            estimate_reconstruction_scale,
        )

        h, w = 64, 128
        # Metric depth: a constant 2.0 m everywhere.
        depth = np.full((h, w), 2.0, dtype=np.float32)

        # A sparse point straight ahead at a *reconstruction* range of 20 units.
        k = 10.0  # reconstruction is 10x too large
        recon_range = 2.0 * k
        model = {
            "cameras": {1: {"model": "PINHOLE", "width": w, "height": h, "params": [60, 60, w / 2, h / 2]}},
            "images": {
                1: {
                    "name": "frame_000.png",
                    "qw": 1.0,
                    "qx": 0.0,
                    "qy": 0.0,
                    "qz": 0.0,
                    "tx": 0.0,
                    "ty": 0.0,
                    "tz": 0.0,
                    "camera_id": 1,
                    "point3D_ids": list(range(1, 21)),
                }
            },
            "points3D": {},
        }
        # Spread points around the viewing sphere at the reconstruction range.
        rng = np.random.RandomState(0)
        dirs = rng.normal(size=(20, 3))
        dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
        for i, d in enumerate(dirs):
            model["points3D"][i + 1] = {
                "x": float(d[0] * recon_range),
                "y": float(d[1] * recon_range),
                "z": float(d[2] * recon_range),
            }

        scale = estimate_reconstruction_scale([depth], ["frame_000.png"], model, None)

        assert scale is not None
        assert scale == pytest.approx(1.0 / k, rel=0.05)


class TestUnalignedFrameFallback:
    """A frame that fails SfM alignment must not stay in raw monocular units."""

    def test_failed_frames_get_median_aligned_scale(self, tmp_path) -> None:
        """Failed frames are rescaled by the median scale of the aligned frames."""
        from sphereforge.common.io import read_depth, write_depth
        from sphereforge.stages.stage04_depth.pipeline import _rescale_unaligned_frames

        paths = [tmp_path / f"f{i}_depth.npy" for i in range(4)]
        raw = np.full((4, 8), 2.0, dtype=np.float32)
        for p in paths:
            write_depth(p, raw)
        results = [
            (paths[0], raw * 1.2, 1.2, 0.0, True),
            (paths[1], raw * 1.4, 1.4, 0.0, True),
            (paths[2], raw * 1.3, 1.3, 0.0, True),
            (paths[3], raw.copy(), 1.0, 0.0, False),
        ]
        out = _rescale_unaligned_frames(results)

        assert out[3][2] == pytest.approx(1.3)
        assert out[3][4] is False  # still reported as unaligned
        assert np.allclose(out[3][1], 2.6)
        assert np.allclose(read_depth(paths[3]), 2.6)
        for got, want in zip(out[:3], results[:3], strict=True):
            assert got[0] == want[0] and got[2] == want[2] and got[4] is True

    def test_no_aligned_frames_leaves_results_unchanged(self, tmp_path) -> None:
        """With nothing to borrow a scale from, results pass through."""
        from sphereforge.stages.stage04_depth.pipeline import _rescale_unaligned_frames

        raw = np.ones((2, 2), dtype=np.float32)
        results = [(tmp_path / "a.npy", raw, 1.0, 0.0, False)]
        assert _rescale_unaligned_frames(results) is results
