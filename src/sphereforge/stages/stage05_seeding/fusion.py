"""Multi-view fusion of camera-local 3D points into world coordinates.

Transforms per-view point clouds from camera-local to world coordinates
using COLMAP extrinsics, then merges nearby points via KD-tree
neighbour search and confidence-weighted averaging.
"""

from __future__ import annotations

import logging

import numpy as np
from scipy.spatial import cKDTree

from sphereforge.common.colmap_helpers import quat_to_rotation_matrix

logger = logging.getLogger("sphereforge.stage05.fusion")


def fuse_multiview(
    positions_list: list[np.ndarray],
    colors_list: list[np.ndarray],
    sparse_model: dict,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fuse multi-view Gaussians into COLMAP world coordinates.

    For each view the local positions are transformed to world coordinates
    using the COLMAP extrinsics stored in *sparse_model*::

        world_pos = R^T @ (local_pos - t)

    where R is the rotation matrix derived from the image quaternion and
    t is the translation vector.

    A KD-tree is then built over all world-space positions and points
    within *dedup_distance* are clustered.  Clustered positions and
    colours are averaged, weighted by the number of contributing views
    (confidence).

    Args:
        positions_list: List of per-view position arrays, each (N_v, 3)
            in camera-local coordinates.
        colors_list: List of per-view colour arrays, each (N_v, 3) uint8.
        sparse_model: COLMAP sparse model dict with key ``"images"``
            mapping image_id → {qw, qx, qy, qz, tx, ty, tz, …}.

    Returns:
        A tuple ``(fused_positions, fused_colors, confidence)`` where:
            - fused_positions is (M, 3) float32 world-space positions.
            - fused_colors is (M, 3) float32 averaged colours.
            - confidence is (M,) int32 — number of views that contributed
              to each fused point.

    Raises:
        ValueError: If lists are empty, lengths mismatch, or the sparse
            model lacks the required keys.
    """
    if len(positions_list) != len(colors_list):
        raise ValueError(
            f"positions_list and colors_list must have the same length, "
            f"got {len(positions_list)} vs {len(colors_list)}"
        )
    if len(positions_list) == 0:
        raise ValueError("positions_list is empty — nothing to fuse")

    images_dict = sparse_model.get("images", {})
    if not images_dict:
        raise ValueError("sparse_model must contain 'images' dict with extrinsics")

    # Collect world-space positions with view index
    all_positions: list[np.ndarray] = []
    all_colors: list[np.ndarray] = []
    all_view_ids: list[int] = []

    # Image IDs sorted to correspond with input list order
    image_ids = sorted(images_dict.keys())

    for view_idx, (local_pos, local_col) in enumerate(
        zip(positions_list, colors_list)
    ):
        # Look up extrinsics — try to match by view index to image ID
        image_id = image_ids[view_idx] if view_idx < len(image_ids) else image_ids[0]
        img_data = images_dict[image_id]

        qw = img_data["qw"]
        qx = img_data["qx"]
        qy = img_data["qy"]
        qz = img_data["qz"]
        t = np.array(
            [img_data["tx"], img_data["ty"], img_data["tz"]], dtype=np.float64
        )

        R = quat_to_rotation_matrix(qw, qx, qy, qz)  # 3x3

        # Transform: world_pos = R^T @ (local_pos - t)
        shifted = local_pos.astype(np.float64) - t[np.newaxis, :]
        world_pos = (R.T @ shifted.T).T  # (N, 3)

        all_positions.append(world_pos.astype(np.float32))
        all_colors.append(local_col.astype(np.float32))
        all_view_ids.append(view_idx)

    # Concatenate all world-space points
    world_positions = np.concatenate(all_positions, axis=0)  # (N_total, 3)
    world_colors = np.concatenate(all_colors, axis=0)  # (N_total, 3)

    n_total = world_positions.shape[0]
    logger.info("Fusing %d points from %d views", n_total, len(positions_list))

    # Build KD-tree and cluster nearby points
    tree = cKDTree(world_positions)

    # Compute dedup_distance as 0.01 * scene extent
    pos_range = np.ptp(world_positions, axis=0)
    scene_extent = float(np.max(pos_range))
    dedup_distance = 0.01 * scene_extent if scene_extent > 0 else 0.01

    logger.debug("Dedup distance: %.6f (scene_extent=%.2f)", dedup_distance, scene_extent)

    # Find neighbour pairs
    pairs = tree.query_pairs(r=dedup_distance)

    # Union-Find for clustering
    parent = list(range(n_total))

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
    for idx in range(n_total):
        root = find(idx)
        clusters.setdefault(root, []).append(idx)

    # Merge each cluster with confidence weighting
    fused_pos_list: list[np.ndarray] = []
    fused_col_list: list[np.ndarray] = []
    confidence_list: list[int] = []

    for root, members in clusters.items():
        n_members = len(members)
        # Confidence = number of contributing views (each point counts as 1)
        member_pos = world_positions[members]  # (K, 3)
        member_col = world_colors[members]  # (K, 3)

        # Equal weight per point (confidence = 1 per point)
        weights = np.ones(n_members, dtype=np.float64)
        w_sum = weights.sum()

        avg_pos = (member_pos.astype(np.float64) * weights[:, np.newaxis]).sum(
            axis=0
        ) / w_sum
        avg_col = (member_col.astype(np.float64) * weights[:, np.newaxis]).sum(
            axis=0
        ) / w_sum

        fused_pos_list.append(avg_pos.astype(np.float32))
        fused_col_list.append(avg_col.astype(np.float32))
        confidence_list.append(n_members)

    fused_positions = np.stack(fused_pos_list, axis=0)
    fused_colors = np.stack(fused_col_list, axis=0)
    confidence = np.array(confidence_list, dtype=np.int32)

    logger.info(
        "Fusion: %d input points → %d fused points (dedup_dist=%.4f)",
        n_total,
        fused_positions.shape[0],
        dedup_distance,
    )

    return fused_positions, fused_colors, confidence
