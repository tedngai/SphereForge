"""SphereForge Stage 8: SPZ (streaming-optimized) export.

Reorganizes PLY data with Morton-code ordering, delta encoding for positions,
and quantized attributes for compact streaming delivery.
"""

from __future__ import annotations

import logging
import struct
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

# SPZ magic number and version
SPZ_MAGIC = b"SPZF"
SPZ_VERSION = 1


def _morton_code_3d(x: int, y: int, z: int) -> int:
    """Compute 3D Morton code (Z-order curve index) from integer coordinates.

    Args:
        x: X coordinate (non-negative integer).
        y: Y coordinate (non-negative integer).
        z: Z coordinate (non-negative integer).

    Returns:
        Morton code as integer.
    """
    def _split_by_1(n: int) -> int:
        n = n & 0x000003FF
        n = (n | (n << 16)) & 0x030000FF
        n = (n | (n << 8)) & 0x0300F00F
        n = (n | (n << 4)) & 0x030C30C3
        n = (n | (n << 2)) & 0x09249249
        return n

    return (_split_by_1(x) << 2) | (_split_by_1(y) << 1) | _split_by_1(z)


def _compute_morton_codes(positions: np.ndarray, n_bits: int = 21) -> np.ndarray:
    """Compute Morton codes for a set of 3D positions.

    Quantizes positions to n_bits integers, then computes Morton codes.

    Args:
        positions: (N, 3) float positions.
        n_bits: Number of bits for quantization (default 21, fits in 63-bit int).

    Returns:
        (N,) array of Morton code integers.
    """
    # Normalize to [0, 2^n_bits - 1]
    mins = positions.min(axis=0)
    maxs = positions.max(axis=0)
    ranges = maxs - mins
    ranges[ranges < 1e-8] = 1.0  # Avoid division by zero

    normalized = (positions - mins) / ranges
    quantized = (normalized * ((1 << n_bits) - 1)).astype(np.int64)
    quantized = np.clip(quantized, 0, (1 << n_bits) - 1)

    morton = np.array([
        _morton_code_3d(int(q[0]), int(q[1]), int(q[2]))
        for q in quantized
    ])

    return morton


def export_spz(ply_path: Path, output_path: Path | None = None) -> Path:
    """Convert a Gaussian Splat PLY file to SPZ streaming-optimized format.

    SPZ format:
    - Header: magic (4B) + version (1B) + n_gaussians (4B) + n_sh (1B)
    - Positions sorted by Morton code, delta-encoded as float32
    - Scales log-encoded as float32
    - Rotations quantized as int16 (normalized quaternion x 32767)
    - Colors as float32 (SH DC coefficients)
    - Opacities as float32 (logit-encoded)

    Args:
        ply_path: Path to input Gaussian Splat PLY file.
        output_path: Output path. Defaults to ply_path with .spz extension.

    Returns:
        Path to the written .spz file.
    """
    from sphereforge.common.io import read_ply

    ply_path = Path(ply_path)
    if output_path is None:
        output_path = ply_path.with_suffix(".spz")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Exporting SPZ from %s", ply_path)

    # Read PLY
    data = read_ply(ply_path)
    positions = data["positions"]  # (N, 3)
    colors = data["colors"]        # (N, 3) or (N, K)
    opacities = data["opacities"]  # (N,)
    scales = data["scales"]        # (N, 3)
    rotations = data["rotations"]  # (N, 4)
    sh_coeffs = data.get("sh_coeffs", None)

    n_gaussians = positions.shape[0]
    n_sh = sh_coeffs.shape[1] if sh_coeffs is not None else colors.shape[1]

    # Sort by Morton code for spatial locality
    morton = _compute_morton_codes(positions)
    sort_idx = np.argsort(morton)

    positions = positions[sort_idx]
    colors = colors[sort_idx]
    opacities = opacities[sort_idx]
    scales = scales[sort_idx]
    rotations = rotations[sort_idx]
    if sh_coeffs is not None:
        sh_coeffs = sh_coeffs[sort_idx]

    # Delta-encode positions
    positions_delta = np.zeros_like(positions)
    positions_delta[0] = positions[0]
    positions_delta[1:] = np.diff(positions, axis=0)

    # Log-encode scales
    scales_log = np.log(scales + 1e-8)

    # Quantize rotations (normalize quaternion, then quantize to int16)
    rot_norms = np.linalg.norm(rotations, axis=1, keepdims=True)
    rotations_normalized = rotations / (rot_norms + 1e-8)
    rotations_quantized = (rotations_normalized * 32767).astype(np.int16)

    # Logit-encode opacities
    opacities_clamped = np.clip(opacities, 1e-6, 1.0 - 1e-6)
    opacities_logit = np.log(opacities_clamped / (1.0 - opacities_clamped))

    # Write binary file
    with open(output_path, "wb") as f:
        # Header
        f.write(SPZ_MAGIC)
        f.write(struct.pack("<B", SPZ_VERSION))
        f.write(struct.pack("<I", n_gaussians))
        f.write(struct.pack("<B", min(n_sh, 255)))

        # Delta-encoded positions (float32)
        f.write(positions_delta.astype(np.float32).tobytes())

        # Log-encoded scales (float32)
        f.write(scales_log.astype(np.float32).tobytes())

        # Quantized rotations (int16)
        f.write(rotations_quantized.tobytes())

        # Colors/SH DC (float32)
        if colors.dtype == np.uint8:
            colors_float = colors.astype(np.float32) / 255.0
        else:
            colors_float = colors.astype(np.float32)
        f.write(colors_float.tobytes())

        # Logit-encoded opacities (float32)
        f.write(opacities_logit.astype(np.float32).tobytes())

        # Additional SH coefficients (float32)
        if sh_coeffs is not None and sh_coeffs.shape[1] > 3:
            f.write(sh_coeffs[:, 3:].astype(np.float32).tobytes())

    size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info("SPZ export complete: %s (%.1f MB, %d Gaussians)", output_path, size_mb, n_gaussians)
    return output_path
