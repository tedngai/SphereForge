"""Tests for Stage 2: Equirect→Cubemap + COLMAP Prep (T2.1–T2.12).

Tests cover cubemap face extraction correctness, intrinsics computation,
extrinsics quaternion generation, yaw diversification, and mask generation.
"""

from __future__ import annotations

import math

import numpy as np
import pytest


# ==========================================================================
# T2.1 — Cubemap extraction
# ==========================================================================


class TestExtractCubemap:
    """Tests for extract_cubemap (T2.1)."""

    def test_extracts_six_faces(self) -> None:
        """Should return 6 crops for a standard cubemap."""
        from sphereforge.stages.stage02_cubemap.cubemap import extract_cubemap

        h, w = 64, 128
        erp = np.zeros((h, w, 3), dtype=np.uint8)
        crops = extract_cubemap(erp, fov=90)

        assert len(crops) == 6
        for crop, face_name, yaw, pitch in crops:
            assert crop.ndim == 3
            assert crop.shape[2] == 3
            assert face_name in {"front", "right", "back", "left", "top", "bottom"}

    def test_front_face_center_not_empty(self) -> None:
        """Front face should produce a non-empty crop."""
        from sphereforge.stages.stage02_cubemap.cubemap import extract_cubemap

        h, w = 64, 128
        erp = np.full((h, w, 3), [128, 64, 32], dtype=np.uint8)

        crops = extract_cubemap(erp, fov=90)
        front_crop = next(c for c in crops if c[1] == "front")[0]

        # Front face should contain the background color, not be empty/black
        assert front_crop.shape[0] > 0
        assert front_crop.shape[1] > 0
        assert not np.all(front_crop == 0)

    def test_different_fov_produces_valid_crops(self) -> None:
        """Different FOV should still produce valid square crops."""
        from sphereforge.stages.stage02_cubemap.cubemap import extract_cubemap

        h, w = 64, 128
        erp = np.zeros((h, w, 3), dtype=np.uint8)

        crops_90 = extract_cubemap(erp, fov=90)
        crops_60 = extract_cubemap(erp, fov=60)

        for crop, name, yaw, pitch in crops_90:
            assert crop.shape[0] == crop.shape[1], f"Face {name} not square"
            assert crop.ndim == 3

        for crop, name, yaw, pitch in crops_60:
            assert crop.shape[0] == crop.shape[1], f"Face {name} not square"
            assert crop.ndim == 3

    def test_front_face_quaternion_is_unit(self) -> None:
        """Front face quaternion should be a unit quaternion."""
        from sphereforge.stages.stage02_cubemap.extrinsics import compute_extrinsics

        ex = compute_extrinsics("front")
        norm = math.sqrt(ex["qw"] ** 2 + ex["qx"] ** 2 + ex["qy"] ** 2 + ex["qz"] ** 2)
        assert abs(norm - 1.0) < 1e-5

    def test_yaw_offset_changes_quaternion(self) -> None:
        """Applying yaw offset should produce a different quaternion."""
        from sphereforge.stages.stage02_cubemap.extrinsics import compute_extrinsics

        ex0 = compute_extrinsics("front", yaw_offset=0.0)
        ex30 = compute_extrinsics("front", yaw_offset=30.0)
        assert ex0["qw"] != ex30["qw"] or ex0["qx"] != ex30["qx"]

    def test_unknown_face_raises(self) -> None:
        """Unknown face name should raise ValueError."""
        from sphereforge.stages.stage02_cubemap.extrinsics import compute_extrinsics

        with pytest.raises(ValueError, match="Unknown face name"):
            compute_extrinsics("diagonal")


# ==========================================================================
# T2.2 — Yaw diversification
# ==========================================================================


class TestYawDiversify:
    """Tests for yaw diversification (T2.2)."""

    def test_yaw_offset_wraps_360(self) -> None:
        """Yaw offset should wrap at 360°."""
        from sphereforge.stages.stage02_cubemap.yaw_diversify import apply_yaw_offset

        step = 30
        assert apply_yaw_offset(0, step) == 0.0
        assert apply_yaw_offset(1, step) == 30.0
        assert apply_yaw_offset(12, step) == 0.0  # 360° wrap
        assert apply_yaw_offset(13, step) == 30.0

    def test_extract_diversified_produces_six_faces(self) -> None:
        """extract_diversified_cubemaps should return 6 faces."""
        from sphereforge.stages.stage02_cubemap.yaw_diversify import extract_diversified_cubemaps
        from sphereforge.config import Stage02Config

        h, w = 64, 128
        erp = np.zeros((h, w, 3), dtype=np.uint8)
        config = Stage02Config(fov=90, overlap=15, yaw_offset_step=30, n_faces=6)

        crops = extract_diversified_cubemaps(erp, frame_index=0, config=config)
        assert len(crops) == 6

    def test_different_frames_different_yaw(self) -> None:
        """Different frame indices should produce different yaw offsets."""
        from sphereforge.stages.stage02_cubemap.yaw_diversify import extract_diversified_cubemaps
        from sphereforge.config import Stage02Config

        h, w = 64, 128
        erp = np.zeros((h, w, 3), dtype=np.uint8)
        config = Stage02Config(fov=90, overlap=15, yaw_offset_step=30, n_faces=6)

        crops0 = extract_diversified_cubemaps(erp, frame_index=0, config=config)
        crops1 = extract_diversified_cubemaps(erp, frame_index=1, config=config)

        # Front face yaw should differ by 30°
        front0 = next(c for c in crops0 if c[1] == "front")[2]
        front1 = next(c for c in crops1 if c[1] == "front")[2]
        assert abs(front1 - front0 - 30.0) < 1e-6


# ==========================================================================
# T2.5 / T2.6 — Masking
# ==========================================================================


class TestMasking:
    """Tests for masking functions (T2.5, T2.6)."""

    def test_yolo_mask_fallback_without_ultralytics(self) -> None:
        """Without ultralytics, YOLO masks should be all zeros."""
        from sphereforge.stages.stage02_cubemap.masking import generate_yolo_masks

        crops = [
            np.zeros((32, 32, 3), dtype=np.uint8),
            np.zeros((32, 32, 3), dtype=np.uint8),
        ]
        masks = generate_yolo_masks(crops)
        assert len(masks) == 2
        for m in masks:
            assert m.shape == (32, 32)
            assert np.all(m == 0)

    def test_overexposure_mask_detects_bright_pixels(self) -> None:
        """Overexposure mask should mark pixels above threshold."""
        from sphereforge.stages.stage02_cubemap.masking import generate_overexposure_masks

        crop = np.full((4, 4, 3), 200, dtype=np.uint8)
        crop[0, 0] = [255, 255, 255]  # one bright pixel
        crop[1, 1] = [251, 251, 251]  # another bright pixel (> threshold)

        masks = generate_overexposure_masks([crop], threshold=250)
        assert len(masks) == 1
        mask = masks[0]
        assert mask[0, 0] == 255
        assert mask[1, 1] == 255
        assert mask[2, 2] == 0  # not bright enough

    def test_combine_masks_union(self) -> None:
        """Combined mask should be the union of input masks."""
        from sphereforge.stages.stage02_cubemap.masking import combine_masks

        m1 = np.zeros((4, 4), dtype=np.uint8)
        m1[0, 0] = 255
        m2 = np.zeros((4, 4), dtype=np.uint8)
        m2[1, 1] = 255

        combined = combine_masks([m1], [m2])
        assert combined[0][0, 0] == 255
        assert combined[0][1, 1] == 255
        assert combined[0][2, 2] == 0


# ==========================================================================
# T2.7 — COLMAP dataset writer (integration smoke test)
# ==========================================================================


class TestColmapWriter:
    """Smoke tests for COLMAP text file writers (T2.7)."""

    def test_write_cameras_txt_roundtrip(self, tmp_path) -> None:
        """Writing and reading cameras.txt should preserve data."""
        from sphereforge.common.colmap_helpers import (
            parse_cameras_txt,
            write_cameras_txt,
        )

        cameras = {
            1: {
                "camera_id": 1,
                "model": "PINHOLE",
                "width": 1024,
                "height": 1024,
                "params": [512.0, 512.0, 512.0, 512.0],
            }
        }
        path = tmp_path / "cameras.txt"
        write_cameras_txt(path, cameras)
        parsed = parse_cameras_txt(path)

        assert 1 in parsed
        assert parsed[1]["model"] == "PINHOLE"
        assert parsed[1]["width"] == 1024
        np.testing.assert_allclose(parsed[1]["params"], [512.0, 512.0, 512.0, 512.0])

    def test_write_images_txt_roundtrip(self, tmp_path) -> None:
        """Writing and reading images.txt should preserve data."""
        from sphereforge.common.colmap_helpers import (
            parse_images_txt,
            write_images_txt,
        )

        images = {
            1: {
                "name": "images/frame_000_front.png",
                "qw": 1.0,
                "qx": 0.0,
                "qy": 0.0,
                "qz": 0.0,
                "tx": 0.0,
                "ty": 0.0,
                "tz": 0.0,
                "camera_id": 1,
                "point3D_ids": [],
            }
        }
        path = tmp_path / "images.txt"
        write_images_txt(path, images)
        parsed = parse_images_txt(path)

        assert 1 in parsed
        assert parsed[1]["name"] == "images/frame_000_front.png"
        assert parsed[1]["qw"] == 1.0
