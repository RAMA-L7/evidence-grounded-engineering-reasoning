# EGER — CHANGE-058

## Change Record: P186 — Independent Research Review of P185

| Field | Value |
| ----- | ----- |
| Baseline | `cb4d7b9` (P185) |
| Change ID | CHANGE-058 |
| Date | 2026-09-07 |
| Gate | P186 (research-review gate only) |
| Status | COMPLETE |

## Purpose

Independently audit the P185 model-comparison experiment: raw-record reconciliation, matrix verification, candidate-validity/retry semantics, PO-1/PO-2/PO-3 validity, qualified-accept definition, replication consistency, claim boundaries, and provenance. Raw records were the sole authority; PO definitions were re-derived independently of the harness analysis module.

## Findings

1. **Reconciliation: exact.** 16 records / 15 completed / 1 failed (T1-mimo-R2, CANDIDATE_INVALID, both attempts retained) / 3 retries / 43 evaluations / 43 evidence artifacts / 11 ACCEPT / 12 REJECT — all match the raw records. Independent PO re-derivation matches `analysis.json` and the P185 report per model. Assignment fields consistent with trial IDs; order equals the pre-trial manifest order.
2. **Protocol compliance: clean.** No un-gated Oracle evaluation; no silent repair (hash identity holds); retries only for retryable CANDIDATE_INVALID; OpenSTA vacuous guard held (14/14 evaluated iterations clock-defined); Ṛta metadata validated on all evaluated iterations; identity audit ok=True, 0 violations.
3. **Two prose-count discrepancies found in P185 §11** (documentation only; data and §13 table correct):
   - Replication consistency: §11 says "6 of 8 cells agree / two diverging" — actual and per §13's own table: **5 of 8 agree / 3 differ** (mimo|T1-Rta, mimo|T2-Rta, nemotron|T2-OpenSTA).
   - Model stochasticity: §11 says filler in "3 of 24 model invocations / 0 of 19" — actual: **4 of 17 mimo model invocations (3 trials) / 0 of 10 nemotron**. The 24/19 figures are Oracle evaluation counts, not model invocations.
4. **Failure preserved honestly:** T1-mimo-R2 conversational-filler output classified CANDIDATE_INVALID on both attempts; initial Ṛta evaluation retained; no substitution or silent repair.
5. **Claim boundary held:** operation under two tested models supported descriptively; model independence, statistical superiority, and generalization claims NOT supported.

## Decision

```text
P186 verdict: PASS WITH REVISION

P185 is methodologically defensible with valid data and clean provenance.
Two minimal prose-count corrections to P185 §11 applied (replication
count and model-invocation counts). No data correction, no protocol
change, no experiment rerun. All frozen conclusions unchanged.
```

## Corrections Applied (P180-R precedent)

- `EGER-P185-MODEL-COMPARISON-RQ5-CONTROLLED-EXECUTION-001.md` §11: replication-consistency count corrected to 5 of 8 / three diverging cells; model-invocation counts corrected to 4 of 17 (mimo) and 0 of 10 (nemotron); revision note added to the header. Raw records, analysis, §13 table, and all conclusions unchanged.

## Research Boundaries

```text
RQ-4 reopened: NO
RQ-5 reopened: NO
C0-C5 changed: NO
Rta modified: NO
VerificationGate modified: NO
Model independence established: NO
New experiment executed: NO
Raw experimental data modified: NO
```

## Git / Tests

- Commit: `ff3f5ed`
- EGER suite: 878/878 PASS · Harness suite: 74/74 PASS (re-run in P186)
- Raw experimental records remain local
- Universal_Principles_Library/ untouched

## Next

STOP. Documentation/research packaging is the appropriate next phase — not another uncontrolled experiment. Await explicit user direction.