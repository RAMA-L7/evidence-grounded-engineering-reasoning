# EGER-P092 — Cross-Task Variability Analysis

| Field | Value |
|---|---|
| ID | EGER-P092-CROSS-TASK-VARIABILITY-ANALYSIS-001 |
| Date | 2026-08-28 |
| Status | **ANALYSIS COMPLETE** |

---

## 1. Executive Summary

Cross-task analysis of existing RQ-4 treatment artifacts. Of 4 error-bearing tasks, 3 adhered (75%) and 1 did not (25%). However, each task has only **one observation**, so task-level variability cannot be assessed from this data alone. The P090 BENCH2-001 repeated experiment is the only task with sufficient observations to characterize variability.

---

## 2. Error-Bearing Tasks (initial ERROR > 0)

| Task | Init Errors | Final Errors | Delta | Adhered? | Control Delta |
|------|-------------|-------------|-------|----------|---------------|
| BENCH2-001 | 2 | 2 | 0 | ❌ NO | 0 |
| BENCH2-002 | 2 | 0 | -2 | ✅ YES | 0 |
| BENCH2-004 | 2 | 0 | -2 | ✅ YES | 0 |
| BENCH2-005 | 2 | 0 | -2 | ✅ YES | 0 |

**Treatment adherence: 3/4 = 75%**
**Control adherence: 0/4 = 0%**

---

## 3. Already-Correct Tasks (initial ERROR = 0)

| Task | Init Errors | Final Errors | Delta | Notes |
|------|-------------|-------------|-------|-------|
| BENCH2-003 | 0 | 0 | 0 | No improvement possible |
| BENCH2-006 | 0 | 0 | 0 | No improvement possible |

**These tasks cannot provide adherence evidence** — there were no ERROR findings to fix.

---

## 4. Per-Task Analysis

### BENCH2-001 (DID NOT ADHERE — 1 observation)
- n=1 in RQ-4 (did not adhere)
- n=10 in P090 (4 adhered, 6 did not)
- **Variability demonstrated:** YES (P090)
- Adherence rate: 4/10 = 40% [12.6%, 72.9%]

### BENCH2-002 (ADHERED — 1 observation)
- n=1 in RQ-4 (adhered)
- No repeated observations
- **Variability demonstrated:** NO (insufficient data)
- Cannot determine whether this task would also show stochastic adherence

### BENCH2-004 (ADHERED — 1 observation)
- n=1 in RQ-4 (adhered)
- No repeated observations
- **Variability demonstrated:** NO (insufficient data)

### BENCH2-005 (ADHERED — 1 observation)
- n=1 in RQ-4 (adhered)
- No repeated observations
- **Variability demonstrated:** NO (insufficient data)

---

## 5. Control Branch Behavior

| Task | Control Changed? | Control Delta |
|------|-----------------|---------------|
| BENCH2-001 | False | 0 |
| BENCH2-002 | False | 0 |
| BENCH2-003 | True | 0 |
| BENCH2-004 | False | 0 |
| BENCH2-005 | False | 0 |
| BENCH2-006 | True | 0 |

**Control never reduced errors (0/4 error-bearing tasks).** Control sometimes changed output (2/6) but never improved correctness.

---

## 6. What This Data Can and Cannot Support

### Supported
- Treatment caused ERROR reduction in 3/4 error-bearing tasks (single observation each)
- Control never reduced errors
- BENCH2-001 shows demonstrated variability (from P090)
- The treatment effect direction is positive across all error-bearing tasks

### NOT supported (n=1 per task)
- That BENCH2-002/004/005 are deterministic (always adhere)
- That BENCH2-001 is uniquely variable (other tasks might be too)
- That the 75% task-level adherence rate is stable
- That any specific task will or will not improve under feedback

---

## 7. The Core Limitation

Each of BENCH2-002, 004, 005 has exactly **one treatment observation** (from P074/P082). A single success does not prove determinism — just as a single failure (BENCH2-001 in P074) did not prove determinism in the negative direction.

P090 showed that BENCH2-001's single observation (failure) was one sample from a stochastic process. We have no evidence that BENCH2-002/004/005 are different.

---

## 8. Should Variability Be Investigated Across Tasks?

**YES.** The current evidence is insufficient to determine whether:

1. BENCH2-002/004/005 are truly deterministic (always adhere)
2. BENCH2-002/004/005 are also stochastic but happened to adhere in their single observation
3. Different tasks have different adherence rates

Without repeated observations on other tasks, we cannot answer these questions.

---

## 9. Relationship to P076/P077

P076/P077 hypothesized that BENCH2-001 failed due to context anchoring, task-scope interpretation, or feedback overload. P082/P090 showed that BENCH2-001 sometimes succeeds under identical conditions, rendering those explanations unnecessary.

However, P076/P077 also noted that BENCH2-002/004/005 had richer initial SDCs. This correlation is real but cannot be interpreted as causal without repeated observations on each task.

---

## 10. Recommended Next Steps

1. **Repeated observations on BENCH2-002** — is its single success deterministic or stochastic?
2. **Repeated observations on BENCH2-004 or 005** — same question
3. **Compare adherence rates across tasks** — are some tasks inherently more adherent?
4. **Only after task-level variability is characterized:** consider C3

---

## 11. C3 Status

**C3 REMAINS BLOCKED.**

Before C3, we need to understand:
- Whether variability is task-specific or universal
- Whether different tasks have different adherence rates
- What determines adherence in a given run

Current evidence is insufficient for these questions.

---

## 12. Status

```
P092 COMPLETE
ANALYSIS COMPLETE
VARIABILITY: DEMONSTRATED FOR BENCH2-001, UNTESTED FOR OTHERS
N=1 PER TASK (EXCEPT BENCH2-001)
REPEATED OBSERVATIONS NEEDED FOR 002/004/005
C3: NOT AUTHORIZED
```
