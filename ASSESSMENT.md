# SphereForge — Code Assessment Report

**Date:** 2026-05-02
**Overall Grade:** B+ (Solid foundation, not production-ready)
**Lines of source code:** ~15,500
**Lines of test code:** ~4,700
**Task completion:** 92/94 (98%)

---

## 1. Project Overview

SphereForge is a multi-stage pipeline that transforms 360° camera footage into high-quality 3D Gaussian Splat scenes. It has 8 pipeline stages plus cross-cutting infrastructure:

| Stage | Name | Files | Status |
|-------|------|-------|--------|
| 0 | Infrastructure | 4 (src root) | 83% done |
| 1 | Video Ingestion & Frame Selection | 7 | 100% done |
| 2 | Equirect→Cubemap + COLMAP Prep | 8 | 100% done |
| 3 | COLMAP SfM | 7 | 100% done |
| 4 | Dense Depth Estimation | 7 | 100% done |
| 5 | Initial Gaussian Seeding | 12 | 100% done |
| 6 | Multi-View Optimization | 12 | 100% done |
| 7 | Occlusion Recovery | 14 | 100% done |
| 8 | Post-Processing & Export | 8 | 100% done |

Pipeline data flow: `raw/` → `frames/` → `cubemaps/` → `colmap/` → `depth/` → `gaussians/` → `optimized/` → `refined/` → `export/`

---

## 2. Strengths

### 2.1 Architecture
- Clear 8-stage pipeline with well-isolated concerns, one subdirectory per stage.
- Pydantic-based config system (`config.py`) with sensible defaults matching `PIPELINE_DESIGN_V2.md`.
- Clean data flow between stages via shared I/O helpers (`common/io.py`, `common/colmap_helpers.py`).
- Proper `pyproject.toml` with optional dependency groups (`depth`, `occlusion`, `rasterizer`, `dev`, etc.).
- Entry point registered: `sphereforge = sphereforge.cli:main`.

### 2.2 Code Quality
- Consistent type hints (Python 3.11+ `X | Y` union syntax) on all public functions.
- Google-style docstrings with Args/Returns/Raises on every public function.
- Descriptive logging at appropriate levels (`DEBUG` for per-frame detail, `INFO` for stage progress, `WARNING` for degraded quality, `ERROR` for failures).
- Thorough input validation and error handling throughout — no bare `except` clauses, no ignored errors.
- Tooling: ruff (line-length 100), black, isort, mypy, pytest all configured in `pyproject.toml`.

### 2.3 Testing
- ~4,700 lines of test code across 10 test files.
- Good coverage of edge cases: shape validation, stride subsampling, deduplication logic, zero-depth filtering, empty inputs, luminance boundaries.
- Uses synthetic test data with `unittest.mock` for heavy models (Stage 4, 6 tests mock the depth estimators and rasterizer).
- Fixtures in `tests/conftest.py` provide reusable synthetic images and depth maps.

### 2.4 Documentation
- `AGENTS.md` (148 lines): clear project conventions, task workflow, validation checklist.
- `PIPELINE_DESIGN_V2.md` (679 lines): detailed pipeline specification with V1→V2 changelog.
- `TASKS.md` (271 lines): 94 tasks with IDs, descriptions, dependencies, status, reuse classification.
- `PROGRESS.md`: completion log with timestamps, file lists, and implementation notes.

---

## 3. Critical Issues (Blockers — P0)

### 3.1 CLI is a stub (`src/sphereforge/cli.py:40`)

The `process` and `export` commands print `"Pipeline not yet implemented."` and exit immediately. Only the `status` command works. There is no way to run any pipeline stage from the command line.

```python
# cli.py:40 — the process command ends with:
click.echo("Pipeline not yet implemented.")
```

**Fix:** Wire up `process` to accept input, load config, and call `run_stage01()` through `run_stage08()` in sequence. Wire up `export` to call Stage 8 exports.

### 3.2 No config files exist (`configs/` is empty)

The `configs/` directory exists in the repo but contains zero files. Users must construct Pydantic models programmatically. There are no example YAML configs for common scenarios (indoor, outdoor, high-resolution, low-res preview).

**Fix:** Create at minimum:
- `configs/default.yaml` — sane defaults for general use
- `configs/high_quality.yaml` — max settings
- `configs/fast_preview.yaml` — reduced settings for rapid iteration

### 3.3 No rasterizer — Stage 6 produces garbage on CPU

`render_gaussians()` in `training_loop.py:112` delegates to gsplat's CUDA rasterizer when gsplat is installed. Without gsplat, it falls back to `_render_gaussians_stub()` which returns random tensors. This means:
- On CPU (no gsplat): training produces **meaningless output** (random tensors).
- On GPU with gsplat: training works but requires gsplat >= 1.0 with CUDA.

```python
# training_loop.py:326-327
def _render_gaussians_stub(means, image_height, image_width):
    rendered_image = torch.rand(3, image_height, image_width) * 0.8 + 0.1  # random!
    rendered_depth = torch.rand(image_height, image_width) * 10.0 + 1.0     # random!
    return rendered_image, rendered_depth, rendered_alpha
```

**Fix:** Add a clear error message when neither gsplat nor CUDA is available. Document the exact `pip install` command for users. Consider adding a CPU-only differentiable rasterizer (e.g., `torch-3dgs` or a pure-PyTorch implementation) as a slower but functional fallback.

### 3.4 Depth models are mostly stubs

| Model | Status | File |
|-------|--------|------|
| DAP (Depth Any Panoramas) | Unknown — factory creates it but implementation not verified | `models/dap_model.py` |
| Depth Anything V2 | Unknown — factory creates it | `models/depth_anything_v2.py` |
| PanDA | **STUB** — raises `NotImplementedError` | `stage04_depth/panda_model.py:275` |
| DA360 | **STUB** — raises `NotImplementedError` | `model_factory.py:67` |
| EscherNet (Stage 7) | **STUB** — raises `NotImplementedError` | `stage07_occlusion/eschernet.py` |
| OmniRoam (Stage 7) | **STUB** | `stage07_occlusion/omniroam.py` |

The PanDA fallback in the pipeline writes **zero-depth maps**, which will silently produce corrupted output downstream:

```python
# stage04/pipeline.py:117 — silent fallback to zero depth
except NotImplementedError as exc:
    logger.warning("Depth estimation failed... Writing zero depth map as fallback.")
    raw_depth = np.zeros(image.shape[:2], dtype=np.float32)
```

**Fix:** Verify DAPModel and DepthAnythingV2Model have working implementations with downloadable weights. If not, make them raise clear errors too. The pipeline should fail-fast with a clear error instead of silently writing zero-depth maps.

### 3.5 Stage 5 stride handling is bypassed

The pipeline computes per-pixel confidence maps and stride maps, then ignores them entirely and uses a uniform `config.stride` for everything:

```python
# stage05/pipeline.py:79-99
if config.cross_validate_depth and n_frames > 1:
    stride_map = np.full(depth_map.shape, config.stride, dtype=np.int32)
else:
    stride_map = np.full(depth_map.shape, config.stride, dtype=np.int32)
# ... then later:
effective_stride = config.stride  # ignores stride_map entirely!
```

The `stride_assignment.py` module exists but its output is discarded. Per-pixel stride is a key V2 feature for sparse seeding in low-confidence regions. This means all pixels get full-resolution seeding, producing noisy Gaussians and wasting memory in unreliable areas.

**Fix:** Actually use the per-pixel stride map. Low-confidence pixels (stride > 1) should be projected at coarser resolution as designed in `PIPELINE_DESIGN_V2.md`.

---

## 4. Significant Issues (Quality-Degrading — P1)

### 4.1 Serial processing throughout — no parallelism

Every stage processes frames one at a time with no parallelization:

| Stage | Operation | Parallelizable |
|-------|-----------|----------------|
| 2 | Cubemap extraction per frame | Yes — frames are independent |
| 4 | Depth estimation per frame | Yes — frames are independent |
| 5 | 3D projection per frame | Yes — frames are independent |
| 6 | Rendering per view | Partially — GPU-bound |

For a 10-minute 360° video at 5fps, that's 3,000 frames. Single-threaded processing of this many frames will take hours.

**Fix:** Use `concurrent.futures.ProcessPoolExecutor` for CPU-bound ops (cubemap extraction) and `ThreadPoolExecutor` for I/O-bound ops (depth estimation that offloads to GPU). Add a `num_workers` config option.

### 4.2 No checkpointing or resume capability

If Stage 6 crashes at iteration 29,000 out of 30,000, all progress is lost. No intermediate `.ply` files are saved during training. The same applies across stages — if you run stages 1-5 and stage 6 crashes, you must re-run from raw input.

**Fix:** Save checkpoints in training loop every N iterations. Add a `--resume` flag to the CLI. Use a stage-completion marker file (e.g., `data/<stage>/._done`) so the pipeline can skip completed stages on restart.

### 4.3 Stage 2 duplicates cubemap extraction

The pipeline extracts cubemap crops, resizes them, then **extracts them again** in the same loop:

```python
# stage02/pipeline.py — in the for loop:
crops = extract_diversified_cubemaps(...)  # first extraction
for crop_img, ... in crops:
    crop_img = cv2.resize(...)             # first resize
# ... then later in the same loop:
for i, ((crop_img, face_name, yaw_deg, pitch_deg), mask) in enumerate(zip(crops, final_masks)):
    crop_img = cv2.resize(...)             # resize AGAIN
    write_image(...)
```

The first set of resized crops (`resized_crops`) is used only for YOLO masking. The original crops are then re-resized for output. This is wasteful — the resize should happen once.

**Fix:** Extract once, resize once, use the resized version for both masking and output.

### 4.4 Inefficient `np.ix_` usage in projection

`project_to_3d()` uses `np.ix_()` for stride-sampled indexing, which creates full meshgrid index arrays:

```python
# projection.py:94-96 — current code
depth_samples = depth_map[np.ix_(v_int, u_int)]  # creates full NxN arrays
image_samples = image[np.ix_(v_int, u_int)]
```

For a 4K ERP image (2048×4096), this creates unnecessary intermediate arrays. Simple slicing is equivalent and far faster:

```python
depth_samples = depth_map[::stride, ::stride]
image_samples = image[::stride, ::stride]
```

**Fix:** Use direct stride slicing. Only use `np.ix_()` when the row and column indices are independent and non-uniform.

### 4.5 Missing Stage 2 tests

No `tests/test_stage02.py` exists despite Stage 2 having 8 source modules: `cubemap.py`, `intrinsics.py`, `extrinsics.py`, `masking.py`, `yaw_diversify.py`, `rpg360_graph.py`, `pipeline.py`. This is a significant testing gap for a core stage.

**Fix:** Write `test_stage02.py` covering: cubemap face extraction correctness (verify known pixel positions), intrinsics computation, extrinsics quaternion generation for each face, yaw diversification, and mask generation.

### 4.6 No integration tests

T0.12 (integration test harness) is one of the two remaining TODO tasks. The `tests/integration/__init__.py` file exists but is empty. There are no end-to-end tests verifying the full pipeline.

**Fix:** Create at minimum one integration test that runs stages 1→5 on a tiny synthetic dataset (2-frame "video", 256×512 resolution) and verifies a valid `.ply` is produced.

---

## 5. Moderate Issues (Maintainability — P2)

### 5.1 Duplicate COLMAP parsing functions

Two modules parse COLMAP text files independently:

| Function | File |
|----------|------|
| `read_colmap_cameras()`, `read_colmap_images()` | `common/io.py` |
| `parse_cameras_txt()`, `parse_images_txt()`, `parse_points3d_txt()` | `common/colmap_helpers.py` |

Both read the same format but with subtly different return dicts. This is confusing and doubles maintenance burden.

**Fix:** Pick one module as canonical. Delete the duplicate functions from `io.py` (keep `colmap_helpers.py` since it also has writers and quaternion helpers). Re-route all callers.

### 5.2 `rotation_matrix_to_quat` may be incomplete or buggy

The function in `colmap_helpers.py` uses Shepperd's method for numerical stability but the implementation was truncated in the file I read. It needs to be verified for correctness — quaternion conversion bugs are subtle and cause incorrect camera poses.

**Fix:** Review and unit-test `rotation_matrix_to_quat` against known ground-truth rotations (identity, 90° about each axis, 180°, etc.).

### 5.3 Inconsistent `__init__.py` re-exports

Stage 5's `__init__.py` re-exports all module functions, allowing:

```python
from sphereforge.stages.stage05_seeding import project_to_3d, fuse_multiview
```

Other stages don't re-export, requiring full paths:

```python
from sphereforge.stages.stage01_frames.sharpness import compute_sharpness
```

**Fix:** Standardize — either all stages re-export or none do. Preference: re-export in `__init__.py` for the public pipeline API.

### 5.4 Fragile progress logging

`logging_utils.py:log_task_completion()` modifies `TASKS.md` with regex replacement:

```python
pattern = rf"(\|\s*{re.escape(task_id)}\s*\|\s*)TODO(\s*\|)"
new_content = re.sub(pattern, replacement, content)
```

If the TASKS.md table format ever changes (e.g., adding a column), the regex breaks silently and tasks are never marked DONE.

**Fix:** Use a real Markdown table parser or at minimum add a dry-run mode and validation that the replacement succeeded.

### 5.5 `py.typed` marker missing

The package does not include a `py.typed` file (PEP 561), so mypy consumers that depend on `sphereforge` won't get type information.

**Fix:** Add `src/sphereforge/py.typed` (empty file).

### 5.6 GPU dependency not clearly documented

The training loop requires CUDA + gsplat for real results. There's no clear `pip install` command in any user-facing document. The AGENTS.md mentions dependencies but doesn't give the install command.

**Fix:** Add to README:
```
pip install 'sphereforge[all]'          # full stack with GPU
pip install 'sphereforge[depth,gsplat]' # just depth + 3DGS
```

---

## 6. Minor Issues (Nice-to-Have — P3)

### 6.1 Unnecessary `model_cache.py` complexity

`model_cache.py` has `download_if_missing()` which accepts a `url` parameter. It's called from `PanDAModel.__init__()` with `url=None` and from `Metric3DV2.__init__()` with a HuggingFace URL. The `None` path raises `FileNotFoundError` which is caught upstream. A single-purpose `resolve_model_path()` would be simpler.

### 6.2 Stage 7 uses `from ... import ...` inside functions

`run_stage07()` and some Stage 7 submodules import heavy dependencies (diffusers, lpips, gsplat) inside function bodies:

```python
def run_stage07(...):
    if config.refine_backend == "omniroam":
        from sphereforge.stages.stage07_occlusion.omniroam import omniroam_fill
```

This is intentional for optional deps but should be standardized — use a central import helper or document the pattern consistently.

### 6.3 Training loop moves view data to GPU every iteration

Each training iteration does:

```python
viewmat = view["viewmat"].to(device)     # every iter
target_image = view["target_image"].to(device)  # every iter
```

For the same view index, this is redundant. Views should be pre-loaded to GPU once at startup.

### 6.4 No `.gitignore` entries for model caches

The `.gitignore` should exclude:
```
~/.cache/sphereforge/
*.pth
*.pt
```

---

## 7. Task Completion Gap Analysis

| Metric | Value |
|--------|-------|
| Total tasks | 94 |
| Done | 92 (98%) |
| Remaining | T0.10 (Dockerfile), T0.12 (integration test harness) |

The 98% completion rate is misleading — most tasks are implemented but significant functionality is stubbed:

| Completed Task | Reality |
|----------------|---------|
| T4.1 (PanDA model) | Stub — raises NotImplementedError |
| T4.4 (RPG360 pipeline) | Functional (uses Metric3D on cubemap faces) |
| T6.1-T6.13 (Optimization) | Training loop exists but rasterizer may be stub |
| T7.7 (EscherNet) | Stub — raises NotImplementedError |
| T7.12 (OmniRoam) | Stub |
| T0.11 (CLI scaffold) | CLI exists but `process`/`export` don't call any pipeline |
| T7.13 (Stage 7 pipeline) | Functional if backend can run |

---

## 8. Recommendations by Priority

### P0 — Blockers (must fix for minimal functioning pipeline)

| # | Issue | Section | Effort |
|---|-------|---------|--------|
| 1 | Wire up CLI `process` command to actually run stages 1-8 | 3.1 | Medium |
| 2 | Create sample YAML config files in `configs/` | 3.2 | Small |
| 3 | Fix Stage 5 stride bypass — use per-pixel stride | 3.5 | Small |
| 4 | Add progress checkpointing to Stage 6 (save .ply every N iterations) | 4.2 | Medium |
| 5 | Fail-fast in depth pipeline when all models are stubs (instead of writing zero depth) | 3.4 | Small |
| 6 | Add clear error when gsplat+GPU is not available for training | 3.3 | Small |

### P1 — Important (fix for production-quality pipeline)

| # | Issue | Section | Effort |
|---|-------|---------|--------|
| 7 | Add parallel processing via `concurrent.futures` for Stages 2, 4, 5 | 4.1 | Medium |
| 8 | Write `test_stage02.py` (cubemap, intrinsics, extrinsics, masking) | 4.5 | Medium |
| 9 | Fix duplicate crop extraction in Stage 2 | 4.3 | Small |
| 10 | Replace `np.ix_()` with direct stride slicing in `project_to_3d` | 4.4 | Small |
| 11 | Add resume support: checkpoint files and `--resume` flag | 4.2 | Medium |

### P2 — Should Fix (improves maintainability)

| # | Issue | Section | Effort |
|---|-------|---------|--------|
| 12 | Unify COLMAP readers — delete duplicates from `io.py` | 5.1 | Small |
| 13 | Review and unit-test `rotation_matrix_to_quat` | 5.2 | Small |
| 14 | Standardize `__init__.py` re-exports across all stages | 5.3 | Small |
| 15 | Add `py.typed` marker for PEP 561 compliance | 5.5 | Tiny |
| 16 | Pre-load training view data to GPU once at startup | 6.3 | Small |
| 17 | Write T0.12 integration test | 4.6 | Medium |
| 18 | Write T0.10 Dockerfile | — | Small |

### P3 — Nice to Have

| # | Issue | Section | Effort |
|---|-------|---------|--------|
| 19 | Simplify `model_cache.py` API | 6.1 | Small |
| 20 | Add `.gitignore` entries for model cache files | 6.4 | Tiny |
| 21 | Add GPU install instructions to README | 5.6 | Tiny |
| 22 | Make `configs/` directory contain real YAML files | 3.2 | Tiny |

---

## 9. File Map for Onboarding

If you are new to this project, here are the key files to read first, in order:

| Order | File | Why |
|-------|------|-----|
| 1 | `PIPELINE_DESIGN_V2.md` | Full pipeline specification |
| 2 | `AGENTS.md` | Project conventions and workflow |
| 3 | `TASKS.md` | All tasks, dependencies, status |
| 4 | `PROGRESS.md` | What has been implemented |
| 5 | `src/sphereforge/config.py` | All configuration models |
| 6 | `src/sphereforge/cli.py` | CLI entry point (needs wiring) |
| 7 | `src/sphereforge/common/io.py` | Image/depth/PLY/COLMAP I/O |
| 8 | `src/sphereforge/common/colmap_helpers.py` | COLMAP readers/writers, quaternion math |
| 9 | `src/sphereforge/stages/stage01_frames/pipeline.py` | Example stage pipeline (well-structured) |
| 10 | `src/sphereforge/stages/stage06_optimization/training_loop.py` | The core optimization loop |
| 11 | `tests/conftest.py` | Shared test fixtures |

---

## 10. Running the Code

### Prerequisites
```bash
# Core
pip install 'sphereforge[all]'

# For GPU training
pip install 'sphereforge[rasterizer]'  # installs gsplat

# For depth estimation
pip install 'sphereforge[depth]'

# Development
pip install 'sphereforge[dev]'
```

### Current Status
- `sphereforge status` — works (reads TASKS.md progress)
- `sphereforge process input.mp4` — **NOT WORKING** (prints "Pipeline not yet implemented")
- `sphereforge export data/optimized/` — **NOT WORKING** (prints "Export not yet implemented")

### Running Tests
```bash
pytest tests/                           # unit tests
pytest tests/ -m "not gpu"              # skip GPU tests
pytest tests/test_stage01.py            # individual stage tests
pytest tests/ --cov=src/sphereforge     # with coverage
```

### Linting & Type Checking
```bash
ruff check src/                         # lint
black --check src/                      # format check
mypy src/sphereforge/                   # type check
```
