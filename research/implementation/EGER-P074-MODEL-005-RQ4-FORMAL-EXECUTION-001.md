# EGER-P074 — MODEL-005 RQ-4 Formal Execution

| Field | Value |
|---|---|
| ID | EGER-P074-MODEL-005-RQ4-FORMAL-EXECUTION-001 |
| Date | 2026-08-28 |
| Authorization | EGER-AUTH-007 |
| Status | **EXECUTION COMPLETE — SCIENTIFIC REVIEW REQUIRED** |

---

## 1. Executive Summary

Executed the frozen paired RQ-4 experiment using MODEL-005 (mimo-v2.5-free) under AUTH-007. All 6 BENCH-002 tasks completed. 3/6 tasks showed treatment improvement (fewer ERROR findings with structured feedback). 3/6 tasks showed no difference. 0/6 tasks showed control improvement.

---

## 2. Execution Details

| Parameter | Value |
|-----------|-------|
| Model | opencode/mimo-v2.5-free |
| MODEL_ID | EGER-MODEL-005 |
| Benchmark | BENCH-002 v0.1 (6 tasks) |
| Oracle | 3b5c2f2 |
| Metadata | eger.design_metadata.v1 |
| Temperature | 0.0 |
| Max tokens | 2048 |
| Tools | [] |
| Namespace | formal/RQ4-MODEL-005/ |
| Total artifacts | 67 files |

---

## 3. Task Completion

| Task | Status |
|------|--------|
| BENCH2-001 | ✅ COMPLETED |
| BENCH2-002 | ✅ COMPLETED |
| BENCH2-003 | ✅ COMPLETED |
| BENCH2-004 | ✅ COMPLETED |
| BENCH2-005 | ✅ COMPLETED |
| BENCH2-006 | ✅ COMPLETED |

**6/6 tasks completed. 0 missing. 0 incomplete.**

---

## 4. Primary Metric Results (ERROR-Severity Delta)

| Task | Init Errors | Control Final | Control Δ | Treatment Final | Treatment Δ | Treatment Effect |
|------|-------------|---------------|-----------|-----------------|-------------|------------------|
| BENCH2-001 | 2 | 2 | 0 | 2 | 0 | **0** |
| BENCH2-002 | 2 | 2 | 0 | 0 | -2 | **-2** |
| BENCH2-003 | 0 | 0 | 0 | 0 | 0 | **0** |
| BENCH2-004 | 2 | 2 | 0 | 0 | -2 | **-2** |
| BENCH2-005 | 2 | 2 | 0 | 0 | -2 | **-2** |
| BENCH2-006 | 0 | 0 | 0 | 0 | 0 | **0** |

---

## 5. Paired Comparison Summary

| Outcome | Count | Tasks |
|---------|-------|-------|
| Treatment better (fewer errors) | **3** | BENCH2-002, BENCH2-004, BENCH2-005 |
| Control better | **0** | — |
| Tie (no difference) | **3** | BENCH2-001, BENCH2-003, BENCH2-006 |

---

## 6. Key Observations (Descriptive, Not Causal Interpretation)

### Control condition
- **Control delta_error = 0 for ALL 6 tasks.** The model never reduced ERROR findings without feedback.
- Control proposal_changed: 4/6 tasks (model changed output but not error count).

### Treatment condition
- **Treatment delta_error = -2 for 3 tasks** (BENCH2-002, BENCH2-004, BENCH2-005).
- Treatment delta_error = 0 for 3 tasks (BENCH2-001, BENCH2-003, BENCH2-006).
- All 6 treatment tasks showed proposal_changed = True.

### Where improvement occurred
- BENCH2-002: initial had 2 errors → treatment reduced to 0 (missing input_delay + output_delay)
- BENCH2-004: initial had 2 errors → treatment reduced to 0
- BENCH2-005: initial had 2 errors → treatment reduced to 0

### Where no improvement occurred
- BENCH2-001: initial had 2 errors → treatment kept 2 errors (scope: FULL → FULL)
- BENCH2-003: initial had 0 errors → treatment kept 0 (already correct)
- BENCH2-006: initial had 0 errors → treatment kept 0 (already correct)

---

## 7. Secondary Metrics

### Proposal Change

| Branch | proposal_changed |
|--------|-----------------|
| Control | 4/6 (67%) |
| Treatment | 6/6 (100%) |

### Evidence Scope

| Task | Initial Scope | Control Final | Treatment Final |
|------|--------------|---------------|-----------------|
| BENCH2-001 | FULL | FULL | FULL |
| BENCH2-002 | FULL | FULL | PARTIAL |
| BENCH2-003 | FULL | FULL | PARTIAL |
| BENCH2-004 | FULL | FULL | PARTIAL |
| BENCH2-005 | PARTIAL | PARTIAL | PARTIAL |
| BENCH2-006 | FULL | FULL | PARTIAL |

Note: Some treatment final scopes are PARTIAL — this may indicate the model's revised SDC introduced constructs that the metadata cannot fully validate. This requires investigation during scientific review.

### CVR

| Task | Initial CVR | Control Final | Treatment Final |
|------|------------|---------------|-----------------|
| BENCH2-001 | 1.0 | 1.0 | 1.0 |
| BENCH2-002 | 1.0 | 1.0 | None |
| BENCH2-003 | 1.0 | 1.0 | None |
| BENCH2-004 | 1.0 | 1.0 | None |
| BENCH2-005 | None | None | None |
| BENCH2-006 | 1.0 | 1.0 | None |

---

## 8. Run Identifiers

| Task | Run ID | Control Hash | Treatment Hash |
|------|--------|-------------|----------------|
| BENCH2-001 | RQ4-AEA4AFFE | — | — |
| BENCH2-002 | RQ4-1F23EEB5 | — | — |
| BENCH2-003 | RQ4-8840E4EF | — | — |
| BENCH2-004 | RQ4-7278E13E | — | — |
| BENCH2-005 | RQ4-5EB06571 | — | — |
| BENCH2-006 | RQ4-D71B03C1 | — | — |

---

## 9. Regression

```
162 passed in 21.58s
```

No test regressions. No code was modified during execution.

---

## 10. Historical Preservation

| Item | Status |
|------|--------|
| C0 | ✅ UNCHANGED |
| C1 | ✅ UNCHANGED (1 manifest) |
| C2 canned | ✅ UNCHANGED (1 manifest) |
| MODEL-004-C2 | ✅ UNCHANGED (1 manifest) |
| BENCH-002 | ✅ UNCHANGED |
| MODEL-004 | ✅ FROZEN |
| Ṛta | ✅ 3b5c2f2, HEAD unchanged |

---

## 11. Artifact Namespace

```
research/experiments/EGER-EXP-001/formal/RQ4-MODEL-005/
    ├── RUN_INDEX.json
    ├── control/
    │   ├── manifests/ (6 files)
    │   └── raw/ (6 directories × 4 files = 24 files)
    └── treatment/
        ├── manifests/ (6 files)
        └── raw/ (6 directories × 5 files = 30 files)
```

Total: 67 files (1 RUN_INDEX + 12 manifests + 54 raw artifacts).

---

## 12. deviations

None. Execution followed AUTH-007 exactly.

---

## 13. Status

```
P074 COMPLETE
RQ-4 FORMAL EXECUTION COMPLETE
6/6 TASKS COMPLETED
SCIENTIFIC REVIEW REQUIRED
DO NOT INTERPRET RESULTS YET
C3 NOT AUTHORIZED
```

---

## 14. Next Gate

**P075 — RQ-4 Scientific Review**

The scientific review should:
1. Interpret the primary metric results
2. Investigate why control never reduced errors
3. Investigate why treatment improved 3/6 tasks but not the other 3
4. Assess the PARTIAL scope in treatment final evaluations
5. Determine whether the results answer RQ-4
6. Assess limitations (free-tier model, n=6, temperature 0.0)
