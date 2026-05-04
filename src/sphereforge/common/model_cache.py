"""SphereForge model weight download and caching.

Provides utilities to download model weights on first use and cache them
in a configurable directory (default: ~/.cache/sphereforge/models/).
"""

from __future__ import annotations

import hashlib
import logging
import shutil
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "sphereforge" / "models"


def get_model_path(
    model_name: str,
    filename: str,
    cache_dir: Path | None = None,
) -> Path:
    """Get the local path for a model weight file.

    Does NOT download — just returns where it would be cached.
    Use ``download_if_missing`` to ensure the file exists.

    Args:
        model_name: Name of the model (e.g. "panda", "metric3d_v2").
        filename: Specific weight file name (e.g. "model.safetensors").
        cache_dir: Root cache directory. Defaults to ~/.cache/sphereforge/models/.

    Returns:
        Path to the cached weight file.
    """
    base = cache_dir or DEFAULT_CACHE_DIR
    return base / model_name / filename


def download_if_missing(
    model_name: str,
    filename: str,
    url: str,
    cache_dir: Path | None = None,
    expected_sha256: str | None = None,
    force: bool = False,
) -> Path:
    """Download a model weight file if not already cached.

    Supports downloading from HTTP(S) URLs or HuggingFace repos.

    Args:
        model_name: Name of the model (e.g. "panda", "metric3d_v2").
        filename: Specific weight file name.
        url: Direct download URL or HuggingFace repo identifier.
            Must be a non-empty string.
        cache_dir: Root cache directory.
        expected_sha256: Optional SHA-256 hex digest for integrity check.
        force: If True, re-download even if file exists.

    Returns:
        Path to the cached weight file.

    Raises:
        RuntimeError: If download fails or integrity check fails.
    """
    if not url:
        raise ValueError("url must be a non-empty string")
    target = get_model_path(model_name, filename, cache_dir)

    if target.exists() and not force:
        logger.debug("Model weight already cached: %s", target)
        if expected_sha256:
            if _sha256_file(target) == expected_sha256:
                return target
            logger.warning("SHA-256 mismatch for %s, re-downloading", target)
        else:
            return target

    target.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading model weight: %s/%s", model_name, filename)

    if url:
        _download_url(url, target)
    else:
        _download_huggingface(model_name, filename, target)

    # Integrity check
    if expected_sha256:
        actual = _sha256_file(target)
        if actual != expected_sha256:
            target.unlink(missing_ok=True)
            raise RuntimeError(
                f"SHA-256 integrity check failed for {target}. "
                f"Expected {expected_sha256}, got {actual}"
            )

    logger.info("Model weight cached: %s", target)
    return target


def _download_url(url: str, target: Path) -> None:
    """Download a file from a direct URL."""
    try:
        from urllib.request import urlretrieve

        urlretrieve(url, str(target))
    except Exception as e:
        raise RuntimeError(f"Failed to download {url}: {e}") from e


def _download_huggingface(repo_id: str, filename: str, target: Path) -> None:
    """Download a file from a HuggingFace repository."""
    try:
        from huggingface_hub import hf_hub_download

        downloaded = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            cache_dir=str(target.parent.parent),
        )
        src = Path(downloaded)
        if src != target:
            shutil.copy2(src, target)
    except ImportError:
        raise FileNotFoundError(
            f"Cannot download {repo_id}/{filename}: "
            f"huggingface_hub package not installed. "
            f"Install with: pip install huggingface_hub"
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to download {repo_id}/{filename} from HuggingFace: {e}"
        ) from e


def _sha256_file(path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def list_cached_models(cache_dir: Path | None = None) -> dict[str, list[str]]:
    """List all cached model weights.

    Args:
        cache_dir: Root cache directory.

    Returns:
        Dict mapping model_name -> list of cached filenames.
    """
    base = cache_dir or DEFAULT_CACHE_DIR
    if not base.exists():
        return {}

    models: dict[str, list[str]] = {}
    for model_dir in sorted(base.iterdir()):
        if model_dir.is_dir():
            files = sorted(f.name for f in model_dir.iterdir() if f.is_file())
            if files:
                models[model_dir.name] = files
    return models


def clear_cache(model_name: str | None = None, cache_dir: Path | None = None) -> None:
    """Clear cached model weights.

    Args:
        model_name: If provided, clear only this model's cache.
            If None, clear the entire cache directory.
        cache_dir: Root cache directory.
    """
    base = cache_dir or DEFAULT_CACHE_DIR
    if model_name:
        target = base / model_name
        if target.exists():
            shutil.rmtree(target)
            logger.info("Cleared cache for model: %s", model_name)
    else:
        if base.exists():
            shutil.rmtree(base)
            logger.info("Cleared entire model cache: %s", base)
