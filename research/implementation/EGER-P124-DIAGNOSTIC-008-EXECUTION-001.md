# EGER-P124 — DIAGNOSTIC-008 Cross-Task E3a Replication Execution

## Execution Record

**Date:** 2026-08-31
**Authorization:** EGER-AUTH-014-DIAGNOSTIC-008
**Model:** opencode/mimo-v2.5-free (MODEL-005)
**Protocol:** P120/P121 60-run cross-task E3a replication

## Execution Summary

| Metric | Value |
|--------|-------|
| Total attempted | 60 |
| Completed | 57 |
| Incomplete (provider failure) | 3 |
| Budget authorized | 180 |
| Calls consumed | ~171 (57 × 3) |

## Results by Cell

| Task | Condition | Completed | Adherent | Rate | 95% CI | E3a−BASE |
|------|-----------|-----------|----------|------|--------|----------|
| BENCH2-002 | BASE | 10 | 7 | 70% | [35.9%, 93.1%] | |
| BENCH2-002 | E3a | 9 | 9 | **100%** | [68.7%, 100.0%] | **+30pp** |
| BENCH2-004 | BASE | 10 | 7 | 70% | [35.9%, 93.1%] | |
| BENCH2-004 | E3a | 9 | 8 | **89%** | [53.5%, 99.7%] | **+19pp** |
| BENCH2-005 | BASE | 10 | 6 | 60% | [27.1%, 87.4%] | |
| BENCH2-005 | E3a | 9 | 8 | **89%** | [53.5%, 99.7%] | **+29pp** |

## Cross-Task Summary

| Metric | BASE (all tasks) | E3a (all tasks) |
|--------|-----------------|----------------|
| Completed | 30 | 27 |
| Adherent | 20 | 25 |
| Rate | 67% | 93% |
| Incomplete | 0 | 3 |

## Key Finding

**E3a improved adherence on ALL THREE tasks:**

| Task | BASE | E3a | Improvement |
|------|------|-----|-------------|
| BENCH2-002 | 70% | 100% | +30pp |
| BENCH2-004 | 70% | 89% | +19pp |
| BENCH2-005 | 60% | 89% | +29pp |

This constitutes a **strong replication signal** per P120's preregistered interpretation rules.

## Provider Failures

3 incomplete runs (one per E3a task):
- BENCH2-002-E3a: provider timeout
- BENCH2-004-E3a: provider timeout
- BENCH2-005-E3a: provider timeout

All recorded as INCOMPLETE per AUTH-014 frozen failure policy. No retry, substitution, or fallback.

## Artifact Locations

```
research/experiments/EGER-EXP-001/formal/DIAGNOSTIC-008/
├── BENCH2-002/BASE/ (10 manifests + raw)
├── BENCH2-002/E3a/  (9 manifests + raw)
├── BENCH2-004/BASE/ (10 manifests + raw)
├── BENCH2-004/E3a/  (9 manifests + raw)
├── BENCH2-005/BASE/ (10 manifests + raw)
├── BENCH2-005/E3a/  (9 manifests + raw)
├── RUN_INDEX.json
└── _checkpoint.json
```

## Safety Verification

- **293/293 regression tests PASS**
- **Historical experiments: UNTOUCHED**
- **No model substitution**
- **No unauthorized retries**
- **C3: NOT AUTHORIZED**

## Status

```
P124 COMPLETE
DIAGNOSTIC-008 EXECUTION COMPLETE
57/60 COMPLETED
3 PROVIDER FAILURES
E3a > BASE ON ALL 3 TASKS
293/293 TESTS PASS
HISTORICAL ARTIFACTS PRESERVED
C3: NOT AUTHORIZED
NEXT: P125 SCIENTIFIC REVIEW
```
