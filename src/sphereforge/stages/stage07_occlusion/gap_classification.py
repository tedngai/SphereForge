"""Gap classification for hole regions.

Categorises detected holes into semantic types based on depth
discontinuities and spatial location. This classification guides the
occlusion-recovery strategy (e.g., ShareGS homogenization vs. diffusion
inpainting).
"""

from __future__ import annotations

import logging

import numpy as np
from scipy.ndimage import binary_dilation, sobel

logger = logging.getLogger("sphereforge.stage07.gap_classification")

# Classification labels
NOT_HOLE = 0
BEHIND_FOREGROUND = 1  # depth discontinuity at boundary
AT_BOUNDARY = 2  # hole touches image edge
MISSING_GEOMETRY = 3  # surrounded by valid pixels


def classify_gaps(hole_mask: np.ndarray, depth_map: np.ndarray) -> np.ndarray:
    """Categorise holes by their relationship to scene geometry.

    Each hole pixel is assigned one of:
    - 0 (not_hole): pixel is not a hole.
    - 1 (behind_foreground): hole lies at a depth discontinuity — likely
      behind foreground geometry.
    - 2 (at_boundary): hole touches the image edge (likely an
      unobserved boundary region).
    - 3 (missing_geometry): hole is surrounded by valid pixels (true
      missing geometry that needs to be filled).

    The classification uses depth gradient magnitude to detect
    discontinuities near hole boundaries.

    Args:
        hole_mask: Boolean mask of shape (H, W). ``True`` = hole.
        depth_map: Float32 depth map of shape (H, W). Invalid/missing
            depth values should be 0 or NaN.

    Returns:
        Integer classification map of shape (H, W) with values in {0,1,2,3}.
    """
    hole_mask = np.asarray(hole_mask, dtype=bool)
    depth_map = np.asarray(depth_map, dtype=np.float32)

    if hole_mask.shape != depth_map.shape:
        raise ValueError(
            f"Shape mismatch: hole_mask {hole_mask.shape} vs depth_map {depth_map.shape}"
        )

    H, W = hole_mask.shape
    classification = np.zeros((H, W), dtype=np.int32)

    if not np.any(hole_mask):
        logger.debug("No holes detected — returning all-zero classification")
        return classification

    # --- 1. AT_BOUNDARY: holes that touch the image edge ---
    edge_mask = np.zeros_like(hole_mask)
    edge_mask[0, :] = True
    edge_mask[-1, :] = True
    edge_mask[:, 0] = True
    edge_mask[:, -1] = True

    # Dilate from the edge by a few pixels so holes near the edge count
    boundary_region = binary_dilation(edge_mask, iterations=3)
    at_boundary = hole_mask & boundary_region
    classification[at_boundary] = AT_BOUNDARY

    # --- 2. BEHIND_FOREGROUND: holes at depth discontinuities ---
    # Compute depth gradient magnitude
    valid_depth = np.isfinite(depth_map) & (depth_map > 0)
    depth_filled = np.where(valid_depth, depth_map, 0.0)

    gx = sobel(depth_filled, axis=1, mode="constant")
    gy = sobel(depth_filled, axis=0, mode="constant")
    grad_mag = np.sqrt(gx ** 2 + gy ** 2)

    # Threshold: high gradient = discontinuity
    grad_threshold = np.percentile(grad_mag[valid_depth], 90) if np.any(valid_depth) else 0.0
    discontinuity_map = grad_mag > grad_threshold

    # Dilate discontinuity map so holes *near* a discontinuity are caught
    disc_dilated = binary_dilation(discontinuity_map, iterations=5)
    behind_fg = hole_mask & disc_dilated & ~at_boundary
    classification[behind_fg] = BEHIND_FOREGROUND

    # --- 3. MISSING_GEOMETRY: remaining holes surrounded by valid pixels ---
    remaining = hole_mask & (classification == 0)
    # Verify remaining holes have valid neighbours
    valid_pixel = ~hole_mask
    valid_dilated = binary_dilation(valid_pixel, iterations=3)
    missing_geo = remaining & valid_dilated
    classification[missing_geo] = MISSING_GEOMETRY

    # Any remaining unclassified holes default to missing_geometry
    unclassified = hole_mask & (classification == 0)
    if np.any(unclassified):
        classification[unclassified] = MISSING_GEOMETRY
        logger.debug(
            "Reclassified %d unclassified holes as MISSING_GEOMETRY", int(np.sum(unclassified))
        )

    counts = {
        "not_hole": int(np.sum(classification == NOT_HOLE)),
        "behind_foreground": int(np.sum(classification == BEHIND_FOREGROUND)),
        "at_boundary": int(np.sum(classification == AT_BOUNDARY)),
        "missing_geometry": int(np.sum(classification == MISSING_GEOMETRY)),
    }
    logger.info("Gap classification: %s", counts)

    return classification
