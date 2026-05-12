"""ShareGS Gaussian homogenization for gap filling.

For each hole pixel, finds the nearest non-hole Gaussian, clones it,
and adjusts its position/scale/color to fill the gap. The cloning is
guided by feature similarity and scale consistency so that the new
Gaussians blend naturally with their neighbours.
"""

from __future__ import annotations

import logging

import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt

logger = logging.getLogger("sphereforge.stage07.sharegs_homogenize")


def homogenize_gaussians(
    gaussians: dict,
    hole_mask: np.ndarray,
    camera_pose: np.ndarray,
    intrinsics: dict,
    feature_radius: int = 5,
) -> dict:
    """Fill holes by cloning and adjusting neighbouring Gaussians.

    For each hole pixel, the function finds the nearest non-hole pixel,
    identifies the Gaussian contributing to that pixel, clones it, and
    adjusts the clone's 3-D position to project into the hole location.
    Scale is slightly increased to ensure coverage, and colour is
    inherited from the source Gaussian.

    Args:
        gaussians: Dictionary with keys ``positions`` (N,3), ``colors``
            (N,3), ``opacities`` (N,), ``scales`` (N,3), ``rotations`` (N,4),
            and optionally ``sh_coeffs`` (N,45).
        hole_mask: Boolean mask of shape (H, W). ``True`` = hole pixel.
        camera_pose: 4x4 camera extrinsic matrix (world-to-camera).
        intrinsics: Dict with ``fx``, ``fy``, ``cx``, ``cy`` and image
            dimensions (``height``, ``width``).
        feature_radius: Radius in pixels for feature-similarity neighbourhood
            when selecting the best source Gaussian (default 5).

    Returns:
        Updated gaussians dict with new Gaussians appended to fill holes.
        The original Gaussians are not modified.
    """
    hole_mask = np.asarray(hole_mask, dtype=bool)
    camera_pose = np.asarray(camera_pose, dtype=np.float64)

    positions = np.asarray(gaussians["positions"], dtype=np.float32)
    colors = np.asarray(gaussians["colors"], dtype=np.float32)
    opacities = np.asarray(gaussians["opacities"], dtype=np.float32)
    scales = np.asarray(gaussians["scales"], dtype=np.float32)
    rotations = np.asarray(gaussians["rotations"], dtype=np.float32)
    sh_coeffs = gaussians.get("sh_coeffs")
    if sh_coeffs is not None:
        sh_coeffs = np.asarray(sh_coeffs, dtype=np.float32)

    H, W = hole_mask.shape

    if not np.any(hole_mask):
        logger.debug("No holes to homogenize")
        return gaussians

    # Compute the distance transform: for each hole pixel, find the
    # nearest non-hole pixel.
    _dist_map, nearest_yx = distance_transform_edt(~hole_mask, return_indices=True)

    # Project existing Gaussian centres into image to find per-pixel assignments.
    fx = intrinsics.get("fx", 1.0)
    fy = intrinsics.get("fy", 1.0)
    cx = intrinsics.get("cx", W / 2.0)
    cy = intrinsics.get("cy", H / 2.0)

    # World-to-camera projection
    R = camera_pose[:3, :3]
    t = camera_pose[:3, 3]
    cam_positions = (R @ positions.T + t[:, None]).T  # (N, 3)

    # Filter Gaussians in front of camera (z > 0)
    valid_mask = cam_positions[:, 2] > 1e-6
    if not np.any(valid_mask):
        logger.warning("No Gaussians visible in this camera — skipping homogenization")
        return gaussians

    valid_cam_pos = cam_positions[valid_mask]
    valid_idx = np.where(valid_mask)[0]

    # Project to pixel coordinates
    px = (valid_cam_pos[:, 0] / valid_cam_pos[:, 2]) * fx + cx
    py = (valid_cam_pos[:, 1] / valid_cam_pos[:, 2]) * fy + cy
    px_int = np.clip(np.round(px).astype(int), 0, W - 1)
    py_int = np.clip(np.round(py).astype(int), 0, H - 1)

    # Build a per-pixel index map of the nearest Gaussian
    gauss_idx_map = np.full((H, W), -1, dtype=np.int32)
    gauss_idx_map[py_int, px_int] = valid_idx

    # Dilate the index map so each pixel has a Gaussian assignment
    # Use iterative dilation of the index map
    for _ in range(feature_radius):
        dilated = binary_dilation(gauss_idx_map >= 0)
        # For newly filled pixels, copy from neighbours
        new_pixels = dilated & (gauss_idx_map < 0)
        if not np.any(new_pixels):
            break
        # Simple nearest-neighbour fill via the distance map
        for y, x in zip(*np.where(new_pixels), strict=False):
            ny, nx = nearest_yx[:, y, x]
            ny, nx = int(ny), int(nx)
            if gauss_idx_map[ny, nx] >= 0:
                gauss_idx_map[y, x] = gauss_idx_map[ny, nx]

    # For hole pixels, determine which Gaussian to clone
    hole_ys, hole_xs = np.where(hole_mask)
    n_holes = len(hole_ys)

    if n_holes == 0:
        return gaussians

    # Subsample holes for efficiency — we don't need one Gaussian per pixel.
    # Use stride proportional to average Gaussian scale.
    avg_scale = float(np.mean(np.exp(scales[valid_idx])))
    stride = max(1, round(avg_scale * fx * 0.5))
    stride = min(stride, max(H, W) // 8)

    hole_ys_sub = hole_ys[::stride]
    hole_xs_sub = hole_xs[::stride]
    n_new = len(hole_ys_sub)

    logger.info(
        "Homogenizing %d hole pixels (stride=%d → %d new Gaussians)",
        n_holes,
        stride,
        n_new,
    )

    new_positions = []
    new_colors = []
    new_opacities = []
    new_scales = []
    new_rotations = []
    new_sh = [] if sh_coeffs is not None else None

    cam_to_world = np.linalg.inv(camera_pose)

    for hy, hx in zip(hole_ys_sub, hole_xs_sub, strict=False):
        src_gi = gauss_idx_map[nearest_yx[0, hy, hx], nearest_yx[1, hy, hx]]
        if src_gi < 0:
            continue

        src_pos = positions[src_gi]
        src_col = colors[src_gi]
        src_opa = opacities[src_gi]
        src_scl = scales[src_gi]
        src_rot = rotations[src_gi]

        # Compute 3-D position for the new Gaussian by back-projecting
        # the hole pixel to the same depth as the source Gaussian.
        src_z_cam = (R @ src_pos + t)[2]
        if src_z_cam < 1e-6:
            continue

        # Back-project pixel (hx, hy) to camera space
        x_cam = (hx - cx) / fx * src_z_cam
        y_cam = (hy - cy) / fy * src_z_cam
        pt_cam = np.array([x_cam, y_cam, src_z_cam, 1.0])

        # Transform to world space
        pt_world = cam_to_world @ pt_cam
        new_pos = pt_world[:3]

        # Slightly inflate scale for better coverage
        new_scl = src_scl + np.log(1.2)  # ~20% larger in each axis

        new_positions.append(new_pos)
        new_colors.append(src_col)
        new_opacities.append(min(src_opa, 1.0))
        new_scales.append(new_scl)
        new_rotations.append(src_rot)
        if new_sh is not None:
            new_sh.append(sh_coeffs[src_gi])

    if not new_positions:
        logger.warning("No new Gaussians created during homogenization")
        return gaussians

    # Append new Gaussians
    new_positions = np.array(new_positions, dtype=np.float32)
    new_colors = np.array(new_colors, dtype=np.float32)
    new_opacities = np.array(new_opacities, dtype=np.float32)
    new_scales = np.array(new_scales, dtype=np.float32)
    new_rotations = np.array(new_rotations, dtype=np.float32)

    result = {
        "positions": np.concatenate([positions, new_positions], axis=0),
        "colors": np.concatenate([colors, new_colors], axis=0),
        "opacities": np.concatenate([opacities, new_opacities], axis=0),
        "scales": np.concatenate([scales, new_scales], axis=0),
        "rotations": np.concatenate([rotations, new_rotations], axis=0),
    }

    if sh_coeffs is not None and new_sh is not None:
        new_sh_arr = np.array(new_sh, dtype=np.float32)
        result["sh_coeffs"] = np.concatenate([sh_coeffs, new_sh_arr], axis=0)
    elif sh_coeffs is not None:
        # Pad sh_coeffs with zeros for new Gaussians
        n_new_gauss = new_positions.shape[0]
        result["sh_coeffs"] = np.concatenate(
            [sh_coeffs, np.zeros((n_new_gauss, sh_coeffs.shape[1]), dtype=np.float32)],
            axis=0,
        )

    logger.info(
        "Homogenization added %d Gaussians (total: %d)",
        new_positions.shape[0],
        result["positions"].shape[0],
    )
    return result
