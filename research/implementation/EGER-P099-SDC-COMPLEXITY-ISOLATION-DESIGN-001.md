# EGER-P099 — SDC Complexity Isolation Design

| Field | Value |
|---|---|
| ID | EGER-P099-SDC-COMPLEXITY-ISOLATION-DESIGN-001 |
| Date | 2026-08-28 |
| Scope | DESIGN ONLY — no execution |
| Status | **DESIGN READY** |

---

## 1. Executive Summary

Design a 2×2 crossed experiment to isolate whether the BENCH2-001 vs BENCH2-002 adherence difference is caused by initial SDC complexity or task identity/objective. By crossing SDC complexity with task identity, we can determine which factor (if either) drives adherence.

---

## 2. Governing Evidence

From P098:
- BENCH2-001 (51-char SDC, simple objective): 4/10 adherent
- BENCH2-002 (287-char SDC, complex objective): 10/10 adherent
- Confound: SDC complexity and task identity covary

---

## 3. Experimental Design: 2×2 Cross

### Factors

| Factor | Level 1 | Level 2 |
|--------|---------|---------|
| **Initial SDC** | BENCH2-001's 51-char SDC | BENCH2-002's 287-char SDC |
| **Task context** | BENCH2-001 objective/context | BENCH2-002 objective/context |

### Conditions

| Condition | SDC | Task Context | What It Tests |
|-----------|-----|-------------|---------------|
| **W** (baseline) | 51-char (BENCH2-001) | BENCH2-001 | Original BENCH2-001 behavior |
| **X** | 287-char (BENCH2-002) | BENCH2-001 | SDC complexity effect on BENCH2-001 |
| **Y** | 51-char (BENCH2-001) | BENCH2-002 | Task context effect on BENCH2-002 |
| **Z** (baseline) | 287-char (BENCH2-002) | BENCH2-002 | Original BENCH2-002 behavior |

### Key comparisons

| Comparison | Isolates |
|-----------|----------|
| W vs X | SDC complexity effect (same task) |
| Y vs Z | SDC complexity effect (same task) |
| W vs Y | Task context effect (same SDC) |
| X vs Z | Task context effect (same SDC) |

---

## 4. Condition Details

### Condition W — BENCH2-001 baseline
- SDC: `create_clock -name clk -period 10.0 [get_ports clk]` (51 chars)
- Objective: "Generate SDC that correctly defines the primary clock on clk"
- Context: "Module top with ports clk, reset, data_in[7:0], data_out[7:0]. Single clock domain clk at 10ns. No generated clocks."
- **Expected: ~40% adherence** (from P090)

### Condition X — BENCH2-001 with rich SDC
- SDC: BENCH2-002's 287-char SDC (clock + generated + groups)
- Objective: "Generate SDC that correctly defines the primary clock on clk" (BENCH2-001's)
- Context: BENCH2-001's context
- **Key question:** Does richer SDC improve BENCH2-001's adherence?

### Condition Y — BENCH2-002 with minimal SDC
- SDC: `create_clock -name clk -period 10.0 [get_ports clk]` (51 chars)
- Objective: "Generate SDC with primary clock and correctly constrained generated clock" (BENCH2-002's)
- Context: BENCH2-002's context
- **Key question:** Does BENCH2-002's context improve adherence even with minimal SDC?

### Condition Z — BENCH2-002 baseline
- SDC: BENCH2-002's 287-char SDC
- Objective: BENCH2-002's objective
- Context: BENCH2-002's context
- **Expected: ~100% adherence** (from P097)

---

## 5. Hypotheses

### H1 (SDC complexity drives adherence)
**Predicted pattern:**
- W (51-char) → low adherence (~40%)
- X (287-char) → high adherence (~100%)
- Y (51-char) → low adherence (~40%)
- Z (287-char) → high adherence (~100%)

SDC complexity matters; task context does not.

### H2 (Task context drives adherence)
**Predicted pattern:**
- W (BENCH2-001 context) → low adherence (~40%)
- X (BENCH2-001 context) → low adherence (~40%)
- Y (BENCH2-002 context) → high adherence (~100%)
- Z (BENCH2-002 context) → high adherence (~100%)

Task context matters; SDC complexity does not.

### H3 (Both factors contribute)
**Predicted pattern:**
Intermediate adherence in crossed conditions (X and Y).

### H4 (Neither factor explains the difference)
**Predicted pattern:**
No clear pattern — the difference is caused by an unmeasured variable.

---

## 6. Sample Size and Budget

### Per condition
**5 runs** per condition (not 10). Rationale:
- This is a screening experiment, not a definitive measurement
- 5 runs per condition gives 20 total runs
- Enough to detect large effects (e.g., 100% vs 40%)
- Keeps budget manageable

### Total budget
- 20 runs × 3 calls = **60 calls maximum**
- Plus 1 reference evaluation = **61 calls total**

### Why not 10 per condition
- 40 runs would require 120 calls — excessive for a screening experiment
- 5 runs per condition is sufficient to detect the expected large effect
- If results are ambiguous, a follow-up with more runs can be designed

---

## 7. Pre-Registered Analysis

### Primary metric
**ERROR adherence** (binary per run)

### Analysis plan
1. Compute adherence rate per condition: W, X, Y, Z
2. Compute 95% Clopper-Pearson CI per condition
3. Compare W vs X (SDC effect on BENCH2-001)
4. Compare Y vs Z (SDC effect on BENCH2-002)
5. Compare W vs Y (context effect with minimal SDC)
6. Compare X vs Z (context effect with rich SDC)

### Decision rules
| Pattern | Interpretation |
|---------|---------------|
| W<X and Y<Z (SDC helps both tasks) | SDC complexity drives adherence |
| W<Y and X<Z (context helps both SDCs) | Task context drives adherence |
| W<X and W<Y (both help) | Both factors contribute |
| No clear pattern | Unmeasured variable |

---

## 8. Important Limitations

### What this design can establish
- Whether SDC complexity is **associated** with adherence (within task)
- Whether task context is **associated** with adherence (within SDC)
- The crossed design provides stronger evidence than separate experiments

### What this design CANNOT establish
- **Causation** — we are not randomly assigning SDCs to tasks; we are using existing SDCs
- **Mechanism** — we observe adherence, not the reason for it
- **Generalization** — results are specific to MODEL-005 + BENCH-002

### Confound: SDC content vs SDC complexity
The 287-char SDC is not just "more complex" — it has specific constructs (generated clock, clock groups) that are relevant to BENCH2-002's task. Using it with BENCH2-001's objective creates a mismatch that could affect the model's interpretation. This is an inherent limitation of the crossed design.

---

## 9. Artifact Namespace

```
research/experiments/EGER-EXP-001/formal/DIAGNOSTIC-005/
    ├── RUN_INDEX.json
    ├── W-bench2-001-baseline/
    ├── X-bench2-001-rich-sdc/
    ├── Y-bench2-002-minimal-sdc/
    └── Z-bench2-002-baseline/
```

---

## 10. Execution Configuration

| Parameter | Value |
|-----------|-------|
| Model | MODEL-005 (mimo-v2.5-free) |
| Oracle | 3b5c2f2 |
| Metadata | eger.design_metadata.v1 |
| Runs per condition | 5 |
| Total runs | 20 |
| Budget | 61 calls |
| Namespace | DIAGNOSTIC-005/ |

---

## 11. Relationship to Prior Evidence

| Document | Relationship |
|----------|-------------|
| P076/P077 | Background — hypothesized context anchoring |
| P090 | Background — BENCH2-001 baseline (4/10) |
| P097 | Background — BENCH2-002 baseline (10/10) |
| P098 | Governing — identified the confound |
| P099 (this) | New design — isolates SDC from task |

---

## 12. C3 Status

**C3 REMAINS BLOCKED.** This experiment tests a confound, not C3's epistemic-state hypothesis.

---

## 13. Next Implementation Gate

P100 — Implementation → P101 readiness → P102 authorization → P103 execution → P104 scientific review

---

## 14. Status

```
P099 COMPLETE
DESIGN READY
NO EXECUTION
ALL PRIOR ARTIFACTS UNTOUCHED
C3: NOT AUTHORIZED
```
