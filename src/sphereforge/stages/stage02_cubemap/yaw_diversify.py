"""Yaw diversification for cubemap extraction.

Applies a progressive yaw offset to cubemap crops across frames so that
consecutive frames do not all share the same set of viewing directions.
This increases multi-view coverage and improves COLMAP feature matching.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

from sphereforge.stages.stage02_cubemap.cubemap import CUBEMAP_FACES

if TYPE_CHECKING:
    from sphereforge.config import Stage02Config

logger = logging.getLogger("sphereforge.stage02.yaw_diversify")


def apply_yaw_offset(frame_index: int, yaw_offset_step: int = 30) -> float:
    """Compute the progressive yaw offset for a given frame index.

    The offset cycles through multiples of *yaw_offset_step* modulo 360°,
    so every group of ``360 / yaw_offset_step`` frames covers a full
    circle of yaw offsets before repeating.

    Args:
        frame_index: Zero-based index of the current frame.
        yaw_offset_step: Degrees of yaw increment per frame group.

    Returns:
        Yaw offset in degrees (float) to apply before cubemap extraction.
    """
    offset = (frame_index * yaw_offset_step) % 360
    logger.debug("Frame %d → yaw offset %.1f°", frame_index, offset)
    return float(offset)


def extract_diversified_cubemaps(
    erp_image: np.ndarray,
    frame_index: int,
    config: Stage02Config,
) -> list[tuple[np.ndarray, str, float, float]]:
    """Extract cubemap crops with a yaw offset determined by the frame index.

    Each cubemap face's nominal yaw is shifted by the computed offset before
    extraction, so consecutive frames observe the scene from rotated viewing
    directions.

    Args:
        erp_image: Equirectangular image as (H, W, C) uint8 array.
        frame_index: Zero-based frame index used to compute the yaw offset.
        config: Stage02 configuration (used for fov, overlap, n_faces,
            yaw_offset_step).

    Returns:
        List of ``(crop_image, face_name, yaw_deg, pitch_deg)`` tuples.
        The ``yaw_deg`` values already include the diversification offset.
    """
    yaw_offset = apply_yaw_offset(frame_index, config.yaw_offset_step)

    # We first extract cubemaps without yaw offset, then we need to
    # re-extract with offset.  The simplest correct approach is to
    # manually call extract_cubemap with modified face definitions that
    # incorporate the yaw offset.
    n_faces = min(config.n_faces, len(CUBEMAP_FACES))

    # Build modified face list with yaw offset applied
    offset_faces: list[tuple[str, float, float]] = []
    for i in range(n_faces):
        name, base_yaw, base_pitch = CUBEMAP_FACES[i]
        offset_faces.append((name, base_yaw + yaw_offset, base_pitch))

    # We call extract_cubemap with the default faces first to get crops,
    # but we need to use offset yaws.  Since extract_cubemap uses the
    # CUBEMAP_FACES list internally, we temporarily override it.
    # A cleaner approach: extract directly with offset.

    # Actually, extract_cubemap takes the faces from CUBEMAP_FACES constant.
    # Let's create a more flexible approach by calling extract_cubemap with
    # the offset applied to each face individually.

    results: list[tuple[np.ndarray, str, float, float]] = []
    total_fov = config.fov + config.overlap

    for face_name, face_yaw, face_pitch in offset_faces:
        crop = _extract_single_face(
            erp_image,
            face_yaw=face_yaw,
            face_pitch=face_pitch,
            total_fov=total_fov,
        )
        results.append((crop, face_name, face_yaw, face_pitch))

    logger.info(
        "Extracted %d diversified cubemaps for frame %d (yaw offset=%.1f°)",
        len(results),
        frame_index,
        yaw_offset,
    )
    return results


def _extract_single_face(
    erp_image: np.ndarray,
    face_yaw: float,
    face_pitch: float,
    total_fov: int,
) -> np.ndarray:
    """Extract a single cubemap face crop from an ERP image.

    Args:
        erp_image: Equirectangular image as (H, W, C) uint8 array.
        face_yaw: Yaw angle of the face centre in degrees.
        face_pitch: Pitch angle of the face centre in degrees.
        total_fov: Total field of view (fov + overlap) in degrees.

    Returns:
        Crop image as a numpy array.
    """
    import math

    import cv2

    erp_h, erp_w = erp_image.shape[:2]
    render_res = max(256, int(erp_w / 4 * total_fov / 90))

    focal = render_res / (2.0 * math.tan(math.radians(total_fov) / 2.0))
    cx_out = render_res / 2.0
    cy_out = render_res / 2.0

    # Build rotation matrix for this face
    yaw_rad = math.radians(face_yaw)
    pitch_rad = math.radians(face_pitch)

    cy, sy = math.cos(yaw_rad), math.sin(yaw_rad)
    ry = np.array(
        [[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]], dtype=np.float64
    )
    cp, sp = math.cos(pitch_rad), math.sin(pitch_rad)
    rx = np.array(
        [[1.0, 0.0, 0.0], [0.0, cp, -sp], [0.0, sp, cp]], dtype=np.float64
    )
    R = rx @ ry

    # Pixel grid
    u_coords = np.arange(render_res, dtype=np.float64)
    v_coords = np.arange(render_res, dtype=np.float64)
    uu, vv = np.meshgrid(u_coords, v_coords)

    dx = (uu - cx_out) / focal
    dy = (vv - cy_out) / focal
    dz = np.ones_like(dx)

    norms = np.sqrt(dx * dx + dy * dy + dz * dz)
    dx /= norms
    dy /= norms
    dz /= norms

    dirs_cam = np.stack([dx, dy, dz], axis=-1)

    # cam->world = R^T
    R_inv = R.T
    dirs_world = np.einsum("ij,...j->...i", R_inv, dirs_cam)

    # Direction to ERP coordinates
    x = dirs_world[..., 0]
    y = dirs_world[..., 1]
    z = dirs_world[..., 2]

    phi = np.arctan2(x, -z)
    theta = np.arcsin(np.clip(y, -1.0, 1.0))

    erp_u = (phi + math.pi) / (2.0 * math.pi) * erp_w
    erp_v = (math.pi / 2.0 - theta) / math.pi * erp_h

    map_x = erp_u.astype(np.float32)
    map_y = erp_v.astype(np.float32)

    crop = cv2.remap(
        erp_image,
        map_x,
        map_y,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_WRAP,
    )

    return crop
