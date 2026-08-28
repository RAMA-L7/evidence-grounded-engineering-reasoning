# EGER-P085 — Repeated Baseline Scientific Review

| Field | Value |
|---|---|
| ID | EGER-P085-REPEATED-BASELINE-SCIENTIFIC-REVIEW-001 |
| Date | 2026-08-28 |
| Status | **SCIENTIFIC REVIEW COMPLETE** |

---

## 1. Executive Summary

Review of 5 independent Condition-A observations (BENCH2-001 with identical inputs). **2/5 achieved ERROR adherence.** The model response is demonstrably variable. However, one confound exists: P074's initial SDC included a comment line not present in P082/P084. The feedback content is identical. The strongest justified claim is that ERROR correction is non-deterministic under these conditions.

**Classification: PARTIALLY SUPPORTED** (for the variability claim)

---

## 2. Five Condition-A Observations

| Source | Initial SDC | Feedback Hash | ERROR Adherence | Error Delta | Proposal Changed |
|--------|------------|---------------|----------------|-------------|-----------------|
| P074 | 97 chars (with comment) | c3803b9a... | ❌ False | 0 | True |
| P082 | 51 chars (bare) | c3803b9a... | ✅ True | -2 | True |
| P084 Run 1 | 51 chars (bare) | c3803b9a... | ✅ True | -2 | True |
| P084 Run 2 | 51 chars (bare) | c3803b9a... | ❌ False | 0 | True |
| P084 Run 3 | 51 chars (bare) | c3803b9a... | ❌ False | 0 | True |

---

## 3. Input Identity Verification

### What was identical
- **Feedback content:** ✅ Same hash (c3803b9a...) across all 5 runs
- **Initial evidence:** ✅ Same scope (FULL), same findings (23), same errors (SDC-005, SDC-006)
- **Task objective:** ✅ "Generate SDC that correctly defines the primary clock on clk"
- **Design context:** ✅ Same module description
- **Model:** ✅ MODEL-005 (mimo-v2.5-free) in all runs
- **Oracle:** ✅ Same revision (3b5c2f2)
- **Metadata:** ✅ Same version (eger.design_metadata.v1)

### What differed
- **Initial SDC:** P074 had a comment line (97 chars); P082/P084 did not (51 chars)
- **Execution context:** P074 ran as part of a 6-task batch; P082 ran as part of a 4-condition batch; P084 ran as standalone

### Impact of the SDC difference
The comment line (`# BENCH2-001: Primary clock definition on clk`) is not an SDC construct. It does not affect Oracle evaluation (same 2 errors detected). However, it is part of the model's input prompt and could theoretically influence the model's interpretation. This is a **minor confound** — the comment is decorative, not functional.

### Impact of execution context
P074 ran in a batch of 6 tasks; P082 in a batch of 4; P084 as standalone. Provider load, caching, and timing could differ. This is an **uncontrolled variable** that could contribute to variability.

---

## 4. Adherence Rate Calculation

### Strict calculation (identical inputs only: P082 + P084)
Runs with 51-char bare SDC: 4 (P082 + P084 × 3)
Adherent: 2 (P082 + P084 Run 1)
Rate: **2/4 = 50%**

### All Condition-A runs (including P074)
Total runs: 5
Adherent: 2
Rate: **2/5 = 40%**

### Conservative claim
With n=4–5, the adherence rate is **between 40% and 50%** with wide uncertainty. We cannot claim a stable probability from this sample.

---

## 5. Proposal Activation vs ERROR Adherence

| Metric | Rate | Interpretation |
|--------|------|---------------|
| Proposal activation | **5/5 = 100%** | Model always changes output with feedback |
| ERROR adherence | **2/5 = 40%** | Model sometimes follows ERROR findings |

**Activation is reliable. Adherence is not.** The model consistently responds to feedback (changes its output) but inconsistently addresses ERROR-level findings.

---

## 6. H4 Assessment

### Claim
"ERROR correction is non-deterministic under identical conditions."

### Evidence for
- 5 independent runs with same inputs: 2 adhered, 3 did not
- All runs produced proposal_changed=True
- No systematic pattern in successes/failures

### Qualifications
1. **n=5 is small** — the true adherence rate could be anywhere from ~15% to ~85% (binomial confidence interval at 95%)
2. **One minor confound** — P074's initial SDC had a comment line
3. **Execution context varied** — batch vs standalone could contribute
4. **Provider-side nondeterminism** — cannot distinguish model variability from provider variability
5. **temperature=0.0 does not guarantee determinism** — the model provider may introduce nondeterminism

### Strongest justified claim
> The model's ERROR correction in response to structured feedback is demonstrably non-deterministic. Under identical task/model/feedback conditions, the model fixed ERROR findings in 2 out of 5 independent runs. This is consistent with model-response variability but does not exclude provider-side or execution-context contributions.

---

## 7. P074 RQ-4 Conclusion Reassessment

### Original P074 conclusion
"3/6 tasks improved under structured feedback"

### Revised interpretation
The P074 result was a **single observation from a stochastic process**. The true adherence rate for each task is unknown from a single run. The 3/6 improvement rate is one sample from a distribution, not a stable measurement.

### What P074 still supports
- Structured feedback **causes** proposal changes (activation)
- In some tasks, proposal changes **include** ERROR reduction
- The effect direction is positive (more improvements than regressions)

### What P074 does NOT support
- That the 3/6 rate is stable or generalizable
- That any specific task will or will not improve under feedback
- That the treatment is deterministic

---

## 8. Provenance and Protocol Audit

| Check | Result |
|-------|--------|
| All 5 runs used MODEL-005 | ✅ |
| All 5 runs used same Oracle | ✅ |
| All 5 runs used same metadata | ✅ |
| Feedback was byte-identical | ✅ Same hash |
| Initial evidence was identical | ✅ Same scope, findings |
| Initial SDC had minor difference | ⚠️ P074 had comment line |
| No code was modified | ✅ |
| No historical artifacts were modified | ✅ |
| No budget violations | ✅ |
| No model substitution | ✅ |

---

## 9. C3 Status

**C3 REMAINS BLOCKED.**

The adherence mechanism is now better characterized (non-deterministic, ~40-50% rate), but:
- We do not understand *why* the model sometimes follows ERROR findings
- We do not know whether the rate is task-dependent or model-dependent
- Epistemic state (C3) presupposes a reliable feedback mechanism

---

## 10. Classification

**PARTIALLY SUPPORTED**

The variability claim is supported: ERROR correction is demonstrably non-deterministic (2/5 adherent). However:
- n=5 is insufficient for a stable probability estimate
- One minor confound exists (comment line in P074 SDC)
- Provider-side vs model-side variability cannot be distinguished
- The true adherence rate has wide uncertainty

---

## 11. Status

```
P085 COMPLETE
SCIENTIFIC REVIEW RECORDED
CLASSIFICATION: PARTIALLY SUPPORTED
VARIABILITY: DEMONSTRATED (2/5)
ACTIVATION: RELIABLE (5/5)
H4: SUPPORTED WITH QUALIFICATIONS
C3: NOT AUTHORIZED
```
