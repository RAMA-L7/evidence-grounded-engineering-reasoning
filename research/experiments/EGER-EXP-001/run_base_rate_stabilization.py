"""Base-rate stabilization (DIAGNOSTIC-007, P114/P115).

20 identical BENCH2-001 Base runs to establish a reliable baseline
ERROR-adherence rate.

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
TASK_ID = "BENCH2-001"

METADATA_DIR = (Path(__file__).resolve().parent.parent /
                "EGER-BENCH-002" / "evaluator_context")

DESIGN_CONTEXT = (
    "Module top with ports clk, reset, data_in[7:0], data_out[7:0]. "
    "Single clock domain clk at 10ns. No generated clocks."
)
OBJECTIVE = "Generate SDC that correctly defines the primary clock on clk"
INITIAL_SDC = "create_clock -name clk -period 10.0 [get_ports clk]"

RUNS_TOTAL = 20


def _load_design_metadata(task_id):
    path = METADATA_DIR / f"{task_id}.design_metadata.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return DesignMetadata.from_dict(json.load(f))


def _clopper_pearson_ci(k, n, alpha=0.05):
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


def run_single(run_number, oracle, engine_adapter, base_dir):
    """Run one iteration of the base-rate experiment."""
    start = datetime.now(timezone.utc)
    run_id = f"Base-run{run_number:02d}"
    design_metadata = _load_design_metadata(TASK_ID)

    result = {
        "run_id": run_id,
        "run_number": run_number,
        "start_timestamp": start.isoformat(),
        "status": "IN_PROGRESS",
    }

    # Oracle initial evaluation
    oracle_init = oracle.validate(
        INITIAL_SDC,
        input_identity=f"P115-{run_id}-INIT",
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
        input_identity=f"P115-{run_id}-FINAL",
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
    (base_dir / f"manifest-{run_id}.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )

    return result


def main():
    base = Path(__file__).parent
    diag7_dir = base / "formal" / "DIAGNOSTIC-007"
    diag7_dir.mkdir(parents=True, exist_ok=True)

    oracle = EvidenceOracle()
    engine_adapter = EngineerAdapter(
        LiveEngineerModel(timeout=60, max_tokens=2048, live=True,
                          model=MODEL_NAME)
    )

    all_results = []

    print(f"=== DIAGNOSTIC-007: Base-Rate Stabilization ({RUNS_TOTAL} runs) ===")
    for i in range(1, RUNS_TOTAL + 1):
        print(f"  Run {i}/{RUNS_TOTAL}...")
        r = run_single(i, oracle, engine_adapter, diag7_dir)
        all_results.append(r)
        adh = r.get("error_adherence", "?")
        delta = r.get("error_delta", "?")
        print(f"    adherence={adh}, delta={delta}, status={r['status']}")

    # Summary
    completed = [r for r in all_results if r["status"] == "COMPLETED"]
    adherent = sum(1 for r in completed if r.get("error_adherence"))
    activated = sum(1 for r in completed if r.get("proposal_changed"))
    n = len(completed)
    k = adherent
    lo, hi = _clopper_pearson_ci(k, n) if n > 0 else (0, 0)

    print(f"\n=== Summary ===")
    print(f"Completed: {n}/{RUNS_TOTAL}")
    print(f"Adherent:  {k}/{n} = {k/n:.0%}" if n > 0 else "Adherent: N/A")
    print(f"Activated: {activated}/{n}")
    print(f"95% CI:    [{lo:.1%}, {hi:.1%}]")
    print(f"\nHistorical comparison:")
    print(f"  P090 Base:              4/10 = 40%")
    print(f"  DIAGNOSTIC-006 Base:    8/10 = 80%")
    print(f"  DIAGNOSTIC-007 (this):  {k}/{n} = {k/n:.0%}" if n > 0 else "  DIAGNOSTIC-007: N/A")

    index = {
        "experiment": "P114-BASE-RATE-STABILIZATION",
        "model_id": MODEL_ID,
        "model_name": MODEL_NAME,
        "runs_total": RUNS_TOTAL,
        "completed": n,
        "adherent": k,
        "activated": activated,
        "rate": k / n if n > 0 else None,
        "ci_lower": lo,
        "ci_upper": hi,
        "results": [{
            "run_id": r["run_id"],
            "status": r["status"],
            "error_adherence": r.get("error_adherence"),
            "error_delta": r.get("error_delta"),
            "proposal_changed": r.get("proposal_changed"),
            "revised_sdc_length": r.get("revised_sdc_length"),
        } for r in all_results],
    }
    (diag7_dir / "RUN_INDEX.json").write_text(
        json.dumps(index, indent=2), encoding="utf-8"
    )
    print(f"\nRUN_INDEX written to {diag7_dir / 'RUN_INDEX.json'}")
    return all_results


if __name__ == "__main__":
    main()
