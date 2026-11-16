"""Tests for CLI helpers that rewrite the sparse model."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

pycolmap = pytest.importorskip("pycolmap")

_REPO_ROOT = Path(__file__).resolve().parent.parent
_RIG_DATABASE = _REPO_ROOT / "data" / "e2e" / "colmap" / "database.db"
_RIG_IMAGES = _REPO_ROOT / "data" / "e2e" / "cubemaps" / "images"


def _build_model(tmp_path: Path, rig_model_dir: Path) -> Path:
    """Copy a rig-bearing model into *tmp_path* and return the model directory.

    Mapping takes minutes, so the reconstruction is built once per session and
    copied for each test.
    """
    out = tmp_path / "sparse"
    out.mkdir(parents=True)
    for item in rig_model_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, out / item.name)
    return out


def _map_rig_database(root: Path) -> Path:
    """Run the mapper under *root* and return the largest resulting model directory."""
    if not _RIG_DATABASE.exists() or not _RIG_IMAGES.is_dir():
        pytest.skip("no Stage 2 rig database available to build a fixture from")

    options = pycolmap.IncrementalPipelineOptions()
    options.multiple_models = False
    options.min_model_size = 2
    options.ba_refine_focal_length = False
    options.ba_refine_extra_params = False
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
    return root / str(best_id)


@pytest.fixture(scope="session")
def rig_model_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Map the rig database once per session into pytest's managed temp dir."""
    return _map_rig_database(tmp_path_factory.mktemp("sphereforge-cli-fixture"))


@pytest.fixture
def model_dir(tmp_path: Path, rig_model_dir: Path) -> Path:
    """A per-test copy of the session's rig-bearing model."""
    return _build_model(tmp_path, rig_model_dir)


@pytest.mark.slow
class TestRescaleSparsePoints:
    """The metric rescale must move points and cameras together."""

    def test_ratio_is_preserved(self, model_dir) -> None:
        """Scaling must not change camera_to_point_radius.

        Scaling only the points used to leave the cameras behind, which drove
        the ratio from 1.99 to 4.87 and pushed the camera path outside the
        geometry. The ratio is scale-invariant, so this is the invariant that
        catches it.
        """
        from sphereforge.cli import _rescale_sparse_points
        from sphereforge.stages.stage03_sfm.model_reader import read_sparse_model
        from sphereforge.stages.stage03_sfm.pycolmap_probe import _reconstruction_quality

        before = _reconstruction_quality(read_sparse_model(model_dir))

        _rescale_sparse_points(model_dir, 0.5)

        after = _reconstruction_quality(read_sparse_model(model_dir))
        assert after["camera_to_point_radius"] == pytest.approx(
            before["camera_to_point_radius"], abs=0.05
        )

    def test_positions_actually_shrink(self, model_dir) -> None:
        """The factor is applied to points and cameras alike."""
        from sphereforge.cli import _rescale_sparse_points
        from sphereforge.stages.stage03_sfm.model_reader import read_sparse_model
        from sphereforge.stages.stage03_sfm.pycolmap_probe import _reconstruction_quality

        before = _reconstruction_quality(read_sparse_model(model_dir))

        _rescale_sparse_points(model_dir, 0.5)

        after = _reconstruction_quality(read_sparse_model(model_dir))
        # The mapper is not deterministic, so the fixture's absolute radii vary.
        # What must hold is that both shrink by exactly the requested factor.
        assert after["point_radius_p50"] == pytest.approx(
            before["point_radius_p50"] * 0.5, rel=0.02
        )
        assert after["camera_radius_p50"] == pytest.approx(
            before["camera_radius_p50"] * 0.5, rel=0.02
        )

    def test_observations_survive_the_rewrite(self, model_dir) -> None:
        """Rewriting images.txt must not corrupt the 2D observation lines."""
        from sphereforge.cli import _rescale_sparse_points
        from sphereforge.stages.stage03_sfm.model_reader import read_sparse_model

        before = read_sparse_model(model_dir)
        n_before = sum(
            len([p for p in img.get("point3D_ids", []) if p >= 0])
            for img in before["images"].values()
        )

        _rescale_sparse_points(model_dir, 0.5)

        after = read_sparse_model(model_dir)
        n_after = sum(
            len([p for p in img.get("point3D_ids", []) if p >= 0])
            for img in after["images"].values()
        )
        assert n_after == n_before
        assert len(after["images"]) == len(before["images"])

