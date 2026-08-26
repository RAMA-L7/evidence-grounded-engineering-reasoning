# EGER-AUTH-001 — C0 Formal Execution (LLM ONLY)

| Field | Value |
|---|---|
| ID | EGER-AUTH-001 / C0 |
| Authorization | HUMAN AUTHORIZED — formal C0 only (EGER-P013-R1 READY) |
| Experiment | EGER-EXP-001 v0.1, BENCH-002 v0.1 (6 CLEAN held-out), MODEL-002 (opencode/muse-spark-1.2 NOT_EXPOSED, temp 0.0, LiveEngineerModel task-aware) |
| Condition | C0 — LLM ONLY (no text feedback, no structured evidence, no epistemic, no routing, no authorization) |
| Tasks | BENCH2-001..006 in frozen order |
| Runs | 6 formal manifests, all COMPLETED |
| Date | 2026-08-26 |
| Status | COMPLETE (no C1–C5 executed) |

## Pre-Execution Verification

- MODEL-002 matches frozen record: opencode/muse-spark-1.2-contributor-free, NOT_EXPOSED, temp 0.0/top_p 1.0/max 2048/prompt eger.prompt.v1/timeout 60/model-calls 5
- BENCH-002 v0.1: 6 tasks BENCH2-001..006, contamination CLEAN, hashes distinct (verified Get-FileHash)
- Information boundary: Engineer sees only engineer_visible (design_context/objective) — verified 0 hits for evaluator_only in eger/engineer
- Capability audit: text/structured evidence/epistemic/routing/auth all OFF for C0 (verified pilot_runner branching, now formal_runner_c0 omits them)
- Single probabilistic component: LiveEngineerModel only (no second LLM)
- RTA before: 3b5c2f2 main 19 — after: same, no modification

## Task Execution

| Task | run_id | candidate | oracle result | failure class | artifacts |
|---|---|---|---|---|---|
| BENCH2-001 primary_clocks | EGER-C0-81390F4B | d57e79c5391a (create_clock only) | INSUFFICIENT scope + SDC-005/006 errors → INVALID_ARTIFACT | INVALID_ARTIFACT | formal/raw/EGER-C0-81390F4B/ |
| BENCH2-002 generated_clocks | EGER-C0-1DC51343 | 58eb7302 (clock + generated) | INSUFFICIENT + errors? → INVALID_ARTIFACT | INVALID_ARTIFACT | formal/raw/EGER-C0-1DC51343/ |
| BENCH2-003 io_constraints | EGER-C0-6C2482FB | 21af5d96 (clock + I/O) | INSUFFICIENT, no errors → INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | formal/raw/EGER-C0-6C2482FB/ |
| BENCH2-004 false_paths | EGER-C0-D9C5AFFE | 788310c6 (false path) | INSUFFICIENT + warnings → INVALID_ARTIFACT | INVALID_ARTIFACT | formal/raw/EGER-C0-D9C5AFFE/ |
| BENCH2-005 multicycle_paths | EGER-C0-8B6BEF1A | b942044a (multicycle) | INSUFFICIENT + errors → INVALID_ARTIFACT | INVALID_ARTIFACT | formal/raw/EGER-C0-8B6BEF1A/ |
| BENCH2-006 adversarial_clock_on_data | EGER-C0-781627F3 | fa59a938 (clock on data_bus_0) | INSUFFICIENT + SDC-007 error → INVALID_ARTIFACT | INVALID_ARTIFACT | formal/raw/EGER-C0-781627F3/ |

All 6 COMPLETED, no CAPABILITY_LEAKAGE, no PROPOSAL_FAILURE (all produced extractable SDC).

## Run Inventory

6 manifests under `research/experiments/EGER-EXP-001/formal/manifests/` + `RUN_INDEX.json` mapping run_id → condition/task_id/manifest path/status. Pilot manifests remain under `pilot/` (12, pilot=true) and are excluded.

## Raw Artifact Integrity

Per run: `raw_model_output.txt`, `candidate.json` (verified:false), `raw_evidence.json` (oracle raw_bytes), `evidence.json` (normalized scope/findings/hash). All retained, not overwritten, not deleted.

## Evidence Integrity

All 6 have `evidence_scope=INSUFFICIENT` (due to get_ports + netlist-required) — correctly not `FULL`. 5 have error findings (SDC-005/006/007 etc.) → `INVALID_ARTIFACT` evaluator classification; 1 (BENCH2-003) is `INSUFFICIENT_EVIDENCE` (complete I/O but still insufficient scope, no error). No `ORACLE_FAILURE`.

## Epistemic Assessment

C0 has no epistemic state exposed to Engineer (by design). Evaluator-side: all 6 remain `HYPOTHESIS` (no transition attempted without grounding). For formal comparison, epistemic violations = 0/0 (no attempted transitions) — EVR not applicable for C0 in this evaluator mode; will be measured for C2+ where L2 is active.

## Convergence

No run `converged` (converged requires `VALIDATED` FULL + no errors + APPROVED, which C0 cannot achieve without grounding and with INSUFFICIENT scope). All 6 `not converged`, termination `COMPLETED` within budget (1 model call, 1 oracle call each).

## Efficiency

- `model_calls`: 1 per run (6 total)
- `oracle_calls`: 1 per run (evaluator-side, 6 total)
- `routing_calls`: 0 (C0 has no routing)
- `wall_clock`: per manifest start/end, all <5s

## Aggregate Results

- **Artifact reliability:** 0/6 VALID (all INSUFFICIENT scope, so none can be VALIDATED; 5/6 INVALID due to error findings, 1/6 INSUFFICIENT without error)
- **Failure distribution:** `INVALID_ARTIFACT` 5, `INSUFFICIENT_EVIDENCE` 1
- **Epistemic:** `HYPOTHESIS` 6, no transitions, EVR N/A for C0
- **Convergence:** 0/6 converged

## Reproducibility Check

Analysis script run twice on same 6 manifests → identical aggregate (`outcomes Counter(INVALID 5, INSUFFICIENT 1)`, `epistemic HYPOTHESIS 6`, `agg_hash 6c80c4dbd1df...`). No difference.

## Human Authorization

`AUTHORIZED` via EGER-AUTH-001. No C1–C5 executed.

## Limitations

- C0 baseline reflects `LiveEngineerModel` with task-aware deterministic mapping (canned per task) at temp 0.0 — not a stochastic sample; real LLM sampling variance (temperature, top_p) would require multiple repetitions per task for statistical power (protocol allows but P013-AUTH used single run per task for this gate).
- All 6 INSUFFICIENT scope due to `get_ports` without netlist — VALIDATED unattainable under current oracle scope, so C0 `VALID` rate is 0 by construction; this is an oracle-scope artifact, not just LLM failure.

## Next

Human review of C0 required before authorizing C1. Do not proceed automatically.
