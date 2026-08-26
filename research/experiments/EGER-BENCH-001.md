# EGER-BENCH-001 — Benchmark v0.1

| Field | Value |
|---|---|
| ID | EGER-BENCH-001 v0.1 |
| Status | **PROVISIONAL FREEZE** (P011 gate) |
| Date | 2026-08-26 |
| Oracle pin | Ṛta 3b5c2f2 (v1.5.11) |
| Source | `rta-constraint-intelligence/samples/` — 19 artifacts at this revision |

## Purpose

Provide an initial, reproducible engineering-task corpus for dry-runs and for establishing the protocol's measurability. **Not** the final publication evaluation set — too small and insufficiently adversarial (see Known Limitations).

## Inclusion Criteria

- File is an SDC (or TCL) artifact shipped with the characterized oracle revision
- Deterministically validatable by `EvidenceOracle.validate()` under the frozen adapter
- Covers at least one constraint category (clocks, I/O, exceptions) where oracle can emit scope/findings

## Exclusion Criteria

- Non-text assets, HTML reports, generated artifacts, or build products
- Tasks requiring netlist-aware validation beyond the characterized `NETLIST_REQUIRED` scope (deferred until netlist mode is exercised)

## Task IDs (frozen at v0.1)

| task_id | file | provenance | notes |
|---|---|---|---|
| BENCH-001 | `minimal_sdc.sdc` | Ṛta samples @ 3b5c2f2 | minimal clocks + I/O — P006 EVID-003/006, INSUFFICIENT scope example |
| BENCH-002 | `example.sdc` | @ 3b5c2f2 | general example |
| BENCH-003 | `real_design_full.sdc` | @ 3b5c2f2 | larger realistic design |
| BENCH-004 | `buggy_no_clocks.sdc` | @ 3b5c2f2 | missing clocks — tests missing-clock detection |
| BENCH-005 | `clock_relations.sdc` | @ 3b5c2f2 | clock relations |
| BENCH-006 | `edge_case_empty.sdc` | @ 3b5c2f2 | empty edge case |
| BENCH-007 | `edge_case_malformed.sdc` | @ 3b5c2f2 | malformed — P006 EVID-004, error findings |
| BENCH-008 | `edge_case_extreme_values.sdc` | @ 3b5c2f2 | extreme values |
| BENCH-009 | `warning_heavy.sdc` | @ 3b5c2f2 | warning-heavy |
| BENCH-010 | `constraint_diff_v1.sdc` | @ 3b5c2f2 | diff baseline v1 |
| BENCH-011 | `constraint_diff_v2.sdc` | @ 3b5c2f2 | diff revision v2 |
| BENCH-012 | `external_feedback_regression.sdc` | @ 3b5c2f2 | regression shape |
| BENCH-013 | `multi_corner_template.sdc` | @ 3b5c2f2 | corner template |
| BENCH-014 | `test_custom_rules.yaml` | @ 3b5c2f2 | custom rule example (not used as SDC task) |
| BENCH-015 | `variables_v1.tcl` | @ 3b5c2f2 | TCL variables v1 |
| + dirs | `check_variants/`, `diff/`, `reset_demo/` | @ 3b5c2f2 | variant/diff/reset suites (sub-tasks enumerated in future manifest) |

Each task's hash is implicitly the file content hash at the pinned revision — changing the file or revision → new benchmark version.

## Evaluation Method

Per-task: `CandidateArtifact.sdc_text` (proposed SDC for the task's design context) → `EvidenceOracle.validate()` → `EvidenceArtifact` (findings/scope) → evaluator maps oracle findings to artifact reliability (deterministic, no model self-evaluation). No ground-truth answer is supplied to the Engineer.

## Expected Evidence Requirements

- Tasks with `get_ports`/`get_cells` references → `INSUFFICIENT` without netlist (proving insufficient → VALIDATED is a violation)
- Tasks with missing clocks → error findings → `REFUTED` path
- Well-formed tasks with `FULL` scope and no errors → potential `VALIDATED`

## Leakage Controls

Benchmark answers (oracle JSON for these files) are **never** included in Engineer prompts. Only the task's design context and engineering objective are supplied.

## Development / Test Separation

No held-out split frozen at v0.1. All 13 SDC tasks above have been visible during engineering (P006/P008 validation). **Documented as limitation**: formal evaluation will require a held-out split or fresh BENCH-002 generation where prompt development tasks are explicitly disjoint from evaluation tasks. No formal C0–C5 results will be claimed against this provisional set as publication evidence.

## Input Artifacts

Each task's input artifact is the SDC/TCL file itself at the pinned revision; no external design netlists are included at v0.1 (hence `NETLIST_REQUIRED` tasks remain INSUFFICIENT by design).

## Freeze Status

**BENCH-001 v0.1 = PROVISIONALLY FROZEN** at P011 (file list + provenance frozen, hashes reproducible). Formal publication freeze to a larger, adversarial, held-out **BENCH-002** before any C0–C5 results are claimed as generalizable.

## Known Limitations

- Small (15 SDC tasks + variants), narrow coverage, no adversarial “plausibly-wrong” synthesis challenges.
- No incomplete-specification or ambiguous-situation tasks beyond empty/malformed edges.
- No unsupported-construct suite beyond what samples contain.
- All tasks from one oracle's own samples — favorable to that oracle.
- No held-out evaluation split yet.

## Versioning

`BENCH-001 v0.1` is immutable. Adding/removing a task or changing a file → `v0.2` + `EGER-CHANGE-###`.
