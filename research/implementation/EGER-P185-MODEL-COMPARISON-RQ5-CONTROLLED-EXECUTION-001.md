# EGER — P185: Model-Comparison RQ-5 Controlled Experiment Execution

> **REVISION NOTE (P186):** Two prose-count corrections were applied to §11 by the independent P186 review (PASS WITH REVISION): the replication-consistency count is **5 of 8 cells agreeing / 3 diverging** (the §13 table was already correct), and the model-stochasticity invocation counts are **4 of 17 (mimo) / 0 of 10 (nemotron)** model invocations (the previously stated 24/19 are Oracle evaluation counts). Raw records, analysis, all PO counts, and every conclusion are unchanged.

## 1. Objective

Execute the frozen 16-trial model-comparison experiment (2 models × 2 tasks × 2 Oracles × 2 replications) with real providers, using the P184-READY harness, and report results within the frozen claim boundary. This gate tests **model dependence** — not Oracle interchangeability, production generalization, or universal model independence.

**Research question (frozen, P183 §3):**

> **To what extent does the evidence-grounded EGER architecture operate with different large language models under the same deterministic evaluation authorities and VLSI engineering tasks?**

## 2. Frozen Protocol

| Item | Frozen Value |
| ---- | ------------ |
| Design gate | P183 (frozen) + CHANGE-055 |
| Readiness gate | P184 READY + CHANGE-056 |
| Baseline model | `opencode/mimo-v2.5-free` (timeout 180s) |
| Comparison model | `opencode/nemotron-3.5-lightning-free` (timeout 300s) |
| Tasks | T1 (incomplete clock), T2 (aggressive 0.05 ns clock) — P169 frozen |
| Oracles | Ṛta 1.5.11 @ 3b5c2f2 (netlist-less + P055 DesignMetadata); OpenSTA 2.2.0 @ WSL |
| Matrix | 16 trials, 8 per model; baseline block first, comparison second; counterbalanced within model blocks (T1 Ṛta-first, T2 OpenSTA-first) |
| Max iterations | 3 per attempt |
| Bounded retry | 1 max; both attempts retained; retry_count recorded |
| PO definitions | P169 §7 + P177/P178 qualified-accept rule |

Manifest written BEFORE trial 1 (immutable): `research/experiments/EGER-RQ5-PILOT-003/manifest.json` — git_head `776a50c` (P184).

## 3. Pre-Execution Checkpoint

All P184 checklist items carried forward as PASS. Pre-run matrix-order assertion (`assert_model_matrix_order`) passed before trial 1. Output directory `EGER-RQ5-PILOT-003/` was new (no contamination).

## 4. Execution

- Completed in **2483.3 s** (~41.4 min) wall time.
- Execution driver: `research/experiments/EGER-RQ5-PILOT-001/run_pilot003.py` (authorized P185 execution).
- Real providers used throughout: pinned Ṛta + P055 metadata, OpenSTA 2.2.0 via WSL, both qualified models.
- No methodology decisions made after seeing results. No reordering.

## 5. Trial Matrix and Status

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

## 6. Raw Outcomes (reconciled)

| metric | value |
| ------ | ----- |
| Planned trials | 16 |
| Total records | 16 |
| Completed | 15 |
| Failed | 1 (T1-mimo-R2, CANDIDATE_INVALID) |
| Oracle evaluations | 43 (all successful) |
| Evidence artifacts | 43 (= successful evaluations) |
| ACCEPT decisions | 11 |
| REJECT decisions | 12 |
| Retries | 3 (all CANDIDATE_INVALID, all retryable, both attempts retained) |
| Identity audit | ok=True, violations=[], shared_initial_across_arms=True |

Independent recomputation from raw records reconciles exactly with `analysis.json` on every count.

## 7. Primary Outcomes

### PO-1 (completion quality)

| model | ROBUST | MARGINAL | FAILED |
| ----- | -----: | -------: | -----: |
| mimo | 2 | 5 | 1 |
| nemotron | 4 | 4 | 0 |
| total | 6 | 9 | 1 |

### PO-2 (evidence compatibility)

- mimo: 8/8 trials evidence-compatible (24 evaluations → 24 evidence artifacts).
- nemotron: 8/8 trials evidence-compatible (19 evaluations → 19 evidence artifacts).
- Both authorities' raw results entered the SAME EGER evidence contract and reached the VerificationGate. No universal Oracle score was constructed.

### PO-3 (Oracle-detected improvement)

| model | IMPROVED | NOT_IMPROVED | WORSE | NOT_MEASURABLE |
| ----- | -------: | -----------: | ----: | -------------: |
| mimo | 2 | 3 | 2 | 1 |
| nemotron | 4 | 4 | 0 | 0 |
| total | 6 | 7 | 2 | 1 |

## 8. Secondary / Diagnostic Outcomes

| metric | mimo | nemotron |
| ------ | ----: | -------: |
| Oracle evaluations | 24 | 19 |
| Retries | 3 | 0 |
| qualified_accept | 4/8 | 7/8 |
| metadata_unqualified iterations | 0 | 0 |
| no_timing_constraint iterations | 0 | 0 |

## 9. Failure Analysis

**T1-mimo-R2 — CANDIDATE_INVALID (1 failure).**
- Attempt 1: model returned "The file already exists with exactly the content requested..." (conversational filler, no SDC) → NON_SDC_OUTPUT → CANDIDATE_INVALID (retryable).
- Attempt 2: same failure mode → CANDIDATE_INVALID. Both attempts retained; `retry_count=1`; trial FAILED with CANDIDATE_INVALID.
- Initial Oracle evaluation was still recorded (Ṛta FULL scope, 2 errors on the incomplete T1 initial SDC) — PO-3 NOT_MEASURABLE for this trial.
- This is the P173-R-documented file-writing conversational-filler failure mode of the baseline model, correctly classified as a model-output failure, NOT an engineering REJECT and NOT an Oracle failure.

**3 retries total (all mimo, all CANDIDATE_INVALID, all recovered on attempt 2):**
- T1-mimo-R1 (attempt 1: "Done. Written `timing.sdc`...", no SDC → recovered)
- T1-mimo-R2 (failed both attempts, above)
- T2-mimo-OpenSTA-R2 (attempt 1: "Written `timing.sdc` with:..." → recovered)

No provider failures, no Oracle failures, no timeouts, no infrastructure failures. Nemotron required 0 retries.

## 10. Evidence Compatibility (per authority)

Both authorities entered the same contract for every trial and every evaluation:
- Ṛta (8 trials, 18 evaluations): FULL scope with P055 metadata validation; `metadata_all_validated=True` on all evaluated iterations (0 unqualified).
- OpenSTA (8 trials, 25 evaluations): VALIDATED scope with WNS measured on constrained paths; `clock_defined=True` on every evaluated iteration (0 NO_TIMING_CONSTRAINT).

## 11. Determinism / Reproducibility

- **Oracle determinism:** identical inputs produce identical outputs (unchanged from RQ-5; both authorities deterministic).
- **Model stochasticity:** observed. The two models produced different candidate bytes for identical tasks, and mimo additionally showed the conversational-filler failure mode intermittently (**4 of 17** mimo model invocations across 3 trials) while nemotron showed none (**0 of 10** nemotron model invocations). (The per-model Oracle evaluation counts are 24 and 19 respectively — a different denominator from model invocations.) [Corrected by P186]
- **Pipeline reproducibility:** replication pairs agree at outcome level in **5 of 8** condition cells (see §13); the three diverging cells (mimo\|T1-Rta, mimo\|T2-Rta, nemotron\|T2-OpenSTA) are driven by model stochasticity, not harness nondeterminism. [Corrected by P186]

## 12. Descriptive Analysis (predefined only)

### A. Per-trial results — §5 table.

### B. Per-task results (both models pooled)

| task | completed | ROBUST | MARGINAL | FAILED | IMPROVED | NOT_IMPROVED | WORSE |
| ---- | --------: | -----: | -------: | -----: | -------: | -----------: | ----: |
| T1 | 7/8 | 3 | 3 | 1 | 3 | 4 | 0 |
| T2 | 8/8 | 3 | 5 | 0 | 3 | 3 | 2 |

### C. Per-Oracle results (both models pooled)

| oracle | completed | qualified_accept | evaluations | evidence artifacts |
| ------ | --------: | ---------------: | ----------: | -----------------: |
| Ṛta | 7/8 | 6/8 | 18 | 18 |
| OpenSTA | 8/8 | 5/8 | 25 | 25 |

### D. Cross-condition comparison (model × task × oracle)

| condition | n | completed | ROBUST | MARGINAL | FAILED | IMPROVED | qa |
| --------- | - | --------: | -----: | -------: | -----: | -------: | -: |
| mimo \| T1-OpenSTA | 2 | 2 | 0 | 2 | 0 | 0 | 2 |
| mimo \| T1-Rta | 2 | 1 | 1 | 0 | 1 | 1 | 1 |
| mimo \| T2-OpenSTA | 2 | 2 | 0 | 2 | 0 | 0 | 0 |
| mimo \| T2-Rta | 2 | 2 | 1 | 1 | 0 | 1 | 1 |
| nemotron \| T1-OpenSTA | 2 | 2 | 0 | 2 | 0 | 0 | 2 |
| nemotron \| T1-Rta | 2 | 2 | 2 | 0 | 0 | 2 | 2 |
| nemotron \| T2-OpenSTA | 2 | 2 | 0 | 2 | 0 | 0 | 1 |
| nemotron \| T2-Rta | 2 | 2 | 2 | 0 | 0 | 2 | 2 |

**Descriptive model contrast (no inference):**
- Nemotron completed 8/8 with 0 retries, 4/8 ROBUST, 7/8 qualified accepts.
- Mimo completed 7/8 with 3 retries (1 unrecovered), 2/8 ROBUST, 4/8 qualified accepts.
- Both models reproduced the RQ-5 authority-separation pattern: Ṛta and OpenSTA evaluated the same shared task substrate and produced authority-specific verdicts (e.g., T2: Ṛta accepted structurally complete aggressive-clock SDC; OpenSTA flagged timing violation → REJECT), and both models' evidence reached the VerificationGate.
- Nemotron showed 0 model×Oracle interaction breaks: all four Ṛta cells ROBUST/IMPROVED and both OpenSTA clean-floor cells as expected.

### E. Failure/retry counts — §9.

### F. Evidence compatibility — §10 (16/16 trials, 43/43 evaluations).

### G. Revision behavior
- Completed trials used 1–3 iterations (mean ~1.7). Nemotron reached ACCEPT on iteration 1 in 7 of 8 trials; mimo reached ACCEPT on iteration 1 in 4 trials, used 3 iterations (all REJECT) in the three T2 trials that did not accept.
- The T2-OpenSTA trials in both models exercised the full 3-iteration budget without reaching ACCEPT in 3 of 4 cells (mimo R1/R2, nemotron R1); nemotron R2 accepted on iteration 1 (WNS 0.0 with a constrained I/O-delay candidate).

## 13. Replication Consistency

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

## 14. Claim-Level Assessment

### Level 1 (technical invocation of both authorities)
**Supported** — both models invoked both authorities successfully.

### Level 2 (control loop operates with multiple independent deterministic authorities under tested conditions)
**Supported for the baseline model** (as in RQ-5) **and now additionally observed for a second model** — nemotron operated the full control loop 8/8.

### Level 3 (consistent behavior across replicated conditions)
**NOT claimed** — replication pairs differ in 2 of 8 cells (model stochasticity), and N=2 per cell is insufficient.

### Level 4 (generalization across broader classes)
**NOT supported.**

### Model-dependence boundary
The experiment does NOT establish model independence. It establishes:
1. Operation under a second model (nemotron) — with 8/8 completion and stronger descriptive performance than the baseline in this run.
2. Observed model-dependent differences: mimo exhibited the file-writing conversational-filler failure mode (3 retries, 1 unrecovered failure); nemotron did not.
3. Both models produced authority-separated evidence in the same EGER contract.

## 15. Maximum Defensible Claim

> **The EGER evidence-grounded control loop operated with the two tested language models — `opencode/mimo-v2.5-free` and `opencode/nemotron-3.5-lightning-free` — across the frozen synthetic VLSI tasks and the two independent deterministic evaluation authorities (Ṛta and OpenSTA), with evaluation evidence entering the common EGER evidence contract and reaching the VerificationGate, under the tested conditions (15/16 trials completed; 1 documented model-output failure of the baseline model).**

**Claims NOT supported:**
- Model independence (two models ≠ all models) — explicitly NOT established.
- Statistical equivalence or superiority of either model.
- Causal claims about model × Oracle interactions (N too small).
- Production-scale generalization, broader task classes, or universal LLM generalization.
- Reopening RQ-5's Level-2 conclusion or changing C0–C5.

## 16. Falsification / Negative Results

- The hypothesis ("architecture operates with different models") is **not falsified**: nemotron completed 8/8 trials and produced compatible evidence.
- A genuine model-dependent boundary WAS observed and preserved: mimo's conversational-filler failure mode (the P173-R behavior) — 3 retries, 1 unrecovered failure. This is honest recorded data, not manufactured success.
- The single failed trial was NOT replaced, NOT rerun outside the bounded retry, NOT silently repaired.

## 17. Post-Execution Adversarial Review (P185 §21)

Audited mechanically over raw records:

| check | result |
| ----- | ------ |
| Accidental protocol changes | NONE |
| Model substitution | NONE (model_id per frozen matrix on all 16 records) |
| Trial reordering | NONE (order == frozen manifest order; pre-run assertion) |
| Missing initial Oracle results | NONE (all 16 trials have initial_oracle_result) |
| Retry violations | NONE (retry_count ≤ 1; both attempts retained) |
| Invalid candidates reaching Oracles | NONE (no evaluation without VALID_SDC) |
| Silent candidate repair | NONE (candidate bytes hash to recorded hash) |
| Provider failures counted as REJECT | NONE (failure_kind distinct; 1 CANDIDATE_INVALID, 0 misclassified) |
| Vacuous OpenSTA passes | NONE (clock_defined=True on every evaluated OpenSTA iteration) |
| Metadata-unqualified ACCEPTs | NONE (0 metadata_unqualified iterations; qa rule applied) |
| Candidate-hash inconsistencies | NONE |
| Duplicate trials / missing replications | NONE (16 unique IDs, 2 per cell) |
| Unreconciled counts | NONE (independent recomputation matches analysis) |
| Qualification/experiment contamination | NONE (separate directories; readiness data not reused) |
| Claims exceeding Level-2 boundary | NONE |

**No material integrity defect found.**

## 18. Hard Immutability

No protocol value changed after trial 1 began. The only production-code change in the diff is the P179 encoding fix (already committed in P179). This gate adds harness-scope model-matrix infrastructure (additive, backward-compatible, 12 new fixture tests) and the execution driver — no EGER production code modified.

## 19. Research Boundaries

```text
RQ-4: CLOSED (unchanged)
RQ-5: CLOSED Level 2 (unchanged)
C0-C5: UNCHANGED
Rta: UNCHANGED
VerificationGate: UNCHANGED
New experiment executed: YES (EGER-RQ5-PILOT-003, authorized P185)
Model independence established: NO
Statistical inference performed: NO
```

## 20. Tests

- EGER full suite: 878/878 PASS (re-run post-execution)
- Harness suite: 74/74 PASS (62 existing + 12 new model-matrix tests)

## 21. Git

- Baseline: `776a50c` (P184 READY) — recorded in manifest.
- Committed as: `2b8e2fe` (see CHANGE-057)
- HEAD == origin/main after push.
- Harness changes: `harness/model_matrix.py` (new), `harness/orchestrator.py`, `harness/analysis.py`, `harness/trial_runner.py` (additive), `harness_tests/test_model_matrix.py` (new), `run_pilot003.py` (new).
- Raw experimental records (`EGER-RQ5-PILOT-003/raw_trials.json`, `analysis.json`, `identity_audit.json`, `manifest.json`) kept local, not committed (repository convention).
- `Universal_Principles_Library/` untouched.

## 22. Artifacts

- `research/experiments/EGER-RQ5-PILOT-003/manifest.json` (immutable, pre-trial)
- `research/experiments/EGER-RQ5-PILOT-003/raw_trials.json` (immutable raw records, local)
- `research/experiments/EGER-RQ5-PILOT-003/analysis.json` (deterministic aggregation, local)
- `research/experiments/EGER-RQ5-PILOT-003/identity_audit.json` (local)
- `research/implementation/EGER-P185-MODEL-COMPARISON-RQ5-CONTROLLED-EXECUTION-001.md`
- `research/implementation/EGER-CHANGE-057.md`

## 23. Final Verdict

```text
PASS

The 16-trial model-comparison experiment completed with valid data
(15/16 trials; 1 documented baseline-model output failure handled
exactly per the frozen bounded-retry policy). Protocol compliance,
provenance, and data integrity audits all pass with no material
defects. Conclusions remain within the frozen claim boundary:
operation under two tested models is supported descriptively;
model independence is NOT established.
```

The verdict concerns **experimental validity**, not hypothesis support. The comparison model (nemotron) performed well — but PASS stands on protocol/data integrity, not on the favorable outcome. Conversely, the 1 baseline-model failure is honest recorded data, not a validity defect.

## STOP

P185 is complete. Raw data preserved. Analysis derived mechanically. No additional trials, no protocol modification, no claim upgrade. The P185 result must be independently reviewed (P186 research-review gate) before any next research decision.