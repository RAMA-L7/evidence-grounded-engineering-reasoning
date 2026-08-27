# EGER-P029 — MODEL-003 Selection & Responsiveness Test Design

| Field | Value |
|-------|-------|
| ID | EGER-P029 |
| Date | 2026-08-26 |
| Type | Design and selection plan (read-only) |
| Predecessor | EGER-P028 (Feedback-Responsive Model Design) |
| Status | **FRAMEWORK COMPLETE — HUMAN DECISIONS REQUIRED** |

---

## 1. Executive Summary

This document establishes the controlled process for selecting a candidate feedback-responsive experimental model and validating its suitability before it can become MODEL-003. No model is selected. No tests are executed. The output is a selection framework only.

---

## 2. Scientific Purpose

The purpose of MODEL-003 is NOT:

> "Find the strongest or smartest available model."

The purpose IS:

> "Establish an experimental EngineerModel whose behavior permits causal observation of whether deterministic engineering evidence influences proposal revision."

This distinction must be maintained throughout.

---

## 3. MODEL-002 Historical Status

| Item | Status |
|------|--------|
| MODEL-002 | FROZEN — remains the historical C0/C1 model condition |
| C0 | UNCHANGED — historical baseline preserved |
| C1 | UNCHANGED — identical initial/final outputs preserved |
| No reinterpretation | C0/C1 results are not retroactively reinterpreted |

**MODEL-002 is NOT replaced. Its specification is NOT edited.**

---

## 4. Proposed MODEL-003 Status

```
MODEL-003 = PROPOSED EXPERIMENTAL CONDITION
Status: NOT YET FROZEN
Distinguished from:
  - MODEL-002 (historical)
  - implementation/coding model (current agent)
  - any specific commercial model (not yet evaluated)
```

**No final model identity is selected in this document.**

---

## 5. Candidate Requirements

### Mandatory

| # | Requirement | Why |
|---|-------------|-----|
| 1 | Accept task context | Engineering task input |
| 2 | Accept existing SDC candidate | Revision mechanism |
| 3 | Accept deterministic feedback/evidence | Treatment delivery |
| 4 | Produce SDC in required format | Artifact extraction |
| 5 | Demonstrate meaningful conditioning on feedback | Treatment activation |
| 6 | Preserve task identity | Causal validity |
| 7 | Preserve output format | Schema compliance |
| 8 | Operate without evaluator-only information | Benchmark integrity |
| 9 | Operate without unauthorized tools | Capability control |
| 10 | Operate without hidden subagents | P7 compliance |
| 11 | Stable model identity/version | Reproducibility |
| 12 | EngineerModel-compatible interface | Implementation |
| 13 | Permit information boundary enforcement | Experimental control |

### Preferred

| # | Criterion | Why |
|---|-----------|-----|
| 14 | Strong engineering reasoning | Practical usefulness |
| 15 | Strong code/SDC reasoning | Domain suitability |
| 16 | Large context window | Budget compatibility |
| 17 | Low cost | Operational feasibility |
| 18 | Low latency | Execution efficiency |
| 19 | Deterministic/controllable sampling | Reproducibility |
| 20 | Local execution | Experimental control |
| 21 | Stable API | Reliability |
| 22 | Open-weight availability | Reproducibility |

**Preferred criteria do NOT override mandatory scientific requirements.**

---

## 6. Model Category Analysis

| Category | Example | Responsiveness | Reproducibility | Control | Engineering | Complexity |
|----------|---------|---------------|-----------------|---------|-------------|------------|
| A: Canned/task-mapped | MODEL-002 | ❌ NONE | ✅ PERFECT | ✅ PERFECT | ⚠️ LIMITED | ✅ LOW |
| B: General-purpose LLM | (not selected) | ✅ LIKELY | ⚠️ VARIABLE | ⚠️ DEPENDS | ✅ HIGH | ⚠️ MEDIUM |
| C: Coding/reasoning model | (not selected) | ✅ LIKELY | ⚠️ VARIABLE | ⚠️ DEPENDS | ✅ HIGH | ⚠️ MEDIUM |
| D: Local/open-weight | (not selected) | ✅ POSSIBLE | ✅ POTENTIALLY HIGH | ✅ HIGH | ⚠️ VARIABLE | ⚠️ HIGH |

**No category is pre-selected.** The choice depends on which satisfies all mandatory criteria.

---

## 7. Selection Matrix

| Criterion | Mandatory/Preferred | Why It Matters | Verification Method |
|-----------|--------------------| -------------- |--------------------|
| Feedback conditioning | MANDATORY | Treatment activation | Responsiveness test |
| SDC generation | MANDATORY | Engineering task | Candidate test |
| Revision capability | MANDATORY | C1/C2 mechanism | Revision test |
| Output format compliance | MANDATORY | Artifact extraction | Schema/parser check |
| Task preservation | MANDATORY | Causal validity | Task consistency check |
| Model identity stability | MANDATORY | Reproducibility | Configuration record |
| Information isolation | MANDATORY | Benchmark integrity | Boundary audit |
| Tool isolation | MANDATORY | Capability control | Environment audit |
| Reproducibility | MANDATORY | Scientific repeatability | Controlled repeat test |
| Engineering quality | PREFERRED | Practical usefulness | Separate quality evaluation |
| Cost | PREFERRED | Operational feasibility | Provider/runtime record |
| Latency | PREFERRED | Execution efficiency | Runtime measurement |

**No scores assigned to untested models.**

---

## 8. Responsiveness Test Design

### Purpose

> Determine whether the candidate model can condition its proposal on feedback.

**This is NOT C1.** This is a pre-experiment readiness test.

### Fixed Inputs (held constant)

| Input | Value |
|-------|-------|
| Task context | BENCH2-001 (primary_clocks, easy) |
| Objective | Generate SDC for the given design |
| Initial candidate | `create_clock -name clk -period 10 [get_ports clk]` |
| Model configuration | Candidate MODEL-003 configuration |
| Prompt version | eger.prompt.v1 |

### Variable Input (changes across conditions)

| Condition | Feedback |
|-----------|----------|
| R0 | None (no feedback) |
| R1 | Meaningful error findings |
| R2 | Non-actionable feedback |

### Procedure

```
For each condition (R0, R1, R2):
  1. Construct prompt with fixed inputs + condition-specific feedback
  2. Call model.generate(prompt)
  3. Extract SDC candidate from output
  4. Record: raw output, extracted candidate, candidate hash
  5. Repeat N times for statistical control (if model is stochastic)
```

---

## 9. Control Conditions

### R0 — No-Feedback Control

| Field | Value |
|-------|-------|
| Input | task context + initial candidate |
| Feedback | None |
| Expected | Model produces a proposal without treatment feedback |
| Purpose | Baseline for comparison |

### R1 — Relevant Engineering Feedback

| Field | Value |
|-------|-------|
| Input | task context + initial candidate + error findings |
| Feedback | `ERROR: SDC-005: No set_input_delay. ERROR: SDC-006: No set_output_delay.` |
| Expected | Model addresses the identified issues where technically appropriate |
| Purpose | Tests feedback responsiveness |

### R2 — Non-Actionable Feedback

| Field | Value |
|-------|-------|
| Input | task context + initial candidate + scope limitation |
| Feedback | `Scope: FULL. No findings. All constructs analyzed within scope.` |
| Expected | Model preserves the candidate (no change needed) |
| Purpose | Tests that model does not change output when feedback is non-actionable |

### Distinguishing Controls

| Control pair | What it distinguishes |
|-------------|---------------------|
| R0 vs R1 | Whether feedback changes output |
| R1 vs R2 | Whether change is feedback-conditioned vs random |
| R0 vs R2 | Whether mere presence of feedback text causes change |

---

## 10. Responsiveness Definition

### What Counts as Responsiveness

| Criterion | Assessment |
|-----------|-----------|
| Semantically meaningful | Change reflects engagement with evidence content |
| Technically related | Change addresses the specific feedback |
| Task-consistent | Output remains valid SDC for the same task |
| Format-consistent | Output follows ```sdc format |
| Not formatting noise | Not whitespace, comments, or ordering changes |
| Not arbitrary mutation | Change correlates with feedback content |
| Not unrelated prompt effect | Change is caused by feedback, not other prompt differences |

### Outcome Classification

| Outcome | Criteria |
|---------|----------|
| **PASS** | R1 output ≠ R0 output AND change is semantically related to feedback AND R2 output = R0 output (or minimally different) |
| **FAIL** | R1 output = R0 output (model ignores feedback) |
| **INCONCLUSIVE** | R1 ≠ R0 but change is superficial OR R2 ≠ R0 (model changes output regardless of feedback content) |

---

## 11. Positive/Negative Controls

### Positive Control (R1)

**Setup:** Initial candidate missing `set_input_delay` and `set_output_delay`. Feedback identifies these as errors.

**Expected responsive behavior:** Model adds `set_input_delay` and/or `set_output_delay` constraints.

**Purpose:** Demonstrates that the model can respond to a specific, actionable error finding.

### Negative Control (R2)

**Setup:** Feedback says "No findings. All constructs analyzed."

**Expected responsive behavior:** Model preserves the candidate unchanged.

**Purpose:** Demonstrates that the model does not change output when feedback indicates no action is needed.

### Why Both Are Required

| Without positive control | Without negative control |
|-------------------------|------------------------|
| Cannot confirm model can respond | Cannot confirm model responds to content, not presence |
| Only shows model doesn't change | May PASS due to random variation |

---

## 12. Responsiveness vs Quality

| Dimension | Question | MODEL-003 Requirement |
|-----------|----------|----------------------|
| Responsiveness | Does the model condition on feedback? | MANDATORY — must PASS |
| Engineering quality | Is the resulting SDC correct? | PREFERRED — evaluated separately |

### Possible Combinations

| Responsiveness | Quality | Interpretation |
|---------------|---------|----------------|
| YES | YES | Ideal — responsive and capable |
| YES | NO | Responsive but needs quality improvement — acceptable for treatment testing |
| NO | YES | Non-responsive — CANNOT be used for treatment experiments |
| NO | NO | Neither responsive nor capable — CANNOT be used |

**MODEL-003 requires responsiveness first.** Quality is a separate dimension evaluated under formal experiment conditions.

---

## 13. Randomness Control

### How to Distinguish Feedback-Conditioned Change from Random Variation

| Method | Purpose |
|--------|---------|
| Fixed temperature (0.0) | Minimize sampling variance |
| Fixed prompt | Eliminate prompt-induced variation |
| Fixed model version | Eliminate version-induced variation |
| Fixed task/initial candidate | Eliminate task-induced variation |
| Repeated trials (if stochastic) | Establish variance baseline |
| Semantic comparison | Distinguish meaningful change from noise |

### If Model Is Inherently Stochastic

1. **Document the limitation** — nondeterminism is a known property
2. **Run N repeated trials** — establish how often output varies
3. **Apply semantic comparison** — not byte-identical comparison
4. **Report the variance** — what fraction of runs show feedback-conditioned change?
5. **Classification rule:** PASS requires feedback-conditioned change in >50% of trials (adjustable threshold — OPEN DESIGN QUESTION)

**Do not claim deterministic behavior solely because temperature=0.**

---

## 14. Model Identity Freeze

Before formal experimentation, MODEL-003 must have a complete recorded identity:

| Field | Status |
|-------|--------|
| Provider | OPEN DESIGN QUESTION |
| Model name | OPEN DESIGN QUESTION |
| Model version/snapshot | OPEN DESIGN QUESTION |
| Endpoint/runtime | OPEN DESIGN QUESTION |
| System prompt (if applicable) | OPEN DESIGN QUESTION |
| Experiment prompt | eger.prompt.v1 (frozen) |
| Temperature | 0.0 (proposed) |
| Top_p | 1.0 (proposed) |
| Max tokens | 2048 (proposed) |
| Seed (if applicable) | OPEN DESIGN QUESTION |
| Timeout | 60s (proposed) |
| Tool configuration | EngineerAdapter only (frozen) |
| Context limits | OPEN DESIGN QUESTION |
| Model-call budget | 2 per run (frozen) |

**Unknown fields remain OPEN DESIGN QUESTIONS until resolved.**

---

## 15. Hidden-Capability Audit

Before MODEL-003 is approved, verify:

| Capability | Must NOT Be Present |
|------------|-------------------|
| Uncontrolled tools | Model cannot access tools beyond EngineerAdapter |
| Web access | Model cannot fetch external content during generation |
| Filesystem access | Model cannot read/write files during generation |
| Shell access | Model cannot execute commands during generation |
| Hidden retrieval | Model cannot retrieve information beyond prompt |
| Hidden memory | Model cannot retain state across calls |
| Subagents | Model cannot delegate to other agents |
| Provider-side context | Provider does not inject hidden context |
| System prompts | No hidden system prompts beyond documented ones |
| External knowledge injection | No knowledge injected beyond prompt |

**Any uncontrolled capability that could affect treatment interpretation must be documented.**

---

## 16. Information Boundary

### MODEL-003 May Receive

| Information | Source |
|-------------|--------|
| Task context | BENCH-002 engineer_visible |
| Objective | BENCH-002 engineer_visible |
| Initial candidate | Model call 1 output |
| Text feedback (C1) | Deterministic renderer |
| Structured evidence (C2) | EvidenceArtifact |

### MODEL-003 Must NOT Receive

| Information | Reason |
|-------------|--------|
| Evaluator-only answers | Benchmark integrity |
| Hidden labels | Benchmark integrity |
| C0/C1 results | Information boundary |
| Research ledger | Information boundary |
| Research contract | Information boundary |
| Git history | Information boundary |
| Ṛta source | Oracle boundary |
| Oracle implementation | Oracle boundary |
| Future condition info | Capability matrix |

---

## 17. EngineerModel Compatibility

### Required Interface

```python
class EngineerModel:
    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        ...
```

### Compatibility Requirements

| Requirement | Status |
|-------------|--------|
| Accept prompt string | REQUIRED |
| Return ModelResponse | REQUIRED |
| Preserve raw_output | REQUIRED |
| Support timeout | REQUIRED |
| Support max_tokens | REQUIRED |
| Compatible with EngineerAdapter | REQUIRED |

### If Incompatibilities Exist

| Classification | Meaning |
|---------------|---------|
| BLOCKING | Cannot be used without interface modification |
| NON-BLOCKING | Minor adaptation needed in adapter, not model |
| OPEN DESIGN QUESTION | Requires further analysis |

---

## 18. Change-Control Requirements

### Required Sequence

| Step | Record | Purpose |
|------|--------|---------|
| 1 | Candidate evaluation | Apply selection framework |
| 2 | Responsiveness readiness test | Verify feedback conditioning |
| 3 | EGER-CHANGE-002 | Formal model-condition change control |
| 4 | MODEL-003 specification | Frozen model configuration |
| 5 | EXP-001 v0.3 | Protocol update for new condition |
| 6 | Human authorization | Explicit approval |
| 7 | Formal experiment execution | C1' or C2 with MODEL-003 |

### Does This Require EXP-001 v0.3?

**YES.** The existing protocol specifies MODEL-002. Introducing MODEL-003 is a material change.

---

## 19. Comparability

### What Remains Comparable

| Aspect | Comparable? |
|--------|------------|
| Benchmark (BENCH-002) | ✅ Same tasks |
| Task structure | ✅ Same format |
| Oracle | ✅ Same Ṛta |
| Evaluation | ✅ Same criteria |
| Information boundary | ✅ Same rules |
| Metrics | ✅ Same definitions |

### What Changes

| Aspect | Change |
|--------|--------|
| Model condition | Different model |
| Model behavior | Potentially different outputs |
| Reproducibility characteristics | Depends on model/provider |
| C0/C1 direct comparability | Reduced (different model) |

### Consequence

C0/C1 (MODEL-002) and future conditions (MODEL-003) are **separate experimental conditions**, not direct continuations. Comparison requires explicit justification.

---

## 20. MODEL-003 Condition Structure

### Provenance Relationship

```
MODEL-002 (canned proxy)
  ↓
C0 (1 call, no feedback)
  ↓
C1 (2 calls, feedback delivered, identical candidates)
  ↓
Historical infrastructure findings

MODEL-003 (feedback-responsive)
  ↓
Readiness test
  ↓
Formal change control
  ↓
New experimental condition (C1' or C2)
  ↓
Treatment-effect experiment
```

### Condition Classification

MODEL-003 experiments are:
- **NOT** a replacement for MODEL-002
- **NOT** a continuation of C0/C1
- **YES** a separate experimental condition
- **YES** comparability requires explicit justification

---

## 21. GO/NO-GO Criteria

### GO (ALL required)

| # | Criterion | Verification |
|---|-----------|-------------|
| 1 | Model identity recorded | Configuration document |
| 2 | Interface compatible | EngineerModel test |
| 3 | Information boundary verified | Boundary audit |
| 4 | No evaluator leakage | Leakage test |
| 5 | No uncontrolled tools | Capability audit |
| 6 | Responsiveness test PASS | R1 ≠ R0 AND semantically related |
| 7 | Negative control PASS | R2 ≈ R0 |
| 8 | Task preserved | Task consistency check |
| 9 | Format preserved | Schema compliance check |
| 10 | Reproducibility requirements satisfied | Repeated trial analysis |
| 11 | Change control completed | EGER-CHANGE-### approved |
| 12 | Human authorization granted | Explicit approval |

### NO-GO (ANY blocks)

| # | Criterion |
|---|-----------|
| 1 | Output ignores feedback (R1 = R0) |
| 2 | Only superficial output changes |
| 3 | Response cannot be distinguished from randomness |
| 4 | Evaluator leakage possible |
| 5 | Uncontrolled tools present |
| 6 | Model identity cannot be frozen |
| 7 | Interface incompatibility (BLOCKING) |
| 8 | Reproducibility inadequate |
| 9 | Change control incomplete |
| 10 | Human authorization absent |

### INCONCLUSIVE

Use when evidence is insufficient to distinguish responsiveness from randomness or another explanation.

---

## 22. Selection Procedure

| Step | Action | Document |
|------|--------|----------|
| 1 | Identify candidate models | Candidate list |
| 2 | Record candidate identities | Configuration records |
| 3 | Apply mandatory compatibility checks | Compatibility audit |
| 4 | Apply information-boundary audit | Boundary audit |
| 5 | Apply hidden-capability audit | Capability audit |
| 6 | Run responsiveness readiness test | Test results |
| 7 | Classify PASS / FAIL / INCONCLUSIVE | Classification record |
| 8 | Document results | Results document |
| 9 | Select MODEL-003 only after pre-specified criteria | Selection record |
| 10 | Freeze MODEL-003 | MODEL-003 specification |
| 11 | Complete formal change control | EGER-CHANGE-### |
| 12 | Obtain human authorization | Authorization record |
| 13 | Only then conduct formal treatment experiment | Experiment record |

**No step is performed in this document.**

---

## 23. Scientific Risks

| Risk | Impact | Mitigation | Residual |
|------|--------|-----------|----------|
| Selection bias | Choose model that produces good-looking results | Pre-specified criteria, blind evaluation | Medium |
| Cherry-picking models | Select model that confirms hypothesis | Mandatory criteria applied before results | Low |
| Provider/model drift | Results not reproducible | Version pinning, provider documentation | Medium |
| Hidden prompts | Information boundary violated | Prompt audit, API inspection | Low |
| Hidden tools | Unauthorized capabilities | Environment audit, static verification | Low |
| Nondeterminism | Cannot reproduce results | Temperature=0, semantic comparison, repeats | Medium |
| Feedback overfitting | Model memorizes feedback patterns | Held-out evaluation, diverse feedback | Low |
| Benchmark leakage | Evaluator answers enter prompt | Boundary tests, prompt audit | Low |
| Model capability mismatch | Cannot produce valid SDC | Readiness test, capability verification | Low |
| Excessive model strength | Produces perfect SDC without feedback — treatment invisible | Responsiveness test specifically checks this | Low |
| Cost constraints | Cannot complete experiments | Budget verification, provider documentation | Low |
| Loss of C0 comparability | Cannot compare historical and new results | Document model change, separate conditions | High (accepted) |

---

## 24. Decision Matrix

| Question | MODEL-002 | MODEL-003 Requirement |
|----------|-----------|----------------------|
| Feedback responsive? | Established NO | Must PASS |
| Task responsive? | Task-ID mapping | Must PASS |
| Revision capable? | Established NO | Must PASS |
| C1 treatment identifiable? | NO | Required |
| C2 treatment identifiable? | Likely NO | Must be demonstrated |
| Model identity frozen? | YES | Required |
| Information boundary | YES | Required |
| Oracle isolation | YES | Required |
| Historical comparability | HIGH | MODERATE (separate condition) |
| Experimental suitability | Limited | Must be established |

---

## 25. Human Decisions Required

| # | Decision | Options |
|---|----------|---------|
| 1 | Approve the MODEL-003 selection framework? | YES / NO |
| 2 | Approve the responsiveness readiness test design? | YES / NO |
| 3 | Approve candidate-model evaluation? | YES / NO |
| 4 | Approve initiation of EGER-CHANGE-002 if a new model is selected? | YES / NO |
| 5 | Approve creation of a MODEL-003 specification? | YES / NO |
| 6 | Approve a future responsiveness test execution? | YES / NO |
| 7 | Approve future C2 execution only after MODEL-003 passes readiness? | YES / NO |

**None of these are already approved.**

---

## 26. Exact Next Authorized Step

**Human decision required:**

> Approve the MODEL-003 selection framework and responsiveness test design?

If YES:
→ `EGER-CHANGE-002` — Formal model-condition change control
→ `EGER-P030` — Candidate model evaluation and responsiveness testing

If NO:
→ Document decision and determine alternative path

---

*This selection and test design framework is COMPLETE. No model has been selected. No tests have been executed. Human decisions required before any further action.*
