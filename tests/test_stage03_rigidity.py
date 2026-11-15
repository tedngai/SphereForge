"""Tests for panorama-rig rigidity enforcement (Stage 3)."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest

from sphereforge.stages.stage03_sfm.rigidity import (
    _SIDECAR_NAME,
    _average_rotations,
    _matrix_to_quat,
    _quat_to_matrix,
    apply_rigidity_to_model,
    enforce_rig_rigidity,
)

pycolmap = pytest.importorskip("pycolmap")

_REPO_ROOT = Path(__file__).resolve().parent.parent
_RIG_DATABASE = _REPO_ROOT / "data" / "e2e" / "colmap" / "database.db"
_RIG_IMAGES = _REPO_ROOT / "data" / "e2e" / "cubemaps" / "images"


def _rotation_y(angle_deg: float) -> np.ndarray:
    """Rotation matrix about the Y axis."""
    a = np.radians(angle_deg)
    return np.array(
        [[np.cos(a), 0.0, np.sin(a)], [0.0, 1.0, 0.0], [-np.sin(a), 0.0, np.cos(a)]]
    )


class TestQuaternionHelpers:
    """Quaternion/matrix conversion must round-trip."""

    def test_roundtrip(self) -> None:
        """A rotation survives matrix -> quat -> matrix."""
        rot = _rotation_y(37.0)
        assert np.allclose(_quat_to_matrix(_matrix_to_quat(rot)), rot, atol=1e-9)

    def test_quat_is_unit_norm(self) -> None:
        """The produced quaternion is normalised."""
        assert np.linalg.norm(_matrix_to_quat(_rotation_y(123.0))) == pytest.approx(1.0, abs=1e-9)

    def test_identity_roundtrip(self) -> None:
        """Identity maps to identity."""
        assert np.allclose(_quat_to_matrix(_matrix_to_quat(np.eye(3))), np.eye(3), atol=1e-9)


class TestAverageRotations:
    """The chordal mean must return a valid rotation."""

    def test_single_rotation_is_returned(self) -> None:
        """A single input is passed through."""
        rot = _rotation_y(20.0)
        assert np.allclose(_average_rotations([rot]), rot)

    def test_mean_is_orthonormal(self) -> None:
        """The averaged matrix is a proper rotation."""
        mean = _average_rotations([_rotation_y(a) for a in (0.0, 10.0, 20.0)])
        assert np.allclose(mean @ mean.T, np.eye(3), atol=1e-9)
        assert np.linalg.det(mean) == pytest.approx(1.0, abs=1e-9)

    def test_identical_rotations_average_to_themselves(self) -> None:
        """Averaging copies of one rotation returns that rotation."""
        rot = _rotation_y(45.0)
        assert np.allclose(_average_rotations([rot, rot, rot]), rot, atol=1e-9)


def _copy_source_model(tmp_path: Path) -> Path:
    """Copy a rig-bearing Stage 3 model into *tmp_path* and return its directory.

    pycolmap enforces strong invariants on ``Reconstruction`` (frames must own
    their data ids, images must be registered), so a hand-assembled model does
    not survive a write/reload cycle. The reliable source is a reconstruction
    the mapper produced from the rig database. Mapping takes minutes, so the
    result is built once per session and copied from there.
    """
    cached = _session_rig_model()
    out = tmp_path / "sparse" / "0"
    out.mkdir(parents=True)
    for item in cached.iterdir():
        if item.is_file():
            shutil.copy2(item, out / item.name)
    return out


_RIG_MODEL_CACHE: Path | None = None


def _session_rig_model() -> Path:
    """Build (once) a rig-bearing reconstruction and return its directory."""
    global _RIG_MODEL_CACHE
    if _RIG_MODEL_CACHE is not None and _RIG_MODEL_CACHE.exists():
        return _RIG_MODEL_CACHE
    if not _RIG_DATABASE.exists() or not _RIG_IMAGES.is_dir():
        pytest.skip("no Stage 2 rig database available to build a fixture from")

    root = Path(tempfile.mkdtemp(prefix="sphereforge-rig-fixture-"))
    options = pycolmap.IncrementalPipelineOptions()
    options.multiple_models = False
    options.min_model_size = 2
    options.ba_refine_focal_length = False
    options.ba_refine_extra_params = False
    options.ba_refine_sensor_from_rig = False
    options.mapper.init_min_tri_angle = 4.0
    options.mapper.abs_pose_min_num_inliers = 12
    options.triangulation.min_angle = 0.5
    reconstructions = pycolmap.incremental_mapping(
        database_path=str(_RIG_DATABASE),
        image_path=str(_RIG_IMAGES),
        output_path=str(root),
        options=options,
    )
    if not reconstructions:
        pytest.skip("mapper produced no reconstruction for the fixture")
    best_id = max(reconstructions, key=lambda k: len(reconstructions[k].images))
    model_dir = root / str(best_id)
    if not any(rig.num_sensors() > 1 for rig in reconstructions[best_id].rigs.values()):
        pytest.skip("mapper did not produce a multi-sensor rig")
    _RIG_MODEL_CACHE = model_dir
    return model_dir


@pytest.mark.slow
class TestEnforceRigRigidity:
    """A rig-constrained model is rigid by construction; the check must see that."""

    def test_mapped_rig_model_is_already_rigid(self, tmp_path) -> None:
        """Optical centres of a frame coincide, so nothing is repaired.

        (The old check compared raw translations, which differ per sensor, and
        "repaired" every frame of a correct model into wrong poses.)
        """
        model_dir = _copy_source_model(tmp_path)

        summary = enforce_rig_rigidity(model_dir)

        assert summary["frames_repaired"] == 0
        assert summary["max_spread_before"] < 1e-6
        assert not (model_dir / _SIDECAR_NAME).exists()

    def test_stale_sidecar_is_removed(self, tmp_path) -> None:
        """A sidecar left by an older (buggy) run must not override good poses."""
        model_dir = _copy_source_model(tmp_path)
        (model_dir / _SIDECAR_NAME).write_text('{"x": {}}', encoding="utf-8")

        enforce_rig_rigidity(model_dir)

        assert not (model_dir / _SIDECAR_NAME).exists()

    def test_mapped_rig_path_is_not_degenerate(self, tmp_path) -> None:
        """The rig model's camera path must not be mistaken for a collapse."""
        from sphereforge.stages.stage03_sfm.pycolmap_probe import _camera_path_is_degenerate

        model_dir = _copy_source_model(tmp_path)
        assert _camera_path_is_degenerate(model_dir) is False


class TestCameraCentre:
    """Positions must come from -R^T t, never from the raw translation."""

    def test_centre_is_minus_rt_t(self) -> None:
        """Two sensors at one centre with different rotations share -R^T t."""
        from sphereforge.stages.stage03_sfm.rigidity import camera_centre_from_pose

        centre = np.array([1.0, -2.0, 0.5])
        poses = []
        for yaw in (0.0, 90.0, 200.0):
            rot = _rotation_y(yaw)
            pose = pycolmap.Rigid3d()
            pose.rotation = pycolmap.Rotation3d(rot)
            pose.translation = -rot @ centre
            poses.append(pose)
        translations = [np.asarray(p.translation) for p in poses]
        assert np.ptp(np.stack(translations), axis=0).max() > 1.0  # raw t differs
        for pose in poses:
            assert np.allclose(camera_centre_from_pose(pose), centre, atol=1e-9)
        # pycolmap 4.x exposes cam_from_world as a method.
        assert np.allclose(camera_centre_from_pose(lambda: poses[0]), centre, atol=1e-9)


class TestRigidFramePoses:
    """Repair math for a frame whose sensors disagree."""

    def test_snaps_to_one_centre_and_keeps_rig_rotations(self) -> None:
        """Output poses share the mean centre and respect cam_from_rig."""
        from sphereforge.stages.stage03_sfm.rigidity import rigid_frame_poses

        rng = np.random.default_rng(0)
        rig_from_world = _rotation_y(25.0)
        cam_from_rig = [np.eye(3), _rotation_y(90.0), _rotation_y(180.0), _rotation_y(270.0)]
        true_centre = np.array([0.3, 0.1, -0.7])
        rotations, centres = [], []
        for s in cam_from_rig:
            noise = _rotation_y(float(rng.normal(0.0, 0.5)))
            rotations.append(noise @ s @ rig_from_world)
            centres.append(true_centre + rng.normal(0.0, 0.2, size=3))

        poses = rigid_frame_poses(rotations, centres, cam_from_rig)

        mean_centre = np.mean(np.stack(centres), axis=0)
        implied_rigs = []
        for (rot, trans), s in zip(poses, cam_from_rig, strict=True):
            assert np.allclose(-rot.T @ trans, mean_centre, atol=1e-9)
            implied_rigs.append(s.T @ rot)
        for implied in implied_rigs[1:]:
            assert np.allclose(implied, implied_rigs[0], atol=1e-9)
        # Close to the true rig orientation despite the per-sensor noise.
        assert np.allclose(implied_rigs[0], rig_from_world, atol=0.02)


class TestPathDegeneracy:
    """Only a path that collapsed to a point counts as degenerate."""

    def test_straight_path_is_not_degenerate(self) -> None:
        """A straight capture path (like the synthetic room) is legitimate."""
        from sphereforge.stages.stage03_sfm.pycolmap_probe import _path_is_degenerate

        t = np.linspace(0.0, 1.0, 12)[:, None]
        path = np.hstack([-0.9 + 1.8 * t, np.zeros_like(t), -0.8 + 1.6 * t])
        points = np.random.default_rng(1).uniform(-2.5, 2.5, size=(500, 3))
        assert _path_is_degenerate(path, points) is False

    def test_collapsed_path_is_degenerate(self) -> None:
        """All frames at (nearly) one centre: pure-rotation collapse."""
        from sphereforge.stages.stage03_sfm.pycolmap_probe import _path_is_degenerate

        path = np.random.default_rng(2).normal(0.0, 1e-4, size=(12, 3))
        points = np.random.default_rng(3).uniform(-2.5, 2.5, size=(500, 3))
        assert _path_is_degenerate(path, points) is True

    def test_too_few_frames_is_not_judged(self) -> None:
        """Two frames cannot establish a collapse."""
        from sphereforge.stages.stage03_sfm.pycolmap_probe import _path_is_degenerate

        assert _path_is_degenerate(np.zeros((2, 3)), np.ones((10, 3))) is False


class TestApplyRigidityToModel:
    """Downstream stages must receive the corrected poses."""

    def test_missing_sidecar_is_a_no_op(self, tmp_path) -> None:
        """Without a sidecar the model is returned unchanged."""
        model = {"images": {"1": {"name": "a/b.png", "tx": 5.0, "ty": 0.0, "tz": 0.0}}}
        model["_source_dir"] = str(tmp_path)
        assert apply_rigidity_to_model(model)["images"]["1"]["tx"] == 5.0

    def test_poses_are_replaced(self, tmp_path) -> None:
        """Poses in the model are overwritten from the sidecar."""
        import json

        (tmp_path / _SIDECAR_NAME).write_text(
            json.dumps({"a/b.png": {"qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                                    "tx": 1.0, "ty": 2.0, "tz": 3.0}}),
            encoding="utf-8",
        )
        model = {
            "_source_dir": str(tmp_path),
            "images": {"1": {"name": "a/b.png", "tx": 9.0, "ty": 9.0, "tz": 9.0}},
        }

        result = apply_rigidity_to_model(model)

        assert result["images"]["1"]["tx"] == 1.0
        assert result["images"]["1"]["tz"] == 3.0


