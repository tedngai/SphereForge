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
