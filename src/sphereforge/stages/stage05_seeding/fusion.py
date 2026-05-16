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
        zip(positions_list, colors_list, strict=False)
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
    # Use a fine grid for initial clustering, then merge neighboring cells.
    # Cell size = dedup_distance / 4 gives ~64× more cells than points in dense regions,
    # and the neighborhood merge catches points spanning cell boundaries.
    pos_range = np.ptp(world_positions, axis=0)
    scene_extent = float(np.max(pos_range))
    dedup_distance = max(0.01 * scene_extent, 0.01) if scene_extent > 0 else 0.01
    cell_size = max(dedup_distance / 4, max(0.0001, scene_extent / 100000))

    logger.debug("Dedup: dist=%.4f cell=%.4f (scene_extent=%.2f)", dedup_distance, cell_size, scene_extent)

    world_positions_f64 = world_positions.astype(np.float64)
    origin = world_positions_f64.min(axis=0) - cell_size
    grid_cells = np.floor((world_positions_f64 - origin) / cell_size).astype(np.int64)

    cell_indices = (
        grid_cells[:, 0].astype(np.int64) * 1_000_000_000_000
        + grid_cells[:, 1].astype(np.int64) * 1_000_000
        + grid_cells[:, 2].astype(np.int64)
    )

    sort_order = np.argsort(cell_indices)
    sorted_cells = cell_indices[sort_order]
    sorted_pos = world_positions[sort_order]
    sorted_col = world_colors[sort_order]

    cell_bounds = np.where(np.diff(sorted_cells) != 0)[0].astype(np.int64)
    starts = np.concatenate([[0], cell_bounds + 1])
    ends = np.concatenate([cell_bounds + 1, [n_total]])

    # Average within each fine-grid cell
    n_cells = len(starts)
    cell_pos = np.empty((n_cells, 3), dtype=np.float32)
    cell_col = np.empty((n_cells, 3), dtype=np.float32)
    cell_conf = np.empty(n_cells, dtype=np.int32)
    for i in range(n_cells):
        s, e = int(starts[i]), int(ends[i])
        cluster_size = e - s
        cell_pos[i] = sorted_pos[s:e].mean(axis=0).astype(np.float32)
        cell_col[i] = sorted_col[s:e].mean(axis=0).astype(np.float32)
        cell_conf[i] = cluster_size

    # Merge neighboring fine-grid cells using a KD-tree on cell centers
    # Only if cell count is manageable (<500K), otherwise skip neighborhood merge
    from scipy.spatial import cKDTree

    if len(cell_pos) <= 500000:
        tree = cKDTree(cell_pos)
        pairs = tree.query_pairs(r=dedup_distance)

        parent = list(range(len(cell_pos)))
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        for i, j in pairs:
            union(i, j)

        clusters: dict[int, list[int]] = {}
        for idx in range(len(cell_pos)):
            root = find(idx)
            clusters.setdefault(root, []).append(idx)

        fused_pos_list = np.empty((len(clusters), 3), dtype=np.float32)
        fused_col_list = np.empty((len(clusters), 3), dtype=np.float32)
        confidence_list = np.empty(len(clusters), dtype=np.int32)
        for ci, (_root, members) in enumerate(clusters.items()):
            total_conf = cell_conf[members].sum()
            fused_pos_list[ci] = (cell_pos[members] * cell_conf[members, np.newaxis]).sum(axis=0) / total_conf
            fused_col_list[ci] = (cell_col[members] * cell_conf[members, np.newaxis]).sum(axis=0) / total_conf
            confidence_list[ci] = total_conf

        fused_positions = fused_pos_list
        fused_colors = fused_col_list
        confidence = confidence_list
    else:
        fused_positions = cell_pos
        fused_colors = cell_col
        confidence = cell_conf

    logger.info(
        "Fusion: %d input points → %d fused points (dedup_dist=%.4f)",
        n_total,
        fused_positions.shape[0],
        dedup_distance,
    )

    return fused_positions, fused_colors, confidence
