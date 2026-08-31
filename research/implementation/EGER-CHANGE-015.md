# EGER-CHANGE-015 — Cross-Task E3a Replication (DIAGNOSTIC-008)

## Change Identifier
EGER-CHANGE-015

## Date
2026-08-31

## Why

DIAGNOSTIC-006 E3a produced 10/10 adherence on BENCH2-001. P119 recommended cross-task replication to determine whether the broader-objective effect generalizes.

## Relationship to P120

Implements the P120 frozen design:
- 3 tasks × 2 conditions × 10 runs = 60 runs
- 180-call budget
- MODEL-005 only

## Files Introduced

| File | Purpose |
|------|---------|
| `research/experiments/EGER-EXP-001/run_cross_task_e3a_replication.py` | DIAGNOSTIC-008 runner |
| `tests/test_cross_task_e3a_replication.py` | 19 deterministic tests |
| `EGER-P120-CROSS-TASK-E3A-REPLICATION-DESIGN-001.md` | Design record |
| `EGER-P121-...001.md` | Implementation record |

## Frozen Protocol

- Model: opencode/mimo-v2.5-free (MODEL-005)
- Temperature: 0.0, Tools: [], Max tokens: 2048, Timeout: 60s
- Tasks: BENCH2-002, BENCH2-004, BENCH2-005
- Conditions: BASE (original objective) vs E3a (broader objective)
- Namespace: formal/DIAGNOSTIC-008/

## Budget

180 calls (60 runs × 3)

## Historical Preservation

All prior experiments untouched.
