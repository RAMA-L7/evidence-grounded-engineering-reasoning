# EGER-AUTH-009 — DIAGNOSTIC-003 Execution Authorization

| Field | Value |
|---|---|
| ID | EGER-AUTH-009 |
| Date | 2026-08-28 |
| Authorization | **DIAGNOSTIC-003 EXECUTION AUTHORIZED — EXECUTION NOT PERFORMED** |
| Governing | P086 design, P087 implementation, P088 readiness |

---

## 1. Human Authorization

> The human researcher authorizes execution of the P086 controlled variability confirmation: 10 identical BENCH2-001 runs using MODEL-005 to test whether ERROR adherence is non-deterministic under genuinely identical conditions.

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
| Initial SDC | `create_clock -name clk -period 10.0 [get_ports clk]` (51 chars) |
| Task | BENCH2-001 |
| Objective | "Generate SDC that correctly defines the primary clock on clk" |

---

## 3. Frozen Protocol

| Parameter | Value |
|-----------|-------|
| Runs | 10 sequential |
| Execution mode | Single batch, sequential |
| Early stopping | None — all 10 executed |
| Primary metric | ERROR adherence (binary) |
| CI method | Clopper-Pearson 95% |

---

## 4. Execution Budget

**30 calls maximum:** 10 runs × (1 model + 2 Oracle) = 30

No retries. No model substitution. No fallback.

---

## 5. Provider Failure Policy

| Failure | Action |
|---------|--------|
| Rate limiting | Record INCOMPLETE; continue |
| Timeout | Record INCOMPLETE; continue |
| Provider unavailable | Record INCOMPLETE; continue |

Do not substitute. Do not retry beyond budget.

---

## 6. Artifact Namespace

```
research/experiments/EGER-EXP-001/formal/DIAGNOSTIC-003/
```

Currently does not exist.

---

## 7. Historical Preservation

| Item | Status |
|------|--------|
| RQ4-MODEL-005 | PRESERVED |
| DIAGNOSTIC-001 | PRESERVED |
| DIAGNOSTIC-002 | PRESERVED |
| C0/C1/C2/C2-live | PRESERVED |
| BENCH-002 | UNCHANGED |
| Rta | 3b5c2f2 |

---

## 8. Scientific Gate

| # | Question | Answer |
|---|----------|--------|
| 1 | P088 = READY? | ✅ |
| 2 | P086 protocol frozen? | ✅ |
| 3 | MODEL-005 = mimo-v2.5-free? | ✅ |
| 4 | 51-char bare SDC? | ✅ |
| 5 | 10 sequential runs? | ✅ |
| 6 | 30-call max? | ✅ |
| 7 | No early stopping? | ✅ |
| 8 | No retry/substitution? | ✅ |
| 9 | DIAGNOSTIC-003 empty? | ✅ |
| 10 | Historical preserved? | ✅ |
| 11 | C3 blocked? | ✅ |

---

## 9. Test Baseline

```
203 passed in 19.31s
```

---

## 10. Authorization Scope

This authorization covers ONLY:

- Running 10 identical BENCH2-001 runs
- Using MODEL-005 (mimo-v2.5-free)
- Evaluating outputs with Oracle + metadata
- Writing results to DIAGNOSTIC-003/ only
- Computing adherence rate and Clopper-Pearson CI

This authorization does NOT cover:

- C3
- Any model change
- Any benchmark change
- Any Oracle change
- Any historical artifact modification
- Any RQ-4 result reinterpretation

---

## 11. Status

```
P089 COMPLETE
DIAGNOSTIC-003 EXECUTION AUTHORIZED
EXECUTION NOT PERFORMED
C3 NOT AUTHORIZED
```

---

## 12. Next Gate

**P090 — Diagnostic Execution (10 runs)**
