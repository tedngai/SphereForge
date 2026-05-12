"""ImprovedGS+ Recovery-Aware Pruning (RAP).

Implements the Recovery-Aware Pruning strategy from the ImprovedGS+ paper.
RAP addresses a common failure mode in 3DGS optimisation: aggressive pruning
of Gaussians can cause a sudden PSNR drop, especially in thin structures
or specular regions.  RAP stores pruned Gaussians in a buffer and recovers
them if the PSNR drops by more than a configurable threshold after a
pruning round.

This module provides:

- ``PruningBuffer``: Stores pruned Gaussians for potential recovery.
- ``rap_prune``: Prunes near-transparent and excessively large Gaussians,
  returning both the kept subset and a mask indicating which Gaussians
  were retained.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import NamedTuple

import torch

logger = logging.getLogger("sphereforge.stage06.pruning")

# ---------------------------------------------------------------------------
# Data class for a single pruning batch
# ---------------------------------------------------------------------------


class _PrunedBatch(NamedTuple):
    """A batch of Gaussians pruned at a given optimisation step."""

    positions: torch.Tensor
    scales: torch.Tensor
    rotations: torch.Tensor
    opacities: torch.Tensor
    sh_coeffs: torch.Tensor
    step: int


# ---------------------------------------------------------------------------
# T6.8 — PruningBuffer
# ---------------------------------------------------------------------------


class PruningBuffer:
    """Buffer that stores pruned Gaussians for potential recovery.

    After each pruning round, the pruned Gaussians are stored alongside
    the optimisation step number.  If the PSNR drops by more than a
    threshold after pruning, the most recent batch can be recovered.
    Old batches are automatically evicted once they exceed
    *max_recovery_steps*.

    Example usage::

        buf = PruningBuffer(max_recovery_steps=5)
        # ... pruning round at step 100 ...
        buf.store(positions, scales, rotations, opacities, sh, step=100)
        # ... evaluate PSNR ...
        recovered = buf.recover_if_needed(psnr_now, psnr_before, threshold=0.1)
        if recovered is not None:
            pos, sc, rot, op, sh = recovered
            # merge back into scene
        buf.clear_old(current_step=101)

    Args:
        max_recovery_steps: Number of pruning rounds to keep in the buffer.
            Older batches are discarded by ``clear_old``.
    """

    def __init__(self, max_recovery_steps: int = 5) -> None:
        self.max_recovery_steps = max_recovery_steps
        self._batches: deque[_PrunedBatch] = deque()

    def store(
        self,
        positions: torch.Tensor,
        scales: torch.Tensor,
        rotations: torch.Tensor,
        opacities: torch.Tensor,
        sh_coeffs: torch.Tensor,
        step: int,
    ) -> None:
        """Store a batch of pruned Gaussians.

        All tensors are detached and cloned to avoid retaining the
        computation graph.

        Args:
            positions: Pruned Gaussian means, shape ``(K, 3)``.
            scales: Pruned Gaussian scales, shape ``(K, 3)``.
            rotations: Pruned Gaussian rotations ``(qw, qx, qy, qz)``,
                shape ``(K, 4)``.
            opacities: Pruned Gaussian opacities, shape ``(K,)``.
            sh_coeffs: Pruned Gaussian spherical-harmonic coefficients,
                shape ``(K, C)`` where ``C`` is the number of SH channels.
            step: Optimisation step at which pruning occurred.
        """
        batch = _PrunedBatch(
            positions=positions.detach().clone(),
            scales=scales.detach().clone(),
            rotations=rotations.detach().clone(),
            opacities=opacities.detach().clone(),
            sh_coeffs=sh_coeffs.detach().clone(),
            step=step,
        )
        self._batches.append(batch)

        logger.debug(
            "PruningBuffer.store: step=%d, K=%d, buffer_size=%d",
            step,
            positions.shape[0],
            len(self._batches),
        )

    def recover_if_needed(
        self,
        current_psnr: float,
        previous_psnr: float,
        threshold: float = 0.1,
    ) -> tuple[torch.Tensor, ...] | None:
        """Recover the most recent batch if PSNR dropped too much.

        If ``previous_psnr - current_psnr > threshold``, the most recent
        batch of pruned Gaussians is returned for re-insertion into the
        scene.  The batch is removed from the buffer.

        Args:
            current_psnr: PSNR after pruning.
            previous_psnr: PSNR before pruning.
            threshold: Maximum acceptable PSNR drop (in dB).  If the
                drop exceeds this, recovery is triggered.

        Returns:
            Tuple ``(positions, scales, rotations, opacities, sh_coeffs)``
            of the most recently pruned batch if recovery is needed,
            otherwise ``None``.
        """
        psnr_drop = previous_psnr - current_psnr

        if psnr_drop <= threshold:
            logger.debug(
                "recover_if_needed: PSNR drop=%.4f dB (threshold=%.4f), "
                "no recovery needed",
                psnr_drop,
                threshold,
            )
            return None

        if len(self._batches) == 0:
            logger.warning(
                "recover_if_needed: PSNR drop=%.4f dB exceeds threshold, "
                "but buffer is empty — cannot recover",
                psnr_drop,
            )
            return None

        batch = self._batches.pop()
        logger.info(
            "recover_if_needed: PSNR drop=%.4f dB exceeds threshold=%.4f, "
            "recovering %d Gaussians from step %d",
            psnr_drop,
            threshold,
            batch.positions.shape[0],
            batch.step,
        )

        return (
            batch.positions,
            batch.scales,
            batch.rotations,
            batch.opacities,
            batch.sh_coeffs,
        )

    def clear_old(self, current_step: int) -> None:
        """Remove batches older than *max_recovery_steps* from the buffer.

        Args:
            current_step: Current optimisation step.  Batches with
                ``step < current_step - max_recovery_steps`` are removed.
        """
        min_step = current_step - self.max_recovery_steps
        while self._batches and self._batches[0].step < min_step:
            old = self._batches.popleft()
            logger.debug(
                "clear_old: evicting batch from step %d (%d Gaussians)",
                old.step,
                old.positions.shape[0],
            )

    @property
    def num_batches(self) -> int:
        """Number of batches currently in the buffer."""
        return len(self._batches)


# ---------------------------------------------------------------------------
# T6.8 — Recovery-Aware Prune
# ---------------------------------------------------------------------------


def rap_prune(
    positions: torch.Tensor,
    scales: torch.Tensor,
    opacities: torch.Tensor,
    min_opacity: float = 0.005,
    max_scale_ratio: float = 10.0,
    scene_extent: float | None = None,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Prune near-transparent and excessively large Gaussians.

    Implements the core pruning criteria from ImprovedGS+:

    1. **Opacity pruning**: Remove Gaussians whose opacity is below
       *min_opacity*.  These contribute negligibly to rendering.
    2. **Scale pruning**: Remove Gaussians whose maximum scale exceeds
       ``scene_extent * max_scale_ratio``.  These are likely outlier
       Gaussians that cover an unreasonable fraction of the scene.

    Args:
        positions: Gaussian means, shape ``(N, 3)``.
        scales: Gaussian scales, shape ``(N, 3)``.  Must be positive.
        opacities: Gaussian opacities, shape ``(N,)``.  Values in [0, 1]
            (after sigmoid or similar activation).
        min_opacity: Minimum opacity threshold (default 0.005).  Gaussians
            with opacity below this are pruned.
        max_scale_ratio: Maximum ratio of a Gaussian's largest scale to
            ``scene_extent`` (default 10.0).  Gaussians exceeding this are
            pruned.
        scene_extent: Approximate scene radius or extent.  If ``None``,
            computed as the maximum distance from the centroid of all
            Gaussian positions.

    Returns:
        Tuple ``(positions, scales, opacities, keep_mask)`` of the kept
        Gaussians only.  ``keep_mask`` is a boolean tensor of shape
        ``(N,)`` indicating which input Gaussians were retained.
    """
    N = positions.shape[0]
    device = positions.device

    if N == 0:
        keep_mask = torch.zeros(0, dtype=torch.bool, device=device)
        return positions, scales, opacities, keep_mask

    # --- Opacity mask ---
    opacity_ok = opacities >= min_opacity  # (N,)

    # --- Scale mask ---
    max_scale_per_gaussian = scales.max(dim=1).values  # (N,)

    if scene_extent is None:
        # Compute scene extent as max distance from centroid
        centroid = positions.mean(dim=0)  # (3,)
        dists = (positions - centroid).norm(dim=1)  # (N,)
        scene_extent = dists.max().clamp(min=1e-6).item()
        logger.debug(
            "rap_prune: auto-computed scene_extent=%.4f", scene_extent
        )

    scale_ok = max_scale_per_gaussian <= (scene_extent * max_scale_ratio)  # (N,)

    # Combined keep mask
    keep_mask = opacity_ok & scale_ok  # (N,)

    # Extract kept Gaussians
    kept_positions = positions[keep_mask]
    kept_scales = scales[keep_mask]
    kept_opacities = opacities[keep_mask]

    n_pruned_opacity = (~opacity_ok).sum().item()
    n_pruned_scale = (~scale_ok).sum().item()
    n_pruned_total = (~keep_mask).sum().item()
    n_kept = keep_mask.sum().item()

    logger.info(
        "rap_prune: N=%d, kept=%d, pruned=%d "
        "(opacity=%d, scale=%d, overlap=%d)",
        N,
        n_kept,
        n_pruned_total,
        n_pruned_opacity,
        n_pruned_scale,
        n_pruned_opacity + n_pruned_scale - n_pruned_total,
    )

    return kept_positions, kept_scales, kept_opacities, keep_mask
