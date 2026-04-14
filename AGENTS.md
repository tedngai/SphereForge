# SphereForge — Agent Instructions

You are working on **SphereForge**, a multi-stage pipeline that transforms 360° camera footage into high-quality 3D Gaussian Splat scenes. This document tells you how to work on this project.

---

## Project Overview

SphereForge is a Python project implementing the pipeline described in `PIPELINE_DESIGN_V2.md` (in the parent directory). It has 8 stages plus cross-cutting infrastructure. Every piece of work is tracked as a task in `TASKS.md`, and completion is logged in `PROGRESS.md`.

## Key Files

| File | Purpose |
|------|---------|
| `TASKS.md` | Complete task list with IDs, descriptions, dependencies, and status |
| `PROGRESS.md` | Log of completed tasks with timestamps, outputs, and notes |
| `PIPELINE_DESIGN_V2.md` | Full pipeline specification (parent directory) |
| `src/sphereforge/` | Python package root |
| `src/sphereforge/stages/` | One subdirectory per pipeline stage |
| `src/sphereforge/common/` | Shared utilities (I/O, config, depth helpers) |
| `tests/` | Unit and integration tests |
| `configs/` | YAML/JSON config files for each stage |

## How to Work on a Task

1. **Find your task** in `TASKS.md`. Your assignment will reference a task ID like `T2.3`.
2. **Check prerequisites** in `PROGRESS.md`. Every task lists dependencies — confirm those tasks are marked DONE before you start.
3. **Read the spec** in `PIPELINE_DESIGN_V2.md`. Find the stage and step that corresponds to your task. The design doc has the full technical details.
4. **Write code** following the project conventions below.
5. **Write tests** for your code. Every task should have at least one test.
6. **Log completion** in `PROGRESS.md`. Append an entry with:
   - Task ID
   - Timestamp (ISO 8601)
   - What you implemented (brief)
   - Files created/modified
   - Any deviations from the spec or issues encountered
7. **Update task status** in `TASKS.md`. Change the task status from `TODO` to `DONE`.

## Project Conventions

### Python Style
- Python 3.11+ (uses `X | Y` union syntax, `match` statements, etc.)
- Type hints on all public functions
- Docstrings on all public functions (Google style)
- `ruff` for linting, `black` for formatting, `isort` for imports
- Line length: 100

### Project Structure
```
src/sphereforge/
├── __init__.py
├── cli.py                  # CLI entry point
├── config.py               # Pydantic config models
├── common/
│   ├── __init__.py
│   ├── io.py               # Image/depth/PLY I/O
│   ├── colmap_helpers.py    # COLMAP format readers/writers
│   ├── depth_utils.py       # Depth alignment, NCC, cross-validation
│   └── metrics.py           # PSNR, SSIM, LPIPS helpers
├── stages/
│   ├── __init__.py
│   ├── stage01_frames/      # Video ingestion & frame selection
│   ├── stage02_cubemap/     # Equirect→Cubemap + COLMAP prep
│   ├── stage03_sfm/         # COLMAP SfM
│   ├── stage04_depth/       # Dense depth estimation
│   ├── stage05_seeding/     # Initial Gaussian seeding
│   ├── stage06_optimization/ # Multi-view optimization
│   ├── stage07_occlusion/   # Occlusion recovery
│   └── stage08_export/      # Post-processing & export
├── models/                  # Model wrappers (PanDA, RPG360, etc.)
│   ├── panda.py
│   ├── metric3d.py
│   ├── eschernet.py
│   └── marigold.py
└── logging_utils.py         # Progress logging to PROGRESS.md
```

### Config System
- All stage configs are Pydantic models in `src/sphereforge/config.py`
- Default values match those in `PIPELINE_DESIGN_V2.md`
- Configs can be overridden via YAML files in `configs/` or CLI arguments
- Every stage function accepts a config object as its first argument

### Logging
- Use Python `logging` module (not print statements)
- Logger name: `sphereforge.stageXX.description` (e.g., `sphereforge.stage02.cubemap`)
- Log levels: DEBUG for per-frame detail, INFO for stage-level progress, WARNING for degraded quality, ERROR for failures

### Testing
- `pytest` with fixtures in `tests/conftest.py`
- One test file per module: `test_stage02_cubemap.py`, etc.
- Use small synthetic test data (not real 360 footage)
- Integration tests go in `tests/integration/`
- Every task should produce at least one test

### Dependencies
- Core: `numpy`, `opencv-python`, `torch`, `pydantic`, `click`
- Stage-specific dependencies are isolated — don't add heavy deps to core
- GPU code uses `torch.cuda` with CPU fallbacks where possible
- COLMAP is called via CLI (subprocess), not Python bindings

### Git Conventions
- Branch per task: `feat/T2.3-camera-intrinsics`
- Commit messages: `feat(stage02): implement camera intrinsics computation`
- One PR per task — keep them small and reviewable

## Task Dependency Rules

- **Never start a task whose dependencies are not DONE.** Check `PROGRESS.md`.
- **If you discover a dependency that isn't listed**, add it to `TASKS.md` and note it in your PR.
- **If a task is blocked** by an unresolved dependency, mark it `BLOCKED` in `TASKS.md` with a note explaining why.
- **Cross-stage dependencies** are real — Stage 5 depends on outputs from Stages 3 and 4. Within a stage, follow the dependency order in `TASKS.md`.

## Pipeline Data Flow

Every stage reads from a shared data directory and writes to it:

```
data/
├── raw/              # Input video files
├── frames/           # Stage 1 output: selected equirect frames
├── cubemaps/         # Stage 2 output: perspective crops + masks
├── colmap/           # Stage 3 output: sparse model + camera poses
├── depth/            # Stage 4 output: metric depth maps
├── gaussians/        # Stage 5 output: initial .ply
├── optimized/        # Stage 6 output: optimized .ply with SH
├── refined/          # Stage 7 output: hole-filled .ply
└── export/           # Stage 8 output: final PLY/SOG/SPZ/HTML
```

When implementing a stage, read inputs from the previous stage's directory and write outputs to your stage's directory. Use `src/sphereforge/common/io.py` helpers for consistent I/O.

## Model Weights

Model weights are not stored in the repo. They are downloaded on first use to a configurable cache directory (default: `~/.cache/sphereforge/models/`). Each model wrapper in `src/sphereforge/models/` handles its own download logic.

## Validation Checklist

Before marking a task DONE, verify:
- [ ] Code compiles and passes `ruff check`
- [ ] Unit tests pass (`pytest tests/`)
- [ ] Type hints on all public functions
- [ ] Docstrings on all public functions
- [ ] Config defaults match `PIPELINE_DESIGN_V2.md`
- [ ] Logging uses `sphereforge.stageXX` loggers
- [ ] Data I/O uses `common/io.py` helpers
- [ ] Progress logged in `PROGRESS.md`
- [ ] Task status updated in `TASKS.md`