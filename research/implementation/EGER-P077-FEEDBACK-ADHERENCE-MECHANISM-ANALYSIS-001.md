# EGER-P077 — Feedback Adherence Mechanism Analysis

| Field | Value |
|---|---|
| ID | EGER-P077-FEEDBACK-ADHERENCE-MECHANISM-ANALYSIS-001 |
| Date | 2026-08-28 |
| Scope | READ-ONLY analysis of RQ4-MODEL-005 artifacts |
| Status | **ANALYSIS COMPLETE** |

---

## 1. Executive Conclusion

The structured feedback was **byte-identical** (3544 chars) for all error-bearing tasks. The same ERROR findings (SDC-005, SDC-006) were delivered with the same messages. The model's adherence differed:

- **BENCH2-002, 004, 005:** Model directly addressed SDC-005/SDC-006 by adding `set_input_delay` and `set_output_delay`
- **BENCH2-001:** Model addressed informational findings (SDC-100: sdc_version, SDC-101: units, SDC-030: propagated_clock) but **skipped the ERROR findings**

The only difference between the conditions was the **initial SDC text** provided as `existing_sdc` in the prompt. BENCH2-001's initial SDC was a minimal 97-char clock definition. BENCH2-002/004/005 had richer initial SDCs (280–624 chars) with multiple constraint types.

**Conclusion:** The model's feedback adherence is influenced by the initial SDC context. Minimal initial SDC produced narrow revisions that addressed informational but not ERROR findings. Richer initial SDC produced comprehensive revisions that included ERROR fixes.

---

## 2. Task-by-Task Feedback → Response Table

| Task | Feedback (identical) | Initial SDC | Model Followed ERROR? | Model Followed INFO? | Outcome |
|------|---------------------|------------|----------------------|---------------------|---------|
| BENCH2-001 | SDC-005, SDC-006 | 97 chars, clock only | ❌ NO | ✅ YES (SDC-100, 101, 030) | FAILED |
| BENCH2-002 | SDC-005, SDC-006 | 287 chars, clock+generated+groups | ✅ YES | ✅ YES (comprehensive) | IMPROVED |
| BENCH2-004 | SDC-005, SDC-006 | 280 chars, clock+false_path | ✅ YES | ✅ YES (comprehensive) | IMPROVED |
| BENCH2-005 | SDC-005, SDC-006 | 624 chars, clock+I/O+multicycle | ✅ YES | ✅ YES (comprehensive) | IMPROVED |

---

## 3. Successful Adherence Analysis (002, 004, 005)

### BENCH2-002
- Initial: `create_clock` + `create_generated_clock` + `set_clock_groups` (287 chars)
- Feedback: SDC-005 (no input_delay), SDC-006 (no output_delay)
- Response: Added `set_input_delay` (4 variants) + `set_output_delay` (4 variants) + 10 other constructs
- Final: 2692 chars — comprehensive SDC rewrite
- **Directly addressed both ERROR findings**

### BENCH2-004
- Initial: `create_clock` + `set_false_path` (280 chars)
- Feedback: SDC-005, SDC-006
- Response: Added `set_input_delay 2.0` + `set_output_delay 2.0` + clock_transition + clock_uncertainty
- Final: 775 chars
- **Directly addressed both ERROR findings**

### BENCH2-005
- Initial: `create_clock` + `set_multicycle_path` + `set_max_fanout` + `set_max_transition` (624 chars)
- Feedback: SDC-005, SDC-006
- Response: Added `set_input_delay` (2 variants) + `set_output_delay` (2 variants) + many other constructs
- Final: 2252 chars
- **Directly addressed both ERROR findings**

### Common pattern
All three successful tasks had **multiple constraint types** in the initial SDC. The model treated the feedback as a signal to produce a comprehensive, production-quality SDC that addressed all findings.

---

## 4. BENCH2-001 Failure Analysis

### What the model received
- **Design context:** "Generate SDC that correctly defines the primary clock on clk."
- **Existing SDC:** `create_clock -name clk -period 10.0 [get_ports clk]` (97 chars)
- **Objective:** Same as design context
- **Feedback:** SDC-005 (ERROR: no input_delay), SDC-006 (ERROR: no output_delay), SDC-030 (WARNING: no propagated_clock), + 20 INFO findings

### What the model produced
```
set sdc_version 2.2
set_units -time ns -capacitance pF
create_clock -name clk -period 10.0 [get_ports clk]
set_propagated_clock [all_clocks]
```

### What the model addressed
| Finding | Addressed? | How |
|---------|-----------|-----|
| SDC-100 (sdc_version) | ✅ YES | Added `set sdc_version 2.2` |
| SDC-101 (units) | ✅ YES | Added `set_units -time ns -capacitance pF` |
| SDC-030 (propagated_clock) | ✅ YES | Added `set_propagated_clock [all_clocks]` |
| **SDC-005 (input_delay)** | **❌ NO** | **Not addressed** |
| **SDC-006 (output_delay)** | **❌ NO** | **Not addressed** |
| SDC-102–SDC-123 (INFO) | ❌ NO | Not addressed (expected — informational) |

### Interpretation
The model treated BENCH2-001 as a **clock-definition task** and focused on clock-related improvements. It addressed the WARNING finding (propagated_clock) and two informational findings (sdc_version, units) but did not add I/O delay constraints. The task description ("correctly defines the primary clock on clk") may have led the model to interpret I/O delays as outside scope.

---

## 5. Control Comparison

| Task | Control Behavior | Treatment Behavior | Difference |
|------|-----------------|-------------------|------------|
| BENCH2-001 | Identical SDC (no change) | Changed SDC (but no ERROR fix) | Treatment triggered revision but not ERROR adherence |
| BENCH2-002 | Identical SDC (no change) | Comprehensive rewrite with ERROR fixes | Treatment triggered comprehensive revision |
| BENCH2-004 | Identical SDC (no change) | Added I/O delays + clock constraints | Treatment triggered ERROR-specific revision |
| BENCH2-005 | Identical SDC (no change) | Added I/O delays + many constructs | Treatment triggered comprehensive revision |

**Key observation:** Without feedback, the model returned identical SDC in 4/6 tasks. Feedback reliably triggered revision (6/6 changed). But revision quality varied.

---

## 6. Common Mechanism

### Supported by evidence
1. **Feedback triggers revision** — all 6 treatment tasks changed output (100% activation)
2. **Richer initial context → more comprehensive revision** — tasks with multiple constraint types produced full SDC rewrites; the minimal task produced a narrow revision
3. **ERROR findings are addressable** — when the model chose to address them, it succeeded (3/3)
4. **The model can selectively follow findings** — it addressed some findings but not others in the same feedback

### Not supported
- That feedback quality causes the difference (feedback was identical)
- That model capability causes the difference (same model, same temperature)
- That task difficulty causes the difference (BENCH2-001 is arguably simpler)

### Best explanation
The initial SDC acts as a **context anchor**. When the model sees a rich SDC with multiple constraint types, it interprets the feedback as requiring a comprehensive update. When it sees a minimal SDC, it interprets the feedback as requiring targeted improvements within the task's narrow scope.

---

## 7. Alternative Explanations

### Could it be token budget?
BENCH2-001's final SDC is only 226 chars. The model had 2048 max tokens. Token budget was not the constraint.

### Could it be prompt ordering?
The feedback is appended after the task context and initial SDC. The model may weight earlier context more heavily. With a minimal initial SDC, the task description ("primary clock on clk") may dominate.

### Could it be stochastic?
Temperature=0.0 does not guarantee deterministic output across different prompts. But the pattern is consistent across 4 error-bearing tasks — not random.

### Could it be model interpretation?
The model may have interpreted "correctly defines the primary clock" as a scope boundary, treating I/O delays as outside the task. With richer initial SDC, no such scope boundary exists.

---

## 8. Scientific Limitations

| Limitation | Impact |
|------------|--------|
| n=4 error-bearing tasks | Cannot claim this is a universal pattern |
| Single model | May not generalize to other models |
| No raw prompt logs | Cannot verify exact model input |
| Task description confound | Different tasks have different objectives |
| No multi-round test | Cannot verify whether second feedback round would fix 001 |

---

## 9. Recommendation for Next Experiment

1. **Test with uniform initial SDC** — give all tasks the same initial candidate to isolate feedback adherence from initial-context effects
2. **Test with explicit ERROR-only feedback** — reduce the 23-finding feedback to just the 2 ERROR findings to test whether information overload causes the model to skip ERROR findings
3. **Test BENCH2-001 specifically** — rerun with a richer initial SDC to verify the context-anchor hypothesis
4. **Consider multi-round feedback** — would a second round of the same feedback fix BENCH2-001?

---

## 10. Status

```
P077 COMPLETE
READ-ONLY ANALYSIS
NO EXPERIMENTAL STATE MODIFIED
NO CODE CHANGED
NO ARTIFACTS MODIFIED
```
