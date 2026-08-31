# EGER-P119 — DIAGNOSTIC-007 Scientific Review

## Classification: **PARTIALLY SUPPORTED**

---

## 1. Dataset Verification

| Metric | Value |
|--------|-------|
| Attempted | 20 |
| Completed | 18 |
| Incomplete (provider timeout) | 2 (Base-run07, Base-run08) |
| Adherent | 7/18 |
| Non-adherent | 11/18 |
| Activated | 18/18 (100% of completed) |

The 2 incomplete runs are provider failures, not adherence observations.

---

## 2. Primary Result

```
Adherence: 7/18 = 38.9% ≈ 39%
95% Clopper-Pearson CI: [17.8%, 63.4%]
```

The CI is wide, reflecting the modest sample size. The interval includes 40% and 50% but excludes 80%.

---

## 3. Activation vs Adherence

| Metric | Rate | Note |
|--------|------|------|
| Proposal activation | 18/18 (100%) | Among completed runs |
| ERROR adherence | 7/18 (39%) | Among completed runs |

The model **always revised** its proposal when it responded. But only 39% of revisions addressed the ERROR findings. This confirms the DIAGNOSTIC-006 pattern: activation is reliable, adherence is not.

---

## 4. Historical Comparison

| Experiment | Completed | Adherent | Rate | 95% CI |
|------------|-----------|----------|------|--------|
| P090 | 10 | 4 | 40% | [12.6%, 72.9%] |
| DIAGNOSTIC-006 Base | 10 | 8 | 80% | [45.8%, 100.0%] |
| **DIAGNOSTIC-007** | **18** | **7** | **39%** | **[17.8%, 63.4%]** |

### Pooled Descriptive (Not Exchangeable)

| Combined | Adherent | Total | Rate |
|----------|----------|-------|------|
| P090 + DG-006 + DG-007 | 19 | 38 | 50% |

This pooling is **descriptive only**. The experiments occurred in different execution contexts and may not be exchangeable.

---

## 5. Key Observation: SDC Length Correlation

| Experiment | Adherent Mean SDC | Non-Adherent Mean SDC | Ratio |
|------------|------------------|----------------------|-------|
| DIAGNOSTIC-006 Base | 786 chars | 179 chars | 4.4x |
| DIAGNOSTIC-007 | 1,272 chars | 271 chars | 4.7x |

**Consistent pattern:** Adherent runs produce ~4.5x longer revised SDCs. Non-adherent runs produce short revisions that don't address I/O delays.

This correlation is stable across experiments but is an **association, not a causal claim**. We cannot say "making the SDC longer causes adherence."

---

## 6. The DIAGNOSTIC-006 Outlier

DIAGNOSTIC-006 Base produced 8/10 = 80%, while P090 (40%) and DIAGNOSTIC-007 (39%) are much lower.

### Possible Explanations (Unresolved)

1. **Provider state at time of execution** — the model/provider may have been in a different state during DIAGNOSTIC-006
2. **Execution context** — different API key, session, timing
3. **Sampling variation** — n=10 is small; 8/10 could occur from a ~50% true rate
4. **Model version drift** — the model may have been updated between experiments
5. **Uncontrolled factor** — something else changed between execution sessions

### What This Means

DIAGNOSTIC-006 is **not proven erroneous**, but it is **inconsistent** with the other two Base observations. The most conservative interpretation is that the Base rate is **not a single stable value** — it varies across execution contexts.

---

## 7. Base-Rate Stability Assessment

**Has the Base-rate stabilization experiment established a stable adherence rate?**

**No.** The evidence shows:

- Two experiments produce ~40% (P090, DIAGNOSTIC-007)
- One experiment produces 80% (DIAGNOSTIC-006)
- The CI for DIAGNOSTIC-007 [17.8%, 63.4%] is wide
- Execution-context variability remains unresolved

The strongest defensible conclusion is:

> **ERROR adherence under the Base condition is empirically variable, with repeated experiments producing rates ranging from ~40% to ~80%. The underlying source of this variability is unresolved.**

---

## 8. H4 Assessment

| Claim | Status |
|-------|--------|
| Repeated runs produce different outcomes | **ESTABLISHED** |
| The variability is model-side | Not established |
| The variability is provider-side | Not established |
| The variability is execution-context | Plausible but unproven |
| The exact adherence rate is known | Not established |

**H4 is rephrased as:**

> ERROR-adherence behavior is empirically variable across repeated executions under nominally identical conditions. The source of variability (model, provider, or execution context) cannot be determined from the current evidence.

---

## 9. RQ-4 Implications

| Finding | Status |
|---------|--------|
| Structured feedback causes proposal revision | **STRONGLY SUPPORTED** (100% activation across all experiments) |
| ERROR adherence is task-dependent | **SUPPORTED** (DIAGNOSTIC-006 E3a = 100%, Base ≈ 40-50%) |
| ERROR adherence is variable | **ESTABLISHED** (repeated experiments produce different rates) |
| Task framing improves adherence | **SUPPORTED SIGNAL** (E3a = 10/10 in DIAGNOSTIC-006) |
| Feedback overload reduces adherence | **SUPPORTED SIGNAL** (E4a = 4/9 in DIAGNOSTIC-006) |
| The exact Base rate is known | **NOT ESTABLISHED** |
| The causal mechanism is known | **NOT ESTABLISHED** |

---

## 10. C3 Assessment

| Requirement | Status |
|-------------|--------|
| Evidence of model epistemic uncertainty | None |
| Evidence that uncertainty causes adherence failures | None |
| Evidence that epistemic-state intervention would help | None |
| Evidence that the mechanism is model-internal | None |

```
C3: NOT JUSTIFIED
```

The evidence points to prompt design (task framing, feedback completeness) and execution-context variability, not epistemic uncertainty.

---

## 11. Research-Direction Assessment

DIAGNOSTIC-007 has achieved its purpose: **the Base rate is now characterized as variable (~40-80%), with two experiments converging near 40%.**

The remaining uncertainty is:
1. Why DIAGNOSTIC-006 produced 80% (execution-context question)
2. Whether the E3a broader-objective effect replicates across tasks
3. What causes the model to produce thorough vs minimal revisions

### Recommended Next Step

**Cross-task E3a replication** (Direction B from P114). Now that the Base rate is characterized (~40-50%), testing whether E3a's 10/10 effect replicates on BENCH2-002/004/005 would be the most informative next experiment.

Another Base-rate experiment is **not recommended** — three experiments already provide sufficient evidence that the rate is variable.

---

## 12. Limitations

1. **n=18** — modest sample, wide CI
2. **2 provider failures** — cannot be counted as adherence observations
3. **Execution-context confound** — DIAGNOSTIC-006 vs P090/DIAGNOSTIC-007 discrepancy unresolved
4. **One task, one model** — results may not generalize
5. **Cannot distinguish model vs provider variability**
6. **SDC length correlation is associative, not causal**

---

## 13. Strongest Defensible Conclusion

> Under the Base condition (BENCH2-001 + minimal SDC + full feedback + MODEL-005), ERROR adherence is empirically variable. Two experiments produce approximately 40% adherence, while one produced 80%. The combined evidence across three experiments suggests a Base rate in the range of 40-50%, but with substantial execution-to-execution variability. The source of this variability remains unresolved. Proposal activation is nearly universal (100% among completed runs), confirming that the model reliably responds to feedback even when it does not follow ERROR findings.

---

```
P119 COMPLETE
DIAGNOSTIC-007 SCIENTIFIC REVIEW COMPLETE
BASE-RATE VARIABILITY CONFIRMED
EXACT BASE RATE NOT ESTABLISHED (~40-50% range)
MODEL-SIDE VS PROVIDER-SIDE VARIABILITY UNRESOLVED
SDC LENGTH CORRELATION CONSISTENT ACROSS EXPERIMENTS
C3: NOT JUSTIFIED
NEXT RESEARCH GATE: Cross-task E3a replication (BENCH2-002/004/005)
```
