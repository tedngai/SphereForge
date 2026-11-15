"""Tests for SphereForge Stage 8: Post-Processing & Export."""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_gaussians(synthetic_gaussians):
    """Convert conftest synthetic gaussians to the dict format used by Stage 8."""
    g = synthetic_gaussians
    return {
        "positions": g["positions"],
        "colors": g["colors"],
        "opacities": g["opacities"],
        "scales": g["scales"],
        "rotations": g["rotations"],
    }


@pytest.fixture
def sample_ply(tmp_path, sample_gaussians):
    """Write sample Gaussians to a PLY file and return the path."""
    from sphereforge.common.io import write_ply

    ply_path = tmp_path / "test.ply"
    g = sample_gaussians
    write_ply(
        ply_path,
        positions=g["positions"],
        colors=g["colors"],
        opacities=g["opacities"],
        scales=g["scales"],
        rotations=g["rotations"],
    )
    return ply_path


# ---------------------------------------------------------------------------
# T8.1: Final RAP pruning
# ---------------------------------------------------------------------------


class TestFinalPruning:
    """Tests for final_rap_prune."""

    def test_removes_low_opacity(self, sample_gaussians):
        from sphereforge.stages.stage08_export.final_pruning import final_rap_prune

        # Set some opacities very low
        g = sample_gaussians.copy()
        g["opacities"] = g["opacities"].copy()
        g["opacities"][:10] = 0.001  # Below min_opacity=0.005

        result, stats = final_rap_prune(g, min_opacity=0.005)
        assert result["positions"].shape[0] < g["positions"].shape[0]
        assert stats["n_pruned_opaque"] >= 0

    def test_preserves_high_opacity(self, sample_gaussians):
        from sphereforge.stages.stage08_export.final_pruning import final_rap_prune

        g = sample_gaussians.copy()
        g["opacities"] = np.ones(g["opacities"].shape, dtype=np.float32)  # All high

        result, stats = final_rap_prune(g, min_opacity=0.005)
        assert result["positions"].shape[0] == g["positions"].shape[0]

    def test_stats_keys(self, sample_gaussians):
        from sphereforge.stages.stage08_export.final_pruning import final_rap_prune

        _, stats = final_rap_prune(sample_gaussians)
        assert "n_before" in stats
        assert "n_after" in stats

    def test_logit_encoded_opacity_is_activated_before_pruning(self, sample_gaussians):
        from sphereforge.stages.stage08_export.final_pruning import final_rap_prune

        g = sample_gaussians.copy()
        g["opacities"] = np.full(g["opacities"].shape, -2.0, dtype=np.float32)
        g["scales"] = np.full(g["scales"].shape, -2.0, dtype=np.float32)

        result, stats = final_rap_prune(g, min_opacity=0.005)
        assert result["positions"].shape[0] == g["positions"].shape[0]
        assert stats["n_pruned_opaque"] == 0


# ---------------------------------------------------------------------------
# T8.2: Compact box culling
# ---------------------------------------------------------------------------


class TestCompactCulling:
    """Tests for compact_box_cull."""

    def test_returns_boolean_mask(self, sample_gaussians):
        from sphereforge.stages.stage08_export.compact_culling import compact_box_cull

        mask = compact_box_cull(
            sample_gaussians["positions"],
            sample_gaussians["scales"],
            sample_gaussians["rotations"],
        )
        assert mask.dtype == bool
        assert mask.shape[0] == sample_gaussians["positions"].shape[0]

    def test_keeps_most_gaussians(self, sample_gaussians):
        from sphereforge.stages.stage08_export.compact_culling import compact_box_cull

        mask = compact_box_cull(
            sample_gaussians["positions"],
            sample_gaussians["scales"],
            sample_gaussians["rotations"],
            sigma=3.0,
        )
        # Most Gaussians should be kept (reasonable scales)
        assert mask.sum() > 0

    def test_extreme_sigma_removes_more(self, sample_gaussians):
        from sphereforge.stages.stage08_export.compact_culling import compact_box_cull

        mask_loose = compact_box_cull(
            sample_gaussians["positions"],
            sample_gaussians["scales"],
            sample_gaussians["rotations"],
            sigma=5.0,
        )
        mask_tight = compact_box_cull(
            sample_gaussians["positions"],
            sample_gaussians["scales"],
            sample_gaussians["rotations"],
            sigma=1.0,
        )
        # Tighter sigma should remove more (or same)
        assert mask_tight.sum() <= mask_loose.sum()


# ---------------------------------------------------------------------------
# T8.3: PLY round-trip
# ---------------------------------------------------------------------------


class TestPLYRoundTrip:
    """Tests for PLY write/read consistency."""

    def test_round_trip(self, tmp_path, sample_gaussians):
        from sphereforge.common.io import read_ply, write_ply

        g = sample_gaussians
        ply_path = tmp_path / "roundtrip.ply"
        write_ply(ply_path, g["positions"], g["colors"], g["opacities"], g["scales"], g["rotations"])

        loaded = read_ply(ply_path)
        assert loaded["positions"].shape == g["positions"].shape
        assert loaded["opacities"].shape == g["opacities"].shape
        np.testing.assert_allclose(loaded["positions"], g["positions"], atol=1e-5)


# ---------------------------------------------------------------------------
# T8.4: SOG export
# ---------------------------------------------------------------------------


class TestSOGExport:
    """Tests for SOG format export."""

    def test_creates_file(self, sample_ply, tmp_path):
        from sphereforge.stages.stage08_export.sog_export import export_sog

        sog_path = export_sog(sample_ply, tmp_path / "test.sog")
        assert sog_path.exists()

    def test_header_magic(self, sample_ply, tmp_path):
        from sphereforge.stages.stage08_export.sog_export import export_sog

        sog_path = export_sog(sample_ply, tmp_path / "test.sog")
        with open(sog_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"SOGF"

    def test_has_n_clusters(self, sample_ply, tmp_path):
        from sphereforge.stages.stage08_export.sog_export import export_sog

        sog_path = export_sog(sample_ply, tmp_path / "test.sog", n_clusters=8)
        assert sog_path.exists()
        assert sog_path.stat().st_size > 0


# ---------------------------------------------------------------------------
# T8.5: SPZ export
# ---------------------------------------------------------------------------


class TestSPZExport:
    """Tests for SPZ format export."""

    def test_creates_file(self, sample_ply, tmp_path):
        from sphereforge.stages.stage08_export.spz_export import export_spz

        spz_path = export_spz(sample_ply, tmp_path / "test.spz")
        assert spz_path.exists()

    def test_header_magic(self, sample_ply, tmp_path):
        from sphereforge.stages.stage08_export.spz_export import export_spz

        spz_path = export_spz(sample_ply, tmp_path / "test.spz")
        with open(spz_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"SPZF"

    def test_morton_ordering(self):
        """Verify Morton codes produce spatially-ordered indices."""
        from sphereforge.stages.stage08_export.spz_export import _compute_morton_codes

        # Points along x-axis should have increasing Morton codes
        positions = np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0]], dtype=np.float32)
        morton = _compute_morton_codes(positions)
        # Morton codes should be monotonically increasing for this simple case
        assert np.all(np.diff(morton) >= 0)


# ---------------------------------------------------------------------------
# T8.6: HTML viewer
# ---------------------------------------------------------------------------


class TestHTMLViewer:
    """Tests for HTML viewer generation."""

    def test_creates_html(self, sample_ply, tmp_path):
        from sphereforge.stages.stage08_export.html_viewer import generate_html_viewer

        html_path = generate_html_viewer(sample_ply, tmp_path / "viewer.html")
        assert html_path.exists()

    def test_contains_viewer_script(self, sample_ply, tmp_path):
        from sphereforge.stages.stage08_export.html_viewer import generate_html_viewer

        html_path = generate_html_viewer(sample_ply, tmp_path / "viewer.html")
        content = html_path.read_text()
        assert "gaussian-splats-3d" in content.lower() or "GaussianSplats3D" in content

    def test_contains_ply_reference(self, sample_ply, tmp_path):
        from sphereforge.stages.stage08_export.html_viewer import generate_html_viewer

        html_path = generate_html_viewer(sample_ply, tmp_path / "viewer.html")
        content = html_path.read_text()
        assert sample_ply.name in content


# ---------------------------------------------------------------------------
# T8.7: Mesh extraction
# ---------------------------------------------------------------------------


class TestMeshExtraction:
    """Tests for navigation mesh extraction."""

    def test_convex_hull_fallback(self, tmp_path):
        """Convex hull always works (scipy is a core dep)."""
        from sphereforge.stages.stage08_export.mesh_extraction import extract_navigation_mesh

        positions = np.random.randn(100, 3).astype(np.float32) * 5.0
        mesh_path = extract_navigation_mesh(positions, tmp_path / "mesh.obj", method="convex_hull")
        assert mesh_path.exists()

    def test_obj_format(self, tmp_path):
        from sphereforge.stages.stage08_export.mesh_extraction import extract_navigation_mesh

        positions = np.random.randn(50, 3).astype(np.float32) * 5.0
        mesh_path = extract_navigation_mesh(positions, tmp_path / "mesh.obj", method="convex_hull")
        content = mesh_path.read_text()
        assert content.startswith("#")
        assert "v " in content  # Vertices
        assert "f " in content  # Faces


# ---------------------------------------------------------------------------
# T8.8: Pipeline orchestration
# ---------------------------------------------------------------------------


class TestPipeline:
    """Tests for Stage 8 pipeline."""

    def test_resolve_max_scale_ratio(self):
        from sphereforge.stages.stage08_export.pipeline import (
            AUTO_MAX_SCALE_RATIO,
            _resolve_max_scale_ratio,
        )

        # "auto" must be an outlier filter, not a detail filter: a 0.1 ratio
        # rejected every Gaussian and emptied the export.
        assert _resolve_max_scale_ratio("auto") == AUTO_MAX_SCALE_RATIO
        assert _resolve_max_scale_ratio("0.25") == 0.25

    def test_resolve_max_scale_ratio_rejects_invalid(self):
        from sphereforge.stages.stage08_export.pipeline import _resolve_max_scale_ratio

        with pytest.raises(ValueError, match="stage08.max_scale"):
            _resolve_max_scale_ratio("0")

        with pytest.raises(ValueError, match="Invalid stage08.max_scale"):
            _resolve_max_scale_ratio("huge")

    def test_exports_ply_by_default(self, sample_ply, tmp_path):
        from sphereforge.config import Stage08Config
        from sphereforge.stages.stage08_export.pipeline import run_stage08

        config = Stage08Config(export_format=["ply"], rap_final_pass=False, compact_box_culling=False)
        result = run_stage08(config, sample_ply, tmp_path / "export")
        assert "ply" in result["output_paths"]
        assert result["output_paths"]["ply"].exists()

    def test_multiple_formats(self, sample_ply, tmp_path):
        from sphereforge.config import Stage08Config
        from sphereforge.stages.stage08_export.pipeline import run_stage08

        config = Stage08Config(
            export_format=["ply", "sog", "html"],
            rap_final_pass=False,
            compact_box_culling=False,
        )
        result = run_stage08(config, sample_ply, tmp_path / "export")
        assert "ply" in result["output_paths"]
        assert "sog" in result["output_paths"]
        assert "html" in result["output_paths"]

    def test_stats_populated(self, sample_ply, tmp_path):
        from sphereforge.config import Stage08Config
        from sphereforge.stages.stage08_export.pipeline import run_stage08

        config = Stage08Config(export_format=["ply"], rap_final_pass=True, compact_box_culling=True)
        result = run_stage08(config, sample_ply, tmp_path / "export")
        assert "n_before" in result["stats"]
        assert "n_after" in result["stats"]


class TestFinalPruningNonFinite:
    """Non-finite Gaussians must not destroy the whole export."""

    def _gaussians(self, n: int = 6) -> dict:
        return {
            "positions": np.random.default_rng(0).normal(size=(n, 3)).astype(np.float32),
            "opacities": np.full(n, 0.9, dtype=np.float32),
            "scales": np.full((n, 3), 0.01, dtype=np.float32),
            "rotations": np.tile(np.array([1, 0, 0, 0], dtype=np.float32), (n, 1)),
            "colors": np.full((n, 3), 0.5, dtype=np.float32),
        }

    def test_nan_position_is_dropped_not_fatal(self) -> None:
        """One NaN position used to make the scene extent NaN and prune all."""
        from sphereforge.stages.stage08_export.final_pruning import final_rap_prune

        gaussians = self._gaussians()
        gaussians["positions"][2] = np.nan

        pruned, stats = final_rap_prune(gaussians)

        assert stats["n_after"] > 0
        assert pruned["positions"].shape[0] == stats["n_after"]
        assert np.isfinite(pruned["positions"]).all()

    def test_all_finite_is_unchanged(self) -> None:
        """A clean scene keeps every Gaussian."""
        from sphereforge.stages.stage08_export.final_pruning import final_rap_prune

        pruned, stats = final_rap_prune(self._gaussians())

        assert stats["n_after"] == 6
        assert np.isfinite(pruned["positions"]).all()


class TestPruneNeverEmptiesExport:
    """A misconfigured threshold must not silently produce an empty scene."""

    def _gaussians(self, n: int = 8) -> dict:
        return {
            "positions": np.random.default_rng(0).normal(size=(n, 3)).astype(np.float32),
            "opacities": np.full(n, 0.9, dtype=np.float32),
            "scales": np.full((n, 3), 1.0, dtype=np.float32),
            "rotations": np.tile(np.array([1, 0, 0, 0], dtype=np.float32), (n, 1)),
            "colors": np.full((n, 3), 0.5, dtype=np.float32),
        }

    def test_impossible_scale_ratio_keeps_input(self) -> None:
        """A ratio that rejects every Gaussian falls back to keeping them all."""
        from sphereforge.stages.stage08_export.final_pruning import final_rap_prune

        # Scales of 1.0 against a tiny extent: ratio 0.01 rejects everything.
        pruned, stats = final_rap_prune(self._gaussians(), max_scale_ratio=0.01)

        assert stats["n_after"] == stats["n_before"]
        assert pruned["positions"].shape[0] == stats["n_before"]

    def test_reasonable_ratio_still_prunes(self) -> None:
        """The guard must not disable pruning that legitimately removes some."""
        from sphereforge.stages.stage08_export.final_pruning import final_rap_prune

        gaussians = self._gaussians()
        gaussians["opacities"][:2] = 0.0  # clearly transparent

        _, stats = final_rap_prune(gaussians, min_opacity=0.01, max_scale_ratio=0.5)

        assert stats["n_pruned_opaque"] == 2
        assert stats["n_after"] < stats["n_before"]


class TestAutoMaxScaleRatio:
    """The "auto" scale ratio must be an outlier filter, not a detail filter."""

    def test_auto_ratio_keeps_typical_gaussians(self) -> None:
        """Typical Gaussians are a large fraction of scene extent.

        A ratio of 0.1 (0.68 m against a 6.8 m scene) rejected every Gaussian
        and emptied the export; the auto value must be well above that.
        """
        from sphereforge.stages.stage08_export.pipeline import (
            AUTO_MAX_SCALE_RATIO,
            _resolve_max_scale_ratio,
        )

        assert AUTO_MAX_SCALE_RATIO >= 0.5
        assert _resolve_max_scale_ratio("auto") == AUTO_MAX_SCALE_RATIO

    def test_explicit_ratio_is_honoured(self) -> None:
        """A numeric config value is used verbatim."""
        from sphereforge.stages.stage08_export.pipeline import _resolve_max_scale_ratio

        assert _resolve_max_scale_ratio("0.25") == 0.25

    def test_invalid_ratio_is_rejected(self) -> None:
        """A non-positive ratio is a configuration error."""
        import pytest

        from sphereforge.stages.stage08_export.pipeline import _resolve_max_scale_ratio

        with pytest.raises(ValueError):
            _resolve_max_scale_ratio("0")


class TestExportedQuaternionsAreUnitNorm:
    """3DGS PLY files store unit quaternions; export must normalise them."""

    def test_drifted_rotations_are_normalised(self, tmp_path) -> None:
        """Optimisation drifts quaternions off the unit sphere (0.58-1.62).

        The exported file must be standards-compliant regardless.
        """
        import numpy as np

        from sphereforge.common.io import read_ply
        from sphereforge.config import Stage08Config
        from sphereforge.stages.stage08_export.pipeline import run_stage08

        n = 12
        rng = np.random.default_rng(0)
        rotations = rng.normal(size=(n, 4)).astype(np.float32)
        rotations *= rng.uniform(0.6, 1.6, size=(n, 1)).astype(np.float32)
        gaussians = {
            "positions": rng.normal(size=(n, 3)).astype(np.float32),
            "opacities": np.full(n, 0.9, dtype=np.float32),
            "scales": np.full((n, 3), 0.05, dtype=np.float32),
            "rotations": rotations,
            "colors": np.full((n, 3), 0.5, dtype=np.float32),
        }
        source = tmp_path / "in.ply"
        from sphereforge.common.io import write_ply

        write_ply(source, **gaussians)

        out_dir = tmp_path / "out"
        out_dir.mkdir()
        run_stage08(Stage08Config(), source, out_dir)

        exported = read_ply(out_dir / "final.ply")
        norms = np.linalg.norm(exported["rotations"], axis=1)
        assert np.allclose(norms, 1.0, atol=1e-4)
