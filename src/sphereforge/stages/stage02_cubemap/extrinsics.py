"""Camera extrinsics computation for cubemap faces.

Derives the quaternion and translation for each cubemap face direction,
optionally applying a yaw rotation to diversify multi-view coverage
across frames.
"""

from __future__ import annotations

import logging
import math

import numpy as np

from sphereforge.common.colmap_helpers import rotation_matrix_to_quat

logger = logging.getLogger("sphereforge.stage02.extrinsics")

# Face name → view direction (the direction the camera looks towards)
# in the world coordinate system.
# Convention: X=right, Y=down, Z=forward (OpenCV / COLMAP standard).
#   front  → (0,  0, -1)  looking along -Z
#   right  → (1,  0,  0)  looking along +X
#   back   → (0,  0,  1)  looking along +Z
#   left   → (-1, 0,  0)  looking along -X
#   top    → (0, -1,  0)  looking along -Y (up)
#   bottom → (0,  1,  0)  looking along +Y (down)
FACE_DIRECTIONS: dict[str, tuple[float, float, float]] = {
    "front": (0.0, 0.0, -1.0),
    "right": (1.0, 0.0, 0.0),
    "back": (0.0, 0.0, 1.0),
    "left": (-1.0, 0.0, 0.0),
    "top": (0.0, -1.0, 0.0),
    "bottom": (0.0, 1.0, 0.0),
}


def _look_at_rotation(
    forward: tuple[float, float, float],
    up: tuple[float, float, float] = (0.0, -1.0, 0.0),
) -> np.ndarray:
    """Compute a 3x3 rotation matrix for a camera looking in *forward* direction.

    The rotation is constructed so that:
    - The camera Z axis (forward) points along *forward*.
    - The camera Y axis (down) is as close to *up* as possible.
    - The camera X axis (right) completes the orthonormal basis.

    Args:
        forward: The desired look direction as (x, y, z).
        up: The world up direction as (x, y, z).

    Returns:
        3x3 rotation matrix mapping from camera frame to world frame.
    """
    fwd = np.array(forward, dtype=np.float64)
    fwd /= np.linalg.norm(fwd)

    up_vec = np.array(up, dtype=np.float64)

    # Handle the degenerate case where forward ≈ up
    if abs(np.dot(fwd, up_vec)) > 0.999:
        # Pick an arbitrary orthogonal direction as up
        up_vec = np.array([1.0, 0.0, 0.0])
        if abs(np.dot(fwd, up_vec)) > 0.999:
            up_vec = np.array([0.0, 1.0, 0.0])

    right = np.cross(up_vec, fwd)
    right /= np.linalg.norm(right)

    # Recompute up to ensure orthogonality
    down = np.cross(fwd, right)
    down /= np.linalg.norm(down)

    # COLMAP convention: columns are the camera axes expressed in world coords
    # R = [right | down | forward]  →  R maps cam→world
    # But COLMAP stores R such that world_point_cam = R @ world_point_world + t
    # i.e. R is world→cam. So we need R = [right; down; forward]^T
    R = np.stack([right, down, fwd], axis=0)

    return R


def _yaw_rotation_matrix(yaw_deg: float) -> np.ndarray:
    """Build a 3x3 rotation matrix for a yaw rotation about the Y axis.

    In the OpenCV/COLMAP convention (Y-down), a positive yaw rotates
    the view direction from -Z towards +X.

    Args:
        yaw_deg: Yaw angle in degrees.

    Returns:
        3x3 rotation matrix.
    """
    yaw_rad = math.radians(yaw_deg)
    cy, sy = math.cos(yaw_rad), math.sin(yaw_rad)
    # Rotation about Y axis (Y-down convention)
    R_yaw = np.array(
        [
            [cy, 0.0, sy],
            [0.0, 1.0, 0.0],
            [-sy, 0.0, cy],
        ],
        dtype=np.float64,
    )
    return R_yaw


def compute_extrinsics(
    face_name: str,
    yaw_offset: float = 0.0,
    image_id: int = 1,
    camera_id: int = 1,
) -> dict:
    """Compute extrinsic parameters for a cubemap face camera.

    Builds a world-to-camera rotation from the face's look direction,
    applies a yaw offset, and returns the quaternion (qw, qx, qy, qz)
    and translation (tx, ty, tz).  The camera is placed at the origin
    so the translation is always ``(0, 0, 0)``.

    Args:
        face_name: One of ``"front"``, ``"right"``, ``"back"``, ``"left"``,
            ``"top"``, ``"bottom"``.
        yaw_offset: Additional yaw rotation in degrees applied before the
            face direction (used for diversification).
        image_id: COLMAP image ID (default 1).
        camera_id: COLMAP camera ID (default 1).

    Returns:
        Dict with keys: ``qw``, ``qx``, ``qy``, ``qz``, ``tx``, ``ty``,
        ``tz``, ``camera_id``, ``image_id``, ``name``.

    Raises:
        ValueError: If *face_name* is not a recognised face direction.
    """
    if face_name not in FACE_DIRECTIONS:
        raise ValueError(
            f"Unknown face name '{face_name}'. "
            f"Expected one of: {list(FACE_DIRECTIONS.keys())}"
        )

    forward = FACE_DIRECTIONS[face_name]

    # Base rotation for this face (world→cam)
    R_face = _look_at_rotation(forward)

    # Apply yaw offset (diversification): rotate the world around Y
    # before transforming into the camera frame.
    # New R = R_face @ R_yaw
    if abs(yaw_offset) > 1e-9:
        R_yaw = _yaw_rotation_matrix(yaw_offset)
        R_total = R_face @ R_yaw
    else:
        R_total = R_face

    # Convert to quaternion
    qw, qx, qy, qz = rotation_matrix_to_quat(R_total)

    # Translation: camera at origin
    tx, ty, tz = 0.0, 0.0, 0.0

    result = {
        "qw": qw,
        "qx": qx,
        "qy": qy,
        "qz": qz,
        "tx": tx,
        "ty": ty,
        "tz": tz,
        "camera_id": camera_id,
        "image_id": image_id,
        "name": face_name,
    }

    logger.debug(
        "Extrinsics for '%s' (yaw_offset=%.1f): qw=%.4f qx=%.4f qy=%.4f qz=%.4f",
        face_name,
        yaw_offset,
        qw,
        qx,
        qy,
        qz,
    )

    return result
