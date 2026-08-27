# EGER-C1-PROTOCOL-CHANGE-ASSESSMENT-001

| Field | Value |
|-------|-------|
| ID | EGER-C1-PROTOCOL-CHANGE-ASSESSMENT-001 |
| Produced by | EGER-P021 (2026-08-26) |
| Type | Audit and change-control assessment — READ ONLY |
| Predecessor | EGER-P020 (C1 Causal Mechanism Reconciliation) |
| Status | **CHANGE-CONTROL DECISION READY — HUMAN APPROVAL REQUIRED** |
| Purpose | Determine whether feedback-assisted revision requires formal experimental change control |

---

## 1. Purpose

This document assesses the protocol consequences of the C1 causal-mechanism decision from EGER-P020. P020 recommended Interpretation B (feedback-assisted revision). This assessment determines whether adopting that mechanism requires formal experimental change control.

**Key principle:** Budget compatibility ≠ experimental-protocol compatibility.

---

## 2. Historical C1 Definition

### What EXP-001 v0.1 §6 Actually Says

> **C1**: + textual tool feedback (deterministic oracle output rendered as text)

### What EXP-001 v0.1 §7 (Capability Matrix) Shows

| Capability | C0 | C1 |
|------------|----|----|
| Candidate generation | ✓ | ✓ |
| Text feedback | - | ✓ |
| Structured evidence | - | - |
| Epistemic state (read-only) | - | - |
| Deterministic routing | - | - |
| Authorization gate | - | - |

### What ARCH-002 Condition Deltas Say

> C0→C1: Oracle execution; findings as plain text

### What the Protocol Does NOT Specify

- Whether the Engineer revises its candidate after receiving feedback
- Whether C1 uses one model call or two
- Whether the initial candidate or the revised candidate is the measured artifact
- Whether the oracle evaluates the revised candidate

### Assessment

**The original protocol is AMBIGUOUS about the C1 execution mechanism.** It defines the capability (text feedback) but not the procedure (whether revision occurs).

---

## 3. P019's Interpretation (Single-Shot)

### What P019 Decided

| Aspect | P019 Decision |
|--------|--------------|
| Model calls | 1 |
| Oracle calls | 1 |
| Revision | None |
| Primary artifact | First proposal |
| Pipeline | LLM → candidate → oracle → feedback → END |

### P019's Rationale

> "C0 is single-proposal. If C1 introduces iteration, it introduces both 'text feedback' AND 'iterative interaction / additional model calls' as simultaneous changes. That violates the one-variable-at-a-time principle."

### Scientific Verdict (from P020)

**Interpretation A is scientifically vacuous.** The feedback arrives after the model has finished generating. The measured artifact was produced without feedback influence. C1 would measure the same thing as C0.

---

## 4. P020's Recommended C1 Definition (Feedback-Assisted Revision)

### What P020 Recommended

| Aspect | P020 Decision |
|--------|--------------|
| Model calls | 2 |
| Oracle calls | 2 |
| Revision | Yes (one revision) |
| Primary artifact | Final revised candidate |
| Pipeline | LLM → initial → oracle → feedback → LLM → revised → oracle (measurement) |

### P020's Rationale

The treatment is "feedback-assisted revision." Revision inherently requires a model call. The revision call is part of the treatment, not a confound.

### Scientific Verdict

**Interpretation B tests the intended research question** with a clear causal pathway.

---

## 5. Scientific Difference

### What Changes Between P019 and P020

| Aspect | P019 (Historical) | P020 (Recommended) | Delta |
|--------|-------------------|-------------------|-------|
| Model calls | 1 | 2 | +1 |
| Oracle calls | 1 | 2 | +1 |
| Primary artifact | Initial candidate | Final revised candidate | Changed |
| Independent variable | "Exposure to feedback" | "Feedback-assisted revision" | Redefined |
| Causal pathway | None (feedback after completion) | Feedback → revision → outcome | Established |
| CM indicators observable | 0/7 | 6/7 | +6 |

### What Does NOT Change

- Text feedback contract (format, fields, rendering)
- Information boundary (what Engineer may/may not receive)
- Authority separation (P7)
- Subagent boundary
- Model/benchmark freeze
- Oracle boundary
- Research question
- Hypothesis H1

---

## 6. Independent Variable

### Original Protocol Language

C1 = "+ textual tool feedback (deterministic oracle output rendered as text)"

### Under P019

IV = "Exposure to text feedback after proposal generation"

### Under P020

IV = "Access to deterministic oracle text feedback during proposal revision"

### Assessment

The IV is **redefined, not added.** P020's IV is a more precise and scientifically meaningful version of the original protocol's intent. The original protocol said "text feedback" — P020 specifies how that feedback is used.

**This is a clarification of the independent variable, not a new variable.**

---

## 7. Iteration as Treatment vs Confound

### P019's Concern

> "If C1 introduces iteration, it introduces both 'text feedback' AND 'iterative interaction / additional model calls' as simultaneous changes."

### P020's Resolution

The revision call is **part of the treatment**, not a confound. The treatment is defined as "feedback-assisted revision." Revision inherently requires a model call.

### This Assessment's Analysis

P019's concern was based on a misunderstanding: it treated the revision call as an "additional variable" rather than as the mechanism through which the treatment (feedback) exerts its effect.

Analogies:
- A drug trial where the treatment is "drug + monitoring" — monitoring visits are part of the treatment protocol
- A teaching experiment where the treatment is "feedback on draft" — the revision step is part of the treatment

**The revision call is not a confound. It is the treatment mechanism.**

---

## 8. Model Budget

### MODEL-002 Frozen Budget

| Parameter | Value |
|-----------|-------|
| max_model_calls | 5 |
| max_oracle_calls | 5 |
| max_iterations | 5 |
| max_wall_clock | 300s |

### C0 Usage

| Resource | C0 Actual |
|----------|-----------|
| Model calls | 1 |
| Oracle calls | 0 (evaluator-side only) |

### C1 Usage (P020)

| Resource | C1 Actual |
|----------|-----------|
| Model calls | 2 |
| Oracle calls | 2 |

### Budget Compatibility

| Resource | C1 Usage | Budget | Within? |
|----------|----------|--------|---------|
| Model calls | 2 | 5 | YES |
| Oracle calls | 2 | 5 | YES |

### Protocol Compatibility

**The budget accommodates C1. But does the original protocol authorize two model calls?**

The original protocol (EXP-001 v0.1 §13) says:

> Per-run caps: max_iterations = 5, max_model_calls = 5, max_oracle_calls = 5

This is a **resource budget**, not a **protocol definition**. It says C1 *can* use up to 5 calls. It does not say C1 *should* use exactly 1 or exactly 2.

### Assessment

**Budget compatibility is necessary but not sufficient.** The budget allows 2 calls. But the original protocol did not explicitly authorize 2 calls for C1 — it was ambiguous. P019 interpreted it as 1 call. P020 recommends 2 calls. Both fit within the budget.

**This is a protocol clarification, not a budget change.**

---

## 9. Oracle Budget

### C0 Oracle Usage

C0 uses 0 oracle calls during the Engineer's run. The oracle evaluates candidates evaluator-side (after the run).

### C1 Oracle Usage (P020)

| Call | Purpose | Classification |
|------|---------|---------------|
| Oracle call 1 | Evaluate initial candidate → generate text feedback | **Treatment mechanism** |
| Oracle call 2 | Evaluate revised candidate → measure outcome | **Measurement** |

### Assessment

**Both oracle calls are scientifically necessary.**
- Call 1 is the treatment (generates feedback)
- Call 2 is measurement (evaluates the outcome)

Without call 2, we cannot compare C1 artifact quality to C0 using the same oracle evaluation.

**This is a clarification of oracle usage, not a new oracle capability.**

---

## 10. Artifact Measurement

### What P019 Measured

Initial candidate (only artifact produced).

### What P020 Measures

| Artifact | Classification | Purpose |
|----------|---------------|---------|
| Initial candidate | Intermediate | Revision-magnitude analysis |
| Final revised candidate | **Primary outcome** | C0 vs C1 comparison |
| Initial oracle evidence | Treatment | Generates feedback |
| Final oracle evidence | Measurement | Evaluates outcome |

### Assessment

**The primary measured artifact changes from initial to final candidate.** This is a material change in what C1 measures.

However, this change is **scientifically justified** — the initial candidate is the same as C0 (no feedback influence), so measuring it would not test the treatment effect.

---

## 11. Metric Impact

### Primary Metrics

| Metric | C0 | C1 (P019) | C1 (P020) | Change? |
|--------|----|-----------|-----------|---------| 
| Artifact reliability | Final candidate evaluation | Initial candidate evaluation | Final revised candidate evaluation | **Yes — measurement point changed** |
| Reasoning reliability | N/A | N/A | Revision quality, finding response | **Yes — now measurable** |
| Epistemic reliability | N/A | N/A | N/A | No change (C3) |
| Convergence | N/A | N/A | N/A | No change (C3+) |
| Efficiency | 1 model call | 1 model call | 2 model calls | **Yes — reported differently** |

### Assessment

**Artifact reliability measurement point changes.** Under P019, C1 measured the initial candidate. Under P020, C1 measures the final revised candidate. This is a material change in what the metric captures.

**Reasoning reliability becomes measurable.** Under P019, there was no revision to measure. Under P020, revision quality is observable.

**Efficiency must be reported carefully.** C1 uses more computation than C0. This must be reported without conflating improved outcome with increased expenditure.

---

## 12. Confound Monitoring

### CM-1 through CM-7 Assessment

| Indicator | P019 (Single-Shot) | P020 (Revision) | Change? |
|-----------|--------------------|--------------------|---------| 
| CM-1: Recovery from specific finding | Not observable (no revision) | Observable | **Yes — now measurable** |
| CM-2: Correction of known error | Not observable | Observable | **Yes** |
| CM-3: Response to INSUFFICIENT | Not observable | Observable | **Yes** |
| CM-4: Unchanged after non-actionable | Not observable | Observable | **Yes** |
| CM-5: Improvement from evidence | Not observable | Observable | **Yes** |
| CM-6: New errors introduced | Not observable | Observable | **Yes** |
| CM-7: Convergence attempt | Not applicable | Partially observable | **Yes — needs review** |

### CM-7 Specific Assessment

P019 said CM-7 "requires iteration" and marked it N/A for single-shot C1.

Under P020, C1 has one revision (not iterative convergence). CM-7 concerns "convergence attempt" — which in C1 context means "does the Engineer attempt to improve toward VALIDATED?"

**CM-7 should be redefined for C1:** Instead of measuring iterative convergence (which requires C3+), measure whether the Engineer's revision moves the candidate toward a state that the oracle would evaluate more favorably.

### Assessment

**CM-1 through CM-6 become observable under P020.** This is a significant improvement in confound-monitoring capability.

**CM-7 requires definition update** for the single-revision C1 context.

---

## 13. Information Boundary

### Model Call 1

| Allowed | Not Allowed |
|---------|-------------|
| Task context | Evaluator answers |
| Objective | Expected solutions |
| Constraints | C0/C1 results |
| | Research canon |
| | Git history |
| | Oracle source |

### Model Call 2

| Allowed | Not Allowed |
|---------|-------------|
| Task context | Evaluator answers |
| Objective | Expected solutions |
| Constraints | C0/C1 results |
| Initial candidate (from call 1) | Research canon |
| Deterministic text feedback | Git history |
| | Oracle source |
| | Epistemic state (C3) |
| | Authorization (C5) |
| | Structured evidence (C2) |

### Assessment

**Call 2 receives the initial candidate.** This is necessary for the Engineer to relate findings to its proposal. It does not create an unintended information advantage relative to C0 — C0 also produces a candidate, it just doesn't see it again.

**The information boundary is preserved.** No evaluator answers, no research canon, no capabilities from C2–C5 leak into C1.

---

## 14. Authority Separation

### Under P020

```
PROPOSAL AUTHORITY:    LLM (call 1: initial, call 2: revision)
EVIDENCE AUTHORITY:    Oracle (evaluates + generates feedback)
EPISTEMIC STATE:       Not active in C1
AUTHORIZATION:         Not active in C1
```

### P7 Compliance

- LLM proposes and revises — Proposal authority only ✓
- Oracle evaluates and generates feedback — Evidence authority only ✓
- LLM does not declare validation ✓
- Oracle does not generate candidates ✓

**P7 is preserved. No authority leakage.**

---

## 15. Benchmark Impact

### BENCH-002 Status

**No changes required.** The C1 revision mechanism uses the same tasks, same engineer-visible inputs, same evaluator-only expected answers.

The revision mechanism does not require:
- New tasks
- Modified tasks
- Different task ordering
- Different evaluation criteria

**BENCH-002 remains frozen and valid.**

---

## 16. Ṛta Impact

### Oracle Interface

**No changes required.** The C1 flow uses the same oracle interface:
- Input: candidate SDC
- Output: EvidenceArtifact (findings, scope, hashes)

The oracle is called twice in C1 (once for feedback, once for measurement), but each call uses the same interface. No oracle modification is needed.

**Ṛta remains EXTERNAL / READ-ONLY.**

---

## 17. Reproducibility Impact

### Additional Run Information Required

Under P020, C1 runs must record:

| Artifact | P019 | P020 | Required? |
|----------|------|------|-----------|
| Initial candidate | Not recorded | candidate_v1.json | YES |
| First oracle evidence | evidence.json | evidence_initial.json | YES |
| Text feedback | Not recorded | text_feedback.txt | YES |
| Final candidate | candidate_v1.json | candidate_final_v1.json | YES |
| Final oracle evidence | Not recorded | evidence_final.json | YES |
| Model call identifiers | 1 call | 2 calls (call_1_id, call_2_id) | YES |
| Oracle call identifiers | 0 calls | 2 calls (call_1_id, call_2_id) | YES |

### Assessment

**Run manifest schema requires extension** to record initial/final candidates and initial/final oracle evidence. This is a **documentation/schema change**, not an experimental change.

---

## 18. Change-Control Classification

### Primary Classification

**C. EGER-CHANGE-### REQUIRED**

### Rationale

The move from P019's single-shot interpretation to P020's feedback-assisted revision constitutes a **formal experimental protocol change** because:

1. **The independent variable is redefined:** From "exposure to feedback" to "feedback-assisted revision"
2. **The primary measured artifact changes:** From initial candidate to final revised candidate
3. **The execution mechanism changes:** From 1 model call to 2 model calls
4. **The oracle interaction changes:** From 1 call (feedback only) to 2 calls (feedback + measurement)
5. **The run manifest schema requires extension**
6. **CM-7 requires definition update**

### What This Is NOT

- This is NOT a new independent variable (it's a clarification of the existing one)
- This is NOT a budget change (fits within existing budget)
- This is NOT a benchmark change (same tasks, same evaluation)
- This is NOT a model change (same model, same parameters)
- This is NOT an oracle change (same interface, same configuration)

### What This IS

A **formal clarification and operational definition** of the C1 experimental condition. The original protocol was ambiguous about the C1 mechanism. P019 proposed one interpretation (single-shot). P020 identified it as scientifically vacuous and recommended another (feedback-assisted revision). This recommendation requires formal change-control because it materially changes what C1 measures and how it executes.

---

## 19. Required Document Revisions

### If Human Approves Feedback-Assisted Revision

| Document | Change | Scientific Content Change? | Priority |
|----------|--------|--------------------------|----------|
| EGER-CHANGE-001 (new) | Record the C1 protocol clarification | YES — formalizes the change | REQUIRED |
| EGER-EXP-001 v0.1 → v0.2 | Clarify §6 C1 definition to include revision | YES — updates protocol version | REQUIRED |
| EGER-C1-TEXT-FEEDBACK-CONTRACT-001-R1 | Revise ODQ-2 from "single-shot" to "feedback-assisted revision" | YES — corrects contradiction | REQUIRED |
| EGER-C1-READINESS-001 | Update C1 pipeline definition | YES — reflects revised understanding | REQUIRED |
| EGER-MODEL-002 | Document that C1 uses 2 model calls (within budget) | NO — documentation only | RECOMMENDED |
| STATE.md | Update C1 status | NO — traceability only | REQUIRED |
| RESEARCH_LEDGER.md | Record EGER-P021 and EGER-CHANGE-001 | NO — traceability only | REQUIRED |

### What Must NOT Change

- BENCH-002 (frozen benchmark)
- MODEL-002 (frozen model — budget accommodates 2 calls)
- Ṛta (external, read-only)
- C0 artifacts (historical evidence)
- P018/P019/P020 documents (historical provenance)

---

## 20. Human Decision Required

The human researcher must decide:

### Decision 1: Accept Feedback-Assisted Revision as C1?

**Recommended: YES.** P020's analysis is scientifically rigorous. Interpretation A is vacuous. Interpretation B tests the intended research question.

### Decision 2: Accept Two Model Calls for C1?

**Recommended: YES.** The revision call is part of the treatment, not a confound. Fits within MODEL-002 budget.

### Decision 3: Accept Two Oracle Calls for C1?

**Recommended: YES.** First call generates feedback (treatment). Second call measures outcome (measurement). Both necessary.

### Decision 4: Accept Final Revised Candidate as Primary Artifact?

**Recommended: YES.** The initial candidate is the same as C0 (no feedback influence). The final candidate is the treatment outcome.

### Decision 5: Authorize EGER-CHANGE-001?

**Recommended: YES.** The protocol clarification is material and should be formally recorded.

### Decision 6: Authorize EXP-001 v0.2?

**Recommended: YES.** The C1 definition should be explicitly updated to include revision.

---

## 21. Non-Decisions

This assessment does NOT decide:

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

## 22. Final Change-Control Decision

### Classification: **EGER-CHANGE-### REQUIRED**

### Summary

| Aspect | Original (Ambiguous) | P019 (Single-Shot) | P020 (Recommended) | Change Control? |
|--------|---------------------|--------------------|--------------------|-----------------|
| Independent variable | "Text feedback" | "Exposure to feedback" | "Feedback-assisted revision" | YES — clarification |
| Model calls | Unspecified | 1 | 2 | YES — operational definition |
| Oracle calls | Unspecified | 1 | 2 | YES — operational definition |
| Primary artifact | Unspecified | Initial candidate | Final revised candidate | YES — measurement point |
| CM indicators | Unspecified | 0/7 observable | 6/7 observable | YES — CM-7 needs update |
| Run manifest | Unspecified | Minimal | Extended | YES — schema update |

### What Requires Formal Change Control

1. **EGER-CHANGE-001:** Record the C1 protocol clarification (feedback-assisted revision)
2. **EXP-001 v0.2:** Update §6 C1 definition to explicitly include revision
3. **Run manifest schema:** Extend to record initial/final candidates and oracle evidence

### What Does NOT Require Change Control

- MODEL-002 (budget accommodates 2 calls)
- BENCH-002 (same tasks, same evaluation)
- Ṛta (same interface)
- Text feedback contract (format unchanged)
- Information boundary (preserved)
- Authority separation (preserved)

---

## 23. Files Created

| File | Content |
|------|---------|
| `research/implementation/EGER-C1-PROTOCOL-CHANGE-ASSESSMENT-001.md` | This assessment |

## 24. Files Modified

```
No tracked files modified.
New untracked documentation files from P017-P021:
  EGER-C1-READINESS-001.md
  EGER-C1-TEXT-FEEDBACK-CONTRACT-001.md
  EGER-C1-TEXT-FEEDBACK-CONTRACT-001-R1.md
  EGER-C1-CAUSAL-MECHANISM-RECONCILIATION-001.md
  EGER-C1-PROTOCOL-CHANGE-ASSESSMENT-001.md
```

## 25. C1 Execution

**C1 EXECUTED = NO**

## 26. Ṛta

**MODIFIED = NO**

## 27. GitHub

**PUSHED = NO**

## 28. FINAL STATUS

**CHANGE-CONTROL DECISION READY — HUMAN APPROVAL REQUIRED**

The move from single-shot to feedback-assisted revision requires formal change control (EGER-CHANGE-001 + EXP-001 v0.2). Budget, benchmark, model, and oracle are unaffected. The protocol clarification is scientifically justified and necessary.

---

*This assessment is PROPOSED — AWAITING HUMAN APPROVAL. Once approved, EGER-CHANGE-001 may be created and EXP-001 may be updated to v0.2.*
