# EGER-AUTH-014 — Cross-Task E3a Replication Execution Authorization

## Authorization Identifier
EGER-AUTH-014-DIAGNOSTIC-008

## Date
2026-08-31

## Authorization Statement

**DIAGNOSTIC-008 execution is authorized.**

This authorization permits the execution of the frozen cross-task E3a replication experiment as specified in P120/P121/P122.

**This authorization does NOT execute the experiment.** Execution occurs in P124.

---

## Experiment Specification

| Parameter | Value |
|-----------|-------|
| Experiment | Cross-Task E3a Replication (DIAGNOSTIC-008) |
| Tasks | BENCH2-002, BENCH2-004, BENCH2-005 |
| Conditions | BASE (original objective) / E3a (broader objective) |
| Runs per cell | 10 |
| Total runs | 60 |
| Model | EGER-MODEL-005: `opencode/mimo-v2.5-free` |
| Temperature | 0.0 |
| Tools | [] |
| Max tokens | 2048 |
| Timeout | 60s |
| Namespace | `formal/DIAGNOSTIC-008/` |

---

## Call Budget

60 runs × 3 calls = **180 maximum calls**

---

## Critical SDC Control

| Task | BASE SDC | E3a SDC | Identical |
|------|----------|---------|-----------|
| BENCH2-002 | 287 chars | same object | YES |
| BENCH2-004 | 280 chars | same object | YES |
| BENCH2-005 | 532 chars | same object | YES |

---

## Objective Manipulation (Frozen)

| Task | BASE Objective | E3a Objective |
|------|---------------|---------------|
| BENCH2-002 | original | broader + generated clocks |
| BENCH2-004 | original | broader + false paths |
| BENCH2-005 | original | broader + multicycle exceptions |

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
| P122 readiness | 28/28 checks PASS | READY |
| Tests | 19/19 new, 293/293 regression | PASS |
| Namespace | DIAGNOSTIC-008 empty | VERIFIED |
| Historical preservation | All artifacts untouched | VERIFIED |
| Security | No secrets found | VERIFIED |

---

## C3 Status

**NOT AUTHORIZED.** This experiment tests task framing, not epistemic state.

---

## Scope Limitation

This authorization covers **only** the execution of DIAGNOSTIC-008 as frozen in P120/P121. It does not authorize:
- Changes to the experimental protocol
- Model substitution
- Additional runs beyond 60
- Retries beyond the frozen budget
- Interpretation of results (belongs to P125)
- C3 execution

---

```
AUTHORIZATION: DIAGNOSTIC-008 EXECUTION AUTHORIZED
EXPERIMENT: Cross-Task E3a Replication
TASKS: BENCH2-002, BENCH2-004, BENCH2-005
CONDITIONS: BASE / E3a
RUNS: 60
MAXIMUM CALLS: 180
MODEL: EGER-MODEL-005 (mimo-v2.5-free)
EXECUTION: NOT PERFORMED
C3: NOT AUTHORIZED
```
