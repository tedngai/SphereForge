"""Scene analysis for metric depth maps.

Computes scene-level statistics from a metric depth map including depth
range, sky/infinity threshold, orbit radius, and clipping planes. These
parameters are used downstream for Gaussian seeding, depth clipping, and
sky masking.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger("sphereforge.stage04.scene_analysis")


def analyze_depth_scene(depth_map: np.ndarray) -> dict:
    """Analyze a metric depth map and return scene parameters.

    Computes statistical summaries and derived parameters useful for
    downstream pipeline stages (seeding, sky masking, clipping).

    Args:
        depth_map: Metric depth map of shape (H, W) with dtype float32
            or float64. Values should be in metric units (metres).
            Zero or negative values are treated as invalid and excluded
            from percentile computations.

    Returns:
        Dictionary with the following keys:

        - **depth_range** (dict): ``min``, ``max``, ``p1`` (1st percentile),
          ``p99`` (99th percentile) computed from valid (positive) depth.
        - **sky_depth** (float): Depth value at the 95th percentile,
          typically corresponding to sky / far geometry.
        - **orbit_radius** (float): Median depth across the map,
          approximating the camera-to-scene distance.
        - **sky_mask** (np.ndarray): Boolean mask of shape (H, W) where
          ``True`` indicates pixels deeper than ``sky_depth``.
        - **near_clip** (float): 1st percentile depth (near clipping plane).
        - **far_clip** (float): 99th percentile depth (far clipping plane).

    Raises:
        ValueError: If ``depth_map`` is not 2D or contains no valid
            (positive) values.
    """
    if depth_map.ndim != 2:
        raise ValueError(
            f"depth_map must be 2D, got shape {depth_map.shape}"
        )

    # Filter to valid (positive) depth values
    valid_depth = depth_map[depth_map > 0].astype(np.float64)

    if valid_depth.size == 0:
        raise ValueError(
            "depth_map contains no valid (positive) depth values"
        )

    # Percentile computations
    d_min = float(np.min(valid_depth))
    d_max = float(np.max(valid_depth))
    p1 = float(np.percentile(valid_depth, 1))
    p99 = float(np.percentile(valid_depth, 99))
    p95 = float(np.percentile(valid_depth, 95))
    median = float(np.median(valid_depth))

    # Sky depth: 95th percentile (likely sky / infinity)
    sky_depth = p95

    # Sky mask: pixels deeper than sky_depth
    sky_mask = depth_map > sky_depth

    # Near / far clipping planes
    near_clip = p1
    far_clip = p99

    depth_range = {
        "min": d_min,
        "max": d_max,
        "p1": p1,
        "p99": p99,
    }

    logger.info(
        "Scene analysis: depth range [%.2f, %.2f], "
        "p1=%.2f, p99=%.2f, sky_depth=%.2f, orbit_radius=%.2f",
        d_min,
        d_max,
        p1,
        p99,
        sky_depth,
        median,
    )
    logger.info(
        "Sky mask: %.1f%% of pixels classified as sky",
        100.0 * float(np.mean(sky_mask)),
    )

    return {
        "depth_range": depth_range,
        "sky_depth": sky_depth,
        "orbit_radius": median,
        "sky_mask": sky_mask,
        "near_clip": near_clip,
        "far_clip": far_clip,
    }
