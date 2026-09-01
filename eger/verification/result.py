"""VerificationResult — typed, deterministic verification decision.

ENGINEERING DESIGN CHOICE: verification gate (P1 principle).

This contract records the final accept/reject decision from the
deterministic verification gate. It is NOT modifiable by the LLM.

INVARIANT: decision must be one of: ACCEPT, REJECT
INVARIANT: error_count must be >= 0
INVARIANT: all fields are immutable (frozen=True)

PRODUCER: VerificationGate (deterministic)
CONSUMER: RunRecord, external system
AUTHORITY: AUTHORIZATION — final decision
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

SCHEMA_VERIFICATION = "eger.verification.v1"

VALID_DECISIONS = {"ACCEPT", "REJECT"}


@dataclass(frozen=True)
class VerificationResult:
    """Deterministic verification decision — immutable once created.

    INVARIANT: decision must be ACCEPT or REJECT.
    INVARIANT: The LLM cannot produce this — only the gate can.
    """
    decision: str
    reason: str
    error_count: int
    unresolved_findings: List[str]
    provenance: Dict[str, Any]
    schema_version: str = SCHEMA_VERIFICATION

    def __post_init__(self):
        if self.decision not in VALID_DECISIONS:
            raise ValueError(f"decision must be one of {VALID_DECISIONS}, got '{self.decision}'")
        if self.error_count < 0:
            raise ValueError("error_count must be >= 0")

    @property
    def is_accepted(self) -> bool:
        return self.decision == "ACCEPT"

    @property
    def is_rejected(self) -> bool:
        return self.decision == "REJECT"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "decision": self.decision,
            "reason": self.reason,
            "error_count": self.error_count,
            "unresolved_findings": list(self.unresolved_findings),
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> VerificationResult:
        return cls(
            decision=d["decision"],
            reason=d["reason"],
            error_count=d["error_count"],
            unresolved_findings=list(d.get("unresolved_findings", [])),
            provenance=dict(d.get("provenance", {})),
            schema_version=d.get("schema_version", SCHEMA_VERIFICATION),
        )
