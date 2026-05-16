"""Isolated pycolmap panorama-rig probe for Stage 3 debugging."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any

import numpy as np

from sphereforge.common.colmap_helpers import (
    parse_images_txt,
    quat_to_rotation_matrix,
    rotation_matrix_to_quat,
)
from sphereforge.stages.stage03_sfm.model_reader import read_sparse_model

logger = logging.getLogger("sphereforge.stage03.pycolmap_probe")

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def _import_pycolmap() -> Any:
    """Import pycolmap lazily so the main package stays optional."""
    try:
        import pycolmap  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "pycolmap is not installed in the active Python environment. "
            "Run this probe with a Python interpreter that has pycolmap available."
        ) from exc
    return pycolmap


def _camera_name_from_image_name(image_name: str) -> str:
    """Extract the panorama-rig camera folder name from an image path."""
    normalized = _normalize_stage03_image_name(image_name)
    parts = Path(normalized).parts
    if len(parts) < 2:
        raise ValueError(f"Expected panorama-rig image path with a camera folder, got '{image_name}'")
    return parts[-2]


def _normalize_stage03_image_name(image_name: str) -> str:
    """Normalize Stage 2/3 image names to a common relative path form."""
    normalized = image_name.replace("\\", "/")
    if normalized.startswith("images/"):
        normalized = normalized[len("images/") :]
    return normalized


def _list_stage03_input_images(image_dir: Path) -> list[str]:
    """List Stage 2 images that should be eligible for registration."""
    return sorted(
        path.relative_to(image_dir).as_posix()
        for path in image_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in _IMAGE_SUFFIXES
    )


def _load_panorama_rig_manifest(colmap_dataset_dir: Path) -> dict | None:
    """Load panorama-rig metadata if the Stage 2 dataset provides it."""
    manifest_path = colmap_dataset_dir / "panorama_rig.json"
    if not manifest_path.exists():
        return None
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _build_stage03_image_list(image_dir: Path, panorama_rig_manifest: dict | None) -> list[str]:
    """Build the frame-major panorama-rig image ordering used in Stage 3."""
    if panorama_rig_manifest is None:
        return _list_stage03_input_images(image_dir)

    image_sequences: list[list[str]] = []
    for camera in panorama_rig_manifest.get("cameras", []):
        camera_dir = image_dir / camera["name"]
        image_sequences.append(
            sorted(
                path.relative_to(image_dir).as_posix()
                for path in camera_dir.glob("*")
                if path.is_file() and path.suffix.lower() in _IMAGE_SUFFIXES
            )
        )
    ordered_images: list[str] = []
    max_sequence_length = max((len(sequence) for sequence in image_sequences), default=0)
    for frame_idx in range(max_sequence_length):
        for sequence in image_sequences:
            if frame_idx < len(sequence):
                ordered_images.append(sequence[frame_idx])
    return ordered_images


def _write_stage03_diagnostics(image_dir: Path, sparse_dir: Path, output_dir: Path, sparse_model: dict) -> dict:
    """Persist a machine-readable Stage 3 registration summary."""
    import cv2

    input_image_names = _list_stage03_input_images(image_dir)
    registered_image_names = sorted(
        _normalize_stage03_image_name(image_entry["name"])
        for image_entry in sparse_model["images"].values()
    )
    registered_name_set = set(registered_image_names)
    all_image_names = sorted(set(input_image_names) | registered_name_set)

    total_input_images = len(input_image_names)
    registered_images = len(registered_image_names)
    registration_fraction = registered_images / total_input_images if total_input_images > 0 else 0.0

    report_path = output_dir / "registration_report.json"
    csv_path = output_dir / "registered_vs_total.csv"
    preview_path = output_dir / "sparse_preview.png"

    report = {
        "total_input_images": total_input_images,
        "registered_images": registered_images,
        "registration_fraction": registration_fraction,
        "sparse_point_count": len(sparse_model["points3D"]),
        "camera_count": len(sparse_model["cameras"]),
        "model_count": 1 if sparse_model["images"] else 0,
        "registered_image_names": registered_image_names,
        "artifacts": {
            "registration_report": str(report_path),
            "registered_vs_total": str(csv_path),
            "sparse_preview": str(preview_path),
        },
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    csv_lines = ["image_name,registered\n"]
    for image_name in all_image_names:
        csv_lines.append(f"{image_name},{int(image_name in registered_name_set)}\n")
    csv_path.write_text("".join(csv_lines), encoding="utf-8")

    canvas = np.full((960, 960, 3), 255, dtype=np.uint8)
    if sparse_model["points3D"]:
        cv2.putText(
            canvas,
            f"points={len(sparse_model['points3D'])} cameras={len(sparse_model['images'])}",
            (24, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (30, 30, 30),
            2,
            cv2.LINE_AA,
        )
    else:
        cv2.putText(
            canvas,
            "No registered geometry",
            (220, 480),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            (40, 40, 40),
            2,
            cv2.LINE_AA,
        )
    cv2.imwrite(str(preview_path), canvas)
    return report


def _frame_name_from_image_name(image_name: str) -> str:
    """Extract the panorama timestamp key from an image path."""
    return Path(_normalize_stage03_image_name(image_name)).stem


def _camera_rotations_from_stage2_images(stage2_images: dict[int, dict]) -> dict[str, tuple[int, np.ndarray]]:
    """Collect one world-to-camera rotation per panorama-rig camera folder."""
    camera_rotations: dict[str, tuple[int, np.ndarray]] = {}
    for image_entry in sorted(stage2_images.values(), key=lambda item: _normalize_stage03_image_name(item["name"])):
        camera_name = _camera_name_from_image_name(image_entry["name"])
        if camera_name in camera_rotations:
            continue
        camera_rotations[camera_name] = (
            int(image_entry["camera_id"]),
            quat_to_rotation_matrix(
                float(image_entry["qw"]),
                float(image_entry["qx"]),
                float(image_entry["qy"]),
                float(image_entry["qz"]),
            ),
        )
    return camera_rotations


def _build_sensor_from_rig_rotations(
    panorama_rig_manifest: dict,
    stage2_images: dict[int, dict],
) -> dict[int, np.ndarray]:
    """Build fixed sensor-from-rig rotations relative to the first rig camera."""
    camera_rotations = _camera_rotations_from_stage2_images(stage2_images)
    rig_cameras = panorama_rig_manifest.get("cameras", [])
    if not rig_cameras:
        raise ValueError("Panorama-rig manifest contains no cameras")

    ref_camera_name = str(rig_cameras[0]["name"])
    if ref_camera_name not in camera_rotations:
        raise ValueError(f"Missing Stage 2 pose for reference rig camera '{ref_camera_name}'")
    ref_rotation = camera_rotations[ref_camera_name][1]

    sensor_from_rig: dict[int, np.ndarray] = {}
    for camera in rig_cameras:
        camera_name = str(camera["name"])
        if camera_name not in camera_rotations:
            raise ValueError(f"Missing Stage 2 pose for rig camera '{camera_name}'")
        camera_id = int(camera["camera_id"])
        camera_rotation = camera_rotations[camera_name][1]
        sensor_from_rig[camera_id] = camera_rotation @ ref_rotation.T
    return sensor_from_rig


def _group_database_images_by_frame(database_images: list[Any]) -> dict[str, list[Any]]:
    """Group database images by panorama timestamp/frame stem."""
    grouped: dict[str, list[Any]] = {}
    for image in sorted(database_images, key=lambda item: int(item.image_id)):
        grouped.setdefault(_frame_name_from_image_name(str(image.name)), []).append(image)
    return grouped


def _pycolmap_sensor(pycolmap: Any, camera_id: int) -> Any:
    """Create a pycolmap camera sensor identifier."""
    sensor = pycolmap.sensor_t()
    sensor.type = pycolmap.SensorType.CAMERA
    sensor.id = int(camera_id)
    return sensor


def _pycolmap_rigid3d(pycolmap: Any, rotation: np.ndarray, translation: np.ndarray | None = None) -> Any:
    """Create a pycolmap rigid transform from a rotation matrix."""
    qw, qx, qy, qz = rotation_matrix_to_quat(rotation)
    transform = pycolmap.Rigid3d()
    transform.rotation.quat = np.array([qx, qy, qz, qw], dtype=np.float64)
    transform.translation = np.zeros(3, dtype=np.float64) if translation is None else np.asarray(translation, dtype=np.float64)
    return transform


def _annotate_database_with_panorama_rig(
    pycolmap: Any,
    database_path: Path,
    panorama_rig_manifest: dict,
    stage2_images: dict[int, dict],
) -> int:
    """Populate pycolmap rig/frame tables for a panorama-rig database."""
    db = pycolmap.Database.open(database_path)
    database_images = db.read_all_images()
    if not database_images:
        db.close()
        raise RuntimeError(f"No images found in COLMAP database {database_path}")

    db.clear_frames()
    db.clear_rigs()

    sensor_from_rig_rotations = _build_sensor_from_rig_rotations(panorama_rig_manifest, stage2_images)
    rig_cameras = panorama_rig_manifest.get("cameras", [])
    ref_camera_id = int(rig_cameras[0]["camera_id"])

    rig = pycolmap.Rig()
    rig.add_ref_sensor(_pycolmap_sensor(pycolmap, ref_camera_id))
    for camera in rig_cameras[1:]:
        camera_id = int(camera["camera_id"])
        rig.add_sensor(
            _pycolmap_sensor(pycolmap, camera_id),
            _pycolmap_rigid3d(pycolmap, sensor_from_rig_rotations[camera_id]),
        )

    rig_id = int(db.write_rig(rig))

    grouped_images = _group_database_images_by_frame(database_images)
    for frame_name in sorted(grouped_images):
        frame = pycolmap.Frame()
        frame.rig_id = rig_id
        for image in grouped_images[frame_name]:
            frame.add_data_id(image.data_id)
        frame_id = int(db.write_frame(frame))
        for image in grouped_images[frame_name]:
            image.frame_id = frame_id
            db.update_image(image)

    logger.info(
        "Annotated database %s with rig_id=%d across %d frame(s)",
        database_path,
        rig_id,
        len(grouped_images),
    )
    db.close()
    return rig_id


def run_panorama_rig_pycolmap_probe(
    *,
    colmap_dataset_dir: Path,
    source_database_path: Path,
    output_dir: Path,
) -> dict:
    """Run a rig-aware pycolmap probe from an existing panorama-rig database.

    Args:
        colmap_dataset_dir: Stage 2 panorama-rig dataset root.
        source_database_path: Existing COLMAP database to copy and annotate.
        output_dir: Probe output directory.

    Returns:
        Parsed sparse-model payload with registration diagnostics.

    Raises:
        RuntimeError: If pycolmap is unavailable or the reconstruction fails.
        FileNotFoundError: If required Stage 2 artifacts are missing.
    """
    pycolmap = _import_pycolmap()
    colmap_dataset_dir = Path(colmap_dataset_dir)
    source_database_path = Path(source_database_path)
    output_dir = Path(output_dir)
    image_dir = colmap_dataset_dir / "images"
    sparse_dir = output_dir / "sparse"
    database_path = output_dir / "database.db"

    panorama_rig_manifest = _load_panorama_rig_manifest(colmap_dataset_dir)
    if panorama_rig_manifest is None:
        raise FileNotFoundError(f"Panorama-rig manifest not found in {colmap_dataset_dir}")
    stage2_images = parse_images_txt(colmap_dataset_dir / "images.txt")

    output_dir.mkdir(parents=True, exist_ok=True)
    if sparse_dir.exists():
        shutil.rmtree(sparse_dir)
    sparse_dir.mkdir(parents=True, exist_ok=True)
    if source_database_path.resolve() != database_path.resolve():
        shutil.copy2(source_database_path, database_path)

    rig_id = _annotate_database_with_panorama_rig(
        pycolmap=pycolmap,
        database_path=database_path,
        panorama_rig_manifest=panorama_rig_manifest,
        stage2_images=stage2_images,
    )

    options = pycolmap.IncrementalPipelineOptions()
    options.multiple_models = False
    options.min_model_size = 2
    options.image_names = _build_stage03_image_list(image_dir, panorama_rig_manifest)
    options.constant_rigs = {rig_id}
    options.constant_cameras = {int(camera["camera_id"]) for camera in panorama_rig_manifest.get("cameras", [])}
    options.ba_refine_focal_length = False
    options.ba_refine_extra_params = False
    options.ba_refine_sensor_from_rig = False
    options.mapper.init_min_tri_angle = 4.0
    options.mapper.init_max_reg_trials = 6
    options.mapper.abs_pose_min_num_inliers = 12
    options.mapper.max_reg_trials = 6
    options.mapper.ba_local_min_tri_angle = 2.0
    options.mapper.filter_min_tri_angle = 0.5
    options.triangulation.min_angle = 0.5
    options.triangulation.ignore_two_view_tracks = False

    logger.info(
        "Running pycolmap incremental_mapping: database=%s, images=%s, output=%s",
        database_path,
        image_dir,
        sparse_dir,
    )
    reconstructions = pycolmap.incremental_mapping(
        database_path=database_path,
        image_path=image_dir,
        output_path=sparse_dir,
        options=options,
    )
    if not reconstructions:
        raise RuntimeError("pycolmap incremental_mapping produced no reconstruction")

    sparse_model = read_sparse_model(sparse_dir)
    diagnostics = _write_stage03_diagnostics(image_dir, sparse_dir, output_dir, sparse_model)
    logger.info(
        "pycolmap probe coverage: %d/%d images (%.1f%%), %d sparse points",
        diagnostics["registered_images"],
        diagnostics["total_input_images"],
        diagnostics["registration_fraction"] * 100.0,
        diagnostics["sparse_point_count"],
    )

    return {
        "cameras": sparse_model["cameras"],
        "images": sparse_model["images"],
        "points3D": sparse_model["points3D"],
        "diagnostics": diagnostics,
        "num_reconstructions": len(reconstructions),
    }
