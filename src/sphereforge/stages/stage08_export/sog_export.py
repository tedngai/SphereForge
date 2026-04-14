"""SOG (Structured-Organized Gaussians) export (Stage 8).

Converts PLY Gaussian Splatting files to the SOG format for streaming.
SOG organizes Gaussians into a hierarchical cluster structure using
k-means on positions, enabling progressive loading and level-of-detail.

This is a Python reimplementation since LichtFeld-Studio's C++ SOG
writer is GPLv3. The binary format is kept compatible where possible.
"""

from __future__ import annotations

import logging
import struct
from pathlib import Path

import numpy as np

from sphereforge.common.io import read_ply

logger = logging.getLogger("sphereforge.stage08.sog_export")

# SOG file format magic number and version
SOG_MAGIC = b"SOG1"
SOG_VERSION = 1


def _kmeans_clusters(
    positions: np.ndarray,
    n_clusters: int,
    max_iter: int = 100,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Simple k-means clustering on positions.

    Uses sklearn if available, otherwise falls back to a simple
    Lloyd's algorithm implementation.

    Args:
        positions: Nx3 float32 array of positions.
        n_clusters: Number of clusters.
        max_iter: Maximum number of k-means iterations.
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (labels, centers) where labels is (N,) int array of
        cluster assignments and centers is (n_clusters, 3) float32 array.
    """
    try:
        from sklearn.cluster import KMeans

        kmeans = KMeans(n_clusters=n_clusters, max_iter=max_iter, random_state=seed, n_init=1)
        labels = kmeans.fit_predict(positions)
        centers = kmeans.cluster_centers_.astype(np.float32)
        logger.debug("Used sklearn KMeans for SOG clustering")
        return labels.astype(np.int32), centers
    except ImportError:
        logger.debug("sklearn not available, using simple k-means")

    # Simple Lloyd's algorithm
    rng = np.random.RandomState(seed)
    n = positions.shape[0]
    n_clusters = min(n_clusters, n)

    # Initialize centroids using random selection
    indices = rng.choice(n, size=n_clusters, replace=False)
    centers = positions[indices].copy().astype(np.float32)

    labels = np.zeros(n, dtype=np.int32)

    for _ in range(max_iter):
        # Assign each point to nearest centroid
        # Compute distances: (n, n_clusters)
        diffs = positions[:, np.newaxis, :] - centers[np.newaxis, :, :]
        dists = np.sum(diffs ** 2, axis=2)
        new_labels = np.argmin(dists, axis=1).astype(np.int32)

        # Check convergence
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels

        # Update centroids
        for k in range(n_clusters):
            mask = labels == k
            if mask.any():
                centers[k] = positions[mask].mean(axis=0).astype(np.float32)

    return labels, centers


def export_sog(
    ply_path: Path,
    output_path: Path,
    n_clusters: int = 64,
) -> Path:
    """Convert a PLY file to SOG format for streaming.

    SOG organizes Gaussians into a hierarchical cluster structure:

    1. Cluster Gaussians using k-means (n_clusters groups) based on
       position.
    2. For each cluster, write: bounding box, center, list of Gaussian
       offsets (relative to cluster center).
    3. Write as a custom binary format with header.

    Binary format layout::

        [4 bytes] Magic: "SOG1"
        [4 bytes] Version: uint32 (1)
        [4 bytes] n_clusters: uint32
        [4 bytes] n_gaussians: uint32
        [4 bytes] n_sh_coeffs: uint32 (0 if no SH)
        --- Per-cluster header (repeated n_clusters times) ---
        [12 bytes] center: 3x float32 (x, y, z)
        [24 bytes] bbox_min: 3x float32
        [24 bytes] bbox_max: 3x float32
        [4 bytes]  count: uint32 (Gaussians in this cluster)
        --- Per-cluster Gaussian data ---
        [12 bytes * count] offsets: count x 3x float32
        [3 bytes * count]   colors: count x uint8 RGB
        [4 bytes * count]   opacities: count x float32
        [12 bytes * count]  scales: count x 3x float32
        [16 bytes * count]  rotations: count x 4x float32
        [n_sh * 4 * count]  sh_coeffs: count x n_sh float32 (if present)

    Args:
        ply_path: Path to the input PLY file.
        output_path: Path for the output .sog file.
        n_clusters: Number of clusters for k-means. Default 64.

    Returns:
        Path to the written .sog file.
    """
    ply_path = Path(ply_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Exporting SOG: %s → %s (n_clusters=%d)", ply_path, output_path, n_clusters)

    # Read PLY data
    gaussians = read_ply(ply_path)
    positions = gaussians["positions"]
    colors = gaussians["colors"]
    opacities = gaussians["opacities"]
    scales = gaussians["scales"]
    rotations = gaussians["rotations"]
    sh_coeffs = gaussians.get("sh_coeffs", None)

    n_gaussians = positions.shape[0]

    # Ensure colors are uint8 RGB
    if colors.dtype == np.float32:
        # DC SH coefficients → convert to RGB
        # SH DC to RGB: C = 0.5 + SH_C * 0.2821
        rgb = np.clip(0.5 + colors * 0.2821, 0, 1)
        colors_uint8 = (rgb * 255).astype(np.uint8)
    else:
        colors_uint8 = colors.astype(np.uint8)

    # Determine SH coeff count (excluding DC which is stored as colors)
    n_sh = 0
    if sh_coeffs is not None:
        # sh_coeffs includes DC (3) + rest
        n_sh = sh_coeffs.shape[-1] - 3 if sh_coeffs.shape[-1] > 3 else 0
        if n_sh > 0:
            sh_rest = sh_coeffs[:, 3:].astype(np.float32)  # Remove DC part
        else:
            sh_rest = None
    else:
        sh_rest = None

    # Cluster Gaussians by position
    actual_clusters = min(n_clusters, n_gaussians)
    if actual_clusters < 1:
        actual_clusters = 1

    labels, centers = _kmeans_clusters(positions, actual_clusters)

    # Write SOG binary file
    with open(output_path, "wb") as f:
        # Header
        f.write(SOG_MAGIC)
        f.write(struct.pack("<I", SOG_VERSION))
        f.write(struct.pack("<I", actual_clusters))
        f.write(struct.pack("<I", n_gaussians))
        f.write(struct.pack("<I", n_sh))

        # Per-cluster data
        for k in range(actual_clusters):
            mask = labels == k
            cluster_positions = positions[mask]
            cluster_colors = colors_uint8[mask]
            cluster_opacities = opacities[mask]
            cluster_scales = scales[mask]
            cluster_rotations = rotations[mask]

            count = int(mask.sum())

            # Cluster bounding box
            if count > 0:
                cluster_center = centers[k]
                bbox_min = cluster_positions.min(axis=0)
                bbox_max = cluster_positions.max(axis=0)
                offsets = cluster_positions - cluster_center
            else:
                cluster_center = np.zeros(3, dtype=np.float32)
                bbox_min = np.zeros(3, dtype=np.float32)
                bbox_max = np.zeros(3, dtype=np.float32)
                offsets = np.zeros((0, 3), dtype=np.float32)

            # Write cluster header
            f.write(struct.pack("<3f", *cluster_center))
            f.write(struct.pack("<3f", *bbox_min))
            f.write(struct.pack("<3f", *bbox_max))
            f.write(struct.pack("<I", count))

            if count > 0:
                # Offsets (positions relative to cluster center)
                f.write(offsets.astype(np.float32).tobytes())
                # Colors (RGB as uint8)
                f.write(cluster_colors.tobytes())
                # Opacities
                f.write(cluster_opacities.astype(np.float32).tobytes())
                # Scales
                f.write(cluster_scales.astype(np.float32).tobytes())
                # Rotations
                f.write(cluster_rotations.astype(np.float32).tobytes())
                # SH rest coefficients
                if sh_rest is not None:
                    cluster_sh = sh_rest[mask]
                    f.write(cluster_sh.astype(np.float32).tobytes())

    file_size = output_path.stat().st_size
    logger.info(
        "SOG export complete: %d Gaussians in %d clusters, file size: %.2f MB",
        n_gaussians, actual_clusters, file_size / (1024 * 1024),
    )

    return output_path
