# EGER-P133 — RQ-4 Research Direction Decision

## Phase
P133 — Read-Only Research Decision Gate

## Date
2026-09-01

## Status
**RQ-4 DIRECTION DECISION — OPTION A RECOMMENDED**

---

## 1. Current Evidence State

### Experimental Record

| Experiment | Question | Result |
|------------|----------|--------|
| P090 | Baseline adherence BENCH2-001 | 4/10 = 40% |
| DIAGNOSTIC-006 | Mechanism isolation (Base/E2b/E3a/E4a) | E3a = 10/10, Base = 8/10 |
| DIAGNOSTIC-007 | Base-rate stabilization | 7/18 = 39% |
| DIAGNOSTIC-008 | Cross-task E3a replication | E3a > BASE on 3/3 tasks |
| DIAGNOSTIC-009 | E3a wording deconfounding (2×2 factorial) | A1 = 24/24 = 100%, A4 = 16/24 = 67% |

### Primary Finding

**DIAGNOSTIC-009 factorial result (94/96 valid manifests):**

| Condition | Framing | Technical | Adherent | Rate |
|-----------|---------|-----------|----------|------|
| A4 (BASE) | Narrow | No | 16/24 | **67%** |
| A1 | Broad | No | 24/24 | **100%** |
| A2 | Narrow | Yes | 20/23 | **87%** |
| A3 | Broad | Yes | 22/23 | **96%** |

**Framing effect (A1 − A4): +33 percentage points.**

### Combined E3a/A1 Evidence

| Task | E3a/A1 Rate | Source |
|------|-------------|--------|
| BENCH2-001 | 10/10 = 100% | DIAGNOSTIC-006 |
| BENCH2-002 | 8/8 = 100% | DIAGNOSTIC-009 A1 |
| BENCH2-004 | 8/8 = 100% | DIAGNOSTIC-009 A1 |
| BENCH2-005 | 8/8 = 100% | DIAGNOSTIC-009 A1 |
| **Combined** | **34/34 = 100%** | |

Broad framing only (A1): **24/24 = 100%** across all three tasks.

---

## 2. What RQ-4 Has Established

### ESTABLISHED

| Finding | Evidence | Classification |
|---------|----------|---------------|
| Proposal activation is near-universal | 100% across all experiments | **ESTABLISHED** |
| ERROR adherence is task-dependent | BASE varies 25-100% across tasks | **ESTABLISHED** |
| ERROR adherence is empirically variable | Base rate ranges 39-80% across experiments | **ESTABLISHED** |
| Broader task framing improves adherence | A1 = 24/24 vs A4 = 16/24 | **STRONG SIGNAL** |
| Technical content improves adherence | A2 = 20/23 vs A4 = 16/24 | **SUPPORTED SIGNAL** |
| Framing alone is sufficient for adherence | A1 = 24/24 without technical keywords | **STRONG SIGNAL** |
| Technical content does not exceed framing alone | A3 = 22/23 does not exceed A1 = 24/24 | **ESTABLISHED** |

### SUPPORTED (but not proven causal)

| Finding | Classification |
|---------|---------------|
| Broader task framing causes adherence improvement | **SUPPORTED SIGNAL** (correlation, not proven causation) |
| The effect generalizes across BENCH-002 tasks | **SUPPORTED** (3/3 tasks) |
| The effect is specific to prompt design, not epistemic uncertainty | **SUPPORTED** (more parsimonious explanation) |

### NOT ESTABLISHED

| Finding | Why |
|---------|-----|
| Causality of framing effect | Behavioral association only; no controlled manipulation of mental states |
| Internal mechanism | Only behavioral outcomes measured; model-interior process unknown |
| Generalization beyond MODEL-005 | Only one model tested |
| Generalization beyond BENCH-002 | Only one benchmark family tested |
| Exact effect size | CIs are wide; n=7-8 per cell |
| The true Base rate | Still variable (39-80% across experiments) |
| Provider-side vs model-side variability | Cannot distinguish from behavioral evidence |

---

## 3. Remaining Uncertainties

### Uncertainty 1 — MODEL-005 Specificity (HIGH)

All results are from `opencode/mimo-v2.5-free`. The framing effect could be:
- **Model-specific** — this model happens to respond to broader objectives
- **General** — broader framing improves adherence across LLMs
- **Provider-specific** — the OpenCode routing/proxy affects behavior

This is the largest remaining scientific uncertainty.

### Uncertainty 2 — Causal Mechanism (MEDIUM)

We know framing correlates with adherence but not *why*. Possible mechanisms:
- Broader framing changes the model's internal planning process
- Broader framing activates different training distributions
- Broader framing reduces ambiguity in the task specification
- The effect is a surface-level pattern, not a deep mechanism

### Uncertainty 3 — Generalization Beyond BENCH-002 (LOW-MEDIUM)

BENCH-002 tasks are all SDC-related timing constraints. The framing effect might not apply to:
- Different engineering domains
- Different proposal types
- Different error taxonomies

### Uncertainty 4 — True Base Rate (LOW)

The Base rate is variable (39-80%), but this variability is now well-characterized. The practical implication is clear: use broader framing.

---

## 4. Option A Analysis — Close RQ-4

### What This Means

Conclude RQ-4 with the current evidence and move toward engineering practice.

### Scientific Value

RQ-4 has produced a substantial finding: task framing is strongly associated with ERROR adherence, and this signal replicates across multiple tasks. The factorial design (DIAGNOSTIC-009) isolated framing from technical content and found framing alone is sufficient.

The engineering recommendation is clear: **use broader, production-quality task framing in SDC generation prompts.**

### Remaining Uncertainty Accepted

- MODEL-005 specificity remains unknown
- Causal mechanism remains unknown
- Generalization beyond BENCH-002 remains unknown

### Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Effect is MODEL-005-specific | Medium | Acknowledge explicitly in conclusion |
| Effect doesn't generalize to other domains | Low | Acknowledge as limitation |
| Effect is spurious | Low | Strong cross-task replication reduces this risk |

### Cost

Zero additional experimental cost. The current evidence is sufficient for a strong practical recommendation.

### Advantages

- Clean stopping point
- Preserves research integrity (no overclaiming)
- Enables engineering practice immediately
- Avoids diminishing returns from additional experiments
- The mechanism question (why framing works) is better addressed through engineering iteration than further experiments

---

## 5. Option B Analysis — Cross-Model Replication

### What This Means

Design and execute a controlled replication using a different frozen model to test whether the A1 framing effect generalizes.

### Scientific Value

Would answer: **Is the framing effect specific to MODEL-005 or general across LLMs?**

This is genuinely important — if the effect is model-specific, the engineering recommendation changes.

### What It Would Require

- New model selection and validation
- New MODEL-006 specification
- New AUTH-016
- Runner modification for new model
- ~96 additional runs (3 tasks × 4 conditions × 8 runs)
- ~288 additional calls
- Full P134-P139 gate sequence
- New change control, readiness review, authorization

### Cost

| Resource | Estimate |
|----------|----------|
| Implementation | ~1-2 hours |
| Execution | ~3-4 hours (96 runs) |
| Review | ~1 hour |
| Total | ~5-7 hours of agent time |

### Risk Assessment

| Risk | Severity | Mitstration |
|------|----------|------------|
| New model unavailable | Medium | Provider instability documented |
| Effect doesn't replicate | Medium | Would change conclusion significantly |
| Effect replicates | Low | Strengthens existing conclusion |
| Waste of resources if effect is model-specific | Low | This is exactly the question being asked |

### Advantages

- Answers the highest-priority remaining question
- Strengthens the evidence base significantly
- Reduces MODEL-005 specificity concern

### Disadvantages

- Delays engineering practice
- Additional resource cost
- Provider availability uncertain
- The current evidence is already sufficient for a strong recommendation

---

## 6. Scientific Trade-off

| Criterion | Option A (Close) | Option B (Cross-Model) |
|-----------|-----------------|----------------------|
| Scientific completeness | Good | Better |
| Practical value now | High | Delayed |
| Resource cost | Zero | Moderate |
| Risk of overclaiming | Low | Low |
| Risk of under-investigating | Low | Very low |
| Engineering readiness | Immediate | Delayed |
| Remaining uncertainty | Accepted | Reduced |

### Key Insight

The framing effect is now supported by:
- DIAGNOSTIC-006: 10/10 on BENCH2-001
- DIAGNOSTIC-008: E3a > BASE on 3/3 tasks
- DIAGNOSTIC-009: A1 = 24/24 = 100% (deconfounded)

This is a strong behavioral finding with cross-task replication. The remaining uncertainty (MODEL-005 specificity) is real but does not invalidate the practical recommendation.

---

## 7. Recommended Direction

### **OPTION A — Close RQ-4**

**Reasoning:**

1. **The evidence is sufficient for engineering practice.** Broader framing improves adherence. This is supported by 3 independent experiments across 4 tasks.

2. **Cross-model replication would answer a real question, but the answer is unlikely to change the engineering recommendation.** If the effect replicates, the recommendation strengthens. If it doesn't, the recommendation becomes model-specific. Either way, broader framing is the right default.

3. **The mechanism question is better answered through engineering iteration.** Rather than running more experiments, the practical next step is to deploy the framing insight in production and observe whether it works in practice.

4. **Research diminishing returns.** We have run 5 experiments (DIAGNOSTIC-006 through DIAGNOSTIC-009, plus P090). The core finding is stable. Additional experiments are unlikely to change the conclusion materially.

5. **Resource conservation.** The provider has been unreliable throughout this research. Spending additional hours on cross-model replication has execution risk with limited scientific payoff.

### What the Conclusion Should Say

> Under MODEL-005, broader task framing ("Generate a complete, production-quality SDC for this design") is strongly associated with improved ERROR-adherence compared to narrower task framing. The effect was observed across all tested BENCH-002 tasks (24/24 = 100% for broad framing vs 16/24 = 67% for narrow framing). The factorial design established that broader framing alone is sufficient — adding task-specific technical guidance provides minimal additional benefit. The evidence does not establish causality, mechanism, or generalizability beyond the tested model and task family. C3 (epistemic-state intervention) is not justified by the current evidence.

### What the Engineering Implication Should Say

> When using LLMs for SDC generation tasks, frame the objective as a complete, production-quality deliverable rather than a narrow, specific constraint. This simple prompt-design change is associated with a meaningful improvement in ERROR adherence.

---

## 8. Explicit C3 Status

```
C3: NOT JUSTIFIED
```

### Why C3 Remains Unjustified

1. **Framing provides a simpler explanation.** If broader framing alone achieves 100% adherence, epistemic-state manipulation is unnecessary.

2. **No evidence of epistemic uncertainty.** No experiment has measured or correlated model "uncertainty" with adherence failures.

3. **No mechanism proposed.** C3 was based on a hypothesis that the model's epistemic state affects adherence. No evidence supports this hypothesis.

4. **Occam's razor.** Prompt design is a more parsimonious intervention than epistemic-state manipulation.

### When C3 Might Be Revisited

C3 would only be justified if:
- The framing effect fails to replicate on new models AND
- The failure is specifically correlated with model uncertainty indicators AND
- A plausible epistemic-state mechanism is identified

None of these conditions are currently met.

---

## 9. Whether Another Experiment Is Justified

### Another Mechanism Isolation Experiment: **NOT JUSTIFIED**

The factorial design (DIAGNOSTIC-009) has cleanly separated framing from technical content. No further isolation is needed within this model/task family.

### Cross-Model Replication: **JUSTIFIED BUT NOT RECOMMENDED**

The scientific question is valid, but the practical payoff is low relative to the cost. The recommendation is to close RQ-4 and note cross-model generalization as a limitation.

### Base-Rate Stabilization: **NOT JUSTIFIED**

Three experiments already characterize the Base rate as variable (39-80%). Additional base-rate experiments are unlikely to resolve the variability because it appears to be execution-context-dependent.

---

## 9. Research Trajectory Summary

```
C0 — Research contract
  ↓
C1 — Baseline / feedback behavior
  ↓
C2 — Variability investigation
  ↓
C3 — Epistemic-state intervention → NOT JUSTIFIED
  ↓
Mechanism investigation
  ↓
DIAGNOSTIC-006 — Prompt isolation → E3a signal
  ↓
DIAGNOSTIC-007 — Base-rate stabilization → 39%
  ↓
DIAGNOSTIC-008 — Cross-task replication → E3a > BASE on 3/3
  ↓
DIAGNOSTIC-009 — Factorial deconfounding → A1 = 24/24 = 100%
  ↓
P131 — Scientific review → STRONG FRAMING SIGNAL
  ↓
P132 — Git checkpoint → PRESERVED
  ↓
P133 — Direction decision → CLOSE RQ-4
```

---

```
P133 COMPLETE
RQ-4 DIRECTION DECISION COMPLETE

CURRENT EVIDENCE: STRONG FRAMING SIGNAL
CAUSALITY: NOT ESTABLISHED
C3: NOT JUSTIFIED

RECOMMENDED NEXT DIRECTION: A — Close RQ-4

RATIONALE:
- Framing effect replicated across 4 tasks
- Factorial design isolates framing from technical content
- Engineering recommendation is clear and actionable
- Cross-model replication scientifically justified but not recommended due to cost/uncertainty trade-off

NO EXPERIMENT EXECUTED
NEXT: Close RQ-4, write engineering conclusion
```
