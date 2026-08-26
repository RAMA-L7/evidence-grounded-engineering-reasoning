# EGER Research STATE

Last updated: 2026-08-26 (EGER-GITHUB-001 GitHub release)

| Item | Status |
|---|---|
| Current contract | EGER Research Contract v0.2 (canonical docx; now version-controlled @ baseline `6be2314`; formal freeze acceptance still to be confirmed — see Open Questions) |
| Current phase | **Phase 1 — C0 COMPLETE (6/6 tasks, LLM ONLY, 47+6 formal manifests) — awaiting human authorization for C1.** |
| Research memory | **VERSION-CONTROLLED** (baseline commit `6be2314`, branch `main`) |
| Git | **INITIALIZED** at `D:\Research on EGER` (EGER_ROOT); Ṛta excluded via `.gitignore`; pushed to `origin/main` (`cd826fc`) |
| Research baseline | **ESTABLISHED** (`6be23141785dce7c4a6b8bce0f390bad99b13c87`, 2026-08-26) |
| Current architecture | **EGER-ARCH-002** (recommended; pending formal implementation authorization) |
| Primary experiment | **C0 COMPLETE (6/6, LLM ONLY), C1–C5 NOT EXECUTED** — controlled ablation, frozen `EXP-001 v0.1` |
| Engineering extension | C6 specialized subagents — deferred until after C0–C5 evaluation (still deferred) |
| Oracle | External deterministic Ṛta v1.5.11 (`rta-constraint-intelligence`), **runtime characterization complete** (EGER-ORACLE-002); CLI/MCP byte-determinism & scope live at runtime verified; adapter **IMPLEMENTED (P008)** |
| Oracle runtime evidence | Raw outputs at `research/oracle/runtime/` (untracked pending retention policy) |
| Implementation status | **L1/L2/L3 + LLM proposal layer (47/47) + C0 formal (6/6, LLM ONLY) IMPLEMENTED**; C1–C5/C6 not yet |
| Subagent status | Not implemented — single Engineer only (fake), C6 deferred |
| Experiment status | **C0 COMPLETE (6/6 held-out, formal, LLM ONLY)** — C1–C5 NOT EXECUTED (await human auth per condition) |
| Benchmark status | **BENCH-002 v0.1 FROZEN** (6 CLEAN held-out, evaluator_only separated, formal C0 used BENCH2-001..006) + BENCH-001 provisional |
| Model status | **MODEL-002 FROZEN** (`opencode/muse-spark-1.2-contributor-free` `NOT_EXPOSED`, LiveEngineerModel task-aware, temp 0.0) — used identically for all 6 C0 tasks |
| Prompt status | **PROMPT-001 frozen** (`eger.prompt.v1` neutral, versioned, hashed) |
| Research ledger | Established by EGER-P004; version-controlled since P005; P006–P014 recorded |
| Pilot (P012) | **PASS** — 12 pilot runs (3 tasks × 4 conditions), pilot=true, 0 formal results, 2 informational findings |
| Model freeze | **MODEL-001 control FROZEN, MODEL-002 FROZEN** (`opencode/muse-spark-1.2-contributor-free`, `LiveEngineerModel`, `NOT_EXPOSED` version, temp 0.0, max 2048, timeout 60s) |
| Benchmark freeze | **BENCH-001 v0.1 provisional + BENCH-002 v0.1 FROZEN** (6 CLEAN held-out tasks, separated evaluator_only, hashes 20C754… ) |
| P014 gate | **BLOCKED — was MODEL-002 BLOCKED + BENCH-002 BLOCKED → P014 BLOCKED** (historical, see ledger) |
| P015 gate | **PASS — MODEL-002 FROZEN + BENCH-002 FROZEN** (6 CLEAN tasks, LiveEngineerModel, no performance-based selection) |
| Git / version control | INITIALIZED (EGER_ROOT, branch `main`, baseline `6be2314`); Ṛta explicitly excluded; **PUSHED to GitHub** (`origin/main` `cd826fc`) |
| EvidenceOracle contract | **EGER-ORACLE-CONTRACT-001** FROZEN/PROVISIONAL per matrix (see §20 of contract doc) — **IMPLEMENTED** |
| Typed artifact schemas | **EGER-SCHEMA-001** FROZEN v1 family (`eger.candidate.v1`/`raw.v1`/`evidence.v1`) — **IMPLEMENTED** |
| EvidenceOracle adapter | **IMPLEMENTED — PASS (14/14 tests)** (`eger/oracle/adapter.py`, `eger/oracle/schemas.py`; tests `tests/test_evidence_oracle.py`) |
| Adapter tests | PASS (14/14); RTA integrity verified (3b5c2f2 main 19 unchanged) |
| Epistemic state (L2) | **IMPLEMENTED — PASS (17/17 tests)** (`eger/epistemic/state.py`, `eger/epistemic/transitions.py`; deterministic engine, immutable baseline, EVR raw counts) |
| Authorization (L3) | **IMPLEMENTED — PASS (17/17 tests)** (`eger/authorization/gate.py`; hard gate VALIDATED+FULL+SUCCESS) |
| L2/L3 schemas | **EGER-EPISTEMIC-001** FROZEN (`eger.epistemic.v1`, `eger.transition.v1`, `eger.authorization.*`) — EGER-SCHEMA-001 unchanged |
| L2/L3 tests | PASS (17/17) + regression 14/14 = 31/31 overall; RTA 3b5c2f2 main 19 unchanged; EvidenceOracle not modified |
| LLM proposal layer | **IMPLEMENTED — PASS (16/16 tests)** (`eger/engineer/*`; `FakeEngineerModel` + `EngineerAdapter` + `CandidateArtifact`; `tests/test_llm_proposal.py`); 47/47 total |
| LLM tests | PASS (16/16) + full regression 31/31 = 47/47 overall; RTA 3b5c2f2 main 19 unchanged; deterministic layers not modified |
| Violation metrics | `EpistemicEngine.evr()` + `AuthorizationGate.violation_stats()` PROVISIONAL — machine-readable |
| Provenance / determinism | Hash trio (input/raw/evidence/candidate) + timestamp-as-provenance FROZEN and implemented; deterministic file path `eger_oracle_<hash>/candidate.sdc`; transitions + extraction deterministic |

## Two memories — explicit separation

- RESEARCH MEMORY: version-controlled in `research/` (ledger, state, implementation records).
- ENGINEERING EPISTEMIC MEMORY: deterministic engine (`eger/epistemic`, `eger/authorization`) + single LLM Engineer proposals — proposal authority only, verified separate (T-P010-012).

## Accepted decisions

| ID | Decision | Status |
|---|---|---|
| EGER-DEC-005 | C0–C5 uses exactly one probabilistic component; Evidence/State/Authorization are deterministic layers | ACCEPTED as architecture recommendation (pending implementation review) |
| EGER-DEC-006 | `rta_generate` forbidden to all EGER components | ACCEPTED |
| EGER-DEC-007 | C4 routing is deterministic (frozen table); LLM-controlled routing rejected | ACCEPTED |

## Superseded decisions / artifacts

| ID | Content | Superseded by | Note |
|---|---|---|---|
| EGER-ARCH-001 | Three-LLM-role topology (supervisor/proposer/analyst) + 3 deterministic layers | EGER-ARCH-002 for C0–C5 | Preserved at [`architecture/EGER-ARCH-001.md`](architecture/EGER-ARCH-001.md). Deterministic-layer core survives unchanged. |
| EGER-DEC-001…004 (P001-era) | Determinize-everything axiom; adapter boundary; per-condition configs; Critic deferral | Partially absorbed into ARCH-002 | Original full records exist only in chat transcript (P001 response); canonical detail unavailable — recorded as historical references in LEDGER. |

## Open questions

1. Formal confirmation that contract v0.2 is accepted/frozen.
2. Ṛta pinned-commit hygiene: P002 observed a dirty working tree; confirm inspected bytes == intended baseline before any series.
3. Runtime verification — **core unknowns now RESOLVED** (CLI formats, byte determinism, trust scope, exit 0/1, MCP handshake per ORACLE-002); remaining: exit codes 2/3 paths, finding-identity emission contexts, netlist-aware mode, baseline/gate E2E, large-design perf.
4. Benchmark corpus selection and freezing.
5. Model/sampling-parameter freeze policy per condition sweep.
6. Claim-registration enforcement mechanism (reject vs flag unstructured claims) — affects future EVR denominator.
7. Adapter transport: subprocess-first chosen; revisit MCP at C6.
8. ~~Runtime artifact retention policy for `research/oracle/runtime/` outputs (evidence vs temp).~~ RESOLVED: `research/oracle/runtime/` added to `.gitignore` as runtime scratch (EGER-GIT-001).

## Known risks

- Ṛta actively developed → version drift; pin commit+version per series.
- Single-LLM design carries self-evaluation bias (validator finality mitigates; C6 can quantify).
- All research history prior to P004 lives only in chat transcripts (backfilled now with retrospective IDs; marked as such).
- Windows path/locale fragility around non-ASCII "Ṛta" characters in tooling.
- **Evaluator-only benchmark answers now public** (EGER-GITHUB-001) — BENCH-002 integrity compromised for public use; requires remediation decision.

## GitHub Release (EGER-GITHUB-001)

- **Repository:** https://github.com/RAMA-L7/evidence-grounded-engineering-reasoning
- **Visibility:** PUBLIC
- **Remote:** origin → https://github.com/RAMA-L7/evidence-grounded-engineering-reasoning.git
- **Commits pushed:** All 13 commits on main (6be2314 through cd826fc)
- **Remote HEAD:** cd826fc (matches local)
- **⚠️ CRITICAL: Evaluator-only benchmark answers (6 files) exposed to public repository** (see EGER-GITHUB-001 §6)
- **Remediation required:** Make repo private, filter history, or accept exposure — requires separate explicit authorization
- **Secret scan:** No secrets found
- **Ṛta boundary:** INTACT (3b5c2f2 main 19 unchanged, 0 paths in git ls-files)

## Next authorized step

C0 **COMPLETE** (6/6 tasks, 5 INVALID_ARTIFACT + 1 INSUFFICIENT, 0 converged). GitHub **PUSHED** (`cd826fc`). **Evaluator-only exposure requires remediation decision.** Next research activity: EGER-C0-REVIEW-001 (separate step). Do not proceed automatically.

## C0 Verification (EGER-AUTH-001)

- Model: MODEL-002 live `opencode/muse-spark-1.2` task-aware, temp 0.0, `eger.prompt.v1`, budget 5 — identical for all 6 tasks
- Benchmark: BENCH-002 v0.1 6 CLEAN held-out in frozen order BENCH2-001..006, engineer_visible only, no model performance-based selection
- Only one probabilistic component (LiveEngineerModel) — no second LLM/subagent
- Information boundary: C0 prompt contains only design_context/objective, no text/structured evidence/epistemic/routing/auth (verified before each run, no CAPABILITY_LEAKAGE)
- Task isolation: fresh run context per task (no previous output leakage)
- Raw artifacts: 6 manifests + 6 raw dirs (raw_model_output, candidate.json, raw_evidence.json, evidence.json) + RUN_INDEX.json under `formal/`, pilot remains `pilot/` excluded
- RTA: 3b5c2f2 main 19 before/after — no modification, `rta_generate` NOT INVOKED
- Reproducibility: analysis run twice → identical aggregate (`INVALID 5, INSUFFICIENT 1`, `HYPOTHESIS` 6)
- Formal/pilot separation: `pilot=false formal=true` vs pilot `pilot=true`; no mixing
- Next: **human review of C0 before C1**

## Pre-Flight Verification (P013-R1)

- 25-check gate: all PASS or PASS WITH LIMITATION, 0 FAIL on a critical item
- MODEL-002: `opencode/muse-spark-1.2-contributor-free` `NOT_EXPOSED` version, `LiveEngineerModel` exists, sampling/context/budgets frozen
- BENCH-002: 6 CLEAN held-out tasks (BENCH2-001..006), hashes distinct, no formal-run mutation, contamination=CLEAN
- Information boundary: **PASS** — Engineer has no file-read, `evaluator_only` 0 hits in `eger/`, sentinel test (`_SENTINEL.txt`) verified not exposed and removed
- Evaluator separation: **PASS** — no wildcard loading, `evaluator_only` only consumed by evaluator
- RTA: 3b5c2f2 main 19 — unchanged; `rta_generate` 0 hits
- No C6, no GitHub push, **C0–C5 = NOT EXECUTED** (PRE-FLIGHT ONLY)
- **FINAL GATE: READY FOR HUMAN AUTHORIZATION**

## P015 Verification

- MODEL-002: `opencode/muse-spark-1.2-contributor-free`, `NOT_EXPOSED` version, `LiveEngineerModel` implemented, sampling/context/budgets frozen, infrastructure test NON-FORMAL PASS
- BENCH-002: 6 CLEAN held-out tasks (BENCH2-001..006), hand-authored after PROMPT-001, contamination=CLEAN, hidden answers separated (`engineer_visible` vs `evaluator_only`), hashes distinct, oracle_scope FULL
- RTA: 3b5c2f2 main 19 — unchanged (no RTA invocation needed for construction, read-only samples only for BENCH-001)
- No formal C0–C5 executed, no C6, no GitHub push, exactly one probabilistic component preserved

## Pilot Verification (P012)

- RTA before: 3b5c2f2 main 19 — after: 3b5c2f2 main 19 (no mutation, L1 invocation only via pilot runner)
- 12 pilot manifests: pilot=true formal=false, experiment_version EXP-001 v0.1, BENCH-001 v0.1, MODEL-001, oracle 3b5c2f2
- Capability leakage: PASS (C0 omits evidence, C5 enforces gate)
- Authorities: PASS (single LLM, L1/L2/L3 separate, no rta_generate, no direct LLM→L2/L3)
- Two memories: PASS (ledger ∄ claim IDs)
- No C6, no GitHub push, no formal results (0 C0–C5 formal runs)
- Findings: 2 informational (INSUFFICIENT prevents VALIDATED — expected), 0 blocking

## Implementation Records

- `research/implementation/EGER-P008-ADAPTER.md`
- `research/implementation/EGER-P009-EPISTEMIC-AUTHORIZATION.md`
- `research/implementation/EGER-P010-LLM-PROPOSAL.md`
- `research/implementation/EGER-P011-EXPERIMENT-FREEZE.md`
- `research/implementation/EGER-P012-PILOT.md`
- `research/implementation/EGER-P014-MODEL-BENCHMARK-FREEZE.md` (historical BLOCKED)
- `research/implementation/EGER-P015-MODEL-BENCHMARK-CONSTRUCTION.md` (FROZEN)
- `research/implementation/EGER-P013-R1-PREFLIGHT.md` (READY, 25-check gate)
- `research/schemas/EGER-EPISTEMIC-SCHEMAS.md`
- `research/schemas/EGER-ARTIFACT-SCHEMAS.md` (unchanged)
- `research/experiments/EGER-EXP-001-PROTOCOL.md`
- `research/experiments/EGER-BENCH-001.md`
- `research/experiments/EGER-MODEL-001.md`
- `research/experiments/EGER-PROMPT-001.md`
- `research/experiments/EGER-MODEL-002.md` (**FROZEN**, `opencode/muse-spark-1.2`, `LiveEngineerModel`)
- `research/experiments/EGER-BENCH-002.md` (**FROZEN v0.1**, 6 CLEAN)
- `research/experiments/EGER-BENCH-002-TASKS.json` (**FROZEN**, 6 tasks, held_out 6)
- `research/experiments/EGER-BENCH-002-CONSTRUCTION.md`
- `research/experiments/EGER-BENCH-002/tasks/engineer_visible/` (6)
- `research/experiments/EGER-BENCH-002/evaluator_only/` (6 hidden)
- `research/implementation/EGER-AUTH-001-C0.md` (C0 formal, 6 tasks)
- `research/implementation/EGER-GIT-001.md` (C0 provenance checkpoint)
- `research/implementation/EGER-GITHUB-001.md` (GitHub release — evaluator-only exposure)
- `research/experiments/EGER-EXP-001/formal/` (6 manifests + RUN_INDEX + raw artifacts, formal=true)

## Verification (P011)

- RTA before: 3b5c2f2 main 19 dirty — after: 3b5c2f2 main 19 (no mutation, no runtime invocation needed)
- EvidenceOracle/L2/L3/Engineer: not modified; 47/47 still PASS (no experiment execution — 0 C0–C5 runs)
- Protocol: EXP-001 v0.1 frozen (30 sections) + BENCH-001 v0.1 provisional + MODEL-001 control frozen + PROMPT-001 frozen
- No GitHub push (never run)
- P011: PASS WITH DOCUMENTED LIMITATIONS (live MODEL-002 + BENCH-002 deferred — honest, not hidden)

## Verification (P010, preserved)

- RTA 3b5c2f2 main 19 — unchanged
- L1/L2/L3/Engineer 47/47 PASS; no C0–C5/C6, no rta_generate
- Two memories verified separate (T-P010-012)
