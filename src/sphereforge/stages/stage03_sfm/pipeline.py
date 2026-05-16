"""Stage 3.6: Multi-View SfM pipeline orchestration.

Coordinates the full Stage 3 workflow: feature extraction, feature
matching, bundle adjustment (mapper), sparse model reading, and
optional dense reconstruction.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import numpy as np

from sphereforge.common.colmap_helpers import quat_to_rotation_matrix
from sphereforge.logging_utils import log_task_completion
from sphereforge.stages.stage02_cubemap.cubemap import _make_rotation_matrix
from sphereforge.stages.stage03_sfm.bundle_adjustment import run_bundle_adjustment
from sphereforge.stages.stage03_sfm.dense_reconstruction import run_dense_reconstruction
from sphereforge.stages.stage03_sfm.feature_extraction import run_feature_extraction
from sphereforge.stages.stage03_sfm.feature_matching import build_vocab_tree, run_feature_matching
from sphereforge.stages.stage03_sfm.model_reader import read_sparse_model

if TYPE_CHECKING:
    from sphereforge.config import Stage03Config

logger = logging.getLogger("sphereforge.stage03.pipeline")

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}
_PYCOLMAP_ENABLE_ENV = "SPHEREFORGE_ENABLE_PYCOLMAP_RIG"
_PYCOLMAP_PYTHON_ENV = "SPHEREFORGE_PYCOLMAP_PYTHON"


def _list_stage03_input_images(image_dir: Path) -> list[str]:
    """List Stage 2 images that should be eligible for COLMAP registration."""
    return sorted(
        path.relative_to(image_dir).as_posix()
        for path in image_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in _IMAGE_SUFFIXES
    )


def _normalize_stage03_image_name(image_name: str) -> str:
    """Normalize Stage 2/3 image names to a common relative path form."""
    normalized = image_name.replace("\\", "/")
    if normalized.startswith("images/"):
        normalized = normalized[len("images/") :]
    return normalized


def _load_panorama_rig_manifest(colmap_dataset_dir: Path) -> dict | None:
    """Load panorama-rig metadata if the Stage 2 dataset provides it."""
    manifest_path = colmap_dataset_dir / "panorama_rig.json"
    if not manifest_path.exists():
        return None
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _env_flag_enabled(env_var: str) -> bool:
    """Interpret common truthy environment variable values."""
    return os.environ.get(env_var, "").strip().lower() in {"1", "true", "yes", "on"}


def _should_use_panorama_rig_pycolmap(config: Stage03Config, panorama_rig_manifest: dict | None) -> bool:
    """Return whether the optional pycolmap rig path is enabled for this run."""
    return (
        panorama_rig_manifest is not None
        and bool(config.panorama_use_pycolmap_rig)
        and _env_flag_enabled(_PYCOLMAP_ENABLE_ENV)
    )


def _effective_panorama_temporal_window(config: Stage03Config, panorama_rig_manifest: dict | None) -> int:
    """Compute the temporal window to use for panorama-rig matching."""
    temporal_window = max(1, int(config.panorama_temporal_window))
    if _should_use_panorama_rig_pycolmap(config, panorama_rig_manifest) and temporal_window < 3:
        logger.info(
            "Panorama-rig pycolmap backend enabled; preferring temporal window 3 over configured value %d",
            temporal_window,
        )
        return 3
    return temporal_window


def _effective_matcher_type(
    config: Stage03Config,
    panorama_rig_manifest: dict | None,
    vocab_tree_candidate: Path,
) -> str:
    """Choose a practical matcher for the current Stage 3 backend.

    The rig-aware pycolmap path already benefits from frame-major sequential
    matching and does not need an expensive locally built vocabulary tree for
    the current panorama-rig rerun workflow. If the user did not provide an
    external tree beside the dataset, prefer plain sequential matching so the
    productized pycolmap rerun can complete in this environment.
    """
    matcher_type = config.matcher_type
    if (
        matcher_type == "sequential+vocabulary_tree"
        and _should_use_panorama_rig_pycolmap(config, panorama_rig_manifest)
        and not vocab_tree_candidate.exists()
    ):
        logger.info(
            "Panorama-rig pycolmap backend enabled without an external vocab_tree.bin; "
            "falling back from sequential+vocabulary_tree to sequential matching"
        )
        return "sequential"
    return matcher_type


def _run_panorama_rig_pycolmap_reconstruction(
    *,
    colmap_dataset_dir: Path,
    database_path: Path,
    output_dir: Path,
) -> None:
    """Run the optional pycolmap panorama-rig reconstruction backend."""
    pycolmap_python = os.environ.get(_PYCOLMAP_PYTHON_ENV, "").strip()
    if pycolmap_python:
        project_root = Path(__file__).resolve().parents[4]
        src_dir = project_root / "src"
        env = dict(os.environ)
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            f"{src_dir}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else str(src_dir)
        )
        probe_code = (
            "from pathlib import Path; "
            "from sphereforge.stages.stage03_sfm.pycolmap_probe import run_panorama_rig_pycolmap_probe; "
            f"run_panorama_rig_pycolmap_probe(colmap_dataset_dir=Path({str(colmap_dataset_dir)!r}), "
            f"source_database_path=Path({str(database_path)!r}), output_dir=Path({str(output_dir)!r}))"
        )
        logger.info("Running panorama-rig pycolmap backend via interpreter %s", pycolmap_python)
        result = subprocess.run(
            [pycolmap_python, "-c", probe_code],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        if result.returncode != 0:
            logger.error("pycolmap backend stdout:\n%s", result.stdout)
            logger.error("pycolmap backend stderr:\n%s", result.stderr)
            raise RuntimeError(
                f"Panorama-rig pycolmap backend failed (exit code {result.returncode})"
            )
        if result.stdout.strip():
            logger.debug("pycolmap backend stdout:\n%s", result.stdout)
        if result.stderr.strip():
            logger.debug("pycolmap backend stderr:\n%s", result.stderr)
        return

    from sphereforge.stages.stage03_sfm.pycolmap_probe import run_panorama_rig_pycolmap_probe

    run_panorama_rig_pycolmap_probe(
        colmap_dataset_dir=colmap_dataset_dir,
        source_database_path=database_path,
        output_dir=output_dir,
    )


def _build_stage03_image_list(image_dir: Path, panorama_rig_manifest: dict | None) -> list[str]:
    """Build a deterministic image ordering for feature extraction."""
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


def _camera_forward_from_manifest(camera: dict) -> np.ndarray:
    """Compute the world-space forward direction for a panorama-rig camera."""
    rotation = _make_rotation_matrix(float(camera["yaw_deg"]), float(camera["pitch_deg"]))
    forward = rotation.T @ np.array([0.0, 0.0, 1.0], dtype=np.float64)
    return forward / np.linalg.norm(forward)


def _camera_neighbors_from_manifest(panorama_rig_manifest: dict) -> dict[str, set[str]]:
    """Build a neighbor graph for panorama-rig cameras based on angular overlap."""
    cameras = panorama_rig_manifest.get("cameras", [])
    max_neighbor_angle = float(panorama_rig_manifest.get("fov", 90.0)) + float(
        panorama_rig_manifest.get("overlap", 0.0)
    ) + 5.0
    neighbor_graph = {camera["name"]: set() for camera in cameras}
    forwards = {camera["name"]: _camera_forward_from_manifest(camera) for camera in cameras}

    for idx, camera_a in enumerate(cameras):
        for camera_b in cameras[idx + 1 :]:
            dot = float(np.clip(np.dot(forwards[camera_a["name"]], forwards[camera_b["name"]]), -1.0, 1.0))
            angle_deg = float(np.degrees(np.arccos(dot)))
            if angle_deg <= max_neighbor_angle:
                neighbor_graph[camera_a["name"]].add(camera_b["name"])
                neighbor_graph[camera_b["name"]].add(camera_a["name"])

    return neighbor_graph


def _write_panorama_rig_match_list(
    image_dir: Path,
    output_dir: Path,
    panorama_rig_manifest: dict,
    temporal_window: int,
    pair_strategy: str,
) -> Path:
    """Persist allowed panorama-rig image pairs for restricted retrieval."""
    image_sequences: dict[str, list[str]] = {}
    for camera in panorama_rig_manifest.get("cameras", []):
        camera_dir = image_dir / camera["name"]
        image_sequences[camera["name"]] = sorted(
            path.relative_to(image_dir).as_posix()
            for path in camera_dir.glob("*")
            if path.is_file() and path.suffix.lower() in _IMAGE_SUFFIXES
        )

    pair_lines: set[str] = set()
    neighbor_graph = _camera_neighbors_from_manifest(panorama_rig_manifest)
    camera_names = sorted(image_sequences.keys())
    if pair_strategy == "all":
        candidate_cameras = {camera_name: {other for other in camera_names if other != camera_name} for camera_name in camera_names}
    else:
        candidate_cameras = neighbor_graph

    for camera_name in camera_names:
        current_images = image_sequences[camera_name]
        for idx, image_name in enumerate(current_images):
            for step in range(1, temporal_window + 1):
                if idx + step >= len(current_images):
                    break
                pair_lines.add(f"{image_name} {current_images[idx + step]}")

            for other_camera in sorted(candidate_cameras.get(camera_name, set())):
                other_images = image_sequences[other_camera]
                for step in range(1, temporal_window + 1):
                    other_idx = idx + step
                    if other_idx >= len(other_images):
                        break
                    pair_lines.add(f"{image_name} {other_images[other_idx]}")

    match_list_path = output_dir / "panorama_rig_match_list.txt"
    match_list_path.write_text("\n".join(sorted(pair_lines)) + ("\n" if pair_lines else ""), encoding="utf-8")
    return match_list_path


def _count_colmap_models(sparse_dir: Path) -> int:
    """Count COLMAP sparse model directories under the stage output."""
    subdirs = [path for path in sparse_dir.iterdir() if path.is_dir()]
    if subdirs:
        return len(subdirs)
    if any((sparse_dir / name).exists() for name in ("cameras.txt", "cameras.bin")):
        return 1
    return 0


def _camera_center(image_entry: dict) -> np.ndarray:
    """Compute a COLMAP camera center in world coordinates."""
    rotation = quat_to_rotation_matrix(
        image_entry["qw"],
        image_entry["qx"],
        image_entry["qy"],
        image_entry["qz"],
    )
    translation = np.array(
        [image_entry["tx"], image_entry["ty"], image_entry["tz"]],
        dtype=np.float32,
    )
    return (-rotation.T @ translation).astype(np.float32)


def _write_sparse_preview(sparse_model: dict, output_path: Path) -> None:
    """Write a simple top-down sparse-model preview for quick inspection."""
    canvas = np.full((960, 960, 3), 255, dtype=np.uint8)
    complete_camera_entries = [
        image_entry
        for image_entry in sparse_model["images"].values()
        if all(
            key in image_entry
            for key in ("qw", "qx", "qy", "qz", "tx", "ty", "tz")
        )
    ]
    points = np.array(
        [
            [point["x"], point["z"]]
            for point in sparse_model["points3D"].values()
            if "x" in point and "z" in point
        ],
        dtype=np.float32,
    )
    cameras = np.array(
        [
            _camera_center(image_entry)[[0, 2]]
            for image_entry in complete_camera_entries
        ],
        dtype=np.float32,
    )

    if points.size == 0 and cameras.size == 0:
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
        cv2.imwrite(str(output_path), canvas)
        return

    planar = []
    if points.size > 0:
        planar.append(points)
    if cameras.size > 0:
        planar.append(cameras)
    stacked = np.concatenate(planar, axis=0)

    min_xy = stacked.min(axis=0)
    max_xy = stacked.max(axis=0)
    center_xy = (min_xy + max_xy) * 0.5
    span = max(float(np.max(max_xy - min_xy)), 1e-6)
    scale = 760.0 / span

    def _to_canvas(coords: np.ndarray) -> np.ndarray:
        normalized = (coords - center_xy) * scale
        mapped = np.empty_like(normalized)
        mapped[:, 0] = normalized[:, 0] + 480.0
        mapped[:, 1] = 480.0 - normalized[:, 1]
        return np.round(mapped).astype(np.int32)

    if points.size > 0:
        for x, y in _to_canvas(points):
            cv2.circle(canvas, (int(x), int(y)), 1, (170, 170, 170), -1)

    if cameras.size > 0:
        for x, y in _to_canvas(cameras):
            cv2.circle(canvas, (int(x), int(y)), 6, (40, 80, 220), -1)

    cv2.putText(
        canvas,
        f"points={len(sparse_model['points3D'])} cameras={len(complete_camera_entries)}",
        (24, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (30, 30, 30),
        2,
        cv2.LINE_AA,
    )
    cv2.imwrite(str(output_path), canvas)


def _write_stage03_diagnostics(
    image_dir: Path,
    sparse_dir: Path,
    output_dir: Path,
    sparse_model: dict,
    *,
    matcher_type: str,
    reconstruction_backend: str,
    panorama_temporal_window: int | None,
) -> dict:
    """Persist a machine-readable Stage 3 registration summary."""
    input_image_names = _list_stage03_input_images(image_dir)
    registered_image_names = sorted(
        _normalize_stage03_image_name(image_entry["name"])
        for image_entry in sparse_model["images"].values()
    )
    registered_name_set = set(registered_image_names)
    all_image_names = sorted(set(input_image_names) | registered_name_set)

    total_input_images = len(input_image_names)
    registered_images = len(registered_image_names)
    registration_fraction = (
        registered_images / total_input_images if total_input_images > 0 else 0.0
    )

    report_path = output_dir / "registration_report.json"
    csv_path = output_dir / "registered_vs_total.csv"
    preview_path = output_dir / "sparse_preview.png"

    report = {
        "total_input_images": total_input_images,
        "registered_images": registered_images,
        "registration_fraction": registration_fraction,
        "sparse_point_count": len(sparse_model["points3D"]),
        "camera_count": len(sparse_model["cameras"]),
        "model_count": _count_colmap_models(sparse_dir),
        "matcher_type": matcher_type,
        "reconstruction_backend": reconstruction_backend,
        "registered_image_names": registered_image_names,
        "artifacts": {
            "registration_report": str(report_path),
            "registered_vs_total": str(csv_path),
            "sparse_preview": str(preview_path),
        },
    }
    if panorama_temporal_window is not None:
        report["panorama_temporal_window"] = panorama_temporal_window

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    csv_lines = ["image_name,registered\n"]
    for image_name in all_image_names:
        csv_lines.append(f"{image_name},{int(image_name in registered_name_set)}\n")
    csv_path.write_text("".join(csv_lines), encoding="utf-8")
    _write_sparse_preview(sparse_model, preview_path)

    return report


def run_stage03(
    config: Stage03Config,
    colmap_dataset_dir: Path,
    output_dir: Path,
) -> dict:
    """Run the full Stage 3 (Multi-View SfM) pipeline.

    Orchestrates the following steps:

    1. Set up database path and directories.
    2. Run feature extraction.
    3. Run feature matching.
    4. Run bundle adjustment (mapper + bundle_adjuster).
    5. Read sparse model.
    6. Optionally run dense reconstruction.
    7. Return dict with sparse model data.

    Args:
        config: Stage 3 configuration (``Stage03Config``).
        colmap_dataset_dir: Root directory of the COLMAP dataset,
            expected to contain an ``images/`` subdirectory and
            optionally a ``masks/`` subdirectory.
        output_dir: Directory where Stage 3 outputs are written.

    Returns:
        Dict with keys ``"cameras"``, ``"images"``, ``"points3D"``
        containing the parsed sparse model data.

    Raises:
        RuntimeError: If any COLMAP subprocess fails.
        FileNotFoundError: If required input directories or files
            are missing.
    """
    colmap_dataset_dir = Path(colmap_dataset_dir)
    output_dir = Path(output_dir)

    # Step 1: Set up directories
    database_path = output_dir / "database.db"
    sparse_dir = output_dir / "sparse"
    dense_dir = output_dir / "dense"
    image_dir = colmap_dataset_dir / "images"
    mask_dir = colmap_dataset_dir / "masks"

    # Ensure output directories exist
    sparse_dir.mkdir(parents=True, exist_ok=True)
    if config.dense_reconstruction:
        dense_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Starting Stage 3 SfM pipeline: dataset=%s, output=%s",
        colmap_dataset_dir,
        output_dir,
    )
    logger.info(
        "Config: feature_type=%s, matcher_type=%s, "
        "refine_intrinsics=%s, dense_reconstruction=%s, panorama_use_pycolmap_rig=%s",
        config.feature_type,
        config.matcher_type,
        config.refine_intrinsics,
        config.dense_reconstruction,
        config.panorama_use_pycolmap_rig,
    )

    # Step 2: Feature extraction
    logger.info("Step 2: Feature extraction")
    mask_dir_path = mask_dir if mask_dir.is_dir() else None
    panorama_rig_manifest = _load_panorama_rig_manifest(colmap_dataset_dir)
    panorama_temporal_window = _effective_panorama_temporal_window(config, panorama_rig_manifest)
    image_list = _build_stage03_image_list(image_dir, panorama_rig_manifest)
    match_list_path: Path | None = None
    if panorama_rig_manifest is not None and config.panorama_use_match_list:
        match_list_path = _write_panorama_rig_match_list(
            image_dir,
            output_dir,
            panorama_rig_manifest,
            temporal_window=panorama_temporal_window,
            pair_strategy=config.panorama_pair_strategy,
        )
    run_feature_extraction(
        database_path=database_path,
        image_dir=image_dir,
        camera_model="PINHOLE",
        feature_type=config.feature_type,
        mask_dir=mask_dir_path,
        single_camera_per_folder=panorama_rig_manifest is not None,
        image_list=image_list,
    )

    # Step 3: Feature matching
    logger.info("Step 3: Feature matching")
    # Resolve vocabulary tree path (commonly placed alongside the dataset)
    vocab_tree_candidate = colmap_dataset_dir / "vocab_tree.bin"
    matcher_type = _effective_matcher_type(config, panorama_rig_manifest, vocab_tree_candidate)
    vocab_tree_path: Path | None = None
    if vocab_tree_candidate.exists():
        vocab_tree_path = vocab_tree_candidate
    elif panorama_rig_manifest is not None and "vocabulary_tree" in matcher_type:
        vocab_tree_path = build_vocab_tree(database_path, output_dir / "panorama_rig_vocab_tree.bin")

    sequential_overlap = None
    sequential_quadratic_overlap = None
    if panorama_rig_manifest is not None:
        sequential_overlap = panorama_temporal_window
        sequential_quadratic_overlap = False
        logger.info(
            "Panorama-rig dataset detected; constraining sequential matching to overlap=%d and quadratic_overlap=%s",
            sequential_overlap,
            sequential_quadratic_overlap,
        )

    run_feature_matching(
        database_path=database_path,
        matcher_type=matcher_type,
        vocab_tree_path=vocab_tree_path,
        match_list_path=match_list_path,
        sequential_overlap=sequential_overlap,
        sequential_quadratic_overlap=sequential_quadratic_overlap,
    )

    # Step 4: Reconstruction backend
    reconstruction_backend = "colmap_cli"
    if _should_use_panorama_rig_pycolmap(config, panorama_rig_manifest):
        logger.info("Step 4: Rig-aware pycolmap reconstruction")
        reconstruction_backend = "pycolmap_panorama_rig"
        _run_panorama_rig_pycolmap_reconstruction(
            colmap_dataset_dir=colmap_dataset_dir,
            database_path=database_path,
            output_dir=output_dir,
        )
    else:
        logger.info("Step 4: Bundle adjustment")
        run_bundle_adjustment(
            database_path=database_path,
            sparse_dir=sparse_dir,
            refine_intrinsics=config.refine_intrinsics,
            image_dir=image_dir,
        )

    # Step 5: Read sparse model and persist registration diagnostics
    logger.info("Step 5: Reading sparse model")
    sparse_model = read_sparse_model(sparse_dir)
    diagnostics = _write_stage03_diagnostics(
        image_dir,
        sparse_dir,
        output_dir,
        sparse_model,
        matcher_type=matcher_type,
        reconstruction_backend=reconstruction_backend,
        panorama_temporal_window=panorama_temporal_window if panorama_rig_manifest is not None else None,
    )
    logger.info(
        "Registration coverage: %d/%d images (%.1f%%), %d sparse points across %d model(s)",
        diagnostics["registered_images"],
        diagnostics["total_input_images"],
        diagnostics["registration_fraction"] * 100.0,
        diagnostics["sparse_point_count"],
        diagnostics["model_count"],
    )

    min_registration_fraction = max(float(config.min_registration_fraction), 0.0)
    if (
        min_registration_fraction > 0.0
        and diagnostics["total_input_images"] > 0
        and diagnostics["registration_fraction"] < min_registration_fraction
    ):
        raise RuntimeError(
            "Stage 3 registration coverage is too low to trust downstream stages: "
            f"{diagnostics['registered_images']}/{diagnostics['total_input_images']} "
            f"({diagnostics['registration_fraction']:.1%}) registered, below the configured "
            f"minimum of {min_registration_fraction:.1%}. See {diagnostics['artifacts']['registration_report']}"
        )

    # Step 6: Optionally run dense reconstruction
    if config.dense_reconstruction:
        logger.info("Step 6: Dense reconstruction")
        try:
            run_dense_reconstruction(
                sparse_dir=sparse_dir,
                image_dir=image_dir,
                dense_dir=dense_dir,
            )
        except RuntimeError as exc:
            logger.warning(
                "Dense reconstruction failed (non-fatal): %s", exc
            )

    # Step 7: Log completion and return
    logger.info("Stage 3 SfM pipeline completed successfully.")
    try:
        log_task_completion(
            task_id="T3.6",
            notes="Stage 3 SfM pipeline completed",
            files_created=[
                str(database_path),
                str(sparse_dir),
            ],
        )
    except Exception:
        # Don't fail the pipeline if progress logging has an issue
        logger.debug("Progress logging skipped", exc_info=True)

    return {
        "cameras": sparse_model["cameras"],
        "images": sparse_model["images"],
        "points3D": sparse_model["points3D"],
        "diagnostics": diagnostics,
    }
