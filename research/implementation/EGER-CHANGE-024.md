# EGER-CHANGE-024 — Oracle Subprocess Timeout

## Change ID

CHANGE-024

## Date

2026-09-01

## Gate

P149 — Oracle Timeout & Resource-Limit Hardening

## Classification

Engineering hardening — P0 production blocker resolution

## Summary

Add explicit subprocess timeout to Oracle execution boundary to prevent indefinite pipeline hangs.

## Motivation

P148 identified: `eger/oracle/adapter.py` invokes the Oracle through `subprocess.run()` without a timeout. A hung Oracle process can block EGER indefinitely. This is a P0 production blocker.

## Changes

### Modified Files

| File | Change |
|------|--------|
| `eger/oracle/adapter.py` | Added `timeout_seconds` parameter to `EvidenceOracle.__init__()`, `DEFAULT_ORACLE_TIMEOUT_SECONDS = 60` constant, `MINIMUM_ORACLE_TIMEOUT_SECONDS = 1` constant, `subprocess.run(timeout=self.timeout_seconds)` in `_invoke_rta()`, `subprocess.TimeoutExpired` handling in `_invoke_rta()`, `exit_code == -1` classification in `validate()` |

### New Files

| File | Purpose |
|------|---------|
| `tests/test_oracle_timeout.py` | 29 deterministic tests for timeout configuration, behavior, failure propagation, backward compatibility, and security |

## Interface Changes

### EvidenceOracle.__init__

```python
# Before:
def __init__(self, rta_cli=None, oracle_revision=ORACLE_REVISION):

# After:
def __init__(self, rta_cli=None, oracle_revision=ORACLE_REVISION, timeout_seconds=60):
```

- `timeout_seconds` is optional with default 60
- Backward compatible — existing callers work unchanged
- Raises `ValueError` if `timeout_seconds < 1`

### Exit Code Classification

```python
# New exit code handling in validate():
if exit_code == -1:
    # Timeout — classified as ORACLE_FAILURE
    return OracleResult(is_success=False, failure=OracleFailure(kind="ORACLE_FAILURE", exit_code=-1, ...))
```

## Failure Semantics

```
Oracle subprocess exceeds timeout
    ↓
subprocess.TimeoutExpired caught in _invoke_rta()
    ↓
OracleResult(is_success=False, failure=OracleFailure(kind="ORACLE_FAILURE", exit_code=-1))
    ↓
EvidenceNormalizer.normalize_failure()
    ↓
EvidenceArtifact(oracle_status="ORACLE_FAILURE", evidence_scope="UNSUPPORTED", has_errors=True)
    ↓
VerificationGate.evaluate()
    ↓
REJECT
```

## Test Results

```
New tests: 29
Full regression: 564/564 PASS
New failures: 0
```

## Backward Compatibility

- `EvidenceOracle()` without timeout arg: ✅ Works (default 60s)
- `validate()` signature: ✅ Unchanged
- `OracleResult` type: ✅ Unchanged
- `OracleFailure` type: ✅ Unchanged
- All existing tests: ✅ Pass

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Existing callers break | None | None | Default value preserves behavior |
| Timeout too aggressive | Low | Medium | 60s default, configurable |
| Timeout too lenient | Low | Low | Configurable per-deployment |
| False acceptance on timeout | None | High | Architecture prevents (verified) |

## Research Impact

None. This is engineering hardening only.

## Historical Artifacts Modified

None.
