"""Helpers for Gaussian parameter encodings used across stages.

SphereForge stores Gaussian opacities and scales in two slightly different
representations depending on the stage:

- Stage 5 commonly writes activated values directly to PLY.
- Stage 6 optimization works in raw parameter space and writes logit opacities
  and log-scales to PLY checkpoints / outputs.

These helpers make later stages robust to either representation.
"""

from __future__ import annotations

import numpy as np


def opacities_to_activated(opacities: np.ndarray) -> np.ndarray:
    """Convert Gaussian opacities to the activated [0, 1] domain.

    Args:
        opacities: Opacity array in either activated form or raw logit form.

    Returns:
        Array with the same shape containing activated opacities.
    """
    opacities = np.asarray(opacities, dtype=np.float32)
    if opacities.size == 0:
        return opacities.copy()
    if np.all((opacities >= 0.0) & (opacities <= 1.0)):
        return np.clip(opacities, 0.0, 1.0)
    clipped = np.clip(opacities, -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def scales_to_activated(scales: np.ndarray) -> np.ndarray:
    """Convert Gaussian scales to positive activated values.

    Args:
        scales: Scale array in either activated form or raw log-scale form.

    Returns:
        Array with the same shape containing positive scales.
    """
    scales = np.asarray(scales, dtype=np.float32)
    if scales.size == 0:
        return scales.copy()
    if np.any(scales <= 0.0):
        return np.exp(np.clip(scales, -20.0, 20.0))
    return np.maximum(scales, 1e-12)


def attenuate_opacities(opacities: np.ndarray, factor: float) -> np.ndarray:
    """Reduce opacities while preserving the input encoding.

    Args:
        opacities: Opacity array in activated or raw-logit form.
        factor: Multiplicative attenuation factor in activated space.

    Returns:
        Array with the same shape and encoding as the input.
    """
    if factor <= 0.0:
        raise ValueError(f"factor must be positive, got {factor}")

    opacities = np.asarray(opacities, dtype=np.float32)
    if opacities.size == 0:
        return opacities.copy()
    if np.all((opacities >= 0.0) & (opacities <= 1.0)):
        return np.clip(opacities * factor, 0.0, 1.0)

    activated = np.clip(opacities_to_activated(opacities) * factor, 1e-6, 1.0 - 1e-6)
    return np.log(activated / (1.0 - activated))


def inflate_scales(scales: np.ndarray, factor: float) -> np.ndarray:
    """Increase Gaussian scales while preserving the input encoding.

    Args:
        scales: Scale array in activated or raw-log-scale form.
        factor: Multiplicative inflation factor in activated space.

    Returns:
        Array with the same shape and encoding as the input.
    """
    if factor <= 0.0:
        raise ValueError(f"factor must be positive, got {factor}")

    scales = np.asarray(scales, dtype=np.float32)
    if scales.size == 0:
        return scales.copy()
    if np.any(scales <= 0.0):
        return scales + np.log(factor)
    return scales * factor
