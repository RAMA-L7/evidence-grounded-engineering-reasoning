# EGER-EXP-001 — Experimental Protocol v0.1

| Field | Value |
|---|---|
| ID | EGER-EXP-001 v0.1 |
| Status | FROZEN (P011 gate) |
| Date | 2026-08-26 |
| Architecture | EGER-ARCH-002 (one probabilistic component) |
| Deterministic base | L1 EGER-ORACLE-CONTRACT-001, L2/L3 EGER-EPISTEMIC-001, schemas EGER-SCHEMA-001 |
| Goal | Test whether progressive authority-separated deterministic grounding improves reliability |

> No C0–C5 runs executed under this protocol. All claims below are **prospective**.

---

## 1. Research Question

> Can engineering-agent reliability be improved by separating the authorities responsible for proposing engineering hypotheses, establishing deterministic evidence, representing evidence-derived epistemic state, and authorizing engineering-state transitions?

The object of study is **authority-separated evidence-grounded engineering reasoning**, not generic LLM text generation. Proxy question "Can an LLM generate better SDC?" is explicitly excluded.

## 2. Hypothesis

**H1 (working hypothesis, falsifiable):** Progressively stronger deterministic grounding and authority separation (C0→C5) can improve artifact reliability, reasoning reliability, and epistemic reliability (reduce epistemic violations and unsupported promotion) without requiring additional probabilistic components.

H1 is **not** claimed true; it is what the experiment is designed to potentially support, remain inconclusive about, or falsify.

## 3. Null / Falsification Position

Results **not** supporting H1 include any of:

- No meaningful difference in primary metrics between conditions (within pre-registered negligible-effect band).
- Deterministic grounding increases tool/model calls without improving reliability.
- EVR does not decrease from C0 to C5 (or increases).
- Authorization reduces throughput without improving correctness.
- Improvements confined to one narrow task subset and absent on held-out tasks.
- Gains disappear under repetition (same condition, same task, multiple runs).
- Gains disappear on held-out evaluation split.
- Deterministic layers introduce more infrastructure failures than they prevent.

The experiment must be able to return **SUPPORT**, **INCONCLUSIVE**, or **FALSIFICATION / NO SUPPORT** — not forced to find improvement.

## 4. Independent Variables

Primary IV: **Degree of authority-separated deterministic grounding**, operationalized as **C0–C5** (see §6). This is the sole treatment variable for the primary experiment.

Excluded as IV for C0–C5: agent count, model identity, benchmark task.

## 5. Dependent Variables

A. **Artifact reliability** — is the resulting SDC technically acceptable under deterministic oracle evaluation?

B. **Reasoning reliability** — does the Engineer respond appropriately to evidence (successful correction, no inappropriate repetition, convergence)?

C. **Epistemic reliability** — does the system correctly represent validated/refuted/unknown/insufficient? (measured via EVR)

Additional: authorization violation rate, convergence rate, tool-call efficiency. See §15–19.

All measured the same way in every condition.

## 6. C0–C5 Definitions

| Condition | Engineer gets as reasoning aid | Deterministic infrastructure still runs for measurement? |
|---|---|---|
| **C0** | Task context only. No feedback. | Measurement only — evidence collected by evaluator, not shown to Engineer |
| **C1** | + textual tool feedback (deterministic oracle output rendered as text) | Same oracle; only text shown |
| **C2** | + structured `EvidenceArtifact` (scope, findings, provenance) | Same oracle/schema |
| **C3** | + `EvidenceArtifact` + read-only `EpistemicState` (hypothesis/validated/refuted/unknown + evidence linkage) | Same oracle+L2 |
| **C4** | + C3 + **deterministic** evidence-conditioned routing (retry/revise/terminate) — no second LLM, no supervisor | Same oracle+L2+routing table |
| **C5** | + C4 + **non-bypassable L3 AuthorizationGate** | Same oracle+L2+L3 |

C6 (specialized subagents, agent count) is **excluded** from the primary causal experiment.

## 7. Capability Matrix (frozen)

| Capability                  | C0 | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|---|
| Candidate generation        | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Text feedback               | - | ✓ | - | - | - | - |
| Structured evidence         | - | - | ✓ | ✓ | ✓ | ✓ |
| Epistemic state (read-only) | - | - | - | ✓ | ✓ | ✓ |
| Deterministic routing       | - | - | - | - | ✓ | ✓ |
| Authorization gate          | - | - | - | - | - | ✓ |

Adding a capability requires a new protocol version (`v0.2`).

## 8. Model Freeze (EGER-MODEL-001)

Frozen for control runs: `FakeEngineerModel` (`fake`/`fake-engineer-v1` v1.0) — deterministic, no network — via `eger/engineer/model.py`. Prompt version `eger.prompt.v1`, context config as in §14. Live-model selection (provider/model/version/temperature/top-p/max-tokens/timeout/retry/budget) is **NOT frozen** for the formal experiment; documented as **PROVISIONAL** with status `NOT FROZEN` in `EGER-MODEL-001.md` and will be frozen as `MODEL-002` before any formal run. P011 passes with this limitation documented (see §27).

## 9. Prompt Freeze (EGER-PROMPT-001)

Frozen: system prompt `eger.prompt.v1` (neutral SDC proposal, “do not claim validated”), task/evidence/epistemic/routing/authorization presentation templates, output format (` ```sdc ` fences or keyword-scanned SDC), extraction rules (`candidate.py`), all versioned and hashed per `EGER-PROMPT-001.md`. No modifications after formal execution without `v0.2` + `EGER-CHANGE-###`.

## 10. Benchmark Freeze (EGER-BENCH-001)

Provisional freeze **v0.1** at P011: **19 artifacts under `rta-constraint-intelligence/samples/`** (15 SDC files + 2 TCL + 1 YAML + 1 dir of variants) — IDs frozen in `EGER-BENCH-001.md` with provenance `Ṛta samples @ 3b5c2f2`. This corpus is an **engineering validation benchmark** — small, not yet adversarial nor held-out in final publication sense. Formal evaluation freeze to a larger, adversarial, held-out corpus will be `BENCH-002` before publication; P011 documents the limitation rather than pretending this small set is definitive.

## 11. Run Protocol

One unit = one task × one condition × one model configuration × one run, producing: candidate(s), `EvidenceArtifact`/`RawEvidence`, `EpistemicTransition`(s), `AuthorizationDecision`(s), tool interaction log, manifest, outcome, failure class. Every run independently traceable via `run_id`.

## 12. Failure Taxonomy (frozen)

`PROPOSAL_FAILURE` (model unavailable/timeout/malformed/missing candidate), `ORACLE_FAILURE`, `INVALID_ARTIFACT`, `INSUFFICIENT_EVIDENCE`, `UNSUPPORTED`, `EPISTEMIC_VIOLATION`, `AUTHORIZATION_REJECTION`, `TIMEOUT`, `ITERATION_LIMIT`, `INFRASTRUCTURE_FAILURE`. Never collapsed to single `FAILED`.

## 13. Termination Policy (frozen)

Per-run caps: `max_iterations = 5`, `max_model_calls = 5`, `max_oracle_calls = 5`, `max_wall_clock = 300s`, `max_candidate_revisions = 4`. A run terminates deterministically at the first limit or on `converged`/`FAILED`. No condition receives unlimited retries.

## 14. Retry Policy (frozen)

- **Technical retry** (allowed, logged): network timeout, provider 5xx, infrastructure crash — does not count as new experimental attempt.
- **Experimental attempt**: any `generate → validate` cycle, including bad SDC. Model-generated bad SDC is **not** a technical retry. No silent retries; every attempt appears in the run manifest.

## 15. Metrics (frozen)

Primary (per §28): artifact reliability, reasoning reliability, epistemic reliability (EVR). Plus authorization violation rate, convergence, tool efficiency (§16–19). Secondary ( §33): time-to-valid, revisions, evidence utilization, repeated-error rate, authorization rejection rate. No promotion of secondary to primary after results.

## 16. EVR (Epistemic Violation Rate)

`EVR = violations / attempted_epistemic_transitions` (numerator/denominator both reported, not EVR alone), computed from `EpistemicEngine.evr()`. Violations are machine-detected typed records ( §44 of P009). **PROVISIONAL** denominator definition per v0.2 contract phrasing `violations / evaluated epistemic claims` — raw counts retained so either denominator can be computed post-hoc. Never changed after results.

## 17. Authorization Violation Rate (AVR)

`AVR = authorization_violations / authorization_attempts`, from `AuthorizationGate.violation_stats()`. Example violations: approval despite `INSUFFICIENT`/`UNSUPPORTED`/non-`VALIDATED` state, bypass attempts. Separate from EVR; never implicitly combined.

## 18. Convergence

A run is `converged` iff it reaches `VALIDATED` epistemic state + `APPROVED` authorization (where applicable for the condition) within the frozen budget. Not “model says correct” — tied to deterministic `evidence_scope=FULL` + no error findings + `SUCCESS`. Record: `converged` (bool), `termination_reason`, `iteration_count`, `oracle_calls`.

## 19. Tool Efficiency

Record per run: `model_calls`, `oracle_calls`, `routing_calls`, `total_tool_interactions`, `wall_clock` (if reliable). Efficiency is a dependent variable, not a reason to alter the protocol.

## 20. Statistical Analysis Plan

- Per-condition aggregates (mean rates, distributions) across tasks × repetitions.
- Per-task outcomes and paired comparisons `C0↔C1 … C4↔C5` plus `C0↔C5` overall.
- Where repetition allows: per-condition confidence intervals and effect sizes (Cohen-type) for primary metrics.
- If sample is small for strong inference (as with BENCH v0.1), the analysis **states the power limitation** rather than inventing a threshold.
- No invented `p < 0.05` gate solely to manufacture a positive finding.

## 21. Anti-Gaming Rules (frozen)

No task removal after results; no selective run removal; no prompt tuning on held-out data; no model switching between conditions; no oracle revision switching; no changing success criteria after execution; no hidden retries; no condition-specific manual repair; no post-hoc metric invention; no cherry-picking; no changing iteration/tool budgets after observing results; no changing evidence presentation; no Ṛta modification; failed runs preserved, never deleted.

## 22. Data Leakage Controls

Engineer must not receive ground-truth answers, evaluation labels, hidden test metadata, or expected validation results. Only explicitly declared read-only evidence/epistemic views per condition are allowed (capability matrix). Benchmark answers never enter the prompt.

## 23. Run Manifests

Every run produces `RunManifest` (frozen schema) with: `run_id`, `experiment_version (EGER-EXP-001 v0.1)`, `condition`, `task_id`, `model configuration` (EGER-MODEL-001), `prompt version`, `oracle revision (3b5c2f2)`, `schema versions`, `random_seed`, `start/end timestamps`, budgets, candidate/evidence/epistemic/authorization hashes, final outcome, failure class. No invisible runs.

## 24. Artifact Retention

Retain per run: model raw output, `CandidateArtifact`, `RawEvidence`, `EvidenceArtifact`, `EpistemicTransition`(s), `AuthorizationDecision`(s), `RunManifest`. No secrets; raw evidence never modified post-execution.

## 25. Falsification Criteria

See §3 plus contract-defined criteria where applicable. H1 is not supported if: C5 does not improve epistemic reliability over predecessor conditions, EVR unchanged across C0–C5, improvements statistically/experimentally negligible, gains only via increased compute/tool budget, failure to reproduce across repetitions, gains vanish on held-out tasks, or deterministic layers introduce more failures than they prevent. No threshold invented merely to sound rigorous.

## 26. Claim Discipline

Before experiment: “hypothesis”, “expected”, “designed to test”, “proposed”. After: “observed”, “measured”, “supported”, “not supported”, “inconclusive”. Forbidden before results: “proves”, “demonstrates superiority”, “solves/eliminates hallucination”.

## 27. Known Limitations

- BENCH v0.1 is small/provisional (15 SDC files from one oracle's samples, not adversarial suite) — formal publication benchmark will be BENCH-002.
- MODEL-001 frozen as deterministic `FakeEngineerModel` for controls; live model configuration (provider/version/temperature) not yet frozen for formal experiment — documented as limitation, not as feasibility.
- Statistical power limited with current task count — analysis will report intervals/effects and limitation rather than pretend definitiveness.
- Prompt development may have seen some BENCH tasks during engineering (contamination risk) — managed via §28 leakage controls and the planned held-out split for BENCH-002.

## 28. Open Questions

- Final live-model selection (provider, version pinning, cost/reproducibility tradeoff).
- BENCH-002 corpus construction (size, adversarial/ambiguous split, held-out design).
- Whether `PARTIAL` scope can ever warrant `VALIDATED` with additional justification (currently frozen as no).

## 29. Versioning

- Experiment protocol: `EGER-EXP-001 v0.1` (this document). Every run references it. Material change → `v0.2` + new commit.
- Benchmark: `EGER-BENCH-001 v0.1` (P011); future → `v0.2`.
- Model: `EGER-MODEL-001` (fake control, frozen); live model → `MODEL-002` before formal runs.
- Prompt: `EGER-PROMPT-001` `eger.prompt.v1` (frozen).
- Historical protocols remain immutable.

## 30. Change-Control Policy

After P011 PASS, the protocol is FROZEN. Material change to benchmark/model/prompt/metrics/C0–C5/budgets/evaluation/falsification criteria requires new protocol version and `EGER-CHANGE-###` with `status: PROPOSED` → external review before authorized. Silent mutation of `v0.1` is forbidden.
