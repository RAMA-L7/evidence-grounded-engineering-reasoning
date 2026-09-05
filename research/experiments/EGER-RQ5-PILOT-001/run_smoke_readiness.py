"""P174 — Real-provider harness smoke test (readiness gate, not experimental data).

Exercises the complete repaired chain with REAL providers, once per Oracle:

    model -> candidate-validity gate -> Oracle (Rta | OpenSTA) -> evidence
    -> VerificationGate

plus the P172 PO-3 initial-Oracle-evaluation step. One model invocation per
Oracle path (bounded, ~30-180s each). Outputs are readiness observations,
NOT RQ-5 experimental data — recorded locally, never aggregated into the
experiment dataset.

Smoke-test assertions (P174):
  1. Initial Oracle evaluation on the frozen T1 initial SDC succeeds and
     produces evidence entering the contract (PO-3 measurement exists).
  2. A real model call produces a candidate that passes the validity gate
     (VALID_SDC) or is recorded as a clean generation failure — no crash.
  3. Oracle evaluation of the candidate succeeds and evidence normalizes.
  4. VerificationGate returns ACCEPT/REJECT (never raises) and remains the
     sole decision authority.
  5. OpenSTA results are NOT vacuous: candidate must define create_clock and
     the evaluation must report a measured WNS (NO_TIMING_CONSTRAINT guard).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PILOT_DIR = Path(__file__).resolve().parent
for p in (str(PROJECT_ROOT), str(PILOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from harness.tasks import TASKS
from harness.trial_runner import (
    _build_prompt,
    oracle_summary,
    sha256_text,
)
from harness.candidate_validity import (
    classify_candidate,
    extract_sdc_block,
    VALID_SDC,
)
from harness.providers import (
    build_model_call,
    build_rta_oracle_call,
    build_opensta_oracle_call,
    resolve_opensta_binary_wsl,
    build_pipeline_components,
)

SUBSTRATE = PROJECT_ROOT / "research/implementation/opensta_pilot"
NETLIST = SUBSTRATE / "design/simple_path.v"
LIB = SUBSTRATE / "liberty/simple_cells.lib"


def smoke_one(oracle_name: str, task_id: str, workdir: Path) -> dict:
    """Run one smoke trial: initial eval -> model -> validity -> Oracle -> gate."""
    task = TASKS[task_id]
    initial_sdc = task["initial_sdc"]
    normalizer, gate = build_pipeline_components()["normalizer"], build_pipeline_components()["gate"]

    if oracle_name == "Rta":
        oracle_call = build_rta_oracle_call(timeout_seconds=180)
    else:
        sta_bin = resolve_opensta_binary_wsl()
        oracle_call = build_opensta_oracle_call(
            sta_binary=sta_bin, netlist_path=NETLIST, lib_path=LIB,
            design_name="simple_path", timeout_seconds=180,
        )

    record = {"oracle": oracle_name, "task_id": task_id}

    # 1. Initial Oracle evaluation (PO-3 repair)
    initial_result = oracle_call(initial_sdc, f"smoke-{oracle_name}-initial")
    record["initial_oracle_summary"] = oracle_summary(initial_result, oracle_name)
    if not initial_result.is_success:
        record["status"] = "INITIAL_EVAL_FAILED"
        return record
    record["initial_evidence_hash"] = getattr(initial_result.evidence, "evidence_hash", None)

    # 2. Real model call -> validity gate
    prompt = _build_prompt(task["design_context"], initial_sdc, [], oracle_name)
    model_call = build_model_call(model="opencode/mimo-v2.5-free",
                                  cwd=PROJECT_ROOT, workdir=workdir, timeout_seconds=180)
    raw = model_call(prompt)
    validity = classify_candidate(raw, task_id=task_id)
    record["candidate_validity"] = validity
    record["candidate_raw_hash"] = sha256_text(raw or "")
    if validity != VALID_SDC:
        record["status"] = "CANDIDATE_GENERATION_FAILED"
        record["raw_preview"] = (raw or "")[:200]
        return record

    sdc_block = extract_sdc_block(raw)
    record["clock_defined"] = "create_clock" in (sdc_block or "")
    record["candidate_sdc_hash"] = sha256_text(sdc_block or "")

    # 3. Oracle evaluation of candidate
    result = oracle_call(sdc_block, f"smoke-{oracle_name}-candidate")
    record["candidate_oracle_summary"] = oracle_summary(result, oracle_name)
    if not result.is_success:
        record["status"] = "ORACLE_EVAL_FAILED"
        return record

    # NO_TIMING_CONSTRAINT guard: OpenSTA must have a measured WNS (clock present).
    if oracle_name == "OpenSTA":
        scope = getattr(result.evidence, "analysis_scope", None) or {}
        record["wns"] = scope.get("wns") if isinstance(scope, dict) else getattr(scope, "wns", None)
        if record["wns"] is None:
            record["status"] = "NO_TIMING_CONSTRAINT"
            return record

    # 4. Evidence normalization + VerificationGate
    from eger.engineer.candidate import build_candidate
    candidate = build_candidate(sdc_block)
    evidence = normalizer.normalize(
        result.evidence, task_id=task_id,
        candidate_hash=sha256_text(sdc_block)[:12],
    )
    verification = gate.evaluate(candidate, evidence)
    record["evidence_hash"] = evidence.evidence_hash
    record["verification_decision"] = verification.decision
    record["verification_reason"] = verification.reason
    record["status"] = "CHAIN_COMPLETE"
    return record


def main() -> int:
    print("=" * 60)
    print("P174 — REAL-PROVIDER HARNESS SMOKE TEST (readiness)")
    print("=" * 60)
    print("NOTE: readiness observations only; NOT RQ-5 experimental data.\n")

    workdir = PILOT_DIR / "model_scratch"
    workdir.mkdir(parents=True, exist_ok=True)
    results = {}
    exit_code = 0
    for oracle_name in ("Rta", "OpenSTA"):
        for task_id in ("T1",):  # one bounded smoke per Oracle path
            print(f"[smoke] oracle={oracle_name} task={task_id} ...")
            rec = smoke_one(oracle_name, task_id, workdir)
            results[f"{oracle_name}-{task_id}"] = rec
            print(json.dumps(rec, indent=2))
            # Remove the model's file output between calls (agent-mode writes
            # timing.sdc into the workspace).
            for stray in (PROJECT_ROOT / "timing.sdc", workdir / "timing.sdc"):
                if stray.exists():
                    stray.unlink()
            if rec["status"] != "CHAIN_COMPLETE":
                exit_code = 1

    print("=" * 60)
    print("SMOKE SUMMARY")
    for key, rec in sorted(results.items()):
        print(f"  {key}: {rec['status']}  -> {rec.get('verification_decision', 'N/A')}")
    print("=" * 60)
    summary = {
        "statuses": {k: v["status"] for k, v in results.items()},
        "chain_complete": all(v["status"] == "CHAIN_COMPLETE" for v in results.values()),
    }
    out = PILOT_DIR / "smoke_readiness_record.json"
    out.write_text(json.dumps({"results": results, "summary": summary}, indent=2), encoding="utf-8")
    print(f"Record written: {out} (kept local, not committed)")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
