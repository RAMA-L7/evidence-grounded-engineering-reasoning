# EGER-P199 — EGER-002 Boundary Note (excluded from this submission)

> **STATUS: DRAFT SUBMISSION EXTRA — NOT A FROZEN RESEARCH RECORD.**
> Reclassified by `EGER-P199-VERDICT-CORRECTION-001.md`.

**Purpose:** one page, so an examiner or reviewer knows exactly what
EGER-002 is and why it is *not* part of the EGER-001 submission.

---

## What EGER-002 is

A separate research program, designed after EGER-001's content freeze:
a **four-arm controlled benchmark** of LLM-based SDC revision —

| Arm | Evidence available to the revision loop |
|---|---|
| B1 | none (self-correction) |
| R | Ṛta only (structural-rule authority) |
| S | OpenSTA only (timing authority) |
| H | heterogeneous (Ṛta + OpenSTA, semantics preserved) |

with a frozen 128-run Stage-A manifest (4 arms × 4 tasks × 8; manifest
SHA-256 `aecca0f2032de179…`), frozen coverage-adjusted-SWD primary
estimand, exact sign-flip/convolution inference, and an authority-confusion
guard.

## Its status (accurate as of 2026-09-15)

- Stage A **executed completely** (128/128 scheduled runs; 117 COMPLETED,
  11 INCOMPLETE retained under the frozen unconditional treatment).
- Primary outcome **saturated**: every completed run in all four arms
  reached SWD = 0.0 / TNS = 0.0 on the shared substrate — a genuine
  **negative methodological finding** (the primary metric has no
  discriminating power on this substrate), not evidence of arm equivalence.
- Frozen Stage-B gate **failed** per its pre-specified rule → Stage B not
  executed. Descriptive panel (acceptance, alignment, confusion) recorded
  as descriptive only.
- Documented in `research/experiments/EGER-002/execution/`
  (STAGE-A-ANALYSIS-REVIEW-001, visualization amendments V1→V5,
  byte-deterministic publication figures).

## Why it is excluded from EGER-001

1. **Chronology and integrity.** EGER-001's content froze at P194-R3;
   EGER-002 was designed and run afterward. Adding post-freeze results to
   a frozen thesis would violate the program's own record discipline.
2. **Different claim.** EGER-001's contribution is the framework plus the
   controlled characterization within it. EGER-002's outcome is a
   negative-methodology finding (metric saturation) — valuable, but a
   different paper with different lessons, best published separately.
3. **Submission hygiene.** Mixing a saturated-primary benchmark into a
   thesis whose causal claims are deliberately bounded would invite exactly
   the over-claiming the program has spent five gates eliminating.

## How it may be cited

As future work: "A four-arm multi-authority benchmark (EGER-002) has been
designed and executed under the same record discipline; its Stage-A
analysis — including a primary-metric saturation finding and a cohort-scale
descriptive behavioral panel — is documented separately and will be
reported in a dedicated follow-up."

**No EGER-002 material is included in, or required by, this submission.**
