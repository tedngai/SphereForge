"""Depth Anything V2 wrapper for perspective (rectilinear) depth estimation.

Wraps the HuggingFace ``transformers`` implementation of Depth Anything V2
(``depth-anything/Depth-Anything-V2-*-hf``). The relative checkpoints output
*affine-invariant disparity*: larger values are **closer**, and the values are
only defined up to an unknown scale and shift. :meth:`estimate_disparity_batch`
returns that raw output; :meth:`estimate_depth` / :meth:`estimate_depth_batch`
invert it to depth (larger = farther) so callers that expect distances get
distances. Stage 4 aligns the result to COLMAP sparse-point scale afterwards.

Treating the raw disparity as depth turns the scene inside out (the nearest
surfaces come back as the farthest). On the synthetic room the uninverted maps
correlated with ground-truth distance at Spearman -0.48 to -0.81.

Repo ids containing ``Metric`` (e.g. ``Depth-Anything-V2-Metric-Indoor-Small-hf``)
already output metric depth and are passed through unchanged.

The wrapper is used in two places:

1. Directly on rectilinear cubemap faces (``depth_model="depth_anything_v2"``).
2. Inside the ERP-native ``dap`` backend, which renders a panorama rig of
   rectilinear views, runs this model per view, and fuses them back into an
   equirectangular depth map (see :mod:`sphereforge.models.dap_model`).

Weights are downloaded on first use to the HuggingFace cache (respects
``HF_HOME`` / ``HF_HUB_CACHE``) and may be pre-seeded into
``cache_dir/depth_anything_v2/<model_size>`` to work fully offline.

License note: the *Small* variant is Apache-2.0. The *Base* and *Large*
variants are released under CC-BY-NC-4.0 (non-commercial). The default is
``small`` so that the default pipeline stays commercially usable.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger("sphereforge.stage04.depth_anything_v2")

# HuggingFace repo ids per model size.
_HF_REPOS: dict[str, str] = {
    "vits": "depth-anything/Depth-Anything-V2-Small-hf",
    "vitb": "depth-anything/Depth-Anything-V2-Base-hf",
    "vitl": "depth-anything/Depth-Anything-V2-Large-hf",
}

# Accepted aliases -> canonical size key.
_SIZE_ALIASES: dict[str, str] = {
    "small": "vits",
    "vits": "vits",
    "vit_s": "vits",
    "base": "vitb",
    "vitb": "vitb",
    "vit_b": "vitb",
    "large": "vitl",
    "vitl": "vitl",
    "vit_l": "vitl",
}

# Non-commercial variants (CC-BY-NC-4.0).
_NON_COMMERCIAL_SIZES = {"vitb", "vitl"}


# Disparity below ``max(disparity) / _MAX_RANGE_RATIO`` is treated as "too far to
# trust" (sky, or a negative-shift artefact) and marked invalid (depth 0)
# instead of becoming a huge distance.
_MAX_RANGE_RATIO = 100.0


def disparity_to_depth(
    disparity: np.ndarray, max_range_ratio: float = _MAX_RANGE_RATIO
) -> np.ndarray:
    """Convert a relative disparity map into a relative depth map.

    Args:
        disparity: Disparity map (larger = closer), any shape.
        max_range_ratio: Largest allowed far/near ratio. Pixels whose disparity
            is below ``max(disparity) / max_range_ratio`` (including zero and
            negative values) are returned as 0, the pipeline's "invalid depth".

    Returns:
        Depth map (larger = farther), same shape, float32. The scale is
        arbitrary; Stage 4 alignment fixes it against SfM.
    """
    disp = np.asarray(disparity, dtype=np.float64)
    finite = np.isfinite(disp)
    if not np.any(finite & (disp > 0)):
        return np.zeros(disp.shape, dtype=np.float32)
    floor = float(np.max(disp[finite])) / max(float(max_range_ratio), 1.0)
    valid = finite & (disp > floor) & (disp > 0)
    depth = np.zeros(disp.shape, dtype=np.float64)
    depth[valid] = 1.0 / disp[valid]
    return depth.astype(np.float32)


def _resolve_device(device: str) -> str:
    """Resolve ``"auto"`` to ``cuda`` when available, else ``cpu``."""
    if device != "auto":
        return device
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:  # pragma: no cover - torch is a hard dependency
        return "cpu"


class DepthAnythingV2Model:
    """Monocular relative depth estimator (Depth Anything V2).

    Args:
        model_size: ``"small"``/``"vits"`` (Apache-2.0, default),
            ``"base"``/``"vitb"`` or ``"large"``/``"vitl"`` (CC-BY-NC-4.0).
        device: ``"auto"``, ``"cuda"``, ``"cuda:1"`` or ``"cpu"``.
        cache_dir: Optional local directory that already contains a saved
            HuggingFace model (``config.json`` + weights). When given and
            present, the model is loaded from disk instead of the Hub.
        repo_id: Optional explicit HuggingFace repo id overriding *model_size*.
        half: If True, load float16 weights on CUDA for lower memory use.

    Raises:
        ValueError: If *model_size* is not a recognized variant.
        NotImplementedError: If ``transformers``/``torch`` are not installed.
    """

    def __init__(
        self,
        model_size: str = "small",
        device: str = "auto",
        cache_dir: Path | None = None,
        repo_id: str | None = None,
        half: bool = False,
    ) -> None:
        size_key = _SIZE_ALIASES.get(str(model_size).lower())
        if size_key is None:
            raise ValueError(
                f"Unknown Depth Anything V2 model size {model_size!r}. "
                f"Expected one of: {sorted(_SIZE_ALIASES)}"
            )
        self.model_size = size_key
        self.repo_id = repo_id or _HF_REPOS[size_key]
        self.device = _resolve_device(device)
        self.half = bool(half) and self.device.startswith("cuda")
        self.cache_dir = Path(cache_dir) if cache_dir is not None else None
        # Metric checkpoints output depth directly; relative ones output disparity.
        self.outputs_metric_depth = "metric" in self.repo_id.lower()

        if size_key in _NON_COMMERCIAL_SIZES:
            logger.warning(
                "Depth Anything V2 '%s' weights are CC-BY-NC-4.0 (non-commercial). "
                "Use model_size='small' for Apache-2.0 weights.",
                size_key,
            )

        self._processor: Any = None
        self._model: Any = None

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Lazily load the processor and model (downloads weights if needed).

        Raises:
            NotImplementedError: If ``transformers`` or ``torch`` is missing.
            RuntimeError: If the weights cannot be resolved.
        """
        if self._model is not None:
            return

        try:
            import torch
            from transformers import AutoImageProcessor, AutoModelForDepthEstimation
        except ImportError as exc:  # pragma: no cover - depends on env
            raise NotImplementedError(
                "Depth Anything V2 requires 'transformers' and 'torch'. "
                "Install with: pip install 'sphereforge[depth]'"
            ) from exc

        source: str = self.repo_id
        if self.cache_dir is not None and (self.cache_dir / "config.json").exists():
            source = str(self.cache_dir)
            logger.info("Loading Depth Anything V2 from local cache: %s", source)
        else:
            logger.info("Loading Depth Anything V2 from HuggingFace: %s", source)

        try:
            self._processor = AutoImageProcessor.from_pretrained(source)
            model = AutoModelForDepthEstimation.from_pretrained(source)
        except Exception as exc:  # pragma: no cover - network dependent
            raise RuntimeError(
                f"Failed to load Depth Anything V2 weights from {source!r}: {exc}. "
                "Pre-download with `huggingface-cli download <repo>` or pass "
                "cache_dir pointing at a local copy."
            ) from exc

        model.eval()
        if self.half:
            model = model.half()
        self._model = model.to(self.device)
        if self.device.startswith("cuda"):
            # The panorama rig renders many identically shaped views, so cuDNN
            # autotuning pays for itself (~10x faster than the default heuristics).
            torch.backends.cudnn.benchmark = True
        logger.info(
            "Depth Anything V2 ready: size=%s, device=%s, half=%s",
            self.model_size,
            self.device,
            self.half,
        )

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def estimate_depth(self, image: np.ndarray) -> np.ndarray:
        """Estimate relative depth for a single rectilinear image.

        Args:
            image: RGB image of shape ``(H, W, 3)``, dtype uint8.

        Returns:
            Depth map of shape ``(H, W)``, dtype float32. Values are relative
            (larger = farther, 0 = invalid) and not metric.

        Raises:
            ValueError: If *image* is not ``(H, W, 3)``.
        """
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError(f"Expected image with shape (H, W, 3), got {image.shape}")
        return self.estimate_depth_batch([image])[0]

    def estimate_depth_batch(self, images: list[np.ndarray]) -> list[np.ndarray]:
        """Estimate relative depth for a batch of rectilinear images.

        Runs :meth:`estimate_disparity_batch` and inverts the result with
        :func:`disparity_to_depth` (metric checkpoints are passed through).

        Args:
            images: List of RGB images, each ``(H_i, W_i, 3)`` uint8.

        Returns:
            List of float32 depth maps (larger = farther, 0 = invalid), each
            ``(H_i, W_i)``, in input order.

        Raises:
            ValueError: If any image is not ``(H, W, 3)``.
        """
        raw = self.estimate_disparity_batch(images)
        if self.outputs_metric_depth:
            return raw
        return [disparity_to_depth(d) for d in raw]

    def estimate_disparity_batch(self, images: list[np.ndarray]) -> list[np.ndarray]:
        """Run the network and return its raw output for each image.

        For the relative checkpoints this is affine-invariant disparity
        (larger = closer); for ``Metric`` checkpoints it is metric depth.
        Each image is processed independently at its native resolution so that
        outputs can be resized back exactly to the input shape.

        Args:
            images: List of RGB images, each ``(H_i, W_i, 3)`` uint8.

        Returns:
            List of float32 maps, each ``(H_i, W_i)``, in input order.

        Raises:
            ValueError: If any image is not ``(H, W, 3)``.
        """
        if not images:
            return []
        for idx, image in enumerate(images):
            if image.ndim != 3 or image.shape[2] != 3:
                raise ValueError(
                    f"Image at index {idx} has shape {image.shape}, expected (H, W, 3)"
                )

        self._load()
        import torch

        results: list[np.ndarray] = []
        with torch.inference_mode():
            for idx, image in enumerate(images):
                inputs = self._processor(images=image, return_tensors="pt")
                inputs = {
                    k: (v.to(self.device, dtype=torch.float16) if self.half else v.to(self.device))
                    for k, v in inputs.items()
                }
                predicted = self._model(**inputs).predicted_depth
                predicted = torch.nn.functional.interpolate(
                    predicted.unsqueeze(1),
                    size=image.shape[:2],
                    mode="bicubic",
                    align_corners=False,
                ).squeeze(1)
                results.append(predicted[0].float().cpu().numpy().astype(np.float32))
                logger.debug(
                    "Depth Anything V2: image %d/%d %s -> range [%.3f, %.3f]",
                    idx + 1,
                    len(images),
                    image.shape[:2],
                    float(results[-1].min()),
                    float(results[-1].max()),
                )
        return results

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def is_stub(self) -> bool:
        """Depth Anything V2 is a fully implemented backend."""
        return False

    def __repr__(self) -> str:
        return (
            f"DepthAnythingV2Model(model_size={self.model_size!r}, "
            f"device={self.device!r}, repo_id={self.repo_id!r})"
        )
