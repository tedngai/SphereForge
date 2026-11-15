"""ERP-native depth backend for Stage 4.

The ``dap`` backend produces equirectangular (ERP) depth by rendering a
panorama rig of rectilinear virtual cameras from each ERP frame, running a
perspective monocular depth model on every view, and fusing the per-view depth
back into ERP pixel space.

Why a rig instead of feeding the ERP image straight to a perspective model?
Perspective models (Depth Anything V2, Metric3D, ...) assume a pinhole camera
with a limited field of view. Applied directly to a 360° equirectangular image
they see extreme distortion and produce inconsistent depth across the seam and
at the poles. Rendering rectilinear views removes that distortion; fusing the
views with inverse-distance weighting produces a seam-free ERP depth map.

Optional ERP-native weights
---------------------------
If a true ERP-native checkpoint is available (the original ``dap`` /
"Depth Any Panoramas" weights), it can be supplied explicitly via
``Stage04Config.dap_erp_weights`` (a directory containing ``config.json`` and
weights for a HuggingFace ``AutoModelForDepthEstimation``). Those weights are
**not** distributed with SphereForge, so by default the backend uses a
perspective model on the rig views, which needs no special weights.

The rig geometry mirrors :mod:`sphereforge.stages.stage02_cubemap.panorama_rig`
so that the ERP depth maps line up with the virtual views used for SfM.
"""

from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Any

import numpy as np

from sphereforge.stages.stage02_cubemap.cubemap import _make_rotation_matrix

logger = logging.getLogger("sphereforge.stage04.dap")

# Default rig: 8 yaw steps x 5 pitches = 40 views. Each view is rendered with a
# generous FOV so that neighbouring views overlap for robust fusion.
#
# The +/-90 rings matter: with only -45/0/+45 the poles are never viewed
# head-on, so the nadir and zenith are covered solely by grazing-angle
# observations where perspective depth models are least reliable. That shows up
# as a systematic ~3x depth bias at the poles.
_DEFAULT_YAW_STEPS = 8
_DEFAULT_PITCHES = (-90.0, -45.0, 0.0, 45.0, 90.0)
_DEFAULT_VIEW_FOV = 90.0
_DEFAULT_VIEW_RES = 512


def _render_rig_views(
    erp_image: np.ndarray,
    yaw_steps: int,
    pitches: tuple[float, ...],
    fov_deg: float,
    view_res: int,
) -> tuple[list[np.ndarray], list[tuple[float, float]]]:
    """Render rectilinear rig views from an ERP image.

    Args:
        erp_image: ERP image ``(H, W, 3)`` uint8.
        yaw_steps: Number of evenly spaced yaw angles around the horizon.
        pitches: Elevation angles (degrees) for each ring of views.
        fov_deg: Field of view of each square view (degrees).
        view_res: Side length of each square view in pixels.

    Returns:
        ``(images, angles)`` where *images* is a list of ``(view_res, view_res, 3)``
        uint8 arrays and *angles* lists the ``(yaw_deg, pitch_deg)`` of each view.
    """
    import cv2

    erp_h, erp_w = erp_image.shape[:2]
    focal = view_res / (2.0 * math.tan(math.radians(fov_deg) / 2.0))
    center = view_res / 2.0

    u_coords = np.arange(view_res, dtype=np.float64)
    v_coords = np.arange(view_res, dtype=np.float64)
    uu, vv = np.meshgrid(u_coords, v_coords)
    dx = (uu - center) / focal
    dy = (vv - center) / focal
    dz = np.ones_like(dx)
    norms = np.sqrt(dx * dx + dy * dy + dz * dz)
    dirs_cam = np.stack([dx / norms, dy / norms, dz / norms], axis=-1)

    images: list[np.ndarray] = []
    angles: list[tuple[float, float]] = []
    for pitch_deg in pitches:
        # A view pointing at a pole is invariant to yaw, so rendering it once
        # per yaw step would just duplicate the same image (and skew the fusion
        # weights toward the poles).
        at_pole = abs(abs(pitch_deg) - 90.0) < 1e-6
        steps = 1 if at_pole else yaw_steps
        for step in range(steps):
            yaw_deg = 360.0 * step / yaw_steps
            rotation = _make_rotation_matrix(yaw_deg, pitch_deg)
            dirs_world = np.einsum("ij,...j->...i", rotation.T, dirs_cam)

            x, y, z = dirs_world[..., 0], dirs_world[..., 1], dirs_world[..., 2]
            phi = np.arctan2(x, -z)
            theta = np.arcsin(np.clip(y, -1.0, 1.0))
            erp_u = (phi + math.pi) / (2.0 * math.pi) * erp_w
            erp_v = (math.pi / 2.0 - theta) / math.pi * erp_h

            # ERP is periodic in longitude, but cv2.remap's BORDER_WRAP only
            # replicates the edge pixel, so the seam column (u == W) would
            # sample the wrong part of the panorama. Wrap u explicitly.
            erp_u = np.mod(erp_u, erp_w)
            erp_v = np.clip(erp_v, 0.0, erp_h - 1.0)

            view = cv2.remap(
                erp_image,
                erp_u.astype(np.float32),
                erp_v.astype(np.float32),
                interpolation=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REPLICATE,
            )
            images.append(view)
            angles.append((yaw_deg, pitch_deg))

    return images, angles


def _harmonize_view_scales(
    view_depths: list[np.ndarray],
    max_scale_ratio: float = 4.0,
) -> list[np.ndarray]:
    """Put per-view relative depth (or disparity) maps onto a common scale.

    The rig path calls this on *disparity*, the space in which Depth Anything
    V2's per-image ambiguity is affine. Each image is only defined up
    to an unknown affine transform, so the same surface seen by two rig views
    can come back at wildly different magnitudes. Measured on a panorama rig of
    one room, the per-view scale factors spanned 5x (0.63 to 3.08).

    Two passes are used:

    1. **Median normalisation.** Cheap and robust, and it removes most of the
       per-image ambiguity.
    2. **Affine refinement against the consensus.** After step 1 the views
       disagree mainly by an offset, so each view is fitted to the median
       (consensus) map with a least-squares ``a * view + b``. This recovers the
       per-view scale and shift that median normalisation alone cannot.

    Args:
        view_depths: Per-view depth maps, any common square shape.
        max_scale_ratio: Views whose median differs from the global median by
            more than this factor are treated as outliers and left unscaled.

    Returns:
        New list of depth maps on a common scale.
    """
    if not view_depths:
        return []

    medians = np.array(
        [float(np.median(d[d > 0])) if np.any(d > 0) else 0.0 for d in view_depths],
        dtype=np.float64,
    )
    valid = medians > 0
    if not np.any(valid):
        return list(view_depths)

    target = float(np.median(medians[valid]))

    # Pass 1: median normalisation.
    normalized: list[np.ndarray] = []
    for depth, median, is_valid in zip(view_depths, medians, valid, strict=True):
        if not is_valid or median <= 0:
            normalized.append(depth.astype(np.float32))
            continue
        ratio = median / target
        if ratio > max_scale_ratio or ratio < 1.0 / max_scale_ratio:
            normalized.append(depth.astype(np.float32))
            continue
        normalized.append((depth * (target / median)).astype(np.float32))

    # Pass 2: affine refinement against the per-pixel consensus.
    stack = np.stack([d.astype(np.float64) for d in normalized], axis=0)
    consensus = np.median(stack, axis=0)
    refined: list[np.ndarray] = []
    for depth in normalized:
        sample = depth.astype(np.float64)
        ok = (sample > 0) & (consensus > 0)
        if int(np.sum(ok)) < 64:
            refined.append(depth)
            continue
        x = sample[ok]
        y = consensus[ok]
        # Least-squares fit y = a*x + b.
        design = np.stack([x, np.ones_like(x)], axis=1)
        try:
            (a, b), *_ = np.linalg.lstsq(design, y, rcond=None)
        except np.linalg.LinAlgError:
            refined.append(depth)
            continue
        # Reject degenerate fits (collapse or flip).
        if not np.isfinite(a) or not np.isfinite(b) or a <= 0.2 or a > 5.0:
            refined.append(depth)
            continue
        adjusted = a * sample + b
        adjusted = np.where(sample > 0, adjusted, 0.0)
        refined.append(np.clip(adjusted, 0.0, None).astype(np.float32))

    logger.debug(
        "Harmonized %d rig views (median + affine refinement, target median %.3f)",
        int(np.sum(valid)),
        target,
    )
    return refined


def _erp_world_dirs(erp_height: int, erp_width: int) -> np.ndarray:
    """Unit world directions for every ERP pixel (Stage 2 convention)."""
    phi = (np.arange(erp_width) + 0.5) / erp_width * 2.0 * math.pi - math.pi
    theta = math.pi / 2.0 - (np.arange(erp_height) + 0.5) / erp_height * math.pi
    phi_grid, theta_grid = np.meshgrid(phi, theta)
    cos_theta = np.cos(theta_grid)
    return np.stack(
        [np.sin(phi_grid) * cos_theta, np.sin(theta_grid), -np.cos(phi_grid) * cos_theta],
        axis=-1,
    )


def _sample_view_on_erp(
    view: np.ndarray,
    yaw_deg: float,
    pitch_deg: float,
    fov_deg: float,
    dirs_world: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Sample one rig view at the ERP pixels it covers.

    Args:
        view: Square per-view map ``(S, S)``.
        yaw_deg: View yaw in degrees.
        pitch_deg: View pitch in degrees.
        fov_deg: View field of view in degrees.
        dirs_world: ERP world directions ``(H, W, 3)``.

    Returns:
        ``(flat_idx, values, ray_norm, weight)`` for the covered ERP pixels:
        flat ERP indices, the bilinearly sampled view values, the
        perspective-to-radial factor ``|(dx, dy, 1)|`` and a centre-weighted
        blending weight.
    """
    from scipy.ndimage import map_coordinates

    view_res = view.shape[0]
    focal = view_res / (2.0 * math.tan(math.radians(fov_deg) / 2.0))
    center = view_res / 2.0
    rotation = _make_rotation_matrix(yaw_deg, pitch_deg)
    dirs_cam = np.einsum("ij,...j->...i", rotation, dirs_world)
    z = dirs_cam[..., 2]
    in_front = z > 1e-6
    safe_z = np.where(in_front, z, 1.0)
    u = dirs_cam[..., 0] / safe_z * focal + center
    v = dirs_cam[..., 1] / safe_z * focal + center
    inside = in_front & (u >= 0) & (u <= view_res - 1) & (v >= 0) & (v <= view_res - 1)
    flat_idx = np.flatnonzero(inside)
    if flat_idx.size == 0:
        empty = np.zeros(0, dtype=np.float64)
        return flat_idx, empty, empty, empty
    uu = u.ravel()[flat_idx]
    vv = v.ravel()[flat_idx]
    values = map_coordinates(np.asarray(view, dtype=np.float64), [vv, uu], order=1, mode="nearest")
    off_x = (uu - center) / focal
    off_y = (vv - center) / focal
    ray_norm = np.sqrt(1.0 + off_x**2 + off_y**2)
    r2 = ((uu - center) ** 2 + (vv - center) ** 2) / (center**2)
    weight = 1.0 / (1.0 + 4.0 * r2)
    return flat_idx, values, ray_norm, weight


def _fuse_disparity_views_to_erp(
    view_disparities: list[np.ndarray],
    angles: list[tuple[float, float]],
    fov_deg: float,
    erp_height: int,
    erp_width: int,
    iterations: int = 40,
    fit_downsample: int = 4,
    max_range_ratio: float = 100.0,
    tolerance: float = 1e-5,
) -> np.ndarray:
    """Fuse per-view relative *disparity* maps into one ERP depth map.

    Depth Anything V2 predicts each view's disparity only up to its own affine
    transform ``pred = a / z + b``. Views are put on a common scale by fitting
    each view's ``(a, b)`` to the consensus of the *other* views where they
    actually overlap on the sphere, working in radial inverse depth
    ``1 / r = (a * pred + b) / |(dx, dy, 1)|``. That is the space in which the
    ambiguity is linear, so a least-squares fit is exact for noise-free input.

    (Comparing views pixel-for-pixel in their own image grids, as the older
    harmonisation did, compares unrelated scene points; on the synthetic room
    it lowered depth/ground-truth rank correlation from about 0.55 to 0.3.)

    Args:
        view_disparities: Per-view disparity maps ``(S, S)`` (larger = closer).
        angles: ``(yaw_deg, pitch_deg)`` per view.
        fov_deg: View field of view in degrees.
        erp_height: Output ERP height.
        erp_width: Output ERP width.
        iterations: Maximum alternating consensus/fit rounds. The update is
            Jacobi-style and needs ~20 rounds to converge on exact input.
        fit_downsample: ERP subsampling factor used while fitting (the fit
            grid is never smaller than 64 x 128, or the ERP itself).
        tolerance: Stop early once no view's ``(a, b)`` changes by more than
            this relative amount.
        max_range_ratio: Largest allowed far/near distance ratio; farther
            pixels are returned as 0 (invalid).

    Returns:
        ERP radial depth ``(erp_height, erp_width)`` float32, arbitrary scale,
        0 where invalid.

    Raises:
        ValueError: If *view_disparities* is empty or not all ``(S, S)``.
    """
    if not view_disparities:
        raise ValueError("Cannot fuse an empty list of view disparities")
    view_res = view_disparities[0].shape[0]
    if any(d.shape != (view_res, view_res) for d in view_disparities):
        raise ValueError("All view disparities must share the same square shape")

    # --- Fit per-view affine parameters on a subsampled ERP grid. ---
    fit_h = min(erp_height, max(64, erp_height // max(fit_downsample, 1)))
    fit_w = min(erp_width, max(128, erp_width // max(fit_downsample, 1)))
    fit_dirs = _erp_world_dirs(fit_h, fit_w)
    samples = [
        _sample_view_on_erp(view, yaw, pitch, fov_deg, fit_dirs)
        for view, (yaw, pitch) in zip(view_disparities, angles, strict=True)
    ]
    n_views = len(samples)
    a = np.ones(n_views, dtype=np.float64)
    b = np.zeros(n_views, dtype=np.float64)
    for i, (_, vals, _, _) in enumerate(samples):
        pos = vals[vals > 0]
        if pos.size:
            a[i] = 1.0 / float(np.median(pos))

    n_pix = fit_h * fit_w
    for _ in range(max(iterations, 0)):
        acc = np.zeros(n_pix, dtype=np.float64)
        wsum = np.zeros(n_pix, dtype=np.float64)
        count = np.zeros(n_pix, dtype=np.int32)
        per_view_q = []
        for i, (idx, vals, rn, w) in enumerate(samples):
            q = (a[i] * vals + b[i]) / rn
            per_view_q.append(q)
            np.add.at(acc, idx, w * q)
            np.add.at(wsum, idx, w)
            np.add.at(count, idx, 1)
        new_a = a.copy()
        new_b = b.copy()
        for i, (idx, vals, rn, w) in enumerate(samples):
            # Consensus of the *other* views at this view's pixels.
            other_w = wsum[idx] - w
            shared = (count[idx] >= 2) & (other_w > 1e-9)
            if int(np.sum(shared)) < 64:
                continue
            target = (acc[idx][shared] - (w * per_view_q[i])[shared]) / other_w[shared]
            x1 = vals[shared] / rn[shared]
            x0 = 1.0 / rn[shared]
            sw = np.sqrt(w[shared])
            design = np.stack([x1 * sw, x0 * sw], axis=1)
            try:
                (ai, bi), *_ = np.linalg.lstsq(design, target * sw, rcond=None)
            except np.linalg.LinAlgError:
                continue
            if np.isfinite(ai) and np.isfinite(bi) and ai > 0:
                new_a[i], new_b[i] = ai, bi
        # Fix the gauge (overall scale is arbitrary) so it cannot drift.
        q_all = np.concatenate(
            [(new_a[i] * s[1] + new_b[i]) / s[2] for i, s in enumerate(samples)]
        )
        q_pos = q_all[q_all > 0]
        gauge = float(np.median(q_pos)) if q_pos.size else 1.0
        new_a, new_b = new_a / gauge, new_b / gauge
        change = float(
            np.max(np.abs(new_a - a) / np.maximum(np.abs(a), 1e-12))
            + np.max(np.abs(new_b - b)) / max(float(np.median(np.abs(new_a))), 1e-12)
        )
        a, b = new_a, new_b
        if change < tolerance:
            break

    # --- Full-resolution fusion in inverse-depth space. ---
    dirs = _erp_world_dirs(erp_height, erp_width)
    acc = np.zeros(erp_height * erp_width, dtype=np.float64)
    wsum = np.zeros(erp_height * erp_width, dtype=np.float64)
    for i, (view, (yaw, pitch)) in enumerate(zip(view_disparities, angles, strict=True)):
        idx, vals, rn, w = _sample_view_on_erp(view, yaw, pitch, fov_deg, dirs)
        if idx.size == 0:
            continue
        q = (a[i] * vals + b[i]) / rn
        ok = np.isfinite(q) & (q > 0)
        np.add.at(acc, idx[ok], (w * q)[ok])
        np.add.at(wsum, idx[ok], w[ok])
    inv_depth = np.zeros_like(acc)
    covered = wsum > 0
    inv_depth[covered] = acc[covered] / wsum[covered]
    depth = np.zeros_like(acc, dtype=np.float32)
    if np.any(inv_depth > 0):
        floor = float(np.max(inv_depth)) / max(max_range_ratio, 1.0)
        valid = inv_depth > floor
        depth[valid] = (1.0 / inv_depth[valid]).astype(np.float32)
    logger.info(
        "ERP disparity fusion: %d views, per-view scale a in [%.3g, %.3g], "
        "%.1f%% of ERP pixels valid",
        n_views,
        float(np.min(a)),
        float(np.max(a)),
        100.0 * float(np.mean(depth > 0)),
    )
    return depth.reshape(erp_height, erp_width)


def _fuse_views_to_erp(
    view_depths: list[np.ndarray],
    angles: list[tuple[float, float]],
    fov_deg: float,
    erp_height: int,
    erp_width: int,
) -> np.ndarray:
    """Fuse per-view perspective depth maps into an ERP depth map.

    Every ERP pixel is back-projected to a world direction, mapped into each
    view, and the view's depth is converted to a radial (ray) distance. Views
    are combined with inverse-distance weighting that favours pixels near the
    view centre (where perspective models are most accurate) and tapers off
    toward the view borders, which also removes seams between views.

    Args:
        view_depths: Per-view depth maps ``(S, S)`` float32, larger = farther.
        angles: ``(yaw_deg, pitch_deg)`` for each view, same order as *view_depths*.
        fov_deg: Field of view of each view (degrees).
        erp_height: Output ERP height.
        erp_width: Output ERP width.

    Returns:
        ERP depth map ``(erp_height, erp_width)`` float32. Pixels not covered by
        any view are set to 0.

    Raises:
        ValueError: If *view_depths* is empty or shapes are inconsistent.
    """
    if not view_depths:
        raise ValueError("Cannot fuse an empty list of view depths")
    view_res = view_depths[0].shape[0]
    if any(d.shape != (view_res, view_res) for d in view_depths):
        raise ValueError("All view depths must share the same square shape")

    focal = view_res / (2.0 * math.tan(math.radians(fov_deg) / 2.0))
    center = view_res / 2.0

    # ERP pixel grid -> world directions (matches stage02 cubemap convention).
    phi = (np.arange(erp_width) + 0.5) / erp_width * 2.0 * math.pi - math.pi
    theta = math.pi / 2.0 - (np.arange(erp_height) + 0.5) / erp_height * math.pi
    phi_grid, theta_grid = np.meshgrid(phi, theta)
    cos_theta = np.cos(theta_grid)
    dirs_world = np.stack(
        [
            np.sin(phi_grid) * cos_theta,
            np.sin(theta_grid),
            -np.cos(phi_grid) * cos_theta,
        ],
        axis=-1,
    )

    accum = np.zeros((erp_height, erp_width), dtype=np.float64)
    weight_sum = np.zeros((erp_height, erp_width), dtype=np.float64)
    # Track the nearest observation so that thin foreground geometry survives
    # averaging (a far background view must not pull a foreground pixel back).
    nearest = np.full((erp_height, erp_width), np.inf, dtype=np.float64)
    # Neighbouring views see the same surface at slightly different depths, so
    # "nearest" is only trusted when it is clearly closer than the weighted mean.
    near_ratio = 0.85

    for view_depth, (yaw_deg, pitch_deg) in zip(view_depths, angles, strict=True):
        rotation = _make_rotation_matrix(yaw_deg, pitch_deg)
        dirs_cam = np.einsum("ij,...j->...i", rotation, dirs_world)
        z = dirs_cam[..., 2]
        in_front = z > 1e-6
        safe_z = np.where(in_front, z, 1.0)
        u = dirs_cam[..., 0] / safe_z * focal + center
        v = dirs_cam[..., 1] / safe_z * focal + center
        inside = in_front & (u >= 0) & (u <= view_res - 1) & (v >= 0) & (v <= view_res - 1)

        if not np.any(inside):
            continue

        from scipy.ndimage import map_coordinates

        view_depth_f = np.asarray(view_depth, dtype=np.float64)
        # A view pixel's perspective depth is the distance along the view axis,
        # so the pixel's 3D point is depth * (dx, dy, 1). Its radial distance
        # from the camera is therefore depth * |(dx, dy, 1)|.
        offset_x = (u[inside] - center) / focal
        offset_y = (v[inside] - center) / focal
        ray_norm = np.sqrt(1.0 + offset_x**2 + offset_y**2)
        sampled = map_coordinates(
            view_depth_f,
            [v[inside], u[inside]],
            order=1,
            mode="nearest",
        )
        radial = sampled * ray_norm

        # Centre-weighted blending: weight falls off toward the view border.
        # The weight is applied in *inverse* radial depth space, so nearby
        # geometry (which is what matters for Gaussian seeding) is not
        # dominated by far-away views.
        r2 = ((u[inside] - center) ** 2 + (v[inside] - center) ** 2) / (center**2)
        weight = 1.0 / (1.0 + 4.0 * r2)

        valid = np.isfinite(radial) & (radial > 0)
        idx = np.where(inside)
        rows, cols = idx[0][valid], idx[1][valid]
        accum[rows, cols] += (radial * weight)[valid]
        weight_sum[rows, cols] += weight[valid]
        np.minimum.at(nearest, (rows, cols), radial[valid])

    erp_depth = np.zeros((erp_height, erp_width), dtype=np.float32)
    covered = weight_sum > 0
    weighted_mean = np.zeros_like(accum)
    weighted_mean[covered] = accum[covered] / weight_sum[covered]
    erp_depth[covered] = weighted_mean[covered].astype(np.float32)
    # Prefer the nearest observation where it is clearly closer than the mean.
    keep_nearest = covered & (nearest < weighted_mean * near_ratio)
    erp_depth[keep_nearest] = nearest[keep_nearest].astype(np.float32)
    logger.info(
        "ERP fusion: %d views, %.1f%% of ERP pixels covered",
        len(view_depths),
        100.0 * float(np.mean(covered)),
    )
    return erp_depth


class DAPModel:
    """ERP-native depth backend (panorama rig + perspective model fusion).

    Args:
        model_size: Perspective model size passed to
            :class:`~sphereforge.models.depth_anything_v2.DepthAnythingV2Model`
            (``"small"`` default, Apache-2.0).
        device: ``"auto"``, ``"cuda"`` or ``"cpu"``.
        cache_dir: Optional local cache directory for the perspective model.
        max_depth: Upper clip applied to the fused ERP depth (0 disables).
        erp_weights: Optional directory with true ERP-native weights. When
            provided, the ERP frame is fed directly to that model instead of
            using the rig fusion path.
        yaw_steps: Number of yaw samples in the rig (default 8).
        pitches: Elevation angles for the rig rings (default -45/0/45).
        view_fov: Field of view of each rig view in degrees (default 90).
        view_res: Side length of each rig view in pixels (default 512).
        half: Load the perspective model in float16 on CUDA.

    Raises:
        ValueError: If the rig parameters are invalid.
    """

    def __init__(
        self,
        model_size: str = "small",
        device: str = "auto",
        cache_dir: Path | None = None,
        max_depth: float = 0.0,
        erp_weights: Path | None = None,
        yaw_steps: int = _DEFAULT_YAW_STEPS,
        pitches: tuple[float, ...] = _DEFAULT_PITCHES,
        view_fov: float = _DEFAULT_VIEW_FOV,
        view_res: int = _DEFAULT_VIEW_RES,
        half: bool = False,
    ) -> None:
        if yaw_steps < 1:
            raise ValueError("yaw_steps must be >= 1")
        if not pitches:
            raise ValueError("pitches must contain at least one angle")
        if view_res < 16:
            raise ValueError("view_res must be >= 16")

        self.model_size = model_size
        self.device = device
        self.cache_dir = cache_dir
        self.max_depth = float(max_depth)
        self.erp_weights = Path(erp_weights) if erp_weights is not None else None
        self.yaw_steps = int(yaw_steps)
        self.pitches = tuple(float(p) for p in pitches)
        self.view_fov = float(view_fov)
        self.view_res = int(view_res)
        self.half = half

        self._perspective: Any = None
        self._erp: Any = None

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Lazily construct the underlying perspective or ERP-native model."""
        if self._erp is not None or self._perspective is not None:
            return

        if self.erp_weights is not None:
            if not (self.erp_weights / "config.json").exists():
                raise RuntimeError(
                    f"dap_erp_weights={self.erp_weights} does not contain config.json. "
                    "Point it at a local HuggingFace AutoModelForDepthEstimation directory."
                )
            self._erp = self._build_erp_model(self.erp_weights)
            logger.info("DAP backend using ERP-native weights: %s", self.erp_weights)
            return

        from sphereforge.models.depth_anything_v2 import DepthAnythingV2Model

        self._perspective = DepthAnythingV2Model(
            model_size=self.model_size,
            device=self.device,
            cache_dir=self.cache_dir,
            half=self.half,
        )
        logger.info(
            "DAP backend using panorama-rig fusion: %d views "
            "(yaw_steps=%d, pitches=%s, fov=%.0f, res=%d)",
            self.yaw_steps * len(self.pitches),
            self.yaw_steps,
            list(self.pitches),
            self.view_fov,
            self.view_res,
        )

    @staticmethod
    def _build_erp_model(weights_dir: Path) -> Any:
        """Load a HuggingFace depth model that accepts ERP images directly."""
        try:
            import torch
            from transformers import AutoImageProcessor, AutoModelForDepthEstimation
        except ImportError as exc:  # pragma: no cover - env dependent
            raise NotImplementedError(
                "ERP-native DAP weights require 'transformers' and 'torch'. "
                "Install with: pip install 'sphereforge[depth]'"
            ) from exc

        processor = AutoImageProcessor.from_pretrained(str(weights_dir))
        model = AutoModelForDepthEstimation.from_pretrained(str(weights_dir)).eval()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        return {"processor": processor, "model": model.to(device), "device": device}

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def estimate_depth(self, image: np.ndarray) -> np.ndarray:
        """Estimate ERP depth for a single equirectangular frame.

        Args:
            image: ERP image ``(H, W, 3)`` uint8.

        Returns:
            ERP depth map ``(H, W)`` float32 (larger = farther).

        Raises:
            ValueError: If *image* is not ``(H, W, 3)``.
        """
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError(f"Expected ERP image with shape (H, W, 3), got {image.shape}")
        return self.estimate_depth_batch([image])[0]

    def estimate_depth_batch(self, images: list[np.ndarray]) -> list[np.ndarray]:
        """Estimate ERP depth for a list of equirectangular frames.

        Args:
            images: List of ERP images ``(H_i, W_i, 3)`` uint8.

        Returns:
            List of ERP depth maps ``(H_i, W_i)`` float32.

        Raises:
            ValueError: If any image is not ``(H, W, 3)``.
        """
        if not images:
            return []
        self._load()
        results: list[np.ndarray] = []
        for idx, image in enumerate(images):
            if image.ndim != 3 or image.shape[2] != 3:
                raise ValueError(
                    f"Image at index {idx} has shape {image.shape}, expected (H, W, 3)"
                )
            if self._erp is not None:
                depth = self._estimate_erp_native(image)
            else:
                depth = self._estimate_via_rig(image)
            if self.max_depth > 0:
                depth = np.where(depth > self.max_depth, 0.0, depth).astype(np.float32)
            results.append(depth)
            logger.debug(
                "DAP depth %d/%d: %s -> range [%.3f, %.3f]",
                idx + 1,
                len(images),
                image.shape[:2],
                float(depth[depth > 0].min()) if np.any(depth > 0) else 0.0,
                float(depth.max()),
            )
        return results

    def _estimate_erp_native(self, image: np.ndarray) -> np.ndarray:
        """Run a true ERP-native model directly on the equirectangular image."""
        import torch

        processor = self._erp["processor"]
        model = self._erp["model"]
        device = self._erp["device"]
        with torch.inference_mode():
            inputs = processor(images=image, return_tensors="pt")
            inputs = {k: v.to(device) for k, v in inputs.items()}
            predicted = model(**inputs).predicted_depth
            predicted = torch.nn.functional.interpolate(
                predicted.unsqueeze(1),
                size=image.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze(1)
        return predicted[0].float().cpu().numpy().astype(np.float32)

    def _estimate_via_rig(self, image: np.ndarray) -> np.ndarray:
        """Render rig views, estimate per-view depth, and fuse back to ERP."""
        views, angles = _render_rig_views(
            image,
            yaw_steps=self.yaw_steps,
            pitches=self.pitches,
            fov_deg=self.view_fov,
            view_res=self.view_res,
        )
        if not getattr(self._perspective, "outputs_metric_depth", False):
            # Relative Depth Anything V2 outputs affine-invariant *disparity*.
            # Fit each view's affine onto its real overlap with the other
            # views, in inverse-depth space, then invert to depth.
            view_disp = self._perspective.estimate_disparity_batch(views)
            return _fuse_disparity_views_to_erp(
                view_disp,
                angles,
                fov_deg=self.view_fov,
                erp_height=image.shape[0],
                erp_width=image.shape[1],
            )
        view_depths = _harmonize_view_scales(self._perspective.estimate_depth_batch(views))
        return _fuse_views_to_erp(
            view_depths,
            angles,
            fov_deg=self.view_fov,
            erp_height=image.shape[0],
            erp_width=image.shape[1],
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def is_stub(self) -> bool:
        """The rig-fusion path is a fully implemented backend."""
        return False

    @property
    def backend_kind(self) -> str:
        """``"erp_native"`` when ERP weights are supplied, else ``"rig_fusion"``."""
        return "erp_native" if self.erp_weights is not None else "rig_fusion"

    def __repr__(self) -> str:
        return (
            f"DAPModel(backend={self.backend_kind!r}, model_size={self.model_size!r}, "
            f"yaw_steps={self.yaw_steps}, pitches={self.pitches}, "
            f"view_fov={self.view_fov}, view_res={self.view_res})"
        )
