# EGER-CHANGE-033 — OpenSTA Availability Resolution

## Change ID

EGER-CHANGE-033

## Date

2026-09-03

## Gate

P162-R — OpenSTA Availability Resolution

## Summary

Environment resolution gate. Assessed WSL, Docker, and Windows-native paths for OpenSTA availability. WSL is the preferred route — available but requires user action to enable WSL2 and install Ubuntu. Docker is not available. Windows-native build failed in P162. Decision: CONDITIONALLY RESOLVED.

---

## Baseline Commit

`1821aac` (P158 checkpoint)

## Environments Inspected

| Environment | Status | Assessment |
|------------|--------|-----------|
| WSL | AVAILABLE (no distros) | PREFERRED — needs user setup |
| Docker | NOT AVAILABLE | Install timed out |
| Windows-native | FAILED | Missing TCL import library |
| MSYS2 | MINIMAL | No package manager |

## Tools Inspected

| Tool | Status |
|------|--------|
| WSL binary | Available |
| Docker | Not installed |
| MSYS2 pacman | Not available |
| Build tools (P162) | Installed but insufficient |

## OpenSTA Availability

**NOT YET AVAILABLE** — requires WSL setup first.

## Acquisition Path

WSL → Ubuntu → apt/source build → OpenSTA v2.2.0

## Tool Provenance

All tools from official/trusted sources (pip, GitHub, SourceForge, MSYS2).

## Substrate Compatibility

| Component | Assessment |
|-----------|-----------|
| Verilog | Needs correction (behavioral → gate-level) |
| Liberty | Plausible |
| SDC | Sound |
| Tcl | Needs validation |

## Security

No production code modified. No secrets exposure. WSL is a standard Windows feature.

## Decision

**CONDITIONALLY RESOLVED** — WSL is the viable path, requires user to enable WSL2 and install Ubuntu.

## Implementation Changes

**NONE.** This is an environment resolution gate. No EGER production code, tests, or architecture were modified.

## Research-State Impact

NONE — no research conclusions changed.

## Ṛta Impact

NONE — Ṛta was not modified.

## Historical Research Impact

NONE — no historical artifacts were modified.

## Next Gate

P163 — OpenSTA Substrate Validation (after WSL is available)

---

> P162-R resolves OpenSTA environment availability only. No EGER Oracle adapter or Oracle-generalization experiment was implemented.
