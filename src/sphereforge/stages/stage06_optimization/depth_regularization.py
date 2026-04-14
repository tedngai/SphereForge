"""Depth regularization combining ErpGS and 360-GeoGS.

Provides depth regularization losses that align the rendered intersection-depth
(from 360-GeoGS) with the PanDA estimated depth, optionally weighted by
cos(latitude) following the ErpGS distortion-aware weighting scheme.

This module combines:
- **ErpGS** style latitude weighting (cos(latitude)) for ERP distortion.
- **360-GeoGS** depth and D-Normal regularization for geometric consistency.
"""

from __future__ import annotations

import logging

import torch

from sphereforge.stages.stage06_optimization.d_normal_loss import d_normal_loss

logger = logging.getLogger("sphereforge.stage06.depth_regularization")


def depth_reg_loss(
    rendered_depth: torch.Tensor,
    target_depth: torch.Tensor,
    latitudes: torch.Tensor | None = None,
    weight: float = 0.2,
) -> torch.Tensor:
    """Compute L1 depth regularization between rendered and target depth.

    Computes the L1 loss between the rendered intersection-depth and the
    PanDA target depth.  When *latitudes* is provided, the loss is weighted
    by ``cos(latitude)`` per pixel, following the ErpGS distortion-aware
    scheme that down-weights pixels near the poles.

    Args:
        rendered_depth: Rendered depth map (from intersection-depth or
            centre-depth), shape ``(H, W)``, positive values.
        target_depth: Target depth map (e.g. from PanDA), shape ``(H, W)``.
        latitudes: Per-pixel latitude in radians, shape ``(H, W)``.
            0 at equator, ±π/2 at poles.  If provided, the per-pixel loss
            is weighted by ``cos(latitude)``.  If ``None``, uniform weighting.
        weight: Scalar weight applied to the total loss (default 0.2).

    Returns:
        Scalar loss tensor (differentiable w.r.t. *rendered_depth*).

    Raises:
        ValueError: If shapes are incompatible.
    """
    if rendered_depth.shape != target_depth.shape:
        raise ValueError(
            f"Shape mismatch: rendered_depth {rendered_depth.shape} "
            f"vs target_depth {target_depth.shape}"
        )

    # Per-pixel L1 loss
    l1_per_pixel = (rendered_depth - target_depth).abs()  # (H, W)

    if latitudes is not None:
        if latitudes.shape != rendered_depth.shape:
            raise ValueError(
                f"Shape mismatch: latitudes {latitudes.shape} "
                f"vs rendered_depth {rendered_depth.shape}"
            )
        # ErpGS-style cosine weighting: 1 at equator, ~0 at poles
        weights = torch.cos(latitudes).clamp(min=0.0)  # (H, W)
        weighted_loss = (weights * l1_per_pixel).mean()
    else:
        weighted_loss = l1_per_pixel.mean()

    loss = weight * weighted_loss

    logger.debug(
        "depth_reg_loss: L1=%.6f, weight=%.4f, total=%.6f, "
        "latitudes_provided=%s",
        weighted_loss.item(),
        weight,
        loss.item(),
        latitudes is not None,
    )

    return loss


def combined_depth_normal_loss(
    rendered_depth: torch.Tensor,
    target_depth: torch.Tensor,
    gaussian_normals: torch.Tensor | None = None,
    latitudes: torch.Tensor | None = None,
    depth_weight: float = 0.2,
    normal_weight: float = 0.05,
) -> torch.Tensor:
    """Compute combined depth + D-Normal regularization loss.

    Weighted sum of:
        1. :func:`depth_reg_loss` — L1 depth alignment with optional
           latitude weighting.
        2. :func:`d_normal_loss` — D-Normal consistency loss from 360-GeoGS.

    Args:
        rendered_depth: Rendered depth map, shape ``(H, W)``, positive values.
        target_depth: Target depth map, shape ``(H, W)``.
        gaussian_normals: Optional external surface normal map,
            shape ``(H, W, 3)``.  Passed to :func:`d_normal_loss` as
            *surface_normals*.  If ``None``, the D-Normal loss reduces to
            a smoothness regularizer.
        latitudes: Per-pixel latitude in radians, shape ``(H, W)``.
            Used for ErpGS-style weighting in the depth loss.
        depth_weight: Weight for the depth regularization component
            (default 0.2).
        normal_weight: Weight for the D-Normal regularization component
            (default 0.05).

    Returns:
        Scalar loss tensor (differentiable w.r.t. *rendered_depth*).
    """
    # Depth regularization
    depth_loss = depth_reg_loss(
        rendered_depth=rendered_depth,
        target_depth=target_depth,
        latitudes=latitudes,
        weight=1.0,  # Apply weight externally to allow separate scaling
    )

    # D-Normal regularization
    dnorm_loss = d_normal_loss(
        rendered_depth=rendered_depth,
        surface_normals=gaussian_normals,
        depth_weight=1.0,  # Apply weight externally
    )

    loss = depth_weight * depth_loss + normal_weight * dnorm_loss

    logger.debug(
        "combined_depth_normal_loss: depth=%.6f * %.4f + normal=%.6f * %.4f "
        "= %.6f",
        depth_loss.item(),
        depth_weight,
        dnorm_loss.item(),
        normal_weight,
        loss.item(),
    )

    return loss
