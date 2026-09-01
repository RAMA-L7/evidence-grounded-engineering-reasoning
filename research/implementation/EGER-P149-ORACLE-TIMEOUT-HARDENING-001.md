# EGER-P149 — Oracle Timeout & Resource-Limit Hardening

## Gate

P149 — Implementation + Deterministic Testing

## Date

2026-09-01

## Purpose

Resolve the P0 production blocker identified in P148: Oracle subprocess has no timeout. A hung Oracle process can block the EGER pipeline indefinitely.

**No historical artifacts changed. No research conclusions modified. No live model calls.**

---

## 1. Problem Statement

P148 identified:

> `eger/oracle/adapter.py` invokes the Oracle through `subprocess.run()` without a timeout. A hung Oracle process can block EGER indefinitely.

This is classified as **P0 — production blocker**.

---

## 2. Solution Design

### 2.1 Configuration

Added `timeout_seconds` parameter to `EvidenceOracle.__init__()`:

| Property | Value |
|----------|-------|
| Default | 60 seconds |
| Minimum | 1 second |
| Maximum | Unlimited (deployment-configurable) |
| Validation | `ValueError` if < 1 |
| Location | `eger/oracle/adapter.py` constants |

Rationale for 60s default:
- Oracle typically completes in <5s for well-formed SDC
- 60s provides generous headroom
- Prevents indefinite hangs
- Configurable per-deployment

### 2.2 Implementation

1. `EvidenceOracle.__init__()` accepts `timeout_seconds` parameter
2. `_invoke_rta()` passes `timeout=self.timeout_seconds` to `subprocess.run()`
3. `subprocess.TimeoutExpired` is caught in `_invoke_rta()`
4. Timeout returns `(stdout, stderr, exit_code=-1)` — consistent tuple interface
5. `validate()` classifies `exit_code == -1` as `ORACLE_FAILURE` with kind `TIMEOUT`
6. Failure propagates through existing chain: `OracleFailure` → `EvidenceNormalizer.normalize_failure()` → `EvidenceArtifact(oracle_status="ORACLE_FAILURE")` → `VerificationGate` → `REJECT`

### 2.3 Exit Code Classification

| Exit Code | Classification | Prior | P149 |
|-----------|---------------|-------|------|
| 0 | SUCCESS | ✅ | ✅ Unchanged |
| 1 | SUCCESS (with findings) | ✅ | ✅ Unchanged |
| 2 | INVALID_REQUEST or ORACLE_FAILURE | ✅ | ✅ Unchanged |
| 3 | ORACLE_FAILURE | ✅ | ✅ Unchanged |
| -1 | ORACLE_FAILURE (timeout) | N/A | ✅ **New** |
| 127 | ORACLE_FAILURE (binary not found) | ✅ | ✅ Unchanged |

---

## 3. Timeout Failure Semantics

### 3.1 Chain Verification

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
REJECT (oracle_status != SUCCESS)
```

### 3.2 Safety Guarantee

- Timeout **never** produces `is_success=True`
- Timeout **never** produces zero-error evidence
- Timeout **never** results in `ACCEPT`
- Timeout **never** gives Oracle authority to accept
- VerificationGate remains sole acceptance authority

### 3.3 Classification

| Property | Classification |
|----------|---------------|
| Timeout → ORACLE_FAILURE | ✅ FAIL CLOSED |
| Timeout → REJECT | ✅ CORRECT |
| Timeout → no false acceptance | ✅ VERIFIED |
| Authority boundary preserved | ✅ VERIFIED |

---

## 4. Files Changed

### 4.1 Modified

| File | Change |
|------|--------|
| `eger/oracle/adapter.py` | Added `timeout_seconds` parameter, `DEFAULT_ORACLE_TIMEOUT_SECONDS` constant, `MINIMUM_ORACLE_TIMEOUT_SECONDS` constant, timeout handling in `_invoke_rta()`, timeout classification in `validate()` |

### 4.2 New

| File | Purpose |
|------|---------|
| `tests/test_oracle_timeout.py` | 29 deterministic tests for timeout behavior |

---

## 5. Test Results

### 5.1 New Tests (P149)

```
29 tests — ALL PASSED
```

| Category | Tests | Status |
|----------|-------|--------|
| Configuration validation | 8 | ✅ All passed |
| Timeout behavior | 7 | ✅ All passed |
| Failure propagation | 4 | ✅ All passed |
| _invoke_rta boundary | 4 | ✅ All passed |
| Backward compatibility | 3 | ✅ All passed |
| Security | 3 | ✅ All passed |

### 5.2 Full Regression

```
Previous baseline: 535 tests
New tests: 29
Current total: 564 tests
Failures: 0
```

All 564 tests pass.

---

## 6. Backward Compatibility

| Check | Result |
|-------|--------|
| `EvidenceOracle()` call without timeout arg | ✅ Works (uses default 60s) |
| `validate()` signature unchanged | ✅ No new required parameters |
| `OracleResult` type unchanged | ✅ Same interface |
| `OracleFailure` type unchanged | ✅ Same interface |
| `EvidenceNormalizer` unchanged | ✅ Works with timeout failure |
| `VerificationGate` unchanged | ✅ Works with timeout evidence |
| `RevisionController` unchanged | ✅ Works with timeout oracle |
| `EGERPipeline` unchanged | ✅ Works with timeout oracle |
| Existing T004 test (missing binary) | ✅ Still passes |

---

## 7. Security Review

| Check | Result |
|-------|--------|
| Credential leakage | ✅ No credentials in timeout message |
| Shell injection | ✅ `shell=True` not used |
| Environment leakage | ✅ `os.environ.copy()` read-only |
| Unsafe subprocess | ✅ `timeout=` parameter enforced |
| Unsafe temp files | ✅ Cleanup on timeout path |
| Privilege escalation | ✅ Timeout cannot become ACCEPT |
| Authority boundary | ✅ VerificationGate remains sole authority |

---

## 8. Authority Boundary Verification

| Component | P149 Impact |
|-----------|------------|
| LLM → Candidate | Unchanged |
| Oracle → Evidence | Timeout produces failure evidence |
| VerificationGate → Decision | Timeout evidence → REJECT |
| CandidateArtifact cannot self-promote | Unchanged |
| VerificationGate sole authority | Unchanged |

**No authority violations introduced.**

---

## 9. Research State Preservation

```
C0: ESTABLISHED          — Unchanged
C1: ESTABLISHED          — Unchanged
C2: PARTIALLY SUPPORTED  — Unchanged
C3: NOT JUSTIFIED        — Unchanged
C4: DEFERRED             — Unchanged
C5: DEFERRED             — Unchanged

RQ-4: CLOSED             — Unchanged
```

P149 is engineering hardening, NOT research evidence.

---

## 10. Architectural Debt Impact

| Debt | P149 Impact |
|------|------------|
| D1 — CandidateArtifact mutability | Unchanged (not addressed) |
| D2 — Pipeline/Controller overlap | Unchanged (not addressed) |

---

## 11. What P149 Does NOT Do

- Does NOT fix D1 (CandidateArtifact mutability)
- Does NOT fix D2 (Pipeline/Controller overlap)
- Does NOT implement C3/C4/C5
- Does NOT reopen RQ-4
- Does NOT change verification policy
- Does NOT add stdout/stderr size limits (designed for future gate)
- Does NOT add input size limits (designed for future gate)
- Does NOT add persistent logging (designed for future gate)

---

```
P149 COMPLETE
ORACLE TIMEOUT HARDENING COMPLETE

P0 BLOCKER: RESOLVED

ORACLE TIMEOUT: 60 seconds (configurable, minimum 1s)
TIMEOUT FAILURE: exit_code=-1 → ORACLE_FAILURE → REJECT
FAIL-CLOSED: PASS
AUTHORITY BOUNDARY: PASS

NEW TESTS: 29
FULL REGRESSION: 564/564 PASS

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
P150 — Contract Hardening (D1 resolution, interface stability)
```
