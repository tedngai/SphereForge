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
