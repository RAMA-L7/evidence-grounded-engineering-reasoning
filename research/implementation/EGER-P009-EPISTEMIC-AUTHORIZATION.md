# EGER-P009 — Deterministic Epistemic State & Authorization Implementation Record

| Field | Value |
|---|---|
| ID | EGER-P009 |
| Previous | P008 adapter (`b4dffc3`) |
| Contracts | EGER-ORACLE-CONTRACT-001, EGER-SCHEMA-001 (unchanged), new EGER-EPISTEMIC-001 |
| Goal | Deterministic L2 (Epistemic State) + L3 (Authorization) before any LLM |
| Status | PASS — 17/17 P009 tests + 14/14 P008 regression = 31/31 overall |

## Implementation Scope (L2/L3 only)

- **L2 Epistemic State**: typed state model (HYPOTHESIS/VALIDATED/REFUTED/UNKNOWN), claim object with evidence linkage + baseline hash + transition history, deterministic transition engine, violation detection, immutable validated baseline, EVR raw counts.
- **L3 Authorization**: typed request/decision, deterministic policy (VALIDATED + FULL + SUCCESS + evidence linkage required for commit/promote), hard programmatic gate (no prompts), separate authorization violation metric.
- **Not implemented**: LLM, agents, subagents, planner, reflection, routing, memory retrieval, C0–C5, C6, benchmark, experiment runner, OpenCode integration, git commit gates.

## Files Created

- `eger/epistemic/__init__.py`
- `eger/epistemic/state.py` — `EpistemicClaim`, `EpistemicTransition`, `ViolationRecord`, `create_hypothesis`, violation type constants, `VALID_STATES`, schema versions
- `eger/epistemic/transitions.py` — `EpistemicEngine`, `TransitionRequest`, `TransitionResult`, predicates `_can_support_validated/_refuted`, scope checks, REFUTED→VALIDATED new-evidence rule, baseline immutability, deterministic `evr()` metric
- `eger/authorization/__init__.py`
- `eger/authorization/gate.py` — `AuthorizationGate`, `AuthorizationRequest`, `AuthorizationDecision`, `AuthViolation`, policy: VALIDATED required, evidence_scope FULL required, oracle_status SUCCESS required
- `tests/test_epistemic_authorization.py` — 17 tests T-E001..T-E016 + integration + two-memories
- `research/schemas/EGER-EPISTEMIC-SCHEMAS.md` — schema families `eger.epistemic.v1 / eger.transition.v1 / eger.authorization.*`

## Evidence Requirements (deterministic rules, §7 of P009)

- `VALIDATED` requires: `oracle_status=SUCCESS` + `evidence_scope=FULL` + no error findings. All other scopes (PARTIAL/INSUFFICIENT/UNSUPPORTED) or oracle failures → reject + violation.
- `REFUTED` requires: SUCCESS + scope FULL/PARTIAL + at least one error finding.
- `UNKNOWN` is the explicit state for INSUFFICIENT/UNSUPPORTED/ORACLE_FAILURE (not a silent stay in HYPOTHESIS).
- Missing evidence (`evidence_ids=[]` or `evidence=None`) → `MISSING_EVIDENCE`/`NO_EVIDENCE_TO_VALIDATED`.

These predicates are pure functions (`_can_support_validated`, `_can_support_refuted`) with no probabilistic scoring.

## Immutability & Provenance

- First HYPOTHESIS→VALIDATED stores `baseline_evidence_hash` + `baseline_evidence_ids`.
- Subsequent `VALIDATED→VALIDATED` with different supporting ids is treated as revalidation; allowed only if new evidence also satisfies VALIDATED predicate; otherwise `BASELINE_REPLACEMENT` violation and baseline unchanged.
- Every transition produces `EpistemicTransition` with deterministic `transition_id`, provenance, reason. Every rejection produces `ViolationRecord` with machine-readable type.

## Authorization Boundaries

- L3 does NOT override evidence: commit/promote requires VALIDATED. Evidence INSUFFICIENT → REJECTED even if requested. Proven by T-E013.
- `force_approve` helper exists solely to record authorization violations for testing — real gate never force-approves.
- Proposal (future LLM) is separate from Authorization: a request cannot become APPROVED because its proposer claims correctness; policy checks epistemic state, not prose.

## Two-Memories Verification (T-E014)

Research memory = `research/RESEARCH_LEDGER.md` (version-controlled history of EGER decisions).
Engineering memory = `EpistemicEngine` in-memory/file-backed claim store.
Test verifies: ledger does not contain engineering claim IDs, engine does not contain ledger content — representations are separate with distinct owners/schemas/lifecycles.

## Test Strategy & Results

| Test | Description | Result |
|---|---|---|
| T-E001 | initial hypothesis | PASS |
| T-E002 | validated with sufficient evidence (FULL, no errors) | PASS |
| T-E003 | refuted with contradictory evidence | PASS |
| T-E004 | insufficient → UNKNOWN, VALIDATED rejected | PASS |
| T-E005 | oracle failure cannot validate | PASS |
| T-E006 | unsupported cannot validate | PASS |
| T-E007 | missing evidence rejected, violation detectable | PASS |
| T-E008 | REFUTED→VALIDATED requires new evidence | PASS |
| T-E009 | validated baseline immutable | PASS |
| T-E010 | deterministic transition (same inputs → same decision) | PASS |
| T-E011 | authorization approved (VALIDATED + FULL) | PASS |
| T-E012 | authorization rejected (non-VALIDATED) | PASS |
| T-E013 | authorization cannot override evidence | PASS |
| T-E014 | two memories separate | PASS |
| T-E015 | schema compliance (versions, required fields) | PASS |
| T-E016 | epistemic violation detection + EVR raw counts | PASS |
| +integration | real EvidenceOracle evidence still produces correct scope | PASS |

Total: 17/17 P009 + 14/14 P008 regression = **31/31 overall**.

## EVR & Authorization Violation Metrics

- **EVR** (`EpistemicEngine.evr()`): `{attempted_transitions, violations, evr = violations/attempted, violations_by_type{...}}` — PROVISIONAL denominator definition per P009 §45 (attempted transitions). Raw counts exposed for future experiments.
- **Authorization violations** (`AuthorizationGate.violation_stats()`): `{attempted_authorizations, authorization_violations, auth_violation_rate, violations_by_type, decisions{APPROVED, REJECTED}}` — separate from EVR per §46.

Both metrics are deterministic and machine-readable; no subjective post-hoc judgment required for the counts.

## RTA & EvidenceOracle Integrity

- EvidenceOracle adapter **not modified** (git diff on `eger/oracle/adapter.py` → empty).
- RTA before P009 tests: `3b5c2f2` `main` 19 dirty — after: `3b5c2f2` `main` 19 (no mutation).
- L2/L3 consume `EvidenceArtifact`/`OracleFailure` via `EvidenceOracle.validate()` interface — never directly call RTA from L2/L3 (P009 §2).

## Deviations & Open Questions

- No deviations from P009 spec; no contract v0.2 modification; no EGER-CHANGE required.
- `AMBIGUOUS` and `INSUFFICIENT_EVIDENCE` as explicit states evaluated per §5 but deferred for P009 minimal (represented as `UNKNOWN` with associated evidence).
- Schema versioning: no modification to EGER-SCHEMA-001; new family EGER-EPISTEMIC-001 created separately per §26 guidance.

## Non-Goals Preserved

- No LLM, no agents, no reflection, no memory retrieval, no routing, no C0–C5/C6, no benchmark, no file commits. Deterministic reference system established before probabilistic engineer.
