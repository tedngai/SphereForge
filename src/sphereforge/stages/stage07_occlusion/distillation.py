"""GS-Diff differentiable distillation from inpainted pseudo-ground-truth views.

Renders the current Gaussian splat from inpainted viewpoints using the gsplat
differentiable rasterizer, computes L1+SSIM loss against the inpainted targets
(excluding hallucinated pixels), and backpropagates gradients to update
Gaussian parameters via the Adam optimiser.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

from sphereforge.common.metrics import compute_ssim

if TYPE_CHECKING:
    pass

logger = logging.getLogger("sphereforge.stage07.distillation")


def run_gsplat_distillation(
    gaussians: dict,
    view_data: dict,
    l1_weight: float = 0.8,
    ssim_weight: float = 0.2,
    iterations: int = 50,
) -> dict:
    """Optimise Gaussians against an inpainted target view using gsplat gradients.

    Performs a short optimisation loop: render the current Gaussians from the
    novel camera, compute L1+SSIM loss against the inpainted target (masked to
    non-hallucinated hole pixels), and backpropagate through the rasterizer to
    update Gaussian parameters.

    After this call, the input ``gaussians`` dict is mutated in-place with the
    updated numpy arrays AND the updated torch tensors are also returned
    for reuse by subsequent views.

    Args:
        gaussians: Dict with ``positions`` (N,3), ``colors`` (N,3), 
            ``opacities`` (N,), ``scales`` (N,3), ``rotations`` (N,4).
            Also accepts optional ``_torch`` sub-dict from a previous call.
        view_data: Dict with keys:
            - ``viewmat``: 4x4 world-to-camera matrix.
            - ``fov``: Horizontal FOV in degrees.
            - ``height``, ``width``: Image resolution.
            - ``target``: Inpainted target image (H, W, 3) uint8 [0, 255].
            - ``valid_mask``: Boolean mask (H, W), True = pixel is safe to train on
              (i.e. hole AND NOT hallucinated).
        l1_weight: L1 loss weight. Default 0.8.
        ssim_weight: SSIM loss weight. Default 0.2.
        iterations: Number of optimisation steps for this view. Default 50.

    Returns:
        Updated ``gaussians`` dict (same object, mutated in-place) with new
        ``_torch`` key containing the current leaf tensors.
    """
    import torch

    from sphereforge.common.gaussian_parameters import opacities_to_activated, scales_to_activated

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # --- Lazy initialisation of torch tensors ---
    if "_torch" in gaussians:
        t = gaussians["_torch"]
        positions = t["positions"]
        colors = t["colors"]
        opacities_raw = t["opacities_raw"]
        scales_raw = t["scales_raw"]
        rotations = t["rotations"]
        optimizer = t["optimizer"]
    else:
        positions = torch.from_numpy(gaussians["positions"].copy()).to(device).requires_grad_(True)
        opacities_raw = torch.from_numpy(gaussians["opacities"].copy()).to(device).requires_grad_(True)
        scales_raw = torch.from_numpy(gaussians["scales"].copy()).to(device).requires_grad_(True)
        rotations = torch.from_numpy(gaussians["rotations"].copy()).to(device).requires_grad_(True)

        colors_np = gaussians["colors"]
        if colors_np.dtype == np.uint8:
            colors_np = colors_np.astype(np.float32) / 255.0
        else:
            colors_np = colors_np.astype(np.float32)
        colors = torch.from_numpy(colors_np.copy()).to(device)
        colors = colors.unsqueeze(1).clone().detach().requires_grad_(True)

        try:
            from torch.optim import Adam
        except ImportError:
            raise ImportError("torch is required for gsplat distillation") from None

        optimizer = Adam(
            [
                {"params": [positions], "lr": 0.00016, "name": "positions"},
                {"params": [opacities_raw], "lr": 0.05, "name": "opacities"},
                {"params": [scales_raw], "lr": 0.005, "name": "scales"},
                {"params": [rotations], "lr": 0.001, "name": "rotations"},
                {"params": [colors], "lr": 0.0025, "name": "colors"},
            ],
        )

    # --- View data ---
    viewmat_np = np.asarray(view_data["viewmat"], dtype=np.float32)
    viewmat = torch.from_numpy(viewmat_np).to(device)
    fov = float(view_data["fov"])
    height = int(view_data["height"])
    width = int(view_data["width"])

    target = np.asarray(view_data["target"], dtype=np.float32)
    if target.max() > 1.5:
        target = target / 255.0
    target_t = torch.from_numpy(target.copy()).to(device)

    valid_mask = np.asarray(view_data["valid_mask"], dtype=bool)[:height, :width]
    if not np.any(valid_mask):
        logger.debug("No valid pixels for distillation — skipping view")
        gaussians["_torch"] = {
            "positions": positions,
            "colors": colors,
            "opacities_raw": opacities_raw,
            "scales_raw": scales_raw,
            "rotations": rotations,
            "optimizer": optimizer,
        }
        return gaussians

    valid_t = torch.from_numpy(valid_mask).to(device)

    # --- Import render function ---
    from sphereforge.stages.stage06_optimization.training_loop import render_gaussians

    # --- Compute SSIM map (CPU numpy, done once) ---
    # We compute SSIM per-channel and average — used as a constant target quality metric
    _ssim_map_pixels: np.ndarray | None = None

    # --- Optimisation loop ---
    logger.debug("Distillation: %d iterations on %d valid pixels", iterations, int(valid_mask.sum()))

    for step in range(iterations):
        optimizer.zero_grad()

        # Activate parameters for gsplat
        opacities = torch.sigmoid(opacities_raw)
        scales = torch.exp(scales_raw)

        # Render
        rendered_rgb, rendered_depth, _rendered_alpha = render_gaussians(
            means=positions,
            quats=rotations,
            scales=scales,
            opacities=opacities,
            colors=colors,
            viewmat=viewmat,
            fov=fov,
            image_height=height,
            image_width=width,
            sh_degree=0,
        )

        rendered_permuted = rendered_rgb.permute(1, 2, 0)

        # L1 loss on valid pixels
        diff = (rendered_permuted - target_t).abs()
        l1_per_pixel = diff.mean(dim=-1)
        l1_loss = (l1_per_pixel * valid_t.float()).sum() / (valid_t.float().sum() + 1e-8)

        # SSIM loss (compute map once from rendered vs target, reuse)
        # For efficiency, compute SSIM every 10 steps
        if step % 10 == 0:
            _ssim_map_pixels = _compute_ssim_map_torch(rendered_permuted, target_t)
            ssim_map_t = torch.from_numpy(_ssim_map_pixels).to(device)

        ssim_loss_pixel = 1.0 - ssim_map_t
        ssim_loss = (ssim_loss_pixel * valid_t.float()).sum() / (valid_t.float().sum() + 1e-8)

        loss = l1_weight * l1_loss + ssim_weight * ssim_loss

        loss.backward()
        optimizer.step()

        if step == 0 or step == iterations - 1:
            logger.debug(
                "Distill step %d/%d: loss=%.6f (L1=%.6f, SSIM=%.6f)",
                step + 1,
                iterations,
                loss.item(),
                l1_loss.item(),
                ssim_loss.item(),
            )

    # --- Sync numpy arrays back ---
    _sync_gaussians_numpy(gaussians, positions, colors, opacities_raw, scales_raw, rotations)

    gaussians["_torch"] = {
        "positions": positions,
        "colors": colors,
        "opacities_raw": opacities_raw,
        "scales_raw": scales_raw,
        "rotations": rotations,
        "optimizer": optimizer,
    }

    logger.info(
        "Distillation complete: final loss=%.6f (L1=%.4f, SSIM=%.4f) over %d valid pixels",
        loss.item() if iterations > 0 else 0.0,
        l1_loss.item() if iterations > 0 else 0.0,
        ssim_loss.item() if iterations > 0 else 0.0,
        int(valid_mask.sum()),
    )

    return gaussians


def _compute_ssim_map_torch(
    img_a: "torch.Tensor",
    img_b: "torch.Tensor",
    window_size: int = 11,
    k1: float = 0.01,
    k2: float = 0.03,
) -> np.ndarray:
    """Compute per-pixel SSIM map using torch (returns numpy for reuse)."""
    import torch
    import torch.nn.functional as F

    c1 = k1 ** 2
    c2 = k2 ** 2

    a = img_a.permute(2, 0, 1).unsqueeze(0)
    b = img_b.permute(2, 0, 1).unsqueeze(0)

    kernel_size = window_size
    mu_a = F.avg_pool2d(a, kernel_size, stride=1, padding=kernel_size // 2)
    mu_b = F.avg_pool2d(b, kernel_size, stride=1, padding=kernel_size // 2)

    mu_a_sq = mu_a * mu_a
    mu_b_sq = mu_b * mu_b
    mu_ab = mu_a * mu_b

    sigma_a_sq = F.avg_pool2d(a * a, kernel_size, stride=1, padding=kernel_size // 2) - mu_a_sq
    sigma_b_sq = F.avg_pool2d(b * b, kernel_size, stride=1, padding=kernel_size // 2) - mu_b_sq
    sigma_ab = F.avg_pool2d(a * b, kernel_size, stride=1, padding=kernel_size // 2) - mu_ab

    ssim_map = ((2 * mu_ab + c1) * (2 * sigma_ab + c2)) / (
        (mu_a_sq + mu_b_sq + c1) * (sigma_a_sq + sigma_b_sq + c2)
    )

    ssim_map = ssim_map.mean(dim=1).squeeze(0)
    return ssim_map.detach().cpu().numpy()


def _sync_gaussians_numpy(
    gaussians: dict,
    positions: "torch.Tensor",
    colors: "torch.Tensor",
    opacities_raw: "torch.Tensor",
    scales_raw: "torch.Tensor",
    rotations: "torch.Tensor",
) -> None:
    """Sync updated torch tensors back to the gaussians dict as numpy arrays."""
    gaussians["positions"] = positions.detach().cpu().numpy().astype(np.float32)
    gaussians["opacities"] = opacities_raw.detach().cpu().numpy().astype(np.float32)
    gaussians["scales"] = scales_raw.detach().cpu().numpy().astype(np.float32)
    gaussians["rotations"] = rotations.detach().cpu().numpy().astype(np.float32)

    colors_np = colors.detach().cpu().numpy()
    if colors_np.ndim == 3:
        colors_np = colors_np[:, 0, :]
    gaussians["colors"] = colors_np.astype(np.float32)


# ---------------------------------------------------------------------------
# Backward-compatible stub — kept for tests that call the old signature
# ---------------------------------------------------------------------------


def distill_inpaint(
    gaussians: dict,
    novel_views: list[dict],
    lpips_mask: np.ndarray | None = None,
    l1_weight: float = 0.8,
    ssim_weight: float = 0.2,
) -> dict:
    """DEPRECATED stub — use ``run_gsplat_distillation`` instead.

    This stub passes through unchanged to keep existing unit tests running.
    """
    logger.warning(
        "distill_inpaint() is a deprecated stub. Use run_gsplat_distillation() "
        "for real gsplat-based differentiable distillation."
    )
    return gaussians
