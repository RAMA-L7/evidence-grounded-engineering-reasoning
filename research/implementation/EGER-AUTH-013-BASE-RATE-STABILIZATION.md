# EGER-AUTH-013 — Base-Rate Stabilization Execution Authorization

## Authorization Identifier
EGER-AUTH-013-BASE-RATE-STABILIZATION

## Date
2026-08-31

## Authorization Statement

**DIAGNOSTIC-007 execution is authorized.**

This authorization permits the execution of the frozen base-rate stabilization experiment as specified in P114/P115/P116.

**This authorization does NOT execute the experiment.** Execution occurs in P118.

---

## Experiment Specification

| Parameter | Value |
|-----------|-------|
| Experiment | Base-Rate Stabilization (DIAGNOSTIC-007) |
| Task | BENCH2-001 |
| Initial SDC | `create_clock -name clk -period 10.0 [get_ports clk]` (51 chars) |
| Design context | `Module top with ports clk, reset, data_in[7:0], data_out[7:0]. Single clock domain clk at 10ns. No generated clocks.` |
| Objective | `Generate SDC that correctly defines the primary clock on clk` |
| Feedback | Full structured EvidenceArtifact |
| Model | EGER-MODEL-005: `opencode/mimo-v2.5-free` |
| Temperature | 0.0 |
| Tools | [] |
| Max tokens | 2048 |
| Timeout | 60s |
| Oracle | EGER EvidenceOracle |
| Metadata | eger.design_metadata.v1 |

---

## Execution Parameters

| Parameter | Value |
|-----------|-------|
| Total runs | 20 sequential |
| Calls per run | 3 (1 Oracle init + 1 model + 1 Oracle final) |
| Maximum calls | 60 |
| Namespace | `formal/DIAGNOSTIC-007/` |
| Primary metric | ERROR adherence: `final_error_count < initial_error_count` |

---

## Failure Policy (Frozen)

| Failure | Action |
|---------|--------|
| Provider timeout | Record INCOMPLETE; no retry |
| Empty model output | Record INCOMPLETE; no retry |
| Oracle failure | Record INCOMPLETE_MEASUREMENT; no retry |
| Model substitution | **FORBIDDEN** |
| Retry beyond budget | **FORBIDDEN** |
| Canned/fallback output | **FORBIDDEN** |

---

## Gates Verified

| Gate | Reference | Status |
|------|-----------|--------|
| P114 design | EGER-P114-BASE-RATE-STABILIZATION-DESIGN-001.md | APPROVED |
| P115 implementation | EGER-P115-BASE-RATE-STABILIZATION-IMPLEMENTATION-001.md | APPROVED |
| P116 readiness | 49/49 checks PASS | READY |
| CHANGE-014 | EGER-CHANGE-014.md | PRESENT |
| Tests | 16/16 new, 274/274 regression | PASS |
| Namespace | DIAGNOSTIC-007 empty | VERIFIED |
| Historical preservation | All artifacts untouched | VERIFIED |
| Security | No secrets found | VERIFIED |

---

## Historical Preservation Statement

Authorization of DIAGNOSTIC-007 does not alter:
- RQ-4 historical results
- DIAGNOSTIC-001 through DIAGNOSTIC-006
- BENCH-002
- MODEL-004 artifacts
- C0/C1/C2 artifacts
- Rta
- Existing research records

---

## C3 Status

**NOT AUTHORIZED.** This experiment is a base-rate measurement, not a C3 intervention.

---

## Scope Limitation

This authorization covers **only** the execution of DIAGNOSTIC-007 as frozen in P114/P115. It does not authorize:
- Changes to the experimental protocol
- Model substitution
- Additional runs beyond 20
- Retries beyond the frozen budget
- Interpretation of results (belongs to P119)
- C3 execution
- Cross-task replication (separate authorization required)

---

## Statement

```
AUTHORIZATION: DIAGNOSTIC-007 EXECUTION AUTHORIZED
EXPERIMENT: Base-Rate Stabilization
TASK: BENCH2-001
RUNS: 20
MAXIMUM CALLS: 60
MODEL: EGER-MODEL-005 (mimo-v2.5-free)
EXECUTION: NOT PERFORMED
C3: NOT AUTHORIZED
```
