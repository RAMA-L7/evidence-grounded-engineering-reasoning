# EGER-P178 — RQ-5 Shared-Candidate Pairing Repair & Readiness Revalidation

- **Gate**: P178 — RQ-5 Shared-Candidate Pairing Repair & Readiness
- **Governing records**: P169–P177 + CHANGE-040..049
- **Date**: 2026-09-05
- **Baseline**: `391aad7ee685b6490c703a1f72b83feea865ecfb` (P177)
- **Decision**: **READY** — with the corrected, protocol-true definition of
  checklist item 2 (this record supersedes the P177 item-2 wording). A
  separate, explicit user authorization is still REQUIRED before the first
  PILOT-002 trial. If the user instead wants the stronger paired-generation
  design described in §4, that requires a new protocol-design gate.

---

## 1. Objective

Address the P177 review finding that checklist item 2 ("same candidate SDC
bytes evaluated by both Oracles") was marked PASS without being mechanically
testable. Make every shared-candidate identity property the frozen P169/P172
protocol actually guarantees mechanically true, enforced by a post-run audit
and fixture tests — without changing the frozen protocol.

## 2. The P177 Overclaim — Conceded and Corrected

P177's item-2 evidence claimed the runner "passes the identical extracted
candidate to whichever Oracle is bound," which reads as byte-identity of
candidates across the Ṛta and OpenSTA trials of a task. **That stronger
claim is not what the frozen protocol provides, and P177's wording
overclaimed it.** The correction:

### 2.1 What the frozen P169 protocol actually specifies (authoritative text)

- Experimental unit: "One trial = one complete EGER pipeline execution"
  (P169 §12), with `trial_id = T-<task>-<oracle>-<replicate>` — trials are
  per-Oracle pipeline runs.
- "Both Oracles can evaluate the same SDC" (P169 §6) refers to the **task
  level**: the task SDC substrate (T1 incomplete clock constraints, T2
  aggressive clock + missing constraints) is common to both authority
  conditions, and both Oracles produce findings on it — "findings differ by
  property — by design."
- The revision loop is **feedback-driven per arm**: the model revises using
  the evidence of the arm's own Oracle (Ṛta errors SDC-005/006 vs OpenSTA
  WNS/slack). Revised candidates therefore diverge across arms by design.
- The maximum claim (Level 2) is about the pipeline operating under each
  authority ("Pipeline completes with both Oracles on both tasks, with
  evidence production") — not about paired outcome differences.

### 2.2 Corrected item-2 definition (protocol-true)

1. **Task-shared initial candidate across Oracle arms** — byte-identical:
   every trial of a task starts from the frozen initial SDC, identical
   across the Ṛta and OpenSTA trials of that task.
2. **Single candidate path per trial iteration** — each iteration generates
   exactly one candidate; the trial's Oracle evaluates exactly those bytes;
   no Oracle-specific candidate variant, no silent repair, no second
   generation triggered by evaluation.
3. Candidate validity is checked **before** either Oracle evaluation.

## 3. Repair — Mechanical Identity Layer

### 3.1 `harness/orchestrator.py` — `audit_candidate_identity(records)`

Deterministic post-run audit over the raw trial records (including every
retry attempt). Returns `{ok, violations, checks, shared_task_initial_hashes,
shared_initial_across_arms}`:

- **Initial-candidate identity**: every attempt's `initial_sdc` bytes equal
  the frozen task SDC and `initial_sdc_hash` matches.
- **Single-path per iteration**: each iteration is either (a) a VALID_SDC
  candidate whose recorded bytes hash to `candidate_sdc_hash` and which was
  evaluated, or (b) a validity-gate rejection (no candidate bytes, no Oracle
  call). Any drift is a violation.
- **Cross-arm shared substrate**: same-task trials share one initial-SDC
  hash across the Ṛta and OpenSTA arms.
- `run_matrix` now returns `identity_audit` alongside records + analysis.

### 3.2 Fixture tests (`harness_tests/test_orchestrator.py`, +3)

- `test_shared_initial_sdc_across_oracle_arms` — asserts one shared initial
  hash per task across all four trials (both Oracle arms) and equality with
  the frozen task SDC hash.
- `test_identity_audit_ok_on_full_matrix` — audit passes on all 8 trials +
  the retried attempt.
- `test_oracle_received_exact_recorded_candidate_bytes` — spy proof: the
  Oracle received, in exact call order, precisely the recorded bytes
  (initial SDC then one gated candidate per evaluated iteration) — no extra
  call, no substituted bytes, evaluation never triggered a second
  generation.

## 4. Design-Boundary Finding (explicit, not hidden)

The P178 review asked for byte-identity of revised candidates across the
Ṛta and OpenSTA trials of a task×replication. **The frozen protocol does not
and cannot provide that**: trials are per-Oracle pipeline executions with
feedback-driven revision (P169 §12), and the model is stochastic
(provider-default sampling, recorded P177 §6). Enforcing byte-identical
revised candidates across arms would require changing the experimental unit
— e.g., decoupling candidate generation from Oracle feedback (a paired-
generation design that evaluates a common candidate stream under both
authorities). That is a protocol change, explicitly out of scope for P178
("Do NOT change the frozen RQ-5 protocol").

Consequence for the design: the RQ-5 Level-2 claim ("the evidence-grounded
control loop operates with multiple independent deterministic authorities
under the tested conditions") does **not** require cross-arm revised-candidate
identity — it is a per-authority operational claim, and the frozen design
deliberately avoided paired outcome-difference inference. The shared
properties the design does require are now mechanically enforced (§3).

**Open decision for the user:** keep the frozen independent-loop design
(this gate's READY) or authorize a new protocol-design gate for a
paired-generation design. P178 does not take that decision.

## 5. Readiness Revalidation (18-item re-audit)

All 18 P169/P172 items remain PASS under the corrected definitions; item 2
now reads per §2.2 and is mechanically enforced (§3). Items unchanged from
P177 except item 2's evidence (this record supersedes the P177 wording).

## 6. Dry-Run (fixture only, re-run)

`run_dryrun_matrix.py` re-run with the identity audit:

- 8/8 trials completed in frozen counterbalanced order (asserted pre-run).
- Identity audit: `ok=True`, `shared_initial_across_arms=True`; per-task
  shared initial hashes: T1
  `42a3c9717440757c5956aaeb80825380c7ce3d42dbfff2fa512b88df3790d5a3`,
  T2 `94594929576437db5583df32fb5eba52fbc7643cd990dba96042e0e4f4cbd3c5`.
- 1 bounded retry exercised (T2-OpenSTA-R2, both attempts retained);
  17 Oracle evaluations = 17 evidence artifacts.
- Dry-run record (with identity audit) kept local — not committed.

## 7. Regression

| Suite | Result |
| ----- | ------ |
| EGER full suite | **878 passed** |
| Harness suite | **62 passed** (59 + 3 new identity tests) |

## 8. Research Boundary

```text
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: NO (fixture dry-run only)
C0-C5 conclusions changed: NO
Oracle comparison performed: NO
VerificationGate authority changed: NO
EGER production code changed: NO (harness-scope only)
Frozen RQ-5 protocol changed: NO
PILOT-002 executed: NO
```

## 9. Files Changed

- Modified: `harness/orchestrator.py` (identity audit; `run_matrix` returns it),
  `run_dryrun_matrix.py` (runs + records the audit),
  `harness_tests/test_orchestrator.py` (+3 identity tests)
- Added: this record, CHANGE-050

## 10. Decision

```text
READY
```

The P177 item-2 overclaim is corrected to the protocol-true definition and
every identity the frozen protocol guarantees is now mechanically enforced
by `audit_candidate_identity` and proven by fixture tests (shared task
initial across Oracle arms; single gated candidate path per trial iteration;
oracle-received bytes == recorded candidate bytes). Regressions green
(878 EGER / 62 harness); fixture dry-run passes with the audit clean.

**READY does NOT authorize execution.** A separate, explicit user
authorization is required before the first EGER-RQ5-PILOT-002 trial. If the
user prefers the stronger paired-generation design (byte-identical revised
candidates across arms), that is a protocol change requiring a new
protocol-design gate — not this gate.

## 11. Git

- Commit: `(P178 commit, see git log)`
- HEAD == origin/main: YES
- `Universal_Principles_Library/` untouched
- Local-only: `raw_trials.json`, `analysis.json`, `qualification_record.json`,
  `smoke_readiness_record.json`, `dryrun_records.json`
