# EGER — P181: Research State Consolidation & Post-RQ-5 Synthesis Gate

## 1. Executive Summary

The EGER project has completed two major research arcs:

1. **C0–C1/C2 + RQ-4** (P025–P150): Evidence-grounded revision architecture discovery and implementation
2. **RQ-5** (P159–P180): Oracle-first validation — does the architecture generalize across independent deterministic evaluation authorities?

This document consolidates the authoritative post-RQ-5 research state, reconciles all major findings, and identifies the boundary between completed evidence and future work.

**No experiment was run. No code was modified. No historical records were changed.**

## 2. Frozen Research Questions

### RQ-4 (CLOSED)

> "Does structured engineering evidence cause an improvement in the correctness of an engineering proposal?"

**Answer:** Partially, through a specific mechanism. Structured evidence reliably causes proposal revision (100% activation). Revision does not always address ERROR findings (adherence 67–100% depending on task framing). Broader task framing is strongly associated with improved adherence (A1 = 24/24 = 100% vs A4 = 16/24 = 67%). The effect is probabilistic, not deterministic. Framing causality is NOT established (behavioral association only).

### RQ-5 (CLOSED — Level 2)

> "To what extent does the evidence-grounded EGER architecture generalize across independent deterministic evaluation authorities within VLSI engineering tasks?"

**Answer:** The evidence-grounded EGER control loop operated with two independent deterministic evaluation authorities (Ṛta and OpenSTA) across the two frozen synthetic VLSI tasks, with evaluation evidence entering the common EGER evidence contract and reaching the VerificationGate — under the tested conditions.

**Maximum claim: Level 2** (descriptive pilot). Oracle interchangeability is NOT established (refuted on T2 by observation: same task, opposite verdicts, each correct in its own domain). Generalization beyond tested conditions is NOT established.

## 3. C0–C5 Final Status

| Stage | Objective | Status | Strongest Finding |
| ----- | --------- | ------ | ----------------- |
| **C0** | LLM only baseline | **ESTABLISHED** | Proposal activation near-universal; no deterministic validation |
| **C1** | LLM + structured evidence feedback | **ESTABLISHED** | Structured evidence reliably activates revision (100% activation); ERROR adherence is task-dependent and stochastic |
| **C2** | Evidence normalization | **PARTIALLY SUPPORTED** | Absorbed into C1 investigation; structured feedback is more actionable than text |
| **C3** | C2 + epistemic-state intervention | **NOT JUSTIFIED** | Prompt design provides a simpler explanation; no evidence of model epistemic uncertainty |
| **C4** | C3 + evidence-conditioned routing | **DEFERRED** | Engineering design choice, not experimental stage |
| **C5** | C4 + non-bypassable authorization | **DEFERRED** | Engineering design choice, not experimental stage |

**Key insight:** C3 was NOT JUSTIFIED because the research discovered a more parsimonious explanation for adherence variability — prompt design (task framing) explains more variance than epistemic-state intervention would. A1 (broad framing only) = 24/24 = 100% adherence, making epistemic-state manipulation unnecessary.

## 4. Empirical Evidence Matrix

### Established Findings

| Finding | Classification | Evidence | Record |
| ------- | -------------- | -------- | ------ |
| Structured evidence causes proposal revision | ESTABLISHED | 100% activation across all experiments | C0–C1 |
| ERROR adherence is task-dependent | ESTABLISHED | BASE varies 25–100% across tasks | C1 |
| Broader framing improves adherence | STRONG SIGNAL | A1 = 24/24 vs A4 = 16/24 | RQ-4 |
| Authority separation is architecturally necessary | ESTABLISHED | LLM cannot verify its own proposals | P7/P136 |
| EGER operates with multiple independent Oracles | ESTABLISHED (Level 2) | PILOT-002: 8/8 completed, both authorities drove their own loops | RQ-5 |
| Authority-specific evaluation produces divergent verdicts | ESTABLISHED | T2: same task, opposite verdicts (Ṛta ACCEPT, OpenSTA REJECT) | RQ-5 |

### Supported Signals

| Finding | Classification | Evidence |
| ------- | -------------- | -------- |
| Technical content improves adherence | SUPPORTED SIGNAL | A2 = 20/23 vs A4 = 16/24 |
| Framing alone is sufficient | STRONG SIGNAL | A1 without technical keywords = 100% |
| Deterministic verification provides ground truth | ESTABLISHED | Oracle provides ground truth for ERROR findings |

### NOT Established

| Claim | Status | Reason |
| ----- | ------ | ------ |
| Framing causally determines adherence | NOT ESTABLISHED | Behavioral association only |
| Mechanism is model-interior | NOT ESTABLISHED | Only behavioral outcomes measured |
| Effect generalizes beyond MODEL-005 | NOT ESTABLISHED | Only one model tested |
| Epistemic uncertainty causes adherence failures | NOT ESTABLISHED | No evidence measured or correlated |
| Oracle interchangeability | NOT ESTABLISHED | Refuted on T2 (same task, opposite verdicts) |
| Production-scale generalization | NOT ESTABLISHED | Synthetic 3-cell substrate only |
| Causal inference from RQ-5 | NOT ESTABLISHED | N=8 descriptive pilot |

## 5. Architecture Decisions

### Validated (Empirically Supported)

| Decision | Status | Evidence |
| -------- | ------ | -------- |
| OracleAdapter abstraction | VALIDATED | P160–P176: Rta and OpenSTA both work through the same adapter interface |
| EvidenceNormalizer canonical pipeline | VALIDATED | P176: both authorities' evidence enters the same contract |
| VerificationGate as sole final authority | VALIDATED | P179: gate received and processed evidence from both authorities |
| Deterministic Oracle evaluation | VALIDATED | Both Rta 1.5.11 and OpenSTA 2.2.0 produce deterministic outputs |
| Shared candidate evaluation across authorities | VALIDATED | P178: shared initial SDC byte-identical across Oracle arms |

### Chosen (Engineering Design)

| Decision | Status | Basis |
| -------- | ------ | ------- |
| Netlist-less Rta evaluation | CHOSEN | P175/P176: avoids feeding Rta structural context toward OpenSTA's lane |
| P055 DesignMetadata for scope elevation | CHOSEN | P175: harness passes frozen metadata; adapter elevates to FULL |
| Canonical scope pass-through in normalizer | CHOSEN | P176: single-function change; canonical values pass through unchanged |
| Candidate-validity gate before Oracle | CHOSEN | P172: reject non-SDC before Oracle invocation |
| NO_TIMING_CONSTRAINT / metadata_unqualified at experiment layer | CHOSEN | P176/P177: experiment-layer levers, not gate changes |
| Bounded retry (1 max, both attempts retained) | CHOSEN | P169: frozen retry policy |

### Deferred

| Decision | Status | Reason |
| -------- | ------ | ------- |
| C3 epistemic-state intervention | DEFERRED | Not justified by evidence; prompt design is simpler |
| C4 evidence-conditioned routing | DEFERRED | Engineering choice, not experimentally motivated |
| C5 non-bypassable authorization | DEFERRED | Engineering choice, not experimentally motivated |
| C6 specialized subagents | DEFERRED | Deferred until after C0–C5 evaluation |
| Paired-generation design (byte-identical revised candidates across arms) | DEFERRED | Requires new protocol-design gate |
| Production-scale VLSI tasks | DEFERRED | Requires new research-design gate |

### Rejected

| Decision | Status | Reason |
| -------- | ------ | ------- |
| Rta as timing authority | REJECTED | Rta measures constraint quality, not timing |
| OpenSTA as constraint-quality authority | REJECTED | OpenSTA measures timing, not constraint quality |
| Universal Oracle score | REJECTED | Different authorities measure different properties |
| Epistemic-state as primary mechanism | REJECTED | More parsimonious explanation exists (prompt design) |

## 6. Authority-Separation Statement

The EGER architecture implements a clear authority separation:

```
┌─────────────────────────────────────────────────────┐
│                    EGER Pipeline                      │
│                                                       │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐       │
│  │ Engineer  │───▶│  Oracle   │───▶│   Gate   │       │
│  │ (propose) │    │ (verify) │    │ (decide) │       │
│  └──────────┘    └──────────┘    └──────────┘       │
│       │               │               │               │
│   PROPOSAL         EVIDENCE       AUTHORIZATION      │
│   authority        authority       authority          │
└─────────────────────────────────────────────────────┘
```

- **Engineer (LLM):** Proposal authority only. Generates SDC candidates.
- **Oracle (Rta or OpenSTA):** Evidence authority. Evaluates proposals against its deterministic property.
- **VerificationGate:** Authorization authority. Receives evidence and makes ACCEPT/REJECT decision.

**Critical:** The Oracle does NOT produce final ACCEPT/REJECT authority. The VerificationGate remains the sole final decision authority. The Oracle produces evidence; the Gate interprets it.

**RQ-5 demonstrated:** Both Rta and OpenSTA can serve as the Oracle authority, each producing evidence that enters the same EGER evidence contract and reaches the same VerificationGate. The two authorities legitimately disagree about the same artifact because they measure different engineering properties.

## 7. Rta Boundary

- **Version:** 1.5.11, pinned at revision `3b5c2f2`
- **Property measured:** SDC constraint quality (structural completeness, syntax, constraint relationships)
- **Invocation:** `check <file> --json` (netlist-less) + P055 DesignMetadata
- **Scope:** FULL when design_metadata references are valid; PARTIAL when references are invalid
- **Findings:** SDC-005 (missing input delay), SDC-006 (missing output delay), SDC-008/009 (I/O delay ≥ clock period)
- **Authority boundary:** Rta does NOT compute timing. It evaluates whether the SDC is structurally correct and internally consistent.
- **Modification:** UNCHANGED throughout P159–P180

## 8. OpenSTA Boundary

- **Version:** 2.2.0, WSL binary at `/root/opensta_build/OpenSTA/app/sta`
- **Property measured:** Static timing analysis (setup/hold slack, WNS, TNS)
- **Invocation:** Staged Tcl script via WSL2
- **Scope:** VALIDATED when clock is defined and timing can be computed
- **Findings:** Timing violations (negative WNS), timing clean (WNS ≥ 0)
- **Authority boundary:** OpenSTA does NOT evaluate SDC constraint quality. It evaluates whether the design meets timing under the given constraints.
- **Modification:** adapter unchanged; harness-only encoding fix (utf-8)

## 9. VerificationGate Boundary

- **Authority:** Sole final decision authority (ACCEPT/REJECT)
- **Input:** EvidenceArtifact from EvidenceNormalizer
- **Decision logic:** Fail-closed on ERROR findings; accept on zero errors with sufficient scope
- **Scope handling:** FULL → normal processing; PARTIAL → accept with zero errors (existing contract); INSUFFICIENT/UNSUPPORTED → fail-closed REJECT
- **Modification:** UNCHANGED throughout P159–P180

## 10. Evidence-Contract Role

The EGER evidence contract serves as the common interface between authorities:

```
Oracle raw output
    ↓
EvidenceOracle (adapter)
    ↓
EvidenceNormalizer
    ↓
EvidenceArtifact
    ↓
VerificationGate
```

**Key property:** Both Rta and OpenSTA produce evidence that enters the same contract without authority-specific architectural changes. The normalizer's canonical scope pass-through (P176) ensures Rta's canonical vocabulary survives normalization.

**RQ-5 demonstrated:** 22/22 Oracle evaluations produced evidence artifacts that entered the EGER evidence contract. Both authorities' evidence reached the VerificationGate.

## 11. Unsupported Claims

The following claims are explicitly NOT supported by the current evidence:

1. **Oracle interchangeability** — Refuted on T2 (same task, opposite verdicts)
2. **Oracle equivalence** — Different authorities measure different properties
3. **Universal generalization** — Only tested on synthetic 3-cell substrate
4. **Production-scale generalization** — Synthetic substrate only
5. **Causal inference from RQ-5** — N=8 descriptive pilot
6. **Framing causality** — Behavioral association only (RQ-4)
7. **Model-interior mechanism** — Only behavioral outcomes measured
8. **Generalization beyond MODEL-005** — Only one model tested

## 12. Future Research Candidates

The following are candidates for future research-design gates. None are authorized or designed:

### High Priority

1. **Production-scale RQ-5 replication:** Larger VLSI designs, real SDCs, production timing constraints. Would test whether Level-2 findings hold at scale.

2. **Multi-task RQ-5 expansion:** More synthetic tasks with diverse timing/constraint scenarios. Would test whether authority-separated results generalize across task families.

3. **RQ-4 causal investigation:** Controlled experiment isolating framing effects with multiple models. Would test whether framing causally determines adherence.

### Medium Priority

4. **Paired-generation design:** Byte-identical revised candidates evaluated by both authorities. Would eliminate the revision-feedback confound.

5. **Model-comparison RQ-5:** Same tasks, same protocol, different LLMs. Would test whether the architecture pattern generalizes across models.

6. **Larger-N RQ-5:** More replications per condition. Would support stronger descriptive claims.

### Lower Priority

7. **C3 revisit with modern models:** Epistemic-state intervention with models that expose confidence/uncertainty signals.

8. **C4/C5 implementation:** Evidence-conditioned routing and authorization gates, if motivated by a new research question.

9. **C6 specialized subagents:** Multi-agent EGER architectures.

10. **Cross-domain validation:** Apply EGER architecture to non-VLSI engineering domains.

## 13. Final Frozen Thesis

> **The EGER evidence-grounded engineering reasoning architecture establishes that structured deterministic evidence reliably activates proposal revision in LLMs (C0–C1), and that this revision pattern operates with multiple independent deterministic evaluation authorities within the tested synthetic VLSI conditions (RQ-5 Level 2). The architecture implements clear authority separation: the LLM proposes, the Oracle verifies, and the VerificationGate decides. Different authorities legitimately disagree about the same artifact because they measure different engineering properties — this is a feature of the architecture, not a defect.**

## 14. Explicit Stopping Boundary

The following are the hard boundaries of the completed evidence base:

- **C0–C1/C2:** Established on MODEL-005 (opencode/mimo-v2.5-free) with BENCH-002 tasks. Generalization to other models and tasks NOT established.
- **RQ-4:** Closed at behavioral-association level. Causality NOT established.
- **RQ-5:** Closed at Level 2 (descriptive pilot) on synthetic 3-cell substrate with Rta 1.5.11 and OpenSTA 2.2.0. Generalization NOT established.
- **C3:** Not justified. Prompt design is a more parsimonious explanation.
- **C4/C5:** Deferred. No experimental motivation.
- **Production architecture:** Implemented but not validated at production scale.

**Any future work requires a new research-design gate.** The completed P159–P180 arc and the earlier C0–C1/RQ-4 arc form the authoritative baseline for any future research question.

## 15. Research Boundary

```text
C0: ESTABLISHED
C1: ESTABLISHED
C2: PARTIALLY SUPPORTED
C3: NOT JUSTIFIED
C4: DEFERRED
C5: DEFERRED

RQ-4: CLOSED
RQ-5: CLOSED (Level 2)

Rta modified: NO
VerificationGate modified: NO
C0-C5 conclusions changed: NO
```

## 16. Test Regression

- EGER full suite: 878/878 PASS
- Harness suite: 62/62 PASS

## 17. Git

- P181 committed as: `<hash>` (see CHANGE-053)
- HEAD == origin/main (after push)
- No code changes; research records only
- Universal_Principles_Library/ untouched

## 18. Artifacts

- `research/implementation/EGER-P181-RESEARCH-STATE-CONSOLIDATION-AND-POST-RQ5-SYNTHESIS-001.md`
- `research/implementation/EGER-CHANGE-053.md`

## STOP

No future research question was designed or executed in P181. This is a consolidation gate only. The authoritative EGER research state is now frozen and can serve as the baseline for any future research-design gate.
