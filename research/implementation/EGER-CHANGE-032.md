# EGER-CHANGE-032 — OpenSTA Pilot Substrate Attempt

## Change ID

EGER-CHANGE-032

## Date

2026-09-03

## Gate

P162 — Minimal OpenSTA Pilot Substrate Implementation

## Summary

Implementation gate for OpenSTA pilot substrate. Build tools were installed (CMake, MinGW GCC, Flex/Bison, SWIG, Eigen3, GTest), OpenSTA source was cloned, but the build failed due to missing TCL import library in the MSYS2 installation. Substrate artifacts were designed but not validated through execution.

---

## Baseline Commit

`1821aac` (P158 checkpoint)

## Tools Obtained/Used

| Tool | Version | Method |
|------|---------|--------|
| CMake | 4.4.3 | pip install cmake |
| Ninja | 1.13.2 | pip install ninja |
| MinGW GCC | 13.2.0 | niXman/mingw-builds-binaries |
| Flex/Bison | 2.5.25 | lexxmark/winflexbison |
| SWIG | 4.1.1 | sourceforge |
| Eigen3 | 3.4.0 | gitlab |
| GTest | 1.14.0 | github (built from source) |
| OpenSTA | v2.2.0 | github (cloned, NOT built) |
| py7zr | latest | pip install |
| TCL headers | 8.6.14 | tcl.sourceforge.net (extracted) |

## Build Attempt

OpenSTA CMake configuration completed through all dependencies except TCL:
- CMake: ✅
- Flex/Bison: ✅
- SWIG: ✅
- Eigen3: ✅
- GTest: ✅
- TCL headers: ✅ (extracted from source)
- TCL import library: ❌ NOT AVAILABLE

## Blocker

```
CMake Error: TCL_LIBRARY-NOTFOUND
```

The MSYS2 installation provides TCL runtime (tcl86.dll, tclsh.exe) but not the development import library (libtcl86.dll.a) required by MinGW GCC for linking.

## Artifacts Created

| Artifact | Status |
|----------|--------|
| simple_path.v | Designed |
| simple_cells.lib | Designed |
| pass_case.sdc | Designed |
| violation_case.sdc | Designed |
| run_sta.tcl | Designed |
| P162 implementation record | Created |
| CHANGE-032 | Created |

## Tests

EGER regression: 734/734 PASS (unchanged)
Substrate validation: BLOCKED (OpenSTA not available)

## Security Review

No production code changed. Build tools are from trusted sources (pip, GitHub, SourceForge).

## EGER Architecture Impact

NONE — no EGER production code was modified.

## Ṛta Impact

NONE — Ṛta was not modified.

## Historical Research Impact

NONE — no historical artifacts were modified.

## Research-State Impact

NONE — no research conclusions were changed.

## Next Gate

P162-R — Resolve OpenSTA Availability (switch environment or obtain admin access)

---

> P162 establishes only the OpenSTA pilot substrate attempt. No EGER OpenSTA adapter or Oracle-generalization experiment was implemented.
