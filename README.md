# SphereForge

Transform 360° camera footage into high-quality 3D Gaussian Splat scenes.

SphereForge is an 8-stage pipeline that takes equirectangular (360°) video or images and produces optimized 3D Gaussian Splat files ready for viewing and streaming. It integrates the latest research in panoramic depth estimation, distortion-aware optimization, and multi-view hole filling.

## Pipeline Overview

```
Video/ERP Images
       │
  ┌────▼────┐
  │ Stage 1 │  Frame Selection — extract sharpest frames, filter by luminance
  └────┬────┘
       │
  ┌────▼────┐
  │ Stage 2 │  Cubemap Prep — ERP→cubemap, YOLO masking, COLMAP dataset
  └────┬────┘
       │
  ┌────▼────┐
  │ Stage 3 │  SfM — COLMAP feature extraction, matching, bundle adjustment
  └────┬────┘
       │
  ┌────▼────┐
  │ Stage 4 │  Depth Estimation — DAP (ERP-native) or RPG360 depth alignment
  └────┬────┘
       │
  ┌────▼────┐
  │ Stage 5 │  Gaussian Seeding — project to 3D, fuse, prune, write PLY
  └────┬────┘
       │
  ┌────▼────┐
  │ Stage 6 │  Optimization — ErpGS loss, 360-GeoGS reg, ImprovedGS+ densify
  └────┬────┘
       │
  ┌────▼────┐
  │ Stage 7 │  Occlusion Recovery — ShareGS fill + SD/EscherNet inpainting
  └────┬────┘
       │
  ┌────▼────┐
  │ Stage 8 │  Export — final pruning, PLY/SOG/SPZ/HTML output
  └────┬────┘
       │
  Final 3DGS Scene
```

## Key Features

- **ERP-native depth**: Uses [DAP (Depth Any Panoramas)](https://github.com/Insta360-Research-Team/DAP) for distortion-aware equirectangular depth estimation — no cubemap conversion needed for depth
- **Distortion-aware optimization**: ErpGS `cos(latitude)` weighted loss eliminates polar artifacts in 360° scenes
- **360-GeoGS regularization**: Ray-ellipsoid intersection depth + D-Normal loss for geometric consistency
- **ImprovedGS+ densification**: Edge-Aware Score triggers + Long-Axis Split + Recovery-Aware Pruning
- **Two-phase occlusion recovery**: ShareGS (Gaussian homogenization) fills small gaps, then Stable Diffusion inpainting fills remaining holes with LPIPS hallucination filtering
- **Multiple export formats**: Standard 3DGS PLY, SOG (structured streaming), SPZ (Morton-ordered + delta-encoded), and self-contained HTML viewer

## Installation

```bash
# Core pipeline
pip install -e .

# With depth estimation models
pip install -e ".[depth]"

# With gsplat rasterizer (recommended for training)
pip install -e ".[rasterizer]"

# With inpainting support
pip install -e ".[occlusion]"

# With YOLO dynamic object masking
pip install -e ".[yolo]"

# Everything
pip install -e ".[all]"

# Development
pip install -e ".[dev]"
```

### External Dependencies

- **COLMAP**: Required for Stage 3 (SfM). Install from [colmap.github.io](https://colmap.github.io/)
- **FFmpeg**: Required for Stage 1 (video ingestion). Usually pre-installed or `apt install ffmpeg`
- **CUDA GPU**: Required for training (Stage 6) and depth estimation (Stage 4)

## Quick Start

```bash
# Process a 360° video end-to-end
sphereforge process input_video.mp4 --output ./output

# Process a directory of ERP images
sphereforge process ./erp_frames/ --output ./output

# Export to specific formats
sphereforge export ./output/optimized/ --format ply sog html

# Check pipeline progress
sphereforge status
```

## Configuration

Each stage has sensible defaults, but all parameters can be overridden via YAML config:

```bash
sphereforge process input.mp4 --config my_config.yaml
```

Example config:

```yaml
stage01:
  input_fps: 5
  chunk_size: 30

stage04:
  depth_model: dap       # DAP for ERP-native depth
  max_depth: 10.0

stage06:
  iterations: 30000
  erp_distortion_weights: true
  densification: igs_plus

stage07:
  gsdiff_backend: sd      # Stable Diffusion inpainting
  gsdiff_prompt: "clean indoor scene, high quality"

stage08:
  export_format:
    - ply
    - html
```

## Project Structure

```
src/sphereforge/
├── cli.py                          # Click CLI entry point
├── config.py                       # Pydantic config models for all stages
├── logging_utils.py                # Progress tracking
├── common/
│   ├── io.py                       # Image/depth/PLY/COLMAP I/O
│   ├── colmap_helpers.py           # COLMAP text/binary parsers
│   ├── depth_utils.py              # Depth alignment, NCC, fusion
│   ├── metrics.py                  # PSNR, SSIM, LPIPS
│   └── model_cache.py             # Model weight download/cache
├── models/
│   ├── dap_model.py               # DAP (Depth Any Panoramas)
│   ├── depth_anything_v2.py       # Depth Anything V2
│   └── metric3d.py                # Metric3D v2
└── stages/
    ├── stage01_frames/            # Video ingestion & frame selection
    ├── stage02_cubemap/           # ERP→cubemap + COLMAP prep
    ├── stage03_sfm/               # COLMAP SfM wrappers
    ├── stage04_depth/             # Dense depth estimation
    ├── stage05_seeding/           # Initial Gaussian seeding
    ├── stage06_optimization/      # Multi-view Gaussian optimization
    ├── stage07_occlusion/         # Occlusion recovery & refinement
    └── stage08_export/            # Post-processing & export
```

## Research Credits

SphereForge integrates techniques from the following papers:

| Component | Paper | Source |
|-----------|-------|--------|
| DAP depth | [Depth Any Panoramas (CVPR 2026)](https://arxiv.org/abs/2512.16913) | [GitHub](https://github.com/Insta360-Research-Team/DAP) |
| ErpGS loss | [ErpGS (2025)](https://arxiv.org/abs/2505.19883) | Implemented from paper |
| 360-GeoGS reg | [360-GeoGS (2025)](https://arxiv.org/abs/2601.02102) | Implemented from paper |
| ImprovedGS+ | [ImprovedGS+ (2024)](https://arxiv.org/abs/2508.12313) | Adapted from code |
| ShareGS fill | [ShareGS (Pattern Recognition 2025)](https://doi.org/10.1016/j.patcog.2025.111573) | Implemented from paper |
| GS-Diff | [GS-Diff (2025)](https://arxiv.org/abs/2504.01960) | Implemented from paper |
| RPG360 depth | [RPG360 (2024)](https://arxiv.org/abs/2509.23991) | Adapted from code |
| gsplat rasterizer | [gsplat (2024)](https://github.com/nerfstudio-project/gsplat) | Direct use |
| FastGS culling | [FastGS (2024)](https://arxiv.org/abs/2408.14210) | Adapted from code |
| CDC-GS prior | [CDC-GS (2024)](https://arxiv.org/abs/2409.15266) | Adapted from code |

## License

GNU General Public License v3.0 or later (GPLv3+). See [LICENSE](LICENSE) for details.

This project incorporates code and model weights under various licenses:

- **MIT/Apache-2.0/BSD-2**: Core utilities and some model code — no restrictions
- **NC-3DGS**: ImprovedGS+, FastGS, CDC-GS inherit the original 3DGS non-commercial license
- **CreativeML RAIL-M**: EscherNet and Stable Diffusion weights — non-commercial use
- **GPLv3**: LichtFeld-Studio SOG/SPZ export — called as separate process

For commercial use, contact the respective rights holders or replace NC components with alternatives (e.g., gsplat for the INRIA 3DGS rasterizer).

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run only fast tests (skip GPU/slow)
pytest tests/ -v -m "not slow and not gpu"

# Lint
ruff check src/
black --check src/
```
