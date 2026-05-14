"""ShareGS Gaussian homogenization for gap filling.

For each hole pixel, finds the nearest non-hole Gaussian, clones it,
and adjusts its position/scale/color to fill the gap. The cloning is
guided by feature similarity and scale consistency so that the new
Gaussians blend naturally with their neighbours.
"""

from __future__ import annotations

import logging

import numpy as np
from scipy.ndimage import distance_transform_edt

from sphereforge.common.gaussian_parameters import inflate_scales, scales_to_activated
from sphereforge.stages.stage07_occlusion.projection import (
    world_to_camera_with_positive_depth,
)

logger = logging.getLogger("sphereforge.stage07.sharegs_homogenize")


def homogenize_gaussians(
    gaussians: dict,
    hole_mask: np.ndarray,
    camera_pose: np.ndarray,
    intrinsics: dict,
    feature_radius: int = 5,
    max_new_gaussians: int | None = None,
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
        max_new_gaussians: Optional hard cap for the number of new Gaussians
            added in this call.

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

    # Project existing Gaussian centres into image to find per-pixel assignments.
    fx = intrinsics.get("fx", 1.0)
    fy = intrinsics.get("fy", 1.0)
    cx = intrinsics.get("cx", W / 2.0)
    cy = intrinsics.get("cy", H / 2.0)

    R = camera_pose[:3, :3]
    t = camera_pose[:3, 3]
    cam_positions, positive_depth, forward_sign = world_to_camera_with_positive_depth(
        positions,
        camera_pose,
    )

    valid_mask = positive_depth > 1e-6
    if not np.any(valid_mask):
        logger.warning("No Gaussians visible in this camera — skipping homogenization")
        return gaussians

    valid_cam_pos = cam_positions[valid_mask]
    valid_depth = positive_depth[valid_mask]
    valid_idx = np.where(valid_mask)[0]

    # Project to pixel coordinates
    px = (valid_cam_pos[:, 0] / valid_depth) * fx + cx
    py = (valid_cam_pos[:, 1] / valid_depth) * fy + cy
    px_int = np.clip(np.round(px).astype(int), 0, W - 1)
    py_int = np.clip(np.round(py).astype(int), 0, H - 1)

    # Build a per-pixel index map of projected visible Gaussians.
    gauss_idx_map = np.full((H, W), -1, dtype=np.int32)
    gauss_idx_map[py_int, px_int] = valid_idx

    seed_mask = gauss_idx_map >= 0
    if not np.any(seed_mask):
        logger.warning("No projected Gaussian assignments available — skipping homogenization")
        return gaussians

    # Fill every pixel with the nearest projected Gaussian assignment so hole
    # pixels can clone from the closest actually visible source Gaussian.
    _seed_dist, nearest_seed_yx = distance_transform_edt(~seed_mask, return_indices=True)
    nearest_gauss_idx = gauss_idx_map[nearest_seed_yx[0], nearest_seed_yx[1]]

    # For hole pixels, determine which Gaussian to clone
    hole_ys, hole_xs = np.where(hole_mask)
    n_holes = len(hole_ys)

    if n_holes == 0:
        return gaussians

    # Subsample holes for efficiency — we don't need one Gaussian per pixel.
    # Use projected image-space footprint rather than raw world-space scale so
    # the sampling density tracks the visible splat size in the target view.
    projected_footprints = np.mean(scales_to_activated(scales[valid_idx]), axis=1)
    projected_footprints = projected_footprints * fx / np.maximum(valid_depth, 1e-6)
    median_footprint = float(np.median(projected_footprints)) if projected_footprints.size else 1.0
    stride = max(4, round(median_footprint * 0.5))
    stride = min(stride, max(H, W) // 16)

    hole_ys_sub = hole_ys[::stride]
    hole_xs_sub = hole_xs[::stride]
    if max_new_gaussians is not None and len(hole_ys_sub) > max_new_gaussians:
        hole_ys_sub = hole_ys_sub[:max_new_gaussians]
        hole_xs_sub = hole_xs_sub[:max_new_gaussians]
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
        src_gi = nearest_gauss_idx[hy, hx]
        if src_gi < 0:
            continue

        src_pos = positions[src_gi]
        src_col = colors[src_gi]
        src_opa = opacities[src_gi]
        src_scl = scales[src_gi]
        src_rot = rotations[src_gi]

        # Compute 3-D position for the new Gaussian by back-projecting
        # the hole pixel to the same depth as the source Gaussian.
        src_depth = float(positive_depth[src_gi])
        if src_depth < 1e-6:
            continue

        # Back-project pixel (hx, hy) to camera space
        x_cam = (hx - cx) / fx * src_depth
        y_cam = (hy - cy) / fy * src_depth
        pt_cam = np.array([x_cam, y_cam, src_depth * forward_sign, 1.0])

        # Transform to world space
        pt_world = cam_to_world @ pt_cam
        new_pos = pt_world[:3]

        # Slightly inflate scale for better coverage
        new_scl = inflate_scales(np.asarray([src_scl], dtype=np.float32), 1.2)[0]

        new_positions.append(new_pos)
        new_colors.append(src_col)
        new_opacities.append(src_opa)
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
