"""Stage 3.4: Read COLMAP sparse and dense models.

Provides functions to parse both text and binary COLMAP output formats
using helpers from ``sphereforge.common.colmap_helpers``.
"""

from __future__ import annotations

import logging
from pathlib import Path

from sphereforge.common.colmap_helpers import (
    parse_cameras_txt,
    parse_images_txt,
    parse_points3d_txt,
    read_colmap_binary,
)

logger = logging.getLogger("sphereforge.stage03.model_reader")


def read_sparse_model(sparse_dir: Path) -> dict:
    """Read a COLMAP sparse reconstruction from disk.

    Supports both the text format (``cameras.txt``, ``images.txt``,
    ``points3D.txt``) and the binary format (``cameras.bin``,
    ``images.bin``, ``points3D.bin``).  If text files are present they
    take precedence; otherwise the binary readers are used.

    Args:
        sparse_dir: Directory containing the COLMAP sparse model files.
            This is typically ``sparse/0/`` or ``sparse/``.

    Returns:
        Dict with keys ``"cameras"``, ``"images"``, ``"points3D"``, each
        mapping to the dict returned by the respective parser.

    Raises:
        FileNotFoundError: If no recognised model files are found.
    """
    sparse_dir = Path(sparse_dir)

    # If the caller passes the parent (e.g. sparse/), look for the "0" subdir
    if not (sparse_dir / "cameras.txt").exists() and not (sparse_dir / "cameras.bin").exists():
        sub = sparse_dir / "0"
        if sub.is_dir():
            sparse_dir = sub
            logger.debug("Redirected sparse model read to %s", sub)

    cameras: dict
    images: dict
    points3D: dict

    # Prefer text format
    txt_cameras = sparse_dir / "cameras.txt"
    txt_images = sparse_dir / "images.txt"
    txt_points = sparse_dir / "points3D.txt"

    bin_cameras = sparse_dir / "cameras.bin"
    bin_images = sparse_dir / "images.bin"
    bin_points = sparse_dir / "points3D.bin"

    if txt_cameras.exists() and txt_images.exists() and txt_points.exists():
        logger.info("Reading sparse model in text format from %s", sparse_dir)
        cameras = parse_cameras_txt(txt_cameras)
        images = parse_images_txt(txt_images)
        points3D = parse_points3d_txt(txt_points)
    elif bin_cameras.exists() and bin_images.exists() and bin_points.exists():
        logger.info("Reading sparse model in binary format from %s", sparse_dir)
        cameras = read_colmap_binary(bin_cameras)
        images = read_colmap_binary(bin_images)
        points3D = read_colmap_binary(bin_points)
    else:
        raise FileNotFoundError(
            f"No COLMAP sparse model files found in {sparse_dir}. "
            f"Expected cameras.txt/images.txt/points3D.txt or "
            f"cameras.bin/images.bin/points3D.bin."
        )

    logger.info(
        "Read sparse model: %d cameras, %d images, %d 3D points",
        len(cameras),
        len(images),
        len(points3D),
    )

    return {
        "cameras": cameras,
        "images": images,
        "points3D": points3D,
    }


def read_dense_model(dense_dir: Path) -> dict:
    """Read a COLMAP dense reconstruction from disk.

    COLMAP dense output includes a refined sparse model in
    ``dense/sparse/`` alongside fused point clouds.  This function
    reads the sparse model component of the dense reconstruction.

    Supports both text and binary formats, just like
    :func:`read_sparse_model`.

    Args:
        dense_dir: Directory containing the COLMAP dense output
            (e.g. ``dense/`` or ``dense/0/``).

    Returns:
        Dict with keys ``"cameras"``, ``"images"``, ``"points3D"``.

    Raises:
        FileNotFoundError: If no recognised model files are found.
    """
    dense_dir = Path(dense_dir)

    # The sparse model for dense reconstruction is typically in dense/sparse/
    sparse_in_dense = dense_dir / "sparse"
    if sparse_in_dense.is_dir():
        return read_sparse_model(sparse_in_dense)

    # Fall back to reading directly from dense_dir
    return read_sparse_model(dense_dir)
