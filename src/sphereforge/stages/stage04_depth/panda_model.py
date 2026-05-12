"""PanDA monocular depth estimation model wrapper for ERP images.

DEPRECATED: PanDA has been superseded by DAP (Depth Any Panoramas),
which is MIT licensed, has publicly downloadable weights on HuggingFace,
and produces better results. Use ``DAPModel`` instead.

    from sphereforge.models.dap_model import DAPModel
    model = DAPModel(model_size="vitl")

This file is kept for backward compatibility only.

Wraps the PanDA (Panoramic Depth Architecture) model which uses a MiDaS-like
backbone with Möbius conformal padding for distortion-aware equirectangular
depth estimation. Since PanDA model weights are not publicly available via a
simple URL, this class is implemented as a stub that raises
``NotImplementedError`` when the weights file is not found locally.

To use this model:
1. Obtain PanDA weights from the authors (see comments below).
2. Place the weight file at ``~/.cache/sphereforge/models/panda/panda_erp.pth``
   or pass the path via the ``model_path`` argument.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from sphereforge.common.model_cache import get_model_path

logger = logging.getLogger("sphereforge.stage04.panda")

# ImageNet normalisation constants (same as MiDaS / DPT)
_IMAGENET_MEAN = [0.485, 0.456, 0.406]
_IMAGENET_STD = [0.229, 0.224, 0.225]

# PanDA ERP input resolution (height x width)
_PANDA_INPUT_H = 384
_PANDA_INPUT_W = 768

# Default weight file name
_PANDA_WEIGHT_FILENAME = "panda_erp.pth"

# ---------------------------------------------------------------------------
# Weight acquisition instructions
# ---------------------------------------------------------------------------
# PanDA (Panoramic Depth Architecture) is described in:
#   "PanDA: Panoramic Depth Estimation with Möbius Conformal Padding"
#   The model is not released on a public download URL or HuggingFace hub.
#
# To obtain weights:
#   1. Contact the PanDA authors or check the project repository for a
#      download link.
#   2. Alternatively, if you have trained PanDA from source, export the
#      model's ``state_dict`` as a ``.pth`` file.
#   3. Place the file at: ~/.cache/sphereforge/models/panda/panda_erp.pth
#      Or set the environment variable SPHEREFORGE_PANDA_WEIGHTS to the
#      absolute path of the weight file.
# ---------------------------------------------------------------------------


class PanDAModel:
    """Wrapper around PanDA for equirectangular monocular depth estimation.

    PanDA uses a MiDaS-like (DPT) backbone with Möbius conformal padding to
    handle the distortion inherent in equirectangular images. It produces
    monocular, relative-scale depth maps.

    .. note::
        This is a **stub implementation**. The class structure, preprocessing,
        and postprocessing logic are complete, but the actual model loading
        and inference are gated behind a ``NotImplementedError`` because
        PanDA weights are not publicly downloadable via a simple URL.

    Args:
        model_path: Optional path to the PanDA weight file (``.pth``).
            If ``None``, looks in the default cache directory
            (``~/.cache/sphereforge/models/panda/panda_erp.pth``).
        device: Compute device. ``"auto"`` selects CUDA if available,
            otherwise CPU. Can also be ``"cuda"`` or ``"cpu"`` explicitly.

    Raises:
        NotImplementedError: If model weights are not found locally.
    """

    def __init__(
        self,
        model_path: Path | None = None,
        device: str = "auto",
    ) -> None:
        # Device selection
        if device == "auto":
            try:
                import torch

                self._device_str = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self._device_str = "cpu"
        else:
            self._device_str = device

        # Resolve model weight path
        if model_path is not None:
            self._model_path = Path(model_path)
        else:
            self._model_path = get_model_path("panda", _PANDA_WEIGHT_FILENAME)

        self._model = None
        self._weights_loaded = False

        # Check whether weights exist locally (no public download URL)
        if self._model_path.exists():
            self._weights_loaded = True
            logger.info("PanDA weights found at: %s", self._model_path)
        else:
            logger.warning(
                "PanDA weights not found at %s and no public download URL "
                "is available. See docstring for weight acquisition instructions.",
                self._model_path,
            )
            self._weights_loaded = False

    def _load_model(self) -> None:
        """Load the PanDA model weights into memory.

        Raises:
            NotImplementedError: Always, because PanDA weights are not
                publicly available and the model architecture is not
                bundled in SphereForge.
        """
        if not self._weights_loaded:
            raise NotImplementedError(
                "PanDA model weights are not available. "
                "PanDA (Panoramic Depth Architecture) weights must be obtained "
                "from the original authors and placed at: "
                f"{self._model_path}\n\n"
                "Steps to set up PanDA:\n"
                "1. Contact the PanDA authors or find the weights at their "
                "project repository.\n"
                "2. Place the .pth file at "
                "~/.cache/sphereforge/models/panda/panda_erp.pth\n"
                "3. Alternatively, pass the path directly: "
                "PanDAModel(model_path='/path/to/panda_erp.pth')\n\n"
                "If you have the weights but this error persists, ensure "
                "the file exists and is readable."
            )
        # If weights are available, this is where we would:
        # 1. Build the MiDaS/DPT backbone with Möbius conformal padding layers
        # 2. Load the state dict from self._model_path
        # 3. Move model to self._device_str and set eval mode
        # The actual implementation requires the PanDA model code, which is
        # not bundled in SphereForge.
        raise NotImplementedError(
            "PanDA model architecture is not bundled in SphereForge. "
            "The model uses a MiDaS-like DPT backbone with Möbius conformal "
            "padding for ERP distortion handling. To enable full inference, "
            "install the PanDA package and override this method."
        )

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocess an ERP image for PanDA inference.

        Normalises with ImageNet mean/std and resizes to the model's expected
        ERP input resolution (384x768).

        Args:
            image: Input ERP image of shape (H, W, 3) with dtype uint8.

        Returns:
            Preprocessed image array of shape (3, 384, 768) with dtype
            float32, normalised with ImageNet statistics.
        """
        import cv2

        # Resize to PanDA ERP input size
        resized = cv2.resize(
            image, (_PANDA_INPUT_W, _PANDA_INPUT_H), interpolation=cv2.INTER_LINEAR
        )

        # Convert HWC uint8 -> CHW float32 in [0, 1]
        image_float = resized.astype(np.float32) / 255.0
        image_chw = np.transpose(image_float, (2, 0, 1))  # (3, H, W)

        # ImageNet normalisation (channel-wise)
        mean = np.array(_IMAGENET_MEAN, dtype=np.float32).reshape(3, 1, 1)
        std = np.array(_IMAGENET_STD, dtype=np.float32).reshape(3, 1, 1)
        image_norm = (image_chw - mean) / std

        return image_norm

    def _postprocess(
        self, raw_depth: np.ndarray, orig_h: int, orig_w: int
    ) -> np.ndarray:
        """Postprocess PanDA raw output back to original resolution.

        Resizes the model output from (384, 768) back to (orig_h, orig_w).

        Args:
            raw_depth: Raw depth output from the model, shape (384, 768).
            orig_h: Original image height.
            orig_w: Original image width.

        Returns:
            Depth map of shape (orig_h, orig_w) with dtype float32.
        """
        import cv2

        if raw_depth.shape != (orig_h, orig_w):
            depth_resized = cv2.resize(
                raw_depth, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR
            )
        else:
            depth_resized = raw_depth

        return depth_resized.astype(np.float32)

    def estimate_depth(self, image: np.ndarray) -> np.ndarray:
        """Run PanDA depth estimation on a single ERP image.

        Preprocesses the input (normalise + resize), runs inference, and
        resizes the output back to the original resolution.

        Args:
            image: Input ERP image of shape (H, W, 3) with dtype uint8.

        Returns:
            Monocular depth map of shape (H, W) with dtype float32. The
            depth is in relative (monocular) scale — not metric.

        Raises:
            NotImplementedError: If PanDA model weights are not available.
            ValueError: If the input image does not have shape (H, W, 3).
        """
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError(
                f"Expected image with shape (H, W, 3), got {image.shape}"
            )

        _orig_h, _orig_w = image.shape[:2]

        # This will raise NotImplementedError if weights are missing
        self._load_model()

        # Preprocess
        input_tensor = self._preprocess(image)
        logger.debug(
            "PanDA preprocessed input: shape %s", input_tensor.shape
        )

        # -----------------------------------------------------------------
        # Inference placeholder — actual inference requires the PanDA model
        # code with Möbius conformal padding. The expected flow is:
        #
        #   with torch.no_grad():
        #       input_torch = (
        #           torch.from_numpy(input_tensor)
        #           .unsqueeze(0)
        #           .to(self._device_str)
        #       )
        #       output = self._model(input_torch)
        #       raw_depth = output.squeeze().cpu().numpy()
        #
        # The model produces inverse depth (disparity) which should be
        # inverted: depth = 1.0 / (raw_depth + eps)
        # -----------------------------------------------------------------
        raise NotImplementedError(
            "PanDA inference is not available without the model weights "
            "and architecture. See PanDAModel.__init__ docstring for setup "
            "instructions."
        )

        # Postprocess — unreachable without model, but shown for reference:
        # depth = self._postprocess(raw_depth, orig_h, orig_w)
        # logger.debug(
        #     "PanDA depth output: shape %s, range [%.2f, %.2f]",
        #     depth.shape, float(np.min(depth)), float(np.max(depth)),
        # )
        # return depth

    def estimate_depth_batch(self, images: list[np.ndarray]) -> list[np.ndarray]:
        """Run PanDA depth estimation on a batch of ERP images.

        Processes each image independently (PanDA does not natively support
        variable-size batching for ERP images).

        Args:
            images: List of input ERP images, each of shape (H, W, 3) with
                dtype uint8. Images may have different resolutions.

        Returns:
            List of monocular depth maps, each of shape (H_i, W_i) with
            dtype float32. The i-th output corresponds to ``images[i]``.

        Raises:
            NotImplementedError: If PanDA model weights are not available.
            ValueError: If any image does not have shape (H, W, 3).
        """
        results: list[np.ndarray] = []
        n = len(images)
        logger.info("Running PanDA batch inference on %d images", n)

        for i, image in enumerate(images):
            if image.ndim != 3 or image.shape[2] != 3:
                raise ValueError(
                    f"Image at index {i} has shape {image.shape}, "
                    f"expected (H, W, 3)"
                )
            depth = self.estimate_depth(image)
            results.append(depth)

            if (i + 1) % 10 == 0 or i == n - 1:
                logger.info("PanDA batch: %d / %d images processed", i + 1, n)

        return results
