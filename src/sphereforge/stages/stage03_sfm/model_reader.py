"""Stage 3.4: Read COLMAP sparse and dense models.

Provides functions to parse both text and binary COLMAP output formats
using helpers from ``sphereforge.common.colmap_helpers``.
"""

from __future__ import annotations

import logging
import struct
from pathlib import Path

from sphereforge.common.colmap_helpers import (
    parse_cameras_txt,
    parse_images_txt,
    parse_points3d_txt,
    read_colmap_binary,
)

logger = logging.getLogger("sphereforge.stage03.model_reader")


def _count_points3d(path: Path) -> int:
    """Count points in a COLMAP points3D file (.bin or .txt), cheaply."""
    try:
        if path.suffix == ".bin":
            with open(path, "rb") as f:
                return int(struct.unpack("<Q", f.read(8))[0])
        with open(path, encoding="utf-8") as f:
            return sum(1 for line in f if line.strip() and not line.startswith("#"))
    except (OSError, struct.error):
        return 0


def _select_best_model_dir(sparse_dir: Path) -> Path:
    """Pick the largest sub-model when a COLMAP run produced several.

    Incremental mapping can emit more than one reconstruction
    (``sparse/0``, ``sparse/1``, ...). Downstream stages need the model with
    the most registered images, not whichever folder happens to be first.
    """
    candidates = [
        d
        for d in sorted(sparse_dir.iterdir())
        if d.is_dir()
        and (
            (d / "images.bin").exists()
            or (d / "images.txt").exists()
            or (d / "cameras.bin").exists()
            or (d / "cameras.txt").exists()
        )
    ]
    if len(candidates) <= 1:
        return candidates[0] if candidates else sparse_dir

    def score(d: Path) -> tuple[int, int]:
        points = max(
            _count_points3d(d / "points3D.bin"),
            _count_points3d(d / "points3D.txt"),
        )
        images_size = max(
            (d / "images.bin").stat().st_size if (d / "images.bin").exists() else 0,
            (d / "images.txt").stat().st_size if (d / "images.txt").exists() else 0,
        )
        return (points, images_size)

    best = max(candidates, key=score)
    logger.info(
        "Multiple COLMAP sub-models found in %s; using %s (scores: %s)",
        sparse_dir,
        best.name,
        {d.name: score(d) for d in candidates},
    )
    return best


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

    # If the caller passes the parent (e.g. sparse/), look for a sub-model.
    if not (sparse_dir / "cameras.txt").exists() and not (sparse_dir / "cameras.bin").exists():
        sub = _select_best_model_dir(sparse_dir)
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

    model = {
        "cameras": cameras,
        "images": images,
        "points3D": points3D,
        # Remember where this came from so a rescaled model can be written back.
        "_source_dir": str(sparse_dir),
    }
    # Panorama-rig poses are corrected out-of-band (pycolmap cannot store a
    # rig whose sensors share one optical centre), so fold them in here where
    # every downstream consumer picks them up.
    from sphereforge.stages.stage03_sfm.rigidity import apply_rigidity_to_model

    return apply_rigidity_to_model(model)


def write_sparse_model(model: dict, sparse_dir: Path) -> None:
    """Write a sparse model back to disk as COLMAP text files.

    Only the fields that downstream stages consume are written (camera
    intrinsics/poses and 3D point positions/colours), which is sufficient for
    re-reading through :func:`read_sparse_model`.

    Args:
        model: Sparse model as returned by :func:`read_sparse_model`.
        sparse_dir: Destination directory (created if missing).
    """
    sparse_dir = Path(sparse_dir)
    sparse_dir.mkdir(parents=True, exist_ok=True)

    with (sparse_dir / "cameras.txt").open("w", encoding="utf-8") as handle:
        handle.write("# Camera list with one line of data per camera:\n")
        handle.write("#   CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n")
        for cam_id, cam in model["cameras"].items():
            params = " ".join(str(float(p)) for p in cam.get("params", []))
            handle.write(
                f"{cam_id} {cam.get('model', 'SIMPLE_RADIAL')} "
                f"{cam.get('width', 0)} {cam.get('height', 0)} {params}\n"
            )

    with (sparse_dir / "images.txt").open("w", encoding="utf-8") as handle:
        handle.write("# Image list with two lines of data per image:\n")
        handle.write("#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME\n")
        handle.write("#   POINTS2D[] as (X, Y, POINT3D_ID)\n")
        for img_id, img in model["images"].items():
            handle.write(
                f"{img_id} {img['qw']} {img['qx']} {img['qy']} {img['qz']} "
                f"{img['tx']} {img['ty']} {img['tz']} {img['camera_id']} {img['name']}\n"
            )
            handle.write("\n")

    with (sparse_dir / "points3D.txt").open("w", encoding="utf-8") as handle:
        handle.write("# 3D point list with one line of data per point:\n")
        handle.write("#   POINT3D_ID, X, Y, Z, R, G, B, ERROR, TRACK[]\n")
        for pid, pt in model["points3D"].items():
            handle.write(
                f"{pid} {pt['x']} {pt['y']} {pt['z']} "
                f"{pt.get('r', 128)} {pt.get('g', 128)} {pt.get('b', 128)} "
                f"{pt.get('error', 0.0)}\n"
            )

    logger.info("Wrote sparse model to %s", sparse_dir)


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
