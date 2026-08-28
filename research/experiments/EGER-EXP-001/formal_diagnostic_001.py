"""Diagnostic runner — P078 Hypothesis Isolation (EGER-CHANGE-009).

Tests why BENCH2-001 ignored ERROR feedback in RQ-4.

Conditions:
  A — Baseline: original task + original SDC + full feedback
  B — Richer SDC: same task/feedback, richer initial SDC
  C — Broader objective: same SDC/feedback, broader objective
  D — ERROR-only feedback: same task/SDC/objective, reduced feedback

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
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

from eger.engineer.model import LiveEngineerModel
from eger.engineer.adapter import EngineerAdapter
from eger.oracle.adapter import EvidenceOracle
from eger.oracle.schemas import DesignMetadata

# ---------------------------------------------------------------------------
# Frozen configuration
# ---------------------------------------------------------------------------
MODEL_ID = "EGER-MODEL-005"
MODEL_NAME = "opencode/mimo-v2.5-free"
ORACLE_REVISION = "3b5c2f2"
METADATA_VERSION = "eger.design_metadata.v1"
TASK_ID = "BENCH2-001"

METADATA_DIR = (Path(__file__).resolve().parent.parent /
                "EGER-BENCH-002" / "evaluator_context")

# ---------------------------------------------------------------------------
# BENCH2-001 task data (frozen)
# ---------------------------------------------------------------------------
DESIGN_CONTEXT = (
    "Module top with ports clk, reset, data_in[7:0], data_out[7:0]. "
    "Single clock domain clk at 10ns. No generated clocks."
)

ORIGINAL_OBJECTIVE = "Generate SDC that correctly defines the primary clock on clk."

BROADER_OBJECTIVE = (
    "Generate a complete, production-quality SDC for this design. "
    "Include all required timing constraints: clock definitions, "
    "I/O delays, and any applicable exceptions."
)

# Original minimal SDC (BENCH2-001 initial candidate)
ORIGINAL_SDC = "create_clock -name clk -period 10.0 [get_ports clk]"

# Richer SDC from BENCH2-002 initial candidate (for condition B)
RICH_SDC = """\
create_clock -name clk -period 10.0 [get_ports clk]

create_generated_clock -name clk_div2 \\
    -source [get_ports clk] \\
    -divide_by 2 \\
    -master_clock clk \\
    [get_pins div_reg/Q]

set_clock_groups -asynchronous \\
    -group [get_clocks clk] \\
    -group [get_clocks clk_div2]"""

# ERROR-only feedback (for condition D)
ERROR_ONLY_FEEDBACK = json.dumps([
    {
        "severity": "error",
        "code": "SDC-005",
        "message": "No set_input_delay — all input ports are unconstrained.",
        "line": None,
    },
    {
        "severity": "error",
        "code": "SDC-006",
        "message": "No set_output_delay — all output ports are unconstrained.",
        "line": None,
    },
], sort_keys=True, separators=(",", ":"), ensure_ascii=False)

# ---------------------------------------------------------------------------
# Condition definitions
# ---------------------------------------------------------------------------
CONDITIONS = {
    "A": {
        "name": "A-baseline",
        "description": "Original BENCH2-001: minimal SDC, original objective, full feedback",
        "sdc": ORIGINAL_SDC,
        "objective": ORIGINAL_OBJECTIVE,
        "feedback_mode": "full",
    },
    "B": {
        "name": "B-richer-sdc",
        "description": "Same task/feedback, richer initial SDC",
        "sdc": RICH_SDC,
        "objective": ORIGINAL_OBJECTIVE,
        "feedback_mode": "full",
    },
    "C": {
        "name": "C-broader-objective",
        "description": "Same SDC/feedback, broader task objective",
        "sdc": ORIGINAL_SDC,
        "objective": BROADER_OBJECTIVE,
        "feedback_mode": "full",
    },
    "D": {
        "name": "D-error-only-feedback",
        "description": "Same task/SDC/objective, ERROR-only feedback",
        "sdc": ORIGINAL_SDC,
        "objective": ORIGINAL_OBJECTIVE,
        "feedback_mode": "error_only",
    },
}


def _load_design_metadata(task_id: str) -> Optional[DesignMetadata]:
    """Load frozen evaluator-side design metadata."""
    path = METADATA_DIR / f"{task_id}.design_metadata.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return DesignMetadata.from_dict(json.load(f))


def _build_full_feedback(evidence: Any) -> str:
    """Build full structured feedback from evidence (same as RQ-4 runner)."""
    from eger.engineer.structured_feedback import render_structured_feedback
    return render_structured_feedback(evidence)


def _check_error_adherence(sdc_text: str) -> Dict[str, bool]:
    """Check whether the SDC addresses ERROR findings (SDC-005, SDC-006)."""
    lower = sdc_text.lower()
    has_input_delay = "set_input_delay" in lower
    has_output_delay = "set_output_delay" in lower
    return {
        "has_set_input_delay": has_input_delay,
        "has_set_output_delay": has_output_delay,
        "error_adherence": has_input_delay and has_output_delay,
    }


def run_diagnostic_condition(
    condition_key: str,
    condition: Dict[str, Any],
    oracle: EvidenceOracle,
    design_metadata: Optional[DesignMetadata],
    engine_adapter: EngineerAdapter,
    base_dir: Path,
    full_feedback_text: str,
) -> Dict[str, Any]:
    """Execute a single diagnostic condition.

    Returns a manifest dict with results.
    """
    start = datetime.now(timezone.utc).isoformat()
    result = {
        "condition": condition_key,
        "condition_name": condition["name"],
        "description": condition["description"],
        "task_id": TASK_ID,
        "model_id": MODEL_ID,
        "model_name": MODEL_NAME,
        "oracle_revision": ORACLE_REVISION,
        "metadata_version": METADATA_VERSION,
        "start_timestamp": start,
        "status": "IN_PROGRESS",
        "model_calls": 0,
        "oracle_calls": 0,
    }

    # Select feedback
    if condition["feedback_mode"] == "error_only":
        feedback_text = ERROR_ONLY_FEEDBACK
    else:
        feedback_text = full_feedback_text

    result["feedback_mode"] = condition["feedback_mode"]
    result["feedback_hash"] = hashlib.sha256(
        feedback_text.encode("utf-8")
    ).hexdigest()

    # Initial SDC
    initial_sdc = condition["sdc"]
    result["initial_sdc_hash"] = hashlib.sha256(
        initial_sdc.encode("utf-8")
    ).hexdigest()
    result["initial_sdc_length"] = len(initial_sdc)

    # Oracle evaluation of initial SDC
    try:
        oracle_init = oracle.validate(
            initial_sdc,
            input_identity=f"DIAG-{condition_key}-INIT",
            design_metadata=design_metadata,
        )
        result["oracle_calls"] += 1
        if oracle_init.is_success:
            ev = oracle_init.evidence
            result["initial_evidence_hash"] = ev.evidence_hash
            result["initial_evidence_scope"] = ev.evidence_scope
            err_count = sum(1 for f in (ev.findings or [])
                           if f.get("severity") == "error")
            result["initial_error_count"] = err_count
            result["initial_findings"] = ev.findings
        else:
            result["status"] = "INCOMPLETE_MEASUREMENT"
            return result
    except Exception as e:
        result["status"] = "INCOMPLETE_MEASUREMENT"
        result["failure_message"] = str(e)
        return result

    # Model Call — generate revised SDC
    try:
        prop = engine_adapter.propose(
            design_context=f"[{TASK_ID}] {DESIGN_CONTEXT}",
            existing_sdc=initial_sdc,
            objective=f"[{TASK_ID}] {condition['objective']}",
            evidence_summary=feedback_text,
        )
        result["model_calls"] += 1
    except Exception as e:
        result["status"] = "INCOMPLETE"
        result["failure_class"] = "MODEL_FAILURE"
        result["failure_message"] = str(e)
        result["end_timestamp"] = datetime.now(timezone.utc).isoformat()
        return result

    if not prop.is_success:
        result["status"] = "INCOMPLETE"
        result["failure_class"] = prop.failure.kind if prop.failure else "MODEL_FAILURE"
        result["failure_message"] = prop.failure.message if prop.failure else "unknown"
        result["end_timestamp"] = datetime.now(timezone.utc).isoformat()
        return result

    revised_candidate = prop.candidate
    result["revised_sdc_hash"] = revised_candidate.candidate_hash
    result["revised_sdc_length"] = len(revised_candidate.sdc_text)
    result["proposal_changed"] = (
        revised_candidate.candidate_hash != hashlib.sha256(
            initial_sdc.encode("utf-8")
        ).hexdigest()
    )

    # Oracle evaluation of revised SDC
    try:
        oracle_final = oracle.validate(
            revised_candidate.sdc_text,
            input_identity=f"DIAG-{condition_key}-FINAL",
            design_metadata=design_metadata,
        )
        result["oracle_calls"] += 1
        if oracle_final.is_success:
            ev_final = oracle_final.evidence
            result["final_evidence_hash"] = ev_final.evidence_hash
            result["final_evidence_scope"] = ev_final.evidence_scope
            err_count_final = sum(1 for f in (ev_final.findings or [])
                                  if f.get("severity") == "error")
            result["final_error_count"] = err_count_final
            result["final_findings"] = ev_final.findings
            result["error_delta"] = err_count_final - result["initial_error_count"]
        else:
            result["final_evidence_hash"] = None
            result["final_evidence_scope"] = None
            result["final_error_count"] = None
            result["error_delta"] = None
    except Exception as e:
        result["measurement_failure"] = str(e)
        result["final_evidence_hash"] = None
        result["final_evidence_scope"] = None
        result["final_error_count"] = None
        result["error_delta"] = None

    # ERROR adherence check
    adherence = _check_error_adherence(revised_candidate.sdc_text)
    result["has_set_input_delay"] = adherence["has_set_input_delay"]
    result["has_set_output_delay"] = adherence["has_set_output_delay"]
    result["error_adherence"] = adherence["error_adherence"]

    result["status"] = "COMPLETED"
    result["end_timestamp"] = datetime.now(timezone.utc).isoformat()

    # Save artifacts
    cond_dir = base_dir / "formal" / "DIAGNOSTIC-001" / condition["name"]
    cond_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = cond_dir / "raw"
    raw_dir.mkdir(exist_ok=True)

    (raw_dir / "initial_sdc.txt").write_text(initial_sdc, encoding="utf-8")
    (raw_dir / "revised_candidate.json").write_text(
        json.dumps(revised_candidate.to_dict(), indent=2), encoding="utf-8"
    )
    (raw_dir / "feedback.json").write_text(feedback_text, encoding="utf-8")
    (raw_dir / "evidence_initial.json").write_text(
        json.dumps({
            "artifact_id": result.get("initial_evidence_hash", ""),
            "evidence_scope": result.get("initial_evidence_scope", ""),
            "findings": result.get("initial_findings", []),
        }, indent=2), encoding="utf-8"
    )
    if result.get("final_evidence_hash"):
        (raw_dir / "evidence_final.json").write_text(
            json.dumps({
                "artifact_id": result.get("final_evidence_hash", ""),
                "evidence_scope": result.get("final_evidence_scope", ""),
                "findings": result.get("final_findings", []),
            }, indent=2), encoding="utf-8"
        )

    # Save manifest (without findings lists for cleanliness)
    manifest = {k: v for k, v in result.items()
                if k not in ("initial_findings", "final_findings")}
    (cond_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    return result


def run_diagnostic(live: bool = False):
    """Run all 4 diagnostic conditions.

    Args:
        live: If True, use live opencode. If False, dry-run only (structure check).
    """
    base = Path(__file__).parent
    oracle = EvidenceOracle()
    design_metadata = _load_design_metadata(TASK_ID)

    engine_adapter = EngineerAdapter(
        LiveEngineerModel(
            timeout=60, max_tokens=2048, live=live,
            model=MODEL_NAME,
        )
    )

    # Generate full feedback from a reference initial evaluation
    ref_oracle = oracle.validate(
        ORIGINAL_SDC,
        input_identity="DIAG-REF-INIT",
        design_metadata=design_metadata,
    )
    if ref_oracle.is_success:
        full_feedback_text = _build_full_feedback(ref_oracle.evidence)
    else:
        raise RuntimeError("Reference Oracle evaluation failed")

    results = []
    for key in ["A", "B", "C", "D"]:
        cond = CONDITIONS[key]
        print(f"\n--- Condition {key}: {cond['name']} ---")
        result = run_diagnostic_condition(
            key, cond, oracle, design_metadata,
            engine_adapter, base, full_feedback_text,
        )
        results.append(result)
        status = result["status"]
        adherence = result.get("error_adherence", "?")
        delta = result.get("error_delta", "?")
        print(f"  status: {status}")
        print(f"  error_adherence: {adherence}")
        print(f"  error_delta: {delta}")

    # Save RUN_INDEX
    diag_dir = base / "formal" / "DIAGNOSTIC-001"
    diag_dir.mkdir(parents=True, exist_ok=True)
    index = {
        "experiment": "P078-HYPOTHESIS-ISOLATION",
        "model_id": MODEL_ID,
        "model_name": MODEL_NAME,
        "task_id": TASK_ID,
        "conditions": {
            r["condition"]: {
                "status": r["status"],
                "error_adherence": r.get("error_adherence"),
                "error_delta": r.get("error_delta"),
                "proposal_changed": r.get("proposal_changed"),
                "has_set_input_delay": r.get("has_set_input_delay"),
                "has_set_output_delay": r.get("has_set_output_delay"),
            }
            for r in results
        },
    }
    (diag_dir / "RUN_INDEX.json").write_text(
        json.dumps(index, indent=2), encoding="utf-8"
    )

    print(f"\nDiagnostic complete: {len(results)} conditions")
    print(f"RUN_INDEX written to {diag_dir / 'RUN_INDEX.json'}")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="P078 diagnostic runner")
    parser.add_argument("--live", action="store_true",
                        help="Use live opencode")
    args = parser.parse_args()
    run_diagnostic(live=args.live)
