"""SphereForge configuration models.

Pydantic models for each pipeline stage with defaults matching PIPELINE_DESIGN_V2.md.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class Stage01Config(BaseModel):
    """Stage 1: Video Ingestion & Frame Selection."""

    input_fps: int = Field(default=5, description="Frame extraction framerate")
    chunk_size: int = Field(default=30, description="Frames per chunk for sharpness selection")
    min_luminance: float = Field(default=10.0, description="Discard frames darker than this")
    max_luminance: float = Field(default=245.0, description="Discard frames brighter than this")


class Stage02Config(BaseModel):
    """Stage 2: Equirect→Cubemap + COLMAP Prep."""

    n_faces: int = Field(default=6, description="Cubemap faces per frame")
    fov: int = Field(default=90, description="Degrees per cubemap face")
    overlap: int = Field(default=15, description="Degrees of overlap between faces")
    yaw_offset_step: int = Field(default=30, description="Yaw offset increment per frame group")
    crop_resolution: int = Field(default=1024, description="Pixels per crop side")
    generate_masks: bool = Field(default=True, description="Enable YOLO dynamic object masking")
    mask_classes: list[str] = Field(
        default=["person", "vehicle"], description="YOLO classes to mask"
    )
    overexposure_threshold: int = Field(default=250, description="Pixel value threshold for overexposure mask")

    # V2: RPG360 depth alignment
    rpg360_depth_model: Literal["metric3d_v2", "omnidata_v2"] = Field(
        default="metric3d_v2", description="Perspective depth model for RPG360"
    )
    rpg360_graph_optimize: bool = Field(
        default=True, description="Enable per-face scale + cross-face consistency"
    )
    rpg360_fallback: Literal["median_ratio"] = Field(
        default="median_ratio", description="Fallback if graph solve fails"
    )


class Stage03Config(BaseModel):
    """Stage 3: Multi-View SfM (COLMAP)."""

    feature_type: Literal["root_sift", "sift"] = Field(default="root_sift")
    matcher_type: Literal["sequential+vocabulary_tree", "exhaustive", "sequential"] = Field(
        default="sequential+vocabulary_tree"
    )
    refine_intrinsics: bool = Field(default=False, description="Intrinsics are known from Stage 2")
    dense_reconstruction: bool = Field(default=True, description="Run COLMAP patch-match stereo")


class Stage04Config(BaseModel):
    """Stage 4: Dense Depth Estimation."""

    depth_model: Literal["dap", "depth_anything_v2", "rpg360", "panda", "da360"] = Field(
        default="dap", description="V2 default: DAP (Depth Any Panoramas). 'panda' is deprecated."
    )
    scale_alignment: Literal["median_ratio_with_rpg360_anchor", "median_ratio"] = Field(
        default="median_ratio_with_rpg360_anchor",
        description="V2: uses RPG360/DAP depth as local anchor",
    )
    sky_threshold: str = Field(default="auto", description="Percentile or fixed value")
    depth_min: str = Field(default="auto", description="Clip near geometry")
    depth_max: str = Field(default="auto", description="Clip far geometry")

    # RPG360-only fallback config
    rpg360_perspective_model: Literal["metric3d_v2", "depth_anything_v2", "omnidata_v2"] = Field(
        default="depth_anything_v2", description="Perspective model for RPG360 cubemap faces"
    )


class Stage05Config(BaseModel):
    """Stage 5: Initial Gaussian Seeding."""

    stride: int = Field(default=1, description="V2: full resolution by default")
    stride_low_confidence: int = Field(
        default=4, description="V2: sparse seeding for unreliable depth pixels"
    )
    grazing_angle: int = Field(default=65, description="Edge clipping threshold (90=off)")
    outlier_pruning: float = Field(default=0.3, description="Floater removal strength")
    sparse_pruning: float = Field(default=0.3, description="Isolated splat removal strength")
    sky_threshold: str = Field(default="auto")
    dedup_distance: str = Field(default="auto", description="Based on local point density")

    # V2: Depth-inlier filtering
    ncc_confidence_threshold: float = Field(
        default=0.5, description="NCC below this → low confidence → sparse seeding"
    )
    cross_validate_depth: bool = Field(
        default=True, description="Compare PanDA vs RPG360 depth"
    )


class Stage06Config(BaseModel):
    """Stage 6: Multi-View Gaussian Optimization."""

    iterations: int = Field(default=30000)
    densify_until_iter: int = Field(default=15000)
    densify_every: int = Field(default=500)
    prune_every: int = Field(default=3000)
    l1_weight: float = Field(default=0.8)
    ssim_weight: float = Field(default=0.2)
    sh_degree: int = Field(default=3, description="Full spherical harmonics")

    # V2: ImprovedGS+ densification
    densification: Literal["igs_plus", "cdc_gs", "adc", "mcmc"] = Field(
        default="igs_plus", description="V2 default: ImprovedGS+"
    )

    # V2: ErpGS distortion-aware loss
    erp_distortion_weights: bool = Field(
        default=True, description="Enable cos(latitude) weighting"
    )
    erp_scale_flattening_loss: float = Field(
        default=0.01, description="Prevent oversized polar Gaussians"
    )
    erp_omnidirectional_neighbors: bool = Field(
        default=True, description="Tangent-plane neighbors for depth/normal reg"
    )

    # V2: 360-GeoGS D-Normal regularization
    depth_reg_weight: float = Field(
        default=0.2, description="V2: increased from 0.1 (intersection-depth is more reliable)"
    )
    d_normal_weight: float = Field(default=0.05, description="V2: depth-normal consistency loss")
    use_intersection_depth: bool = Field(
        default=True, description="V2: ray-surface intersection instead of center depth"
    )

    # V2 Optional: CDC-GS
    cdc_gs_enabled: bool = Field(default=False, description="Enable complexity-density prior")
    cdc_gs_wavelet: str = Field(default="db2", description="Daubechies-2 wavelet")

    # Checkpointing
    checkpoint_every: int = Field(
        default=5000, description="Save intermediate .ply every N iterations (0 = disabled)"
    )


class Stage07Config(BaseModel):
    """Stage 7: Occlusion Recovery & Refinement."""

    # V2: Two-phase occlusion recovery
    refine_backend: Literal["sharegs_gsdiff", "gsfix3d", "omniroam"] = Field(
        default="sharegs_gsdiff", description="V2 default"
    )
    refine_cameras: int = Field(default=36, description="Novel-view cameras")
    refine_hole_threshold: float = Field(default=0.02, description="Stop when holes < 2%")

    # ShareGS pre-pass
    sharegs_enabled: bool = Field(default=True, description="V2: lightweight gap fill before diffusion")
    sharegs_homogenization: bool = Field(default=True, description="Feature-scale guided Gaussian redistribution")
    sharegs_patch_reuse: bool = Field(default=True, description="Copy Gaussians from other viewpoints")
    sharegs_optimize_iters: int = Field(default=500, description="Quick blend optimization")

    # GS-Diff (V2 replaces GSFix3D)
    # GS-Diff inpainting backend
    gsdiff_backend: Literal["sd", "eschernet"] = Field(
        default="sd", description="Inpainting backend: 'sd' (Stable Diffusion, recommended) or 'eschernet' (multi-view, RAIL-M license)"
    )
    gsdiff_prompt: str = Field(
        default="clean indoor scene, high quality, detailed", description="Text prompt for SD inpainting"
    )
    gsdiff_lpips_threshold: float = Field(
        default=0.4, description="Exclude hallucinated pixels from training"
    )
    gsdiff_softmax_depth: bool = Field(default=True, description="Depth-prior-guided training")
    gsdiff_depth_prior: str = Field(default="marigold", description="Monocular depth model")
    refine_rounds: int = Field(
        default=2, description="V2: reduced from 3 (ShareGS pre-pass handles easy gaps)"
    )

    # OmniRoam (optional)
    trajectory_mode: str = Field(default="auto")
    tier2_weight: float = Field(default=0.20)
    upscale: str = Field(default="seedvr2")


class Stage08Config(BaseModel):
    """Stage 8: Post-Processing & Export."""

    min_opacity: float = Field(default=0.005)
    max_scale: str = Field(default="auto", description="Relative to scene bounds")

    # V2: Improved pruning
    rap_final_pass: bool = Field(default=True, description="Recovery-aware pruning")
    compact_box_culling: bool = Field(default=True, description="V2: FastGS Mahalanobis tile culling")
    compact_box_sigma: float = Field(default=3.0, description="Cull tiles outside Nσ of Gaussian extent")

    export_format: list[Literal["ply", "sog", "spz", "html"]] = Field(
        default=["ply", "sog"], description="Export formats"
    )
    extract_mesh: bool = Field(default=False, description="Poisson mesh for navigation")


class SphereForgeConfig(BaseModel):
    """Top-level SphereForge configuration."""

    data_dir: Path = Field(default=Path("data"), description="Root data directory")
    model_cache_dir: Path = Field(
        default=Path.home() / ".cache" / "sphereforge" / "models",
        description="Model weight cache directory",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")
    num_workers: int = Field(
        default=1,
        description="Parallel workers for CPU-bound stages (1 = serial). "
        "Stages 2, 4, 5 use this when > 1.",
    )

    stage01: Stage01Config = Field(default_factory=Stage01Config)
    stage02: Stage02Config = Field(default_factory=Stage02Config)
    stage03: Stage03Config = Field(default_factory=Stage03Config)
    stage04: Stage04Config = Field(default_factory=Stage04Config)
    stage05: Stage05Config = Field(default_factory=Stage05Config)
    stage06: Stage06Config = Field(default_factory=Stage06Config)
    stage07: Stage07Config = Field(default_factory=Stage07Config)
    stage08: Stage08Config = Field(default_factory=Stage08Config)
