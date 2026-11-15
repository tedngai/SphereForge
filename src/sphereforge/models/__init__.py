"""Model wrappers used by SphereForge stages.

Each wrapper exposes a small, uniform interface so that stages never depend on
a specific upstream repository:

- Depth estimators implement ``estimate_depth(image) -> np.ndarray`` and
  ``estimate_depth_batch(images) -> list[np.ndarray]`` for ``(H, W, 3)`` uint8
  inputs, returning float32 depth maps with the same spatial shape.
- All wrappers resolve weights through :mod:`sphereforge.common.model_cache`
  (or HuggingFace's own cache) and download on first use.
"""

from __future__ import annotations

from sphereforge.models.depth_anything_v2 import DepthAnythingV2Model

__all__ = ["DepthAnythingV2Model"]
