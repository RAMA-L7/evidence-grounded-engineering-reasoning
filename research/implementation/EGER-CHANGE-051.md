# CHANGE-051 — P179 RQ-5 PILOT-002 Execution

## Baseline

- HEAD before change: `04c33b4b88a4d3e4caedcd227daac40a4f995079` (P178)
- Branch: main; origin/main in sync

## Purpose

Execute the frozen RQ-5 controlled Oracle-validation pilot (EGER-RQ5-PILOT-002) authorized by P179 on the P178 READY state, using the repaired `harness/orchestrator.py` with real providers (opencode/mimo-v2.5-free, Ṛta 1.5.11 @ 3b5c2f2, OpenSTA 2.2.0). Record raw outcomes immutably, derive analysis deterministically, and produce the compliance/integrity/claim audit.

## Changes

| File | Change |
| ---- | ------ |
| research/experiments/EGER-RQ5-PILOT-001/run_pilot002.py | New: execution driver (manifest, real providers via orchestrator, raw/analysis/identity outputs) |
| research/experiments/EGER-RQ5-PILOT-001/harness/providers.py | Fix: subprocess encoding utf-8 (opencode UTF-8 output vs locale cp1252 decode crash) — harness robustness only |
| research/implementation/EGER-P179-RQ5-PILOT002-CONTROLLED-ORACLE-VALIDATION-EXECUTION-001.md | New: P179 execution report |
| research/implementation/EGER-CHANGE-051.md | This record |

Experimental outputs (`EGER-RQ5-PILOT-002/` manifest/raw/identity/analysis + execution log) are publication-sensitive and kept local-only.

## Execution Results

- 8/8 trials COMPLETED; 0 failures; 0 retries
- Counterbalanced frozen order executed exactly as manifested
- 22 Oracle evaluations, all successful, all evidence-compatible
- PO-1: T1-Ṛta 2 ROBUST, T1-OpenSTA 2 MARGINAL, T2-Ṛta 2 ROBUST, T2-OpenSTA 2 MARGINAL
- PO-3: T1-Ṛta IMPROVED×2; T1-OpenSTA NOT_IMPROVED×2 (already-clean initial); T2-Ṛta IMPROVED×2; T2-OpenSTA WORSE×2 (genuine persistent timing violation, qualified_accept=0)
- Identity audit ok=true; shared initial SDC hash per task across both Oracle arms
- Key observation: T2 aggressive 0.05 ns clock — Ṛta ACCEPT (structurally valid constraints), OpenSTA REJECT (WNS −0.01/−0.02) on the same shared candidate: authority-separated disagreement, not interchangeability
- Replication pairs agree at outcome level on all four conditions

## Decision

RQ-5 PILOT VALIDATED — descriptive, Level 2 claim only. Execution was protocol-conformant: no deviation (unlike P170); the frozen bounded retry was available but never needed.

## Research Boundaries

```text
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: YES
C0-C5 conclusions changed: NO
Oracle comparison performed: YES (descriptive, authority-separated)
Oracle interchangeability established: NO
VerificationGate authority changed: NO
Epistemic-state logic added: NO
Authorization logic added: NO
```

## Verification

- EGER full suite: 878/878 PASS
- Harness suite: 62/62 PASS
- Independent recomputation reconciles analysis counts with raw records

## Git

- Commit: `ad4d86a` — message: `research: execute P179 RQ5 PILOT-002 oracle validation`
- Pushed to origin/main; HEAD == origin/main
- Universal_Principles_Library/ untouched and unstaged

## Next

STOP. No additional trials, no protocol modification, no claim upgrade. Await an explicit research-review gate before further interpretation.
