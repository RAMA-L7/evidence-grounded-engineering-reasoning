# EGER-CHANGE-005 — Measurement Upgrade (Design Metadata for Oracle Validation)

| Field | Value |
|---|---|
| Identifier | EGER-CHANGE-005 |
| Date | 2026-08-27 |
| Status | **IMPLEMENTED** |
| Reason | Enable FULL scope Oracle validation via evaluator-side design metadata |
| Scope | Measurement infrastructure only |

---

## 1. Change Summary

Added evaluator-side design metadata (port list, clock definitions) to enable the Oracle to validate SDC references against actual design objects, achieving `FULL` scope where previously `NETLIST_REQUIRED` forced `INSUFFICIENT`.

---

## 2. What Changed

| File | Change | Risk |
|------|--------|------|
| `eger/oracle/schemas.py` | Added `DesignMetadata`, `PortDef`, `ClockDef`, `CellDef` dataclasses | LOW — additive |
| `eger/oracle/adapter.py` | Added `design_metadata` parameter to `validate()`, metadata validation logic | LOW — additive, backward compatible |
| `eger/oracle/re_evaluate.py` | New module: read-only re-evaluation mechanism | NONE — new file |
| `tests/test_measurement_upgrade.py` | 28 new tests (T025–T052) | LOW — additive |
| `research/experiments/EGER-BENCH-002/evaluator_context/*.json` | 6 new metadata files | NONE — new files |

---

## 3. What Did NOT Change

| File | Preserved |
|------|-----------|
| BENCH-002 task files | ✅ UNCHANGED |
| BENCH-002 evaluator_only files | ✅ UNCHANGED |
| MODEL-003 specification | ✅ UNCHANGED |
| MODEL-004 specification | ✅ UNCHANGED |
| C0/C1/C2/C2-live artifacts | ✅ UNCHANGED |
| Engineer adapter | ✅ UNCHANGED |
| feedback.py | ✅ UNCHANGED |
| structured_feedback.py | ✅ UNCHANGED |
| LiveEngineerModel | ✅ UNCHANGED |
| epistemic components | ✅ UNCHANGED |
| authorization components | ✅ UNCHANGED |
| Ṛta | ✅ UNCHANGED |

---

## 4. Information Boundary

| Tier | Who Sees It | Metadata |
|------|-------------|----------|
| ENGINEER_VISIBLE | Model only | Task text (design_context, objective, constraints) |
| ORACLE_VISIBLE | Oracle only | Design metadata (ports, clocks, cells) |
| EVALUATOR_ONLY | Neither | Expected SDC, hidden answers |

**The model NEVER sees design_metadata.** Verified by test T040.

---

## 5. Backward Compatibility

`Oracle.validate(sdc_text)` without `design_metadata` continues to behave identically to pre-CHANGE-005. The metadata parameter is optional.

---

## 6. Test Results

| Test Suite | Before | After |
|-----------|--------|-------|
| Original tests | 95 PASS | 95 PASS |
| New tests (T025–T052) | — | 28 PASS |
| **Total** | **95** | **123** |

---

## 7. Historical Re-Evaluation

**NOT EXECUTED.** The re-evaluation mechanism is implemented but not yet run. This is a separate gate.

---

## 8. Authorization

- EGER-CHANGE-005 = APPROVED (per P054 human authorization)
- Implementation = COMPLETED
- Historical re-evaluation = NOT AUTHORIZED (separate gate)
- C3 = NOT AUTHORIZED
