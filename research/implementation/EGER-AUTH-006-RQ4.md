# EGER-AUTH-006 — RQ-4 Formal Execution Authorization

| Field | Value |
|---|---|
| ID | EGER-AUTH-006-RQ4 |
| Date | 2026-08-28 |
| Authorization | **FORMAL RQ-4 EXECUTION AUTHORIZED** |
| Governing Chain | P061 → P062 → P063 → P064 |
| Test Baseline | 162/162 PASS |

---

## 1. Human Authorization

> The human researcher authorizes formal execution of the controlled RQ-4 experiment.
>
> This authorization is for the frozen paired RQ-4 experiment using MODEL-004, BENCH-002 tasks 001–006, with control vs structured-feedback treatment.
>
> This authorization does NOT authorize: C3, changing MODEL-004, changing BENCH-002, changing the Oracle, changing the treatment definition, changing the RQ-4 metrics, modifying C0/C1/C2 historical artifacts, modifying Ṛta, calling rta_generate, changing the experimental design after seeing results, adding retries outside the frozen budget, or p-hacking.

---

## 2. Frozen Model Configuration

| Parameter | Value | Frozen |
|-----------|-------|--------|
| Provider | opencode | ✅ |
| Model | opencode/nemotron-3-ultra-free | ✅ |
| MODEL_ID | EGER-MODEL-004 | ✅ |
| Temperature | 0.0 | ✅ |
| Max tokens | 2048 | ✅ |
| Tools | [] | ✅ |
| Timeout | 60s | ✅ |
| Prompt | eger.prompt.v1 | ✅ |

Both control and treatment branches use this identical configuration.

---

## 3. Frozen Benchmark

BENCH-002 v0.1 — 6 tasks:

| Task | Hash |
|------|------|
| BENCH2-001 | 20c754d47cb111c1 |
| BENCH2-002 | ff5848b840de3415 |
| BENCH2-003 | cb0c1671b37db6fc |
| BENCH2-004 | caf76eca17ef06f5 |
| BENCH2-005 | d69d81c6cb0635ac |
| BENCH2-006 | f79d64a23c0969e7 |

Benchmark is UNCHANGED and UNMODIFIED.

---

## 4. Frozen RQ-4 Design

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
```

The ONLY experimental difference is: presence vs absence of structured EvidenceArtifact feedback in Call 2.

---

## 5. Frozen Call Budget

Per task:

| Resource | Maximum | Breakdown |
|----------|---------|-----------|
| Model calls | 3 | 1 initial + 1 control + 1 treatment |
| Oracle calls | 3 | 1 initial + 1 control evidence + 1 treatment evidence |

No retries beyond these limits. If the provider fails, the task is recorded as incomplete/missing data.

---

## 6. Frozen Primary Metric

```
error_delta = final_error_count - initial_error_count
```

Where `error_count` counts only ERROR-severity findings (SDC-005, SDC-006, SDC-007).

```
paired_effect = error_delta_treatment - error_delta_control
```

Interpretation:
- negative → treatment reduced errors relative to control
- zero → no difference
- positive → treatment increased errors relative to control

WARNING and INFO findings are tracked separately but excluded from the primary metric.

This metric is FROZEN before execution and must not be changed after observing results.

---

## 7. Provider Failure Policy

| Failure | Action |
|---------|--------|
| Rate limiting | Record task as INCOMPLETE; do not retry |
| Provider unavailable | Record task as INCOMPLETE; do not retry |
| Timeout | Record task as INCOMPLETE; do not retry |
| Authentication failure | Record task as INCOMPLETE; do not retry |
| Malformed response | Record task as INCOMPLETE; do not retry |
| Oracle failure | Record task as INCOMPLETE_MEASUREMENT |

Additional rules:
1. Do not substitute another model for MODEL-004.
2. Do not retry beyond the frozen call budget.
3. Do not silently fall back to canned output.
4. Do not fabricate missing values.

---

## 8. Information Boundary

| Tier | What | Who |
|------|------|-----|
| ENGINEER_VISIBLE | task, objective, existing candidate, treatment feedback (treatment only) | Model |
| ORACLE_VISIBLE | design metadata, candidate SDC, benchmark evaluation context | Oracle |
| EVALUATOR_ONLY | hidden expected answers, protected benchmark material | Neither model nor treatment |

---

## 9. Artifact Namespace

```
research/experiments/EGER-EXP-001/formal/RQ4/
    ├── control/
    │   ├── manifests/
    │   └── raw/
    ├── treatment/
    │   ├── manifests/
    │   └── raw/
    └── RUN_INDEX.json
```

---

## 10. Historical Preservation

| Item | Status |
|------|--------|
| C0 | UNTOUCHED |
| C1 | UNTOUCHED |
| C2 canned | UNTOUCHED |
| C2-live | UNTOUCHED |
| MODEL-003 | UNTOUCHED |
| MODEL-004 historical | UNTOUCHED |
| BENCH-002 | UNTOUCHED |
| evaluator_only | UNTOUCHED |
| Oracle historical | UNTOUCHED |
| Ṛta | UNTOUCHED (3b5c2f2) |

---

## 11. Critical Scientific Gate

| # | Question | Answer |
|---|----------|--------|
| 1 | MODEL-004 identical in both branches? | ✅ YES |
| 2 | Initial candidate identical? | ✅ YES |
| 3 | Control feedback-free? | ✅ YES |
| 4 | Treatment structured-feedback only? | ✅ YES |
| 5 | Oracle identical? | ✅ YES |
| 6 | Evaluator-only isolated? | ✅ YES |
| 7 | Primary metric frozen? | ✅ YES |
| 8 | Call budget frozen (3+3)? | ✅ YES |
| 9 | Provider failure policy frozen? | ✅ YES |
| 10 | RQ4 artifact namespace isolated? | ✅ YES |
| 11 | C0/C1/C2 historical protected? | ✅ YES |
| 12 | Ṛta protected? | ✅ YES |
| 13 | rta_generate forbidden? | ✅ YES |
| 14 | C3 still unauthorized? | ✅ YES |
| 15 | Any remaining scientific blocker? | ❌ NO |

---

## 12. Test Baseline

```
162 passed in 21.38s
```

| Suite | Count | Status |
|-------|-------|--------|
| Original | 95 | ✅ ALL PASS |
| Measurement (T025–T059) | 35 | ✅ ALL PASS |
| RQ4 (T060–T091) | 32 | ✅ ALL PASS |
| **Total** | **162** | **✅ ALL PASS** |

---

## 13. Execution Authorization

Formal RQ-4 execution is AUTHORIZED under the following conditions:

1. Use `python formal_runner_rq4.py --live` for formal execution
2. The OPENCODE_API_KEY credential must be present
3. All 6 tasks must be attempted
4. Provider failures must be recorded as INCOMPLETE per the frozen policy
5. No modifications to the runner, model, oracle, benchmark, or treatment during execution
6. Results must be written to `formal/RQ4/` namespace only

---

## 14. C3

C3 remains: **NOT AUTHORIZED**

This authorization is for RQ-4 only.

---

## 15. Authorization Scope

This authorization covers ONLY:

- Running the frozen paired RQ-4 experiment
- Using MODEL-004 (nemotron-3-ultra-free)
- Using BENCH-002 tasks 001–006
- Using the control vs structured-feedback treatment design
- Using the upgraded Oracle with design metadata

This authorization does NOT cover:

- C3
- Any model change
- Any benchmark change
- Any Oracle change
- Any treatment change
- Any metric change
- Any historical artifact modification
- Any Ṛta modification
- Any rta_generate invocation
