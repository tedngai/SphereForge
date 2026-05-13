"""SphereForge COLMAP format helpers.

Read and write COLMAP text and binary format files for cameras, images,
and 3D points. Also provides quaternion/rotation-matrix conversions.
"""

from __future__ import annotations

import logging
import struct
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Text format parsers
# ---------------------------------------------------------------------------


def parse_cameras_txt(path: Path) -> dict[int, dict]:
    """Parse a COLMAP cameras.txt file.

    Each non-comment line has the format::

        camera_id MODEL width height params...

    Args:
        path: Path to the cameras.txt file.

    Returns:
        Dict mapping camera_id -> {model, width, height, params}.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If a line cannot be parsed.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"COLMAP cameras file not found: {path}")

    cameras: dict[int, dict] = {}
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 4:
                raise ValueError(f"Invalid cameras.txt line {line_no}: {line}")
            camera_id = int(parts[0])
            model = parts[1]
            width = int(parts[2])
            height = int(parts[3])
            params = [float(p) for p in parts[4:]]
            cameras[camera_id] = {
                "model": model,
                "width": width,
                "height": height,
                "params": params,
            }
    logger.debug("Parsed %d cameras from %s", len(cameras), path)
    return cameras


def parse_images_txt(path: Path) -> dict[int, dict]:
    """Parse a COLMAP images.txt file.

    Each image occupies two consecutive non-comment lines::

        image_id qw qx qy qz tx ty tz camera_id name
        point2D_x point2D_y point3D_id  ... (repeated per point)

    Args:
        path: Path to the images.txt file.

    Returns:
        Dict mapping image_id -> {name, qw, qx, qy, qz, tx, ty, tz,
        camera_id, point3D_ids}.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If lines cannot be parsed.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"COLMAP images file not found: {path}")

    images: dict[int, dict] = {}
    with open(path, encoding="utf-8") as f:
        # Keep blank lines — they represent empty point-observation lines
        # in COLMAP's two-line-per-image format.
        lines = [line.strip() for line in f if not line.strip().startswith("#")]

    i = 0
    while i < len(lines):
        # Skip blank lines between entries
        if not lines[i]:
            i += 1
            continue

        # First line: image header
        header = lines[i].split()
        if len(header) < 10:
            raise ValueError(f"Invalid images.txt line {i + 1}: {lines[i]}")
        image_id = int(header[0])
        qw, qx, qy, qz = float(header[1]), float(header[2]), float(header[3]), float(header[4])
        tx, ty, tz = float(header[5]), float(header[6]), float(header[7])
        camera_id = int(header[8])
        name = header[9]

        # Second line: 2D point data (may be blank)
        point3d_ids: list[int] = []
        if i + 1 < len(lines) and lines[i + 1]:
            pts_line = lines[i + 1].split()
            # Points are triples: x y point3D_id
            num_pts = len(pts_line) // 3
            for j in range(num_pts):
                pid = int(pts_line[j * 3 + 2])
                if pid != -1:
                    point3d_ids.append(pid)

        images[image_id] = {
            "name": name,
            "qw": qw,
            "qx": qx,
            "qy": qy,
            "qz": qz,
            "tx": tx,
            "ty": ty,
            "tz": tz,
            "camera_id": camera_id,
            "point3D_ids": point3d_ids,
        }
        i += 2

    logger.debug("Parsed %d images from %s", len(images), path)
    return images


def parse_points3d_txt(path: Path) -> dict[int, dict]:
    """Parse a COLMAP points3D.txt file.

    Each non-comment line has the format::

        point3D_id x y z r g b error track...

    Args:
        path: Path to the points3D.txt file.

    Returns:
        Dict mapping point3D_id -> {x, y, z, r, g, b, error}.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If a line cannot be parsed.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"COLMAP points3D file not found: {path}")

    points: dict[int, dict] = {}
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 8:
                raise ValueError(f"Invalid points3D.txt line {line_no}: {line}")
            pid = int(parts[0])
            points[pid] = {
                "x": float(parts[1]),
                "y": float(parts[2]),
                "z": float(parts[3]),
                "r": int(parts[4]),
                "g": int(parts[5]),
                "b": int(parts[6]),
                "error": float(parts[7]),
            }

    logger.debug("Parsed %d 3D points from %s", len(points), path)
    return points


# ---------------------------------------------------------------------------
# Text format writers
# ---------------------------------------------------------------------------


def write_cameras_txt(path: Path, cameras: dict[int, dict]) -> None:
    """Write a COLMAP cameras.txt file.

    Args:
        path: Output file path. Parent directories are created if needed.
        cameras: Dict mapping camera_id -> {model, width, height, params}.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Camera list with one line of data per camera:\n")
        f.write("#   CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n")
        f.write(f"# Number of cameras: {len(cameras)}\n")
        for cam_id in sorted(cameras):
            cam = cameras[cam_id]
            params_str = " ".join(str(p) for p in cam["params"])
            f.write(f"{cam_id} {cam['model']} {cam['width']} {cam['height']} {params_str}\n")

    logger.debug("Wrote %d cameras to %s", len(cameras), path)


def write_images_txt(path: Path, images: dict[int, dict]) -> None:
    """Write a COLMAP images.txt file.

    Args:
        path: Output file path. Parent directories are created if needed.
        images: Dict mapping image_id -> {name, qw, qx, qy, qz, tx, ty, tz,
            camera_id, point3D_ids}.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Image list with two lines of data per image:\n")
        f.write("#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME\n")
        f.write("#   POINTS2D[] as (X, Y, POINT3D_ID)\n")
        f.write(f"# Number of images: {len(images)}\n")
        for img_id in sorted(images):
            img = images[img_id]
            f.write(
                f"{img_id} {img['qw']:.6f} {img['qx']:.6f} "
                f"{img['qy']:.6f} {img['qz']:.6f} "
                f"{img['tx']:.6f} {img['ty']:.6f} {img['tz']:.6f} "
                f"{img['camera_id']} {img['name']}\n"
            )
            f.write("\n")  # Empty line for point observations

    logger.debug("Wrote %d images to %s", len(images), path)


# ---------------------------------------------------------------------------
# Quaternion / rotation conversions
# ---------------------------------------------------------------------------


def quat_to_rotation_matrix(qw: float, qx: float, qy: float, qz: float) -> NDArray[np.float64]:
    """Convert a quaternion to a 3x3 rotation matrix.

    Uses the standard unit-quaternion-to-rotation formula.

    Args:
        qw: Scalar part of the quaternion.
        qx: x component.
        qy: y component.
        qz: z component.

    Returns:
        3x3 rotation matrix as float64 numpy array.

    Raises:
        ValueError: If the quaternion has zero norm.
    """
    q = np.array([qw, qx, qy, qz], dtype=np.float64)
    norm = np.linalg.norm(q)
    if norm < 1e-10:
        raise ValueError(f"Quaternion has near-zero norm: ({qw}, {qx}, {qy}, {qz})")
    q = q / norm

    w, x, y, z = q
    R = np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
            [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
            [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
        ],
        dtype=np.float64,
    )
    return R


def rotation_matrix_to_quat(R: NDArray[np.floating]) -> tuple[float, float, float, float]:
    """Convert a 3x3 rotation matrix to a quaternion (qw, qx, qy, qz).

    Uses Shepperd's method for numerical stability, which selects the
    largest diagonal element to avoid division by near-zero values.

    Args:
        R: 3x3 rotation matrix.

    Returns:
        Tuple (qw, qx, qy, qz) with unit norm.

    Raises:
        ValueError: If R is not 3x3.
    """
    R = np.asarray(R, dtype=np.float64)
    if R.shape != (3, 3):
        raise ValueError(f"Expected 3x3 matrix, got shape {R.shape}")

    # Shepperd's method: pick the largest diagonal element
    trace = R[0, 0] + R[1, 1] + R[2, 2]

    if trace > 0:
        s = 2.0 * np.sqrt(1.0 + trace)
        qw = 0.25 * s
        qx = (R[2, 1] - R[1, 2]) / s
        qy = (R[0, 2] - R[2, 0]) / s
        qz = (R[1, 0] - R[0, 1]) / s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
        qw = (R[2, 1] - R[1, 2]) / s
        qx = 0.25 * s
        qy = (R[0, 1] + R[1, 0]) / s
        qz = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
        qw = (R[0, 2] - R[2, 0]) / s
        qx = (R[0, 1] + R[1, 0]) / s
        qy = 0.25 * s
        qz = (R[1, 2] + R[2, 1]) / s
    else:
        s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
        qw = (R[1, 0] - R[0, 1]) / s
        qx = (R[0, 2] + R[2, 0]) / s
        qy = (R[1, 2] + R[2, 1]) / s
        qz = 0.25 * s

    # Ensure positive qw (canonical form)
    norm = np.sqrt(qw * qw + qx * qx + qy * qy + qz * qz)
    if norm < 1e-10:
        return (1.0, 0.0, 0.0, 0.0)  # Identity quaternion fallback
    if qw < 0:
        qw, qx, qy, qz = -qw, -qx, -qy, -qz

    return (float(qw / norm), float(qx / norm), float(qy / norm), float(qz / norm))


# ---------------------------------------------------------------------------
# Binary format reader
# ---------------------------------------------------------------------------


def _read_string_binary(f) -> str:
    """Read a null-terminated string from a COLMAP binary file."""
    chars = []
    while True:
        c = f.read(1)
        if not c or c == b"\x00":
            break
        chars.append(c.decode("ascii"))
    return "".join(chars)


def read_colmap_binary(path: Path) -> dict:
    """Read a COLMAP binary file (cameras.bin, images.bin, or points3D.bin).

    Auto-detects which format based on the filename. Returns the same
    dict structure as the text parsers.

    Args:
        path: Path to the binary file. Must be named cameras.bin,
            images.bin, or points3D.bin.

    Returns:
        Dict matching the text parser output for the detected format.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the filename is not recognized.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"COLMAP binary file not found: {path}")

    name = path.name.lower()
    if name == "cameras.bin":
        return _read_cameras_binary(path)
    elif name == "images.bin":
        return _read_images_binary(path)
    elif name == "points3d.bin":
        return _read_points3d_binary(path)
    else:
        raise ValueError(
            f"Unrecognized COLMAP binary file: {path.name}. "
            f"Expected cameras.bin, images.bin, or points3D.bin"
        )


def _read_cameras_binary(path: Path) -> dict[int, dict]:
    """Read cameras.bin in COLMAP binary format (v3.8+ model IDs)."""
    _MODEL_NAMES = {
        0: "SIMPLE_PINHOLE",
        1: "PINHOLE",
        2: "SIMPLE_RADIAL",
        3: "RADIAL",
        4: "OPENCV",
        5: "OPENCV_FISHEYE",
        6: "FULL_OPENCV",
        7: "FOV",
        8: "SIMPLE_RADIAL_FISHEYE",
        9: "RADIAL_FISHEYE",
        10: "THIN_PRISM_FISHEYE",
    }
    _MODEL_PARAMS = {
        0: 3, 1: 4, 2: 4, 3: 5, 4: 8, 5: 8, 6: 12, 7: 5, 8: 4, 9: 5, 10: 12,
    }
    cameras: dict[int, dict] = {}
    with open(path, "rb") as f:
        num_cameras = struct.unpack("<Q", f.read(8))[0]
        for _ in range(num_cameras):
            camera_id = struct.unpack("<I", f.read(4))[0]
            model_id = struct.unpack("<i", f.read(4))[0]
            width = struct.unpack("<Q", f.read(8))[0]
            height = struct.unpack("<Q", f.read(8))[0]
            model = _MODEL_NAMES.get(model_id, f"UNKNOWN_{model_id}")
            np_ = _MODEL_PARAMS.get(model_id, 4)
            params = list(struct.unpack(f"<{np_}d", f.read(8 * np_)))
            cameras[camera_id] = {
                "model": model,
                "width": width,
                "height": height,
                "params": params,
            }
    logger.debug("Read %d cameras from binary %s", len(cameras), path)
    return cameras


def _read_images_binary(path: Path) -> dict[int, dict]:
    """Read images.bin in COLMAP binary format."""
    images: dict[int, dict] = {}
    with open(path, "rb") as f:
        num_images = struct.unpack("<Q", f.read(8))[0]
        for _ in range(num_images):
            image_id = struct.unpack("<I", f.read(4))[0]
            qw, qx, qy, qz = struct.unpack("<4d", f.read(32))
            tx, ty, tz = struct.unpack("<3d", f.read(24))
            camera_id = struct.unpack("<I", f.read(4))[0]
            name = _read_string_binary(f)
            num_points2D = struct.unpack("<Q", f.read(8))[0]

            # Read all point data at once: x y point3D_id per point
            point3d_ids: list[int] = []
            if num_points2D > 0:
                struct.unpack(f"<{num_points2D * 2}d", f.read(16 * num_points2D))
                point3d_raw = struct.unpack(f"<{num_points2D}q", f.read(8 * num_points2D))
                point3d_ids = [int(p) for p in point3d_raw if int(p) != -1]

            images[image_id] = {
                "name": name,
                "qw": qw,
                "qx": qx,
                "qy": qy,
                "qz": qz,
                "tx": tx,
                "ty": ty,
                "tz": tz,
                "camera_id": camera_id,
                "point3D_ids": point3d_ids,
            }
    logger.debug("Read %d images from binary %s", len(images), path)
    return images


def _read_points3d_binary(path: Path) -> dict[int, dict]:
    """Read points3D.bin in COLMAP binary format."""
    points: dict[int, dict] = {}
    with open(path, "rb") as f:
        num_points = struct.unpack("<Q", f.read(8))[0]
        for _ in range(num_points):
            point3D_id = struct.unpack("<Q", f.read(8))[0]
            x, y, z = struct.unpack("<3d", f.read(24))
            r, g, b = struct.unpack("<3B", f.read(3))
            error = struct.unpack("<d", f.read(8))[0]
            track_length = struct.unpack("<Q", f.read(8))[0]
            # Skip track data: image_id (uint32) + point2D_idx (int32) per track element
            f.read(track_length * 8)
            points[point3D_id] = {
                "x": x,
                "y": y,
                "z": z,
                "r": int(r),
                "g": int(g),
                "b": int(b),
                "error": error,
            }
    logger.debug("Read %d 3D points from binary %s", len(points), path)
    return points
