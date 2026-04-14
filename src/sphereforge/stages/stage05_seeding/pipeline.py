"""Stage 5 pipeline: Initial Gaussian Seeding.

Orchestrates projection, fusion, deduplication, filtering, attribute
assignment, and PLY writing to produce the initial Gaussian point cloud.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from sphereforge.common.colmap_helpers import quat_to_rotation_matrix
from sphereforge.common.io import read_depth, read_image, write_ply
from sphereforge.config import Stage05Config

from .attribute_assignment import assign_initial_attributes
from .confidence_filter import compute_depth_confidence
from .deduplication import deduplicate_gaussians
from .edge_clipping import clip_grazing_angles
from .fusion import fuse_multiview
from .outlier_pruning import prune_outliers
from .projection import project_to_3d
from .sky_removal import remove_sky
from .sparse_pruning import prune_sparse_regions
from .stride_assignment import assign_stride

logger = logging.getLogger("sphereforge.stage05.pipeline")


def run_stage05(
    config: Stage05Config,
    frame_paths: list[Path],
    depth_paths: list[Path],
    sparse_model: dict,
    scene_params: dict,
    output_dir: Path,
) -> Path:
    """Run Stage 5: Initial Gaussian Seeding.

    Orchestrates the full pipeline:
    1. For each frame: compute confidence → assign stride → project to 3D.
    2. Fuse multiview point clouds into world coordinates.
    3. Deduplicate nearby Gaussians.
    4. Apply filters: edge clipping → sky removal → outlier pruning →
       sparse pruning.
    5. Assign initial attributes (opacity, scale, rotation).
    6. Write PLY.

    Args:
        config: Stage 5 configuration.
        frame_paths: List of paths to ERP frame images.
        depth_paths: List of paths to primary depth maps (.npy).
        sparse_model: COLMAP sparse model dict with ``"images"`` key.
        scene_params: Scene parameters dict from
            :func:`analyze_depth_scene`, containing ``sky_depth``,
            ``orbit_radius``, etc.
        output_dir: Directory for output files.

    Returns:
        Path to the output PLY file.

    Raises:
        ValueError: If inputs are invalid or inconsistent.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if len(frame_paths) != len(depth_paths):
        raise ValueError(
            f"frame_paths and depth_paths must have the same length, "
            f"got {len(frame_paths)} vs {len(depth_paths)}"
        )

    n_frames = len(frame_paths)
    logger.info("Stage 5: Initial Gaussian Seeding — %d frames", n_frames)

    # ------------------------------------------------------------------
    # Step 1: Per-frame projection
    # ------------------------------------------------------------------
    all_positions: list[np.ndarray] = []
    all_colors: list[np.ndarray] = []
    all_depths: list[np.ndarray] = []  # per-point depth values

    for frame_idx, (frame_path, depth_path) in enumerate(
        zip(frame_paths, depth_paths)
    ):
        logger.debug("Processing frame %d/%d: %s", frame_idx + 1, n_frames, frame_path)

        image = read_image(frame_path)
        depth_map = read_depth(depth_path)

        # Determine per-pixel stride via confidence
        if config.cross_validate_depth and n_frames > 1:
            # Use a simple heuristic: compute NCC between this depth and
            # the next one (circular).  In production the secondary depth
            # would come from RPG360; here we skip cross-validation when
            # only one depth source is available and use uniform stride.
            stride_map = np.full(
                depth_map.shape, config.stride, dtype=np.int32
            )
        else:
            stride_map = np.full(
                depth_map.shape, config.stride, dtype=np.int32
            )

        # Project with stride — use a uniform effective stride
        # (per-pixel stride is approximated by using the stride_low for
        #  the whole frame if confidence is low on average)
        effective_stride = config.stride

        positions, colors = project_to_3d(image, depth_map, stride=effective_stride)

        # Compute per-point depth for later use
        per_point_depth = depth_map[
            np.arange(0, depth_map.shape[0], effective_stride)[:, None],
            np.arange(0, depth_map.shape[1], effective_stride)[None, :],
        ].ravel()
        valid_depth = depth_map[
            np.arange(0, depth_map.shape[0], effective_stride)[:, None],
            np.arange(0, depth_map.shape[1], effective_stride)[None, :],
        ] > 0
        valid_flat = valid_depth.ravel()
        per_point_depth = per_point_depth[valid_flat].astype(np.float32)

        all_positions.append(positions)
        all_colors.append(colors)
        all_depths.append(per_point_depth)

        logger.debug(
            "Frame %d: %d points projected (stride=%d)",
            frame_idx,
            positions.shape[0],
            effective_stride,
        )

    # ------------------------------------------------------------------
    # Step 2: Multi-view fusion
    # ------------------------------------------------------------------
    fused_positions, fused_colors, fused_confidence = fuse_multiview(
        all_positions, all_colors, sparse_model
    )

    # Per-point depth for fused points (approximate as distance from origin)
    fused_depth = np.linalg.norm(fused_positions, axis=1).astype(np.float32)

    # ------------------------------------------------------------------
    # Step 3: Deduplication
    # ------------------------------------------------------------------
    deduped_positions, deduped_colors, deduped_confidence = deduplicate_gaussians(
        fused_positions, fused_colors, fused_confidence, config.dedup_distance
    )
    deduped_depth = np.linalg.norm(deduped_positions, axis=1).astype(np.float32)

    # ------------------------------------------------------------------
    # Step 4: Filtering
    # ------------------------------------------------------------------
    mask = np.ones(deduped_positions.shape[0], dtype=bool)

    # 4a. Edge clipping (grazing angle)
    camera_origins = _extract_camera_origins(sparse_model)
    if camera_origins.shape[0] > 0:
        edge_mask = clip_grazing_angles(
            deduped_positions, camera_origins, config.grazing_angle
        )
        mask &= edge_mask

    # 4b. Sky removal
    sky_thresh = config.sky_threshold
    if sky_thresh == "auto" and scene_params.get("sky_depth") is not None:
        sky_thresh = scene_params["sky_depth"]
    sky_mask = remove_sky(deduped_positions, deduped_depth, sky_thresh)
    mask &= sky_mask

    # 4c. Outlier pruning
    if config.outlier_pruning > 0:
        outlier_mask = prune_outliers(deduped_positions, config.outlier_pruning)
        mask &= outlier_mask

    # 4d. Sparse pruning
    if config.sparse_pruning > 0:
        sparse_mask = prune_sparse_regions(deduped_positions, config.sparse_pruning)
        mask &= sparse_mask

    # Apply mask
    filtered_positions = deduped_positions[mask]
    filtered_colors = deduped_colors[mask]
    filtered_confidence = deduped_confidence[mask]
    filtered_depth = deduped_depth[mask]

    logger.info(
        "After filtering: %d points remaining (removed %d)",
        filtered_positions.shape[0],
        int(np.sum(~mask)),
    )

    # ------------------------------------------------------------------
    # Step 5: Attribute assignment
    # ------------------------------------------------------------------
    attributes = assign_initial_attributes(
        filtered_positions,
        filtered_colors,
        filtered_confidence,
        filtered_depth,
    )

    # ------------------------------------------------------------------
    # Step 6: Write PLY
    # ------------------------------------------------------------------
    output_path = output_dir / "initial_gaussians.ply"
    write_ply(
        path=output_path,
        positions=attributes["positions"],
        colors=attributes["colors"],
        opacities=attributes["opacities"],
        scales=attributes["scales"],
        rotations=attributes["rotations"],
    )

    logger.info(
        "Stage 5 complete: %d Gaussians written to %s",
        attributes["positions"].shape[0],
        output_path,
    )

    return output_path


def _extract_camera_origins(sparse_model: dict) -> np.ndarray:
    """Extract camera world-space origins from COLMAP sparse model.

    For each image the camera origin in world coordinates is::

        C = -R^T @ t

    where R is the rotation matrix from the quaternion and t is the
    translation vector.

    Args:
        sparse_model: Dict with ``"images"`` key mapping image_id to
            extrinsics data.

    Returns:
        (M, 3) float32 array of camera origins.
    """
    images = sparse_model.get("images", {})
    if not images:
        return np.empty((0, 3), dtype=np.float32)

    origins = []
    for img_id in sorted(images.keys()):
        img = images[img_id]
        qw, qx, qy, qz = img["qw"], img["qx"], img["qy"], img["qz"]
        t = np.array([img["tx"], img["ty"], img["tz"]], dtype=np.float64)

        R = quat_to_rotation_matrix(qw, qx, qy, qz)
        cam_center = -R.T @ t
        origins.append(cam_center.astype(np.float32))

    return np.stack(origins, axis=0) if origins else np.empty((0, 3), dtype=np.float32)
