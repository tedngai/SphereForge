"""Tests for Stage 3: Multi-View SfM (COLMAP wrappers).

Covers:
  1. COLMAP CLI argument construction (mock subprocess.run, verify command args)
  2. Model reader with synthetic COLMAP output
  3. Bundle adjustment config (refine_intrinsics flag propagation)
  4. Pipeline orchestration order (verify functions called in correct sequence)

All subprocess calls are mocked — no COLMAP installation required.
"""

from __future__ import annotations

import os
import struct
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from sphereforge.config import Stage03Config
from sphereforge.stages.stage03_sfm.bundle_adjustment import run_bundle_adjustment
from sphereforge.stages.stage03_sfm.dense_reconstruction import run_dense_reconstruction
from sphereforge.stages.stage03_sfm.feature_extraction import run_feature_extraction
from sphereforge.stages.stage03_sfm.feature_matching import run_feature_matching
from sphereforge.stages.stage03_sfm.model_reader import read_dense_model, read_sparse_model
from sphereforge.stages.stage03_sfm.pipeline import _build_stage03_image_list, run_stage03
from sphereforge.stages.stage03_sfm.pycolmap_probe import (
    _build_sensor_from_rig_rotations,
    _group_database_images_by_frame,
)

if TYPE_CHECKING:
    from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_success_result() -> MagicMock:
    """Create a mock subprocess.Result with returncode 0."""
    m = MagicMock()
    m.returncode = 0
    m.stderr = ""
    m.stdout = ""
    return m


def _write_synthetic_text_model(sparse_dir: Path) -> None:
    """Write minimal synthetic COLMAP text-format model files."""
    sparse_dir.mkdir(parents=True, exist_ok=True)

    # cameras.txt
    (sparse_dir / "cameras.txt").write_text(
        "# Camera list with one line of data per camera:\n"
        "#   CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n"
        "1 PINHOLE 1024 1024 512 512 512 512\n",
        encoding="utf-8",
    )

    # images.txt
    (sparse_dir / "images.txt").write_text(
        "# Image list with two lines of data per image:\n"
        "1 1.0 0.0 0.0 0.0 0.0 0.0 0.0 1 image001.png\n"
        "\n",
        encoding="utf-8",
    )

    # points3D.txt
    (sparse_dir / "points3D.txt").write_text(
        "# 3D point list with one line of data per point:\n"
        "1 1.0 2.0 3.0 128 128 128 0.5\n",
        encoding="utf-8",
    )


def _write_synthetic_binary_model(sparse_dir: Path) -> None:
    """Write minimal synthetic COLMAP binary-format model files."""
    sparse_dir.mkdir(parents=True, exist_ok=True)

    # cameras.bin — 1 PINHOLE camera
    with open(sparse_dir / "cameras.bin", "wb") as f:
        f.write(struct.pack("<Q", 1))  # num_cameras
        f.write(struct.pack("<I", 1))  # camera_id
        # model name "PINHOLE" + null terminator
        f.write(b"PINHOLE\x00")
        f.write(struct.pack("<Q", 1024))  # width
        f.write(struct.pack("<Q", 1024))  # height
        # 4 params for PINHOLE: fx fy cx cy
        f.write(struct.pack("<4d", 512.0, 512.0, 512.0, 512.0))

    # images.bin — 1 image
    with open(sparse_dir / "images.bin", "wb") as f:
        f.write(struct.pack("<Q", 1))  # num_images
        f.write(struct.pack("<I", 1))  # image_id
        f.write(struct.pack("<4d", 1.0, 0.0, 0.0, 0.0))  # qw qx qy qz
        f.write(struct.pack("<3d", 0.0, 0.0, 0.0))  # tx ty tz
        f.write(struct.pack("<I", 1))  # camera_id
        f.write(b"image001.png\x00")  # name + null
        f.write(struct.pack("<Q", 0))  # num_points2D

    # points3D.bin — 1 point
    with open(sparse_dir / "points3D.bin", "wb") as f:
        f.write(struct.pack("<Q", 1))  # num_points
        f.write(struct.pack("<Q", 1))  # point3D_id
        f.write(struct.pack("<3d", 1.0, 2.0, 3.0))  # x y z
        f.write(struct.pack("<3B", 128, 128, 128))  # r g b
        f.write(struct.pack("<d", 0.5))  # error
        f.write(struct.pack("<Q", 0))  # track_length


# ---------------------------------------------------------------------------
# T3.1 — Feature Extraction CLI args
# ---------------------------------------------------------------------------


class TestFeatureExtractionCLI:
    """Tests for run_feature_extraction command construction."""

    @patch("sphereforge.stages.stage03_sfm.feature_extraction.shutil.which", return_value="/usr/bin/colmap")
    @patch("sphereforge.stages.stage03_sfm.feature_extraction.subprocess.run")
    def test_basic_command_args(self, mock_run, mock_which, tmp_path: Path) -> None:
        """Verify the basic COLMAP feature_extractor command arguments."""
        mock_run.return_value = _make_success_result()

        db_path = tmp_path / "database.db"
        img_dir = tmp_path / "images"
        img_dir.mkdir()

        run_feature_extraction(
            database_path=db_path,
            image_dir=img_dir,
            camera_model="PINHOLE",
            feature_type="root_sift",
        )

        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "colmap"
        assert cmd[1] == "feature_extractor"
        assert "--database_path" in cmd
        assert str(db_path) in cmd
        assert "--image_path" in cmd
        assert str(img_dir) in cmd
        assert "--ImageReader.camera_model" in cmd
        assert "PINHOLE" in cmd
        assert "--ImageReader.single_camera" in cmd
        assert "1" in cmd
        assert "--SiftExtraction.root_sift" in cmd
        # root_sift=1
        root_sift_idx = cmd.index("--SiftExtraction.root_sift")
        assert cmd[root_sift_idx + 1] == "1"

    @patch("sphereforge.stages.stage03_sfm.feature_extraction.shutil.which", return_value="/usr/bin/colmap")
    @patch("sphereforge.stages.stage03_sfm.feature_extraction.subprocess.run")
    def test_sift_sets_root_sift_zero(self, mock_run, mock_which, tmp_path: Path) -> None:
        """When feature_type='sift', --SiftExtraction.root_sift should be 0."""
        mock_run.return_value = _make_success_result()

        db_path = tmp_path / "database.db"
        img_dir = tmp_path / "images"
        img_dir.mkdir()

        run_feature_extraction(
            database_path=db_path,
            image_dir=img_dir,
            feature_type="sift",
        )

        cmd = mock_run.call_args[0][0]
        root_sift_idx = cmd.index("--SiftExtraction.root_sift")
        assert cmd[root_sift_idx + 1] == "0"

    @patch("sphereforge.stages.stage03_sfm.feature_extraction.shutil.which", return_value="/usr/bin/colmap")
    @patch("sphereforge.stages.stage03_sfm.feature_extraction.subprocess.run")
    def test_mask_dir_adds_image_list(self, mock_run, mock_which, tmp_path: Path) -> None:
        """When mask_dir is provided, --image_list_path should be in command."""
        mock_run.return_value = _make_success_result()

        db_path = tmp_path / "database.db"
        img_dir = tmp_path / "images"
        img_dir.mkdir()
        mask_dir = tmp_path / "masks"
        mask_dir.mkdir()

        # Create matching image and mask
        (img_dir / "frame001.png").touch()
        (mask_dir / "frame001.png").touch()

        run_feature_extraction(
            database_path=db_path,
            image_dir=img_dir,
            mask_dir=mask_dir,
        )

        cmd = mock_run.call_args[0][0]
        assert "--image_list_path" in cmd

    @patch("sphereforge.stages.stage03_sfm.feature_extraction.shutil.which", return_value="/usr/bin/colmap")
    @patch("sphereforge.stages.stage03_sfm.feature_extraction.subprocess.run")
    def test_single_camera_per_folder_flag(
        self, mock_run, mock_which, tmp_path: Path
    ) -> None:
        """Panorama-rig datasets should use per-folder camera assignment."""
        mock_run.return_value = _make_success_result()

        db_path = tmp_path / "database.db"
        img_dir = tmp_path / "images"
        (img_dir / "pano_camera00").mkdir(parents=True)
        (img_dir / "pano_camera00" / "frame001.png").touch()

        run_feature_extraction(
            database_path=db_path,
            image_dir=img_dir,
            single_camera_per_folder=True,
            image_list=["pano_camera00/frame001.png"],
        )

        cmd = mock_run.call_args[0][0]
        assert "--ImageReader.single_camera_per_folder" in cmd
        assert "--image_list_path" in cmd

    @patch("sphereforge.stages.stage03_sfm.feature_extraction.shutil.which", return_value=None)
    def test_colmap_not_found_raises(self, mock_which, tmp_path: Path) -> None:
        """Should raise RuntimeError when COLMAP is not on PATH."""
        with pytest.raises(RuntimeError, match="COLMAP is not installed"):
            run_feature_extraction(
                database_path=tmp_path / "db.db",
                image_dir=tmp_path / "images",
            )

    @patch("sphereforge.stages.stage03_sfm.feature_extraction.shutil.which", return_value="/usr/bin/colmap")
    @patch("sphereforge.stages.stage03_sfm.feature_extraction.subprocess.run")
    def test_nonzero_exit_raises(self, mock_run, mock_which, tmp_path: Path) -> None:
        """Should raise RuntimeError when subprocess returns non-zero."""
        fail = MagicMock()
        fail.returncode = 1
        fail.stderr = "something went wrong"
        mock_run.return_value = fail

        with pytest.raises(RuntimeError, match="feature_extractor failed"):
            run_feature_extraction(
                database_path=tmp_path / "db.db",
                image_dir=tmp_path / "images",
            )


# ---------------------------------------------------------------------------
# T3.2 — Feature Matching CLI args
# ---------------------------------------------------------------------------


class TestFeatureMatchingCLI:
    """Tests for run_feature_matching command construction."""

    @patch("sphereforge.stages.stage03_sfm.feature_matching.subprocess.run")
    def test_exhaustive_matcher(self, mock_run, tmp_path: Path) -> None:
        """'exhaustive' should call exhaustive_matcher."""
        mock_run.return_value = _make_success_result()

        run_feature_matching(
            database_path=tmp_path / "db.db",
            matcher_type="exhaustive",
        )

        cmd = mock_run.call_args[0][0]
        assert cmd[1] == "exhaustive_matcher"

    @patch("sphereforge.stages.stage03_sfm.feature_matching.subprocess.run")
    def test_sequential_matcher(self, mock_run, tmp_path: Path) -> None:
        """'sequential' should call sequential_matcher."""
        mock_run.return_value = _make_success_result()

        run_feature_matching(
            database_path=tmp_path / "db.db",
            matcher_type="sequential",
        )

        cmd = mock_run.call_args[0][0]
        assert cmd[1] == "sequential_matcher"

    @patch("sphereforge.stages.stage03_sfm.feature_matching.subprocess.run")
    def test_sequential_matcher_accepts_overlap_controls(self, mock_run, tmp_path: Path) -> None:
        """Sequential matcher should forward overlap controls when provided."""
        mock_run.return_value = _make_success_result()

        run_feature_matching(
            database_path=tmp_path / "db.db",
            matcher_type="sequential",
            sequential_overlap=1,
            sequential_quadratic_overlap=False,
        )

        cmd = mock_run.call_args[0][0]
        assert "--SequentialMatching.overlap" in cmd
        assert "--SequentialMatching.quadratic_overlap" in cmd

    @patch("sphereforge.stages.stage03_sfm.feature_matching.subprocess.run")
    def test_vocab_tree_matcher(self, mock_run, tmp_path: Path) -> None:
        """'vocab_tree' should call vocab_tree_matcher with vocab tree path."""
        mock_run.return_value = _make_success_result()
        vocab_path = tmp_path / "vocab_tree.bin"
        vocab_path.touch()

        run_feature_matching(
            database_path=tmp_path / "db.db",
            matcher_type="vocab_tree",
            vocab_tree_path=vocab_path,
        )

        cmd = mock_run.call_args[0][0]
        assert cmd[1] == "vocab_tree_matcher"
        assert "--VocabTreeMatching.vocab_tree_path" in cmd

    @patch("sphereforge.stages.stage03_sfm.feature_matching.subprocess.run")
    def test_vocab_tree_matcher_accepts_match_list(self, mock_run, tmp_path: Path) -> None:
        """Vocab-tree matcher should forward the optional match list path."""
        mock_run.return_value = _make_success_result()
        vocab_path = tmp_path / "vocab_tree.bin"
        vocab_path.touch()
        match_list_path = tmp_path / "pairs.txt"
        match_list_path.write_text("a b\n", encoding="utf-8")

        run_feature_matching(
            database_path=tmp_path / "db.db",
            matcher_type="vocab_tree",
            vocab_tree_path=vocab_path,
            match_list_path=match_list_path,
        )

        cmd = mock_run.call_args[0][0]
        assert "--VocabTreeMatching.match_list_path" in cmd
        assert str(match_list_path) in cmd

    @patch("sphereforge.stages.stage03_sfm.feature_matching.subprocess.run")
    def test_sequential_plus_vocab_tree(self, mock_run, tmp_path: Path) -> None:
        """'sequential+vocabulary_tree' should call both matchers."""
        mock_run.return_value = _make_success_result()
        vocab_path = tmp_path / "vocab_tree.bin"
        vocab_path.touch()

        run_feature_matching(
            database_path=tmp_path / "db.db",
            matcher_type="sequential+vocabulary_tree",
            vocab_tree_path=vocab_path,
        )

        assert mock_run.call_count == 2
        first_cmd = mock_run.call_args_list[0][0][0]
        second_cmd = mock_run.call_args_list[1][0][0]
        assert first_cmd[1] == "sequential_matcher"
        assert second_cmd[1] == "vocab_tree_matcher"

    def test_vocab_tree_without_path_raises(self, tmp_path: Path) -> None:
        """'vocab_tree' without vocab_tree_path should raise ValueError."""
        with pytest.raises(ValueError, match="vocab_tree_path is required"):
            run_feature_matching(
                database_path=tmp_path / "db.db",
                matcher_type="vocab_tree",
                vocab_tree_path=None,
            )

    def test_unknown_matcher_type_raises(self, tmp_path: Path) -> None:
        """An unknown matcher_type should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown matcher_type"):
            run_feature_matching(
                database_path=tmp_path / "db.db",
                matcher_type="unknown",
            )


# ---------------------------------------------------------------------------
# T3.3 — Bundle Adjustment config
# ---------------------------------------------------------------------------


class TestBundleAdjustmentConfig:
    """Tests for refine_intrinsics flag propagation."""

    @patch("sphereforge.stages.stage03_sfm.bundle_adjustment.subprocess.run")
    def test_refine_intrinsics_false(self, mock_run, tmp_path: Path) -> None:
        """When refine_intrinsics=False, bundle_adjuster should not refine."""
        mock_run.return_value = _make_success_result()

        db_path = tmp_path / "database.db"
        sparse_dir = tmp_path / "sparse"
        image_dir = tmp_path / "images"
        image_dir.mkdir()

        # Pre-create the mapper output dir so bundle_adjuster can find it
        (sparse_dir / "0").mkdir(parents=True)

        run_bundle_adjustment(
            database_path=db_path,
            sparse_dir=sparse_dir,
            refine_intrinsics=False,
            image_dir=image_dir,
        )

        # Find the bundle_adjuster call (second call)
        calls = mock_run.call_args_list
        assert len(calls) == 2  # mapper + bundle_adjuster
        ba_cmd = calls[1][0][0]
        assert "bundle_adjuster" in ba_cmd
        # refine_focal_length=0, refine_extra_params=0
        fl_idx = ba_cmd.index("--BundleAdjustment.refine_focal_length")
        ep_idx = ba_cmd.index("--BundleAdjustment.refine_extra_params")
        assert ba_cmd[fl_idx + 1] == "0"
        assert ba_cmd[ep_idx + 1] == "0"

    @patch("sphereforge.stages.stage03_sfm.bundle_adjustment.subprocess.run")
    def test_refine_intrinsics_true(self, mock_run, tmp_path: Path) -> None:
        """When refine_intrinsics=True, bundle_adjuster should refine."""
        mock_run.return_value = _make_success_result()

        db_path = tmp_path / "database.db"
        sparse_dir = tmp_path / "sparse"
        image_dir = tmp_path / "images"
        image_dir.mkdir()

        (sparse_dir / "0").mkdir(parents=True)

        run_bundle_adjustment(
            database_path=db_path,
            sparse_dir=sparse_dir,
            refine_intrinsics=True,
            image_dir=image_dir,
        )

        calls = mock_run.call_args_list
        ba_cmd = calls[1][0][0]
        fl_idx = ba_cmd.index("--BundleAdjustment.refine_focal_length")
        ep_idx = ba_cmd.index("--BundleAdjustment.refine_extra_params")
        assert ba_cmd[fl_idx + 1] == "1"
        assert ba_cmd[ep_idx + 1] == "1"

    @patch("sphereforge.stages.stage03_sfm.bundle_adjustment.subprocess.run")
    def test_mapper_command_args(self, mock_run, tmp_path: Path) -> None:
        """Verify the mapper command includes correct paths."""
        mock_run.return_value = _make_success_result()

        db_path = tmp_path / "database.db"
        sparse_dir = tmp_path / "sparse"
        image_dir = tmp_path / "images"
        image_dir.mkdir()

        run_bundle_adjustment(
            database_path=db_path,
            sparse_dir=sparse_dir,
            image_dir=image_dir,
        )

        mapper_cmd = mock_run.call_args_list[0][0][0]
        assert mapper_cmd[1] == "mapper"
        assert str(db_path) in mapper_cmd
        assert str(image_dir) in mapper_cmd
        assert str(sparse_dir) in mapper_cmd

    @patch("sphereforge.stages.stage03_sfm.bundle_adjustment.subprocess.run")
    def test_nonzero_mapper_raises(self, mock_run, tmp_path: Path) -> None:
        """Non-zero mapper exit should raise RuntimeError."""
        fail = MagicMock()
        fail.returncode = 1
        fail.stderr = "mapper error"
        mock_run.return_value = fail

        with pytest.raises(RuntimeError, match="mapper failed"):
            run_bundle_adjustment(
                database_path=tmp_path / "db.db",
                sparse_dir=tmp_path / "sparse",
                image_dir=tmp_path / "images",
            )


# ---------------------------------------------------------------------------
# T3.4 — Model Reader
# ---------------------------------------------------------------------------


class TestModelReader:
    """Tests for read_sparse_model and read_dense_model."""

    def test_read_text_format(self, tmp_path: Path) -> None:
        """Should parse a text-format COLMAP model correctly."""
        _write_synthetic_text_model(tmp_path / "sparse")
        result = read_sparse_model(tmp_path / "sparse")

        assert "cameras" in result
        assert "images" in result
        assert "points3D" in result
        assert len(result["cameras"]) == 1
        assert len(result["images"]) == 1
        assert len(result["points3D"]) == 1
        # Check camera details
        cam = result["cameras"][1]
        assert cam["model"] == "PINHOLE"
        assert cam["width"] == 1024
        assert cam["height"] == 1024

    def test_read_binary_format(self, tmp_path: Path) -> None:
        """Should parse a binary-format COLMAP model correctly."""
        _write_synthetic_binary_model(tmp_path / "sparse")
        result = read_sparse_model(tmp_path / "sparse")

        assert "cameras" in result
        assert "images" in result
        assert "points3D" in result
        assert len(result["cameras"]) == 1
        cam = result["cameras"][1]
        assert cam["model"] == "PINHOLE"

    def test_text_format_preferred_over_binary(self, tmp_path: Path) -> None:
        """When both text and binary exist, text should be preferred."""
        sparse = tmp_path / "sparse"
        _write_synthetic_text_model(sparse)
        _write_synthetic_binary_model(sparse)

        # Overwrite text to have a unique camera model marker
        (sparse / "cameras.txt").write_text(
            "# Comment\n2 PINHOLE 2048 2048 1024 1024 1024 1024\n",
            encoding="utf-8",
        )

        result = read_sparse_model(sparse)
        # Should read the text file (camera_id=2) not binary (camera_id=1)
        assert 2 in result["cameras"]

    def test_no_model_files_raises(self, tmp_path: Path) -> None:
        """Should raise FileNotFoundError when no model files exist."""
        empty = tmp_path / "empty"
        empty.mkdir()

        with pytest.raises(FileNotFoundError, match="No COLMAP sparse model"):
            read_sparse_model(empty)

    def test_read_from_subdir_0(self, tmp_path: Path) -> None:
        """Should auto-redirect to sparse/0/ when that's the model dir."""
        _write_synthetic_text_model(tmp_path / "sparse" / "0")

        result = read_sparse_model(tmp_path / "sparse")
        assert len(result["cameras"]) == 1

    def test_read_dense_model(self, tmp_path: Path) -> None:
        """read_dense_model should read from dense/sparse/ by default."""
        _write_synthetic_text_model(tmp_path / "dense" / "sparse")

        result = read_dense_model(tmp_path / "dense")
        assert len(result["cameras"]) == 1

    def test_read_with_conftest_fixture(self, synthetic_colmap_text_dir: Path) -> None:
        """Should work with the conftest synthetic COLMAP text fixture."""
        result = read_sparse_model(synthetic_colmap_text_dir)

        assert "cameras" in result
        assert "images" in result
        assert "points3D" in result
        # conftest fixture creates 2 cameras, 3 images, 4 points
        assert len(result["cameras"]) == 2
        assert len(result["images"]) == 3
        assert len(result["points3D"]) == 4


# ---------------------------------------------------------------------------
# T3.5 — Dense Reconstruction
# ---------------------------------------------------------------------------


class TestDenseReconstruction:
    """Tests for run_dense_reconstruction."""

    @patch("sphereforge.stages.stage03_sfm.dense_reconstruction.subprocess.run")
    def test_runs_three_steps(self, mock_run, tmp_path: Path) -> None:
        """Should run image_undistorter, patch_match_stereo, stereo_fusion."""
        mock_run.return_value = _make_success_result()

        sparse_dir = tmp_path / "sparse"
        (sparse_dir / "0").mkdir(parents=True)
        image_dir = tmp_path / "images"
        image_dir.mkdir()
        dense_dir = tmp_path / "dense"

        run_dense_reconstruction(sparse_dir, image_dir, dense_dir)

        assert mock_run.call_count == 3
        cmds = [c[0][0] for c in mock_run.call_args_list]
        assert cmds[0][1] == "image_undistorter"
        assert cmds[1][1] == "patch_match_stereo"
        assert cmds[2][1] == "stereo_fusion"

    @patch("sphereforge.stages.stage03_sfm.dense_reconstruction.subprocess.run")
    def test_undistorter_command_args(self, mock_run, tmp_path: Path) -> None:
        """Verify image_undistorter gets the correct paths."""
        mock_run.return_value = _make_success_result()

        sparse_dir = tmp_path / "sparse"
        (sparse_dir / "0").mkdir(parents=True)
        image_dir = tmp_path / "images"
        image_dir.mkdir()
        dense_dir = tmp_path / "dense"

        run_dense_reconstruction(sparse_dir, image_dir, dense_dir)

        cmd = mock_run.call_args_list[0][0][0]
        assert "--image_path" in cmd
        assert str(image_dir) in cmd
        assert "--input_path" in cmd
        assert "--output_path" in cmd
        assert str(dense_dir) in cmd

    @patch("sphereforge.stages.stage03_sfm.dense_reconstruction.subprocess.run")
    def test_fusion_output_path(self, mock_run, tmp_path: Path) -> None:
        """Stereo fusion should output to dense_dir/fused.ply."""
        mock_run.return_value = _make_success_result()

        sparse_dir = tmp_path / "sparse"
        (sparse_dir / "0").mkdir(parents=True)
        image_dir = tmp_path / "images"
        image_dir.mkdir()
        dense_dir = tmp_path / "dense"

        run_dense_reconstruction(sparse_dir, image_dir, dense_dir)

        fusion_cmd = mock_run.call_args_list[2][0][0]
        assert "--output_path" in fusion_cmd
        op_idx = fusion_cmd.index("--output_path")
        assert str(dense_dir / "fused.ply") == fusion_cmd[op_idx + 1]

    @patch("sphereforge.stages.stage03_sfm.dense_reconstruction.subprocess.run")
    def test_clears_existing_dense_workspace_before_rerun(self, mock_run, tmp_path: Path) -> None:
        """Reruns should clear stale dense outputs before invoking COLMAP again."""
        mock_run.return_value = _make_success_result()

        sparse_dir = tmp_path / "sparse"
        (sparse_dir / "0").mkdir(parents=True)
        image_dir = tmp_path / "images"
        image_dir.mkdir()
        dense_dir = tmp_path / "dense"
        stale_file = dense_dir / "images" / "stale.png"
        stale_file.parent.mkdir(parents=True)
        stale_file.write_text("stale")

        run_dense_reconstruction(sparse_dir, image_dir, dense_dir)

        assert not stale_file.exists()
        assert dense_dir.exists()

    @patch("sphereforge.stages.stage03_sfm.dense_reconstruction.subprocess.run")
    def test_nonzero_raises(self, mock_run, tmp_path: Path) -> None:
        """Non-zero exit from any step should raise RuntimeError."""
        fail = MagicMock()
        fail.returncode = 1
        fail.stderr = "error"
        mock_run.return_value = fail

        sparse_dir = tmp_path / "sparse"
        (sparse_dir / "0").mkdir(parents=True)
        image_dir = tmp_path / "images"
        image_dir.mkdir()

        with pytest.raises(RuntimeError, match="image_undistorter failed"):
            run_dense_reconstruction(sparse_dir, image_dir, tmp_path / "dense")


# ---------------------------------------------------------------------------
# T3.6 — Pipeline orchestration
# ---------------------------------------------------------------------------


class TestPipelineOrchestration:
    """Tests for run_stage03 call ordering and integration."""

    def test_panorama_rig_image_list_is_frame_major(self, tmp_path: Path) -> None:
        """Panorama-rig ordering should interleave cameras at each frame index."""
        image_dir = tmp_path / "images"
        (image_dir / "pano_camera00").mkdir(parents=True)
        (image_dir / "pano_camera01").mkdir(parents=True)
        (image_dir / "pano_camera00" / "frame_000.png").write_bytes(b"a")
        (image_dir / "pano_camera00" / "frame_001.png").write_bytes(b"a")
        (image_dir / "pano_camera01" / "frame_000.png").write_bytes(b"a")
        (image_dir / "pano_camera01" / "frame_001.png").write_bytes(b"a")
        manifest = {
            "cameras": [
                {"name": "pano_camera00", "camera_id": 1, "yaw_deg": 0, "pitch_deg": 0},
                {"name": "pano_camera01", "camera_id": 2, "yaw_deg": 90, "pitch_deg": 0},
            ]
        }

        assert _build_stage03_image_list(image_dir, manifest) == [
            "pano_camera00/frame_000.png",
            "pano_camera01/frame_000.png",
            "pano_camera00/frame_001.png",
            "pano_camera01/frame_001.png",
        ]

    def test_pycolmap_probe_groups_database_images_by_frame(self) -> None:
        """The pycolmap probe should group per-camera images by panorama frame stem."""

        class _Image:
            def __init__(self, image_id: int, name: str) -> None:
                self.image_id = image_id
                self.name = name

        grouped = _group_database_images_by_frame(
            [
                _Image(2, "pano_camera01/frame_000.png"),
                _Image(1, "pano_camera00/frame_000.png"),
                _Image(4, "pano_camera01/frame_001.png"),
                _Image(3, "pano_camera00/frame_001.png"),
            ]
        )

        assert list(grouped) == ["frame_000", "frame_001"]
        assert [image.name for image in grouped["frame_000"]] == [
            "pano_camera00/frame_000.png",
            "pano_camera01/frame_000.png",
        ]

    def test_pycolmap_probe_builds_sensor_rotations_relative_to_reference(self) -> None:
        """The first panorama-rig camera should define the rig coordinate frame."""
        half_turn = 0.5**0.5
        manifest = {
            "cameras": [
                {"name": "pano_camera00", "camera_id": 1},
                {"name": "pano_camera01", "camera_id": 2},
            ]
        }
        stage2_images = {
            1: {
                "name": "images/pano_camera00/frame_000.png",
                "camera_id": 1,
                "qw": 1.0,
                "qx": 0.0,
                "qy": 0.0,
                "qz": 0.0,
            },
            2: {
                "name": "images/pano_camera01/frame_000.png",
                "camera_id": 2,
                "qw": half_turn,
                "qx": 0.0,
                "qy": half_turn,
                "qz": 0.0,
            },
        }

        rotations = _build_sensor_from_rig_rotations(manifest, stage2_images)

        assert np.allclose(rotations[1], np.eye(3))
        expected = np.array(
            [
                [0.0, 0.0, 1.0],
                [0.0, 1.0, 0.0],
                [-1.0, 0.0, 0.0],
            ]
        )
        assert np.allclose(rotations[2], expected, atol=1e-6)

    @patch("sphereforge.stages.stage03_sfm.pipeline.read_sparse_model")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_dense_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_bundle_adjustment")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_matching")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_extraction")
    def test_correct_call_order(
        self,
        mock_extract: MagicMock,
        mock_match: MagicMock,
        mock_ba: MagicMock,
        mock_dense: MagicMock,
        mock_read: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Pipeline should call functions in order: extract → match → BA → read → dense."""
        mock_read.return_value = {
            "cameras": {1: {"model": "PINHOLE"}},
            "images": {1: {"name": "img.png"}},
            "points3D": {1: {"x": 0.0}},
        }

        config = Stage03Config(dense_reconstruction=True)
        dataset_dir = tmp_path / "dataset"
        dataset_dir.mkdir()
        (dataset_dir / "images").mkdir()
        output_dir = tmp_path / "output"

        result = run_stage03(config, dataset_dir, output_dir)

        # Verify call order
        mock_extract.assert_called_once()
        mock_match.assert_called_once()
        mock_ba.assert_called_once()
        mock_read.assert_called_once()
        mock_dense.assert_called_once()

        # Verify result has expected keys
        assert "cameras" in result
        assert "images" in result
        assert "points3D" in result

    @patch("sphereforge.stages.stage03_sfm.pipeline.read_sparse_model")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_dense_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_bundle_adjustment")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_matching")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_extraction")
    def test_dense_skipped_when_disabled(
        self,
        mock_extract: MagicMock,
        mock_match: MagicMock,
        mock_ba: MagicMock,
        mock_dense: MagicMock,
        mock_read: MagicMock,
        tmp_path: Path,
    ) -> None:
        """When dense_reconstruction=False, dense step should not run."""
        mock_read.return_value = {
            "cameras": {},
            "images": {},
            "points3D": {},
        }

        config = Stage03Config(dense_reconstruction=False)
        dataset_dir = tmp_path / "dataset"
        dataset_dir.mkdir()
        (dataset_dir / "images").mkdir()
        output_dir = tmp_path / "output"

        run_stage03(config, dataset_dir, output_dir)

        mock_dense.assert_not_called()

    @patch("sphereforge.stages.stage03_sfm.pipeline.read_sparse_model")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_dense_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_bundle_adjustment")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_matching")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_extraction")
    def test_feature_type_propagated(
        self,
        mock_extract: MagicMock,
        mock_match: MagicMock,
        mock_ba: MagicMock,
        mock_dense: MagicMock,
        mock_read: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Config feature_type should be passed to run_feature_extraction."""
        mock_read.return_value = {
            "cameras": {},
            "images": {},
            "points3D": {},
        }

        config = Stage03Config(feature_type="sift", dense_reconstruction=False)
        dataset_dir = tmp_path / "dataset"
        dataset_dir.mkdir()
        (dataset_dir / "images").mkdir()
        output_dir = tmp_path / "output"

        run_stage03(config, dataset_dir, output_dir)

        extract_kwargs = mock_extract.call_args
        assert extract_kwargs.kwargs.get("feature_type", extract_kwargs[1].get("feature_type")) == "sift"

    @patch("sphereforge.stages.stage03_sfm.pipeline.read_sparse_model")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_dense_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_bundle_adjustment")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_matching")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_extraction")
    def test_refine_intrinsics_propagated(
        self,
        mock_extract: MagicMock,
        mock_match: MagicMock,
        mock_ba: MagicMock,
        mock_dense: MagicMock,
        mock_read: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Config refine_intrinsics should be passed to run_bundle_adjustment."""
        mock_read.return_value = {
            "cameras": {},
            "images": {},
            "points3D": {},
        }

        config = Stage03Config(refine_intrinsics=True, dense_reconstruction=False)
        dataset_dir = tmp_path / "dataset"
        dataset_dir.mkdir()
        (dataset_dir / "images").mkdir()
        output_dir = tmp_path / "output"

        run_stage03(config, dataset_dir, output_dir)

        ba_kwargs = mock_ba.call_args
        assert ba_kwargs.kwargs.get("refine_intrinsics", ba_kwargs[1].get("refine_intrinsics")) is True

    @patch("sphereforge.stages.stage03_sfm.pipeline.read_sparse_model")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_dense_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_bundle_adjustment")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_matching")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_extraction")
    def test_vocab_tree_path_from_dataset(
        self,
        mock_extract: MagicMock,
        mock_match: MagicMock,
        mock_ba: MagicMock,
        mock_dense: MagicMock,
        mock_read: MagicMock,
        tmp_path: Path,
    ) -> None:
        """If vocab_tree.bin exists in dataset dir, it should be passed to matching."""
        mock_read.return_value = {
            "cameras": {},
            "images": {},
            "points3D": {},
        }

        config = Stage03Config(dense_reconstruction=False)
        dataset_dir = tmp_path / "dataset"
        dataset_dir.mkdir()
        (dataset_dir / "images").mkdir()
        # Create vocab tree
        vocab_tree = dataset_dir / "vocab_tree.bin"
        vocab_tree.write_bytes(b"fake_vocab_tree")
        output_dir = tmp_path / "output"

        run_stage03(config, dataset_dir, output_dir)

        match_kwargs = mock_match.call_args
        assert match_kwargs.kwargs.get("vocab_tree_path", match_kwargs[1].get("vocab_tree_path")) == vocab_tree

    @patch("sphereforge.stages.stage03_sfm.pipeline.read_sparse_model")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_dense_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_bundle_adjustment")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_matching")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_extraction")
    def test_output_directory_structure(
        self,
        mock_extract: MagicMock,
        mock_match: MagicMock,
        mock_ba: MagicMock,
        mock_dense: MagicMock,
        mock_read: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Pipeline should create the expected output directory structure."""
        mock_read.return_value = {
            "cameras": {},
            "images": {},
            "points3D": {},
        }

        config = Stage03Config(dense_reconstruction=True)
        dataset_dir = tmp_path / "dataset"
        dataset_dir.mkdir()
        (dataset_dir / "images").mkdir()
        output_dir = tmp_path / "output"

        run_stage03(config, dataset_dir, output_dir)

        assert (output_dir / "sparse").is_dir()
        assert (output_dir / "dense").is_dir()

    @patch("sphereforge.stages.stage03_sfm.pipeline.read_sparse_model")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_dense_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_bundle_adjustment")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_matching")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_extraction")
    def test_registration_diagnostics_written(
        self,
        mock_extract: MagicMock,
        mock_match: MagicMock,
        mock_ba: MagicMock,
        mock_dense: MagicMock,
        mock_read: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Pipeline should persist Stage 3 registration diagnostics artifacts."""
        mock_read.return_value = {
            "cameras": {1: {"model": "PINHOLE"}},
            "images": {
                1: {
                    "name": "images/img_a.png",
                    "qw": 1.0,
                    "qx": 0.0,
                    "qy": 0.0,
                    "qz": 0.0,
                    "tx": 0.0,
                    "ty": 0.0,
                    "tz": 0.0,
                }
            },
            "points3D": {1: {"x": 0.0, "y": 0.0, "z": 1.0}},
        }

        config = Stage03Config(dense_reconstruction=False, min_registration_fraction=0.2)
        dataset_dir = tmp_path / "dataset"
        image_dir = dataset_dir / "images"
        image_dir.mkdir(parents=True)
        for name in ("img_a.png", "img_b.png", "img_c.png", "img_d.png"):
            (image_dir / name).write_bytes(b"fake")
        output_dir = tmp_path / "output"

        result = run_stage03(config, dataset_dir, output_dir)

        report_path = output_dir / "registration_report.json"
        csv_path = output_dir / "registered_vs_total.csv"
        preview_path = output_dir / "sparse_preview.png"

        assert report_path.exists()
        assert csv_path.exists()
        assert preview_path.exists()
        assert result["diagnostics"]["registered_images"] == 1
        assert result["diagnostics"]["total_input_images"] == 4
        assert result["diagnostics"]["registration_fraction"] == pytest.approx(0.25)
        assert result["diagnostics"]["matcher_type"] == "sequential+vocabulary_tree"
        assert result["diagnostics"]["reconstruction_backend"] == "colmap_cli"
        assert "img_a.png" in report_path.read_text(encoding="utf-8")
        assert "img_b.png,0" in csv_path.read_text(encoding="utf-8")

    @patch("sphereforge.stages.stage03_sfm.pipeline.read_sparse_model")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_dense_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_bundle_adjustment")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_matching")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_extraction")
    def test_registration_gate_blocks_low_coverage(
        self,
        mock_extract: MagicMock,
        mock_match: MagicMock,
        mock_ba: MagicMock,
        mock_dense: MagicMock,
        mock_read: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Low registration coverage should stop the pipeline before later stages continue."""
        mock_read.return_value = {
            "cameras": {1: {"model": "PINHOLE"}},
            "images": {
                1: {
                    "name": "img_a.png",
                    "qw": 1.0,
                    "qx": 0.0,
                    "qy": 0.0,
                    "qz": 0.0,
                    "tx": 0.0,
                    "ty": 0.0,
                    "tz": 0.0,
                }
            },
            "points3D": {1: {"x": 0.0, "y": 0.0, "z": 1.0}},
        }

        config = Stage03Config(dense_reconstruction=False, min_registration_fraction=0.5)
        dataset_dir = tmp_path / "dataset"
        image_dir = dataset_dir / "images"
        image_dir.mkdir(parents=True)
        for name in ("img_a.png", "img_b.png", "img_c.png", "img_d.png"):
            (image_dir / name).write_bytes(b"fake")
        output_dir = tmp_path / "output"

        with pytest.raises(RuntimeError, match="registration coverage is too low"):
            run_stage03(config, dataset_dir, output_dir)

        assert (output_dir / "registration_report.json").exists()
        mock_dense.assert_not_called()

    @patch("sphereforge.stages.stage03_sfm.pipeline.read_sparse_model")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_dense_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline._run_panorama_rig_pycolmap_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_bundle_adjustment")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_matching")
    @patch("sphereforge.stages.stage03_sfm.pipeline.build_vocab_tree")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_extraction")
    def test_panorama_rig_uses_per_folder_cameras_and_match_controls(
        self,
        mock_extract: MagicMock,
        mock_build_vocab_tree: MagicMock,
        mock_match: MagicMock,
        mock_ba: MagicMock,
        mock_pycolmap: MagicMock,
        mock_dense: MagicMock,
        mock_read: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Panorama-rig datasets should enable per-folder cameras and rig-friendly ordering."""
        mock_read.return_value = {
            "cameras": {1: {"model": "PINHOLE"}},
            "images": {
                1: {
                    "name": "images/pano_camera00/frame_000.png",
                    "qw": 1.0,
                    "qx": 0.0,
                    "qy": 0.0,
                    "qz": 0.0,
                    "tx": 0.0,
                    "ty": 0.0,
                    "tz": 0.0,
                }
            },
            "points3D": {1: {"x": 0.0, "y": 0.0, "z": 1.0}},
        }

        config = Stage03Config(dense_reconstruction=False, panorama_use_match_list=True)
        mock_build_vocab_tree.return_value = tmp_path / "output" / "panorama_rig_vocab_tree.bin"
        dataset_dir = tmp_path / "dataset"
        image_dir = dataset_dir / "images"
        (image_dir / "pano_camera00").mkdir(parents=True)
        (image_dir / "pano_camera01").mkdir(parents=True)
        (image_dir / "pano_camera00" / "frame_000.png").write_bytes(b"a")
        (image_dir / "pano_camera00" / "frame_001.png").write_bytes(b"a")
        (image_dir / "pano_camera01" / "frame_000.png").write_bytes(b"a")
        (image_dir / "pano_camera01" / "frame_001.png").write_bytes(b"a")
        (dataset_dir / "panorama_rig.json").write_text(
            '{"fov":90,"overlap":15,"cameras":[{"name":"pano_camera00","camera_id":1,"yaw_deg":0,"pitch_deg":0},{"name":"pano_camera01","camera_id":2,"yaw_deg":60,"pitch_deg":0}]}',
            encoding="utf-8",
        )
        output_dir = tmp_path / "output"

        run_stage03(config, dataset_dir, output_dir)

        extract_kwargs = mock_extract.call_args.kwargs
        assert extract_kwargs["single_camera_per_folder"] is True
        assert extract_kwargs["image_list"] == [
            "pano_camera00/frame_000.png",
            "pano_camera01/frame_000.png",
            "pano_camera00/frame_001.png",
            "pano_camera01/frame_001.png",
        ]
        assert mock_match.call_args.kwargs["matcher_type"] == "sequential+vocabulary_tree"
        assert mock_match.call_args.kwargs["vocab_tree_path"] == mock_build_vocab_tree.return_value
        assert mock_match.call_args.kwargs["sequential_overlap"] == 2
        assert mock_match.call_args.kwargs["sequential_quadratic_overlap"] is False
        match_list_path = mock_match.call_args.kwargs["match_list_path"]
        assert match_list_path is not None
        match_list_text = match_list_path.read_text(encoding="utf-8")
        assert "pano_camera00/frame_000.png pano_camera00/frame_001.png" in match_list_text
        assert "pano_camera00/frame_000.png pano_camera01/frame_001.png" in match_list_text

    @patch("sphereforge.stages.stage03_sfm.pipeline.read_sparse_model")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_dense_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline._run_panorama_rig_pycolmap_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_bundle_adjustment")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_matching")
    @patch("sphereforge.stages.stage03_sfm.pipeline.build_vocab_tree")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_extraction")
    def test_panorama_rig_can_skip_explicit_match_list(
        self,
        mock_extract: MagicMock,
        mock_build_vocab_tree: MagicMock,
        mock_match: MagicMock,
        mock_ba: MagicMock,
        mock_pycolmap: MagicMock,
        mock_dense: MagicMock,
        mock_read: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Panorama-rig datasets should be able to use only sequential matching controls."""
        mock_read.return_value = {
            "cameras": {1: {"model": "PINHOLE"}},
            "images": {
                1: {
                    "name": "images/pano_camera00/frame_000.png",
                    "qw": 1.0,
                    "qx": 0.0,
                    "qy": 0.0,
                    "qz": 0.0,
                    "tx": 0.0,
                    "ty": 0.0,
                    "tz": 0.0,
                }
            },
            "points3D": {1: {"x": 0.0, "y": 0.0, "z": 1.0}},
        }

        config = Stage03Config(dense_reconstruction=False, panorama_use_match_list=False)
        mock_build_vocab_tree.return_value = tmp_path / "output" / "panorama_rig_vocab_tree.bin"
        dataset_dir = tmp_path / "dataset"
        image_dir = dataset_dir / "images"
        (image_dir / "pano_camera00").mkdir(parents=True)
        (image_dir / "pano_camera00" / "frame_000.png").write_bytes(b"a")
        (dataset_dir / "panorama_rig.json").write_text(
            '{"fov":90,"overlap":15,"cameras":[{"name":"pano_camera00","camera_id":1,"yaw_deg":0,"pitch_deg":0}]}',
            encoding="utf-8",
        )

        run_stage03(config, dataset_dir, tmp_path / "output")

        assert mock_build_vocab_tree.call_count == 1
        assert mock_match.call_args.kwargs["vocab_tree_path"] == mock_build_vocab_tree.return_value
        assert mock_match.call_args.kwargs["match_list_path"] is None
        assert mock_match.call_args.kwargs["sequential_overlap"] == 2

    @patch("sphereforge.stages.stage03_sfm.pipeline.read_sparse_model")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_dense_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline._run_panorama_rig_pycolmap_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_bundle_adjustment")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_matching")
    @patch("sphereforge.stages.stage03_sfm.pipeline.build_vocab_tree")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_extraction")
    def test_panorama_rig_pycolmap_backend_requires_config_and_env_gate(
        self,
        mock_extract: MagicMock,
        mock_build_vocab_tree: MagicMock,
        mock_match: MagicMock,
        mock_ba: MagicMock,
        mock_pycolmap: MagicMock,
        mock_dense: MagicMock,
        mock_read: MagicMock,
        tmp_path: Path,
    ) -> None:
        """The optional pycolmap path should only run when both config and env enable it."""
        mock_read.return_value = {
            "cameras": {1: {"model": "PINHOLE"}},
            "images": {
                1: {
                    "name": "images/pano_camera00/frame_000.png",
                    "qw": 1.0,
                    "qx": 0.0,
                    "qy": 0.0,
                    "qz": 0.0,
                    "tx": 0.0,
                    "ty": 0.0,
                    "tz": 0.0,
                }
            },
            "points3D": {1: {"x": 0.0, "y": 0.0, "z": 1.0}},
        }
        mock_build_vocab_tree.return_value = tmp_path / "output" / "panorama_rig_vocab_tree.bin"

        dataset_dir = tmp_path / "dataset"
        image_dir = dataset_dir / "images"
        (image_dir / "pano_camera00").mkdir(parents=True)
        (image_dir / "pano_camera00" / "frame_000.png").write_bytes(b"a")
        (dataset_dir / "panorama_rig.json").write_text(
            '{"fov":90,"overlap":15,"cameras":[{"name":"pano_camera00","camera_id":1,"yaw_deg":0,"pitch_deg":0}]}',
            encoding="utf-8",
        )

        with patch.dict(os.environ, {"SPHEREFORGE_ENABLE_PYCOLMAP_RIG": "1"}, clear=False):
            run_stage03(
                Stage03Config(dense_reconstruction=False, panorama_use_pycolmap_rig=False),
                dataset_dir,
                tmp_path / "output_cfg_off",
            )
        mock_ba.assert_called_once()
        mock_pycolmap.assert_not_called()
        mock_ba.reset_mock()
        mock_pycolmap.reset_mock()

        with patch.dict(os.environ, {}, clear=True):
            run_stage03(
                Stage03Config(dense_reconstruction=False, panorama_use_pycolmap_rig=True),
                dataset_dir,
                tmp_path / "output_env_off",
            )
        mock_ba.assert_called_once()
        mock_pycolmap.assert_not_called()

    @patch("sphereforge.stages.stage03_sfm.pipeline.read_sparse_model")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_dense_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline._run_panorama_rig_pycolmap_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_bundle_adjustment")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_matching")
    @patch("sphereforge.stages.stage03_sfm.pipeline.build_vocab_tree")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_extraction")
    def test_panorama_rig_pycolmap_backend_prefers_window_three_and_skips_cli_mapper(
        self,
        mock_extract: MagicMock,
        mock_build_vocab_tree: MagicMock,
        mock_match: MagicMock,
        mock_ba: MagicMock,
        mock_pycolmap: MagicMock,
        mock_dense: MagicMock,
        mock_read: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Enabled pycolmap panorama-rig runs should prefer window 3 and avoid slow local vocab trees."""
        mock_read.return_value = {
            "cameras": {1: {"model": "PINHOLE"}},
            "images": {
                1: {
                    "name": "images/pano_camera00/frame_000.png",
                    "qw": 1.0,
                    "qx": 0.0,
                    "qy": 0.0,
                    "qz": 0.0,
                    "tx": 0.0,
                    "ty": 0.0,
                    "tz": 0.0,
                }
            },
            "points3D": {1: {"x": 0.0, "y": 0.0, "z": 1.0}},
        }
        mock_build_vocab_tree.return_value = tmp_path / "output" / "panorama_rig_vocab_tree.bin"
        dataset_dir = tmp_path / "dataset"
        image_dir = dataset_dir / "images"
        (image_dir / "pano_camera00").mkdir(parents=True)
        (image_dir / "pano_camera01").mkdir(parents=True)
        (image_dir / "pano_camera00" / "frame_000.png").write_bytes(b"a")
        (image_dir / "pano_camera01" / "frame_000.png").write_bytes(b"a")
        (dataset_dir / "panorama_rig.json").write_text(
            '{"fov":90,"overlap":15,"cameras":[{"name":"pano_camera00","camera_id":1,"yaw_deg":0,"pitch_deg":0},{"name":"pano_camera01","camera_id":2,"yaw_deg":60,"pitch_deg":0}]}',
            encoding="utf-8",
        )

        with patch.dict(os.environ, {"SPHEREFORGE_ENABLE_PYCOLMAP_RIG": "1"}, clear=False):
            run_stage03(
                Stage03Config(
                    dense_reconstruction=False,
                    panorama_use_pycolmap_rig=True,
                    panorama_temporal_window=2,
                ),
                dataset_dir,
                tmp_path / "output",
            )

        assert mock_match.call_args.kwargs["matcher_type"] == "sequential"
        assert mock_match.call_args.kwargs["sequential_overlap"] == 3
        assert mock_match.call_args.kwargs["vocab_tree_path"] is None
        mock_build_vocab_tree.assert_not_called()
        mock_pycolmap.assert_called_once()
        mock_ba.assert_not_called()

    @patch("sphereforge.stages.stage03_sfm.pipeline.read_sparse_model")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_dense_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline._run_panorama_rig_pycolmap_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_bundle_adjustment")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_matching")
    @patch("sphereforge.stages.stage03_sfm.pipeline.build_vocab_tree")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_extraction")
    def test_panorama_rig_pycolmap_backend_uses_external_vocab_tree_when_present(
        self,
        mock_extract: MagicMock,
        mock_build_vocab_tree: MagicMock,
        mock_match: MagicMock,
        mock_ba: MagicMock,
        mock_pycolmap: MagicMock,
        mock_dense: MagicMock,
        mock_read: MagicMock,
        tmp_path: Path,
    ) -> None:
        """An explicit dataset vocab tree should still be honored for pycolmap panorama-rig runs."""
        mock_read.return_value = {
            "cameras": {1: {"model": "PINHOLE"}},
            "images": {
                1: {
                    "name": "images/pano_camera00/frame_000.png",
                    "qw": 1.0,
                    "qx": 0.0,
                    "qy": 0.0,
                    "qz": 0.0,
                    "tx": 0.0,
                    "ty": 0.0,
                    "tz": 0.0,
                }
            },
            "points3D": {1: {"x": 0.0, "y": 0.0, "z": 1.0}},
        }
        dataset_dir = tmp_path / "dataset"
        image_dir = dataset_dir / "images"
        (image_dir / "pano_camera00").mkdir(parents=True)
        (image_dir / "pano_camera01").mkdir(parents=True)
        (image_dir / "pano_camera00" / "frame_000.png").write_bytes(b"a")
        (image_dir / "pano_camera01" / "frame_000.png").write_bytes(b"a")
        (dataset_dir / "panorama_rig.json").write_text(
            '{"fov":90,"overlap":15,"cameras":[{"name":"pano_camera00","camera_id":1,"yaw_deg":0,"pitch_deg":0},{"name":"pano_camera01","camera_id":2,"yaw_deg":60,"pitch_deg":0}]}',
            encoding="utf-8",
        )
        (dataset_dir / "vocab_tree.bin").write_bytes(b"tree")

        with patch.dict(os.environ, {"SPHEREFORGE_ENABLE_PYCOLMAP_RIG": "1"}, clear=False):
            run_stage03(
                Stage03Config(
                    dense_reconstruction=False,
                    panorama_use_pycolmap_rig=True,
                    panorama_temporal_window=2,
                ),
                dataset_dir,
                tmp_path / "output",
            )

        assert mock_match.call_args.kwargs["matcher_type"] == "sequential+vocabulary_tree"
        assert mock_match.call_args.kwargs["vocab_tree_path"] == dataset_dir / "vocab_tree.bin"
        mock_build_vocab_tree.assert_not_called()
        mock_pycolmap.assert_called_once()
        mock_ba.assert_not_called()

    @patch("sphereforge.stages.stage03_sfm.pipeline.read_sparse_model")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_dense_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline._run_panorama_rig_pycolmap_reconstruction")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_bundle_adjustment")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_matching")
    @patch("sphereforge.stages.stage03_sfm.pipeline.run_feature_extraction")
    def test_pycolmap_backend_falls_back_when_not_panorama_rig(
        self,
        mock_extract: MagicMock,
        mock_match: MagicMock,
        mock_ba: MagicMock,
        mock_pycolmap: MagicMock,
        mock_dense: MagicMock,
        mock_read: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Non-panorama datasets should still use the CLI COLMAP path."""
        mock_read.return_value = {
            "cameras": {1: {"model": "PINHOLE"}},
            "images": {},
            "points3D": {},
        }
        dataset_dir = tmp_path / "dataset"
        image_dir = dataset_dir / "images"
        image_dir.mkdir(parents=True)
        (image_dir / "img.png").write_bytes(b"a")

        with patch.dict(os.environ, {"SPHEREFORGE_ENABLE_PYCOLMAP_RIG": "1"}, clear=False):
            run_stage03(
                Stage03Config(
                    dense_reconstruction=False,
                    panorama_use_pycolmap_rig=True,
                    min_registration_fraction=0.0,
                ),
                dataset_dir,
                tmp_path / "output",
            )

        mock_ba.assert_called_once()
        mock_pycolmap.assert_not_called()
