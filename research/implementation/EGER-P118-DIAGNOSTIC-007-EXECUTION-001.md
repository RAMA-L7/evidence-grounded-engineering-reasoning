# EGER-P118 — DIAGNOSTIC-007 Base-Rate Stabilization Execution

## Execution Record

**Date:** 2026-08-31
**Authorization:** EGER-AUTH-013-BASE-RATE-STABILIZATION
**Model:** opencode/mimo-v2.5-free (MODEL-005)
**Protocol:** P114/P115 20-run base-rate stabilization

## Execution Summary

| Metric | Value |
|--------|-------|
| Total runs attempted | 20 |
| Completed | 18 |
| Incomplete (provider failure) | 2 (Base-run07, Base-run08) |
| Budget authorized | 60 |
| Calls consumed | ~54 (18 × 3) |

## Primary Result

| Metric | Value |
|--------|-------|
| Adherent | 7/18 |
| Rate | **39%** |
| 95% Clopper-Pearson CI | **[17.8%, 63.4%]** |
| Activated | 18/18 (100%) |

## Run-by-Run Detail

| Run | Adherent | delta | Activated | Status |
|-----|----------|-------|-----------|--------|
| 01 | Y | -2 | Y | COMPLETED |
| 02 | Y | -2 | Y | COMPLETED |
| 03 | Y | -2 | Y | COMPLETED |
| 04 | N | 0 | Y | COMPLETED |
| 05 | N | 0 | Y | COMPLETED |
| 06 | N | 0 | Y | COMPLETED |
| 07 | — | — | — | INCOMPLETE |
| 08 | — | — | — | INCOMPLETE |
| 09 | Y | -2 | Y | COMPLETED |
| 10 | N | 0 | Y | COMPLETED |
| 11 | N | 0 | Y | COMPLETED |
| 12 | N | 0 | Y | COMPLETED |
| 13 | Y | -2 | Y | COMPLETED |
| 14 | N | 0 | Y | COMPLETED |
| 15 | Y | -2 | Y | COMPLETED |
| 16 | Y | -2 | Y | COMPLETED |
| 17 | N | 0 | Y | COMPLETED |
| 18 | N | 0 | Y | COMPLETED |
| 19 | N | 0 | Y | COMPLETED |
| 20 | N | 0 | Y | COMPLETED |

## Historical Comparison

| Experiment | Runs | Adherent | Rate | 95% CI |
|------------|------|----------|------|--------|
| P090 | 10 | 4 | 40% | [12.6%, 72.9%] |
| DIAGNOSTIC-006 Base | 10 | 8 | 80% | [45.8%, 100.0%] |
| **DIAGNOSTIC-007** | **18** | **7** | **39%** | **[17.8%, 63.4%]** |

## Combined Base Evidence

| Source | Adherent | Total | Rate |
|--------|----------|-------|------|
| P090 + DIAGNOSTIC-006 + DIAGNOSTIC-007 | 19 | 38 | 50% |

The three Base experiments produce: 4/10 + 8/10 + 7/18 = 19/38 = 50%.

DIAGNOSTIC-007's 39% closely matches P090's 40%, suggesting the DIAGNOSTIC-006 Base result (80%) was the outlier.

## Provider Failures

- **Base-run07:** Model call timed out at 60s. Build initiated but no response.
- **Base-run08:** Same timeout pattern.
- Both recorded as INCOMPLETE per AUTH-013 frozen failure policy. No retry, substitution, or fallback.

## Artifact Locations

```
research/experiments/EGER-EXP-001/formal/DIAGNOSTIC-007/
├── raw/Base-run01/ through Base-run20/ (18 with artifacts)
├── manifest-Base-run01.json through Base-run20.json (18 manifests)
├── RUN_INDEX.json
└── _checkpoint.json
```

## Safety Verification

- **274/274 regression tests PASS**
- **Historical RQ-4 artifacts: UNTOUCHED**
- **DIAGNOSTIC-006: UNTOUCHED**
- **BENCH-002: UNTOUCHED**
- **MODEL-005 configuration: FROZEN**
- **C3: NOT AUTHORIZED**

## Status

```
P118 COMPLETE
DIAGNOSTIC-007 EXECUTION COMPLETE
18/20 COMPLETED
2 PROVIDER FAILURES RECORDED
7/18 ADHERENT (39%)
95% CI: [17.8%, 63.4%]
AUTHORIZATION: EGER-AUTH-013
NO MODEL SUBSTITUTION
NO RETRIES
P119 SCIENTIFIC REVIEW NEXT
C3: NOT AUTHORIZED
```
