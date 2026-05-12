"""Stage 5: Initial Gaussian Seeding."""

from __future__ import annotations

from .attribute_assignment import assign_initial_attributes
from .confidence_filter import compute_depth_confidence
from .deduplication import deduplicate_gaussians
from .edge_clipping import clip_grazing_angles
from .fusion import fuse_multiview
from .outlier_pruning import prune_outliers
from .pipeline import run_stage05
from .projection import project_to_3d
from .sky_removal import remove_sky
from .sparse_pruning import prune_sparse_regions
from .stride_assignment import assign_stride

__all__ = [
    "assign_initial_attributes",
    "assign_stride",
    "clip_grazing_angles",
    "compute_depth_confidence",
    "deduplicate_gaussians",
    "fuse_multiview",
    "project_to_3d",
    "prune_outliers",
    "prune_sparse_regions",
    "remove_sky",
    "run_stage05",
]
