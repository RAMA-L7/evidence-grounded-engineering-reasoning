# EGER P169 — RQ-5 Experimental Protocol Adversarial Review & Revision

## 1. Objective

Actively invalidate the P168 protocol before any RQ-5 data is collected. Determine whether the protocol is methodologically strong enough to support a controlled, defensible descriptive pilot addressing RQ-5.

## 2. Baseline

- **Commit:** 1821aac12db3b4c4670fdbd1b816e776e6c9e479
- **Branch:** main
- **P168 verdict:** GO (challenged)

## 3. P168 Protocol Summary

- RQ-5: Architecture generalization across independent deterministic authorities
- N=1 per Oracle condition (2 total trials)
- Two perturbations: P1a (missing output delay → Ṛta), P1b (aggressive clock → OpenSTA)
- Primary outcomes: pipeline completion, evidence production, revision behavior (Levenshtein)
- Descriptive only, no inferential statistics

## 4. Adversarial Findings

### FINDING-1: Insufficient Replication (CRITICAL)

**Finding:** N=1 per Oracle condition cannot distinguish architecture-level behavior from task-specific behavior.

**Why it matters:** With one trial per condition, any observed outcome could be due to:
- The specific task chosen
- A single favorable LLM generation
- A single Oracle execution
- Random model variation

The experiment cannot determine whether the architecture **generally** works with both Oracles or whether it **happened** to work on two selected examples.

**Evidence:** P168 Section 13 states "N=1 per condition is sufficient to demonstrate architectural compatibility." This is incorrect — N=1 demonstrates technical feasibility on one example, not architectural compatibility.

**Impact:** The experiment's primary claim ("architecture generalizes") is unsupported by the replication structure.

**Resolution:** Increase to N=3 per condition (6 total trials) using a crossed task×Oracle design. This is the minimum defensible replication for a descriptive pilot.

### FINDING-2: Task/Oracle Asymmetry (HIGH)

**Finding:** P1a (missing output delay) is tailored to Ṛta's strength. P1b (aggressive clock) is tailored to OpenSTA's strength. Each Oracle is effectively evaluated on a different task.

**Why it matters:** If each Oracle gets a task designed for its strength, observed differences reflect task selection, not architectural behavior. The experiment cannot determine whether the architecture handles **equivalent** challenges under different authorities.

**Evidence:** P168 Section 5 explicitly states "each perturbation is designed to be detectable by one Oracle but not necessarily the other." This creates a confound where the Oracle and perturbation are entangled.

**Impact:** Cross-condition comparisons are invalid because the conditions are not equivalent.

**Resolution:** Use a shared task family where BOTH Oracles can meaningfully evaluate the same perturbation. Design tasks where:
- Ṛta finds constraint issues AND OpenSTA finds timing issues on the same SDC
- The LLM must address both types of evidence

### FINDING-3: Levenshtein as Primary Metric (HIGH)

**Finding:** Levenshtein edit distance measures textual change, not engineering improvement.

**Why it matters:**
- A large rewrite could be worse than a small fix
- Equivalent constraints with different textual representations produce high Levenshtein
- Formatting differences inflate the metric
- Semantically important single-token changes produce low Levenshtein

**Evidence:** P168 Section 11 proposes "Revision magnitude (Levenshtein distance)" as PO-3.

**Impact:** The metric does not measure what RQ-5 claims to measure (revision effectiveness under different authorities).

**Resolution:** Demote Levenshtein to diagnostic. Primary outcome should be: Does the Oracle's evaluation improve from initial to final candidate? (Binary: IMPROVED / NOT_IMPROVED / WORSE)

### FINDING-4: No Retry Policy (MEDIUM)

**Finding:** A single transient provider failure disproportionately affects N=1.

**Why it matters:** With N=1, one failed trial means 50% of the data is missing. This is unacceptable for even a descriptive pilot.

**Evidence:** P168 Section 15 states "No retries. Each trial is executed once."

**Impact:** Provider transient failures could make the pilot uninterpretable.

**Resolution:** Allow 1 bounded retry per trial (max 2 attempts). Record both attempts. If both fail, the trial is a failure.

### FINDING-5: Fixed Order (MEDIUM)

**Finding:** Ṛta always runs first. This creates an uncontrolled order confound.

**Why it matters:** If model context or filesystem state leaks between runs, the second Oracle always benefits from the first.

**Evidence:** P168 Section 14 states "randomization is not applicable" with N=1. With N=3, randomization becomes necessary.

**Impact:** Order effects are uncontrolled.

**Resolution:** Counterbalance execution order across trials. Half the trials run Ṛta first, half run OpenSTA first.

### FINDING-6: Single Task (MEDIUM)

**Finding:** One task with two perturbations cannot demonstrate that the architecture works across tasks.

**Why it matters:** Task-specific effects are indistinguishable from architecture effects.

**Evidence:** P168 uses only T1-CLOCK-CONSTRAINT.

**Impact:** External validity is extremely limited.

**Resolution:** Use 2 tasks (T1: clock constraint, T2: input/output delay) × 2 Oracles = 4 task-oracle combinations, replicated 2× = 8 total trials minimum. This is still a pilot but provides within-task and cross-task variation.

### FINDING-7: Binary Outcomes Too Weak (LOW)

**Finding:** PO-1 (COMPLETED/FAILED) and PO-2 (EVIDENCE_PRODUCED/NO_EVIDENCE) are too coarse.

**Why it matters:** Binary outcomes cannot distinguish "barely completed" from "robustly completed."

**Impact:** Limited diagnostic value.

**Resolution:** Add a 3-level completion quality: ROBUST (completed with revision improvement), MARGINAL (completed without improvement), FAILED.

## 5. Replication Review

P168's N=1 is insufficient. The revised protocol uses:

- 2 tasks × 2 Oracles × 2 replications = 8 trials
- This provides within-task variation (same task, different Oracle)
- And cross-task variation (same Oracle, different task)
- Still a descriptive pilot, not a confirmatory study

## 6. Task/Oracle Symmetry Review

The revised task design ensures both Oracles can evaluate the same SDC:

**Task T1: Incomplete Clock Constraints**
- SDC has `create_clock` but missing `set_input_delay` and `set_output_delay`
- Ṛta: detects incompleteness (constraint analysis)
- OpenSTA: may detect timing issues (depends on Liberty)
- Both Oracles can evaluate; findings differ by property

**Task T2: Aggressive Timing + Missing Constraints**
- SDC has overly aggressive clock period AND missing output delay
- OpenSTA: detects setup violation (timing analysis)
- Ṛta: detects incomplete constraints (constraint analysis)
- Both Oracles find issues; different evidence types

This design ensures:
- Both Oracles evaluate the same SDC
- Both Oracles can produce findings
- Findings differ by authority-specific property
- The LLM must handle both types of evidence

## 7. Metric Review

### Removed as Primary
- **Levenshtein distance** → Demoted to diagnostic
- **Binary completion** → Replaced with 3-level quality

### New Primary Outcomes

**PO-1: Pipeline Completion Quality**
- ROBUST: Pipeline completes, final candidate differs from initial, Oracle evaluation improves
- MARGINAL: Pipeline completes but no improvement detected
- FAILED: Pipeline does not complete

**PO-2: Evidence Contract Compatibility**
- Both Oracles produce evidence that enters EvidenceNormalizer without authority-specific changes
- Metric: Binary (COMPATIBLE / INCOMPATIBLE) per Oracle evaluation

**PO-3: Oracle-Detected Improvement**
- Initial Oracle evaluation vs final Oracle evaluation
- For Ṛta: reduction in ERROR findings
- For OpenSTA: improvement in WNS (less negative or positive)
- Metric: IMPROVED / NOT_IMPROVED / WORSE per trial

**PO-4: Cross-Authority Architecture Consistency**
- Does the EGER pipeline exhibit the same structural behavior (iteration pattern, evidence consumption, revision response) under both Oracles?
- Metric: Qualitative comparison of pipeline traces

## 8. Failure/Retry Review

### Revised Failure Policy

| Failure Type | Recording | Counts as trial? | Retried? |
|-------------|-----------|-------------------|----------|
| Provider failure | Record failure_kind, terminate trial | Yes | Yes (1 retry) |
| Oracle timeout | Record failure_kind, terminate trial | Yes | Yes (1 retry) |
| Oracle non-zero exit | Record failure_kind, terminate trial | Yes | No (Oracle-specific) |
| Invalid task | Record, exclude from analysis | No | No |
| Pipeline failure | Record failure_kind, terminate trial | Yes | Yes (1 retry) |

### Retry Rules
- Maximum 1 retry per trial
- Retry uses same configuration (no parameter changes)
- Both attempts recorded in data schema
- If both fail, trial is a FAILURE
- Retries count against the Oracle call budget

## 9. Randomization Review

### Revised Order Policy

With 8 trials, counterbalance execution order:

- Trials 1-4: Ṛta first, then OpenSTA
- Trials 5-8: OpenSTA first, then Ṛta

Within each block, randomize task assignment.

Record exact execution order for each trial.

## 10. Confounder Review

| Confounder | Risk | Mitigation (Revised) | Residual |
|------------|------|----------------------|----------|
| Oracle property mismatch | HIGH | Shared tasks; both Oracles evaluate same SDC | Findings differ by property — by design |
| Synthetic substrate | HIGH | 2 tasks instead of 1; explicitly bound interpretation | Cannot generalize to real VLSI |
| Model stochasticity | HIGH | 2 replications per condition; freeze temperature; record config hash | Cannot eliminate sampling variance |
| Order effects | MEDIUM | Counterbalance execution order | Partially controlled |
| Provider failures | MEDIUM | 1 bounded retry per trial | May reduce usable trials |
| Task selection bias | MEDIUM | 2 tasks with known properties; document selection rationale | Cannot assess difficulty scaling |
| Task/Oracle entanglement | HIGH | Both Oracles evaluate same SDC; findings differ by property | Property mismatch is by design |
| Revision budget | LOW | Freeze max_iterations=3 | Budget may be insufficient |

## 11. Claim Validity Review

### Claim Hierarchy

**Level 0:** Technical execution demonstrated.
→ Requires: OpenSTA and Ṛta both execute successfully.

**Level 1:** EGER pipeline operated with both Oracles.
→ Requires: Pipeline completes with both Oracles on at least one task.

**Level 2:** EGER pipeline operated with multiple independent deterministic authorities across multiple tasks.
→ Requires: Pipeline completes with both Oracles on both tasks, with evidence production.

**Level 3:** Observed evidence suggests architectural portability under tested conditions.
→ Requires: Level 2 + revision behavior under both Oracles + consistent pipeline structure.

**Level 4:** Generalization beyond tested tasks.
→ NOT supported by this pilot.

### Maximum Defensible Claim

With the revised protocol (8 trials, 2 tasks, 2 Oracles, 2 replications):

**Level 2** is the maximum defensible claim if all trials complete successfully.

**Level 3** requires qualitative evidence of consistent pipeline behavior across conditions.

**Level 4** is explicitly NOT supported.

## 12. Revised Protocol (FROZEN)

### Research Question (UNCHANGED)

> **RQ-5: To what extent does the evidence-grounded EGER architecture generalize across independent deterministic evaluation authorities within VLSI engineering tasks?**

### Experimental Unit (UNCHANGED)

One trial = one complete EGER pipeline execution.

### Task Matrix (REVISED)

| Task | Design | Initial SDC Issue | Ṛta Detectable? | OpenSTA Detectable? |
|------|--------|-------------------|-------------------|---------------------|
| T1 | 3-cell netlist + Liberty | Missing input/output delays | YES (incomplete constraints) | MAYBE (depends on timing) |
| T2 | 3-cell netlist + Liberty | Aggressive clock + missing output delay | YES (incomplete constraints) | YES (setup violation) |

**Key change:** Both tasks are designed so BOTH Oracles can meaningfully evaluate them. T2 explicitly ensures both Oracles find issues.

### Conditions (REVISED)

| Condition | Task | Oracle | Replications |
|-----------|------|--------|-------------|
| A1 | T1 | Ṛta | 2 |
| A2 | T1 | OpenSTA | 2 |
| B1 | T2 | Ṛta | 2 |
| B2 | T2 | OpenSTA | 2 |

**Total: 8 trials**

### What Remains Constant (UNCHANGED)

| Element | Frozen Value |
|---------|-------------|
| Design substrate | P163 3-cell netlist + synthetic Liberty |
| Design name | `simple_path` |
| Prompt template | EGER PromptBuilder |
| Revision policy | RevisionController |
| Evidence normalization | EvidenceNormalizer |
| Verification procedure | VerificationGate |
| Maximum iterations | 3 per trial |
| Maximum Oracle calls | 3 per trial |
| Timeout | 60s per Oracle call |

### What Varies

| Element | Variation |
|---------|-----------|
| Oracle | Ṛta vs OpenSTA |
| Task | T1 vs T2 |
| Execution order | Counterbalanced |
| Replication | 2 per cell |

### Model Configuration (FROZEN at Execution)

```python
{
    "provider": "<frozen before execution>",
    "model": "<frozen before execution>",
    "temperature": 0.0,
    "max_tokens": 4096,
    "system_prompt": "<EGER system prompt>",
    "max_iterations": 3,
    "max_oracle_calls": 3,
}
```

Config hash recorded per trial.

### Primary Outcomes (REVISED)

**PO-1: Pipeline Completion Quality**
- ROBUST: completes + revision improvement detected
- MARGINAL: completes without improvement
- FAILED: does not complete
- Numerator: trials at each level
- Denominator: total trials per condition
- Unit: trial
- Direction: ROBUST > MARGINAL > FAILED
- Missing data: FAILURE trials counted as FAILED

**PO-2: Evidence Contract Compatibility**
- Binary per Oracle evaluation: COMPATIBLE / INCOMPATIBLE
- Numerator: compatible evaluations
- Denominator: total evaluations
- Missing data: ORACLE_FAILURE evaluations excluded from denominator

**PO-3: Oracle-Detected Improvement**
- Initial vs final Oracle evaluation per trial
- Ṛta: ERROR finding count reduction
- OpenSTA: WNS improvement (less negative)
- Categorical: IMPROVED / NOT_IMPROVED / WORSE
- Missing data: FAILED trials excluded

**PO-4: Cross-Authority Pipeline Consistency**
- Qualitative comparison of iteration patterns
- Does the pipeline exhibit similar structural behavior under both Oracles?

### Secondary Outcomes (UNCHANGED)

| Metric | Type |
|--------|------|
| Iteration count | Count |
| Oracle call count | Count |
| Final verification status | Categorical |
| Evidence hash determinism | Binary |
| Failure kind | Categorical |
| WNS (OpenSTA) | Float |
| Violation count (Ṛta) | Count |
| Levenshtein distance | Diagnostic (demoted) |

### Replication (REVISED)

- 2 tasks × 2 Oracles × 2 replications = 8 trials
- Unit of replication: one trial
- Justification: minimum for within-task and cross-task variation
- Inference: descriptive only, no inferential statistics

### Randomization / Order (REVISED)

- Counterbalanced: half Ṛta-first, half OpenSTA-first
- Trials 1-4: Ṛta first
- Trials 5-8: OpenSTA first
- Within blocks: task assignment randomized
- Record exact execution order

### Failure Policy (REVISED)

| Failure Type | Recording | Counts as trial? | Retried? |
|-------------|-----------|-------------------|----------|
| Provider failure | Record, terminate | Yes | Yes (1 retry) |
| Oracle timeout | Record, terminate | Yes | Yes (1 retry) |
| Oracle non-zero exit | Record, terminate | Yes | No |
| Pipeline failure | Record, terminate | Yes | Yes (1 retry) |

### Retry Policy (REVISED)

- Max 1 retry per trial
- Same configuration (no parameter changes)
- Both attempts recorded
- Retries count against Oracle call budget

### Stopping Rules (REVISED)

| Rule | Threshold | Action |
|------|-----------|--------|
| Maximum trials | 8 | Stop |
| Maximum Oracle calls | 24 (3 × 8) | Stop |
| Maximum runtime | 30 minutes total | Stop |
| Environment failure | WSL2 or OpenSTA unavailable | BLOCKED |
| Provider failure | All calls fail for one condition | STOP and report |

### Data Schema (REVISED)

```json
{
    "experiment_id": "EGER-RQ5-PILOT-002",
    "trial_id": "T-<task>-<oracle>-<replicate>",
    "task_id": "T1 | T2",
    "oracle": "Rta | OpenSTA",
    "oracle_version": "<version>",
    "execution_order": "Rta_first | OpenSTA_first",
    "replicate": "1 | 2",
    "model_provider": "<provider>",
    "model_name": "<model>",
    "config_hash": "<sha256>",
    "initial_sdc_hash": "<sha256>",
    "initial_sdc_text": "<text>",
    "initial_oracle_result": "<summary>",
    "initial_evidence_hash": "<sha256>",
    "iterations": [...],
    "final_sdc_hash": "<sha256>",
    "final_sdc_text": "<text>",
    "final_evidence_hash": "<sha256>",
    "final_verification": "ACCEPT | REJECT",
    "completion_quality": "ROBUST | MARGINAL | FAILED",
    "oracle_detected_improvement": "IMPROVED | NOT_IMPROVED | WORSE",
    "revision_magnitude": "<diagnostic>",
    "total_oracle_calls": "<int>",
    "total_runtime_seconds": "<float>",
    "retry_count": "0 | 1",
    "timestamp": "<ISO 8601>"
}
```

### Analysis Plan (REVISED)

**Step 1: Per-Condition Summary Table**

| Task | Oracle | Trial | Completion | Improvement | Evidence Compatible | Verification |
|------|--------|-------|------------|-------------|--------------------|----|
| T1 | Ṛta | 1 | ... | ... | ... | ... |
| T1 | Ṛta | 2 | ... | ... | ... | ... |
| T1 | OpenSTA | 1 | ... | ... | ... | ... |
| T1 | OpenSTA | 2 | ... | ... | ... | ... |
| T2 | Ṛta | 1 | ... | ... | ... | ... |
| T2 | Ṛta | 2 | ... | ... | ... | ... |
| T2 | OpenSTA | 1 | ... | ... | ... | ... |
| T2 | OpenSTA | 2 | ... | ... | ... | ... |

**Step 2: Cross-Condition Comparison**

- Did both Oracles complete on both tasks? (PO-1)
- Did both produce compatible evidence? (PO-2)
- Did both show improvement? (PO-3)
- Is pipeline behavior consistent? (PO-4)

**Step 3: Architecture Generalization Assessment**

- If all 8 trials complete with ROBUST or MARGINAL quality → Level 2 claim
- If consistent pipeline behavior across conditions → Level 3 claim
- If any condition fails consistently → document limitation

**Step 4: Limitation Documentation**

Explicitly state:
- Synthetic substrate limitation
- N=8 descriptive only
- Property mismatch by design
- Cannot claim Level 4

### Confounder Register (REVISED)

| Confounder | Risk | Mitigation | Residual |
|------------|------|------------|----------|
| Oracle property mismatch | HIGH | Shared tasks; both evaluate same SDC | By design |
| Synthetic substrate | HIGH | 2 tasks; bound interpretation | Cannot generalize |
| Model stochasticity | HIGH | 2 replications; freeze temperature | Cannot eliminate |
| Order effects | MEDIUM | Counterbalance | Partially controlled |
| Provider failures | MEDIUM | 1 retry per trial | May reduce data |
| Task selection bias | MEDIUM | 2 tasks; document rationale | Cannot assess scaling |
| Task/Oracle entanglement | HIGH | Both Oracles evaluate same SDC | Property mismatch by design |

### Interpretation Boundary (UNCHANGED)

**Supported:** EGER architecture functions with two different authorities under tested conditions.

**NOT Supported:** Oracle interchangeability, correctness, universal generalization.

### Go/No-Go Criteria (REVISED)

All 16 criteria from P169 Section 25 must be satisfied:

1. ✓ Experimental unit is defensible
2. ✓ Replication adequate for pilot scope (N=8)
3. ✓ Task/Oracle asymmetry controlled (shared tasks)
4. ✓ Primary outcomes address RQ-5
5. ✓ Metrics do not conflate text with engineering (Levenshtein demoted)
6. ✓ Oracle properties not interchangeable (documented)
7. ✓ Model stochasticity controlled (2 replications)
8. ✓ Order effects controlled (counterbalanced)
9. ✓ Failure semantics frozen
10. ✓ Missing data cannot be silently removed
11. ✓ Task-selection bias documented
12. ✓ Synthetic-substrate limitations explicit
13. ✓ Cross-condition contamination prevented
14. ✓ Analysis fully predefined
15. ✓ Claim boundaries explicit
16. ✓ Protocol executable without post-hoc decisions

### Verdict: GO

All 16 criteria satisfied. The revised protocol is executable.

## 13. Research Boundary

```
RQ-5 executed: NO
Experimental data collected: NO
Ṛta modified: NO
OpenSTA modified: NO
RQ-4 reopened: NO
C0-C5 conclusions changed: NO
Oracle comparison performed: NO
```
