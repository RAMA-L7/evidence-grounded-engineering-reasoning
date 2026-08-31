# EGER-AUTH-015 — E3a Wording Deconfounding Execution Authorization

## Authorization Identifier
EGER-AUTH-015-DIAGNOSTIC-009

## Date
2026-08-31

## Authorization Statement

**DIAGNOSTIC-009 execution is authorized.**

This authorization permits the execution of the frozen 2×2 factorial E3a wording deconfounding experiment as specified in P126/P127/P128.

**This authorization does NOT execute the experiment.** Execution occurs in P130.

---

## Experiment Specification

| Parameter | Value |
|-----------|-------|
| Experiment | E3a Wording Deconfounding (DIAGNOSTIC-009) |
| Tasks | BENCH2-002, BENCH2-004, BENCH2-005 |
| Conditions | A4 (BASE), A1 (framing), A2 (tech), A3 (both) |
| Runs per cell | 8 |
| Total runs | 96 |
| Model | EGER-MODEL-005: `opencode/mimo-v2.5-free` |
| Namespace | `formal/DIAGNOSTIC-009/` |

---

## Factorial Design

```
                    Technical Content
                    NO              YES

Narrow Framing      A4 (BASE)       A2

Broad Framing       A1              A3 (current E3a)
```

---

## Call Budget

96 runs × 3 calls = **288 maximum calls**

---

## Failure Policy (Frozen)

| Failure | Action |
|---------|--------|
| Provider timeout | INCOMPLETE; no retry |
| Empty model output | INCOMPLETE; no retry |
| Oracle failure | INCOMPLETE_MEASUREMENT; no retry |
| Model substitution | FORBIDDEN |
| Retry | FORBIDDEN |
| Fallback/canned | FORBIDDEN |
| Budget exceeded | FORBIDDEN |

---

## Gates Verified

| Gate | Reference | Status |
|------|-----------|--------|
| P128 readiness | 43/43 checks PASS | READY |
| Tests | 20/20 new, 313/313 regression | PASS |
| Namespace | DIAGNOSTIC-009 empty | VERIFIED |
| Historical preservation | All artifacts untouched | VERIFIED |

---

## Scientific Constraint

DIAGNOSTIC-009 is designed to separate broader framing from additional technical content. The experiment does not automatically establish causality, mechanism, or epistemic uncertainty.

---

## C3 Status

**NOT AUTHORIZED.**

---

```
AUTHORIZATION: DIAGNOSTIC-009 EXECUTION AUTHORIZED
EXPERIMENT: E3a Wording Deconfounding
TASKS: BENCH2-002, BENCH2-004, BENCH2-005
CONDITIONS: A4 / A1 / A2 / A3
RUNS: 96
MAXIMUM CALLS: 288
MODEL: EGER-MODEL-005 (mimo-v2.5-free)
EXECUTION: NOT PERFORMED
C3: NOT AUTHORIZED
```
