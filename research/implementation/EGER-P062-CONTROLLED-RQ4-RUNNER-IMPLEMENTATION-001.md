# EGER-P062 — Controlled RQ-4 Runner Implementation

| Field | Value |
|---|---|
| ID | EGER-P062-CONTROLLED-RQ4-RUNNER-IMPLEMENTATION-001 |
| Date | 2026-08-28 |
| Governing Design | EGER-P061-CONTROLLED-RQ4-EXPERIMENT-DESIGN-001 |
| Change Control | EGER-CHANGE-007 |
| Status | **IMPLEMENTATION COMPLETE — RQ4 RUNNER READY** |

---

## 1. Executive Summary

P062 implements the controlled RQ4 paired runner per the P061 experimental design. The runner executes both control (no feedback) and treatment (structured feedback) branches for each benchmark task, using the SAME initial candidate and SAME MODEL-004 identity. The primary metric is error-count delta (ERROR-severity findings only).

**162/162 tests PASS. No regressions.**

---

## 2. Governing Principal

> EGER must not claim that an engineering proposal is better merely because an agent changed its output.
>
> EGER must experimentally separate:
> 1. Evidence delivery
> 2. Model response / treatment activation
> 3. Engineering correctness improvement

This principal is embedded in the runner design: the runner measures proposal change AND correctness independently.

---

## 3. P061 Conformance

| P061 Requirement | Implementation | Status |
|------------------|---------------|--------|
| Same model (MODEL-004) both conditions | `MODEL_NAME = "opencode/nemotron-3-ultra-free"` | ✅ |
| Same initial candidate | `initial_candidate` shared | ✅ |
| Paired design | control/treatment branches from same initial | ✅ |
| Error-count delta as primary | `_compute_error_delta()` | ✅ |
| Hard/soft finding split | `HARD_FINDING_CODES`, `WARNING_FINDING_CODES` | ✅ |
| New namespace (RQ4/) | `formal/RQ4/control/` + `formal/RQ4/treatment/` | ✅ |
| Information boundary verified | T080, T088 | ✅ |
| Historical artifacts preserved | T083, T084 | ✅ |

---

## 4. Implementation Files

| File | Purpose |
|------|---------|
| `research/experiments/EGER-EXP-001/formal_runner_rq4.py` | RQ4 paired runner |
| `tests/test_rq4_runner.py` | 32 unit tests |
| `research/implementation/EGER-CHANGE-007.md` | Change control |

---

## 5. Experimental Architecture

```
For each BENCH2 task:

    SAME INITIAL CANDIDATE (Call 1)
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

Primary metric: treatment_delta_error - control_delta_error
```

---

## 6. Control Branch

```
Call 1: task + objective → initial candidate
Oracle 1: initial candidate + design_metadata → initial evidence
Call 2: task + initial candidate + NO feedback → final_control
Oracle 2: final_control + design_metadata → final_control_evidence
```

Control Call 2 prompt contains ONLY:
- task context
- objective
- initial candidate (existing_sdc)

It does NOT contain:
- structured EvidenceArtifact
- design metadata
- evaluator answers
- hidden benchmark info

---

## 7. Treatment Branch

```
Call 1: task + objective → initial candidate
Oracle 1: initial candidate + design_metadata → initial evidence
structured_feedback = render_structured_feedback(initial_evidence)
Call 2: task + initial candidate + structured_feedback → final_treatment
Oracle 2: final_treatment + design_metadata → final_treatment_evidence
```

Treatment Call 2 prompt contains:
- task context
- objective
- initial candidate (existing_sdc)
- deterministic structured EvidenceArtifact

---

## 8. Model Configuration (Frozen)

| Parameter | Value |
|-----------|-------|
| Provider | opencode |
| Model | opencode/nemotron-3-ultra-free |
| Temperature | 0.0 |
| Max tokens | 2048 |
| Tools | [] |
| Timeout | 60s |
| Prompt | eger.prompt.v1 |

---

## 9. Primary Metric (Pre-Registered)

```python
def _compute_error_delta(initial_findings, final_findings):
    """Only counts ERROR-severity findings."""
    initial_errors = sum(1 for f in initial_findings
                         if f["severity"] == "error")
    final_errors = sum(1 for f in final_findings
                       if f["severity"] == "error")
    return final_errors - initial_errors
```

ERROR findings: SDC-005, SDC-006, SDC-007 (hard defects).

Treatment effect: `treatment_delta_error - control_delta_error`

---

## 10. Secondary Metrics

| Metric | Definition | Interpretation |
|--------|-----------|---------------|
| proposal_changed | initial_hash ≠ final_hash | Treatment activation |
| CVR_delta | final_CVR - initial_CVR | Reference validity change |
| scope_delta | initial_scope → final_scope | Measurement confidence |
| warning_delta | warning_count(final) - warning_count(initial) | Advisory change |

---

## 11. Finding Classification (Frozen)

### Hard (in primary metric)
| Code | Severity | Meaning |
|------|----------|---------|
| SDC-005 | ERROR | No set_input_delay |
| SDC-006 | ERROR | No set_output_delay |
| SDC-007 | ERROR | create_clock on data port |

### Soft (NOT in primary metric)
| Code | Severity | Meaning |
|------|----------|---------|
| SDC-020 | WARNING | set_false_path confirm |
| SDC-021 | WARNING | Multicycle -hold fix |
| SDC-028 | WARNING | No set_input_delay -min |
| SDC-029 | WARNING | No set_output_delay -min |
| SDC-030 | WARNING | No set_propagated_clock |

### Informational (NOT in any metric)
All INFO-severity findings.

---

## 12. Budget

| Resource | Maximum per task |
|----------|-----------------|
| Model calls | 3 (1 initial + 1 control + 1 treatment) |
| Oracle calls | 3 (1 initial + 1 control + 1 treatment) |
| Retries | 0 |

---

## 13. Artifact Namespace

```
formal/RQ4/
    ├── control/
    │   ├── manifests/
    │   │   └── RQ4-{hash}.json
    │   └── raw/
    │       └── RQ4-{hash}/
    │           ├── initial_candidate.json
    │           ├── evidence_initial.json
    │           ├── revised_candidate.json
    │           └── evidence_final.json
    ├── treatment/
    │   ├── manifests/
    │   │   └── RQ4-{hash}.json
    │   └── raw/
    │       └── RQ4-{hash}/
    │           ├── initial_candidate.json
    │           ├── evidence_initial.json
    │           ├── structured_feedback.json
    │           ├── revised_candidate.json
    │           └── evidence_final.json
    └── RUN_INDEX.json
```

---

## 14. Tests

**32 unit tests (T060–T091) — ALL PASS**

| Category | Tests | Status |
|----------|-------|--------|
| Paired design (T060–T066) | 7 | ✅ ALL PASS |
| Metrics (T067–T072) | 6 | ✅ ALL PASS |
| Persistence (T073–T076) | 4 | ✅ ALL PASS |
| Budget (T077) | 1 | ✅ PASS |
| Failures (T078–T079) | 2 | ✅ ALL PASS |
| Isolation (T080–T084) | 5 | ✅ ALL PASS |
| Calculation (T085) | 1 | ✅ PASS |
| Artifacts (T086–T088) | 3 | ✅ ALL PASS |
| Functions (T089–T091) | 3 | ✅ ALL PASS |

---

## 15. Regression

| Suite | Count | Status |
|-------|-------|--------|
| Original tests | 95 | ✅ ALL PASS |
| Measurement tests (T025–T059) | 35 | ✅ ALL PASS |
| RQ4 tests (T060–T091) | 32 | ✅ ALL PASS |
| **Total** | **162** | **✅ ALL PASS** |

---

## 16. Scientific Integrity Check

| # | Question | Answer |
|---|----------|--------|
| 1 | Is the initial candidate genuinely identical between branches? | ✅ YES — `initial_candidate` is a single object shared by both branches |
| 2 | Is feedback the ONLY treatment difference? | ✅ YES — verified by T066 (design_context, existing_sdc, objective identical; only evidence_summary differs) |
| 3 | Is MODEL-004 identical in both branches? | ✅ YES — same model instance (verified by T064) |
| 4 | Is the Oracle identical? | ✅ YES — same Oracle instance, same metadata |
| 5 | Is measurement identical? | ✅ YES — same Oracle.validate() for both final evaluations |
| 6 | Is evaluator-only information excluded? | ✅ YES — verified by T080, T088 |
| 7 | Is the primary metric pre-registered? | ✅ YES — error-count delta, ERROR-severity only |
| 8 | Can artifacts support paired causal comparison? | ✅ YES — same initial, separate control/treatment outputs |
| 9 | Did implementation introduce any confound? | ❌ NO — verified by T066 |
| 10 | Does implementation require changing P061? | ❌ NO — P061 design fully implemented |

---

## 17. Preservation Verified

| Item | Status |
|------|--------|
| BENCH-002 | ✅ UNCHANGED (6 hashes match P061) |
| C0 (6 manifests) | ✅ PRESERVED |
| C1 (6 manifests) | ✅ PRESERVED |
| C2 canned (6 manifests) | ✅ PRESERVED |
| MODEL-004 historical (4 manifests) | ✅ PRESERVED |
| MODEL-003 | ✅ UNCHANGED |
| MODEL-004 | ✅ FROZEN |
| structured_feedback.py | ✅ UNCHANGED |
| feedback.py | ✅ UNCHANGED |
| EngineerAdapter | ✅ UNCHANGED |
| EvidenceOracle | ✅ UNCHANGED |
| Ṛta | ✅ 3b5c2f2, unchanged |
| rta_generate invocations | ✅ ZERO |

---

## 18. Deviations

**None.** P061 design is implemented as specified.

---

## 19. Unresolved Issues

**None blocking.**

Known limitation: temperature=0.0 does not guarantee byte-identical model output across calls. This is a provider limitation, not an implementation issue. The design accounts for this by recording all hashes.

---

## 20. Status

```
P062 IMPLEMENTATION COMPLETE
RQ4 RUNNER READY FOR POST-IMPLEMENTATION READINESS REVIEW
RQ4 LIVE EXECUTION NOT PERFORMED
NO SCIENTIFIC RESULT CLAIMED
NO GITHUB PUSH
```

---

## 21. Next Gate

**P063 — RQ4 Runner Post-Implementation Readiness Review**

Then:
```
P062 (this) ← YOU ARE HERE
    ↓
P063 Readiness review
    ↓
Human execution authorization (P064)
    ↓
Controlled RQ-4 execution
    ↓
Scientific review
    ↓
RQ-4 decision
    ↓
Only then: C3
```
