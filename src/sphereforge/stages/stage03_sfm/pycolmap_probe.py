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
        # Reconstruction quality. pycolmap's mapper is not deterministic (two
        # runs on an identical database differ by a few hundred points and by
        # several metres of path span), so these are recorded to make the
        # variance visible instead of silent.
        **_reconstruction_quality(sparse_model),
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


def _reconstruction_score(quality: dict) -> float:
    """Score a reconstruction so competing attempts can be ranked.

    Higher is better. A good reconstruction registers most images, triangulates
    many points, and keeps the camera path *inside* the captured geometry
    (``camera_to_point_radius`` below 1).

    Args:
        quality: Metrics from :func:`_reconstruction_quality`, optionally
            including ``registered_images`` and ``sparse_point_count``.

    Returns:
        Score in roughly [0, 3]; 0 when the model is unusable.
    """
    if not quality:
        return 0.0
    ratio = quality.get("camera_to_point_radius")
    if ratio is None or not np.isfinite(ratio):
        return 0.0
    # 1.0 when the cameras sit well inside the cloud, falling to 0 at ratio 1.
    inside = max(0.0, min(1.0, 1.0 - ratio))
    points = float(quality.get("sparse_point_count") or 0)
    registered = float(quality.get("registered_images") or 0)
    # Log-scaled so a large point count cannot swamp the geometry term.
    point_term = np.log1p(points) / np.log1p(20000.0)
    return float(inside + min(1.0, point_term) + min(1.0, registered / 144.0))


def _reconstruction_quality(sparse_model: dict) -> dict:
    """Summarise how well-formed a sparse reconstruction is.

    Monocular SfM is ambiguous up to a similarity and pycolmap's mapper is not
    deterministic, so two runs on identical input can differ noticeably. These
    numbers make that variance observable: a healthy reconstruction puts the
    camera path *inside* the point cloud, with a camera-to-point radius ratio
    well below 1.

    Args:
        sparse_model: Parsed sparse model.

    Returns:
        Dict of quality metrics, empty when the model has no points or images.
    """
    points = sparse_model.get("points3D") or {}
    images = sparse_model.get("images") or {}
    if not points or not images:
        return {}

    xyz = np.array([[p["x"], p["y"], p["z"]] for p in points.values()], dtype=np.float64)
    centres = []
    for image in images.values():
        rotation = np.asarray(
            [
                image.get("qw", 1.0),
                image.get("qx", 0.0),
                image.get("qy", 0.0),
                image.get("qz", 0.0),
            ],
            dtype=np.float64,
        )
        quat = np.array([rotation[1], rotation[2], rotation[3], rotation[0]])
        norm = np.linalg.norm(quat)
        if norm < 1e-12:
            continue
        qx, qy, qz, qw = quat / norm
        rot = np.array(
            [
                [1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
                [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
                [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)],
            ]
        )
        translation = np.array(
            [image.get("tx", 0.0), image.get("ty", 0.0), image.get("tz", 0.0)],
            dtype=np.float64,
        )
        centres.append(-rot.T @ translation)
    if not centres:
        return {}

    centres = np.stack(centres)
    origin = xyz.mean(axis=0)
    point_radius = float(np.median(np.linalg.norm(xyz - origin, axis=1)))
    camera_radius = float(np.median(np.linalg.norm(centres - origin, axis=1)))
    return {
        "point_radius_p50": point_radius,
        "camera_radius_p50": camera_radius,
        # Below 1 means the cameras sit inside the captured geometry, which is
        # what a real capture looks like. Well above 1 means the mapper put the
        # path outside the scene and downstream stages will struggle.
        "camera_to_point_radius": (
            camera_radius / point_radius if point_radius > 1e-9 else float("inf")
        ),
        "camera_path_span": float(np.max(np.ptp(centres, axis=0))),
    }


def _path_is_degenerate(
    frame_centres: np.ndarray, points: np.ndarray, min_ratio: float = 0.01
) -> bool:
    """Decide whether a camera path collapsed to (almost) a single point.

    A rig mapper that explains the data by pure rotation leaves every frame at
    the same optical centre: the path has no extent compared with the scene and
    carries no parallax. A *straight* path is not degenerate; real captures are
    often close to a line (the synthetic test path is one).

    Args:
        frame_centres: Per-frame optical centres ``(F, 3)``.
        points: Sparse 3D points ``(P, 3)`` (used for the scene scale).
        min_ratio: The path counts as collapsed when its radius is below this
            fraction of the median point distance from the path centre.

    Returns:
        True when the path radius is negligible relative to the scene.
    """
    if frame_centres.shape[0] < 3:
        return False
    centre = frame_centres.mean(axis=0)
    path_radius = float(np.max(np.linalg.norm(frame_centres - centre, axis=1)))
    if points.shape[0] == 0:
        return path_radius <= 1e-9
    scene_radius = float(np.median(np.linalg.norm(points - centre, axis=1)))
    if scene_radius <= 1e-12:
        return False
    return path_radius / scene_radius < min_ratio


def _camera_path_is_degenerate(sparse_dir: Path, min_ratio: float = 0.01) -> bool:
    """Check whether a reconstruction's camera path collapsed to pure rotation.

    Camera positions are the optical centres ``-R^T t``. (An earlier version
    used the raw ``cam_from_world`` translations; for rig sensors those differ
    by each sensor's rotation and their per-frame mean is meaningless. On the
    synthetic room it reported X/Z spans of exactly 0 for a correct rig model
    whose path matched ground truth to 1.5 cm, which sent Stage 3 to the
    unconstrained fallback and broke the rig.)

    Args:
        sparse_dir: Directory containing the COLMAP sparse model.
        min_ratio: See :func:`_path_is_degenerate`.

    Returns:
        True when the camera path is negligible relative to the scene.
    """
    try:
        import pycolmap

        reconstruction = pycolmap.Reconstruction(str(sparse_dir))
    except Exception:  # a model we cannot read is not our concern
        return False

    from sphereforge.stages.stage03_sfm.rigidity import camera_centre_from_pose

    centres = []
    if reconstruction.frames:
        for frame in reconstruction.frames.values():
            sensors = [
                camera_centre_from_pose(reconstruction.image(data_id.id).cam_from_world)
                for data_id in frame.data_ids
                if reconstruction.image(data_id.id).has_pose
            ]
            if sensors:
                centres.append(np.mean(np.stack(sensors), axis=0))
    else:
        for image in reconstruction.images.values():
            if image.has_pose:
                centres.append(camera_centre_from_pose(image.cam_from_world))
    points = np.array(
        [np.asarray(p.xyz, dtype=np.float64) for p in reconstruction.points3D.values()]
    ).reshape(-1, 3)
    if len(centres) < 3:
        return False
    return _path_is_degenerate(np.stack(centres), points, min_ratio=min_ratio)


def _strip_rig_from_database(pycolmap: Any, database_path: Path) -> None:
    """Remove the panorama-rig annotation from a COLMAP database copy.

    The rig is stored in the database, so an unconstrained mapping run has to
    start from a copy without it; otherwise the mapper rebuilds the same rig and
    reproduces the degenerate pure-rotation solution.

    Args:
        pycolmap: The imported pycolmap module.
        database_path: Database to modify in place.
    """
    import sqlite3

    connection = sqlite3.connect(str(database_path))
    try:
        connection.execute("DELETE FROM frames")
        connection.execute("DELETE FROM rigs")
        connection.commit()
    finally:
        connection.close()
    logger.info("Cleared rig annotation from %s", database_path)


def run_panorama_rig_pycolmap_probe(
    *,
    colmap_dataset_dir: Path,
    source_database_path: Path,
    output_dir: Path,
    attempts: int = 3,
) -> dict:
    """Run a rig-aware pycolmap probe from an existing panorama-rig database.

    Args:
        colmap_dataset_dir: Stage 2 panorama-rig dataset root.
        source_database_path: Existing COLMAP database to copy and annotate.
        output_dir: Probe output directory.
        attempts: How many unconstrained mapping runs to try when the rig
            constraint collapses the camera path. The mapper is not
            deterministic, so the best-scoring attempt is kept.

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

    _annotate_database_with_panorama_rig(
        pycolmap=pycolmap,
        database_path=database_path,
        panorama_rig_manifest=panorama_rig_manifest,
        stage2_images=stage2_images,
    )

    options = pycolmap.IncrementalPipelineOptions()
    options.multiple_models = False
    options.min_model_size = 2
    options.image_names = _build_stage03_image_list(image_dir, panorama_rig_manifest)
    # The rig *structure* (sensor_from_rig) is held fixed by
    # ``ba_refine_sensor_from_rig = False`` below; frame poses stay free.
    # (Note: the old "X and Z spans of exactly 0" measurement that motivated
    # extra workarounds here came from averaging raw cam_from_world
    # translations, which cancel for a yaw-symmetric rig. The optical centres of
    # this configuration match the ground-truth path to ~1.5 cm.)
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

    # Safety net: if the mapper explained the data by pure rotation, every frame
    # sits at (almost) one optical centre and the model has no parallax. Only
    # then re-run without the rig annotation. Dropping the rig is a last resort:
    # the unconstrained model does not keep a panorama's faces together.
    # ``sparse_dir`` is the parent that holds the numbered sub-models, so the
    # check must run on the model the mapper actually wrote.
    from sphereforge.stages.stage03_sfm.model_reader import _select_best_model_dir

    best_model_dir = _select_best_model_dir(sparse_dir) or sparse_dir
    degenerate = _camera_path_is_degenerate(best_model_dir)
    logger.info("Camera path degeneracy check on %s: degenerate=%s", best_model_dir, degenerate)
    if degenerate:
        logger.warning(
            "Rig-constrained mapping collapsed the camera path to a point (pure "
            "rotation); re-running without the rig constraint to recover translation"
        )
        shutil.rmtree(sparse_dir)
        sparse_dir.mkdir(parents=True, exist_ok=True)
        # The rig lives in the database, so simply dropping the options is not
        # enough: the mapper would rebuild the same 12-sensor rig. Rebuild the
        # database from a copy with the rig tables cleared.
        plain_database = output_dir / "database_plain.db"
        shutil.copy2(database_path, plain_database)
        _strip_rig_from_database(pycolmap, plain_database)
        plain_options = pycolmap.IncrementalPipelineOptions()
        plain_options.multiple_models = False
        plain_options.min_model_size = 2
        plain_options.ba_refine_focal_length = False
        plain_options.ba_refine_extra_params = False
        plain_options.mapper.init_min_tri_angle = options.mapper.init_min_tri_angle
        plain_options.mapper.abs_pose_min_num_inliers = options.mapper.abs_pose_min_num_inliers
        plain_options.triangulation.min_angle = options.triangulation.min_angle

        # The unconstrained mapper is not deterministic: two runs on identical
        # input differ by hundreds of points and by several metres of path span,
        # and some runs place the camera path outside the point cloud entirely.
        # Run it a few times and keep the best-scoring reconstruction rather than
        # accepting whatever the first attempt produced.
        attempts = max(1, int(attempts))
        best: tuple[float, Path] | None = None
        for attempt in range(attempts):
            attempt_dir = output_dir / f"sparse_attempt{attempt}"
            if attempt_dir.exists():
                shutil.rmtree(attempt_dir)
            attempt_dir.mkdir(parents=True, exist_ok=True)
            plain_reconstructions = pycolmap.incremental_mapping(
                database_path=plain_database,
                image_path=image_dir,
                output_path=str(attempt_dir),
                options=plain_options,
            )
            if not plain_reconstructions:
                logger.warning("Attempt %d produced no reconstruction", attempt + 1)
                continue
            attempt_model = _select_best_model_dir(attempt_dir)
            if attempt_model is None:
                continue
            attempt_sparse = read_sparse_model(attempt_model)
            score = _reconstruction_score(
                {
                    **_reconstruction_quality(attempt_sparse),
                    "registered_images": len(attempt_sparse["images"]),
                    "sparse_point_count": len(attempt_sparse["points3D"]),
                }
            )
            logger.info(
                "Attempt %d/%d: score=%.3f (higher is better)", attempt + 1, attempts, score
            )
            if best is None or score > best[0]:
                best = (score, attempt_model)

        if best is not None:
            best_model_dir, best_score = best[1], best[0]
            logger.info("Selected reconstruction with score %.3f", best_score)
            for item in Path(best_model_dir).iterdir():
                target = sparse_dir / item.name
                if item.is_file():
                    shutil.copy2(item, target)
                elif item.is_dir():
                    shutil.copytree(item, target, dirs_exist_ok=True)
            if best_score <= 0.0:
                logger.warning(
                    "Every unconstrained attempt placed the camera path outside the "
                    "point cloud; geometry quality will be reduced"
                )
        else:
            logger.warning("Unconstrained re-run produced no reconstruction; keeping the rig model")

    sparse_model = read_sparse_model(sparse_dir)
    diagnostics = _write_stage03_diagnostics(image_dir, sparse_dir, output_dir, sparse_model)
    logger.info(
        "pycolmap probe coverage: %d/%d images (%.1f%%), %d sparse points",
        diagnostics["registered_images"],
        diagnostics["total_input_images"],
        diagnostics["registration_fraction"] * 100.0,
        diagnostics["sparse_point_count"],
    )
    ratio = diagnostics.get("camera_to_point_radius")
    if ratio is not None and ratio > 1.0:
        logger.warning(
            "Camera path lies outside the point cloud (camera/point radius %.2f); "
            "the mapper likely landed in a poor solution — downstream geometry "
            "quality will be reduced. Re-running Stage 3 may give a better result.",
            ratio,
        )

    return {
        "cameras": sparse_model["cameras"],
        "images": sparse_model["images"],
        "points3D": sparse_model["points3D"],
        "diagnostics": diagnostics,
        "num_reconstructions": len(reconstructions),
    }


