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

    # Handle shape mismatch gracefully by resizing inpainted to match original
    if original.shape[:2] != inpainted.shape[:2]:
        logger.warning(
            "Shape mismatch: original %s vs inpainted %s — resizing inpainted",
            original.shape, inpainted.shape,
        )
        try:
            import cv2
            inpainted = cv2.resize(
                inpainted,
                (original.shape[1], original.shape[0]),
                interpolation=cv2.INTER_LINEAR,
            )
            if inpainted.ndim == 2:
                inpainted = inpainted[:, :, None]
        except Exception:
            # Fallback: return all-flagged mask (exclude from training)
            logger.error("Failed to resize inpainted image — flagging all pixels")
            return np.ones(original.shape[:2], dtype=bool)

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

    H, W, _C = original.shape
    hallucination_mask = np.zeros((H, W), dtype=bool)

    # Try to use the full LPIPS metric; fall back to simple MSE-based
    # approximation if lpips is not installed.
    try:
        import torch

        from sphereforge.common.metrics import _get_lpips_model

        lpips_fn = _get_lpips_model("alex")
        use_lpips = True
    except ImportError:
        use_lpips = False
        logger.warning(
            "lpips package not available — falling back to MSE-based "
            "approximation for hallucination filtering"
        )

    # Sliding window comparison — batch patches for LPIPS efficiency
    n_windows = 0
    n_flagged = 0

    if use_lpips:
        # Collect all patches first, then batch-evaluate
        patches_a = []
        patches_b = []
        coords = []

        for y in range(0, H, stride):
            for x in range(0, W, stride):
                y_end = min(y + window_size, H)
                x_end = min(x + window_size, W)
                if (y_end - y) < 8 or (x_end - x) < 8:
                    continue
                orig_patch = original[y:y_end, x:x_end, :]
                inp_patch = inpainted[y:y_end, x:x_end, :]
                # Pad to window_size for batching
                if orig_patch.shape[0] < window_size or orig_patch.shape[1] < window_size:
                    pad_a = np.zeros((window_size, window_size, _C), dtype=np.float32)
                    pad_b = np.zeros((window_size, window_size, _C), dtype=np.float32)
                    pad_a[: orig_patch.shape[0], : orig_patch.shape[1], :] = orig_patch
                    pad_b[: inp_patch.shape[0], : inp_patch.shape[1], :] = inp_patch
                    orig_patch = pad_a
                    inp_patch = pad_b
                a_t = torch.from_numpy(orig_patch).permute(2, 0, 1).float() * 2 - 1
                b_t = torch.from_numpy(inp_patch).permute(2, 0, 1).float() * 2 - 1
                patches_a.append(a_t)
                patches_b.append(b_t)
                coords.append((y, x, min(y + window_size, H), min(x + window_size, W)))
                n_windows += 1

        if patches_a:
            batch_size = 16
            with torch.no_grad():
                for i in range(0, len(patches_a), batch_size):
                    batch_a = torch.stack(patches_a[i : i + batch_size])
                    batch_b = torch.stack(patches_b[i : i + batch_size])
                    dists = lpips_fn(batch_a, batch_b)
                    for j, d_val in enumerate(dists):
                        idx = i + j
                        y0, x0, y1, x1 = coords[idx]
                        if float(d_val) > threshold:
                            hallucination_mask[y0:y1, x0:x1] = True
                            n_flagged += 1
    else:
        for y in range(0, H, stride):
            for x in range(0, W, stride):
                y_end = min(y + window_size, H)
                x_end = min(x + window_size, W)
                if (y_end - y) < 8 or (x_end - x) < 8:
                    continue
                orig_patch = original[y:y_end, x:x_end, :]
                inp_patch = inpainted[y:y_end, x:x_end, :]
                n_windows += 1
                mse = float(np.mean((orig_patch - inp_patch) ** 2))
                dist = mse * 5.0
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
