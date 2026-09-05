# EGER — P182: Future Research Direction & Research-Question Gate

## 1. Objective

Select and stress-test the next research question for the EGER project, treating P181 as the authoritative frozen baseline. Evaluate all P181 candidate directions against 14 assessment criteria, identify the largest remaining uncertainty, and determine whether any direction is sufficiently justified for a future design gate.

**Research-question selection only.** No experiment was run. No code was modified.

## 2. Frozen Baseline (from P181)

```
C0  ESTABLISHED
C1  ESTABLISHED
C2  PARTIALLY SUPPORTED
C3  NOT JUSTIFIED
C4  DEFERRED
C5  DEFERRED

RQ-4  CLOSED — behavioral association (framing → adherence), causality NOT established
RQ-5  CLOSED — Level 2 (descriptive pilot), authority separation demonstrated

Interchangeability       NOT ESTABLISHED (refuted on T2)
Generalization           NOT ESTABLISHED
Causal inference         NOT ESTABLISHED
Model dependence         NOT ESTABLISHED
Task dependence          NOT ESTABLISHED
Scale dependence         NOT ESTABLISHED
```

## 3. Remaining Major Uncertainties

Ranked by scientific impact and unresolved status:

| Rank | Uncertainty | Current Status | Why It Matters |
| ---- | ----------- | -------------- | -------------- |
| 1 | **Model dependence** | NOT ESTABLISHED | Only MODEL-005 (opencode/mimo-v2.5-free) tested. If the architecture only works with one LLM, its value is model-specific, not architectural. |
| 2 | **Task dependence** | NOT ESTABLISHED | Only 2 synthetic 3-cell tasks tested. Authority-separated results may be task-specific. |
| 3 | **Revision-feedback confounding** | PARTIALLY ADDRESSED | RQ-5 used feedback-driven revision per arm; revised candidates diverge across Oracles by design. The paired-generation design would address this but requires protocol redesign. |
| 4 | **Scale dependence** | NOT ESTABLISHED | Synthetic 3-cell substrate only. Production VLSI behavior unknown. |
| 5 | **Framing causality** | NOT ESTABLISHED | RQ-4 found behavioral association (A1 = 100% vs A4 = 67%) but not causation. |
| 6 | **Model-interior mechanism** | NOT ESTABLISHED | Only behavioral outcomes measured; no internal state observation. |

## 4. Candidate Direction Assessment

### Candidate 1: Production-Scale RQ-5 Replication

| Criterion | Assessment |
| --------- | ---------- |
| Research question clarity | Clear: "Does the EGER architecture operate with multiple Oracles on production VLSI designs?" |
| Scientific novelty | Moderate — extends RQ-5 to realistic scale |
| Connection to existing evidence | Direct — tests Level-2 claim at production scale |
| Unresolved limitation addressed | Scale dependence |
| Experimental unit | One trial = one EGER pipeline execution on a production design |
| Independent variable | Oracle authority (Rta vs OpenSTA) |
| Dependent variables | PO-1, PO-2, PO-3 (same as RQ-5) |
| Controls | Same model, same tasks, same protocol |
| Sample size | N ≥ 8 (same as RQ-5 or larger) |
| Measurement validity | Same as RQ-5 — already validated |
| Feasibility | **LOW** — requires new production substrates (real netlists, Liberty, SDCs), potentially new Oracle adapters, new validation |
| Expected information gain | HIGH if positive; HIGH if negative (architecture doesn't scale) |
| Risk of repeating RQ-5 | LOW — genuinely different scale |
| Distinguishes competing explanations | Tests scale as the limiting factor |
| Maximum defensible claim | Level 2 at production scale |
| Required engineering | Significant: new substrates, possibly new adapters, new validation |

**Verdict: HIGH scientific value, LOW feasibility.** The engineering burden is substantial — new production substrates, new Liberty files, new SDCs, new validation. This is a major research program, not a pilot extension.

### Candidate 2: Multi-Task RQ-5 Expansion

| Criterion | Assessment |
| --------- | ---------- |
| Research question clarity | Clear: "Do authority-separated results generalize across diverse VLSI task families?" |
| Scientific novelty | Moderate — adds task diversity |
| Connection to existing evidence | Direct — tests task dependence |
| Unresolved limitation addressed | Task dependence |
| Experimental unit | One trial = one EGER pipeline execution on one task |
| Independent variable | Oracle authority × task family |
| Dependent variables | PO-1, PO-2, PO-3 |
| Controls | Same model, same Oracles |
| Sample size | N ≥ 8 per task family |
| Measurement validity | Same as RQ-5 |
| Feasibility | MODERATE — requires new synthetic tasks (still 3-cell substrate, different SDC scenarios) |
| Expected information gain | MODERATE — adds task diversity but still synthetic |
| Risk of repeating RQ-5 | MODERATE — same architecture, same Oracles, different SDCs |
| Distinguishes competing explanations | Tests task as the limiting factor |
| Maximum defensible claim | Level 2 across task families |
| Required engineering | Moderate: new task definitions, new SDCs, new substrate variants |

**Verdict: MODERATE scientific value, MODERATE feasibility.** Adds task diversity but remains synthetic. The engineering burden is manageable (new SDC scenarios on the same substrate), but the scientific value is incremental rather than transformative.

### Candidate 3: RQ-4 Causal Investigation

| Criterion | Assessment |
| --------- | ---------- |
| Research question clarity | Clear: "Does task framing causally determine ERROR adherence?" |
| Scientific novelty | HIGH — addresses the most important RQ-4 limitation |
| Connection to existing evidence | Direct — RQ-4 found behavioral association, not causation |
| Unresolved limitation addressed | Framing causality |
| Experimental unit | One trial = one model invocation with one framing condition |
| Independent variable | Task framing (broad vs narrow) |
| Dependent variable | ERROR adherence |
| Controls | Same model, same tasks, same evidence |
| Sample size | N ≥ 24 per condition (matching RQ-4 scale) |
| Measurement validity | Established in RQ-4 |
| Feasibility | HIGH — existing harness, existing tasks, existing Oracles |
| Expected information gain | HIGH — either establishes causation or confirms it's unmeasurable |
| Risk of repeating RQ-5 | ZERO — completely different research question |
| Distinguishes competing explanations | Directly tests framing vs other explanations |
| Maximum defensible claim | Causal claim (if design is adequate) |
| Required engineering | Minimal: reuse existing C1/C2 harness |

**Verdict: HIGH scientific value, HIGH feasibility.** This addresses the most important limitation in the RQ-4 evidence base. The existing harness and tasks can be reused with minimal modification. A controlled experiment isolating framing effects (with model randomization, counterbalancing, and sufficient N) could establish or refute framing causality.

### Candidate 4: Paired-Generation RQ-5 Design

| Criterion | Assessment |
| --------- | ---------- |
| Research question clarity | Clear: "Does the architecture produce convergent outcomes when both Oracles evaluate identical candidates?" |
| Scientific novelty | HIGH — eliminates revision-feedback confound |
| Connection to existing evidence | Direct — addresses RQ-5 confounder |
| Unresolved limitation addressed | Revision-feedback confounding |
| Experimental unit | One trial = one candidate evaluated by both Oracles |
| Independent variable | Oracle authority |
| Dependent variables | Oracle verdict, evidence type |
| Controls | Same candidate bytes (byte-identical across arms) |
| Sample size | N ≥ 8 candidate×Oracle pairs |
| Measurement validity | Established in RQ-5 |
| Feasibility | MODERATE — requires protocol redesign (decouple generation from Oracle feedback) |
| Expected information gain | HIGH — eliminates the most important RQ-5 confounder |
| Risk of repeating RQ-5 | LOW — genuinely different design |
| Distinguishes competing explanations | Isolates Oracle-specific evaluation from revision feedback |
| Maximum defensible claim | Level 2 with confound eliminated |
| Required engineering | Moderate: protocol redesign, harness changes |

**Verdict: HIGH scientific value, MODERATE feasibility.** This is the methodologically cleanest extension of RQ-5. However, it requires a new protocol-design gate and harness modifications, making it more expensive than Candidate 3.

### Candidate 5: Model-Comparison RQ-5

| Criterion | Assessment |
| --------- | ---------- |
| Research question clarity | Clear: "Does the EGER architecture operate with different LLMs under the same task and Oracle conditions?" |
| Scientific novelty | HIGH — addresses model dependence, the most critical untested assumption |
| Connection to existing evidence | Direct — RQ-5 used one model; generalization is untested |
| Unresolved limitation addressed | Model dependence |
| Experimental unit | One trial = one EGER pipeline execution with one model |
| Independent variable | LLM model |
| Dependent variables | PO-1, PO-2, PO-3 |
| Controls | Same tasks, same Oracles, same protocol |
| Sample size | N ≥ 8 per model (matching RQ-5) |
| Measurement validity | Established in RQ-5 |
| Feasibility | HIGH — reuse existing harness, tasks, Oracles; only change model |
| Expected information gain | HIGH — either architecture generalizes across models or it doesn't |
| Risk of repeating RQ-5 | LOW — same protocol but different model; genuinely tests model dependence |
| Distinguishes competing explanations | Isolates model as the variable |
| Maximum defensible claim | Level 2 with model as a second condition |
| Required engineering | Minimal: add a second model to the harness |

**Verdict: HIGH scientific value, HIGH feasibility.** This is the most efficient test of the most critical uncertainty. The existing RQ-5 protocol, tasks, Oracles, and harness can be reused with only a model change. If the architecture works with a second model, the Level-2 claim becomes model-independent. If it doesn't, the architecture's boundaries are precisely identified.

### Candidate 6: Larger-N RQ-5

| Criterion | Assessment |
| --------- | ---------- |
| Research question clarity | Clear: "Are the RQ-5 results reliable across more replications?" |
| Scientific novelty | LOW — adds statistical power to existing design |
| Connection to existing evidence | Direct — extends RQ-5 |
| Unresolved limitation addressed | Statistical reliability |
| Sample size | N ≥ 16 (doubling RQ-5) |
| Feasibility | HIGH — reuse everything |
| Expected information gain | LOW-MODERATE — confirms or weakens existing descriptive results |
| Risk of repeating RQ-5 | HIGH — same design, more data |
| Maximum defensible claim | Level 2 with stronger descriptive support |

**Verdict: LOW scientific value, HIGH feasibility.** Adding replications to the same design provides marginal information gain. The existing N=8 descriptive pilot is adequate for Level 2; larger N would support Level 3 claims but the engineering cost is not justified by the information gain.

## 5. Scientific Value Ranking

| Rank | Candidate | Scientific Value | Feasibility | Net Assessment |
| ---- | --------- | ---------------- | ----------- | -------------- |
| 1 | **Candidate 5: Model-Comparison RQ-5** | HIGH | HIGH | **HIGHEST** |
| 2 | Candidate 3: RQ-4 Causal Investigation | HIGH | HIGH | HIGH |
| 3 | Candidate 4: Paired-Generation RQ-5 | HIGH | MODERATE | HIGH |
| 4 | Candidate 2: Multi-Task RQ-5 Expansion | MODERATE | MODERATE | MODERATE |
| 5 | Candidate 1: Production-Scale RQ-5 | HIGH | LOW | MODERATE |
| 6 | Candidate 6: Larger-N RQ-5 | LOW | HIGH | LOW |

## 6. Methodological Risk Ranking

| Rank | Candidate | Risk of Repeating RQ-5 | Confound Control | Claim Strength |
| ---- | --------- | ---------------------- | ---------------- | -------------- |
| 1 | **Candidate 5: Model-Comparison** | LOW | GOOD (same protocol) | Level 2 (model-general) |
| 2 | Candidate 3: RQ-4 Causal | ZERO | GOOD (controlled design) | Causal (if adequate N) |
| 3 | Candidate 4: Paired-Generation | LOW | EXCELLENT (eliminates confound) | Level 2 (confound-free) |
| 4 | Candidate 2: Multi-Task | MODERATE | GOOD | Level 2 (task-general) |
| 5 | Candidate 1: Production-Scale | LOW | GOOD | Level 2 (scale-general) |
| 6 | Candidate 6: Larger-N | HIGH | SAME | Level 2 (stronger) |

## 7. The Largest Remaining Uncertainty

The P181 synthesis explicitly lists "Generalization beyond MODEL-005" as NOT ESTABLISHED. This is the most critical gap because:

1. **If the architecture only works with one specific LLM, it is a model-specific artifact, not an architectural finding.** The entire P159–P180 research program would be bounded to one model's behavior.

2. **If the architecture works with multiple LLMs, the Level-2 claim becomes model-independent.** This is a qualitative leap in the strength of the evidence base.

3. **Model dependence is the most efficient variable to test.** The existing RQ-5 protocol, tasks, Oracles, and harness require only a model change — no new substrates, no new adapters, no protocol redesign.

4. **The alternative (Candidate 3, RQ-4 causal) is also high-value but addresses a different uncertainty.** Framing causality is important for RQ-4 but does not directly strengthen the RQ-5 evidence base.

**Recommended priority: Candidate 5 (Model-Comparison RQ-5) as the next research-design gate, followed by Candidate 3 (RQ-4 Causal) as a parallel or subsequent investigation.**

## 8. Recommended Research Direction

### Proposed Research Question

> **To what extent does the evidence-grounded EGER architecture operate with different large language models under the same deterministic evaluation authorities and VLSI engineering tasks?**

### Why This Question Is Preferable

1. **Highest information gain per engineering cost.** Reuses the entire P179 infrastructure (harness, tasks, Oracles, protocol) with only a model change.

2. **Addresses the most critical uncertainty.** Model dependence is the single most important untested assumption in the current evidence base.

3. **Clean experimental design.** Same protocol, same tasks, same Oracles — only the model varies. This isolates the model as the independent variable with minimal confounders.

4. **Binary outcome with high stakes.** Either the architecture generalizes across models (strong positive) or it doesn't (precise boundary identification). Both outcomes are highly informative.

5. **Does not repeat RQ-5.** RQ-5 tested Oracle authority variation; this tests model variation. Different independent variable, different research question.

### Preliminary Design Boundaries

- **Protocol:** Reuse P169/P172/P177/P178 frozen protocol (2×2×2 matrix, counterbalanced, bounded retry)
- **Tasks:** Same T1 and T2 from RQ-5
- **Oracles:** Same Rta 1.5.11 and OpenSTA 2.2.0
- **Model:** One additional LLM (different provider/architecture from opencode/mimo-v2.5-free)
- **Primary outcomes:** PO-1, PO-2, PO-3 (same definitions)
- **Claim level:** Level 2 (model-general)
- **Non-goals:** No production scale, no causal investigation, no Oracle comparison, no architecture redesign

## 9. Explicit Non-Goals

- Do NOT test production-scale VLSI designs
- Do NOT investigate framing causality (separate research question)
- Do NOT redesign the paired-generation protocol
- Do NOT modify Ṛta, OpenSTA, or VerificationGate
- Do NOT claim interchangeability, generalization beyond tested conditions, or causal inference

## 10. Maximum Anticipated Claim Level

**Level 2 — model-general.** If the architecture operates with two independent LLMs across both tasks and both Oracles, the claim becomes:

> The evidence-grounded EGER control loop operated with multiple independent deterministic evaluation authorities and multiple independent language models across the frozen synthetic VLSI tasks, under the tested conditions.

This is a qualitative strengthening of the Level-2 claim from RQ-5, making it model-independent.

## 11. Decision

```text
GO — Candidate 5 (Model-Comparison RQ-5) is recommended for a future
research-design gate. It addresses the largest remaining uncertainty
(model dependence) with the highest information gain per engineering cost,
using the existing RQ-5 infrastructure with only a model change.
```

**GO authorizes only a future research-design gate.** It does NOT authorize experimentation. The design gate must freeze the protocol, model selection, and analysis plan before any data collection.

## 12. Research Boundary

```text
RQ-4: CLOSED (unchanged)
RQ-5: CLOSED (unchanged)
C0-C5: UNCHANGED
Rta: UNCHANGED
VerificationGate: UNCHANGED
New experiment executed: NO
New research question designed: NO (only selected)
```

## 13. Tests

- EGER full suite: 878/878 PASS (no code changes)
- Harness suite: 62/62 PASS

## 14. Git

- P182 committed as: `<hash>` (see CHANGE-054)
- HEAD == origin/main (after push)
- No code changes; research records only
- Universal_Principles_Library/ untouched

## 15. Artifacts

- `research/implementation/EGER-P182-FUTURE-RESEARCH-DIRECTION-AND-RQ-GATE-001.md`
- `research/implementation/EGER-CHANGE-054.md`

## STOP

P182 selected a research direction. The next step, when authorized, is a research-design gate for Candidate 5 (Model-Comparison RQ-5). No experiment was run. No protocol was designed. No data was collected.
