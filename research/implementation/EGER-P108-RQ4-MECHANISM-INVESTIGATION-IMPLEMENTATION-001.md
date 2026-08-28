# EGER-P108 — RQ-4 Adherence Mechanism Investigation Implementation

## Phase
P108 — Implementation of P107 Design

## Status
**IMPLEMENTATION COMPLETE — NO LIVE EXECUTION — HISTORICAL ARTIFACTS UNCHANGED**

## Governing Principal
Do not assume epistemic uncertainty is the cause. The investigation must determine
which prompt components influence ERROR adherence without presupposing the mechanism.

## What Was Implemented

### Runner: run_mechanism_investigation.py

4-condition mechanism investigation for BENCH2-001:

| Condition | SDC | Objective | Feedback | Tests |
|-----------|-----|-----------|----------|-------|
| Base | 51-char minimal | Original | Full (23 findings) | Baseline |
| E2b | 51-char + added constructs | Original | Full | SDC content effect |
| E3a | 51-char minimal | Broader (production-quality) | Full | Framing effect |
| E4a | 51-char minimal | Original | ERROR-only (2 findings) | Overload effect |

### Condition Isolation

| Comparison | Variable Changed |
|-----------|-----------------|
| Base vs E2b | SDC content (added constructs) |
| Base vs E3a | Task objective (broader framing) |
| Base vs E4a | Feedback scope (ERROR-only vs full) |

All other variables held constant across conditions.

### Configuration

| Parameter | Value |
|-----------|-------|
| Model | MODEL-005 (opencode/mimo-v2.5-free) |
| Runs per condition | 10 |
| Total runs | 40 |
| Calls per run | 3 (initial Oracle + model + final Oracle) |
| Maximum budget | 120 calls |
| Namespace | formal/DIAGNOSTIC-006/ |

### Metrics
- Primary: ERROR adherence (binary)
- Secondary: proposal activation, error_delta, proposal text

### Preregistered Decision Rules
- If E2b > base: SDC content influences adherence
- If E3a > base: Task framing influences adherence
- If E4a > base: Feedback overload influences adherence
- If all ≈ base: Tested prompt factors do not explain variance

### Falsification
If no prompt factor improves adherence over base, the tested manipulations do not
explain the observed stochastic behavior. This does not prove provider nondeterminism
— it means the mechanism remains unidentified.

## Tests

### New Tests (T135–T153)
- 4 conditions exist with correct names
- Base is true baseline
- E2b: only SDC differs
- E3a: only objective differs
- E4a: only feedback differs
- E2b SDC has added constructs
- E3a objective is broader
- E4a feedback is ERROR-only (2 findings)
- Configuration: 10 runs, 40 total, 120 budget
- Model and task frozen
- Namespace isolated
- Historical preservation

**19/19 mechanism-investigation tests PASS**

### Full Regression
**258/258 tests PASS**

## Historical Preservation
- RQ-4 artifacts: UNCHANGED
- DIAGNOSTIC-001–005: UNCHANGED
- C0/C1/C2: UNCHANGED
- MODEL-004: UNCHANGED
- Ṛta: UNCHANGED

## Scientific Constraints
- No live model execution
- No result interpretation
- No C3 authorization
- "No prompt effect ≠ provider nondeterminism" — mechanism remains open

## What This Enables
P109 readiness review → P110 authorization → P111 execution → P112 scientific review

## What This Does NOT Establish
- That any prompt factor causes adherence changes
- That provider nondeterminism is the mechanism
- That C3 is or is not justified

**STATUS: P108 COMPLETE — IMPLEMENTATION ONLY — NO LIVE EXECUTION — READY FOR P109**
