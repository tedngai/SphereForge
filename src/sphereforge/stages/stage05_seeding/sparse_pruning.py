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

    For each point the number of neighbours within a radius
    ``r = 0.02 * scene_extent`` is counted.  Points with fewer than
    ``min_neighbors`` neighbours are removed.  The ``min_neighbors``
    value scales with *strength*: higher strength means a higher
    minimum neighbour requirement.

    Args:
        positions: (N, 3) float32 Gaussian world-space positions.
        strength: Pruning strength in [0, 1].  Controls the minimum
            neighbour count.  ``min_neighbors = max(1, int(strength * 10))``.
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

    radius = 0.02 * scene_extent

    # Min neighbours scales with strength
    min_neighbors = max(1, int(strength * 10))

    # Build KD-tree
    tree = cKDTree(positions)

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
