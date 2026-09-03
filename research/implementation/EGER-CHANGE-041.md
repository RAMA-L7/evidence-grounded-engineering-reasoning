# EGER CHANGE-041 — RQ-5 Experiment Execution (P170)

## Purpose

Execute the P169 frozen protocol to test RQ-5: architecture generalization across independent deterministic evaluation authorities.

## Baseline

- **Commit:** 1821aac12db3b4c4670fdbd1b816e776e6c9e479
- **Branch:** main
- **Prior change:** CHANGE-040 (P169 — Protocol Review)

## Changes

| File | Change |
|------|--------|
| `research/experiments/EGER-RQ5-PILOT-001/run_experiment.py` | NEW — execution script |
| `research/experiments/EGER-RQ5-PILOT-001/raw_trials.json` | NEW — raw trial data |
| `research/experiments/EGER-RQ5-PILOT-001/analysis.json` | NEW — analysis results |
| `research/implementation/EGER-P170-RQ5-CONTROLLED-ORACLE-VALIDATION-EXECUTION-001.md` | NEW |
| `research/implementation/EGER-CHANGE-041.md` | NEW (this file) |

## Results

- 8 planned trials, 7 completed, 1 failed (provider failure)
- Both Oracles produced compatible evidence
- Pipeline completed with both Oracles
- OpenSTA: 3/3 completed (ACCEPT)
- Ṛta: 4/4 completed (REJECT — constraint incompleteness)

## Decision

RQ-5 PILOT VALIDATED — Level 2 claim supported.

## Research Boundary

RQ-5 executed: YES. Oracle comparison: YES (descriptive). Oracle interchangeability: NO.
