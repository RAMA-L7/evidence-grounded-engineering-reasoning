# EGER-P078 — RQ-4 Hypothesis Isolation Design

| Field | Value |
|---|---|
| ID | EGER-P078-RQ4-HYPOTHESIS-ISOLATION-DESIGN-001 |
| Date | 2026-08-28 |
| Scope | DESIGN ONLY — no execution |
| Status | **DESIGN COMPLETE** |

---

## 1. Executive Summary

Design a minimal diagnostic experiment to determine why BENCH2-001 ignored ERROR feedback (SDC-005, SDC-006) while BENCH2-002/004/005 followed it. The experiment uses BENCH2-001 as the primary case and varies one factor at a time across 4 conditions.

**Minimum sufficient design: 4 conditions, 1 run each, same MODEL-005.**

---

## 2. Competing Hypotheses

| # | Hypothesis | Mechanism | Testable? |
|---|-----------|-----------|-----------|
| H1 | **Initial-SDC context anchoring** | Minimal SDC → model produces narrow revision | YES — change initial SDC |
| H2 | **Task-objective interpretation** | "Primary clock on clk" → model treats I/O delays as out of scope | YES — change objective wording |
| H3 | **Feedback overload** | 23 findings (2 ERROR + 21 soft) → model skips ERROR findings | YES — reduce feedback |
| H4 | **Model variability** | Stochastic behavior at temperature=0.0 | PARTIALLY — repeat same condition |

---

## 3. Existing Evidence

From P074/P075/P077:

| Task | Initial SDC | Objective | Feedback | ERROR Fixed? |
|------|------------|-----------|----------|-------------|
| BENCH2-001 | 97 chars, clock only | "primary clock on clk" | 23 findings | ❌ NO |
| BENCH2-002 | 287 chars, clock+generated+groups | "primary clock + generated clock" | 23 findings | ✅ YES |
| BENCH2-004 | 280 chars, clock+false_path | "false path without over-constraining" | 23 findings | ✅ YES |
| BENCH2-005 | 624 chars, clock+I/O+multicycle | "multicycle exception" | 18 findings | ✅ YES |

**Critical confound:** In the original RQ-4, initial SDC, task objective, and feedback all changed together across tasks. We cannot determine which factor caused the adherence difference.

---

## 4. Confounds in P077

P077 concluded "richer initial SDC → better adherence" but this is confounded because:

1. **Task objective changed** — BENCH2-001 says "primary clock on clk"; BENCH2-002 says "primary clock + generated clock"
2. **Initial SDC changed** — 97 chars vs 287+ chars
3. **Task constraints changed** — "No other clocks" (001) vs multiple constraint types (002+)
4. **Feedback was identical** — this is the one controlled variable

**P077 cannot distinguish H1 from H2.** The proposed design isolates each factor.

---

## 5. Proposed Conditions

### Condition A — Baseline (replicates BENCH2-001)

| Parameter | Value |
|-----------|-------|
| Task | BENCH2-001 |
| Design context | "Module top with ports clk, reset, data_in[7:0], data_out[7:0]. Single clock domain clk at 10ns. No generated clocks." |
| Objective | "Generate SDC that correctly defines the primary clock on clk." |
| Initial SDC | `create_clock -name clk -period 10.0 [get_ports clk]` (97 chars) |
| Feedback | Full structured feedback (23 findings: 2 ERROR, 1 WARNING, 20 INFO) |
| Model | MODEL-005 (mimo-v2.5-free) |

**Purpose:** Establish baseline adherence for BENCH2-001 under identical conditions to P074.

### Condition B — Richer Initial SDC (tests H1)

| Parameter | Value |
|-----------|-------|
| Task | BENCH2-001 |
| Design context | SAME as A |
| Objective | SAME as A |
| Initial SDC | BENCH2-002's initial SDC (287 chars: clock + generated clock + clock groups) |
| Feedback | SAME as A (23 findings) |
| Model | SAME |

**Variable changed:** Initial SDC only.
**If B fixes errors → H1 supported (context anchoring).**
**If B still fails → H1 weakened.**

### Condition C — Broader Objective (tests H2)

| Parameter | Value |
|-----------|-------|
| Task | BENCH2-001 |
| Design context | SAME as A |
| Objective | "Generate a complete, production-quality SDC for this design. Include all required timing constraints: clock definitions, I/O delays, and any applicable exceptions." |
| Initial SDC | SAME as A (97 chars) |
| Feedback | SAME as A (23 findings) |
| Model | SAME |

**Variable changed:** Objective wording only.
**If C fixes errors → H2 supported (task-scope interpretation).**
**If C still fails → H2 weakened.**

### Condition D — ERROR-Only Feedback (tests H3)

| Parameter | Value |
|-----------|-------|
| Task | BENCH2-001 |
| Design context | SAME as A |
| Objective | SAME as A |
| Initial SDC | SAME as A (97 chars) |
| Feedback | **ERROR-only:** `[{"code": "SDC-005", "severity": "error", "message": "No set_input_delay — all input ports are unconstrained."}, {"code": "SDC-006", "severity": "error", "message": "No set_output_delay — all output ports are unconstrained."}]` |
| Model | SAME |

**Variable changed:** Feedback reduced from 23 to 2 findings.
**If D fixes errors → H3 supported (feedback overload).**
**If D still fails → H3 weakened.**

---

## 6. Independent and Dependent Variables

### Independent Variables (what changes)

| Condition | SDC | Objective | Feedback |
|-----------|-----|-----------|----------|
| A | Original | Original | Full |
| B | **Richer** | Original | Full |
| A | Original | **Broader** | Full |
| A | Original | Original | **ERROR-only** |

### Dependent Variables (what we measure)

| Variable | Definition | Measurement |
|----------|-----------|-------------|
| **ERROR adherence** | Did model add set_input_delay + set_output_delay? | Oracle finding check |
| proposal_changed | Did model change its output? | Hash comparison |
| error_delta | final_error_count - initial_error_count | Oracle |
| constructs_added | What SDC constructs did the model add? | Text diff |
| scope_final | FULL / PARTIAL / INSUFFICIENT | Oracle |

### Primary dependent variable
**ERROR adherence:** binary yes/no — did the final SDC contain `set_input_delay` and `set_output_delay`?

---

## 7. Minimum Sufficient Design

**4 conditions are sufficient** because:

- A vs B isolates H1 (context anchoring)
- A vs C isolates H2 (task-scope interpretation)
- A vs D isolates H3 (feedback overload)
- H4 (variability) is addressed by A replicating the original BENCH2-001 result

**3 conditions would not be sufficient** because:
- Without B, we cannot test H1
- Without C, we cannot test H2
- Without D, we cannot test H3

**5+ conditions are not needed** because the 4 conditions above fully-cross the hypotheses.

---

## 8. Expected Outcomes for Each Hypothesis

### If H1 (context anchoring) is true
| Condition | Expected ERROR adherence |
|-----------|------------------------|
| A (baseline) | ❌ NO |
| B (richer SDC) | ✅ YES |
| C (broader objective) | ❌ NO |
| D (ERROR-only) | ❌ NO |

**Interpretation:** The initial SDC determines revision scope. Richer SDC → comprehensive revision including ERROR fixes.

### If H2 (task-scope interpretation) is true
| Condition | Expected ERROR adherence |
|-----------|------------------------|
| A (baseline) | ❌ NO |
| B (richer SDC) | ❌ NO |
| C (broader objective) | ✅ YES |
| D (ERROR-only) | ❌ NO |

**Interpretation:** The task objective determines what the model considers "in scope." Broader objective → I/O delays become in scope.

### If H3 (feedback overload) is true
| Condition | Expected ERROR adherence |
|-----------|------------------------|
| A (baseline) | ❌ NO |
| B (richer SDC) | ❌ NO |
| C (broader objective) | ❌ NO |
| D (ERROR-only) | ✅ YES |

**Interpretation:** Too many findings cause the model to skip ERROR findings. Focused feedback → ERROR findings get addressed.

### If H4 (variability) is true
| Condition | Expected ERROR adherence |
|-----------|------------------------|
| A (baseline) | sometimes YES, sometimes NO |
| B, C, D | variable |

**Interpretation:** The original failure was stochastic. Would require multiple runs to detect.

### If multiple hypotheses are true
| Pattern | Interpretation |
|---------|---------------|
| B and C both fix errors | Both context anchoring and task-scope contribute |
| B and D both fix errors | Both context anchoring and feedback overload contribute |
| All three fix errors | All factors contribute |
| None fix errors | Unknown mechanism — requires further investigation |

---

## 9. Scientific Decision Rule

After executing A–D:

1. **Count how many conditions fix ERROR findings** (0–4)
2. **If exactly 1 condition fixes errors:** that hypothesis is supported
3. **If 2+ conditions fix errors:** multiple factors contribute — report which ones
4. **If 0 conditions fix errors:** unknown mechanism — the original RQ-4 failure may be model-specific or stochastic
5. **If A (baseline) fixes errors this time:** the original failure was stochastic (H4) — requires repeat runs

**Do not claim certainty from n=1 per condition.** This is a diagnostic exploration, not a confirmatory experiment.

---

## 10. Artifact Namespace and Preservation Plan

### Namespace
```
research/experiments/EGER-EXP-001/formal/DIAGNOSTIC-001/
    ├── RUN_INDEX.json
    ├── A-baseline/
    │   ├── manifest.json
    │   └── raw/
    ├── B-richer-sdc/
    │   ├── manifest.json
    │   └── raw/
    ├── C-broader-objective/
    │   ├── manifest.json
    │   └── raw/
    └── D-error-only-feedback/
        ├── manifest.json
        └── raw/
```

### Preservation
- P074/P075 RQ-4 results: **UNTOUCHED**
- RQ4-MODEL-005 artifacts: **UNTOUCHED**
- BENCH-002: **UNTOUCHED**
- MODEL-005: **FROZEN**
- Oracle: **UNCHANGED**
- Ṛta: **UNTOUCHED**

### Call budget
Per condition: 1 model call + 1 Oracle call = 2 calls
Total: 4 conditions × 2 calls = 8 calls maximum

---

## 11. Recommendation for Implementation

1. **Implement as a lightweight diagnostic script** — not a full runner
2. **Reuse existing Oracle, adapter, and model infrastructure**
3. **Manually construct the 4 prompt variants** (SDC, objective, feedback)
4. **Run all 4 conditions sequentially** (not in parallel)
5. **Record raw SDC output for each condition**
6. **Evaluate each with the same Oracle + metadata**
7. **Compare ERROR adherence across conditions**
8. **Keep total execution under 10 minutes**

---

## 12. Relationship to Existing Evidence

| Document | Relationship |
|----------|-------------|
| P074 RQ-4 execution | Frozen evidence — not modified |
| P075 scientific review | Frozen interpretation — not modified |
| P076 mechanism analysis | Background — this design tests its hypotheses |
| P077 feedback adherence | Background — this design isolates its confounds |
| P078 (this) | New diagnostic design |

**P078 does not modify, override, or reinterpret P074/P075/P077.**

---

## 13. Status

```
P078 COMPLETE
DESIGN ONLY
NO EXECUTION
HISTORICAL RQ-4 EVIDENCE UNCHANGED
```
