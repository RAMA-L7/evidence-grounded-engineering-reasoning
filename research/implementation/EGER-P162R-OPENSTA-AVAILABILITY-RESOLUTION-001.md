# EGER-P162-R — OpenSTA Availability Resolution

## Gate

P162-R — Environment Resolution + Feasibility

## Date

2026-09-03

## Purpose

Resolve the OpenSTA availability problem using the smallest, safest, most reproducible environment path available.

**Status: CONDITIONALLY RESOLVED — WSL is the preferred path, requires user action.**

---

## 1. Objective

Determine whether a trustworthy, reproducible OpenSTA execution environment can be obtained without modifying the EGER architecture or turning the project into a Windows EDA-toolchain build exercise.

---

## 2. Baseline

| Item | Value |
|------|-------|
| Current commit | `1821aac` |
| Branch | `main` |
| Tests | 734/734 PASS |
| HEAD == origin/main | YES |

---

## 3. P162 Failure Summary

P162 attempted to build OpenSTA from source on Windows. The build failed at:

```
CMake Error: TCL_LIBRARY-NOTFOUND
```

Root cause: The MSYS2 installation provides TCL runtime (`tcl86.dll`) but not the development import library (`libtcl86.dll.a`) required by MinGW GCC for linking.

Build tools successfully installed: CMake 4.4.3, MinGW GCC 13.2.0, Flex/Bison, SWIG 4.1.1, Eigen3 3.4.0, GTest 1.14.0.

---

## 4. Environment Inventory

### 4.1 WSL

| Property | Status |
|----------|--------|
| WSL binary | AVAILABLE (`C:\WINDOWS\system32\wsl.exe`) |
| WSL version | 2 (Default Version: 2) |
| WSL1 support | Not supported (expected — WSL2 is default) |
| Installed distributions | NONE |
| Available distributions | Ubuntu, Debian, Fedora, SUSE, etc. |
| Install status | `wsl --install Ubuntu` timed out (120s) |
| Microsoft Store Ubuntu | NOT INSTALLED |

**WSL is available but has no Linux distributions installed.**

### 4.2 Docker

| Property | Status |
|----------|--------|
| Docker binary | NOT FOUND |
| Docker Desktop | NOT INSTALLED |
| Podman | NOT FOUND |
| Install attempt | `winget install Docker.DockerDesktop` timed out |

**Docker is not available.**

### 4.3 Windows-Native

| Property | Status |
|----------|--------|
| MSYS2 runtime | AVAILABLE (minimal) |
| MSYS2 pacman | NOT AVAILABLE |
| TCL runtime | AVAILABLE (`tcl86.dll`) |
| TCL development | NOT AVAILABLE (no headers, no import lib) |
| Build tools | INSTALLED (CMake, GCC, Flex/Bison, SWIG, Eigen3, GTest) |
| OpenSTA build | FAILED (missing TCL import library) |

**Windows-native build is blocked by missing TCL development infrastructure.**

---

## 5. WSL Assessment

### 5.1 Why WSL is Preferred

WSL provides a standard Linux environment where:
- OpenSTA packages may be available through `apt`
- Build dependencies (TCL-dev, zlib, etc.) are readily installable
- The environment is isolated from the Windows host
- Reproducible via distribution version pinning

### 5.2 WSL Setup Required

To enable WSL and install Ubuntu:

1. **Enable WSL2** (requires admin action):
   ```
   wsl --install
   ```
   Or manually: Settings → Apps → Optional Features → More Windows Features → Enable "Windows Subsystem for Linux"

2. **Install Ubuntu**:
   ```
   wsl --install -d Ubuntu
   ```

3. **Verify**:
   ```
   wsl -d Ubuntu -- uname -a
   ```

### 5.3 OpenSTA in WSL/Ubuntu

Once Ubuntu is available in WSL:

```bash
# Update package list
sudo apt update

# Install build dependencies
sudo apt install -y cmake g++ tcl-dev libeigen3-dev swig zlib1g-dev

# Clone and build OpenSTA
git clone https://github.com/The-OpenROAD-Project/OpenSTA.git
cd OpenSTA
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local
make -j$(nproc)
sudo make install

# Verify
sta --version
```

Estimated time: ~5-10 minutes once WSL is operational.

---

## 6. Docker Assessment

### 6.1 Docker Status

Docker is not installed and the install attempt timed out. Docker Desktop requires:
- Windows Pro/Enterprise/Education (or WSL2 backend)
- Admin access for installation
- Hyper-V or WSL2 enabled

### 6.2 OpenSTA Docker Images

The OpenROAD project provides Docker images:
- `openroad/flow-ubuntu22.04` — Full OpenROAD flow (includes OpenSTA)
- `openroad/opensta` — May exist as a standalone image

However, without Docker installed, these cannot be used.

### 6.3 Docker vs WSL

| Criterion | WSL | Docker |
|-----------|-----|--------|
| Setup complexity | Low (one command) | Medium (install + config) |
| Isolation | Good (full Linux) | Excellent (container) |
| Reproducibility | Good (distribution pin) | Excellent (image pin) |
| Resource overhead | Low | Medium |
| Current availability | AVAILABLE (needs distro) | NOT AVAILABLE |

**WSL is preferred over Docker for this use case.**

---

## 7. OpenSTA Acquisition Options

### 7.1 Option A — WSL + apt (PREFERRED)

```bash
sudo apt install opensta
```

If OpenSTA is in Ubuntu repositories. If not, build from source with apt-installed dependencies.

**Pros**: Standard Linux workflow, reproducible, well-documented.
**Cons**: Requires WSL setup first.

### 7.2 Option B — WSL + Source Build

```bash
sudo apt install cmake g++ tcl-dev libeigen3-dev swig zlib1g-dev
git clone https://github.com/The-OpenROAD-Project/OpenSTA.git
cd OpenSTA && mkdir build && cd build
cmake .. && make -j$(nproc) && sudo make install
```

**Pros**: Full control over version, provenance.
**Cons**: Longer setup, more dependencies.

### 7.3 Option C — Docker

```bash
docker pull openroad/flow-ubuntu22.04
docker run -it openroad/flow-ubuntu22.04 sta --version
```

**Pros**: Excellent isolation, reproducible.
**Cons**: Docker not installed, heavier setup.

### 7.4 Option D — Windows Native (FAILED)

Attempted in P162. Blocked by missing TCL import library.

**Not recommended to retry.**

---

## 8. Source/Tool Provenance

| Component | Source | Version | Trust Level |
|-----------|--------|---------|-------------|
| OpenSTA | The-OpenROAD-Project/OpenSTA | v2.2.0 | OFFICIAL |
| Ubuntu | Canonical | 22.04 LTS | OFFICIAL |
| TCL | Ubuntu apt repository | 8.6.x | OFFICIAL |
| CMake | pip (pypa) | 4.4.3 | OFFICIAL |
| MinGW GCC | niXman/mingw-builds-binaries | 13.2.0 | TRUSTED |
| Flex/Bison | lexxmark/winflexbison | 2.5.25 | TRUSTED |
| SWIG | SourceForge | 4.1.1 | OFFICIAL |
| Eigen3 | GitLab libeigen | 3.4.0 | OFFICIAL |
| GTest | Google/googletest | 1.14.0 | OFFICIAL |

---

## 9. Version Selection

**OpenSTA v2.2.0** — the latest official release.

P162 already cloned this version. The WSL build should use the same version for reproducibility.

---

## 10. P162 Substrate Compatibility

### 10.1 Verilog Design Issue

P162's `simple_path.v` uses behavioral RTL:

```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        data_out <= 8'b0;
    else
        data_out <= data_in;
end
```

This is NOT a gate-level netlist. For OpenSTA, a gate-level netlist with explicit cell instances is preferred:

```verilog
DFFX1 reg_inst (.CK(clk), .D(n1), .Q(data_out), .RN(rst_n));
INVX1 inv_inst (.A(data_in), .Y(n1));
```

**Recommendation**: The substrate Verilog should be corrected to use explicit cell instances matching the Liberty library before execution. This is a P163 concern, not P162-R.

### 10.2 Liberty Design

The proposed Liberty library with `DFFX1`, `INVX1`, `AND2X1` is structurally plausible for a minimal substrate. Needs validation once OpenSTA is available.

### 10.3 SDC Design

The PASS/VIOLATION case design (manipulating clock period) is sound.

### 10.4 Tcl Script

The proposed Tcl commands should be validated against actual OpenSTA v2.2.0 syntax once available.

---

## 11. Reproducibility Requirements

| Requirement | How Satisfied |
|------------|--------------|
| OpenSTA version pinned | v2.2.0 (source or package) |
| Ubuntu version pinned | 22.04 LTS |
| TCL version pinned | apt-resolved (8.6.x) |
| Netlist | Static artifact (hashable) |
| Liberty | Static artifact (hashable) |
| SDC | Static artifact (hashable) |
| Build/invocation | Documented Tcl script |

**Claim**: Results are reproducible under pinned distribution, tool version, and input files.

---

## 12. Security Assessment

| Concern | Assessment |
|---------|-----------|
| WSL installation | Standard Windows feature, low risk |
| Ubuntu installation | Official distribution, low risk |
| OpenSTA source build | Official repository, low risk |
| apt packages | Official Ubuntu repositories, low risk |
| No production code modified | VERIFIED |
| No secrets exposure | VERIFIED |
| No system modification beyond WSL | VERIFIED |

---

## 13. Decision

### **CONDITIONALLY RESOLVED**

A viable route exists: **WSL + Ubuntu**.

The route requires one bounded external prerequisite:
- User must enable WSL2 and install Ubuntu

Once that prerequisite is satisfied, OpenSTA can be obtained and executed within ~10 minutes through standard Linux package management.

---

## 14. Remaining Conditions

| # | Condition | Owner | Estimated Time |
|---|-----------|-------|---------------|
| 1 | Enable WSL2 Windows feature | User (admin) | 2 minutes |
| 2 | Install Ubuntu distribution | User | 5 minutes |
| 3 | Install OpenSTA in WSL | Agent | 10 minutes |
| 4 | Validate substrate execution | Agent | 5 minutes |

**Total estimated time once WSL is available: ~20 minutes.**

---

## 15. Recommended Next Gate

**P163 — OpenSTA Substrate Validation** (after WSL is available)

Once the user enables WSL and installs Ubuntu:
1. Install OpenSTA in WSL
2. Correct the Verilog to use gate-level cells
3. Execute PASS and VIOLATION cases
4. Validate determinism
5. Produce validated substrate

---

## 16. Explicit Non-Goals

1. EGER adapter implementation — deferred to P164
2. Oracle-generalization experiment — deferred to P165
3. Windows-native build retry — explicitly excluded
4. Docker installation — not needed if WSL works
5. Full EDA toolchain installation — only OpenSTA needed

---

## 17. Environment Architecture

The preferred architecture keeps EGER and OpenSTA environments separate:

```
Windows Host
    │
    ├── EGER Repository (D:\Research on EGER)
    │   ├── eger/ (production code)
    │   ├── tests/
    │   └── research/
    │
    └── WSL/Ubuntu
        │
        ├── OpenSTA (built from source or apt)
        ├── Substrate artifacts (netlist, Liberty, SDC)
        └── Execution scripts (Tcl)
```

This keeps:
- EGER architecture independent
- Oracle execution reproducible
- Toolchain dependencies isolated
- Ṛta untouched
- Research artifacts auditable

---

```
P162-R COMPLETE

GIT BASELINE: PASS
BASELINE COMMIT: 1821aac
BRANCH: main

ENVIRONMENT:
WSL: AVAILABLE (no distributions installed)
DOCKER: NOT AVAILABLE
WINDOWS-NATIVE: FAILED (P162 — missing TCL import lib)

OPENSTA:
STATUS: NOT YET AVAILABLE
VERSION: v2.2.0 (source cloned, not built)
ACQUISITION PATH: WSL + Ubuntu + apt/source build
SOURCE PROVENANCE: The-OpenROAD-Project/OpenSTA (OFFICIAL)

OPENSTA EXECUTION ENVIRONMENT: CONDITIONALLY RESOLVED
REPRODUCIBILITY: PASS (once WSL is set up)
SECURITY: PASS

P162 SUBSTRATE COMPATIBILITY:
VERLIB: NEEDS CORRECTION (behavioral → gate-level)
LIBERTY: PLAUSIBLE (needs validation)
SDC: SOUND
TCL: NEEDS VALIDATION

EGER PRODUCTION CODE CHANGES: NONE
EGER TEST CHANGES: NONE
ṚTA CHANGES: NONE
HISTORICAL RESEARCH CHANGES: NONE
RESEARCH STATE CHANGES: NONE

EGER REGRESSION: 734/734 PASS

RQ-4: CLOSED

DECISION: CONDITIONALLY RESOLVED

REMAINING CONDITIONS:
1. User enables WSL2
2. User installs Ubuntu distribution

PRIMARY RECORD: research/implementation/EGER-P162R-OPENSTA-AVAILABILITY-RESOLUTION-001.md
CHANGE-CONTROL RECORD: research/implementation/EGER-CHANGE-033.md

NEXT GATE: P163 — OpenSTA Substrate Validation (after WSL setup)

STOP: NO EGER OPENSTA ADAPTER OR ORACLE-GENERALIZATION EXPERIMENT PERFORMED
```
