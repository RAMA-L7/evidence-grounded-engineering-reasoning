# EGER-001 — Cover Page, Declarations & Disclosures

> **STATUS: DRAFT SUBMISSION EXTRA — NOT A FROZEN RESEARCH RECORD.**
> Reclassified by `EGER-P199-VERDICT-CORRECTION-001.md`. This file is
> expected to change before formal submission (author fields, destination
> requirements). Permitted use: informal examiner/academic review only;
> a formal submission must apply the target venue/institution's
> requirements for F1/F2/F3.

> **Template status:** `[BRACKETED]` fields must be completed with the
> author's details before any actual submission. Nothing here invents
> author identity. F3 scope statement is included verbatim (source:
> `EGER-P199-F1-F2-F3-SUBMISSION-CONDITIONS-001.md`).

---

## Cover page

**Title:** EGER: Evidence-Grounded Revision of LLM-Generated Engineering
Artifacts Under Heterogeneous Deterministic Authorities — A Controlled
Study in the SDC/STA Domain

**Document type:** Independent research thesis (M.Tech-standard), Draft 003,
Final Submission Package v1.0

**Author:** Rama Krishna Ketha
**ORCID:** none (registration deferred; may be added before formal submission)
**Affiliation:** Independent Researcher
**Contact:** ramasketha14093@gmail.com
**Date:** [SUBMISSION DATE]
**Research baseline:** public repository commit `28777b2` (frozen release)
**Package integrity:** SHA-256 hashes for every package file are recorded in
`EGER-P199-CLOSURE-MANIFEST-001.md`.

---

## Originality declaration

I declare that this thesis is my own work. It contains no material that has
been accepted for the award of any other degree or diploma, and no material
published or written by another person except where due reference is made
in the text. All experimental results reported in this thesis are traceable
to frozen, hash-identified research records; the derivation of every
reported number is documented in the research log, and an independent
audit pass (P194-R1) specifically removed one unverifiable historical
statistic before the content freeze. The research program, experimental
design, executed runs, and analysis records are available for examiner
inspection as described in `README-REVIEW.md`.

Signed: ______________________  Date: ____________
Rama Krishna Ketha

---

## AI-assistance disclosure (truthful, specific)

This research was conducted with AI assistance in three distinct and
separate roles, which the author declares explicitly:

1. **AI-assisted research execution and writing.** The thesis text,
   research-gate records, analysis scripts, and implementation were drafted
   and iterated with the assistance of the Freebuff coding agent (Codebuff,
   running the GLM model) under the author's direction and gate-controlled
   review. Research gates (P169–P199) were explicit review checkpoints;
   frozen records were hash-pinned at each gate and were not rewritten by
   any tool. The author directed the research, approved every gate decision,
   and is accountable for the content.

2. **LLM systems as the *subject* of the study.** Large language models
   (`opencode/mimo-v2.5-free`; comparison model `opencode/nemotron-3.5-lightning-free`)
   appear inside the experiments as the *proposal generator under study* —
   that is the research object, not a hidden aid. Their prompts, budgets,
   timeouts, seeds, and invocation records are frozen and disclosed in the
   experimental records and `REPRODUCIBILITY.md`.

3. **What is *not* AI.** The evaluation authorities that decide acceptance
   (Ṛta v1.5.11, pinned commit `3b5c2f2`; OpenSTA v2.2.0) are deterministic,
   version-pinned, non-AI engineering tools. The VerificationGate, evidence
   normalizer, and provenance tracker are deterministic software components
   with regression-tested invariants. No AI system had authority to accept
   an artifact, alter a frozen record, or change a gate decision.

No AI tool was used to fabricate data; one fabricated/unverifiable
historical statistic was caught and removed during the independent audit
before release, which the author regards as evidence the verification
discipline functioned.

---

## Literature-review scope statement (F3, verbatim)

The literature position of this thesis rests on a documented adversarial
audit: targeted web and index searches across general and domain-specific
sources, citation chaining from the closest prior systems, and verification
of every load-bearing citation against primary or near-primary sources at
the dates recorded in the research log (P193 → P193-R1 → P193-R2 →
P194-R3 → P199). It is **not** a PRISMA-compliant systematic literature
review: no registered protocol, no multi-database string-based screening
(ACM DL / IEEE Xplore / Scopus / Web of Science), and no formal
inclusion/exclusion or duplicate-resolution pipeline were employed. Any
claim of systematic-review completeness is therefore explicitly **not
made**. The final novelty re-check documented in
`EGER-P199-F1-F2-F3-SUBMISSION-CONDITIONS-001.md` (queries and dates
recorded) found no direct occupant of the stated gap as of 2026-09-15.

---

## Residual submission conditions (retained, not hidden)

- **F1:** Elsayed/TIMINGLLM — substantially resolved at abstract/near-primary
  + related-full-text level; original full-text direct inspection still
  outstanding (re-checked 2026-09-15; see F1/F2/F3 record).
- **F2:** literature search is documented and narrowed; not claimed as
  PRISMA-complete (see scope statement above).
- **F3:** novelty re-check performed at submission date 2026-09-15; no
  direct occupant found; frozen P193-R2 novelty statement preserved.
