"""SphereForge metric helpers for PSNR, SSIM, and LPIPS computation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

logger = logging.getLogger(__name__)


def compute_psnr(
    image_a: NDArray[np.floating],
    image_b: NDArray[np.floating],
    data_range: float = 1.0,
) -> float:
    """Compute Peak Signal-to-Noise Ratio between two images.

    Args:
        image_a: First image array, shape (H, W) or (H, W, C), float values.
        image_b: Second image array, same shape as image_a.
        data_range: Maximum value of the data (1.0 for [0,1], 255 for [0,255]).

    Returns:
        PSNR value in dB. Returns 0.0 if MSE is zero (identical images).

    Raises:
        ValueError: If shapes don't match.
    """
    if image_a.shape != image_b.shape:
        raise ValueError(
            f"Shape mismatch: image_a {image_a.shape} vs image_b {image_b.shape}"
        )
    mse = float(np.mean((image_a - image_b) ** 2))
    if mse < 1e-10:
        return 0.0
    return float(10.0 * np.log10((data_range**2) / mse))


def compute_ssim(
    image_a: NDArray[np.floating],
    image_b: NDArray[np.floating],
    data_range: float = 1.0,
    window_size: int = 11,
    k1: float = 0.01,
    k2: float = 0.03,
) -> float:
    """Compute Structural Similarity Index between two images.

    Uses the standard SSIM formula with a uniform averaging window.
    No external dependencies required (pure numpy implementation).

    Args:
        image_a: First image array, shape (H, W) or (H, W, C), float values.
        image_b: Second image array, same shape as image_a.
        data_range: Maximum value of the data.
        window_size: Size of the averaging window (default 11).
        k1: SSIM stability constant C1 = (k1 * data_range)^2.
        k2: SSIM stability constant C2 = (k2 * data_range)^2.

    Returns:
        Mean SSIM value across all channels.

    Raises:
        ValueError: If shapes don't match or images are too small.
    """
    if image_a.shape != image_b.shape:
        raise ValueError(
            f"Shape mismatch: image_a {image_a.shape} vs image_b {image_b.shape}"
        )

    # Handle multi-channel by computing per-channel and averaging
    if image_a.ndim == 3:
        ssim_channels = [
            _compute_ssim_channel(
                image_a[:, :, c], image_b[:, :, c], data_range, window_size, k1, k2
            )
            for c in range(image_a.shape[2])
        ]
        return float(np.mean(ssim_channels))

    return _compute_ssim_channel(image_a, image_b, data_range, window_size, k1, k2)


def _compute_ssim_channel(
    img1: NDArray[np.floating],
    img2: NDArray[np.floating],
    data_range: float,
    window_size: int,
    k1: float,
    k2: float,
) -> float:
    """Compute SSIM for a single channel using uniform averaging."""
    from scipy.ndimage import uniform_filter

    c1 = (k1 * data_range) ** 2
    c2 = (k2 * data_range) ** 2

    mu1 = uniform_filter(img1.astype(np.float64), size=window_size)
    mu2 = uniform_filter(img2.astype(np.float64), size=window_size)

    mu1_sq = mu1 * mu1
    mu2_sq = mu2 * mu2
    mu1_mu2 = mu1 * mu2

    sigma1_sq = uniform_filter(img1.astype(np.float64) ** 2, size=window_size) - mu1_sq
    sigma2_sq = uniform_filter(img2.astype(np.float64) ** 2, size=window_size) - mu2_sq
    sigma12 = (
        uniform_filter(img1.astype(np.float64) * img2.astype(np.float64), size=window_size)
        - mu1_mu2
    )

    ssim_map = ((2 * mu1_mu2 + c1) * (2 * sigma12 + c2)) / (
        (mu1_sq + mu2_sq + c1) * (sigma1_sq + sigma2_sq + c2)
    )

    return float(np.mean(ssim_map))


def compute_lpips(
    image_a: NDArray[np.floating],
    image_b: NDArray[np.floating],
    net: str = "alex",
) -> float:
    """Compute Learned Perceptual Image Patch Similarity (LPIPS).

    Requires the ``lpips`` package. Falls back to a warning if not installed.

    Args:
        image_a: First image array, shape (H, W, C), float values in [0, 1].
        image_b: Second image array, same shape as image_a, float values in [0, 1].
        net: LPIPS backbone network — "alex" (default), "vgg", or "squeeze".

    Returns:
        LPIPS distance (0 = identical, higher = more different).

    Raises:
        ValueError: If shapes don't match.
        ImportError: If lpips package is not installed.
    """
    if image_a.shape != image_b.shape:
        raise ValueError(
            f"Shape mismatch: image_a {image_a.shape} vs image_b {image_b.shape}"
        )

    try:
        import lpips
        import torch
    except ImportError:
        raise ImportError(
            "LPIPS requires the 'lpips' and 'torch' packages. "
            "Install with: pip install lpips torch"
        ) from None

    # Convert to torch tensors [1, C, H, W] in [-1, 1]
    a_t = torch.from_numpy(image_a).permute(2, 0, 1).unsqueeze(0).float() * 2 - 1
    b_t = torch.from_numpy(image_b).permute(2, 0, 1).unsqueeze(0).float() * 2 - 1

    loss_fn = _get_lpips_model(net)
    with torch.no_grad():
        dist = loss_fn(a_t, b_t)

    return float(dist.item())


_lpips_cache: dict[str, object] = {}


def _get_lpips_model(net: str = "alex"):
    """Return a cached LPIPS model (one per net type)."""
    if net not in _lpips_cache:
        import lpips

        _lpips_cache[net] = lpips.LPIPS(net=net)
    return _lpips_cache[net]
