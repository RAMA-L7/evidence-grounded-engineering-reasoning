# EGER CHANGE-039 — RQ-5 Experimental Protocol Design (P168)

## Purpose

Design and freeze the RQ-5 controlled Oracle-validation experiment protocol. No experiment execution — protocol design only.

## Baseline

- **Commit:** 1821aac12db3b4c4670fdbd1b816e776e6c9e479
- **Branch:** main
- **Prior change:** CHANGE-038 (P167 — Integration Readiness)

## Changes

No code changes. Protocol documentation only.

| File | Change |
|------|--------|
| `research/implementation/EGER-P168-RQ5-CONTROLLED-ORACLE-VALIDATION-PROTOCOL-001.md` | NEW |
| `research/implementation/EGER-CHANGE-039.md` | NEW (this file) |

## Protocol Summary

- **RQ-5:** Architecture generalization across independent deterministic authorities
- **Design:** Descriptive controlled pilot, N=1 per condition
- **Conditions:** ORACLE_RTA (constraint quality) + ORACLE_OPENSTA (timing analysis)
- **Task:** T1-CLOCK-CONSTRAINT with two perturbations
- **Primary outcomes:** Pipeline completion, evidence production, revision behavior
- **Go/No-Go:** GO (all 15 criteria satisfied)

## Key Design Decision

Ṛta and OpenSTA evaluate fundamentally different properties. The experiment does not compare scores — it tests whether the EGER architecture functions with both authorities.

## Research Boundary

UNCHANGED — no RQ-5 execution, no Oracle comparison, no C0–C5 modification.

## Decision

GO — protocol is executable.
