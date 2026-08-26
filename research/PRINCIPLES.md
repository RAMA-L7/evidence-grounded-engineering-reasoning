# EGER Principles — Operational Form (P1–P8)

Source of definitions: EGER Research Contract v0.2. This file records how each
principle constrains architecture and experiments. Definitions are frozen;
operational notes evolve only via `EGER-CHANGE-###`.

---

## P1 — No Unverified State Transition

- **Definition:** An agent may propose an engineering change, but may not commit it as verified engineering state without required deterministic verification.
- **Why:** LLM assertions about correctness carry no evidential weight; silent promotion is the root corruption.
- **Architectural implication:** Commit path must pass through a deterministic gate that no probabilistic component can override or route around (filesystem/permission enforcement).
- **Experimental implication:** C5 tests the gate's causal effect; C0–C4 must not silently contain gate-like behavior in prompts.
- **Violation examples:** Agent declares its SDC "verified" after self-review; agent writes to a validated baseline directly.

## P2 — Externalized Epistemic State

- **Definition:** Engineering knowledge must not depend solely on model context. Represent HYPOTHESIS, VALIDATED, REFUTED, UNKNOWN, AMBIGUOUS explicitly.
- **Why:** Context-dependent "knowledge" evaporates, mutates, and cannot be audited.
- **Architectural implication:** On-disk typed claim store + append-only journal owned by a deterministic validator (EGER layer L2).
- **Experimental implication:** Memory OFF in C0–C2, ON from C3 — the toggle IS the treatment.
- **Violation examples:** System "remembers" validation from a prior session without artifact; state exists only in prose.

## P3 — Evidence-Conditioned Reasoning

- **Definition:** Where deterministic evidence identifies a known condition or failure, route behavior through an appropriate procedure instead of unrestricted improvisation.
- **Why:** Free improvisation on known failure classes produces inconsistent, unmeasurable behavior.
- **Architectural implication:** Versioned deterministic routing table keyed by finding codes (C4).
- **Experimental implication:** Routing must be deterministic in C4; an LLM router would add a probabilistic variable inside the routing condition (EGER-DEC-007).
- **Violation examples:** Ignoring a refuted finding and regenerating freely; inventing a repair unrelated to evidence.

## P4 — Executable Engineering Checklist

- **Definition:** Engineering rules should be executable wherever possible; deterministic tools perform checks and produce evidence.
- **Why:** Prose checklists decay into suggestions; executable rules produce machine-checkable findings.
- **Architectural implication:** The oracle (Ṛta rule engine) IS the checklist; EGER adds no prose-only quality gates.
- **Experimental implication:** Oracle configuration frozen per experiment series (custom rules off unless declared).
- **Violation examples:** Treating a narrative review as validation; disabling rules mid-series.

## P5 — Repetition Drives Convergence

- **Definition:** Hypothesis → Oracle Validation → Evidence → Epistemic Update → Next Hypothesis.
- **Why:** Iteration with feedback is the mechanism under study; convergence rate is a dependent variable.
- **Architectural implication:** Every cycle emits typed artifacts sharing a cycle_id — the loop must be observable end-to-end.
- **Experimental implication:** Stopping criteria fixed per experiment definition, never agent discretion.
- **Violation examples:** Undocumented cycles; loop termination by model mood.

## P6 — Explicit Epistemic Boundaries

- **Definition:** Validation by Oracle X must not silently become universal truth. Every evidence source has declared scope.
- **Why:** Scoped findings promoted to universal facts is textbook epistemic corruption.
- **Architectural implication:** Adopt Ṛta's `AnalysisScope` trust statuses (VALIDATED / PARTIALLY_VALIDATED / NETLIST_REQUIRED / UNSUPPORTED / TCL_EXECUTION_REQUIRED) as mandatory fields on every Evidence artifact; the state validator rejects out-of-scope promotions.
- **Experimental implication:** Trust-status distribution is reportable per run.
- **Violation examples:** "Ṛta found no errors ⇒ the design timing is correct"; using PARTIALLY_VALIDATED findings to ground VALIDATED claims.

## P7 — Authority Separation  ★ core new principle

- **Definition:** Proposal, Evidence, Knowledge, and Authorization are distinct system authorities.
- **Why:** This separation IS the primary research question; collapsing authorities destroys the experiment's meaning.
- **Architectural implication:** Separation enforced by deterministic tool boundaries and permissions, NOT by LLM identity or prompt instructions. One LLM can hold Proposal authority while three deterministic layers hold the rest (EGER-DEC-005). A permission system cannot be persuaded; a persona can.
- **Experimental implication:** Any condition where a probabilistic component touches Evidence/State/Authorization write-paths invalidates the run.
- **Violation examples:** Oracle generating candidate SDCs consumed as proposals (`rta_generate`, forbidden by EGER-DEC-006); analyst agent able to edit candidates it certifies; gate accepting natural-language justification instead of evidence references.

## P8 — Research Traceability and Reproducibility  ★ core new principle

- **Definition:** Every material research decision, hypothesis, architecture proposal, experiment, failure, evidence artifact, and conclusion receives persistent provenance. Source-derived claims, agent inferences, hypotheses, observations, results, and conclusions remain distinguishable.
- **Why:** Untraceable research cannot be reviewed, reproduced, falsified, or corrected.
- **Architectural implication:** Canonical documents (`RESEARCH.md`, `PRINCIPLES.md`, `STATE.md`, `RESEARCH_LEDGER.md`, `LITERATURE.md`) + stable ID families (P###, DEC-###, ARCH-###, ORACLE-###, EXP-###, RES-###, FAIL-###, CHANGE-###, HYP-###, LIT-###, EVID-###, MEM-###) + version control + run manifests recording model/oracle/benchmark/config versions.
- **Experimental implication:** No experiment runs without a manifest; superseded artifacts preserved, never deleted.
- **Violation examples:** Decisions living only in chat transcripts (the pre-P004 condition); rewriting history so the process looks linear.

---

## Two Memories Rule

**Research memory** ("what have we learned about EGER?") lives here in
`research/`. **Engineering epistemic memory** ("what does the future EGER system
know about a design?") will live in runtime claim stores. They MUST NOT be
mixed: different owners, formats, lifecycles, and authority chains.
