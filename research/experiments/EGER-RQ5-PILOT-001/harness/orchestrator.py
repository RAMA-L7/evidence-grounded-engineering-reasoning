"""Frozen-matrix orchestrator (P172 §9 / P177).

Executes the frozen 2×2×2 trial matrix through the repaired trial runner
and the deterministic analysis module. The SAME orchestrator is used for:

- the P177 fixture dry-run (deterministic FakeOracle/FakeModelProvider), and
- (with separate authorization) the real EGER-RQ5-PILOT-002 run (real Ṛta /
  OpenSTA / model providers from providers.py).

Pre-run protocol assertions (P172 §9, P177 §7):
- Exactly the frozen 8 trials, in frozen order (Ṛta first in T1,
  OpenSTA first in T2) — assert_matrix_order() must pass BEFORE trial 1.
- No reordering or re-randomization is possible after construction.

The orchestrator itself makes no methodology decisions: trials are executed
in the order given, retries follow the frozen bounded-retry policy in
trial_runner, and all aggregates are derived from raw records by
analysis.analyze_trials.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from .matrix import frozen_matrix, assert_matrix_order
from .tasks import TASKS
from .trial_runner import run_trial, MAX_RETRIES
from .analysis import analyze_trials

# Max iterations per attempt (frozen: P169 protocol). Do not change after
# results are visible.
MAX_ITERATIONS = 3


def run_matrix(
    callables: Callable[[Dict[str, Any]], tuple],
    normalizer,
    gate,
    max_iterations: int = MAX_ITERATIONS,
    max_retries: int = MAX_RETRIES,
) -> Dict[str, Any]:
    """Run the frozen 8-trial matrix.

    Args:
        callables: a callable taking a frozen-matrix row dict and returning
            (oracle_call, model_call) for that trial. The dry-run driver
            supplies fixture providers; a future authorized execution gate
            supplies the real providers from providers.py. The SAME
            construction contract therefore applies to both.
        normalizer / gate: the real EGER pipeline components.

    Returns:
        {"records": [raw trial records...], "analysis": deterministic analysis}
    """
    trials = frozen_matrix()
    # Protocol assertion BEFORE trial 1 (P172 §9). Raises on violation.
    assert_matrix_order(trials)

    records: List[Dict[str, Any]] = []
    for row in trials:
        task = TASKS[row["task_id"]]
        oracle_call, model_call = callables(row)
        record = run_trial(
            trial_id=row["trial_id"],
            task_id=row["task_id"],
            oracle_name=row["oracle"],
            replication_id=row["replication_id"],
            execution_order=row["order"],
            initial_sdc=task["initial_sdc"],
            design_context=task["design_context"],
            oracle_call=oracle_call,
            model_call=model_call,
            normalizer=normalizer,
            gate=gate,
            max_iterations=max_iterations,
            max_retries=max_retries,
        )
        records.append(record)

    analysis = analyze_trials(records, planned=len(trials))
    return {"records": records, "analysis": analysis}
