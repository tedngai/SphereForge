"""Panorama-rig virtual camera generation for Stage 2.

Builds a fixed set of virtual perspective cameras from an ERP panorama,
following the general layout used by COLMAP's panorama example.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from sphereforge.stages.stage02_cubemap.cubemap import (
    _make_rotation_matrix,
    extract_perspective_view,
)

if TYPE_CHECKING:
    from sphereforge.config import Stage02Config


@dataclass(frozen=True)
class PanoramaRigCamera:
    """A fixed virtual camera in the panorama rig."""

    name: str
    yaw_deg: float
    pitch_deg: float
    camera_id: int


def build_panorama_rig_cameras(config: Stage02Config) -> list[PanoramaRigCamera]:
    """Create fixed virtual-camera definitions for panorama-rig extraction."""
    cameras: list[PanoramaRigCamera] = []
    yaws = [360.0 * idx / config.rig_yaw_steps for idx in range(config.rig_yaw_steps)]

    camera_id = 1
    for pitch_deg in config.rig_pitch_angles:
        yaw_offset = 180.0 / config.rig_yaw_steps if pitch_deg > 0 else 0.0
        for yaw_deg in yaws:
            cameras.append(
                PanoramaRigCamera(
                    name=f"pano_camera{camera_id - 1:02d}",
                    yaw_deg=yaw_deg + yaw_offset,
                    pitch_deg=float(pitch_deg),
                    camera_id=camera_id,
                )
            )
            camera_id += 1

    return cameras


def extract_panorama_rig_views(
    erp_image: np.ndarray,
    config: Stage02Config,
) -> list[tuple[np.ndarray, PanoramaRigCamera]]:
    """Render all fixed panorama-rig views from an ERP image."""
    total_fov = config.fov + config.overlap
    return [
        (
            extract_perspective_view(
                erp_image,
                yaw_deg=camera.yaw_deg,
                pitch_deg=camera.pitch_deg,
                fov_deg=total_fov,
            ),
            camera,
        )
        for camera in build_panorama_rig_cameras(config)
    ]


def _render_resolution(erp_width: int, fov_deg: float) -> int:
    """Compute the internal render resolution used for a perspective view."""
    return max(256, int(erp_width / 4 * fov_deg / 90))


def _camera_center_directions(cameras: list[PanoramaRigCamera]) -> np.ndarray:
    """Compute world-space forward directions for all rig cameras."""
    centers = []
    for camera in cameras:
        rotation = _make_rotation_matrix(camera.yaw_deg, camera.pitch_deg)
        centers.append(rotation.T @ np.array([0.0, 0.0, 1.0], dtype=np.float64))
    return np.stack(centers, axis=0)


def _view_rays_world(
    *,
    yaw_deg: float,
    pitch_deg: float,
    fov_deg: float,
    erp_width: int,
) -> np.ndarray:
    """Return unit world rays for each pixel in a virtual perspective view."""
    render_res = _render_resolution(erp_width, fov_deg)
    focal = render_res / (2.0 * np.tan(np.deg2rad(fov_deg) / 2.0))
    center = render_res / 2.0

    u_coords = np.arange(render_res, dtype=np.float64)
    v_coords = np.arange(render_res, dtype=np.float64)
    uu, vv = np.meshgrid(u_coords, v_coords)

    dx = (uu - center) / focal
    dy = (vv - center) / focal
    dz = np.ones_like(dx)
    norms = np.sqrt(dx * dx + dy * dy + dz * dz)
    dirs_cam = np.stack([dx / norms, dy / norms, dz / norms], axis=-1)

    rotation = _make_rotation_matrix(yaw_deg, pitch_deg)
    return np.einsum("ij,...j->...i", rotation.T, dirs_cam)


def compute_panorama_rig_assignment_masks(
    erp_image: np.ndarray,
    config: Stage02Config,
) -> list[tuple[PanoramaRigCamera, np.ndarray]]:
    """Assign each panorama pixel to the nearest virtual camera center."""
    cameras = build_panorama_rig_cameras(config)
    total_fov = config.fov + config.overlap
    center_directions = _camera_center_directions(cameras)

    outputs: list[tuple[PanoramaRigCamera, np.ndarray]] = []
    for camera_idx, camera in enumerate(cameras):
        rays_world = _view_rays_world(
            yaw_deg=camera.yaw_deg,
            pitch_deg=camera.pitch_deg,
            fov_deg=total_fov,
            erp_width=erp_image.shape[1],
        )
        scores = rays_world @ center_directions.T
        closest_camera = np.argmax(scores, axis=-1)
        mask = np.zeros(closest_camera.shape, dtype=np.uint8)
        if config.rig_assignment_margin_deg <= 0:
            mask[closest_camera != camera_idx] = 255
        else:
            best_scores = np.take_along_axis(scores, closest_camera[..., None], axis=-1)[..., 0]
            own_scores = scores[..., camera_idx]
            best_angles = np.degrees(np.arccos(np.clip(best_scores, -1.0, 1.0)))
            own_angles = np.degrees(np.arccos(np.clip(own_scores, -1.0, 1.0)))
            keep = own_angles <= (best_angles + float(config.rig_assignment_margin_deg))
            mask[~keep] = 255
        outputs.append((camera, mask))

    return outputs
