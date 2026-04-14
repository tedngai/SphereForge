"""Stage 5: Initial Gaussian Seeding."""

from __future__ import annotations

from .pipeline import run_stage05
from .projection import project_to_3d
from .fusion import fuse_multiview
from .deduplication import deduplicate_gaussians
from .edge_clipping import clip_grazing_angles
from .outlier_pruning import prune_outliers
from .sparse_pruning import prune_sparse_regions
from .sky_removal import remove_sky
from .confidence_filter import compute_depth_confidence
from .stride_assignment import assign_stride
from .attribute_assignment import assign_initial_attributes

__all__ = [
    "run_stage05",
    "project_to_3d",
    "fuse_multiview",
    "deduplicate_gaussians",
    "clip_grazing_angles",
    "prune_outliers",
    "prune_sparse_regions",
    "remove_sky",
    "compute_depth_confidence",
    "assign_stride",
    "assign_initial_attributes",
]
