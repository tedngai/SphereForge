"""360-GeoGS D-Normal regularisation loss.

Implements the D-Normal loss from the 360-GeoGS paper (arXiv:2601.02102).
This loss penalises disagreement between the surface normal derived from
rendered depth and an optional external surface-normal prior.  When no
external normals are provided, the depth-derived normal is compared against
the local planarity assumption — encouraging smooth, planar surfaces in the
reconstruction.
"""

from __future__ import annotations

import logging

import torch
import torch.nn.functional as F

logger = logging.getLogger("sphereforge.stage06.d_normal_loss")


# ---------------------------------------------------------------------------
# T6.5 helper — compute surface normals from depth
# ---------------------------------------------------------------------------


def compute_normals_from_depth(
    depth: torch.Tensor,
    fx: float = 1.0,
    fy: float = 1.0,
) -> torch.Tensor:
    """Compute surface normals from a depth map using finite differences.

    For each pixel (u, v), the 3-D point in camera space is::

        X = (u - cx) * depth / fx
        Y = (v - cy) * depth / fy
        Z = depth

    where ``cx = width / 2`` and ``cy = height / 2`` are assumed to be
    at the image centre.  The tangent vectors along u and v are computed
    with central differences and the normal is their cross product.

    Border pixels (where the 3x3 stencil crosses the image edge) are
    filled by replicating the nearest valid normal.

    Args:
        depth: Depth map, shape ``(H, W)``, positive values.
        fx: Horizontal focal length in pixels (default 1.0).
        fy: Vertical focal length in pixels (default 1.0).

    Returns:
        Normal map, shape ``(H, W, 3)``.  Each normal is a unit-length
        vector in camera space.  Convention: normals point **towards**
        the camera (positive Z component).
    """
    H, W = depth.shape
    device = depth.device
    dtype = depth.dtype

    cx = W / 2.0
    cy = H / 2.0

    # Pixel coordinate grids
    u = torch.arange(W, device=device, dtype=dtype)  # (W,)
    v = torch.arange(H, device=device, dtype=dtype)  # (H,)
    uu, vv = torch.meshgrid(u, v, indexing="xy")  # (H, W)

    # 3-D point at each pixel: (X, Y, Z)
    # X = (u - cx) / fx * depth
    # Y = (v - cy) / fy * depth
    # Z = depth
    pts_x = (uu - cx) / fx * depth  # (H, W)
    pts_y = (vv - cy) / fy * depth  # (H, W)
    pts_z = depth  # (H, W)

    # Central finite differences with padding (replicate border)
    # dx = d(pts) / du, dy = d(pts) / dv
    pts_x_pad = F.pad(pts_x.unsqueeze(0), (1, 1, 1, 1), mode="replicate").squeeze(0)
    pts_y_pad = F.pad(pts_y.unsqueeze(0), (1, 1, 1, 1), mode="replicate").squeeze(0)
    pts_z_pad = F.pad(pts_z.unsqueeze(0), (1, 1, 1, 1), mode="replicate").squeeze(0)

    # Tangent along u (horizontal): pts[u+1, v] - pts[u-1, v]
    dx_x = pts_x_pad[1:-1, 2:] - pts_x_pad[1:-1, :-2]  # (H, W)
    dx_y = pts_y_pad[1:-1, 2:] - pts_y_pad[1:-1, :-2]
    dx_z = pts_z_pad[1:-1, 2:] - pts_z_pad[1:-1, :-2]

    # Tangent along v (vertical): pts[u, v+1] - pts[u, v-1]
    dy_x = pts_x_pad[2:, 1:-1] - pts_x_pad[:-2, 1:-1]  # (H, W)
    dy_y = pts_y_pad[2:, 1:-1] - pts_y_pad[:-2, 1:-1]
    dy_z = pts_z_pad[2:, 1:-1] - pts_z_pad[:-2, 1:-1]

    # Normal = cross(dx, dy)
    # nx = dy_y * dx_z - dy_z * dx_y
    # ny = dy_z * dx_x - dy_x * dx_z
    # nz = dy_x * dx_y - dy_y * dx_x
    nx = dx_z * dy_y - dx_y * dy_z
    ny = dx_x * dy_z - dx_z * dy_x
    nz = dx_y * dy_x - dx_x * dy_y

    # Ensure normals point towards the camera (positive Z in camera space)
    # If nz < 0, flip the normal
    flip = (nz < 0).float()
    nx = nx * (1.0 - 2.0 * flip)
    ny = ny * (1.0 - 2.0 * flip)
    nz = nz * (1.0 - 2.0 * flip)

    # Normalise
    normal = torch.stack([nx, ny, nz], dim=-1)  # (H, W, 3)
    norm = normal.norm(dim=-1, keepdim=True).clamp(min=1e-8)
    normal = normal / norm

    logger.debug(
        "compute_normals_from_depth: shape=(%d, %d), "
        "normal Z range=[%.4f, %.4f]",
        H,
        W,
        normal[..., 2].min().item(),
        normal[..., 2].max().item(),
    )

    return normal


# ---------------------------------------------------------------------------
# T6.5 — D-Normal loss
# ---------------------------------------------------------------------------


def d_normal_loss(
    rendered_depth: torch.Tensor,
    surface_normals: torch.Tensor | None = None,
    depth_weight: float = 0.05,
) -> torch.Tensor:
    """Compute the 360-GeoGS D-Normal regularisation loss.

    The D-Normal loss penalises disagreement between the normal derived
    from the rendered depth gradient and an external surface-normal
    prior.  When *surface_normals* is ``None``, the depth-derived normal
    is compared to itself in a smoothness sense (the loss reduces to
    encouraging locally planar geometry).

    For each pixel ``(u, v)``, the depth-derived normal is::

        n_depth = normalise(cross(dx, dy))

    where ``dx`` and ``dy`` are tangent vectors computed from the depth
    map via finite differences.  The loss per pixel is::

        loss_pixel = 1 - dot(n_depth, n_surface)

    and the total loss is the mean over all valid pixels, multiplied by
    *depth_weight*.

    Args:
        rendered_depth: Rendered depth map, shape ``(H, W)``, positive
            values.  Must be differentiable w.r.t. the Gaussian parameters
            that produced it.
        surface_normals: Optional external normal map, shape ``(H, W, 3)``.
            Each vector should be unit length.  If ``None``, a smoothness
            loss is computed instead (see note above).
        depth_weight: Scalar weight applied to the loss (default 0.05).

    Returns:
        Scalar loss tensor (differentiable w.r.t. *rendered_depth*).

    Raises:
        ValueError: If *surface_normals* has an incompatible shape.
    """
    # Compute normals from rendered depth
    n_depth = compute_normals_from_depth(rendered_depth)  # (H, W, 3)

    if surface_normals is None:
        # Smoothness loss: encourage neighbouring normals to be similar
        # This is equivalent to penalising the normal variation across
        # the image.  Use total variation on the normal map.
        # Loss = mean(1 - dot(n_{u,v}, n_{u+1,v})) + mean(1 - dot(n_{u,v}, n_{u,v+1}))
        n_right = n_depth[:, 1:, :]  # (H, W-1, 3)
        n_left = n_depth[:, :-1, :]
        n_up = n_depth[1:, :, :]  # (H-1, W, 3)
        n_down = n_depth[:-1, :, :]

        cos_h = (n_right * n_left).sum(dim=-1).clamp(-1.0, 1.0)  # (H, W-1)
        cos_v = (n_up * n_down).sum(dim=-1).clamp(-1.0, 1.0)  # (H-1, W)

        loss = (1.0 - cos_h).mean() + (1.0 - cos_v).mean()
        loss = depth_weight * loss

        logger.debug("d_normal_loss (smoothness): %.6f", loss.item())
        return loss

    # Validate shape
    if surface_normals.shape[:2] != rendered_depth.shape:
        raise ValueError(
            f"Shape mismatch: surface_normals {surface_normals.shape[:2]} "
            f"vs rendered_depth {rendered_depth.shape}"
        )
    if surface_normals.shape[2] != 3:
        raise ValueError(
            f"surface_normals must have 3 channels, got {surface_normals.shape[2]}"
        )

    # Normalise surface normals (they should already be unit, but be safe)
    n_surf = F.normalize(surface_normals, dim=-1)  # (H, W, 3)

    # Per-pixel loss: 1 - cos(angle) = 1 - dot(n_depth, n_surface)
    cos_angle = (n_depth * n_surf).sum(dim=-1).clamp(-1.0, 1.0)  # (H, W)

    # Mask invalid pixels (where depth is zero or very small)
    valid_mask = rendered_depth > 1e-6  # (H, W)

    # Only compute loss on valid pixels
    if valid_mask.any():
        per_pixel_loss = (1.0 - cos_angle) * valid_mask.float()
        loss = depth_weight * per_pixel_loss.sum() / valid_mask.float().sum().clamp(
            min=1.0
        )
    else:
        # No valid pixels — return zero loss
        loss = depth_weight * (1.0 - cos_angle).mean() * 0.0

    logger.debug("d_normal_loss: %.6f", loss.item())

    return loss
