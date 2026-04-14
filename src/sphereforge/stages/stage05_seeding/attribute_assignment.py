"""Initial Gaussian attribute assignment.

Assigns opacity, scale, and rotation to each Gaussian based on its
confidence and depth.  High-confidence points get full opacity while
low-confidence points are reduced.  Scale is derived from the pixel
footprint at depth.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger("sphereforge.stage05.attribute_assignment")

# Confidence threshold for high/low classification
_CONFIDENCE_THRESHOLD = 0.5

# Approximate ERP pixel footprint factor: depth * factor = scale
# For ERP with ~90° vertical FOV over 512 pixels:
#   pixel_angular_size = (pi/2) / 512 ≈ 0.00307 rad
#   scale ≈ depth * pixel_angular_size ≈ depth * 0.003
# We use 0.002 as a slightly more conservative estimate.
_ERP_SCALE_FACTOR = 0.002


def assign_initial_attributes(
    positions: np.ndarray,
    colors: np.ndarray,
    confidence: np.ndarray,
    depth_map: np.ndarray,
) -> dict:
    """Assign initial Gaussian attributes: opacity, scale, rotation.

    Opacity is set to 1.0 for high-confidence points and 0.3 for
    low-confidence points.  Scale is computed as
    ``depth * 0.002`` (approximate ERP pixel footprint).  Rotation
    is the identity quaternion for all Gaussians.

    Args:
        positions: (N, 3) float32 Gaussian positions.
        colors: (N, 3) float32 or uint8 per-Gaussian colours.
        confidence: (N,) float32 confidence values.  Values >= 0.5
            are treated as high confidence; below 0.5 as low.
        depth_map: (N,) float32 per-point depth values (distance from
            camera / origin).  Can also be a 2-D (H, W) depth map —
            in that case per-point depth is approximated as the
            Euclidean norm of each position.

    Returns:
        Dictionary with keys:
            - **positions** (np.ndarray): (N, 3) float32.
            - **colors** (np.ndarray): (N, 3) float32.
            - **opacities** (np.ndarray): (N,) float32.
            - **scales** (np.ndarray): (N, 3) float32.
            - **rotations** (np.ndarray): (N, 4) float32.
    """
    n = positions.shape[0]

    if n == 0:
        return {
            "positions": np.empty((0, 3), dtype=np.float32),
            "colors": np.empty((0, 3), dtype=np.float32),
            "opacities": np.empty(0, dtype=np.float32),
            "scales": np.empty((0, 3), dtype=np.float32),
            "rotations": np.empty((0, 4), dtype=np.float32),
        }

    # --- Opacity ---
    conf = confidence.astype(np.float64).ravel()
    opacities = np.where(conf >= _CONFIDENCE_THRESHOLD, 1.0, 0.3).astype(np.float32)

    # --- Depth per point ---
    if depth_map.ndim == 1 and depth_map.shape[0] == n:
        per_point_depth = depth_map.astype(np.float64)
    else:
        # Approximate depth as distance from origin
        per_point_depth = np.linalg.norm(positions.astype(np.float64), axis=1)

    # --- Scale: isotropic, depth * ERP_SCALE_FACTOR ---
    scale_val = per_point_depth * _ERP_SCALE_FACTOR
    scale_val = np.maximum(scale_val, 1e-6)  # avoid zero scale
    scales = np.stack([scale_val, scale_val, scale_val], axis=-1).astype(np.float32)

    # --- Rotation: identity quaternion ---
    rotations = np.zeros((n, 4), dtype=np.float32)
    rotations[:, 0] = 1.0  # (1, 0, 0, 0)

    n_high = int(np.sum(conf >= _CONFIDENCE_THRESHOLD))
    logger.info(
        "Attribute assignment: %d points (%d high confidence, %d low), "
        "mean scale=%.6f",
        n,
        n_high,
        n - n_high,
        float(np.mean(scale_val)),
    )

    return {
        "positions": positions.astype(np.float32),
        "colors": colors.astype(np.float32),
        "opacities": opacities,
        "scales": scales,
        "rotations": rotations,
    }
