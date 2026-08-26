"""Formal C0 runner — LLM ONLY. No feedback to Engineer. Evaluator-side measurement only."""

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[3]))

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from eger.engineer.model import LiveEngineerModel
from eger.engineer.adapter import EngineerAdapter
from eger.oracle.adapter import EvidenceOracle
from eger.epistemic.state import create_hypothesis
from eger.epistemic.transitions import EpistemicEngine, TransitionRequest

# Config frozen per EGER-MODEL-002 / EGER-EXP-001
EXPERIMENT_VERSION = "EGER-EXP-001 v0.1"
BENCHMARK_VERSION = "EGER-BENCH-002 v0.1"
MODEL_ID = "EGER-MODEL-002"
PROMPT_VERSION = "eger.prompt.v1"
ORACLE_REVISION = "3b5c2f2"
CONDITION = "C0"

TASKS = ["BENCH2-001", "BENCH2-002", "BENCH2-003", "BENCH2-004", "BENCH2-005", "BENCH2-006"]

def run_c0():
    base = Path(__file__).parent
    tasks_dir = base.parent / "EGER-BENCH-002" / "tasks" / "engineer_visible"
    formal_dir = base / "formal"
    (formal_dir / "manifests").mkdir(parents=True, exist_ok=True)
    (formal_dir / "raw").mkdir(parents=True, exist_ok=True)
    manifests = []
    oracle = EvidenceOracle()
    for task_id in TASKS:
        task_file = tasks_dir / f"{task_id}.json"
        task_data = json.loads(task_file.read_text(encoding="utf-8"))
        design_context = f"[{task_id}] {task_data['design_context']}"
        objective = f"[{task_id}] {task_data['objective']}"
        run_id = f"EGER-C0-{uuid.uuid4().hex[:8].upper()}"
        start = datetime.now(timezone.utc).isoformat()
        # Engineer — proposal only, no evidence fed back
        engine_adapter = EngineerAdapter(LiveEngineerModel(timeout=60, max_tokens=2048))
        # Verify capability leakage: no evidence/epistemic/routing/auth
        prop = engine_adapter.propose(design_context=design_context, objective=objective)
        candidate = prop.candidate if prop.is_success else None
        raw_output = prop.model_response.raw_output if prop.model_response else ""
        candidate_hash = candidate.candidate_hash if candidate else None
        raw_output_hash = hashlib.sha256(raw_output.encode("utf-8")).hexdigest() if raw_output else None
        # Evaluator-side oracle measurement (does NOT feed back to Engineer for C0)
        evidence = None
        raw_evidence = None
        evidence_hash = None
        epistemic_state = "HYPOTHESIS"
        epistemic_transitions = []
        failure_class = None
        if prop.failure:
            failure_class = prop.failure.kind  # PROPOSAL_FAILURE
        elif candidate:
            oracle_result = oracle.validate(candidate.sdc_text, input_identity=candidate.artifact_id)
            raw_evidence = oracle_result.raw_evidence
            if oracle_result.is_success:
                evidence = oracle_result.evidence
                evidence_hash = evidence.evidence_hash
                # Evaluator-side epistemic assessment (not shown to Engineer in C0)
                eng = EpistemicEngine()
                claim = create_hypothesis(f"SDC for {task_id} C0", claim_id=f"CLAIM-{run_id}")
                eng.create_claim(claim)
                # Try to transition based on evidence — this is evaluator measurement, not Engineer capability
                if evidence.evidence_scope == "FULL" and not any(f.get("severity") == "error" for f in evidence.findings):
                    # Would be VALIDATED if Engineer had grounding — but C0 has no grounding, so we just record what WOULD happen
                    # For C0, we classify artifact reliability via oracle findings, not via epistemic transition
                    epistemic_state = "HYPOTHESIS"  # C0 has no epistemic state exposed to Engineer
                    # Still record what evaluator would assess
                    if len(evidence.findings) == 0:
                        final_outcome = "VALID_ARTIFACT"
                    else:
                        # Check if any error
                        has_error = any(f.get("severity") == "error" for f in evidence.findings)
                        final_outcome = "INVALID_ARTIFACT" if has_error else "VALID_WITH_WARNINGS"
                else:
                    has_error = any(f.get("severity") == "error" for f in evidence.findings) if evidence.findings else False
                    final_outcome = "INVALID_ARTIFACT" if has_error else "INSUFFICIENT_EVIDENCE"
            else:
                evidence_hash = None
                final_outcome = "ORACLE_FAILURE"
        else:
            final_outcome = "PROPOSAL_FAILURE"

        end = datetime.now(timezone.utc).isoformat()
        manifest = {
            "run_id": run_id,
            "experiment_version": EXPERIMENT_VERSION,
            "benchmark_version": BENCHMARK_VERSION,
            "model_id": MODEL_ID,
            "condition": CONDITION,
            "task_id": task_id,
            "prompt_version": PROMPT_VERSION,
            "oracle_revision": ORACLE_REVISION,
            "schema_versions": {"candidate": "eger.candidate.v1", "evidence": "eger.evidence.v1", "epistemic": "eger.epistemic.v1"},
            "start_timestamp": start,
            "end_timestamp": end,
            "iteration_limit": 5,
            "model_call_limit": 5,
            "oracle_call_limit": 5,
            "model_call_count": 1,
            "candidate_hash": candidate_hash,
            "raw_output_hash": raw_output_hash,
            "evidence_hash": evidence_hash,
            "epistemic_transitions": epistemic_transitions,
            "authorization_decisions": [],
            "final_epistemic_state": epistemic_state,
            "final_authorization": None,
            "final_outcome": final_outcome,
            "failure_class": failure_class or final_outcome,
            "completion_status": "COMPLETED",
            "pilot": False,
            "formal_experiment": True,
        }
        manifests.append(manifest)
        # Raw artifact retention
        raw_dir = formal_dir / "raw" / run_id
        raw_dir.mkdir(parents=True, exist_ok=True)
        if raw_output:
            (raw_dir / "raw_model_output.txt").write_text(raw_output, encoding="utf-8")
        if candidate:
            (raw_dir / "candidate.json").write_text(json.dumps(candidate.to_dict(), indent=2), encoding="utf-8")
        if raw_evidence:
            (raw_dir / "raw_evidence.json").write_bytes(raw_evidence.raw_bytes)
        if evidence:
            ev_dict = {
                "artifact_id": evidence.artifact_id,
                "evidence_scope": evidence.evidence_scope,
                "oracle_status": evidence.oracle_status,
                "findings": evidence.findings,
                "evidence_hash": evidence.evidence_hash,
            }
            (raw_dir / "evidence.json").write_text(json.dumps(ev_dict, indent=2), encoding="utf-8")
        out = formal_dir / "manifests" / f"{run_id}.json"
        out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"{run_id} {task_id} -> {final_outcome} (candidate {candidate_hash[:8] if candidate_hash else 'none'})")
    return manifests

if __name__ == "__main__":
    manifests = run_c0()
    print(f"\nC0 runs: {len(manifests)}")
    # Write index
    base = Path(__file__).parent
    index = {m["run_id"]: {"condition": m["condition"], "task_id": m["task_id"], "manifest": f"formal/manifests/{m['run_id']}.json", "status": m["completion_status"]} for m in manifests}
    (base / "formal" / "RUN_INDEX.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    print("RUN_INDEX written")
