# EGER-P114 — Base-Rate Stabilization Experiment Design

## Objective

Establish a more reliable baseline ERROR-adherence rate for **BENCH2-001 + minimal SDC** before performing cross-task replication of the E3a broader-objective effect.

### Motivation

The observed baseline varies substantially:

| Experiment | Adherent | Rate | 95% CI |
|------------|----------|------|--------|
| P090 (DIAGNOSTIC-003) | 4/10 | 40% | [12.6%, 72.9%] |
| P112 Base (DIAGNOSTIC-006) | 8/10 | 80% | [45.8%, 100.0%] |

Without a stable baseline, all condition comparisons (including E3a) are uncertain.

---

## Frozen Experimental Inputs

Identical to DIAGNOSTIC-006 Base condition:

| Parameter | Value |
|-----------|-------|
| Task | BENCH2-001 |
| Initial SDC | `create_clock -name clk -period 10.0 [get_ports clk]` (51 chars) |
| Design context | `Module top with ports clk, reset, data_in[7:0], data_out[7:0]. Single clock domain clk at 10ns. No generated clocks.` |
| Objective | `Generate SDC that correctly defines the primary clock on clk` |
| Feedback mode | `full` (structured EvidenceArtifact from Oracle) |
| Model | `opencode/mimo-v2.5-free` (MODEL-005) |
| Temperature | 0.0 |
| Tools | [] |
| Max tokens | 2048 |
| Timeout | 60s |
| Oracle | EGER EvidenceOracle (existing) |
| Metadata | eger.design_metadata.v1 (existing) |

---

## Experiment Design

**20 sequential identical runs.**

Each run uses the exact same:
- task representation
- initial SDC
- design context
- objective
- Oracle initial evaluation → structured feedback
- model call with feedback
- Oracle final evaluation

### Namespace

`formal/DIAGNOSTIC-007/`

### Run Budget

| Resource | Per Run | Total (20 runs) |
|----------|---------|-----------------|
| Oracle initial | 1 | 20 |
| Model call | 1 | 20 |
| Oracle final | 1 | 20 |
| **Total** | **3** | **60** |

---

## Primary Metric

**ERROR adherence** (binary per run):

```
adherent = (final_error_count < initial_error_count)
```

Where ERROR count counts only findings with `severity == "error"`.

### Pre-Registered Summary Statistics

1. Adherence count: `k / n` where `n = completed runs`
2. Adherence proportion: `k / n`
3. 95% Clopper-Pearson confidence interval
4. Descriptive comparison against:
   - P090: 4/10 = 40%
   - DIAGNOSTIC-006 Base: 8/10 = 80%

---

## Secondary Metrics (recorded, not primary)

- proposal_activation (binary)
- initial_error_count
- final_error_count
- error_delta
- initial_evidence_scope
- final_evidence_scope
- revised_sdc_length
- has_set_input_delay
- has_set_output_delay
- feedback_hash
- duration_seconds
- provider_status

---

## Failure Handling (Pre-Registered)

| Failure Type | Handling |
|-------------|----------|
| Provider timeout | Record INCOMPLETE, do not retry |
| Model returns empty | Record INCOMPLETE, do not retry |
| Oracle failure | Record INCOMPLETE_MEASUREMENT, do not retry |
| Model substitution | **FORBIDDEN** — record as protocol violation |
| Retry beyond budget | **FORBIDDEN** — record as protocol violation |
| Canned/fallback output | **FORBIDDEN** — record as protocol violation |

Incomplete runs are reported separately. They are **not excluded** from the record, but they are **not counted** as adherent or non-adherent.

---

## Statistical Analysis (Pre-Registered)

### Primary Analysis

1. Count completed runs: `n`
2. Count adherent runs: `k`
3. Compute proportion: `p = k / n`
4. Compute 95% Clopper-Pearson CI: `[lo, hi]`

### Descriptive Comparison

Compare the P114 CI against:
- P090 point estimate: 40% (CI: [12.6%, 72.9%])
- DIAGNOSTIC-006 Base point estimate: 80% (CI: [45.8%, 100.0%])

### What We Will NOT Do

- Claim that the CI establishes the "true" long-run probability
- Use non-overlapping CIs as a hypothesis test
- Exclude incomplete runs post-hoc
- Change the metric after seeing results
- Claim statistical significance at any alpha level
- Generalize beyond MODEL-005 + BENCH2-001

### Interpretation Framework

| CI Range | Interpretation |
|----------|---------------|
| CI entirely above 60% | Baseline likely high; E3a 100% less distinguishable |
| CI contains 50% | Baseline uncertain; E3a comparison ambiguous |
| CI entirely below 60% | Baseline likely low; E3a 100% would be a strong contrast |
| CI very wide (>50pp) | Insufficient data; more runs needed |

---

## Scientific Question

> **How stable is ERROR adherence for the BENCH2-001 minimal-SDC Base condition under repeated identical trials?**

This experiment should NOT attempt to prove:
- Model randomness
- Provider randomness
- A causal effect of SDC complexity
- A causal effect of task framing
- Epistemic uncertainty
- C3 effectiveness

---

## Relationship to Previous Experiments

| Experiment | Runs | Adherent | Rate |
|------------|------|----------|------|
| P090 | 10 | 4 | 40% |
| P112 Base | 10 | 8 | 80% |
| **P114** | **20** | **TBD** | **TBD** |

P114 combines with P090 and P112 Base to give a total of 40 Base observations for BENCH2-001 (though execution contexts may differ).

---

## Limitations

1. **Execution-context confound unresolved** — P090 and P112 used different API keys/times; P114 may also differ
2. **n=20 still modest** — CI will remain wide
3. **One task, one model** — results may not generalize
4. **Provider/model version drift** — the model may change between experiments
5. **Cannot separate model stochasticity from provider effects**

---

## Implementation Prerequisite

This is a design-only document. Implementation requires:
1. A batch runner (similar to DIAGNOSTIC-006)
2. Deterministic unit tests
3. Change-control record
4. Readiness review
5. Execution authorization

---

## Deliverables (Design Phase Only)

1. `EGER-P114-BASE-RATE-STABILIZATION-DESIGN-001.md` (this document)
2. `EGER-CHANGE-014.md` (if required by protocol)

No runner, no tests, no execution, no authorization.

---

```
P114 COMPLETE
DESIGN ONLY
NO EXECUTION
NO LIVE MODEL CALLS
HISTORICAL ARTIFACTS UNCHANGED
C3: NOT AUTHORIZED
```
