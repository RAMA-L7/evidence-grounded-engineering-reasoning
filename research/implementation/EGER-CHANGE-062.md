# EGER-CHANGE-062 — P191-R5 Manuscript Reconciliation with P191-R4 Causal Pilot

Date: 2026-09-09
Gate: P191-R5 — Manuscript Reconciliation & Final Publication Preparation
Baseline at change: `928d573fe9647eaeb7e1f112f76eebb07a303a23` (HEAD == origin/main)

## Change

Reconciliation of the publication manuscript, research state, and reproducibility
documentation with the independently verified P191-R4 framing-causality pilot
(EGER-RQ5-PILOT-004). Documentation-only change.

## Purpose

P191-R4 executed the pre-registered 48-run causal framing pilot as the planned final
experiment of the thesis (P192 Path B decision). The pilot reached its defined
endpoint and was independently audited (PASS WITH MINOR DOCUMENTATION REVISIONS).
This change reconciles the research documentation with that evidence so the
manuscript can proceed to the final publication gate with a synchronized research
state.

## Verified P191-R4 result (source of truth: local raw records)

- 48 scheduled runs; 46 COMPLETED; 2 INCOMPLETE (provider timeouts, retained;
  SUCCESS=0 under the frozen unconditional estimand).
- Primary outcome: `SUCCESS = 1` iff `status==COMPLETED` AND both `set_input_delay`
  and `set_output_delay` present; otherwise 0.
- Primary results (scheduled-run denominators): BENCH2-002 A1 7/8 vs A4 5/8
  (RD +0.250); BENCH2-004 A1 8/8 vs A4 5/8 (RD +0.375); BENCH2-005 A1 7/8 vs
  **A4 4/8** (RD +0.375).
- `RD_equal = +1/3 ≈ +0.3333`.
- Primary inference: exact blocked permutation test of `RD_equal` — exhaustive
  C(16,8)=12,870 relabelings per task, exact rational convolution across tasks
  (2,131,746,903,000 enumerations; deterministic; no common-effect assumption).
  One-sided exact p = 0.16265286; two-sided descriptive p = 0.32530572.
- Verdict class: **positive-direction, non-significant causal pilot evidence.**
  Framing causality NOT established. RQ-4 remains closed at behavioral-association
  level.

### BENCH2-005 discrepancy resolution

The authoritative BENCH2-005 result is **A1 = 7/8, A4 = 4/8, RD = +0.375**. The
transient "A4 5/8" wording existed only in local execution narrative prose and was
a reporting discrepancy, not a raw-data or analysis error. No raw record was
modified; prose was reconciled to the raw evidence.

### Primary vs secondary analysis separation

`analysis.json` reports completed-only conditional success rates (aggregate +0.4167).
This is explicitly labeled in the manuscript as a **secondary descriptive analysis**
and is not presented as the primary causal estimate. The primary causal result is
the unconditional scheduled-run estimand (`RD_equal = +0.3333`, exact one-sided
blocked permutation p = 0.16265286).

## Artifacts changed (version-controlled documentation)

1. `research/paper/EGER-RESEARCH-TECHNICAL-REPORT-001.md`
   - Abstract: RQ-4 line extended with the bounded P191-R4 pilot result.
   - Abstract limitations: inferential-statistics wording updated; pilot N stated.
   - §2.1: pre-registered pilot noted with pointer to §6.3.
   - New §6.3 "RQ-4 framing-causality pilot (P191-R4 / PILOT-004)": design,
     estimand, per-task table (BENCH2-005 A4 = 4/8), exact permutation inference,
     execution accounting, secondary completed-only analysis explicitly labeled,
     bounded interpretation, attempt-1/attempt-2 execution integrity.
   - §10 Limitations: pilot N, non-significance, INCOMPLETE handling added.
   - §11.3: pilot model configuration added.
   - §11.4: P191-R2 design record and PILOT-004 matrix added.
   - §11.5: PILOT-004 protocol constraints and execution-integrity note added.
   - §11.9: PILOT-004 added to intentionally-local raw records.
   - §12 Conclusion: bounded pilot-conclusion item 6 added (no causality claim).
   - §13 Source Record Map: P191-R2/P192/CHANGE-062 records and PILOT-004 path added.
   - §14 Claim Audit: pilot counts/inference added as directly supported; bounded
     directional finding added; "framing causality established" added to Not supported.
   - §15 Final Status: reconciliation note added.
2. `research/STATE.md` — current snapshot refreshed (post-P191-R5): frozen-state
   block extended with P191-R4/P191-R5 entries; Arc 1 annotated; new
   "P191-R4 causal pilot" section; Next section updated. Historical content
   above the snapshot is untouched.
3. `research/REPRODUCIBILITY.md` — PILOT-004 added: model configuration, frozen
   matrix, manifest/seed/hash, no-retry exception, primary outcome definition,
   data boundaries, reproduction requirements, provenance (attempt-1 abort,
   attempt-2 cohort, runner-local hardening).

## Research state

- This is a documentation/packaging artifact only.
- No experiment was rerun. No raw experimental data was modified.
- No research conclusion was upgraded. No evidence level was changed.
- No historical research record was rewritten. `research/STATE.md` follows its
  established append-only snapshot convention; the new snapshot is added and
  prior snapshots preserved.
- The strongest defensible pilot statement remains: under the tested MODEL-005,
  frozen synthetic VLSI tasks, frozen A1/A4 framing manipulations, and
  deterministic Ṛta evaluation conditions, the causal pilot observed a
  positive-direction but non-significant framing effect on the pre-specified
  SUCCESS outcome (RD_equal = +0.33, exact one-sided p ≈ 0.16).

## Claim boundaries

P191-R5 / CHANGE-062 does NOT establish:

- framing causality (pilot is positive-direction, non-significant)
- statistical significance of the framing effect
- model independence
- statistical model superiority/equivalence
- arbitrary-authority generalization
- universal generalization
- production-scale validity
- Oracle interchangeability
- causal model×Oracle interaction claims

## Validation

- EGER regression: 878/878 PASS (run after pilot execution; no code changed since).
- Harness subset (C1/C2/RQ4 runner tests): 80/80 PASS.
- Numerical claims verified against local raw records: PASS
  (raw_trials.json snapshot 506870dc04e30048; perm_test_results.json 72e0271abdc69337;
  manifest hash `8350e3519b00ab24373e7a57e04c38df5bc3657b935f50db56101880c50ba890`).
- Protected historical records: untouched.
- Raw experimental data: local-only, untracked, unchanged.

## Git

- Documentation artifacts are new working-tree modifications; no commit has yet
  been created for P191-R5.
- Commit requires explicit authorization at the next publication gate.
- Intended commit set: `research/paper/EGER-RESEARCH-TECHNICAL-REPORT-001.md`,
  `research/STATE.md`, `research/REPRODUCIBILITY.md`,
  `research/implementation/EGER-CHANGE-062.md` (this file).
- Raw experimental data (including `research/experiments/EGER-RQ5-PILOT-004/`)
  remains local-only and is NOT part of the intended commit set.
