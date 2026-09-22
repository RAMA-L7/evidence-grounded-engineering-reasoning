# EGER — Evidence-Grounded Engineering Reasoning

A research project studying whether a probabilistic LLM proposal generator can be paired with **deterministic external engineering evaluation** to form an evidence-grounded control loop for Synopsys Design Constraints (SDC) generation.

**Research site:** <https://rama-l7.github.io/evidence-grounded-engineering-reasoning/> — the findings, story, method, evidence, results, reproducibility, limitations and materials, served from `docs/`. The [primary documents](https://rama-l7.github.io/evidence-grounded-engineering-reasoning/materials.html) link to the checksummed submission package in `research/thesis/EGER-001-Final-Submission-Package-v1.0/`.

**Research directory:** `research/` — this README is a repo-level map; the canonical research narrative lives there.

## What EGER is

EGER investigates a specific architectural question: **can LLM-generated SDC be steered by deterministic evaluation evidence rather than by textual/model self-evaluation?**

The key distinction is between:

- **Probabilistic LLM proposal generation** — the LLM proposes candidate SDC. This is the only probabilistic component.
- **Deterministic external engineering evaluation** — Ṛta (structural/constraint-quality) and OpenSTA (timing) evaluate proposals against their own deterministic properties. These are evidence authorities, not LLM components.

The LLM is **not** the final authority. In the implemented architecture, the **VerificationGate** is the sole ACCEPT/REJECT authority.

## Research objective

Determine, with controlled experiments and explicit claim boundaries, what EGER has actually demonstrated and what remains unproven.

The project deliberately separates:

- **C0–C5 / RQ-4** — architecture hypothesis and controlled evidence/revision behavior
- **RQ-5 / PILOT-002 / P185** — deterministic authority separation and an additive two-model observation under frozen synthetic VLSI conditions

These are two research questions and must be kept separate. Do not merge them into one over-strong causal claim.

## High-level architecture

```
Task Definition
      ↓
LLM Proposal
      ↓
Deterministic Oracle (Ṛta and/or OpenSTA, each with its own property)
      ↓
Structured Evidence
      ↓
Revision Loop
      ↓
Verification Gate
      ↓
ACCEPT / REJECT
```

Implementation layer:

```
TaskDefinition
      ↓
PromptBuilder
      ↓
ProposalGenerator (LLM)
      ↓
CandidateArtifact
      ↓
OracleAdapter
      ↓
EvidenceNormalizer
      ↓
EvidenceArtifact
      ↓
RevisionController
      ↓
VerificationGate
      ↓
ProvenanceTracker
```

Authority separation:

- **Engineer (LLM):** proposal authority only. Probabilistic component.
- **Oracle (Ṛta or OpenSTA):** evidence authority. Evaluates proposals against its own deterministic property. Deterministic.
- **VerificationGate:** authorization authority. Sole ACCEPT/REJECT decider. Deterministic.
- **RevisionController:** architectural mechanism under study. Operates on Oracle-derived evidence.

Do not describe Ṛta as an LLM. Do not describe VerificationGate as an LLM. Do not imply the LLM is the final authority. Do not collapse Oracle execution success into validation.

## Research status (frozen)

```text
C0: ESTABLISHED
C1: ESTABLISHED
C2: PARTIALLY SUPPORTED / absorbed into C1 where applicable
C3: NOT JUSTIFIED
C4: DEFERRED
C5: DEFERRED

RQ-4: CLOSED (behavioral-association level; causality NOT established)
RQ-5: CLOSED at Level 2 (descriptive pilot; generalization NOT established)

P185: additive second-model observation (mimo vs nemotron; 15/16 completed)
P186: independent review PASS WITH REVISION (two prose-count corrections)
P187: packaging review PASS WITH REMAINING DOCUMENTATION GAPS (closed in P187-R)
```

Ṛta: deterministic, external, read-only (1.5.11 @ 3b5c2f2; unchanged through P159–P186).
VerificationGate: sole ACCEPT/REJECT authority (UNCHANGED).

## Explicit limitations

This research does **NOT** establish:

- model independence
- statistical superiority / equivalence
- universal generalization
- production-scale generalization
- Oracle interchangeability (refuted on T2 by observation: same task, opposite verdicts, each authority correct in its own property)
- causal inference (RQ-4 is closed at behavioral-association level)

The strongest defensible aggregate claim is:

> The EGER evidence-grounded control loop operated with the two tested language models — `opencode/mimo-v2.5-free` and `opencode/nemotron-3.5-lightning-free` — across the frozen synthetic VLSI tasks and the two independent deterministic evaluation authorities (Ṛta and OpenSTA), with evaluation evidence entering the common EGER evidence contract and reaching the VerificationGate, under the tested conditions.

## Documentation entry points

- Research state snapshot: `research/STATE.md` — frozen record through P187
- Consolidated research state: `research/implementation/EGER-P181-RESEARCH-STATE-CONSOLIDATION-AND-POST-RQ5-SYNTHESIS-001.md`
- RQ-5 model-comparison execution: `research/implementation/EGER-P185-MODEL-COMPARISON-RQ5-CONTROLLED-EXECUTION-001.md`
- Independent review: `research/implementation/EGER-P186-INDEPENDENT-RESEARCH-REVIEW-OF-P185-001.md`
- Packaging / claim-surface review: `research/implementation/EGER-P187-RESEARCH-PACKAGING-AND-CLAIM-SURFACE-REVIEW-001.md`
- Reproducibility: `research/REPRODUCIBILITY.md`
- Architecture (pending/unvalidated design recommendation): `research/architecture/EGER-ARCH-002.md`
- EvidenceOracle contract: `research/oracle/EGER-EVIDENCE-ORACLE-CONTRACT.md`
- Change control: `research/implementation/EGER-CHANGE-001.md` through `EGER-CHANGE-060.md`

## Repository integrity

- Ṛta is excluded from version control and is not modified by the project.
- VerificationGate is not modified as part of these research gates.
- Raw experimental records are intentionally local and are not automatically exposed by this package.
- `Universal_Principles_Library/` is internal/protected and is not part of the research record.

## Tests

Run the normal regression suite to verify implementation integrity:

```bash
python -m pytest tests -q
```

The EGER regression suite also covers deterministic-layer tests. The research results themselves are documented in the `research/` records above, not in the regression suite.

## Not a marketing document

This README is a technical/research map, not an endorsement or a claim of production readiness. The research record is bounded by the frozen conclusions above.
