"""VerificationGate — deterministic acceptance authority.

ENGINEERING DESIGN CHOICE: verification gate (P1 principle).

This module is the SOLE acceptance authority in the EGER architecture.
It makes the final ACCEPT/REJECT decision from deterministic,
Oracle-derived evidence.

INVARIANT: VerificationGate is the only component that can produce ACCEPT/REJECT.
INVARIANT: The LLM cannot produce this decision.
INVARIANT: The RevisionController cannot produce this decision.
INVARIANT: CandidateArtifact cannot self-promote.
INVARIANT: Fail-closed: ambiguous conditions → REJECT.

PRODUCER: VerificationGate (deterministic)
CONSUMER: RunRecord, external system
AUTHORITY: AUTHORIZATION — final decision
"""

from __future__ import annotations

from typing import Optional

from eger.engineer.candidate import CandidateArtifact
from eger.evidence.schemas import EvidenceArtifact
from .result import VerificationResult


class VerificationGate:
    """Deterministic verification gate — sole acceptance authority.

    Acceptance policy:
        ACCEPT: candidate is eligible AND evidence has zero ERROR findings
                AND evidence is valid/usable
        REJECT: any ERROR finding exists
        REJECT: evidence is malformed, missing, inconsistent, or insufficient

    INVARIANT: Same candidate + same evidence → same decision, always.
    INVARIANT: Cannot mutate CandidateArtifact or EvidenceArtifact.
    INVARIANT: Cannot call LLM or model provider.
    """

    def evaluate(
        self,
        candidate: Optional[CandidateArtifact],
        evidence: Optional[EvidenceArtifact],
    ) -> VerificationResult:
        """Evaluate candidate against evidence.

        Args:
            candidate: The candidate SDC to evaluate
            evidence: The Oracle-derived evidence

        Returns:
            VerificationResult with deterministic ACCEPT/REJECT decision
        """
        # --- Fail-closed: missing candidate ---
        if candidate is None:
            return self._reject(
                reason="No candidate provided",
                error_count=0,
                evidence_id=None,
                candidate_id=None,
            )

        # --- Fail-closed: missing evidence ---
        if evidence is None:
            return self._reject(
                reason="No evidence provided — cannot verify candidate",
                error_count=0,
                evidence_id=None,
                candidate_id=candidate.artifact_id,
            )

        # --- Fail-closed: evidence not from valid Oracle ---
        if evidence.oracle_status not in ("SUCCESS",):
            return self._reject(
                reason=f"Evidence Oracle status is {evidence.oracle_status} — not SUCCESS",
                error_count=evidence.summary.error_count,
                evidence_id=evidence.evidence_id,
                candidate_id=candidate.artifact_id,
            )

        # --- Fail-closed: evidence scope insufficient ---
        if evidence.evidence_scope in ("UNSUPPORTED", "INSUFFICIENT"):
            return self._reject(
                reason=f"Evidence scope is {evidence.evidence_scope} — insufficient for acceptance",
                error_count=evidence.summary.error_count,
                evidence_id=evidence.evidence_id,
                candidate_id=candidate.artifact_id,
            )

        # --- Check ERROR findings ---
        if evidence.summary.error_count > 0:
            # Collect unresolved ERROR finding IDs
            error_findings = [
                f.finding_id for f in evidence.findings
                if f.severity == "error"
            ]
            return self._reject(
                reason=f"{evidence.summary.error_count} ERROR finding(s) remain unresolved",
                error_count=evidence.summary.error_count,
                evidence_id=evidence.evidence_id,
                candidate_id=candidate.artifact_id,
                unresolved_findings=error_findings,
            )

        # --- ACCEPT: zero ERROR findings, valid evidence ---
        return self._accept(
            reason="Zero ERROR findings — candidate passes verification",
            error_count=0,
            evidence_id=evidence.evidence_id,
            candidate_id=candidate.artifact_id,
        )

    def _accept(
        self,
        reason: str,
        error_count: int,
        evidence_id: str,
        candidate_id: str,
    ) -> VerificationResult:
        """Create an ACCEPT VerificationResult."""
        provenance = {
            "gate": "VerificationGate",
            "gate_version": "1.0.0",
            "decision": "ACCEPT",
            "evidence_id": evidence_id,
            "candidate_id": candidate_id,
        }
        return VerificationResult(
            decision="ACCEPT",
            reason=reason,
            error_count=error_count,
            unresolved_findings=[],
            provenance=provenance,
        )

    def _reject(
        self,
        reason: str,
        error_count: int,
        evidence_id: Optional[str],
        candidate_id: Optional[str],
        unresolved_findings: Optional[list] = None,
    ) -> VerificationResult:
        """Create a REJECT VerificationResult."""
        provenance = {
            "gate": "VerificationGate",
            "gate_version": "1.0.0",
            "decision": "REJECT",
            "evidence_id": evidence_id or "",
            "candidate_id": candidate_id or "",
        }
        return VerificationResult(
            decision="REJECT",
            reason=reason,
            error_count=error_count,
            unresolved_findings=unresolved_findings or [],
            provenance=provenance,
        )
