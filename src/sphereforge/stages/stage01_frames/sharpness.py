"""Sharpness metric based on variance of the Laplacian.

Provides :func:`compute_sharpness` which computes the variance of the
Laplacian of a grayscale image — a widely-used focus-measure operator
(Pech-Pacheco et al., 2000).
"""

from __future__ import annotations

import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def compute_sharpness(image: np.ndarray) -> float:
    """Compute the sharpness of an image using the variance of the Laplacian.

    The image is first converted to grayscale (if it is colour), then the
    Laplacian is applied and its variance is returned.  Higher values
    indicate sharper (more in-focus) images.

    Args:
        image: Input image as a NumPy array.  Can be either grayscale
            ``(H, W)`` or colour ``(H, W, 3)`` with dtype ``uint8`` or
            ``float``.

    Returns:
        Variance of the Laplacian as a float.  Always non-negative.
    """
    # Convert to grayscale if needed
    if image.ndim == 3:
        if image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        elif image.shape[2] == 1:
            gray = image[:, :, 0]
        else:
            raise ValueError(
                f"Expected 1 or 3 channels, got {image.shape[2]}"
            )
    elif image.ndim == 2:
        gray = image
    else:
        raise ValueError(
            f"Expected 2D (grayscale) or 3D (colour) array, got {image.ndim}D"
        )

    # Ensure uint8 for Laplacian (cv2 expects uint8 or float32)
    if gray.dtype != np.uint8:
        gray = np.clip(gray, 0, 255).astype(np.uint8)

    # Compute Laplacian and its variance
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance: float = float(laplacian.var())

    logger.debug("Sharpness (Laplacian variance): %.2f", variance)
    return variance
