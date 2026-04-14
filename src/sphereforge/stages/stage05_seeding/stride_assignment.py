"""Per-pixel stride assignment based on depth confidence.

Assigns a denser stride (smaller number) to high-confidence pixels and a
sparser stride to low-confidence pixels, so that unreliable depth regions
contribute fewer Gaussians.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger("sphereforge.stage05.stride_assignment")


def assign_stride(
    confidence_map: np.ndarray,
    stride_high: int = 1,
    stride_low: int = 4,
    threshold: float = 0.5,
) -> np.ndarray:
    """Assign per-pixel stride based on depth confidence.

    Pixels with confidence >= *threshold* receive *stride_high* (dense
    seeding, typically 1).  Pixels below the threshold receive
    *stride_low* (sparse seeding, typically 4).

    Args:
        confidence_map: (H, W) float32 confidence map with values in
            [0, 1].  Higher is more confident.
        stride_high: Stride for high-confidence pixels (default 1 =
            every pixel).
        stride_low: Stride for low-confidence pixels (default 4 =
            every 4th pixel).
        threshold: Confidence threshold separating high from low.
            Default 0.5.

    Returns:
        (H, W) int32 array of per-pixel strides.
    """
    strides = np.full(confidence_map.shape, stride_low, dtype=np.int32)
    high_conf = confidence_map >= threshold
    strides[high_conf] = stride_high

    n_high = int(np.sum(high_conf))
    n_total = confidence_map.size
    logger.info(
        "Stride assignment: %d/%d (%.1f%%) pixels high confidence "
        "(stride=%d), rest stride=%d",
        n_high,
        n_total,
        100.0 * n_high / n_total if n_total > 0 else 0.0,
        stride_high,
        stride_low,
    )

    return strides
