# README — For Examiners and Reviewers

> **STATUS: DRAFT SUBMISSION EXTRA — NOT A FROZEN RESEARCH RECORD.**
> Reclassified by `EGER-P199-VERDICT-CORRECTION-001.md`. The verification
> paths below are real and usable now; the package they describe is
> **submission-prepared with residual conditions disclosed** (F1 full-text
> inspection outstanding; F2 not a PRISMA review; F3 re-check required at
> the actual submission date).

This document tells a reviewer what they are looking at, how to check it,
and how to see more. The thesis answers a bounded question — *what happens
to generator–verifier control when engineering correctness is property-
plural and the evaluators are heterogeneous deterministic authorities?* —
and every number in it traces to frozen, hash-identified records.

## 1. What is in this package

| File | Purpose | SHA-256 (first 16) |
|---|---|---|
| `EGER-THESIS-001.md` | the thesis (Draft 003, content-frozen) | `296674dd4d51a399` |
| `EGER-THESIS-001-SubmissionCandidate-v1.0.pdf` | rendered submission PDF | `9e65a5e1333f55d0` |
| `REPRODUCIBILITY.md` | environment, frozen protocols, data boundaries | `c8d35f81bab35c22` |
| `SUBMISSION-NOTES.md` | package integrity, examiner checklist, F1–F3 | `e3c9e7c2c3a23520` |
| `COVER-PAGE-AND-DECLARATIONS.md` | cover page, originality declaration, AI disclosure, scope statement | (this gate) |
| `EGER-P199-CLOSURE-MANIFEST-001.md` | full-hash manifest + pre-submission checklist | (this gate) |
| `EGER-P199-F1-F2-F3-SUBMISSION-CONDITIONS-001.md` | submission-date F1/F2/F3 resolution | (this gate) |

Full hashes: `EGER-P199-CLOSURE-MANIFEST-001.md`. Verify with
`sha256sum <file>` — any mismatch means the file is not the reviewed one.

## 2. The five-minute integrity check

1. **Baseline:** the released research package is public at commit
   `28777b2`. Tracked-tree modifications at submission time: **zero**.
2. **Thesis ↔ frozen numbers:** every reported statistic traces to a frozen
   record (see §3). The independent audit (P194-R1) exists precisely because
   one unverifiable historical statistic was found and removed.
3. **Claim discipline:** the thesis makes no "first" claims, no causal
   claims beyond the recorded pilot (p = 0.16265286, descriptive panel
   labeled descriptive), and states its T2 result as an existence proof.
   The abstract deliberately under-claims; see Chapter 10's
   established/does-not-establish separation.

## 3. What a reviewer can verify directly (public, from commit `28777b2`)

- **Code with regression-tested invariants:** `eger/` (deterministic
  contracts, verification gate, evidence normalizer, oracle adapters,
  revision controller, provenance tracker). Key components:
  `eger/verification/gate.py` (`7a0109fdbbbf8e56…`),
  `eger/authorization/gate.py` (`744a1d9612072bb8…`),
  `eger/engineer/structured_feedback.py` (`a730a4b1bf54ebdc…`).
  Integrity check: `python -m pytest tests -q`.
- **Frozen benchmark:** `research/experiments/EGER-BENCH-002-TASKS.json`
  (`48a6fadceeeb98b2…`).
- **Frozen causal-pilot protocol and manifest:** PILOT-004 `manifest.json`
  (`50cffba372720c33…`, manifest SHA-256 `8350e351…` as recorded in
  REPRODUCIBILITY.md), runner `run_pilot004.py`
  (`85cf1cc1022e356f…`), exact test `perm_test_rd_equal.py`
  (`e739a4cfbcc72e07…`).
- **All gate/analysis records** referenced by the thesis (P169–P194-R3).

## 4. What is local-only, and how reviewers inspect it

Raw run records (per-run model transcripts, provider traces) are **not
redistributed**: they contain provider account/session traces and are kept
private per the project's data-boundary policy (see REPRODUCIBILITY.md).
This is a deliberate boundary, not an omission — and it is inspectable:

- **On request:** the author will run a mutually agreed verification
  session (shared screen or in person) in which the examiner selects any
  subset of runs; the corresponding raw records, manifests, and re-derived
  statistics are produced live from the local archive, with hashes checked
  against the frozen manifest in front of the examiner.
- **Aggregate integrity:** derived aggregates (dataset.json,
  results.json, analysis.json) and their hashes can be shared with any
  reviewer without exposing provider-sensitive content; raw records can
  then be spot-verified against the aggregates in the session above.
- **Derivation, not trust:** where a thesis number comes from a local raw
  record, the derivation script and its inputs are identified so the
  reviewer can re-derive the number from the aggregate alone.

## 5. Reproducing the headline result

The causal framing pilot (P191-R4): 48 scheduled runs, frozen manifest
(seed 20260908, SHA-256 `8350e351…`), no retries, unconditional estimand.
The reported exact one-sided p (0.16265286) is recomputable from
`perm_test_rd_equal.py` against the frozen trial data; the acceptance/RD
table in Chapter 9 recomputes from `analysis.json` + `RUN_INDEX.json`.

## 6. What this submission does not contain

- **EGER-002** (four-arm benchmark; Stage A complete, documented
  separately). It is future work relative to this thesis by design — see
  `EGER-P199-EGER002-BOUNDARY-NOTE.md`.
- A PRISMA-compliant systematic review (scope statement in
  `COVER-PAGE-AND-DECLARATIONS.md`).
- Any provider credentials, account identifiers, or payment configuration.
