# EGER Epistemic & Authorization Schemas — EGER-EPISTEMIC-001

| Field | Value |
|---|---|
| ID | EGER-EPISTEMIC-001 |
| Produced by | EGER-P009 (2026-08-26) |
| Type | Schema extension — L2/L3 (does NOT modify EGER-SCHEMA-001) |
| Dependencies | EGER-SCHEMA-001 (evidence), EGER-ORACLE-CONTRACT-001 |
| Status | FROZEN v1 family |

---

## 1. Schema Families

- `eger.epistemic.v1` — EpistemicClaim
- `eger.transition.v1` — EpistemicTransition + ViolationRecord
- `eger.authorization.request.v1` — AuthorizationRequest
- `eger.authorization.decision.v1` — AuthorizationDecision

EGER-SCHEMA-001 (`eger.candidate/ raw/ evidence`) remains unchanged.

## 2. EpistemicClaim (`eger.epistemic.v1`)

| Field | Type | Required | Notes |
|---|---|---|---|
| `claim_id` | string | REQUIRED | e.g. `EGER-CLAIM-A1B2C3D4E5F6` or supplied `CLAIM-...` |
| `proposition` | string | REQUIRED | Engineering proposition text (e.g. "SDC candidate X is valid") |
| `state` | enum | REQUIRED | `HYPOTHESIS` \| `VALIDATED` \| `REFUTED` \| `UNKNOWN` |
| `supporting_evidence_ids` | string[] | REQUIRED | may be [] for HYPOTHESIS/UNKNOWN |
| `contradicting_evidence_ids` | string[] | REQUIRED | may be [] |
| `baseline_evidence_hash` | string \| null | REQUIRED | hash of evidence that established VALIDATED; null otherwise |
| `baseline_evidence_ids` | string[] | REQUIRED | snapshot of validating evidence_ids |
| `transition_history` | string[] | REQUIRED | ordered transition_ids |
| `provenance` | object | REQUIRED | `created_by`, `created_at` |
| `schema_version` | string | REQUIRED | `eger.epistemic.v1` |
| `created_at` | ISO8601 | REQUIRED | |
| `updated_at` | ISO8601 | REQUIRED | |

Invariant: non-HYPOTHESIS states with supporting/contradicting ids must have traceable evidence (engine enforces).

## 3. EpistemicTransition (`eger.transition.v1`)

| Field | Type | Required | Notes |
|---|---|---|---|
| `transition_id` | string | REQUIRED | `EGER-TRANS-<suffix>-<counter>` deterministic |
| `claim_id` | string | REQUIRED | |
| `previous_state` | enum | REQUIRED | |
| `new_state` | enum | REQUIRED | |
| `evidence_ids` | string[] | REQUIRED | may be [] for UNKNOWN |
| `reason` | string | REQUIRED | deterministic reason string |
| `authorized` | bool | REQUIRED | whether transition-level check passed (pre-L3) |
| `provenance` | object | REQUIRED | `created_at`, `engine`, `schema_version` |
| `schema_version` | string | REQUIRED | `eger.transition.v1` |
| `created_at` | ISO8601 | REQUIRED | provenance timestamp, not semantic identity |

## 4. ViolationRecord (`eger.transition.v1` — same family)

| Field | Type | Required | Notes |
|---|---|---|---|
| `violation_id` | string | REQUIRED | `EGER-VIOL-...` |
| `claim_id` | string | REQUIRED | |
| `attempted_transition` | string | REQUIRED | e.g. `HYPOTHESIS->VALIDATED` |
| `evidence_ids` | string[] | REQUIRED | |
| `violation_type` | enum | REQUIRED | `MISSING_EVIDENCE` \| `INSUFFICIENT_SCOPE` \| `UNSUPPORTED_SCOPE` \| `ORACLE_FAILURE` \| `REFUTED_TO_VALIDATED_WITHOUT_NEW_EVIDENCE` \| `BASELINE_REPLACEMENT` \| `NO_EVIDENCE_TO_VALIDATED` |
| `reason` | string | REQUIRED | |
| `detected_at` | ISO8601 | REQUIRED | |
| `schema_version` | string | REQUIRED | `eger.transition.v1` |

## 5. AuthorizationRequest (`eger.authorization.request.v1`)

| Field | Type | Required | Notes |
|---|---|---|---|
| `request_id` | string | REQUIRED | `REQ-...` |
| `claim_id` | string | REQUIRED | |
| `proposed_action` | string | REQUIRED | `commit` \| `promote_to_validated` etc |
| `epistemic_state` | enum | REQUIRED | snapshot at request time |
| `evidence_ids` | string[] | REQUIRED | |
| `evidence_scope` | enum \| null | REQUIRED | `FULL`/etc snapshot |
| `oracle_status` | string \| null | REQUIRED | snapshot |
| `baseline_evidence_hash` | string \| null | OPTIONAL | for regression check |
| `schema_version` | string | REQUIRED | `eger.authorization.request.v1` |
| `created_at` | ISO8601 | REQUIRED | |

## 6. AuthorizationDecision (`eger.authorization.decision.v1`)

| Field | Type | Required | Notes |
|---|---|---|---|
| `decision_id` | string | REQUIRED | `EGER-AUTH-...` |
| `request_id` | string | REQUIRED | |
| `claim_id` | string | REQUIRED | |
| `decision` | enum | REQUIRED | `APPROVED` \| `REJECTED` |
| `reason` | string | REQUIRED | deterministic policy reason |
| `policy_result` | object | REQUIRED | `required_state`, `actual_state`, `evidence_scope` etc |
| `provenance` | object | REQUIRED | `created_at`, `gate` |
| `schema_version` | string | REQUIRED | `eger.authorization.decision.v1` |
| `created_at` | ISO8601 | REQUIRED | |

## 7. Invariants

- `VALIDATED` never without `evidence_scope=FULL`, `oracle_status=SUCCESS`, no error findings.
- `INSUFFICIENT`/`UNSUPPORTED`/`ORACLE_FAILURE` never support `VALIDATED`.
- `REFUTED->VALIDATED` requires new evidence (hash and ids disjoint from contradicting set).
- `VALIDATED` baseline immutable — replacement with insufficient evidence rejected (`BASELINE_REPLACEMENT`).
- Authorization `APPROVED` only when epistemic `VALIDATED` + `FULL` + `SUCCESS` + evidence linkage (hard gate).

## 8. What Is Deferred

- `AMBIGUOUS` and `INSUFFICIENT_EVIDENCE` as explicit epistemic states — evaluated but not implemented in P009 minimal; represented as `UNKNOWN` with associated evidence.
- Broad CI/merge integration — deferred; L3 is typed decision now.
- `CandidateArtifact ≠ EngineeringState` distinction — conceptually preserved, schema for EngineeringState is `EpistemicClaim` specialized for engineering proposition.

## 9. Versioning

- Initial versions frozen at P009. Additive optional fields = minor bump (PROVISIONAL). Breaking change = major bump + `EGER-CHANGE-###` if scientific meaning shifts. Old artifacts remain immutable.
