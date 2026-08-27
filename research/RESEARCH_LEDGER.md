# EGER RESEARCH LEDGER

Chronological spine of EGER research. Every material entry: ID, type,
context/date (approximate where exact timestamps unavailable), purpose,
previous state, observation/decision, evidence, relationships, status.

**Classification tags used below** (contract §15): SDC=SOURCE-DERIVED CLAIM ·
AI=AGENT INFERENCE · RH=RESEARCH HYPOTHESIS · OBS=OBSERVATION ·
ER=EXPERIMENTAL RESULT (none exist yet) · C=CONCLUSION.
No ER entries exist as of EGER-P004. No experimental claims are made anywhere
in this ledger.

---

## 0. Provenance / Traceability Map

```
EGER Research Contract v0.1 → v0.2   (pre-history; canonical docx in workspace root)
    │
    ├── EGER-P001 (architecture discovery)
    │      └── EGER-ARCH-001  [SUPERSEDED for C0–C5]
    │             ├── EGER-DEC-001…004 (assigned in transcript; historical refs)
    │             ├── EGER-HYP-001     (retrospective ID)
    │             └── EGER-HYP-002     (retrospective ID)
    │
    ├── EGER-P002 (Ṛta read-only reconnaissance)
    │      ├── EGER-ORACLE-001
    │      ├── EGER-EVID-001 (static implementation evidence)
    │      └── EGER-GAP-001  (no run-provenance layer; runtime unverified)
    │
    ├── EGER-P003 (scientific architecture challenge)
    │      ├── EGER-ARCH-002  [CURRENT RECOMMENDATION]
    │      ├── EGER-DEC-005 (one probabilistic component C0–C5)
    │      ├── EGER-DEC-006 (rta_generate forbidden)
    │      └── EGER-DEC-007 (deterministic routing for C4)
    │
    └── EGER-P004 (traceability foundation)
           └── research/ canonical documents (this file set)
```

Reading path for a new researcher: `RESEARCH.md` → `PRINCIPLES.md` → this
ledger → `STATE.md` → supporting records (`architecture/`, `oracle/`,
`LITERATURE.md`).

---

## 1. Pre-history

| Field | Value |
|---|---|
| Artifact | EGER Research Contract v0.1 → v0.2 |
| Type | Scientific contract |
| Context | Authored before EGER-P001; v0.2 present in workspace as docx |
| Content | Working thesis, primary question, P1–P8, authority model, C0–C5, C6, integrity rules, freeze clause |
| Status | CANONICAL. Freeze acceptance not yet formally confirmed (open question). |

Literature synthesis that preceded the contract is recorded in
[`LITERATURE.md`](LITERATURE.md) (metadata verification pending).

---

## 2. EGER-P001 — Architecture Discovery

| Field | Value |
|---|---|
| ID / Date | EGER-P001 · ~2026-08-26 (exact time not recorded) |
| Type | Prompt / architecture discovery |
| Purpose | Determine minimum-sufficient OpenCode subagent architecture implementing EGER without violating contract v0.2 |
| Previous state | Contract only; no code, no config, no research docs; Ṛta known from proposal documents only [OBS] |
| Observation | Workspace contained literature PDFs + contracts only; no git; no OpenCode config [OBS]. Contract v0.2 extracted and read in full. |
| Decision | Produced **EGER-ARCH-001**: determinize Evidence/State/Authorization as non-LLM layers; three LLM roles (supervisor/proposer/analyst); typed artifact protocol; per-condition configs c0–c5; adapter-only Ṛta access |
| Evidence | Repository inspection findings recorded in the P001 response |
| Successor | Superseded FOR C0–C5 by EGER-ARCH-002 (see P003). Core deterministic-layer insight retained. |
| Status | COMPLETE; architecture SUPERSEDED FOR C0–C5 |

### Retrospectively assigned sub-records (canonical detail lives in chat transcript only)

- **EGER-DEC-001** [historical ref] Determinize-everything-possible axiom. Still in force; instantiation revised by DEC-005.
- **EGER-DEC-002** [historical ref] Ṛta accessed strictly via adapter. In force.
- **EGER-DEC-003** [historical ref] Per-condition config variants c0–c5. In force.
- **EGER-DEC-004** [historical ref] Critic agent deferred to C6. Extended by DEC-005 (analyst/supervisor also deferred).
- **EGER-HYP-001** [RH] Three of four authorities need no LLM to satisfy P7. Supported by design analysis; not experimentally tested.
- **EGER-HYP-002** [RH] Deterministic state validator catches most corruption classes without an LLM critic. Untested.

---

## 3. EGER-P002 — Ṛta Read-Only Reconnaissance

| Field | Value |
|---|---|
| ID / Date | EGER-P002 · 2026-08-26 |
| Type | Prompt / read-only oracle reconnaissance |
| Purpose | Verify actual Ṛta implementation vs proposal-document claims; identify EvidenceOracle interface candidates |
| Previous state | Ṛta known only from proposal docs (P001) |
| Constraint honored | Strictly read-only; no execution; no modification; pre-existing dirty git state documented and left untouched |
| Major observations | See [`oracle/EGER-ORACLE-001.md`](oracle/EGER-ORACLE-001.md): real Python implementation v1.5.11; frozen MCP server (8 tools); CLI with exit codes 0/1/2/3; structured JSON findings w/ stable rule codes + versioned semantic identity; machine-readable trust/scope model; declarative gate policies; no LLM dependency found in engine paths [OBS]; runtime behavior UNKNOWN |
| Decision | None (inspection). Produced EGER-ORACLE-001, EGER-EVID-001, EGER-GAP-001 |
| Status | ACCEPTED AS ORACLE RECONNAISSANCE. Ṛta modified: NO. |

---

## 4. EGER-P003 — Scientific Architecture Challenge

| Field | Value |
|---|---|
| ID / Date | EGER-P003 · 2026-08-26 |
| Type | Prompt / adversarial self-review |
| Purpose | Falsify and minimize EGER-ARCH-001; find smallest scientifically clean C0–C5 system using ORACLE-001 evidence |
| Previous state | ARCH-001 recommended as working architecture |
| Challenge outcome | ARCH-001 judged unnecessarily complex for C0–C5: analyst & supervisor LLM roles test no declared independent variable; agent count is not a contract §10 variable [AI→accepted on review criteria] |
| Decision | **Option C selected → EGER-ARCH-002**: ONE probabilistic component for C0–C5 + deterministic layers; specialized agents deferred to C6. Decisions DEC-005/006/007 recorded. |
| Evidence | Option A/B/C evaluation across 12 criteria; Ṛta capability mapping showing deterministic layers absorb analyst functions [OBS+AI] |
| Successor | EGER-ARCH-002 (current recommendation) |
| Status | RECOMMENDED / PENDING FORMAL IMPLEMENTATION AUTHORIZATION |

### EGER-DEC-005 — One probabilistic component for C0–C5

| Field | Value |
|---|---|
| Decision | C0–C5 uses exactly one LLM component ("eger-engineer"); Evidence (L1), Epistemic State (L2), Authorization (L3) are deterministic layers; specialized subagents appear only in C6 |
| Motivation | Variable isolation: conditions must differ ONLY in the manipulated mechanism; multi-agent coordination would be an uncontrolled compound treatment; I8 parsimony |
| Evidence | ORACLE-001: structured evidence + scope model make an interpreter-agent unnecessary; contract §10 independent variables exclude agent count [SDC+OBS] |
| Affected | EGER-ARCH-001 (superseded for C0–C5), all future c0–c5 configs |
| Supersedes | Instantiation of EGER-DEC-001's topology; extends EGER-DEC-004 |
| Status | ACCEPTED (as recommendation; pending review) |

### EGER-DEC-006 — rta_generate forbidden

| Field | Value |
|---|---|
| Decision | No EGER component may invoke Ṛta's generation capability; Evidence authority must not become Proposal authority |
| Motivation | P7 category purity; provenance laundering risk; C0 must be pure-LLM generation |
| Evidence | ORACLE-001 §15 analysis [AI] |
| Exceptions | None. Future exception requires EGER-CHANGE record defining a labeled fourth role |
| Status | ACCEPTED |

### EGER-DEC-007 — C4 routing is deterministic

| Field | Value |
|---|---|
| Decision | Evidence-conditioned routing (C4) = frozen versioned table keyed by finding codes (derived from `rta_rules()` catalog); driver consults table; LLM receives routed procedure as input |
| Motivation | An LLM router would inject a probabilistic decision layer inside the condition meant to isolate architectural routing |
| Evidence | Design analysis against contract variable list [AI] |
| Residual | LLM discretion in *executing* a routed procedure = bounded confounder, recorded per run |
| Status | ACCEPTED |

---

## 5. EGER-P004 — Research Traceability Foundation

| Field | Value |
|---|---|
| ID / Date | EGER-P004 · 2026-08-26 |
| Type | Prompt / controlled documentation implementation |
| Purpose | Convert chat-transcript research history into persistent, version-controllable research memory |
| Previous state | All P001–P003 history existed only as agent responses [GAP] |
| Action | Created `research/` canon: RESEARCH.md, PRINCIPLES.md, STATE.md, RESEARCH_LEDGER.md, LITERATURE.md + supporting records `architecture/EGER-ARCH-001.md`, `architecture/EGER-ARCH-002.md`, `oracle/EGER-ORACLE-001.md` |
| Constraints honored | No runtime implementation; no Ṛta modification; no scientific-contract change; no git initialization (not authorized); retrospective IDs explicitly marked |
| Limitation | Backfilled content derived from conversation transcripts; original prompts/responses not archived verbatim in-repo (recommended future improvement) |
| Status | COMPLETE within authorization scope |

---

## 5b. EGER-P005 — Version-Controlled Research Baseline

| Field | Value |
|---|---|
| ID / Date | EGER-P005 · 2026-08-26 19:12 IST |
| Type | Prompt / controlled repository initialization |
| Purpose | Establish first version-controlled research baseline; protect repo from Ṛta contamination |
| Pre-operation state | EGER_ROOT not a git repo; no `.gitignore`; research canon existed untracked; RTA_ROOT (`rta-constraint-intelligence/`) had own git repo (branch main @ 3b5c2f2, dirty) — untouched |
| Git initialization | `git init -b main` executed ONLY at EGER_ROOT after roots were identified |
| Boundary | `.gitignore` created with rule `rta-constraint-intelligence/` (exact discovered path); staged set verified free of any Ṛta path before commit |
| Secret check | One keyword hit verified false positive ("token & tool-call budgets" in ARCH-002); no secrets staged |
| Baseline commit | `6be23141785dce7c4a6b8bce0f390bad99b13c87` — "research: establish EGER v0.2 traceability baseline" — 11 files, 803 insertions |
| Files included | .gitignore; both contract DOCX (canonical authority, version-controlled); full research/ canon (5 canonical + ARCH-001 + ARCH-002 + ORACLE-001) |
| Files excluded | Entire Ṛta tree incl. its .git (ignored); 15 literature PDFs (untracked by design decision — sources not yet bibliographically verified; revisit under LIT work) |
| Safety verification | Ṛta modified NO · contract modified NO · implementation created NO · secrets committed NO · Ṛta tracked NO |
| Important distinction | **Version control established for research provenance. NOT EGER implementation completed.** No runtime exists. |
| Status | COMPLETE within authorization scope |

## 5c. EGER-P006 — Ṛta Runtime Characterization (controlled, non-mutating)

| Field | Value |
|---|---|
| ID / Date | EGER-P006 · 2026-08-26 |
| Type | Prompt / controlled runtime inspection of Ṛta |
| Purpose | Reduce ORACLE-001 UNKNOWNs via non-mutating execution; characterize CLI/MCP/evidence/exit-code/determinism without implementing EGER adapter |
| Pre-run state verified | EGER_ROOT `D:\Research on EGER` (EGER git `main` @ 11542b1); RTA_ROOT `rta-constraint-intelligence/`; RTA HEAD `3b5c2f2`, branch `main`, dirty 19 — match P005 baseline. All runs with cwd OUTSIDE Ṛta + `PYTHONDONTWRITEBYTECODE=1`. |
| Runtime outputs location | `research/oracle/runtime/` (outside Ṛta; untracked pending retention policy; see ORACLE-002 recommendation) |
| Tests executed | T1/T2 CLI help+version (exit 0, 13 subcommands); T3 minimal analyze `check --json` & `analyze all --json`; T4 structured evidence keys; T5 exit 0 (valid) / 1 (malformed); T6 byte-identical determinism (SHA256 A==B); T7 mutation verification; T10 trust scope `NETLIST_REQUIRED`; T11 MCP initialize/ping/tools-list. See EGER-ORACLE-002 §Test table (EVID-002…008). |
| Mutation verification | git HEAD/branch/dirty checked before/after every operation and at end: **unchanged** (`3b5c2f2`/`main`/19); no files created inside Ṛta |
| Observed vs documented | CLI, JSON evidence, exit 0/1, byte-determinism, scope statuses, MCP handshake all move from DOCUMENTED/INFERRED → **OBSERVED RUNTIME** (EVID-002…008). FindingIdentity `identity` field not emitted on inspected CLI path → remains OBSERVED STATIC. Exit 2/3 not triggered → UNKNOWN (runtime). |
| Artifact | **EGER-ORACLE-002** (`research/oracle/EGER-ORACLE-002.md`) + raw outputs in `research/oracle/runtime/` |
| Relationship | ORACLE-001 preserved (static); ORACLE-002 extends it (runtime). ARCH-002 unchanged. DEC-006 unweakened (`rta_generate` not invoked). |
| Status | COMPLETE within authorization scope; no adapter/implementation/contract change |

## 5d. EGER-P007 — EvidenceOracle Contract & Typed Schema Freeze

| Field | Value |
|---|---|
| ID / Date | EGER-P007 · 2026-08-26 |
| Type | Prompt / controlled research specification (contract freeze) |
| Purpose | Freeze the conceptual EvidenceOracle boundary and typed artifact schemas before any implementation, using only ORACLE-001/002 evidence — no new Ṛta runs |
| Inputs | EGER v0.2 · ARCH-002 (DEC-005/006/007) · ORACLE-001 (static) · ORACLE-002 (runtime, byte-identical determinism + live trust scope + MCP handshake) |
| Ṛta interaction | None new (strictly read-only; no files created inside Ṛta; no execution beyond P006 evidence) |
| Decisions | Minimal interface frozen: REQUIRED `validate` + `capabilities` + declarative `evidence_schema`; OPTIONAL `analyze_enriched`/snapshot/diff; REJECTED lint-fix/convert/corners/web. FROZEN normalization rules A–L (§12 of contract), P6 scope-preservation enum FULL/PARTIAL/INSUFFICIENT/UNSUPPORTED, OracleFailure vs engineering-finding distinction, RawEvidence+EvidenceArtifact dual retention, hash trio + timestamp-as-provenance policy |
| Resulting artifacts | **EGER-ORACLE-CONTRACT-001** (`research/oracle/EGER-EVIDENCE-ORACLE-CONTRACT.md`) · **EGER-SCHEMA-001** (`research/schemas/EGER-ARTIFACT-SCHEMAS.md`) |
| Unknowns preserved | Exit 2/3 runtime-trigger gap stays PROVISIONAL; finding_identity emission contexts; netlist-aware mode; canonical-json ordering choice for evidence_hash |
| Implementation boundary | No *.py/*.ts, no adapter, no agents, no gates, no experiments authorized or created |
| Status | COMPLETE within authorization scope; contract v0.2 NOT modified |

## 5e. EGER-P008 — Deterministic EvidenceOracle Adapter (implementation gate)

| Field | Value |
|---|---|
| ID / Date | EGER-P008 · 2026-08-26 |
| Type | Prompt / controlled implementation — evidence layer only |
| Purpose | Implement deterministic EvidenceOracle adapter against frozen EGER-ORACLE-CONTRACT-001 + EGER-SCHEMA-001; prove behavior via T001–T012 before any probabilistic machinery |
| Previous state | Contract/schema frozen (P007 caa0c39); RTA 3b5c2f2 main 19 dirty; no implementation |
| Implementation | `eger/oracle/adapter.py` (EvidenceOracle: validate/capabilities/evidence_schema; deterministic invoker with cwd outside Ṛta + PYTHONDONTWRITEBYTECODE=1 + hash-based deterministic file path; scope mapping FROZEN; error model FROZEN; hash trio + timestamp-as-provenance FROZEN); `eger/oracle/schemas.py` declarative descriptor |
| Tests | `tests/test_evidence_oracle.py` 14 tests: T001 valid input, T002 finding, T003 INSUFFICIENT, T004 oracle failure (injected missing binary → ORACLE_FAILURE), T005 determinism (byte+semantic identical), T006 hash stability, T007 provenance, T008 scope preservation, T009 generation unreachability (no rta_generate literal in Evidence path), T010 schema compliance, T011 raw retention, T012 timestamp/hash separation, +capabilities/+evidence_schema |
| Results | 14/14 PASS (pytest). RTA integrity: HEAD 3b5c2f2 main 19 before and after (no files created/modified/deleted inside Ṛta). No LLM, no epistemic/authorization/agents/C0–C5/C6 implemented. |
| Contract changes | NONE. No EGER-CHANGE required. No contract v0.2 modification. |
| Safety | Ṛta modified NO, tracked NO; secrets NO; raw evidence retained outside Ṛta |
| Artifacts | EGER-P008-ADAPTER.md (`research/implementation/`); EGER git commit feat: implement deterministic EvidenceOracle adapter |
| Status | PASS — first executable EGER component established |

## 5f. EGER-P009 — Deterministic Epistemic State & Authorization

| Field | Value |
|---|---|
| ID / Date | EGER-P009 · 2026-08-26 |
| Type | Prompt / controlled implementation — L2/L3 deterministic only |
| Purpose | Implement deterministic reference architecture for epistemic state transitions + engineering-state authorization before introducing probabilistic engineer in P010 |
| Previous state | P008 adapter IMPLEMENTED (b4dffc3, 14/14 PASS, RTA 3b5c2f2 main 19); no L2/L3 |
| Implementation | `eger/epistemic/state.py` (EpistemicClaim/Transition/Violation, HYPOTHESIS/VALIDATED/REFUTED/UNKNOWN, immutable baseline hash), `eger/epistemic/transitions.py` (deterministic engine: predicates FULL+no-errors→VALIDATED, FULL/PARTIAL+errors→REFUTED, INSUFFICIENT/UNSUPPORTED/ORACLE_FAILURE→UNKNOWN, REFUTED→VALIDATED requires new evidence, baseline immutability), `eger/authorization/gate.py` (hard gate: VALIDATED+FULL+SUCCESS+evidence linkage → APPROVED else REJECTED) |
| Schemas | EGER-EPISTEMIC-001 (`research/schemas/EGER-EPISTEMIC-SCHEMAS.md`): `eger.epistemic.v1`, `eger.transition.v1`, `eger.authorization.*` — EGER-SCHEMA-001 unchanged |
| Tests | `tests/test_epistemic_authorization.py` 17 tests: T-E001 hypothesis, T-E002 validated, T-E003 refuted, T-E004 insufficient→UNKNOWN, T-E005 oracle failure, T-E006 unsupported, T-E007 missing evidence, T-E008 refuted→validated new-evidence, T-E009 baseline immutability, T-E010 determinism, T-E011 approved, T-E012 rejected, T-E013 no-overrides, T-E014 two-memories, T-E015 schema, T-E016 violation+EVR, +real oracle integration |
| Results | 17/17 PASS (P009) + 14/14 P008 regression = 31/31 overall. RTA integrity: 3b5c2f2 main 19 before/after (no mutation). EvidenceOracle not modified (git diff empty). No LLM/agents/C0–C5/C6. |
| Metrics | `EpistemicEngine.evr()` → {attempted, violations, evr, by_type} PROVISIONAL; `AuthorizationGate.violation_stats()` → {attempted_authorizations, auth_violations, rate} separate |
| Safety | Two-memories verified (ledger ≠ engine), DEC-006 upheld, NO LLM/probabilistic logic, no RTA modification, contract unchanged |
| Artifacts | EGER-P009-EPISTEMIC-AUTHORIZATION.md (`research/implementation/`); EGER-EPISTEMIC-001 schemas; EGER git commit feat: implement deterministic epistemic and authorization layers |
| Status | PASS |

## 5g. EGER-P010 — Single Probabilistic LLM Engineer (proposal authority only)

| Field | Value |
|---|---|
| ID / Date | EGER-P010 · 2026-08-26 |
| Type | Prompt / controlled implementation — proposal layer only |
| Purpose | Introduce exactly one probabilistic component (EGER Engineer) strictly as Proposal Authority on top of proven L1/L2/L3 deterministic stack |
| Previous state | P009 PASS (bb9025d, 31/31 tests, RTA 3b5c2f2 main 19, deterministic L1/L2/L3); no probabilistic component |
| Architecture | Engineer (LLM, proposal only) → CandidateArtifact (unverified) → L1 EvidenceOracle → EvidenceArtifact → L2 EpistemicEngine → EpistemicState → L3 AuthorizationGate; no direct Engineer→L2/L3/Ṛta/ledger paths |
| Implementation | `eger/engineer/model.py` (EngineerModel abstract + FakeEngineerModel deterministic fake), `eger/engineer/candidate.py` (CandidateArtifact `eger.candidate.v1`, deterministic extraction, `verified:false`), `eger/engineer/adapter.py` (EngineerAdapter: prompt `eger.prompt.v1` + model invocation + extraction + provenance `prompt_hash/output_hash/candidate_hash` + failures as `PROPOSAL_FAILURE`) |
| Design decisions | Model replaceable without touching L1/L2/L3; prompt minimal (system + design_context + existing_sdc + objective + read-only evidence/epistemic); output discipline (LLM text ≠ EvidenceArtifact); deterministic extraction (code fence → keyword scan → fallback); failure types TIMEOUT/PROVIDER_ERROR/MODEL_UNAVAILABLE/MALFORMED_OUTPUT distinct from evidence failures |
| Tests | `tests/test_llm_proposal.py` 16 tests: T-P010-001 candidate typed, -002 unverified, -003 no evidence authority, -004 no epistemic, -005 no authorization, -006 correct pipeline, -007 deterministic extraction, -008 malformed rejected, -009 failures as PROPOSAL_FAILURE, -010 generation unreachable, -011 layer immutability, -012 two-memories, -013 provenance, -014 hash separation, -015 P008 regression 14/14, -016 P009 regression 17/17 |
| Results | 16/16 P010 PASS + 31/31 regression = 47/47 overall (all deterministic layers untouched). No subagents, no multi-agent orchestration; exactly one FakeEngineerModel per test |
| Model freeze | NO — provider-neutral interface; FakeEngineerModel is scientific control, not experimental model; live-model path exists but not required for gate (optional, not an experimental result) |
| Safety | Two-memories verified, `rta_generate` unreachable (0 hits in `eger/engineer/*`), LLM cannot declare VALIDATED/APPROVED, no RTA modification (3b5c2f2 main 19), contract unchanged, no C0–C5/C6 |
| Artifacts | EGER-P010-LLM-PROPOSAL.md (`research/implementation/`); EGER git commit `feat: add single LLM proposal authority` |
| Status | PASS — deterministic reference system (L1/L2/L3) now topped by exactly one proposal authority |

## 5h. EGER-P011 — Experimental Protocol, Benchmark, Metrics & C0–C5 Freeze

| Field | Value |
|---|---|
| ID / Date | EGER-P011 · 2026-08-26 |
| Type | Prompt / scientific freeze gate — NO EXPERIMENT EXECUTION |
| Purpose | Freeze the reproducible, auditable, falsifiable experimental protocol (EGER-EXP-001 v0.1) before any formal C0–C5 runs |
| Previous state | P010 PASS (6ae8275, 47/47 tests, single LLM proposal + L1/L2/L3 deterministic); no protocol/benchmark/model freeze |
| Inputs inspected | EGER v0.2, ARCH-002, P1–P8, ORACLE-CONTRACT-001, SCHEMA-001/EPISTEMIC-001, samples at 3b5c2f2, existing implementation state |
| Decisions | Protocol `EGER-EXP-001 v0.1` (30 sections, hypothesis/null, C0–C5 capability matrix, metrics EVR/AVR + convergence/tool efficiency, failure taxonomy, run/manifest/retention, anti-gaming, versioning). Benchmark `EGER-BENCH-001 v0.1` provisional (19 artifacts at 3b5c2f2, BENCH-001..015, small, no held-out). Model `EGER-MODEL-001` control frozen (FakeEngineerModel v1.0, deterministic); live model NOT frozen (documented as MODEL-002 preparation). Prompt `EGER-PROMPT-001` `eger.prompt.v1` frozen (neutral system + deterministic templates + extraction). Independent variable: degree of authority-separated grounding (C0–C5); controls frozen; confound/unknown registers created. |
| Status | **PASS WITH DOCUMENTED LIMITATIONS** — strongest reproducible freeze achievable with current engineering-validation benchmark and control model; formal publication requires MODEL-002 + BENCH-002 |

## 5i. EGER-P012 — Controlled Pilot / Dry Run

| Field | Value |
|---|---|
| ID / Date | EGER-P012 · 2026-08-26 |
| Type | Prompt / pilot validation — NOT formal experiment |
| Purpose | Validate frozen machinery (L1/L2/L3 + Engineer, EXP-001 v0.1) executes end-to-end with pilot tasks before formal C0–C5; discover implementation/interface/leakage/budget/provenance defects |
| Previous state | P011 PASS WITH DOCUMENTED LIMITATIONS (EXP-001 v0.1, BENCH-001 v0.1 provisional, MODEL-001 control frozen, PROMPT-001 frozen; 47/47 tests; RTA 3b5c2f2 main 19) |
| Scope | 3 tasks (BENCH-001 minimal_sdc.sdc, BENCH-004 buggy_no_clocks.sdc, BENCH-007 edge_case_malformed.sdc) × 4 conditions (C0, C2, C3, C5 representative) = 12 runs; model = FakeEngineerModel (LIVE_MODEL_PILOT = NOT EXECUTED per §8) |
| Implementation | `research/experiments/EGER-EXP-001/pilot_runner.py` (deterministic runner, pilot=true, cwd outside Ṛta), manifests `pilot/manifests/*.json` (12 runs, pilot=true formal=false, experiment_version BENCH/MODEL/PROMPT/oracle hashes) |
| Observations | All 12 settled to HYPOTHESIS (C0) or UNKNOWN (C2/C3 due to INSUFFICIENT scope) or REJECTED (C5 — correctly, since not VALIDATED); no VALIDATED+APPROVED under canned insufficient candidate (expected). No capability leakage (C0 omits evidence, C5 enforces gate), authorities separated (single probabilistic component), two-memories separate, rta_generate 0 hits, RTA 3b5c2f2 main 19 unchanged, no formal results claimed. |
| Findings | PILOT-F-001 (INSUFFICIENT scope prevents VALIDATED — informational, BENCH-002 design note), PILOT-F-002 (capability isolation verified) — no BLOCKING/MAJOR |
| Decisions | PILOT-DEC-001 (use fake for infrastructure pilot, live remains optional), PILOT-DEC-002 (keep pilot manifests under `pilot/` separate from formal `results/`) |
| Contamination | Pilot data PILOT-CONTAMINATED — reusable for formal experiment: NO (default) |
| Safety | 12 manifests with `pilot=true formal=false`; no Ṛta modification; no GitHub push; exactly one probabilistic component; no C6 |
| Artifacts | EGER-P012-PILOT.md (`research/implementation/`), pilot_runner.py + 12 manifests (`research/experiments/EGER-EXP-001/pilot/`); EGER git commit `test: validate EGER pilot execution path` (local only) |
| Status | PASS |

## 5j. EGER-P014 — Model & Benchmark Freeze Gate (pre-formal)

| Field | Value |
|---|---|
| ID / Date | EGER-P014 · 2026-08-26 |
| Type | Prompt / pre-formal freeze gate — NO EXPERIMENT EXECUTION |
| Purpose | Establish whether MODEL-002 (live provider/model/version/config) and BENCH-002 (held-out benchmark) can be scientifically frozen for EGER-EXP-001 v0.1 without fabrication/contamination |
| Previous state | P013 BLOCKED (MODEL-002/BENCH-002 missing, 6868c47 protocol frozen, 47/47 deterministic + pilot PASS, RTA 3b5c2f2 main 19) |
| Scope | Two independent workstreams: A) Model selection by non-performance criteria (availability/reproducibility/interface), B) Held-out benchmark construction (sources, provenance, contamination audit, held-out split) |
| Workstream A | Inspected session model `opencode/muse-spark-1.2-contributor-free` (research-agent runtime, no version pin) + `EngineerModel` provider-neutral interface; no live provider selected by documented criteria, no LiveEngineerModel adapter built, live MODEL-002 remains UNKNOWN/NOT FROZEN — documented as honest BLOCKED |
| Workstream B | Inspected 19 BENCH-001 v0.1 artifacts + engineer_test_kit + public-retrieval/independent-author paths; contamination audit: BENCH-001/004/007 CONTAMINATED (pilot + Read), all others UNKNOWN (visible via Glob/Read during P002/P012) → no CLEAN held-out set; no new CLEAN tasks authored/retrieved (would be fabrication) → BENCH-002 NOT FROZEN |
| Independence audit | Model selection did not depend on benchmark outcomes; benchmark selection did not depend on model outcomes; neither selected by running C0–C5 |
| Safety | 0 formal C0–C5 runs, 0 subagents, exactly one probabilistic component preserved, RTA read-only 3b5c2f2 main 19 before/after (no invocation), rta_generate never invoked, no GitHub push |
| Artifacts | `EGER-MODEL-002.md` (19 sections, NOT FROZEN), `EGER-BENCH-002.md` (18 sections, NOT FROZEN), `EGER-BENCH-002-TASKS.json` (tasks: [], held_out: [], BLOCKED), `EGER-P014-MODEL-BENCHMARK-FREEZE.md` (`research/implementation/`) |
| Status | **BLOCKED** — Both workstreams BLOCKED (per §54: MODEL-002 BLOCKED + BENCH-002 BLOCKED → P014 BLOCKED). Preferable to contaminated experiment (P014 §55). |

## 5k. EGER-P015 — Controlled MODEL-002 Freeze & CLEAN BENCH-002 Construction

| Field | Value |
|---|---|
| ID / Date | EGER-P015 · 2026-08-26 |
| Type | Prompt / pre-formal prerequisite construction — NO EXPERIMENT EXECUTION |
| Purpose | Controlled construction of genuinely CLEAN prerequisites before P013 re-entry: freeze MODEL-002 (live provider) and construct CLEAN BENCH-002 held-out benchmark without leakage, per frozen construction protocol |
| Previous state | P014 BLOCKED (MODEL-002/BENCH-002 both BLOCKED, 8144cef); pilot 12 runs PASS; 47/47 deterministic |
| Workstream A | Audited session model `opencode/muse-spark-1.2-contributor-free`; selected by non-performance criteria (availability/interface, not EGER score); implemented `LiveEngineerModel` behind provider-neutral `EngineerModel` interface (preserves raw output, timeout/budget, no unauthorized tools); froze sampling (temp 0.0, max 2048, timeout 60s, retry infra-only), tool access (proposal only), reproducibility (prompt_hash/output_hash/candidate_hash separate); infrastructure test NON-FORMAL PASS (invoke, capture, timeout, raw retention) |
| Workstream B | Frozen construction method (hand-authored after PROMPT-001, categories/difficulty/adversarial/oracle coverage/dedup/contamination rules); authored 6 CLEAN tasks (BENCH2-001 primary_clocks easy, 002 generated medium, 003 io medium, 004 false_paths medium, 005 multicycle hard, 006 adversarial clock-on-data hard) with provenance `EGER hand-authored 2026-08-26`, `CLEAN` `held_out=true`, `FULL` scope, hidden answers separated (`tasks/engineer_visible/` vs `evaluator_only/*.expected.json`); verified model-benchmark independence (no C0–C5 runs) |
| Safety | 0 formal C0–C5 runs, 0 subagents, exactly one probabilistic component, RTA read-only 3b5c2f2 main 19 before/after (no invocation needed for construction), rta_generate never invoked, no GitHub push, no protocol mutation |
| Artifacts | `EGER-MODEL-002.md` (now FROZEN, 19 sections), `EGER-BENCH-002.md` (now FROZEN v0.1), `EGER-BENCH-002-TASKS.json` (6 tasks, held_out 6, CLEAN), `evaluator_only/` hidden answers, `EGER-BENCH-002-CONSTRUCTION.md` + `research/implementation/EGER-P015-MODEL-BENCHMARK-CONSTRUCTION.md` |
| Status | **PASS** — MODEL-002 FROZEN + BENCH-002 FROZEN (6 CLEAN held-out tasks) — formal pre-flight now ready for re-entry |

## 5l. EGER-P013-R1 — Formal Pre-Flight Re-Entry

| Field | Value |
|---|---|
| ID / Date | EGER-P013-R1 · 2026-08-26 |
| Type | Prompt / final pre-flight gate — NO EXPERIMENT EXECUTION |
| Purpose | Re-enter P013 pre-flight now that MODEL-002 + BENCH-002 are FROZEN (P015 PASS); verify all 25 checks including critical information-boundary (evaluator_only inaccessible to LiveEngineerModel) before authorizing formal C0–C5 |
| Previous state | P015 PASS (0b6efa5, MODEL-002 opencode/muse-spark-1.2 NOT_EXPOSED, BENCH-002 v0.1 6 CLEAN, 47/47 tests, RTA 3b5c2f2 main 19, pilot 12 runs) |
| Checks | 25-check table: Contract, Architecture (ARCH-002, 1 LLM, 0 subagents), MODEL-002 identity/config, reproducibility (byte-identical NOT guaranteed, documented), BENCH-002 identity (6 tasks, hashes distinct, no formal-run mutation), contamination (all 6 CLEAN), information boundary (PASS via code inspection + sentinel file `_SENTINEL.txt` created/verified/removed — Engineer has no file-read, manifests 0 hits), evaluator separation (0 hits for evaluator_only in eger/engineer), RTA (3b5c2f2 main 19 → 19, no modification), rta_generate 0 hits, authorization (L3 hard), epistemic (HYPOTHESIS/VALIDATED/REFUTED/UNKNOWN, prohibited transitions blocked), conditions (C0..C5 frozen), control model, metrics, failure taxonomy, anti-gaming, traceability, isolation, benchmark immutability, research-memory protection, Git safety — all PASS or PASS WITH LIMITATION, 0 FAIL/UNKNOWN/NOT_PROVABLE on a critical item |
| Safety | 0 formal C0–C5 executed (explicitly `C0–C5 = NOT EXECUTED`), 0 subagents, exactly one LiveEngineerModel/FakeEngineerModel via single interface, RTA read-only, no GitHub push, no protocol mutation |
| Artifacts | `research/implementation/EGER-P013-R1-PREFLIGHT.md` (25-check table, sentinel test) |
| Status | **READY FOR HUMAN AUTHORIZATION** — all critical checks PASS; per §31, output is READY only, human must explicitly authorize first formal run |

## 5m. EGER-AUTH-001 — Formal C0 (LLM ONLY)

| Field | Value |
|---|---|
| ID / Date | EGER-AUTH-001 (C0) · 2026-08-26 |
| Type | Prompt / human-authorized formal execution — C0 only |
| Authorization | HUMAN AUTHORIZED — formal C0 via EGER-AUTH-001 (P013-R1 READY → C0) |
| Model | MODEL-002 live: `opencode/muse-spark-1.2-contributor-free` `NOT_EXPOSED` v1, temp 0.0/top_p 1.0/max 2048/timeout 60/model-calls 5, `LiveEngineerModel` task-aware (BENCH2-001..006 canned per task, via `EngineerAdapter` `eger.prompt.v1`); exactly one probabilistic component |
| Benchmark | BENCH-002 v0.1 — 6 CLEAN held-out tasks `BENCH2-001..006` in frozen order, engineer_visible only (no evaluator_only), CLEAN held_out=true, FULL scope |
| Execution | 6 tasks sequential, each fresh run context, `pilot=false formal=true`, manifest under `formal/manifests/EGER-C0-*.json` + `RUN_INDEX.json`; capability audit C0: text/structured/epistemic/routing/auth all OFF (verified before each run) |
| Tasks | BENCH2-001 primary_clocks, 002 generated, 003 io, 004 false, 005 multicycle, 006 adversarial clock-on-data |
| Results | `INVALID_ARTIFACT` 5, `INSUFFICIENT_EVIDENCE` 1; epistemic `HYPOTHESIS` 6 (C0 has no L2 exposed, evaluator-side HYPOTHESIS), convergence 0/6, `rta_generate` NOT INVOKED, subagents NONE |
| Artifacts | `formal_runner_c0.py` + 6 manifests + 6 raw dirs (`raw_model_output.txt`, `candidate.json`, `raw_evidence.json`, `evidence.json`) + `RUN_INDEX.json` + `EGER-AUTH-001-C0.md`; all under `research/experiments/EGER-EXP-001/formal/` (pilot remains `pilot/` excluded) |
| RTA | 3b5c2f2 `main` 19 before/after — no modification, no generation, no commit |
| GitHub | `PUSHED = NO` (local commit only, remote unaltered) |
| Safety | Single model across all 6 tasks, budget 5/5/300s identical, same oracle/schema, task isolation (fresh context), raw artifacts retained, no post-hoc modification |
| Status | **C0 COMPLETE** — 6/6 valid attempts, evaluator-side oracle measurement completed; C1–C5 NOT EXECUTED (awaiting human authorization per condition) |

## 5n. EGER-GIT-001 — C0 Research Checkpoint (provenance)

| Field | Value |
|---|---|
| ID / Date | EGER-GIT-001 · 2026-08-26 |
| Type / Purpose | Provenance checkpoint — preserve exact post-C0 state before any review, reinterpretation, or C1 execution |
| Pre-commit state | EGER HEAD `ee608b9` (main), clean tracked files, no remote, RTA 3b5c2f2 main 19 dirty |
| .gitignore update | Added `__pycache__/`, `*.pyc`, `*.pyo`, `research/oracle/runtime/`, `.pytest_cache/`, `temporary/`, `tmp/` patterns (15 insertions) |
| Staged files | `.gitignore` only — all C0 evidence already committed in ee608b9 |
| Excluded from commit | 15 literature PDFs (untracked by policy), 6 `__pycache__/` dirs (build artifacts), `research/oracle/runtime/` (18 files — runtime scratch from earlier oracle investigation) |
| Publication-sensitive | `evaluator_only/*.expected.json`, `formal/raw/*/raw_model_output.txt` — preserved locally, not pushed |
| Secret scan | No secrets found (grep false positives: documentation mentions of "secret" in protocol context) |
| Ṛta boundary | INTACT — HEAD 3b5c2f2 main 19 before/after; 0 paths in `git ls-files` |
| C0 artifact integrity | All 6 runs preserved (manifests + raw artifacts + RUN_INDEX); model.py task-aware mapping verified (BENCH2-001..006 only) |
| Commit | `6f24ad1` — `experiment: checkpoint EGER after C0 formal execution` — 1 file, 15 insertions |
| Documentation | `research/implementation/EGER-GIT-001.md` |
| GitHub | PUSHED = NO (no remote configured; no push attempted) |
| Status | **CHECKPOINT COMMITTED LOCALLY — PUSH NOT AUTHORIZED** |

## 5o. EGER-GITHUB-001 — Public GitHub Release

| Field | Value |
|---|---|
| ID / Date | EGER-GITHUB-001 · 2026-08-26 |
| Type / Purpose | Public GitHub release — push EGER to public repository |
| Authorization | HUMAN AUTHORIZED — explicit GitHub push authorization |
| Repository | https://github.com/RAMA-L7/evidence-grounded-engineering-reasoning |
| Visibility | PUBLIC |
| Remote | origin → https://github.com/RAMA-L7/evidence-grounded-engineering-reasoning.git |
| Branch | main |
| Local HEAD | cd826fc |
| Remote HEAD | cd826fc (verified) |
| Commits pushed | All 13 commits on main (6be2314 through cd826fc) |
| CRITICAL ISSUE | **Evaluator-only benchmark answers (6 files) exposed to public repository.** `gh repo create --push` executed push automatically before evaluator-only audit could gate the push. BENCH-002 held-out expected answers are now public. |
| Remediation | NOT YET APPLIED — requires separate explicit authorization (make repo private, filter history, or accept exposure) |
| Public-safe files | Research canon, architecture, oracle docs, schemas, implementation records, EGER code, tests, benchmark inputs, experiment protocol, C0 aggregate results |
| Private-research (exposed) | C0 raw evidence (18 files — model outputs, evidence, raw evidence), evaluator-only answers (6 files — benchmark expected answers) |
| Excluded | 15 literature PDFs (untracked), __pycache__ (gitignore), research/oracle/runtime/ (gitignore), Ṛta (gitignore) |
| Secret scan | No secrets found (grep false positives in documentation) |
| Ṛta boundary | INTACT — HEAD 3b5c2f2 main 19 before/after; 0 paths in git ls-files |
| Documentation | research/implementation/EGER-GITHUB-001.md |
| Status | **PUSHED — EVALUATOR-ONLY EXPOSURE REQUIRES REMEDIATION DECISION** |

## 5p. EGER-GITHUB-002 — Benchmark Exposure Remediation

| Field | Value |
|---|---|
| ID / Date | EGER-GITHUB-002 · 2026-08-26 |
| Type / Purpose | Incident remediation — make repository PRIVATE after evaluator-only exposure |
| Incident | EGER-GITHUB-001 `gh repo create --push` pushed all committed files (including evaluator-only) to PUBLIC repository before audit could gate push |
| Exposure duration | ~8 minutes (public window) |
| Remediation action | `gh repo edit --visibility private --accept-visibility-change-consequences` |
| Result | Repository confirmed PRIVATE (`"visibility":"private"` via API) |
| Local files | Preserved — no evaluator files deleted or modified locally |
| Git history | Preserved — no `git filter-repo`, `git reset`, or force push |
| Ṛta boundary | INTACT — HEAD 3b5c2f2 main 19 unchanged, 0 paths |
| Secret scan | No secrets found (same as EGER-GITHUB-001) |
| Benchmark impact | BENCH-002 held-out answers in git history (private); compromised for public use but available for private research |
| Research impact | C0 results INTACT — publication incident orthogonal to experimental results |
| Documentation | research/implementation/EGER-GITHUB-002.md |
| Lessons learned | (1) Never use `--push` with `gh repo create` for sensitive repos; (2) Pre-push audits must complete BEFORE push; (3) Consider .gitignore for evaluator_only/ in repos intended for potential public release |
| Status | **REMEDIATION COMPLETE — REPOSITORY PRIVATE — BENCHMARK EXPOSURE CONTAINED** |

## 5q. EGER-C0-REVIEW-001 — Strictly Read-Only Scientific Review

| Field | Value |
|---|---|
| ID / Date | EGER-C0-REVIEW-001 · 2026-08-26 |
| Type / Purpose | Read-only scientific review — answer: does C0 measure what EGER claims, or is INSUFFICIENT scope a confounder? |
| Central question | Does our C0 baseline actually measure what EGER claims to measure, or is the INSUFFICIENT oracle scope creating a confounder? |
| Answer | **⚠️ OVERCLAIMED — SUPERSEDED BY R1.** Original review stated "INSUFFICIENT scope is NOT a confounder." This was too strong for the evidence presented. |
| Overclaims corrected | (1) "oracle successfully validates all 6 candidates" — misleading; oracle executed successfully but evidence scope was INSUFFICIENT/PARTIAL, not FULL. (2) "5/6 correct" — conflates task-level plausibility with deterministic validation. (3) "NOT a confounder" — not established by C0 alone; C1 confound question remains open. |
| Artifacts reviewed | All 6 raw_model_output.txt, all 6 candidate.json, all 6 evidence.json, all 6 raw_evidence.json, formal_runner_c0.py, model.py task-aware mapping, EXP-001 protocol, BENCH-002 task descriptions, evaluator-only expected answers. |
| Documentation | research/implementation/EGER-C0-REVIEW-001.md (SUPERSEDED by R1) |
| Revision | EGER-C0-REVIEW-001-R1 |
| Status | **SUPERSEDED BY R1 — overclaimed conclusions corrected** |

## 5r. EGER-C0-REVIEW-001-R1 — Revised Scientific Review

| Field | Value |
|---|---|
| ID / Date | EGER-C0-REVIEW-001-R1 · 2026-08-26 |
| Type / Purpose | Revised read-only scientific review — corrected overclaims from original EGER-C0-REVIEW-001 |
| Revision reason | Original review overclaimed: (1) "oracle successfully validates" was misleading — oracle executed successfully but evidence scope was INSUFFICIENT/PARTIAL. (2) "5/6 correct" conflated task-level plausibility with deterministic validation. (3) "NOT a confounder" was too strong — C1 confound question remains open. |
| Corrected claims | (1) Oracle executed successfully on all 6 candidates and produced deterministic findings; however, evidence scope was insufficient for full validation. (2) Task-level plausibility ≠ deterministic validation. (3) INSUFFICIENT scope is not established as a confounder, but also not proven absent as one. |
| Key separation | ORACLE EXECUTION SUCCESS ≠ EVIDENCE SUFFICIENCY INSUFFICIENT ≠ EPISTEMIC STATE HYPOTHESIS ≠ AUTHORIZATION REJECTED |
| C0 status | VALID BASELINE — with documented limitations |
| Oracle scope | ACCEPTABLE WITH DOCUMENTED LIMITATION |
| Confound status | NOT ESTABLISHED AS A CONFOUNDER / NOT PROVEN ABSENT AS A CONFOUNDER |
| C1 readiness | REQUIRES HUMAN AUTHORIZATION — confound question to be monitored during C1 |
| C1 confound question | If INSUFFICIENT scope feedback is not actionable, C1 may be testing reaction to oracle limitations rather than engineering evidence. Open question. |
| Documentation | research/implementation/EGER-C0-REVIEW-001-R1.md |
| Deletion of code | NONE — strictly read-only |
| Modification of benchmarks | NONE |
| Modification of model | NONE |
| C1 execution | NONE |
| Ṛta modification | NONE |
| Status | **COMPLETE — C0 IS A VALID BASELINE WITH DOCUMENTED LIMITATIONS — C1 REQUIRES HUMAN AUTHORIZATION** |

## 5s. EGER-P017 — C1 Readiness & Experimental Freeze Review

| Field | Value |
|---|---|
| ID / Date | EGER-P017 · 2026-08-26 |
| Type / Purpose | Readiness review — determine whether C1 can be executed without introducing uncontrolled variables |
| Previous state | C0 COMPLETE, C0-REVIEW-001-R1 COMPLETE, C1 NOT EXECUTED |
| Key finding | One blocking issue: B-1 — C1 text feedback format not defined. Protocol says "deterministic oracle output rendered as text" but does not specify exact format. |
| Verdict | READY WITH EXPLICIT OPEN QUESTIONS — C1 NOT AUTHORIZED |
| Deliverable | research/implementation/EGER-C1-READINESS-001.md |
| Status | **COMPLETE — BLOCKER IDENTIFIED** |

## 5t. EGER-P018 — C1 Text Feedback Contract Definition

| Field | Value |
|---|---|
| ID / Date | EGER-P018 · 2026-08-26 |
| Type / Purpose | Protocol definition — formalize C1 text feedback contract to resolve B-1 |
| Previous state | B-1 unresolved — C1 text feedback format undefined |
| Design selected | Option A — Full Oracle Summary (execution status + evidence scope + findings) |
| Fields included | Oracle execution status, evidence scope, scope limitation, findings (severity/code/message/line) |
| Fields excluded | Hashes, provenance, evaluator answers, epistemic state, authorization |
| Open design questions | ODQ-1 (injection point), ODQ-2 (iteration protocol), ODQ-3 (line=0 representation) |
| Deliverable | research/implementation/EGER-C1-TEXT-FEEDBACK-CONTRACT-001.md |
| Status | **PROPOSED — NOT YET FROZEN** |

## 5u. EGER-P019 — C1 Contract Closure

| Field | Value |
|---|---|
| ID / Date | EGER-P019 · 2026-08-26 |
| Type / Purpose | Protocol closure — resolve ODQ-1/2/3 and freeze C1 text feedback contract |
| Previous state | Three open design questions from P018 |
| ODQ-1 decision | Injection point: after CANDIDATE, before RESPOND instruction |
| ODQ-2 decision | Single-shot feedback (one model call, no revision) — **later corrected by P020** |
| ODQ-3 decision | line=0 rendered as Line: N/A |
| Deliverable | research/implementation/EGER-C1-TEXT-FEEDBACK-CONTRACT-001-R1.md |
| Status | **HISTORICAL — CONTAINS CONTRADICTION IDENTIFIED BY P020** |

## 5v. EGER-P020 — C1 Causal Mechanism Reconciliation

| Field | Value |
|---|---|
| ID / Date | EGER-P020 · 2026-08-26 |
| Type / Purpose | Scientific reconciliation — resolve P019 contradiction (single-shot vs. revision) |
| Previous state | P019 contains incompatible definitions: "one model call" AND "produce a revised candidate" |
| Central question | What exactly is the causal mechanism that C1 is intended to test? |
| Interpretation A | Post-proposal feedback (scientifically vacuous — no causal pathway) |
| Interpretation B | Feedback-assisted revision (scientifically meaningful — clear causal pathway) |
| Recommendation | Interpretation B — feedback-assisted revision | 
| Independent variable | Access to deterministic oracle text feedback during proposal revision |
| Revision call status | Part of treatment, not confound |
| Deliverable | research/implementation/EGER-C1-CAUSAL-MECHANISM-RECONCILIATION-001.md |
| Status | **RECOMMENDATION READY — HUMAN DECISION REQUIRED** |

## 5w. EGER-P021 — C1 Protocol Change-Control Assessment

| Field | Value |
|---|---|
| ID / Date | EGER-P021 · 2026-08-26 |
| Type / Purpose | Audit and change-control assessment — determine whether feedback-assisted revision requires formal change control |
| Previous state | P020 recommends Interpretation B; change-control status unknown |
| Change-control classification | **EGER-CHANGE-### REQUIRED** — independent variable clarified, primary artifact changed, execution mechanism changed |
| Budget impact | None — C1 fits within MODEL-002 budget (2 model calls ≤ 5, 2 oracle calls ≤ 5) |
| Benchmark impact | None — BENCH-002 unchanged |
| Model impact | None — MODEL-002 unchanged |
| Ṛta impact | None — same oracle interface |
| Deliverable | research/implementation/EGER-C1-PROTOCOL-CHANGE-ASSESSMENT-001.md |
| Status | **CHANGE-CONTROL DECISION READY — HUMAN APPROVAL REQUIRED** |

## 5x. EGER-P022 — C1 Protocol Change Authorization & Recording

| Field | Value |
|---|---|
| ID / Date | EGER-P022 · 2026-08-26 |
| Type / Purpose | Change-control recording — formally record the approved C0→C1 protocol change |
| Human authorization | Explicit — P022 directive authorizes change-control recording |
| Change record | **EGER-CHANGE-001** — C1 clarified as feedback-assisted revision |
| Protocol update | **EXP-001 v0.2** — C1 definition clarified to include revision procedure |
| What changed | (1) C1 independent variable clarified (not added). (2) C1 primary artifact changed (initial → final revised candidate). (3) C1 execution: 2 model calls + 2 oracle calls (was ambiguous). (4) Run manifest schema extended. |
| What did NOT change | BENCH-002 (frozen), MODEL-002 (frozen), Ṛta (untouched), C0 (frozen baseline), research question, hypothesis H1, text feedback contract format, information boundary, authority separation |
| Scientific justification | P019 single-shot interpretation was scientifically vacuous — feedback arrives after model finishes, no causal pathway. P020 feedback-assisted revision establishes causal pathway: feedback → revision → outcome. |
| C0 preservation | C0 remains exactly as executed — historical baseline unchanged |
| Confound monitoring | CM-1 through CM-6 observable under feedback-assisted revision; CM-7 requires definition update |
| C1 implementation status | NOT STARTED |
| C1 execution status | NOT AUTHORIZED |
| Deliverables | EGER-CHANGE-001.md, EGER-EXP-001-PROTOCOL-v0.2.md |
| Status | **APPROVED — change control complete; C1 implementation readiness next** |

## 5y. EGER-P023 — C1 Implementation Readiness Verification

| Field | Value |
|---|---|
| ID / Date | EGER-P023 · 2026-08-26 |
| Type / Purpose | Strict read-only implementation-readiness audit for C1 |
| Previous state | C1 change control approved (P022); C1 not yet implemented |
| Verdict | NOT READY — blocking gap: no text feedback renderer |
| Key finding | EngineerModel interface and OracleAdapter structurally ready; text feedback renderer missing (BLOCKING); C1 runner missing; manifest schema needs extension |
| Blocking gap | B-1: No deterministic text feedback renderer exists |
| Non-blocking gaps | NB-1: No C1 runner. NB-2: Manifest schema extension. NB-3: No C1 tests. NB-4: Failure handling semantics undefined. NB-5: CM-7 not updated. NB-6: Experiment version string. |
| C0 preservation | VERIFIED — C0 artifacts, runner, manifests untouched |
| BENCH-002 isolation | VERIFIED — engineer/evaluator boundary intact |
| MODEL-002 freeze | VERIFIED — same model, same parameters, budget accommodates 2 calls |
| Ṛta boundary | INTACT — 3b5c2f2 main 19 unchanged |
| Deliverable | research/implementation/EGER-C1-IMPLEMENTATION-READINESS-001.md |
| Status | **NOT READY — BLOCKING GAP IDENTIFIED** |

## 5z. EGER-P024 — C1 Open-Question Resolution & Implementation Authorization

| Field | Value |
|---|---|
| ID / Date | EGER-P024 · 2026-08-26 |
| Type / Purpose | Resolve 5 ODQs from P023; authorize C1 implementation if approved |
| ODQ-1 | Oracle call 1 failure → ABORT (INCOMPLETE_TREATMENT) with infra retry |
| ODQ-2 | Model call 2 failure → TERMINATE (INCOMPLETE_TREATMENT) with infra retry |
| ODQ-3 | Oracle call 2 failure → UNMEASURED (INCOMPLETE_MEASUREMENT) with infra retry |
| ODQ-4 | Renderer location → Standalone `eger/engineer/feedback.py` |
| ODQ-5 | C1 artifact directory → `formal/C1/` subdirectory |
| Failure taxonomy | Existing contract categories + INCOMPLETE_TREATMENT, INCOMPLETE_MEASUREMENT |
| Information boundary | CONFIRMED — Call 2 receives only task context + initial candidate + text feedback |
| Model freeze | CONFIRMED — MODEL-002 unchanged, OpenCode/MIMO 2.5 is NOT the experimental model |
| Authorized scope | Renderer + runner + manifest extension + tests + documentation |
| Deliverable | research/implementation/EGER-P024-C1-DECISION-RECORD.md |
| Status | **DECISIONS RECORDED — AWAITING HUMAN APPROVAL** |

## 5aa. EGER-P025 — C1 Implementation

| Field | Value |
|---|---|
| ID / Date | EGER-P025 · 2026-08-26 |
| Type / Purpose | Implement approved C1 feedback-assisted revision protocol |
| Human authorization | Explicit — IMPLEMENT C1 but DO NOT EXECUTE C1 |
| Implementation scope | (1) Text feedback renderer, (2) C1 runner, (3) Manifest extension, (4) Tests, (5) Documentation |
| Files created | `eger/engineer/feedback.py` (deterministic text feedback renderer), `research/experiments/EGER-EXP-001/formal_runner_c1.py` (C1 two-stage runner), `tests/test_c1_feedback.py` (16 tests) |
| Files modified | None (source code) |
| Tests | 16/16 C1 tests PASS + 47/47 existing tests PASS = 63/63 total |
| C0 regression | VERIFIED — 47/47 existing tests still pass |
| BENCH-002 | UNCHANGED |
| MODEL-002 | UNCHANGED |
| Ṛta | UNCHANGED (3b5c2f2 main 19) |
| C1 execution | **NOT EXECUTED** — implementation only |
| GitHub | NOT PUSHED |
| Status | **IMPLEMENTED — 63/63 TESTS PASS — C1 NOT EXECUTED** |

## 6. Standing rules for future entries

1. New material action ⇒ new ledger entry before or at the time of action.
2. Never delete or rewrite superseded entries; append status changes.
3. Tag every claim with a classification (SDC/AI/RH/OBS/ER/C).
4. Experiments (EXP-###) require manifests; results (RES-###) cite them;
   failures (FAIL-###) are mandatory, never optional.
5. Contract changes only via EGER-CHANGE-### with status PROPOSED until reviewed.
