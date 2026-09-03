# EGER CHANGE-037 — OpenSTA Adapter design_name Security Hardening (P166)

## Purpose

Resolve P165 FINDING-004: Tcl injection via `design_name`. Add input validation to prevent Tcl command injection.

## Baseline

- **Commit:** 1821aac12db3b4c4670fdbd1b816e776e6c9e479
- **Branch:** main
- **Prior change:** CHANGE-036 (P165 — Contract Validation)

## Changes

### Production Code

| File | Change |
|------|--------|
| `eger/oracle/opensta_adapter.py` | Added `_validate_design_name()`, validation call in `validate()` |

### Tests

| File | Change |
|------|--------|
| `tests/test_opensta_security.py` | NEW — 41 security tests |
| `tests/test_opensta_adapter_contract.py` | Updated injection tests to verify rejection |

### Documentation

| File | Change |
|------|--------|
| `research/implementation/EGER-P166-OPENSTA-DESIGN-NAME-SECURITY-HARDENING-001.md` | NEW |
| `research/implementation/EGER-CHANGE-037.md` | NEW (this file) |

## Validation Contract

```python
_DESIGN_NAME_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_/]*$")
MAX_DESIGN_NAME_LENGTH = 256
```

Invalid names return `INVALID_REQUEST` failure before any subprocess execution.

## Test Results

- **P166 security tests:** 41/41 PASS
- **Full regression:** 864/864 PASS

## Ṛta Impact

None.

## Historical Research Impact

None.

## Decision

PASS — P165 FINDING-004 resolved, no remaining security defects.
