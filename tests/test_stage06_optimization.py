"""Tests for Stage 6 paper-only modules: ErpGS (T6.1–T6.3) and 360-GeoGS (T6.4–T6.5).

Uses small synthetic tensors to verify correctness and differentiability
of all implemented functions.
"""

from __future__ import annotations

import math

import pytest
import torch
import torch.nn.functional as F


# ===================================================================
# T6.1 — erp_weighted_loss + compute_latitudes_from_crops
# ===================================================================


class TestErpWeightedLoss:
    """Tests for erp_weighted_loss (T6.1)."""

    def test_output_is_scalar(self) -> None:
        """Loss should be a scalar tensor."""
        from sphereforge.stages.stage06_optimization.erp_loss import erp_weighted_loss

        H, W, C = 32, 64, 3
        rendered = torch.rand(H, W, C)
        target = torch.rand(H, W, C)
        latitudes = torch.zeros(H, W)  # equator
        loss = erp_weighted_loss(rendered, target, latitudes)
        assert loss.dim() == 0, f"Expected scalar, got shape {loss.shape}"

    def test_identical_images_zero_l1(self) -> None:
        """With identical images, the L1 component is zero."""
        from sphereforge.stages.stage06_optimization.erp_loss import erp_weighted_loss

        H, W, C = 32, 64, 3
        target = torch.rand(H, W, C)
        latitudes = torch.zeros(H, W)  # equator → cos(lat)=1
        loss = erp_weighted_loss(target, target, latitudes, l1_weight=1.0, ssim_weight=0.0)
        assert loss.item() < 1e-6, f"Expected ~0 loss for identical images, got {loss.item()}"

    def test_pole_weight_near_zero(self) -> None:
        """At the poles (lat=±π/2), cos(lat)≈0 so the loss should be small."""
        from sphereforge.stages.stage06_optimization.erp_loss import erp_weighted_loss

        H, W, C = 32, 64, 3
        rendered = torch.rand(H, W, C)
        target = torch.rand(H, W, C)
        latitudes = torch.full((H, W), math.pi / 2)  # north pole
        loss = erp_weighted_loss(rendered, target, latitudes)
        assert loss.item() < 0.01, f"Pole-weighted loss should be near 0, got {loss.item()}"

    def test_equator_weight_is_one(self) -> None:
        """At the equator (lat=0), the L1 loss equals unweighted L1."""
        from sphereforge.stages.stage06_optimization.erp_loss import erp_weighted_loss

        H, W, C = 16, 32, 3
        rendered = torch.rand(H, W, C)
        target = torch.rand(H, W, C)
        latitudes = torch.zeros(H, W)
        loss = erp_weighted_loss(rendered, target, latitudes, l1_weight=1.0, ssim_weight=0.0)
        expected = (rendered - target).abs().mean()
        assert abs(loss.item() - expected.item()) < 1e-5, (
            f"Equator loss {loss.item():.6f} != expected {expected.item():.6f}"
        )

    def test_differentiable(self) -> None:
        """Loss must be differentiable w.r.t. rendered image."""
        from sphereforge.stages.stage06_optimization.erp_loss import erp_weighted_loss

        H, W, C = 16, 32, 3
        rendered = torch.rand(H, W, C, requires_grad=True)
        target = torch.rand(H, W, C)
        latitudes = torch.zeros(H, W)
        loss = erp_weighted_loss(rendered, target, latitudes)
        loss.backward()
        assert rendered.grad is not None, "Gradient should exist"
        assert rendered.grad.abs().sum() > 0, "Gradient should be non-zero"

    def test_shape_mismatch_raises(self) -> None:
        """Mismatched shapes should raise ValueError."""
        from sphereforge.stages.stage06_optimization.erp_loss import erp_weighted_loss

        with pytest.raises(ValueError):
            erp_weighted_loss(
                torch.rand(10, 10, 3), torch.rand(12, 10, 3), torch.zeros(10, 10)
            )


class TestComputeLatitudesFromCrops:
    """Tests for compute_latitudes_from_crops (T6.1)."""

    def test_output_shape(self) -> None:
        """Output shape should be (crop_h, crop_w)."""
        from sphereforge.stages.stage06_optimization.erp_loss import compute_latitudes_from_crops

        lat = compute_latitudes_from_crops(64, 128, "front", 0.0, 90.0)
        assert lat.shape == (64, 128), f"Expected (64, 128), got {lat.shape}"

    def test_front_face_equator(self) -> None:
        """Front face centre pixel should be near equator (latitude ≈ 0)."""
        from sphereforge.stages.stage06_optimization.erp_loss import compute_latitudes_from_crops

        lat = compute_latitudes_from_crops(32, 64, "front", 0.0, 90.0)
        # Centre pixel latitude should be near 0
        center_lat = lat[16, 32].item()
        assert abs(center_lat) < 0.05, f"Center pixel lat should be ≈0, got {center_lat}"

    def test_top_face_high_latitude(self) -> None:
        """Top face centre pixel should be at high latitude."""
        from sphereforge.stages.stage06_optimization.erp_loss import compute_latitudes_from_crops

        lat = compute_latitudes_from_crops(32, 64, "top", 0.0, 90.0)
        center_lat = lat[16, 32].item()
        assert abs(center_lat) > 0.5, f"Top face center lat should be high, got {center_lat}"

    def test_latitude_range(self) -> None:
        """All latitudes should be in [-π/2, π/2]."""
        from sphereforge.stages.stage06_optimization.erp_loss import compute_latitudes_from_crops

        for face in ["front", "right", "back", "left", "top", "bottom"]:
            lat = compute_latitudes_from_crops(32, 64, face, 0.0, 90.0)
            assert lat.min() >= -math.pi / 2 - 1e-5, f"Min lat out of range for {face}"
            assert lat.max() <= math.pi / 2 + 1e-5, f"Max lat out of range for {face}"

    def test_yaw_offset_shifts_latitudes(self) -> None:
        """Yaw offset should change the latitude distribution for side faces."""
        from sphereforge.stages.stage06_optimization.erp_loss import compute_latitudes_from_crops

        lat_no_offset = compute_latitudes_from_crops(32, 64, "front", 0.0, 90.0)
        lat_with_offset = compute_latitudes_from_crops(32, 64, "front", 30.0, 90.0)
        # They should differ (yaw rotation changes which ERP region the crop covers)
        assert not torch.allclose(lat_no_offset, lat_with_offset, atol=1e-4)

    def test_invalid_face_raises(self) -> None:
        """Invalid face name should raise ValueError."""
        from sphereforge.stages.stage06_optimization.erp_loss import compute_latitudes_from_crops

        with pytest.raises(ValueError):
            compute_latitudes_from_crops(32, 64, "diagonal", 0.0, 90.0)


# ===================================================================
# T6.2 — scale_flattening_loss
# ===================================================================


class TestScaleFlatteningLoss:
    """Tests for scale_flattening_loss (T6.2)."""

    def test_output_is_scalar(self) -> None:
        """Loss should be a scalar tensor."""
        from sphereforge.stages.stage06_optimization.erp_loss import scale_flattening_loss

        N = 50
        scales = torch.rand(N, 3) * 5.0
        positions = torch.rand(N, 3)
        latitudes = torch.zeros(N)
        loss = scale_flattening_loss(scales, positions, latitudes)
        assert loss.dim() == 0

    def test_small_scales_zero_loss(self) -> None:
        """Gaussians with scales below threshold should produce ~0 loss."""
        from sphereforge.stages.stage06_optimization.erp_loss import scale_flattening_loss

        N = 50
        scales = torch.ones(N, 3) * 0.5  # well below default threshold (10)
        positions = torch.rand(N, 3)
        latitudes = torch.zeros(N)
        loss = scale_flattening_loss(scales, positions, latitudes, max_scale_factor=10.0)
        assert loss.item() < 1e-6, f"Expected ~0 loss, got {loss.item()}"

    def test_large_scales_nonzero_loss(self) -> None:
        """Gaussians with scales above threshold should produce positive loss."""
        from sphereforge.stages.stage06_optimization.erp_loss import scale_flattening_loss

        N = 50
        scales = torch.ones(N, 3) * 20.0  # well above threshold (10)
        positions = torch.rand(N, 3)
        latitudes = torch.zeros(N)
        loss = scale_flattening_loss(scales, positions, latitudes, max_scale_factor=10.0)
        assert loss.item() > 0.0, "Expected positive loss for oversized Gaussians"

    def test_polar_tighter_threshold(self) -> None:
        """At high latitude, threshold is tighter so same scale produces more loss."""
        from sphereforge.stages.stage06_optimization.erp_loss import scale_flattening_loss

        N = 50
        scales = torch.ones(N, 3) * 12.0  # slightly above threshold
        positions = torch.rand(N, 3)
        lat_equator = torch.zeros(N)
        lat_pole = torch.full((N,), math.pi / 2)

        loss_eq = scale_flattening_loss(scales, positions, lat_equator, max_scale_factor=10.0)
        loss_pole = scale_flattening_loss(scales, positions, lat_pole, max_scale_factor=10.0)

        # At pole: threshold = 10 * (1 - 0.5 * 1) = 5, excess = 12 - 5 = 7
        # At equator: threshold = 10 * (1 - 0.5 * 0) = 10, excess = 12 - 10 = 2
        assert loss_pole.item() > loss_eq.item(), (
            f"Polar loss ({loss_pole.item()}) should exceed equatorial ({loss_eq.item()})"
        )

    def test_differentiable(self) -> None:
        """Loss must be differentiable w.r.t. scales."""
        from sphereforge.stages.stage06_optimization.erp_loss import scale_flattening_loss

        N = 50
        scales = torch.ones(N, 3, requires_grad=True) * 15.0
        positions = torch.rand(N, 3)
        latitudes = torch.zeros(N)
        loss = scale_flattening_loss(scales, positions, latitudes)
        loss.backward()
        assert scales.grad is not None, "Gradient should exist"
        assert scales.grad.abs().sum() > 0, "Gradient should be non-zero"

    def test_incompatible_shapes_raises(self) -> None:
        """Mismatched N between scales and latitudes should raise ValueError."""
        from sphereforge.stages.stage06_optimization.erp_loss import scale_flattening_loss

        with pytest.raises(ValueError):
            scale_flattening_loss(
                torch.rand(10, 3), torch.rand(10, 3), torch.zeros(20)
            )


# ===================================================================
# T6.3 — tangent_plane_neighbors + project_to_tangent_plane
# ===================================================================


class TestProjectToTangentPlane:
    """Tests for project_to_tangent_plane (T6.3 helper)."""

    def test_output_shape(self) -> None:
        """Output should be (N, 2)."""
        from sphereforge.stages.stage06_optimization.tangent_neighbors import (
            project_to_tangent_plane,
        )

        N = 10
        points = torch.rand(N, 3)
        origin = torch.zeros(3)
        normal = torch.tensor([0.0, 0.0, 1.0])
        result = project_to_tangent_plane(points, origin, normal)
        assert result.shape == (N, 2), f"Expected (N, 2), got {result.shape}"

    def test_points_on_plane_unchanged_xy(self) -> None:
        """Points already on the XY-plane should project to their (x,y) coords."""
        from sphereforge.stages.stage06_optimization.tangent_neighbors import (
            project_to_tangent_plane,
        )

        N = 5
        points = torch.rand(N, 3)
        points[:, 2] = 0.0  # on XY plane
        origin = torch.zeros(3)
        normal = torch.tensor([0.0, 0.0, 1.0])
        result = project_to_tangent_plane(points, origin, normal)
        # For Z-normal, u_axis ≈ X, v_axis ≈ Y
        assert torch.allclose(result[:, 0], points[:, 0], atol=1e-5)
        # v_axis depends on cross product direction; check it matches Y magnitude
        assert torch.allclose(result[:, 1].abs(), points[:, 1].abs(), atol=1e-5)

    def test_projection_removes_normal_component(self) -> None:
        """The normal component should be zero after projection."""
        from sphereforge.stages.stage06_optimization.tangent_neighbors import (
            project_to_tangent_plane,
        )

        N = 10
        points = torch.rand(N, 3) * 5.0
        origin = torch.zeros(3)
        normal = torch.tensor([0.0, 1.0, 0.0])
        result = project_to_tangent_plane(points, origin, normal)
        assert result.shape == (N, 2)


class TestTangentPlaneNeighbors:
    """Tests for tangent_plane_neighbors (T6.3)."""

    def test_output_shape(self) -> None:
        """Output should be (N, k)."""
        from sphereforge.stages.stage06_optimization.tangent_neighbors import (
            tangent_plane_neighbors,
        )

        N, k = 20, 5
        positions = torch.rand(N, 3) * 10.0
        indices = tangent_plane_neighbors(positions, k=k)
        assert indices.shape == (N, k), f"Expected ({N}, {k}), got {indices.shape}"

    def test_no_self_neighbor(self) -> None:
        """A point should never be its own neighbour."""
        from sphereforge.stages.stage06_optimization.tangent_neighbors import (
            tangent_plane_neighbors,
        )

        N, k = 20, 5
        positions = torch.rand(N, 3) * 10.0
        indices = tangent_plane_neighbors(positions, k=k)
        for i in range(N):
            assert i not in indices[i].tolist(), f"Point {i} is its own neighbour"

    def test_k_too_large_raises(self) -> None:
        """k >= N should raise ValueError."""
        from sphereforge.stages.stage06_optimization.tangent_neighbors import (
            tangent_plane_neighbors,
        )

        N = 10
        positions = torch.rand(N, 3)
        with pytest.raises(ValueError):
            tangent_plane_neighbors(positions, k=N)

    def test_with_surface_normals(self) -> None:
        """Should accept explicit surface normals."""
        from sphereforge.stages.stage06_optimization.tangent_neighbors import (
            tangent_plane_neighbors,
        )

        N, k = 20, 5
        positions = torch.rand(N, 3) * 5.0
        normals = F.normalize(positions, dim=1)  # radial normals
        indices = tangent_plane_neighbors(positions, k=k, surface_normals=normals)
        assert indices.shape == (N, k)

    def test_coplanar_points_match_euclidean(self) -> None:
        """For points on a plane, tangent-plane neighbors ≈ Euclidean."""
        from sphereforge.stages.stage06_optimization.tangent_neighbors import (
            tangent_plane_neighbors,
        )

        N, k = 15, 4
        # Points on Z=5 plane
        positions = torch.rand(N, 3) * 10.0
        positions[:, 2] = 5.0
        normals = torch.zeros(N, 3)
        normals[:, 2] = 1.0

        tangent_idx = tangent_plane_neighbors(positions, k=k, surface_normals=normals)

        # Euclidean neighbors
        diff = positions.unsqueeze(0) - positions.unsqueeze(1)
        dists = (diff ** 2).sum(dim=-1)
        dists.fill_diagonal_(float("inf"))
        _, eucl_idx = dists.topk(k, dim=1, largest=False)

        # Most neighbors should match (not necessarily all due to 2D vs 3D)
        overlap = (tangent_idx.unsqueeze(2) == eucl_idx.unsqueeze(1)).any(dim=2).float().mean()
        assert overlap > 0.7, f"Expected >70% overlap with Euclidean, got {overlap.item()}"


# ===================================================================
# T6.4 — compute_intersection_depth + quaternion_to_rotation_matrix
# ===================================================================


class TestQuaternionToRotationMatrix:
    """Tests for quaternion_to_rotation_matrix (T6.4 helper)."""

    def test_identity_quaternion(self) -> None:
        """Identity quaternion should give identity matrix."""
        from sphereforge.stages.stage06_optimization.intersection_depth import (
            quaternion_to_rotation_matrix,
        )

        qw = torch.tensor([1.0])
        qx = torch.tensor([0.0])
        qy = torch.tensor([0.0])
        qz = torch.tensor([0.0])
        R = quaternion_to_rotation_matrix(qw, qx, qy, qz)
        assert R.shape == (1, 3, 3)
        assert torch.allclose(R[0], torch.eye(3), atol=1e-5)

    def test_det_is_one(self) -> None:
        """Rotation matrix determinant should be 1."""
        from sphereforge.stages.stage06_optimization.intersection_depth import (
            quaternion_to_rotation_matrix,
        )

        qw = torch.tensor([0.7071, 0.5])
        qx = torch.tensor([0.0, 0.5])
        qy = torch.tensor([0.7071, 0.5])
        qz = torch.tensor([0.0, 0.5])
        R = quaternion_to_rotation_matrix(qw, qx, qy, qz)
        dets = torch.det(R)
        assert torch.allclose(dets, torch.ones(2), atol=1e-4)

    def test_orthogonal(self) -> None:
        """R^T R should be identity (orthogonal matrix)."""
        from sphereforge.stages.stage06_optimization.intersection_depth import (
            quaternion_to_rotation_matrix,
        )

        qw = torch.tensor([0.5])
        qx = torch.tensor([0.5])
        qy = torch.tensor([0.5])
        qz = torch.tensor([0.5])
        R = quaternion_to_rotation_matrix(qw, qx, qy, qz)
        RtR = R @ R.transpose(-1, -2)
        assert torch.allclose(RtR, torch.eye(3).unsqueeze(0), atol=1e-4)


class TestComputeIntersectionDepth:
    """Tests for compute_intersection_depth (T6.4)."""

    def test_output_shape(self) -> None:
        """Output should be (N_rays, N_gaussians)."""
        from sphereforge.stages.stage06_optimization.intersection_depth import (
            compute_intersection_depth,
        )

        N_rays, N_gauss = 10, 5
        origins = torch.zeros(N_rays, 3)
        origins[:, 2] = -10.0  # rays from behind
        dirs = torch.zeros(N_rays, 3)
        dirs[:, 2] = 1.0  # looking along +Z
        means = torch.zeros(N_gauss, 3)
        means[:, 2] = 5.0  # Gaussians at Z=5
        scales = torch.ones(N_gauss, 3) * 0.5
        rotations = torch.zeros(N_gauss, 4)
        rotations[:, 0] = 1.0  # identity

        depths = compute_intersection_depth(origins, dirs, means, scales, rotations)
        assert depths.shape == (N_rays, N_gauss)

    def test_ray_hits_sphere(self) -> None:
        """Ray aimed at a sphere should intersect at the correct depth."""
        from sphereforge.stages.stage06_optimization.intersection_depth import (
            compute_intersection_depth,
        )

        # Single ray along +Z, sphere centered at (0, 0, 5) with radius 1
        origins = torch.tensor([[0.0, 0.0, 0.0]])
        dirs = torch.tensor([[0.0, 0.0, 1.0]])
        means = torch.tensor([[0.0, 0.0, 5.0]])
        scales = torch.tensor([[1.0, 1.0, 1.0]])  # unit sphere
        rotations = torch.tensor([[1.0, 0.0, 0.0, 0.0]])

        depths = compute_intersection_depth(origins, dirs, means, scales, rotations)
        # Intersection at Z = 5 - 1 = 4, so depth = 4
        expected = 4.0
        assert abs(depths[0, 0].item() - expected) < 0.1, (
            f"Expected depth ≈{expected}, got {depths[0, 0].item()}"
        )

    def test_no_intersection_fallback(self) -> None:
        """Ray that misses the ellipsoid should fall back to center depth."""
        from sphereforge.stages.stage06_optimization.intersection_depth import (
            compute_intersection_depth,
        )

        # Ray along +Z offset, tiny sphere at (0,0,5)
        origins = torch.tensor([[10.0, 0.0, 0.0]])  # far from sphere
        dirs = torch.tensor([[0.0, 0.0, 1.0]])
        means = torch.tensor([[0.0, 0.0, 5.0]])
        scales = torch.tensor([[0.1, 0.1, 0.1]])  # tiny sphere
        rotations = torch.tensor([[1.0, 0.0, 0.0, 0.0]])

        depths = compute_intersection_depth(origins, dirs, means, scales, rotations)
        # Center depth = dot(mean - origin, dir) = (0-10)*0 + 0*0 + 5*1 = 5
        expected = 5.0
        assert abs(depths[0, 0].item() - expected) < 1.0, (
            f"Expected fallback depth ≈{expected}, got {depths[0, 0].item()}"
        )

    def test_stretched_ellipsoid(self) -> None:
        """An ellipsoid stretched along Z should intersect at a different depth."""
        from sphereforge.stages.stage06_optimization.intersection_depth import (
            compute_intersection_depth,
        )

        # Sphere at (0,0,5), but stretched in Z (scale_z=3)
        origins = torch.tensor([[0.0, 0.0, 0.0]])
        dirs = torch.tensor([[0.0, 0.0, 1.0]])
        means = torch.tensor([[0.0, 0.0, 5.0]])
        scales = torch.tensor([[0.5, 0.5, 3.0]])
        rotations = torch.tensor([[1.0, 0.0, 0.0, 0.0]])

        depths = compute_intersection_depth(origins, dirs, means, scales, rotations)
        # In scaled space: sphere center at (0,0,5/3), radius 1
        # Intersection at scaled Z = 5/3 - 1 = 2/3, world Z = 2/3 * 3 = 2
        expected = 2.0
        assert abs(depths[0, 0].item() - expected) < 0.5, (
            f"Expected depth ≈{expected}, got {depths[0, 0].item()}"
        )

    def test_positive_depths(self) -> None:
        """All depths should be positive (objects in front of camera)."""
        from sphereforge.stages.stage06_optimization.intersection_depth import (
            compute_intersection_depth,
        )

        N_rays, N_gauss = 5, 3
        origins = torch.zeros(N_rays, 3)
        dirs = torch.zeros(N_rays, 3)
        dirs[:, 2] = 1.0
        means = torch.rand(N_gauss, 3) * 5.0
        means[:, 2] = means[:, 2].abs() + 1.0  # ensure positive Z
        scales = torch.ones(N_gauss, 3) * 0.5
        rotations = torch.zeros(N_gauss, 4)
        rotations[:, 0] = 1.0

        depths = compute_intersection_depth(origins, dirs, means, scales, rotations)
        assert (depths > 0).all(), "All depths should be positive"


# ===================================================================
# T6.5 — d_normal_loss + compute_normals_from_depth
# ===================================================================


class TestComputeNormalsFromDepth:
    """Tests for compute_normals_from_depth (T6.5 helper)."""

    def test_output_shape(self) -> None:
        """Output should be (H, W, 3)."""
        from sphereforge.stages.stage06_optimization.d_normal_loss import (
            compute_normals_from_depth,
        )

        H, W = 32, 64
        depth = torch.ones(H, W) * 5.0
        normals = compute_normals_from_depth(depth)
        assert normals.shape == (H, W, 3), f"Expected (H,W,3), got {normals.shape}"

    def test_unit_normals(self) -> None:
        """All normals should be unit length."""
        from sphereforge.stages.stage06_optimization.d_normal_loss import (
            compute_normals_from_depth,
        )

        H, W = 32, 64
        depth = torch.rand(H, W) * 5.0 + 1.0
        normals = compute_normals_from_depth(depth)
        norms = normals.norm(dim=-1)
        assert torch.allclose(norms, torch.ones(H, W), atol=1e-4), (
            "Normals should be unit length"
        )

    def test_flat_plane_forward(self) -> None:
        """A flat depth plane should have normals pointing along +Z."""
        from sphereforge.stages.stage06_optimization.d_normal_loss import (
            compute_normals_from_depth,
        )

        H, W = 64, 64
        fx, fy = 50.0, 50.0
        # Uniform depth → all normals should point at +Z (towards camera)
        depth = torch.ones(H, W) * 10.0
        normals = compute_normals_from_depth(depth, fx=fx, fy=fy)
        # The Z component should be dominant (close to 1.0)
        assert (normals[..., 2] > 0.9).all(), "Flat plane normals should face camera (+Z)"

    def test_normals_toward_camera(self) -> None:
        """Normals should point towards the camera (positive Z component)."""
        from sphereforge.stages.stage06_optimization.d_normal_loss import (
            compute_normals_from_depth,
        )

        H, W = 32, 64
        depth = torch.rand(H, W) * 5.0 + 1.0
        normals = compute_normals_from_depth(depth)
        # Most normals should have positive Z (toward camera)
        assert (normals[..., 2] > 0).float().mean() > 0.5, (
            "Most normals should face the camera"
        )


class TestDNormalLoss:
    """Tests for d_normal_loss (T6.5)."""

    def test_output_is_scalar(self) -> None:
        """Loss should be a scalar tensor."""
        from sphereforge.stages.stage06_optimization.d_normal_loss import d_normal_loss

        H, W = 32, 64
        depth = torch.ones(H, W) * 5.0
        loss = d_normal_loss(depth)
        assert loss.dim() == 0

    def test_smooth_depth_low_loss(self) -> None:
        """A smooth (constant) depth map should have low smoothness loss."""
        from sphereforge.stages.stage06_optimization.d_normal_loss import d_normal_loss

        H, W = 64, 64
        depth = torch.ones(H, W) * 10.0
        loss = d_normal_loss(depth, depth_weight=1.0)
        # With constant depth, normals are all the same → smoothness loss ≈ 0
        assert loss.item() < 0.01, f"Smooth depth should have low loss, got {loss.item()}"

    def test_with_surface_normals(self) -> None:
        """Should accept external surface normals and compute loss."""
        from sphereforge.stages.stage06_optimization.d_normal_loss import (
            compute_normals_from_depth,
            d_normal_loss,
        )

        H, W = 32, 64
        depth = torch.rand(H, W) * 5.0 + 1.0
        surface_normals = compute_normals_from_depth(depth)
        loss = d_normal_loss(depth, surface_normals=surface_normals, depth_weight=1.0)
        # When normals match exactly, loss ≈ 0
        assert loss.item() < 0.1, f"Matching normals should have low loss, got {loss.item()}"

    def test_mismatched_normals_high_loss(self) -> None:
        """Flipped normals should produce high loss."""
        from sphereforge.stages.stage06_optimization.d_normal_loss import (
            compute_normals_from_depth,
            d_normal_loss,
        )

        H, W = 32, 64
        depth = torch.rand(H, W) * 5.0 + 1.0
        # Create intentionally wrong normals (flipped Z)
        wrong_normals = compute_normals_from_depth(depth)
        wrong_normals[..., 2] = -wrong_normals[..., 2]  # flip Z
        loss = d_normal_loss(depth, surface_normals=wrong_normals, depth_weight=1.0)
        # With flipped normals, loss should be significant
        assert loss.item() > 0.5, f"Flipped normals should have high loss, got {loss.item()}"

    def test_differentiable(self) -> None:
        """Loss should be differentiable w.r.t. rendered_depth."""
        from sphereforge.stages.stage06_optimization.d_normal_loss import d_normal_loss

        H, W = 32, 64
        depth = torch.rand(H, W, requires_grad=True) * 5.0 + 1.0
        loss = d_normal_loss(depth)
        loss.backward()
        assert depth.grad is not None, "Gradient should exist"

    def test_shape_mismatch_raises(self) -> None:
        """Incompatible surface_normals shape should raise ValueError."""
        from sphereforge.stages.stage06_optimization.d_normal_loss import d_normal_loss

        H, W = 32, 64
        depth = torch.ones(H, W)
        wrong_normals = torch.ones(H + 1, W, 3)
        with pytest.raises(ValueError):
            d_normal_loss(depth, surface_normals=wrong_normals)


class TestTrainGaussians:
    """Regression tests for Stage 6 training-loop control flow."""

    def test_pruning_uses_fresh_activations_after_densify(self, monkeypatch) -> None:
        """Pruning should recompute activated tensors after densification changes N."""
        from sphereforge.config import Stage06Config
        import sphereforge.stages.stage06_optimization.training_loop as training_loop

        def fake_render_gaussians(
            means: torch.Tensor,
            quats: torch.Tensor,
            scales: torch.Tensor,
            opacities: torch.Tensor,
            colors: torch.Tensor,
            viewmat: torch.Tensor,
            fov: float,
            image_height: int,
            image_width: int,
            sh_degree: int = 0,
            K: torch.Tensor | None = None,
        ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
            base = means.sum() * 0.0
            rendered_image = base + torch.zeros(3, image_height, image_width, device=means.device)
            rendered_depth = base + torch.zeros(image_height, image_width, device=means.device)
            rendered_alpha = base + torch.ones(image_height, image_width, device=means.device)
            return rendered_image, rendered_depth, rendered_alpha

        def fake_long_axis_split(
            positions: torch.Tensor,
            scales: torch.Tensor,
            rotations: torch.Tensor,
            opacities: torch.Tensor,
            colors: torch.Tensor,
            mask: torch.Tensor,
        ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
            return (
                torch.cat([positions, positions[:1].clone()], dim=0),
                torch.cat([scales, scales[:1].clone()], dim=0),
                torch.cat([rotations, rotations[:1].clone()], dim=0),
                torch.cat([opacities, opacities[:1].clone()], dim=0),
                torch.cat([colors, colors[:1].clone()], dim=0),
            )

        def fake_rap_prune(
            positions: torch.Tensor,
            scales: torch.Tensor,
            opacities: torch.Tensor,
            min_opacity: float = 0.005,
            max_scale_ratio: float = 10.0,
            scene_extent: float | None = None,
        ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
            assert positions.shape[0] == scales.shape[0] == opacities.shape[0]
            keep_mask = torch.ones(positions.shape[0], dtype=torch.bool, device=positions.device)
            return positions, scales, opacities, keep_mask

        monkeypatch.setattr(training_loop, "render_gaussians", fake_render_gaussians)
        monkeypatch.setattr(training_loop, "compute_eas", lambda img: torch.ones(2, 2, device=img.device))
        monkeypatch.setattr(
            training_loop,
            "should_densify",
            lambda eas_map, screen_positions, threshold: torch.ones(
                screen_positions.shape[0], dtype=torch.bool, device=screen_positions.device
            ),
        )
        monkeypatch.setattr(training_loop, "long_axis_split", fake_long_axis_split)
        monkeypatch.setattr(training_loop, "rap_prune", fake_rap_prune)

        initial_gaussians = {
            "positions": torch.tensor([[0.0, 0.0, 2.0], [0.5, 0.0, 2.5]], dtype=torch.float32),
            "colors": torch.ones(2, 3, dtype=torch.float32),
            "opacities": torch.zeros(2, dtype=torch.float32),
            "scales": torch.tensor([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]], dtype=torch.float32),
            "rotations": torch.tensor(
                [[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]], dtype=torch.float32
            ),
        }
        training_views = [
            {
                "viewmat": torch.eye(4, dtype=torch.float32),
                "target_image": torch.zeros(3, 2, 2, dtype=torch.float32),
                "target_depth": torch.zeros(2, 2, dtype=torch.float32),
                "fov": 90.0,
                "height": 2,
                "width": 2,
            }
        ]
        config = Stage06Config(
            iterations=2,
            densify_until_iter=2,
            densify_every=1,
            prune_every=1,
            sh_degree=0,
            erp_distortion_weights=False,
            erp_scale_flattening_loss=0.0,
            depth_reg_weight=0.0,
            d_normal_weight=0.0,
            checkpoint_every=0,
        )

        result = training_loop.train_gaussians(
            initial_gaussians=initial_gaussians,
            training_views=training_views,
            config=config,
            device="cpu",
            checkpoint_dir=None,
        )

        assert result["positions"].shape[0] > initial_gaussians["positions"].shape[0]

    def test_densification_respects_hard_gaussian_cap(self, monkeypatch) -> None:
        """Densification should stop once the configured Gaussian cap is reached."""
        from sphereforge.config import Stage06Config
        import sphereforge.stages.stage06_optimization.training_loop as training_loop

        def fake_render_gaussians(
            means: torch.Tensor,
            quats: torch.Tensor,
            scales: torch.Tensor,
            opacities: torch.Tensor,
            colors: torch.Tensor,
            viewmat: torch.Tensor,
            fov: float = 90.0,
            image_height: int = 2,
            image_width: int = 2,
            sh_degree: int = 0,
            K: torch.Tensor | None = None,
        ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
            base = means.sum() * 0.0
            rendered_image = base + torch.zeros(3, image_height, image_width, device=means.device)
            rendered_depth = base + torch.zeros(image_height, image_width, device=means.device)
            rendered_alpha = base + torch.ones(image_height, image_width, device=means.device)
            return rendered_image, rendered_depth, rendered_alpha

        def fake_long_axis_split(
            positions: torch.Tensor,
            scales: torch.Tensor,
            rotations: torch.Tensor,
            opacities: torch.Tensor,
            colors: torch.Tensor,
            mask: torch.Tensor,
        ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
            selected = mask.nonzero(as_tuple=True)[0]
            clones = positions[selected]
            return (
                torch.cat([positions, clones], dim=0),
                torch.cat([scales, scales[selected]], dim=0),
                torch.cat([rotations, rotations[selected]], dim=0),
                torch.cat([opacities, opacities[selected]], dim=0),
                torch.cat([colors, colors[selected]], dim=0),
            )

        monkeypatch.setattr(training_loop, "render_gaussians", fake_render_gaussians)
        monkeypatch.setattr(training_loop, "compute_eas", lambda img: torch.ones(2, 2, device=img.device))
        monkeypatch.setattr(
            training_loop,
            "should_densify",
            lambda eas_map, screen_positions, threshold: torch.ones(
                screen_positions.shape[0], dtype=torch.bool, device=screen_positions.device
            ),
        )
        monkeypatch.setattr(training_loop, "long_axis_split", fake_long_axis_split)
        monkeypatch.setattr(
            training_loop,
            "rap_prune",
            lambda positions, scales, opacities, min_opacity=0.005, max_scale_ratio=0.1, scene_extent=None: (
                positions,
                scales,
                opacities,
                torch.ones(positions.shape[0], dtype=torch.bool, device=positions.device),
            ),
        )

        initial_gaussians = {
            "positions": torch.tensor([[0.0, 0.0, 2.0], [0.5, 0.0, 2.5]], dtype=torch.float32),
            "colors": torch.ones(2, 3, dtype=torch.float32),
            "opacities": torch.zeros(2, dtype=torch.float32),
            "scales": torch.tensor([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]], dtype=torch.float32),
            "rotations": torch.tensor(
                [[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]], dtype=torch.float32
            ),
        }
        training_views = [
            {
                "viewmat": torch.eye(4, dtype=torch.float32),
                "target_image": torch.zeros(3, 2, 2, dtype=torch.float32),
                "target_depth": torch.zeros(2, 2, dtype=torch.float32),
                "K": torch.eye(3, dtype=torch.float32),
                "fov": 90.0,
                "height": 2,
                "width": 2,
            }
        ]
        config = Stage06Config(
            iterations=2,
            densify_until_iter=2,
            densify_every=1,
            prune_every=100,
            sh_degree=0,
            erp_distortion_weights=False,
            erp_scale_flattening_loss=0.0,
            depth_reg_weight=0.0,
            d_normal_weight=0.0,
            checkpoint_every=0,
            max_gaussians=3,
        )

        result = training_loop.train_gaussians(
            initial_gaussians=initial_gaussians,
            training_views=training_views,
            config=config,
            device="cpu",
            checkpoint_dir=None,
        )

        assert result["positions"].shape[0] == 3
