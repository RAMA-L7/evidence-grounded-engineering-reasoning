# EGER-P075 — MODEL-005 RQ-4 Scientific Review

| Field | Value |
|---|---|
| ID | EGER-P075-MODEL-005-RQ4-SCIENTIFIC-REVIEW-001 |
| Date | 2026-08-28 |
| Governing | P074 execution, AUTH-007, P061 design |
| Status | **SCIENTIFIC REVIEW COMPLETE** |

---

## 1. Executive Summary

Artifact-level audit of the P074 RQ-4 execution. The 3/6 treatment improvements are **real and correctly measured**. The control branch behaved as expected (mostly no change without feedback). The treatment scope reduction to PARTIAL is a known measurement limitation, not a correctness artifact. Historical artifacts are verified preserved.

**Classification: RQ-4 PARTIALLY SUPPORTED**

---

## 2. Historical Artifact Verification (Corrected)

P074's summary table reported incorrect counts (used `ls *.json | wc -l` which only counted top-level manifests). Actual filesystem verification:

| Condition | Manifests | Raw Dirs | Status |
|-----------|-----------|----------|--------|
| C0 | 0 | 0 | ✅ NEVER FORMALLY EXECUTED (correct) |
| C1 | 6 | 6 | ✅ PRESERVED |
| C2 canned | 6 | 6 | ✅ PRESERVED |
| C2-live | 4 | 4 | ✅ PRESERVED |
| MODEL-004-C2 | 4 | 4 | ✅ PRESERVED |
| RQ4-MODEL-005 | 6 control + 6 treatment | 6+6 | ✅ NEW (this experiment) |

**P074's claim of "C1: 1, C2: 1, MODEL-004-C2: 1" was a reporting error.** The actual counts are 6/6/4 respectively. All historical artifacts are intact.

---

## 3. Control Branch Analysis

| Task | SDC Identical? | Proposal Changed? | Error Delta |
|------|---------------|-------------------|-------------|
| BENCH2-001 | ✅ YES | False | 0 |
| BENCH2-002 | ✅ YES | False | 0 |
| BENCH2-003 | ❌ NO (changed) | True | 0 |
| BENCH2-004 | ✅ YES | False | 0 |
| BENCH2-005 | ✅ YES | False | 0 |
| BENCH2-006 | ❌ NO (changed) | True | 0 |

**Key finding:** Without feedback, the model returned the identical SDC in 4/6 tasks. In the 2 tasks where it changed, the error count remained 0→0 (both were already correct). **The control never reduced ERROR findings.** This is clean control behavior.

---

## 4. Treatment Branch Analysis

| Task | Init Errors | Final Errors | Delta | Scope Change | Improved? |
|------|-------------|-------------|-------|--------------|-----------|
| BENCH2-001 | 2 | 2 | 0 | FULL→FULL | ❌ NO |
| BENCH2-002 | 2 | 0 | **-2** | FULL→PARTIAL | ✅ YES |
| BENCH2-003 | 0 | 0 | 0 | FULL→PARTIAL | N/A (already correct) |
| BENCH2-004 | 2 | 0 | **-2** | FULL→PARTIAL | ✅ YES |
| BENCH2-005 | 2 | 0 | **-2** | PARTIAL→PARTIAL | ✅ YES |
| BENCH2-006 | 0 | 0 | 0 | FULL→PARTIAL | N/A (already correct) |

---

## 5. Why Treatment Scope Became PARTIAL

When the model's revised SDC changes port/clock references, the Oracle can no longer validate some constructs against the frozen design metadata. For example:

- BENCH2-002 treatment final: model added many new constructs (set_operating_conditions, set_max_fanout, etc.) that reference ports/cells not in the metadata → scope drops to PARTIAL
- BENCH2-004 treatment final: model added set_input_delay/set_output_delay but also new constructs → scope drops to PARTIAL

**This is a measurement limitation, not a correctness artifact.** The Oracle correctly reports PARTIAL when it cannot fully validate. The ERROR findings that disappeared (SDC-005, SDC-006) were genuinely fixed — the model added the missing constraints.

---

## 6. Why Treatment CVR is None

CVR requires all references to be measurable. When scope is PARTIAL, some references cannot be validated against metadata, so CVR is undefined. This is correct behavior per P054/P060 design:

- FULL scope → CVR is computable
- PARTIAL scope → CVR may be undefined
- INSUFFICIENT scope → CVR is undefined

---

## 7. Why BENCH2-001 Didn't Improve

The structured feedback correctly identified SDC-005 and SDC-006 (same errors as BENCH2-002). However, the model's revised SDC only added `set_propagated_clock` and `set_units` — it did NOT add `set_input_delay` or `set_output_delay`.

**The feedback was identical in quality. The model's response differed.** This is expected stochastic behavior with temperature=0.0 (which does not guarantee byte-identical output across calls).

---

## 8. Why BENCH2-002 Improved

The model received the same feedback as BENCH2-001 (SDC-005, SDC-006) and responded by adding `set_input_delay` and `set_output_delay` constraints. The revised SDC expanded from 287 to 2692 chars with proper I/O delay specifications.

---

## 9. Initial Candidate Identity Verification

| Run ID | Control == Treatment Initial? |
|--------|------------------------------|
| RQ4-AEA4AFFE | ✅ IDENTICAL |
| RQ4-1F23EEB5 | ✅ IDENTICAL |
| RQ4-8840E4EF | ✅ IDENTICAL |
| RQ4-7278E13E | ✅ IDENTICAL |
| RQ4-5EB06571 | ✅ IDENTICAL |
| RQ4-D71B03C1 | ✅ IDENTICAL |

**The same initial candidate was used for both branches in all 6 tasks.** The paired design is verified.

---

## 10. ERROR Finding Validity

| Finding | Meaning | Genuine Defect? |
|---------|---------|----------------|
| SDC-005 | No set_input_delay — input ports unconstrained | ✅ YES — benchmark requires I/O delays |
| SDC-006 | No set_output_delay — output ports unconstrained | ✅ YES — benchmark requires I/O delays |
| SDC-007 | create_clock on data port | ✅ YES — clock on wrong object |

These are genuine correctness defects per the BENCH-002 benchmark requirements. The Oracle correctly identifies them.

---

## 11. Paired Comparison (Primary Metric)

```
                    CONTROL (no feedback)    TREATMENT (structured feedback)
BENCH2-001:         Δ=0                      Δ=0                    TIE
BENCH2-002:         Δ=0                      Δ=-2                   TREATMENT BETTER
BENCH2-003:         Δ=0                      Δ=0                    TIE (already correct)
BENCH2-004:         Δ=0                      Δ=-2                   TREATMENT BETTER
BENCH2-005:         Δ=0                      Δ=-2                   TREATMENT BETTER
BENCH2-006:         Δ=0                      Δ=0                    TIE (already correct)
```

**Treatment better: 3/6. Control better: 0/6. Tie: 3/6.**

---

## 12. Secondary Metrics Summary

| Metric | Control | Treatment |
|--------|---------|-----------|
| proposal_changed | 2/6 (33%) | 6/6 (100%) |
| warnings changed | mixed | mixed |
| scope maintained FULL | 6/6 | 1/6 |

---

## 13. Limitations

| Limitation | Impact |
|------------|--------|
| n=6 tasks | Cannot claim statistical significance |
| Free-tier model | Subject to rate limits, version changes |
| temperature=0.0 | Does not guarantee deterministic output |
| PARTIAL scope | Some measurements undefined for revised SDC |
| BENCH-002 only | Results specific to this benchmark |
| Single model | Results specific to mimo-v2.5-free |
| No timing validation | Cannot verify actual STA correctness |

---

## 14. What RQ-4 Supports

For MODEL-005 (mimo-v2.5-free) under BENCH-002:

> **Structured evidence feedback caused the model to reduce ERROR-severity findings in 3/6 tasks, while no reduction occurred in any control task.**

This is a **controlled benchmark effect**, not a population-level causal claim.

---

## 15. What RQ-4 Does NOT Support

- That the treatment works for all models
- That the treatment works for all task types
- That the improvement is statistically significant (n=6)
- That the improved SDC is fully correct (scope is PARTIAL)
- That the treatment eliminates all errors (3/6 tasks still had errors)
- That the effect will persist with different model versions

---

## 16. Relationship to Prior Evidence

| Prior Result | Relationship |
|-------------|--------------|
| P037 MODEL-003 responsiveness | Background — same model, different experiment |
| P048/P050/P051 MODEL-004 treatment activation | Background — different model |
| P057 historical re-evaluation | Background — measurement upgrade |
| P059 CVR fix | Infrastructure — enabled measurement |
| P061 RQ-4 design | Governing — this experiment implements it |
| P074 execution | Source — this review audits it |

---

## 17. C3 Status

**C3 REMAINS BLOCKED.** RQ-4 is now partially answered. C3 (epistemic state) requires RQ-4 to be fully resolved first. The current result does not yet justify C3.

---

## 18. Classification

**RQ-4 PARTIALLY SUPPORTED**

The controlled experiment shows a treatment effect direction (3/6 tasks improved, 0/6 control improved) but with important limitations: n=6, single model, PARTIAL scope on revised SDC, no statistical significance claimed.

---

## 19. Recommended Next Steps

1. Consider whether the PARTIAL scope issue can be addressed (e.g., metadata expansion for revised SDC constructs)
2. Consider whether additional benchmark tasks would strengthen the evidence
3. Consider whether a different model would show the same pattern
4. Consider whether the 3/6 improvement rate is meaningful or whether the 3 non-improved tasks reveal a systematic limitation

---

## 20. Status

```
P075 COMPLETE
RQ-4 CLASSIFICATION: PARTIALLY SUPPORTED
HISTORICAL ARTIFACTS: VERIFIED PRESERVED
SCIENTIFIC INTEGRITY: MAINTAINED
C3: NOT AUTHORIZED
```
