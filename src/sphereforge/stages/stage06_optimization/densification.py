"""ImprovedGS+ Edge-Aware Score (EAS) and densification decision logic.

Implements the Edge-Aware Score from the ImprovedGS+ paper for detecting
under-reconstructed regions in rendered images.  The EAS uses the Laplacian
of the rendered image to highlight edges that are not well represented by
the current set of Gaussians.  A per-pixel EAS map is produced that can
later be sampled at each Gaussian's screen position to decide whether
that Gaussian should spawn new children (densify).

This module also provides a fallback to the traditional gradient-accumulation
densification trigger used in the original 3DGS paper.
"""

from __future__ import annotations

import logging

import torch
import torch.nn.functional as F

logger = logging.getLogger("sphereforge.stage06.densification")

# ---------------------------------------------------------------------------
# Laplacian kernels (float32, on CPU — moved to device at call site)
# ---------------------------------------------------------------------------
_LAPLACIAN_KERNEL_2D = torch.tensor(
    [[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=torch.float32
).reshape(1, 1, 3, 3)


# ---------------------------------------------------------------------------
# T6.6 — Edge-Aware Score
# ---------------------------------------------------------------------------


def compute_eas(
    rendered_image: torch.Tensor,
    threshold: float = 0.01,
) -> torch.Tensor:
    """Compute the Edge-Aware Score (EAS) map from a rendered image.

    The EAS highlights pixels where the Laplacian of the rendered image is
    large, indicating under-reconstructed edges.  Pixels with EAS above
    *threshold* are candidates for densification.

    Steps:
        1. Convert the rendered image to grayscale (if RGB).
        2. Compute the absolute Laplacian of the grayscale image.
        3. Apply a small Gaussian blur to smooth noise in the Laplacian.
        4. Return a per-pixel EAS map of shape ``(H, W)``.

    The returned map is differentiable w.r.t. *rendered_image*, allowing
    gradient-based optimisation if desired.

    Args:
        rendered_image: Rendered image, shape ``(H, W)`` (grayscale) or
            ``(H, W, 3)`` / ``(3, H, W)`` (RGB).  If ``(3, H, W)`` the
            channels dimension is moved to the end automatically.
        threshold: Minimum EAS value to be considered a densification
            candidate.  Used only for logging; the full continuous map is
            returned so the caller can apply their own threshold.

    Returns:
        EAS map of shape ``(H, W)``.  Higher values indicate stronger
        edge signals (under-reconstructed regions).
    """
    # Normalise input to (H, W) grayscale tensor
    gray = _to_grayscale(rendered_image)  # (H, W)

    H, W = gray.shape
    device = gray.device
    dtype = gray.dtype

    # Prepare Laplacian kernel on the correct device and dtype
    lap_kernel = _LAPLACIAN_KERNEL_2D.to(device=device, dtype=dtype)

    # Apply Laplacian via conv2d — needs (1, 1, H, W) input
    gray_4d = gray.unsqueeze(0).unsqueeze(0)  # (1, 1, H, W)

    # Pad with reflect mode to keep output the same size
    lap_response = F.conv2d(
        gray_4d,
        lap_kernel,
        bias=None,
        stride=1,
        padding=1,
    )  # (1, 1, H, W)

    # Absolute Laplacian → edge strength
    eas_map = lap_response.squeeze(0).squeeze(0).abs()  # (H, W)

    # Smooth with a small Gaussian to reduce noise
    if H >= 5 and W >= 5:
        blur_kernel = _gaussian_kernel_1d(1.0, device=device, dtype=dtype)
        eas_map = _separable_blur(eas_map, blur_kernel)

    n_candidates = (eas_map > threshold).sum().item()
    logger.debug(
        "compute_eas: shape=(%d, %d), threshold=%.4f, candidates=%d, "
        "max=%.4f, mean=%.6f",
        H,
        W,
        threshold,
        n_candidates,
        eas_map.max().item(),
        eas_map.mean().item(),
    )

    return eas_map


def should_densify(
    eas_map: torch.Tensor,
    screen_positions: torch.Tensor,
    threshold: float = 0.01,
) -> torch.Tensor:
    """Determine which Gaussians should be densified based on EAS.

    Samples the EAS map at each Gaussian's 2-D screen position.  A Gaussian
    is marked for densification if its sampled EAS value exceeds *threshold*.

    Screen positions are expected in pixel coordinates ``(x, y)`` where
    ``(0, 0)`` is the top-left corner of the image.  Values are clamped to
    valid image bounds before sampling.

    Args:
        eas_map: Per-pixel Edge-Aware Score map, shape ``(H, W)``.
        screen_positions: 2-D screen positions of Gaussians, shape
            ``(N, 2)`` in ``(x, y)`` pixel coordinates.
        threshold: EAS value above which a Gaussian is a densification
            candidate.

    Returns:
        Boolean mask of shape ``(N,)``.  ``True`` means the Gaussian at
        that index should be densified.
    """
    N = screen_positions.shape[0]
    if N == 0:
        return torch.zeros(0, dtype=torch.bool, device=eas_map.device)

    H, W = eas_map.shape
    device = eas_map.device

    # Clamp positions to valid pixel range
    x = screen_positions[:, 0].clamp(0, W - 1)  # (N,)
    y = screen_positions[:, 1].clamp(0, H - 1)  # (N,)

    # Bilinear sampling using grid_sample
    # grid_sample expects normalised coordinates in [-1, 1]
    x_norm = (2.0 * x / max(W - 1, 1)) - 1.0
    y_norm = (2.0 * y / max(H - 1, 1)) - 1.0

    grid = torch.stack([x_norm, y_norm], dim=-1)  # (N, 1, 2)
    grid = grid.unsqueeze(1)  # (N, 1, 2) → (N, 1, 2) but grid_sample wants (1, 1, H, W) input and (N, 1, 2) grid

    # Reshape for grid_sample: input is (1, 1, H, W), grid is (N, 1, 2)
    input_4d = eas_map.unsqueeze(0).unsqueeze(0)  # (1, 1, H, W)

    # grid_sample expects grid shape (N, H_out, W_out, 2)
    # We want one sample per Gaussian, so H_out=1, W_out=1
    grid_4d = grid.reshape(1, N, 1, 2)  # (1, N, 1, 2)

    sampled = F.grid_sample(
        input_4d,
        grid_4d,
        mode="bilinear",
        padding_mode="zeros",
        align_corners=True,
    )  # (1, 1, N, 1)

    eas_values = sampled.reshape(N)  # (N,)

    mask = eas_values > threshold

    logger.debug(
        "should_densify: N=%d, densify=%d (%.1f%%), threshold=%.4f",
        N,
        mask.sum().item(),
        100.0 * mask.float().mean().item() if N > 0 else 0.0,
        threshold,
    )

    return mask


def compute_grad_accum(
    grad_accum: torch.Tensor,
    grad_threshold: float = 0.0002,
) -> torch.Tensor:
    """Traditional gradient-based densification trigger from 3DGS.

    In the original 3DGS paper, Gaussians whose accumulated positional
    gradient norm exceeds a threshold are candidates for densification
    (splitting or cloning).

    Args:
        grad_accum: Accumulated gradient norms for each Gaussian,
            shape ``(N,)``.  Typically ``sqrt(sum_of_grad_x^2 + grad_y^2)``
            per view, accumulated over many training steps.
        grad_threshold: Gradient norm above which a Gaussian is flagged
            for densification (default 0.0002 from 3DGS).

    Returns:
        Boolean mask of shape ``(N,)``.  ``True`` means the Gaussian
        should be densified.
    """
    mask = grad_accum > grad_threshold

    N = grad_accum.shape[0]
    logger.debug(
        "compute_grad_accum: N=%d, densify=%d (%.1f%%), threshold=%.6f",
        N,
        mask.sum().item(),
        100.0 * mask.float().mean().item() if N > 0 else 0.0,
        grad_threshold,
    )

    return mask


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _to_grayscale(image: torch.Tensor) -> torch.Tensor:
    """Convert an image tensor to grayscale.

    Accepts:
        - ``(H, W)`` — returned unchanged.
        - ``(H, W, 3)`` — RGB channels-last, converted with luminance weights.
        - ``(3, H, W)`` — RGB channels-first, transposed then converted.

    Args:
        image: Input image tensor.

    Returns:
        Grayscale image of shape ``(H, W)``.
    """
    if image.ndim == 2:
        return image

    if image.ndim == 3:
        C, H, W_or_c = image.shape

        # Channels-last: (H, W, 3)
        if image.shape[-1] == 3:
            # ITU-R BT.601 luminance weights
            weights = torch.tensor(
                [0.299, 0.587, 0.114],
                dtype=image.dtype,
                device=image.device,
            )
            return (image * weights).sum(dim=-1)

        # Channels-first: (3, H, W)
        if image.shape[0] == 3:
            weights = torch.tensor(
                [0.299, 0.587, 0.114],
                dtype=image.dtype,
                device=image.device,
            ).reshape(3, 1, 1)
            return (image * weights).sum(dim=0)

    raise ValueError(
        f"Cannot convert image of shape {image.shape} to grayscale. "
        "Expected (H, W), (H, W, 3), or (3, H, W)."
    )


def _gaussian_kernel_1d(
    sigma: float,
    device: torch.device | None = None,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    """Create a 1-D Gaussian kernel for separable blur.

    Args:
        sigma: Standard deviation of the Gaussian.
        device: Target device.
        dtype: Target dtype.

    Returns:
        1-D kernel of shape ``(k,)`` where ``k = 2 * ceil(3 * sigma) + 1``.
    """
    k = int(2 * torch.ceil(torch.tensor(3.0 * sigma)).item()) + 1
    x = torch.arange(k, device=device, dtype=dtype) - (k - 1) / 2.0
    kernel = torch.exp(-0.5 * (x / sigma) ** 2)
    kernel = kernel / kernel.sum()
    return kernel


def _separable_blur(
    image: torch.Tensor,
    kernel_1d: torch.Tensor,
) -> torch.Tensor:
    """Apply a separable Gaussian blur to a 2-D image.

    Args:
        image: 2-D image tensor ``(H, W)``.
        kernel_1d: 1-D Gaussian kernel ``(k,)``.

    Returns:
        Blurred image ``(H, W)``.
    """
    k = kernel_1d.shape[0]
    pad = k // 2

    # Horizontal pass: conv along width dimension
    img_4d = image.unsqueeze(0).unsqueeze(0)  # (1, 1, H, W)
    kh = kernel_1d.reshape(1, 1, 1, -1).to(device=image.device, dtype=image.dtype)
    blurred_h = F.conv2d(img_4d, kh, bias=None, stride=1, padding=(0, pad))

    # Vertical pass: conv along height dimension
    kv = kernel_1d.reshape(1, 1, -1, 1).to(device=image.device, dtype=image.dtype)
    blurred = F.conv2d(blurred_h, kv, bias=None, stride=1, padding=(pad, 0))

    return blurred.squeeze(0).squeeze(0)  # (H, W)