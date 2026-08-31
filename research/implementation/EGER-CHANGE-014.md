# EGER-CHANGE-014 — Base-Rate Stabilization (DIAGNOSTIC-007)

## Change Identifier
EGER-CHANGE-014

## Date
2026-08-31

## Why

P090 and DIAGNOSTIC-006 Base produced different adherence rates (40% vs 80%) for the same BENCH2-001 configuration. A 20-run replication establishes a more reliable baseline before cross-task E3a comparison.

## Relationship to P114

Implements the P114 frozen design exactly:
- 20 sequential identical BENCH2-001 Base runs
- MODEL-005 (mimo-v2.5-free)
- 51-char minimal SDC
- Full structured feedback
- 60-call budget

## Files Introduced

| File | Purpose |
|------|---------|
| `research/experiments/EGER-EXP-001/run_base_rate_stabilization.py` | DIAGNOSTIC-007 runner |
| `tests/test_base_rate_stabilization.py` | 16 deterministic tests |
| `EGER-P114-BASE-RATE-STABILIZATION-DESIGN-001.md` | Design record |
| `EGER-P115-BASE-RATE-STABILIZATION-IMPLEMENTATION-001.md` | Implementation record |

## Frozen Protocol

- Model: opencode/mimo-v2.5-free (MODEL-005)
- Temperature: 0.0
- Tools: []
- Max tokens: 2048
- Timeout: 60s
- Task: BENCH2-001
- SDC: 51-char minimal
- Feedback: full structured EvidenceArtifact
- Oracle: EGER EvidenceOracle
- Namespace: formal/DIAGNOSTIC-007/

## Budget

60 calls (20 runs × 3)

## No-Live-Execution Constraint

This change control covers implementation only. No live model calls. Execution requires separate authorization.

## Historical Preservation

- DIAGNOSTIC-006: untouched
- DIAGNOSTIC-005/004/003/002/001: untouched
- RQ-4 MODEL-005 results: untouched
- BENCH-002: untouched
- MODEL-004 artifacts: untouched
- C0/C1/C2: untouched
- Rta: untouched

## Rollback

DIAGNOSTIC-007 is isolated in its own namespace. Removal = delete `formal/DIAGNOSTIC-007/` and the runner/test files.
