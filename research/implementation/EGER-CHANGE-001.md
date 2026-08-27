# EGER-CHANGE-001 — C1 Protocol Clarification: Feedback-Assisted Revision

| Field | Value |
|-------|-------|
| ID | EGER-CHANGE-001 |
| Date | 2026-08-26 |
| Type | Experimental protocol clarification |
| Status | **APPROVED — human-authorized change control** |
| Trigger | Scientific inconsistency discovered during C1 protocol design (P019–P020) |
| Human authorization | Explicit — P022 directive |

---

## 1. Purpose

Formally record the approved C0→C1 protocol change identified through the C1 design process (P017–P021). This change clarifies the C1 execution mechanism from an ambiguous protocol definition to a precise, reproducible experimental procedure.

**This is a protocol clarification, not a new experimental variable.**

---

## 2. Trigger / Source Records

| Record | Contribution |
|--------|-------------|
| EGER-P017 (C1 Readiness) | Identified B-1: C1 text feedback format undefined |
| EGER-P018 (Text Feedback Contract) | Proposed three candidate designs; Option A selected |
| EGER-P019 (Contract Closure) | Closed ODQ-1/2/3; introduced single-shot contradiction |
| EGER-P020 (Causal Mechanism Reconciliation) | Identified P019 contradiction; recommended Interpretation B |
| EGER-P021 (Protocol Change Assessment) | Determined EGER-CHANGE-### required; classified change |
| EGER-P022 (This record) | Human-authorized formal change-control record |

---

## 3. Previous C1 Definition

### What EXP-001 v0.1 §6 Says

> **C1**: + textual tool feedback (deterministic oracle output rendered as text)

### What EXP-001 v0.1 §7 (Capability Matrix) Shows

| Capability | C0 | C1 |
|------------|----|----|
| Candidate generation | ✓ | ✓ |
| Text feedback | - | ✓ |

### What the Protocol Does NOT Specify

- Whether the Engineer revises its candidate after receiving feedback
- Whether C1 uses one model call or two
- Whether the initial candidate or the revised candidate is the measured artifact
- Whether the oracle evaluates the revised candidate

**The original protocol was AMBIGUOUS about the C1 execution mechanism.**

---

## 4. Problem with Previous Definition

P019 attempted to resolve the ambiguity with a "single-shot" interpretation:

```
LLM (1 call)
  ↓
CANDIDATE
  ↓
ORACLE
  ↓
TEXT FEEDBACK
  ↓
END
```

With constraint: "One model call. No second model call."

**This is scientifically vacuous.** The feedback arrives after the model has finished generating. The measured artifact was produced without feedback influence. C1 would measure the same thing as C0.

However, P019 also stated: "produce a revised SDC candidate" — which necessarily requires another model generation. These two statements are incompatible.

---

## 5. New C1 Definition

### Feedback-Assisted Revision

```
LLM (call 1)
  ↓
INITIAL CANDIDATE
  ↓
ORACLE (evaluates initial candidate)
  ↓
TEXT FEEDBACK (deterministic rendering per C1 text feedback contract)
  ↓
LLM (call 2 — revision)
  ↓
FINAL CANDIDATE (measured artifact)
  ↓
ORACLE (evaluates revised candidate — measurement)
```

### What Each Step Does

| Step | Component | Purpose | Classification |
|------|-----------|---------|----------------|
| 1 | LLM call 1 | Generate initial proposal | Treatment baseline |
| 2 | Oracle call 1 | Evaluate initial candidate | Treatment mechanism |
| 3 | Text feedback | Render deterministic findings | Treatment information |
| 4 | LLM call 2 | Revise candidate based on feedback | Treatment mechanism |
| 5 | Oracle call 2 | Evaluate revised candidate | Measurement |

---

## 6. Scientific Rationale

### Why This Change Is Necessary

The original protocol asked: "Does feedback representation measurably change reliability?"

For this question to be testable, the feedback must have a **causal pathway** to the measured artifact. Under the single-shot interpretation, the feedback arrives after the model finishes — no causal pathway exists.

Under feedback-assisted revision:
1. The Engineer proposes a candidate (same as C0)
2. The oracle evaluates it and generates deterministic text feedback
3. The Engineer reads the feedback and revises its candidate
4. The revised candidate is the measured artifact

This creates a clear causal pathway: **feedback → revision → outcome.**

### Why the Revision Call Is Not a Confound

The revision call is an **inherent component of the treatment**, not an additional variable.

The treatment is defined as "feedback-assisted revision." Revision inherently requires a model call. Without the revision call, there is no treatment to measure.

**Analogy:** A drug trial where the treatment is "drug + monitoring" — the monitoring visits are part of the treatment protocol, not a confound.

### What IS a Confound (and Does Not Occur)

- Changing the model between calls
- Changing the temperature
- Adding oracle capabilities beyond feedback generation
- Introducing a second probabilistic component

None of these occur in C1.

---

## 7. Independent Variable

**C1 Treatment:** Access to deterministic oracle text feedback during proposal revision.

This decomposes into:
- **Feedback availability:** Engineer receives deterministic text feedback
- **Revision opportunity:** Engineer may revise its proposal based on feedback
- **Single revision:** Only one feedback-revision cycle (not iterative convergence)

The independent variable is **redefined, not added.** P020's IV is a more precise and scientifically meaningful version of the original protocol's intent. The original protocol said "text feedback" — P020 specifies how that feedback is used.

---

## 8. C0→C1 Causal Pathway

```
C0:
  LLM → candidate → [END]
  (no feedback, no revision)

C1:
  LLM → initial candidate
  ORACLE → feedback
  LLM → revised candidate
  ORACLE → measurement
  (feedback → revision → outcome)
```

### What Remains Constant

| Aspect | C0 | C1 | Changed? |
|--------|----|----|----------|
| Model identity | MODEL-002 | MODEL-002 | NO |
| Model parameters | temp 0.0, top_p 1.0 | temp 0.0, top_p 1.0 | NO |
| Benchmark | BENCH-002 v0.1 | BENCH-002 v0.1 | NO |
| Task order | BENCH2-001..006 | BENCH2-001..006 | NO |
| Task inputs | engineer_visible | engineer_visible | NO |
| Oracle | Ṛta 3b5c2f2 | Ṛta 3b5c2f2 | NO |
| Oracle configuration | Frozen | Frozen | NO |
| Evaluator | Same | Same | NO |
| Scoring | Same | Same | NO |
| Information boundary | C0 boundary | C0 + text feedback | **YES** |
| Text feedback | None | Per C1 contract | **YES** |

---

## 9. Model-Call Change

| Resource | C0 Actual | C1 Actual | Budget | Within? |
|----------|-----------|-----------|--------|---------|
| Model calls | 1 | 2 | 5 | YES |
| Oracle calls | 0 (evaluator-side) | 2 | 5 | YES |
| Max iterations | 1 | 1 | 5 | YES |

**No MODEL-002 modification required.** The budget accommodates 2 model calls and 2 oracle calls.

However, the model-call count is an **execution-resource difference inherent to the feedback-assisted revision treatment** and must be reported in the C1 results.

---

## 10. Oracle-Call Change

| Call | Purpose | Classification |
|------|---------|----------------|
| Oracle call 1 | Evaluate initial candidate → generate text feedback | **Treatment mechanism** |
| Oracle call 2 | Evaluate revised candidate → measure outcome | **Measurement** |

Both calls are scientifically necessary:
- Call 1 is the treatment (generates feedback)
- Call 2 is measurement (evaluates the outcome)

Without call 2, we cannot compare C1 artifact quality to C0 using the same oracle evaluation.

---

## 11. Primary Artifact Definition

**The primary experimental artifact is: the final revised SDC candidate after receiving deterministic oracle text feedback.**

| Artifact | Classification | Purpose |
|----------|---------------|---------|
| Initial candidate | Intermediate | Revision-magnitude analysis |
| First oracle evidence | Treatment | Generates feedback |
| Text feedback | Treatment | Information presented to Engineer |
| Final revised candidate | **Primary outcome** | C0 vs C1 comparison |
| Final oracle evidence | Measurement | Evaluates outcome |

The initial candidate is retained for within-condition diagnostic comparison but is not the primary measured outcome.

---

## 12. Secondary / Diagnostic Comparisons

| Comparison | Purpose |
|------------|---------|
| C0 final artifact vs. C1 final artifact | **Primary:** Does feedback-assisted revision improve outcome? |
| C1 initial vs. C1 final | **Secondary:** How much revision occurred? |
| C0 final vs. C1 initial | **Diagnostic:** Are first proposals consistent across conditions? |

---

## 13. C1 Text-Feedback Boundary

The Engineer may receive:
1. Oracle execution status
2. Evidence scope
3. Scope limitation text
4. Findings (severity/code/message/line)

The Engineer MUST NOT receive:
- Evaluator-only answers
- Expected solutions
- Research canon
- Other benchmark tasks
- Git history
- Ṛta source
- Structured EvidenceArtifact
- Epistemic state
- Authorization decisions
- Hidden labels

---

## 14. Authority Separation

```
PROPOSAL AUTHORITY:    LLM (call 1: initial, call 2: revision)
EVIDENCE AUTHORITY:    Oracle (evaluates + generates feedback)
EPISTEMIC STATE:       Not active in C1
AUTHORIZATION:         Not active in C1
```

P7 preserved. No authority leakage.

---

## 15. Confound-Monitoring Implications

### CM-1 through CM-7 Under Feedback-Assisted Revision

| Indicator | Observable in C1? | Notes |
|-----------|-------------------|-------|
| CM-1: Recovery from specific finding | YES | Engineer sees SDC-xxx, may address in revision |
| CM-2: Correction of known error | YES | Engineer may fix errors identified by oracle |
| CM-3: Response to INSUFFICIENT | YES | Engineer sees scope limitation, may react |
| CM-4: Unchanged after non-actionable | YES | Info findings may produce no change |
| CM-5: Improvement from evidence | YES | Compare initial vs. revised candidate |
| CM-6: New errors introduced | YES | Compare initial vs. revised evidence |
| CM-7: Convergence attempt | PARTIAL | Single revision, not iterative convergence |

**CM-1 through CM-6 become observable under feedback-assisted revision.** This is a significant improvement in confound-monitoring capability.

**CM-7 requires definition update** for the single-revision C1 context. Instead of measuring iterative convergence (which requires C3+), measure whether the Engineer's revision moves the candidate toward a state that the oracle would evaluate more favorably.

---

## 16. Benchmark Impact

**None.** BENCH-002 remains frozen. Same tasks, same evaluation, same engineer-visible inputs.

---

## 17. MODEL-002 Impact

**None.** Same model, same parameters, same prompt. Budget accommodates 2 calls.

---

## 18. Ṛta Impact

**None.** Same oracle interface. Two calls use the same interface as one.

---

## 19. Reproducibility Implications

Run manifest schema requires extension:

| Artifact | Schema Update |
|----------|--------------|
| Initial candidate | Record `candidate_v1.json` |
| First oracle evidence | Record `evidence_initial.json` |
| Text feedback | Record `text_feedback.txt` |
| Final candidate | Record `candidate_final_v1.json` |
| Final oracle evidence | Record `evidence_final.json` |
| Model call IDs | Record `call_1_id`, `call_2_id` |
| Oracle call IDs | Record `call_1_id`, `call_2_id` |

This is a **documentation/schema change**, not an experimental change.

---

## 20. Manifest / Schema Implications

EXP-001 v0.2 run manifest must record:
- `initial_candidate_hash`
- `initial_oracle_evidence_hash`
- `text_feedback_hash`
- `final_candidate_hash`
- `final_oracle_evidence_hash`
- `model_calls: 2`
- `oracle_calls: 2`

---

## 21. Required Implementation Work

| Item | Classification | Priority |
|------|---------------|----------|
| EGER-CHANGE-001 (this document) | Change-control record | REQUIRED |
| EXP-001 v0.2 (C1 clarification) | Protocol version update | REQUIRED |
| C1 text feedback contract (R1) | Already defined | COMPLETE |
| Run manifest schema extension | Documentation | REQUIRED before C1 |
| C1 runner implementation | Implementation | REQUIRED before C1 |
| CM-7 definition update | Protocol | REQUIRED before C1 |

---

## 22. Explicitly Unauthorized Actions

This change-control record does NOT authorize:

- C1 implementation
- C1 execution
- BENCH-002 modification
- MODEL-002 modification
- Ṛta modification
- GitHub push
- Subagent creation
- C2–C5 design
- Research contract modification

---

## 23. Relationship to C0 Frozen Baseline

**C0 remains exactly as executed.** C0 did NOT expose oracle feedback to the LLM. C0 remains the baseline condition.

Do not rewrite C0 as if it used feedback or revision.

---

## 24. Change-Control Classification

**Classification: C. EGER-CHANGE-### REQUIRED**

The move from ambiguous single-shot to feedback-assisted revision constitutes a formal experimental protocol change because:

1. Independent variable redefined (clarified)
2. Primary measured artifact changed (initial → final revised candidate)
3. Execution mechanism changed (1 model call → 2)
4. Oracle interaction changed (0 evaluator-side → 2 in-run)
5. Run manifest schema requires extension
6. CM-7 requires definition update

---

## 25. Approval Status

**APPROVED** — human-authorized via EGER-P022 directive.

---

## 26. Next Authorized Step

**C1 implementation readiness verification** — verify that the C1 runner can execute the feedback-assisted revision pipeline within the frozen protocol.

---

## 27. Non-Decisions

This change-control record does NOT decide:

- C1 experimental outcome
- C1 performance metrics
- H1 validity for C1
- C0→C1 improvement
- Confound presence or absence
- C2–C6 design

---

## 28. Contract / Principle References

| Reference | Relevance |
|-----------|-----------|
| RESEARCH.md §5 | Secondary research question: "Does feedback representation measurably change reliability?" |
| EXP-001 v0.1 §6 | C1 definition: "+ textual tool feedback" |
| EXP-001 v0.1 §13 | Budget: max_model_calls = 5, max_oracle_calls = 5 |
| ARCH-002 condition deltas | C0→C1 adds oracle execution + text rendering |
| P5 — Repetition Drives Convergence | "Iteration with feedback is the mechanism under study" |
| P7 — Authority Separation | Proposal ≠ Evidence ≠ Epistemic ≠ Authorization |
| P8 — Research Traceability | Every material decision receives persistent provenance |
| DEC-005 | One probabilistic component for C0–C5 |
| DEC-006 | rta_generate forbidden |

---

*This change-control record is APPROVED — human-authorized. C0 remains frozen. C1 implementation and execution require separate authorization.*
