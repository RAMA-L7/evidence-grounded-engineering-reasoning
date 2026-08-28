"""10-run variability confirmation for BENCH2-002 (DIAGNOSTIC-004, P093/P094).

Runs BENCH2-002 treatment exactly 10 times with identical inputs.
Uses the frozen 287-char initial SDC with generated clock and clock groups.

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

from eger.engineer.model import LiveEngineerModel
from eger.engineer.adapter import EngineerAdapter
from eger.engineer.structured_feedback import render_structured_feedback
from eger.oracle.adapter import EvidenceOracle
from eger.oracle.schemas import DesignMetadata

# ---------------------------------------------------------------------------
# Frozen configuration
# ---------------------------------------------------------------------------
MODEL_ID = "EGER-MODEL-005"
MODEL_NAME = "opencode/mimo-v2.5-free"
ORACLE_REVISION = "3b5c2f2"
METADATA_VERSION = "eger.design_metadata.v1"
TASK_ID = "BENCH2-002"

METADATA_DIR = (Path(__file__).resolve().parent.parent /
                "EGER-BENCH-002" / "evaluator_context")

DESIGN_CONTEXT = (
    "Module top with ports clk, reset, data_in[7:0], data_out[7:0], cfg_reg[3:0]. "
    "Primary clock clk at 10ns. Generated clock clk_div2 = clk/2 on div_reg/Q. "
    "Asynchronous clock domains."
)
OBJECTIVE = "Generate SDC with primary clock and correctly constrained generated clock."

# Frozen 287-char initial SDC from RQ-4 BENCH2-002 initial candidate
INITIAL_SDC = """\
create_clock -name clk -period 10.0 [get_ports clk]

create_generated_clock -name clk_div2 \\
    -source [get_ports clk] \\
    -divide_by 2 \\
    -master_clock clk \\
    [get_pins div_reg/Q]

set_clock_groups -asynchronous \\
    -group [get_clocks clk] \\
    -group [get_clocks clk_div2]"""

NUM_RUNS = 10


def _load_design_metadata(task_id):
    path = METADATA_DIR / f"{task_id}.design_metadata.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return DesignMetadata.from_dict(json.load(f))


def _clopper_pearson_ci(k, n, alpha=0.05):
    """Compute 95% Clopper-Pearson CI using beta distribution quantiles."""
    from math import lgamma, exp, log as math_log

    def _betainc(a, b, x):
        if x <= 0: return 0.0
        if x >= 1: return 1.0
        if x > (a + 1) / (a + b + 2):
            return 1.0 - _betainc(b, a, 1.0 - x)
        lbeta = lgamma(a) + lgamma(b) - lgamma(a + b)
        front = exp(a * math_log(x) + b * math_log(1.0 - x) - lbeta) / a
        f = 1.0; c = 1.0; d = 0.0
        for i in range(200):
            m = i // 2 + 1
            if i == 0: num = 1.0
            elif i % 2 == 0:
                num = m * (b - m) * x / ((a + 2*m - 2) * (a + 2*m - 1))
            else:
                num = -((a + m - 1) * (a + b + m - 1) * x) / ((a + 2*m - 1) * (a + 2*m))
            d = 1.0 + num * d
            if abs(d) < 1e-30: d = 1e-30
            d = 1.0 / d
            c = 1.0 + num / c
            if abs(c) < 1e-30: c = 1e-30
            f *= d * c
        return front * (f - 1.0)

    def _quantile(p, a, b):
        if p <= 0: return 0.0
        if p >= 1: return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(100):
            mid = (lo + hi) / 2.0
            if _betainc(a, b, mid) < p: lo = mid
            else: hi = mid
        return (lo + hi) / 2.0

    if n == 0: return 0.0, 1.0
    lo = _quantile(alpha / 2, k, n - k + 1) if k > 0 else 0.0
    hi = _quantile(1 - alpha / 2, k + 1, n - k) if k < n else 1.0
    return lo, hi


def run_single(run_number, oracle, design_metadata, engine_adapter, base_dir):
    """Run one iteration of BENCH2-002 treatment."""
    start = datetime.now(timezone.utc)
    run_id = f"run-{run_number:03d}"
    result = {
        "run_id": run_id,
        "run_number": run_number,
        "task_id": TASK_ID,
        "start_timestamp": start.isoformat(),
        "status": "IN_PROGRESS",
    }

    # Oracle initial evaluation
    oracle_init = oracle.validate(
        INITIAL_SDC,
        input_identity=f"P094-{run_id}-INIT",
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

    # Build structured feedback (deterministic from evidence)
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

    # ERROR adherence check
    lower = revised.sdc_text.lower()
    result["has_set_input_delay"] = "set_input_delay" in lower
    result["has_set_output_delay"] = "set_output_delay" in lower
    result["error_adherence"] = (
        result["has_set_input_delay"] and result["has_set_output_delay"]
    )

    # Oracle final evaluation
    oracle_final = oracle.validate(
        revised.sdc_text,
        input_identity=f"P094-{run_id}-FINAL",
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

    end = datetime.now(timezone.utc)
    result["status"] = "COMPLETED"
    result["end_timestamp"] = end.isoformat()
    result["duration_seconds"] = (end - start).total_seconds()

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

    manifest = {k: v for k, v in result.items()}
    (base_dir / f"manifest-{run_id}.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    return result


def main():
    base = Path(__file__).parent
    diag4_dir = base / "formal" / "DIAGNOSTIC-004"
    diag4_dir.mkdir(parents=True, exist_ok=True)

    oracle = EvidenceOracle()
    design_metadata = _load_design_metadata(TASK_ID)
    engine_adapter = EngineerAdapter(
        LiveEngineerModel(timeout=60, max_tokens=2048, live=True,
                          model=MODEL_NAME)
    )

    # Verify feedback determinism
    ref_oracle = oracle.validate(
        INITIAL_SDC, input_identity="P094-REF",
        design_metadata=design_metadata,
    )
    ref_feedback = render_structured_feedback(ref_oracle.evidence)
    ref_hash = hashlib.sha256(ref_feedback.encode("utf-8")).hexdigest()
    print(f"Reference feedback hash: {ref_hash}")

    results = []
    for i in range(1, NUM_RUNS + 1):
        print(f"\n--- Run {i}/{NUM_RUNS} ---")
        r = run_single(i, oracle, design_metadata, engine_adapter, diag4_dir)
        results.append(r)
        adh = r.get("error_adherence", "?")
        delta = r.get("error_delta", "?")
        changed = r.get("proposal_changed", "?")
        print(f"  status: {r['status']}")
        print(f"  error_adherence: {adh}")
        print(f"  error_delta: {delta}")
        print(f"  proposal_changed: {changed}")

    completed = [r for r in results if r["status"] == "COMPLETED"]
    adherent = sum(1 for r in completed if r.get("error_adherence"))
    activated = sum(1 for r in completed if r.get("proposal_changed"))
    n = len(completed)

    ci_lower, ci_upper = _clopper_pearson_ci(adherent, n) if n > 0 else (0, 0)

    print(f"\n=== Summary ===")
    print(f"Completed: {n}/{NUM_RUNS}")
    print(f"Adherent: {adherent}/{n}")
    print(f"Activated: {activated}/{n}")
    print(f"Adherence rate: {adherent}/{n} = {adherent/n:.1%}" if n > 0 else "N/A")
    print(f"95% CI: [{ci_lower:.1%}, {ci_upper:.1%}]" if n > 0 else "N/A")

    index = {
        "experiment": "P093-BENCH2-002-VARIABILITY-CONFIRMATION",
        "model_id": MODEL_ID,
        "model_name": MODEL_NAME,
        "task_id": TASK_ID,
        "initial_sdc": INITIAL_SDC,
        "initial_sdc_length": len(INITIAL_SDC),
        "num_runs": NUM_RUNS,
        "runs_completed": n,
        "adherent": adherent,
        "activated": activated,
        "adherence_rate": adherent / n if n > 0 else None,
        "ci_95_lower": ci_lower,
        "ci_95_upper": ci_upper,
        "feedback_hash": ref_hash,
        "results": [{
            "run_id": r["run_id"],
            "status": r["status"],
            "error_adherence": r.get("error_adherence"),
            "error_delta": r.get("error_delta"),
            "proposal_changed": r.get("proposal_changed"),
            "duration_seconds": r.get("duration_seconds"),
        } for r in results],
    }
    (diag4_dir / "RUN_INDEX.json").write_text(
        json.dumps(index, indent=2), encoding="utf-8"
    )
    print(f"\nRUN_INDEX written to {diag4_dir / 'RUN_INDEX.json'}")
    return results


if __name__ == "__main__":
    main()
