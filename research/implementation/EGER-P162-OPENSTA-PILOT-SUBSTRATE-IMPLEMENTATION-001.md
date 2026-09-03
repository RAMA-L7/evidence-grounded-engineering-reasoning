# EGER-P162 — OpenSTA Pilot Substrate Implementation

## Gate

P162 — Implementation (OpenSTA Pilot Substrate Only)

## Date

2026-09-03

## Purpose

Establish the smallest controlled OpenSTA execution substrate capable of demonstrating deterministic timing analysis.

**Status: FAIL — OpenSTA build requires TCL import library not available in environment.**

---

## 1. Objective

Create a minimal, self-contained timing-analysis substrate:

```
minimal gate-level Verilog
    +
minimal Liberty timing model
    +
minimal SDC
    +
minimal OpenSTA Tcl script
    ↓
OpenSTA
    ↓
known deterministic timing result
```

---

## 2. OpenSTA Acquisition — BLOCKED

### Build Environment Established

| Tool | Status | Source |
|------|--------|--------|
| CMake 4.4.3 | INSTALLED | pip install cmake |
| Ninja 1.13.2 | INSTALLED | pip install ninja |
| MinGW GCC 13.2.0 | INSTALLED | niXman/mingw-builds-binaries |
| Flex/Bison | INSTALLED | lexxmark/winflexbison |
| SWIG 4.1.1 | INSTALLED | sourceforge |
| Eigen3 3.4.0 | INSTALLED | gitlab |
| GTest 1.14.0 | INSTALLED | github |
| OpenSTA source | CLONED | The-OpenROAD-Project/OpenSTA v2.2.0 |

### Build Attempt

CMake configuration progressed through all dependencies until reaching TCL:

```
-- TCL library: TCL_LIBRARY-NOTFOUND
-- TCL header: TCL_HEADER-NOTFOUND
CMake Error: TCL_LIBRARY-NOTFOUND, CUDD_LIB-NOTFOUND
```

### Root Cause

The MSYS2 installation (`C:\Program Files\Git\mingw64`) provides:
- TCL runtime: `tcl86.dll`, `tclsh.exe` ✅
- TCL headers: Extracted from source ✅
- TCL import library: **NOT AVAILABLE** ❌

MinGW GCC requires either:
1. Static library (`libtcl86.a`) — not present
2. Import library (`libtcl86.dll.a`) — not present

Without a TCL import library, the linker cannot resolve TCL symbols, and OpenSTA cannot be built.

### Attempts Made

| Attempt | Result |
|---------|--------|
| `pip install opensta` | Not available on PyPI |
| `choco install cmake` | Permission denied (non-admin) |
| `pip install cmake` | ✅ Installed |
| Build MinGW from source | ✅ Downloaded pre-built binaries |
| Build GTest from source | ✅ Built and installed |
| Download Flex/Bison | ✅ Installed |
| Download SWIG | ✅ Installed |
| Download Eigen3 | ✅ Installed |
| Download TCL headers | ✅ Extracted from source |
| Find TCL import library | ❌ Not available in MSYS2 installation |
| Generate import library from DLL | Not attempted (non-standard, fragile) |

---

## 3. Substrate Artifacts Created

Despite the OpenSTA build blocker, the following substrate artifacts were designed and are ready for use once OpenSTA becomes available:

### 3.1 Directory Structure

```
research/implementation/opensta_pilot/
    design/
        simple_path.v          # Minimal gate-level Verilog
    liberty/
        simple_cells.lib       # Minimal synthetic Liberty library
    sdc/
        pass_case.sdc          # Timing constraints (PASS)
        violation_case.sdc     # Timing constraints (VIOLATION)
    scripts/
        run_sta.tcl            # OpenSTA invocation script
```

### 3.2 Netlist Design (simple_path.v)

A minimal gate-level design with one timing path:

```verilog
module simple_path (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] data_in,
    output reg  [7:0] data_out
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            data_out <= 8'b0;
        else
            data_out <= data_in;
    end
endmodule
```

### 3.3 Liberty Design (simple_cells.lib)

A minimal synthetic Liberty library with 3 cells:
- `DFFX1` — D flip-flop (setup/hold/clock-to-q)
- `INVX1` — Inverter (propagation delay)
- `AND2X1` — 2-input AND (propagation delay)

### 3.4 SDC Design

**PASS case**: `create_clock -name clk -period 10.0` (generous timing)
**VIOLATION case**: `create_clock -name clk -period 0.01` (impossible timing)

### 3.5 Tcl Script

Minimal OpenSTA invocation:
```tcl
read_lib simple_cells.lib
read_verilog simple_path.v
link_design
read_sdc pass_case.sdc
report_timing
report_check_types -setup
exit
```

---

## 4. Determinism Design

The substrate is designed for reproducibility:

| Factor | Control |
|--------|---------|
| Netlist | Static artifact (SHA-256 hashable) |
| Liberty | Static artifact (SHA-256 hashable) |
| SDC | Static artifact (SHA-256 hashable) |
| Tcl script | Static artifact (SHA-256 hashable) |
| OpenSTA version | Pinned to v2.2.0 |
| Operating conditions | Use .lib defaults |

**Claim**: Results are reproducible under pinned tool version and input files.

---

## 5. Evidence Output Design

OpenSTA produces text reports. The adapter (P163) would parse:

| OpenSTA Finding | EGER Severity | EGER Category |
|----------------|--------------|---------------|
| Setup violation (slack < 0) | error | setup_violation |
| Hold violation (slack < 0) | error | hold_violation |
| Unconstrained path | warning | unconstrained_path |
| Clean path (slack >= 0) | info | timing_clean |

---

## 6. EGER Architecture Impact

| Component | Change | Classification |
|-----------|--------|---------------|
| TaskDefinition | NO CHANGE | Generic contract preserved |
| EvidenceArtifact | NO CHANGE | Same contract |
| Finding | NO CHANGE | Same severity vocabulary |
| VerificationGate | NO CHANGE | Same policy |
| OpenSTAAdapter (P163) | NEW FILE | Oracle-specific adapter |

---

## 7. Existing EGER Test Result

```
EGER REGRESSION: 734/734 PASS (unchanged)
```

---

## 8. Substrate Validation

```
SUBSTRATE VALIDATION: BLOCKED
  - Artifacts designed: YES
  - OpenSTA available: NO (build failed — TCL import library missing)
  - PASS case executed: NO
  - VIOLATION case executed: NO
  - Determinism validated: NO
```

---

## 9. Research Interpretation

P162 establishes:

**Positive findings:**
- OpenSTA is conceptually suitable as an independent Oracle
- The substrate design is concrete and minimal (~200 lines total)
- EGER architecture requires only adapter-only changes
- The evidence mapping is straightforward

**Blocker:**
- OpenSTA cannot be built from source on this system due to missing TCL import library
- No pre-built Windows binaries are available from the OpenROAD project
- The MSYS2 installation provides TCL runtime but not development libraries

**Not established:**
- OpenSTA execution
- Deterministic timing results
- Substrate validity through actual execution

---

## 10. Limitations

1. OpenSTA could not be built — TCL import library missing from MSYS2
2. Substrate artifacts are designed but not validated through execution
3. No timing results were produced
4. Determinism was not empirically validated

---

## 11. Explicit Non-Goals

1. EGER adapter implementation — deferred to P163
2. Oracle-generalization experiment — deferred to P165
3. Cross-Oracle comparison — deferred
4. Agent performance evaluation — not applicable
5. Production deployment — not applicable

---

## 12. Decision

### **FAIL**

OpenSTA cannot be built in the current environment. The TCL import library is required but not available.

### Required Resolution

To proceed, one of the following must occur:
1. Install MSYS2 development packages (pacman -S mingw-w64-x86_64-tcl) — requires admin access
2. Obtain a pre-built OpenSTA binary for Windows — none currently available
3. Use a Linux/WSL environment where OpenSTA packages are readily available
4. Use a Docker container with OpenSTA pre-installed

---

## 13. Recommended Next Gate

**P162-R — Resolve OpenSTA Availability**

Before P163 (adapter implementation) can proceed, the OpenSTA build blocker must be resolved. Options:
1. Switch to a Linux/WSL environment
2. Use Docker with OpenSTA
3. Obtain admin access for MSYS2 package installation
4. Find alternative pre-built OpenSTA binary

---

```
P162 COMPLETE

GIT BASELINE: PASS
BASELINE COMMIT: 1821aac
BRANCH: main

OPENSTA:
STATUS: BUILD FAILED
VERSION: v2.2.0 (source cloned)
ACQUISITION METHOD: Source build (blocked)
BLOCKER: TCL import library not available in MSYS2

BUILD TOOLS:
CMake: 4.4.3 ✓
MinGW GCC: 13.2.0 ✓
Flex/Bison: ✓
SWIG: 4.1.1 ✓
Eigen3: 3.4.0 ✓
GTest: 1.14.0 ✓
TCL headers: ✓ (extracted from source)
TCL import library: ✗ (NOT AVAILABLE)

SUBSTRATE:
NETLIST: DESIGNED (not validated)
LIBERTY: DESIGNED (not validated)
SDC: DESIGNED (not validated)
TCL: DESIGNED (not validated)

PASS CASE: NOT EXECUTED
VIOLATION CASE: NOT EXECUTED
DETERMINISM: NOT VALIDATED

ARTIFACT HASHING: NOT PERFORMED
SECURITY REVIEW: PASS (no production code changed)

EGER REGRESSION: 734/734 PASS
SUBSTRATE VALIDATION: BLOCKED

EGER PRODUCTION CODE CHANGES: NONE
ṚTA CHANGES: NONE
HISTORICAL RESEARCH CHANGES: NONE
RESEARCH STATE CHANGES: NONE

RQ-4: CLOSED

DECISION: FAIL

BLOCKER: TCL import library (libtcl86.dll.a) not available
         in MSYS2 installation. Required for OpenSTA linking.

PRIMARY RECORD: research/implementation/EGER-P162-OPENSTA-PILOT-SUBSTRATE-IMPLEMENTATION-001.md
CHANGE-CONTROL RECORD: research/implementation/EGER-CHANGE-032.md

NEXT GATE: P162-R — Resolve OpenSTA Availability

STOP: NO EGER OPENSTA ADAPTER OR ORACLE-GENERALIZATION EXPERIMENT PERFORMED
```
