"""ImprovedGS+ RAP final pruning pass (Stage 8).

Applies Recovery-Aware Pruning to the refined Gaussians from Stage 7.
Uses the same PruningBuffer from Stage 6 for recovery tracking, but
operates on numpy arrays (the post-optimization representation) rather
than torch tensors.
"""

from __future__ import annotations

import logging

import numpy as np
import torch

from sphereforge.stages.stage06_optimization.pruning import PruningBuffer, rap_prune

logger = logging.getLogger("sphereforge.stage08.final_pruning")


def final_rap_prune(
    gaussians: dict,
    min_opacity: float = 0.005,
    max_scale_ratio: float = 10.0,
) -> tuple[dict, dict]:
    """Run RAP final pruning on refined Gaussians from Stage 7.

    Applies the ImprovedGS+ Recovery-Aware Pruning criteria in a final
    pass after occlusion recovery and refinement. Prunes Gaussians that
    are near-transparent (opacity below *min_opacity*) or excessively
    large (max scale exceeding scene_extent * max_scale_ratio).

    Uses the same ``rap_prune`` function from Stage 6, converting numpy
    arrays to torch tensors and back. A ``PruningBuffer`` is created for
    potential recovery tracking.

    Args:
        gaussians: Dictionary with keys ``positions`` (Nx3 float32),
            ``opacities`` (N float32), ``scales`` (Nx3 float32),
            ``rotations`` (Nx4 float32), ``colors`` (Nx3), and
            optionally ``sh_coeffs`` (Nx48 float32 or None).
        min_opacity: Minimum opacity threshold. Gaussians with opacity
            below this are pruned. Default 0.005.
        max_scale_ratio: Maximum ratio of a Gaussian's largest scale to
            the scene extent. Gaussians exceeding this are pruned.
            Default 10.0.

    Returns:
        Tuple of (pruned_gaussians, pruned_stats) where:

        - **pruned_gaussians** is a dict with the same keys as input,
          containing only the kept Gaussians.
        - **pruned_stats** is a dict with keys: ``n_before`` (int),
          ``n_after`` (int), ``n_pruned_opaque`` (int),
          ``n_pruned_scale`` (int).
    """
    positions = gaussians["positions"]
    opacities = gaussians["opacities"]
    scales = gaussians["scales"]
    rotations = gaussians["rotations"]
    colors = gaussians["colors"]
    sh_coeffs = gaussians.get("sh_coeffs")

    n_before = positions.shape[0]
    logger.info("Final RAP pruning: %d Gaussians, min_opacity=%.4f, max_scale_ratio=%.1f",
                n_before, min_opacity, max_scale_ratio)

    if n_before == 0:
        logger.warning("Final RAP pruning: no Gaussians to prune")
        empty_result = {k: np.array([], dtype=v.dtype).reshape(0, *v.shape[1:])
                        for k, v in gaussians.items() if v is not None}
        stats = {"n_before": 0, "n_after": 0, "n_pruned_opaque": 0, "n_pruned_scale": 0}
        return empty_result, stats

    # Convert numpy arrays to torch tensors for rap_prune
    pos_t = torch.from_numpy(positions.astype(np.float32))
    scales_t = torch.from_numpy(scales.astype(np.float32))
    opacities_t = torch.from_numpy(opacities.astype(np.float32))

    # Compute scene extent for scale pruning
    centroid = pos_t.mean(dim=0)
    dists = (pos_t - centroid).norm(dim=1)
    scene_extent = dists.max().clamp(min=1e-6).item()

    # Track opacity and scale masks separately for stats
    opacity_mask = opacities_t >= min_opacity
    max_scale_per_gaussian = scales_t.max(dim=1).values
    scale_mask = max_scale_per_gaussian <= (scene_extent * max_scale_ratio)

    n_pruned_opaque = int((~opacity_mask).sum().item())
    n_pruned_scale = int((~scale_mask).sum().item())

    # Run rap_prune
    _, _, _, keep_mask_t = rap_prune(
        positions=pos_t,
        scales=scales_t,
        opacities=opacities_t,
        min_opacity=min_opacity,
        max_scale_ratio=max_scale_ratio,
        scene_extent=scene_extent,
    )

    keep_mask = keep_mask_t.numpy()

    # Create a PruningBuffer for recovery tracking (stored for potential future use)
    _buffer = PruningBuffer(max_recovery_steps=1)
    if (~keep_mask).any():
        # Store pruned Gaussians in the buffer
        pruned_pos = pos_t[~keep_mask].clone()
        pruned_scales = scales_t[~keep_mask].clone()
        pruned_rot = torch.from_numpy(rotations[~keep_mask].astype(np.float32)).clone()
        pruned_op = opacities_t[~keep_mask].clone()
        if sh_coeffs is not None:
            pruned_sh = torch.from_numpy(sh_coeffs[~keep_mask].astype(np.float32)).clone()
        else:
            # Create zero SH coeffs for pruned Gaussians (they have no SH data)
            pruned_sh = torch.zeros(pruned_pos.shape[0], 0, dtype=torch.float32)
        _buffer.store(
            positions=pruned_pos,
            scales=pruned_scales,
            rotations=pruned_rot,
            opacities=pruned_op,
            sh_coeffs=pruned_sh,
            step=0,  # Final pass uses step 0
        )

    # Apply keep mask to all arrays
    n_after = int(keep_mask.sum())
    pruned_gaussians: dict = {
        "positions": positions[keep_mask],
        "opacities": opacities[keep_mask],
        "scales": scales[keep_mask],
        "rotations": rotations[keep_mask],
        "colors": colors[keep_mask],
    }
    if sh_coeffs is not None:
        pruned_gaussians["sh_coeffs"] = sh_coeffs[keep_mask]
    else:
        pruned_gaussians["sh_coeffs"] = None

    pruned_stats: dict = {
        "n_before": n_before,
        "n_after": n_after,
        "n_pruned_opaque": n_pruned_opaque,
        "n_pruned_scale": n_pruned_scale,
    }

    logger.info(
        "Final RAP pruning complete: %d → %d Gaussians "
        "(pruned: opacity=%d, scale=%d)",
        n_before, n_after, n_pruned_opaque, n_pruned_scale,
    )

    return pruned_gaussians, pruned_stats
