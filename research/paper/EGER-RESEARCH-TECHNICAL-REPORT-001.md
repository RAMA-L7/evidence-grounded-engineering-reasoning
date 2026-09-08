# EGER — Evidence-Grounded Engineering Reasoning with Deterministic Evaluation Authorities

**Type:** Technical report / research paper (manuscript)

**Manuscript ID:** EGER-RESEARCH-TECHNICAL-REPORT-001

**Repository:** `D:\Research on EGER` (private, version-controlled; see README.md)

**Status:** Assembled from the frozen research package after P187-R. This is a packaging artifact, not a new experiment and not a conclusion upgrade.

---

## Abstract

Large language models (LLMs) can generate syntactically plausible synchronous digital constraint (SDC) files, but fluent generation is not the same as engineering correctness. This paper presents **EGER (Evidence-Grounded Engineering Reasoning)**, an architecture that pairs LLM proposal generation with **deterministic external engineering evaluation** and uses structured evaluation evidence to drive bounded revision before a deterministic final verification authority decides accept/reject.

EGER introduces a clear separation of roles:

- a **probabilistic LLM** proposes candidate SDC,
- one or more **deterministic evaluation authorities** produce structured evidence from their own engineering properties,
- evidence is **normalized** into a common evidence contract,
- a **revision controller** operates on that evidence within bounded iteration and retry budgets,
- a deterministic **VerificationGate** remains the sole final accept/reject authority.

We report two coordinated research threads:

1. An **architecture ladder (C0–C5)** and **RQ-4**, investigating whether structured evidence reliably drives revision behavior. RQ-4 is **closed** at the behavioral-association level; causality is **not established**. C3 was **not justified** because a more parsimonious explanation (task framing) was found; C4 and C5 remain **deferred**.

2. An **RQ-5** series testing whether the EGER control loop operates with **two independent deterministic evaluation authorities** — **Ṛta** (structural/constraint-quality) and **OpenSTA** (timing) — under frozen synthetic VLSI conditions. The RQ-5 pilot (PILOT-002, 8 trials) completed 8/8 with **0 failures and 0 retries**; both authorities drove their own evidence-grounded loops. On one task, the two authorities **legitimately disagreed** because they measured different engineering properties — evidence for authority separation, **not** interchangeability.

A subsequent **model-comparison experiment (P185, PILOT-003)** tested whether the same architecture operated with a **second LLM** under the same authorities and tasks: **2 models × 2 tasks × 2 Oracles × 2 replications = 16 trials**. The experiment completed **15/16 trials** (1 documented baseline-model output failure, handled per the frozen bounded-retry policy), with **43 Oracle evaluations / 43 evidence artifacts**, **3 retries**, and an identity audit of **ok=True, 0 violations**. This supports a **descriptive** statement that the architecture operated with two tested models under the tested conditions. It does **not** establish model independence.

**Explicit limitations:** small pilot samples; synthetic VLSI tasks; two language models only; two deterministic authorities only; descriptive statistics only; no inferential superiority claim; no universal model-independence claim; no arbitrary-authority generalization; no production-scale evaluation.

---

## 1. Introduction

Engineering reasoning about digital constraints requires more than fluent text generation. An LLM can produce an SDC file that reads coherently and still contain constraint defects: missing delays, invalid syntax, incomplete scope, or timing-implausible structure. A proposal-only LLM workflow has no deterministic external check inserted between generation and acceptance. The central question EGER investigates is therefore not whether LLMs can write SDC, but **whether inserting deterministic external engineering evaluation into the reasoning loop improves the structure of the resulting engineering reasoning process**.

The motivation is architectural rather than performance-optimizing. If an LLM is the only component touching the candidate between generation and acceptance, then correctness claims ultimately collapse into the model's own self-evaluation. EGER instead introduces **deterministic external evaluation authorities** as evidence sources:

- **Ṛta** evaluates structural/constraint-quality properties of the SDC against a frozen rule catalog.
- **OpenSTA** evaluates actual timing properties (for example, worst negative slack under a clock and constrained paths).

These authorities are **deterministic** and **external** to the LLM. Their outputs are normalized into a **common evidence contract** so that a revision controller can operate on structured findings rather than on free-form interpretation.

The key idea is that **evidence grounded in deterministic evaluation** is a different kind of input to the reasoning loop than free-form textual feedback. The research asks what difference that makes, where it makes it, and — critically — what it does **not** imply.

### What EGER is not

- EGER does **not** make the LLM the final authority. **VerificationGate** is the sole final accept/reject authority.
- EGER does **not** treat Oracle execution success as engineering validation. Execution is not the same as sufficiency, which is not the same as correctness, which is not the same as authorization.
- EGER does **not** claim that different authorities are interchangeable. Authority-specific semantics are preserved.
- EGER does **not** claim model independence, universal generalization, statistical superiority, or production readiness from the present evidence.

---

## 2. Research Questions

The present manuscript reports two explicitly separate research questions. They must not be collapsed into one over-strong claim.

### 2.1 Architecture research (C0–C5 / RQ-4)

**RQ-4 (closed):** To what extent does structured deterministic evidence affect proposal revision behavior in the EGER framework?

This thread studies an **architecture hypothesis**: that inserting deterministic evaluation evidence into the revision loop changes revision behavior in a measurable way, and whether that effect is consistent, causal, or dependent on framing.

### 2.2 Cross-authority operation (RQ-5)

**RQ-5 (closed at Level 2):** To what extent does the evidence-grounded EGER architecture operate with independent deterministic evaluation authorities under frozen synthetic VLSI conditions?

RQ-5 uses two authorities — **Ṛta** and **OpenSTA** — that evaluate **different engineering properties** by design. The research question is whether the control loop can operate faithfully with both, and what the authority-specific outcomes look like. It is **not** a question of whether the authorities agree or are equivalent.

### 2.3 Model comparison (P185)

**Model comparison (descriptive, P185):** To what extent does the evidence-grounded EGER architecture operate with **different large language models** under the same deterministic evaluation authorities and VLSI engineering tasks?

This question tests **model dependence** as an explicit uncertainty, not general model independence. The strongest defensible statement from P185 is **operation under two tested models under the tested conditions**, not model independence.

---

## 3. EGER Architecture

### 3.1 Conceptual loop

```
Task Definition
      ↓
LLM Proposal
      ↓
Deterministic Oracle (Ṛta and/or OpenSTA; each with its own property)
      ↓
Structured Evidence
      ↓
Revision Loop
      ↓
Verification Gate
      ↓
ACCEPT / REJECT
```

The LLM proposes a candidate SDC for a defined task. A deterministic Oracle evaluates that candidate against its own property. The raw output is normalized into structured evidence. The revision controller may iterate, within a bounded budget, using the evidence as input. The VerificationGate receives the evidence and makes the final accept/reject decision.

### 3.2 Implemented components

```
TaskDefinition
      ↓
PromptBuilder
      ↓
ProposalGenerator (LLM)
      ↓
CandidateArtifact
      ↓
OracleAdapter
      ↓
EvidenceNormalizer
      ↓
EvidenceArtifact
      ↓
RevisionController
      ↓
VerificationGate
      ↓
ProvenanceTracker
```

Key architectural distinctions:

- **Proposal generation** is probabilistic. The LLM is the only probabilistic component.
- **Deterministic evaluation** is external and deterministic. Ṛta and OpenSTA each apply their own semantics.
- **Evidence normalization** converts raw Oracle outputs into a common structured form so that the revision controller and VerificationGate can operate on evidence rather than on raw authority-specific formatting.
- **Revision** operates on evidence within bounded iteration/retry budgets. It is deterministic-at-interface in the control-loop sense (the architecture, not the LLM).
- **Authorization** is singular: VerificationGate is the sole final accept/reject authority.
- **Provenance** tracks candidate bytes, hashes, evaluation evidence, and decisions.

### 3.3 Authority boundary

- **Ṛta** is a structural/constraint-quality authority. It checks whether the SDC constraints are structurally complete and internally consistent according to a frozen rule catalog.
- **OpenSTA** is a timing authority. It evaluates timing under the constraints present in the SDC (e.g., WNS on constrained paths under a clock).

These authorities **do not** compute the same property. A Ṛta accept does not imply timing feasibility, and an OpenSTA reject does not imply structural invalidity. This distinction is central to the research and to the manuscript.

### 3.4 Architecture source status

`research/architecture/EGER-ARCH-002.md` is the **recommended architecture design** for C0–C5. It is **not** an experimentally validated result; ARCH-002 itself states it is "Not validated" and that "C0–C5 have not been executed." The implemented loop described above is the **executed-series architecture**, which should be presented alongside ARCH-002 rather than conflated with it. ARCH-001 is the superseded predecessor and is preserved for traceability.

---

## 4. Evidence Contract

### 4.1 Why normalization matters

Raw Oracle outputs are **not** directly consumed by the reasoning loop. Different authorities produce different output formats and different semantics. If the revision controller consumed raw authority-specific output directly, the architecture would either become authority-specific or would risk conflating different kinds of findings.

EGER therefore normalizes Oracle outputs into a **structured evidence artifact**:

- findings with typed scope and severity,
- evidence provenance,
- compatibility metadata.

The normalization layer preserves **authority-specific semantics** while presenting a common interface to the rest of the loop. This is what makes multiple deterministic authorities compatible with the same pipeline **without** making them equivalent.

### 4.2 What the evidence contract does not do

Normalization does **not**:

- make Ṛta and OpenSTA evaluate the same property,
- make an accept from one authority imply an accept from another,
- erase the distinction between constraint-quality evaluation and timing evaluation,
- turn execution into validation.

The evidence contract is an interface, not an equivalence claim.

### 4.3 Provenance

Provenance is hash-based and timestamped: input/raw/evidence/candidate hashes and provenance metadata are recorded. This supports identity auditing (for example, verifying that the bytes an Oracle evaluated are the bytes recorded) and prevents silent candidate substitution.

---

## 5. Experimental Method

### 5.1 Tasks and substrate

RQ-5 and the model-comparison experiment use **frozen synthetic VLSI tasks** on a **3-cell substrate** (simple path). Two tasks are used:

- **T1:** incomplete clock/constraint scenario — a candidate must complete missing constraints.
- **T2:** aggressive 0.05 ns clock scenario — the frozen task fixes the clock period; the model must add/modify I/O delays without changing the clock.

These are **descriptive pilot tasks**, not production designs. Their scope is explicitly limited to the tested conditions.

### 5.2 Authorities

- **Ṛta:** version 1.5.11, pinned commit `3b5c2f2`, invoked netlist-less with P055 DesignMetadata for FULL-scope evaluation where applicable.
- **OpenSTA:** version 2.2.0, used under WSL2 in the relevant experimental records.

Both authorities are **deterministic** for a given input. Both are **unchanged** by the research gates reported here.

### 5.3 Candidate validity gate

Before any Oracle invocation, each candidate is classified:

- **VALID_SDC**
- **NON_SDC_OUTPUT**
- **EMPTY_OUTPUT**
- **PROVIDER_FAILURE**

Invalid candidates **do not reach the Oracle**. The failure is recorded deterministically. This is a gate, not a repair step.

### 5.4 Initial Oracle evaluation

For every valid initial candidate, the assigned Oracle evaluates it **before revision**. The `initial_oracle_result` is mandatory and is used for PO-3. This establishes a before/after baseline within each trial.

### 5.5 Revision loop

- Maximum **3 revision iterations per attempt**.
- The model receives the **assigned Oracle's feedback**.
- Oracle-specific feedback is preserved; one Oracle's feedback is not exposed to the other Oracle's arm.
- Each revised candidate must pass candidate validation before Oracle invocation.
- No manual modification of the candidate; no silent repair.

### 5.6 Bounded retry

- Maximum **1 bounded retry per trial**.
- Retry is for provider failure, empty output, invalid model output, timeout, or infrastructure failure.
- Retry is **not** for obtaining a better engineering result from a valid REJECT.
- If a retry occurs, `retry_count` is incremented, **both attempts are retained**, and both candidate/result chains are recorded.

### 5.7 Counterbalancing and candidate identity

- **RQ-5 / PILOT-002:** 2 tasks × 2 Oracles × 2 replications = **8 trials**. Order is counterbalanced: **T1 Ṛta-first, T2 OpenSTA-first**.
- **P185 / PILOT-003:** 2 models × 2 tasks × 2 Oracles × 2 replications = **16 trials**. The baseline model block (mimo) runs first, the comparison model block (nemotron) second; counterbalancing is preserved within each model block (**T1 Ṛta-first, T2 OpenSTA-first**).

**Candidate identity** is handled precisely:

- The **shared initial SDC** for a task is byte-identical across the two Oracle arms and across replications (verified by identity audit).
- **Oracle-specific revised candidates are allowed to diverge** by design because Oracle-specific feedback drives revision.
- Revised candidates are **not** asserted to be byte-identical across Oracle arms.

### 5.8 Outcome definitions

- **PO-1 (completion quality):** ROBUST / MARGINAL / FAILED.
- **PO-2 (evidence compatibility):** whether the Oracle's evidence entered the common EGER evidence contract.
- **PO-3 (Oracle-detected improvement):** IMPROVED / NOT_IMPROVED / WORSE / NOT_MEASURABLE — Oracle-specific by design (Ṛta uses ERROR-count delta; OpenSTA uses WNS delta).

### 5.9 Qualified accept

An ACCEPT based on metadata-unqualified or PARTIAL evidence is **not** a fully qualified ACCEPT. The qualified-accept rule is applied as a frozen experiment-layer rule:

- For Ṛta: FULL evidence is expected when frozen P055 DesignMetadata references validate.
- For OpenSTA: require valid clock and meaningful constrained timing evaluation (no `NO_TIMING_CONSTRAINT` vacuous-pass condition).

### 5.10 Aggregation

All primary outcomes are derived **deterministically from raw records**. No manual totals are entered.

---

## 6. C0–C5 / RQ-4 Results

### 6.1 Architecture ladder

| Stage | Status | Notes |
| ----- | ------ | ----- |
| C0 | ESTABLISHED | Baseline: proposal activation near-universal; no deterministic validation; documented limitations. |
| C1 | ESTABLISHED | Structured evidence feedback reliably activates revision; ERROR adherence is task-dependent. |
| C2 | PARTIALLY SUPPORTED / absorbed into C1 | Structured feedback is more actionable than text; structure-over-prose is the important signal. |
| C3 | NOT JUSTIFIED | Prompt design (task framing) is a more parsimonious explanation for adherence variability; epistemic-state intervention was not justified by the evidence. |
| C4 | DEFERRED | Evidence-conditioned routing is a deferred engineering design choice, not an experimentally disproven architecture. |
| C5 | DEFERRED | Non-bypassable authorization is a deferred engineering design choice, not an experimentally disproven architecture. |

Deferred **does not** mean disproven. It means "not yet motivated by evidence."

### 6.2 RQ-4

**RQ-4 is CLOSED** at the behavioral-association level.

The evidence shows:

- Structured evidence was associated with reliable revision activation (100% activation in the tested conditions).
- Revision does **not** always address ERROR findings; adherence ranges across task framing (broad framing associated with higher adherence than narrow framing in the tested conditions).
- The effect is **probabilistic, not deterministic**.
- **Framing causality is NOT established.**

RQ-4 is therefore closed with a bounded conclusion: structured evidence is associated with revision behavior in a task- and framing-dependent way, but causality and mechanism are not established.

---

## 7. RQ-5 Pilot Results (PILOT-002)

### 7.1 Execution summary

| Metric | Value |
| ------ | ----- |
| Planned trials | 8 |
| Completed | 8 |
| Failed | 0 |
| Retries | 0 |
| Oracle evaluations | 22 |
| Evidence artifacts | 22 |

Execution order was counterbalanced (T1 Ṛta-first, T2 OpenSTA-first). The 8/8 completion with 0 failures and 0 retries is the reported outcome.

### 7.2 PO-1 (completion quality)

| Condition | ROBUST | MARGINAL | FAILED |
| --------- | :----: | :------: | :----: |
| T1-Ṛta | 2 | 0 | 0 |
| T1-OpenSTA | 0 | 2 | 0 |
| T2-Ṛta | 2 | 0 | 0 |
| T2-OpenSTA | 0 | 2 | 0 |

### 7.3 PO-2 (evidence compatibility)

All 8 trials: **evidence compatible**. Both authorities' evidence entered the existing EGER evidence contract. 22 Oracle evaluations → 22 evidence artifacts.

### 7.4 PO-3 (Oracle-detected improvement)

| Condition | IMPROVED | NOT_IMPROVED | WORSE | NOT_MEASURABLE |
| --------- | :------: | :----------: | :---: | :------------: |
| T1-Ṛta | 2 | 0 | 0 | 0 |
| T1-OpenSTA | 0 | 2 | 0 | 0 |
| T2-Ṛta | 2 | 0 | 0 | 0 |
| T2-OpenSTA | 0 | 0 | 2 | 0 |

### 7.5 Qualified accept

- T1-Ṛta: 2/2
- T1-OpenSTA: 2/2
- T2-Ṛta: 2/2
- T2-OpenSTA: 0/2

### 7.6 The T2 result and why it matters

The most important result in PILOT-002 is **not** that the two authorities agreed. They did **not** agree on T2.

**Same task, same shared initial SDC bytes; each Oracle then evaluated its own feedback-driven revision candidate:**

- **Ṛta (constraint-quality authority):** found no constraint error after the model added structurally valid I/O delays → **ACCEPT** (qualified).
- **OpenSTA (timing authority):** the identical shared substrate produced a genuine timing violation (WNS −0.01/−0.02) that persisted across iterations → **REJECT** (never qualified).

This is **not** a correctness disagreement. It is a **property disagreement**: Ṛta evaluates structural constraint quality; OpenSTA evaluates timing. Each authority operated correctly in its own domain.

### 7.7 The T2 OpenSTA "WORSE" interpretation

The T2-OpenSTA **WORSE** result must **not** be read as "the model made timing worse." The initial 0.05 ns clock-only SDC has no `set_input_delay` / `set_output_delay`, so OpenSTA finds no constrained paths and returns WNS 0.0 — a **vacuous-clean initial floor**. The model's first real candidate (with I/O delays) exposes the genuine timing violation. The frozen task fixes the 0.05 ns clock period, and **no OpenSTA-acceptable candidate was found within the frozen three-iteration revision budget**. This is the task ceiling, not a harness defect.

### 7.8 Replication consistency (descriptive)

All four replication pairs agreed at the outcome level in PILOT-002. This is descriptive only; N=2 per condition is not sufficient for statistical inference.

### 7.9 Claim level

**Level 2 descriptive pilot evidence.**

The highest supported claim from PILOT-002 is:

> The evidence-grounded EGER control loop operated with two independent deterministic evaluation authorities (Ṛta and OpenSTA) across the two frozen synthetic VLSI tasks, with complete, reproducible, authority-separated evaluation evidence entering the same EGER evidence contract and reaching the VerificationGate — under the tested conditions.

**Not supported:** Oracle interchangeability (refuted on T2); universal or production-scale generalization; generalization beyond the tested synthetic substrate/tasks; causal or inferential claims.

---

## 8. Model Comparison Results (P185 / PILOT-003)

### 8.1 Execution summary

| Metric | Value |
| ------ | ----- |
| Planned trials | 16 |
| Completed | 15 |
| Failed | 1 (T1-mimo-R2, CANDIDATE_INVALID) |
| Oracle evaluations | 43 |
| Evidence artifacts | 43 |
| ACCEPT decisions | 11 |
| REJECT decisions | 12 |
| Retries | 3 |

Execution time: ~2483.3 s (~41.4 min) wall time.

### 8.2 Trial matrix

| order | trial | model | task | oracle | status |
| ----: | ------ | ----- | ---- | ------ | ------ |
| 1 | T1-mimo-R1 | mimo | T1 | Ṛta | COMPLETED (ROBUST, retry 1) |
| 2 | T1-mimo-OpenSTA-R1 | mimo | T1 | OpenSTA | COMPLETED (MARGINAL) |
| 3 | T1-mimo-R2 | mimo | T1 | Ṛta | **FAILED** (CANDIDATE_INVALID, retry 1) |
| 4 | T1-mimo-OpenSTA-R2 | mimo | T1 | OpenSTA | COMPLETED (MARGINAL) |
| 5 | T2-mimo-OpenSTA-R1 | mimo | T2 | OpenSTA | COMPLETED (MARGINAL) |
| 6 | T2-mimo-R1 | mimo | T2 | Ṛta | COMPLETED (MARGINAL) |
| 7 | T2-mimo-OpenSTA-R2 | mimo | T2 | OpenSTA | COMPLETED (MARGINAL, retry 1) |
| 8 | T2-mimo-R2 | mimo | T2 | Ṛta | COMPLETED (ROBUST) |
| 9 | T1-nemotron-R1 | nemotron | T1 | Ṛta | COMPLETED (ROBUST) |
| 10 | T1-nemotron-OpenSTA-R1 | nemotron | T1 | OpenSTA | COMPLETED (MARGINAL) |
| 11 | T1-nemotron-R2 | nemotron | T1 | Ṛta | COMPLETED (ROBUST) |
| 12 | T1-nemotron-OpenSTA-R2 | nemotron | T1 | OpenSTA | COMPLETED (MARGINAL) |
| 13 | T2-nemotron-OpenSTA-R1 | nemotron | T2 | OpenSTA | COMPLETED (MARGINAL) |
| 14 | T2-nemotron-R1 | nemotron | T2 | Ṛta | COMPLETED (ROBUST) |
| 15 | T2-nemotron-OpenSTA-R2 | nemotron | T2 | OpenSTA | COMPLETED (MARGINAL) |
| 16 | T2-nemotron-R2 | nemotron | T2 | Ṛta | COMPLETED (ROBUST) |

### 8.3 PO-1 (completion quality)

| model | ROBUST | MARGINAL | FAILED |
| ----- | :----: | :------: | :----: |
| mimo | 2 | 5 | 1 |
| nemotron | 4 | 4 | 0 |
| total | 6 | 9 | 1 |

### 8.4 PO-2 (evidence compatibility)

- mimo: 8/8 trials evidence-compatible (24 evaluations → 24 evidence artifacts).
- nemotron: 8/8 trials evidence-compatible (19 evaluations → 19 evidence artifacts).
- Both authorities' raw results entered the **same** EGER evidence contract and reached the VerificationGate. No universal Oracle score was constructed.

### 8.5 PO-3 (Oracle-detected improvement)

| model | IMPROVED | NOT_IMPROVED | WORSE | NOT_MEASURABLE |
| ----- | :------: | :----------: | :---: | :------------: |
| mimo | 2 | 3 | 2 | 1 |
| nemotron | 4 | 4 | 0 | 0 |
| total | 6 | 7 | 2 | 1 |

### 8.6 Secondary outcomes

| metric | mimo | nemotron |
| ------ | ----: | -------: |
| Oracle evaluations | 24 | 19 |
| Retries | 3 | 0 |
| qualified_accept | 4/8 | 7/8 |
| metadata_unqualified iterations | 0 | 0 |
| no_timing_constraint iterations | 0 | 0 |

### 8.7 Failure analysis

**T1-mimo-R2 — CANDIDATE_INVALID (1 failure).**

- Attempt 1: model returned conversational filler ("The file already exists with exactly the content requested...") with no SDC → NON_SDC_OUTPUT → CANDIDATE_INVALID (retryable).
- Attempt 2: same failure mode → CANDIDATE_INVALID.
- Both attempts retained; `retry_count=1`; trial **FAILED** with CANDIDATE_INVALID.
- Initial Oracle evaluation was still recorded (Ṛta FULL scope, errors on the incomplete T1 initial SDC) — PO-3 NOT_MEASURABLE for this trial.
- This is the P173-R-documented file-writing conversational-filler failure mode of the baseline model, correctly classified as a **model-output failure**, **not** an engineering REJECT and **not** an Oracle failure.

The 3 retries total were all mimo, all CANDIDATE_INVALID, and all were retryable. Nemotron required 0 retries.

### 8.8 Evidence compatibility per authority

- Ṛta (8 trials, 18 evaluations): FULL scope with P055 metadata validation; `metadata_all_validated=True` on all evaluated iterations (0 unqualified).
- OpenSTA (8 trials, 25 evaluations): VALIDATED scope with WNS measured on constrained paths; `clock_defined=True` on every evaluated iteration (0 NO_TIMING_CONSTRAINT).

### 8.9 Replication consistency (descriptive)

| condition pair | R1 vs R2 | consistent? |
| -------------- | -------- | ----------- |
| mimo \| T1-OpenSTA | MARGINAL / MARGINAL | AGREE |
| mimo \| T1-Rta | ROBUST / **FAILED** | DIFFER (model stochasticity) |
| mimo \| T2-OpenSTA | MARGINAL / MARGINAL (both WORSE) | AGREE |
| mimo \| T2-Rta | MARGINAL / ROBUST | DIFFER (iteration-depth variation) |
| nemotron \| T1-OpenSTA | MARGINAL / MARGINAL | AGREE |
| nemotron \| T1-Rta | ROBUST / ROBUST | AGREE |
| nemotron \| T2-OpenSTA | MARGINAL (qa=0) / MARGINAL (qa=1) | DIFFER (accept on R2) |
| nemotron \| T2-Rta | ROBUST / ROBUST | AGREE |

Descriptive only — N=2 per cell does not support statistical reliability claims.

### 8.10 Identity audit

- `ok=True`, `violations=[]`, `shared_initial_across_arms=True`.
- One shared initial-SDC hash per task across both arms and both models.

### 8.11 Descriptive model contrast (no inference)

- Nemotron completed **8/8** with **0 retries**, **4/8 ROBUST**, **7/8 qualified accepts**.
- Mimo completed **7/8** with **3 retries** (1 unrecovered), **2/8 ROBUST**, **4/8 qualified accepts**.
- Both models reproduced the RQ-5 authority-separation pattern: Ṛta and OpenSTA evaluated the same shared task substrate and produced authority-specific verdicts (e.g., T2: Ṛta accepted structurally complete aggressive-clock SDC; OpenSTA flagged a timing violation → REJECT), and both models' evidence reached the VerificationGate.
- No qualitative model×Oracle inconsistency was observed in the reported run: all four Ṛta cells ROBUST/IMPROVED and both OpenSTA clean-floor cells as expected. This is a descriptive observation under the tested sampling and does not establish causal model×Oracle interaction or general model superiority.

### 8.12 Claim level

**Descriptive observation — not model independence.**

The highest defensible model-comparison statement is:

> The EGER evidence-grounded control loop operated with the two tested language models — `opencode/mimo-v2.5-free` and `opencode/nemotron-3.5-lightning-free` — across the frozen synthetic VLSI tasks and the two independent deterministic evaluation authorities (Ṛta and OpenSTA), with evaluation evidence entering the common EGER evidence contract and reaching the VerificationGate, **under the tested conditions** (15/16 trials completed; 1 documented model-output failure of the baseline model).

**Not supported:** model independence (two models ≠ all models); statistical equivalence or superiority of either model; causal claims about model×Oracle interactions; production-scale generalization; broader task classes; universal LLM generalization; reopening RQ-5's Level-2 conclusion or changing C0–C5.

---

## 9. Discussion

### 9.1 Deterministic evaluation as an external control mechanism

The central architectural contribution is not that an LLM can propose SDC, but that **deterministic external evaluation evidence can be inserted between proposal and acceptance** and used as structured input to a bounded revision process. This changes the epistemic structure of the loop: the LLM remains the only probabilistic component, while evaluation and authorization are deterministic.

### 9.2 Structured evidence as an interface

Normalizing raw Oracle outputs into a common evidence contract makes multiple deterministic authorities compatible with the same pipeline **without** making them equivalent. The evidence contract is an interface layer, not an equivalence claim. The RQ-5 results show that both Ṛta and OpenSTA can feed the same contract with authority-specific evidence, and that the pipeline does not require a universal Oracle score.

### 9.3 Authority-specific semantics

Ṛta and OpenSTA evaluate **different engineering properties**. A Ṛta accept does not mean the design meets timing; an OpenSTA reject does not mean the SDC is structurally invalid. The T2 result in PILOT-002 demonstrates this cleanly: the same shared substrate produced an ACCEPT from Ṛta and a REJECT from OpenSTA, each correct in its own property. This is **authority separation**, not oracle interchangeability.

### 9.4 Bounded revision

Revision is bounded by iteration budgets and a bounded retry policy. This is an architectural constraint, not merely a practical convenience. It keeps the loop's behavior auditable and prevents unbounded self-correction outside a recorded process.

### 9.5 Model-dependent operational behavior

P185 shows that the architecture operated with a second model (nemotron) under the same authorities and tasks. It also shows a **model-dependent operational difference**: mimo exhibited the file-writing conversational-filler failure mode intermittently (4 of 17 model invocations across 3 trials), while nemotron showed none (0 of 10). This is an honest recorded observation, not a claim that one model is generally superior.

### 9.6 Why two models do not establish model independence

Two tested models can establish **operation under an additional tested model**. They cannot establish **model independence** across the space of LLMs. Model independence would require additional models and an appropriate experimental design. The present evidence is therefore bounded to the statement that the architecture operated with the two tested models under the tested conditions.

### 9.7 Why two authorities do not establish arbitrary-authority generalization

Two tested authorities (Ṛta and OpenSTA) can establish that the architecture operated with those two authorities under the tested conditions. They cannot establish that the architecture generalizes to arbitrary deterministic engineering authorities, especially those with different evaluation semantics, scopes, or substrates.

### 9.8 Synthetic tasks and external validity

The tasks are synthetic 3-cell VLSI scenarios. The results are therefore bounded to the tested synthetic conditions. External validity to broader task classes, larger designs, or production-scale VLSI is **not established**.

---

## 10. Limitations

- Small pilot samples (PILOT-002 N=8; P185 N=16 with N=2 per condition cell).
- Synthetic VLSI tasks (2 tasks, 3-cell substrate).
- Two language models only (mimo and nemotron).
- Two deterministic authorities only (Ṛta and OpenSTA).
- Descriptive statistics only; **no inferential statistics performed**.
- **No statistical superiority or equivalence claim.**
- **No universal model-independence claim.**
- **No arbitrary-authority generalization claim.**
- **No production-scale evaluation.**
- Authority-specific evaluation semantics (Ṛta constraint-quality vs OpenSTA timing).
- Bounded revision budget (3 iterations per attempt; 1 bounded retry).
- The T2 OpenSTA initial condition is a documented vacuous-clean floor; the "WORSE" metric reflects the first real constraints exposing a timing violation under an unmeetable frozen clock.
- The C0–C5 architecture ladder includes deferred stages (C4, C5) that are **not** experimentally disproven.
- RQ-4 is closed at behavioral-association level; **causality not established**.
- ARCH-002 is a recommended/unvalidated design, not an experimentally validated result.

---

## 11. Reproducibility

### 11.1 Environment

- EGER implementation lives in `eger/` and is tested by the regression suite.
- Deterministic layers (contracts, verification, evidence, oracle, epistemic, authorization, engineer, revision, provenance) are implemented and tested.
- Regression suite: `python -m pytest tests -q`.

### 11.2 Oracle configuration (frozen)

- **Ṛta:** version 1.5.11, pinned commit `3b5c2f2`, invoked as a read-only external deterministic authority. `rta_generate` is not invoked by EGER.
- **OpenSTA:** version 2.2.0 (used under WSL2 in the relevant experimental records).

### 11.3 Models used in P185

- **Baseline:** `opencode/mimo-v2.5-free`
- **Comparison:** `opencode/nemotron-3.5-lightning-free`

Model identifiers: `opencode/mimo-v2.5-free` (baseline) and `opencode/nemotron-3.5-lightning-free` (comparison). Provider/runtime configuration and frozen invocation parameters — including default provider sampling behavior, no explicit temperature override, and the frozen per-model timeout values recorded in the P184/P185 experimental records (180 s for mimo, 300 s for nemotron) — are intentionally recorded in the local P184/P185 experimental records and are not embedded in the public repository package. The repository does not expose provider API keys, credentials, or payment configuration.

### 11.4 Frozen experimental design

- P169 / P172: RQ-5 experimental methodology.
- P177 / P178: matrix, identity, and trial-qualification rules.
- P183: model-comparison experimental design.
- P184: execution readiness gate.
- P185: model-comparison execution (PILOT-003).

Matrices:

- PILOT-002: 2 tasks × 2 Oracles × 2 replications = 8 trials.
- PILOT-003: 2 models × 2 tasks × 2 Oracles × 2 replications = 16 trials.

### 11.5 Protocol constraints

- Maximum 1 bounded retry per trial; both attempts retained.
- Maximum 3 revision iterations per attempt.
- Candidate validity gate before Oracle invocation.
- Initial Oracle evaluation before revision.
- Counterbalanced order where applicable (PILOT-002: T1 Ṛta-first, T2 OpenSTA-first; PILOT-003: baseline model block first, comparison block second, counterbalanced within each block).
- Shared initial SDC identity verified; Oracle-specific revised candidates allowed to diverge.
- PO-2 / PO-3 derived deterministically from raw records.
- VerificationGate is the sole final accept/reject authority.

### 11.6 Provenance / identity auditing

- Hash-based provenance (input/raw/evidence/candidate hashes + timestamp-as-provenance).
- Identity audit verifies that the bytes an Oracle evaluated are the bytes recorded (no silent substitution).

### 11.7 Execution requirements

- Ṛta pinned version/commit and netlist-less invocation with P055 DesignMetadata where applicable.
- OpenSTA 2.2.0 under WSL2 for the timing runs in the reported experiments.
- Both models available under the provider's free-tier configuration as recorded in the experimental records.

### 11.8 Repository structure

- `EGER/` — implementation.
- `research/` — protocols, records, schemas, contracts, architectures, state.
- `research/paper/` — this manuscript.
- `research/implementation/` — gate records and change records.
- `research/architecture/` — architecture designs (ARCH-002 is unvalidated).
- `research/experiments/` — task/substrate definitions (partial); raw experimental records are intentionally local.

### 11.9 Raw experimental data

Raw experimental records (PILOT-002, PILOT-003) are **intentionally local** and are **not automatically exposed by the repository package**. The manuscript cites them by manifest path where needed. The published research records and this manuscript do not embed raw experimental JSON or execution logs.

### 11.9 Test counts

- EGER regression suite: **878/878 PASS**.
- Harness suite: **74/74 PASS**.

---

## 12. Conclusion

The EGER research package establishes a concrete **evidence-grounded engineering control-loop architecture** in which a probabilistic LLM proposes candidate SDC and deterministic external evaluation authorities produce structured evidence that drives bounded revision before a deterministic final verification authority decides accept/reject.

The evidence supports the following conclusions:

1. EGER establishes a concrete architecture separating **proposal generation**, **deterministic evaluation**, **evidence normalization**, **revision**, and **authorization**.
2. Deterministic evaluation evidence can be normalized into a **common EGER evidence contract** without erasing authority-specific semantics.
3. The tested loop **operated with two deterministic authorities** (Ṛta and OpenSTA) and **two tested language models** (mimo and nemotron) under **frozen synthetic VLSI conditions**.
4. Authority-specific semantics remain important: the T2 result shows that the two authorities can legitimately disagree because they measure different engineering properties — evidence for authority separation, **not** interchangeability.
5. Broader generalization and **model independence remain open research questions**. The present evidence does not establish model independence, statistical superiority, universal generalization, arbitrary-authority generalization, or production-scale validity.

**Strongest defensible aggregate statement:**

> The EGER evidence-grounded control loop operated with the two tested language models — `opencode/mimo-v2.5-free` and `opencode/nemotron-3.5-lightning-free` — across the frozen synthetic VLSI tasks and the two independent deterministic evaluation authorities (Ṛta and OpenSTA), with evaluation evidence entering the common EGER evidence contract and reaching the VerificationGate, under the tested conditions.

This statement is explicitly qualified by **"under the tested conditions."**

---

## 13. Source Record Map

This manuscript is assembled from the frozen research package. Key source records:

- **State:** `research/STATE.md` (frozen record through P187).
- **Consolidated state:** `research/implementation/EGER-P181-RESEARCH-STATE-CONSOLIDATION-AND-POST-RQ5-SYNTHESIS-001.md`.
- **RQ-4 / architecture:** `research/implementation/EGER-P133-RESEARCH-DIRECTION-DECISION-001.md`, `EGER-P134-EGER-RESEARCH-STATE-CLOSURE-REVIEW-001.md`, `EGER-P135-RESEARCH-ARCHITECTURE-RECONCILIATION-001.md`, `EGER-P136-EVIDENCE-TO-ARCHITECTURE-SYNTHESIS-001.md`, `EGER-P137-ARCHITECTURE-IMPLEMENTATION-DESIGN-001.md`, `EGER-P138-CORE-CONTRACTS-IMPLEMENTATION-001.md`.
- **Architecture design:** `research/architecture/EGER-ARCH-002.md` (recommended/unvalidated), `EGER-ARCH-001.md` (superseded, preserved).
- **Evidence contract:** `research/oracle/EGER-EVIDENCE-ORACLE-CONTRACT.md`.
- **RQ-5 pilot:** `research/implementation/EGER-P179-RQ5-PILOT002-CONTROLLED-ORACLE-VALIDATION-EXECUTION-001.md` (execution), `EGER-P180-INDEPENDENT-RQ5-RESEARCH-REVIEW-001.md` (review).
- **Model comparison:** `research/implementation/EGER-P185-MODEL-COMPARISON-RQ5-CONTROLLED-EXECUTION-001.md` (execution, revised by P186), `EGER-P186-INDEPENDENT-RESEARCH-REVIEW-OF-P185-001.md` (review).
- **Packaging:** `research/implementation/EGER-P187-RESEARCH-PACKAGING-AND-CLAIM-SURFACE-REVIEW-001.md`, `research/REPRODUCIBILITY.md`, `README.md`.
- **Change records:** `research/implementation/EGER-CHANGE-051.md` through `EGER-CHANGE-060.md`.
- **Schema/contracts:** `research/schemas/EGER-EPISTEMIC-SCHEMAS.md`, `research/schemas/EGER-ARTIFACT-SCHEMAS.md`.
- **Tasks/substrate:** `research/experiments/EGER-BENCH-002.md`, `research/experiments/EGER-BENCH-002-TASKS.json`.
- **Models:** `research/experiments/EGER-MODEL-002.md`, `EGER-MODEL-005.md`.
- **Raw experimental records:** intentionally local under `research/experiments/EGER-RQ5-PILOT-002/` and `research/experiments/EGER-RQ5-PILOT-003/` (not committed).

---

## 14. Claim Audit (manuscript-level)

Each substantive claim in this manuscript was classified before finalization.

### Directly supported

- EGER establishes a concrete evidence-grounded control-loop architecture.
- Deterministic evaluation evidence can be normalized into a common EGER evidence contract.
- The tested loop operated with two deterministic authorities and two tested models under frozen synthetic VLSI conditions.
- VerificationGate is the sole final accept/reject authority.
- Ṛta and OpenSTA are independent deterministic authorities with different evaluation semantics.
- The T2 result demonstrates authority separation, not interchangeability.
- PILOT-002: 8/8 completed, 0 failures, 0 retries, 22 evaluations, 22 evidence artifacts.
- P185: 15/16 completed, 1 failed, 3 retries, 43 evaluations, 43 evidence artifacts; identity audit ok=True, 0 violations.
- Mimo exhibited the conversational-filler failure mode; nemotron did not (in the reported run).
- ARCH-002 is recommended/unvalidated, not experimentally validated.

### Supported with boundary

- Structured evidence is associated with revision behavior (RQ-4 behavioral association; not causal).
- The architecture operated with a second tested model (descriptive; not model independence).
- Mimo showed stronger descriptive failure-mode behavior than nemotron in this run (observed under this sampling; not a proven stable trait).

### Historical design statement

- ARCH-002 recommended C0–C5 topology (design, not validated result).
- C4 and C5 are deferred engineering design choices (not disproven).

### Interpretation (bounded)

- The T2 OpenSTA "WORSE" metric reflects the first real constraints exposing a timing violation under an unmeetable frozen clock — not model harm.
- Two models establish operation under an additional tested model — not model independence.
- Two authorities establish operation with those authorities — not arbitrary-authority generalization.

### Not supported (removed / never included)

- Model independence.
- Statistical superiority or equivalence of either model.
- Causal claims about model×Oracle interaction.
- Universal model generalization.
- Arbitrary-authority generalization.
- Production-scale generalization.
- Oracle interchangeability (explicitly refuted on T2).
- Revised candidates byte-identical across authorities (not asserted).
- ARCH-002 as an experimentally validated result.

No claim in this manuscript exceeds Level-2 evidence.

---

## 15. Final Status

This manuscript is a packaging artifact assembled from the frozen research package after P187-R. It does **not** rerun any experiment, does **not** modify any raw experimental data, does **not** modify Ṛta, OpenSTA, or the VerificationGate, does **not** alter frozen research conclusions, and does **not** upgrade any evidence level.

Manuscript path: `research/paper/EGER-RESEARCH-TECHNICAL-REPORT-001.md`

Status: **Assembled from the frozen EGER research package; publication status is documented by CHANGE-061.**

---

*End of manuscript.*
