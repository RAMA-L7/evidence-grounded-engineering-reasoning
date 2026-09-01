# EGER-CHANGE-022 — Provenance Tracker Implementation

## Date
2026-09-01

## Status
**IMPLEMENTED**

## Reason for Change

P137 (Architecture Implementation Design) identified the need for a
ProvenanceTracker that makes EGER runs auditable and reconstructable.
P143 implements this component.

## Affected Modules

| Module | Change |
|--------|--------|
| `eger/provenance/tracker.py` | Enhanced — run lifecycle, artifact relationships, reconstruction |
| `eger/provenance/__init__.py` | Unchanged |

## Provenance Architecture

```
TaskDefinition
    ↓
PromptRequest → record_prompt()
    ↓
CandidateArtifact → record_candidate()
    ↓
OracleAdapter → record_oracle_evaluation()
    ↓
EvidenceArtifact → record_evidence()
    ↓
VerificationGate → record_verification()
    ↓
RevisionController → complete_run()
    ↓
ProvenanceTracker → Complete Run Provenance
```

### Event Sequence

| Event | Producer | What is Recorded |
|-------|----------|------------------|
| RUN_STARTED | RevisionController | run_id, task_id |
| PROMPT_CREATED | PromptBuilder | prompt_hash, request_id, iteration |
| CANDIDATE_CREATED | ProposalGenerator | candidate_id, candidate_hash, iteration |
| ORACLE_EVALUATED | OracleAdapter | oracle_artifact_id, candidate_hash |
| EVIDENCE_RECORDED | EvidenceNormalizer | evidence_id, evidence_hash, iteration |
| VERIFICATION_COMPLETED | VerificationGate | decision, candidate_id, evidence_id |
| RUN_COMPLETED | RevisionController | status, terminal_reason |

### Artifact Relationships

```
run
 ├── task
 ├── prompt(s)
 ├── candidate(s)
 ├── evidence artifact(s)
 ├── revision iterations
 ├── Oracle evaluations
 ├── verification result
 └── terminal state
```

### Reconstruction

Given `run_id`, reconstruct:
- TaskDefinition
- All PromptRequests
- All CandidateArtifacts
- All EvidenceArtifacts
- Revision sequence
- Final VerificationResult
- Terminal state

## Tests

- 25 new deterministic unit tests
- All 518 tests pass (25 new + 493 existing)

## Historical Preservation

- All DIAGNOSTIC artifacts: UNCHANGED
- All AUTH records: UNCHANGED
- All P090–P142 records: UNCHANGED

## Rollback

Remove `tests/test_provenance_tracker.py`.
Revert `eger/provenance/tracker.py` to P138 version.
