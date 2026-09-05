# EGER-CHANGE-049

- **Gate**: P177 — RQ-5 PILOT-002 Execution Readiness & Authorization
- **Baseline**: `5b20ac9a5cb2af594318ebdcc04a425e021cb0f4` (P176)
- **Purpose**: Verify the repaired harness is protocol-complete against the
  frozen P169/P172 design and run a fixture-only dry-run. No PILOT-002
  execution.
- **Decision**: **READY** — separate user authorization still required
  before the first PILOT-002 trial.

## What was verified (18-item checklist, all PASS)

Frozen 8-trial counterbalanced matrix + pre-run assertion; shared candidate
bytes per trial; validity gate before Oracle invocation; initial Oracle
evaluation recorded; 1 bounded retry with both attempts retained;
deterministic PO-2/PO-3 from raw records; OpenSTA valid-clock guard; Ṛta
repaired FULL-scope path with frozen P055 DesignMetadata; no silent
candidate repair; failure kinds distinguished from engineering REJECT;
order/replication frozen; no post-result retry/reorder.

## Harness gap closed

No repaired matrix orchestrator existed (run_experiment.py is the flawed
P170 script, retained as history only). Added `harness/orchestrator.py`
(frozen-order matrix runner + pre-run assertion + deterministic analysis)
used by the fixture dry-run now and the real run later (same code path),
plus `run_dryrun_matrix.py` (fixture-only).

## Item-13 treatment defined and implemented

`derive_trial_metrics` now computes `qualified_accept`: an ACCEPT resting on
metadata-unqualified (PARTIAL) evidence is not qualified and PO-1 is capped
at MARGINAL (never ROBUST). Propagated into `analysis.py` per-condition,
per-Oracle (`qualified_accepts`, `metadata_unqualified_iterations`), and
per-trial rows.

## Model-configuration correction (item 16)

Verified the opencode CLI exposes no temperature flag and no config sets
sampling → sampling is provider default. This supersedes the P170-era
"temperature = 0.0" notation (not reproducible via `opencode run`).

## Fixture dry-run result

8/8 trials completed in frozen counterbalanced order; 1 bounded retry
exercised (T2-OpenSTA-R2, 2 attempts retained); 17 Oracle evaluations = 17
evidence artifacts; PO-1/PO-3/qualified_accept derived deterministically.
Dry-run record kept local (`dryrun_records.json`), not committed.

## Regression

EGER suite 878/878; harness suite 59/59 (52 + 7 new orchestrator /
qualified-accept tests).

## Research boundaries

```text
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: NO (fixture simulation only)
C0-C5 conclusions changed: NO
VerificationGate authority changed: NO
EGER production code changed: NO (harness-scope only)
PILOT-002 executed: NO
```

## Files

- Added: `harness/orchestrator.py`, `run_dryrun_matrix.py`,
  `harness_tests/test_orchestrator.py`,
  `EGER-P177-RQ5-PILOT002-EXECUTION-READINESS-AND-AUTHORIZATION-GATE-001.md`,
  this file
- Modified: `harness/trial_runner.py` (qualified_accept rule),
  `harness/analysis.py` (propagation)
