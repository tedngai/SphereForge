"""SphereForge progress logging utilities.

Reads and writes TASKS.md and PROGRESS.md to track pipeline task completion.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class TaskProgress:
    """A single task's progress entry."""

    task_id: str
    status: str  # TODO, IN_PROGRESS, DONE, BLOCKED
    completed_at: str | None = None
    output_files: list[str] = field(default_factory=list)
    modified_files: list[str] = field(default_factory=list)
    notes: str = ""
    deviations: str = ""
    issues: str = ""


# Stage name mapping
STAGE_NAMES = {
    0: "Infrastructure",
    1: "Frame Selection",
    2: "Cubemap + COLMAP Prep",
    3: "COLMAP SfM",
    4: "Depth Estimation",
    5: "Gaussian Seeding",
    6: "Optimization",
    7: "Occlusion Recovery",
    8: "Export",
}


def parse_stage_from_id(task_id: str) -> int:
    """Extract stage number from task ID like 'T2.9' → 2."""
    match = re.match(r"T(\d+)", task_id)
    return int(match.group(1)) if match else 0


def read_tasks_status(tasks_path: Path | None = None) -> dict[str, str]:
    """Read all task IDs and their statuses from TASKS.md.

    Returns:
        Dict mapping task_id → status string.
    """
    if tasks_path is None:
        tasks_path = Path(__file__).parent.parent.parent / "TASKS.md"

    if not tasks_path.exists():
        return {}

    content = tasks_path.read_text(encoding="utf-8")
    statuses: dict[str, str] = {}

    # Match table rows like: | T0.1 | TODO | ... |
    for match in re.finditer(r"\|\s*(T\d+\.\d+)\s*\|\s*(\w+)\s*\|", content):
        task_id = match.group(1)
        status = match.group(2)
        if status in ("TODO", "IN_PROGRESS", "DONE", "BLOCKED"):
            statuses[task_id] = status

    return statuses


def read_progress(progress_path: Path | None = None) -> dict:
    """Read progress summary from PROGRESS.md and cross-reference with TASKS.md.

    Returns:
        Dict with 'total', 'completed', 'in_progress', 'blocked', 'stages' keys.
    """
    project_dir = Path(__file__).parent.parent.parent
    if progress_path is None:
        progress_path = project_dir / "PROGRESS.md"

    tasks_path = project_dir / "TASKS.md"
    statuses = read_tasks_status(tasks_path)

    # Group by stage
    stages: dict[str, dict] = {}
    for task_id, status in statuses.items():
        stage_num = parse_stage_from_id(task_id)
        stage_key = f"Stage {stage_num}: {STAGE_NAMES.get(stage_num, 'Unknown')}"
        if stage_key not in stages:
            stages[stage_key] = {"total": 0, "done": 0, "in_progress": 0, "blocked": 0}
        stages[stage_key]["total"] += 1
        if status == "DONE":
            stages[stage_key]["done"] += 1
        elif status == "IN_PROGRESS":
            stages[stage_key]["in_progress"] += 1
        elif status == "BLOCKED":
            stages[stage_key]["blocked"] += 1

    total = len(statuses)
    completed = sum(1 for s in statuses.values() if s == "DONE")
    in_progress = sum(1 for s in statuses.values() if s == "IN_PROGRESS")
    blocked = sum(1 for s in statuses.values() if s == "BLOCKED")

    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "blocked": blocked,
        "stages": stages,
    }


def log_task_completion(
    task_id: str,
    notes: str = "",
    files_created: list[str] | None = None,
    files_modified: list[str] | None = None,
    deviations: str = "",
    issues: str = "",
    progress_path: Path | None = None,
    tasks_path: Path | None = None,
    dry_run: bool = False,
) -> None:
    """Log a task completion to PROGRESS.md and update status in TASKS.md.

    Args:
        task_id: Task identifier like 'T2.3'.
        notes: Brief description of what was implemented.
        files_created: List of file paths created.
        files_modified: List of file paths modified.
        deviations: Any differences from the spec.
        issues: Any problems encountered.
        progress_path: Path to PROGRESS.md (auto-detected if None).
        tasks_path: Path to TASKS.md (auto-detected if None).
        dry_run: If True, validate that the replacement would succeed but
            do not write any files. Raises ``RuntimeError`` if the task
            row cannot be found or is already marked DONE.
    """
    project_dir = Path(__file__).parent.parent.parent
    if progress_path is None:
        progress_path = project_dir / "PROGRESS.md"
    if tasks_path is None:
        tasks_path = project_dir / "TASKS.md"

    timestamp = datetime.now(timezone.utc).isoformat()

    # Update TASKS.md status
    if tasks_path.exists():
        content = tasks_path.read_text(encoding="utf-8")
        # Validate that the task exists and is not already DONE
        if task_id not in content:
            raise RuntimeError(f"Task {task_id} not found in {tasks_path}")
        # Find the row and current status using a more robust pattern
        row_pattern = rf"\|\s*{re.escape(task_id)}\s*\|\s*(\w+)\s*\|"
        row_match = re.search(row_pattern, content)
        if not row_match:
            raise RuntimeError(
                f"Could not locate status cell for task {task_id} in {tasks_path}. "
                "The table format may have changed."
            )
        current_status = row_match.group(1)
        if current_status == "DONE":
            if dry_run:
                return  # Already done — nothing to validate
            # Silently skip re-logging if already DONE
        else:
            pattern = rf"(\|\s*{re.escape(task_id)}\s*\|\s*){re.escape(current_status)}(\s*\|)"
            replacement = rf"\g<1>DONE\2"
            new_content = re.sub(pattern, replacement, content)
            if new_content == content:
                raise RuntimeError(
                    f"Failed to update status for {task_id} in {tasks_path}. "
                    f"Current status '{current_status}' may not match the expected pattern."
                )
            if not dry_run:
                tasks_path.write_text(new_content, encoding="utf-8")

    if dry_run:
        return

    # Append to PROGRESS.md
    entry_lines = [
        f"\n### [{task_id}] Task Completed",
        f"- **Completed:** {timestamp}",
        f"- **Files created:**",
    ]
    for f in files_created or []:
        entry_lines.append(f"  - `{f}`")
    if not files_created:
        entry_lines.append("  - (none)")

    entry_lines.append("- **Files modified:**")
    for f in files_modified or []:
        entry_lines.append(f"  - `{f}`")
    if not files_modified:
        entry_lines.append("  - (none)")

    entry_lines.append(f"- **Implementation notes:** {notes}")
    if deviations:
        entry_lines.append(f"- **Deviations:** {deviations}")
    if issues:
        entry_lines.append(f"- **Issues:** {issues}")

    entry = "\n".join(entry_lines) + "\n"

    if progress_path.exists():
        content = progress_path.read_text(encoding="utf-8")
        # Insert before the Statistics section
        if "## Statistics" in content:
            content = content.replace("## Statistics", entry + "\n## Statistics")
        else:
            content += "\n" + entry
        progress_path.write_text(content, encoding="utf-8")
    else:
        progress_path.write_text(entry, encoding="utf-8")


def check_dependencies(task_id: str, tasks_path: Path | None = None) -> list[str]:
    """Check if all dependencies for a task are DONE.

    Args:
        task_id: Task identifier like 'T2.3'.

    Returns:
        List of dependency task IDs that are NOT done. Empty list = all clear.
    """
    project_dir = Path(__file__).parent.parent.parent
    if tasks_path is None:
        tasks_path = project_dir / "TASKS.md"

    if not tasks_path.exists():
        return []

    content = tasks_path.read_text(encoding="utf-8")
    statuses = read_tasks_status(tasks_path)

    # Find the row for this task and extract the Depends On column
    # Pattern: | T2.3 | TODO | description | T0.6, T2.2 | ...
    pattern = rf"\|\s*{re.escape(task_id)}\s*\|\s*\w+\s*\|[^|]*\|\s*([^|]+)\s*\|"
    match = re.search(pattern, content)
    if not match:
        return []

    deps_str = match.group(1).strip()
    if deps_str == "—" or not deps_str:
        return []

    # Parse dependency IDs (handles formats like "T0.5, T0.6", "T1.1–T1.5", "T6.1–T6.10")
    dep_ids: list[str] = []
    for part in re.split(r"[,;]", deps_str):
        part = part.strip()
        # Handle ranges like "T2.1–T2.10" or "T1.1-T1.5"
        range_match = re.match(r"(T\d+)\.(\d+)\s*[–\-]\s*\1\.(\d+)", part)
        if range_match:
            prefix = range_match.group(1)
            start = int(range_match.group(2))
            end = int(range_match.group(3))
            for i in range(start, end + 1):
                dep_ids.append(f"{prefix}.{i}")
        # Handle single task IDs
        elif re.match(r"T\d+\.\d+", part):
            dep_ids.append(part)

    # Return deps that are not DONE
    not_done = [d for d in dep_ids if statuses.get(d) != "DONE"]
    return not_done
