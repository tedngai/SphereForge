"""RPG360-only depth estimation pipeline.

Implements the full RPG360 depth pipeline: run a perspective depth model
(e.g. Metric3D v2) on each of the 6 cubemap faces, graph-optimize per-face
scales for cross-face consistency, align the face depths, and fuse them
back into a single equirectangular depth map.

This pipeline is an alternative to the PanDA monocular depth estimator and
provides metric-scale depth directly (no separate COLMAP alignment needed).
"""

from __future__ import annotations

import logging

import numpy as np

from sphereforge.models.metric3d import Metric3DV2
from sphereforge.stages.stage02_cubemap.rpg360_graph import (
    align_face_depths,
    fuse_to_erp,
    graph_optimize_scales,
)

logger = logging.getLogger("sphereforge.stage04.rpg360_pipeline")

# Canonical 6-face directions
_FACE_DIRECTIONS: list[str] = ["front", "right", "back", "left", "top", "bottom"]


def rpg360_depth_pipeline(
    images: list[np.ndarray],
    face_directions: list[str],
    erp_height: int,
    erp_width: int,
    model_name: str = "metric3d_v2",
) -> np.ndarray:
    """Run the full RPG360 depth estimation pipeline on cubemap faces.

    The pipeline:
    1. Runs Metric3D (or another perspective model) on each cubemap face
       to get per-face metric depth maps.
    2. Graph-optimizes per-face scale and shift parameters so that depth
       values agree in the overlap regions between adjacent faces
       (RPG360 algorithm).
    3. Applies the optimised scale and shift to each face depth map.
    4. Fuses the aligned face depth maps into a single equirectangular
       depth map.

    Args:
        images: List of 6 cubemap face images, each of shape (H_f, W_f, 3)
            with dtype uint8.
        face_directions: List of 6 direction strings, each one of
            ``"front"``, ``"back"``, ``"right"``, ``"left"``,
            ``"top"``, ``"bottom"``. Order must correspond to ``images``.
        erp_height: Height of the output equirectangular depth map.
        erp_width: Width of the output equirectangular depth map.
        model_name: Perspective depth model name. Currently only
            ``"metric3d_v2"`` is supported. Default is ``"metric3d_v2"``.

    Returns:
        Equirectangular metric depth map of shape ``(erp_height, erp_width)``,
        dtype float32.

    Raises:
        ValueError: If input lists have incorrect length, unknown directions,
            or invalid ERP dimensions.
        RuntimeError: If the perspective depth model fails to load or infer.
    """
    if len(images) != 6 or len(face_directions) != 6:
        raise ValueError(
            f"Expected 6 cubemap faces, got {len(images)} images and "
            f"{len(face_directions)} directions"
        )

    valid_directions = {"front", "back", "right", "left", "top", "bottom"}
    for d in face_directions:
        if d not in valid_directions:
            raise ValueError(
                f"Unknown face direction '{d}', must be one of {valid_directions}"
            )

    if erp_height <= 0 or erp_width <= 0:
        raise ValueError(
            f"erp_height and erp_width must be positive, "
            f"got {erp_height} x {erp_width}"
        )

    logger.info(
        "RPG360 depth pipeline: %d faces, ERP %dx%d, model=%s",
        len(images),
        erp_width,
        erp_height,
        model_name,
    )

    # Step 1: Run perspective depth model on each cubemap face
    if model_name == "metric3d_v2":
        depth_model = Metric3DV2(model_name="metric3d_vit_small")
    else:
        raise ValueError(
            f"Unsupported perspective depth model '{model_name}'. "
            f"Currently only 'metric3d_v2' is supported."
        )

    logger.info("Running %s on %d cubemap faces", model_name, len(images))
    face_depths = depth_model.estimate_depth_batch(images)
    logger.info(
        "Per-face depth estimation complete. Face shapes: %s",
        [d.shape for d in face_depths],
    )

    # Step 2: Graph-optimize per-face scales
    logger.info("Running RPG360 graph scale optimization")
    scales, shifts = graph_optimize_scales(face_depths, face_directions)
    logger.info("Graph optimization complete")

    # Step 3: Apply scale+shift alignment to each face
    aligned_face_depths = align_face_depths(face_depths, scales, shifts)
    logger.info("Applied scale+shift alignment to %d faces", len(aligned_face_depths))

    # Step 4: Fuse aligned faces back to ERP
    erp_depth = fuse_to_erp(aligned_face_depths, face_directions, erp_height, erp_width)

    logger.info(
        "RPG360 pipeline complete: ERP depth %s, range [%.2f, %.2f]",
        erp_depth.shape,
        float(np.min(erp_depth[erp_depth > 0])) if np.any(erp_depth > 0) else 0.0,
        float(np.max(erp_depth)),
    )

    return erp_depth
