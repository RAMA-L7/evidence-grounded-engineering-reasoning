"""Pilot runner — P012 controlled dry run. PILOT ONLY, not formal experiment."""

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[3]))

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from eger.engineer.model import FakeEngineerModel
from eger.engineer.adapter import EngineerAdapter
from eger.oracle.adapter import EvidenceOracle
from eger.epistemic.state import create_hypothesis
from eger.epistemic.transitions import EpistemicEngine, TransitionRequest
from eger.authorization.gate import AuthorizationGate, AuthorizationRequest

PILOT_TASKS = [
    {"task_id": "BENCH-001", "file": "minimal_sdc.sdc", "reason": "simple valid + INSUFFICIENT scope example"},
    {"task_id": "BENCH-004", "file": "buggy_no_clocks.sdc", "reason": "missing clocks — REFUTED path"},
    {"task_id": "BENCH-007", "file": "edge_case_malformed.sdc", "reason": "malformed — error findings"},
]

CONDITIONS = ["C0", "C2", "C3", "C5"]  # representative subset covering leakage matrix

def _task_context(task):
    # Minimal design context — not ground truth
    return f"Task {task['task_id']} from {task['file']}: generate SDC for the described design."

def run_pilot():
    manifests = []
    base_dir = Path(__file__).parent / "pilot"
    (base_dir / "manifests").mkdir(parents=True, exist_ok=True)
    oracle = EvidenceOracle()
    for task in PILOT_TASKS:
        for cond in CONDITIONS:
            run_id = f"EGER-PILOT-{uuid.uuid4().hex[:8].upper()}"
            start = datetime.now(timezone.utc).isoformat()
            # Engineer — fake deterministic
            adapter = EngineerAdapter(FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]\nset_input_delay -clock clk 1.5 [get_ports data_in]"))
            prop = adapter.propose(design_context=_task_context(task), objective=f"Pilot {cond} for {task['task_id']}")
            candidate = prop.candidate if prop.is_success else None

            # L1 — evidence (always runs for measurement, but Engineer only sees it in C2+)
            evidence = None
            raw_evidence = None
            oracle_result = None
            if candidate:
                oracle_result = oracle.validate(candidate.sdc_text, input_identity=candidate.artifact_id)
                if oracle_result.is_success:
                    evidence = oracle_result.evidence
                    raw_evidence = oracle_result.raw_evidence
                else:
                    # Oracle failure case — keep raw for manifest
                    raw_evidence = oracle_result.raw_evidence

            # L2 — epistemic (engineer may see read-only state in C3+)
            eng = EpistemicEngine()
            claim = create_hypothesis(f"SDC for {task['task_id']} in {cond}", claim_id=f"CLAIM-{run_id}")
            eng.create_claim(claim)
            epistemic_state = claim.state
            violation = None
            transition = None
            if cond in ("C2", "C3", "C5") and evidence:
                # Attempt VALIDATED — will succeed only if evidence supports it
                req = TransitionRequest(claim_id=claim.claim_id, target_state="VALIDATED", evidence=evidence, evidence_ids=[evidence.artifact_id] if hasattr(evidence, 'artifact_id') else [], reason=f"pilot {cond}")
                res = eng.request_transition(req)
                if res.accepted:
                    transition = res.transition
                    epistemic_state = claim.state
                else:
                    violation = res.violation
                    # Try UNKNOWN for insufficient cases
                    if evidence.evidence_scope in ("INSUFFICIENT", "UNSUPPORTED"):
                        req2 = TransitionRequest(claim_id=claim.claim_id, target_state="UNKNOWN", evidence=evidence, evidence_ids=[evidence.artifact_id], reason="insufficient -> unknown")
                        res2 = eng.request_transition(req2)
                        if res2.accepted:
                            epistemic_state = claim.state

            # L3 — authorization (only C5)
            auth_decision = None
            gate = AuthorizationGate()
            if cond == "C5":
                req_auth = AuthorizationRequest(
                    request_id=f"REQ-{run_id}",
                    claim_id=claim.claim_id,
                    proposed_action="commit",
                    epistemic_state=epistemic_state,
                    evidence_ids=[evidence.artifact_id] if evidence and hasattr(evidence, 'artifact_id') else [],
                    evidence_scope=evidence.evidence_scope if evidence else None,
                    oracle_status=evidence.oracle_status if evidence else None,
                )
                auth_decision = gate.authorize(req_auth)

            end = datetime.now(timezone.utc).isoformat()

            # Manifest — pilot=true
            manifest = {
                "run_id": run_id,
                "pilot": True,
                "formal_experiment": False,
                "experiment_version": "EGER-EXP-001 v0.1",
                "condition": cond,
                "task_id": task["task_id"],
                "benchmark_version": "EGER-BENCH-001 v0.1",
                "model": {"provider": "fake", "model": "fake-engineer-v1", "version": "1.0", "prompt_version": "eger.prompt.v1"},
                "oracle_revision": "3b5c2f2",
                "schema_versions": {"candidate": "eger.candidate.v1", "evidence": "eger.evidence.v1", "epistemic": "eger.epistemic.v1"},
                "start": start,
                "end": end,
                "iteration_limit": 5,
                "tool_call_limit": 5,
                "candidate_hash": candidate.candidate_hash if candidate else None,
                "evidence_hash": evidence.evidence_hash if evidence else None,
                "epistemic_transitions": [t.transition_id for t in eng.get_transitions()],
                "authorization_decisions": [auth_decision.decision_id] if auth_decision else [],
                "final_epistemic_state": epistemic_state,
                "final_authorization": auth_decision.decision if auth_decision else None,
                "failure_class": violation.violation_type if violation else ("AUTHORIZATION_REJECTION" if auth_decision and auth_decision.decision == "REJECTED" else None),
                "violation": {"type": violation.violation_type, "reason": violation.reason} if violation else None,
            }
            manifests.append(manifest)
            out = base_dir / "manifests" / f"{run_id}.json"
            out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifests

if __name__ == "__main__":
    manifests = run_pilot()
    print(f"Pilot runs: {len(manifests)}")
    for m in manifests:
        print(m["run_id"], m["condition"], m["task_id"], m["final_epistemic_state"], m["final_authorization"])
