# EGER: Evidence-Grounded Engineering Reasoning with Deterministic Evaluation Authorities

## An Independent Research Thesis (M.Tech Academic Standard)

**Manuscript ID:** EGER-THESIS-001 (Version A — Academic Thesis)
**Compiled:** 2026-09-09
**Research baseline:** repository `evidence-grounded-engineering-reasoning` @ release `28777b2`
**As-of date for novelty claims:** 2026-09-09 (per P193-R2 freeze; re-verification required at submission — Freeze Conditions F1–F3)

> **Academic status statement.** This document presents an independently conducted research study developed to M.Tech-level academic research standards. It was produced outside a formal degree program and is **not submitted for the award of any academic degree**. It is offered as a completed independent research foundation for critical evaluation by qualified university researchers, whose criticism is explicitly welcomed as the basis for any future formally supervised research program.
>
> **Integrity statement.** All experimental claims in this thesis are bounded by the evidence records of the underlying research program, which was conducted under frozen, pre-registered protocols with independent audits. Claims that the evidence does not support are stated as such in the text and consolidated in Chapter 11. The thesis deliberately preserves negative and non-significant results.

---

## Abstract

Large language models (LLMs) can produce syntactically plausible engineering artifacts — programs, hardware descriptions, timing-constraint files — but fluent generation is not engineering correctness. A dominant research response is to place the LLM in a generate–repair loop with an automated checker. This thesis begins from the observation that such loops are well established when the checker has a single, kernel-decidable acceptance semantics (compilers, test suites, proof kernels), and asks what generator–verifier control requires in a **property-plural engineering domain** — one where correctness has multiple, semantically distinct dimensions, each with its own deterministic authority, and where no single verifier is structurally sufficient.

We present **EGER (Evidence-Grounded Engineering Reasoning)**, a controlled, reproducible framework for evidence-grounded revision of LLM-generated engineering artifacts. EGER separates three authorities architecturally: a probabilistic **proposal authority** (the LLM), **deterministic evaluation authorities** (each evaluating a different engineering property of the artifact), and a **final verification authority** (a non-bypassable gate that solely decides ACCEPT/REJECT). Outputs of heterogeneous authorities are normalized through a common **typed evidence interface** that preserves authority-specific semantics, revision is driven by that evidence within bounded budgets, and every artifact transformation is provenance-audited.

The empirical program uses LLM-generated **Synopsys Design Constraints (SDC)** — timing-constraint files whose correctness is objectively determinable — as the study domain. A frozen architecture ladder (C0–C5) established that structured deterministic evidence reliably activates revision behavior, that epistemic-state injection is not justified by the evidence, and that task framing is a more parsimonious explanation of adherence variability than architectural extension. A cross-authority pilot (RQ-5) demonstrated that two independent deterministic authorities — a constraint-quality rule catalog (Ṛta) and a static timing analyzer (OpenSTA) — can each drive faithful evidence-grounded loops, and that they **legitimately diverge** on the same artifact because they evaluate different properties: the authority-divergence result that motivates the architecture itself. A two-model comparison (P185) provided a descriptive demonstration that the framework operates with different LLMs under identical authorities. A pre-registered, randomized **causal framing pilot** (P191-R4; 48 scheduled runs, frozen manifest, exact blocked permutation inference) observed a positive-direction but **non-significant** effect of broad versus narrow task framing on error adherence (RD = +1/3, exact one-sided p = 0.163); framing causality is not established by this pilot, and the result is reported as such.

**Contribution.** Against a 2026 literature baseline that already includes LLM-based SDC generation (LLM4SDC, DAC 2026), LLM–EDA feedback repair loops (RTLFixer, AutoChip, TimelyHLS), LLM timing-report analysis (Timing Analysis Agent), evidence-contract terminology in fact-checking (GAVEL), and a handoff-validity research agenda for agentic EDA, this thesis contributes **not** any of those elements individually, but their integration as an experimentally controlled intra-loop architecture: heterogeneous deterministic authorities held semantically distinct, evidence normalized without collapsing authority semantics, revision under bounded control, and final acceptance separated from both proposal and evaluation. The thesis argues that this separation is structurally required for property-plural engineering domains and provides an empirical existence proof motivating that requirement under the tested conditions.

**Limitations.** Small samples (N=8 per cell in the causal pilot); synthetic 3-cell VLSI tasks; two LLMs and two deterministic authorities only; one non-significant causal pilot; no production-scale evaluation. All generalizations are bounded to the tested conditions.

---

## Table of Contents

1. Introduction
2. Background
3. Literature Review and Research Gap
4. The EGER Framework
5. Research Methodology
6. The Architecture Ladder: C0–C5 and RQ-4
7. Cross-Authority Operation: RQ-5 and the Authority-Divergence Result
8. Model Comparison: P185
9. The Causal Framing Pilot: P191-R4
10. Discussion
11. Limitations
12. Reproducibility
13. Conclusions
14. Future Research
References
Appendices

---

## Chapter 1 — Introduction

### 1.1 Problem

Engineering artifacts whose correctness is objectively determinable — programs, hardware descriptions, constraint files — are increasingly drafted by LLMs. Fluent output, however, is not correct output: an SDC file can read coherently and still omit required input/output delays, mis-specify a generated clock, or over-constrain a path that is false by design. In deployment, such defects surface only when a downstream tool evaluates the artifact — synthesis, static timing analysis, formal verification — i.e., when a **deterministic authority** passes judgment.

A proposal-only LLM workflow has no such authority between generation and acceptance. Correctness claims then collapse into the model's self-assessment, which the literature has repeatedly shown to be unreliable for reasoning tasks: LLMs cannot reliably self-correct without external signal (Huang et al., 2024; Kamoi et al., 2024).

### 1.2 The state of the art, precisely

The established response is the **generate–repair loop**: LLM proposes; an automated checker evaluates; the LLM revises. This pattern is mature across compilers (RTLFixer, OriGen), EDA tool feedback (AutoChip, TimelyHLS), tool-augmented critique (CRITIC), and formal theorem proving (Lean-based provers), where the checker's kernel-decidable semantics make acceptance unambiguous. In the specific domain of this thesis, LLM-based SDC *generation* now exists (LLM4SDC, DAC 2026), as does LLM-proposed constraint fixing under static timing analysis (Elsayed 2026). This thesis neither claims nor requires novelty for any of these elements.

### 1.3 The research gap

What the established pattern does not address is the structure of correctness in real engineering domains. A compiler answers one question ("does it parse?"). A proof kernel answers one question ("does the proof check?"). An engineering artifact such as an SDC file is different: its correctness is **property-plural** — syntactic validity, structural constraint quality, and timing effectiveness are distinct dimensions, each judged by a different deterministic tool, each with different semantics, and no single tool's verdict subsumes the others. The 2026 agentic-EDA survey (Liu et al.) identifies exactly this as an open problem: stage-local checker verdicts "do not, by themselves, establish downstream synthesizability, timing compliance, or integration compatibility."

This yields the thesis research question:

> **How should an LLM revise an engineering artifact when multiple deterministic authorities provide evidence about different properties of that artifact — and what architecture makes such revision controlled, auditable, and experimentally characterizable?**

### 1.4 Research questions

Four research questions in three threads, deliberately kept separate (they are not collapsed into one claim anywhere in this thesis). **Note on numbering:** RQ-4 and RQ-5 are legacy identifiers from the underlying research program's frozen records; they are retained unchanged for traceability and are not renumbered here. RQ-M and RQ-C are thesis-local identifiers for the model-comparison and framing-causality threads.

- **RQ-4 (architecture ladder; legacy id; closed).** To what extent does structured deterministic evidence affect proposal revision behavior in the EGER framework? Investigated through the C0–C5 ladder. Closed at the behavioral-association level.
- **RQ-5 (cross-authority operation; legacy id; closed at Level 2).** Can the control loop operate faithfully with two independent deterministic authorities that evaluate different properties? Investigated through PILOT-002. Closed at Level-2 descriptive evidence, including the authority-divergence result.
- **RQ-M (model dependence; thesis-local; closed at pilot level).** Does the framework operate with a second LLM under identical authorities? Investigated descriptively through P185 (Chapter 8).
- **RQ-C (framing causality; thesis-local; closed at pilot level).** Does task framing *causally* affect error adherence? Investigated through the pre-registered randomized pilot P191-R4 (Chapter 9); the pilot was non-significant, so the question remains open.

### 1.5 Contributions

Following the frozen contribution statement (P193-R2, as-of 2026-09-09). **Labeling note:** thesis contributions are labeled K1–K6; the labels C0–C5 are reserved exclusively for the experimental architecture-ladder conditions of Chapter 6 and are never used for contributions.

- **K1 — Architecture (engineering).** The EGER control-loop architecture with three-way authority separation: proposal authority, multiple deterministic evaluation authorities, and a sole, non-bypassable final verification authority.
- **K2 — Evidence interface (engineering + methodological).** A typed evidence contract that normalizes outputs of heterogeneous authorities into a common representation while preserving authority-specific semantics.
- **K3 — Authority separation as an empirically motivated design invariant (scientific-empirical).** The Ṛta/OpenSTA divergence result: two correct authorities legitimately disagreed on the same artifact in the tested conditions because they evaluate different properties. This existence proof converts authority separation from a design preference into an empirically motivated architectural requirement, without claiming demonstrated prevalence or universality.
- **K4 — Methodology.** A frozen-manifest, pre-registered experimental methodology for LLM engineering-behavior studies: randomized blocked designs, unconditional estimands defined before execution, exact non-asymptotic inference, and byte-level identity auditing.
- **K5 — Empirical findings (bounded).** The C0–C5 ladder outcome; Level-2 two-authority operation; descriptive two-model operation; and a positive-direction, non-significant randomized framing pilot.
- **K6 — Research boundaries.** Explicit non-claims (model independence, statistical superiority, Oracle interchangeability, universal/production generalization, established framing causality), maintained throughout.

### 1.6 Thesis organization

Chapter 2 supplies background. Chapter 3 reviews the literature and states the gap. Chapter 4 formalizes the EGER framework. Chapter 5 describes methodology. Chapters 6–9 report the four investigation threads. Chapter 10 discusses what the aggregate evidence means. Chapters 11–14 cover limitations, reproducibility, conclusions, and future research. Appendices carry protocols, schemas, task definitions, statistical derivations, and provenance documentation.

### 1.7 Reader's guide: claims, evidence, and status

Every substantive thesis claim, its evidentiary basis, and its frozen status, in one place:

| # | Claim | Evidence | Status |
|---|---|---|---|
| 1 | Structured deterministic evidence is associated with reliable revision activation | C0–C5 ladder (Ch. 6) | Established, association-level, tested conditions |
| 2 | Epistemic-state injection is not justified by the evidence; framing is more parsimonious | C3 outcome (Ch. 6) | Established within the ladder's evidence |
| 3 | Two independent deterministic authorities can each drive faithful evidence-grounded loops | PILOT-002 (Ch. 7) | Established, Level-2 descriptive |
| 4 | Heterogeneous authorities can legitimately diverge on the same artifact | T2 result (Ch. 7) | **Existence proof** — not prevalence |
| 5 | Single-authority verification cannot establish property-complete correctness in property-plural domains | Architectural argument (§4.4) + claim 4 | Argued + motivating existence proof, not demonstrated as a universal law |
| 6 | The framework operates with a second tested LLM under identical authorities | P185 (Ch. 8) | Descriptive, additive observation only |
| 7 | Broad framing increases SUCCESS probability vs narrow framing | P191-R4 (Ch. 9) | **Positive-direction, non-significant** (p = 0.163); not established |
| 8 | Framing causality | — | **Not established**; open at adequate scale |
| 9 | Model independence / superiority; Oracle interchangeability; universal generalization; production validity | — | **Not established** (non-claims, K6) |

Claims 4–8 are where this thesis most differs from a typical systems paper: the boundary rows are maintained with the same prominence as the positive rows.

---

## Chapter 2 — Background

### 2.1 LLM reasoning and its failure modes

LLMs generate fluent artifacts by next-token prediction; their reasoning failures are well documented, including confident but incorrect rationales. Two findings anchor this thesis's motivation. First, *intrinsic* self-correction — asking a model to find and fix its own errors without external signal — frequently fails or degrades performance (Huang et al., 2024). Second, self-correction succeeds when feedback comes from a **reliable external source** (Kamoi et al., 2024; Gou et al., 2024). The design consequence is direct: the verifier must be outside the model, and its reliability must be structural rather than hoped for.

### 2.2 Generator–verifier architectures across domains

The generate–repair pattern appears with domain-appropriate checkers: compilers and test suites for code; simulators for hardware; retrieval and interpreters for tool-augmented critique (CRITIC); proof kernels for formal mathematics. In formal mathematics the checker is a **kernel** — acceptance semantics are mechanically defined and finality is absolute. This is the strongest existing form of generator–verifier control, and Chapter 4 uses it as the theoretical reference point.

### 2.3 Deterministic evaluation in EDA

Electronic design automation is built on deterministic authorities: synthesis engines, layout checkers, and static timing analyzers (STA) evaluate artifacts against mathematically defined properties. VerilogEval established deterministic, automatic evaluation as the standard methodology for LLM-generated RTL. For SDC specifically, two property families dominate: **constraint quality** (structural properties of the constraint set: clocks, delays, exceptions) and **timing effectiveness** (what an STA engine computes under the constraints, e.g., worst negative slack). These are evaluated by different tools with different semantics — the property pluralism this thesis is built around.

### 2.4 SDC and timing constraints

Synopsys Design Constraints (SDC) is the industry-standard format for expressing timing intent: clock definitions (`create_clock`, `create_generated_clock`), port delays (`set_input_delay`, `set_output_delay`), and path exceptions (`set_false_path`, `set_multicycle_path`, clock groups). Three properties of the format matter for this thesis. First, **input/output delays define the boundary conditions of timing analysis**: `set_input_delay`/`set_output_delay` tell the STA engine when signals arrive at and are required to leave the design's ports; if they are missing, input- and output-path analysis is silently voided — the tool does not fail loudly, it simply constrains nothing, producing optimistically empty results. Second, **structural validity and timing effectiveness are independent dimensions**: a constraint set can be syntactically well-formed and structurally complete (correct clock definitions, plausible exception structure) yet still be timing-ineffective — e.g., missing delays leave paths unconstrained, or an over-broad exception masks real violations. Conversely, a structurally imperfect set may still produce meaningful timing results. Neither authority's verdict subsumes the other's. Third, **legitimate authority pluralism follows**: constraint quality (structural properties of the constraint set itself) and timing effectiveness (what an STA engine computes under the constraints) are evaluated by different tools, over different object semantics, with different failure modes — the property pluralism this thesis is built around. SDC quality directly conditions synthesis and timing analysis, and constraint authorship remains expert manual work, which is why LLM automation of SDC is an active frontier (LLM4SDC, DAC 2026) — and why a controlled framework for *evaluating and revising* generated SDC is the complementary open problem this thesis addresses.

---

## Chapter 3 — Literature Review and Research Gap

### 3.1 Review method and scope

The review was conducted as a staged adversarial audit (August–September 2026): a systematic web-index scan across six areas (P193); a depth pass on the closest prior art with full-text verification of the highest-risk items (P193-R1); a completion sweep with mechanism-level adversarial comparison (P193-R2); and a documented database sweep executed for this submission-integrity audit (P194-R3, 2026-09-09: Semantic Scholar API — rate-limited, recorded; Google-indexed ACM DL / IEEE Xplore records via documented query strings; citation chaining on the closest prior art; query strings, dates, and inclusion/exclusion decisions logged in the P194-R3 record). **Methodological limitation, stated rather than hidden:** the sweep used documented query strings against indexed sources rather than institutional Scopus/Web-of-Science screening with PRISMA flow accounting; formal PRISMA-grade screening is retained as a submission-time condition (F2, narrowed). The novelty statement carries an as-of date of 2026-09-09.

### 3.2 Self-refinement and external-feedback correction

Self-Refine (Madaan et al., 2023) established iterative self-feedback refinement; Reflexion (Shinn et al., 2023) added verbal reinforcement from environmental signals; CoVe (Dhuliawala et al., 2023) structured draft–verify–revise for hallucination reduction. The critical line — Huang et al. (2024) and Kamoi et al. (2024) — showed that self-correction without external signal is unreliable, locating the field's open problem exactly where EGER operates: **the reliability and structure of the external verifier**. CRITIC (Gou et al., 2024) demonstrated tool-interactive critiquing, the closest general-LLM architecture, but with no authority separation, no typed evidence artifact, and no final gate.

### 3.3 LLM × EDA: feedback loops and generation

RTLFixer (Tsai et al., 2024) closes a Stage-Bound repair loop for Verilog **syntax** errors with compiler feedback (ReAct + RAG; 98.5% of compilation errors resolved on its debugging dataset). AutoChip (Blocklove et al., 2025) iterates Verilog repair on compiler and simulation feedback — and reports that EDA-tool feedback beat zero-shot only for GPT-4o among four models, an independent model-dependence finding convergent with this thesis's P185 observations. OriGen (Cui et al., 2024) adds compiler-driven self-reflection to open-source RTL generation. TimelyHLS (Mashnoor et al., 2025) iterates HLS code against synthesis and timing reports. Timing Analysis Agent (Nainani et al., 2025) autonomously **debugs** MCMM timing reports — analysis, not constraint revision. VTR-LLM (Wu, Liu & Betz, ACM 2026) debugs failures in the Verilog-to-Routing FPGA CAD flow with a multi-agent LLM framework — SDC appears there as a flow input, not as a revised artifact under authority evaluation. VerilogEval (Liu et al., ICCAD 2023) anchored deterministic evaluation of generated RTL as standard practice.

### 3.4 SDC generation arrives: LLM4SDC

LLM4SDC (Han et al., DAC 2026) generates SDC from natural-language specifications plus RTL via three cooperative agents (specification parsing; false/multi-cycle path discovery; SDC generation), evaluated against expert-validated SDCs with a +9.8% average improvement over rule-based baselines and general LLMs. This work establishes LLM-based SDC generation and benchmarking. **It does not, per its available material, implement in-loop deterministic evaluation, a typed evidence contract, authority separation, or an independent final verification authority; its false-path discovery agent is LLM-based rather than a deterministic STA authority.** It is therefore complementary to EGER (generation vs. controlled revision/verification), and is cited as such — the two halves of an emerging SDC-automation literature.

### 3.5 Evidence contracts, provenance, and handoff validity

GAVEL (Xu et al., Findings of ACL 2026) uses an "Evidence Contract" — atomic subclaims bound to cited text-span evidence units, with deterministic validation of citations and a judge deciding the outcome — in fact-checking. W3C PROV standardizes provenance modeling. The agentic-EDA survey (Liu et al., 2026) proposes **handoff validity** — acceptance conditions, evidence, provenance for artifacts crossing tool/session/organizational boundaries — reviews 82 systems, and explicitly names multi-property validity as open. EGER's own survey classification under that taxonomy is a **Stage-Bound generate–repair system**; what EGER adds is intra-loop: multi-authority evidence normalization, authority separation as an implemented invariant, and a non-bypassable final gate — with controlled experiments, which no surveyed system provides.

### 3.6 The research gap, stated conservatively

| Established (do not claim) | Evidence |
|---|---|
| Generate–repair loops with deterministic feedback | Self-Refine; CRITIC; RTLFixer; AutoChip; OriGen; TimelyHLS |
| LLM-based SDC generation + benchmarking | LLM4SDC (DAC 2026) |
| LLM-proposed constraint fixes under STA | Elsayed 2026 (framework: TIMINGLLM — LLM+RAG diagnosis and constraint-fix generation, validated by replaying through Quartus Prime STA; single timing authority, timing-closure workflow; adjacent; original full-text inspection outstanding — F1 substantially resolved) |
| LLM debugging of FPGA CAD flows | VTR-LLM (ACM 2026; SDC as flow input, not revised artifact) |
| "Evidence contract" terminology | GAVEL (ACL Findings 2026) |
| Provenance modeling | W3C PROV |
| Generator + deterministic checker | Formal theorem proving (Lean et al.) |
| Handoff validity agenda | Liu et al. 2026 |

> **Gap.** No surveyed system implements, within a single engineering-reasoning loop: (1) a typed evidence contract normalizing outputs of **multiple heterogeneous deterministic authorities** while preserving authority-specific semantics; (2) **three-way authority separation** — proposal, evaluation, and a sole non-bypassable final verification authority — as an architectural invariant; and (3) controlled empirical characterization of that architecture, including authority-divergence behavior, model dependence, and a randomized causal pilot, on an artifact whose correctness is objectively determinable. EGER occupies this gap. (Frozen P193-R2; as-of 2026-09-09; conditions F1–F3 apply.)

### 3.7 Related-work comparison matrix

The matrix makes the gap statement checkable claim by claim (✓ present; ✗ absent; — not applicable). Values reflect the surveyed material cited in §3.2–§3.5.

| Work | Artifact / domain | External deterministic feedback | Multiple heterogeneous authorities | Typed evidence contract | Authority semantics preserved | Independent final gate | Controlled experiment | Randomized design |
|---|---|---|---|---|---|---|---|---|
| CRITIC | general reasoning | ✓ (tools) | ✗ | ✗ | — | ✗ | partial | ✗ |
| RTLFixer | Verilog syntax | ✓ (compiler) | ✗ | ✗ | — | ✗ | ✓ | ✗ |
| AutoChip | Verilog | ✓ (EDA tools) | ✗ | ✗ | — | ✗ | ✓ | ✗ |
| OriGen | RTL | ✓ (compiler) | ✗ | ✗ | — | ✗ | ✓ | ✗ |
| TimelyHLS | HLS | ✓ (synthesis/timing reports) | ✗ | ✗ | — | ✗ | ✓ | ✗ |
| LLM4SDC | SDC | ✗ (LLM agents; post-hoc benchmark evaluation) | ✗ | ✗ | — | ✗ | ✓ | ✗ |
| GAVEL | fact-checking | ✓ (deterministic citation validation) | ✗ (single evidence domain) | ✓ (text spans) | — (single type) | ✓ (judge) | ✓ | ✗ |
| Agentic EDA Handoff | research agenda | — (proposes requirements) | proposed | proposed | proposed | proposed | ✗ (no system) | ✗ |
| Lean / LeanDojo | formal proofs | ✓ (proof kernel) | ✗ (single kernel) | ✗ | — | ✓ (kernel) | ✓ | ✗ |
| **EGER (this thesis)** | **SDC** | **✓ (two authorities)** | **✓** | **✓** | **✓** | **✓ (VerificationGate)** | **✓ (four investigations)** | **✓ (P191-R4)** |

The combination row — heterogeneous authorities **and** semantics-preserving typed evidence **and** a non-bypassable final gate **and** controlled/randomized evaluation — is the contribution surface; each individual column has prior art, which §3.6 disclaims.

---

## Chapter 4 — The EGER Framework

### 4.1 Formal model

Let a task specify a design context T and an initial artifact P₀. A model M operating under framing/context C produces a proposal:

```
P = f(M, T, C)
```

A deterministic evaluation authority Oᵢ evaluates a property of the artifact and yields raw findings, which are normalized into structured evidence:

```
E = N(Oᵢ(P, T))
```

A bounded revision controller maps artifact-plus-evidence to a revised proposal:

```
P' = R(P, E),   |iterations| ≤ B
```

A final verification authority V — distinct from every Oᵢ and from M — decides acceptance:

```
V(P') → {ACCEPT, REJECT}
```

The composed loop: `T → M → P → Oᵢ → E → R → P' → V`.

**Notation.**

| Symbol | Meaning |
|---|---|
| T | task / design context |
| M | proposal model (the single probabilistic component) |
| C | framing / context under which M operates |
| P, P₀, P' | artifact (initial, revised) |
| Oᵢ | deterministic evaluation authority i (Ṛta, OpenSTA) |
| E | normalized structured evidence |
| N | evidence normalization (semantics-preserving) |
| R | bounded revision controller |
| B | revision budget (frozen iteration/retry bounds) |
| V | final verification authority (sole ACCEPT/REJECT decision point) |

### 4.1.1 Architecture figure

```
Figure 4.1 — The EGER control loop (three-way authority separation).

            ┌──────────────────────────────────────────────────────┐
            │                    PROPOSAL AUTHORITY                 │
            │        M (LLM, probabilistic) under framing C         │
            └──────────────┬───────────────────────────────────────┘
                           │ P (candidate artifact)
                           ▼
   ┌────────────────────────────────────┐   ┌──────────────────────────────────┐
   │      EVALUATION AUTHORITIES        │   │  (each: deterministic,           │
   │  O₁ Ṛta — constraint quality       │──▶│   version-pinned, read-only,     │
   │  O₂ OpenSTA — timing effectiveness │   │   semantically distinct)         │
   └──────────────┬─────────────────────┘   └──────────────────────────────────┘
                  │ raw findings
                  ▼
   ┌────────────────────────────────────┐
   │  N: EvidenceNormalizer (typed)     │  E preserves authority identity,
   │  → EvidenceArtifact (eger.evidence)│  property scope, severity
   └──────────────┬─────────────────────┘
                  │ E
                  ▼
   ┌────────────────────────────────────┐
   │  R: RevisionController (bounded B) │──▶ P' (revised artifact)
   └──────────────┬─────────────────────┘
                  ▼
   ┌────────────────────────────────────┐
   │  V: VerificationGate               │  sole ACCEPT/REJECT decision;
   │  (final verification authority)    │  non-bypassable by construction
   └────────────────────────────────────┘

   Every arrow is provenance-audited (hash trio + identity audit).
```

### 4.2 Defined properties

The architecture is characterized by six properties, each implemented and (where applicable) tested:

1. **Authority separation.** M proposes; Oᵢ evaluates; V decides. No component exercises another's authority. The LLM never grades its own work; evaluation authorities never author; V is the sole accept/reject decision point.
2. **Evidence preservation.** Normalization N is semantics-preserving: findings remain attributable to their authority with their property-specific meaning. Normalization does not create authority equivalence (demonstrated empirically in Chapter 7).
3. **Verification finality.** V's decision is final and non-bypassable by construction: no path exists from proposal or evaluation output to acceptance that does not pass through V.
4. **Deterministic acceptance inputs.** All evaluation and verification components are deterministic and version-pinned (Ṛta 1.5.11 @ frozen commit; OpenSTA 2.2.0), so behavioral variance is attributable to the single probabilistic component, M.
5. **Provenance.** Every artifact transformation is hash-audited (input/raw/evidence/candidate hashes; timestamp-as-provenance), and identity auditing verifies that the bytes an authority evaluated are the bytes recorded.
6. **Bounded revision.** Revision operates under frozen iteration and retry budgets; no unbounded self-correction exists in the loop.

### 4.3 Implemented components

The reference implementation maps the formal model onto tested components:

```
TaskDefinition → PromptBuilder → ProposalGenerator (LLM)
      → CandidateArtifact → OracleAdapter (Ṛta | OpenSTA)
      → EvidenceNormalizer → EvidenceArtifact
      → RevisionController → VerificationGate
      → ProvenanceTracker
```

The deterministic layers (contracts, verification, evidence, oracle, epistemic, authorization, revision, provenance) are covered by the regression suite (878/878 at release). The LLM is the single probabilistic component; everything it touches is audited.

### 4.4 Why property pluralism forces this architecture

In a kernel-verifiable domain (Lean), a single final checker suffices because correctness has one decidable semantics. An SDC artifact does not: constraint quality (structural) and timing effectiveness (analytical) are different questions with different deterministic answerers. A single-authority loop cannot, on its own, establish property-complete correctness under this condition. Chapter 7 provides an empirical existence proof of this condition under the tested authority pair: the two authorities, both correct in their own property, produce **divergent verdicts on the same artifact**. EGER's architecture is the minimal structural adaptation of generator–verifier control to this condition: normalize without collapsing, separate authorities, gate the result.

---

## Chapter 5 — Research Methodology

### 5.1 Research philosophy

The program is conducted as hypothesis-driven experimental research with frozen protocols: questions, designs, outcome definitions, and analysis procedures are fixed **before** execution; deviations are recorded, never silently absorbed; results are reported regardless of direction (a non-significant causal pilot is reported in Chapter 9 rather than suppressed).

### 5.2 Domain and tasks

Synthetic 3-cell VLSI scenarios (the BENCH-002 set), each defining a design context, an initial SDC, and evaluator-side metadata. Three tasks carry the behavioral studies: BENCH2-002 (generated-clock correctness), BENCH2-004 (false-path exception), BENCH2-005 (multicycle path). Synthetic construction is a deliberate boundary: it enables deterministic ground truth and frozen identity at the cost of external validity (Chapter 11).

### 5.3 Models and authorities

- **Models (proposal authority):** `opencode/mimo-v2.5-free` (baseline, MODEL-005) and `opencode/nemotron-3.5-lightning-free` (comparison). Temperature 0.0; frozen invocation parameters; provider configuration held in local records.
- **Authorities (evaluation):** Ṛta 1.5.11 @ frozen commit — deterministic, external to the reasoning loop, and read-only within EGER; evaluates structural/constraint-quality properties against a frozen rule catalog. **Provenance note:** Ṛta is a self-developed rule authority within this research program; its authority status derives from determinism, version pinning, read-only operation, semantic distinctness from OpenSTA, and independent execution from the proposal process — not from institutional independence (see Chapter 11). OpenSTA 2.2.0 (WSL2 where applicable) is an established external timing tool — deterministic timing analysis.
- **Verification:** VerificationGate — sole final ACCEPT/REJECT authority; untouched across the entire program.

### 5.4 Experimental methodology

Four investigations share one methodology template:

| Investigation | Design | N | Outcome definition | Inference |
|---|---|---|---|---|
| C0–C5 ladder (Ch. 6) | Controlled condition ladder, per-condition frozen series | Condition-level runs (frozen series; see released report §6) | Revision activation; error adherence | Descriptive, association-level |
| RQ-5 / PILOT-002 (Ch. 7) | 2 tasks × 2 authorities × 2 replications, counterbalanced | 8 trials | PO-1 completion quality; PO-2 evidence compatibility; PO-3 per-authority change | Descriptive (Level 2) |
| P185 / PILOT-003 (Ch. 8) | 2 models × 2 tasks × 2 authorities × 2 replications | 16 trials | Same PO family; model invocation counts | Descriptive |
| P191-R4 / PILOT-004 (Ch. 9) | Randomized blocked: 3 tasks × 2 framings (A1/A4) × 8, frozen manifest | 48 scheduled | SUCCESS = 1 iff COMPLETED ∧ both delays present; else 0 (unconditional) | Exact blocked permutation + exact CIs |

### 5.5 Statistical reporting standards

For the causal pilot, the hypotheses were frozen before execution: **H0:** P(SUCCESS|A1) = P(SUCCESS|A4) under the tested conditions; **H1:** P(SUCCESS|A1) > P(SUCCESS|A4) (one-sided, pre-registered). The estimand was frozen as: `RD_task = P(SUCCESS|A1) − P(SUCCESS|A4)` per task; the primary aggregate `RD_equal` is the equal-task-weighted mean (task is a blocking/effect-modification factor). The primary test is an **exact blocked permutation test** — all C(16,8) = 12,870 within-task relabelings per task, combined by exact rational convolution (2,131,746,903,000 enumerations; deterministic; no common-effect assumption). INCOMPLETE runs contribute SUCCESS = 0 (no post-treatment conditioning). Completed-only conditional rates are reported only as explicitly labeled secondary descriptives. The pilot is interpreted as pilot evidence; no inferential superiority or causality claim is made anywhere in this thesis.

### 5.6 Integrity mechanisms

Immutable pre-execution manifests (seed, task order, condition assignment, run IDs, artifact hashes, authority versions); frozen protocol parameters (no retries/replacement/early stopping/extension in the causal pilot); independent audits at every gate; and preserved raw records (local-only) with abort records for infrastructure failures (Chapter 12).

---

## Chapter 6 — The Architecture Ladder: C0–C5 and RQ-4

### 6.1 Design

The ladder evaluates what information the revision loop needs, by controlled condition:

| Condition | Information available to the LLM |
|---|---|
| C0 | Task only |
| C1 | Textual feedback |
| C2 | Structured evidence |
| C3 | Explicit epistemic state |
| C4 | Evidence-conditioned routing |
| C5 | Non-bypassable authorization |

Each transition encodes a hypothesis about what the loop needs; the ladder asks which hypotheses the evidence justifies.

### 6.2 Results

| Stage | Outcome | Evidentiary basis |
|---|---|---|
| C0 | **ESTABLISHED** | Baseline across the frozen task set: proposal activation near-universal; no deterministic validation; limitations documented |
| C1 | **ESTABLISHED** | Structured evidence feedback reliably activates revision (100% activation in tested conditions) |
| C2 | **PARTIALLY SUPPORTED / absorbed into C1** | Structure-over-prose is the operative signal; C2's distinct mechanism not separable from C1 |
| C3 | **NOT JUSTIFIED** | Epistemic-state intervention unjustified; task framing is a more parsimonious explanation of adherence variability |
| C4 | **DEFERRED** | No evidence-driven motivation; deferred ≠ disproven |
| C5 | **DEFERRED** | Deferred engineering design choice |

### 6.2.1 Ladder figure

```
Figure 6.1 — The C0–C5 architecture ladder and its frozen outcomes.

  C0 task only ────▶ C1 +textual feedback ────▶ C2 +structured evidence
     ESTABLISHED         ESTABLISHED              PARTIALLY SUPPORTED
                                                  (absorbed into C1)
                                                        │
        ┌───────────────────────────────────────────────┘
        ▼
  C3 +epistemic state ────▶ C4 evidence-conditioned routing ────▶ C5 non-bypassable
     NOT JUSTIFIED              DEFERRED                            authorization
     (framing is more                                               DEFERRED
      parsimonious)                                          (deferred ≠ disproven)

  RQ-4 closed at the behavioral-association level; causality not established.
  The framing association (Ch. 6.3) motivated the randomized pilot of Ch. 9.
```

### 6.3 RQ-4 conclusion

**RQ-4 is closed at the behavioral-association level.** Structured evidence is associated with reliable revision activation; adherence is probabilistic, task- and framing-dependent; **causality is not established by the ladder**. The observed broad-vs-narrow framing association (broad framing was associated with higher adherence than narrow framing in the earlier single-model series) motivated the dedicated randomized pilot of Chapter 9 rather than being promoted to a causal claim.

---

## Chapter 7 — Cross-Authority Operation: RQ-5 and the Authority-Divergence Result

### 7.1 Design

PILOT-002: 2 tasks (T1, T2) × 2 authorities (Ṛta, OpenSTA) × 2 replications = 8 trials, counterbalanced authority order, shared initial SDC per task, per-authority revised candidates permitted to diverge.

### 7.2 Execution

8/8 trials completed; 0 failures; 0 retries; 22 oracle evaluations → 22 evidence artifacts (PILOT-002).

### 7.3 The authority-divergence result

On T2, the same artifact class produced **ACCEPT from Ṛta and REJECT from OpenSTA**. Both verdicts were correct in their own property: the constraint set was structurally acceptable while the timing evaluation — under a frozen, deliberately unmeetable clock and a vacuous-clean initial floor — exposed a real timing violation. The "WORSE" metric on T2 reflects the first real constraints exposing a violation under an unmeetable frozen clock, **not model harm**.

This is the thesis's most consequential descriptive finding: **authority divergence is the expected behavior of correct authorities with different evaluation semantics, observed here as a single frozen existence proof (T2).** Within its Level-2 boundary it demonstrates concretely why single-authority verification is insufficient in property-plural domains, and why the evidence contract must preserve (not erase) authority-specific semantics — Chapter 4's Property 2 exists because of this observation. Generalization beyond the tested authority pair is not claimed (Chapter 11). **This is explicitly not prevalence evidence:** one observed divergence establishes that heterogeneous authorities *can* legitimately disagree on the same artifact; it does not measure how often, and no prevalence or rate claim is made.

### 7.3.1 Divergence figure

```
Figure 7.1 — The T2 authority-divergence existence proof.

                          same artifact class (T2)
                                   │
              ┌────────────────────┴────────────────────┐
              ▼                                         ▼
   ┌─────────────────────┐                   ┌─────────────────────┐
   │  O₁ Ṛta             │                   │  O₂ OpenSTA         │
   │  property:          │                   │  property:          │
   │  constraint quality │                   │  timing effect      │
   │  verdict: ACCEPT    │                   │  verdict: REJECT    │
   └─────────────────────┘                   └─────────────────────┘
        both verdicts correct in their own property

   Structural cause: frozen unmeetable clock + vacuous-clean initial
   floor → timing evaluation exposes a real violation that structural
   checks cannot see. Not a failure mode: expected behavior of correct
   authorities with different semantics (existence proof; Ch. 11.7).
```

### 7.4 RQ-5 conclusion

**RQ-5 is closed at Level-2 descriptive evidence:** the EGER loop operated faithfully with two independent deterministic authorities under frozen synthetic VLSI conditions; authority separation is empirically motivated. No claim is made that the authorities are interchangeable or that the loop generalizes to arbitrary authorities.

---

## Chapter 8 — Model Comparison: P185

### 8.1 Design and execution

2 models (mimo baseline; nemotron comparison) × 2 tasks × 2 authorities × 2 replications = 16 planned trials. **15 completed; 1 failed (documented baseline-model output failure under the frozen bounded-retry policy); 3 retries; 43 oracle evaluations → 43 evidence artifacts; identity audit ok=True, 0 violations.** Gate outcomes across the 43 evaluations: **11 ACCEPT, 12 REJECT.**

### 8.2 Findings (descriptive)

- The architecture operated with **both tested models** under identical frozen authorities — an additive second-model observation, not model independence. Of the 8 design replication cells, 5 agreed across replications.
- Model-dependent operational behavior was observed: mimo exhibited an intermittent conversational-filler failure mode (4 of 17 model invocations across its trials); nemotron did not (0 of 10). This is an honest recorded observation under this sampling — not a stable trait of either model.
- No qualitative model×authority inconsistency was observed in the reported run; this is descriptive and does not establish causal model×authority interaction or model superiority.

### 8.3 Boundary

Two models demonstrate operation under an additional tested model. Model independence, statistical superiority/equivalence, and population-level generalization are **not established** — and the AutoChip model-dependence finding (EDA feedback benefiting only GPT-4o among four models) independently corroborates that model dependence of feedback benefit is a real phenomenon worth controlled study.

---

## Chapter 9 — The Causal Framing Pilot: P191-R4

### 9.1 Motivation and design

The ladder left a specific causal question open: does task framing *cause* the observed adherence difference? A pre-registered randomized blocked pilot was designed (P191-R2 frozen protocol; P191-S causal-identification audit; P191-R3 immutable manifest), then executed under explicit authorization (P191-R4).

Design: 3 tasks × 2 framings — A1 broad ("generate a complete, production-quality SDC") vs A4 narrow (task-specific objective only) — × 8 runs per cell = **48 scheduled runs**. Model: mimo (MODEL-005), temperature 0.0. Authority: Ṛta only (the causal question determines the design; introducing a second authority would have added a factor without serving the estimand). Manifest frozen before first invocation: seed 20260908, task order BENCH2-002 → BENCH2-004 → BENCH2-005, per-task randomized A1/A4 sequences, SHA-256 recorded. No retries, no replacement, no early stopping, no extension.

### 9.1.1 Pilot design figure

```
Figure 9.1 — P191-R4 randomized blocked design (frozen before execution).

  manifest seed 20260908 · SHA-256 8350e351…ba890 · frozen BEFORE first invocation
  ┌───────────────────────────────────────────────────────────────────┐
  │ task block 1: BENCH2-002   block 2: BENCH2-004   block 3: BENCH2-005 │
  │   8 × A1  8 × A4           8 × A1  8 × A4         8 × A1  8 × A4     │
  │   (within-block A1/A4 run order randomized; 48 scheduled runs)       │
  └───────────────────────────────────────────────────────────────────┘
        │ each run: mimo (MODEL-005, temp 0.0) → Ṛta → revision → V
        ▼
  SUCCESS = 1 iff COMPLETED ∧ set_input_delay ∧ set_output_delay (else 0,
  including INCOMPLETE — unconditional estimand, no post-treatment conditioning)
        │
        ▼
  RD_task per block → RD_equal = mean → exact blocked permutation test
  (12,870 relabelings/block; exact rational convolution; 2.13×10¹² paths)

  Result: RD_equal = +1/3; one-sided exact p = 0.16265286 → non-rejection.
```

### 9.2 Outcomes

Primary outcome (frozen, unconditional): SUCCESS = 1 iff status COMPLETED ∧ revised SDC contains both `set_input_delay` and `set_output_delay`; INCOMPLETE runs contribute 0.

| Task | A1 SUCCESS | A4 SUCCESS | RD_task |
|---|:---:|:---:|:---:|
| BENCH2-002 | 7/8 | 5/8 | +0.250 |
| BENCH2-004 | 8/8 | 5/8 | +0.375 |
| BENCH2-005 | 7/8 | 4/8 | +0.375 |

- **RD_equal = +1/3 ≈ +0.333** (equal-task-weighted mean).
- **Primary inference:** exact blocked permutation test of RD_equal — exhaustive within-task relabeling (12,870 per task), exact rational convolution (2,131,746,903,000 enumerations, deterministic, no common-effect assumption). **One-sided exact p = 0.16265286**; two-sided descriptive p = 0.32530572.
- Accounting: 48 scheduled; **46 completed; 2 incomplete** (provider timeouts, retained, SUCCESS = 0).
- Secondary (completed-only conditional success rates, explicitly non-causal descriptives): aggregate +0.4167; A1 conditional success 22/22 completed runs.

### 9.3 Execution integrity

An initial execution attempt was aborted for an infrastructure failure (a Windows subprocess timeout-reaping defect that hung the runner); partial artifacts were preserved and excluded from the cohort; the full frozen manifest was re-executed in a single pass with a runner-local process-tree-termination fix only — no protocol parameter changed. The abort is documented; the cohort is clean.

### 9.4 Interpretation

> Under the tested model, frozen synthetic VLSI tasks, frozen framing manipulations, and deterministic evaluation conditions, the causal pilot observed a **positive-direction but non-significant** framing effect on the pre-specified outcome (RD_equal = +0.33, exact one-sided p ≈ 0.16). The evidence is insufficient to reject the null at conventional significance levels at this pilot N. **Framing causality is not established**; the direction is consistent across all three task blocks and concordant with the earlier association-level observation, which is precisely why the question remains open at adequate sample size rather than closed by either a premature causal claim or a premature null claim.

---

## Chapter 10 — Discussion

### 10.0 Evidence-status summary figure

```
Figure 10.1 — What the evidence establishes, and what it does not.

  ESTABLISHED (association / descriptive, tested conditions)
  ├─ C1: structured evidence ↔ reliable revision activation ....... Ch. 6
  ├─ C3: epistemic machinery not justified; framing parsimonious .. Ch. 6
  ├─ RQ-5: two authorities each drive faithful loops .............. Ch. 7
  └─ P185: second model operates under identical authorities ...... Ch. 8

  EXISTENCE PROOF (single frozen observation; not prevalence)
  └─ T2: authorities legitimately diverge on the same artifact .... Ch. 7

  ARGUED + MOTIVATED (not demonstrated as universal law)
  └─ authority separation structurally required in property-plural
     domains (architectural argument + T2 motivating proof) ...... §4.4

  OPEN (positive direction, non-significant)
  └─ framing → adherence causality: RD_equal = +1/3, p = 0.163;
     question remains open at adequate scale ..................... Ch. 9

  NOT ESTABLISHED (explicit non-claims, K6)
  └─ model independence · superiority · Oracle interchangeability ·
     arbitrary-authority generalization · universal/production claims
```

### 10.1 What the aggregate evidence shows

Across four investigations, one result recurs: **the structure of the verifier matters more than the presence of a verifier.** The ladder shows feedback must be structured to be reliably actionable (C1) but that adding epistemic machinery without evidence does not help (C3). The cross-authority pilot shows that even correct verifiers legitimately disagree when correctness is property-plural — so the loop must carry authority semantics, not erase them (RQ-5). The model comparison shows the loop's benefit is model-dependent in ways that demand controlled study, not assumption (P185; corroborated by AutoChip's independent finding). The causal pilot shows that even the behavioral signal's cause — framing — resists confirmation at honest pilot scale (P191-R4).

### 10.2 Generator–verifier control in property-plural domains

The thesis's central intellectual claim is the adaptation argument of §4.4. In kernel-verifiable domains, correctness has one decidable semantics and a single final checker is the whole story. Engineering artifacts like SDC are property-plural: correctness is a conjunction of dimensions evaluated by different deterministic tools with different semantics. In such domains:

- the observed authority divergence provides an empirical existence proof of a condition under which a single-authority verification loop cannot establish property-complete correctness (Ch. 7);
- evidence must be normalized **without collapsing** authority semantics (the typed evidence contract);
- acceptance must be separated from both proposal and evaluation (VerificationGate finality);
- and the resulting system's behavior is an empirical question that requires controlled, randomized methodology — because the obvious behavioral confounds (framing, model choice) are real (Ch. 8–9).

EGER is the minimal architecture satisfying these requirements, and this thesis is its first controlled empirical characterization.

A terminological defense before the examiner asks: the EGER implementation is an engineering artifact; the research contribution is the **controlled investigation** of generator–verifier behavior under property pluralism — the authority-divergence existence result, the negative findings (C3, the non-significant pilot), the model-dependence observations, and the randomized methodology that produced them. The architecture is the instrument of the investigation, not the investigation itself.

### 10.3 Relation to the agentic-EDA agenda

The handoff-validity survey (Liu et al., 2026) provides the field-level vocabulary — acceptance conditions, evidence, provenance — and names multi-property validity as open. EGER is best read as an **intra-loop, experimentally validated realization** of one node of that agenda (Stage-Bound generate–repair), strengthened by the two elements the agenda proposes but does not implement: a typed multi-authority evidence contract and a non-bypassable final gate. The relationship is complementary: the survey maps the territory; this thesis contributes a controlled point within it.

### 10.4 Why the negative results are load-bearing

C3's rejection and the non-significant pilot are not noise; they are what makes the positive claims credible. A program that reports only confirmations would leave the ladder's parsimony argument (framing over epistemic machinery) unsupported and would make the causal claim unfalsifiable-in-practice. The frozen decision rule — the pilot's result, whatever it is, is the evidence — was applied, and the result was a disciplined non-rejection.

### 10.5 Practical significance

For EDA practice, the results suggest a concrete pattern: LLM-proposed constraints are most safely used inside an authority-separated loop in which (i) a constraint-quality authority checks structure, (ii) a timing authority checks effect, (iii) their evidence is presented to the model without merging, and (iv) a final gate — not the model, not a single authority — decides. This is implementable with existing tools and is the engineering payoff of the thesis independent of any generalization claim.

---

## Chapter 11 — Limitations

1. **Scale.** The causal pilot uses N=8 per task×condition cell; its non-significant result cannot rule out effects of the observed magnitude. The ladder and pilots are small-N descriptive studies.
2. **Synthetic tasks.** All tasks are synthetic 3-cell scenarios with frozen metadata; external validity to production designs is not established.
3. **Two models.** Both LLMs are provider free-tier models; model independence and population-level claims are unsupported.
4. **Two authorities.** Ṛta and OpenSTA do not span the space of deterministic engineering authorities; arbitrary-authority generalization is unclaimed. Additionally, **Ṛta is a self-developed rule authority within this research program**, whereas OpenSTA is an established external tool; the scientific weight of cross-authority claims rests on determinism, version pinning, read-only operation, semantic distinctness, and independent execution from the proposal process — not on institutional independence (cf. §5.3).
5. **One non-significant causal pilot.** Framing causality remains open; no causal claim is made anywhere.
6. **Descriptive core.** C0–C5, RQ-5, and P185 are descriptive/association-level; only the pilot uses inferential statistics, and it does not reject its null.
7. **Authority-specific semantics.** Findings about divergence are specific to the two authorities' properties; other authority pairs may behave differently.
8. **Bounded revision.** All conclusions hold under frozen revision/retry budgets; unbounded settings are unexplored.
9. **Literature-audit boundaries.** The novelty freeze carries an as-of date (2026-09-09). The P194-R3 documented database sweep (Semantic Scholar API — rate-limited; indexed ACM DL / IEEE Xplore records via logged query strings; citation chaining) found no occupant of the frozen gap; formal PRISMA-grade screening with institutional databases remains a submission-time condition (F2, narrowed), and F1 is **substantially resolved** (abstract/near-primary + related-full-text level) with original full-text direct inspection still outstanding.
10. **Single-study domain.** SDC is one artifact class; the property-plural argument is argued generally but tested on one domain.

---

## Chapter 12 — Reproducibility

### 12.1 What the repository provides

- Implementation (`eger/`) with the deterministic layers and their regression suite (878/878 at release `28777b2`).
- Frozen task definitions, schemas, contracts, and architecture records (`research/`).
- All protocol records, gate records, and change records (P001–P193), including adversarial review and audit records.
- `research/REPRODUCIBILITY.md`: environment, authorities (Ṛta 1.5.11 @ commit; OpenSTA 2.2.0), model identifiers, matrices, retry policies, outcome definitions, qualified-accept rules.
- `research/paper/EGER-RESEARCH-TECHNICAL-REPORT-001.md`: the released technical report synchronized with all experimental records.

### 12.2 What is intentionally local

Raw experimental records (PILOT-001–004 raw trials, analyses, execution logs, attempt-1 partial artifacts) remain **local-only and private** by policy. The published records cite them by manifest path. This is a deliberate boundary: identity-auditable provenance without exposing raw provider interactions.

### 12.3 Reproduction expectations

From the repository: the implementation, its tests, the frozen designs, and every documented protocol parameter — sufficient to re-execute studies under one's own provider configuration. Bit-for-bit reproduction of raw trials requires the local artifacts and provider environment and is not claimed. The causal pilot's manifest (seed 20260908; SHA-256 `8350e351…ba890`) makes its randomization exactly reconstructible.

---

## Chapter 13 — Conclusions

1. EGER establishes a **concrete, tested architecture** for evidence-grounded engineering reasoning: proposal authority, heterogeneous deterministic evaluation authorities normalized through a semantics-preserving evidence interface, bounded revision, and a sole non-bypassable verification authority.
2. **Authority separation is empirically motivated, not incidental:** two correct deterministic authorities legitimately diverged on the same artifact because they evaluate different properties (the T2 existence proof). This observation is the architectural implication the EGER design encodes: in property-plural domains, a single-authority verification loop cannot by itself establish property-complete correctness.
3. The framework **operated with two deterministic authorities and two tested models** under frozen synthetic VLSI conditions — a bounded, Level-2 descriptive result.
4. Task framing shows a **positive-direction, non-significant** causal-pilot effect on error adherence; causality is not established and remains an open question at adequate scale.
5. The contribution, positioned against the 2026 literature, is the **integration and controlled empirical characterization** of these mechanisms — explicitly not the loop, not SDC generation, not the evidence-contract term, not provenance modeling.
6. All claims are bounded by explicit non-claims; negative and non-significant results are preserved as evidence.

---

## Chapter 14 — Future Research

Sequenced by what the evidence says is most informative first; each item is a candidate for supervised research, not a commitment:

1. **Adequate-scale causal study of framing** (the open question the pilot leaves): power from pilot-estimated effect ranges, multi-model replication, pre-registered confirmatory analysis.
2. **A third authority with a third property** (e.g., coverage or power intent): tests the property-plural architecture where the divergence structure is richer than pairwise.
3. **Production-substrate transfer:** real designs, vendor STA, industrial constraint corpora (LLM4SDC's benchmark is a natural evaluation partner).
4. **Model-dependence characterization:** the convergent AutoChip/EGER observations motivate a controlled study of *which models benefit from which authority types*.
5. **Formalization:** the P/E/R/V model of §4 admits properties (non-bypassability, evidence preservation) that may be provable as invariants of the implementation.
6. **Beyond SDC:** the architecture is artifact-agnostic; testlets on other property-plural engineering artifacts (linker scripts, build configs, test plans) would test the generality of the adaptation argument.

Per the frozen publication decision (P192, Path B): the experimental phase of this thesis is complete; items above belong to future supervised research.

---

## References

*(Final bibliography. All items verified against primary or near-primary sources as of 2026-09-09; author lists completed where verified — see the P194-R3 submission-integrity audit. Refs 12 and 15 carry venue-only identifiers because no public arXiv/DOI record exists for them; no identifier has been invented. Freeze Conditions F1–F3 remain attached submission conditions, recorded in §3.1 and Chapter 11.)*

1. Madaan, A., et al. "Self-Refine: Iterative Refinement with Self-Feedback." NeurIPS 2023. arXiv:2303.17651.
2. Gou, Z., et al. "CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing." ICLR 2024. arXiv:2305.11738.
3. Huang, J., et al. "Large Language Models Cannot Self-Correct Reasoning Yet." ICLR 2024. arXiv:2310.01798.
4. Kamoi, R., Zhang, Y., Zhang, N., Han, J., Zhang, R. "When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs." TACL 12, 2024. arXiv:2406.01297. ACL Anthology 2024.tacl-1.78.
5. Shinn, N., et al. "Reflexion: Language Agents with Verbal Reinforcement Learning." NeurIPS 2023. arXiv:2303.11366.
6. Dhuliawala, S., et al. "Chain-of-Verification Reduces Hallucination in Large Language Models." 2023. arXiv:2309.11495.
7. Tsai, Y.-D., Liu, M., Ren, H. "RTLFixer: Automatically Fixing RTL Syntax Errors with Large Language Models." DAC 2024. arXiv:2311.16543.
8. Blocklove, J., et al. "Automatically Improving LLM-based Verilog Generation using EDA Tool Feedback (AutoChip)." TODAES 2025. arXiv:2411.11856.
9. Cui, F., et al. "OriGen: Enhancing RTL Code Generation with Code-to-Code Augmentation and Self-Reflection." 2024. arXiv:2407.16237.
10. Mashnoor, N., et al. "TimelyHLS: LLM-Based Timing-Aware and Architecture-Specific FPGA HLS Optimization." 2025. arXiv:2507.17962.
11. Nainani, J., Ho, C.-T., Dhurka, A., Ren, H. "Timing Analysis Agent: Autonomous Multi-Corner Multi-Mode (MCMM) Timing Debugging with Timing Debug Relation Graph." 2025. arXiv:2504.11502.
12. Han, P., Lu, Y., Liu, H., Liu, F., Yao, X., Ye, Y. "LLM4SDC: Leveraging Multi-Agent System for Automated SDC Generation and Benchmarking." DAC 2026.
13. Liu, J., Han, P., Lu, Y., Zheng, S., Yan, F., Yu, B. "Agentic Electronic Design Automation: A Handoff Perspective." 2026. arXiv:2606.19795.
14. Xu, R., Li, G., Sheng, V.S. "GAVEL: Evidence-Contract Debate with Mechanized Scrutiny for Provenance-Grounded Fact-Checking." Findings of ACL 2026, pp. 35907–35920.
15. Elsayed, S. "LLM-Augmented FPGA Timing Closure: Toward Intelligent Static Timing Analysis Agents." Architecture 2.0 Workshop @ ASPLOS 2026. The framework introduced by this work is referred to as **TIMINGLLM** in the associated materials; this citation refers to the paper/presentation, not to a separate system entry. Publisher-adjacent material (March 2026) characterizes it as an LLM+RAG pipeline for timing-violation diagnosis and automated fix recommendation, evaluated on 12 production-representative FPGA designs — 658 timing violations (extended to 1,200 in extended evaluation; 20% cross-domain degradation) — with 82% F1 root-cause classification and 56% average WNS reduction from LLM-generated constraint fixes. A related full-text study by the same author reports the pipeline in detail: extraction from STA reports, `.xdc`/`.sdc` constraints, and netlists; retrieval from an FPGA knowledge base; LLM-generated `.xdc` patches; validation by replaying violations through Quartus Prime STA with and without the patches. TIMINGLLM is therefore clear prior art for LLM-assisted STA diagnosis and LLM-generated timing-constraint fixing, within a **single timing-analysis authority / timing-closure workflow** — not the EGER combination. F1 status: **substantially resolved at abstract/near-primary + related-full-text level; original full-text direct inspection still outstanding.**
16. W3C. "PROV Model Primer." W3C Recommendation.
17. Liu, M., et al. (NVIDIA). "VerilogEval: Evaluating Large Language Models for Verilog Code Generation." ICCAD 2023 (Invited). arXiv:2309.07544. DOI 10.1109/ICCAD57390.2023.10323812.
18. Liu, M., et al. "ChipNeMo: Domain-Adapted LLMs for Chip Design." 2023. arXiv:2311.00176.
19. Zhong, R., et al. "LLM4EDA: Emerging Progress in Large Language Models for Electronic Design Automation." 2024. arXiv:2401.12224.
20. Yao, S., et al. "ReAct: Synergizing Reasoning and Acting in Language Models." ICLR 2023.
21. Internal EGER records: P133–P193 gate/change records; `research/STATE.md`; `research/REPRODUCIBILITY.md`; `research/paper/EGER-RESEARCH-TECHNICAL-REPORT-001.md`; P193/P193-R1/P193-R2 literature-audit records.

---

## Appendix A — Frozen Protocols (summary)

- **PILOT-002 (RQ-5):** 2 tasks × 2 authorities × 2 replications; counterbalanced; shared initial SDC; PO-1/2/3 outcome family; 0 retries.
- **PILOT-003 (P185):** 2 models × 2 tasks × 2 authorities × 2 replications; ≤1 bounded retry; identity audit mandatory.
- **PILOT-004 (P191-R4):** 3 tasks × 2 framings × 8; manifest seed 20260908, SHA-256 `8350e3519b00ab24373e7a57e04c38df5bc3657b935f50db56101880c50ba890`; no retries/replacement/early stopping/extension; unconditional SUCCESS estimand; exact blocked permutation inference.

## Appendix B — Evidence and Artifact Schemas

Typed artifact family (`eger.candidate.v1` / `eger.raw.v1` / `eger.evidence.v1`); evidence artifacts preserve authority identity, property scope, and per-finding severity; hash trio + timestamp-as-provenance; identity audit verifies evaluated bytes == recorded bytes. See `research/schemas/`.

## Appendix C — Task Definitions

BENCH2-002 (generated clock), BENCH2-004 (false path), BENCH2-005 (multicycle): design contexts, initial SDCs, and hashes as frozen in the manifest and `research/experiments/EGER-BENCH-002/`.

## Appendix D — Statistical Derivations

Exact blocked permutation test of RD_equal: per-task exhaustive relabeling distribution (C(16,8) = 12,870), combined by exact rational convolution over the three task distributions; one-sided p = P(RD_equal^perm ≥ RD_equal^obs) under H0; Clopper–Pearson intervals for completed-cell rates. Derivation and implementation: `research/experiments/EGER-RQ5-PILOT-004/perm_test_rd_equal.py` (local).

## Appendix E — Provenance and Manifests

Manifest contents (seed, order, assignments, hashes, versions, commit), attempt-1 abort record, attempt-2 cohort definition, and raw-data boundary policy: see `research/REPRODUCIBILITY.md` and the local pilot records.

---

*End of thesis (EGER-THESIS-001, Version A — Final Submission Package v1.0). Status: **final submission status** — research content frozen at Draft 003 (P194-R3); presentation finalized per P195/P197; Freeze Conditions F1–F3 remain attached submission conditions.*
