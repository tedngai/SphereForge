"""OmniRoam trajectory fill (optional, config-gated).

OmniRoam is an Adobe Research method that generates virtual camera
trajectories through a scene to fill unobserved regions. It requires
the Adobe Research License and significant GPU resources.

This module is a STUB — it raises ``NotImplementedError`` when called,
with instructions for users who have the required license and hardware.
"""

from __future__ import annotations

import logging

logger = logging.getLogger("sphereforge.stage07.omniroam")


def omniroam_fill(
    gaussians: dict,
    config: object,
    colmap_model: dict,
) -> dict:
    """Fill unobserved regions using OmniRoam virtual camera trajectories.

    STUB: This function is not yet implemented. OmniRoam requires:

    1. **Adobe Research License** — The OmniRoam method and its
       pre-trained trajectory planner are proprietary to Adobe
       Research. Contact Adobe Research for licensing terms.

    2. **20 GB+ VRAM** — The trajectory planner and diffusion model
       together require at least 20 GB of GPU memory (tested on
       NVIDIA A100 40 GB).

    3. **Pre-trained weights** — Available only through the Adobe
       Research License:
         - ``omniroam_planner.pt`` (~3 GB)
         - ``omniroam_diffusion.pt`` (~7 GB)
       Place them in ``~/.cache/sphereforge/models/omniroam/``.

    To enable OmniRoam in your config, set::

        stage07.refine_backend = "omniroam"

    Args:
        gaussians: Dictionary with Gaussian splat data.
        config: Stage 7 configuration object.
        colmap_model: COLMAP sparse model dict.

    Returns:
        Updated gaussians dict (currently raises NotImplementedError).

    Raises:
        NotImplementedError: Always — OmniRoam is not yet available
            under an open-source license.
    """
    raise NotImplementedError(
        "OmniRoam fill requires the Adobe Research License and 20 GB+ "
        "VRAM. See the module docstring in "
        "sphereforge/stages/stage07_occlusion/omniroam.py for details. "
        "To use the open-source pipeline, set "
        "config.refine_backend='sharegs_gsdiff' instead."
    )
