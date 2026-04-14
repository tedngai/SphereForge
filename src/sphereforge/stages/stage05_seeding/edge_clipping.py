"""Grazing-angle edge clipping for 3D Gaussians.

Removes Gaussians that are observed at a grazing angle (angle between
view direction and surface normal exceeds a threshold), which typically
corresponds to unreliable geometry at object edges.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger("sphereforge.stage05.edge_clipping")


def clip_grazing_angles(
    positions: np.ndarray,
    camera_origins: np.ndarray,
    threshold_deg: int = 65,
) -> np.ndarray:
    """Remove Gaussians viewed at a grazing angle exceeding a threshold.

    For each Gaussian the surface normal is approximated by the direction
    from the scene centre to the point.  The viewing angle is the angle
    between the view direction (camera → point) and this approximate
    normal.  Points viewed at angles greater than *threshold_deg* are
    marked for removal.

    When multiple camera origins are provided, a point is kept if *any*
    camera views it below the threshold.

    Args:
        positions: (N, 3) float32 Gaussian world-space positions.
        camera_origins: (M, 3) float32 camera world-space origins.
        threshold_deg: Maximum allowed angle in degrees between view
            direction and surface normal.  Default 65.  Set to 90 to
            disable clipping.

    Returns:
        Boolean mask of shape (N,) where ``True`` means "keep".
    """
    n = positions.shape[0]
    if n == 0:
        return np.empty(0, dtype=bool)

    # Scene centre = centroid of all positions
    scene_center = positions.mean(axis=0)

    # Approximate surface normal: direction from scene centre to point
    normal_dirs = positions - scene_center  # (N, 3)
    normal_norms = np.linalg.norm(normal_dirs, axis=1, keepdims=True)
    safe_norms = np.where(normal_norms > 1e-10, normal_norms, 1.0)
    normal_dirs = normal_dirs / safe_norms  # (N, 3) unit vectors

    # Convert threshold to radians — compute cosine threshold
    # "Angle between view direction and normal" — keep if angle <= threshold
    cos_threshold = np.cos(np.radians(threshold_deg))

    # Start with all removed
    keep = np.zeros(n, dtype=bool)

    for cam_idx in range(camera_origins.shape[0]):
        cam_origin = camera_origins[cam_idx]  # (3,)

        # View direction: camera → point (unnormalized is fine for angle calc)
        view_dirs = positions - cam_origin  # (N, 3)
        view_norms = np.linalg.norm(view_dirs, axis=1, keepdims=True)
        safe_view = np.where(view_norms > 1e-10, view_norms, 1.0)
        view_dirs = view_dirs / safe_view  # (N, 3) unit vectors

        # Cosine of angle between view direction and surface normal
        cos_angle = np.sum(view_dirs * normal_dirs, axis=1)  # (N,)

        # Keep if cos(angle) >= cos(threshold), i.e., angle <= threshold
        # cos_angle can be negative (viewing from behind) — those are grazing
        keep |= cos_angle >= cos_threshold

    n_removed = int(np.sum(~keep))
    logger.info(
        "Grazing-angle clipping: %d/%d points removed (threshold=%d°)",
        n_removed,
        n,
        threshold_deg,
    )

    return keep
