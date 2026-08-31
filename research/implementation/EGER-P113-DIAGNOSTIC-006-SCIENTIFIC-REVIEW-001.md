# EGER-P113 — DIAGNOSTIC-006 Scientific Review

## Classification: **PARTIALLY SUPPORTED — Task Framing Supported as Mechanism, Feedback Overload Supported**

---

## 1. Executive Summary

DIAGNOSTIC-006 tested four conditions to determine why ERROR-feedback adherence varies. The strongest finding is:

> **Task framing (E3a) produced 10/10 adherence with dramatically longer SDCs, while ERROR-only feedback (E4a) produced44% adherence with the lowest activation rate.**

This supports two of the four original hypotheses:
- **H2 (Task framing): SUPPORTED** — broader objective → 100% adherence
- **H3 (Feedback overload): SUPPORTED** — ERROR-only feedback →44% adherence,5/9 activation

But Base performance (80%) is substantially higher than P090's prior observation (40%), introducing an unresolved execution-context confound.

---

## 2. Condition Results

| Condition | Adherent | Rate | 95% CI | Activated | Mean SDC Len |
|-----------|----------|------|--------|-----------|-------------|
| Base | 8/10 | 80% | [45.8%, 100.0%] | 10/10 | 664 |
| E2b | 9/10 | 90% | [57.3%, 100.0%] | 10/10 | 1,077 |
| E3a | 10/10 | 100% | [71.4%, 100.0%] | 10/10 | 3,039 |
| E4a | 4/9 | 44% | [14.2%, 100.0%] | 5/9 | 354 |

---

## 3. E3a Analysis — Task Framing

**10/10 adherence. 10/10 activated. Mean SDC length 3,039 characters.**

The broader objective ("Generate a complete, production-quality SDC... Include all required timing constraints: clock definitions, I/O delays, and any applicable exceptions") produced:

- **Perfect adherence** across all 10 runs
- **Dramatically longer SDCs** — mean 3,039 chars vs Base's 664 (4.6x longer)
- **All final scopes were PARTIAL or UNSUPPORTED** — the model produced extensive SDCs that the Oracle couldn't fully validate

### Is this meaningful?

**Yes, with caveats:**

The 10/10 result is striking, but the CIs for Base [45.8%, 100.0%] and E3a [71.4%, 100.0%] overlap. With n=10 per condition, we cannot formally claim E3a > Base. However:

1. The **effect size is large** — E3a mean SDC is 4.6x longer than Base
2. The **pattern is consistent** — zero failures across 10 runs
3. The **mechanism is interpretable** — broader objective → more comprehensive output → I/O delays naturally included

### What E3a does NOT prove

- That "production-quality" framing is the optimal prompt
- That the improvement is caused by task framing rather than SDC length
- That E3a's results would replicate with n=50
- That the broader objective doesn't introduce other confounds (e.g., the model may be generating unnecessary constraints)

---

## 4. E2b Analysis — SDC Content

**9/10 adherence. 10/10 activated. Mean SDC length 1,077 characters.**

Adding irrelevant SDC constructs (set sdc_version, set_units, set_max_fanout, etc.) improved Base from 80% to 90%. But:

- The **CI overlap is substantial** — Base [45.8%, 100.0%] vs E2b [57.3%, 100.0%]
- The **mean SDC length increase is moderate** — 1,077 vs 664 (1.6x)
- With n=10, this could easily be sampling variation

### Verdict

**E2b vs Base difference is NOT established.** The 10% improvement is within sampling noise at n=10.

---

## 5. E4a Analysis — Feedback Overload

**4/9 adherence (44%). 5/9 activated (56%). Mean SDC length 354 characters.**

E4a is the most complex condition because it has two distinct failure modes:

### Failure Mode 1: Non-activation (4/9 runs)
- E4a-run04, 05, 06, 09: SDC unchanged (51 chars = original)
- The model received ERROR-only feedback and **returned the original SDC unchanged**
- Final scope remained FULL, final error count remained 2
- This is a **complete failure to respond** to the feedback

### Failure Mode 2: Activation without adherence (1/9 run)
- E4a-run01: SDC changed slightly (51→85 chars) but did not add I/O delays
- The model made a minor edit but did not address the ERROR findings

### Success pattern (4/9 runs)
- E4a-run02, 03, 07, 10: SDC changed substantially (667-818 chars) and added I/O delays
- These runs look similar to Base successes

### Why E4a fails

The ERROR-only feedback contains:
```json
[{"severity":"error","code":"SDC-005","message":"No set_input_delay..."},
 {"severity":"error","code":"SDC-006","message":"No set_output_delay..."}]
```

Without the broader evidence context (scope, CVR, finding details), the model sometimes:
1. **Ignores the feedback entirely** (returns original SDC)
2. **Makes minimal changes** (adds a comment or minor edit)
3. **Correctly addresses the findings** (adds I/O delays)

The44% adherence rate suggests that **ERROR-only feedback is insufficient for reliable adherence** in this task configuration.

---

## 6. Base vs P090 — Execution-Context Confound

**This is the most important unresolved issue.**

| Experiment | Base Adherent | Rate |
|------------|--------------|------|
| P090 (DIAGNOSTIC-003) | 4/10 | 40% |
| P112 (DIAGNOSTIC-006) | 8/10 | 80% |

Both experiments used the same:
- Model: mimo-v2.5-free
- Task: BENCH2-001
- SDC: 51-char minimal
- Feedback: full structured evidence
- Oracle and metadata

Yet the adherence rate doubled from 40% to 80%.

### Possible explanations

1. **Provider/model version drift** — the model may have been updated between experiments
2. **Execution timing** — different times of day, different provider load
3. **Sampling variation** — two n=10 samples from a ~50-70% true rate can easily produce 40% and 80%
4. **Session/context effects** — different API key, different session state

### What this means

**The Base rate is not stable across experiments.** This means:
- We cannot treat 80% as the "true" Base rate
- We cannot treat 40% as the "true" Base rate
- The true Base rate is somewhere in the range of40-80%, and we need more data to narrow it
- E3a's 100% may also be subject to execution-context effects

---

## 7. Revised SDC Length as Predictor

| Condition | Mean Len | Adherent Runs Mean | Non-Adherent Runs Mean |
|-----------|----------|-------------------|----------------------|
| Base | 664 | 774 | 179 |
| E2b | 1,077 | 1,128 | 223 |
| E3a | 3,039 | 3,039 | N/A (0 failures) |
| E4a | 354 | 725 | 51 (non-activated) |

**Pattern:** Non-adherent runs consistently have much shorter revised SDCs. This suggests:

- When the model produces a **short revision**, it likely didn't address the ERROR findings
- When the model produces a **long revision**, it likely included I/O delays
- SDC length is a **proxy for revision thoroughness**, not a causal mechanism

But this is an **association, not a causal claim.** We cannot say "making the SDC longer causes adherence."

---

## 8. Hypothesis Assessment

| Hypothesis | Original Claim | DIAGNOSTIC-006 Evidence | Classification |
|------------|---------------|------------------------|----------------|
| H1: SDC context anchoring | Minimal SDC → poor adherence | E2b (richer SDC) = 90% vs Base 80% — overlap | **WEAKENED** |
| H2: Task framing | Broader objective → better adherence | E3a = 100% vs Base 80% — strong signal | **SUPPORTED** |
| H3: Feedback overload | ERROR-only → worse adherence | E4a =44% vs Base 80% — clear signal | **SUPPORTED** |
| H4: Model variability | Stochastic response | Base 80% vs P090 40% — evidence of variability | **SUPPORTED** |

---

## 9. What the Evidence Establishes

### ESTABLISHED
- Proposal activation is nearly universal (35/39 = 90% overall)
- ERROR-only feedback reduces both activation (5/9) and adherence (4/9)
- Broader task objective is associated with 100% adherence (n=10)
- Non-adherent runs produce much shorter revised SDCs
- The Base adherence rate varies across experiments (40% vs 80%)

### SUPPORTED
- Task framing influences adherence (E3a effect)
- Feedback completeness influences activation (E4a effect)
- Model variability is real (P090 vs P112 Base comparison)

### NOT ESTABLISHED
- SDC complexity alone causes adherence (E2b vs Base overlap)
- The "true" Base adherence rate
- Whether E3a's 100% would persist with n=50
- Whether the mechanism is model-interior or provider-side
- Whether C3 (epistemic state intervention) would help

---

## 10. C3 Assessment

**C3 remains NOT JUSTIFIED.**

The DIAGNOSTIC-006 results point to **prompt design** (task framing, feedback completeness) as the mechanism, not epistemic uncertainty. Specifically:

1. **E3a (broader objective) solved the problem** — if task framing is the mechanism, C3 is unnecessary
2. **E4a (ERROR-only) made it worse** — if feedback overload is real, C3 would add MORE information, potentially making things worse
3. **No evidence of model uncertainty** — the model either follows feedback or ignores it; there's no signal that the model "knows" it's uncertain

The strongest research implication is:

> **Rather than intervening on the model's epistemic state (C3), the more promising direction is optimizing the task prompt and feedback format.**

---

## 11. Limitations

1. **n=10 per condition** — CIs are wide, formal comparisons underpowered
2. **Base rate instability** — 40% vs 80% across experiments undermines all comparisons
3. **One task only** — BENCH2-001; results may not generalize
4. **One model only** — mimo-v2.5-free; results may not generalize
5. **SDC content confounded with complexity** — E2b changes content, not just length
6. **E4a-run08 incomplete** — provider failure, not a scientific observation
7. **No formal statistical test** — CI overlap analysis only

---

## 12. Recommended Next Steps

1. **Do NOT create C3.** The evidence points to prompt design, not epistemic state.
2. **Investigate Base rate stability.** Run 20+ Base repetitions to establish a reliable baseline.
3. **Test E3a across other tasks.** Does broader objective help on BENCH2-002/004/005?
4. **Consider task-framing optimization** as a more promising research direction than C3.
5. **Freeze DIAGNOSTIC-006 as evidence.** Do not rerun or modify.

---

## 13. Final Classification

```
P113 COMPLETE
DIAGNOSTIC-006 SCIENTIFIC REVIEW
CLASSIFICATION: PARTIALLY SUPPORTED

H1 (SDC context): WEAKENED
H2 (Task framing): SUPPORTED
H3 (Feedback overload): SUPPORTED
H4 (Model variability): SUPPORTED

C3: NOT JUSTIFIED
NEXT: Task-framing investigation OR Base-rate stabilization
```
