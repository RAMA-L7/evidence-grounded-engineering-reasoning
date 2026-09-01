# EGER-P150 — Contract Hardening & Interface Stability

## Gate

P150 — Implementation + Deterministic Testing

## Date

2026-09-01

## Purpose

Resolve D1 (CandidateArtifact.verified mutability) and improve interface stability across all core contracts. Ensure all contracts are immutable, serializable, and have consistent authority boundaries.

**No historical artifacts changed. No research conclusions modified. No live model calls.**

---

## 1. D1 Problem

### 1.1 Original Debt (from P145/P146)

```
D1 — CandidateArtifact.verified mutability
```

`CandidateArtifact` was a mutable dataclass with a `verified: bool = False` field. While no code ever set it to `True`, the mutable field represented a potential authority violation:

- A candidate could theoretically self-promote to `verified=True`
- The VerificationGate did not check `candidate.verified`
- But the PromptBuilder included `Verified: {candidate.verified}` in prompts

### 1.2 Authority Analysis

| Risk | Assessment |
|------|-----------|
| Candidate self-promotes via `verified` field | LOW — no code sets it to True |
| PromptBuilder trusts `verified` field | NO — includes as data only |
| VerificationGate trusts `verified` field | NO — makes independent decision |
| Other components trust `verified` | NO — no code reads it for decisions |

**Classification**: MINOR DEBT — no actual authority violation, but mutable state contradicts the immutable architecture.

---

## 2. Solution

### 2.1 Chosen Approach

**Make `CandidateArtifact` frozen and remove the `verified` field.**

This is the smallest clean solution consistent with the existing architecture:

- `CandidateArtifact` becomes `@dataclass(frozen=True)` — immutable once created
- `verified` field removed entirely — verification authority belongs solely to VerificationGate
- `build_candidate()` updated to not pass `verified=False`
- `to_dict()`/`from_dict()` added for serialization round-trip
- PromptBuilder no longer includes "Verified:" in prompts

### 2.2 Why This Works

1. **No code sets `verified=True`** — removal has zero behavioral impact
2. **VerificationGate never checked `verified`** — removal has zero decision impact
3. **Frozen dataclass** — prevents all field mutation, matching the architecture's immutability invariant
4. **Authority separation** — VerificationResult (frozen) is the sole source of ACCEPT/REJECT

### 2.3 What P150 Does NOT Change

- VerificationGate behavior (unchanged)
- EvidenceArtifact (already frozen)
- TaskDefinition (already frozen)
- PromptRequest (already frozen)
- RevisionConfig (already frozen)
- RunRecord (already frozen)
- VerificationResult (already frozen)

---

## 3. Files Changed

### 3.1 Modified

| File | Change |
|------|--------|
| `eger/engineer/candidate.py` | `CandidateArtifact` → `frozen=True`, removed `verified` field, added `from_dict()`, updated `build_candidate()` |
| `eger/prompting/builder.py` | Removed `Verified: {candidate.verified}` from prompt text |
| `tests/test_core_contracts.py` | Updated `test_candidate_starts_unverified` → `test_candidate_is_frozen`, added `TestCandidateArtifact` class with 11 tests, added authority-boundary tests |
| `tests/test_prompt_builder.py` | Updated `test_revision_preserves_verified_state` → `test_revision_preserves_candidate_metadata` |
| `tests/test_verification_gate.py` | Removed `candidate.verified` references, updated `test_candidate_not_mutated` |
| `tests/test_llm_proposal.py` | Updated `test_T_P010_002_unverified` — no longer checks `.verified` field |

---

## 4. Interface Impact

### 4.1 CandidateArtifact

```python
# Before:
@dataclass
class CandidateArtifact:
    artifact_id: str
    sdc_text: str
    input_hash: str
    candidate_hash: str
    provision: Dict[str, Any]
    schema_version: str = SCHEMA_CANDIDATE
    created_at: str = ""
    verified: bool = False  # MUTABLE

# After:
@dataclass(frozen=True)
class CandidateArtifact:
    artifact_id: str
    sdc_text: str
    input_hash: str
    candidate_hash: str
    provision: Dict[str, Any]
    schema_version: str = SCHEMA_CANDIDATE
    created_at: str = ""
    # verified field REMOVED
```

### 4.2 CandidateArtifact.to_dict()

```python
# Before:
def to_dict(self):
    return {
        ...,
        "verified": self.verified,  # REMOVED
        "provision": self.provision,
        ...
    }

# After:
def to_dict(self):
    return {
        ...,
        "provision": dict(self.provision),  # Explicit copy
        ...
    }
```

### 4.3 CandidateArtifact.from_dict() (NEW)

```python
@classmethod
def from_dict(cls, d: Dict[str, Any]) -> CandidateArtifact:
    return cls(
        artifact_id=d["artifact_id"],
        sdc_text=d["sdc_text"],
        input_hash=d["input_hash"],
        candidate_hash=d["candidate_hash"],
        provision=dict(d.get("provision", {})),
        schema_version=d.get("schema_version", SCHEMA_CANDIDATE),
        created_at=d.get("created_at", ""),
    )
```

### 4.4 PromptBuilder

```python
# Before:
sections.append(f"Verified: {candidate.verified}")

# After:
# Line removed — verified field no longer exists
```

---

## 5. Compatibility Impact

| Consumer | Impact | Action |
|----------|--------|--------|
| `build_candidate()` | Removed `verified=False` arg | Updated |
| `PromptBuilder` | Removed `candidate.verified` reference | Updated |
| `VerificationGate` | Never checked `verified` | No change needed |
| `RevisionController` | Uses `candidate.sdc_text`, `candidate.candidate_hash` | No change needed |
| `EGERPipeline` | Same as RevisionController | No change needed |
| `ProvenanceTracker` | Records by artifact_id, not verified | No change needed |
| `EvidenceNormalizer` | Takes Oracle result, not candidate | No change needed |
| Tests | Reference `.verified` | Updated |

### Backward Compatibility

- `EvidenceOracle()` without timeout: ✅ Unchanged (P149)
- `validate()` signature: ✅ Unchanged
- `CandidateArtifact()` construction: ⚠️ No longer accepts `verified` kwarg
- `to_dict()` output: ⚠️ No longer includes `verified` key
- `from_dict()`: ✅ New method — backward compatible

---

## 6. Serialization Impact

| Contract | Serialization | Hash Stability |
|----------|--------------|---------------|
| TaskDefinition | ✅ to_dict/from_dict | ✅ Deterministic |
| PromptRequest | ✅ to_dict/from_dict | ✅ Deterministic |
| CandidateArtifact | ✅ to_dict/from_dict | ✅ Deterministic |
| EvidenceArtifact | ✅ to_dict/from_dict | ✅ Deterministic |
| Finding | ✅ to_dict/from_dict | N/A (frozen) |
| FindingSummary | ✅ to_dict | N/A (computed) |
| VerificationResult | ✅ to_dict/from_dict | N/A (decision) |
| RevisionConfig | ✅ to_dict/from_dict | N/A (config) |
| RunRecord | ✅ to_dict/from_dict | N/A (record) |

### Round-Trip Verification

All core contracts support:
```
object → to_dict() → from_dict() → equivalent object
```

---

## 7. Provenance Impact

Provenance recording is **unaffected**:

- `ProvenanceTracker.record_candidate()` takes `candidate_id` and `candidate_hash` — not `verified`
- `VerificationResult` (frozen) carries the decision — not CandidateArtifact
- RunRecord records `final_decision` and `status` — not candidate verification state

---

## 8. Security Impact

| Check | Result |
|-------|--------|
| Candidate self-promotion | ✅ ELIMINATED — no `verified` field exists |
| Mutable authority state | ✅ ELIMINATED — frozen dataclass |
| Prompt injection via verified | ✅ ELIMINATED — field removed |
| Credential leakage | ✅ No changes affect credentials |

---

## 9. Test Results

### 9.1 New Tests

```
14 new tests — ALL PASSED
```

| Category | Tests | Status |
|----------|-------|--------|
| CandidateArtifact construction | 3 | ✅ All passed |
| CandidateArtifact immutability | 2 | ✅ All passed |
| CandidateArtifact serialization | 3 | ✅ All passed |
| CandidateArtifact authority boundary | 3 | ✅ All passed |
| Authority safety (existing) | 5 | ✅ All passed |

### 9.2 Full Regression

```
Previous baseline: 564 tests
New tests: 14
Current total: 578 tests
Failures: 0
```

All 578 tests pass.

---

## 10. Remaining Contract Debt

| Debt | Status | Notes |
|------|--------|-------|
| D1 — CandidateArtifact mutability | ✅ RESOLVED | Frozen, verified removed |
| D2 — Pipeline/Controller overlap | ⏳ NOT ADDRESSED | Separate gate (P153) |
| Schema version checks in from_dict | ⏳ NOT ADDRESSED | Future gate |
| EvidenceArtifact from_dict schema validation | ⏳ NOT ADDRESSED | Future gate |

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

P150 is engineering hardening, NOT research evidence.

---

```
P150 COMPLETE
CONTRACT HARDENING COMPLETE

D1: RESOLVED

CANDIDATE IMMUTABILITY: PASS
VERIFICATION AUTHORITY: PASS
INTERFACE STABILITY: PASS
SERIALIZATION: PASS
PROVENANCE COMPATIBILITY: PASS
FAIL-CLOSED: PASS

NEW TESTS: 14
FULL REGRESSION: 578/578 PASS
SECURITY: NO ISSUES
HISTORICAL PRESERVATION: PASS

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
P151 — Configuration & Logging (structured logging, model metadata, environment overrides)
```
