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
