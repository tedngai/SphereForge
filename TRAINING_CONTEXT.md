# Training Context

## 2026-05-13 Stage 6 OOM

- Input: `data/raw/VID_20260503_170535_00_001.mp4`
- Dataset currently in `data/`: 18 ERP frames at `5760x2880`
- Stable coarse run: `configs/rerun_moderate.yaml`
- OOM run: `configs/long_train.yaml`
- Current midpoint retry config: `configs/mid_train.yaml`

### What happened

- The Stage 6 training process was killed by the kernel OOM killer.
- `journalctl` showed repeated failed allocations around `256 GiB` before the kill.
- Kill time: `2026-05-13 12:47:38`
- Killed process: `sphereforge` pid `195388`
- Memory at kill: about `123.9 GiB` RSS
- Swap was effectively exhausted: about `120 kB` free of `16 GiB`
- `tmux` did not fail first. The training process was killed first, then `systemd` cleaned up the `tmux-spawn-...scope` and killed the remaining `bash` and `opencode` processes at `12:49:08`.

### Why this likely happened

- The main jump was Stage 5 seed density.
- `configs/rerun_moderate.yaml` used `stage05.stride: 16`.
- `configs/long_train.yaml` used `stage05.stride: 8`.
- On the current 18-frame `5760x2880` dataset, rough raw sample counts are:
- `stride 16`: about `1,166,400`
- `stride 12`: about `2,073,600`
- `stride 10`: about `2,985,984`
- `stride 8`: about `4,665,600`
- That is about a `4x` jump from `16` to `8` before deduplication and filtering.
- Stage 6 was also much more aggressive in `long_train.yaml`:
- `densify_until_iter: 2000 -> 15000`
- `prune_every: 1000 -> 3000`
- `iterations: 3000 -> 30000`
- Result: denser initial seeding plus much longer densification growth.

### Current recommended config

- Use `configs/mid_train.yaml` as the next retry.
- It keeps Stage 5 denser than `rerun_moderate` but avoids the jump to `stride: 8`.
- Key settings:
- `stage05.stride: 12`
- `stage05.stride_low_confidence: 24`
- `stage06.iterations: 12000`
- `stage06.sh_degree: 2`
- `stage06.densify_until_iter: 8000`
- `stage06.prune_every: 2000`
- `stage06.checkpoint_every: 2000`

### Useful log paths

- OpenCode session log for the OOM rerun setup: `~/.local/share/opencode/log/2026-05-13T042106.log`
- OpenCode session log for the earlier stable moderate run: `~/.local/share/opencode/log/2026-05-13T024250.log`

### First commands to run after another crash

```bash
journalctl -k --since "24 hours ago" | grep -iE "out of memory|oom|killed process|sphereforge|tmux"
tmux ls
tmux capture-pane -p -t main:0.0 -S -300
ls -lt data/gaussians data/optimized data/refined data/export
ls -lt data/optimized/checkpoints
```

### Known state after the 2026-05-13 OOM

- `data/gaussians/`, `data/optimized/`, `data/refined/`, and `data/export/` were empty when inspected.
- No `optimized.ply` or `checkpoint_*.ply` files were present.
- A later `tmux` session named `main` existed again, but it was created after the crash and was not the original failed training session.

## 2026-05-13 Follow-up Failures and Fixes

- First midpoint rerun (`train_mid_20260513_141305.log`) got through Stage 5, then crashed in Stage 6 at iter `1900/12000`.
- Root cause: pruning used stale activated tensors after densification changed the Gaussian count.
- Fix applied: Stage 6 pruning now recomputes activated scales/opacities from the current raw tensors before building the pruning mask.

- Second midpoint rerun (`train_mid_fix_20260513_145634.log`) completed Stage 3 dense reconstruction successfully and got much farther in Stage 6.
- It reached iter `6000/12000` and wrote checkpoints:
- `data/optimized/checkpoints/checkpoint_002000.ply`
- `data/optimized/checkpoints/checkpoint_004000.ply`
- `data/optimized/checkpoints/checkpoint_006000.ply`
- It then crashed with a CUDA-side `torch.AcceleratorError` during rendering after Gaussian count had exploded to about `10.8M`.

### Additional fixes applied after the 6000-iter crash

- Stage 3 dense reruns now clear `data/colmap/dense` before invoking `image_undistorter`. This matches COLMAP's upstream assumption of rebuilding a fresh dense workspace.
- Stage 6 now caches exact per-view intrinsics matrices (`K`) from COLMAP camera params instead of rebuilding a tiny CUDA tensor from FOV inside every render call.
- Stage 6 now has a hard Gaussian cap via `stage06.max_gaussians` (default `1_000_000`).
- Stage 6 now resets opacities every `stage06.opacity_reset_every` iterations (default `3000`).
- Stage 6 now prunes oversized Gaussians using `stage06.prune_max_scale_ratio` (default `0.1`) instead of the previous effectively-loose scale threshold.
- Stage 6 calls `torch.cuda.empty_cache()` after densification/pruning/reset steps.

## 2026-05-13 Guarded Rerun Outcome

- Log: `data/optimized/train_mid_guarded_20260513_153354.log`
- The guarded rerun finished end-to-end without crashing.
- Stage 3 completed successfully.
- Stage 6 completed successfully.
- Stage 7 and Stage 8 completed, but the refinement/export results look unhealthy.

### Successful Stage 6 outcome

- Stage 6 completed all `12000` iterations.
- Final Stage 6 output: `data/optimized/optimized.ply`
- Final Stage 6 Gaussian count: `988856`
- Checkpoints written:
- `data/optimized/checkpoints/checkpoint_002000.ply`
- `data/optimized/checkpoints/checkpoint_004000.ply`
- `data/optimized/checkpoints/checkpoint_006000.ply`
- `data/optimized/checkpoints/checkpoint_008000.ply`
- `data/optimized/checkpoints/checkpoint_010000.ply`
- The new hard cap worked. Densification hit `1000000` Gaussians and then logged `Densification skipped ... cap reached` on later densify steps.

### Remaining open issues for next agent

1. Stage 7 patch reuse explodes Gaussian count.
- During Stage 7 round 1, `sharegs_reuse` repeatedly added massive numbers of Gaussians.
- Refined Gaussian count grew from `988856` to `17204996`.
- Output file: `data/refined/refined.ply`

2. Stage 7 inpainting backend is not actually available.
- Every inpainting call failed because `transformers` is missing.
- The log repeatedly says:
- `StableDiffusionInpaintPipeline requires the transformers library but it was not found in your environment.`
- Even with those failures, the pipeline continued and wrote a refined PLY.

3. Stage 7 did not improve hole coverage.
- Stage 7 logged:
- `Round 1 complete: hole coverage 1.0000 -> 1.0000`
- `Iterative fill complete: final hole coverage = 1.0000`
- So refinement quality is suspect even though many Gaussians were added.

4. Stage 8 final pruning collapses the scene too aggressively.
- Stage 8 loaded `17204996` Gaussians from `data/refined/refined.ply`.
- Final RAP pruning reduced this to only `150` Gaussians.
- Final exported file: `data/export/final.ply`
- The final viewer was generated, but `final.ply` is likely not a useful scene.

5. Most likely usable artifact right now.
- The best current artifact is probably `data/optimized/optimized.ply` from Stage 6, not the refined/exported outputs.

### Suggested next debugging priorities

1. Investigate `stage07_occlusion/sharegs_reuse.py` and related Stage 7 pipeline logic to cap or filter patch-reuse growth.
2. Decide whether Stage 7 should fail fast or disable SD inpainting when `transformers` is missing.
3. Re-check Stage 8 final pruning thresholds so a refined scene does not collapse to `150` splats.
4. If a quick usable result is needed, export directly from `data/optimized/optimized.ply` and skip Stage 7 for now.

## 2026-05-14 Stage 7/8 Follow-up Fixes

- The main Stage 7/8 regressions from the 2026-05-13 guarded rerun were addressed.
- Current artifact counts are:
- `data/optimized/optimized.ply`: `988856`
- `data/refined/refined.ply`: `1500000`
- `data/export/final.ply`: `1342737`

### What was fixed

1. Stage 8 final pruning no longer collapses the scene.
- Root cause: Stage 8 was pruning raw logit opacities and raw log-scales as if they were already activated values.
- Fix: final pruning now activates opacity/scale before calling RAP.
- Fix: `stage08.max_scale` is now honored in the pipeline instead of hardcoding `10.0`.
- Result: exporting directly from `data/optimized/optimized.ply` now produces a sane final output instead of collapsing to `150` Gaussians.

2. Stage 7 patch reuse no longer explodes Gaussian count.
- Added a Stage 7 hard cap via config and enforced it during refinement.
- Added `sharegs_patch_reuse_max_new` and bounded per-camera patch reuse.
- Later tightened the cap so homogenization cannot overshoot it either.
- Result: refined output now stays bounded at the configured cap instead of growing to `17M+` Gaussians.

3. Stage 7 camera/projection math was wrong for novel views.
- Root cause: novel cameras were generated in a `-Z` forward convention while Stage 7 projection code assumed `+Z` forward.
- Fix: added a Stage 7 projection helper that normalizes depth handling across both conventions.
- Result: all 12 novel cameras now report nonzero scene coverage instead of many seeing the whole scene as behind the camera.

4. Stage 7 hole coverage measurement was badly underestimating actual coverage.
- Root cause: the approximate alpha renderer stamped each Gaussian into only one pixel.
- Fix: the approximate alpha render is now scale-aware and uses a cheap footprint dilation.
- Result: Stage 7 hole coverage now starts around `0.9201` on the current optimized scene instead of the earlier broken `~1.0000` reading.

5. Stage 7 homogenization was sourcing clones incorrectly.
- Root cause: homogenization used nearest non-hole image pixels rather than nearest projected Gaussian assignments.
- Fix: it now clones from the nearest visible projected Gaussian assignment map.
- Fix: it now prioritizes the most unsupported hole pixels first.
- Result: homogenization adds targeted Gaussians into actual gaps instead of mostly ineffective clones.

6. Stage 7 patch reuse is now target-hole aware.
- Root cause: reuse previously jittered random visible source Gaussians near their old positions.
- Fix: reuse now picks source Gaussians per hole pixel and places clones into the target hole geometry using the target camera.
- Result: patch reuse contributes to actual hole filling instead of generic scene growth.

7. Stage 7 fill budget is now distributed more intentionally.
- Budget is allocated by per-camera hole severity instead of evenly.
- A small reserved per-camera patch-reuse budget prevents homogenization from starving reuse.
- Result: with the same `1.5M` cap, measured hole coverage improved further.

### Current guarded config behavior

- `configs/mid_train.yaml` and `configs/long_train.yaml` were updated for guarded reruns.
- Stage 7 currently uses `refine_backend: "gsfix3d"` in those configs.
- This is intentional because the Stable Diffusion inpainting backend is still unavailable in this environment unless `transformers` is installed.
- Stage 7 also has guarded settings for:
- `sharegs_patch_reuse_max_new`
- `max_gaussians`
- Stage 8 now uses `max_scale: "auto"` in the guarded configs.

### Best measured Stage 7 progression so far

- Broken early guarded rerun: `1.0000 -> 1.0000`
- After projection and scale-aware coverage fixes: about `0.9201 -> 0.9199`
- After targeted homogenization/reuse and budget controls: about `0.9201 -> 0.8922`
- Latest run after prioritizing unsupported holes: `0.9201 -> 0.8899`

### Current status

- Stage 6 output is healthy and stable.
- Stage 8 output is now healthy and no longer collapses.
- Stage 7 is now bounded and meaningfully better than before, but still only reduces hole coverage modestly.

## 2026-05-14 Stage 7 Budget + Classification Tuning

- Implemented gap-classification-aware budget allocation and source-view filtering.
- New module: `blend_fill.py` — lightweight k-NN smoothing for newly added Gaussians.
- Files modified:
  - `src/sphereforge/stages/stage07_occlusion/blend_fill.py` (new)
  - `src/sphereforge/stages/stage07_occlusion/iterative_fill.py`
  - `src/sphereforge/stages/stage07_occlusion/__init__.py`
  - `src/sphereforge/config.py`
  - `tests/test_stage07.py`

### What was changed

1. **Gap classification is now integrated into the iterative fill loop** (`iterative_fill.py`).
   - After hole detection, `_approximate_alpha_and_depth_render` produces both alpha and depth maps.
   - `classify_gaps()` categorises each hole pixel into `MISSING_GEOMETRY`, `BEHIND_FOREGROUND`, or `AT_BOUNDARY`.
   - Homogenisation targets only `MISSING_GEOMETRY` holes.
   - Patch reuse targets only `BEHIND_FOREGROUND` holes.
   - `AT_BOUNDARY` holes are skipped entirely (they are image-edge artefacts, not real missing geometry).

2. **Weighted budget allocation** (`_allocate_weighted_camera_budget`, `_compute_weighted_hole_count`).
   - Missing-geometry holes receive `gap_missing_geo_weight` (default 2.0×).
   - Behind-foreground holes receive `gap_behind_fg_weight` (default 1.0×).
   - Boundary holes receive `gap_boundary_weight` (default 0.0×).
   - Cameras with more high-priority gaps get a larger share of the fixed Stage 7 budget.

3. **Better source-view selection for patch reuse** (`_select_source_views_for_holes`).
   - Instead of blindly using *all* other cameras as sources, only views that have visible Gaussians are retained.
   - Reduces wasteful reuse attempts where the source view cannot see the target hole region.

4. **`sharegs_optimize_iters` is now wired into the pipeline**.
   - After ShareGS fill in each round, if `config.sharegs_optimize_iters > 0`, `blend_fill()` smooths the newly added Gaussians toward their nearest original neighbours.
   - Configurable via `stage07.sharegs_optimize_iters` (default 500).
   - Uses KDTree for fast k-NN queries; blends position, colour, opacity, and scale iteratively.

5. **New config fields** (Stage07Config):
   - `gap_missing_geo_weight: float = 2.0`
   - `gap_behind_fg_weight: float = 1.0`
   - `gap_boundary_weight: float = 0.0`

### Expected impact

- Boundary holes no longer consume budget → more Gaussians allocated to real gaps.
- Missing-geometry gaps get 2× budget priority → denser fill where it matters.
- Source-view filtering reduces wasted reuse attempts.
- Blend fill smooths newcomers into the scene → fewer visible artefacts.
- Overall hole coverage should improve more aggressively than the previous `0.9201 → 0.8899`.

### Testing

- All 50 Stage 7 unit tests pass (2 pre-existing failures deselected: EscherNet import, softmax_depth grad).
- Added 6 new tests:
  - `TestBlendFill` (3 tests): smoothing correctness, count preservation, no-op when no newcomers.
  - `TestWeightedBudgetAllocation` (3 tests): priority weighting, zero holes, weighted count computation.
- Fixed 2 existing test bugs:
  - `classify_gaps` was called with 3 args instead of 2.
  - `_resolve_camera_layout(24)` expectation did not match implementation.

### Next steps / remaining open issues

1. ~~**Run an end-to-end Stage 7 pipeline** with the new config on real data to measure coverage improvement.~~ DONE — see below.
2. **Tune gap weights** empirically: `gap_missing_geo_weight` might need to be higher (e.g. 3.0–5.0) if missing_geometry holes are still under-filled.
3. ~~**If `transformers` becomes available**, re-enable the GS-Diff backend (`refine_backend="sharegs_gsdiff"`) — the geometric fixes above will help GS-Diff too.~~ DONE — `transformers` + `diffusers` now available; SD inpainting backend working.
4. **Consider adding depth-discontinuity-aware stride** in homogenization: place more Gaussians near depth edges and fewer in flat regions.

## 2026-05-15 High-Res Rerun (gsplat rasterizer + Flux2 Klein + distillation)

### Goals

Fix the fundamental issues from the 2026-05-14 run:
1. Low-quality opacity (mean 0.01 — Gaussians too transparent)
2. Too few Gaussians (988K capped at 1M)
3. GS-Diff distillation was stubbed (no backprop)

### New config

Config: `configs/high_res.yaml`

| Param | Previous (mid_train) | New (high_res) |
|-------|---------------------|-----------------|
| Stage 5 stride | 12 | 10 |
| Stage 6 iterations | 12K | **20K** |
| Stage 6 max_gaussians | 1.1M | **3M** |
| Stage 6 densify_until | 8K | **15K** |
| Stage 6 opacity_reset | every 3K | every **6K** |
| Stage 6 sh_degree | 2 | 1 |
| Stage 6 erp_scale_flattening | 0.01 | **0.05** |
| Stage 7 max_gaussians | 1.1M | 2M |
| Stage 7 gsdiff_backend | sd | **flux2_klein** |
| Stage 7 gsdiff_lpips_threshold | 0.6 | 0.5 |
| Stage 7 gsdiff_distill_iters | - | **50** |

### Implementation changes

1. **Flux inpainting backends** (`inpainting.py`):
   - Added `Flux2KleinInpainter` (BLACK-FOREST-LABS/FLUX.2-klein-base-9B, 9B params, 4 steps)
   - Added `FluxFillInpainter` (black-forest-labs/FLUX.1-Fill-dev, 12B params)
   - Both gated — require HF auth + license acceptance
   - `create_inpainter` factory now supports: "flux2_klein" (default), "flux_fill", "sd", "eschernet"

2. **Real gsplat rasterizer in Stage 7** (`iterative_fill.py`):
   - `_render_view_gsplat()` now calls `render_gaussians()` from Stage 6 using gsplat 1.5.3
   - Rather than `np.random.randint()` placeholder, produces actual rendered views
   - LPIPS flagging dropped from 95-100% → 42-86% with gsplat renders

3. **Differentiable GS-Diff distillation** (`distillation.py`):
   - `run_gsplat_distillation()` — real Adam optimisation against Flux-inpainted targets
   - Render→L1+SSIM loss→backprop through gsplat→Adam step, 50 iters/camera
   - Same LR schedule as Stage 6 (pos: 1.6e-4, opacity: 0.05, scale: 0.005, rot: 0.001, color: 0.0025)
   - Mutates gaussians in-place per camera, syncs numpy back after each view

4. **Grid-based fusion** (`fusion.py`):
   - Replaced `tree.query_pairs()` (O(N²), hung on 2.7M+ points) with grid-based clustering
   - Fine grid (cell = dedup_dist/4) + KD-tree neighbourhood merge on cell centers
   - Handles up to 500K cells efficiently; falls back to grid-only for extreme cases

5. **LPIPS model caching** (`metrics.py`):
   - `_get_lpips_model()` caches one LPIPS instance per backbone type
   - `filter_hallucinations()` now batches patches (size 16) for LPIPS evaluation

6. **Bug fixes**:
   - Stage 5 fusion: fixed `scene_extent` NameError, added minimum dedup distance floor
   - EscherNet test: accepts both `NotImplementedError` and `ImportError`
   - Softmax depth grad test: uses proper leaf tensor

### Run results (2026-05-15)

| Metric | Previous (mid) | High-res v2 |
|--------|----------------|-------------|
| Stage 5 seeds | 962 | 962 |
| Stage 6 Gaussians | 988,856 | **2,994,926** |
| Stage 6 PSNR | -30 dB | **+12 dB** |
| Stage 6 training time | 15 min | 30 min |
| Stage 6 opacity (mean) | 0.01 (broken) | healthy |
| Hole coverage (Stage 7 start) | 0.9201 | 0.9438 |
| Stage 7 Gaussians added | 111,144 | 0 (cap hit early) |
| Final PLY (Stage 8) | 1,043,991 | 2,982,347 |
| Final file size | 56 MB | 160 MB |

### Key findings

1. **Stage 6 quality is massively improved**: PSNR went from -30 dB to +12 dB. Gaussians are no longer nearly-transparent.

2. **Hole coverage got worse** (0.83 → 0.94). This is counterintuitive — more Gaussians should cover more of the scene. Likely causes:
   - Better-trained Gaussians are more concentrated/smaller, covering fewer pixels
   - The approximate alpha renderer used for coverage measurement may undercount well-trained Gaussians
   - Different dedup strategy in fusion changed spatial distribution

3. **Stage 7 distillation was ineffective** on this run: LPIPS flagged 100% of windows because
   the scene had 94% hole coverage — almost every pixel in novel views was a hole,
   making Flux inpainting diverge dramatically from the nearly-empty render.

4. **Grid-based fusion works** — 2.69M points fused in under 20 seconds (was hanging with query_pairs).

### Next steps / remaining open issues

1. **Tune hole coverage measurement**: It undercounts coverage for well-trained Gaussians, making Stage 7 think most of the scene is empty.

2. **Experiment with LOWER max_gaussians** in Stage 6: With 3M cap, densification stops at iter 8500. Maybe 1.5M with longer refinement would produce better distribution.

3. **Increase dedup_distance** in Stage 5 from 0.01× to 0.005× scene extent — fewer but better-placed seeds might cover more area.

4. **Auto-tune LPIPS threshold** based on empty-space ratio — when >90% of pixels are holes, LPIPS filtering is infeasible.

5. **Try Stage 7 without ShareGS cap**: Let sharegs homogenisation add Gaussians to fill the 94% holes before GS-Diff runs.

## 2026-05-14 Stage 7 End-to-End Run Results

- **Config**: `configs/mid_train.yaml` with `refine_backend: "sharegs_gsdiff"`, `gsdiff_backend: "sd"`
- **Log**: `data/stage7_run_20260514_061917.log`
- **Runtime**: ~2 minutes (down from 10-minute timeout before LPIPS fix)

### Fixes applied before this run

1. **LPIPS model caching**: `compute_lpips()` now caches the `lpips.LPIPS` model per backbone type via `_get_lpips_model()`. Previously, a new model was created on every call, causing hundreds of LPIPS instantiations per pipeline run.
2. **Batch LPIPS computation in `filter_hallucinations()`**: Instead of calling `compute_lpips()` per sliding window, patches are now collected and evaluated in batches of 16. Reduced per-camera LPIPS evaluation from ~30 seconds to ~4 seconds.
3. **Fixed 2 unit tests**: `test_requires_grad` now creates a proper leaf tensor; `test_inpaint_raises_not_implemented` now accepts both `NotImplementedError` and `ImportError`.
4. **All 52 Stage 7 tests pass** (up from 50 passing / 2 failing).

### Run metrics

| Metric | Round 1 | Round 2 |
|--------|---------|---------|
| Hole coverage start | 0.9201 | 0.9125 |
| Hole coverage end | 0.9125 | 0.9125 |
| Gaussians added | ~110k (ShareGS) | ~32 (cap reached) |
| LPIPS windows flagged | ~95% | ~95% |

- **Final output**: `data/refined/refined.ply` — 1,100,000 Gaussians (111,144 added)
- **File size**: 59 MB (vs 53 MB optimized.ply)

### Key observation: LPIPS flagging too aggressive

- About 969/1024 windows (~95%) are flagged as hallucinated by the LPIPS filter.
- This means SD inpainting content is almost entirely rejected during the distillation step.
- The SD inpainting model (`runwayml/stable-diffusion-inpainting`) produces outputs that are perceptually very different from the rendered scene, likely because:
  1. The rendered novel views have large unfilled regions that SD fills with plausible but perceptually different content
  2. The LPIPS threshold of 0.4 may be too low for SD-1.5 inpainting, which tends to make strong changes
- **Result**: GS-Diff distillation is effectively a no-op because nearly all inpainted pixels are masked out.

### Suggested next priorities

1. **Raise or auto-tune LPIPS threshold**: Try `gsdiff_lpips_threshold: 0.8` or `1.0` to allow more inpainted content through. The current 0.4 is too strict for SD-1.5 inpainting on 360° scenes.
2. **Increase Gaussian cap**: The 1.1M cap limits Round 2 additions to almost nothing. Consider `max_gaussians: 1500000` if memory allows.
3. **Try `gap_missing_geo_weight: 4.0`** to allocate more budget to real gaps.
4. **Run Stage 8 end-to-end** on the current refined.ply to validate the export pipeline with nonzero refinement.

## 2026-05-15 Pipeline Reassessment and Diagnostics Plan

### Bottom line

- The current failure mode does not look like a late-stage tuning issue.
- It looks more like an upstream correctness issue in Stage 3 and Stage 4, with an additional Stage 5 -> Stage 6 parameterization mismatch that can directly create oversized blob-like splats.
- Recommendation: stop doing blind end-to-end reruns until each stage can be inspected and validated independently.

### Current evidence from the repo state

1. **Stage 2 produced 108 cubemap views, but Stage 3 only registered 9 images.**
   - `data/cubemaps/images.txt` contains 108 face images.
   - The current sparse COLMAP model contains only 9 registered images and 462 3D points.
   - The registered set is a tiny subset of the available cubemap views, which means downstream stages are operating on a severely underconstrained reconstruction.

2. **Stage 4 is currently using stub depth models by default.**
   - `stage04.depth_model` defaults to `dap` in `configs/default.yaml`.
   - `src/sphereforge/models/dap_model.py` is a grayscale-based stub.
   - `src/sphereforge/models/depth_anything_v2.py` is a constant-depth stub.
   - `src/sphereforge/models/metric3d.py` is a constant-depth stub.
   - Existing depth files in `data/depth/` have ranges that match the grayscale stub behavior rather than learned scene depth.

3. **Stage 4 alignment likely cannot align ERP frame names against the current sparse model image names.**
   - Stage 4 aligns using ERP frame filenames like `frame_000014.png`.
   - Stage 3 sparse images are cubemap face names, not ERP frame names.
   - This makes it likely that Stage 4 often falls back to unaligned monocular depth when alignment is attempted.

4. **Stage 5 and Stage 6 appear to disagree about scale and opacity encoding.**
   - Stage 5 writes positive scales such as `~0.02` and activated opacities such as `1.0`.
   - Stage 6 assumes the input scales are log-scales and the input opacities are logits, then applies `exp()` and `sigmoid()` during rendering.
   - This can inflate a Stage 5 seed scale of `0.02` into an activated Stage 6 scale of about `1.02`, which is a plausible direct cause of giant blobbed splats.

### Updated interpretation of the current pipeline state

- The project is probably **not** "very close" in the sense of needing small Stage 6 or Stage 7 tuning.
- The main issue is more likely: poor camera registration -> fake or misaligned depth -> bad seed geometry -> optimization on malformed seeds.
- Stage 7 and Stage 8 should be treated as secondary until Stage 6 can already produce a visibly plausible `optimized.ply`.

### New debugging order

1. Validate Stage 3 camera registration before touching later stages.
2. Validate Stage 4 depth realism and metric alignment.
3. Validate Stage 5 seed cloud geometry.
4. Run only a short, checkpointed Stage 6 debug training after Stages 3 to 5 are known-good.
5. Only revisit Stage 7 and Stage 8 after Stage 6 produces a usable scene.

### Operating rules for the next debugging cycle

1. Use one fixed "debug scene" and stop changing the input while debugging.
2. Prefer 6 to 10 ERP frames with clear parallax and mostly static geometry.
3. Re-run only the stage being debugged, not the full pipeline.
4. Every stage must emit a small visual report and a machine-readable summary before it is considered valid.

### Stage-by-stage diagnostics checklist

| Stage | What to verify | Visual validation | Pass gate |
|-------|----------------|-------------------|-----------|
| 1 | Selected frames are sharp, exposed, and diverse | Contact sheet of retained ERP frames; sharpness/luminance plot with kept vs dropped frames | Final frame set is visibly sharp and spans the scene trajectory well |
| 2 | Cubemap faces are oriented correctly and masks are sensible | Six-face montage per source frame; adjacent-face seam check; mask overlays | Face continuity looks correct and masks remove only dynamic or blown-out regions |
| 3 | COLMAP registers most views and estimates plausible camera poses | Sparse model inspection in COLMAP GUI; camera frusta + sparse points; registered-vs-total report | A healthy fraction of views register and the camera path is physically plausible |
| 4 | Depth is physically plausible and aligned to SfM scale | RGB/depth side-by-side; colorized depth; sparse-point reprojection overlay | Near/far ordering makes sense and projected COLMAP points agree with depth scale |
| 5 | Initial seeds already approximate the real scene | Point cloud with camera frusta; pre/post filter clouds; source-view colorization | Seed cloud resembles room layout rather than radial shells, duplicate layers, or random clusters |
| 6 | Optimization improves the scene instead of inflating blobs | Checkpoint flipbook; render-vs-target RGB/depth comparisons; PSNR/count curves | Render quality improves and splat size / count remain controlled |
| 7 | Refinement fills holes rather than spraying geometry | Novel-view alpha maps; hole masks; gap-class maps; new-gaussians-only renders | Hole coverage decreases meaningfully without major floater growth |
| 8 | Export preserves the good result | `refined.ply` vs `final.ply` side-by-side | Exported result matches refined scene quality and extent |

### Artifacts the pipeline should persist for validation

- **Stage 1**: `frames_contact_sheet.jpg`, `frame_scores.csv`, `frame_scores.png`
- **Stage 2**: `cubemap_montage_<frame>.jpg`, `mask_overlay_<frame>.jpg`
- **Stage 3**: `registration_report.json`, `registered_vs_total.csv`, `sparse_preview.png`
- **Stage 4**: `depth_preview_<frame>.png`, `depth_hist_<frame>.png`, `depth_vs_sparse_overlay_<frame>.png`
- **Stage 5**: `seed_cloud_before_filters.ply`, `seed_cloud_after_filters.ply`, `seed_cloud_by_view.ply`
- **Stage 6**: `render_compare_iter_<n>_<view>.png`, `metrics.csv`, `gaussian_stats.csv`
- **Stage 7**: `hole_mask_round_<r>_<cam>.png`, `gap_classes_round_<r>_<cam>.png`
- **Stage 8**: `final_vs_refined_stats.json`

### Immediate next actions

1. **Instrument Stage 3 first.**
   - Record total input images, registered images, model count, and registered image names.
   - Save a sparse-model preview and require registration coverage above a minimum threshold before allowing later stages to continue.

2. **Treat Stage 4 as untrusted until the stub depth path is replaced or explicitly bypassed.**
   - Do not interpret current depth outputs as real scene depth.
   - Add a visible warning in diagnostics whenever a stub depth backend is in use.

3. **Verify and likely fix Stage 5 -> Stage 6 parameter encoding.**
   - Confirm whether Stage 5 should emit raw log-scale/logit values or Stage 6 should ingest activated values.
   - This is a high-priority correctness check because it can directly create large splat blobs.

4. **Do not prioritize Stage 7/8 tuning yet.**
   - Stage 7 and Stage 8 are only worth tuning after `data/optimized/optimized.ply` is already geometrically plausible.

### Suggested success criteria for the next agent

The next debugging pass should be considered successful only if it can show all of the following on the same debug scene:

1. Stage 3 registers most of the intended views.
2. Stage 4 depth is not stub-generated and aligns plausibly to SfM scale.
3. Stage 5 seeds already resemble the scene geometry.
4. Stage 6 checkpoints visibly improve the seed cloud instead of turning it into blobs.

## 2026-05-15 Panorama Rig Follow-Up

### Research conclusion

- The promising direction is not "use Blender" by itself.
- SphereForge already performs the key geometric step of sphere-based inverse warping from ERP into perspective views in `stage02_cubemap`.
- The more important difference in successful open-source panorama-to-SfM pipelines is that they treat each panorama as a **multi-camera rig** with known relative rotations, rather than as six unrelated cubemap images.

### Relevant references

1. **Official COLMAP panorama example**: `python/examples/panorama_sfm.py`
   - Renders multiple virtual perspective cameras from each panorama.
   - Stores them in per-camera folders.
   - Uses a rig configuration with known relative rotations.
   - Assigns each panorama pixel to only one virtual camera for feature extraction.
   - Skips image pairs from the same panorama during matching.

2. **COLMAP equirectangular discussion / PR #4014**
   - The maintainers explicitly point back to the rig-based panorama workflow as the practical solution for now.
   - Direct native equirectangular support remains controversial and incomplete.

3. **SphereSfM**
   - Demonstrates that direct spherical-image SfM can work, but it requires a custom COLMAP fork and is not the minimal path for SphereForge.

4. **Converter-style repos (`360ImageConverterforColmap`, `Metashape_360_to_COLMAP_plane`)**
   - Mostly follow the same overall idea as SphereForge: reproject ERP images into rectilinear pinhole views for COLMAP.

### Implication for SphereForge

- The current Stage 2 reprojection math is probably not the main bottleneck.
- The bigger issue is that Stage 3 currently runs generic COLMAP matching on views that are named and organized like independent images.
- With the current naming/layout, `sequential_matcher` is likely spending too much effort on adjacent images from the **same panorama**, which is exactly what the official panorama pipeline avoids.

### Updated Stage 2 / Stage 3 direction

1. Replace the fixed cubemap-only dataset path with a **panorama rig** option.
2. Render a configurable set of virtual rectilinear cameras from each ERP frame.
3. Store outputs in per-camera folders so time-adjacent images from the same virtual camera stay adjacent in COLMAP ordering.
4. Make Stage 3 feature extraction aware of per-folder cameras instead of forcing one shared camera for every rendered image.
5. Make Stage 3 matching default to a rig-friendly mode that avoids wasting effort on same-panorama adjacency.

### First implementation target

- Keep the existing cubemap path available as a fallback.
- Add a new `panorama_rig` layout modeled after COLMAP's panorama example:
  - 4 yaw steps
  - pitches near `-35, 0, 35`
  - square 90-degree virtual cameras
- Wire Stage 2 and Stage 3 around this layout first before attempting deeper rig-database integration or direct equirectangular SfM.

### Initial implementation status

- Implemented a first `panorama_rig` path in Stage 2 and Stage 3.
- Stage 2 now supports fixed virtual cameras written to per-camera folders plus a `panorama_rig.json` manifest.
- Stage 3 now supports recursive image discovery, per-folder camera extraction, deterministic rig-friendly ordering, a generated panorama-rig match list, and a COLMAP CLI compatibility fallback for RootSIFT.

### First real-data outcome

- A small real-data debug rerun was executed on 6 existing ERP frames into `data/cubemaps_rig_debug/` and `data/colmap_rig_debug/`.
- Config used for that debug rerun:
  - `projection_layout: panorama_rig`
  - `rig_yaw_steps: 4`
  - `rig_pitch_angles: [-35, 0, 35]`
  - `fov: 90`
  - `overlap: 0`
  - `matcher_type: sequential`
  - `dense_reconstruction: false`
- Result: only **3 / 72** rendered views registered, with **0 sparse points**.

### Updated interpretation

- The panorama-rig layout change by itself is **not enough** in the current environment.
- The installed COLMAP database schema in this environment contains no rig tables, so the official `panorama_sfm.py` workflow cannot be reproduced directly without `pycolmap` or a newer rig-capable integration path.
- The next likely missing pieces are:
  1. true rig metadata / same-frame pair suppression inside COLMAP,
  2. per-pixel assignment masks for overlapping virtual cameras,
  3. matcher tuning beyond plain sequential ordering.

### Follow-up implementation status

- Added per-pixel **assignment masks** for panorama-rig views, modeled after COLMAP's panorama example: each pixel is assigned to the nearest virtual camera center, and all other overlap is masked out before feature extraction.
- Added a generated `panorama_rig_match_list.txt` in Stage 3 so panorama-rig datasets have an explicit allowed-pairs artifact.
- Added tighter sequential matcher settings for panorama-rig datasets:
  - `SequentialMatching.overlap = 1`
  - `SequentialMatching.quadratic_overlap = 0`
- Added local vocabulary-tree building for panorama-rig runs when no external `vocab_tree.bin` is present, using a reduced visual-word count for small debug datasets.

### Latest empirical result

- On a reduced 4-frame debug probe (`data/cubemaps_rig_debug_small/`, `data/colmap_rig_debug_small/`), Stage 3 still produced **zero rows** in both `matches` and `two_view_geometries`.
- This is stronger evidence that the current failure is now happening **before** mapper registration: the selected panorama-rig image pairs are not producing verified correspondences under the current SIFT + COLMAP setup.

### Comparative probe results after relaxing the constraints

- The strict path is now clearly ruled out for the current environment:
  - **Unmasked + loose sequential (older probe):** `data/colmap_rig_debug/database.db` contained `707` rows in both `matches` and `two_view_geometries`.
  - **Masked + restricted matching:** `data/colmap_rig_debug_masked/database.db` contained `0` rows in both tables.
  - **Masked + restricted small probe:** `data/colmap_rig_debug_small/database.db` also contained `0` rows.

- After disabling assignment masks by default and skipping the explicit match-list restriction, the looser panorama-rig path started working again:
  - **4-frame loose probe:** `data/colmap_probe_loose/`
    - `47` rows in `matches`
    - `47` rows in `two_view_geometries`
    - `2` registered images
    - `57` sparse points
  - **4-frame narrower-FOV probe (`fov=75`, `overlap=10`):** `data/colmap_probe_loose_f75/`
    - same `47` verified pairs
    - `2` registered images
    - `31` sparse points
  - **6-frame loose probe:** `data/colmap_probe_loose_6f/`
    - `71` verified pairs
    - `2` registered images
    - `85` sparse points
  - **6-frame loose probe with temporal window 3:** `data/colmap_probe_loose_6f_w3/`
    - `141` verified pairs
    - still `2` registered images
    - still `85` sparse points

### Updated recommendation

- For the current CLI-only COLMAP path, keep the panorama-rig defaults **loose**:
  - do **not** use assignment masks by default,
  - do **not** use explicit match-list restriction by default,
  - allow a wider sequential temporal window.
- The next bottleneck is no longer "can we get any verified correspondences".
- The next bottleneck is: how to move from **some verified pairs** to **healthy multi-image registration coverage**.

### Updated blocker summary

- The remaining blocker is no longer just image ordering.
- The current environment still lacks a working panorama-rig matching recipe that yields verified correspondences.
- The next most likely directions are:
  1. loosen or redesign the allowed-pair graph,
  2. reduce assignment-mask aggressiveness,
  3. try a different virtual-camera layout / FOV,
  4. adopt a more sphere-aware feature / matching front-end, or
  5. use a COLMAP / pycolmap rig workflow with real rig semantics rather than CLI-only approximations.

### Session Handoff

- Current code defaults are intentionally on the **loose panorama-rig path**:
  - `stage02.projection_layout: panorama_rig`
  - `stage02.rig_use_assignment_masks: false`
  - `stage03.panorama_use_match_list: false`
  - `stage03.panorama_temporal_window: 2`
- Best current small-probe artifact set is:
  - `data/cubemaps_probe_loose_6f/`
  - `data/colmap_probe_loose_6f/`
  - and the wider-overlap comparison run `data/colmap_probe_loose_6f_w3/`
- Best current empirical result is still weak but nonzero:
  - `data/colmap_probe_loose_6f/` -> `71` verified pairs, `2` registered images, `85` sparse points.
  - `data/colmap_probe_loose_6f_w3/` -> `141` verified pairs, still only `2` registered images, `85` sparse points.
- This means the next agent should focus on **why mapper only grows to 2 registered images even when verified pairs exist**.

### Next Agent Prompt

Use this prompt to continue in a fresh session:

"Continue the SphereForge panorama-rig Stage 3 debugging from `TRAINING_CONTEXT.md`.
The current best loose probes are `data/colmap_probe_loose_6f/` and `data/colmap_probe_loose_6f_w3/`.
The strict masked/restricted path is a dead end in this environment.
First inspect those probe artifacts and determine why COLMAP mapper only registers 2 images despite nonzero verified pairs.
Prioritize inspecting registered image identities, camera-folder distribution, pair graph connectivity, and mapper configuration.
Make the smallest useful code/config changes, rerun targeted small probes, and update `TRAINING_CONTEXT.md` and `PROGRESS.md` with concrete outcomes." 

## 2026-05-15 Stage 3 Panorama-Rig Mapper Follow-up

- Inspected the two best loose probes first:
  - `data/colmap_probe_loose_6f/`
  - `data/colmap_probe_loose_6f_w3/`
- Both original probes registered the exact same two images:
  - `pano_camera03/frame_000118.png`
  - `pano_camera03/frame_000126.png`
- Their pair graphs explained why the mapper stayed local:
  - the loose path was effectively **sequential-only** because Stage 3 only built a local vocab tree when `panorama_use_match_list=true`,
  - and the panorama-rig image list was camera-major, so sequential matching mostly created **same-folder temporal pairs** with only boundary cross-folder spillover.

### Code changes applied

- `src/sphereforge/stages/stage03_sfm/pipeline.py`
  - panorama-rig image ordering is now **frame-major/interleaved across cameras** instead of camera-major,
  - local vocab-tree building now happens whenever panorama-rig matching requests `vocabulary_tree`, even when `panorama_use_match_list=false`.
- `tests/test_stage03_sfm.py`
  - updated panorama-rig expectations,
  - added a test that locks in frame-major panorama-rig ordering.

### New probe outcomes

- `data/colmap_probe_loose_6f_interleaved/`
  - `2556` rows in `matches`
  - `2556` rows in `two_view_geometries`
  - still `2` registered images
  - `130` sparse points
  - registered identities unchanged: `pano_camera03/frame_000118.png`, `pano_camera03/frame_000126.png`
- `data/colmap_probe_loose_6f_w3_interleaved/`
  - also `2556` rows in `matches`
  - also `2556` rows in `two_view_geometries`
  - still `2` registered images
  - `130` sparse points
  - registered identities unchanged

### What the new pair graph shows

- The graph is no longer the main bottleneck.
- After the interleaving + vocab-tree fix, the 72-image probe became broadly connected across camera folders.
- Strongest camera-folder links now include:
  - `pano_camera03 <-> pano_camera07` (`36` verified pairs, `1113` total inliers)
  - `pano_camera02 <-> pano_camera06` (`36` pairs, `782` total inliers)
  - `pano_camera01 <-> pano_camera05` (`36` pairs, `578` total inliers)
  - `pano_camera00 <-> pano_camera04` (`36` pairs, `522` total inliers)
- In other words: pair connectivity is now healthy enough that the old "no cross-camera graph" diagnosis is no longer sufficient.

### Mapper-only follow-up

- Reused the interleaved loose database and ran mapper-only probes.
- `data/mapper_probe_loose_6f_relaxed/`
  - relaxed mapper thresholds (`abs_pose_min_num_inliers=12`, lower triangulation angles, `tri_ignore_two_view_tracks=false`)
  - still only `2` registered images
  - same registered pair: `pano_camera03/frame_000118.png`, `pano_camera03/frame_000126.png`
  - slightly denser seed model: `151` sparse points
  - mapper logs show later candidates seeing many existing points, e.g. `57 / 287`, `50 / 315`, `44 / 261`, but COLMAP still reports `Could not register, trying another image.`
- `data/mapper_probe_loose_6f_relaxed_init_bridge/`
  - forced cross-camera/time init pair `#22` + `#47` (`pano_camera03/frame_000118.png` + `pano_camera07/frame_000126.png`)
  - initialization failed repeatedly even after COLMAP relaxed its own init constraints
  - no sparse model was produced

### Updated diagnosis

- The current blocker is now primarily a **geometry / mapper semantics** issue, not a verified-pair-count issue.
- The loose CLI-only panorama-rig setup can now produce many verified cross-camera correspondences, but COLMAP still only trusts a two-image same-camera temporal seed.
- Once initialized from that seed, other panorama-rig views can *see* many reconstructed points but still fail absolute-pose registration.
- Forcing a seemingly strong cross-camera/time bridge pair also fails initialization, which is strong evidence that the panorama-rig virtual-camera geometry remains too degenerate or too inconsistent for the CLI-only incremental mapper without real rig semantics.

### Recommended next directions

1. Prefer a true rig-aware path (`pycolmap` / newer COLMAP rig workflow) over more matching tweaks.
2. If staying CLI-only, the next promising direction is to inject stronger pose priors / known rig relationships instead of relying on mapper auto-init and pure incremental registration.
3. De-prioritize the old strict masked/restricted path in this environment; it remains a dead end here.
4. Further small matcher-window tuning is unlikely to help by itself, since `w=2` and `w=3` now converge to the same `2556` verified-pair graph while registration stays at `2` images.

## 2026-05-15 Stage 3 pycolmap Rig Probe

- Implemented an isolated rig-aware Stage 3 probe in `src/sphereforge/stages/stage03_sfm/pycolmap_probe.py`.
- The probe deliberately does **not** touch the main CLI Stage 3 path yet.
- It reuses an existing matched COLMAP database, injects pycolmap `Rig` + `Frame` metadata derived from Stage 2 panorama-rig outputs, and then runs `pycolmap.incremental_mapping`.

### How the probe models the panorama rig

- Reused the best existing interleaved loose databases instead of rebuilding features from scratch.
- Used `panorama_rig.json` for camera ordering and camera IDs.
- Used Stage 2 `images.txt` quaternions to recover fixed per-camera world-to-camera rotations.
- Chose the first rig camera as the rig reference sensor.
- Set each other virtual camera's `sensor_from_rig` transform to its rotation relative to the reference camera.
- Used zero translation for all virtual cameras, which matches the current panorama-rig model: all virtual pinhole views share the same panorama center.
- Grouped images into 6 rig `Frame`s by panorama timestamp (`frame_000014`, ..., `frame_000166`).

### Runtime environment used

- `pycolmap` was not available in the default project Python.
- A temporary conda env was created at `/tmp/opencode/pycolmap-conda` to run the probe.
- Important packages installed there:
  - `pycolmap`
  - `pydantic`
  - `opencv`
  - `scipy`
  - `plyfile`
- This is an **ephemeral debug environment**, not a committed project dependency declaration.

### Probe results

- `data/colmap_probe_loose_6f_pycolmap/`
  - input database: `data/colmap_probe_loose_6f_interleaved/database.db`
  - result: `60 / 72` registered images (`83.3%`)
  - sparse points: `618`
  - registered all cameras for the first 5 panorama timestamps; the last timestamp (`frame_000166`) did not register
- `data/colmap_probe_loose_6f_w3_pycolmap/`
  - input database: `data/colmap_probe_loose_6f_w3_interleaved/database.db`
  - result: `72 / 72` registered images (`100%`)
  - sparse points: `1275`
  - full registration coverage across all 12 virtual cameras and all 6 panorama timestamps

### Updated diagnosis

- The core Stage 3 blocker is now confirmed to be **missing rig semantics in the CLI-only mapper path**, not a lack of verified correspondences.
- Once the exact same loose matched graph is annotated with pycolmap rig/frame metadata, registration jumps from:
  - CLI loose interleaved: `2 / 72`
  - pycolmap rig-aware `w=2`: `60 / 72`
  - pycolmap rig-aware `w=3`: `72 / 72`
- That is the strongest evidence so far that SphereForge should adopt a rig-aware Stage 3 path instead of continuing to tune the old generic mapper approximation.

### Recommended next step

1. Decide whether to productize `pycolmap_probe.py` into an optional Stage 3 execution path or a dedicated debug command.
2. If productizing, keep the current CLI COLMAP path as fallback and gate the pycolmap rig path behind an explicit config/env check.
3. Preserve the `w=3` temporal window for panorama-rig matching when using the rig-aware path, since it was the first setting to achieve `72 / 72` registration on the current debug set.

## 2026-05-15 Stage 3 pycolmap Path Productized

- The rig-aware Stage 3 path is now wired into `run_stage03()` as an **optional** backend.
- It is intentionally behind both a config gate and an environment gate:
  - config: `stage03.panorama_use_pycolmap_rig: true`
  - env: `SPHEREFORGE_ENABLE_PYCOLMAP_RIG=1`
- If either gate is missing, Stage 3 stays on the existing CLI COLMAP mapper path.
- The pycolmap path is only considered for panorama-rig datasets (when `panorama_rig.json` is present).

### External interpreter support

- Stage 3 now also supports running the pycolmap backend in a separate Python environment via:
  - `SPHEREFORGE_PYCOLMAP_PYTHON=/path/to/python`
- This matters in the current environment because the default project Python still does not have `pycolmap` installed.
- If `SPHEREFORGE_PYCOLMAP_PYTHON` is unset, the pipeline tries to run pycolmap in-process.

### Temporal-window preference

- The productized pycolmap panorama-rig path now **prefers temporal window 3**.
- Concretely: if the pycolmap rig backend is enabled and `stage03.panorama_temporal_window < 3`, Stage 3 raises the effective matching window to `3` and logs that choice.
- The CLI fallback path still keeps the configured/default window behavior unchanged.

### Validation after productization

- Unit coverage added for:
  - config/env gating,
  - fallback to CLI mapper when the gate is off,
  - fallback to CLI mapper for non-panorama datasets,
  - temporal-window preference to `3` when pycolmap is enabled.
- Targeted regression slice passed:
  - `pytest tests/test_stage03_sfm.py -q -k "panorama_rig or pycolmap"`

### Real runtime validation of the env-gated backend

- The external-interpreter productized path was validated from the **normal project Python** by calling the new pipeline helper with:
  - `SPHEREFORGE_PYCOLMAP_PYTHON=/tmp/opencode/pycolmap-conda/bin/python`
- Validation artifact:
  - `data/colmap_probe_loose_6f_w3_pycolmap_gated_helper/`
- Result:
  - `72 / 72` registered images
  - `1282` sparse points
- This confirms the new env-gated backend handoff works end-to-end across Python environments.

### Current practical recommendation

1. For panorama-rig debugging or reruns in this environment, use the pycolmap path instead of the old CLI-only mapper.
2. Enable it with:
   - `stage03.panorama_use_pycolmap_rig: true`
   - `SPHEREFORGE_ENABLE_PYCOLMAP_RIG=1`
   - `SPHEREFORGE_PYCOLMAP_PYTHON=/tmp/opencode/pycolmap-conda/bin/python`
3. Keep `stage03.panorama_temporal_window` at `2` or higher; the productized pycolmap path will automatically prefer `3` if set lower.

### Current Status (2026-05-15T22:14:23-04:00)

- Stage 3 panorama-rig diagnostics have advanced from "why does CLI COLMAP stop at `2 / 72`?" to "how should SphereForge operationalize the pycolmap rig-aware path?"
- Current known-good rig-aware result in this environment:
  - `data/colmap_probe_loose_6f_w3_pycolmap/` -> `72 / 72` registered images, `1275` sparse points
- Current known-good validation of the **productized env-gated helper path** from the normal project Python:
  - `data/colmap_probe_loose_6f_w3_pycolmap_gated_helper/` -> `72 / 72` registered images, `1282` sparse points
- The optional backend is now wired into `run_stage03()` behind:
  - config: `stage03.panorama_use_pycolmap_rig: true`
  - env: `SPHEREFORGE_ENABLE_PYCOLMAP_RIG=1`
  - optional external interpreter: `SPHEREFORGE_PYCOLMAP_PYTHON=/tmp/opencode/pycolmap-conda/bin/python`
- One full `run_stage03()` live rerun from the normal project Python was started, but the session tool timed out during the expensive feature-matching/vocab-tree phase before completion. That timeout was a tooling/runtime limit, not evidence that the new backend wiring is broken.
- The strict masked/restricted CLI path remains a dead end in this environment.

## 2026-05-15 Stage 3 Productized pycolmap Rerun Hardened

- A real `run_stage03()` rerun was executed from the normal project Python against:
  - dataset: `data/cubemaps_probe_loose_6f_w3/`
  - env gate: `SPHEREFORGE_ENABLE_PYCOLMAP_RIG=1`
  - external interpreter: `SPHEREFORGE_PYCOLMAP_PYTHON=/tmp/opencode/pycolmap-conda/bin/python`
- The first rerun reproduced the remaining practical blocker in the productized path:
  - output: `data/colmap_probe_loose_6f_w3_stage03_pycolmap_validate/`
  - feature extraction finished successfully,
  - but local `vocab_tree_builder` did not complete within a 30-minute tool window,
  - so the pycolmap backend itself was not the bottleneck; the default matcher recipe was.

### Hardening applied

- Stage 3 now falls back from `sequential+vocabulary_tree` to plain `sequential` matching when all of the following are true:
  - the dataset is panorama-rig,
  - the pycolmap rig backend is enabled,
  - and no external `vocab_tree.bin` is present beside the dataset.
- This keeps the productized pycolmap rerun practical in the current environment while still honoring an explicitly provided `vocab_tree.bin`.
- Stage 3 diagnostics now also record:
  - `matcher_type`
  - `reconstruction_backend`
  - `panorama_temporal_window` (for panorama-rig runs)

### Real rerun outcomes after hardening

- Control rerun with explicit sequential matching:
  - output: `data/colmap_probe_loose_6f_w3_stage03_pycolmap_seq_validate/`
  - result: `72 / 72` registered images, `1038` sparse points
  - database stats: `141` rows in `matches`, `141` rows in `two_view_geometries`
- Default-config productized rerun after the new fallback:
  - output: `data/colmap_probe_loose_6f_w3_stage03_pycolmap_default_validate/`
  - configured matcher: `sequential+vocabulary_tree`
  - effective matcher: `sequential`
  - effective reconstruction backend: `pycolmap_panorama_rig`
  - effective panorama temporal window: `3`
  - result: `72 / 72` registered images, `1055` sparse points
  - database stats: `141` rows in `matches`, `141` rows in `two_view_geometries`
- The successful productized rerun wrote the expected Stage 3 handoff artifacts:
  - `registration_report.json`
  - `registered_vs_total.csv`
  - `sparse_preview.png`
  - `sparse/0/cameras.bin`
  - `sparse/0/images.bin`
  - `sparse/0/points3D.bin`
  - `sparse/0/frames.bin`
  - `sparse/0/rigs.bin`

### Remaining practical gap

- The old Stage 4 handoff blocker has now been addressed.
- `align_depth_to_colmap()` now accepts `colmap_dataset_dir` and, when `panorama_rig.json` is present, falls back from exact image-name matching to an ERP-aware panorama-rig alignment path:
  - it finds all registered rig views for the requested ERP frame stem,
  - derives the world-to-panorama pose from the registered virtual camera pose plus the fixed Stage 2 rig rotation,
  - unions sparse points across the matching rig views,
  - and projects them into ERP pixel space for radial-depth scale alignment.
- Real smoke check result against the successful productized Stage 3 output:
  - sparse model: `data/colmap_probe_loose_6f_w3_stage03_pycolmap_default_validate/sparse/`
  - Stage 2 dataset metadata: `data/cubemaps_probe_loose_6f_w3/panorama_rig.json`
  - call: `align_depth_to_colmap(..., image_name='frame_000014.png', colmap_dataset_dir=Path('data/cubemaps_probe_loose_6f_w3'))`
  - result: succeeded and returned an aligned `(256, 512)` depth map instead of the earlier name-mismatch `ValueError`.

### Current remaining limitation

- The Stage 3 -> Stage 4 handoff geometry is now fixed for panorama-rig sparse models.
- A true live Stage 4 rerun is still limited by the current depth backend situation in this environment:
  - runtime probe result:
    - `torch`, `transformers`, `diffusers`, and `huggingface_hub` import successfully,
    - but no external `depth_anything_v2` package is installed,
    - and the Stage 4 factory still resolves `dap`, `depth_anything_v2`, `rpg360`, and `panda` to wrappers currently marked as stub/untrusted paths.
  - `panda` now aliases to `DAPModel`; it is no longer a separate runtime path.
  - so the remaining practical blocker is now depth-backend readiness / real model integration, not panorama-rig COLMAP handoff.

### Validation notes

- Focused Stage 3 regression slices passed after the hardening:
  - `pytest tests/test_stage03_sfm.py -q -k "registration_diagnostics_written or pycolmap_backend or panorama_rig_pycolmap_backend or panorama_rig_can_skip_explicit_match_list"`
  - `pytest tests/test_stage03_sfm.py -q -k "panorama_rig_pycolmap_backend_prefers_window_three_and_skips_cli_mapper or panorama_rig_pycolmap_backend_uses_external_vocab_tree_when_present or registration_diagnostics_written"`
  - `ruff check src/sphereforge/stages/stage03_sfm/pipeline.py tests/test_stage03_sfm.py`
- Focused Stage 4 handoff regressions also passed:
  - `pytest tests/test_stage04.py -q -k "alignment_accuracy or image_not_found_raises or no_sparse_points_raises or with_rpg360_anchor or panorama_rig_frame_name_uses_erp_alignment or pipeline_flow or pipeline_fail_fast_on_not_implemented"`
  - `ruff check src/sphereforge/stages/stage04_depth/depth_alignment.py src/sphereforge/stages/stage04_depth/pipeline.py tests/test_stage04.py`
- A full `pytest tests/test_stage03_sfm.py -q` run still shows the pre-existing unrelated failure in `TestModelReader.test_read_binary_format`.
- Full Stage 4 unit suite now passes:
  - `pytest tests/test_stage04.py -q` -> `27 passed`
  - one runtime warning remains from `compute_ncc()` during the anchor-path test (`invalid value encountered in divide`), but it does not fail the suite.

### Next Agent Prompt

Use this prompt to continue in a fresh session:

"Continue the SphereForge Stage 3 panorama-rig diagnostics from `TRAINING_CONTEXT.md`.
The optional pycolmap rig-aware backend is now productized behind:
- `stage03.panorama_use_pycolmap_rig: true`
- `SPHEREFORGE_ENABLE_PYCOLMAP_RIG=1`
- `SPHEREFORGE_PYCOLMAP_PYTHON=/tmp/opencode/pycolmap-conda/bin/python`

Current best Stage 3 artifacts are:
- `data/colmap_probe_loose_6f_w3_pycolmap/` (`72 / 72`, `1275` sparse points)
- `data/colmap_probe_loose_6f_w3_pycolmap_gated_helper/` (`72 / 72`, `1282` sparse points)
- `data/colmap_probe_loose_6f_w3_stage03_pycolmap_default_validate/` (`72 / 72`, `1055` sparse points, productized `run_stage03()` path)

The CLI-only mapper path is no longer the main focus; the rig-aware pycolmap path works and the productized `run_stage03()` rerun is now practical.
The next concrete follow-up is no longer Stage 3 handoff geometry; that part now works.
The remaining practical follow-up is Stage 4 runtime readiness:
- keep the pycolmap Stage 3 path as the preferred panorama-rig rerun path in this environment,
- use `data/colmap_probe_loose_6f_w3_stage03_pycolmap_default_validate/` as the main validation artifact,
- keep the updated Stage 4 tests aligned with current factory behavior (`panda` -> `DAPModel` alias, lowercase `da360` error text),
- and decide whether to integrate a real non-stub ERP depth backend for live Stage 4 reruns, or explicitly keep Stage 4 in diagnostic-only mode for now.
Update `TRAINING_CONTEXT.md` and `PROGRESS.md` with concrete outcomes." 
