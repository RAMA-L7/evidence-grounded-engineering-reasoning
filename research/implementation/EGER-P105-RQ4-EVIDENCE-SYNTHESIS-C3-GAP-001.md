# EGER-P105 — RQ-4 Evidence Synthesis & C3 Gap Analysis

| Field | Value |
|---|---|
| ID | EGER-P105-RQ4-EVIDENCE-SYNTHESIS-C3-GAP-001 |
| Date | 2026-08-28 |
| Scope | READ-ONLY synthesis of all RQ-4 evidence |
| Status | **SYNTHESIS COMPLETE** |

---

## 1. Executive Summary

After 52 prompts of scientific investigation (P052–P104), the evidence establishes:

1. **Structured feedback reliably causes proposal activation** (100%)
2. **ERROR adherence is task-dependent and stochastic for some tasks**
3. **BENCH2-001 + minimal SDC shows reduced adherence (~53%)**
4. **All other tested conditions show high adherence (~100%)**
5. **The causal mechanism is unknown**

C3 remains blocked. The evidence does not specifically motivate an epistemic-state intervention.

---

## 2. Complete Evidence Inventory

### Condition-A observations (BENCH2-001 + minimal SDC)

| Source | Runs | Adherent | Rate |
|--------|------|----------|------|
| P074 (RQ-4 treatment) | 1 | 0 | 0% |
| P082 (Diagnostic) | 1 | 1 | 100% |
| P084 (Repeated A) | 3 | 1 | 33% |
| P090 (Controlled 10-run) | 10 | 4 | 40% |
| P103 W (2×2 cross) | 5 | 4 | 80% |
| **Total** | **20** | **10** | **50%** |

### Condition-Z observations (BENCH2-002 + rich SDC)

| Source | Runs | Adherent | Rate |
|--------|------|----------|------|
| P074 (RQ-4 treatment) | 1 | 1 | 100% |
| P097 (Controlled 10-run) | 10 | 10 | 100% |
| P103 Z (2×2 cross) | 5 | 5 | 100% |
| **Total** | **16** | **16** | **100%** |

### Other conditions (P103)

| Condition | Runs | Adherent | Rate |
|-----------|------|----------|------|
| X (rich SDC + BENCH2-001) | 5 | 5 | 100% |
| Y (minimal SDC + BENCH2-002) | 5 | 5 | 100% |

---

## 3. Observed Facts (Not Interpretations)

### Fact 1: Proposal activation is universal
- 36/36 runs across all conditions produced proposal_changed=True
- The model always changes its output when given structured feedback
- This is deterministic across all tested conditions

### Fact 2: ERROR adherence varies by condition
- W (minimal + 001): 10/20 = 50%
- X (rich + 001): 5/5 = 100%
- Y (minimal + 002): 5/5 = 100%
- Z (rich + 002): 16/16 = 100%

### Fact 3: Only W shows failures
- Every non-adherent run occurred in condition W
- No failures in X, Y, or Z

### Fact 4: W failures are stochastic, not systematic
- P090 showed alternating success/failure patterns
- Same inputs sometimes succeed, sometimes fail
- No systematic pattern in which runs fail

### Fact 5: Sample sizes are modest
- Largest controlled sample: n=10 (P090, P097)
- 2×2 cross: n=5 per cell
- Combined W: n=20

### Fact 6: SDC content and complexity are confounded
- "Rich" SDC contains specific constructs (generated clock, clock groups), not just more text
- "Minimal" SDC is a bare clock definition
- We cannot separate content from complexity

---

## 4. Supported Interpretations

### Interpretation 1: Structured feedback causes proposal revision
**STRONGLY SUPPORTED.** 36/36 runs produced proposal changes. The model reliably responds to feedback.

### Interpretation 2: ERROR adherence is task-dependent
**SUPPORTED.** Condition W shows ~50% adherence; all other conditions show ~100%. The difference is consistent across experiments.

### Interpretation 3: BENCH2-001 + minimal SDC is the lowest-adherence condition
**SUPPORTED.** W is the only condition with failures. Combined rate: 10/20 = 50%.

### Interpretation 4: Some tasks show stochastic adherence
**SUPPORTED for BENCH2-001.** P090's alternating pattern (runs 1–4 fail, 5 succeeds, 6–7 fail, 8–10 succeed) is consistent with stochastic behavior.

---

## 5. Plausible Hypotheses (Not Yet Established)

### Hypothesis A: Task context drives adherence
BENCH2-002's context (two clock domains, generated clock) may make the model more likely to address I/O delays. The P103 Y condition (minimal SDC + BENCH2-002 context) showed 5/5 adherence, supporting this.

**Status:** Plausible but not established. Y has n=5 only.

### Hypothesis B: SDC content drives adherence
The rich SDC's specific constructs (generated clock, clock groups) may provide context that makes I/O delays more salient. The P103 X condition (rich SDC + BENCH2-001) showed 5/5, supporting this.

**Status:** Plausible but not established. X has n=5 only.

### Hypothesis C: Both factors interact
The pattern (W fails, X/Y/Z succeed) could indicate an interaction. But n=5 per cell is insufficient to test for interactions.

**Status:** Possible but not testable at current sample size.

### Hypothesis D: An unmeasured variable causes the difference
The real cause might be something we haven't measured (e.g., prompt token count, specific SDC construct ordering, provider-side caching).

**Status:** Cannot be ruled out.

---

## 6. Unsupported Claims

### Claim: "BENCH2-002 is deterministically adherent"
**UNSUPPORTED.** 16/16 successes is impressive but n=16 is insufficient to prove determinism. The true rate could be 90% and we'd observe 16/16 about 20% of the time.

### Claim: "SDC complexity causes adherence"
**UNSUPPORTED as causation.** SDC content and complexity are confounded. We have not manipulated complexity while holding content constant.

### Claim: "Task context causes adherence"
**UNSUPPORTED as causation.** We have not manipulated context while holding SDC constant (the 2×2 cross did this, but with n=5).

### Claim: "The adherence rate is 50% for BENCH2-001"
**OVERSTATED.** 10/20 = 50% is a point estimate with wide uncertainty. The true rate could be anywhere from ~27% to ~73%.

### Claim: "C3 would improve adherence"
**NOT MOTIVATED.** The evidence shows task-dependent stochastic adherence. Epistemic state is one possible mechanism, but nothing in the current evidence specifically points to it.

---

## 7. What Remains Unresolved

### Unresolved 1: The causal mechanism
We do not know WHY the model sometimes follows ERROR findings and sometimes does not. Possible mechanisms:
- Task description interpretation
- SDC semantic context
- Token-level attention patterns
- Provider-side nondeterminism
- Some combination

### Unresolved 2: The SDC content vs complexity confound
We cannot determine whether the W/X difference is caused by:
- More text (complexity)
- Specific constructs (content)
- Semantic relevance to the task
- Some combination

### Unresolved 3: Whether X/Y/Z are truly deterministic
With n=5, we cannot rule out that these conditions are stochastic with high adherence rates. Only larger samples would resolve this.

### Unresolved 4: Generalization
We tested only MODEL-005 (mimo-v2.5-free) on BENCH-002 tasks. We do not know whether the pattern holds for other models or benchmarks.

### Unresolved 5: The mechanism of stochastic behavior
Even if we established that BENCH2-001 is stochastic, we don't know what causes the nondeterminism. Temperature=0.0 should produce deterministic output, yet it doesn't. This suggests provider-side or system-level nondeterminism.

---

## 8. Is Another Experiment Necessary?

### For RQ-4 itself: NO
RQ-4 is answered:
> Structured evidence feedback causes proposal revision (100%) and sometimes ERROR correction (~50% for BENCH2-001, ~100% for others). The effect is task-dependent and stochastic for some tasks.

### For understanding the mechanism: YES, if we want to pursue C3
Before C3, we would need to understand:
1. What determines adherence in a given run
2. Whether epistemic state could influence this
3. Whether the mechanism is model-specific

### For generalizability: YES
We would need to test:
- Other tasks (BENCH2-003 through 006)
- Other models
- Other benchmarks

---

## 9. Evidence Quality Assessment

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Internal validity | GOOD | Controlled conditions, frozen protocol |
| Statistical power | MODEST | n=5–10 per condition |
| Construct validity | ADEQUATE | ERROR adherence is measurable |
| External validity | LOW | Single model, single benchmark |
| Mechanistic understanding | LOW | We observe but don't explain |

---

## 10. Strongest Defensible RQ-4 Conclusion

> Structured evidence feedback reliably causes the model to revise its engineering proposal (100% activation). In some task configurations, the revision addresses identified ERROR findings (adherence). Adherence is task-dependent: BENCH2-001 with a minimal initial SDC shows stochastic adherence (~50%), while other tested configurations show high adherence (~100%). The causal mechanism is unknown.

---

## 11. Remaining Scientific Gaps

1. **Mechanism** — What determines whether the model follows ERROR findings?
2. **SDC content vs complexity** — Which aspect drives adherence?
3. **Determinism of high-adherence conditions** — Are X/Y/Z truly deterministic?
4. **Generalization** — Does the pattern hold for other models/tasks?
5. **Epistemic state relevance** — Could epistemic state improve adherence?

---

## 12. C3 Assessment

### Is C3 scientifically justified?
**NOT YET.** C3 tests whether epistemic state improves reasoning. The current evidence shows:
- Task-dependent adherence
- Stochastic behavior for some tasks
- Unknown mechanism

None of these findings specifically motivate an epistemic-state intervention. Before C3, we would need:
1. Evidence that the model's "uncertainty" correlates with adherence failures
2. A plausible mechanism by which epistemic state could improve adherence
3. Evidence that the mechanism is model-interior rather than provider-side

### What would motivate C3?
If we found that:
- The model's non-adherent runs show different internal representations
- Epistemic state could provide information that resolves the uncertainty
- The mechanism is model-side rather than provider-side

Then C3 would be motivated. Currently, none of these conditions are met.

---

## 13. Status

```
P105 COMPLETE
EVIDENCE SYNTHESIS RECORDED
RQ-4: ANSWERED (PROBABILISTIC EFFECT)
C3: NOT MOTIVATED BY CURRENT EVIDENCE
STRONGEST DEFENSIBLE CLAIM: STRUCTURED FEEDBACK CAUSES PROPOSAL REVISION;
ADHERENCE IS TASK-DEPENDENT AND STOCHASTIC FOR SOME TASKS
NEXT GATE: DETERMINED BY RESEARCH QUESTION DECISION
```
