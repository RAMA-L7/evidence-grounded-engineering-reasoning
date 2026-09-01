# EGER-CHANGE-018 — Evidence Pipeline Implementation

## Date
2026-09-01

## Status
**IMPLEMENTED**

## Reason for Change

P137 (Architecture Implementation Design) identified the need for an
EvidenceNormalizer that connects the existing Oracle layer to the new
P138 evidence contracts. P139 implements this pipeline.

## Affected Modules

| Module | Change |
|--------|--------|
| `eger/evidence/normalizer.py` | NEW — EvidenceNormalizer |
| `eger/evidence/__init__.py` | Updated — exports EvidenceNormalizer |

## Oracle → Evidence Transformation

```
Oracle EvidenceArtifact
    ↓
EvidenceNormalizer.normalize()
    ↓
P138 EvidenceArtifact
```

### Severity Mapping

| Oracle Severity | P138 Severity | Notes |
|----------------|---------------|-------|
| error | error | Direct mapping |
| warning | warning | Direct mapping |
| info | info | Direct mapping |
| ERROR | error | Case-insensitive |
| WARNING | warning | Case-insensitive |
| INFO | info | Case-insensitive |
| unknown | FAIL CLOSED | Raises ValueError |

### Scope Mapping

| Oracle Scope | P138 Scope |
|-------------|-----------|
| VALIDATED | FULL |
| PARTIALLY_VALIDATED | PARTIAL |
| NETLIST_REQUIRED | INSUFFICIENT |
| UNSUPPORTED | UNSUPPORTED |
| TCL_EXECUTION_REQUIRED | UNSUPPORTED |
| NOT_VALIDATED | UNSUPPORTED |

### Failure Semantics

| Oracle Failure | P138 Response |
|---------------|---------------|
| Success | Normalized EvidenceArtifact |
| Parser failure | INCOMPLETE_MEASUREMENT (error finding) |
| Unavailable | INCOMPLETE_MEASUREMENT (error finding) |
| Malformed | INCOMPLETE_MEASUREMENT (error finding) |
| Unknown severity | FAIL CLOSED (ValueError) |

## Tests

- 29 new deterministic unit tests
- All 406 tests pass (29 new + 377 existing)

## Historical Preservation

- All DIAGNOSTIC artifacts: UNCHANGED
- All AUTH records: UNCHANGED
- All P090–P138 records: UNCHANGED

## Rollback

Remove `eger/evidence/normalizer.py` and `tests/test_evidence_pipeline.py`.
Revert `eger/evidence/__init__.py` to P138 version.
