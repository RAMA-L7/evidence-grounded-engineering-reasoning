# EGER CHANGE-043 — RQ-5 Replication Recovery & Experimental Repair Design (P172)

## Baseline

- **Commit:** 49bebdf16f3036c1998e6b135db0cd1e6f5ee0e2
- **Branch:** main
- **Prior change:** CHANGE-042 (P171 — Results Integrity & Claim Assessment)

## Purpose

Design the minimum scientifically sufficient repair for a future controlled RQ-5 replication, given the P171 verdict that the P170 pilot is **INCONCLUSIVE**. This is a design/recovery gate only — no experiment, no Oracle rerun, no raw-data modification, no code implementation.

## P171 Findings (accepted as fixed, not reopened)

- CRITICAL: 0/15 candidates contained valid SDC syntax (conversational filler in every invocation)
- CRITICAL: OpenSTA ACCEPTs vacuous (no clock → unconstrained → WNS 0.0 → clean)
- CRITICAL: T2 aggressive-clock condition never exercised
- HIGH: PO-3 never measured (no initial Oracle evaluation)
- HIGH: PO-2 report counts unreconcilable with raw data (11/11 vs 15 evaluations)
- HIGH: Ṛta findings mischaracterized in P170 report
- MEDIUM: retry not implemented; counterbalancing not as frozen; schema fields absent

## Repair Decisions

| Area | Decision |
|------|----------|
| Candidate validity | Deterministic gate classifying VALID_SDC / NON_SDC_OUTPUT / EMPTY_OUTPUT / PROVIDER_FAILURE; requires non-empty, non-conversational, ≥1 valid SDC command, task-required construct (create_clock), no injection markers |
| Model recovery | Pre-experiment qualification test (≥5/6 VALID_SDC across both tasks); deterministic-fixture harness validation phase before real-model replication; disqualification on qualification failure |
| Initial Oracle evaluation | Mandatory Oracle evaluation of initial SDC before any model invocation; records initial_oracle_result + initial_evidence_hash; PO-3 frozen definition preserved with NO_TIMING_CONSTRAINT boundary |
| Retry | 1 bounded retry; retry triggers = generation/harness failures (PROVIDER_FAILURE, EMPTY, CANDIDATE_INVALID, timeout); NOT retried = REJECT on valid candidate, Oracle non-zero exit; both attempts recorded; call budget counts retries |
| Counterbalancing | Fixed frozen matrix: Ṛta-first in T1 block, OpenSTA-first in T2 block; script asserts order before trial 1 |
| Task validity | Both Oracles evaluate the same candidate bytes; T1-OpenSTA floor effect documented (initial likely clean → NOT_IMPROVED is valid) |
| OpenSTA vacuous-pass defense | Layered: create_clock requirement in validity gate (primary), NO_TIMING_CONSTRAINT experiment-level classification (secondary); no VerificationGate or adapter change |
| PO-2 accounting | Single authoritative denominator + deterministic aggregation script (raw → analysis.json → report); no manually typed totals |
| Data schema | Corrected with attempt/retry_count, initial/final Oracle results, candidate_validity, raw candidate retained; every field justified |
| Readiness gate | Mandatory checklist (model qualification, validity gate, Oracle verification, timing, retry, counterbalancing, schema, analysis, git) — any critical failure = NO-GO |
| Replication size | N=8 retained (2×2×2) — P170 failure was qualitative (garbage candidates), not under-powered; descriptive pilot remains |

## Decision

**GO** — design completeness for a future controlled replication. Conditions: model qualification passes, readiness gate all-PASS, harness validated on deterministic fixtures, frozen matrix/retry asserted pre-run. Failure of conditions 1–3 = BLOCKED/NO-GO, not improvised run.

The GO authorizes design only. It does NOT authorize experiment execution.

## Research Boundaries

- RQ-5 executed: NO (design only)
- New experiment executed: NO
- P170/P171 records altered: NO
- Raw experimental data modified: NO
- Ṛta modified: NO
- RQ-4 reopened: NO
- C0–C5 conclusions changed: NO
- Oracle comparison performed: NO
- VerificationGate authority changed: NO
- Epistemic-state / authorization logic added: NO
- Production code modified: NO (design gate)

## Test Results

`python -m pytest tests -q` → **864 passed** (unchanged).

## Next Gate

Implementation/readiness gate (harness repair + fixture validation + model qualification), then — only if that passes — a separately authorized controlled replication (EGER-RQ5-PILOT-002). Not started here.