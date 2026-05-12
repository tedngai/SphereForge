"""Camera intrinsics computation for PINHOLE model.

Computes the focal length and principal point for the perspective crops
extracted from equirectangular images, using the standard PINHOLE camera
model expected by COLMAP.
"""

from __future__ import annotations

import logging
import math

logger = logging.getLogger("sphereforge.stage02.intrinsics")


def compute_intrinsics(
    crop_resolution: int,
    source_width: int,
    source_height: int,
    fov: float,
) -> dict:
    """Compute PINHOLE camera model intrinsics for a cubemap crop.

    For a perspective camera with a square sensor of resolution R and
    horizontal field of view *fov*, the focal length is::

        f = R / (2 * tan(fov / 2))

    and the principal point is at the image centre ``(R/2, R/2)``.

    Args:
        crop_resolution: Output crop size in pixels (width = height = R).
        source_width: Width of the source equirectangular image (unused
            for the PINHOLE model but recorded for provenance).
        source_height: Height of the source equirectangular image (unused
            for the PINHOLE model but recorded for provenance).
        fov: Horizontal field of view in degrees for the crop.

    Returns:
        Dict with keys: ``camera_id`` (int), ``model`` (str), ``width``
        (int), ``height`` (int), ``params`` (list of float).  The params
        list is ``[fx, fy, cx, cy]`` in COLMAP PINHOLE convention.
    """
    fov_rad = math.radians(fov)
    fx = crop_resolution / (2.0 * math.tan(fov_rad / 2.0))
    fy = fx  # square pixels, square crop
    cx = crop_resolution / 2.0
    cy = crop_resolution / 2.0

    result = {
        "camera_id": 1,
        "model": "PINHOLE",
        "width": crop_resolution,
        "height": crop_resolution,
        "params": [fx, fy, cx, cy],
    }

    logger.debug(
        "Computed intrinsics: fx=%.2f, fy=%.2f, cx=%.2f, cy=%.2f "
        "(crop_res=%d, fov=%.1f°)",
        fx,
        fy,
        cx,
        cy,
        crop_resolution,
        fov,
    )

    return result
