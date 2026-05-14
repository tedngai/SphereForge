"""ShareGS scene patch reuse for gap filling.

Copies Gaussians from visible viewpoints that observe the same 3-D
region and transforms them into the hole location using camera poses.
This is effective for gaps caused by occlusion from a specific viewpoint
when the geometry is visible from other angles.
"""

from __future__ import annotations

import logging

import numpy as np
from scipy.ndimage import distance_transform_edt

from sphereforge.common.gaussian_parameters import attenuate_opacities, inflate_scales
from sphereforge.stages.stage07_occlusion.projection import (
    world_to_camera_with_positive_depth,
)

logger = logging.getLogger("sphereforge.stage07.sharegs_reuse")


def reuse_patches(
    gaussians: dict,
    hole_mask: np.ndarray,
    target_view: dict,
    source_views: list[dict],
    colmap_model: dict,
    max_new_gaussians: int | None = None,
) -> dict:
    """Fill holes by reusing Gaussians from other viewpoints.

    For gaps that match visible patches from other viewpoints, this
    function copies the contributing Gaussians and transforms them into
    the hole's coordinate frame using camera poses.

    Args:
        gaussians: Dictionary with keys ``positions`` (N,3), ``colors``
            (N,3), ``opacities`` (N,), ``scales`` (N,3), ``rotations`` (N,4),
            and optionally ``sh_coeffs`` (N,45).
        hole_mask: Boolean mask of shape (H, W). ``True`` = hole pixel.
        target_view: Dict for the camera currently being filled. Must contain
            ``viewmat`` plus ``fov``, ``height``, and ``width``.
        source_views: List of dicts, each with ``viewmat`` (4,4), ``fov``,
            ``height``, ``width``. These are the views where the geometry
            *is* visible.
        colmap_model: COLMAP sparse model dict with ``cameras`` and
            ``images`` keys providing extrinsics and intrinsics for
            coordinate-frame alignment.
        max_new_gaussians: Optional hard cap for the number of reused
            Gaussians added in this call.

    Returns:
        Updated gaussians dict with reused Gaussians added to fill holes.
    """
    hole_mask = np.asarray(hole_mask, dtype=bool)
    positions = np.asarray(gaussians["positions"], dtype=np.float32)
    colors = np.asarray(gaussians["colors"], dtype=np.float32)
    opacities = np.asarray(gaussians["opacities"], dtype=np.float32)
    scales = np.asarray(gaussians["scales"], dtype=np.float32)
    rotations = np.asarray(gaussians["rotations"], dtype=np.float32)
    sh_coeffs = gaussians.get("sh_coeffs")
    if sh_coeffs is not None:
        sh_coeffs = np.asarray(sh_coeffs, dtype=np.float32)

    H, W = hole_mask.shape
    n_holes = int(np.sum(hole_mask))

    if n_holes == 0:
        logger.debug("No holes to fill via patch reuse")
        return gaussians

    if not source_views:
        logger.warning("No source views provided for patch reuse")
        return gaussians

    target_viewmat = np.asarray(target_view["viewmat"], dtype=np.float64)
    target_fov = float(target_view.get("fov", 90.0))
    target_fx = (W / 2.0) / np.tan(np.radians(target_fov) / 2.0)
    target_fy = target_fx
    target_cx = W / 2.0
    target_cy = H / 2.0
    target_cam_to_world = np.linalg.inv(target_viewmat)
    _, target_depth, target_forward_sign = world_to_camera_with_positive_depth(positions, target_viewmat)

    reused_positions = []
    reused_colors = []
    reused_opacities = []
    reused_scales = []
    reused_rotations = []
    reused_sh = [] if sh_coeffs is not None else None
    source_assignments: list[tuple[np.ndarray, np.ndarray, int, int]] = []

    for sv in source_views:
        viewmat = np.asarray(sv["viewmat"], dtype=np.float64)
        sv_H = sv.get("height", H)
        sv_W = sv.get("width", W)
        fov = sv.get("fov", 90.0)

        # Compute intrinsics from fov
        fx = (sv_W / 2.0) / np.tan(np.radians(fov) / 2.0)
        fy = fx  # square pixels
        cx = sv_W / 2.0
        cy = sv_H / 2.0

        # Project existing Gaussians into this source view
        cam_pos, depth, _forward_sign = world_to_camera_with_positive_depth(positions, viewmat)
        visible = depth > 1e-6

        if not np.any(visible):
            continue

        vis_cam = cam_pos[visible]
        vis_depth = depth[visible]
        vis_idx = np.where(visible)[0]

        px = (vis_cam[:, 0] / vis_depth) * fx + cx
        py = (vis_cam[:, 1] / vis_depth) * fy + cy

        # Check which projected Gaussians fall within the image
        in_image = (px >= 0) & (px < sv_W) & (py >= 0) & (py < sv_H)

        if not np.any(in_image):
            continue

        in_view_idx = vis_idx[in_image]
        in_view_px = np.clip(np.round(px[in_image]).astype(int), 0, sv_W - 1)
        in_view_py = np.clip(np.round(py[in_image]).astype(int), 0, sv_H - 1)

        gauss_idx_map = np.full((sv_H, sv_W), -1, dtype=np.int32)
        gauss_idx_map[in_view_py, in_view_px] = in_view_idx
        seed_mask = gauss_idx_map >= 0
        if not np.any(seed_mask):
            continue

        seed_dist, nearest_seed_yx = distance_transform_edt(~seed_mask, return_indices=True)
        nearest_gauss_idx = gauss_idx_map[nearest_seed_yx[0], nearest_seed_yx[1]]
        source_assignments.append((nearest_gauss_idx, seed_dist.astype(np.float32), sv_H, sv_W))

    if not source_assignments:
        logger.warning("No Gaussians reused from source views")
        return gaussians

    hole_budget = max(64, n_holes // 256)
    effective_budget = hole_budget
    if max_new_gaussians is not None:
        effective_budget = min(effective_budget, max_new_gaussians)

    if effective_budget <= 0:
        logger.info("Patch reuse skipped: no remaining Gaussian budget")
        return gaussians

    hole_ys, hole_xs = np.where(hole_mask)
    if hole_ys.size == 0:
        return gaussians

    step = max(1, hole_ys.size // effective_budget)
    sampled_ys = hole_ys[::step][:effective_budget]
    sampled_xs = hole_xs[::step][:effective_budget]

    for hy, hx in zip(sampled_ys, sampled_xs, strict=False):
        best_gi = -1
        best_dist = float("inf")
        for nearest_gauss_idx, seed_dist, sv_H, sv_W in source_assignments:
            sy = min(int(round(hy * (sv_H / max(H, 1)))), sv_H - 1)
            sx = min(int(round(hx * (sv_W / max(W, 1)))), sv_W - 1)
            gi = int(nearest_gauss_idx[sy, sx])
            if gi < 0:
                continue
            dist = float(seed_dist[sy, sx])
            if dist < best_dist:
                best_dist = dist
                best_gi = gi

        if best_gi < 0:
            continue

        target_point_depth = float(target_depth[best_gi])
        if target_point_depth <= 1e-6:
            continue

        x_cam = (hx - target_cx) / target_fx * target_point_depth
        y_cam = (hy - target_cy) / target_fy * target_point_depth
        pt_cam = np.array([x_cam, y_cam, target_point_depth * target_forward_sign, 1.0], dtype=np.float32)
        pt_world = target_cam_to_world @ pt_cam

        reused_positions.append(pt_world[:3].astype(np.float32))
        gi = best_gi
        reused_colors.append(colors[gi])
        reused_opacities.append(
            attenuate_opacities(np.asarray([opacities[gi]], dtype=np.float32), 0.95)[0]
        )
        reused_scales.append(
            inflate_scales(np.asarray([scales[gi]], dtype=np.float32), 1.1)[0]
        )
        reused_rotations.append(rotations[gi])
        if reused_sh is not None:
            reused_sh.append(sh_coeffs[gi])

    if not reused_positions:
        logger.warning("No Gaussians reused from source views")
        return gaussians

    reused_positions = np.array(reused_positions, dtype=np.float32)
    reused_colors = np.array(reused_colors, dtype=np.float32)
    reused_opacities = np.array(reused_opacities, dtype=np.float32)
    reused_scales = np.array(reused_scales, dtype=np.float32)
    reused_rotations = np.array(reused_rotations, dtype=np.float32)

    result = {
        "positions": np.concatenate([positions, reused_positions], axis=0),
        "colors": np.concatenate([colors, reused_colors], axis=0),
        "opacities": np.concatenate([opacities, reused_opacities], axis=0),
        "scales": np.concatenate([scales, reused_scales], axis=0),
        "rotations": np.concatenate([rotations, reused_rotations], axis=0),
    }

    if sh_coeffs is not None and reused_sh is not None:
        reused_sh_arr = np.array(reused_sh, dtype=np.float32)
        result["sh_coeffs"] = np.concatenate([sh_coeffs, reused_sh_arr], axis=0)
    elif sh_coeffs is not None:
        n_new = reused_positions.shape[0]
        result["sh_coeffs"] = np.concatenate(
            [sh_coeffs, np.zeros((n_new, sh_coeffs.shape[1]), dtype=np.float32)],
            axis=0,
        )

    logger.info(
        "Patch reuse added %d Gaussians from %d source views (total: %d)",
        reused_positions.shape[0],
        len(source_views),
        result["positions"].shape[0],
    )
    return result
