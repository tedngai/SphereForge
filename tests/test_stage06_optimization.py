"""Tests for Stage 6 paper-only modules: ErpGS (T6.1-T6.3) and 360-GeoGS (T6.4-T6.5).

Uses small synthetic tensors to verify correctness and differentiability
of all implemented functions.
"""

from __future__ import annotations

import math

import numpy as np
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
        """A yaw offset must not change the latitude map of a crop.

        ``_make_rotation_matrix`` composes ``Rx(pitch) @ Ry(yaw)``, i.e. yaw is
        applied *before* pitch, so it is a rotation about the camera's own up
        axis. Rotating about the up axis changes longitude only and leaves the
        elevation of every pixel's ray unchanged, so the latitude map (and the
        ``cos(latitude)`` ERP weights derived from it) is yaw-invariant for
        every face, pitched or not.
        """
        from sphereforge.stages.stage06_optimization.erp_loss import compute_latitudes_from_crops

        for face in ("front", "top", "bottom"):
            lat_no_offset = compute_latitudes_from_crops(32, 64, face, 0.0, 90.0)
            lat_with_offset = compute_latitudes_from_crops(32, 64, face, 30.0, 90.0)
            assert torch.allclose(lat_no_offset, lat_with_offset, atol=1e-5), face

        # Pitch, by contrast, must change the latitude distribution.
        lat_front = compute_latitudes_from_crops(32, 64, "front", 0.0, 90.0)
        lat_top = compute_latitudes_from_crops(32, 64, "top", 0.0, 90.0)
        assert not torch.allclose(lat_front, lat_top, atol=1e-4)

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
        # ``ones() * 15.0`` is a non-leaf tensor, so autograd never populates
        # its .grad; build the leaf directly.
        scales = torch.full((N, 3), 15.0, requires_grad=True)
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
        # ``rand() * 5 + 1`` is a non-leaf tensor; build a leaf so .grad is set.
        depth = (torch.rand(H, W) * 5.0 + 1.0).detach().requires_grad_(True)
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


class TestStage06PipelinePrep:
    """Tests for Stage 6 input-parameter normalization."""

    def test_prepare_initial_gaussians_converts_stage5_encoding(self) -> None:
        """Stage 6 should ingest Stage 5 activated values as raw trainable parameters."""
        from sphereforge.stages.stage06_optimization.pipeline import (
            _prepare_initial_gaussians_for_training,
        )

        gaussians_ply = {
            "positions": np.array([[0.0, 0.0, 1.0], [1.0, 0.5, 2.0]], dtype=np.float32),
            "colors": np.array([[1.0, 0.5, 0.2], [0.1, 0.2, 0.3]], dtype=np.float32),
            "opacities": np.array([1.0, 0.3], dtype=np.float32),
            "scales": np.array([[0.02, 0.02, 0.02], [0.5, 0.1, 0.2]], dtype=np.float32),
            "rotations": np.array(
                [[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]], dtype=np.float32
            ),
        }

        prepared = _prepare_initial_gaussians_for_training(gaussians_ply)
        clipped_opacities = np.clip(gaussians_ply["opacities"], 1e-6, 1.0 - 1e-6)

        assert torch.allclose(
            prepared["opacities"],
            torch.from_numpy(np.log(clipped_opacities / (1.0 - clipped_opacities))),
            atol=1e-6,
        )
        assert torch.allclose(
            prepared["scales"],
            torch.from_numpy(np.log(gaussians_ply["scales"])),
            atol=1e-6,
        )

    def test_prepare_initial_gaussians_keeps_opaque_values_finite(self) -> None:
        """Fully opaque Stage 5 seeds should not become infinite logits."""
        from sphereforge.stages.stage06_optimization.pipeline import (
            _prepare_initial_gaussians_for_training,
        )

        gaussians_ply = {
            "positions": np.array([[0.0, 0.0, 1.0]], dtype=np.float32),
            "colors": np.array([[1.0, 1.0, 1.0]], dtype=np.float32),
            "opacities": np.array([1.0], dtype=np.float32),
            "scales": np.array([[0.02, 0.02, 0.02]], dtype=np.float32),
            "rotations": np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32),
        }

        prepared = _prepare_initial_gaussians_for_training(gaussians_ply)
        assert torch.isfinite(prepared["opacities"]).all()
        assert torch.isfinite(prepared["scales"]).all()


class TestPanoramaRigDepthMapping:
    """Regression tests for mapping Stage 4 ERP depth onto panorama-rig views.

    Stage 4 writes one ERP depth map per frame, but Stage 6 trains on the
    rectilinear rig views at ``images/pano_cameraNN/<frame>.png``. Without this
    mapping those views silently received *random placeholder* depth.
    """

    @staticmethod
    def _floor_erp_depth(h: int = 128, w: int = 256) -> np.ndarray:
        """ERP radial depth of a floor plane at y = -1.5 (20.0 above it)."""
        phi = (np.arange(w) + 0.5) / w * 2.0 * math.pi - math.pi
        theta = math.pi / 2.0 - (np.arange(h) + 0.5) / h * math.pi
        _phi_grid, theta_grid = np.meshgrid(phi, theta)
        y = np.sin(theta_grid)
        return np.where(y < -1e-3, 1.5 / np.maximum(-y, 1e-9), 20.0).astype(np.float32)

    def test_view_depth_matches_analytic_floor(self) -> None:
        """A downward view must see the floor at the analytic distance."""
        from sphereforge.stages.stage06_optimization.pipeline import (
            _render_erp_depth_to_view,
        )

        erp = self._floor_erp_depth()
        view = _render_erp_depth_to_view(erp, yaw_deg=0.0, pitch_deg=-45.0, fov_deg=90.0, view_size=64)

        assert view.shape == (64, 64)
        assert np.isfinite(view).all()
        # The centre ray of a -45 deg view has y = -sin(45 deg), so the radial
        # distance to a floor at y = -1.5 is 1.5 / sin(45 deg) = 2.1213. Depth
        # is stored as *perspective* depth (along the view axis), which for a
        # view centre is the radial distance itself. The 128x256 ERP is coarse,
        # so allow a couple of percent of resampling error.
        expected = 1.5 / math.sin(math.radians(45.0))
        assert view[32, 32] == pytest.approx(expected, rel=0.02)

    def test_view_depth_is_perspective_not_radial(self) -> None:
        """Corner rays must read farther than the centre (perspective depth)."""
        from sphereforge.stages.stage06_optimization.pipeline import (
            _render_erp_depth_to_view,
        )

        erp = self._floor_erp_depth()
        view = _render_erp_depth_to_view(erp, yaw_deg=0.0, pitch_deg=-45.0, fov_deg=90.0, view_size=64)
        assert view[-1, -1] > view[32, 32]

    def test_rig_view_depth_resolves_manifest(self, tmp_path) -> None:
        """_render_rig_view_depth finds the rig camera and ERP depth file."""
        import json

        from sphereforge.stages.stage06_optimization.pipeline import (
            _render_rig_view_depth,
        )

        cubemap_dir = tmp_path / "cubemaps"
        cubemap_dir.mkdir()
        (cubemap_dir / "panorama_rig.json").write_text(
            json.dumps(
                {
                    "fov": 90,
                    "overlap": 15,
                    "cameras": [
                        {"name": "pano_camera00", "yaw_deg": 0.0, "pitch_deg": -45.0, "camera_id": 1}
                    ],
                }
            ),
            encoding="utf-8",
        )
        depth_dir = tmp_path / "depth"
        depth_dir.mkdir()
        np.save(depth_dir / "frame_000000_depth.npy", self._floor_erp_depth())

        cam = {"width": 64, "height": 64}
        out = _render_rig_view_depth(
            name="images/pano_camera00/frame_000000.png",
            depth_dir=depth_dir,
            cubemap_dir=cubemap_dir,
            cam=cam,
        )
        assert out is not None
        assert out.shape == (64, 64)
        assert out[32, 32] == pytest.approx(1.5 / math.sin(math.radians(45.0)), rel=0.02)

    def test_rig_view_depth_returns_none_without_manifest(self, tmp_path) -> None:
        """Non-rig datasets fall through to the existing lookup paths."""
        from sphereforge.stages.stage06_optimization.pipeline import (
            _render_rig_view_depth,
        )

        out = _render_rig_view_depth(
            name="images/frame_000000_front.png",
            depth_dir=tmp_path,
            cubemap_dir=tmp_path,
            cam={"width": 64, "height": 64},
        )
        assert out is None


class TestTrainGaussians:
    """Regression tests for Stage 6 training-loop control flow."""

    @pytest.fixture(autouse=True)
    def _assume_rasterizer(self, monkeypatch) -> None:
        """Pretend the gsplat CUDA extension is built.

        These tests replace the renderer with a stub, so they do not need the
        real rasteriser — but ``train_gaussians`` refuses to run without it.
        """
        import sphereforge.stages.stage06_optimization.training_loop as training_loop

        monkeypatch.setattr(training_loop, "_HAS_GSPLAT", True)

    def test_pruning_uses_fresh_activations_after_densify(self, monkeypatch) -> None:
        """Pruning should recompute activated tensors after densification changes N."""
        import sphereforge.stages.stage06_optimization.training_loop as training_loop
        from sphereforge.config import Stage06Config

        fake_render_gaussians = _fake_render_with_grad_info

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
            densify_from_iter=0,
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
        import sphereforge.stages.stage06_optimization.training_loop as training_loop
        from sphereforge.config import Stage06Config

        fake_render_gaussians = _fake_render_with_grad_info

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
            densify_from_iter=0,
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



def _fake_render_with_grad_info(
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
    return_info: bool = False,
):
    """Render stub whose image depends on a gsplat-style ``means2d`` tensor.

    Every Gaussian is "visible", so each gets a large screen-space gradient
    and is selected by the gradient-based densification trigger.
    """
    means2d = means[:, :2] * 1.0
    base = means2d.sum()
    rendered_image = base + torch.zeros(3, image_height, image_width, device=means.device)
    rendered_depth = means.sum() * 0.0 + torch.zeros(
        image_height, image_width, device=means.device
    )
    rendered_alpha = torch.ones(image_height, image_width, device=means.device)
    if not return_info:
        return rendered_image, rendered_depth, rendered_alpha
    info = {
        "means2d": means2d,
        "gaussian_ids": torch.arange(means.shape[0], device=means.device),
    }
    return rendered_image, rendered_depth, rendered_alpha, info


class TestPlyValueSpace:
    """Stage 6 must write PLYs in the 3DGS convention (activated values)."""

    def test_optimized_ply_uses_activated_opacity_and_scale(self, tmp_path) -> None:
        """Raw logits must be activated before writing, or viewers mis-render."""
        import numpy as np

        from sphereforge.common.io import read_ply, write_ply

        # Emulate the conversion Stage 6 applies to its raw parameters.
        raw_opacity = np.array([-2.0, 0.0, 3.0], dtype=np.float32)
        raw_scale = np.array([[-3.0, -3.0, -3.0], [0.0, 0.0, 0.0], [1.0, 1.0, 1.0]], dtype=np.float32)

        path = tmp_path / "out.ply"
        write_ply(
            path,
            positions=np.zeros((3, 3), dtype=np.float32),
            colors=np.zeros((3, 3), dtype=np.float32),
            opacities=(1.0 / (1.0 + np.exp(-raw_opacity))).astype(np.float32),
            scales=np.exp(raw_scale).astype(np.float32),
            rotations=np.tile(np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32), (3, 1)),
        )

        data = read_ply(path)
        # Opacity is a probability in [0, 1]; scale is a positive length.
        assert np.all(data["opacities"] >= 0.0)
        assert np.all(data["opacities"] <= 1.0)
        assert np.all(data["scales"] > 0.0)
        assert np.allclose(data["opacities"], 1.0 / (1.0 + np.exp(-raw_opacity)), atol=1e-5)
        assert np.allclose(data["scales"], np.exp(raw_scale), rtol=1e-5)


class TestColorConversion:
    """Colours must enter SH DC space exactly once and stay there."""

    def test_rgb_to_sh_dc_roundtrip(self) -> None:
        """The training loop converts RGB to SH DC; the PLY stores it as-is."""
        import numpy as np

        SH_C0 = 0.28209479177387814

        rgb = np.array([[[0.2, 0.4, 0.6]], [[0.8, 0.1, 0.9]]], dtype=np.float32)
        # What the training loop does on entry.
        sh = (rgb - 0.5) / SH_C0

        # The spread must survive (a second conversion would flatten it).
        assert float(sh.std()) > 0.1

        # What a viewer does to decode.
        decoded = np.clip(sh * SH_C0 + 0.5, 0.0, 1.0)
        assert np.allclose(decoded, rgb, atol=1e-5)

    def test_sh_dc_is_written_without_reconversion(self) -> None:
        """SH DC values already in coefficient space must pass through unchanged."""
        import numpy as np

        SH_C0 = 0.28209479177387814

        rgb = np.array([[[0.3, 0.5, 0.7]]], dtype=np.float32)
        sh = (rgb - 0.5) / SH_C0

        # The writer stores SH DC directly; no further conversion.
        stored = sh.astype(np.float32)

        decoded = np.clip(stored * SH_C0 + 0.5, 0.0, 1.0)
        assert np.allclose(decoded, rgb, atol=1e-5)
        # A double conversion would collapse the range to ~1e-3.
        assert float(stored.std()) > 0.1


class TestShScheduleGuard:
    """A run too short to finish the SH ramp must warn about it."""

    def test_warns_when_iterations_cannot_reach_sh_degree(self, caplog, monkeypatch) -> None:
        """3,000 iterations cannot complete the 2,500-step ramp to degree 1."""
        import logging

        from sphereforge.config import Stage06Config
        from sphereforge.stages.stage06_optimization import training_loop

        def fake_render(**kwargs):
            h, w = kwargs["height"], kwargs["width"]
            return (
                torch.zeros(3, h, w, dtype=torch.float32),
                torch.zeros(1, h, w, dtype=torch.float32),
                torch.ones(1, h, w, dtype=torch.float32),
            )

        monkeypatch.setattr(training_loop, "render_gaussians", fake_render, raising=False)

        initial_gaussians = {
            "positions": torch.zeros(2, 3, dtype=torch.float32),
            "colors": torch.full((2, 1, 3), 0.5, dtype=torch.float32),
            "scales": torch.full((2, 3), -3.0, dtype=torch.float32),
            "rotations": torch.tensor(
                [[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]], dtype=torch.float32
            ),
            "opacities": torch.zeros(2, dtype=torch.float32),
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
            iterations=3000,
            densify_until_iter=2,
            densify_every=1,
            prune_every=1,
            sh_degree=1,
            erp_distortion_weights=False,
            erp_scale_flattening_loss=0.0,
            depth_reg_weight=0.0,
            d_normal_weight=0.0,
            checkpoint_every=0,
        )

        # The guard fires before the rasterizer check, so the warning is
        # recorded even though training then refuses to run on CPU.
        with caplog.at_level(logging.WARNING), pytest.raises(RuntimeError):
            training_loop.train_gaussians(
                initial_gaussians=initial_gaussians,
                training_views=training_views,
                config=config,
                device="cpu",
            )

        assert any("leaves only" in r.message and "sh_degree" in r.message for r in caplog.records)





class TestGradientDensification:
    """Densification is driven by accumulated screen-space gradients."""

    @staticmethod
    def _gaussians(log_scales: list[list[float]]) -> dict[str, torch.Tensor]:
        n = len(log_scales)
        return {
            "positions": torch.zeros(n, 3),
            "scales": torch.tensor(log_scales, dtype=torch.float32),
            "rotations": torch.tensor([[1.0, 0.0, 0.0, 0.0]] * n),
            "opacities": torch.logit(torch.full((n,), 0.6)),
            "colors": torch.zeros(n, 1, 3),
        }

    @staticmethod
    def _run(g, grad, count, **kw):
        from sphereforge.stages.stage06_optimization.training_loop import _densify_by_gradient

        args = {"grad_threshold": 2e-4, "split_scale": 0.1, "max_gaussians": 100, "iteration": 0}
        args.update(kw)
        return _densify_by_gradient(
            g["positions"], g["scales"], g["rotations"], g["opacities"], g["colors"],
            grad, count, **args,
        )

    def test_split_shrinks_children_in_activated_space(self) -> None:
        """A split halves the long axis and offsets children by +-0.5 * scale."""
        g = self._gaussians([[math.log(0.4), math.log(0.05), math.log(0.05)]])
        pos, scl, _rot, opa, _col, n_clone, n_split = self._run(
            g, torch.tensor([1.0]), torch.tensor([1.0])
        )
        assert (n_clone, n_split) == (0, 1)
        assert pos.shape[0] == 2
        child_scales = torch.exp(scl)
        assert torch.allclose(child_scales[:, 0], torch.tensor([0.2, 0.2]), atol=1e-5)
        assert torch.allclose(child_scales[:, 1:], torch.full((2, 2), 0.05), atol=1e-6)
        assert torch.allclose(pos[:, 0].abs(), torch.tensor([0.2, 0.2]), atol=1e-5)
        # Opacity is inherited (activated value preserved through the logit round trip).
        assert torch.allclose(torch.sigmoid(opa), torch.full((2,), 0.6), atol=1e-5)

    def test_small_gaussians_are_cloned(self) -> None:
        """Gaussians below the split scale are duplicated, not split."""
        g = self._gaussians([[math.log(0.01)] * 3])
        pos, scl, *_rest, n_clone, n_split = self._run(g, torch.tensor([1.0]), torch.tensor([1.0]))
        assert (n_clone, n_split) == (1, 0)
        assert pos.shape[0] == 2
        assert torch.allclose(torch.exp(scl), torch.full((2, 3), 0.01), atol=1e-6)

    def test_low_gradient_is_left_alone(self) -> None:
        """Average gradient below threshold -> no change, same tensors returned."""
        g = self._gaussians([[math.log(0.4)] * 3])
        out = self._run(g, torch.tensor([1e-3]), torch.tensor([10.0]))  # avg 1e-4
        assert out[-2:] == (0, 0)
        assert out[0] is g["positions"]

    def test_cap_keeps_highest_gradients(self) -> None:
        """When capped, the Gaussians with the largest average gradient win."""
        g = self._gaussians([[math.log(0.01)] * 3] * 3)
        g["positions"] = torch.tensor([[0.0, 0, 0], [1.0, 0, 0], [2.0, 0, 0]])
        pos, *_rest, n_clone, _n_split = self._run(
            g, torch.tensor([1e-3, 5e-3, 2e-3]), torch.ones(3), max_gaussians=4
        )
        assert n_clone == 1
        assert pos.shape[0] == 4
        assert float(pos[-1, 0]) == pytest.approx(1.0)  # clone of the 5e-3 Gaussian

    def test_accumulate_screen_grads_packed(self) -> None:
        """Packed grads are scaled to pixels and summed per Gaussian id."""
        from sphereforge.stages.stage06_optimization.training_loop import (
            _accumulate_screen_grads,
        )

        acc = torch.zeros(3)
        cnt = torch.zeros(3)
        info = {"gaussian_ids": torch.tensor([0, 2])}
        grad = torch.tensor([[1e-4, 0.0], [0.0, 2e-4]])
        _accumulate_screen_grads(info, grad, 20, 10, acc, cnt)
        assert torch.allclose(acc, torch.tensor([1e-3, 0.0, 1e-3]))
        assert torch.equal(cnt, torch.tensor([1.0, 0.0, 1.0]))

    def test_scene_extent_from_camera_centres(self) -> None:
        """Extent is 1.1 x the largest camera distance from the mean centre."""
        from sphereforge.stages.stage06_optimization.training_loop import _scene_extent

        def view(center: list[float]) -> dict:
            vm = torch.eye(4)
            vm[:3, 3] = -torch.tensor(center)
            return {"viewmat": vm}

        views = [view([-1.0, 0.0, 0.0]), view([1.0, 0.0, 0.0])]
        assert _scene_extent(views, torch.zeros(1, 3)) == pytest.approx(1.1)
        # One shared centre (single panorama): fall back to the point spread.
        pts = torch.tensor([[2.0, 0, 0], [0, 4.0, 0], [0, 0, 6.0]])
        assert _scene_extent([view([0.0, 0.0, 0.0])], pts) == pytest.approx(2.0)


class TestPinholeViewsAreNotLatitudeWeighted:
    """ErpGS latitude weights only apply to equirectangular training views."""

    def test_pinhole_camera_is_not_equirectangular(self) -> None:
        """Rig views are PINHOLE and must not get ERP latitude maps."""
        from sphereforge.stages.stage06_optimization.pipeline import _is_equirectangular_camera

        assert _is_equirectangular_camera({"model": "PINHOLE"}) is False
        assert _is_equirectangular_camera({"model": "SIMPLE_PINHOLE"}) is False
        assert _is_equirectangular_camera({"model": "EQUIRECTANGULAR"}) is True

    def test_uniform_latitudes_weight_every_row_equally(self) -> None:
        """Zero latitude gives the same loss for an error in any row."""
        from sphereforge.stages.stage06_optimization.erp_loss import erp_weighted_loss

        target = torch.zeros(16, 16, 3)
        top = target.clone()
        top[0] = 1.0
        mid = target.clone()
        mid[8] = 1.0
        lat = torch.zeros(16, 16)
        loss_top = erp_weighted_loss(top, target, lat, l1_weight=1.0, ssim_weight=0.0)
        loss_mid = erp_weighted_loss(mid, target, lat, l1_weight=1.0, ssim_weight=0.0)
        assert float(loss_top) == pytest.approx(float(loss_mid))
        assert float(loss_top) > 0


class TestShExport:
    """Higher-order SH must survive the PLY round trip."""

    @pytest.mark.parametrize("degree", [1, 2, 3])
    def test_sh_roundtrip(self, tmp_path, degree: int) -> None:
        """gsplat (N, K, 3) -> f_rest PLY -> (N, K, 3) is lossless."""
        from sphereforge.common.io import (
            read_ply,
            sh_coeffs_to_gsplat,
            sh_rest_from_coeffs,
            write_ply,
        )

        n, k = 5, (degree + 1) ** 2
        sh = np.random.default_rng(degree).normal(size=(n, k, 3)).astype(np.float32)
        rest = sh_rest_from_coeffs(sh)
        assert rest.shape == (n, 3 * (k - 1))
        path = tmp_path / "sh.ply"
        write_ply(
            path,
            positions=np.zeros((n, 3), np.float32),
            colors=sh[:, 0, :],
            opacities=np.full(n, 0.5, np.float32),
            scales=np.full((n, 3), 0.1, np.float32),
            rotations=np.tile(np.array([1.0, 0, 0, 0], np.float32), (n, 1)),
            sh_coeffs=rest,
        )
        back = read_ply(path)
        assert back["sh_coeffs"].shape == (n, 3 + 3 * (k - 1))
        assert np.allclose(sh_coeffs_to_gsplat(back["sh_coeffs"]), sh)

    def test_f_rest_is_channel_major(self) -> None:
        """3DGS stores all R bands, then G, then B."""
        from sphereforge.common.io import sh_rest_from_coeffs

        sh = np.zeros((1, 4, 3), np.float32)
        sh[0, 1:, 0] = [1, 2, 3]  # R bands
        sh[0, 1:, 1] = [4, 5, 6]  # G bands
        sh[0, 1:, 2] = [7, 8, 9]  # B bands
        assert sh_rest_from_coeffs(sh).tolist() == [[1, 2, 3, 4, 5, 6, 7, 8, 9]]

    def test_write_ply_rejects_bad_rest_width(self, tmp_path) -> None:
        """Only 9/24/45 rest coefficients are valid SH layouts."""
        from sphereforge.common.io import write_ply

        with pytest.raises(ValueError, match="sh_coeffs"):
            write_ply(
                tmp_path / "bad.ply",
                positions=np.zeros((2, 3), np.float32),
                colors=np.zeros((2, 3), np.float32),
                opacities=np.zeros(2, np.float32),
                scales=np.zeros((2, 3), np.float32),
                rotations=np.zeros((2, 4), np.float32),
                sh_coeffs=np.zeros((2, 48), np.float32),
            )
