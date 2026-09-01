# EGER-CHANGE-017 — Core Contracts Implementation

## Date
2026-09-01

## Status
**IMPLEMENTED**

## Reason for Change

P137 (Architecture Implementation Design) identified foundational data contracts
that must be implemented before the EGER architecture can be built. P138
implements these contracts as frozen, typed, deterministic data boundaries.

## Affected Modules

| Module | Change |
|--------|--------|
| `eger/task/` | NEW — TaskDefinition |
| `eger/evidence/` | NEW — Finding, EvidenceArtifact, FindingSummary |
| `eger/prompting/` | NEW — PromptRequest |
| `eger/verification/` | NEW — VerificationResult |
| `eger/revision/` | NEW — RunRecord, RevisionConfig |
| `eger/provenance/` | NEW — ProvenanceTracker |

## Contracts Introduced

| Contract | Schema Version | Frozen |
|----------|---------------|--------|
| TaskDefinition | `eger.task.v1` | YES |
| Finding | `eger.finding.v1` | YES |
| EvidenceArtifact | `eger.evidence.v1` | YES |
| FindingSummary | (part of evidence) | YES |
| PromptRequest | `eger.prompt.v1` | YES |
| VerificationResult | `eger.verification.v1` | YES |
| RunRecord | `eger.run.v1` | YES |
| RevisionConfig | `eger.config.v1` | YES |
| ProvenanceTracker | `eger.provenance.v1` | YES |

## Backward Compatibility

- Existing `eger/oracle/adapter.py` EvidenceArtifact is NOT modified
- Existing `eger/engineer/candidate.py` CandidateArtifact is NOT modified
- New contracts are additive — no existing code is broken
- Historical experiment artifacts are NOT modified

## Tests

- 64 new deterministic unit tests
- All 377 tests pass (64 new + 313 existing)

## Historical Preservation

- DIAGNOSTIC-001 through DIAGNOSTIC-009: UNCHANGED
- RQ4-MODEL-005: UNCHANGED
- All AUTH records: UNCHANGED
- All P090–P137 records: UNCHANGED

## Rollback

Remove the new modules (`eger/task/`, `eger/evidence/`, `eger/prompting/`,
`eger/verification/`, `eger/revision/`, `eger/provenance/`) and
`tests/test_core_contracts.py`. No existing code depends on them.
