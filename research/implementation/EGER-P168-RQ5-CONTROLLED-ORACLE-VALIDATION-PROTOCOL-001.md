# EGER P168 — RQ-5 Controlled Oracle-Validation Experiment Design

## 1. Research Question (FROZEN)

> **RQ-5: To what extent does the evidence-grounded EGER architecture generalize across independent deterministic evaluation authorities within VLSI engineering tasks?**

### What RQ-5 Can Support

- The EGER evidence-grounded revision loop can operate with more than one independent deterministic Oracle under the tested conditions.
- The architecture's Oracle boundary is compatible with structurally different evaluation authorities.

### What RQ-5 Cannot Support

- OpenSTA and Ṛta are interchangeable correctness authorities.
- OpenSTA validates the same engineering property as Ṛta.
- EGER generalizes to all deterministic Oracles.
- EGER improves engineering correctness universally.

## 2. Hypothesis / Expected Observation

**Primary observation:** The EGER pipeline completes successfully (produces evidence, enters verification) with both Oracle A (Ṛta) and Oracle B (OpenSTA) on the same task, without architecture modification.

**Secondary observation:** The evidence-grounded revision loop produces measurable changes between initial and final candidates under both Oracles.

**Null observation:** The pipeline fails to complete with one or both Oracles, or produces no revision behavior under one Oracle.

## 3. Scope

This is a **descriptive controlled pilot**, not a confirmatory study. The replication count is chosen for feasibility and descriptive adequacy, not statistical power. Claims are bounded by the pilot's scope.

## 4. Experimental Unit

| Unit | Definition |
|------|-----------|
| **Task** | A VLSI engineering task defined by: task_id, design substrate (Verilog + Liberty), initial SDC, objective, allowed modification scope |
| **Trial** | One complete EGER pipeline execution: task → initial candidate → Oracle evaluation → evidence → revision loop → final verification |
| **Candidate revision** | One SDC modification proposed by the LLM in response to Oracle evidence |
| **Oracle evaluation** | One invocation of the Oracle on a candidate SDC, producing an OracleResult |
| **Successful run** | Pipeline completes with final VerificationResult (ACCEPT or REJECT) |
| **Failed run** | Pipeline terminates due to provider failure, Oracle failure, timeout, or environment error |
| **Invalid trial** | A trial where the task definition is malformed or the substrate is inaccessible |
| **Missing data** | A trial where the Oracle produces no usable evidence (ORACLE_FAILURE without partial evidence) |

## 5. Task Substrate Design

### Critical Design Decision: Shared Task Property

Ṛta and OpenSTA evaluate **fundamentally different properties**:

| Oracle | Property | Evidence Type |
|--------|----------|---------------|
| Ṛta | SDC constraint quality: syntax, semantics, completeness, best practices | ERROR/WARNING/INFO findings with severity, code, message, location |
| OpenSTA | Static timing analysis: setup/hold violations, path timing, slack | Timing violations, WNS/TNS, path reports |

**There is no single engineering property that both Oracles meaningfully evaluate.**

Therefore, the experiment does **not** test whether both Oracles agree on "correctness." Instead, it tests whether the **EGER architecture** (evidence-grounded revision loop) functions with both authorities.

### Task Set (FROZEN)

The experiment uses **one controlled task** with **two constraint perturbations**:

#### Task T1: Clock Constraint Completeness

```
task_id: T1-CLOCK-CONSTRAINT
design substrate: P163 minimal 3-cell netlist (INVX1 → AND2X1 → DFFX1)
                  + synthetic Liberty (simple_cells.lib)
                  + WSL2 OpenSTA v2.2.0
objective: Produce an SDC that defines clock constraints for the design
allowed modification scope: SDC text only (create_clock, set_input_delay,
                            set_output_delay, set_clock_groups, etc.)
```

#### Perturbation P1a: Missing output delay (RQ-5-Rta)

Initial SDC has `create_clock` but no `set_output_delay`. Ṛta should identify this as incomplete.

```
Initial SDC:
  create_clock -name clk -period 10.0 [get_ports clk]
  # Missing: set_output_delay, set_input_delay
```

#### Perturbation P1b: Aggressive clock period (RQ-5-OpenSTA)

Initial SDC has `create_clock` with a period too short for the Liberty timing. OpenSTA should identify a setup violation.

```
Initial SDC:
  create_clock -name clk -period 0.05 [get_ports clk]
  # Clock period too short → setup violation
```

### Why Two Perturbations

Each perturbation is designed to be **detectable by one Oracle but not necessarily the other**:

- **P1a (missing output delay)**: Ṛta can detect incompleteness via constraint analysis. OpenSTA may or may not flag it depending on whether the missing delay causes a timing violation.
- **P1b (aggressive clock)**: OpenSTA will definitively detect the setup violation. Ṛta may not flag it because the SDC is syntactically correct.

This asymmetry is **by design** — it tests whether the architecture handles authority-specific evidence, not whether authorities agree.

## 6. Conditions

### Condition A: ORACLE_RTA

```
Task: T1-CLOCK-CONSTRAINT with perturbation P1a
Oracle: EvidenceOracle (Ṛta v1.5.11, revision 3b5c2f2)
Evidence path: Ṛta → OracleResult → EvidenceNormalizer → EvidenceArtifact
```

### Condition B: ORACLE_OPENSTA

```
Task: T1-CLOCK-CONSTRAINT with perturbation P1b
Oracle: OpenSTAAdapter (OpenSTA v2.2.0, WSL2)
Evidence path: OpenSTA → OracleResult → EvidenceNormalizer → EvidenceArtifact
```

### What Remains Constant

| Element | Frozen Value |
|---------|-------------|
| Task substrate | P163 3-cell netlist + synthetic Liberty |
| Design name | `simple_path` |
| Model provider | (to be frozen at execution time) |
| Model name | (to be frozen at execution time) |
| Prompt template | EGER PromptBuilder (existing) |
| Revision policy | RevisionController (existing) |
| Evidence normalization | EvidenceNormalizer (existing) |
| Verification procedure | VerificationGate (existing) |
| Maximum iterations | 3 per trial |
| Maximum Oracle calls | 3 per trial |
| Timeout | 60s per Oracle call |

### What Varies

| Element | Condition A | Condition B |
|---------|-------------|-------------|
| Oracle | Ṛta | OpenSTA |
| Perturbation | P1a (missing output delay) | P1b (aggressive clock) |
| Evidence type | Constraint quality | Timing analysis |

## 7. Oracle Definitions

### Oracle A — Ṛta

```python
EvidenceOracle(
    rta_cli=Path("rta-constraint-intelligence/cli.py"),
    oracle_revision="3b5c2f2",
    timeout_seconds=60,
)
```

- Evaluates: SDC constraint quality
- Produces: ERROR/WARNING/INFO findings
- Input: SDC text only (no netlist required)
- Deterministic: Yes (same SDC → same findings)

### Oracle B — OpenSTA

```python
OpenSTAAdapter(
    sta_binary=Path(win_path),  # resolved via wslpath
    timeout_seconds=60,
)
```

- Evaluates: Static timing analysis
- Produces: WNS/TNS, timing violations, path reports
- Input: SDC text + Verilog netlist + Liberty library
- Deterministic: Yes (same inputs → same timing)

## 8. Model Configuration (FROZEN at Execution)

The following must be frozen before any trial execution:

```python
{
    "provider": "<to be filled at execution>",
    "model": "<to be filled at execution>",
    "temperature": 0.0,  # or provider-appropriate deterministic setting
    "max_tokens": 4096,
    "system_prompt": "<EGER system prompt>",
    "task_prompt": "<PromptBuilder output>",
    "max_iterations": 3,
    "max_oracle_calls": 3,
}
```

The model configuration hash must be recorded for each trial.

## 9. Prompt/Protocol Freeze

The prompt template is the existing `PromptBuilder` output. No prompt modification is permitted during the experiment. The prompt must be recorded (hashed) before execution.

## 10. Control Conditions

### Baseline: Initial Candidate (No Revision)

For each perturbation, record the initial candidate SDC and its Oracle evaluation **before any revision**. This establishes the starting point.

### Revision Condition: EGER Pipeline

Run the full EGER pipeline (up to 3 iterations) and record the final candidate and its Oracle evaluation.

## 11. Primary Outcomes

### PO-1: Pipeline Completion

**Definition:** Does the EGER pipeline complete successfully (produce a final VerificationResult) with each Oracle?

**Metric:** Binary (COMPLETED / FAILED) per trial.

**Why it answers RQ-5:** If the pipeline completes with both Oracles, the architecture generalizes at the Oracle boundary.

### PO-2: Evidence Production

**Definition:** Does each Oracle produce structured evidence that enters the EGER evidence contract without authority-specific changes?

**Metric:** Binary (EVIDENCE_PRODUCED / NO_EVIDENCE) per Oracle evaluation.

**Why it answers RQ-5:** Evidence contract compatibility is the architectural prerequisite for generalization.

### PO-3: Revision Behavior

**Definition:** Does the evidence-grounded revision loop produce measurable changes between initial and final candidates?

**Metric:** Revision magnitude (Levenshtein distance or structural diff between initial and final SDC) per trial.

**Why it answers RQ-5:** If revision behavior occurs under both Oracles, the architecture's control loop is functional across authorities.

## 12. Secondary Outcomes

| Metric | Definition | Type |
|--------|-----------|------|
| Iteration count | Number of revision iterations completed | Count |
| Oracle call count | Total Oracle invocations per trial | Count |
| Final verification status | ACCEPT or REJECT per trial | Categorical |
| Evidence hash determinism | Same inputs → same evidence hash | Binary |
| Failure kind | ORACLE_FAILURE / INVALID_REQUEST / timeout | Categorical |
| WNS (OpenSTA only) | Worst negative slack | Float |
| Violation count (Ṛta only) | Number of ERROR findings | Count |

## 13. Replication

**Unit of replication:** One trial = one complete pipeline execution.

**Replication count:** 1 per condition (total: 2 trials).

**Justification:** This is a feasibility pilot. The primary question is whether the pipeline **can** operate with both Oracles, not whether it does so reliably across many trials. A single trial per condition is sufficient to demonstrate (or fail to demonstrate) architectural compatibility.

**If the pilot succeeds:** Future work should replicate with N ≥ 10 per condition for descriptive statistics.

**Inference justified:** Descriptive only. No inferential statistics are appropriate with N=1 per condition.

## 14. Randomization / Order

With one trial per condition, randomization is not applicable. The execution order is:

1. Condition A (Ṛta) — first
2. Condition B (OpenSTA) — second

**Rationale:** Ṛta is the established baseline; OpenSTA is the candidate. Running the baseline first provides a reference point.

**Confounder:** Order effects are not controlled. This is documented as a limitation.

## 15. Failure / Missing-Data Policy (FROZEN)

| Failure Type | Recording | Counts as trial? | Retried? |
|-------------|-----------|-------------------|----------|
| Provider failure | Record failure_kind="PROVIDER_FAILURE", terminate trial | Yes | No |
| Oracle timeout | Record failure_kind="TIMEOUT", terminate trial | Yes | No |
| Oracle non-zero exit | Record failure_kind="ORACLE_FAILURE", terminate trial | Yes | No |
| Invalid task | Record failure_kind="INVALID_TASK", exclude from analysis | No | No |
| Missing Oracle output | Record failure_kind="MISSING_OUTPUT", terminate trial | Yes | No |
| Partial evidence | Record as partial, include in analysis with caveat | Yes | No |
| Pipeline failure | Record failure_kind="PIPELINE_FAILURE", terminate trial | Yes | No |

**Retry policy:** No retries. Each trial is executed once. Failures are recorded, not deleted.

## 16. Stopping Rules (FROZEN)

| Rule | Threshold | Action |
|------|-----------|--------|
| Maximum trials | 2 (1 per condition) | Stop |
| Maximum Oracle calls | 6 total (3 per condition) | Stop |
| Maximum runtime | 10 minutes total | Stop |
| Environment failure | WSL2 or OpenSTA unavailable | BLOCKED |
| Provider failure | All model calls fail | STOP and report |

## 17. Data Schema (FROZEN)

```json
{
    "experiment_id": "EGER-RQ5-PILOT-001",
    "trial_id": "T-<condition>-<task>",
    "task_id": "T1-CLOCK-CONSTRAINT",
    "perturbation": "P1a | P1b",
    "oracle": "Rta | OpenSTA",
    "oracle_version": "<version>",
    "oracle_revision": "<revision>",
    "model_provider": "<provider>",
    "model_name": "<model>",
    "config_hash": "<sha256>",
    "initial_sdc_hash": "<sha256>",
    "initial_sdc_text": "<text>",
    "initial_oracle_result": "<OracleResult summary>",
    "initial_evidence_hash": "<sha256>",
    "iterations": [
        {
            "iteration": 1,
            "candidate_sdc_hash": "<sha256>",
            "candidate_sdc_text": "<text>",
            "oracle_result": "<OracleResult summary>",
            "evidence_hash": "<sha256>",
            "verification_decision": "ACCEPT | REJECT",
            "runtime_seconds": "<float>"
        }
    ],
    "final_sdc_hash": "<sha256>",
    "final_sdc_text": "<text>",
    "final_evidence_hash": "<sha256>",
    "final_verification": "ACCEPT | REJECT",
    "revision_magnitude": "<Levenshtein distance>",
    "completion_status": "COMPLETED | FAILED",
    "failure_kind": "<if failed>",
    "total_oracle_calls": "<int>",
    "total_runtime_seconds": "<float>",
    "timestamp": "<ISO 8601>"
}
```

## 18. Provenance

Every trial must be reconstructable. Capture:

- Task definition (hash)
- Initial SDC (hash + text)
- Model configuration (hash)
- Prompt (hash)
- Each Oracle invocation: input hash, output bytes, exit code, evidence hash
- Each candidate SDC: hash + text
- Final verification result
- Failure state (if any)

## 19. Blinding / Analysis

**Blinding is not feasible.** The two Oracles produce fundamentally different evidence types (constraint findings vs. timing reports). An analyst can always distinguish them.

**Analysis is descriptive.** No inferential statistics. Report per-condition outcomes in a table.

## 20. Analysis Plan (FROZEN)

### Step 1: Per-Condition Summary

For each condition (A and B), report:
- Pipeline completion status
- Evidence produced (yes/no)
- Final verification decision
- Iteration count
- Oracle call count
- Revision magnitude

### Step 2: Cross-Condition Comparison

Compare:
- Did both conditions complete? (PO-1)
- Did both produce evidence? (PO-2)
- Did both show revision behavior? (PO-3)

### Step 3: Architecture Generalization Assessment

Answer RQ-5 based on:
- If both conditions complete with evidence and revision → architecture generalizes (under tested conditions)
- If one condition fails → architecture has Oracle-specific limitations (document which)
- If neither completes → architecture does not generalize (under tested conditions)

### Step 4: Limitation Documentation

Explicitly state what cannot be claimed based on the pilot's scope.

## 21. Confounder Register

| Confounder | Risk | Mitigation | Residual |
|------------|------|------------|----------|
| Oracle property mismatch | HIGH | Document shared vs authority-specific outcomes; do not compare scores | Cannot be eliminated — by design |
| Synthetic substrate | HIGH | Explicitly bound interpretation to synthetic 3-cell circuit | Cannot generalize to real VLSI |
| Model stochasticity | MEDIUM | Freeze temperature, record config hash; N=1 limits inference | Cannot control sampling variance |
| Oracle execution order | LOW | Document fixed order (Ṛta first) | Order effect uncontrolled |
| Provider failures | MEDIUM | Predefined failure policy; no retries | May reduce usable trials |
| Parser differences | LOW | Shared EvidenceNormalizer contract | Both adapters map to same contract |
| Different error taxonomies | MEDIUM | Preserve raw + normalized evidence; do not compare finding counts | Taxonomy mismatch acknowledged |
| Environment differences | LOW | Freeze WSL2, OpenSTA version, Tcl version | Windows host assumed |
| Task difficulty | MEDIUM | Single task with known perturbations | Cannot assess difficulty scaling |
| Revision budget | LOW | Freeze max_iterations=3, max_oracle_calls=3 | Budget may be insufficient for complex tasks |

## 22. Threats to Validity

### Internal Validity

**Can observed differences be attributed to the Oracle condition?**

Partially. The two conditions differ in Oracle AND perturbation. This is intentional — each Oracle gets the perturbation it can detect. The experiment does not claim to isolate the Oracle effect independent of perturbation.

### Construct Validity

**Does the experiment actually measure "architecture generalization"?**

It measures whether the pipeline completes with two different Oracles. This is a necessary but not sufficient condition for architecture generalization. The experiment does not measure whether the architecture produces **good** engineering outcomes — only whether it **functions** with different authorities.

### External Validity

**What can and cannot be generalized?**

- **Can:** The EGER architecture's Oracle boundary is compatible with structurally different evaluation authorities (under tested conditions).
- **Cannot:** Generalization to real VLSI workloads, other Oracle types, other engineering domains, or production deployment.

### Statistical Conclusion Validity

**What conclusions are justified?**

Descriptive only. With N=1 per condition, no inferential statistics are appropriate. The pilot demonstrates feasibility, not reliability.

## 23. Interpretation Boundary

### Supported Claim (if pilot succeeds)

> The EGER evidence-grounded control loop can operate with at least two structurally different deterministic evaluation authorities (Ṛta for constraint quality, OpenSTA for timing analysis) under the tested synthetic conditions, without architecture modification.

### NOT Supported (regardless of outcome)

- OpenSTA and Ṛta are interchangeable
- OpenSTA validates the same property as Ṛta
- EGER generalizes to all deterministic Oracles
- EGER improves engineering correctness
- The architecture works for production VLSI tasks
- One trial demonstrates reliability

## 24. Go / No-Go Criteria

### GO

All of the following must be true:

1. ✓ Research question is frozen (Section 1)
2. ✓ Experimental unit is unambiguous (Section 4)
3. ✓ Oracle roles are clearly separated (Section 7)
4. ✓ Shared vs authority-specific outcomes are defined (Section 5)
5. ✓ Task set is frozen (Section 5)
6. ✓ Model configuration can be frozen (Section 8)
7. ✓ Revision budget is frozen (Section 6)
8. ✓ Failure/missing-data policy is frozen (Section 15)
9. ✓ Replication plan is justified (Section 13)
10. ✓ Analysis plan is defined before execution (Section 20)
11. ✓ Confounders are documented (Section 21)
12. ✓ Interpretation boundaries are explicit (Section 23)
13. ✓ No Ṛta modification is required
14. ✓ No EGER architecture change is required
15. ✓ Experimental artifacts can be captured without contaminating Git

### Verdict: GO

All 15 criteria are satisfied. The protocol is executable.

## 25. Execution Checklist

For the execution agent:

- [ ] Freeze model provider and model name
- [ ] Record model configuration hash
- [ ] Verify WSL2 + OpenSTA availability
- [ ] Verify Ṛta availability
- [ ] Execute Condition A (Ṛta + P1a)
- [ ] Record all artifacts for Condition A
- [ ] Execute Condition B (OpenSTA + P1b)
- [ ] Record all artifacts for Condition B
- [ ] Run analysis plan (Section 20)
- [ ] Create execution record
- [ ] Do NOT modify Ṛta, RQ-4, or C0–C5 conclusions

## Research Boundary

```
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: NO (protocol designed only)
C0-C5 conclusions changed: NO
OpenSTA implementation changed: NO
VerificationGate authority changed: NO
Epistemic-state logic added: NO
Authorization logic added: NO
```
