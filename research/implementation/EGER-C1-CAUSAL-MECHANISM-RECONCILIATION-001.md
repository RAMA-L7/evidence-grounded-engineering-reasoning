# EGER-C1-CAUSAL-MECHANISM-RECONCILIATION-001

| Field | Value |
|-------|-------|
| ID | EGER-C1-CAUSAL-MECHANISM-RECONCILIATION-001 |
| Produced by | EGER-P020 (2026-08-26) |
| Type | Scientific reconciliation — READ ONLY |
| Predecessor | EGER-P019 (C1 Text Feedback Contract R1) |
| Status | **RECOMMENDATION READY — HUMAN DECISION REQUIRED** |
| Purpose | Resolve the C1 causal-mechanism contradiction discovered during human review of P019 |

---

## 1. Issue Identified

P019 contains two incompatible definitions of C1 execution:

**Definition A (from §4 ODQ-2):**
```
MODEL (1 call)
  ↓
CANDIDATE
  ↓
ORACLE
  ↓
TEXT FEEDBACK
  ↓
END
```

With stated constraint: "One model call. No second model call."

**Definition B (from §3 ODQ-1):**
```
CANDIDATE (Engineer's proposal)
  ↓
ORACLE TEXT FEEDBACK
  ↓
"produce a revised SDC candidate"
```

The instruction "produce a revised candidate" necessarily requires another model generation. A model cannot produce output without being called.

These two definitions cannot both be true simultaneously.

---

## 2. Existing C1 Definition

From EGER-EXP-001 v0.1 §6:

> **C1**: + textual tool feedback (deterministic oracle output rendered as text)

From EGER-ARCH-002 condition deltas:

> C0→C1: Oracle execution; findings as plain text

From the secondary research question (RESEARCH.md §5):

> Does feedback representation (none / text / structured evidence) measurably change reliability?

The protocol defines C1 as adding text feedback. It does not explicitly specify whether the Engineer revises its candidate after receiving feedback.

---

## 3. Interpretation A — Post-Proposal Feedback

### Pipeline

```
LLM (1 call)
  ↓
CANDIDATE (measured artifact)
  ↓
ORACLE (evaluates candidate)
  ↓
TEXT FEEDBACK (rendered, shown to Engineer)
  ↓
END (no further model call)
```

### What It Tests

The effect of **exposing** the Engineer to deterministic text feedback **after** it has already produced its candidate.

### Scientific Problem

The feedback arrives after the model has finished generating. The measured artifact (the candidate) was produced **without** knowledge of the feedback. Therefore:

- The feedback cannot influence the candidate that is measured
- The feedback has no causal pathway to the outcome
- C1 would measure the same thing as C0 (an LLM proposal without feedback influence)

### What C1 Would Actually Measure Under This Interpretation

Nothing useful about feedback effectiveness. The only difference from C0 is that the feedback text exists in the prompt after the candidate — but the model has already stopped generating.

### Verdict

**Interpretation A is scientifically vacuous.** It does not test the intended research question.

---

## 4. Interpretation B — Feedback-Assisted Revision

### Pipeline

```
LLM (call 1)
  ↓
INITIAL CANDIDATE
  ↓
ORACLE (evaluates initial candidate)
  ↓
TEXT FEEDBACK (rendered)
  ↓
LLM (call 2 — revision)
  ↓
FINAL CANDIDATE (measured artifact)
```

### What It Tests

The effect of **deterministic text feedback on subsequent engineering revision.**

### Scientific Meaning

This directly answers the secondary research question:

> Does feedback representation measurably change reliability?

The Engineer:
1. Proposes a candidate (same as C0)
2. Receives deterministic oracle feedback
3. Produces a revised candidate informed by that feedback
4. The revised candidate is the measured artifact

### Causal Mechanism

```
TREATMENT: Deterministic text feedback
MECHANISM: Engineer reads feedback → revises candidate
OUTCOME: Revised candidate quality vs. C0 initial proposal quality
```

### Verdict

**Interpretation B is the scientifically meaningful C1.** It tests the intended research question with a clear causal pathway.

---

## 5. Scientific Meaning of Each

| Aspect | Interpretation A | Interpretation B |
|--------|-----------------|-----------------|
| Research question answered | "Does feedback exist after proposal?" (trivial: yes) | "Does feedback improve the proposal?" (the actual question) |
| Causal pathway | Feedback → [blocked] → measured artifact | Feedback → revision → measured artifact |
| Comparison to C0 | Identical (no feedback influence on artifact) | Meaningful (C0 = no feedback, C1 = feedback-assisted revision) |
| Independent variable | None (feedback has no effect) | Text feedback availability during revision |
| Scientific value | None | Directly tests H1 for C1 |

---

## 6. Independent Variable Analysis

### Under Interpretation A

The independent variable is ill-defined. "Exposure to feedback after completion" is not a treatment that can affect the outcome.

### Under Interpretation B

The independent variable is precisely defined:

**C1 Treatment:** Access to deterministic oracle text feedback during iterative proposal refinement.

This decomposes into:
- **Feedback availability:** Engineer receives deterministic text feedback
- **Revision opportunity:** Engineer may revise its proposal based on feedback
- **Single revision:** Only one feedback-revision cycle (not iterative convergence)

### Is the Additional Model Call a Confound?

**No.** The additional model call is an **inherent component of the treatment.**

The treatment is defined as "feedback-assisted revision." Revision requires a model call. Without the revision call, there is no treatment to measure.

This is analogous to:
- A drug trial where the treatment is "drug + monitoring" — the monitoring visits are part of the treatment protocol, not a confound
- A teaching experiment where the treatment is "feedback on draft" — the revision step is part of the treatment, not a confound

The key question is not "does C1 have more model calls than C0?" but "does the feedback during the revision call improve the outcome?"

### What IS a Confound

If C1 introduced:
- A different model
- A different temperature
- A different prompt structure (beyond adding feedback)
- A different oracle configuration
- Additional oracle evaluations beyond what C0 uses

Those would be confounds. The revision model call itself is not.

---

## 7. C0→C1 Comparability

### What Should Be Compared

| Comparison | C0 | C1 | Valid? |
|------------|----|----|--------|
| Initial proposal quality | LLM → candidate | LLM → initial candidate | Same (both are first proposals) |
| Final artifact quality | LLM → candidate (only artifact) | LLM → revised candidate (after feedback) | **This is the primary comparison** |
| Feedback responsiveness | N/A (no feedback) | Engineer addresses findings | C1-specific metric |

### Primary Comparison

**C0 final artifact vs. C1 final artifact.**

C0 produces one candidate (no feedback, no revision).
C1 produces one candidate (after feedback and revision).

The comparison asks: **Does the feedback-assisted revision produce a better artifact than the no-feedback proposal?**

### Secondary Comparison

**C1 initial proposal vs. C1 final proposal.**

This measures the **magnitude of revision** — how much did the Engineer change its candidate in response to feedback? This is an additional metric that C1 enables but C0 does not.

### Why Not Compare C0 Final vs. C1 Initial

C1 initial is produced under the same conditions as C0 (no feedback yet). Comparing C0 final to C1 initial would test model variance, not feedback effectiveness.

---

## 8. Artifact Measurement

### What Should Be the Measured C1 Artifact?

**The final revised candidate** (output of the second model call).

### Rationale

- The research question is "does feedback improve the proposal?"
- The improved proposal is the revised candidate
- The initial candidate is an intermediate artifact (same as C0, not the treatment outcome)

### Initial Candidate Retention

The initial candidate should be **retained as a run artifact** for:
- Measuring revision magnitude (initial vs. final)
- Verifying the feedback was about the actual candidate
- Post-hoc analysis of what the Engineer changed

But the **primary measured artifact** for C1 comparison is the **final revised candidate**.

---

## 9. Oracle Interaction

### Should the Oracle Evaluate the Revised Candidate?

**Recommended: YES — but as measurement, not as treatment.**

```
C1 Pipeline (recommended):
  LLM (call 1) → initial candidate
  ORACLE → evaluates initial candidate → text feedback
  LLM (call 2) → revised candidate (informed by feedback)
  ORACLE → evaluates revised candidate (measurement only)
```

### Rationale

- The first oracle evaluation is part of the **treatment** (generates feedback)
- The second oracle evaluation is part of **measurement** (evaluates the outcome)
- Without the second evaluation, we cannot compare C1 artifact quality to C0 artifact quality using the same oracle

### Alternative: No Second Oracle Evaluation

```
C1 Pipeline (alternative):
  LLM (call 1) → initial candidate
  ORACLE → evaluates initial candidate → text feedback
  LLM (call 2) → revised candidate
  [END — no second oracle evaluation]
```

**Problem:** We cannot compare C1 final artifact quality to C0 using the same oracle evaluation. The C0 artifacts were evaluated by the oracle (evaluator-side). If C1 final artifacts are not evaluated, we lose the primary comparison metric.

### Recommendation

**Include the second oracle evaluation.** It is measurement, not treatment. The treatment is the feedback; the second evaluation measures the outcome.

### Budget Impact

| Resource | C0 | C1 | Within Budget? |
|----------|----|----|----------------|
| Model calls | 1 | 2 | YES (budget: 5) |
| Oracle calls | 0 (evaluator-side) | 2 (1 treatment + 1 measurement) | YES (budget: 5) |
| Max iterations | 1 | 1 | YES (budget: 5) |

**No budget change required. No REQUIRES EXPERIMENT CHANGE CONTROL.**

---

## 10. Model Budget

### MODEL-002 Current Budget

| Parameter | Value | C0 Usage | C1 Usage (Interpretation B) |
|-----------|-------|----------|----------------------------|
| max_model_calls | 5 | 1 | 2 |
| max_oracle_calls | 5 | 0 | 2 |
| max_iterations | 5 | 1 | 1 |
| max_wall_clock | 300s | <5s | <10s |

### Assessment

C1 with Interpretation B fits within the existing MODEL-002 budget. No change control required.

---

## 11. Information Boundary

### What Each Model Call Receives

**Call 1 (Initial Proposal):**
- Task context (design_context, objective, constraints)
- Same as C0 — no feedback yet

**Call 2 (Revision):**
- Task context (design_context, objective, constraints)
- Initial candidate (from call 1)
- Deterministic text feedback (per C1 text feedback contract)
- Instruction: "Given the oracle feedback above, produce a revised SDC candidate"

### What Call 2 Does NOT Receive

- Evaluator-only answers
- Expected solutions
- C0 results
- Other tasks
- Research canon
- Git history
- Oracle source
- Epistemic state (C3 treatment)
- Authorization decisions (C5 treatment)
- Structured EvidenceArtifact (C2 treatment)

### Boundary Integrity

Call 2 receives the same task context as Call 1 (necessary for revision) plus the feedback (the treatment). No additional capabilities are introduced beyond text feedback.

---

## 12. Metrics Implications

### Primary Metrics Under Interpretation B

| Metric | C0 | C1 | Comparison |
|--------|----|----|------------|
| Artifact reliability | Final candidate evaluation | Final (revised) candidate evaluation | **Primary comparison** |
| Reasoning reliability | N/A (no feedback) | Revision quality, finding response | C1-specific |
| Epistemic reliability | N/A (no L2 in C0/C1) | N/A (no L2 in C1) | Not applicable until C3 |
| Convergence | N/A (single-shot) | N/A (single revision) | Not applicable until C3+ |

### Additional C1-Specific Metrics

| Metric | Definition | Purpose |
|--------|-----------|---------|
| Revision magnitude | How much did the candidate change? | Measures feedback responsiveness |
| Finding recovery | Did Engineer address specific SDC-xxx findings? | Measures evidence utilization |
| Over-correction | Did Engineer introduce new errors while fixing old ones? | Measures revision quality |
| INSUFFICIENT response | How did Engineer react to scope limitation? | Confound monitoring (CM-3) |

### Metrics NOT Changed

No primary metrics are redefined. The additional C1-specific metrics are **secondary exploratory metrics** — they provide insight into the mechanism but do not replace the primary comparison.

---

## 13. Confound Monitoring (CM-1 through CM-7)

### Validity Under Interpretation B

| Indicator | Valid under Interpretation A? | Valid under Interpretation B? |
|-----------|------------------------------|------------------------------|
| CM-1: Recovery from specific finding | N/A (no revision) | YES — Engineer sees SDC-xxx, may address in revision |
| CM-2: Correction of known error | N/A | YES — Engineer may fix errors identified by oracle |
| CM-3: Response to INSUFFICIENT | N/A | YES — Engineer sees scope limitation, may react |
| CM-4: Unchanged after non-actionable | N/A | YES — Info findings may produce no change |
| CM-5: Improvement from evidence | N/A | YES — Compare initial vs. revised candidate |
| CM-6: New errors introduced | N/A | YES — Compare initial vs. revised evidence |
| CM-7: Convergence attempt | N/A | N/A (single revision, no iteration) |

### Assessment

Interpretation B makes **all 7 CM indicators observable** (except CM-7 which requires iteration). Interpretation A makes **none observable** (no revision = no behavioral response to measure).

This is strong evidence that Interpretation B is the intended design.

---

## 14. Authority Separation (P7)

### Under Interpretation B

```
PROPOSAL AUTHORITY:    LLM (call 1: initial, call 2: revision)
EVIDENCE AUTHORITY:    Oracle (deterministic — evaluates and generates feedback)
EPISTEMIC STATE:       Not exposed in C1 (C3 treatment)
AUTHORIZATION:         Not exposed in C1 (C5 treatment)
```

### P7 Compliance

- LLM proposes and revises — Proposal authority only ✓
- Oracle establishes evidence and generates feedback — Evidence authority only ✓
- LLM does not declare validation — No epistemic authority ✓
- LLM does not authorize commits — No authorization authority ✓
- Oracle does not generate candidates — No proposal authority ✓

**P7 is preserved under Interpretation B.**

---

## 15. Subagent Boundary

### Under Interpretation B

C1 remains **one probabilistic model identity** across both calls. The same LLM makes the initial proposal and the revision. No supervisor, critic, reviewer, or second model is introduced.

```
C1 = one LLM, two calls, same identity, same configuration
```

**No subagent boundary violation.**

---

## 16. Scientific Recommendation

### What Does EGER Actually Intend C1 to Test?

The secondary research question (RESEARCH.md §5) asks:

> Does feedback representation (none / text / structured evidence) measurably change reliability?

C1 tests the first step: **text feedback vs. no feedback.**

For this test to be meaningful, the Engineer must **use** the feedback to revise its proposal. If the feedback is delivered after the candidate is already generated and no revision occurs, the test measures nothing.

### Which Interpretation Is Scientifically Stronger?

**Interpretation B (feedback-assisted revision) is overwhelmingly stronger.**

| Criterion | Interpretation A | Interpretation B |
|-----------|-----------------|-----------------|
| Tests intended research question | NO | YES |
| Causal pathway exists | NO (feedback after completion) | YES (feedback → revision → outcome) |
| CM indicators observable | NO | YES (6/7) |
| Comparison to C0 meaningful | NO (identical) | YES (feedback-assisted vs. no feedback) |
| Independent variable defined | NO (no treatment effect) | YES (text feedback during revision) |

### What Exactly Is the Independent Variable?

**C1 independent variable:** Access to deterministic oracle text feedback during proposal revision.

This is a single variable with two levels:
- **C0:** No feedback available (LLM proposes blindly)
- **C1:** Text feedback available (LLM proposes, receives feedback, revises)

### Is Iteration Part of the Treatment or a Confound?

**Iteration (the revision call) is part of the treatment.**

The treatment is defined as "feedback-assisted revision." Revision inherently requires a model call. The revision call is not an additional variable — it is the mechanism through which the treatment (feedback) exerts its effect.

A confound would be:
- Changing the model between calls
- Changing the temperature
- Adding oracle capabilities beyond feedback generation
- Introducing a second probabilistic component

None of these occur in Interpretation B.

### What Should Be the Measured C1 Artifact?

**The final revised candidate** (output of call 2, after feedback).

The initial candidate is retained as an intermediate artifact for revision-magnitude analysis but is not the primary measured outcome.

### How Should C0 and C1 Outcomes Be Compared?

| Comparison | Purpose |
|------------|---------|
| C0 final artifact vs. C1 final artifact | **Primary:** Does feedback-assisted revision improve the outcome? |
| C1 initial vs. C1 final | **Secondary:** How much did the Engineer revise? |
| C0 artifact vs. C1 initial | **Diagnostic:** Are first proposals similar across conditions? (tests model consistency) |

### What Additional Oracle Interaction Is Required?

**Two oracle evaluations in C1:**
1. First evaluation: generates feedback (part of treatment)
2. Second evaluation: evaluates revised candidate (measurement)

Both are necessary. The first is the treatment mechanism; the second is the outcome measurement.

### What Model-Call Budget Is Required?

| Resource | C0 | C1 | Budget | Within Budget? |
|----------|----|----|--------|----------------|
| Model calls | 1 | 2 | 5 | YES |
| Oracle calls | 0 | 2 | 5 | YES |

**No budget change required.**

### What Changes Require Formal Change Control?

**None.** Interpretation B fits within the existing frozen protocol:
- MODEL-002 budget accommodates 2 model calls
- EXP-001 v0.1 §6 defines C1 as "+ textual tool feedback" — revision is implied by "feedback"
- No new capabilities beyond text feedback are introduced

---

## 17. Required Change-Control Items

### If Interpretation B Is Selected

**No EGER-CHANGE-### required.** The existing protocol accommodates Interpretation B:
- Budget fits within MODEL-002
- C1 definition ("+ textual tool feedback") implies revision
- No new capabilities beyond text feedback

### Documentation Updates Required

| Document | Change | Reason |
|----------|--------|--------|
| EGER-C1-TEXT-FEEDBACK-CONTRACT-001-R1 | Revise ODQ-2 from "single-shot" to "feedback-assisted revision" | Correct the contradiction |
| EGER-C1-READINESS-001 | Update C1 pipeline definition | Reflect revised understanding |
| EGER-EXP-001 v0.1 | Clarify §6 C1 definition to explicitly include revision | Remove ambiguity |

These are **documentation corrections**, not protocol changes. The underlying scientific design is unchanged.

---

## 18. Remaining Open Questions

| # | Question | Status | Impact |
|---|----------|--------|--------|
| 1 | Should the second oracle evaluation be mandatory or optional? | RECOMMENDED: mandatory | Affects measurement completeness |
| 2 | How should C1 initial vs. C1 final comparison be formalized? | OPEN | Secondary metric definition |
| 3 | Should CM-7 (convergence) be redefined for single-revision C1? | OPEN | May need adaptation for C1 |

---

## 19. Human Decision Required

The human researcher must decide:

### Decision 1: Accept Interpretation B?

**Recommended: YES.** Interpretation A is scientifically vacuous. Interpretation B tests the intended research question.

### Decision 2: Accept Two Oracle Evaluations?

**Recommended: YES.** First evaluation generates feedback (treatment). Second evaluation measures outcome (measurement). Both are necessary.

### Decision 3: Accept "Revised Candidate" as Primary Measured Artifact?

**Recommended: YES.** The revised candidate is the treatment outcome. The initial candidate is an intermediate artifact.

### Decision 4: Authorize Documentation Corrections?

If Interpretation B is accepted, the P019 contract needs documentation corrections (not protocol changes) to resolve the contradiction.

---

## 20. Non-Decisions

This reconciliation does NOT decide:

- C1 experimental outcome
- C1 performance metrics
- H1 validity for C1
- C0→C1 improvement
- Confound presence or absence
- C2 design
- C3 design
- C4 design
- C5 design
- C6 design

Those remain future research questions.

---

## 21. Contract / Principle References

| Reference | Relevance |
|-----------|-----------|
| RESEARCH.md §5 | Secondary research question: "Does feedback representation measurably change reliability?" |
| EXP-001 v0.1 §6 | C1 definition: "+ textual tool feedback" |
| ARCH-002 condition deltas | C0→C1 adds oracle execution + text rendering |
| P5 — Repetition Drives Convergence | "Iteration with feedback is the mechanism under study" |
| P7 — Authority Separation | Proposal ≠ Evidence ≠ Epistemic ≠ Authorization |
| DEC-005 | One probabilistic component for C0–C5 |

---

## 22. Final Reconciliation

### The Contradiction

P019 says "single-shot" (one model call) AND "produce a revised candidate" (requires another call). These are incompatible.

### The Resolution

**Interpretation B is correct.** C1 tests feedback-assisted revision. The pipeline is:

```
LLM (call 1) → initial candidate
ORACLE → evaluates initial candidate → text feedback
LLM (call 2) → revised candidate (informed by feedback)
ORACLE → evaluates revised candidate (measurement)
```

### What Changes

| Aspect | P019 (Incorrect) | Reconciliation (Correct) |
|--------|------------------|-------------------------|
| Model calls | 1 | 2 |
| Oracle calls | 1 | 2 |
| Primary artifact | Ambiguous | Final revised candidate |
| Independent variable | "Exposure to feedback" | "Feedback-assisted revision" |
| CM indicators observable | 0/7 | 6/7 |

### What Does NOT Change

- Text feedback contract (format, fields, rendering)
- Information boundary
- Authority separation
- Subagent boundary
- Model/benchmark freeze
- Oracle boundary

---

*This reconciliation is PROPOSED — AWAITING HUMAN DECISION. Once the human accepts Interpretation B, the P019 contract may be corrected and C1 implementation may proceed.*
