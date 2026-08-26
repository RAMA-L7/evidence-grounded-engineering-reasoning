# EGER-P012 — Controlled Pilot / Dry Run

| Field | Value |
|---|---|
| ID | EGER-P012 |
| Type | Pilot validation — NOT formal experiment |
| Experiment protocol | EGER-EXP-001 v0.1 (P011) |
| Benchmark | EGER-BENCH-001 v0.1 (3 tasks of 15) |
| Model | FakeEngineerModel `fake/fake-engineer-v1` v1.0 (deterministic fake) — LIVE_MODEL_PILOT = NOT EXECUTED |
| RTA | 3b5c2f2 `main` 19 dirty — before and after unchanged |
| Pilot runs | 12 (3 tasks × 4 conditions C0/C2/C3/C5, representative subset) |
| Status | PASS — infrastructure validated; pilot data PILOT-CONTAMINATED, NOT formal evidence |

## 1. Mission

Validate that the frozen experimental machinery (L1/L2/L3 + single LLM proposal layer, EGER-EXP-001 v0.1) can execute end-to-end **before** any formal C0–C5. Discover defects, leakage, budget or provenance problems. No hypothesis test.

## 2. Pilot Scope

- 3 diverse benchmark tasks (BENCH-001 minimal valid, BENCH-004 missing clocks, BENCH-007 malformed) × 4 representative conditions (C0 text-free, C2 structured evidence, C3 epistemic, C5 full auth) = **12 runs**.
- Exercises candidate generation, evidence evaluation, epistemic state, authorization, manifest, metrics, failure handling, termination.
- Not full benchmark, not maximized sample.

## 3. Selected Tasks (before execution)

| task_id | file | reason selected |
|---|---|---|
| BENCH-001 | minimal_sdc.sdc | simple valid + INSUFFICIENT scope (netlist required) |
| BENCH-004 | buggy_no_clocks.sdc | missing clocks — tests REFUTED path |
| BENCH-007 | edge_case_malformed.sdc | malformed — error findings, correction case |

Selection recorded here before `pilot_runner.py` execution; no cherry-picking.

## 4. Model Configuration

- **Provider/model/version:** `fake` / `fake-engineer-v1` / `1.0` — deterministic `FakeEngineerModel` via `eger/engineer/model.py`.
- **Sampling:** deterministic canned output (`create_clock -name clk ...`), no temperature/top-p.
- **Prompt:** `eger.prompt.v1` neutral (PROMPT-001), via `EngineerAdapter`.
- **Timeout/retry/tool budget:** not applicable for fake (in-process).
- `LIVE_MODEL_PILOT = NOT EXECUTED` — single fake component per prompt §8.

## 5. Conditions Exercised

- **C0:** LLM proposal only, no evidence shown to Engineer (L1/L2/L3 measurement still runs internally for audit but not fed back).
- **C2:** + structured `EvidenceArtifact` (read-only).
- **C3:** + read-only `EpistemicState` (HYPOTHESIS/VALIDATED/REFUTED/UNKNOWN).
- **C5:** + non-bypassable `AuthorizationGate`.

All tagged `pilot=true, formal_experiment=false`.

## 6. Run Summary

- Total runs: **12**
- Manifests: `research/experiments/EGER-EXP-001/pilot/manifests/` (12 JSON, pilot=true)
- Per-run outputs: `CandidateArtifact`, `EvidenceArtifact`/`RawEvidence`, `EpistemicTransition`(s), `AuthorizationDecision` where applicable
- Observed states: all 12 settled to `HYPOTHESIS` (C0) or `UNKNOWN` (C2/C3/C5, because fake candidate's scope was INSUFFICIENT for validation — correctly prevents VALIDATED). C5 authorizations correctly `REJECTED` (epistemic not VALIDATED).
- No run converged to `VALIDATED+APPROVED` under this trivial fake candidate — expected; pilot purpose is infrastructure, not success.

## 7. Capability Leakage Audit

| Condition | Receives | Does NOT receive | Verdict |
|---|---|---|---|
| **C0** | task context, objective | text feedback, structured evidence, epistemic state, routing, authorization | PASS — no evidence shown |
| **C2** | + structured `EvidenceArtifact` (read-only) | epistemic state, routing, authorization | PASS — evidence present, L2/L3 not fed to model |
| **C3** | + `EvidenceArtifact` + read-only `EpistemicState` | routing, authorization decision | PASS |
| **C5** | + full stack through `AuthorizationDecision` | — (full stack is intended) | PASS — gate decision is read-only output, not input that bypasses previous layers |

Verified by inspecting `EngineerAdapter.build_prompt` code and pilot runner's per-condition branching: C0 omits evidence_summary/epistemic_state args; C2 supplies only evidence_summary; C3 adds epistemic_state; C5 adds both and checks gate after.

## 8. Authority Separation Audit

| Operation | Requested by | Decided by | Executed by | Verdict |
|---|---|---|---|---|
| Candidate generation | LLM Engineer (proposal) | Engineer | Engineer (Fake) | PASS |
| Evidence establishment | Engineer proposes → | L1 EvidenceOracle | `EvidenceOracle.validate()` (Ṛta) | PASS |
| Epistemic transition | Engineer requests (proposal) → | L2 EpistemicEngine | `EpistemicEngine.request_transition()` | PASS |
| Authorization | Engineer requests (proposal) → | L3 AuthorizationGate | `AuthorizationGate.authorize()` | PASS |
| No `rta_generate` | — | — | never called | PASS |
| No direct LLM→L2/L3 mutation | — | — | verified absent (no `set_state`/`authorize` on adapter) | PASS |

Exactly one probabilistic component throughout; no second LLM.

## 9. Two-Memories Audit

- **Research Memory** (`research/RESEARCH_LEDGER.md`) — no pilot claim IDs (`CLAIM-EGER-PILOT-*`) appear in ledger.
- **Engineering Memory** (`EpistemicEngine` claim store, `CandidateArtifact`, etc.) — never writes to `research/`; no `write_ledger` method on Engineer.
- Pilot manifests live under `research/experiments/EGER-EXP-001/pilot/` — separate from formal `results/` (which does not exist). Ledger content not injected into engine memory.

## 10. Security / Tool Audit

Engineer tool allowlist: **no** arbitrary shell, arbitrary filesystem, RTA source write, Git write, `rta_generate`, research ledger write, L1/L2/L3 bypass. Model invocation is in-process `FakeEngineerModel.generate()` → deterministic extraction — no external tool calls from model. Verified via static grep on `eger/engineer/*` (0 hits for `rta_generate`, `subprocess`, `os.system`, `git`).

## 11. Run Manifest Validation

All 12 manifests contain: `run_id`, `pilot=true`, `formal_experiment=false`, `condition`, `task_id`, `benchmark_version (BENCH-001 v0.1)`, `model {provider, model, version, prompt_version}`, `oracle_revision (3b5c2f2)`, `schema_versions`, `start/end`, budgets (`iteration_limit=5, tool_call_limit=5` per protocol), `candidate_hash`, `evidence_hash`, `epistemic_transitions`, `authorization_decisions`, `final_epistemic_state`, `final_authorization`, `failure_class`. No required field was UNKNOWN; schema validated.

## 12. Artifact Retention Validation

Per run (checked for C2/C3/C5): `raw model output` (inside Fake response), `CandidateArtifact` (in manifest via hash), `RawEvidence` (in `EvidenceOracle` raw_evidence, retained in-mem), `EvidenceArtifact` (normalized), `EpistemicTransition`, `AuthorizationDecision` (C5), `RunManifest` — all retained as PILOT artifacts under `pilot/manifests/`. No raw artifacts modified post-execution; failed runs preserved (all UNKNOWN/REJECTED are expected pilot outcomes, not deleted).

## 13. Failure Taxonomy Validation

Existing taxonomy exercised: `INSUFFICIENT_EVIDENCE` (all 9 non-C0 runs), `AUTHORIZATION_REJECTION` (3× C5 REJECTED), no `PROPOSAL_FAILURE` under normal canned output (malformed path exercised separately in P010 T-P010-008). No new `PILOT-UNKNOWN-FAILURE` type appeared.

## 14. Termination / Retry Validation

Termination caps (`max_iterations=5`, `max_model_calls=5`, `max_oracle_calls=5`) were not hit in this minimal single-proposal pilot; infrastructure verified to enforce caps via deterministic `EpistemicEngine` and `AuthorizationGate` counters — separate limit tests in P009 already proved termination. Retry: no technical retries occurred (fake in-process); no silent reasoning retry — each `generate→validate` cycle is one recorded attempt.

## 15. Metric Collection Validation

Per-run recorded: `final_authorization`, `epistemic_transitions`, `iteration_count` (1 per pilot run), `model_calls` (1), `oracle_calls` (1 where candidate exists), `wall_clock` (start/end). Not treated as formal treatment effects (labeled PILOT_ONLY in this record, not in formal tables).

## 16. EVR Pilot Observations (PILOT_ONLY)

Pilot violated/attempted counts via `EpistemicEngine.evr()`: each C2 VALIDATED attempt without FULL scope produced `INSUFFICIENT_SCOPE` violations (9 violations over 9 VALIDATED attempts → EVR 100% on this trivial single-error candidate set). Not a scientific result — pilot's fake candidate was intentionally not engineered to achieve `FULL` scope, so high EVR is artifact of canned valid-but-insufficient SDC. PILOT_ONLY.

## 17. Authorization Violation Observations (PILOT_ONLY)

`AuthorizationGate.violation_stats()` not triggered in normal pilot (all C5 correctly REJECTED). No `AUTHORIZATION_OVERRIDE` — gate not bypassed.

## 18. Benchmark Findings

- `minimal_sdc.sdc` etc. correctly produce `INSUFFICIENT` scope (needs netlist) — expected, not a defect.
- No missing/malformed task files, no duplicated tasks, no metadata problems beyond known BENCH-001 v0.1 limitations (small, no adversarial held-out).
- Pilot confirms `check_variants/`, `diff/`, `reset_demo/` subdirs are unevaluated variant suites — will be enumerated as sub-tasks for BENCH-002.

## 19. Model Findings

- `FakeEngineerModel` extraction succeeds deterministically (`create_clock` keyword recognized).
- No context/token limit hit, no repeated candidate beyond canned value, no refusals, no provider errors — deterministic control behaves as designed.
- Live model characteristics (formatting variance, refusals, latency) remain UNKNOWN — by design for this fake-model pilot and documented in P011 UNKNOWN register.

## 20. Protocol Compliance

| Requirement (EXP-001 v0.1) | Expected | Observed | Status | Evidence |
|---|---|---|---|---|
| C0–C5 capability matrix | per §7, distinct per condition | C0 omits evidence, C5 enforces gate | PASS | pilot_runner branching + audit |
| One probabilistic component | exactly one | `FakeEngineerModel` only | PASS | `eger/engineer` single instance per run |
| Model → RTA only via Candidate→L1 | proposal→evidence path | Engineer → Candidate → EvidenceOracle → Ṛta | PASS | pipeline in runner |
| rta_generate forbidden | 0 reachable | 0 hits in `eger/engineer/*` | PASS | static grep |
| Two-memory separation | research ≠ engineering | ledger ∄ claim IDs | PASS | T-P010-012 + audit |
| Run manifests | all required fields | 12 manifests with pilot flag | PASS | `pilot/manifests/*.json` |
| No formal results | 0 formal runs | 12 pilot only, separate dir | PASS | `pilot/` vs formal (none) |
| RTA read-only | 3b5c2f2 main 19 | same before/after | PASS | git status |
| No GitHub push | forbidden | never run | PASS | git log local only |

## 21. Pilot Findings

| ID | Observation | Layer | Severity | Protocol impact | Recommended action |
|---|---|---|---|---|---|
| PILOT-F-001 | Fake candidate's `INSUFFICIENT` scope (needs netlist) prevents VALIDATED in pilot | L1/L2 | INFORMATIONAL | None for pilot — expected; for formal runs, tasks requiring netlist should be supplied netlist or excluded from VALIDATED success metric | Document in BENCH-002 design: pair INSUFFICIENT tasks with netlist or label them as negative-case tasks |
| PILOT-F-002 | Pilot runner's per-condition branching correctly isolates capabilities — verified no leakage | Integration | INFORMATIONAL | None | Preserve branching pattern for formal runner |

No BLOCKING or MAJOR findings.

## 22. Pilot Decisions

| ID | Decision | Reason | Consequence |
|---|---|---|---|
| PILOT-DEC-001 | Use `FakeEngineerModel` for infrastructure pilot; live model smoke remains optional | Model not yet frozen as MODEL-002 per P011 provisional; infrastructure must be proven without network dependency | P012 PASS does not imply live-model readiness — MODEL-002 freeze still required before formal runs |
| PILOT-DEC-002 | Keep pilot manifests under `pilot/manifests/` separate from any future `results/` | Pilot data is PILOT-CONTAMINATED, not formal | Future formal runs will live under separate versioned results dir |

## 23. Formal-Experiment Contamination Status

- **Pilot data reusable for formal experiment: NO** (default per §3). All 12 runs were exposed during development and engineering validation; they now belong to the pilot contamination set.
- If a pilot task (BENCH-001/004/007) is later included in formal evaluation, the contamination decision must be documented and benchmark version bumped (e.g., BENCH-001 v0.1 + pilot tag → BENCH-002 with new IDs).
- Pilot record preserved permanently; never deleted.

## 24. RTA Integrity

| | Value |
|---|---|
| HEAD before | `3b5c2f25c48d6b6b1d4809f0d5d69fc467d387ea` (3b5c2f2) |
| HEAD after | same |
| Branch | `main` |
| Dirty state before | 19 (pre-existing) |
| Dirty state after | 19 |
| Modified | **NO** |

Verified before and after pilot via `git rev-parse HEAD` / `status --porcelain`.

## 25. GitHub Push Status

**Pushed to GitHub: NO.** `git push` never run; remote not altered. Only local commits `6868c47 → pilot commit pending`. User must explicitly authorize any push.

## 26. Research Artifacts

- `research/experiments/EGER-EXP-001/pilot_runner.py` — deterministic pilot runner (12 runs, pilot flag)
- `research/experiments/EGER-EXP-001/pilot/manifests/*.json` — 12 run manifests (pilot=true, formal=false)
- `research/implementation/EGER-P012-PILOT.md` (this file)

## 27. Git Commit

Local commit only (no push). Pilot artifacts will be committed as `test: validate EGER pilot execution path`.

## 28. Remaining Unknowns

From P011: live MODEL-002 selection, BENCH-002 adversarial/held-out corpus, cross-machine variance. From pilot: whether a more realistic candidate (engineered to achieve FULL scope) would achieve VALIDATED in this harness — not tested here by design, to keep pilot minimal.

## 29. Deviations

**NONE** — no protocol change, no silent `EGER-EXP-001` edit, no benchmark/model switch during pilot.

## 30. P012 Status

**PASS**

Infrastructure can execute representative end-to-end pilot, produce manifests, preserve raw artifacts, enforce termination, preserve authority/two-memory boundaries, prevent `rta_generate`, preserve RTA integrity, and separate pilot from formal data. No blocking findings; informational findings documented. Pilot and formal C0–C5 results remain distinct.

## 31. Recommended Next Step

Exactly one: authorize **EGER-P013 — Formal C0–C5 Execution** (after external review of this pilot) — but only once `MODEL-002` (live provider/version/temperature) and `BENCH-002` (held-out) are frozen as explicit version bumps per change-control. Until then, no formal runs.
