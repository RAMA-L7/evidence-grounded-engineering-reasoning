# EGER-P093 — BENCH2-002 Variability Confirmation Design

| Field | Value |
|---|---|
| ID | EGER-P093-BENCH2-002-VARIABILITY-DESIGN-001 |
| Date | 2026-08-28 |
| Scope | DESIGN ONLY — no execution |
| Status | **DESIGN READY** |

---

## 1. Executive Summary

Design a preregistered 10-run repeated-treatment experiment for BENCH2-002 to determine whether its single RQ-4 success is deterministic or stochastic. BENCH2-002 has a richer initial SDC (287 chars: clock + generated clock + clock groups) compared to BENCH2-001's minimal SDC (51 chars).

---

## 2. Governing Evidence

From P092:
- BENCH2-002 adhered once in RQ-4 (n=1)
- BENCH2-001 showed stochastic adherence (4/10 in P090)
- We cannot determine whether BENCH2-002's success is stable without repeated observations

---

## 3. BENCH2-002 Configuration

### Initial SDC (287 chars, frozen)
```
create_clock -name clk -period 10.0 [get_ports clk]

create_generated_clock -name clk_div2 \
    -source [get_ports clk] \
    -divide_by 2 \
    -master_clock clk \
    [get_pins div_reg/Q]

set_clock_groups -asynchronous \
    -group [get_clocks clk] \
    -group [get_clocks clk_div2]
```

### Task
- Task ID: BENCH2-002
- Objective: "Generate SDC with primary clock and correctly constrained generated clock"
- Design context: "Module top with ports clk, reset, data_in[7:0], data_out[7:0], cfg_reg[3:0]. Primary clock clk at 10ns. Generated clock clk_div2 = clk/2 on div_reg/Q. Asynchronous clock domains."

### Feedback
- Initial errors: SDC-005 (no input_delay), SDC-006 (no output_delay)
- Initial scope: FULL
- Initial CVR: 1.0
- Feedback hash: c3803b9a... (same as BENCH2-001 — same ERROR findings)

---

## 4. Comparison with P090 (BENCH2-001)

| Parameter | BENCH2-001 (P090) | BENCH2-002 (P093) |
|-----------|-------------------|-------------------|
| Initial SDC | 51 chars (clock only) | 287 chars (clock + generated + groups) |
| Initial errors | 2 (SDC-005, SDC-006) | 2 (SDC-005, SDC-006) |
| Initial scope | FULL | FULL |
| Feedback | Same ERROR findings | Same ERROR findings |
| RQ-4 result | Did not adhere | Adhered |
| P090 result | 4/10 adherent | TBD |

**Key question:** Is BENCH2-002's richer initial SDC associated with different adherence behavior?

---

## 5. Experimental Design

### Condition
Single condition: **BENCH2-002 treatment** with:
- Frozen 287-char initial SDC
- Same objective and design context
- Full structured feedback (23 findings)
- MODEL-005 (mimo-v2.5-free)
- Oracle 3b5c2f2
- Metadata eger.design_metadata.v1

### Execution mode
All 10 runs executed sequentially in a single batch using the same script invocation.

### Run count
**N = 10 runs.** Same as P090 for comparability.

### Stopping rule
**All 10 runs are executed regardless of intermediate results.**

---

## 6. Pre-Registered Analysis

### Primary metric
**ERROR adherence:** binary — did the final SDC contain `set_input_delay` AND `set_output_delay`?

### Secondary metrics
- proposal_changed (activation)
- error_delta
- final_evidence_scope
- proposal SDC length
- duration

### Pre-registered analysis plan
1. Count adherent runs: X/10
2. Compute point estimate: X/10
3. Compute 95% Clopper-Pearson CI
4. Compare with P090 BENCH2-001 result (4/10)

### Decision rules
| Outcome | Interpretation |
|---------|---------------|
| 0/10 adherent | BENCH2-002 always fails — different from RQ-4 |
| 1–9/10 adherent | Non-deterministic — similar to BENCH2-001 |
| 10/10 adherent | Deterministic — BENCH2-002 always succeeds |
| Rate significantly different from 40% | Task-dependent adherence |

---

## 7. What This Experiment Can Determine

1. Whether BENCH2-002's single RQ-4 success is deterministic or stochastic
2. Whether BENCH2-002 has a different adherence rate than BENCH2-001
3. Whether the richer initial SDC is associated with different adherence behavior

---

## 8. What This Experiment Cannot Determine

1. Whether the rate generalizes to other models
2. Whether the rate generalizes to other tasks with similar SDC complexity
3. The exact mechanism causing variability
4. Whether BENCH2-001 and BENCH2-002 adherence rates are statistically different (n=10 is insufficient for formal comparison)

---

## 9. Artifact Namespace

```
research/experiments/EGER-EXP-001/formal/DIAGNOSTIC-004/
    ├── RUN_INDEX.json
    ├── manifest-run-001.json ... manifest-run-010.json
    └── raw/
        ├── run-001/
        │   ├── initial_sdc.txt
        │   ├── revised_candidate.json
        │   ├── feedback.json
        │   ├── evidence_initial.json
        │   └── evidence_final.json
        └── ... (10 runs)
```

---

## 10. Call Budget

Per run: 1 model call + 2 Oracle calls = 3 calls
Total: 10 runs × 3 = **30 calls maximum**

---

## 11. Preservation

| Item | Status |
|------|--------|
| P090 DIAGNOSTIC-003 | PRESERVED |
| RQ4-MODEL-005 | PRESERVED |
| All historical artifacts | PRESERVED |

---

## 12. C3 Status

**C3 REMAINS BLOCKED.**

---

## 13. Status

```
P093 COMPLETE
DESIGN READY
NO EXECUTION
ALL PRIOR ARTIFACTS UNTOUCHED
C3: NOT AUTHORIZED
```
