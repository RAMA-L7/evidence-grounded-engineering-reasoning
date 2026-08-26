# EGER-BENCH-002 — Held-Out Benchmark

| Field | Value |
|---|---|
| ID | EGER-BENCH-002 v0.1 |
| Status | **FROZEN** (P015 construction gate) |
| Date | 2026-08-26 |
| Previous | EGER-BENCH-001 v0.1 (development/pilot, contaminated) |
| Oracle pin | Ṛta 3b5c2f2 (v1.5.11) — same |
| Tasks | 6 held-out tasks, CLEAN |

> New CLEAN tasks authored **after** `PROMPT-001` freeze (`eger.prompt.v1`) and never shown to Engineer before formal run (hidden answers separated).

---

## 1. Purpose

Provide the formal held-out evaluation corpus for `C0–C5` — disjoint from development/pilot, adversarially meaningful, frozen before any formal run.

## 2. Version

`EGER-BENCH-002 v0.1` — immutable at this commit. Changing member, content, or evaluator expectation → `v0.2` + `EGER-CHANGE-###`.

## 3. Source Inventory

| Source | Provenance | Accessibility | Contamination risk at freeze |
|---|---|---|---|
| New hand-authored tasks (6) — `EGER-BENCH-002/tasks/` | EGER hand-authored 2026-08-26, after `PROMPT-001` freeze, `construction_method: hand-authored` per frozen construction protocol | Local `research/experiments/EGER-BENCH-002/` (engineer_visible + evaluator_only separation) | **CLEAN** — never shown to Engineer; Engineer-visible files contain only design_context/objective, not expected answers |
| `rta-constraint-intelligence/samples/` (previous 19) | Pinned `3b5c2f2` | Read-only, local | **CONTAMINATED / development** — visible during `P002`/`P012` |

No external retrieval for `v0.1`; all `BENCH-002` tasks are independently authored.

## 4. Task Inventory (frozen)

| task_id | file (engineer_visible) | category | difficulty | contamination | held_out | oracle_scope |
|---|---|---|---|---|---|---|
| BENCH2-001 | `tasks/engineer_visible/BENCH2-001.json` | primary_clocks | easy | CLEAN | true | FULL |
| BENCH2-002 | `tasks/engineer_visible/BENCH2-002.json` | generated_clocks | medium | CLEAN | true | FULL |
| BENCH2-003 | `tasks/engineer_visible/BENCH2-003.json` | io_constraints | medium | CLEAN | true | FULL |
| BENCH2-004 | `tasks/engineer_visible/BENCH2-004.json` | false_paths | medium | CLEAN | true | FULL |
| BENCH2-005 | `tasks/engineer_visible/BENCH2-005.json` | multicycle_paths | hard | CLEAN | true | FULL |
| BENCH2-006 | `tasks/engineer_visible/BENCH2-006.json` | adversarial_clock_on_data | hard | CLEAN | true | FULL |

All 6 `held_out = true`.

## 5. Provenance

Per task: `task_id`, `source = EGER hand-authored`, `provenance = "EGER hand-authored 2026-08-26, after PROMPT-001 freeze, never shown to Engineer"`, `construction_method = hand-authored`, `category`, `artifact_paths` (engineer_visible path only), `oracle_scope = FULL`. Engineer-visible manifests never contain expected answers.

## 6. Categories

Covered: primary clocks, generated clocks (divide), I/O delays, false paths, multicycle paths, adversarial clock-on-data (`SDC-007`). Evaluator claims only these categories are represented.

## 7. Difficulty Method

Objective: number of constructs (`1–2`), clocks (`1–2`), clock relationships, dependency depth, exception complexity. `easy = 1 construct, medium = 2 constructs, hard = exception/adversarial`. Not by model success rate.

## 8. Adversarial Method

`BENCH2-006`: plausible but incorrect — `create_clock` on `data_bus_0` is syntactically valid but semantically wrong; correct answer must **not** create clock on data port. Oracle should emit `SDC-007`. Rationale documented in task `provenance` and `evaluator_only/BENCH2-006.expected.json`.

## 9. Development Set

`BENCH-001 v0.1` (19 artifacts) — may be used for debugging/infrastructure before `BENCH-002` freeze; already frozen as development corpus.

## 10. Held-Out Set

The 6 tasks above — **unseen** by Engineer until formal execution. Engineer-visible directory contains only `design_context`/`objective`/`constraints`; evaluator-only directory `evaluator_only/BENCH2-*.expected.json` contains `expected_artifact_validity`/`expected_findings` and is **not** in Engineer-visible manifest.

## 11. Contamination Audit

| task_id | visible to OpenCode before freeze? | used in P012? | visible during prompt construction? | classification |
|---|---|---|---|---|
| BENCH2-001..006 | **NO** — authored after `PROMPT-001` freeze, files not `Read` into model context before freeze, `git status` shows untracked until now | NO | NO (`PROMPT-001` was `eger.prompt.v1` built before these files) | **CLEAN** |

Only `CLEAN` tasks entered held-out set — satisfied.

## 12. Leakage Audit

- **Implementation-time leakage:** New tasks authored in `P015` after prompt freeze; not `Read` during `P002`/`P006`/`P012` (those used `BENCH-001` samples). Construction agent (this session) is not the formal Engineer that will execute `C0–C5` — same workspace but files were not fed to Engineer.
- **Prompt leakage:** `eger.prompt.v1` built before these tasks; no task content in prompt.
- **Unavoidable limitation:** Same workspace stores both research and benchmark — mitigated by explicit `engineer_visible` vs `evaluator_only` directory separation and by not feeding evaluator-only files to Engineer. Documented.

## 13. Deduplication

Method: `SHA256` of canonical `engineer_visible` JSON (sorted keys, `engineer_visible` content only). All 6 hashes are distinct (prefixes `20C754…`, `FF5848…`, `CB0C16…`, `CAF76E…`, `D69D81…`, `F79D64…` — verified). No near-duplicates; no removal for difficulty.

## 14. Oracle Coverage

All 6 tasks: `oracle_scope = FULL` (within `FULL` scope where `PARTIAL`/`INSUFFICIENT` would be a violation to convert to `VALIDATED`). Oracle can evaluate syntax/structure/semantics within scope; evidence sufficiency is the task's challenge (e.g., `BENCH2-006` expects `SDC-007` detection).

## 15. Evaluation Contract

Frozen in `EGER-EXP-001 §34`: `FULL` + no error findings → potential `VALIDATED`; `PARTIAL`/`INSUFFICIENT`/`UNSUPPORTED` never auto-`VALIDATED`; evaluator maps oracle findings (`SDC-007` for `BENCH2-006`, missing `set_input_delay` etc.) to artifact validity. Not redefined.

## 16. Known Limitations

- Small (6 tasks) — statistical power limited; analysis must report limitation rather than pretend definitiveness.
- Hand-authored, not externally sourced — provenance is EGER, not independent corpus.
- No `TCL_EXECUTION_REQUIRED` discipline beyond `UNSUPPORTED` handling.
- No netlist-aware `NETLIST_REQUIRED` tasks in this `v0.1` (all `FULL`).

## 17. Statistical Considerations

With 6 held-out tasks, strong statistical inference is limited — analysis will report per-condition aggregates, paired comparisons, and limitation rather than `p < 0.05` gates.

## 18. Freeze Status

**FROZEN** — all §38 checkboxes satisfied: construction method frozen (hand-authored, after `PROMPT-001`), provenance documented, membership frozen (6), contamination audit `CLEAN`, held-out clean, hidden answers separated (`engineer_visible` vs `evaluator_only`), categories/difficulty/adversarial documented, deduplication done, oracle coverage `FULL`, evaluation contract compatible, `benchmark_hash` generated (see §19), no formal results used, no adaptive construction.

## 19. Benchmark Identity / Hash

- **Task manifest hash:** `SHA256(canonical JSON of sorted task hashes)` — computed from `EGER-BENCH-002-TASKS.json` (`tasks` array sorted by `task_id`).
- **Benchmark version:** `EGER-BENCH-002 v0.1`
- **Source inventory hash:** hash of `BENCH-002.md` at this commit.
- **Generator hash:** `N/A` (hand-authored, not procedural generator; no `benchmark_generator/` at `v0.1`).

Formal runs will record `benchmark_version = EGER-BENCH-002 v0.1` and `benchmark_hash` from manifest.

## 20. What Remains

Formal `C0–C5` execution still requires `MODEL-002` live freeze (separate workstream) and `P013` re-entry. `BENCH-002` alone does not authorize formal runs.
