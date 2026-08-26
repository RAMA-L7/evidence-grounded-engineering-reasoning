# EGER-BENCH-002 — Construction Log

| Field | Value |
|---|---|
| Benchmark | EGER-BENCH-002 v0.1 |
| Construction start | 2026-08-26, after EGER-PROMPT-001 freeze (`eger.prompt.v1`) |
| Method | Hand-authored, frozen categories per P015 §24 |
| Status | FROZEN |

## Candidate Sources Inspected

- `rta/samples/` (19 artifacts) — HIGH contamination, therefore NOT used for held-out (remains BENCH-001 development only)
- New CLEAN sources — 6 hand-authored tasks (see below)

## Generation Method

No procedural generator at v0.1; tasks hand-authored per frozen task schema:

- Task schema: `{task_id, benchmark_version, category, difficulty, provenance, construction_method, contamination_status, held_out, design_context, objective, constraints, artifact_paths, oracle_scope, evaluation_scope}`
- Categories: per P015 §25 — primary_clocks, generated_clocks, io_constraints, false_paths, multicycle_paths, adversarial_clock_on_data
- Difficulty method: objective — number of constructs/clocks, dependency depth, exception complexity (easy=1, medium=2, hard=exception/adversarial)

All tasks authored after prompt freeze — not shown to Engineer before freeze.

## Exclusions

- No task removed for difficulty
- No task selected based on model performance (0 formal runs at construction time)

## Contamination Decisions

- BENCH-001 tasks (all 19) remain development/pilot — not promoted to BENCH-002
- New BENCH2-001..006 classified CLEAN because:
  - Not Read into Engineer context before freeze
  - Not used in P012 (which used BENCH-001/004/007 from old corpus)
  - Not visible during prompt construction (prompt built before these files)
  - Expected answers placed in `evaluator_only/` (not in engineer_visible)

## Deduplication

Canonical JSON hash of each `engineer_visible` task file — all 6 distinct (prefixes above). No near-duplicates (different categories).

## Final Selection

6 tasks frozen, all `held_out=true`, all `CLEAN`, all `FULL` oracle scope for `v0.1`. Hash prefixes recorded in manifest.

## Freeze Decision

P015 Workstream B: **FROZEN** — all §38 checkboxes satisfied (construction method frozen, provenance documented, membership frozen, contamination audit CLEAN, held-out clean, hidden answers separated, categories/difficulty/adversarial documented, deduplication done, oracle coverage FULL, evaluation contract compatible, benchmark hash generated via task hashes, no formal results used, no adaptive construction).

## Limitations

Small (6 tasks) — statistical power limited; will be reported as limitation in analysis.
