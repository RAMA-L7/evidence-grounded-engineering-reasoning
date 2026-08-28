# EGER-P091 — DIAGNOSTIC-003 Scientific Review

| Field | Value |
|---|---|
| ID | EGER-P091-DIAGNOSTIC-003-SCIENTIFIC-REVIEW-001 |
| Date | 2026-08-28 |
| Status | **SCIENTIFIC REVIEW COMPLETE** |

---

## 1. Executive Summary

**Non-deterministic ERROR adherence is strongly supported.** Under genuinely identical observable conditions (same task, model, SDC, objective, feedback, Oracle, metadata), the model fixed ERROR findings in 4/10 runs (P090) and 6/15 runs combined across all experiments. Activation is 100% — the model always changes its output with feedback, but only sometimes addresses ERROR findings.

**Classification: H4 STRONGLY SUPPORTED**

---

## 2. Non-Deterministic Adherence — Supported?

**YES.** The P090 10-run experiment provides the strongest evidence:

| Run | Adherent |
|-----|----------|
| 1–4 | ❌❌❌❌ |
| 5 | ✅ |
| 6–7 | ❌❌ |
| 8–10 | ✅✅✅ |

The pattern shows clusters of non-adherence (runs 1–4) and adherence (runs 8–10), with no systematic explanation. This is consistent with stochastic behavior.

---

## 3. Adherence Rate and CI

### P090 (controlled, 10 runs)
- Rate: 4/10 = 40%
- 95% CI: [12.6%, 72.9%]

### Combined (15 observations across experiments)
- Rate: 6/15 = 40%
- Note: Combined observations include different execution contexts (batch vs standalone), so the combined rate has additional confounds

### Interpretation
The true adherence rate for BENCH2-001/mimo-v2.5-free is **somewhere between ~13% and ~73%** with 95% confidence. The point estimate is 40%, but the CI is wide. We cannot claim a precise probability.

---

## 4. Proposal Activation Rate

**10/10 = 100%** in P090. **15/15 = 100%** combined.

The model **always** changes its output when given structured feedback. Activation is deterministic. Only adherence is non-deterministic.

---

## 5. Input Identity Verification

| Parameter | P090 Value | Verified? |
|-----------|-----------|-----------|
| Initial SDC | 51-char bare `create_clock...` | ✅ Same in all 10 runs |
| Objective | "primary clock on clk" | ✅ Same in all 10 runs |
| Feedback hash | c3803b9a... | ✅ Same in all 10 runs |
| Model | mimo-v2.5-free | ✅ Same in all 10 runs |
| Oracle | 3b5c2f2 | ✅ Same in all 10 runs |
| Metadata | eger.design_metadata.v1 | ✅ Same in all 10 runs |
| Execution mode | Sequential, single batch | ✅ Same for all 10 |

**All inputs were genuinely identical.** The variability is not attributable to observable input differences.

---

## 6. Provider Failures, Retries, Substitutions

| Check | Result |
|-------|--------|
| Provider failures | 0/10 |
| Retries | 0 |
| Model substitution | None |
| Fallback/canned output | None |
| Budget exceeded | No (30/30 calls) |

No confounds from provider issues.

---

## 7. Comparison with Prior Experiments

| Experiment | Runs | Adherent | Rate | Context |
|-----------|------|----------|------|---------|
| P074 | 1 | 0 | 0% | Batch of 6 tasks |
| P082 | 1 | 1 | 100% | Batch of 4 conditions |
| P084 | 3 | 1 | 33% | Standalone |
| P090 | 10 | 4 | 40% | Standalone, controlled |
| **Total** | **15** | **6** | **40%** | Mixed |

The P090 result (4/10) is the most reliable because it used the most controlled conditions (identical bare SDC, single batch, no confounds from other conditions).

---

## 8. What Can Be Claimed from n=15

### Supported
- ERROR adherence is non-deterministic
- Activation is deterministic (100%)
- The adherence rate is between ~13% and ~73% (95% CI from P090)
- The P074 failure was one observation from a stochastic process

### NOT supported
- That 40% is the true probability
- That the rate generalizes to other tasks or models
- That the variability is model-side vs provider-side
- That the rate is stable across time

---

## 9. H4 Classification

**H4 STRONGLY SUPPORTED.**

The evidence is now strong:
- 10 controlled identical runs: 4/10 adherent
- 15 combined observations: 6/15 adherent
- All inputs verified identical
- No provider failures or confounds
- Activation is 100% (deterministic)
- Adherence is ~40% (non-deterministic)

The model's ERROR correction is demonstrably stochastic under identical observable conditions.

---

## 10. P076/P077 Explanations — Status

| Explanation | P076/P077 Claim | P090 Status |
|------------|----------------|-------------|
| Context anchoring (H1) | Richer SDC → better adherence | **DOWNGRADED** — P082 showed A succeeded with bare SDC |
| Task-scope interpretation (H2) | Broader objective → better adherence | **DOWNGGRADED** — P082 showed A succeeded with original objective |
| Feedback overload (H3) | ERROR-only → better adherence | **DOWNGRADED** — P082 showed A succeeded with full feedback |
| Model variability (H4) | Stochastic behavior | **STRONGLY SUPPORTED** — P090 confirms with n=10 |

P076/P077's explanations were reasonable hypotheses at the time, but P082 and P090 have rendered them unnecessary. The simplest explanation — stochastic model response — now has the strongest evidence.

---

## 11. RQ-4 Interpretation

### Original RQ-4 (P074)
"3/4 error-bearing tasks improved under structured feedback"

### Revised RQ-4
"Structured evidence feedback causes the model to change its output (100% activation) and sometimes correct ERROR findings (~40% adherence for BENCH2-001/mimo-v2.5-free). The treatment effect is real but probabilistic, not deterministic."

### What RQ-4 supports
- Feedback **causes** proposal revision (activation)
- Feedback **sometimes causes** ERROR correction (adherence)
- The effect is **task-dependent and stochastic**

### What RQ-4 does NOT support
- That the effect is deterministic
- That 40% is the true probability
- That the effect generalizes beyond this task/model
- That C3 (epistemic state) would improve adherence

---

## 12. C3 Status

**C3 REMAINS BLOCKED.**

Understanding variability is prerequisite to understanding whether epistemic state could improve adherence. We now know:
- Variability exists
- The rate is uncertain (~13%–73%)
- The mechanism is unknown

Before C3, we would need to understand *why* the model sometimes follows ERROR findings and sometimes does not. Epistemic state is one hypothesis, but it is not the only one, and the current evidence does not specifically motivate it.

---

## 13. Recommended Next Research Gate

The variability question is now well-characterized for BENCH2-001/mimo-v2.5-free. Possible next steps:

1. **Test other tasks** — does BENCH2-002/004/005 show the same variability pattern?
2. **Test other models** — does a different model show different adherence rates?
3. **Investigate the mechanism** — what determines whether the model follows ERROR findings in a given run?
4. **C3 design** — if the mechanism is understood, design an epistemic-state experiment

---

## 14. Status

```
P091 COMPLETE
SCIENTIFIC REVIEW RECORDED
H4: STRONGLY SUPPORTED
ADHERENCE: NON-DETERMINISTIC (~40%, CI [13%, 73%])
ACTIVATION: DETERMINISTIC (100%)
RQ-4: SUPPORTED (PROBABILISTIC EFFECT)
C3: NOT AUTHORIZED
```
