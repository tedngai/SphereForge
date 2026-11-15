"""SphereForge Stage 4: Depth model factory.

Returns the appropriate depth estimator based on configuration.

Backends:

- ``dap``: ERP-native depth. Renders a panorama rig of rectilinear views,
  runs a perspective model on each view and fuses them back into ERP space
  (see :mod:`sphereforge.models.dap_model`). If true ERP-native weights are
  supplied via ``erp_weights`` they are used directly.
- ``depth_anything_v2``: Depth Anything V2 on rectilinear images. Used on
  cubemap faces, or on the full ERP frame if you accept the distortion.
- ``rpg360``: Metric3D v2 on cubemap faces (legacy RPG360 path).
- ``panda``: Deprecated alias for ``dap``.
- ``da360``: Not implemented (placeholder).
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Backends that are not yet backed by a real, runnable model. Kept explicit so
# Stage 4 can flag diagnostic-only outputs in its diagnostics JSON.
_STUB_DEPTH_MODELS = {"da360"}

# Backends that are fully implemented and runnable.
_IMPLEMENTED_DEPTH_MODELS = {"dap", "depth_anything_v2", "rpg360"}

# Map config-level perspective model names to Depth Anything V2 sizes.
_DA_V2_SIZE_ALIASES = {
    "small": "small",
    "vits": "small",
    "base": "base",
    "vitb": "base",
    "large": "large",
    "vitl": "large",
}


def _normalize_model_name(model_name: str) -> str:
    """Resolve deprecated aliases to canonical backend names."""
    return "dap" if model_name == "panda" else model_name


def is_stub_depth_model(model_name: str) -> bool:
    """Return whether the selected depth backend is still a stub path."""
    return _normalize_model_name(model_name) in _STUB_DEPTH_MODELS


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
            Common keys: ``device``, ``cache_dir``, ``model_size``, ``half``.
            DAP-specific: ``max_depth``, ``erp_weights``, ``yaw_steps``,
            ``pitches``, ``view_fov``, ``view_res``.

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
            model_size=kwargs.get("model_size", "small"),
            device=kwargs.get("device", "auto"),
            cache_dir=kwargs.get("cache_dir"),
            max_depth=float(kwargs.get("max_depth") or 0.0),
            erp_weights=kwargs.get("erp_weights"),
            yaw_steps=int(kwargs.get("yaw_steps") or 8),
            pitches=tuple(kwargs.get("pitches") or (-45.0, 0.0, 45.0)),
            view_fov=float(kwargs.get("view_fov") or 90.0),
            view_res=int(kwargs.get("view_res") or 512),
            half=bool(kwargs.get("half", False)),
        )

    elif model_name == "depth_anything_v2":
        from sphereforge.models.depth_anything_v2 import DepthAnythingV2Model

        size = str(kwargs.get("model_size", "small")).lower()
        return DepthAnythingV2Model(
            model_size=_DA_V2_SIZE_ALIASES.get(size, "small"),
            device=kwargs.get("device", "auto"),
            cache_dir=kwargs.get("cache_dir"),
            half=bool(kwargs.get("half", False)),
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
