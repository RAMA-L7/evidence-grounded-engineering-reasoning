# EGER-P135 — EGER Research Architecture Reconciliation & Next-Gate Decision

## Phase
P135 — Read-Only Research Architecture Review

## Date
2026-09-01

## Status
**ARCHITECTURE RECONCILED — REVISED RESEARCH PATH RECOMMENDED**

---

## 1. Executive Summary

The original EGER C0–C5 ablation assumed that each stage would add one architectural mechanism and demonstrate incremental reliability improvement. The evidence obtained through P090–P134 has **substantially diverged** from this assumption. The research discovered that **prompt design (task framing)** explains more variance in ERROR adherence than the epistemic-state mechanisms C3–C5 were designed to test. This is not a failure — it is a successful identification that the original hypothesis is less explanatory than an observed behavioral finding.

**Recommended architecture:** Revise the research path to treat C3–C5 as **separate architectural hypotheses** rather than mandatory experimental stages. Close the current empirical phase. Move toward engineering synthesis and architecture design informed by the actual evidence.

---

## 2. Original C0–C5 Architecture

The EGER Research Contract v0.2 defines the primary controlled ablation:

| Stage | Mechanism Added | Assumption |
|-------|----------------|-----------|
| **C0** | None (LLM only) | Baseline |
| **C1** | Textual feedback | Feedback improves revision |
| **C2** | Structured evidence | Structured evidence is more actionable than text |
| **C3** | Explicit epistemic state | Epistemic uncertainty affects adherence |
| **C4** | Evidence-conditioned routing | Deterministic routing reduces invalid actions |
| **C5** | Non-bypassable authorization | Authorization gate prevents regressions |

The original plan assumed a clean causal chain: each mechanism would produce measurable improvement, justifying the next.

---

## 3. Actual Evidence Trajectory

The research did not follow the planned progression. Instead:

```
C0 (baseline) → C1/C2 (feedback/revision) → RQ-4 mechanism investigation
                                                    ↓
                                              DIAGNOSTIC-006
                                              DIAGNOSTIC-007
                                              DIAGNOSTIC-008
                                              DIAGNOSTIC-009
                                                    ↓
                                              STRONG FRAMING SIGNAL
                                                    ↓
                                              C3 NOT JUSTIFIED
```

The evidence discovered a **more parsimonious explanation** (prompt design) before the C3–C5 mechanisms were tested.

---

## 4. C0–C5 Classification Table

| Stage | Classification | Evidence Supporting | Evidence Missing | Experiment Justified? | Remain in Architecture? |
|-------|---------------|--------------------|--------------------|---------------------|------------------------|
| **C0** | **ESTABLISHED** | 6/6 tasks completed; proposal activation ~100%; no deterministic validation achieved | Oracle scope limitation acknowledged | No — complete | **Yes — as baseline** |
| **C1** | **ESTABLISHED** | Structured evidence reliably activates revision (100% activation); ERROR adherence is task-dependent and stochastic; factorial design isolates key variables | Mechanism of adherence variability unresolved during C1 phase | No — complete | **Yes — as feedback/revision evidence** |
| **C2** | **PARTIALLY SUPPORTED** | Structured feedback is more actionable than text; absorbed into C1 investigation | Confound: structured feedback may provide more information, not just better representation; dedicated C2 comparison not isolated | No — C1 investigation already captured this | **Yes — as absorbed into C1** |
| **C3** | **NOT JUSTIFIED** | No evidence of model epistemic uncertainty; prompt design provides simpler explanation; A1 = 24/24 = 100% with prompt change alone | No experiment measuring epistemic state; no correlation between uncertainty and adherence | **No** — insufficient motivation | **Yes — as deferred hypothesis** |
| **C4** | **DEFERRED** | Not tested | Routing design not evaluated | **No** — no research question motivates it | **Yes — as architectural component, not experimental stage** |
| **C5** | **DEFERRED** | Not tested | Gate design not evaluated | **No** — no research question motivates it | **Yes — as architectural component, not experimental stage** |

---

## 5. Evidence Supporting Each Classification

### C0 — ESTABLISHED

- 6/6 tasks completed with LLM-only baseline
- Proposal activation near-universal
- No deterministic validation achieved (INSUFFICIENT oracle scope)
- **Valid baseline with documented limitations**

### C1/C2 — ESTABLISHED

- Structured evidence reliably causes proposal revision (100% activation)
- ERROR adherence is task-dependent (25–100% across tasks)
- ERROR adherence is empirically variable (39–80% across experiments)
- Base-rate stabilization achieved (DIAGNOSTIC-007: 39%)
- **Structured feedback is effective for activation; adherence depends on other factors**

### C3 — NOT JUSTIFIED

- No experiment measured model epistemic uncertainty
- No correlation between uncertainty and adherence failures identified
- Prompt design (broader framing) explains more variance
- A1 = 24/24 = 100% with a simple prompt change
- **The original hypothesis (epistemic-state intervention improves reliability) is less explanatory than the observed behavioral finding (prompt design improves reliability)**

### C4 — DEFERRED

- Routing design is an architectural decision, not an experimental question
- The research has not identified a routing problem that needs solving
- **Deferrable until architecture is designed based on actual evidence**

### C5 — DEFERRED

- Authorization gate is an architectural decision
- The research has not identified an authorization problem that needs solving
- **Deferrable until architecture is designed based on actual evidence**

---

## 6. Original-Plan vs Evidence-Driven-Plan Comparison

| Aspect | Original Plan | Evidence-Driven Reality |
|--------|--------------|------------------------|
| C3 trigger | C2 completion | C3 not motivated by evidence |
| C4 trigger | C3 completion | C4 not motivated by evidence |
| C5 trigger | C4 completion | C5 not motivated by evidence |
| Key variable | Epistemic state | Prompt design (task framing) |
| Mechanism | Model-interior uncertainty | Behavioral prompt-response relationship |
| Architecture assumption | Each stage adds one causal mechanism | Prompt design explains more than epistemic-state manipulation |
| Required experiments | All C0–C5 | C0, C1/C2 complete; C3–C5 not experimentally required |

---

## 7. C3 — Should It Remain Blocked?

**Yes. C3 should remain NOT JUSTIFIED.**

### Reasoning

1. **No evidence motivates it.** No experiment has measured or correlated model epistemic uncertainty with adherence failures.

2. **More parsimonious explanation exists.** Prompt design explains adherence variability without invoking internal model states.

3. **A1 = 24/24 = 100%** with a simple prompt change. If a prompt change achieves 100% adherence, adding epistemic-state manipulation is unnecessary complexity.

4. **C3 was a hypothesis, not a proven mechanism.** The research successfully tested the hypothesis and found it less explanatory than an alternative.

5. **Blocking is scientifically correct.** The research process should stop when the evidence does not motivate continuation. C3 blocking is a sign of scientific integrity, not research failure.

### When C3 Might Be Reopened

C3 would only be scientifically justified if:
- The framing effect fails to replicate on new models
- AND the failure is specifically correlated with model uncertainty indicators
- AND a plausible epistemic-state mechanism is identified
- AND prompt design alone proves insufficient for some task/model combinations

None of these conditions are currently met.

---

## 8. C4/C5 — Should They Remain Deferred?

**Yes. C4 and C5 should remain DEFERRED.**

### Reasoning

1. **C4 and C5 are architectural decisions, not experimental questions.** Evidence-conditioned routing (C4) and non-bypassable authorization (C5) are design patterns that can be implemented based on engineering judgment, not experimental evidence.

2. **The research has not identified a routing or authorization problem.** The evidence shows prompt design is the key variable. Routing and gate design are orthogonal to this finding.

3. **C4/C5 depend on C3 being justified.** The original C0–C5 progression assumed C3 would be tested first. Since C3 is not justified, C4/C5 lose their experimental motivation.

4. **C4/C5 can be designed based on actual evidence.** The architecture should be informed by what was learned (prompt design matters, structured feedback activates revision) rather than by the original plan (epistemic state matters).

---

## 9. Remaining Scientifically Meaningful Questions

| Question | Priority | Requires Experiment? | Current Status |
|----------|----------|---------------------|----------------|
| Does the framing effect generalize to other models? | HIGH | **Optional** (cross-model replication) | MODEL-005 only |
| Does the framing effect apply to other EDA domains? | MEDIUM | **Optional** (domain replication) | BENCH-002 only |
| Why does broader framing improve adherence? | MEDIUM | **Better through engineering practice** | Mechanism unknown |
| What is the true long-run Base rate? | LOW | **No** — well-characterized as variable | 39–80% range established |
| Does the model have internal epistemic states that affect behavior? | LOW | **Not currently motivated** | No evidence measured |

---

## 10. Recommended Research Architecture Going Forward

### Revised Architecture

```
PHASE 1 — EMPIRICAL (COMPLETE)
├── C0: Baseline                          ✅ ESTABLISHED
├── C1/C2: Feedback/Revision              ✅ ESTABLISHED
├── RQ-4: Mechanism Investigation         ✅ CLOSED
│   ├── DIAGNOSTIC-006: Prompt isolation
│   ├── DIAGNOSTIC-007: Base-rate stabilization
│   ├── DIAGNOSTIC-008: Cross-task replication
│   └── DIAGNOSTIC-009: Factorial deconfounding
└── Finding: Prompt design is the strongest signal

PHASE 2 — ARCHITECTURE SYNTHESIS (NEXT)
├── Design EGER architecture based on actual evidence
├── Integrate prompt-design insight into architecture
├── Implement C4 routing as architectural component (not experiment)
├── Implement C5 authorization as architectural component (not experiment)
└── C3 remains deferred (not motivated by evidence)

PHASE 3 — OPTIONAL FUTURE RESEARCH
├── Cross-model replication (if generalizability needed)
├── Domain replication (if scope expansion needed)
└── C3 epistemic-state test (if new evidence motivates it)
```

### What Changes

| Original | Revised |
|----------|---------|
| C3–C5 are mandatory experimental stages | C3 is a deferred hypothesis; C4/C5 are architectural components |
| Each stage adds one mechanism | Architecture designed from actual evidence |
| C3 must be tested before C4/C5 | C4/C5 can be designed without C3 |
| Research continues until C5 complete | Empirical phase closes when evidence is sufficient |

### What Stays the Same

| Item | Status |
|------|--------|
| C0 baseline | Complete and preserved |
| C1/C2 feedback evidence | Complete and preserved |
| RQ-4 findings | Closed with conservative claims |
| P1–P8 principles | Applicable to architecture design |
| Authority separation (P7) | Still the core architectural principle |
| Deterministic oracle boundary | Still the core engineering invariant |

---

## 11. Distinction Between Findings, Implications, and Hypotheses

### Empirical Findings (What the Evidence Shows)

| Finding | Classification |
|---------|---------------|
| Structured evidence causes proposal revision | **ESTABLISHED** |
| ERROR adherence is task-dependent | **ESTABLISHED** |
| ERROR adherence is empirically variable | **ESTABLISHED** |
| Broader framing improves adherence | **STRONG SIGNAL** |
| Technical content improves adherence | **SUPPORTED SIGNAL** |
| Framing alone is sufficient | **STRONG SIGNAL** |

### Engineering Implications (What This Means for Practice)

| Implication |
|-------------|
| Use broader, production-quality framing in SDC generation prompts |
| Structured evidence feedback is effective for activating revision |
| Prompt design is a more actionable lever than epistemic-state manipulation |
| The EGER architecture should incorporate prompt-design insights |

### Future Hypotheses (What Might Be Tested Later)

| Hypothesis | Status |
|-----------|--------|
| Framing effect generalizes across models | **Testable if needed** |
| Framing effect applies to other EDA domains | **Testable if needed** |
| Epistemic-state intervention improves adherence | **NOT JUSTIFIED — requires new evidence** |
| Evidence-conditioned routing reduces invalid actions | **DEFERRED — architectural decision** |
| Non-bypassable authorization prevents regressions | **DEFERRED — architectural decision** |

---

## 12. Final Decision

### The Original C0–C5 Progression Is No longer Scientifically Justified as a Mandatory Experimental Sequence

The evidence has revealed that:

1. **C0 and C1/C2 are complete and established.** These stages provided the foundation for understanding feedback/revision behavior.

2. **C3 is not motivated by evidence.** The research found a more parsimonious explanation (prompt design) before C3 was tested.

3. **C4 and C5 are architectural decisions, not experimental stages.** They can be designed based on actual evidence rather than experimental results.

4. **The empirical phase is complete.** RQ-4 is closed. The strongest finding (prompt design) is established through multiple experiments.

5. **The next phase is architecture synthesis.** Design the EGER system based on what was learned, not based on the original plan.

### Recommended Action

**Close the empirical research phase. Move to architecture synthesis.**

The EGER architecture should be designed to incorporate:
- Structured evidence feedback (from C1)
- Broader task framing (from RQ-4/DIAGNOSTIC-009)
- Deterministic oracle boundary (from P1–P8 principles)
- Authority separation (from P7)
- Non-bypassable verification (from P1)

C3 (epistemic-state intervention) remains a **deferred hypothesis** — scientifically legitimate but not currently motivated by evidence.

---

```
P135 COMPLETE
RESEARCH ARCHITECTURE RECONCILIATION COMPLETE

C0: ESTABLISHED
C1: ESTABLISHED
C2: PARTIALLY SUPPORTED (absorbed into C1)
C3: NOT JUSTIFIED — remains blocked
C4: DEFERRED — architectural component
C5: DEFERRED — architectural component

RQ-4: CLOSED
CAUSALITY: NOT ESTABLISHED
C3: NOT JUSTIFIED

RECOMMENDED ARCHITECTURE:
- Close empirical phase
- Move to architecture synthesis
- C3 remains deferred
- C4/C5 become architectural components, not experimental stages
- Design EGER based on actual evidence (prompt design + structured feedback)

NO EXPERIMENT EXECUTED
```
