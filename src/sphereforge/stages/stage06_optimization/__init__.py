"""Stage 6: Multi-View Gaussian Optimization.

This stage implements the training and optimisation of 3-D Gaussian Splat
scenes from multi-view cubemap crops.  It incorporates techniques from
three papers:

- **ErpGS** (arXiv:2505.19883) — distortion-aware loss, scale-flattening
  regularisation, and tangent-plane neighbour selection for equirectangular
  projection training.
- **360-GeoGS** (arXiv:2601.02102) — ray-ellipsoid intersection depth and
  D-Normal regularisation loss for geometrically accurate 360° scenes.
- **ImprovedGS+** — edge-aware densification, long-axis split, and
  recovery-aware pruning (implemented in separate modules).
"""

from __future__ import annotations

# T6.5 — 360-GeoGS D-Normal loss
from sphereforge.stages.stage06_optimization.d_normal_loss import (
    compute_normals_from_depth,
    d_normal_loss,
)

# T6.6 — ImprovedGS+ Edge-Aware Score & densification
from sphereforge.stages.stage06_optimization.densification import (
    compute_eas,
    compute_grad_accum,
    should_densify,
)

# T6.1 + T6.2 — ErpGS loss functions
from sphereforge.stages.stage06_optimization.erp_loss import (
    compute_latitudes_from_crops,
    erp_weighted_loss,
    scale_flattening_loss,
)

# T6.4 — 360-GeoGS intersection-depth computation
from sphereforge.stages.stage06_optimization.intersection_depth import (
    compute_intersection_depth,
    quaternion_to_rotation_matrix,
)

# T6.8 — ImprovedGS+ Recovery-Aware Pruning
from sphereforge.stages.stage06_optimization.pruning import (
    PruningBuffer,
    rap_prune,
)

# T6.7 — ImprovedGS+ Long-Axis Split & cloning
from sphereforge.stages.stage06_optimization.split_clone import (
    clone_under_reconstructed,
    long_axis_split,
)

# T6.3 — ErpGS tangent-plane neighbour selection
from sphereforge.stages.stage06_optimization.tangent_neighbors import (
    project_to_tangent_plane,
    tangent_plane_neighbors,
)

__all__ = [
    # T6.8
    "PruningBuffer",
    "clone_under_reconstructed",
    # T6.6
    "compute_eas",
    "compute_grad_accum",
    # T6.4
    "compute_intersection_depth",
    "compute_latitudes_from_crops",
    "compute_normals_from_depth",
    # T6.5
    "d_normal_loss",
    # T6.1
    "erp_weighted_loss",
    # T6.7
    "long_axis_split",
    "project_to_tangent_plane",
    "quaternion_to_rotation_matrix",
    "rap_prune",
    # T6.2
    "scale_flattening_loss",
    "should_densify",
    # T6.3
    "tangent_plane_neighbors",
]
