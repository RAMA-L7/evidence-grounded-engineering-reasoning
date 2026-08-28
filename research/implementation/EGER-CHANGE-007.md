# EGER-CHANGE-007 — RQ4 Paired Runner Implementation

| Field | Value |
|---|---|
| ID | EGER-CHANGE-007 |
| Date | 2026-08-28 |
| Governing Design | EGER-P061-CONTROLLED-RQ4-EXPERIMENT-DESIGN-001 |
| Status | **IMPLEMENTED** |
| Tests | 162/162 PASS |

## 1. Scope

### INCLUDED

| What | Description |
|------|-------------|
| `formal_runner_rq4.py` | New RQ4 paired control/treatment runner |
| `tests/test_rq4_runner.py` | 32 deterministic unit tests (T060–T091) |
| `formal/RQ4/` artifact namespace | New, separate from C0/C1/C2/C2-live |

### EXCLUDED (must not change)

| What | Status |
|------|--------|
| BENCH-002 tasks | UNCHANGED |
| MODEL-003 | UNCHANGED |
| MODEL-004 | FROZEN |
| C0/C1/C2 artifacts | PRESERVED |
| C2-live artifacts | PRESERVED |
| MODEL-004 historical | PRESERVED |
| Oracle semantics | UNCHANGED |
| structured_feedback.py | UNCHANGED |
| feedback.py | UNCHANGED |
| EngineerAdapter | UNCHANGED |
| LiveEngineerModel | UNCHANGED |
| EvidenceOracle | UNCHANGED |
| Ṛta | UNCHANGED |
| C3 | NOT AUTHORIZED |

## 2. Implementation

### Files Changed

| File | Change | Lines |
|------|--------|-------|
| `research/experiments/EGER-EXP-001/formal_runner_rq4.py` | NEW — RQ4 paired runner | ~350 |
| `tests/test_rq4_runner.py` | NEW — 32 unit tests | ~550 |

### Files NOT Changed

All existing source and test files remain byte-identical.

## 3. Experimental Architecture

```
Same initial candidate (Call 1)
         │
    ┌────┴────┐
    │         │
  CONTROL  TREATMENT
  (NO FB)  (STRUCTURED FB)
    │         │
    ↓         ↓
  FINAL_C   FINAL_T
    │         │
    └────┬────┘
         ↓
     COMPARE
```

## 4. Model Configuration

| Parameter | Value | Frozen |
|-----------|-------|--------|
| Provider | opencode | ✅ |
| Model | opencode/nemotron-3-ultra-free | ✅ |
| Temperature | 0.0 | ✅ |
| Max tokens | 2048 | ✅ |
| Tools | [] | ✅ |
| Timeout | 60s | ✅ |
| Prompt | eger.prompt.v1 | ✅ |

## 5. Primary Metric (Pre-Registered)

**Error-count delta** — counts only ERROR-severity findings:

```
delta_error = error_count(final) - error_count(initial)
```

ERROR findings: SDC-005, SDC-006, SDC-007.

## 6. Secondary Metrics

- proposal_changed (hash inequality)
- CVR delta
- Evidence scope transition
- Warning count delta

## 7. Tests

| Test ID | Category | Status |
|---------|----------|--------|
| T060 | Same initial candidate | ✅ PASS |
| T061 | Control receives NO feedback | ✅ PASS |
| T062 | Treatment receives structured feedback | ✅ PASS |
| T063 | MODEL-004 identity fixed | ✅ PASS |
| T064 | Model config identical between branches | ✅ PASS |
| T065 | Oracle config identical | ✅ PASS |
| T066 | Only feedback differs | ✅ PASS |
| T067 | ERROR-only primary metric | ✅ PASS |
| T068 | WARNING excluded from primary | ✅ PASS |
| T069 | INFO excluded from primary | ✅ PASS |
| T070 | CVR persistence | ✅ PASS |
| T071 | Evidence scope persistence | ✅ PASS |
| T072 | proposal_changed calculation | ✅ PASS |
| T073 | Candidate hash persistence | ✅ PASS |
| T074 | Evidence hash persistence | ✅ PASS |
| T075 | Feedback hash persistence | ✅ PASS |
| T076 | Branch identity persistence | ✅ PASS |
| T077 | Budget enforcement | ✅ PASS |
| T078 | Failure: model Call 1 | ✅ PASS |
| T079 | Failure: oracle Call 1 | ✅ PASS |
| T080 | Evaluator-only isolation | ✅ PASS |
| T081 | No credential leakage | ✅ PASS |
| T082 | No Rta access/modification | ✅ PASS |
| T083 | Historical artifact isolation | ✅ PASS |
| T084 | RQ4 namespace isolation | ✅ PASS |
| T085 | Treatment effect calculation | ✅ PASS |
| T086 | Materialized artifact files | ✅ PASS |
| T087 | Design metadata loaded | ✅ PASS |
| T088 | No metadata in engineer prompt | ✅ PASS |
| T089 | Finding count function | ✅ PASS |
| T090 | Error delta function | ✅ PASS |
| T091 | Error delta no change | ✅ PASS |

## 8. Regression

| Suite | Count | Status |
|-------|-------|--------|
| Original tests | 95 | ✅ ALL PASS |
| Measurement tests (T025–T059) | 35 | ✅ ALL PASS |
| RQ4 tests (T060–T091) | 32 | ✅ ALL PASS |
| **Total** | **162** | **✅ ALL PASS** |

## 9. Information Boundary

| Tier | Control | Treatment |
|------|---------|-----------|
| ENGINEER_VISIBLE | task + candidate | task + candidate + structured feedback |
| ORACLE_VISIBLE | design metadata | design metadata |
| EVALUATOR_ONLY | hidden answers | hidden answers |

Verified by T080, T088.

## 10. Preservation

| Item | Status |
|------|--------|
| BENCH-002 | ✅ UNCHANGED (6 hashes verified) |
| C0 | ✅ PRESERVED (6 manifests) |
| C1 | ✅ PRESERVED (6 manifests) |
| C2 canned | ✅ PRESERVED (6 manifests) |
| MODEL-004 historical | ✅ PRESERVED (4 manifests) |
| MODEL-003 | ✅ UNCHANGED |
| MODEL-004 | ✅ FROZEN |
| Ṛta | ✅ 3b5c2f2, unchanged |
| structured_feedback.py | ✅ UNCHANGED |
| feedback.py | ✅ UNCHANGED |

## 11. RQ-4 Execution

**NOT PERFORMED.**

RQ4 runner is ready for post-implementation readiness review (P063).
