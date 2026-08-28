# EGER-P086 — Controlled Variability Confirmation Design

| Field | Value |
|---|---|
| ID | EGER-P086-CONTROLLED-VARIABILITY-CONFIRMATION-DESIGN-001 |
| Date | 2026-08-28 |
| Scope | DESIGN ONLY — no execution |
| Status | **DESIGN READY** |

---

## 1. Executive Summary

Design a preregistered experiment to determine whether BENCH2-001 ERROR adherence remains variable under genuinely identical observable conditions. The experiment removes two confounds from P085: (1) initial SDC comment-line difference, and (2) execution-context variation.

---

## 2. Governing Evidence

From P085:
- 5 Condition-A observations: 2/5 adherent (40%)
- Feedback: byte-identical across all runs
- Initial evidence: identical across all runs
- Initial SDC: P074 had comment line (97 chars), P082/P084 had bare SDC (51 chars)
- Execution context: batch (P074, P082) vs standalone (P084)

---

## 3. Confounds to Remove

| Confound | P085 Status | P086 Solution |
|----------|------------|---------------|
| Initial SDC comment line | P074 had comment, others didn't | Use bare 51-char SDC for all runs |
| Execution context | Batch vs standalone varied | Run all N in same batch mode |
| Provider load/timing | Uncontrolled | Record timestamps; accept as irreducible |

---

## 4. Experimental Design

### Condition
Single condition: **BENCH2-001 baseline** with:
- Initial SDC: `create_clock -name clk -period 10.0 [get_ports clk]` (51 chars)
- Objective: "Generate SDC that correctly defines the primary clock on clk"
- Feedback: full structured feedback (23 findings, same hash c3803b9a...)
- Model: MODEL-005 (mimo-v2.5-free)
- Oracle: 3b5c2f2
- Metadata: eger.design_metadata.v1

### Execution mode
All runs executed **sequentially in a single batch** using the same script invocation. No parallel execution. No different execution contexts.

### Run count
**N = 10 runs.** Rationale:
- P085 had 5 runs (including 1 with different SDC)
- N=10 provides enough observations to estimate adherence rate with reasonable precision
- Binomial confidence interval at N=10: if 5/10 adherent, 95% CI is roughly 23%–77%
- N=10 is feasible within budget (~30 model calls + ~20 Oracle calls)

### Stopping rule
**All 10 runs are executed regardless of intermediate results.** No early stopping based on observed adherence. This prevents selection bias.

---

## 5. Pre-Registered Analysis

### Primary metric
**ERROR adherence:** binary per run — did the final SDC contain `set_input_delay` AND `set_output_delay`?

### Secondary metrics
- proposal_changed (activation)
- error_delta (final - initial ERROR count)
- final_evidence_scope
- proposal SDC length
- time per run

### Pre-registered analysis plan
1. Count adherent runs: X/10
2. Compute point estimate: X/10
3. Compute 95% Clopper-Pearson confidence interval
4. If X/10 is between 1/10 and 9/10: **variability demonstrated** — adherence is non-deterministic
5. If X/10 = 0/10 or 10/10: **possible deterministic behavior** — more evidence needed
6. Report proposal activation rate separately (expected: 10/10 = 100%)
7. Do NOT compute p-values or perform hypothesis tests
8. Do NOT compare to P074/P082/P084 rates (different confounds)

### Decision rules
| Outcome | Interpretation |
|---------|---------------|
| 1–9/10 adherent | ERROR adherence is non-deterministic under identical conditions |
| 0/10 adherent | ERROR adherence may be deterministic (always fails) — requires investigation |
| 10/10 adherent | ERROR adherence may be deterministic (always succeeds) — P074/P084 failures were context-dependent |

---

## 6. What This Experiment Cannot Determine

1. **Whether variability is model-side or provider-side** — we observe the combined effect
2. **Whether variability is truly random or context-dependent** — we control observable context, not provider internals
3. **The "true" probability** — N=10 gives a point estimate with wide CI
4. **Whether other tasks show the same pattern** — this tests only BENCH2-001

---

## 7. Remaining Confounds (Irreducible)

| Confound | Why Irreducible | Impact |
|----------|----------------|--------|
| Provider-side nondeterminism | Cannot control upstream inference | May contribute to observed variability |
| Provider load/caching | Cannot freeze provider state | May affect timing/responses |
| Model version drift | Free-tier model may update | Acceptable for current study |

These are accepted as limitations. If variability persists under controlled conditions, it demonstrates that **something** is non-deterministic, even if we cannot pinpoint the source.

---

## 8. Artifact Namespace

```
research/experiments/EGER-EXP-001/formal/DIAGNOSTIC-003/
    ├── RUN_INDEX.json
    ├── manifest-001.json ... manifest-010.json
    └── raw/
        ├── run-001/
        │   ├── initial_sdc.txt
        │   ├── revised_candidate.json
        │   ├── feedback.json
        │   ├── evidence_initial.json
        │   └── evidence_final.json
        ├── run-002/
        └── ... (10 runs)
```

### Preservation
- P074: UNTOUCHED
- P082 DIAGNOSTIC-001: UNTOUCHED
- P084 DIAGNOSTIC-002: UNTOUCHED
- RQ4-MODEL-005: UNTOUCHED
- All historical artifacts: UNTOUCHED

---

## 9. Call Budget

Per run: 1 model call + 2 Oracle calls = 3 calls
Total: 10 runs × 3 = **30 calls maximum**

This includes the initial Oracle evaluation (necessary for error_delta computation).

---

## 10. Relationship to Prior Evidence

| Document | Relationship |
|----------|-------------|
| P074 RQ-4 | Background — contains one non-adherent observation with different SDC |
| P082 Diagnostic | Background — one adherent observation with bare SDC |
| P084 Repeated A | Background — 1/3 adherent with bare SDC |
| P085 Scientific Review | Governing — identifies confounds to remove |
| P086 (this) | New design — removes confounds, preregisters analysis |

**P086 does not modify, override, or reinterpret any prior document.**

---

## 11. C3 Status

**C3 REMAINS BLOCKED.** P086 tests variability, not the mechanism. Understanding variability is prerequisite to understanding whether epistemic state could improve adherence.

---

## 12. Implementation Requirements

1. Reuse existing diagnostic infrastructure (adapter, Oracle, metadata, feedback renderer)
2. Run all 10 conditions sequentially in a single batch
3. Use the same script invocation for all runs
4. Record timestamp for each run
5. Save all artifacts to DIAGNOSTIC-003/
6. Compute adherence and confidence interval after all runs
7. Do not modify any existing code or artifacts

---

## 13. Status

```
P086 COMPLETE
DESIGN READY
NO EXECUTION
ALL PRIOR ARTIFACTS UNTOUCHED
C3: NOT AUTHORIZED
```
