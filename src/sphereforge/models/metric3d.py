"""Metric3D v2 wrapper for metric monocular depth on rectilinear images.

Metric3D v2 (Yin et al., "Metric3D v2: A Versatile Monocular Geometric
Foundation Model for Zero-shot Metric Depth and Surface Normal Estimation")
produces *metric* depth in metres when given camera intrinsics; without
intrinsics it falls back to canonical-camera metric depth, which is still
metrically scaled (unlike Depth Anything V2's relative output).

This wrapper targets the Torch Hub entry point published by the authors
(``yvanyin/metric3d``). The model is loaded lazily on first use and cached in
the process. If Torch Hub is unavailable (no network, or the repo cannot be
fetched) the wrapper raises ``NotImplementedError`` with setup instructions so
that Stage 4 can fail fast instead of silently emitting invalid depth.

Usage in SphereForge:

- ``depth_model="rpg360"`` runs this model on the six cubemap faces and fuses
  the results with the RPG360 graph alignment
  (:mod:`sphereforge.stages.stage04_depth.rpg360_pipeline`).

License: Metric3D v2 code is BSD-2-Clause; check the upstream repository for
weight licensing before commercial use.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger("sphereforge.stage04.metric3d")

_VALID_MODELS = ("metric3d_vit_giant2", "metric3d_vit_large", "metric3d_vit_small")

# Canonical input size used by Metric3D v2 (H, W).
_CANONICAL_INPUT = (616, 1064)

# ImageNet normalisation used by the ViT backbone.
_IMAGENET_MEAN = np.array([123.675, 116.28, 103.53], dtype=np.float32)
_IMAGENET_STD = np.array([58.395, 57.12, 57.375], dtype=np.float32)


def _resolve_device(device: str) -> str:
    """Resolve ``"auto"`` to ``cuda`` when available, else ``cpu``."""
    if device != "auto":
        return device
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:  # pragma: no cover
        return "cpu"


class Metric3DV2:
    """Metric3D v2 metric-depth estimator.

    Args:
        model_name: One of ``"metric3d_vit_giant2"`` (default),
            ``"metric3d_vit_large"`` or ``"metric3d_vit_small"``.
        cache_dir: Optional directory for cached Torch Hub weights. Defaults to
            Torch Hub's own cache (``~/.cache/torch/hub``).
        device: ``"auto"``, ``"cuda"`` or ``"cpu"``.

    Raises:
        ValueError: If *model_name* is not a supported variant.
    """

    def __init__(
        self,
        model_name: str = "metric3d_vit_giant2",
        cache_dir: Path | None = None,
        device: str = "auto",
    ) -> None:
        if model_name not in _VALID_MODELS:
            raise ValueError(
                f"Unknown model_name {model_name!r}; expected one of {list(_VALID_MODELS)}"
            )
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.device = _resolve_device(device)
        # ``None`` until first use; tests inject a mock here.
        self._model: Any = None

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load the Torch Hub model lazily.

        Raises:
            NotImplementedError: If the Torch Hub model cannot be loaded.
        """
        if self._model is not None:
            return
        try:
            import torch
        except ImportError as exc:  # pragma: no cover
            raise NotImplementedError(
                "Metric3D v2 requires PyTorch. Install with: pip install torch"
            ) from exc

        hub_kwargs: dict[str, Any] = {"source": "github", "trust_repo": True}
        if self.cache_dir is not None:
            hub_kwargs["model_dir"] = str(self.cache_dir)
        try:
            model = torch.hub.load(
                "yvanyin/metric3d", self.model_name, pretrain=True, **hub_kwargs
            )
        except Exception as exc:  # pragma: no cover - network dependent
            raise NotImplementedError(
                "Metric3D v2 weights could not be loaded from Torch Hub "
                f"(model_name={self.model_name!r}): {exc}. "
                "Metric3D v2 requires network access on first use, or a "
                "pre-populated Torch Hub cache directory. Alternatives: use "
                "depth_model='dap' or 'depth_anything_v2'."
            ) from exc

        model.eval()
        self._model = model.to(self.device)
        logger.info("Metric3D v2 ready: %s on %s", self.model_name, self.device)

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def _preprocess(self, image: np.ndarray) -> Any:
        """Convert an RGB uint8 image to a normalised canonical-size tensor."""
        import cv2
        import torch

        resized = cv2.resize(
            image, (_CANONICAL_INPUT[1], _CANONICAL_INPUT[0]), interpolation=cv2.INTER_LINEAR
        ).astype(np.float32)
        normalised = (resized - _IMAGENET_MEAN) / _IMAGENET_STD
        tensor = torch.from_numpy(normalised.transpose(2, 0, 1)).unsqueeze(0)
        return tensor.to(self.device)

    def estimate_depth(self, image: np.ndarray) -> np.ndarray:
        """Estimate metric depth for a single rectilinear image.

        Args:
            image: RGB image ``(H, W, 3)`` uint8.

        Returns:
            Metric depth map ``(H, W)`` float32 in metres.

        Raises:
            ValueError: If *image* is not ``(H, W, 3)``.
            NotImplementedError: If the model cannot be loaded.
        """
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError(f"Expected image with shape (H, W, 3), got {image.shape}")
        return self.estimate_depth_batch([image])[0]

    def estimate_depth_batch(self, images: list[np.ndarray]) -> list[np.ndarray]:
        """Estimate metric depth for a batch of rectilinear images.

        Args:
            images: List of RGB images ``(H_i, W_i, 3)`` uint8.

        Returns:
            List of metric depth maps ``(H_i, W_i)`` float32, in input order.

        Raises:
            ValueError: If any image is not ``(H, W, 3)``.
            NotImplementedError: If the model cannot be loaded.
        """
        if not images:
            return []
        for idx, image in enumerate(images):
            if image.ndim != 3 or image.shape[2] != 3:
                raise ValueError(
                    f"Image at index {idx} has shape {image.shape}, expected (H, W, 3)"
                )

        self._load()
        import cv2
        import torch

        results: list[np.ndarray] = []
        with torch.inference_mode():
            for image in images:
                tensor = self._preprocess(image)
                output = self._model(tensor)
                if isinstance(output, dict):
                    depth = output["depth"]
                elif isinstance(output, (list, tuple)):
                    depth = output[0]
                else:
                    depth = output
                if isinstance(depth, (list, tuple)):
                    depth = depth[-1]
                depth_np = (
                    depth.squeeze().detach().float().cpu().numpy().astype(np.float32)
                    if hasattr(depth, "detach")
                    else np.asarray(depth, dtype=np.float32).squeeze()
                )
                if depth_np.ndim != 2:
                    raise RuntimeError(
                        f"Metric3D returned depth with shape {depth_np.shape}; expected (H, W)"
                    )
                if depth_np.shape != image.shape[:2]:
                    depth_np = cv2.resize(
                        depth_np, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_LINEAR
                    )
                results.append(depth_np.astype(np.float32))
        return results

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def is_stub(self) -> bool:
        """Metric3D v2 is implemented (weights are fetched on first use)."""
        return False

    def __repr__(self) -> str:
        return f"Metric3DV2(model_name={self.model_name!r}, device={self.device!r})"
