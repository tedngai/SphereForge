"""ErpGS distortion-aware loss functions and scale-flattening regularization.

Implements the ErpGS (arXiv:2505.19883) latitude-weighted loss for
equirectangular projection training, which counteracts the area distortion
inherent in ERP by weighting per-pixel losses by cos(latitude).

Also provides the scale-flattening loss that penalises oversized Gaussians
at high latitudes where ERP distortion amplifies their apparent size.
"""

from __future__ import annotations

import logging
import math

import torch
import torch.nn.functional as F

logger = logging.getLogger("sphereforge.stage06.erp_loss")

# ---------------------------------------------------------------------------
# Face direction → (yaw_deg, pitch_deg) mapping
# Matches cubemap.py CUBEMAP_FACES convention (camera looks along +Z in
# camera frame, rotated by yaw then pitch to obtain world-frame direction).
# ---------------------------------------------------------------------------
_FACE_YAW_PITCH: dict[str, tuple[float, float]] = {
    "front": (0.0, 0.0),
    "right": (90.0, 0.0),
    "back": (180.0, 0.0),
    "left": (-90.0, 0.0),
    "top": (0.0, 90.0),
    "bottom": (0.0, -90.0),
}


# ---------------------------------------------------------------------------
# Helpers for differentiable SSIM map
# ---------------------------------------------------------------------------


def _gaussian_kernel_1d(size: int, sigma: float, device: torch.device) -> torch.Tensor:
    """Create a 1-D Gaussian kernel.

    Args:
        size: Kernel size (odd number).
        sigma: Standard deviation.
        device: Torch device.

    Returns:
        1-D kernel of shape ``(size,)``.
    """
    coords = torch.arange(size, dtype=torch.float32, device=device) - size // 2
    g = torch.exp(-coords ** 2 / (2.0 * sigma ** 2))
    return g / g.sum()


def _gaussian_kernel_2d(
    size: int, sigma: float, channels: int, device: torch.device
) -> torch.Tensor:
    """Create a 2-D Gaussian kernel for grouped depthwise convolution.

    Args:
        size: Kernel size (odd).
        sigma: Standard deviation.
        channels: Number of input channels (each processed independently).
        device: Torch device.

    Returns:
        Kernel of shape ``(channels, 1, size, size)`` suitable for
        ``F.conv2d(..., groups=channels)``.
    """
    k1d = _gaussian_kernel_1d(size, sigma, device)
    k2d = k1d.unsqueeze(1) * k1d.unsqueeze(0)  # (size, size)
    kernel = k2d.unsqueeze(0).unsqueeze(0).expand(channels, 1, size, size).contiguous()
    return kernel


def _ssim_map(
    x: torch.Tensor,
    y: torch.Tensor,
    window_size: int = 11,
    sigma: float = 1.5,
) -> torch.Tensor:
    """Compute a per-pixel SSIM map between two images.

    Uses a Gaussian-windowed SSIM formulation that is differentiable
    and suitable for training.

    Args:
        x: First image, shape ``(H, W, C)``, float values in [0, 1].
        y: Second image, shape ``(H, W, C)``, float values in [0, 1].
        window_size: Side length of the Gaussian window (default 11).
        sigma: Std-dev of the Gaussian window (default 1.5).

    Returns:
        SSIM map of shape ``(H, W)`` with values in approximately [-1, 1].
    """
    C = x.shape[2]
    device = x.device

    # Reshape to (1, C, H, W) for conv2d
    x_4d = x.permute(2, 0, 1).unsqueeze(0)
    y_4d = y.permute(2, 0, 1).unsqueeze(0)

    kernel = _gaussian_kernel_2d(window_size, sigma, C, device)
    pad = window_size // 2

    # Local means
    mu_x = F.conv2d(x_4d, kernel, padding=pad, groups=C)
    mu_y = F.conv2d(y_4d, kernel, padding=pad, groups=C)

    mu_x_sq = mu_x ** 2
    mu_y_sq = mu_y ** 2
    mu_xy = mu_x * mu_y

    # Local variances and covariance
    sigma_x_sq = F.conv2d(x_4d ** 2, kernel, padding=pad, groups=C) - mu_x_sq
    sigma_y_sq = F.conv2d(y_4d ** 2, kernel, padding=pad, groups=C) - mu_y_sq
    sigma_xy = F.conv2d(x_4d * y_4d, kernel, padding=pad, groups=C) - mu_xy

    # SSIM stability constants
    C1 = 0.01 ** 2
    C2 = 0.03 ** 2

    ssim_4d = ((2.0 * mu_xy + C1) * (2.0 * sigma_xy + C2)) / (
        (mu_x_sq + mu_y_sq + C1) * (sigma_x_sq + sigma_y_sq + C2)
    )

    # Average over channels, squeeze batch dim: (1, C, H, W) -> (H, W)
    return ssim_4d.mean(dim=1).squeeze(0)


# ---------------------------------------------------------------------------
# T6.1 — ErpGS distortion-aware loss
# ---------------------------------------------------------------------------


def erp_weighted_loss(
    rendered: torch.Tensor,
    target: torch.Tensor,
    latitudes: torch.Tensor,
    l1_weight: float = 0.8,
    ssim_weight: float = 0.2,
) -> torch.Tensor:
    """Compute ErpGS distortion-aware latitude-weighted loss.

    Weights per-pixel L1 and SSIM losses by ``cos(latitude)`` to counteract
    the area distortion of equirectangular projection.  Pixels near the
    equator (latitude ≈ 0) receive weight ≈ 1.0; pixels near the poles
    (latitude ≈ ±π/2) receive weight ≈ 0.0.

    The combined loss is::

        loss = l1_weight * mean(cos(lat) * |rendered - target|)
             + ssim_weight * mean(cos(lat) * (1 - SSIM_map))

    Args:
        rendered: Rendered image, shape ``(H, W, C)``, float in [0, 1].
        target: Ground-truth image, shape ``(H, W, C)``, float in [0, 1].
        latitudes: Per-pixel latitude in radians, shape ``(H, W)``.
            0 at equator, ±π/2 at poles.
        l1_weight: Weight for the L1 component (default 0.8).
        ssim_weight: Weight for the SSIM component (default 0.2).

    Returns:
        Scalar loss tensor (differentiable w.r.t. *rendered*).

    Raises:
        ValueError: If shapes are incompatible.
    """
    if rendered.shape != target.shape:
        raise ValueError(
            f"Shape mismatch: rendered {rendered.shape} vs target {target.shape}"
        )
    if rendered.ndim != 3:
        raise ValueError(f"Expected (H, W, C) tensor, got shape {rendered.shape}")

    # Cosine weight map — 1 at equator, 0 at poles
    weights = torch.cos(latitudes)  # (H, W)

    # --- L1 component, per-pixel weighted ---
    l1_per_pixel = (rendered - target).abs().mean(dim=-1)  # (H, W)
    l1_weighted = (weights * l1_per_pixel).mean()

    # --- SSIM component, per-pixel weighted ---
    ssim = _ssim_map(rendered, target)  # (H, W)
    ssim_loss_per_pixel = 1.0 - ssim  # (H, W)
    ssim_weighted = (weights * ssim_loss_per_pixel).mean()

    loss = l1_weight * l1_weighted + ssim_weight * ssim_weighted

    logger.debug(
        "erp_weighted_loss: L1=%.6f, SSIM_loss=%.6f, total=%.6f",
        l1_weighted.item(),
        ssim_weighted.item(),
        loss.item(),
    )

    return loss


# ---------------------------------------------------------------------------
# T6.1 helper — latitude computation from cubemap crop geometry
# ---------------------------------------------------------------------------


def _make_rotation_matrix(yaw_deg: float, pitch_deg: float) -> torch.Tensor:
    """Build a 3x3 rotation matrix from yaw and pitch (Y-down convention).

    Rotation order: yaw around Y, then pitch around X.  The resulting
    matrix **R** is the world→camera rotation so that
    ``R @ world_point = camera_point``.

    Matches the convention in ``stage02_cubemap/cubemap.py``.

    Args:
        yaw_deg: Yaw angle in degrees (positive = rotate right).
        pitch_deg: Pitch angle in degrees (positive = tilt up).

    Returns:
        3x3 rotation matrix, float64.
    """
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)

    cy, sy = math.cos(yaw), math.sin(yaw)
    ry = torch.tensor(
        [[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]],
        dtype=torch.float64,
    )

    cp, sp = math.cos(pitch), math.sin(pitch)
    rx = torch.tensor(
        [[1.0, 0.0, 0.0], [0.0, cp, -sp], [0.0, sp, cp]],
        dtype=torch.float64,
    )

    return rx @ ry


def compute_latitudes_from_crops(
    crop_h: int,
    crop_w: int,
    face_name: str,
    yaw_offset: float,
    fov: float,
) -> torch.Tensor:
    """Compute ERP latitude for each pixel in a cubemap crop.

    For each pixel, compute its 3D direction ray based on the cubemap face
    direction, yaw offset, and field of view, then extract the latitude as
    ``arcsin(y)`` of the world-frame direction vector.

    Matches the rotation convention used in
    ``stage02_cubemap/cubemap.py`` so that the latitudes are consistent
    with the crop extraction geometry.

    Args:
        crop_h: Height of the crop in pixels.
        crop_w: Width of the crop in pixels.
        face_name: Cubemap face — one of ``"front"``, ``"right"``,
            ``"back"``, ``"left"``, ``"top"``, ``"bottom"``.
        yaw_offset: Additional yaw rotation in degrees added to the
            face's base yaw (positive = look right).
        fov: Field of view of the crop in degrees.

    Returns:
        ``(crop_h, crop_w)`` float32 tensor of latitudes in radians.
        0 at equator, ±π/2 at poles.

    Raises:
        ValueError: If *face_name* is not recognised.
    """
    if face_name not in _FACE_YAW_PITCH:
        raise ValueError(
            f"Unknown face name '{face_name}'. "
            f"Expected one of: {list(_FACE_YAW_PITCH.keys())}"
        )

    base_yaw, base_pitch = _FACE_YAW_PITCH[face_name]
    combined_yaw = base_yaw + yaw_offset

    # World→cam rotation; cam→world = R^T
    R = _make_rotation_matrix(combined_yaw, base_pitch)
    R_c2w = R.T  # (3, 3) float64

    # Pinhole camera intrinsics from fov
    focal = crop_w / (2.0 * math.tan(math.radians(fov) / 2.0))
    cx = crop_w / 2.0
    cy = crop_h / 2.0

    # Pixel coordinate grid (pixel centres)
    u = torch.arange(crop_w, dtype=torch.float64) + 0.5
    v = torch.arange(crop_h, dtype=torch.float64) + 0.5
    uu, vv = torch.meshgrid(u, v, indexing="xy")  # (crop_h, crop_w)

    # Direction vectors in camera frame: [(u-cx)/f, (v-cy)/f, 1]
    dx = (uu - cx) / focal
    dy = (vv - cy) / focal
    dz = torch.ones_like(dx)

    # Normalise to unit vectors
    norms = torch.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
    dx = dx / norms
    dy = dy / norms
    dz = dz / norms

    # Stack into (crop_h, crop_w, 3) and rotate to world frame
    dirs_cam = torch.stack([dx, dy, dz], dim=-1)
    dirs_world = torch.einsum("ij,...j->...i", R_c2w, dirs_cam)  # (H, W, 3)

    # Latitude = arcsin(y_component), clamped for numerical safety
    latitudes = torch.arcsin(dirs_world[..., 1].clamp(-1.0, 1.0))  # (H, W)

    logger.debug(
        "compute_latitudes_from_crops: face='%s', yaw_offset=%.1f, fov=%.1f, "
        "lat range=[%.4f, %.4f] rad",
        face_name,
        yaw_offset,
        fov,
        latitudes.min().item(),
        latitudes.max().item(),
    )

    return latitudes.float()


# ---------------------------------------------------------------------------
# T6.2 — ErpGS scale-flattening loss
# ---------------------------------------------------------------------------


def scale_flattening_loss(
    scales: torch.Tensor,
    positions: torch.Tensor,
    latitudes: torch.Tensor,
    max_scale_factor: float = 10.0,
) -> torch.Tensor:
    """Compute ErpGS scale-flattening regularisation loss.

    Penalises Gaussians whose maximum scale exceeds a latitude-dependent
    threshold.  At higher latitudes the threshold is tighter because
    Gaussians tend to appear oversized in ERP space due to polar
    area distortion.

    The threshold is::

        threshold = max_scale_factor * (1.0 - 0.5 * |sin(latitude)|)

    The loss is ``mean(ReLU(max_scale - threshold))`` over all Gaussians.

    Args:
        scales: Gaussian scale parameters, shape ``(N, 3)``.
        positions: Gaussian centre positions, shape ``(N, 3)``.
            (Kept for API consistency; not used in the computation.)
        latitudes: Latitude of each Gaussian in radians, shape ``(N,)``.
            0 at equator, ±π/2 at poles.
        max_scale_factor: Base maximum scale factor (default 10.0).

    Returns:
        Scalar loss tensor (differentiable w.r.t. *scales*).

    Raises:
        ValueError: If shapes are incompatible.
    """
    if scales.shape[0] != latitudes.shape[0]:
        raise ValueError(
            f"Incompatible shapes: scales has {scales.shape[0]} rows, "
            f"latitudes has {latitudes.shape[0]}"
        )

    # Max scale per Gaussian
    max_scale = scales.max(dim=1).values  # (N,)

    # Latitude-dependent threshold: tighter at high latitude
    threshold = max_scale_factor * (1.0 - 0.5 * torch.sin(latitudes).abs())

    # Penalise excess above threshold
    excess = torch.relu(max_scale - threshold)
    loss = excess.mean()

    logger.debug(
        "scale_flattening_loss: max_scale range=[%.4f, %.4f], "
        "threshold range=[%.4f, %.4f], loss=%.6f",
        max_scale.min().item(),
        max_scale.max().item(),
        threshold.min().item(),
        threshold.max().item(),
        loss.item(),
    )

    return loss
