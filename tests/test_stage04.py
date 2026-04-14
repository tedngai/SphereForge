"""Tests for Stage 4: Dense Depth Estimation (T4.1–T4.7).

All model inference is mocked — no GPU required.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

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

        aligned, scale, shift = align_depth_to_colmap(
            depth, sparse_model, "test.png", rpg360_anchor=anchor
        )
        assert aligned.shape == (h, w)
        assert scale > 0


# ---------------------------------------------------------------------------
# T4.5 — Model Factory
# ---------------------------------------------------------------------------


class TestModelFactory:
    """Tests for model_factory.get_depth_estimator."""

    def test_panda_returns_correct_type(self) -> None:
        """Factory should return PanDAModel for 'panda'."""
        from sphereforge.stages.stage04_depth.model_factory import (
            get_depth_estimator,
        )
        from sphereforge.stages.stage04_depth.panda_model import PanDAModel

        model = get_depth_estimator("panda")
        assert isinstance(model, PanDAModel)

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

        with pytest.raises(NotImplementedError, match="DA360"):
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
    @patch("sphereforge.stages.stage04_depth.pipeline.write_depth")
    @patch("sphereforge.stages.stage04_depth.pipeline.read_image")
    def test_pipeline_flow(
        self,
        mock_read_image: MagicMock,
        mock_write_depth: MagicMock,
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

            # Verify estimator was created
            mock_get_estimator.assert_called_once()

            # Verify depth was estimated for each frame
            assert mock_estimator.estimate_depth.call_count == 3

            # Verify alignment was called for each frame
            assert mock_align.call_count == 3

            # Verify depth was written for each frame
            assert mock_write_depth.call_count >= 3

            # Verify scene analysis was called
            mock_analyze.assert_called_once()

            # Verify return structure
            assert "depth_paths" in result
            assert "scene_params" in result
            assert len(result["depth_paths"]) == 3

    @patch("sphereforge.stages.stage04_depth.pipeline.analyze_depth_scene")
    @patch("sphereforge.stages.stage04_depth.pipeline.align_depth_to_colmap")
    @patch("sphereforge.stages.stage04_depth.pipeline.get_depth_estimator")
    @patch("sphereforge.stages.stage04_depth.pipeline.log_task_completion")
    @patch("sphereforge.stages.stage04_depth.pipeline.write_depth")
    @patch("sphereforge.stages.stage04_depth.pipeline.read_image")
    def test_pipeline_fallback_on_not_implemented(
        self,
        mock_read_image: MagicMock,
        mock_write_depth: MagicMock,
        mock_log_task: MagicMock,
        mock_get_estimator: MagicMock,
        mock_align: MagicMock,
        mock_analyze: MagicMock,
    ) -> None:
        """Pipeline should write zero depth when estimator raises NotImplementedError."""
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

            result = run_stage04(
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

            # Should still return results (fallback zero depth)
            assert "depth_paths" in result
            assert len(result["depth_paths"]) == 1


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
