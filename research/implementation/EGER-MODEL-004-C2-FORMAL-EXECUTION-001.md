# EGER-MODEL-004-C2-FORMAL-EXECUTION-001 — Formal Execution Report

| Field | Value |
|---|---|
| ID | EGER-MODEL-004-C2-FORMAL-EXECUTION-001 |
| Date | 2026-08-27 |
| Authorization | EGER-AUTH-005 |
| Model | EGER-MODEL-004 (opencode/nemotron-3-ultra-free) |
| Condition | C2 — Structured EvidenceArtifact |
| Status | **4/6 COMPLETED — TREATMENT ACTIVATION CONFIRMED** |

---

## 1. Executive Summary

**4/6 tasks completed. All 4 show CHANGED=True.** 2 tasks failed due to provider rate limits (INCOMPLETE_TREATMENT). Treatment activation is confirmed across all completed tasks.

## 2. Task-Level Results

| Task | Status | Call 1 Hash | Call 2 Hash | CHANGED? | O1 Scope | O2 Scope | O1→O2 Findings | Outcome |
|------|--------|------------|------------|----------|----------|----------|----------------|---------|
| BENCH2-001 | COMPLETED | 6745a1b832a6 | 0577343abd95 | **YES** | INSUFFICIENT | PARTIAL | 23 → 13 | VALID_ARTIFACT |
| BENCH2-002 | COMPLETED | 06e33e7bb9d9 | 4bc9344514db | **YES** | INSUFFICIENT | PARTIAL | 24 → 8 | VALID_ARTIFACT |
| BENCH2-003 | INCOMPLETE | 9eec00d3ddda | — | NOT MEASURED | INSUFFICIENT | — | — | INCOMPLETE_TREATMENT |
| BENCH2-004 | COMPLETED | a697e7203af4 | b91da2b4e8a6 | **YES** | INSUFFICIENT | INSUFFICIENT | 25 → 22 | INVALID_ARTIFACT |
| BENCH2-005 | COMPLETED | 0f5d577a0e8b | 4ddd86325fcf | **YES** | PARTIAL | PARTIAL | 21 → 18 | INVALID_ARTIFACT |
| BENCH2-006 | INCOMPLETE | — | — | NOT MEASURED | — | — | — | INCOMPLETE_TREATMENT |

## 3. Primary Outcome

```
Completed: 4/6
Changed:   4/4 (100% of completed)
Unchanged: 0/4
Failed:    2/6 (rate limit)
```

**Treatment activation: CONFIRMED**

## 4. Evidence Analysis

| Task | O1→O2 Scope | Findings Δ | Interpretation |
|------|-------------|------------|----------------|
| BENCH2-001 | INSUFFICIENT → PARTIAL | 23 → 13 | **Improved** scope + reduced findings |
| BENCH2-002 | INSUFFICIENT → PARTIAL | 24 → 8 | **Improved** scope + significant finding reduction |
| BENCH2-004 | INSUFFICIENT → INSUFFICIENT | 25 → 22 | Same scope, 3 fewer findings |
| BENCH2-005 | PARTIAL → PARTIAL | 21 → 18 | Same scope, 3 fewer findings |

## 5. Comparison with Exploratory Run

| Dimension | Exploratory (P048) | Formal (this) |
|-----------|-------------------|---------------|
| Completed | 4/6 | 4/6 |
| Changed | 4/4 | 4/4 |
| BENCH2-001 | INSUFFICIENT → PARTIAL | INSUFFICIENT → PARTIAL |
| BENCH2-002 | FAILED | **COMPLETED** (was missing before) |
| BENCH2-003 | COMPLETED | FAILED (rate limit) |
| BENCH2-004 | INSUFFICIENT → INSUFFICIENT | INSUFFICIENT → INSUFFICIENT |
| BENCH2-005 | PARTIAL → PARTIAL | PARTIAL → PARTIAL |

**Consistent signal across both runs.** BENCH2-002 now completed (was missing before), BENCH2-003 now failed (rate limit). The pattern is stable.

## 6. Provider Failures

| Task | Failure | Classification |
|------|---------|---------------|
| BENCH2-003 | Call 2 MODEL_UNAVAILABLE | INCOMPLETE_TREATMENT |
| BENCH2-006 | Call 1 MODEL_UNAVAILABLE | INCOMPLETE_TREATMENT |

Per frozen policy: recorded as MISSING DATA, not treatment failure.

## 7. Scientific Classification

**B — Treatment Activated, Improvement Mixed**

- Treatment activation: **CONFIRMED** (4/4 completed)
- Improvement: **MIXED** (BENCH2-001/002 improved scope; BENCH2-004/005 reduced findings)
- NOT all improvements are clean (BENCH2-003 incomplete)

## 8. Preservation

| Artifact | Status |
|----------|--------|
| C0 (6) | ✅ UNTOUCHED |
| C1 (6) | ✅ UNTOUCHED |
| C2 canned (6) | ✅ UNTOUCHED |
| C2-live exploratory (4) | ✅ PRESERVED |
| MODEL-004-C2 formal (4) | ✅ CREATED |
| BENCH-002 | ✅ UNTOUCHED |
| MODEL-003 | ✅ UNTOUCHED |
| Ṛta | ✅ 3b5c2f2 unchanged |

## 9. Artifact Inventory

```
formal/MODEL-004-C2/
├── manifests/
│   ├── EGER-M004C2-EC73742C.json  (BENCH2-001)
│   ├── EGER-M004C2-03C39A05.json  (BENCH2-002)
│   ├── EGER-M004C2-EC977E68.json  (BENCH2-004)
│   └── EGER-M004C2-9C250E20.json  (BENCH2-005)
├── raw/
│   ├── EGER-M004C2-EC73742C/
│   ├── EGER-M004C2-03C39A05/
│   ├── EGER-M004C2-EC977E68/
│   └── EGER-M004C2-9C250E20/
└── RUN_INDEX.json
```

## 10. Next Step

**EGER-P051 — MODEL-004 Formal C2 Scientific Review**

---

**FORMAL MODEL-004 C2 EXECUTED — 4/6 TASKS — TREATMENT ACTIVATION CONFIRMED**
