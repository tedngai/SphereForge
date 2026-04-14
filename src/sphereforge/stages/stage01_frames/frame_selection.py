"""Frame selection: keep the sharpest frame per chunk.

Divides a list of frame paths into fixed-size chunks and retains only the
sharpest frame from each chunk, using :func:`compute_sharpness` backed by
:class:`~sphereforge.stages.stage01_frames.sharpness_cache.SharpnessCache`.
"""

from __future__ import annotations

import logging
from pathlib import Path

from sphereforge.common.io import read_image
from sphereforge.stages.stage01_frames.sharpness import compute_sharpness
from sphereforge.stages.stage01_frames.sharpness_cache import SharpnessCache

logger = logging.getLogger(__name__)


def select_sharpest_per_chunk(
    frame_paths: list[Path],
    chunk_size: int,
    cache: SharpnessCache,
) -> list[Path]:
    """Select the sharpest frame from each fixed-size chunk.

    The list of *frame_paths* is split into consecutive chunks of
    *chunk_size* frames (the last chunk may be smaller).  Within each
    chunk the frame with the highest sharpness score (variance of the
    Laplacian) is kept.  Sharpness scores are cached so that re-runs
    avoid redundant computation.

    Args:
        frame_paths: Ordered list of paths to candidate frame images.
        chunk_size: Number of frames per chunk.  Must be ≥ 1.
        cache: A :class:`SharpnessCache` instance for memoising sharpness
            scores across runs.

    Returns:
        List of Paths to the selected (sharpest) frames, one per chunk,
        preserving the original order.
    """
    if chunk_size < 1:
        raise ValueError(f"chunk_size must be ≥ 1, got {chunk_size}")

    if not frame_paths:
        logger.warning("select_sharpest_per_chunk called with empty frame list")
        return []

    selected: list[Path] = []

    for chunk_start in range(0, len(frame_paths), chunk_size):
        chunk = frame_paths[chunk_start : chunk_start + chunk_size]
        best_path: Path | None = None
        best_score: float = -1.0

        for fp in chunk:
            # Try cache first
            cached_score = cache.get(fp)
            if cached_score is not None:
                score = cached_score
                logger.debug("Cache hit for %s: %.4f", fp, score)
            else:
                image = read_image(fp)
                score = compute_sharpness(image)
                cache.set(fp, score)
                logger.debug("Computed sharpness for %s: %.4f", fp, score)

            if score > best_score:
                best_score = score
                best_path = fp

        if best_path is not None:
            selected.append(best_path)
            logger.debug(
                "Chunk [%d:%d] → %s (sharpness=%.4f)",
                chunk_start,
                chunk_start + len(chunk),
                best_path.name,
                best_score,
            )

    logger.info(
        "Selected %d frames from %d total (%d chunks of size %d)",
        len(selected),
        len(frame_paths),
        (len(frame_paths) + chunk_size - 1) // chunk_size,
        chunk_size,
    )
    return selected