"""Stage 3.1: COLMAP feature extraction.

Wraps the COLMAP ``feature_extractor`` CLI to detect SIFT / RootSIFT
keypoints and write them into a COLMAP database.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger("sphereforge.stage03.feature_extraction")


def _check_colmap_installed() -> None:
    """Verify that the ``colmap`` executable is on PATH.

    Raises:
        RuntimeError: If COLMAP is not found.
    """
    if shutil.which("colmap") is None:
        raise RuntimeError(
            "COLMAP is not installed or not on PATH. "
            "Install COLMAP and ensure the `colmap` command is available."
        )


def run_feature_extraction(
    database_path: Path,
    image_dir: Path,
    camera_model: str = "PINHOLE",
    feature_type: str = "root_sift",
    mask_dir: Path | None = None,
    single_camera_per_folder: bool = False,
    image_list: Sequence[str] | None = None,
) -> None:
    """Run COLMAP feature extraction on a set of images.

    Calls the COLMAP ``feature_extractor`` command via subprocess.  When
    *mask_dir* is provided, an ``--image_list`` file is written so that
    COLMAP only processes images that have a corresponding mask.

    Args:
        database_path: Path to the COLMAP database file (created if missing).
        image_dir: Directory containing input images.
        camera_model: COLMAP camera model name (e.g. ``"PINHOLE"``).
        feature_type: ``"root_sift"`` or ``"sift"``.
        mask_dir: Optional directory of mask images.  When given, only
            images that have a corresponding mask file are included.

    Raises:
        RuntimeError: If COLMAP is not installed or if the subprocess
            returns a non-zero exit code.
    """
    _check_colmap_installed()

    cmd: list[str] = [
        "colmap", "feature_extractor",
        "--database_path", str(database_path),
        "--image_path", str(image_dir),
        "--ImageReader.camera_model", camera_model,
    ]
    if single_camera_per_folder:
        cmd.extend(["--ImageReader.single_camera_per_folder", "1"])
    else:
        cmd.extend(["--ImageReader.single_camera", "1"])
    root_sift_enabled = "1" if feature_type == "root_sift" else "0"
    cmd.extend(["--SiftExtraction.root_sift", root_sift_enabled])

    # If mask_dir is provided, build an image list file with only the
    # images that have a corresponding mask. Panorama-rig layouts also use
    # this path to enforce a stable per-folder ordering for sequential matching.
    temp_image_list: Path | None = None
    requested_images = list(image_list) if image_list is not None else None
    if requested_images is not None or mask_dir is not None:
        mask_dir_path = Path(mask_dir) if mask_dir is not None else None
        image_names = requested_images
        if image_names is None:
            image_names = sorted(
                path.relative_to(image_dir).as_posix()
                for path in Path(image_dir).rglob("*")
                if path.is_file()
            )

        if mask_dir_path is not None:
            mask_names = {
                path.relative_to(mask_dir_path).with_suffix("").as_posix()
                for path in mask_dir_path.rglob("*")
                if path.is_file()
            }
            filtered_names = [
                image_name
                for image_name in image_names
                if Path(image_name).with_suffix("").as_posix() in mask_names
            ]
            if not filtered_names:
                logger.warning(
                    "No images in %s match masks in %s; falling back to all images",
                    image_dir,
                    mask_dir_path,
                )
            else:
                image_names = filtered_names

        if image_names:
            tmp = tempfile.NamedTemporaryFile(  # noqa: SIM115
                mode="w", suffix=".txt", delete=False, prefix="colmap_imagelist_"
            )
            for image_name in image_names:
                tmp.write(f"{image_name}\n")
            tmp.close()
            temp_image_list = Path(tmp.name)
            cmd.extend(["--image_list_path", str(temp_image_list)])
            logger.info("Using explicit image list with %d images", len(image_names))

    logger.info(
        "Running COLMAP feature_extractor: database=%s, images=%s, "
        "camera_model=%s, feature_type=%s, single_camera_per_folder=%s",
        database_path,
        image_dir,
        camera_model,
        feature_type,
        single_camera_per_folder,
    )

    try:
        env = {
            **os.environ,
            "QT_QPA_PLATFORM": "offscreen",
            "PATH": "/home/tngai/.local/bin:" + os.environ.get("PATH", ""),
                            "LD_LIBRARY_PATH": "/home/tngai/miniconda3/lib:" + os.environ.get("LD_LIBRARY_PATH", ""),
        }
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
        if result.returncode != 0 and "unrecognised option '--SiftExtraction.root_sift'" in result.stderr:
            descriptor_norm = "l1_root" if feature_type == "root_sift" else "l2"
            fallback_cmd = list(cmd)
            root_sift_idx = fallback_cmd.index("--SiftExtraction.root_sift")
            del fallback_cmd[root_sift_idx : root_sift_idx + 2]
            fallback_cmd.extend(["--descriptor_normalization", descriptor_norm])
            logger.info(
                "COLMAP build does not support --SiftExtraction.root_sift; retrying with --descriptor_normalization=%s",
                descriptor_norm,
            )
            result = subprocess.run(
                fallback_cmd,
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
        if result.returncode != 0:
            logger.error("COLMAP feature_extractor stderr:\n%s", result.stderr)
            raise RuntimeError(
                f"COLMAP feature_extractor failed (exit code {result.returncode}): "
                f"{result.stderr[:500]}"
            )
        logger.info("Feature extraction completed successfully.")
    finally:
        # Clean up temporary image list file
        if temp_image_list is not None and temp_image_list.exists():
            temp_image_list.unlink()
