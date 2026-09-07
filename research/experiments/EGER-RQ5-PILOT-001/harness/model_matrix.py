"""Frozen 16-trial model-comparison matrix (P183 §10 / P185 §2).

The model-comparison experiment extends the frozen RQ-5 design by one
dimension — LLM model identity:

    2 models × 2 tasks × 2 Oracles × 2 replications = 16 planned trials
    (8 trials per model)

Frozen properties (P183 §10, §11; P185 §2):
- Baseline model block first (mimo), comparison model block second
  (nemotron) — fixed ordering (the two model blocks are independent).
- Within each model block, the PILOT-002 counterbalanced order is
  preserved: T1 block is Ṛta-first, T2 block is OpenSTA-first.
- Trial IDs follow the P183 convention: T<task>-<model>-<Oracle>-R<rep>,
  with "R" = Ṛta (so "T1-mimo-R1" = T1, mimo, Ṛta, replication 1 and
  "T1-mimo-OpenSTA-R1" = T1, mimo, OpenSTA, replication 1).

The execution driver MUST call assert_model_matrix_order() before trial 1
(P185 §2: "The exact frozen order must be asserted before trial 1").
No reordering after results are observed.
"""

from __future__ import annotations

from typing import Dict, List, Any

# Frozen model identifiers (P184 §3). Do not substitute.
MODEL_LABELS = ("mimo", "nemotron")
MODEL_IDS = {
    "mimo": "opencode/mimo-v2.5-free",
    "nemotron": "opencode/nemotron-3.5-lightning-free",
}
# Per-model model-call timeout (P184 §3): nemotron is a slower agent-mode
# model (300s) vs mimo (180s). Infrastructure, not a protocol parameter.
MODEL_TIMEOUTS = {
    "mimo": 180,
    "nemotron": 300,
}

# Per-model block template (PILOT-002 frozen counterbalanced order).
_BLOCK = [
    {"task_id": "T1", "oracle": "Rta",     "replication_id": 1, "oracle_first": "Rta"},
    {"task_id": "T1", "oracle": "OpenSTA", "replication_id": 1, "oracle_first": "Rta"},
    {"task_id": "T1", "oracle": "Rta",     "replication_id": 2, "oracle_first": "Rta"},
    {"task_id": "T1", "oracle": "OpenSTA", "replication_id": 2, "oracle_first": "Rta"},
    {"task_id": "T2", "oracle": "OpenSTA", "replication_id": 1, "oracle_first": "OpenSTA"},
    {"task_id": "T2", "oracle": "Rta",     "replication_id": 1, "oracle_first": "OpenSTA"},
    {"task_id": "T2", "oracle": "OpenSTA", "replication_id": 2, "oracle_first": "OpenSTA"},
    {"task_id": "T2", "oracle": "Rta",     "replication_id": 2, "oracle_first": "OpenSTA"},
]


def _trial_id(model: str, block: Dict[str, Any]) -> str:
    task = block["task_id"]
    oracle = block["oracle"]
    rep = block["replication_id"]
    if oracle == "Rta":
        # P183 convention: the Ṛta trial is written "T<task>-<model>-R<rep>".
        return f"{task}-{model}-R{rep}"
    return f"{task}-{model}-{oracle}-R{rep}"


# Frozen 16-trial matrix (P183 §10 / P185 §2). Execution order is fixed.
FROZEN_MODEL_MATRIX: List[Dict[str, Any]] = []
_order = 0
for model in MODEL_LABELS:
    for block in _BLOCK:
        _order += 1
        FROZEN_MODEL_MATRIX.append({
            "order": _order,
            "trial_id": _trial_id(model, block),
            "model": model,
            "model_id": MODEL_IDS[model],
            "task_id": block["task_id"],
            "oracle": block["oracle"],
            "replication_id": block["replication_id"],
            "oracle_first": block["oracle_first"],
        })


def frozen_model_matrix() -> List[Dict[str, Any]]:
    """Return a copy of the frozen 16-trial model-comparison matrix."""
    return [dict(row) for row in FROZEN_MODEL_MATRIX]


def assert_model_matrix_order(trials: List[Dict[str, Any]]) -> None:
    """Assert the given trial list satisfies the frozen 16-trial order.

    Checks:
    1. Exactly the 16 frozen trial IDs, each exactly once.
    2. Order matches the frozen matrix order.
    3. Model blocks: baseline (mimo) first, comparison (nemotron) second.
    4. Within each model block and task block, the first Oracle is the
       frozen first Oracle (T1 Ṛta-first, T2 OpenSTA-first).

    Raises AssertionError on violation. Must pass BEFORE trial 1.
    """
    frozen = FROZEN_MODEL_MATRIX
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

    # Model block order: baseline first, comparison second.
    first_model = trials[0]["model"]
    if first_model != "mimo":
        raise AssertionError(f"baseline model must run first, got {first_model}")
    # Model blocks must be contiguous (no interleaving).
    seen: Dict[str, int] = {}
    for row in trials:
        seen[row["model"]] = seen.get(row["model"], 0) + 1
    if seen.get("mimo") != 8 or seen.get("nemotron") != 8:
        raise AssertionError(f"per-model trial counts must be 8/8, got {seen}")

    # Per (model, task) block first-Oracle check.
    firsts: Dict[tuple, str] = {}
    for row in trials:
        key = (row["model"], row["task_id"])
        if key not in firsts:
            firsts[key] = row["oracle"]
    expected_firsts = {
        ("mimo", "T1"): "Rta",
        ("mimo", "T2"): "OpenSTA",
        ("nemotron", "T1"): "Rta",
        ("nemotron", "T2"): "OpenSTA",
    }
    for key, expected in expected_firsts.items():
        actual = firsts.get(key)
        if actual != expected:
            raise AssertionError(
                f"counterbalancing violated for {key}: expected first Oracle "
                f"{expected}, got {actual}"
            )


def validate_model_matrix_row_count(trials: List[Dict[str, Any]]) -> None:
    """Validate the 2×2×2×2 replication structure (P183 §9)."""
    counts: Dict[tuple, int] = {}
    for row in trials:
        key = (row["model"], row["task_id"], row["oracle"])
        counts[key] = counts.get(key, 0) + 1
    for key, count in sorted(counts.items()):
        if count != 2:
            raise AssertionError(
                f"cell {key} has {count} trials, expected 2 (replications)"
            )