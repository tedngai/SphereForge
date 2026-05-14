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

## Statistics

- **Total tasks:** 94 (94 DONE, 0 remaining)
- **Completion rate:** 100%
- **Source code:** ~15,500 lines
- **Test code:** ~4,900 lines
- **Total Python:** ~20,400 lines

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

1. **Rasterizer is a STUB** (T6.11): `render_gaussians()` returns random tensors. Must integrate gsplat (Apache 2.0) or INRIA 3DGS CUDA rasterizer for actual training. **FIXED 2026-05-02**: now raises RuntimeError with install instructions when gsplat is missing.
2. **PanDA is a STUB** (T4.1): `PanDAModel` raises NotImplementedError. Weights must be obtained separately.
3. **EscherNet is a STUB** (T7.7): `EscherNetWrapper` raises NotImplementedError. Weights under RAIL-M license.
4. **RPG360 license** (T2.9): No license file. Contact authors or implement from paper.
5. **OmniRoam is a STUB** (T7.12): Requires Adobe Research License + 20GB+ VRAM.
