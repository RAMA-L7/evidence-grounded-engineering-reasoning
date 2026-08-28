# EGER-AUTH-011 — SDC Complexity Isolation Execution Authorization

| Field | Value |
|---|---|
| ID | EGER-AUTH-011 |
| Date | 2026-08-28 |
| Authorization | **DIAGNOSTIC-005 EXECUTION AUTHORIZED — EXECUTION NOT PERFORMED** |
| Governing | P099 design, P100 implementation, P101 readiness |

---

## 1. Human Authorization

> The human researcher authorizes execution of the P099 2×2 SDC complexity isolation experiment: 20 runs (4 conditions × 5 runs) using MODEL-005 to determine whether adherence differences are caused by SDC complexity or task context.

---

## 2. Frozen Configuration

| Parameter | Value |
|-----------|-------|
| Model | opencode/mimo-v2.5-free |
| MODEL_ID | EGER-MODEL-005 |
| Oracle | 3b5c2f2 |
| Metadata | eger.design_metadata.v1 |
| Minimal SDC | 51 chars (clock only) |
| Rich SDC | 287 chars (clock + generated + groups) |

---

## 3. Frozen Conditions

| Condition | SDC | Task Context | Runs |
|-----------|-----|-------------|------|
| W | minimal | BENCH2-001 | 5 |
| X | rich | BENCH2-001 | 5 |
| Y | minimal | BENCH2-002 | 5 |
| Z | rich | BENCH2-002 | 5 |

---

## 4. Execution Budget

**61 calls maximum:** 20 runs × (1 model + 2 Oracle) + 1 reference = 61

No retries. No model substitution. No fallback.

---

## 5. Provider Failure Policy

Record INCOMPLETE and continue within budget.

---

## 6. Artifact Namespace

```
research/experiments/EGER-EXP-001/formal/DIAGNOSTIC-005/
```

Currently does not exist.

---

## 7. Historical Preservation

| Item | Status |
|------|--------|
| RQ4-MODEL-005 | PRESERVED |
| DIAGNOSTIC-001–004 | PRESERVED |
| All other artifacts | PRESERVED |

---

## 8. Critical Gate

| # | Question | Answer |
|---|----------|--------|
| 1 | P101 = READY? | ✅ |
| 2 | P099 protocol frozen? | ✅ |
| 3 | W/X/Y/Z conditions frozen? | ✅ |
| 4 | 5 runs per condition? | ✅ |
| 5 | 20 runs total? | ✅ |
| 6 | 61-call max? | ✅ |
| 7 | MODEL-005 = mimo-v2.5-free? | ✅ |
| 8 | Oracle/metadata unchanged? | ✅ |
| 9 | DIAGNOSTIC-005 empty? | ✅ |
| 10 | Historical preserved? | ✅ |
| 11 | Tests: 239/239? | ✅ |
| 12 | No retry/substitution? | ✅ |
| 13 | C3 blocked? | ✅ |

---

## 9. Status

```
P102 COMPLETE
DIAGNOSTIC-005 EXECUTION AUTHORIZED
EXECUTION NOT PERFORMED
C3 NOT AUTHORIZED
```

---

## 10. Next Gate

**P103 — SDC Complexity Isolation Execution (20 runs)**
