"""SphereForge CLI entry point."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

import click
import numpy as np
import yaml

from sphereforge.config import SphereForgeConfig

logger = logging.getLogger("sphereforge.cli")

# Stage pipeline imports (imported inside functions to keep CLI startup fast)

def _import_stage_runner(stage_num: int) -> Any:
    """Dynamically import the run_stageXX function."""
    if stage_num == 1:
        from sphereforge.stages.stage01_frames.pipeline import run_stage01
        return run_stage01
    elif stage_num == 2:
        from sphereforge.stages.stage02_cubemap.pipeline import run_stage02
        return run_stage02
    elif stage_num == 3:
        from sphereforge.stages.stage03_sfm.pipeline import run_stage03
        return run_stage03
    elif stage_num == 4:
        from sphereforge.stages.stage04_depth.pipeline import run_stage04
        return run_stage04
    elif stage_num == 5:
        from sphereforge.stages.stage05_seeding.pipeline import run_stage05
        return run_stage05
    elif stage_num == 6:
        from sphereforge.stages.stage06_optimization.pipeline import run_stage06
        return run_stage06
    elif stage_num == 7:
        from sphereforge.stages.stage07_occlusion.pipeline import run_stage07
        return run_stage07
    elif stage_num == 8:
        from sphereforge.stages.stage08_export.pipeline import run_stage08
        return run_stage08
    else:
        raise ValueError(f"Unknown stage number: {stage_num}")


def _load_config(config_path: str | None) -> SphereForgeConfig:
    """Load SphereForgeConfig from an optional YAML file."""
    if config_path is None:
        return SphereForgeConfig()

    path = Path(config_path)
    if not path.exists():
        raise click.BadParameter(f"Config file not found: {config_path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return SphereForgeConfig(**data)


def _setup_logging(log_level: str) -> None:
    """Configure Python logging for the pipeline."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group()
@click.version_option(package_name="sphereforge")
def main() -> None:
    """SphereForge: Transform 360° footage into 3D Gaussian Splat scenes."""


# ---------------------------------------------------------------------------
# Process command
# ---------------------------------------------------------------------------

@main.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--config", "-c", type=click.Path(exists=True), help="YAML config file")
@click.option("--stage", "-s", type=click.IntRange(1, 8), help="Run only this stage (1-8)")
@click.option("--output", "-o", type=click.Path(), help="Output data directory")
@click.option("--resume", is_flag=True, help="Skip stages that already have outputs")
@click.option("--log-level", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]), default="INFO")
def process(
    input_path: str,
    config: str | None,
    stage: int | None,
    output: str | None,
    resume: bool,
    log_level: str,
) -> None:
    """Process 360° video or images into a Gaussian Splat scene.

    INPUT_PATH can be a video file (.mp4, .mov) or a directory of
    equirectangular images.
    """
    cfg = _load_config(config)
    cfg.log_level = log_level
    _setup_logging(log_level)

    data_dir = Path(output) if output else cfg.data_dir
    input_path_obj = Path(input_path)

    logger = logging.getLogger("sphereforge.cli")
    logger.info("SphereForge processing: %s", input_path_obj)
    logger.info("Data directory: %s", data_dir.resolve())

    # Determine stage range
    stages = [stage] if stage else list(range(1, 9))

    # Keep track of intermediate results
    frame_paths: list[Path] | None = None
    sparse_model: dict[str, Any] | None = None
    depth_result: dict[str, Any] | None = None
    stage5_ply: Path | None = None
    stage6_ply: Path | None = None
    stage7_ply: Path | None = None

    for s in stages:
        logger.info("=" * 50)
        logger.info("Stage %d/%d", s, 8)
        logger.info("=" * 50)

        runner = _import_stage_runner(s)

        if s == 1:
            frames_dir = data_dir / "frames"
            if resume and _has_frames(frames_dir):
                logger.info("Resuming: Stage 1 output found, skipping")
                frame_paths = sorted(frames_dir.glob("*.png"))
                if not frame_paths:
                    frame_paths = sorted(frames_dir.glob("*.jpg"))
            else:
                frame_paths = runner(cfg.stage01, input_path_obj, frames_dir)
            if not frame_paths:
                raise click.ClickException("Stage 1 produced no frames. Aborting.")

        elif s == 2:
            # Starting mid-pipeline (`--stage 2`) means Stage 1 is not in this
            # run's loop, so pick up its output from disk when resuming.
            if frame_paths is None and resume:
                frame_paths = _load_existing_frames(data_dir / "frames")
                if frame_paths:
                    logger.info(
                        "Resuming: using %d Stage 1 frames from %s",
                        len(frame_paths),
                        data_dir / "frames",
                    )
            if frame_paths is None:
                raise click.ClickException("Stage 2 requires Stage 1 output. Run Stage 1 first.")
            cubemap_dir = data_dir / "cubemaps"
            if resume and (cubemap_dir / "cameras.txt").exists():
                logger.info("Resuming: Stage 2 output found, skipping")
            else:
                runner(cfg.stage02, frame_paths, cubemap_dir, num_workers=cfg.num_workers)

        elif s == 3:
            cubemap_dir = data_dir / "cubemaps"
            colmap_output = data_dir / "colmap"
            if resume and (colmap_output / "sparse" / "cameras.txt").exists():
                logger.info("Resuming: Stage 3 output found, skipping")
                from sphereforge.stages.stage03_sfm.model_reader import read_sparse_model
                sparse_model = read_sparse_model(colmap_output / "sparse")
            else:
                sparse_model = runner(cfg.stage03, cubemap_dir, colmap_output)

        elif s == 4:
            if frame_paths is None and resume:
                frame_paths = _load_existing_frames(data_dir / "frames")
            if frame_paths is None:
                raise click.ClickException("Stage 4 requires Stage 1 output. Run Stage 1 first.")
            if sparse_model is None:
                colmap_output = data_dir / "colmap"
                from sphereforge.stages.stage03_sfm.model_reader import read_sparse_model
                sparse_model = read_sparse_model(colmap_output / "sparse")
            depth_dir = data_dir / "depth"
            cubemap_dir = data_dir / "cubemaps"
            if resume and _has_depth_maps(depth_dir):
                logger.info("Resuming: Stage 4 output found, skipping")
                depth_paths = sorted(depth_dir.glob("*_depth.npy"))
                depth_result = {"depth_paths": depth_paths, "scene_params": {}}
            else:
                depth_result = runner(
                    cfg.stage04,
                    frame_paths,
                    cubemap_dir,
                    sparse_model,
                    depth_dir,
                    num_workers=cfg.num_workers,
                )

            # Monocular SfM recovers geometry only up to a global scale, while
            # Stage 4 depth is metric. Resolve the ambiguity once here so every
            # later stage works in metres.
            sparse_model = _rescale_sparse_model_to_metric(
                sparse_model,
                depth_result.get("depth_paths", []),
                frame_paths,
                cubemap_dir,
            )

        elif s == 5:
            if frame_paths is None and resume:
                frame_paths = _load_existing_frames(data_dir / "frames")
            if frame_paths is None:
                raise click.ClickException("Stage 5 requires Stage 1 output. Run Stage 1 first.")
            if depth_result is None:
                depth_dir = data_dir / "depth"
                depth_paths = sorted(depth_dir.glob("*_depth.npy"))
                depth_result = {"depth_paths": depth_paths, "scene_params": {}}
            if sparse_model is None:
                colmap_output = data_dir / "colmap"
                from sphereforge.stages.stage03_sfm.model_reader import read_sparse_model
                sparse_model = read_sparse_model(colmap_output / "sparse")
            gaussians_dir = data_dir / "gaussians"
            if resume and (gaussians_dir / "initial_gaussians.ply").exists():
                logger.info("Resuming: Stage 5 output found, skipping")
                stage5_ply = gaussians_dir / "initial_gaussians.ply"
            else:
                stage5_ply = runner(
                    cfg.stage05,
                    frame_paths,
                    depth_result["depth_paths"],
                    sparse_model,
                    depth_result.get("scene_params", {}),
                    gaussians_dir,
                    num_workers=cfg.num_workers,
                    cubemap_dir=data_dir / "cubemaps",
                )

        elif s == 6:
            if stage5_ply is None:
                stage5_ply = data_dir / "gaussians" / "initial_gaussians.ply"
                if not stage5_ply.exists():
                    raise click.ClickException(
                        "Stage 6 requires Stage 5 output. Run Stage 5 first."
                    )
            optimized_dir = data_dir / "optimized"
            colmap_dir = data_dir / "colmap" / "sparse"
            depth_dir = data_dir / "depth"
            if resume and (optimized_dir / "optimized.ply").exists():
                logger.info("Resuming: Stage 6 output found, skipping")
                stage6_ply = optimized_dir / "optimized.ply"
            else:
                stage6_ply = runner(
                    cfg.stage06,
                    stage5_ply,
                    colmap_dir,
                    depth_dir,
                    optimized_dir,
                )

        elif s == 7:
            if stage6_ply is None:
                stage6_ply = data_dir / "optimized" / "optimized.ply"
                if not stage6_ply.exists():
                    raise click.ClickException(
                        "Stage 7 requires Stage 6 output. Run Stage 6 first."
                    )
            refined_dir = data_dir / "refined"
            colmap_dir = data_dir / "colmap" / "sparse"
            depth_dir = data_dir / "depth"
            if resume and (refined_dir / "refined.ply").exists():
                logger.info("Resuming: Stage 7 output found, skipping")
                stage7_ply = refined_dir / "refined.ply"
            else:
                stage7_ply = runner(
                    cfg.stage07,
                    stage6_ply,
                    colmap_dir,
                    depth_dir,
                    refined_dir,
                )

        elif s == 8:
            if stage7_ply is None:
                stage7_ply = data_dir / "refined" / "refined.ply"
                if not stage7_ply.exists():
                    # Fallback to optimized if refinement was skipped
                    stage7_ply = data_dir / "optimized" / "optimized.ply"
                if not stage7_ply or not stage7_ply.exists():
                    raise click.ClickException(
                        "Stage 8 requires Stage 6/7 output. Run Stage 6 or 7 first."
                    )
            export_dir = data_dir / "export"
            if resume and (export_dir / "final.ply").exists():
                logger.info("Resuming: Stage 8 output found, skipping")
            else:
                runner(cfg.stage08, stage7_ply, export_dir)

    logger.info("=" * 50)
    logger.info("Pipeline complete. Outputs in: %s", data_dir.resolve())
    logger.info("=" * 50)


# ---------------------------------------------------------------------------
# Export command
# ---------------------------------------------------------------------------

@main.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--config", "-c", type=click.Path(exists=True), help="YAML config file")
@click.option(
    "--format",
    "-f",
    "formats",
    multiple=True,
    type=click.Choice(["ply", "sog", "spz", "html"]),
    help="Export format (can be given multiple times)",
)
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option("--log-level", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]), default="INFO")
def export(
    input_path: str,
    config: str | None,
    formats: tuple[str, ...],
    output: str | None,
    log_level: str,
) -> None:
    """Export an optimized Gaussian Splat to final formats.

    INPUT_PATH is the directory containing optimized/refined Gaussians
    (typically ``data/optimized`` or ``data/refined``).
    """
    cfg = _load_config(config)
    cfg.log_level = log_level
    _setup_logging(log_level)

    input_dir = Path(input_path)
    export_dir = Path(output) if output else cfg.data_dir / "export"

    logger = logging.getLogger("sphereforge.cli")
    logger.info("SphereForge export: %s", input_dir)

    # Find the best available PLY
    refined_ply = input_dir / "refined.ply"
    optimized_ply = input_dir / "optimized.ply"
    if refined_ply.exists():
        ply_path = refined_ply
    elif optimized_ply.exists():
        ply_path = optimized_ply
    else:
        # Maybe the user pointed directly at a PLY file
        if input_dir.suffix.lower() == ".ply":
            ply_path = input_dir
        else:
            raise click.ClickException(
                f"No refined.ply or optimized.ply found in {input_dir}. "
                "Please provide a directory with Gaussian output or a .ply file."
            )

    logger.info("Using input PLY: %s", ply_path)

    # Override export formats if specified on CLI
    if formats:
        cfg.stage08.export_format = list(formats)

    run_stage08 = _import_stage_runner(8)
    result = run_stage08(cfg.stage08, ply_path, export_dir)

    click.echo("Export complete:")
    for fmt, path in result["output_paths"].items():
        click.echo(f"  {fmt}: {path}")


# ---------------------------------------------------------------------------
# Status command
# ---------------------------------------------------------------------------

@main.command()
@click.option("--json-output", is_flag=True, help="Output as JSON for scripting")
def status(json_output: bool) -> None:
    """Show pipeline progress and task completion status."""
    from sphereforge.logging_utils import read_progress

    progress = read_progress()

    if json_output:
        import json

        click.echo(json.dumps(progress, indent=2))
    else:
        click.echo("SphereForge Progress")
        click.echo("=" * 40)
        total = progress.get("total", 0)
        completed = progress.get("completed", 0)
        if total > 0:
            pct = completed / total * 100
            click.echo(f"  Completed: {completed}/{total} ({pct:.0f}%)")
        else:
            click.echo("  No tasks found.")
        click.echo()
        stages = progress.get("stages", {})
        for stage_name, stage_info in stages.items():
            done = stage_info.get("done", 0)
            total_s = stage_info.get("total", 0)
            pct_s = done / total_s * 100 if total_s > 0 else 0
            bar_len = 20
            filled = int(bar_len * done / total_s) if total_s > 0 else 0
            bar = "█" * filled + "░" * (bar_len - filled)
            click.echo(f"  {stage_name}: [{bar}] {done}/{total_s} ({pct_s:.0f}%)")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rescale_sparse_model_to_metric(
    sparse_model: dict[str, Any],
    depth_paths: list[Path],
    frame_paths: list[Path],
    cubemap_dir: Path,
) -> dict[str, Any]:
    """Rescale a scale-free SfM reconstruction into metric units.

    Monocular SfM cannot recover absolute scale, so the sparse model and the
    metric depth maps produced by Stage 4 disagree by an unknown factor.
    Without correcting it, Stage 5 projects metric depth into a
    non-metric world frame and every downstream stage inherits the error.

    Args:
        sparse_model: Parsed COLMAP sparse model.
        depth_paths: Stage 4 depth maps (``*_depth.npy``).
        frame_paths: Stage 1 ERP frames, aligned with *depth_paths*.
        cubemap_dir: Stage 2 dataset directory.

    Returns:
        The sparse model rescaled into metres, or the original model when the
        scale cannot be estimated (a warning is logged).
    """
    from sphereforge.stages.stage04_depth.depth_alignment import (
        estimate_reconstruction_scale,
        rescale_sparse_model,
    )

    if not depth_paths or not frame_paths:
        return sparse_model

    # Rescaling is not idempotent: applying it twice would square the factor.
    source_dir = sparse_model.get("_source_dir")
    if source_dir is not None and (Path(source_dir) / ".metric_scale.json").exists():
        logger.info("Sparse model already in metric units; skipping rescale")
        return sparse_model

    depth_maps = []
    names = []
    for depth_path, frame_path in zip(depth_paths, frame_paths, strict=False):
        try:
            depth_maps.append(np.load(str(depth_path)))
        except (OSError, ValueError) as exc:
            logger.warning("Could not read depth map %s: %s", depth_path, exc)
            continue
        names.append(Path(frame_path).name)

    if not depth_maps:
        return sparse_model

    scale = estimate_reconstruction_scale(depth_maps, names, sparse_model, cubemap_dir)
    if scale is None:
        logger.warning(
            "Could not estimate the SfM-to-metric scale; downstream stages will "
            "work in arbitrary units and depth/geometry may disagree."
        )
        return sparse_model

    rescaled = rescale_sparse_model(sparse_model, scale)
    # Persist the rescaled model. Keeping it only in memory means any later
    # stage that re-reads the sparse model from disk (a standalone --stage 5
    # run, or a --resume after Stage 4) silently works in the old, scale-free
    # units, so geometry and depth disagree by the scale factor.
    _persist_rescaled_sparse_model(rescaled, scale)
    return rescaled


def _persist_rescaled_sparse_model(sparse_model: dict[str, Any], scale: float) -> None:
    """Persist the metric rescale so a later re-read sees the same geometry.

    ``rescale_sparse_model`` already scaled the points and the image
    translations in memory. Only the *persisted* point cloud needs updating:
    the rig sidecar is applied on top of the model's image translations by
    :func:`apply_rigidity_to_model`, so scaling it here as well would apply the
    factor twice and leave the cameras ~15x too close to the origin.

    pycolmap cannot hold a panorama rig (``Image.cam_from_world`` is read-only
    and ``Frame.set_cam_from_world`` keeps only the last sensor written), so the
    corrected poses stay in the sidecar and the point cloud is rewritten
    directly.

    Args:
        sparse_model: The already-rescaled model (used for its source directory).
        scale: Factor that was applied to the model.
    """
    sparse_dir = sparse_model.get("_source_dir")
    if sparse_dir is None:
        return
    sparse_dir = Path(sparse_dir)
    marker = sparse_dir / ".metric_scale.json"
    if marker.exists():
        logger.debug("Sparse model already rescaled; skipping rewrite")
        return
    try:
        _rescale_sparse_points(sparse_dir, scale)
        # Written last: its presence is what makes the rescale idempotent.
        marker.write_text(json.dumps({"scale": scale}), encoding="utf-8")
        logger.info("Recorded metric rescale (%.4f) for %s", scale, sparse_dir)
    except (OSError, ValueError, ImportError) as exc:
        logger.warning("Could not record the metric rescale: %s", exc)


def _rescale_sparse_points(sparse_dir: Path, scale: float) -> None:
    """Scale the 3D points *and* the camera poses in the COLMAP model.

    Points and cameras must share one scale. Scaling only the points leaves the
    cameras at the old scale, which makes ``camera_to_point_radius`` explode
    (measured: 1.99 -> 4.87 after a 0.136 rescale) and pushes the camera path
    outside the geometry. That ratio is scale-invariant, so the corruption is
    invisible until downstream stages place Gaussians badly.

    The whole model is rewritten through pycolmap's *binary* writer. The text
    writer is not an option here: ``write_text`` on a panorama-rig model drops
    observations (measured 60,740 -> 49,710) because the text format cannot
    faithfully represent the rig. Scaling ``rig_from_world`` scales every sensor
    of a frame at once, which is exactly right for a shared optical centre.

    Args:
        sparse_dir: Directory holding the COLMAP sparse model.
        scale: Factor to apply to every 3D position.
    """
    import pycolmap

    reconstruction = pycolmap.Reconstruction(str(sparse_dir))
    for point in reconstruction.points3D.values():
        point.xyz = np.asarray(point.xyz, dtype=np.float64) * scale

    # The mapper does not always model the rig sensors as sharing one optical
    # centre: ``sensor_from_rig`` can carry a non-zero translation (measured up
    # to ~1.3 units). Those offsets are world-space distances too, so they must
    # be scaled alongside the rig pose or the cameras end up in a different
    # scale from the points.
    for rig in reconstruction.rigs.values():
        ref_id = rig.ref_sensor_id.id
        for sensor in rig.sensor_ids():
            if sensor.id == ref_id:
                continue
            transform = rig.sensor_from_rig(sensor)
            scaled = pycolmap.Rigid3d()
            scaled.rotation.quat = np.asarray(transform.rotation.quat)
            scaled.translation = np.asarray(transform.translation, dtype=np.float64) * scale
            rig.set_sensor_from_rig(sensor, scaled)

    for frame in reconstruction.frames.values():
        pose = frame.rig_from_world
        if callable(pose):
            pose = pose()
        scaled = pycolmap.Rigid3d()
        scaled.rotation.quat = np.asarray(pose.rotation.quat)
        scaled.translation = np.asarray(pose.translation, dtype=np.float64) * scale
        frame.rig_from_world = scaled

    # Models without a rig still need their per-image poses scaled.
    if not reconstruction.frames:
        for image in reconstruction.images.values():
            pose = image.cam_from_world
            if callable(pose):
                pose = pose()
            scaled = pycolmap.Rigid3d()
            scaled.rotation.quat = np.asarray(pose.rotation.quat)
            scaled.translation = np.asarray(pose.translation, dtype=np.float64) * scale
            reconstruction.frame(image.frame_id).set_cam_from_world(
                image.camera_id, scaled
            )

    reconstruction.write(str(sparse_dir))
    logger.info(
        "Rescaled %d sparse points and %d camera poses by %.4f",
        len(reconstruction.points3D),
        len(reconstruction.images),
        scale,
    )


def _has_frames(frames_dir: Path) -> bool:
    """Check whether *frames_dir* contains image files."""
    if not frames_dir.is_dir():
        return False
    return any(frames_dir.glob("*.png")) or any(frames_dir.glob("*.jpg"))


def _load_existing_frames(frames_dir: Path) -> list[Path]:
    """Return the Stage 1 frame paths already present on disk (sorted)."""
    if not frames_dir.is_dir():
        return []
    frames = sorted(frames_dir.glob("*.png"))
    if not frames:
        frames = sorted(frames_dir.glob("*.jpg"))
    return frames


def _has_depth_maps(depth_dir: Path) -> bool:
    """Check whether *depth_dir* contains depth map files."""
    if not depth_dir.is_dir():
        return False
    return any(depth_dir.glob("*_depth.npy"))


if __name__ == "__main__":
    main()

