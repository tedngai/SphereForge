"""Luminance-based frame filtering.

Provides functions to discard frames whose mean luminance falls outside a
configurable range, removing very dark or very bright (over-exposed) images
that would degrade 3D reconstruction quality.
"""

from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np

from sphereforge.common.io import read_image

logger = logging.getLogger(__name__)


def filter_by_luminance(
    image: np.ndarray,
    min_lum: float = 10.0,
    max_lum: float = 245.0,
) -> bool:
    """Check whether an image passes the luminance filter.

    Converts the image to grayscale (if needed), computes the mean pixel
    intensity, and returns ``True`` when the mean is within
    ``[min_lum, max_lum]``.

    Args:
        image: Input image as a NumPy array.  Can be grayscale ``(H, W)``
            or colour ``(H, W, 3)`` with dtype ``uint8``.
        min_lum: Minimum acceptable mean luminance.  Defaults to 10.0.
        max_lum: Maximum acceptable mean luminance.  Defaults to 245.0.

    Returns:
        ``True`` if the image passes the luminance filter (should be kept),
        ``False`` if it should be discarded.
    """
    # Convert to grayscale if needed
    if image.ndim == 3:
        if image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        elif image.shape[2] == 1:
            gray = image[:, :, 0]
        else:
            raise ValueError(
                f"Expected 1 or 3 channels, got {image.shape[2]}"
            )
    elif image.ndim == 2:
        gray = image
    else:
        raise ValueError(
            f"Expected 2D (grayscale) or 3D (colour) array, got {image.ndim}D"
        )

    mean_lum: float = float(gray.mean())
    passes = min_lum <= mean_lum <= max_lum

    if not passes:
        logger.debug(
            "Luminance filter: mean=%.1f not in [%.1f, %.1f] → discard",
            mean_lum,
            min_lum,
            max_lum,
        )

    return passes


def filter_frame_list(
    frame_paths: list[Path],
    min_lum: float = 10.0,
    max_lum: float = 245.0,
) -> list[Path]:
    """Filter a list of frame paths by luminance.

    Reads each image, checks its mean luminance, and keeps only those
    within ``[min_lum, max_lum]``.

    Args:
        frame_paths: List of paths to frame images.
        min_lum: Minimum acceptable mean luminance.  Defaults to 10.0.
        max_lum: Maximum acceptable mean luminance.  Defaults to 245.0.

    Returns:
        List of Paths that pass the luminance filter, preserving original
        order.
    """
    passed: list[Path] = []

    for fp in frame_paths:
        image = read_image(fp)
        if filter_by_luminance(image, min_lum, max_lum):
            passed.append(fp)
        else:
            logger.info("Discarding frame %s (luminance out of range)", fp.name)

    discarded = len(frame_paths) - len(passed)
    logger.info(
        "Luminance filter: %d passed, %d discarded out of %d frames",
        len(passed),
        discarded,
        len(frame_paths),
    )
    return passed