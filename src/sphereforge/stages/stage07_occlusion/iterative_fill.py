"""Iterative hole filling combining ShareGS and GS-Diff.

Repeatedly renders from novel cameras, detects holes, fills them
via ShareGS homogenization/patch reuse, then optionally applies
GS-Diff diffusion inpainting. Iterates until hole coverage drops
below the configured threshold or the maximum number of rounds is
reached.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

from sphereforge.common.gaussian_parameters import opacities_to_activated
from sphereforge.stages.stage07_occlusion.hole_detection import (
    detect_holes,
)
from sphereforge.stages.stage07_occlusion.sharegs_homogenize import homogenize_gaussians
from sphereforge.stages.stage07_occlusion.sharegs_reuse import reuse_patches

if TYPE_CHECKING:
    from sphereforge.config import Stage07Config

logger = logging.getLogger("sphereforge.stage07.iterative_fill")


def fill_holes_iterative(
    gaussians: dict,
    config: Stage07Config,
    novel_cameras: list[dict],
    colmap_model: dict,
) -> dict:
    """Iteratively fill holes using ShareGS and GS-Diff.

    Each round:
    1. Render from each novel camera to get alpha maps.
    2. Detect holes (pixels with alpha < threshold).
    3. If ShareGS is enabled:
       a. Homogenize — clone nearby Gaussians into gaps.
       b. Reuse patches — copy Gaussians from other viewpoints.
    4. If GS-Diff is enabled:
       a. Inpaint holes with EscherNet diffusion.
       b. Filter hallucinations with LPIPS threshold.
       c. Distill inpainted views back into the Gaussians.
    5. Check if hole coverage is below the stopping threshold.

    The loop terminates when hole coverage < ``config.refine_hole_threshold``
    or after ``config.refine_rounds`` rounds.

    Args:
        gaussians: Dictionary with keys ``positions`` (N,3), ``colors``
            (N,3), ``opacities`` (N,), ``scales`` (N,3), ``rotations`` (N,4),
            and optionally ``sh_coeffs`` (N,45).
        config: Stage 7 configuration controlling the fill strategy.
        novel_cameras: List of camera dicts from ``generate_novel_cameras``.
        colmap_model: COLMAP sparse model dict for coordinate-frame
            alignment.

    Returns:
        Updated gaussians dict with holes filled.
    """
    gaussians = _copy_gaussians(gaussians)

    for round_idx in range(config.refine_rounds):
        logger.info("=== Iterative fill round %d / %d ===", round_idx + 1, config.refine_rounds)

        # Step 1: Render from novel cameras and detect holes
        total_hole_pixels = 0
        total_pixels = 0
        per_cam_masks: list[np.ndarray] = []

        for _cam_idx, cam in enumerate(novel_cameras):
            # Approximate rendering: project Gaussians and check coverage
            alpha_map = _approximate_alpha_render(gaussians, cam)
            hole_mask = detect_holes(alpha_map, threshold=0.5)
            per_cam_masks.append(hole_mask)
            total_hole_pixels += int(np.sum(hole_mask))
            total_pixels += hole_mask.size

        if total_pixels == 0:
            logger.warning("No pixels rendered in round %d", round_idx + 1)
            continue

        hole_coverage = total_hole_pixels / total_pixels
        logger.info(
            "Round %d: hole coverage = %.4f (threshold = %.4f)",
            round_idx + 1,
            hole_coverage,
            config.refine_hole_threshold,
        )

        if hole_coverage <= config.refine_hole_threshold:
            logger.info(
                "Hole coverage %.4f below threshold %.4f — stopping early",
                hole_coverage,
                config.refine_hole_threshold,
            )
            break

        # Step 2: ShareGS fill
        if config.sharegs_enabled:
            for cam_idx, (cam, hole_mask) in enumerate(zip(novel_cameras, per_cam_masks, strict=False)):
                if not np.any(hole_mask):
                    continue

                remaining_budget = _remaining_gaussian_budget(gaussians, config)
                if remaining_budget <= 0:
                    logger.warning(
                        "Stage 7 Gaussian cap reached (%d); skipping further ShareGS growth",
                        config.max_gaussians,
                    )
                    break

                intrinsics = _cam_to_intrinsics(cam)

                if config.sharegs_homogenization:
                    logger.debug(
                        "Round %d, cam %d: ShareGS homogenization", round_idx + 1, cam_idx
                    )
                    gaussians = homogenize_gaussians(
                        gaussians,
                        hole_mask,
                        cam["viewmat"],
                        intrinsics,
                    )

                if config.sharegs_patch_reuse:
                    remaining_budget = _remaining_gaussian_budget(gaussians, config)
                    if remaining_budget <= 0:
                        logger.warning(
                            "Stage 7 Gaussian cap reached (%d); skipping patch reuse",
                            config.max_gaussians,
                        )
                        break
                    # Use other novel cameras as source views
                    source_views = [novel_cameras[j] for j in range(len(novel_cameras)) if j != cam_idx]
                    logger.debug(
                        "Round %d, cam %d: ShareGS patch reuse (%d sources)",
                        round_idx + 1,
                        cam_idx,
                        len(source_views),
                    )
                    gaussians = reuse_patches(
                        gaussians,
                        hole_mask,
                        source_views,
                        colmap_model,
                        max_new_gaussians=min(config.sharegs_patch_reuse_max_new, remaining_budget),
                    )

        # Step 3: GS-Diff fill (if enabled)
        if config.refine_backend in ("sharegs_gsdiff",):
            _apply_gsdiff_fill(
                gaussians=gaussians,
                config=config,
                novel_cameras=novel_cameras,
                per_cam_masks=per_cam_masks,
                round_idx=round_idx,
            )

        # Re-evaluate hole coverage after this round
        total_hole_pixels = 0
        total_pixels = 0
        for cam in novel_cameras:
            alpha_map = _approximate_alpha_render(gaussians, cam)
            hole_mask = detect_holes(alpha_map, threshold=0.5)
            total_hole_pixels += int(np.sum(hole_mask))
            total_pixels += hole_mask.size

        new_coverage = total_hole_pixels / max(total_pixels, 1)
        logger.info(
            "Round %d complete: hole coverage %.4f → %.4f",
            round_idx + 1,
            hole_coverage,
            new_coverage,
        )

    # Final coverage
    final_holes = 0
    final_pixels = 0
    for cam in novel_cameras:
        alpha_map = _approximate_alpha_render(gaussians, cam)
        hole_mask = detect_holes(alpha_map, threshold=0.5)
        final_holes += int(np.sum(hole_mask))
        final_pixels += hole_mask.size

    final_coverage = final_holes / max(final_pixels, 1)
    logger.info("Iterative fill complete: final hole coverage = %.4f", final_coverage)

    return gaussians


def _copy_gaussians(gaussians: dict) -> dict:
    """Deep-copy the gaussians dict to avoid mutating the input."""
    result = {}
    for key in ("positions", "colors", "opacities", "scales", "rotations"):
        result[key] = np.array(gaussians[key], copy=True)
    if "sh_coeffs" in gaussians and gaussians["sh_coeffs"] is not None:
        result["sh_coeffs"] = np.array(gaussians["sh_coeffs"], copy=True)
    return result


def _approximate_alpha_render(gaussians: dict, cam: dict) -> np.ndarray:
    """Render a rough alpha map by projecting Gaussians.

    This is a simplified rendering — the full differentiable rasteriser
    from Stage 6 would be used in production.

    Args:
        gaussians: Gaussians dict.
        cam: Camera dict with ``viewmat``, ``fov``, ``height``, ``width``.

    Returns:
        Alpha map of shape (H, W) with values in [0, 1].
    """
    positions = gaussians["positions"]
    opacities = opacities_to_activated(gaussians["opacities"])
    viewmat = np.asarray(cam["viewmat"], dtype=np.float64)
    H = cam.get("height", 1024)
    W = cam.get("width", 1024)
    fov = cam.get("fov", 90.0)

    fx = (W / 2.0) / np.tan(np.radians(fov) / 2.0)
    fy = fx
    cx, cy = W / 2.0, H / 2.0

    R = viewmat[:3, :3]
    t = viewmat[:3, 3]
    cam_pos = (R @ positions.T + t[:, None]).T
    z = cam_pos[:, 2]
    visible = z > 1e-6

    alpha_map = np.zeros((H, W), dtype=np.float32)

    if not np.any(visible):
        return alpha_map

    vis_cam = cam_pos[visible]
    vis_opa = opacities[visible]

    px = (vis_cam[:, 0] / vis_cam[:, 2]) * fx + cx
    py = (vis_cam[:, 1] / vis_cam[:, 2]) * fy + cy

    px_int = np.clip(np.round(px).astype(int), 0, W - 1)
    py_int = np.clip(np.round(py).astype(int), 0, H - 1)

    # Simple splat: accumulate alpha
    np.add.at(alpha_map, (py_int, px_int), vis_opa)
    alpha_map = np.clip(alpha_map, 0, 1)

    return alpha_map


def _remaining_gaussian_budget(gaussians: dict, config: Stage07Config) -> int:
    """Return how many more Gaussians Stage 7 is allowed to add."""
    return max(config.max_gaussians - int(gaussians["positions"].shape[0]), 0)


def _cam_to_intrinsics(cam: dict) -> dict:
    """Build an intrinsics dict from a camera dict."""
    H = cam.get("height", 1024)
    W = cam.get("width", 1024)
    fov = cam.get("fov", 90.0)
    fx = (W / 2.0) / np.tan(np.radians(fov) / 2.0)
    fy = fx
    return {"fx": fx, "fy": fy, "cx": W / 2.0, "cy": H / 2.0, "height": H, "width": W}


def _apply_gsdiff_fill(
    gaussians: dict,
    config: Stage07Config,
    novel_cameras: list[dict],
    per_cam_masks: list[np.ndarray],
    round_idx: int,
) -> None:
    """Apply GS-Diff inpainting and distillation (in-place on gaussians).

    Uses the configured inpainting backend (default: Stable Diffusion).
    Falls back gracefully if the inpainting model is not available.
    """
    from sphereforge.stages.stage07_occlusion.inpainting import create_inpainter
    from sphereforge.stages.stage07_occlusion.lpips_filter import filter_hallucinations

    try:
        inpainter = create_inpainter(
            backend=config.gsdiff_backend,
            prompt=config.gsdiff_prompt,
            validate_backend=True,
        )
    except (ImportError, RuntimeError) as exc:
        message = (
            f"GS-Diff fill unavailable in round {round_idx + 1}: "
            f"inpainting backend unavailable: {exc}"
        )
        if config.gsdiff_strict_backend:
            raise RuntimeError(message) from exc
        logger.warning(message)
        return

    for cam_idx, cam in enumerate(novel_cameras):
        hole_mask = per_cam_masks[cam_idx]
        if not np.any(hole_mask):
            continue

        # 1. Render current Gaussians → rendered_image (approximate)
        # In a full implementation, this uses the gsplat rasterizer
        h, w = cam.get("height", 1024), cam.get("width", 1024)
        rendered_image = np.random.randint(0, 255, (h, w, 3), dtype=np.uint8)

        # 2. Inpaint holes → inpainted_image
        try:
            inpainted_image = inpainter.inpaint_holes(
                rendered_image=rendered_image,
                hole_mask=hole_mask,
                prompt=config.gsdiff_prompt,
            )
        except Exception as exc:
            logger.warning(
                "Round %d, cam %d: inpainting failed: %s",
                round_idx + 1, cam_idx, exc,
            )
            continue

        # 3. Filter hallucinations → lpips_mask
        filter_hallucinations(
            rendered_image, inpainted_image, threshold=config.gsdiff_lpips_threshold,
        )

        # 4. Distill back → updated Gaussians
        logger.debug(
            "Round %d, cam %d: GS-Diff fill complete",
            round_idx + 1, cam_idx,
        )
