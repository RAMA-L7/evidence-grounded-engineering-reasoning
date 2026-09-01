# EGER-P145 — Architecture Validation / System-Level Review

## Gate

P145 — Strict Read-Only Validation

## Date

2026-09-01

## Scope

Validate the implemented EGER architecture (P138–P144) against the evidence-grounded design (P136–P137). Determine whether the code realizes the architecture as designed.

**No production code modified. No live model calls. No experiments. No historical artifacts changed.**

---

## 1. Architecture Under Review

```
TaskDefinition (P138)
       ↓
PromptBuilder (P140)
       ↓
ProposalGenerator (LLM — external)
       ↓
CandidateArtifact (P138)
       ↓
OracleAdapter (deterministic — external)
       ↓
EvidenceNormalizer (P139)
       ↓
EvidenceArtifact (P138)
       ↓
RevisionController (P141)
       ↓
Final Candidate + Evidence
       ↓
VerificationGate (P142) — SOLE acceptance authority
       ↓
VerificationResult (P138)
       ↓
ProvenanceTracker (P143) — complete audit trail
```

---

## 2. Component-by-Component Validation

### Transition Matrix

| Transition | Input | Output | Authority | Contract | Failure | Tests |
|-----------|-------|--------|-----------|----------|---------|-------|
| Task → Prompt | TaskDefinition | PromptRequest | PromptBuilder | P138 PromptRequest | Empty task → error | ✅ 32 tests |
| Prompt → Proposal | PromptRequest | raw output | LLM | External | Timeout/error → INCOMPLETE | ✅ 17 tests |
| Proposal → Candidate | raw output | CandidateArtifact | build_candidate | P138 CandidateArtifact | Malformed → None | ✅ 25 tests |
| Candidate → Oracle | CandidateArtifact | Oracle result | OracleAdapter | External | Failure → failure evidence | ✅ 29 tests |
| Oracle → Evidence | Oracle result | EvidenceArtifact | EvidenceNormalizer | P138 EvidenceArtifact | Unknown severity → FAIL CLOSED | ✅ 29 tests |
| Evidence → Revision | EvidenceArtifact + CandidateArtifact | RunRecord | RevisionController | P138 RunRecord | Budget exhausted → terminal | ✅ 25 tests |
| Candidate+Evidence → Decision | CandidateArtifact + EvidenceArtifact | VerificationResult | VerificationGate | P138 VerificationResult | Missing/fail → REJECT | ✅ 30 tests |
| Run → Provenance | All artifacts | Provenance | ProvenanceTracker | Append-only trail | Missing artifact → incomplete | ✅ 25 tests |

---

## 3. Authority Boundary Audit

### Programmatic Search Results

Searched all production code under `eger/` for decision-making strings:

| String | Production files containing | Classification |
|--------|---------------------------|----------------|
| `"ACCEPT"` | `eger/verification/gate.py` (2 occurrences) | ✅ Sole authority — correct |
| `"ACCEPT"` | `eger/verification/result.py` (1 occurrence) | ✅ Contract definition — correct |
| `"REJECT"` | `eger/verification/gate.py` (2 occurrences) | ✅ Sole authority — correct |
| `"REJECT"` | `eger/verification/result.py` (1 occurrence) | ✅ Contract definition — correct |
| `"VERIFIED"` | None in production code | ✅ No bypass |
| `"AUTHORIZED"` | None in production code | ✅ No bypass |
| `"APPROVED"` | `eger/authorization/gate.py` (2 occurrences) | ✅ Deferred C5 — not imported by core |

### Authority Summary

| Component | Expected Authority | Actual | Status |
|-----------|-------------------|--------|--------|
| TaskDefinition | Defines task | Defines task | ✅ |
| PromptBuilder | Constructs prompts | Constructs prompts | ✅ |
| LLM | Generates proposals | Generates proposals | ✅ |
| CandidateArtifact | Records proposal | Records proposal | ✅ |
| Oracle | Produces evidence | Produces evidence | ✅ |
| EvidenceNormalizer | Translates evidence | Translates evidence | ✅ |
| RevisionController | Orchestrates revision | Orchestrates revision | ✅ |
| **VerificationGate** | **Sole ACCEPT/REJECT** | **Sole ACCEPT/REJECT** | ✅ |
| ProvenanceTracker | Records history | Records history | ✅ |
| Pipeline | Composition only | Composition only | ✅ |

**No authority violations found.**

---

## 4. Verification Authority

Proved that VerificationGate is the sole component converting Candidate+Evidence into ACCEPT/REJECT.

**Bypass check results:**

| Potential bypass | Found in production code? | Status |
|-----------------|--------------------------|--------|
| LLM → ACCEPT | No | ✅ |
| Oracle → ACCEPT | No | ✅ |
| RevisionController → ACCEPT | No (defaults to REJECTED) | ✅ |
| Pipeline → ACCEPT | No | ✅ |
| CandidateArtifact → ACCEPT | No (verified field exists but gate doesn't trust it) | ✅ |
| ProvenanceTracker → ACCEPT | No | ✅ |
| AuthorizationGate → ACCEPT | Yes (eger/authorization/gate.py) | ✅ Deferred, not imported by core |

---

## 5. Evidence Authority

Verified that:

- LLM output → CandidateArtifact (proposal)
- Oracle result → EvidenceArtifact (evidence)
- LLM cannot manufacture EvidenceArtifact
- EvidenceNormalizer is deterministic transformation only
- No code path allows LLM to inject findings

---

## 6. Fail-Closed Audit

| Condition | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Missing candidate + missing evidence | REJECT | REJECT | ✅ |
| Missing evidence | REJECT | REJECT | ✅ |
| Oracle failure evidence | REJECT | REJECT | ✅ |
| ERROR findings present | REJECT | REJECT | ✅ |
| Zero ERROR findings, valid evidence | ACCEPT | ACCEPT | ✅ |
| Unsupported evidence scope | REJECT | REJECT | ✅ |
| Unknown oracle status | REJECT | REJECT | ✅ |
| Model timeout | INCOMPLETE | INCOMPLETE | ✅ |
| Budget exhaustion | Terminal non-success | Terminal non-success | ✅ |

**No false acceptance paths found.**

---

## 7. Revision Loop Audit

Verified:
- Every revision is based on Oracle evidence
- Candidate history is preserved (append-only)
- Evidence history is preserved (append-only)
- Iteration numbers are consistent
- Budget limits are enforced (max_iterations, max_total_calls)
- Infinite revision is impossible (bounded by config)
- RevisionController does NOT independently accept candidates

### Orchestration Duplication

The `EGERPipeline._run_with_tracking` duplicates the revision loop logic from `RevisionController.run()`. Both implement the same generate→evaluate→revise flow independently.

**Classification: MINOR ARCHITECTURAL DEBT**

- Not a blocker: both produce correct results
- The pipeline's version adds provenance tracking around the loop
- The RevisionController's version is the canonical implementation
- The duplication doesn't affect correctness or authority boundaries
- Future cleanup: pipeline should delegate to RevisionController directly

---

## 8. Provenance Audit

Verified complete event chain for a 2-iteration run:

```
RUN_STARTED
    ↓
PROMPT_CREATED (iteration 0)
    ↓
CANDIDATE_CREATED (iteration 0)
    ↓
ORACLE_EVALUATED (iteration 0)
    ↓
EVIDENCE_RECORDED (iteration 0)
    ↓
PROMPT_CREATED (iteration 1)
    ↓
CANDIDATE_CREATED (iteration 1)
    ↓
ORACLE_EVALUATED (iteration 1)
    ↓
EVIDENCE_RECORDED (iteration 1)
    ↓
VERIFICATION_COMPLETED
    ↓
RUN_COMPLETED
```

Verified:
- run ID consistency across all events
- candidate → prompt relationships preserved
- candidate → Oracle evaluation relationships preserved
- Oracle evaluation → evidence relationships preserved
- revision ordering preserved
- terminal state recorded
- full reconstruction from run_id possible

**Provenance classification: COMPLETE**

---

## 9. Determinism Audit

| Component | Deterministic? | Evidence |
|-----------|---------------|----------|
| TaskDefinition | Yes (frozen) | Same input → same hash |
| PromptBuilder | Yes | Same inputs → same prompt_hash |
| EvidenceNormalizer | Yes | Same Oracle input → same EvidenceArtifact |
| VerificationGate | Yes | Same inputs → same decision |
| ProvenanceTracker | Yes | Same events → same reconstruction |
| CandidateArtifact | Yes | Same SDC → same candidate_hash |

**All deterministic components produce equivalent outputs for identical inputs.**

---

## 10. Immutability Audit

| Contract | Frozen? | Can mutate? | Status |
|----------|---------|------------|--------|
| TaskDefinition | Yes | No | ✅ PASS |
| Finding | Yes | No | ✅ PASS |
| EvidenceArtifact | Yes | No | ✅ PASS |
| PromptRequest | Yes | No | ✅ PASS |
| VerificationResult | Yes | No | ✅ PASS |
| RevisionConfig | Yes | No | ✅ PASS |
| RunRecord | Yes | No | ✅ PASS |
| CandidateArtifact | No (dataclass) | `verified` can be set | ⚠️ MINOR DEBT |

### CandidateArtifact Immutability Concern

`CandidateArtifact` is not a frozen dataclass. The `verified` field can be set to True externally. However:
- VerificationGate does NOT check `candidate.verified`
- VerificationGate makes its own decision from evidence
- No component promotes candidates based on `verified` field
- The gate's test explicitly verifies "unverified candidate accepted" when evidence is clean

**Classification: MINOR DEBT — no impact on correctness**

---

## 11. Provenance + Immutability Interaction

Verified that artifact hashes and recorded references remain stable:
- CandidateArtifact hashes are content-based (SHA256 of SDC text)
- EvidenceArtifact hashes are content-based
- Provenance records reference artifacts by ID, not by mutable state
- No code path modifies an artifact after provenance records its reference

---

## 12. Prompt Boundary Audit

Verified that PromptBuilder produces prompts containing:
- Task identity, context, objective
- Task constraints
- Current candidate (revision only)
- Evidence (revision only)
- Instructions

Verified that prompts do NOT contain:
- `ACCEPT` (tested: test_prompt_builder.py T234)
- `REJECT` (tested: test_prompt_builder.py T235)
- `AUTHORIZED` (tested: test_prompt_builder.py T236)

**LLM remains proposal authority only.**

---

## 13. Oracle Boundary Audit

Verified that Oracle produces evidence, not decisions:
- OracleAdapter.validate() → OracleResult (is_success + evidence/failure)
- Oracle does not produce ACCEPT/REJECT
- VerificationGate consumes evidence independently
- No code path allows Oracle to bypass VerificationGate

---

## 14. C0–C5 Reconciliation

| Stage | Research Status | Implementation Status | Consistent? |
|-------|----------------|----------------------|-------------|
| C0 | ESTABLISHED | Not in core pipeline (historical) | ✅ |
| C1 | ESTABLISHED | Structured evidence pipeline implemented | ✅ |
| C2 | PARTIALLY SUPPORTED | Evidence normalization implemented | ✅ |
| C3 | NOT JUSTIFIED | Excluded from core architecture | ✅ |
| C4 | DEFERRED | Not implemented (engineering choice) | ✅ |
| C5 | DEFERRED | Authorization gate exists but not imported by core | ✅ |

**IMPLEMENTATION CONSISTENT with research state.**

---

## 15. RQ-4 Boundary

The implementation uses broad/production-quality framing (TaskDefinition.objective) as an engineering default. This is consistent with the empirically supported signal from DIAGNOSTIC-009.

The code does NOT encode the claim "broad framing causes adherence" as a proven mechanism. It uses broad framing as a configuration choice supported by evidence.

**IMPLEMENTATION CONSISTENT with RQ-4 closure.**

---

## 16. Security Audit

| Scan | Result |
|------|--------|
| API keys in production code | NONE |
| Credentials in production code | NONE |
| `.env` files in production code | NONE |
| Private keys in production code | NONE |
| False positives | `os.environ.copy()` in oracle/adapter.py (read-only env access) |

**No real credentials found.**

---

## 17. Test Results

```
Previous baseline: 535 tests
Current total: 535 tests
New failures: 0
```

All 535 tests pass. No tests were modified to make the architecture pass.

---

## 18. Dependency Audit

### Import Graph (production code only)

```
eger.task.definition          → (none)
eger.evidence.schemas         → (none)
eger.prompting.request        → (none)
eger.revision.record          → (none)
eger.verification.result      → (none)
eger.provenance.tracker       → (none)
eger.engineer.candidate       → (none)

eger.prompting.builder        → task.definition, evidence.schemas, engineer.candidate
eger.evidence.normalizer      → evidence.schemas
eger.revision.controller      → task.definition, evidence.schemas, engineer.candidate,
                                 prompting.builder, prompting.request, evidence.normalizer
eger.verification.gate        → engineer.candidate, evidence.schemas

eger.pipeline.e2e             → task.definition, prompting.builder, evidence.normalizer,
                                 revision.controller, verification.gate, verification.result,
                                 provenance.tracker, revision.record, engineer.candidate,
                                 evidence.schemas
```

### Checks

| Check | Result |
|-------|--------|
| Circular dependencies | NONE |
| Lower-level → pipeline imports | NONE |
| VerificationGate → LLM imports | NONE |
| Authority inversion | NONE |
| Deferred modules imported by core | NONE |

---

## 19. Architectural Quality Classification

| Property | Classification |
|----------|---------------|
| Component separation | PASS |
| Authority separation | PASS |
| Deterministic evidence | PASS |
| Fail-closed behavior | PASS |
| Revision control | PASS |
| Verification isolation | PASS |
| Provenance completeness | PASS |
| Immutability | PASS WITH MINOR DEBT (CandidateArtifact) |
| Prompt boundary | PASS |
| Oracle boundary | PASS |
| Dependency structure | PASS |
| Testability | PASS |
| Reproducibility | PASS |
| Historical compatibility | PASS |

### Architectural Debt

1. **CandidateArtifact not frozen** — `verified` field is mutable. Gate doesn't trust it, so no correctness impact. Future: consider making frozen.

2. **Pipeline/Controller duplication** — `EGERPipeline._run_with_tracking` duplicates `RevisionController.run()`. Both produce correct results. Future: pipeline should delegate to controller.

---

## 20. Critical Question

> **If the LLM disappeared tomorrow, which parts of EGER would still remain deterministic and trustworthy?**

| Category | Components | Deterministic? |
|----------|-----------|---------------|
| **Fully deterministic** | TaskDefinition, PromptRequest, EvidenceArtifact, Finding, VerificationResult, RunRecord, RevisionConfig | Yes — pure data contracts |
| **Deterministic logic** | PromptBuilder, EvidenceNormalizer, VerificationGate, ProvenanceTracker, RevisionController | Yes — no randomness, no external calls |
| **External/deterministic** | OracleAdapter (deterministic local Oracle) | Yes — deterministic verification |
| **Probabilistic** | LLM proposal generation | No — stochastic by design |

**The entire EGER infrastructure except the LLM proposal layer is deterministic and trustworthy.** The LLM is the single point of nondeterminism. All verification, evidence, provenance, and acceptance logic operates independently of the model.

---

## 21. Final Verdict

### **B — VALIDATED WITH MINOR DEBT**

The EGER architecture is internally coherent, deterministic, auditable, and faithful to the evidence-grounded design established through P136–P144.

**Minor debt items (non-blocking):**
1. CandidateArtifact `verified` field is mutable (gate doesn't trust it)
2. Pipeline duplicates RevisionController orchestration logic

**No blockers. No authority violations. No false acceptance paths.**

---

```
P145 COMPLETE
EGER ARCHITECTURE VALIDATION COMPLETE

VERDICT: B — VALIDATED WITH MINOR DEBT

PRODUCTION CODE MODIFIED: NO
LIVE MODEL CALLS: NO
EXPERIMENT EXECUTED: NO
HISTORICAL ARTIFACTS MODIFIED: NO

AUTHORITY BOUNDARIES: PASS
EVIDENCE BOUNDARY: PASS
FAIL-CLOSED BEHAVIOR: PASS
REVISION CONTROL: PASS
VERIFICATION ISOLATION: PASS
PROVENANCE: COMPLETE
DETERMINISM: PASS
IMMUTABILITY: PASS WITH MINOR DEBT

C0: ESTABLISHED
C1: ESTABLISHED
C2: PARTIALLY SUPPORTED
C3: NOT JUSTIFIED
C4: DEFERRED
C5: DEFERRED

RQ-4: CLOSED

ARCHITECTURAL DEBT:
1. CandidateArtifact verified field mutable
2. Pipeline/Controller orchestration duplication

NEXT GATE:
P146 — Git Checkpoint + Architecture Debt Cleanup (optional)
or
P146 — Engineering Documentation / Usage Guide
```
