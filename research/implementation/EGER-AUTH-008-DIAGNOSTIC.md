# EGER-AUTH-008 — Diagnostic Execution Authorization

| Field | Value |
|---|---|
| ID | EGER-AUTH-008 |
| Date | 2026-08-28 |
| Authorization | **DIAGNOSTIC EXECUTION AUTHORIZED** |
| Governing | P078 design, P079 implementation, P080 readiness |

---

## 1. Human Authorization

> The human researcher authorizes execution of the P078 diagnostic experiment using MODEL-005 (mimo-v2.5-free) for 4 conditions (A/B/C/D) testing why BENCH2-001 ignored ERROR feedback.

---

## 2. Frozen Configuration

| Parameter | Value |
|-----------|-------|
| Model | opencode/mimo-v2.5-free |
| MODEL_ID | EGER-MODEL-005 |
| Temperature | 0.0 |
| Max tokens | 2048 |
| Tools | [] |
| Timeout | 60s |
| Oracle | 3b5c2f2 |
| Metadata | eger.design_metadata.v1 |

---

## 3. Frozen Conditions

| Condition | Variable Changed |
|-----------|-----------------|
| A (baseline) | None — original BENCH2-001 |
| B (richer SDC) | Initial SDC only |
| C (broader objective) | Objective wording only |
| D (ERROR-only) | Feedback content only |

---

## 4. Execution Budget

**8 calls maximum:** 4 conditions × (1 model + 1 Oracle)

No retries. No model substitution. No fallback.

---

## 5. Provider Failure Policy

| Failure | Action |
|---------|--------|
| Rate limiting | Record INCOMPLETE; continue to next condition |
| Timeout | Record INCOMPLETE; continue to next condition |
| Provider unavailable | Record INCOMPLETE; continue to next condition |

Do not substitute another model. Do not retry beyond budget.

---

## 6. Artifact Namespace

```
research/experiments/EGER-EXP-001/formal/DIAGNOSTIC-001/
```

Currently EMPTY.

---

## 7. Historical Preservation

| Item | Status |
|------|--------|
| RQ4-MODEL-005 | PRESERVED (RUN_INDEX.json exists) |
| C0/C1/C2/C2-live | PRESERVED |
| BENCH-002 | UNCHANGED |
| MODEL-005 | FROZEN |
| Rta | 3b5c2f2, UNTOUCHED |

---

## 8. Critical Scientific Gate

| # | Question | Answer |
|---|----------|--------|
| 1 | P080 complete and READY? | ✅ |
| 2 | P079 implementation unchanged? | ✅ |
| 3 | Conditions A/B/C/D frozen? | ✅ |
| 4 | MODEL-005/Oracle/metadata unchanged? | ✅ |
| 5 | DIAGNOSTIC-001 empty? | ✅ |
| 6 | Historical RQ-4 artifacts preserved? | ✅ |
| 7 | Tests pass? | ✅ 186/186 |
| 8 | Budget frozen at 8 calls? | ✅ |
| 9 | No model substitution/retries? | ✅ |
| 10 | H4 unresolved? | ✅ |

---

## 9. Test Baseline

```
186 passed in 20.86s
```

---

## 10. Authorization Scope

This authorization covers ONLY:

- Running 4 diagnostic conditions (A/B/C/D)
- Using MODEL-005 (mimo-v2.5-free)
- Using BENCH2-001 task data
- Evaluating outputs with Oracle + metadata
- Writing results to DIAGNOSTIC-001/ only

This authorization does NOT cover:

- C3
- Any model change
- Any benchmark change
- Any Oracle change
- Any RQ-4 result modification
- Any historical artifact modification
- Any Rta modification

---

## 11. Status

```
P081 COMPLETE
DIAGNOSTIC EXECUTION AUTHORIZED
EXECUTION NOT PERFORMED
C3 NOT AUTHORIZED
```

---

## 12. Next Gate

**P082 — Diagnostic Execution**
