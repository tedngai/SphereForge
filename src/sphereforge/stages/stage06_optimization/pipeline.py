"""SphereForge Stage 6: Multi-View Gaussian Optimization pipeline orchestration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import torch

from sphereforge.common.io import read_ply, write_ply

if TYPE_CHECKING:
    from sphereforge.config import Stage06Config

logger = logging.getLogger(__name__)


def run_stage06(
    config: Stage06Config,
    initial_ply_path: Path,
    colmap_dir: Path,
    depth_dir: Path,
    output_dir: Path,
) -> Path:
    """Run Stage 6: Multi-View Gaussian Optimization.

    Loads initial Gaussians from PLY, constructs training views from COLMAP
    data, runs the training loop, and writes optimized Gaussians.

    Args:
        config: Stage 6 configuration.
        initial_ply_path: Path to initial .ply from Stage 5.
        colmap_dir: Path to COLMAP sparse model directory.
        depth_dir: Path to aligned depth maps from Stage 4.
        output_dir: Output directory for optimized Gaussians.

    Returns:
        Path to the optimized .ply file.
    """
    from sphereforge.common.colmap_helpers import parse_cameras_txt, parse_images_txt
    from sphereforge.stages.stage06_optimization.training_loop import train_gaussians

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load initial Gaussians
    logger.info("Loading initial Gaussians from %s", initial_ply_path)
    gaussians_ply = read_ply(initial_ply_path)

    # Convert to torch tensors
    initial_gaussians = {
        "positions": torch.from_numpy(gaussians_ply["positions"]).float(),
        "colors": torch.from_numpy(gaussians_ply["colors"]).float(),
        "opacities": torch.from_numpy(gaussians_ply["opacities"]).float(),
        "scales": torch.from_numpy(gaussians_ply["scales"]).float(),
        "rotations": torch.from_numpy(gaussians_ply["rotations"]).float(),
    }

    # Load COLMAP model
    cameras_path = colmap_dir / "cameras.txt"
    images_path = colmap_dir / "images.txt"

    cameras = {}
    images_dict = {}
    if cameras_path.exists():
        cameras = parse_cameras_txt(cameras_path)
    if images_path.exists():
        images_dict = parse_images_txt(images_path)

    # Build training views
    training_views = []
    for _img_id, img_data in sorted(images_dict.items()):
        cam = cameras.get(img_data["camera_id"], None)
        if cam is None:
            logger.warning("Camera %d not found for image %s, skipping", img_data["camera_id"], img_data["name"])
            continue

        # Build viewmat from quaternion + translation
        from sphereforge.common.colmap_helpers import quat_to_rotation_matrix
        R = quat_to_rotation_matrix(img_data["qw"], img_data["qx"], img_data["qy"], img_data["qz"])
        t = np.array([img_data["tx"], img_data["ty"], img_data["tz"]])
        viewmat = np.eye(4)
        viewmat[:3, :3] = R
        viewmat[:3, 3] = t

        # Load target image
        img_path = colmap_dir / "images" / img_data["name"]
        if img_path.exists():
            from sphereforge.common.io import read_image
            target_image = read_image(img_path)  # (H, W, 3) uint8
            target_image = torch.from_numpy(target_image).float().permute(2, 0, 1) / 255.0  # (3, H, W)
        else:
            logger.warning("Image %s not found, using placeholder", img_path)
            target_image = torch.rand(3, cam["height"], cam["width"])

        # Load target depth
        depth_path = depth_dir / img_data["name"].replace(".png", ".npy")
        if depth_path.exists():
            target_depth = np.load(str(depth_path)).astype(np.float32)
            target_depth = torch.from_numpy(target_depth)
        else:
            logger.warning("Depth %s not found, using placeholder", depth_path)
            target_depth = torch.rand(cam["height"], cam["width"]) * 10.0

        # Compute FOV from camera intrinsics
        params = cam["params"]
        fx = params[0]
        fov = 2 * np.degrees(np.arctan(cam["width"] / (2 * fx)))

        # Compute latitudes (ERP pixel → latitude mapping)
        latitudes = _compute_view_latitudes(cam["height"], cam["width"])

        training_views.append({
            "viewmat": torch.from_numpy(viewmat.astype(np.float32)),
            "fov": float(fov),
            "height": cam["height"],
            "width": cam["width"],
            "target_image": target_image,
            "target_depth": target_depth,
            "latitudes": latitudes,
        })

    if not training_views:
        raise RuntimeError(f"No training views found in {colmap_dir}")

    logger.info("Built %d training views", len(training_views))

    # Run training
    checkpoint_dir = output_dir / "checkpoints"
    final_gaussians = train_gaussians(
        initial_gaussians=initial_gaussians,
        training_views=training_views,
        config=config,
        checkpoint_dir=checkpoint_dir,
    )

    # Write optimized PLY
    output_ply = output_dir / "optimized.ply"
    write_ply(
        output_ply,
        positions=final_gaussians["positions"].numpy(),
        colors=final_gaussians["colors"].numpy().astype(np.uint8)
            if final_gaussians["colors"].max() > 1 else (final_gaussians["colors"].numpy() * 255).astype(np.uint8),
        opacities=final_gaussians["opacities"].numpy(),
        scales=final_gaussians["scales"].numpy(),
        rotations=final_gaussians["rotations"].numpy(),
    )

    logger.info("Stage 6 complete: %s (%d Gaussians)", output_ply, final_gaussians["positions"].shape[0])
    return output_ply


def _compute_view_latitudes(height: int, width: int) -> torch.Tensor:
    """Compute latitude map for a training view.

    For cubemap crops, approximate latitude based on vertical position.
    For ERP images, exact latitude from pixel row.

    Args:
        height: Image height.
        width: Image width.

    Returns:
        (H, W) tensor of latitudes in radians.
    """
    v = torch.linspace(-np.pi / 2, np.pi / 2, height)
    latitudes = v.unsqueeze(1).expand(height, width)
    return latitudes
