"""Formal RQ4 runner — Controlled Experiment (EGER-CHANGE-007).

RQ4 Pipeline:
  For each BENCH2 task:
    SAME INITIAL CANDIDATE
         │
    ┌────┴────┐
    │         │
  CONTROL  TREATMENT
  (NO FB)  (STRUCTURED FB)
    │         │
    ↓         ↓
  FINAL_C   FINAL_T
    │         │
    └────┬────┘
         ↓
     COMPARE

CONTROL branch:
  initial candidate → model Call 2 (NO feedback) → final_control

TREATMENT branch:
  initial candidate → structured EvidenceArtifact → model Call 2 → final_treatment

The ONLY difference is whether structured feedback is provided.

EGER PRINCIPAL:
  A changed proposal proves response/activation.
  It does NOT by itself prove correctness improvement.

Frozen MODEL-005:
  provider = opencode
  model = opencode/mimo-v2.5-free
  temperature = 0.0
  tools = []
  max_tokens = 2048
  timeout = 60s
"""

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[3]))

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

from eger.engineer.model import LiveEngineerModel
from eger.engineer.adapter import EngineerAdapter
from eger.engineer.structured_feedback import render_structured_feedback
from eger.oracle.adapter import EvidenceOracle
from eger.oracle.schemas import DesignMetadata

# ---------------------------------------------------------------------------
# Frozen configuration per P069 / EGER-CHANGE-008
# ---------------------------------------------------------------------------
EXPERIMENT_VERSION = "EGER-EXP-001 v0.3"
BENCHMARK_VERSION = "EGER-BENCH-002 v0.1"
MODEL_ID = "EGER-MODEL-005"
MODEL_NAME = "opencode/mimo-v2.5-free"
PROMPT_VERSION = "eger.prompt.v1"
ORACLE_REVISION = "3b5c2f2"
METADATA_VERSION = "eger.design_metadata.v1"
CONDITION_CONTROL = "RQ4-CONTROL"
CONDITION_TREATMENT = "RQ4-TREATMENT"

TASKS = ["BENCH2-001", "BENCH2-002", "BENCH2-003", "BENCH2-004", "BENCH2-005", "BENCH2-006"]

MAX_MODEL_CALLS = 3  # 1 initial + 1 control + 1 treatment
MAX_ORACLE_CALLS = 3  # 1 initial + 1 control + 1 treatment

# ---------------------------------------------------------------------------
# Finding classification (P061 §14, pre-registered)
# ---------------------------------------------------------------------------
HARD_FINDING_CODES = {"SDC-005", "SDC-006", "SDC-007"}
WARNING_FINDING_CODES = {"SDC-020", "SDC-021", "SDC-028", "SDC-029", "SDC-030"}
# INFO: everything else

ERROR_SEVERITY = "error"
WARNING_SEVERITY = "warning"
INFO_SEVERITY = "info"


def _count_findings_by_severity(findings: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count findings by severity (error/warning/info)."""
    counts = {"error": 0, "warning": 0, "info": 0}
    for f in (findings or []):
        sev = (f.get("severity") or "info").lower()
        if sev in counts:
            counts[sev] += 1
    return counts


def _compute_error_delta(initial_findings: List[Dict[str, Any]],
                         final_findings: List[Dict[str, Any]]) -> int:
    """Primary metric: error-count delta.

    Only counts ERROR-severity findings (SDC-005, SDC-006, SDC-007).
    Negative delta = improvement (fewer errors).
    """
    initial_errors = sum(1 for f in (initial_findings or [])
                         if f.get("severity") == ERROR_SEVERITY)
    final_errors = sum(1 for f in (final_findings or [])
                       if f.get("severity") == ERROR_SEVERITY)
    return final_errors - initial_errors


# ---------------------------------------------------------------------------
# Metadata loading
# ---------------------------------------------------------------------------
METADATA_DIR = (Path(__file__).resolve().parents[1] /
                "EGER-BENCH-002" / "evaluator_context")


def _load_design_metadata(task_id: str) -> Optional[DesignMetadata]:
    """Load frozen evaluator-side design metadata for a task."""
    path = METADATA_DIR / f"{task_id}.design_metadata.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return DesignMetadata.from_dict(json.load(f))


# ---------------------------------------------------------------------------
# RQ4 single-task paired runner
# ---------------------------------------------------------------------------

def run_rq4_task(
    task_id: str,
    task_data: Dict[str, Any],
    oracle: EvidenceOracle,
    base_dir: Path,
    model: Optional[Any] = None,
    live: bool = False,
) -> Dict[str, Any]:
    """Execute the RQ4 paired experiment for a single task.

    Returns a manifest dict with both control and treatment results.
    """
    run_id = f"RQ4-{uuid.uuid4().hex[:8].upper()}"
    start = datetime.now(timezone.utc).isoformat()

    design_context = f"[{task_id}] {task_data['design_context']}"
    objective = f"[{task_id}] {task_data['objective']}"

    # Load evaluator-side metadata (Oracle only)
    design_metadata = _load_design_metadata(task_id)

    # Use provided model or default LiveEngineerModel (MODEL-004)
    engine_adapter = EngineerAdapter(
        model or LiveEngineerModel(
            timeout=60, max_tokens=2048, live=live,
            model=MODEL_NAME,
        )
    )

    # ---- RESULT CONTAINERS ----
    result: Dict[str, Any] = {
        "run_id": run_id,
        "experiment_version": EXPERIMENT_VERSION,
        "benchmark_version": BENCHMARK_VERSION,
        "model_id": MODEL_ID,
        "model_name": MODEL_NAME,
        "condition_control": CONDITION_CONTROL,
        "condition_treatment": CONDITION_TREATMENT,
        "task_id": task_id,
        "prompt_version": PROMPT_VERSION,
        "oracle_revision": ORACLE_REVISION,
        "metadata_version": METADATA_VERSION,
        "start_timestamp": start,
        "status": "IN_PROGRESS",
        "model_calls": 0,
        "oracle_calls": 0,
    }

    # =====================================================================
    # STAGE 1: Call 1 → initial candidate (shared between branches)
    # =====================================================================
    try:
        prop1 = engine_adapter.propose(
            design_context=design_context,
            objective=objective,
        )
        result["model_calls"] += 1
    except Exception as e:
        result["status"] = "INCOMPLETE_TREATMENT"
        result["failure_class"] = "MODEL_FAILURE"
        result["failure_message"] = str(e)
        result["end_timestamp"] = datetime.now(timezone.utc).isoformat()
        return result

    if not prop1.is_success:
        result["status"] = "INCOMPLETE_TREATMENT"
        result["failure_class"] = prop1.failure.kind if prop1.failure else "MODEL_FAILURE"
        result["failure_message"] = prop1.failure.message if prop1.failure else "unknown"
        result["end_timestamp"] = datetime.now(timezone.utc).isoformat()
        return result

    initial_candidate = prop1.candidate
    result["initial_candidate_hash"] = initial_candidate.candidate_hash
    result["initial_sdc_text"] = initial_candidate.sdc_text

    # =====================================================================
    # STAGE 2: Oracle 1 → initial evidence (with metadata)
    # =====================================================================
    try:
        oracle_result_1 = oracle.validate(
            initial_candidate.sdc_text,
            input_identity=initial_candidate.artifact_id,
            design_metadata=design_metadata,
        )
        result["oracle_calls"] += 1
    except Exception as e:
        result["status"] = "INCOMPLETE_TREATMENT"
        result["failure_class"] = "ORACLE_FAILURE"
        result["failure_message"] = str(e)
        result["end_timestamp"] = datetime.now(timezone.utc).isoformat()
        return result

    if not oracle_result_1.is_success:
        result["status"] = "INCOMPLETE_TREATMENT"
        result["failure_class"] = "ORACLE_FAILURE"
        result["failure_message"] = oracle_result_1.failure.message if oracle_result_1.failure else "oracle failed"
        result["end_timestamp"] = datetime.now(timezone.utc).isoformat()
        return result

    evidence_initial = oracle_result_1.evidence
    result["initial_evidence_hash"] = evidence_initial.evidence_hash
    result["initial_evidence_scope"] = evidence_initial.evidence_scope
    result["initial_findings"] = evidence_initial.findings
    initial_severity_counts = _count_findings_by_severity(evidence_initial.findings)
    result["initial_error_count"] = initial_severity_counts["error"]
    result["initial_warning_count"] = initial_severity_counts["warning"]
    result["initial_info_count"] = initial_severity_counts["info"]

    # Initial CVR from metadata_validation
    mv_initial = evidence_initial.provenance.get("metadata_validation")
    result["initial_CVR"] = (mv_initial["constraint_validity_rate"]
                             if mv_initial else None)

    # =====================================================================
    # STAGE 3: Structured feedback (deterministic from evidence_initial)
    # =====================================================================
    structured_feedback = render_structured_feedback(evidence_initial)
    result["structured_feedback_hash"] = hashlib.sha256(
        structured_feedback.encode("utf-8")
    ).hexdigest()

    # =====================================================================
    # STAGE 4A: CONTROL branch — model Call 2 WITHOUT feedback
    # =====================================================================
    try:
        prop_ctrl = engine_adapter.propose(
            design_context=design_context,
            existing_sdc=initial_candidate.sdc_text,
            objective=objective,
            evidence_summary=None,  # NO feedback
        )
        result["model_calls"] += 1
    except Exception as e:
        result["control_status"] = "INCOMPLETE"
        result["control_failure"] = str(e)
        prop_ctrl = None

    control_candidate = None
    control_candidate_hash = None
    if prop_ctrl and prop_ctrl.is_success:
        control_candidate = prop_ctrl.candidate
        control_candidate_hash = control_candidate.candidate_hash

    result["control_candidate_hash"] = control_candidate_hash
    result["control_proposal_changed"] = (
        control_candidate_hash != initial_candidate.candidate_hash
        if control_candidate_hash else None
    )

    # =====================================================================
    # STAGE 4B: TREATMENT branch — model Call 2 WITH structured feedback
    # =====================================================================
    try:
        prop_treat = engine_adapter.propose(
            design_context=design_context,
            existing_sdc=initial_candidate.sdc_text,
            objective=objective,
            evidence_summary=structured_feedback,  # YES feedback
        )
        result["model_calls"] += 1
    except Exception as e:
        result["treatment_status"] = "INCOMPLETE"
        result["treatment_failure"] = str(e)
        prop_treat = None

    treatment_candidate = None
    treatment_candidate_hash = None
    if prop_treat and prop_treat.is_success:
        treatment_candidate = prop_treat.candidate
        treatment_candidate_hash = treatment_candidate.candidate_hash

    result["treatment_candidate_hash"] = treatment_candidate_hash
    result["treatment_proposal_changed"] = (
        treatment_candidate_hash != initial_candidate.candidate_hash
        if treatment_candidate_hash else None
    )

    # =====================================================================
    # STAGE 5A: Oracle 2 → final control evidence (with metadata)
    # =====================================================================
    control_evidence = None
    if control_candidate:
        try:
            oracle_ctrl = oracle.validate(
                control_candidate.sdc_text,
                input_identity=control_candidate.artifact_id,
                design_metadata=design_metadata,
            )
            result["oracle_calls"] += 1
            if oracle_ctrl.is_success:
                control_evidence = oracle_ctrl.evidence
        except Exception as e:
            result["control_measurement_failure"] = str(e)

    if control_evidence:
        result["control_evidence_hash"] = control_evidence.evidence_hash
        result["control_evidence_scope"] = control_evidence.evidence_scope
        ctrl_sev = _count_findings_by_severity(control_evidence.findings)
        result["control_error_count"] = ctrl_sev["error"]
        result["control_warning_count"] = ctrl_sev["warning"]
        result["control_info_count"] = ctrl_sev["info"]
        mv_ctrl = control_evidence.provenance.get("metadata_validation")
        result["control_CVR"] = (mv_ctrl["constraint_validity_rate"]
                                 if mv_ctrl else None)
    else:
        result["control_evidence_hash"] = None
        result["control_evidence_scope"] = None
        result["control_error_count"] = None
        result["control_warning_count"] = None
        result["control_info_count"] = None
        result["control_CVR"] = None

    # =====================================================================
    # STAGE 5B: Oracle 2 → final treatment evidence (with metadata)
    # =====================================================================
    treatment_evidence = None
    if treatment_candidate:
        try:
            oracle_treat = oracle.validate(
                treatment_candidate.sdc_text,
                input_identity=treatment_candidate.artifact_id,
                design_metadata=design_metadata,
            )
            result["oracle_calls"] += 1
            if oracle_treat.is_success:
                treatment_evidence = oracle_treat.evidence
        except Exception as e:
            result["treatment_measurement_failure"] = str(e)

    if treatment_evidence:
        result["treatment_evidence_hash"] = treatment_evidence.evidence_hash
        result["treatment_evidence_scope"] = treatment_evidence.evidence_scope
        treat_sev = _count_findings_by_severity(treatment_evidence.findings)
        result["treatment_error_count"] = treat_sev["error"]
        result["treatment_warning_count"] = treat_sev["warning"]
        result["treatment_info_count"] = treat_sev["info"]
        mv_treat = treatment_evidence.provenance.get("metadata_validation")
        result["treatment_CVR"] = (mv_treat["constraint_validity_rate"]
                                   if mv_treat else None)
    else:
        result["treatment_evidence_hash"] = None
        result["treatment_evidence_scope"] = None
        result["treatment_error_count"] = None
        result["treatment_warning_count"] = None
        result["treatment_info_count"] = None
        result["treatment_CVR"] = None

    # =====================================================================
    # PRIMARY METRIC: Error-count delta (P061 §15)
    # =====================================================================
    if (result["control_error_count"] is not None and
            result["initial_error_count"] is not None):
        result["control_delta_error"] = (
            result["control_error_count"] - result["initial_error_count"]
        )
    else:
        result["control_delta_error"] = None

    if (result["treatment_error_count"] is not None and
            result["initial_error_count"] is not None):
        result["treatment_delta_error"] = (
            result["treatment_error_count"] - result["initial_error_count"]
        )
    else:
        result["treatment_delta_error"] = None

    # Treatment effect = treatment_delta - control_delta
    if (result["control_delta_error"] is not None and
            result["treatment_delta_error"] is not None):
        result["treatment_effect"] = (
            result["treatment_delta_error"] - result["control_delta_error"]
        )
    else:
        result["treatment_effect"] = None

    # =====================================================================
    # SECONDARY METRICS: CVR delta, scope transition, warnings
    # =====================================================================
    if (result["control_CVR"] is not None and
            result["initial_CVR"] is not None):
        result["control_delta_CVR"] = result["control_CVR"] - result["initial_CVR"]
    else:
        result["control_delta_CVR"] = None

    if (result["treatment_CVR"] is not None and
            result["initial_CVR"] is not None):
        result["treatment_delta_CVR"] = result["treatment_CVR"] - result["initial_CVR"]
    else:
        result["treatment_delta_CVR"] = None

    if (result["control_warning_count"] is not None and
            result["initial_warning_count"] is not None):
        result["control_delta_warning"] = (
            result["control_warning_count"] - result["initial_warning_count"]
        )
    else:
        result["control_delta_warning"] = None

    if (result["treatment_warning_count"] is not None and
            result["initial_warning_count"] is not None):
        result["treatment_delta_warning"] = (
            result["treatment_warning_count"] - result["initial_warning_count"]
        )
    else:
        result["treatment_delta_warning"] = None

    # =====================================================================
    # STATUS DETERMINATION
    # =====================================================================
    all_complete = (
        control_candidate is not None and
        treatment_candidate is not None and
        control_evidence is not None and
        treatment_evidence is not None
    )
    result["status"] = "COMPLETED" if all_complete else "PARTIAL"
    result["end_timestamp"] = datetime.now(timezone.utc).isoformat()

    # =====================================================================
    # SAVE ARTIFACTS
    # =====================================================================
    _save_rq4_artifacts(result, task_data, initial_candidate,
                        structured_feedback, design_metadata,
                        control_candidate, treatment_candidate,
                        evidence_initial, control_evidence, treatment_evidence,
                        base_dir)

    return result


def _save_rq4_artifacts(
    result: Dict[str, Any],
    task_data: Dict[str, Any],
    initial_candidate: Any,
    structured_feedback: str,
    design_metadata: Optional[DesignMetadata],
    control_candidate: Any,
    treatment_candidate: Any,
    evidence_initial: Any,
    control_evidence: Any,
    treatment_evidence: Any,
    base_dir: Path,
) -> None:
    """Save RQ4 artifacts to the formal/RQ4/ namespace."""
    run_id = result["run_id"]
    rq4_dir = base_dir / "formal" / "RQ4-MODEL-005"

    # ---- CONTROL artifacts ----
    ctrl_raw_dir = rq4_dir / "control" / "raw" / run_id
    ctrl_raw_dir.mkdir(parents=True, exist_ok=True)

    if initial_candidate:
        (ctrl_raw_dir / "initial_candidate.json").write_text(
            json.dumps(initial_candidate.to_dict(), indent=2), encoding="utf-8"
        )
    if evidence_initial:
        (ctrl_raw_dir / "evidence_initial.json").write_text(
            json.dumps({
                "artifact_id": evidence_initial.artifact_id,
                "evidence_scope": evidence_initial.evidence_scope,
                "oracle_status": evidence_initial.oracle_status,
                "findings": evidence_initial.findings,
                "evidence_hash": evidence_initial.evidence_hash,
            }, indent=2), encoding="utf-8"
        )
    if control_candidate:
        (ctrl_raw_dir / "revised_candidate.json").write_text(
            json.dumps(control_candidate.to_dict(), indent=2), encoding="utf-8"
        )
    if control_evidence:
        (ctrl_raw_dir / "evidence_final.json").write_text(
            json.dumps({
                "artifact_id": control_evidence.artifact_id,
                "evidence_scope": control_evidence.evidence_scope,
                "oracle_status": control_evidence.oracle_status,
                "findings": control_evidence.findings,
                "evidence_hash": control_evidence.evidence_hash,
            }, indent=2), encoding="utf-8"
        )

    ctrl_manifest = {
        "run_id": run_id,
        "branch": "CONTROL",
        "task_id": result["task_id"],
        "model_id": result["model_id"],
        "model_name": result["model_name"],
        "initial_candidate_hash": result["initial_candidate_hash"],
        "control_candidate_hash": result["control_candidate_hash"],
        "control_proposal_changed": result["control_proposal_changed"],
        "initial_evidence_hash": result["initial_evidence_hash"],
        "control_evidence_hash": result["control_evidence_hash"],
        "initial_error_count": result["initial_error_count"],
        "control_error_count": result["control_error_count"],
        "control_delta_error": result["control_delta_error"],
        "initial_CVR": result["initial_CVR"],
        "control_CVR": result["control_CVR"],
        "control_delta_CVR": result["control_delta_CVR"],
        "initial_warning_count": result["initial_warning_count"],
        "control_warning_count": result["control_warning_count"],
        "control_delta_warning": result["control_delta_warning"],
        "initial_evidence_scope": result["initial_evidence_scope"],
        "control_evidence_scope": result["control_evidence_scope"],
        "oracle_revision": result["oracle_revision"],
        "metadata_version": result["metadata_version"],
        "feedback_provided": False,
    }
    ctrl_manifest_dir = rq4_dir / "control" / "manifests"
    ctrl_manifest_dir.mkdir(parents=True, exist_ok=True)
    (ctrl_manifest_dir / f"{run_id}.json").write_text(
        json.dumps(ctrl_manifest, indent=2), encoding="utf-8"
    )

    # ---- TREATMENT artifacts ----
    treat_raw_dir = rq4_dir / "treatment" / "raw" / run_id
    treat_raw_dir.mkdir(parents=True, exist_ok=True)

    if initial_candidate:
        (treat_raw_dir / "initial_candidate.json").write_text(
            json.dumps(initial_candidate.to_dict(), indent=2), encoding="utf-8"
        )
    if evidence_initial:
        (treat_raw_dir / "evidence_initial.json").write_text(
            json.dumps({
                "artifact_id": evidence_initial.artifact_id,
                "evidence_scope": evidence_initial.evidence_scope,
                "oracle_status": evidence_initial.oracle_status,
                "findings": evidence_initial.findings,
                "evidence_hash": evidence_initial.evidence_hash,
            }, indent=2), encoding="utf-8"
        )
    if structured_feedback:
        (treat_raw_dir / "structured_feedback.json").write_text(
            structured_feedback, encoding="utf-8"
        )
    if treatment_candidate:
        (treat_raw_dir / "revised_candidate.json").write_text(
            json.dumps(treatment_candidate.to_dict(), indent=2), encoding="utf-8"
        )
    if treatment_evidence:
        (treat_raw_dir / "evidence_final.json").write_text(
            json.dumps({
                "artifact_id": treatment_evidence.artifact_id,
                "evidence_scope": treatment_evidence.evidence_scope,
                "oracle_status": treatment_evidence.oracle_status,
                "findings": treatment_evidence.findings,
                "evidence_hash": treatment_evidence.evidence_hash,
            }, indent=2), encoding="utf-8"
        )

    treat_manifest = {
        "run_id": run_id,
        "branch": "TREATMENT",
        "task_id": result["task_id"],
        "model_id": result["model_id"],
        "model_name": result["model_name"],
        "initial_candidate_hash": result["initial_candidate_hash"],
        "treatment_candidate_hash": result["treatment_candidate_hash"],
        "treatment_proposal_changed": result["treatment_proposal_changed"],
        "initial_evidence_hash": result["initial_evidence_hash"],
        "treatment_evidence_hash": result["treatment_evidence_hash"],
        "structured_feedback_hash": result["structured_feedback_hash"],
        "initial_error_count": result["initial_error_count"],
        "treatment_error_count": result["treatment_error_count"],
        "treatment_delta_error": result["treatment_delta_error"],
        "treatment_effect": result["treatment_effect"],
        "initial_CVR": result["initial_CVR"],
        "treatment_CVR": result["treatment_CVR"],
        "treatment_delta_CVR": result["treatment_delta_CVR"],
        "initial_warning_count": result["initial_warning_count"],
        "treatment_warning_count": result["treatment_warning_count"],
        "treatment_delta_warning": result["treatment_delta_warning"],
        "initial_evidence_scope": result["initial_evidence_scope"],
        "treatment_evidence_scope": result["treatment_evidence_scope"],
        "oracle_revision": result["oracle_revision"],
        "metadata_version": result["metadata_version"],
        "feedback_provided": True,
    }
    treat_manifest_dir = rq4_dir / "treatment" / "manifests"
    treat_manifest_dir.mkdir(parents=True, exist_ok=True)
    (treat_manifest_dir / f"{run_id}.json").write_text(
        json.dumps(treat_manifest, indent=2), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Main entry point (for verification, NOT formal execution)
# ---------------------------------------------------------------------------

def run_rq4(live: bool = False):
    """Run RQ4 pipeline for all tasks.

    Args:
        live: If True, use live opencode (requires OPENCODE_API_KEY).
              If False (default), use deterministic canned mapping.
    """
    base = Path(__file__).parent
    tasks_dir = base.parent / "EGER-BENCH-002" / "tasks" / "engineer_visible"
    oracle = EvidenceOracle()
    manifests = []

    for task_id in TASKS:
        task_file = tasks_dir / f"{task_id}.json"
        task_data = json.loads(task_file.read_text(encoding="utf-8"))
        manifest = run_rq4_task(task_id, task_data, oracle, base, live=live)
        manifests.append(manifest)

    rq4_dir = base / "formal" / "RQ4-MODEL-005"
    rq4_dir.mkdir(parents=True, exist_ok=True)

    # Aggregate metrics
    completed = [m for m in manifests if m["status"] == "COMPLETED"]
    control_better = sum(1 for m in completed
                         if m.get("treatment_effect") is not None
                         and m["treatment_effect"] > 0)
    treatment_better = sum(1 for m in completed
                           if m.get("treatment_effect") is not None
                           and m["treatment_effect"] < 0)
    tie = sum(1 for m in completed
              if m.get("treatment_effect") is not None
              and m["treatment_effect"] == 0)
    missing = sum(1 for m in manifests if m["status"] != "COMPLETED")

    index = {
        "experiment_version": EXPERIMENT_VERSION,
        "model_id": MODEL_ID,
        "model_name": MODEL_NAME,
        "tasks_attempted": len(manifests),
        "tasks_completed": len(completed),
        "tasks_missing": missing,
        "paired_comparison": {
            "control_better": control_better,
            "treatment_better": treatment_better,
            "tie": tie,
        },
        "runs": {
            m["run_id"]: {
                "task_id": m["task_id"],
                "status": m["status"],
                "treatment_effect": m.get("treatment_effect"),
                "control_delta_error": m.get("control_delta_error"),
                "treatment_delta_error": m.get("treatment_delta_error"),
            }
            for m in manifests
        },
    }
    (rq4_dir / "RUN_INDEX.json").write_text(
        json.dumps(index, indent=2), encoding="utf-8"
    )

    print(f"\nRQ4 runs: {len(manifests)} "
          f"(completed: {len(completed)}, missing: {missing})")
    print(f"Paired comparison: treatment_better={treatment_better} "
          f"control_better={control_better} tie={tie}")
    print("RQ4 RUN_INDEX written")
    return manifests


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RQ4 runner")
    parser.add_argument("--live", action="store_true",
                        help="Use live opencode")
    args = parser.parse_args()
    manifests = run_rq4(live=args.live)
