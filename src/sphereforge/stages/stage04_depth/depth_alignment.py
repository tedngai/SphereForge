"""Depth alignment to COLMAP sparse point metric scale.

Aligns monocular (relative-scale) depth maps to metric scale using the
sparse 3D point cloud from COLMAP SfM. Supports optional refinement with
an RPG360 anchor depth map for locally weighted blending in overlap regions.
"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path

import numpy as np

from sphereforge.common.colmap_helpers import quat_to_rotation_matrix
from sphereforge.common.depth_utils import align_depth_median_ratio
from sphereforge.stages.stage02_cubemap.cubemap import _make_rotation_matrix

logger = logging.getLogger("sphereforge.stage04.depth_alignment")


def _normalize_stage03_image_name(image_name: str) -> str:
    """Normalize COLMAP image names to a project-relative path form."""
    normalized = image_name.replace("\\", "/")
    if normalized.startswith("images/"):
        normalized = normalized[len("images/") :]
    return normalized


def _frame_stem_from_image_name(image_name: str) -> str:
    """Return the panorama frame stem from a Stage 2/3 image name."""
    return Path(_normalize_stage03_image_name(image_name)).stem


def _camera_name_from_image_name(image_name: str) -> str | None:
    """Return the panorama-rig camera folder name from a Stage 2/3 image name."""
    parts = Path(_normalize_stage03_image_name(image_name)).parts
    if len(parts) < 2:
        return None
    return parts[-2]


def _load_panorama_rig_manifest(colmap_dataset_dir: Path | None) -> dict | None:
    """Load panorama-rig metadata if the Stage 2 dataset provides it."""
    if colmap_dataset_dir is None:
        return None
    manifest_path = Path(colmap_dataset_dir) / "panorama_rig.json"
    if not manifest_path.exists():
        return None
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _find_image_entry(images: dict, image_name: str) -> dict | None:
    """Find an exact image entry by name, tolerating `images/` prefixes."""
    normalized_target = _normalize_stage03_image_name(image_name)
    for img_data in images.values():
        if _normalize_stage03_image_name(str(img_data["name"])) == normalized_target:
            return img_data
    return None


def _find_panorama_rig_frame_entries(images: dict, image_name: str, panorama_rig_manifest: dict) -> list[dict]:
    """Find all registered panorama-rig views that belong to one ERP frame."""
    frame_stem = Path(image_name).stem
    valid_camera_names = {
        str(camera["name"])
        for camera in panorama_rig_manifest.get("cameras", [])
    }
    matches: list[dict] = []
    for img_data in images.values():
        camera_name = _camera_name_from_image_name(str(img_data["name"]))
        if camera_name not in valid_camera_names:
            continue
        if _frame_stem_from_image_name(str(img_data["name"])) == frame_stem:
            matches.append(img_data)
    return matches


def _camera_rotation_from_manifest(camera_name: str, panorama_rig_manifest: dict) -> np.ndarray:
    """Return the fixed Stage 2 world-to-camera rotation for one rig camera."""
    for camera in panorama_rig_manifest.get("cameras", []):
        if str(camera["name"]) == camera_name:
            return _make_rotation_matrix(float(camera["yaw_deg"]), float(camera["pitch_deg"]))
    raise ValueError(f"Panorama-rig camera '{camera_name}' not found in manifest")


def _build_panorama_pose_from_rig_image(image_entry: dict, panorama_rig_manifest: dict) -> np.ndarray:
    """Derive a world-to-panorama pose from one registered rig view.

    Each Stage 2 panorama-rig view uses a fixed world-to-camera rotation derived
    from its yaw/pitch inside the panorama coordinate frame. Once a registered
    Stage 3 image pose is known, we can recover the world-to-panorama transform
    by factoring out that fixed sensor rotation.
    """
    camera_name = _camera_name_from_image_name(str(image_entry["name"]))
    if camera_name is None:
        raise ValueError(f"Image '{image_entry['name']}' is not a panorama-rig view")

    sensor_rotation = _camera_rotation_from_manifest(camera_name, panorama_rig_manifest)
    image_rotation = quat_to_rotation_matrix(
        image_entry["qw"],
        image_entry["qx"],
        image_entry["qy"],
        image_entry["qz"],
    )
    image_translation = np.array(
        [image_entry["tx"], image_entry["ty"], image_entry["tz"]],
        dtype=np.float64,
    )

    panorama_pose = np.eye(4, dtype=np.float64)
    panorama_pose[:3, :3] = sensor_rotation.T @ image_rotation
    panorama_pose[:3, 3] = sensor_rotation.T @ image_translation
    return panorama_pose


def _get_sparse_points_for_images(image_entries: list[dict], points3d: dict[int, dict]) -> np.ndarray:
    """Collect the union of sparse 3D points observed across multiple images."""
    point_ids: set[int] = set()
    for image_entry in image_entries:
        point_ids.update(int(pid) for pid in image_entry.get("point3D_ids", []) if int(pid) > 0)

    coords: list[np.ndarray] = []
    for point_id in sorted(point_ids):
        if point_id not in points3d:
            continue
        point = points3d[point_id]
        coords.append(np.array([point["x"], point["y"], point["z"]], dtype=np.float64))

    if not coords:
        return np.empty((0, 3), dtype=np.float64)
    return np.stack(coords, axis=0)


def _direction_to_erp_uv(
    directions: np.ndarray,
    erp_width: int,
    erp_height: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Convert unit directions in panorama coordinates to ERP pixel coordinates."""
    x = directions[:, 0]
    y = directions[:, 1]
    z = directions[:, 2]
    phi = np.arctan2(x, -z)
    theta = np.arcsin(np.clip(y, -1.0, 1.0))
    u = (phi + math.pi) / (2.0 * math.pi) * erp_width
    v = (math.pi / 2.0 - theta) / math.pi * erp_height
    return u, v


def _align_erp_depth_to_panorama_sparse_points(
    depth_map: np.ndarray,
    sparse_points_3d: np.ndarray,
    panorama_pose: np.ndarray,
) -> tuple[np.ndarray, float, float]:
    """Align ERP radial depth using sparse points projected into panorama space."""
    h, w = depth_map.shape
    ones = np.ones((sparse_points_3d.shape[0], 1), dtype=np.float64)
    points_hom = np.hstack([sparse_points_3d.astype(np.float64), ones])
    points_pano = (panorama_pose.astype(np.float64) @ points_hom.T).T[:, :3]

    metric_depth = np.linalg.norm(points_pano, axis=1)
    valid = metric_depth > 1e-8
    if not np.any(valid):
        raise ValueError("No valid sparse points remain after projection into panorama space")

    directions = points_pano[valid] / metric_depth[valid][:, None]
    u_img, v_img = _direction_to_erp_uv(directions, w, h)
    u_idx = np.mod(np.round(u_img).astype(int), w)
    v_idx = np.clip(np.round(v_img).astype(int), 0, h - 1)

    mono_depth_vals = depth_map[v_idx, u_idx].astype(np.float64)
    metric_depth_vals = metric_depth[valid]
    valid_mono = mono_depth_vals > 0
    if not np.any(valid_mono):
        raise ValueError("No valid ERP depth values at projected sparse point locations")

    mono_valid = mono_depth_vals[valid_mono]
    metric_valid = metric_depth_vals[valid_mono]
    ratios = metric_valid / mono_valid
    scale = float(np.median(ratios))
    residuals = metric_valid - scale * mono_valid
    shift = float(np.median(residuals))
    aligned_depth = depth_map.astype(np.float64) * scale + shift

    logger.info(
        "Panorama-rig ERP alignment: scale=%.4f, shift=%.4f, valid_points=%d/%d",
        scale,
        shift,
        int(np.sum(valid_mono)),
        sparse_points_3d.shape[0],
    )
    return aligned_depth.astype(np.float32), scale, shift


def _build_camera_pose(image_entry: dict) -> np.ndarray:
    """Build a 4x4 world-to-camera transformation matrix from a COLMAP image entry.

    COLMAP stores the camera pose as a quaternion (q_w, q_x, q_y, q_z)
    and translation (t_x, t_y, t_z) such that:

        X_cam = R * X_world + t

    where R is the rotation matrix derived from the quaternion and t is the
    translation vector. This is the world-to-camera (extrinsic) transformation.

    Args:
        image_entry: COLMAP image dict with keys ``qw``, ``qx``, ``qy``,
            ``qz``, ``tx``, ``ty``, ``tz``.

    Returns:
        4x4 world-to-camera transformation matrix (float64).
    """
    R = quat_to_rotation_matrix(
        image_entry["qw"],
        image_entry["qx"],
        image_entry["qy"],
        image_entry["qz"],
    )
    t = np.array(
        [image_entry["tx"], image_entry["ty"], image_entry["tz"]],
        dtype=np.float64,
    )

    pose = np.eye(4, dtype=np.float64)
    pose[:3, :3] = R
    pose[:3, 3] = t
    return pose


def _get_intrinsics_from_camera(
    camera_entry: dict, image_width: int, image_height: int
) -> dict[str, float]:
    """Extract pinhole intrinsics dict from a COLMAP camera entry.

    Supports PINHOLE (fx, fy, cx, cy) and SIMPLE_PINHOLE (f, cx, cy)
    camera models.

    Args:
        camera_entry: COLMAP camera dict with key ``params``.
        image_width: Image width (unused, for validation only).
        image_height: Image height (unused, for validation only).

    Returns:
        Dict with keys ``fx``, ``fy``, ``cx``, ``cy``.

    Raises:
        ValueError: If the camera model is not supported.
    """
    model = camera_entry.get("model", "PINHOLE")
    params = camera_entry["params"]

    if model == "PINHOLE":
        # params = [fx, fy, cx, cy]
        fx, fy, cx, cy = params[0], params[1], params[2], params[3]
    elif model == "SIMPLE_PINHOLE":
        # params = [f, cx, cy]
        f, cx, cy = params[0], params[1], params[2]
        fx = fy = f
    elif model == "SIMPLE_RADIAL":
        # params = [f, cx, cy, k]
        f, cx, cy = params[0], params[1], params[2]
        fx = fy = f
    else:
        # Fallback: assume first 4 params are fx, fy, cx, cy
        logger.warning(
            "Unsupported camera model '%s', assuming params = [fx, fy, cx, cy]",
            model,
        )
        fx, fy, cx, cy = params[0], params[1], params[2], params[3]

    return {"fx": float(fx), "fy": float(fy), "cx": float(cx), "cy": float(cy)}


def _get_sparse_points_for_image(
    image_entry: dict,
    points3d: dict[int, dict],
) -> np.ndarray:
    """Get the 3D coordinates of sparse points observed in a given image.

    Args:
        image_entry: COLMAP image dict with key ``point3D_ids``.
        points3d: Dict mapping point3D_id -> {x, y, z, ...}.

    Returns:
        Array of shape (N, 3) with 3D point coordinates in world frame.
        May be empty if no matching points are found.
    """
    point_ids = image_entry.get("point3D_ids", [])
    coords: list[np.ndarray] = []
    for pid in point_ids:
        if pid in points3d:
            pt = points3d[pid]
            coords.append(np.array([pt["x"], pt["y"], pt["z"]], dtype=np.float64))

    if not coords:
        return np.empty((0, 3), dtype=np.float64)

    return np.stack(coords, axis=0)


def align_depth_to_colmap(
    depth_map: np.ndarray,
    sparse_model: dict,
    image_name: str,
    rpg360_anchor: np.ndarray | None = None,
    colmap_dataset_dir: Path | None = None,
) -> tuple[np.ndarray, float, float]:
    """Align monocular depth to COLMAP sparse point metric scale.

    The alignment uses the median-of-ratios method: sparse 3D points are
    projected into the image, the monocular depth is sampled at those
    locations, and the median ratio of metric depth to monocular depth gives
    the scale factor. A shift (bias) is also computed.

    If an RPG360 anchor depth map is provided, the alignment is refined by
    blending the COLMAP-aligned depth with the anchor in regions where both
    are valid, using a weighted blend based on local NCC agreement.

    Args:
        depth_map: Monocular depth map of shape (H, W), dtype float32/64.
            Values should be positive (relative / monocular scale).
        sparse_model: Dictionary with keys ``cameras``, ``images``,
            ``points3D``, each matching the COLMAP text-format schema.
            - ``cameras``: dict[int, dict] with keys ``model``, ``width``,
              ``height``, ``params``.
            - ``images``: dict[int, dict] with keys ``name``, ``qw/qx/qy/qz``,
              ``tx/ty/tz``, ``camera_id``, ``point3D_ids``.
            - ``points3D``: dict[int, dict] with keys ``x``, ``y``, ``z``, ...
        image_name: Filename of the image to match in the sparse model
            (e.g. ``"frame_000.png"``). The image entry is found by
            comparing ``image_name`` against each image's ``name`` field.
        rpg360_anchor: Optional RPG360-derived metric depth map of the same
            shape (H, W). Used for local refinement in overlap regions.
            If ``None``, no refinement is performed.
        colmap_dataset_dir: Optional Stage 2 dataset directory. When it contains
            `panorama_rig.json` and `image_name` refers to an ERP frame rather
            than one virtual view, alignment falls back to a panorama-rig ERP
            projection path.

    Returns:
        A tuple ``(aligned_depth, scale, shift)`` where:

        - **aligned_depth**: Depth map aligned to metric scale, shape (H, W),
          dtype float32. Computed as ``depth_map * scale + shift``.
        - **scale**: Median-of-ratios scale factor (float).
        - **shift**: Median shift / bias after scaling (float).

    Raises:
        ValueError: If the image is not found in the sparse model, or
            if alignment fails due to insufficient valid projections.
    """
    cameras = sparse_model["cameras"]
    images = sparse_model["images"]
    points3d = sparse_model["points3D"]

    # Step 1: Find the image entry by name
    image_entry = _find_image_entry(images, image_name)
    panorama_rig_manifest = _load_panorama_rig_manifest(colmap_dataset_dir)

    if image_entry is None and panorama_rig_manifest is not None:
        panorama_frame_entries = _find_panorama_rig_frame_entries(
            images,
            image_name,
            panorama_rig_manifest,
        )
        if panorama_frame_entries:
            best_entry = max(
                panorama_frame_entries,
                key=lambda entry: len(entry.get("point3D_ids", [])),
            )
            panorama_pose = _build_panorama_pose_from_rig_image(best_entry, panorama_rig_manifest)
            sparse_points_3d = _get_sparse_points_for_images(panorama_frame_entries, points3d)
            if sparse_points_3d.shape[0] == 0:
                raise ValueError(
                    f"No sparse 3D points found for panorama-rig frame '{image_name}'. "
                    "Cannot compute ERP depth alignment without sparse observations."
                )

            aligned_depth, scale, shift = _align_erp_depth_to_panorama_sparse_points(
                depth_map=depth_map,
                sparse_points_3d=sparse_points_3d,
                panorama_pose=panorama_pose,
            )
            logger.info(
                "COLMAP panorama-rig alignment for '%s': scale=%.4f, shift=%.4f (%d sparse points across %d rig views)",
                image_name,
                scale,
                shift,
                sparse_points_3d.shape[0],
                len(panorama_frame_entries),
            )
            if rpg360_anchor is not None:
                aligned_depth = _refine_with_anchor(aligned_depth, rpg360_anchor)
                logger.info("Applied RPG360 anchor refinement for '%s'", image_name)
            return aligned_depth, scale, shift

    if image_entry is None:
        raise ValueError(
            f"Image '{image_name}' not found in sparse model. "
            f"Available images: {[img['name'] for img in images.values()]}"
        )

    # Step 2: Get camera intrinsics and extrinsics
    camera_id = image_entry["camera_id"]
    if camera_id not in cameras:
        raise ValueError(
            f"Camera ID {camera_id} (referenced by image '{image_name}') "
            f"not found in sparse model cameras."
        )

    camera_entry = cameras[camera_id]
    intrinsics = _get_intrinsics_from_camera(
        camera_entry, camera_entry["width"], camera_entry["height"]
    )
    camera_pose = _build_camera_pose(image_entry)

    # Step 3: Get sparse 3D points for this image
    sparse_points_3d = _get_sparse_points_for_image(image_entry, points3d)

    if sparse_points_3d.shape[0] == 0:
        raise ValueError(
            f"No sparse 3D points found for image '{image_name}'. "
            f"Cannot compute depth alignment without sparse observations."
        )

    # Step 4 & 5: Align using median-of-ratios
    aligned_depth, scale, shift = align_depth_median_ratio(
        depth=depth_map,
        sparse_points_3d=sparse_points_3d,
        camera_pose=camera_pose,
        intrinsics=intrinsics,
    )

    logger.info(
        "COLMAP alignment for '%s': scale=%.4f, shift=%.4f (%d sparse points)",
        image_name,
        scale,
        shift,
        sparse_points_3d.shape[0],
    )

    # Step 6: RPG360 anchor refinement
    if rpg360_anchor is not None:
        aligned_depth = _refine_with_anchor(aligned_depth, rpg360_anchor)
        logger.info("Applied RPG360 anchor refinement for '%s'", image_name)

    return aligned_depth, scale, shift


def _refine_with_anchor(
    aligned_depth: np.ndarray,
    anchor_depth: np.ndarray,
    blend_weight: float = 0.3,
) -> np.ndarray:
    """Refine aligned depth using an RPG360 anchor depth map.

    In regions where both depth maps are valid (positive), the result is
    a weighted blend: ``(1 - w) * colmap_aligned + w * anchor``. The blend
    weight is modulated by local NCC agreement between the two depth maps.

    Args:
        aligned_depth: COLMAP-aligned metric depth map, shape (H, W).
        anchor_depth: RPG360 anchor metric depth map, shape (H, W).
        blend_weight: Base blend weight for the anchor (0-1). Default 0.3
            means 30% anchor + 70% COLMAP-aligned.

    Returns:
        Refined depth map of shape (H, W), dtype float32.
    """
    if aligned_depth.shape != anchor_depth.shape:
        logger.warning(
            "Anchor shape %s does not match aligned depth %s; "
            "skipping anchor refinement.",
            anchor_depth.shape,
            aligned_depth.shape,
        )
        return aligned_depth

    # Valid region: both positive
    valid = (aligned_depth > 0) & (anchor_depth > 0)

    # Compute local NCC to modulate the blend weight
    from sphereforge.common.depth_utils import compute_ncc

    ncc_map = compute_ncc(aligned_depth, anchor_depth, window_size=11)

    # Modulate blend weight: higher NCC → more anchor influence
    # NCC in [0, 1] maps to blend_weight * NCC
    local_weight = blend_weight * np.clip(ncc_map, 0.0, 1.0)

    # Weighted blend
    refined = aligned_depth.astype(np.float64).copy()
    anchor_f64 = anchor_depth.astype(np.float64)
    weight = local_weight
    refined[valid] = (
        (1.0 - weight[valid]) * refined[valid] + weight[valid] * anchor_f64[valid]
    )

    return refined.astype(np.float32)
