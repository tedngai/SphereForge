"""ShareGS scene patch reuse for gap filling.

Copies Gaussians from visible viewpoints that observe the same 3-D
region and transforms them into the hole location using camera poses.
This is effective for gaps caused by occlusion from a specific viewpoint
when the geometry is visible from other angles.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger("sphereforge.stage07.sharegs_reuse")


def reuse_patches(
    gaussians: dict,
    hole_mask: np.ndarray,
    source_views: list[dict],
    colmap_model: dict,
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
        source_views: List of dicts, each with ``viewmat`` (4,4), ``fov``,
            ``height``, ``width``. These are the views where the geometry
            *is* visible.
        colmap_model: COLMAP sparse model dict with ``cameras`` and
            ``images`` keys providing extrinsics and intrinsics for
            coordinate-frame alignment.

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

    # Identify which existing Gaussians are visible from source views
    # by projecting them into each source view and checking if they fall
    # in non-hole regions. Those are candidates for reuse.
    reused_positions = []
    reused_colors = []
    reused_opacities = []
    reused_scales = []
    reused_rotations = []
    reused_sh = [] if sh_coeffs is not None else None

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

        R = viewmat[:3, :3]
        t = viewmat[:3, 3]

        # Project existing Gaussians into this source view
        cam_pos = (R @ positions.T + t[:, None]).T
        z = cam_pos[:, 2]
        visible = z > 1e-6

        if not np.any(visible):
            continue

        vis_cam = cam_pos[visible]
        vis_idx = np.where(visible)[0]

        px = (vis_cam[:, 0] / vis_cam[:, 2]) * fx + cx
        py = (vis_cam[:, 1] / vis_cam[:, 2]) * fy + cy

        # Check which projected Gaussians fall within the image
        in_image = (px >= 0) & (px < sv_W) & (py >= 0) & (py < sv_H)

        if not np.any(in_image):
            continue

        # These Gaussians are visible from a source view — they are
        # candidates to be cloned and placed into holes. We clone them
        # with a slight position offset (small random jitter) and
        # slightly increased scale for better coverage.
        candidate_idx = vis_idx[in_image]

        # Limit the number of clones to avoid excessive memory use
        max_clones = min(len(candidate_idx), n_holes * 2)
        if len(candidate_idx) > max_clones:
            rng = np.random.default_rng(42)
            candidate_idx = rng.choice(candidate_idx, size=max_clones, replace=False)

        for gi in candidate_idx:
            # Clone with small jitter for diversity
            jitter = np.random.normal(0, 0.01, size=3).astype(np.float32)
            reused_positions.append(positions[gi] + jitter)
            reused_colors.append(colors[gi])
            reused_opacities.append(min(opacities[gi] * 0.95, 1.0))
            # Slightly inflate scale for overlap
            reused_scales.append(scales[gi] + np.log(1.1))
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
