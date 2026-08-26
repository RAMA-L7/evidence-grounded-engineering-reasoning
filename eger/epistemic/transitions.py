"""Deterministic transition engine — P009 L2.

No LLM. No probabilistic scoring. No embeddings.
Pure deterministic function: (current_state + evidence + explicit request) -> decision.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from .state import (
    EpistemicClaim,
    EpistemicTransition,
    ViolationRecord,
    SCHEMA_EPISTEMIC,
    SCHEMA_TRANSITION,
    VALID_STATES,
    VIOLATION_MISSING_EVIDENCE,
    VIOLATION_INSUFFICIENT_SCOPE,
    VIOLATION_UNSUPPORTED_SCOPE,
    VIOLATION_ORACLE_FAILURE,
    VIOLATION_REFUTED_TO_VALIDATED_WITHOUT_NEW_EVIDENCE,
    VIOLATION_BASELINE_REPLACEMENT,
    VIOLATION_NO_EVIDENCE_TO_VALIDATED,
)

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _tid(claim_id: str, counter: int) -> str:
    return f"EGER-TRANS-{claim_id[-6:]}-{counter:04d}"

def _vid(claim_id: str, counter: int) -> str:
    return f"EGER-VIOL-{claim_id[-6:]}-{counter:04d}"

@dataclass
class TransitionRequest:
    claim_id: str
    target_state: str
    evidence: Optional[Any] = None  # EvidenceArtifact or OracleFailure wrapper
    evidence_ids: List[str] = field(default_factory=list)
    reason: str = ""

@dataclass
class TransitionResult:
    accepted: bool
    transition: Optional[EpistemicTransition] = None
    violation: Optional[ViolationRecord] = None
    reason: str = ""

# ---------------------------------------------------------------------------
# Evidence inspection helpers — operate on EvidenceArtifact / OracleFailure
# ---------------------------------------------------------------------------

def _evidence_scope(ev) -> Optional[str]:
    if ev is None:
        return None
    # EvidenceArtifact has evidence_scope
    return getattr(ev, "evidence_scope", None)

def _oracle_status(ev) -> Optional[str]:
    if ev is None:
        return None
    return getattr(ev, "oracle_status", None)

def _evidence_hash(ev) -> Optional[str]:
    if ev is None:
        return None
    return getattr(ev, "evidence_hash", None)

def _has_error_findings(ev) -> bool:
    if ev is None:
        return False
    findings = getattr(ev, "findings", []) or []
    for f in findings:
        sev = f.get("severity", "") if isinstance(f, dict) else getattr(f, "severity", "")
        if sev == "error":
            return True
    return False

def _is_failure(ev) -> bool:
    # OracleFailure has kind
    if ev is None:
        return False
    return hasattr(ev, "kind")

def _failure_kind(ev) -> Optional[str]:
    if ev is None:
        return None
    return getattr(ev, "kind", None)

# ---------------------------------------------------------------------------
# Evidence requirement predicates (deterministic, per P009 §7)
# ---------------------------------------------------------------------------

def _can_support_validated(ev) -> tuple[bool, str]:
    """Check if evidence can support VALIDATED. Returns (ok, reason)."""
    if ev is None:
        return False, "no evidence provided"
    if _is_failure(ev):
        return False, f"oracle failure {getattr(ev, 'kind', '')} cannot support VALIDATED"
    scope = _evidence_scope(ev)
    status = _oracle_status(ev)
    if status != "SUCCESS":
        return False, f"oracle_status {status} is not SUCCESS"
    if scope != "FULL":
        return False, f"evidence_scope {scope} is not FULL — insufficient/unsupported cannot validate"
    if _has_error_findings(ev):
        return False, "evidence contains error findings — contradictory, cannot validate"
    return True, "FULL scope, SUCCESS, no error findings"

def _can_support_refuted(ev) -> tuple[bool, str]:
    if ev is None:
        return False, "no evidence provided"
    if _is_failure(ev):
        return False, f"oracle failure {getattr(ev, 'kind', '')} cannot support REFUTED"
    scope = _evidence_scope(ev)
    status = _oracle_status(ev)
    if status != "SUCCESS":
        return False, f"oracle_status {status} is not SUCCESS"
    if scope not in ("FULL", "PARTIAL"):
        return False, f"evidence_scope {scope} insufficient to establish REFUTED"
    if not _has_error_findings(ev):
        return False, "no error findings — cannot establish REFUTED"
    return True, "error findings present with sufficient scope"

def _is_insufficient_or_unsupported(ev) -> bool:
    if ev is None:
        return True
    if _is_failure(ev):
        return True
    scope = _evidence_scope(ev)
    return scope in ("INSUFFICIENT", "UNSUPPORTED")

# ---------------------------------------------------------------------------
# Epistemic Engine
# ---------------------------------------------------------------------------

class EpistemicEngine:
    """Deterministic L2 engine — owns claim store, transition history, violation counts."""

    def __init__(self):
        self.claims: Dict[str, EpistemicClaim] = {}
        self.transitions: List[EpistemicTransition] = []
        self.violations: List[ViolationRecord] = []
        self._trans_counter = 0
        self._viol_counter = 0
        self._attempted_transitions = 0  # for EVR denominator
        # Baseline store: claim_id -> baseline evidence hash
        self.baselines: Dict[str, str] = {}

    # -- claim management -----------------------------------------------

    def create_claim(self, claim: EpistemicClaim) -> EpistemicClaim:
        if claim.claim_id in self.claims:
            raise ValueError(f"claim {claim.claim_id} already exists")
        if claim.state not in VALID_STATES:
            raise ValueError(f"invalid state {claim.state}")
        self.claims[claim.claim_id] = claim
        return claim

    def get_claim(self, claim_id: str) -> Optional[EpistemicClaim]:
        return self.claims.get(claim_id)

    # -- transition ----------------------------------------------------

    def request_transition(self, req: TransitionRequest) -> TransitionResult:
        self._attempted_transitions += 1
        claim = self.claims.get(req.claim_id)
        if claim is None:
            v = self._violation(req.claim_id, f"{req.target_state}", req.evidence_ids, VIOLATION_MISSING_EVIDENCE, "claim not found")
            return TransitionResult(accepted=False, violation=v, reason="claim not found")
        if req.target_state not in VALID_STATES:
            v = self._violation(req.claim_id, f"{claim.state}->{req.target_state}", req.evidence_ids, VIOLATION_MISSING_EVIDENCE, f"invalid target state {req.target_state}")
            return TransitionResult(accepted=False, violation=v, reason=f"invalid target state {req.target_state}")

        prev = claim.state
        target = req.target_state
        ev = req.evidence
        ev_ids = req.evidence_ids or []

        # No-op same state -> allow only if evidence re-confirms? For P009 allow idempotent.
        if prev == target:
            # Still require evidence linkage check for VALIDATED
            if target == "VALIDATED":
                # Must still have valid supporting evidence; otherwise violation
                ok, reason = _can_support_validated(ev)
                if not ok:
                    v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_BASELINE_REPLACEMENT, f"VALIDATED re-affirmation without supporting evidence: {reason}")
                    return TransitionResult(accepted=False, violation=v, reason=reason)
            tr = self._record_transition(claim, prev, target, ev_ids, req.reason)
            return TransitionResult(accepted=True, transition=tr, reason="idempotent re-affirmation")

        # ---- Rule: HYPOTHESIS -> VALIDATED ---------------------------------
        if prev == "HYPOTHESIS" and target == "VALIDATED":
            if not ev_ids or ev is None:
                v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_NO_EVIDENCE_TO_VALIDATED, "HYPOTHESIS->VALIDATED without evidence")
                return TransitionResult(accepted=False, violation=v, reason="missing evidence")
            ok, reason = _can_support_validated(ev)
            if not ok:
                vtype = VIOLATION_INSUFFICIENT_SCOPE if "scope" in reason.lower() or "insufficient" in reason.lower() else VIOLATION_NO_EVIDENCE_TO_VALIDATED
                if _is_failure(ev):
                    vtype = VIOLATION_ORACLE_FAILURE
                elif _evidence_scope(ev) == "UNSUPPORTED":
                    vtype = VIOLATION_UNSUPPORTED_SCOPE
                v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, vtype, reason)
                return TransitionResult(accepted=False, violation=v, reason=reason)
            tr = self._record_transition(claim, prev, target, ev_ids, req.reason)
            # Set baseline
            eh = _evidence_hash(ev)
            if eh:
                self.baselines[claim.claim_id] = eh
                claim.baseline_evidence_hash = eh
                claim.baseline_evidence_ids = list(ev_ids)
            claim.supporting_evidence_ids = list(ev_ids)
            return TransitionResult(accepted=True, transition=tr, reason="validated")

        # ---- Rule: HYPOTHESIS -> REFUTED -----------------------------------
        if prev == "HYPOTHESIS" and target == "REFUTED":
            if not ev_ids or ev is None:
                v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_MISSING_EVIDENCE, "HYPOTHESIS->REFUTED without evidence")
                return TransitionResult(accepted=False, violation=v, reason="missing evidence")
            ok, reason = _can_support_refuted(ev)
            if not ok:
                v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_INSUFFICIENT_SCOPE, reason)
                return TransitionResult(accepted=False, violation=v, reason=reason)
            tr = self._record_transition(claim, prev, target, ev_ids, req.reason)
            claim.contradicting_evidence_ids = list(ev_ids)
            return TransitionResult(accepted=True, transition=tr, reason="refuted")

        # ---- Rule: HYPOTHESIS -> UNKNOWN (insufficient/unsupported/failure) --
        if prev == "HYPOTHESIS" and target == "UNKNOWN":
            # UNKNOWN with insufficient/unsupported/failure is allowed; also empty evidence allowed
            tr = self._record_transition(claim, prev, target, ev_ids, req.reason or "insufficient evidence")
            return TransitionResult(accepted=True, transition=tr, reason="unknown")

        # ---- Rule: UNKNOWN -> VALIDATED -------------------------------------
        if prev == "UNKNOWN" and target == "VALIDATED":
            if not ev_ids or ev is None:
                v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_NO_EVIDENCE_TO_VALIDATED, "UNKNOWN->VALIDATED without evidence")
                return TransitionResult(accepted=False, violation=v, reason="missing evidence")
            ok, reason = _can_support_validated(ev)
            if not ok:
                vtype = VIOLATION_INSUFFICIENT_SCOPE if "scope" in reason.lower() else VIOLATION_NO_EVIDENCE_TO_VALIDATED
                if _is_failure(ev):
                    vtype = VIOLATION_ORACLE_FAILURE
                v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, vtype, reason)
                return TransitionResult(accepted=False, violation=v, reason=reason)
            tr = self._record_transition(claim, prev, target, ev_ids, req.reason)
            eh = _evidence_hash(ev)
            if eh:
                self.baselines[claim.claim_id] = eh
                claim.baseline_evidence_hash = eh
                claim.baseline_evidence_ids = list(ev_ids)
            claim.supporting_evidence_ids = list(ev_ids)
            return TransitionResult(accepted=True, transition=tr, reason="validated from unknown")

        # ---- Rule: REFUTED -> VALIDATED requires new evidence ---------------
        if prev == "REFUTED" and target == "VALIDATED":
            if not ev_ids or ev is None:
                v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_REFUTED_TO_VALIDATED_WITHOUT_NEW_EVIDENCE, "REFUTED->VALIDATED without evidence")
                return TransitionResult(accepted=False, violation=v, reason="missing evidence")
            # Check if evidence is same as contradicting evidence (no new evidence)
            eh = _evidence_hash(ev)
            if eh and eh in claim.contradicting_evidence_ids:
                v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_REFUTED_TO_VALIDATED_WITHOUT_NEW_EVIDENCE, "evidence same as refuting evidence — no new evidence")
                return TransitionResult(accepted=False, violation=v, reason="no new evidence")
            # Also check baseline: if hash matches old contradicting hash, reject
            if ev_ids and set(ev_ids) & set(claim.contradicting_evidence_ids):
                # Allow if additional new evidence_ids present? For P009 strict: require evidence_ids disjoint from contradicting set
                # If overlap and no additional distinct evidence, treat as violation
                if set(ev_ids).issubset(set(claim.contradicting_evidence_ids)):
                    v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_REFUTED_TO_VALIDATED_WITHOUT_NEW_EVIDENCE, "no new evidence beyond refuting evidence")
                    return TransitionResult(accepted=False, violation=v, reason="no new evidence")
            ok, reason = _can_support_validated(ev)
            if not ok:
                v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_INSUFFICIENT_SCOPE, reason)
                return TransitionResult(accepted=False, violation=v, reason=reason)
            tr = self._record_transition(claim, prev, target, ev_ids, req.reason)
            eh = _evidence_hash(ev)
            if eh:
                self.baselines[claim.claim_id] = eh
                claim.baseline_evidence_hash = eh
                claim.baseline_evidence_ids = list(ev_ids)
            claim.supporting_evidence_ids = list(ev_ids)
            return TransitionResult(accepted=True, transition=tr, reason="validated after refuted with new evidence")

        # ---- Rule: VALIDATED -> VALIDATED baseline immutability -------------
        if prev == "VALIDATED" and target == "VALIDATED":
            # This is the idempotent case already handled above for same-state, but
            # if evidence_ids differ from baseline, that is baseline replacement without revalidation path
            if ev_ids and claim.baseline_evidence_ids and set(ev_ids) != set(claim.baseline_evidence_ids):
                # For P009: any change to supporting evidence while staying VALIDATED without explicit revalidation is a violation
                # Allow only if new evidence also satisfies VALIDATED and is considered a revalidation
                ok, reason = _can_support_validated(ev)
                if not ok:
                    v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_BASELINE_REPLACEMENT, f"baseline replacement without sufficient evidence: {reason}")
                    return TransitionResult(accepted=False, violation=v, reason=reason)
                # Even if new evidence is valid, for P009 we treat this as revalidation — update baseline
                eh = _evidence_hash(ev)
                if eh:
                    self.baselines[claim.claim_id] = eh
                    claim.baseline_evidence_hash = eh
                    claim.baseline_evidence_ids = list(ev_ids)
                claim.supporting_evidence_ids = list(ev_ids)
                tr = self._record_transition(claim, prev, target, ev_ids, req.reason or "revalidated")
                return TransitionResult(accepted=True, transition=tr, reason="revalidated baseline")
            # else handled by idempotent path above

        # ---- Generic: insufficient/unsupported/oracle failure cannot validate ---
        if target == "VALIDATED":
            # Catch-all for any other prev state -> VALIDATED without sufficient evidence
            if not ev_ids or ev is None:
                v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_NO_EVIDENCE_TO_VALIDATED, f"{prev}->VALIDATED without evidence")
                return TransitionResult(accepted=False, violation=v, reason="missing evidence")
            if _is_failure(ev):
                v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_ORACLE_FAILURE, "oracle failure cannot support VALIDATED")
                return TransitionResult(accepted=False, violation=v, reason="oracle failure")
            scope = _evidence_scope(ev)
            if scope in ("INSUFFICIENT", "UNSUPPORTED"):
                vtype = VIOLATION_INSUFFICIENT_SCOPE if scope == "INSUFFICIENT" else VIOLATION_UNSUPPORTED_SCOPE
                v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, vtype, f"scope {scope} cannot support VALIDATED")
                return TransitionResult(accepted=False, violation=v, reason=f"scope {scope}")

        # ---- Default: allow UNKNOWN, disallow other unspecified ----------------
        # For any other transition not explicitly allowed, require evidence linkage
        if target == "UNKNOWN":
            tr = self._record_transition(claim, prev, target, ev_ids, req.reason or "transition to unknown")
            return TransitionResult(accepted=True, transition=tr, reason="unknown")
        if target == "REFUTED":
            if not ev_ids or ev is None:
                v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_MISSING_EVIDENCE, f"{prev}->REFUTED without evidence")
                return TransitionResult(accepted=False, violation=v, reason="missing evidence")
            ok, reason = _can_support_refuted(ev)
            if not ok:
                v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_INSUFFICIENT_SCOPE, reason)
                return TransitionResult(accepted=False, violation=v, reason=reason)
            tr = self._record_transition(claim, prev, target, ev_ids, req.reason)
            claim.contradicting_evidence_ids = list(ev_ids)
            return TransitionResult(accepted=True, transition=tr, reason="refuted")

        # Fallback reject
        v = self._violation(req.claim_id, f"{prev}->{target}", ev_ids, VIOLATION_MISSING_EVIDENCE, f"transition {prev}->{target} not allowed")
        return TransitionResult(accepted=False, violation=v, reason=f"transition {prev}->{target} not allowed")

    # -- internal helpers ---------------------------------------------

    def _record_transition(self, claim: EpistemicClaim, prev: str, new_state: str, ev_ids: List[str], reason: str) -> EpistemicTransition:
        self._trans_counter += 1
        tid = _tid(claim.claim_id, self._trans_counter)
        now = _now()
        tr = EpistemicTransition(
            transition_id=tid,
            claim_id=claim.claim_id,
            previous_state=prev,
            new_state=new_state,
            evidence_ids=list(ev_ids),
            reason=reason,
            authorized=True,
            provenance={"created_at": now, "engine": "epistemic", "schema_version": SCHEMA_TRANSITION},
            created_at=now,
        )
        self.transitions.append(tr)
        claim.state = new_state
        claim.updated_at = now
        claim.transition_history.append(tid)
        return tr

    def _violation(self, claim_id: str, attempted: str, ev_ids: List[str], vtype: str, reason: str) -> ViolationRecord:
        self._viol_counter += 1
        vid = _vid(claim_id, self._viol_counter)
        v = ViolationRecord(
            violation_id=vid,
            claim_id=claim_id,
            attempted_transition=attempted,
            evidence_ids=list(ev_ids),
            violation_type=vtype,
            reason=reason,
            detected_at=_now(),
        )
        self.violations.append(v)
        return v

    # -- metrics ------------------------------------------------------

    def evr(self) -> Dict[str, Any]:
        """Epistemic Violation Rate raw counts."""
        attempted = self._attempted_transitions
        violations = len(self.violations)
        rate = (violations / attempted) if attempted else 0.0
        return {
            "attempted_transitions": attempted,
            "violations": violations,
            "evr": rate,
            "violations_by_type": {vt: sum(1 for v in self.violations if v.violation_type == vt) for vt in set(v.violation_type for v in self.violations)},
        }

    def get_violations(self) -> List[ViolationRecord]:
        return list(self.violations)

    def get_transitions(self) -> List[EpistemicTransition]:
        return list(self.transitions)
