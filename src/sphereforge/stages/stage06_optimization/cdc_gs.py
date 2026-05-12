"""Complexity-Density Consistency for Gaussian Splatting (CDC-GS).

Implements the CDC-GS module that aligns Gaussian density to local visual
complexity. Regions with high visual complexity (fine texture, edges) should
have more Gaussians, while smooth regions need fewer. The complexity map is
computed via Discrete Wavelet Transform (DWT) and used to derive per-Gaussian
density weights that influence densification and pruning decisions.

This module is config-gated (``Stage06Config.cdc_gs_enabled``) and is optional.
It requires the ``pywt`` (PyWavelets) package.
"""

from __future__ import annotations

import logging

import numpy as np
import torch

logger = logging.getLogger("sphereforge.stage06.cdc_gs")


def compute_visual_complexity(
    image: np.ndarray,
    wavelet: str = "db2",
) -> np.ndarray:
    """Compute a visual complexity map using Discrete Wavelet Transform.

    Steps:
        1. Convert the image to grayscale.
        2. Apply 2D DWT using the specified wavelet.
        3. Sum absolute values of high-frequency subbands (LH, HL, HH).
        4. Upsample back to original resolution.

    Args:
        image: Input image, shape ``(H, W, 3)`` or ``(H, W)``, uint8 or
            float in [0, 1].
        wavelet: Wavelet name for PyWavelets (default ``"db2"``).

    Returns:
        Complexity map of shape ``(H, W)`` as float32.  Higher values
        indicate more visual complexity (edges, fine texture).

    Raises:
        ImportError: If ``pywt`` (PyWavelets) is not installed.
        ValueError: If the image has an unexpected shape.
    """
    try:
        import pywt
    except ImportError:
        raise ImportError(
            "PyWavelets is required for CDC-GS visual complexity computation. "
            "Install with: pip install PyWavelets"
        ) from None

    # Convert to grayscale if needed
    if image.ndim == 3:
        if image.shape[2] == 3:
            # ITU-R BT.601 luminance weights
            gray = (
                image[..., 0].astype(np.float64) * 0.299
                + image[..., 1].astype(np.float64) * 0.587
                + image[..., 2].astype(np.float64) * 0.114
            )
        else:
            raise ValueError(
                f"Expected image with 3 channels or grayscale, got shape {image.shape}"
            )
    elif image.ndim == 2:
        gray = image.astype(np.float64)
    else:
        raise ValueError(f"Expected 2D or 3D image, got shape {image.shape}")

    # Normalize to [0, 1] if uint8
    if gray.max() > 1.0:
        gray = gray / 255.0

    H, W = gray.shape

    # Apply 2D DWT
    coeffs = pywt.dwt2(gray, wavelet)
    _cA, (cH, cV, cD) = coeffs

    # Sum absolute values of high-frequency subbands
    # cH = LH (horizontal detail), cV = HL (vertical detail), cD = HH (diagonal)
    complexity = np.abs(cH) + np.abs(cV) + np.abs(cD)  # (H/2, W/2)

    # Upsample back to original resolution using bilinear interpolation
    # Use simple bilinear upsampling via numpy repeat + interpolation
    complexity_map = _bilinear_upsample(complexity, (H, W))

    # Normalize to [0, 1] range for numerical stability
    max_val = complexity_map.max()
    if max_val > 0:
        complexity_map = complexity_map / max_val

    complexity_map = complexity_map.astype(np.float32)

    logger.debug(
        "compute_visual_complexity: shape=(%d, %d), wavelet='%s', "
        "range=[%.4f, %.4f]",
        H,
        W,
        wavelet,
        complexity_map.min(),
        complexity_map.max(),
    )

    return complexity_map


def _bilinear_upsample(array: np.ndarray, target_shape: tuple[int, int]) -> np.ndarray:
    """Upsample a 2D array to target_shape using bilinear interpolation.

    Args:
        array: Input 2D array.
        target_shape: Target (H, W).

    Returns:
        Upsampled array of shape ``target_shape``.
    """
    h_in, w_in = array.shape
    h_out, w_out = target_shape

    # Create coordinate grids for the output
    y_out = np.linspace(0, h_in - 1, h_out)
    x_out = np.linspace(0, w_in - 1, w_out)

    x_grid, y_grid = np.meshgrid(x_out, y_out)

    # Bilinear interpolation
    x0 = np.floor(x_grid).astype(int)
    y0 = np.floor(y_grid).astype(int)
    x1 = np.minimum(x0 + 1, w_in - 1)
    y1 = np.minimum(y0 + 1, h_in - 1)

    fx = x_grid - x0
    fy = y_grid - y0

    result = (
        array[y0, x0] * (1 - fx) * (1 - fy)
        + array[y0, x1] * fx * (1 - fy)
        + array[y1, x0] * (1 - fx) * fy
        + array[y1, x1] * fx * fy
    )

    return result


def align_density_to_complexity(
    gaussian_positions: torch.Tensor,
    gaussian_scales: torch.Tensor,
    complexity_map: np.ndarray,
    image_shape: tuple[int, int],
) -> torch.Tensor:
    """Compute density weight for each Gaussian based on local complexity.

    Gaussians in high-complexity regions receive weight > 1 (encouraging
    densification), while those in low-complexity regions receive weight < 1
    (encouraging pruning or discouraging densification).

    The mapping from 3D Gaussian positions to 2D image coordinates uses a
    simple equirectangular projection (longitude from x/z, latitude from y).

    Args:
        gaussian_positions: Gaussian centre positions, shape ``(N, 3)``.
        gaussian_scales: Gaussian scales, shape ``(N, 3)`` (not directly
            used for weighting but included for API completeness).
        complexity_map: Visual complexity map from
            :func:`compute_visual_complexity`, shape ``(H, W)``.
        image_shape: Shape of the corresponding image ``(H, W)``.

    Returns:
        Density weights of shape ``(N,)``.  Values > 1 for high-complexity
        regions, < 1 for low-complexity regions, with mean ≈ 1.0.
    """
    N = gaussian_positions.shape[0]
    device = gaussian_positions.device
    dtype = gaussian_positions.dtype
    H, W = image_shape

    if N == 0:
        return torch.ones(0, device=device, dtype=dtype)

    # Project 3D positions to 2D equirectangular coordinates
    # longitude = atan2(x, z), latitude = arcsin(y / r)
    x = gaussian_positions[:, 0]
    y = gaussian_positions[:, 1]
    z = gaussian_positions[:, 2]

    r = torch.sqrt(x**2 + y**2 + z**2).clamp(min=1e-8)
    longitude = torch.atan2(x, z)  # [-pi, pi]
    latitude = torch.asin((y / r).clamp(-1.0, 1.0))  # [-pi/2, pi/2]

    # Map to pixel coordinates
    u = ((longitude + np.pi) / (2 * np.pi) * W).clamp(0, W - 1).long()  # (N,)
    v = ((latitude + np.pi / 2) / np.pi * H).clamp(0, H - 1).long()  # (N,)

    # Sample complexity at each Gaussian's projected position
    complexity_np = complexity_map
    complexity_at_gaussians = torch.from_numpy(
        complexity_np[v.cpu().numpy(), u.cpu().numpy()]
    ).to(device=device, dtype=dtype)

    # Compute density weights: center around 1.0
    # High complexity → weight > 1, low complexity → weight < 1
    mean_complexity = complexity_at_gaussians.mean().clamp(min=1e-8)
    density_weights = complexity_at_gaussians / mean_complexity

    # Clamp to reasonable range
    density_weights = density_weights.clamp(min=0.1, max=5.0)

    logger.debug(
        "align_density_to_complexity: N=%d, weight range=[%.4f, %.4f], mean=%.4f",
        N,
        density_weights.min().item(),
        density_weights.max().item(),
        density_weights.mean().item(),
    )

    return density_weights
