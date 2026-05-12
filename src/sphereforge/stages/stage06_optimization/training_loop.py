"""SphereForge Stage 6: Gaussian Splatting training loop.

Main optimization loop that combines ErpGS distortion-aware loss,
360-GeoGS depth/normal regularization, and ImprovedGS+ densification/pruning.

The differentiable rasterizer uses gsplat (Apache 2.0) when available,
falling back to a random-tensor stub when gsplat is not installed.

gsplat API reference (v1.x, verified 2025-01):
    from gsplat import rasterization
    render_colors, render_alphas, info = rasterization(
        means, quats, scales, opacities, colors,
        viewmats, Ks, width, height,
        sh_degree=..., render_mode="RGB+D", ...
    )

See: https://github.com/nerfstudio-project/gsplat
"""

from __future__ import annotations

import logging
import math
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import torch
from torch import Tensor
from torch.optim import Adam

from sphereforge.stages.stage06_optimization.d_normal_loss import (
    d_normal_loss,
)
from sphereforge.stages.stage06_optimization.densification import (
    clone_under_reconstructed,
    compute_eas,
    long_axis_split,
    should_densify,
)
from sphereforge.stages.stage06_optimization.erp_loss import (
    erp_weighted_loss,
    scale_flattening_loss,
)
from sphereforge.stages.stage06_optimization.pruning import (
    PruningBuffer,
    rap_prune,
)

if TYPE_CHECKING:
    from sphereforge.config import Stage06Config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# gsplat availability check
# ---------------------------------------------------------------------------

_HAS_GSPLAT = False
try:
    import gsplat  # noqa: F401 — import to check availability
    from gsplat import rasterization as _gsplat_rasterization

    _HAS_GSPLAT = True
    logger.debug("gsplat is available — using real rasterizer")
except ImportError:
    logger.debug("gsplat is NOT available — render_gaussians() will use random stub")


# ---------------------------------------------------------------------------
# Camera-intrinsics helper
# ---------------------------------------------------------------------------


def _fov_to_intrinsics_matrix(
    fov: float,
    image_height: int,
    image_width: int,
    device: torch.device | str = "cpu",
) -> Tensor:
    """Build a 3x3 pinhole camera intrinsics matrix from horizontal FOV.

    Assumes square pixels and principal point at the image centre.

    Args:
        fov: Horizontal field of view in degrees.
        image_height: Image height in pixels.
        image_width: Image width in pixels.
        device: Torch device.

    Returns:
        (3, 3) intrinsics matrix K with [fx, 0, cx; 0, fy, cy; 0, 0, 1].
    """
    fx = float(image_width) / (2.0 * math.tan(math.radians(fov / 2.0)))
    fy = fx  # square pixels
    cx = image_width / 2.0
    cy = image_height / 2.0
    K = torch.tensor(
        [[fx, 0.0, cx],
         [0.0, fy, cy],
         [0.0, 0.0, 1.0]],
        device=device,
        dtype=torch.float32,
    )
    return K


# ---------------------------------------------------------------------------
# Rasterizer
# ---------------------------------------------------------------------------


def render_gaussians(
    means: Tensor,          # (N, 3)
    quats: Tensor,          # (N, 4)
    scales: Tensor,         # (N, 3)
    opacities: Tensor,      # (N,)
    colors: Tensor,         # (N, K) — K=3 for SH degree 0, 48 for degree 3
    viewmat: Tensor,        # (4, 4) world-to-camera
    fov: float,
    image_height: int,
    image_width: int,
    sh_degree: int = 0,
) -> tuple[Tensor, Tensor, Tensor]:
    """Render Gaussians from a single camera view.

    When gsplat is installed, delegates to ``gsplat.rasterization()`` for
    high-performance CUDA-accelerated differentiable rendering.  When gsplat
    is not available, falls back to a random-tensor stub that matches the
    expected output shapes (useful for CPU-only testing / CI).

    gsplat version compatibility notes:
        - gsplat >= 1.0: ``rasterization()`` signature used here is stable.
        - gsplat < 1.0 (pre-release): the function accepted positional args
          only and used different parameter names.  If you are on a
          pre-1.0 gsplat, upgrade with ``pip install gsplat>=1.0``.
        - The ``render_mode="RGB+ED"`` (expected depth) is available in
          gsplat >= 1.0.  For older builds, fall back to ``"RGB+D"``
          (accumulated depth).

    Args:
        means: Gaussian positions (N, 3).
        quats: Gaussian rotations as quaternions (N, 4).  Must be normalized
            (unit quaternions) for gsplat.
        scales: Gaussian scales (N, 3).  Should already be activated
            (e.g. ``torch.exp(log_scales)``) — gsplat expects positive scales.
        opacities: Gaussian opacities (N,).  Should already be activated
            (e.g. ``torch.sigmoid(raw_opacities)``) — gsplat expects [0, 1].
        colors: SH color coefficients (N, K).  Layout matches 3DGS convention:
            K = (sh_degree+1)^2 * 3.  For degree 0, K=3 (DC only).
        viewmat: World-to-camera 4x4 matrix.
        fov: Horizontal field of view in degrees.
        image_height: Rendered image height.
        image_width: Rendered image width.
        sh_degree: Spherical harmonics degree (0-3).  Passed to gsplat so it
            can evaluate SH internally.  Defaults to 0.

    Returns:
        Tuple of (rendered_image, rendered_depth, rendered_alpha).
        - rendered_image: (3, H, W) float32 in [0, 1].
        - rendered_depth: (H, W) float32.
        - rendered_alpha: (H, W) float32 in [0, 1].
    """
    if _HAS_GSPLAT:
        return _render_gaussians_gsplat(
            means=means,
            quats=quats,
            scales=scales,
            opacities=opacities,
            colors=colors,
            viewmat=viewmat,
            fov=fov,
            image_height=image_height,
            image_width=image_width,
            sh_degree=sh_degree,
        )
    else:
        raise RuntimeError(
            "gsplat is not installed — rendering requires a differentiable rasterizer. "
            "Install with: pip install 'sphereforge[rasterizer]' "
            "(or manually: pip install gsplat>=1.0)"
        )


def _render_gaussians_gsplat(
    means: Tensor,
    quats: Tensor,
    scales: Tensor,
    opacities: Tensor,
    colors: Tensor,
    viewmat: Tensor,
    fov: float,
    image_height: int,
    image_width: int,
    sh_degree: int = 0,
) -> tuple[Tensor, Tensor, Tensor]:
    """Render Gaussians using gsplat's rasterization function.

    gsplat.rasterization() signature (v1.x):
        rasterization(
            means, quats, scales, opacities, colors,
            viewmats, Ks, width, height,
            near_plane=0.01, far_plane=1e10,
            sh_degree=None, packed=True, tile_size=16,
            render_mode="RGB",  # or "RGB+D", "RGB+ED", "D", "ED"
            sparse_grad=False, absgrad=False,
            rasterize_mode="classic",  # or "antialiased"
            ...
        ) -> (render_colors, render_alphas, info)

    Returns:
        (rendered_image, rendered_depth, rendered_alpha) with shapes
        (3, H, W), (H, W), (H, W).
    """
    device = means.device

    # gsplat expects viewmats as (C, 4, 4) — batch dimension even for single view
    viewmats = viewmat.unsqueeze(0).to(device)  # (1, 4, 4)

    # Build intrinsics matrix K from FOV
    Ks = _fov_to_intrinsics_matrix(fov, image_height, image_width, device=device)
    Ks = Ks.unsqueeze(0)  # (1, 3, 3)

    # Ensure quaternions are normalized (unit quaternions) — gsplat requirement
    quats_norm = quats / (quats.norm(dim=1, keepdim=True) + 1e-8)

    # Determine render mode — "RGB+ED" gives expected depth (better for loss)
    # Fall back to "RGB+D" for very old gsplat builds
    render_mode = "RGB+ED"
    try:
        render_colors, render_alphas, info = _gsplat_rasterization(
            means=means,
            quats=quats_norm,
            scales=scales,
            opacities=opacities,
            colors=colors,
            viewmats=viewmats,
            Ks=Ks,
            width=image_width,
            height=image_height,
            near_plane=0.01,
            far_plane=1e10,
            sh_degree=sh_degree,
            packed=False,
            render_mode=render_mode,
            sparse_grad=False,
            absgrad=False,
            rasterize_mode="classic",
        )
    except (TypeError, ValueError) as exc:
        # Fallback: if "RGB+ED" is not supported (very old gsplat), try "RGB+D"
        logger.warning(
            "gsplat render_mode='RGB+ED' failed (%s); falling back to 'RGB+D'",
            exc,
        )
        render_mode = "RGB+D"
        render_colors, render_alphas, info = _gsplat_rasterization(
            means=means,
            quats=quats_norm,
            scales=scales,
            opacities=opacities,
            colors=colors,
            viewmats=viewmats,
            Ks=Ks,
            width=image_width,
            height=image_height,
            near_plane=0.01,
            far_plane=1e10,
            sh_degree=sh_degree,
            packed=False,
            render_mode=render_mode,
            sparse_grad=False,
            absgrad=False,
            rasterize_mode="classic",
        )

    # Extract single-view results (gsplat always returns batched)
    # render_colors shape depends on render_mode:
    #   "RGB"     -> (C, H, W, 3)
    #   "RGB+ED"  -> (C, H, W, 4)  (3 color channels + 1 depth channel)
    #   "RGB+D"   -> (C, H, W, 4)  (3 color channels + 1 depth channel)
    # render_alphas -> (C, H, W, 1)
    rendered_image = render_colors[0, :, :, :3].permute(2, 0, 1)  # (3, H, W)
    rendered_alpha = render_alphas[0, :, :, 0]  # (H, W)

    if render_colors.shape[-1] > 3:
        # Depth channel is the last channel
        rendered_depth = render_colors[0, :, :, 3]  # (H, W)
    else:
        # No depth in output — derive from alpha-weighted z-buffer
        # This is a rough approximation; prefer render_mode with depth.
        if "depths" in info:
            rendered_depth = info["depths"][0]  # (H, W) or similar
        else:
            # Last resort: zeros
            rendered_depth = torch.zeros(
                image_height, image_width, device=device, dtype=torch.float32,
            )

    return rendered_image, rendered_depth, rendered_alpha


def _render_gaussians_stub(
    means: Tensor,
    image_height: int,
    image_width: int,
) -> tuple[Tensor, Tensor, Tensor]:
    """Fallback stub renderer that returns random tensors of the correct shape.

    Used when gsplat is not installed.  Not suitable for actual training —
    only for testing / CI where the rasterizer is not needed.

    Args:
        means: Gaussian positions (N, 3).  Used only to determine device.
        image_height: Rendered image height.
        image_width: Rendered image width.

    Returns:
        Tuple of (rendered_image, rendered_depth, rendered_alpha) with the
        same shapes as the real renderer.
    """
    device = means.device

    rendered_image = torch.rand(3, image_height, image_width, device=device) * 0.8 + 0.1
    rendered_depth = torch.rand(image_height, image_width, device=device) * 10.0 + 1.0
    rendered_alpha = torch.rand(image_height, image_width, device=device) * 0.5 + 0.5

    return rendered_image, rendered_depth, rendered_alpha


# ---------------------------------------------------------------------------
# SH expansion
# ---------------------------------------------------------------------------


def expand_sh_degree(colors: Tensor, current_degree: int, target_degree: int) -> Tensor:
    """Expand spherical harmonics from current_degree to target_degree.

    Degree 0 has 1 coefficient per channel (3 total per Gaussian).
    Degree 1 has 4 coefficients per channel (12 total).
    Degree 2 has 9 coefficients per channel (27 total).
    Degree 3 has 16 coefficients per channel (48 total).

    New coefficients are initialized to zero.

    Args:
        colors: Current SH coefficients (N, K).
        current_degree: Current SH degree (0-3).
        target_degree: Target SH degree (must be >= current_degree).

    Returns:
        Expanded SH coefficients (N, K_new).
    """
    if target_degree <= current_degree:
        return colors

    n = colors.shape[0]
    coeffs_per_channel = [1, 3, 5, 7]  # additional coeffs per degree
    total_per_channel = sum(coeffs_per_channel[: target_degree + 1])
    total_coeffs = total_per_channel * 3  # 3 channels (RGB)

    new_colors = torch.zeros(n, total_coeffs, device=colors.device, dtype=colors.dtype)
    new_colors[:, : colors.shape[1]] = colors

    logger.debug(
        "Expanded SH from degree %d to %d: %d -> %d coefficients",
        current_degree,
        target_degree,
        colors.shape[1],
        total_coeffs,
    )
    return new_colors


# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------


def train_gaussians(
    initial_gaussians: dict[str, Tensor],
    training_views: list[dict[str, Any]],
    config: Stage06Config,
    device: str = "auto",
    checkpoint_dir: Path | None = None,
) -> dict[str, Tensor]:
    """Train Gaussians via multi-view optimization.

    This is the main training loop that optimizes Gaussian positions, colors,
    opacities, scales, and rotations using photometric + geometric losses.

    When gsplat is installed, the rendering uses gsplat's CUDA-accelerated
    differentiable rasterizer.  Parameters are stored in gsplat's native
    format directly:
        - positions: raw (N, 3) — optimized directly
        - scales: log-scale (N, 3) — activated via ``torch.exp()`` before render
        - rotations: unnormalized quaternions (N, 4) — normalized before render
        - opacities: logit (N,) — activated via ``torch.sigmoid()`` before render
        - colors: SH coefficients (N, K) — passed directly to gsplat with
          ``sh_degree`` so gsplat evaluates view-dependent colors internally

    Args:
        initial_gaussians: Dict with keys: positions (N,3), colors (N,K),
            opacities (N,), scales (N,3), rotations (N,4).
        training_views: List of dicts, each with: viewmat (4,4), fov, height,
            width, target_image (3,H,W), target_depth (H,W), latitudes (H,W).
        config: Stage06 configuration.
        device: "auto", "cuda", or "cpu".
        checkpoint_dir: Optional directory to save intermediate PLY checkpoints.

    Returns:
        Dict with final Gaussian attributes (same keys as initial_gaussians).
    """
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"

    if not _HAS_GSPLAT:
        raise RuntimeError(
            "gsplat is not installed — training requires a differentiable rasterizer. "
            "Install with: pip install 'sphereforge[rasterizer]' "
            "(or manually: pip install gsplat>=1.0)"
        )

    # Move initial Gaussians to device
    positions = initial_gaussians["positions"].to(device).requires_grad_(True)
    colors = initial_gaussians["colors"].to(device).requires_grad_(True)
    opacities = initial_gaussians["opacities"].to(device).requires_grad_(True)
    scales = initial_gaussians["scales"].to(device).requires_grad_(True)
    rotations = initial_gaussians["rotations"].to(device).requires_grad_(True)

    # Determine current SH degree from color dimension
    n_sh_per_channel = colors.shape[1] // 3
    current_sh_degree = {1: 0, 4: 1, 9: 2, 16: 3}.get(n_sh_per_channel, 0)

    # Determine target SH degree from config
    target_sh_degree = config.sh_degree

    # Active SH degree (may increase during training)
    active_sh_degree = current_sh_degree

    # Set up optimizer with per-parameter learning rates
    # Learning rates match gsplat simple_trainer defaults and SphereForge pipeline spec
    optimizer = Adam(
        [
            {"params": [positions], "lr": 0.00016, "name": "positions"},
            {"params": [opacities], "lr": 0.05, "name": "opacities"},
            {"params": [scales], "lr": 0.005, "name": "scales"},
            {"params": [rotations], "lr": 0.001, "name": "rotations"},
            {"params": [colors], "lr": 0.0025, "name": "colors"},
        ],
    )

    # Pruning buffer for recovery-aware pruning
    pruning_buffer = PruningBuffer(max_recovery_steps=5)

    # Training state
    n_gaussians = positions.shape[0]
    prev_psnr = 0.0

    logger.info(
        "Starting training: %d Gaussians, %d iterations, %d views, device=%s, "
        "gsplat=%s, sh_degree=%d->%d",
        n_gaussians, config.iterations, len(training_views), device,
        _HAS_GSPLAT, current_sh_degree, target_sh_degree,
    )

    # Pre-load view tensors to GPU once to avoid redundant .to() calls per iter
    _gpu_views: list[dict[str, Any]] = []
    for view in training_views:
        gpu_view: dict[str, Any] = {
            "viewmat": view["viewmat"].to(device),
            "target_image": view["target_image"].to(device),
            "target_depth": view["target_depth"].to(device),
            "fov": view["fov"],
            "height": view["height"],
            "width": view["width"],
        }
        latitudes = view.get("latitudes", None)
        if latitudes is not None:
            gpu_view["latitudes"] = latitudes.to(device)
        _gpu_views.append(gpu_view)

    start_time = time.time()

    for iteration in range(config.iterations):
        # Pick a random training view
        view_idx = torch.randint(0, len(_gpu_views), (1,)).item()
        view = _gpu_views[view_idx]

        viewmat = view["viewmat"]
        target_image = view["target_image"]
        target_depth = view["target_depth"]
        latitudes = view.get("latitudes", None)

        # Normalize rotations (unit quaternions) — required by gsplat
        rotations_norm = rotations / (rotations.norm(dim=1, keepdim=True) + 1e-8)

        # Activate opacities (sigmoid) — gsplat expects [0, 1]
        opacities_activated = torch.sigmoid(opacities)

        # Activate scales (exp, clamped) — gsplat expects positive scales
        scales_activated = torch.exp(scales).clamp(max=10.0)

        # SH degree scheduling: gradually increase during early training
        # This matches common 3DGS practice and gsplat simple_trainer
        if active_sh_degree < target_sh_degree:
            # Ramp up SH degree every 2500 iterations (common schedule)
            sh_schedule_step = (iteration // 2500)
            sh_degree_to_use = min(sh_schedule_step, target_sh_degree)
            sh_degree_to_use = max(sh_degree_to_use, current_sh_degree)
        else:
            sh_degree_to_use = active_sh_degree

        # Render using gsplat (or stub fallback)
        rendered_image, rendered_depth, _rendered_alpha = render_gaussians(
            means=positions,
            quats=rotations_norm,
            scales=scales_activated,
            opacities=opacities_activated,
            colors=colors,
            viewmat=viewmat,
            fov=view["fov"],
            image_height=view["height"],
            image_width=view["width"],
            sh_degree=sh_degree_to_use,
        )

        # ---- Compute losses ----
        total_loss = torch.tensor(0.0, device=device)

        # 1. Photometric loss (L1 + SSIM, optionally ERP-weighted)
        if config.erp_distortion_weights and latitudes is not None:
            photo_loss = erp_weighted_loss(
                rendered_image.permute(1, 2, 0),  # (H,W,3)
                target_image.permute(1, 2, 0),    # (H,W,3)
                latitudes,
                l1_weight=config.l1_weight,
                ssim_weight=config.ssim_weight,
            )
        else:
            # Standard L1 + SSIM
            l1_loss = torch.abs(rendered_image - target_image).mean()
            total_loss = total_loss + config.l1_weight * l1_loss

        if config.erp_distortion_weights and latitudes is not None:
            total_loss = total_loss + photo_loss

        # 2. Scale + flattening loss (prevent oversized polar Gaussians)
        if config.erp_scale_flattening_loss > 0:
            sf_loss = scale_flattening_loss(
                scales=scales_activated,
                positions=positions,
                latitudes=latitudes,
            )
            total_loss = total_loss + config.erp_scale_flattening_loss * sf_loss

        # 3. Depth regularization
        if config.depth_reg_weight > 0:
            depth_loss = torch.abs(rendered_depth - target_depth).mean()
            if config.erp_distortion_weights and latitudes is not None:
                cos_weights = torch.cos(latitudes).unsqueeze(0)  # (1, H, W)
                depth_loss = (depth_loss.unsqueeze(0) * cos_weights).mean()
            total_loss = total_loss + config.depth_reg_weight * depth_loss

        # 4. D-Normal loss
        if config.d_normal_weight > 0:
            dn_loss = d_normal_loss(rendered_depth, depth_weight=config.d_normal_weight)
            total_loss = total_loss + config.d_normal_weight * dn_loss

        # ---- Backward pass ----
        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()

        # ---- Densification ----
        if iteration < config.densify_until_iter and iteration % config.densify_every == 0:
            with torch.no_grad():
                # Compute EAS from rendered image
                eas_map = compute_eas(rendered_image.detach())
                densify_mask = should_densify(
                    eas_map,
                    screen_positions=_get_screen_positions(
                        positions, viewmat, view["fov"],
                        view["height"], view["width"],
                    ),
                    threshold=0.01,
                )

                if densify_mask.any():
                    # Split large Gaussians along long axis
                    large_mask = (
                        (scales_activated.max(dim=1).values > scales_activated.mean())
                        & densify_mask
                    )
                    small_mask = densify_mask & ~large_mask

                    if large_mask.any():
                        positions, scales, rotations, opacities = long_axis_split(
                            positions, scales, rotations, opacities, large_mask,
                        )
                        # Re-create optimizer for new parameter sizes
                        _update_optimizer(
                            optimizer, positions, scales, rotations, opacities, colors,
                        )

                    if small_mask.any():
                        positions, opacities = clone_under_reconstructed(
                            positions, opacities, small_mask,
                        )
                        _update_optimizer(
                            optimizer, positions, scales, rotations, opacities, colors,
                        )

                n_gaussians = positions.shape[0]

        # ---- Pruning ----
        if iteration > 0 and iteration % config.prune_every == 0:
            with torch.no_grad():
                # Compute PSNR for recovery check
                with torch.no_grad():
                    mse = ((rendered_image - target_image) ** 2).mean()
                    current_psnr = 10 * torch.log10(1.0 / (mse + 1e-8)).item()

                # Prune
                kept_mask = rap_prune(
                    positions, scales_activated, opacities_activated,
                    min_opacity=0.005,
                )

                # Store pruned for potential recovery
                pruned_positions = positions[~kept_mask]
                if pruned_positions.shape[0] > 0:
                    pruning_buffer.store(
                        pruned_positions,
                        scales[~kept_mask],
                        rotations[~kept_mask],
                        opacities[~kept_mask],
                        colors[~kept_mask],
                        step=iteration,
                    )

                # Apply mask
                positions = positions[kept_mask]
                scales = scales[kept_mask]
                rotations = rotations[kept_mask]
                opacities = opacities[kept_mask]
                colors = colors[kept_mask]

                # Check recovery
                recovered = pruning_buffer.recover_if_needed(
                    current_psnr, prev_psnr, threshold=0.1,
                )
                if recovered is not None:
                    r_pos, r_scl, r_rot, r_opa, r_col = recovered
                    positions = torch.cat([positions, r_pos])
                    scales = torch.cat([scales, r_scl])
                    rotations = torch.cat([rotations, r_rot])
                    opacities = torch.cat([opacities, r_opa])
                    colors = torch.cat([colors, r_col])

                pruning_buffer.clear_old(iteration)
                _update_optimizer(optimizer, positions, scales, rotations, opacities, colors)

                prev_psnr = current_psnr
                n_gaussians = positions.shape[0]

        # ---- SH expansion ----
        # Expand SH coefficients when schedule reaches target degree
        if iteration == 7500 and active_sh_degree < target_sh_degree:
            with torch.no_grad():
                colors = expand_sh_degree(colors, active_sh_degree, target_sh_degree)
                active_sh_degree = target_sh_degree
                _update_optimizer(optimizer, positions, scales, rotations, opacities, colors)
                logger.info(
                    "SH degree expanded from %d to %d at iteration %d",
                    current_sh_degree, target_sh_degree, iteration,
                )

        # ---- Checkpointing ----
        if (
            checkpoint_dir is not None
            and config.checkpoint_every > 0
            and iteration > 0
            and iteration % config.checkpoint_every == 0
        ):
            _save_checkpoint(
                checkpoint_dir,
                iteration,
                positions,
                colors,
                opacities,
                scales,
                rotations,
            )

        # ---- Logging ----
        if iteration % 100 == 0:
            with torch.no_grad():
                mse = ((rendered_image - target_image) ** 2).mean()
                psnr = 10 * torch.log10(1.0 / (mse + 1e-8)).item()
            elapsed = time.time() - start_time
            logger.info(
                "Iter %d/%d | PSNR: %.2f | Gaussians: %d | Loss: %.4f | "
                "SH: %d | Time: %.1fs",
                iteration, config.iterations, psnr, n_gaussians, total_loss.item(),
                sh_degree_to_use, elapsed,
            )

    elapsed = time.time() - start_time
    logger.info(
        "Training complete: %d Gaussians, %.2fs, %.1f it/s",
        n_gaussians, elapsed, config.iterations / max(elapsed, 0.001),
    )

    return {
        "positions": positions.detach(),
        "colors": colors.detach(),
        "opacities": opacities.detach(),
        "scales": scales.detach(),
        "rotations": rotations.detach(),
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _save_checkpoint(
    checkpoint_dir: Path,
    iteration: int,
    positions: Tensor,
    colors: Tensor,
    opacities: Tensor,
    scales: Tensor,
    rotations: Tensor,
) -> None:
    """Save an intermediate PLY checkpoint during training.

    Args:
        checkpoint_dir: Directory for checkpoint files.
        iteration: Current training iteration.
        positions: Gaussian positions (N, 3).
        colors: SH coefficients (N, K).
        opacities: Opacities (N,).
        scales: Scales (N, 3).
        rotations: Rotations (N, 4).
    """
    checkpoint_dir = Path(checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    from sphereforge.common.io import write_ply

    ckpt_path = checkpoint_dir / f"checkpoint_{iteration:06d}.ply"

    # Convert tensors to numpy for PLY writing
    colors_np = colors.detach().cpu().numpy()
    if colors_np.max() > 1:
        colors_np = colors_np.astype(np.uint8)
    else:
        colors_np = (colors_np * 255).astype(np.uint8)

    write_ply(
        ckpt_path,
        positions=positions.detach().cpu().numpy(),
        colors=colors_np,
        opacities=opacities.detach().cpu().numpy(),
        scales=scales.detach().cpu().numpy(),
        rotations=rotations.detach().cpu().numpy(),
    )
    logger.info("Checkpoint saved: %s (%d Gaussians)", ckpt_path, positions.shape[0])


def _get_screen_positions(
    positions: Tensor, viewmat: Tensor, fov: float, height: int, width: int,
) -> Tensor:
    """Project 3D positions to 2D screen coordinates.

    Args:
        positions: (N, 3) world-space positions.
        viewmat: (4, 4) world-to-camera matrix.
        fov: Horizontal FOV in degrees.
        height: Image height.
        width: Image width.

    Returns:
        (N, 2) screen positions in pixel coordinates [0, W] x [0, H].
    """
    # Transform to camera space
    ones = torch.ones(positions.shape[0], 1, device=positions.device)
    homogenous = torch.cat([positions, ones], dim=1)  # (N, 4)
    cam_coords = (viewmat @ homogenous.T).T[:, :3]  # (N, 3)

    # Project to screen
    fx = width / (2 * math.tan(math.radians(fov / 2)))
    fy = fx  # Assume square pixels

    # Avoid division by zero
    z = cam_coords[:, 2].clamp(min=0.001)
    screen_x = (cam_coords[:, 0] * fx / z + width / 2).clamp(0, width - 1)
    screen_y = (cam_coords[:, 1] * fy / z + height / 2).clamp(0, height - 1)

    return torch.stack([screen_x, screen_y], dim=1)


def _update_optimizer(
    optimizer: Adam,
    positions: Tensor,
    scales: Tensor,
    rotations: Tensor,
    opacities: Tensor,
    colors: Tensor,
) -> None:
    """Update optimizer parameter groups after tensor size changes.

    When densification or pruning changes the number of Gaussians,
    the optimizer needs new parameter references.
    """
    # Find which param group each belongs to by name
    for group in optimizer.param_groups:
        name = group.get("name", "")
        if name == "positions" and positions is not None:
            group["params"] = [positions.requires_grad_(True)]
        elif name == "opacities" and opacities is not None:
            group["params"] = [opacities.requires_grad_(True)]
        elif name == "scales" and scales is not None:
            group["params"] = [scales.requires_grad_(True)]
        elif name == "rotations" and rotations is not None:
            group["params"] = [rotations.requires_grad_(True)]
        elif name == "colors" and colors is not None:
            group["params"] = [colors.requires_grad_(True)]
