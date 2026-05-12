"""Dynamic-object and overexposure masking for cubemap crops.

Generates binary masks (255 = masked/invalid, 0 = valid) from YOLO
object detection and overexposure detection.  The two mask types are
combined via pixel-wise union before being saved alongside the crops.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger("sphereforge.stage02.masking")


def generate_yolo_masks(
    crops: list[np.ndarray],
    classes: list[str] | None = None,
) -> list[np.ndarray]:
    """Run YOLO on each crop and produce binary object masks.

    Uses the ``ultralytics`` package if available; otherwise returns
    all-zero masks (no masking) so the pipeline can proceed without
    the optional dependency.

    Args:
        crops: List of crop images, each (H, W, 3) uint8.
        classes: YOLO class names to mask out.  Defaults to
            ``["person", "vehicle"]``.

    Returns:
        List of binary mask arrays, each (H, W) uint8, where 255
        indicates a masked (invalid) pixel and 0 indicates a valid pixel.
    """
    if classes is None:
        classes = ["person", "vehicle"]

    _h, _w = crops[0].shape[:2] if crops else 0, 0
    if not crops:
        return []

    # Attempt to import ultralytics
    try:
        from ultralytics import YOLO
    except ImportError:
        logger.warning(
            "ultralytics not installed — returning all-zero YOLO masks. "
            "Install with: pip install ultralytics"
        )
        return [np.zeros(c.shape[:2], dtype=np.uint8) for c in crops]

    logger.info("Running YOLO masking for %d classes on %d crops", len(classes), len(crops))

    # Load the default YOLO model (yolov8n is the smallest)
    model = YOLO("yolov8n.pt")

    # Map class names to YOLO class IDs
    class_name_to_id: dict[str, int] = {}
    for idx, name in enumerate(model.names.values()):
        if name in classes:
            class_name_to_id[name] = idx

    if not class_name_to_id:
        logger.warning(
            "None of the requested classes %s found in YOLO model. "
            "Returning all-zero masks.",
            classes,
        )
        return [np.zeros(c.shape[:2], dtype=np.uint8) for c in crops]

    target_class_ids = set(class_name_to_id.values())

    masks: list[np.ndarray] = []
    for i, crop in enumerate(crops):
        mask = np.zeros(crop.shape[:2], dtype=np.uint8)

        # Run inference
        results = model(crop, verbose=False)

        for result in results:
            if result.boxes is None:
                continue
            boxes = result.boxes
            for box_idx in range(len(boxes)):
                cls_id = int(boxes.cls[box_idx])
                if cls_id not in target_class_ids:
                    continue
                conf = float(boxes.conf[box_idx])
                if conf < 0.25:
                    continue
                # Get the segmentation mask if available
                if result.masks is not None and box_idx < len(result.masks):
                    seg_mask = result.masks.data[box_idx].cpu().numpy()
                    # Resize mask to crop size if needed
                    if seg_mask.shape != crop.shape[:2]:
                        import cv2

                        seg_mask = cv2.resize(
                            seg_mask.astype(np.float32),
                            (crop.shape[1], crop.shape[0]),
                        )
                    mask[seg_mask > 0.5] = 255
                else:
                    # Fall back to bounding box
                    x1, y1, x2, y2 = map(int, boxes.xyxy[box_idx].cpu().numpy())
                    x1, y1 = max(0, x1), max(0, y1)
                    x2 = min(crop.shape[1], x2)
                    y2 = min(crop.shape[0], y2)
                    mask[y1:y2, x1:x2] = 255

        masks.append(mask)
        logger.debug(
            "Crop %d: %d/%d pixels masked by YOLO",
            i,
            int(np.count_nonzero(mask)),
            mask.size,
        )

    return masks


def generate_overexposure_masks(
    crops: list[np.ndarray],
    threshold: int = 250,
) -> list[np.ndarray]:
    """Detect overexposed pixels in each crop and return binary masks.

    A pixel is considered overexposed if **all** three channel values
    exceed *threshold*.

    Args:
        crops: List of crop images, each (H, W, 3) uint8.
        threshold: Per-channel brightness threshold (0-255).

    Returns:
        List of binary mask arrays, each (H, W) uint8, where 255
        indicates an overexposed pixel and 0 indicates a valid pixel.
    """
    masks: list[np.ndarray] = []
    for i, crop in enumerate(crops):
        # Overexposed: all channels above threshold
        overexposed = np.all(crop > threshold, axis=-1)
        mask = np.zeros(crop.shape[:2], dtype=np.uint8)
        mask[overexposed] = 255
        masks.append(mask)

        n_overexposed = int(np.count_nonzero(overexposed))
        total = crop.shape[0] * crop.shape[1]
        logger.debug(
            "Crop %d: %d/%d pixels overexposed (threshold=%d)",
            i,
            n_overexposed,
            total,
            threshold,
        )

    return masks


def combine_masks(
    masks_a: list[np.ndarray],
    masks_b: list[np.ndarray],
) -> list[np.ndarray]:
    """Combine two mask lists via pixel-wise union (OR).

    Both lists must have the same length.  For each index, the result
    mask is 255 wherever either input mask is 255.

    Args:
        masks_a: First list of (H, W) uint8 masks.
        masks_b: Second list of (H, W) uint8 masks.

    Returns:
        List of combined (H, W) uint8 masks.

    Raises:
        ValueError: If the two lists have different lengths.
    """
    if len(masks_a) != len(masks_b):
        raise ValueError(
            f"Mask lists must have the same length, got "
            f"{len(masks_a)} and {len(masks_b)}"
        )

    combined: list[np.ndarray] = []
    for _i, (a, b) in enumerate(zip(masks_a, masks_b, strict=False)):
        combined_mask = np.maximum(a, b)
        combined.append(combined_mask)

    return combined
