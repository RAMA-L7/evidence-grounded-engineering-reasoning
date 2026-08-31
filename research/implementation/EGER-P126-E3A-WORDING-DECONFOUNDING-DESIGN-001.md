# EGER-P126 — E3a Wording Deconfounding Experiment Design

## Research Question

DIAGNOSTIC-008 established a strong replication signal: E3a > BASE on all three tested tasks (+19 to +30 percentage points). However, the E3a objective combines two manipulations:

1. **Broader task framing** ("complete, production-quality")
2. **Additional task-specific technical guidance** ("generated clocks", "false paths", "multicycle exceptions")

P126 must determine whether the adherence improvement comes from framing, technical content, both, or their interaction.

---

## Factorial Design

```
                    Technical Content
                    NO              YES

Narrow Framing      A4 (BASE)       A2

Broad Framing       A1              A3 (current E3a)
```

### Conditions

| Condition | Framing | Technical Content | Purpose |
|-----------|---------|-------------------|---------|
| **A4** | Narrow (original) | No | Baseline |
| **A1** | Broad ("complete, production-quality") | No | Framing-only effect |
| **A2** | Narrow (original) | Yes | Technical-content-only effect |
| **A3** | Broad ("complete, production-quality") | Yes | Combined effect (current E3a) |

---

## Exact Objective Manipulations Per Task

### BENCH2-002

| Condition | Objective |
|-----------|-----------|
| **A4** | Generate SDC with primary clock and correctly constrained generated clock. |
| **A1** | Generate a complete, production-quality SDC for this design. |
| **A2** | Generate SDC with primary clock and correctly constrained generated clock. Include generated clocks and any applicable exceptions. |
| **A3** | Generate a complete, production-quality SDC for this design. Include all required timing constraints: clock definitions, generated clocks, and any applicable exceptions. |

### BENCH2-004

| Condition | Objective |
|-----------|-----------|
| **A4** | Generate SDC that correctly declares the false path without over-constraining. |
| **A1** | Generate a complete, production-quality SDC for this design. |
| **A2** | Generate SDC that correctly declares the false path without over-constraining. Include timing exceptions and any applicable false paths. |
| **A3** | Generate a complete, production-quality SDC for this design. Include all required timing constraints: clock definitions, timing exceptions, and any applicable false paths. |

### BENCH2-005

| Condition | Objective |
|-----------|-----------|
| **A4** | Generate SDC with correct multicycle exception. |
| **A1** | Generate a complete, production-quality SDC for this design. |
| **A2** | Generate SDC with correct multicycle exception. Include multicycle exceptions and any applicable constraints. |
| **A3** | Generate a complete, production-quality SDC for this design. Include all required timing constraints: clock definitions, multicycle exceptions, and any applicable constraints. |

### Manipulation Verification

| Check | A1 vs A4 | A2 vs A4 | A3 vs A1 | A3 vs A2 |
|-------|----------|----------|----------|----------|
| Framing changes | Yes | No | No | Yes |
| Technical content changes | No | Yes | Yes | No |

---

## Task Selection

Use BENCH2-002, BENCH2-004, BENCH2-005 (same as DIAGNOSTIC-008).

**BENCH2-001 excluded:** It has a different SDC structure (51-char minimal) and the historical Base rate is more variable. Including it would introduce cross-task heterogeneity without improving the factorial identification. The three selected tasks provide sufficient replication.

---

## Sample Size

**8 runs per cell.**

Justification:
- DIAGNOSTIC-008 used 10 per cell and detected +19-30pp effects
- 8 per cell gives adequate signal for the factorial decomposition
- Reduces total budget to a manageable level

```
3 tasks × 4 conditions × 8 runs = 96 runs
96 × 3 calls = 288 maximum calls
```

---

## Call Budget

| Resource | Per Run | Total |
|----------|---------|-------|
| Oracle initial | 1 | 96 |
| MODEL-005 call | 1 | 96 |
| Oracle final | 1 | 96 |
| **Total** | **3** | **288** |

---

## Frozen Model

```
EGER-MODEL-005
opencode/mimo-v2.5-free
temperature = 0.0
tools = []
max_tokens = 2048
timeout = 60s
```

---

## Primary Metric

```
adherent = final_error_count < initial_error_count
```

Only `severity == "error"` findings count.

---

## Secondary Metrics

- activation (binary)
- initial ERROR count
- final ERROR count
- error delta
- initial/final evidence scope
- revised SDC length
- task-specific constraint indicators
- feedback hash
- duration
- provider status
- completion status

---

## Preregistered Comparisons

### Main Effects

| Comparison | Isolates |
|-----------|----------|
| **A1 vs A4** | Effect of broader framing WITHOUT technical content |
| **A2 vs A4** | Effect of technical content WITHOUT broader framing |

### Incremental Effects

| Comparison | Isolates |
|-----------|----------|
| **A3 vs A1** | Incremental effect of technical content WHEN framing is broad |
| **A3 vs A2** | Incremental effect of broader framing WHEN technical content is present |

### Interaction

| Comparison | Isolates |
|-----------|----------|
| **(A3−A1) vs (A2−A4)** | Whether technical content effect depends on framing level |
| **(A3−A2) vs (A1−A4)** | Whether framing effect depends on technical content level |

---

## Interpretation Rules (Preregistered)

### Pattern 1: Framing Dominant
If A1 > A4 AND A3 > A2 (framing effect consistent regardless of technical content):
> Evidence favors **framing** as the primary mechanism.

### Pattern 2: Technical Content Dominant
If A2 > A4 AND A3 > A1 (technical effect consistent regardless of framing):
> Evidence favors **technical content** as the primary mechanism.

### Pattern 3: Both Contribute
If A1 > A4 AND A2 > A4 (both factors improve over baseline independently):
> Evidence suggests **both framing and technical content contribute**.

### Pattern 4: Interaction/Synergy
If A3 > max(A1, A2) (combined effect exceeds both single factors):
> Possible **interaction/synergy** — the combination produces more than either factor alone.

### Pattern 5: No Effect
If neither A1 nor A2 improves over A4:
> Current E3a effect may depend on the **exact combination** or an **unidentified factor**.

### What We Will NOT Claim
- Causality from rate differences alone
- Statistical significance from CI overlap
- Generalization beyond MODEL-005 + BENCH-002
- That the mechanism is model-interior

---

## Confound Controls

| Variable | Control |
|----------|---------|
| Initial SDC | Identical across all 4 conditions within each task |
| Design context | Identical |
| Feedback | Same Oracle, same metadata |
| Model | Same MODEL-005 |
| Temperature/tools/tokens/timeout | Identical |
| Oracle | Same implementation |
| Runs per cell | 8 (equal) |
| Failure policy | Same frozen policy |

**Only the objective wording changes between conditions.**

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

## Statistical Plan

For each cell: completed n, adherent k, rate k/n, 95% Clopper-Pearson CI.

For each comparison: report absolute difference in percentage points.

**No formal hypothesis testing** — the experiment is underpowered for formal tests at n=8 per cell. Interpretation is based on the preregistered pattern rules and effect consistency across tasks.

---

## Limitations

1. **n=8 per cell** — CIs will be wide; results are indicative, not definitive
2. **One model** — MODEL-005 only
3. **One benchmark family** — BENCH-002 only
4. **Objective wording is not perfectly decomposable** — some overlap between framing and technical content is inevitable
5. **Cannot determine model-interior mechanism** — only behavioral outcomes are measured
6. **BASE rate variability** — the underlying adherence rate varies across execution contexts

---

## Relationship to Prior Evidence

```
DIAGNOSTIC-006: E3a = 10/10 on BENCH2-001
DIAGNOSTIC-008: E3a > BASE on 3/3 tasks
P126: Decompose E3a into framing vs technical content
```

P126 does NOT replace DIAGNOSTIC-008. It extends it by isolating the mechanism.

---

## C3 Status

```
C3: NOT JUSTIFIED
```

This experiment tests prompt/objective design, not epistemic state.

---

## Namespace

```
formal/DIAGNOSTIC-009/
```

Must be empty before implementation/execution.

---

## Implementation Gates

```
P126 Design ← WE ARE HERE
    ↓
P127 Implementation
    ↓
P128 Readiness
    ↓
P129 Authorization
    ↓
P130 Execution
    ↓
P131 Scientific Review
```

---

```
P126 COMPLETE
E3A WORDING DECONFOUNDING DESIGN COMPLETE
DESIGN ONLY
NO LIVE MODEL CALLS
DIAGNOSTIC-009 NOT EXECUTED
EXECUTION NOT AUTHORIZED
C3: NOT AUTHORIZED
NEXT: P127 IMPLEMENTATION
```
