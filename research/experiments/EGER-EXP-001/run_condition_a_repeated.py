"""Run Condition A 3 times for H4 repeatability test (P084).

Identical to DIAGNOSTIC-001 Condition A, repeated 3 times independently.
"""

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[3]))

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from eger.engineer.model import LiveEngineerModel
from eger.engineer.adapter import EngineerAdapter
from eger.oracle.adapter import EvidenceOracle
from eger.oracle.schemas import DesignMetadata

MODEL_NAME = "opencode/mimo-v2.5-free"
TASK_ID = "BENCH2-001"
ORACLE_REVISION = "3b5c2f2"
METADATA_VERSION = "eger.design_metadata.v1"

METADATA_DIR = (Path(__file__).resolve().parent.parent /
                "EGER-BENCH-002" / "evaluator_context")

DESIGN_CONTEXT = (
    "Module top with ports clk, reset, data_in[7:0], data_out[7:0]. "
    "Single clock domain clk at 10ns. No generated clocks."
)
OBJECTIVE = "Generate SDC that correctly defines the primary clock on clk."
INITIAL_SDC = "create_clock -name clk -period 10.0 [get_ports clk]"


def _load_design_metadata(task_id):
    path = METADATA_DIR / f"{task_id}.design_metadata.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return DesignMetadata.from_dict(json.load(f))


def run_single(run_number, oracle, design_metadata, engine_adapter, base_dir):
    """Run Condition A once."""
    from eger.engineer.structured_feedback import render_structured_feedback

    start = datetime.now(timezone.utc).isoformat()
    run_id = f"A-RUN{run_number}-{datetime.now(timezone.utc).strftime('%H%M%S')}"
    result = {
        "run_id": run_id,
        "run_number": run_number,
        "task_id": TASK_ID,
        "start_timestamp": start,
        "status": "IN_PROGRESS",
    }

    # Oracle initial evaluation
    oracle_init = oracle.validate(
        INITIAL_SDC,
        input_identity=f"P084-R{run_number}-INIT",
        design_metadata=design_metadata,
    )
    if not oracle_init.is_success:
        result["status"] = "INCOMPLETE_MEASUREMENT"
        return result

    evidence_initial = oracle_init.evidence
    result["initial_evidence_scope"] = evidence_initial.evidence_scope
    initial_errors = sum(1 for f in (evidence_initial.findings or [])
                         if f.get("severity") == "error")
    result["initial_error_count"] = initial_errors
    result["initial_findings_count"] = len(evidence_initial.findings or [])

    # Build structured feedback
    structured_feedback = render_structured_feedback(evidence_initial)
    result["feedback_hash"] = hashlib.sha256(
        structured_feedback.encode("utf-8")
    ).hexdigest()

    # Model call
    try:
        prop = engine_adapter.propose(
            design_context=f"[{TASK_ID}] {DESIGN_CONTEXT}",
            existing_sdc=INITIAL_SDC,
            objective=f"[{TASK_ID}] {OBJECTIVE}",
            evidence_summary=structured_feedback,
        )
    except Exception as e:
        result["status"] = "INCOMPLETE"
        result["failure"] = str(e)
        return result

    if not prop.is_success:
        result["status"] = "INCOMPLETE"
        result["failure"] = prop.failure.message if prop.failure else "unknown"
        return result

    revised = prop.candidate
    result["proposal_changed"] = (
        revised.candidate_hash != hashlib.sha256(
            INITIAL_SDC.encode("utf-8")
        ).hexdigest()
    )
    result["revised_sdc_length"] = len(revised.sdc_text)

    # Check ERROR adherence
    lower = revised.sdc_text.lower()
    result["has_set_input_delay"] = "set_input_delay" in lower
    result["has_set_output_delay"] = "set_output_delay" in lower
    result["error_adherence"] = (
        result["has_set_input_delay"] and result["has_set_output_delay"]
    )

    # Oracle final evaluation
    oracle_final = oracle.validate(
        revised.sdc_text,
        input_identity=f"P084-R{run_number}-FINAL",
        design_metadata=design_metadata,
    )
    if not oracle_final.is_success:
        result["final_evidence_scope"] = None
        result["final_error_count"] = None
        result["error_delta"] = None
    else:
        ev_final = oracle_final.evidence
        result["final_evidence_scope"] = ev_final.evidence_scope
        final_errors = sum(1 for f in (ev_final.findings or [])
                          if f.get("severity") == "error")
        result["final_error_count"] = final_errors
        result["error_delta"] = final_errors - initial_errors
        result["final_findings_count"] = len(ev_final.findings or [])

    result["status"] = "COMPLETED"
    result["end_timestamp"] = datetime.now(timezone.utc).isoformat()

    # Save artifacts
    run_dir = base_dir / "raw" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "initial_sdc.txt").write_text(INITIAL_SDC, encoding="utf-8")
    (run_dir / "revised_candidate.json").write_text(
        json.dumps(revised.to_dict(), indent=2), encoding="utf-8"
    )
    (run_dir / "feedback.json").write_text(structured_feedback, encoding="utf-8")
    (run_dir / "evidence_initial.json").write_text(
        json.dumps({"scope": evidence_initial.evidence_scope,
                     "findings": evidence_initial.findings}, indent=2),
        encoding="utf-8"
    )
    if oracle_final.is_success:
        (run_dir / "evidence_final.json").write_text(
            json.dumps({"scope": oracle_final.evidence.evidence_scope,
                         "findings": oracle_final.evidence.findings}, indent=2),
            encoding="utf-8"
        )

    # Save manifest
    manifest = {k: v for k, v in result.items() if k != "initial_findings"}
    (base_dir / f"manifest-{run_id}.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    return result


def main():
    base = Path(__file__).parent
    diag2_dir = base / "formal" / "DIAGNOSTIC-002"
    diag2_dir.mkdir(parents=True, exist_ok=True)

    oracle = EvidenceOracle()
    design_metadata = _load_design_metadata(TASK_ID)
    engine_adapter = EngineerAdapter(
        LiveEngineerModel(timeout=60, max_tokens=2048, live=True,
                          model=MODEL_NAME)
    )

    results = []
    for i in range(1, 4):
        print(f"\n--- Run {i} ---")
        r = run_single(i, oracle, design_metadata, engine_adapter, diag2_dir)
        results.append(r)
        print(f"  status: {r['status']}")
        print(f"  error_adherence: {r.get('error_adherence', '?')}")
        print(f"  error_delta: {r.get('error_delta', '?')}")
        print(f"  proposal_changed: {r.get('proposal_changed', '?')}")

    # Summary
    adherent = sum(1 for r in results if r.get("error_adherence"))
    print(f"\n=== Summary: {adherent}/3 runs achieved ERROR adherence ===")

    # Save index
    index = {
        "experiment": "P084-REPEATED-A",
        "task_id": TASK_ID,
        "runs": len(results),
        "adherent": adherent,
        "results": [{
            "run_id": r["run_id"],
            "status": r["status"],
            "error_adherence": r.get("error_adherence"),
            "error_delta": r.get("error_delta"),
            "proposal_changed": r.get("proposal_changed"),
        } for r in results],
    }
    (diag2_dir / "RUN_INDEX.json").write_text(
        json.dumps(index, indent=2), encoding="utf-8"
    )
    print(f"RUN_INDEX written to {diag2_dir / 'RUN_INDEX.json'}")
    return results


if __name__ == "__main__":
    main()
