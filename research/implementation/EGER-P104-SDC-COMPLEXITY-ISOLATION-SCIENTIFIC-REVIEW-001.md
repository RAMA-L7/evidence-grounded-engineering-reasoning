# EGER-P104 — SDC Complexity Isolation Scientific Review

| Field | Value |
|---|---|
| ID | EGER-P104-SDC-COMPLEXITY-ISOLATION-SCIENTIFIC-REVIEW-001 |
| Date | 2026-08-28 |
| Status | **SCIENTIFIC REVIEW COMPLETE** |

---

## 1. Executive Summary

The 2×2 cross produced 19/20 adherent runs. Only condition W (minimal SDC + BENCH2-001 context) had any failures. However, with n=5 per cell, the evidence is suggestive but not conclusive. The most notable finding is that condition Y (minimal SDC + BENCH2-002 context) achieved 5/5 adherence — suggesting that **task context may matter more than SDC complexity**. But the sample is too small to draw firm conclusions.

**Classification: PARTIALLY SUPPORTED**

---

## 2. Raw Results

| Condition | SDC | Context | Adherent | Rate | 95% CI |
|-----------|-----|---------|----------|------|--------|
| W | minimal | BENCH2-001 | 4/5 | 80% | [29.6%, 99.5%] |
| X | rich | BENCH2-001 | 5/5 | 100% | [50.1%, 100.0%] |
| Y | minimal | BENCH2-002 | 5/5 | 100% | [50.1%, 100.0%] |
| Z | rich | BENCH2-002 | 5/5 | 100% | [50.1%, 100.0%] |

---

## 3. Pairwise Comparisons

### W vs X (SDC effect on BENCH2-001)
- W: 4/5, X: 5/5
- Difference: 1 run
- CI overlap: substantial ([29.6%, 99.5%] vs [50.1%, 100.0%])
- **Conclusion:** Suggestive that richer SDC improves adherence for BENCH2-001, but not conclusive with n=5

### Y vs Z (SDC effect on BENCH2-002)
- Y: 5/5, Z: 5/5
- Difference: 0 runs
- **Conclusion:** No observable SDC effect for BENCH2-002. Both achieved 100% adherence.

### W vs Y (context effect with minimal SDC)
- W: 4/5, Y: 5/5
- Difference: 1 run
- CI overlap: substantial
- **Conclusion:** Suggestive that BENCH2-002 context improves adherence even with minimal SDC, but not conclusive

### X vs Z (context effect with rich SDC)
- X: 5/5, Z: 5/5
- Difference: 0 runs
- **Conclusion:** No observable context effect when SDC is rich. Both achieved 100% adherence.

---

## 4. Combined Evidence (All Experiments)

| Condition | P090/P097 | P103 | Total | Rate |
|-----------|-----------|------|-------|------|
| W (minimal + 001) | 4/10 | 4/5 | 8/15 | 53% |
| X (rich + 001) | — | 5/5 | 5/5 | 100% |
| Y (minimal + 002) | — | 5/5 | 5/5 | 100% |
| Z (rich + 002) | 10/10 | 5/5 | 15/15 | 100% |

### What the combined evidence shows
- Condition W (BENCH2-001 + minimal SDC) is the only condition with failures
- All other conditions (X, Y, Z) show 100% adherence across all experiments
- The 8/15 rate for W is the lowest observed

---

## 5. Hypothesis Assessment

### H1 (SDC complexity drives adherence)
**PARTIALLY SUPPORTED as association.** W (minimal) → 80%, X (rich) → 100%. The difference is 1 run in P103. But Y (minimal) → 100%, which contradicts a pure SDC-complexity explanation.

### H2 (Task context drives adherence)
**PARTIALLY SUPPORTED as association.** W (BENCH2-001 context) → 80%, Y (BENCH2-002 context) → 100% (both with minimal SDC). But X (BENCH2-001 context) → 100%, which contradicts a pure context explanation.

### H3 (Interaction between SDC and context)
**POSSIBLE but not demonstrable.** The pattern (W fails, X/Y/Z succeed) could indicate an interaction, but n=5 is insufficient to test for interactions.

### H4 (No identifiable effect at current sample size)
**ALSO PLAUSIBLE.** With n=5 per cell, we cannot distinguish real effects from sampling variability. The W failure could be a single observation from a stochastic process with a high adherence rate.

---

## 6. Critical Limitations

### Limitation 1: SDC content ≠ SDC complexity
The "rich" SDC is not just "more text" — it contains specific constructs (generated clock, clock groups) that are relevant to BENCH2-002's task. Using it with BENCH2-001's objective creates a semantic mismatch. We cannot claim that "complexity" causes the effect; it might be specific SDC content.

### Limitation 2: n=5 per cell is small
With n=5, the 95% CI for 5/5 adherence is [50.1%, 100.0%]. The true rate could be as low as 50%. We cannot rule out that X, Y, and Z are also stochastic but happened to succeed in all runs.

### Limitation 3: No formal statistical test
Non-overlapping CIs are not a hypothesis test. We have not performed Fisher's exact test or any other formal comparison. The differences are descriptive, not tested.

### Limitation 4: Confound between task identity and SDC content
The SDCs are not arbitrary — they are the actual initial candidates from BENCH2-001 and BENCH2-002. Changing SDC changes the task's semantic context, not just its syntactic complexity.

### Limitation 5: Previous experiments used different sample sizes
P090 used 10 runs for W; P103 used 5. Combining them increases the total but introduces a methodological inconsistency.

---

## 7. Reconciliation with P090/P097

| Source | Condition | Runs | Adherent | Rate |
|--------|-----------|------|----------|------|
| P090 | W (minimal + 001) | 10 | 4 | 40% |
| P097 | Z (rich + 002) | 10 | 10 | 100% |
| P103 | W (minimal + 001) | 5 | 4 | 80% |
| P103 | X (rich + 001) | 5 | 5 | 100% |
| P103 | Y (minimal + 002) | 5 | 5 | 100% |
| P103 | Z (rich + 002) | 5 | 5 | 100% |

The P090 W rate (40%) is lower than P103 W rate (80%). This could reflect:
- Different sample sizes (10 vs 5)
- Sampling variability
- Different execution contexts (P090 was standalone, P103 was part of a batch)

The combined W rate (8/15 = 53%) is intermediate. The difference between W and all other conditions is real but small in absolute terms (53% vs 100%).

---

## 8. What the Evidence Establishes

1. **BENCH2-001 with minimal SDC shows reduced adherence** — 8/15 across experiments
2. **All other conditions show high adherence** — 25/25 across experiments
3. **The pattern is consistent** — W is always the lowest-adherence condition
4. **Activation is universal** — 100% across all conditions

---

## 9. What Remains Unresolved

1. **Whether the W effect is caused by SDC complexity, task context, or their interaction**
2. **Whether the 53% rate for W is stable** — n=15 is still modest
3. **Whether X, Y, Z are truly deterministic** — n=5 is insufficient
4. **The mechanism** — what causes the model to sometimes skip ERROR findings in condition W

---

## 10. C3 Status

**C3 REMAINS BLOCKED.**

The evidence shows task-dependent adherence, but:
- The mechanism is unknown
- The effect is small (53% vs 100%)
- The sample sizes are modest
- Epistemic state is not specifically motivated by these findings

---

## 11. Classification

**PARTIALLY SUPPORTED**

The 2×2 cross provides suggestive evidence that:
- BENCH2-001 + minimal SDC is associated with lower adherence
- BENCH2-002 context or rich SDC is associated with higher adherence
- The effect is real but modest in absolute terms

However:
- The sample is small (n=5 per cell)
- SDC content and complexity are confounded
- No formal statistical test has been performed
- The mechanism is unknown

---

## 12. Status

```
P104 COMPLETE
SCIENTIFIC REVIEW RECORDED
CLASSIFICATION: PARTIALLY SUPPORTED
SDC COMPLEXITY EFFECT: ASSOCIATION (NOT CAUSATION)
TASK CONTEXT EFFECT: ASSOCIATION (NOT CAUSATION)
INTERACTION: POSSIBLE (NOT TESTABLE AT N=5)
C3: NOT AUTHORIZED
```
