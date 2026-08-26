# EGER — Evidence-Grounded Engineering Reasoning
## Canonical Research Definition

| Field | Value |
|---|---|
| Contract version | **EGER Research Contract v0.2** (canonical: `EGER_Research_Contract_v0.2.docx`, workspace root) |
| Status | Research definition — v0.2 |
| Domain | AI-assisted hardware engineering / EDA |
| Initial experimental domain | SDC generation and repair |
| Primary scientific experiment | C0–C5 controlled ablation |
| Engineering extension | C6 specialized EGER subagents |
| Deterministic oracle | External Ṛta (`rta-constraint-intelligence` v1.5.11), adapter boundary only |

> This document mirrors contract v0.2. It does NOT modify any scientific
> definition. Ambiguities are recorded in `STATE.md`, never resolved silently
> here. Proposed changes require an `EGER-CHANGE-###` record.

---

## 1. Project Name

EGER — Evidence-Grounded Engineering Reasoning

## 2. Research Purpose

Determine whether engineering-agent reliability improves when probabilistic
reasoning is architecturally bounded by deterministic evidence, explicit
epistemic state, and non-bypassable verification gates.

## 3. Working Thesis (falsifiable)

AI engineering agents can become more reliable when probabilistic reasoning is
architecturally bounded by deterministic evidence, explicit epistemic state,
and non-bypassable verification gates.
EGER must actively seek evidence that weakens, refutes, or qualifies this thesis.

## 4. Primary Research Question

Can engineering-agent reliability be improved by separating the authorities
responsible for proposing engineering hypotheses and candidate artifacts,
establishing deterministic evidence, representing evidence-derived epistemic
state, and authorizing engineering-state transitions?

NOT the research question:
- "Does a multi-agent system perform better than a single LLM?"
- "Can an LLM generate better SDC when given feedback?" (existing literature area)

## 5. Secondary Research Questions

- Does feedback representation (none / text / structured evidence) measurably change reliability?
- Does explicit externalized epistemic state reduce epistemic violations and repeated errors?
- Does evidence-conditioned routing reduce invalid or unnecessary actions?
- Does a non-bypassable authorization gate reduce regressions and unauthorized overwrites?
- Can validated mechanisms be decomposed across specialized subagents without unacceptable coordination overhead or epistemic corruption? (C6)

## 6–7. Domain / Initial Experimental Domain

Digital ASIC/VLSI constraint engineering; specifically SDC generation and repair
against deterministic validation.

## 8. Principles P1–P8

Operational form maintained in [`PRINCIPLES.md`](PRINCIPLES.md).

- **P1** No Unverified State Transition
- **P2** Externalized Epistemic State
- **P3** Evidence-Conditioned Reasoning
- **P4** Executable Engineering Checklist
- **P5** Repetition Drives Convergence
- **P6** Explicit Epistemic Boundaries
- **P7** Authority Separation
- **P8** Research Traceability and Reproducibility

## 9. Reliability Dimensions (never collapsed into one score)

- **Artifact reliability** — is the engineering artifact technically correct?
- **Reasoning reliability** — appropriate response to evidence, recovery, next-action quality, avoiding unnecessary/contradictory actions?
- **Epistemic reliability** — correct representation of validated / refuted / unknown / ambiguous / hypothetical?

## 10. Epistemic Corruption (first-class failure category)

Examples: HYPOTHESIS→VALIDATED without sufficient evidence; REFUTED→VALIDATED
without new evidence; UNKNOWN→TRUE/FALSE without proof; oracle-scoped fact →
universal fact; validated baseline modified without regression verification;
evidence discarded without documented reason; state claims without provenance.

## 11. Epistemic Violation Rate (candidate metric — NOT yet operationalized)

    EVR = epistemic violations / evaluated epistemic claims

Violations include: unsupported validation, incorrect state transitions,
ignored refuted evidence, unknown treated as known, oracle scope exceeded,
provenance lost, unauthorized overwrite.
Status: architecture must expose required data first (journal-based);
operationalization precedes any formal use. No EVR numbers exist.

## 12. Primary Experiment C0–C5

- **C0** LLM only: Design → LLM → SDC
- **C1** LLM + textual feedback: … → Oracle → Text → LLM
- **C2** LLM + structured evidence: … → Oracle → Structured Evidence → LLM
- **C3** C2 + explicit epistemic state
- **C4** C3 + evidence-conditioned routing
- **C5** C4 + non-bypassable authorization

C0–C5 are the primary scientific ablation. Each stage adds exactly one intended
mechanism; causal isolation table lives in the ARCH-002 record.

## 13. C6 Engineering Extension

Specialized subagents introduced ONLY after C0–C5 evaluation. Not part of the
primary causal experiment. Multi-agent complexity is never evidence that EGER works.

## 14. Authority Model

PROPOSAL ≠ EVIDENCE ≠ EPISTEMIC STATE ≠ AUTHORIZATION.

Core invariant: **NO PROBABILISTIC COMPONENT CAN PROMOTE A PROPOSITION INTO
VERIFIED ENGINEERING STATE BY ITSELF.**

Current instantiation (EGER-DEC-005): for C0–C5 exactly ONE probabilistic
component (single LLM agent); Evidence, Epistemic State, and Authorization are
deterministic layers enforced by tool boundaries and permissions.

## 15. Ṛta Boundary

Ṛta = external deterministic constraint intelligence / oracle candidate
(v1.5.11 confirmed by static reconnaissance, EGER-ORACLE-001).
EGER communicates only through an adapter around its declared interface.
No EGER code inside Ṛta; no LLM added to Ṛta; Ṛta's identity unchanged.
See [`oracle/EGER-ORACLE-001.md`](oracle/EGER-ORACLE-001.md).

## 16. Scientific Invariants I1–I8

I1 no probabilistic self-promotion · I2 four distinct authorities ·
I3 UNKNOWN ≠ TRUE/FALSE · I4 oracle validation scoped to declared capabilities ·
I5 validated state not overwritten without regression/authorization ·
I6 research claims retain provenance · I7 no silent change of frozen scientific
definitions · I8 complexity ≠ quality.

## 17. Anti-Gaming Principles

Benchmark must include unseen designs, unseen constraint combinations,
adversarially invalid constraints, plausible-but-semantically-wrong constraints,
incomplete context, ambiguity, regression scenarios. Passing a visible validator
is not equivalent to engineering correctness.

## 18. Research Integrity Rules

Do not modify results to support the thesis; record failed/unexpected experiments;
record model/runtime/oracle/tool/benchmark versions; preserve rejected hypotheses
and alternatives; preserve provenance; separate observation from interpretation;
no silent change of frozen definitions; changes require explicit review;
reproduce before strong conclusions; negative results are valid outcomes.

## 19. Current Research Phase

Phase 0 → transitioning to Phase 1 preparation: traceability foundation
established (EGER-P004); implementation not started. See [`STATE.md`](STATE.md).

## 20. Contract Version & Change Control

Canonical: **v0.2**. Frozen upon acceptance for implementation: research
question, thesis, P1–P8, authority boundaries, C0–C5 definitions, primary
variables, reliability dimensions, corruption definition, traceability requirement.

Change mechanism: create `EGER-CHANGE-###` containing current definition,
proposed definition, reason, evidence, experimental impact, status=PROPOSED.
Only research review makes it authoritative. Implementation agents MUST NOT
silently modify this document's scientific content.

## Artifact Classification (contract §15)

Every material statement carries one of:
`SOURCE-DERIVED CLAIM` · `AGENT INFERENCE` · `RESEARCH HYPOTHESIS` ·
`OBSERVATION` · `EXPERIMENTAL RESULT` · `CONCLUSION`.
Silent promotion between categories is forbidden.
Notably: EGER-ARCH-002 is an architecture DECISION/RECOMMENDATION — not an
experimental result. C0–C5 have not been run. No improvement has been demonstrated.
