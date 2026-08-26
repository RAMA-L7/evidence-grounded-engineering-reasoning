# EGER-P010 — LLM Proposal Authority Integration

| Field | Value |
|---|---|
| ID | EGER-P010 |
| Title | Single Probabilistic LLM Engineer — Proposal Authority Integration |
| Previous | P009 (L2/L3 deterministic, bb9025d, 31/31 PASS) |
| Contracts | EGER-ORACLE-CONTRACT-001, EGER-SCHEMA-001, EGER-EPISTEMIC-001 (L2/L3 schemas) |
| Deterministic base | L1 EvidenceOracle, L2 EpistemicEngine, L3 AuthorizationGate — all frozen, all PASS |
| Scope | Exactly **one** probabilistic component, proposal authority only |
| Status | PASS — 16/16 P010 + 31/31 regression = 47/47 overall |

## 1. Mission

Introduce the first and only probabilistic component — **EGER Engineer** — strictly as **Proposal Authority** on top of the proven L1/L2/L3 deterministic stack (`Candidate → L1 → L2 → L3`). The LLM may interpret context and generate/revise candidates, but may not declare validation, establish evidence, mutate epistemic state, authorize commits, bypass any layer, invoke generation tooling, or modify Ṛta / the research contract. P010 is an integration gate, not a C0–C5 experiment.

## 2. Architecture

```
              ┌─────────────────────┐
              │  EGER Engineer LLM  │  ← exactly one, proposal only
              │  (FakeEngineerModel │
              │   or replaceable    │
              │   provider)         │
              └──────────┬──────────┘
                         │ CandidateArtifact (unverified)
                         ▼
              ┌─────────────────────┐
              │ L1 EvidenceOracle   │  deterministic (P008)
              └──────────┬──────────┘
                         │ EvidenceArtifact
                         ▼
              ┌─────────────────────┐
              │ L2 EpistemicEngine  │  deterministic (P009)
              └──────────┬──────────┘
                         │ EpistemicState
                         ▼
              ┌─────────────────────┐
              │ L3 AuthorizationGate│  deterministic (P009)
              └─────────────────────┘
```

No direct paths exist from Engineer to L2/L3/Ṛta generation/research memory.

## 3. Authority Separation

- **PROPOSAL** = Engineer (LLM) only
- **EVIDENCE** = L1 EvidenceOracle only
- **EPISTEMIC** = L2 EpistemicEngine only
- **AUTHORIZATION** = L3 AuthorizationGate only

All four separately typed, separately tested, no inheritance. Hard programmatic boundaries, not prompts. Verified by T-P010-003/004/005/006/011.

## 4. Engineer Interface

Abstract base `EngineerModel` with `generate(prompt) -> ModelResponse` and `describe() -> {provider, model, model_version}`. Concrete `FakeEngineerModel` (deterministic, no network) drives the P010 gate; any future provider (Anthropic, OpenAI, etc.) implements the same interface — L1/L2/L3 need not change (experimental isolation). The interface lives in `eger/engineer/model.py`.

## 5. Model Adapter

`EngineerAdapter` (`eger/engineer/adapter.py`) isolates invocation from scientific protocol:

- **Responsible for:** prompt construction (versioned `eger.prompt.v1`), model invocation, response capture, deterministic candidate extraction, model metadata preservation, failure typing.
- **NOT responsible for:** validation, evidence interpretation as truth, epistemic transitions, authorization.
- **Capabilities surface:** `capabilities() -> {role: proposal, model: describe(), prompt_version, schema_version, forbidden_authorities}` — explicit negative claims.

## 6. CandidateArtifact

Typed per `eger.candidate.v1` (`eger/engineer/candidate.py`):

`{artifact_id: EGER-CAND-<hash[:12]>, sdc_text, input_hash (=candidate_hash = SHA256(sdc_text)), provision{provider, model, prompt_hash, output_hash}, schema_version, created_at, verified: false}`

`verified: false` is the FROZEN invariant — candidate is **unverified** until L1 evidence exists. Candidate hash is semantic (sdc_text), distinct from prompt and raw-output hashes.

## 7. Prompt Protocol

- System instructions (frozen `eger.prompt.v1`): neutral proposal prompt requesting SDC inside ```sdc fences, explicitly "do not claim validated."
- Inputs: `design_context`, `existing_sdc`, `objective`, `evidence_summary` (read-only), `epistemic_state` (read-only) — minimal per P010 §14, no ledger/STATE dump.
- Output: `build_prompt(...) -> (prompt, prompt_hash)` deterministically; `prompt_hash` retained for provenance and versioned as `PROMPT_VERSION`.

No C0–C5-specific prompt differences in P010 (neutral prompt only).

## 8. Output Extraction

Deterministic, side-effect free, no LLM (`eger/engineer/candidate.py`):

1. Extract ```sdc / ```tcl fenced block if present and contains SDC keywords
2. Else scan lines for SDC keywords (`create_clock`, `set_input_delay`, etc.)
3. Fallback: raw output itself if it contains keywords
4. Otherwise `None` → `MALFORMED_OUTPUT`

No heuristic repair, no second LLM, no Ṛta generation fallback, no semantic guessing. Verified T-P010-007 determinism (same raw → same sdc_text → same hash).

## 9. Failure Model

Typed **PROPOSAL_FAILURE** — distinct from `ORACLE_FAILURE` / `ENGINEERING_INVALID`:

- `TIMEOUT` (TimeoutError from model)
- `PROVIDER_ERROR` (RuntimeError from model)
- `MODEL_UNAVAILABLE` (catch-all Exception)
- `MALFORMED_OUTPUT` (no extractable SDC)
- `MISSING_CANDIDATE` (future)

`ProposalResult = Success(CandidateArtifact + ModelResponse) | Failure(ProposalFailure)` — same union discipline as OracleResult.

## 10. Provenance

Per P010 §20/22, every proposal carries:

- `provider`, `model`, `model_version`, `sampling_params`, `request_id` (when supplied), `prompt_hash`, `prompt_version`, `output_hash`, `produced_at` (in `ModelResponse`)
- Mirrored into `CandidateArtifact.provision` for traceability (`prompt_hash`, `output_hash`, `candidate_hash` kept separate)

No secrets captured. Volatile metadata (timestamps) excluded from candidate semantic hash.

## 11. Hash Model

Three hashes strictly separated:

- `prompt_hash = SHA256(prompt)` — proves input context
- `output_hash = SHA256(raw_output)` — proves raw model output
- `candidate_hash (=input_hash) = SHA256(sdc_text)` — proves semantic candidate identity

T-P010-014 verifies: same output → same candidate_hash; candidate_hash ≠ prompt_hash; volatile metadata does not alter semantic identity.

## 12. Tests

| ID | Description |
|---|---|
| T-P010-001 | model adapter returns typed CandidateArtifact |
| T-P010-002 | candidate explicitly unverified before L1 |
| T-P010-003 | model cannot create EvidenceArtifact |
| T-P010-004 | model cannot mutate EpistemicState |
| T-P010-005 | model cannot authorize |
| T-P010-006 | correct pipeline CandidateArtifact → L1 → EvidenceArtifact |
| T-P010-007 | deterministic extraction (same raw → same candidate) |
| T-P010-008 | malformed output → PROPOSAL_FAILURE, no side effects |
| T-P010-009 | model failures typed as PROPOSAL_FAILURE |
| T-P010-010 | `rta_generate` unreachable (static/interface) |
| T-P010-011 | L1/L2/L3 immutable by model output alone |
| T-P010-012 | two-memory separation (engineer ∤ research ledger) |
| T-P010-013 | model provenance recorded |
| T-P010-014 | output/candidate/prompt hashes separated and deterministic |
| T-P010-015 | P008 regression 14/14 |
| T-P010-016 | P009 regression 17/17 |

## 13. Results

- **16/16 P010 PASS**
- **14/14 P008 regression PASS** (via subprocess invocation in T-P010-015)
- **17/17 P009 regression PASS** (via subprocess in T-P010-016)
- **47/47 total PASS**
- No subagents, no multi-agent orchestration; exactly one `FakeEngineerModel` instance per test.

## 14. P008 Regression

Verified inside `test_T_P010_015_p008_regression`: `pytest tests/test_evidence_oracle.py -q` → `14 passed`.

## 15. P009 Regression

Verified inside `test_T_P010_016_p009_regression`: `pytest tests/test_epistemic_authorization.py -q` → `17 passed`.

## 16. Security Boundary

- Engineering input treated as untrusted content; output is constrained to typed `CandidateArtifact` via deterministic parser.
- Engineer has no: arbitrary shell, arbitrary filesystem, Ṛta source write, Git write.
- Tool use occurs through typed interfaces (`EngineerModel.generate`, `EvidenceOracle.validate`, etc.) — never through free-form tool commands.
- Research memory write path does not exist on Engineer.

## 17. Two-Memories Verification

- **Research Memory** (`research/RESEARCH_LEDGER.md`, `research/STATE.md`) — version-controlled history of EGER decisions.
- **Engineering Memory** (`EpistemicClaim`, `EvidenceArtifact`, `AuthorizationDecision`, `CandidateArtifact`) — state of the engineering artifact.
- T-P010-012 proves: candidate `artifact_id` / `sdc_text` never appears in ledger; adapter has no `write_ledger`/`update_research_memory`; ledger content never appears in engine's claim map.

## 18. Model-Selection Status

**Experimental model NOT frozen (NO).**

P010 implements a provider-neutral interface. The concrete `FakeEngineerModel` is a deterministic stand-in for the scientific control — the P010 gate **must** pass without a live model (and does). Live-model smoke testing remains strictly **optional** per P010 §48 and is NOT an experimental result.

Actual model/provider/version/sampling freeze belongs to the experimental preparation gate (P011). Recorded as `implementation choice / NOT EXPERIMENTAL FREEZE`.

## 19. Known Limitations

- Real LLM nondeterminism expected; P010 does not claim deterministic LLM output — only deterministic infrastructure + deterministic extraction.
- Evidence feedback loop (`EvidenceArtifact → Engineer → new Candidate`) is permitted architecturally but not optimized or measured as convergence in P010.
- Prompt template is neutral and not tuned; C0–C5 prompts will be explicit experimental conditions later.
- Optional live-model path exists only if a verifier configures it; no network dependency for the gate.

## 20. Remaining UNKNOWNs

- Which provider/model/sampling parameters will be frozen for C0–C5 (P011).
- Benchmark corpus selection and run-manifest freeze (P011).
- Whether prompt wording materially affects proposal quality (explicitly deferred to experiment).
- Larger prompt-context tradeoffs (evidence + epistemic read-only views) under token constraints.

## 21. Deviations

**NONE.** No `EGER-CHANGE-###` required. No contract modification, no `rta_generate` exposure, no additional probabilistic component, no C0–C5 implementation, no OpenCode subagent creation.

## 22. P010 Status

**PASS**

All §60 criteria satisfied: exactly one probabilistic component with proposal-only authority, replaceable model, typed unverified candidate, evidence/epistemic/authorization boundaries intact, `rta_generate` unreachable, no direct Engineer→Ṛta/L2/L3, failures as `PROPOSAL_FAILURE`, deterministic extraction, provenance/hashes separated, research memory protected, regressions 47/47, Ṛta untouched, contract unchanged, no C0–C5/C6.

*Implementation validated against the P010 test suite under the tested conditions — the phrase “now proven” refers to this suite, not to empirical reliability claims about EGER (none made).*
