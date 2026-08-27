# EGER-P054 — Measurement Upgrade Specification & Change-Control Design

| Field | Value |
|---|---|
| ID | EGER-P054-MEASUREMENT-UPGRADE-SPECIFICATION-001 |
| Date | 2026-08-27 |
| Scope | SCIENTIFIC DESIGN AND CHANGE-CONTROL — no implementation |
| Status | **DESIGN COMPLETE — AWAITING HUMAN AUTHORIZATION** |

---

## 1. Executive Verdict

**The measurement upgrade must be evaluator-side only.** Design metadata (port list, clock definitions) is classified `EVALUATOR_ONLY` — it is never exposed to the model. This preserves causal comparability with all historical C0/C1/C2 results while enabling the Oracle to achieve `FULL` scope.

The upgrade requires:
- New auxiliary metadata files (one per task)
- Oracle adapter modification to accept metadata
- Re-evaluation of existing artifacts
- No benchmark modification, no model modification, no treatment modification

---

## 2. Governing Scientific State

| Item | Status | Source |
|------|--------|--------|
| RQ-1 | SUPPORTED | C0/C1/C2 |
| RQ-2 | SUPPORTED | P037, C2/MODEL-004 |
| RQ-3 | SUPPORTED | C2/MODEL-004 (4/4 changed) |
| RQ-4 | **INCONCLUSIVE** | P051 — oracle limitation |
| RQ-5 | PREMATURE | P052 — blocked on RQ-4 |
| C3 | NOT AUTHORIZED | P052 — premature |
| Measurement bottleneck | NETLIST_REQUIRED | P053 |

---

## 3. Critical Design Question

> What information does the Oracle need to validate each SDC construct, and should the model see that information?

### 3.1 Per-Construct Analysis

| SDC Construct | Oracle Needs | Model Needs? | Evaluator-Only Sufficient? |
|---------------|-------------|-------------|---------------------------|
| `create_clock [get_ports clk]` | Port list (clk exists, type=clock) | ❌ NO — task text already says "clk" | ✅ YES |
| `create_generated_clock ... [get_pins div_reg/Q]` | Cell/pin list (div_reg exists) | ❌ NO — task text says "div_reg" | ✅ YES |
| `set_input_delay ... [get_ports data_in]` | Port list (data_in exists, direction=input) | ❌ NO — task text says "data_in" | ✅ YES |
| `set_output_delay ... [get_ports data_out]` | Port list (data_out exists, direction=output) | ❌ NO — task text says "data_out" | ✅ YES |
| `set_false_path -from [get_pins cfg_reg/Q]` | Cell/pin list (cfg_reg exists) | ❌ NO — task text says "cfg_reg" | ✅ YES |
| `set_multicycle_path ... [get_pins pipe_reg1/Q]` | Cell/pin list (pipe_reg1 exists) | ❌ NO — task text says "pipe_reg1" | ✅ YES |
| Clock period validation | Clock definition (clk = 10ns) | ❌ NO — task text says "10ns" | ✅ YES |

**Key insight:** The model already receives all this information in the task text (`design_context` field). The metadata merely gives the Oracle the same information in a structured format it can programmatically validate against.

### 3.2 Does Metadata Leak Solution Information?

| Metadata Field | Reveals Correct SDC? | Reveals Constraint Values? |
|---------------|---------------------|---------------------------|
| Port name: `clk` | ❌ NO — doesn't tell you what to write | ❌ NO |
| Port direction: `input` | ❌ NO | ❌ NO |
| Port type: `clock` | ❌ NO | ❌ NO |
| Clock period: `10` | ⚠️ PARTIALLY — Oracle can check if period matches | ❌ NO (doesn't tell you to write `create_clock`) |
| Cell name: `div_reg` | ❌ NO | ❌ NO |
| Pin name: `div_reg/Q` | ❌ NO | ❌ NO |

**Conclusion:** The metadata describes the design structure, not the solution. It enables validation but does not enable generation.

---

## 4. Information Boundary Matrix

### 4.1 Three-Tier Classification

| Tier | Description | Who Sees It |
|------|-------------|------------|
| `ENGINEER_VISIBLE` | Task context, objective, constraints, structured feedback | Model only |
| `ORACLE_VISIBLE` | SDC candidate, design metadata, evaluation context | Oracle only |
| `EVALUATOR_ONLY` | Expected SDC, hidden answers, research canon | Neither model nor Oracle |

### 4.2 Per-Field Classification

| Field | Current Tier | Proposed Tier | Justification |
|-------|-------------|---------------|---------------|
| `task_id` | ENGINEER_VISIBLE | ENGINEER_VISIBLE | Model needs task identity |
| `design_context` | ENGINEER_VISIBLE | ENGINEER_VISIBLE | Model needs design description |
| `objective` | ENGINEER_VISIBLE | ENGINEER_VISIBLE | Model needs task objective |
| `constraints` | ENGINEER_VISIBLE | ENGINEER_VISIBLE | Model needs constraints |
| `oracle_scope` | EVALUATOR_ONLY | EVALUATOR_ONLY | Oracle metadata, not for model |
| `evaluation_scope` | EVALUATOR_ONLY | EVALUATOR_ONLY | Oracle metadata, not for model |
| **`design_metadata`** | **N/A** | **ORACLE_VISIBLE** | **NEW — Oracle validation context** |
| `expected_artifact_validity` | EVALUATOR_ONLY | EVALUATOR_ONLY | Hidden answer |
| `expected_findings` | EVALUATOR_ONLY | EVALUATOR_ONLY | Hidden answer |
| `classification` | EVALUATOR_ONLY | EVALUATOR_ONLY | Hidden answer |

### 4.3 Critical Rule

**`design_metadata` must NEVER appear in the model's prompt.**

The model receives only:
- `design_context` (natural language description)
- `objective` (task goal)
- `constraints` (SDC requirements)
- `structured_feedback` (EvidenceArtifact findings)

The Oracle receives additionally:
- `design_metadata` (structured port/clock/cell definitions)

---

## 5. Minimum Metadata Specification

### 5.1 Design

The minimum metadata package for each task:

```json
{
  "task_id": "BENCH2-001",
  "design_metadata": {
    "ports": [
      {"name": "clk", "direction": "input", "type": "clock", "bus": false},
      {"name": "reset", "direction": "input", "type": "reset", "bus": false},
      {"name": "data_in", "direction": "input", "type": "data", "bus": true, "range": "[7:0]"},
      {"name": "data_out", "direction": "output", "type": "data", "bus": true, "range": "[7:0]"}
    ],
    "clocks": [
      {"name": "clk", "period_ns": 10, "port": "clk"}
    ],
    "cells": [],
    "metadata_version": "eger.design_metadata.v1"
  }
}
```

### 5.2 Metadata Fields

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `ports[].name` | string | YES | Port identifier for validation |
| `ports[].direction` | enum | YES | input/output/inout |
| `ports[].type` | enum | YES | clock/reset/data/control/power |
| `ports[].bus` | boolean | YES | Whether port is a bus |
| `ports[].range` | string | NO | Bus range if bus=true |
| `clocks[].name` | string | YES | Clock identifier |
| `clocks[].period_ns` | number | YES | Clock period in nanoseconds |
| `clocks[].port` | string | YES | Port that carries this clock |
| `cells[].name` | string | NO | Cell instance name |
| `cells[].type` | string | NO | Cell type (e.g., "register", "latch") |
| `cells[].pins` | list | NO | Pin names for timing references |
| `metadata_version` | string | YES | Schema version |

### 5.3 Minimum vs Full

| Level | Includes | Measurement Capability | Leakage Risk |
|-------|----------|----------------------|-------------|
| A: Port names only | Port names | Validates port references | LOW |
| B: Ports + directions | Port names + directions | Validates I/O direction | LOW |
| C: Ports + clocks | Ports + clock definitions | Validates clock constraints | LOW |
| D: Ports + clocks + cells | Ports + clocks + cell/pin references | Validates timing references | LOW |
| E: Full netlist | All design objects | Complete validation | MEDIUM |

**Recommended: Level C (Ports + Clocks)**

This provides:
- Port reference validation (all 6 tasks)
- Clock constraint validation (all 6 tasks)
- I/O direction validation (tasks 003, 005)
- Generated clock validation (task 002)

It does NOT provide:
- Pin/cell reference validation (tasks 002, 004, 005)
- Full timing analysis

Level C is the minimum that achieves `FULL` scope for the majority of constructs.

---

## 6. Benchmark Status Decision

### 6.1 Classification

The metadata is:

**B. An evaluator-side auxiliary artifact**

### 6.2 Justification

| Option | Assessment | Why Not/Why |
|--------|-----------|-------------|
| A. Part of BENCH-002 | ❌ REJECTED | Modifies historical benchmark |
| B. Evaluator-side auxiliary | ✅ SELECTED | Clean separation, no benchmark mutation |
| C. New benchmark version | ❌ REJECTED | Unnecessary version proliferation |
| D. Generated from benchmark | ⚠️ PARTIALLY | Can be generated, but should be frozen |
| E. Another approach | ❌ REJECTED | B is sufficient |

### 6.3 Implementation

The metadata files live in a NEW directory:

```
research/experiments/EGER-BENCH-002/evaluator_context/
  ├── BENCH2-001.design_metadata.json
  ├── BENCH2-002.design_metadata.json
  ├── BENCH2-003.design_metadata.json
  ├── BENCH2-004.design_metadata.json
  ├── BENCH2-005.design_metadata.json
  └── BENCH2-006.design_metadata.json
```

This directory:
- Is separate from `tasks/engineer_visible/` (model input)
- Is separate from `evaluator_only/` (hidden answers)
- Is `ORACLE_VISIBLE` (Oracle reads it)
- Is NOT `ENGINEER_VISIBLE` (model never sees it)
- Is version-controlled as auxiliary evaluation context

### 6.4 BENCH-002 Preservation

**BENCH-002 remains UNCHANGED.** The task JSON files in `tasks/engineer_visible/` are not modified. The evaluator_only expected answers are not modified. Only a NEW directory is created.

---

## 7. Historical Artifact Re-Evaluation

### 7.1 Re-Evaluation Plan

All existing candidate SDC files can be re-evaluated with the enhanced Oracle (with metadata) WITHOUT generating new model outputs.

| Condition | Artifacts | Can Re-Evaluate? | Scientific Value |
|-----------|-----------|-------------------|-----------------|
| C0 (MODEL-002) | 6 final candidates | ✅ YES | Baseline with measurement improvement |
| C1 (MODEL-002) | 6 final candidates | ✅ YES | Text feedback with measurement improvement |
| C2 canned (MODEL-003) | 6 final candidates | ✅ YES | Structured feedback, canned model |
| C2 exploratory (MODEL-004) | 4 final candidates | ✅ YES | Live model, exploratory |
| C2 formal (MODEL-004) | 4 final candidates | ✅ YES | Live model, formal |

### 7.2 Scientific Advantage

Re-evaluation isolates the measurement improvement:

```
Before: C0 candidate → Oracle (without metadata) → INSUFFICIENT scope
After:  C0 candidate → Oracle (with metadata) → FULL scope

Same candidate. Same model output. Better measurement.
```

This directly answers: **"Does the measurement improvement reveal new information about existing results?"**

### 7.3 What Re-Evaluation Cannot Do

- Cannot change model outputs (same SDC files)
- Cannot change treatment (same feedback)
- Cannot change model identity (same MODEL-002/004)
- Cannot answer "did the model improve?" (already answered by P051)

### 7.4 Re-Evaluation vs Re-Execution

| | Re-Evaluation | Re-Execution |
|---|--------------|--------------|
| Model calls | 0 | 12 (6 tasks × 2 calls) |
| Oracle calls | 12 (6 tasks × 2 calls) | 12 |
| Nondeterminism | NONE | POTENTIAL |
| Scientific value | HIGH — measurement improvement | HIGH — complete sample |
| Recommended first | ✅ YES | Only if re-evaluation is insufficient |

---

## 8. Causal Control

### 8.1 If Metadata is ORACLE_VISIBLE Only

| Concern | Assessment |
|---------|-----------|
| Model sees metadata | ❌ NO — never in model prompt |
| Model behavior changes | ❌ NO — same prompts, same model |
| Treatment changes | ❌ NO — same feedback |
| Historical comparability | ✅ PRESERVED — same candidates, better measurement |
| Confounding risk | ✅ MINIMAL — no model-information change |

### 8.2 If Metadata Were ENGINEER_VISIBLE

| Concern | Assessment |
|---------|-----------|
| Model sees metadata | ⚠️ YES — different information environment |
| Model behavior changes | ⚠️ POSSIBLE — might influence generation |
| Treatment changes | ⚠️ EFFECTIVELY — different model inputs |
| Historical comparability | ❌ COMPROMISED — C0/C1/C2 results not comparable |
| Confounding risk | ❌ HIGH — measurement upgrade and model change confounded |

**CONCLUSION:** Metadata must remain `EVALUATOR_ONLY` (ORACLE_VISIBLE) to preserve causal validity.

---

## 9. Oracle Design

### 9.1 Input Contract (After Upgrade)

```
Oracle.validate(
    sdc_text: str,                    # SDC candidate (existing)
    design_metadata: Dict = None,     # NEW — optional metadata
    input_identity: str = "candidate",
    ...
) -> OracleResult
```

### 9.2 Metadata Contract

```python
@dataclass
class DesignMetadata:
    metadata_version: str  # "eger.design_metadata.v1"
    ports: List[Port]      # Port definitions
    clocks: List[Clock]    # Clock definitions
    cells: List[Cell]      # Cell definitions (optional)
```

### 9.3 Validation Stages (After Upgrade)

```
Stage 1: Syntax validation (existing)
    ↓
Stage 2: Structural validation (existing)
    ↓
Stage 3: Scope classification (existing)
    ↓
Stage 4: Design metadata validation (NEW)
    - Port reference check: get_ports X → does X exist?
    - Clock reference check: get_clocks X → does X exist?
    - Clock period check: create_clock period → matches metadata?
    - Direction check: set_input_delay on output port → ERROR
    ↓
Stage 5: Finding generation (existing, enhanced by Stage 4)
```

### 9.4 Scope Determination (After Upgrade)

| Condition | Without Metadata | With Metadata |
|-----------|-----------------|---------------|
| All constructs VALIDATED | FULL | FULL |
| All constructs PARTIALLY_VALIDATED | PARTIAL | PARTIAL |
| Any construct NETLIST_REQUIRED (port ref) | INSUFFICIENT | **FULL** (port metadata available) |
| Any construct NETLIST_REQUIRED (cell ref) | INSUFFICIENT | **PARTIAL** (no cell metadata at Level C) |
| Any construct UNSUPPORTED | UNSUPPORTED | UNSUPPORTED |

### 9.5 Deterministic Behavior

The metadata is static (frozen per task). The Oracle's validation against metadata is deterministic. Therefore:
- Same SDC + same metadata → same EvidenceArtifact
- Re-evaluation is reproducible
- Evidence hashes remain stable for identical inputs

### 9.6 Oracle Must NOT Become

- ❌ Proposal authority (doesn't generate SDC)
- ❌ Treatment authority (doesn't provide feedback)
- ❌ Model selector (doesn't choose models)

---

## 10. FULL/PARTIAL/INSUFFICIENT Definitions (After Upgrade)

### 10.1 FULL

```
FULL = ALL constructs in the SDC are validated against design metadata:
  - All get_ports references exist in metadata
  - All get_clocks references exist in metadata
  - All clock periods match metadata
  - All I/O directions match metadata
  - No unsupported constructs present
```

### 10.2 PARTIAL

```
PARTIAL = Some constructs validated, some require additional context:
  - Port/clock references validated
  - But cell/pin references require netlist (not available at Level C)
  - OR some constructs are UNSUPPORTED
```

### 10.3 INSUFFICIENT

```
INSUFFICIENT = Critical references cannot be validated:
  - Metadata does not contain required port/clock definitions
  - OR metadata is not available for this task
  - OR metadata version mismatch
```

### 10.4 UNSUPPORTED

```
UNSUPPORTED = Construct type not supported by Oracle:
  - TCL_EXECUTION_REQUIRED
  - NOT_VALIDATED
  - Unknown construct type
```

---

## 11. Correctness Metrics (Pre-Registered)

### 11.1 Primary Metric

**Constraint Validity Rate (CVR):**

```
CVR = (constraints with valid references) / (total constraints in SDC)
```

Where "valid references" means:
- `get_ports X` → X exists in metadata port list
- `get_clocks X` → X exists in metadata clock list
- `get_pins X/Y` → X exists in metadata cell list (if available)
- Clock period matches metadata definition

**Range:** 0.0 (all invalid) to 1.0 (all valid)

### 11.2 Secondary Metrics

| Metric | Description | Range |
|--------|-------------|-------|
| Evidence scope | FULL / PARTIAL / INSUFFICIENT / UNSUPPORTED | Categorical |
| Oracle finding count | Total findings per SDC | 0+ |
| Error count | Findings with severity=error | 0+ |
| Warning count | Findings with severity=warning | 0+ |
| Required-constraint coverage | % of required constraints present | 0–100% |
| Invalid-reference rate | % of constraints with invalid references | 0–100% |
| Artifact validity | VALID_ARTIFACT / INVALID_ARTIFACT | Categorical |
| Proposal changed | initial_hash ≠ final_hash | Boolean |
| Finding resolution | Findings addressed by revision | 0+ |

### 11.3 Metrics NOT Chosen

| Metric | Why Not |
|--------|---------|
| Finding count alone | Doesn't distinguish errors from warnings |
| Scope alone | Doesn't measure correctness within scope |
| Binary valid/invalid | Too coarse — misses partial correctness |
| Timing correctness | Not measurable without STA tools |

---

## 12. Missing Tasks

### 12.1 BENCH2-003 and BENCH2-006

These tasks were MODEL_UNAVAILABLE in the formal C2 run.

### 12.2 Impact of Measurement Upgrade

With enhanced metadata:
- Existing artifacts from tasks 003/006 **still cannot be re-evaluated** (no artifacts exist)
- BUT: C0/C1 artifacts for these tasks CAN be re-evaluated (they exist from those runs)
- Re-evaluation of existing C0/C1 artifacts for 003/006 provides measurement-improved baselines

### 12.3 Re-Execution Decision

If the measurement upgrade reveals that C0/C1/C2 comparisons are more informative with complete data, then re-execution of tasks 003/006 may be warranted. This is a separate decision after re-evaluation results.

---

## 13. Model Control

### 13.1 MODEL-004 Status

MODEL-004 remains frozen:
- provider = opencode
- model = opencode/nemotron-3-ultra-free
- temperature = 0.0
- tools = []
- prompt = eger.prompt.v1

### 13.2 Measurement Upgrade Independence

The measurement upgrade is **independent of model identity**:
- Same candidates are re-evaluated (no model calls)
- Same metadata applies to all conditions
- No model selection involved
- No model behavior change

### 13.3 Future Model Experiments

If future experiments use a different model, the same metadata enables fair comparison:
- Same Oracle, same metadata, different model
- Measurement improvement applies uniformly

---

## 14. C3 Gate

### 14.1 Should C3 Be Blocked Until Measurement Is Adequate?

**YES.** C3 introduces epistemic state (hypothesis/validated/refuted/unknown). The epistemic transitions require the Oracle to establish `VALIDATED` or `REFUTED` — which requires `FULL` scope.

Without measurement improvement:
- C3's epistemic transitions cannot be reliably measured
- The question "does epistemic state improve reasoning?" cannot be answered
- Adding C3 on top of an incompletely-measured C2 creates compounding unknowns

### 14.2 C3 Authorization Requirement

C3 authorization requires:
1. Measurement upgrade implemented and validated
2. Re-evaluation of existing artifacts shows measurement improvement
3. RQ-4 becomes resolvable
4. Human authorization for C3 design

---

## 15. Change Control

### 15.1 EGER-CHANGE-005

| Field | Value |
|-------|-------|
| Identifier | EGER-CHANGE-005 |
| Reason | Measurement upgrade — enable FULL scope Oracle validation |
| Scope | Measurement infrastructure only |
| Affects | Oracle adapter, new metadata files |
| Does NOT affect | BENCH-002 tasks, MODEL-003/004, treatment, C0/C1/C2 artifacts, Ṛta |

### 15.2 Change Scope

```
INCLUDED:
  ✅ New directory: evaluator_context/ with design_metadata files
  ✅ Oracle adapter: accept optional design_metadata parameter
  ✅ Oracle scope logic: use metadata for port/clock validation
  ✅ Re-evaluation script: re-run Oracle on existing artifacts
  ✅ Unit tests: metadata loading, validation, scope determination

EXCLUDED:
  ❌ BENCH-002 task files (unchanged)
  ❌ evaluator_only files (unchanged)
  ❌ MODEL-003 or MODEL-004 (unchanged)
  ❌ Treatment definition (unchanged)
  ❌ C0/C1/C2 artifacts (preserved, re-evaluated not modified)
  ❌ Ṛta (unchanged)
  ❌ C3 (not authorized)
  ❌ Experiment protocol (unchanged — metadata is evaluator-side)
```

### 15.3 Authorization Sequence

```
P054 design ← YOU ARE HERE
    ↓
Human approval of P054 design
    ↓
EGER-CHANGE-005 formal change-control record
    ↓
Implementation (metadata files + Oracle adapter)
    ↓
Unit tests (95+ tests PASS)
    ↓
Re-evaluation of existing artifacts
    ↓
Scientific review of measurement improvement
    ↓
Decision: proceed to C3 or further improvement
```

---

## 16. Implementation Boundary

### 16.1 Required Changes

| File | Change | Risk |
|------|--------|------|
| `eger/oracle/adapter.py` | Add `design_metadata` parameter to `validate()` | LOW — additive |
| `eger/oracle/schemas.py` | Add `DesignMetadata` dataclass | LOW — new type |
| `research/experiments/EGER-BENCH-002/evaluator_context/*.json` | New metadata files | NONE — new files |
| `tests/test_evidence_oracle.py` | Add metadata-related tests | LOW — additive |

### 16.2 Prohibited Changes

| File | Why Prohibited |
|------|---------------|
| `research/experiments/EGER-BENCH-002/tasks/engineer_visible/*.json` | Benchmark preservation |
| `research/experiments/EGER-BENCH-002/evaluator_only/*.json` | Answer preservation |
| `eger/engineer/model.py` | Model unchanged |
| `eger/engineer/adapter.py` | Treatment unchanged |
| `eger/engineer/feedback.py` | Feedback unchanged |
| `eger/engineer/structured_feedback.py` | Feedback unchanged |
| `eger/epistemic/*` | Not active in C0-C2 |
| `eger/authorization/*` | Not active in C0-C2 |
| `research/experiments/EGER-MODEL-003.md` | Model identity unchanged |
| `research/experiments/EGER-MODEL-004.md` | Model identity unchanged |
| `rta-constraint-intelligence/*` | Oracle engine unchanged |

---

## 17. Validation Plan

### 17.1 Tests Required Before Re-Evaluation

| Test | Purpose | Expected |
|------|---------|----------|
| Metadata loading | Load design_metadata from JSON | PASS |
| Metadata validation | Validate metadata schema | PASS |
| Port reference check | get_ports X → X exists in metadata | PASS |
| Clock reference check | get_clocks X → X exists in metadata | PASS |
| Clock period check | create_clock period matches metadata | PASS |
| Direction check | set_input_delay on input port → PASS | PASS |
| Direction check | set_input_delay on output port → ERROR | PASS |
| Scope determination | Metadata available → FULL scope | PASS |
| Scope determination | No metadata → INSUFFICIENT scope (backward compat) | PASS |
| Determinism | Same SDC + same metadata → same EvidenceArtifact | PASS |
| Historical compatibility | Existing Oracle tests still PASS | PASS |
| No benchmark mutation | BENCH-002 task files unchanged | PASS |
| No model mutation | MODEL-003/004 files unchanged | PASS |
| No treatment mutation | feedback.py / structured_feedback.py unchanged | PASS |
| No Ṛta interaction | rta_generate never called | PASS |

### 17.2 Regression

All existing tests (95/95) must continue to PASS. The metadata parameter is optional, so backward compatibility is preserved.

---

## 18. Scientific Success Criteria

### 18.1 Measurement Upgrade Success

The upgrade is successful if:

| Criterion | Required |
|-----------|----------|
| Oracle can validate port references with metadata | ✅ YES |
| Oracle can validate clock references with metadata | ✅ YES |
| Oracle scope improves from INSUFFICIENT to FULL/PARTIAL | ✅ YES |
| No evaluator-only leakage to model | ✅ YES |
| Historical artifacts re-evaluable | ✅ YES |
| All existing tests PASS | ✅ YES |
| Backward compatibility preserved | ✅ YES |

### 18.2 What Success Does NOT Mean

| Claim | NOT Success Criterion |
|-------|----------------------|
| "C2 looks better" | ❌ — measurement improvement must be independent of treatment |
| "C0/C1/C2 comparison improves" | ⚠️ — this is a consequence, not the success criterion |
| "Correctness is established" | ❌ — that requires the actual re-evaluation |
| "C3 is justified" | ❌ — that's a separate decision |

---

## 19. Decision Matrix

| Option | Scientific Value | Implementation Cost | Leakage Risk | Causal Validity | **Recommended** |
|--------|-----------------|--------------------|--------------|-----------------|----|
| A. Oracle-only evaluator-side metadata | HIGH | LOW | LOW | HIGH | **✅ YES** |
| B. Engineer-visible metadata | HIGH | LOW | MEDIUM | LOW | ❌ NO — confound |
| C. New benchmark version | MEDIUM | MEDIUM | LOW | HIGH | ❌ NO — unnecessary |
| D. Independent correctness oracle | VERY HIGH | HIGH | LOW | HIGH | ❌ NO — too complex |
| E. Other approach | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | ❌ NO — A is sufficient |

**Recommendation: Option A — Oracle-only evaluator-side metadata**

This is the smallest change that maximizes causal validity.

---

## 20. Required Artifact

This document:
```
research/implementation/EGER-P054-MEASUREMENT-UPGRADE-SPECIFICATION-001.md
```

---

## 21. Strict Stop

After P054:

STOP.

Do NOT:
- modify benchmark
- modify Oracle
- modify model
- execute anything
- re-evaluate artifacts
- execute C3
- modify Ṛta
- commit
- push

P054 is DESIGN ONLY.

The next stage must be explicit human authorization followed by implementation/readiness verification.

END.
