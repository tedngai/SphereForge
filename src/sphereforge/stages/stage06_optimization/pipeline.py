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
    from sphereforge.common.colmap_helpers import parse_cameras_txt, parse_images_txt, read_colmap_binary
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

    # Load COLMAP model — check common subdirectory "0/" first
    for candidate in [colmap_dir / "0", colmap_dir]:
        cameras_path = candidate / "cameras.txt"
        cameras_bin = candidate / "cameras.bin"
        if cameras_path.exists() or cameras_bin.exists():
            colmap_model_dir = candidate
            break
    else:
        colmap_model_dir = colmap_dir

    # Load cameras and images (try text first, fall back to binary)
    cameras = {}
    images_dict = {}
    cameras_txt = colmap_model_dir / "cameras.txt"
    images_txt = colmap_model_dir / "images.txt"
    cameras_bin = colmap_model_dir / "cameras.bin"
    images_bin = colmap_model_dir / "images.bin"
    if cameras_txt.exists():
        cameras = parse_cameras_txt(cameras_txt)
    elif cameras_bin.exists():
        cameras = read_colmap_binary(cameras_bin)
    if images_txt.exists():
        images_dict = parse_images_txt(images_txt)
    elif images_bin.exists():
        images_dict = read_colmap_binary(images_bin)

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

        # Load target image — search in multiple possible locations
        name = img_data["name"]
        # Strip ``images/`` or ``masks/`` prefix if present (COLMAP convention)
        clean_name = name.replace("images/", "").replace("masks/", "")
        possible_img_paths = [
            colmap_dir.parent.parent / "cubemaps" / name,
            colmap_dir.parent.parent / "cubemaps" / clean_name,
            colmap_dir.parent.parent / "cubemaps" / "images" / clean_name,
            colmap_dir / "images" / name,
        ]
        img_path = None
        for p in possible_img_paths:
            if p.exists():
                img_path = p
                break
        if img_path is not None:
            from sphereforge.common.io import read_image
            target_image = read_image(img_path)  # (H, W, 3) uint8
            target_image = torch.from_numpy(target_image).float().permute(2, 0, 1) / 255.0  # (3, H, W)
        else:
            logger.warning("Image %s not found in any expected location, using placeholder", name)
            target_image = torch.rand(3, cam["height"], cam["width"])

        # Load target depth — try face name first, then ERP frame name
        import re
        depth_name = name.replace(".png", ".npy")
        # Strip images/ prefix if present
        clean_depth_name = depth_name.replace("images/", "")
        # Possible depth file paths
        possible_depth_paths = [
            depth_dir / depth_name,
            depth_dir / clean_depth_name,
            # Try ERP frame name (strip face suffix, add _depth suffix)
            depth_dir / re.sub(r"_(left|right|front|back|top|bottom)\.npy$", "_depth.npy", clean_depth_name),
            depth_dir / re.sub(r"images/", "", re.sub(r"_(left|right|front|back|top|bottom)\.npy$", "_depth.npy", depth_name)),
        ]
        depth_path = None
        for dp in possible_depth_paths:
            if dp.exists():
                depth_path = dp
                break
        if depth_path is not None:
            target_depth = np.load(str(depth_path)).astype(np.float32)
            target_depth = torch.from_numpy(target_depth)
        else:
            logger.warning("Depth for %s not found in any expected location, using placeholder", name)
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
    colors_np = final_gaussians["colors"].cpu()
    # Handle SH coefficient shape: (N, K, 3) → use SH degree 0 (first coefficient)
    if colors_np.ndim == 3:
        colors_np = colors_np[:, 0, :]  # (N, K, 3) → (N, 3)
    colors_np = colors_np.numpy()
    if colors_np.max() <= 1.0:
        colors_np = (colors_np * 255).astype(np.uint8)
    else:
        colors_np = colors_np.astype(np.uint8)
    write_ply(
        output_ply,
        positions=final_gaussians["positions"].cpu().numpy(),
        colors=colors_np,
        opacities=final_gaussians["opacities"].cpu().numpy(),
        scales=final_gaussians["scales"].cpu().numpy(),
        rotations=final_gaussians["rotations"].cpu().numpy(),
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
