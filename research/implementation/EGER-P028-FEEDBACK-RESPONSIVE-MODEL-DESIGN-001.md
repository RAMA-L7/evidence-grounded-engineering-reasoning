# EGER-P028 — Feedback-Responsive Model Condition Design & Validation Plan

| Field | Value |
|-------|-------|
| ID | EGER-P028 |
| Date | 2026-08-26 |
| Type | Design and validation plan (read-only) |
| Predecessor | EGER-P027 (C1→C2 readiness) |
| Status | **DESIGN COMPLETE — HUMAN DECISIONS REQUIRED** |

---

## 1. Executive Summary

C1 demonstrated that the EGER pipeline works but the current `LiveEngineerModel` cannot process feedback. This document defines what "feedback responsiveness" means scientifically, proposes a MODEL-003 condition, and specifies the validation requirements before any treatment-effect experiment can proceed.

**The expected result is NOT a model choice. It is a scientifically justified definition and validation plan.**

---

## 2. Scientific Problem

The EGER research question asks: "Can engineering-agent reliability be improved by separating the authorities responsible for proposing engineering hypotheses, establishing deterministic evidence, and authorizing engineering-state transitions?"

To answer this, the experimental EngineerModel must be capable of:
1. Receiving deterministic evidence
2. Processing that evidence
3. Conditioning its proposal on the evidence
4. Producing a measurable change in the output

The current `LiveEngineerModel` fails at step 2 — it selects output based on task ID, not prompt content.

---

## 3. Established C1 Finding

| Finding | Status |
|---------|--------|
| C1 pipeline executes correctly | ✅ VERIFIED |
| Feedback is generated deterministically | ✅ VERIFIED |
| Feedback is delivered to Call 2 | ✅ VERIFIED |
| Initial = final candidates (6/6) | ✅ OBSERVED |
| LiveEngineerModel selects by task ID | ✅ VERIFIED |
| evidence_summary does not affect output | ✅ VERIFIED |
| C1 treatment effect NOT IDENTIFIABLE | ✅ CONCLUDED |
| C1 is valid pipeline/infrastructure result | ✅ CONCLUDED |

---

## 4. Definition of Feedback Responsiveness

### What "Feedback-Responsive" Means Scientifically

An EngineerModel is **feedback-responsive** if and only if:

> Given identical task context and identical initial candidate, the model's second proposal demonstrably conditions on the supplied deterministic evidence in a manner that is:
> 1. **Non-trivial** — the change reflects engagement with the evidence content, not superficial formatting
> 2. **Task-preserved** — the output remains a valid SDC proposal for the same task
> 3. **Format-preserved** — the output follows the required ```sdc format
> 4. **Evidence-conditioned** — the change correlates with the evidence content, not random variation

### What "Feedback-Responsive" Does NOT Mean

- ❌ "Every feedback input produces a different string" — trivial formatting changes are not responsiveness
- ❌ "The model always improves the candidate" — responsiveness is about conditioning, not improvement
- ❌ "The model produces a perfect SDC" — engineering quality is a separate question
- ❌ "The model is the smartest available" — responsiveness is a behavioral property, not a capability ranking

### Why Semantic Responsiveness > String Difference

A model that changes whitespace or adds comments in response to feedback is "responsive" by string comparison but NOT by scientific definition. The change must reflect engagement with the evidence content — e.g., addressing a specific finding, modifying a specific construct, adding a missing constraint.

---

## 5. Proposed MODEL-003

**NON-BINDING DESIGN PROPOSAL**

### Designation

`MODEL-003` — PROPOSED FEEDBACK-RESPONSIVE ENGINEER MODEL

### Proposed Configuration

| Field | Value | Status |
|-------|-------|--------|
| Provider | OPEN DESIGN QUESTION | Must be selected |
| Model identifier | OPEN DESIGN QUESTION | Must be selected |
| Version | OPEN DESIGN QUESTION | Must be frozen |
| Temperature | 0.0 | Per MODEL-002 convention |
| Top_p | 1.0 | Per MODEL-002 convention |
| Max tokens | 2048 | Per MODEL-002 convention |
| Prompt | eger.prompt.v1 | Per PROMPT-001 (frozen) |
| Timeout | 60s | Per MODEL-002 convention |
| Model-call budget | 2 per C1/C2 run | Per EXP-001 v0.2 |
| Tool access | EngineerAdapter only | Per P10/DEC-005 |
| Subagent policy | None | Per DEC-005 |

### Key Difference from MODEL-002

| Property | MODEL-002 | MODEL-003 |
|----------|-----------|-----------|
| Output selection | Task-ID-driven | Prompt-content-driven |
| Feedback processing | None | Required |
| Revision capability | None (identical output) | Required |

### Open Design Questions

| # | Question |
|---|----------|
| 1 | Which provider/model satisfies all mandatory criteria? |
| 2 | How to ensure temperature=0.0 produces reproducible output? |
| 3 | How to handle provider nondeterminism? |
| 4 | What version-pinning strategy is required? |

---

## 6. Responsiveness Readiness Test

### Purpose

> Determine whether the candidate model is capable of conditioning its proposal on supplied feedback.

**This is NOT the EGER treatment experiment.** It is a capability/readiness test.

### Test Design

```
INPUTS:
  task_context = identical across all tests
  initial_candidate = identical across all tests
  feedback_A = no feedback (baseline)
  feedback_B = meaningful deterministic feedback with specific findings

PROCEDURE:
  Test 1: model.generate(task_context + initial_candidate + feedback_A) → output_A
  Test 2: model.generate(task_context + initial_candidate + feedback_B) → output_B

ANALYSIS:
  Compare output_A and output_B
```

### Test Cases

#### Test Case 1: Error Finding Response

| Input | Value |
|-------|-------|
| Task | BENCH2-001 (primary_clocks) |
| Initial candidate | `create_clock -name clk -period 10 [get_ports clk]` |
| Feedback | ERROR: SDC-005: No set_input_delay. ERROR: SDC-006: No set_output_delay. |

**Expected responsive behavior:** Model adds `set_input_delay` and/or `set_output_delay` constraints.

**Expected non-responsive behavior:** Output identical to baseline.

#### Test Case 2: Warning Response

| Input | Value |
|-------|-------|
| Task | BENCH2-001 |
| Initial candidate | `create_clock -name clk -period 10 [get_ports clk]` |
| Feedback | WARNING: SDC-030: No set_propagated_clock. |

**Expected responsive behavior:** Model may add `set_propagated_clock` or similar.

**Expected non-responsive behavior:** Output identical to baseline.

#### Test Case 3: INSUFFICIENT Scope Response

| Input | Value |
|-------|-------|
| Task | BENCH2-003 (io_constraints) |
| Initial candidate | `create_clock -name clk -period 10 [get_ports clk]` |
| Feedback | Scope: INSUFFICIENT. Netlist-dependent checks could not be evaluated. |

**Expected responsive behavior:** Model may acknowledge scope limitation or produce unchanged candidate (both acceptable — INSUFFICIENT is not actionable).

**Expected non-responsive behavior:** Output identical to baseline regardless of feedback.

### Outcome Classification

| Outcome | Criteria |
|---------|----------|
| **PASS** | output_A ≠ output_B AND change reflects evidence content (not formatting) |
| **FAIL** | output_A = output_B (model ignores feedback) |
| **INCONCLUSIVE** | output_A ≠ output_B but change is superficial (formatting, comments, whitespace) |

### Anti-Cheating Criteria

The test must detect:

| Superficial Change | Detection |
|-------------------|-----------|
| Whitespace-only | Strip whitespace, compare |
| Comment-only | Remove comments, compare |
| Ordering-only | Normalize ordering, compare |
| Formatting-only | Parse SDC, compare semantics |
| Random noise | Repeat test, check consistency |

A PASS requires **semantic change** — the SDC content itself must differ in a way that relates to the feedback.

---

## 7. Positive/Negative Controls

### Positive Control

**Setup:**
- Initial candidate: `create_clock -name clk -period 10 [get_ports clk]`
- Feedback: `ERROR: SDC-005: No set_input_delay — all input ports are unconstrained.`

**Expected responsive behavior:** Model adds `set_input_delay` constraint.

**Purpose:** Demonstrates that the model can respond to a specific, actionable error finding.

### Negative Control

**Setup:**
- Initial candidate: `create_clock -name clk -period 10 [get_ports clk]`
- Feedback: `Scope: FULL. No findings. All constructs analyzed.`

**Expected responsive behavior:** Model preserves the candidate (no change needed — FULL scope with no errors).

**Purpose:** Demonstrates that the model does not change output when feedback indicates no action is needed.

### Distinction

| Control | Tests |
|---------|-------|
| Positive | Model can respond to actionable feedback |
| Negative | Model does not change output when feedback is non-actionable |
| Together | Model conditions on feedback content, not just feedback presence |

---

## 8. Reproducibility Requirements

| Requirement | Specification |
|-------------|--------------|
| Temperature | 0.0 (minimize variance) |
| Top_p | 1.0 |
| Seed | If provider supports: frozen. If not: documented limitation. |
| Model version | Frozen (specific version pin) |
| Prompt version | eger.prompt.v1 (frozen) |
| Provider | Frozen |
| Token budget | 2048 (frozen) |
| Timeout | 60s (frozen) |
| Tool access | EngineerAdapter only |
| Environment | Identical across runs |

### Nondeterminism Handling

If the provider does not guarantee deterministic output at temperature=0.0:

1. **Document the limitation** — nondeterminism is a known property
2. **Repeat the readiness test** — multiple runs to establish consistency
3. **Use semantic comparison** — not byte-identical comparison
4. **Report the variance** — how often does the model produce different output for identical input?

**Do not assume deterministic behavior merely because temperature=0.**

---

## 9. Causal Identifiability

### Intended Causal Pathway

```
Feedback treatment
  ↓
Model receives feedback
  ↓
Model conditions proposal on feedback
  ↓
Proposal changes in feedback-relevant manner
  ↓
Oracle outcome changes or remains appropriately unchanged
  ↓
Treatment effect becomes measurable
```

### Link Analysis

| Link | Observability | Instrumentation |
|------|--------------|-----------------|
| Feedback delivered to model | DIRECTLY OBSERVABLE | Prompt hash, evidence_summary parameter |
| Model processes feedback | INDIRECTLY OBSERVABLE | Output comparison (positive/negative controls) |
| Proposal changes | DIRECTLY OBSERVABLE | Candidate hash comparison |
| Change reflects feedback | INDIRECTLY OBSERVABLE | Semantic analysis of change |
| Oracle outcome changes | DIRECTLY OBSERVABLE | Evidence hash comparison |
| Treatment effect measurable | DIRECTLY OBSERVABLE | C0 vs C1/C2 comparison |

### Consequence

If the readiness test PASSes, all links become observable. The causal pathway is identifiable.

If the readiness test FAILs, the pathway is broken at link 2 — model does not process feedback.

---

## 10. C0/C1/Model-003 Provenance

### Historical (MODEL-002)

```
MODEL-002 (canned proxy)
  ↓
C0 (1 call, no feedback)
  ↓
C1 (2 calls, feedback delivered, identical candidates)
  ↓
Historical infrastructure findings
```

### Future (MODEL-003)

```
MODEL-003 (feedback-responsive)
  ↓
Responsiveness readiness test
  ↓
Formal change control (EGER-CHANGE-###)
  ↓
New experimental condition (C1' or C2)
  ↓
Treatment-effect experiment
```

### Relationship

| Aspect | MODEL-002/C0/C1 | MODEL-003/Condition |
|--------|-----------------|-------------------|
| Model | Canned proxy | Responsive LLM |
| Treatment effect | Not identifiable | Identifiable (if readiness passes) |
| Comparability | Historical baseline | New condition |
| Provenance | Preserved | Separate |

**Do not overwrite MODEL-002. Do not alter historical C0/C1 conclusions.**

---

## 11. Change-Control Requirements

### Required Sequence

| Step | Record | Purpose |
|------|--------|---------|
| 1 | EGER-CHANGE-002 | Formal model-condition change control |
| 2 | MODEL-003 specification | Frozen model configuration |
| 3 | EXP-001 v0.3 | Protocol update for new condition |
| 4 | Responsiveness readiness test | Pre-experiment validation |
| 5 | Human authorization | Explicit approval |
| 6 | C1' or C2 execution | Formal experiment |

### Does This Require EXP-001 v0.3?

**YES.** The existing protocol (v0.2) specifies MODEL-002 as the experimental model. Introducing MODEL-003 changes the experimental model, which is a material protocol change requiring a new version.

### What v0.3 Would Change

| Section | Change |
|---------|--------|
| §8 Model Freeze | Add MODEL-003 specification |
| §6 C0–C5 Definitions | Clarify which model runs which condition |
| §27 Known Limitations | Document canned-model limitation and MODEL-003 introduction |
| New §32 | MODEL-003 responsiveness requirements |

---

## 12. Benchmark Integrity

### Requirements

| Requirement | Status |
|-------------|--------|
| Do not inspect evaluator-only answers | ✅ |
| Do not modify BENCH-002 | ✅ |
| Do not modify task membership | ✅ |
| Do not reveal expected solutions | ✅ |
| Do not use tasks as hidden training data | ✅ |

### Readiness Test Benchmark Use

The readiness test uses **synthetic feedback** on existing tasks. It does NOT:
- Run formal BENCH-002 experiments
- Use evaluator-only expected answers
- Modify task definitions
- Expose hidden labels

**Benchmark isolation preserved.**

---

## 13. Information Boundary

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
| Evaluator-only answers | Benchmark isolation |
| Hidden labels | Benchmark isolation |
| Research conclusions | Information boundary |
| C0/C1 results | Information boundary |
| Research ledger | Information boundary |
| Git history | Information boundary |
| Ṛta source | Oracle boundary |
| Oracle implementation | Oracle boundary |
| Epistemic state (unless C3) | Capability matrix |
| Authorization state (unless C5) | Capability matrix |

---

## 14. Oracle Boundary

| Requirement | Status |
|-------------|--------|
| MODEL-003 does not inspect Ṛta directly | ✅ Required |
| MODEL-003 interacts through EGER interfaces only | ✅ Required |
| Oracle remains deterministic evidence authority | ✅ Required |
| Model remains proposal authority | ✅ Required |
| No direct filesystem access to Ṛta | ✅ Required |
| No oracle source inspection | ✅ Required |
| No hidden oracle calls | ✅ Required |
| No generation tools | ✅ Required |
| No subagents | ✅ Required |

---

## 15. Model Selection Criteria

### Mandatory

| # | Criterion | Why |
|---|-----------|-----|
| 1 | Prompt responsiveness | Must process full prompt including evidence |
| 2 | SDC revision capability | Must be able to modify existing SDC |
| 3 | Evidence consumption | Must condition output on supplied feedback |
| 4 | Output format compliance | Must produce ```sdc format |
| 5 | No evaluator access | Must not see expected answers |
| 6 | API/provider stability | Must be available for formal experiments |

### Preferred

| # | Criterion | Why |
|---|-----------|-----|
| 7 | Deterministic output at temp=0 | Reproducibility |
| 8 | Context capacity ≥ 2048 tokens | Budget compatibility |
| 9 | Cost feasibility | Practical constraint |
| 10 | Version pinning | Reproducibility |
| 11 | No hidden system prompts | Information boundary |

---

## 16. Model Category Analysis

| Category | Responsiveness | Reproducibility | Experimental Control | Engineering Suitability | Operational Complexity |
|----------|---------------|-----------------|---------------------|------------------------|----------------------|
| A: Canned proxy | ❌ NONE | ✅ PERFECT | ✅ PERFECT | ⚠️ LIMITED | ✅ LOW |
| B: General-purpose LLM | ✅ LIKELY | ⚠️ VARIABLE | ⚠️ DEPENDS | ✅ HIGH | ⚠️ MEDIUM |
| C: Specialized coding model | ✅ LIKELY | ⚠️ VARIABLE | ⚠️ DEPENDS | ✅ HIGH | ⚠️ MEDIUM |
| D: Local/open-weight | ✅ POSSIBLE | ✅ POTENTIALLY HIGH | ✅ HIGH | ⚠️ VARIABLE | ⚠️ HIGH |

### Assessment

- **Category A** (current): Perfect control but zero responsiveness
- **Category B/C**: Likely responsive but reproducibility and control require careful management
- **Category D**: Potentially most controllable but operational complexity is highest

**The choice depends on which category best satisfies all mandatory criteria.**

---

## 17. Scientific Risk Analysis

| Risk | Impact | Mitigation | Residual |
|------|--------|-----------|----------|
| Model nondeterminism | Cannot reproduce results | Temperature=0, semantic comparison, multiple runs | Medium |
| Provider/version drift | Results not reproducible | Version pinning, provider documentation | Medium |
| Hidden system prompts | Information boundary violated | API inspection, prompt documentation | Low |
| Tool access uncontrolled | Unauthorized capabilities | Static grep, interface verification | Low |
| Context leakage | Evaluator information enters prompt | Boundary tests, prompt audit | Low |
| Feedback overfitting | Model memorizes feedback patterns | Held-out evaluation, diverse feedback | Low |
| Prompt sensitivity | Small prompt changes cause large output changes | Prompt freeze, version pinning | Medium |
| C0/C1 comparability loss | Cannot compare historical and new results | Document model change explicitly, separate conditions | High (accepted) |
| Cost/rate limits | Cannot complete formal experiments | Budget verification, provider documentation | Low |
| Model capability insufficient | Cannot produce valid SDC | Readiness test, capability verification | Low |

---

## 18. Model Quality vs Responsiveness

### Critical Distinction

> A stronger model is not automatically a better experimental model.

The requirement is NOT:
> "Choose the smartest model."

The requirement IS:
> "Choose a model whose behavior allows the treatment mechanism to be causally observed and measured under controlled conditions."

### Why This Matters

- A very strong model might produce perfect SDC without any feedback — treatment effect invisible
- A weaker model might produce poor SDC but respond meaningfully to feedback — treatment effect visible
- The experimental question is about **whether evidence changes proposals**, not about **whether the model is good at SDC generation**

### Selection Implication

Model selection should prioritize:
1. **Responsiveness** — can the model condition on feedback?
2. **Control** — can the model's behavior be reproduced?
3. **Suitability** — can the model produce valid SDC?
4. **Not** raw capability or benchmark scores

---

## 19. Decision Matrix

| Criterion | MODEL-002 | MODEL-003 (Proposed) |
|-----------|-----------|---------------------|
| Task responsiveness | ✅ Task-ID-driven | ✅ REQUIRED (prompt-content-driven) |
| Feedback responsiveness | ❌ NONE | ✅ REQUIRED |
| Revision capability | ❌ NONE (identical output) | ✅ REQUIRED |
| Determinism | ✅ PERFECT (canned) | ⚠️ DEPENDS on provider |
| Reproducibility | ✅ PERFECT | ⚠️ REQUIRES version pinning |
| Experimental control | ✅ PERFECT | ⚠️ REQUIRES careful management |
| Treatment identifiability | ❌ NOT POSSIBLE | ✅ REQUIRED (readiness test) |
| C0 comparability | ✅ SAME MODEL | ⚠️ DIFFERENT MODEL |
| C1 comparability | ✅ SAME MODEL | ⚠️ DIFFERENT MODEL |
| Engineering suitability | ⚠️ LIMITED (canned) | ✅ REQUIRED |
| Main limitation | Cannot process feedback | Nondeterminism, reproducibility |

---

## 20. GO/NO-GO Gate

### GO Conditions (ALL required)

| # | Condition | Verification |
|---|-----------|-------------|
| 1 | Readiness test PASS | Semantic output change correlates with feedback |
| 2 | Information boundary verified | No evaluator leakage |
| 3 | Model identity frozen | Provider, model, version documented |
| 4 | Configuration recorded | Temperature, top_p, tokens, timeout frozen |
| 5 | No evaluator leakage | Prompt audit, boundary test |
| 6 | Reproducibility established | Multiple runs, semantic comparison |
| 7 | Formal change control approved | EGER-CHANGE-### approved |
| 8 | Human authorization granted | Explicit approval |

### NO-GO Conditions (ANY blocks)

| # | Condition | Evidence |
|---|-----------|----------|
| 1 | Output ignores feedback | Readiness test FAIL |
| 2 | Feedback response is random variation | Inconclusive readiness test |
| 3 | Hidden tools/context uncontrolled | Prompt audit failure |
| 4 | Model identity/version cannot be frozen | Provider limitation |
| 5 | Evaluator leakage possible | Boundary test failure |
| 6 | Reproducibility cannot be established | High variance at temp=0 |
| 7 | Change control incomplete | Missing authorization |
| 8 | Human authorization denied | Explicit rejection |

---

## 21. Future Experiment Path

### If MODEL-003 Passes Readiness

```
MODEL-003 readiness test PASS
  ↓
EGER-CHANGE-002 (formal change control)
  ↓
MODEL-003 specification (frozen)
  ↓
EXP-001 v0.3 (protocol update)
  ↓
Human authorization
  ↓
C1' (feedback-assisted revision with responsive model)
  ↓
C2 (structured evidence with responsive model)
  ↓
C3 (epistemic state with responsive model)
  ↓
C4 (routing with responsive model)
  ↓
C5 (authorization with responsive model)
```

### If MODEL-003 Fails Readiness

```
MODEL-003 readiness test FAIL
  ↓
Evaluate alternative models (Category B/C/D)
  ↓
Or: accept canned-model limitations and proceed with infrastructure-only findings
  ↓
Human decision required
```

### Each Condition Requires Separate Verification

C1' would need its own:
- Readiness verification
- Execution authorization
- Scientific review

The same applies to C2, C3, C4, C5.

---

## 22. Human Decisions Required

| # | Decision | Options |
|---|----------|---------|
| 1 | Accept MODEL-003 as a proposed condition? | YES / NO |
| 2 | Approve responsiveness readiness testing? | YES / NO |
| 3 | Approve formal change-control initiation? | YES / NO |
| 4 | Approve a specific model specification? | (requires model selection first) |
| 5 | Approve EXP-001 v0.3? | YES / NO |
| 6 | Approve future C1'/C2 execution only after readiness passes? | YES / NO |

**None of these are already approved.**

---

## 23. Exact Next Authorized Step

**Human decision required:**

> Should EGER proceed with MODEL-003 design and responsiveness readiness testing?

If YES:
→ `EGER-CHANGE-002` — Formal model-condition change control
→ `EGER-P029` — Model selection and responsiveness readiness testing

If NO:
→ Document decision and determine alternative path

---

*This design and validation plan is COMPLETE. No model has been selected. No tests have been executed. Human decisions required before any further action.*
