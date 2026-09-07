# EGER — P186: Independent Research Review of P185 Model-Comparison Experiment

## 1. Objective

Independently audit the methodological validity, evidence reconciliation, reproducibility, and claim boundaries of the P185 model-comparison experiment (EGER-RQ5-PILOT-003). This is a **review gate only** — no experiment was rerun, no raw data modified, no protocol changed.

**Review method:** all counts were re-derived from `raw_trials.json` (the authority) with an independent audit script (`p186_audit.py`) that re-implements the frozen P169 §7 PO definitions and P177/P178 qualified-accept rule WITHOUT importing the harness analysis module. `analysis.json` and the P185 report were then cross-checked against the independent derivation.

**Baseline:** `cb4d7b9` (P185 pushed). Raw records local at `research/experiments/EGER-RQ5-PILOT-003/`.

## 2. Executive Verdict

**PASS WITH REVISION** — one research-record correction required (P185 §11 prose counts; see §5). The experimental data, protocol compliance, provenance, and conclusions are fully valid; the correction is documentation-only.

## 3. Role Checks

### 3.1 Research Methodology & Evidence Auditor
- **Finding:** All counts reconcile exactly with the raw records. PO-1/PO-2/PO-3 independently re-derived from the frozen definitions match `analysis.json` and the P185 report for every model. One internal inconsistency found in P185 §11 prose (replication-consistency count) — see §5.
- **Evidence:** independent recount: 16 records, 15 completed, 1 failed (T1-mimo-R2, CANDIDATE_INVALID), 3 retries, 43 Oracle evaluations, 43 evidence artifacts, 11 ACCEPT / 12 REJECT; assignment fields consistent with trial IDs; order == pre-trial manifest order.
- **Concern:** §11 prose says "6 of 8 cells agree / two diverging" while §13's own table shows 5 AGREE / 3 DIFFER.
- **Verdict:** PASS WITH REVISION.

### 3.2 Research Architect
- **Finding:** The model dimension was added without disturbing the frozen RQ-5 architecture: same tasks, same Oracles, same evidence contract, same VerificationGate, same iteration/retry budgets. Model is recorded per trial and per-model aggregation is deterministic.
- **Verdict:** PASS.

### 3.3 EGER Systems/Software Engineer
- **Finding:** Harness additions are additive and backward-compatible (`model` kwarg default None; new matrix module; additive analysis keys). 12 new fixture tests cover the 16-cell matrix, order assertion, model propagation, per-model analysis, and identity audit.
- **Evidence:** EGER suite 878/878; harness suite 74/74 (re-run in this gate).
- **Verdict:** PASS.

### 3.4 VLSI / EDA Domain Expert
- **Finding:** Both authorities operated on the frozen substrate with their own semantics: Ṛta FULL-scope constraint-quality findings (P055 metadata all validated, 0 unqualified) and OpenSTA measured WNS on clock-defined, constrained evaluations (14/14 evaluated iterations `clock_defined=True`, 0 vacuous).
- **Verdict:** PASS.

### 3.5 Experimental Scientist / Statistician
- **Finding:** N=2 per cell is descriptive only. PO derivations are deterministic given raw records. The two mimo WORSE results (T2-OpenSTA R1/R2) are the documented vacuous-initial artifact (initial clock-only WNS 0.0 "clean" → first real I/O constraints expose −0.01), not evidence that revision harmed timing. No inferential statistics performed or warranted.
- **Verdict:** PASS.

### 3.6 Adversarial Reviewer / Red-Team
- **Finding:** The single failure (T1-mimo-R2) is honestly preserved: both attempts returned conversational filler ("The file already exists...") → NON_SDC_OUTPUT → CANDIDATE_INVALID on both; initial Ṛta evaluation retained; no substitution, no silent repair, no extra retry. No un-gated Oracle evaluation exists anywhere in the records. Candidate bytes hash to recorded hashes on every evaluated iteration.
- **Concern:** P185 §11's "3 of 24 model invocations" miscounts the filler rate (actual: 4 of 17 mimo model invocations across 3 trials; the 24/19 figures are Oracle evaluation counts, not model invocations).
- **Verdict:** PASS WITH REVISION.

### 3.7 Reproducibility & Provenance Auditor
- **Finding:** Manifest written before trial 1 (git_head `776a50c`); frozen model IDs, Oracle versions (Ṛta 1.5.11 @ 3b5c2f2, OpenSTA 2.2.0), substrate hashes, and 16-row matrix recorded. Identity audit `ok=True`, 0 violations, one shared initial-SDC hash per task across both arms and both models. Raw records local (deliberate publication-sensitive boundary, consistent with repository convention since P170 — not a defect).
- **Verdict:** PASS.

### 3.8 Release / Git Integrity Officer
- **Finding:** P185 committed as `2b8e2fe` (+ hash-fix commit `cb4d7b9`), pushed, HEAD == origin/main at review start. Working tree clean except intentionally untracked experiment artifacts. `Universal_Principles_Library/` untouched.
- **Verdict:** PASS.

## 4. Reconciliation Table (raw records = authority)

| Item | Expected | Observed | Status |
| ------------------- | -------: | -------: | ------ |
| Planned trials | 16 | 16 | MATCH |
| Completed trials | 15 | 15 | MATCH |
| Failed trials | 1 | 1 (T1-mimo-R2, CANDIDATE_INVALID) | MATCH |
| Oracle evaluations | 43 | 43 (24 mimo + 19 nemotron) | MATCH |
| Evidence artifacts | 43 | 43 (independent recount) | MATCH |
| Retries | 3 | 3 (T1-mimo-R1, T1-mimo-R2, T2-mimo-OpenSTA-R2; all retryable; both attempts retained) | MATCH |
| ACCEPT / REJECT decisions | 11 / 12 | 11 / 12 | MATCH |
| Identity violations | 0 | 0 | MATCH |
| PO-1 (mimo) | 2/5/1 | 2 ROBUST / 5 MARGINAL / 1 FAILED (independent re-derivation) | MATCH |
| PO-1 (nemotron) | 4/4/0 | 4 ROBUST / 4 MARGINAL / 0 FAILED | MATCH |
| PO-3 (mimo) | 2/3/2/1 | 2 IMPROVED / 3 NOT_IMPROVED / 2 WORSE / 1 NOT_MEASURABLE | MATCH |
| PO-3 (nemotron) | 4/4/0/0 | 4 IMPROVED / 4 NOT_IMPROVED / 0 WORSE / 0 NOT_MEASURABLE | MATCH |
| qualified_accept | 4/8, 7/8 | 4/8, 7/8 | MATCH |
| EGER tests | 878/878 | 878/878 (re-run in P186) | MATCH |
| Harness tests | 74/74 | 74/74 (re-run in P186) | MATCH |
| Replication cells agreeing | 6 (P185 §11 text) | **5 of 8** (§13 table and independent recount) | **DISCREPANCY (prose only)** |

No unexplained count mismatch exists anywhere in the data. The single discrepancy is P185 §11's prose sentence contradicting its own §13 table.

## 5. Required Corrections (minimal, documentation-only)

**Correction 1 — P185 §11 replication-consistency count.** §11 states replication pairs agree "in 6 of 8 condition cells" with "the two diverging cells." §13's own table — and the independent recount — show **5 AGREE / 3 DIFFER** (diverging: mimo|T1-Rta, mimo|T2-Rta, nemotron|T2-OpenSTA). Correct §11 to 5 of 8 / three diverging cells. §13's table is already correct and unchanged.

**Correction 2 — P185 §11 model-invocation counts.** §11 states the filler failure mode occurred in "3 of 24 model invocations... 0 of 19." The actual counts: **4 of 17 mimo model invocations** (3 trials) and **0 of 10 nemotron model invocations**. The 24/19 figures are Oracle *evaluation* counts, not model invocations. Correct §11 with the actual invocation counts.

Both corrections are prose-only. Raw records, `analysis.json`, §13's table, all PO counts, and every conclusion in P185 are unaffected. No historical evidence is rewritten; the corrections are recorded here and applied to the report with a revision note (P180-R precedent).

## 6. Claim Audit

| Claim | Classification |
| ----- | -------------- |
| The EGER control loop operated with the two tested models under the tested conditions (15/16; 1 documented model-output failure) | **SUPPORTED** |
| Both models entered the common evidence contract and reached the VerificationGate (43/43 evaluations → evidence) | **SUPPORTED** |
| Authority separation preserved under both models (Ṛta constraint-quality vs OpenSTA timing; no universal score) | **SUPPORTED** |
| Mimo exhibited the conversational-filler failure mode; nemotron did not | **SUPPORTED WITH BOUNDARY** (observed under this run's sampling; not a proven stable model trait) |
| Nemotron completed 8/8 with 0 retries vs mimo 7/8 with 3 retries | **SUPPORTED WITH BOUNDARY** (descriptive observation only; no statistical claim) |
| Nemotron is statistically superior / universally stronger | **UNSUPPORTED** |
| EGER is model-independent | **UNSUPPORTED** |
| EGER generalizes to arbitrary LLMs / VLSI tasks / production scale | **UNSUPPORTED** |
| Replication pairs agree in 6 of 8 cells (P185 §11) | **OVERCLAIM** (corrected to 5 of 8; §13 table was already correct) |
| RQ-5 Level-2 conclusion extended by a second-model observation | **SUPPORTED WITH BOUNDARY** (additive observation; RQ-5 conclusion itself unchanged) |

## 7. Frozen Conclusions

```text
RQ-4: CLOSED — unchanged
RQ-5: CLOSED at Level 2 — unchanged (P185 is an additive model-dimension observation, not a reinterpretation)
C0-C5: UNCHANGED
Rta: deterministic, external, read-only — UNCHANGED (1.5.11 @ 3b5c2f2)
VerificationGate: sole ACCEPT/REJECT authority — UNCHANGED
Model independence: NOT established
Statistical inference: NONE performed
```

## 8. Tests

- EGER full suite: 878/878 PASS (re-run in P186)
- Harness suite: 74/74 PASS (re-run in P186)

## 9. Git

- Review baseline: `cb4d7b9` (HEAD == origin/main)
- P186 committed as: `ff3f5ed` (see CHANGE-058)
- Raw experimental records remain local (deliberate boundary)
- `Universal_Principles_Library/` untouched

## 10. Final Research Verdict

```text
P186 PASS WITH REVISION

P185 is methodologically defensible: every count reconciles with the raw
records, the failure is honestly preserved, the claim boundary held, and
all frozen conclusions are unchanged. Two minimal prose-count corrections
to P185 §11 are required (replication-consistency 6→5 of 8; model-
invocation counts 3/24, 0/19 → 4/17, 0/10). No data correction, no
protocol change, no experiment rerun.
```

Per the P186 mandate: with PASS WITH REVISION, the next work should be **documentation/research packaging**, not another uncontrolled experiment.

## STOP

No new experiment. No protocol modification. No claim upgrade. Await explicit user direction for the packaging/publication phase.