# EGER-P027 — C1→C2 Scientific Readiness & Model-Responsiveness Decision

| Field | Value |
|-------|-------|
| ID | EGER-P027 |
| Date | 2026-08-26 |
| Type | Strictly read-only scientific decision analysis |
| Predecessor | EGER-C1-EXECUTION-REVIEW-001 |
| Status | **DECISION ANALYSIS COMPLETE — HUMAN DECISION REQUIRED** |

---

## 1. Executive Summary

**C1 established that the EGER feedback pipeline works correctly but the current `LiveEngineerModel` cannot process feedback. C2 with the same model would face the identical limitation. The recommended path is to establish a feedback-responsive model condition before continuing the primary ablation.**

---

## 2. Current Scientific State

```
C0                         ✓ COMPLETE (canned model, 1 call)
C1                         ✓ COMPLETE (canned model, 2 calls, identical candidates)
C1 pipeline                ✓ VALID
C1 feedback delivery       ✓ VERIFIED
C1 treatment effect        ✗ NOT IDENTIFIABLE (model limitation)
C2                         ✗ NOT EXECUTED
C3–C5                      ✗ NOT EXECUTED
MODEL-002                  ✓ FROZEN (canned proxy)
BENCH-002                  ✓ FROZEN
Ṛta                        ✓ UNTOUCHED
```

---

## 3. Central Decision

Should EGER:
- **Option A:** Proceed to C2 using the current MODEL-002?
- **Option B:** Establish a feedback-responsive model condition first?

---

## 4. Important Distinction

| Question | C1 Answer |
|----------|-----------|
| Can EGER deliver feedback? | ✅ YES |
| Can the model process feedback? | ❌ NOT OBSERVABLE (canned model) |
| Does feedback improve proposals? | ✗ NOT ANSWERED |

**These are three separate questions. C1 answered only the first.**

---

## 5. C2 Purpose (from EXP-001 v0.2 §6)

C2 adds **structured `EvidenceArtifact`** (scope, findings, provenance) instead of text feedback.

| Aspect | C2 Definition |
|--------|--------------|
| Independent variable | Structured evidence (EvidenceArtifact) |
| Treatment | Engineer receives structured EvidenceArtifact |
| Control/baseline | C0 (no evidence) |
| Causal pathway | Evidence → Engineer processes → candidate changes → measurable outcome |
| Required model behavior | Engineer must meaningfully consume structured evidence |
| Primary artifact | Final revised candidate |
| Information boundary | Engineer receives EvidenceArtifact (scope, findings, provenance) |

### C2 Pipeline (from contract)

```
LLM (call 1) → initial candidate
ORACLE → EvidenceArtifact
LLM (call 2) → revised candidate (informed by structured evidence)
ORACLE → measurement
```

**C2 requires the Engineer to meaningfully consume structured evidence.**

---

## 6. Model-Responsiveness Dependency

### Question: Can C2 produce an interpretable result with the current MODEL-002?

**Answer: NO.**

### Reasoning

The current `LiveEngineerModel` selects output based on **task ID presence in the prompt**. It does NOT examine:
- `evidence_summary` (text feedback in C1)
- `existing_sdc` (initial candidate)
- Any structured evidence (would be added in C2)

If C2 passes an `EvidenceArtifact` to the model, the model will still produce the same canned output because it only looks for the task ID.

### Consequence

C2 with the current model would:
- ✅ Validate the C2 pipeline (structured evidence transport)
- ✅ Validate information boundaries
- ❌ NOT measure whether structured evidence changes proposals
- ❌ NOT answer the C2 research question
- ❌ Produce identical candidates for all 6 tasks (same as C1)

**C2 would be a valid infrastructure test but NOT a valid treatment-effect test.**

---

## 7. Causal Identifiability

### C2 Required Causal Pathway

```
C2 treatment (structured evidence)
  → Engineer processes evidence
  → candidate changes
  → measurable outcome changes
```

### Link Analysis with Current Model

| Link | Status | Reason |
|------|--------|--------|
| Evidence delivered to model | OBSERVABLE | Pipeline works (C1 verified) |
| Engineer processes evidence | NOT OBSERVABLE | Canned model doesn't process prompt content |
| Candidate changes | NOT OBSERVABLE | Output selected by task ID |
| Outcome changes | NOT OBSERVABLE | Same candidate → same outcome |

**C2 causal pathway is NOT IDENTIFIABLE with the current model.**

---

## 8. Model Behavior Classification

The current model behavior is:

- **NOT a confound** — it doesn't systematically vary with treatment
- **NOT a protocol violation** — the model interface is correct
- **NOT an implementation defect** — the model works as designed

It IS:
- **A treatment non-activation** — the model cannot process the treatment input
- **A measurement limitation** — the model's output cannot reflect treatment effects
- **An experimental-condition limitation** — the canned model is not suitable for treatment-effect testing

---

## 9. C0, C1, C2 Comparability

### C0

```
LLM → candidate → oracle
```
- Model calls: 1
- Oracle calls: 0 (evaluator-side)
- Evidence exposure: None
- Primary artifact: Single candidate
- Treatment effect measurable: N/A (no treatment)

### C1

```
LLM → candidate → oracle → text feedback → LLM → revised candidate → oracle
```
- Model calls: 2
- Oracle calls: 2
- Evidence exposure: Text feedback
- Primary artifact: Revised candidate
- Treatment effect measurable: NO (canned model)

### C2 (proposed)

```
LLM → candidate → oracle → EvidenceArtifact → LLM → revised candidate → oracle
```
- Model calls: 2
- Oracle calls: 2
- Evidence exposure: Structured EvidenceArtifact
- Primary artifact: Revised candidate
- Treatment effect measurable: NO (same canned model)

### Comparability Assessment

| Comparison | Interpretable? | Reason |
|------------|---------------|--------|
| C0 vs C1 | YES (infrastructure) | Same model, same output, different pipeline |
| C0 vs C2 | YES (infrastructure) | Same model, same output, different evidence format |
| C1 vs C2 | YES (infrastructure) | Same model, different evidence format |
| Treatment effect (any) | NO | Canned model cannot process evidence |

---

## 10. Two Research Tracks

### Track 1 — Architecture-First (Proceed to C2)

| Aspect | Assessment |
|--------|-----------|
| Purpose | Validate C2 pipeline, structured evidence transport, information boundaries |
| Scientific benefit | Infrastructure validation for C2 layer |
| Limitation | Treatment effect remains unidentifiable |
| Risk | Low (no model change, clean comparability) |
| Authorization | C2 execution authorization |
| Preserves C1 | ✅ |

### Track 2 — Treatment-First (Establish Responsive Model)

| Aspect | Assessment |
|--------|-----------|
| Purpose | Make evidence consumption observable, enable causal treatment testing |
| Scientific benefit | Would make C0→C1→C2→C3→C4→C5 treatment effects identifiable |
| Limitation | Changes MODEL-002; reduces direct comparability with C0/C1 canned results |
| Risk | Medium (model change requires change control, new experiment version) |
| Authorization | EGER-CHANGE-### + EXP-001 v0.3 |
| Preserves C1 | ✅ (canned result preserved as historical) |

### Track Comparison

| Criterion | Track 1 | Track 2 |
|-----------|---------|---------|
| Causal identifiability | NO | YES |
| Infrastructure validation | YES | YES |
| C0 comparability | HIGH | MODERATE |
| C1 comparability | HIGH | MODERATE |
| Scientific value | LIMITED | HIGH |
| Implementation risk | LOW | MEDIUM |
| Time to treatment-effect result | LONGER (must revisit later) | SHORTER (direct) |

---

## 11. Model Change Requirements

Replacing the current model would constitute:

| Classification | Required |
|---------------|----------|
| MODEL-002 modification | YES — new behavioral model |
| New model condition | YES — different responsiveness property |
| New experimental condition | Potentially — depends on design |
| EGER-CHANGE-### | YES — formal change control |
| New experiment version | YES — v0.3 |
| Explicit authorization | YES — human decision |

---

## 12. Non-Binding Proposal: Feedback-Responsive Model Condition

### Required Behavioral Property

> The EngineerModel must condition its second proposal on the supplied deterministic evidence/feedback rather than selecting output solely from task identity.

### Verification Requirements

Before such a model could be used scientifically:

| Requirement | Purpose |
|-------------|---------|
| Prompt responsiveness test | Verify model processes full prompt including evidence |
| Deterministic configuration | Temperature=0.0 for reproducibility where possible |
| Identical task context | Same task inputs across conditions |
| Explicit feedback exposure | Evidence passed to model, not ignored |
| No evaluator access | Model cannot see expected answers |
| No hidden research context | Model receives only task information |
| No additional agents | Single probabilistic component |
| No unauthorized tools | Same tool restrictions as C0/C1 |

### Minimum Model Responsiveness Test

**Purpose:** Establish whether a candidate model can respond to feedback.

**Design:**

```
Test A: Same task + no feedback → Candidate_A
Test B: Same task + meaningful deterministic feedback → Candidate_B

If Candidate_A ≠ Candidate_B: model is feedback-responsive
If Candidate_A = Candidate_B: model is not feedback-responsive
```

**This is a capability/readiness test, NOT the EGER treatment experiment.**

---

## 13. C2 Scientific Validity Under Current Model

**Classification: VALID INFRASTRUCTURE EXPERIMENT — TREATMENT EFFECT NOT IDENTIFIABLE**

C2 with the current model would:
- ✅ Validate the C2 structured-evidence pipeline
- ✅ Validate information boundaries for EvidenceArtifact
- ✅ Produce reproducible infrastructure results
- ❌ NOT measure whether structured evidence improves proposals
- ❌ NOT answer the C2 research question

---

## 14. Recommendation

**Option B: Establish a feedback-responsive model condition first.**

### Rationale

1. **Causal identifiability** — The primary EGER hypothesis tests whether evidence improves reliability. Without a responsive model, no condition (C1–C5) can measure treatment effects.

2. **Scientific efficiency** — Establishing model responsiveness once benefits all subsequent conditions (C1–C5), not just C2.

3. **Contract compliance** — The research question asks "Can engineering-agent reliability be improved by separating authorities?" This requires a model that can actually respond to the evidence provided.

4. **Provenance preservation** — C1 (canned model) remains as a valid infrastructure finding. A new model condition would be a separate experiment, not a replacement.

5. **Research integrity** — Proceeding to C2–C5 with a non-responsive model would produce a series of infrastructure validations without answering the research question.

### What This Means

- C1 (canned model) is PRESERVED as a valid pipeline/infrastructure result
- A new model condition would be established under formal change control
- C0/C1 canned results remain as historical baseline
- The responsive-model condition would be tested before C2–C5 execution
- This is NOT a model "upgrade" — it's a different experimental condition

---

## 15. What We Should NOT Do

| Action | Acceptable? | Reason |
|--------|-------------|--------|
| Silently replace MODEL-002 | ❌ NO | Violates frozen contract |
| Rerun C1 with another model without change control | ❌ NO | Protocol violation |
| Edit C1 results | ❌ NO | Destroys provenance |
| Delete identical initial/final candidates | ❌ NO | Destroys evidence |
| Treat C1 as proof feedback is ineffective | ❌ NO | Model limitation, not evidence |
| Treat C1 as proof feedback works | ❌ NO | Treatment not activated |
| Proceed to C2 ignoring model non-responsiveness | ❌ NO | Same limitation applies |
| Change benchmark tasks to make model respond | ❌ NO | Anti-gaming violation |

---

## 16. Research Value from C1

| Lesson | Implication for C2+ |
|--------|-------------------|
| EGER feedback pipeline is operational | C2 structured-evidence pipeline can be built on same infrastructure |
| Deterministic evidence can be rendered and delivered | Text and structured evidence rendering both work |
| Model responsiveness must be separately verified | Pre-experiment responsiveness test required |
| Treatment cannot be inferred from treatment delivery | Delivery ≠ activation ≠ effect |
| Infrastructure correctness ≠ treatment effectiveness | These are separate research questions |

---

## 17. Decision Table

| Question | Current MODEL-002 | Feedback-responsive model |
|----------|-------------------|--------------------------|
| Feedback delivery | ✅ YES | ✅ YES |
| Structured evidence delivery | ✅ YES | ✅ YES |
| Output responsiveness | ❌ NO (task-ID driven) | ✅ REQUIRED |
| Treatment activation | ❌ NO | ✅ YES |
| Causal effect identifiable | ❌ NO | ✅ YES |
| C0 comparability | ✅ HIGH (same model) | ⚠️ MODERATE (different model) |
| C1 comparability | ✅ HIGH (same model) | ⚠️ MODERATE (different model) |
| Change-control requirement | ✅ NONE | ❌ EGER-CHANGE-### required |
| Scientific value | ⚠️ LIMITED (infrastructure only) | ✅ HIGH (treatment testing) |
| Main risk | ⚠️ No treatment effect | ⚠️ Model change reduces comparability |

---

## 18. Final Verdict

### C1 Status

**VALID PIPELINE / INFRASTRUCTURE RESULT — TREATMENT EFFECT NOT IDENTIFIABLE**

### C2 Status (with current model)

**VALID INFRASTRUCTURE EXPERIMENT — TREATMENT EFFECT NOT IDENTIFIABLE**

### Recommended Path

**Establish a feedback-responsive model condition under formal change control before C2–C5 execution.**

### MODEL-002 Status

FROZEN — remains unchanged until formal change control.

### BENCH-002 Status

FROZEN — remains unchanged.

### Ṛta Status

UNTOUCHED — remains unchanged.

### C2 Execution Status

**NOT AUTHORIZED** — pending model-condition decision.

---

## 19. Exact Next Authorized Step

**Human decision required:**

> Should EGER establish a feedback-responsive experimental model condition under formal change control before proceeding to C2–C5?

If YES:
→ `EGER-CHANGE-002` — Model-condition change control
→ `EGER-P028` — Model responsiveness readiness test design

If NO (proceed to C2 with current model):
→ `EGER-AUTH-003` — C2 execution authorization (infrastructure only)

---

*This decision analysis is COMPLETE. Human decision required before any further action.*
