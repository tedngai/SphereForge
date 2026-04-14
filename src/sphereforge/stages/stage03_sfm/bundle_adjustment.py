"""Stage 3.3: COLMAP bundle adjustment (mapper + bundle_adjuster).

Runs the COLMAP ``mapper`` to build a sparse 3D model, then optionally
refines it with the ``bundle_adjuster`` command.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("sphereforge.stage03.bundle_adjustment")


def _run_colmap_mapper(
    database_path: Path,
    image_dir: Path,
    output_path: Path,
) -> None:
    """Execute the COLMAP mapper to produce a sparse reconstruction.

    Args:
        database_path: Path to the COLMAP database.
        image_dir: Directory containing input images.
        output_path: Directory where the mapper writes its output
            (``0/`` subdirectory with sparse model).

    Raises:
        RuntimeError: If the mapper subprocess returns non-zero.
    """
    cmd: list[str] = [
        "colmap", "mapper",
        "--database_path", str(database_path),
        "--image_path", str(image_dir),
        "--output_path", str(output_path),
    ]

    logger.info(
        "Running COLMAP mapper: database=%s, images=%s, output=%s",
        database_path,
        image_dir,
        output_path,
    )
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        logger.error("COLMAP mapper stderr:\n%s", result.stderr)
        raise RuntimeError(
            f"COLMAP mapper failed (exit code {result.returncode}): "
            f"{result.stderr[:500]}"
        )
    logger.info("COLMAP mapper completed successfully.")


def _run_colmap_bundle_adjuster(
    input_path: Path,
    output_path: Path,
    refine_focal_length: bool,
    refine_extra_params: bool,
) -> None:
    """Execute the COLMAP bundle_adjuster to refine the sparse model.

    Args:
        input_path: Path to the input sparse model directory.
        output_path: Path where refined model is written.
        refine_focal_length: Whether to refine focal lengths.
        refine_extra_params: Whether to refine extra distortion params.

    Raises:
        RuntimeError: If the bundle_adjuster subprocess returns non-zero.
    """
    cmd: list[str] = [
        "colmap", "bundle_adjuster",
        "--input_path", str(input_path),
        "--output_path", str(output_path),
        "--BundleAdjustment.refine_focal_length", str(int(refine_focal_length)),
        "--BundleAdjustment.refine_extra_params", str(int(refine_extra_params)),
    ]

    logger.info(
        "Running COLMAP bundle_adjuster: input=%s, output=%s, "
        "refine_focal_length=%s, refine_extra_params=%s",
        input_path,
        output_path,
        refine_focal_length,
        refine_extra_params,
    )
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        logger.error("COLMAP bundle_adjuster stderr:\n%s", result.stderr)
        raise RuntimeError(
            f"COLMAP bundle_adjuster failed (exit code {result.returncode}): "
            f"{result.stderr[:500]}"
        )
    logger.info("COLMAP bundle_adjuster completed successfully.")


def run_bundle_adjustment(
    database_path: Path,
    sparse_dir: Path,
    refine_intrinsics: bool = False,
    image_dir: Path | None = None,
) -> None:
    """Run COLMAP mapper and optional bundle adjustment.

    First runs the COLMAP ``mapper`` to produce an initial sparse
    reconstruction.  Then runs ``bundle_adjuster`` with the
    *refine_intrinsics* flag controlling whether focal length and
    extra distortion parameters are refined.

    The *sparse_dir* is created if it does not already exist.  The mapper
    writes its output to ``sparse_dir/`` (typically a ``0/`` subdirectory).
    After the mapper, bundle_adjuster reads from ``0/`` and writes the
    refined model back to the same directory.

    Args:
        database_path: Path to the COLMAP database.
        sparse_dir: Output directory for the sparse model.
        refine_intrinsics: If ``True``, allow bundle adjustment to refine
            camera focal lengths and distortion parameters.  Defaults to
            ``False`` since intrinsics are known from Stage 2.
        image_dir: Directory containing input images.  Required by the
            mapper.  If ``None``, the function will attempt to infer it
            from the parent of *database_path*.

    Raises:
        RuntimeError: If either COLMAP subprocess returns non-zero.
    """
    database_path = Path(database_path)
    sparse_dir = Path(sparse_dir)
    sparse_dir.mkdir(parents=True, exist_ok=True)

    if image_dir is None:
        # Try to infer image directory from database path structure
        image_dir = database_path.parent / "images"
        logger.warning(
            "image_dir not specified; inferred as %s. "
            "Pass image_dir explicitly for reliable results.",
            image_dir,
        )
    image_dir = Path(image_dir)

    # Step 1: Run mapper
    _run_colmap_mapper(database_path, image_dir, sparse_dir)

    # Step 2: Run bundle_adjuster on the mapper output
    # The mapper creates a subdirectory (usually "0/") inside sparse_dir
    mapper_output = sparse_dir / "0"
    if not mapper_output.exists():
        # Fallback: look for any subdirectory the mapper may have created
        subdirs = [d for d in sparse_dir.iterdir() if d.is_dir()]
        if subdirs:
            mapper_output = subdirs[0]
            logger.info("Using mapper output from %s", mapper_output)
        else:
            logger.warning(
                "No mapper output subdirectory found in %s; "
                "skipping bundle_adjuster.",
                sparse_dir,
            )
            return

    _run_colmap_bundle_adjuster(
        input_path=mapper_output,
        output_path=mapper_output,
        refine_focal_length=refine_intrinsics,
        refine_extra_params=refine_intrinsics,
    )

    logger.info(
        "Bundle adjustment completed (refine_intrinsics=%s).", refine_intrinsics
    )
