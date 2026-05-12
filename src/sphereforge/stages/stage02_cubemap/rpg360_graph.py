"""RPG360 graph-based scale optimization for cross-face depth consistency.

Implements the core algorithm from arXiv:2509.23991 (RPG360) that optimizes
per-face scale and shift parameters so that depth estimates from adjacent
cubemap faces agree in their overlap regions. The result is a set of six
(scale, shift) pairs — one per cubemap face — that bring all face depth
maps into a globally consistent metric scale.

The module also provides utilities to apply the computed alignment
parameters and to fuse aligned face depth maps into a single equirectangular
depth map.
"""

from __future__ import annotations

import logging

import numpy as np
from scipy.optimize import least_squares

from sphereforge.common.depth_utils import fuse_cubemap_depth_to_erp

logger = logging.getLogger("sphereforge.stage02.rpg360")

# Canonical ordering of the four equatorial faces for adjacency traversal.
# Adjacent faces share a vertical border:
#   front  ↔ right  (front's right edge meets right's left edge)
#   right  ↔ back   (right's right edge meets back's left edge)
#   back   ↔ left   (back's right edge meets left's left edge)
#   left   ↔ front  (left's right edge meets front's left edge)
_EQUATORIAL_CYCLE: list[str] = ["front", "right", "back", "left"]

# Direction name → index in the standard 6-face ordering used by this module.
_DIRECTION_INDEX: dict[str, int] = {
    "front": 0,
    "right": 1,
    "back": 2,
    "left": 3,
    "top": 4,
    "bottom": 5,
}

# Adjacency pairs for the equatorial ring.
# Each tuple is (face_a, face_b, edge_a, edge_b) where edge is "right" or
# "left", indicating which border of each face is shared.
_EQUATORIAL_ADJACENCIES: list[tuple[str, str, str, str]] = [
    ("front", "right", "right", "left"),
    ("right", "back", "right", "left"),
    ("back", "left", "right", "left"),
    ("left", "front", "right", "left"),
]

# Top/bottom adjacency: top and bottom faces share borders with all four
# equatorial faces along their top/bottom edges.
# (equatorial_face, polar_face, equatorial_edge, polar_edge)
_POLAR_ADJACENCIES: list[tuple[str, str, str, str]] = [
    ("front", "top", "top", "bottom"),  # front's top edge meets top's bottom edge
    ("right", "top", "top", "bottom"),
    ("back", "top", "top", "bottom"),
    ("left", "top", "top", "bottom"),
    ("front", "bottom", "bottom", "top"),  # front's bottom meets bottom's top
    ("right", "bottom", "bottom", "top"),
    ("back", "bottom", "bottom", "top"),
    ("left", "bottom", "bottom", "top"),
]


def _extract_overlap_strip(
    depth: np.ndarray,
    edge: str,
    overlap_pixels: int,
) -> np.ndarray:
    """Extract a border strip from a depth map.

    Args:
        depth: Depth map of shape (H, W).
        edge: Which border to extract — one of ``"right"``, ``"left"``,
            ``"top"``, ``"bottom"``.
        overlap_pixels: Width (in pixels) of the strip to extract.

    Returns:
        Strip array of shape (H, overlap_pixels) for left/right edges,
        or (overlap_pixels, W) for top/bottom edges.
    """
    w = depth.shape[1]
    h = depth.shape[0]
    if edge == "right":
        return depth[:, w - overlap_pixels : w]
    elif edge == "left":
        return depth[:, :overlap_pixels]
    elif edge == "top":
        return depth[:overlap_pixels, :]
    elif edge == "bottom":
        return depth[h - overlap_pixels : h, :]
    else:
        raise ValueError(f"Unknown edge '{edge}', expected right/left/top/bottom")


def _build_residuals(
    x: np.ndarray,
    face_depths: list[np.ndarray],
    face_directions: list[str],
    overlap_pixels: int,
    ref_index: int,
) -> np.ndarray:
    """Compute residuals for the least-squares scale+shift optimisation.

    For each adjacent pair, the residual is the difference between the
    scaled+shifted depth values in the overlap region.

    Args:
        x: Parameter vector of length 2*N where x[2*i] = scale_i and
            x[2*i+1] = shift_i. The reference face's parameters are
            fixed (scale=1, shift=0) and not included in x.
        face_depths: List of 6 depth maps.
        face_directions: List of 6 direction strings.
        overlap_pixels: Width of overlap region in pixels.
        ref_index: Index of the reference face (parameters fixed).

    Returns:
        1-D array of residuals.
    """
    n_faces = len(face_depths)
    scales = np.zeros(n_faces, dtype=np.float64)
    shifts = np.zeros(n_faces, dtype=np.float64)

    # Reconstruct full parameter vector including fixed reference face
    param_idx = 0
    for i in range(n_faces):
        if i == ref_index:
            scales[i] = 1.0
            shifts[i] = 0.0
        else:
            scales[i] = x[param_idx]
            shifts[i] = x[param_idx + 1]
            param_idx += 2

    # Build direction → index mapping
    dir_to_idx = {d: i for i, d in enumerate(face_directions)}

    residuals_list: list[np.ndarray] = []

    # Equatorial adjacency pairs
    for face_a, face_b, edge_a, edge_b in _EQUATORIAL_ADJACENCIES:
        if face_a not in dir_to_idx or face_b not in dir_to_idx:
            continue
        idx_a = dir_to_idx[face_a]
        idx_b = dir_to_idx[face_b]

        strip_a = _extract_overlap_strip(face_depths[idx_a], edge_a, overlap_pixels)
        strip_b = _extract_overlap_strip(face_depths[idx_b], edge_b, overlap_pixels)

        # Align: scale_i * depth_i + shift_i should match scale_j * depth_j + shift_j
        aligned_a = scales[idx_a] * strip_a.astype(np.float64) + shifts[idx_a]
        aligned_b = scales[idx_b] * strip_b.astype(np.float64) + shifts[idx_b]

        # Flatten difference
        diff = (aligned_a - aligned_b).ravel()
        residuals_list.append(diff)

    # Polar adjacency pairs
    for eq_face, pol_face, eq_edge, pol_edge in _POLAR_ADJACENCIES:
        if eq_face not in dir_to_idx or pol_face not in dir_to_idx:
            continue
        idx_eq = dir_to_idx[eq_face]
        idx_pol = dir_to_idx[pol_face]

        strip_eq = _extract_overlap_strip(face_depths[idx_eq], eq_edge, overlap_pixels)
        strip_pol = _extract_overlap_strip(face_depths[idx_pol], pol_edge, overlap_pixels)

        # For top/bottom vs equatorial overlap, the strips may have different
        # shapes (e.g. equatorial horizontal strip vs polar horizontal strip).
        # We match them using the minimum overlapping area by trimming to
        # common length along the shared dimension.
        if strip_eq.ndim != strip_pol.ndim:
            continue
        if strip_eq.shape != strip_pol.shape:
            # Trim to common shape along the varying dimension
            min_rows = min(strip_eq.shape[0], strip_pol.shape[0])
            min_cols = min(strip_eq.shape[1], strip_pol.shape[1])
            strip_eq = strip_eq[:min_rows, :min_cols]
            strip_pol = strip_pol[:min_rows, :min_cols]

        aligned_eq = scales[idx_eq] * strip_eq.astype(np.float64) + shifts[idx_eq]
        aligned_pol = scales[idx_pol] * strip_pol.astype(np.float64) + shifts[idx_pol]

        diff = (aligned_eq - aligned_pol).ravel()
        residuals_list.append(diff)

    if not residuals_list:
        logger.warning("No adjacency pairs found — returning zero residuals")
        return np.array([0.0])

    return np.concatenate(residuals_list)


def graph_optimize_scales(
    face_depths: list[np.ndarray],
    face_directions: list[str],
    overlap_pixels: int = 50,
) -> tuple[list[float], list[float]]:
    """Optimize per-face scale and shift for cross-face depth consistency.

    Implements the RPG360 graph-based scale optimization algorithm
    (arXiv:2509.23991). For each pair of adjacent cubemap faces, the
    scaled+shifted depth values in the overlap region should agree.
    This is formulated as a least-squares problem over 12 parameters
    (6 scales + 6 shifts) with one face fixed as reference to resolve
    gauge freedom.

    Args:
        face_depths: List of 6 per-face depth maps, each of shape
            ``(H_face, W_face)``. All faces should have the same
            spatial dimensions for best results.
        face_directions: List of 6 direction strings, each one of
            ``"front"``, ``"back"``, ``"right"``, ``"left"``,
            ``"top"``, ``"bottom"``. Order must correspond to
            ``face_depths``.
        overlap_pixels: Number of pixels near each shared edge to use
            as the overlap region for consistency computation. Default
            is 50.

    Returns:
        A tuple ``(scales, shifts)`` where each is a list of 6 floats.
        ``scales[i]`` and ``shifts[i]`` are the alignment parameters for
        ``face_depths[i]``. The reference face (front, or the first
        equatorial face found) has ``scale=1.0`` and ``shift=0.0``.

    Raises:
        ValueError: If input lists have mismatched lengths or unknown
            directions.
    """
    valid_directions = {"front", "back", "right", "left", "top", "bottom"}
    if len(face_depths) != 6 or len(face_directions) != 6:
        raise ValueError(
            f"Expected 6 faces, got {len(face_depths)} depths and "
            f"{len(face_directions)} directions"
        )
    for d in face_directions:
        if d not in valid_directions:
            raise ValueError(
                f"Unknown face direction '{d}', must be one of {valid_directions}"
            )

    # Clamp overlap_pixels to at most half the face dimension
    min_face_dim = min(d.shape[0] for d in face_depths)
    min_face_dim = min(min_face_dim, min(d.shape[1] for d in face_depths))
    if overlap_pixels > min_face_dim // 2:
        overlap_pixels = min_face_dim // 2
        logger.warning(
            "overlap_pixels reduced to %d (half of smallest face dimension %d)",
            overlap_pixels,
            min_face_dim,
        )

    # Determine reference face: prefer "front", fall back to first equatorial
    ref_index = 0
    for i, d in enumerate(face_directions):
        if d == "front":
            ref_index = i
            break

    logger.info(
        "RPG360 graph optimisation: %d faces, overlap=%d px, "
        "reference face='%s' (index %d)",
        len(face_depths),
        overlap_pixels,
        face_directions[ref_index],
        ref_index,
    )

    # Initial guess: all scales = 1, all shifts = 0 (excluding reference)
    n_free = 5  # 6 faces minus 1 reference = 5 free faces
    x0 = np.zeros(2 * n_free, dtype=np.float64)
    for i in range(n_free):
        x0[2 * i] = 1.0  # scale
        x0[2 * i + 1] = 0.0  # shift

    # Solve least-squares
    result = least_squares(
        _build_residuals,
        x0,
        args=(face_depths, face_directions, overlap_pixels, ref_index),
        method="trf",
        max_nfev=500,
        ftol=1e-10,
        xtol=1e-10,
        gtol=1e-10,
    )

    if not result.success:
        logger.warning(
            "RPG360 least-squares did not converge: %s", result.message
        )
    else:
        logger.info(
            "RPG360 optimisation converged: cost=%.6f, nfev=%d",
            float(result.cost),
            result.nfev,
        )

    # Reconstruct full scale+shift vectors
    scales = [0.0] * 6
    shifts = [0.0] * 6
    param_idx = 0
    for i in range(6):
        if i == ref_index:
            scales[i] = 1.0
            shifts[i] = 0.0
        else:
            scales[i] = float(result.x[param_idx])
            shifts[i] = float(result.x[param_idx + 1])
            param_idx += 2

    logger.info(
        "Optimised scales: %s",
        {face_directions[i]: f"{scales[i]:.6f}" for i in range(6)},
    )
    logger.info(
        "Optimised shifts: %s",
        {face_directions[i]: f"{shifts[i]:.6f}" for i in range(6)},
    )

    return scales, shifts


def align_face_depths(
    face_depths: list[np.ndarray],
    scales: list[float],
    shifts: list[float],
) -> list[np.ndarray]:
    """Apply per-face scale and shift alignment to depth maps.

    Computes ``aligned = depth * scale + shift`` for each face depth map,
    producing depth maps that are consistent across face boundaries.

    Args:
        face_depths: List of 6 per-face depth maps, each of shape
            ``(H_face, W_face)``.
        scales: List of 6 scale factors, one per face.
        shifts: List of 6 shift values, one per face.

    Returns:
        List of 6 aligned depth maps, each of shape ``(H_face, W_face)``
        with dtype float32.

    Raises:
        ValueError: If input lists have mismatched lengths.
    """
    if len(face_depths) != len(scales) or len(face_depths) != len(shifts):
        raise ValueError(
            f"Length mismatch: {len(face_depths)} depths, "
            f"{len(scales)} scales, {len(shifts)} shifts"
        )

    aligned: list[np.ndarray] = []
    for _i, (depth, s, t) in enumerate(zip(face_depths, scales, shifts, strict=False)):
        aligned_i = depth.astype(np.float64) * s + t
        aligned.append(aligned_i.astype(np.float32))

    logger.info("Applied scale+shift alignment to %d face depth maps", len(face_depths))
    return aligned


def fuse_to_erp(
    aligned_face_depths: list[np.ndarray],
    face_directions: list[str],
    erp_height: int,
    erp_width: int,
) -> np.ndarray:
    """Fuse aligned cubemap face depth maps into a single ERP depth map.

    Delegates to
    ``sphereforge.common.depth_utils.fuse_cubemap_depth_to_erp`` which
    performs per-pixel ray-casting from the ERP to the cubemap faces and
    resolves overlaps by taking the minimum depth (closest surface wins).

    Args:
        aligned_face_depths: List of 6 aligned (scale+shift applied)
            depth maps, each of shape ``(H_face, W_face)``.
        face_directions: List of 6 direction strings, each one of
            ``"front"``, ``"back"``, ``"right"``, ``"left"``,
            ``"top"``, ``"bottom"``.
        erp_height: Height of the output equirectangular depth map.
        erp_width: Width of the output equirectangular depth map.

    Returns:
        Equirectangular depth map of shape ``(erp_height, erp_width)``,
        dtype float32.

    Raises:
        ValueError: Propagated from ``fuse_cubemap_depth_to_erp`` for
            invalid inputs.
    """
    erp_depth = fuse_cubemap_depth_to_erp(
        aligned_face_depths, face_directions, erp_height, erp_width
    )

    logger.info(
        "Fused %d aligned face depths to ERP (%dx%d)",
        len(aligned_face_depths),
        erp_width,
        erp_height,
    )

    return erp_depth
