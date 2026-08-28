# EGER-AUTH-012 — DIAGNOSTIC-006 Mechanism Investigation Execution Authorization

## Authorization Identifier
EGER-AUTH-012-RQ4-MECHANISM

## Date
2026-08-28

## Status
**DIAGNOSTIC-006 EXECUTION AUTHORIZED — EXECUTION NOT PERFORMED**

---

## Human Authorization Statement

Formal execution of the P107/P108 mechanism investigation is authorized under the frozen protocol. This authorization covers only the 4-condition × 10-run prompt-isolation study for BENCH2-001.

---

## Gate Verification

| Gate | Source | Status |
|------|--------|--------|
| P109 READY | EGER-P109-...001.md | PASS |
| P107 protocol unchanged | P107 design | PASS |
| P108 implementation unchanged | P108 record + code | PASS |
| 4 conditions isolated | Programmatic verification | PASS |
| 10 runs × 4 conditions | RUNS_PER_CONDITION = 10 | PASS |
| 120-call budget | 10 × 4 × 3 = 120 | PASS |
| MODEL-005 frozen | opencode/mimo-v2.5-free | PASS |
| Oracle/metadata frozen | Unchanged from P108 | PASS |
| DIAGNOSTIC-006 empty | Directory does not exist | PASS |
| Failure policy frozen | No retry/substitution/fallback | PASS |
| Historical artifacts preserved | No RQ4/DIAG-003–005 overwrite | PASS |
| C3 unauthorized | No C3 path in code | PASS |
| Tests pass | 258/258 | PASS |

## Frozen Configuration

### Model
- Provider: opencode
- Model: opencode/mimo-v2.5-free
- Model ID: EGER-MODEL-005
- Temperature: 0.0
- Tools: []
- Max tokens: 2048
- Timeout: 60s

### Conditions
| Condition | SDC | Objective | Feedback | Runs |
|-----------|-----|-----------|----------|------|
| Base | 51-char minimal | Original | Full (23 findings) | 10 |
| E2b | 51-char + added constructs | Original | Full | 10 |
| E3a | 51-char minimal | Broader (production-quality) | Full | 10 |
| E4a | 51-char minimal | Original | ERROR-only (2 findings) | 10 |

### Budget
- Total: 120 calls (40 runs × 3 calls/run)
- Per run: initial Oracle + model + final Oracle
- No retries beyond budget

### Namespace
- Output: formal/DIAGNOSTIC-006/

### Failure Policy
- On provider failure: record INCOMPLETE, continue within budget
- No model substitution
- No retry beyond frozen budget
- No fallback/canned output
- No fabrication of missing values

### Primary Metric
- ERROR adherence (binary: model output contains set_input_delay AND set_output_delay)

### Secondary Metrics
- proposal activation (binary)
- error_delta
- 95% Clopper-Pearson CI

## Information Boundary
- ENGINEER_VISIBLE: task, objective, existing SDC, structured feedback
- ORACLE_VISIBLE: evaluator-side design metadata, candidate SDC
- EVALUATOR_ONLY: never enters model prompt

## Historical Isolation
- RQ-4 artifacts: UNTOUCHED
- DIAGNOSTIC-003 (variability-001): UNTOUCHED
- DIAGNOSTIC-004 (variability-002): UNTOUCHED
- DIAGNOSTIC-005 (sdc-complexity): UNTOUCHED
- C0/C1/C2: UNTOUCHED
- MODEL-004: UNTOUCHED
- Ṛta: UNTOUCHED

## C3 Status
**C3 NOT AUTHORIZED**

## Scope Limitation
This authorization covers ONLY the mechanism investigation (DIAGNOSTIC-006). It does NOT authorize:
- C3 execution
- RQ-4 re-execution
- Model substitution
- Treatment design modification
- Oracle modification
- Benchmark modification
- Historical artifact modification

---

## Authorization Record

```
EGER-AUTH-012-RQ4-MECHANISM
DIAGNOSTIC-006 EXECUTION AUTHORIZED
EXECUTION NOT PERFORMED
C3 NOT AUTHORIZED
```
