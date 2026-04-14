"""Sky removal for 3D Gaussian points.

Filters out Gaussians whose source depth exceeds a sky threshold,
effectively removing sky / infinity geometry that would otherwise
waste Gaussian budget.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger("sphereforge.stage05.sky_removal")


def remove_sky(
    positions: np.ndarray,
    depth_map: np.ndarray,
    sky_threshold: str | float = "auto",
) -> np.ndarray:
    """Remove Gaussians at sky depth.

    Points whose source depth exceeds the sky threshold are marked for
    removal.  When *sky_threshold* is ``"auto"``, the 95th percentile
    of the depth map is used as the threshold.

    Args:
        positions: (N, 3) float32 Gaussian positions.  Used only to
            determine the number of points.
        depth_map: (H, W) float32 depth map from which the positions
            were projected.  Also accepted as a 1-D array of per-point
            depth values (length N) for efficiency.
        sky_threshold: Depth threshold for sky removal.  ``"auto"`` uses
            the 95th percentile of the depth map.  A float value is
            used directly as the threshold in the same units as the
            depth map.

    Returns:
        Boolean mask of shape (N,) where ``True`` means "keep" (not sky).
    """
    n = positions.shape[0]

    if n == 0:
        return np.empty(0, dtype=bool)

    # If depth_map is 2D, flatten it for percentile computation
    depth_flat = depth_map.ravel().astype(np.float64)
    valid_depth = depth_flat[depth_flat > 0]

    if valid_depth.size == 0:
        logger.warning("No valid depth values — keeping all points")
        return np.ones(n, dtype=bool)

    # Determine threshold
    if sky_threshold == "auto":
        threshold = float(np.percentile(valid_depth, 95))
    else:
        threshold = float(sky_threshold)

    # For a 2D depth map we cannot directly map points to depths here
    # without the original pixel coordinates.  In practice this function
    # is called with per-point depth values passed as a 1-D array.
    # If depth_map is 1-D, use it directly.
    if depth_map.ndim == 1:
        per_point_depth = depth_map.astype(np.float64)
    else:
        # Fallback: use the depth map percentile to classify
        # This is a heuristic — all points with depth > threshold are removed
        # For 2D depth maps, compute per-point depths from positions
        # (distance from origin as approximation of radial depth)
        per_point_depth = np.linalg.norm(positions.astype(np.float64), axis=1)

    keep = per_point_depth <= threshold

    n_removed = int(np.sum(~keep))
    logger.info(
        "Sky removal: %d/%d removed (threshold=%.2f)",
        n_removed,
        n,
        threshold,
    )

    return keep
