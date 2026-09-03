# EGER-P160 — OpenSTA Oracle Feasibility & Adapter Design

## Gate

P160 — Feasibility + Architecture Design (No Implementation)

## Date

2026-09-03

## Purpose

Determine whether OpenSTA can serve as an independent deterministic Oracle through the existing EGER Oracle boundary without requiring a fundamental redesign of the EGER architecture. Define the smallest adapter design needed if feasible.

**No production code modified. No live model calls. No experiments. No historical artifacts changed.**

---

## 1. Executive Summary

OpenSTA is **not currently available** in the execution environment, and the repository contains **no Verilog netlists, Liberty files, or timing-analysis artifacts**. However, the EGER Oracle architecture is **cleanly abstracted** and can accommodate a new Oracle through adapter-only changes. The evidence mapping from OpenSTA timing findings to EGER's Finding schema is straightforward.

**Decision: REFINE** — OpenSTA is architecturally feasible, but three prerequisite conditions must be satisfied before adapter implementation:

1. OpenSTA must be installed or made available
2. Minimal synthetic netlist + Liberty library must be created for pilot tasks
3. Task configuration must be extended to carry netlist/library paths

The adapter itself requires only **ADAPTER-ONLY** changes — no core EGER architecture modification.

---

## 2. Baseline

| Item | Value |
|------|-------|
| Current commit | `1821aac` |
| Branch | `main` |
| Tests | 734/734 PASS |
| HEAD == origin/main | YES |

---

## 3. Current Oracle Architecture

### 3.1 The Oracle Boundary

```
EvidenceOracle.validate(sdc_text)
    ↓
OracleResult(is_success, evidence, raw_evidence, failure)
    ↓
EvidenceNormalizer.normalize(oracle_evidence)
    ↓
EvidenceArtifact(findings, summary, scope, status)
    ↓
RevisionController → VerificationGate
```

### 3.2 What an Oracle Must Satisfy

| Requirement | Current Contract | Source |
|-------------|-----------------|--------|
| Input | `sdc_text: str` (candidate SDC) | `EvidenceOracle.validate()` |
| Output | `OracleResult` (success with `EvidenceArtifact` or failure with `OracleFailure`) | `OracleResult` dataclass |
| Exit codes | 0/1 = SUCCESS, 2 = INVALID_REQUEST, 3 = ORACLE_FAILURE | `adapter.py` classification |
| Findings format | List of dicts with `severity`, `code`, `message`, `location`, `context` | `_normalize_findings()` |
| Evidence scope | `FULL`, `PARTIAL`, `INSUFFICIENT`, `UNSUPPORTED` | `SCOPE_MAP` |
| Oracle status | `SUCCESS`, `INVALID_REQUEST`, `ORACLE_FAILURE` | `ORACLE_STATUS_VALUES` |
| Provenance | `oracle_name`, `oracle_version`, `oracle_revision`, `input_hash`, `raw_hash`, `evidence_hash` | `EvidenceArtifact.provenance` |

### 3.3 Contract Analysis — Ṛta-Specific Assumptions

| Contract Element | Ṛta-Specific? | OpenSTA Compatible? |
|-----------------|---------------|-------------------|
| `sdc_text: str` input | NO — generic | YES — OpenSTA also takes SDC |
| `OracleResult` union type | NO — generic | YES — same success/failure pattern |
| `Finding.severity` (error/warning/info) | NO — generic vocabulary | YES — timing violations map cleanly |
| `Finding.category` (code) | NO — generic string | YES — use OpenSTA rule/path IDs |
| `Finding.message` | NO — generic string | YES — timing violation descriptions |
| `EvidenceArtifact.evidence_scope` | NO — generic enum | YES — FULL if timing analysis completes |
| `OracleResult.failure` | NO — generic | YES — same failure representation |
| `EvidenceArtifact.provenance` | NO — generic dict | YES — populate with OpenSTA identity |
| Exit code semantics (0/1/2/3) | Ṛta-specific | MUST DEFINE for OpenSTA |
| `_normalize_findings` format | Expects `errors`/`warnings`/`info` buckets | MUST MAP OpenSTA output to this format |
| `_normalize_scope` format | Expects `analysis_scope` dict | MUST DEFINE for OpenSTA |

**Conclusion**: The core EGER contracts are NOT Ṛta-specific. An OpenSTA adapter can produce compatible `OracleResult` without changing any existing contract.

---

## 4. OpenSTA Availability

### 4.1 Environment Assessment

| Check | Result |
|-------|--------|
| `which opensta` | NOT FOUND |
| `which sta` | NOT FOUND |
| `opensta --version` | NOT AVAILABLE |
| `sta --version` | NOT AVAILABLE |
| Repository-local OpenSTA | NOT FOUND |
| OpenSTA in PATH | NO |

### 4.2 OpenSTA References in Repository

OpenSTA is mentioned in:
- `rta-constraint-intelligence/rta/docs/company/STARTUP_BACKLOG.md` — competitive landscape
- `rta-constraint-intelligence/rta/docs/architecture/BLOCK_LEVEL_FEATURE_PLAN_2.md` — as an adjacent tool
- `EGER-P159-ORACLE-FIRST-VALIDATION-RESEARCH-DESIGN-001.md` — our own design doc

**OpenSTA is not installed, not bundled, and not referenced as a dependency.**

### 4.3 OpenSTA Characteristics (from authoritative documentation)

OpenSTA is:
- Open-source (BSD license)
- C++ based static timing analyzer
- CLI tool: `sta <script>` or `sta -exit <commands>`
- Reads: Verilog netlist + Liberty (.lib) + SDC
- Outputs: timing paths, slack, violations — text or JSON
- Deterministic: given same inputs, produces same output
- Available via: GitHub (openroad/FlowRs or similar), package managers, or source build

---

## 5. Required Inputs

### 5.1 OpenSTA Minimum Inputs for Timing Analysis

| Input | Required? | Description | Currently in Repository? |
|-------|----------|-------------|------------------------|
| Gate-level netlist (Verilog) | YES | Synthesized design | **NO** |
| Technology library (.lib) | YES | Cell timing models | **NO** |
| SDC constraints | YES | Timing constraints (the candidate) | YES (in tests/experiments) |
| Clock definition | IMPLICIT | In SDC or .lib | YES (in SDC) |
| Operating conditions | OPTIONAL | PVT corner | NO — use .lib defaults |
| RC parasitics (.spef/.sdf) | OPTIONAL | For accurate delay | NO — skip for pilot |

### 5.2 What Must Be Created for the Pilot

| Artifact | How to Create | Complexity |
|----------|--------------|-----------|
| Minimal Verilog netlist | Write by hand (simple comb/seq logic) | LOW |
| Minimal Liberty library | Use open-source .lib generator or hand-craft minimal | MEDIUM |
| Pilot SDC files | Already exist in test fixtures | NONE |

### 5.3 Minimal Pilot Netlist Example

A minimal pilot could use a simple design like:

```verilog
module simple_timer (
    input wire clk,
    input wire rst_n,
    input wire [7:0] data_in,
    output reg [7:0] data_out
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            data_out <= 8'b0;
        else
            data_out <= data_in;
    end
endmodule
```

This is sufficient to demonstrate:
- OpenSTA can parse the netlist
- OpenSTA can apply SDC constraints
- OpenSTA can report timing violations (setup/hold)
- EGER can normalize those violations into evidence

---

## 6. Existing Artifact Assessment

### 6.1 SDC Content in Repository

The repository contains SDC content in:
- Test fixtures: `create_clock -name clk -period 10.0 [get_ports clk]`
- Experiment scripts: BENCH2-001, BENCH2-002 initial candidates
- Task definitions: `initial_sdc` field in `TaskDefinition`

These are **constraint definitions** — exactly what OpenSTA consumes as input.

### 6.2 Verilog/Netlist Content

**NONE** in the repository. No `.v`, `.sv`, or netlist files exist.

### 6.3 Liberty Content

**NONE** in the repository. No `.lib` or `.lef` files exist.

### 6.3 Classification

```
SUITABLE EXISTING TASK: NO
SUITABLE WITH MINOR PREPARATION: NO
NO SUITABLE EXISTING TASK: YES — netlist + .lib must be created
```

---

## 7. OpenSTA Output Assessment

### 7.1 What OpenSTA Produces

OpenSTA can report:
- **Setup violations**: paths where data arrives too late
- **Hold violations**: paths where data arrives too early
- **Slack values**: timing margin (negative = violation)
- **Unconstrained paths**: paths without timing constraints
- **Clock relationships**: clock network analysis
- **Report timing**: detailed path analysis

### 7.2 Output Format

OpenSTA outputs text reports by default. With scripting, it can produce structured data:
- `report_timing` → text path reports
- `report_constraints` → constraint violation summary
- Tcl commands for programmatic access
- JSON output possible via OpenSTA extensions or post-processing

### 7.3 What Would Become Evidence

| OpenSTA Finding | EGER Severity | EGER Category | EGER Message |
|----------------|--------------|---------------|-------------|
| Setup violation (negative slack) | error | setup_violation | "Setup violation on path X: slack = -Y ns" |
| Hold violation (negative slack) | error | hold_violation | "Hold violation on path X: slack = -Y ns" |
| Unconstrained input | warning | unconstrained_input | "Input port X has no input delay constraint" |
| Unconstrained output | warning | unconstrained_output | "Output port X has no output delay constraint" |
| Clock not defined | error | missing_clock | "Clock X is not defined in SDC" |
| Clean path (positive slack) | info | timing_clean | "Path X meets timing: slack = Y ns" |

---

## 8. Evidence Mapping Design

### 8.1 OpenSTA → OracleResult

```
OpenSTA timing analysis
    ↓
OpenSTAAdapter.validate(sdc_text, netlist_path, lib_path)
    ↓
Parse OpenSTA output → structured findings
    ↓
OracleResult(
    is_success=True,
    evidence=EvidenceArtifact(
        oracle_status="SUCCESS",
        evidence_scope="FULL",
        findings=[...],
        ...
    )
)
```

### 8.2 Severity Mapping

| OpenSTA Condition | Finding Severity | Rationale |
|-------------------|-----------------|-----------|
| Setup timing violation (slack < 0) | `error` | Design does not meet timing — must be fixed |
| Hold timing violation (slack < 0) | `error` | Design does not meet timing — must be fixed |
| Unconstrained input port | `warning` | May be intentional, but should be reviewed |
| Unconstrained output port | `warning` | May be intentional, but should be reviewed |
| Missing clock definition | `error` | Timing analysis cannot proceed without clock |
| Clean path (slack >= 0) | `info` | Informational — timing is met |
| OpenSTA execution failure | N/A | `OracleFailure(kind="ORACLE_FAILURE")` |

### 8.3 Finding Category Mapping

| OpenSTA Concept | EGER Finding.category | EGER Finding.source |
|----------------|----------------------|-------------------|
| Setup violation path | `setup_violation` | `opensta/report_timing` |
| Hold violation path | `hold_violation` | `opensta/report_timing` |
| Unconstrained port | `unconstrained_port` | `opensta/report_constraints` |
| Clock analysis | `clock_analysis` | `opensta/report_clock` |
| General violation | `timing_violation` | `opensta/report_constraints` |

### 8.4 Evidence Scope Mapping

| OpenSTA Result | EGER evidence_scope | Rationale |
|---------------|--------------------|-----------| 
| Full timing analysis complete | `FULL` | All paths analyzed |
| Partial analysis (some paths skipped) | `PARTIAL` | Some paths not analyzed |
| Netlist missing/incomplete | `INSUFFICIENT` | Cannot analyze timing |
| OpenSTA execution failed | `UNSUPPORTED` | No evidence produced |

---

## 9. Authority Separation

### Future OpenSTA Authority Model

```
LLM
  ↓
Candidate (SDC text — proposal)

OpenSTAAdapter
  ↓
Evidence (timing findings)

EvidenceNormalizer
  ↓
Normalized EvidenceArtifact

VerificationGate
  ↓
Decision (ACCEPT/REJECT)
```

| Authority | Who | CANNOT |
|-----------|-----|--------|
| Proposal | LLM | Verify, authorize, modify evidence |
| Timing evidence | OpenSTA | Generate proposals, authorize |
| Normalization | EvidenceNormalizer | Invent findings, reinterpret Oracle truth |
| Revision | RevisionController | Generate proposals, verify, authorize |
| Decision | VerificationGate | Generate proposals, produce evidence |
| Recording | ProvenanceTracker | Authorize decisions |

**No component may silently acquire additional authority.** The OpenSTA adapter is evidence-only, just like the Ṛta adapter.

---

## 10. Determinism / Reproducibility

### OpenSTA Determinism Assessment

| Factor | Deterministic? | Control |
|--------|---------------|---------|
| Netlist parsing | YES | Same .v → same internal representation |
| Liberty reading | YES | Same .lib → same cell models |
| SDC application | YES | Same .sdc → same constraints |
| Timing analysis | YES | Same inputs → same slack/violations |
| Report generation | YES | Same analysis → same report |
| Version effects | MAYBE | Different OpenSTA versions may produce slightly different results |
| Operating conditions | YES | Same .lib corner → same results |
| Tool configuration | YES | Same Tcl commands → same analysis flow |

### Reproducibility Requirements

To make a pilot reproducible:

| Requirement | How to Satisfy |
|------------|---------------|
| Pin OpenSTA version | Record exact version + commit hash |
| Pin Liberty library | Include .lib in experiment artifacts |
| Pin netlist | Include .v in experiment artifacts |
| Pin SDC | Candidate SDC is already tracked |
| Record Tcl commands | Include exact OpenSTA script |
| Record environment | Python version, OS, library paths |

**Classification**: Reproducible under controlled inputs and tool configuration.

---

## 11. Oracle Independence

### Ṛta vs OpenSTA — Independent Evaluation Authorities

| Property | Ṛta | OpenSTA |
|----------|-----|---------|
| Evaluates | SDC constraint quality | Timing closure |
| Checks | Syntax, semantics, completeness | Setup/hold timing, slack |
| Authority type | Constraint-quality authority | Timing-analysis authority |
| Input | SDC text only | SDC + netlist + .lib |
| Output | Constraint findings | Timing violation findings |
| Independence | FUNDAMENTALLY DIFFERENT | Different engineering property |

**Critical invariant**: These are NOT competing correctness authorities. They evaluate different aspects of the same design. A design can have correct constraints (Ṛta PASS) but fail timing (OpenSTA FAIL), or vice versa.

The research question is whether the **architecture pattern** works across these different authorities — not whether they agree.

---

## 12. Adapter Feasibility

### Classification: ADAPTER-ONLY

The existing EGER architecture can accommodate OpenSTA through:

1. **New file**: `eger/oracle/opensta_adapter.py` — implements OpenSTA invocation and output parsing
2. **Extended config**: Add `netlist_path`, `lib_path` to task configuration (or use separate config)
3. **New normalizer or extended normalizer**: Map OpenSTA findings to Finding schema
4. **No changes to**: EvidenceArtifact, Finding, VerificationResult, VerificationGate, RevisionController, ProvenanceTracker, PromptBuilder, CandidateArtifact, EGERPipeline

### What Changes

| Component | Change | Scope |
|-----------|--------|-------|
| `eger/oracle/opensta_adapter.py` | NEW FILE | OpenSTA-specific adapter |
| `eger/oracle/__init__.py` | EXPORT | Export OpenSTAAdapter |
| Task configuration | EXTEND | Add netlist/lib paths |
| EvidenceNormalizer | POSSIBLY EXTEND | If OpenSTA findings need different normalization |

### What Does NOT Change

| Component | Why |
|-----------|-----|
| EvidenceArtifact | Same contract — findings, summary, scope |
| Finding | Same severity vocabulary (error/warning/info) |
| VerificationResult | Same contract |
| VerificationGate | Same policy (zero ERROR → ACCEPT) |
| RevisionController | Same loop logic |
| ProvenanceTracker | Same event chain |
| PromptBuilder | Same prompt construction |
| CandidateArtifact | Same contract |
| EGERPipeline | Same orchestration |

---

## 13. Minimal Pilot Design

### 13.1 Pilot Objective

> Can an independently developed deterministic timing Oracle participate in the same EGER evidence-grounded revision loop?

### 13.2 Pilot Scope

| Parameter | Value |
|-----------|-------|
| Tasks | 1 minimal task (simple timer) |
| Oracles | Ṛta (baseline) + OpenSTA (new) |
| Initial candidate | Same SDC for both Oracles |
| Agent | FakeEngineerModel (deterministic, no LLM needed for pilot) |
| Revisions | 1–2 iterations (proof of concept) |
| Total runs | 2 (one per Oracle) |

### 13.3 Pilot Flow

```
Task: simple_timer
    ↓
Initial SDC: create_clock -name clk -period 10.0 [get_ports clk]
    ↓
    ├── Oracle A (Ṛta) → constraint findings → evidence → revision → verification
    │
    └── Oracle B (OpenSTA) → timing findings → evidence → revision → verification
    ↓
Compare: architecture behavior across Oracles
```

### 13.4 What the Pilot Demonstrates

| Demonstration | Success Criterion |
|--------------|------------------|
| OpenSTA can be invoked through adapter | `OpenSTAAdapter.validate()` returns `OracleResult` |
| OpenSTA findings normalize to evidence | `EvidenceNormalizer` produces valid `EvidenceArtifact` |
| Revision loop works with OpenSTA evidence | LLM receives timing findings and revises |
| VerificationGate accepts/rejects correctly | Decision matches evidence (zero errors → ACCEPT) |
| Provenance captures OpenSTA run | Complete event chain reconstructable |
| No core EGER changes required | Same pipeline path for both Oracles |

---

## 14. Controlled Comparison

### Valid Comparisons

| Comparison | What It Shows |
|-----------|--------------|
| Same task, different Oracle | Architecture behavior across evaluation authorities |
| Same initial candidate, different Oracle | How different evidence affects revision |
| Same revision protocol, different Oracle | Whether revision loop generalizes |
| Same verification policy, different Oracle | Whether gate policy works across evidence types |

### Invalid Interpretations

| Invalid Claim | Why |
|--------------|-----|
| "OpenSTA proves EGER is better" | Not the research question |
| "OpenSTA performance = EGER performance" | Conflates Oracle and architecture |
| "所有情节 constraints are correct" | Different Oracles measure different things |
| "Architecture works for all Oracles" | Pilot uses only 2 Oracles |

---

## 15. Threats to Validity

| Threat | Assessment | Mitigation |
|--------|-----------|-----------|
| Task confounding | Timing tasks differ from constraint tasks | Acknowledge; pilot uses same task for both |
| Oracle-property confounding | Different Oracles measure different properties | By design — this IS the research question |
| Tool/environment confounding | Different toolchains introduce different failure modes | Pin versions, same environment |
| Agent adaptation | Prompting may need Oracle-specific terminology | Pilot uses fake model; no LLM adaptation needed |
| Evidence normalization | Differences may arise from normalization layer | Compare raw Oracle findings separately |
| Verification policy | Timing Oracle may need different acceptance semantics | Test with existing gate policy first |
| Small pilot size | Cannot establish broad generalization | Pilot is proof-of-concept, not definitive |
| OpenSTA unavailable | Cannot execute pilot without OpenSTA | Documented as REFINE condition |

---

## 16. GO / REFINE / NO-GO Decision

### **REFINE**

**Rationale:**

OpenSTA is architecturally feasible through ADAPTER-ONLY changes. The EGER Oracle boundary is cleanly abstracted and not Ṛta-specific. Evidence mapping is straightforward. However, three prerequisite conditions must be satisfied:

### Refinement Conditions

| # | Condition | Current Status | How to Satisfy |
|---|-----------|---------------|---------------|
| 1 | OpenSTA available in environment | NOT AVAILABLE | Install OpenSTA (source build or package) |
| 2 | Minimal netlist + Liberty library exist | NOT AVAILABLE | Create synthetic pilot artifacts |
| 3 | Task config extended for netlist/lib paths | NOT IMPLEMENTED | Extend TaskDefinition or use separate config |

### Why Not GO

- OpenSTA is not installed — adapter cannot be tested
- No netlist or .lib files exist — OpenSTA cannot be invoked
- Task configuration does not carry netlist/lib paths — adapter interface is undefined

### Why Not NO-GO

- The EGER Oracle boundary is NOT Ṛta-specific (verified from code)
- Evidence mapping is clean (timing violations → error/warning/info findings)
- Adapter-only changes are sufficient (no core architecture modification)
- OpenSTA is open-source and available for installation
- The scientific value of the pilot is clear

---

## 17. Explicit Non-Goals

1. **Installing OpenSTA** — P160 does not install anything
2. **Creating netlist/library artifacts** — P160 documents the requirement, does not create them
3. **Implementing the adapter** — P160 is design-only
4. **Running the pilot** — P160 is feasibility assessment only
5. **Modifying EGER architecture** — P160 confirms no changes needed
6. **Comparing Oracle correctness** — Oracles measure different properties
7. **Claiming broad generalization** — Pilot is proof-of-concept only

---

## 18. Recommended Next Gate

**P161 — OpenSTA Adapter Implementation** (after refinement conditions are met)

Before P161 can begin:
1. OpenSTA must be installed
2. Minimal netlist + .lib must be created
3. Task configuration extension must be designed

If the refinement conditions cannot be met, the next gate should reassess Oracle candidacy.

---

```
P160 COMPLETE

GIT BASELINE: PASS
BASELINE COMMIT: 1821aac
BRANCH: main

OPENSTA AVAILABILITY: UNAVAILABLE
OPENSTA VERSION: N/A

CURRENT ORACLE ARCHITECTURE: CLEAN — NOT Ṛta-SPECIFIC
INPUT ARTIFACT AVAILABILITY: SDC YES, NETLIST NO, LIB NO
OUTPUT EVIDENCE MAPPING: STRAIGHTFORWARD
DETERMINISM ASSESSMENT: REPRODUCIBLE UNDER CONTROLLED INPUTS
ORACLE INDEPENDENCE: VERIFIED — DIFFERENT ENGINEERING PROPERTY
ADAPTER FEASIBILITY: ADAPTER-ONLY — NO CORE CHANGES

MINIMAL PILOT: DESIGNED — 1 TASK, 2 ORACLES, 2 RUNS
THREATS-TO-VALIDITY: DOCUMENTED

DECISION: REFINE

REFINEMENT CONDITIONS:
1. Install OpenSTA
2. Create minimal netlist + Liberty library
3. Extend task configuration

IMPLEMENTATION CHANGES: NONE

TESTS: 734/734 PASS

ṚTA CHANGES: NONE
HISTORICAL RESEARCH CHANGES: NONE
RESEARCH STATE CHANGES: NONE

RQ-4: CLOSED

PRIMARY RECORD: research/implementation/EGER-P160-OPENSTA-FEASIBILITY-ADAPTER-DESIGN-001.md
CHANGE-CONTROL RECORD: research/implementation/EGER-CHANGE-030.md

WORKING TREE: CLEAN (2 new P160 docs + 2 untracked P159 docs + unrelated Universal_Principles_Library/)

NEXT GATE: P161 — OpenSTA Adapter Implementation (after refinement)

STOP: NO OPENSTA IMPLEMENTATION OR EXPERIMENT PERFORMED
```
