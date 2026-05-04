"""Integration test: stages 2 → 5 on a tiny synthetic dataset.

Creates 2 synthetic ERP frames (256×512), runs Stage 2 cubemap extraction,
fakes Stage 3 (sparse COLMAP model) and Stage 4 (depth maps), then runs
Stage 5 and asserts a valid PLY is produced.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest

from sphereforge.common.io import read_image, read_ply, write_image
from sphereforge.config import Stage02Config, Stage05Config
from sphereforge.stages.stage02_cubemap.pipeline import run_stage02
from sphereforge.stages.stage05_seeding.pipeline import run_stage05


def _make_synthetic_erp(h: int = 256, w: int = 512) -> np.ndarray:
    """Create a synthetic equirectangular image with a simple gradient."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    # Horizontal gradient in R, vertical in G
    img[:, :, 0] = np.linspace(0, 255, w, dtype=np.uint8)[None, :]
    img[:, :, 1] = np.linspace(0, 255, h, dtype=np.uint8)[:, None]
    img[:, :, 2] = 128
    return img


def _make_fake_depth(h: int = 256, w: int = 512) -> np.ndarray:
    """Create a fake metric depth map (radial fall-off from centre)."""
    yy, xx = np.ogrid[:h, :w]
    cy, cx = h / 2.0, w / 2.0
    dist = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    depth = 10.0 - dist / max(cy, cx) * 8.0
    return depth.astype(np.float32)


def test_stages_2_through_5_produce_valid_ply() -> None:
    """End-to-end smoke test for cubemap extraction → Gaussian seeding."""
    h, w = 256, 512
    n_frames = 2

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # ---- Stage 1 surrogate: write synthetic ERP frames ----
        frame_dir = tmpdir_path / "frames"
        frame_dir.mkdir()
        frame_paths: list[Path] = []
        for i in range(n_frames):
            path = frame_dir / f"frame_{i:03d}.png"
            write_image(path, _make_synthetic_erp(h, w))
            frame_paths.append(path)

        # ---- Stage 2: cubemap extraction ----
        stage02_config = Stage02Config(
            crop_size=512,
            crop_resolution=256,
            yaw_diversify=True,
            num_yaw_steps=2,
            generate_masks=False,  # skip YOLO dependency
        )
        cubemap_dir = tmpdir_path / "cubemaps"
        run_stage02(
            config=stage02_config,
            frame_paths=frame_paths,
            output_dir=cubemap_dir,
            num_workers=1,
        )

        # Verify Stage 2 outputs
        assert (cubemap_dir / "cameras.txt").exists()
        assert (cubemap_dir / "images.txt").exists()
        images_out = list((cubemap_dir / "images").glob("*.png"))
        assert len(images_out) > 0

        # ---- Stage 3 surrogate: fake sparse COLMAP model ----
        # One camera, one image per cubemap face
        sparse_model: dict = {
            "cameras": {
                1: {
                    "model": "PINHOLE",
                    "width": 256,
                    "height": 256,
                    "params": [300.0, 300.0, 128.0, 128.0],
                }
            },
            "images": {},
        }
        # Parse images.txt to get image names and assign dummy poses
        from sphereforge.common.colmap_helpers import parse_images_txt

        images_txt = cubemap_dir / "images.txt"
        parsed_images = parse_images_txt(images_txt)
        for img_id, img in parsed_images.items():
            sparse_model["images"][img_id] = {
                **img,
                "qw": 1.0,
                "qx": 0.0,
                "qy": 0.0,
                "qz": 0.0,
                "tx": 0.0,
                "ty": 0.0,
                "tz": 0.0,
                "camera_id": 1,
            }

        # ---- Stage 4 surrogate: write fake depth maps ----
        depth_dir = tmpdir_path / "depth"
        depth_dir.mkdir()
        depth_paths: list[Path] = []
        for i in range(n_frames):
            path = depth_dir / f"frame_{i:03d}_depth.npy"
            np.save(path, _make_fake_depth(h, w))
            depth_paths.append(path)

        # ---- Stage 5: Gaussian seeding ----
        stage05_config = Stage05Config(
            stride=4,
            cross_validate_depth=False,
            sky_threshold="auto",
            outlier_pruning=0,
            sparse_pruning=0,
        )
        scene_params = {"sky_depth": 15.0, "orbit_radius": 5.0}
        gaussian_dir = tmpdir_path / "gaussians"
        ply_path = run_stage05(
            config=stage05_config,
            frame_paths=frame_paths,
            depth_paths=depth_paths,
            sparse_model=sparse_model,
            scene_params=scene_params,
            output_dir=gaussian_dir,
            num_workers=1,
        )

        # ---- Assertions ----
        assert ply_path.exists(), f"PLY not found at {ply_path}"
        data = read_ply(ply_path)
        assert data["positions"].shape[0] > 0, "PLY has no Gaussians"
        assert data["positions"].shape[1] == 3
        assert data["colors"].shape[1] == 3
        assert data["opacities"].shape[0] == data["positions"].shape[0]
        assert data["scales"].shape == data["positions"].shape
        assert data["rotations"].shape == (data["positions"].shape[0], 4)
