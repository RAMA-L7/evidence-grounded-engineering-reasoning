"""Formal C1 runner — Feedback-Assisted Revision. Two-stage pipeline.

C1 Pipeline:
  LLM (call 1) → INITIAL CANDIDATE
  ORACLE (call 1) → EvidenceArtifact
  TEXT FEEDBACK → deterministic rendering
  LLM (call 2) → REVISED CANDIDATE
  ORACLE (call 2) → MEASUREMENT

This runner does NOT execute BENCH-002 experiments. It is an implementation
artifact that must be verified via tests before formal execution.

C0 artifacts are NOT modified. C1 artifacts write to formal/C1/.
"""

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[3]))

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

from eger.engineer.model import LiveEngineerModel
from eger.engineer.adapter import EngineerAdapter
from eger.engineer.feedback import render_text_feedback
from eger.oracle.adapter import EvidenceOracle

# ---------------------------------------------------------------------------
# Frozen configuration per MODEL-002 / EXP-001 v0.2
# ---------------------------------------------------------------------------
EXPERIMENT_VERSION = "EGER-EXP-001 v0.2"
BENCHMARK_VERSION = "EGER-BENCH-002 v0.1"
MODEL_ID = "EGER-MODEL-002"
PROMPT_VERSION = "eger.prompt.v1"
ORACLE_REVISION = "3b5c2f2"
CONDITION = "C1"

TASKS = ["BENCH2-001", "BENCH2-002", "BENCH2-003", "BENCH2-004", "BENCH2-005", "BENCH2-006"]

# Budget enforcement (EXP-001 v0.2 §13)
MAX_MODEL_CALLS = 2
MAX_ORACLE_CALLS = 2


# ---------------------------------------------------------------------------
# C1 two-stage pipeline
# ---------------------------------------------------------------------------

def run_c1_task(
    task_id: str,
    task_data: Dict[str, Any],
    oracle: EvidenceOracle,
    base_dir: Path,
) -> Dict[str, Any]:
    """Execute the C1 pipeline for a single task.

    Returns a manifest dict. Does NOT execute BENCH-002 formally.
    This is an implementation artifact for verification.
    """
    run_id = f"EGER-C1-{uuid.uuid4().hex[:8].upper()}"
    start = datetime.now(timezone.utc).isoformat()

    design_context = f"[{task_id}] {task_data['design_context']}"
    objective = f"[{task_id}] {task_data['objective']}"

    # Budget counters
    model_calls = 0
    oracle_calls = 0

    # Artifact storage
    initial_candidate = None
    initial_candidate_hash = None
    raw_output_1 = None
    raw_output_hash_1 = None
    evidence_1 = None
    evidence_hash_1 = None
    raw_evidence_1 = None
    text_feedback = None
    text_feedback_hash = None
    revised_candidate = None
    final_candidate_hash = None
    raw_output_2 = None
    raw_output_hash_2 = None
    evidence_2 = None
    evidence_hash_2 = None
    raw_evidence_2 = None

    final_outcome = None
    failure_class = None

    # ------------------------------------------------------------------
    # STAGE 1: Model call 1 → initial candidate
    # ------------------------------------------------------------------
    engine_adapter = EngineerAdapter(LiveEngineerModel(timeout=60, max_tokens=2048))

    try:
        prop1 = engine_adapter.propose(
            design_context=design_context,
            objective=objective,
        )
        model_calls += 1
    except Exception as e:
        final_outcome = "PROPOSAL_FAILURE"
        failure_class = "MODEL_FAILURE"
        return _build_manifest(
            run_id=run_id, start=start, task_id=task_id,
            final_outcome=final_outcome, failure_class=failure_class,
            model_calls=model_calls, oracle_calls=oracle_calls,
        )

    if not prop1.is_success:
        final_outcome = "PROPOSAL_FAILURE"
        failure_class = prop1.failure.kind if prop1.failure else "MODEL_FAILURE"
        return _build_manifest(
            run_id=run_id, start=start, task_id=task_id,
            final_outcome=final_outcome, failure_class=failure_class,
            model_calls=model_calls, oracle_calls=oracle_calls,
        )

    initial_candidate = prop1.candidate
    raw_output_1 = prop1.model_response.raw_output if prop1.model_response else ""
    raw_output_hash_1 = hashlib.sha256(raw_output_1.encode("utf-8")).hexdigest() if raw_output_1 else None
    initial_candidate_hash = initial_candidate.candidate_hash if initial_candidate else None

    # ------------------------------------------------------------------
    # STAGE 2: Oracle call 1 → evaluate initial candidate
    # ------------------------------------------------------------------
    try:
        oracle_result_1 = oracle.validate(
            initial_candidate.sdc_text,
            input_identity=initial_candidate.artifact_id,
        )
        oracle_calls += 1
    except Exception as e:
        final_outcome = "INCOMPLETE_TREATMENT"
        failure_class = "ORACLE_FAILURE"
        return _build_manifest(
            run_id=run_id, start=start, task_id=task_id,
            final_outcome=final_outcome, failure_class=failure_class,
            model_calls=model_calls, oracle_calls=oracle_calls,
            initial_candidate_hash=initial_candidate_hash,
        )

    if not oracle_result_1.is_success:
        # ODQ-1: Oracle call 1 failure → INCOMPLETE_TREATMENT
        final_outcome = "INCOMPLETE_TREATMENT"
        failure_class = "ORACLE_FAILURE"
        raw_evidence_1 = oracle_result_1.raw_evidence
        return _build_manifest(
            run_id=run_id, start=start, task_id=task_id,
            final_outcome=final_outcome, failure_class=failure_class,
            model_calls=model_calls, oracle_calls=oracle_calls,
            initial_candidate_hash=initial_candidate_hash,
            raw_evidence_1=raw_evidence_1,
        )

    evidence_1 = oracle_result_1.evidence
    raw_evidence_1 = oracle_result_1.raw_evidence
    evidence_hash_1 = evidence_1.evidence_hash if evidence_1 else None

    # ------------------------------------------------------------------
    # STAGE 3: Render deterministic text feedback
    # ------------------------------------------------------------------
    text_feedback = render_text_feedback(evidence_1)
    text_feedback_hash = hashlib.sha256(text_feedback.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # STAGE 4: Model call 2 → revised candidate
    # ------------------------------------------------------------------
    try:
        prop2 = engine_adapter.propose(
            design_context=design_context,
            existing_sdc=initial_candidate.sdc_text,
            objective=objective,
            evidence_summary=text_feedback,
        )
        model_calls += 1
    except Exception as e:
        # ODQ-2: Model call 2 failure → INCOMPLETE_TREATMENT
        final_outcome = "INCOMPLETE_TREATMENT"
        failure_class = "MODEL_FAILURE"
        return _build_manifest(
            run_id=run_id, start=start, task_id=task_id,
            final_outcome=final_outcome, failure_class=failure_class,
            model_calls=model_calls, oracle_calls=oracle_calls,
            initial_candidate_hash=initial_candidate_hash,
            evidence_hash_1=evidence_hash_1,
            text_feedback_hash=text_feedback_hash,
        )

    if not prop2.is_success:
        # ODQ-2: Model call 2 failure → INCOMPLETE_TREATMENT
        final_outcome = "INCOMPLETE_TREATMENT"
        failure_class = prop2.failure.kind if prop2.failure else "MODEL_FAILURE"
        raw_output_2 = prop2.model_response.raw_output if prop2.model_response else ""
        raw_output_hash_2 = hashlib.sha256(raw_output_2.encode("utf-8")).hexdigest() if raw_output_2 else None
        return _build_manifest(
            run_id=run_id, start=start, task_id=task_id,
            final_outcome=final_outcome, failure_class=failure_class,
            model_calls=model_calls, oracle_calls=oracle_calls,
            initial_candidate_hash=initial_candidate_hash,
            evidence_hash_1=evidence_hash_1,
            text_feedback_hash=text_feedback_hash,
            raw_output_hash_2=raw_output_hash_2,
        )

    revised_candidate = prop2.candidate
    raw_output_2 = prop2.model_response.raw_output if prop2.model_response else ""
    raw_output_hash_2 = hashlib.sha256(raw_output_2.encode("utf-8")).hexdigest() if raw_output_2 else None
    final_candidate_hash = revised_candidate.candidate_hash if revised_candidate else None

    # ------------------------------------------------------------------
    # STAGE 5: Oracle call 2 → measure revised candidate
    # ------------------------------------------------------------------
    try:
        oracle_result_2 = oracle.validate(
            revised_candidate.sdc_text,
            input_identity=revised_candidate.artifact_id,
        )
        oracle_calls += 1
    except Exception as e:
        # ODQ-3: Oracle call 2 failure → INCOMPLETE_MEASUREMENT
        final_outcome = "INCOMPLETE_MEASUREMENT"
        failure_class = "ORACLE_FAILURE"
        return _build_manifest(
            run_id=run_id, start=start, task_id=task_id,
            final_outcome=final_outcome, failure_class=failure_class,
            model_calls=model_calls, oracle_calls=oracle_calls,
            initial_candidate_hash=initial_candidate_hash,
            evidence_hash_1=evidence_hash_1,
            text_feedback_hash=text_feedback_hash,
            final_candidate_hash=final_candidate_hash,
        )

    if not oracle_result_2.is_success:
        # ODQ-3: Oracle call 2 failure → INCOMPLETE_MEASUREMENT
        final_outcome = "INCOMPLETE_MEASUREMENT"
        failure_class = "ORACLE_FAILURE"
        raw_evidence_2 = oracle_result_2.raw_evidence
        return _build_manifest(
            run_id=run_id, start=start, task_id=task_id,
            final_outcome=final_outcome, failure_class=failure_class,
            model_calls=model_calls, oracle_calls=oracle_calls,
            initial_candidate_hash=initial_candidate_hash,
            evidence_hash_1=evidence_hash_1,
            text_feedback_hash=text_feedback_hash,
            final_candidate_hash=final_candidate_hash,
            raw_evidence_2=raw_evidence_2,
        )

    evidence_2 = oracle_result_2.evidence
    raw_evidence_2 = oracle_result_2.raw_evidence
    evidence_hash_2 = evidence_2.evidence_hash if evidence_2 else None

    # ------------------------------------------------------------------
    # Determine final outcome
    # ------------------------------------------------------------------
    if evidence_2.evidence_scope == "FULL" and not any(
        f.get("severity") == "error" for f in (evidence_2.findings or [])
    ):
        if len(evidence_2.findings or []) == 0:
            final_outcome = "VALID_ARTIFACT"
        else:
            final_outcome = "VALID_WITH_WARNINGS"
    else:
        has_error = any(f.get("severity") == "error" for f in (evidence_2.findings or []))
        if has_error:
            final_outcome = "INVALID_ARTIFACT"
        else:
            final_outcome = "INSUFFICIENT_EVIDENCE"

    failure_class = final_outcome

    # ------------------------------------------------------------------
    # Save raw artifacts
    # ------------------------------------------------------------------
    raw_dir = base_dir / "formal" / "C1" / "raw" / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)

    if raw_output_1:
        (raw_dir / "raw_model_output_call1.txt").write_text(raw_output_1, encoding="utf-8")
    if initial_candidate:
        (raw_dir / "initial_candidate.json").write_text(
            json.dumps(initial_candidate.to_dict(), indent=2), encoding="utf-8"
        )
    if raw_evidence_1:
        (raw_dir / "raw_evidence_initial.json").write_bytes(raw_evidence_1.raw_bytes)
    if evidence_1:
        (raw_dir / "evidence_initial.json").write_text(
            json.dumps({
                "artifact_id": evidence_1.artifact_id,
                "evidence_scope": evidence_1.evidence_scope,
                "oracle_status": evidence_1.oracle_status,
                "findings": evidence_1.findings,
                "evidence_hash": evidence_1.evidence_hash,
            }, indent=2), encoding="utf-8"
        )
    if text_feedback:
        (raw_dir / "text_feedback.txt").write_text(text_feedback, encoding="utf-8")
    if raw_output_2:
        (raw_dir / "raw_model_output_call2.txt").write_text(raw_output_2, encoding="utf-8")
    if revised_candidate:
        (raw_dir / "revised_candidate.json").write_text(
            json.dumps(revised_candidate.to_dict(), indent=2), encoding="utf-8"
        )
    if raw_evidence_2:
        (raw_dir / "raw_evidence_final.json").write_bytes(raw_evidence_2.raw_bytes)
    if evidence_2:
        (raw_dir / "evidence_final.json").write_text(
            json.dumps({
                "artifact_id": evidence_2.artifact_id,
                "evidence_scope": evidence_2.evidence_scope,
                "oracle_status": evidence_2.oracle_status,
                "findings": evidence_2.findings,
                "evidence_hash": evidence_2.evidence_hash,
            }, indent=2), encoding="utf-8"
        )

    end = datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # Build manifest
    # ------------------------------------------------------------------
    manifest = _build_manifest(
        run_id=run_id, start=start, end=end, task_id=task_id,
        final_outcome=final_outcome, failure_class=failure_class,
        model_calls=model_calls, oracle_calls=oracle_calls,
        initial_candidate_hash=initial_candidate_hash,
        evidence_hash_1=evidence_hash_1,
        text_feedback_hash=text_feedback_hash,
        final_candidate_hash=final_candidate_hash,
        evidence_hash_2=evidence_hash_2,
        raw_output_hash_1=raw_output_hash_1,
        raw_output_hash_2=raw_output_hash_2,
    )

    # Write manifest
    manifest_dir = base_dir / "formal" / "C1" / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    (manifest_dir / f"{run_id}.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    print(f"{run_id} {task_id} -> {final_outcome} "
          f"(initial {initial_candidate_hash[:8] if initial_candidate_hash else 'none'}, "
          f"revised {final_candidate_hash[:8] if final_candidate_hash else 'none'})")

    return manifest


def _build_manifest(
    run_id: str,
    start: str = "",
    end: str = "",
    task_id: str = "",
    final_outcome: str = "",
    failure_class: str = "",
    model_calls: int = 0,
    oracle_calls: int = 0,
    initial_candidate_hash: Optional[str] = None,
    evidence_hash_1: Optional[str] = None,
    text_feedback_hash: Optional[str] = None,
    final_candidate_hash: Optional[str] = None,
    evidence_hash_2: Optional[str] = None,
    raw_output_hash_1: Optional[str] = None,
    raw_output_hash_2: Optional[str] = None,
    raw_evidence_1: Any = None,
    raw_evidence_2: Any = None,
) -> Dict[str, Any]:
    """Build a C1 run manifest."""
    return {
        "run_id": run_id,
        "experiment_version": EXPERIMENT_VERSION,
        "benchmark_version": BENCHMARK_VERSION,
        "model_id": MODEL_ID,
        "condition": CONDITION,
        "task_id": task_id,
        "prompt_version": PROMPT_VERSION,
        "oracle_revision": ORACLE_REVISION,
        "schema_versions": {
            "candidate": "eger.candidate.v1",
            "evidence": "eger.evidence.v1",
        },
        "start_timestamp": start,
        "end_timestamp": end,
        "iteration_limit": 5,
        "model_call_limit": MAX_MODEL_CALLS,
        "oracle_call_limit": MAX_ORACLE_CALLS,
        "model_calls": model_calls,
        "oracle_calls": oracle_calls,
        # C1-specific fields
        "initial_candidate_hash": initial_candidate_hash,
        "initial_oracle_evidence_hash": evidence_hash_1,
        "text_feedback_hash": text_feedback_hash,
        "final_candidate_hash": final_candidate_hash,
        "final_oracle_evidence_hash": evidence_hash_2,
        "raw_output_hash_call1": raw_output_hash_1,
        "raw_output_hash_call2": raw_output_hash_2,
        # Outcomes
        "final_outcome": final_outcome,
        "failure_class": failure_class,
        "completion_status": "COMPLETED" if final_outcome not in ("INCOMPLETE_TREATMENT", "INCOMPLETE_MEASUREMENT") else "INCOMPLETE",
        "pilot": False,
        "formal_experiment": True,
    }


# ---------------------------------------------------------------------------
# Main entry point (for verification, NOT formal execution)
# ---------------------------------------------------------------------------

def run_c1():
    """Run C1 pipeline for all tasks. For implementation verification only."""
    base = Path(__file__).parent
    tasks_dir = base.parent / "EGER-BENCH-002" / "tasks" / "engineer_visible"
    oracle = EvidenceOracle()
    manifests = []

    for task_id in TASKS:
        task_file = tasks_dir / f"{task_id}.json"
        task_data = json.loads(task_file.read_text(encoding="utf-8"))
        manifest = run_c1_task(task_id, task_data, oracle, base)
        manifests.append(manifest)

    # Write C1 RUN_INDEX
    c1_dir = base / "formal" / "C1"
    c1_dir.mkdir(parents=True, exist_ok=True)
    index = {
        m["run_id"]: {
            "condition": m["condition"],
            "task_id": m["task_id"],
            "manifest": f"formal/C1/manifests/{m['run_id']}.json",
            "status": m["completion_status"],
        }
        for m in manifests
    }
    (c1_dir / "RUN_INDEX.json").write_text(json.dumps(index, indent=2), encoding="utf-8")

    print(f"\nC1 runs: {len(manifests)}")
    print("C1 RUN_INDEX written")
    return manifests


if __name__ == "__main__":
    manifests = run_c1()
