# EGER-CHANGE-050

- **Gate**: P178 — RQ-5 Shared-Candidate Pairing Repair & Readiness
- **Baseline**: `391aad7ee685b6490c703a1f72b83feea865ecfb` (P177)
- **Purpose**: Correct the P177 item-2 overclaim and make every
  shared-candidate identity the frozen protocol guarantees mechanically
  true and testable. No protocol change; no PILOT-002 execution.
- **Decision**: **READY** (corrected item-2 definition supersedes P177);
  separate user authorization still required before PILOT-002.

## P177 overclaim conceded and corrected

P177 item 2 claimed cross-arm candidate byte-identity. The frozen P169
protocol (experimental unit = one per-Oracle pipeline execution;
`trial_id = T-<task>-<oracle>-<replicate>`; feedback-driven revision per
arm) provides candidate sharing at the task/initial-SDC level, not for
revised candidates. Corrected item-2 definition: task-shared initial
candidate across Oracle arms (byte-identical), single candidate path per
trial iteration, validity gated before Oracle evaluation.

## Mechanical repair implemented

- `harness/orchestrator.py` `audit_candidate_identity(records)`: verifies
  initial SDC bytes/hash per attempt, single gated candidate path per
  iteration (valid candidate bytes hash-match, or pre-evaluation rejection
  with no Oracle call), and cross-arm shared initial-SDC hashes per task.
  `run_matrix` returns the audit.
- `run_dryrun_matrix.py`: runs + records the audit.
- Fixture tests (+3): shared initial across Oracle arms (one hash per task
  == frozen task SDC hash), audit clean over 8 trials + retried attempt,
  and an Oracle spy proof that the Oracle received exactly the recorded
  candidate bytes in call order (no second generation, no substitution).

## Design-boundary finding (explicit)

Byte-identical REVISED candidates across the Ṛta/OpenSTA arms are not part
of the frozen protocol and cannot be enforced without changing the
experimental unit (paired-generation design). That is a protocol change,
out of scope for P178. READY here attests the protocol-true properties; a
paired-generation design, if desired, requires a new protocol-design gate.

## Revalidation

Fixture dry-run: 8/8 completed, identity audit ok=True,
shared_initial_across_arms=True, 1 bounded retry retained. EGER suite
878/878; harness suite 62/62.

## Research boundaries

```text
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: NO
C0-C5 conclusions changed: NO
VerificationGate authority changed: NO
EGER production code changed: NO (harness-scope only)
Frozen RQ-5 protocol changed: NO
PILOT-002 executed: NO
```

## Files

- Modified: `harness/orchestrator.py`, `run_dryrun_matrix.py`,
  `harness_tests/test_orchestrator.py`
- Added: `EGER-P178-RQ5-SHARED-CANDIDATE-PAIRING-REPAIR-AND-READINESS-REVALIDATION-001.md`,
  this file
