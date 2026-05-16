"""Stage 7: Occlusion Recovery & Refinement.

This stage fills holes in the Gaussian splat by:
1. Generating novel camera viewpoints around the scene.
2. Detecting holes (insufficient alpha coverage) from those views.
3. Classifying gaps by type (behind foreground, at boundary, missing geometry).
4. ShareGS pre-pass: homogenize Gaussians and reuse patches from other views.
5. GS-Diff pass: EscherNet diffusion inpainting with LPIPS filtering.
6. Distilling inpainted pseudo-ground-truth back into the splat.
7. Iterating until hole coverage drops below the threshold.

Public API:
    - ``run_stage07`` — Full pipeline orchestrator.
    - ``generate_novel_cameras`` — Camera placement.
    - ``detect_holes`` / ``compute_hole_coverage`` — Hole detection.
    - ``classify_gaps`` — Gap type classification.
    - ``homogenize_gaussians`` — ShareGS Gaussian cloning.
    - ``reuse_patches`` — ShareGS cross-view patch reuse.
    - ``filter_hallucinations`` — LPIPS-based hallucination filtering.
    - ``softmax_depth_loss`` — Depth-prior-guided loss.
    - ``distill_inpaint`` — Pseudo-view distillation.
    - ``fill_holes_iterative`` — Iterative fill loop.
    - ``omniroam_fill`` — OmniRoam stub (license-gated).

Import conventions:
    Heavy optional dependencies (diffusers, lpips, gsplat, torch for SD)
    are imported inside function bodies so that Stage 7 modules can be
    imported without installing every backend.  This pattern is used
    consistently across all submodules.
"""

from __future__ import annotations

from sphereforge.stages.stage07_occlusion.blend_fill import blend_fill
from sphereforge.stages.stage07_occlusion.distillation import distill_inpaint
from sphereforge.stages.stage07_occlusion.eschernet import EscherNetWrapper
from sphereforge.stages.stage07_occlusion.gap_classification import classify_gaps
from sphereforge.stages.stage07_occlusion.hole_detection import (
    compute_hole_coverage,
    detect_holes,
)
from sphereforge.stages.stage07_occlusion.iterative_fill import fill_holes_iterative
from sphereforge.stages.stage07_occlusion.lpips_filter import filter_hallucinations
from sphereforge.stages.stage07_occlusion.novel_cameras import generate_novel_cameras
from sphereforge.stages.stage07_occlusion.omniroam import omniroam_fill
from sphereforge.stages.stage07_occlusion.pipeline import run_stage07
from sphereforge.stages.stage07_occlusion.sharegs_homogenize import homogenize_gaussians
from sphereforge.stages.stage07_occlusion.sharegs_reuse import reuse_patches
from sphereforge.stages.stage07_occlusion.softmax_depth import softmax_depth_loss

__all__ = [
    "EscherNetWrapper",
    "blend_fill",
    "classify_gaps",
    "compute_hole_coverage",
    "detect_holes",
    "distill_inpaint",
    "fill_holes_iterative",
    "filter_hallucinations",
    "generate_novel_cameras",
    "homogenize_gaussians",
    "omniroam_fill",
    "reuse_patches",
    "run_stage07",
    "softmax_depth_loss",
]
