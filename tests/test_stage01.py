"""Tests for Stage 1: Video Ingestion & Frame Selection.

Covers:
  1. Sharpness scoring (checkerboard vs. blurred)
  2. Chunk-based sharpest-frame selection
  3. Luminance filtering
  4. SharpnessCache hit / miss
  5. End-to-end pipeline with synthetic data
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from sphereforge.common.io import read_image, write_image
from sphereforge.stages.stage01_frames.frame_selection import (
    select_sharpest_per_chunk,
)
from sphereforge.stages.stage01_frames.luminance_filter import (
    filter_by_luminance,
    filter_frame_list,
)
from sphereforge.stages.stage01_frames.sharpness import compute_sharpness
from sphereforge.stages.stage01_frames.sharpness_cache import SharpnessCache


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sharp_image() -> np.ndarray:
    """A sharp checkerboard image (uint8, HxWx3)."""
    h, w = 64, 64
    # 8x8-pixel checkerboard squares
    checker = np.indices((h, w)).sum(axis=0) // 8 % 2
    img = np.stack([checker * 255] * 3, axis=-1).astype(np.uint8)
    return img


@pytest.fixture
def blurry_image(sharp_image: np.ndarray) -> np.ndarray:
    """A Gaussian-blurred version of the sharp image."""
    return cv2.GaussianBlur(sharp_image, (31, 31), sigmaX=5)


@pytest.fixture
def dark_image() -> np.ndarray:
    """An almost-black image (mean luminance ≈ 5)."""
    img = np.full((64, 64, 3), 5, dtype=np.uint8)
    return img


@pytest.fixture
def bright_image() -> np.ndarray:
    """An almost-white image (mean luminance ≈ 250)."""
    img = np.full((64, 64, 3), 250, dtype=np.uint8)
    return img


@pytest.fixture
def mid_image() -> np.ndarray:
    """A mid-grey image (mean luminance ≈ 128)."""
    img = np.full((64, 64, 3), 128, dtype=np.uint8)
    return img


@pytest.fixture
def frame_dir(tmp_path: Path, sharp_image: np.ndarray, blurry_image: np.ndarray) -> Path:
    """Directory with 6 synthetic frame PNGs (alternating sharp/blurry)."""
    d = tmp_path / "frames"
    d.mkdir()
    for i in range(6):
        img = sharp_image if i % 2 == 0 else blurry_image
        write_image(d / f"frame_{i + 1:06d}.png", img)
    return d


# ---------------------------------------------------------------------------
# T1.2 — Sharpness
# ---------------------------------------------------------------------------


class TestSharpness:
    """Tests for compute_sharpness."""

    def test_sharp_image_has_higher_score(
        self, sharp_image: np.ndarray, blurry_image: np.ndarray
    ) -> None:
        """A checkerboard image should score higher than a blurred version."""
        s_sharp = compute_sharpness(sharp_image)
        s_blurry = compute_sharpness(blurry_image)
        assert s_sharp > s_blurry, (
            f"Sharp image ({s_sharp:.2f}) should be > blurry ({s_blurry:.2f})"
        )

    def test_grayscale_input(self, sharp_image: np.ndarray) -> None:
        """compute_sharpness should accept a 2D grayscale image."""
        gray = cv2.cvtColor(sharp_image, cv2.COLOR_RGB2GRAY)
        score = compute_sharpness(gray)
        assert score > 0.0

    def test_uniform_image_has_low_sharpness(self) -> None:
        """A uniform-colour image should have near-zero sharpness."""
        uniform = np.full((64, 64, 3), 128, dtype=np.uint8)
        score = compute_sharpness(uniform)
        assert score < 1.0, f"Uniform image sharpness should be ≈0, got {score}"


# ---------------------------------------------------------------------------
# T1.3 — SharpnessCache
# ---------------------------------------------------------------------------


class TestSharpnessCache:
    """Tests for SharpnessCache."""

    def test_miss_then_set_then_hit(self, tmp_path: Path) -> None:
        """A new key should return None (miss); after set(), it should hit."""
        cache = SharpnessCache(tmp_path / "cache.csv")
        fp = Path("/tmp/frame_000001.png")

        # Miss
        assert cache.get(fp) is None
        assert not cache.has(fp)

        # Set
        cache.set(fp, 42.5)

        # Hit
        assert cache.has(fp)
        assert cache.get(fp) == pytest.approx(42.5)

    def test_persistence(self, tmp_path: Path) -> None:
        """Data written to the cache should survive re-instantiation."""
        csv_path = tmp_path / "cache.csv"
        fp = Path("/tmp/frame_000001.png")

        cache1 = SharpnessCache(csv_path)
        cache1.set(fp, 99.9)

        cache2 = SharpnessCache(csv_path)
        assert cache2.get(fp) == pytest.approx(99.9)

    def test_csv_header(self, tmp_path: Path) -> None:
        """A new cache file should have the correct header row."""
        csv_path = tmp_path / "cache.csv"
        SharpnessCache(csv_path)
        lines = csv_path.read_text().strip().split("\n")
        assert lines[0] == "frame_path,sharpness,timestamp"

    def test_multiple_entries(self, tmp_path: Path) -> None:
        """Multiple entries should all be retrievable."""
        cache = SharpnessCache(tmp_path / "cache.csv")
        paths = [Path(f"/tmp/frame_{i:06d}.png") for i in range(5)]
        scores = [10.0 * i for i in range(5)]

        for fp, s in zip(paths, scores):
            cache.set(fp, s)

        for fp, s in zip(paths, scores):
            assert cache.get(fp) == pytest.approx(s)


# ---------------------------------------------------------------------------
# T1.4 — Frame Selection
# ---------------------------------------------------------------------------


class TestFrameSelection:
    """Tests for select_sharpest_per_chunk."""

    def test_picks_sharpest_per_chunk(
        self, frame_dir: Path, sharp_image: np.ndarray
    ) -> None:
        """Within each 2-frame chunk, the sharp frame should be selected."""
        frame_paths = sorted(frame_dir.glob("frame_*.png"))
        cache_path = frame_dir.parent / "sharpness_cache.csv"
        cache = SharpnessCache(cache_path)

        # chunk_size=2 means 3 chunks of 2 frames each
        selected = select_sharpest_per_chunk(frame_paths, chunk_size=2, cache=cache)

        assert len(selected) == 3  # 6 frames / 2 = 3 chunks
        # Every selected frame should be a "sharp" one (even-indexed: 1, 3, 5)
        for sp in selected:
            img = read_image(sp)
            # Sharp image is checkerboard — should have high sharpness
            assert compute_sharpness(img) > compute_sharpness(
                cv2.GaussianBlur(sharp_image, (31, 31), sigmaX=5)
            )

    def test_empty_input(self, tmp_path: Path) -> None:
        """An empty frame list should return an empty list."""
        cache = SharpnessCache(tmp_path / "cache.csv")
        result = select_sharpest_per_chunk([], chunk_size=10, cache=cache)
        assert result == []

    def test_invalid_chunk_size(self, tmp_path: Path) -> None:
        """A chunk_size < 1 should raise ValueError."""
        cache = SharpnessCache(tmp_path / "cache.csv")
        with pytest.raises(ValueError):
            select_sharpest_per_chunk([Path("/tmp/x.png")], chunk_size=0, cache=cache)


# ---------------------------------------------------------------------------
# T1.5 — Luminance Filter
# ---------------------------------------------------------------------------


class TestLuminanceFilter:
    """Tests for luminance filtering functions."""

    def test_dark_image_fails(self, dark_image: np.ndarray) -> None:
        """A dark image (mean ≈ 5) should fail the default luminance filter."""
        assert not filter_by_luminance(dark_image, min_lum=10.0, max_lum=245.0)

    def test_bright_image_fails(self, bright_image: np.ndarray) -> None:
        """A bright image (mean ≈ 250) should fail the default luminance filter."""
        assert not filter_by_luminance(bright_image, min_lum=10.0, max_lum=245.0)

    def test_mid_image_passes(self, mid_image: np.ndarray) -> None:
        """A mid-grey image (mean ≈ 128) should pass the luminance filter."""
        assert filter_by_luminance(mid_image, min_lum=10.0, max_lum=245.0)

    def test_grayscale_input(self, mid_image: np.ndarray) -> None:
        """A 2D grayscale image should be accepted."""
        gray = cv2.cvtColor(mid_image, cv2.COLOR_RGB2GRAY)
        assert filter_by_luminance(gray, min_lum=10.0, max_lum=245.0)

    def test_filter_frame_list(
        self, tmp_path: Path, dark_image: np.ndarray, bright_image: np.ndarray,
        mid_image: np.ndarray,
    ) -> None:
        """filter_frame_list should keep only frames within the luminance range."""
        d = tmp_path / "lum_frames"
        d.mkdir()
        dark_path = d / "dark.png"
        bright_path = d / "bright.png"
        mid_path = d / "mid.png"
        write_image(dark_path, dark_image)
        write_image(bright_path, bright_image)
        write_image(mid_path, mid_image)

        result = filter_frame_list(
            [dark_path, mid_path, bright_path],
            min_lum=10.0,
            max_lum=245.0,
        )
        assert len(result) == 1
        assert result[0] == mid_path


# ---------------------------------------------------------------------------
# T1.7 — End-to-end pipeline (with synthetic frames, no FFmpeg)
# ---------------------------------------------------------------------------


class TestPipeline:
    """Integration test for run_stage01.

    Because we cannot guarantee FFmpeg in CI, the end-to-end test
    bypasses frame extraction by pre-populating the extracted-frames
    directory and then calling the downstream steps directly.
    """

    def test_stage01_end_to_end(
        self,
        tmp_path: Path,
        sharp_image: np.ndarray,
        blurry_image: np.ndarray,
        mid_image: np.ndarray,
    ) -> None:
        """Full pipeline: extract → select → filter → copy.

        We simulate frame extraction by writing frames directly, then
        run select + filter + copy manually (since we don't assume FFmpeg).
        """
        # Set up "extracted" frames directory manually
        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        frames_dir = output_dir / "_extracted"
        frames_dir.mkdir()

        # Write 4 frames: sharp, blurry, sharp, blurry
        write_image(frames_dir / "frame_000001.png", sharp_image)
        write_image(frames_dir / "frame_000002.png", blurry_image)
        write_image(frames_dir / "frame_000003.png", sharp_image)
        write_image(frames_dir / "frame_000004.png", blurry_image)

        frame_paths = sorted(frames_dir.glob("frame_*.png"))
        assert len(frame_paths) == 4

        # Step 2: Select sharpest per chunk
        cache_path = output_dir / "sharpness_cache.csv"
        cache = SharpnessCache(cache_path)
        selected = select_sharpest_per_chunk(frame_paths, chunk_size=2, cache=cache)
        assert len(selected) == 2

        # Step 3: Filter by luminance — checkerboard mean ≈ 128, so it passes
        filtered = filter_frame_list(
            selected, min_lum=10.0, max_lum=245.0
        )
        assert len(filtered) == 2

        # Step 4: Copy to output
        import shutil as _shutil

        final: list[Path] = []
        for src in filtered:
            dst = output_dir / src.name
            _shutil.copy2(src, dst)
            final.append(dst)

        assert len(final) == 2
        for p in final:
            assert p.exists()