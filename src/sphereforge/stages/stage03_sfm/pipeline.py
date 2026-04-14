"""Stage 3.6: Multi-View SfM pipeline orchestration.

Coordinates the full Stage 3 workflow: feature extraction, feature
matching, bundle adjustment (mapper), sparse model reading, and
optional dense reconstruction.
"""

from __future__ import annotations

import logging
from pathlib import Path

from sphereforge.config import Stage03Config
from sphereforge.logging_utils import log_task_completion

from sphereforge.stages.stage03_sfm.bundle_adjustment import run_bundle_adjustment
from sphereforge.stages.stage03_sfm.dense_reconstruction import run_dense_reconstruction
from sphereforge.stages.stage03_sfm.feature_extraction import run_feature_extraction
from sphereforge.stages.stage03_sfm.feature_matching import run_feature_matching
from sphereforge.stages.stage03_sfm.model_reader import read_sparse_model

logger = logging.getLogger("sphereforge.stage03.pipeline")


def run_stage03(
    config: Stage03Config,
    colmap_dataset_dir: Path,
    output_dir: Path,
) -> dict:
    """Run the full Stage 3 (Multi-View SfM) pipeline.

    Orchestrates the following steps:

    1. Set up database path and directories.
    2. Run feature extraction.
    3. Run feature matching.
    4. Run bundle adjustment (mapper + bundle_adjuster).
    5. Read sparse model.
    6. Optionally run dense reconstruction.
    7. Return dict with sparse model data.

    Args:
        config: Stage 3 configuration (``Stage03Config``).
        colmap_dataset_dir: Root directory of the COLMAP dataset,
            expected to contain an ``images/`` subdirectory and
            optionally a ``masks/`` subdirectory.
        output_dir: Directory where Stage 3 outputs are written.

    Returns:
        Dict with keys ``"cameras"``, ``"images"``, ``"points3D"``
        containing the parsed sparse model data.

    Raises:
        RuntimeError: If any COLMAP subprocess fails.
        FileNotFoundError: If required input directories or files
            are missing.
    """
    colmap_dataset_dir = Path(colmap_dataset_dir)
    output_dir = Path(output_dir)

    # Step 1: Set up directories
    database_path = output_dir / "database.db"
    sparse_dir = output_dir / "sparse"
    dense_dir = output_dir / "dense"
    image_dir = colmap_dataset_dir / "images"
    mask_dir = colmap_dataset_dir / "masks"

    # Ensure output directories exist
    sparse_dir.mkdir(parents=True, exist_ok=True)
    if config.dense_reconstruction:
        dense_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Starting Stage 3 SfM pipeline: dataset=%s, output=%s",
        colmap_dataset_dir,
        output_dir,
    )
    logger.info(
        "Config: feature_type=%s, matcher_type=%s, "
        "refine_intrinsics=%s, dense_reconstruction=%s",
        config.feature_type,
        config.matcher_type,
        config.refine_intrinsics,
        config.dense_reconstruction,
    )

    # Step 2: Feature extraction
    logger.info("Step 2: Feature extraction")
    mask_dir_path = mask_dir if mask_dir.is_dir() else None
    run_feature_extraction(
        database_path=database_path,
        image_dir=image_dir,
        camera_model="PINHOLE",
        feature_type=config.feature_type,
        mask_dir=mask_dir_path,
    )

    # Step 3: Feature matching
    logger.info("Step 3: Feature matching")
    # Resolve vocabulary tree path (commonly placed alongside the dataset)
    vocab_tree_path: Path | None = None
    vocab_tree_candidate = colmap_dataset_dir / "vocab_tree.bin"
    if vocab_tree_candidate.exists():
        vocab_tree_path = vocab_tree_candidate

    run_feature_matching(
        database_path=database_path,
        matcher_type=config.matcher_type,
        vocab_tree_path=vocab_tree_path,
    )

    # Step 4: Bundle adjustment (mapper + bundle_adjuster)
    logger.info("Step 4: Bundle adjustment")
    run_bundle_adjustment(
        database_path=database_path,
        sparse_dir=sparse_dir,
        refine_intrinsics=config.refine_intrinsics,
        image_dir=image_dir,
    )

    # Step 5: Read sparse model
    logger.info("Step 5: Reading sparse model")
    sparse_model = read_sparse_model(sparse_dir)

    # Step 6: Optionally run dense reconstruction
    if config.dense_reconstruction:
        logger.info("Step 6: Dense reconstruction")
        try:
            run_dense_reconstruction(
                sparse_dir=sparse_dir,
                image_dir=image_dir,
                dense_dir=dense_dir,
            )
        except RuntimeError as exc:
            logger.warning(
                "Dense reconstruction failed (non-fatal): %s", exc
            )

    # Step 7: Log completion and return
    logger.info("Stage 3 SfM pipeline completed successfully.")
    try:
        log_task_completion(
            task_id="T3.6",
            notes="Stage 3 SfM pipeline completed",
            files_created=[
                str(database_path),
                str(sparse_dir),
            ],
        )
    except Exception:
        # Don't fail the pipeline if progress logging has an issue
        logger.debug("Progress logging skipped", exc_info=True)

    return {
        "cameras": sparse_model["cameras"],
        "images": sparse_model["images"],
        "points3D": sparse_model["points3D"],
    }
