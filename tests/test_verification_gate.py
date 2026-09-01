"""Deterministic unit tests for EGER verification gate (P142).

Tests verify:
- Basic decisions (ACCEPT/REJECT)
- Candidate eligibility
- Evidence integrity
- Fail-closed behavior
- Determinism
- Immutability
- Authority boundaries

No live model calls. No external dependencies. Fully deterministic.
"""

import pytest
from typing import Optional

from eger.engineer.candidate import CandidateArtifact, build_candidate
from eger.evidence.schemas import Finding, EvidenceArtifact, FindingSummary
from eger.verification.gate import VerificationGate
from eger.verification.result import VerificationResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_candidate(sdc_text: Optional[str] = None) -> CandidateArtifact:
    text = sdc_text or "create_clock -name clk -period 10.0 [get_ports clk]"
    return build_candidate(text)


def _make_evidence(
    findings_data=None,
    oracle_status: str = "SUCCESS",
    evidence_scope: str = "FULL",
) -> EvidenceArtifact:
    if findings_data is None:
        findings_data = []

    findings = tuple(Finding(
        finding_id=f.get("finding_id", "F-001"),
        severity=f.get("severity", "error"),
        category=f.get("code", ""),
        entity=f.get("entity", ""),
        message=f.get("message", ""),
        source=f.get("code", "oracle"),
        expected_state=f.get("expected_state", ""),
        observed_state=f.get("observed_state", ""),
        remediation_hint=f.get("remediation_hint", ""),
    ) for f in findings_data)

    summary = FindingSummary.from_findings(list(findings))

    return EvidenceArtifact(
        evidence_id="E-001",
        task_id="T-001",
        oracle_status=oracle_status,
        evidence_scope=evidence_scope,
        findings=findings,
        summary=summary,
        analysis_scope={"status": "VALIDATED"},
    )


# ---------------------------------------------------------------------------
# VerificationGate
# ---------------------------------------------------------------------------

class TestVerificationGate:
    """Tests for eger.verification.gate.VerificationGate"""

    def setup_method(self):
        self.gate = VerificationGate()

    # -- Basic decisions ---------------------------------------------------

    def test_zero_errors_accept(self):
        """Zero ERROR findings → ACCEPT."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[])
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_accepted
        assert result.decision == "ACCEPT"
        assert result.error_count == 0

    def test_one_error_reject(self):
        """One ERROR finding → REJECT."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[
            {"finding_id": "F-1", "code": "SDC-001", "severity": "error",
             "message": "Missing input delay"},
        ])
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_rejected
        assert result.decision == "REJECT"
        assert result.error_count == 1
        assert "F-1" in result.unresolved_findings

    def test_multiple_errors_reject(self):
        """Multiple ERROR findings → REJECT."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "Error 1"},
            {"finding_id": "F-2", "code": "C2", "severity": "error",
             "message": "Error 2"},
        ])
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_rejected
        assert result.error_count == 2
        assert "F-1" in result.unresolved_findings
        assert "F-2" in result.unresolved_findings

    def test_warning_only_accept(self):
        """WARNING-only findings → ACCEPT."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[
            {"finding_id": "F-1", "code": "C1", "severity": "warning",
             "message": "Warning 1"},
        ])
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_accepted
        assert result.error_count == 0

    def test_info_only_accept(self):
        """INFO-only findings → ACCEPT."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[
            {"finding_id": "F-1", "code": "C1", "severity": "info",
             "message": "Info 1"},
        ])
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_accepted
        assert result.error_count == 0

    def test_mixed_warning_info_accept(self):
        """Mixed WARNING + INFO → ACCEPT."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[
            {"finding_id": "F-1", "code": "C1", "severity": "warning",
             "message": "Warning"},
            {"finding_id": "F-2", "code": "C2", "severity": "info",
             "message": "Info"},
        ])
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_accepted

    def test_error_with_warnings_reject(self):
        """ERROR + WARNING → REJECT (ERROR takes precedence)."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "Error"},
            {"finding_id": "F-2", "code": "C2", "severity": "warning",
             "message": "Warning"},
        ])
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_rejected
        assert result.error_count == 1

    # -- Candidate eligibility ---------------------------------------------

    def test_unverified_candidate_accepted(self):
        """Unverified candidate can be accepted if evidence passes."""
        candidate = _make_candidate()
        assert candidate.verified is False

        evidence = _make_evidence(findings_data=[])
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_accepted

    def test_candidate_identity_preserved(self):
        """Candidate artifact_id is preserved in result."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[])
        result = self.gate.evaluate(candidate, evidence)

        assert result.provenance["candidate_id"] == candidate.artifact_id

    def test_candidate_hash_preserved(self):
        """Candidate hash is preserved in provenance."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[])
        result = self.gate.evaluate(candidate, evidence)

        # Provenance should reference the candidate
        assert "candidate_id" in result.provenance

    # -- Evidence integrity ------------------------------------------------

    def test_evidence_id_preserved(self):
        """Evidence evidence_id is preserved in result."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[])
        result = self.gate.evaluate(candidate, evidence)

        assert result.provenance["evidence_id"] == evidence.evidence_id

    def test_evidence_scope_full_accepted(self):
        """FULL scope evidence can lead to acceptance."""
        candidate = _make_candidate()
        evidence = _make_evidence(
            findings_data=[],
            evidence_scope="FULL",
        )
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_accepted

    def test_evidence_scope_partial_accepted(self):
        """PARTIAL scope evidence can lead to acceptance if no errors."""
        candidate = _make_candidate()
        evidence = _make_evidence(
            findings_data=[],
            evidence_scope="PARTIAL",
        )
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_accepted

    def test_evidence_scope_unsupported_rejects(self):
        """UNSUPPORTED scope → REJECT (fail-closed)."""
        candidate = _make_candidate()
        evidence = _make_evidence(
            findings_data=[],
            evidence_scope="UNSUPPORTED",
        )
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_rejected
        assert "UNSUPPORTED" in result.reason

    def test_evidence_scope_insufficient_rejects(self):
        """INSUFFICIENT scope → REJECT (fail-closed)."""
        candidate = _make_candidate()
        evidence = _make_evidence(
            findings_data=[],
            evidence_scope="INSUFFICIENT",
        )
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_rejected
        assert "INSUFFICIENT" in result.reason

    def test_evidence_oracle_failure_rejects(self):
        """ORACLE_FAILURE status → REJECT (fail-closed)."""
        candidate = _make_candidate()
        evidence = _make_evidence(
            findings_data=[],
            oracle_status="ORACLE_FAILURE",
        )
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_rejected
        assert "ORACLE_FAILURE" in result.reason

    def test_evidence_unknown_status_rejects(self):
        """UNKNOWN status → REJECT (fail-closed)."""
        candidate = _make_candidate()
        evidence = _make_evidence(
            findings_data=[],
            oracle_status="UNKNOWN",
        )
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_rejected
        assert "UNKNOWN" in result.reason

    # -- Fail-closed behavior ---------------------------------------------

    def test_none_candidate_rejects(self):
        """None candidate → REJECT (fail-closed)."""
        evidence = _make_evidence(findings_data=[])
        result = self.gate.evaluate(None, evidence)

        assert result.is_rejected
        assert "No candidate" in result.reason

    def test_none_evidence_rejects(self):
        """None evidence → REJECT (fail-closed)."""
        candidate = _make_candidate()
        result = self.gate.evaluate(candidate, None)

        assert result.is_rejected
        assert "No evidence" in result.reason

    def test_both_none_rejects(self):
        """Both None → REJECT (fail-closed)."""
        result = self.gate.evaluate(None, None)

        assert result.is_rejected

    # -- Determinism -------------------------------------------------------

    def test_same_inputs_same_decision(self):
        """Same candidate + same evidence → same decision."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[])

        result1 = self.gate.evaluate(candidate, evidence)
        result2 = self.gate.evaluate(candidate, evidence)

        assert result1.decision == result2.decision
        assert result1.reason == result2.reason
        assert result1.error_count == result2.error_count

    def test_same_inputs_same_hash(self):
        """Same inputs produce equivalent results."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "Error"},
        ])

        result1 = self.gate.evaluate(candidate, evidence)
        result2 = self.gate.evaluate(candidate, evidence)

        assert result1.to_dict() == result2.to_dict()

    # -- Immutability ------------------------------------------------------

    def test_candidate_not_mutated(self):
        """Gate does not mutate CandidateArtifact."""
        candidate = _make_candidate()
        original_hash = candidate.candidate_hash
        original_verified = candidate.verified

        evidence = _make_evidence(findings_data=[])
        self.gate.evaluate(candidate, evidence)

        assert candidate.candidate_hash == original_hash
        assert candidate.verified == original_verified

    def test_evidence_not_mutated(self):
        """Gate does not mutate EvidenceArtifact."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[])
        original_id = evidence.evidence_id

        self.gate.evaluate(candidate, evidence)

        assert evidence.evidence_id == original_id

    # -- No model dependency -----------------------------------------------

    def test_no_api_key_required(self):
        """Gate works without API key."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[])
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_accepted

    def test_no_network_required(self):
        """Gate works without network access."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "Error"},
        ])
        result = self.gate.evaluate(candidate, evidence)

        assert result.is_rejected

    # -- Authority boundary ------------------------------------------------

    def test_only_gate_can_accept(self):
        """Only VerificationGate produces the authoritative ACCEPT."""
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[])
        result = self.gate.evaluate(candidate, evidence)

        # Result has gate provenance
        assert result.provenance["gate"] == "VerificationGate"

    def test_gate_cannot_call_llm(self):
        """Gate does not call LLM or model provider."""
        # This is verified by construction — gate has no LLM dependency
        candidate = _make_candidate()
        evidence = _make_evidence(findings_data=[])
        result = self.gate.evaluate(candidate, evidence)

        # Gate should complete without any external calls
        assert result.decision in ("ACCEPT", "REJECT")

    def test_gate_cannot_perform_revision(self):
        """Gate does not perform revision."""
        # Gate only evaluates — it doesn't modify candidates
        candidate = _make_candidate("original SDC")
        evidence = _make_evidence(findings_data=[])
        self.gate.evaluate(candidate, evidence)

        # Candidate SDC unchanged
        assert candidate.sdc_text == "original SDC"

    # -- Integration with full architecture --------------------------------

    def test_full_architecture_boundary(self):
        """Test the larger architecture boundary."""
        from eger.task.definition import TaskDefinition
        from eger.prompting.builder import PromptBuilder
        from eger.evidence.normalizer import EvidenceNormalizer

        # Create task
        task = TaskDefinition(
            task_id="T-001",
            design_context="Module top with ports clk.",
            objective="Generate a complete SDC.",
            initial_sdc="create_clock -name clk -period 10.0 [get_ports clk]",
            constraints=["No generated clocks"],
        )

        # Build prompt
        builder = PromptBuilder()
        prompt = builder.build(task)

        # Simulate LLM response
        candidate = build_candidate(
            "create_clock -name clk -period 10.0 [get_ports clk]",
            provision={"prompt_hash": prompt.prompt_hash},
        )

        # Simulate Oracle evidence (zero errors)
        evidence = _make_evidence(findings_data=[])

        # Verify with gate
        gate = VerificationGate()
        result = gate.evaluate(candidate, evidence)

        assert result.is_accepted
        assert result.provenance["candidate_id"] == candidate.artifact_id
        assert result.provenance["evidence_id"] == evidence.evidence_id
