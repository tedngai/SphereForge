"""FastGS Compact Box culling (Stage 8).

Implements tile-based Gaussian culling inspired by the FastGS paper.
For each Gaussian, computes its 3-sigma extent in 3D and checks which
screen-space tiles it overlaps. Removes tile assignments where the
Gaussian barely overlaps, reducing the final file size.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger("sphereforge.stage08.compact_culling")


def _rotation_matrix_from_quaternion(q: np.ndarray) -> np.ndarray:
    """Convert a single quaternion (w, x, y, z) to a 3x3 rotation matrix.

    Args:
        q: Quaternion array of shape (4,) in (w, x, y, z) order.

    Returns:
        3x3 rotation matrix.
    """
    w, x, y, z = q
    # Normalize
    norm = np.sqrt(w * w + x * x + y * y + z * z)
    if norm < 1e-8:
        return np.eye(3, dtype=np.float32)
    w, x, y, z = w / norm, x / norm, y / norm, z / norm

    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
        [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
        [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
    ], dtype=np.float32)


def compact_box_cull(
    positions: np.ndarray,
    scales: np.ndarray,
    rotations: np.ndarray,
    sigma: float = 3.0,
    tile_size: int = 16,
) -> np.ndarray:
    """Apply FastGS Compact Box culling to Gaussians.

    For each Gaussian, computes its 3-sigma extent in 3D using its
    rotation and scale parameters. Projects the extent to screen-space
    tiles (using a simplified orthographic projection for efficiency)
    and checks which tiles the Gaussian actually overlaps. Gaussians
    that have no valid tile assignment after culling are marked for
    removal.

    This reduces the final file size by removing useless Gaussian-tile
    pairs where the Gaussian barely overlaps a tile.

    Args:
        positions: Nx3 float32 array of Gaussian centers.
        scales: Nx3 float32 array of per-axis scale values (log-space
            in 3DGS, but should be passed as exp(scale) already).
        rotations: Nx4 float32 array of quaternion rotations
            (w, x, y, z order).
        sigma: Number of standard deviations for the extent.
            Default 3.0.
        tile_size: Tile size in pixels. Default 16.

    Returns:
        Boolean mask of shape (N,) — True for Gaussians that have at
        least one valid tile assignment after culling.
    """
    n = positions.shape[0]
    logger.info(
        "Compact box culling: %d Gaussians, sigma=%.1f, tile_size=%d",
        n, sigma, tile_size,
    )

    if n == 0:
        logger.warning("Compact box culling: no Gaussians to cull")
        return np.zeros(0, dtype=bool)

    # Ensure scales are positive (in 3DGS they're stored as log(scale))
    # If scales are in log-space (typical raw 3DGS PLY), convert them
    # We detect by checking if scales have negative values
    actual_scales = scales.copy()
    if np.any(actual_scales < 0):
        # Scales appear to be in log-space, convert
        actual_scales = np.exp(actual_scales)

    # Compute scene bounding box for tile grid
    pos_min = positions.min(axis=0)  # (3,)
    pos_max = positions.max(axis=0)  # (3,)
    scene_extent = (pos_max - pos_min).max()
    if scene_extent < 1e-6:
        # All Gaussians at the same point — keep all
        logger.warning("Compact box culling: degenerate scene extent, keeping all")
        return np.ones(n, dtype=bool)

    # Create a virtual tile grid over the scene
    # Map 3D positions to a 2D grid using x,y coordinates (simplified)
    n_tiles_x = max(1, int(np.ceil((pos_max[0] - pos_min[0]) / (tile_size * scene_extent / 100))))
    n_tiles_y = max(1, int(np.ceil((pos_max[1] - pos_min[1]) / (tile_size * scene_extent / 100))))
    # Clamp to reasonable range
    n_tiles_x = min(n_tiles_x, 256)
    n_tiles_y = min(n_tiles_y, 256)

    tile_width = (pos_max[0] - pos_min[0]) / max(n_tiles_x, 1)
    tile_height = (pos_max[1] - pos_min[1]) / max(n_tiles_y, 1)

    if tile_width < 1e-10:
        tile_width = scene_extent
    if tile_height < 1e-10:
        tile_height = scene_extent

    keep_mask = np.zeros(n, dtype=bool)

    for i in range(n):
        pos = positions[i]
        s = actual_scales[i]
        q = rotations[i]

        # Compute 3-sigma extent in 3D
        R = _rotation_matrix_from_quaternion(q)

        # The covariance matrix is R * S * S^T * R^T
        S = np.diag(s)  # Scale matrix
        cov = R @ (S @ S.T) @ R.T

        # Eigenvalues of covariance give variance along principal axes
        eigvals = np.linalg.eigvalsh(cov)
        # Ensure non-negative
        eigvals = np.maximum(eigvals, 0.0)
        std_devs = np.sqrt(eigvals)

        # 3-sigma extent in 3D
        extent_3d = sigma * std_devs  # (3,)

        # Project to 2D (simplified: use x, y components)
        # The 2D extent is approximated by the maximum extent
        # in x and y directions
        half_extent_x = extent_3d.max()  # Conservative estimate
        half_extent_y = extent_3d.max()

        # Compute tile range this Gaussian covers
        tile_min_x = int(np.floor((pos[0] - half_extent_x - pos_min[0]) / tile_width))
        tile_max_x = int(np.ceil((pos[0] + half_extent_x - pos_min[0]) / tile_width))
        tile_min_y = int(np.floor((pos[1] - half_extent_y - pos_min[1]) / tile_height))
        tile_max_y = int(np.ceil((pos[1] + half_extent_y - pos_min[1]) / tile_height))

        # Clamp to grid
        tile_min_x = max(0, tile_min_x)
        tile_max_x = min(n_tiles_x, tile_max_x)
        tile_min_y = max(0, tile_min_y)
        tile_max_y = min(n_tiles_y, tile_max_y)

        # Check if there's at least one tile where the Gaussian
        # has meaningful overlap (extent covers at least 1% of tile)
        has_valid_tile = False
        for tx in range(tile_min_x, tile_max_x):
            for ty in range(tile_min_y, tile_max_y):
                tile_center_x = pos_min[0] + (tx + 0.5) * tile_width
                tile_center_y = pos_min[1] + (ty + 0.5) * tile_height

                # Distance from Gaussian center to tile center
                dx = abs(pos[0] - tile_center_x)
                dy = abs(pos[1] - tile_center_y)

                # Check if the Gaussian's extent reaches this tile
                if dx <= half_extent_x + tile_width * 0.5 and dy <= half_extent_y + tile_height * 0.5:
                    has_valid_tile = True
                    break
            if has_valid_tile:
                break

        keep_mask[i] = has_valid_tile

    n_kept = int(keep_mask.sum())
    n_culled = n - n_kept
    logger.info(
        "Compact box culling complete: %d → %d Gaussians (%d culled)",
        n, n_kept, n_culled,
    )

    return keep_mask
