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

    descriptor_norm = "l1_root" if feature_type == "root_sift" else "l2"

    cmd: list[str] = [
        "colmap", "feature_extractor",
        "--database_path", str(database_path),
        "--image_path", str(image_dir),
        "--ImageReader.camera_model", camera_model,
        "--ImageReader.single_camera", "1",
        "--descriptor_normalization", descriptor_norm,
    ]

    # If mask_dir is provided, build an image list file with only the
    # images that have a corresponding mask.
    temp_image_list: Path | None = None
    if mask_dir is not None:
        mask_dir = Path(mask_dir)
        mask_names = {p.stem for p in mask_dir.iterdir() if p.is_file()}
        image_files = sorted(
            p for p in Path(image_dir).iterdir()
            if p.is_file() and p.stem in mask_names
        )
        if not image_files:
            logger.warning(
                "No images in %s match masks in %s; falling back to all images",
                image_dir,
                mask_dir,
            )
        else:
            # Write a temporary image-list file
            tmp = tempfile.NamedTemporaryFile(  # noqa: SIM115
                mode="w", suffix=".txt", delete=False, prefix="colmap_imagelist_"
            )
            for img_path in image_files:
                tmp.write(f"{img_path.name}\n")
            tmp.close()
            temp_image_list = Path(tmp.name)
            cmd.extend(["--image_list_path", str(temp_image_list)])
            logger.info(
                "Using mask-aware image list with %d images", len(image_files)
            )

    logger.info(
        "Running COLMAP feature_extractor: database=%s, images=%s, "
        "camera_model=%s, feature_type=%s",
        database_path,
        image_dir,
        camera_model,
        feature_type,
    )

    try:
        env = {
            **os.environ,
            "QT_QPA_PLATFORM": "offscreen",
            "PATH": "/home/tngai/.local/bin:" + os.environ.get("PATH", ""),
                            "LD_LIBRARY_PATH": "/home/tngai/miniconda3/lib:" + os.environ.get("LD_LIBRARY_PATH", ""),
        }
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
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
