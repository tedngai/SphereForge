"""Projection helpers for Stage 7 occlusion recovery.

Stage 7 mixes novel cameras generated in an OpenGL-style convention
(-Z forward) with simpler pinhole projection code that expects +Z forward.
These helpers normalize depth handling so both conventions project
consistently.
"""

from __future__ import annotations

import numpy as np


def world_to_camera_with_positive_depth(
    positions: np.ndarray,
    viewmat: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Transform world points to camera space with a positive forward depth.

    Args:
        positions: World-space points of shape ``(N, 3)``.
        viewmat: 4x4 world-to-camera matrix.

    Returns:
        Tuple ``(camera_points, positive_depth, forward_sign)`` where:

        - ``camera_points`` is the raw transformed ``(N, 3)`` array.
        - ``positive_depth`` is a depth array where points in front of the
          camera are positive regardless of whether the camera uses +Z or -Z
          as its forward axis.
        - ``forward_sign`` is ``1.0`` for +Z-forward cameras and ``-1.0`` for
          -Z-forward cameras.
    """
    positions = np.asarray(positions, dtype=np.float32)
    viewmat = np.asarray(viewmat, dtype=np.float64)

    R = viewmat[:3, :3]
    t = viewmat[:3, 3]
    camera_points = (R @ positions.T + t[:, None]).T.astype(np.float32)

    positive = int(np.count_nonzero(camera_points[:, 2] > 1e-6))
    negative = int(np.count_nonzero(camera_points[:, 2] < -1e-6))
    forward_sign = -1.0 if negative > positive else 1.0
    positive_depth = camera_points[:, 2] * forward_sign
    return camera_points, positive_depth, forward_sign
