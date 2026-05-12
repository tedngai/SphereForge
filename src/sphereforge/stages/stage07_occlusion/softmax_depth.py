"""GS-Diff softmax-depth loss with Marigold depth prior.

Implements the depth-consistency loss used during GS-Diff distillation.
The loss uses softmax-weighted rendering weights (derived from a
monocular depth prior like Marigold) to produce a differentiable depth
alignment that is robust to outliers and scale ambiguity.
"""

from __future__ import annotations

import logging

import torch
import torch.nn.functional as F

logger = logging.getLogger("sphereforge.stage07.softmax_depth")


def softmax_depth_loss(
    rendered_depth: torch.Tensor,
    prior_depth: torch.Tensor,
    temperature: float = 0.1,
) -> torch.Tensor:
    """Compute depth loss using softmax-weighted rendering weights.

    Aligns the rendered Gaussian depth to a monocular depth prior
    (e.g., Marigold) using a softmax-weighted L1 loss. The softmax
    weighting comes from the rendering alpha weights and suppresses
    contributions from low-confidence regions.

    The prior depth is assumed to be in a normalised/relative scale.
    The loss first estimates a scale-and-shift alignment, then computes
    a weighted L1 residual.

    Args:
        rendered_depth: Rendered depth map of shape (H, W) or (1, 1, H, W),
            float32. Values should be positive (depth from camera).
        prior_depth: Monocular depth prior of the same shape,
            float32. May be in arbitrary scale (will be aligned).
        temperature: Softmax temperature for the weighting. Lower values
            produce sharper weighting (more peaked). Defaults to 0.1.

    Returns:
        Scalar loss tensor (0-dimensional).
    """
    # Ensure 4-D: (1, 1, H, W)
    if rendered_depth.ndim == 2:
        rendered_depth = rendered_depth[None, None, :, :]
    elif rendered_depth.ndim == 3:
        rendered_depth = rendered_depth[None, :, :, :]

    if prior_depth.ndim == 2:
        prior_depth = prior_depth[None, None, :, :]
    elif prior_depth.ndim == 3:
        prior_depth = prior_depth[None, :, :, :]

    # Match spatial dims
    if rendered_depth.shape[-2:] != prior_depth.shape[-2:]:
        prior_depth = F.interpolate(
            prior_depth,
            size=rendered_depth.shape[-2:],
            mode="bilinear",
            align_corners=False,
        )

    _H, _W = rendered_depth.shape[-2], rendered_depth.shape[-1]

    # Create validity masks (valid = finite and positive)
    valid_render = torch.isfinite(rendered_depth) & (rendered_depth > 0)
    valid_prior = torch.isfinite(prior_depth) & (prior_depth > 0)
    valid = valid_render & valid_prior

    if not torch.any(valid):
        logger.warning("No valid depth pixels for softmax-depth loss")
        return torch.tensor(0.0, device=rendered_depth.device, requires_grad=True)

    # Flatten for computation
    rd = rendered_depth[valid].squeeze()  # (V,)
    pd = prior_depth[valid].squeeze()  # (V,)

    if rd.numel() == 0:
        return torch.tensor(0.0, device=rendered_depth.device, requires_grad=True)

    # --- Scale-and-shift alignment ---
    # Solve: pd ≈ s * rd + t  via least-squares on valid pixels
    # Normalise both to zero-mean, unit-variance for stability
    rd_mean = rd.mean()
    pd_mean = pd.mean()
    rd_norm = rd - rd_mean
    pd_norm = pd - pd_mean

    rd_std = rd_norm.std() + 1e-8
    pd_std = pd_norm.std() + 1e-8

    scale = pd_std / rd_std
    shift = pd_mean - scale * rd_mean

    aligned_rendered = scale * rendered_depth + shift

    # --- Softmax-weighted L1 loss ---
    # Compute per-pixel L1 residual
    residual = torch.abs(aligned_rendered - prior_depth)

    # Mask invalid pixels
    residual = residual * valid.float()

    # Compute softmax weights from the rendered depth confidence.
    # Deeper pixels (farther) typically have lower rendering confidence.
    # We use the inverse of rendered depth as a proxy for confidence.
    confidence = 1.0 / (rendered_depth + 1e-6)
    confidence = confidence * valid.float()

    # Softmax over valid pixels
    flat_conf = confidence[valid].squeeze()
    weights = F.softmax(flat_conf / temperature, dim=0)

    # Weighted L1
    flat_residual = residual[valid].squeeze()
    loss = (weights * flat_residual).sum()

    logger.debug(
        "Softmax depth loss: %.6f (scale=%.4f, shift=%.4f, V=%d)",
        loss.item(),
        scale.item(),
        shift.item(),
        flat_residual.numel(),
    )

    return loss
