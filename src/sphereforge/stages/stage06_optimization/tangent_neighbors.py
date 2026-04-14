"""ErpGS omnidirectional tangent-plane neighbour selection.

Implements the tangent-plane proximity neighbour search described in the
ErpGS paper (arXiv:2505.19883).  Instead of using Euclidean distance in 3D
space, each Gaussian's neighbours are found by projecting candidate points
onto the tangent plane at that Gaussian and selecting the *k* closest
in the 2D projection.  This correctly handles the spherical geometry of
360° scenes where Euclidean proximity is a poor proxy for surface
adjacency, especially near the poles of the equirectangular projection.
"""

from __future__ import annotations

import logging

import torch

logger = logging.getLogger("sphereforge.stage06.tangent_neighbors")


# ---------------------------------------------------------------------------
# Helper — project points onto a tangent plane
# ---------------------------------------------------------------------------


def project_to_tangent_plane(
    points: torch.Tensor,
    origin: torch.Tensor,
    normal: torch.Tensor,
) -> torch.Tensor:
    """Project 3-D points onto the tangent plane at *origin* with *normal*.

    The tangent plane is defined by the point *origin* and the unit normal
    *normal*.  For each point *p*, the projection is::

        p_proj = p - dot(p - origin, normal) * normal

    The result is then expressed in a local 2-D orthonormal basis
    ``(u_axis, v_axis)`` on the tangent plane so that the output has
    shape ``(N, 2)``.

    Args:
        points: 3-D points to project, shape ``(N, 3)``.
        origin: Centre of the tangent plane, shape ``(3,)``.
        normal: Unit normal of the tangent plane, shape ``(3,)``.

    Returns:
        2-D projected coordinates, shape ``(N, 2)``.
    """
    # Ensure normal is unit length
    normal = normal / (normal.norm() + 1e-8)

    # Project onto the plane
    diff = points - origin  # (N, 3)
    dist_to_plane = (diff * normal).sum(dim=-1, keepdim=True)  # (N, 1)
    projected_3d = diff - dist_to_plane * normal  # (N, 3)

    # Build an orthonormal basis on the tangent plane
    # Choose an arbitrary vector not parallel to normal
    arbitrary = torch.tensor([1.0, 0.0, 0.0], device=normal.device, dtype=normal.dtype)
    if torch.abs(torch.dot(normal, arbitrary)) > 0.9:
        arbitrary = torch.tensor([0.0, 1.0, 0.0], device=normal.device, dtype=normal.dtype)

    u_axis = arbitrary - torch.dot(arbitrary, normal) * normal
    u_axis = u_axis / (u_axis.norm() + 1e-8)
    v_axis = torch.cross(normal, u_axis)
    v_axis = v_axis / (v_axis.norm() + 1e-8)

    # Express projected points in the 2-D basis
    u_coords = (projected_3d * u_axis).sum(dim=-1)  # (N,)
    v_coords = (projected_3d * v_axis).sum(dim=-1)  # (N,)

    return torch.stack([u_coords, v_coords], dim=-1)  # (N, 2)


# ---------------------------------------------------------------------------
# T6.3 — Tangent-plane neighbour selection
# ---------------------------------------------------------------------------


def tangent_plane_neighbors(
    positions: torch.Tensor,
    k: int = 16,
    surface_normals: torch.Tensor | None = None,
) -> torch.Tensor:
    """Find *k* nearest neighbours using tangent-plane proximity.

    For each Gaussian *p_i*, all other Gaussians are projected onto *p_i*'s
    tangent plane (defined by its surface normal, or the radial direction
    from the origin if no normal is given).  The *k* closest projections
    in 2-D are returned as neighbours.

    When *surface_normals* is ``None``, the normal at each point is taken
    as the unit vector from the scene origin ``(0, 0, 0)`` to the point,
    which is appropriate for scenes captured from a single viewpoint at the
    origin (the standard 360° capture setup).

    The implementation is fully vectorised and runs on GPU when the inputs
    are on a CUDA device.

    Args:
        positions: Gaussian centre positions, shape ``(N, 3)``.
        k: Number of neighbours to return per point (default 16).
        surface_normals: Optional per-point surface normals, shape ``(N, 3)``.
            If ``None``, normals are derived from the radial direction
            ``(position / ||position||)``.

    Returns:
        Neighbour indices, shape ``(N, k)``.  Each row ``i`` contains the
        indices of the *k* closest tangent-plane neighbours of point *i*,
        **excluding** point *i* itself.

    Raises:
        ValueError: If *k* is larger than ``N - 1``.
    """
    N = positions.shape[0]
    device = positions.device
    dtype = positions.dtype

    if k >= N:
        raise ValueError(
            f"k ({k}) must be less than the number of points ({N})"
        )

    # Derive normals from radial direction if not provided
    if surface_normals is None:
        normals = positions / (positions.norm(dim=1, keepdim=True) + 1e-8)
    else:
        normals = surface_normals / (surface_normals.norm(dim=1, keepdim=True) + 1e-8)

    # Build orthonormal tangent-plane bases for every point ---------------
    # For each point i, build u_axis_i and v_axis_i on its tangent plane.
    # We choose a global "arbitrary" direction and use Gram-Schmidt.
    arbitrary = torch.tensor([1.0, 0.0, 0.0], device=device, dtype=dtype)
    # Handle the degenerate case where normal ≈ arbitrary
    dot_with_arb = (normals * arbitrary).sum(dim=-1)  # (N,)
    needs_alt = dot_with_arb.abs() > 0.9
    # For those points, use (0, 1, 0) instead
    arb = arbitrary.unsqueeze(0).expand(N, -1)  # (N, 3)
    alt = torch.tensor([0.0, 1.0, 0.0], device=device, dtype=dtype)
    arb = torch.where(needs_alt.unsqueeze(-1), alt.unsqueeze(0).expand(N, -1), arb)

    # u_axis = (arb - dot(arb, n) * n), normalised
    proj_len = (arb * normals).sum(dim=-1, keepdim=True)  # (N, 1)
    u_axes = arb - proj_len * normals  # (N, 3)
    u_axes = u_axes / (u_axes.norm(dim=1, keepdim=True) + 1e-8)

    # v_axis = cross(normal, u_axis)
    v_axes = torch.cross(normals, u_axes, dim=-1)  # (N, 3)
    v_axes = v_axes / (v_axes.norm(dim=1, keepdim=True) + 1e-8)

    # Project all points onto each tangent plane --------------------------------
    # For point i, project all OTHER points j onto i's tangent plane.
    # diff_ij = positions[j] - positions[i]
    # projected_ij = diff_ij - dot(diff_ij, normal_i) * normal_i
    # Then: u_coord = dot(projected_ij, u_axis_i)
    #        v_coord = dot(projected_ij, v_axis_i)

    # Vectorised over all (i, j) pairs:
    # diff: (N, N, 3) where diff[i, j] = positions[j] - positions[i]
    diff = positions.unsqueeze(0) - positions.unsqueeze(1)  # (N, N, 3)

    # Project out the normal component for each row i
    # dot(diff[i,j], normal[i]) for all j
    dot_n = (diff * normals.unsqueeze(1)).sum(dim=-1, keepdim=True)  # (N, N, 1)
    projected = diff - dot_n * normals.unsqueeze(1)  # (N, N, 3)

    # 2-D coordinates in each tangent plane
    u_coords = (projected * u_axes.unsqueeze(1)).sum(dim=-1)  # (N, N)
    v_coords = (projected * v_axes.unsqueeze(1)).sum(dim=-1)  # (N, N)
    dist_2d_sq = u_coords ** 2 + v_coords ** 2  # (N, N)

    # Zero out self-distance (set to inf so self is never selected)
    diag_mask = torch.eye(N, device=device, dtype=dtype).bool()
    dist_2d_sq = dist_2d_sq.masked_fill(diag_mask, float("inf"))

    # Select k nearest neighbours for each point
    _, neighbor_indices = dist_2d_sq.topk(k, dim=1, largest=False)  # (N, k)

    logger.debug(
        "tangent_plane_neighbors: found %d neighbors for %d points", k, N
    )

    return neighbor_indices