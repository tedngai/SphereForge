"""SphereForge test fixtures.

Provides synthetic test data for all pipeline stages: equirectangular images,
depth maps, COLMAP model files, and Gaussian Splat PLY data.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Synthetic image fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def synthetic_erp_image() -> np.ndarray:
    """A 512x1024 equirectangular RGB test image with gradient + checkerboard.

    Returns:
        HxWx3 uint8 array.
    """
    h, w = 512, 1024
    img = np.zeros((h, w, 3), dtype=np.uint8)

    # Horizontal gradient in red channel
    img[:, :, 0] = np.linspace(0, 255, w, dtype=np.uint8)[np.newaxis, :]

    # Vertical gradient in green channel
    img[:, :, 1] = np.linspace(0, 255, h, dtype=np.uint8)[:, np.newaxis]

    # Checkerboard in blue channel (32px squares)
    checker = np.indices((h, w)).sum(axis=0) // 32 % 2
    img[:, :, 2] = (checker * 255).astype(np.uint8)

    return img


@pytest.fixture
def synthetic_depth_map() -> np.ndarray:
    """A 512x1024 synthetic depth map for the ERP image.

    Simulates a room: walls at distance 5m, floor/ceiling at varying depth,
    and a close object (1m) in the center.

    Returns:
        HxW float32 array with depth in meters.
    """
    h, w = 512, 1024
    depth = np.full((h, w), 5.0, dtype=np.float32)

    # Floor gets closer toward the bottom
    for y in range(h):
        depth[y, :] = 3.0 + 4.0 * (y / h)

    # Close object in center (2m radius sphere)
    cy, cx = h // 2, w // 2
    yy, xx = np.mgrid[:h, :w]
    dist = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    mask = dist < 100
    depth[mask] = 1.0

    return depth


@pytest.fixture
def synthetic_cubemap_faces() -> list[np.ndarray]:
    """Six 256x256 perspective crop images (cubemap faces).

    Returns:
        List of 6 HxWx3 uint8 arrays (front, right, back, left, top, bottom).
    """
    faces = []
    colors = [
        (255, 0, 0),    # front  - red
        (0, 255, 0),    # right  - green
        (0, 0, 255),    # back   - blue
        (255, 255, 0),  # left   - yellow
        (255, 0, 255),  # top    - magenta
        (0, 255, 255),  # bottom - cyan
    ]
    for r, g, b in colors:
        face = np.full((256, 256, 3), [r, g, b], dtype=np.uint8)
        # Add some texture so it's not uniform
        noise = np.random.randint(0, 30, (256, 256, 3), dtype=np.uint8)
        face = np.clip(face.astype(np.int16) + noise.astype(np.int16), 0, 255).astype(np.uint8)
        faces.append(face)
    return faces


# ---------------------------------------------------------------------------
# Synthetic COLMAP fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def synthetic_colmap_cameras() -> dict[int, dict]:
    """Synthetic COLMAP cameras dict (2 PINHOLE cameras).

    Returns:
        Dict mapping camera_id -> {model, width, height, params}.
    """
    return {
        1: {"model": "PINHOLE", "width": 1024, "height": 512, "params": [512.0, 512.0, 512.0, 256.0]},
        2: {"model": "PINHOLE", "width": 1024, "height": 512, "params": [512.0, 512.0, 512.0, 256.0]},
    }


@pytest.fixture
def synthetic_colmap_images() -> dict[int, dict]:
    """Synthetic COLMAP images dict (3 images with identity/rotated poses).

    Returns:
        Dict mapping image_id -> {name, qw/qx/qy/qz, tx/ty/tz, camera_id, point3D_ids}.
    """
    return {
        1: {
            "name": "frame_000_front.png",
            "qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
            "tx": 0.0, "ty": 0.0, "tz": 0.0,
            "camera_id": 1,
            "point3D_ids": [1, 2, 3],
        },
        2: {
            "name": "frame_000_right.png",
            "qw": 0.7071, "qx": 0.0, "qy": -0.7071, "qz": 0.0,  # 90° yaw
            "tx": 0.0, "ty": 0.0, "tz": 0.0,
            "camera_id": 1,
            "point3D_ids": [2, 3, 4],
        },
        3: {
            "name": "frame_000_back.png",
            "qw": 0.0, "qx": 0.0, "qy": 1.0, "qz": 0.0,  # 180° yaw
            "tx": 0.0, "ty": 0.0, "tz": 0.0,
            "camera_id": 2,
            "point3D_ids": [3, 4],
        },
    }


@pytest.fixture
def synthetic_colmap_points3d() -> dict[int, dict]:
    """Synthetic COLMAP 3D points (4 points forming a small scene).

    Returns:
        Dict mapping point3D_id -> {x, y, z, r, g, b, error}.
    """
    return {
        1: {"x": -2.0, "y": 1.5, "z": 5.0, "r": 128, "g": 64, "b": 32, "error": 0.5},
        2: {"x": 0.0, "y": 1.5, "z": 5.0, "r": 200, "g": 100, "b": 50, "error": 0.3},
        3: {"x": 2.0, "y": 1.5, "z": 5.0, "r": 100, "g": 200, "b": 150, "error": 0.4},
        4: {"x": 0.0, "y": 0.0, "z": 3.0, "r": 50, "g": 50, "b": 200, "error": 0.2},
    }


@pytest.fixture
def synthetic_colmap_text_dir(
    tmp_path: Path,
    synthetic_colmap_cameras: dict,
    synthetic_colmap_images: dict,
    synthetic_colmap_points3d: dict,
) -> Path:
    """Write synthetic COLMAP text files to a temp directory.

    Returns:
        Path to directory containing cameras.txt, images.txt, points3D.txt.
    """
    from sphereforge.common.colmap_helpers import (
        write_cameras_txt,
        write_images_txt,
    )

    # Write cameras.txt
    cam_path = tmp_path / "cameras.txt"
    write_cameras_txt(cam_path, synthetic_colmap_cameras)

    # Write images.txt
    img_path = tmp_path / "images.txt"
    write_images_txt(img_path, synthetic_colmap_images)

    # Write points3D.txt manually
    pts_path = tmp_path / "points3D.txt"
    with open(pts_path, "w") as f:
        f.write("# 3D point list\n")
        for pid, pt in synthetic_colmap_points3d.items():
            f.write(f"{pid} {pt['x']} {pt['y']} {pt['z']} "
                    f"{pt['r']} {pt['g']} {pt['b']} {pt['error']}\n")

    return tmp_path


# ---------------------------------------------------------------------------
# Synthetic Gaussian Splat fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def synthetic_gaussians() -> dict[str, np.ndarray]:
    """Synthetic Gaussian Splat data (100 Gaussians).

    Returns:
        Dict with keys: positions (100x3), colors (100x3), opacities (100,),
        scales (100x3), rotations (100x4).
    """
    rng = np.random.RandomState(42)
    n = 100

    positions = rng.randn(n, 3).astype(np.float32) * 5.0
    colors = rng.randint(0, 256, (n, 3)).astype(np.uint8)
    opacities = rng.uniform(0.5, 1.0, (n,)).astype(np.float32)
    scales = np.exp(rng.randn(n, 3).astype(np.float32) * 0.5)
    rotations = np.zeros((n, 4), dtype=np.float32)
    rotations[:, 0] = 1.0  # Identity quaternion

    return {
        "positions": positions,
        "colors": colors,
        "opacities": opacities,
        "scales": scales,
        "rotations": rotations,
    }


# ---------------------------------------------------------------------------
# Temp directory fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Create a SphereForge data directory structure.

    Returns:
        Path to data/ with subdirs: raw, frames, cubemaps, colmap, depth,
        gaussians, optimized, refined, export.
    """
    subdirs = [
        "raw", "frames", "cubemaps", "cubemaps/masks",
        "colmap", "depth", "gaussians", "optimized", "refined", "export",
    ]
    for sub in subdirs:
        (tmp_path / sub).mkdir(parents=True, exist_ok=True)
    return tmp_path
