# EGER-P098 — Cross-Task Variability Scientific Review

| Field | Value |
|---|---|
| ID | EGER-P098-CROSS-TASK-VARIABILITY-SCIENTIFIC-REVIEW-001 |
| Date | 2026-08-28 |
| Status | **SCIENTIFIC REVIEW COMPLETE** |

---

## 1. Executive Summary

Two tasks tested under identical conditions (same model, Oracle, metadata, feedback mechanism):

| Task | Initial SDC | Adherence | Rate | 95% CI |
|------|------------|-----------|------|--------|
| BENCH2-001 | 51 chars (clock only) | 4/10 | 40% | [12.6%, 72.9%] |
| BENCH2-002 | 287 chars (clock + generated + groups) | 10/10 | 100% | [71.4%, 100.0%] |

The evidence supports **task-dependent adherence** — different tasks show different adherence rates under the same model and feedback mechanism. However, the confound between task SDC complexity and task identity cannot be resolved without further experiments.

---

## 2. Raw Evidence

### BENCH2-001 (P090)
- 10 identical runs, same 51-char SDC
- 4 adhered, 6 did not
- All 10 activated (changed output)
- Pattern: runs 1–4 failed, run 5 succeeded, runs 6–7 failed, runs 8–10 succeeded

### BENCH2-002 (P097)
- 10 identical runs, same 287-char SDC
- 10 adhered, 0 did not
- All 10 activated (changed output)
- Pattern: all 10 succeeded consistently

### Shared Properties
- Same model: MODEL-005 (mimo-v2.5-free)
- Same Oracle: 3b5c2f2
- Same metadata: eger.design_metadata.v1
- Same feedback mechanism: deterministic structured feedback
- Same feedback content: same ERROR findings (SDC-005, SDC-006)
- Same execution mode: sequential single batch
- Same budget: 30 calls per experiment

---

## 3. What Differs Between Tasks

| Property | BENCH2-001 | BENCH2-002 |
|----------|-----------|-----------|
| Initial SDC length | 51 chars | 287 chars |
| SDC constructs | create_clock only | create_clock + create_generated_clock + set_clock_groups |
| Task objective | "primary clock on clk" | "primary clock and correctly constrained generated clock" |
| Design context | Simple clock domain | Two clock domains, asynchronous |
| Initial scope | FULL | FULL |
| Initial errors | 2 (SDC-005, SDC-006) | 2 (SDC-005, SDC-006) |
| Feedback | Same | Same |

---

## 4. Statistical Caution

### What non-overlapping CIs do NOT mean
Non-overlapping confidence intervals (BENCH2-001 upper 72.9% vs BENCH2-002 lower 71.4%) **are not a valid hypothesis test**. They suggest a difference but do not prove it. The CIs barely touch (72.9% vs 71.4%), which means the evidence for a difference is suggestive but not conclusive.

### What would be needed for a formal test
A formal comparison would require:
- A two-proportion test (e.g., Fisher's exact test)
- Or a larger sample size
- Or a within-task crossover design

With n=10 per task, we can describe the observed difference but cannot formally test it.

### Correct interpretation
> BENCH2-002 showed higher adherence than BENCH2-001 in these specific experiments. The difference is notable but not formally tested.

---

## 5. Task-Dependent Adherence — Supported?

**PARTIALLY SUPPORTED.** The evidence shows different adherence rates for different tasks:
- BENCH2-001: stochastic (~40%)
- BENCH2-002: apparently deterministic (100%)

However, there are multiple confounds:

### Confound 1: SDC complexity vs task identity
BENCH2-002 has a richer initial SDC (287 chars) than BENCH2-001 (51 chars). We cannot determine whether the difference is caused by:
- SDC complexity (P076/P077 context-anchor hypothesis)
- Task identity (different tasks, different model behavior)
- Some other task-specific property

### Confound 2: n=10 is small
With n=10, the true adherence rate for BENCH2-002 could be anywhere from 71% to 100%. We cannot rule out that BENCH2-002 is also stochastic but happened to succeed in all 10 runs. The probability of 10/10 successes if the true rate is 80% is about 10.7% — not negligible.

### Confound 3: Provider-side nondeterminism
We cannot distinguish model-side from provider-side variability. BENCH2-002's 10/10 might reflect different provider behavior for different SDC inputs.

---

## 6. H1/H2/H3/H4 Assessment

### H1 (context anchoring)
**PARTIALLY SUPPORTED as association, not causation.** BENCH2-002 has a richer SDC and higher adherence. But we have not experimentally manipulated SDC complexity while holding task identity constant.

### H2 (task-scope interpretation)
**NOT TESTED.** We have not manipulated task objective wording while holding SDC constant.

### H3 (feedback overload)
**NOT TESTED.** We have not manipulated feedback content for BENCH2-002.

### H4 (model variability)
**SUPPORTED for BENCH2-001, NOT YET TESTED for BENCH2-002.** BENCH2-001 shows genuine stochastic behavior. BENCH2-002 showed 10/10 adherence, which is consistent with either deterministic behavior or stochastic behavior with a high adherence rate.

---

## 7. What Cannot Be Claimed

1. **That BENCH2-002 is deterministically adherent** — n=10 is insufficient. The true rate could be 80% and we'd see 10/10 about 10.7% of the time.

2. **That the CIs being non-overlapping proves a difference** — this is not a valid statistical test.

3. **That SDC complexity causes higher adherence** — this is an association, not a causal finding. We have not controlled for task identity.

4. **That the 40% rate for BENCH2-001 is the "true" rate** — the CI is wide [12.6%, 72.9%].

5. **That these results generalize to other models or tasks** — we tested only MODEL-005 on two tasks.

---

## 8. What CAN Be Claimed

1. **BENCH2-001 shows genuine stochastic adherence** — 4/10 in controlled conditions, with a pattern of alternating success/failure.

2. **BENCH2-002 showed consistent adherence** — 10/10 in controlled conditions, with no failures.

3. **The two tasks behaved differently** — the observed difference is notable, though not formally tested.

4. **Feedback activation is universal** — 100% across both tasks (20/20 runs).

5. **ERROR adherence is task-dependent** — different tasks show different patterns under the same model and feedback.

---

## 9. Remaining Confounds

| Confound | Status | Resolution Required |
|----------|--------|-------------------|
| SDC complexity vs task identity | Unresolved | Manipulate SDC while holding task constant |
| n=10 small sample | Unresolved | More runs or formal test |
| Provider-side variability | Irresolvable | Cannot control provider internals |
| Task description confound | Unresolved | Hold SDC constant, vary description |

---

## 10. Implications for C3

**C3 REMAINS BLOCKED.**

The evidence now shows:
- Adherence is task-dependent
- Some tasks are stochastic, others appear stable
- The mechanism is unknown

Before C3 (epistemic state), we would need to understand:
1. What determines whether a task shows stochastic or stable adherence
2. Whether epistemic state could influence this determination
3. Whether the effect is model-specific or general

The current evidence does not specifically motivate an epistemic-state intervention. The task-dependence finding is interesting but does not directly point to epistemic state as the mechanism.

---

## 11. Recommended Next Steps

1. **Formal cross-task comparison** — Fisher's exact test or larger sample
2. **SDC complexity manipulation** — test BENCH2-001 with BENCH2-002's SDC (and vice versa) to isolate SDC from task identity
3. **Additional tasks** — test BENCH2-004 and BENCH2-005 to see if the pattern holds
4. **Only after mechanism is understood:** consider C3

---

## 12. Status

```
P098 COMPLETE
SCIENTIFIC REVIEW RECORDED
TASK-DEPENDENT ADHERENCE: PARTIALLY SUPPORTED (ASSOCIATION)
H1: PARTIALLY SUPPORTED (ASSOCIATION, NOT CAUSATION)
H2/H3: NOT TESTED
H4: SUPPORTED FOR BENCH2-001, UNRESOLVED FOR BENCH2-002
C3: NOT AUTHORIZED
STATISTICAL SIGNIFICANCE: NOT CLAIMED
```
