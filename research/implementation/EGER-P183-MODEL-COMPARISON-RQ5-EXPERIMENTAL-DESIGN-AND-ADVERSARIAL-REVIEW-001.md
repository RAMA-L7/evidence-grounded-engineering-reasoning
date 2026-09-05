# EGER — P183: Model-Comparison RQ-5 Experimental Design & Adversarial Protocol Review

## 1. Objective

Design and adversarially review a controlled model-comparison experiment that tests whether the EGER evidence-grounded architecture operates with different large language models under the same deterministic evaluation authorities and VLSI engineering tasks. Freeze the complete protocol before any data collection.

**Design and review only.** No experiment was run. No model was invoked. No code was modified.

## 2. Frozen Baseline

```
C0  ESTABLISHED
C1  ESTABLISHED
C2  PARTIALLY SUPPORTED
C3  NOT JUSTIFIED
C4  DEFERRED
C5  DEFERRED

RQ-4  CLOSED
RQ-5  CLOSED — Level 2 (PILOT-002: 8/8, both authorities operated)

Baseline model: opencode/mimo-v2.5-free (provider-default sampling)
Rta: 1.5.11 @ 3b5c2f2 (netlist-less + P055 DesignMetadata)
OpenSTA: 2.2.0 @ WSL
Substrate: 3-cell simple_path (P163)
Tasks: T1 (incomplete clock), T2 (aggressive 0.05 ns clock)
Protocol: P169 frozen, repaired by P172/P177/P178
```

## 3. Research Question

> **To what extent does the evidence-grounded EGER architecture operate with different large language models under the same deterministic evaluation authorities and VLSI engineering tasks?**

This is NOT RQ-5 reopened. RQ-5 tested Oracle authority variation. This tests model variation. Different independent variable, different research question.

## 4. Competing Hypotheses

### H0 (Null)

The EGER architecture's operational behavior is model-dependent: the control loop, evidence utilization, and revision patterns observed with the baseline model are specific to that model's capabilities and do not reliably appear with a different model.

### H1 (Alternative)

The EGER architecture's core operational properties — evidence-driven revision, Oracle-specific evaluation, and VerificationGate integration — are sufficiently model-independent that a different LLM can operate the same control loop under the same task and Oracle conditions.

### Important: What This Experiment Can and Cannot Establish

| Claim | Supported? | Reason |
| ----- | ---------- | ------ |
| Architecture operates with two specific models | YES (if both complete) | Direct observation |
| Architecture is model-independent | NO | Two models ≠ all models |
| Architecture works with all free-tier LLMs | NO | Sample biased by qualification |
| Architecture works with any SDC-capable model | NO | Only two models tested |
| Performance is equivalent across models | MAYBE | Depends on effect size and N |

**The maximum defensible claim is bounded to the two tested models under the tested conditions.** Claiming "model independence" from two data points would be an overgeneralization.

## 5. Experimental Unit

One trial = one complete EGER pipeline execution with one model, one task, one Oracle, and one replication.

## 6. Variables

### Independent Variable

**LLM model identity.** Two levels:
- **Baseline:** opencode/mimo-v2.5-free (existing PILOT-002 model)
- **Comparison:** opencode/deepseek-v4-flash (new model)

### Controlled Variables

| Variable | Frozen Value |
| -------- | ------------ |
| Tasks | T1, T2 (identical to RQ-5) |
| Oracles | Rta 1.5.11, OpenSTA 2.2.0 |
| Substrate | simple_path 3-cell netlist + Liberty |
| Protocol | P169 frozen, repaired by P172/P177/P178 |
| Evidence contract | EvidenceNormalizer canonical pass-through |
| VerificationGate | Unchanged |
| Max iterations | 3 per attempt |
| Max retries | 1 bounded retry |
| Candidate validity gate | Same as PILOT-002 |
| Design metadata | Same frozen P055 SIMPLE_PATH |
| Prompt format | Same EGER prompt template |

### Dependent Variables

| Variable | Type | Definition |
| -------- | ---- | ----------- |
| PO-1 | Categorical | Completion quality: ROBUST / MARGINAL / FAILED |
| PO-2 | Binary | Evidence compatibility: COMPATIBLE / INCOMPATIBLE |
| PO-3 | Categorical | Oracle-detected improvement: IMPROVED / NOT_IMPROVED / WORSE / NOT_MEASURABLE |
| qualified_accept | Binary | Whether final acceptance rests on fully-qualified evidence |
| iteration_count | Count | Number of revision iterations |
| oracle_call_count | Count | Total Oracle evaluations |
| completion_status | Categorical | COMPLETED / PROVIDER_FAILURE / etc. |

## 7. Model-Selection Rationale

### Baseline Model: opencode/mimo-v2.5-free

- Provider: mimo
- Already validated: P173-R qualification (6/6), PILOT-002 (8/8 completed)
- Free tier
- File-writing invocation protocol (P173-R)

### Comparison Model: opencode/deepseek-v4-flash

**Selection criteria (applied independently of expected outcome):**

| Criterion | Assessment |
| --------- | ---------- |
| **Different provider family** | ✅ DeepSeek (vs mimo) — genuinely distinct provider |
| **Different architecture** | ✅ DeepSeek V4 architecture (vs mimo V2.5) |
| **Free tier** | ✅ Available at no cost through opencode |
| **Sufficient coding capability** | ✅ DeepSeek V4 is a strong code-generation model |
| **Available via opencode CLI** | ✅ `opencode/deepseek-v4-flash` listed in `opencode models` |
| **Same invocation protocol** | ✅ `opencode run --model opencode/deepseek-v4-flash <prompt>` |
| **Not selected for expected success** | ✅ Selected on provider/architecture distinctness, not predicted performance |

**Why NOT other candidates:**

| Model | Reason Excluded |
| ----- | --------------- |
| opencode/gpt-5-nano | Different provider (OpenAI), but nano-tier may lack SDC capability; harder to qualify |
| opencode/gemini-3.5-flash-lite | Different provider (Google), but "lite" tier may lack engineering precision |
| opencode/claude-haiku-4-5 | Different provider (Anthropic), but different cost tier (not free in all configurations) |
| opencode/mimo-v2.5 | Same provider as baseline — does not test provider independence |

**DeepSeek V4 Flash is the optimal choice because it maximizes provider/architecture distinctness while remaining free-tier and CLI-compatible.**

## 8. Model Qualification Protocol

Both models must pass the same qualification test before experimental trials begin.

### Qualification Test

6 SDC generation tasks (same as P173-R):

1. `simple_path` with complete constraints (clock + I/O delays)
2. `simple_path` with missing input delay
3. `simple_path` with missing output delay
4. `simple_path` with aggressive clock
5. `simple_path` with relaxed clock
6. `simple_path` with both delays and clock

### Qualification Criteria

- Model returns a response containing `create_clock` (proof of SDC generation)
- Model returns a response containing `set_input_delay` or `set_output_delay` (proof of constraint generation)
- Response is classified as VALID_SDC by the candidate-validity gate
- 6/6 passing = QUALIFIED
- <6/6 = NOT QUALIFIED → BLOCKED (experiment cannot proceed with this model)

### Qualification as a Methodological Gate

**Qualification is a readiness gate, not experimental data.** Qualification results are NOT included in the experimental dataset. However, qualification performance is recorded as a diagnostic variable because:

- If the comparison model fails qualification, the experiment is BLOCKED (no data collected)
- If the comparison model barely qualifies (6/6 with near-misses), this is documented as a limitation
- Qualification performance is NOT used to predict or interpret experimental outcomes

**Anti-bias:** Qualification uses the same tasks and criteria for both models. No model receives easier qualification tasks.

## 9. Sample Size and Replication Rationale

### Design

2 models × 2 tasks × 2 Oracles × 2 replications = **16 planned trials** (8 per model)

### Rationale

- **8 trials per model** matches the PILOT-002 design, providing within-model and cross-model variation
- **2 replications per condition** supports descriptive consistency assessment
- **N=16 total** is the minimum feasible design that can detect model × Oracle interactions
- **Statistical power:** NOT claimed. This is a descriptive controlled pilot. N=16 is insufficient for inferential statistics.
- **Information gain:** 8 trials per model provides enough data to observe whether the control loop operates, evidence enters the contract, and revision behavior appears — without claiming statistical reliability.

### What N=16 Can and Cannot Support

| Claim | Supported? |
| ----- | ---------- |
| Both models operated the pipeline | YES (if 16/16 complete) |
| One model performed differently | DESCRIBATIVE (observed difference, no inference) |
| Models are statistically equivalent | NO (N too small) |
| Architecture is model-independent | NO (two models only) |

## 10. Frozen Trial Matrix

### Per-Model Matrix (same as PILOT-002)

| order | trial | task | oracle_first |
| ----: | ----- | ---- | ------------ |
| 1 | T1-{Model}-R1 | T1 | Ṛta |
| 2 | T1-{Model}-OpenSTA-R1 | T1 | Ṛta |
| 3 | T1-{Model}-R2 | T1 | Ṛta |
| 4 | T1-{Model}-OpenSTA-R2 | T1 | Ṛta |
| 5 | T2-{Model}-OpenSTA-R1 | T2 | OpenSTA |
| 6 | T2-{Model}-R1 | T2 | OpenSTA |
| 7 | T2-{Model}-OpenSTA-R2 | T2 | OpenSTA |
| 8 | T2-{Model}-R2 | T2 | OpenSTA |

### Full 16-Trial Matrix

The baseline model (mimo) runs first, then the comparison model (DeepSeek). Within each model block, the frozen PILOT-002 order is preserved.

| order | trial_id | model | task | oracle | replication |
| ----: | -------- | ----- | ---- | ------ | ----------: |
| 1 | T1-mimo-R1 | mimo | T1 | Ṛta | 1 |
| 2 | T1-mimo-OpenSTA-R1 | mimo | T1 | OpenSTA | 1 |
| 3 | T1-mimo-R2 | mimo | T1 | Ṛta | 2 |
| 4 | T1-mimo-OpenSTA-R2 | mimo | T1 | OpenSTA | 2 |
| 5 | T2-mimo-OpenSTA-R1 | mimo | T2 | OpenSTA | 1 |
| 6 | T2-mimo-R1 | mimo | T2 | Ṛta | 1 |
| 7 | T2-mimo-OpenSTA-R2 | mimo | T2 | OpenSTA | 2 |
| 8 | T2-mimo-R2 | mimo | T2 | Ṛta | 2 |
| 9 | T1-deepseek-R1 | deepseek | T1 | Ṛta | 1 |
| 10 | T1-deepseek-OpenSTA-R1 | deepseek | T1 | OpenSTA | 1 |
| 11 | T1-deepseek-R2 | deepseek | T1 | Ṛta | 2 |
| 12 | T1-deepseek-OpenSTA-R2 | deepseek | T1 | OpenSTA | 2 |
| 13 | T2-deepseek-OpenSTA-R1 | deepseek | T2 | OpenSTA | 1 |
| 14 | T2-deepseek-R1 | deepseek | T2 | Ṛta | 1 |
| 15 | T2-deepseek-OpenSTA-R2 | deepseek | T2 | OpenSTA | 2 |
| 16 | T2-deepseek-R2 | deepseek | T2 | Ṛta | 2 |

**Model ordering:** baseline first, comparison second. This is a fixed ordering (not counterbalanced across models) because the models are independent — there is no shared state between model blocks that could create order effects. Each model's 8 trials are a complete, independent experiment.

## 11. Trial Ordering and Counterbalancing

- **Within each model block:** counterbalanced as PILOT-002 (T1 Ṛta-first, T2 OpenSTA-first)
- **Across model blocks:** baseline first, comparison second (fixed — models are independent)
- **Pre-run assertion:** `assert_matrix_order` verifies the frozen order before trial 1
- **No reordering after results**

## 12–22. Protocol Items (Frozen)

All protocol items 12–22 are IDENTICAL to PILOT-002 (P177/P178):

| Item | Frozen Value |
| ---- | ------------ |
| Candidate-validity gate | VALID_SDC check + clock_defined before Oracle |
| Initial Oracle evaluation | Recorded before revision loop |
| Revision-loop semantics | Up to 3 iterations; model revises using Oracle-specific feedback |
| Bounded retry | 1 max; both attempts retained; retry_count recorded |
| Candidate identity | Shared initial SDC per task; single candidate path per iteration |
| Oracle-specific feedback | Preserved per arm (Ṛta errors vs OpenSTA WNS) |
| PO-1 | ROBUST / MARGINAL / FAILED |
| PO-2 | Evidence compatible (binary per evaluation) |
| PO-3 | IMPROVED / NOT_IMPROVED / WORSE / NOT_MEASURABLE (Oracle-specific) |
| Failure vs REJECT | failure_kind (PROVIDER_FAILURE etc.) distinguished from gate REJECT |
| metadata_unqualified | qualified_accept rule: PARTIAL + zero errors → MARGINAL cap |
| OpenSTA valid-clock guard | create_clock required; no_timing_constraint flag |
| Raw records | Immutable JSON per trial; analysis derived after all trials |
| Deterministic analysis | Single pass from raw records; no manual totals |

## 23. Claim-Level Interpretation

### Before Experimentation

The maximum defensible claim **if both models complete successfully:**

> The evidence-grounded EGER control loop operated with two independent language models (opencode/mimo-v2.5-free and opencode/deepseek-v4-flash) and two independent deterministic evaluation authorities (Ṛta and OpenSTA) across the frozen synthetic VLSI tasks, with evaluation evidence entering the common EGER evidence contract and reaching the VerificationGate — under the tested conditions.

**This is NOT a claim of model independence.** It is a claim of operation under two specific models.

### If the Comparison Model Fails

| Failure Mode | Interpretation |
| ------------ | -------------- |
| Fails qualification | BLOCKED — architecture cannot be tested with this model |
| Qualifies but 0/8 trials complete | Model-dependent failure — architecture does not operate with this model |
| Qualifies but some trials complete | Partial operational compatibility — boundary identification |
| Model × Oracle interaction | Architecture operates differently under different model × Oracle combinations |

**Even a negative result is informative:** it precisely identifies the model-dependence boundary.

## 24. Confounder Analysis

| Confounder | Risk | Mitigation | Residual |
| ---------- | ---- | ---------- | -------- |
| Model capability difference | HIGH | Qualification gate; same tasks | Different models may produce different SDC quality |
| Provider/runtime difference | HIGH | Same CLI invocation protocol | Provider-side differences (latency, token limits) |
| Prompt compatibility | MEDIUM | Same prompt template | Different models may interpret prompts differently |
| Context-window differences | LOW | Tasks are short; no context overflow expected | Unknown until tested |
| Sampling configuration | MEDIUM | Provider-default for both models | Cannot control provider-side sampling |
| Qualification bias | MEDIUM | Same tasks and criteria for both | Qualification conditions the sample |
| Failure-rate differences | MEDIUM | Bounded retry; record all failures | One model may fail more often |
| File-writing behavior | MEDIUM | P173-R protocol | Different models may write files differently |
| Model × Oracle interaction | HIGH | Counterbalanced within each model | May not be detectable with N=8 per model |
| Small substrate hiding differences | HIGH | Same 3-cell substrate for both | Model differences may only appear at scale |
| N too small for conclusion | HIGH | Descriptive pilot; no inference claimed | Cannot detect subtle differences |

## 25. Adversarial Review

### Q1: Could model qualification manufacture a positive result?

**No.** Qualification tests basic SDC generation capability. If a model qualifies, it can produce SDC text. Qualification does not test the full EGER pipeline. A model could qualify but fail in the revision loop (e.g., unable to process Oracle feedback). Qualification is a necessary but not sufficient condition for pipeline operation.

### Q2: Could one model receive effectively different prompts?

**Partially.** The same prompt template is used, but different models may tokenize or interpret it differently. This is an inherent limitation of cross-model comparison — the prompt is the same bytes, but the model's processing is opaque. **Mitigation:** Record the exact prompt sent to each model; compare prompt hashes.

### Q3: Could provider failures be mistaken for engineering failures?

**Yes, if not carefully distinguished.** The harness distinguishes PROVIDER_FAILURE from gate REJECT via `failure_kind`. **Mitigation:** The same distinction used in PILOT-002 is applied here. Provider failures are recorded as failures, not engineering outcomes.

### Q4: Could Oracle feedback interact with model capability?

**Yes.** This is the model × Oracle interaction confounder. A model may process Ṛta feedback well but OpenSTA feedback poorly (or vice versa). **Mitigation:** The 2×2×2 design (2 models × 2 tasks × 2 Oracles) can detect this interaction if it is large. With N=2 per cell, subtle interactions will be missed. **Documented limitation.**

### Q5: Could different output formats create an artificial model effect?

**Possible.** Different models may produce SDC with different formatting (whitespace, comments, flag syntax). The candidate-validity gate normalizes some of this, but semantic differences in SDC construction could affect Oracle evaluation. **Mitigation:** Record exact candidate bytes and hashes; compare output patterns descriptively.

### Q6: Could the small synthetic substrate hide model differences?

**Yes.** The 3-cell substrate has very few timing paths. Model differences may only emerge on complex designs with many paths, diverse constraints, and realistic SDC patterns. **Mitigation:** This is explicitly documented as a limitation. The experiment tests architecture operation, not production-scale performance.

### Q7: Could N be too small to support the proposed conclusion?

**Yes.** N=8 per model is a descriptive pilot. It can observe whether the pipeline operates but cannot claim statistical equivalence or difference. **Mitigation:** The claim is appropriately bounded to descriptive observation. No inferential statistics are planned.

### Q8: Could successful replication still be compatible with substantial model dependence?

**Yes.** Both models could complete 8/8 trials but with dramatically different revision behavior, evidence quality, or verification outcomes. Completion alone does not prove equivalent operation. **Mitigation:** PO-1/PO-2/PO-3 capture qualitative differences beyond mere completion. The analysis plan includes per-model and per-condition comparison.

### Q9: What result would genuinely falsify the hypothesis?

**If the comparison model fails qualification, or qualifies but completes 0/8 trials, or shows no evidence of revision behavior across all trials.** These would demonstrate that the architecture does not operate with the comparison model under the tested conditions.

### Q10: What claim remains valid if the second model fails completely?

**The RQ-5 Level-2 claim remains valid for the baseline model.** The model-comparison experiment is additive — failure of the comparison model narrows the architecture's demonstrated scope but does not invalidate the existing evidence base.

## 26. Threats to Validity

- **Internal:** model capability differences, provider differences, prompt interpretation differences
- **Construct:** "architecture operation" is measured by pipeline completion and evidence production, not by engineering quality
- **External:** synthetic 3-cell substrate; two models only; free-tier models only
- **Statistical conclusion:** N=16 descriptive pilot; no inference

## 27. Falsification Criteria

The hypothesis (architecture operates with different models) is falsified if:

1. Comparison model fails qualification (<6/6)
2. Comparison model qualifies but completes 0/8 trials
3. Comparison model shows 0% revision activation across all trials
4. Comparison model produces no compatible evidence across all trials
5. A strong model × Oracle interaction is observed (one model works with one Oracle but not the other)

## 28. Explicit Non-Goals

- Do NOT claim model independence from two models
- Do NOT test production-scale designs
- Do NOT investigate framing causality (RQ-4)
- Do NOT redesign the paired-generation protocol
- Do NOT modify Ṛta, OpenSTA, or VerificationGate
- Do NOT compare model quality or capability
- Do NOT infer statistical equivalence or difference

## 29. Decision

```text
GO — the design is sufficiently rigorous and frozen for a future
execution-readiness gate. The model-comparison experiment tests the
most critical remaining uncertainty (model dependence) with a
well-controlled design, appropriate claim boundaries, and thorough
adversarial analysis.

P183 authorizes a future execution-readiness gate only.
It does not authorize model-comparison experimentation.
```

## 30. Research Boundary

```text
RQ-4: CLOSED (unchanged)
RQ-5: CLOSED (unchanged)
C0-C5: UNCHANGED
Rta: UNCHANGED
VerificationGate: UNCHANGED
New experiment executed: NO
New model invoked: NO
```

## 31. Tests

- EGER full suite: 878/878 PASS (no code changes)
- Harness suite: 62/62 PASS

## 32. Git

- P183 committed as: `56acfc5` (see CHANGE-055)
- HEAD == origin/main (after push)
- No code changes; research records only
- Universal_Principles_Library/ untouched

## 33. Artifacts

- `research/implementation/EGER-P183-MODEL-COMPARISON-RQ5-EXPERIMENTAL-DESIGN-AND-ADVERSARIAL-REVIEW-001.md`
- `research/implementation/EGER-CHANGE-055.md`

## STOP

P183 designed and adversarially reviewed the model-comparison experiment. The protocol is frozen. The next step, when authorized, is a P184 execution-readiness gate (model qualification + harness adaptation + fixture dry-run). No experiment was run. No data was collected.
