"""Depth utility functions: alignment, NCC, cross-validation, and cubemap fusion.

Provides tools for aligning monocular depth to metric scale, computing local
normalized cross-correlation between depth maps, cross-validating depth estimates,
and fusing cubemap face depth maps into equirectangular projections.
"""

from __future__ import annotations

import logging

import numpy as np
from scipy.ndimage import uniform_filter

logger = logging.getLogger(__name__)


def align_depth_median_ratio(
    depth: np.ndarray,
    sparse_points_3d: np.ndarray,
    camera_pose: np.ndarray,
    intrinsics: dict,
) -> tuple[np.ndarray, float, float]:
    """Align monocular depth to metric scale using median-of-ratios.

    Projects sparse 3D points into the image using the camera pose and intrinsics,
    samples the monocular depth at those locations, and computes the median ratio
    of metric depth to monocular depth as the scale factor. Also computes the
    median shift (bias) after scaling.

    Args:
        depth: Monocular depth map of shape (H, W).
        sparse_points_3d: Sparse 3D points in world coordinates, shape (N, 3).
        camera_pose: 4x4 world-to-camera transformation matrix. Assumes the
            camera coordinate system has +Z as the viewing direction (COLMAP /
            OpenCV convention).
        intrinsics: Dictionary with keys ``fx``, ``fy``, ``cx``, ``cy`` for
            camera intrinsics (pinhole model).

    Returns:
        A tuple of (aligned_depth, scale, shift) where:
            - aligned_depth: Depth map aligned to metric scale, shape (H, W),
              dtype float32. Computed as ``depth * scale + shift``.
            - scale: Median-of-ratios scale factor (float).
            - shift: Median shift / bias after scaling (float).

    Raises:
        ValueError: If input shapes are invalid, required keys are missing from
            intrinsics, or no valid point projections are found.
    """
    if depth.ndim != 2:
        raise ValueError(f"depth must be 2D, got shape {depth.shape}")
    if sparse_points_3d.ndim != 2 or sparse_points_3d.shape[1] != 3:
        raise ValueError(
            f"sparse_points_3d must have shape (N, 3), got {sparse_points_3d.shape}"
        )
    if camera_pose.shape != (4, 4):
        raise ValueError(
            f"camera_pose must be 4x4, got shape {camera_pose.shape}"
        )
    for key in ("fx", "fy", "cx", "cy"):
        if key not in intrinsics:
            raise ValueError(f"intrinsics must contain key '{key}'")

    h, w = depth.shape
    fx = float(intrinsics["fx"])
    fy = float(intrinsics["fy"])
    cx = float(intrinsics["cx"])
    cy = float(intrinsics["cy"])

    n_points = sparse_points_3d.shape[0]
    if n_points == 0:
        raise ValueError("sparse_points_3d is empty — no points to align with")

    # Convert to homogeneous coordinates and transform to camera frame
    ones = np.ones((n_points, 1), dtype=np.float64)
    points_hom = np.hstack([sparse_points_3d.astype(np.float64), ones])  # (N, 4)
    points_cam = (camera_pose.astype(np.float64) @ points_hom.T).T[:, :3]  # (N, 3)

    x_cam = points_cam[:, 0]
    y_cam = points_cam[:, 1]
    z_cam = points_cam[:, 2]  # metric depth

    # Filter: depth must be positive (point in front of camera)
    valid_front = z_cam > 0

    # Project to image pixel coordinates
    u_img = fx * x_cam / z_cam + cx
    v_img = fy * y_cam / z_cam + cy

    # Filter: projection must be within image bounds
    valid_bounds = (u_img >= 0) & (u_img < w) & (v_img >= 0) & (v_img < h)
    valid = valid_front & valid_bounds

    if not np.any(valid):
        raise ValueError(
            "No valid sparse points project into the image with positive depth"
        )

    # Sample monocular depth at projected pixel locations (nearest neighbour)
    u_idx = np.clip(np.round(u_img[valid]).astype(int), 0, w - 1)
    v_idx = np.clip(np.round(v_img[valid]).astype(int), 0, h - 1)
    mono_depth_vals = depth[v_idx, u_idx].astype(np.float64)
    metric_depth_vals = z_cam[valid]

    # Discard samples where monocular depth is zero or negative
    valid_mono = mono_depth_vals > 0
    if not np.any(valid_mono):
        raise ValueError(
            "No valid monocular depth values at projected point locations"
        )

    metric_valid = metric_depth_vals[valid_mono]
    mono_valid = mono_depth_vals[valid_mono]

    # Compute scale as median of (metric / monocular) ratios
    ratios = metric_valid / mono_valid
    scale = float(np.median(ratios))

    # Compute shift as median residual after scaling
    residuals = metric_valid - scale * mono_valid
    shift = float(np.median(residuals))

    # Apply alignment: aligned = depth * scale + shift
    aligned_depth = depth.astype(np.float64) * scale + shift

    logger.info(
        "Depth alignment: scale=%.4f, shift=%.4f, valid_points=%d/%d",
        scale,
        shift,
        int(np.sum(valid_mono)),
        n_points,
    )

    return aligned_depth.astype(np.float32), scale, shift


def compute_ncc(
    depth_a: np.ndarray,
    depth_b: np.ndarray,
    window_size: int = 11,
) -> np.ndarray:
    """Compute Normalized Cross-Correlation between two depth maps in local windows.

    For each pixel, a square window of side ``window_size`` is extracted from both
    depth maps and the Pearson correlation coefficient (NCC) is computed. The
    implementation uses ``scipy.ndimage.uniform_filter`` for efficient local
    statistics. Reflective padding is used at image borders.

    Zero-variance windows (flat regions in either map) are assigned an NCC
    value of 0.

    Args:
        depth_a: First depth map, shape (H, W).
        depth_b: Second depth map, shape (H, W).
        window_size: Side length of the square NCC window. Must be odd and >= 3.

    Returns:
        Per-pixel NCC map of shape (H, W), dtype float32, values in [-1, 1].

    Raises:
        ValueError: If input shapes do not match, inputs are not 2D, or
            ``window_size`` is invalid.
    """
    if depth_a.shape != depth_b.shape:
        raise ValueError(
            f"depth_a and depth_b must have the same shape, "
            f"got {depth_a.shape} vs {depth_b.shape}"
        )
    if depth_a.ndim != 2:
        raise ValueError(f"depth maps must be 2D, got shape {depth_a.shape}")
    if window_size < 3 or window_size % 2 == 0:
        raise ValueError(
            f"window_size must be odd and >= 3, got {window_size}"
        )

    a = depth_a.astype(np.float64)
    b = depth_b.astype(np.float64)

    # Local means (reflective padding at borders)
    mean_a = uniform_filter(a, size=window_size, mode="reflect")
    mean_b = uniform_filter(b, size=window_size, mode="reflect")

    # Local means of products
    mean_ab = uniform_filter(a * b, size=window_size, mode="reflect")
    mean_a2 = uniform_filter(a * a, size=window_size, mode="reflect")
    mean_b2 = uniform_filter(b * b, size=window_size, mode="reflect")

    # Local covariance and variances
    cov = mean_ab - mean_a * mean_b
    var_a = mean_a2 - mean_a * mean_a
    var_b = mean_b2 - mean_b * mean_b

    # NCC = cov / (sqrt(var_a) * sqrt(var_b))
    denom = np.sqrt(np.maximum(var_a, 0.0) * np.maximum(var_b, 0.0))

    # Handle zero-variance windows: set NCC to 0
    ncc = np.where(denom > 1e-10, cov / denom, 0.0)

    # Clamp to [-1, 1] for numerical stability
    ncc = np.clip(ncc, -1.0, 1.0)

    return ncc.astype(np.float32)


def cross_validate_depth(
    depth_primary: np.ndarray,
    depth_secondary: np.ndarray,
    ncc_threshold: float = 0.5,
) -> np.ndarray:
    """Cross-validate two depth maps using Normalized Cross-Correlation.

    Computes the per-pixel NCC between the two depth maps and returns a boolean
    mask indicating high-confidence regions where the NCC meets or exceeds the
    threshold.

    Args:
        depth_primary: Primary depth map, shape (H, W).
        depth_secondary: Secondary depth map, shape (H, W).
        ncc_threshold: Minimum NCC value for a pixel to be considered high
            confidence. Must be in [-1, 1]. Default is 0.5.

    Returns:
        Boolean mask of shape (H, W) where ``True`` indicates high confidence
        (NCC >= threshold) and ``False`` indicates low confidence.

    Raises:
        ValueError: If input shapes do not match or ncc_threshold is out of range.
    """
    if depth_primary.shape != depth_secondary.shape:
        raise ValueError(
            f"depth_primary and depth_secondary must have the same shape, "
            f"got {depth_primary.shape} vs {depth_secondary.shape}"
        )
    if not -1.0 <= ncc_threshold <= 1.0:
        raise ValueError(
            f"ncc_threshold must be in [-1, 1], got {ncc_threshold}"
        )

    ncc_map = compute_ncc(depth_primary, depth_secondary)
    mask = ncc_map >= ncc_threshold

    logger.info(
        "Cross-validation: %.1f%% pixels above NCC threshold %.2f",
        100.0 * float(np.mean(mask)),
        ncc_threshold,
    )

    return mask


def fuse_cubemap_depth_to_erp(
    face_depths: list[np.ndarray],
    face_directions: list[str],
    erp_height: int,
    erp_width: int,
) -> np.ndarray:
    """Fuse 6 cubemap face depth maps into a single equirectangular depth map.

    For each pixel in the ERP output, computes its 3D ray direction, determines
    which cubemap face(s) that ray falls on, and samples the corresponding depth.
    Overlap regions at face boundaries are handled by taking the minimum depth
    (closest surface wins).

    Coordinate conventions
    ----------------------
    * **ERP**: longitude ``theta = 2*pi*u/W`` (0 at left edge), colatitude
      ``phi = pi*v/H`` (0 at north pole, pi at south pole).
    * **Ray direction**:
      ``x = sin(phi)*sin(theta)``, ``y = cos(phi)``, ``z = sin(phi)*cos(theta)``.
    * **Cubemap faces** use the OpenGL convention for UV mapping:

      ========  ===  ===  ===
      Face      sc   tc   ma
      ========  ===  ===  ===
      front +Z  x    -y   |z|
      back  -Z  -x   -y   |z|
      right +X  -z   -y   |x|
      left  -X  z    -y   |x|
      top   +Y  x    z    |y|
      bottom-Y  x    -z   |y|
      ========  ===  ===  ===

      where ``s = 0.5*(sc/ma + 1)``, ``t = 0.5*(tc/ma + 1)``, and pixel
      coordinates are ``col = s*(W_face-1)``, ``row = t*(H_face-1)``.

    Args:
        face_depths: List of 6 cubemap face depth maps, each of shape
            ``(H_face, W_face)``. All faces must have the same spatial dimensions.
        face_directions: List of 6 direction strings, each one of ``'front'``,
            ``'back'``, ``'right'``, ``'left'``, ``'top'``, ``'bottom'``.
            Order must correspond to ``face_depths``.
        erp_height: Height of the output equirectangular depth map (pixels).
        erp_width: Width of the output equirectangular depth map (pixels).

    Returns:
        Equirectangular depth map of shape ``(erp_height, erp_width)``,
        dtype float32. Pixels that do not map to any provided face are set to 0.

    Raises:
        ValueError: If input lists have mismatched lengths, unknown face
            directions, or invalid ERP dimensions.
    """
    valid_directions = {"front", "back", "right", "left", "top", "bottom"}

    if len(face_depths) != len(face_directions):
        raise ValueError(
            f"face_depths and face_directions must have the same length, "
            f"got {len(face_depths)} vs {len(face_directions)}"
        )
    for d in face_directions:
        if d not in valid_directions:
            raise ValueError(
                f"Unknown face direction '{d}', must be one of {valid_directions}"
            )
    if erp_height <= 0 or erp_width <= 0:
        raise ValueError(
            f"erp_height and erp_width must be positive, "
            f"got {erp_height} x {erp_width}"
        )

    # Build ERP pixel grid
    u_coords = np.arange(erp_width, dtype=np.float64)
    v_coords = np.arange(erp_height, dtype=np.float64)
    uu, vv = np.meshgrid(u_coords, v_coords)  # (H, W)

    # Spherical coordinates
    theta = 2.0 * np.pi * uu / erp_width  # longitude [0, 2*pi]
    phi = np.pi * (vv + 0.5) / erp_height  # colatitude — offset by 0.5 for pixel centres

    # 3D ray directions (unit vectors)
    sin_phi = np.sin(phi)
    cos_phi = np.cos(phi)
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    dx = sin_phi * sin_theta  # x
    dy = cos_phi  # y  (up)
    dz = sin_phi * cos_theta  # z

    # Initialize output with infinity for min-reduction across faces
    erp_depth = np.full((erp_height, erp_width), np.inf, dtype=np.float64)

    # Process each cubemap face
    for face_depth, face_dir in zip(face_depths, face_directions):
        fh, fw = face_depth.shape[:2]
        face_float = face_depth.astype(np.float64)

        # Compute (s, t) UV on this face using OpenGL cubemap convention
        if face_dir == "front":  # +Z
            sc = dx
            tc = -dy
            ma = np.abs(dz)
        elif face_dir == "back":  # -Z
            sc = -dx
            tc = -dy
            ma = np.abs(dz)
        elif face_dir == "right":  # +X
            sc = -dz
            tc = -dy
            ma = np.abs(dx)
        elif face_dir == "left":  # -X
            sc = dz
            tc = -dy
            ma = np.abs(dx)
        elif face_dir == "top":  # +Y
            sc = dx
            tc = dz
            ma = np.abs(dy)
        elif face_dir == "bottom":  # -Y
            sc = dx
            tc = -dz
            ma = np.abs(dy)
        else:
            # Should not reach here due to earlier validation, but be safe
            raise ValueError(f"Unknown face direction '{face_dir}'")

        # Avoid division by zero for rays perpendicular to this face
        safe_ma = np.where(ma > 1e-10, ma, 1.0)
        s = 0.5 * (sc / safe_ma + 1.0)
        t = 0.5 * (tc / safe_ma + 1.0)

        # Validity mask: direction has a meaningful projection onto this face
        valid = ma > 1e-10

        # In-bounds mask: UV falls within [0, 1] on this face
        in_bounds = valid & (s >= 0.0) & (s <= 1.0) & (t >= 0.0) & (t <= 1.0)

        # Convert normalised UV to floating-point pixel coordinates
        col_f = s * (fw - 1)
        row_f = t * (fh - 1)

        # Bilinear interpolation for smooth sampling
        r0 = np.floor(row_f).astype(np.int32)
        c0 = np.floor(col_f).astype(np.int32)
        r1 = r0 + 1
        c1 = c0 + 1

        dr = row_f - r0.astype(np.float64)
        dc = col_f - c0.astype(np.float64)

        # Clamp indices to face image bounds for safe indexing
        r0c = np.clip(r0, 0, fh - 1)
        r1c = np.clip(r1, 0, fh - 1)
        c0c = np.clip(c0, 0, fw - 1)
        c1c = np.clip(c1, 0, fw - 1)

        sampled = (
            face_float[r0c, c0c] * (1.0 - dr) * (1.0 - dc)
            + face_float[r0c, c1c] * (1.0 - dr) * dc
            + face_float[r1c, c0c] * dr * (1.0 - dc)
            + face_float[r1c, c1c] * dr * dc
        )

        # Only trust samples whose bilinear footprint is entirely inside the face
        bilinear_valid = in_bounds & (r0 >= 0) & (r1 < fh) & (c0 >= 0) & (c1 < fw)
        safe_sampled = np.where(bilinear_valid, sampled, np.inf)

        # Min-reduce: closest surface wins
        erp_depth = np.minimum(erp_depth, safe_sampled)

    # Replace any remaining inf (unmapped pixels) with 0
    erp_depth = np.where(np.isinf(erp_depth), 0.0, erp_depth)

    valid_depth = erp_depth[erp_depth > 0]
    depth_min = float(np.min(valid_depth)) if valid_depth.size > 0 else 0.0
    depth_max = float(np.max(valid_depth)) if valid_depth.size > 0 else 0.0

    logger.info(
        "Fused %d cubemap faces to ERP %dx%d, depth range [%.2f, %.2f]",
        len(face_depths),
        erp_width,
        erp_height,
        depth_min,
        depth_max,
    )

    return erp_depth.astype(np.float32)
