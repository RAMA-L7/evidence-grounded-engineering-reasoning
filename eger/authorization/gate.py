"""Deterministic authorization gate — P009 L3.

No LLM. No prompts. Hard programmatic boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

SCHEMA_AUTH_REQUEST = "eger.authorization.request.v1"
SCHEMA_AUTH_DECISION = "eger.authorization.decision.v1"

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class AuthorizationRequest:
    request_id: str
    claim_id: str
    proposed_action: str  # e.g. "commit" or "promote_to_validated"
    epistemic_state: str  # snapshot of claim state at request time
    evidence_ids: List[str]
    evidence_scope: Optional[str] = None  # FULL etc for policy check
    oracle_status: Optional[str] = None
    baseline_evidence_hash: Optional[str] = None
    schema_version: str = SCHEMA_AUTH_REQUEST
    created_at: str = ""

@dataclass
class AuthorizationDecision:
    decision_id: str
    request_id: str
    claim_id: str
    decision: str  # APPROVED | REJECTED
    reason: str
    policy_result: Dict[str, Any]
    provenance: Dict[str, Any]
    schema_version: str = SCHEMA_AUTH_DECISION
    created_at: str = ""

@dataclass
class AuthViolation:
    violation_id: str
    request_id: str
    claim_id: str
    violation_type: str
    reason: str
    detected_at: str

class AuthorizationGate:
    """Deterministic gate — only approves when epistemic + evidence policy satisfied."""

    def __init__(self):
        self.decisions: List[AuthorizationDecision] = []
        self.violations: List[AuthViolation] = []
        self._dec_counter = 0
        self._viol_counter = 0
        self._attempted = 0

    def authorize(self, req: AuthorizationRequest) -> AuthorizationDecision:
        self._attempted += 1
        # Policy: for commit/promote actions, require VALIDATED + FULL + SUCCESS
        # For other actions (e.g. read), no auth needed — but for P009 all requests are treated as engineering-state-affecting
        now = _now()
        self._dec_counter += 1
        did = f"EGER-AUTH-{req.claim_id[-6:]}-{self._dec_counter:04d}"

        # Determine if epistemic state satisfies policy
        is_validated_action = req.proposed_action in ("commit", "promote_to_validated", "validate_commit", "promote")
        # For P009, treat any promotion/commit as requiring VALIDATED epistemic state

        if is_validated_action:
            if req.epistemic_state != "VALIDATED":
                reason = f"epistemic state {req.epistemic_state} is not VALIDATED — cannot authorize {req.proposed_action}"
                decision = AuthorizationDecision(
                    decision_id=did,
                    request_id=req.request_id,
                    claim_id=req.claim_id,
                    decision="REJECTED",
                    reason=reason,
                    policy_result={"required_state": "VALIDATED", "actual_state": req.epistemic_state, "evidence_scope": req.evidence_scope, "oracle_status": req.oracle_status},
                    provenance={"created_at": now, "gate": "authorization", "schema_version": SCHEMA_AUTH_DECISION},
                    created_at=now,
                )
                self.decisions.append(decision)
                return decision

            # Also require evidence_scope FULL and oracle_status SUCCESS
            if req.evidence_scope != "FULL":
                reason = f"evidence_scope {req.evidence_scope} is not FULL — insufficient for {req.proposed_action}"
                decision = AuthorizationDecision(
                    decision_id=did,
                    request_id=req.request_id,
                    claim_id=req.claim_id,
                    decision="REJECTED",
                    reason=reason,
                    policy_result={"required_scope": "FULL", "actual_scope": req.evidence_scope, "oracle_status": req.oracle_status},
                    provenance={"created_at": now, "gate": "authorization", "schema_version": SCHEMA_AUTH_DECISION},
                    created_at=now,
                )
                self.decisions.append(decision)
                # Authorization cannot override epistemic limitation — this REJECTED is correct
                # If someone had approved despite this, that would be an auth violation
                return decision

            if req.oracle_status != "SUCCESS":
                reason = f"oracle_status {req.oracle_status} is not SUCCESS — cannot authorize"
                decision = AuthorizationDecision(
                    decision_id=did,
                    request_id=req.request_id,
                    claim_id=req.claim_id,
                    decision="REJECTED",
                    reason=reason,
                    policy_result={"required_oracle_status": "SUCCESS", "actual": req.oracle_status},
                    provenance={"created_at": now, "gate": "authorization", "schema_version": SCHEMA_AUTH_DECISION},
                    created_at=now,
                )
                self.decisions.append(decision)
                return decision

            # Evidence linkage required
            if not req.evidence_ids:
                reason = "no evidence_ids linked — cannot authorize"
                decision = AuthorizationDecision(
                    decision_id=did,
                    request_id=req.request_id,
                    claim_id=req.claim_id,
                    decision="REJECTED",
                    reason=reason,
                    policy_result={"evidence_ids": req.evidence_ids},
                    provenance={"created_at": now, "gate": "authorization", "schema_version": SCHEMA_AUTH_DECISION},
                    created_at=now,
                )
                self.decisions.append(decision)
                return decision

            # All checks pass
            decision = AuthorizationDecision(
                decision_id=did,
                request_id=req.request_id,
                claim_id=req.claim_id,
                decision="APPROVED",
                reason="epistemic state VALIDATED with FULL scope and SUCCESS, evidence linked",
                policy_result={"required_state": "VALIDATED", "actual_state": req.epistemic_state, "evidence_scope": req.evidence_scope, "oracle_status": req.oracle_status, "evidence_ids": req.evidence_ids},
                provenance={"created_at": now, "gate": "authorization", "schema_version": SCHEMA_AUTH_DECISION},
                created_at=now,
            )
            self.decisions.append(decision)
            return decision
        else:
            # Unknown action type — for P009, reject unless explicitly known
            decision = AuthorizationDecision(
                decision_id=did,
                request_id=req.request_id,
                claim_id=req.claim_id,
                decision="REJECTED",
                reason=f"unknown proposed_action {req.proposed_action}",
                policy_result={"proposed_action": req.proposed_action},
                provenance={"created_at": now, "gate": "authorization", "schema_version": SCHEMA_AUTH_DECISION},
                created_at=now,
            )
            self.decisions.append(decision)
            return decision

    def authorize_or_record_violation(self, req: AuthorizationRequest, force_approve: bool = False) -> AuthorizationDecision:
        """Helper that detects authorization violations: if force_approve is True despite policy, record violation."""
        decision = self.authorize(req)
        if force_approve and decision.decision == "REJECTED":
            # Someone tried to force approval despite epistemic limitation — record violation
            self._viol_counter += 1
            vid = f"EGER-AUTH-VIOL-{req.claim_id[-6:]}-{self._viol_counter:04d}"
            self.violations.append(AuthViolation(
                violation_id=vid,
                request_id=req.request_id,
                claim_id=req.claim_id,
                violation_type="AUTHORIZATION_OVERRIDE",
                reason=f"attempted to approve {req.proposed_action} despite {decision.reason}",
                detected_at=_now(),
            ))
        return decision

    def violation_stats(self) -> Dict[str, Any]:
        attempted = self._attempted
        violations = len(self.violations)
        return {
            "attempted_authorizations": attempted,
            "authorization_violations": violations,
            "auth_violation_rate": (violations / attempted) if attempted else 0.0,
            "violations_by_type": {vt: sum(1 for v in self.violations if v.violation_type == vt) for vt in set(v.violation_type for v in self.violations)},
            "decisions": {"APPROVED": sum(1 for d in self.decisions if d.decision == "APPROVED"), "REJECTED": sum(1 for d in self.decisions if d.decision == "REJECTED")},
        }
