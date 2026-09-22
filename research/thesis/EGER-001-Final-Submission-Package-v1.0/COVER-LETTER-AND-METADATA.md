# EGER-001 — Cover Letter Template & Venue Metadata

> **STATUS: DRAFT SUBMISSION EXTRA — NOT A FROZEN RESEARCH RECORD.**
> Reclassified by `EGER-P199-VERDICT-CORRECTION-001.md`; expected to change
> before formal submission (destination, venue standard, author fields).

> **Template status:** `[BRACKETED]` fields only. Pick ONE letter variant
> (A: examiner/outreach, B: journal/conference) per submission.

---

## Variant A — Independent thesis for academic evaluation / outreach

[Date]

[Name / Title]
[Department / Graduate Research Office]
[Institution]
[Address]

**Subject: Submission of an independent research thesis for critical
academic review — "EGER: Evidence-Grounded Revision of LLM-Generated
Engineering Artifacts Under Heterogeneous Deterministic Authorities"**

Dear [NAME / COMMITTEE],

I am submitting EGER-001, an independent M.Tech-standard research thesis,
for critical academic evaluation and would welcome the opportunity to
discuss it with [research group / department] and, where appropriate,
supervised continuation of the research program.

The thesis studies one bounded question: what happens to
generator–verifier control when an LLM revises an engineering artifact
that is evaluated by multiple deterministic authorities whose correctness
semantics are not identical? Its contributions are deliberately bounded:
a controlled, evidence-grounded revision framework; an authority-divergence
existence proof; a model-dependence comparison; a randomized causal framing
pilot reported with exact inference (p = 0.16265286, non-significant); and
explicit non-claims — the thesis asserts no "first" and presents its
literature position as a documented adversarial audit, not a PRISMA
systematic review.

Integrity provisions for examiners: every reported number traces to
frozen, hash-identified records; the released research baseline is public
at commit `28777b2`; a reviewer supplement (README-REVIEW.md) describes a
controlled inspection path for local-only raw records, which are retained
private for provider-privacy reasons. An AI-assistance disclosure
(COVER-PAGE-AND-DECLARATIONS.md) separates AI-assisted execution and
writing from the LLM-as-subject role inside the experiments; the
evaluation authorities are deterministic, version-pinned, non-AI tools.

I confirm the enclosed package is the Final Submission Package v1.0 whose
file hashes are recorded in EGER-P199-CLOSURE-MANIFEST-001.md.

Thank you for your time and consideration.

Sincerely,
Rama Krishna Ketha
ORCID: none · ramasketha14093@gmail.com · Independent Researcher

Enclosures: EGER-THESIS-001-SubmissionCandidate-v1.0.pdf; declarations;
reviewer supplement; closure manifest.

---

## Variant B — Journal / conference (use if Route B is later activated)

Dear [EDITOR / TRACK CHAIRS],

We submit "[PAPER TITLE]" for consideration in [VENUE, TRACK].

Statement of contribution (bounded): a controlled framework for
evidence-grounded revision of LLM-generated engineering artifacts in a
property-plural domain — heterogeneous deterministic authorities preserved
as semantically distinct, outputs normalized through a typed evidence
interface, bounded revision, and a separate non-bypassable verification
authority — evaluated by C0–C5 controlled conditions, an authority-
divergence existence proof, a two-model comparison, and a randomized
causal framing pilot (exact one-sided p = 0.16265286).

Positioning: the LLM→tool→feedback→revision loop, LLM-based SDC
generation, and LLM-assisted STA are established prior art (Self-Refine,
CRITIC, RTLFixer, AutoChip, LLM4SDC, Elsayed/TIMINGLLM); we claim none of
them. Our contribution is the control architecture around evidence under
property pluralism. Literature scope: documented adversarial audit, not a
PRISMA systematic review (statement included).

Declarations: originality declaration; truthful AI-assistance disclosure
(author-directed execution/writing via the Freebuff coding agent; LLMs
studied as the experimental subject; deterministic non-AI evaluation
authorities); all results hash-traceable to frozen records; raw run
records available for controlled examiner inspection (provider privacy).

This manuscript is derived from the frozen EGER-001 thesis (commit
`28777b2`); no experiment was rerun or altered in extraction.

Sincerely,
Rama Krishna Ketha — Independent Researcher — ORCID: none — ramasketha14093@gmail.com

---

## Venue / author metadata template

```yaml
paper:
  title: "EGER: Evidence-Grounded Revision of LLM-Generated Engineering
          Artifacts Under Heterogeneous Deterministic Authorities"
  document_type: independent_research_thesis   # or article (Route B)
  version: "Final Submission Package v1.0 (Draft 003)"
  research_baseline_commit: "28777b2"
  keywords:
    - LLM agents
    - evidence-grounded revision
    - static timing analysis
    - SDC constraints
    - generator-verifier control
    - EDA automation
  primary_subject_areas: [EDA, LLM4EDA, verification, AI for chip design]
author:
  name: "Rama Krishna Ketha"
  orcid: "none"
  affiliation: "Independent Researcher"
  email: "ramasketha14093@gmail.com"
  contribution_roles: "[CRediT roles — complete honestly]"
  ai_assistance: >
    Author-directed execution and writing with the Freebuff coding agent
    (Codebuff, GLM model). LLMs appear inside the experiments as the
    studied proposal generator. Evaluation authorities (Rta 1.5.11,
    OpenSTA 2.2.0) are deterministic, version-pinned, non-AI tools.
claims:
  firsts_claimed: none
  causal_claim_boundary: >
    randomized causal framing pilot only; exact one-sided p = 0.16265286;
    negative/non-significant reported as such; descriptive panels labeled
    descriptive
  literature_scope: >
    documented adversarial audit with dated queries; NOT a PRISMA
    systematic review
conditions_open_at_submission:
  - "F1: Elsayed/TIMINGLLM original full-text direct inspection outstanding"
  - "F2: no PRISMA-complete coverage claimed"
frozen_artifacts:
  thesis_md_sha256: "296674dd4d51a39900046e41d56b60eb0d7c9f75dce210b58e5e1a0357d91b9e"
  thesis_pdf_sha256: "9e65a5e1333f55d0a9562127173d41cc762edb1848764bf1468018b6de2dc4f4"
  pilot004_manifest_sha256: "8350e3519b00ab24373e7a57e04c38df5bc3657b935f50db56101880c50ba890"
related_work_excluded:
  - "EGER-002 (separate program; see EGER-P199-EGER002-BOUNDARY-NOTE.md)"
```
