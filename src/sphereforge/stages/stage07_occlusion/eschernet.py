"""EscherNet model wrapper for multi-view diffusion inpainting.

DEPRECATED: This standalone wrapper has been superseded by the unified
inpainting module at ``sphereforge.stages.stage07_occlusion.inpainting``.

Use one of these instead:

    # Recommended: Stable Diffusion inpainting (easy to install)
    from sphereforge.stages.stage07_occlusion.inpainting import SDInpainter
    inpainter = SDInpainter()

    # Optional: EscherNet multi-view diffusion (better view consistency)
    from sphereforge.stages.stage07_occlusion.inpainting import EscherNetInpainter
    inpainter = EscherNetInpainter()

    # Factory function
    from sphereforge.stages.stage07_occlusion.inpainting import create_inpainter
    inpainter = create_inpainter("sd")  # or "eschernet"

This file is kept for backward compatibility.
"""

from __future__ import annotations

import logging

import numpy as np

from sphereforge.common.model_cache import DEFAULT_CACHE_DIR

logger = logging.getLogger("sphereforge.stage07.eschernet")


class EscherNetWrapper:
    """EscherNet multi-view diffusion model wrapper.

    DEPRECATED: Use ``EscherNetInpainter`` from
    ``sphereforge.stages.stage07_occlusion.inpainting`` instead.

    This class is kept for backward compatibility and delegates to the
    new ``EscherNetInpainter`` implementation.
    """

    def __init__(self, cache_dir=None) -> None:
        from sphereforge.stages.stage07_occlusion.inpainting import EscherNetInpainter
        self._impl = EscherNetInpainter(cache_dir=cache_dir)

    def inpaint_holes(
        self,
        rendered_image: np.ndarray,
        hole_mask: np.ndarray,
        reference_images: list[np.ndarray] | None = None,
    ) -> np.ndarray:
        """Inpaint holes using EscherNet multi-view diffusion.

        Args:
            rendered_image: Rendered image (H, W, 3) uint8.
            hole_mask: Binary mask (H, W) where True = hole.
            reference_images: Optional reference views for conditioning.

        Returns:
            Inpainted image (H, W, 3) uint8.
        """
        return self._impl.inpaint_holes(
            rendered_image=rendered_image,
            hole_mask=hole_mask,
            reference_images=reference_images,
        )
