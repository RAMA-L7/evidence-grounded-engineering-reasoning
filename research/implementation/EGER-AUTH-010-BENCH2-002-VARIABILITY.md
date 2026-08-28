# EGER-AUTH-010 — BENCH2-002 Variability Execution Authorization

| Field | Value |
|---|---|
| ID | EGER-AUTH-010 |
| Date | 2026-08-28 |
| Authorization | **BENCH2-002 VARIABILITY EXECUTION AUTHORIZED — EXECUTION NOT PERFORMED** |
| Governing | P093 design, P094 implementation, P095 readiness |

---

## 1. Human Authorization

> The human researcher authorizes execution of the P093 BENCH2-002 variability confirmation: 10 identical BENCH2-002 treatment runs using MODEL-005 to test whether its single RQ-4 success is deterministic or stochastic.

---

## 2. Frozen Configuration

| Parameter | Value |
|-----------|-------|
| Model | opencode/mimo-v2.5-free |
| MODEL_ID | EGER-MODEL-005 |
| Task | BENCH2-002 |
| Initial SDC | 287 chars (clock + generated + groups) |
| Objective | "primary clock and correctly constrained generated clock" |
| Oracle | 3b5c2f2 |
| Metadata | eger.design_metadata.v1 |

---

## 3. Frozen Protocol

| Parameter | Value |
|-----------|-------|
| Runs | 10 sequential |
| Early stopping | None |
| Primary metric | ERROR adherence (binary) |
| CI method | Clopper-Pearson 95% |

---

## 4. Execution Budget

**30 calls maximum:** 10 runs × (1 model + 2 Oracle) = 30

No retries. No model substitution. No fallback.

---

## 5. Provider Failure Policy

Record INCOMPLETE and continue within budget. No substitution. No retry beyond budget.

---

## 6. Artifact Namespace

```
research/experiments/EGER-EXP-001/formal/DIAGNOSTIC-004/
```

Currently does not exist.

---

## 7. Historical Preservation

| Item | Status |
|------|--------|
| RQ4-MODEL-005 | PRESERVED |
| DIAGNOSTIC-001 | PRESERVED |
| DIAGNOSTIC-002 | PRESERVED |
| DIAGNOSTIC-003 | PRESERVED |
| All other artifacts | PRESERVED |

---

## 8. Critical Gate

| # | Question | Answer |
|---|----------|--------|
| 1 | P095 = READY? | ✅ |
| 2 | P093 protocol frozen? | ✅ |
| 3 | MODEL-005 = mimo-v2.5-free? | ✅ |
| 4 | 287-char BENCH2-002 SDC? | ✅ |
| 5 | 10 sequential runs? | ✅ |
| 6 | 30-call max? | ✅ |
| 7 | No retry/substitution? | ✅ |
| 8 | DIAGNOSTIC-004 empty? | ✅ |
| 9 | Historical preserved? | ✅ |
| 10 | Tests: 221/221? | ✅ |
| 11 | C3 blocked? | ✅ |

---

## 9. Status

```
P096 COMPLETE
BENCH2-002 VARIABILITY EXECUTION AUTHORIZED
EXECUTION NOT PERFORMED
C3 NOT AUTHORIZED
```

---

## 10. Next Gate

**P097 — BENCH2-002 Variability Execution (10 runs)**
