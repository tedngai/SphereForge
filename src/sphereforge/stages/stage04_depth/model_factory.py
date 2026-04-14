"""SphereForge Stage 4: Depth model factory.

Returns the appropriate depth estimator based on configuration.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def get_depth_estimator(model_name: str, **kwargs: Any) -> Any:
    """Create a depth estimation model by name.

    Supported models:
    - "dap": Depth Any Panoramas — ERP-native depth (recommended for 360°)
    - "depth_anything_v2": Depth Anything V2 — perspective depth (for cubemap faces)
    - "rpg360": Uses Metric3D on cubemap faces (legacy RPG360 path)
    - "panda": DEPRECATED alias for "dap"
    - "da360": Not implemented (placeholder)

    Args:
        model_name: Model identifier string.
        **kwargs: Additional arguments passed to the model constructor.

    Returns:
        An instantiated depth model with an ``estimate_depth()`` method.

    Raises:
        NotImplementedError: If the model is not yet implemented.
        ValueError: If the model name is not recognized.
    """
    # Deprecated alias
    if model_name == "panda":
        logger.warning(
            "model_name='panda' is deprecated. PanDA has been superseded by "
            "DAP (Depth Any Panoramas). Use model_name='dap' instead."
        )
        model_name = "dap"

    if model_name == "dap":
        from sphereforge.models.dap_model import DAPModel
        return DAPModel(
            model_size=kwargs.get("model_size", "vitl"),
            device=kwargs.get("device", "auto"),
            cache_dir=kwargs.get("cache_dir"),
            max_depth=kwargs.get("max_depth", 10.0),
        )

    elif model_name == "depth_anything_v2":
        from sphereforge.models.depth_anything_v2 import DepthAnythingV2Model
        return DepthAnythingV2Model(
            model_size=kwargs.get("model_size", "large"),
            device=kwargs.get("device", "auto"),
            cache_dir=kwargs.get("cache_dir"),
        )

    elif model_name == "rpg360":
        from sphereforge.models.metric3d import Metric3DV2
        return Metric3DV2(
            model_name=kwargs.get("metric3d_model", "metric3d_vit_giant2"),
            cache_dir=kwargs.get("cache_dir"),
        )

    elif model_name == "da360":
        raise NotImplementedError(
            "da360 depth model is not implemented. "
            "Use 'dap' for ERP-native depth or 'depth_anything_v2' for perspective."
        )

    else:
        raise ValueError(
            f"Unknown depth model: {model_name!r}. "
            f"Supported: 'dap', 'depth_anything_v2', 'rpg360', 'panda' (deprecated)"
        )
