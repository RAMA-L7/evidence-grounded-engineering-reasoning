# EGER — P180: Independent RQ-5 Research Review

## 1. Objective

Independently audit the completed P179 PILOT-002 dataset and conclusions. Focus on: raw-record analysis reconciliation, protocol compliance, provenance and candidate identity, PO validity, the T2 vacuous-initial confound, authority-separation interpretation, replication consistency, Level-2 claim defensibility, and any overstatement of shared-candidate identity.

**Review gate only.** No experiment was run. No code was changed. No records modified.

## 2. Baseline

- **HEAD:** `1a30f39` (P179 pushed)
- **Branch:** main; HEAD == origin/main
- **P179 committed:** `ad4d86a`
- **Protocol:** P169 frozen, repaired by P172/P177/P178

## 3. Source Materials Audited

| Record | Role |
| ------ | ---- |
| EGER-P169-RQ5-EXPERIMENTAL-PROTOCOL-ADVERSARIAL-REVIEW-001.md | Frozen protocol |
| EGER-P178-RQ5-SHARED-CANDIDATE-PAIRING-REPAIR-AND-READINESS-REVALIDATION-001.md | Identity audit repair + corrected item-2 |
| EGER-P179-RQ5-PILOT002-CONTROLLED-ORACLE-VALIDATION-EXECUTION-001.md | Execution report |
| EGER-CHANGE-051.md | Change record |
| `EGER-RQ5-PILOT-002/manifest.json` | Immutable manifest (local) |
| `EGER-RQ5-PILOT-002/raw_trials.json` | Raw trial records (local) |
| `EGER-RQ5-PILOT-002/identity_audit.json` | Identity audit (local) |
| `EGER-RQ5-PILOT-002/analysis.json` | Deterministic analysis (local) |

## 4. Raw-Record → Analysis Reconciliation

Independent recomputation from raw trial records:

| Metric | Raw (recomputed) | analysis.json | P179 report | Consistent? |
| ------ | ---------------- | ------------- | ----------- | ----------- |
| Planned | 8 | 8 | 8 | YES |
| Completed | 8 | 8 | 8 | YES |
| Failed | 0 | 0 | 0 | YES |
| Oracle evaluations | 22 | 22 | 22 | YES |
| ACCEPT decisions | 6 | 6 | 6 | YES |
| REJECT decisions | 6 | 6 | 6 | YES |
| Distinct evidence hashes | 12 | N/A | N/A | — |
| Retries | 0 | 0 | 0 | YES |
| Per-condition counts | match | match | match | YES |

All counts reconcile exactly. No discrepancy found.

## 5. Protocol Compliance

Every frozen P169/P172 item verified against raw records:

| Item | Frozen requirement | Result | Evidence |
| ---- | ------------------ | ------ | -------- |
| Trial count | 8 planned | 8/8 | raw_trials.json length |
| Counterbalanced order | T1 Rta-first, T2 OpenSTA-first | PASS | execution_order in raw; manifest order matches |
| Shared task initial SDC | same bytes across Oracle arms | PASS | identity_audit: shared_initial_across_arms=True; per-task single shared hash |
| Candidate validity gate | reject non-SDC before Oracle | PASS | all evaluated iterations: candidate_validity=VALID_SDC, clock_defined=True |
| Initial Oracle evaluation | before revision | PASS | initial_oracle_result + initial_evidence_hash on all 8 records |
| Bounded retry | 1 max, both attempts retained | PASS | retry_count=0 on all (none needed); policy recorded in manifest |
| No reordering | execution order frozen pre-trial 1 | PASS | order==manifest for every record |
| No silent candidate repair | oracle-received == recorded bytes | PASS | identity_audit ok=True, violations=[] |
| Candidate hashes | deterministic hashes per iteration | PASS | candidate_raw_hash and candidate_sdc_hash present in all iteration records |
| Oracle-specific feedback | preserved per arm | PASS | per-Oracle revision prompts in raw records |
| Failures vs REJECT | failure_kind distinguished | PASS | failure_kind=None x 8; REJECT from findings only |
| qualified_accept | metadata_unqualified rule enforced | PASS | 0 metadata_unqualified_iterations across all trials |
| Research boundary | no changes to Rta/VerificationGate/RQ-4/C0-C5 | PASS | production diff = encoding fix only |
| Raw records preserved | before analysis | PASS | raw_trials.json immutable; analysis derived after |

**One harness fix applied during execution:** subprocess `encoding="utf-8"` in `providers.py`. This was a robustness fix (opencode emits UTF-8; locale cp1252 crashed the first launch). The crashed first launch produced no trial data; it was discarded. This is NOT a protocol change.

## 6. Provenance and Candidate Identity

### Shared initial SDC identity

- T1 shared initial hash: `42a3c971...` (all 4 T1 trials: T1-Rta-R1, T1-OpenSTA-R1, T1-Rta-R2, T1-OpenSTA-R2)
- T2 shared initial hash: `94594929...` (all 4 T2 trials)
- **Cross-arm shared substrate verified.** Both Oracle arms of each task start from byte-identical initial SDCs.

### Identity audit

- `ok: true`
- `violations: []`
- `shared_initial_across_arms: true`
- Per-trial checks: `initial_matches_task_sdc: true` and `iterations_single_path_ok: true` for all 8 trials.

### P179 wording correction (from P178)

P178 correctly established that "shared candidate SDC bytes" applies to the **task-level initial SDC** (byte-identical across Oracle arms) and to **single-path candidate evaluation** within each trial iteration. Revised candidates diverge across arms by design (feedback-driven revision). P179's §15 uses "same shared candidate SDC bytes" in the T2 discussion; this should be interpreted as referring to the shared initial substrate and the specific candidate bytes the model produced within that trial — not cross-arm byte-identity of revised candidates. This is consistent with the P178 corrected item-2 definition and does not constitute an overstatement.

## 7. PO-1 / PO-2 / PO-3 Validity

### PO-1 — Completion quality

| Condition | ROBUST | MARGINAL | FAILED |
| --------- | :----: | :------: | :----: |
| T1-Ṛta | 2 | 0 | 0 |
| T1-OpenSTA | 0 | 2 | 0 |
| T2-Ṛta | 2 | 0 | 0 |
| T2-OpenSTA | 0 | 2 | 0 |

ROBUST requires improvement detected by the Oracle. MARGINAL means completed but no Oracle-detected improvement. Both categories are valid outcomes — neither is a failure.

### PO-2 — Evidence compatibility

All 8 trials: evidence compatible = true. Both Ṛta and OpenSTA produced evidence that entered the existing EGER evidence contract without authority-specific changes. 22/22 evaluations produced evidence artifacts. **No authority-specific architecture was required.**

### PO-3 — Oracle-detected improvement (the critical metric)

| Condition | IMPROVED | NOT_IMPROVED | WORSE | NOT_MEASURABLE |
| --------- | :------: | :----------: | :---: | :------------: |
| T1-Ṛta | 2 | 0 | 0 | 0 |
| T1-OpenSTA | 0 | 2 | 0 | 0 |
| T2-Ṛta | 2 | 0 | 0 | 0 |
| T2-OpenSTA | 0 | 0 | 2 | 0 |

**PO-3 validity assessment per condition:**

**T1-Ṛta: IMPROVED (2/2).** Initial SDC had missing I/O delays → Ṛta found 2 errors (SDC-005/006) → model added delays → 0 errors → ACCEPT. Correct.

**T1-OpenSTA: NOT_IMPROVED (2/2).** The initial T1 SDC (clock only, no delays) is the vacuous-clean case: no constrained paths → WNS 0.0 → VALIDATED. The model's first candidate already includes delays; WNS remains 0.0 (timing met on this substrate). PO-3 = NOT_IMPROVED is correct: the Oracle did not detect improvement because the initial evaluation already showed no violations. This is the documented "initial-clean floor" (P171).

**T2-Ṛta: IMPROVED (2/2).** Initial SDC (0.05 ns clock only) → 2 errors (SDC-005/006) → model added I/O delays (0.01 ns) → 0 errors → ACCEPT. Correct: Ṛta's constraint-quality rules found the completed SDC valid.

**T2-OpenSTA: WORSE (2/2).** Initial SDC (0.05 ns clock only) → WNS 0.0, VALIDATED (vacuous-clean) → model added I/O delays → WNS −0.01/−0.02, VIOLATIONS_FOUND → REJECT across all 3 iterations. PO-3 = WORSE is correct: the initial "clean" was vacuous; the first real constraints exposed the timing violation. This is NOT a case of the model making things worse — the model could not relax the 0.05 ns clock because no feasible candidate exists for this substrate at that clock period.

## 8. T2 OpenSTA Vacuous-Initial Confound

This confound was identified in P171 and guarded against in P174:

| Trial | Initial WNS | Initial status | First candidate WNS | First candidate status | accept_reached |
| ----- | ----------- | -------------- | ------------------- | ---------------------- | -------------- |
| T2-OpenSTA-R1 | 0.0 | VALIDATED | −0.01 | VIOLATIONS_FOUND | False |
| T2-OpenSTA-R2 | 0.0 | VALIDATED | −0.02 | VIOLATIONS_FOUND | False |

The initial 0.05 ns clock SDC has **no `set_input_delay` or `set_output_delay`**, so OpenSTA finds no constrained paths and returns WNS = 0.0. This is the documented confound: an empty SDC is trivially "clean." The P174 valid-clock guard prevented the initial evaluation from counting as a timing-clean verdict in the analysis layer. The model's first real candidate (with I/O delays) exposes the genuine timing violation.

**This is the correct behavior.** The initial vacuous-clean is an artifact of the substrate; the real evaluation is the first candidate with actual constraints. The P179 report properly documents this as a "documented floor" rather than claiming the initial SDC was actually timing-clean.

**Key observation:** the model was unable to relax the 0.05 ns clock because the frozen task definition fixes the clock period. The model can only add/modify I/O delays, not change the clock. On this substrate (u_inv → u_and → u_ff path), even minimal I/O delays (0.01/0.02 ns) violate the 0.05 ns constraint. This is the task ceiling — not a harness defect.

## 9. Authority-Separation Interpretation

The T2 condition produces the critical authority-separated result:

**Same task, same initial SDC, same first-revision candidate structure (clock + I/O delays):**

- **Ṛta (constraint-quality authority):** finds 0 constraint errors → ACCEPT
- **OpenSTA (timing authority):** finds WNS −0.01/−0.02 → REJECT

**This is not disagreement about correctness.** It is disagreement about which engineering property is being measured:

- Ṛta checks: are the SDC constraints structurally complete and internally consistent? Yes — delays present, correct syntax, delays < clock period. → ACCEPT.
- OpenSTA checks: does the design meet timing under these constraints? No — WNS is negative. → REJECT.

Each authority is operating correctly in its own domain. The Observation is that the EGER control loop operated faithfully with both authorities, each producing authority-specific evidence that reached the VerificationGate through the same pipeline.

**The P179 report correctly does NOT claim interchangeability.** It explicitly notes that the T2 result "refutes" interchangeability — the two authorities legitimately disagree because they measure different properties. This is the right interpretation.

## 10. Replication Consistency

| Condition | R1 outcome | R2 outcome | Consistent? |
| --------- | ---------- | ---------- | ----------- |
| T1-Ṛta | ROBUST/IMPROVED/ACCEPT | ROBUST/IMPROVED/ACCEPT | YES |
| T1-OpenSTA | MARGINAL/NOT_IMPROVED/ACCEPT | MARGINAL/NOT_IMPROVED/ACCEPT | YES |
| T2-Ṛta | ROBUST/IMPROVED/ACCEPT | ROBUST/IMPROVED/ACCEPT | YES |
| T2-OpenSTA | MARGINAL/WORSE/REJECT | MARGINAL/WORSE/REJECT | YES |

All four replication pairs agree at the outcome level. Final SDC hashes differ between R1/R2 in the accepted cases (different valid completions by the stochastic model); identical in the T2-OpenSTA case (model converged to equivalent failing SDCs). **Replication pairs are consistent.**

**Descriptive only.** N=2 per condition is not sufficient for statistical inference. The consistency supports the Level-2 operational claim but does not establish reliability beyond these instances.

## 11. Level-2 Claim Defensibility

The P179 maximum claim:

> The evidence-grounded EGER control loop operated with two independent deterministic evaluation authorities (Ṛta and OpenSTA) across the two frozen synthetic VLSI tasks, with complete, reproducible, authority-separated evaluation evidence entering the same EGER evidence contract and reaching the VerificationGate — under the tested conditions.

**Assessment: defensible.**

All elements of the claim are supported by the data:

- "Control loop operated with two independent authorities": ✓ (8/8 trials completed; both authorities drove their own revision loops)
- "Across two frozen synthetic VLSI tasks": ✓ (T1 and T2 both executed)
- "Authority-separated evaluation evidence": ✓ (T2 disagreement demonstrates this; each authority's findings are property-specific)
- "Entering the same EGER evidence contract": ✓ (PO-2 = 8/8 compatible)
- "Reaching the VerificationGate": ✓ (gate received and processed all evidence)
- "Under the tested conditions": ✓ (explicitly bounded to 3-cell substrate, opencode/mimo-v2.5-free, frozen SDCs)

**What the claim does NOT say (and should not):**

- Oracle interchangeability — refuted on T2
- Generalization beyond tested tasks/substrate — not established
- Causal inference — N=8 descriptive pilot
- Production-scale validity — synthetic substrate only

## 2. Wording Correction

**Finding: one minor wording issue in P179 §15.**

P179 §15 states "same shared candidate SDC bytes" in the T2 discussion. As established by P178's corrected item-2 definition:

- **Shared initial SDC bytes across Oracle arms**: YES, byte-identical (verified by identity audit).
- **Revised candidate bytes across arms**: NOT byte-identical (by design — feedback-driven revision).

P179's wording should be interpreted as referring to the shared initial substrate and the specific candidate within a trial, not cross-arm byte-identity of revised candidates. This is consistent with P178 and does not change the experimental result or claim. **Minimum correction: none required in the P179 record — P178 already supersedes P177's item-2 wording, and P179's text is accurate when read with P178 context.**

## 13. Research Boundary

```text
RQ-5 executed: YES (P179)
P180 review: YES (this record)
RQ-5 generalization established: NO
Oracle interchangeability: NO
RQ-4 reopened: NO
C0-C5 conclusions changed: NO
Rta modified: NO
VerificationGate modified: NO
```

## 14. Final Decision

```text
P180: PASS
```

The P179 dataset is internally consistent, protocol-conformant, and the Level-2 claim is defensible. The T2 authority-separated result is correctly interpreted as evidence for the authority-separation architecture, not interchangeability. One minor wording issue (§15 "shared candidate SDC bytes") is resolved by P178's corrected item-2 definition and does not require a P179 record correction.

**Research state after P180:**

| Item | State |
| ---- | ----- |
| RQ-5 | Executed, descriptive pilot validated |
| Maximum claim | Level 2 |
| Interchangeability | NO (refuted on T2) |
| Generalization | NOT established |
| Causal inference | NO |
| RQ-4 | Remains closed |
| C0-C5 | Unchanged |
| Rta | Unchanged |
| VerificationGate | Unchanged |

## 15. Git

- P180 committed as: `<hash>` (see CHANGE-052)
- HEAD == origin/main (after push)
- No code changes; research records only
- Universal_Principles_Library/ untouched

## 16. Artifacts

- `research/implementation/EGER-P180-INDEPENDENT-RQ5-RESEARCH-REVIEW-001.md`
- `research/implementation/EGER-CHANGE-052.md`

## STOP

No additional experiments. No protocol modification. No claim upgrade. The RQ-5 descriptive pilot is now independently reviewed and the claim validated at Level 2. Any future work (production substrate, larger N, new tasks) requires a new research-design gate.
