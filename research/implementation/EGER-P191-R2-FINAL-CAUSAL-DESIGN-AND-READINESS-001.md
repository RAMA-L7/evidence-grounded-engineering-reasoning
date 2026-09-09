# EGER — P191-R2: Final Causal Design & Readiness

> **Status:** DESIGN REVIEW COMPLETE — IMPLEMENTATION-READY (subject to explicit manifest/execution authorization in P191-R3)
>
> **This gate does NOT execute the experiment. No model calls. No raw data generated. No commit. No push.**

## 1. Baseline verified

- **HEAD:** `928d573fe9647eaeb7e1f112f76eebb07a303a23`
- **origin/main:** `928d573fe9647eaeb7e1f112f76eebb07a303a23`
- **HEAD == origin/main:** YES
- **Tracked/staged changes:** none
- **Regression (actual):** EGER **878/878 PASS**; harness **74/74 PASS**
- **Publication baseline:** unchanged (P188 manuscript at `928d573`)

## 2. Research question frozen

> Does task framing causally affect the probability that the model produces a valid, adherent SDC candidate under controlled conditions?

## 3. Outcome freeze

**Primary outcome (binary):**

```
SUCCESS = 1  iff  status == COMPLETED
                 AND has_set_input_delay
                 AND has_set_output_delay
             else 0
```

- `SUCCESS=1` means: a valid, evaluable candidate was produced AND both ERROR findings (missing input delay, missing output delay) were addressed.
- Invalid/incomplete runs → `SUCCESS=0`. No run is excluded from the primary analysis.

**Secondary outcome (ordinal, descriptive):**

```
Y = 2  iff SUCCESS = 1
Y = 1  iff status == COMPLETED, valid candidate, but NOT both delays
Y = 0  otherwise (INCOMPLETE / invalid / non-evaluable)
```

Y is retained for descriptive process analysis only. It is not a second primary outcome.

## 4. Estimand freeze

**Primary estimand (unconditional, per task):**

```
RD_task = P(SUCCESS=1 | assigned A1) - P(SUCCESS=1 | assigned A4)
```

**Primary aggregate estimand:**

```
RD_equal = mean(RD_task over BENCH2-002, BENCH2-004, BENCH2-005)
```

- Equal task weighting is intentional: task is a blocking/effect-modification factor.
- This is the **unconditional causal effect of randomized framing assignment**.
- No conditioning on candidate validity.

## 5. Hypothesis freeze

- **H0:** A1 and A4 have the same SUCCESS probability under the tested conditions.
- **H1:** A1 increases SUCCESS probability relative to A4.

No required effect homogeneity across tasks. Task-level effects are estimated and reported per task; the aggregate is an equal-weighted summary.

## 6. Inference freeze

**Primary descriptive effect:**

- Three task-specific RD estimates
- Exact binomial confidence intervals (Clopper-Pearson, as already implemented in the existing runner's `_clopper_pearson_ci`)

**Primary aggregate inference:**

- Exact blocked randomization/permutation test of `RD_equal`
- Treatment labels permuted only **within each task**
- Preserve exactly 8 A1 + 8 A4 assignments per task
- No common-effect assumption (unlike CMH)

**CMH status:** CMH may remain secondary/exploratory only. It is not the primary analysis.

## 7. Secondary analysis freeze

Retained as explicitly secondary/descriptive:

- Ordinal Y distribution
- Completion probability (P(Y > 0))
- Conditional adherence among valid candidates — explicitly labeled conditional/descriptive, NOT the primary causal result
- Other process descriptors (revised_sdc_length, final_evidence_scope, error_delta, proposal_changed, duration)

No post-treatment variable may adjust the primary analysis.

## 8. Execution protocol freeze

- 3 tasks: BENCH2-002, BENCH2-004, BENCH2-005
- Framing: A1 vs A4 (frozen strings from P126)
- 8 runs per task × condition
- 48 total scheduled runs
- Model: MODEL-005 / `opencode/mimo-v2.5-free`
- Frozen task/framing definitions
- Oracle: Ṛta 1.5.11 @ `3b5c2f2`
- No retries
- No replacement
- No early stopping
- No sample-size extension

## 9. Randomization / manifest freeze

The implementation will create an **immutable pre-execution manifest** containing:

- seed
- task order
- within-task A1/A4 sequence
- run IDs
- model ID
- framing IDs
- initial SDC hashes
- Oracle version
- runner/implementation commit

The manifest must exist **before the first model invocation**. This gate does **not** generate or execute the manifest; that belongs to P191-R3.

## 10. Analysis implementation status

**Concrete implementability:** CONFIRMED.

- The per-run fields needed for SUCCESS (status, has_set_input_delay, has_set_output_delay) are already recorded by the existing runner (`run_e3a_wording_deconfounding.py`).
- The existing runner already implements exact Clopper-Pearson CIs in stdlib (`_clopper_pearson_ci`).
- An exact blocked permutation test is deterministically implementable with stdlib:
  - Per-task exhaustive permutations: C(16, 8) = 12,870 per task (feasible)
  - Combined exact test via convolution of per-task permutation distributions (feasible, deterministic)
- No ambiguity remains about the primary analysis implementation.

## 11. Focused 8-role review

### Role 1 — Research Methodology & Evidence Auditor
- **Finding:** The design now correctly uses an unconditional primary estimand (RD_equal) with a binary SUCCESS outcome defined for every scheduled run. The ordinal Y is correctly relegated to secondary/descriptive. The estimation approach (per-task RD + equal-weighted aggregate + exact blocked permutation) is internally consistent.
- **Verdict:** PASS

### Role 2 — Research Architect
- **Finding:** No disturbance to EGER architecture. Framing is a prompt-level manipulation. Outcome measurement uses the existing frozen runner fields.
- **Verdict:** PASS

### Role 3 — EGER Systems/Software Engineer
- **Finding:** SUCCESS is deterministically computable from existing per-run fields. The inference stack (Clopper-Pearson + exact blocked permutation) is concretely implementable with stdlib. No new runtime measurement is required.
- **Verdict:** PASS

### Role 4 — VLSI / EDA Domain Expert
- **Finding:** SUCCESS captures the engineering-relevant process: produce a usable SDC AND fix the ERROR findings. Encoding invalid/incomplete as SUCCESS=0 is appropriate for a process-level causal claim.
- **Verdict:** PASS

### Role 5 — Experimental Scientist / Statistician
- **Finding:** The conditional adherence estimand issue from P191-S is resolved by the unconditional SUCCESS estimand. The exact blocked permutation test respects the blocked design without imposing a common-effect assumption. Equal task weighting is defensible given task is a blocking/effect-modification factor. H1 no longer requires homogeneity.
- **Concern (resolved):** N=8 per cell is sparse for a three-level ordinal outcome; the binary SUCCESS primary is a reasonable simplification for the pilot.
- **Verdict:** PASS

### Role 6 — Adversarial Reviewer / Red-Team
- **Finding:** The design no longer conditions on candidate validity as the primary estimand. Every scheduled run contributes to the primary outcome (SUCCESS in {0,1}). The primary causal claim is correctly bounded as a process-level effect of framing assignment under the tested conditions.
- **Concern (enforced):** Conditional adherence among valid candidates must remain explicitly secondary and must not be presented as the primary causal result.
- **Verdict:** PASS

### Role 7 — Reproducibility & Provenance Auditor
- **Finding:** The primary outcome is fully reproducible from the frozen apparatus and the immutable manifest. The inference is deterministic given the manifest.
- **Verdict:** PASS

### Role 8 — Release / Git Integrity Officer
- **Finding:** Baseline `928d573`; origin/main in sync; no tracked/staged changes; regression 878/878, 74/74. No experiment executed. No manifest generated. No commit.
- **Verdict:** PASS

## 12. Decision

**CAUSAL IMPLEMENTATION-READY**

The causal design is finalized and concretely implementable. No open methodological issues remain. The only remaining requirement is the explicit manifest creation and pre-execution authorization gate.

**STOP.** Do not execute the 48-run experiment in P191-R2.

**Next gate:**

```
P191-R3 — Final Manifest Creation & Pre-Execution Authorization
```
