"""Stage 3.5: COLMAP dense reconstruction.

Runs image undistortion, patch-match stereo, and stereo fusion to
produce a dense point cloud from the sparse reconstruction.
"""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from sphereforge.config import Stage03Config

logger = logging.getLogger("sphereforge.stage03.dense_reconstruction")


def _run_subprocess(cmd: list[str], step_name: str) -> None:
    """Run a subprocess command and log errors on failure.

    Args:
        cmd: Command and arguments to execute.
        step_name: Human-readable name for logging.

    Raises:
        RuntimeError: If the subprocess returns non-zero.
    """
    logger.info("Running COLMAP %s: %s", step_name, " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, check=False,
                            env={
                                **os.environ,
                                "QT_QPA_PLATFORM": "offscreen",
                                "PATH": "/home/tngai/.local/bin:" + os.environ.get("PATH", ""),
                            "LD_LIBRARY_PATH": "/home/tngai/miniconda3/lib:"
                                + os.environ.get("LD_LIBRARY_PATH", ""),
                            })
    if result.returncode != 0:
        logger.error("COLMAP %s stderr:\n%s", step_name, result.stderr)
        raise RuntimeError(
            f"COLMAP {step_name} failed (exit code {result.returncode}): "
            f"{result.stderr[:500]}"
        )
    logger.info("COLMAP %s completed successfully.", step_name)


def run_dense_reconstruction(
    sparse_dir: Path,
    image_dir: Path,
    dense_dir: Path,
) -> None:
    """Run COLMAP dense reconstruction pipeline.

    Executes three COLMAP commands in sequence:

    1. ``image_undistorter`` — undistort images for dense stereo.
    2. ``patch_match_stereo`` — compute depth and normal maps.
    3. ``stereo_fusion`` — fuse depth maps into a dense point cloud.

    This function is config-gated: it only runs when
    ``Stage03Config.dense_reconstruction`` is ``True``.  Callers should
    check the config before calling, but the function also performs an
    internal check as a safety net.

    Args:
        sparse_dir: Directory containing the COLMAP sparse model.
        image_dir: Directory containing the input images.
        dense_dir: Output directory for the dense reconstruction.

    Raises:
        RuntimeError: If any COLMAP subprocess returns non-zero.
        RuntimeError: If the config disables dense reconstruction.
    """
    # Config gate — check default config value
    default_config = Stage03Config()
    if not default_config.dense_reconstruction:
        logger.info(
            "Dense reconstruction disabled in config (dense_reconstruction=False). "
            "Skipping."
        )
        return

    sparse_dir = Path(sparse_dir)
    image_dir = Path(image_dir)
    dense_dir = Path(dense_dir)
    dense_dir.mkdir(parents=True, exist_ok=True)

    # The mapper typically puts the model in sparse_dir/0/
    sparse_model_dir = sparse_dir / "0"
    if not sparse_model_dir.exists():
        # Try using sparse_dir directly
        if (sparse_dir / "cameras.bin").exists() or (sparse_dir / "cameras.txt").exists():
            sparse_model_dir = sparse_dir
        else:
            subdirs = sorted(d for d in sparse_dir.iterdir() if d.is_dir())
            if subdirs:
                sparse_model_dir = subdirs[0]
            else:
                raise FileNotFoundError(
                    f"No sparse model found in {sparse_dir} for dense reconstruction."
                )

    # Step 1: Image undistortion
    cmd_undistort: list[str] = [
        "colmap", "image_undistorter",
        "--image_path", str(image_dir),
        "--input_path", str(sparse_model_dir),
        "--output_path", str(dense_dir),
        "--output_type", "COLMAP",
    ]
    _run_subprocess(cmd_undistort, "image_undistorter")

    # Step 2: Patch-match stereo
    cmd_patch_match: list[str] = [
        "colmap", "patch_match_stereo",
        "--workspace_path", str(dense_dir),
    ]
    _run_subprocess(cmd_patch_match, "patch_match_stereo")

    # Step 3: Stereo fusion
    cmd_fusion: list[str] = [
        "colmap", "stereo_fusion",
        "--workspace_path", str(dense_dir),
        "--output_path", str(dense_dir / "fused.ply"),
    ]
    _run_subprocess(cmd_fusion, "stereo_fusion")

    logger.info("Dense reconstruction completed. Output in %s", dense_dir)
