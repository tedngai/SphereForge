"""CSV-backed sharpness score cache.

Caches per-frame sharpness scores to a CSV file so that re-running the
pipeline avoids recomputing the Laplacian variance for frames that have
already been scored.
"""

from __future__ import annotations

import csv
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class SharpnessCache:
    """A simple CSV-backed cache for sharpness scores.

    The CSV file has three columns: ``frame_path``, ``sharpness``,
    ``timestamp``.  If the file does not exist it is created with a header
    row on first write.

    Args:
        cache_path: Path to the CSV file used for persistence.
    """

    HEADER = "frame_path,sharpness,timestamp"

    def __init__(self, cache_path: Path) -> None:
        self.cache_path = Path(cache_path)
        self._cache: dict[str, float] = {}
        self._loaded = False

        # Create parent dirs and header if needed
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.cache_path.exists():
            self.cache_path.write_text(self.HEADER + "\n", encoding="utf-8")
            logger.debug("Created sharpness cache at %s", self.cache_path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_loaded(self) -> None:
        """Load the CSV into memory if it has not been read yet."""
        if self._loaded:
            return
        self._cache.clear()
        if self.cache_path.exists():
            with open(self.cache_path, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    self._cache[row["frame_path"]] = float(row["sharpness"])
        self._loaded = True
        logger.debug("Loaded %d entries from sharpness cache", len(self._cache))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, frame_path: Path) -> float | None:
        """Return the cached sharpness score for *frame_path*, or ``None``.

        Args:
            frame_path: Path to the frame image.

        Returns:
            The cached sharpness score, or ``None`` if the frame is not
            in the cache.
        """
        self._ensure_loaded()
        key = str(frame_path)
        return self._cache.get(key)

    def set(self, frame_path: Path, score: float) -> None:
        """Append a sharpness score to the cache.

        The entry is both stored in the in-memory dict and appended to the
        CSV file on disk.

        Args:
            frame_path: Path to the frame image.
            score: Sharpness score to store.
        """
        self._ensure_loaded()
        key = str(frame_path)
        self._cache[key] = score

        timestamp = time.time()
        with open(self.cache_path, "a", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow([key, score, timestamp])

        logger.debug("Cached sharpness %.4f for %s", score, frame_path)

    def has(self, frame_path: Path) -> bool:
        """Check whether *frame_path* has a cached sharpness score.

        Args:
            frame_path: Path to the frame image.

        Returns:
            ``True`` if the frame is in the cache, ``False`` otherwise.
        """
        self._ensure_loaded()
        return str(frame_path) in self._cache
