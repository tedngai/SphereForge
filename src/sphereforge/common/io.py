"""Common I/O utilities for SphereForge.

Provides functions for reading and writing images, depth maps, 3DGS PLY files,
and COLMAP text-format reconstruction files. All functions use pathlib.Path for
file paths and raise helpful errors when files are missing or malformed.
"""

from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np
from plyfile import PlyData, PlyElement

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Image I/O
# ---------------------------------------------------------------------------


def read_image(path: Path) -> np.ndarray:
    """Read an image file and return it as an RGB numpy array.

    Uses OpenCV to read the image (which loads in BGR order) and converts
    to RGB before returning.

    Args:
        path: Path to the image file (e.g. .png, .jpg).

    Returns:
        Image array of shape (H, W, 3) with dtype uint8 in RGB channel order.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file cannot be read as an image.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Failed to read image (unsupported format or corrupt): {path}")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def write_image(path: Path, image: np.ndarray) -> None:
    """Write an RGB image array to a file, creating parent directories as needed.

    Converts the image from RGB to BGR (OpenCV convention) before writing.

    Args:
        path: Destination file path. The extension determines the format.
        image: Image array of shape (H, W, 3) with dtype uint8 in RGB order.

    Raises:
        ValueError: If OpenCV fails to write the image.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    success = cv2.imwrite(str(path), bgr)
    if not success:
        raise ValueError(f"Failed to write image to: {path}")


# ---------------------------------------------------------------------------
# Depth I/O
# ---------------------------------------------------------------------------


def read_depth(path: Path) -> np.ndarray:
    """Read a depth map from a .npy file.

    Args:
        path: Path to the .npy file containing the depth map.

    Returns:
        Depth array of shape (H, W) with dtype float32.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file cannot be loaded or has an unexpected shape/dtype.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Depth file not found: {path}. "
            "Ensure depth estimation has been run and the output path is correct."
        )
    depth = np.load(str(path))
    if depth.dtype != np.float32:
        logger.debug("Casting depth from %s to float32 for %s", depth.dtype, path)
        depth = depth.astype(np.float32)
    if depth.ndim != 2:
        raise ValueError(
            f"Expected depth map with 2 dimensions (H, W), got {depth.ndim}D "
            f"with shape {depth.shape} from {path}"
        )
    return depth


def write_depth(path: Path, depth: np.ndarray) -> None:
    """Save a depth map as a .npy file in float32 format.

    Creates parent directories if they do not exist.

    Args:
        path: Destination file path (should end in .npy).
        depth: Depth array of shape (H, W). Will be cast to float32 if needed.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    depth = depth.astype(np.float32)
    np.save(str(path), depth)
    logger.debug("Wrote depth map (%s) to %s", depth.shape, path)


# ---------------------------------------------------------------------------
# 3DGS PLY I/O
# ---------------------------------------------------------------------------


def _extract_vertex_prop(vertex: PlyElement, name: str) -> np.ndarray | None:
    """Extract a property array from a PLY vertex element.

    Args:
        vertex: The vertex PlyElement.
        name: Property name to look up.

    Returns:
        1-D numpy array with the property values, or None if the property
        does not exist in the element.
    """
    for prop in vertex.properties:
        if prop.name == name:
            return vertex[name]
    return None


def read_ply(path: Path) -> dict:
    """Read a 3D Gaussian Splatting PLY file.

    Supports both binary and ASCII PLY formats via plyfile. The returned
    dictionary follows 3DGS property naming conventions (f_dc_N for DC SH
    coefficients, f_rest_N for higher-degree SH coefficients).

    Args:
        path: Path to the .ply file.

    Returns:
        Dictionary with the following keys:

        - **positions** (np.ndarray): Nx3 float32 — x, y, z coordinates.
        - **colors** (np.ndarray): Nx3 uint8 or Nx3 float32 — per-Gaussian
          colours. Stored as uint8 when the PLY uses ``red``/``green``/``blue``
          uchar properties; float32 when the PLY uses ``f_dc_0``/``1``/``2``.
        - **opacities** (np.ndarray): N float32 — opacity values.
        - **scales** (np.ndarray): Nx3 float32 — scale_0, scale_1, scale_2.
        - **rotations** (np.ndarray): Nx4 float32 — rot_0 … rot_3 (quaternion).
        - **sh_coeffs** (np.ndarray | None): Nx48 float32 combining DC (3)
          and rest (45) SH coefficients for degree 3, or None if the file
          contains no ``f_rest`` properties.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a valid PLY or is missing required
            3DGS properties.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PLY file not found: {path}")

    try:
        ply = PlyData.read(str(path))
    except Exception as exc:
        raise ValueError(f"Failed to read PLY file {path}: {exc}") from exc

    if "vertex" not in [e.name for e in ply.elements]:
        raise ValueError(f"PLY file {path} does not contain a 'vertex' element.")

    vertex = ply["vertex"]
    prop_names = {p.name for p in vertex.properties}
    n = vertex.count

    # ---- Positions (required) ----
    for ax in ("x", "y", "z"):
        if ax not in prop_names:
            raise ValueError(f"PLY file {path} is missing required property '{ax}'.")
    positions = np.stack([vertex["x"], vertex["y"], vertex["z"]], axis=-1).astype(np.float32)

    # ---- Colors / f_dc (required) ----
    if all(p in prop_names for p in ("f_dc_0", "f_dc_1", "f_dc_2")):
        colors = np.stack(
            [vertex["f_dc_0"], vertex["f_dc_1"], vertex["f_dc_2"]], axis=-1
        ).astype(np.float32)
    elif all(p in prop_names for p in ("red", "green", "blue")):
        colors = np.stack(
            [vertex["red"], vertex["green"], vertex["blue"]], axis=-1
        ).astype(np.uint8)
    elif all(p in prop_names for p in ("nx", "ny", "nz")):
        # Some 3DGS files reuse nx/ny/nz for f_dc_0/1/2
        logger.warning(
            "PLY %s uses nx/ny/nz instead of f_dc_0/1/2; "
            "treating them as DC SH coefficients.",
            path,
        )
        colors = np.stack(
            [vertex["nx"], vertex["ny"], vertex["nz"]], axis=-1
        ).astype(np.float32)
    else:
        raise ValueError(
            f"PLY file {path} is missing colour/DC SH properties. "
            "Expected f_dc_0/1/2 or red/green/blue."
        )

    # ---- Opacity (required) ----
    if "opacity" not in prop_names:
        raise ValueError(f"PLY file {path} is missing required property 'opacity'.")
    opacities = vertex["opacity"].astype(np.float32)

    # ---- Scales (required) ----
    for s in ("scale_0", "scale_1", "scale_2"):
        if s not in prop_names:
            raise ValueError(f"PLY file {path} is missing required property '{s}'.")
    scales = np.stack(
        [vertex["scale_0"], vertex["scale_1"], vertex["scale_2"]], axis=-1
    ).astype(np.float32)

    # ---- Rotations (required) ----
    for r in ("rot_0", "rot_1", "rot_2", "rot_3"):
        if r not in prop_names:
            raise ValueError(f"PLY file {path} is missing required property '{r}'.")
    rotations = np.stack(
        [vertex["rot_0"], vertex["rot_1"], vertex["rot_2"], vertex["rot_3"]], axis=-1
    ).astype(np.float32)

    # ---- SH rest coefficients (optional) ----
    f_rest_names = sorted(
        [p.name for p in vertex.properties if p.name.startswith("f_rest_")],
        key=lambda n: int(n.split("_")[-1]),
    )
    if f_rest_names:
        f_rest = np.stack([vertex[n] for n in f_rest_names], axis=-1).astype(np.float32)
        # sh_coeffs = DC (3) + rest (45) = 48 for degree 3
        if colors.dtype == np.float32 and colors.shape[-1] == 3:
            sh_coeffs = np.concatenate([colors, f_rest], axis=-1)
        else:
            # If colors are uint8 we cannot meaningfully combine with float32 rest;
            # store just the rest coefficients and pad DC with zeros.
            logger.warning(
                "Colors are uint8 but f_rest is float32; "
                "filling DC portion of sh_coeffs with zeros."
            )
            dc_zeros = np.zeros((n, 3), dtype=np.float32)
            sh_coeffs = np.concatenate([dc_zeros, f_rest], axis=-1)
    else:
        sh_coeffs = None

    logger.info(
        "Read PLY %s: %d gaussians, sh_coeffs=%s",
        path,
        n,
        f"Nx{sh_coeffs.shape[-1]}" if sh_coeffs is not None else "None",
    )

    return {
        "positions": positions,
        "colors": colors,
        "opacities": opacities,
        "scales": scales,
        "rotations": rotations,
        "sh_coeffs": sh_coeffs,
    }


def write_ply(
    path: Path,
    positions: np.ndarray,
    colors: np.ndarray,
    opacities: np.ndarray,
    scales: np.ndarray,
    rotations: np.ndarray,
    sh_coeffs: np.ndarray | None = None,
) -> None:
    """Write a 3D Gaussian Splatting PLY file in standard binary format.

    The PLY header follows 3DGS naming conventions: ``x/y/z``, ``f_dc_0/1/2``,
    ``opacity``, ``scale_0/1/2``, ``rot_0/1/2/3``, and optionally
    ``f_rest_0`` through ``f_rest_44`` for higher-degree spherical harmonics.

    Args:
        path: Destination file path (should end in .ply).
        positions: Nx3 float32 array of Gaussian centres.
        colors: Nx3 float32 array of DC SH coefficients (f_dc_0/1/2).
        opacities: N float32 array of opacity values.
        scales: Nx3 float32 array of per-axis scale values.
        rotations: Nx4 float32 array of quaternion rotations (rot_0..3).
        sh_coeffs: Optional Nx45 float32 array of remaining SH coefficients
            (f_rest_0 through f_rest_44) for degree 3. When None, only DC
            SH components are written.

    Raises:
        ValueError: If input arrays have inconsistent lengths or invalid shapes.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    n = positions.shape[0]

    # Validate shapes
    if positions.shape != (n, 3):
        raise ValueError(f"positions must be Nx3, got {positions.shape}")
    if colors.shape != (n, 3):
        raise ValueError(f"colors must be Nx3, got {colors.shape}")
    if opacities.shape != (n,):
        raise ValueError(f"opacities must be N, got {opacities.shape}")
    if scales.shape != (n, 3):
        raise ValueError(f"scales must be Nx3, got {scales.shape}")
    if rotations.shape != (n, 4):
        raise ValueError(f"rotations must be Nx4, got {rotations.shape}")
    if sh_coeffs is not None and sh_coeffs.shape != (n, 45):
        raise ValueError(
            f"sh_coeffs must be Nx45 for degree-3 SH, got {sh_coeffs.shape}"
        )

    # Cast types
    positions = positions.astype(np.float32)
    colors = colors.astype(np.float32)
    opacities = opacities.astype(np.float32)
    scales = scales.astype(np.float32)
    rotations = rotations.astype(np.float32)
    if sh_coeffs is not None:
        sh_coeffs = sh_coeffs.astype(np.float32)

    # Build structured dtype for the vertex element
    dtype_list = [
        ("x", "f4"), ("y", "f4"), ("z", "f4"),
        ("f_dc_0", "f4"), ("f_dc_1", "f4"), ("f_dc_2", "f4"),
        ("opacity", "f4"),
        ("scale_0", "f4"), ("scale_1", "f4"), ("scale_2", "f4"),
        ("rot_0", "f4"), ("rot_1", "f4"), ("rot_2", "f4"), ("rot_3", "f4"),
    ]
    if sh_coeffs is not None:
        for i in range(45):
            dtype_list.append((f"f_rest_{i}", "f4"))

    # Create structured array
    vertex_data = np.empty(n, dtype=dtype_list)
    vertex_data["x"] = positions[:, 0]
    vertex_data["y"] = positions[:, 1]
    vertex_data["z"] = positions[:, 2]
    vertex_data["f_dc_0"] = colors[:, 0]
    vertex_data["f_dc_1"] = colors[:, 1]
    vertex_data["f_dc_2"] = colors[:, 2]
    vertex_data["opacity"] = opacities
    vertex_data["scale_0"] = scales[:, 0]
    vertex_data["scale_1"] = scales[:, 1]
    vertex_data["scale_2"] = scales[:, 2]
    vertex_data["rot_0"] = rotations[:, 0]
    vertex_data["rot_1"] = rotations[:, 1]
    vertex_data["rot_2"] = rotations[:, 2]
    vertex_data["rot_3"] = rotations[:, 3]
    if sh_coeffs is not None:
        for i in range(45):
            vertex_data[f"f_rest_{i}"] = sh_coeffs[:, i]

    vertex_element = PlyElement.describe(vertex_data, "vertex")
    ply = PlyData([vertex_element], text=False, byte_order="<")
    ply.write(str(path))

    logger.info(
        "Wrote PLY %s: %d gaussians, sh_coeffs=%s",
        path,
        n,
        "Nx45" if sh_coeffs is not None else "None",
    )


# ---------------------------------------------------------------------------
# COLMAP text-format readers
# ---------------------------------------------------------------------------
#
# NOTE: The canonical COLMAP parsers live in ``colmap_helpers.py``
# (``parse_cameras_txt``, ``parse_images_txt``, ``parse_points3d_txt``),
# which also provide writers and quaternion helpers.
# ``io.py`` only exposes thin wrappers here for backwards compatibility.
# New code should import from ``sphereforge.common.colmap_helpers`` directly.
# ---------------------------------------------------------------------------

