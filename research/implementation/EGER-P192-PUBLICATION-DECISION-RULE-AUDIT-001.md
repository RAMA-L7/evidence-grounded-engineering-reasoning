# EGER — P192: Publication Decision Rule Audit

> **Status:** REVIEW COMPLETE — Publication decision rule applied against the current frozen evidence package.
>
> **This gate does NOT execute the causal pilot. No model calls. No raw data generated. No commit. No push.**

## 1. Publication decision rule (from project rule)

The project will publish **as soon as the planned research flow is complete and the evidence supports the manuscript's final claims**.

Publication is reached when all of the following are true:

1. The planned causal investigation has reached its defined endpoint, or a documented result establishes that further execution is not scientifically required.
2. The resulting evidence has undergone independent analysis and review.
3. The manuscript's claims have been reconciled with the final evidence and all known limitations.
4. No unresolved methodological or reproducibility blocker remains.
5. The final manuscript and reproducibility package are complete.
6. The final research/release review passes.

**No additional experiment is required merely to extend the project.** Any new research question discovered after this point belongs to a future study rather than delaying publication of the current thesis.

**Publication timing:** publish immediately once this gate passes. The September 30, 2026 date is a target ceiling, not a mandatory waiting date.

---

## 2. The planned causal investigation and its current endpoint

**Planned causal investigation:** P191-R / P191-S / P191-R2 defined a framing-causality pilot designed to test whether broad task framing (A1) causally increases the probability that the model produces a valid, adherent SDC candidate, relative to narrow framing (A4), under frozen MODEL-005, frozen BENCH2-002/004/005 tasks, frozen Ṛta, and frozen N=8-per-cell design.

**Current endpoint status:**

- The causal design is **frozen and implementation-ready** (P191-R2: CAUSAL IMPLEMENTATION-READY).
- The causal pilot has **not yet been executed** (no manifest created; no model calls; no raw data).
- Therefore criterion 1 ("the planned causal investigation has reached its defined endpoint") is **NOT yet satisfied** in the sense of execution + independent review of results.

However, the publication decision rule also allows publication once "a documented result establishes that further execution is not scientifically required." That alternative is **not** claimed here: the framing-causality pilot is scientifically worthwhile (P191/P191-R/P191-S/P191-R2 all agreed the design is sound and implementation-ready), so further execution **is** scientifically required before the causal RQ-4 conclusion can be finalized.

**Implication:** The planned causal investigation is still pending execution. Publication of the *full* manuscript — including a finalized RQ-4 causal conclusion — must wait until the causal pilot completes and is reviewed, **unless** a separate publication decision is made to publish the current evidence package with RQ-4 left explicitly open at the behavioral-association level.

---

## 3. What the current evidence package already supports

The current frozen evidence package (through `928d573`) already includes:

- **C0–C5 / RQ-4:** C0/C1 established; C2 partially supported/absorbed; C3 not justified; C4/C5 deferred; RQ-4 closed at behavioral-association level; causality NOT established.
- **RQ-5:** Level 2 descriptive pilot (PILOT-002, 8/8, 0 failures, 0 retries, 22/22, authority separation demonstrated on T2).
- **Model comparison:** P185 (15/16, 1 documented baseline-model failure, 43/43, 3 retries, identity audit ok=True 0 violations); P186 independent review PASS WITH REVISION (two prose-count corrections).
- **Packaging:** P187/P187-R (documentation gaps closed), P188 (manuscript assembled), P189/P189-R (publication polish + revalidation), P191-R2 (causal design frozen, implementation-ready).
- **Regression:** EGER 878/878, harness 74/74.

The manuscript's **current final claims** (through P188/P189-R) are bounded to:

- EGER establishes a concrete evidence-grounded control-loop architecture.
- Deterministic evaluation evidence can be normalized into a common EGER evidence contract without erasing authority-specific semantics.
- The tested loop operated with two deterministic authorities (Ṛta, OpenSTA) and two tested models (mimo, nemotron) under frozen synthetic VLSI conditions.
- Authority-specific semantics remain important (T2 authority separation, not interchangeability).
- Model independence, statistical superiority, universal generalization, arbitrary-authority generalization, and production-scale validity are NOT established.

These claims are fully supported by the current frozen evidence. They do **not** require the causal pilot to be true.

---

## 4. What the causal pilot would add

If executed and reviewed favorably, the causal pilot would:

- Add a **causal** (not merely behavioral-association) result to RQ-4: broad framing causally increases the probability of the SUCCESS outcome relative to narrow framing, under the tested conditions.
- Strengthen the RQ-4 conclusion from "behavioral association only" to "causal evidence under the tested conditions (pilot)."
- Leave untouched: model independence, RQ-5, P185, authority separation, ARCH-002 unvalidated status, production-scale generalization, arbitrary-authority generalization.

If executed and reviewed unfavorably (no causal effect detected at N=8 per cell), the RQ-4 conclusion would remain at behavioral association, possibly with a documented null pilot result. Either way, the rest of the manuscript would not change.

**Key point:** The causal pilot is about RQ-4 framing causality. It is not required for the rest of the publication's claims.

---

## 5. Reconcile the publication rule with the current state

### Criterion-by-criterion assessment

| # | Criterion | Status | Note |
|---|-----------|--------|-------|
| 1 | Planned causal investigation reached endpoint, or further execution not scientifically required | **NOT YET (execution pending)** | The causal pilot is implementation-ready but not executed. Further execution IS scientifically required if the goal is a finalized causal RQ-4 conclusion. |
| 2 | Resulting evidence undergone independent analysis and review | **PARTIAL** | Current evidence (C0–C5, RQ-5, P185, P186) has been independently reviewed. The causal pilot evidence has NOT yet been generated or reviewed. |
| 3 | Manuscript claims reconciled with final evidence and limitations | **YES (for current claims)** | Current manuscript claims are fully reconciled with the current frozen evidence. If the causal pilot completed and changed RQ-4, the manuscript would need reconciliation. |
| 4 | No unresolved methodological or reproducibility blocker | **YES (for current package)** | No blocker for the current evidence package. The causal pilot design has no unresolved methodological blocker (P191-R2 confirmed implementation-ready). |
| 5 | Final manuscript and reproducibility package complete | **YES (for current package)** | Manuscript at `research/paper/EGER-RESEARCH-TECHNICAL-REPORT-001.md`; reproducibility package at `research/REPRODUCIBILITY.md`; README; STATE.md; all source records present. |
| 6 | Final research/release review passes | **PARTIAL** | P187/P187-R/P188/P189/P189-R passed. A final release review that includes the causal pilot results would be required if the goal is publication with a finalized RQ-4 causal claim. |

---

## 6. Two legitimate publication paths

Given the publication rule, there are two coherent options:

### Path A — Publish now with RQ-4 left open at behavioral-association level

- Publish the current manuscript as-is.
- RQ-4 conclusion remains: "closed at behavioral-association level; causality not established."
- The framing-causality pilot becomes **explicitly future work**, not a publication blocker.
- This is consistent with the rule's statement that "any new research question discovered after this point belongs to a future study rather than delaying publication of the current thesis."
- This path is defensible **if** the project accepts that RQ-4's causal question is not essential to the core publication thesis (which is about the evidence-grounded architecture, authority separation, and two-model operation).

### Path B — Complete the causal pilot, then publish with a finalized RQ-4 conclusion

- Execute P191-R3 (manifest + authorization), run the pilot, independently review the results, reconcile the manuscript, then publish.
- This produces a more complete RQ-4 conclusion (causal pilot evidence, possibly positive, possibly null).
- This is consistent with the rule's criterion 1 (planned causal investigation reaches its endpoint).
- This path delays publication until the pilot completes and is reviewed.

**Which path the project chooses depends on whether RQ-4 framing causality is considered essential to the core publication thesis.** The publication rule does not force either path; it only requires that, whichever is chosen, the evidence supports the manuscript's final claims and the decision rule's criteria are satisfied.

---

## 7. No unresolved blocker remains for the current package

For the current manuscript and evidence package (through `928d573`):

- No unresolved methodological blocker.
- No unresolved reproducibility blocker (reproducibility package complete; raw data intentionally local).
- No unresolved claim-boundary issue (all claims bounded; no overclaim; no model independence; no superiority; no generalization).
- No unresolved Git/release blocker (HEAD == origin/main; publication manuscript finalized at P189-R; no protected files modified; no raw data tracked).

The only "open" item is the **optional** causal pilot, which is a future research question, not a publication blocker for the current thesis.

---

## 8. Decision

**Publication decision rule audit result: The current evidence package satisfies criteria 2–6 for the manuscript's current claims.**

Criterion 1 is the only item that depends on the pending causal pilot, and only if the project chooses to treat RQ-4 framing causality as essential to the publication.

**Therefore:**

- If the project's publication thesis is the current manuscript (architecture + authority separation + two-model operation, with RQ-4 left open at behavioral association), then **the publication decision rule is satisfiable now** and publication does not require the causal pilot.
- If the project wants RQ-4 to carry a causal conclusion, then **publication must wait** for P191-R3 + pilot execution + independent review + manuscript reconciliation.

**No additional experiment is required merely to extend the project.** The causal pilot is optional relative to the current publication thesis; if left as future work, it does not delay publication of the current manuscript.

---

## 9. Recommended explicit decision for the project

Before publication, the project should explicitly decide:

1. **Is RQ-4 framing causality essential to the publication thesis?**
   - If **no**: publish the current manuscript now (Path A). The causal pilot becomes future work.
   - If **yes**: complete P191-R3, execute the pilot, review, reconcile, then publish (Path B).

2. **If Path A:** confirm that the manuscript's RQ-4 wording ("closed at behavioral-association level; causality not established") is the intended final RQ-4 conclusion for publication.

3. **If Path B:** confirm that the project is ready to authorize P191-R3 (manifest creation + pre-execution authorization) and the subsequent pilot execution.

---

## 10. STOP

This gate does **not** execute the causal pilot. No model calls. No raw data. No commit. No push.

**P192 result: Publication decision rule audit complete. The current evidence package is publication-ready for the manuscript's current claims; the only remaining variable is whether the project treats the pending causal pilot as essential to the publication thesis.**
