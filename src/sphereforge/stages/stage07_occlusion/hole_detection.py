"""Hole detection in rendered alpha maps.

Identifies regions where the Gaussian splat has insufficient coverage
(alpha below a threshold), producing a binary mask used to guide
occlusion-recovery inpainting.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger("sphereforge.stage07.hole_detection")


def detect_holes(rendered_alpha: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """Identify pixels where alpha is below the coverage threshold.

    Args:
        rendered_alpha: Rendered alpha map of shape (H, W) or (H, W, 1)
            with values in [0, 1]. Values below *threshold* indicate holes.
        threshold: Alpha value below which a pixel is considered a hole.
            Defaults to 0.5.

    Returns:
        Boolean mask of shape (H, W). ``True`` indicates a hole pixel.
    """
    rendered_alpha = np.asarray(rendered_alpha, dtype=np.float32)
    if rendered_alpha.ndim == 3 and rendered_alpha.shape[-1] == 1:
        rendered_alpha = rendered_alpha[:, :, 0]
    if rendered_alpha.ndim != 2:
        raise ValueError(
            f"rendered_alpha must be (H, W) or (H, W, 1), got shape {rendered_alpha.shape}"
        )

    hole_mask = rendered_alpha < threshold
    n_holes = int(np.sum(hole_mask))
    coverage = n_holes / hole_mask.size
    logger.debug(
        "Detected %d hole pixels (%.2f%% coverage) with threshold %.2f",
        n_holes,
        coverage * 100,
        threshold,
    )
    return hole_mask


def compute_hole_coverage(hole_mask: np.ndarray) -> float:
    """Compute the fraction of pixels that are holes.

    Args:
        hole_mask: Boolean mask of shape (H, W) where ``True`` = hole.

    Returns:
        Float in [0, 1] — percentage of pixels that are holes.
    """
    hole_mask = np.asarray(hole_mask, dtype=bool)
    if hole_mask.ndim != 2:
        raise ValueError(f"hole_mask must be 2-D, got shape {hole_mask.shape}")
    total = hole_mask.size
    if total == 0:
        return 0.0
    n_holes = int(np.sum(hole_mask))
    coverage = n_holes / total
    logger.debug("Hole coverage: %.4f (%d / %d pixels)", coverage, n_holes, total)
    return float(coverage)
