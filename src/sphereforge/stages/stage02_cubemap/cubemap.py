"""Extract cubemap faces from equirectangular images via inverse warping.

For each cubemap face direction (front, right, back, left, top, bottom),
a perspective crop is extracted from the equirectangular image by computing
the direction vector for every pixel in the output crop and looking up the
corresponding ERP pixel.  Pole distortion is handled correctly by the
spherical coordinate conversion.
"""

from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING

import cv2
import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

logger = logging.getLogger("sphereforge.stage02.cubemap")

# Canonical cubemap face definitions: (face_name, yaw_deg, pitch_deg)
# Yaw: rotation around vertical axis (positive = look right from front)
# Pitch: elevation angle (positive = look up)
CUBEMAP_FACES: list[tuple[str, float, float]] = [
    ("front", 0.0, 0.0),
    ("right", 90.0, 0.0),
    ("back", 180.0, 0.0),
    ("left", -90.0, 0.0),
    ("top", 0.0, 90.0),
    ("bottom", 0.0, -90.0),
]


def _direction_to_erp_uv(
    directions: NDArray[np.float64],
    erp_width: int,
    erp_height: int,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Convert 3D direction vectors to equirectangular pixel coordinates.

    Args:
        directions: Array of shape (..., 3) with unit direction vectors.
        erp_width: Width of the equirectangular image in pixels.
        erp_height: Height of the equirectangular image in pixels.

    Returns:
        Tuple of (u, v) coordinate arrays, each of shape (...,),
        in equirectangular pixel space.
    """
    x = directions[..., 0]
    y = directions[..., 1]
    z = directions[..., 2]

    # Spherical coordinates from direction vector
    # longitude (phi) = atan2(x, -z) — COLMAP convention: front looks along -Z
    # latitude (theta) = asin(y)
    phi = np.arctan2(x, -z)  # longitude
    theta = np.arcsin(np.clip(y, -1.0, 1.0))  # latitude

    # Map to ERP pixel coordinates
    # u: longitude [-pi, pi] -> [0, width]
    # v: latitude [-pi/2, pi/2] -> [0, height]
    u = (phi + math.pi) / (2.0 * math.pi) * erp_width
    v = (math.pi / 2.0 - theta) / math.pi * erp_height

    return u, v


def _make_rotation_matrix(yaw_deg: float, pitch_deg: float) -> NDArray[np.float64]:
    """Build a 3x3 rotation matrix from yaw and pitch angles.

    The rotation order is: first yaw around Y, then pitch around X.
    This matches the convention where yaw rotates the view direction
    horizontally and pitch tilts it vertically.

    Args:
        yaw_deg: Yaw angle in degrees (rotation around Y axis).
        pitch_deg: Pitch angle in degrees (rotation around X axis).

    Returns:
        3x3 rotation matrix as float64 numpy array.
    """
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)

    # Rotation around Y axis (yaw)
    cy, sy = math.cos(yaw), math.sin(yaw)
    ry = np.array(
        [
            [cy, 0.0, sy],
            [0.0, 1.0, 0.0],
            [-sy, 0.0, cy],
        ],
        dtype=np.float64,
    )

    # Rotation around X axis (pitch)
    cp, sp = math.cos(pitch), math.sin(pitch)
    rx = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, cp, -sp],
            [0.0, sp, cp],
        ],
        dtype=np.float64,
    )

    return rx @ ry


def extract_cubemap(
    erp_image: np.ndarray,
    fov: int = 90,
    overlap: int = 15,
    n_faces: int = 6,
) -> list[tuple[np.ndarray, str, float, float]]:
    """Extract cubemap face crops from an equirectangular (ERP) image.

    For each of the *n_faces* cubemap directions, generates a perspective
    crop via inverse warping: every pixel in the output crop is back-projected
    to a 3D direction vector, rotated by the face's yaw/pitch, and then
    looked up in the ERP image.

    The effective field of view per crop is ``fov + overlap`` to provide
    boundary overlap between adjacent faces.

    Args:
        erp_image: Equirectangular image as an (H, W, C) uint8 array.
        fov: Base field of view per face in degrees (default 90).
        overlap: Extra overlap to add per face in degrees (default 15).
        n_faces: Number of faces to extract (default 6; max 6).

    Returns:
        List of ``(crop_image, face_name, yaw_deg, pitch_deg)`` tuples,
        one per cubemap face.  Each ``crop_image`` is a square
        ``crop_resolution x crop_resolution`` array derived from the
        effective FOV.

    Raises:
        ValueError: If *erp_image* has fewer than 3 dimensions.
    """
    if erp_image.ndim < 3:
        raise ValueError(
            f"Expected ERP image with shape (H, W, C), got {erp_image.shape}"
        )

    erp_h, erp_w = erp_image.shape[:2]
    total_fov = fov + overlap

    # Determine output resolution so that the base-fov portion maps to
    # the configured crop resolution.  The crop_resolution pixels span the
    # total_fov, but we want the central fov portion to correspond to
    # crop_resolution pixels in the final output.
    scale = total_fov / fov
    render_res = math.ceil(scale * erp_w / 4)  # reasonable default
    # We'll compute at render_res and then resize to crop_resolution later.
    # Actually, let's use a fixed approach: render at a resolution that
    # covers the total_fov, then the crop_resolution is the output size.
    render_res = max(256, int(erp_w / 4 * scale))

    focal = render_res / (2.0 * math.tan(math.radians(total_fov) / 2.0))
    cx_out = render_res / 2.0
    cy_out = render_res / 2.0

    results: list[tuple[np.ndarray, str, float, float]] = []
    faces_to_process = CUBEMAP_FACES[:n_faces]

    logger.info(
        "Extracting %d cubemap faces (fov=%d, overlap=%d, total_fov=%d, "
        "render_res=%d) from ERP (%dx%d)",
        n_faces,
        fov,
        overlap,
        total_fov,
        render_res,
        erp_w,
        erp_h,
    )

    for face_name, face_yaw, face_pitch in faces_to_process:
        # Build rotation that takes the face's view direction to the front
        R = _make_rotation_matrix(face_yaw, face_pitch)

        # Create pixel coordinate grid for the output crop
        # Pixel (u, v) maps to direction:
        #   d_cam = [(u - cx) / focal, (v - cy) / focal, 1.0]
        # then rotate to world: d_world = R^T @ d_cam  (since R rotates
        # world->cam, we need cam->world = R^T)
        u_coords = np.arange(render_res, dtype=np.float64)
        v_coords = np.arange(render_res, dtype=np.float64)
        uu, vv = np.meshgrid(u_coords, v_coords)

        # Direction vectors in camera frame
        dx = (uu - cx_out) / focal
        dy = (vv - cy_out) / focal
        dz = np.ones_like(dx)

        # Normalise to unit vectors
        norms = np.sqrt(dx * dx + dy * dy + dz * dz)
        dx /= norms
        dy /= norms
        dz /= norms

        # Stack into (render_res, render_res, 3)
        dirs_cam = np.stack([dx, dy, dz], axis=-1)

        # Rotate to world frame: R^T @ d_cam
        # R is world->cam rotation; we want cam->world so use R^T
        R_inv = R.T  # cam->world
        dirs_world = np.einsum("ij,...j->...i", R_inv, dirs_cam)

        # Convert world directions to ERP pixel coordinates
        erp_u, erp_v = _direction_to_erp_uv(dirs_world, erp_w, erp_h)

        # Remap using OpenCV
        map_x = erp_u.astype(np.float32)
        map_y = erp_v.astype(np.float32)

        # Handle boundary: wrap horizontally (ERP is 360° wrap-around)
        # Use BORDER_WRAP for horizontal, BORDER_REFLECT for vertical
        crop = cv2.remap(
            erp_image,
            map_x,
            map_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_WRAP,
        )

        logger.debug(
            "Extracted face '%s' (yaw=%.1f, pitch=%.1f), crop shape %s",
            face_name,
            face_yaw,
            face_pitch,
            crop.shape,
        )
        results.append((crop, face_name, face_yaw, face_pitch))

    return results
