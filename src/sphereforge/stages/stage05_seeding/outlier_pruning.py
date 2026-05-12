"""Statistical outlier pruning for 3D Gaussian points.

Removes points whose mean distance to their k nearest neighbours exceeds
a statistical threshold (global mean + factor * global std), which
effectively eliminates isolated floaters.
"""

from __future__ import annotations

import logging

import numpy as np
from scipy.spatial import cKDTree

logger = logging.getLogger("sphereforge.stage05.outlier_pruning")


def prune_outliers(
    positions: np.ndarray,
    strength: float = 0.3,
) -> np.ndarray:
    """Remove statistical outliers based on k-nearest-neighbour distances.

    For each point the mean distance to its k=20 nearest neighbours is
    computed.  Points whose mean distance exceeds
    ``global_mean + strength * 3.0 * global_std`` are removed.

    Args:
        positions: (N, 3) float32 Gaussian world-space positions.
        strength: Pruning strength in [0, 1].  Higher values remove
            more aggressively.  A strength of 0 keeps all points.
            The effective multiplier is ``strength * 3.0`` so that the
            default (0.3) corresponds to a 0.9o threshold above the
            global mean.

    Returns:
        Boolean mask of shape (N,) where ``True`` means "keep".
    """
    n = positions.shape[0]
    k = 20

    if n == 0:
        return np.empty(0, dtype=bool)

    if n <= k:
        logger.warning(
            "Only %d points (k=%d) — too few for outlier pruning, keeping all",
            n,
            k,
        )
        return np.ones(n, dtype=bool)

    # Build KD-tree
    tree = cKDTree(positions)

    # Query k+1 because the first neighbour is the point itself
    dists, _ = tree.query(positions, k=k + 1)
    # Exclude self-distance (column 0)
    mean_dists = dists[:, 1:].mean(axis=1)  # (N,)

    # Global statistics
    global_mean = float(np.mean(mean_dists))
    global_std = float(np.std(mean_dists))

    # Threshold: mean + strength * factor * std
    factor = 3.0
    threshold = global_mean + strength * factor * global_std

    keep = mean_dists <= threshold

    n_removed = int(np.sum(~keep))
    logger.info(
        "Outlier pruning: %d/%d removed (strength=%.2f, "
        "mean_dist=%.4f, std=%.4f, threshold=%.4f)",
        n_removed,
        n,
        strength,
        global_mean,
        global_std,
        threshold,
    )

    return keep
