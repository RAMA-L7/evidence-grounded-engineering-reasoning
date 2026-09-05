# EGER-CHANGE-046

- **Gate**: P174 — RQ-5 Final Experiment Readiness
- **Baseline**: `6df39ea28343c9ac5b4320a0f1531c7f98cd2ce1` (P173-R)
- **Purpose**: Verify the remaining P172 §16 prerequisites so a future,
  separately authorized EGER-RQ5-PILOT-002 can begin from a validated state.
- **Decision**: **READY** — PILOT-002 still requires separate authorization.

## What was verified

1. Ṛta 1.5.11 @ revision `3b5c2f2` (== adapter pin == nested HEAD);
   read-only `check --json` executes from cwd outside Ṛta. Nested-repo
   working-tree dirt (engineer_test_kit, dated 2026-08-16) pre-dates the
   P164+ series and was not caused by this gate.
2. OpenSTA 2.2.0 at `/root/opensta_build/OpenSTA/app/sta` (Ubuntu-24.04).
3. P163 substrate discrimination in WSL: PASS WNS 0.00 / slack 9.85 MET;
   VIOLATION WNS −0.10 / slack −0.10 VIOLATED.
4. Timing precondition: valid `clk` clock and constrained path
   `u_ff → data_out` present in both cases.
5. Real-provider harness smoke test (new `run_smoke_readiness.py`):
   both Oracle paths ran the full chain model → validity → Oracle →
   evidence → VerificationGate to completion. OpenSTA ACCEPT with a
   measured WNS (not vacuous); Ṛta REJECT via the pre-existing
   netlist-less fail-closed scope contract (recorded in P171).
6. Harness fixture tests 44/44 (validity gate, matrix assertion, retry,
   initial Oracle evaluation, NO_TIMING_CONSTRAINT, PO-2 aggregation).
7. EGER regression 864/864.

## Repair decisions (none required — all P172 items passed)

- No production-code change. No Ṛta, VerificationGate, evidence-contract,
  or C0–C5 change.

## Condition recorded for the future experiment gate

The Ṛta arm evaluates netlist-less at INSUFFICIENT scope and the gate
fail-closes REJECT on every evaluation (pre-existing contract; P171
retained). The future PILOT-002 authorization must resolve the Ṛta
evaluation-scope protocol question before trials, or the Ṛta condition will
exhibit a reject floor.

## Research boundaries

```text
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: NO
C0-C5 conclusions changed: NO
Oracle comparison performed: NO
VerificationGate authority changed: NO
PILOT-002 executed: NO
```

## Files

- Added: `research/implementation/EGER-P174-RQ5-FINAL-EXPERIMENT-READINESS-GATE-001.md`
- Added: `research/implementation/EGER-CHANGE-046.md`
- Added: `research/experiments/EGER-RQ5-PILOT-001/run_smoke_readiness.py` (readiness driver)
- Local-only (not committed): `smoke_readiness_record.json` and pre-existing
  raw/analysis/qualification records
