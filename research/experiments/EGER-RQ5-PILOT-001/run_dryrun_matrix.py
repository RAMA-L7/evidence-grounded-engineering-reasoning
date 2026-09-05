"""P177 — RQ-5 PILOT-002 Execution Readiness: fixture dry-run.

Runs the frozen 2×2×2 matrix through the REPAIRED harness with DETERMINISTIC
FIXTURES ONLY (FakeOracle / FakeModelProvider). No real Ṛta, no OpenSTA, no
model, no WSL. This is a readiness simulation — NOT PILOT-002 execution and
NOT experimental data. Records are written locally (dryrun_records.json) and
never aggregated into the experiment dataset.

The dry-run exercises, mechanically:
- the frozen counterbalanced matrix + pre-run assertion,
- initial Oracle evaluation on the initial SDC (PO-3),
- candidate-validity gate (one trial's first attempt produces
  conversational filler → CANDIDATE_INVALID → bounded retry),
- both attempts retained when a retry occurs,
- deterministic PO-2/PO-3 derivation and qualified-accept accounting.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
PILOT_DIR = Path(__file__).resolve().parent
for p in (str(PROJECT_ROOT), str(PILOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from harness.orchestrator import run_matrix
from harness.matrix import frozen_matrix
from harness.fixtures import (
    FakeOracle,
    FakeModelProvider,
    build_pipeline,
    CONVERSATIONAL_FILLER,
    SDC_T1_VALID,
    SDC_T2_AGGRESSIVE,
    SDC_T2_RELAXED,
)

# Fixture output plans per trial (deterministic; task semantics only — the
# realistic Ṛta/OpenSTA discrimination is covered by the P176 real-chain
# tests, not by these fixtures).
#
#  - T1-Rta:      initial incomplete (REJECT) -> candidate complete (ACCEPT)
#  - T1-OpenSTA:  clean from the start (documented floor effect)
#  - T2-Rta:      initial incomplete (REJECT) -> relaxed complete (ACCEPT)
#  - T2-OpenSTA:  aggressive (REJECT) -> relaxed (ACCEPT), OR a retry path
#                 where the first model output is conversational filler
#                 (CANDIDATE_INVALID -> 1 bounded retry).
_FIXTURE_MODEL_OUTPUTS = {
    "T1-Rta-R1": [SDC_T1_VALID],
    "T1-Rta-R2": [SDC_T1_VALID],
    "T1-OpenSTA-R1": [SDC_T1_VALID],
    "T1-OpenSTA-R2": [SDC_T1_VALID],
    "T2-Rta-R1": [SDC_T2_RELAXED],
    "T2-Rta-R2": [SDC_T2_RELAXED],
    "T2-OpenSTA-R1": [SDC_T2_AGGRESSIVE, SDC_T2_RELAXED],
    # Retry path: attempt 1 iteration 1 -> conversational filler
    # (CANDIDATE_INVALID, retryable) -> attempt 2 -> relaxed complete.
    "T2-OpenSTA-R2": [CONVERSATIONAL_FILLER, SDC_T2_RELAXED],
}


def fixture_callables(row: dict):
    oracle_name = row["oracle"]
    outputs = _FIXTURE_MODEL_OUTPUTS[row["trial_id"]]
    oracle = FakeOracle(oracle_name=oracle_name)
    model = FakeModelProvider(outputs)
    return oracle.validate, model.invoke


def main() -> int:
    print("=" * 60)
    print("P177 — FIXTURE DRY-RUN of the frozen 8-trial matrix")
    print("=" * 60)
    print("NOTE: deterministic fixtures only. NOT PILOT-002. NOT experiment data.\n")

    normalizer, gate = build_pipeline()
    result = run_matrix(fixture_callables, normalizer, gate)

    records = result["records"]
    analysis = result["analysis"]
    identity_audit = result["identity_audit"]
    assert len(records) == 8, f"expected 8 records, got {len(records)}"

    print(f"Trials executed: {len(records)} (frozen order, asserted pre-run)")
    print(
        f"Identity audit: ok={identity_audit['ok']} "
        f"shared_initial_across_arms={identity_audit['shared_initial_across_arms']}"
    )
    print(f"  shared task initial hashes: {identity_audit['shared_task_initial_hashes']}")
    for rec in records:
        retry = f", retries={rec.get('retry_count')}, attempts={len(rec.get('attempts', []))}"
        print(
            f"  {rec['trial_id']:<15s} status={rec.get('completion_status'):9s} "
            f"iter={rec.get('iteration_count')} calls={rec.get('oracle_call_count')}{retry}"
        )

    print("\nDerived (from raw records only):")
    print(f"  completed={analysis['completed_trials']} failed={analysis['failed_trials']}")
    print(f"  oracle_evaluations={analysis['oracle_evaluations']} "
          f"successful={analysis['successful_oracle_evaluations']}")
    print(f"  evidence_artifacts={analysis['evidence_artifacts']} "
          f"retry_attempts={analysis['retry_attempts']}")
    for cond, c in sorted(analysis["per_condition"].items()):
        print(f"  {cond}: po1={c['po1']} po3={c['po3']} qualified_accept={c['qualified_accept']}")

    # Record locally (readiness simulation, not committed as experiment data).
    out = PILOT_DIR / "dryrun_records.json"
    out.write_text(
        json.dumps(
            {"records": records, "analysis": analysis, "identity_audit": identity_audit},
            indent=2, default=str,
        ),
        encoding="utf-8",
    )
    print(f"\nDry-run record written: {out} (kept local)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
