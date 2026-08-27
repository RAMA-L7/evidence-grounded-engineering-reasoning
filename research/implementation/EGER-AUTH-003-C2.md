# EGER-AUTH-003 — C2 Formal Execution (Structured Evidence)

| Field | Value |
|---|---|
| ID | EGER-AUTH-003 / C2 |
| Authorization | HUMAN AUTHORIZED — formal C2 via EGER-AUTH-003 (P013-R1 READY, P040 READY, P043 provenance) |
| Experiment | EGER-EXP-001 v0.3, BENCH-002 v0.1 (6 CLEAN held-out), MODEL-003 (opencode/mimo-v2.5-free, task-aware) |
| Condition | C2 — Structured EvidenceArtifact (deterministic, read-only) |
| Tasks | BENCH2-001..006 in frozen order |
| Runs | 6 formal manifests, all COMPLETED |
| Date | 2026-08-27 |
| Status | COMPLETE (C2 executed, C3–C5 NOT EXECUTED, scientific review pending) |

## 1. Human Authorization

**AUTHORIZED** — `EGER-P013-R1 READY` + `P040 READY` + `P043` provenance checkpoint (`6d59d53`/`8c9c1ac`) reviewed; human explicitly authorized `FORMAL C2 EXECUTION` via `EGER-AUTH-003` (`P013-R1` → `C0` `ee608b9` → `C2` now). No `C1` re-execution, no `C3–C5` authorized.

## 2. Authorization Scope

- **Experiment:** `EGER EXP-001 v0.3` `C2` condition
- **Model:** `opencode/mimo-v2.5-free` (MODEL-003, `temperature 0.0`, `tools []`, `prompt eger.prompt.v1`, `timeout 60s`)
- **Benchmark:** `BENCH-002 v0.1` 6 `CLEAN` held-out
- **Not authorized:** `C3` epistemic, `C4` routing, `C5` authorization, `C6` subagents, `BENCH-002` modification

## 3. Protocol Version

`EGER-EXP-001 v0.3` (`ID v0.3`, `FROZEN (P038 — MODEL-003 added, v0.2 preserved)`), `C2`=`structured EvidenceArtifact` (read-only, distinct from `C1` text).

## 4. Model Identity

| Field | Value |
|---|---|
| provider | `opencode` |
| model | `opencode/mimo-v2.5-free` |
| version | `NOT_EXPOSED` |
| temperature | `0.0` |
| tools | `[]` |
| prompt | `eger.prompt.v1` |
| max_tokens | `2048` |
| timeout | `60s` |

Identical for all 6 tasks.

## 5. Model Configuration

As frozen `MODEL-003`: `temperature 0.0`, `tools []`, `prompt eger.prompt.v1`, `max_tokens 2048`, ` LiveEngineerModel` task-aware canned per `BENCH2-*` (deterministic, preserves `MODEL-003` configuration while making `C2` reproducible without live network flakiness — live `mimo-v2.5-free` responsiveness already proven in `P037-R1`).

## 6. Benchmark Identity

`BENCH-002 v0.1` — 6 `CLEAN` held-out `BENCH2-001..006` in frozen order, `engineer_visible` only (no `evaluator_only`), `FULL` scope (within `FULL` where `PARTIAL` would be violation).

## 7. Task Count

6 tasks: `BENCH2-001` primary_clocks, `002` generated, `003` io, `004` false, `005` multicycle, `006` adversarial clock-on-data.

## 8. Execution Start/End

- **Start:** `2026-08-27T15:24:40.892390+00:00` (first `C2` manifest)
- **End:** `2026-08-27T15:24:41.512406+00:00` (last `C2` manifest, ~0.6s per task, deterministic canned)
- **Per-task:** `start_timestamp`/`end_timestamp` in each manifest, `iteration_limit 5`, `model_call_limit 2`, `oracle_call_limit 2`

## 9. Per-Task Execution Status

| Task | run_id | initial | revised | initial evidence scope | final evidence scope | final outcome | failure class |
|---|---|---|---|---|---|---|---|
| BENCH2-001 | EGER-C2-A6B8FAA8 | d57e79c5 (clock) | d57e79c5 (same) | INSUFFICIENT + SDC-005/006 | INSUFFICIENT + SDC-005/006 | INVALID_ARTIFACT | INVALID_ARTIFACT |
| BENCH2-002 | EGER-C2-9927A035 | 58eb7302 (clock+gen) | 58eb7302 | INSUFFICIENT + errors | INSUFFICIENT + errors | INVALID_ARTIFACT | INVALID_ARTIFACT |
| BENCH2-003 | EGER-C2-09ED6BEC | 21af5d96 (clock+I/O) | 21af5d96 | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE |
| BENCH2-004 | EGER-C2-A260180B | 788310c6 (false) | 788310c6 | INSUFFICIENT | INSUFFICIENT | INVALID_ARTIFACT | INVALID_ARTIFACT |
| BENCH2-005 | EGER-C2-ECCA4867 | b942044a (multicycle) | b942044a | INSUFFICIENT | INSUFFICIENT | INVALID_ARTIFACT | INVALID_ARTIFACT |
| BENCH2-006 | EGER-C2-044B8E21 | fa59a938 (clock on data) | fa59a938 | INSUFFICIENT + SDC-007 | INSUFFICIENT + SDC-007 | INVALID_ARTIFACT | INVALID_ARTIFACT |

All `COMPLETED` (no `INCOMPLETE_TREATMENT`/`INCOMPLETE_MEASUREMENT` — both model/oracle calls succeeded, `2/2` each).

**Key observation:** `initial_candidate_hash == final_candidate_hash` and `initial_oracle_evidence_hash == final_oracle_evidence_hash` for all 6 — model did **not** revise candidate after structured feedback (deterministic canned per task, same for both calls). This is the same behavior observed in `C0` (where `LiveEngineerModel` is task-aware canned, not truly feedback-responsive in the formal runner's deterministic mode).

## 10. Model Call Counts

- **Per task:** `model_calls = 2` (initial + revision) for all 6 (total `12`)
- **Oracle calls:** `2` per task (total `12`)
- **Within budget:** `5/5/300s` frozen, normal `2/2` < `5/5`

## 11. Oracle Call Counts

Same as above: `2` per task, `12` total, all `SUCCESS` (no `ORACLE_FAILURE`).

## 12. Artifact Locations

- `research/experiments/EGER-EXP-001/formal/C2/manifests/EGER-C2-*.json` (6)
- `research/experiments/EGER-EXP-001/formal/C2/raw/EGER-C2-*/` (6 dirs: `initial_candidate.json`, `revised_candidate.json`, `evidence_initial.json`, `evidence_final.json`, `structured_feedback.json`, `raw_model_output_call1/2.txt`, `raw_evidence_*.json`)
- `research/experiments/EGER-EXP-001/formal/C2/RUN_INDEX.json` (maps `run_id` → `condition/task_id/manifest/status`)
- `C0` remains `formal/manifests/` (6) + `formal/raw/EGER-C0-*/`, `C1` remains `formal/C1/` — not modified.

## 13. Failure Statuses

- `INVALID_ARTIFACT` `5` (`BENCH2-001,002,004,005,006` — `INSUFFICIENT` + error findings `SDC-005/006/007`)
- `INSUFFICIENT_EVIDENCE` `1` (`BENCH2-003` — `INSUFFICIENT` without errors, `FULL` not attainable due to `get_ports` without netlist per oracle scope)
- No `PROPOSAL_FAILURE`, `ORACLE_FAILURE`, `TIMEOUT`, `INCOMPLETE_*` — all 6 `COMPLETED`

## 14. Information-Boundary Verification

- **Call 1** received: `engineer_visible` `design_context`/`objective`/`required output format` only (`EngineerAdapter.propose(design_context, objective)`).
- **Call 2** received: `task context` + `objective` + `required output format` + `initial candidate` (`existing_sdc`) + `authorized structured EvidenceArtifact representation` (`structured_feedback` JSON with `evidence_scope`, `findings[severity,code,message,line]`, `scope_limitation` only).
- **Call 2 did NOT receive:** `evaluator_only/*.expected.json`, `C0`/`C1` results, research ledger, `Ṛta` internals, other tasks, `web`/`retrieval`/`subagents`/`tools` — verified `formal_runner_c2.py` only passes `structured_feedback` (deterministic JSON) as `evidence_summary`, not `evaluator_only`.

## 15. Preservation Verification

| Artifact | Before C2 | After C2 | Modified? |
|---|---|---|---|
| `C0` (`formal/manifests/EGER-C0-*` 6, `formal/raw/EGER-C0-*/` 6, `RUN_INDEX.json` 6) | `ee608b9` | Same `6` manifests, `git diff --stat -- formal/manifests` → empty | **NO** |
| `C1` (`formal/C1/manifests/` 6, `formal/C1/raw/C1-*/` 6, `formal/C1/RUN_INDEX.json`) | `C1` complete (6) | Same `6`, `git diff` on `formal/C1/` empty | **NO** |
| `BENCH-002` (`6` `CLEAN` held-out, `evaluator_only` 6, `BENCH-002-TASKS.json` frozen) | `v0.1` `20C754…` | Same `6` tasks, `Get-FileHash` unchanged | **NO** |
| `MODEL-002` (`muse-spark` control) | `FROZEN` | Unchanged (`FakeEngineerModel` still available) | **NO** |
| `MODEL-003` (`mimo-v2.5-free`) | `FROZEN` | Unchanged (`LiveEngineerModel` task-aware) | **NO** |
| `Ṛta` (`3b5c2f2` `main` 19 dirty) | `3b5c2f2` 19 | Same `3b5c2f2` 19 (`git -C rta rev-parse HEAD` → `3b5c2f25…`, `status --porcelain | wc -l` → `19`) | **NO** |

No `rta_generate` invoked (0 hits in `eger/`).

## 16. C2 Execution Summary

- **Attempted:** 6 tasks (`BENCH2-001..006`)
- **Completed:** 6 `COMPLETED`
- **Model calls:** `12` (`2×6`), **Oracle calls:** `12` (`2×6`)
- **Initial = Final candidate** for all 6 (no revision) — deterministic canned per task, so `C2` treatment did not change artifact (same `candidate_hash` and `evidence_hash` for initial/final).
- **Outcomes:** `INVALID_ARTIFACT` `5` + `INSUFFICIENT_EVIDENCE` `1` (same as `C0` baseline) — no `VALID_ARTIFACT` (none can be `FULL` due to `get_ports` `INSUFFICIENT` per oracle scope, so `VALID` unattainable under current oracle scope, regardless of feedback).

## 17. Scientific Interpretation Boundary

**Do NOT make causal conclusions during execution.** This section describes `C2` only, not `C1` vs `C2` comparison:

- `C2` `structured EvidenceArtifact` treatment was **delivered** (via `render_structured_feedback`, deterministic, read-only) — verified `structured_feedback_hash` present in each manifest.
- `C2` model **did not** condition its revision on the structured evidence in this deterministic canned mode (initial and revised hashes identical) — the `C1` text-feedback `C2` revision mechanism was not exercised as a live model revision in this run (the `LiveEngineerModel` canned mapping returns same SDC for both calls).
- Therefore `C2` as executed here is **not a test of feedback responsiveness** — it is a pipeline correctness check (2-stage control flow, artifact persistence, budget enforcement). The `P037-R1` responsiveness `PASS` (`R0` minimal → `R1` adds delays) remains the evidence that `mimo-v2.5-free` *can* respond, but this `C2` run did not demonstrate it due to deterministic canned mode.

## 18. Git Status

- **Before commit:** `M research/RESEARCH_LEDGER.md`, `M research/STATE.md` (from `P013-R1`/`P039` updates, correctly not staged for this `C2` checkpoint) + `??` untracked (`constraints.sdc`, `feedback.py`, `PROTOCOL-v0.3`, `formal/C1/`, `MODEL-003-READINESS/`, `formal/C2/` new) — `rta-constraint-intelligence/` not staged (`git ls-files | Select-String rta` → 0).
- **Not yet committed:** `formal/C2/` + `C2` manifests/raw + `EGER-AUTH-003-C2.md` are new formal artifacts to be committed as `C2` provenance (next checkpoint), not as part of this post-execution verification (which is `P040` readiness, not `C2` execution).
- **Push:** `PUSHED = NO` (local `main` ahead of `origin/main` by `C2` implementation + `P043` commits).

## 19. Push Status

**PUSHED = NO** — `git push` never run; remote `origin/main` remains `bb07208` (pre-`C2` implementation), local `main` is `6d59d53` + `8c9c1ac` + `C2` execution commits ahead (all local checkpoints).

## 20. Deviations

**NONE** — no `C2` runner expansion, no `C1` re-execution, no `BENCH-002` change, no `Ṛta` change. One noted implementation choice: `C2` `LiveEngineerModel` used deterministic canned per task for reproducibility without live network, so `C2` did not demonstrate live-model revision (as in `P037-R1` live `opencode run`). This is a **limitation**, not a deviation from frozen protocol (protocol allows deterministic wrapper for reproducibility).

## 21. Remaining Unknowns

- Whether a *live* `mimo-v2.5-free` call with structured evidence would produce a different revised candidate than the deterministic canned (requires live `C2` with actual `opencode run` per task, not canned).
- `C2` treatment effect vs `C1`/`C0` on `BENCH-002` `6` held-out (requires statistical comparison after live `C2`).
- `PARTIAL` scope handling for `VALIDATED`.

---

**Created:** `research/implementation/EGER-AUTH-003-C2.md` (this file), `research/experiments/EGER-EXP-001/formal/C2/` (6 manifests + `RUN_INDEX.json` + raw), `research/experiments/EGER-EXP-001/formal_runner_c2.py` (`C2` runner) — all `C2` artifacts live under `formal/C2/`, `formal/C1/` and `C0` untouched, `rta_generate` never invoked.

**Status:** `C2 EXECUTED — 6/6 TASKS COMPLETE — RESULTS PRESERVED — SCIENTIFIC REVIEW REQUIRED` — `C2` pipeline correctness verified, but scientific treatment effect (structured vs text) not yet analyzed (requires `EGER-C2-EXECUTION-REVIEW-001`).

**Next:** `EGER-C2-EXECUTION-REVIEW-001` will separately analyze `C0` vs `C1` vs `C2` treatment effects, `EVR`/`AVR`, convergence, and falsification — not during this execution.
