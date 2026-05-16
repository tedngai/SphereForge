"""Stage 4 pipeline orchestration: dense depth estimation.

Coordinates depth estimation, COLMAP alignment, scene analysis, and
optional RPG360 anchor refinement for each frame in the dataset.
"""

from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

import numpy as np

from sphereforge.common.io import read_depth, read_image, write_depth
from sphereforge.logging_utils import log_task_completion
from sphereforge.stages.stage04_depth.depth_alignment import align_depth_to_colmap
from sphereforge.stages.stage04_depth.model_factory import (
    get_depth_estimator,
    is_stub_depth_model,
)
from sphereforge.stages.stage04_depth.scene_analysis import analyze_depth_scene

if TYPE_CHECKING:
    from pathlib import Path

    from sphereforge.config import Stage04Config

logger = logging.getLogger("sphereforge.stage04.pipeline")


def _write_stage04_diagnostics(
    output_dir: Path,
    *,
    depth_model: str,
    stub_depth_backend: bool,
    total_frames: int,
    aligned_frames: int,
    depth_paths: list[Path],
) -> Path:
    """Persist a small Stage 4 summary with stub-backend visibility."""
    warnings: list[str] = []
    if stub_depth_backend:
        warnings.append(
            "Selected depth backend is currently a stub implementation; treat these depth maps as diagnostic-only."
        )

    diagnostics_path = output_dir / "depth_diagnostics.json"
    payload = {
        "depth_model": depth_model,
        "stub_depth_backend": stub_depth_backend,
        "total_frames": total_frames,
        "aligned_frames": aligned_frames,
        "unaligned_frames": total_frames - aligned_frames,
        "warnings": warnings,
        "depth_paths": [str(path) for path in depth_paths],
    }
    diagnostics_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return diagnostics_path


def _process_single_frame_stage04(
    frame_path: Path,
    frame_idx: int,
    config: Stage04Config,
    sparse_model: dict,
    cubemap_dir: Path,
    output_dir: Path,
    rpg360_anchor: np.ndarray | None,
) -> tuple[Path, np.ndarray, float, float, bool]:
    """Process a single frame: depth estimation + alignment + write.

    Creates its own depth estimator to avoid thread-safety issues.

    Returns:
        (depth_path, aligned_depth, scale, shift)
    """
    frame_name = frame_path.stem + frame_path.suffix
    logger.info("Processing frame %d: %s", frame_idx + 1, frame_name)

    image = read_image(frame_path)

    # Create estimator locally for thread safety
    estimator_kwargs: dict = {}
    if config.depth_model == "rpg360":
        estimator_kwargs["rpg360_perspective_model"] = config.rpg360_perspective_model
    depth_estimator = get_depth_estimator(config.depth_model, **estimator_kwargs)

    try:
        raw_depth = depth_estimator.estimate_depth(image)
    except NotImplementedError as exc:
        raise RuntimeError(
            f"Depth estimation failed for frame '{frame_name}': {exc}. "
            f"The selected model ('{config.depth_model}') is not fully implemented "
            f"or its weights are missing. Choose a working model in the config "
            f"(e.g., depth_model='depth_anything_v2') and ensure dependencies "
            f"are installed (pip install 'sphereforge[depth]')."
        ) from exc

    image_name_for_model = frame_path.name
    try:
        aligned_depth, scale, shift = align_depth_to_colmap(
            depth_map=raw_depth,
            sparse_model=sparse_model,
            image_name=image_name_for_model,
            rpg360_anchor=rpg360_anchor if frame_idx == 0 else None,
            colmap_dataset_dir=cubemap_dir,
        )
        alignment_succeeded = True
    except (ValueError, FileNotFoundError) as exc:
        logger.warning(
            "COLMAP alignment failed for '%s': %s. Using unaligned depth.",
            frame_name,
            exc,
        )
        aligned_depth = raw_depth.astype(np.float32)
        scale = 1.0
        shift = 0.0
        alignment_succeeded = False

    depth_path = output_dir / f"{frame_path.stem}_depth.npy"
    write_depth(depth_path, aligned_depth)

    logger.debug(
        "Frame '%s': depth range [%.2f, %.2f], scale=%.4f, shift=%.4f",
        frame_name,
        float(np.min(aligned_depth[aligned_depth > 0])) if np.any(aligned_depth > 0) else 0.0,
        float(np.max(aligned_depth)),
        scale,
        shift,
    )

    return depth_path, aligned_depth, scale, shift, alignment_succeeded


def run_stage04(
    config: Stage04Config,
    frame_paths: list[Path],
    cubemap_dir: Path,
    sparse_model: dict,
    output_dir: Path,
    num_workers: int = 1,
) -> dict:
    """Run Stage 4: Dense Depth Estimation.

    Orchestrates the full depth estimation pipeline:

    1. Creates the depth estimator via the model factory.
    2. For each frame:
       a. Loads the ERP image.
       b. Estimates depth using the selected model.
       c. Aligns the monocular depth to COLMAP metric scale.
       d. Writes the aligned depth map to the output directory.
    3. Runs scene analysis on the first frame's depth map.
    4. If the RPG360 anchor is available, refines alignment using it.
    5. Returns a summary dict with depth paths and scene parameters.

    Args:
        config: Stage04Config with model selection and alignment settings.
        frame_paths: List of paths to equirectangular frame images.
        cubemap_dir: Directory containing cubemap face images (used for
            RPG360 anchor computation if needed).
        sparse_model: COLMAP sparse model dict with keys ``cameras``,
            ``images``, ``points3D``.
        output_dir: Directory where depth maps will be written.

    Returns:
        Dictionary with keys:

        - **depth_paths** (list[Path]): Paths to the written depth maps,
          one per frame, in the same order as ``frame_paths``.
        - **scene_params** (dict): Scene analysis results from the first
          frame's depth map (see ``analyze_depth_scene``).

    Raises:
        FileNotFoundError: If any frame path does not exist.
        ValueError: If the sparse model is missing required keys or
            alignment fails.
    """
    logger.info(
        "Starting Stage 4: depth_model=%s, scale_alignment=%s, "
        "%d frames, workers=%d",
        config.depth_model,
        config.scale_alignment,
        len(frame_paths),
        num_workers,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    stub_depth_backend = is_stub_depth_model(config.depth_model)
    if stub_depth_backend:
        logger.warning(
            "Stage 4 is using stub depth backend '%s'; outputs are not trustworthy scene depth.",
            config.depth_model,
        )

    # Pre-compute RPG360 anchor if needed
    rpg360_anchor: np.ndarray | None = None
    use_rpg360_anchor = (
        config.scale_alignment == "median_ratio_with_rpg360_anchor"
    )
    if use_rpg360_anchor and config.depth_model == "panda":
        rpg360_anchor = _compute_rpg360_anchor(
            cubemap_dir, sparse_model, output_dir, config
        )

    # Step 2: Process each frame (serial or threaded)
    if num_workers > 1:
        logger.info("Using %d threads for depth estimation", num_workers)
        args = [
            (fp, idx, config, sparse_model, cubemap_dir, output_dir, rpg360_anchor)
            for idx, fp in enumerate(frame_paths)
        ]
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            results = list(executor.map(_process_single_frame_stage04_worker, args))
    else:
        results = []
        for idx, fp in enumerate(frame_paths):
            results.append(
                _process_single_frame_stage04(
                    fp, idx, config, sparse_model, cubemap_dir, output_dir, rpg360_anchor
                )
            )

    depth_paths = [r[0] for r in results]
    first_aligned_depth = results[0][1] if results else None
    aligned_frames = sum(1 for result in results if result[4])

    # Step 3: Run scene analysis on first frame
    scene_params: dict = {}
    if first_aligned_depth is not None:
        try:
            scene_params = analyze_depth_scene(first_aligned_depth)
            logger.info("Scene analysis complete for first frame")
        except ValueError as exc:
            logger.warning("Scene analysis failed: %s", exc)
            scene_params = {}

    # Step 4: If RPG360 anchor available, refine remaining frames
    if rpg360_anchor is not None and len(frame_paths) > 1:
        _refine_remaining_frames(
            depth_paths, rpg360_anchor, output_dir, frame_paths
        )

    # Apply depth clipping from config
    _apply_depth_clipping(depth_paths, config, scene_params)
    diagnostics_path = _write_stage04_diagnostics(
        output_dir,
        depth_model=config.depth_model,
        stub_depth_backend=stub_depth_backend,
        total_frames=len(frame_paths),
        aligned_frames=aligned_frames,
        depth_paths=depth_paths,
    )

    logger.info(
        "Stage 4 complete: %d depth maps written to %s",
        len(depth_paths),
        output_dir,
    )

    # Log task completion
    log_task_completion(
        task_id="T4.6",
        notes="Stage 4 pipeline: dense depth estimation orchestration",
        files_created=[str(p) for p in depth_paths],
        files_modified=[],
    )

    return {
        "depth_paths": depth_paths,
        "scene_params": scene_params,
        "diagnostics": {
            "path": diagnostics_path,
            "stub_depth_backend": stub_depth_backend,
            "aligned_frames": aligned_frames,
        },
    }


def _compute_rpg360_anchor(
    cubemap_dir: Path,
    sparse_model: dict,
    output_dir: Path,
    config: Stage04Config,
) -> np.ndarray | None:
    """Compute the RPG360 anchor depth map for alignment refinement.

    Runs the RPG360 cubemap-face depth pipeline and returns the resulting
    ERP depth map as an anchor.

    Args:
        cubemap_dir: Directory with cubemap face images.
        sparse_model: COLMAP sparse model dict.
        output_dir: Output directory (for intermediate files).
        config: Stage04Config.

    Returns:
        ERP anchor depth map, or None if computation fails.
    """
    try:
        from sphereforge.stages.stage04_depth.rpg360_pipeline import (
            rpg360_depth_pipeline,
        )

        # Look for the first set of cubemap faces
        face_images = []
        face_directions = ["front", "right", "back", "left", "top", "bottom"]

        for direction in face_directions:
            # Try common naming patterns
            candidates = list(cubemap_dir.glob(f"*{direction}*"))
            if candidates:
                face_images.append(read_image(candidates[0]))
            else:
                logger.warning(
                    "No cubemap face image found for direction '%s' "
                    "in %s; skipping RPG360 anchor computation.",
                    direction,
                    cubemap_dir,
                )
                return None

        if len(face_images) != 6:
            logger.warning(
                "Expected 6 cubemap faces, found %d; "
                "skipping RPG360 anchor computation.",
                len(face_images),
            )
            return None

        # Determine ERP dimensions from the first frame's camera
        # Use a reasonable default
        erp_h = 512
        erp_w = 1024
        if sparse_model.get("cameras"):
            first_cam = next(iter(sparse_model["cameras"].values()))
            erp_w = first_cam.get("width", 1024)
            erp_h = first_cam.get("height", 512)

        anchor = rpg360_depth_pipeline(
            images=face_images,
            face_directions=face_directions,
            erp_height=erp_h,
            erp_width=erp_w,
            model_name=config.rpg360_perspective_model,
        )

        # Save anchor for potential reuse
        anchor_path = output_dir / "rpg360_anchor_depth.npy"
        write_depth(anchor_path, anchor)

        logger.info("RPG360 anchor depth computed and saved to %s", anchor_path)
        return anchor

    except Exception as exc:
        logger.warning(
            "Failed to compute RPG360 anchor: %s. "
            "Continuing without anchor refinement.",
            exc,
        )
        return None


def _refine_remaining_frames(
    depth_paths: list[Path],
    rpg360_anchor: np.ndarray,
    output_dir: Path,
    frame_paths: list[Path],
) -> None:
    """Refine remaining frames' depth with RPG360 anchor.

    Re-reads depth maps from disk (skipping the first which was already
    refined), blends with the anchor, and re-writes.

    Args:
        depth_paths: Paths to all depth maps (first already refined).
        rpg360_anchor: RPG360 anchor depth map.
        output_dir: Output directory.
        frame_paths: Original frame image paths.
    """
    from sphereforge.stages.stage04_depth.depth_alignment import _refine_with_anchor

    for i in range(1, len(depth_paths)):
        try:
            depth = read_depth(depth_paths[i])
            if depth.shape == rpg360_anchor.shape:
                refined = _refine_with_anchor(depth, rpg360_anchor)
                write_depth(depth_paths[i], refined)
                logger.debug("Refined frame %d with RPG360 anchor", i)
        except Exception as exc:
            logger.warning(
                "Failed to refine frame %d with RPG360 anchor: %s", i, exc
            )


def _apply_depth_clipping(
    depth_paths: list[Path],
    config: Stage04Config,
    scene_params: dict,
) -> None:
    """Apply near/far depth clipping based on config and scene parameters.

    Modifies depth maps in-place: values outside [near_clip, far_clip]
    are set to zero.

    Args:
        depth_paths: Paths to depth maps on disk.
        config: Stage04Config with ``depth_min`` and ``depth_max``.
        scene_params: Scene analysis dict with ``near_clip`` and ``far_clip``.
    """
    # Resolve near/far clip values
    near_clip = _resolve_clip_value(
        config.depth_min, scene_params.get("near_clip", 0.0), "near"
    )
    far_clip = _resolve_clip_value(
        config.depth_max, scene_params.get("far_clip", 1000.0), "far"
    )

    if near_clip <= 0 and far_clip <= 0:
        return  # No clipping needed

    for dp in depth_paths:
        try:
            depth = read_depth(dp)
            if near_clip > 0:
                depth[depth < near_clip] = 0.0
            if far_clip > 0:
                depth[depth > far_clip] = 0.0
            write_depth(dp, depth)
        except Exception as exc:
            logger.warning("Failed to clip depth at %s: %s", dp, exc)


def _resolve_clip_value(
    config_value: str,
    scene_value: float,
    clip_type: str,
) -> float:
    """Resolve a clip value from config ('auto' or numeric) and scene params.

    Args:
        config_value: Config value string — ``"auto"`` to use scene value,
            or a numeric string like ``"0.5"``.
        scene_value: Value from scene analysis (near_clip or far_clip).
        clip_type: ``"near"`` or ``"far"`` (for logging only).

    Returns:
        Resolved float value for the clipping plane.
    """
    if config_value == "auto":
        logger.debug("Using auto %s clip: %.2f", clip_type, scene_value)
        return scene_value

    try:
        val = float(config_value)
        logger.debug("Using config %s clip: %.2f", clip_type, val)
        return val
    except ValueError:
        logger.warning(
            "Invalid %s clip value '%s', falling back to scene value %.2f",
            clip_type,
            config_value,
            scene_value,
        )
        return scene_value


def _process_single_frame_stage04_worker(
    args: tuple[Path, int, Stage04Config, dict, Path, Path, np.ndarray | None],
) -> tuple[Path, np.ndarray, float, float, bool]:
    """Picklable wrapper for ``_process_single_frame_stage04``."""
    frame_path, frame_idx, config, sparse_model, cubemap_dir, output_dir, rpg360_anchor = args
    return _process_single_frame_stage04(
        frame_path, frame_idx, config, sparse_model, cubemap_dir, output_dir, rpg360_anchor
    )
