# EGER-P053 — Full-Scope Oracle & Correctness Measurement Design

| Field | Value |
|---|---|
| ID | EGER-P053-FULL-SCOPE-ORACLE-MEASUREMENT-DESIGN-001 |
| Date | 2026-08-27 |
| Scope | SCIENTIFIC DESIGN ANALYSIS ONLY — no implementation |
| Status | **MEASUREMENT DESIGN COMPLETE — AWAITING HUMAN DECISION** |

---

## 1. Executive Verdict

**The Oracle's `NETLIST_REQUIRED` limitation is the primary measurement bottleneck preventing RQ-4 from being answered.** This document designs the minimum scientifically sufficient measurement upgrade: augment benchmark tasks with design metadata (port list, clock definitions) so the Oracle can achieve `FULL` scope and actually validate SDC correctness.

---

## 2. Governing Scientific State

| Item | Status |
|------|--------|
| P051 | FORMAL TREATMENT ACTIVATION OBSERVED; IMPROVEMENT INCONCLUSIVE |
| P052 | MEASUREMENT ADEQUACY: CONDITIONAL — IMPROVE BEFORE C3 |
| RQ-1 | SUPPORTED (EGER can deliver evidence) |
| RQ-2 | SUPPORTED (model can respond to evidence) |
| RQ-3 | SUPPORTED (evidence causes proposal revision) |
| RQ-4 | **INCONCLUSIVE** (correctness measurement inadequate) |
| RQ-5 | OPEN (premature — requires RQ-4 resolution) |
| C2 | COMPLETE — treatment activation established |
| C3 | NOT AUTHORIZED — premature until measurement adequate |

---

## 3. Current Oracle Limitation

### 3.1 Scope Mapping

The Oracle classifies each SDC construct into a scope level:

| Raw Status | Normalized Scope | Can Validate? |
|------------|-----------------|---------------|
| `VALIDATED` | `FULL` | ✅ Yes — construct fully validated |
| `PARTIALLY_VALIDATED` | `PARTIAL` | ⚠️ Partially — some checks possible |
| `NETLIST_REQUIRED` | `INSUFFICIENT` | ❌ No — needs design context |
| `UNSUPPORTED` | `UNSUPPORTED` | ❌ No — construct not supported |

### 3.2 What NETLIST_REQUIRED Means

When the Oracle encounters SDC commands that reference design objects (ports, cells, clocks), it needs to know what those objects are in the actual design. Without this information:

- `create_clock [get_ports clk]` → `NETLIST_REQUIRED` (which port is `clk`?)
- `set_input_delay 5.0 [get_ports data_in]` → `NETLIST_REQUIRED` (does `data_in` exist? what type?)
- `set_false_path -from [get_clocks clk1]` → `NETLIST_REQUIRED` (is `clk1` a real clock?)

### 3.3 What CAN Be Validated Without Netlist

From runtime evidence (`t3_analyze_all.json`), these constructs achieve `FULL` scope:

| Command | Scope | Why |
|---------|-------|-----|
| `set_sdc_version` | FULL | Pure syntax, no design objects |
| `set_units` | FULL | Pure syntax, no design objects |

### 3.4 What CANNOT Be Validated Without Netlist

| Command | Scope | Why |
|---------|-------|-----|
| `create_clock` | NETLIST_REQUIRED | References port objects |
| `set_input_delay` | NETLIST_REQUIRED | References port objects |
| `set_output_delay` | NETLIST_REQUIRED | References port objects |
| `set_clock_uncertainty` | NETLIST_REQUIRED | References clock objects |
| `set_max_transition` | NETLIST_REQUIRED | References net objects |
| `set_max_capacitance` | NETLIST_REQUIRED | References net objects |
| Most constraint commands | NETLIST_REQUIRED | Reference design objects |

**The fundamental problem:** Nearly all meaningful SDC commands reference design objects, so nearly all achieve `INSUFFICIENT` scope without netlist context.

---

## 4. Define "Engineering Correctness" for BENCH-002

### 4.1 Operational Definition

"Engineering correctness" for SDC means:

> The SDC file correctly constrains the timing of the design such that:
> 1. All clocks are properly defined
> 2. All input/output ports have appropriate delay constraints
> 3. Clock relationships are correctly specified
> 4. Timing exceptions are properly applied
> 5. The constraints are consistent with the design's port list, clock structure, and timing requirements

### 4.2 Measurable Dimensions

| Dimension | Measurable? | Oracle Can Check? |
|-----------|-------------|-------------------|
| Required clocks defined | YES | With port list |
| I/O delays specified | YES | With port list + timing info |
| Clock period correct | YES | With clock definition |
| Port references valid | YES | With port list |
| No invalid object references | YES | With port list |
| Constraint consistency | PARTIAL | With design metadata |
| Timing closure | NO | Requires static timing analysis |
| Physical correctness | NO | Requires P&R tools |
| Power correctness | NO | Requires power analysis |

**Key insight:** The Oracle CAN validate most syntactic and structural correctness dimensions if given a port list and clock definitions. It CANNOT validate timing closure or physical correctness (those require external tools).

### 4.3 What We Can Actually Measure

Given a port list and clock definitions, the Oracle can establish:

1. **Port reference validity** — Does `get_ports clk` reference an actual port?
2. **Clock definition correctness** — Is the clock period appropriate? Are all clocks defined?
3. **I/O constraint presence** — Are input/output delays specified for all ports?
4. **Constraint completeness** — Are all required constraints present?
5. **No invalid references** — Does the SDC reference non-existent objects?

This is **structural correctness**, not **timing correctness**. But it is a meaningful, measurable improvement over the current `INSUFFICIENT` scope.

---

## 5. Full-Scope Requirement

### 5.1 Minimum Design Context

To achieve `FULL` scope for BENCH-002 tasks, the Oracle needs:

```
PORTS:
  clk (input, clock)
  reset (input, reset)
  data_in[7:0] (input, data)
  data_out[7:0] (output, data)

CLOCKS:
  clk: period=10ns, port=clk
```

This is **design metadata**, not a netlist. It tells the Oracle:
- What ports exist
- What type each port is (clock, data, reset)
- What clocks are defined
- What the clock period is

### 5.2 What This Enables

With this metadata, the Oracle can:

| Check | Without Metadata | With Metadata |
|-------|-----------------|---------------|
| `create_clock [get_ports clk]` | INSUFFICIENT | FULL |
| `set_input_delay [get_ports data_in]` | INSUFFICIENT | FULL |
| `set_output_delay [get_ports data_out]` | INSUFFICIENT | FULL |
| `set_clock_uncertainty` | INSUFFICIENT | FULL |
| Port reference validity | INSUFFICIENT | FULL |
| Constraint completeness | INSUFFICIENT | FULL |

### 5.3 What This Does NOT Enable

| Check | Why Not |
|-------|---------|
| Timing closure | Requires static timing analysis |
| Physical correctness | Requires P&R tools |
| Power correctness | Requires power analysis |
| Glitch analysis | Requires simulation |
| Clock domain crossing | Requires CDC analysis |

---

## 6. Benchmark Preservation Analysis

### 6.1 Classification

Providing design metadata to the Oracle constitutes:

**B. Addition of auxiliary evaluation context**

This is NOT:
- ❌ A modification of BENCH-002 (the task text/objective/constraints don't change)
- ❌ A new benchmark version (same tasks, same structure)
- ❌ A new evaluation condition (same C2 treatment)

It IS:
- ✅ Additional information provided to the evaluator (Oracle) for correctness measurement
- ✅ Separated from the model's prompt (model does NOT receive this metadata)

### 6.2 Information Boundary

```
ENGINEER/MODEL receives:
  - Task context (design_context, objective, constraints)
  - Structured feedback (EvidenceArtifact findings)

ORACLE receives:
  - Task context
  - Generated SDC candidate
  - Design metadata (ports, clocks) ← NEW, EVALUATOR-ONLY
  - Expected SDC (evaluator_only) ← EXISTING, EVALUATOR-ONLY

DESIGN METADATA is:
  - Available to Oracle for validation
  - NOT available to the model
  - NOT hidden benchmark answers (it's structural info, not the solution)
```

### 6.3 Evaluator Leakage Risk

| Risk | Assessment |
|------|-----------|
| Model sees design metadata | ❌ BLOCKED — not in model prompt |
| Model infers solution from metadata | ⚠️ LOW — metadata describes structure, not solution |
| Metadata reveals evaluator answers | ❌ NO — ports/clocks ≠ correct SDC |
| Metadata enables overfitting | ⚠️ LOW — structural info doesn't tell you what constraints to write |

**Conclusion:** Design metadata is safe to provide to the Oracle without compromising the information boundary.

---

## 7. Oracle Design Options

### Option A: Augment Benchmark Tasks with Design Metadata

**Description:** Add a `design_metadata` field to each BENCH-002 task JSON containing port list and clock definitions. The Oracle uses this for validation; the model never sees it.

| Aspect | Assessment |
|--------|-----------|
| Scientific validity | HIGH — enables FULL scope validation |
| Causal interpretability | HIGH — same treatment, better measurement |
| Reproducibility | HIGH — deterministic metadata, deterministic oracle |
| Implementation complexity | LOW — add field to task JSON, update oracle adapter |
| Provenance impact | LOW — new metadata, existing tasks unchanged |
| Evaluator leakage risk | LOW — metadata is structural, not solution |
| Compatibility with C0/C1/C2 | HIGH — existing artifacts can be re-evaluated |

### Option B: Create Independent Correctness Oracle

**Description:** Build a separate validator that checks SDC against expected constraints.

| Aspect | Assessment |
|--------|-----------|
| Scientific validity | VERY HIGH — direct correctness comparison |
| Causal interpretability | HIGH — clear pass/fail |
| Reproducibility | HIGH — deterministic |
| Implementation complexity | HIGH — new tool, new validation logic |
| Provenance impact | MEDIUM — new validation path |
| Evaluator leakage risk | MEDIUM — must ensure model doesn't see expected SDC |
| Compatibility with C0/C1/C2 | MEDIUM — different validation semantics |

### Option C: Improve Existing Oracle (Extend Ṛta)

**Description:** Modify Ṛta to accept design context directly.

| Aspect | Assessment |
|--------|-----------|
| Scientific validity | HIGH — extends existing proven oracle |
| Causal interpretability | HIGH — same oracle, broader scope |
| Reproducibility | HIGH — deterministic |
| Implementation complexity | MEDIUM — requires Ṛta modification |
| Provenance impact | HIGH — modifies frozen oracle |
| Evaluator leakage risk | LOW |
| Compatibility with C0/C1/C2 | MEDIUM — oracle version change |

### Option D: Repeat C2 with Existing Oracle

**Description:** Re-run C2 without measurement improvement.

| Aspect | Assessment |
|--------|-----------|
| Scientific validity | LOW — same measurement limitation |
| Causal interpretability | LOW — cannot measure correctness |
| Reproducibility | MEDIUM |
| Implementation complexity | LOW |
| Provenance impact | LOW |
| Evaluator leakage risk | LOW |
| Compatibility with C0/C1/C2 | HIGH |

### Option E: Proceed to C3

**Description:** Add epistemic state without measurement improvement.

| Aspect | Assessment |
|--------|-----------|
| Scientific validity | LOW — measurement bottleneck remains |
| Causal interpretability | LOW — cannot measure reasoning quality |
| Reproducibility | MEDIUM |
| Implementation complexity | MEDIUM |
| Provenance impact | MEDIUM |
| Evaluator leakage risk | MEDIUM |
| Compatibility with C0/C1/C2 | MEDIUM |

### Recommendation

**Option A: Augment Benchmark Tasks with Design Metadata**

This is the minimum scientifically sufficient improvement:
- Highest scientific value per implementation cost
- Preserves all existing provenance
- Enables FULL scope validation
- Maintains information boundary
- Can re-evaluate existing C0/C1/C2 artifacts

---

## 8. Causal Design for Future Experiment

### 8.1 Clean Comparison

```
Condition: C2 / MODEL-004
Treatment: structured EvidenceArtifact feedback
Measurement: Oracle with design metadata (FULL scope)

Comparison:
  C0 (baseline) → Oracle with design metadata (FULL scope)
  C2 (treatment) → Oracle with design metadata (FULL scope)

Both use the same Oracle, same metadata, same tasks.
Only the treatment differs.
```

### 8.2 What Changes

| Variable | C0 | C2 |
|----------|----|----|
| Model | MODEL-002/004 | MODEL-004 |
| Treatment | None | Structured feedback |
| Oracle | With metadata | With metadata |
| Measurement | FULL scope | FULL scope |

### 8.3 What Stays Constant

- Benchmark tasks
- Task structure
- Evaluation criteria
- Oracle engine (Ṛta)
- Design metadata
- Information boundary (model doesn't see metadata)

---

## 9. Re-Evaluation of Existing Artifacts

### 9.1 Can Existing C0/C1/C2 Artifacts Be Re-Evaluated?

**YES.** The existing C0, C1, and C2 candidate artifacts (SDC files) can be re-evaluated with the enhanced Oracle (with design metadata) without re-running the model.

This is valuable because:
- It provides a measurement-improved comparison across conditions
- It doesn't require model re-execution
- It preserves all existing provenance
- It directly addresses RQ-4

### 9.2 Re-Evaluation Scope

| Condition | Artifacts Available | Can Re-Evaluate? |
|-----------|--------------------|--------------------| 
| C0 (MODEL-002) | 6 final candidates | YES |
| C1 (MODEL-002) | 6 final candidates | YES |
| C2 canned (MODEL-003) | 6 final candidates | YES |
| C2 formal (MODEL-004) | 4 final candidates | YES |
| C2 exploratory (MODEL-004) | 4 final candidates | YES |

### 9.3 Re-Evaluation Not Re-Execution

**Critical distinction:**
- Re-evaluation = re-run Oracle on existing SDC files (deterministic, fast)
- Re-execution = re-run model to generate new SDC files (nondeterministic, slow)

Re-evaluation is preferred because:
- No model calls needed
- Deterministic results
- Preserves all existing provenance
- Directly answers "does the measurement improvement reveal new information?"

---

## 10. Missing Data Treatment

### 10.1 BENCH2-003 and BENCH2-006

These tasks were MODEL_UNAVAILABLE in the formal C2 run.

### 10.2 Options for Missing Tasks

| Option | Description | Scientific Value |
|--------|-------------|-----------------|
| A | Re-run only the missing tasks | MEDIUM — fills data gaps |
| B | Accept 4/6 as sufficient | LOW — incomplete sample |
| C | Re-run all 6 tasks | HIGH — complete sample, clean comparison |
| D | Re-evaluate only existing artifacts | HIGH — measurement improvement without re-execution |

### 10.3 Recommendation

**Start with Option D (re-evaluate existing artifacts with enhanced Oracle).** If the re-evaluation reveals interesting patterns, then consider Option A or C for missing tasks.

---

## 11. Metrics

### 11.1 Primary Outcome (Pre-Registered)

**Proposal change rate:**
```
proposal_changed = initial_candidate_hash != final_candidate_hash
```
Denominator: completed tasks only (not MODEL_UNAVAILABLE)

### 11.2 Secondary Outcomes (Pre-Registered)

| Metric | Description |
|--------|-------------|
| Oracle evidence scope | FULL / PARTIAL / INSUFFICIENT / UNSUPPORTED |
| Oracle finding count | Number of findings per task |
| Finding resolution | Findings addressed by revision |
| Artifact validity | VALID_ARTIFACT / INVALID_ARTIFACT |
| Correctness rate | % of tasks with FULL scope + no errors |
| Constraint coverage | % of required constraints present |
| Invalid constraint rate | % of constraints referencing non-existent objects |

### 11.3 What These Metrics Can and Cannot Establish

| Metric | Can Establish | Cannot Establish |
|--------|--------------|-----------------|
| proposal_changed | Treatment activation | Engineering improvement |
| evidence scope | Oracle confidence level | Actual correctness |
| finding count | Oracle detection rate | True error rate |
| finding resolution | Feedback conditioning | Correct resolution |
| artifact validity | Oracle assessment | Engineering truth |
| correctness rate | Structural correctness | Timing correctness |

---

## 12. Sample Considerations

### 12.1 Current Sample

n = 6 BENCH-002 tasks (4 completed in formal C2)

### 12.2 Is n=6 Sufficient?

**For treatment activation:** YES — 4/4 activation is strong evidence
**For improvement claims:** NO — too small for reliable effect estimation
**For generalization:** NO — single benchmark, single model

### 12.3 What n=6 Can and Cannot Support

| Claim | Supported? |
|-------|-----------|
| Treatment activation exists | YES |
| Effect size estimation | NO |
| Statistical significance | NO |
| Generalization across models | NO |
| Generalization across benchmarks | NO |

---

## 13. Historical Results

### 13.1 Preserved As-Is

| Condition | Status | Must NOT Change |
|-----------|--------|-----------------|
| C0 | COMPLETE, FROZEN | Artifacts, outcomes, provenance |
| C1 | COMPLETE, FROZEN | Artifacts, outcomes, provenance |
| C2 canned | COMPLETE, FROZEN | Artifacts, outcomes, provenance |
| P048 exploratory | PRESERVED | Artifacts, provenance |
| P050 formal | PRESERVED | Artifacts, provenance |
| P051 scientific review | PRESERVED | Classification, evidence |
| P052 measurement decision | PRESERVED | Recommendation, analysis |

### 13.2 What the Measurement Upgrade Does

- **New evaluation of existing artifacts** — same SDC files, better Oracle
- **New measurement baseline** — future experiments use enhanced Oracle
- **Historical comparison** — C0/C1/C2 with old Oracle vs new Oracle

---

## 14. C3 Gate

### 14.1 Should C3 Be Blocked Until RQ-4 Is Answered?

**YES.** C3 introduces epistemic state (hypothesis/validated/refuted/unknown). The epistemic transitions require the Oracle to establish `VALIDATED` or `REFUTED` — which requires `FULL` scope — which the current Oracle cannot provide.

Without measurement improvement:
- C3's epistemic transitions cannot be reliably measured
- The question "does epistemic state improve reasoning?" cannot be answered
- Adding C3 on top of an incompletely-measured C2 creates a compounding measurement problem

### 14.2 Recommendation

**Block C3 until measurement improvement is implemented and validated.**

---

## 15. Recommended Path

### 15.1 Ranked Options

| Rank | Option | Description | Scientific Value |
|------|--------|-------------|-----------------|
| 1 | **A** | Augment BENCH-002 tasks with design metadata | HIGH |
| 2 | **D** | Re-evaluate existing artifacts with enhanced Oracle | HIGH |
| 3 | **C** | Re-run all 6 C2 tasks with enhanced Oracle | HIGH (if resources allow) |
| 4 | **B** | Build independent correctness oracle | VERY HIGH (long-term) |
| 5 | **E** | Proceed to C3 | LOW (premature) |

### 15.2 Recommended Sequence

```
Step 1: Design design-metadata schema (P053 — THIS DOCUMENT)
    ↓
Step 2: Human approval of measurement upgrade design
    ↓
Step 3: Implement design metadata in BENCH-002 tasks
    ↓
Step 4: Update Oracle adapter to accept design metadata
    ↓
Step 5: Re-evaluate existing C0/C1/C2 artifacts with enhanced Oracle
    ↓
Step 6: Analyze measurement improvement
    ↓
Step 7: If measurement is adequate → consider re-running missing tasks
    ↓
Step 8: If measurement is adequate → consider C3 design
    ↓
Step 9: If measurement is NOT adequate → design further improvements
```

---

## 16. Blocking Issues

| Issue | Status | Impact |
|-------|--------|--------|
| Design metadata schema not defined | THIS DOCUMENT defines it | Blocks implementation |
| Oracle adapter doesn't accept metadata | Needs modification | Blocks FULL scope |
| BENCH-002 tasks don't have metadata | Needs augmentation | Blocks FULL scope |
| Missing tasks (003, 006) | Data gap | Blocks complete analysis |
| Provider rate limiting | Infrastructure | Blocks model re-execution |

---

## 17. Non-Blocking Issues

| Issue | Status | Impact |
|-------|--------|--------|
| MODEL-004 rate limiting | Known limitation | Can work around with existing artifacts |
| UnicodeDecodeError (BENCH2-002) | Non-blocking | Artifact is complete |
| C3 authorization | Not yet needed | Can wait for measurement improvement |

---

## 18. GO/NO-GO

### GO for Implementation

If:
- Design metadata schema is approved
- Oracle adapter modification is approved
- BENCH-002 augmentation is approved
- Information boundary is verified
- Provenance separation is maintained
- Human authorization is granted

### NO-GO if:

- Design metadata leaks to model
- Oracle modification breaks existing provenance
- BENCH-002 tasks are modified (only metadata added)
- C3 is authorized before measurement improvement

---

## 19. Required Artifact

This document:
```
research/implementation/EGER-P053-FULL-SCOPE-ORACLE-MEASUREMENT-DESIGN-001.md
```

---

## 20. Final Status

```
P053 COMPLETE
MEASUREMENT DESIGN: COMPLETE
RECOMMENDATION: Augment BENCH-002 with design metadata
C3: BLOCKED until measurement adequate
NEXT: Human decision on measurement upgrade implementation
TREATMENT ACTIVATION: ESTABLISHED (C2 complete)
CORRECTNESS: INCONCLUSIVE (measurement upgrade designed)
```

---

## 21. Strict Stop

After P053:

STOP.

Do NOT:
- implement design metadata
- modify Oracle adapter
- modify BENCH-002
- modify MODEL-003 or MODEL-004
- execute C2
- execute C3
- commit
- push

The next action must be a human decision on whether to proceed with the measurement upgrade.

END.
