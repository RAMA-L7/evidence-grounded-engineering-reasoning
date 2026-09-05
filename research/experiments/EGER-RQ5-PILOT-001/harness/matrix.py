"""Frozen counterbalanced trial matrix (P172 §9).

P169 §9 required counterbalanced Oracle ordering. P170 ran Ṛta-first in
both task blocks — a documented deviation. This module freezes the
repaired matrix: Ṛta-first in the T1 block, OpenSTA-first in the T2 block.
The execution script MUST call assert_matrix_order() before trial 1.
"""

from __future__ import annotations

from typing import Dict, List, Any

# Frozen trial matrix (P172 §9). Execution order is fixed and asserted.
FROZEN_MATRIX: List[Dict[str, Any]] = [
    {"order": 1, "trial_id": "T1-Rta-R1",   "task_id": "T1", "oracle": "Rta",     "replication_id": 1, "oracle_first": "Rta"},
    {"order": 2, "trial_id": "T1-OpenSTA-R1", "task_id": "T1", "oracle": "OpenSTA", "replication_id": 1, "oracle_first": "Rta"},
    {"order": 3, "trial_id": "T1-Rta-R2",   "task_id": "T1", "oracle": "Rta",     "replication_id": 2, "oracle_first": "Rta"},
    {"order": 4, "trial_id": "T1-OpenSTA-R2", "task_id": "T1", "oracle": "OpenSTA", "replication_id": 2, "oracle_first": "Rta"},
    {"order": 5, "trial_id": "T2-OpenSTA-R1", "task_id": "T2", "oracle": "OpenSTA", "replication_id": 1, "oracle_first": "OpenSTA"},
    {"order": 6, "trial_id": "T2-Rta-R1",   "task_id": "T2", "oracle": "Rta",     "replication_id": 1, "oracle_first": "OpenSTA"},
    {"order": 7, "trial_id": "T2-OpenSTA-R2", "task_id": "T2", "oracle": "OpenSTA", "replication_id": 2, "oracle_first": "OpenSTA"},
    {"order": 8, "trial_id": "T2-Rta-R2",   "task_id": "T2", "oracle": "Rta",     "replication_id": 2, "oracle_first": "OpenSTA"},
]

# Expected per-task-block first Oracle (counterbalancing invariant)
_EXPECTED_FIRST_PER_TASK = {
    "T1": "Rta",
    "T2": "OpenSTA",
}


def frozen_matrix() -> List[Dict[str, Any]]:
    """Return a copy of the frozen matrix."""
    return [dict(row) for row in FROZEN_MATRIX]


def assert_matrix_order(trials: List[Dict[str, Any]]) -> None:
    """Assert the given trial list satisfies the frozen counterbalanced order.

    Checks:
    1. Exactly the 8 frozen trial IDs, each exactly once.
    2. Order matches the frozen matrix order.
    3. Within each task block, the first Oracle is the frozen first Oracle.

    Raises AssertionError (via pytest-style assert) on violation.
    """
    frozen = FROZEN_MATRIX
    if len(trials) != len(frozen):
        raise AssertionError(
            f"trial count mismatch: expected {len(frozen)}, got {len(trials)}"
        )

    frozen_ids = [row["trial_id"] for row in frozen]
    actual_ids = [row["trial_id"] for row in trials]

    if actual_ids != frozen_ids:
        raise AssertionError(
            f"trial order mismatch:\n  frozen:  {frozen_ids}\n  actual:  {actual_ids}"
        )

    # Per-task first-Oracle check
    seen_first: Dict[str, str] = {}
    for row in trials:
        task = row["task_id"]
        if task not in seen_first:
            seen_first[task] = row["oracle"]
    for task, expected_first in _EXPECTED_FIRST_PER_TASK.items():
        actual_first = seen_first.get(task)
        if actual_first != expected_first:
            raise AssertionError(
                f"counterbalancing violated for {task}: expected first Oracle "
                f"{expected_first}, got {actual_first}"
            )


def validate_matrix_row_count(trials: List[Dict[str, Any]]) -> None:
    """Validate the 2×2×2 replication structure (P169 frozen design)."""
    counts: Dict[tuple, int] = {}
    for row in trials:
        key = (row["task_id"], row["oracle"])
        counts[key] = counts.get(key, 0) + 1
    expected = 2  # replications per task-oracle cell
    for key, count in sorted(counts.items()):
        if count != expected:
            raise AssertionError(
                f"cell {key} has {count} trials, expected {expected}"
            )