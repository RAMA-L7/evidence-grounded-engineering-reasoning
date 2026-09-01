"""EGER Evidence Schemas — typed, deterministic evidence contracts.

EMPIRICALLY SUPPORTED: structured feedback (C1/C2).

These contracts define the normalized evidence representation that flows
between the Oracle and the RevisionController. They are NOT modifiable
by the LLM layer.

INVARIANT: EvidenceArtifact is a data boundary, not an authority bypass.
INVARIANT: The LLM cannot mutate EvidenceArtifact through CandidateArtifact.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import hashlib
import json

SCHEMA_FINDING = "eger.finding.v1"
SCHEMA_EVIDENCE = "eger.evidence.v1"

VALID_SEVERITY = {"error", "warning", "info"}
VALID_ORACLE_STATUS = {"SUCCESS", "INVALID_REQUEST", "ORACLE_FAILURE", "UNKNOWN"}
VALID_EVIDENCE_SCOPE = {"FULL", "PARTIAL", "INSUFFICIENT", "UNSUPPORTED"}


def _deterministic_hash(text: str) -> str:
    """SHA256 hash — deterministic."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _now_iso() -> str:
    """UTC timestamp — deterministic for same call sequence."""
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Finding:
    """Single evidence finding — immutable once created.

    INVARIANT: severity must be one of: error, warning, info.
    INVARIANT: finding_id must be non-empty.
    INVARIANT: source must be non-empty.
    INVARIANT: all fields are immutable (frozen=True).
    """
    finding_id: str
    severity: str
    category: str
    entity: str
    message: str
    source: str
    expected_state: str
    observed_state: str
    remediation_hint: str
    provenance: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_FINDING

    def __post_init__(self):
        """Validate invariants."""
        if not self.finding_id:
            raise ValueError("finding_id must be non-empty")
        if self.severity not in VALID_SEVERITY:
            raise ValueError(f"severity must be one of {VALID_SEVERITY}, got '{self.severity}'")
        if not self.source:
            raise ValueError("source must be non-empty")

    @property
    def is_error(self) -> bool:
        return self.severity == "error"

    @property
    def is_warning(self) -> bool:
        return self.severity == "warning"

    @property
    def is_info(self) -> bool:
        return self.severity == "info"

    def to_dict(self) -> Dict[str, Any]:
        """Deterministic serialization."""
        return {
            "schema_version": self.schema_version,
            "finding_id": self.finding_id,
            "severity": self.severity,
            "category": self.category,
            "entity": self.entity,
            "message": self.message,
            "source": self.source,
            "expected_state": self.expected_state,
            "observed_state": self.observed_state,
            "remediation_hint": self.remediation_hint,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Finding:
        """Deserialize from dict."""
        return cls(
            finding_id=d["finding_id"],
            severity=d["severity"],
            category=d.get("category", ""),
            entity=d.get("entity", ""),
            message=d.get("message", ""),
            source=d["source"],
            expected_state=d.get("expected_state", ""),
            observed_state=d.get("observed_state", ""),
            remediation_hint=d.get("remediation_hint", ""),
            provenance=dict(d.get("provenance", {})),
            schema_version=d.get("schema_version", SCHEMA_FINDING),
        )


@dataclass(frozen=True)
class FindingSummary:
    """Aggregate counts — deterministic given findings list.

    INVARIANT: error_count == len([f for f in findings if f.severity == "error"])
    INVARIANT: warning_count == len([f for f in findings if f.severity == "warning"])
    INVARIANT: info_count == len([f for f in findings if f.severity == "info"])
    """
    error_count: int
    warning_count: int
    info_count: int
    total_count: int

    @classmethod
    def from_findings(cls, findings: List[Finding]) -> FindingSummary:
        """Deterministic construction from findings list."""
        errors = sum(1 for f in findings if f.severity == "error")
        warnings = sum(1 for f in findings if f.severity == "warning")
        infos = sum(1 for f in findings if f.severity == "info")
        return cls(
            error_count=errors,
            warning_count=warnings,
            info_count=infos,
            total_count=len(findings),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "total_count": self.total_count,
        }


@dataclass(frozen=True)
class EvidenceArtifact:
    """Normalized evidence — immutable once created.

    INVARIANT: summary.error_count == len([f for f in findings if f.severity == "error"])
    INVARIANT: oracle_status must be in VALID_ORACLE_STATUS
    INVARIANT: evidence_scope must be in VALID_EVIDENCE_SCOPE
    INVARIANT: evidence_id must be non-empty
    INVARIANT: all fields are immutable (frozen=True)
    INVARIANT: LLM cannot mutate this through CandidateArtifact

    PRODUCER: EvidenceNormalizer (deterministic)
    CONSUMER: RevisionController, VerificationGate, PromptBuilder
    AUTHORITY: EVIDENCE — not modifiable by LLM
    """
    evidence_id: str
    task_id: str
    oracle_status: str
    evidence_scope: str
    findings: tuple  # Tuple[Finding, ...] — immutable
    summary: FindingSummary
    analysis_scope: Dict[str, Any]
    raw_ref: Dict[str, str] = field(default_factory=dict)
    schema_version: str = SCHEMA_EVIDENCE
    created_at: str = ""

    def __post_init__(self):
        """Validate invariants."""
        if not self.evidence_id:
            raise ValueError("evidence_id must be non-empty")
        if self.oracle_status not in VALID_ORACLE_STATUS:
            raise ValueError(f"oracle_status must be one of {VALID_ORACLE_STATUS}, got '{self.oracle_status}'")
        if self.evidence_scope not in VALID_EVIDENCE_SCOPE:
            raise ValueError(f"evidence_scope must be one of {VALID_EVIDENCE_SCOPE}, got '{self.evidence_scope}'")
        # Validate summary matches findings
        expected = FindingSummary.from_findings(list(self.findings))
        if self.summary.error_count != expected.error_count:
            raise ValueError(
                f"summary.error_count ({self.summary.error_count}) != "
                f"actual error findings ({expected.error_count})"
            )
        if self.summary.warning_count != expected.warning_count:
            raise ValueError(
                f"summary.warning_count ({self.summary.warning_count}) != "
                f"actual warning findings ({expected.warning_count})"
            )
        if self.summary.info_count != expected.info_count:
            raise ValueError(
                f"summary.info_count ({self.summary.info_count}) != "
                f"actual info findings ({expected.info_count})"
            )

    @property
    def has_errors(self) -> bool:
        return self.summary.error_count > 0

    @property
    def error_findings(self) -> List[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warning_findings(self) -> List[Finding]:
        return [f for f in self.findings if f.severity == "warning"]

    @property
    def evidence_hash(self) -> str:
        """Deterministic hash of evidence content."""
        data = {
            "evidence_id": self.evidence_id,
            "task_id": self.task_id,
            "oracle_status": self.oracle_status,
            "evidence_scope": self.evidence_scope,
            "findings": [f.to_dict() for f in self.findings],
        }
        return hashlib.sha256(
            json.dumps(data, sort_keys=True).encode("utf-8")
        ).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Deterministic serialization."""
        return {
            "schema_version": self.schema_version,
            "evidence_id": self.evidence_id,
            "task_id": self.task_id,
            "oracle_status": self.oracle_status,
            "evidence_scope": self.evidence_scope,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary.to_dict(),
            "analysis_scope": dict(self.analysis_scope),
            "raw_ref": dict(self.raw_ref),
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> EvidenceArtifact:
        """Deserialize from dict."""
        findings = tuple(Finding.from_dict(f) for f in d.get("findings", []))
        summary_data = d.get("summary", {})
        summary = FindingSummary(
            error_count=summary_data.get("error_count", 0),
            warning_count=summary_data.get("warning_count", 0),
            info_count=summary_data.get("info_count", 0),
            total_count=summary_data.get("total_count", len(findings)),
        )
        return cls(
            evidence_id=d["evidence_id"],
            task_id=d["task_id"],
            oracle_status=d["oracle_status"],
            evidence_scope=d["evidence_scope"],
            findings=findings,
            summary=summary,
            analysis_scope=dict(d.get("analysis_scope", {})),
            raw_ref=dict(d.get("raw_ref", {})),
            schema_version=d.get("schema_version", SCHEMA_EVIDENCE),
            created_at=d.get("created_at", ""),
        )
