# EGER-CHANGE-016 — E3a Wording Deconfounding (DIAGNOSTIC-009)

## Change Identifier
EGER-CHANGE-016

## Date
2026-08-31

## Why

DIAGNOSTIC-008 established a strong replication signal (E3a > BASE on 3/3 tasks), but the E3a objective confounds framing with technical content. P126 designed a 2x2 factorial to separate these factors.

## Files Introduced

| File | Purpose |
|------|---------|
| `research/experiments/EGER-EXP-001/run_e3a_wording_deconfounding.py` | DIAGNOSTIC-009 runner |
| `tests/test_e3a_wording_deconfounding.py` | 20 deterministic tests |

## Frozen Protocol

- 3 tasks x 4 conditions x 8 runs = 96 runs
- 288-call budget
- MODEL-005 only
- Namespace: formal/DIAGNOSTIC-009/

## Historical Preservation

All prior experiments untouched.
