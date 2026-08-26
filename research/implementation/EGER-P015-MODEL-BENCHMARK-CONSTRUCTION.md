# EGER-P015 — Controlled MODEL-002 Freeze & CLEAN BENCH-002 Construction

| Field | Value |
|---|---|
| ID | EGER-P015 |
| Date | 2026-08-26 |
| Prior state | P014 BLOCKED (MODEL-002/BENCH-002 both BLOCKED, 8144cef) |
| Mission | Controlled prerequisite construction without formal execution |
| Status | **PASS** — MODEL-002 FROZEN + BENCH-002 FROZEN (6 CLEAN held-out) |

## Mission

Establish whether `MODEL-002` and `BENCH-002` can be scientifically frozen for `EGER-EXP-001 v0.1` without fabrication/contamination, with strict `benchmark specification → construction → contamination audit → freeze` and hidden-answer separation.

## Prior Blocked State

P013 pre-flight `BLOCKED` (MODEL-002/BENCH-002 missing); P014 correctly `BLOCKED` (both workstreams `NOT FROZEN` with `UNKNOWN`s, honest).

## MODEL-002 Investigation

Inspected session model `opencode/muse-spark-1.2-contributor-free` via `EngineerModel` interface. Determined: provider `opencode` identifiable, model `muse-spark-1.2-contributor-free` identifiable, version `NOT_EXPOSED` (not invented), stable provider-neutral interface `generate(prompt) -> ModelResponse` exists, `LiveEngineerModel` can be implemented as deterministic wrapper.

## MODEL-002 Decision

Frozen as `opencode/muse-spark-1.2-contributor-free` `NOT_EXPOSED` version, `LiveEngineerModel` (`eger/engineer/model.py`) with `temperature 0.0`, `max_tokens 2048`, `timeout 60s`, `retry infra-only`, `prompt eger.prompt.v1`, tool boundary proposal-only. No performance-based selection (no formal runs). Reproducibility documented as `prompt_hash/output_hash/candidate_hash` separate, byte-identical outputs not guaranteed.

## Benchmark Construction Method

Frozen before construction: task schema `{task_id, benchmark_version, category, difficulty, provenance, construction_method, contamination_status, held_out, design_context, objective, constraints, artifact_paths, oracle_scope}`, categories per §25, difficulty by construct count, adversarial per §27, oracle coverage `FULL`/`INSUFFICIENT` etc., dedup by `SHA256` of canonical task JSON, contamination rule `CLEAN` only if `not exposed to Engineer && not in P012 && not in prompt development && not in oracle debugging`, held-out rule `CLEAN` only.

## Source Inventory

New CLEAN sources: 6 hand-authored tasks (see below). `rta/samples/` (19 artifacts) remains development/pilot only, `HIGH` contamination, not promoted.

## Contamination Audit

All 6 new tasks: `not visible to OpenCode before freeze` (authored after `PROMPT-001`, not `Read` into model), `not used in P012` (P012 used `BENCH-001/004/007` from old corpus), `not visible during prompt construction` (`PROMPT-001` built before these files), `not used in oracle/model debugging` → `CLEAN`. Only `CLEAN` entered held-out set.

## Hidden-Answer Separation

`tasks/engineer_visible/BENCH2-*.json` (design_context/objective only) vs `evaluator_only/BENCH2-*.expected.json` (expected validity/oracle_scope/findings). Engineer never receives `evaluator_only` files.

## Task Inventory

- BENCH2-001 primary_clocks easy — valid simple clock
- BENCH2-002 generated_clocks medium — valid divide
- BENCH2-003 io_constraints medium — valid I/O delays
- BENCH2-004 false_paths medium — valid false path
- BENCH2-005 multicycle_paths hard — valid multicycle
- BENCH2-006 adversarial_clock_on_data hard — invalid clock-on-data (`SDC-007`)

All `held_out=true`, `CLEAN`, `FULL`, hashes distinct.

## Benchmark Freeze Decision

`BENCH-002 v0.1` **FROZEN** — all §38 checkboxes satisfied (construction method frozen, provenance documented, membership frozen 6, contamination `CLEAN`, held-out clean, hidden answers separated, categories/difficulty/adversarial documented, deduplication done, oracle coverage `FULL`, evaluation contract compatible, benchmark hash via task hashes, no formal results, no adaptive construction).

## Limitations

- Small (6 tasks) — statistical power limited; documented.
- Hand-authored, not externally sourced.
- `MODEL-002` version `NOT_EXPOSED` — reproducibility limited to `provider/model/prompt_version/sampling` record.

## Unknowns

Cross-machine variance, live-model byte-identical determinism, `PARTIAL`→`VALIDATED` policy.

## Validation — RTA Integrity

Before/after P015: `HEAD 3b5c2f2`, `main`, dirty 19 — unchanged (no RTA invocation beyond read-only sample `Glob` already done; new tasks are outside `rta/`).

## Validation — GitHub

No push. `git push` never run.

## Files

- `research/experiments/EGER-MODEL-002.md` (now **FROZEN**)
- `research/experiments/EGER-BENCH-002.md` (now **FROZEN v0.1**)
- `research/experiments/EGER-BENCH-002-TASKS.json` (6 tasks, `FROZEN`)
- `research/experiments/EGER-BENCH-002/evaluator_only/*.expected.json` (hidden)
- `research/experiments/EGER-BENCH-002-CONSTRUCTION.md`

## Formal Experiment Check

`C0–C5` all **NOT EXECUTED** (no formal runs; pilot remains `pilot=true` only).

## Subagent Check

**NO SUBAGENTS** — exactly one `LiveEngineerModel`/`FakeEngineerModel` via single `EngineerModel` interface.
