# EGER-P155 — Input Validation & Size Limits

## Gate

P155 — Input Validation & Resource-Boundary Hardening

## Date

2026-09-02

## Purpose

Harden EGER's externally reachable engineering interfaces against malformed, oversized, pathological, or resource-exhausting inputs while preserving all established behavior and authority boundaries.

**No architecture redesign. No research conclusions changed. No Ṛta modifications.**

---

## 1. Threat Model

### Size exhaustion

| Threat | Current behavior | P155 mitigation |
|---|---|---|
| Extremely large candidate SDC text | No limit — passed to Oracle subprocess | MAX_SDC_TEXT_LENGTH = 100,000 |
| Extremely large task fields | No limit — used in prompt construction | Per-field limits (1K–50K) |
| Excessive findings count | No limit — stored in memory | MAX_FINDINGS_COUNT = 1,000 |
| Excessive constraint count | No limit — included in prompt | MAX_CONSTRAINTS_COUNT = 100 |
| Excessive revision iterations | Min bound only | Max bound = 100 |
| Excessive total calls | Min bound only | Max bound = 500 |

### Structural exhaustion

| Threat | Current behavior | P155 mitigation |
|---|---|---|
| Oversized finding messages | No limit | MAX_FINDING_MESSAGE_LENGTH = 10,000 |
| Oversized identifiers | No limit | Per-contract limits (1K) |
| Excessive temperature/max_tokens | No upper bound | Bounds enforced |

### Invalid input

| Threat | Current behavior | P155 mitigation |
|---|---|---|
| Non-string sdc_text | TypeError at hash | Explicit TypeError before hash |
| Invalid temperature range | No validation | 0.0–2.0 bounds |
| Invalid max_tokens range | No validation | 1–128,000 bounds |

---

## 2. Validation Philosophy Applied

| Principle | Application |
|---|---|
| A — Validate at boundaries | All validation in `__post_init__` and `build_candidate()` |
| B — Fail closed | Oversized input raises ValueError before Oracle/LLM invocation |
| C — Preserve valid behavior | All existing valid inputs continue to work |
| D — Avoid semantic overreach | No restrictions on valid SDC syntax or command names |
| E — Deterministic limits | All limits are explicit constants in `eger/contracts.py` |

---

## 3. Limits Selected

| Input | Constant | Limit | Rationale |
|---|---|---|---|
| `task_id` | MAX_TASK_ID_LENGTH | 1,000 | Identifier; prevents hash/storage issues |
| `design_context` | MAX_DESIGN_CONTEXT_LENGTH | 50,000 | Prompt content; prevents token limit issues |
| `objective` | MAX_OBJECTIVE_LENGTH | 50,000 | Prompt content; prevents token limit issues |
| `initial_sdc` | MAX_INITIAL_SDC_LENGTH | 100,000 | SDC content; same as candidate |
| `constraints` count | MAX_CONSTRAINTS_COUNT | 100 | Prompt content; prevents token limit issues |
| `constraint` item | MAX_CONSTRAINT_LENGTH | 5,000 | Prompt content |
| `sdc_text` (candidate) | MAX_SDC_TEXT_LENGTH | 100,000 | Oracle subprocess input; prevents resource exhaustion |
| `artifact_id` | MAX_ARTIFACT_ID_LENGTH | 1,000 | Identifier; prevents storage issues |
| `finding_id` | MAX_FINDING_ID_LENGTH | 1,000 | Identifier |
| `finding.message` | MAX_FINDING_MESSAGE_LENGTH | 10,000 | Evidence content |
| `evidence_id` | MAX_EVIDENCE_ID_LENGTH | 1,000 | Identifier |
| `findings` count | MAX_FINDINGS_COUNT | 1,000 | Evidence memory; prevents explosion |
| `max_iterations` | (inline) | 100 | Prevents unbounded execution |
| `max_total_calls` | (inline) | 500 | Prevents unbounded execution |
| `temperature` | (inline) | 0.0–2.0 | Valid range for LLM sampling |
| `max_tokens` | (inline) | 1–128,000 | Valid range for LLM output |

---

## 4. Validation Behavior

### TaskDefinition

```python
TaskDefinition(
    task_id="A" * 1001,  # → ValueError: task_id length exceeds maximum
    ...
)
```

### build_candidate

```python
build_candidate("A" * 100001)  # → ValueError: sdc_text length exceeds maximum
build_candidate(123)            # → TypeError: sdc_text must be str
```

### Finding

```python
Finding(
    finding_id="F" * 1001,  # → ValueError: finding_id length exceeds maximum
    message="M" * 10001,    # → ValueError: finding message length exceeds maximum
    ...
)
```

### EvidenceArtifact

```python
EvidenceArtifact(
    findings=tuple(f for ... in range(1001)),  # → ValueError: findings count exceeds maximum
    ...
)
```

### RevisionConfig

```python
RevisionConfig(max_iterations=101)  # → ValueError: max_iterations must be <= 100
RevisionConfig(temperature=2.1)     # → ValueError: temperature must be between 0.0 and 2.0
```

---

## 5. Failure Semantics

```
Input validation FAIL
    ↓
ValueError / TypeError raised
    ↓
Oracle is NOT invoked
    ↓
Prompt is NOT constructed
    ↓
VerificationGate is NOT reached
    ↓
No ACCEPT possible
```

**Fail-closed: VERIFIED**

---

## 6. Oracle Pre-Validation

The validation chain before Oracle invocation:

```
TaskDefinition.__post_init__  (size limits)
    ↓
build_candidate()  (sdc_text size limit)
    ↓
Oracle.validate()  (P149 timeout boundary)
    ↓
EvidenceNormalizer  (severity validation)
    ↓
VerificationGate  (sole authority)
```

Oversized input is rejected before Oracle invocation.

---

## 7. Files Changed

### New

| File | Purpose |
|---|---|
| `eger/contracts.py` | Shared size-limit constants |
| `tests/test_input_validation.py` | 70 deterministic tests |
| `research/implementation/EGER-P155-INPUT-VALIDATION-SIZE-LIMITS-001.md` | This record |
| `research/implementation/EGER-CHANGE-027.md` | Change control |

### Modified

| File | Change |
|---|---|
| `eger/task/definition.py` | Added size limits to `__post_init__` |
| `eger/engineer/candidate.py` | Added size/type validation to `build_candidate()` |
| `eger/evidence/schemas.py` | Added size limits to Finding and EvidenceArtifact `__post_init__` |
| `eger/revision/record.py` | Added max bounds to RevisionConfig `__post_init__` |

---

## 8. Backward Compatibility

| Component | Impact |
|---|---|
| TaskDefinition constructors | ✅ All existing valid inputs still work |
| build_candidate() | ✅ All existing valid inputs still work |
| Finding constructors | ✅ All existing valid inputs still work |
| EvidenceArtifact constructors | ✅ All existing valid inputs still work |
| RevisionConfig constructors | ✅ All existing valid inputs still work |
| Serialization round-trips | ✅ Unchanged |
| CandidateArtifact immutability | ✅ Unchanged (frozen) |
| VerificationGate behavior | ✅ Unchanged |
| Oracle timeout | ✅ Unchanged (P149) |
| Configuration precedence | ✅ Unchanged (P151) |

---

## 9. Test Results

### New Tests

```
70 tests — ALL PASSED
```

| Category | Tests | Status |
|---|---|---|
| TaskDefinition size limits | 12 | ✅ All passed |
| TaskDefinition existing validation | 5 | ✅ All passed |
| CandidateArtifact size limits | 7 | ✅ All passed |
| CandidateArtifact backward compat | 3 | ✅ All passed |
| Finding size limits | 6 | ✅ All passed |
| Finding existing validation | 3 | ✅ All passed |
| EvidenceArtifact findings limit | 5 | ✅ All passed |
| EvidenceArtifact existing validation | 4 | ✅ All passed |
| RevisionConfig max bounds | 10 | ✅ All passed |
| RevisionConfig existing validation | 3 | ✅ All passed |
| Fail-closed verification | 3 | ✅ All passed |
| Backward compatibility | 7 | ✅ All passed |
| Serialization round-trips | 2 | ✅ All passed |

### Full Regression

```
Previous baseline: 664 tests
New tests: 70
Current total: 734 tests
Failures: 0
```

All 734 tests pass.

---

## 10. Security Review

| Check | Result |
|---|---|
| Oversized input rejected before Oracle | ✅ VERIFIED |
| Oversized input rejected before LLM prompt | ✅ VERIFIED |
| No secret leakage through validation errors | ✅ ValueError messages contain only field names and sizes |
| No execution of supplied input | ✅ Validation is pure string length checking |
| No semantic restrictions on valid SDC | ✅ Only size limits, no content filtering |

---

## 11. Research State Preservation

```
C0: ESTABLISHED          — Unchanged
C1: ESTABLISHED          — Unchanged
C2: PARTIALLY SUPPORTED  — Unchanged
C3: NOT JUSTIFIED        — Unchanged
C4: DEFERRED             — Unchanged
C5: DEFERRED             — Unchanged

RQ-4: CLOSED             — Unchanged
```

P155 is engineering hardening, NOT research evidence.

---

## 12. Debt State

| Debt | Status |
|---|---|
| D1 — CandidateArtifact mutability | RESOLVED (P150) |
| D2 — Pipeline/Controller overlap | ACCEPTED (P153, D2-A) |

---

## 13. What P155 Does NOT Do

- Does NOT restrict valid SDC syntax
- Does NOT filter SDC content semantically
- Does NOT change verification policy
- Does NOT modify Oracle authority
- Does NOT refactor D2
- Does NOT reopen RQ-4
- Does NOT change C0–C5 classifications
- Does NOT execute experiments
- Does NOT modify historical artifacts

---

```
P155 COMPLETE
INPUT VALIDATION & SIZE LIMITS COMPLETE

INPUT-BOUNDARY AUDIT: PASS
THREAT MODEL: COMPLETE
VALIDATION: PASS
SIZE LIMITS: PASS
RESOURCE BOUNDS: PASS
FAIL-CLOSED: PASS
ORACLE PRE-VALIDATION: PASS
REVISION LIMIT INTEGRATION: PASS
LOGGING SAFETY: PASS
PROVENANCE SAFETY: PASS
SECURITY REVIEW: PASS
BACKWARD COMPATIBILITY: PASS

NEW TESTS: 70
FULL REGRESSION: 734/734 PASS

IMPLEMENTATION:
Added size limits to TaskDefinition, build_candidate, Finding,
EvidenceArtifact, and max bounds to RevisionConfig. Created
eger/contracts.py with shared constants.

CONFIGURATION CHANGES: None (limits are contract-level, not config)

FILES CHANGED: 8

D1: RESOLVED
D2: ACCEPTED — NO REFACTOR

C0: ESTABLISHED
C1: ESTABLISHED
C2: PARTIALLY SUPPORTED
C3: NOT JUSTIFIED
C4: DEFERRED
C5: DEFERRED

RQ-4: CLOSED

HISTORICAL RESEARCH CHANGES: NONE
ṚTA CHANGES: NONE

GIT COMMIT: NO
GIT PUSH: NO

REMAINING RISKS:
- In-memory provenance has no persistence (deferred)
- No prompt-size boundary beyond field limits (deferred)
- No Oracle stdout/stderr size limit (deferred)

NEXT GATE:
P156 — Git Checkpoint for P155
```
