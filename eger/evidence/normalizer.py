"""EvidenceNormalizer — deterministic transformation from Oracle to EvidenceArtifact.

EMPIRICALLY SUPPORTED: structured feedback (C1/C2).

This module transforms the Oracle's raw evidence representation into the
normalized EvidenceArtifact contract defined in P138. It is a deterministic
transformation — same input produces same output, always.

INVARIANT: Same Oracle input → same EvidenceArtifact (modulo timestamp).
INVARIANT: Normalizer cannot invent findings.
INVARIANT: Normalizer cannot reinterpret Oracle truth.
INVARIANT: Normalizer cannot decide ACCEPT/REJECT.
INVARIANT: Normalizer cannot modify CandidateArtifact.

PRODUCER: EvidenceNormalizer (deterministic)
CONSUMER: RevisionController, VerificationGate, PromptBuilder
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
import hashlib
import json

from .schemas import (
    Finding,
    EvidenceArtifact,
    FindingSummary,
    VALID_SEVERITY,
    VALID_ORACLE_STATUS,
    VALID_EVIDENCE_SCOPE,
    SCHEMA_EVIDENCE,
)


# ---------------------------------------------------------------------------
# Severity mapping
# ---------------------------------------------------------------------------

# Oracle findings use "sev" field with values: "error", "warning", "info"
# These map directly to our severity vocabulary.
# Unknown/unmapped severity → fail closed (INCOMPLETE_MEASUREMENT)

_SEVERITY_MAP = {
    "error": "error",
    "warning": "warning",
    "info": "info",
    # Oracle uses these in some contexts
    "ERROR": "error",
    "WARNING": "warning",
    "INFO": "info",
}

# Oracle status mapping
_ORACLE_STATUS_MAP = {
    "SUCCESS": "SUCCESS",
    "INVALID_REQUEST": "INVALID_REQUEST",
    "ORACLE_FAILURE": "ORACLE_FAILURE",
}

# Oracle scope mapping (from schemas.py SCOPE_MAP)
_SCOPE_MAP = {
    "VALIDATED": "FULL",
    "PARTIALLY_VALIDATED": "PARTIAL",
    "NETLIST_REQUIRED": "INSUFFICIENT",
    "UNSUPPORTED": "UNSUPPORTED",
    "TCL_EXECUTION_REQUIRED": "UNSUPPORTED",
    "NOT_VALIDATED": "UNSUPPORTED",
}


def _deterministic_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _map_severity(raw_sev: str) -> Optional[str]:
    """Map Oracle severity to canonical severity. Returns None for unknown."""
    return _SEVERITY_MAP.get(raw_sev)


def _map_oracle_status(raw_status: str) -> str:
    """Map Oracle status to canonical status. Defaults to UNKNOWN."""
    return _ORACLE_STATUS_MAP.get(raw_status, "UNKNOWN")


def _map_scope(raw_scope: str) -> str:
    """Map Oracle scope to canonical scope. Defaults to UNSUPPORTED."""
    return _SCOPE_MAP.get(raw_scope, "UNSUPPORTED")


# ---------------------------------------------------------------------------
# EvidenceNormalizer
# ---------------------------------------------------------------------------

class EvidenceNormalizer:
    """Deterministic transformation from Oracle result to EvidenceArtifact.

    Core invariant:
        Oracle result → EvidenceNormalizer → EvidenceArtifact
        must be deterministic.

    Same input → same output, always.
    """

    def normalize(
        self,
        oracle_evidence: Any,
        task_id: str,
        candidate_hash: Optional[str] = None,
        oracle_version: Optional[str] = None,
        oracle_commit: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> EvidenceArtifact:
        """Normalize Oracle evidence into EvidenceArtifact.

        Args:
            oracle_evidence: Oracle's EvidenceArtifact (or compatible object
                           with attributes: oracle_status, evidence_scope,
                           findings, analysis_scope, artifact_id, provenance)
            task_id: Task identifier
            candidate_hash: Hash of the candidate SDC being evaluated
            oracle_version: Oracle version string
            oracle_commit: Oracle commit hash
            timestamp: Explicit timestamp (if None, generates one)

        Returns:
            Normalized EvidenceArtifact

        Raises:
            ValueError: If Oracle evidence is malformed or has unmappable severity
        """
        # Extract Oracle fields
        oracle_status = self._extract_oracle_status(oracle_evidence)
        evidence_scope = self._extract_evidence_scope(oracle_evidence)
        raw_findings = self._extract_findings(oracle_evidence)
        analysis_scope = self._extract_analysis_scope(oracle_evidence)
        oracle_artifact_id = self._extract_artifact_id(oracle_evidence)
        oracle_provenance = self._extract_provenance(oracle_evidence)

        # Normalize findings
        findings, unmapped_severities = self._normalize_findings(
            raw_findings, oracle_artifact_id
        )

        # If any severity is unmappable, fail closed
        if unmapped_severities:
            raise ValueError(
                f"Unmapped Oracle severities found: {unmapped_severities}. "
                f"Cannot normalize — failing closed as INCOMPLETE_MEASUREMENT."
            )

        # Build summary
        summary = FindingSummary.from_findings(findings)

        # Generate evidence ID
        evidence_input = {
            "task_id": task_id,
            "oracle_artifact_id": oracle_artifact_id,
            "findings_count": len(findings),
            "oracle_status": oracle_status,
        }
        evidence_hash = _deterministic_hash(json.dumps(evidence_input, sort_keys=True))
        evidence_id = f"EGER-EVID-{evidence_hash[:12].upper()}"

        # Build provenance
        provenance = {
            "oracle_version": oracle_version or oracle_provenance.get("oracle_version", ""),
            "oracle_commit": oracle_commit or oracle_provenance.get("oracle_revision", ""),
            "oracle_artifact_id": oracle_artifact_id,
            "candidate_hash": candidate_hash or "",
            "task_id": task_id,
            "normalizer": "EvidenceNormalizer",
            "normalizer_version": "1.0.0",
        }

        # Build raw_ref
        raw_ref = {
            "oracle_artifact_id": oracle_artifact_id,
            "evidence_hash": evidence_hash,
        }

        # Create EvidenceArtifact
        ts = timestamp or _now_iso()

        return EvidenceArtifact(
            evidence_id=evidence_id,
            task_id=task_id,
            oracle_status=oracle_status,
            evidence_scope=evidence_scope,
            findings=tuple(findings),
            summary=summary,
            analysis_scope=analysis_scope or {},
            raw_ref=raw_ref,
            schema_version=SCHEMA_EVIDENCE,
            created_at=ts,
        )

    def normalize_failure(
        self,
        oracle_failure: Any,
        task_id: str,
        candidate_hash: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> EvidenceArtifact:
        """Create an INCOMPLETE_MEASUREMENT evidence from Oracle failure.

        This is a critical safety path: Oracle failures must NOT produce
        zero-error evidence that could lead to false acceptance.
        """
        # Extract failure info
        failure_kind = getattr(oracle_failure, "kind", "UNKNOWN")
        failure_message = getattr(oracle_failure, "message", "")
        failure_exit_code = getattr(oracle_failure, "exit_code", -1)

        # Create a single finding documenting the failure
        finding = Finding(
            finding_id="EGER-FIND-ORACLE-FAILURE",
            severity="error",
            category="oracle_failure",
            entity="oracle_invocation",
            message=f"Oracle failure: {failure_kind} (exit_code={failure_exit_code}): {failure_message}",
            source="EvidenceNormalizer",
            expected_state="Oracle produces valid evidence",
            observed_state=f"Oracle failed with {failure_kind}",
            remediation_hint="Check Oracle availability and input validity",
            provenance={
                "failure_kind": failure_kind,
                "exit_code": failure_exit_code,
            },
        )

        summary = FindingSummary.from_findings([finding])

        ts = timestamp or _now_iso()
        evidence_id = f"EGER-EVID-FAILURE-{_deterministic_hash(failure_message)[:8].upper()}"

        return EvidenceArtifact(
            evidence_id=evidence_id,
            task_id=task_id,
            oracle_status="ORACLE_FAILURE",
            evidence_scope="UNSUPPORTED",
            findings=(finding,),
            summary=summary,
            analysis_scope={},
            raw_ref={"failure_kind": failure_kind},
            schema_version=SCHEMA_EVIDENCE,
            created_at=ts,
        )

    # -- Private helpers ---------------------------------------------------

    def _extract_oracle_status(self, evidence: Any) -> str:
        """Extract and map Oracle status."""
        raw_status = getattr(evidence, "oracle_status", None) or "UNKNOWN"
        return _map_oracle_status(raw_status)

    def _extract_evidence_scope(self, evidence: Any) -> str:
        """Extract and map evidence scope."""
        raw_scope = getattr(evidence, "evidence_scope", None) or "UNSUPPORTED"
        return _map_scope(raw_scope)

    def _extract_findings(self, evidence: Any) -> List[Dict[str, Any]]:
        """Extract raw findings from Oracle evidence."""
        findings = getattr(evidence, "findings", None) or []
        # Findings may be dicts or objects
        if findings and isinstance(findings[0], dict):
            return findings
        # If they're objects, convert to dicts
        result = []
        for f in findings:
            if hasattr(f, "to_dict"):
                result.append(f.to_dict())
            elif isinstance(f, dict):
                result.append(f)
            else:
                # Try to extract attributes
                result.append({
                    "finding_id": getattr(f, "finding_id", ""),
                    "code": getattr(f, "code", ""),
                    "severity": getattr(f, "severity", "info"),
                    "message": getattr(f, "message", ""),
                    "location": getattr(f, "location", {}),
                    "related_location": getattr(f, "related_location", None),
                    "context": getattr(f, "context", None),
                    "affected_object": getattr(f, "affected_object", None),
                    "finding_identity": getattr(f, "finding_identity", None),
                })
        return result

    def _extract_analysis_scope(self, evidence: Any) -> Optional[Dict[str, Any]]:
        """Extract analysis scope."""
        scope = getattr(evidence, "analysis_scope", None)
        if scope is None:
            return None
        if isinstance(scope, dict):
            return scope
        if hasattr(scope, "to_dict"):
            return scope.to_dict()
        return None

    def _extract_artifact_id(self, evidence: Any) -> str:
        """Extract Oracle artifact ID."""
        return getattr(evidence, "artifact_id", "") or "UNKNOWN"

    def _extract_provenance(self, evidence: Any) -> Dict[str, Any]:
        """Extract Oracle provenance."""
        prov = getattr(evidence, "provenance", None) or {}
        if isinstance(prov, dict):
            return prov
        return {}

    def _normalize_findings(
        self, raw_findings: List[Dict[str, Any]], oracle_artifact_id: str
    ) -> Tuple[List[Finding], List[str]]:
        """Normalize raw Oracle findings into Finding objects.

        Returns:
            (findings, unmapped_severities)
        """
        findings = []
        unmapped = []
        counter = 0

        for raw in raw_findings:
            counter += 1

            # Extract severity
            raw_sev = raw.get("severity") or raw.get("sev") or "info"
            severity = _map_severity(raw_sev)
            if severity is None:
                unmapped.append(raw_sev)
                continue

            # Extract fields
            finding_id = raw.get("finding_id", "") or f"EGER-FIND-{oracle_artifact_id[:8]}-{counter:03d}"
            code = raw.get("code", "")
            message = raw.get("message") or raw.get("msg", "")
            location = raw.get("location", {})
            related_location = raw.get("related_location")
            context = raw.get("context")
            affected_object = raw.get("affected_object") or raw.get("entity", "")
            finding_identity = raw.get("finding_identity") or raw.get("identity")

            # Build entity from location if available
            entity = affected_object
            if not entity and location:
                line = location.get("line", 0)
                if line:
                    entity = f"line {line}"

            # Build expected/observed from context if available
            expected_state = ""
            observed_state = ""
            if context:
                if isinstance(context, dict):
                    expected_state = context.get("expected", "")
                    observed_state = context.get("observed", "")
                elif isinstance(context, str):
                    observed_state = context

            # Build remediation hint
            remediation_hint = ""
            if code:
                remediation_hint = f"Fix {code}: {message}"

            # Build provenance
            provenance = {
                "oracle_artifact_id": oracle_artifact_id,
                "oracle_code": code,
                "oracle_line": location.get("line", 0) if isinstance(location, dict) else 0,
            }
            if finding_identity:
                provenance["oracle_identity"] = str(finding_identity)

            finding = Finding(
                finding_id=finding_id,
                severity=severity,
                category=code or "unknown",
                entity=entity,
                message=message,
                source=code or "oracle",
                expected_state=expected_state,
                observed_state=observed_state,
                remediation_hint=remediation_hint,
                provenance=provenance,
            )
            findings.append(finding)

        return findings, unmapped
