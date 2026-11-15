"""Stage 7 pipeline orchestrator: Occlusion Recovery & Refinement.

Loads the optimized Gaussian splat from Stage 6, computes scene bounds,
generates novel camera viewpoints, and iteratively fills holes using
the configured backend (ShareGS + GS-Diff). Writes the refined PLY
to the output directory.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from sphereforge.common.io import read_ply, write_ply
from sphereforge.logging_utils import log_task_completion
from sphereforge.stages.stage07_occlusion.iterative_fill import fill_holes_iterative
from sphereforge.stages.stage07_occlusion.novel_cameras import generate_novel_cameras

if TYPE_CHECKING:
    from sphereforge.config import Stage07Config

logger = logging.getLogger("sphereforge.stage07.pipeline")


def run_stage07(
    config: Stage07Config,
    optimized_ply_path: Path,
    colmap_dir: Path,
    depth_dir: Path,
    output_dir: Path,
) -> Path:
    """Run Stage 7: Occlusion Recovery & Refinement.

    Orchestrates the full pipeline:
    1. Load optimized Gaussians from Stage 6 PLY.
    2. Compute scene bounding sphere (centre + radius).
    3. Generate novel camera positions around the scene.
    4. Iteratively fill holes using ShareGS + GS-Diff.
    5. Write refined PLY to the output directory.

    Args:
        config: Stage 7 configuration.
        optimized_ply_path: Path to the Stage 6 output PLY file.
        colmap_dir: Path to the COLMAP sparse model directory.
        depth_dir: Path to the depth maps directory (from Stage 4).
        output_dir: Path to write the refined PLY and intermediate data.

    Returns:
        Path to the refined PLY file in the output directory.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ---- 1. Load optimized Gaussians ----
    logger.info("Loading optimized Gaussians from %s", optimized_ply_path)
    gaussians = read_ply(optimized_ply_path)
    n_original = gaussians["positions"].shape[0]
    logger.info("Loaded %d Gaussians", n_original)

    # Stage 6 can hand over far more Gaussians than Stage 7 can afford: the
    # diffusion pass and the differentiable rasterizer both hold full-resolution
    # tensors, and a 386k-Gaussian input exhausted an 8 GB card. ``max_gaussians``
    # only limited *growth* inside ShareGS, so cap the input here too, keeping
    # the most opaque Gaussians (the ones that actually contribute to the image).
    if config.max_gaussians > 0 and n_original > config.max_gaussians:
        opacities = np.asarray(gaussians["opacities"], dtype=np.float32)
        keep = np.argsort(-opacities)[: config.max_gaussians]
        keep.sort()
        gaussians = {
            key: (value[keep] if value is not None else None)
            for key, value in gaussians.items()
        }
        logger.info(
            "Capped Stage 7 input to %d Gaussians (from %d, keeping the most opaque)",
            config.max_gaussians,
            n_original,
        )

    # ---- 2. Compute scene bounds ----
    scene_center, scene_radius = _compute_scene_bounds(gaussians)
    logger.info(
        "Scene bounds: centre=%s, radius=%.4f",
        scene_center.tolist(),
        scene_radius,
    )

    # ---- 3. Load COLMAP model ----
    colmap_model = _load_colmap_model(colmap_dir)

    # ---- 4. Generate novel cameras ----
    # Determine number of cameras from config
    # refine_cameras=36 → n_directions=12, n_distances=3 → 36 cameras
    n_directions, n_distances = _resolve_camera_layout(config.refine_cameras)
    novel_cameras = generate_novel_cameras(
        scene_center=scene_center,
        scene_radius=scene_radius,
        n_directions=n_directions,
        n_distances=n_distances,
    )
    logger.info("Generated %d novel cameras for occlusion recovery", len(novel_cameras))

    # ---- 5. Iterative hole fill ----
    if config.refine_backend == "omniroam":
        from sphereforge.stages.stage07_occlusion.omniroam import omniroam_fill

        gaussians = omniroam_fill(gaussians, config, colmap_model)
    else:
        # Default: sharegs_gsdiff or gsfix3d
        gaussians = fill_holes_iterative(
            gaussians=gaussians,
            config=config,
            novel_cameras=novel_cameras,
            colmap_model=colmap_model,
        )

    # ---- 6. Write refined PLY ----
    output_ply = output_dir / "refined.ply"
    n_final = gaussians["positions"].shape[0]
    logger.info(
        "Writing refined PLY: %d Gaussians (%d added during refinement)",
        n_final,
        n_final - n_original,
    )

    sh_coeffs = gaussians.get("sh_coeffs")
    write_ply(
        path=output_ply,
        positions=gaussians["positions"],
        colors=gaussians["colors"],
        opacities=gaussians["opacities"],
        scales=gaussians["scales"],
        rotations=gaussians["rotations"],
        # read_ply's sh_coeffs carries the DC term first; write_ply wants only
        # the f_rest_* bands (9/24/45 wide for SH degree 1/2/3).
        sh_coeffs=sh_coeffs[:, 3:] if sh_coeffs is not None and sh_coeffs.shape[-1] > 3 else None,
    )

    # ---- 7. Log completion ----
    log_task_completion(
        task_id="T7.13",
        notes=f"Stage 7 pipeline complete: {n_final} Gaussians, {n_final - n_original} added",
        files_created=[str(output_ply)],
        files_modified=[],
    )

    logger.info("Stage 7 complete. Output: %s", output_ply)
    return output_ply


def _compute_scene_bounds(gaussians: dict) -> tuple[np.ndarray, float]:
    """Compute the bounding sphere of the scene from Gaussian positions.

    Uses a simple axis-aligned bounding box to estimate the centre and
    radius. A more accurate approach would use the minimum enclosing
    sphere (Welzl's algorithm), but the AABB is sufficient for camera
    placement.

    Args:
        gaussians: Dict with ``positions`` (N, 3).

    Returns:
        Tuple of (centre (3,), radius (float)).
    """
    positions = np.asarray(gaussians["positions"], dtype=np.float32)
    # A handful of stray Gaussians (left over from depth outliers) can sit far
    # outside the real scene. Using the farthest point would then place the
    # novel cameras outside the captured volume, so nearly every pixel reads as
    # a hole and Stage 7 fabricates hundreds of thousands of Gaussians.
    # Weight by opacity so near-invisible floaters do not define the bounds.
    opacities = gaussians.get("opacities")
    if opacities is not None:
        from sphereforge.common.gaussian_parameters import opacities_to_activated

        weights = opacities_to_activated(np.asarray(opacities))
        # Keep the Gaussians that actually contribute to the image.
        keep = weights >= max(0.05, float(np.percentile(weights, 40)))
        if int(np.sum(keep)) >= 8:
            positions = positions[keep]

    scene_center = np.median(positions, axis=0)
    distances = np.linalg.norm(positions - scene_center, axis=1)
    # Use a tight percentile. The novel cameras orbit at 0.5-1.5x this radius,
    # so a radius inflated by a tail of stray Gaussians places cameras outside
    # the captured volume; they then synthesise Gaussians beyond the walls and
    # drag the whole reconstruction outward. The median distance is the
    # distance to the walls themselves, which is what the cameras should orbit.
    scene_radius = float(np.percentile(distances, 50))
    # Ensure a minimum radius to avoid degenerate cases
    scene_radius = max(scene_radius, 1e-3)
    return scene_center, scene_radius


def _resolve_camera_layout(n_cameras: int) -> tuple[int, int]:
    """Determine n_directions and n_distances from the target camera count.

    Tries to factorise *n_cameras* into two integers that multiply to the
    target. Falls back to (n_cameras, 1) if no good factorisation exists.

    Args:
        n_cameras: Target number of cameras.

    Returns:
        (n_directions, n_distances) tuple.
    """
    # Prefer 3 distance rings (matches design doc: 0.5x, 1.0x, 1.5x)
    if n_cameras % 3 == 0:
        return n_cameras // 3, 3
    # Try 2 distance rings
    if n_cameras % 2 == 0:
        return n_cameras // 2, 2
    # Single distance ring
    return n_cameras, 1


def _load_colmap_model(colmap_dir: Path) -> dict:
    """Load COLMAP sparse model data from the given directory.

    Returns a dict with ``cameras`` and ``images`` keys. Returns an
    empty dict if the directory does not exist or is incomplete.

    Args:
        colmap_dir: Path to the COLMAP sparse model directory.

    Returns:
        Dict with COLMAP data or empty dict.
    """
    colmap_dir = Path(colmap_dir)
    model: dict = {"cameras": {}, "images": {}}

    if not colmap_dir.exists():
        logger.warning("COLMAP directory not found: %s", colmap_dir)
        return model

    try:
        from sphereforge.common.colmap_helpers import (
            parse_cameras_txt,
            parse_images_txt,
        )

        cameras_file = colmap_dir / "cameras.txt"
        images_file = colmap_dir / "images.txt"

        if cameras_file.exists():
            model["cameras"] = parse_cameras_txt(cameras_file)
        if images_file.exists():
            model["images"] = parse_images_txt(images_file)
    except Exception as exc:
        logger.warning("Failed to load COLMAP model from %s: %s", colmap_dir, exc)

    return model
