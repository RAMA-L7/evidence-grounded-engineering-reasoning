# EGER-P136 — EGER Evidence-to-Architecture Synthesis Design

## Phase
P136 — Read-Only Architecture Design Gate

## Date
2026-09-01

## Status
**ARCHITECTURE SYNTHESIS COMPLETE — READY FOR IMPLEMENTATION DESIGN**

---

## 1. Executive Summary

The EGER empirical phase (C0–C1/C2, RQ-4) has established that:

1. **Structured evidence reliably activates proposal revision** (100% activation)
2. **ERROR adherence depends on task framing** (A1 = 24/24 = 100% vs A4 = 16/24 = 67%)
3. **Deterministic verification provides the ground truth** for engineering correctness
4. **Authority separation is architecturally necessary** — the LLM must not verify its own proposals

This document translates these findings into a minimal, evidence-grounded EGER architecture. The architecture is designed around **what the evidence actually supports**, not around the original C0–C5 ablation plan.

---

## 2. Evidence Boundary

### What the Evidence Supports

| Finding | Classification | Evidence |
|---------|---------------|----------|
| Structured evidence causes revision | **ESTABLISHED** | 100% activation across all experiments |
| ERROR adherence is task-dependent | **ESTABLISHED** | BASE varies 25–100% across tasks |
| Broader framing improves adherence | **STRONG SIGNAL** | A1 = 24/24 vs A4 = 16/24 |
| Technical content improves adherence | **SUPPORTED SIGNAL** | A2 = 20/23 vs A4 = 16/24 |
| Deterministic verification is authoritative | **ESTABLISHED** | Oracle provides ground truth for ERROR findings |
| Authority separation is necessary | **ESTABLISHED** | LLM cannot verify its own proposals (P7) |

### What the Evidence Does NOT Support

| Claim | Status |
|-------|--------|
| Framing causally determines adherence | NOT ESTABLISHED |
| Model epistemic uncertainty causes failures | NOT ESTABLISHED |
| Epistemic-state intervention improves reliability | NOT JUSTIFIED |
| Effect generalizes beyond MODEL-005 | NOT ESTABLISHED |
| Deterministic routing reduces invalid actions | NOT TESTED |
| Authorization gate prevents regressions | NOT TESTED |

---

## 3. Architecture Principles

The EGER architecture is grounded in these principles, derived from both the Research Contract v0.2 and the empirical evidence:

### P1 — No Unverified State Transition

**Empirical support:** C0 showed that without deterministic validation, proposals remain unverified. The Oracle provides the verification boundary.

**Architecture implication:** Every engineering state transition must pass through deterministic verification.

### P7 — Authority Separation

**Empirical support:** The research consistently separated LLM proposal generation from Oracle verification. The LLM proposes; the Oracle verifies.

**Architecture implication:** The LLM has PROPOSAL authority only. The Oracle has EVIDENCE authority. The system has AUTHORIZATION authority.

### P4 — Executable Engineering Checklist

**Empirical support:** The Oracle's deterministic checks provided the evidence that structured feedback activates revision.

**Architecture implication:** Engineering rules are executable checks, not prose suggestions.

### P3 — Evidence-Conditioned Reasoning

**Empirical support:** Structured evidence feedback improved revision quality compared to no feedback.

**Architecture implication:** When deterministic evidence identifies a condition, route behavior through an appropriate procedure.

### Framing Insight (from RQ-4)

**Empirical support:** Broader task framing improved adherence (A1 = 24/24 = 100%).

**Architecture implication:** Task definition should use broader, production-quality framing rather than narrow, specific constraints.

---

## 4. Minimal EGER Architecture

The smallest architecture justified by current evidence:

```
┌─────────────────────────────────────────────────────────┐
│                    TASK DEFINITION                       │
│  Broad/production-quality objective                     │
│  Design context                                         │
│  Engineering constraints                                │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    LLM PROPOSAL                          │
│  Single probabilistic component                         │
│  Generates candidate SDC                                 │
│  PROPOSAL AUTHORITY ONLY                                 │
│  Cannot verify its own output                           │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              DETERMINISTIC ORACLE                        │
│  Ṛta constraint intelligence                            │
│  EXECUTABLE CHECKS                                       │
│  Produces structured findings                           │
│  EVIDENCE AUTHORITY                                      │
│  Cannot generate proposals                              │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              STRUCTURED EVIDENCE                         │
│  ERROR / WARNING / INFO findings                        │
│  Evidence-conditioned scope                             │
│  Deterministic representation                           │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              REVISION LOOP                               │
│  LLM receives structured evidence                      │
│  LLM revises proposal                                   │
│  Oracle re-evaluates                                    │
│  Loop until: verified / rejected / budget exhausted     │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              VERIFICATION GATE                           │
│  Deterministic acceptance criteria                      │
│  All ERROR findings resolved?                           │
│  No unauthorized modifications?                         │
│  AUTHORIZATION AUTHORITY                                 │
│  Cannot generate proposals or evidence                  │
└───────────────────────┬─────────────────────────────────┘
                        ↓
                ACCEPT / REJECT
```

### Component Justification

| Component | Evidence Support | Classification |
|-----------|-----------------|---------------|
| Broad task framing | A1 = 24/24 = 100% | **EMPIRICALLY SUPPORTED** |
| LLM proposal generation | 100% activation across all experiments | **EMPIRICALLY SUPPORTED** |
| Structured evidence feedback | C1/C2 established | **EMPIRICALLY SUPPORTED** |
| Deterministic Oracle boundary | P1, P4, P7 principles + experimental evidence | **EMPIRICALLY SUPPORTED** |
| Revision loop | C1 established (model revises in response to feedback) | **EMPIRICALLY SUPPORTED** |
| Verification gate | P1 principle (no unverified state transition) | **ENGINEERING DESIGN CHOICE** |
| Authority separation | P7 principle + experimental design | **ENGINEERING DESIGN CHOICE** |
| Evidence-conditioned routing | P3 principle | **ENGINEERING DESIGN CHOICE** |

---

## 5. Extended EGER Architecture

The full architecture, including components that are engineering design choices (not experimentally proven):

```
┌─────────────────────────────────────────────────────────┐
│                    TASK DEFINITION                       │
│  Broad/production-quality objective                     │
│  Design context                                         │
│  Engineering constraints                                │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    LLM PROPOSAL                          │
│  Single probabilistic component                         │
│  Generates candidate SDC                                 │
│  PROPOSAL AUTHORITY ONLY                                 │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              DETERMINISTIC ORACLE                        │
│  Ṛta constraint intelligence                            │
│  Produces structured findings                           │
│  EVIDENCE AUTHORITY                                      │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              STRUCTURED EVIDENCE                         │
│  ERROR / WARNING / INFO findings                        │
│  Deterministic representation                           │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│        EVIDENCE-CONDITIONED ROUTING (C4)                │
│  Deterministic routing table                            │
│  Maps finding codes to procedures                       │
│  ENGINEERING DESIGN CHOICE — not experimentally tested  │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              REVISION LOOP                               │
│  LLM receives structured evidence                      │
│  LLM revises proposal                                   │
│  Oracle re-evaluates                                    │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│        AUTHORIZATION GATE (C5)                          │
│  Non-bypassable verification                            │
│  Deterministic acceptance criteria                      │
│  AUTHORIZATION AUTHORITY                                 │
│  ENGINEERING DESIGN CHOICE — not experimentally tested  │
└───────────────────────┬─────────────────────────────────┘
                        ↓
                ACCEPT / REJECT
```

### Extended Component Justification

| Component | Evidence Support | Classification |
|-----------|-----------------|---------------|
| Evidence-conditioned routing (C4) | P3 principle | **ENGINEERING DESIGN CHOICE** |
| Authorization gate (C5) | P1 principle | **ENGINEERING DESIGN CHOICE** |
| Epistemic state (C3) | NOT JUSTIFIED | **DEFERRED HYPOTHESIS** |

---

## 6. Component-by-Component Justification

### 6.1 Task Definition with Broad Framing

**What:** The task is defined using broader, production-quality framing rather than narrow, specific constraints.

**Evidence:** A1 (broad framing only) = 24/24 = 100% adherence. A4 (narrow baseline) = 16/24 = 67%.

**Classification:** EMPIRICALLY SUPPORTED — strongest behavioral signal in the research.

**Implementation:**
```python
task_objective = (
    "Generate a complete, production-quality SDC for this design. "
    "Include all required timing constraints: clock definitions, "
    "input/output delays, and any applicable exceptions."
)
```

**Caveat:** This is a strong behavioral signal, not proven causality. The effect may be model-specific (MODEL-005 only).

### 6.2 LLM Proposal Generation

**What:** A single LLM generates candidate SDC proposals.

**Evidence:** Proposal activation is near-universal (100% across all experiments). The model reliably responds to structured feedback.

**Classification:** EMPIRICALLY SUPPORTED.

**Authority:** PROPOSAL ONLY. The LLM cannot:
- Verify its own proposals
- Modify evidence
- Authorize state transitions
- Override the Oracle

### 6.3 Structured Evidence Feedback

**What:** The Oracle produces structured findings (ERROR/WARNING/INFO) that are fed back to the LLM.

**Evidence:** C1/C2 established that structured evidence reliably activates revision. The model revises its proposal in response to structured feedback.

**Classification:** EMPIRICALLY SUPPORTED.

**Schema:**
```json
{
  "findings": [
    {
      "severity": "error",
      "rule": "missing_input_delay",
      "message": "No input delay constraint found",
      "scope": "ports[data_in*]"
    }
  ],
  "summary": {
    "error_count": 2,
    "warning_count": 1,
    "info_count": 0
  }
}
```

### 6.4 Deterministic Oracle Boundary

**What:** The Oracle (Ṛta) provides deterministic verification. It cannot generate proposals.

**Evidence:** P1 (No Unverified State Transition) and P4 (Executable Engineering Checklist) require a deterministic verification boundary. The Oracle's findings are the ground truth for engineering correctness.

**Classification:** ENGINEERING DESIGN CHOICE — supported by principles P1/P4, not by direct experimental comparison.

**Invariant:** The Oracle never generates SDC candidates (`rta_generate` is forbidden per EGER-DEC-006).

### 6.5 Revision Loop

**What:** The LLM receives structured evidence and revises its proposal. The Oracle re-evaluates.

**Evidence:** C1 established that the model revises in response to feedback. The revision loop is the mechanism by which structured evidence improves proposals.

**Classification:** EMPIRICALLY SUPPORTED — but adherence is variable (67–100% depending on framing).

**Loop control:**
- Maximum revision iterations: configurable (suggest 3–5)
- Budget enforcement: total Oracle + LLM calls tracked
- Termination: verified / rejected / budget exhausted

### 6.6 Verification Gate (C5-style)

**What:** A deterministic gate that accepts or rejects the final proposal based on evidence.

**Evidence:** NOT EXPERIMENTALLY TESTED. This is an engineering design choice based on P1 (No Unverified State Transition).

**Classification:** ENGINEERING DESIGN CHOICE.

**Design:**
```
Gate accepts if:
  - All ERROR findings resolved
  - No unauthorized modifications to validated baseline
  - Evidence provenance intact
  - Revision budget not exceeded

Gate rejects if:
  - Unresolved ERROR findings
  - Unauthorized modifications detected
  - Evidence chain broken
```

### 6.7 Evidence-Conditioned Routing (C4-style)

**What:** A deterministic routing table that maps finding codes to appropriate procedures.

**Evidence:** NOT EXPERIMENTALLY TESTED. This is an engineering design choice based on P3 (Evidence-Conditioned Reasoning).

**Classification:** ENGINEERING DESIGN CHOICE.

**Design:**
```
Finding code → Procedure
missing_input_delay → LLM revision with specific guidance
missing_output_delay → LLM revision with specific guidance
missing_generated_clock → LLM revision with specific guidance
unknown_finding → Log and escalate
```

### 6.8 Epistemic State (C3-style)

**What:** Explicit representation of validated/refuted/unknown/ambiguous states.

**Evidence:** NOT JUSTIFIED by current evidence. Prompt design provides a more parsimonious explanation.

**Classification:** DEFERRED HYPOTHESIS.

**Status:** C3 remains blocked. This component is NOT included in the minimal or extended architecture.

---

## 7. Authority Model

```
┌─────────────────────────────────────────────────────┐
│                 AUTHORITY SEPARATION                  │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   PROPOSAL   │  │   EVIDENCE   │  │ AUTHORITY  │ │
│  │   LLM only   │  │  Oracle only │  │  Gate only │ │
│  │              │  │              │  │            │ │
│  │ • Generate   │  │ • Execute    │  │ • Accept   │ │
│  │   candidate  │  │   checks     │  │ • Reject   │ │
│  │ • Revise     │  │ • Produce    │  │ • Authorize│ │
│  │   proposal   │  │   findings   │  │            │ │
│  │              │  │ • Represent  │  │            │ │
│  │ CANNOT:      │  │   evidence   │  │ CANNOT:    │ │
│  │ • Verify     │  │              │  │ • Generate │ │
│  │ • Authorize  │  │ CANNOT:      │  │ • Verify   │ │
│  │ • Modify     │  │ • Generate   │  │ • Modify   │ │
│  │   evidence   │  │   proposals  │  │   evidence │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                      │
│  Core Invariant:                                     │
│  NO PROBABILISTIC COMPONENT CAN PROMOTE A            │
│  PROPOSITION INTO VERIFIED ENGINEERING STATE         │
│  BY ITSELF.                                          │
└─────────────────────────────────────────────────────┘
```

**Classification:** ENGINEERING DESIGN CHOICE — supported by P7 principle and experimental design, not by direct experimental comparison.

---

## 8. Verification Model

```
┌─────────────────────────────────────────────────────┐
│                 VERIFICATION FLOW                     │
│                                                      │
│  Initial SDC ──→ Oracle ──→ Findings                │
│                      │                               │
│                      ↓                               │
│              ERROR count > 0?                        │
│                      │                               │
│              ┌───────┴───────┐                       │
│              ↓               ↓                       │
│             YES              NO                      │
│              │               │                       │
│              ↓               ↓                       │
│      Feed to LLM      ACCEPT proposal               │
│              │                                       │
│              ↓                                       │
│      LLM revises                                    │
│              │                                       │
│              ↓                                       │
│      Oracle re-evaluates                             │
│              │                                       │
│              ↓                                       │
│      ERROR count reduced?                            │
│              │                                       │
│      ┌───────┴───────┐                               │
│      ↓               ↓                               │
│     YES              NO                              │
│      │               │                               │
│      ↓               ↓                               │
│  Continue loop   REJECT proposal                    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 9. Failure/Revision Loop Design

```
┌─────────────────────────────────────────────────────┐
│              REVISION LOOP CONTROL                    │
│                                                      │
│  Parameters:                                         │
│  - max_iterations: 5 (configurable)                 │
│  - max_total_calls: 15 (5 iterations × 3 calls)    │
│  - timeout_per_call: 60s                            │
│                                                      │
│  Termination conditions:                             │
│  1. All ERROR findings resolved → ACCEPT             │
│  2. Max iterations reached → REJECT                  │
│  3. Budget exhausted → REJECT                        │
│  4. Provider failure → INCOMPLETE (no retry)         │
│  5. Oracle failure → INCOMPLETE (no retry)           │
│                                                      │
│  Revision tracking:                                  │
│  - Each iteration produces a manifest                │
│  - Manifests are preserved for audit                 │
│  - ERROR count delta tracked per iteration           │
│  - Adherence measured as: final < initial            │
│                                                      │
│  Failure policy:                                     │
│  - Provider timeout → INCOMPLETE, no retry           │
│  - Empty output → INCOMPLETE, no retry               │
│  - Model substitution → FORBIDDEN                    │
│  - Retry beyond budget → FORBIDDEN                   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 10. C3/C4/C5 Treatment

| Component | Treatment | Rationale |
|-----------|-----------|-----------|
| **C3 (Epistemic State)** | **NOT INCLUDED** — deferred hypothesis | NOT JUSTIFIED by evidence. Prompt design is simpler. |
| **C4 (Routing)** | **INCLUDED as engineering choice** — optional | P3 principle supports it. Not experimentally tested, but useful architecture. |
| **C5 (Authorization)** | **INCLUDED as engineering choice** — optional | P1 principle supports it. Not experimentally tested, but useful architecture. |

### Why C3 Is Excluded

- A1 = 24/24 = 100% with a simple prompt change
- No evidence of model epistemic uncertainty
- Prompt design is more parsimonious
- Including C3 would add complexity without evidence

### Why C4 Is Included (as optional)

- P3 (Evidence-Conditioned Reasoning) is a sound engineering principle
- Deterministic routing reduces the need for LLM judgment about next steps
- Can be implemented without experimental validation

### Why C5 Is Included (as optional)

- P1 (No Unverified State Transition) is a core invariant
- Non-bypassable gates prevent unauthorized state changes
- Can be implemented based on engineering judgment

---

## 11. Empirically Supported vs Engineering Choice vs Future Hypothesis

### EMPIRICALLY SUPPORTED

| Component | Evidence |
|-----------|----------|
| Broad task framing | A1 = 24/24 = 100% |
| LLM proposal generation | 100% activation |
| Structured evidence feedback | C1/C2 established |
| Deterministic Oracle boundary | P1/P4 principles + experimental design |
| Revision loop | C1 established |

### ENGINEERING DESIGN CHOICE

| Component | Rationale |
|-----------|-----------|
| Authority separation (P7) | Sound principle, not experimentally compared |
| Verification gate (C5-style) | P1 principle, not experimentally tested |
| Evidence-conditioned routing (C4-style) | P3 principle, not experimentally tested |
| Revision loop budget/termination | Practical constraint, not experimental finding |

### FUTURE HYPOTHESIS

| Component | Status |
|-----------|--------|
| Epistemic state (C3) | NOT JUSTIFIED — requires new evidence |
| Cross-model generalization | NOT TESTED — optional future research |
| Domain generalization | NOT TESTED — optional future research |

---

## 12. Architecture Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Framing effect is MODEL-005-specific | Medium | Acknowledge limitation; test on new models if deployed |
| Oracle scope insufficient | Low | Ṛta v1.5.11 provides SDC-specific checks; scope documented |
| Revision loop doesn't converge | Medium | Budget enforcement; max iteration limit |
| Provider instability | High | Checkpoint/resume; no retry policy |
| Authority separation violated | High | Deterministic enforcement; no LLM access to evidence/authorization |
| C4/C5 routing/gate adds complexity without benefit | Low | Make optional; start without them |

---

## 13. Open Research Questions

| Question | Priority | Status |
|----------|----------|--------|
| Does framing generalize to other models? | HIGH | Optional future research |
| Does framing apply to other EDA domains? | MEDIUM | Optional future research |
| Why does framing improve adherence? | MEDIUM | Better through engineering practice |
| Should C4 routing be mandatory? | LOW | Engineering decision |
| Should C5 gate be mandatory? | LOW | Engineering decision |

---

## 14. Recommended Next Gate

### Architecture Implementation Design

The evidence is sufficient to begin designing the EGER system. The next gate should be:

**P137 — EGER Architecture Implementation Design**

This would translate the P136 architecture into:
- Detailed component specifications
- Interface definitions
- Data flow diagrams
- Implementation priority
- Test strategy

No further experiments are required before architecture implementation. The empirical phase is complete.

---

```
P136 COMPLETE
EVIDENCE-TO-ARCHITECTURE SYNTHESIS COMPLETE

EMPIRICAL PHASE: COMPLETE
RQ-4: CLOSED
C0: ESTABLISHED
C1: ESTABLISHED
C2: PARTIALLY SUPPORTED
C3: NOT JUSTIFIED — excluded from architecture
C4: DEFERRED — included as optional engineering choice
C5: DEFERRED — included as optional engineering choice

STRONGEST SIGNAL: BROAD TASK FRAMING

CAUSALITY: NOT ESTABLISHED

ARCHITECTURE:
- Minimal: Task → LLM → Oracle → Evidence → Revision → Gate
- Extended: + Routing (C4) + Authorization (C5)
- C3: NOT INCLUDED (not justified by evidence)

RECOMMENDED NEXT GATE:
Architecture Implementation Design (P137)

NO MODEL CALLS
NO EXPERIMENT EXECUTED
```
