# EGER CHANGE-042 — RQ-5 Results Integrity & Claim Assessment (P171)

## Purpose

Independently audit the frozen P170 experiment records and determine what RQ-5 claim (if any) the collected data legitimately supports, given the documented missing-retry deviation.

## Baseline

- **Commit:** 624fbb5a2869099788ebc02dbaecd838c988a3bf
- **Branch:** main
- **Prior change:** CHANGE-041 (P170 — Experiment Execution)

## Review Scope

- P169 frozen protocol (authoritative)
- P170 execution report and CHANGE-041
- `run_experiment.py` (committed)
- `raw_trials.json`, `analysis.json` (local, reviewed only)
- Independent recomputation of all trial counts and outcomes

## Key Findings

| # | Finding | Severity | Impact |
|---|---------|----------|--------|
| 1 | All 15 candidate evaluations were conversational text, not SDC (0/15 contain SDC syntax) | CRITICAL | Revision loop never operated on valid SDC; task manipulation never occurred |
| 2 | OpenSTA ACCEPT results are vacuous — no `create_clock` in candidate → unconstrained design → WNS 0.0 → timing_clean | CRITICAL | T2 aggressive-clock (0.05 ns) scenario never actually tested; ACCEPT ≠ timing satisfied |
| 3 | PO-3 never measured — no `initial_oracle_result` recorded; "already clean/IMPROVED" is inference | HIGH | Frozen PO-3 definition unsatisfiable from collected data |
| 4 | PO-2 report figures (7/7, 4/4, 11/11) unreconcilable with raw data (12 Ṛta + 3 OpenSTA = 15 evaluations) | HIGH | Reporting inconsistency |
| 5 | 0 retries executed (frozen: 1 bounded retry); `retry_count` field absent | MEDIUM | Documented deviation |
| 6 | Counterbalancing not implemented as frozen (Ṛta-first in both task blocks) | MEDIUM | Documented deviation |
| 7 | Ṛta ERROR finding is SDC-001 "No create_clock defined" (garbage input), not the designed "missing I/O delays" perturbation | HIGH | Report mischaracterizes the finding |

## Protocol Compliance Summary

- Task matrix (2×2×2): EXECUTED
- Max iterations/calls: RESPECTED
- Counterbalancing: NOT as frozen
- Bounded retry: NOT executed (0 retries)
- initial_oracle_result / retry_count schema fields: ABSENT

## Verified Retained Observations

- Both Oracle adapters execute within the pipeline and produce evidence entering the same EGER evidence contract (technical, Level 0/1 — consistent with P164–P167).
- Authority separation held: Ṛta findings remain constraint-quality; OpenSTA findings remain timing; VerificationGate remained sole final authority.
- Trial statuses, iteration counts, call counts, and decisions in the raw records are internally consistent and match `analysis.json`.

## Test Results

`python -m pytest tests -q` → **864 passed** (unchanged). No production code modified.

## Decision

**RQ-5 PILOT INCONCLUSIVE** — the candidate-generation failure (15/15 non-SDC outputs) and the unmeasured PO-3 prevent even a defensible descriptive conclusion about RQ-5. P170's stated Level 2 claim is not supported by the collected data.

## Future Recommendation (documented only)

A future controlled replication must: validate model output is SDC before Oracle invocation; implement the frozen bounded retry; implement counterbalancing as frozen; record initial Oracle evaluations (PO-3); treat "no clock → timing_clean" as a substrate confounder.

## Ṛta Impact

None.

## Research Boundary

- RQ-5 executed: NO (review gate only)
- Experimental data modified: NO
- Ṛta modified: NO
- RQ-4 reopened: NO
- C0-C5 conclusions changed: NO
- Oracle comparison performed: NO
- VerificationGate authority changed: NO
- Epistemic-state/authorization logic added: NO