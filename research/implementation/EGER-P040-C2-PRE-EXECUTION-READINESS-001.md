# EGER-P040 — C2 Pre-Execution Readiness 001

| Field | Value |
|---|---|
| ID | EGER-P040-C2-PRE-EXECUTION-READINESS-001 |
| Date | 2026-08-27 |
| Scope | Readiness audit only — no C2 execution |
| Model | `opencode/mimo-v2.5-free` (MODEL-003) via `opencode` `LiveEngineerModel` |
| Benchmark | `EGER-BENCH-002 v0.1` (6 CLEAN held-out) |
| Status | **C2 READINESS COMPLETE — NOT READY — BLOCKING ISSUES IDENTIFIED** |

---

## 1. Executive Summary

**C2 is NOT READY for formal execution.** While `EGER-CHANGE-002` (`MODEL-003 = opencode/mimo-v2.5-free`) and `EXP-001 v0.3` are `APPROVED`/`FROZEN`, and `P037` `PASS` proves the candidate is feedback-responsive (`R0` minimal → `R1` adds `set_input_delay`/`set_output_delay`, `R2` preserved), the **C2 execution implementation is missing**: no `formal_runner_c2.py` (or equivalent) exists that implements the `C2` structured-`EvidenceArtifact` feedback loop with budget enforcement, manifest generation, and information-boundary controls. All other critical checks (`Ṛta` boundary, `rta_generate` prohibition, authority separation, benchmark preservation, `C0`/`C1` preservation) are `PASS`, but the absent runner is a **blocking** gap. No `C2` was executed.

## 2. Current Research State

- `C0 = COMPLETE` (6/6 `BENCH2-*` via `MODEL-002` `muse-spark`, `formal/manifests/EGER-C0-*` + `raw/EGER-C0-*/` + `RUN_INDEX.json`, `HYPOTHESIS` 6, `0` converged, `ee608b9`)
- `C1 = COMPLETE` (6/6 via `MODEL-002`, `formal/C1/manifests/` + `raw/C1-*/` with `initial`/`revised` candidates and `text_feedback`, treatment effect `NOT IDENTIFIABLE` per `P030` `R0==R1==R2`)
- `P037 = PASS` (`opencode/mimo-v2.5-free` `R0` minimal → `R1` adds delays, `R2` preserved, all four `R-*` satisfied)
- `MODEL-003 = opencode/mimo-v2.5-free` **formally selected** (`EGER-CHANGE-002` `APPROVED` via `P039`, `EGER-MODEL-003.md` `FROZEN`)
- `EXP-001 v0.3` (`ID v0.3`, changelog `MODEL-003` addition, preserved `v0.1`/`v0.2`) — `APPROVED`
- `BENCH-002 v0.1` `6` `CLEAN` held-out (`BENCH2-001..006`, `evaluator_only` separated, hashes distinct)
- `P040` is **readiness audit** — `C2` remains `NOT AUTHORIZED` / `NOT EXECUTED`

## 3. EGER-CHANGE-002 Verification

| Check | Result | Evidence |
|---|---|---|
| `EGER-CHANGE-002` exists | **PASS** | `research/implementation/EGER-CHANGE-002.md` exists, `Status: APPROVED — HUMAN AUTHORIZED (EGER-P039)`, `Human authorization: GRANTED — EGER-P039` |
| Scope limited to subsequent conditions | **PASS** | `Scope: Applies only to subsequent conditions requiring feedback responsiveness (initially C2)`, `Does not rewrite history: C0 on MODEL-002` |
| Not inferred from `P037` `PASS` | **PASS** | `CHANGE-002` explicitly states `P038 does not infer authorization from P037 PASS` |

## 4. EXP-001 v0.3 Verification

| Check | Result | Evidence |
|---|---|---|
| `EXP-001 v0.3` exists and is `FROZEN` | **PASS** | `research/experiments/EGER-EXP-001-PROTOCOL-v0.3.md` exists, `ID v0.3`, `Status FROZEN (P038 — MODEL-003 added, v0.2 preserved)` |
| `v0.1` preserved | **PASS** | `EGER-EXP-001-PROTOCOL.md` still `v0.1` (`ID v0.1`, `FROZEN (P011)`) — not overwritten |
| Historical `C0`/`C1` definitions preserved | **PASS** | `v0.3` is copy of `v0.1` + changelog `MODEL-003` addition only |
| `MODEL-003` addition clearly recorded | **PASS** | `Changelog v0.2 → v0.3` lists `MODEL-003 = opencode/mimo-v2.5-free` |

## 5. MODEL-003 Verification

| Check | Result | Evidence |
|---|---|---|
| `provider = opencode` | **PASS** | `EGER-MODEL-003.md` `provider: opencode` |
| `model = opencode/mimo-v2.5-free` | **PASS** | `model: opencode/mimo-v2.5-free` |
| `temperature = 0.0` | **PASS** | `temperature: 0.0` |
| `tools = []` | **PASS** | `tools: []` (no web/retrieval) |
| `prompt = eger.prompt.v1` | **PASS** | `prompt: eger.prompt.v1` |
| Model remains callable | **PASS** | `opencode run --model opencode/mimo-v2.5-free` verified `200` in `P037-R1` (`LiveEngineerModel`); no substitution |
| `MODEL-003` spec unchanged | **PASS** | `EGER-MODEL-003.md` `FROZEN` (P038), not modified since `P039` |

## 6. C2 Protocol Definition

Per `EXP-001 v0.3` (inherited from `v0.1` §6) and `P038`/`P039`:

- **Independent variable:** `structured EvidenceArtifact` (deterministic, `evidence_scope`, `findings`, `provenance`) vs `C1` text feedback vs `C0` none.
- **Control condition:** `MODEL-002` `C0` (LLM only) or `C1` text (depending on comparison); `C2` treatment is **structured evidence** (read-only, externally established via `EvidenceOracle`).
- **Treatment condition:** `C2` = `MODEL-003` + `structured EvidenceArtifact` (read-only) to revise candidate.
- **Model calls:** `max_model_calls = 5` per `EXP-001` (same across conditions)
- **Oracle calls:** `max_oracle_calls = 5` (same)
- **Feedback mechanism:** `Engineer → SDC candidate → Oracle → EvidenceArtifact → authorized text rendering?` — **No**, `C2` is **structured** `EvidenceArtifact` directly (not text). The approved renderer for `C2` is the structured `EvidenceArtifact` object, not the `EGER-C1-TEXT-FEEDBACK-CONTRACT` text.
- **Primary artifact:** `revised CandidateArtifact` (after feedback)
- **Measurement artifact:** `RunManifest` + `EvidenceArtifact`/`EpistemicTransition`/`AuthorizationDecision` + `final_outcome`
- **Comparison:** `C1` text vs `C2` structured (and `C0` vs `C2` overall)
- **Budget:** `max_iterations 5`, `model 5`, `oracle 5`, `wall 300s` — frozen
- **Information boundary:** `engineer_visible` task data + `initial candidate` + `structured EvidenceArtifact` (read-only) — no `evaluator_only`, no `C0`/`C1` results
- **Authority separation:** `MODEL=Proposal`, `ORACLE=Evidence`, `EVALUATOR=Evaluation` (no `L2`/`L3` exposed to model in `C2` per protocol — `L2`/`L3` are evaluator-side)
- **Confound controls:** single model `MODEL-003` for `C2`, same `BENCH-002` tasks, same budgets, same oracle

**Gap:** `EXP-001 v0.3` still contains the generic `C2` definition from `v0.1` (“`+ structured EvidenceArtifact`”) without an explicit `C2`-specific procedure for how the structured artifact is rendered to the model (text vs JSON, field subset). This is a **non-blocking** documentation gap, not a blocking protocol gap — the intended `C2` treatment is `structured EvidenceArtifact` (read-only) as distinct from `C1` text, and the implementation can render the structured fields deterministically.

## 7. C2 Runner Audit

| Check | Result | Evidence |
|---|---|---|
| `C2` runner exists | **FAIL — BLOCKING** | `research/experiments/EGER-EXP-001/formal_runner_c2.py` **does NOT exist** (only `formal_runner_c0.py`, `formal_runner_c1.py`, `pilot_runner.py` exist; `Get-ChildItem formal*` shows 0 `*c2*`) |
| Matches `EXP-001 v0.3` | **UNKNOWN** — no runner to compare | — |
| Model invocation path | **NOT IMPLEMENTED** for `C2` (would be `LiveEngineerModel` `mimo-v2.5-free` via `EngineerModel`) | — |
| Oracle invocation path | **NOT IMPLEMENTED** for `C2` (would be `EvidenceOracle` `Ṛta` → `EvidenceArtifact`) | — |
| Feedback path | **NOT IMPLEMENTED** | — |
| Artifact persistence | **NOT IMPLEMENTED** | — |
| Manifest generation | **NOT IMPLEMENTED** | — |
| Budget enforcement | **NOT IMPLEMENTED** | — |
| Failure handling | **NOT IMPLEMENTED** | — |
| Task iteration | **NOT IMPLEMENTED** | — |
| Deterministic config | **NOT IMPLEMENTED** | — |

**Conclusion:** `C2 RUNNER NOT IMPLEMENTED` — **blocking**.

## 8. MODEL-003 Integration Audit

| Check | Result | Evidence |
|---|---|---|
| `C2` runner can invoke `opencode/mimo-v2.5-free` via `EngineerModel` | **NOT IMPLEMENTED** — no `C2` runner, so integration not present | `eger/engineer/model.py` has `LiveEngineerModel` (`mimo-v2.5-free`, `NOT_EXPOSED` version) **and** `FakeEngineerModel` (control), but no `C2` runner wires `mimo-v2.5-free` to `BENCH-002` tasks with structured evidence |
| `tools = []` | **UNKNOWN** for `C2` (would be `[]` per `MODEL-003` spec, but no `C2` runner to verify) | — |
| Correct prompt version `eger.prompt.v1` | **UNKNOWN** | — |
| No OpenRouter/Gemini fallback | **PASS** (no `C2` runner to contain fallback, and existing `eger/` has 0 `rta_generate` hits) | `grep -r openrouter|gemini` in `eger/` = 0 (except historical `P034` docs) |

**Gap:** `MODEL-003 INTEGRATION GAP` — runner missing.

## 9. Oracle Boundary

Intended `C2` boundary (per `ORACLE-001`/`ORACLE-002`):

```
Engineer → SDC candidate → Oracle (Ṛta, deterministic, 3b5c2f2) → EvidenceArtifact → authorized structured rendering → Engineer
```

Model must **not** receive `evaluator answers`, `oracle internals`, `research canon`, `epistemic`/`authorization` state, hidden benchmark, `Ṛta` test fixtures. **No `C2` runner to verify**, but existing `L1` `EvidenceOracle` (`eger/oracle/adapter.py`) already enforces `cwd OUTSIDE Ṛta`, `PYTHONDONTWRITEBYTECODE=1`, `rta_generate` never invoked — **boundary design is intact, implementation for `C2` is absent**.

## 10. Information Boundary

Per `P013-R1` sentinel, `EngineerAdapter.build_prompt` only injects `engineer_visible` context. `C2` would add `structured EvidenceArtifact` (read-only) — still `engineer_visible` + `initial candidate` + `structured evidence` only. **No `C2` runner to verify leakage**, but `evaluator_only/*.expected.json` remains separate (verified `Select-String` 0 hits for `evaluator_only` in `eger/`).

## 11. Authority Separation

Intended: `MODEL=Proposal`, `ORACLE=Evidence`, `EVALUATOR=Evaluation` (no `L2`/`L3` exposed to model in `C2` per `EXP-001 v0.1` — `L2`/`L3` are evaluator-side). **No `C2` runner to verify**, but `C0`/`C1` runners already separate these authorities correctly (verified in `P012` pilot).

## 12. Capability Audit

Required `tools = []` (no `web`/`search`/`retrieval`/`browsing`/`subagents`/`hidden tool calls`). **No `C2` runner to verify**, but `MODEL-003` spec says `tools: []` and `P037-R1` `R0`/`R1`/`R2` used `tools: []` single `generate` calls — pattern exists.

## 13. BENCH-002 Preservation

| Check | Result | Evidence |
|---|---|---|
| Benchmark remains frozen | **PASS** | `EGER-BENCH-002.md` `v0.1` `6` `CLEAN` held-out, `FROZEN` (not modified since `0b6efa5`) |
| Task count unchanged | **PASS** | `BENCH2-001..006` (6) |
| Task identifiers unchanged | **PASS** | `BENCH2-001..006` |
| Evaluator data unchanged | **PASS** | `evaluator_only/BENCH2-*.expected.json` 6 files, not modified |
| Engineer-visible inputs unchanged | **PASS** | `tasks/engineer_visible/BENCH2-*.json` 6 files |

Verified `git diff --stat -- research/experiments/EGER-BENCH-002*` → empty (no `BENCH-002` file dirty).

## 14. C0 Preservation

`C0` artifacts = **unchanged**: `formal/RUN_INDEX.json` (6 `C0` manifests `EGER-C0-*` + `formal/C1/RUN_INDEX.json` 6 `C1` manifests), `formal/manifests/EGER-C0-*`, `formal/raw/EGER-C0-*/` (`candidate.json`/`evidence.json`/`raw_evidence.json`/`raw_model_output.txt`), `formal/MODEL-003-READINESS/R0` `PASS` artifacts — all present, no `C0` file modified (`git diff` on `formal/RUN_INDEX.json` → empty).

## 15. C1 Preservation

`C1` artifacts = **unchanged**: `formal/C1/manifests/` (6) + `formal/C1/raw/C1-*/` (initial/revised candidates, `text_feedback.txt`, `evidence_initial`/`_final`) — verified `git status` shows `formal/C1/` not dirty.

## 16. Artifact Schema

`C2` must preserve: `run ID`, `task ID`, `model identity` (`opencode/mimo-v2.5-free`), `model configuration` (`temperature 0.0`, `tools []`), `initial candidate`, `final candidate`, `treatment/control` (`C2` vs `C0`/`C1`), `oracle evidence` (`EvidenceArtifact` + `RawEvidence`), `feedback` (`structured EvidenceArtifact` rendering), `measurement` (`final_outcome`, `failure_class`), `hashes` (`candidate_hash`, `evidence_hash`), `execution status`, `failure status`, `timestamps/metadata`.

**Gap:** No `C2` schema instance to verify, but `C0`/`C1` schemas already capture these fields via `formal_runner_c0.py`/`formal_runner_c1.py` (`run_id`, `task_id`, `model_id`, `candidate_hash`, `evidence_hash`, `epistemic_*`, `authorization_*`) — pattern exists, `C2` can reuse.

## 17. Failure Semantics

`C2` must distinguish: `model call failure` (`PROPOSAL_FAILURE` timeout/provider), `oracle call failure` (`ORACLE_FAILURE` exit 3), `malformed candidate` (`MALFORMED_OUTPUT` → `PROPOSAL_FAILURE`), `timeout`/`provider failure`/`authentication failure` (infra), `partial execution` (e.g., `R1` succeeds but `R2` fails), `measurement failure` (evaluator crash). Each must be distinguishable from a successful treatment outcome (`SUCCESS` `EvidenceArtifact`). Existing `L1`/`L2` already distinguish these (`P008` `T004` `ORACLE_FAILURE` vs `INVALID_ARTIFACT`), but `C2`-specific failure handling (e.g., `model` `503` on structured evidence) is **not yet documented for `C2`** — **non-blocking** gap.

## 18. Budget Audit

Per `EXP-001 v0.3` (inherited `v0.1`): `max_iterations 5`, `max_model_calls 5`, `max_oracle_calls 5`, `timeout 60s` (`request`) / `300s` (`run`), `model-call budget 5`, `tool-call budget` (none for `C2` beyond `tools: []`). **No `C2` runner to verify enforcement**, but `C0`/`C1` runners already enforce via `model_call_limit`/`oracle_call_limit` counters.

## 19. Reproducibility

`C2` must record: exact `model identifier` (`opencode/mimo-v2.5-free`), `provider` (`opencode`), `configuration` (`temperature 0.0`, `max_tokens 2048`, `tools []`, `prompt_version eger.prompt.v1`), `task identifier` (`BENCH2-*`), `relevant execution metadata` (`prompt_hash`, `output_hash`, `candidate_hash`, `evidence_hash`, `timestamps`). `C0`/`C1` already record these; `C2` can reuse same manifest schema.

## 20. Existing Test Coverage

| Test suite | Count | Result | Covers `C2` runner? |
|---|---|---|---|
| `tests/test_evidence_oracle.py` | 14 | `PASS` | No — covers `L1` only |
| `tests/test_epistemic_authorization.py` | 17 | `PASS` | No — covers `L2`/`L3` |
| `tests/test_llm_proposal.py` | 16 | `PASS` | No — covers proposal layer, `R0`/`R1`/`R2` via `FakeEngineerModel` |
| **Total** | **47** | `47 passed` | **No** — `C2` runner, `MODEL-003` integration, artifact persistence, budget enforcement, information boundary for `C2`have **no** dedicated tests |

**Gap:** `C2` runner, `MODEL-003` integration, `C2` artifact persistence, `C2` budget enforcement, `C2` information boundary — **no coverage**.

## 21. Repository Safety

`C2` output **must** live in `research/experiments/EGER-EXP-001/formal/` (or `formal/C2/`), not in `pilot/`, not in `rta/`, not in `formal/C1/`. `C2` must not modify `C0`/`C1`/`BENCH-002`/`MODEL-002`/`Ṛta`/`evaluator-only`/`frozen protocol`. No `C2` output exists yet, so safety is `PASS` by vacuity, but **would-be files** are clearly designated.

## 22. Blocking Issues

1. **C2 RUNNER NOT IMPLEMENTED** — blocking, per §6/7.
2. **MODEL-003 INTEGRATION GAP** — blocking (same root cause).
3. **No C2-specific tests** — blocking ( §19).

## 23. Non-Blocking Issues

- `C2` structured `EvidenceArtifact` rendering to `Engineer` (text vs JSON field subset) not explicitly documented in `EXP-001 v0.3` — non-blocking, can be `deterministic text rendering` of `evidence_scope`/`findings` as in `P037-R1`.
- `Gemini` `404` (`gemini-2.5-flash` no longer available) deviation already documented in `P037-R1` — not a `C2` `opencode/mimo-v2.5-free` issue.

## 24. GO/NO-GO Decision

**C2 READINESS COMPLETE — NOT READY — BLOCKING ISSUES IDENTIFIED**

Despite all frozen prerequisites (`MODEL-003` `FROZEN`, `EXP-001 v0.3` `FROZEN`, `BENCH-002` `FROZEN`, `C0`/`C1` preserved, `Ṛta` untouched, `rta_generate` never invoked, no `C2` executed), the **execution implementation is absent**. This is not a scientific `FAIL` — it is a readiness `NOT READY` that correctly prevents formal `C2` execution.

## 25. Required Next Step

Implement the **minimal `C2` runner** that:

- Takes one `BENCH2-*` `engineer_visible` task
- Calls `LiveEngineerModel` `opencode/mimo-v2.5-free` (`temperature 0.0`, `tools: []`, `eger.prompt.v1`) for the initial candidate (`R0`-like)
- Calls `EvidenceOracle` (`Ṛta` `3b5c2f2`) → `EvidenceArtifact` (structured)
- Renders `EvidenceArtifact` deterministically as **structured** feedback (read-only, not `C1` text) and calls `LiveEngineerModel` again for the revised candidate
- Persists `initial`/`final` candidates, `EvidenceArtifact`/`RawEvidence`, `RunManifest` under `formal/C2/` (or `formal/` with `condition: C2`), enforces budgets, handles `PROPOSAL_FAILURE`/`ORACLE_FAILURE` distinctly, and respects `pilot=false formal=true` separation.

Do **not** execute `C2` after implementing the runner — implementation alone is the next gate; execution requires a separate human `C2` authorization (see `P013`).

---

**Do not confuse this readiness audit with `C2` execution:** No `C2` task was executed, no `C2` outcome data generated, no `C2` experimental results exist. `C2` remains `NOT AUTHORIZED` / `NOT EXECUTED`.

**Ṛta:** `HEAD 3b5c2f25c48d6b6b1d4809f0d5d69fc467d387ea` (`3b5c2f2`) `main` 19 dirty — unchanged; no `rta_generate`.

**Git:** No `C2` runner to stage; `C0`/`C1`/`BENCH-002` not modified; `git status` shows `formal/C1/` (already committed) and `formal/MODEL-003-READINESS/R0` (from `P037-R1` `gemini-3.6-flash`/`mimo-v2.5-free` `R0` runs) — none are `C2`.

**Human researcher will review `P040` before authorizing `C2`.**

**Stop after `P040`.**
