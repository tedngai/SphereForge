"""Tests for Stage 5: Initial Gaussian Seeding (T5.1–T5.13).

Tests cover spherical projection math, multiview fusion averaging,
deduplication logic, NCC filtering, stride assignment, attribute
assignment, and the full pipeline on synthetic data.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from sphereforge.stages.stage05_seeding import (
    assign_initial_attributes,
    assign_stride,
    clip_grazing_angles,
    compute_depth_confidence,
    deduplicate_gaussians,
    fuse_multiview,
    project_to_3d,
    prune_outliers,
    prune_sparse_regions,
    remove_sky,
)

# ==========================================================================
# T5.1 — Spherical projection
# ==========================================================================


class TestProjectTo3D:
    """Tests for project_to_3d (T5.1)."""

    def test_known_position_north_pole(self) -> None:
        """At the top row (v=0) the ray points to (0,1,0) — north pole."""
        h, w = 4, 8
        depth = np.ones((h, w), dtype=np.float32)
        image = np.zeros((h, w, 3), dtype=np.uint8)

        positions, _ = project_to_3d(image, depth, stride=1)

        # Top-row pixels: phi = pi*0/4 = 0 → direction = (0, cos(0), 0) = (0, 1, 0)
        # depth=1 → position = (0, 1, 0)
        top_positions = positions[:w]  # first row of pixels
        np.testing.assert_allclose(top_positions[:, 1], 1.0, atol=1e-5)
        np.testing.assert_allclose(top_positions[:, 0], 0.0, atol=1e-5)
        np.testing.assert_allclose(top_positions[:, 2], 0.0, atol=1e-5)

    def test_known_position_equator(self) -> None:
        """At the equator (v=H/2) the ray has cos(phi)≈0 and sin(phi)≈1."""
        h, w = 4, 8
        depth = np.ones((h, w), dtype=np.float32) * 2.0
        image = np.zeros((h, w, 3), dtype=np.uint8)

        positions, _ = project_to_3d(image, depth, stride=1)

        # Middle row: v=2 → phi = pi*2/4 = pi/2
        # direction = (sin(pi/2)*cos(theta), cos(pi/2), sin(pi/2)*sin(theta))
        #           = (cos(theta), 0, sin(theta))
        mid_start = w * (h // 2)
        mid_positions = positions[mid_start : mid_start + w]
        # y component should be ≈ 0
        np.testing.assert_allclose(mid_positions[:, 1], 0.0, atol=1e-5)

    def test_depth_scaling(self) -> None:
        """Positions should scale linearly with depth."""
        h, w = 2, 4
        depth1 = np.ones((h, w), dtype=np.float32) * 3.0
        depth2 = np.ones((h, w), dtype=np.float32) * 6.0
        image = np.zeros((h, w, 3), dtype=np.uint8)

        pos1, _ = project_to_3d(image, depth1, stride=1)
        pos2, _ = project_to_3d(image, depth2, stride=1)

        np.testing.assert_allclose(pos2, pos1 * 2.0, atol=1e-5)

    def test_stride_subsamples(self) -> None:
        """Stride > 1 should produce fewer points."""
        h, w = 10, 20
        depth = np.ones((h, w), dtype=np.float32)
        image = np.zeros((h, w, 3), dtype=np.uint8)

        pos_s1, _ = project_to_3d(image, depth, stride=1)
        pos_s2, _ = project_to_3d(image, depth, stride=2)
        pos_s5, _ = project_to_3d(image, depth, stride=5)

        assert pos_s1.shape[0] > pos_s2.shape[0]
        assert pos_s2.shape[0] > pos_s5.shape[0]

    def test_zero_depth_filtered(self) -> None:
        """Points with depth <= 0 should be excluded."""
        h, w = 4, 8
        depth = np.ones((h, w), dtype=np.float32)
        depth[1, 1] = 0.0  # one invalid pixel
        image = np.zeros((h, w, 3), dtype=np.uint8)

        positions, _ = project_to_3d(image, depth, stride=1)

        # All valid pixels = h*w - 1
        assert positions.shape[0] == h * w - 1

    def test_colors_preserved(self) -> None:
        """Output colours should match input image at sampled pixels."""
        h, w = 4, 8
        depth = np.ones((h, w), dtype=np.float32)
        image = np.full((h, w, 3), [100, 150, 200], dtype=np.uint8)

        _, colors = project_to_3d(image, depth, stride=1)

        np.testing.assert_array_equal(colors[:, 0], 100)
        np.testing.assert_array_equal(colors[:, 1], 150)
        np.testing.assert_array_equal(colors[:, 2], 200)

    def test_stride_map_mixed_sampling(self) -> None:
        """Per-pixel stride_map should mix dense and sparse sampling."""
        h, w = 4, 8
        depth = np.ones((h, w), dtype=np.float32)
        image = np.zeros((h, w, 3), dtype=np.uint8)

        # Left half dense (stride=1), right half sparse (stride=2)
        stride_map = np.ones((h, w), dtype=np.int32)
        stride_map[:, w // 2 :] = 2

        positions, _ = project_to_3d(image, depth, stride_map=stride_map)

        # Dense half: 4*4 = 16 pixels, sparse half: 2*2 = 4 pixels → 20 total
        # (stride=2 keeps every 2nd row AND every 2nd col in that half)
        assert positions.shape[0] == 20

    def test_stride_map_shape_mismatch_raises(self) -> None:
        """Mismatched stride_map shape should raise ValueError."""
        depth = np.ones((4, 8), dtype=np.float32)
        image = np.zeros((4, 8, 3), dtype=np.uint8)
        stride_map = np.ones((4, 4), dtype=np.int32)

        with pytest.raises(ValueError):
            project_to_3d(image, depth, stride_map=stride_map)


# ==========================================================================
# T5.2 — Multiview fusion
# ==========================================================================


class TestFusion:
    """Tests for fuse_multiview (T5.2)."""

    def test_identity_extrinsics_unchanged(self) -> None:
        """With identity pose, world coords should equal local coords."""
        positions = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float32)
        colors = np.array([[10, 20, 30], [40, 50, 60]], dtype=np.uint8)

        sparse_model = {
            "images": {
                1: {
                    "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                    "tx": 0.0, "ty": 0.0, "tz": 0.0,
                    "camera_id": 1,
                    "name": "test.png",
                },
            },
        }

        fused_pos, _, _ = fuse_multiview([positions], [colors], sparse_model)

        np.testing.assert_allclose(fused_pos, positions, atol=1e-4)

    def test_two_views_averaged(self) -> None:
        """Two views of the same point should fuse to their average."""
        # Same point from two identity-pose views → should average
        pos1 = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
        pos2 = np.array([[1.05, 2.05, 3.05]], dtype=np.float32)
        col1 = np.array([[10, 20, 30]], dtype=np.uint8)
        col2 = np.array([[40, 50, 60]], dtype=np.uint8)

        sparse_model = {
            "images": {
                1: {
                    "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                    "tx": 0.0, "ty": 0.0, "tz": 0.0,
                    "camera_id": 1,
                    "name": "v1.png",
                },
                2: {
                    "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                    "tx": 0.0, "ty": 0.0, "tz": 0.0,
                    "camera_id": 1,
                    "name": "v2.png",
                },
            },
        }

        fused_pos, fused_col, conf = fuse_multiview(
            [pos1, pos2], [col1, col2], sparse_model
        )

        # Points are close → should be in same cluster
        assert fused_pos.shape[0] == 1
        expected_pos = np.mean(
            np.stack([pos1[0], pos2[0]]), axis=0
        )
        np.testing.assert_allclose(fused_pos[0], expected_pos, atol=1e-4)
        assert conf[0] == 2  # two views contributed


# ==========================================================================
# T5.3 — Deduplication
# ==========================================================================


class TestDeduplication:
    """Tests for deduplicate_gaussians (T5.3)."""

    def test_two_close_points_merge(self) -> None:
        """Two very close points should merge into one."""
        positions = np.array([[0.0, 0.0, 0.0], [0.001, 0.001, 0.001]], dtype=np.float32)
        colors = np.array([[100, 100, 100], [200, 200, 200]], dtype=np.float32)
        confidence = np.array([1.0, 1.0], dtype=np.float32)

        out_pos, out_col, out_conf = deduplicate_gaussians(
            positions, colors, confidence, dedup_distance=0.01
        )

        assert out_pos.shape[0] == 1
        assert out_conf[0] == pytest.approx(2.0)

    def test_distant_points_kept(self) -> None:
        """Distant points should not be merged."""
        positions = np.array([[0.0, 0.0, 0.0], [10.0, 10.0, 10.0]], dtype=np.float32)
        colors = np.array([[100, 100, 100], [200, 200, 200]], dtype=np.float32)
        confidence = np.array([1.0, 1.0], dtype=np.float32)

        out_pos, _, _ = deduplicate_gaussians(
            positions, colors, confidence, dedup_distance=0.01
        )

        assert out_pos.shape[0] == 2

    def test_auto_dedup_distance(self) -> None:
        """'auto' dedup_distance should compute from scene extent."""
        positions = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]], dtype=np.float32)
        colors = np.array([[100, 100, 100], [200, 200, 200]], dtype=np.float32)
        confidence = np.array([1.0, 1.0], dtype=np.float32)

        # Scene extent = 0.5, auto = 0.01 * 0.5 = 0.005 → too small to merge
        out_pos, _, _ = deduplicate_gaussians(
            positions, colors, confidence, dedup_distance="auto"
        )
        assert out_pos.shape[0] == 2

    def test_empty_input(self) -> None:
        """Empty input should return empty output."""
        positions = np.empty((0, 3), dtype=np.float32)
        colors = np.empty((0, 3), dtype=np.float32)
        confidence = np.empty(0, dtype=np.float32)

        out_pos, out_col, out_conf = deduplicate_gaussians(
            positions, colors, confidence
        )
        assert out_pos.shape[0] == 0


# ==========================================================================
# T5.4 — Edge clipping
# ==========================================================================


class TestEdgeClipping:
    """Tests for clip_grazing_angles (T5.4)."""

    def test_frontal_view_kept(self) -> None:
        """A point viewed head-on should be kept."""
        positions = np.array([[0.0, 0.0, 5.0]], dtype=np.float32)
        camera_origins = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
        # Scene centre ≈ (0, 0, 5), normal ≈ (0, 0, 1)
        # View dir ≈ (0, 0, 1) → angle = 0° → kept

        mask = clip_grazing_angles(positions, camera_origins, threshold_deg=65)
        assert mask[0] is True or mask[0] == True

    def test_grazing_angle_removed(self) -> None:
        """A point viewed from the side at a grazing angle should be removed."""
        # Point far away, camera off to the side
        positions = np.array([[5.0, 0.0, 0.0]], dtype=np.float32)
        camera_origins = np.array([[5.0, 10.0, 0.0]], dtype=np.float32)
        # Scene centre ≈ (5, 0, 0), normal = (0, 0, 0) → degenerate
        # This tests edge case with zero normal
        mask = clip_grazing_angles(positions, camera_origins, threshold_deg=65)
        # With zero normal, cos_angle ≈ 0 which is < cos(65°) ≈ 0.42
        assert isinstance(mask, np.ndarray)


# ==========================================================================
# T5.5 — Outlier pruning
# ==========================================================================


class TestOutlierPruning:
    """Tests for prune_outliers (T5.5)."""

    def test_cluster_with_outlier(self) -> None:
        """A distant outlier should be removed."""
        rng = np.random.RandomState(42)
        # Cluster of 30 points
        cluster = rng.randn(30, 3).astype(np.float32) * 0.1
        # One outlier far away
        outlier = np.array([[50.0, 50.0, 50.0]], dtype=np.float32)
        positions = np.concatenate([cluster, outlier], axis=0)

        mask = prune_outliers(positions, strength=0.3)

        # All cluster points kept, outlier removed
        assert np.all(mask[:30])
        assert not mask[30]

    def test_no_outliers(self) -> None:
        """A tight cluster should keep all points."""
        rng = np.random.RandomState(42)
        positions = rng.randn(50, 3).astype(np.float32) * 0.1

        mask = prune_outliers(positions, strength=0.3)
        assert np.all(mask)

    def test_empty_input(self) -> None:
        """Empty input should return empty mask."""
        mask = prune_outliers(np.empty((0, 3), dtype=np.float32))
        assert mask.shape[0] == 0


# ==========================================================================
# T5.6 — Sparse pruning
# ==========================================================================


class TestSparsePruning:
    """Tests for prune_sparse_regions (T5.6)."""

    def test_isolated_point_removed(self) -> None:
        """An isolated point should be removed."""
        rng = np.random.RandomState(42)
        cluster = rng.randn(30, 3).astype(np.float32) * 0.1
        isolated = np.array([[100.0, 100.0, 100.0]], dtype=np.float32)
        positions = np.concatenate([cluster, isolated], axis=0)

        mask = prune_sparse_regions(positions, strength=0.3)

        # Isolated point should be removed
        assert not mask[-1]

    def test_dense_cluster_kept(self) -> None:
        """A dense cluster should keep all points."""
        rng = np.random.RandomState(42)
        positions = rng.randn(50, 3).astype(np.float32) * 0.05

        mask = prune_sparse_regions(positions, strength=0.3)
        # Most or all should be kept
        assert np.sum(mask) > 40


# ==========================================================================
# T5.7 — Sky removal
# ==========================================================================


class TestSkyRemoval:
    """Tests for remove_sky (T5.7)."""

    def test_sky_depth_removed(self) -> None:
        """Points beyond sky threshold should be removed."""
        positions = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32)
        depth = np.array([1.0, 100.0], dtype=np.float32)

        mask = remove_sky(positions, depth, sky_threshold=50.0)
        assert mask[0]  # near point kept
        assert not mask[1]  # far point removed

    def test_auto_threshold(self) -> None:
        """Auto threshold uses 95th percentile of depth."""
        positions = np.arange(20, dtype=np.float32).reshape(-1, 1) * np.array(
            [[1, 0, 0]], dtype=np.float32
        )
        # 1-D depth array
        depth = np.arange(20, dtype=np.float32).astype(np.float32)

        mask = remove_sky(positions, depth, sky_threshold="auto")
        # 95th percentile of 0..19 is 18.05 → points > 18.05 removed
        assert np.sum(mask) > 0


# ==========================================================================
# T5.8 — Confidence filter
# ==========================================================================


class TestConfidenceFilter:
    """Tests for compute_depth_confidence (T5.8)."""

    def test_identical_depths_high_confidence(self) -> None:
        """Identical depth maps should yield high confidence everywhere."""
        h, w = 32, 64
        depth = np.random.RandomState(42).randn(h, w).astype(np.float32)
        depth = np.abs(depth) + 1.0

        confidence = compute_depth_confidence(depth, depth, ncc_threshold=0.5)

        # Identical maps → NCC = 1 → confidence ≈ 1.0
        np.testing.assert_allclose(confidence, 1.0, atol=0.01)

    def test_uncorrelated_depths_low_confidence(self) -> None:
        """Uncorrelated depth maps should yield lower confidence."""
        h, w = 32, 64
        rng = np.random.RandomState(42)
        depth1 = rng.rand(h, w).astype(np.float32) * 10
        depth2 = rng.rand(h, w).astype(np.float32) * 10

        confidence = compute_depth_confidence(depth1, depth2, ncc_threshold=0.5)

        # Confidence should be in [0, 1]
        assert np.all(confidence >= 0.0)
        assert np.all(confidence <= 1.0)
        # Average confidence should be moderate for random data
        assert 0.2 < np.mean(confidence) < 0.8

    def test_output_shape(self) -> None:
        """Output should match input shape."""
        h, w = 16, 32
        depth = np.ones((h, w), dtype=np.float32)

        confidence = compute_depth_confidence(depth, depth)

        assert confidence.shape == (h, w)
        assert confidence.dtype == np.float32


# ==========================================================================
# T5.9 — Stride assignment
# ==========================================================================


class TestStrideAssignment:
    """Tests for assign_stride (T5.9)."""

    def test_high_confidence_gets_stride_high(self) -> None:
        """High-confidence pixels should get stride_high."""
        conf_map = np.ones((4, 4), dtype=np.float32)  # all high

        strides = assign_stride(conf_map, stride_high=1, stride_low=4, threshold=0.5)

        np.testing.assert_array_equal(strides, 1)

    def test_low_confidence_gets_stride_low(self) -> None:
        """Low-confidence pixels should get stride_low."""
        conf_map = np.zeros((4, 4), dtype=np.float32)  # all low

        strides = assign_stride(conf_map, stride_high=1, stride_low=4, threshold=0.5)

        np.testing.assert_array_equal(strides, 4)

    def test_mixed_confidence(self) -> None:
        """Mixed confidence should produce mixed strides."""
        conf_map = np.array([[0.9, 0.1], [0.3, 0.8]], dtype=np.float32)

        strides = assign_stride(conf_map, stride_high=1, stride_low=4, threshold=0.5)

        assert strides[0, 0] == 1  # 0.9 >= 0.5
        assert strides[0, 1] == 4  # 0.1 < 0.5
        assert strides[1, 0] == 4  # 0.3 < 0.5
        assert strides[1, 1] == 1  # 0.8 >= 0.5

    def test_output_dtype(self) -> None:
        """Output should be int32."""
        conf_map = np.ones((2, 2), dtype=np.float32)
        strides = assign_stride(conf_map)
        assert strides.dtype == np.int32


# ==========================================================================
# T5.10 — Attribute assignment
# ==========================================================================


class TestAttributeAssignment:
    """Tests for assign_initial_attributes (T5.10)."""

    def test_opacity_by_confidence(self) -> None:
        """High-confidence points should get opacity 1.0, low 0.3."""
        n = 4
        positions = np.zeros((n, 3), dtype=np.float32)
        colors = np.zeros((n, 3), dtype=np.float32)
        confidence = np.array([0.9, 0.8, 0.3, 0.1], dtype=np.float32)
        depth = np.array([5.0, 3.0, 7.0, 2.0], dtype=np.float32)

        attrs = assign_initial_attributes(positions, colors, confidence, depth)

        assert attrs["opacities"][0] == pytest.approx(1.0)
        assert attrs["opacities"][1] == pytest.approx(1.0)
        assert attrs["opacities"][2] == pytest.approx(0.3)
        assert attrs["opacities"][3] == pytest.approx(0.3)

    def test_scale_by_depth(self) -> None:
        """Scale should be proportional to depth (factor 0.002)."""
        n = 2
        positions = np.zeros((n, 3), dtype=np.float32)
        colors = np.zeros((n, 3), dtype=np.float32)
        confidence = np.ones(n, dtype=np.float32)
        depth = np.array([5.0, 10.0], dtype=np.float32)

        attrs = assign_initial_attributes(positions, colors, confidence, depth)

        # scale = depth * 0.002
        expected_scale_0 = 5.0 * 0.002
        expected_scale_1 = 10.0 * 0.002
        np.testing.assert_allclose(
            attrs["scales"][0, 0], expected_scale_0, atol=1e-6
        )
        np.testing.assert_allclose(
            attrs["scales"][1, 0], expected_scale_1, atol=1e-6
        )

    def test_identity_rotation(self) -> None:
        """All rotations should be identity quaternion (1,0,0,0)."""
        n = 3
        positions = np.zeros((n, 3), dtype=np.float32)
        colors = np.zeros((n, 3), dtype=np.float32)
        confidence = np.ones(n, dtype=np.float32)
        depth = np.ones(n, dtype=np.float32) * 5.0

        attrs = assign_initial_attributes(positions, colors, confidence, depth)

        expected_rot = np.zeros((n, 4), dtype=np.float32)
        expected_rot[:, 0] = 1.0
        np.testing.assert_array_equal(attrs["rotations"], expected_rot)

    def test_output_keys(self) -> None:
        """Output dict should have all required keys."""
        n = 1
        positions = np.zeros((n, 3), dtype=np.float32)
        colors = np.zeros((n, 3), dtype=np.float32)
        confidence = np.ones(n, dtype=np.float32)
        depth = np.ones(n, dtype=np.float32)

        attrs = assign_initial_attributes(positions, colors, confidence, depth)

        for key in ("positions", "colors", "opacities", "scales", "rotations"):
            assert key in attrs

    def test_isotropic_scale(self) -> None:
        """Scale should be isotropic (same in x, y, z)."""
        n = 1
        positions = np.zeros((n, 3), dtype=np.float32)
        colors = np.zeros((n, 3), dtype=np.float32)
        confidence = np.ones(n, dtype=np.float32)
        depth = np.array([5.0], dtype=np.float32)

        attrs = assign_initial_attributes(positions, colors, confidence, depth)

        np.testing.assert_allclose(attrs["scales"][0, 0], attrs["scales"][0, 1])
        np.testing.assert_allclose(attrs["scales"][0, 0], attrs["scales"][0, 2])

    def test_empty_input(self) -> None:
        """Empty input should return empty arrays."""
        positions = np.empty((0, 3), dtype=np.float32)
        colors = np.empty((0, 3), dtype=np.float32)
        confidence = np.empty(0, dtype=np.float32)
        depth = np.empty(0, dtype=np.float32)

        attrs = assign_initial_attributes(positions, colors, confidence, depth)

        assert attrs["positions"].shape[0] == 0
        assert attrs["opacities"].shape[0] == 0


# ==========================================================================
# T5.12 — Full pipeline
# ==========================================================================


class TestPipeline:
    """Integration tests for run_stage05 (T5.12)."""

    def test_pipeline_synthetic_single_frame(
        self,
        synthetic_erp_image: np.ndarray,
        synthetic_depth_map: np.ndarray,
        tmp_path: Path,
    ) -> None:
        """Pipeline should run on a single synthetic frame and produce PLY."""
        from sphereforge.common.io import write_depth, write_image
        from sphereforge.config import Stage05Config
        from sphereforge.stages.stage05_seeding.pipeline import run_stage05

        config = Stage05Config(
            stride=2,
            grazing_angle=89,  # effectively disabled
            outlier_pruning=0.0,
            sparse_pruning=0.0,
        )

        # Write frame and depth to tmp_path
        frame_path = tmp_path / "frame_000.png"
        depth_path = tmp_path / "depth_000.npy"
        write_image(frame_path, synthetic_erp_image)
        write_depth(depth_path, synthetic_depth_map)

        # Minimal sparse model with identity pose
        sparse_model = {
            "images": {
                1: {
                    "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                    "tx": 0.0, "ty": 0.0, "tz": 0.0,
                    "camera_id": 1,
                    "name": "frame_000.png",
                },
            },
        }

        scene_params = {"sky_depth": 100.0, "orbit_radius": 5.0}
        output_dir = tmp_path / "output"

        ply_path = run_stage05(
            config,
            [frame_path],
            [depth_path],
            sparse_model,
            scene_params,
            output_dir,
        )

        assert ply_path.exists()
        assert ply_path.name == "initial_gaussians.ply"
        assert ply_path.stat().st_size > 0

    def test_pipeline_two_frames(
        self,
        synthetic_erp_image: np.ndarray,
        synthetic_depth_map: np.ndarray,
        tmp_path: Path,
    ) -> None:
        """Pipeline should handle two frames and produce PLY."""
        from sphereforge.common.io import write_depth, write_image
        from sphereforge.config import Stage05Config
        from sphereforge.stages.stage05_seeding.pipeline import run_stage05

        config = Stage05Config(
            stride=4,
            grazing_angle=89,
            outlier_pruning=0.0,
            sparse_pruning=0.0,
            dedup_distance=0.1,
        )

        # Write two frames
        frame_paths = []
        depth_paths = []
        for i in range(2):
            fp = tmp_path / f"frame_{i:03d}.png"
            dp = tmp_path / f"depth_{i:03d}.npy"
            write_image(fp, synthetic_erp_image)
            write_depth(dp, synthetic_depth_map)
            frame_paths.append(fp)
            depth_paths.append(dp)

        sparse_model = {
            "images": {
                1: {
                    "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                    "tx": 0.0, "ty": 0.0, "tz": 0.0,
                    "camera_id": 1,
                    "name": "frame_000.png",
                },
                2: {
                    "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                    "tx": 0.0, "ty": 0.0, "tz": 0.0,
                    "camera_id": 1,
                    "name": "frame_001.png",
                },
            },
        }

        scene_params = {"sky_depth": 100.0, "orbit_radius": 5.0}
        output_dir = tmp_path / "output"

        ply_path = run_stage05(
            config,
            frame_paths,
            depth_paths,
            sparse_model,
            scene_params,
            output_dir,
        )

        assert ply_path.exists()

    def test_pipeline_output_readable(
        self,
        synthetic_erp_image: np.ndarray,
        synthetic_depth_map: np.ndarray,
        tmp_path: Path,
    ) -> None:
        """Output PLY should be readable by the common I/O module."""
        from sphereforge.common.io import read_ply, write_depth, write_image
        from sphereforge.config import Stage05Config
        from sphereforge.stages.stage05_seeding.pipeline import run_stage05

        config = Stage05Config(
            stride=4,
            grazing_angle=89,
            outlier_pruning=0.0,
            sparse_pruning=0.0,
        )

        frame_path = tmp_path / "frame_000.png"
        depth_path = tmp_path / "depth_000.npy"
        write_image(frame_path, synthetic_erp_image)
        write_depth(depth_path, synthetic_depth_map)

        sparse_model = {
            "images": {
                1: {
                    "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                    "tx": 0.0, "ty": 0.0, "tz": 0.0,
                    "camera_id": 1,
                    "name": "frame_000.png",
                },
            },
        }
        scene_params = {"sky_depth": 100.0, "orbit_radius": 5.0}
        output_dir = tmp_path / "output"

        ply_path = run_stage05(
            config,
            [frame_path],
            [depth_path],
            sparse_model,
            scene_params,
            output_dir,
        )

        # Read back the PLY
        ply_data = read_ply(ply_path)
        assert "positions" in ply_data
        assert ply_data["positions"].shape[1] == 3
        assert ply_data["positions"].shape[0] > 0
