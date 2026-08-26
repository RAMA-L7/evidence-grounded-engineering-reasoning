# EGER-BENCH-002 — Held-Out Benchmark

| Field | Value |
|---|---|
| ID | EGER-BENCH-002 |
| Status | **NOT FROZEN — BLOCKED** (P014 gate) |
| Date | 2026-08-26 |
| Previous | EGER-BENCH-001 v0.1 (provisional, 19 artifacts, no held-out) |
| Oracle pin | Ṛta 3b5c2f2 (v1.5.11) — same as BENCH-001 |

> This document records why a defensible held-out benchmark cannot yet be frozen. Per P014 §55, a blocked gate is preferable to artificial certainty.

---

## 1. Purpose

Provide the **formal held-out evaluation corpus** for C0–C5 — disjoint from development/pilot, adversarially meaningful, and frozen before any formal run. `BENCH-001 v0.1` is explicitly pilot/development only.

## 2. Version

`EGER-BENCH-002` — **not assigned a frozen version** (would be `v0.1` at freeze).

## 3. Source Inventory (inspected candidates)

| Source | Provenance | Accessibility | Contamination risk |
|---|---|---|---|
| `rta-constraint-intelligence/samples/` (19 artifacts at 3b5c2f2) | Shipped with oracle, pinned revision | Read-only, local | **HIGH** — all files visible to OpenCode during P002/P006/P008/P012; pilot used BENCH-001/004/007 |
| `rta-constraint-intelligence/engineer_test_kit/` (19 scenarios, shared fixtures) | Oracle repo at 3b5c2f2 | Read-only, local | **HIGH** — inspected during P002 static reconnaissance |
| `rta/tests/` and `rta/evidence/` golden fixtures | Oracle repo | Read-only, local | **HIGH** — inspected via `Glob` during P002 |
| Public SDC examples (e.g., open-source SDC corpora) | External | Would require retrieval + license check | **UNKNOWN** — not retrieved (no fabrication) |
| Independently authored tasks (new SDC problems) | Would be authored, provenance = EGER team, construction method = frozen generation procedure | Not yet authored | **CLEAN** if authored after protocol freeze and never shown to Engineer before formal run |
| Generated tasks with frozen generation procedure | Would require frozen generator (e.g., template-based SDC synthesis) | Not yet built | **CLEAN** if generation procedure frozen before formal |

No new external tasks were retrieved or authored during P014 — doing so without frozen provenance/construction method would be fabrication.

## 4. Task Inventory

**No formal held-out tasks frozen.** The 19 artifacts of `BENCH-001` remain the only inspected corpus (see `EGER-BENCH-001.md` table BENCH-001..015). All 15 SDC tasks plus `variables_v1.tcl` etc. were visible to the implementation agent (via `Glob`, `Read` during P002/P006, pilot selection), so per §31 they classify as **CONTAMINATED** or **UNKNOWN**, not **CLEAN**:

| task_id (BENCH-001) | file | visible to OpenCode? | pilot used? | contamination |
|---|---|---|---|---|
| BENCH-001 | minimal_sdc.sdc | YES (`Read`, pilot runner) | YES (P012) | **CONTAMINATED** |
| BENCH-004 | buggy_no_clocks.sdc | YES | YES (P012) | **CONTAMINATED** |
| BENCH-007 | edge_case_malformed.sdc | YES | YES (P012) | **CONTAMINATED** |
| All others | example.sdc, real_design_full.sdc, etc. | YES (`Glob`, `ls`) | NO (not in pilot) | **UNKNOWN** — visible during reconnaissance, so cannot be certified CLEAN per §32 (OpenCode inspected workspace artifacts) |

A **CLEAN** held-out set requires tasks that have **not** been visible to the Engineer/implementation agent — not satisfiable from the already-inspected sample corpus alone.

## 5. Provenance

Per task (for any future CLEAN task): `task_id`, `source`, `provenance` (URI/hash), `construction date`, `construction method` (hand-authored / template-generated / retrieved), `task category`, `input artifact refs`, `evaluation scope`. At `v0.1` BENCH-001, provenance is `Ṛta samples @ 3b5c2f2` — documented but not held-out.

## 6. Categories

Desired coverage (per P014 §23): clock definitions, generated clocks, primary clocks, clock relationships, input/output delays, clock uncertainty/latency, false paths, multicycle, max/min, I/O, incomplete/conflicting/unsupported/malformed, topology-dependent, evidence-insufficient cases. Only categories actually supported by oracle/artifacts may be claimed. Current corpus covers a subset; full coverage not yet established.

## 7. Difficulty Method

Objective: number of constructs, clocks, clock relationships, dependency depth, ambiguity, topology requirements, expected evidence scope, exception complexity. **Not** model success rate. Not yet frozen for formal set.

## 8. Adversarial Method

Scientifically meaningful challenges (plausible but incorrect constraint, evidence-absent requirement, contradictory constraints, hidden clock relationship, topology mismatch) — not arbitrary traps. No adversarial tasks constructed at P014.

## 9. Development Set

`BENCH-001 v0.1` as **development/pilot corpus** — may be used for debugging, infrastructure testing, prompt refinement *before* `BENCH-002` freeze. All its tasks are by definition development-visible.

## 10. Held-Out Set

**No held-out set frozen.** Would require explicitly excluded tasks (see §4 classification) plus new independently authored/generated tasks. Prefer a smaller clean set over a larger contaminated one (P014 §27) — hence no claim with current corpus.

## 11. Contamination Audit

For every candidate BENCH-002 task (the 19 inspected), the five §31 questions were answered per table in §4: all are `CONTAMINATED` or `UNKNOWN` (visible to OpenCode). **Only `CLEAN` tasks may enter formal held-out set** → formal set is currently empty, so `BENCH-002` cannot be frozen.

## 12. Leakage Audit

- **Implementation-time leakage:** OpenCode performed `Glob`/`Read` on `rta-constraint-intelligence/samples/` during P002, P006, P012 — all tasks were visible to the engineering agent that built L1/L2/L3/prompt.
- **Prompt construction leakage:** `EGER-PROMPT-001` `eger.prompt.v1` was built after samples were visible.
- **Human knowledge leakage:** author has seen pilot outcomes (12 runs, all `INSUFFICIENT`).
- **Unavoidable limitations:** documented here; not hidden.

## 13. Deduplication

Not yet performed on a formal set (no formal set). Method would be: hash of canonical SDC text + topology key; same netlist with trivial SDC variation flagged as near-duplicate; not removing tasks because difficult. Deferred until CLEAN tasks exist.

## 14. Oracle Coverage

Per P011 §35, each task must state whether frozen oracle can evaluate syntax/structure/topology/semantics within scope and where evaluation is limited. Current samples: oracle emits `PARTIAL`/`INSUFFICIENT`/`UNSUPPORTED` as appropriate (P006 `NETLIST_REQUIRED` → `INSUFFICIENT` per contract). Future CLEAN tasks will carry explicit `oracle_coverage` field.

## 15. Evaluation Contract

Frozen in `EGER-EXP-001 §34`: what constitutes artifact validity, what evidence is required, what is `INSUFFICIENT`/`UNSUPPORTED`/rejection/success. Not redefined here. Oracle scope `FULL` + no error findings → potential `VALIDATED`; `PARTIAL`/`INSUFFICIENT`/`UNSUPPORTED` never auto-converts to `VALIDATED`.

## 16. Known Limitations

- No held-out tasks; no adversarial set; small corpus; single-oracle favorable.
- All inspected tasks contaminated by development visibility.
- No `TCL_EXECUTION_REQUIRED` discipline beyond `UNSUPPORTED` handling.
- No benchmark hash (nothing clean to hash).

## 17. Statistical Considerations

With 15 SDC tasks from one source, statistical power for generalizable reliability claims would be insufficient — analysis would have to report limitation rather than pretend definitiveness (per protocol §20). A larger CLEAN set is needed.

## 18. Freeze Status

**NOT FROZEN — BLOCKED.**

Per §37, requires: frozen membership, IDs, provenance, contamination audit, held-out split, categories, difficulty/adversarial methods, oracle coverage, evaluation criteria, deduplication, leakage controls, version. Membership/provenance/contamination/held-out are incomplete → BLOCKED.

## 19. What Remains to Freeze BENCH-002

- Author or generate a **new** task set (or retrieve a public SDC corpus) **after** `EGER-PROMPT-001` freeze, with construction method and provenance frozen *before* any formal run.
- Keep those tasks **unseen** by the Engineer: do not `Read` them into model context, do not use them for prompt tuning, do not inspect expected outcomes.
- Freeze membership, provenance, categories, difficulty/adversarial methods, oracle coverage, held-out split, deduplication, and version `BENCH-002 v0.1`.

Until then, **P014 remains BLOCKED** on the benchmark workstream.
