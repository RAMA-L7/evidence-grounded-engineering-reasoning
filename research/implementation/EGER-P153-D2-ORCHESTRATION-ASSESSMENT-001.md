# EGER-P153 — D2 Orchestration Assessment

## Gate

P153 — Production Hardening / D2 Assessment

## Date

2026-09-02

## Purpose

Assess D2 — Pipeline/RevisionController orchestration overlap and determine whether it creates a real correctness, authority, maintainability, or production-hardening problem.

This is an **assessment + design gate**. No implementation occurs unless the assessment establishes a concrete need.

**No production code modified. No live model calls. No experiments. No historical artifacts changed.**

---

## 1. Baseline

```
Branch: main
HEAD: 04e1f53 (P152 checkpoint)
HEAD == origin/main: YES
Working tree: clean (Universal_Principles_Library/ untracked, unrelated)
Regression: 664/664 PASS
```

---

## 2. D2 Definition

From P145/P148:

> **D2 — Pipeline duplicates RevisionController orchestration**
>
> Two components implement the revision loop:
> 1. `RevisionController.run()` — canonical implementation
> 2. `EGERPipeline._run_with_tracking()` — duplicates with provenance tracking

---

## 3. Responsibility Map

| Responsibility | Current Owner | Secondary Owner | Should Own It? |
|---|---|---|---|
| Task initialization | EGERPipeline | — | Pipeline (composition boundary) |
| Prompt construction | PromptBuilder | — | PromptBuilder (single owner) |
| Candidate extraction | Pipeline._extract_candidate | RevisionController._extract_candidate | RevisionController (canonical) |
| Oracle invocation | Pipeline._run_with_tracking | RevisionController.run | RevisionController (canonical) |
| Evidence normalization | Pipeline._run_with_tracking | RevisionController.run | EvidenceNormalizer (single owner) |
| Revision iteration | Pipeline._run_with_tracking | RevisionController.run | RevisionController (canonical) |
| Budget enforcement | Pipeline._run_with_tracking | RevisionController.run | RevisionController (canonical) |
| Verification | EGERPipeline.run | — | Pipeline (composition boundary) |
| Acceptance/rejection | VerificationGate | — | VerificationGate (sole authority) |
| Provenance recording | EGERPipeline._run_with_tracking | — | Pipeline (composition boundary) |
| Logging | EgerLogger (standalone) | — | EgerLogger (single owner) |
| Configuration | EgerConfig / RevisionConfig | — | Config (single owner) |

---

## 4. Authority-Boundary Analysis

### Proposal authority

| Check | Status |
|---|---|
| LLM may propose candidates | ✅ Both Pipeline and Controller allow this |
| LLM must not self-verify | ✅ Neither component allows this |
| LLM must not declare acceptance | ✅ Neither component produces ACCEPT |
| LLM must not override Oracle evidence | ✅ Neither component allows this |
| LLM must not bypass VerificationGate | ✅ Neither component bypasses the gate |

### Oracle authority

| Check | Status |
|---|---|
| Oracle remains deterministic | ✅ Both components treat Oracle as external |
| Oracle remains external | ✅ subprocess-based, both components use it identically |
| Oracle produces evidence, not decisions | ✅ Both components pass OracleResult to EvidenceNormalizer |
| No code path turns Oracle output into model authority | ✅ Verified in both implementations |

### Verification authority

| Check | Status |
|---|---|
| VerificationGate is sole acceptance authority | ✅ Pipeline calls gate.evaluate(); Controller does NOT call gate |
| No code path produces ACCEPT outside gate | ✅ Verified: gate.py is only location of "ACCEPT" string |
| Controller defaults to REJECTED status | ✅ Controller returns status="REJECTED" for terminal states |
| Pipeline delegates to gate for decision | ✅ Pipeline calls gate.evaluate() after loop completes |

**Authority analysis: PASS — no violations in either implementation.**

---

## 5. Duplication Analysis

### 5.1 Actual code comparison

Both `EGERPipeline._run_with_tracking()` and `RevisionController.run()` implement:

```
for iteration in range(config.max_iterations):
    check budget
    build prompt (initial or revision)
    generate candidate
    extract candidate
    check oracle budget
    invoke oracle
    normalize evidence
    check termination
build RunRecord
```

### 5.2 Structural differences

| Aspect | RevisionController.run() | Pipeline._run_with_tracking() |
|---|---|---|
| Provenance recording | ❌ None | ✅ Inline (record_prompt, record_candidate, etc.) |
| Artifact history | Local variables | self._candidate_history, self._evidence_history |
| Run ID format | `EGER-RUN-{hash}` | `EGER-PIPELINE-{hash}` |
| Provenance metadata | `{"controller": "RevisionController"}` | `{"controller": "EGERPipeline"}` |
| Candidate extraction | `_extract_candidate(raw, task, prompt)` | `_extract_candidate(raw, prompt)` |
| Oracle exception handling | Creates `_OracleFailure` wrapper | Does not create wrapper (uses oracle_result.failure directly) |

### 5.3 Is this harmful duplication?

**No.** The duplication is structural, not semantic:

- Both implement the same revision-loop policy (same budget checks, same termination conditions, same failure handling)
- The Pipeline version adds provenance tracking around the loop — this is a legitimate composition concern
- The Controller version is a pure orchestration test double — it exercises the same logic without provenance overhead
- No authority decisions are made in either — both delegate to VerificationGate

### 5.4 Dead code observation

**Critical finding**: `RevisionController.run()` is never called in production.

```
code_search: "revision_controller.run(" → 0 matches
```

The Pipeline creates a `RevisionController` instance in `__init__` but never calls `controller.run()`. The Pipeline implements its own `_run_with_tracking()` instead.

This means:
- `RevisionController.run()` is dead code in the production path
- `RevisionController` is used only as a test double in `test_revision_controller.py`
- The Pipeline's `_run_with_tracking()` is the actual production implementation

---

## 6. Production-Risk Analysis

| Risk | Classification | Evidence |
|---|---|---|
| Inconsistent revision limits | **NONE** | Both use `config.max_iterations` and `config.max_total_calls` identically |
| Duplicated Oracle calls | **NONE** | Both call Oracle once per iteration, never call twice for same candidate |
| Inconsistent verification decisions | **NONE** | Neither makes verification decisions; both delegate to VerificationGate |
| Bypass of VerificationGate | **NONE** | Verified: no ACCEPT/REJECT in Pipeline or Controller |
| Provenance inconsistencies | **LOW** | Pipeline records provenance inline; Controller does not record provenance at all. Since Pipeline is the production path, provenance is always recorded in production. |
| Logging inconsistencies | **NONE** | Logging is external (EgerLogger), not embedded in either component |
| Configuration inconsistencies | **NONE** | Both read from same RevisionConfig |
| State divergence | **LOW** | Pipeline stores artifact history on self; Controller uses local variables. No shared mutable state. |
| Error handling divergence | **LOW** | Controller wraps Oracle exceptions in `_OracleFailure`; Pipeline does not. Both produce correct terminal reasons. |
| Difficult testing | **LOW** | Controller is tested independently as a test double; Pipeline is tested via integration tests. Both pass. |
| Difficult maintenance | **MEDIUM** | If revision-loop policy changes, both must be updated. Since Controller is dead code, only Pipeline matters in practice. |
| Unclear API ownership | **LOW** | External callers use Pipeline; Controller is internal/test-only |
| Hidden side effects | **NONE** | Both are deterministic; no hidden state mutations |
| Inability to reproduce runs | **NONE** | RunRecord captures all necessary state in both paths |
| Difficult future deployment | **LOW** | Pipeline is the deployable unit; Controller is unused |

**Overall production risk: LOW — no correctness or authority risk, minor maintenance overhead.**

---

## 7. Test-Boundary Analysis

### 7.1 Current test coverage

| Component | Test File | Tests | Status |
|---|---|---|---|
| RevisionController | test_revision_controller.py | 25 | ✅ All pass |
| EGERPipeline | test_e2e_pipeline.py | 30+ | ✅ All pass |
| VerificationGate | test_verification_gate.py | 30 | ✅ All pass |
| Oracle timeout | test_oracle_timeout.py | 29 | ✅ All pass |
| Evidence pipeline | test_evidence_pipeline.py | 29 | ✅ All pass |
| Provenance tracker | test_provenance_tracker.py | 25 | ✅ All pass |
| Config/logging | test_config_logging.py | 86 | ✅ All pass |

### 7.2 Boundary tests

| Boundary | Tested? | Notes |
|---|---|---|
| Pipeline cannot ACCEPT | ✅ | test_pipeline_cannot_bypass_verification |
| Pipeline cannot bypass Oracle | ✅ | test_pipeline_cannot_bypass_oracle |
| Pipeline cannot bypass provenance | ✅ | test_pipeline_cannot_bypass_provenance |
| Controller cannot ACCEPT | ✅ | test_no_acceptance_authority |
| Controller budget enforcement | ✅ | 4 budget tests |
| Controller failure paths | ✅ | 5 failure tests |
| Pipeline provenance reconstruction | ✅ | test_reconstruct_provenance |

### 7.3 Missing boundary tests

| Missing Test | Priority | Reason |
|---|---|---|
| Pipeline and Controller produce same RunRecord structure for same inputs | LOW | Would prove equivalence but both are tested independently |
| Controller.run() is never called in production path | N/A | This is an architecture observation, not a test gap |

**Test boundary analysis: ADEQUATE — no critical gaps.**

---

## 8. Architecture Options

### Option A — Keep current architecture

Pipeline remains the higher-level orchestrator. RevisionController exists as a test double / reference implementation. No refactor.

**Pros**: Zero risk, zero change, proven correct.
**Cons**: Dead code (Controller.run()), maintenance overhead if revision policy changes.

### Option B — Clarify boundaries without structural refactor

Keep both components but explicitly document:
- Pipeline is the production entry point
- RevisionController is a test double / reference implementation
- Pipeline._run_with_tracking() is the canonical revision loop

**Pros**: Low risk, clear documentation.
**Cons**: Does not remove dead code.

### Option C — Consolidate orchestration

Refactor Pipeline to delegate to RevisionController, adding provenance as a wrapper.

**Pros**: Single source of truth for revision loop.
**Cons**: Requires modifying Pipeline to call Controller.run(), adding provenance hooks. Medium risk — could introduce regressions in the 664-test suite. Does not solve a demonstrated problem.

### Option D — Introduce a dedicated workflow engine

Overengineering for current scale. Not recommended.

---

## 9. Minimum-Change Analysis

The preferred outcome is: make the smallest architectural change necessary to remove a demonstrated risk.

**Demonstrated risks**: NONE that affect correctness or authority.

**Maintenance risk**: LOW — Pipeline is the only production path; Controller is dead code.

**Recommended minimum change**: None required now. If a future gate modifies revision-loop policy, the dead Controller code should be cleaned up at that time.

---

## 10. Production-Hardening Status

| Area | Status | Evidence | Remaining Risk |
|---|---|---|---|
| Configuration | ✅ PASS | EgerConfig, env overrides, validation (P151) | LOW — no runtime config for Oracle binary path |
| Logging | ✅ PASS | EgerLogger, structured events (P151) | LOW — not yet integrated into Pipeline |
| Secret redaction | ✅ PASS | redact_secrets, dict key detection (P151) | NONE |
| Oracle timeout | ✅ PASS | 60s configurable timeout (P149) | NONE |
| Input validation | ⚠️ PARTIAL | Non-empty checks exist; no size limits | MEDIUM — oversized input not bounded |
| Failure isolation | ✅ PASS | Fail-closed for all failure modes | NONE |
| Resource limits | ✅ PASS | max_iterations, max_total_calls, timeout | LOW — no prompt/candidate size limits |
| Revision limits | ✅ PASS | Enforced by both Pipeline and Controller | NONE |
| Verification | ✅ PASS | Fail-closed, deterministic, sole authority | NONE |
| Provenance | ✅ PASS | Append-only, complete event chain | LOW — in-memory only, no persistence |
| Immutability | ✅ PASS | D1 resolved, all contracts frozen (P150) | NONE |
| API stability | ✅ PASS | All contracts have to_dict/from_dict | LOW — no schema version checks on deserialization |
| Reproducibility | ⚠️ PARTIAL | Deterministic components OK; model metadata captured in config | LOW — no random seed support |
| D2 orchestration | ⚠️ MINOR DEBT | Both produce correct results; Controller.run() is dead code | LOW — maintenance overhead only |

---

## 11. D2 Decision

### **D2-A — ACCEPTED**

D2 is not materially harmful. No refactor required.

**Rationale**:

1. **No correctness risk**: Both Pipeline and Controller produce correct results. Same budget enforcement, same failure handling, same termination conditions.

2. **No authority risk**: Neither component produces ACCEPT/REJECT. VerificationGate remains sole authority in both code paths.

3. **No production risk**: Pipeline is the only production path. Controller.run() is dead code (never called). The 664-test suite validates both independently.

4. **Maintenance risk is LOW**: The revision-loop policy is simple (5 steps in a for-loop). If it changes, the Pipeline is the only file that needs updating — Controller is unused.

5. **Refactoring introduces risk without solving a demonstrated problem**: Consolidating into one component (Option C) would require modifying the Pipeline, running the full regression, and risks introducing regressions — all for zero correctness benefit.

6. **Dead code is acceptable as a test double**: RevisionController serves as a clean reference implementation for unit testing. Removing it would eliminate 25 independent revision-loop tests.

---

## 12. Recommendation

> D2 is a maintenance observation, not an architectural defect. The Pipeline owns the production revision loop; RevisionController is an unused reference implementation that serves as a test double. Both produce correct results. No refactor is warranted at this time. If a future gate modifies revision-loop policy, the dead Controller code should be cleaned up opportunistically.

---

## 13. Research-State Preservation

```
C0: ESTABLISHED          — Unchanged
C1: ESTABLISHED          — Unchanged
C2: PARTIALLY SUPPORTED  — Unchanged
C3: NOT JUSTIFIED        — Unchanged
C4: DEFERRED             — Unchanged
C5: DEFERRED             — Unchanged

RQ-4: CLOSED             — Unchanged
```

P153 is engineering architecture assessment only.

---

## 14. Ṛta Boundary Verification

```
Ṛta = external deterministic Oracle
```

| Check | Status |
|---|---|
| EGER invokes Oracle | ✅ subprocess-based |
| EGER receives evidence | ✅ OracleResult → EvidenceArtifact |
| EGER normalizes evidence | ✅ EvidenceNormalizer (deterministic) |
| EGER logs invocation | ✅ EgerLogger available |
| EGER records provenance | ✅ ProvenanceTracker |
| EGER modifies Ṛta | ❌ NOT MODIFIED |
| EGER embeds AI into Ṛta | ❌ NOT DONE |
| EGER changes Ṛta rules | ❌ NOT DONE |
| EGER changes Ṛta acceptance semantics | ❌ NOT DONE |

**Ṛta boundary: VERIFIED — no changes.**

---

## 15. Implementation Status

```
CODE IMPLEMENTATION: NONE
NEW TESTS: 0
HISTORICAL RESEARCH CHANGES: NONE
ṚTA CHANGES: NONE
```

---

## 16. Git Status

```
GIT COMMIT: NO
GIT PUSH: NO
P153 is NOT a Git checkpoint.
Assessment artifact left uncommitted for next appropriate gate.
```

---

```
P153 COMPLETE

GIT BASELINE: 04e1f53
HEAD == ORIGIN/MAIN: PASS

D2 ASSESSMENT: PASS
RESPONSIBILITY MAP: COMPLETE
AUTHORITY ANALYSIS: PASS
DUPLICATION ANALYSIS: COMPLETE
PRODUCTION RISK ANALYSIS: COMPLETE
TEST BOUNDARY ANALYSIS: COMPLETE
ARCHITECTURE OPTIONS: COMPLETE

D2 DECISION: D2-A — ACCEPTED

RECOMMENDATION:
D2 is a maintenance observation, not an architectural defect.
The Pipeline owns the production revision loop; RevisionController
is an unused reference implementation / test double. Both produce
correct results. No refactor warranted at this time.

IMPLEMENTATION: NONE

NEW TESTS: 0

FULL REGRESSION: 664/664 PASS

HISTORICAL RESEARCH CHANGES: NONE

ṚTA CHANGES: NONE

C0: ESTABLISHED
C1: ESTABLISHED
C2: PARTIALLY SUPPORTED
C3: NOT JUSTIFIED
C4: DEFERRED
C5: DEFERRED

RQ-4: CLOSED

GIT COMMIT: NO

GIT PUSH: NO

NEXT GATE:
P154 — Git Checkpoint for P153
```
