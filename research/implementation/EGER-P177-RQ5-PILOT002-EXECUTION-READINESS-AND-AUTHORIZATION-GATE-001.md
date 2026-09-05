# EGER-P177 — RQ-5 PILOT-002 Execution Readiness & Authorization Gate

- **Gate**: P177 — RQ-5 PILOT-002 Execution Readiness & Authorization
- **Governing records**: P169 (frozen protocol), P170–P176 + CHANGE-040..048
  (P170 executed pilot, P171 INCONCLUSIVE audit, P172 repair design, P173/P173-R
  harness repair + model qualification, P174 READY, P175 scope resolution,
  P176 implementation/validation PASS)
- **Date**: 2026-09-05
- **Baseline**: `5b20ac9a5cb2af594318ebdcc04a425e021cb0f4` (P176)
- **Decision**: **READY** — a separate, explicit user authorization is still
  REQUIRED before the first PILOT-002 trial. This gate performs a fixture
  dry-run only; no PILOT-002 execution, no experimental data collected.

---

## 1. Objective

Pre-execution authorization gate: verify that the repaired experiment
harness is protocol-complete against the frozen P169/P172 design, audit the
18-point checklist, run all relevant tests, and execute a fixture-only
dry-run/readiness simulation of the full 8-trial matrix.

## 2. Protocol-Completeness Audit (18 items)

| # | Requirement | Status | Evidence |
| - | ----------- | ------ | -------- |
| 1 | 2 tasks × 2 Oracles × 2 reps = 8 planned trials | PASS | `harness/matrix.py` `FROZEN_MATRIX` (8 rows); `orchestrator.run_matrix` asserts len == 8 |
| 2 | Same candidate SDC bytes evaluated by both Oracles | PASS | Task-level shared frozen initial SDC (`tasks.py`); per-trial the runner passes the identical extracted candidate to whichever Oracle is bound; no Oracle-specific candidates exist |
| 3 | Validity gate rejects non-SDC before Oracle invocation | PASS | `trial_runner._run_attempt` classifies via `classify_candidate`; non-VALID_SDC fails the attempt before any `oracle_call` |
| 4 | Initial Oracle evaluation recorded before revision | PASS | `_run_attempt` step 1 records `initial_oracle_result` + `initial_evidence_hash` before the revision loop |
| 5 | `initial_oracle_result` present and complete | PASS | Record includes is_success/scope/error count/evidence hash; dry-run asserts every trial has a successful initial evaluation |
| 6 | Max 1 bounded retry implemented; `retry_count` recorded | PASS | `MAX_RETRIES = 1`; `run_trial` records `attempts` + `retry_count = len(attempts)-1` |
| 7 | Counterbalanced order: T1 Ṛta first, T2 OpenSTA first | PASS | `FROZEN_MATRIX` (Ṛta-first T1 block, OpenSTA-first T2 block); `assert_matrix_order` runs pre-trial-1 |
| 8 | Both attempts retained when a retry occurs | PASS | `attempts` list on every record; test asserts 2 attempts for the retry trial |
| 9 | PO-2 mechanically derivable from raw trial records | PASS | `analysis.analyze_trials` derives all counts from records only; no manual totals; dry-run confirms evidence_artifacts == evaluations |
| 10 | PO-3 mechanically derivable (initial vs final Oracle result) | PASS | `compute_po3` over initial vs final summaries; per-condition PO-3 tables derived in the dry-run |
| 11 | OpenSTA valid-clock guard prevents vacuous timing ACCEPT | PASS | Validity gate requires `create_clock` (P172 §5/§13 layer 1) + `no_timing_constraint_iterations` experiment-layer flag |
| 12 | Ṛta uses the repaired FULL-scope path + frozen P055 DesignMetadata | PASS | P176 wiring (`providers.build_rta_oracle_call` passes frozen `design_metadata`); real-chain tests prove FULL scope + discriminations |
| 13 | `metadata_unqualified_iterations` propagated; treatment in qualification explicitly defined | PASS | **P177 rule:** `derive_trial_metrics` computes `qualified_accept`; an ACCEPT resting on metadata-unqualified (PARTIAL) evidence is not qualified and PO-1 is capped at MARGINAL (never ROBUST). Propagated to `analysis.py` per-condition/per-Oracle/per-trial |
| 14 | No silent candidate repair | PASS | Runner never edits candidate command lines; `extract_sdc_block` only strips fences/wrappers (documented); no Oracle-specific candidate rewriting |
| 15 | Provider/model failures distinguished from engineering REJECT | PASS | PROVIDER_FAILURE / EMPTY_OUTPUT / CANDIDATE_INVALID / TIMEOUT are failure kinds (retryable per policy); gate REJECT on a valid candidate is an engineering outcome, never retried |
| 16 | Temperature/model configuration frozen and recorded | PASS (with correction) | Model `opencode/mimo-v2.5-free` frozen (`providers.DEFAULT_MODEL`); invocation flags constant. **Verified: the opencode CLI exposes NO temperature parameter and no config file sets sampling** → sampling is provider-default, recorded as such. This supersedes the P170-era "temperature = 0.0" claim (not reproducible via `opencode run`). Model stochasticity is handled by the frozen bounded retry + replication |
| 17 | Trial order and replication identities frozen before execution | PASS | `FROZEN_MATRIX` in code; `assert_matrix_order` before trial 1; no runtime shuffling |
| 18 | No retry or reordering after seeing results | PASS | Retry policy and order are code-frozen in `run_trial`/`orchestrator`; the orchestrator makes no methodology decisions |

## 3. Harness Gap Closed in This Gate

The repaired machinery (matrix, trial runner, providers, analysis) existed
after P173/P176 but **no repaired orchestrator** executed the frozen matrix:
`run_experiment.py` is the flawed P170 script (no validity gate, no initial
Oracle evaluation, no retry, chat-style prompts, Ṛta-first in both blocks)
and is retained only as a historical record — it MUST NOT be used for
PILOT-002.

This gate adds the protocol-complete orchestrator:

- **`harness/orchestrator.py`**: `run_matrix(callables, normalizer, gate)` —
  frozen order, `assert_matrix_order` pre-run, `run_trial` per row,
  `analyze_trials` for deterministic aggregation. The SAME orchestrator is
  used for the fixture dry-run (this gate) and, with separate authorization,
  the real PILOT-002 run (callables from `providers.py`).
- **`run_dryrun_matrix.py`**: fixture-only driver (no Ṛta/OpenSTA/model/WSL).

## 4. Qualified-Accept Rule (P177 §13 — explicit treatment)

Defined in `harness/trial_runner.py` `derive_trial_metrics`:

- `qualified_accept` = True iff the trial reached ACCEPT and no ACCEPTing
  iteration was metadata-unqualified (`metadata_all_validated is False`).
  OpenSTA has no design_metadata → `qualified_accept == accept_reached`.
- An unqualified accept is **not** a clean success: PO-1 is capped at
  MARGINAL (an accept resting on PARTIAL-metadata evidence can never be
  ROBUST). This is the experiment-layer fail-closed treatment of the
  FROZEN gate's PARTIAL-with-zero-errors acceptance (P176 residual).
- Propagated into `analysis.py`: per-condition `qualified_accept` counts,
  per-Oracle `qualified_accepts` + `metadata_unqualified_iterations`,
  per-trial `qualified_accept` + `metadata_unqualified_iterations`.

## 5. Fixture Dry-Run (readiness simulation — NOT PILOT-002)

`run_dryrun_matrix.py` executed the full frozen matrix with deterministic
fixtures (FakeOracle/FakeModelProvider; real EvidenceNormalizer +
VerificationGate):

| Trial | Status | Iterations | Oracle calls | Retries |
| ----- | ------ | ---------: | -----------: | ------: |
| T1-Rta-R1 | COMPLETED | 1 | 2 | 0 |
| T1-OpenSTA-R1 | COMPLETED | 1 | 2 | 0 |
| T1-Rta-R2 | COMPLETED | 1 | 2 | 0 |
| T1-OpenSTA-R2 | COMPLETED | 1 | 2 | 0 |
| T2-OpenSTA-R1 | COMPLETED | 2 | 3 | 0 |
| T2-Rta-R1 | COMPLETED | 1 | 2 | 0 |
| T2-OpenSTA-R2 | COMPLETED | 1 | 2 | **1** (2 attempts) |
| T2-Rta-R2 | COMPLETED | 1 | 2 | 0 |

Derived: 8/8 completed, 17 Oracle evaluations = 17 evidence artifacts,
1 retry (both attempts retained). Per-condition PO-1/PO-3/qualified_accept
derived deterministically. The T1-OpenSTA MARGINAL result reproduces the
documented clean-from-start floor effect; the retry trial exercised
CANDIDATE_INVALID → bounded retry → completed. Dry-run record written
locally (`dryrun_records.json`), never committed.

## 6. Model Configuration Freeze (item 16 — recorded)

- Model: `opencode/mimo-v2.5-free` (frozen constant).
- Invocation: `opencode.cmd run --model <model> <prompt>` (default agent).
- Sampling: **provider default** — verified `opencode run --help` exposes no
  temperature flag, and no opencode config file (user or repo) sets sampling
  parameters. This corrects the earlier "temperature = 0.0" notation from
  P170/P171, which is not reproducible through this CLI.
- Stochasticity handling (unchanged): one bounded retry for generation
  failures + 2 replications per cell (descriptive pilot, P169/P172).

## 7. Regression

| Suite | Result |
| ----- | ------ |
| EGER full suite (`python -m pytest tests -q`) | **878 passed** (unchanged) |
| Harness suite (`python -m pytest .../harness_tests -q`) | **59 passed** (52 + 7 new orchestrator/qualified-accept tests) |

## 8. Research Boundary

```text
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: NO (dry-run is fixture simulation, not data collection)
C0-C5 conclusions changed: NO
Oracle comparison performed: NO
VerificationGate authority changed: NO
EGER production code changed: NO (harness-scope only)
PILOT-002 executed: NO
```

## 9. Known Limitations / Conditions for PILOT-002

1. Synthetic 3-cell substrate; WSL2 + full OpenSTA binary path required.
2. Model is an agent-mode file-writing model; prompt must stay in the terse
   directive form (P173-R); sampling is provider-default (stochastic).
3. Real-provider execution needs a thin driver supplying the real callables
   from `providers.py` through the SAME orchestrator (authorized at the
   execution gate).
4. `metadata_unqualified` treatment is defined (P177 §4); the execution gate
   must record it in the trial manifest.
5. OpenSTA T1 floor effect and Ṛta SDC-005/006 (T1) / SDC-008/009 (T2)
   gradients are documented design properties.

## 10. Decision

```text
READY
```

All 18 protocol-completeness items verified; harness is protocol-complete
(frozen matrix, bounded retry, counterbalancing, initial Oracle evaluation,
validity gate, deterministic PO-2/PO-3, qualified-accept rule); fixture
dry-run of all 8 trials succeeds; regressions green (878 EGER / 59 harness).

**READY does NOT authorize execution.** A separate, explicit user
authorization is required before the first EGER-RQ5-PILOT-002 trial. That
authorized execution must use `harness/orchestrator.py` with real providers
and must not alter the frozen protocol after seeing results.

## 11. Git

- Commit: `(P177 commit, see git log)`
- HEAD == origin/main: YES
- `Universal_Principles_Library/` untouched
- Local-only (not committed): `raw_trials.json`, `analysis.json`,
  `qualification_record.json`, `smoke_readiness_record.json`,
  `dryrun_records.json`
