"""SphereForge Stage 6: Multi-View Gaussian Optimization pipeline orchestration."""

from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import torch

from sphereforge.common.io import read_ply, sh_rest_from_coeffs, write_ply

if TYPE_CHECKING:
    from sphereforge.config import Stage06Config

logger = logging.getLogger(__name__)


def _activated_opacity_to_logit(opacities: np.ndarray) -> np.ndarray:
    """Convert activated Stage 5 opacities into raw logits for Stage 6."""
    clipped = np.clip(np.asarray(opacities, dtype=np.float32), 1e-6, 1.0 - 1e-6)
    return np.log(clipped / (1.0 - clipped)).astype(np.float32)


def _activated_scale_to_log(scale: np.ndarray) -> np.ndarray:
    """Convert activated Stage 5 scales into raw log-scales for Stage 6."""
    clipped = np.clip(np.asarray(scale, dtype=np.float32), 1e-12, None)
    return np.log(clipped).astype(np.float32)


def _prepare_initial_gaussians_for_training(gaussians_ply: dict) -> dict[str, torch.Tensor]:
    """Normalize Stage 5 PLY parameters into Stage 6 raw optimization space."""
    colors = torch.from_numpy(gaussians_ply["colors"]).float()
    # Stage 5 stores 0-255 colours, but gsplat treats the colour channel as
    # SH DC coefficients in 0-1 space. Without this normalisation every
    # Gaussian renders ~255x too bright and the image saturates to white.
    if colors.numel() and float(colors.max()) > 1.5:
        colors = colors / 255.0

    return {
        "positions": torch.from_numpy(gaussians_ply["positions"]).float(),
        "colors": colors,
        "opacities": torch.from_numpy(
            _activated_opacity_to_logit(gaussians_ply["opacities"])
        ).float(),
        "scales": torch.from_numpy(
            _activated_scale_to_log(gaussians_ply["scales"])
        ).float(),
        "rotations": torch.from_numpy(gaussians_ply["rotations"]).float(),
    }


def _render_erp_depth_to_view(
    erp_depth: np.ndarray,
    yaw_deg: float,
    pitch_deg: float,
    fov_deg: float,
    view_size: int,
) -> np.ndarray:
    """Render an ERP depth map into a rectilinear virtual view.

    Stage 4 produces one depth map per ERP frame, but Stage 6 trains on the
    rectilinear panorama-rig views written by Stage 2. This resamples the ERP
    depth into a view using exactly the same geometry as
    :func:`sphereforge.stages.stage02_cubemap.cubemap.extract_perspective_view`,
    so the rendered depth lines up pixel-for-pixel with the training image.

    ERP depth is stored as *radial* distance (``depth * ray_direction``), so
    the resampled value is converted to the view's *perspective* depth
    (distance along the view axis) by dividing by the ray norm.

    Args:
        erp_depth: ERP depth map ``(H, W)``, radial distance.
        yaw_deg: View yaw in degrees (Stage 2 convention).
        pitch_deg: View pitch in degrees.
        fov_deg: View field of view in degrees.
        view_size: Output view side length in pixels.

    Returns:
        Perspective depth map ``(view_size, view_size)`` float32.
    """
    import cv2

    from sphereforge.stages.stage02_cubemap.cubemap import (
        _direction_to_erp_uv,
        _make_rotation_matrix,
    )

    erp_h, erp_w = erp_depth.shape[:2]
    focal = view_size / (2.0 * math.tan(math.radians(fov_deg) / 2.0))
    center = view_size / 2.0

    u_coords = np.arange(view_size, dtype=np.float64)
    v_coords = np.arange(view_size, dtype=np.float64)
    uu, vv = np.meshgrid(u_coords, v_coords)
    dx = (uu - center) / focal
    dy = (vv - center) / focal
    dz = np.ones_like(dx)
    ray_norm = np.sqrt(dx * dx + dy * dy + dz * dz)
    dirs_cam = np.stack([dx / ray_norm, dy / ray_norm, dz / ray_norm], axis=-1)

    rotation = _make_rotation_matrix(yaw_deg, pitch_deg)
    dirs_world = np.einsum("ij,...j->...i", rotation.T, dirs_cam)
    erp_u, erp_v = _direction_to_erp_uv(dirs_world, erp_w, erp_h)

    # ERP is periodic in longitude but cv2.remap's BORDER_WRAP replicates the
    # edge pixel instead of wrapping, so normalise u into [0, W) by hand.
    # Without this, the seam column (u == W) samples the wrong pixel and the
    # whole view can collapse to zeros.
    erp_u = np.mod(erp_u, erp_w)
    erp_v = np.clip(erp_v, 0.0, erp_h - 1.0)

    radial = cv2.remap(
        erp_depth.astype(np.float32),
        erp_u.astype(np.float32),
        erp_v.astype(np.float32),
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return (radial / ray_norm).astype(np.float32)


def _render_rig_view_depth(
    name: str,
    depth_dir: Path,
    cubemap_dir: Path,
    cam: dict,
) -> np.ndarray | None:
    """Render the ERP depth of a panorama-rig view into that view's frame.

    Args:
        name: COLMAP image name, e.g. ``images/pano_camera03/frame_000014.png``.
        depth_dir: Stage 4 output directory containing ``<frame>_depth.npy``.
        cubemap_dir: Stage 2 dataset directory containing ``panorama_rig.json``.
        cam: Parsed COLMAP camera entry for this view (for width/height).

    Returns:
        Perspective depth map ``(height, width)`` float32, or ``None`` when the
        dataset is not a panorama rig or the ERP depth for the frame is missing.
    """
    import json

    manifest_path = Path(cubemap_dir) / "panorama_rig.json"
    if not manifest_path.exists():
        return None

    parts = Path(name.replace("\\", "/")).parts
    # The COLMAP image name may or may not carry the "images/" prefix, so take
    # the last two components rather than requiring a fixed depth.
    if len(parts) < 2:
        return None
    camera_name, frame_file = parts[-2], parts[-1]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        logger.warning("Could not read panorama-rig manifest %s: %s", manifest_path, exc)
        return None

    camera = next(
        (c for c in manifest.get("cameras", []) if str(c.get("name")) == camera_name),
        None,
    )
    if camera is None:
        return None

    erp_depth_path = Path(depth_dir) / f"{Path(frame_file).stem}_depth.npy"
    if not erp_depth_path.exists():
        return None

    erp_depth = np.load(str(erp_depth_path)).astype(np.float32)
    fov_deg = float(manifest.get("fov", 90)) + float(manifest.get("overlap", 15))
    return _render_erp_depth_to_view(
        erp_depth,
        yaw_deg=float(camera["yaw_deg"]),
        pitch_deg=float(camera["pitch_deg"]),
        fov_deg=fov_deg,
        view_size=int(cam["width"]),
    )


def _camera_to_intrinsics_matrix(cam: dict) -> torch.Tensor:
    """Build a 3x3 intrinsics matrix from a parsed COLMAP camera entry.

    Supports the pinhole family, including models with distortion parameters.
    Stage 6 renders with a pure pinhole rasteriser, so the distortion
    coefficients are ignored; for the small distortions typical of a
    panorama-rig view this is an acceptable approximation.

    Args:
        cam: Parsed COLMAP camera entry with ``model`` and ``params``.

    Returns:
        3x3 intrinsics tensor.

    Raises:
        ValueError: If the camera model is not a supported pinhole variant.
    """
    model = cam["model"]
    params = cam["params"]

    if model == "PINHOLE":
        fx, fy, cx, cy = params[:4]
    elif model == "SIMPLE_PINHOLE":
        fx, cx, cy = params[:3]
        fy = fx
    elif model in ("SIMPLE_RADIAL", "RADIAL", "OPENCV", "SIMPLE_RADIAL_FISHEYE",
                   "RADIAL_FISHEYE", "OPENCV_FISHEYE", "FULL_OPENCV", "FOV"):
        # The first four parameters of every radial/OpenCV model are f, cx, cy.
        fx, cx, cy = params[:3]
        fy = fx
    else:
        raise ValueError(f"Unsupported COLMAP camera model for Stage 6: {model}")

    return torch.tensor(
        [[fx, 0.0, cx], [0.0, fy, cy], [0.0, 0.0, 1.0]],
        dtype=torch.float32,
    )


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
    from sphereforge.common.colmap_helpers import (
        parse_cameras_txt,
        parse_images_txt,
        read_colmap_binary,
    )
    from sphereforge.stages.stage06_optimization.training_loop import train_gaussians

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load initial Gaussians
    logger.info("Loading initial Gaussians from %s", initial_ply_path)
    gaussians_ply = read_ply(initial_ply_path)

    initial_gaussians = _prepare_initial_gaussians_for_training(gaussians_ply)
    logger.info(
        "Converted Stage 5 PLY parameters to Stage 6 raw space: opacity range %.4f..%.4f -> %.4f..%.4f, scale range %.6f..%.6f -> %.6f..%.6f",
        float(np.min(gaussians_ply["opacities"])),
        float(np.max(gaussians_ply["opacities"])),
        float(torch.min(initial_gaussians["opacities"]).item()),
        float(torch.max(initial_gaussians["opacities"]).item()),
        float(np.min(gaussians_ply["scales"])),
        float(np.max(gaussians_ply["scales"])),
        float(torch.min(initial_gaussians["scales"]).item()),
        float(torch.max(initial_gaussians["scales"]).item()),
    )

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
            # Panorama-rig views live at images/pano_cameraNN/<frame>.png, so the
            # per-face patterns above never match. Stage 4 stores one ERP depth
            # map per frame; render it into this virtual view instead of
            # falling back to random placeholder depth.
            rig_depth = _render_rig_view_depth(
                name=name,
                depth_dir=depth_dir,
                cubemap_dir=colmap_dir.parent.parent / "cubemaps",
                cam=cam,
            )
            if rig_depth is not None:
                target_depth = torch.from_numpy(rig_depth)
            else:
                logger.warning(
                    "Depth for %s not found in any expected location, using placeholder", name
                )
                target_depth = torch.rand(cam["height"], cam["width"]) * 10.0

        # Compute FOV from camera intrinsics
        params = cam["params"]
        fx = params[0]
        fov = 2 * np.degrees(np.arctan(cam["width"] / (2 * fx)))
        K = _camera_to_intrinsics_matrix(cam)

        # ErpGS cos(latitude) weighting corrects the pole oversampling of an
        # *equirectangular* image. Pinhole rig views have no such distortion;
        # mapping their rows onto -90..+90 degrees would zero the loss weight
        # of the top and bottom rows of every training image.
        latitudes = (
            _compute_view_latitudes(cam["height"], cam["width"])
            if _is_equirectangular_camera(cam)
            else None
        )

        training_views.append({
            "viewmat": torch.from_numpy(viewmat.astype(np.float32)),
            "K": K,
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

    # Write optimized PLY. The 3DGS PLY convention (and every external viewer)
    # stores *activated* opacity and scale, so undo the raw parameterisation
    # that the optimiser works in; f_dc stays in SH coefficient space.
    output_ply = output_dir / "optimized.ply"
    # ``train_gaussians`` keeps colours in SH coefficient space (gsplat's
    # convention), which is exactly what the PLY stores, so write them as-is.
    # Converting again here would divide by SH_C0 twice and flatten the scene.
    sh = final_gaussians["colors"].detach().cpu().numpy().astype(np.float32)
    if sh.ndim == 2:
        sh = sh[:, None, :]  # (N, 3) -> (N, 1, 3)
    colors_np = sh[:, 0, :]
    # Higher SH bands carry the trained view-dependent colour. Dropping them
    # leaves a DC term that was co-trained with them, so colours shift.
    sh_rest = sh_rest_from_coeffs(sh)

    raw_opacities = final_gaussians["opacities"].cpu().numpy()
    raw_scales = final_gaussians["scales"].cpu().numpy()
    write_ply(
        output_ply,
        positions=final_gaussians["positions"].cpu().numpy(),
        colors=colors_np,
        opacities=(1.0 / (1.0 + np.exp(-raw_opacities))).astype(np.float32),
        scales=np.exp(raw_scales).astype(np.float32),
        rotations=final_gaussians["rotations"].cpu().numpy(),
        sh_coeffs=sh_rest,
    )

    logger.info("Stage 6 complete: %s (%d Gaussians)", output_ply, final_gaussians["positions"].shape[0])
    return output_ply


_ERP_CAMERA_MODELS = {"EQUIRECTANGULAR", "SPHERE", "SPHERICAL"}


def _is_equirectangular_camera(cam: dict) -> bool:
    """Return True when the COLMAP camera model is equirectangular.

    Args:
        cam: Parsed COLMAP camera dict.

    Returns:
        True only for equirectangular cameras; pinhole rig views return False.
    """
    model = str(cam.get("model", "")).upper()
    return model in _ERP_CAMERA_MODELS


def _compute_view_latitudes(height: int, width: int) -> torch.Tensor:
    """Compute the per-pixel latitude map of an equirectangular training view.

    Only meaningful for ERP images, where pixel row maps linearly to latitude.
    Do not use it for pinhole views (see :func:`_is_equirectangular_camera`).

    Args:
        height: Image height.
        width: Image width.

    Returns:
        (H, W) tensor of latitudes in radians.
    """
    v = torch.linspace(-np.pi / 2, np.pi / 2, height)
    latitudes = v.unsqueeze(1).expand(height, width)
    return latitudes
