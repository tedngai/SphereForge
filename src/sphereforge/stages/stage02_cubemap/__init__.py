"""Stage 2: Equirect→Cubemap + COLMAP Prep.

Extracts perspective cubemap crops from equirectangular frames with yaw
diversification, computes PINHOLE camera intrinsics/extrinsics, generates
dynamic-object and overexposure masks, and writes a COLMAP-format dataset
ready for multi-view SfM.
"""

from sphereforge.stages.stage02_cubemap.cubemap import CUBEMAP_FACES, extract_cubemap
from sphereforge.stages.stage02_cubemap.extrinsics import (
    FACE_DIRECTIONS,
    compute_extrinsics,
)
from sphereforge.stages.stage02_cubemap.intrinsics import compute_intrinsics
from sphereforge.stages.stage02_cubemap.masking import (
    combine_masks,
    generate_overexposure_masks,
    generate_yolo_masks,
)
from sphereforge.stages.stage02_cubemap.pipeline import run_stage02
from sphereforge.stages.stage02_cubemap.rpg360_graph import (
    align_face_depths,
    fuse_to_erp,
    graph_optimize_scales,
)
from sphereforge.stages.stage02_cubemap.yaw_diversify import (
    apply_yaw_offset,
    extract_diversified_cubemaps,
)

__all__ = [
    "CUBEMAP_FACES",
    "FACE_DIRECTIONS",
    "align_face_depths",
    "apply_yaw_offset",
    "combine_masks",
    "compute_extrinsics",
    "compute_intrinsics",
    "extract_cubemap",
    "extract_diversified_cubemaps",
    "fuse_to_erp",
    "generate_overexposure_masks",
    "generate_yolo_masks",
    "graph_optimize_scales",
    "run_stage02",
]
