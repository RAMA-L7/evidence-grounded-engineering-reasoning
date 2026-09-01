# EGER-CHANGE-025 — CandidateArtifact Immutability (D1 Resolution)

## Change ID

CHANGE-025

## Date

2026-09-01

## Gate

P150 — Contract Hardening & Interface Stability

## Classification

Engineering hardening — D1 architectural debt resolution

## Summary

Make `CandidateArtifact` frozen (immutable) and remove the `verified` field. Add `from_dict()` for serialization round-trip. Update PromptBuilder to remove verified reference.

## Motivation

D1 (from P145): `CandidateArtifact.verified` was mutable, contradicting the architecture's immutability invariant. While no code ever set it to `True` and VerificationGate never checked it, the mutable field represented a potential authority violation and architectural inconsistency.

## Changes

### Modified Files

| File | Change |
|------|--------|
| `eger/engineer/candidate.py` | `CandidateArtifact` → `frozen=True`, removed `verified` field, added `from_dict()`, updated `to_dict()` to use `dict(self.provision)`, updated `build_candidate()` to not pass `verified=False` |
| `eger/prompting/builder.py` | Removed `Verified: {candidate.verified}` line from prompt text |
| `tests/test_core_contracts.py` | Updated `test_candidate_starts_unverified` → `test_candidate_is_frozen`, added `TestCandidateArtifact` class (11 tests), added 4 authority-boundary tests |
| `tests/test_prompt_builder.py` | Updated `test_revision_preserves_verified_state` → `test_revision_preserves_candidate_metadata` |
| `tests/test_verification_gate.py` | Removed `candidate.verified` references, updated `test_candidate_not_mutated` |
| `tests/test_llm_proposal.py` | Updated `test_T_P010_002_unverified` — no longer checks `.verified` field |

## Interface Changes

### CandidateArtifact

```python
# Before:
@dataclass
class CandidateArtifact:
    ...
    verified: bool = False  # MUTABLE

# After:
@dataclass(frozen=True)
class CandidateArtifact:
    ...  # verified field REMOVED
```

### CandidateArtifact.to_dict

```python
# Before: included "verified" key
# After: "verified" key removed, provision uses dict() copy
```

### CandidateArtifact.from_dict (NEW)

```python
@classmethod
def from_dict(cls, d: Dict[str, Any]) -> CandidateArtifact:
    ...
```

### PromptBuilder

```python
# Before: sections.append(f"Verified: {candidate.verified}")
# After: line removed
```

## Authority Impact

| Before | After |
|--------|-------|
| CandidateArtifact.verified = False (mutable) | CandidateArtifact has no verified field |
| Potential for self-promotion | Self-promotion impossible |
| VerificationGate ignores verified | N/A — field doesn't exist |

## Test Results

```
New tests: 14
Full regression: 578/578 PASS
New failures: 0
```

## Backward Compatibility

- `CandidateArtifact()` no longer accepts `verified` kwarg
- `to_dict()` output no longer includes `verified` key
- `from_dict()` is new — fully backward compatible
- `build_candidate()` no longer sets `verified=False`
- All existing callers that used `.sdc_text`, `.candidate_hash`, `.artifact_id` — unchanged

## Research Impact

None. This is engineering hardening only.

## Historical Artifacts Modified

None.
