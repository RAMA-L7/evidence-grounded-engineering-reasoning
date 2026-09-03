# EGER-CHANGE-034 — OpenSTA Substrate Validation

## Change ID

EGER-CHANGE-034

## Date

2026-09-03

## Gate

P163 — OpenSTA Substrate Validation

## Summary

Substrate validation gate. Installed Ubuntu 24.04 in WSL2, built OpenSTA v2.2.0 from source, created explicit gate-level netlist with synthetic Liberty library, and validated deterministic PASS/VIOLATION timing outcomes. Both cases produce identical results across repeated runs. Manual timing cross-check confirms OpenSTA results.

---

## Baseline Commit

`1821aac` (P158 checkpoint)

## Environment

| Component | Value |
|-----------|-------|
| Host | Windows (Git Bash) |
| WSL | Ubuntu 24.04.4 LTS |
| WSL Kernel | 6.6.87.2-microsoft-standard-WSL2 |
| OpenSTA | v2.2.0 (built from source) |
| Build tools | CMake 3.28, GCC 13.3.0, TCL 8.6.14, SWIG 4.2.0 |

## OpenSTA Acquisition

Cloned from `The-OpenROAD-Project/OpenSTA` (v2.2.0 tag), built inside WSL2 with patched CMakeLists.txt (SWIG version constraint removed). All dependencies from official Ubuntu apt repositories.

## Substrate Artifacts

| Artifact | Status | Hash (SHA-256) |
|----------|--------|----------------|
| simple_path.v | Created (gate-level) | e03887f... |
| simple_cells.lib | Created (synthetic) | cfd8b3f... |
| pass_case.sdc | Created | 66430f9... |
| violation_case.sdc | Created | e215494... |
| run_pass.tcl | Created | 35b5fa1... |
| run_violation.tcl | Created | 8f280db... |

## Execution Results

| Case | WNS | TNS | Slack | Classification | Deterministic? |
|------|-----|-----|-------|---------------|---------------|
| PASS | 0.00 | 0.00 | 9.85 ns | MET | YES |
| VIOLATION | -0.10 | -0.10 | -0.10 ns | VIOLATED | YES |

## Manual Timing Cross-Check

PASS case: data arrival = 0.05 ns, data required = 9.9 ns, slack = 9.85 ns ✓
VIOLATION case: data arrival = 0.05 ns, data required = -0.05 ns, slack = -0.10 ns ✓

## EGER Code Impact

NONE — no EGER production code was modified.

## Ṛta Impact

NONE — Ṛta was not modified or compared.

## Historical Research Impact

NONE — no historical artifacts were modified.

## Research-State Impact

NONE — no research conclusions were changed. RQ-4 remains CLOSED.

## Decision

**PASS** — All substrate-validation success criteria satisfied.

## Next Gate

P164 — OpenSTA Adapter Design/Implementation

---

> P163 validates the external OpenSTA substrate only. No EGER Oracle adapter or Oracle-generalization experiment was implemented.
