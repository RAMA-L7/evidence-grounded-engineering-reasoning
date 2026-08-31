# EGER-P112 — DIAGNOSTIC-006 Mechanism Investigation Formal Execution

## Execution Record

**Date:** 2026-08-31
**Authorization:** EGER-AUTH-012-RQ4-MECHANISM
**Model:** opencode/mimo-v2.5-free (MODEL-005)
**Protocol:** P107/P108 4-condition mechanism investigation

## Execution Summary

| Metric | Value |
|--------|-------|
| Total runs attempted | 40 |
| Completed | 39 |
| Incomplete (provider failure) | 1 (E4a-run08) |
| Budget used | ~117 model+oracle calls |
| Provider failures | 1 (E4a-run08 — model call returned empty) |

## Condition Results

| Condition | Description | Adherent | Rate | 95% CI | Activated |
|-----------|-------------|----------|------|--------|-----------|
| **Base** | Baseline: minimal SDC + full feedback | 8/10 | **80%** | [45.8%, 100.0%] | 10/10 |
| **E2b** | Base + irrelevant SDC constructs | 9/10 | **90%** | [57.3%, 100.0%] | 10/10 |
| **E3a** | Base + broader task objective | 10/10 | **100%** | [71.4%, 100.0%] | 10/10 |
| **E4a** | Base + ERROR-only feedback | 4/9 | **44%** | [14.2%, 100.0%] | 5/9 |

## Overall

- **31/39 adherent (79%)**
- **35/39 activated (90%)**

## Run-by-Run Detail

### Base (BENCH2-001 + minimal SDC + full feedback)

| Run | Adherent | delta | Activated |
|-----|----------|-------|-----------|
| 01 | Y | -2 | Y |
| 02 | Y | -2 | Y |
| 03 | Y | -2 | Y |
| 04 | N | 0 | Y |
| 05 | Y | -2 | Y |
| 06 | N | 0 | Y |
| 07 | Y | -2 | Y |
| 08 | Y | -2 | Y |
| 09 | Y | -2 | Y |
| 10 | Y | -2 | Y |

### E2b (Base + irrelevant SDC constructs)

| Run | Adherent | delta | Activated |
|-----|----------|-------|-----------|
| 01 | Y | -2 | Y |
| 02 | Y | -2 | Y |
| 03 | Y | -2 | Y |
| 04 | Y | -2 | Y |
| 05 | Y | -2 | Y |
| 06 | N | 0 | Y |
| 07 | Y | -2 | Y |
| 08 | Y | -2 | Y |
| 09 | Y | -2 | Y |
| 10 | Y | -2 | Y |

### E3a (Base + broader task objective)

| Run | Adherent | delta | Activated |
|-----|----------|-------|-----------|
| 01 | Y | -2 | Y |
| 02 | Y | -2 | Y |
| 03 | Y | -2 | Y |
| 04 | Y | -2 | Y |
| 05 | Y | -2 | Y |
| 06 | Y | -2 | Y |
| 07 | Y | -2 | Y |
| 08 | Y | -2 | Y |
| 09 | Y | -2 | Y |
| 10 | Y | -2 | Y |

### E4a (Base + ERROR-only feedback)

| Run | Adherent | delta | Activated |
|-----|----------|-------|-----------|
| 01 | N | 0 | Y |
| 02 | Y | -2 | Y |
| 03 | Y | -2 | Y |
| 04 | N | 0 | N |
| 05 | N | 0 | N |
| 06 | N | 0 | N |
| 07 | Y | -2 | Y |
| 08 | INCOMPLETE | — | — |
| 09 | N | 0 | N |
| 10 | Y | -2 | Y |

## Provider Failure

- **E4a-run08:** Model call returned empty/INCOMPLETE. Provider accepted request but returned no usable output. Recorded as INCOMPLETE per AUTH-012 frozen failure policy. No retry, substitution, or fallback.

## Artifact Locations

```
research/experiments/EGER-EXP-001/formal/DIAGNOSTIC-006/
├── base-bench2-001/          (10 manifests + raw runs)
├── E2b-added-constructs/     (10 manifests + raw runs)
├── E3a-broader-objective/    (10 manifests + raw runs)
├── E4a-error-only-feedback/  (9 manifests + raw runs, run08 missing)
├── RUN_INDEX.json
└── _checkpoint.json
```

## Safety Verification

- **258/258 regression tests PASS**
- **Historical RQ-04 artifacts: UNTOUCHED**
- **BENCH-002: UNTOUCHED**
- **MODEL-005 configuration: FROZEN**
- **Oracle/metadata: UNTOUCHED**
- **C3: NOT AUTHORIZED**

## Budget

| Resource | Authorized | Used |
|----------|------------|------|
| Model calls | 40 | 39 (1 incomplete) |
| Oracle calls | 80 | 78 (2 skipped with incomplete) |
| Total | 120 | 117 |

## Status

```
P112 COMPLETE
DIAGNOSTIC-006 EXECUTION COMPLETE
39/40 RUNS COMPLETED
1 PROVIDER FAILURE RECORDED
P113 SCIENTIFIC REVIEW NEXT
```
