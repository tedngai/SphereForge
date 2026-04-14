"""Stage 8: Post-Processing & Export.

Provides final pruning, compact box culling, and multi-format export
for 3D Gaussian Splatting scenes.
"""

from __future__ import annotations

from sphereforge.stages.stage08_export.final_pruning import final_rap_prune
from sphereforge.stages.stage08_export.compact_culling import compact_box_cull
from sphereforge.stages.stage08_export.sog_export import export_sog
from sphereforge.stages.stage08_export.spz_export import export_spz
from sphereforge.stages.stage08_export.html_viewer import generate_html_viewer
from sphereforge.stages.stage08_export.mesh_extraction import extract_navigation_mesh
from sphereforge.stages.stage08_export.pipeline import run_stage08

__all__ = [
    "final_rap_prune",
    "compact_box_cull",
    "export_sog",
    "export_spz",
    "generate_html_viewer",
    "extract_navigation_mesh",
    "run_stage08",
]
