"""Spherical projection from ERP frame + depth to 3D point cloud.

Projects equirectangular pixels along their spherical ray directions,
scaled by per-pixel depth, to produce 3D positions and corresponding colours.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger("sphereforge.stage05.projection")


def project_to_3d(
    image: np.ndarray,
    depth_map: np.ndarray,
    stride: int = 1,
) -> tuple[np.ndarray, np.ndarray]:
    """Project an equirectangular image and depth map to 3D point positions.

    For each pixel at (v, u) sampled with *stride*, the ERP spherical
    coordinates are computed as::

        phi   = pi * v / H        (latitude, 0 at top row)
        theta = 2 * pi * u / W    (longitude, 0 at left column)

    The ray direction (y-up convention) is::

        d = (sin(phi)*cos(theta), cos(phi), sin(phi)*sin(theta))

    and the 3-D position is ``depth[v, u] * d``.

    Args:
        image: ERP image of shape (H, W, 3) with dtype uint8.
        depth_map: Depth map of shape (H, W) with dtype float32.
        stride: Sampling stride — only every *stride*-th pixel in both
            dimensions is projected.  A stride of 1 produces a point per
            pixel; stride > 1 subsamples for faster processing.

    Returns:
        A tuple ``(positions, colors)`` where:
            - positions is an (N, 3) float32 array of 3-D coordinates.
            - colors is an (N, 3) uint8 array of per-point RGB colours.

    Raises:
        ValueError: If shapes are inconsistent or stride < 1.
    """
    if stride < 1:
        raise ValueError(f"stride must be >= 1, got {stride}")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"image must be (H, W, 3), got shape {image.shape}")
    if depth_map.ndim != 2:
        raise ValueError(f"depth_map must be (H, W), got shape {depth_map.shape}")
    if image.shape[:2] != depth_map.shape:
        raise ValueError(
            f"image and depth_map spatial dims must match: "
            f"{image.shape[:2]} vs {depth_map.shape}"
        )

    h, w = depth_map.shape

    # Sampled pixel coordinates
    v_idx = np.arange(0, h, stride, dtype=np.float64)
    u_idx = np.arange(0, w, stride, dtype=np.float64)
    uu, vv = np.meshgrid(u_idx, v_idx)  # (rows, cols)

    # Spherical coordinates
    phi = np.pi * vv / h  # latitude [0, pi]
    theta = 2.0 * np.pi * uu / w  # longitude [0, 2*pi)

    # Ray directions (y-up)
    sin_phi = np.sin(phi)
    cos_phi = np.cos(phi)
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    dx = sin_phi * cos_theta
    dy = cos_phi
    dz = sin_phi * sin_theta

    # Sample depth and image at stride positions
    v_int = v_idx.astype(int)
    u_int = u_idx.astype(int)
    depth_samples = depth_map[np.ix_(v_int, u_int)]  # (rows, cols)
    image_samples = image[np.ix_(v_int, u_int)]  # (rows, cols, 3)

    # Valid mask: depth > 0
    valid = depth_samples > 0

    # 3-D positions: depth * direction
    pos_x = depth_samples * dx
    pos_y = depth_samples * dy
    pos_z = depth_samples * dz

    # Stack and filter
    positions = np.stack([pos_x, pos_y, pos_z], axis=-1)  # (rows, cols, 3)
    colors_raw = image_samples  # (rows, cols, 3)

    # Flatten and filter by valid depth
    positions_flat = positions.reshape(-1, 3)
    colors_flat = colors_raw.reshape(-1, 3)
    valid_flat = valid.reshape(-1)

    positions_out = positions_flat[valid_flat].astype(np.float32)
    colors_out = colors_flat[valid_flat].astype(np.uint8)

    logger.debug(
        "project_to_3d: stride=%d, %d/%d valid points from %dx%d image",
        stride,
        positions_out.shape[0],
        valid_flat.shape[0],
        h,
        w,
    )

    return positions_out, colors_out
