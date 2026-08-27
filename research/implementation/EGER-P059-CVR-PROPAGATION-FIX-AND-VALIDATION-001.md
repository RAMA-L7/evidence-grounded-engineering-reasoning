# EGER-P059 — CVR Propagation Fix & Measurement Validation

| Field | Value |
|---|---|
| ID | EGER-P059-CVR-PROPAGATION-FIX-AND-VALIDATION-001 |
| Date | 2026-08-27 |
| Scope | Measurement-layer repair only |
| Status | **MEASUREMENT REPAIR COMPLETE — CVR OBSERVABLE** |

---

## 1. Executive Summary

P058 identified that `metadata_validation` was not propagated to `EvidenceArtifact.provenance`. P059 fixed this with a one-line change. CVR is now observable through provenance. All 130 tests pass. Historical artifacts unchanged.

---

## 2. P058 Defect

In `eger/oracle/adapter.py`, `metadata_validation` was included in `evidence_dict_for_hash` (for hashing) but NOT in `provenance` (for external access). This caused:

- `result.evidence.provenance.get('metadata_validation')` → `None`
- P057 reported CVR = 0.00 for all tasks
- `valid_refs = 0, total_refs = 0` for all tasks

---

## 3. Root Cause

The provenance dict was constructed before the metadata validation result was available (or more precisely, the field was simply omitted from the dict literal).

---

## 4. Implementation Change

```python
# BEFORE (buggy):
provenance = {
    "oracle_name": ORACLE_NAME,
    ...
    "raw_path": raw_evidence.raw_path,
    # metadata_validation MISSING
}

# AFTER (fixed):
provenance = {
    "oracle_name": ORACLE_NAME,
    ...
    "raw_path": raw_evidence.raw_path,
    "metadata_validation": metadata_validation,  # ADDED
}
```

One line added. No other code changes.

---

## 5. CVR Contract

| Test | SDC | Expected | Actual | Status |
|------|-----|----------|--------|--------|
| A: Valid reference | `[get_ports clk]` | CVR=1.0 | CVR=1.0 | ✅ |
| B: Invalid reference | `[get_ports nonexistent]` | CVR=0.0 | CVR=0.0 | ✅ |
| C: Mixed | valid + invalid | CVR=0.5 | CVR=0.5 | ✅ |
| D: No references | `set_sdc_version 2.0` | CVR=1.0 | CVR=1.0 | ✅ |

---

## 6. Test Results

| Suite | Count | Status |
|-------|-------|--------|
| Original (T001–T024 + others) | 95 | ✅ ALL PASS |
| Measurement (T025–T052) | 28 | ✅ ALL PASS |
| CVR (T053–T059) | 7 | ✅ ALL PASS |
| **Total** | **130** | **✅ ALL PASS** |

---

## 7. Provenance Verification

| Check | Result |
|-------|--------|
| `provenance["metadata_validation"]` exists | ✅ Yes (T057) |
| Contains valid_refs, total_refs, CVR | ✅ Yes (T057) |
| Matches direct calculation | ✅ Yes (T058) |
| Without metadata → None | ✅ Yes (T059) |

---

## 8. Information Boundary

| Check | Result |
|-------|--------|
| metadata remains Oracle-visible only | ✅ |
| EngineerAdapter unchanged | ✅ |
| LiveEngineerModel unchanged | ✅ |
| Model prompt unchanged | ✅ |

---

## 9. Historical Preservation

| Item | Status |
|------|--------|
| BENCH-002 tasks | ✅ UNCHANGED (hashes verified) |
| evaluator_only | ✅ UNCHANGED |
| C0 manifests (6) | ✅ PRESERVED |
| C1 manifests (6) | ✅ PRESERVED |
| C2 manifests (6) | ✅ PRESERVED |
| MODEL-003/004 | ✅ UNCHANGED |
| Ṛta | ✅ UNCHANGED |

---

## 10. Post-Fix Validation

CVR is now observable through provenance:

| Condition | Before Fix | After Fix |
|-----------|-----------|-----------|
| Valid reference CVR | None (not in provenance) | 1.00 ✅ |
| Invalid reference CVR | None | 0.00 ✅ |
| Mixed references CVR | None | 0.50 ✅ |
| No metadata | None | None ✅ |

---

## 11. Scientific Interpretation

P057's reported `CVR = 0.00` was a **measurement-reporting defect**, not a true universal zero-CVR result. The fix confirms that CVR is task-dependent and meaningful:

- BENCH2-003 (valid simple clock) → CVR = 1.0
- Tasks with missing I/O delays → CVR = 1.0 (port refs valid, but constraints missing)

**CVR does NOT measure engineering correctness.** It measures reference validity (do get_ports/get_clocks reference actual design objects?). A task can have CVR = 1.0 and still be INVALID_ARTIFACT (if it has error-severity findings).

---

## 12. Remaining Measurement Limitations

| Limitation | Impact |
|-----------|--------|
| CVR measures reference validity, not correctness | Must not be used as correctness proxy |
| PARTIAL scope for 2/6 tasks | Some constructs still cannot be validated |
| 2/6 tasks missing from MODEL-004 runs | Incomplete sample |
| Cross-model comparison invalid for causal claims | Need same-model controlled experiment |

---

## 13. C3 Status

**C3 REMAINS BLOCKED.**

The measurement repair establishes that CVR is observable, but:
1. RQ-4 has not been answered
2. A clean controlled experiment under the repaired Oracle has not been conducted
3. C3 requires reliable correctness measurement, which is now possible but not yet demonstrated in a treatment experiment

---

## 14. Next Recommended Gate

```
P059 (this fix) ← YOU ARE HERE
    ↓
P060 — Measurement validation readiness (verify repair is sufficient)
    ↓
Clean MODEL-004 C2 re-execution under repaired Oracle
    ↓
Scientific review
    ↓
RQ-4 decision
    ↓
Only then: C3 design/authorization
```

---

## 15. Files Changed

| File | Change |
|------|--------|
| `eger/oracle/adapter.py` | +1 line (metadata_validation in provenance) |
| `tests/test_measurement_upgrade.py` | +7 tests (T053–T059) |
| `research/implementation/EGER-CHANGE-006.md` | New change-control record |

---

## 16. Final Status

```
MEASUREMENT REPAIR COMPLETE — CVR OBSERVABLE
TESTS: 130/130 PASS
HISTORICAL ARTIFACTS: UNCHANGED
C3: REMAINS BLOCKED
NEXT: P060 — measurement validation readiness
```
