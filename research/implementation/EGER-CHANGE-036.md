# EGER CHANGE-036 — OpenSTA Adapter Contract Validation (P165)

## Purpose

Adversarially validate the OpenSTA adapter contract and fix any defects found.

## Baseline

- **Commit:** 1821aac12db3b4c4670fdbd1b816e776e6c9e479
- **Branch:** main
- **Prior change:** CHANGE-035 (P164 — Adapter Implementation)

## Defects Found and Fixed

### 1. evidence_scope Contract Mismatch (High)

**File:** `eger/oracle/opensta_adapter.py`

**Before:**
```python
evidence_scope = "FULL"
```

**After:**
```python
evidence_scope = "VALIDATED"
```

**Rationale:** The normalizer's `_SCOPE_MAP` maps raw values (`VALIDATED → FULL`), not already-mapped values. Setting `evidence_scope = "FULL"` caused the normalizer to map it to `"UNSUPPORTED"`, rejecting all OpenSTA evidence.

### 2. analysis_scope Status Ternary (Low)

**File:** `eger/oracle/opensta_adapter.py`

**Before:**
```python
"status": "VALIDATED" if not report.has_violations else "VALIDATED"
```

**After:**
```python
"status": "VALIDATED" if not report.has_violations else "VIOLATIONS_FOUND"
```

### 3. Unused sdc_escaped Variable (Low)

**File:** `eger/oracle/opensta_adapter.py`

Removed dead code.

## Test Changes

| File | Change |
|------|--------|
| `tests/test_opensta_adapter.py` | Updated `evidence_scope` assertion from `"FULL"` to `"VALIDATED"` |
| `tests/test_opensta_adapter_contract.py` | NEW — 63 adversarial contract tests |

## Test Results

- **P164 tests:** 26/26 PASS
- **P165 tests:** 63/63 PASS
- **Full regression:** 823/823 PASS

## Ṛta Impact

None.

## Historical Research Impact

None.

## Decision

PASS — 3 defects found and fixed, 1 documented vulnerability, no remaining critical issues.
