"""Frozen-matrix orchestrator (P172 §9 / P177 / P178).

Executes the frozen 2×2×2 trial matrix through the repaired trial runner
and the deterministic analysis module. The SAME orchestrator is used for:

- the P177/P178 fixture dry-run (deterministic FakeOracle/FakeModelProvider),
  and
- (with separate authorization) the real EGER-RQ5-PILOT-002 run (real Ṛta /
  OpenSTA / model providers from providers.py).

Pre-run protocol assertions (P172 §9, P177 §7):
- Exactly the frozen 8 trials, in frozen order (Ṛta first in T1,
  OpenSTA first in T2) — assert_matrix_order() must pass BEFORE trial 1.
- No reordering or re-randomization is possible after construction.

P178 candidate-identity audit: after the run, audit_candidate_identity()
mechanically verifies every identity the frozen protocol guarantees —
task-shared initial candidate across Oracle arms, single candidate path per
trial iteration, and validity gating before Oracle evaluation.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from .matrix import frozen_matrix, assert_matrix_order
from .model_matrix import (
    frozen_model_matrix,
    assert_model_matrix_order,
    MODEL_IDS,
    MODEL_TIMEOUTS,
)
from .tasks import TASKS
from .trial_runner import run_trial, MAX_RETRIES, sha256_text
from .analysis import analyze_trials

# Max iterations per attempt (frozen: P169 protocol). Do not change after
# results are visible.
MAX_ITERATIONS = 3


def audit_candidate_identity(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Mechanical candidate-identity audit over raw trial records (P178).

    Verifies every identity property the frozen P169/P172 protocol actually
    guarantees — the corrected, protocol-true reading of checklist item 2
    ("same candidate SDC evaluated by both Oracles"):

    1. Task-shared initial candidate across Oracle arms: every trial of a
       task evaluates the byte-identical frozen initial SDC (equal hash).
    2. Single candidate path per trial iteration: each iteration contains
       exactly one generated candidate, its recorded bytes hash to the
       recorded candidate_sdc_hash, and an Oracle evaluation occurred only
       after the candidate was classified VALID_SDC (gated before
       evaluation). No Oracle-specific variant, no silent repair, no second
       generation.
    3. Every attempt (including retries) satisfies the above.

    NOTE: byte-identity of REVISED candidates across the Ṛta and OpenSTA
    arms is NOT guaranteed by the frozen design (per-Oracle pipeline
    trials, feedback-driven revision — see the P169 experimental unit), so
    it is not audited here. See EGER-P178 record §4 for the boundary
    statement and correction of the P177 item-2 overclaim.

    Returns a deterministic audit dict: {ok, violations, checks, ...}.
    """
    violations: List[str] = []
    checks: List[Dict[str, Any]] = []

    for rec in records:
        task = TASKS[rec["task_id"]]
        attempts = rec.get("attempts") or [rec]
        for attempt in attempts:
            check = {
                "trial_id": rec["trial_id"],
                "attempt": attempt.get("attempt", 1),
            }
            # 1. Initial candidate == frozen task initial SDC (bytes + hash).
            init_ok = (
                attempt.get("initial_sdc") == task["initial_sdc"]
                and attempt.get("initial_sdc_hash")
                == sha256_text(task["initial_sdc"])
            )
            check["initial_matches_task_sdc"] = init_ok
            if not init_ok:
                violations.append(
                    f"{rec['trial_id']} attempt {attempt.get('attempt')}: "
                    f"initial SDC differs from frozen task SDC"
                )
            # 2. Per-iteration single-candidate path + gating.
            #    Two legal states per iteration:
            #    (a) a VALID_SDC candidate was produced, its recorded bytes
            #        hash to candidate_sdc_hash, and it was evaluated; or
            #    (b) the validity gate rejected the model output BEFORE any
            #        Oracle evaluation — no candidate bytes, no oracle_result.
            iter_ok = True
            for it in attempt.get("iterations", []):
                cand = it.get("candidate_sdc")
                cand_hash = it.get("candidate_sdc_hash")
                ores = it.get("oracle_result")
                validity = it.get("candidate_validity")
                if cand is not None:
                    bytes_ok = cand_hash == sha256_text(cand)
                    gated_ok = validity == "VALID_SDC"
                else:
                    # No candidate: must have been rejected pre-evaluation.
                    bytes_ok = True
                    gated_ok = ores is None and validity != "VALID_SDC"
                if not (bytes_ok and gated_ok):
                    iter_ok = False
                    violations.append(
                        f"{rec['trial_id']} attempt {attempt.get('attempt')} "
                        f"iteration {it.get('iteration')}: candidate bytes/gating "
                        f"violation (bytes_ok={bytes_ok}, gated_ok={gated_ok})"
                    )
            check["iterations_single_path_ok"] = iter_ok
            checks.append(check)

    # 3. Cross-arm shared task substrate: same-task trials share the initial
    #    SDC hash across the Ṛta and OpenSTA arms.
    task_initial_hashes = {}
    for rec in records:
        task_initial_hashes.setdefault(rec["task_id"], set()).add(
            rec.get("initial_sdc_hash")
        )
    shared_initial = {
        task: sorted(h) for task, h in sorted(task_initial_hashes.items())
    }
    shared_ok = all(len(h) == 1 for h in shared_initial.values())
    if not shared_ok:
        violations.append(f"shared task initial violated: {shared_initial}")

    return {
        "ok": len(violations) == 0,
        "violations": violations,
        "shared_task_initial_hashes": shared_initial,
        "shared_initial_across_arms": shared_ok,
        "checks": checks,
    }


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
        {"records", "analysis", "identity_audit"} — deterministic
        aggregation plus the candidate-identity audit over raw records.
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
    identity_audit = audit_candidate_identity(records)
    return {
        "records": records,
        "analysis": analysis,
        "identity_audit": identity_audit,
    }


def run_model_matrix(
    callables: Callable[[Dict[str, Any]], tuple],
    normalizer,
    gate,
    max_iterations: int = MAX_ITERATIONS,
    max_retries: int = MAX_RETRIES,
) -> Dict[str, Any]:
    """Run the frozen 16-trial model-comparison matrix (P185 §2).

    Identical construction contract to run_matrix, with the model
    dimension added: the callable receives a frozen model-matrix row dict
    (including "model" / "model_id") and returns (oracle_call, model_call)
    for that trial. The pre-run assertion (assert_model_matrix_order) must
    pass BEFORE trial 1 and raises on violation.

    The model label is recorded on every trial record via run_trial(model=...)
    and the deterministic analysis adds per_model / per_model_condition
    aggregation.

    Returns:
        {"records", "analysis", "identity_audit"}.
    """
    trials = frozen_model_matrix()
    # Protocol assertion BEFORE trial 1 (P185 §2). Raises on violation.
    assert_model_matrix_order(trials)

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
            model=row["model"],
        )
        records.append(record)

    analysis = analyze_trials(records, planned=len(trials))
    identity_audit = audit_candidate_identity(records)
    return {
        "records": records,
        "analysis": analysis,
        "identity_audit": identity_audit,
    }
