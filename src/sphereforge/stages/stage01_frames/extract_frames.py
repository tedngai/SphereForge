"""Extract frames from video using FFmpeg.

Provides the ``extract_frames`` function which calls FFmpeg via subprocess
to decode a video file and save frames as 6-digit zero-padded PNG images
at a configurable framerate.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_frames(
    video_path: Path,
    output_dir: Path,
    fps: int = 5,
) -> list[Path]:
    """Extract frames from a video file at a target FPS using FFmpeg.

    Calls ``ffmpeg`` to decode the input video and write frames as
    ``frame_000001.png``, ``frame_000002.png``, etc. into *output_dir*.

    Args:
        video_path: Path to the input video file (e.g. .mp4, .mov).
        output_dir: Directory where extracted PNG frames will be written.
            Created automatically if it does not exist.
        fps: Target extraction framerate.  Defaults to 5.

    Returns:
        Sorted list of Paths to the extracted frame PNGs.

    Raises:
        FileNotFoundError: If *video_path* does not exist.
        RuntimeError: If FFmpeg is not installed or the extraction fails.
    """
    # --- Validate FFmpeg availability ----------------------------------------
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "FFmpeg is not installed. Please install FFmpeg and ensure it "
            "is available on your PATH."
        )
    except subprocess.CalledProcessError:
        raise RuntimeError(
            "FFmpeg is installed but returned a non-zero exit code when "
            "checking its version."
        )

    # --- Validate input ------------------------------------------------------
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Build FFmpeg command ------------------------------------------------
    output_pattern = output_dir / "frame_%06d.png"
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vf", f"fps={fps}",
        "-q:v", "2",  # high-quality PNG
        str(output_pattern),
    ]

    logger.info(
        "Extracting frames from %s at %d fps → %s",
        video_path,
        fps,
        output_dir,
    )

    # --- Run FFmpeg -----------------------------------------------------------
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode(errors="replace")
        raise RuntimeError(
            f"FFmpeg failed with return code {result.returncode}:\n{stderr}"
        )

    # --- Collect output paths -------------------------------------------------
    frame_paths = sorted(output_dir.glob("frame_*.png"))
    logger.info("Extracted %d frames to %s", len(frame_paths), output_dir)

    return frame_paths