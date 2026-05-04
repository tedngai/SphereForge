"""Stage 2 pipeline: Equirect→Cubemap + COLMAP dataset preparation.

Orchestrates the full Stage 2 workflow: for each input equirectangular
frame, extract diversified cubemap crops, compute camera intrinsics and
extrinsics, generate masks, and write the COLMAP-format dataset to disk.
"""

from __future__ import annotations

import logging
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

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


def _process_single_frame(
    frame_path: Path,
    frame_idx: int,
    config: Stage02Config,
    images_dir: Path,
    masks_dir: Path,
) -> list[dict[str, Any]]:
    """Process one frame: extract crops, generate masks, write files.

    Returns a list of COLMAP image dicts (one per face) with a
    placeholder ``image_id`` of 0.  The caller assigns real IDs.
    """
    erp_image = read_image(frame_path)
    frame_stem = Path(frame_path).stem

    # Extract diversified cubemap crops
    crops = extract_diversified_cubemaps(
        erp_image=erp_image,
        frame_index=frame_idx,
        config=config,
    )

    # Resize crops to crop_resolution if needed
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

    image_entries: list[dict[str, Any]] = []

    for (_, face_name, yaw_deg, _pitch_deg), crop_img, mask in zip(
        crops, resized_crops, final_masks, strict=True
    ):
        img_filename = f"{frame_stem}_{face_name}.png"
        mask_filename = f"{frame_stem}_{face_name}.png"

        write_image(images_dir / img_filename, crop_img)
        write_image(masks_dir / mask_filename, mask)

        extrinsic = compute_extrinsics(
            face_name=face_name,
            yaw_offset=yaw_offset,
            image_id=0,  # placeholder
            camera_id=1,
        )

        image_entries.append({
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
            "_debug_face": face_name,
            "_debug_yaw": yaw_deg,
        })

    return image_entries


def run_stage02(
    config: Stage02Config,
    frame_paths: list[Path],
    output_dir: Path,
    num_workers: int = 1,
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
        num_workers: Parallel workers for frame processing (1 = serial).

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
        "crop_resolution=%d, generate_masks=%s, workers=%d",
        len(frame_paths),
        config.fov,
        config.overlap,
        config.crop_resolution,
        config.generate_masks,
        num_workers,
    )

    # Compute shared intrinsics (all crops use the same camera model).
    total_fov = config.fov + config.overlap

    first_erp = read_image(frame_paths[0])
    intrinsic_info = compute_intrinsics(
        crop_resolution=config.crop_resolution,
        source_width=first_erp.shape[1],
        source_height=first_erp.shape[0],
        fov=total_fov,
    )

    cameras_dict: dict[int, dict] = {1: intrinsic_info}
    images_dict: dict[int, dict] = {}

    if num_workers > 1:
        logger.info("Using %d parallel workers for cubemap extraction", num_workers)
        args = [
            (fp, idx, config, images_dir, masks_dir)
            for idx, fp in enumerate(frame_paths)
        ]
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            all_entries = list(executor.map(_process_single_frame_worker, args))
    else:
        all_entries = []
        for idx, fp in enumerate(frame_paths):
            all_entries.append(
                _process_single_frame(fp, idx, config, images_dir, masks_dir)
            )

    # Assign sequential image IDs
    global_image_id = 1
    for entries in all_entries:
        for entry in entries:
            images_dict[global_image_id] = {
                "name": entry["name"],
                "qw": entry["qw"],
                "qx": entry["qx"],
                "qy": entry["qy"],
                "qz": entry["qz"],
                "tx": entry["tx"],
                "ty": entry["ty"],
                "tz": entry["tz"],
                "camera_id": entry["camera_id"],
                "point3D_ids": entry["point3D_ids"],
            }
            logger.debug(
                "Wrote %s (image_id=%d, face=%s, yaw=%.1f)",
                entry["name"],
                global_image_id,
                entry["_debug_face"],
                entry["_debug_yaw"],
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


def _process_single_frame_worker(
    args: tuple[Path, int, Stage02Config, Path, Path],
) -> list[dict[str, Any]]:
    """Picklable wrapper for ``_process_single_frame``.

    ProcessPoolExecutor requires a top-level function; this unwraps the
    tuple arguments and delegates to the real implementation.
    """
    frame_path, frame_idx, config, images_dir, masks_dir = args
    return _process_single_frame(
        frame_path, frame_idx, config, images_dir, masks_dir
    )
