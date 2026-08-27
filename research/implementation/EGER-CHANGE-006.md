# EGER-CHANGE-006 — CVR Propagation Fix (Measurement/Provenance Repair)

| Field | Value |
|---|---|
| Identifier | EGER-CHANGE-006 |
| Date | 2026-08-27 |
| Status | **IMPLEMENTED** |
| Reason | P058 identified metadata_validation not propagated to provenance |
| Scope | Measurement/provenance repair only |

---

## 1. Defect

`metadata_validation` was included in `evidence_dict_for_hash` but NOT in `provenance`. External consumers read `None` for CVR data.

## 2. Fix

Added `"metadata_validation": metadata_validation` to the provenance dict in `adapter.py` line ~460.

## 3. What Changed

| File | Change |
|------|--------|
| `eger/oracle/adapter.py` | +1 line: metadata_validation in provenance |
| `tests/test_measurement_upgrade.py` | +7 tests (T053–T059) |

## 4. What Did NOT Change

- BENCH-002 tasks
- MODEL-003/004
- Treatment logic
- Oracle semantic rules
- Historical artifacts
- Ṛta

## 5. Test Results

| Suite | Before | After |
|-------|--------|-------|
| Original | 95 | 95 |
| Measurement (T025–T052) | 28 | 28 |
| CVR (T053–T059) | — | 7 |
| **Total** | **123** | **130** |

## 6. CVR Contract Verified

| Test | Expected | Actual |
|------|----------|--------|
| Valid reference | CVR=1.0 | CVR=1.0 ✅ |
| Invalid reference | CVR=0.0 | CVR=0.0 ✅ |
| Mixed references | CVR=0.5 | CVR=0.5 ✅ |
| No references | CVR=1.0 | CVR=1.0 ✅ |
| Provenance contains MV | Yes | Yes ✅ |
| No metadata → None | None | None ✅ |
