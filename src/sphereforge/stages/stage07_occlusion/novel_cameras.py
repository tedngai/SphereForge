"""Novel camera generation for occlusion-recovery rendering.

Generates camera positions arranged around the scene center at multiple
distances and equally-spaced azimuth angles. Each camera looks at the scene
center, producing a full spherical sampling of viewpoints for hole detection
and inpainting.
"""

from __future__ import annotations

import logging
import math

import numpy as np

logger = logging.getLogger("sphereforge.stage07.novel_cameras")


def generate_novel_cameras(
    scene_center: np.ndarray,
    scene_radius: float,
    n_directions: int = 12,
    n_distances: int = 3,
    extra_views: list[dict] | None = None,
) -> list[dict]:
    """Generate novel camera positions arranged around the scene.

    Cameras are placed at *n_directions* equally-spaced azimuth angles, each
    at *n_distances* radial distances (0.5x, 1.0x, 1.5x scene_radius). Every
    camera looks at ``scene_center``. The up-vector is chosen so that cameras
    near the poles do not flip (we use a world-up of +Z).

    Args:
        scene_center: 3-element array — the centre of the scene (x, y, z).
        scene_radius: Scalar radius bounding the scene geometry.
        n_directions: Number of equally-spaced azimuth directions (default 12).
        n_distances: Number of distance rings (default 3). The multipliers are
            fixed at [0.5, 1.0, 1.5] regardless of this value; the parameter
            is kept for API compatibility and future extension.
        extra_views: Optional list of additional view dicts to append. Each
            dict must contain a ``viewmat`` key with a 4x4 numpy array.

    Returns:
        List of dicts, each with keys:
        - ``viewmat`` (np.ndarray): 4x4 world-to-camera matrix.
        - ``fov`` (float): Horizontal field of view in degrees (90).
        - ``height`` (int): Render height in pixels (1024).
        - ``width`` (int): Render width in pixels (1024).
    """
    scene_center = np.asarray(scene_center, dtype=np.float64).reshape(3)

    distance_multipliers = [0.5, 1.0, 1.5]
    # Respect n_distances if caller requests fewer rings
    distance_multipliers = distance_multipliers[:n_distances]

    cameras: list[dict] = []
    for _d_idx, d_mult in enumerate(distance_multipliers):
        distance = d_mult * scene_radius
        for a_idx in range(n_directions):
            azimuth = 2.0 * math.pi * a_idx / n_directions
            # Place cameras in the XZ plane (Y-up convention would use XY;
            # we use Z-up to match COLMAP/SfM defaults for 360 capture).
            cam_x = scene_center[0] + distance * math.cos(azimuth)
            cam_z = scene_center[2] + distance * math.sin(azimuth)
            cam_y = scene_center[1]  # same height as scene centre

            cam_pos = np.array([cam_x, cam_y, cam_z], dtype=np.float64)

            # Build view matrix (world-to-camera).
            # forward = normalize(centre - position)
            forward = scene_center - cam_pos
            forward = forward / (np.linalg.norm(forward) + 1e-12)

            # World-up is +Y
            world_up = np.array([0.0, 1.0, 0.0], dtype=np.float64)

            # right = normalize(up x forward) — but handle degenerate case
            # when forward is nearly parallel to world_up
            if abs(np.dot(forward, world_up)) > 0.999:
                world_up = np.array([0.0, 0.0, 1.0], dtype=np.float64)

            right = np.cross(world_up, forward)
            right = right / (np.linalg.norm(right) + 1e-12)

            up = np.cross(forward, right)
            up = up / (np.linalg.norm(up) + 1e-12)

            # View matrix: [right; up; -forward] stacked, then translation
            viewmat = np.eye(4, dtype=np.float64)
            viewmat[0, :3] = right
            viewmat[1, :3] = up
            viewmat[2, :3] = -forward
            viewmat[0, 3] = -np.dot(right, cam_pos)
            viewmat[1, 3] = -np.dot(up, cam_pos)
            viewmat[2, 3] = np.dot(forward, cam_pos)

            cameras.append(
                {
                    "viewmat": viewmat.astype(np.float32),
                    "fov": 90.0,
                    "height": 1024,
                    "width": 1024,
                }
            )

    logger.info(
        "Generated %d novel cameras (%d directions x %d distances)",
        len(cameras),
        n_directions,
        len(distance_multipliers),
    )

    if extra_views:
        for ev in extra_views:
            if "viewmat" not in ev:
                logger.warning("Skipping extra view without 'viewmat' key")
                continue
            cameras.append(ev)
        logger.info("Added %d extra views, total cameras: %d", len(extra_views), len(cameras))

    return cameras
