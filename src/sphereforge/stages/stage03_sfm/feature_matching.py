"""Stage 3.2: COLMAP feature matching.

Wraps the COLMAP matcher CLIs (exhaustive, sequential, vocabulary_tree)
to establish 2D-2D correspondences between images in the database.
"""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger("sphereforge.stage03.feature_matching")


def _run_colmap_matcher(matcher_name: str, database_path: Path, extra_args: list[str] | None = None) -> None:
    """Execute a single COLMAP matcher command.

    Args:
        matcher_name: COLMAP matcher sub-command (e.g. ``"sequential_matcher"``).
        database_path: Path to the COLMAP database.
        extra_args: Optional additional CLI arguments.

    Raises:
        RuntimeError: If the subprocess returns a non-zero exit code.
    """
    cmd: list[str] = [
        "colmap", matcher_name,
        "--database_path", str(database_path),
    ]
    if extra_args:
        cmd.extend(extra_args)

    logger.info("Running COLMAP %s on database %s", matcher_name, database_path)
    result = subprocess.run(cmd, capture_output=True, text=True, check=False,
                            env={
                                **os.environ,
                                "QT_QPA_PLATFORM": "offscreen",
                                "PATH": "/home/tngai/.local/bin:" + os.environ.get("PATH", ""),
                            "LD_LIBRARY_PATH": "/home/tngai/miniconda3/lib:"
                                + os.environ.get("LD_LIBRARY_PATH", ""),
                            })
    if result.returncode != 0:
        logger.error("COLMAP %s stderr:\n%s", matcher_name, result.stderr)
        raise RuntimeError(
            f"COLMAP {matcher_name} failed (exit code {result.returncode}): "
            f"{result.stderr[:500]}"
        )
    logger.info("COLMAP %s completed successfully.", matcher_name)


def run_feature_matching(
    database_path: Path,
    matcher_type: str = "sequential+vocabulary_tree",
    vocab_tree_path: Path | None = None,
) -> None:
    """Run COLMAP feature matching on the database.

    Dispatches to the appropriate COLMAP matcher based on *matcher_type*:

    - ``"exhaustive"`` → ``exhaustive_matcher``
    - ``"sequential"`` → ``sequential_matcher``
    - ``"sequential+vocabulary_tree"`` → ``sequential_matcher`` first,
      then ``vocab_tree_matcher`` (if *vocab_tree_path* is provided).
    - ``"vocab_tree"`` → ``vocab_tree_matcher``

    Args:
        database_path: Path to the COLMAP database file.
        matcher_type: Matcher strategy string.
        vocab_tree_path: Path to the vocabulary tree file (required for
            vocabulary-tree-based matching).

    Raises:
        RuntimeError: If any COLMAP matcher subprocess returns non-zero.
        ValueError: If ``"vocab_tree"`` or ``"sequential+vocabulary_tree"``
            is requested but *vocab_tree_path* is ``None``.
    """
    database_path = Path(database_path)

    if matcher_type == "exhaustive":
        _run_colmap_matcher("exhaustive_matcher", database_path)

    elif matcher_type == "sequential":
        _run_colmap_matcher("sequential_matcher", database_path)

    elif matcher_type == "sequential+vocabulary_tree":
        # Run sequential matcher first
        _run_colmap_matcher("sequential_matcher", database_path)
        # Then run vocabulary tree matcher if vocab tree is provided
        if vocab_tree_path is not None:
            extra = ["--VocabTreeMatching.vocab_tree_path", str(vocab_tree_path)]
            _run_colmap_matcher("vocab_tree_matcher", database_path, extra)
        else:
            logger.warning(
                "vocab_tree_path not provided; skipping vocabulary_tree "
                "matching for 'sequential+vocabulary_tree' mode."
            )

    elif matcher_type == "vocab_tree":
        if vocab_tree_path is None:
            raise ValueError(
                "vocab_tree_path is required when matcher_type is 'vocab_tree'"
            )
        extra = ["--VocabTreeMatching.vocab_tree_path", str(vocab_tree_path)]
        _run_colmap_matcher("vocab_tree_matcher", database_path, extra)

    else:
        raise ValueError(
            f"Unknown matcher_type '{matcher_type}'. Expected one of: "
            "'exhaustive', 'sequential', 'sequential+vocabulary_tree', 'vocab_tree'."
        )

    logger.info("Feature matching completed (matcher_type=%s).", matcher_type)
