# EGER-P024 — C1 Open-Question Resolution & Implementation Authorization

| Field | Value |
|-------|-------|
| ID | EGER-P024 |
| Date | 2026-08-26 |
| Type | Decision record + implementation authorization |
| Status | **DECISIONS RECORDED — AWAITING HUMAN APPROVAL** |
| Predecessor | EGER-P023 (Implementation Readiness) |

---

## 1. Executive Decision

Five open design questions from EGER-P023 are resolved below. Each decision is scientifically justified and preserves causal validity. If approved by the human researcher, implementation of the approved C1 protocol is authorized.

---

## 2. Current Research State

```
C0                         ✓ COMPLETE
C0 Review R1               ✓ COMPLETE
C1 Readiness (P017)        ✓ COMPLETE
C1 Text Feedback Contract  ✓ DEFINED (P018/P019)
C1 Causal Mechanism        ✓ RESOLVED → Interpretation B (P020)
C1 Change Control          ✓ APPROVED (EGER-CHANGE-001, EXP-001 v0.2)
C1 Implementation Readiness ✓ AUDITED (P023) — NOT READY — gaps identified
C1 Open Questions          ⏸ RESOLVED BELOW (P024)
C1 Implementation          ✗ NOT STARTED
C1 Execution               ✗ NOT AUTHORIZED
C2–C5                      ✗ NOT STARTED
Ṛta                        ✓ UNTOUCHED
GitHub                     ✓ PRIVATE
```

---

## 3. ODQ-1 — Oracle Call 1 Failure

### Question

If Ṛta oracle call #1 fails, should C1 degrade to C0 or abort?

### Options

| Option | Description | Scientific Concern |
|--------|-------------|-------------------|
| A: Degrade to C0 | No feedback → terminate as C0-like run | Risk: misclassifying a no-feedback run as C1 treatment |
| B: Abort run | Terminate without revision | Clean: preserves C1 treatment integrity |
| C: Retry oracle | Only if retry semantics already permitted | Protocol §14 allows technical retries for infrastructure failures |

### Analysis

C1's independent variable is **access to deterministic oracle text feedback during revision.** If oracle call #1 fails, the treatment cannot be delivered.

Under Option A (degrade to C0), the run would produce:
- LLM call 1 → initial candidate
- Oracle call 1 → FAILURE
- No feedback
- No revision
- Final outcome = initial candidate

This is **functionally identical to C0** (one model call, no feedback influence). Classifying it as C1 would contaminate the C1 data set with runs that received no treatment.

Under Option B (abort), the run is clearly classified as **INCOMPLETE_TREATMENT** — the treatment was attempted but could not be delivered. This preserves clean attribution.

Under Option C (retry), the retry policy (EXP-001 v0.1 §14) allows technical retries for infrastructure crashes and provider 5xx. An oracle execution failure due to missing binary or invalid input is NOT a technical retry — it is an experimental failure. However, a transient infrastructure failure (e.g., temporary file system issue) IS a legitimate technical retry.

### Decision

**Option B (Abort) — with technical retry for infrastructure failures only.**

| Scenario | Classification |
|----------|---------------|
| Oracle binary missing | ABORT → INCOMPLETE_TREATMENT |
| Invalid input to oracle | ABORT → INCOMPLETE_TREATMENT |
| Transient infrastructure failure | TECHNICAL RETRY (per §14) → if still fails, ABORT |
| Oracle returns non-zero exit with valid evidence | Use evidence (exit 0/1 path) |

### Rationale

Clean causal attribution requires that every C1 run in the data set actually received the treatment. A no-feedback run classified as C1 would weaken the primary comparison (C0 vs C1 final artifact).

### Change Control Required

**NO.** This is an implementation-level failure-handling decision consistent with EXP-001 v0.1 §12 (failure taxonomy) and §14 (retry policy).

---

## 4. ODQ-2 — Model Call 2 Failure

### Question

If LLM call #2 fails, should the initial candidate become the final outcome?

### Options

| Option | Description | Scientific Concern |
|--------|-------------|-------------------|
| A: Initial candidate as final | Use initial candidate as C1 outcome | Risk: C1 outcome = same as C0 (no feedback influence) |
| B: Terminate as incomplete | Record as INCOMPLETE_TREATMENT | Clean: preserves treatment integrity |
| C: Retry model call | Per §14 technical retry policy | May be legitimate for infrastructure failures |

### Analysis

If model call #2 fails after oracle call #1 succeeded and feedback was rendered, the treatment was **partially delivered**:
- Feedback was generated ✅
- Feedback was presented to the Engineer ✅
- Engineer attempted revision ❌ (model call failed)
- No revised candidate exists

Option A (use initial candidate) would produce a C1 run where the primary measured artifact (revised candidate) is actually the initial candidate — which is identical to C0. This contaminates the C1 data set.

Option B (terminate as incomplete) cleanly separates "treatment attempted but incomplete" from "treatment delivered successfully."

Option C (retry) is legitimate for infrastructure failures (provider 5xx, timeout) per §14.

### Decision

**Option B (Terminate as incomplete) — with technical retry for infrastructure failures only.**

| Scenario | Classification |
|----------|---------------|
| Model timeout (infra) | TECHNICAL RETRY (per §14) → if still fails, ABORT |
| Provider 5xx (infra) | TECHNICAL RETRY → if still fails, ABORT |
| Model unavailable | ABORT → INCOMPLETE_TREATMENT |
| Malformed output | ABORT → INCOMPLETE_TREATMENT (initial candidate recorded, not used as final) |

### Manifest Recording

If model call #2 fails:
- `initial_candidate_hash`: recorded ✅
- `final_candidate_hash`: null
- `final_outcome`: INCOMPLETE_TREATMENT
- `failure_class`: MODEL_FAILURE or TIMEOUT
- `revised_candidate_available`: false

The initial candidate is **retained as an artifact** for diagnostic analysis but is **not used as the C1 primary outcome.**

### Rationale

The primary C1 comparison is "C0 final artifact vs C1 final revised candidate." If no revised candidate exists, the comparison cannot be made. Recording the run as INCOMPLETE_TREATMENT preserves data integrity.

### Change Control Required

**NO.** Implementation-level failure handling consistent with §12 and §14.

---

## 5. ODQ-3 — Oracle Call 2 Failure

### Question

If the second oracle call fails, how is the revised candidate measured?

### Options

| Option | Description | Scientific Concern |
|--------|-------------|-------------------|
| A: Unmeasured/incomplete | Revised candidate exists but is unmeasured | Clean: preserves measurement integrity |
| B: Retry oracle | Per §14 technical retry | May be legitimate for infrastructure failures |
| C: Fall back to first oracle result | Use oracle call 1 evidence as measurement | **UNACCEPTABLE** — first oracle evaluated initial candidate, not revised |

### Analysis

Option C is scientifically invalid. Oracle call 1 evaluated the **initial candidate**. Oracle call 2 evaluates the **revised candidate**. These are different artifacts. Using oracle call 1 evidence as measurement of the revised candidate would be a **measurement error** — the evidence would not correspond to the artifact it purports to measure.

Option A is clean: the revised candidate exists but cannot be measured. The run is INCOMPLETE_MEASUREMENT — the treatment was delivered (feedback → revision) but the outcome cannot be quantified.

Option B is legitimate for infrastructure failures.

### Decision

**Option A (Unmeasured/incomplete) — with technical retry for infrastructure failures only.**

| Scenario | Classification |
|----------|---------------|
| Oracle binary missing | ABORT → INCOMPLETE_MEASUREMENT |
| Transient infrastructure failure | TECHNICAL RETRY → if still fails, ABORT |
| Oracle returns non-zero with valid evidence | Use evidence (exit 0/1 path) |

### Manifest Recording

If oracle call #2 fails:
- `final_candidate_hash`: recorded ✅ (revised candidate exists)
- `final_evidence_hash`: null
- `final_outcome`: INCOMPLETE_MEASUREMENT
- `failure_class`: ORACLE_FAILURE
- `revised_candidate_available`: true
- `revised_candidate_measured`: false

### Rationale

The primary C1 comparison requires both a revised candidate AND its oracle evaluation. If the evaluation is missing, the comparison cannot be made. The revised candidate is retained for potential manual inspection but is not used in the primary quantitative comparison.

### Change Control Required

**NO.** Implementation-level failure handling consistent with §12 and §14.

---

## 6. ODQ-4 — Renderer Location

### Question

Should deterministic text rendering be a standalone module or a method on EvidenceOracle?

### Options

| Option | Location | Pros | Cons |
|--------|----------|------|------|
| A: Standalone module | `eger/engineer/feedback.py` | Clean separation of evidence generation from presentation | One more file |
| B: Method on EvidenceOracle | `oracle.render_text_feedback()` | Co-located with evidence | Couples evidence generation with presentation |

### Analysis

**Authority separation (P7):**
- Oracle = Evidence authority (generates EvidenceArtifact)
- Renderer = Presentation layer (converts EvidenceArtifact to text)
- These are distinct concerns

If the renderer is on EvidenceOracle, then the Evidence authority is also responsible for how evidence is presented to the Engineer. This couples evidence generation with presentation — a mild P7 concern.

If the renderer is standalone, the Evidence authority (Oracle) produces evidence, and a separate deterministic module renders it as text. This preserves clean separation.

**Testability:**
- Standalone renderer: independently testable with mock EvidenceArtifacts
- Method on Oracle: requires Oracle instantiation for rendering tests

**Reuse:**
- Standalone renderer: can be used by C1 runner, C2 runner (if structured evidence includes text), and tests
- Method on Oracle: tied to Oracle lifecycle

**P6 (Explicit Epistemic Boundaries):**
The renderer must not become an epistemic engine. A standalone module with a single function `render_text_feedback(evidence) -> str` is the simplest way to ensure it does not accumulate epistemic logic.

### Decision

**Option A: Standalone module `eger/engineer/feedback.py`.**

The renderer is a deterministic presentation layer, not an evidence authority. It belongs in the Engineer package because it prepares information for the Engineer's consumption, not because it has Proposal authority.

### Module Structure

```python
# eger/engineer/feedback.py

def render_text_feedback(evidence: EvidenceArtifact) -> str:
    """Deterministic rendering of EvidenceArtifact to text feedback.
    
    Same input → same output, always.
    No LLM, no probabilistic component, no interpretation.
    """
    ...
```

### Rationale

Clean authority separation. The Oracle generates evidence. The renderer presents it. The Engineer consumes it. Three distinct concerns, three distinct layers.

### Change Control Required

**NO.** Implementation architecture decision. Does not change the frozen protocol.

---

## 7. ODQ-5 — C1 Artifact Directory

### Question

Where should C1 experimental artifacts be stored?

### Options

| Option | Structure | Pros | Cons |
|--------|-----------|------|------|
| A: `formal/C1/` | `research/experiments/EGER-EXP-001/formal/C1/` | Co-located with C0 | Nested under `formal/` |
| B: `results/C1/` | `research/experiments/EGER-EXP-001/results/C1/` | Clean separation from `formal/` | Different from C0 convention |
| C: Parallel to `formal/` | `research/experiments/EGER-EXP-001/C1/` | Flat, visible | Breaks C0 convention |

### Analysis

C0 artifacts live at:
```
research/experiments/EGER-EXP-001/formal/
├── manifests/
├── raw/
└── RUN_INDEX.json
```

Option A places C1 at `formal/C1/`:
```
research/experiments/EGER-EXP-001/formal/
├── manifests/          ← C0 manifests
├── raw/                ← C0 raw artifacts
├── RUN_INDEX.json      ← C0 index
└── C1/                 ← C1 directory
    ├── manifests/
    ├── raw/
    └── RUN_INDEX.json
```

This keeps all formal experiment artifacts under one root while clearly separating C0 and C1. C0 paths remain untouched.

Option B places C1 at `results/C1/` — this introduces a new `results/` directory that doesn't exist in the current structure.

Option C places C1 parallel to `formal/` — this breaks the convention that `formal/` contains formal experiment results.

### Decision

**Option A: `formal/C1/` subdirectory.**

```
research/experiments/EGER-EXP-001/formal/
├── manifests/          ← C0 manifests (UNCHANGED)
├── raw/                ← C0 raw artifacts (UNCHANGED)
├── RUN_INDEX.json      ← C0 index (UNCHANGED)
└── C1/                 ← C1 directory (NEW)
    ├── manifests/      ← C1 manifests
    ├── raw/            ← C1 raw artifacts
    └── RUN_INDEX.json  ← C1 index
```

### C1 Artifact Structure Per Run

```
formal/C1/raw/<run_id>/
├── initial_candidate.json        ← CandidateArtifact from call 1
├── raw_evidence_initial.json     ← RawEvidence from oracle call 1
├── evidence_initial.json         ← EvidenceArtifact from oracle call 1
├── text_feedback.txt             ← Rendered text feedback
├── raw_model_output_call2.txt    ← Raw model output from call 2
├── revised_candidate.json        ← CandidateArtifact from call 2
├── raw_evidence_final.json       ← RawEvidence from oracle call 2
└── evidence_final.json           ← EvidenceArtifact from oracle call 2
```

### Run ID Convention

C1 run IDs use the prefix `EGER-C1-` (vs. C0's `EGER-C0-`):
- `EGER-C1-<UUID[:8]>` — e.g., `EGER-C1-A1B2C3D4`

### What MUST NOT Change

- C0 `formal/manifests/` — untouched
- C0 `formal/raw/` — untouched
- C0 `formal/RUN_INDEX.json` — untouched
- C0 run IDs — untouched

### Rationale

Co-location under `formal/` preserves the convention that formal experiment artifacts live in one place. The `C1/` subdirectory provides clear separation without introducing new top-level directories.

### Change Control Required

**NO.** Implementation-level file organization. Does not change the frozen protocol.

---

## 8. C1 Failure Taxonomy

### Existing Contract Taxonomy (EXP-001 v0.1 §12)

```
PROPOSAL_FAILURE
ORACLE_FAILURE
INVALID_ARTIFACT
INSUFFICIENT_EVIDENCE
UNSUPPORTED
EPISTEMIC_VIOLATION
AUTHORIZATION_REJECTION
TIMEOUT
ITERATION_LIMIT
INFRASTRUCTURE_FAILURE
```

### C1 Additions

| Classification | Definition | When Used |
|---------------|------------|-----------|
| INCOMPLETE_TREATMENT | Treatment attempted but not delivered (oracle call 1 failure or model call 2 failure before revision) | Oracle call 1 fails, or model call 2 fails |
| INCOMPLETE_MEASUREMENT | Treatment delivered but outcome not measured (oracle call 2 failure) | Oracle call 2 fails after successful revision |

### Assessment

These two new classifications are **implementation-level terminology** that falls under the existing `PROPOSAL_FAILURE` and `ORACLE_FAILURE` categories. They can be implemented as subtypes:

- `INCOMPLETE_TREATMENT` → `failure_class = "ORACLE_FAILURE"` (if oracle call 1 failed) or `failure_class = "MODEL_FAILURE"` (if model call 2 failed)
- `INCOMPLETE_MEASUREMENT` → `failure_class = "ORACLE_FAILURE"` (if oracle call 2 failed)

The manifest `final_outcome` field can use the more specific terms (`INCOMPLETE_TREATMENT`, `INCOMPLETE_MEASUREMENT`) for C1-specific analysis while the `failure_class` field uses the existing contract taxonomy.

### Decision

**Use existing taxonomy for `failure_class`. Use C1-specific terms for `final_outcome`.**

| `final_outcome` | `failure_class` | Meaning |
|-----------------|-----------------|---------|
| VALID_ARTIFACT | — | Revised candidate validated |
| INVALID_ARTIFACT | INVALID_ARTIFACT | Revised candidate has errors |
| INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | Scope insufficient |
| INCOMPLETE_TREATMENT | ORACLE_FAILURE or MODEL_FAILURE | Treatment not delivered |
| INCOMPLETE_MEASUREMENT | ORACLE_FAILURE | Treatment delivered but not measured |
| ORACLE_FAILURE | ORACLE_FAILURE | Oracle call 2 failed |
| PROPOSAL_FAILURE | PROPOSAL_FAILURE | Model call 1 failed |

### Change Control Required

**NO.** Implementation-level taxonomy extension. The existing contract categories cover all cases.

---

## 9. Information-Boundary Confirmation

### Approved C1 Call 2 Input

| May Receive | Source |
|-------------|--------|
| Task context (design_context) | BENCH-002 engineer_visible |
| Objective | BENCH-002 engineer_visible |
| Required output format | Protocol §6 |
| Initial candidate | Call 1 output |
| Deterministic text feedback | Renderer output |

| Must NOT Receive | Reason |
|------------------|--------|
| Evaluator-only expected answers | Benchmark isolation |
| Hidden benchmark labels | Benchmark isolation |
| Research canon | Information boundary |
| Other tasks | Task isolation |
| Git history | Information boundary |
| Ṛta source code | Oracle boundary |
| Ṛta fixtures | Oracle boundary |
| Structured EvidenceArtifact | C2 treatment |
| Epistemic state | C3 treatment |
| Authorization state | C5 treatment |
| C2/C3/C4/C5 capabilities | Capability matrix |

### Implementation Guard

The `EngineerAdapter.build_prompt()` method accepts:
- `design_context` → task context ✅
- `existing_sdc` → initial candidate ✅
- `evidence_summary` → text feedback ✅
- `objective` → objective ✅

No parameter accepts evaluator answers, research canon, or epistemic/authorization state. The C1 runner must construct the prompt using only these parameters with the approved inputs.

### Confirmed: ✅

---

## 10. Model Freeze Confirmation

| Parameter | Value | Frozen? |
|-----------|-------|---------|
| Provider | opencode | ✅ MODEL-002 |
| Model | muse-spark-1.2-contributor-free | ✅ MODEL-002 |
| Version | NOT_EXPOSED | ✅ MODEL-002 |
| Temperature | 0.0 | ✅ MODEL-002 |
| Max tokens | 2048 | ✅ MODEL-002 |
| Timeout | 60s | ✅ MODEL-002 |
| Prompt version | eger.prompt.v1 | ✅ PROMPT-001 |
| Model-call budget | 5 | ✅ EXP-001 |

**Critical distinction:** The model used by the human researcher for OpenCode engineering assistance (currently MIMO 2.5) is NOT the experimental MODEL-002. The C1 runner must explicitly instantiate `LiveEngineerModel(timeout=60, max_tokens=2048)` per MODEL-002.

### Confirmed: ✅

---

## 11. C0 Preservation Requirements

| Requirement | Status |
|-------------|--------|
| C0 runner remains at original path | ✅ `formal_runner_c0.py` untouched |
| C0 manifests at `formal/manifests/` | ✅ Untouched |
| C0 raw artifacts at `formal/raw/` | ✅ Untouched |
| C0 `RUN_INDEX.json` | ✅ Untouched |
| C0 run IDs (`EGER-C0-*`) | ✅ Untouched |
| C0 model configuration | ✅ `LiveEngineerModel(timeout=60, max_tokens=2048)` |
| C0 does not receive feedback | ✅ By design |

**Any C1 implementation that modifies C0 artifacts is a protocol violation.**

---

## 12. BENCH-002 Preservation Requirements

| Requirement | Status |
|-------------|--------|
| engineer_visible boundary | ✅ Only task context exposed |
| evaluator_only boundary | ✅ Separated, not loaded by Engineer |
| Task membership frozen | ✅ 6 tasks BENCH2-001..006 |
| Task order frozen | ✅ BENCH-002-TASKS.json |
| Expected answers not in prompt | ✅ Verified |

**C1 uses the same frozen benchmark as C0. No benchmark modification.**

---

## 13. Ṛta Boundary Requirements

| Requirement | Status |
|-------------|--------|
| No source modification | ✅ |
| No test fixture modification | ✅ |
| No generated artifacts inside Ṛta | ✅ |
| No commits | ✅ |
| No reset/clean/checkout | ✅ |
| No `rta_generate` | ✅ 0 hits in `eger/` |
| External interface only | ✅ subprocess with cwd outside Ṛta |

**Ṛta boundary INTACT. No modification permitted.**

---

## 14. Authorized Implementation Scope

If the human researcher approves the five decisions above, the following implementation is authorized:

### 14.1 Deterministic C1 Feedback Renderer

Create `eger/engineer/feedback.py`:
- `render_text_feedback(evidence: EvidenceArtifact) -> str`
- Follow C1 Text Feedback Contract exactly
- Deterministic: same input → same output
- No LLM, no probabilistic component
- No evaluator data, no epistemic state, no authorization

### 14.2 C1 Two-Stage Runner

Create `research/experiments/EGER-EXP-001/formal_runner_c1.py`:
- Implement approved C1 pipeline (EXP-001 v0.2 §31)
- Call 1: `adapter.propose()` → initial candidate
- Oracle 1: `oracle.validate()` → evidence
- Render: `render_text_feedback(evidence)` → text feedback
- Call 2: `adapter.propose(existing_sdc=..., evidence_summary=...)` → revised candidate
- Oracle 2: `oracle.validate()` → measurement
- Record all artifacts to `formal/C1/`
- Handle failures per ODQ-1/2/3 decisions
- Write extended manifest per EXP-001 v0.2 §23

### 14.3 Manifest/Schema Extension

Extend C1 manifests with:
- `initial_candidate_hash`
- `initial_oracle_evidence_hash`
- `text_feedback_hash`
- `final_candidate_hash`
- `final_oracle_evidence_hash`
- `oracle_call_count: 2`
- `oracle_call_1_status`
- `oracle_call_2_status`

### 14.4 Required Tests

Create `tests/test_c1_feedback.py`:
- Text feedback determinism
- Information boundary enforcement
- Two-stage call sequencing
- Initial/final artifact preservation
- Oracle call count verification
- Budget enforcement
- Failure handling (ODQ-1/2/3)
- C0 regression protection (47/47 still passes)
- No epistemic leakage
- No authorization leakage
- No evaluator data leakage

### 14.5 Implementation Documentation

Update `STATE.md` and `RESEARCH_LEDGER.md` with implementation entry.

---

## 15. Explicitly Unauthorized Actions

Even if implementation is authorized:

| Action | Authorized? |
|--------|-------------|
| C1 execution | ❌ NO |
| Benchmark runs | ❌ NO |
| BENCH-002 modification | ❌ NO |
| MODEL-002 modification | ❌ NO |
| Ṛta modification | ❌ NO |
| C0 artifact modification | ❌ NO |
| Evaluator answer exposure | ❌ NO |
| Subagent creation | ❌ NO |
| GitHub push | ❌ NO |
| Git history rewrite | ❌ NO |
| C0 artifact movement | ❌ NO |

---

## 16. Human Authorization Status

### Decisions Requiring Approval

| ODQ | Question | Recommended Option | Change Control? |
|-----|----------|-------------------|----------------|
| ODQ-1 | Oracle call 1 failure | Abort (INCOMPLETE_TREATMENT) with infra retry | NO |
| ODQ-2 | Model call 2 failure | Terminate (INCOMPLETE_TREATMENT) with infra retry | NO |
| ODQ-3 | Oracle call 2 failure | Unmeasured (INCOMPLETE_MEASUREMENT) with infra retry | NO |
| ODQ-4 | Renderer location | Standalone `eger/engineer/feedback.py` | NO |
| ODQ-5 | C1 artifact directory | `formal/C1/` subdirectory | NO |

### HUMAN DECISION REQUIRED

> Implementation authorization is granted ONLY for the decisions explicitly approved by the human researcher.

The human researcher must approve:
1. All five ODQ decisions
2. The authorized implementation scope (§14)
3. The understanding that this authorizes implementation only, NOT execution

---

## 17. Exact Next Step

**If human approves P024 decisions:**

→ `EGER-P025 — C1 Implementation`
- Create `eger/engineer/feedback.py` (text feedback renderer)
- Create `formal_runner_c1.py` (C1 two-stage runner)
- Create `tests/test_c1_feedback.py` (11 required tests)
- Verify C0 regression (47/47)
- Update documentation

**If human does not approve:**

→ Record dissent and revise decisions.

---

*This decision record is PROPOSED — AWAITING HUMAN APPROVAL. Implementation authorization requires explicit human consent for each decision and the overall implementation scope.*
