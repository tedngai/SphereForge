"""Depth confidence filtering via cross-validation.

Computes per-pixel confidence by comparing two depth estimates (e.g. PanDA
vs RPG360) using Normalized Cross-Correlation (NCC).  High NCC indicates
that both depth estimators agree, yielding high confidence.
"""

from __future__ import annotations

import logging

import numpy as np

from sphereforge.common.depth_utils import compute_ncc

logger = logging.getLogger("sphereforge.stage05.confidence_filter")


def compute_depth_confidence(
    depth_primary: np.ndarray,
    depth_secondary: np.ndarray,
    ncc_threshold: float = 0.5,
) -> np.ndarray:
    """Cross-validate two depth maps and return a per-pixel confidence map.

    Computes NCC between *depth_primary* and *depth_secondary* using
    :func:`sphereforge.common.depth_utils.compute_ncc`, then rescales
    NCC values from ``[-1, 1]`` to ``[0, 1]`` to produce a confidence
    map where 1 = most confident.

    Args:
        depth_primary: Primary depth map, shape (H, W).
        depth_secondary: Secondary depth map, shape (H, W).
        ncc_threshold: NCC threshold used only for logging.  The returned
            confidence map is continuous; thresholding is left to the
            caller (e.g. :func:`assign_stride`).

    Returns:
        Per-pixel confidence map of shape (H, W), dtype float32, with
        values in [0, 1].  Higher values indicate higher confidence.
    """
    ncc_map = compute_ncc(depth_primary, depth_secondary)  # (H, W), [-1, 1]

    # Rescale from [-1, 1] to [0, 1]
    confidence = (ncc_map.astype(np.float64) + 1.0) / 2.0
    confidence = np.clip(confidence, 0.0, 1.0).astype(np.float32)

    high_conf_ratio = float(np.mean(confidence >= (ncc_threshold + 1.0) / 2.0))
    logger.info(
        "Depth confidence: %.1f%% pixels above NCC threshold %.2f "
        "(confidence >= %.2f)",
        100.0 * high_conf_ratio,
        ncc_threshold,
        (ncc_threshold + 1.0) / 2.0,
    )

    return confidence
