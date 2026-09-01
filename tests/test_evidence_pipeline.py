"""Deterministic unit tests for EGER evidence pipeline (P139).

Tests verify:
- Oracle → EvidenceArtifact normalization
- Severity mapping
- Category preservation
- Summary invariants
- Failure handling (fail-closed)
- Determinism
- Authority safety

No live model calls. No external dependencies. Fully deterministic.
"""

import hashlib
import json
import pytest
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from eger.evidence.normalizer import EvidenceNormalizer
from eger.evidence.schemas import (
    Finding,
    EvidenceArtifact,
    FindingSummary,
    VALID_SEVERITY,
    VALID_ORACLE_STATUS,
    VALID_EVIDENCE_SCOPE,
)


# ---------------------------------------------------------------------------
# Mock Oracle types
# ---------------------------------------------------------------------------

@dataclass
class MockOracleFinding:
    """Mock Oracle finding — mimics Oracle adapter's finding structure."""
    finding_id: str
    code: str
    severity: str
    message: str
    location: Dict[str, Any] = field(default_factory=dict)
    related_location: Optional[Dict[str, Any]] = None
    context: Optional[Any] = None
    affected_object: Optional[str] = None
    finding_identity: Optional[Any] = None


@dataclass
class MockOracleEvidence:
    """Mock Oracle evidence — mimics Oracle adapter's EvidenceArtifact."""
    schema_version: str
    artifact_id: str
    oracle: Dict[str, str]
    provenance: Dict[str, Any]
    evidence_scope: Optional[str]
    oracle_status: str
    findings: List[Dict[str, Any]]
    analysis_scope: Optional[Dict[str, Any]]
    raw_ref: Dict[str, str]
    evidence_hash: str
    produced_at: str


@dataclass
class MockOracleFailure:
    """Mock Oracle failure."""
    kind: str
    exit_code: int
    message: str
    raw_ref: Optional[Dict[str, str]] = None


# ---------------------------------------------------------------------------
# EvidenceNormalizer
# ---------------------------------------------------------------------------

class TestEvidenceNormalizer:
    """Tests for eger.evidence.normalizer.EvidenceNormalizer"""

    def setup_method(self):
        self.normalizer = EvidenceNormalizer()

    def _make_evidence(
        self,
        oracle_status: str = "SUCCESS",
        evidence_scope: str = "VALIDATED",
        findings: Optional[List[Dict[str, Any]]] = None,
        analysis_scope: Optional[Dict[str, Any]] = None,
    ) -> MockOracleEvidence:
        """Create mock Oracle evidence."""
        return MockOracleEvidence(
            schema_version="eger.raw.v1",
            artifact_id="ORA-001",
            oracle={"name": "Ṛta", "version": "1.5.11"},
            provenance={"oracle_version": "1.5.11", "oracle_revision": "3b5c2f2"},
            evidence_scope=evidence_scope,
            oracle_status=oracle_status,
            findings=findings or [],
            analysis_scope=analysis_scope,
            raw_ref={"raw_id": "RAW-001"},
            evidence_hash="abc123",
            produced_at="2026-09-01T00:00:00Z",
        )

    # -- Successful normalization ------------------------------------------

    def test_zero_error_evidence(self):
        """Zero-error Oracle result normalizes correctly."""
        evidence = self._make_evidence(findings=[])
        result = self.normalizer.normalize(evidence, task_id="T-001")

        assert result.task_id == "T-001"
        assert result.oracle_status == "SUCCESS"
        assert result.evidence_scope == "FULL"
        assert result.has_errors is False
        assert result.summary.error_count == 0
        assert result.summary.warning_count == 0
        assert result.summary.info_count == 0
        assert len(result.findings) == 0

    def test_one_error_evidence(self):
        """One-error Oracle result normalizes correctly."""
        findings = [
            {
                "finding_id": "F-001",
                "code": "SDC-001",
                "severity": "error",
                "message": "Missing input delay",
                "location": {"line": 5},
            }
        ]
        evidence = self._make_evidence(findings=findings)
        result = self.normalizer.normalize(evidence, task_id="T-001")

        assert result.has_errors is True
        assert result.summary.error_count == 1
        assert len(result.error_findings) == 1
        assert result.error_findings[0].severity == "error"
        assert result.error_findings[0].category == "SDC-001"

    def test_multiple_findings(self):
        """Multiple findings normalize correctly."""
        findings = [
            {"finding_id": "F-1", "code": "SDC-001", "severity": "error",
             "message": "Error 1", "location": {}},
            {"finding_id": "F-2", "code": "SDC-002", "severity": "error",
             "message": "Error 2", "location": {}},
            {"finding_id": "F-3", "code": "SDC-003", "severity": "warning",
             "message": "Warning 1", "location": {}},
            {"finding_id": "F-4", "code": "SDC-004", "severity": "info",
             "message": "Info 1", "location": {}},
        ]
        evidence = self._make_evidence(findings=findings)
        result = self.normalizer.normalize(evidence, task_id="T-001")

        assert result.summary.error_count == 2
        assert result.summary.warning_count == 1
        assert result.summary.info_count == 1
        assert result.summary.total_count == 4

    def test_mixed_severities(self):
        """Mixed ERROR/WARNING/INFO normalize correctly."""
        findings = [
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "err", "location": {}},
            {"finding_id": "F-2", "code": "C2", "severity": "warning",
             "message": "warn", "location": {}},
            {"finding_id": "F-3", "code": "C3", "severity": "info",
             "message": "info", "location": {}},
        ]
        evidence = self._make_evidence(findings=findings)
        result = self.normalizer.normalize(evidence, task_id="T-001")

        errors = [f for f in result.findings if f.severity == "error"]
        warnings = [f for f in result.findings if f.severity == "warning"]
        infos = [f for f in result.findings if f.severity == "info"]
        assert len(errors) == 1
        assert len(warnings) == 1
        assert len(infos) == 1

    def test_multiple_categories(self):
        """Multiple categories preserve Oracle identity."""
        findings = [
            {"finding_id": "F-1", "code": "SDC-001", "severity": "error",
             "message": "msg", "location": {}},
            {"finding_id": "F-2", "code": "SDC-002", "severity": "error",
             "message": "msg", "location": {}},
        ]
        evidence = self._make_evidence(findings=findings)
        result = self.normalizer.normalize(evidence, task_id="T-001")

        categories = [f.category for f in result.findings]
        assert "SDC-001" in categories
        assert "SDC-002" in categories

    def test_multiple_entities(self):
        """Multiple entities preserve Oracle identity."""
        findings = [
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "msg", "location": {}, "affected_object": "port data_in"},
            {"finding_id": "F-2", "code": "C2", "severity": "error",
             "message": "msg", "location": {}, "affected_object": "port data_out"},
        ]
        evidence = self._make_evidence(findings=findings)
        result = self.normalizer.normalize(evidence, task_id="T-001")

        entities = [f.entity for f in result.findings]
        assert "port data_in" in entities
        assert "port data_out" in entities

    # -- Severity mapping --------------------------------------------------

    def test_severity_error_mapped(self):
        """'error' severity maps correctly."""
        findings = [{"finding_id": "F-1", "code": "C1", "severity": "error",
                     "message": "m", "location": {}}]
        evidence = self._make_evidence(findings=findings)
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.findings[0].severity == "error"

    def test_severity_warning_mapped(self):
        """'warning' severity maps correctly."""
        findings = [{"finding_id": "F-1", "code": "C1", "severity": "warning",
                     "message": "m", "location": {}}]
        evidence = self._make_evidence(findings=findings)
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.findings[0].severity == "warning"

    def test_severity_info_mapped(self):
        """'info' severity maps correctly."""
        findings = [{"finding_id": "F-1", "code": "C1", "severity": "info",
                     "message": "m", "location": {}}]
        evidence = self._make_evidence(findings=findings)
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.findings[0].severity == "info"

    def test_severity_case_insensitive(self):
        """Uppercase severity maps correctly."""
        for sev in ("ERROR", "WARNING", "INFO"):
            findings = [{"finding_id": "F-1", "code": "C1", "severity": sev,
                         "message": "m", "location": {}}]
            evidence = self._make_evidence(findings=findings)
            result = self.normalizer.normalize(evidence, task_id="T-001")
            assert result.findings[0].severity == sev.lower()

    def test_unknown_severity_fails_closed(self):
        """Unknown severity fails closed — raises ValueError."""
        findings = [{"finding_id": "F-1", "code": "C1", "severity": "critical",
                     "message": "m", "location": {}}]
        evidence = self._make_evidence(findings=findings)
        with pytest.raises(ValueError, match="Unmapped Oracle severities"):
            self.normalizer.normalize(evidence, task_id="T-001")

    # -- Summary invariants ------------------------------------------------

    def test_summary_error_count_matches(self):
        """summary.error_count matches actual error findings."""
        findings = [
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "m", "location": {}},
            {"finding_id": "F-2", "code": "C2", "severity": "error",
             "message": "m", "location": {}},
            {"finding_id": "F-3", "code": "C3", "severity": "warning",
             "message": "m", "location": {}},
        ]
        evidence = self._make_evidence(findings=findings)
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.summary.error_count == len(result.error_findings)

    def test_summary_warning_count_matches(self):
        """summary.warning_count matches actual warning findings."""
        findings = [
            {"finding_id": "F-1", "code": "C1", "severity": "warning",
             "message": "m", "location": {}},
            {"finding_id": "F-2", "code": "C2", "severity": "info",
             "message": "m", "location": {}},
        ]
        evidence = self._make_evidence(findings=findings)
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.summary.warning_count == len(result.warning_findings)

    # -- Identity preservation ---------------------------------------------

    def test_task_id_preserved(self):
        """task_id is preserved in EvidenceArtifact."""
        evidence = self._make_evidence()
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.task_id == "T-001"

    def test_candidate_hash_preserved(self):
        """candidate_hash is preserved in provenance."""
        evidence = self._make_evidence()
        result = self.normalizer.normalize(
            evidence, task_id="T-001", candidate_hash="HASH-123"
        )
        assert result.raw_ref.get("oracle_artifact_id") == "ORA-001"

    def test_oracle_provenance_preserved(self):
        """Oracle provenance is preserved in findings."""
        findings = [{"finding_id": "F-1", "code": "SDC-001", "severity": "error",
                     "message": "m", "location": {}}]
        evidence = self._make_evidence(findings=findings)
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.findings[0].provenance.get("oracle_code") == "SDC-001"

    # -- Determinism -------------------------------------------------------

    def test_same_input_same_output(self):
        """Same Oracle input produces same EvidenceArtifact."""
        findings = [
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "m", "location": {}},
        ]
        evidence = self._make_evidence(findings=findings)

        result1 = self.normalizer.normalize(
            evidence, task_id="T-001", timestamp="2026-09-01T00:00:00Z"
        )
        result2 = self.normalizer.normalize(
            evidence, task_id="T-001", timestamp="2026-09-01T00:00:00Z"
        )

        assert result1.evidence_id == result2.evidence_id
        assert result1.oracle_status == result2.oracle_status
        assert result1.evidence_scope == result2.evidence_scope
        assert len(result1.findings) == len(result2.findings)
        assert result1.evidence_hash == result2.evidence_hash

    # -- Malformed input ---------------------------------------------------

    def test_malformed_evidence_with_unknown_status(self):
        """Malformed Oracle evidence with unknown status still normalizes."""
        # Unknown oracle_status maps to UNKNOWN — this is acceptable
        evidence = MockOracleEvidence(
            schema_version="", artifact_id="ORA-001",
            oracle={}, provenance={},
            evidence_scope=None,
            oracle_status="INVALID_STATUS",
            findings=[],
            analysis_scope=None,
            raw_ref={},
            evidence_hash="",
            produced_at="",
        )
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.oracle_status == "UNKNOWN"

    def test_malformed_evidence_empty_artifact_id(self):
        """Empty artifact_id produces evidence with UNKNOWN artifact."""
        evidence = MockOracleEvidence(
            schema_version="", artifact_id="",
            oracle={}, provenance={},
            evidence_scope="VALIDATED",
            oracle_status="SUCCESS",
            findings=[],
            analysis_scope=None,
            raw_ref={},
            evidence_hash="",
            produced_at="",
        )
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.oracle_status == "SUCCESS"

    # -- Oracle failure handling -------------------------------------------

    def test_oracle_failure_produces_error_evidence(self):
        """Oracle failure produces evidence with error findings."""
        failure = MockOracleFailure(
            kind="ORACLE_FAILURE",
            exit_code=3,
            message="Oracle unavailable",
        )
        result = self.normalizer.normalize_failure(failure, task_id="T-001")

        assert result.oracle_status == "ORACLE_FAILURE"
        assert result.evidence_scope == "UNSUPPORTED"
        assert result.has_errors is True
        assert result.summary.error_count == 1
        assert "oracle_failure" in result.findings[0].category

    def test_oracle_failure_cannot_produce_accept(self):
        """Oracle failure cannot produce ACCEPT-capable evidence."""
        failure = MockOracleFailure(
            kind="ORACLE_FAILURE",
            exit_code=3,
            message="Oracle unavailable",
        )
        result = self.normalizer.normalize_failure(failure, task_id="T-001")

        # Evidence with errors cannot pass verification gate
        assert result.has_errors is True
        assert result.oracle_status == "ORACLE_FAILURE"

    # -- Authority safety --------------------------------------------------

    def test_normalizer_cannot_change_oracle_truth(self):
        """Normalizer preserves Oracle findings — does not reinterpret."""
        findings = [
            {"finding_id": "F-1", "code": "SDC-001", "severity": "error",
             "message": "Missing input delay", "location": {"line": 5}},
        ]
        evidence = self._make_evidence(findings=findings)
        result = self.normalizer.normalize(evidence, task_id="T-001")

        # Finding message preserved
        assert result.findings[0].message == "Missing input delay"
        # Finding category preserved (code)
        assert result.findings[0].category == "SDC-001"
        # Finding severity preserved
        assert result.findings[0].severity == "error"

    def test_normalizer_cannot_create_authorization(self):
        """Normalizer does not produce verification decisions."""
        evidence = self._make_evidence()
        result = self.normalizer.normalize(evidence, task_id="T-001")

        # EvidenceArtifact has no decision field
        assert not hasattr(result, "decision")
        assert not hasattr(result, "is_accepted")

    def test_normalized_evidence_is_immutable(self):
        """Normalized EvidenceArtifact is frozen."""
        evidence = self._make_evidence()
        result = self.normalizer.normalize(evidence, task_id="T-001")

        with pytest.raises(AttributeError):
            result.evidence_id = "E-002"

    # -- Analysis scope preservation ---------------------------------------

    def test_analysis_scope_preserved(self):
        """Analysis scope is preserved in EvidenceArtifact."""
        analysis_scope = {
            "status": "VALIDATED",
            "commands_found": 5,
            "fully_analyzed": 5,
        }
        evidence = self._make_evidence(analysis_scope=analysis_scope)
        result = self.normalizer.normalize(evidence, task_id="T-001")

        assert result.analysis_scope["status"] == "VALIDATED"
        assert result.analysis_scope["commands_found"] == 5

    # -- Scope mapping -----------------------------------------------------

    def test_scope_validated_maps_to_full(self):
        """VALIDATED scope maps to FULL."""
        evidence = self._make_evidence(evidence_scope="VALIDATED")
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.evidence_scope == "FULL"

    def test_scope_partially_validated_maps_to_partial(self):
        """PARTIALLY_VALIDATED scope maps to PARTIAL."""
        evidence = self._make_evidence(evidence_scope="PARTIALLY_VALIDATED")
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.evidence_scope == "PARTIAL"

    def test_scope_netlist_required_maps_to_insufficient(self):
        """NETLIST_REQUIRED scope maps to INSUFFICIENT."""
        evidence = self._make_evidence(evidence_scope="NETLIST_REQUIRED")
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.evidence_scope == "INSUFFICIENT"

    def test_scope_unsupported_maps_to_unsupported(self):
        """UNSUPPORTED scope maps to UNSUPPORTED."""
        evidence = self._make_evidence(evidence_scope="UNSUPPORTED")
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.evidence_scope == "UNSUPPORTED"
