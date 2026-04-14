"""Stage 4: Dense Depth Estimation.

Provides depth estimation, COLMAP alignment, scene analysis, and the
RPG360 cubemap-face depth pipeline.
"""

from __future__ import annotations

from sphereforge.stages.stage04_depth.depth_alignment import align_depth_to_colmap
from sphereforge.stages.stage04_depth.model_factory import get_depth_estimator
from sphereforge.stages.stage04_depth.panda_model import PanDAModel
from sphereforge.stages.stage04_depth.pipeline import run_stage04
from sphereforge.stages.stage04_depth.rpg360_pipeline import rpg360_depth_pipeline
from sphereforge.stages.stage04_depth.scene_analysis import analyze_depth_scene

__all__ = [
    "PanDAModel",
    "align_depth_to_colmap",
    "analyze_depth_scene",
    "get_depth_estimator",
    "rpg360_depth_pipeline",
    "run_stage04",
]
