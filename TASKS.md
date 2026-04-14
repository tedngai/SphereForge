# SphereForge — Task List

Status: TODO | IN_PROGRESS | DONE | BLOCKED

Each task is the smallest independently assignable unit. Dependencies reference task IDs that must be DONE first.

### Reuse Classification

| Tag | Meaning | Effort Multiplier |
|-----|---------|-------------------|
| **REUSE** | Code exists, drop in with minimal wrapping | ~0.2x (just wrap + test) |
| **ADAPT** | Code exists but needs extraction, refactoring, or API changes | ~0.5x (extract + refactor + test) |
| **NEW** | No code available; implement from paper/spec | ~1.0x (design + implement + test) |
| **GLUE** | Orchestration, config, logging — always new but trivial | ~0.3x (wiring only) |
| **TEST** | Unit/integration tests — always new | ~0.3x |

### License Flags

> **Project license context:** SphereForge is developed for non-commercial, copyleft use. All licenses below are acceptable for this project. Flags are kept for reference and for anyone who may want a commercial-clean fork later.

| Tag | Meaning | Status for this project |
|-----|---------|------------------------|
| **MIT** | Fully permissive — no restrictions | ✅ Clear |
| **Apache-2.0** | Fully permissive — no restrictions | ✅ Clear |
| **BSD-2** | Fully permissive — no restrictions | ✅ Clear |
| **NC-3DGS** | Inherits original 3DGS non-commercial license | ✅ Clear — non-commercial use is our use case |
| **NC-Adobe** | Adobe Research License — non-commercial research only | ✅ Clear — non-commercial use is our use case |
| **NC-RAIL** | RAIL++-M on model weights — non-commercial use of model | ✅ Clear — non-commercial use is our use case |
| **GPLv3** | Copyleft — derivative works must also be GPLv3+ | ✅ Clear — SphereForge is copyleft; can link/import directly |
| **NOLICENSE** | No license file found — all rights reserved by default | ⚠️ Action needed — contact authors for permission OR implement from paper |
| **PAPER** | No code released — implement from paper | ✅ Clear — your implementation, your license |

---

## Cross-Cutting Infrastructure (Stage 0)

| ID | Status | Description | Depends On | Reuse | Source | License | Notes |
|----|--------|-------------|------------|------|--------|---------|-------|
| T0.1 | DONE | Project skeleton: `pyproject.toml`, `src/sphereforge/__init__.py`, directory structure, `ruff`/`black`/`isort` config | — | GLUE | — | — | Creates all empty `__init__.py` files and the package layout from AGENTS.md |
| T0.2 | DONE | Pydantic config models for all stages: `Stage01Config` through `Stage08Config` with defaults from PIPELINE_DESIGN_V2.md | T0.1 | GLUE | — | — | All fields, types, and defaults must match the design doc |
| T0.3 | DONE | CLI entry point with `click`: `sphereforge process`, `sphereforge export`, `sphereforge status` | T0.1, T0.2 | GLUE | — | — | `status` command reads PROGRESS.md and reports completion % |
| T0.4 | DONE | Progress logging module: `logging_utils.py` — functions to read/write TASKS.md and PROGRESS.md, check dependencies, log completion | T0.1 | GLUE | — | — | Core of the automatic logging system |
| T0.5 | DONE | Common I/O utilities: `common/io.py` — `read_image()`, `write_image()`, `read_depth()`, `write_depth()`, `read_ply()`, `write_ply()`, `read_colmap_cameras()`, `read_colmap_images()` | T0.1 | ADAPT | SPAG-4D | MIT | Image/depth I/O patterns from SPAG-4D; PLY I/O also from SPAG-4D. Wrap into unified helpers. |
| T0.6 | DONE | COLMAP format helpers: `common/colmap_helpers.py` — parse/write `cameras.txt`, `images.txt`, `points3D.txt`; convert between quaternion and rotation matrix | T0.5 | REUSE | COLMAP scripts | BSD-2 | COLMAP ships Python read/write scripts. Adapt for our types. Needed by Stages 2, 3, 5. |
| T0.7 | DONE | Depth utility functions: `common/depth_utils.py` — `align_depth_median_ratio()`, `compute_ncc()`, `cross_validate_depth()` | T0.5 | ADAPT | SPAG-4D | MIT | SPAG-4D has depth alignment; NCC is NEW (no existing code). Used by Stages 4, 5. |
| T0.8 | DONE | Metric helpers: `common/metrics.py` — `compute_psnr()`, `compute_ssim()`, `compute_lpips()` | T0.5 | REUSE | Standard libs | — | PSNR/SSIM from torch/torchmetrics; LPIPS from `lpips` pip package. Thin wrappers. Used by Stages 6, 7. |
| T0.9 | DONE | Model weight download helper: `common/model_cache.py` — `download_if_missing()`, `get_model_path()`, configurable cache dir | T0.1 | GLUE | — | — | All model wrappers use this. Standard huggingface_hub pattern. |
| T0.10 | TODO | Dockerfile / conda environment: CUDA 12.8+, PyTorch, COLMAP CLI, Python deps | T0.1 | GLUE | — | — | Enables reproducible builds |
| T0.11 | DONE | Test framework setup: `tests/conftest.py` with synthetic ERP image fixtures, depth map fixtures, COLMAP model fixtures | T0.1 | TEST | — | — | Shared fixtures for all stage tests |
| T0.12 | TODO | Integration test harness: `tests/integration/conftest.py` — runs pipeline end-to-end on synthetic data | T0.11 | TEST | — | — | Validates full pipeline on tiny synthetic scene |

---

## Stage 1: Video Ingestion & Frame Selection

| ID | Status | Description | Depends On | Reuse | Source | License | Notes |
|----|--------|-------------|------------|------|--------|---------|-------|
| T1.1 | DONE | Frame extraction: `extract_frames()` — call FFmpeg via subprocess, configurable FPS, output to `data/frames/` with sequential naming | T0.5 | REUSE | Extract_sharpest_frame | MIT | Direct lift. Validate FFmpeg is installed; handle missing video gracefully |
| T1.2 | DONE | Laplacian sharpness scorer: `compute_sharpness()` — variance of Laplacian on luminance channel, returns float per frame | T0.5 | REUSE | Extract_sharpest_frame | MIT | Direct lift. Must handle grayscale and color input |
| T1.3 | DONE | Sharpness cache: `SharpnessCache` class — CSV-backed, reads/writes per-frame sharpness scores, skips re-computation on re-runs | T1.2 | REUSE | Extract_sharpest_frame | MIT | Direct lift. CSV columns: frame_path, sharpness, timestamp |
| T1.4 | DONE | Chunk-based frame selection: `select_sharpest_per_chunk()` — divide frames into N-sized chunks, keep sharpest per chunk, return list of selected frame paths | T1.3 | REUSE | Extract_sharpest_frame | MIT | Direct lift. Configurable chunk_size |
| T1.5 | DONE | Luminance filter: `filter_by_luminance()` — discard frames with mean luminance outside [min, max] thresholds | T0.5 | REUSE | Extract_sharpest_frame | MIT | Direct lift. Works on single frames or lists |
| T1.6 | DONE | Stage 1 orchestration: `run_stage01()` — connect T1.1→T1.5 into a single pipeline function, takes `Stage01Config`, writes selected frames to `data/frames/` | T1.1–T1.5 | GLUE | — | — | Logs progress via `logging_utils` |
| T1.7 | DONE | Stage 1 unit tests: test sharpness scoring, chunk selection, luminance filtering, cache hit/miss, end-to-end on synthetic video | T1.6 | TEST | — | — | Synthetic video = static + blurred frames |

---

## Stage 2: Equirect→Cubemap + COLMAP Prep

| ID | Status | Description | Depends On | Reuse | Source | License | Notes |
|----|--------|-------------|------------|------|--------|---------|-------|
| T2.1 | DONE | Cubemap extraction: `extract_cubemap()` — equirect→6 perspective crops, configurable FOV (default 90°) and overlap (default 15°), output per-face images | T0.5 | REUSE | Metashape_360_to_COLMAP | MIT | Direct lift. Must handle pole distortion correctly |
| T2.2 | DONE | Yaw diversification: `apply_yaw_offset()` — compute progressive yaw offset per frame group (default +30°/group), rotate extraction angles | T2.1 | REUSE | Metashape_360_to_COLMAP | MIT | Direct lift. Offset wraps at 360° |
| T2.3 | DONE | Camera intrinsics: `compute_intrinsics()` — PINHOLE model (fx, fy, cx, cy) from crop resolution, source ERP dimensions, and extraction FOV | T0.6 | REUSE | Metashape_360_to_COLMAP | MIT | Direct lift. Output as COLMAP `cameras.txt` entry |
| T2.4 | DONE | Camera extrinsics: `compute_extrinsics()` — quaternion + translation (world-to-camera) from face direction, yaw offset, and optional tracker poses | T0.6, T2.2 | REUSE | Metashape_360_to_COLMAP | MIT | Direct lift. Output as COLMAP `images.txt` entry |
| T2.5 | DONE | YOLO dynamic object masking: `generate_yolo_masks()` — run ultralytics YOLO on each crop, mask configurable classes (person, vehicle), output binary masks to `data/cubemaps/masks/` | T0.5 | REUSE | Metashape_360_to_COLMAP | MIT | Direct lift. Falls back to empty mask if YOLO unavailable |
| T2.6 | DONE | Overexposure masking: `generate_overexposure_masks()` — detect pixels above threshold (default 250), output binary mask per crop | T0.5 | REUSE | Metashape_360_to_COLMAP | MIT | Direct lift. Combines with YOLO mask (union) |
| T2.7 | DONE | COLMAP dataset writer: `write_colmap_dataset()` — write `images/`, `masks/`, `cameras.txt`, `images.txt` in COLMAP sparse model format | T0.6, T2.3, T2.4, T2.5, T2.6 | REUSE | Metashape_360_to_COLMAP | MIT | Direct lift. Validates format against COLMAP requirements |
| T2.8 | DONE | RPG360 per-face depth estimation: `estimate_face_depth()` — run Metric3D v2 (or Omnidata v2) on each cubemap face independently, return per-face depth map | T0.9, T2.1 | ADAPT | Metric3D v2 | BSD-2 | Metric3D has PyTorch Hub integration (trivially importable). Wrap as `models/metric3d.py`. RPG360 just calls this per face. |
| T2.9 | DONE | RPG360 graph-based scale optimization: `graph_optimize_scales()` — model per-face scale+shift params, solve for cross-face consistency using overlap region depth agreement | T0.7, T2.8 | ADAPT | RPG360 | ⚠️ NOLICENSE | Core algorithm in RPG360 `src/` can be extracted but config-driven with hardcoded paths. **⚠️ ACTION: Open GitHub issue requesting license, OR implement from arXiv:2509.23991 paper.** |
| T2.10 | DONE | RPG360 fallback alignment: `median_ratio_align()` — simple median-of-ratios scale+shift alignment, used when graph solve fails | T0.7 | REUSE | SPAG-4D | MIT | SPAG-4D has this. V1 approach, kept as safety net |
| T2.11 | DONE | Stage 2 orchestration: `run_stage02()` — connect T2.1→T2.10 into a single pipeline function, writes COLMAP dataset + RPG360 depth to `data/cubemaps/` | T2.1–T2.10 | GLUE | — | — | Config selects RPG360 depth on/off |
| T2.12 | DONE | Stage 2 unit tests: test cubemap extraction geometry, yaw offset logic, intrinsics/extrinsics values, YOLO mask generation, RPG360 graph optimization on synthetic depth | T2.11 | TEST | — | — | Verify intrinsics against known projection math |

---

## Stage 3: Multi-View SfM (COLMAP)

| ID | Status | Description | Depends On | Reuse | Source | License | Notes |
|----|--------|-------------|------------|------|--------|---------|-------|
| T3.1 | DONE | COLMAP feature extraction wrapper: `run_feature_extraction()` — call COLMAP CLI `feature_extractor` with RootSIFT, pass masks from Stage 2 | T0.6, T2.7 | REUSE | COLMAP CLI | BSD-2 | Thin subprocess wrapper. Validates COLMAP is installed |
| T3.2 | DONE | COLMAP feature matching wrapper: `run_feature_matching()` — call COLMAP CLI `exhaustive_matcher` or `sequential_matcher` + `vocab_tree_matcher`, configurable matcher type | T3.1 | REUSE | COLMAP CLI | BSD-2 | Thin subprocess wrapper. Sequential+vocab_tree is default |
| T3.3 | DONE | COLMAP bundle adjustment wrapper: `run_bundle_adjustment()` — call COLMAP CLI `bundle_adjuster`, fix intrinsics (refine only extrinsics + points) | T3.2 | REUSE | COLMAP CLI | BSD-2 | Thin subprocess wrapper. Known intrinsics from Stage 2 |
| T3.4 | DONE | COLMAP sparse model reader: `read_sparse_model()` — parse COLMAP output: cameras.bin, images.bin, points3D.bin into Python dicts | T0.6 | REUSE | COLMAP scripts | BSD-2 | COLMAP ships Python read/write scripts. Both text and binary format support |
| T3.5 | DONE | COLMAP dense reconstruction wrapper: `run_dense_reconstruction()` — call COLMAP CLI `patch_match_stereo` + `stereo_fusion`, optional | T3.3 | REUSE | COLMAP CLI | BSD-2 | Thin subprocess wrapper. Config-gated; only runs if `dense_reconstruction=true` |
| T3.6 | DONE | Stage 3 orchestration: `run_stage03()` — connect T3.1→T3.5, writes sparse model to `data/colmap/` | T3.1–T3.5 | GLUE | — | — | Handles COLMAP failures gracefully |
| T3.7 | DONE | Stage 3 unit tests: test CLI argument construction, sparse model reader with synthetic COLMAP output, bundle adjustment config | T3.6 | TEST | — | — | Mock COLMAP CLI calls |

---

## Stage 4: Dense Depth Estimation

| ID | Status | Description | Depends On | Reuse | Source | License | Notes |
|----|--------|-------------|------------|------|--------|---------|-------|
| T4.1 | DONE | PanDA model wrapper: `models/panda.py` — load PanDA weights, `estimate_depth()` on ERP frame, handle Mobius conformal padding, return float32 depth map | T0.9 | ADAPT | PanDA | Apache-2.0 | Clean inference scripts exist but not pip-installable. Need to wrap `run_image.py` logic into a callable class. Downloads weights on first use |
| T4.2 | DONE | PanDA scene analysis: `analyze_depth_scene()` — compute depth range (1st/99th percentile), detect sky regions (95th percentile threshold), compute orbit radius | T4.1 | ADAPT | SPAG-4D | MIT | SPAG-4D has scene analysis; adapt pattern for PanDA depth maps. Outputs dict of scene params |
| T4.3 | DONE | Depth-to-SfM scale alignment: `align_depth_to_colmap()` — sample COLMAP sparse points per view, fit scale+shift via median of ratios, with optional RPG360 depth anchor for local refinement | T0.7, T3.4, T4.1, T2.9 | ADAPT | SPAG-4D + RPG360 | MIT / ⚠️ NOLICENSE | SPAG-4D has median-ratio. RPG360 anchor integration is NEW. RPG360 depth code: **⚠️ ACTION: contact authors or implement from paper** |
| T4.4 | DONE | RPG360-only depth pipeline: `rpg360_depth_pipeline()` — run perspective model on cubemaps, graph-optimize scales, fuse back to ERP depth maps | T2.8, T2.9 | ADAPT | RPG360 | ⚠️ NOLICENSE | Composes T2.8 + T2.9 + cubemap-to-ERP fusion. **⚠️ ACTION: contact authors or implement from paper.** Alternative when PanDA unavailable |
| T4.5 | DONE | Depth model abstraction: `get_depth_estimator()` — factory function, returns appropriate estimator based on config (`panda`, `rpg360`, `da360` legacy) | T4.1, T4.4 | GLUE | — | — | Swappable model interface |
| T4.6 | DONE | Stage 4 orchestration: `run_stage04()` — connect T4.1→T4.5, writes metric depth maps to `data/depth/` | T4.1–T4.5 | GLUE | — | — | Logs per-frame depth stats |
| T4.7 | DONE | Stage 4 unit tests: test PanDA wrapper with tiny model, scene analysis on known depth, scale alignment accuracy, RPG360 fusion seamlessness | T4.6 | TEST | — | — | Mock heavy model inference |

---

## Stage 5: Initial Gaussian Seeding

| ID | Status | Description | Depends On | Reuse | Source | License | Notes |
|----|--------|-------------|------------|------|--------|---------|-------|
| T5.1 | DONE | Spherical projection: `project_to_3d()` — given ERP frame + aligned depth map, compute `position = depth * ray_direction(theta, phi)` for each pixel at configurable stride | T0.7 | REUSE | SPAG-4D | MIT | SPAG-4D converter does exactly this. Must handle ERP coordinate system correctly |
| T5.2 | DONE | Multi-view fusion: `fuse_multiview()` — project all frames' Gaussians into COLMAP coordinate system, average positions visible from multiple views, flag single-view points as lower confidence | T3.4, T5.1 | NEW | — | — | SPAG-4D does single-view only; multi-view averaging is new logic |
| T5.3 | DONE | Gaussian deduplication: `deduplicate_gaussians()` — merge Gaussians within threshold distance, weighted by confidence (view count), adaptive threshold based on local density | T5.2 | ADAPT | SPAG-4D | MIT | SPAG-4D has dedup; adapt for confidence weighting |
| T5.4 | DONE | Edge clipping: `clip_grazing_angles()` — remove Gaussians at grazing angles above configurable threshold (default 65°) | T5.2 | REUSE | SPAG-4D | MIT | Direct reuse — `scene_filter.py` |
| T5.5 | DONE | Statistical outlier pruning: `prune_outliers()` — remove points far from neighbors using k-nearest-neighbor distance statistics | T5.3 | REUSE | SPAG-4D | MIT | Direct reuse. Configurable strength (default 0.3) |
| T5.6 | DONE | Sparse region pruning: `prune_sparse_regions()` — remove isolated Gaussians not supported by neighbors within a radius | T5.5 | REUSE | SPAG-4D | MIT | Direct reuse. Configurable strength (default 0.3) |
| T5.7 | DONE | Sky removal: `remove_sky()` — remove Gaussians above auto-computed or configured sky depth threshold | T4.2, T5.2 | REUSE | SPAG-4D | MIT | Direct reuse — scene analysis sky detection |
| T5.8 | DONE | NCC confidence filtering: `compute_depth_confidence()` — cross-validate PanDA ERP depth vs RPG360 back-projected depth using NCC, mark pixels below threshold (default 0.5) as low-confidence | T0.7, T4.1, T4.4 | NEW | PFGS360 concept | NC-3DGS | PFGS360 paper describes this; implementation is straightforward NCC. No need to import PFGS360 code. Returns per-pixel confidence map |
| T5.9 | DONE | Stride assignment by confidence: `assign_stride()` — high-confidence pixels get stride=1, low-confidence get stride=4, feed into `project_to_3d()` | T5.1, T5.8 | NEW | — | — | Simple conditional logic. Reduces phantom Gaussians from bad depth |
| T5.10 | DONE | Initial attribute assignment: `assign_initial_attributes()` — color (sRGB from source), opacity (1.0 high-conf / 0.3 low-conf), scale (pixel footprint at depth), rotation (identity quaternion) | T5.2, T5.8 | ADAPT | SPAG-4D | MIT | SPAG-4D has attribute assignment; extend for confidence-based opacity |
| T5.11 | DONE | PLY writer for initial Gaussian Splat: `write_gaussian_ply()` — write positions, colors, opacities, scales, rotations in 3DGS PLY format (SH degree 0) | T0.5, T5.10 | REUSE | SPAG-4D | MIT | Direct reuse. Must match standard 3DGS PLY schema |
| T5.12 | DONE | Stage 5 orchestration: `run_stage05()` — connect T5.1→T5.11, writes initial .ply to `data/gaussians/` | T5.1–T5.11 | GLUE | — | — | Logs Gaussian count and stats |
| T5.13 | DONE | Stage 5 unit tests: test spherical projection math, fusion averaging, dedup logic, NCC filtering on synthetic depth, PLY output format validation | T5.12 | TEST | — | — | Verify PLY against 3DGS viewer |

---

## Stage 6: Multi-View Gaussian Optimization

| ID | Status | Description | Depends On | Reuse | Source | License | Notes |
|----|--------|-------------|------------|------|--------|---------|-------|
| T6.1 | DONE | ErpGS distortion-aware loss: `erp_weighted_loss()` — weight per-pixel L1+SSIM loss by `cos(latitude)` of the corresponding ERP pixel; must map cubemap crop pixels back to ERP latitude | T0.8 | NEW | ErpGS paper | PAPER | **No public code.** Implement from arXiv:2505.19883. Critical for 360 quality |
| T6.2 | DONE | ErpGS scale+flattening loss: `scale_flattening_loss()` — penalize Gaussians whose scale exceeds a latitude-dependent threshold; prevents oversized polar Gaussians | — | NEW | ErpGS paper | PAPER | **No public code.** Implement from arXiv:2505.19883. Operates on Gaussian scale parameters |
| T6.3 | DONE | ErpGS omnidirectional neighbor selection: `tangent_plane_neighbors()` — find neighbors via tangent-plane proximity instead of pixel adjacency for depth/normal regularization | — | NEW | ErpGS paper | PAPER | **No public code.** Implement from arXiv:2505.19883. Critical near ERP boundary |
| T6.4 | DONE | 360-GeoGS intersection-depth: `compute_intersection_depth()` — compute actual ray-Gaussian-surface intersection point instead of Gaussian center depth; handles large flat Gaussians correctly | — | NEW | 360-GeoGS paper | PAPER | **No public code.** Implement from arXiv:2601.02102. Requires analytical ray-ellipsoid intersection |
| T6.5 | DONE | 360-GeoGS D-Normal loss: `d_normal_loss()` — compute normals from rendered depth gradient, penalize disagreement with Gaussian's inherent normal, enforce local planarity | T6.4 | NEW | 360-GeoGS paper | PAPER | **No public code.** Implement from arXiv:2601.02102. Uses intersection-depth from T6.4 |
| T6.6 | DONE | ImprovedGS+ Edge-Aware Score: `compute_eas()` — Laplacian-based metric on rendered image to identify under-reconstructed edges; replaces gradient-threshold densification trigger | — | ADAPT | ImprovedGS+ | NC-3DGS | Code exists in `train.py` but embedded in monolithic training loop. Extract EAS logic. Must be differentiable for backprop |
| T6.7 | DONE | ImprovedGS+ Long-Axis Split: `long_axis_split()` — split Gaussian along its longest axis tangentially; place children on the surface being reconstructed instead of random offsets | — | ADAPT | ImprovedGS+ | NC-3DGS | Code exists in `train.py` but embedded in monolithic training loop. Extract LAS logic. Uses Gaussian's rotation quaternion |
| T6.8 | DONE | ImprovedGS+ Recovery-Aware Pruning: `rap_prune()` — remove near-transparent/excessively-large Gaussians but track them for recovery if PSNR drops after pruning | T0.8 | ADAPT | ImprovedGS+ | NC-3DGS | Code exists in `train.py` but embedded in monolithic training loop. Extract RAP logic. Maintains a "pruned" buffer with PSNR checkpoints |
| T6.9 | DONE | CDC-GS complexity-density prior (optional): `compute_visual_complexity()` — DWT high-frequency components as visual complexity map; `align_density_to_complexity()` — adjust Gaussian density to match | — | ADAPT | CDC-GS | NC-3DGS | Wavelet module in `wavelets/` dir is extractable but coupled to custom rasterizer. Config-gated; adds ~5% overhead |
| T6.10 | DONE | Depth regularization with intersection-depth: `depth_reg_loss()` — L1 between rendered intersection-depth and PanDA depth, weighted by `cos(latitude)`, with configurable weight (default 0.2) | T6.1, T6.4 | NEW | — | — | Combines ErpGS weights (T6.1) + GeoGS intersection depth (T6.4). No single source; compose from both |
| T6.11 | DONE | Training loop: `train_gaussians()` — main optimization loop with configurable iterations, densification schedule (EAS every 500 iters), RAP pruning schedule (every 3000 iters), SH expansion (degree 0→3 at 7500 iters) | T6.1–T6.10 | ADAPT | LichtFeld-Studio + ImprovedGS+ | GPLv3 / NC-3DGS | Can import/link LichtFeld-Studio directly (copyleft compatible). ImprovedGS+ training loop can be adapted for densification logic. Reads initial Gaussians from Stage 5, crops from Stage 2, poses from Stage 3 |
| T6.12 | DONE | Stage 6 orchestration: `run_stage06()` — connect training loop, write optimized .ply with SH to `data/optimized/` | T6.11 | GLUE | — | — | Logs training curve (PSNR, Gaussian count) |
| T6.13 | DONE | Stage 6 unit tests: test EAS on known edge patterns, LAS split geometry, RAP prune/recover cycle, distortion weight values at known latitudes, intersection-depth accuracy on synthetic Gaussians | T6.12 | TEST | — | — | Most complex test suite in the project |

---

## Stage 7: Occlusion Recovery & Refinement

| ID | Status | Description | Depends On | Reuse | Source | License | Notes |
|----|--------|-------------|------------|------|--------|---------|-------|
| T7.1 | DONE | Novel-view camera rig generation: `generate_novel_cameras()` — place 36 cameras (12 directions × 3 distances) around scene center and along viewing paths, configurable count | T3.4 | NEW | — | — | Simple geometry. Uses COLMAP sparse model bounds to set distances |
| T7.2 | DONE | Hole detection via alpha threshold: `detect_holes()` — render splat from each novel camera, identify pixels where alpha < threshold (default 0.5), return hole mask per camera | T6.12 | ADAPT | GSFix3D | Apache-2.0 / NC-3DGS | GSFix3D has alpha-threshold hole detection; adapt pattern. Requires differentiable rasterizer from Stage 6 |
| T7.3 | DONE | Gap classification: `classify_gaps()` — categorize holes as behind-foreground / at-boundary / missing-geometry using depth discontinuity analysis | T7.2 | REUSE | SPAG-4D | MIT | SPAG-4D's `gap_analysis.py` does this directly |
| T7.4 | DONE | ShareGS Gaussian homogenization: `homogenize_gaussians()` — for small gaps, clone nearby Gaussians and adjust position/scale/color to fill gap, guided by feature similarity and scale consistency | T7.3 | NEW | ShareGS paper | PAPER | **No public code.** Implement from Pattern Recognition 2025 paper. Conceptually straightforward: clone + adjust nearby Gaussians |
| T7.5 | DONE | ShareGS scene patch reuse: `reuse_patches()` — for gaps matching visible patches from other viewpoints, copy Gaussians from those viewpoints and transform into gap using camera poses | T3.4, T7.3 | NEW | ShareGS paper | PAPER | **No public code.** Implement from paper. Uses COLMAP poses for transformation |
| T7.6 | DONE | ShareGS quick optimization: `blend_fill()` — run 500 iterations of differentiable rendering to blend new Gaussians with surrounding scene | T7.4, T7.5 | GLUE | — | — | Same training loop as Stage 6 but short (500 iters) |
| T7.7 | DONE | GS-Diff EscherNet model wrapper: `models/eschernet.py` — load multi-view diffusion model, `inpaint_holes()` on rendered images, return inpainted RGB per novel view | T0.9 | ADAPT | EscherNet | NC-RAIL | Code exists as research scripts; modifies diffusers internals directly. Needs significant wrapping. **Model weights: CreativeML Open RAIL-M (non-commercial).** Downloads weights on first use |
| T7.8 | DONE | GS-Diff LPIPS thresholding: `filter_hallucinations()` — compute LPIPS between inpainted and rendered images; exclude pixels where LPIPS > threshold (default 0.4) from training | T0.8, T7.7 | NEW | GS-Diff paper | PAPER | **No public code.** Conceptually simple: compute LPIPS, mask above threshold. Core GS-Diff innovation |
| T7.9 | DONE | GS-Diff softmax-depth loss: `softmax_depth_loss()` — use Marigold depth prior with softmax-scaled rendering weights; reduces floaters from inconsistent inpainted depth | T0.9 | NEW | GS-Diff paper | PAPER | **No public code.** Implement from arXiv:2504.01960. Marigold wrapper in `models/marigold.py`. **Marigold weights: RAIL++-M (non-commercial)** |
| T7.10 | DONE | GS-Diff distillation: `distill_inpaint()` — render current splat from inpainted viewpoints, compute L1+SSIM loss (excluding LPIPS-thresholded pixels), backpropagate to update Gaussians | T7.7, T7.8, T7.9 | ADAPT | GSFix3D | Apache-2.0 / NC-3DGS | GSFix3D has 3D lifting logic; adapt to add LPIPS filtering. Similar to Stage 6 training but on pseudo-views |
| T7.11 | DONE | Iterative hole-filling loop: `fill_holes_iterative()` — repeat hole detection → ShareGS fill → GS-Diff fill until hole coverage < 2% or max 2 rounds | T7.2, T7.6, T7.10 | GLUE | — | — | Checks convergence after each round |
| T7.12 | DONE | OmniRoam trajectory fill (optional): `omniroam_fill()` — gap-directed trajectory gen, 81-frame ERP video gen, SeedVR2 upscale, multi-tier distillation with tier-2 weight 0.20 | T7.3 | ADAPT | OmniRoam | NC-Adobe | Complex multi-stage pipeline. **Adobe Research License = non-commercial only.** Requires 20GB+ VRAM. Config-gated |
| T7.13 | DONE | Stage 7 orchestration: `run_stage07()` — connect T7.1→T7.12, writes refined .ply to `data/refined/` | T7.1–T7.12 | GLUE | — | — | Default: ShareGS+GS-Diff; OmniRoam optional |
| T7.14 | DONE | Stage 7 unit tests: test novel camera placement, hole detection on synthetic splat with known gap, LPIPS filtering threshold, ShareGS homogenization geometry | T7.13 | TEST | — | — | Synthetic splat with intentional holes |

---

## Stage 8: Post-Processing & Export

| ID | Status | Description | Depends On | Reuse | Source | License | Notes |
|----|--------|-------------|------------|------|--------|---------|-------|
| T8.1 | DONE | ImprovedGS+ RAP final pruning: `final_rap_prune()` — remove redundant Gaussians from Stage 7's occlusion recovery, track and recover if PSNR drops | T6.8, T7.13 | ADAPT | ImprovedGS+ | NC-3DGS | Reuses RAP logic from T6.8 (already extracted). Just different config for final pass |
| T8.2 | DONE | FastGS Compact Box culling: `compact_box_cull()` — Mahalanobis-distance-based Gaussian-tile pair pruning; remove tile assignments where Gaussian's 3σ extent barely overlaps the tile | — | ADAPT | FastGS | MIT / NC-3DGS | Mahalanobis culling exists in FastGS `train.py` but embedded in training loop. Extract the culling logic. Reduces file size |
| T8.3 | DONE | PLY export: `export_ply()` — write final Gaussian Splat in standard 3DGS PLY format with full SH coefficients | T0.5 | REUSE | SPAG-4D | MIT | Direct reuse. Must validate against 3DGS viewers |
| T8.4 | DONE | SOG export: `export_sog()` — structured-organized Gaussians format for streaming | T8.3 | ADAPT | LichtFeld-Studio | GPLv3 | Can link/import directly (copyleft compatible). SOG export from LichtFeld-Studio C++; either call via Python bindings or subprocess |
| T8.5 | DONE | SPZ export: `export_spz()` — streaming-optimized format | T8.3 | ADAPT | LichtFeld-Studio | GPLv3 | Can link/import directly (copyleft compatible). Same approach as T8.4 |
| T8.6 | DONE | HTML viewer generation: `generate_html_viewer()` — self-contained HTML with embedded GaussianSplats3D viewer + final .ply encoded as base64 or linked | T8.3 | REUSE | LichtFeld-Studio | GPLv3 | Viewer JS can be extracted from CDN (GaussianSplats3D is Apache-2.0). HTML template is new |
| T8.7 | DONE | Mesh extraction (optional): `extract_navigation_mesh()` — Poisson reconstruction or marching cubes from Gaussian positions, output as OBJ/GLB | T0.5 | REUSE | Open3D / PyMeshLab | MIT / GPL | Standard library calls. Config-gated; for collision/wayfinding |
| T8.8 | DONE | Stage 8 orchestration: `run_stage08()` — connect T8.1→T8.7, writes final outputs to `data/export/` | T8.1–T8.7 | GLUE | — | — | Config selects export formats |
| T8.9 | DONE | Stage 8 unit tests: test RAP final pruning preserves quality, Compact Box culling reduces size without visual loss, PLY format validation, HTML viewer renders | T8.8 | TEST | — | — | Validate PLY with plyfile reader |

---

## Summary

### By Stage

| Stage | Tasks | REUSE | ADAPT | NEW | GLUE | TEST | First Dependency |
|-------|-------|-------|-------|-----|------|------|-----------------|
| 0: Infrastructure | 12 | 2 | 2 | 0 | 5 | 3 | None |
| 1: Frame Selection | 7 | 5 | 0 | 0 | 1 | 1 | T0.5 |
| 2: Cubemap + COLMAP Prep | 12 | 7 | 2 | 0 | 1 | 1 | T0.5, T0.6, T0.7 |
| 3: COLMAP SfM | 7 | 4 | 0 | 0 | 1 | 1 | T0.6, T2.7 |
| 4: Depth Estimation | 7 | 0 | 4 | 0 | 2 | 1 | T0.7, T0.9, T2.9, T3.4 |
| 5: Gaussian Seeding | 13 | 5 | 2 | 3 | 1 | 1 | T0.5, T0.7, T3.4, T4.1 |
| 6: Optimization | 13 | 0 | 4 | 5 | 1 | 1 | T0.8, T2.1, T3.4 |
| 7: Occlusion Recovery | 14 | 1 | 3 | 4 | 2 | 1 | T0.8, T0.9, T3.4, T6.12 |
| 8: Export | 9 | 2 | 3 | 0 | 1 | 1 | T6.8, T7.13 |
| **Total** | **94** | **26** | **20** | **12** | **15** | **11** | |

Note: Total increased from 80 to 94 because the Reuse column made some implicit subtasks explicit (e.g., T0.7 now splits NCC as NEW vs alignment as ADAPT).

### By Reuse Category

| Category | Count | % | Effort Factor | Effective Work |
|----------|-------|---|---------------|---------------|
| REUSE (drop in) | 26 | 28% | 0.2x | ~5 tasks |
| ADAPT (extract/refactor) | 20 | 21% | 0.5x | ~10 tasks |
| NEW (from paper/spec) | 12 | 13% | 1.0x | ~12 tasks |
| GLUE (orchestration) | 15 | 16% | 0.3x | ~5 tasks |
| TEST (tests only) | 11 | 12% | 0.3x | ~3 tasks |
| **Total** | **94** | | | **~35 effective tasks** |

With reuse, SphereForge's 94 tasks represent roughly **35 tasks worth of from-scratch effort**.

### By License

| License | Tasks | Status for this project | Notes |
|---------|-------|------------------------|-------|
| MIT | 23 | ✅ Clear | SPAG-4D core, Extract_sharpest_frame, Metashape_360_to_COLMAP, DA360 |
| Apache-2.0 | 4 | ✅ Clear | PanDA, GSFix3D code |
| BSD-2-Clause | 7 | ✅ Clear | Metric3D v2, COLMAP |
| PAPER (no code) | 12 | ✅ Clear | Your implementation = your license. ErpGS, 360-GeoGS, ShareGS, GS-Diff concepts |
| NC-3DGS (inherited) | 13 | ✅ Clear | ImprovedGS+, FastGS, CDC-GS, PFGS360. Non-commercial = our use case |
| NC-RAIL / CreativeML RAIL-M | 3 | ✅ Clear | EscherNet weights, Marigold weights. Non-commercial = our use case |
| NC-Adobe | 1 | ✅ Clear | OmniRoam. Non-commercial research = our use case |
| GPLv3 | 3 | ✅ Clear | LichtFeld-Studio. SphereForge is copyleft; can link/import directly |
| ⚠️ NOLICENSE | 3 | ⚠️ **Action needed** | RPG360 (T2.9, T4.3, T4.4). Contact authors OR implement from paper |
| N/A (GLUE/TEST) | 26 | ✅ Clear | Infrastructure, orchestration, tests — all original code |

**Total blockers:** 3 tasks (T2.9, T4.3, T4.4) need RPG360 author contact or paper-based reimplementation. All other tasks are clear for non-commercial copyleft use.

### Paper-Only Components (highest implementation risk)

These 12 tasks have no public code and must be implemented from the papers:

| Task | Paper | Key Algorithm | Risk |
|------|-------|---------------|------|
| T6.1 | ErpGS (arXiv:2505.19883) | `cos(latitude)` weighted loss on cubemap pixels | Low — math is straightforward |
| T6.2 | ErpGS | Scale+flattening loss for polar Gaussians | Low — direct scale parameter operation |
| T6.3 | ErpGS | Tangent-plane neighbor selection | Medium — requires spatial data structure |
| T6.4 | 360-GeoGS (arXiv:2601.02102) | Ray-ellipsoid intersection depth | Medium — analytical math is well-known but integration with 3DGS rasterizer is non-trivial |
| T6.5 | 360-GeoGS | D-Normal loss from depth gradients | Medium — depends on T6.4; gradient computation is standard |
| T5.8 | PFGS360 (arXiv:2603.23324) | NCC cross-validation of depth maps | Low — standard NCC computation |
| T5.9 | New | Stride assignment by confidence | Low — trivial conditional |
| T7.4 | ShareGS (PatRec 2025) | Gaussian homogenization | Medium — clone+adjust nearby Gaussians; paper describes approach but not all implementation details |
| T7.5 | ShareGS | Scene patch reuse with pose transform | Medium — requires careful pose-based Gaussian copying |
| T7.8 | GS-Diff (arXiv:2504.01960) | LPIPS thresholding mask | Low — compute LPIPS, threshold, create mask |
| T7.9 | GS-Diff | Softmax-depth loss with Marigold prior | Medium — softmax weighting + Marigold depth integration |

### Critical Path (longest dependency chain)

T0.1 → T0.5 → T1.1 → T1.6 → T2.1 → T2.8 → T2.9 → T4.3 → T5.2 → T5.10 → T5.11 → T5.12 → T6.11 → T6.12 → T7.11 → T7.13 → T8.8

This is the minimum sequence that must be completed for a full pipeline run. All other tasks can be parallelized off this path.

### Recommended Parallelization Strategy

**Wave 1 (no external deps):** T0.1–T0.12 (infrastructure) — all can run in parallel
**Wave 2 (needs Wave 1):** T1.1–T1.7, T2.1–T2.7, T6.1–T6.5, T6.6–T6.9 — Stages 1+2 core + Stage 6 paper-only tasks (no code deps)
**Wave 3 (needs Wave 2):** T2.8–T2.9, T3.1–T3.7, T4.1–T4.7, T6.10–T6.13 — RPG360 depth + COLMAP + PanDA + training loop
**Wave 4 (needs Wave 3):** T5.1–T5.13, T7.1–T7.14 — Seeding + Occlusion recovery
**Wave 5 (needs Wave 4):** T8.1–T8.9 — Final export
