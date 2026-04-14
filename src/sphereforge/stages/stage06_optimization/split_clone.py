"""ImprovedGS+ Long-Axis Split (LAS) and cloning logic.

Implements the Long-Axis Split strategy from the ImprovedGS+ paper for
densifying large Gaussians.  Instead of splitting Gaussians along a random
or uniformly-sampled direction, LAS identifies the principal (longest) axis
of each Gaussian's ellipsoid and splits along that axis, placing two child
Gaussians at ``position ± 0.5 * scale_long * direction`` with half the
parent's scale on the long axis.  This preserves the anisotropic shape
that is common in 360° scenes (e.g. thin wall Gaussians) while still
increasing detail.

Also provides a ``clone_under_reconstructed`` helper for small Gaussians
in under-reconstructed regions.
"""

from __future__ import annotations

import logging

import torch

from sphereforge.stages.stage06_optimization.intersection_depth import (
    quaternion_to_rotation_matrix,
)

logger = logging.getLogger("sphereforge.stage06.split_clone")

# ---------------------------------------------------------------------------
# T6.7 — Long-Axis Split
# ---------------------------------------------------------------------------


def long_axis_split(
    positions: torch.Tensor,
    scales: torch.Tensor,
    rotations: torch.Tensor,
    opacities: torch.Tensor,
    mask: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Split masked Gaussians along their longest scale axis.

    For each Gaussian where *mask* is ``True``, the function:

    1. Finds the longest scale axis (``argmax`` of ``(s_x, s_y, s_z)``).
    2. Computes the split direction in world space by rotating the unit
       vector along that axis by the Gaussian's rotation quaternion.
    3. Creates two child Gaussians at
       ``position ± 0.5 * scale_long_axis * direction``.
    4. Each child inherits the parent's rotation and opacity.  The child's
       scale is the parent's scale with the long axis multiplied by 0.5.
    5. Removes the parent Gaussian from the output.

    The operation is differentiable w.r.t. *positions*, *scales*, and
    *rotations* so that gradient flow is preserved for downstream losses.

    Args:
        positions: Gaussian means, shape ``(N, 3)``.
        scales: Gaussian scales (standard deviations along each local axis),
            shape ``(N, 3)``.  Must be positive.
        rotations: Gaussian rotation quaternions ``(qw, qx, qy, qz)``,
            shape ``(N, 4)``.  Need not be unit-normalised — the function
            normalises internally.
        opacities: Gaussian opacities (activation inputs or raw values),
            shape ``(N,)``.
        mask: Boolean mask of Gaussians to split, shape ``(N,)``.

    Returns:
        Tuple ``(positions, scales, rotations, opacities)`` with the split
        Gaussians replacing their parents.  The total count changes from
        ``N`` to ``N - num_split + 2 * num_split = N + num_split``.
    """
    N = positions.shape[0]
    device = positions.device
    dtype = positions.dtype

    num_split = mask.sum().item()

    if num_split == 0:
        logger.debug("long_axis_split: no Gaussians to split")
        return positions, scales, rotations, opacities

    logger.debug("long_axis_split: splitting %d / %d Gaussians", num_split, N)

    # Indices of Gaussians to keep (mask == False)
    keep_mask = ~mask
    keep_indices = keep_mask.nonzero(as_tuple=True)[0]

    # Indices of Gaussians to split (mask == True)
    split_indices = mask.nonzero(as_tuple=True)[0]

    # --- Extract split Gaussians ---
    pos_split = positions[split_indices]  # (K, 3)
    scale_split = scales[split_indices]  # (K, 3)
    rot_split = rotations[split_indices]  # (K, 4)
    op_split = opacities[split_indices]  # (K,)

    K = pos_split.shape[0]

    # --- Step 1: Find the longest axis for each split Gaussian ---
    long_axis_idx = scale_split.argmax(dim=1)  # (K,) in {0, 1, 2}

    # Create unit vectors along each axis
    # e_i for axis i
    axis_vectors = torch.zeros(K, 3, device=device, dtype=dtype)
    axis_vectors.scatter_(1, long_axis_idx.unsqueeze(1), 1.0)  # (K, 3)

    # --- Step 2: Rotate axis vectors into world space ---
    # Build rotation matrices from quaternions
    qw = rot_split[:, 0]
    qx = rot_split[:, 1]
    qy = rot_split[:, 2]
    qz = rot_split[:, 3]
    R = quaternion_to_rotation_matrix(qw, qx, qy, qz)  # (K, 3, 3)

    # Direction in world space: R @ axis_vector
    # axis_vectors: (K, 3), R: (K, 3, 3)
    # We want R[i] @ axis_vectors[i] for each i
    directions = torch.einsum("kij,kj->ki", R, axis_vectors)  # (K, 3)

    # --- Step 3: Compute offset along the long axis ---
    # Scale along the long axis
    scale_long = scale_split.gather(1, long_axis_idx.unsqueeze(1)).squeeze(1)  # (K,)

    offset = 0.5 * scale_long.unsqueeze(1) * directions  # (K, 3)

    # --- Step 4: Create two children ---
    pos_child1 = pos_split + offset  # (K, 3)
    pos_child2 = pos_split - offset  # (K, 3)

    # Scale: parent scale * 0.5 on the long axis, unchanged on other axes
    scale_factor = torch.ones_like(scale_split)  # (K, 3)
    scale_factor.scatter_(1, long_axis_idx.unsqueeze(1), 0.5)
    scale_child1 = scale_split * scale_factor  # (K, 3)
    scale_child2 = scale_split * scale_factor  # (K, 3) — same as child1

    # Rotation: inherited from parent
    rot_child1 = rot_split.clone()
    rot_child2 = rot_split.clone()

    # Opacity: inherited from parent
    op_child1 = op_split.clone()
    op_child2 = op_split.clone()

    # --- Step 5: Assemble output ---
    # Kept Gaussians + child1 + child2
    if keep_indices.shape[0] > 0:
        new_positions = torch.cat(
            [positions[keep_indices], pos_child1, pos_child2], dim=0
        )
        new_scales = torch.cat(
            [scales[keep_indices], scale_child1, scale_child2], dim=0
        )
        new_rotations = torch.cat(
            [rotations[keep_indices], rot_child1, rot_child2], dim=0
        )
        new_opacities = torch.cat(
            [opacities[keep_indices], op_child1, op_child2], dim=0
        )
    else:
        new_positions = torch.cat([pos_child1, pos_child2], dim=0)
        new_scales = torch.cat([scale_child1, scale_child2], dim=0)
        new_rotations = torch.cat([rot_child1, rot_child2], dim=0)
        new_opacities = torch.cat([op_child1, op_child2], dim=0)

    logger.debug(
        "long_axis_split: N=%d → N'=%d (split %d, kept %d)",
        N,
        new_positions.shape[0],
        num_split,
        keep_indices.shape[0],
    )

    return new_positions, new_scales, new_rotations, new_opacities


def clone_under_reconstructed(
    positions: torch.Tensor,
    opacities: torch.Tensor,
    mask: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Clone masked Gaussians (small ones in under-reconstructed regions).

    Cloning duplicates a Gaussian at its current position but with half
    the opacity.  This is the standard 3DGS cloning strategy for small
    Gaussians that lie in under-reconstructed regions (as identified by
    the EAS or gradient trigger).

    Args:
        positions: Gaussian means, shape ``(N, 3)``.
        opacities: Gaussian opacities, shape ``(N,)``.
        mask: Boolean mask of Gaussians to clone, shape ``(N,)``.

    Returns:
        Tuple ``(positions, opacities)`` with cloned Gaussians appended.
        The total count changes from ``N`` to ``N + num_cloned``.
    """
    num_clone = mask.sum().item()
    N = positions.shape[0]

    if num_clone == 0:
        logger.debug("clone_under_reconstructed: no Gaussians to clone")
        return positions, opacities

    clone_indices = mask.nonzero(as_tuple=True)[0]

    # Clone positions: same as parent
    pos_clone = positions[clone_indices]  # (K, 3)

    # Clone opacity: half of parent
    op_clone = opacities[clone_indices] * 0.5  # (K,)

    # Reduce parent opacity by half as well (standard 3DGS convention)
    # This ensures total "mass" is conserved
    new_opacities = opacities.clone()
    new_opacities[clone_indices] = opacities[clone_indices] * 0.5

    new_positions = torch.cat([positions, pos_clone], dim=0)
    new_opacities = torch.cat([new_opacities, op_clone], dim=0)

    logger.debug(
        "clone_under_reconstructed: N=%d → N'=%d (cloned %d)",
        N,
        new_positions.shape[0],
        num_clone,
    )

    return new_positions, new_opacities