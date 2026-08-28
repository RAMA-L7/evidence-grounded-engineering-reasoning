# EGER-CHANGE-009 — P078 Diagnostic Experiment Implementation

| Field | Value |
|---|---|
| ID | EGER-CHANGE-009 |
| Date | 2026-08-28 |
| Governing Design | EGER-P078-RQ4-HYPOTHESIS-ISOLATION-DESIGN-001 |
| Status | **IMPLEMENTED** |

---

## 1. Purpose

Implement the P078 diagnostic experiment to determine why BENCH2-001 ignored ERROR feedback while BENCH2-002/004/005 followed it.

---

## 2. Scope

### INCLUDED

| What | Description |
|------|-------------|
| Diagnostic runner | `formal_diagnostic_001.py` — 4 conditions (A/B/C/D) |
| Unit tests | `test_diagnostic_001.py` — 24 tests (T092–T104) |
| Artifact namespace | `formal/DIAGNOSTIC-001/` |

### EXCLUDED (must not change)

| What | Status |
|------|--------|
| BENCH-002 | UNCHANGED |
| MODEL-005 | FROZEN |
| Oracle | UNCHANGED |
| P074/P075 RQ-4 results | PRESERVED |
| RQ4-MODEL-005 artifacts | PRESERVED |
| C0/C1/C2/C2-live | PRESERVED |
| Ṛta | UNTOUCHED |

---

## 3. Condition Design

| Condition | Variable Changed | Tests |
|-----------|-----------------|-------|
| A (baseline) | None — original BENCH2-001 | H4 baseline |
| B (richer SDC) | Initial SDC only | H1: context anchoring |
| C (broader objective) | Objective wording only | H2: task-scope interpretation |
| D (ERROR-only) | Feedback content only | H3: feedback overload |

---

## 4. Implementation

| File | Purpose |
|------|---------|
| `formal_diagnostic_001.py` | Diagnostic runner with 4 conditions |
| `test_diagnostic_001.py` | 24 deterministic unit tests |
| `EGER-CHANGE-009.md` | This change control |

---

## 5. Test Results

| Suite | Count | Status |
|-------|-------|--------|
| Diagnostic tests (T092–T104) | 24 | ✅ ALL PASS |
| Original + measurement + RQ4 | 162 | ✅ ALL PASS |
| **Total** | **186** | **✅ ALL PASS** |

---

## 6. Historical Preservation

| Item | Status |
|------|--------|
| P074/P075 RQ-4 results | ✅ UNTOUCHED |
| RQ4-MODEL-005 | ✅ UNTOUCHED |
| C0/C1/C2/C2-live | ✅ PRESERVED |
| BENCH-002 | ✅ UNCHANGED |
| MODEL-005 | ✅ FROZEN |
| Ṛta | ✅ UNTOUCHED |

---

## 7. H4 Note

P078 stated that "A replicating the original result" could test H4 (model variability). This is corrected: **one new A run cannot establish stochastic variability.** H4 remains **unresolved** unless repeated A runs are later performed.
