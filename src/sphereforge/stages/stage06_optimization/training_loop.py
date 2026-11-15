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
from sphereforge.stages.stage06_optimization.erp_loss import (
    erp_weighted_loss,
    scale_flattening_loss,
)
from sphereforge.stages.stage06_optimization.pruning import (
    PruningBuffer,
    rap_prune,
)
from sphereforge.stages.stage06_optimization.split_clone import (
    clone_under_reconstructed,
    long_axis_split,
)

if TYPE_CHECKING:
    from sphereforge.config import Stage06Config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# gsplat availability check
# ---------------------------------------------------------------------------

_HAS_GSPLAT = False
try:
    from gsplat import rasterization as _gsplat_rasterization

    # Importing gsplat succeeds even when its CUDA kernels were never built;
    # the backend object is then None and rasterization fails deep inside the
    # call with an opaque AttributeError. Check it up front instead.
    from gsplat.cuda import _backend as _gsplat_backend

    if _gsplat_backend._C is None:
        logger.warning(
            "gsplat is installed but its CUDA extension is not built; "
            "render_gaussians() will use the stub. Build it with "
            "scripts/build_gsplat_cuda.bat (needs the CUDA toolkit and MSVC)."
        )
    else:
        _HAS_GSPLAT = True
        logger.debug("gsplat is available — using real rasterizer")
except ImportError:
    logger.debug("gsplat is NOT available — render_gaussians() will use random stub")


# ---------------------------------------------------------------------------
# Camera-intrinsics helper
# ---------------------------------------------------------------------------

# Opacity (post-sigmoid) that periodic opacity resets restore. This matches
# the 3DGS reference implementation: low enough to force every Gaussian to
# re-earn its contribution, high enough to survive the next prune pass.
_OPACITY_RESET_VALUE = 0.01


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
    K: Tensor | None = None,
    return_info: bool = False,
) -> tuple[Tensor, Tensor, Tensor] | tuple[Tensor, Tensor, Tensor, dict[str, Any]]:
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
        K: Optional 3x3 pinhole intrinsics matrix.  If provided, used directly.
        fov: Horizontal field of view in degrees.
        image_height: Rendered image height.
        image_width: Rendered image width.
        sh_degree: Spherical harmonics degree (0-3).  Passed to gsplat so it
            can evaluate SH internally.  Defaults to 0.
        return_info: Also return gsplat's ``info`` dict (``means2d``,
            ``gaussian_ids``, ``radii`` ...), needed for gradient-based
            densification.

    Returns:
        Tuple of (rendered_image, rendered_depth, rendered_alpha), plus the
        gsplat ``info`` dict as a fourth element when *return_info* is True.
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
            K=K,
            fov=fov,
            image_height=image_height,
            image_width=image_width,
            sh_degree=sh_degree,
            return_info=return_info,
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
    K: Tensor | None,
    fov: float,
    image_height: int,
    image_width: int,
    sh_degree: int = 0,
    return_info: bool = False,
) -> tuple[Tensor, Tensor, Tensor] | tuple[Tensor, Tensor, Tensor, dict[str, Any]]:
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

    if K is not None:
        Ks = K.to(device=device, dtype=torch.float32).unsqueeze(0)
    else:
        Ks = _fov_to_intrinsics_matrix(fov, image_height, image_width, device=device).unsqueeze(0)

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
            packed=True,
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
            packed=True,
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

    if return_info:
        return rendered_image, rendered_depth, rendered_alpha, info
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
        colors: Current SH coefficients (N, K, 3) in gsplat format.
        current_degree: Current SH degree (0-3).
        target_degree: Target SH degree (must be >= current_degree).

    Returns:
        Expanded SH coefficients (N, K_new, 3).
    """
    if target_degree <= current_degree:
        return colors

    n = colors.shape[0]
    new_k = (target_degree + 1) ** 2
    current_k = colors.shape[1]

    new_colors = torch.zeros(n, new_k, 3, device=colors.device, dtype=colors.dtype)
    new_colors[:, :current_k, :] = colors

    logger.debug(
        "Expanded SH from degree %d to %d: (%d,%d,%d) -> (%d,%d,%d)",
        current_degree,
        target_degree,
        n, current_k, 3,
        n, new_k, 3,
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
            width, target_image (3,H,W), target_depth (H,W), optional K,
            and latitudes (H,W).
        config: Stage06 configuration.
        device: "auto", "cuda", or "cpu".
        checkpoint_dir: Optional directory to save intermediate PLY checkpoints.

    Returns:
        Dict with final Gaussian attributes (same keys as initial_gaussians).
    """
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"

    # SH degree ramps every 2500 iterations, so degree d only becomes active at
    # iteration 2500*d. A run that ends shortly after that trains almost
    # entirely on diffuse colour, which caps PSNR far below what the scene
    # supports (measured: 8.96 dB at 3000 iterations vs 22.75 dB at 8000 on
    # identical inputs). Require at least half the run to use the target degree.
    _sh_ramp = 2500
    _sh_active_from = _sh_ramp * config.sh_degree
    if config.sh_degree > 0 and config.iterations - _sh_active_from < config.iterations // 2:
        logger.warning(
            "iterations=%d leaves only %d iterations at sh_degree=%d (it activates "
            "at %d); quality will be dominated by diffuse colour — consider >= %d",
            config.iterations,
            max(0, config.iterations - _sh_active_from),
            config.sh_degree,
            _sh_active_from,
            _sh_active_from * 2,
        )

    if not _HAS_GSPLAT:
        raise RuntimeError(
            "gsplat's CUDA rasterizer is unavailable — training requires a "
            "differentiable rasterizer. Install with: pip install "
            "'sphereforge[rasterizer]' (or manually: pip install gsplat>=1.0), "
            "then build the CUDA extension with scripts/build_gsplat_cuda.bat "
            "(needs the CUDA toolkit and Visual Studio Build Tools)."
        )

    # Move initial Gaussians to device
    positions = initial_gaussians["positions"].to(device).requires_grad_(True)
    colors = initial_gaussians["colors"].to(device)
    opacities = initial_gaussians["opacities"].to(device).requires_grad_(True)
    scales = initial_gaussians["scales"].to(device).requires_grad_(True)
    rotations = initial_gaussians["rotations"].to(device).requires_grad_(True)

    # Ensure colors are in gsplat-compatible shape (N, SH_K, 3)
    if colors.ndim == 2:
        colors = colors.unsqueeze(1)  # (N, 3) → (N, 1, 3)
    # gsplat interprets ``colors`` as spherical-harmonic coefficients, not RGB.
    # Stage 5 emits RGB in [0, 1], so convert the DC term to SH space; otherwise
    # the rasteriser evaluates SH_C0 * rgb + 0.5 and renders a flat grey scene.
    SH_C0 = 0.28209479177387814
    if colors.shape[1] == 1 and float(colors.max()) <= 1.5:
        colors = (colors - 0.5) / SH_C0
    colors = colors.clone().detach().requires_grad_(True)

    # Determine current SH degree from color dimension
    n_sh_coefs = colors.shape[1]  # K in (N, K, 3)
    current_sh_degree = int(np.sqrt(n_sh_coefs)) - 1 if n_sh_coefs >= 1 else 0

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
        K = view.get("K", None)
        if K is not None:
            gpu_view["K"] = K.to(device)
        latitudes = view.get("latitudes", None)
        if latitudes is not None:
            gpu_view["latitudes"] = latitudes.to(device)
        # Zero latitude everywhere = cos weight 1: plain (unweighted) L1 + SSIM
        # for pinhole views, through the same loss function.
        gpu_view["uniform_latitudes"] = torch.zeros(
            view["height"], view["width"], device=device
        )
        _gpu_views.append(gpu_view)

    # Gradient-based densification state (3DGS adaptive density control):
    # per-Gaussian sum of screen-space positional gradient norms and the number
    # of views in which the Gaussian was visible.
    scene_extent = _scene_extent(_gpu_views, positions.detach())
    grad_accum = torch.zeros(positions.shape[0], device=device)
    grad_count = torch.zeros(positions.shape[0], device=device)
    logger.info(
        "Densification: grad threshold %.2e, split above %.4f (percent_dense %.3f x "
        "scene extent %.3f), from iter %d to %d",
        config.densify_grad_threshold,
        config.densify_percent_dense * scene_extent,
        config.densify_percent_dense,
        scene_extent,
        config.densify_from_iter,
        config.densify_until_iter,
    )

    start_time = time.time()

    nan_skips = 0
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
            # Expand SH coefficients BEFORE rendering if schedule advanced
            if sh_degree_to_use > active_sh_degree:
                with torch.no_grad():
                    colors = expand_sh_degree(colors, active_sh_degree, sh_degree_to_use)
                    active_sh_degree = sh_degree_to_use
                    _update_optimizer(optimizer, positions, scales, rotations, opacities, colors)
                    logger.info(
                        "SH degree expanded from %d to %d at iteration %d",
                        current_sh_degree, active_sh_degree, iteration,
                    )
        else:
            sh_degree_to_use = active_sh_degree

        # Render using gsplat (or stub fallback)
        rendered_image, rendered_depth, _rendered_alpha, render_info = render_gaussians(
            means=positions,
            quats=rotations_norm,
            scales=scales_activated,
            opacities=opacities_activated,
            colors=colors,
            viewmat=viewmat,
            K=view.get("K", None),
            fov=view["fov"],
            image_height=view["height"],
            image_width=view["width"],
            sh_degree=sh_degree_to_use,
            return_info=True,
        )
        track_grads = iteration < config.densify_until_iter
        means2d = render_info.get("means2d") if track_grads else None
        if means2d is not None and means2d.requires_grad:
            means2d.retain_grad()

        # ---- Compute losses ----
        total_loss = torch.tensor(0.0, device=device)

        # 1. Photometric loss: L1 + SSIM. The ErpGS cos(latitude) weighting is
        # only applied to equirectangular views (which carry ``latitudes``);
        # pinhole rig views have no pole oversampling to correct.
        use_erp_weights = config.erp_distortion_weights and latitudes is not None
        photo_loss = erp_weighted_loss(
            rendered_image.permute(1, 2, 0),  # (H,W,3)
            target_image.permute(1, 2, 0),    # (H,W,3)
            latitudes if use_erp_weights else view["uniform_latitudes"],
            l1_weight=config.l1_weight,
            ssim_weight=config.ssim_weight,
        )
        total_loss = total_loss + photo_loss

        # 2. Scale + flattening loss (prevent oversized polar Gaussians). Its
        # latitude is measured from the world origin, which is only the
        # panorama centre for ERP training; skip it for pinhole rig views.
        if config.erp_scale_flattening_loss > 0 and use_erp_weights:
            pos_norms = torch.norm(positions, dim=1).clamp(min=1e-8)
            gaussian_latitudes = torch.asin(
                positions[:, 1] / pos_norms
            ).clamp(-math.pi / 2, math.pi / 2)
            sf_loss = scale_flattening_loss(
                scales=scales_activated,
                positions=positions,
                latitudes=gaussian_latitudes,
            )
            total_loss = total_loss + config.erp_scale_flattening_loss * sf_loss

        # 3. Depth regularization
        # Uncovered ERP pixels carry a depth of 0. Including them makes the
        # D-Normal term divide by zero (it differentiates depth to get normals),
        # which poisons the whole loss with NaN after a few hundred iterations.
        if config.depth_reg_weight > 0:
            # rendered_depth may carry a leading batch dimension; align it with
            # the target before building the validity mask.
            rendered_for_depth = rendered_depth
            while rendered_for_depth.dim() > target_depth.dim():
                rendered_for_depth = rendered_for_depth.squeeze(0)
            valid_depth = target_depth > 0
            if bool(valid_depth.any()):
                diff = torch.abs(rendered_for_depth - target_depth)
                if config.erp_distortion_weights and latitudes is not None:
                    cos_weights = torch.cos(latitudes)
                    while cos_weights.dim() < diff.dim():
                        cos_weights = cos_weights.unsqueeze(0)
                    weighted = diff * cos_weights
                    depth_loss = weighted[valid_depth].mean()
                else:
                    depth_loss = diff[valid_depth].mean()
                total_loss = total_loss + config.depth_reg_weight * depth_loss

        # 4. D-Normal loss
        if config.d_normal_weight > 0:
            dn_loss = d_normal_loss(rendered_depth, depth_weight=config.d_normal_weight)
            if torch.isfinite(dn_loss):
                total_loss = total_loss + config.d_normal_weight * dn_loss

        # ---- Backward pass ----
        optimizer.zero_grad()
        # A non-finite loss would otherwise propagate NaN into every parameter on
        # the first bad iteration and the run can never recover.
        if not torch.isfinite(total_loss):
            optimizer.zero_grad(set_to_none=True)
            nan_skips += 1
            if nan_skips <= 5 or nan_skips % 100 == 0:
                logger.warning(
                    "Iter %d: non-finite loss (%.4f); skipping update (%d total)",
                    iteration,
                    float(total_loss),
                    nan_skips,
                )
            continue

        total_loss.backward()
        if means2d is not None and means2d.grad is not None:
            _accumulate_screen_grads(
                render_info, means2d.grad, view["width"], view["height"], grad_accum, grad_count
            )
        optimizer.step()

        # ---- Densification ----
        # Standard 3DGS trigger: densify Gaussians whose screen-space positional
        # gradient, averaged over the views that saw them, is large (the
        # optimiser keeps wanting to move them, i.e. the region is
        # under-reconstructed). Small ones are cloned, large ones split along
        # their long axis (ImprovedGS+ LAS).
        if (
            config.densify_from_iter <= iteration < config.densify_until_iter
            and iteration % config.densify_every == 0
        ):
            with torch.no_grad():
                positions, scales, rotations, opacities, colors, n_clone, n_split = (
                    _densify_by_gradient(
                        positions, scales, rotations, opacities, colors,
                        grad_accum, grad_count,
                        grad_threshold=config.densify_grad_threshold,
                        split_scale=config.densify_percent_dense * scene_extent,
                        max_gaussians=config.max_gaussians,
                        iteration=iteration,
                    )
                )
                if n_clone or n_split:
                    _update_optimizer(
                        optimizer, positions, scales, rotations, opacities, colors,
                    )
                grad_accum = torch.zeros(positions.shape[0], device=positions.device)
                grad_count = torch.zeros(positions.shape[0], device=positions.device)
                n_gaussians = positions.shape[0]
                if positions.is_cuda:
                    torch.cuda.empty_cache()

        # ---- Pruning ----
        if iteration > 0 and iteration % config.prune_every == 0:
            with torch.no_grad():
                # Densification earlier in this iteration may have changed the
                # parameter count, so recompute activated tensors from the
                # current raw parameters before building the pruning mask.
                current_opacities_activated = torch.sigmoid(opacities)
                current_scales_activated = torch.exp(scales).clamp(max=10.0)

                # Compute PSNR for recovery check
                with torch.no_grad():
                    mse = ((rendered_image - target_image) ** 2).mean()
                    current_psnr = 10 * torch.log10(1.0 / (mse + 1e-8)).item()

                # Prune - get keep_mask from rap_prune (positions/scales/opacities returned are activated, ignore them)
                _, _, _, keep_mask = rap_prune(
                    positions, current_scales_activated, current_opacities_activated,
                    min_opacity=config.prune_min_opacity,
                    max_scale_ratio=config.prune_max_scale_ratio,
                )

                # Store pruned for potential recovery
                pruned_positions = positions[~keep_mask]
                if pruned_positions.shape[0] > 0:
                    pruning_buffer.store(
                        pruned_positions,
                        scales[~keep_mask],
                        rotations[~keep_mask],
                        opacities[~keep_mask],
                        colors[~keep_mask],
                        step=iteration,
                    )

                # Apply mask to all raw parameters
                positions = positions[keep_mask]
                scales = scales[keep_mask]
                rotations = rotations[keep_mask]
                opacities = opacities[keep_mask]
                colors = colors[keep_mask]
                grad_accum = grad_accum[keep_mask]
                grad_count = grad_count[keep_mask]

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
                    pad = torch.zeros(r_pos.shape[0], device=grad_accum.device)
                    grad_accum = torch.cat([grad_accum, pad])
                    grad_count = torch.cat([grad_count, pad])

                pruning_buffer.clear_old(iteration)
                _update_optimizer(optimizer, positions, scales, rotations, opacities, colors)
                if positions.is_cuda:
                    torch.cuda.empty_cache()

                prev_psnr = current_psnr
                n_gaussians = positions.shape[0]

        # ---- Opacity reset ----
        # Only reset while densification is still running. A reset lowers
        # opacity so densification can re-grow the scene; once densification
        # has stopped there is nothing to recover the loss, and the remaining
        # iterations just render a faint, under-opaque scene.
        if (
            config.opacity_reset_every > 0
            and iteration > 0
            and iteration % config.opacity_reset_every == 0
            and iteration < config.densify_until_iter
        ):
            with torch.no_grad():
                # Opacity reset is a *regulariser*, not a wipe: it nudges
                # over-confident Gaussians down so densification can reconsider
                # them. Clamping every Gaussian to a fixed low value destroys
                # the scene whenever densification has already stopped, because
                # nothing is left to grow back before the next prune pass.
                # Only lower opacities that are above the reset value, and never
                # below it.
                activated = torch.sigmoid(opacities)
                reset_value = _OPACITY_RESET_VALUE
                clamped = torch.clamp(activated, max=reset_value)
                reset_logit = torch.logit(clamped.clamp(1e-6, 1 - 1e-6))
                n_lowered = int((activated > reset_value).sum())
                opacities.copy_(reset_logit)
                if opacities.is_cuda:
                    torch.cuda.empty_cache()
                logger.info(
                    "Opacity reset at iteration %d: lowered %d/%d Gaussians to <= %.3f",
                    iteration,
                    n_lowered,
                    int(activated.numel()),
                    reset_value,
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

    # Drop any Gaussian whose parameters went non-finite. Densification can
    # occasionally produce a degenerate sample, and one NaN position propagates
    # into the scene extent used by every later prune step, which then discards
    # the whole scene. Removing them here keeps the output well-formed.
    with torch.no_grad():
        finite = torch.isfinite(positions).all(dim=1)
        for tensor in (colors, opacities, scales, rotations):
            finite &= torch.isfinite(tensor.reshape(tensor.shape[0], -1)).all(dim=1)
        n_bad = int((~finite).sum())
        if n_bad:
            logger.warning(
                "Dropping %d Gaussian(s) with non-finite parameters after training", n_bad
            )
            positions = positions[finite]
            colors = colors[finite]
            opacities = opacities[finite]
            scales = scales[finite]
            rotations = rotations[finite]
            n_gaussians = int(positions.shape[0])

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

    from sphereforge.common.io import sh_rest_from_coeffs, write_ply

    ckpt_path = checkpoint_dir / f"checkpoint_{iteration:06d}.ply"

    # Convert tensors to numpy for PLY writing; keep the higher SH bands.
    sh = colors.detach().cpu().numpy().astype(np.float32)
    if sh.ndim == 2:
        sh = sh[:, None, :]
    colors_np = sh[:, 0, :]

    write_ply(
        ckpt_path,
        positions=positions.detach().cpu().numpy(),
        colors=colors_np,
        # Checkpoints follow the 3DGS PLY convention (activated opacity/scale),
        # so they can be opened directly in a viewer.
        opacities=torch.sigmoid(opacities).detach().cpu().numpy(),
        scales=torch.exp(scales).detach().cpu().numpy(),
        rotations=rotations.detach().cpu().numpy(),
        sh_coeffs=sh_rest_from_coeffs(sh),
    )
    logger.info("Checkpoint saved: %s (%d Gaussians)", ckpt_path, positions.shape[0])


def _scene_extent(views: list[dict[str, Any]], positions: Tensor) -> float:
    """Scene radius used to tell "small" from "large" Gaussians when densifying.

    Matches 3DGS / gsplat: 1.1 x the largest distance of a camera centre from
    the mean camera centre. A single panorama (all rig views share one centre)
    has no camera baseline, so fall back to half the median Gaussian distance
    from the camera.

    Args:
        views: Training views with ``viewmat`` (world-to-camera 4x4).
        positions: Current Gaussian means ``(N, 3)``.

    Returns:
        Positive scene extent in world units.
    """
    centers = []
    for view in views:
        vm = view["viewmat"].detach().to(torch.float64).cpu()
        rot, trans = vm[:3, :3], vm[:3, 3]
        centers.append(-(rot.T @ trans))
    if not centers:
        return 1.0
    cams = torch.stack(centers)
    center = cams.mean(dim=0)
    radius = 1.1 * float((cams - center).norm(dim=1).max())
    if radius < 1e-3 and positions.numel():
        dists = (positions.detach().to(torch.float64).cpu() - center).norm(dim=1)
        radius = 0.5 * float(dists.median())
    return max(radius, 1e-6)


def _accumulate_screen_grads(
    info: dict[str, Any],
    means2d_grad: Tensor,
    width: int,
    height: int,
    grad_accum: Tensor,
    grad_count: Tensor,
) -> None:
    """Add one view's screen-space positional gradient norms to the running sums.

    Gradients are converted from gsplat's normalised units to pixels (x W/2,
    x H/2), as in gsplat's ``DefaultStrategy``, so the standard 3DGS threshold
    of 2e-4 applies.

    Args:
        info: gsplat ``info`` dict from the render (``gaussian_ids``/``radii``).
        means2d_grad: Gradient of ``info["means2d"]``.
        width: Rendered image width.
        height: Rendered image height.
        grad_accum: Per-Gaussian gradient-norm sum ``(N,)``, updated in place.
        grad_count: Per-Gaussian visibility count ``(N,)``, updated in place.
    """
    with torch.no_grad():
        grads = means2d_grad.detach().clone()
        grads[..., 0] *= width / 2.0
        grads[..., 1] *= height / 2.0
        ids = info.get("gaussian_ids")
        if ids is not None:  # packed: grads (nnz, 2)
            grads = grads.reshape(-1, 2)
        else:  # dense: grads (C, N, 2); keep only visible Gaussians
            radii = info["radii"]
            visible = radii > 0 if radii.dim() == 2 else (radii > 0).all(dim=-1)
            ids = torch.where(visible)[1]
            grads = grads[visible]
        ids = ids.long()
        grad_accum.index_add_(0, ids, grads.norm(dim=-1))
        grad_count.index_add_(0, ids, torch.ones_like(ids, dtype=grad_count.dtype))


def _densify_by_gradient(
    positions: Tensor,
    scales: Tensor,
    rotations: Tensor,
    opacities: Tensor,
    colors: Tensor,
    grad_accum: Tensor,
    grad_count: Tensor,
    *,
    grad_threshold: float,
    split_scale: float,
    max_gaussians: int,
    iteration: int,
) -> tuple[Tensor, Tensor, Tensor, Tensor, Tensor, int, int]:
    """Clone or split Gaussians whose average screen-space gradient is high.

    Operates on the *raw* optimiser parameters (log-scales, opacity logits)
    but runs :func:`clone_under_reconstructed` / :func:`long_axis_split` on
    activated values, which is what those helpers expect. (Passing log-scales
    straight in made splits offset children by a log value and *enlarge*
    them: halving a log-scale of -3.9 gives exp(-1.95), about 7x bigger.)

    Args:
        positions: Means ``(N, 3)``.
        scales: Log-scales ``(N, 3)``.
        rotations: Quaternions ``(N, 4)``.
        opacities: Opacity logits ``(N,)``.
        colors: SH coefficients ``(N, K, 3)``.
        grad_accum: Summed screen-space gradient norms ``(N,)``.
        grad_count: Visibility counts ``(N,)``.
        grad_threshold: Average-gradient trigger (3DGS default 2e-4).
        split_scale: Max activated scale above which a Gaussian is split
            rather than cloned.
        max_gaussians: Hard cap on the resulting count.
        iteration: Current iteration (for logging).

    Returns:
        ``(positions, scales, rotations, opacities, colors, n_clone, n_split)``
        with new leaf tensors (the inputs are returned unchanged when nothing
        is densified).
    """
    avg_grad = grad_accum / grad_count.clamp(min=1.0)
    candidates = avg_grad >= grad_threshold
    if not bool(candidates.any()):
        return positions, scales, rotations, opacities, colors, 0, 0

    act_scales = torch.exp(scales)
    is_small = act_scales.max(dim=1).values <= split_scale
    # Both a clone and a split add exactly one Gaussian.
    remaining = max(int(max_gaussians) - int(positions.shape[0]), 0)
    if remaining <= 0:
        logger.info(
            "Densification skipped at iter %d: Gaussian cap reached (%d)",
            iteration,
            max_gaussians,
        )
        return positions, scales, rotations, opacities, colors, 0, 0
    n_requested = int(candidates.sum())
    if n_requested > remaining:
        # Keep the Gaussians that most want to move.
        scores = torch.where(candidates, avg_grad, torch.full_like(avg_grad, -1.0))
        top = torch.topk(scores, remaining).indices
        limited = torch.zeros_like(candidates)
        limited[top] = True
        candidates = limited
        logger.info(
            "Densification capped at iter %d: requested +%d, allowing +%d (cap=%d)",
            iteration,
            n_requested,
            remaining,
            max_gaussians,
        )
    clone_mask = candidates & is_small
    split_mask = candidates & ~is_small
    n_clone = int(clone_mask.sum())
    n_split = int(split_mask.sum())

    act_opac = torch.sigmoid(opacities)
    pos, s_act, rot, o_act, col = positions, act_scales, rotations, act_opac, colors
    if n_clone:
        pos, s_act, rot, o_act, col = clone_under_reconstructed(
            pos, s_act, rot, o_act, col, clone_mask
        )
        # Clones are appended at the end and are not split this round.
        split_mask = torch.cat(
            [split_mask, torch.zeros(n_clone, dtype=torch.bool, device=split_mask.device)]
        )
    if n_split:
        pos, s_act, rot, o_act, col = long_axis_split(pos, s_act, rot, o_act, col, split_mask)

    new_scales = torch.log(s_act.clamp(min=1e-12))
    new_opac = torch.logit(o_act.clamp(1e-6, 1.0 - 1e-6))
    logger.info(
        "Densify iter %d: cloned %d, split %d (avg-grad >= %.1e) -> %d Gaussians",
        iteration,
        n_clone,
        n_split,
        grad_threshold,
        pos.shape[0],
    )
    return (
        pos.detach().clone(),
        new_scales.detach().clone(),
        rot.detach().clone(),
        new_opac.detach().clone(),
        col.detach().clone(),
        n_clone,
        n_split,
    )


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
    # Adam keys its state by tensor object. Replaced tensors would otherwise
    # keep their (now orphaned) moment buffers alive for the rest of the run.
    replacements = {
        "positions": positions,
        "opacities": opacities,
        "scales": scales,
        "rotations": rotations,
        "colors": colors,
    }
    for group in optimizer.param_groups:
        new_param = replacements.get(group.get("name", ""))
        for old_param in group["params"]:
            if new_param is not None and old_param is not new_param:
                optimizer.state.pop(old_param, None)

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

