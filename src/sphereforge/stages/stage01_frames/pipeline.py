"""Stage 1 pipeline: Video Ingestion & Frame Selection.

Orchestrates the full Stage 1 pipeline:
  1. Extract frames from the input video at the configured FPS.
  2. Select the sharpest frame per chunk (using a sharpness cache).
  3. Filter frames by luminance range.
  4. Copy surviving frames to the output directory.

The function returns the list of final selected frame paths.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from sphereforge.config import Stage01Config
from sphereforge.stages.stage01_frames.extract_frames import extract_frames
from sphereforge.stages.stage01_frames.frame_selection import (
    select_sharpest_per_chunk,
)
from sphereforge.stages.stage01_frames.luminance_filter import filter_frame_list
from sphereforge.stages.stage01_frames.sharpness_cache import SharpnessCache

logger = logging.getLogger("sphereforge.stage01.pipeline")


def run_stage01(
    config: Stage01Config,
    input_path: Path,
    output_dir: Path,
) -> list[Path]:
    """Run Stage 1: Video Ingestion & Frame Selection.

    Extracts frames from *input_path*, selects the sharpest per chunk,
    filters by luminance, and copies the final set to *output_dir*.

    Args:
        config: Stage01Config with ``input_fps``, ``chunk_size``,
            ``min_luminance``, and ``max_luminance``.
        input_path: Path to the input video file.
        output_dir: Destination directory for the selected frame images.

    Returns:
        Sorted list of Paths to the final selected frames in *output_dir*.
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ---- Step 1: Extract frames ------------------------------------------------
    logger.info("Step 1: Extracting frames from %s at %d fps", input_path, config.input_fps)
    frames_dir = output_dir / "_extracted"
    frame_paths = extract_frames(
        video_path=input_path,
        output_dir=frames_dir,
        fps=config.input_fps,
    )
    if not frame_paths:
        logger.warning("No frames extracted from %s", input_path)
        return []

    # ---- Step 2: Select sharpest per chunk -------------------------------------
    logger.info(
        "Step 2: Selecting sharpest frame per chunk (chunk_size=%d)",
        config.chunk_size,
    )
    cache_path = output_dir / "sharpness_cache.csv"
    cache = SharpnessCache(cache_path)
    selected = select_sharpest_per_chunk(frame_paths, config.chunk_size, cache)
    logger.info("Selected %d frames after chunk-based sharpness filtering", len(selected))

    # ---- Step 3: Filter by luminance -------------------------------------------
    logger.info(
        "Step 3: Filtering by luminance [%.1f, %.1f]",
        config.min_luminance,
        config.max_luminance,
    )
    filtered = filter_frame_list(
        selected,
        min_lum=config.min_luminance,
        max_lum=config.max_luminance,
    )
    logger.info("Retained %d frames after luminance filtering", len(filtered))

    # ---- Step 4: Copy to output directory --------------------------------------
    final_paths: list[Path] = []
    for src in filtered:
        dst = output_dir / src.name
        shutil.copy2(src, dst)
        final_paths.append(dst)

    logger.info(
        "Stage 1 complete: %d frames written to %s", len(final_paths), output_dir
    )

    return final_paths