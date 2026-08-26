# EGER-P011 — Experimental Freeze Implementation Record

| Field | Value |
|---|---|
| ID | EGER-P011 |
| Title | Experimental Protocol, Benchmark, Metrics & C0–C5 Freeze |
| Date | 2026-08-26 |
| Previous gates | P008 PASS (b4dffc3, 14/14), P009 PASS (bb9025d, 31/31), P010 PASS (6ae8275, 47/47) |
| Deterministic base | L1 EGER-ORACLE-CONTRACT-001, L2/L3 EGER-EPISTEMIC-001, Engineer proposal-only (FakeEngineerModel control) |
| RTA pin | 3b5c2f2 (v1.5.11) — untouched |
| Status | PASS WITH DOCUMENTED LIMITATIONS |

## Purpose

Freeze the scientific experiment before any formal C0–C5 execution. Establish a reproducible, auditable, falsifiable protocol (EGER-EXP-001 v0.1) with independent variables (C0–C5), control variables, metrics (artifact/reasoning/epistemic, EVR/AVR, convergence, tool efficiency), failure taxonomy, run/manifest/retention discipline, anti-gaming rules, and versioning — without executing any experimental run.

## Documents Inspected

- EGER Research Contract v0.2 (canonical docx, version-controlled)
- EGER-ARCH-002, EGER-ORACLE-CONTRACT-001, EGER-SCHEMA-001, EGER-EPISTEMIC-001
- Implementation: `eger/oracle/*` (P008), `eger/epistemic/*` + `eger/authorization/*` (P009), `eger/engineer/*` (P010)
- Benchmark source: `rta-constraint-intelligence/samples/` (19 artifacts at 3b5c2f2)

## Decisions

- **Experiment version:** `EGER-EXP-001 v0.1` — immutable after P011 PASS; material change → `v0.2` + `EGER-CHANGE-###`.
- **Benchmark:** `EGER-BENCH-001 v0.1` provisional freeze: 19 artifacts under `rta/samples/` (15 SDC + 2 TCL + 1 YAML + 3 dirs), IDs BENCH-001..015, hashes implicit at pinned revision. Honest limitation: small, non-adversarial, no held-out split — formal publication freeze will be `BENCH-002`.
- **Model:** `EGER-MODEL-001` — control frozen as `FakeEngineerModel (fake/fake-engineer-v1 v1.0, deterministic)`; live provider/model/version/temperature/top-p/max-tokens/timeout *not* frozen for formal experiment — documented as PROVISIONAL, to be `MODEL-002` before any formal run. This honest non-freeze is why status is PASS WITH DOCUMENTED LIMITATIONS rather than full PASS.
- **Prompt:** `EGER-PROMPT-001` `eger.prompt.v1` — frozen neutral system prompt + task/evidence/epistemic presentation templates + deterministic extraction rules, versioned and hashed.
- **Metrics:** EVR (`violations / attempted_transitions`, via `EpistemicEngine.evr()`), AVR (`auth_violations / auth_attempts` via `AuthorizationGate`), convergence (VALIDATED+APPROVED within budget), tool efficiency — all frozen with numerator/denominator reporting, never changed after results.
- **Capability matrix:** frozen per §7 of protocol (Candidate always ✓; text feedback C1 only; structured evidence C2+; epistemic C3+; routing C4+; authorization C5 only).
- **Run protocol:** `max_iterations=5`, `max_model_calls=5`, `max_oracle_calls=5`, `max_wall_clock=300s`, `max_candidate_revisions=4`, deterministic termination; retry = technical (network/infra) only.

## Scientific Variables

- **Independent:** degree of authority-separated grounding → C0–C5 (sole treatment; agent count excluded per DEC-005).
- **Controls:** model (when frozen), prompt, task, oracle revision (3b5c2f2), schema versions, output requirements, iteration/tool/timeout budgets, evaluation criteria — only declared condition varies.
- **Confounds registered:** model randomness, task difficulty, prompt leakage, tool/info budget, oracle scope, context length, retry, task ordering, evaluator bias, infra failures — each with mitigation + residual risk in protocol §65.

## Metrics & Falsification

Falsification position documented (§3/25 of protocol): H1 not supported if C5 does not improve epistemic reliability over predecessors, EVR unchanged, improvements negligible, gains only via compute, non-reproducible, vanishing on held-out, or deterministic layers introduce more failures. Claim discipline frozen: before experiment “hypothesis/expected”, after “observed/measured/supported/not supported/inconclusive”, never “proves”.

## Unknowns Preserved

- BENCH-002 corpus for publication (size, adversarial/ambiguous split, held-out)
- MODEL-002 live selection (provider, version pinning, reproducibility limits)
- Whether `PARTIAL` scope could ever warrant `VALIDATED` with additional justification
- Cross-machine variance, statistical power with current task count

All preserved as UNKNOWN, not converted to assumptions.

## Implementation Boundary

No formal experiment executed: 0 runs under `research/experiments/` (directories/files for future runs may exist empty — none populated with results). No live model invoked for formal runs. No C0–C5 result generated, no benchmark after-results modification, no prompt after-results tuning.

## RTA  & GitHub Boundaries

- RTA: read-only, 3b5c2f2 main 19 dirty before and after (no invocation needed for docs-only P011; recorded).
- GitHub: **no push** (`git push` never run; instruction “PUSH AUTHORIZATION REQUIRED” honored).

## Change Control

Protocol frozen after P011: material change to benchmark/model/prompt/metrics/C0–C5/budgets/evaluation/falsification → new protocol version + `EGER-CHANGE-###`. Silent mutation of `v0.1` forbidden.

## Validation

All P011 §72 PASS-condition items audited: research question/hypothesis/falsification frozen; C0–C5 + C6 exclusion frozen; exactly one probabilistic component retained; prompt protocol frozen; benchmark documented as provisional v0.1 with justified limitation; dependent variables (EVR/AVR/convergence/tool efficiency) frozen; run budget/retry/failure taxonomy/anti-gaming/leakage/run-manifest/retention frozen; statistical plan documented; confound/unknown registers created; no formal experiment executed; no C0–C5 results; RTA untouched (19), contract unchanged, no GitHub push.

Status rationale: full PASS would require live MODEL-002 and a held-out BENCH-002; those are explicitly deferred, so P011 is **PASS WITH DOCUMENTED LIMITATIONS** — the strongest reproducible freeze achievable with the current engineering-validation benchmark and control model.

## Remaining UNKNOWNs

As listed above; tracked in protocol §28 and `STATE.md`.

## Deviations

NONE. No contract modification, no `rta_generate` exposure, no additional probabilistic component.

## Next Step

Authorized next: **EGER-P012 — Controlled Pilot / Dry Run** (small, explicitly pilot-labeled, no formal results) after external review of this frozen `v0.1` protocol.
