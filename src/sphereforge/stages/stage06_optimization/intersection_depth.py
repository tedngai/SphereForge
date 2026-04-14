"""360-GeoGS ray–ellipsoid intersection depth computation.

Implements the analytical ray–ellipsoid intersection described in the
360-GeoGS paper (arXiv:2601.02102).  For each ray and each Gaussian, the
module finds the intersection of the ray with the 3-D ellipsoid defined
by the Gaussian's mean, scale, and rotation.  This gives a more accurate
depth estimate than using the Gaussian centre alone, which is critical
for large, flat Gaussians that characterise planar surfaces in 360° scenes.
"""

from __future__ import annotations

import logging

import torch

logger = logging.getLogger("sphereforge.stage06.intersection_depth")


# ---------------------------------------------------------------------------
# Quaternion → rotation matrix (torch-native)
# ---------------------------------------------------------------------------


def quaternion_to_rotation_matrix(
    qw: torch.Tensor,
    qx: torch.Tensor,
    qy: torch.Tensor,
    qz: torch.Tensor,
) -> torch.Tensor:
    """Convert unit quaternions to 3×3 rotation matrices.

    This is a PyTorch-native reimplementation that supports batched
    quaternions, unlike the NumPy version in
    ``common/colmap_helpers.py``.

    Args:
        qw: Scalar (w) component, shape ``(...,)``.
        qx: x component, shape ``(...,)``.
        qy: y component, shape ``(...,)``.
        qz: z component, shape ``(...,)``.

    Returns:
        Rotation matrices, shape ``(..., 3, 3)``.
    """
    # Normalise to unit quaternions
    norm = torch.sqrt(qw ** 2 + qx ** 2 + qy ** 2 + qz ** 2)
    norm = norm.clamp(min=1e-10)
    qw = qw / norm
    qx = qx / norm
    qy = qy / norm
    qz = qz / norm

    # Build rotation matrix element-by-element
    # R = [[1-2(y²+z²), 2(xy-wz),  2(xz+wy)],
    #      [2(xy+wz),   1-2(x²+z²), 2(yz-wx)],
    #      [2(xz-wy),   2(yz+wx),   1-2(x²+y²)]]
    r00 = 1.0 - 2.0 * (qy ** 2 + qz ** 2)
    r01 = 2.0 * (qx * qy - qw * qz)
    r02 = 2.0 * (qx * qz + qw * qy)
    r10 = 2.0 * (qx * qy + qw * qz)
    r11 = 1.0 - 2.0 * (qx ** 2 + qz ** 2)
    r12 = 2.0 * (qy * qz - qw * qx)
    r20 = 2.0 * (qx * qz - qw * qy)
    r21 = 2.0 * (qy * qz + qw * qx)
    r22 = 1.0 - 2.0 * (qx ** 2 + qy ** 2)

    R = torch.stack(
        [
            torch.stack([r00, r01, r02], dim=-1),
            torch.stack([r10, r11, r12], dim=-1),
            torch.stack([r20, r21, r22], dim=-1),
        ],
        dim=-2,
    )

    return R


# ---------------------------------------------------------------------------
# T6.4 — Ray–ellipsoid intersection depth
# ---------------------------------------------------------------------------


def compute_intersection_depth(
    ray_origins: torch.Tensor,
    ray_directions: torch.Tensor,
    gaussian_means: torch.Tensor,
    gaussian_scales: torch.Tensor,
    gaussian_rotations: torch.Tensor,
) -> torch.Tensor:
    """Compute ray–Gaussian-surface intersection depths.

    For each ray and each Gaussian, find the intersection of the ray with
    the 3-D ellipsoid defined by the Gaussian's mean, scale, and rotation.
    This is the analytical ray–ellipsoid intersection:

    1. Transform the ray to the Gaussian's local frame using its rotation.
    2. Apply the Gaussian's scale to transform the ellipsoid into a unit
       sphere in the scaled frame.
    3. Solve the quadratic for ray–sphere intersection in the scaled frame.
    4. If an intersection exists, transform back to world space and compute
       depth.
    5. If no intersection (discriminant < 0), fall back to the depth of the
       Gaussian centre projected onto the ray.

    Args:
        ray_origins: Ray origin positions, shape ``(N_rays, 3)``.
        ray_directions: Ray direction vectors (should be unit length),
            shape ``(N_rays, 3)``.
        gaussian_means: Gaussian centre positions, shape ``(N_gaussians, 3)``.
        gaussian_scales: Gaussian scale parameters, shape ``(N_gaussians, 3)``.
        gaussian_rotations: Gaussian rotation quaternions ``(qw, qx, qy, qz)``,
            shape ``(N_gaussians, 4)``.

    Returns:
        Intersection depths, shape ``(N_rays, N_gaussians)``.  Depth is the
        distance along the ray direction from the ray origin to the
        intersection point on the ellipsoid surface.  Falls back to the
        centre depth when there is no intersection.
    """
    N_rays = ray_origins.shape[0]
    N_gauss = gaussian_means.shape[0]
    device = ray_origins.device
    dtype = ray_origins.dtype

    logger.debug(
        "compute_intersection_depth: %d rays x %d Gaussians", N_rays, N_gauss
    )

    # Clamp scales to avoid division by zero
    scales_clamped = gaussian_scales.clamp(min=1e-6)  # (N_g, 3)
    scale_inv = 1.0 / scales_clamped  # (N_g, 3)

    # Build rotation matrices from quaternions: (N_g, 3, 3)
    qw = gaussian_rotations[:, 0]
    qx = gaussian_rotations[:, 1]
    qy = gaussian_rotations[:, 2]
    qz = gaussian_rotations[:, 3]
    R = quaternion_to_rotation_matrix(qw, qx, qy, qz)  # (N_g, 3, 3)

    # R is the rotation that maps from the Gaussian's local frame to world.
    # To map from world to local, we need R^T.
    R_w2l = R.transpose(-1, -2)  # (N_g, 3, 3)

    # Scale transform: S = diag(s_x, s_y, s_z)
    # To go from world to unit-sphere frame: apply R^T first (world→local),
    # then apply diag(1/s_x, 1/s_y, 1/s_z) (local→unit-sphere).
    # Combined transform matrix: M = diag(1/s) @ R^T
    # Point in unit-sphere frame: p_unit = diag(1/s) @ R^T @ (p - mean)

    # --- Vectorised over all (ray, gaussian) pairs -------------------------
    # We compute the intersection for every (ray, gaussian) pair.
    # For memory efficiency with large scenes, we process in chunks.

    CHUNK_SIZE = 4096  # rays per chunk to limit peak memory

    depths = torch.zeros(N_rays, N_gauss, device=device, dtype=dtype)

    for chunk_start in range(0, N_rays, CHUNK_SIZE):
        chunk_end = min(chunk_start + CHUNK_SIZE, N_rays)
        origins_chunk = ray_origins[chunk_start:chunk_end]  # (C, 3)
        dirs_chunk = ray_directions[chunk_start:chunk_end]  # (C, 3)
        C = origins_chunk.shape[0]

        # Expand for broadcasting: (C, 1, 3) - (1, N_g, 3) = (C, N_g, 3)
        origins_exp = origins_chunk.unsqueeze(1)  # (C, 1, 3)
        dirs_exp = dirs_chunk.unsqueeze(1)  # (C, 1, 3)
        means_exp = gaussian_means.unsqueeze(0)  # (1, N_g, 3)

        # Offset: ray_origin - gaussian_mean
        offset = origins_exp - means_exp  # (C, N_g, 3)

        # Transform to Gaussian local frame: R^T @ offset
        # offset: (C, N_g, 3), R_w2l: (N_g, 3, 3)
        offset_local = torch.einsum("gji, cgj -> cgi", R_w2l, offset)  # (C, N_g, 3)

        # Transform direction to local frame: R^T @ direction
        dirs_local = torch.einsum("gji, cgj -> cgi", R_w2l, dirs_exp)  # (C, N_g, 3)

        # Scale to unit-sphere frame: multiply by diag(1/s)
        scale_inv_exp = scale_inv.unsqueeze(0)  # (1, N_g, 3)
        offset_unit = offset_local * scale_inv_exp  # (C, N_g, 3)
        dirs_unit = dirs_local * scale_inv_exp  # (C, N_g, 3)

        # Solve quadratic: |offset_unit + t * dirs_unit|^2 = 1
        # a = |dirs_unit|^2
        # b = 2 * dot(offset_unit, dirs_unit)
        # c = |offset_unit|^2 - 1
        a = (dirs_unit ** 2).sum(dim=-1)  # (C, N_g)
        b = 2.0 * (offset_unit * dirs_unit).sum(dim=-1)  # (C, N_g)
        c = (offset_unit ** 2).sum(dim=-1) - 1.0  # (C, N_g)

        discriminant = b ** 2 - 4.0 * a  # (C, N_g)

        # Intersection exists when discriminant >= 0
        has_intersection = discriminant >= 0.0  # (C, N_g)

        # Compute intersection parameter t for valid intersections
        # t = (-b - sqrt(discriminant)) / (2a)  (smaller root = nearer surface)
        sqrt_disc = torch.sqrt(discriminant.clamp(min=0.0))  # (C, N_g)
        t_near = (-b - sqrt_disc) / (2.0 * a.clamp(min=1e-10))  # (C, N_g)

        # If t_near < 0 (ray origin inside ellipsoid), use the far intersection
        t_far = (-b + sqrt_disc) / (2.0 * a.clamp(min=1e-10))  # (C, N_g)
        t_valid = torch.where(t_near > 0, t_near, t_far)  # (C, N_g)

        # Intersection depth in world space:
        # The ray is P(t) = O + t * D.  The intersection point is O + t * D.
        # Depth (distance along viewing direction) = dot(P - O, D_hat)
        #   where D_hat = D / |D|.
        # = dot(t * D, D / |D|) = t * |D|
        # For unit D, depth = t directly.
        dir_sq = (dirs_chunk ** 2).sum(dim=-1, keepdim=True)  # (C, 1)
        dir_sq = dir_sq.clamp(min=1e-10)
        dir_norm = torch.sqrt(dir_sq.squeeze(-1))  # (C,)
        depth_intersection = t_valid * dir_norm.unsqueeze(1)  # (C, N_g)

        # Fallback: depth of Gaussian centre projected onto ray
        # depth_center = dot(M - O, D_hat) = dot(M - O, D) / |D|
        center_vec = (
            gaussian_means.unsqueeze(0) - origins_chunk.unsqueeze(1)
        )  # (C, N_g, 3)
        depth_center = (center_vec * dirs_chunk.unsqueeze(1)).sum(
            dim=-1
        ) / dir_norm.unsqueeze(1).clamp(min=1e-10)  # (C, N_g)

        # Choose intersection depth where valid, otherwise fall back to centre
        chunk_depths = torch.where(
            has_intersection & (t_valid > 0),
            depth_intersection,
            depth_center,
        )

        # If intersection exists but t <= 0 (behind the ray), also use centre
        chunk_depths = torch.where(
            has_intersection & (t_valid <= 0), depth_center, chunk_depths
        )

        depths[chunk_start:chunk_end] = chunk_depths

    logger.debug(
        "compute_intersection_depth: done, depth range=[%.4f, %.4f]",
        depths.min().item(),
        depths.max().item(),
    )

    return depths