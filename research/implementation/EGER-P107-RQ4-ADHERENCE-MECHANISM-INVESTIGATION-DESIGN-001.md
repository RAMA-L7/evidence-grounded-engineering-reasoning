# EGER-P107 — RQ-4 Adherence Mechanism Investigation Design

| Field | Value |
|---|---|
| ID | EGER-P107-RQ4-ADHERENCE-MECHANISM-INVESTIGATION-DESIGN-001 |
| Date | 2026-08-28 |
| Scope | DESIGN ONLY — no execution |
| Status | **DESIGN READY** |

---

## 1. Executive Summary

Design a controlled investigation to determine WHY ERROR-feedback adherence varies. The investigation must distinguish five competing explanations without assuming any particular mechanism. The minimum experiment is a **prompt-isolation study** that holds all variables constant except the specific information the model receives.

---

## 2. Competing Explanations

| # | Explanation | Mechanism | Testable? |
|---|------------|-----------|-----------|
| E1 | **Prompt token count** | Longer prompts cause different behavior | YES — vary prompt length |
| E2 | **SDC semantic content** | Specific constructs (generated clock, etc.) influence the model | YES — manipulate SDC content |
| E3 | **Task description framing** | "Primary clock" vs "complete SDC" changes interpretation | YES — vary task wording |
| E4 | **Feedback structure** | ERROR + WARNING + INFO vs ERROR-only affects attention | YES — vary feedback composition |
| E5 | **Provider nondeterminism** | Same inputs produce different outputs due to system-level effects | PARTIALLY — can test by repeating identical conditions |

---

## 3. Governing Evidence

From P105:
- W (minimal SDC + BENCH2-001): 10/20 = 50% adherent
- X (rich SDC + BENCH2-001): 5/5 = 100% adherent
- Y (minimal SDC + BENCH2-002): 5/5 = 100% adherent
- Z (rich SDC + BENCH2-002): 16/16 = 100% adherent

The critical comparison is W vs X (same task, different SDC) and W vs Y (different task, same SDC). But n=5 is insufficient for both.

---

## 4. Design Principle

**Hold everything constant except the variable being tested.**

Each experiment tests exactly ONE explanation by manipulating exactly ONE factor while holding all others constant.

---

## 5. Experiment Design: Prompt Isolation Study

### Objective
Determine which component of the prompt most influences ERROR adherence.

### Base condition (replicates W)
- SDC: minimal 51-char clock definition
- Objective: "Generate SDC that correctly defines the primary clock on clk"
- Context: BENCH2-001 context
- Feedback: full (23 findings)
- **Expected: ~50% adherence** (baseline)

### Experimental conditions (vary one factor at a time)

| Condition | What Changes | Tests | Expected if Explanation Correct |
|-----------|-------------|-------|--------------------------------|
| **E1a** | Add padding to prompt (100 tokens of neutral text) | E1 (token count) | Different adherence from baseline |
| **E1b** | Remove padding from baseline prompt | E1 (token count) | Same as baseline |
| **E2a** | Replace minimal SDC with syntactically equivalent but content-neutral SDC (e.g., same clock, different port names) | E2 (SDC content) | Same as baseline if content matters |
| **E2b** | Add irrelevant SDC constructs (e.g., set_max_fanout, set_units) to minimal SDC | E2 (SDC content) | Higher adherence if complexity matters |
| **E3a** | Change objective to "Generate a complete production-quality SDC" | E3 (framing) | Higher adherence if framing matters |
| **E3b** | Change objective to "Add I/O delays to the existing SDC" | E3 (framing) | Higher adherence if framing matters |
| **E4a** | Feedback: ERROR findings only (2 findings) | E4 (feedback structure) | Higher adherence if overload matters |
| **E4b** | Feedback: ERROR + WARNING only (3 findings) | E4 (feedback structure) | Intermediate if overload matters |
| **E5** | Repeat base condition 10 times (already done in P090) | E5 (nondeterminism) | Stochastic pattern |

### Minimum sufficient experiment

**Not all conditions are necessary.** The minimum sufficient experiment tests the strongest competing explanations:

1. **Base** (replicate W) — 10 runs
2. **E2b** (add irrelevant constructs) — 10 runs
3. **E3a** (broader objective) — 10 runs
4. **E4a** (ERROR-only feedback) — 10 runs

Total: 40 runs. Budget: 40 × 3 = 120 calls.

### Why these four
- E2b tests whether adding SDC complexity (without changing semantics) improves adherence
- E3a tests whether task framing affects adherence
- E4a tests whether feedback overload causes non-adherence
- Base provides the comparison baseline

---

## 6. Hypotheses and Decision Rules

### Hypothesis: SDC content drives adherence
- If E2b (added constructs) shows higher adherence than base → SDC content matters
- If E2b shows same adherence as base → SDC content does not matter

### Hypothesis: Task framing drives adherence
- If E3a (broader objective) shows higher adherence than base → framing matters
- If E3a shows same adherence as base → framing does not matter

### Hypothesis: Feedback overload drives non-adherence
- If E4a (ERROR-only) shows higher adherence than base → overload matters
- If E4a shows same adherence as base → overload does not matter

### Hypothesis: Provider nondeterminism is the sole cause
- If base condition shows stochastic behavior (already established in P090)
- AND none of E2b/E3a/E4a show consistent improvement → nondeterminism may be the primary cause

---

## 7. What Can and Cannot Be Inferred

### CAN be inferred
- Whether specific prompt components influence adherence
- Whether feedback structure matters
- Whether SDC content matters
- Whether task framing matters

### CANNOT be inferred
- What the model is "thinking" internally
- Whether the model has "uncertainty"
- Whether the model "understands" the feedback
- Whether provider-side nondeterminism is the cause (only that model-side factors are or are not sufficient)

---

## 8. Controls

| Control | Purpose |
|---------|---------|
| Same model (MODEL-005) | Isolate prompt effects from model effects |
| Same Oracle | Isolate prompt effects from measurement effects |
| Same metadata | Isolate prompt effects from validation effects |
| Same execution mode | Isolate prompt effects from context effects |
| Same feedback content (where not varied) | Isolate prompt effects from feedback effects |
| Sequential single batch | Minimize context variation |

---

## 9. Sample Size and Budget

| Condition | Runs | Calls | Total |
|-----------|------|-------|-------|
| Base (W replicate) | 10 | 30 | 30 |
| E2b (added constructs) | 10 | 30 | 30 |
| E3a (broader objective) | 10 | 30 | 30 |
| E4a (ERROR-only feedback) | 10 | 30 | 30 |
| **Total** | **40** | **120** | **120** |

---

## 10. Artifact Namespace

```
research/experiments/EGER-EXP-001/formal/MECHANISM-001/
    ├── RUN_INDEX.json
    ├── base/
    ├── E2b-added-constructs/
    ├── E3a-broader-objective/
    └── E4a-error-only-feedback/
```

---

## 11. Preregistered Analysis

### Primary metric
ERROR adherence (binary per run)

### Analysis plan
1. Compute adherence rate per condition
2. Compute 95% Clopper-Pearson CI per condition
3. Compare each experimental condition to base
4. Report effect direction and magnitude
5. Do NOT perform formal hypothesis tests (n=10 insufficient)

### Decision rules
| Pattern | Interpretation |
|---------|---------------|
| E2b > base | SDC content/complexity influences adherence |
| E3a > base | Task framing influences adherence |
| E4a > base | Feedback overload influences adherence |
| All ≈ base | None of these factors explain the variability |
| All ≈ base, base stochastic | Provider nondeterminism is the most parsimonious explanation |

---

## 12. Falsification Criteria

The investigation would falsify:
- **SDC content hypothesis** if E2b shows no improvement over base
- **Task framing hypothesis** if E3a shows no improvement over base
- **Feedback overload hypothesis** if E4a shows no improvement over base
- **All prompt-based hypotheses** if no condition improves over base

If all prompt-based hypotheses are falsified, the most parsimonious explanation is **provider/system nondeterminism** — the stochastic behavior is not caused by anything in the prompt.

---

## 13. Relationship to C3

This investigation is prerequisite to C3:
- If prompt factors explain adherence → C3 is not needed (the fix is in the prompt)
- If provider nondeterminism explains adherence → C3 cannot help (the cause is external)
- If nothing explains adherence → C3 is premature (mechanism unknown)

Only if the investigation reveals a model-internal factor would C3 become motivated.

---

## 14. Next Implementation Gate

P108 — Implementation → P109 readiness → P110 authorization → P111 execution → P112 scientific review

---

## 15. Status

```
P107 COMPLETE
DESIGN READY
NO EXECUTION
ALL PRIOR ARTIFACTS UNTOUCHED
C3: NOT AUTHORIZED
```
