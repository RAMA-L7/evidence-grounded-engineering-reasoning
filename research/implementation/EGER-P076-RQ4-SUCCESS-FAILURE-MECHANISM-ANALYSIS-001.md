# EGER-P076 — RQ-4 Success/Failure Mechanism Analysis

| Field | Value |
|---|---|
| ID | EGER-P076-RQ4-SUCCESS-FAILURE-MECHANISM-ANALYSIS-001 |
| Date | 2026-08-28 |
| Scope | READ-ONLY analysis of RQ4-MODEL-005 artifacts |
| Status | **ANALYSIS COMPLETE** |

---

## 1. Executive Conclusion

Treatment success depended on **whether the model's revised SDC actually added `set_input_delay` and `set_output_delay`** when told to. The feedback was identical in quality across tasks (same SDC-005/SDC-006 errors). The difference was in the **model's response behavior**:

- **Success (002, 004, 005):** Model expanded SDC significantly, adding I/O delay constraints
- **Failure (001):** Model added minor improvements (sdc_version, units, propagated_clock) but **did not address the ERROR findings**
- **Ties (003, 006):** Already had zero ERROR findings; nothing to fix

The pattern suggests the model's response is influenced by the **initial SDC's structural complexity** — richer initial context produced more comprehensive revisions.

---

## 2. Task-by-Task Evidence Table

| Task | Initial SDC | Feedback Errors | Model Response | I/O Delays Added? | Delta Error |
|------|------------|----------------|----------------|-------------------|-------------|
| BENCH2-001 | 97 chars: clock only | SDC-005, SDC-006 | +sdc_version, +units, +propagated_clock | ❌ NO | 0 (no improve) |
| BENCH2-002 | 287 chars: clock + generated + groups | SDC-005, SDC-006 | +sdc_version, +units, +I/O delays, +operating_conditions, +fanout, +transition, +capacitance | ✅ YES | **-2 (improved)** |
| BENCH2-003 | 293 chars: clock + I/O delays | 0 errors (already correct) | Expanded but kept I/O delays | N/A (already had) | 0 (tie) |
| BENCH2-004 | 280 chars: clock + false_path | SDC-005, SDC-006 | +sdc_version, +units, +I/O delays, +clock_transition, +clock_uncertainty | ✅ YES | **-2 (improved)** |
| BENCH2-005 | 624 chars: clock + I/O + multicycle | SDC-005, SDC-006 (initial scope PARTIAL) | +sdc_version, +units, +I/O delays (confirmed) | ✅ YES | **-2 (improved)** |
| BENCH2-006 | 268 chars: clock + I/O + data port check | 0 errors (already correct) | Expanded but kept correctness | N/A (already had) | 0 (tie) |

---

## 3. Successful Treatment Analysis (002, 004, 005)

### What they had in common
- Initial SDC contained **multiple constraint types** (clock + something else)
- Feedback identified SDC-005 and SDC-006
- Model **directly addressed** the feedback by adding `set_input_delay` and `set_output_delay`
- Model also added many other constructs (sdc_version, units, operating_conditions, etc.)

### BENCH2-002 (most dramatic improvement)
- Initial: 287 chars → Final: 2692 chars (9.4x expansion)
- Added: set_input_delay, set_output_delay, set_operating_conditions, set_max_fanout, set_max_transition, set_max_capacitance, set_max_area
- The model treated the feedback as a prompt to do a comprehensive SDC rewrite

### BENCH2-004
- Initial: 280 chars → Final: 775 chars (2.8x expansion)
- Added: set_input_delay, set_output_delay, set_clock_transition, set_clock_uncertainty
- Preserved the original false_path constraint

### BENCH2-005
- Initial: 624 chars → Final: 2252 chars (3.6x expansion)
- Initial scope was already PARTIAL; treatment maintained PARTIAL
- Added I/O delays that were missing from the initial candidate

---

## 4. Failed Treatment Analysis (001)

### What happened
- Initial SDC: only `create_clock -name clk -period 10.0 [get_ports clk]` (97 chars)
- Feedback: SDC-005 (no set_input_delay), SDC-006 (no set_output_delay)
- Final SDC: added sdc_version, units, propagated_clock (226 chars)
- **Model did NOT add set_input_delay or set_output_delay**

### Why it failed
The model addressed **some** feedback findings but not the ERROR-level ones:
- ✅ SDC-100 (sdc_version) → fixed
- ✅ SDC-101 (units) → fixed
- ✅ SDC-030 (propagated_clock) → fixed
- ❌ SDC-005 (input_delay) → NOT addressed
- ❌ SDC-006 (output_delay) → NOT addressed

### Possible explanation
BENCH2-001's task description is "Generate SDC that correctly defines the primary clock on clk." The model may have interpreted this as a clock-only task and focused on clock-related improvements, treating I/O delays as outside the task scope. With a richer initial SDC (002, 004, 005), the model treated the feedback as a comprehensive correctness signal.

---

## 5. Tie-Task Analysis (003, 006)

### BENCH2-003
- Initial: 293 chars with set_input_delay and set_output_delay already present
- Feedback: 0 ERROR findings (already correct)
- Final: 740 chars (expanded but no errors to fix)
- **Genuine tie: no improvement possible**

### BENCH2-006
- Initial: 268 chars with set_input_delay and set_output_delay already present
- Feedback: 0 ERROR findings (already correct)
- Final: 876 chars (expanded but no errors to fix)
- **Genuine tie: no improvement possible**

---

## 6. Feedback → Revision Trace

### Same feedback, different outcomes

| Task | Feedback (ERROR) | Model Added | Outcome |
|------|-----------------|-------------|---------|
| 001 | SDC-005, SDC-006 | sdc_version, units, propagated_clock | ❌ Missed errors |
| 002 | SDC-005, SDC-006 | sdc_version, units, I/O delays, +10 more | ✅ Fixed errors |
| 004 | SDC-005, SDC-006 | sdc_version, units, I/O delays, clock_transition | ✅ Fixed errors |
| 005 | SDC-005, SDC-006 | sdc_version, units, I/O delays (confirmed) | ✅ Fixed errors |

### Control branch (no feedback)

| Task | Model Behavior | Outcome |
|------|---------------|---------|
| 001 | Returned identical SDC | No change |
| 002 | Returned identical SDC | No change |
| 003 | Changed SDC (no error reduction) | No improvement |
| 004 | Returned identical SDC | No change |
| 005 | Returned identical SDC | No change |
| 006 | Changed SDC (no error reduction) | No improvement |

---

## 7. Scope/CVR Limitations

### Why scope dropped to PARTIAL
When the model's revised SDC introduces constructs that reference ports/cells not in the frozen metadata, the Oracle cannot fully validate. For example:
- BENCH2-002 treatment: model added `set_operating_conditions -library <lib_name>` → references unknown library
- BENCH2-004 treatment: model added `set_clock_transition`, `set_clock_uncertainty` → constructs beyond basic metadata

### Why CVR is None for PARTIAL scope
CVR requires all references to be measurable. When scope is PARTIAL, some references are unmeasurable → CVR is undefined per P054 design.

### Impact on interpretation
The scope reduction does NOT mean the treatment made things worse. It means the model's revised SDC is more complex than the metadata can fully validate. The ERROR findings that disappeared (SDC-005, SDC-006) were genuinely fixed — the model added the missing constraints.

---

## 8. Common Patterns

### Pattern 1: Feedback triggers expansion
In all 6 treatment tasks, the model expanded the SDC (proposal_changed=True). The control branch had only 2/6 changes. **Feedback reliably triggers revision.**

### Pattern 2: Richer initial context → better response
Tasks with multiple constraint types in the initial SDC (002, 004, 005) produced comprehensive revisions. The task with only a clock definition (001) produced a narrow revision.

### Pattern 3: ERROR findings are addressable
When the model chose to address SDC-005/SDC-006, it succeeded (3/3 cases). The failure on 001 was not about inability but about response scope.

### Pattern 4: Control behavior is stable
4/6 control tasks returned identical SDC. The model rarely changes its output without feedback. This confirms the control is clean.

---

## 9. Alternative Explanations

### Could the improvement be noise?
Unlikely for 002/004/005: the model explicitly added `set_input_delay` and `set_output_delay` — specific constructs that directly address the feedback. This is not random variation.

### Could the failure on 001 be model limitation?
Possible: the model may have limited "revision budget" per call and chose to address simpler findings first. But with temperature=0.0, this is not stochastic — it's a consistent response pattern for this task.

### Could the PARTIAL scope mask additional errors?
Yes: the Oracle cannot validate all constructs in revised SDC. Some errors may be hidden. But the primary metric (ERROR-severity delta) is based on what the Oracle CAN measure.

---

## 10. Scientific Conclusion

### What the evidence shows

1. **Structured feedback causes the model to revise its SDC** (6/6 treatment vs 2/6 control)
2. **In 3/6 tasks, the revision specifically addressed ERROR findings** (added set_input_delay, set_output_delay)
3. **In 1/6 tasks, the revision addressed minor findings but not ERROR findings**
4. **In 2/6 tasks, no improvement was possible** (already correct)
5. **The control never reduced ERROR findings** (0/6)

### What this means for RQ-4

> Structured evidence feedback **caused** the model to reduce ERROR-severity findings in 3/6 tasks, while no reduction occurred in any control task. The effect is task-dependent: richer initial context produced more comprehensive corrections.

### Limitations of this conclusion

- n=6 (no statistical significance)
- Single model (mimo-v2.5-free)
- PARTIAL scope on revised SDC
- Cannot verify actual STA correctness
- Results specific to BENCH-002

---

## 11. Recommendation for Next Experiment

1. **Investigate why BENCH2-001 failed** — is it task description, initial SDC complexity, or model limitation?
2. **Consider metadata expansion** for constructs introduced by treatment (to reduce PARTIAL scope)
3. **Consider additional tasks** to increase n beyond 6
4. **Consider testing with a different model** to verify the pattern generalizes
5. **Consider multi-round feedback** — would a second round fix BENCH2-001?

---

## 12. Status

```
P076 COMPLETE
READ-ONLY ANALYSIS
NO EXPERIMENTAL STATE MODIFIED
NO CODE CHANGED
NO ARTIFACTS MODIFIED
```
