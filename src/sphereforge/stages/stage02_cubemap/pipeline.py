"""Stage 2 pipeline: Equirect→Cubemap + COLMAP dataset preparation.

Orchestrates the full Stage 2 workflow: for each input equirectangular
frame, extract diversified cubemap crops, compute camera intrinsics and
extrinsics, generate masks, and write the COLMAP-format dataset to disk.
"""

from __future__ import annotations

import json
import logging
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Any

import cv2
import numpy as np

from sphereforge.common.colmap_helpers import (
    rotation_matrix_to_quat,
    write_cameras_txt,
    write_images_txt,
)
from sphereforge.common.io import read_image, write_image
from sphereforge.stages.stage02_cubemap.cubemap import _make_rotation_matrix
from sphereforge.stages.stage02_cubemap.extrinsics import compute_extrinsics
from sphereforge.stages.stage02_cubemap.intrinsics import compute_intrinsics
from sphereforge.stages.stage02_cubemap.masking import (
    combine_masks,
    generate_overexposure_masks,
    generate_yolo_masks,
)
from sphereforge.stages.stage02_cubemap.panorama_rig import (
    PanoramaRigCamera,
    build_panorama_rig_cameras,
    compute_panorama_rig_assignment_masks,
    extract_panorama_rig_views,
)
from sphereforge.stages.stage02_cubemap.yaw_diversify import (
    apply_yaw_offset,
    extract_diversified_cubemaps,
)

if TYPE_CHECKING:
    from sphereforge.config import Stage02Config

logger = logging.getLogger("sphereforge.stage02.pipeline")


def _write_panorama_rig_manifest(
    output_dir: Path,
    cameras: list[PanoramaRigCamera],
    config: Stage02Config,
) -> Path:
    """Persist panorama-rig metadata for Stage 3 orchestration."""
    manifest_path = output_dir / "panorama_rig.json"
    payload = {
        "projection_layout": config.projection_layout,
        "fov": config.fov,
        "overlap": config.overlap,
        "crop_resolution": config.crop_resolution,
        "cameras": [
            {
                "name": camera.name,
                "yaw_deg": camera.yaw_deg,
                "pitch_deg": camera.pitch_deg,
                "camera_id": camera.camera_id,
            }
            for camera in cameras
        ],
    }
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return manifest_path


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
    assignment_masks: list[np.ndarray] | None = None

    if config.projection_layout == "panorama_rig":
        crops = [
            (
                crop_img,
                camera.name,
                camera.yaw_deg,
                camera.pitch_deg,
                camera.camera_id,
            )
            for crop_img, camera in extract_panorama_rig_views(erp_image, config)
        ]
        if config.rig_use_assignment_masks:
            rig_assignment_masks = compute_panorama_rig_assignment_masks(erp_image, config)
            assignment_masks = [mask for _camera, mask in rig_assignment_masks]
    else:
        crops = [
            (crop_img, face_name, yaw_deg, pitch_deg, 1)
            for crop_img, face_name, yaw_deg, pitch_deg in extract_diversified_cubemaps(
                erp_image=erp_image,
                frame_index=frame_idx,
                config=config,
            )
        ]

    # Resize crops to crop_resolution if needed
    resized_crops: list[np.ndarray] = []
    resized_assignment_masks: list[np.ndarray] | None = [] if assignment_masks is not None else None
    for crop_idx, (crop_img, _view_name, _yaw_deg, _pitch_deg, _camera_id) in enumerate(crops):
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
        if assignment_masks is not None and resized_assignment_masks is not None:
            assignment_mask = assignment_masks[crop_idx]
            if assignment_mask.shape != crop_img.shape[:2]:
                assignment_mask = cv2.resize(
                    assignment_mask,
                    (crop_img.shape[1], crop_img.shape[0]),
                    interpolation=cv2.INTER_NEAREST,
                )
            resized_assignment_masks.append(assignment_mask)

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

    if resized_assignment_masks is not None:
        final_masks = combine_masks(final_masks, resized_assignment_masks)

    yaw_offset = 0.0
    if config.projection_layout != "panorama_rig":
        yaw_offset = apply_yaw_offset(frame_idx, config.yaw_offset_step)

    image_entries: list[dict[str, Any]] = []

    for (_, view_name, yaw_deg, pitch_deg, camera_id), crop_img, mask in zip(
        crops, resized_crops, final_masks, strict=True
    ):
        if config.projection_layout == "panorama_rig":
            rel_filename = Path(view_name) / f"{frame_stem}.png"
        else:
            rel_filename = Path(f"{frame_stem}_{view_name}.png")

        write_image(images_dir / rel_filename, crop_img)
        write_image(masks_dir / rel_filename, mask)

        extrinsic = compute_extrinsics(
            face_name=view_name if config.projection_layout != "panorama_rig" else "front",
            yaw_offset=yaw_offset,
            image_id=0,  # placeholder
            camera_id=camera_id,
        )

        if config.projection_layout == "panorama_rig":
            extrinsic = {
                **extrinsic,
                **_compute_panorama_rig_extrinsics(yaw_deg, pitch_deg, camera_id),
            }

        image_entries.append({
            "name": f"images/{rel_filename.as_posix()}",
            "qw": extrinsic["qw"],
            "qx": extrinsic["qx"],
            "qy": extrinsic["qy"],
            "qz": extrinsic["qz"],
            "tx": extrinsic["tx"],
            "ty": extrinsic["ty"],
            "tz": extrinsic["tz"],
            "camera_id": extrinsic["camera_id"],
            "point3D_ids": [],
            "_debug_face": view_name,
            "_debug_yaw": yaw_deg,
            "_debug_pitch": pitch_deg,
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
        "Starting Stage 2: %d frames, layout=%s, fov=%d, overlap=%d, "
        "crop_resolution=%d, generate_masks=%s, workers=%d",
        len(frame_paths),
        config.projection_layout,
        config.fov,
        config.overlap,
        config.crop_resolution,
        config.generate_masks,
        num_workers,
    )

    total_fov = config.fov + config.overlap
    first_erp = read_image(frame_paths[0])
    intrinsic_info = compute_intrinsics(
        crop_resolution=config.crop_resolution,
        source_width=first_erp.shape[1],
        source_height=first_erp.shape[0],
        fov=total_fov,
    )

    if config.projection_layout == "panorama_rig":
        rig_cameras = build_panorama_rig_cameras(config)
        cameras_dict: dict[int, dict] = {
            camera.camera_id: {
                **intrinsic_info,
                "camera_id": camera.camera_id,
            }
            for camera in rig_cameras
        }
        if config.yaw_offset_step != 0:
            logger.info(
                "Stage 2 panorama_rig uses a fixed virtual rig; ignoring yaw_offset_step=%d",
                config.yaw_offset_step,
            )
        _write_panorama_rig_manifest(output_dir, rig_cameras, config)
    else:
        cameras_dict = {1: intrinsic_info}
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
                "Wrote %s (image_id=%d, view=%s, yaw=%.1f)",
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


def _compute_panorama_rig_extrinsics(
    yaw_deg: float,
    pitch_deg: float,
    camera_id: int,
) -> dict[str, float | int]:
    """Compute world-to-camera extrinsics for a fixed panorama-rig view."""
    rotation = _make_rotation_matrix(yaw_deg, pitch_deg)
    qw, qx, qy, qz = rotation_matrix_to_quat(rotation)
    return {
        "qw": qw,
        "qx": qx,
        "qy": qy,
        "qz": qz,
        "tx": 0.0,
        "ty": 0.0,
        "tz": 0.0,
        "camera_id": camera_id,
    }


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
