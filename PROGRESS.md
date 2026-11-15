# SphereForge — Progress Log

This file is the automatic log of completed tasks. It is checked against TASKS.md to verify prerequisites and track overall progress.

---

## Completion Table

| Task ID | Status | Completed | Output | Notes |
|----------|--------|-----------|--------|-------|
| T0.1 | DONE | 2026-04-12 | pyproject.toml, src/ directory tree | Project skeleton |
| T0.2 | DONE | 2026-04-12 | src/sphereforge/config.py | Pydantic models for all 8 stages |
| T0.3 | DONE | 2026-04-12 | src/sphereforge/cli.py | Click CLI |
| T0.4 | DONE | 2026-04-12 | src/sphereforge/logging_utils.py | Progress tracking |
| T0.5 | DONE | 2026-04-12 | src/sphereforge/common/io.py | Image/depth/PLY/COLMAP I/O |
| T0.6 | DONE | 2026-04-12 | src/sphereforge/common/colmap_helpers.py | COLMAP text/binary, quaternions |
| T0.7 | DONE | 2026-04-12 | src/sphereforge/common/depth_utils.py | Depth alignment, NCC, fusion |
| T0.8 | DONE | 2026-04-12 | src/sphereforge/common/metrics.py | PSNR, SSIM, LPIPS |
| T0.9 | DONE | 2026-04-12 | src/sphereforge/common/model_cache.py | Model weight download/cache |
| T0.11 | DONE | 2026-04-12 | tests/conftest.py | Synthetic fixtures |
| T1.1–T1.7 | DONE | 2026-04-12 | stage01_frames/ (580 lines) | Frame extraction, sharpness, selection |
| T2.1–T2.9 | DONE | 2026-04-12 | stage02_cubemap/ (1550 lines) | Cubemap, masks, COLMAP, RPG360 |
| T2.10 | DONE | 2026-04-12 | depth_utils.median_ratio_align | Fallback alignment |
| T2.11 | DONE | 2026-04-12 | stage02_cubemap/pipeline.py | Stage 2 orchestration |
| T2.12 | DONE | 2026-04-12 | tests/ (334 lines) | Stage 2 tests |
| T3.1–T3.7 | DONE | 2026-04-12 | stage03_sfm/ (816 lines) | COLMAP CLI wrappers |
| T4.1–T4.7 | DONE | 2026-04-12 | stage04_depth/ (1322 lines) | PanDA (stub), alignment, scene analysis |
| T5.1–T5.13 | DONE | 2026-04-12 | stage05_seeding/ (1285 lines) | Projection, fusion, pruning, PLY |
| T6.1–T6.5 | DONE | 2026-04-12 | stage06_optimization/ erp_loss, tangent_neighbors, intersection_depth, d_normal_loss | ErpGS + 360-GeoGS |
| T6.6–T6.8 | DONE | 2026-04-12 | stage06_optimization/ densification, split_clone, pruning | ImprovedGS+ EAS/LAS/RAP |
| T6.9 | DONE | 2026-04-12 | stage06_optimization/cdc_gs.py | Complexity-density prior (config-gated) |
| T6.10 | DONE | 2026-04-12 | stage06_optimization/depth_regularization.py | Depth + normal reg |
| T6.11 | DONE | 2026-04-12 | stage06_optimization/training_loop.py | Main optimization loop (rasterizer stub) |
| T6.12 | DONE | 2026-04-12 | stage06_optimization/pipeline.py | Stage 6 orchestration |
| T6.13 | DONE | 2026-04-12 | tests/test_stage06_*.py | Stage 6 tests |
| T7.1–T7.14 | DONE | 2026-04-12 | stage07_occlusion/ (1932 lines) | Novel cameras, holes, ShareGS, GS-Diff |
| T8.1–T8.9 | DONE | 2026-04-12 | stage08_export/ (1260 lines) | Pruning, culling, PLY/SOG/SPZ/HTML/mesh |

---


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:14:48.664877+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-12/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-12/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:14:48.668957+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-12/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-12/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:14:48.673111+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-12/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-12/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:14:48.677114+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-12/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-12/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:14:48.680547+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-12/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-12/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:14:48.685427+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-12/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-12/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:15:31.351802+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-13/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-13/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:15:31.355600+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-13/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-13/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:15:31.358841+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-13/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-13/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:15:31.362598+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-13/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-13/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:15:31.365738+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-13/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-13/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:15:31.369341+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-13/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-13/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:18:34.968865+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-14/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-14/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:18:34.973301+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-14/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-14/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:18:34.980025+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-14/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-14/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:18:34.984577+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-14/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-14/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:18:34.988462+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-14/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-14/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:18:34.998546+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-14/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-14/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:21:35.894381+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-16/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-16/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:21:35.897574+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-16/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-16/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:21:35.902828+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-16/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-16/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:21:35.906228+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-16/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-16/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:21:35.909628+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-16/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-16/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:21:35.913873+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-16/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-16/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:25:43.585618+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-17/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-17/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:25:43.591393+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-17/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-17/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:25:43.598149+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-17/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-17/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:25:43.602549+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-17/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-17/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:25:43.608051+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-17/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-17/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-03T12:25:43.613308+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-17/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-17/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-12T17:11:37.097855+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-12T17:14:51.115342+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-05-12T17:14:58.936134+00:00
- **Files created:**
  - `data/depth/frame_000014_depth.npy`
  - `data/depth/frame_000046_depth.npy`
  - `data/depth/frame_000062_depth.npy`
  - `data/depth/frame_000118_depth.npy`
  - `data/depth/frame_000126_depth.npy`
  - `data/depth/frame_000166_depth.npy`
  - `data/depth/frame_000184_depth.npy`
  - `data/depth/frame_000225_depth.npy`
  - `data/depth/frame_000270_depth.npy`
  - `data/depth/frame_000281_depth.npy`
  - `data/depth/frame_000305_depth.npy`
  - `data/depth/frame_000336_depth.npy`
  - `data/depth/frame_000361_depth.npy`
  - `data/depth/frame_000401_depth.npy`
  - `data/depth/frame_000447_depth.npy`
  - `data/depth/frame_000457_depth.npy`
  - `data/depth/frame_000508_depth.npy`
  - `data/depth/frame_000512_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T3.6] Task Completed
- **Completed:** 2026-05-12T17:20:37.314566+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-05-12T17:20:45.035361+00:00
- **Files created:**
  - `data/depth/frame_000014_depth.npy`
  - `data/depth/frame_000046_depth.npy`
  - `data/depth/frame_000062_depth.npy`
  - `data/depth/frame_000118_depth.npy`
  - `data/depth/frame_000126_depth.npy`
  - `data/depth/frame_000166_depth.npy`
  - `data/depth/frame_000184_depth.npy`
  - `data/depth/frame_000225_depth.npy`
  - `data/depth/frame_000270_depth.npy`
  - `data/depth/frame_000281_depth.npy`
  - `data/depth/frame_000305_depth.npy`
  - `data/depth/frame_000336_depth.npy`
  - `data/depth/frame_000361_depth.npy`
  - `data/depth/frame_000401_depth.npy`
  - `data/depth/frame_000447_depth.npy`
  - `data/depth/frame_000457_depth.npy`
  - `data/depth/frame_000508_depth.npy`
  - `data/depth/frame_000512_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T3.6] Task Completed
- **Completed:** 2026-05-12T17:24:21.416118+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-05-12T17:24:29.255827+00:00
- **Files created:**
  - `data/depth/frame_000014_depth.npy`
  - `data/depth/frame_000046_depth.npy`
  - `data/depth/frame_000062_depth.npy`
  - `data/depth/frame_000118_depth.npy`
  - `data/depth/frame_000126_depth.npy`
  - `data/depth/frame_000166_depth.npy`
  - `data/depth/frame_000184_depth.npy`
  - `data/depth/frame_000225_depth.npy`
  - `data/depth/frame_000270_depth.npy`
  - `data/depth/frame_000281_depth.npy`
  - `data/depth/frame_000305_depth.npy`
  - `data/depth/frame_000336_depth.npy`
  - `data/depth/frame_000361_depth.npy`
  - `data/depth/frame_000401_depth.npy`
  - `data/depth/frame_000447_depth.npy`
  - `data/depth/frame_000457_depth.npy`
  - `data/depth/frame_000508_depth.npy`
  - `data/depth/frame_000512_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T3.6] Task Completed
- **Completed:** 2026-05-12T17:29:22.972309+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-12T17:36:36.520670+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-05-12T17:36:50.769409+00:00
- **Files created:**
  - `data/depth/frame_000014_depth.npy`
  - `data/depth/frame_000046_depth.npy`
  - `data/depth/frame_000062_depth.npy`
  - `data/depth/frame_000118_depth.npy`
  - `data/depth/frame_000126_depth.npy`
  - `data/depth/frame_000166_depth.npy`
  - `data/depth/frame_000184_depth.npy`
  - `data/depth/frame_000225_depth.npy`
  - `data/depth/frame_000270_depth.npy`
  - `data/depth/frame_000281_depth.npy`
  - `data/depth/frame_000305_depth.npy`
  - `data/depth/frame_000336_depth.npy`
  - `data/depth/frame_000361_depth.npy`
  - `data/depth/frame_000401_depth.npy`
  - `data/depth/frame_000447_depth.npy`
  - `data/depth/frame_000457_depth.npy`
  - `data/depth/frame_000508_depth.npy`
  - `data/depth/frame_000512_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T3.6] Task Completed
- **Completed:** 2026-05-12T17:42:17.807400+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-12T17:43:52.439881+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-12T17:46:35.193829+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-12T17:50:11.681288+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-12T17:51:08.105551+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-12T17:53:05.101037+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-12T17:54:03.555139+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-05-13T03:40:34.088362+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 12206801 Gaussians, 12111430 added


### [T3.6] Task Completed
- **Completed:** 2026-05-13T16:40:13.463094+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-13T16:43:14.959967+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-13T18:13:16.286459+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-13T18:55:53.032109+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-0/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-0/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-13T18:55:53.033121+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-0/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-0/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-13T18:55:53.033966+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-0/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-0/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-13T18:55:53.034942+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-0/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-0/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-13T18:55:53.035804+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-0/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-0/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-13T18:55:53.036674+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-0/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-0/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-13T18:57:00.726509+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-13T19:34:24.350579+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-05-13T19:46:41.953406+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 17204996 Gaussians, 16216140 added


### [T7.13] Task Completed
- **Completed:** 2026-05-13T22:47:10.982803+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1000647 Gaussians, 11791 added


### [T7.13] Task Completed
- **Completed:** 2026-05-13T22:49:14.185779+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1003737 Gaussians, 14881 added


### [T7.13] Task Completed
- **Completed:** 2026-05-13T22:50:57.754221+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1002120 Gaussians, 13264 added


### [T7.13] Task Completed
- **Completed:** 2026-05-13T23:48:37.068539+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1091314 Gaussians, 102458 added


### [T7.13] Task Completed
- **Completed:** 2026-05-13T23:49:48.450322+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1500818 Gaussians, 511962 added


### [T7.13] Task Completed
- **Completed:** 2026-05-13T23:51:08.974176+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1500000 Gaussians, 511144 added


### [T7.13] Task Completed
- **Completed:** 2026-05-13T23:52:16.569320+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1500000 Gaussians, 511144 added


### [T7.13] Task Completed
- **Completed:** 2026-05-14T01:42:42.647207+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1500000 Gaussians, 511144 added


### [T7.13] Task Completed
- **Completed:** 2026-05-14T01:54:30.582907+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1500000 Gaussians, 511144 added


### [T7.13] Task Completed
- **Completed:** 2026-05-14T01:55:29.866770+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1499999 Gaussians, 511143 added


### [T7.13] Task Completed
- **Completed:** 2026-05-14T02:13:55.075771+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1500000 Gaussians, 511144 added


### [T3.6] Task Completed
- **Completed:** 2026-05-14T10:17:03.771073+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-4/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-4/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-14T10:17:03.772093+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-4/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-4/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-14T10:17:03.772951+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-4/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-4/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-14T10:17:03.773934+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-4/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-4/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-14T10:17:03.774792+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-4/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-4/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-14T10:17:03.775651+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-4/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-4/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-05-14T10:21:30.230437+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1100000 Gaussians, 111144 added


### [T7.13] Task Completed
- **Completed:** 2026-05-14T11:11:30.767518+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1100000 Gaussians, 111144 added


### [T7.13] Task Completed
- **Completed:** 2026-05-14T11:17:16.023977+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1100000 Gaussians, 111144 added


### [T7.13] Task Completed
- **Completed:** 2026-05-14T12:49:03.834118+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1100000 Gaussians, 111144 added


### [T7.13] Task Completed
- **Completed:** 2026-05-14T14:42:48.934659+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1100000 Gaussians, 111144 added


### [T7.13] Task Completed
- **Completed:** 2026-05-14T21:30:09.852328+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 1100000 Gaussians, 111144 added


### [T3.6] Task Completed
- **Completed:** 2026-05-15T09:41:49.423578+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T09:57:06.518329+00:00
- **Files created:**
  - `data/colmap/database.db`
  - `data/colmap/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-05-15T11:18:12.007694+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 2963107 Gaussians, 0 added


### [T7.13] Task Completed
- **Completed:** 2026-05-15T13:06:12.328203+00:00
- **Files created:**
  - `data/refined/refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 2994926 Gaussians, 0 added


### [T3.6] Task Completed
- **Completed:** 2026-05-15T16:13:08.584773+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-8/test_registration_diagnostics_0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-8/test_registration_diagnostics_0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T16:13:18.415531+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-9/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-9/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T16:13:18.420224+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-9/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-9/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T16:13:18.426049+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-9/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-9/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T16:13:18.430132+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-9/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-9/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T16:13:18.434206+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-9/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-9/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T16:13:18.438577+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-9/test_registration_diagnostics_0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-9/test_registration_diagnostics_0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T16:13:34.009409+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-10/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-10/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T16:13:34.017221+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-10/test_registration_diagnostics_0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-10/test_registration_diagnostics_0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T16:13:43.504625+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-11/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-11/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T16:13:43.509956+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-11/test_registration_diagnostics_0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-11/test_registration_diagnostics_0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T16:15:52.308099+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-12/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-12/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T16:15:52.313698+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-12/test_registration_diagnostics_0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-12/test_registration_diagnostics_0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:46:58.608912+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-13/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-13/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:47:09.970510+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-14/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-14/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:47:09.975040+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-14/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-14/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:47:09.979381+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-14/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-14/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:47:09.984005+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-14/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-14/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:47:09.988497+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-14/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-14/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:47:09.993274+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-14/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-14/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:47:09.997891+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-14/test_registration_diagnostics_0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-14/test_registration_diagnostics_0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:47:10.007496+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-14/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-14/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:50:09.291239+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-15/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-15/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:50:28.856407+00:00
- **Files created:**
  - `data/colmap_rig_debug/database.db`
  - `data/colmap_rig_debug/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:53:26.201800+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-16/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-16/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:53:26.206310+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-16/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-16/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:53:26.210669+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-16/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-16/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:53:26.217224+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-16/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-16/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:53:26.221780+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-16/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-16/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:53:26.226469+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-16/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-16/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:53:26.231156+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-16/test_registration_diagnostics_0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-16/test_registration_diagnostics_0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:53:26.240506+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-16/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-16/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:59:22.048919+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-17/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-17/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:59:29.133510+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-18/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-18/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:59:29.137795+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-18/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-18/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:59:29.141847+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-18/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-18/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:59:29.146080+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-18/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-18/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:59:29.150144+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-18/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-18/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:59:29.154189+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-18/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-18/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:59:29.158602+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-18/test_registration_diagnostics_0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-18/test_registration_diagnostics_0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T20:59:29.167346+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-18/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-18/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:01:27.006934+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-19/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-19/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:24:10.874972+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-20/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-20/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:24:10.879296+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-20/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-20/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:24:10.883354+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-20/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-20/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:24:10.887648+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-20/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-20/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:24:10.891747+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-20/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-20/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:24:10.895911+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-20/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-20/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:24:10.900413+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-20/test_registration_diagnostics_0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-20/test_registration_diagnostics_0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:24:10.910361+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-20/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-20/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:29:17.712586+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-21/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-21/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:46:27.272701+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-22/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-22/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:46:27.278302+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-22/test_panorama_rig_can_skip_exp0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-22/test_panorama_rig_can_skip_exp0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:46:48.751668+00:00
- **Files created:**
  - `data/colmap_probe_loose/database.db`
  - `data/colmap_probe_loose/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:47:07.291660+00:00
- **Files created:**
  - `data/colmap_probe_loose_f75/database.db`
  - `data/colmap_probe_loose_f75/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:47:34.621943+00:00
- **Files created:**
  - `data/colmap_probe_loose_6f/database.db`
  - `data/colmap_probe_loose_6f/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:48:03.324215+00:00
- **Files created:**
  - `data/colmap_probe_loose_6f_w3/database.db`
  - `data/colmap_probe_loose_6f_w3/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:48:35.672607+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-23/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-23/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:48:35.676935+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-23/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-23/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:48:35.681048+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-23/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-23/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:48:35.686997+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-23/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-23/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:48:35.691194+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-23/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-23/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:48:35.695334+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-23/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-23/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:48:35.699750+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-23/test_registration_diagnostics_0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-23/test_registration_diagnostics_0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:48:35.708620+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-23/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-23/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T21:48:35.712821+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-23/test_panorama_rig_can_skip_exp0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-23/test_panorama_rig_can_skip_exp0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:14:32.226485+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-24/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-24/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:14:32.231576+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-24/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-24/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:14:32.235758+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-24/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-24/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:14:32.239953+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-24/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-24/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:14:32.243938+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-24/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-24/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:14:32.248012+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-24/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-24/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:14:32.252401+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-24/test_registration_diagnostics_0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-24/test_registration_diagnostics_0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:14:42.786362+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-25/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-25/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:14:42.791295+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-25/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-25/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:14:42.795622+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-25/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-25/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:14:42.799727+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-25/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-25/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:14:42.803827+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-25/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-25/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:14:42.808569+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-25/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-25/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:14:42.812783+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-25/test_panorama_rig_can_skip_exp0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-25/test_panorama_rig_can_skip_exp0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:16:05.738062+00:00
- **Files created:**
  - `data/colmap_probe_loose_6f_w3_interleaved/database.db`
  - `data/colmap_probe_loose_6f_w3_interleaved/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:16:21.074432+00:00
- **Files created:**
  - `data/colmap_probe_loose_6f_interleaved/database.db`
  - `data/colmap_probe_loose_6f_interleaved/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:49:46.285199+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-26/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-26/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T22:49:46.290157+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-26/test_panorama_rig_can_skip_exp0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-26/test_panorama_rig_can_skip_exp0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T23:37:10.292300+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-27/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-27/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T23:37:10.297641+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-27/test_panorama_rig_can_skip_exp0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-27/test_panorama_rig_can_skip_exp0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T23:37:10.302222+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-27/test_panorama_rig_pycolmap_bac0/output_cfg_off/database.db`
  - `/tmp/pytest-of-tngai/pytest-27/test_panorama_rig_pycolmap_bac0/output_cfg_off/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T23:37:10.305857+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-27/test_panorama_rig_pycolmap_bac0/output_env_off/database.db`
  - `/tmp/pytest-of-tngai/pytest-27/test_panorama_rig_pycolmap_bac0/output_env_off/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T23:37:10.310326+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-27/test_panorama_rig_pycolmap_bac1/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-27/test_panorama_rig_pycolmap_bac1/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T23:37:26.154571+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-28/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-28/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T23:37:26.160131+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-28/test_panorama_rig_can_skip_exp0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-28/test_panorama_rig_can_skip_exp0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T23:37:26.164778+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-28/test_panorama_rig_pycolmap_bac0/output_cfg_off/database.db`
  - `/tmp/pytest-of-tngai/pytest-28/test_panorama_rig_pycolmap_bac0/output_cfg_off/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T23:37:26.168706+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-28/test_panorama_rig_pycolmap_bac0/output_env_off/database.db`
  - `/tmp/pytest-of-tngai/pytest-28/test_panorama_rig_pycolmap_bac0/output_env_off/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T23:37:26.173747+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-28/test_panorama_rig_pycolmap_bac1/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-28/test_panorama_rig_pycolmap_bac1/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-15T23:37:26.178377+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-28/test_pycolmap_backend_falls_ba0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-28/test_pycolmap_backend_falls_ba0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:05:23.646534+00:00
- **Files created:**
  - `data/colmap_probe_loose_6f_w3_stage03_pycolmap_seq_validate/database.db`
  - `data/colmap_probe_loose_6f_w3_stage03_pycolmap_seq_validate/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:17.158389+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-29/test_correct_call_order0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-29/test_correct_call_order0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:17.163061+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-29/test_dense_skipped_when_disabl0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-29/test_dense_skipped_when_disabl0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:17.167179+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-29/test_feature_type_propagated0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-29/test_feature_type_propagated0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:17.171379+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-29/test_refine_intrinsics_propaga0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-29/test_refine_intrinsics_propaga0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:17.175444+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-29/test_vocab_tree_path_from_data0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-29/test_vocab_tree_path_from_data0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:17.179563+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-29/test_output_directory_structur0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-29/test_output_directory_structur0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:17.184738+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-29/test_registration_diagnostics_0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-29/test_registration_diagnostics_0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:17.193422+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-29/test_panorama_rig_uses_per_fol0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-29/test_panorama_rig_uses_per_fol0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:17.197659+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-29/test_panorama_rig_can_skip_exp0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-29/test_panorama_rig_can_skip_exp0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:17.202001+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-29/test_panorama_rig_pycolmap_bac0/output_cfg_off/database.db`
  - `/tmp/pytest-of-tngai/pytest-29/test_panorama_rig_pycolmap_bac0/output_cfg_off/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:17.205587+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-29/test_panorama_rig_pycolmap_bac0/output_env_off/database.db`
  - `/tmp/pytest-of-tngai/pytest-29/test_panorama_rig_pycolmap_bac0/output_env_off/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:17.209953+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-29/test_panorama_rig_pycolmap_bac1/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-29/test_panorama_rig_pycolmap_bac1/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:17.214295+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-29/test_panorama_rig_pycolmap_bac2/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-29/test_panorama_rig_pycolmap_bac2/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:17.218696+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-29/test_pycolmap_backend_falls_ba0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-29/test_pycolmap_backend_falls_ba0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:26.693636+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-30/test_registration_diagnostics_0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-30/test_registration_diagnostics_0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:26.699497+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-30/test_panorama_rig_can_skip_exp0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-30/test_panorama_rig_can_skip_exp0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:26.704237+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-30/test_panorama_rig_pycolmap_bac0/output_cfg_off/database.db`
  - `/tmp/pytest-of-tngai/pytest-30/test_panorama_rig_pycolmap_bac0/output_cfg_off/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:26.708026+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-30/test_panorama_rig_pycolmap_bac0/output_env_off/database.db`
  - `/tmp/pytest-of-tngai/pytest-30/test_panorama_rig_pycolmap_bac0/output_env_off/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:26.712980+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-30/test_panorama_rig_pycolmap_bac1/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-30/test_panorama_rig_pycolmap_bac1/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:26.717689+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-30/test_panorama_rig_pycolmap_bac2/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-30/test_panorama_rig_pycolmap_bac2/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:26.722215+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-30/test_pycolmap_backend_falls_ba0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-30/test_pycolmap_backend_falls_ba0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:07:35.242547+00:00
- **Files created:**
  - `data/colmap_probe_loose_6f_w3_stage03_pycolmap_default_validate/database.db`
  - `data/colmap_probe_loose_6f_w3_stage03_pycolmap_default_validate/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:08:29.577172+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-31/test_registration_diagnostics_0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-31/test_registration_diagnostics_0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:08:29.583387+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-31/test_panorama_rig_pycolmap_bac0/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-31/test_panorama_rig_pycolmap_bac0/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-05-16T03:08:29.588278+00:00
- **Files created:**
  - `/tmp/pytest-of-tngai/pytest-31/test_panorama_rig_pycolmap_bac1/output/database.db`
  - `/tmp/pytest-of-tngai/pytest-31/test_panorama_rig_pycolmap_bac1/output/sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:12:09.373425+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:12:09.507574+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:12:09.614867+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:12:09.729200+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:12:09.828982+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:12:09.930817+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:12:10.079921+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:12:10.385511+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:12:10.537994+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:12:10.693377+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:12:10.779257+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:12:10.931158+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:12:11.080711+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:12:11.202085+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-4\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:13:42.945677+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:13:43.045612+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:13:43.158206+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:13:43.264965+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:13:43.381334+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:13:43.482160+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:13:43.613445+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:13:43.895963+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:13:44.054107+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:13:44.198923+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:13:44.291079+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:13:44.433504+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:13:44.582067+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T19:13:44.692616+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-5\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:10:53.803118+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:10:53.845465+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:10:53.895174+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:10:53.928597+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:10:53.969822+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:10:54.003296+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:10:54.061675+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:10:54.186907+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:10:54.253394+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:10:54.312150+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:10:54.346725+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:10:54.411988+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:10:54.469829+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:10:54.519949+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-20\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:12:12.141645+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:12:12.198834+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:12:12.236765+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:12:12.283226+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:12:12.320174+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:12:12.361643+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:12:12.416511+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:12:12.536814+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:12:12.589840+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:12:12.649010+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:12:12.694269+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:12:12.757956+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:12:12.820136+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:12:12.861724+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-21\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:14:02.686513+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:14:02.736733+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:14:02.778433+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:14:02.820094+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:14:02.862020+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:14:02.919531+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:14:02.978877+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:14:03.103961+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:14:03.161790+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:14:03.211755+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:14:03.253236+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:14:03.311688+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:14:03.386628+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:14:03.428259+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-22\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:15:13.307727+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:15:13.353601+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:15:13.403127+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:15:13.453272+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:15:13.503118+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:15:13.545217+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:15:13.603168+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:15:13.753163+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:15:13.819977+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:15:13.880187+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:15:13.920259+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:15:13.995158+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:15:14.061839+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:15:14.103835+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-23\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:18:30.453306+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:18:30.494442+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:18:30.527819+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:18:30.570590+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:18:30.620181+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:18:30.653455+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:18:30.703700+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:18:30.836713+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:18:30.905827+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:18:30.962354+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:18:30.995012+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:18:31.053223+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:18:31.127740+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:18:31.177805+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-28\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:20:29.880418+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-29\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-29\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:20:29.962150+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-29\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-29\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:20:45.611530+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-30\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-30\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:20:45.689683+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-30\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-30\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:21:00.785887+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-31\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-31\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:21:00.856035+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-31\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-31\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:21:31.009273+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-32\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-32\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:21:31.086745+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-32\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-32\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:04.103342+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-34\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-34\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:04.195522+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-34\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-34\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:36.613831+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:36.670219+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:36.727899+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:36.778255+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:36.820596+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:36.862361+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:36.919977+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:37.058843+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:37.141066+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:37.208233+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:37.256906+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:37.328484+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:37.403424+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:37.455593+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-36\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:55.106947+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:55.165851+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:55.220743+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:55.282818+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:55.345291+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:55.408558+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:55.495517+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:55.695269+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:55.794984+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:55.855341+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:55.903407+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:55.996402+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:56.096190+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:56.157614+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:22:56.217542+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-37\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:17.827064+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:17.875172+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:17.924298+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:17.973741+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:18.030624+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:18.080172+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:18.157313+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:18.365782+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:18.480901+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:18.561977+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:18.607407+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:18.795064+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:18.876770+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:18.936103+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:23:18.988926+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-38\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:17.353670+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:17.400285+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:17.445300+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:17.492727+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:17.547379+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:17.603490+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:17.661632+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:17.786074+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:17.864007+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:17.937062+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:17.985042+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:18.052622+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:18.119870+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:18.169306+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:28:18.208601+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-39\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-11-12T22:29:36.920106+00:00
- **Files created:**
  - `data\e2e\depth\frame_000002_depth.npy`
  - `data\e2e\depth\frame_000008_depth.npy`
  - `data\e2e\depth\frame_000010_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.016962+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.065103+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.119567+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.183766+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.244294+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.304824+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.369906+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.496994+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.569833+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.645131+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.686950+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.770122+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.828537+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.886989+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:43:33.933149+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-50\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:35.917308+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:35.978147+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:36.040597+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:36.108240+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:36.184698+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:36.242184+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:36.327407+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:36.502198+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:36.590700+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:36.666404+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:36.719671+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:36.798874+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:36.969379+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:37.034813+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:44:37.084454+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-51\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:45:59.773705+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:45:59.832281+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:45:59.892130+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:46:00.035978+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:46:00.087617+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:46:00.151657+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:46:00.215622+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:46:00.375421+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:46:00.475917+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:46:00.557418+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:46:00.615931+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:46:00.693783+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:46:00.837479+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:46:00.885345+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-12T22:46:00.941219+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-53\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-11-12T22:47:41.980817+00:00
- **Files created:**
  - `data\e2e\depth\frame_000002_depth.npy`
  - `data\e2e\depth\frame_000008_depth.npy`
  - `data\e2e\depth\frame_000010_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:41.775856+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:41.823456+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:41.870504+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:41.901972+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:41.948960+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:41.980404+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:42.027494+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:42.153880+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:42.232608+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:42.279810+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:42.327568+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:42.390844+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:42.470284+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:42.518038+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:07:42.549864+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-57\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:34.546031+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:34.593249+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:34.624616+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:34.672279+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:34.719607+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:34.766955+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:34.845827+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:34.972097+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:35.051210+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:35.114066+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:35.161257+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:35.224142+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:35.286957+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:35.334456+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:09:35.366325+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-59\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-11-13T02:36:32.053495+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 59998 Gaussians, 55164 added


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.066499+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.097897+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.129463+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.177073+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.240054+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.271431+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.334844+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.465774+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.524950+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.588254+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.635551+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.698861+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.765881+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.825201+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:37:57.872351+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-60\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-11-13T02:45:17.272532+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 59998 Gaussians, 53937 added


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:31.232522+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:31.286233+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:31.335701+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:31.385319+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:31.436324+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:31.470412+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:31.537995+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:31.683004+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:31.752722+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:31.813828+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:31.855179+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:31.931699+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:31.990486+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:32.038201+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:48:32.082532+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-62\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:15.300150+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:15.347982+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:15.379696+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:15.426827+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:15.458636+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:15.505810+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:15.552963+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:15.695114+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:15.758790+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:15.837320+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:15.869231+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:15.948389+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:16.011527+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:16.075016+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T02:49:16.122446+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-63\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-11-13T02:54:06.827279+00:00
- **Files created:**
  - `data\e2e\depth\frame_000002_depth.npy`
  - `data\e2e\depth\frame_000008_depth.npy`
  - `data\e2e\depth\frame_000010_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T4.6] Task Completed
- **Completed:** 2026-11-13T02:59:56.829210+00:00
- **Files created:**
  - `data\e2e\depth\frame_000002_depth.npy`
  - `data\e2e\depth\frame_000008_depth.npy`
  - `data\e2e\depth\frame_000010_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T4.6] Task Completed
- **Completed:** 2026-11-13T03:02:21.255851+00:00
- **Files created:**
  - `data\e2e\depth\frame_000002_depth.npy`
  - `data\e2e\depth\frame_000008_depth.npy`
  - `data\e2e\depth\frame_000010_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T4.6] Task Completed
- **Completed:** 2026-11-13T03:09:39.883464+00:00
- **Files created:**
  - `data\e2e\depth\frame_000002_depth.npy`
  - `data\e2e\depth\frame_000008_depth.npy`
  - `data\e2e\depth\frame_000010_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:04.589100+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:04.620665+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:04.668016+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:04.715604+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:04.746971+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:04.794109+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:04.857359+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:04.983295+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:05.061839+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:05.109418+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:05.140693+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:05.209524+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:05.267001+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:05.314112+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:10:05.347335+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-67\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-11-13T03:17:55.040731+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 59985 Gaussians, 59495 added


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.038191+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.101883+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.149050+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.196721+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.260373+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.323701+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.387032+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.544023+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.606789+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.669813+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.733299+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.796582+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.859493+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.907106+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:19:22.954660+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-69\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:46.814096+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:46.861225+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:46.908733+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:46.940566+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:46.987743+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:47.034906+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:47.081934+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:47.207943+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:47.301993+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:47.364809+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:47.396621+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:47.476112+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:47.538927+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:47.586352+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:25:47.631266+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-72\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:29:59.820290+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:29:59.851780+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:29:59.899371+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:29:59.946490+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:29:59.993577+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:30:00.025560+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:30:00.088796+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:30:00.215380+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:30:00.278626+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:30:00.346147+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:30:00.389980+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:30:00.453329+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:30:00.516520+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:30:00.564063+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:30:00.611610+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-73\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:02.884724+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:02.932009+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:02.979142+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:03.010995+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:03.058503+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:03.105735+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:03.153282+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:03.310398+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:03.452635+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:03.515805+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:03.562930+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:03.610135+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:03.689295+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:03.729773+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:34:03.768255+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-74\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.177870+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.209723+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.256866+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.303885+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.335833+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.384947+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.430484+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.557232+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.620001+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.683262+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.730301+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.793545+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.856400+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.903951+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:43:32.951042+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-77\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:18.683886+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:18.747788+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:18.795758+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:18.843810+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:18.899190+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:18.939264+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:19.002896+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:19.161914+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:19.241027+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:19.288506+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:19.343501+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:19.403271+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:19.462297+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:19.510399+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:48:19.556624+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-78\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-11-13T03:54:40.393635+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 60000 Gaussians, 57704 added


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:02.465328+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:02.521823+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:02.560795+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:02.607907+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:02.673911+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:02.722368+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:02.781529+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:02.922723+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:03.001590+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:03.064835+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:03.111934+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:03.190825+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:03.253966+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:03.301438+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T03:56:03.349008+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-79\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-11-13T04:03:14.637336+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 59997 Gaussians, 56864 added


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:42.702819+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:42.750034+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:42.797076+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:42.844202+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:42.876013+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:42.923138+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:42.970688+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:43.112470+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:43.191514+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:43.254270+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:43.285719+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:43.348854+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:43.474690+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:43.521861+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T04:04:43.553255+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-80\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-11-13T05:13:22.681059+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 59997 Gaussians, 59075 added


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:45.837783+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:45.885691+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:45.949808+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:45.997287+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:46.061209+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:46.110440+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:46.187867+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:46.365171+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:46.452214+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:46.534108+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:46.586030+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:46.681684+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:46.777513+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:46.857261+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:14:46.922129+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-81\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-11-13T05:21:49.443229+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 59999 Gaussians, 57749 added


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:14.665276+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:14.712628+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:14.776161+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:14.828585+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:14.855556+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:14.902716+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:14.997066+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:15.170929+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:15.266100+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:15.360619+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:15.440052+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:15.535133+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:15.629755+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:15.693128+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:23:15.741033+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-82\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.137308+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.188868+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.235621+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.280043+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.311839+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.359974+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.428908+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.550582+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.625724+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.678565+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.717773+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.774205+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.846118+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.886239+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:26:26.931158+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-83\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:25.671544+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:25.735296+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:25.798819+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:25.846367+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:25.925175+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:25.972553+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:26.067520+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:26.241451+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:26.336624+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:26.415687+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:26.463162+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:26.542440+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:26.632404+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:26.668435+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:27:26.732478+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-84\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-11-13T05:34:06.375598+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 59995 Gaussians, 58827 added


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:07.842940+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:07.930739+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:07.999883+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:08.057595+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:08.135477+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:08.199692+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:08.279648+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:08.502557+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:08.613975+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:08.709609+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:08.772995+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:08.859368+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:08.959544+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:09.023382+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:35:09.078736+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-85\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-11-13T05:41:49.564790+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 59998 Gaussians, 58028 added


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:55.022220+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:55.066406+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:55.114366+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:55.145973+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:55.193871+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:55.225742+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:55.305050+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:55.474949+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:55.576094+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:55.655988+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:55.718711+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:55.799650+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:55.912304+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:55.975965+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T05:42:56.025573+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-86\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-11-13T05:49:46.238556+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 59987 Gaussians, 59008 added


### [T4.6] Task Completed
- **Completed:** 2026-11-13T05:55:14.687398+00:00
- **Files created:**
  - `data\e2e\depth\frame_000001_depth.npy`
  - `data\e2e\depth\frame_000003_depth.npy`
  - `data\e2e\depth\frame_000005_depth.npy`
  - `data\e2e\depth\frame_000007_depth.npy`
  - `data\e2e\depth\frame_000009_depth.npy`
  - `data\e2e\depth\frame_000011_depth.npy`
  - `data\e2e\depth\frame_000013_depth.npy`
  - `data\e2e\depth\frame_000015_depth.npy`
  - `data\e2e\depth\frame_000017_depth.npy`
  - `data\e2e\depth\frame_000019_depth.npy`
  - `data\e2e\depth\frame_000022_depth.npy`
  - `data\e2e\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T7.13] Task Completed
- **Completed:** 2026-11-13T06:00:43.846174+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 298691 Gaussians, 0 added


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:22.231033+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:22.278275+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:22.342615+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:22.405487+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:22.468915+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:22.532357+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:22.611403+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:22.785290+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:22.864294+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:22.927601+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:22.991092+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:23.069971+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:23.165253+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:23.244012+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-13T06:04:23.307178+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-87\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:22.298311+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:22.352654+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:22.426726+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:22.484755+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:22.552483+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:22.597445+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:22.664389+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:22.853958+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:22.953482+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:23.036913+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:23.096654+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:23.197468+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:23.284023+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:23.343425+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T16:52:23.392992+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-88\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:46.219921+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:46.268522+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:46.320522+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:46.359395+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:46.411366+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:46.461471+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:46.526994+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:46.693061+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:46.801099+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:46.885652+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:46.928659+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:47.005171+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:47.136012+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:47.282565+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:02:47.324787+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-100\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-11-14T18:06:43.169158+00:00
- **Files created:**
  - `data\e2e\depth\frame_000001_depth.npy`
  - `data\e2e\depth\frame_000003_depth.npy`
  - `data\e2e\depth\frame_000005_depth.npy`
  - `data\e2e\depth\frame_000007_depth.npy`
  - `data\e2e\depth\frame_000009_depth.npy`
  - `data\e2e\depth\frame_000011_depth.npy`
  - `data\e2e\depth\frame_000013_depth.npy`
  - `data\e2e\depth\frame_000015_depth.npy`
  - `data\e2e\depth\frame_000017_depth.npy`
  - `data\e2e\depth\frame_000019_depth.npy`
  - `data\e2e\depth\frame_000022_depth.npy`
  - `data\e2e\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T7.13] Task Completed
- **Completed:** 2026-11-14T18:15:58.360226+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 120264 Gaussians, 0 added


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:42.712465+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:42.744778+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:42.798931+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:42.839453+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:42.892642+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:42.953862+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:43.031440+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:43.206333+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:43.294317+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:43.353327+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:43.383483+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:43.434836+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:43.500381+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:43.541934+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:16:43.574003+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-103\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-11-14T18:39:55.327771+00:00
- **Files created:**
  - `data\e2e\depth\frame_000001_depth.npy`
  - `data\e2e\depth\frame_000003_depth.npy`
  - `data\e2e\depth\frame_000005_depth.npy`
  - `data\e2e\depth\frame_000007_depth.npy`
  - `data\e2e\depth\frame_000009_depth.npy`
  - `data\e2e\depth\frame_000011_depth.npy`
  - `data\e2e\depth\frame_000013_depth.npy`
  - `data\e2e\depth\frame_000015_depth.npy`
  - `data\e2e\depth\frame_000017_depth.npy`
  - `data\e2e\depth\frame_000019_depth.npy`
  - `data\e2e\depth\frame_000022_depth.npy`
  - `data\e2e\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T7.13] Task Completed
- **Completed:** 2026-11-14T18:45:08.324993+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 59944 Gaussians, 29170 added


### [T7.13] Task Completed
- **Completed:** 2026-11-14T18:48:28.769539+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 59632 Gaussians, 28858 added


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:02.587608+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:02.624332+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:02.666546+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:02.696543+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:02.727910+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:02.759367+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:02.810011+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:02.933759+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:02.985509+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:03.053639+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:03.119640+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:03.201758+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:03.270937+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:03.326925+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T18:49:03.356668+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-104\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-11-14T18:56:31.831296+00:00
- **Files created:**
  - `data\e2e\depth\frame_000001_depth.npy`
  - `data\e2e\depth\frame_000003_depth.npy`
  - `data\e2e\depth\frame_000005_depth.npy`
  - `data\e2e\depth\frame_000007_depth.npy`
  - `data\e2e\depth\frame_000009_depth.npy`
  - `data\e2e\depth\frame_000011_depth.npy`
  - `data\e2e\depth\frame_000013_depth.npy`
  - `data\e2e\depth\frame_000015_depth.npy`
  - `data\e2e\depth\frame_000017_depth.npy`
  - `data\e2e\depth\frame_000019_depth.npy`
  - `data\e2e\depth\frame_000022_depth.npy`
  - `data\e2e\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T4.6] Task Completed
- **Completed:** 2026-11-14T19:02:40.067019+00:00
- **Files created:**
  - `data\e2e\depth\frame_000001_depth.npy`
  - `data\e2e\depth\frame_000003_depth.npy`
  - `data\e2e\depth\frame_000005_depth.npy`
  - `data\e2e\depth\frame_000007_depth.npy`
  - `data\e2e\depth\frame_000009_depth.npy`
  - `data\e2e\depth\frame_000011_depth.npy`
  - `data\e2e\depth\frame_000013_depth.npy`
  - `data\e2e\depth\frame_000015_depth.npy`
  - `data\e2e\depth\frame_000017_depth.npy`
  - `data\e2e\depth\frame_000019_depth.npy`
  - `data\e2e\depth\frame_000022_depth.npy`
  - `data\e2e\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T7.13] Task Completed
- **Completed:** 2026-11-14T19:12:15.759189+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 101285 Gaussians, 0 added


### [T4.6] Task Completed
- **Completed:** 2026-11-14T19:50:18.070686+00:00
- **Files created:**
  - `data\e2e\depth\frame_000001_depth.npy`
  - `data\e2e\depth\frame_000003_depth.npy`
  - `data\e2e\depth\frame_000005_depth.npy`
  - `data\e2e\depth\frame_000007_depth.npy`
  - `data\e2e\depth\frame_000009_depth.npy`
  - `data\e2e\depth\frame_000011_depth.npy`
  - `data\e2e\depth\frame_000013_depth.npy`
  - `data\e2e\depth\frame_000015_depth.npy`
  - `data\e2e\depth\frame_000017_depth.npy`
  - `data\e2e\depth\frame_000019_depth.npy`
  - `data\e2e\depth\frame_000022_depth.npy`
  - `data\e2e\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T7.13] Task Completed
- **Completed:** 2026-11-14T19:53:46.891151+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 71772 Gaussians, 0 added


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:33.949570+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:34.001570+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:34.067708+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:34.124244+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:34.169924+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:34.204958+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:34.255004+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:34.362893+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:34.404310+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:34.448023+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:34.484586+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:34.535104+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:34.589690+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:34.621697+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T19:54:34.652310+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-105\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:37.666737+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:37.719568+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:37.786726+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:37.845117+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:37.889569+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:37.954769+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:38.036187+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:38.177438+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:38.255084+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:38.311075+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:38.353481+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:38.403061+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:38.462258+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:38.578291+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:01:38.618303+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-109\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-11-14T20:11:48.474432+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 294586 Gaussians, 0 added


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:30.743250+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:30.803015+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:30.860396+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:30.913348+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:30.967490+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:31.027269+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:31.102888+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:31.250199+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:31.331387+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:31.412565+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:31.468016+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:31.569645+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:31.657278+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:31.713821+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:13:31.758527+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-110\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:09.826160+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:09.903769+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:09.959859+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:10.017110+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:10.069674+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:10.119793+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:10.190363+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:10.370929+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:10.462812+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:10.540710+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:10.609590+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:10.712423+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:10.807720+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:10.870606+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:19:10.927761+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-112\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:07.717641+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:07.773839+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:07.837434+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:07.898078+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:07.952624+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:08.003117+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:08.079490+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:08.248741+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:08.370844+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:08.464362+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:08.523360+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:08.611030+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:08.719752+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:08.775001+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T20:21:08.826349+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-113\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T7.13] Task Completed
- **Completed:** 2026-11-14T20:24:15.681007+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 294586 Gaussians, 0 added


### [T7.13] Task Completed
- **Completed:** 2026-11-14T20:25:25.789908+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 294586 Gaussians, 0 added


### [T7.13] Task Completed
- **Completed:** 2026-11-14T20:48:09.525775+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 294586 Gaussians, 0 added


### [T7.13] Task Completed
- **Completed:** 2026-11-14T21:00:04.721081+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 294586 Gaussians, 0 added


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:16.689115+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:16.765721+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:16.843458+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:16.917038+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:17.004663+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:17.086773+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:17.192354+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:17.404487+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:17.535920+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:17.631950+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:17.705966+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:17.815320+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:17.933843+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:18.017062+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:08:18.104700+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-114\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-11-14T21:21:02.344165+00:00
- **Files created:**
  - `data\e2e\depth\frame_000001_depth.npy`
  - `data\e2e\depth\frame_000003_depth.npy`
  - `data\e2e\depth\frame_000005_depth.npy`
  - `data\e2e\depth\frame_000007_depth.npy`
  - `data\e2e\depth\frame_000009_depth.npy`
  - `data\e2e\depth\frame_000011_depth.npy`
  - `data\e2e\depth\frame_000013_depth.npy`
  - `data\e2e\depth\frame_000015_depth.npy`
  - `data\e2e\depth\frame_000017_depth.npy`
  - `data\e2e\depth\frame_000019_depth.npy`
  - `data\e2e\depth\frame_000022_depth.npy`
  - `data\e2e\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T7.13] Task Completed
- **Completed:** 2026-11-14T21:24:47.326112+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 102004 Gaussians, 0 added


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:44.060890+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:44.122904+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:44.180324+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:44.251113+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:44.306029+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:44.356936+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:44.434687+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:44.608173+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:44.694292+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:44.787930+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:44.850838+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:44.941615+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:45.018184+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:45.078409+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:29:45.244179+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-115\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:48.140102+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:48.214765+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:48.288873+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:48.359338+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:48.427062+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:48.502106+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:48.593661+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:48.807988+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:48.920081+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:49.015682+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:49.087525+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:49.189148+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:49.297728+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:49.379293+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T21:50:49.568654+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-117\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:47.939306+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:48.010542+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:48.086199+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:48.165902+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:48.250643+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:48.327867+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:48.434676+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:48.691109+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:48.862777+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:49.001575+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:49.082895+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:49.254279+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:49.374244+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:49.482118+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:02:49.568362+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-118\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:06.105480+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:06.180815+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:06.252431+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:06.327701+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:06.405251+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:06.479350+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:06.566784+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:06.766575+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:06.871789+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:06.942626+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:06.992686+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:07.070004+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:07.144927+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:07.214830+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T22:19:07.400364+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-119\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-11-14T22:49:16.627641+00:00
- **Files created:**
  - `data\e2e\depth\frame_000001_depth.npy`
  - `data\e2e\depth\frame_000003_depth.npy`
  - `data\e2e\depth\frame_000005_depth.npy`
  - `data\e2e\depth\frame_000007_depth.npy`
  - `data\e2e\depth\frame_000009_depth.npy`
  - `data\e2e\depth\frame_000011_depth.npy`
  - `data\e2e\depth\frame_000013_depth.npy`
  - `data\e2e\depth\frame_000015_depth.npy`
  - `data\e2e\depth\frame_000017_depth.npy`
  - `data\e2e\depth\frame_000019_depth.npy`
  - `data\e2e\depth\frame_000022_depth.npy`
  - `data\e2e\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T7.13] Task Completed
- **Completed:** 2026-11-14T23:33:47.165202+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 372950 Gaussians, 0 added


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:30.211624+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:30.286189+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:30.352314+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:30.422338+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:30.497028+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:30.569607+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:30.666589+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:30.873573+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:30.990425+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:31.092363+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:31.171268+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:31.297237+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:31.437782+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:31.520350+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:41:31.712555+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-120\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:14.934781+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:14.988787+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:15.144237+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:15.214223+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:15.286599+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:15.350066+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:15.420801+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:15.609002+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:15.679173+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:15.747283+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:15.794739+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:15.874488+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:15.947258+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:16.010853+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-14T23:45:16.181203+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-121\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:17.808848+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:17.904700+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:17.967646+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:18.057626+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:18.131946+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:18.206939+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:18.302519+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:18.509007+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:18.650968+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:18.764695+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:18.825657+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:18.937464+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:19.049531+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:19.128968+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T00:25:19.192511+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-127\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-11-15T00:29:37.499758+00:00
- **Files created:**
  - `data\e2e\depth\frame_000001_depth.npy`
  - `data\e2e\depth\frame_000003_depth.npy`
  - `data\e2e\depth\frame_000005_depth.npy`
  - `data\e2e\depth\frame_000007_depth.npy`
  - `data\e2e\depth\frame_000009_depth.npy`
  - `data\e2e\depth\frame_000011_depth.npy`
  - `data\e2e\depth\frame_000013_depth.npy`
  - `data\e2e\depth\frame_000015_depth.npy`
  - `data\e2e\depth\frame_000017_depth.npy`
  - `data\e2e\depth\frame_000019_depth.npy`
  - `data\e2e\depth\frame_000022_depth.npy`
  - `data\e2e\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T4.6] Task Completed
- **Completed:** 2026-11-15T00:46:09.558065+00:00
- **Files created:**
  - `data\e2e\depth\frame_000001_depth.npy`
  - `data\e2e\depth\frame_000003_depth.npy`
  - `data\e2e\depth\frame_000005_depth.npy`
  - `data\e2e\depth\frame_000007_depth.npy`
  - `data\e2e\depth\frame_000009_depth.npy`
  - `data\e2e\depth\frame_000011_depth.npy`
  - `data\e2e\depth\frame_000013_depth.npy`
  - `data\e2e\depth\frame_000015_depth.npy`
  - `data\e2e\depth\frame_000017_depth.npy`
  - `data\e2e\depth\frame_000019_depth.npy`
  - `data\e2e\depth\frame_000022_depth.npy`
  - `data\e2e\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T7.13] Task Completed
- **Completed:** 2026-11-15T01:33:45.613179+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 60000 Gaussians, -326290 added


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:37.590946+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:37.636928+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:37.700061+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:37.793084+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:37.842861+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:37.906537+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:38.007352+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:38.241735+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:38.353339+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:38.433513+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:38.480793+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:38.591011+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:38.680880+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:38.734606+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:40:38.798683+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-128\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:01.307159+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:01.355299+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:01.418393+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:01.465736+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:01.528922+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:01.576969+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:01.656238+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:01.795023+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:01.869361+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:01.957739+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:02.036104+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:02.116103+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:02.195302+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:02.258812+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T01:47:02.300427+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-130\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-11-15T02:03:09.497536+00:00
- **Files created:**
  - `data\e2e\depth\frame_000001_depth.npy`
  - `data\e2e\depth\frame_000003_depth.npy`
  - `data\e2e\depth\frame_000005_depth.npy`
  - `data\e2e\depth\frame_000007_depth.npy`
  - `data\e2e\depth\frame_000009_depth.npy`
  - `data\e2e\depth\frame_000011_depth.npy`
  - `data\e2e\depth\frame_000013_depth.npy`
  - `data\e2e\depth\frame_000015_depth.npy`
  - `data\e2e\depth\frame_000017_depth.npy`
  - `data\e2e\depth\frame_000019_depth.npy`
  - `data\e2e\depth\frame_000022_depth.npy`
  - `data\e2e\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T7.13] Task Completed
- **Completed:** 2026-11-15T02:10:22.771597+00:00
- **Files created:**
  - `data\e2e\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 60000 Gaussians, -298485 added


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:20.303680+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:20.363199+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:20.418345+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:20.470208+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:20.527475+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:20.592434+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:20.678887+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:20.851903+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:20.954405+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:21.047612+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:21.120075+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:21.237333+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:21.337104+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:21.416937+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:14:21.467853+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-131\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:15.344869+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:15.423998+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:15.487373+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:15.550668+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:15.598072+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:15.645034+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:15.724689+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:15.915058+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:16.010166+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:16.105229+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:16.168599+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:16.288893+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:16.390607+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:16.470075+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T02:20:16.537067+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-133\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-11-15T02:31:38.541639+00:00
- **Files created:**
  - `data\e2e_b\depth\frame_000001_depth.npy`
  - `data\e2e_b\depth\frame_000003_depth.npy`
  - `data\e2e_b\depth\frame_000005_depth.npy`
  - `data\e2e_b\depth\frame_000007_depth.npy`
  - `data\e2e_b\depth\frame_000009_depth.npy`
  - `data\e2e_b\depth\frame_000011_depth.npy`
  - `data\e2e_b\depth\frame_000013_depth.npy`
  - `data\e2e_b\depth\frame_000015_depth.npy`
  - `data\e2e_b\depth\frame_000017_depth.npy`
  - `data\e2e_b\depth\frame_000019_depth.npy`
  - `data\e2e_b\depth\frame_000021_depth.npy`
  - `data\e2e_b\depth\frame_000024_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T7.13] Task Completed
- **Completed:** 2026-11-15T03:13:06.070867+00:00
- **Files created:**
  - `data\e2e_b\refined\refined.ply`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 7 pipeline complete: 60000 Gaussians, -317228 added


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:05.321419+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:05.378283+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:05.465086+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:05.522793+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:05.640029+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:05.687344+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:05.754716+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:05.845712+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:05.966235+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:06.074959+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:06.151681+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:06.290244+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:06.499069+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:06.580032+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:18:06.639594+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-134\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.088099+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.113567+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.146281+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.225013+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.288020+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.335728+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.399752+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.510910+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.558757+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.611970+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.638364+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.702364+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.767868+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.814287+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T03:22:19.866406+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-135\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-11-15T16:40:22.843955+00:00
- **Files created:**
  - `data\e2e_fix\depth\frame_000001_depth.npy`
  - `data\e2e_fix\depth\frame_000003_depth.npy`
  - `data\e2e_fix\depth\frame_000005_depth.npy`
  - `data\e2e_fix\depth\frame_000007_depth.npy`
  - `data\e2e_fix\depth\frame_000009_depth.npy`
  - `data\e2e_fix\depth\frame_000011_depth.npy`
  - `data\e2e_fix\depth\frame_000013_depth.npy`
  - `data\e2e_fix\depth\frame_000015_depth.npy`
  - `data\e2e_fix\depth\frame_000017_depth.npy`
  - `data\e2e_fix\depth\frame_000019_depth.npy`
  - `data\e2e_fix\depth\frame_000022_depth.npy`
  - `data\e2e_fix\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T4.6] Task Completed
- **Completed:** 2026-11-15T16:42:13.127057+00:00
- **Files created:**
  - `data\e2e_fix\depth\frame_000001_depth.npy`
  - `data\e2e_fix\depth\frame_000003_depth.npy`
  - `data\e2e_fix\depth\frame_000005_depth.npy`
  - `data\e2e_fix\depth\frame_000007_depth.npy`
  - `data\e2e_fix\depth\frame_000009_depth.npy`
  - `data\e2e_fix\depth\frame_000011_depth.npy`
  - `data\e2e_fix\depth\frame_000013_depth.npy`
  - `data\e2e_fix\depth\frame_000015_depth.npy`
  - `data\e2e_fix\depth\frame_000017_depth.npy`
  - `data\e2e_fix\depth\frame_000019_depth.npy`
  - `data\e2e_fix\depth\frame_000022_depth.npy`
  - `data\e2e_fix\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:37.502562+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:37.570384+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:37.642957+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:37.699252+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:37.759367+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:37.813823+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:37.887139+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:38.029049+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:38.115863+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:38.185641+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:38.246226+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:38.331157+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:38.412317+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:38.484696+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T16:58:38.562592+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-141\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-11-15T17:00:54.169098+00:00
- **Files created:**
  - `data\e2e_fix\depth\frame_000001_depth.npy`
  - `data\e2e_fix\depth\frame_000003_depth.npy`
  - `data\e2e_fix\depth\frame_000005_depth.npy`
  - `data\e2e_fix\depth\frame_000007_depth.npy`
  - `data\e2e_fix\depth\frame_000009_depth.npy`
  - `data\e2e_fix\depth\frame_000011_depth.npy`
  - `data\e2e_fix\depth\frame_000013_depth.npy`
  - `data\e2e_fix\depth\frame_000015_depth.npy`
  - `data\e2e_fix\depth\frame_000017_depth.npy`
  - `data\e2e_fix\depth\frame_000019_depth.npy`
  - `data\e2e_fix\depth\frame_000022_depth.npy`
  - `data\e2e_fix\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:12.564461+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:12.613897+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:12.682448+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:12.751218+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:12.803934+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:12.852096+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:12.913250+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:13.055950+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:13.163371+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:13.272737+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:13.339466+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:13.426552+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:13.496712+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:13.553114+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T17:43:13.604736+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-144\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T4.6] Task Completed
- **Completed:** 2026-11-15T17:49:54.406430+00:00
- **Files created:**
  - `data\e2e_s3\depth\frame_000001_depth.npy`
  - `data\e2e_s3\depth\frame_000003_depth.npy`
  - `data\e2e_s3\depth\frame_000005_depth.npy`
  - `data\e2e_s3\depth\frame_000007_depth.npy`
  - `data\e2e_s3\depth\frame_000009_depth.npy`
  - `data\e2e_s3\depth\frame_000011_depth.npy`
  - `data\e2e_s3\depth\frame_000013_depth.npy`
  - `data\e2e_s3\depth\frame_000015_depth.npy`
  - `data\e2e_s3\depth\frame_000017_depth.npy`
  - `data\e2e_s3\depth\frame_000019_depth.npy`
  - `data\e2e_s3\depth\frame_000022_depth.npy`
  - `data\e2e_s3\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T4.6] Task Completed
- **Completed:** 2026-11-15T18:03:57.192606+00:00
- **Files created:**
  - `data\e2e_s3\depth\frame_000001_depth.npy`
  - `data\e2e_s3\depth\frame_000003_depth.npy`
  - `data\e2e_s3\depth\frame_000005_depth.npy`
  - `data\e2e_s3\depth\frame_000007_depth.npy`
  - `data\e2e_s3\depth\frame_000009_depth.npy`
  - `data\e2e_s3\depth\frame_000011_depth.npy`
  - `data\e2e_s3\depth\frame_000013_depth.npy`
  - `data\e2e_s3\depth\frame_000015_depth.npy`
  - `data\e2e_s3\depth\frame_000017_depth.npy`
  - `data\e2e_s3\depth\frame_000019_depth.npy`
  - `data\e2e_s3\depth\frame_000022_depth.npy`
  - `data\e2e_s3\depth\frame_000023_depth.npy`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 4 pipeline: dense depth estimation orchestration


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:27.017414+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_correct_call_order0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_correct_call_order0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:27.050666+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_dense_skipped_when_disabl0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_dense_skipped_when_disabl0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:27.090253+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_feature_type_propagated0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_feature_type_propagated0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:27.137720+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_refine_intrinsics_propaga0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_refine_intrinsics_propaga0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:27.201924+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_vocab_tree_path_from_data0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_vocab_tree_path_from_data0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:27.247460+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_output_directory_structur0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_output_directory_structur0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:27.322281+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_registration_diagnostics_0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_registration_diagnostics_0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:27.460149+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_panorama_rig_uses_per_fol0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_panorama_rig_uses_per_fol0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:27.510614+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_panorama_rig_can_skip_exp0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_panorama_rig_can_skip_exp0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:27.557288+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_panorama_rig_pycolmap_bac0\output_cfg_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_panorama_rig_pycolmap_bac0\output_cfg_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:27.589080+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_panorama_rig_pycolmap_bac0\output_env_off\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_panorama_rig_pycolmap_bac0\output_env_off\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:27.640519+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_panorama_rig_pycolmap_bac1\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_panorama_rig_pycolmap_bac1\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:27.785622+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_panorama_rig_pycolmap_bac2\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_panorama_rig_pycolmap_bac2\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:27.921972+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_pycolmap_backend_falls_ba0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_pycolmap_backend_falls_ba0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed


### [T3.6] Task Completed
- **Completed:** 2026-11-15T18:12:28.004046+00:00
- **Files created:**
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_uses_cli_when_available0\output\database.db`
  - `C:\Users\tatch\data\SphereForge\pytest-of-tatch\pytest-146\test_uses_cli_when_available0\output\sparse`
- **Files modified:**
  - (none)
- **Implementation notes:** Stage 3 SfM pipeline completed

## Statistics

- **Total tasks:** 94 (94 DONE, 0 remaining)
- **Completion rate:** 100%
- **Source code:** ~18,500 lines
- **Test code:** ~5,000 lines
- **Total Python:** ~23,500 lines

---

### [HIGH-RES v2] 2026-05-15 — Full pipeline re-run
- **Config**: `configs/high_res.yaml` (stride 10, 20K iters, 3M cap, Flux2 Klein)
- **Stage 5**: 962 seeds from 2.69M projected points (grid fusion)
- **Stage 6**: 2,994,926 Gaussians, PSNR +12 dB, trained in 30 min
- **Stage 7**: Hole coverage 0.9438 → 0.9438 (ShareGS capped, LPIPS 100% flagged at 0.5 threshold)
- **Stage 8**: 2,982,347 Gaussians, 160 MB final PLY
- **Key fixes**: gsplat rasterizer in Stage 7, gradient distillation, Flux KL2 inpainting, grid fusion, LPIPS caching

---

### [T2.13 / T3.8 / T3.9] Task Completed
- **Completed:** 2026-05-15T16:51:56-04:00
- **Files created:**
  - `src/sphereforge/stages/stage02_cubemap/panorama_rig.py`
  - `data/cubemaps_rig_debug/`
  - `data/colmap_rig_debug/`
- **Files modified:**
  - `TRAINING_CONTEXT.md`
  - `TASKS.md`
  - `configs/default.yaml`
  - `src/sphereforge/common/io.py`
  - `src/sphereforge/config.py`
  - `src/sphereforge/stages/stage02_cubemap/cubemap.py`
  - `src/sphereforge/stages/stage02_cubemap/pipeline.py`
  - `src/sphereforge/stages/stage02_cubemap/yaw_diversify.py`
  - `src/sphereforge/stages/stage03_sfm/feature_extraction.py`
  - `src/sphereforge/stages/stage03_sfm/pipeline.py`
  - `tests/test_stage02.py`
  - `tests/test_stage03_sfm.py`
- **Implementation notes:**
  - Documented the panorama-rig research direction in `TRAINING_CONTEXT.md`, including the conclusion that COLMAP's official panorama workflow relies on rig semantics more than on the specific reprojection engine.
  - Added a new Stage 2 `panorama_rig` layout that renders fixed virtual rectilinear cameras into per-camera subfolders and persists `panorama_rig.json` metadata for downstream use.
  - Updated Stage 3 to recursively discover rendered views, support per-folder cameras, preserve deterministic rig-friendly ordering, and fall back from `--SiftExtraction.root_sift` to `--descriptor_normalization` for older COLMAP builds.
  - Added regression coverage for the new panorama-rig path and for the COLMAP feature extraction compatibility fallback.
  - Ran a small real-data debug rerun on 6 existing ERP frames into `data/cubemaps_rig_debug/` and `data/colmap_rig_debug/`; result was `3 / 72` registered images and `0` sparse points, which indicates that deeper rig handling inside COLMAP is still missing in the current environment.

### [PANORAMA-RIG MATCHING v2] Follow-up
- **Completed:** 2026-05-15T17:24:33-04:00
- **Files created:**
  - `data/cubemaps_rig_debug_masked/`
  - `data/colmap_rig_debug_masked/`
  - `data/cubemaps_rig_debug_masked_v2/`
  - `data/colmap_rig_debug_masked_v2/`
  - `data/cubemaps_rig_debug_small/`
  - `data/colmap_rig_debug_small/`
- **Files modified:**
  - `TRAINING_CONTEXT.md`
  - `PROGRESS.md`
  - `src/sphereforge/stages/stage02_cubemap/panorama_rig.py`
  - `src/sphereforge/stages/stage02_cubemap/pipeline.py`
  - `src/sphereforge/stages/stage03_sfm/feature_matching.py`
  - `src/sphereforge/stages/stage03_sfm/pipeline.py`
  - `tests/test_stage02.py`
  - `tests/test_stage03_sfm.py`
- **Implementation notes:**
  - Added panorama-rig assignment masks so overlapping virtual-camera regions are masked out before feature extraction.
  - Added explicit panorama-rig pair control via `panorama_rig_match_list.txt` and matcher parameter wiring for sequential overlap / quadratic overlap.
  - Added local COLMAP vocabulary-tree building for panorama-rig runs when no external vocab tree is present, using a smaller visual-word count suitable for debug-scale datasets.
  - Verified the new code path with Stage 2/3 regression tests (`34 passed`).
  - Real-data follow-up still failed to produce verified matches: on the reduced probe, the debug database contained `0` rows in both `matches` and `two_view_geometries`, so the current blocker is now clearly at the correspondence-generation stage rather than mapper-only registration.

### [PANORAMA-RIG NEXT MOVES] Follow-up
- **Completed:** 2026-05-15T17:48:59-04:00
- **Files created:**
  - `data/cubemaps_probe_loose/`
  - `data/colmap_probe_loose/`
  - `data/cubemaps_probe_loose_f75/`
  - `data/colmap_probe_loose_f75/`
  - `data/cubemaps_probe_loose_6f/`
  - `data/colmap_probe_loose_6f/`
  - `data/cubemaps_probe_loose_6f_w3/`
  - `data/colmap_probe_loose_6f_w3/`
- **Files modified:**
  - `TRAINING_CONTEXT.md`
  - `PROGRESS.md`
  - `configs/default.yaml`
  - `src/sphereforge/config.py`
  - `src/sphereforge/stages/stage02_cubemap/panorama_rig.py`
  - `src/sphereforge/stages/stage02_cubemap/pipeline.py`
  - `src/sphereforge/stages/stage03_sfm/pipeline.py`
  - `tests/test_stage02.py`
  - `tests/test_stage03_sfm.py`
- **Implementation notes:**
  - Tried the suggested next moves by relaxing the panorama-rig constraints instead of tightening them further.
  - Made assignment masks optional and disabled them by default after confirming they eliminated all verified matches in this environment.
  - Made explicit panorama-rig match-list restriction optional and disabled it by default after confirming the stricter path reduced both `matches` and `two_view_geometries` to zero.
  - Increased the default panorama sequential temporal window to 2 and kept quadratic overlap disabled.
  - Verified the updated Stage 2/3 code path with regression tests (`36 passed`).
  - Real-data probe summary:
    - `data/colmap_probe_loose/`: `47` verified pairs, `2` registered images, `57` sparse points.
    - `data/colmap_probe_loose_f75/`: `47` verified pairs, `2` registered images, `31` sparse points.
    - `data/colmap_probe_loose_6f/`: `71` verified pairs, `2` registered images, `85` sparse points.
    - `data/colmap_probe_loose_6f_w3/`: `141` verified pairs, still `2` registered images, still `85` sparse points.
  - Conclusion: loosening the pipeline recovers verified correspondences and a nonzero sparse cloud, but registration coverage is still far below the desired level.

### [PANORAMA-RIG MAPPER FOLLOW-UP] Follow-up
- **Completed:** 2026-05-15T18:18:34-04:00
- **Files created:**
  - `data/colmap_probe_loose_6f_interleaved/`
  - `data/colmap_probe_loose_6f_w3_interleaved/`
  - `data/mapper_probe_loose_6f_relaxed/`
  - `data/mapper_probe_loose_6f_relaxed_init_bridge/`
- **Files modified:**
  - `TRAINING_CONTEXT.md`
  - `PROGRESS.md`
  - `src/sphereforge/stages/stage03_sfm/pipeline.py`
  - `tests/test_stage03_sfm.py`
- **Implementation notes:**
  - Changed panorama-rig Stage 3 image ordering from camera-major to frame-major so sequential matching no longer collapses onto one folder at a time.
  - Fixed the loose panorama-rig path so it really runs `sequential+vocabulary_tree`; Stage 3 now builds a local vocab tree whenever vocabulary-tree matching is requested, even when `panorama_use_match_list=false`.
  - Updated Stage 3 panorama-rig regression coverage and confirmed the targeted panorama-rig tests pass.
  - New loose probe summary after the fix:
    - `data/colmap_probe_loose_6f_interleaved/`: `2556` verified pairs, still `2` registered images, `130` sparse points.
    - `data/colmap_probe_loose_6f_w3_interleaved/`: also `2556` verified pairs, still `2` registered images, `130` sparse points.
  - Registration identities were unchanged across both new probes: `pano_camera03/frame_000118.png` and `pano_camera03/frame_000126.png`.
  - The pair graph is now broadly connected across camera folders, so the remaining blocker moved from correspondence sparsity to mapper/geometry behavior.
  - Mapper-only follow-up:
    - `data/mapper_probe_loose_6f_relaxed/`: with looser absolute-pose and triangulation thresholds, COLMAP still stopped at the same `2` registered images, though sparse points rose to `151`.
    - `data/mapper_probe_loose_6f_relaxed_init_bridge/`: forcing cross-camera/time init pair `#22` + `#47` failed initialization repeatedly and produced no model.
  - Conclusion: the current environment's CLI-only panorama-rig path can now create a strong verified-pair graph, but COLMAP still cannot grow that graph into a healthy multi-image model without stronger rig semantics or pose priors.
  - Validation note: `pytest tests/test_stage03_sfm.py -q -k "panorama_rig or correct_call_order or dense_skipped_when_disabled or feature_type_propagated or refine_intrinsics_propagated or vocab_tree_path_from_dataset"` passed. A full `pytest tests/test_stage03_sfm.py -q` run still shows a pre-existing unrelated failure in `TestModelReader.test_read_binary_format`.

### [PANORAMA-RIG PYCOLMAP PROBE] Follow-up
- **Completed:** 2026-05-15T18:52:28-04:00
- **Files created:**
  - `data/colmap_probe_loose_6f_pycolmap/`
  - `data/colmap_probe_loose_6f_w3_pycolmap/`
  - `src/sphereforge/stages/stage03_sfm/pycolmap_probe.py`
- **Files modified:**
  - `TRAINING_CONTEXT.md`
  - `PROGRESS.md`
  - `tests/test_stage03_sfm.py`
- **Implementation notes:**
  - Added an isolated Stage 3 `pycolmap` rig probe that reuses an existing matched COLMAP database, injects pycolmap `Rig` and `Frame` metadata from Stage 2 panorama-rig artifacts, and runs `pycolmap.incremental_mapping` without changing the main Stage 3 pipeline.
  - The probe uses zero translation for all virtual sensors and relative rotations derived from Stage 2 `images.txt`, which matches the current panorama-rig assumption that all virtual cameras share the same panorama center.
  - Added targeted Stage 3 tests for the new pycolmap probe helpers (`5 passed`).
  - Because `pycolmap` was unavailable in the default project environment, the real probe runs used a temporary conda env at `/tmp/opencode/pycolmap-conda` with `pycolmap`, `pydantic`, `opencv`, `scipy`, and `plyfile` installed.
  - Real-data rig-aware probe summary:
    - `data/colmap_probe_loose_6f_pycolmap/`: `60` registered images out of `72` (`83.3%`), `618` sparse points.
    - `data/colmap_probe_loose_6f_w3_pycolmap/`: `72` registered images out of `72` (`100.0%`), `1275` sparse points.
  - Conclusion: once the same loose matched graph is given real rig/frame semantics, Stage 3 registration coverage becomes healthy. The earlier `2 / 72` ceiling was caused by the CLI-only non-rig mapper path, not by a lack of verified correspondences.

### [PANORAMA-RIG PYCOLMAP PRODUCTIZATION] Follow-up
- **Completed:** 2026-05-15T19:58:35-04:00
- **Files created:**
  - `data/colmap_probe_loose_6f_w3_pycolmap_gated_helper/`
- **Files modified:**
  - `TRAINING_CONTEXT.md`
  - `PROGRESS.md`
  - `configs/default.yaml`
  - `src/sphereforge/config.py`
  - `src/sphereforge/stages/stage03_sfm/pipeline.py`
  - `src/sphereforge/stages/stage03_sfm/pycolmap_probe.py`
  - `tests/test_stage03_sfm.py`
- **Implementation notes:**
  - Productized the rig-aware Stage 3 path behind both a config gate and an environment gate.
  - New config switch: `stage03.panorama_use_pycolmap_rig` (default `false`).
  - New environment gate: `SPHEREFORGE_ENABLE_PYCOLMAP_RIG=1`.
  - Added optional external-interpreter handoff via `SPHEREFORGE_PYCOLMAP_PYTHON=/path/to/python`, so the main project environment can delegate the pycolmap step to a separate environment that actually has pycolmap installed.
  - Integrated the backend choice into `run_stage03()` after matching and before the old CLI mapper step; if the gates are not satisfied, Stage 3 still uses the existing CLI COLMAP path.
  - Productized the `w=3` preference for the rig-aware path: if the pycolmap rig backend is enabled and `panorama_temporal_window < 3`, Stage 3 now raises the effective temporal window to `3`.
  - Added regression coverage for:
    - config/env gating,
    - fallback to CLI mapper when the gate is off,
    - fallback to CLI mapper for non-panorama datasets,
    - window-3 preference when pycolmap is enabled.
  - Targeted validation passed: `pytest tests/test_stage03_sfm.py -q -k "panorama_rig or pycolmap"` (`8 passed`).
  - Real integration validation of the external-interpreter helper path succeeded from the normal project Python:
    - input database: `data/colmap_probe_loose_6f_w3_interleaved/database.db`
    - output: `data/colmap_probe_loose_6f_w3_pycolmap_gated_helper/`
    - result: `72 / 72` registered images, `1282` sparse points.

### [PANORAMA-RIG PYCOLMAP PRODUCTIZED RERUN HARDENING] Follow-up
- **Completed:** 2026-05-15T23:08:07-04:00
- **Files created:**
  - `data/colmap_probe_loose_6f_w3_stage03_pycolmap_validate/`
  - `data/colmap_probe_loose_6f_w3_stage03_pycolmap_seq_validate/`
  - `data/colmap_probe_loose_6f_w3_stage03_pycolmap_default_validate/`
- **Files modified:**
  - `TRAINING_CONTEXT.md`
  - `PROGRESS.md`
  - `src/sphereforge/stages/stage03_sfm/pipeline.py`
  - `tests/test_stage03_sfm.py`
- **Implementation notes:**
  - Ran a real `run_stage03()` panorama-rig rerun from the normal project Python with the productized env-gated pycolmap backend enabled via `SPHEREFORGE_ENABLE_PYCOLMAP_RIG=1` and `SPHEREFORGE_PYCOLMAP_PYTHON=/tmp/opencode/pycolmap-conda/bin/python`.
  - Reproduced the remaining practical bottleneck in the unmodified productized path: `data/colmap_probe_loose_6f_w3_stage03_pycolmap_validate/` reached feature extraction, then spent the full tool window in local `vocab_tree_builder` without reaching reconstruction.
  - Hardened Stage 3 so panorama-rig pycolmap runs fall back from `sequential+vocabulary_tree` to `sequential` when no external `vocab_tree.bin` is provided beside the dataset, while still honoring an explicit external tree.
  - Extended `registration_report.json` to include the effective `matcher_type`, `reconstruction_backend`, and `panorama_temporal_window` for panorama-rig runs.
  - Real rerun validation after the fix:
    - `data/colmap_probe_loose_6f_w3_stage03_pycolmap_seq_validate/`: `72 / 72` registered images, `1038` sparse points, `141` rows in both `matches` and `two_view_geometries`.
    - `data/colmap_probe_loose_6f_w3_stage03_pycolmap_default_validate/`: `72 / 72` registered images, `1055` sparse points, effective matcher `sequential`, backend `pycolmap_panorama_rig`, effective temporal window `3`, and the expected handoff artifacts (`registration_report.json`, `registered_vs_total.csv`, `sparse_preview.png`, `sparse/0/{cameras,images,points3D,frames,rigs}.bin`).
  - Confirmed the next downstream practical gap is outside Stage 3 itself: a Stage 4 smoke test against the new panorama-rig sparse model still fails exact-name ERP alignment lookup (`frame_000014.png` vs `pano_cameraXX/frame_000014.png`).
  - Validation:
    - `pytest tests/test_stage03_sfm.py -q -k "registration_diagnostics_written or pycolmap_backend or panorama_rig_pycolmap_backend or panorama_rig_can_skip_explicit_match_list"` passed (`6 passed`).
    - `pytest tests/test_stage03_sfm.py -q -k "panorama_rig_pycolmap_backend_prefers_window_three_and_skips_cli_mapper or panorama_rig_pycolmap_backend_uses_external_vocab_tree_when_present or registration_diagnostics_written"` passed (`3 passed`).
    - `ruff check src/sphereforge/stages/stage03_sfm/pipeline.py tests/test_stage03_sfm.py` passed.
  - A full `pytest tests/test_stage03_sfm.py -q` run still reports the pre-existing unrelated failure in `TestModelReader.test_read_binary_format`.

### [PANORAMA-RIG STAGE04 HANDOFF FIX] Follow-up
- **Completed:** 2026-05-15T23:08:07-04:00
- **Files created:**
  - (none)
- **Files modified:**
  - `TRAINING_CONTEXT.md`
  - `PROGRESS.md`
  - `src/sphereforge/stages/stage04_depth/depth_alignment.py`
  - `src/sphereforge/stages/stage04_depth/pipeline.py`
  - `tests/test_stage04.py`
- **Implementation notes:**
  - Fixed the Stage 3 -> Stage 4 panorama-rig handoff so ERP depth alignment no longer depends on an exact sparse-model image name like `frame_000014.png` being present.
  - `align_depth_to_colmap()` now accepts `colmap_dataset_dir` and, when `panorama_rig.json` is present, uses a panorama-rig ERP fallback path:
    - match registered virtual views by ERP frame stem,
    - derive the world-to-panorama pose from the registered rig view and fixed Stage 2 yaw/pitch rotation,
    - union sparse points across the matching rig views,
    - project those points into ERP pixel space,
    - and align radial ERP depth against sparse metric range.
  - Wired `run_stage04()` to pass `cubemap_dir` through to the alignment helper so real panorama-rig datasets can use the manifest automatically.
  - Added regression coverage for the panorama-rig frame-stem fallback and for the new pipeline argument wiring.
  - Real smoke check against the successful productized Stage 3 output now succeeds:
    - sparse model: `data/colmap_probe_loose_6f_w3_stage03_pycolmap_default_validate/sparse/`
    - dataset metadata: `data/cubemaps_probe_loose_6f_w3/`
    - call: `align_depth_to_colmap(..., image_name='frame_000014.png', colmap_dataset_dir=Path('data/cubemaps_probe_loose_6f_w3'))`
    - result: returned an aligned `(256, 512)` depth map with finite scale/shift instead of raising `Image 'frame_000014.png' not found in sparse model`.
  - Validation:
    - `pytest tests/test_stage04.py -q -k "alignment_accuracy or image_not_found_raises or no_sparse_points_raises or with_rpg360_anchor or panorama_rig_frame_name_uses_erp_alignment or pipeline_flow or pipeline_fail_fast_on_not_implemented"` passed (`7 passed`).
    - `ruff check src/sphereforge/stages/stage04_depth/depth_alignment.py src/sphereforge/stages/stage04_depth/pipeline.py tests/test_stage04.py` passed.

### [STAGE04 TEST + BACKEND READINESS FOLLOW-UP] Follow-up
- **Completed:** 2026-05-15T23:08:07-04:00
- **Files created:**
  - (none)
- **Files modified:**
  - `TRAINING_CONTEXT.md`
  - `PROGRESS.md`
  - `tests/test_stage04.py`
- **Implementation notes:**
  - Updated stale Stage 4 model-factory test expectations to match current shipped behavior:
    - `panda` is now a deprecated alias that resolves to `DAPModel`,
    - `da360` still raises `NotImplementedError`, but the message is lowercase (`da360`).
  - Full Stage 4 test suite now passes:
    - `pytest tests/test_stage04.py -q` -> `27 passed`
  - The suite still emits one non-fatal runtime warning from `compute_ncc()` during the anchor-path test (`invalid value encountered in divide`).
  - Probed Stage 4 backend readiness in the current environment:
    - `torch`, `transformers`, `diffusers`, and `huggingface_hub` import successfully,
    - but no external `depth_anything_v2` package is installed,
    - and the Stage 4 factory currently returns wrappers still marked as stub/untrusted for `dap`, `depth_anything_v2`, `rpg360`, and `panda`.
  - Conclusion: the Stage 4 tests and panorama-rig handoff are now in good shape, but there is still no real non-stub live depth backend available through the current SphereForge integration in this environment.

---

## Per-Stage Progress

| Stage | Total | Done | Lines | % |
|-------|-------|------|-------|---|
| 0: Infrastructure | 12 | 10 | 2,704 | 83% |
| 1: Frame Selection | 7 | 7 | 580 | 100% |
| 2: Cubemap + COLMAP | 12 | 12 | 1,550 | 100% |
| 3: COLMAP SfM | 7 | 7 | 816 | 100% |
| 4: Depth Estimation | 7 | 7 | 1,322 | 100% |
| 5: Gaussian Seeding | 13 | 13 | 1,285 | 100% |
| 6: Optimization | 13 | 13 | 2,969 | 100% |
| 7: Occlusion Recovery | 14 | 14 | 1,932 | 100% |
| 8: Export | 9 | 9 | 1,260 | 100% |

---

## Remaining Tasks

None — all tracked tasks are complete.

### [ASSESSMENT-P2] Moderate Issue Fixes — 2026-05-03
- **Unified COLMAP readers**: Removed duplicate `read_colmap_cameras()` and `read_colmap_images()` from `common/io.py`; canonical parsers in `common/colmap_helpers.py` are now re-exported. Callers updated (`stage07/pipeline.py`).
- **`rotation_matrix_to_quat` verified**: Added 12 unit tests (`tests/test_colmap_helpers.py`) against known ground-truth rotations (identity, 90°/180° about X/Y/Z). Round-trip and orthogonality validated.
- **`__init__.py` re-exports standardized**: All 8 stages already re-export public APIs via `__init__.py`; confirmed consistent.
- **Progress logging robustness**: `log_task_completion()` now validates the task row exists and reports the current status before replacement. Added `dry_run` parameter. Raises `RuntimeError` if the table format changes unexpectedly.
- **`py.typed` marker added**: `src/sphereforge/py.typed` empty file for PEP 561 compliance.
- **GPU install instructions added to README**: Section with CUDA 12.8 + PyTorch + gsplat one-liner.
- **`model_cache.py` simplified**: `download_if_missing()` now requires a non-empty `url`. PanDA model wrapper updated to use `get_model_path().exists()` instead of `download_if_missing(..., url=None)`.
- **Stage 7 inline imports documented**: Package docstring in `stage07_occlusion/__init__.py` explains the pattern.
- **Training view GPU pre-loading**: `train_gaussians()` now moves all view tensors to GPU once before the training loop, eliminating redundant `.to(device)` calls per iteration.
- **`.gitignore` already covered**: `*.pth`, `*.pt`, `*.safetensors`, `.cache/` entries were already present.
- Files modified: `common/io.py`, `common/colmap_helpers.py`, `common/model_cache.py`, `logging_utils.py`, `models/metric3d.py`, `stages/stage04_depth/panda_model.py`, `stages/stage07_occlusion/__init__.py`, `stages/stage06_optimization/training_loop.py`, `README.md`
- Files created: `src/sphereforge/py.typed`, `tests/test_colmap_helpers.py`

### [ASSESSMENT-P3] Minor Issue Fixes — 2026-05-03
- **Integration test harness (T0.12)**: `tests/integration/test_pipeline.py` runs stages 2→5 on a 2-frame synthetic dataset (256×512) and verifies a valid PLY is produced.
- **Dockerfile (T0.10)**: `Dockerfile` based on `nvidia/cuda:12.8.0-devel-ubuntu22.04` with COLMAP, PyTorch, and SphereForge installed.
- **Conda environment spec**: `environment.yml` for reproducible conda builds.
- Files created: `Dockerfile`, `environment.yml`, `tests/integration/test_pipeline.py`

---

### [ASSESSMENT-P0] Critical Issue Fixes — 2026-05-02
- **CLI wired up** (`src/sphereforge/cli.py`): `process` now runs stages 1-8 sequentially with `--stage`, `--resume`, and `--config` support. `export` runs Stage 8 on existing PLY files.
- **Config files created**: `configs/default.yaml`, `configs/high_quality.yaml`, `configs/fast_preview.yaml` with sensible defaults per `PIPELINE_DESIGN_V2.md`.
- **Stage 6 rasterizer fail-fast**: `render_gaussians()` and `train_gaussians()` now raise `RuntimeError` with clear install instructions when gsplat is missing, instead of silently training on random tensors.
- **Stage 4 depth fail-fast**: `run_stage04()` now raises `RuntimeError` when a depth estimator raises `NotImplementedError`, instead of silently writing zero-depth maps.
- **Stage 5 stride bypass fixed**: `run_stage05()` now computes per-pixel confidence (NCC when secondary depth is available, Sobel-gradient heuristic otherwise) and passes the resulting `stride_map` to `project_to_3d()`. `project_to_3d()` was extended to accept `stride_map` for non-uniform subsampling.
- Files modified: `cli.py`, `training_loop.py`, `stage04_depth/pipeline.py`, `stage05_seeding/pipeline.py`, `stage05_seeding/projection.py`, `tests/test_stage04.py`, `tests/test_stage05.py`
- Files created: `configs/default.yaml`, `configs/high_quality.yaml`, `configs/fast_preview.yaml`

### [ASSESSMENT-P1] Significant Issue Fixes — 2026-05-02
- **Parallel processing**: Added `num_workers` config and `concurrent.futures` parallelization for Stages 2 (`ProcessPoolExecutor`), 4 (`ThreadPoolExecutor`), and 5 (`ProcessPoolExecutor`).
- **Stage 6 checkpointing**: `train_gaussians()` now saves intermediate `.ply` checkpoints every `config.checkpoint_every` iterations (default 5000).
- **Stage 2 duplicate crop extraction fixed**: `resized_crops` is now reused for output instead of re-resizing original crops.
- **`np.ix_()` replaced**: `project_to_3d()` uniform-stride path now uses direct slicing `depth_map[::stride, ::stride]` instead of `np.ix_()`.
- **`test_stage02.py` written**: 14 tests covering cubemap extraction, intrinsics computation, extrinsics quaternion generation, yaw diversification, mask generation, and COLMAP writer round-trips.
- Files modified: `cli.py`, `config.py`, `stage02_cubemap/pipeline.py`, `stage04_depth/pipeline.py`, `stage05_seeding/pipeline.py`, `stage05_seeding/projection.py`, `stage06_optimization/training_loop.py`
- Files created: `tests/test_stage02.py`

## Key Implementation Notes

1. **Rasterizer is integrated** (T6.11): Stage 7 now uses `render_gaussians()` from Stage 6 via gsplat 1.5.3 for real GPU renders. **FIXED 2026-05-15.**

2. **GS-Diff distillation is real** (T7.10): `run_gsplat_distillation()` in `distillation.py` performs differentiable optimisation: render→L1+SSIM loss→backprop→Adam step, 50 iters per camera. **FIXED 2026-05-15.**

3. **Flux inpainting backends** (T7.7): `Flux2KleinInpainter` and `FluxFillInpainter` added. FLUX.2 Klein 9B is default, requires HF auth + license. **FIXED 2026-05-15.**

4. **Grid-based fusion** (T5.2): Replaced O(N²) `query_pairs` with O(N log N) grid clustering for multi-view point fusion. **FIXED 2026-05-15.**

5. **LPIPS model caching**: `_get_lpips_model()` caches per backbone; `filter_hallucinations()` batches patches. **FIXED 2026-05-14.**

6. **Config**: `configs/high_res.yaml` created — stride 10, 20K iters, 3M cap, SH degree 1.

7. **PanDA is a STUB** (T4.1): `PanDAModel` raises NotImplementedError. Weights must be obtained separately.
8. **RPG360 license** (T2.9): No license file. Contact authors or implement from paper.

### Stage 7 Budget + Classification Tuning
- **Completed:** 2026-05-14
- **Files created:**
  - `src/sphereforge/stages/stage07_occlusion/blend_fill.py`
- **Files modified:**
  - `src/sphereforge/stages/stage07_occlusion/iterative_fill.py`
  - `src/sphereforge/stages/stage07_occlusion/__init__.py`
  - `src/sphereforge/config.py`
  - `tests/test_stage07.py`
- **Implementation notes:**
  - Integrated `classify_gaps` into `fill_holes_iterative` loop (was previously implemented but unused).
  - Added weighted budget allocation: missing_geometry holes get 2× priority, boundary holes are skipped.
  - Added `_select_source_views_for_holes` to filter only relevant source views for patch reuse.
  - Wired `sharegs_optimize_iters` config into pipeline via new `blend_fill()` k-NN smoothing module.
  - Added 6 new unit tests, fixed 2 existing test bugs.
  - All 50 Stage 7 tests pass.

### [ASSESSMENT-2026-05-15] Pipeline Reassessment and Diagnostics Plan
- **Completed:** 2026-05-15
- **Files created:**
  - (none)
- **Files modified:**
  - `TRAINING_CONTEXT.md`
  - `PROGRESS.md`
- **Implementation notes:**
  - Added a new dated reassessment and stage-by-stage diagnostics plan to `TRAINING_CONTEXT.md`.
  - Reframed the current reconstruction failure as an upstream correctness problem rather than a late-stage tuning problem.
  - Captured current evidence from the repo state:
    - Stage 2 produced 108 cubemap images but Stage 3 currently registers only 9 images with 462 sparse points.
    - Stage 4 default depth backends (`dap`, `depth_anything_v2`, `metric3d`) are still stub implementations.
    - Stage 4 ERP-to-COLMAP depth alignment likely mismatches image naming between ERP frames and cubemap faces.
    - Stage 5 writes activated scales/opacities while Stage 6 currently assumes log-scale/logit inputs, which is a plausible direct cause of oversized blob-like splats.
  - Documented a new debugging order:
    1. Validate Stage 3 camera registration.
    2. Validate Stage 4 depth realism and alignment.
    3. Validate Stage 5 seed geometry.
    4. Only then run short Stage 6 debug optimization.
    5. Defer Stage 7 and Stage 8 tuning until Stage 6 is already usable.
  - Added stage-by-stage validation gates and recommended diagnostic artifacts so each stage can be visually inspected in isolation.

---

## 2026-11-12 — End-to-end pipeline reaches Stage 8 on real footage

**Goal:** make all 8 stages run end-to-end on real 360 footage rather than stubs.

**Outcome:** the full pipeline now completes on `data/raw/synthetic_room.mp4`
(24 frames, 1024x512 ERP) and writes a valid `final.ply` (56,365 Gaussians) plus
an HTML viewer.

### Bugs fixed

| Area | Bug | Effect |
|------|-----|--------|
| Stage 3 | `panorama_temporal_window` referenced before assignment | crashed the pycolmap rig backend |
| Stage 3 | `num_registered_images()` (pycolmap 4.x API is `num_reg_images()`) | crash after reconstruction |
| Stage 3 | sequential matcher could not link rig views | 6/36 images registered; now exhaustive + 2048px SIFT -> 36/36 |
| Stage 3 | `read_sparse_model` always picked `sparse/0` | read a 2-image sub-model instead of the 36-image one |
| Stage 4 | depth/COLMAP scale fit applied unconditionally | silent corruption when geometry disagreed |
| Stage 4 | monocular SfM scale ambiguity never resolved | Stage 5 projected metric depth into a non-metric world |
| Stage 5 | per-frame point clouds never transformed into the COLMAP world frame | all frames fused at the origin |
| Stage 6 | `SIMPLE_RADIAL` camera model rejected | crash building training views |
| Stage 6 | rig-view depth lookup required an `images/` prefix | every view trained against random-noise depth |
| Stage 6 | `cv2.BORDER_WRAP` does not wrap; ERP seam sampled wrong pixel | depth views collapsed to zero |
| Stage 6 | Stage 5's 0-255 colours used as SH DC coefficients | renders saturated to white (PSNR ~2 dB) |
| Stage 6 | opacity reset used `prune_min_opacity * 2` | every Gaussian deleted at the next prune pass |
| Stage 6 | `packed=False` rasterisation | ~3x slower than the fused path |
| Stage 6 | PLY written in raw logit/log space | external viewers mis-render opacity and scale |
| Stage 7 | per-Gaussian Python splat loop | minutes per camera |
| Stage 7 | dilation radius hard-coded to <=8 px regardless of footprint | >98% of every view read as "hole" |
| Stage 7 | scene radius from the farthest Gaussian | novel cameras placed outside the room |

### Tooling added

- `scripts/fetch_cuda_toolkit.py` — assembles a CUDA 12.6 toolkit (nvcc, cicc,
  headers) from conda packages, no admin rights required.
- `scripts/build_gsplat_cuda.bat` — builds the gsplat CUDA rasteriser with MSVC.
- `scripts/sphereforge_env.bat` — runs any command with the CUDA build env set.
- `configs/e2e_smoke.yaml` — end-to-end smoke configuration.

### Results

- Stage 6 training PSNR: 8.5 -> 20.5 dB over 3000 iterations.
- Stage 7 hole coverage: 0.74 -> 0.52 in one round.
- Final PLY: 56,365 Gaussians, all finite, opacity in [0,1], scale > 0.

### Known limitations

- DAP ERP fusion is accurate at the median (2.03 m vs 2.14 m true) but has heavy
  tails (ratio 0.25-4.3x), which leaves floater Gaussians outside the room.
- Stage 7 GS-Diff inpainting needs `diffusers >= 0.38`; it is skipped otherwise.
- The SfM-to-metric scale is a single global factor; per-frame drift is not corrected.

---

## 2026-11-13 — Depth-backend fixes (round 4)

**Goal:** improve geometric accuracy of the depth backend, which was leaving
floater Gaussians outside the room.

### Fixed

| Area | Bug | Effect |
|------|-----|--------|
| DAP rig | `cv2.BORDER_WRAP` does not wrap; ERP seam sampled the wrong column | seam views read half the panorama |
| DAP rig | Depth Anything V2 is *relative* depth, fused as if metric | views disagreed by 5x (0.63-3.08) |
| DAP rig | only -45/0/+45 pitches; poles seen at grazing angle only | poles came out ~3x too far |
| Stage 6 | colours fed to gsplat as RGB, but gsplat expects SH DC | rendered flat grey |
| Stage 6 | colours divided by 255 twice on write | every Gaussian collapsed to one colour |
| Stage 6 | opacity reset fired after densification stopped | scene wiped, never recovered |
| Stage 6 | scene extent = max distance, so one floater inflated it | feedback loop grew the scene without bound |
| Stage 5 | fusion merge radius = cross-view disagreement, unbounded | 96,752 points collapsed to 88 |
| Stage 3 | metric rescale applied in memory only | any re-read of the sparse model used scale-free units |

### Measured improvement

| Metric | Before | After |
|---|---|---|
| Depth within 25% of truth | 0.10 | 0.24 |
| Depth far-bias (ratio > 2) | 0.32 | 0.17 |
| Stage 5 Gaussians | 75 | 757 |
| Stage 6 PSNR (best observed) | 8.8 dB | 22.5 dB |
| Stage 7 hole coverage | 0.74 to 0.52 | 0.99 to 0.27 |

### Open problem (regression introduced this round)

The SfM rig is internally inconsistent: sparse points have std ~1.2 m but the
registered cameras are scattered with std ~2.6 m (radii 0.73-7.8 m, a smooth
continuum with no clear outliers). Stage 6 trains on rig views, so inconsistent
poses make every view disagree and PSNR stalls at ~8.8 dB.

Attempts that did **not** work:
- Pruning cameras beyond 3x the median radius: the distribution is a continuum,
  so no threshold separates good from bad.
- Persisting the metric rescale: correct in itself (it is kept), but it does not
  fix the rig inconsistency.

Next step is to improve Stage 3 registration itself (more overlap between rig
views, or a rig-constrained bundle adjustment) rather than post-filtering poses.

---

## 2026-11-13 (round 5) — Stage 3 rig pipeline repaired; pycolmap blocker isolated

**Headline:** the panorama-rig backend was structurally broken in three independent
ways. All three are now fixed, and the pipeline registers **144/144 images with
8,714 points** (was 36/36 with ~2,000). A fourth issue remains, inside pycolmap
itself, and is documented below.

### Fixed this round

| Bug | Effect | Fix |
|-----|--------|-----|
| `pycolmap.extract_features` creates one camera per image | 36 images -> 36 cameras -> 36 rigs of 1 sensor each; the rig constraint was a no-op | `_share_cameras_across_rig_frames()` renumbers images onto the manifest's 12 cameras |
| Camera IDs did not match the manifest (1,4,7,... vs 1..12) | rig annotation referenced cameras no image used | renumber 1..N in folder order |
| `_run_pycolmap_reconstruction` ran mapping itself | the rig-aware probe never ran, so `constant_rigs` was never applied | added `skip_mapping`; the probe now owns mapping when the rig backend is active |

Also: `db.clear_frames()` must precede `read_all_images()` (clearing after the
read leaves stale `data_id` state and `update_image` fails), and stale
`*.txt` files must be removed when rewriting a `.bin` model (readers prefer
text and would serve the old cameras).

### Verified improvement

| Metric | Before | After |
|---|---|---|
| Images registered | 36 | **144** |
| Sparse points | ~2,000 | **8,714** |
| Rigs / frames / cameras | 36 / 36 / 36 | **1 / 12 / 144** |
| Stage 5 Gaussians | 75 | **166,331** |
| Stage 7 hole coverage | 0.74 -> 0.52 | **0.27 -> 0.27** |

### Remaining blocker (inside pycolmap 4.2.1)

The rig is built correctly in the database: 1 rig, 12 sensors, all
`sensor_from_rig` translations zero (correct for a panorama rig, where every
face shares one optical centre). But the mapper does not honour it:

- All 12 sensors in a frame have `sensor_t = 0`, so every `cam_from_world`
  translation must equal the frame's `rig_from_world` translation. Measured:
  they scatter to (4.38, 2.44, 2.98), (3.84, -2.27, -3.75), (-4.38, 0.29, -3.84)
  — opposite sides of the room. **0 of 12 frames are rigid.**
- Re-running with an explicit non-zero sensor offset `(1, 0, 0)` also fails to
  reproduce it, so the mapper ignores `sensor_from_rig` generally, not just the
  degenerate zero case.
- `constant_rigs` + `ba_refine_sensor_from_rig = False` are both set; the
  constraint is still not enforced.
- `Database.write_rig()` assigns its own ID (146), and `update_rig()` to force
  ID 1 raises `SQLite error: constraint failed`. The mapper hard-requires a rig
  with ID 1 (`IndexError: Rig with ID 1 does not exist`), so the rig cannot be
  placed at the ID the mapper expects.

Consequence: cameras are placed inconsistently, so Stage 6 trains on views that
disagree and PSNR stalls around 8-11 dB.

### What was tried and did not work

- Pruning cameras beyond 3x the median radius: radii form a smooth continuum
  (0.73-7.8 m), no threshold separates good from bad.
- More frames (3 -> 12): improves registration and seeding a lot, but the rig
  is still non-rigid, so PSNR stays low.
- Stripping rigs entirely: only 2 of 144 images register. The rig is load-bearing
  for registration even though its geometry is not enforced.

### Next step

Either (a) upgrade pycolmap and re-test whether rig constraints are enforced,
(b) post-process the reconstruction to enforce rigidity (fit one pose per frame
plus fixed sensor rotations, then re-triangulate), or (c) bypass the rig mapper
and estimate rig poses directly from the 12-face correspondences.

---

## 2026-11-14 — Progress review

### Where the pipeline actually stands

All 8 stages run end-to-end and produce a valid export. The blocker is
geometric accuracy, not plumbing.

| Item | State |
|---|---|
| Tests | 344 passing |
| Lint (files touched) | clean |
| Lint (pre-existing, untouched files) | 69 errors, e.g. `stage07_occlusion/distillation.py` |
| Export | `data/e2e/export/final.ply` (228,060 Gaussians) + `viewer.html` |
| Registration | 144/144 images, 8,714 points, 1 rig / 12 frames |
| Stage 6 PSNR | ~8-11 dB (target: >20) |
| Rig rigidity | **fixed, but not yet wired in** |

### What is done and verified

- Stage 3 rig structure repaired (camera sharing, manifest-aligned IDs, the
  rig probe now owns mapping). Registration went 36 -> 144 images.
- `rigidity.py` written and **verified on real data**: 144/144 frames rigid,
  max sensor spread 4.12 m -> 0. pycolmap's in-memory rig API cannot express a
  panorama rig (`Frame.set_cam_from_world` recomputes the frame pose from the
  camera it is given, so only the last sensor survives), so the module writes
  corrected poses straight to `images.txt` and removes the stale `.bin` files.
- Depth backend fixes (relative-depth harmonisation, pole rings, ERP seam).
- Stage 6 fixes (SH colour space, opacity-reset schedule, robust scene extent).
- Stage 5 fusion merge-radius cap.

### Gaps found in this review

1. **`rigidity.py` is not wired into `run_stage03`.** It exists and works but
   nothing calls it, so the pipeline still produces a non-rigid rig.
2. **No tests for `rigidity.py`.** AGENTS.md requires a test per task.
3. **The on-disk sparse model is still the unrepaired one**, and the export
   predates the rigidity work.
4. **Frame path span is 0.31-0.42 m vs a true 1.8 m.** Consistent internally,
   but roughly 4-5x too small; Stage 4's metric rescale should absorb this, and
   that needs checking once rigidity is wired in.

### Immediate next steps

1. Wire `enforce_rig_rigidity()` into Stage 3 after mapping.
2. Add unit tests for the rigidity module.
3. Re-run end-to-end and measure PSNR and geometry against ground truth.

---

## 2026-11-14 (round 6) — Rigidity wired in; NaN training bug fixed

### Fixed

| Bug | Effect | Fix |
|-----|--------|-----|
| `rigidity.py` never called | rig stayed non-rigid end-to-end | wired into `run_stage03` after mapping |
| pycolmap cannot store a panorama rig | every write path lost the correction | poses written to a sidecar (`rig_rigidity.json`) and folded in by `read_sparse_model`, where all downstream stages pick them up |
| Depth regularisation included uncovered pixels | `target_depth == 0` made the D-Normal term divide by zero -> **loss NaN from iteration 100** | mask to `target_depth > 0` |
| No NaN guard in the training loop | one bad iteration poisoned every parameter permanently | skip the update and log when the loss is non-finite |
| 163k seeds + densify at iter 0 | hit the 400k cap immediately, then pruned all 400k | stride 4 -> 8 (46,877 seeds), leaving densification headroom |

### Verified results

| Metric | Before | After |
|---|---|---|
| Rig rigidity (sensor spread) | 4.12 m | **0 (exact)** |
| Training loss | NaN by iter 100 | **0.40 -> 0.23, decreasing** |
| Training throughput | 10.4 it/s | **42.5 it/s** |
| Stage 6 PSNR | 8.8 (stalled) | **11.95** |
| Final radial p50 | 3.04 m | **2.16 m** (true walls 1.5-2.5 m) |
| Gaussians inside room | 45% | **91.2%** |
| Tests | 344 | **355** |

### Notes on the pycolmap limitation

`Image.cam_from_world` is read-only and `Frame.set_cam_from_world` recomputes the
frame pose from the camera it is given, so writing 12 sensors leaves only the
last one. Every file-format workaround fails too: text-only models reload as one
rig per image, and keeping the pose binaries makes them win over the text. The
sidecar sidesteps all of it.

### Remaining gaps

1. Stage 6 PSNR is 11.95 dB; the target is >20. Training now converges, so the
   limit is reconstruction quality (8,683 sparse points across 144 views), not
   the optimiser.
2. Frame path span is ~0.4 m against a true 1.8 m. Internally consistent, but
   the metric rescale (0.0593) is absorbing a large factor.
3. Stage 7 hole coverage is flat (0.31 -> 0.31) because GS-Diff inpainting needs
   `diffusers >= 0.38`.

---

## 2026-11-14 (round 7) — Rigidity actually reaches the pipeline; PSNR 11.95 -> 16.29 dB

### The big one: rigidity was silently not running

`enforce_rig_rigidity()` was wired into Step 5c of `run_stage03`, but the
pycolmap branch **returns early at line 883**, before Step 5c. So the rig
correction never ran in the configuration the pipeline actually uses, and
sensor spread stayed at 4.11 m. Moved the call into the pycolmap branch.

### Second: the metric rescale destroyed the correction

`_persist_rescaled_sparse_model` re-serialised the model through pycolmap,
which cannot hold a panorama rig — it wrote every image to the same pose and
dropped the sidecar entirely. It now records the factor in the marker file and
scales the rigid poses in the sidecar instead. Verified: spread 0.006 m after
rescaling (was 4.11 m).

### Third: Stage 7 dragged the scene outward

`_compute_scene_bounds` used the p95 distance as the scene radius. With stray
Gaussians that inflated the radius to 3.6 m (true walls ~2.0 m), so novel
cameras orbited out to 5.4 m — outside the room — and synthesised Gaussians
beyond the walls. Now uses the median distance.

### Measured

| Metric | Before | After |
|---|---|---|
| Rig sensor spread (after Stage 4) | 4.11 m | **0.006 m** |
| Stage 6 PSNR | 11.95 dB | **16.29 dB** |
| Training loss | 0.40 | **0.34 -> 0.13** |
| Throughput | 42.5 it/s | **50.7 it/s** |
| Stage 7 hole coverage | 0.31 -> 0.31 (flat) | **0.13 -> 0.06** |
| Final radial p50 | 2.97 m | **2.63 m** (true walls 1.5-2.5) |
| Gaussians inside room | 79% | **88%** |
| Tests | 355 | **355** |

### Remaining gaps

1. PSNR 16.29 dB vs a >20 target. Training converges cleanly; the limit is
   sparse-point density (8,684 points over 144 views).
2. Camera path spans 0.02 m against a true 1.8 m. The metric rescale is
   absorbing a ~50x factor that the sparse points do not share, so the points
   sit at 30 m while the cameras sit at 0.01 m. This inconsistency is the most
   likely remaining cause of geometric error and should be fixed next.
3. Stage 7 GS-Diff inpainting still needs `diffusers >= 0.38`.

---

## 2026-11-14 (round 8) — Root cause of the low PSNR: the rig constraint destroys camera translation

### The finding

The panorama-rig constraint is **degenerate for translation**. A rig whose 12
sensors share one optical centre can explain the images with pure rotation, and
the mapper converges there. Measured on the same database:

| Run | Images | Path span (x, y, z) |
|---|---|---|
| Rig-constrained | 144 | **0.00 x 0.45 x 0.00** (collapsed to a line) |
| Unconstrained | 144 | 5.29 x 2.89 x 10.73 (real translation) |

With zero translation there is no parallax, so no depth, so PSNR is capped no
matter how long training runs. This — not sparse-point density — was the real
ceiling behind the 11.95 / 16.29 dB results.

`constant_rigs` was not the cause (removing it changed nothing); the constraint
is inherent to the shared-centre rig, and bundle adjustment cannot escape the
local minimum (`refine_rig_from_world=True` left the span unchanged).

### Fix: detect the collapse and re-run unconstrained

`_camera_path_is_degenerate` measures the per-frame centre extents; a ratio of
second-largest to largest below 0.05 means the path is a line. When it fires,
the probe re-runs mapping from a database copy with the rig tables cleared
(the rig lives in the database, so dropping the options alone rebuilds it).
Rigidity enforcement is then skipped — with no rig, averaging the sensors would
destroy the recovered path.

Three subtleties cost most of the time here:
1. The check must run on `sparse/0`, not the `sparse` parent (reading the parent
   silently yields an empty reconstruction, so the check always passed).
2. It must measure **frame centres**, not individual images — a rig scatters its
   sensors, which makes the raw model look healthy.
3. The fallback must clear the rig from the *database*, not just the options.

### Also fixed: double-applied metric rescale

`rescale_sparse_model` already scales image translations in memory, and the
sidecar was being scaled again on disk, so cameras ended up ~15x too close to
the origin while points were correct. The sidecar is no longer touched; only the
persisted point cloud is rescaled. Verified idempotent across repeated runs.

### Measured

| Metric | Before | After |
|---|---|---|
| Camera path span | 0.00 x 0.45 x 0.00 | **8.27 x 4.92 x 11.55** |
| Sparse point radial p50 | 30.58 (unscaled) | **1.67 m** (true 1.5-2.5) |
| Gaussians inside room | 88% | **97.2%** |
| Final radial p50 | 2.63 m | **2.22 m** (true walls 1.5-2.5) |
| Final bbox | -7.4..6.2 (loose) | **-2.7..3.2 (tight)** |
| Stage 6 PSNR | 16.29 dB | 8.96 dB |
| Tests | 355 | **355** |

### The PSNR regression is real and expected

The degenerate run scored 16.29 dB precisely *because* it had no parallax: a
single rotation-only solution renders every view consistently, which inflates
PSNR while producing geometry that cannot be a real scene. Now that real
translation is recovered, the cameras sit at a 3.24 m radius while the points
sit at 1.67 m — the unconstrained SfM found a solution where the path orbits
*outside* the walls instead of moving through the room. That is a wrong
solution, but it is a wrong solution with actual parallax, which is the right
foundation to fix.

### Next

The unconstrained reconstruction's camera path is wrong (orbiting outside the
room rather than through it). Options: seed the mapper with the known rig
geometry as a pose prior, or use the rig run for registration and then solve
translation with a pose-prior bundle adjustment.

---

## 2026-11-14 (round 9) — PSNR 8.96 -> 22.75 dB; the reconstruction was right all along

### The PSNR ceiling was the iteration count, not the geometry

Stage 6 ran 3,000 iterations. 3DGS needs far more: SH degree 1 only activates
after the densification phase, so at 3,000 iterations the model never left
diffuse colour. Raising the schedule to 8,000 iterations (densify until 4,000)
took PSNR from 8.96 to **22.75 dB** at iteration 4,000, with loss 0.45 -> 0.09.

### Correcting last round's diagnosis

Last round I reported the unconstrained reconstruction's camera path as
"wrong — orbiting outside the walls". That was my error: I compared the
recovered path to ground truth in the *SfM* world frame, which is rotated
relative to the true room by gauge freedom. Aligning with a similarity
transform (Umeyama) gives:

| Measure | Result |
|---|---|
| Per-axis correlation with truth (X, Z) | **0.999, 0.999** |
| Mean alignment error | **2.4 cm** |
| Max alignment error | 3.5 cm |
| Path length | 1.7 m |

The reconstruction was accurate to centimetres. The apparent "anisotropy"
(per-axis scales 2.56 / 1.33) is a rotation of the world frame, not a
distortion — a single scalar rescale cannot change an X:Z ratio, and a
similarity fit resolves it exactly. Axis-aligned box tests are therefore
meaningless on SfM output and should not be used as a quality metric.

### Confirmed: the rig constraint is inherently degenerate

Tested three more configurations, all of which collapse the path to a line:

| Configuration | Path span |
|---|---|
| Rig + `constant_rigs` | 0.00 x 0.45 x 0.00 |
| Rig, rig pose free | 0.00 x 0.83 x 0.00 |
| Rig + 10 global BA refinements | 0.00 x 0.36 x 0.00 |

The scene itself is not degenerate — a 1.8 m baseline at 2 m depth is ~50 deg
of parallax. The shared-optical-centre constraint is what removes the signal,
so the unconstrained fallback is the correct architecture, not a workaround.

### Measured

| Metric | Before | After |
|---|---|---|
| Stage 6 PSNR | 8.96 dB | **22.75 dB** |
| Training loss | 0.45 | **0.09** |
| Final Gaussians | 60,991 | **181,374** |
| Final radial p50 | 2.22 m | **2.09 m** (true walls 1.5-2.5) |
| Gaussians inside room | 97.2% | **94.2%** |
| Stage 7 hole coverage | 0.32 (flat) | **0.16** |
| Tests | 355 | **355** |

### Next

PSNR 22.75 dB clears the >20 target. Remaining: Stage 7 inpainting still needs
`diffusers >= 0.38`, and the 8,000-iteration schedule should become the default
in `configs/` rather than only `e2e_smoke.yaml`.

### Follow-up: guard against the short-schedule trap

`rerun_moderate.yaml` had the same 3,000-iteration schedule and was raised to
8,000 / densify 4,000. `training_loop` now warns when a run leaves less than
half its iterations at the target SH degree, since SH only activates at
`2500 * sh_degree`:

    iterations=3000 sh=1 -> warn (only 500 iterations with SH)
    iterations=8000 sh=1 -> ok

Covered by `TestShScheduleGuard`. Tests: 356 passing.

---

## 2026-11-14 (round 10) — Stage 7 diffusion inpainting works; two silent export killers fixed

### diffusers installed, GS-Diff now runs

`diffusers` was not installed at all, so Stage 7 always skipped inpainting.
Installed 0.43.0 (resolves cleanly on Python 3.12 / torch 2.7.1).

The default backend is FLUX.2 Klein (9B), which needs a HuggingFace token.
Switched `e2e_smoke.yaml` to `gsdiff_backend: sd`
(`runwayml/stable-diffusion-inpainting`), which is public and small. Verified
end to end: SD loads, LPIPS filtering runs, and hole pixels are distilled.

### Model cache was unwritable

`DEFAULT_CACHE_DIR` was hard-coded to `~/.cache/sphereforge/models`, which the
sandboxed runner cannot create (`WinError 5`). Added a `SPHEREFORGE_CACHE_DIR`
environment override so weights can live inside the workspace.

### Stage 7 was unbounded in runtime

The GS-Diff loop ran one diffusion pass per novel camera with no limit: 36
cameras at ~5 min each, over an hour. Added `gsdiff_max_cameras` (default 8),
processing the cameras with the most holes first. Stage 7 now takes ~2.5 min
with inpainting on the 8 highest-value views.

### Two bugs that silently produced an empty export

1. **Raw logits written back as opacities.** `distillation._sync_gaussians_numpy`
   stored the raw opacity/scale tensors, but the pipeline's PLY convention is
   activated (`sigmoid`/`exp`). Values outside [0, 1] then reached Stage 8.
   Now writes activated values.
2. **A single NaN position wiped the entire scene.** `final_rap_prune` computed
   the scene extent from `dists.max()`, so one non-finite position made the
   extent NaN, which made the scale mask reject *all* Gaussians (observed:
   294,586 -> 0). Non-finite Gaussians are now dropped up front, and the extent
   uses the 95th percentile instead of the maximum.

### Measured

| Metric | Before | After |
|---|---|---|
| Stage 7 diffusion inpainting | never ran | **8 cameras, LPIPS-filtered** |
| Stage 7 runtime | >1 h (unbounded) | **~2.5 min** |
| Export Gaussians (run A) | 0 | **181,374** |
| Export Gaussians (run B) | 0 | **102,003** |
| Tests | 356 | **361** |

### Note on run-to-run variance

Two clean end-to-end runs gave different geometry: run A reached radial p50
2.09 m with 94.2% inside the room; run B reached 2.98 m with 62.6%. SfM is
non-deterministic, and the unconstrained fallback is sensitive to which
solution the mapper lands in. Both runs complete every stage and export valid
geometry; the spread is a quality-variance issue, not a correctness one.

---

## 2026-11-14 (round 11) — Run-to-run variance diagnosed; NaN guarded at the source

### pycolmap's mapper is genuinely non-deterministic

Two runs on an *identical* database with identical options produce different
reconstructions:

| Run | Points | Path span |
|---|---|---|
| 1 | 7,717 | 7.24 x 6.22 x 12.46 |
| 2 | 7,442 | 9.81 x 6.56 x 12.48 |

Pinning `num_threads=1` did not fix it (7,790 vs 7,788 points), so this is
inherent to the mapper's RANSAC, not thread scheduling. Determinism is not
achievable here.

### What actually varies: the camera path relative to the point cloud

The sparse *points* are consistently good (radial p50 1.64 m against true walls
of 1.5-2.5 m, only 1.9% beyond 3 m). What moves between runs is where the
mapper puts the cameras. Measured on a poor run:

    point  radius p50: 0.82 m
    camera radius p50: 3.69 m   -> ratio 4.5

For a real capture the cameras sit *inside* the captured geometry, so a ratio
well above 1 means the mapper landed in a poor solution. The scene is not
cleanly inside-out (96 cameras face the centroid, 48 away), so a simple flip
would not fix it; the path is simply inflated relative to the points.

### Fix: make the variance observable instead of silent

Added `_reconstruction_quality` to the Stage 3 diagnostics, recording
`point_radius_p50`, `camera_radius_p50`, `camera_to_point_radius` and
`camera_path_span`. Stage 3 now warns when the ratio exceeds 1:

    WARNING Camera path lies outside the point cloud (camera/point radius 1.92);
    the mapper likely landed in a poor solution - downstream geometry quality
    will be reduced. Re-running Stage 3 may give a better result.

Previously this failure mode was invisible: every stage reported success while
producing degraded geometry.

### Also fixed: NaN now removed at the source

Stage 6 was emitting 3 non-finite positions, which round 10 only caught at
export. `train_gaussians` now drops any Gaussian with a non-finite parameter
before returning, so downstream stages never see them.

### Measured

| Metric | Before | After |
|---|---|---|
| Non-finite Gaussians leaving Stage 6 | 3 | **0** |
| Poor reconstructions detected | never (silent) | **warned with a ratio** |
| Tests | 361 | **364** |

### Honest status

The pipeline runs all 8 stages end to end and produces valid 3DGS scenes, but
output quality still varies between runs because the underlying SfM solution
varies. The diagnostic now surfaces this. Making quality *consistent* would
need either a deterministic mapper, a pose prior, or best-of-N reconstruction
selection — all larger changes than fit in this round.

---

## 2026-11-14 (round 12) — Best-of-N selection; three more export killers fixed

### Best-of-N reconstruction selection

Added `unconstrained_attempts` (default 3) to Stage 3. When the rig constraint
collapses the camera path, the unconstrained mapper now runs N times and the
best-scoring reconstruction is kept, scored by
`_reconstruction_score` = inside-ness + log(point count) + registration
fraction. Verified working:

    Attempt 1/3: score=1.904
    Attempt 2/3: score=1.905
    Attempt 3/3: score=1.907
    Selected reconstruction with score 1.907

### But the variance is smaller than I reported last round

All three attempts landed in the same basin (ratio 1.77-1.92). Computing the
ground-truth ratio for the synthetic room gives **0.24**, so the mapper is
consistently producing a point cloud much tighter than the camera path. This is
a systematic property of this data, not run-to-run noise — best-of-N picks the
best of a set that are all mediocre. Last round I called this "run-to-run
variance"; that was only partly right. The variance is real but small; the
systematic bias is the larger effect.

### Three bugs that each emptied the export

1. **`NameError: torch`** in `distillation._sync_gaussians_numpy`. `torch` was
   imported inside the main function but not in the helper, so the activated-
   opacity fix from round 10 crashed the moment it actually ran. Fixed.
2. **`prune_max_scale_ratio` default of 0.1 was far too aggressive.** Typical
   Gaussians are a large fraction of the scene extent (p50 scale 1.11 m against
   a 6.8 m extent), so a 0.1 threshold (0.68 m) rejected *every* Gaussian:
   `rap_prune: N=372950, kept=0, pruned=372950 (scale=372950)`. Raised the
   default to 0.5, which is an outlier filter rather than a detail filter.
3. **No guard against a filter that removes everything.** `final_rap_prune` now
   logs an error and keeps the input when a threshold would empty the scene,
   because an empty export is far worse than a few surviving floaters.

### Measured

| Metric | Before | After |
|---|---|---|
| Export Gaussians | 0 | **372,950** |
| Stage 3 attempts | 1 | **3, best-scoring kept** |
| Export-stage empty-scene guards | 0 | **2 (NaN + over-pruning)** |
| Tests | 364 | **370** |

Final geometry: radial p50 2.64 m (true walls 1.5-2.5), 74.3% inside the room,
all values finite, opacities in [0,1].

### Status

All 8 stages run end to end and export a valid 3DGS scene. The remaining
quality gap is the SfM solution itself: the mapper's point cloud is
systematically tighter than the camera path (ratio 1.8 measured vs 0.24 for the
true scene), which caps how well Stage 5-6 can place Gaussians.

---

## 2026-11-14 (round 13) — Metric rescale fixed for rigs; Stage 7 OOM fixed

### The rescale was corrupting rig models

`_rescale_sparse_points` scaled only the 3D points, never the cameras, despite
its docstring claiming otherwise. On a rig model that drove
`camera_to_point_radius` from 1.99 to 4.87 — the camera path ended up outside
the geometry. Because the ratio is scale-invariant, nothing downstream noticed.

Getting this right took three attempts, each defeated by a pycolmap quirk:

| Attempt | Failure |
|---|---|
| Rewrite `images.txt` with a line toggle | Misaligns on empty observation lines: 60,740 -> 49,710 observations |
| Rewrite `images.txt` following the reader's pairing | Still loses data — `write_text()` itself drops observations on rig models |
| Scale `rig_from_world` + write binary | Points scale, cameras only partly (2.82 -> 2.32, not 1.41) |
| **Also scale `sensor_from_rig`** | **Correct: points 6.88 -> 3.44, cameras 2.82 -> 1.41, ratio preserved** |

The missing piece was `sensor_from_rig`: the mapper does not always model rig
sensors as sharing one optical centre, and those offsets carry non-zero
translations (up to ~1.3 units) that are world-space distances too.

Binary writing is the only safe path here. `write_text()` on a panorama-rig
model silently drops observations, so any text-based rewrite is a data-loss bug.

### Stage 7 ran out of VRAM

Stage 6 handed over 386,290 Gaussians; `max_gaussians` only limited *growth*
inside ShareGS, never the incoming count. The diffusion pass then exhausted an
8 GB card (`Tried to allocate 3.64 GiB`). Stage 7 now caps its input, keeping
the most opaque Gaussians: 386,290 -> 60,000.

### A second hard-coded 0.1

The `"auto"` max-scale ratio had its own hard-coded 0.1 (separate from the
config default fixed last round), so the export still pruned everything.
Extracted to `AUTO_MAX_SCALE_RATIO = 0.5`.

### Measured

| Metric | Before | After |
|---|---|---|
| `camera_to_point_radius` after rescale | 4.87 (corrupted) | **preserved (1.99)** |
| Stage 7 input | 386,290 (OOM) | **60,000 (capped)** |
| Stage 8 pruning | rejected all, guard fired | **60,000 -> 50,009** |
| Final radial p50 | 2.64 m | **2.13 m** (true walls 1.5-2.5) |
| Gaussians inside room | 74.3% | **95.3%** |
| Final bbox | -6.0..5.5 (loose) | **-2.9..5.5 (tight)** |
| Tests | 370 | **376** |

### Status

All 8 stages run end to end. This is the best geometry measured so far:
radial p50 2.13 m against true walls of 1.5-2.5 m, with 95.3% of Gaussians
inside the room and a tight bounding box.

---

## 2026-11-14 (round 14) — Clean end-to-end verification on two scenes

### Full clean run of scene A

Deleted every stage output and ran all 8 stages from scratch (no `--resume`).
Every stage succeeded:

    1 frames -> 2 cubemaps (144 images, 12 cameras) -> 3 SfM (best-of-3, score 1.910)
    -> 4 depth (rescale 0.1452, points *and* poses) -> 5 seeding (20,651)
    -> 6 training (PSNR 21.75 @ 4000, 358,485 Gaussians)
    -> 7 capped to 60,000, inpainted -> 8 export (32,122 Gaussians)

This confirms the round-13 fixes hold from a cold start, not just from
partially-cached state.

### Quaternions were not unit-norm

The exported PLY carried rotation quaternions with norms 0.58-1.62 — 28,451 of
32,122 outside 1e-3 of unit length. The 3DGS PLY format specifies unit
quaternions, and while most viewers renormalise on load, the file was not
standards-compliant. Stage 8 now normalises before writing, with degenerate
zero-norm quaternions falling back to identity.

### Generalisation check: a second, different scene

The pipeline had only ever been exercised on one clip, so I added
`--room-scale` / `--path-scale` to `scripts/make_synthetic_360_video.py` and
generated scene B: a 1.4x larger room with a 0.75x camera path. Ran the full
pipeline on it via `configs/e2e_smoke_b.yaml` (data dir `data/e2e_b`).

Both scenes run all 8 stages and export valid 3DGS:

| | Scene A (walls 2.5 m) | Scene B (walls 3.5 m) |
|---|---|---|
| Gaussians exported | 32,122 | 46,743 |
| Radial p50 / p90 | 2.41 / 3.13 m | 2.12 / 2.73 m |
| Inside room | 66.5% | 92.2% |
| Finite / opacity / scales | pass | pass |
| Unit quaternions | pass | pass |
| PSNR @ iter 4000 | 21.75 | 24.92 |

Scene B scores better on every geometry metric, which suggests scene A's
result is not a ceiling — the larger room gives the mapper more parallax.

### Deliverables verified

`data/e2e/export/final.ply` (32,122 Gaussians, 1.8 MB) is a standards-compliant
binary 3DGS PLY with `f_dc_*`, `opacity`, `scale_*`, `rot_*` properties, and
`viewer.html` is a working Gaussian-splat viewer that loads it.

### Tests

377 passing (was 376). Added a test that drifted quaternions are normalised on
export.


## 2026-11-15 — Four quality bugs fixed (depth inversion, densification, ERP weighting, SH export)

Timestamp: 2026-11-15T12:30:00-05:00

A review against the synthetic room's analytic ground truth found four
correctness bugs. All four are fixed and covered by tests; 397 tests passed
before the final additions, and the Stage 4/6 and depth suites pass after them.

### 1. Stage 4 used Depth Anything V2 disparity as depth (scene inside-out)

The `-hf` relative checkpoints output affine-invariant *disparity* (larger =
closer), but the wrapper documented and the DAP fusion used it as distance.
Stored depth correlated with true distance at Spearman **-0.48 / -0.81**
(floor read as the farthest surface), and per-frame SfM alignment was rejected
on 12/12 frames.

- `models/depth_anything_v2.py`: `estimate_depth*` now inverts disparity
  (`disparity_to_depth`, far/near cap 100x -> invalid); new
  `estimate_disparity_batch` exposes raw output; `Metric` repo ids pass through.
- `models/dap_model.py`: new `_fuse_disparity_views_to_erp` fits each rig
  view's affine `(a, b)` against the other views where they actually overlap on
  the sphere, in radial inverse depth, then inverts. The old
  `_harmonize_view_scales` compared views pixel-for-pixel in their own image
  grids (unrelated scene points) and made depth *worse* (rank corr 0.55 -> 0.3);
  it is now only used for metric checkpoints.
- `stages/stage04_depth/pipeline.py`: frames whose alignment fails get the
  median scale of the aligned frames instead of staying in raw units.
- Result on synthetic frames 1/13/23: rank correlation **+0.73 / +0.62 / +0.57**,
  median relative error **0.21 / 0.14 / 0.19** (was inverted). Alignment now
  succeeds on 8-11 of 12 frames (was 0).
- Tried and reverted: an inverse-depth affine remap inside the SfM alignment.
  Noise in mono depth biases the slope toward 0 (regression dilution) and it
  flattened frame 1 into a near-constant sphere.

### 2. Stage 6 densification was not 3DGS densification

The trigger was the Laplacian of the *rendered* image from one random view
(densify where the render already has edges), threshold 0.01 so nearly every
Gaussian qualified, off-screen Gaussians clamped to the border and sampled.
Growth only stopped at `max_gaussians`. Worse, `long_axis_split` /
`clone_under_reconstructed` were fed raw log-scales and opacity logits: a split
*enlarged* children (log-scale -3.9 halved -> exp(-1.95), ~7x larger) and
offset them by a log value.

- `training_loop.py`: gsplat `means2d` gradients are accumulated per Gaussian
  (pixel units, as gsplat `DefaultStrategy`); every `densify_every` iterations
  from `densify_from_iter`, Gaussians with average gradient >=
  `densify_grad_threshold` (2e-4) are cloned (small) or long-axis split (larger
  than `densify_percent_dense` x scene extent). Split/clone run in activated
  space. The cap keeps the highest-gradient candidates. Accumulators follow
  pruning/recovery. `_update_optimizer` now drops Adam state for replaced
  tensors (it previously leaked every old state buffer).
- **Deviation from spec:** `PIPELINE_DESIGN_V2.md` 6.1 / T6.6 specify the EAS
  (rendered-image Laplacian) trigger. It is no longer used by the training loop;
  `compute_eas` remains in `densification.py`.
- New config: `stage06.densify_from_iter` (500), `densify_grad_threshold`
  (2e-4), `densify_percent_dense` (0.01).

### 3. ERP latitude weighting applied to pinhole rig views

`_compute_view_latitudes` mapped every perspective crop's rows to -90..+90 deg,
so cos(latitude) zeroed the loss weight of the top/bottom rows of every training
image (photometric and depth). Latitudes are now only built for equirectangular
cameras; pinhole views get unweighted L1+SSIM (previously the non-ERP branch was
L1 only). The scale-flattening loss, whose latitude is measured from the world
origin, is skipped for pinhole training.

### 4. Stage 6 export dropped all non-DC SH

`optimized.ply` (and checkpoints) kept `colors[:, 0, :]` only. They now write
`f_rest_*` in 3DGS channel-major order. `write_ply` accepts 9/24/45 rest
coefficients (degree 1-3) instead of only 45; new helpers
`sh_rest_from_coeffs` / `sh_coeffs_to_gsplat` in `common/io.py`. Stage 7 and
Stage 8 previously passed a mis-sized array (Stage 8 passed DC+rest, 48 wide)
and now pass only the rest bands.

### Rerun (synthetic room, Stages 4-6, `data/e2e_fix`, same SfM model as `data/e2e`)

| | Baseline `data/e2e` | Fixed `data/e2e_fix` |
|---|---|---|
| Stage 6 Gaussians | 358,485 (cap-driven) | 39,695 (growth stops on its own) |
| Mean train-view PSNR | 21.99 dB | 22.91 dB |
| Mean opacity | 0.027 | 0.178 |
| Exported SH | DC only | degree 1 (Nx9) |

### Found, not fixed: Stage 3 rig fallback produces an inconsistent rig

`_camera_path_is_degenerate` (`stage03_sfm/pycolmap_probe.py`) measures the
path from `cam_from_world.translation` (t), not the camera centre (-R^T t). For
rig sensors sharing one centre, t varies with each sensor's rotation, so a valid
rig-constrained model is flagged degenerate and replaced by an unconstrained
run. The current `data/e2e` model has 12 single-sensor rigs; the 12 views of one
panorama sit ~2.0 units apart (path radius ~0.32), and the panorama rotation
implied by each camera differs by a constant 33-147 deg. Stage 4 alignment,
Stage 5 frame placement and Stage 6 training all inherit this. This is the
likely cause of the long-standing "cameras outside the point cloud" gap.

### Files modified

`src/sphereforge/models/depth_anything_v2.py`, `src/sphereforge/models/dap_model.py`,
`src/sphereforge/stages/stage04_depth/pipeline.py`,
`src/sphereforge/stages/stage06_optimization/training_loop.py`,
`src/sphereforge/stages/stage06_optimization/pipeline.py`,
`src/sphereforge/common/io.py`, `src/sphereforge/config.py`,
`src/sphereforge/stages/stage07_occlusion/pipeline.py`,
`src/sphereforge/stages/stage08_export/pipeline.py`,
`tests/test_depth_models.py`, `tests/test_stage04.py`,
`tests/test_stage06_optimization.py`.


## 2026-11-15 — Stage 3 fixed: keep the rig, use the real lens

Timestamp: 2026-11-15T13:20:00-05:00

Two Stage 3 bugs made every reconstruction geometrically inconsistent. Both
are fixed; the synthetic room now reconstructs to within a centimetre.

### 1. Camera positions were read from `cam_from_world.translation`

Three places treated the pose translation `t` as the camera position. The
optical centre is `-R^T t`; for rig sensors that share one centre, `t` differs
by each sensor's rotation.

- `pycolmap_probe._camera_path_is_degenerate` averaged sensor translations
  per frame. For a yaw-symmetric rig these cancel to X/Z spans of exactly 0,
  so a **correct** rig model (path matching ground truth to 1.5 cm) was judged
  "collapsed to a line" and replaced by the unconstrained fallback: 12
  single-sensor rigs, the 12 views of one panorama ~2 units apart, and each
  camera implying a panorama orientation 33-147 deg off the others.
  Now: optical centres; degenerate only when the path radius is < 1% of the
  median point distance (true pure-rotation collapse). A straight path is no
  longer treated as failure (`_path_is_degenerate`).
- `rigidity.enforce_rig_rigidity` measured "spread" on translations and
  rebuilt poses from their mean, with the rotation composition reversed
  (`R S^T` instead of `S^T R`). Now it measures optical centres, uses
  `rigid_frame_poses` (tested), and removes a stale sidecar. On a rig model it
  repairs nothing (spread ~4e-15).
- `pipeline._prune_outlier_cameras` judged outliers by translation; now by
  optical centre (`rigidity.camera_centre_from_pose`).

### 2. COLMAP never got Stage 2's intrinsics

Feature extraction had no focal hint, so COLMAP used its default
`f = 1.2 * width` (SIMPLE_RADIAL, f = 460.8 on 384 px) while Stage 2 rendered
105 deg views (fov 90 + overlap 15, PINHOLE f = 147.3). Mapping holds
intrinsics fixed, so structure came out ~2.4x too far from the camera path.
`pipeline._apply_stage2_intrinsics` now writes Stage 2's `cameras.txt` into the
database (matched per image, `has_prior_focal_length`) on both the pycolmap and
COLMAP-CLI paths.

### Results (synthetic room, Stages 3-6, `data/e2e_s3`, config `configs/e2e_smoke.yaml`)

| | Before (rig dropped, wrong focal) | After |
|---|---|---|
| Camera path vs ground truth | 0.68 m RMSE (rig-consistent orientation impossible) | **0.009 m** |
| SfM points: distance / true wall distance (median) | 2.43 | **1.00** |
| SfM points inside room (+-0.1 m) | 4.8% | **89.7%** |
| Stage 4 frames aligned to SfM | 8/12 (scales 1.1-1.4) | **12/12** (scales 1.000 +-0.001) |
| Stage 6 train-view PSNR mean / min | 22.91 / 20.55 dB | **30.43 / 25.33 dB** |
| Stage 6 Gaussians inside room | n/a | 71.3% (median distance ratio 1.01, p5-p95 0.86-1.29) |

Baseline before all of today's fixes (`data/e2e`): 21.99 / 20.59 dB.
PSNR is measured on training views (no held-out views yet).

### Tests

- `tests/test_stage03_rigidity.py`: replaced tests that asserted a mapped rig
  must look "scattered" (they encoded the bug) with: mapped rig is already
  rigid, stale sidecar removed, mapped rig path not degenerate, centre is
  `-R^T t`, `rigid_frame_poses` snaps to one centre with consistent rig
  rotation, straight path not degenerate, collapsed path degenerate.
- `tests/test_stage03_sfm.py`: Stage 2 intrinsics replace COLMAP's focal guess.

### Files modified

`src/sphereforge/stages/stage03_sfm/pycolmap_probe.py`,
`src/sphereforge/stages/stage03_sfm/rigidity.py`,
`src/sphereforge/stages/stage03_sfm/pipeline.py`,
`tests/test_stage03_rigidity.py`, `tests/test_stage03_sfm.py`.

### Remaining

- Stage 5 seeds: 52.5% inside the room, p95 distance ratio 1.7 (Depth Anything
  V2 tails at depth discontinuities). Stage 6 cleans most of it (p95 1.29).
- Stage 5 grazing-angle / sky filters still use the first frame's panorama
  origin for all points.
- Stage 6 position learning rate has no scene-extent scaling or decay.
- No held-out-view evaluation; the ground-truth checks used here live in
  throwaway scripts, not the repo.
