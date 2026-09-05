# EGER P171 — RQ-5 Results Integrity & Claim Assessment

## 1. Review Objective

Independently audit the frozen P170 experiment records (`raw_trials.json`, `analysis.json`, `run_experiment.py`, P170 report, CHANGE-041) to determine whether the collected observations are internally consistent, reproducible, traceable, and sufficient to support a defensible RQ-5 descriptive claim — given the documented missing-retry deviation.

This is a REVIEW GATE ONLY. No experiment was rerun. No retry was executed. No raw data was modified.

## 2. Source Artifacts

| Artifact | Role |
|----------|------|
| `research/implementation/EGER-P169-RQ5-EXPERIMENTAL-PROTOCOL-ADVERSARIAL-REVIEW-001.md` | Frozen protocol (authoritative) |
| `research/implementation/EGER-CHANGE-040.md` | P169 change control |
| `research/implementation/EGER-P170-RQ5-CONTROLLED-ORACLE-VALIDATION-EXECUTION-001.md` | P170 execution report |
| `research/implementation/EGER-CHANGE-041.md` | P170 change control |
| `research/experiments/EGER-RQ5-PILOT-001/run_experiment.py` | Committed execution script |
| `research/experiments/EGER-RQ5-PILOT-001/raw_trials.json` | Local raw trial records (reviewed, not committed) |
| `research/experiments/EGER-RQ5-PILOT-001/analysis.json` | Local analysis output (reviewed, not committed) |

## 3. Git Baseline

- **Commit:** `624fbb5a2869099788ebc02dbaecd838c988a3bf` (P170 checkpoint)
- **Branch:** `main`
- **HEAD == origin/main:** confirmed
- **Working tree:** clean except intentionally untracked `Universal_Principles_Library/`, `raw_trials.json`, `analysis.json`

## 4. Data Integrity Audit

### 4.1 Trial-level verification (raw_trials.json, independently recomputed)

| Trial | Raw record | Report (P170) | Analysis (analysis.json) | Consistent? |
|-------|-----------|---------------|--------------------------|-------------|
| T1-Rta-R1 | COMPLETED, 3 iters, 3 calls, REJECT | COMPLETED, 3 iters, REJECT | completed, accepted=0 | YES |
| T1-Rta-R2 | COMPLETED, 3 iters, 3 calls, REJECT | COMPLETED, 3 iters, REJECT | completed, accepted=0 | YES |
| T1-OpenSTA-R1 | COMPLETED, 1 iter, 1 call, ACCEPT | COMPLETED, 1 iter, ACCEPT | completed, accepted=2 | YES |
| T1-OpenSTA-R2 | COMPLETED, 1 iter, 1 call, ACCEPT | COMPLETED, 1 iter, ACCEPT | completed, accepted=2 | YES |
| T2-Rta-R1 | COMPLETED, 3 iters, 3 calls, REJECT | COMPLETED, 3 iters, REJECT | completed, accepted=0 | YES |
| T2-Rta-R2 | COMPLETED, 3 iters, 3 calls, REJECT | COMPLETED, 3 iters, REJECT | completed, accepted=0 | YES |
| T2-OpenSTA-R1 | COMPLETED, 1 iter, 1 call, ACCEPT | COMPLETED, 1 iter, ACCEPT | completed, accepted=1 | YES |
| T2-OpenSTA-R2 | FAILED, 0 iters, 0 calls, PROVIDER_FAILURE | FAILED, PROVIDER_FAILURE | failed | YES |

**Totals recomputed:** 8 planned, 7 completed, 1 failed, 0 retries. Matches all three sources.

### 4.2 Discrepancy: PO-2 evaluation counts

- **P170 report (§7):** "Ṛta 7/7 evaluations, OpenSTA 4/4 evaluations, total 11/11."
- **Raw data:** 12 Ṛta evaluations (4 trials × 3 iterations) + 3 OpenSTA evaluations (3 trials × 1 iteration) = **15 evaluations total**.
- **Finding:** The report's PO-2 numerators/denominators (7/7, 4/4, 11/11) are **not derivable from the raw records**. The raw-consistent numbers are 12/12 Ṛta and 3/3 OpenSTA evaluations (15/15 evidence records produced). The OpenSTA "4/4" would require an evaluation from the failed T2-OpenSTA-R2 trial, which recorded 0 calls. This is a **reporting inconsistency**, not a raw-data inconsistency.

## 5. Trial-by-Trial Verification

Independent recomputation confirms every trial's status, iteration count, Oracle-call count, verification decision, and failure kind in the raw JSON. The script's `analyze_trials()` output (`analysis.json`) is consistent with `raw_trials.json`.

## 6. Protocol Compliance

| P169 Requirement | P170 Actual | Compliance |
|------------------|-------------|------------|
| 2 tasks × 2 Oracles × 2 replications = 8 trials | 8 trials planned | YES |
| Task matrix (T1/T2 × Rta/OpenSTA) | Exact matrix executed | YES |
| Max iterations = 3 | 3 (Ṛta), 1 (OpenSTA) | YES |
| Counterbalanced order (§9) | Ṛta-first in BOTH task blocks | **NO (deviation)** |
| 1 bounded retry per failed trial (§8) | 0 retries | **NO (deviation)** |
| Both attempts recorded | Single attempt only | **NO (deviation)** |
| initial_oracle_result recorded (schema) | Field absent from all records | **NO (deviation)** |
| retry_count recorded (schema) | Field absent from all records | **NO (deviation)** |
| temperature 0.0, max_tokens 4096 | temperature 0.0 (default) | PARTIAL (max_tokens not set) |

## 7. Protocol Deviation

```
PROTOCOL DEVIATION (documented):
1. Retry: P169 froze 1 bounded retry per failed trial. P170 executed 0 retries.
   The retry logic was not implemented in run_experiment.py, and retry_count
   is absent from every trial record.
2. Counterbalancing: P169 §9 froze "Trials 1-4: Rta first; Trials 5-8:
   OpenSTA first." The executed order was Rta-first in both blocks
   (T1-Rta, T1-Rta, T1-OpenSTA, T1-OpenSTA, T2-Rta, T2-Rta, T2-OpenSTA,
   T2-OpenSTA). OpenSTA never ran first.
3. Schema: initial_oracle_result and retry_count fields required by the
   frozen data schema are absent from all records.
```

The retry deviation alone would weaken but not destroy the pilot. The findings below in §8–§9 are more consequential.

## 8. Primary Outcome Verification

### PO-1 — Pipeline Completion Quality

Reported (recomputed from raw, consistent): T1-Ṛta 0 ROBUST/2 MARGINAL; T1-OpenSTA 2 ROBUST; T2-Ṛta 0 ROBUST/2 MARGINAL; T2-OpenSTA 1 ROBUST/1 FAILED.

**Verification:** The "ROBUST" classification requires "Oracle evaluation improves" (P169 §7). For OpenSTA trials, the improvement claim rests on "already clean" — see §9. Classification is **not defensible as measured**.

### PO-2 — Evidence Contract Compatibility

Raw-consistent: 15/15 Oracle evaluations produced EvidenceArtifacts that entered the EvidenceNormalizer. Ṛta evidence carried `evidence_scope="UNSUPPORTED"` (12 evaluations) — this is the pre-existing Ṛta adapter SCOPE_MAP default, not a P170 change. OpenSTA evidence carried `evidence_scope="VALIDATED"` (3 evaluations).

**Verification:** Evidence entry occurred for both authorities. The report's 11/11 figure is unreconcilable with raw data (see §4.2).

### PO-3 — Oracle-Detected Improvement

**METRIC IMPLEMENTATION ISSUE (confirmed).** P169 §7 froze PO-3 as: "Initial Oracle evaluation vs final Oracle evaluation per trial" with Oracle-specific definitions (Ṛta: ERROR finding count reduction; OpenSTA: WNS improvement). The execution script **never invoked either Oracle on the initial SDC** — `run_trial()` invokes `invoke_opencode()` first and only then calls the Oracle on the generated candidate. No `initial_oracle_result` exists anywhere in the raw records.

Consequences:
- The OpenSTA "already clean / IMPROVED" classification in the P170 report is an **inference**, not a measurement: no initial evaluation was recorded to compare against.
- The Ṛta "NOT_IMPROVED" classification (error count constant at 1) is a byproduct of the candidate-generation failure (§9), not a measurement of revision effectiveness.
- PO-3 as frozen **cannot be computed** from the collected data.

## 9. PO-3 Metric Audit — Candidate Validity (CRITICAL)

**Finding:** All 15 candidate evaluations across all 7 completed trials were evaluated on **conversational text, not SDC**. Independent scan of `raw_trials.json`:

```
sdc_like_candidates: 0/15   (none of the 15 candidates contain any SDC
syntax: create_clock, set_input_delay, set_output_delay, set_clock, ...)
```

Example candidates (verbatim):
- `"Understood. I can help you with SDC (Synopsys Design Constraints) for VLSI design. What do you need?"`
- `"Ready to help with SDC constraint authoring for VLSI design. What do you need?"`

**Implications:**

1. **The revision loop never operated on a valid SDC.** The model (`opencode/mimo-v2.5-free`) returned conversational filler in 15/15 invocations. The P170 report's statement "The LLM proposed SDC variations but did not resolve the constraint incompleteness" is **not supported** — no SDC variation was ever proposed.
2. **The OpenSTA ACCEPT results are vacuous.** With no `create_clock` in the candidate, OpenSTA analyzed an *unconstrained* design → no constrained paths → WNS=0.0 → `timing_clean` → ACCEPT. This does **not** mean the candidate satisfied timing; it means no timing constraint was applied. The P170 report's claim that "the initial candidate already satisfied timing constraints" misreads the result.
3. **The designed T2 aggressive-clock (0.05 ns) scenario was never actually tested.** P163 established that 0.05 ns produces a −0.10 ns violation. In T2-OpenSTA-R1 the initial aggressive SDC was replaced by conversational text before OpenSTA ran, so the aggressive clock never reached OpenSTA. The intended PASS/VIOLATION contrast across the task matrix was not exercised.
4. **The Ṛta ERROR finding (SDC-001 "No create_clock defined") is a consequence of the garbage candidate, not the designed task perturbation.** The P170 report describes the finding as "incomplete constraints — missing input/output delays"; the raw record shows the sole ERROR is "No create_clock defined", which exists because the candidate contains no SDC at all.

**Verdict:** The experimental manipulation — evaluating EGER's evidence-grounded revision loop against two authorities on valid SDC artifacts — **did not occur**. The collected observations document a harness/candidate-generation failure, not architecture behavior on the frozen tasks.

## 10. Evidence Contract Audit

- Ṛta: raw evidence → EvidenceNormalizer → EvidenceArtifact → VerificationGate. Evidence entered at `UNSUPPORTED` scope (pre-existing contract); VerificationGate rejects UNSUPPORTED/INSUFFICIENT scope by design (`gate.py` §85). REJECT decisions are consistent with the established contract.
- OpenSTA: raw evidence → EvidenceNormalizer → EvidenceArtifact → VerificationGate. Evidence entered at `VALIDATED` scope; ACCEPT decisions are consistent with the adapter's contract on the (vacuous) WNS=0.0 result.
- Both authorities entered the same evidence pipeline without authority-specific architectural changes. This is retained as a **technical** observation.

## 11. Authority Separation Audit

- Ṛta findings remained constraint-quality findings (SDC-001 etc.).
- OpenSTA findings remained timing findings (WNS/TNS/timing_clean).
- No universal Oracle score was constructed.
- VerificationGate remained the sole final authority.
- No Oracle was used to reinterpret the other's result.
- **PASS** — authority separation held; this was not the failure mode.

## 12. Replication Consistency

| Pair | Model outputs | Oracle outcomes | Decision | Consistent? |
|------|---------------|-----------------|----------|-------------|
| T1-Ṛta R1 vs R2 | Different filler text | 1 ERROR each, 3 iters | REJECT both | YES (mechanically) |
| T1-OpenSTA R1 vs R2 | Different filler text | WNS=0.0, 1 iter | ACCEPT both | YES (mechanically) |
| T2-Ṛta R1 vs R2 | Different filler text | 1 ERROR each, 3 iters | REJECT both | YES (mechanically) |
| T2-OpenSTA R1 vs R2 | R1 filler; R2 provider failure | WNS=0.0 (R1); no data (R2) | ACCEPT / FAILED | NO PAIR |

Replications are mechanically consistent (same Oracle outcome pattern per cell), but both members of each pair evaluated **invalid candidates**, so consistency is consistency of a failed manipulation. No statistical reliability claim is made — descriptive only, as frozen.

## 13. Model Stochasticity

- The model produced different conversational text across replications — consistent with stochastic generation (temperature 0.0 does not guarantee identical output).
- Oracle determinism (same input → same output) was previously established in P163/P167 and was not re-tested in P170 (correctly — no new experiment in this gate).
- Separated: LLM output variability = OBSERVED; Oracle determinism = ESTABLISHED ELSEWHERE; pipeline outcome consistency = mechanically observed on invalid inputs.

## 14. Failure Analysis

| Trial | Failure kind | Retry executed | Retry allowed (P169) | Deviation |
|-------|--------------|----------------|----------------------|-----------|
| T2-OpenSTA-R2 | PROVIDER_FAILURE (empty model output) | 0 | 1 | YES |

The single failure is honestly recorded with 0 calls/0 iterations. The absence of the bounded retry is a **harness limitation** (retry logic never implemented), already disclosed in P170. It does not, by itself, invalidate the pilot — but it is one of three documented deviations (§7).

## 15. Synthetic Substrate Limitations

- 3-cell gate-level netlist (INVX1 → AND2X1 → DFFX1) with synthetic Liberty.
- Established (P163–P167) as a *technical* substrate for demonstrating OpenSTA execution and PASS/VIOLATION discrimination.
- **Cannot** support claims about production RTL, production STA, large SoCs, arbitrary SDCs, or arbitrary VLSI tasks.
- Additionally, the substrate's "no clock → WNS 0.0 → timing_clean" behavior means an unconstrained candidate trivially passes — a limitation that interacts badly with the candidate-generation failure and should be documented as a confounder for any future run.

## 16. Threats to Validity

- **Internal validity:** Compromised. The Oracle condition was isolated, but the candidate-generation failure means observed outcomes reflect harness behavior, not the Oracle-condition effect.
- **Construct validity:** Compromised. The construct "evidence-grounded revision under two authorities" was not measured because no valid SDC was ever evaluated.
- **External validity:** Extremely limited regardless (synthetic substrate, single free model, WSL2 environment); not the primary concern here.
- **Statistical conclusion validity:** N/A — descriptive pilot; no inferential statistics were used or are appropriate.

## 17. Claim-Level Assessment

| Level | Claim | Supported? |
|-------|-------|-----------|
| 0 | Technical execution demonstrated (both Oracle executables work) | YES (P163–P167; P170 shows invocation occurred) |
| 1 | EGER pipeline operated with both Oracles | PARTIAL — pipeline executed mechanically, but on invalid candidates |
| 2 | Pipeline operated with both authorities across tasks with evidence production | **NO** — evidence was produced, but no valid SDC was ever evaluated; the intended task contrast never occurred |
| 3 | Consistent behavior across replicated conditions | NO |
| 4 | Generalization beyond tested tasks | NO |

**P170's stated "Level 2" claim is NOT supported by the collected data.**

## 18. RQ-4 Boundary

RQ-4 remains **CLOSED**. P171 does not reopen or reinterpret it. P170's results are not evidence against the prior RQ-4 conclusion.

## 19. C0–C5 Boundary

Unchanged: C0 ESTABLISHED, C1 ESTABLISHED, C2 PARTIALLY SUPPORTED, C3 NOT JUSTIFIED, C4/C5 DEFERRED. P171 modifies none of these.

## 20. Final Research Decision

**P171 — RQ-5 PILOT INCONCLUSIVE**

Rationale:
1. **CRITICAL — Candidate-generation failure:** 15/15 evaluated candidates were conversational text, not SDC. The core manipulation (evidence-grounded SDC revision under two authorities) never occurred.
2. **CRITICAL — Vacuous OpenSTA ACCEPTs:** No clock in the candidate → unconstrained design → trivial WNS=0.0 clean. The T2 aggressive-clock scenario was never tested.
3. **HIGH — PO-3 never measured:** No initial Oracle evaluation was recorded; "already clean/IMPROVED" is inference, not measurement.
4. **HIGH — Report/raw reconciliation:** PO-2 figures (11/11, 7/7, 4/4) are not derivable from raw data (15 evaluations: 12 Ṛta + 3 OpenSTA).
5. **MEDIUM — Protocol deviations:** 0 retries (allowed: 1); counterbalancing not implemented as frozen; schema fields missing.
6. **RETAINED technical residue:** Both Oracle adapters execute within the pipeline and produce evidence entering the same contract (Level 0/1 technical observations, consistent with P164–P167).

The retry deviation alone would not have forced INCONCLUSIVE; the candidate-generation failure and unmeasured PO-3 do.

### Maximum Defensible Claim

> EGER's Oracle adapters for Ṛta (constraint quality) and OpenSTA (timing) are individually executable, and each can produce evidence that enters the existing EGER evidence contract. The P170 pilot data does not establish that the EGER evidence-grounded revision loop operated on valid SDC artifacts under either authority, because the LLM candidate generator returned non-SDC text in all recorded evaluations.

### Claims NOT Supported

- Oracle interchangeability / equivalence — NOT SUPPORTED
- Universal EGER generalization — NOT SUPPORTED
- Production-scale generalization — NOT SUPPORTED
- Causal claims about Oracle-condition effects — NOT SUPPORTED
- Level 2 architecture-generalization claim (as stated in P170/CHANGE-041) — NOT SUPPORTED

### Future Research Recommendation (documented only, NOT executed)

A future controlled replication should, before any trial:
1. Validate that the model output parses as an SDC (contains `create_clock` etc.) before Oracle invocation — reject/handle non-SDC output deterministically.
2. Implement the frozen bounded retry and record `retry_count`.
3. Implement counterbalancing as frozen (OpenSTA-first block).
4. Record `initial_oracle_result` on the initial SDC before any revision (required for PO-3).
5. Use a model/prompt configuration demonstrated to return SDC text, or record the failure as a harness finding rather than an architecture result.
6. Treat "no clock → WNS 0.0 → timing_clean" as a substrate confounder (e.g., require a defined clock for a valid timing evaluation).

## Research Boundary

```
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: NO (review gate only; P170 data reviewed, not extended)
C0-C5 conclusions changed: NO
Oracle comparison performed: NO (no new comparison executed)
VerificationGate authority changed: NO
Epistemic-state logic added: NO
Authorization logic added: NO
Experimental data modified: NO (raw_trials.json / analysis.json untouched)
```

## Test Regression

`python -m pytest tests -q` → **864 passed** (unchanged; no production code modified).

Note: bare `pytest -q` at the repository root triggers a collection internal error from the external `rta-constraint-intelligence/smoke_test.py` (module-level `sys.exit(0)`), which predates this gate; the established regression scope is the `tests/` directory.

## Git Status

- No files staged by this gate.
- `Universal_Principles_Library/` untouched (untracked, as before).
- `raw_trials.json`, `analysis.json` remain local-only.
- This review and CHANGE-042 are the only new tracked research records intended.

## Decision

```
P171 — RQ-5 PILOT INCONCLUSIVE
```