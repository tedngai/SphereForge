"""Stage 2 pipeline: Equirect→Cubemap + COLMAP dataset preparation.

Orchestrates the full Stage 2 workflow: for each input equirectangular
frame, extract diversified cubemap crops, compute camera intrinsics and
extrinsics, generate masks, and write the COLMAP-format dataset to disk.
"""

from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np

from sphereforge.common.colmap_helpers import write_cameras_txt, write_images_txt
from sphereforge.common.io import read_image, write_image
from sphereforge.config import Stage02Config
from sphereforge.stages.stage02_cubemap.extrinsics import compute_extrinsics
from sphereforge.stages.stage02_cubemap.intrinsics import compute_intrinsics
from sphereforge.stages.stage02_cubemap.masking import (
    combine_masks,
    generate_overexposure_masks,
    generate_yolo_masks,
)
from sphereforge.stages.stage02_cubemap.yaw_diversify import (
    apply_yaw_offset,
    extract_diversified_cubemaps,
)

logger = logging.getLogger("sphereforge.stage02.pipeline")


def run_stage02(
    config: Stage02Config,
    frame_paths: list[Path],
    output_dir: Path,
) -> Path:
    """Run the full Stage 2 pipeline: equirect→cubemap + COLMAP prep.

    For each input frame:
    1. Extract diversified cubemap crops (yaw offset per frame index).
    2. Compute PINHOLE camera intrinsics (shared across all crops).
    3. Compute per-face extrinsics (quaternion + translation).
    4. Generate YOLO + overexposure masks and combine them.
    5. Write images, masks, cameras.txt, and images.txt to *output_dir*.

    Output directory structure::

        output_dir/
        ├── images/
        │   ├── frame_000_front.png
        │   ├── frame_000_right.png
        │   └── ...
        ├── masks/
        │   ├── frame_000_front.png
        │   ├── frame_000_right.png
        │   └── ...
        ├── cameras.txt
        └── images.txt

    Args:
        config: Stage02 configuration.
        frame_paths: List of paths to equirectangular input frames.
        output_dir: Root directory for Stage 2 output.

    Returns:
        Path to the output directory.
    """
    output_dir = Path(output_dir)
    images_dir = output_dir / "images"
    masks_dir = output_dir / "masks"
    images_dir.mkdir(parents=True, exist_ok=True)
    masks_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Starting Stage 2: %d frames, fov=%d, overlap=%d, "
        "crop_resolution=%d, generate_masks=%s",
        len(frame_paths),
        config.fov,
        config.overlap,
        config.crop_resolution,
        config.generate_masks,
    )

    # Compute shared intrinsics (all crops use the same camera model).
    # Use the effective FOV (fov + overlap) since the extracted crops
    # cover the total field of view.
    total_fov = config.fov + config.overlap

    # Read the first frame to determine source dimensions
    first_erp = read_image(frame_paths[0])
    intrinsic_info = compute_intrinsics(
        crop_resolution=config.crop_resolution,
        source_width=first_erp.shape[1],
        source_height=first_erp.shape[0],
        fov=total_fov,
    )

    # COLMAP cameras dict (single shared camera)
    cameras_dict: dict[int, dict] = {1: intrinsic_info}

    # COLMAP images dict
    images_dict: dict[int, dict] = {}

    global_image_id = 1

    for frame_idx, frame_path in enumerate(frame_paths):
        logger.info(
            "Processing frame %d/%d: %s",
            frame_idx + 1,
            len(frame_paths),
            frame_path.name,
        )

        # Read equirectangular frame (reuse first frame already in memory)
        if frame_idx == 0:
            erp_image = first_erp
        else:
            erp_image = read_image(frame_path)
        frame_stem = frame_path.stem

        # Extract diversified cubemap crops
        crops = extract_diversified_cubemaps(
            erp_image=erp_image,
            frame_index=frame_idx,
            config=config,
        )

        # Resize crops to crop_resolution if needed and collect images
        resized_crops: list[np.ndarray] = []
        for crop_img, _face_name, _yaw_deg, _pitch_deg in crops:
            if (
                crop_img.shape[0] != config.crop_resolution
                or crop_img.shape[1] != config.crop_resolution
            ):
                crop_img = cv2.resize(
                    crop_img,
                    (config.crop_resolution, config.crop_resolution),
                    interpolation=cv2.INTER_LINEAR,
                )
            resized_crops.append(crop_img)

        # Generate masks
        if config.generate_masks:
            yolo_masks = generate_yolo_masks(
                resized_crops, classes=config.mask_classes
            )
            overexposure_masks = generate_overexposure_masks(
                resized_crops, threshold=config.overexposure_threshold
            )
            final_masks = combine_masks(yolo_masks, overexposure_masks)
        else:
            final_masks = [
                np.zeros(c.shape[:2], dtype=np.uint8) for c in resized_crops
            ]

        # Compute yaw offset for this frame's extrinsics
        yaw_offset = apply_yaw_offset(frame_idx, config.yaw_offset_step)

        # Write crops and masks, and populate COLMAP image entries
        for i, ((crop_img, face_name, yaw_deg, pitch_deg), mask) in enumerate(
            zip(crops, final_masks)
        ):
            # Resize crop if needed (same as above for the mask-sized version)
            if (
                crop_img.shape[0] != config.crop_resolution
                or crop_img.shape[1] != config.crop_resolution
            ):
                crop_img = cv2.resize(
                    crop_img,
                    (config.crop_resolution, config.crop_resolution),
                    interpolation=cv2.INTER_LINEAR,
                )

            # File naming: frame_stem_face_name.png
            img_filename = f"{frame_stem}_{face_name}.png"
            mask_filename = f"{frame_stem}_{face_name}.png"

            # Write image and mask
            write_image(images_dir / img_filename, crop_img)
            write_image(masks_dir / mask_filename, mask)

            # Compute extrinsics
            extrinsic = compute_extrinsics(
                face_name=face_name,
                yaw_offset=yaw_offset,
                image_id=global_image_id,
                camera_id=1,
            )

            # Store in COLMAP images dict
            images_dict[global_image_id] = {
                "name": f"images/{img_filename}",
                "qw": extrinsic["qw"],
                "qx": extrinsic["qx"],
                "qy": extrinsic["qy"],
                "qz": extrinsic["qz"],
                "tx": extrinsic["tx"],
                "ty": extrinsic["ty"],
                "tz": extrinsic["tz"],
                "camera_id": extrinsic["camera_id"],
                "point3D_ids": [],
            }

            logger.debug(
                "Wrote %s (image_id=%d, face=%s, yaw=%.1f)",
                img_filename,
                global_image_id,
                face_name,
                yaw_deg,
            )

            global_image_id += 1

    # Write COLMAP text files
    write_cameras_txt(output_dir / "cameras.txt", cameras_dict)
    write_images_txt(output_dir / "images.txt", images_dict)

    logger.info(
        "Stage 2 complete: %d images, %d cameras, output at %s",
        len(images_dict),
        len(cameras_dict),
        output_dir,
    )

    return output_dir