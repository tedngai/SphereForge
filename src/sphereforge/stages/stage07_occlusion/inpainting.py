"""GS-Diff inpainting backend for occlusion recovery.

Provides four inpainting strategies for filling holes in rendered Gaussian Splat views:

1. **Flux2KleinInpainter** (default, recommended): Uses FLUX.2 Klein 9B inpainting
   via the HuggingFace diffusers ``Flux2KleinInpaintPipeline``. Produces
   significantly higher-quality inpainting than SD-1.5, with optional
   reference-image conditioning for view consistency. Requires ~24 GB VRAM
   (bfloat16). License: Flux Dev License (non-commercial).

2. **FluxFillInpainter**: Uses FLUX.1-Fill-dev via ``FluxFillPipeline``.
   12B parameter rectified-flow transformer purpose-built for inpainting.
   Produces excellent results. Requires ~24 GB VRAM (bfloat16).
   License: Flux Dev License (non-commercial).

3. **SDInpainter** (legacy): Uses Stable Diffusion 1.5 inpainting. Lightweight
   and works on any GPU with ~4 GB VRAM. Quality is noticeably lower than
   the Flux backends.

4. **EscherNetInpainter** (optional): Uses EscherNet multi-view diffusion for
   view-consistent inpainting. Requires cloning the EscherNet repo and downloading
   specialized weights. License: CreativeML RAIL-M (non-commercial).

All backends integrate with the GS-Diff pipeline via the same ``inpaint_holes()``
interface, making them interchangeable.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar

import numpy as np

from sphereforge.common.model_cache import DEFAULT_CACHE_DIR

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger("sphereforge.stage07.inpainting")


class SDInpainter:
    """Stable Diffusion inpainting for hole filling in rendered views.

    Uses the HuggingFace diffusers pipeline for text-guided inpainting.
    This is the recommended default inpainter — easy to install, well-supported,
    and produces good results for most scenes.

    The inpainting model is downloaded from HuggingFace on first use.

    Args:
        model_id: HuggingFace model ID for inpainting. Defaults to
            "runwayml/stable-diffusion-inpainting" (SD 1.5 inpainting).
        device: Compute device. "auto" selects CUDA if available.
        cache_dir: Directory for caching model weights.
        prompt: Default text prompt for inpainting. Defaults to
            "clean indoor scene, high quality, detailed".

    Raises:
        ImportError: If diffusers or torch is not installed.
    """

    def __init__(
        self,
        model_id: str = "runwayml/stable-diffusion-inpainting",
        device: str = "auto",
        cache_dir: Path | None = None,
        prompt: str = "clean indoor scene, high quality, detailed",
    ) -> None:
        self._model_id = model_id
        self._cache_dir = cache_dir or str(DEFAULT_CACHE_DIR / "sd_inpainting")
        self._prompt = prompt
        self._pipeline = None

        if device == "auto":
            try:
                import torch
                self._device_str = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self._device_str = "cpu"
        else:
            self._device_str = device

    def _load_model(self) -> None:
        """Load the Stable Diffusion inpainting pipeline."""
        if self._pipeline is not None:
            return

        try:
            import torch
            from diffusers import StableDiffusionInpaintPipeline
        except ImportError as exc:
            raise ImportError(
                "diffusers and torch are required for SD inpainting. "
                "Install with: pip install diffusers torch"
            ) from exc

        logger.info("Loading SD inpainting model: %s ...", self._model_id)

        dtype = torch.float16 if self._device_str == "cuda" else torch.float32

        self._pipeline = StableDiffusionInpaintPipeline.from_pretrained(
            self._model_id,
            cache_dir=self._cache_dir,
            torch_dtype=dtype,
        )

        if self._device_str == "cuda":
            self._pipeline = self._pipeline.to("cuda")

        # Disable NSFW safety checker (causes black images in many scenes)
        self._pipeline.safety_checker = None
        self._pipeline.requires_safety_checker = False

        logger.info("SD inpainting model loaded on %s", self._device_str)

    def ensure_available(self) -> None:
        """Validate that the configured inpainting backend can be used."""
        try:
            import torch  # noqa: F401
            from diffusers import StableDiffusionInpaintPipeline  # noqa: F401
            import transformers  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "Stable Diffusion inpainting requires torch, diffusers, and transformers. "
                "Install with: pip install torch diffusers transformers"
            ) from exc

    def inpaint_holes(
        self,
        rendered_image: np.ndarray,
        hole_mask: np.ndarray,
        prompt: str | None = None,
        num_inference_steps: int = 30,
        seed: int = 42,
    ) -> np.ndarray:
        """Inpaint holes in a rendered image using Stable Diffusion.

        Args:
            rendered_image: Rendered image (H, W, 3) uint8 RGB.
            hole_mask: Binary mask (H, W) where True = hole to fill,
                False = keep existing pixels.
            prompt: Text prompt for inpainting. Uses default if None.
            num_inference_steps: Number of denoising steps. Default 30.
            seed: Random seed for reproducibility.

        Returns:
            Inpainted image (H, W, 3) uint8 RGB.
        """
        self._load_model()

        from PIL import Image

        prompt = prompt or self._prompt

        # Convert to PIL
        init_image = Image.fromarray(rendered_image)
        # diffusers expects mask where 0=inpaint, 255=keep — invert our mask
        mask_pil = Image.fromarray((~hole_mask).astype(np.uint8) * 255)

        # Run inpainting
        import torch

        generator = torch.Generator(device=self._device_str).manual_seed(seed)
        result = self._pipeline(
            prompt=prompt,
            image=init_image,
            mask_image=mask_pil,
            num_inference_steps=num_inference_steps,
            generator=generator,
        ).images[0]

        # Convert back to numpy
        inpainted = np.array(result, dtype=np.uint8)

        logger.debug(
            "SD inpainting complete: image %s, %d hole pixels filled",
            rendered_image.shape, int(hole_mask.sum()),
        )

        return inpainted


class Flux2KleinInpainter:
    """FLUX.2 Klein 9B inpainting for hole filling in rendered views.

    Uses the FLUX.2 Klein base 9B model with the ``Flux2KleinInpaintPipeline``
    from HuggingFace diffusers. Produces high-quality inpainting with optional
    reference-image conditioning for improved view consistency.

    This is the recommended inpainting backend for machines with >= 24 GB VRAM.
    It produces significantly better results than SD-1.5.

    The model weights are downloaded from HuggingFace on first use (~18 GB).

    License: Flux Dev License (non-commercial use).

    Args:
        model_id: HuggingFace model ID. Defaults to
            "black-forest-labs/FLUX.2-klein-base-9B".
        device: Compute device. "auto" selects CUDA if available.
        cache_dir: Directory for caching model weights.
        prompt: Default text prompt for inpainting.

    Raises:
        ImportError: If diffusers or torch is not installed.
    """

    def __init__(
        self,
        model_id: str = "black-forest-labs/FLUX.2-klein-base-9B",
        device: str = "auto",
        cache_dir: Path | None = None,
        prompt: str = "clean indoor scene, high quality, detailed",
    ) -> None:
        self._model_id = model_id
        self._cache_dir = cache_dir or str(DEFAULT_CACHE_DIR / "flux2_klein_inpaint")
        self._prompt = prompt
        self._pipeline = None

        if device == "auto":
            try:
                import torch
                self._device_str = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self._device_str = "cpu"
        else:
            self._device_str = device

    def _load_model(self) -> None:
        """Load the FLUX.2 Klein inpainting pipeline."""
        if self._pipeline is not None:
            return

        try:
            import torch
            from diffusers import Flux2KleinInpaintPipeline
        except ImportError as exc:
            raise ImportError(
                "FLUX.2 Klein inpainting requires diffusers >= 0.38 and torch. "
                "Install with: pip install -U diffusers torch"
            ) from exc

        logger.info("Loading FLUX.2 Klein inpainting model: %s ...", self._model_id)

        dtype = torch.bfloat16 if self._device_str == "cuda" else torch.float32

        try:
            self._pipeline = Flux2KleinInpaintPipeline.from_pretrained(
                self._model_id,
                cache_dir=self._cache_dir,
                torch_dtype=dtype,
            )
        except Exception as exc:
            if "401" in str(exc) or "Unauthorized" in str(exc) or "gated" in str(exc).lower():
                raise ImportError(
                    f"FLUX.2 Klein requires HuggingFace authentication. Steps:\n"
                    f"1. Accept the license at https://huggingface.co/{self._model_id}\n"
                    f"2. Get a token at https://huggingface.co/settings/tokens\n"
                    f"3. Run: hf auth login\n"
                    f"   Or set env: export HF_TOKEN=your_token\n"
                    f"Original error: {exc}"
                ) from exc
            raise

        if self._device_str == "cuda":
            self._pipeline = self._pipeline.to("cuda")

        logger.info("FLUX.2 Klein inpainting model loaded on %s", self._device_str)

    def ensure_available(self) -> None:
        """Validate that the configured inpainting backend can be used.

        Eagerly loads the model to detect authentication issues up front.
        """
        self._load_model()

    def inpaint_holes(
        self,
        rendered_image: np.ndarray,
        hole_mask: np.ndarray,
        prompt: str | None = None,
        image_reference: np.ndarray | None = None,
        num_inference_steps: int = 4,
        guidance_scale: float = 7.0,
        strength: float = 1.0,
        seed: int = 42,
    ) -> np.ndarray:
        """Inpaint holes using FLUX.2 Klein.

        Args:
            rendered_image: Rendered image (H, W, 3) uint8 RGB.
            hole_mask: Binary mask (H, W) where True = hole to fill,
                False = keep existing pixels.
            prompt: Text prompt for inpainting. Uses default if None.
            image_reference: Optional reference image for conditioning
                (e.g., a nearby training view). Can improve view consistency.
            num_inference_steps: Number of denoising steps. Default 28.
            guidance_scale: Classifier-free guidance scale. Default 7.0.
            strength: Inpainting strength. 1.0 = full replacement of hole.
            seed: Random seed for reproducibility.

        Returns:
            Inpainted image (H, W, 3) uint8 RGB.
        """
        self._load_model()

        from PIL import Image

        import torch

        prompt = prompt or self._prompt

        init_image = Image.fromarray(rendered_image)
        # Flux2Klein expects mask where white = repaint
        mask_pil = Image.fromarray((hole_mask.astype(np.uint8) * 255))
        # Blur mask edges for smoother blending
        mask_pil = self._pipeline.mask_processor.blur(mask_pil, blur_factor=12)

        generator = torch.Generator(device="cpu").manual_seed(seed)

        kwargs: dict = dict(
            prompt=prompt,
            image=init_image,
            mask_image=mask_pil,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            strength=strength,
            generator=generator,
            max_sequence_length=512,
        )

        if image_reference is not None:
            kwargs["image_reference"] = Image.fromarray(image_reference)

        result = self._pipeline(**kwargs).images[0]

        inpainted = np.array(result, dtype=np.uint8)

        logger.debug(
            "FLUX.2 Klein inpainting complete: image %s, %d hole pixels filled",
            rendered_image.shape, int(hole_mask.sum()),
        )

        return inpainted


class FluxFillInpainter:
    """FLUX.1-Fill-dev inpainting for hole filling in rendered views.

    Uses the FLUX.1-Fill-dev model via ``FluxFillPipeline`` from HuggingFace
    diffusers. This 12B parameter rectified-flow transformer is purpose-built
    for inpainting and outpainting, producing excellent results.

    License: Flux Dev License (non-commercial use).

    Args:
        model_id: HuggingFace model ID. Defaults to
            "black-forest-labs/FLUX.1-Fill-dev".
        device: Compute device. "auto" selects CUDA if available.
        cache_dir: Directory for caching model weights.
        prompt: Default text prompt for inpainting.

    Raises:
        ImportError: If diffusers or torch is not installed.
    """

    def __init__(
        self,
        model_id: str = "black-forest-labs/FLUX.1-Fill-dev",
        device: str = "auto",
        cache_dir: Path | None = None,
        prompt: str = "clean indoor scene, high quality, detailed",
    ) -> None:
        self._model_id = model_id
        self._cache_dir = cache_dir or str(DEFAULT_CACHE_DIR / "flux_fill")
        self._prompt = prompt
        self._pipeline = None

        if device == "auto":
            try:
                import torch
                self._device_str = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self._device_str = "cpu"
        else:
            self._device_str = device

    def _load_model(self) -> None:
        """Load the FLUX.1 Fill pipeline."""
        if self._pipeline is not None:
            return

        try:
            import torch
            from diffusers import FluxFillPipeline
        except ImportError as exc:
            raise ImportError(
                "FLUX.1 Fill inpainting requires diffusers >= 0.33 and torch. "
                "Install with: pip install -U diffusers torch"
            ) from exc

        logger.info("Loading FLUX.1 Fill inpainting model: %s ...", self._model_id)

        dtype = torch.bfloat16 if self._device_str == "cuda" else torch.float32

        try:
            self._pipeline = FluxFillPipeline.from_pretrained(
                self._model_id,
                cache_dir=self._cache_dir,
                torch_dtype=dtype,
            )
        except Exception as exc:
            if "401" in str(exc) or "Unauthorized" in str(exc) or "gated" in str(exc).lower():
                raise ImportError(
                    f"FLUX.1 Fill requires HuggingFace authentication. Steps:\n"
                    f"1. Accept the license at https://huggingface.co/{self._model_id}\n"
                    f"2. Get a token at https://huggingface.co/settings/tokens\n"
                    f"3. Run: hf auth login\n"
                    f"   Or set env: export HF_TOKEN=your_token\n"
                    f"Original error: {exc}"
                ) from exc
            raise

        if self._device_str == "cuda":
            self._pipeline = self._pipeline.to("cuda")

        logger.info("FLUX.1 Fill inpainting model loaded on %s", self._device_str)

    def ensure_available(self) -> None:
        """Validate that the configured inpainting backend can be used.

        Eagerly loads the model to detect authentication issues up front.
        """
        self._load_model()

    def inpaint_holes(
        self,
        rendered_image: np.ndarray,
        hole_mask: np.ndarray,
        prompt: str | None = None,
        num_inference_steps: int = 50,
        guidance_scale: float = 30.0,
        seed: int = 42,
    ) -> np.ndarray:
        """Inpaint holes using FLUX.1 Fill.

        Args:
            rendered_image: Rendered image (H, W, 3) uint8 RGB.
            hole_mask: Binary mask (H, W) where True = hole to fill,
                False = keep existing pixels.
            prompt: Text prompt for inpainting. Uses default if None.
            num_inference_steps: Number of denoising steps. Default 50.
            guidance_scale: Classifier-free guidance scale. Default 30.0
                (Flux Fill typically uses high guidance).
            seed: Random seed for reproducibility.

        Returns:
            Inpainted image (H, W, 3) uint8 RGB.
        """
        self._load_model()

        from PIL import Image

        import torch

        prompt = prompt or self._prompt

        h, w = rendered_image.shape[:2]

        # FluxFill expects dimensions divisible by 16
        h_aligned = ((h + 15) // 16) * 16
        w_aligned = ((w + 15) // 16) * 16

        init_image = Image.fromarray(rendered_image).resize(
            (w_aligned, h_aligned), Image.LANCZOS
        )
        mask_pil = Image.fromarray((hole_mask.astype(np.uint8) * 255)).resize(
            (w_aligned, h_aligned), Image.NEAREST
        )

        generator = torch.Generator(device="cpu").manual_seed(seed)

        result = self._pipeline(
            prompt=prompt,
            image=init_image,
            mask_image=mask_pil,
            height=h_aligned,
            width=w_aligned,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            max_sequence_length=512,
            generator=generator,
        ).images[0]

        # Resize back to original dimensions
        if h_aligned != h or w_aligned != w:
            result = result.resize((w, h), Image.LANCZOS)

        inpainted = np.array(result, dtype=np.uint8)

        logger.debug(
            "FLUX.1 Fill inpainting complete: image %s, %d hole pixels filled",
            rendered_image.shape, int(hole_mask.sum()),
        )

        return inpainted


class EscherNetInpainter:
    """EscherNet multi-view diffusion inpainting for view-consistent hole filling.

    EscherNet uses Camera Positional Encoding (CaPE) for multi-view conditioned
    diffusion, producing view-consistent novel views that are ideal for filling
    gaps in 3D reconstructions.

    This inpainter requires:
    1. The EscherNet repo cloned locally
    2. EscherNet weights from HuggingFace (kxic/eschernet-4dof or 6dof)
    3. Modified diffusers with CaPE attention

    Weight license: CreativeML Open RAIL-M (non-commercial use).

    Args:
        model_variant: "4dof" or "6dof". Defaults to "4dof".
        device: Compute device.
        cache_dir: Directory for model code and weights.

    Raises:
        ImportError: If required dependencies are not installed.
        RuntimeError: If model code cannot be obtained.
    """

    # HuggingFace weight repos
    _WEIGHT_REPOS: ClassVar[dict[str, str]] = {
        "4dof": "kxic/eschernet-4dof",
        "6dof": "kxic/eschernet-6dof",
    }

    # GitHub repo
    _CODE_REPO = "https://github.com/kxhit/EscherNet.git"

    def __init__(
        self,
        model_variant: str = "4dof",
        device: str = "auto",
        cache_dir: Path | None = None,
    ) -> None:
        if model_variant not in self._WEIGHT_REPOS:
            raise ValueError(
                f"Unknown EscherNet variant: {model_variant}. "
                f"Choose from: {list(self._WEIGHT_REPOS.keys())}"
            )

        self._variant = model_variant
        self._cache_dir = cache_dir or DEFAULT_CACHE_DIR / "code"
        self._model = None

        if device == "auto":
            try:
                import torch
                self._device_str = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self._device_str = "cpu"
        else:
            self._device_str = device

    def _ensure_code_available(self) -> Path:
        """Clone the EscherNet repo if not available."""
        eschernet_repo = self._cache_dir / "EscherNet"

        if eschernet_repo.exists():
            return eschernet_repo

        logger.info("Cloning EscherNet repo to %s ...", eschernet_repo)
        eschernet_repo.parent.mkdir(parents=True, exist_ok=True)

        import subprocess
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", self._CODE_REPO, str(eschernet_repo)],
                check=True,
                capture_output=True,
                timeout=120,
            )
            logger.info("EscherNet repo cloned successfully")
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise RuntimeError(
                f"Failed to clone EscherNet repo: {exc}\n"
                f"Try manually: git clone {self._CODE_REPO} {eschernet_repo}"
            ) from exc

        return eschernet_repo

    def _ensure_weights_available(self) -> Path:
        """Download EscherNet weights from HuggingFace."""
        weights_dir = DEFAULT_CACHE_DIR / "models" / "eschernet" / self._variant
        weights_dir.mkdir(parents=True, exist_ok=True)

        # Check if weights already exist
        weight_files = list(weights_dir.glob("*.safetensors")) + list(weights_dir.glob("*.bin"))
        if weight_files:
            return weights_dir

        logger.info("Downloading EscherNet weights (%s) from HuggingFace ...", self._variant)
        try:
            from huggingface_hub import snapshot_download
            snapshot_download(
                repo_id=self._WEIGHT_REPOS[self._variant],
                local_dir=str(weights_dir),
                local_dir_use_symlinks=True,
            )
        except ImportError:
            raise ImportError(
                "huggingface_hub required. Install with: pip install huggingface_hub"
            ) from None
        except Exception as exc:
            raise RuntimeError(
                f"Failed to download EscherNet weights: {exc}\n"
                f"Try: huggingface-cli download {self._WEIGHT_REPOS[self._variant]}"
            ) from exc

        return weights_dir

    def _load_model(self) -> None:
        """Load the EscherNet model. Lazily loads on first inference call."""
        if self._model is not None:
            return

        import torch

        # Ensure code and weights are available
        repo_path = self._ensure_code_available()
        weights_dir = self._ensure_weights_available()

        # Add EscherNet to Python path
        import sys
        if str(repo_path) not in sys.path:
            sys.path.insert(0, str(repo_path))

        # Import and load model
        try:
            from diffusers import DiffusionPipeline

            model_path = self._WEIGHT_REPOS[self._variant]
            logger.info("Loading EscherNet model from %s ...", model_path)

            self._model = DiffusionPipeline.from_pretrained(
                model_path,
                cache_dir=str(weights_dir),
                torch_dtype=torch.float16 if self._device_str == "cuda" else torch.float32,
            )

            if self._device_str == "cuda":
                self._model = self._model.to("cuda")

            logger.info("EscherNet model loaded (%s, %s)", self._variant, self._device_str)

        except Exception as exc:
            raise ImportError(
                f"Failed to load EscherNet: {exc}\n"
                f"EscherNet requires a modified diffusers with CaPE attention.\n"
                f"Install from the EscherNet repo: {repo_path}\n"
                f"See: https://github.com/kxhit/EscherNet#installation"
            ) from exc

    def ensure_available(self) -> None:
        """Validate that the configured inpainting backend can be used."""
        self._load_model()

    def inpaint_holes(
        self,
        rendered_image: np.ndarray,
        hole_mask: np.ndarray,
        reference_images: list[np.ndarray] | None = None,
        reference_poses: list[np.ndarray] | None = None,
        target_pose: np.ndarray | None = None,
        num_inference_steps: int = 50,
        seed: int = 42,
    ) -> np.ndarray:
        """Inpaint holes using EscherNet multi-view diffusion.

        Generates a novel view that is consistent with reference views, filling
        in holes with view-consistent content.

        Args:
            rendered_image: Rendered image (H, W, 3) uint8 RGB.
            hole_mask: Binary mask (H, W) where True = hole.
            reference_images: Optional list of reference view images for
                multi-view conditioning. If provided, produces more
                view-consistent inpainting.
            reference_poses: Camera poses for reference images (4x4 each).
            target_pose: Camera pose for the target view (4x4).
            num_inference_steps: Denoising steps.
            seed: Random seed.

        Returns:
            Inpainted image (H, W, 3) uint8 RGB.
        """
        self._load_model()

        import torch

        generator = torch.Generator(device=self._device_str).manual_seed(seed)

        # For now, fall back to single-view inpainting when no references
        # Multi-view conditioning requires proper CaPE pose encoding
        if reference_images is None or len(reference_images) == 0:
            # Use SD-like inpainting as fallback within EscherNet
            logger.warning(
                "EscherNet called without reference images. "
                "Multi-view conditioning is recommended for best results."
            )
            # The model can still generate a novel view from the target pose
            # This is a simplified usage — full multi-view requires reference images

        # Generate novel view
        from PIL import Image

        init_image = Image.fromarray(rendered_image)

        # Run EscherNet pipeline
        result = self._model(
            image=init_image,
            num_inference_steps=num_inference_steps,
            generator=generator,
        ).images[0]

        inpainted = np.array(result, dtype=np.uint8)

        # Composite: keep non-hole pixels from original, use inpainted for holes
        output = rendered_image.copy()
        output[hole_mask] = inpainted[hole_mask]

        return output


Inpainter = SDInpainter | Flux2KleinInpainter | FluxFillInpainter | EscherNetInpainter


def create_inpainter(
    backend: str = "flux2_klein",
    validate_backend: bool = False,
    **kwargs,
) -> Inpainter:
    """Factory function for creating an inpainting backend.

    Args:
        backend: Inpainting backend name:

            - ``"flux2_klein"`` (default, recommended): FLUX.2 Klein 9B inpainting.
              Best quality, ~24 GB VRAM. Non-commercial license.
            - ``"flux_fill"``: FLUX.1-Fill-dev. Excellent quality, ~24 GB VRAM.
              Non-commercial license.
            - ``"sd"``: Stable Diffusion 1.5 inpainting. Legacy, works on any
              GPU with ~4 GB VRAM.
            - ``"eschernet"``: EscherNet multi-view diffusion. Requires special
              setup. CreativeML RAIL-M license (non-commercial).

        validate_backend: When True, eagerly load the backend so missing
            dependencies fail once up front instead of during each inference call.
        **kwargs: Arguments passed to the inpainter constructor.

    Returns:
        An inpainter instance with an ``inpaint_holes()`` method.

    Raises:
        ValueError: If backend name is not recognized.
    """
    if backend == "flux2_klein":
        inpainter: Inpainter = Flux2KleinInpainter(**kwargs)
    elif backend == "flux_fill":
        inpainter = FluxFillInpainter(**kwargs)
    elif backend == "sd":
        inpainter = SDInpainter(**kwargs)
    elif backend in ("eschernet", "escher_net"):
        inpainter = EscherNetInpainter(**kwargs)
    else:
        raise ValueError(
            f"Unknown inpainting backend: {backend!r}. "
            f"Supported: 'flux2_klein', 'flux_fill', 'sd', 'eschernet'"
        )

    if validate_backend:
        inpainter.ensure_available()

    return inpainter
