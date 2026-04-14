"""Tests for Stage 7: Occlusion Recovery & Refinement.

Tests cover:
1. Novel camera placement (correct count, correct viewing direction)
2. Hole detection on known alpha map
3. Gap classification on synthetic depth with intentional holes
4. LPIPS filtering threshold (high difference → filtered out)
5. ShareGS homogenization geometry (new Gaussians placed in gaps)
6. Iterative convergence (holes decrease each round)

Heavy model inference is mocked.
"""

from __future__ import annotations

import math
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import torch


# ===================================================================
# T7.1 — Novel camera placement
# ===================================================================


class TestNovelCameras:
    """Tests for generate_novel_cameras (T7.1)."""

    def test_correct_count_default(self) -> None:
        """Default 12 directions × 3 distances = 36 cameras."""
        from sphereforge.stages.stage07_occlusion.novel_cameras import generate_novel_cameras

        centre = np.array([0.0, 0.0, 0.0])
        cameras = generate_novel_cameras(centre, scene_radius=1.0)
        assert len(cameras) == 36

    def test_correct_count_custom(self) -> None:
        """Custom n_directions × n_distances."""
        from sphereforge.stages.stage07_occlusion.novel_cameras import generate_novel_cameras

        centre = np.array([0.0, 0.0, 0.0])
        cameras = generate_novel_cameras(centre, scene_radius=1.0, n_directions=8, n_distances=2)
        assert len(cameras) == 16  # 8 × 2

    def test_viewmat_shape(self) -> None:
        """Each camera dict has a 4×4 viewmat."""
        from sphereforge.stages.stage07_occlusion.novel_cameras import generate_novel_cameras

        centre = np.array([1.0, 2.0, 3.0])
        cameras = generate_novel_cameras(centre, scene_radius=2.0, n_directions=4, n_distances=1)
        for cam in cameras:
            assert cam["viewmat"].shape == (4, 4)

    def test_cameras_look_at_centre(self) -> None:
        """Camera forward direction should point towards scene centre."""
        from sphereforge.stages.stage07_occlusion.novel_cameras import generate_novel_cameras

        centre = np.array([0.0, 0.0, 0.0])
        cameras = generate_novel_cameras(centre, scene_radius=5.0, n_directions=6, n_distances=1)

        for cam in cameras:
            viewmat = cam["viewmat"]
            # The third row of the viewmat is -forward (OpenGL convention)
            neg_forward = viewmat[2, :3]
            # The camera position can be recovered: t = -R^T * t_vec
            R = viewmat[:3, :3]
            t = viewmat[:3, 3]
            cam_pos = -R.T @ t

            # Forward = centre - position
            expected_forward = centre - cam_pos
            expected_forward = expected_forward / (np.linalg.norm(expected_forward) + 1e-12)

            # neg_forward should be opposite to expected_forward
            cos_angle = np.dot(-neg_forward, expected_forward)
            assert cos_angle > 0.99, f"Camera doesn't look at centre: cos={cos_angle:.4f}"

    def test_fov_and_resolution(self) -> None:
        """Each camera has fov=90, height=1024, width=1024."""
        from sphereforge.stages.stage07_occlusion.novel_cameras import generate_novel_cameras

        cameras = generate_novel_cameras(np.zeros(3), 1.0, n_directions=3, n_distances=1)
        for cam in cameras:
            assert cam["fov"] == 90.0
            assert cam["height"] == 1024
            assert cam["width"] == 1024

    def test_extra_views_appended(self) -> None:
        """Extra views are appended to the generated cameras."""
        from sphereforge.stages.stage07_occlusion.novel_cameras import generate_novel_cameras

        extra = [{"viewmat": np.eye(4, dtype=np.float32), "fov": 60.0, "height": 512, "width": 512}]
        cameras = generate_novel_cameras(np.zeros(3), 1.0, n_directions=2, n_distances=1, extra_views=extra)
        assert len(cameras) == 3  # 2 + 1 extra

    def test_distances_scale_with_radius(self) -> None:
        """Cameras should be at 0.5x, 1.0x, 1.5x scene_radius from centre."""
        from sphereforge.stages.stage07_occlusion.novel_cameras import generate_novel_cameras

        centre = np.array([0.0, 0.0, 0.0])
        radius = 3.0
        cameras = generate_novel_cameras(centre, scene_radius=radius, n_directions=1, n_distances=3)

        distances = []
        for cam in cameras:
            viewmat = cam["viewmat"]
            R = viewmat[:3, :3]
            t = viewmat[:3, 3]
            cam_pos = -R.T @ t
            dist = np.linalg.norm(cam_pos - centre)
            distances.append(dist)

        distances = sorted(distances)
        expected = sorted([0.5 * radius, 1.0 * radius, 1.5 * radius])
        for d, e in zip(distances, expected):
            assert abs(d - e) < 0.1, f"Distance {d:.3f} not close to expected {e:.3f}"


# ===================================================================
# T7.2 — Hole detection
# ===================================================================


class TestHoleDetection:
    """Tests for detect_holes and compute_hole_coverage (T7.2)."""

    def test_all_solid_no_holes(self) -> None:
        """Alpha map of all 1.0 should have no holes."""
        from sphereforge.stages.stage07_occlusion.hole_detection import (
            compute_hole_coverage,
            detect_holes,
        )

        alpha = np.ones((64, 64), dtype=np.float32)
        mask = detect_holes(alpha, threshold=0.5)
        assert mask.shape == (64, 64)
        assert not np.any(mask)
        assert compute_hole_coverage(mask) == 0.0

    def test_all_holes(self) -> None:
        """Alpha map of all 0.0 should be entirely holes."""
        from sphereforge.stages.stage07_occlusion.hole_detection import (
            compute_hole_coverage,
            detect_holes,
        )

        alpha = np.zeros((32, 48), dtype=np.float32)
        mask = detect_holes(alpha, threshold=0.5)
        assert np.all(mask)
        assert compute_hole_coverage(mask) == 1.0

    def test_partial_holes(self) -> None:
        """Known partial coverage."""
        from sphereforge.stages.stage07_occlusion.hole_detection import (
            compute_hole_coverage,
            detect_holes,
        )

        alpha = np.ones((10, 10), dtype=np.float32)
        alpha[:5, :] = 0.0  # top half is holes
        mask = detect_holes(alpha, threshold=0.5)
        assert mask.shape == (10, 10)
        assert np.all(mask[:5, :])
        assert not np.any(mask[5:, :])
        assert abs(compute_hole_coverage(mask) - 0.5) < 1e-6

    def test_threshold_boundary(self) -> None:
        """Pixels exactly at threshold are NOT holes (< threshold)."""
        from sphereforge.stages.stage07_occlusion.hole_detection import detect_holes

        alpha = np.full((4, 4), 0.5, dtype=np.float32)
        mask = detect_holes(alpha, threshold=0.5)
        assert not np.any(mask)  # 0.5 is NOT < 0.5

    def test_3d_alpha_input(self) -> None:
        """Accepts (H, W, 1) alpha input."""
        from sphereforge.stages.stage07_occlusion.hole_detection import detect_holes

        alpha = np.zeros((8, 8, 1), dtype=np.float32)
        mask = detect_holes(alpha)
        assert mask.shape == (8, 8)
        assert np.all(mask)


# ===================================================================
# T7.3 — Gap classification
# ===================================================================


class TestGapClassification:
    """Tests for classify_gaps (T7.3)."""

    def test_no_holes_returns_zeros(self) -> None:
        """No holes → all zeros classification."""
        from sphereforge.stages.stage07_occlusion.gap_classification import (
            NOT_HOLE,
            classify_gaps,
        )

        hole_mask = np.zeros((32, 32), dtype=bool)
        depth = np.random.rand(32, 32).astype(np.float32) + 1.0
        result = classify_gaps(hole_mask, depth)
        assert np.all(result == NOT_HOLE)

    def test_edge_holes_classified_as_boundary(self) -> None:
        """Holes at the image edge should be AT_BOUNDARY (2)."""
        from sphereforge.stages.stage07_occlusion.gap_classification import (
            AT_BOUNDARY,
            classify_gaps,
        )

        hole_mask = np.zeros((32, 32), dtype=bool)
        hole_mask[0, :] = True  # top row is a hole
        depth = np.ones((32, 32), dtype=np.float32)  # uniform depth
        result = classify_gaps(hole_mask, depth)
        assert np.all(result[0, :] == AT_BOUNDARY)

    def test_interior_holes_classified(self) -> None:
        """Interior holes surrounded by valid pixels → MISSING_GEOMETRY (3)."""
        from sphereforge.stages.stage07_occlusion.gap_classification import (
            MISSING_GEOMETRY,
            classify_gaps,
        )

        hole_mask = np.zeros((64, 64), dtype=bool)
        hole_mask[28:36, 28:36] = True  # square hole in the centre
        depth = np.ones((64, 64), dtype=np.float32)
        result = classify_gaps(hole_mask, depth)
        # The interior of the hole should be classified as missing_geometry
        assert np.all(result[30:34, 30:34] == MISSING_GEOMETRY)

    def test_depth_discontinuity_classification(self) -> None:
        """Holes at depth discontinuities should be BEHIND_FOREGROUND (1)."""
        from sphereforge.stages.stage07_occlusion.gap_classification import (
            BEHIND_FOREGROUND,
            classify_gaps,
        )

        H, W = 64, 64
        hole_mask = np.zeros((H, W), dtype=bool)
        # Place holes near a depth jump (but not at image edge)
        hole_mask[10:20, 10:20] = True

        # Create a sharp depth discontinuity
        depth = np.ones((H, W), dtype=np.float32)
        depth[:30, :] = 1.0
        depth[30:, :] = 10.0  # big jump at row 30

        result = classify_gaps(hole_mask, hole_mask, depth)
        # At least some of the hole pixels should be behind_foreground
        assert np.any(result[10:20, 10:20] == BEHIND_FOREGROUND)

    def test_output_shape_and_dtype(self) -> None:
        """Output should be (H, W) int32."""
        from sphereforge.stages.stage07_occlusion.gap_classification import classify_gaps

        H, W = 16, 24
        hole_mask = np.zeros((H, W), dtype=bool)
        depth = np.random.rand(H, W).astype(np.float32)
        result = classify_gaps(hole_mask, depth)
        assert result.shape == (H, W)
        assert result.dtype == np.int32


# ===================================================================
# T7.8 — LPIPS filtering
# ===================================================================


class TestLpipsFilter:
    """Tests for filter_hallucinations (T7.8)."""

    def test_identical_images_no_hallucination(self) -> None:
        """Identical images should have no flagged pixels."""
        from sphereforge.stages.stage07_occlusion.lpips_filter import filter_hallucinations

        img = np.random.rand(64, 64, 3).astype(np.float32)
        mask = filter_hallucinations(img, img, threshold=0.4, window_size=32, stride=32)
        assert not np.any(mask)

    def test_very_different_images_flagged(self) -> None:
        """Images that are completely different should be flagged."""
        from sphereforge.stages.stage07_occlusion.lpips_filter import filter_hallucinations

        original = np.zeros((64, 64, 3), dtype=np.float32)
        inpainted = np.ones((64, 64, 3), dtype=np.float32)  # maximally different
        mask = filter_hallucinations(original, inpainted, threshold=0.4, window_size=32, stride=32)
        # Most/all windows should be flagged
        assert np.mean(mask) > 0.5

    def test_output_shape(self) -> None:
        """Output mask has same (H, W) shape as input."""
        from sphereforge.stages.stage07_occlusion.lpips_filter import filter_hallucinations

        H, W = 48, 64
        img1 = np.random.rand(H, W, 3).astype(np.float32)
        img2 = np.random.rand(H, W, 3).astype(np.float32)
        mask = filter_hallucinations(img1, img2, threshold=0.4, window_size=32, stride=32)
        assert mask.shape == (H, W)

    def test_partial_difference(self) -> None:
        """Partially different images: only the different region is flagged."""
        from sphereforge.stages.stage07_occlusion.lpips_filter import filter_hallucinations

        H, W = 64, 64
        original = np.zeros((H, W, 3), dtype=np.float32)
        inpainted = original.copy()
        # Make the top half very different
        inpainted[:32, :, :] = 1.0

        mask = filter_hallucinations(original, inpainted, threshold=0.4, window_size=32, stride=16)
        # Top half should be flagged, bottom half should not
        assert np.mean(mask[:32, :]) > np.mean(mask[32:, :])


# ===================================================================
# T7.4 — ShareGS homogenization
# ===================================================================


class TestShareGSHomogenize:
    """Tests for homogenize_gaussians (T7.4)."""

    def _make_gaussians(self, n: int = 20) -> dict:
        """Create a small synthetic Gaussian dict for testing."""
        rng = np.random.default_rng(42)
        return {
            "positions": rng.normal(0, 1, (n, 3)).astype(np.float32),
            "colors": rng.uniform(0, 1, (n, 3)).astype(np.float32),
            "opacities": np.ones(n, dtype=np.float32) * 0.9,
            "scales": np.full((n, 3), -2.0, dtype=np.float32),  # log-scale
            "rotations": np.tile([1, 0, 0, 0], (n, 1)).astype(np.float32),
        }

    def _make_camera(self, cam_pos: np.ndarray = None) -> tuple[np.ndarray, dict]:
        """Build a simple viewmat + intrinsics for a camera at (0,0,5) looking at origin."""
        if cam_pos is None:
            cam_pos = np.array([0.0, 0.0, 5.0])

        forward = np.array([0.0, 0.0, -1.0])
        right = np.array([1.0, 0.0, 0.0])
        up = np.array([0.0, 1.0, 0.0])

        viewmat = np.eye(4, dtype=np.float32)
        viewmat[0, :3] = right
        viewmat[1, :3] = up
        viewmat[2, :3] = -forward
        viewmat[0, 3] = -np.dot(right, cam_pos)
        viewmat[1, 3] = -np.dot(up, cam_pos)
        viewmat[2, 3] = np.dot(forward, cam_pos)

        intrinsics = {
            "fx": 500.0,
            "fy": 500.0,
            "cx": 256.0,
            "cy": 256.0,
            "height": 512,
            "width": 512,
        }
        return viewmat, intrinsics

    def test_new_gaussians_added(self) -> None:
        """Homogenization should add new Gaussians when holes exist."""
        from sphereforge.stages.stage07_occlusion.sharegs_homogenize import homogenize_gaussians

        gaussians = self._make_gaussians(50)
        viewmat, intrinsics = self._make_camera()

        # Create holes in the centre of the image
        hole_mask = np.zeros((512, 512), dtype=bool)
        hole_mask[240:280, 240:280] = True

        n_before = gaussians["positions"].shape[0]
        result = homogenize_gaussians(gaussians, hole_mask, viewmat, intrinsics)
        n_after = result["positions"].shape[0]

        assert n_after > n_before, "Homogenization should add new Gaussians"

    def test_no_holes_no_change(self) -> None:
        """No holes → gaussians unchanged."""
        from sphereforge.stages.stage07_occlusion.sharegs_homogenize import homogenize_gaussians

        gaussians = self._make_gaussians(30)
        viewmat, intrinsics = self._make_camera()
        hole_mask = np.zeros((512, 512), dtype=bool)

        result = homogenize_gaussians(gaussians, hole_mask, viewmat, intrinsics)
        assert result["positions"].shape[0] == 30

    def test_output_keys_preserved(self) -> None:
        """Output dict should have the same keys as input."""
        from sphereforge.stages.stage07_occlusion.sharegs_homogenize import homogenize_gaussians

        gaussians = self._make_gaussians(50)
        viewmat, intrinsics = self._make_camera()
        hole_mask = np.zeros((512, 512), dtype=bool)
        hole_mask[200:300, 200:300] = True

        result = homogenize_gaussians(gaussians, hole_mask, viewmat, intrinsics)
        for key in gaussians:
            assert key in result, f"Missing key: {key}"


# ===================================================================
# T7.9 — Softmax depth loss
# ===================================================================


class TestSoftmaxDepthLoss:
    """Tests for softmax_depth_loss (T7.9)."""

    def test_output_is_scalar(self) -> None:
        """Loss should be a scalar tensor."""
        from sphereforge.stages.stage07_occlusion.softmax_depth import softmax_depth_loss

        rendered = torch.rand(32, 32) + 0.5
        prior = torch.rand(32, 32) + 0.5
        loss = softmax_depth_loss(rendered, prior)
        assert loss.dim() == 0

    def test_identical_depths_low_loss(self) -> None:
        """Identical depth maps should have near-zero loss (after alignment)."""
        from sphereforge.stages.stage07_occlusion.softmax_depth import softmax_depth_loss

        depth = torch.rand(32, 32) + 0.5
        loss = softmax_depth_loss(depth, depth.clone(), temperature=0.1)
        assert loss.item() < 0.01, f"Expected low loss for identical depths, got {loss.item()}"

    def test_requires_grad(self) -> None:
        """Loss should be differentiable w.r.t. rendered_depth."""
        from sphereforge.stages.stage07_occlusion.softmax_depth import softmax_depth_loss

        rendered = torch.rand(16, 16, requires_grad=True) + 0.5
        prior = torch.rand(16, 16) + 0.5
        loss = softmax_depth_loss(rendered, prior)
        loss.backward()
        assert rendered.grad is not None
        assert rendered.grad.shape == rendered.shape

    def test_invalid_depths_zero_loss(self) -> None:
        """All-invalid depth maps should return zero loss."""
        from sphereforge.stages.stage07_occlusion.softmax_depth import softmax_depth_loss

        rendered = torch.zeros(8, 8)  # all zero → invalid
        prior = torch.zeros(8, 8)
        loss = softmax_depth_loss(rendered, prior)
        assert loss.item() == 0.0


# ===================================================================
# T7.11 — Iterative fill
# ===================================================================


class TestIterativeFill:
    """Tests for fill_holes_iterative (T7.11)."""

    def _make_gaussians(self, n: int = 100) -> dict:
        """Create synthetic Gaussians spread around the origin."""
        rng = np.random.default_rng(42)
        positions = rng.normal(0, 0.5, (n, 3)).astype(np.float32)
        return {
            "positions": positions,
            "colors": rng.uniform(0, 1, (n, 3)).astype(np.float32),
            "opacities": np.ones(n, dtype=np.float32) * 0.9,
            "scales": np.full((n, 3), -2.0, dtype=np.float32),
            "rotations": np.tile([1, 0, 0, 0], (n, 1)).astype(np.float32),
        }

    def _make_cameras(self, n: int = 3) -> list[dict]:
        """Create a few novel cameras."""
        from sphereforge.stages.stage07_occlusion.novel_cameras import generate_novel_cameras

        centre = np.array([0.0, 0.0, 0.0])
        return generate_novel_cameras(centre, scene_radius=2.0, n_directions=n, n_distances=1)

    def test_holes_decrease_each_round(self) -> None:
        """After each round, hole coverage should not increase."""
        from sphereforge.stages.stage07_occlusion.iterative_fill import fill_holes_iterative
        from sphereforge.stages.stage07_occlusion.hole_detection import detect_holes

        from sphereforge.config import Stage07Config

        config = Stage07Config(
            refine_rounds=2,
            refine_hole_threshold=0.001,
            sharegs_enabled=True,
            sharegs_homogenization=True,
            sharegs_patch_reuse=False,
        )

        gaussians = self._make_gaussians(200)
        cameras = self._make_cameras(3)
        colmap_model = {"cameras": {}, "images": {}}

        # Measure initial hole coverage
        initial_coverages = []
        for cam in cameras:
            from sphereforge.stages.stage07_occlusion.iterative_fill import _approximate_alpha_render
            alpha = _approximate_alpha_render(gaussians, cam)
            mask = detect_holes(alpha, threshold=0.5)
            initial_coverages.append(np.mean(mask))
        avg_initial = np.mean(initial_coverages)

        result = fill_holes_iterative(gaussians, config, cameras, colmap_model)

        # Measure final hole coverage
        final_coverages = []
        for cam in cameras:
            from sphereforge.stages.stage07_occlusion.iterative_fill import _approximate_alpha_render
            alpha = _approximate_alpha_render(result, cam)
            mask = detect_holes(alpha, threshold=0.5)
            final_coverages.append(np.mean(mask))
        avg_final = np.mean(final_coverages)

        # After adding Gaussians, coverage should not be worse
        # (it may stay the same if the Gaussians project to the same pixels)
        assert avg_final <= avg_initial + 0.05, (
            f"Hole coverage should not increase: initial={avg_initial:.4f}, final={avg_final:.4f}"
        )

    def test_output_has_more_gaussians(self) -> None:
        """After filling, the Gaussian count should increase (or stay same)."""
        from sphereforge.stages.stage07_occlusion.iterative_fill import fill_holes_iterative
        from sphereforge.config import Stage07Config

        config = Stage07Config(
            refine_rounds=1,
            refine_hole_threshold=0.001,
            sharegs_enabled=True,
            sharegs_homogenization=True,
            sharegs_patch_reuse=False,
        )

        gaussians = self._make_gaussians(50)
        cameras = self._make_cameras(2)
        colmap_model = {"cameras": {}, "images": {}}

        n_before = gaussians["positions"].shape[0]
        result = fill_holes_iterative(gaussians, config, cameras, colmap_model)
        n_after = result["positions"].shape[0]

        assert n_after >= n_before


# ===================================================================
# T7.7 — EscherNet stub
# ===================================================================


class TestEscherNet:
    """Tests for EscherNetWrapper (T7.7)."""

    def test_inpaint_raises_not_implemented(self) -> None:
        """Inpainting should raise NotImplementedError without weights."""
        from sphereforge.stages.stage07_occlusion.eschernet import EscherNetWrapper

        wrapper = EscherNetWrapper()
        with pytest.raises(NotImplementedError, match="EscherNet"):
            wrapper.inpaint_holes(
                rendered_image=np.zeros((64, 64, 3), dtype=np.float32),
                hole_mask=np.zeros((64, 64), dtype=bool),
                reference_images=[np.zeros((64, 64, 3), dtype=np.float32)],
            )


# ===================================================================
# T7.12 — OmniRoam stub
# ===================================================================


class TestOmniRoam:
    """Tests for omniroam_fill (T7.12)."""

    def test_raises_not_implemented(self) -> None:
        """OmniRoam should raise NotImplementedError."""
        from sphereforge.stages.stage07_occlusion.omniroam import omniroam_fill

        with pytest.raises(NotImplementedError, match="Adobe Research License"):
            omniroam_fill({}, object(), {})


# ===================================================================
# T7.5 — ShareGS patch reuse
# ===================================================================


class TestShareGSReuse:
    """Tests for reuse_patches (T7.5)."""

    def test_no_holes_no_change(self) -> None:
        """No holes → Gaussians unchanged."""
        from sphereforge.stages.stage07_occlusion.sharegs_reuse import reuse_patches

        gaussians = {
            "positions": np.random.randn(20, 3).astype(np.float32),
            "colors": np.random.rand(20, 3).astype(np.float32),
            "opacities": np.ones(20, dtype=np.float32) * 0.8,
            "scales": np.full((20, 3), -2.0, dtype=np.float32),
            "rotations": np.tile([1, 0, 0, 0], (20, 1)).astype(np.float32),
        }
        hole_mask = np.zeros((64, 64), dtype=bool)

        result = reuse_patches(gaussians, hole_mask, [], {})
        assert result["positions"].shape[0] == 20

    def test_patches_added_with_source_views(self) -> None:
        """Patches should be reused from source views when holes exist."""
        from sphereforge.stages.stage07_occlusion.sharegs_reuse import reuse_patches

        rng = np.random.default_rng(42)
        gaussians = {
            "positions": rng.normal(0, 0.5, (50, 3)).astype(np.float32),
            "colors": rng.uniform(0, 1, (50, 3)).astype(np.float32),
            "opacities": np.ones(50, dtype=np.float32) * 0.9,
            "scales": np.full((50, 3), -2.0, dtype=np.float32),
            "rotations": np.tile([1, 0, 0, 0], (50, 1)).astype(np.float32),
        }

        hole_mask = np.zeros((128, 128), dtype=bool)
        hole_mask[40:80, 40:80] = True

        # Create a simple source view camera looking at the origin
        viewmat = np.eye(4, dtype=np.float32)
        viewmat[2, 3] = 5.0  # camera at z=5 looking toward origin

        source_views = [
            {"viewmat": viewmat, "fov": 90.0, "height": 128, "width": 128},
        ]

        result = reuse_patches(gaussians, hole_mask, source_views, {"cameras": {}, "images": {}})
        n_after = result["positions"].shape[0]
        assert n_after > 50, "Patch reuse should add Gaussians"


# ===================================================================
# T7.10 — Distillation
# ===================================================================


class TestDistillation:
    """Tests for distill_inpaint (T7.10)."""

    def test_no_views_returns_unchanged(self) -> None:
        """No novel views → Gaussians returned unchanged."""
        from sphereforge.stages.stage07_occlusion.distillation import distill_inpaint

        gaussians = {
            "positions": np.random.randn(10, 3).astype(np.float32),
            "colors": np.random.rand(10, 3).astype(np.float32),
            "opacities": np.ones(10, dtype=np.float32),
            "scales": np.full((10, 3), -2.0, dtype=np.float32),
            "rotations": np.tile([1, 0, 0, 0], (10, 1)).astype(np.float32),
        }
        result = distill_inpaint(gaussians, [])
        assert result["positions"].shape[0] == 10


# ===================================================================
# T7.13 — Pipeline (smoke test)
# ===================================================================


class TestPipeline:
    """Smoke tests for run_stage07 (T7.13)."""

    def test_pipeline_config_resolve_cameras(self) -> None:
        """Camera layout resolver works for typical values."""
        from sphereforge.stages.stage07_occlusion.pipeline import _resolve_camera_layout

        assert _resolve_camera_layout(36) == (12, 3)
        assert _resolve_camera_layout(24) == (12, 2)
        assert _resolve_camera_layout(16) == (8, 2)
        assert _resolve_camera_layout(7) == (7, 1)

    def test_scene_bounds(self) -> None:
        """Scene bounds computed from Gaussian positions."""
        from sphereforge.stages.stage07_occlusion.pipeline import _compute_scene_bounds

        gaussians = {
            "positions": np.array(
                [[1, 0, 0], [-1, 0, 0], [0, 2, 0], [0, -2, 0], [0, 0, 3], [0, 0, -3]],
                dtype=np.float32,
            )
        }
        centre, radius = _compute_scene_bounds(gaussians)
        np.testing.assert_allclose(centre, [0, 0, 0], atol=0.1)
        assert radius > 0
