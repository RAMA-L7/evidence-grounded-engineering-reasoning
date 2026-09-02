# EGER-CHANGE-027 — Input Validation & Size Limits

## Change ID

EGER-CHANGE-027

## Date

2026-09-02

## Gate

P155 — Input Validation & Resource-Boundary Hardening

## Summary

Add explicit size limits and validation to all externally reachable engineering interfaces. Create shared validation constants in `eger/contracts.py`. Reject oversized/malformed inputs before Oracle invocation.

---

## Files Added

| File | Purpose |
|------|---------|
| `eger/contracts.py` | Shared size-limit constants (MAX_SDC_TEXT_LENGTH, etc.) |
| `tests/test_input_validation.py` | 70 deterministic tests for validation boundaries |
| `research/implementation/EGER-P155-INPUT-VALIDATION-SIZE-LIMITS-001.md` | Implementation record |
| `research/implementation/EGER-CHANGE-027.md` | This change control |

## Files Modified

| File | Change |
|------|--------|
| `eger/task/definition.py` | Added size limits to `__post_init__` (task_id, design_context, objective, initial_sdc, constraints) |
| `eger/engineer/candidate.py` | Added size/type validation to `build_candidate()` (sdc_text, artifact_id) |
| `eger/evidence/schemas.py` | Added size limits to Finding and EvidenceArtifact `__post_init__` (finding_id, message, evidence_id, findings count) |
| `eger/revision/record.py` | Added max bounds to RevisionConfig `__post_init__` (iterations, calls, temperature, max_tokens) |

## Behavioral Changes

- **Oversized inputs now raise ValueError/TypeError at construction time**
- All existing valid inputs continue to work unchanged
- No semantic restrictions on valid SDC content
- No changes to verification policy or authority boundaries

## Configuration Impact

None — limits are contract-level constants, not runtime configuration.

## Security Impact

- Oversized input rejected before Oracle invocation
- Oversized input rejected before LLM prompt construction
- No secret leakage through validation error messages
- No execution of supplied input content

## Compatibility Impact

- Fully backward compatible for all valid inputs
- Invalid/oversized inputs that previously caused undefined behavior now raise clear errors

## Test Impact

- New tests: 70
- Modified tests: 0
- Previous baseline: 664
- Current total: 734
- Failures: 0

## Research State

```
C0: ESTABLISHED
C1: ESTABLISHED
C2: PARTIALLY SUPPORTED
C3: NOT JUSTIFIED
C4: DEFERRED
C5: DEFERRED
RQ-4: CLOSED
```

No research conclusions changed.
