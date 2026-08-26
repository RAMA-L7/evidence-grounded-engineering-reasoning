"""Epistemic state model — P009 L2.

States are categorical, per EGER v0.2 + EGER-SCHEMA-001 P6/P7.
No numeric confidence. No LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import hashlib
import json

SCHEMA_EPISTEMIC = "eger.epistemic.v1"
SCHEMA_TRANSITION = "eger.transition.v1"

# Epistemic state vocabulary — frozen per P009 §5
# HYPOTHESIS, VALIDATED, REFUTED, UNKNOWN are mandatory.
# AMBIGUOUS and INSUFFICIENT_EVIDENCE evaluated but DEFERRED for P009 minimal.
VALID_STATES = {"HYPOTHESIS", "VALIDATED", "REFUTED", "UNKNOWN"}

# Violation categories — machine-detectable
VIOLATION_MISSING_EVIDENCE = "MISSING_EVIDENCE"
VIOLATION_INSUFFICIENT_SCOPE = "INSUFFICIENT_SCOPE"
VIOLATION_UNSUPPORTED_SCOPE = "UNSUPPORTED_SCOPE"
VIOLATION_ORACLE_FAILURE = "ORACLE_FAILURE"
VIOLATION_REFUTED_TO_VALIDATED_WITHOUT_NEW_EVIDENCE = "REFUTED_TO_VALIDATED_WITHOUT_NEW_EVIDENCE"
VIOLATION_BASELINE_REPLACEMENT = "BASELINE_REPLACEMENT"
VIOLATION_NO_EVIDENCE_TO_VALIDATED = "NO_EVIDENCE_TO_VALIDATED"

@dataclass
class EpistemicClaim:
    """Typed epistemic claim — engineering proposition under reasoning."""
    claim_id: str
    proposition: str
    state: str  # HYPOTHESIS | VALIDATED | REFUTED | UNKNOWN
    supporting_evidence_ids: List[str] = field(default_factory=list)
    contradicting_evidence_ids: List[str] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    transition_history: List[str] = field(default_factory=list)
    baseline_evidence_hash: Optional[str] = None  # hash of evidence that validated it
    baseline_evidence_ids: List[str] = field(default_factory=list)
    schema_version: str = SCHEMA_EPISTEMIC
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class EpistemicTransition:
    """Deterministic transition record — every state change produces one."""
    transition_id: str
    claim_id: str
    previous_state: str
    new_state: str
    evidence_ids: List[str]
    reason: str
    authorized: bool  # whether transition itself was allowed (pre-authorization)
    provenance: Dict[str, Any]
    schema_version: str = SCHEMA_TRANSITION
    created_at: str = ""

@dataclass
class ViolationRecord:
    """Machine-readable epistemic violation."""
    violation_id: str
    claim_id: str
    attempted_transition: str  # e.g. "HYPOTHESIS->VALIDATED"
    evidence_ids: List[str]
    violation_type: str
    reason: str
    detected_at: str
    schema_version: str = SCHEMA_TRANSITION

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _hash_claim_id(proposition: str) -> str:
    return "EGER-CLAIM-" + hashlib.sha256(proposition.encode("utf-8")).hexdigest()[:12].upper()

def create_hypothesis(proposition: str, claim_id: Optional[str] = None) -> EpistemicClaim:
    cid = claim_id or _hash_claim_id(proposition)
    now = _now()
    return EpistemicClaim(
        claim_id=cid,
        proposition=proposition,
        state="HYPOTHESIS",
        supporting_evidence_ids=[],
        contradicting_evidence_ids=[],
        provenance={"created_by": "epistemic_engine", "created_at": now},
        transition_history=[],
        schema_version=SCHEMA_EPISTEMIC,
        created_at=now,
        updated_at=now,
    )
