"""Stage 5 pipeline: Initial Gaussian Seeding.

Orchestrates projection, fusion, deduplication, filtering, attribute
assignment, and PLY writing to produce the initial Gaussian point cloud.
"""

from __future__ import annotations

import logging
from concurrent.futures import ProcessPoolExecutor
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


def _process_single_frame_stage05(
    frame_path: Path,
    depth_path: Path,
    config: Stage05Config,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Process a single frame: confidence → stride → project to 3D.

    Returns:
        (positions, colors, per_point_depth)
    """
    image = read_image(frame_path)
    depth_map = read_depth(depth_path)

    if config.cross_validate_depth:
        secondary_depth_path = depth_path.parent / (
            depth_path.stem + "_rpg360" + depth_path.suffix
        )
        if secondary_depth_path.exists():
            depth_secondary = read_depth(secondary_depth_path)
            confidence_map = compute_depth_confidence(
                depth_map, depth_secondary, ncc_threshold=config.ncc_confidence_threshold
            )
        else:
            confidence_map = _compute_depth_confidence_heuristic(depth_map)
    else:
        confidence_map = np.ones(depth_map.shape, dtype=np.float32)

    stride_map = assign_stride(
        confidence_map,
        stride_high=config.stride,
        stride_low=config.stride_low_confidence,
        threshold=config.ncc_confidence_threshold,
    )

    positions, colors = project_to_3d(image, depth_map, stride_map=stride_map)

    h, w = depth_map.shape
    row_idx = np.arange(h)[:, None]
    col_idx = np.arange(w)[None, :]
    sample_mask = (row_idx % stride_map == 0) & (col_idx % stride_map == 0)
    v_idx, u_idx = np.where(sample_mask)
    per_point_depth = depth_map[v_idx, u_idx].astype(np.float32)
    valid_flat = per_point_depth > 0
    per_point_depth = per_point_depth[valid_flat]

    return positions, colors, per_point_depth


def run_stage05(
    config: Stage05Config,
    frame_paths: list[Path],
    depth_paths: list[Path],
    sparse_model: dict,
    scene_params: dict,
    output_dir: Path,
    num_workers: int = 1,
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
    logger.info(
        "Stage 5: Initial Gaussian Seeding — %d frames, workers=%d",
        n_frames,
        num_workers,
    )

    # ------------------------------------------------------------------
    # Step 1: Per-frame projection
    # ------------------------------------------------------------------
    all_positions: list[np.ndarray] = []
    all_colors: list[np.ndarray] = []
    all_depths: list[np.ndarray] = []  # per-point depth values

    if num_workers > 1:
        logger.info("Using %d parallel workers for projection", num_workers)
        args = [
            (fp, dp, config)
            for fp, dp in zip(frame_paths, depth_paths, strict=True)
        ]
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            results = list(executor.map(_process_single_frame_stage05_worker, args))
    else:
        results = []
        for fp, dp in zip(frame_paths, depth_paths, strict=True):
            results.append(_process_single_frame_stage05(fp, dp, config))

    for positions, colors, per_point_depth in results:
        all_positions.append(positions)
        all_colors.append(colors)
        all_depths.append(per_point_depth)

    # ------------------------------------------------------------------
    # Step 2: Multi-view fusion
    # ------------------------------------------------------------------
    fused_positions, fused_colors, fused_confidence = fuse_multiview(
        all_positions, all_colors, sparse_model
    )

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


def _compute_depth_confidence_heuristic(depth_map: np.ndarray) -> np.ndarray:
    """Compute a per-pixel confidence map from a single depth map.

    Uses the inverse of local gradient magnitude as a proxy for
    confidence: flat regions receive high confidence, edges and
    discontinuities receive low confidence.

    Args:
        depth_map: Depth map of shape (H, W), dtype float32.

    Returns:
        Confidence map of shape (H, W), dtype float32, values in [0, 1].
    """
    from scipy.ndimage import sobel

    # Compute Sobel gradients
    grad_x = sobel(depth_map, axis=1)
    grad_y = sobel(depth_map, axis=0)
    grad_mag = np.sqrt(grad_x ** 2 + grad_y ** 2)

    # Normalise by the 95th percentile of non-zero gradients
    nonzero = grad_mag[grad_mag > 0]
    max_grad = float(np.percentile(nonzero, 95)) if nonzero.size > 0 else 1.0
    max_grad = max(max_grad, 1e-8)

    confidence = 1.0 - np.clip(grad_mag / max_grad, 0.0, 1.0)
    return confidence.astype(np.float32)


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

        r_mat = quat_to_rotation_matrix(qw, qx, qy, qz)
        cam_center = -r_mat.T @ t
        origins.append(cam_center.astype(np.float32))

    return np.stack(origins, axis=0) if origins else np.empty((0, 3), dtype=np.float32)


def _process_single_frame_stage05_worker(
    args: tuple[Path, Path, Stage05Config],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Picklable wrapper for ``_process_single_frame_stage05``."""
    frame_path, depth_path, config = args
    return _process_single_frame_stage05(frame_path, depth_path, config)
