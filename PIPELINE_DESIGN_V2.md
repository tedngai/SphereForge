# Panoramic Gaussian Splatting Pipeline Design V2

## Overview

A multi-stage pipeline that transforms 360° camera footage into high-quality 3D Gaussian Splat scenes of large, complex spaces. V2 incorporates the latest advances (2024-2026) in 360 Gaussian Splatting to improve both speed and quality over V1.

### V1 → V2 Changelog

| Stage | V1 | V2 | Why |
|-------|----|----|-----|
| 2. Cubemap + COLMAP Prep | YOLO masking only | + RPG360 graph-optimized cubemap depth | Better depth scale alignment than median-ratio; training-free |
| 4. Dense Depth Estimation | DA360 | PanDA (primary) / RPG360 (alt) | ~30% lower depth error; Mobius conformal padding eliminates boundary artifacts |
| 5. Gaussian Seeding | SPAG spherical projection | + Depth-Inlier-Aware filtering (PFGS360) | Rejects low-confidence depth points before they become bad Gaussians |
| 6. Multi-View Optimization | ADC densification | ImprovedGS+ (EAS+LAS+RAP) | ~50% fewer Gaussians, SOTA PSNR, 2x faster training |
| 6. Loss Function | L1+SSIM, flat depth reg | + ErpGS distortion-aware weights + 360-GeoGS D-Normal reg | Fixes polar distortion, 2x better depth accuracy |
| 6. Densification | ADC/MCMC/IGS+ | ImprovedGS+ default; CDC-GS optional | Complexity-density prior prevents wasted Gaussians |
| 7. Occlusion Recovery | GSFix3D only | ShareGS pre-pass + GS-Diff (replaces GSFix3D) | Faster gap pre-fill; LPIPS thresholding prevents hallucination training |
| 8. Export | Standard | + FastGS Compact Box pruning | Mahalanobis-distance tile culling for smaller files |

### Sources Table

| Stage | Primary Source | What It Borrows |
|-------|---------------|-----------------|
| 1. Video Ingestion & Frame Selection | Extract_sharpest_frame | Laplacian sharpness scoring, chunk-based selection |
| 2. Equirect→Cubemap + COLMAP Prep | Metashape_360_to_COLMAP_plane + RPG360 | Camera intrinsics/extrinsics, YOLO masking, yaw diversification, graph-optimized depth alignment |
| 3. Multi-View SfM (COLMAP) | Standard COLMAP | Sparse reconstruction, bundle adjustment |
| 4. Dense Depth Estimation | PanDA / RPG360 | Mobius conformal padding, perspective foundation model fusion |
| 5. Initial Gaussian Seeding | SPAG-4D + PFGS360 | Spherical projection, edge clipping, depth-inlier filtering |
| 6. Multi-View Gaussian Optimization | ImprovedGS+ / ErpGS / 360-GeoGS | View-consistent densification, distortion-aware loss, D-Normal regularization |
| 7. Occlusion Recovery & Refinement | ShareGS + GS-Diff | Gaussian homogenization, LPIPS-thresholded diffusion inpainting |
| 8. Post-Processing & Export | ImprovedGS+ + FastGS + LichtFeld-Studio | RAP pruning, Compact Box culling, PLY/SOG/SPZ export |

---

## Stage 1: Video Ingestion & Frame Selection

**Source:** Extract_sharpest_frame

**Problem:** 360° camera footage often has motion blur, especially from handheld or stabilizer-mounted capture. Blurry frames degrade every downstream step — depth estimation, SfM matching, and final Gaussian quality.

**Process:**

1. **Frame extraction** — Use FFmpeg to decompose input video(s) into individual frames at target FPS (e.g., 5 fps for walking-speed capture).
2. **Sharpness scoring** — For each frame, compute the variance of the Laplacian on the luminance channel. Cache results in a CSV metadata file for re-runs.
3. **Chunk-based selection** — Divide frames into chunks of N (default: 30 frames, ~6 seconds at 5fps). Within each chunk, keep only the sharpest frame. This naturally samples across the entire trajectory while discarding blur.
4. **Optional dark/overexposure filter** — Discard frames with mean luminance outside configurable thresholds.

**V2 Note:** No changes to this stage. Laplacian sharpness scoring remains the best practical approach for blur detection in this context.

**Output:** A curated set of sharp equirectangular frames with timing metadata.

**Config:**
```
input_fps = 5              # extraction framerate
chunk_size = 30            # frames per chunk
min_luminance = 10          # discard dark frames
max_luminance = 245         # discard blown-out frames
```

---

## Stage 2: Equirect→Cubemap + COLMAP Prep

**Source:** Metashape_360_to_COLMAP_plane (primary), Equirect2Cube (overlap logic), RPG360 (depth alignment)

**Problem:** COLMAP and Gaussian Splatting training require perspective (rectilinear) images with proper camera intrinsics and extrinsics. Equirectangular images cannot be used directly — the distortion breaks feature matching and projection assumptions.

**Process:**

1. **Cubemap extraction** — For each selected equirectangular frame, extract N perspective crops (default: 6 — front, right, back, left, top, bottom). Each crop uses 90° FOV with configurable overlap (default: 15°) to ensure feature overlap between adjacent faces.
2. **Yaw diversification** — Apply a progressive yaw offset per frame group (e.g., +30° per group of 6 faces). This rotates the extraction angle so that features that fall on cubemap seams in one frame fall on face centers in another, dramatically improving SfM feature coverage.
3. **Camera intrinsics computation** — For each crop, compute the PINHOLE camera model parameters (fx, fy, cx, cy) based on the crop resolution, source equirectangular dimensions, and extraction FOV.
4. **Camera extrinsics computation** — Derive the quaternion + translation (world-to-camera) for each crop based on the face direction, yaw offset, and any known camera poses (if available from a separate tracker).
5. **Dynamic object masking** — Optionally run YOLO segmentation on each crop to mask out dynamic objects (people, vehicles). This prevents the optimizer from wasting capacity on transient content.
6. **Overexposure masking** — Detect blown-out white pixels (threshold configurable) and generate binary masks to exclude them from training.

### V2 Addition: RPG360 Graph-Optimized Depth Alignment

7. **Per-face perspective depth estimation** — Run a perspective foundation model (Metric3D v2 or Omnidata v2) on each cubemap face independently. This provides metric depth per face that is locally consistent.
8. **Graph-based scale optimization** — Instead of the V1 median-ratio approach, use RPG360's graph optimization: model per-face scale parameters and solve for 3D structural consistency across adjacent faces. Adjacent faces share overlap regions — their depth must agree where they overlap. The graph optimizer enforces this with a per-face scale + shift parameterization, producing globally consistent cubemap depth without a 360-specific model.
9. **Foundation model hot-swap** — Because the depth model runs on perspective crops (not the full ERP), any new perspective depth model can be dropped in without retraining. This future-proofs the pipeline.

**Why RPG360 over V1's median-ratio alignment:** The V1 approach aligns monocular depth to COLMAP sparse points using a single global scale+shift per frame. This works on average but fails at depth discontinuities (walls meeting floors, objects at different distances). RPG360's per-face scale parameters with cross-face consistency constraints produce a piecewise-linear alignment that handles discontinuities much better. It also doesn't require a 360-specific model, so you benefit from ongoing improvements to perspective depth models.

**Output:** COLMAP-format dataset: `images/`, `masks/`, `cameras.txt`, `images.txt` + per-face metric depth maps (graph-aligned).

**Config:**
```
n_faces = 6                # cubemap faces per frame
fov = 90                   # degrees per face
overlap = 15                # degrees of overlap between faces
yaw_offset_step = 30       # degrees per frame group
crop_resolution = 1024     # pixels per crop side
generate_masks = true       # YOLO dynamic object masking
mask_classes = ["person", "vehicle"]
overexposure_threshold = 250

# V2: RPG360 depth alignment
rpg360_depth_model = "metric3d_v2"   # or "omnidata_v2"
rpg360_graph_optimize = true          # per-face scale + cross-face consistency
rpg360_fallback = "median_ratio"     # if graph solve fails, fall back to V1 approach
```

---

## Stage 3: Multi-View SfM (COLMAP)

**Source:** Standard COLMAP (used by both Metashape→COLMAP and LichtFeld-Studio)

**Problem:** Even with depth estimation per frame, we need globally consistent camera poses and a sparse point cloud to register all viewpoints into a shared coordinate system. Per-frame depth maps alone drift and disagree across views.

**Process:**

1. **Feature extraction** — SIFT/RootSIFT features on all perspective crops (using the masks from Stage 2 to exclude dynamic objects).
2. **Feature matching** — Sequential matching (for temporally adjacent frames) + vocabulary-tree matching (for loop closure across distant frames). The overlap and yaw diversification from Stage 2 ensure sufficient feature matches across face boundaries.
3. **Bundle adjustment** — Sparse reconstruction with known intrinsics from Stage 2 (refine only extrinsics and point positions). This produces globally consistent camera poses.
4. **Dense reconstruction (optional)** — COLMAP patch-match stereo to produce a dense point cloud. This can supplement or validate the depth maps from Stage 4.

### V2 Note: Future Option — PFGS360 SCA-PE (Pose-Free Alternative)

PFGS360 (arXiv:2603.23324) can estimate camera poses directly from 360 video using spherical consistency — eliminating COLMAP entirely for video inputs. It outperforms even pose-aware OmniGS (35.77 vs 31.35 PSNR). However, it is currently only validated on indoor 360 video sequences. For outdoor or challenging scenes, COLMAP remains more robust. This is flagged as a future replacement path once PFGS360 matures.

**Output:** COLMAP sparse model: camera poses, sparse point cloud, feature matches.

**Config:**
```
feature_type = "root_sift"
matcher_type = "sequential+vocabulary_tree"
refine_intrinsics = false    # intrinsics are known from Stage 2
dense_reconstruction = true  # optional COLMAP dense point cloud

# V2: future option (not yet enabled)
# pose_estimator = "colmap"  # "colmap" or "pfgs360_scape"
```

---

## Stage 4: Dense Depth Estimation

**Source:** PanDA (primary), RPG360 (alternative)

**Problem:** SfM produces sparse point clouds — not enough density for direct Gaussian seeding. We need dense, per-pixel depth for each viewpoint. Standard monocular depth models produce relative depth with seam artifacts at the 360° boundary.

### V2 Change: PanDA replaces DA360

**Why PanDA over DA360:**
- **Mobius conformal padding** — DA360 uses circular padding at the ERP boundary, which eliminates the left-right seam but still introduces distortion near the boundary. PanDA's Mobius conformal padding preserves angles and shapes across the seam, producing geometrically correct depth at the wrap-around.
- **~30% lower relative depth error** — Trained on large-scale unlabeled panoramic data (Matterport3D, Stanford2D3D, etc.), PanDA achieves significantly better zero-shot depth across diverse indoor/outdoor scenes.
- **Better boundary handling** — The conformal padding means depth discontinuities near the ERP boundary (e.g., a wall that wraps from the right edge to the left) are handled correctly.

**Process:**

1. **PanDA depth estimation** — Run PanDA on each selected equirectangular frame. PanDA's Mobius conformal padding eliminates boundary artifacts without requiring cubemap conversion for depth estimation.
2. **Scene analysis (per SPAG-4D)** — For each depth map:
   - Auto-compute depth range (1st/99th percentile)
   - Detect sky regions (depth above 95th percentile threshold)
   - Compute recommended orbit radius for viewer defaults
3. **Depth-to-SfM scale alignment** — Monocular depth is relative, not metric. Align each frame's depth map to the COLMAP sparse point cloud:
   - Sample COLMAP 3D points that project into each view
   - Fit a scale + shift transform (median of ratios) to map PanDA depth → metric depth
   - If RPG360 depth was computed in Stage 2, use it as an additional alignment signal — RPG360's per-face metric depth provides local anchors that improve alignment at depth discontinuities
   - This produces metrically consistent depth across all frames

### V2 Alternative: RPG360-Only Depth (Training-Free)

If GPU memory is limited or PanDA model weights are unavailable, RPG360 provides a training-free alternative:
- Run perspective foundation models on cubemap faces (already generated in Stage 2)
- Graph-optimize per-face scale alignment (already done in Stage 2 Step 8)
- Fuse cubemap depths back into ERP depth maps
- Advantages: No 360-specific model needed, can hot-swap any perspective depth model
- Disadvantages: Cubemap face boundaries may introduce subtle depth seams (mitigated by overlap regions)

**Why depth estimation still matters (even with COLMAP dense):** DA360/PanDA handles textureless surfaces (walls, ceilings, floors) that COLMAP stereo matching fails on. In indoor/large-space scenarios, these flat surfaces dominate. PanDA also runs in ~2s per frame vs. minutes for COLMAP dense reconstruction.

**Output:** Metric depth arrays (H×W float32) per frame, aligned to COLMAP coordinate system.

**Config:**
```
# V2: PanDA (primary)
depth_model = "panda"        # "panda" (V2 default), "rpg360" (alt), "da360" (V1 legacy)
scale_alignment = "median_ratio_with_rpg360_anchor"  # V2: uses RPG360 depth as local anchor
sky_threshold = "auto"       # percentile or fixed value
depth_min = "auto"           # clip near geometry
depth_max = "auto"           # clip far geometry

# RPG360-only fallback
rpg360_perspective_model = "metric3d_v2"  # only used if depth_model = "rpg360"
```

---

## Stage 5: Initial Gaussian Seeding

**Source:** SPAG-4D (SPAG converter + scene_filter) + PFGS360 (depth-inlier filtering)

**Problem:** We need an initial set of 3D Gaussians to start optimization from. Random initialization wastes optimization cycles. Seeding from depth maps gives a strong starting point that already resembles the scene.

**Process:**

1. **Spherical projection** — For each equirectangular frame with its aligned depth map, project pixels into 3D space:
   ```
   position = depth * ray_direction(theta, phi)
   ```
   Each pixel becomes one Gaussian candidate (at stride=1) or every Nth pixel (stride=2, 4 for speed).

2. **Multi-view fusion** — Project all frames' Gaussians into the COLMAP coordinate system using the aligned camera poses. Points visible from multiple views get averaged; points visible from only one view are kept but flagged as lower confidence.

3. **Deduplication** — Gaussians within a threshold distance (based on local density) are merged, weighted by confidence (number of observing views).

4. **Scene filtering (from SPAG-4D's scene_filter):**
   - **Edge clipping** — Remove Gaussians at grazing angles (behind objects, configurable `grazing_angle` threshold)
   - **Outlier pruning** — Statistical outlier removal (points far from their neighbors)
   - **Sparse region pruning** — Remove isolated Gaussians not supported by neighbors
   - **Sky removal** — Remove Gaussians above the sky depth threshold

### V2 Addition: Depth-Inlier-Aware Filtering (from PFGS360)

5. **NCC confidence filtering** — Before seeding, evaluate each depth pixel's reliability using Normalized Cross-Correlation (NCC) similarity between the PanDA depth prediction and the RPG360 cubemap-fused depth (if available). Points where the two depth estimates disagree are unreliable — they likely correspond to textureless regions, specular surfaces, or depth model failures.
   - Compute NCC between PanDA ERP depth and RPG360-back-projected ERP depth
   - Mark pixels with NCC < threshold (default: 0.5) as low-confidence
   - Low-confidence pixels get stride=4 (sparse seeding) instead of stride=1
   - This prevents bad depth pixels from creating misplaced Gaussians that the optimizer then has to clean up

6. **Initial attribute assignment:**
   - **Color** — sRGB from source pixel
   - **Opacity** — 1.0 for high-confidence (multi-view, high-NCC) Gaussians, 0.3 for single-view/low-NCC
   - **Scale** — Derived from pixel footprint at that depth (closer = smaller Gaussians, farther = larger)
   - **Rotation** — Identity quaternion (optimized later)

**Why depth-inlier filtering matters:** V1 seeds every pixel at uniform stride, treating all depth values equally. But depth models are unreliable at specular surfaces (windows, mirrors), textureless regions (blank walls at oblique angles), and moving objects that slipped through YOLO masking. By cross-validating two independent depth estimates, we catch these failures before they become Gaussians. The optimizer then spends its budget on real structure instead of cleaning up phantom Gaussians.

**Output:** Initial Gaussian Splat (.ply) with positions, colors, opacities, scales, rotations.

**Config:**
```
stride = 1                  # V2 change: full resolution by default (ImprovedGS+ handles density better)
stride_low_confidence = 4   # V2: sparse seeding for unreliable depth pixels
grazing_angle = 65           # edge clipping threshold (90=off)
outlier_pruning = 0.3        # floater removal strength
sparse_pruning = 0.3         # isolated splat removal strength
sky_threshold = "auto"
dedup_distance = "auto"      # based on local point density

# V2: Depth-inlier filtering
ncc_confidence_threshold = 0.5   # NCC below this → low confidence → sparse seeding
cross_validate_depth = true      # compare PanDA vs RPG360 depth
```

---

## Stage 6: Multi-View Gaussian Optimization

**Source:** ImprovedGS+ (densification), ErpGS (distortion-aware loss), 360-GeoGS (D-Normal regularization), LichtFeld-Studio (3DGS training pipeline)

**Problem:** The seeded Gaussians from Stage 5 are a rough approximation — they have wrong scales, suboptimal opacities, no SH color representation, and gaps between views. Multi-view optimization refines them into a high-quality splat.

### V2 Changes (3 major improvements)

#### 6.1: ImprovedGS+ Densification (replaces ADC)

V1 used ADC (Adaptive Density Control) which suffers from:
- Over-densifying in already well-reconstructed regions (wasted Gaussians)
- Splitting along random directions (misaligned children)
- Pruning without recovery awareness (over-pruning that can't be undone)

ImprovedGS+ (arXiv:2508.12313) replaces ADC with three components:

- **Edge-Aware Score (EAS)** — Uses Laplacian of the rendered image to identify *where* densification is needed. This is more targeted than the gradient-threshold approach in ADC, which triggers densification based on view-averaged gradient magnitude. EAS specifically detects edges and under-reconstructed boundaries.

- **Long-Axis Split (LAS)** — When a Gaussian is split, children are placed along the parent's longest axis (tangential to the surface), not at random offsets. This means children naturally lie on the surface being reconstructed, instead of potentially floating off into space. Dramatically reduces the number of "floater" Gaussians.

- **Recovery-Aware Pruning (RAP)** — Tracks pruned Gaussians and allows recovery if their removal caused rendering quality to drop. This prevents over-pruning, especially during later training iterations when ADC tends to be too aggressive.

**Result:** ~50% fewer Gaussians with SOTA PSNR (28.19 on Mip-NeRF360). Training time from 14.2 min → 6.7 min.

#### 6.2: ErpGS Distortion-Aware Loss Weighting

V1 trained on cubemap crops with uniform loss weighting across all pixels. This is wrong for 360° content because:

- Pixels near the ERP equator represent more solid angle than pixels near the poles
- When rendered back to ERP, equatorial errors are more visually noticeable
- Without correction, the optimizer over-invests in polar regions (where each pixel covers less area) and under-invests in equatorial regions

ErpGS (arXiv:2505.19883) adds:
- **Latitude-dependent loss weighting** — Weight each training pixel's loss by `cos(latitude)` to account for the varying solid angle per pixel in ERP space. This ensures the optimizer allocates effort proportional to the visual impact of each region.
- **Scale + flattening loss** — Penalize Gaussians that become excessively large near the poles (a known 360° artifact where the optimizer compensates for sparse training views with oversized Gaussians).
- **Omnidirectional neighbor selection** — For depth and normal regularization, select neighbors via tangent-plane proximity instead of pixel adjacency. Pixel adjacency breaks at the ERP boundary and produces wrong neighbor pairs.

#### 6.3: 360-GeoGS D-Normal Regularization (replaces simple depth L1)

V1 used `depth_reg_weight = 0.1` with simple L1 between rendered depth and PanDA depth. This has two problems:

- **Center-depth vs intersection-depth** — The "rendered depth" in standard 3DGS uses the Gaussian center depth, which is correct for small Gaussians but wrong for large flat ones (walls, ceilings). A large Gaussian spanning a wall has its center behind the wall surface; the rendered depth is therefore systematically wrong.
- **No normal consistency** — Depth L1 doesn't enforce that surfaces are locally planar. Gaussians on a wall can "bubble" slightly without the depth loss catching it.

360-GeoGS (arXiv:2601.02102) replaces this with:
- **Intersection-depth calculation** — Compute the actual ray-Gaussian-surface intersection point instead of using the center depth. This is geometrically correct for Gaussians of any size.
- **D-Normal loss** — Compute normals from the rendered depth gradient and penalize disagreement between the depth-derived normal and the Gaussian's inherent normal. This enforces local planarity on walls, ceilings, and floors.
- **2x better depth accuracy** than Splatter-360 on HM3D benchmark.

---

**Full Process (V2):**

1. **Training setup** — Use the COLMAP camera poses (Stage 3) and perspective crops (Stage 2) as the training dataset. Apply masks to exclude dynamic objects and overexposed regions.

2. **Differentiable rasterization** — Render Gaussians from each training viewpoint using differentiable splat rasterization. Compute loss against ground-truth images:
   - **L1 loss** — Pixel-wise color error, weighted by `cos(latitude)` of the corresponding ERP pixel
   - **SSIM loss** — Structural similarity (perceptual quality), weighted by `cos(latitude)`
   - **Combined** — `L1 + λ * (1 - SSIM)`, typically λ = 0.2

3. **ImprovedGS+ densification** (replaces ADC):
   - **EAS-triggered split** — When Edge-Aware Score exceeds threshold, split the Gaussian along its longest axis (LAS)
   - **Clone** — Small Gaussians in under-reconstructed regions are duplicated (same as V1)
   - **RAP pruning** — Near-transparent or excessively large Gaussians are removed, but tracked for potential recovery if rendering quality drops

4. **SH color refinement** — After initial RGB convergence, expand spherical harmonics from degree 0 (DC/color) to degree 3 (view-dependent effects like specular highlights).

5. **Regularization (V2 enhanced):**
   - **D-Normal regularization** — Intersection-depth normal consistency (360-GeoGS)
   - **Scale + flattening regularization** — Prevent oversized Gaussians at poles (ErpGS)
   - **Opacity regularization** — Prevent Gaussians from becoming transparent "fog"
   - **ErpGS distortion-aware weighting** — All regularization losses are weighted by `cos(latitude)` for correct ERP geometry

6. **Iterate** — Train for N iterations (default: 30,000), with EAS densification every M iterations (default: 500) and RAP pruning every K iterations (default: 3,000).

### V2 Optional: CDC-GS Complexity-Density Prior

CDC-GS (NeurIPS 2025) adds a loss-agnostic visual complexity prior on top of ImprovedGS+. It uses discrete wavelet transform (DWT) high-frequency components to estimate the visual complexity of each region, then aligns Gaussian density with complexity. This prevents:
- Over-densifying plain surfaces (walls, ceilings)
- Under-densifying texture-rich regions (shelves, machinery, signage)

Enable if the scene has a mix of textureless and detail-rich areas. Adds ~5% training time overhead.

**Output:** Optimized Gaussian Splat with full SH coefficients, ~50% fewer Gaussians than V1.

**Config:**
```
iterations = 30000
densify_until_iter = 15000
densify_every = 500
prune_every = 3000
l1_weight = 0.8
ssim_weight = 0.2
sh_degree = 3               # full spherical harmonics

# V2: ImprovedGS+ densification
densification = "igs_plus"   # V2 default: "igs_plus" (was "adc" in V1)
                                # Options: "igs_plus", "cdc_gs", "adc" (V1 legacy), "mcmc"

# V2: ErpGS distortion-aware loss
erp_distortion_weights = true   # enable cos(latitude) weighting
erp_scale_flattening_loss = 0.01  # prevent oversized polar Gaussians
erp_omnidirectional_neighbors = true  # tangent-plane neighbors for depth/normal reg

# V2: 360-GeoGS D-Normal regularization
depth_reg_weight = 0.2          # V2: increased from 0.1 (intersection-depth is more reliable)
d_normal_weight = 0.05         # V2: new — depth-normal consistency loss
use_intersection_depth = true   # V2: ray-surface intersection instead of center depth

# V2 Optional: CDC-GS
cdc_gs_enabled = false         # enable complexity-density prior
cdc_gs_wavelet = "db2"         # Daubechies-2 wavelet for complexity estimation
```

---

## Stage 7: Occlusion Recovery & Refinement

**Source:** ShareGS (lightweight pre-pass) + GS-Diff (diffusion inpainting)

**Problem:** Even after multi-view optimization, 3D Gaussians have structural holes — regions that were occluded from every training viewpoint (behind furniture, around corners, inside rooms not captured). These holes become visible when the viewer moves to novel viewpoints.

### V2 Changes

V1 used GSFix3D exclusively. V2 introduces a two-phase approach that is faster and more reliable:

1. **ShareGS lightweight pre-pass** — Fill obvious gaps quickly using Gaussian homogenization (no diffusion model needed)
2. **GS-Diff diffusion inpainting** — Fill remaining complex holes with LPIPS-guarded diffusion (prevents hallucination training, which was GSFix3D's main weakness)

**Process:**

### Phase 7A: Hole Detection (unchanged from V1)

1. **Camera rig generation** — Place 36 novel-view cameras (12 directions × 3 distances) around the scene center and along likely viewing paths.
2. **Render + threshold** — Render the current splat from each camera. Identify pixels where alpha < threshold (default: 0.5) — these are holes.
3. **Gap classification** — Classify holes by angular direction (gap_analysis.py logic):
   - **Behind foreground** — Occluded by nearby objects
   - **At boundaries** — At depth discontinuities
   - **Missing geometry** — Entire regions with no Gaussians at all

### Phase 7B: ShareGS Lightweight Pre-Pass (V2 New)

4. **Gaussian homogenization** — For small gaps (missing geometry, boundary gaps), use ShareGS's feature-and-scale-guided homogenization to redistribute existing nearby Gaussians into the gap. This works by:
   - Identifying Gaussians near the gap boundary
   - Cloning them and adjusting position/scale/color to fill the gap
   - Guiding the cloning by local feature similarity and scale consistency
5. **Scene patch reuse** — For gaps that match patches visible from other viewpoints, directly copy Gaussians from those viewpoints and transform them into the gap using the camera poses.
6. **Quick optimization** — Run 500 iterations of differentiable rendering to blend the new Gaussians with the surrounding scene.

**Why this pre-pass:** ShareGS fills ~60-70% of typical gaps without needing a diffusion model at all. It's fast (~1 minute) and produces geometrically correct fill because it reuses real Gaussians. This dramatically reduces the number of expensive diffusion rounds needed in Phase 7C.

### Phase 7C: GS-Diff Diffusion Inpainting (V2, replaces GSFix3D)

7. **GS-Diff view augmentation** — For remaining holes after the ShareGS pre-pass, use GS-Diff's iterative approach:
   - Render the current splat from each novel-view camera
   - Use a multi-view diffusion model (EscherNet) to inpaint hole regions
   - **LPIPS-thresholded loss** — This is the key improvement over GSFix3D. GSFix3D trains on all inpainted pixels equally, including hallucinated content. GS-Diff computes LPIPS between the inpainted image and the rendered image; if the LPIPS exceeds a threshold, those pixels are excluded from training. This prevents the optimizer from fitting to diffusion hallucinations.
   - **Softmax-depth loss** — Uses monocular depth priors (Marigold) with softmax-scaled rendering weights. Reduces floaters caused by inconsistent depth in inpainted regions.
8. **Distillation** — Project the inpainted images back into 3D via differentiable rendering:
   - Render the current splat from each inpainted viewpoint
   - Compute L1 + SSIM loss between rendered and inpainted images (excluding LPIPS-thresholded pixels)
   - Backpropagate to update Gaussian positions, colors, opacities, and scales
9. **Iterate** — Repeat steps 2-8 until hole coverage drops below 2%, or for a maximum of 2 rounds (V2: reduced from 3 because ShareGS pre-pass already handles most gaps).

### Phase 7C-alt: OmniRoam Trajectory-Coherent Fill (Optional, unchanged from V1)

For highest quality with 48GB+ VRAM, the V1 OmniRoam path remains available:
- Gap-directed trajectory generation
- 81-frame 480×960 ERP video generation
- SeedVR2 upscale
- Multi-tier distillation with tier-2 weight 0.20

**Why GS-Diff over GSFix3D:**
- **LPIPS thresholding** prevents the #1 failure mode of GSFix3D: the optimizer fitting to hallucinated diffusion content, creating "ghost" artifacts when viewed from angles the diffusion model didn't anticipate
- **Softmax-depth loss** reduces floaters — a common GSFix3D artifact where inpainted content spawns Gaussians at wrong depths
- **Fewer rounds needed** — ShareGS pre-pass handles easy gaps, so GS-Diff only runs on genuinely difficult holes

**Output:** Refined Gaussian Splat with filled occlusion holes.

**Config:**
```
# V2: Two-phase occlusion recovery
refine_backend = "sharegs_gsdiff"   # V2 default; "gsfix3d" (V1), "omniroam" (V1 alt)
refine_cameras = 36
refine_hole_threshold = 0.02        # stop when holes < 2%

# ShareGS pre-pass
sharegs_enabled = true              # V2: lightweight gap fill before diffusion
sharegs_homogenization = true       # feature-scale guided Gaussian redistribution
sharegs_patch_reuse = true          # copy Gaussians from other viewpoints
sharegs_optimize_iters = 500        # quick blend optimization

# GS-Diff (V2 replaces GSFix3D)
gsdiff_model = "eschernet"          # multi-view diffusion model
gsdiff_lpips_threshold = 0.4        # exclude hallucinated pixels from training
gsdiff_softmax_depth = true         # depth-prior-guided training
gsdiff_depth_prior = "marigold"     # monocular depth model for depth loss
refine_rounds = 2                   # V2: reduced from 3 (ShareGS pre-pass handles easy gaps)

# OmniRoam (optional, unchanged from V1)
# refine_backend = "omniroam"
# trajectory_mode = "auto"
# tier2_weight = 0.20
# upscale = "seedvr2"
```

---

## Stage 8: Post-Processing & Export

**Source:** ImprovedGS+ (RAP) + FastGS (Compact Box) + LichtFeld-Studio (export formats)

**Process:**

1. **ImprovedGS+ Recovery-Aware Pruning** — Run a final RAP pass to remove any Gaussians that became redundant during Stage 7's occlusion recovery. RAP tracks the quality impact of each removal and recovers Gaussians if PSNR drops, preventing over-aggressive final pruning.

2. **FastGS Compact Box culling** — During export, use FastGS's Mahalanobis-distance-based Gaussian-tile pair pruning. This removes Gaussian-to-tile assignments where the Gaussian contributes negligibly (its 3σ extent barely overlaps the tile). This doesn't remove Gaussians — it removes *rendering work*, producing faster-loading splat files with no visible quality loss.

3. **Compression (optional)** — Export to SOG (structured-organized Gaussians) or SPZ format for streaming.

4. **Standalone viewer** — Generate a self-contained HTML file with embedded GaussianSplats3D viewer (from LichtFeld-Studio).

5. **Mesh extraction (optional)** — Extract a navigation mesh for collision/wayfinding using marching cubes or Poisson reconstruction.

**Output:** Final Gaussian Splat in PLY/SOG/SPZ format + optional HTML viewer.

**Config:**
```
# V2: Improved pruning
min_opacity = 0.005
max_scale = "auto"             # relative to scene bounds
rap_final_pass = true          # V2: recovery-aware pruning
compact_box_culling = true     # V2: FastGS Mahalanobis tile culling
compact_box_sigma = 3.0       # cull tiles outside 3σ of Gaussian extent

export_format = ["ply", "sog"] # "ply", "sog", "spz", "html"
extract_mesh = false           # Poisson mesh for navigation
```

---

## Data Flow Diagram (V2)

```
360° Video (MP4)
     │
     ▼
┌─────────────────────┐
│ Stage 1: Frame       │  Extract_sharpest_frame logic
│ Selection            │  → Sharpest frame per chunk
└─────────┬───────────┘
          │ Selected equirect frames
          ▼
┌─────────────────────┐
│ Stage 2: Cubemap    │  Metashape→COLMAP + Equirect2Cube
│ Extraction +        │  → Perspective crops + COLMAP format
│ COLMAP Prep         │  → Masks (YOLO + overexposure)
│ [V2] + RPG360       │  → V2: Graph-aligned per-face metric depth
│   graph depth       │
└─────────┬───────────┘
          │ COLMAP dataset + RPG360 depth maps
          ▼
┌─────────────────────┐
│ Stage 3: COLMAP     │  Sparse SfM reconstruction
│ SfM                 │  → Camera poses + sparse points
└─────────┬───────────┘
          │ Camera poses    ┌──────────────────────┐
          ▼                 │ Stage 4: PanDA Depth  │
┌─────────────────────┐    │ Estimation [V2]       │
│ Stage 4: Dense      │◄───┘ → Metric depth maps
│ Depth Estimation     │     → Aligned to COLMAP + RPG360 anchor
│ [V2] PanDA/RPG360   │
└─────────┬───────────┘
          │ Depth maps + camera poses
          ▼
┌─────────────────────┐
│ Stage 5: Gaussian   │  SPAG spherical projection
│ Seeding             │  + multi-view fusion + filtering
│ [V2] + NCC depth-   │  → V2: Depth-inlier filtering (PanDA vs RPG360)
│   inlier filtering  │
└─────────┬───────────┘
          │ Initial Gaussians
          ▼
┌─────────────────────┐
│ Stage 6: Multi-View │  ImprovedGS+ (EAS+LAS+RAP)
│ Optimization         │  + ErpGS distortion-aware loss
│ [V2] ImprovedGS+    │  + 360-GeoGS D-Normal regularization
│   ErpGS weights     │  + PanDA depth regularization
│   D-Normal reg      │
└─────────┬───────────┘
          │ Optimized Gaussians (with holes, ~50% fewer than V1)
          ▼
┌─────────────────────┐
│ Stage 7: Occlusion  │  V2: ShareGS pre-pass (lightweight)
│ Recovery             │  → GS-Diff LPIPS-guarded diffusion
│ [V2] ShareGS +      │  → Fewer diffusion rounds needed
│   GS-Diff           │
└─────────┬───────────┘
          │ Refined Gaussians (holes filled)
          ▼
┌─────────────────────┐
│ Stage 8: Post-Proc  │  V2: RAP final pruning
│ & Export             │  + FastGS Compact Box culling
│ [V2] RAP + Compact  │  → PLY / SOG / SPZ / HTML
│   Box               │
└─────────────────────┘
```

---

## Key Innovations Over V1

### V1 Innovations (preserved)

1. **Depth-seeded multi-view optimization** — SPAG-4D seeds from one view; LichtFeld trains from scratch on COLMAP points. We seed from depth maps across all views, then optimize. Better initialization = faster convergence + better geometry.

2. **Scale-aligned depth supervision** — Depth is aligned to COLMAP's metric scale, then used as a regularization signal during 3DGS training. Prevents the splat from collapsing or inflating.

3. **Yaw-diversified cubemap extraction** — Rotating the extraction angle per frame group ensures features don't consistently fall on cubemap seams, improving SfM quality.

4. **Dynamic object masking** — YOLO removes people/vehicles from training, preventing ghost artifacts and wasted optimizer capacity.

### V2 Innovations (new)

5. **ImprovedGS+ EAS+LAS+RAP densification** — Edge-Aware Score targets densification at actual under-reconstructed edges (not just high-gradient regions). Long-Axis Split places children on the surface being reconstructed. Recovery-Aware Pruning prevents over-pruning. Result: ~50% fewer Gaussians, 2x faster training, SOTA quality.

6. **ErpGS distortion-aware training** — Latitude-dependent loss weighting corrects the fundamental mismatch between cubemap training pixels and their visual importance in ERP space. Prevents over-investment in polar regions and the "oversized polar Gaussians" artifact.

7. **360-GeoGS D-Normal + intersection-depth regularization** — Ray-surface intersection depth (instead of center depth) correctly handles large flat Gaussians on walls/ceilings. D-Normal loss enforces local planarity, eliminating "bubbling" artifacts on flat surfaces.

8. **PanDA conformal-padding depth** — Mobius conformal padding preserves geometry at the ERP boundary, eliminating the subtle depth errors that circular padding (DA360) introduces at the wrap-around seam.

9. **RPG360 graph-optimized depth alignment** — Per-face scale parameters with cross-face consistency constraints replace the single global median-ratio alignment. Handles depth discontinuities correctly and future-proofs the pipeline (any new perspective depth model drops in).

10. **Depth-inlier-aware seeding** — Cross-validating PanDA and RPG360 depth estimates identifies unreliable depth pixels before they become misplaced Gaussians. Reduces the "phantom Gaussian" problem that wastes optimizer iterations.

11. **Two-phase occlusion recovery (ShareGS + GS-Diff)** — ShareGS's lightweight homogenization fills ~60-70% of gaps without a diffusion model. GS-Diff's LPIPS-thresholded diffusion fills the remaining complex holes while preventing hallucination training (GSFix3D's main failure mode).

12. **FastGS Compact Box export culling** — Removes negligible Gaussian-tile assignments during export, producing faster-loading splat files with no visible quality change.

---

## Implementation Notes

### Dependencies

| Component | Source | Key Dependencies |
|-----------|--------|-----------------|
| Frame selection | Extract_sharpest_frame | OpenCV, NumPy |
| Cubemap extraction | Metashape→COLMAP | OpenCV, NumPy, ultralytics (YOLO) |
| RPG360 depth alignment | RPG360 | PyTorch, Metric3D v2 / Omnidata v2 |
| SfM | COLMAP | COLMAP (CLI or Python bindings) |
| Depth estimation | PanDA | PyTorch, PanDA model weights |
| Depth cross-validation | PFGS360 logic | NumPy, SciPy |
| Gaussian seeding | SPAG-4D + PFGS360 | NumPy |
| 3DGS optimization | ImprovedGS+ / LichtFeld-Studio | CUDA 12.8+, C++23 |
| Distortion-aware loss | ErpGS | PyTorch (added to 3DGS training loop) |
| D-Normal regularization | 360-GeoGS | PyTorch (added to 3DGS training loop) |
| Lightweight gap fill | ShareGS | PyTorch, NumPy |
| Diffusion inpainting | GS-Diff | Diffusers, EscherNet weights, Marigold |
| Export | ImprovedGS+ + FastGS | plyfile |

### Hardware Requirements

| Stage | VRAM | Notes |
|-------|------|-------|
| 1-2 | <1 GB | CPU-bound (2 base); RPG360 adds ~2-3 GB for perspective depth |
| 3 | 4-8 GB | COLMAP GPU mode |
| 4 | 2-3 GB | PanDA inference (same as DA360) |
| 5 | <1 GB | NumPy operations |
| 6 | 6-12 GB | 3DGS training (ImprovedGS+ uses ~50% less VRAM than V1 ADC) |
| 7a (ShareGS) | 2-4 GB | Lightweight — no diffusion model |
| 7b (GS-Diff) | 12-16 GB | Diffusion model (reduced from 16 GB GSFix3D due to fewer rounds) |
| 7b (OmniRoam) | 48 GB | Video generation + upscaling (unchanged from V1) |
| 8 | <1 GB | CPU-bound |

### Estimated Runtime (per 100 frames, RTX 4090)

| Stage | V1 Time | V2 Time | Improvement |
|-------|---------|---------|-------------|
| 1. Frame selection | ~2 min | ~2 min | No change |
| 2. Cubemap extraction | ~5 min | ~8 min | +3 min (RPG360 depth per face) |
| 3. COLMAP SfM | ~15-30 min | ~15-30 min | No change |
| 4. PanDA depth | ~5 min | ~5 min | No change (PanDA ≈ DA360 speed) |
| 5. Gaussian seeding | ~1 min | ~2 min | +1 min (NCC cross-validation) |
| 6. Multi-view optimization | ~20-40 min | ~10-20 min | ~2x faster (ImprovedGS+ EAS+LAS) |
| 7a. ShareGS pre-pass | — | ~1 min | New (was 0) |
| 7b. GS-Diff refinement | ~15 min (3×5) | ~10 min (2×5) | Fewer rounds (ShareGS pre-fill) |
| 8. Export | <1 min | <1 min | No change |
| **Total** | **~50-90 min** | **~55-80 min** | **~15% faster overall; ~50% fewer Gaussians** |

**Note:** V2 adds ~5 min to Stages 2+5 (RPG360 depth + NCC validation) but saves ~15 min in Stage 6 (ImprovedGS+) and ~5 min in Stage 7 (fewer diffusion rounds). Net: slightly faster overall, with dramatically better quality and ~50% smaller output files.

---

## What Makes This Pipeline Work for Large Complex Spaces

- **Multi-view coverage** — Walking through a space with a 360° camera naturally captures overlapping viewpoints. The yaw diversification ensures nothing falls in cubemap seams.
- **Depth from all angles** — PanDA provides dense depth even on textureless walls/ceilings/floors where COLMAP stereo fails. Mobius conformal padding handles the ERP boundary correctly.
- **COLMAP global consistency** — Locks all viewpoints into a shared coordinate system so depth maps agree across frames.
- **RPG360 graph-aligned depth** — Per-face scale optimization handles depth discontinuities (walls meeting floors, near/far transitions) that a single global alignment misses.
- **Depth-inlier filtering** — Cross-validation prevents unreliable depth from seeding phantom Gaussians that waste optimizer capacity.
- **ImprovedGS+ densification** — Targeted edge-aware splits + surface-aligned child placement = no wasted Gaussians. Recovery-aware pruning = no over-pruning.
- **Distortion-aware training** — Cos(latitude) weighting ensures the optimizer invests effort proportional to visual impact in ERP space, not pixel count.
- **D-Normal geometry enforcement** — Intersection-depth + normal consistency keeps walls flat and edges sharp, even for large Gaussians.
- **Two-phase hole filling** — ShareGS handles most gaps quickly; GS-Diff with LPIPS thresholding fills complex holes without hallucination artifacts.
- **Dynamic object removal** — People walking through the scene are masked out, preventing ghost artifacts.
- **Compact export** — Compact Box culling removes negligible tile assignments for faster loading without quality loss.

---

## Future Considerations

### Short-term (implement when code/models available)

- **PFGS360 SCA-PE** — Replace COLMAP for 360 video inputs. Eliminates Stages 2-3 for video workflows (~20-35 min saved). Needs outdoor validation first.
- **CDC-GS complexity-density prior** — Add as optional Stage 6 enhancement for scenes with mixed texture/textureless regions. Minimal overhead, better Gaussian density distribution.
- **360-GeoGS SphereCNN initialization** — Use the feed-forward SphereCNN + FiLM modulation as an alternative to Stage 5 seeding. Predicts all GS parameters at 512×1024 in a single forward pass.

### Medium-term (monitor, evaluate when mature)

- **Splatter-360 end-to-end** — Currently indoor-only but rapidly improving. Could replace Stages 2-6 for indoor scenes with a single forward pass. Monitor for outdoor generalization.
- **Seam360GS** — Dual-fisheye camera model eliminates stitching seams from real 360 cameras (Insta360, Ricoh Theta). If your footage comes from dual-fisheye cameras, this could replace the equirectangular input assumption entirely.

### Long-term (architectural changes)

- **SPaGS exact spherical AABB** — Replace cubemap rendering with ray-casting using exact axis-aligned bounding boxes for spherical images. Eliminates the need for cubemap conversion during rendering (but not during training, since COLMAP still needs perspective images).
- **Full end-to-end 360 GS** — When feed-forward models (Splatter-360, 360-GeoGS) generalize to outdoor/unbounded scenes, the entire staged pipeline could be replaced by a single model forward pass + short fine-tuning.
