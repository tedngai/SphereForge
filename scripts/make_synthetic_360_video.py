"""Generate a synthetic 360-degree equirectangular video for end-to-end testing.

The scene is a textured box (room) with a few coloured boxes inside. A virtual
360 camera moves along a short path, so consecutive frames share plenty of
overlap and structure-from-motion can register them.

Rendering is done by ray casting against planes: for every ERP pixel we cast a
world-space ray and intersect it with the six room walls, keeping the nearest
hit. That is exact for box geometry and fast enough for a short clip.

Usage:
    python scripts/make_synthetic_360_video.py --out data/raw/synthetic_room.mp4
"""

from __future__ import annotations

import argparse
import math
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np

# Room half-extents (metres). The camera stays well inside.
ROOM_MIN = np.array([-2.5, -1.5, -2.5])
ROOM_MAX = np.array([2.5, 1.5, 2.5])


def _checker(a: float, b: float, scale: float) -> np.ndarray:
    """Two-tone checkerboard colour from two surface coordinates."""
    c = (np.floor(a * scale) + np.floor(b * scale)).astype(np.int64) % 2
    return np.where(c[..., None] == 0, np.array([200, 170, 140]), np.array([90, 120, 160]))


def _texture_noise(a: float, b: float, seed: int) -> np.ndarray:
    """Deterministic pseudo-random texture (gives SIFT something to latch on)."""
    grid = np.stack([np.floor(a * 6.0), np.floor(b * 6.0)], axis=-1).astype(np.int64)
    h = (
        grid[..., 0] * 73856093
        ^ grid[..., 1] * 19349663
        ^ (seed * 83492791)
    )
    v = (h % 97).astype(np.float32) / 96.0
    return np.stack([v * 220 + 20, (1 - v) * 180 + 40, ((v * 7) % 1.0) * 200 + 30], axis=-1)


def _erp_directions(height: int, width: int) -> np.ndarray:
    """World-space unit ray directions for every ERP pixel (Stage 2 convention)."""
    phi = (np.arange(width) + 0.5) / width * 2.0 * math.pi - math.pi
    theta = math.pi / 2.0 - (np.arange(height) + 0.5) / height * math.pi
    phi_grid, theta_grid = np.meshgrid(phi, theta)
    cos_theta = np.cos(theta_grid)
    return np.stack(
        [
            np.sin(phi_grid) * cos_theta,
            np.sin(theta_grid),
            -np.cos(phi_grid) * cos_theta,
        ],
        axis=-1,
    )


def render_erp(camera_pos: np.ndarray, height: int, width: int) -> np.ndarray:
    """Ray-cast the box room from *camera_pos* into an ERP image."""
    dirs = _erp_directions(height, width)
    n = dirs.shape[0] * dirs.shape[1]
    d = dirs.reshape(n, 3)

    with np.errstate(divide="ignore", invalid="ignore"):
        t_max = np.where(d > 1e-9, (ROOM_MAX - camera_pos) / d, np.inf)
        t_min = np.where(d < -1e-9, (ROOM_MIN - camera_pos) / d, np.inf)
    t_hi = np.minimum(t_max, t_min)
    t_hit = np.min(t_hi, axis=1)
    axis = np.argmin(t_hi, axis=1)
    hit = camera_pos + d * t_hit[:, None]

    # Surface coordinates for texturing: use the two axes orthogonal to the hit axis.
    u = np.take_along_axis(hit, ((axis + 1) % 3)[:, None], axis=1)[:, 0]
    v = np.take_along_axis(hit, ((axis + 2) % 3)[:, None], axis=1)[:, 0]
    colour = _checker(u, v, 1.5) * 0.6 + _texture_noise(u, v, 7) * 0.4

    # A few coloured boxes on the floor, plus a bright marker so depth is
    # unambiguous. Each is an axis-aligned box; test ray/box intersection.
    boxes = [
        (np.array([-1.4, -1.5, -1.2]), np.array([-0.6, -0.6, -0.4]), np.array([220, 60, 60])),
        (np.array([0.6, -1.5, -1.4]), np.array([1.5, -0.2, -0.5]), np.array([60, 200, 80])),
        (np.array([-0.8, -1.5, 0.9]), np.array([0.2, -0.9, 1.8]), np.array([70, 90, 230])),
        (np.array([1.2, -0.4, 1.0]), np.array([2.2, 0.9, 2.1]), np.array([230, 200, 60])),
    ]
    for bmin, bmax, bcol in boxes:
        with np.errstate(divide="ignore", invalid="ignore"):
            tb_max = np.where(d > 1e-9, (bmax - camera_pos) / d, np.inf)
            tb_min = np.where(d < -1e-9, (bmin - camera_pos) / d, np.inf)
        t_near = np.maximum(tb_max, tb_min).max(axis=1)
        t_far = np.minimum(tb_max, tb_min).min(axis=1)
        hit_box = (t_near <= t_far) & (t_near > 0) & (t_near < t_hit)
        if np.any(hit_box):
            colour[hit_box] = bcol
            t_hit[hit_box] = t_near[hit_box]

    # Add a little shading so the image is not flat.
    shade = np.clip(1.0 - 0.12 * t_hit, 0.55, 1.0)[:, None]
    img = np.clip(colour * shade, 0, 255).astype(np.uint8)
    return img.reshape(height, width, 3)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("data/raw/synthetic_room.mp4"))
    parser.add_argument("--frames", type=int, default=24)
    parser.add_argument("--fps", type=int, default=6)
    parser.add_argument("--height", type=int, default=512, help="ERP height (width = 2x)")
    parser.add_argument(
        "--room-scale",
        type=float,
        default=1.0,
        help="Uniform scale on the room box; >1 gives a larger room",
    )
    parser.add_argument(
        "--path-scale",
        type=float,
        default=1.0,
        help="Scale on the camera path length, independent of the room",
    )
    args = parser.parse_args()

    # A different room/path combination exercises generalisation: the pipeline
    # should not only work for the one scene it was tuned against.
    global ROOM_MIN, ROOM_MAX
    ROOM_MIN = ROOM_MIN * args.room_scale
    ROOM_MAX = ROOM_MAX * args.room_scale

    width = args.height * 2
    args.out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for i in range(args.frames):
            frac = i / max(1, args.frames - 1)
            # Short arc through the room, with a slow yaw so views differ.
            pos = np.array(
                [
                    (-0.9 + 1.8 * frac) * args.path_scale,
                    (-0.35 + 0.12 * math.sin(frac * math.pi)) * args.path_scale,
                    (-0.8 + 1.6 * frac) * args.path_scale,
                ]
            )
            img = render_erp(pos, args.height, width)
            cv2.imwrite(str(tmp_dir / f"f{i:04d}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            print(f"rendered frame {i + 1}/{args.frames}", flush=True)

        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-framerate", str(args.fps),
            "-i", str(tmp_dir / "f%04d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16",
            str(args.out),
        ]
        subprocess.run(cmd, check=True)

    print(f"wrote {args.out} ({args.frames} frames, {width}x{args.height} ERP)")


if __name__ == "__main__":
    main()
