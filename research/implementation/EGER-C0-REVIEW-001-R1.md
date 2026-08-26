# EGER-C0-REVIEW-001-R1 — Revised Scientific Review

**Prompt ID:** EGER-C0-REVIEW-001-R1 (revision of EGER-C0-REVIEW-001)
**Date:** 2026-08-26
**Type:** Read-only scientific review — NO code changes, NO benchmark changes, NO C1, NO Ṛta modifications
**Central Question:** Does our C0 baseline actually measure what EGER claims to measure, or is the `INSUFFICIENT` oracle scope creating a confounder?
**Revision reason:** Original review overclaimed conclusions. INSUFFICIENT scope is not established as a confounder, but also not proven absent as one.

---

## 1. Executive Summary

**C0 is usable as a baseline, but the review does not establish that INSUFFICIENT oracle scope is categorically non-confounding.**

The available evidence shows that the oracle can produce useful deterministic findings under insufficient scope. Whether the scope limitation materially affects the causal interpretation of C1–C5 remains an open question to be monitored during C1 readiness and subsequent analysis.

```
C0 STATUS:              VALID BASELINE
ORACLE SCOPE:           ACCEPTABLE WITH DOCUMENTED LIMITATION
INSUFFICIENT SCOPE:     NOT CURRENTLY A BLOCKING ISSUE
CONFOUNDING STATUS:     NOT ESTABLISHED AS A CONFOUNDER
                        NOT PROVEN ABSENT AS A CONFOUNDER
C1:                     REQUIRES HUMAN AUTHORIZATION
```

---

## 2. What C0 Established (Precise Claims)

C0 established three things with certainty:

### 2a. Oracle execution succeeded on all 6 candidates

`oracle_status=SUCCESS` for all 6 runs. The oracle executed deterministically and produced findings. This is **not** the same as "the oracle validated the candidates." The oracle executed; it did not validate.

### 2b. Deterministic findings were produced under INSUFFICIENT scope

The oracle produced findings codes SDC-005, SDC-006, SDC-007, SDC-020, SDC-021, SDC-024, SDC-028, SDC-029, SDC-030, SDC-150 — all legitimate findings. INSUFFICIENT scope did not prevent the oracle from executing or from producing findings.

### 2c. The adversarial case was detected

BENCH2-006 (clock on data port) was correctly flagged SDC-007. This demonstrates that the oracle can catch domain-specific errors even without netlist context.

---

## 3. What C0 Did NOT Establish

### 3a. "Oracle validated all 6 candidates" — NOT ESTABLISHED

The original review stated: "The oracle successfully validates all 6 candidates."

This is **misleading**. `oracle_status=SUCCESS` means the oracle **executed successfully**. It does **not** mean the candidates were validated. The evidence scope was INSUFFICIENT for 5/6 runs and PARTIAL for 1/6. No run achieved FULL scope. Therefore:

```
ORACLE EXECUTION:        SUCCESS (all 6)
    ≠
EVIDENCE SUFFICIENCY:    INSUFFICIENT (5/6), PARTIAL (1/6)
    ≠
VALIDATION:              NONE (0/6 VALIDATED)
```

This separation is fundamental to P6/P7 and must not be collapsed.

### 3b. "5/6 correct" — NOT ESTABLISHED AS VALIDATED

The original review stated: "LLM proposal quality → 5/6 correct."

The C0 formal result established:

```
VALIDATED:      0/6
INVALID:        5/6
INSUFFICIENT:   1/6
```

If "correct" means **the generated SDC matched the intended task semantics** (task-level plausibility), that is a separate metric that must be explicitly defined and independently justified. It cannot be inferred from the oracle output.

```
CANDIDATE SYNTACTICALLY/TASK-WISE PLAUSIBLE
        ≠
CANDIDATE DETERMINISTICALLY VALIDATED
```

That distinction is actually central to EGER. The review should not collapse it.

### 3c. "INSUFFICIENT scope is NOT a confounder" — NOT ESTABLISHED

The original review concluded: "The INSUFFICIENT oracle scope is NOT a confounder."

This is **too strong for the evidence presented**. C0 alone cannot establish this because:

1. C0 has no feedback — it measures baseline, not the effect of feedback
2. C1 will receive INSUFFICIENT-scope feedback — whether that feedback is actionable is unknown
3. If INSUFFICIENT scope feedback is not actionable, C1 may be testing reaction to oracle limitations rather than engineering evidence — a potential confound

The review can say: "INSUFFICIENT scope did not prevent error detection in C0." It cannot say: "INSUFFICIENT scope will not confound C1-C5."

---

## 4. Artifact-by-Artifact Analysis (Revised)

### BENCH2-001 (primary_clocks, easy)

| Item | Value |
|------|-------|
| Candidate SDC | `create_clock -name clk -period 10 [get_ports clk]` |
| Task-level plausibility | **Plausible** — matches task objective (primary clock only) |
| Oracle execution | SUCCESS |
| Evidence scope | INSUFFICIENT |
| Error findings | SDC-005 (no input delay), SDC-006 (no output delay) |
| Classification | INVALID_ARTIFACT |
| Deterministic validation | **NOT VALIDATED** (INSUFFICIENT scope) |

**Assessment:** The candidate is plausibly correct for the task. SDC-005/006 are legitimate findings about missing I/O constraints. Whether the candidate is "correct" cannot be determined without FULL scope validation.

### BENCH2-002 (generated_clocks, medium)

| Item | Value |
|------|-------|
| Candidate SDC | `create_clock` + `create_generated_clock` with correct `-source` and `-divide_by` |
| Task-level plausibility | **Plausible** — matches task objective |
| Oracle execution | SUCCESS |
| Evidence scope | INSUFFICIENT |
| Error findings | SDC-005, SDC-006 |
| Classification | INVALID_ARTIFACT |
| Deterministic validation | **NOT VALIDATED** |

**Assessment:** Generated clock structure is plausible. SDC-005/006 are about missing I/O delays, not about the generated clock itself. Whether the candidate is "correct" requires FULL scope.

### BENCH2-003 (io_constraints, medium)

| Item | Value |
|------|-------|
| Candidate SDC | `create_clock` + `set_input_delay -max 1.5` + `set_output_delay -max 2.0` |
| Task-level plausibility | **Plausible** — matches task objective (max delays only) |
| Oracle execution | SUCCESS |
| Evidence scope | INSUFFICIENT |
| Error findings | None (only warnings: SDC-028, SDC-029, SDC-030) |
| Classification | INSUFFICIENT_EVIDENCE |
| Deterministic validation | **NOT VALIDATED** |

**Assessment:** Only run without error-severity findings. Candidate is plausible for the task. The oracle correctly identifies that `-min` delays are missing for hold timing.

### BENCH2-004 (false_paths, medium)

| Item | Value |
|------|-------|
| Candidate SDC | `create_clock` + `set_false_path` with correct pins |
| Task-level plausibility | **Plausible** — matches task objective |
| Oracle execution | SUCCESS |
| Evidence scope | INSUFFICIENT |
| Error findings | SDC-005, SDC-006 + warnings SDC-020, SDC-150 |
| Classification | INVALID_ARTIFACT |
| Deterministic validation | **NOT VALIDATED** |

**Assessment:** False path declaration is plausible. SDC-020 (confirm false path) and SDC-150 (undocumented exception) are reasonable warnings.

### BENCH2-005 (multicycle_paths, hard)

| Item | Value |
|------|-------|
| Candidate SDC | `create_clock` + `set_multicycle_path -setup 2` with correct pins |
| Task-level plausibility | **Plausible** — matches task objective |
| Oracle execution | SUCCESS |
| Evidence scope | **PARTIAL** (only run with PARTIAL scope) |
| Error findings | SDC-005, SDC-006 + warnings SDC-021 (missing `-hold 1`), SDC-150 |
| Classification | INVALID_ARTIFACT |
| Deterministic validation | **NOT VALIDATED** (PARTIAL, not FULL) |

**Assessment:** Candidate is plausible. SDC-021 is a legitimate warning: multicycle `-setup 2` without `-hold 1` can cause hold violations. The PARTIAL scope is informative — it shows the oracle can verify multicycle paths without netlist context.

### BENCH2-006 (adversarial_clock_on_data, hard)

| Item | Value |
|------|-------|
| Candidate SDC | `create_clock` on `clk` + `create_clock` on `data_bus_0` |
| Task-level plausibility | **Intentionally adversarial** — produces expected error |
| Oracle execution | SUCCESS |
| Evidence scope | INSUFFICIENT |
| Error findings | SDC-005, SDC-006, **SDC-007** (clock on data port), SDC-024 |
| Classification | INVALID_ARTIFACT |
| Deterministic validation | **NOT VALIDATED** |

**Assessment:** Oracle correctly detects the adversarial error (SDC-007). This demonstrates the oracle can catch domain-specific errors even without netlist context. The candidate is intentionally incorrect.

---

## 5. The ORACLE EXECUTION ≠ EVIDENCE SUFFICIENCY Separation

This separation is probably going to become one of the most important parts of the EGER architecture:

```
ORACLE EXECUTION
    SUCCESS
        ≠
EVIDENCE SUFFICIENCY
    INSUFFICIENT
        ≠
EPISTEMIC STATE
    HYPOTHESIS
        ≠
AUTHORIZATION
    REJECTED
```

The original review collapsed these. The revised review preserves the separation. Each layer has independent meaning:

- **Oracle execution SUCCESS**: The oracle ran without error. Findings were produced.
- **Evidence sufficiency INSUFFICIENT**: The findings cannot support full validation without netlist context.
- **Epistemic state HYPOTHESIS**: No transition was attempted (C0 has no L2 exposed).
- **Authorization REJECTED**: No authorization was attempted (C0 has no L3 exposed).

---

## 6. C1 Confound Question (Open)

The original review stated: "The gap between INSUFFICIENT and FULL is what C1-C5 are designed to measure."

This is **not yet established**. C1-C5 are designed to test the effect of different grounding/epistemic/authorization mechanisms. If the oracle's evidence scope is fundamentally limited for most tasks, we need to know exactly what information is available to the Engineer in C1.

Consider the C0→C1 pipeline:

```
C0:
LLM → candidate → oracle → insufficient/error

C1:
LLM → candidate → oracle → text feedback → LLM
```

If the feedback is:

> "NETLIST_REQUIRED / INSUFFICIENT"

then C1 may be testing whether the LLM can react to an **oracle limitation**, rather than whether it can reason better from engineering evidence. That's a potential confound.

It might ultimately turn out **not** to be a confounder. But C0 alone doesn't establish that.

**This is an open question to be monitored during C1 readiness.**

---

## 7. C1 Readiness Assessment (Revised)

### Can C1 Proceed?

**YES — with the documented limitation.**

C1 adds "textual tool feedback (deterministic oracle output rendered as text)" to the Engineer's input. The question is: **will INSUFFICIENT scope feedback help the Engineer improve?**

**Argument for proceeding:**
- C1 tests whether *any* feedback (even INSUFFICIENT-scope feedback) helps
- The oracle findings (SDC-005/006/007 etc.) are informative even under INSUFFICIENT scope
- The Engineer could add I/O delays, add comments, or fix the adversarial clock
- If INSUFFICIENT scope feedback is not actionable, that's a valid experimental result (falsification of H1 for C1)
- It would not be a protocol failure

**Argument for caution:**
- If INSUFFICIENT scope feedback is not actionable, C1 may be testing reaction to oracle limitations rather than engineering evidence
- This is a potential confound that should be monitored
- The confound question is not resolved by C0 alone

**Recommendation:** C1 can proceed, but the review must not overclaim that INSUFFICIENT scope is non-confounding. The confound question remains open.

---

## 8. Protocol Compliance Check

| Protocol Section | C0 Compliance |
|-----------------|---------------|
| §6 C0 definition | ✅ Task context only, no feedback |
| §7 capability matrix | ✅ All C0 capabilities correct |
| §11 run protocol | ✅ One task × one condition × one run |
| §12 failure taxonomy | ✅ No collapsed FAILED classes |
| §13 termination | ✅ All within budget |
| §14 retry policy | ✅ No hidden retries |
| §15 metrics | ✅ All recorded |
| §18 convergence | ✅ 0/6 converged (expected) |
| §21 anti-gaming | ✅ No task/run removal |
| §22 data leakage | ✅ No evaluator answers in prompts |
| §23 manifests | ✅ All 6 manifests produced |
| §24 artifact retention | ✅ All raw artifacts retained |
| §26 claim discipline | ✅ "hypothesis" used, not "proves" |

---

## 9. Recommendations (Revised)

1. **C0 is a valid baseline.** The review does not establish that INSUFFICIENT scope is categorically non-confounding, but it also does not identify it as a blocking issue.

2. **Do NOT modify BENCH-002.** The tasks are correct. The INSUFFICIENT scope is a property of the task design (no netlist), not a bug.

3. **Do NOT modify model.py.** The deterministic mapping is correct and frozen.

4. **Do NOT modify the oracle.** The INSUFFICIENT scope is honest and correct.

5. **Record this review as provenance.** C0's INSUFFICIENT scope is now part of the experimental record.

6. **For future benchmark design:** Consider tasks that can achieve PARTIAL or FULL scope without netlist (e.g., tasks where the oracle can verify syntax + structure without port verification).

7. **Monitor the confound question during C1.** If C1 shows no improvement over C0, determine whether the cause is:
   - (a) INSUFFICIENT scope feedback is not actionable (confound), or
   - (b) The Engineer cannot improve from text feedback alone (genuine finding)

---

## 10. Deviations from Protocol

None. C0 was executed exactly as specified in EGER-EXP-001 v0.1.

---

## 11. Remaining Issues

1. **C1 confound question:** Whether INSUFFICIENT scope feedback is actionable vs. whether it tests reaction to oracle limitations. Open question.

2. **C1 design:** How should textual feedback be presented to the Engineer? The protocol says "deterministic oracle output rendered as text" — need to define the exact format.

3. **Statistical power:** With 6 tasks and 1 run per task, statistical inference is limited. Known limitation documented in protocol (§20, §27).

4. **BENCH-002 evaluator exposure:** The evaluator-only answers were exposed during the GitHub incident (EGER-GITHUB-001). Does not affect C0 results but must be recorded for future benchmark design.

5. **Task-level plausibility vs. deterministic validation:** The review uses "plausible" for task-level assessment. This is an informal metric, not a formal EGER metric. It should not be confused with VALIDATED.

---

## 12. FINAL ASSESSMENT

**C0 is usable as a baseline. The review does not establish that INSUFFICIENT oracle scope is categorically non-confounding. The available evidence shows that the oracle can produce useful deterministic findings under insufficient scope. Whether the scope limitation materially affects the causal interpretation of C1–C5 remains an open question.**

```
C0 Review Status:    ✅ COMPLETE — READ-ONLY (R1 revision)
C0 Baseline:         VALID
Oracle Scope:        ACCEPTABLE WITH DOCUMENTED LIMITATION
Insufficient Scope:  NOT CURRENTLY A BLOCKING ISSUE
Confound Status:     NOT ESTABLISHED AS CONFOUNDER
                     NOT PROVEN ABSENT AS CONFOUNDER
C1 Readiness:        REQUIRES HUMAN AUTHORIZATION
Protocol Compliance: ✅ ALL SECTIONS VERIFIED
Deviations:          NONE
Overclaims:          CORRECTED (R1)
```

**Next step:** EGER-C1-001 (separate prompt, requires human authorization). Monitor confound question during C1 readiness.
