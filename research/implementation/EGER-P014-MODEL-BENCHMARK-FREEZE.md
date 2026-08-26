# EGER-P014 — Model & Benchmark Freeze Gate

| Field | Value |
|---|---|
| ID | EGER-P014 |
| Date | 2026-08-26 |
| Pre-flight | P013 BLOCKED — MODEL-002 and BENCH-002 missing (required per EGER-EXP-001) |
| Previous gates | P008 PASS, P009 PASS, P010 PASS, P011 PASS WITH DOCUMENTED LIMITATIONS (MODEL-002/BENCH-002 provisional), P012 PASS (12 pilot runs), P013 BLOCKED |
| Contracts | EGER-ORACLE-CONTRACT-001, EGER-SCHEMA-001, EGER-EPISTEMIC-001, EGER-EXP-001 v0.1 (all frozen, not modified) |
| Status | **BLOCKED** — honest pre-formal freeze gate, not a failure of prior work |

## Purpose

Establish whether `MODEL-002` (exact live provider/model/version/configuration) and `BENCH-002` (held-out formal benchmark) can be **scientifically frozen** for `EGER-EXP-001 v0.1` before any formal C0–C5. Per P014 §55, a blocked gate is preferable to artificial certainty.

## P013 Blocked-State Review

P013 pre-flight correctly found `MODEL-002` (`provider/model/version/sampling/context/timeout/retry`) and `BENCH-002` (`held-out tasks, frozen membership`) absent. P014's job was to determine if they *can* now be frozen without fabrication or contamination.

## Model Selection Criteria (frozen per protocol)

Permitted: availability, reproducibility, stable interface, documented identity, context/output capacity, structured-output feasibility, tool/API compatibility, cost, rate-limit, operational reliability, ability to execute `EngineerModel.generate()` interface. Forbidden: “best preliminary EGER result” or comparative performance experiments.

## Model Candidates / Availability

- **Session runtime:** `opencode / muse-spark-1.2-contributor-free` (this agent, `opencode/muse-spark-1.2-contributor-free`, 2026-08-26, win32). Interface is research-agent orchestration, not a stable experimental provider endpoint with version pin.
- **EngineerModel interface:** `eger/engineer/model.py` — provider-neutral, replaceable. Currently only `FakeEngineerModel` (`fake/fake-engineer-v1` v1.0, deterministic, in-process) is implemented and proven (47/47).
- **No live provider** has been selected by non-performance criteria and configured as `LiveEngineerModel` with endpoint/auth. No `LiveEngineerModel` adapter exists.

Only one suitable model (`FakeEngineerModel`) is available for infrastructure; no live model is defensibly selectable now without fabrication.

## MODEL-002 Configuration

See `research/experiments/EGER-MODEL-002.md` — all 19 required sections populated, most fields `UNKNOWN` / `NOT_EXPOSED` / `NOT FROZEN`. Attempting to invent values would violate §1.

## Model Selection Rationale

No live model selected — therefore no rationale beyond: selection must be by non-performance criteria **before** any formal outcome is observed (P014 §1). Selecting now on pilot `INSUFFICIENT` artifacts would violate integrity.

## Model Reproducibility

- `FakeEngineerModel`: fully deterministic.
- Live: not frozen, so reproducibility (temperature 0 byte-identity, seed, version pin) cannot be documented for a live provider yet.

## Model Infrastructure Test

**NOT EXECUTED** (correct, per P014 §15). A non-formal `model_infrastructure_test` would require a live endpoint; none selected → `model_infrastructure_test = not executed, formal_experiment = false`. No performance comparison performed.

## Benchmark Construction Method

Inspected legitimate sources (P014 §21): `rta/samples/` (19 artifacts), `engineer_test_kit/`, `rta/tests/`, public SDC corpora (not retrieved), independently authored tasks (not yet authored), generated tasks with frozen generation procedure (not yet built). For each source, provenance/access/license/contamination risk recorded in `EGER-BENCH-002.md` §3.

## BENCH-002 Source Inventory

See `EGER-BENCH-002.md` §3/4; inspected corpus is exactly the 19 `BENCH-001 v0.1` artifacts already visible to OpenCode via `Glob`/`Read` during P002/P006/P012. New adversarial/public/generated sources not retrieved/authored (would be fabrication without frozen provenance).

## BENCH-002 Task Inventory

**No formal held-out tasks frozen.** See `EGER-BENCH-002-TASKS.json` — `tasks: []`, `held_out: []`, status `BLOCKED`, with per-task contamination table:

- `BENCH-001`/`004`/`007` → `CONTAMINATED` (pilot used + Read)
- All others → `UNKNOWN` (visible via `Glob`/`ls` during P002 static reconnaissance, cannot be certified `CLEAN` per P014 §32 — OpenCode already inspected workspace artifacts)

Only `CLEAN` tasks may enter held-out set → formal set currently empty.

## Task Categories / Difficulty / Adversarial

Desired categories (§23), difficulty criteria (§24), adversarial types (§26) documented as **methodology**, not as frozen assignments (no tasks to assign). Valid/invalid/insufficient/unsupported/ambiguous mix intended but not instantiated.

## Development / Held-Out Split

`BENCH-001 v0.1` = **development/pilot corpus** (may be used for debugging/infrastructure, never for formal evaluation). Held-out set = **empty** — prefer a smaller clean set over a larger contaminated one (P014 §27). No formal C0–C5 result claimed against pilot set.

## Contamination Audit

Per §31, every candidate task classified `CONTAMINATED` or `UNKNOWN` (see §4 table in `EGER-BENCH-002.md`). **Only `CLEAN` tasks may enter formal held-out set** → none qualify now.

## Leakage Audit

- **Implementation-time leakage:** OpenCode performed `Glob`/`Read` on `rta/samples/` during P002, P006, P012 — all inspected tasks visible to the agent that built L1/L2/L3/prompt.
- **Prompt leakage:** `eger.prompt.v1` built after samples visible.
- **P012 leakage:** 12 pilot manifests used BENCH-001/004/007.
- **Unavoidable limitations:** documented, not hidden.

## Deduplication

Not yet performed on a formal set (no formal set). Method frozen: hash of canonical SDC text + topology key; not removing tasks because difficult.

## Oracle Coverage

Per §35, each future task will state whether frozen oracle can evaluate syntax/structure/topology/semantics within scope (`FULL`/`PARTIAL`/`INSUFFICIENT`/`UNSUPPORTED`). Current `BENCH-001` tasks: oracle emits `INSUFFICIENT` for `get_ports` cases (P006 `NETLIST_REQUIRED` → `INSUFFICIENT`) — correctly not auto-converted to `VALIDATED`.

## Evaluation Contract

Frozen in `EGER-EXP-001 §34` — artifact validity, evidence requirements, `INSUFFICIENT`/`UNSUPPORTED`/rejection/success definitions. Not redefined.

## Benchmark Identity / Hash

No clean benchmark to hash; `benchmark_hash: null` in `EGER-BENCH-002-TASKS.json`. Formal hash will be of frozen manifest at freeze time.

## Model–Benchmark Independence Audit

- Model selection did not depend on formal benchmark outcomes (no formal runs).
- Benchmark selection did not depend on model outcomes (no runs).
- Neither was selected by running C0–C5. Preliminary pilot/infrastructure checks (`FakeEngineerModel` determinism, pilot `INSUFFICIENT` artifacts) were compatibility checks only, not performance optimization — documented.

## Scientific Integrity Check

Honest `BLOCKED` is the integrity-preserving outcome. Forcing a freeze with contaminated tasks or an unpinned model would produce an unfalsifiable experiment.

## Formal Experiment Execution Check

| Condition | Executed |
|---|---|
| C0 | **NOT EXECUTED** |
| C1 | **NOT EXECUTED** |
| C2 | **NOT EXECUTED** |
| C3 | **NOT EXECUTED** |
| C4 | **NOT EXECUTED** |
| C5 | **NOT EXECUTED** |

**ALL = NOT EXECUTED** — no formal result, no treatment comparison, no hypothesis conclusion.

## Subagent Check

**NO SUBAGENTS** — zero `supervisor`/`critic`/`planner`/`reviewer` agents created; exactly one `FakeEngineerModel` per test (as in P010); `C6` remains deferred engineering extension.

## RTA Integrity

| | Value |
|---|---|
| HEAD before | `3b5c2f25c48d6b6b1d4809f0d5d69fc467d387ea` (`3b5c2f2`) |
| HEAD after | same |
| Branch | `main` |
| Dirty before | 19 (pre-existing, since P002) |
| Dirty after | 19 |
| Modified | **NO** — P014 performed no RTA invocation (read-only `Glob`/`Read` on samples only, already done); `rta_generate` never invoked |

## GitHub Push Check

**Pushed to GitHub: NO.** `git push` never run; remote not altered. Only local commits (`6868c47` for P011, `c3327ca` for P012 pilot).

## Files Created / Inventory

- `research/experiments/EGER-MODEL-002.md` (19 sections, status `NOT FROZEN — BLOCKED`)
- `research/experiments/EGER-BENCH-002.md` (18 sections, status `NOT FROZEN — BLOCKED`)
- `research/experiments/EGER-BENCH-002-TASKS.json` (`tasks: [], held_out: [], BLOCKED` with contamination audit)
- `research/implementation/EGER-P014-MODEL-BENCHMARK-FREEZE.md` (this file)

No `MODEL-002` live adapter code created (would require provider selection); no new benchmark SDC files created.

## Model–Benchmark Config Notes

Model and benchmark workstreams kept independent: neither was selected to make the other look good, and neither was tuned by running C0–C5.

## Status

**BLOCKED** — Both workstreams blocked, as designed for a pre-formal freeze gate that refuses artificial certainty. Both `MODEL-002` and `BENCH-002` are `NOT FROZEN` with documented `UNKNOWN`s; per §54, `MODEL-002 = BLOCKED` + `BENCH-002 = BLOCKED` → `P014 = BLOCKED`. This is **preferable** to a contaminated experiment.

## Deviations

**NONE** — no `EGER-CHANGE-###`, no silent protocol edit, no formal execution.

## Unknowns

Live provider/version pinning, completed `LiveEngineerModel` adapter, `rta_generate` generation procedure for tasks, held-out corpus provenance after future authoring, cross-machine variance.

## Next Step

Re-enter preparation: **explicitly freeze `MODEL-002` (live provider) and author a new CLEAN held-out `BENCH-002` corpus after prompt freeze without showing it to the Engineer** — then re-enter **P013 pre-flight** for a second gate pass. Until both are `FROZEN`, do not execute any formal C0–C5.
