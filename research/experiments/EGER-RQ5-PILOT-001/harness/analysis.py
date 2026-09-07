"""Deterministic analysis from raw trial records (P172 §12).

PO-2 accounting repair: ALL aggregate numbers are derived from raw trial
records through this script. No manually typed totals. The report must be
generated from this module's output.

Denominators (P172 §12):
- planned trials: 8 (2 tasks × 2 Oracles × 2 replications)
- completed trials: completion_status == COMPLETED
- Oracle evaluations: every Oracle invocation (initial + per-iteration + final,
  including retries)
- successful Oracle evaluations: is_success == True
- provider failures / retry attempts / EvidenceArtifacts: counted from records
"""

from __future__ import annotations

from typing import Any, Dict, List

from .trial_runner import derive_trial_metrics


def _count_evaluations(record: Dict[str, Any]) -> Dict[str, int]:
    """Count Oracle evaluations in a trial record.

    total = the recorded oracle_call_count (the actual number of Oracle
    invocations made by the runner — initial + iterations + explicit final,
    where the accept-path final reuses the last iteration result).
    successful = invocations that returned is_success.
    """
    total = record.get("oracle_call_count", 0)
    successful = 0
    if record.get("initial_oracle_result", {}).get("is_success"):
        successful += 1
    for it in record.get("iterations", []):
        ores = it.get("oracle_result")
        if ores is not None and ores.get("is_success"):
            successful += 1
    if (
        record.get("final_oracle_result", {}).get("is_success")
        and not record.get("accept_reached", False)
        and record.get("completion_status") == "COMPLETED"
    ):
        successful += 1
    return {"total": total, "successful": successful}


def analyze_trials(trials: List[Dict[str, Any]], planned: int = 8) -> Dict[str, Any]:
    """Deterministic aggregation. `trials` must be the raw records list.

    Derives PO-1/PO-2/PO-3 from raw records only. Returns a dict that is
    the single source of truth for the report.
    """
    completed = [t for t in trials if t.get("completion_status") == "COMPLETED"]
    failed = [t for t in trials if t.get("completion_status") == "FAILED"]

    # Derive metrics for every trial (deterministic)
    derived = []
    for t in trials:
        m = derive_trial_metrics(t)
        row = dict(t)
        row["_po1"] = m["completion_quality"]
        row["_po3"] = m["oracle_detected_improvement"]
        row["_evidence_compatible"] = m["evidence_compatible"]
        row["_evaluation_count"] = m["evaluation_count"]
        row["_no_timing_constraint"] = m["no_timing_constraint_iterations"]
        row["_metadata_unqualified"] = m["metadata_unqualified_iterations"]
        row["_qualified_accept"] = m["qualified_accept"]
        derived.append(row)

    # ---- Oracle evaluations (all attempts) ----
    eval_total = sum(_count_evaluations(t)["total"] for t in trials)
    eval_successful = sum(_count_evaluations(t)["successful"] for t in trials)

    # ---- EvidenceArtifacts (PO-2) ----
    # An evaluation produced evidence if is_success and an evidence hash is present.
    evidence_artifacts = 0
    for t in trials:
        if t.get("initial_oracle_result", {}).get("is_success") and t.get("initial_evidence_hash"):
            evidence_artifacts += 1
        for it in t.get("iterations", []):
            ores = it.get("oracle_result")
            if ores and ores.get("is_success") and it.get("evidence_hash"):
                evidence_artifacts += 1
        if (
            t.get("final_oracle_result", {}).get("is_success")
            and not t.get("accept_reached", False)
            and t.get("completion_status") == "COMPLETED"
        ):
            evidence_artifacts += 1

    # ---- Failure/retry accounting ----
    failure_kinds: Dict[str, int] = {}
    for t in failed:
        kind = t.get("failure_kind", "UNKNOWN")
        failure_kinds[kind] = failure_kinds.get(kind, 0) + 1
    retry_attempts = sum(t.get("retry_count", 0) for t in trials)

    # ---- Per-condition PO-1/PO-3 ----
    conditions = sorted({(t.get("task_id"), t.get("oracle")) for t in trials})
    per_condition = {}
    for task, oracle in conditions:
        rows = [r for r in derived if r.get("task_id") == task and r.get("oracle") == oracle]
        per_condition[f"{task}-{oracle}"] = {
            "count": len(rows),
            "completed": sum(1 for r in rows if r.get("completion_status") == "COMPLETED"),
            "po1": {
                "ROBUST": sum(1 for r in rows if r["_po1"] == "ROBUST"),
                "MARGINAL": sum(1 for r in rows if r["_po1"] == "MARGINAL"),
                "FAILED": sum(1 for r in rows if r["_po1"] == "FAILED"),
            },
            "po3": {
                "IMPROVED": sum(1 for r in rows if r["_po3"] == "IMPROVED"),
                "NOT_IMPROVED": sum(1 for r in rows if r["_po3"] == "NOT_IMPROVED"),
                "WORSE": sum(1 for r in rows if r["_po3"] == "WORSE"),
                "NOT_MEASURABLE": sum(1 for r in rows if r["_po3"] == "NOT_MEASURABLE"),
            },
            "evidence_compatible": sum(1 for r in rows if r["_evidence_compatible"]),
            "qualified_accept": sum(1 for r in rows if r["_qualified_accept"]),
        }

    # ---- Per-Oracle PO-2 with explicit denominators ----
    per_oracle = {}
    for oracle in sorted({t.get("oracle") for t in trials}):
        rows = [r for r in derived if r.get("oracle") == oracle]
        evals = sum(_count_evaluations(t)["total"] for t in trials if t.get("oracle") == oracle)
        evals_ok = sum(_count_evaluations(t)["successful"] for t in trials if t.get("oracle") == oracle)
        compatible = sum(1 for r in rows if r["_evidence_compatible"])
        per_oracle[oracle] = {
            "trials": len(rows),
            "completed_trials": sum(1 for r in rows if r.get("completion_status") == "COMPLETED"),
            "oracle_evaluations": evals,
            "successful_evaluations": evals_ok,
            "evidence_compatible_trials": compatible,
            "qualified_accepts": sum(1 for r in rows if r["_qualified_accept"]),
            "no_timing_constraint_iterations": sum(len(r["_no_timing_constraint"]) for r in rows),
            "metadata_unqualified_iterations": sum(len(r["_metadata_unqualified"]) for r in rows),
        }

    # ---- Verification decisions ----
    accept_count = 0
    reject_count = 0
    for t in trials:
        for it in t.get("iterations", []):
            dec = it.get("verification_decision")
            if dec == "ACCEPT":
                accept_count += 1
            elif dec == "REJECT":
                reject_count += 1

    # ---- Per-model aggregation (P185 model-comparison dimension) ----
    # Present only when records carry a model label (the 16-trial
    # model-comparison matrix). Derived from raw records, deterministic.
    models = sorted({t.get("model") for t in trials if t.get("model")})
    per_model = {}
    per_model_condition = {}
    if models:
        for model in models:
            rows = [r for r in derived if r.get("model") == model]
            per_model[model] = {
                "trials": len(rows),
                "completed_trials": sum(1 for r in rows if r.get("completion_status") == "COMPLETED"),
                "failed_trials": sum(1 for r in rows if r.get("completion_status") == "FAILED"),
                "po1": {
                    "ROBUST": sum(1 for r in rows if r["_po1"] == "ROBUST"),
                    "MARGINAL": sum(1 for r in rows if r["_po1"] == "MARGINAL"),
                    "FAILED": sum(1 for r in rows if r["_po1"] == "FAILED"),
                },
                "po3": {
                    "IMPROVED": sum(1 for r in rows if r["_po3"] == "IMPROVED"),
                    "NOT_IMPROVED": sum(1 for r in rows if r["_po3"] == "NOT_IMPROVED"),
                    "WORSE": sum(1 for r in rows if r["_po3"] == "WORSE"),
                    "NOT_MEASURABLE": sum(1 for r in rows if r["_po3"] == "NOT_MEASURABLE"),
                },
                "evidence_compatible": sum(1 for r in rows if r["_evidence_compatible"]),
                "qualified_accept": sum(1 for r in rows if r["_qualified_accept"]),
                "retry_attempts": sum(r.get("retry_count", 0) for r in rows),
                "oracle_evaluations": sum(_count_evaluations(t)["total"] for t in trials if t.get("model") == model),
            }
        # Per (model, task, oracle) condition breakdown
        cond_keys = sorted({
            (r.get("model"), r.get("task_id"), r.get("oracle"))
            for r in derived if r.get("model")
        })
        for model, task, oracle in cond_keys:
            rows = [r for r in derived
                    if r.get("model") == model and r.get("task_id") == task
                    and r.get("oracle") == oracle]
            key = f"{model}|{task}-{oracle}"
            per_model_condition[key] = {
                "count": len(rows),
                "completed": sum(1 for r in rows if r.get("completion_status") == "COMPLETED"),
                "po1": {
                    "ROBUST": sum(1 for r in rows if r["_po1"] == "ROBUST"),
                    "MARGINAL": sum(1 for r in rows if r["_po1"] == "MARGINAL"),
                    "FAILED": sum(1 for r in rows if r["_po1"] == "FAILED"),
                },
                "po3": {
                    "IMPROVED": sum(1 for r in rows if r["_po3"] == "IMPROVED"),
                    "NOT_IMPROVED": sum(1 for r in rows if r["_po3"] == "NOT_IMPROVED"),
                    "WORSE": sum(1 for r in rows if r["_po3"] == "WORSE"),
                    "NOT_MEASURABLE": sum(1 for r in rows if r["_po3"] == "NOT_MEASURABLE"),
                },
                "evidence_compatible": sum(1 for r in rows if r["_evidence_compatible"]),
                "qualified_accept": sum(1 for r in rows if r["_qualified_accept"]),
            }

    return {
        "planned_trials": planned,
        "total_trials": len(trials),
        "completed_trials": len(completed),
        "failed_trials": len(failed),
        "oracle_evaluations": eval_total,
        "successful_oracle_evaluations": eval_successful,
        "evidence_artifacts": evidence_artifacts,
        "retry_attempts": retry_attempts,
        "failure_kinds": failure_kinds,
        "accept_decisions": accept_count,
        "reject_decisions": reject_count,
        "per_condition": per_condition,
        "per_oracle": per_oracle,
        "per_model": per_model,
        "per_model_condition": per_model_condition,
        "_trials": [
            {
                "trial_id": r.get("trial_id"),
                "model": r.get("model"),
                "task_id": r.get("task_id"),
                "oracle": r.get("oracle"),
                "replication_id": r.get("replication_id"),
                "attempt": r.get("attempt"),
                "retry_count": r.get("retry_count"),
                "completion_status": r.get("completion_status"),
                "failure_kind": r.get("failure_kind"),
                "po1": r["_po1"],
                "po3": r["_po3"],
                "evidence_compatible": r["_evidence_compatible"],
                "qualified_accept": r["_qualified_accept"],
                "metadata_unqualified_iterations": r["_metadata_unqualified"],
                "evaluation_count": r["_evaluation_count"],
                "iteration_count": r.get("iteration_count"),
                "oracle_call_count": r.get("oracle_call_count"),
                "final_sdc_hash": r.get("final_sdc_hash"),
            }
            for r in derived
        ],
    }