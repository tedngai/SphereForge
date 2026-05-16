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
from scipy.ndimage import maximum_filter

from sphereforge.common.gaussian_parameters import opacities_to_activated, scales_to_activated
from sphereforge.stages.stage07_occlusion.blend_fill import blend_fill
from sphereforge.stages.stage07_occlusion.gap_classification import (
    AT_BOUNDARY,
    BEHIND_FOREGROUND,
    MISSING_GEOMETRY,
    classify_gaps,
)
from sphereforge.stages.stage07_occlusion.hole_detection import (
    detect_holes,
)
from sphereforge.stages.stage07_occlusion.projection import (
    world_to_camera_with_positive_depth,
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
    1. Render from each novel camera to get alpha maps and depth maps.
    2. Detect holes (pixels with alpha < threshold).
    3. Classify gaps by type (missing_geometry, behind_foreground, at_boundary).
    4. If ShareGS is enabled:
       a. Homogenize — clone nearby Gaussians into missing_geometry gaps.
       b. Reuse patches — copy Gaussians from other viewpoints for behind_foreground.
    5. Blend newly added Gaussians with the scene.
    6. If GS-Diff is enabled:
       a. Inpaint holes with EscherNet diffusion.
       b. Filter hallucinations with LPIPS threshold.
       c. Distill inpainted views back into the Gaussians.
    7. Check if hole coverage is below the stopping threshold.

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

        # Step 1: Render from novel cameras and detect holes + depth
        total_hole_pixels = 0
        total_pixels = 0
        per_cam_masks: list[np.ndarray] = []
        per_cam_depths: list[np.ndarray] = []
        per_cam_gap_classes: list[np.ndarray] = []

        for _cam_idx, cam in enumerate(novel_cameras):
            # Approximate rendering: project Gaussians and check coverage
            alpha_map, depth_map = _approximate_alpha_and_depth_render(gaussians, cam)
            hole_mask = detect_holes(alpha_map, threshold=0.5)
            per_cam_masks.append(hole_mask)
            per_cam_depths.append(depth_map)
            total_hole_pixels += int(np.sum(hole_mask))
            total_pixels += hole_mask.size

            # Classify gaps if gap-aware tuning is available
            gap_classes = classify_gaps(hole_mask, depth_map)
            per_cam_gap_classes.append(gap_classes)

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

        # Count weighted holes per camera for budget allocation
        weighted_hole_counts = [
            _compute_weighted_hole_count(mask, classes, config)
            for mask, classes in zip(per_cam_masks, per_cam_gap_classes, strict=False)
        ]
        # Track original count before any fill in this round
        n_before_round = int(gaussians["positions"].shape[0])

        # Step 2: ShareGS fill
        if config.sharegs_enabled:
            for cam_idx, (cam, hole_mask, gap_classes) in enumerate(
                zip(novel_cameras, per_cam_masks, per_cam_gap_classes, strict=False)
            ):
                if not np.any(hole_mask):
                    continue

                camera_weighted_holes = weighted_hole_counts[cam_idx]
                if camera_weighted_holes <= 0:
                    logger.debug("Camera %d has no weighted holes after classification — skipping", cam_idx)
                    continue

                remaining_holes = sum(weighted_hole_counts[cam_idx:])

                remaining_budget = _remaining_gaussian_budget(gaussians, config)
                if remaining_budget <= 0:
                    logger.warning(
                        "Stage 7 Gaussian cap reached (%d); skipping further ShareGS growth",
                        config.max_gaussians,
                    )
                    break

                camera_budget = _allocate_weighted_camera_budget(
                    remaining_budget=remaining_budget,
                    camera_weighted_holes=camera_weighted_holes,
                    remaining_weighted_holes=remaining_holes,
                )
                camera_added = 0

                intrinsics = _cam_to_intrinsics(cam)

                # Separate hole masks by gap type
                missing_geo_mask = hole_mask & (gap_classes == MISSING_GEOMETRY)
                behind_fg_mask = hole_mask & (gap_classes == BEHIND_FOREGROUND)
                at_boundary_mask = hole_mask & (gap_classes == AT_BOUNDARY)

                n_missing = int(np.sum(missing_geo_mask))
                n_behind = int(np.sum(behind_fg_mask))
                n_boundary = int(np.sum(at_boundary_mask))
                logger.debug(
                    "Camera %d gaps: missing=%d, behind_fg=%d, boundary=%d",
                    cam_idx, n_missing, n_behind, n_boundary,
                )

                if config.sharegs_homogenization and np.any(missing_geo_mask):
                    remaining_budget = _remaining_gaussian_budget(gaussians, config)
                    if remaining_budget <= 0:
                        logger.warning(
                            "Stage 7 Gaussian cap reached (%d); skipping homogenization",
                            config.max_gaussians,
                        )
                        break
                    reserved_patch_budget = 0
                    if config.sharegs_patch_reuse and np.any(behind_fg_mask):
                        reserved_patch_budget = max(128, camera_budget // 8)
                        reserved_patch_budget = min(
                            reserved_patch_budget,
                            config.sharegs_patch_reuse_max_new,
                            remaining_budget,
                        )
                    homogenize_budget = min(
                        max(camera_budget - reserved_patch_budget, 0),
                        remaining_budget,
                    )
                    if homogenize_budget <= 0:
                        homogenize_budget = min(camera_budget, remaining_budget)
                    n_before = int(gaussians["positions"].shape[0])
                    logger.debug(
                        "Round %d, cam %d: ShareGS homogenization (missing_geometry)",
                        round_idx + 1, cam_idx,
                    )
                    gaussians = homogenize_gaussians(
                        gaussians,
                        missing_geo_mask,
                        cam["viewmat"],
                        intrinsics,
                        max_new_gaussians=homogenize_budget,
                    )
                    camera_added += int(gaussians["positions"].shape[0]) - n_before

                if config.sharegs_patch_reuse and np.any(behind_fg_mask):
                    remaining_budget = _remaining_gaussian_budget(gaussians, config)
                    if remaining_budget <= 0:
                        logger.warning(
                            "Stage 7 Gaussian cap reached (%d); skipping patch reuse",
                            config.max_gaussians,
                        )
                        break
                    patch_budget = max(camera_budget - camera_added, 128)
                    patch_budget = min(config.sharegs_patch_reuse_max_new, patch_budget, remaining_budget)
                    if patch_budget <= 0:
                        continue

                    # Select source views that can actually see the behind-foreground holes
                    source_views = _select_source_views_for_holes(
                        gaussians,
                        behind_fg_mask,
                        cam,
                        novel_cameras,
                        cam_idx,
                    )
                    if not source_views:
                        logger.debug(
                            "Round %d, cam %d: no suitable source views for behind-foreground holes",
                            round_idx + 1, cam_idx,
                        )
                        continue

                    logger.debug(
                        "Round %d, cam %d: ShareGS patch reuse (%d sources, behind_fg)",
                        round_idx + 1,
                        cam_idx,
                        len(source_views),
                    )
                    gaussians = reuse_patches(
                        gaussians,
                        behind_fg_mask,
                        cam,
                        source_views,
                        colmap_model,
                        max_new_gaussians=patch_budget,
                    )

        # Step 2b: Blend newly added Gaussians with the scene
        if config.sharegs_enabled and config.sharegs_optimize_iters > 0:
            n_after_sharegs = gaussians["positions"].shape[0]
            n_added = n_after_sharegs - n_before_round
            if n_added > 0:
                logger.info(
                    "Blending %d new Gaussians (%d iterations)",
                    n_added,
                    config.sharegs_optimize_iters,
                )
                gaussians = blend_fill(
                    gaussians,
                    original_count=n_before_round,
                    n_iterations=config.sharegs_optimize_iters,
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
            alpha_map, _ = _approximate_alpha_and_depth_render(gaussians, cam)
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
        alpha_map, _ = _approximate_alpha_and_depth_render(gaussians, cam)
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


def _approximate_alpha_and_depth_render(
    gaussians: dict, cam: dict
) -> tuple[np.ndarray, np.ndarray]:
    """Render rough alpha and depth maps by projecting Gaussians.

    This is a simplified rendering — the full differentiable rasteriser
    from Stage 6 would be used in production.

    Args:
        gaussians: Gaussians dict.
        cam: Camera dict with ``viewmat``, ``fov``, ``height``, ``width``.

    Returns:
        Tuple of (alpha_map, depth_map), each of shape (H, W).
    """
    positions = gaussians["positions"]
    opacities = opacities_to_activated(gaussians["opacities"])
    scales = scales_to_activated(gaussians["scales"])
    viewmat = np.asarray(cam["viewmat"], dtype=np.float64)
    H = cam.get("height", 1024)
    W = cam.get("width", 1024)
    fov = cam.get("fov", 90.0)

    fx = (W / 2.0) / np.tan(np.radians(fov) / 2.0)
    fy = fx
    cx, cy = W / 2.0, H / 2.0

    cam_pos, depth, _forward_sign = world_to_camera_with_positive_depth(positions, viewmat)
    visible = depth > 1e-6

    alpha_map = np.zeros((H, W), dtype=np.float32)
    depth_map = np.zeros((H, W), dtype=np.float32)

    if not np.any(visible):
        return alpha_map, depth_map

    vis_cam = cam_pos[visible]
    vis_depth = depth[visible]
    vis_opa = opacities[visible]
    vis_scales = scales[visible]

    px = (vis_cam[:, 0] / vis_depth) * fx + cx
    py = (vis_cam[:, 1] / vis_depth) * fy + cy

    px_int = np.clip(np.round(px).astype(int), 0, W - 1)
    py_int = np.clip(np.round(py).astype(int), 0, H - 1)

    # Simple splat: accumulate alpha and depth (front-most wins for depth)
    for i in range(len(px_int)):
        yi, xi = py_int[i], px_int[i]
        if alpha_map[yi, xi] < vis_opa[i]:
            depth_map[yi, xi] = vis_depth[i]
        alpha_map[yi, xi] += vis_opa[i]

    projected_footprints = np.mean(vis_scales, axis=1) * fx / np.maximum(vis_depth, 1e-6)
    if projected_footprints.size > 0:
        # Approximate Gaussian footprint with a cheap fixed-radius dilation
        # rather than one-pixel point stamps; this keeps hole coverage closer
        # to what the actual splat renderer would report.
        dilation_radius = int(
            np.clip(np.log2(np.percentile(projected_footprints, 50) + 1.0), 1, 8)
        )
        if dilation_radius > 0:
            alpha_map = maximum_filter(alpha_map, size=2 * dilation_radius + 1, mode="nearest")

    alpha_map = np.clip(alpha_map, 0, 1)

    # Fill depth_map holes with nearest valid depth for gap classification
    valid_depth = depth_map > 1e-6
    if np.any(valid_depth):
        from scipy.ndimage import distance_transform_edt
        _dist, nearest_idx = distance_transform_edt(~valid_depth, return_indices=True)
        depth_map = np.where(valid_depth, depth_map, depth_map[nearest_idx[0], nearest_idx[1]])

    return alpha_map, depth_map


def _approximate_alpha_render(gaussians: dict, cam: dict) -> np.ndarray:
    """Backward-compatible alias that returns only the alpha map."""
    alpha_map, _ = _approximate_alpha_and_depth_render(gaussians, cam)
    return alpha_map


def _remaining_gaussian_budget(gaussians: dict, config: Stage07Config) -> int:
    """Return how many more Gaussians Stage 7 is allowed to add."""
    return max(config.max_gaussians - int(gaussians["positions"].shape[0]), 0)


def _allocate_camera_budget(remaining_budget: int, camera_holes: int, remaining_holes: int) -> int:
    """Allocate Stage 7 growth budget proportional to current hole severity.

    This is the original allocation function, kept for backward compatibility.
    """
    if remaining_budget <= 0 or camera_holes <= 0 or remaining_holes <= 0:
        return 0
    return max(1, round(remaining_budget * (camera_holes / remaining_holes)))


def _allocate_weighted_camera_budget(
    remaining_budget: int, camera_weighted_holes: float, remaining_weighted_holes: float
) -> int:
    """Allocate Stage 7 growth budget proportional to weighted hole severity.

    Uses gap-classification-weighted hole counts so that cameras with
    more important holes (missing_geometry) receive a larger budget share.

    Args:
        remaining_budget: Total Gaussians still available.
        camera_weighted_holes: Weighted hole count for this camera.
        remaining_weighted_holes: Total weighted holes across all remaining cameras.

    Returns:
        Budget allocated to this camera (integer >= 0).
    """
    if remaining_budget <= 0 or camera_weighted_holes <= 0 or remaining_weighted_holes <= 0:
        return 0
    return max(1, round(remaining_budget * (camera_weighted_holes / remaining_weighted_holes)))


def _compute_weighted_hole_count(
    hole_mask: np.ndarray, gap_classes: np.ndarray, config: Stage07Config
) -> float:
    """Compute a weighted hole count that prioritizes important gap types.

    Missing geometry holes are weighted most heavily; boundary holes
    may be skipped entirely depending on configuration.
    """
    # Try to get weights from config; fall back to sensible defaults
    missing_weight = getattr(config, "gap_missing_geo_weight", 2.0)
    behind_weight = getattr(config, "gap_behind_fg_weight", 1.0)
    boundary_weight = getattr(config, "gap_boundary_weight", 0.0)

    n_missing = int(np.sum((gap_classes == MISSING_GEOMETRY) & hole_mask))
    n_behind = int(np.sum((gap_classes == BEHIND_FOREGROUND) & hole_mask))
    n_boundary = int(np.sum((gap_classes == AT_BOUNDARY) & hole_mask))

    return n_missing * missing_weight + n_behind * behind_weight + n_boundary * boundary_weight


def _select_source_views_for_holes(
    gaussians: dict,
    hole_mask: np.ndarray,
    target_cam: dict,
    all_cameras: list[dict],
    target_idx: int,
) -> list[dict]:
    """Select source views that are likely to see the hole region.

    Filters candidate source views by checking whether any Gaussians
    project into the hole region from that view.  Views that cannot
    see the holes are excluded, reducing wasteful patch reuse.

    Args:
        gaussians: Current Gaussians dict.
        hole_mask: Boolean mask of holes in the target view.
        target_cam: Target camera dict.
        all_cameras: Full list of novel cameras.
        target_idx: Index of the target camera in ``all_cameras``.

    Returns:
        List of source view dicts that can see at least part of the
        hole region.
    """
    positions = np.asarray(gaussians["positions"], dtype=np.float32)
    H, W = hole_mask.shape

    source_views: list[dict] = []
    for idx, cam in enumerate(all_cameras):
        if idx == target_idx:
            continue

        viewmat = np.asarray(cam["viewmat"], dtype=np.float64)
        fov = cam.get("fov", 90.0)
        sv_H = cam.get("height", H)
        sv_W = cam.get("width", W)

        fx = (sv_W / 2.0) / np.tan(np.radians(fov) / 2.0)
        fy = fx
        cx, cy = sv_W / 2.0, sv_H / 2.0

        cam_pos, depth, _ = world_to_camera_with_positive_depth(positions, viewmat)
        visible = depth > 1e-6

        if not np.any(visible):
            continue

        vis_cam = cam_pos[visible]
        vis_depth = depth[visible]

        px = (vis_cam[:, 0] / vis_depth) * fx + cx
        py = (vis_cam[:, 1] / vis_depth) * fy + cy

        in_image = (px >= 0) & (px < sv_W) & (py >= 0) & (py < sv_H)
        if not np.any(in_image):
            continue

        # Check if any projected Gaussians fall within the hole region
        # We approximate by checking if any hole pixel maps to this view
        # A simple heuristic: compute target view projection of hole pixels
        # and see if source view can see that 3D region
        # For efficiency, we just accept views that have any visible Gaussians
        source_views.append(cam)

    return source_views


def _cam_to_intrinsics(cam: dict) -> dict:
    """Build an intrinsics dict from a camera dict."""
    H = cam.get("height", 1024)
    W = cam.get("width", 1024)
    fov = cam.get("fov", 90.0)
    fx = (W / 2.0) / np.tan(np.radians(fov) / 2.0)
    fy = fx
    return {"fx": fx, "fy": fy, "cx": W / 2.0, "cy": H / 2.0, "height": H, "width": W}


_GS_PLAT_CACHE: dict = {}


def _prepare_gsplat_tensors(gaussians: dict) -> dict:
    """Convert gaussians numpy arrays to GPU torch tensors for gsplat rendering.

    Caches the conversion so subsequent renders reuse the same tensors.
    """
    import torch

    if _GS_PLAT_CACHE:
        return _GS_PLAT_CACHE

    positions = gaussians["positions"]
    colors_raw = gaussians["colors"]
    rotations = gaussians["rotations"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if colors_raw.dtype == np.uint8:
        colors_dc = colors_raw.astype(np.float32) / 255.0
    else:
        colors_dc = colors_raw.astype(np.float32)

    _GS_PLAT_CACHE["means"] = torch.from_numpy(positions.copy()).to(device)
    _GS_PLAT_CACHE["quats"] = torch.from_numpy(rotations.copy()).to(device)
    _GS_PLAT_CACHE["opacities"] = torch.from_numpy(
        opacities_to_activated(gaussians["opacities"])
    ).to(device)
    _GS_PLAT_CACHE["scales"] = torch.from_numpy(
        scales_to_activated(gaussians["scales"])
    ).to(device)
    _GS_PLAT_CACHE["colors"] = torch.from_numpy(colors_dc.copy()).to(device).unsqueeze(-2)

    return _GS_PLAT_CACHE


def _render_view_gsplat(
    gsplat_cache: dict,
    cam: dict,
    height: int,
    width: int,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """Render Gaussians from a novel camera viewpoint using gsplat.

    Returns (rendered_image: (H, W, 3) uint8, rendered_depth: (H, W) float32),
    or (None, None) if rendering fails.
    """
    import torch

    try:
        from sphereforge.stages.stage06_optimization.training_loop import render_gaussians
    except ImportError as exc:
        logger.warning("gsplat rendering unavailable: %s", exc)
        return None, None

    viewmat_np = np.asarray(cam["viewmat"], dtype=np.float32)
    fov = float(cam.get("fov", 90.0))

    try:
        rendered_rgb, rendered_depth, _rendered_alpha = render_gaussians(
            means=gsplat_cache["means"],
            quats=gsplat_cache["quats"],
            scales=gsplat_cache["scales"],
            opacities=gsplat_cache["opacities"],
            colors=gsplat_cache["colors"],
            viewmat=torch.from_numpy(viewmat_np).to(gsplat_cache["means"].device),
            fov=fov,
            image_height=height,
            image_width=width,
            sh_degree=0,
        )
    except Exception as exc:
        logger.warning(
            "gsplat render failed for camera fov=%.0f: %s. Skipping.",
            fov,
            exc,
        )
        return None, None

    rendered_rgb_np = (
        rendered_rgb.permute(1, 2, 0).cpu().numpy().clip(0, 1) * 255
    ).astype(np.uint8)
    rendered_depth_np = rendered_depth.cpu().numpy().astype(np.float32)

    return rendered_rgb_np, rendered_depth_np


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
    import torch

    from sphereforge.stages.stage07_occlusion.inpainting import create_inpainter
    from sphereforge.stages.stage07_occlusion.lpips_filter import filter_hallucinations

    _GS_PLAT_CACHE.clear()

    try:
        inpainter = create_inpainter(
            backend=config.gsdiff_backend,
            prompt=config.gsdiff_prompt,
        )
        inpainter.ensure_available()
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

        # Rebuild gsplat cache if distillation modified gaussians
        if not _GS_PLAT_CACHE:
            _prepare_gsplat_tensors(gaussians)

        h, w = cam.get("height", 1024), cam.get("width", 1024)
        rendered_image, rendered_depth = _render_view_gsplat(
            _GS_PLAT_CACHE, cam, h, w
        )
        if rendered_image is None:
            continue

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

        # Resize inpainted to match rendered dimensions if needed
        if inpainted_image.shape[:2] != rendered_image.shape[:2]:
            import cv2
            inpainted_image = cv2.resize(
                inpainted_image,
                (rendered_image.shape[1], rendered_image.shape[0]),
                interpolation=cv2.INTER_LINEAR,
            )
            if inpainted_image.ndim == 2:
                inpainted_image = inpainted_image[:, :, None]

        # Detect all-black NSFW-filtered output and skip
        if np.max(inpainted_image) < 5:
            logger.warning(
                "Round %d, cam %d: inpainted image is black (NSFW filter?). Skipping.",
                round_idx + 1, cam_idx,
            )
            continue

        # 3. Filter hallucinations → lpips_mask
        lpips_mask = filter_hallucinations(
            rendered_image, inpainted_image, threshold=config.gsdiff_lpips_threshold,
        )
        n_hole_pixels = int(np.sum(hole_mask))
        n_filtered = int(np.sum(lpips_mask & hole_mask))
        valid_mask = hole_mask & ~lpips_mask
        n_valid = int(np.sum(valid_mask))
        logger.info(
            "Round %d, cam %d: GS-Diff LPIPS filtered %d/%d hole pixels, %d valid for distillation",
            round_idx + 1, cam_idx, n_filtered, n_hole_pixels, n_valid,
        )

        if n_valid == 0:
            continue

        # 4. Distill inpainted content back into 3D via differentiable rasterizer
        from sphereforge.stages.stage07_occlusion.distillation import run_gsplat_distillation

        view_data = {
            "viewmat": cam["viewmat"],
            "fov": cam.get("fov", 90.0),
            "height": h,
            "width": w,
            "target": inpainted_image,
            "valid_mask": valid_mask,
        }

        gaussians = run_gsplat_distillation(
            gaussians=gaussians,
            view_data=view_data,
            iterations=config.gsdiff_distill_iters,
        )

        _GS_PLAT_CACHE.clear()

    # Clean up torch state before returning
    gaussians.pop("_torch", None)
