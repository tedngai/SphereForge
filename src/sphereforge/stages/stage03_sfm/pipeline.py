"""Stage 3.6: Multi-View SfM pipeline orchestration.

Coordinates the full Stage 3 workflow: feature extraction, feature
matching, bundle adjustment (mapper), sparse model reading, and
optional dense reconstruction.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
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


def _share_cameras_across_rig_frames(database_path: Path) -> int:
    """Point every image at the camera record of its rig sensor.

    ``pycolmap.extract_features`` registers a fresh camera for each image. In a
    panorama rig the same physical lens captures every frame, so all images from
    one rig camera must share a single ``camera_id``. Otherwise each image is a
    distinct sensor, the rig degenerates into one rig per image, and the
    constant-rig constraint has nothing to constrain.

    Images are matched to rig cameras by their directory name, which Stage 2
    lays out as ``<camera_name>/<frame>.png``.

    Args:
        database_path: COLMAP database to rewrite in place.

    Returns:
        Number of images whose camera assignment was changed.
    """
    try:
        import pycolmap
    except ImportError:
        return 0

    db = pycolmap.Database.open(database_path)
    try:
        # An image's data_id is derived from its camera_id, so reassigning the
        # camera invalidates the existing frame rows. Clear them *before*
        # reading images (the read-back objects carry frame state), then rebuild
        # once the cameras are shared; the rig annotation step writes the real
        # frames afterwards.
        db.clear_frames()

        images = db.read_all_images()
        if not images:
            return 0

        # Group images by rig camera folder, in manifest order.
        by_folder: dict[str, list] = {}
        for image in images:
            folder = Path(image.name).parent.name
            by_folder.setdefault(folder, []).append(image)

        if len(by_folder) >= len(images):
            # Every image already has its own folder: not a panorama rig.
            return 0

        # Renumber to 1..N in folder order so the IDs match the panorama-rig
        # manifest. The rig annotation builds its rig from the manifest's
        # camera_ids, so any other numbering leaves the rig sensors pointing at
        # cameras that no image uses.
        ordered_folders = sorted(by_folder)
        # Snapshot a representative camera record before renumbering, so the
        # new IDs can be created with the same intrinsics.
        template_camera = db.read_camera(int(images[0].camera_id))
        changed = 0
        for new_id, folder in enumerate(ordered_folders, start=1):
            group = by_folder[folder]
            if not db.exists_camera(new_id):
                camera = pycolmap.Camera()
                camera.camera_id = new_id
                camera.model = template_camera.model
                camera.width = template_camera.width
                camera.height = template_camera.height
                camera.params = list(template_camera.params)
                db.write_camera(camera)
            for image in group:
                if int(image.camera_id) != new_id:
                    image.camera_id = new_id
                    db.update_image(image)
                    changed += 1
            logger.debug("Rig camera %s -> camera_id %d (%d images)", folder, new_id, len(group))

        if changed:
            logger.info(
                "Shared camera records across %d rig camera(s): %d image(s) reassigned",
                len(by_folder),
                changed,
            )
        return changed
    finally:
        db.close()


def _apply_stage2_intrinsics(database_path: Path, dataset_dir: Path) -> int:
    """Write the exact Stage 2 intrinsics into the COLMAP database cameras.

    Stage 2 renders every view itself, so its ``cameras.txt`` holds the true
    pinhole intrinsics. Feature extraction does not know them: without a
    ``camera_params`` hint COLMAP guesses ``f = 1.2 * max(width, height)``.
    For the 105 deg panorama-rig views (fov 90 + overlap 15, 384 px) that is
    f = 460.8 instead of 147.3, i.e. a 45 deg lens. With intrinsics held fixed
    during mapping, the reconstruction then places structure ~2.4x too far
    from the camera path (measured on the synthetic room).

    Each database image is matched to its Stage 2 camera by name (falling back
    to its rig folder), and its camera record is set to that camera's model and
    parameters with ``has_prior_focal_length`` so the mapper trusts it.

    Args:
        database_path: COLMAP database (after feature extraction).
        dataset_dir: Stage 2 dataset root containing ``cameras.txt`` and
            ``images.txt``.

    Returns:
        Number of camera records updated (0 when Stage 2 intrinsics are
        unavailable or pycolmap is missing).
    """
    from sphereforge.common.colmap_helpers import parse_cameras_txt, parse_images_txt

    cameras_txt = Path(dataset_dir) / "cameras.txt"
    images_txt = Path(dataset_dir) / "images.txt"
    if not cameras_txt.exists() or not images_txt.exists():
        logger.warning(
            "No Stage 2 cameras.txt/images.txt in %s; COLMAP will guess the focal length",
            dataset_dir,
        )
        return 0
    try:
        import pycolmap
    except ImportError:
        return 0

    stage2_cameras = parse_cameras_txt(cameras_txt)
    by_name: dict[str, int] = {}
    by_folder: dict[str, int] = {}
    for entry in parse_images_txt(images_txt).values():
        name = str(entry["name"]).replace("\\", "/")
        name = name[len("images/"):] if name.startswith("images/") else name
        by_name[name] = int(entry["camera_id"])
        by_folder.setdefault(Path(name).parent.as_posix(), int(entry["camera_id"]))

    db = pycolmap.Database.open(database_path)
    try:
        targets: dict[int, int] = {}
        for image in db.read_all_images():
            name = str(image.name).replace("\\", "/")
            stage2_id = by_name.get(name, by_folder.get(Path(name).parent.as_posix()))
            if stage2_id is None or stage2_id not in stage2_cameras:
                continue
            previous = targets.setdefault(int(image.camera_id), stage2_id)
            if previous != stage2_id:
                logger.warning(
                    "Database camera %d is shared by images of different Stage 2 cameras "
                    "(%d, %d); keeping the first",
                    int(image.camera_id),
                    previous,
                    stage2_id,
                )
        updated = 0
        for camera_id, stage2_id in targets.items():
            spec = stage2_cameras[stage2_id]
            camera = db.read_camera(camera_id)
            if (int(camera.width), int(camera.height)) != (int(spec["width"]), int(spec["height"])):
                logger.warning(
                    "Stage 2 camera %d is %dx%d but database camera %d is %dx%d; not updating",
                    stage2_id, spec["width"], spec["height"],
                    camera_id, camera.width, camera.height,
                )
                continue
            before = list(camera.params)
            camera.model = str(spec["model"])
            camera.params = [float(v) for v in spec["params"]]
            camera.has_prior_focal_length = True
            db.update_camera(camera)
            updated += 1
            logger.debug("Camera %d intrinsics %s -> %s %s", camera_id, before, spec["model"],
                         spec["params"])
        if updated:
            sample = stage2_cameras[next(iter(targets.values()))]
            logger.info(
                "Applied Stage 2 intrinsics to %d camera(s) (%s, params %s)",
                updated,
                sample["model"],
                [round(float(v), 3) for v in sample["params"]],
            )
        return updated
    finally:
        db.close()


def _prune_outlier_cameras(
    sparse_dir: Path,
    max_radius_factor: float = 3.0,
) -> int:
    """Remove cameras whose pose is inconsistent with the rest of the rig.

    A panorama rig moves smoothly, so every camera should sit near the others.
    A handful of mis-registered views can nevertheless be placed far outside the
    captured volume; because Stage 5 projects depth through those poses, they
    spray points across the scene and inflate every downstream scale estimate.

    Cameras farther than ``max_radius_factor`` times the median distance from
    the rig centroid are dropped. The sparse model is rewritten in place.

    Args:
        sparse_dir: Directory containing the sparse model (``0``, ``1``, ...).
        max_radius_factor: Radii beyond this multiple of the median are outliers.

    Returns:
        Number of cameras removed.
    """
    try:
        import pycolmap
    except ImportError:
        logger.debug("pycolmap unavailable; skipping camera outlier pruning")
        return 0

    model_dir = _select_sparse_model_dir(sparse_dir)
    if model_dir is None:
        return 0

    try:
        reconstruction = pycolmap.Reconstruction(str(model_dir))
    except Exception as exc:
        logger.warning("Could not read sparse model for camera pruning: %s", exc)
        return 0

    from sphereforge.stages.stage03_sfm.rigidity import camera_centre_from_pose

    images = {img_id: img for img_id, img in reconstruction.images.items() if img.has_pose}
    if len(images) < 4:
        return 0

    centers = {}
    for img_id, img in images.items():
        pose = img.cam_from_world
        # pycolmap exposes this as a method in 4.x and a property in 3.x.
        if callable(pose):
            pose = pose()
        # The optical centre is -R^T t. The raw translation differs between
        # rig sensors that share a centre, so it cannot be used as a position.
        centers[img_id] = camera_centre_from_pose(pose)
    stacked = np.stack(list(centers.values()))
    centroid = np.median(stacked, axis=0)
    radii = np.linalg.norm(stacked - centroid, axis=1)
    median_radius = float(np.median(radii))
    if median_radius <= 0:
        return 0

    threshold = max_radius_factor * median_radius
    outliers = [img_id for img_id, c in centers.items() if np.linalg.norm(c - centroid) > threshold]
    if not outliers:
        return 0

    removed = 0
    for img_id in outliers:
        img = reconstruction.image(img_id)
        frame_id = getattr(img, "frame_id", None)
        try:
            if frame_id is not None and hasattr(reconstruction, "deregister_frame"):
                reconstruction.deregister_frame(frame_id)
            else:
                reconstruction.deregister_image(img_id)
            removed += 1
        except Exception as exc:
            logger.debug("Could not deregister camera %s: %s", img_id, exc)
    if removed == 0:
        return 0
    # Write only the binary model. Leaving a stale images.txt/cameras.txt
    # alongside it is worse than useless: readers prefer the text files, so
    # they would keep serving the cameras we just removed.
    for stale in ("cameras.txt", "images.txt", "points3D.txt"):
        stale_path = model_dir / stale
        if stale_path.exists():
            stale_path.unlink()
    reconstruction.write(str(model_dir))
    logger.info(
        "Pruned %d mis-registered camera(s) beyond %.2f m (median radius %.2f m)",
        removed,
        threshold,
        median_radius,
    )
    return removed


def _select_sparse_model_dir(sparse_dir: Path) -> Path | None:
    """Return the sparse sub-model with the most registered images."""
    candidates = [p for p in sorted(sparse_dir.iterdir()) if p.is_dir()] if sparse_dir.exists() else []
    if not candidates:
        return sparse_dir if sparse_dir.exists() else None
    best = None
    best_count = -1
    for candidate in candidates:
        images_file = candidate / "images.bin"
        if not images_file.exists():
            images_file = candidate / "images.txt"
            if not images_file.exists():
                continue
        try:
            count = _count_registered_images(images_file)
        except OSError:
            continue
        if count > best_count:
            best, best_count = candidate, count
    return best


def _count_registered_images(path: Path) -> int:
    """Count registered images in a COLMAP ``images.bin``/``images.txt`` file."""
    if path.suffix == ".bin":
        import struct

        with path.open("rb") as handle:
            return int(struct.unpack("<Q", handle.read(8))[0])
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            # Image lines start with an id; 2D-point lines are "x y id" triples.
            if len(parts) >= 10 and parts[0].isdigit():
                count += 1
    return count


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


def _run_pycolmap_reconstruction(
    *,
    image_dir: Path,
    database_path: Path,
    sparse_dir: Path,
    image_names: list[str] | None = None,
    sequential_overlap: int | None = None,
    matcher_type: str = "sequential",
    skip_mapping: bool = False,
) -> None:
    """Run SfM entirely through pycolmap (no COLMAP CLI binary required).

    This is the fallback backend for environments where the COLMAP command-line
    tools are not installed but the ``pycolmap`` Python package is. It performs
    the same three stages as the CLI path — feature extraction, feature
    matching and incremental mapping — and writes a standard COLMAP sparse
    model (``cameras.bin``/``images.bin``/``points3D.bin``) into *sparse_dir*.

    Args:
        image_dir: Directory of images (camera intrinsics come from the image
            reader, matching the CLI ``feature_extractor`` behaviour).
        database_path: COLMAP database to create/populate.
        sparse_dir: Output directory for the sparse model (``sparse/0``).
        image_names: Optional explicit image order (relative to *image_dir*).
        sequential_overlap: Sequential matcher overlap. ``None`` uses pycolmap's
            default.
        matcher_type: ``"sequential"`` or ``"exhaustive"``.

    Raises:
        RuntimeError: If pycolmap is unavailable or the reconstruction fails.
    """
    try:
        import pycolmap
    except ImportError as exc:
        raise RuntimeError(
            "Stage 3 needs either the COLMAP CLI tools or the 'pycolmap' package. "
            "Install one of them (pip install pycolmap)."
        ) from exc

    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        database_path.unlink()
    sparse_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Running pycolmap SfM backend: images=%s, db=%s, matcher=%s",
        image_dir,
        database_path,
        matcher_type,
    )

    reader_options = pycolmap.ImageReaderOptions()
    # Large 360-derived views otherwise get downscaled, losing the fine
    # texture that SIFT needs to link rig cameras to each other.
    extraction_options = pycolmap.FeatureExtractionOptions()
    extraction_options.max_image_size = 2048
    extraction_options.sift.max_num_features = 16384
    if _env_flag_enabled("SPHEREFORGE_COLMAP_USE_GPU"):
        extraction_options.use_gpu = True
    pycolmap.extract_features(
        database_path=database_path,
        image_path=image_dir,
        image_names=list(image_names or []),
        reader_options=reader_options,
        extraction_options=extraction_options,
    )

    # ``extract_features`` creates a *new* camera per image. For a panorama rig
    # that is fatal: every image gets a unique camera_id, so the rig ends up
    # with one sensor per image, the rig constraint degenerates to "each image
    # is its own rig", and nothing ties a panorama's faces together. Collapse
    # images that share a rig camera onto a single camera record.
    _share_cameras_across_rig_frames(database_path)
    _apply_stage2_intrinsics(database_path, image_dir.parent)

    matching_options = pycolmap.FeatureMatchingOptions()
    matching_options.sift.max_ratio = 0.85
    matching_options.sift.cross_check = False
    if _env_flag_enabled("SPHEREFORGE_COLMAP_USE_GPU"):
        matching_options.use_gpu = True

    if matcher_type == "exhaustive":
        pycolmap.match_exhaustive(database_path=database_path, matching_options=matching_options)
    else:
        pairing = pycolmap.SequentialPairingOptions()
        if sequential_overlap is not None:
            pairing.overlap = int(sequential_overlap)
            pairing.quadratic_overlap = False
        pycolmap.match_sequential(
            database_path=database_path,
            matching_options=matching_options,
            pairing_options=pairing,
        )

    if skip_mapping:
        # The panorama-rig backend applies its rig constraints (constant rigs
        # and fixed sensor-from-rig transforms) during mapping. Mapping here
        # would run an unconstrained reconstruction first, and the rig probe
        # would then have nothing left to constrain.
        logger.info("Skipping mapping; the panorama-rig backend will run it")
        return

    reconstructions = pycolmap.incremental_mapping(
        database_path=database_path,
        image_path=image_dir,
        output_path=sparse_dir,
    )
    if not reconstructions:
        raise RuntimeError(
            "pycolmap incremental mapping produced no reconstruction. "
            "The images may lack sufficient overlap or texture."
        )

    best_id = max(reconstructions, key=lambda k: reconstructions[k].num_reg_images())
    best = reconstructions[best_id]
    logger.info(
        "pycolmap reconstruction %d: %d/%d images registered, %d points",
        best_id,
        best.num_reg_images(),
        best.num_images(),
        best.num_points3D(),
    )


def _run_panorama_rig_pycolmap_reconstruction(
    *,
    colmap_dataset_dir: Path,
    database_path: Path,
    output_dir: Path,
    unconstrained_attempts: int = 3,
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
            f"source_database_path=Path({str(database_path)!r}), output_dir=Path({str(output_dir)!r}), "
            f"attempts={int(unconstrained_attempts)})"
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
        attempts=unconstrained_attempts,
    )


def _model_has_rig(sparse_dir: Path) -> bool:
    """Check whether the sparse model still carries a multi-sensor rig.

    The unconstrained fallback in the pycolmap probe produces ordinary
    per-image cameras, for which the rigidity correction would be wrong.

    Args:
        sparse_dir: Directory holding the COLMAP sparse model(s).

    Returns:
        True when a rig with more than one sensor is present.
    """
    try:
        import pycolmap

        model_dir = _select_sparse_model_dir(Path(sparse_dir))
        if model_dir is None:
            return False
        reconstruction = pycolmap.Reconstruction(str(model_dir))
        return any(rig.num_sensors() > 1 for rig in reconstruction.rigs.values())
    except Exception:  # absence of a rig is the safe default
        return False


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

    # Backend selection: the COLMAP CLI is preferred when installed; otherwise
    # fall back to the pycolmap Python package (same algorithms, no binary).
    colmap_cli_available = shutil.which("colmap") is not None
    panorama_rig_manifest = _load_panorama_rig_manifest(colmap_dataset_dir)
    panorama_temporal_window = _effective_panorama_temporal_window(config, panorama_rig_manifest)
    use_rig_pycolmap = _should_use_panorama_rig_pycolmap(config, panorama_rig_manifest)
    use_pycolmap_fallback = not colmap_cli_available and not use_rig_pycolmap
    if use_pycolmap_fallback:
        logger.warning(
            "COLMAP CLI not found on PATH; using the pycolmap Python backend "
            "(feature extraction, sequential matching, incremental mapping)."
        )

    if use_pycolmap_fallback or (use_rig_pycolmap and not colmap_cli_available):
        # Without the COLMAP binary the database must also be built by pycolmap;
        # the rig-aware probe below only performs the reconstruction step.
        image_names = _build_stage03_image_list(image_dir, panorama_rig_manifest)
        effective_matcher = "exhaustive" if config.matcher_type == "exhaustive" else "sequential"
        if use_rig_pycolmap:
            logger.info(
                "COLMAP CLI unavailable; building the rig database with pycolmap "
                "(frame-major image order, overlap=%d)",
                panorama_temporal_window,
            )
        _run_pycolmap_reconstruction(
            image_dir=image_dir,
            database_path=database_path,
            sparse_dir=sparse_dir,
            image_names=image_names,
            sequential_overlap=(
                panorama_temporal_window if panorama_rig_manifest is not None else None
            ),
            matcher_type=effective_matcher,
            skip_mapping=use_rig_pycolmap,
        )
        if use_rig_pycolmap:
            # The database now exists with shared cameras and matches; let the
            # rig-aware probe run mapping with the rig constraints applied.
            # Pass the already-built database as the source so the probe does
            # not rebuild it (which would undo the shared camera assignment).
            _run_panorama_rig_pycolmap_reconstruction(
                colmap_dataset_dir=colmap_dataset_dir,
                database_path=database_path,
                output_dir=output_dir,
            )
        reconstruction_backend = "pycolmap_panorama_rig" if use_rig_pycolmap else "pycolmap"
        # Check panorama-rig rigidity before anything reads the model. A
        # rig-constrained model is rigid by construction (the check measures
        # optical centres and normally repairs nothing); this guards against a
        # model whose sensors were nevertheless placed at different centres.
        # This must happen in this branch too: it returns before Step 5c below.
        #
        # Only apply it when the model still carries the rig. The unconstrained
        # fallback (used only when the rig run collapsed to pure rotation) has
        # one rig per image, so there is nothing to check.
        if panorama_rig_manifest is not None and _model_has_rig(sparse_dir):
            try:
                from sphereforge.stages.stage03_sfm.rigidity import enforce_rig_rigidity

                rig_model_dir = _select_sparse_model_dir(sparse_dir)
                if rig_model_dir is not None:
                    enforce_rig_rigidity(rig_model_dir)
            except (ImportError, RuntimeError, ValueError, OSError) as exc:
                logger.warning("Rig rigidity enforcement skipped: %s", exc)

        sparse_model = read_sparse_model(sparse_dir)
        _write_stage03_diagnostics(
            image_dir,
            sparse_dir,
            output_dir,
            sparse_model,
            matcher_type=effective_matcher,
            reconstruction_backend=reconstruction_backend,
            panorama_temporal_window=(
                panorama_temporal_window if panorama_rig_manifest is not None else None
            ),
        )
        logger.info(
            "Stage 3 complete (%s backend): %d images registered, %d points",
            reconstruction_backend,
            len(sparse_model.get("images", {})),
            len(sparse_model.get("points3D", {})),
        )
        return sparse_model

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
    # The CLI extractor has no focal hint either; give it Stage 2's exact lens.
    _apply_stage2_intrinsics(database_path, colmap_dataset_dir)

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
            unconstrained_attempts=max(1, int(config.unconstrained_attempts)),
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

    # Step 5b: Drop mis-registered cameras
    _prune_outlier_cameras(sparse_dir)

    # Step 5c: Check panorama-rig rigidity (sensor optical centres per frame);
    # repairs only frames whose sensors disagree about the shared centre.
    if panorama_rig_manifest is not None:
        try:
            from sphereforge.stages.stage03_sfm.rigidity import enforce_rig_rigidity

            model_dir = _select_sparse_model_dir(sparse_dir)
            if model_dir is not None:
                enforce_rig_rigidity(model_dir)
        except (ImportError, RuntimeError, ValueError, OSError) as exc:
            logger.warning("Rig rigidity enforcement skipped: %s", exc)

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

