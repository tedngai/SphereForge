"""Deduplication of Gaussians by distance-based clustering.

Merges Gaussians that are within a threshold distance of each other using
a greedy DBSCAN-like approach with confidence-weighted averaging.
"""

from __future__ import annotations

import logging

import numpy as np
from scipy.spatial import cKDTree

logger = logging.getLogger("sphereforge.stage05.deduplication")


def deduplicate_gaussians(
    positions: np.ndarray,
    colors: np.ndarray,
    confidence: np.ndarray,
    dedup_distance: str | float = "auto",
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Merge Gaussians within a threshold distance.

    Uses scipy's cKDTree to find neighbour pairs within *dedup_distance*
    and merges them via Union-Find clustering.  Merged positions and
    colours are computed as confidence-weighted averages.

    Args:
        positions: (N, 3) float32 world-space Gaussian centres.
        colors: (N, 3) float32 or uint8 per-Gaussian colours.
        confidence: (N,) float32 or int confidence / view count per point.
        dedup_distance: Merge threshold.  ``"auto"`` computes
            ``0.01 * scene_extent`` where scene_extent is the maximum
            axis-wise range of positions.  A float value is used directly.

    Returns:
        A tuple ``(positions, colors, confidence)`` of deduplicated arrays:
            - positions: (M, 3) float32
            - colors: (M, 3) float32
            - confidence: (M,) float32 — summed confidence of merged points

    Raises:
        ValueError: If input shapes are inconsistent.
    """
    n = positions.shape[0]
    if n == 0:
        return (
            np.empty((0, 3), dtype=np.float32),
            np.empty((0, 3), dtype=np.float32),
            np.empty(0, dtype=np.float32),
        )

    if positions.shape[1] != 3:
        raise ValueError(f"positions must be Nx3, got {positions.shape}")
    if colors.shape[0] != n or colors.shape[1] != 3:
        raise ValueError(f"colors must be Nx3 with N={n}, got {colors.shape}")
    if confidence.shape[0] != n:
        raise ValueError(f"confidence must have length N={n}, got {confidence.shape}")

    # Compute dedup distance
    if dedup_distance == "auto":
        pos_range = np.ptp(positions, axis=0)
        scene_extent = float(np.max(pos_range))
        dedup_dist = 0.01 * scene_extent if scene_extent > 0 else 0.01
    else:
        dedup_dist = float(dedup_distance)

    logger.debug("Dedup distance: %.6f", dedup_dist)

    if dedup_dist <= 0:
        logger.warning("Dedup distance <= 0, returning input unchanged")
        return (
            positions.astype(np.float32),
            colors.astype(np.float32),
            confidence.astype(np.float32),
        )

    # Build KD-tree and find pairs
    tree = cKDTree(positions)
    pairs = tree.query_pairs(r=dedup_dist)

    # Union-Find
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i, j in pairs:
        union(i, j)

    # Group by root
    clusters: dict[int, list[int]] = {}
    for idx in range(n):
        root = find(idx)
        clusters.setdefault(root, []).append(idx)

    # Merge with confidence weighting
    conf = confidence.astype(np.float64)
    pos_f = positions.astype(np.float64)
    col_f = colors.astype(np.float64)

    fused_pos_list: list[np.ndarray] = []
    fused_col_list: list[np.ndarray] = []
    fused_conf_list: list[float] = []

    for _root, members in clusters.items():
        member_pos = pos_f[members]  # (K, 3)
        member_col = col_f[members]  # (K, 3)
        member_conf = conf[members]  # (K,)

        w_sum = member_conf.sum()
        if w_sum < 1e-10:
            w_sum = 1.0

        weights = member_conf / w_sum
        avg_pos = (member_pos * weights[:, np.newaxis]).sum(axis=0)
        avg_col = (member_col * weights[:, np.newaxis]).sum(axis=0)
        total_conf = float(member_conf.sum())

        fused_pos_list.append(avg_pos.astype(np.float32))
        fused_col_list.append(avg_col.astype(np.float32))
        fused_conf_list.append(total_conf)

    out_pos = np.stack(fused_pos_list, axis=0)
    out_col = np.stack(fused_col_list, axis=0)
    out_conf = np.array(fused_conf_list, dtype=np.float32)

    logger.info(
        "Dedup: %d → %d points (dedup_dist=%.4f)",
        n,
        out_pos.shape[0],
        dedup_dist,
    )

    return out_pos, out_col, out_conf
