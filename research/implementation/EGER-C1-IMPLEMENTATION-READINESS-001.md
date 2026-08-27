# EGER-C1-IMPLEMENTATION-READINESS-001

| Field | Value |
|-------|-------|
| ID | EGER-C1-IMPLEMENTATION-READINESS-001 |
| Produced by | EGER-P023 (2026-08-26) |
| Type | Strict read-only implementation-readiness audit |
| Predecessor | EGER-CHANGE-001 (C1 protocol change-control approved) |
| Status | **NOT READY — implementation gaps exist** |

---

## 1. Executive Verdict

**NOT READY — one blocking implementation gap, several non-blocking gaps.**

The approved C1 protocol (feedback-assisted revision) requires a **deterministic text feedback renderer** that does not exist in the repository. This is a blocking gap: without it, C1 cannot execute the approved pipeline.

The existing `EngineerModel` interface, `OracleAdapter`, and `build_prompt()` method are structurally ready to support C1. The gaps are:
1. **BLOCKING:** No text feedback renderer
2. **NON-BLOCKING:** No C1 runner
3. **NON-BLOCKING:** Manifest schema not extended for C1
4. **NON-BLOCKING:** No C1-specific tests
5. **NON-BLOCKING:** Failure-handling semantics not defined for C1 two-stage pipeline

---

## 2. Current Implementation Inventory

| Component | File | Status | C1 Ready? |
|-----------|------|--------|-----------|
| EngineerModel | `eger/engineer/model.py` | IMPLEMENTED (P010) | YES — interface supports multiple calls |
| EngineerAdapter | `eger/engineer/adapter.py` | IMPLEMENTED (P010) | YES — `build_prompt()` accepts `evidence_summary` |
| CandidateArtifact | `eger/engineer/candidate.py` | IMPLEMENTED (P010) | YES — typed, deterministic extraction |
| EvidenceOracle | `eger/oracle/adapter.py` | IMPLEMENTED (P008) | YES — `validate()` callable multiple times |
| Oracle schemas | `eger/oracle/schemas.py` | IMPLEMENTED (P007) | YES — scope/findings/status frozen |
| EpistemicEngine | `eger/epistemic/transitions.py` | IMPLEMENTED (P009) | N/A — not active in C1 |
| AuthorizationGate | `eger/authorization/gate.py` | IMPLEMENTED (P009) | N/A — not active in C1 |
| Text feedback renderer | N/A | **NOT IMPLEMENTED** | **NO — BLOCKING GAP** |
| C0 runner | `research/experiments/EGER-EXP-001/formal_runner_c0.py` | IMPLEMENTED | N/A — C0 only |
| C1 runner | N/A | **NOT IMPLEMENTED** | **NO — REQUIRED** |
| C1 tests | N/A | **NOT IMPLEMENTED** | **NO — REQUIRED** |

---

## 3. C1 Pipeline Readiness Assessment

### Approved C1 Pipeline

```
LLM (call 1) → INITIAL CANDIDATE
ORACLE (call 1) → EvidenceArtifact
TEXT FEEDBACK → deterministic rendering
LLM (call 2) → REVISED CANDIDATE
ORACLE (call 2) → MEASUREMENT
```

### Step-by-Step Readiness

| Step | Component | Exists? | Ready? | Notes |
|------|-----------|---------|--------|-------|
| 1. LLM call 1 | `EngineerAdapter.propose()` | YES | YES | Same as C0 |
| 2. Preserve initial candidate | CandidateArtifact | YES | YES | `candidate.to_dict()` serializable |
| 3. Oracle call 1 | `EvidenceOracle.validate()` | YES | YES | Returns `OracleResult` with `EvidenceArtifact` |
| 4. Render text feedback | **MISSING** | **NO** | **NO** | **BLOCKING GAP** |
| 5. Build C1 prompt | `EngineerAdapter.build_prompt()` | YES | PARTIAL | `evidence_summary` param exists; needs C1-specific prompt template |
| 6. LLM call 2 | `EngineerAdapter.propose()` | YES | YES | Same interface, different prompt |
| 7. Preserve revised candidate | CandidateArtifact | YES | YES | Same as step 2 |
| 8. Oracle call 2 | `EvidenceOracle.validate()` | YES | YES | Same as step 3 |
| 9. Record all artifacts | Manifest | PARTIAL | NO | Schema needs extension |

---

## 4. EngineerModel Readiness

### Interface

```python
class EngineerModel:
    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        ...
```

### Assessment: **READY**

| Requirement | Status |
|-------------|--------|
| First proposal call | ✅ `adapter.propose()` works |
| Preservation of initial candidate | ✅ `ProposalResult.candidate` is a `CandidateArtifact` |
| Second call possible | ✅ `adapter.propose()` can be called again with different prompt |
| Initial candidate passed to second call | ✅ Can serialize `candidate.sdc_text` into prompt |
| Text feedback passed to second call | ✅ `build_prompt(evidence_summary=...)` accepts text |
| Revised candidate received | ✅ `ProposalResult.candidate` from second call |

### Key Evidence

`EngineerAdapter.build_prompt()` at line 58 of `eger/engineer/adapter.py`:

```python
def build_prompt(
    self,
    design_context: str = "",
    existing_sdc: str = "",
    objective: str = "",
    evidence_summary: Optional[str] = None,
    epistemic_state: Optional[str] = None,
) -> tuple[str, str]:
```

The `evidence_summary` parameter is designed to accept deterministic text. The `existing_sdc` parameter can accept the initial candidate. Both are included in the prompt with labels that do not imply validation.

### What Needs to Change

**Nothing in the interface.** The C1 runner will call `propose()` twice with different prompt constructions. The second call will use `existing_sdc=initial_candidate.sdc_text` and `evidence_summary=text_feedback`.

---

## 5. OracleAdapter Readiness

### Interface

```python
class EvidenceOracle:
    def validate(
        self,
        sdc_text: str,
        input_identity: str = "candidate",
        invocation_options: Optional[Dict[str, Any]] = None,
        evidence_store: Optional[Path] = None,
    ) -> OracleResult:
```

### Assessment: **READY**

| Requirement | Status |
|-------------|--------|
| First candidate evaluation | ✅ `oracle.validate(initial_candidate.sdc_text)` |
| Second candidate evaluation | ✅ `oracle.validate(revised_candidate.sdc_text)` |
| Preservation of both EvidenceArtifacts | ✅ `OracleResult.evidence` is typed `EvidenceArtifact` |
| Deterministic execution | ✅ Byte-identical for same input (verified T005, T006, T012) |
| No modification of Ṛta | ✅ Static grep: 0 hits for `rta_generate` in adapter (T009) |
| External oracle interface only | ✅ Invokes via `subprocess.run()` with cwd outside Ṛta |

### Key Properties

- `oracle.validate()` is stateless — can be called multiple times
- Each call produces independent `EvidenceArtifact` with distinct `artifact_id` and `evidence_hash`
- Raw evidence retention works via `evidence_store` parameter
- Exit code classification is deterministic (0/1 → SUCCESS, 2/3 → failure)

---

## 6. Text Feedback Renderer Readiness

### Assessment: **NOT IMPLEMENTED — BLOCKING GAP**

**No text feedback renderer exists in the repository.** Grep for `text_feedback`, `render_feedback`, `feedback_renderer` returns zero matches in `eger/`.

### Required Implementation

A new module (e.g., `eger/engineer/feedback.py`) implementing:

```python
def render_text_feedback(evidence: EvidenceArtifact) -> str:
    """Deterministic rendering of EvidenceArtifact to text feedback.
    
    Same input → same output, always.
    No LLM, no probabilistic component, no interpretation.
    """
```

### Required Semantic Content

Per the C1 Text Feedback Contract (EGER-C1-TEXT-FEEDBACK-CONTRACT-001-R1):

```
ORACLE RESULT
─────────────
Oracle execution: SUCCESS

EVIDENCE SCOPE
──────────────
Scope: INSUFFICIENT
Scope limitation: Netlist-dependent checks could not be evaluated.

FINDINGS
────────
[ERROR] SDC-005: No set_input_delay — all input ports are unconstrained. (Line: N/A)
[WARNING] SDC-030: No set_propagated_clock. (Line: N/A)
```

### Fields to Include

| Field | Source | Exposed? |
|-------|--------|----------|
| Oracle execution status | `evidence.oracle_status` | YES |
| Evidence scope | `evidence.evidence_scope` | YES |
| Scope limitation text | Derived from `evidence.analysis_scope` | YES |
| Findings (severity/code/message/line) | `evidence.findings` | YES |

### Fields to Exclude

| Field | Reason |
|-------|--------|
| Evidence hash | Audit metadata, not engineering feedback |
| Raw hash | Audit metadata |
| Input hash | Audit metadata |
| Provenance | Audit metadata |
| Epistemic state | C3 treatment |
| Authorization | C5 treatment |

### Deterministic Rendering Rules

| Rule | Specification |
|------|--------------|
| Finding order | Severity (ERROR → WARNING → INFO) → code (alphabetical) → source order |
| Line representation | `Line: N/A` if line == 0, else `Line: <number>` |
| Newline | `\n` (LF) |
| Whitespace | Minimal, consistent |
| Empty findings | Omit FINDINGS section entirely |
| Scope limitation | Include only if scope != FULL |

### Verification Requirements

- Same `EvidenceArtifact` → same text, always (determinism test)
- No `rta_generate` or oracle source references
- No evaluator-only data
- No epistemic state (VALIDATED/REFUTED/UNKNOWN)
- No authorization decisions (APPROVED/REJECTED)
- No hashes or provenance metadata

---

## 7. Information-Boundary Audit

### Call 1 (Initial Proposal)

| Allowed | Not Allowed |
|---------|-------------|
| Task context | Evaluator answers |
| Objective | Expected solutions |
| Constraints | C0/C1 results |
| | Research canon |
| | Git history |
| | Oracle source |

**Status:** ✅ Identical to C0. No boundary violation.

### Call 2 (Revision)

| Allowed | Not Allowed |
|---------|-------------|
| Task context | Evaluator answers |
| Objective | Expected solutions |
| Constraints | C0/C1 results |
| Initial candidate (from call 1) | Research canon |
| Deterministic text feedback | Git history |
| | Oracle source |
| | Epistemic state |
| | Authorization decisions |
| | Structured EvidenceArtifact |
| | C2–C5 capabilities |

**Status:** ✅ Structurally supported.

The `build_prompt()` method accepts:
- `design_context` → task context
- `existing_sdc` → initial candidate
- `evidence_summary` → text feedback
- `objective` → objective

No parameter accepts evaluator answers, research canon, or epistemic/authorization state.

### Potential Leakage Paths

| Path | Risk | Assessment |
|------|------|------------|
| `evidence_summary` parameter | Could leak raw EvidenceArtifact | **MITIGATED** — renderer converts to text; raw artifact not passed |
| `existing_sdc` parameter | Could leak expected solution | **MITIGATED** — only initial candidate from call 1 |
| Model prompt construction | LLM could hallucinate evaluator data | **MITIGATED** — no evaluator data in prompt |
| Oracle output | EvidenceArtifact contains scope/findings | **MITIGATED** — renderer filters to text only |

**No boundary violations identified.**

---

## 8. Evidence/Epistemic Separation Audit

### C1 Active Layers

```
PROPOSAL:    LLM (calls 1 and 2)
EVIDENCE:    Oracle (calls 1 and 2)
EPISTEMIC:   NOT ACTIVE
AUTHORIZATION: NOT ACTIVE
```

### Verification

| Layer | Active in C1? | Evidence of leakage? |
|-------|---------------|---------------------|
| Proposal | ✅ YES | N/A — LLM proposes only |
| Evidence | ✅ YES | Oracle evaluates only |
| Epistemic | ❌ NO | No `EpistemicEngine` in C1 pipeline |
| Authorization | ❌ NO | No `AuthorizationGate` in C1 pipeline |

**C1 does NOT activate C3 epistemic behavior.** The `EpistemicEngine` and `AuthorizationGate` are not imported or used in the C0 runner. A C1 runner must also not import or use them.

### Key Separation Preserved

```
ORACLE EXECUTION SUCCESS
    ≠
EVIDENCE SUFFICIENCY INSUFFICIENT
    ≠
EPISTEMIC STATE (not active in C1)
    ≠
AUTHORIZATION (not active in C1)
```

The text feedback renderer must not transform:
- `SUCCESS` → `VALIDATED`
- `INSUFFICIENT` → `FALSE`
- `WARNING` → `ACCEPTED`

**No leakage or ambiguity identified.**

---

## 9. Manifest/Schema Readiness

### Current C0 Manifest Fields

From `formal_runner_c0.py`:

```python
manifest = {
    "run_id": ...,
    "experiment_version": "EGER-EXP-001 v0.1",
    "benchmark_version": "EGER-BENCH-002 v0.1",
    "model_id": "EGER-MODEL-002",
    "condition": "C0",
    "task_id": ...,
    "prompt_version": "eger.prompt.v1",
    "oracle_revision": "3b5c2f2",
    "schema_versions": {...},
    "start_timestamp": ...,
    "end_timestamp": ...,
    "iteration_limit": 5,
    "model_call_limit": 5,
    "oracle_call_limit": 5,
    "model_call_count": 1,
    "candidate_hash": ...,
    "raw_output_hash": ...,
    "evidence_hash": ...,
    "epistemic_transitions": [],
    "authorization_decisions": [],
    "final_epistemic_state": "HYPOTHESIS",
    "final_authorization": None,
    "final_outcome": ...,
    "failure_class": ...,
    "completion_status": "COMPLETED",
    "pilot": False,
    "formal_experiment": True,
}
```

### C1 Required Extensions

| Field | Status | Required? |
|-------|--------|-----------|
| `condition` | EXISTS → "C1" | ✅ |
| `model_call_count` | EXISTS → 2 | ✅ |
| `oracle_call_count` | **MISSING** | **REQUIRED** |
| `initial_candidate_hash` | **MISSING** | **REQUIRED** |
| `initial_evidence_hash` | **MISSING** | **REQUIRED** |
| `text_feedback_hash` | **MISSING** | **REQUIRED** |
| `final_candidate_hash` | **MISSING** | **REQUIRED** |
| `final_evidence_hash` | **MISSING** | **REQUIRED** |
| `oracle_call_1_status` | **MISSING** | **REQUIRED** |
| `oracle_call_2_status` | **MISSING** | **REQUIRED** |

### Assessment

**Schema extension required.** The C0 manifest schema must be extended with C1-specific fields. This is a documentation/schema change, not an experimental change.

---

## 10. C0 Preservation Assessment

### Verification

| Item | Status |
|------|--------|
| C0 runner remains available | ✅ `formal_runner_c0.py` untouched |
| C0 artifacts at historical paths | ✅ `formal/raw/EGER-C0-*` untouched |
| C0 manifests unchanged | ✅ `formal/manifests/EGER-C0-*.json` untouched |
| C0 raw artifacts unchanged | ✅ `formal/raw/*/raw_model_output.txt` etc. untouched |
| C0 benchmark membership | ✅ Same 6 tasks in `RUN_INDEX.json` |
| C0 model configuration | ✅ `LiveEngineerModel(timeout=60, max_tokens=2048)` |

**No C1 implementation should modify any C0 artifact.** A C1 runner must write to a separate directory (e.g., `formal/C1/`).

---

## 11. BENCH-002 Isolation Assessment

### Verification

| Boundary | Status |
|----------|--------|
| `engineer_visible/` contains only task context | ✅ Verified in P015 |
| `evaluator_only/` separated | ✅ Separate directory |
| Task membership frozen | ✅ 6 tasks BENCH2-001..006 |
| Task order frozen | ✅ `BENCH-002-TASKS.json` |
| Expected answer access | ✅ Not loaded by Engineer |
| Filesystem access | ✅ Engineer reads only `engineer_visible/` |
| Prompt construction | ✅ No evaluator data in prompt |

**C1 can use frozen BENCH-002 without exposing evaluator-only answers.**

---

## 12. MODEL-002 Freeze Assessment

### Verification

| Parameter | Value | C1 Compatible? |
|-----------|-------|----------------|
| Provider | opencode | YES |
| Model | muse-spark-1.2-contributor-free | YES |
| Version | NOT_EXPOSED | YES |
| Temperature | 0.0 | YES |
| Max tokens | 2048 | YES |
| Timeout | 60s | YES |
| Model-call budget | 5 | YES (C1 uses 2) |

**Critical distinction:** The model used by the human researcher for OpenCode engineering assistance is NOT automatically the experimental MODEL-002. The C1 runner must explicitly instantiate `LiveEngineerModel(timeout=60, max_tokens=2048)` per MODEL-002.

---

## 13. Budget Assessment

| Resource | C0 Actual | C1 Required | Budget | Within? |
|----------|-----------|-------------|--------|---------|
| Model calls | 1 | 2 | 5 | ✅ |
| Oracle calls | 0 (evaluator-side) | 2 | 5 | ✅ |
| Routing calls | 0 | 0 | 5 | ✅ |
| Max iterations | 1 | 1 | 5 | ✅ |
| Max wall clock | <5s | <10s | 300s | ✅ |

**All budgets accommodate C1. No budget changes required.**

---

## 14. Determinism Assessment

### Deterministic Components

| Component | Deterministic? | Verified? |
|-----------|---------------|-----------|
| Prompt construction | ✅ `build_prompt()` is deterministic | P010 tests |
| Oracle invocation | ✅ Byte-identical for same input | P006 T006, P008 T005 |
| Artifact serialization | ✅ `to_dict()` deterministic | P010 tests |
| Hashing | ✅ SHA256 deterministic | P008 T006, T012 |
| Manifest creation | ✅ JSON serialization | C0 runner |

### Potential Nondeterminism Sources

| Source | Risk | Mitigation |
|--------|------|------------|
| Model output (LLM) | Non-deterministic even at temp=0.0 | Documented as limitation (MODEL-002 §17) |
| `datetime.now()` in manifests | Timestamps differ between runs | `produced_at` excluded from evidence_hash |
| Oracle execution time | May vary |不影响 scientific comparison |

**No implementation-level nondeterminism identified.** Model nondeterminism is a documented limitation of probabilistic components, not an implementation defect.

---

## 15. Failure-Handling Assessment

### C0 Failure Paths (existing)

| Failure | C0 Behavior |
|---------|-------------|
| Model call 1 failure | `ProposalFailure(PROPOSAL_FAILURE)` |
| Oracle failure (evaluator-side) | `ORACLE_FAILURE` final_outcome |
| Malformed candidate | `MALFORMED_OUTPUT` |

### C1 Additional Failure Paths (not defined)

| Failure | Defined in Contract? | Status |
|---------|---------------------|--------|
| Model call 1 failure | ✅ Same as C0 | READY |
| Oracle call 1 failure | ❌ NOT DEFINED | **OPEN DESIGN QUESTION** |
| Malformed initial candidate | ❌ NOT DEFINED | **OPEN DESIGN QUESTION** |
| Empty candidate | ❌ NOT DEFINED | **OPEN DESIGN QUESTION** |
| Feedback rendering failure | ❌ NOT DEFINED | **OPEN DESIGN QUESTION** |
| Model call 2 failure | ❌ NOT DEFINED | **OPEN DESIGN QUESTION** |
| Oracle call 2 failure | ❌ NOT DEFINED | **OPEN DESIGN QUESTION** |
| Timeout during revision | ❌ NOT DEFINED | **OPEN DESIGN QUESTION** |

### Recommended Default Behavior

If oracle call 1 fails → no feedback to render → C1 degrades to C0 (initial candidate measured). This preserves the initial candidate as the outcome.

If model call 2 fails → use initial candidate as final outcome. Document failure.

If oracle call 2 fails → cannot measure revised candidate. Record ORACLE_FAILURE.

**These are OPEN DESIGN QUESTIONS that must be resolved before C1 execution.**

---

## 16. Primary-Measurement Assessment

### Verification

| Requirement | Status |
|-------------|--------|
| Final revised candidate is primary artifact | ✅ Designed in C1 protocol |
| Oracle call 2 evaluates revised candidate | ✅ Planned |
| Initial candidate NOT used as final measurement | ✅ By design |
| First oracle result NOT used as final result | ✅ By design |
| Text feedback NOT used as outcome | ✅ By design |

**No implementation mismatch identified.** The C1 runner must ensure oracle call 2 evaluates the revised candidate, not the initial candidate.

---

## 17. Confound-Monitoring Assessment

| Indicator | Observable in C1? | Implementation Ready? |
|-----------|-------------------|----------------------|
| CM-1: Recovery from specific finding | YES | ✅ Compare initial vs. final findings |
| CM-2: Correction of known error | YES | ✅ Check if error findings removed |
| CM-3: Response to INSUFFICIENT | YES | ✅ Check candidate change after INSUFFICIENT |
| CM-4: Unchanged after non-actionable | YES | ✅ Check if info findings → no change |
| CM-5: Improvement from evidence | YES | ✅ Compare initial vs. final evidence |
| CM-6: New errors introduced | YES | ✅ Check if new errors in final |
| CM-7: Convergence attempt | PARTIAL | ⚠️ Single revision, not iterative |

**CM-1 through CM-6 are structurally observable.** The C1 runner must record both initial and final candidates/evidence to enable comparison.

**CM-7 requires definition update** for single-revision context.

---

## 18. Ṛta Boundary Assessment

| Check | Status |
|-------|--------|
| No source modification | ✅ `rta-constraint-intelligence/` untouched |
| No test fixture modification | ✅ Untouched |
| No generated artifacts inside Ṛta | ✅ Oracle writes to temp dir outside Ṛta |
| No commits in Ṛta | ✅ HEAD: 3b5c2f2 unchanged |
| No reset/clean/checkout | ✅ Untouched |
| No forbidden generation path | ✅ 0 hits for `rta_generate` in `eger/` |
| External interface only | ✅ `subprocess.run()` with cwd outside Ṛta |

**Ṛta boundary INTACT.**

---

## 19. Testing Readiness

### Current Test Coverage

| Test Suite | Tests | Coverage |
|------------|-------|----------|
| `test_evidence_oracle.py` | 14 | Oracle adapter, determinism, hashing, scope |
| `test_epistemic_authorization.py` | 17 | L2/L3, transitions, violations |
| `test_llm_proposal.py` | 16 | EngineerAdapter, extraction, provenance |
| **Total** | **47** | **47/47 PASS** |

### Minimum C1 Tests Required (not created)

| Test | Purpose | Priority |
|------|---------|----------|
| `test_c1_text_feedback_determinism` | Same EvidenceArtifact → same text | REQUIRED |
| `test_c1_information_boundary` | Call 2 receives only authorized info | REQUIRED |
| `test_c1_two_stage_sequencing` | Initial → feedback → revision → measurement | REQUIRED |
| `test_c1_initial_final_preservation` | Both candidates recorded separately | REQUIRED |
| `test_c1_oracle_call_count` | Exactly 2 oracle calls | REQUIRED |
| `test_c1_budget_enforcement` | 2 model calls ≤ 5, 2 oracle calls ≤ 5 | REQUIRED |
| `test_c1_failure_handling` | Oracle/model failure paths | REQUIRED |
| `test_c1_c0_regression` | C0 still passes 47/47 after C1 implementation | REQUIRED |
| `test_c1_no_epistemic_leakage` | C1 does not activate L2 | REQUIRED |
| `test_c1_no_authorization_leakage` | C1 does not activate L3 | REQUIRED |
| `test_c1_no_evaluator_leakage` | No evaluator data in prompt | REQUIRED |

---

## 20. Implementation Gaps

### Blocking

| # | Gap | Resolution |
|---|-----|------------|
| B-1 | **No text feedback renderer** | Create `eger/engineer/feedback.py` implementing `render_text_feedback(evidence: EvidenceArtifact) -> str` |

### Non-Blocking

| # | Gap | Resolution |
|---|-----|------------|
| NB-1 | No C1 runner | Create `research/experiments/EGER-EXP-001/formal_runner_c1.py` |
| NB-2 | Manifest schema not extended | Add C1-specific fields to manifest |
| NB-3 | No C1-specific tests | Create `tests/test_c1_feedback.py` |
| NB-4 | Failure-handling semantics undefined | Define default behavior for C1 two-stage failures |
| NB-5 | CM-7 definition not updated | Define for single-revision context |
| NB-6 | Experiment version string | Update to "EGER-EXP-001 v0.2" in C1 runner |

---

## 21. Open Design Questions

| # | Question | Impact |
|---|----------|--------|
| ODQ-1 | If oracle call 1 fails, should C1 degrade to C0 (use initial candidate) or abort? | Failure handling |
| ODQ-2 | If model call 2 fails, should initial candidate be used as final outcome? | Failure handling |
| ODQ-3 | If oracle call 2 fails, how is the revised candidate measured? | Measurement completeness |
| ODQ-4 | Should the text feedback renderer be a standalone module or a method on EvidenceOracle? | Architecture |
| ODQ-5 | Should C1 write to `formal/C1/` or a separate experiment directory? | File organization |

---

## 22. Minimum Implementation Plan

### Phase 1: Text Feedback Renderer (BLOCKING)

1. Create `eger/engineer/feedback.py`
2. Implement `render_text_feedback(evidence: EvidenceArtifact) -> str`
3. Follow C1 Text Feedback Contract exactly
4. Write determinism test

### Phase 2: C1 Runner

1. Create `research/experiments/EGER-EXP-001/formal_runner_c1.py`
2. Implement two-stage pipeline:
   - Call 1: `adapter.propose()` → initial candidate
   - Oracle 1: `oracle.validate()` → evidence
   - Render: `render_text_feedback(evidence)` → text feedback
   - Call 2: `adapter.propose(existing_sdc=initial.sdc_text, evidence_summary=text_feedback)` → revised candidate
   - Oracle 2: `oracle.validate()` → measurement
3. Record all artifacts to `formal/C1/`
4. Write extended manifest

### Phase 3: Tests

1. Create `tests/test_c1_feedback.py`
2. Implement 11 required tests (see §19)
3. Verify C0 regression (47/47 still passes)

### Phase 4: Documentation

1. Update `STATE.md` with C1 implementation status
2. Update `RESEARCH_LEDGER.md` with implementation entry

---

## 23. Explicit Non-Authorized Actions

This readiness audit does NOT authorize:

- C1 implementation (requires separate authorization)
- C1 execution (requires implementation + authorization)
- BENCH-002 modification
- MODEL-002 modification
- Ṛta modification
- C0 artifact modification
- Research contract modification
- GitHub push
- Subagent creation

---

## 24. Final Readiness Verdict

**NOT READY**

| Category | Verdict |
|----------|---------|
| EngineerModel | ✅ READY |
| OracleAdapter | ✅ READY |
| Text feedback renderer | ❌ NOT IMPLEMENTED (BLOCKING) |
| C1 runner | ❌ NOT IMPLEMENTED |
| Manifest schema | ⚠️ EXTENSION REQUIRED |
| Information boundary | ✅ STRUCTURALLY READY |
| Evidence/epistemic separation | ✅ PRESERVED |
| C0 preservation | ✅ VERIFIED |
| BENCH-002 isolation | ✅ VERIFIED |
| MODEL-002 freeze | ✅ VERIFIED |
| Budgets | ✅ ALL WITHIN LIMITS |
| Determinism | ✅ NO IMPLEMENTATION DEFECTS |
| Failure handling | ⚠️ OPEN DESIGN QUESTIONS |
| Primary measurement | ✅ CORRECTLY DESIGNED |
| Confound monitoring | ✅ CM-1–6 OBSERVABLE |
| Ṛta boundary | ✅ INTACT |
| Testing | ❌ NO C1 TESTS |

---

## 25. Exact Next Authorized Step

**Resolve B-1 (text feedback renderer) and ODQ-1–5 (failure handling), then implement C1.**

This requires a separate authorization prompt (e.g., `EGER-P024 — C1 Implementation Authorization`).

---

*This readiness audit is PROPOSED — AWAITING HUMAN REVIEW. The repository is structurally ready for C1 but requires implementation of the text feedback renderer and C1 runner before execution.*
