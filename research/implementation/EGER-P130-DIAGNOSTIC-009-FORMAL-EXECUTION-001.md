# EGER-P130 — DIAGNOSTIC-009 E3a Wording Deconfounding Execution

## Execution Record

**Date:** 2026-08-31
**Authorization:** EGER-AUTH-015-DIAGNOSTIC-009
**Model:** opencode/mimo-v2.5-free (MODEL-005)
**Protocol:** P126/P127 2×2 factorial wording deconfounding

## Execution Summary

| Metric | Value |
|--------|-------|
| Authorized run slots | 96 |
| Checkpoint completed | 96 |
| Manifests written | 94 |
| Manifests missing (timeout interrupt) | 2 |
| Incomplete (provider failure) | 0 |

**Note:** 2 runs (BENCH2-002-A2-run03, BENCH2-002-A3-run07) were checkpointed as completed but their manifest files were not written before the shell timeout. The model calls succeeded (per checkpoint), but artifacts are incomplete. These are classified as having incomplete artifacts, not as experimental failures.

## Results by Cell

| Task | Condition | Framing | Tech | Adherent | Rate | 95% CI |
|------|-----------|---------|------|----------|------|--------|
| BENCH2-002 | A4 | Narrow | No | 8/8 | **100%** | [65.4%, 100.0%] |
| BENCH2-002 | A1 | Broad | No | 8/8 | **100%** | [65.4%, 100.0%] |
| BENCH2-002 | A2 | Narrow | Yes | 5/7 | **71%** | [30.2%, 96.2%] |
| BENCH2-002 | A3 | Broad | Yes | 7/7 | **100%** | [61.5%, 100.0%] |
| BENCH2-004 | A4 | Narrow | No | 6/8 | **75%** | [36.2%, 96.7%] |
| BENCH2-004 | A1 | Broad | No | 8/8 | **100%** | [65.4%, 100.0%] |
| BENCH2-004 | A2 | Narrow | Yes | 7/8 | **88%** | [49.1%, 99.7%] |
| BENCH2-004 | A3 | Broad | Yes | 7/8 | **88%** | [49.1%, 99.7%] |
| BENCH2-005 | A4 | Narrow | No | 2/8 | **25%** | [3.3%, 63.8%] |
| Bench2-005 | A1 | Broad | No | 8/8 | **100%** | [65.4%, 100.0%] |
| BENCH2-005 | A2 | Narrow | Yes | 8/8 | **100%** | [65.4%, 100.0%] |
| BENCH2-005 | A3 | Broad | Yes | 8/8 | **100%** | [65.4%, 100.0%] |

## Factorial Summary

| | Tech NO | Tech YES |
|--|---------|----------|
| **Narrow (A4)** | 16/24 = 67% | 20/23 = 87% |
| **Broad (A1/A3)** | 24/24 = 100% | 22/23 = 96% |

## Key Observations (Descriptive Only)

1. **A1 (broad framing only): 24/24 = 100%** — perfect adherence across all tasks
2. **A4 (BASE): 16/24 = 67%** — variable across tasks (25%-100%)
3. **A2 (tech only): 20/23 = 87%** — improved over A4 on 004/005, but lower on 002
4. **A3 (both): 22/23 = 96%** — near-perfect, one miss on 004

## Artifact Locations

```
research/experiments/EGER-EXP-001/formal/DIAGNOSTIC-009/
├── BENCH2-002/{A4,A1,A2,A3}/ (manifests + raw)
├── BENCH2-004/{A4,A1,A2,A3}/ (manifests + raw)
├── BENCH2-005/{A4,A1,A2,A3}/ (manifests + raw)
├── RUN_INDEX.json
└── _checkpoint.json
```

## Safety Verification

- **313/313 regression tests PASS**
- **No model substitution**
- **No provider substitution**
- **No unauthorized retries**
- **Historical artifacts untouched**
- **C3: NOT AUTHORIZED**

## Status

```
P130 COMPLETE
DIAGNOSTIC-009 EXECUTION COMPLETE
96/96 CHECKPOINT COMPLETED
94/96 MANIFESTS WRITTEN
2 MANIFESTS MISSING (timeout interrupt)
0 PROVIDER FAILURES
313/313 TESTS PASS
HISTORICAL ARTIFACTS PRESERVED
C3: NOT AUTHORIZED
NEXT: P131 SCIENTIFIC REVIEW
```
