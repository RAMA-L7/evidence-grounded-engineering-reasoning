# EGER — P179: RQ-5 PILOT-002 Controlled Oracle-Validation Experiment Execution

## 1. Objective

Execute EGER-RQ5-PILOT-002 exactly as authorized by P179, on the READY state established by P178, using the repaired `harness/orchestrator.py` with real providers (real model, real Ṛta, real OpenSTA). Produce an immutable raw trial record, deterministic analysis, protocol-compliance audit, provenance audit, and claim-level assessment.

**P179 is the first gate authorized to collect RQ-5 experimental data.** No methodological decision was made after results were observed.

## 2. Frozen Protocol Chain

| Record | Role |
| ------ | ---- |
| P169 + CHANGE-040 | Frozen protocol (2×2×2 = 8 trials, counterbalanced) |
| P172 + CHANGE-043 | Repair design (candidate validity, initial eval, retry, counterbalancing, PO-2 accounting) |
| P173-R | Model qualification resolution (opencode/mimo-v2.5-free, file-writing invocation) |
| P174 + CHANGE-046 | Final readiness (READY) |
| P175/P176 + CHANGE-047/048 | Ṛta scope alignment (FULL-scope path, design_metadata, normalizer pass-through) |
| P177 + CHANGE-049 | Readiness + authorization audit (18 items) |
| P178 + CHANGE-050 | Identity audit + readiness revalidation (item-2 correction) |

Frozen research question (unchanged, exact):

> **To what extent does the evidence-grounded EGER architecture generalize across independent deterministic evaluation authorities within VLSI engineering tasks?**

## 3. Experiment Manifest

Immutable manifest written before trial 1: `research/experiments/EGER-RQ5-PILOT-002/manifest.json`.

- experiment_id: EGER-RQ5-PILOT-002
- authorization_gate: P179
- protocol: P169 (frozen) as repaired by P172/P177/P178
- git_head: `04c33b4b88a4d3e4caedcd227daac40a4f995079` (P178)
- model: opencode/mimo-v2.5-free via `opencode run`, provider-default sampling (no temperature flag exposed), timeout 180 s, qualified P173-R 6/6
- Ṛta: 1.5.11 @ revision `3b5c2f2`, netlist-less `check --json` + P055 design_metadata (SIMPLE_PATH)
- OpenSTA: 2.2.0 @ WSL `/root/opensta_build/OpenSTA/app/sta`
- Substrate: simple_path.v (sha256 e03887fe...) + simple_cells.lib (sha256 cfd8b3f8...)
- retry_policy: 1 bounded retry per trial, both attempts retained
- max_iterations: 3 (per attempt)

## 4. Execution Order

Frozen counterbalanced order, asserted before trial 1 (matrix assertion passed):

| order | trial | task | oracle first |
| ----: | ----- | ---- | ------------ |
| 1 | T1-Rta-R1 | T1 | Rta |
| 2 | T1-OpenSTA-R1 | T1 | Rta |
| 3 | T1-Rta-R2 | T1 | Rta |
| 4 | T1-OpenSTA-R2 | T1 | Rta |
| 5 | T2-OpenSTA-R1 | T2 | OpenSTA |
| 6 | T2-Rta-R1 | T2 | OpenSTA |
| 7 | T2-OpenSTA-R2 | T2 | OpenSTA |
| 8 | T2-Rta-R2 | T2 | OpenSTA |

T1 Ṛta-first; T2 OpenSTA-first. Counterbalancing requirement satisfied.

## 5. Trial Matrix

| Trial | Task | Oracle | Replication | Status |
| ----- | ---- | ------ | ----------: | ------ |
| T1-Rta-R1 | T1 | Ṛta | 1 | COMPLETED |
| T1-OpenSTA-R1 | T1 | OpenSTA | 1 | COMPLETED |
| T1-Rta-R2 | T1 | Ṛta | 2 | COMPLETED |
| T1-OpenSTA-R2 | T1 | OpenSTA | 2 | COMPLETED |
| T2-OpenSTA-R1 | T2 | OpenSTA | 1 | COMPLETED |
| T2-Rta-R1 | T2 | Ṛta | 1 | COMPLETED |
| T2-OpenSTA-R2 | T2 | OpenSTA | 2 | COMPLETED |
| T2-Rta-R2 | T2 | Ṛta | 2 | COMPLETED |

**8/8 completed, 0 failures, 0 retries.**

## 6. Raw Outcomes

Immutable raw records: `research/experiments/EGER-RQ5-PILOT-002/raw_trials.json` (8 records; kept local, publication-sensitive, NOT committed).

Each record retains: trial_id, task_id, oracle, replication_id, execution_order, attempt, retry_count, initial_sdc + hash, initial_oracle_result + initial_evidence_hash, full per-iteration candidate bytes/hashes + validity + Oracle results + evidence hashes + verification decisions, final_sdc + hash, final_oracle_result, oracle_call_count, iteration_count, accept_reached, runtime_seconds, attempts[].

## 7. Primary Outcomes

### PO-1 — Completion quality

| Condition | ROBUST | MARGINAL | FAILED |
| --------- | :----: | :------: | :----: |
| T1-Ṛta | 2 | 0 | 0 |
| T1-OpenSTA | 0 | 2 | 0 |
| T2-Ṛta | 2 | 0 | 0 |
| T2-OpenSTA | 0 | 2 | 0 |

### PO-2 — Evidence compatibility

All 8 trials: evidence compatible = true (both authorities' evidence entered the existing EGER evidence contract). 22 Oracle evaluations → 22 successful evaluations → evidence artifacts; per-Oracle 4/4 compatible (Ṛta 8/8 evaluations, OpenSTA 14/14).

### PO-3 — Oracle-detected improvement (Oracle-specific)

| Condition | IMPROVED | NOT_IMPROVED | WORSE | NOT_MEASURABLE |
| --------- | :------: | :----------: | :---: | :------------: |
| T1-Ṛta | 2 | 0 | 0 | 0 |
| T1-OpenSTA | 0 | 2 | 0 | 0 |
| T2-Ṛta | 2 | 0 | 0 | 0 |
| T2-OpenSTA | 0 | 0 | 2 | 0 |

qualified_accept (P177/P178 rule): T1-Ṛta 2/2, T1-OpenSTA 2/2, T2-Ṛta 2/2, T2-OpenSTA **0/2**.

## 8. Secondary / Diagnostic Outcomes

- Oracle evaluations: 22 (Ṛta 8, OpenSTA 14); successful: 22; evidence artifacts: 22
- Iterations: T1 all trials 1; T2-Ṛta 1; T2-OpenSTA 3 (both replications, all REJECT)
- Retries: 0 (none required)
- Accept decisions: 6 ACCEPT / 6 REJECT across iteration-level verifications
- runtime: total execution 321.7 s across 8 trials
- no_timing_constraint_iterations: 0 (OpenSTA valid-clock guard never tripped)
- metadata_unqualified_iterations: 0 (Ṛta FULL scope held on every evaluation)

## 9. Failure Analysis

No provider, Oracle, infrastructure, or pipeline failure occurred. Zero retries were needed; the frozen bounded-retry policy was available but not exercised. The T2-OpenSTA trials completed with the pipeline rejecting — this is an engineering outcome (timing violation), not a failure.

## 10. Evidence Compatibility

Both authorities entered the same EGER evidence pipeline with no authority-specific architecture:

- Ṛta: raw check → FULL scope (canonical pass-through) → gate ACCEPT/REJECT on Ṛta constraint-quality errors
- OpenSTA: raw STA → VALIDATED scope → measured WNS → gate ACCEPT/REJECT on timing findings

Semantic equivalence between evidence types is NOT claimed.

## 11. Determinism / Reproducibility

- Oracle determinism: Ṛta 1.5.11 and OpenSTA 2.2.0 deterministic (established P163–P176); identical candidate SDCs produced identical Oracle outputs within and across replications
- Model/pipeline: provider-default sampling; replication pairs produced consistent *outcomes* (see §14) though final SDC hashes differ between R1/R2 in the accepted cases — model-generated text is not asserted bitwise-deterministic
- Aggregation: deterministic from raw records (single analysis pass, no manual totals)

## 12. Descriptive Analysis

Per-condition and per-Oracle tables derive mechanically from raw records (analysis.json). Replication pairs agree in every condition at the outcome level:

- T1-Ṛta R1/R2: ROBUST + IMPROVED + qualified ACCEPT
- T1-OpenSTA R1/R2: MARGINAL + NOT_IMPROVED + qualified ACCEPT (initial already clean → no Oracle-detected improvement)
- T2-Ṛta R1/R2: ROBUST + IMPROVED + qualified ACCEPT
- T2-OpenSTA R1/R2: MARGINAL + WORSE + NOT qualified (persistent genuine timing violation)

## 13. Confounders

- Synthetic 3-cell substrate (technical pilot scope only)
- Model stochasticity: provider-default sampling; no temperature control
- Model behavior: in T2-OpenSTA the model repeated an equivalent SDC across all 3 iterations instead of relaxing the clock — revision behavior, not harness intervention
- Task ceiling: T2's 0.05 ns clock is unmeetable on this substrate; no candidate could pass OpenSTA
- OpenSTA initial-candidate "clean floor" on T1 (no delays → no constrained path → WNS 0.0): documented; mitigated by the model's complete first candidate and the valid-clock guard (clock_defined=True on every evaluated iteration)
- Authority property mismatch is the measured signal, not an artifact (see §16)

## 14. Replication Consistency (descriptive)

All four replication pairs produced identical primary outcomes and identical accept/reject structure. Final SDC bytes differ between R1/R2 in accepted cases (different valid completions), identical in the T2-OpenSTA case (model converged to the same failing SDC). Descriptive only; no statistical inference.

## 15. Claim Assessment

### The result that matters — T2 discrimination

Both authorities evaluated the **same task family with the same aggressive initial clock (0.05 ns)** and the **same shared candidate SDC bytes** per trial:

- **Ṛta (constraint-quality authority)**: after the model added structurally valid I/O delays (< period), Ṛta's rules found no constraint error → **ACCEPT** (qualified). Ṛta does not compute timing; 0.05 ns is structurally expressible.
- **OpenSTA (timing authority)**: the identical candidate SDC produces a genuine timing violation (WNS −0.01/−0.02) that persists across all 3 iterations → **REJECT** (never qualified).

The two authorities legitimately disagree about the same artifact because they measure different engineering properties. Each drove its own evidence-grounded control loop correctly to its own authority-consistent verdict. This is precisely the authority-separation the protocol was designed to observe — NOT interchangeability.

### Highest supported claim (Level 2, descriptive)

> The evidence-grounded EGER control loop operated with two independent deterministic evaluation authorities (Ṛta and OpenSTA) across the two frozen synthetic VLSI tasks, with complete, reproducible, authority-separated evaluation evidence entering the same EGER evidence contract and reaching the VerificationGate — under the tested conditions.

### Claims NOT supported

- Oracle interchangeability / equivalence (refuted on T2 by observation: same candidate, opposite verdicts, each correct in its own lane)
- Universal or production-scale generalization
- Generalization beyond the tested synthetic substrate/tasks
- Any causal or inferential claim (N=8 descriptive pilot, replication pairs only)
- Ṛta correctness vs OpenSTA correctness ordering

## 16. Research Boundary

```text
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: YES
C0-C5 conclusions changed: NO
Oracle comparison performed: YES (descriptive, authority-separated)
Oracle interchangeability established: NO
VerificationGate authority changed: NO
Epistemic-state logic added: NO
Authorization logic added: NO
```

## 17. Protocol-Compliance Audit

| Frozen item | Result | Evidence |
| ----------- | ------ | -------- |
| 8 planned trials | PASS | 8/8 raw records |
| Counterbalanced order (T1 Ṛta-first, T2 OpenSTA-first) | PASS | manifest order; pre-run assertion |
| Shared task initial SDC across arms | PASS | identity_audit: shared_initial_across_arms=True |
| Candidate validity gate before Oracle | PASS | all evaluated iterations VALID_SDC, clock_defined=True |
| Initial Oracle evaluation before revision | PASS | initial_oracle_result + initial_evidence_hash on all 8 |
| Bounded retry (1 max, both attempts) | PASS | policy in manifest; 0 retries needed; attempt/retry_count recorded |
| No reordering / no post-result changes | PASS | order == manifest; single immutable run |
| No silent candidate repair | PASS | identity audit: oracle-received == recorded bytes |
| Candidate bytes + deterministic hashes recorded | PASS | candidate_raw/hash + candidate_sdc/hash per iteration |
| Oracle-specific feedback preserved | PASS | per-Oracle revision prompts (raw records) |
| Provider/model failures distinguished from REJECT | PASS | failure_kind None × 8; REJECT only from engineering findings |
| metadata_unqualified / qualified_accept frozen rule | PASS | 0 unqualified iterations; qualified_accept propagated |
| Ṛta / VerificationGate / RQ-4 / C0-C5 untouched | PASS | production diff = encoding fix only (harness) |
| Raw records preserved before analysis | PASS | raw_trials.json immutable; analysis derived after |

One harness robustness fix was required during execution and applied before any trial completed: subprocess `encoding="utf-8"` in `harness/providers.py` (opencode emits UTF-8; locale cp1252 decode crashed the first launch). This is a harness encoding fix, not a protocol, methodology, or data change. The crashed first launch produced no trial data (crashed before trial 1 completed); it was discarded and the run relaunched cleanly.

## 18. Provenance / Integrity Audit

- Independent recomputation from raw records confirms: 8 completed / 0 failed / 22 oracle calls / analysis.json totals reconcile exactly
- identity_audit.json: ok=true, violations=[], shared initial hash per task across arms
- Evidence hashes recorded for every initial evaluation and every iteration
- No credentials or private model/provider outputs in any committed artifact; raw trials remain local-only

## 19. Threats to Validity

- Internal: model stochasticity (provider-default sampling); no causal attribution attempted
- Construct: PO-3 is Oracle-specific by design; T2-OpenSTA "WORSE" means first real constraints exposed an unmeetable clock — the vacuous-clean initial floor documented in P171
- External: synthetic 3-cell substrate; results bounded to tested conditions
- Statistical conclusion: N=8 descriptive pilot; no inferential statistics

## 20. Final Decision

```text
RQ-5 PILOT VALIDATED (descriptive, Level 2 — with the authority-separation
result on T2 explicitly preserved; NOT interchangeability, NOT generalization)
```

Execution summary: 8/8 completed; 0 failures; 0 retries; PO-1/PO-2/PO-3 derived deterministically; identity audit clean; regression 878/878 EGER + 62/62 harness.

## 21. Tests

- EGER full suite: 878/878 PASS
- Harness suite: 62/62 PASS
- (Run post-execution; no production-code change beyond the harness encoding fix)

## 22. Git

- P179 committed as: `<hash>` (see CHANGE-051)
- HEAD == origin/main (after push)
- Universal_Principles_Library/ untouched
- Raw/experimental records (raw_trials.json, analysis.json, identity_audit.json, manifest.json under EGER-RQ5-PILOT-002/, execution log) remain local-only

## 23. Artifacts

- `research/experiments/EGER-RQ5-PILOT-002/manifest.json` (immutable, local)
- `research/experiments/EGER-RQ5-PILOT-002/raw_trials.json` (immutable, local)
- `research/experiments/EGER-RQ5-PILOT-002/identity_audit.json` (local)
- `research/experiments/EGER-RQ5-PILOT-002/analysis.json` (local)
- `research/experiments/EGER-RQ5-PILOT-001/run_pilot002.py` (committed, execution driver)
- `research/implementation/EGER-P179-RQ5-PILOT002-CONTROLLED-ORACLE-VALIDATION-EXECUTION-001.md`
- `research/implementation/EGER-CHANGE-051.md`

## STOP

No additional trials. No protocol modification. No new claims. Await an explicit research-review gate (P180) before any interpretation beyond this record is attempted.
