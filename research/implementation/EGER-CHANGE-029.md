# EGER-CHANGE-029 — Oracle-First Validation Research Design

## Change ID

EGER-CHANGE-029

## Date

2026-09-03

## Gate

P159 — Oracle-First Validation Research Design

## Summary

Research-design gate only. Designed the Oracle-first validation research program (RQ-5) to test whether EGER's evidence-grounded architecture generalizes across independent deterministic evaluation authorities. Identified OpenSTA as the candidate second Oracle. Decision: PROCEED TO ORACLE PILOT.

---

## Baseline Commit

`1821aac` (P158 checkpoint)

## Documents Inspected

| Document | Purpose |
|----------|---------|
| P136 | Evidence-to-Architecture Synthesis |
| P137 | Architecture Implementation Design |
| P145 | Architecture Validation |
| P146 | Engineering State Checkpoint |
| P148 | Production Hardening Design |
| P153 | D2 Orchestration Assessment |
| P157 | Provenance Persistence Assessment |
| P158 | Git Checkpoint |

## Code Inspected

| File | Purpose |
|------|---------|
| `eger/oracle/adapter.py` | OracleAdapter — current Oracle boundary |
| `eger/oracle/schemas.py` | Oracle schemas and evidence format |
| `eger/evidence/normalizer.py` | EvidenceNormalizer — Oracle-to-evidence translation |
| `eger/evidence/schemas.py` | EvidenceArtifact, Finding contracts |
| `eger/pipeline/e2e.py` | EGERPipeline — production orchestrator |
| `eger/revision/controller.py` | RevisionController — revision loop |
| `eger/verification/gate.py` | VerificationGate — sole authority |

## Research Question Assessed

**RQ-5**: To what extent does the evidence-grounded EGER architecture generalize across independent deterministic evaluation authorities within VLSI engineering tasks?

**Assessment**: Sufficiently precise, experimentally testable, distinct from RQ-4, supported by existing architecture.

## Oracle Candidates Considered

| Oracle | Property Evaluated | Status |
|--------|-------------------|--------|
| Ṛta | Constraint quality | READY (baseline) |
| OpenSTA | Timing analysis | CONDITIONALLY SUITABLE (pilot) |
| Synthesis tools | Elaboration/structure | FUTURE OPTION |
| Formal tools | Property verification | FUTURE OPTION |
| Lint tools | Code quality | FUTURE OPTION (lower value) |

## Decision

**PROCEED TO ORACLE PILOT** — with bounded scope (3–5 tasks, 2 Oracles, ~10 runs).

## Implementation Changes

**NONE.** This is a research-design gate. No experimental implementation or production architecture changes are authorized by this gate.

## Test Result

734/734 PASS (unchanged — no code modifications)

## Security Considerations

- No new attack surface
- No new secrets exposure
- No new filesystem access
- Authority boundaries preserved across Oracle substitution

## Research-State Impact

NONE — no research conclusions changed. RQ-5 is a new research question independent of C0–C5.

## Ṛta Impact

NONE — Ṛta remains Oracle A (baseline). OpenSTA is Oracle B (independent). Neither modifies the other.

## Future Recommendation

Proceed to P160 — OpenSTA Oracle Adapter Design. Before implementing, design the adapter interface, evidence normalization strategy, and task configuration extension.

---

> P159 is a research-design gate. No experimental implementation or production architecture changes are authorized by this gate.
