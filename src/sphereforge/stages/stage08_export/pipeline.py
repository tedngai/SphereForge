"""SphereForge Stage 8: Post-Processing & Export pipeline orchestration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from sphereforge.common.io import read_ply, write_ply

if TYPE_CHECKING:
    from sphereforge.config import Stage08Config

logger = logging.getLogger(__name__)


def _resolve_max_scale_ratio(max_scale: str) -> float:
    """Resolve Stage 8 max-scale config to a scene-relative ratio.

    Args:
        max_scale: Config value. ``"auto"`` uses the same 10%-of-scene
            heuristic as guarded Stage 6 pruning. Numeric strings are
            interpreted directly as ratios.

    Returns:
        Positive scale ratio relative to scene extent.

    Raises:
        ValueError: If the config value is unsupported or non-positive.
    """
    if max_scale == "auto":
        return 0.1

    try:
        ratio = float(max_scale)
    except ValueError as exc:
        raise ValueError(
            f"Invalid stage08.max_scale value {max_scale!r}; expected 'auto' or a positive ratio"
        ) from exc

    if ratio <= 0:
        raise ValueError(
            f"stage08.max_scale must resolve to a positive ratio, got {max_scale!r}"
        )

    return ratio


def run_stage08(
    config: Stage08Config,
    refined_ply_path: Path,
    output_dir: Path,
) -> dict:
    """Run Stage 8: Post-Processing & Export.

    Applies final pruning, compact box culling, then exports in requested formats.

    Args:
        config: Stage 8 configuration.
        refined_ply_path: Path to refined .ply from Stage 7.
        output_dir: Output directory for all exports.

    Returns:
        Dict with: output_paths (format -> path), stats (pruning/culling stats).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load refined Gaussians
    logger.info("Loading refined Gaussians from %s", refined_ply_path)
    data = read_ply(refined_ply_path)
    positions = data["positions"]
    colors = data["colors"]
    opacities = data["opacities"]
    scales = data["scales"]
    rotations = data["rotations"]
    sh_coeffs = data.get("sh_coeffs", None)

    n_before = positions.shape[0]
    stats = {"n_before": n_before}

    # ---- Final RAP pruning ----
    if config.rap_final_pass:
        from sphereforge.stages.stage08_export.final_pruning import final_rap_prune

        max_scale_ratio = _resolve_max_scale_ratio(config.max_scale)

        gaussians = {
            "positions": positions,
            "colors": colors,
            "opacities": opacities,
            "scales": scales,
            "rotations": rotations,
        }
        if sh_coeffs is not None:
            gaussians["sh_coeffs"] = sh_coeffs

        gaussians, prune_stats = final_rap_prune(
            gaussians,
            min_opacity=config.min_opacity,
            max_scale_ratio=max_scale_ratio,
        )
        stats.update(prune_stats)
        positions = gaussians["positions"]
        colors = gaussians["colors"]
        opacities = gaussians["opacities"]
        scales = gaussians["scales"]
        rotations = gaussians["rotations"]
        sh_coeffs = gaussians.get("sh_coeffs", None)

        logger.info(
            "RAP pruning: %d → %d Gaussians (max_scale_ratio=%.4f)",
            n_before,
            positions.shape[0],
            max_scale_ratio,
        )

    # ---- Compact box culling ----
    if config.compact_box_culling:
        from sphereforge.stages.stage08_export.compact_culling import compact_box_cull

        keep_mask = compact_box_cull(
            positions, scales, rotations,
            sigma=config.compact_box_sigma,
        )
        n_before_cull = positions.shape[0]
        positions = positions[keep_mask]
        colors = colors[keep_mask]
        opacities = opacities[keep_mask]
        scales = scales[keep_mask]
        rotations = rotations[keep_mask]
        if sh_coeffs is not None:
            sh_coeffs = sh_coeffs[keep_mask]

        n_culled = n_before_cull - positions.shape[0]
        stats["n_culled_compact_box"] = int(n_culled)
        logger.info("Compact box culling: removed %d Gaussians", n_culled)

    stats["n_after"] = positions.shape[0]

    # ---- Write final PLY (always) ----
    final_ply = output_dir / "final.ply"
    write_ply(
        final_ply,
        positions=positions,
        colors=colors,
        opacities=opacities,
        scales=scales,
        rotations=rotations,
        sh_coeffs=sh_coeffs,
    )
    output_paths: dict[str, Path] = {"ply": final_ply}
    logger.info("Final PLY: %s (%d Gaussians)", final_ply, positions.shape[0])

    # ---- Export in requested formats ----
    for fmt in config.export_format:
        if fmt == "ply":
            continue  # Already done

        if fmt == "sog":
            from sphereforge.stages.stage08_export.sog_export import export_sog
            sog_path = export_sog(final_ply, output_dir / "final.sog")
            output_paths["sog"] = sog_path

        elif fmt == "spz":
            from sphereforge.stages.stage08_export.spz_export import export_spz
            spz_path = export_spz(final_ply, output_dir / "final.spz")
            output_paths["spz"] = spz_path

        elif fmt == "html":
            from sphereforge.stages.stage08_export.html_viewer import generate_html_viewer
            html_path = generate_html_viewer(final_ply, output_dir / "viewer.html")
            output_paths["html"] = html_path

        else:
            logger.warning("Unknown export format: %s", fmt)

    # ---- Optional mesh extraction ----
    if config.extract_mesh:
        from sphereforge.stages.stage08_export.mesh_extraction import extract_navigation_mesh
        mesh_path = extract_navigation_mesh(positions, output_dir / "navigation_mesh.obj")
        output_paths["mesh"] = mesh_path

    logger.info(
        "Stage 8 complete: %d Gaussians, %d export formats: %s",
        positions.shape[0],
        len(output_paths),
        list(output_paths.keys()),
    )

    return {
        "output_paths": output_paths,
        "stats": stats,
    }
