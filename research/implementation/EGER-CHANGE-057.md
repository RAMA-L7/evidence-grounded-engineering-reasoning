# EGER — CHANGE-057

## Change Record: P185 — Model-Comparison RQ-5 Controlled Experiment Execution

| Field | Value |
| ----- | ----- |
| Baseline | `776a50c` (P184 READY) |
| Change ID | CHANGE-057 |
| Date | 2026-09-07 |
| Gate | P185 (authorized execution) |
| Status | COMPLETE |

## Purpose

Execute the frozen 16-trial model-comparison experiment (2 models × 2 tasks × 2 Oracles × 2 replications) with real providers, testing model dependence of the EGER evidence-grounded control loop under the same deterministic evaluation authorities and VLSI tasks.

## What Was Done

1. **Execution:** 16 trials run via `run_pilot003.py` → `harness/orchestrator.run_model_matrix` with real providers (pinned Ṛta + P055 metadata, OpenSTA 2.2.0, both qualified models). Completed in 2483.3 s. Immutable manifest written before trial 1; raw records preserved before analysis.
2. **Harness additions (additive, backward-compatible, harness-scope only):**
   - `harness/model_matrix.py` — frozen 16-trial model-comparison matrix + pre-run order assertion (P183 §10 / P185 §2).
   - `harness/orchestrator.py` — `run_model_matrix` entry (same construction contract as `run_matrix`, model recorded on every trial).
   - `harness/trial_runner.py` — optional `model` provenance field on trial records (default None; existing behavior unchanged).
   - `harness/analysis.py` — `per_model` and `per_model_condition` deterministic aggregation (additive keys).
   - `harness_tests/test_model_matrix.py` — 12 new fixture tests (16-cell matrix, order assertion, model propagation, per-model analysis, identity audit).
3. **No EGER production code modified.** Ṛta, VerificationGate, C0–C5, RQ-4, RQ-5 conclusions unchanged.

## Results

| metric | value |
| ------ | ----- |
| Planned / completed / failed | 16 / 15 / 1 |
| Failure | T1-mimo-R2 — CANDIDATE_INVALID (baseline model conversational-filler output; both bounded attempts retained) |
| Retries | 3 (all mimo, all retryable CANDIDATE_INVALID; 2 recovered, 1 unrecovered) |
| Oracle evaluations / evidence artifacts | 43 / 43 (all successful, all compatible) |
| PO-1 | mimo 2 ROBUST / 5 MARGINAL / 1 FAILED; nemotron 4 ROBUST / 4 MARGINAL / 0 FAILED |
| PO-3 | mimo 2 IMPROVED / 3 NOT_IMPROVED / 2 WORSE / 1 NOT_MEASURABLE; nemotron 4 IMPROVED / 4 NOT_IMPROVED / 0 / 0 |
| qualified_accept | mimo 4/8; nemotron 7/8 |
| Identity audit | ok=True, 0 violations, shared initial across arms |

## Decision

```text
P185 verdict: PASS

Experiment completed with valid data; protocol compliance, provenance,
and integrity audits clean; conclusions remain within the frozen claim
boundary. Operation under two tested models is supported descriptively.
Model independence NOT established. 1 documented baseline-model output
failure preserved (not replaced, not silently repaired).
```

## Research Boundaries

```text
RQ-4 reopened: NO
RQ-5 reopened: NO
C0-C5 changed: NO
Rta modified: NO
VerificationGate modified: NO
Model independence established: NO
Statistical inference performed: NO
```

## Git / Tests

- Commit: `<commit>`
- EGER suite: 878/878 PASS · Harness suite: 74/74 PASS
- Raw experimental records kept local (not committed)
- Universal_Principles_Library/ untouched

## Next

STOP. No additional trials, no protocol modification, no claim upgrade. Await independent P186 research-review gate before any further interpretation.