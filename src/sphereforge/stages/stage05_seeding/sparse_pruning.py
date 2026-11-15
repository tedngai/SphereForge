"""Sparse-region pruning for 3D Gaussian points.

Removes isolated Gaussians that have fewer than a minimum number of
neighbours within a specified radius, which cleans up noisy lone points
that do not contribute meaningfully to the scene.
"""

from __future__ import annotations

import logging

import numpy as np
from scipy.spatial import cKDTree

logger = logging.getLogger("sphereforge.stage05.sparse_pruning")


def prune_sparse_regions(
    positions: np.ndarray,
    strength: float = 0.3,
) -> np.ndarray:
    """Remove isolated Gaussians in sparse regions.

    The neighbour radius is derived from the cloud's own spacing: the median
    k-nearest-neighbour distance (k=20).  A point is kept when it has at least
    ``min_neighbors`` neighbours within ``(1 + strength)`` times that spacing.
    This makes the filter scale-invariant and independent of the bounding-box
    extent, which is dominated by a few far-away floaters.

    Args:
        positions: (N, 3) float32 Gaussian world-space positions.
        strength: Pruning strength in [0, 1].  Controls both the neighbour
            radius and the minimum neighbour count:
            ``min_neighbors = max(1, int(strength * 10))``.
            Default 0.3 → min_neighbors = 3.

    Returns:
        Boolean mask of shape (N,) where ``True`` means "keep".
    """
    n = positions.shape[0]

    if n == 0:
        return np.empty(0, dtype=bool)

    # Compute scene extent
    pos_range = np.ptp(positions, axis=0)
    scene_extent = float(np.max(pos_range))
    if scene_extent < 1e-10:
        scene_extent = 1.0

    # Min neighbours scales with strength
    min_neighbors = max(1, int(strength * 10))

    # Build KD-tree
    tree = cKDTree(positions)

    # Neighbour radius is derived from the *typical* spacing of the point cloud
    # (median k-NN distance) rather than from the bounding-box extent. Using the
    # extent makes the radius collapse to a fraction of the spacing for a tight
    # cluster, which would flag every point as "isolated".
    k = min(20, n - 1)
    if k < 1:
        return np.ones(n, dtype=bool)
    knn_dists, _ = tree.query(positions, k=k + 1)
    median_spacing = float(np.median(knn_dists[:, 1:]))

    # A point is "sparse" when it has fewer than min_neighbors neighbours within
    # a radius of (1 + strength) times the typical spacing.
    radius = max(median_spacing * (1.0 + strength), 1e-9)

    # Count neighbours within radius (includes self, so subtract 1)
    neighbor_counts = tree.query_ball_point(positions, r=radius, return_length=True)
    neighbor_counts = neighbor_counts - 1  # exclude self

    keep = neighbor_counts >= min_neighbors

    n_removed = int(np.sum(~keep))
    logger.info(
        "Sparse pruning: %d/%d removed (strength=%.2f, radius=%.4f, "
        "min_neighbors=%d)",
        n_removed,
        n,
        strength,
        radius,
        min_neighbors,
    )

    return keep
