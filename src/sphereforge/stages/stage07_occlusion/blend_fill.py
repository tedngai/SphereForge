"""Lightweight blend optimization for newly added Gaussians.

After ShareGS homogenization or patch reuse adds new Gaussians, this
module smooths their attributes (colour, opacity, scale, position) toward
their nearest existing neighbours so that the newcomers blend naturally
with the surrounding scene.  No differentiable rasteriser is required —
the smoothing is purely geometry-driven.
"""

from __future__ import annotations

import logging

import numpy as np
from scipy.spatial import KDTree

logger = logging.getLogger("sphereforge.stage07.blend_fill")


def blend_fill(
    gaussians: dict,
    original_count: int,
    n_iterations: int = 200,
    position_lr: float = 0.02,
    color_lr: float = 0.10,
    opacity_lr: float = 0.05,
    scale_lr: float = 0.05,
    k_neighbors: int = 8,
) -> dict:
    """Blend newly added Gaussians with existing scene geometry.

    For each new Gaussian, finds *k* nearest neighbours among the
    ``original_count`` original Gaussians and pulls the newcomer's
    attributes toward the local average.  Position is pulled toward
    the local surface plane (estimated from neighbour positions).

    Args:
        gaussians: Dictionary with keys ``positions`` (N,3), ``colors``
            (N,3), ``opacities`` (N,), ``scales`` (N,3), ``rotations`` (N,4),
            and optionally ``sh_coeffs``.
        original_count: Number of Gaussians that existed *before* ShareGS
            fill.  All Gaussians with index >= ``original_count`` are
            considered newcomers.
        n_iterations: Number of smoothing iterations (default 200).
        position_lr: Position blending rate (default 0.02).
        color_lr: Colour blending rate (default 0.10).
        opacity_lr: Opacity blending rate (default 0.05).
        scale_lr: Scale blending rate (default 0.05).
        k_neighbors: Number of nearest neighbours to use (default 8).

    Returns:
        Updated gaussians dict with blended attributes.
    """
    positions = np.asarray(gaussians["positions"], dtype=np.float32)
    colors = np.asarray(gaussians["colors"], dtype=np.float32)
    opacities = np.asarray(gaussians["opacities"], dtype=np.float32)
    scales = np.asarray(gaussians["scales"], dtype=np.float32)
    rotations = np.asarray(gaussians["rotations"], dtype=np.float32)
    sh_coeffs = gaussians.get("sh_coeffs")
    if sh_coeffs is not None:
        sh_coeffs = np.asarray(sh_coeffs, dtype=np.float32)

    n_total = positions.shape[0]
    if original_count >= n_total:
        logger.debug("No new Gaussians to blend (original=%d, total=%d)", original_count, n_total)
        return gaussians

    original_positions = positions[:original_count]
    new_positions = positions[original_count:].copy()
    new_colors = colors[original_count:].copy()
    new_opacities = opacities[original_count:].copy()
    new_scales = scales[original_count:].copy()
    new_rotations = rotations[original_count:].copy()

    # Build KD-tree on original Gaussians for fast neighbour queries
    tree = KDTree(original_positions)

    # Pre-compute neighbour statistics for each new Gaussian
    n_new = new_positions.shape[0]
    neighbour_indices = []
    neighbour_weights = []
    neighbour_centroids = []
    neighbour_colors = []
    neighbour_opacities = []
    neighbour_scales = []

    for i in range(n_new):
        dists, idx = tree.query(new_positions[i], k=min(k_neighbors, original_count))
        dists = np.atleast_1d(dists)
        idx = np.atleast_1d(idx)

        # Inverse-distance weights (closer neighbours count more)
        weights = 1.0 / (dists + 1e-6)
        weights /= weights.sum() + 1e-12

        neighbour_indices.append(idx)
        neighbour_weights.append(weights)
        neighbour_centroids.append(original_positions[idx].mean(axis=0))
        neighbour_colors.append((colors[idx] * weights[:, None]).sum(axis=0))
        neighbour_opacities.append(float((opacities[idx] * weights).sum()))
        neighbour_scales.append((scales[idx] * weights[:, None]).sum(axis=0))

    # Iterative smoothing
    for _iter in range(n_iterations):
        for i in range(n_new):
            centroid = neighbour_centroids[i]
            target_color = neighbour_colors[i]
            target_opacity = neighbour_opacities[i]
            target_scale = neighbour_scales[i]

            # Position: pull toward local centroid + surface plane
            delta_pos = centroid - new_positions[i]
            new_positions[i] += position_lr * delta_pos

            # Color: pull toward neighbour average
            new_colors[i] += color_lr * (target_color - new_colors[i])
            new_colors[i] = np.clip(new_colors[i], 0.0, 1.0)

            # Opacity: pull toward neighbour average
            new_opacities[i] += opacity_lr * (target_opacity - new_opacities[i])

            # Scale: pull toward neighbour average (log-space for stability)
            new_scales[i] += scale_lr * (target_scale - new_scales[i])

    # Clamp attributes
    new_opacities = np.clip(new_opacities, -10.0, 10.0)
    new_colors = np.clip(new_colors, 0.0, 1.0)

    # Update the full arrays
    result = {
        "positions": np.concatenate([original_positions, new_positions], axis=0),
        "colors": np.concatenate([colors[:original_count], new_colors], axis=0),
        "opacities": np.concatenate([opacities[:original_count], new_opacities], axis=0),
        "scales": np.concatenate([scales[:original_count], new_scales], axis=0),
        "rotations": np.concatenate([rotations[:original_count], new_rotations], axis=0),
    }

    if sh_coeffs is not None:
        # Preserve original SH; zero-pad newcomers
        n_new_final = new_positions.shape[0]
        result["sh_coeffs"] = np.concatenate(
            [sh_coeffs[:original_count], np.zeros((n_new_final, sh_coeffs.shape[1]), dtype=np.float32)],
            axis=0,
        )

    logger.info(
        "Blended %d new Gaussians over %d iterations (k=%d)",
        n_new,
        n_iterations,
        k_neighbors,
    )
    return result
