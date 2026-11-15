"""Enforce panorama-rig rigidity on a COLMAP reconstruction.

A panorama rig captures every face of the sphere from a single optical centre,
so all sensors in a frame must share one *optical centre* (``-R^T t``), up to
their fixed rotations. Note that their raw ``cam_from_world`` translations do
**not** coincide: ``t = -R c`` differs per sensor because each has its own
rotation. A rig-constrained pycolmap model is rigid by construction, so the
check here normally finds nothing to repair.

pycolmap cannot represent per-image overrides in its model:
``Image.cam_from_world`` is read-only, and ``Frame.set_cam_from_world``
recomputes the frame pose from the camera it is given. Any repair is therefore
stored in a sidecar file next to the model; :func:`apply_rigidity_to_model`
applies it to the dict that downstream stages read.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger("sphereforge.stage03.rigidity")

_SIDECAR_NAME = "rig_rigidity.json"


def _quat_to_matrix(quat_xyzw: np.ndarray) -> np.ndarray:
    """Convert a (x, y, z, w) quaternion to a 3x3 rotation matrix."""
    x, y, z, w = quat_xyzw
    n = np.sqrt(x * x + y * y + z * z + w * w)
    if n < 1e-12:
        return np.eye(3)
    x, y, z, w = x / n, y / n, z / n, w / n
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )


def _matrix_to_quat(rotation: np.ndarray) -> np.ndarray:
    """Convert a 3x3 rotation matrix to an (x, y, z, w) quaternion."""
    m = rotation
    trace = m[0, 0] + m[1, 1] + m[2, 2]
    if trace > 0:
        s = 0.5 / np.sqrt(trace + 1.0)
        w = 0.25 / s
        x = (m[2, 1] - m[1, 2]) * s
        y = (m[0, 2] - m[2, 0]) * s
        z = (m[1, 0] - m[0, 1]) * s
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = 2.0 * np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2])
        w = (m[2, 1] - m[1, 2]) / s
        x = 0.25 * s
        y = (m[0, 1] + m[1, 0]) / s
        z = (m[0, 2] + m[2, 0]) / s
    elif m[1, 1] > m[2, 2]:
        s = 2.0 * np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2])
        w = (m[0, 2] - m[2, 0]) / s
        x = (m[0, 1] + m[1, 0]) / s
        y = 0.25 * s
        z = (m[1, 2] + m[2, 1]) / s
    else:
        s = 2.0 * np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1])
        w = (m[1, 0] - m[0, 1]) / s
        x = (m[0, 2] + m[2, 0]) / s
        y = (m[1, 2] + m[2, 1]) / s
        z = 0.25 * s
    q = np.array([x, y, z, w], dtype=np.float64)
    return q / np.linalg.norm(q)


def _average_rotations(rotations: list[np.ndarray]) -> np.ndarray:
    """Average rotation matrices via the chordal (Frobenius) mean.

    Args:
        rotations: List of 3x3 rotation matrices.

    Returns:
        The nearest rotation matrix to the arithmetic mean.
    """
    if len(rotations) == 1:
        return rotations[0]
    mean = np.mean(np.stack(rotations), axis=0)
    u, _, vt = np.linalg.svd(mean)
    rot = u @ vt
    if np.linalg.det(rot) < 0:
        u[:, -1] *= -1
        rot = u @ vt
    return rot


def camera_centre_from_pose(pose: object) -> np.ndarray:
    """Optical centre ``-R^T t`` of a pycolmap ``cam_from_world`` pose.

    The raw ``translation`` of ``cam_from_world`` is *not* the camera position:
    for two sensors that share one optical centre but look in different
    directions, the translations differ by their rotations. Every geometric
    test on camera positions must use this centre instead.

    Args:
        pose: A pycolmap ``Rigid3d`` (or a zero-argument callable returning
            one, as in pycolmap 4.x ``Image.cam_from_world``).

    Returns:
        World-space optical centre ``(3,)`` float64.
    """
    if callable(pose):
        pose = pose()
    rotation = np.asarray(pose.rotation.matrix(), dtype=np.float64)
    translation = np.asarray(pose.translation, dtype=np.float64)
    return -rotation.T @ translation


def rigid_frame_poses(
    cam_from_world_rotations: list[np.ndarray],
    centres: list[np.ndarray],
    cam_from_rig_rotations: list[np.ndarray],
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Snap one frame's sensor poses onto a rigid, single-centre rig.

    Each sensor implies a rig orientation ``rig_from_world = S^T R`` (``S`` the
    fixed ``cam_from_rig`` rotation, ``R`` the sensor's ``cam_from_world``
    rotation). These are averaged, the rig centre is the mean optical centre,
    and every sensor is re-posed as ``R' = S rig_from_world``,
    ``t' = -R' c``.

    Args:
        cam_from_world_rotations: Per-sensor ``cam_from_world`` rotations.
        centres: Per-sensor optical centres (``-R^T t``).
        cam_from_rig_rotations: Per-sensor fixed ``cam_from_rig`` rotations.

    Returns:
        Per-sensor ``(rotation, translation)`` ``cam_from_world`` poses.
    """
    rig_from_world = _average_rotations(
        [s.T @ r for r, s in zip(cam_from_world_rotations, cam_from_rig_rotations, strict=True)]
    )
    centre = np.mean(np.stack(centres), axis=0)
    poses = []
    for s in cam_from_rig_rotations:
        rotation = s @ rig_from_world
        poses.append((rotation, -rotation @ centre))
    return poses


def enforce_rig_rigidity(
    sparse_dir: Path,
    max_centre_spread: float = 0.05,
) -> dict[str, float]:
    """Check (and if needed repair) panorama-rig rigidity; record it in a sidecar.

    A rig-constrained pycolmap model is rigid by construction (each image pose
    is ``sensor_from_rig * rig_from_world``), so normally nothing is repaired.
    Earlier versions measured the *translations* of ``cam_from_world`` instead
    of the optical centres; those legitimately differ between sensors that look
    in different directions, so correct models were reported as "scattered" and
    rewritten with wrong poses.

    Frames whose sensor optical centres disagree by more than
    *max_centre_spread* (in model units) are snapped onto one centre with
    :func:`rigid_frame_poses`.

    Args:
        sparse_dir: Directory containing the COLMAP sparse model.
        max_centre_spread: Largest per-frame distance of a sensor centre from
            the frame's mean centre that counts as already rigid.

    Returns:
        Summary statistics (``frames_repaired``, ``max_spread_before``).
    """
    import pycolmap

    sparse_dir = Path(sparse_dir)
    reconstruction = pycolmap.Reconstruction(str(sparse_dir))

    rig = next(iter(reconstruction.rigs.values()))
    ref_sensor_id = rig.ref_sensor_id.id

    # Fixed cam_from_rig rotation of every sensor (identity for the reference).
    cam_from_rig: dict[int, np.ndarray] = {}
    for sensor_id in rig.sensor_ids():
        if sensor_id.id == ref_sensor_id:
            cam_from_rig[sensor_id.id] = np.eye(3)
        else:
            transform = rig.sensor_from_rig(sensor_id)
            cam_from_rig[sensor_id.id] = np.asarray(
                transform.rotation.matrix(), dtype=np.float64
            )

    frames_repaired = 0
    max_spread_before = 0.0
    corrected: dict[str, dict[str, float]] = {}
    for frame in reconstruction.frames.values():
        images = [reconstruction.image(d.id) for d in frame.data_ids]
        images = [img for img in images if img.has_pose]
        if len(images) < 2:
            continue

        centres = [camera_centre_from_pose(img.cam_from_world) for img in images]
        stacked = np.stack(centres)
        spread = float(np.max(np.linalg.norm(stacked - stacked.mean(axis=0), axis=1)))
        max_spread_before = max(max_spread_before, spread)
        if spread <= max_centre_spread:
            continue

        rotations = []
        for img in images:
            pose = img.cam_from_world
            pose = pose() if callable(pose) else pose
            rotations.append(np.asarray(pose.rotation.matrix(), dtype=np.float64))
        sensor_rots = [cam_from_rig[img.data_id.sensor_id.id] for img in images]
        for img, (rotation, translation) in zip(
            images, rigid_frame_poses(rotations, centres, sensor_rots), strict=True
        ):
            quat = _matrix_to_quat(rotation)
            corrected[str(img.name)] = {
                "qw": float(quat[3]),
                "qx": float(quat[0]),
                "qy": float(quat[1]),
                "qz": float(quat[2]),
                "tx": float(translation[0]),
                "ty": float(translation[1]),
                "tz": float(translation[2]),
            }
        frames_repaired += 1

    sidecar = sparse_dir / _SIDECAR_NAME
    if corrected:
        sidecar.write_text(json.dumps(corrected, indent=1), encoding="utf-8")
    elif sidecar.exists():
        # A stale sidecar from an older run would override the correct poses.
        sidecar.unlink()
    summary = {
        "frames_repaired": float(frames_repaired),
        "max_spread_before": max_spread_before,
    }
    logger.info(
        "Rig rigidity check: %d frame(s) repaired (max sensor-centre spread %.3g)",
        frames_repaired,
        max_spread_before,
    )
    return summary


def apply_rigidity_to_model(sparse_model: dict) -> dict:
    """Apply the corrected rig poses in *sparse_model* in place.

    Args:
        sparse_model: Parsed sparse model from :func:`read_sparse_model`.

    Returns:
        The same model, with image poses replaced by their rigid values.
    """
    source_dir = sparse_model.get("_source_dir")
    if source_dir is None:
        return sparse_model
    sidecar = Path(source_dir) / _SIDECAR_NAME
    if not sidecar.exists():
        return sparse_model

    try:
        corrected = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        logger.warning("Could not read rig rigidity sidecar %s: %s", sidecar, exc)
        return sparse_model

    applied = 0
    for image in sparse_model.get("images", {}).values():
        pose = corrected.get(str(image.get("name")))
        if pose is None:
            continue
        image.update(pose)
        applied += 1
    if applied:
        logger.info("Applied rigid rig poses to %d image(s)", applied)
    return sparse_model
