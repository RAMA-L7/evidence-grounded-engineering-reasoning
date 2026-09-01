# EGER-CHANGE-020 — Revision Controller Implementation

## Date
2026-09-01

## Status
**IMPLEMENTED**

## Reason for Change

P137 (Architecture Implementation Design) identified the need for a
RevisionController that orchestrates the generate→verify→revise cycle.
P141 implements this component.

## Affected Modules

| Module | Change |
|--------|--------|
| `eger/revision/controller.py` | NEW — RevisionController |
| `eger/revision/__init__.py` | Updated — exports RevisionController |

## RevisionController Architecture

```
TaskDefinition
    ↓
PromptBuilder.build()
    ↓
PromptRequest
    ↓
ProposalGenerator.generate()
    ↓
CandidateArtifact
    ↓
OracleAdapter.validate()
    ↓
EvidenceNormalizer.normalize()
    ↓
EvidenceArtifact
    ↓
Budget check → continue or terminate
    ↓
RunRecord
```

### Authority Boundaries

| Component | Authority |
|-----------|-----------|
| LLM | Proposal ONLY |
| Oracle | Evidence ONLY |
| RevisionController | Orchestration ONLY |
| VerificationGate | Acceptance ONLY (P142) |

### Budget Enforcement

| Budget | Default | Enforcement |
|--------|---------|-------------|
| max_iterations | 5 | Terminate at limit |
| max_total_calls | 15 | Terminate before call |
| timeout_seconds | 60 | Per-call timeout |

### Failure Semantics

| Failure | Response |
|---------|----------|
| Model failure | INCOMPLETE |
| Malformed output | INCOMPLETE |
| Oracle failure | INCOMPLETE |
| Oracle exception | INCOMPLETE |
| Budget exhausted | REJECTED (P142 decides) |
| Max iterations | REJECTED (P142 decides) |
| No errors | REJECTED (P142 decides) |

## Tests

- 25 new deterministic unit tests
- All 463 tests pass (25 new + 438 existing)

## Historical Preservation

- All DIAGNOSTIC artifacts: UNCHANGED
- All AUTH records: UNCHANGED
- All P090–P140 records: UNCHANGED

## Rollback

Remove `eger/revision/controller.py` and `tests/test_revision_controller.py`.
Revert `eger/revision/__init__.py` to P140 version.
