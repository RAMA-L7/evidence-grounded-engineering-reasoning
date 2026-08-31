# EGER-P125 — DIAGNOSTIC-008 Cross-Task E3a Replication Scientific Review

## Classification: **STRONG REPLICATION SIGNAL — CAUSALITY NOT ESTABLISHED**

---

## 1. Dataset Verification

| Metric | Authorized | Observed |
|--------|-----------|----------|
| Total run slots | 60 | 60 |
| Completed | — | 57 |
| Incomplete (provider timeout) | — | 3 |
| BASE completed | 30 | 30 |
| E3a completed | 30 | 27 |
| BASE adherent | — | 20 |
| E3a adherent | — | 25 |

### Incomplete Runs

| Run | Task | Condition | Status |
|-----|------|-----------|--------|
| BENCH2-002-E3a-run02 | BENCH2-002 | E3a | INCOMPLETE (timeout) |
| BENCH2-004-E3a-run03 | BENCH2-004 | E3a | INCOMPLETE (timeout) |
| BENCH2-005-E3a-run01 | BENCH2-005 | E3a | INCOMPLETE (timeout) |

All three incomplete runs are in E3a conditions. This is noted but does not constitute a protocol violation — provider timeouts are expected per the frozen failure policy. The missingness is unlikely to bias results because:
- 27/30 E3a slots still completed (90% completion rate)
- All three BASE cells achieved 10/10 completion
- The incomplete runs cannot be classified as adherent or non-adherent

---

## 2. Verified Cell Results

| Task | BASE | E3a | Difference |
|------|------|-----|-----------|
| BENCH2-002 | 7/10 = 70% | 9/9 = 100% | +30pp |
| BENCH2-004 | 7/10 = 70% | 8/9 = 89% | +19pp |
| BENCH2-005 | 6/10 = 60% | 8/9 = 89% | +29pp |

### Aggregate (Descriptive Only)

| | Completed | Adherent | Rate |
|--|-----------|----------|------|
| BASE (all tasks) | 30 | 20 | 67% |
| E3a (all tasks) | 27 | 25 | 93% |

---

## 3. Confidence Intervals (Recalculated)

| Cell | k/n | Rate | 95% Clopper-Pearson CI |
|------|-----|------|----------------------|
| 002-BASE | 7/10 | 70% | [34.9%, 93.3%] |
| 002-E3a | 9/9 | 100% | [66.4%, 100.0%] |
| 004-BASE | 7/10 | 70% | [34.9%, 93.3%] |
| 004-E3a | 8/9 | 89% | [51.8%, 99.7%] |
| 005-BASE | 6/10 | 60% | [26.2%, 87.8%] |
| 005-E3a | 8/9 | 89% | [51.8%, 99.7%] |

CIs are wide due to small n per cell. Non-overlapping CIs are **not** used as a significance test per P120 protocol.

---

## 4. Replication Classification

Per P120 preregistered rules:

> **E3a > BASE on 3/3 tasks → Strong replication signal.**

This is the strongest classification available under the preregistered framework.

---

## 5. Activation Analysis

| Cell | Activated | Completed | Rate |
|------|-----------|-----------|------|
| 002-BASE | 10 | 10 | 100% |
| 002-E3a | 9 | 9 | 100% |
| 004-BASE | 10 | 10 | 100% |
| 004-E3a | 9 | 9 | 100% |
| 005-BASE | 7 | 10 | 70% |
| 005-E3a | 9 | 9 | 100% |

Notable: BENCH2-005 BASE had 3/10 non-activated runs (SDC unchanged). E3a had 9/9 activation. This suggests the broader objective may also improve activation on tasks where the original objective produces non-responsive behavior.

---

## 6. Hypothesis Assessment

### H1 — SDC Content/Context

**PARTIALLY CONFOUNDED.** The E3a objectives are not pure abstract framing. They contain task-specific technical guidance:

| Task | E3a adds... |
|------|------------|
| BENCH2-002 | "generated clocks, and any applicable exceptions" |
| BENCH2-004 | "timing exceptions, and any applicable false paths" |
| BENCH2-005 | "multicycle exceptions, and any applicable constraints" |

The BASE objectives are narrower and more specific. The E3a objectives are both broader ("complete, production-quality") AND contain additional technical keywords. Therefore:

> **"Broader objective" is not a pure framing manipulation. Its wording may itself contribute to the effect by providing additional technical guidance to the model.**

This is the most important scientific caveat in P125.

### H2 — Task Framing

**PROMISING / SUPPORTED SIGNAL.** The cross-task replication strengthens H2 beyond the DIAGNOSTIC-006 BENCH2-001 result. However, because H1 is partially confounded, H2 cannot be isolated as the sole mechanism.

Classification: **SUPPORTED SIGNAL** (not proven causal mechanism).

### H3 — Feedback Overload

**NOT TESTED BY THIS EXPERIMENT.** DIAGNOSTIC-008 does not manipulate feedback quantity.

### H4 — Model/Provider Variability

**NOT ELIMINATED.** BASE rates vary across tasks (60-70%) and across experiments (P090: 40%, DIAGNOSTIC-007: 39%, DIAGNOSTIC-008 BASE: 67%). E3a consistently outperforms BASE despite this variability, which suggests the objective manipulation is a stronger signal than the underlying stochasticity. But variability itself remains present.

---

## 7. Comparison With Prior Evidence

| Experiment | Task | Condition | Rate |
|------------|------|-----------|------|
| P090 | BENCH2-001 | Base | 40% |
| DIAGNOSTIC-006 | BENCH2-001 | Base | 80% |
| DIAGNOSTIC-007 | BENCH2-001 | Base | 39% |
| DIAGNOSTIC-006 | BENCH2-001 | E3a | 100% |
| **DIAGNOSTIC-008** | **BENCH2-002** | **BASE** | **70%** |
| **DIAGNOSTIC-008** | **BENCH2-002** | **E3a** | **100%** |
| **DIAGNOSTIC-008** | **BENCH2-004** | **BASE** | **70%** |
| **DIAGNOSTIC-008** | **BENCH2-004** | **E3a** | **89%** |
| **DIAGNOSTIC-008** | **BENCH2-005** | **BASE** | **60%** |
| **DIAGNOSTIC-008** | **BENCH2-005** | **E3a** | **89%** |

### Combined E3a Evidence

| Task | E3a Rate | Source |
|------|----------|--------|
| BENCH2-001 | 10/10 = 100% | DIAGNOSTIC-006 |
| BENCH2-002 | 9/9 = 100% | DIAGNOSTIC-008 |
| BENCH2-004 | 8/9 = 89% | DIAGNOSTIC-008 |
| BENCH2-005 | 8/9 = 89% | DIAGNOSTIC-008 |
| **Combined** | **35/37 = 95%** | |

### Combined BASE Evidence

| Task | BASE Rate | Source |
|------|-----------|--------|
| BENCH2-001 | 19/38 ≈ 50% | P090+DG-007 |
| BENCH2-002 | 7/10 = 70% | DIAGNOSTIC-008 |
| BENCH2-004 | 7/10 = 70% | DIAGNOSTIC-008 |
| BENCH2-005 | 6/10 = 60% | DIAGNOSTIC-008 |

---

## 8. Generalization Limits

### Supported
- E3a > BASE on all three tested tasks under MODEL-005
- The effect is consistent in direction across tasks
- Effect sizes are meaningful (+19 to +30 percentage points)

### Not Established
- Universal task-framing effect (only 4 tasks tested total)
- Deterministic adherence (E3a still had 2/37 non-adherent runs)
- Exact effect size (CIs are wide)
- Generalization to other models
- Generalization to other benchmark families
- Generalization to other providers
- Causal mechanism inside the model
- Whether framing alone causes the effect (H1 confound)

---

## 9. C3 Assessment

| Question | Answer |
|----------|--------|
| Does E3a evidence motivate C3? | **No** |
| Does E3a provide a simpler explanation? | **Yes** — prompt/objective design explains more variance than epistemic uncertainty would |
| Does stochasticity remain? | **Yes** — but E3a appears to reduce it |
| Is C3 still NOT JUSTIFIED? | **Yes** |

> **E3a provides a more parsimonious explanation for adherence variability than C3 would. If task/objective configuration can shift adherence from ~60-70% to ~90-100%, then prompt design is a more actionable mechanism than epistemic-state intervention.**

---

## 10. Recommended Next Research Direction

**Direction A: E3a Wording Deconfounding Study**

The most important unresolved confound is that E3a objectives contain both:
1. Broader framing ("complete, production-quality")
2. Additional technical keywords ("generated clocks", "false paths", "multicycle exceptions")

A controlled study should separate these:
- **A1:** Broader framing ONLY (no technical keywords)
- **A2:** Technical keywords ONLY (no broader framing)
- **A3:** Both (current E3a)
- **A4:** Neither (current BASE)

This would determine whether the benefit comes from framing, technical content, or both.

**Do NOT automatically launch this experiment.** The current evidence is sufficient for a strong replication claim. The deconfounding study is the most scientifically justified next step if further mechanism isolation is desired.

---

## 11. Limitations

1. **H1 confound** — E3a objectives contain technical content, not just framing
2. **n=9-10 per cell** — CIs are wide
3. **3 incomplete E3a runs** — provider timeouts
4. **One model only** — MODEL-005
5. **One benchmark family** — BENCH-002
6. **BASE rate still variable** — 60-70% across tasks, 39-80% across experiments
7. **Cannot pool across experiments** — execution contexts differ

---

## 12. Strongest Defensible Conclusion

> Under MODEL-005, a broader task objective that includes technical constraint guidance was associated with higher ERROR-adherence than the original narrower objective across all three tested BENCH-002 tasks. The effect was consistent in direction (+19 to +30 percentage points) and magnitude. However, the broader objective was not a pure framing manipulation — it included additional technical keywords that may themselves contribute to the effect. Therefore, the experiment demonstrates a strong replication signal for the objective manipulation but does not isolate whether the benefit comes from framing, technical content, or their interaction.

---

```
P125 COMPLETE
DIAGNOSTIC-008 SCIENTIFIC REVIEW COMPLETE

REPLICATION:
E3a > BASE on 3/3 tasks

CLASSIFICATION:
STRONG REPLICATION SIGNAL

CAUSALITY:
NOT ESTABLISHED (H1 confound: technical content in E3a objectives)

H2 (Task Framing):
PROMISING / SUPPORTED SIGNAL

H3 (Feedback Overload):
NOT TESTED BY THIS EXPERIMENT

H4 (Variability):
NOT ELIMINATED — but E3a appears to reduce it

C3:
NOT JUSTIFIED — E3a provides a more parsimonious explanation

NEXT RESEARCH GATE:
E3a wording deconfounding study (Direction A)

293/293 REGRESSION:
PASS
```
