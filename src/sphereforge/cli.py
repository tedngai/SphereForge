"""SphereForge CLI entry point."""

from __future__ import annotations

from pathlib import Path

import click


@click.group()
@click.version_option(package_name="sphereforge")
def main() -> None:
    """SphereForge: Transform 360° footage into 3D Gaussian Splat scenes."""


@main.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--config", "-c", type=click.Path(exists=True), help="YAML config file")
@click.option("--stage", "-s", type=int, help="Run only this stage (1-8)")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
def process(input_path: str, config: str | None, stage: int | None, output: str | None) -> None:
    """Process 360° video or images into a Gaussian Splat scene.

    INPUT_PATH can be a video file (.mp4, .mov) or a directory of equirectangular images.
    """
    click.echo(f"SphereForge processing: {input_path}")
    if config:
        click.echo(f"  Config: {config}")
    if stage:
        click.echo(f"  Stage: {stage}")
    if output:
        click.echo(f"  Output: {output}")

    # TODO: Load config, validate input, run pipeline stages
    click.echo("Pipeline not yet implemented.")


@main.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--config", "-c", type=click.Path(exists=True), help="YAML config file")
@click.option("--format", "-f", "formats", multiple=True, help="Export format (ply, sog, spz, html)")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
def export(input_path: str, config: str | None, formats: tuple[str, ...], output: str | None) -> None:
    """Export an optimized Gaussian Splat to final formats.

    INPUT_PATH is the directory containing optimized/refined Gaussians.
    """
    click.echo(f"SphereForge export: {input_path}")
    if formats:
        click.echo(f"  Formats: {', '.join(formats)}")

    # TODO: Load config, run Stage 8 export
    click.echo("Export not yet implemented.")


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


if __name__ == "__main__":
    main()
