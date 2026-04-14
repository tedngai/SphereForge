"""GS-Diff LPIPS thresholding for hallucination filtering.

Computes LPIPS perceptual distance between original and inpainted images
in sliding windows. Regions where the perceptual change exceeds the
threshold are flagged as hallucinations and excluded from training.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger("sphereforge.stage07.lpips_filter")

# Default sliding-window parameters
_DEFAULT_WINDOW_SIZE = 64
_DEFAULT_STRIDE = 32


def filter_hallucinations(
    original: np.ndarray,
    inpainted: np.ndarray,
    threshold: float = 0.4,
    window_size: int = _DEFAULT_WINDOW_SIZE,
    stride: int = _DEFAULT_STRIDE,
) -> np.ndarray:
    """Identify hallucinated regions by comparing original and inpainted images.

    Computes LPIPS between the original and inpainted images in a
    sliding-window fashion. Windows where the LPIPS distance exceeds the
    threshold are marked as hallucinated. The result is a per-pixel boolean
    mask indicating which pixels should be excluded from training.

    For windows that are smaller than ``window_size`` (at image borders),
    the comparison is done on the available region.

    Args:
        original: Original rendered image, shape (H, W, 3), float32 in
            [0, 1] or uint8 in [0, 255].
        inpainted: Inpainted image, same shape and range as *original*.
        threshold: LPIPS distance above which a window is considered
            hallucinated. Defaults to 0.4.
        window_size: Side length of the sliding window. Defaults to 64.
        stride: Step size for the sliding window. Defaults to 32.

    Returns:
        Boolean mask of shape (H, W). ``True`` = hallucinated pixel
        (should be excluded from training).
    """
    original = np.asarray(original, dtype=np.float32)
    inpainted = np.asarray(inpainted, dtype=np.float32)

    if original.shape != inpainted.shape:
        raise ValueError(
            f"Shape mismatch: original {original.shape} vs inpainted {inpainted.shape}"
        )

    if original.ndim == 2:
        # Add channel dim for grayscale
        original = original[:, :, None]
        inpainted = inpainted[:, :, None]

    if original.ndim != 3:
        raise ValueError(f"Expected 2-D or 3-D image, got shape {original.shape}")

    # Normalize to [0, 1] if uint8-scale
    if original.max() > 1.5:
        original = original / 255.0
    if inpainted.max() > 1.5:
        inpainted = inpainted / 255.0

    H, W, C = original.shape
    hallucination_mask = np.zeros((H, W), dtype=bool)

    # Try to use the full LPIPS metric; fall back to simple MSE-based
    # approximation if lpips is not installed.
    try:
        from sphereforge.common.metrics import compute_lpips

        use_lpips = True
    except ImportError:
        use_lpips = False
        logger.warning(
            "lpips package not available — falling back to MSE-based "
            "approximation for hallucination filtering"
        )

    # Sliding window comparison
    n_windows = 0
    n_flagged = 0

    for y in range(0, H, stride):
        for x in range(0, W, stride):
            y_end = min(y + window_size, H)
            x_end = min(x + window_size, W)

            orig_patch = original[y:y_end, x:x_end, :]
            inp_patch = inpainted[y:y_end, x:x_end, :]

            # Skip tiny patches
            if orig_patch.shape[0] < 8 or orig_patch.shape[1] < 8:
                continue

            n_windows += 1

            if use_lpips:
                try:
                    dist = compute_lpips(orig_patch, inp_patch)
                except Exception:
                    # Fallback to MSE if LPIPS fails on this patch
                    dist = float(np.mean((orig_patch - inp_patch) ** 2)) * 5.0
            else:
                # MSE-based proxy: scale up to approximate LPIPS range
                mse = float(np.mean((orig_patch - inp_patch) ** 2))
                dist = mse * 5.0  # rough scaling

            if dist > threshold:
                hallucination_mask[y:y_end, x:x_end] = True
                n_flagged += 1

    logger.info(
        "LPIPS filter: %d/%d windows flagged (threshold=%.2f)",
        n_flagged,
        n_windows,
        threshold,
    )

    n_flagged_px = int(np.sum(hallucination_mask))
    logger.debug(
        "Hallucinated pixels: %d / %d (%.2f%%)",
        n_flagged_px,
        H * W,
        100.0 * n_flagged_px / max(H * W, 1),
    )

    return hallucination_mask
