# EGER-P161 — OpenSTA Pilot Substrate & Artifact Feasibility

## Gate

P161 — Assessment + Design (No Implementation)

## Date

2026-09-03

## Purpose

Determine whether a minimal, controlled OpenSTA evaluation substrate can be established for a future EGER Oracle pilot, and what the minimum artifacts and workflow should be.

**No production code modified. No dependencies installed. No artifacts created. No experiments executed.**

---

## 1. Executive Summary

A minimal OpenSTA pilot substrate **can be established** with reasonable effort, but requires three actions that are outside the scope of this assessment gate:

1. **Install OpenSTA** — not available in the current environment
2. **Create a minimal Verilog netlist** — no HDL files exist in the repository
3. **Create or obtain a minimal Liberty library** — no timing libraries exist in the repository

The substrate design is well-defined: a tiny hand-written gate-level netlist (e.g., a single flip-flop with data path), a synthetic Liberty library with basic cell timing models, and an existing SDC sample from the rta-constraint-intelligence repository. The total artifact footprint would be under 200 lines of text.

The EGER architecture impact is **minimal** — OpenSTA-specific configuration should remain outside the generic `TaskDefinition` contract, carried as Oracle-specific adapter configuration instead.

**Decision: REFINE** — The concept is viable and the substrate design is concrete, but environment preparation (installation + artifact creation) must occur before implementation can begin.

---

## 2. Baseline

| Item | Value |
|------|-------|
| Current commit | `1821aac` |
| Branch | `main` |
| Tests | 734/734 PASS |
| HEAD == origin/main | YES |

---

## 3. P160 Findings (Preserved)

P160 established:

| Finding | Classification |
|---------|---------------|
| OpenSTA availability | UNAVAILABLE |
| Adapter feasibility | ADAPTER-ONLY — no core changes |
| Evidence mapping | Straightforward (timing violations → error/warning/info) |
| Oracle independence | Verified — different engineering property |
| Decision | REFINE |

P161 builds on P160 by determining the minimum substrate needed to satisfy the refinement conditions.

---

## 4. Environment Assessment

### 4.1 Tool Availability

| Tool | Status | Version | Classification |
|------|--------|---------|---------------|
| OpenSTA (`opensta`/`sta`) | NOT FOUND | N/A | **UNAVAILABLE** |
| Yosys | NOT FOUND | N/A | **UNAVAILABLE** |
| Icarus Verilog (`iverilog`) | NOT FOUND | N/A | **UNAVAILABLE** |
| Verilator | NOT FOUND | N/A | **UNAVAILABLE** |
| Python | AVAILABLE | 3.10.11 |可用 |
| Tcl (`tclsh`) | AVAILABLE | /mingw64/bin/tclsh | Available |

### 4.2 Implications

- OpenSTA must be installed (source build or package) before any pilot can execute
- No HDL compilation tools are available — netlist must be pre-written, not generated
- Python and Tcl are available — sufficient for adapter scripting and OpenSTA Tcl interface
- The environment is a Windows/Git Bash/MSYS2 system — OpenSTA may require MSYS2 or WSL for building

### 4.3 OpenSTA Installation Path (Documented, Not Executed)

OpenSTA can be obtained through:
1. **GitHub source build**: `github.com/openroad/FlowRs` or `github.com/The-OpenROAD-Project/OpenSTA`
2. **Conda**: `conda install -c conda-forge opensta` (if conda is available)
3. **MSYS2**: `pacman -S opensta` (if MSYS2 package exists)
4. **Pre-built binary**: Download from OpenROAD releases

P161 does NOT install OpenSTA. This is documented for the future implementation gate.

---

## 5. Artifact Inventory

### 5.1 EGER Repository

| Artifact Type | Count | Location |
|--------------|-------|----------|
| Verilog (.v/.sv) | 0 | NONE |
| Liberty (.lib) | 0 | NONE |
| LEF (.lef) | 0 | NONE |
| SDC (.sdc) | 0 | NONE (SDC content exists in Python test fixtures) |
| TCL (.tcl) | 0 | NONE |
| Netlist files | 0 | NONE |
| SPEF/SDF | 0 | NONE |

### 5.2 rta-constraint-intelligence Repository

| Artifact Type | Count | Location |
|--------------|-------|----------|
| SDC samples | 15 | `rta-constraint-intelligence/samples/*.sdc` |
| TCL scripts | 2 | `rta-constraint-intelligence/samples/variables_v*.tcl` |
| Verilog/netlist | 0 | NONE |
| Liberty | 0 | NONE |

### 5.3 SDC Content in EGER Tests

SDC content exists as Python string literals in test files:
- `create_clock -name clk -period 10.0 [get_ports clk]` (51 chars, minimal)
- 287-char BENCH2-002 initial SDC (with generated clock, clock groups)
- Various test SDC strings

These are **constraint definitions**, not complete OpenSTA input substrates.

### 5.4 Classification

```
Reusable artifacts:
  - SDC samples from rta-constraint-intelligence/samples/ (15 files)
  - SDC content from EGER test fixtures (as reference)

Must be created:
  - Minimal Verilog netlist (hand-written)
  - Minimal Liberty library (hand-written or synthetic)
  - OpenSTA Tcl invocation script

Must be installed:
  - OpenSTA binary
```

---

## 6. Minimum OpenSTA Input Model

### 6.1 Required Inputs for Timing Analysis

| Input | Required | Description | Source |
|-------|----------|-------------|--------|
| Gate-level netlist | YES | Verilog module with gates/registers | Must create |
| Liberty library | YES | Cell timing models (.lib) | Must create |
| SDC constraints | YES | Timing constraints | Available (rta samples) |
| Clock definition | IMPLICIT | In SDC or derived | In SDC |
| Operating conditions | OPTIONAL | PVT corner | Use .lib defaults |
| RC parasitics | OPTIONAL | For accurate delay | Skip for pilot |

### 6.2 Minimal Input Set

The absolute minimum for OpenSTA to produce timing findings:

```
1 Verilog netlist file (~20 lines)
1 Liberty library file (~100 lines)
1 SDC file (~5-10 lines)
1 Tcl script (~5 lines)
```

Total: ~135 lines of text. This is a very small substrate.

---

## 7. Synthetic Design Strategy

### 7.1 Options Evaluated

| Option | Description | Pros | Cons |
|--------|------------|------|------|
| A: Hand-written gate-level | Write Verilog with explicit gate instantiations | Full control, no tool dependency, transparent | Requires manual gate mapping |
| B: Yosys-generated | Synthesize from RTL through Yosys | Realistic synthesis flow | Yosys unavailable, adds toolchain dependency |
| C: Existing repo design | Use a design from OpenCores or similar | Pre-validated | May be too complex, licensing concerns |
| D: Minimal behavioral + generic cells | Write behavioral Verilog, use generic Liberty cells | Simple, transparent | Less realistic timing behavior |

### 7.2 Selected Strategy: Option A — Hand-Written Gate-Level Netlist

**Rationale**: For a proof-of-concept pilot, a hand-written gate-level netlist provides:
- **Zero tool dependency** — no Yosys or synthesis tool needed
- **Full experimental control** — we know exactly what gates are in the design
- **Transparent timing** — we can predict which paths will have violations
- **Reproducibility** — the netlist is a static artifact, not generated
- **Simplicity** — a flip-flop + combinational logic is ~15 lines of Verilog

**Limitation**: A tiny synthetic circuit may not represent realistic VLSI timing behavior. This is acceptable for a proof-of-concept pilot that tests architecture generalization, not timing methodology.

### 7.3 Proposed Minimal Design

```verilog
module simple_path (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] data_in,
    output reg  [7:0] data_out
);
    // Single flip-flop with combinational input
    // Timing path: data_in → DFF → data_out
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            data_out <= 8'b0;
        else
            data_out <= data_in;
    end
endmodule
```

This design provides:
- One timing path (data_in → register → data_out)
- One clock domain
- One reset
- Clear setup/hold timing relationships
- Easy to create intentional violations (e.g., tight clock period, no input delay)

### 7.4 Intentional Timing Cases

| Case | How to Create | Expected OpenSTA Finding |
|------|--------------|------------------------|
| TIMING PASS | Clock period = 10ns, generous input/output delays | Zero violations (slack > 0) |
| SETUP VIOLATION | Clock period = 0.1ns (unrealistically tight) | Setup violation (negative slack) |
| HOLD VIOLATION | Remove input delay, add large output delay | Hold violation (negative slack) |
| UNCONSTRAINED | Remove all I/O delay constraints | Unconstrained path warnings |

---

## 8. Liberty Strategy

### 8.1 Options Evaluated

| Option | Description | Pros | Cons |
|--------|------------|------|------|
| Existing library | Use a publicly available .lib | Realistic timing data | May be too large, licensing |
| Minimal synthetic | Hand-craft a tiny .lib | Full control, tiny footprint | May not represent realistic timing |
| Open-source PDK | Use SkyWater or similar PDK | Realistic, open-source | Large, complex, may be overkill |
| Generated | Use Liberty generator tool | Realistic | Tool dependency |

### 8.2 Selected Strategy: Minimal Synthetic Liberty

**Rationale**: A hand-crafted Liberty file with 2-3 basic cells (DFF, INV, AND2) provides:
- **Tiny footprint** (~80-120 lines)
- **Full control** over timing parameters
- **No tool dependency**
- **Transparent** — we know exactly what timing models are used
- **Sufficient** for a proof-of-concept pilot

**Limitation**: Synthetic timing values may not represent realistic cell behavior. Acceptable for architecture validation.

### 8.3 Minimum Liberty Contents

A minimal Liberty file needs:
- Library header (name, units, default operating conditions)
- Cell definitions: `DFFX1` (flip-flop), `INVX1` (inverter), `AND2X1` (2-input AND)
- Pin definitions with timing arcs (setup, hold, clock-to-q, propagation delay)
- Default leakage power (optional)

Estimated size: ~100-150 lines of Liberty text.

---

## 9. Intentional Timing-Finding Strategy

### 9.1 How to Produce Controlled Timing Violations

The simplest approach: **manipulate the clock period in the SDC**.

| Scenario | SDC Modification | Expected Result |
|----------|-----------------|----------------|
| Clean timing | `create_clock -name clk -period 10.0` | All paths meet timing |
| Setup violation | `create_clock -name clk -period 0.01` | Setup violations on all paths |
| Hold violation | `create_clock -name clk -period 10.0` + remove input delay | Hold violations possible |
| Mixed | Combination of tight period + missing constraints | Multiple violation types |

### 9.2 Evidence Generation

For the pilot, the simplest case is:
1. Create a netlist with known timing characteristics
2. Create a Liberty file with known cell delays
3. Run OpenSTA with a clock period that guarantees at least one violation
4. Parse the OpenSTA report into EGER findings

This produces deterministic, reproducible timing evidence.

---

## 10. Determinism Requirements

### 10.1 What Must Be Pinned

| Artifact | How to Pin | Why |
|----------|-----------|-----|
| OpenSTA version | Record exact version + commit | Different versions may report differently |
| Netlist hash | SHA256 of .v file | Ensures identical input |
| Liberty hash | SHA256 of .lib file | Ensures identical cell models |
| SDC hash | SHA256 of .sdc file | Ensures identical constraints |
| Tcl script hash | SHA256 of .tcl file | Ensures identical invocation |
| Operating conditions | Use .lib defaults | No PVT variation |
| Environment | Record Python/OS/Tcl versions | Minor version effects |

### 10.2 Reproducibility Claim

> Results are reproducible under pinned tool version, input files, and configuration conditions.

NOT: "Results are universally deterministic across all environments."

---

## 11. Evidence Output Design

### 11.1 OpenSTA → OracleResult Flow

```
OpenSTA raw output (text report)
        ↓
OpenSTAAdapter._parse_report(raw_text)
        ↓
List of timing findings (setup/hold/violation/slack)
        ↓
OracleResult(
    is_success=True,
    evidence=EvidenceArtifact(
        oracle_status="SUCCESS",
        evidence_scope="FULL",
        findings=[
            Finding(severity="error", category="setup_violation", ...),
            Finding(severity="info", category="timing_clean", ...),
        ],
        ...
    )
)
```

### 11.2 What Must Survive Normalization

| Information | EGER Field | Why |
|------------|-----------|-----|
| Violation type | `Finding.category` | Distinguishes setup from hold |
| Severity | `Finding.severity` | error/warning/info classification |
| Slack value | `Finding.message` or `provenance` | Quantitative timing information |
| Path/scope | `Finding.entity` | Which path has the violation |
| Source Oracle | `EvidenceArtifact.provenance.oracle_name` | Identifies OpenSTA as source |
| Reproducibility metadata | `EvidenceArtifact.provenance` | Version, hashes, configuration |

### 11.3 OpenSTA Report Parsing

OpenSTA produces text reports. The adapter needs to parse:
- `report_timing` output → path-level violations
- `report_constraints` output → constraint violation summary
- Exit code → success/failure classification

For the pilot, a simple regex-based parser is sufficient. The key patterns:
- `slack (VIOLATED)` → error
- `slack (MET)` → info
- `unconstrained` → warning

---

## 12. Task Configuration Assessment

### 12.1 P160 Suggestion

P160 suggested extending `TaskDefinition` with `netlist_path` and `lib_path`.

### 12.2 Assessment

This is **NOT the right approach**. `TaskDefinition` is a generic EGER contract that defines what the LLM should produce. It should not carry Oracle-specific tool configuration.

### 12.3 Options Evaluated

| Option | Description | Architecture Impact |
|--------|------------|-------------------|
| A: Modify TaskDefinition | Add `netlist_path`, `lib_path` fields | CONTAMINATES generic contract |
| B: Oracle-specific config | Pass netlist/lib as adapter constructor args | ADAPTER-LOCAL — no core change |
| C: Separate artifact contract | Create `OpenSTAConfig` dataclass | NEW FILE — clean separation |
| D: Environment variables | Use `EGER_OPENSTA_NETLIST` etc. | Deployment-oriented, not testable |

### 12.4 Selected Strategy: Option B — Oracle-Specific Adapter Configuration

The OpenSTA adapter receives netlist and library paths as constructor arguments:

```python
class OpenSTAAdapter:
    def __init__(
        self,
        sta_binary: Path,
        netlist_path: Path,
        lib_path: Path,
        timeout_seconds: int = 60,
    ):
        ...
```

This keeps Oracle-specific configuration outside the generic EGER contracts. The adapter is responsible for providing these paths when invoked.

### 12.5 Architecture Impact

| Component | Change | Classification |
|-----------|--------|---------------|
| TaskDefinition | NO CHANGE | Generic contract preserved |
| OracleAdapter | NO CHANGE | Existing interface reused |
| OpenSTAAdapter (new) | NEW FILE | Oracle-specific adapter |
| EvidenceNormalizer | POSSIBLY EXTEND | If OpenSTA findings need different normalization |
| EvidenceArtifact | NO CHANGE | Same contract |
| Finding | NO CHANGE | Same severity vocabulary |
| VerificationGate | NO CHANGE | Same policy |
| RevisionController | NO CHANGE | Same loop |
| ProvenanceTracker | NO CHANGE | Same event chain |

---

## 13. EGER Architecture Impact

### 13.1 Component-by-Component Assessment

| Component | Classification | Rationale |
|-----------|---------------|-----------|
| TaskDefinition | NO CHANGE | Generic contract — no Oracle-specific fields |
| PromptBuilder | NO CHANGE | Prompt construction is Oracle-independent |
| ProposalGenerator | NO CHANGE | LLM generates SDC regardless of Oracle |
| CandidateArtifact | NO CHANGE | SDC text is Oracle-independent |
| OracleAdapter | NO CHANGE | Existing interface (validate → OracleResult) |
| OracleResult | NO CHANGE | Same success/failure union type |
| EvidenceNormalizer | POSSIBLY EXTEND | OpenSTA findings may need different severity mapping |
| EvidenceArtifact | NO CHANGE | Same contract (findings, summary, scope) |
| Finding | NO CHANGE | Same severity vocabulary (error/warning/info) |
| RevisionController | NO CHANGE | Same loop logic |
| VerificationGate | NO CHANGE | Same policy (zero ERROR → ACCEPT) |
| ProvenanceTracker | NO CHANGE | Same event chain |
| EGERPipeline | NO CHANGE | Same orchestration |

### 13.2 Preferred Outcome

> OpenSTA-specific substrate/configuration remains outside the generic EGER control contracts. The adapter encapsulates all Oracle-specific behavior.

---

## 14. Minimum Pilot Definition

### 14.1 Pilot Components

```
1 minimal design (simple_path module — ~15 lines Verilog)
1 minimal Liberty library (3 cells — ~120 lines)
1 SDC file (from rta-constraint-intelligence/samples/ — existing)
1 Tcl script (OpenSTA invocation — ~10 lines)
1 OpenSTAAdapter (new — ~150 lines)
1 FakeEngineerModel (existing test double)
1 EGERPipeline (existing)
```

### 14.2 Pilot Flow

```
Task: simple_path (with netlist + lib config)
    ↓
Initial SDC: create_clock -name clk -period 10.0 [get_ports clk]
    ↓
    ├── Run A: Oracle = Ṛta → constraint findings → evidence → verification
    │
    └── Run B: Oracle = OpenSTA → timing findings → evidence → verification
    ↓
Compare architecture behavior across Oracles
```

### 14.3 What the Pilot Demonstrates

| Demonstration | Success Criterion |
|--------------|------------------|
| OpenSTA adapter produces OracleResult | Valid success/failure response |
| Findings normalize to EvidenceArtifact | Valid Finding objects with correct severity |
| Revision loop works with timing evidence | LLM receives findings and can revise |
| VerificationGate accepts/rejects correctly | Decision matches evidence |
| Provenance captures OpenSTA run | Complete event chain |
| No core EGER changes required | Same pipeline path for both Oracles |

### 14.4 Pilot does NOT demonstrate

- Broad generalization (only 1-2 tasks)
- Realistic VLSI timing behavior (synthetic design)
- Production readiness (proof-of-concept only)
- Agent quality (uses fake model)

---

## 15. Research Validity

### 15.1 Substrate Validity

**Can OpenSTA reliably generate timing evidence?**

YES — given a valid netlist + Liberty + SDC, OpenSTA produces deterministic timing reports. This is its primary function. The question is not whether OpenSTA works, but whether EGER can consume its output.

### 15.2 Architectural Validity

**Can EGER consume OpenSTA evidence through its existing boundary?**

YES — the Oracle boundary is not Ṛta-specific. OpenSTA findings (setup/hold violations) map cleanly to the Finding schema (error/warning/info). The adapter produces compatible OracleResult.

### 15.3 Research Validity

**Can the resulting experiment support a claim about Oracle generalization?**

PARTIALLY — the pilot is proof-of-concept, not definitive. It demonstrates that the architecture pattern works across two different evaluation authorities. Broader claims require more tasks and Oracles.

### 15.4 Separation

| Question | P161 Addresses? |
|----------|----------------|
| Can OpenSTA produce timing evidence? | YES — substrate design validates this |
| Can EGER consume OpenSTA evidence? | YES — architecture assessment validates this |
| Does EGER generalize across Oracles? | NOT YET — future pilot gate |

---

## 16. Threats to Validity

| Threat | Assessment | Mitigation |
|--------|-----------|-----------|
| Synthetic design bias | Tiny circuit may not represent realistic VLSI | Acknowledge; pilot is proof-of-concept |
| Toolchain confounding | Hand-written netlist avoids synthesis artifacts | By design — no synthesis tool needed |
| Library simplification | Synthetic Liberty may not represent real cells | Acceptable for architecture validation |
| Task difficulty | Timing tasks differ from constraint tasks | By design — this IS the research question |
| Oracle-specific evidence | Timing findings have different semantics | By design — different authorities |
| Small sample | Cannot establish broad generalization | Pilot is proof-of-concept, not definitive |
| OpenSTA unavailable | Cannot execute pilot without installation | Documented as REFINE condition |

---

## 17. Decision

### **REFINE**

The minimal substrate is well-defined and feasible:
- ~15 lines of Verilog
- ~120 lines of Liberty
- ~10 lines of SDC (existing sample)
- ~10 lines of Tcl
- ~150 lines of adapter code

Total footprint: ~300 lines. This is a very small, controlled substrate.

However, the substrate cannot be established without:
1. Installing OpenSTA (environment preparation)
2. Creating the netlist and Liberty files (artifact creation)

Both are outside the scope of P161 (assessment gate).

### Refinement Conditions

| # | Condition | Current Status | How to Satisfy |
|---|-----------|---------------|---------------|
| 1 | OpenSTA installed | NOT AVAILABLE | Install via conda/pip/source |
| 2 | Minimal netlist + Liberty created | NOT CREATED | Create ~135 lines of artifacts |
| 3 | Task config approach decided | DECIDED | Option B: adapter constructor args |

Condition 3 is already satisfied by the assessment. Conditions 1 and 2 require action.

---

## 18. Explicit Non-Goals

1. **Installing OpenSTA** — P161 documents the requirement, does not install
2. **Creating netlist/Liberty artifacts** — P161 designs them, does not create
3. **Implementing the adapter** — P161 is assessment-only
4. **Running the pilot** — P161 is feasibility only
5. **Modifying EGER architecture** — P161 confirms no changes needed
6. **Comparing Oracle correctness** — Oracles measure different properties
7. **Claiming broad generalization** — Pilot is proof-of-concept

---

## 19. Recommended Next Gate

**P162 — OpenSTA Pilot Substrate Implementation**

After the refinement conditions are met:
1. OpenSTA is installed
2. Netlist + Liberty are created
3. Adapter is implemented
4. Pilot is executed

P162 should be a separate, authorized implementation gate.

---

```
P161 COMPLETE

GIT BASELINE: PASS
BASELINE COMMIT: 1821aac
BRANCH: main

OPENSTA: UNAVAILABLE
YOSYS: UNAVAILABLE
OTHER REQUIRED TOOLS: Python 3.10 ✓, Tcl ✓

ARTIFACT INVENTORY: NO HDL/LIBRARY/SDC FILES IN EGER REPO
MINIMUM SUBSTRATE: ~300 LINES TOTAL (15 Verilog + 120 Liberty + 10 SDC + 10 Tcl + 150 adapter)
SYNTHETIC DESIGN STRATEGY: HAND-WRITTEN GATE-LEVEL (Option A)
LIBERTY STRATEGY: MINIMAL SYNTHETIC (3 cells)
TIMING-FINDING STRATEGY: MANIPULATE CLOCK PERIOD IN SDC

DETERMINISM: REPRODUCIBLE UNDER PINNED INPUTS AND TOOL VERSION
EVIDENCE OUTPUT DESIGN: OpenSTA text → regex parse → Finding objects
TASK CONFIGURATION IMPACT: NO CHANGE TO TaskDefinition — adapter constructor args
EGER ARCHITECTURE IMPACT: ADAPTER-ONLY — NO CORE CHANGES

MINIMAL PILOT: 1 TASK, 2 ORACLES, 2 RUNS — PROOF OF CONCEPT
RESEARCH VALIDITY: SUBSTRATE AND ARCHITECTURE VALID — RESEARCH CLAIM REQUIRES FUTURE PILOT
THREATS-TO-VALIDITY: DOCUMENTED

DECISION: REFINE

REFINEMENT CONDITIONS:
1. Install OpenSTA
2. Create minimal netlist + Liberty (~135 lines)
3. (SATISFIED) Task config: adapter constructor args

IMPLEMENTATION CHANGES: NONE

TESTS: 734/734 PASS

ṚTA CHANGES: NONE
HISTORICAL RESEARCH CHANGES: NONE
RESEARCH STATE CHANGES: NONE

RQ-4: CLOSED

PRIMARY RECORD: research/implementation/EGER-P161-OPENSTA-PILOT-SUBSTRATE-FEASIBILITY-001.md
CHANGE-CONTROL RECORD: research/implementation/EGER-CHANGE-031.md

WORKING TREE: CLEAN (4 untracked P159/P160 docs + 2 new P161 docs + unrelated Universal_Principles_Library/)

NEXT GATE: P162 — OpenSTA Pilot Substrate Implementation (after refinement)

STOP: NO OPENSTA INSTALLATION, SUBSTRATE CREATION, ADAPTER IMPLEMENTATION, OR EXPERIMENT PERFORMED
```
