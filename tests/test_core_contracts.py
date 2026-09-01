"""Deterministic unit tests for EGER core contracts (P138).

Tests verify:
- Valid construction for every contract
- Invalid construction rejection
- Deterministic hashing
- Deterministic serialization
- Authority safety (LLM cannot mutate evidence)
- Invariant enforcement

No live model calls. No external dependencies. Fully deterministic.
"""

import hashlib
import json
import pytest
from typing import Dict, Any

from eger.task.definition import TaskDefinition
from eger.evidence.schemas import Finding, EvidenceArtifact, FindingSummary
from eger.prompting.request import PromptRequest
from eger.verification.result import VerificationResult
from eger.revision.record import RunRecord, RevisionConfig
from eger.provenance.tracker import ProvenanceTracker


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ===========================================================================
# TaskDefinition
# ===========================================================================

class TestTaskDefinition:
    """Tests for eger.task.definition.TaskDefinition"""

    def test_valid_construction(self):
        t = TaskDefinition(
            task_id="T-001",
            design_context="Module top with ports clk, reset.",
            objective="Generate a complete, production-quality SDC.",
            initial_sdc="create_clock -name clk -period 10.0 [get_ports clk]",
            constraints=["No generated clocks"],
        )
        assert t.task_id == "T-001"
        assert t.schema_version == "eger.task.v1"

    def test_empty_task_id_rejected(self):
        with pytest.raises(ValueError, match="task_id"):
            TaskDefinition(
                task_id="",
                design_context="ctx",
                objective="obj",
                initial_sdc="sdc",
                constraints=["c"],
            )

    def test_empty_design_context_rejected(self):
        with pytest.raises(ValueError, match="design_context"):
            TaskDefinition(
                task_id="T-001",
                design_context="",
                objective="obj",
                initial_sdc="sdc",
                constraints=["c"],
            )

    def test_empty_objective_rejected(self):
        with pytest.raises(ValueError, match="objective"):
            TaskDefinition(
                task_id="T-001",
                design_context="ctx",
                objective="",
                initial_sdc="sdc",
                constraints=["c"],
            )

    def test_empty_initial_sdc_rejected(self):
        with pytest.raises(ValueError, match="initial_sdc"):
            TaskDefinition(
                task_id="T-001",
                design_context="ctx",
                objective="obj",
                initial_sdc="",
                constraints=["c"],
            )

    def test_empty_constraints_rejected(self):
        with pytest.raises(ValueError, match="constraints"):
            TaskDefinition(
                task_id="T-001",
                design_context="ctx",
                objective="obj",
                initial_sdc="sdc",
                constraints=[],
            )

    def test_deterministic_hash(self):
        t1 = TaskDefinition(
            task_id="T-001", design_context="ctx", objective="obj",
            initial_sdc="sdc", constraints=["c1"],
        )
        t2 = TaskDefinition(
            task_id="T-001", design_context="ctx", objective="obj",
            initial_sdc="sdc", constraints=["c1"],
        )
        assert t1.task_hash == t2.task_hash

    def test_different_tasks_different_hash(self):
        t1 = TaskDefinition(
            task_id="T-001", design_context="ctx", objective="obj",
            initial_sdc="sdc", constraints=["c1"],
        )
        t2 = TaskDefinition(
            task_id="T-002", design_context="ctx", objective="obj",
            initial_sdc="sdc", constraints=["c1"],
        )
        assert t1.task_hash != t2.task_hash

    def test_sdc_hash_deterministic(self):
        t = TaskDefinition(
            task_id="T-001", design_context="ctx", objective="obj",
            initial_sdc="create_clock -name clk -period 10.0 [get_ports clk]",
            constraints=["c1"],
        )
        assert t.sdc_hash == _sha256("create_clock -name clk -period 10.0 [get_ports clk]")

    def test_objective_hash_deterministic(self):
        t = TaskDefinition(
            task_id="T-001", design_context="ctx",
            objective="Generate a complete, production-quality SDC.",
            initial_sdc="sdc", constraints=["c1"],
        )
        assert t.objective_hash == _sha256("Generate a complete, production-quality SDC.")

    def test_serialization_roundtrip(self):
        t = TaskDefinition(
            task_id="T-001", design_context="ctx", objective="obj",
            initial_sdc="sdc", constraints=["c1", "c2"],
        )
        d = t.to_dict()
        t2 = TaskDefinition.from_dict(d)
        assert t.task_id == t2.task_id
        assert t.design_context == t2.design_context
        assert t.objective == t2.objective
        assert t.initial_sdc == t2.initial_sdc
        assert t.constraints == t2.constraints

    def test_frozen(self):
        t = TaskDefinition(
            task_id="T-001", design_context="ctx", objective="obj",
            initial_sdc="sdc", constraints=["c1"],
        )
        with pytest.raises(AttributeError):
            t.task_id = "T-002"


# ===========================================================================
# Finding
# ===========================================================================

class TestFinding:
    """Tests for eger.evidence.schemas.Finding"""

    def test_valid_construction(self):
        f = Finding(
            finding_id="F-001",
            severity="error",
            category="missing_constraint",
            entity="port data_in",
            message="No input delay found",
            source="SDC-001",
            expected_state="set_input_delay defined",
            observed_state="Not found",
            remediation_hint="Add set_input_delay",
        )
        assert f.finding_id == "F-001"
        assert f.severity == "error"
        assert f.is_error is True
        assert f.is_warning is False
        assert f.is_info is False

    def test_empty_finding_id_rejected(self):
        with pytest.raises(ValueError, match="finding_id"):
            Finding(
                finding_id="",
                severity="error",
                category="c",
                entity="e",
                message="m",
                source="s",
                expected_state="e",
                observed_state="o",
                remediation_hint="r",
            )

    def test_invalid_severity_rejected(self):
        with pytest.raises(ValueError, match="severity"):
            Finding(
                finding_id="F-001",
                severity="critical",
                category="c",
                entity="e",
                message="m",
                source="s",
                expected_state="e",
                observed_state="o",
                remediation_hint="r",
            )

    def test_empty_source_rejected(self):
        with pytest.raises(ValueError, match="source"):
            Finding(
                finding_id="F-001",
                severity="error",
                category="c",
                entity="e",
                message="m",
                source="",
                expected_state="e",
                observed_state="o",
                remediation_hint="r",
            )

    def test_severity_levels(self):
        for sev in ("error", "warning", "info"):
            f = Finding(
                finding_id="F-001", severity=sev, category="c", entity="e",
                message="m", source="s", expected_state="e",
                observed_state="o", remediation_hint="r",
            )
            assert f.severity == sev

    def test_serialization_roundtrip(self):
        f = Finding(
            finding_id="F-001", severity="error", category="missing",
            entity="port", message="msg", source="SDC-001",
            expected_state="expected", observed_state="observed",
            remediation_hint="hint", provenance={"key": "value"},
        )
        d = f.to_dict()
        f2 = Finding.from_dict(d)
        assert f.finding_id == f2.finding_id
        assert f.severity == f2.severity
        assert f.provenance == f2.provenance

    def test_frozen(self):
        f = Finding(
            finding_id="F-001", severity="error", category="c", entity="e",
            message="m", source="s", expected_state="e",
            observed_state="o", remediation_hint="r",
        )
        with pytest.raises(AttributeError):
            f.severity = "warning"


# ===========================================================================
# FindingSummary
# ===========================================================================

class TestFindingSummary:
    """Tests for eger.evidence.schemas.FindingSummary"""

    def test_from_findings(self):
        findings = [
            Finding(finding_id="F-1", severity="error", category="c", entity="e",
                    message="m", source="s", expected_state="e",
                    observed_state="o", remediation_hint="r"),
            Finding(finding_id="F-2", severity="error", category="c", entity="e",
                    message="m", source="s", expected_state="e",
                    observed_state="o", remediation_hint="r"),
            Finding(finding_id="F-3", severity="warning", category="c", entity="e",
                    message="m", source="s", expected_state="e",
                    observed_state="o", remediation_hint="r"),
            Finding(finding_id="F-4", severity="info", category="c", entity="e",
                    message="m", source="s", expected_state="e",
                    observed_state="o", remediation_hint="r"),
        ]
        s = FindingSummary.from_findings(findings)
        assert s.error_count == 2
        assert s.warning_count == 1
        assert s.info_count == 1
        assert s.total_count == 4

    def test_empty_findings(self):
        s = FindingSummary.from_findings([])
        assert s.error_count == 0
        assert s.warning_count == 0
        assert s.info_count == 0
        assert s.total_count == 0


# ===========================================================================
# EvidenceArtifact
# ===========================================================================

class TestEvidenceArtifact:
    """Tests for eger.evidence.schemas.EvidenceArtifact"""

    def _make_finding(self, fid: str, severity: str = "error") -> Finding:
        return Finding(
            finding_id=fid, severity=severity, category="c", entity="e",
            message="m", source="s", expected_state="e",
            observed_state="o", remediation_hint="r",
        )

    def test_valid_construction(self):
        findings = (self._make_finding("F-1"),)
        summary = FindingSummary.from_findings(list(findings))
        ea = EvidenceArtifact(
            evidence_id="E-001",
            task_id="T-001",
            oracle_status="SUCCESS",
            evidence_scope="FULL",
            findings=findings,
            summary=summary,
            analysis_scope={"status": "VALIDATED"},
        )
        assert ea.evidence_id == "E-001"
        assert ea.has_errors is True
        assert len(ea.error_findings) == 1

    def test_empty_evidence_id_rejected(self):
        findings = (self._make_finding("F-1"),)
        summary = FindingSummary.from_findings(list(findings))
        with pytest.raises(ValueError, match="evidence_id"):
            EvidenceArtifact(
                evidence_id="",
                task_id="T-001",
                oracle_status="SUCCESS",
                evidence_scope="FULL",
                findings=findings,
                summary=summary,
                analysis_scope={},
            )

    def test_invalid_oracle_status_rejected(self):
        findings = (self._make_finding("F-1"),)
        summary = FindingSummary.from_findings(list(findings))
        with pytest.raises(ValueError, match="oracle_status"):
            EvidenceArtifact(
                evidence_id="E-001",
                task_id="T-001",
                oracle_status="INVALID",
                evidence_scope="FULL",
                findings=findings,
                summary=summary,
                analysis_scope={},
            )

    def test_invalid_evidence_scope_rejected(self):
        findings = (self._make_finding("F-1"),)
        summary = FindingSummary.from_findings(list(findings))
        with pytest.raises(ValueError, match="evidence_scope"):
            EvidenceArtifact(
                evidence_id="E-001",
                task_id="T-001",
                oracle_status="SUCCESS",
                evidence_scope="INVALID",
                findings=findings,
                summary=summary,
                analysis_scope={},
            )

    def test_summary_mismatch_rejected(self):
        findings = (self._make_finding("F-1"),)
        summary = FindingSummary(error_count=0, warning_count=0, info_count=0, total_count=0)
        with pytest.raises(ValueError, match="summary.error_count"):
            EvidenceArtifact(
                evidence_id="E-001",
                task_id="T-001",
                oracle_status="SUCCESS",
                evidence_scope="FULL",
                findings=findings,
                summary=summary,
                analysis_scope={},
            )

    def test_no_errors(self):
        findings = (self._make_finding("F-1", severity="warning"),)
        summary = FindingSummary.from_findings(list(findings))
        ea = EvidenceArtifact(
            evidence_id="E-001", task_id="T-001",
            oracle_status="SUCCESS", evidence_scope="FULL",
            findings=findings, summary=summary, analysis_scope={},
        )
        assert ea.has_errors is False
        assert len(ea.error_findings) == 0
        assert len(ea.warning_findings) == 1

    def test_evidence_hash_deterministic(self):
        findings = (self._make_finding("F-1"),)
        summary = FindingSummary.from_findings(list(findings))
        ea1 = EvidenceArtifact(
            evidence_id="E-001", task_id="T-001",
            oracle_status="SUCCESS", evidence_scope="FULL",
            findings=findings, summary=summary, analysis_scope={},
        )
        ea2 = EvidenceArtifact(
            evidence_id="E-001", task_id="T-001",
            oracle_status="SUCCESS", evidence_scope="FULL",
            findings=findings, summary=summary, analysis_scope={},
        )
        assert ea1.evidence_hash == ea2.evidence_hash

    def test_serialization_roundtrip(self):
        findings = (self._make_finding("F-1"), self._make_finding("F-2", "warning"))
        summary = FindingSummary.from_findings(list(findings))
        ea = EvidenceArtifact(
            evidence_id="E-001", task_id="T-001",
            oracle_status="SUCCESS", evidence_scope="FULL",
            findings=findings, summary=summary, analysis_scope={"status": "VALIDATED"},
        )
        d = ea.to_dict()
        ea2 = EvidenceArtifact.from_dict(d)
        assert ea.evidence_id == ea2.evidence_id
        assert len(ea2.findings) == 2
        assert ea2.summary.error_count == 1

    def test_frozen(self):
        findings = (self._make_finding("F-1"),)
        summary = FindingSummary.from_findings(list(findings))
        ea = EvidenceArtifact(
            evidence_id="E-001", task_id="T-001",
            oracle_status="SUCCESS", evidence_scope="FULL",
            findings=findings, summary=summary, analysis_scope={},
        )
        with pytest.raises(AttributeError):
            ea.evidence_id = "E-002"


# ===========================================================================
# PromptRequest
# ===========================================================================

class TestPromptRequest:
    """Tests for eger.prompting.request.PromptRequest"""

    def test_valid_construction(self):
        pr = PromptRequest(
            request_id="PR-001",
            task_id="T-001",
            prompt_hash=_sha256("prompt text"),
            objective_hash=_sha256("objective"),
            iteration=0,
        )
        assert pr.request_id == "PR-001"
        assert pr.iteration == 0

    def test_empty_request_id_rejected(self):
        with pytest.raises(ValueError, match="request_id"):
            PromptRequest(
                request_id="", task_id="T-001",
                prompt_hash="h", objective_hash="h", iteration=0,
            )

    def test_empty_task_id_rejected(self):
        with pytest.raises(ValueError, match="task_id"):
            PromptRequest(
                request_id="PR-001", task_id="",
                prompt_hash="h", objective_hash="h", iteration=0,
            )

    def test_empty_prompt_hash_rejected(self):
        with pytest.raises(ValueError, match="prompt_hash"):
            PromptRequest(
                request_id="PR-001", task_id="T-001",
                prompt_hash="", objective_hash="h", iteration=0,
            )

    def test_negative_iteration_rejected(self):
        with pytest.raises(ValueError, match="iteration"):
            PromptRequest(
                request_id="PR-001", task_id="T-001",
                prompt_hash="h", objective_hash="h", iteration=-1,
            )

    def test_hash_prompt_deterministic(self):
        h1 = PromptRequest.hash_prompt("test prompt")
        h2 = PromptRequest.hash_prompt("test prompt")
        assert h1 == h2
        assert h1 == _sha256("test prompt")

    def test_serialization_roundtrip(self):
        pr = PromptRequest(
            request_id="PR-001", task_id="T-001",
            prompt_hash="ph", objective_hash="oh",
            iteration=2, evidence_id="E-001",
        )
        d = pr.to_dict()
        pr2 = PromptRequest.from_dict(d)
        assert pr.request_id == pr2.request_id
        assert pr.iteration == pr2.iteration
        assert pr.evidence_id == pr2.evidence_id

    def test_frozen(self):
        pr = PromptRequest(
            request_id="PR-001", task_id="T-001",
            prompt_hash="h", objective_hash="h", iteration=0,
        )
        with pytest.raises(AttributeError):
            pr.iteration = 1


# ===========================================================================
# VerificationResult
# ===========================================================================

class TestVerificationResult:
    """Tests for eger.verification.result.VerificationResult"""

    def test_valid_accept(self):
        vr = VerificationResult(
            decision="ACCEPT",
            reason="All errors resolved",
            error_count=0,
            unresolved_findings=[],
            provenance={"gate": "verification"},
        )
        assert vr.is_accepted is True
        assert vr.is_rejected is False

    def test_valid_reject(self):
        vr = VerificationResult(
            decision="REJECT",
            reason="Unresolved errors",
            error_count=2,
            unresolved_findings=["F-1", "F-2"],
            provenance={"gate": "verification"},
        )
        assert vr.is_rejected is True
        assert vr.is_accepted is False

    def test_invalid_decision_rejected(self):
        with pytest.raises(ValueError, match="decision"):
            VerificationResult(
                decision="PENDING",
                reason="r",
                error_count=0,
                unresolved_findings=[],
                provenance={},
            )

    def test_negative_error_count_rejected(self):
        with pytest.raises(ValueError, match="error_count"):
            VerificationResult(
                decision="REJECT",
                reason="r",
                error_count=-1,
                unresolved_findings=[],
                provenance={},
            )

    def test_serialization_roundtrip(self):
        vr = VerificationResult(
            decision="REJECT", reason="r", error_count=1,
            unresolved_findings=["F-1"], provenance={"k": "v"},
        )
        d = vr.to_dict()
        vr2 = VerificationResult.from_dict(d)
        assert vr.decision == vr2.decision
        assert vr.error_count == vr2.error_count

    def test_frozen(self):
        vr = VerificationResult(
            decision="ACCEPT", reason="r", error_count=0,
            unresolved_findings=[], provenance={},
        )
        with pytest.raises(AttributeError):
            vr.decision = "REJECT"


# ===========================================================================
# RevisionConfig
# ===========================================================================

class TestRevisionConfig:
    """Tests for eger.revision.record.RevisionConfig"""

    def test_valid_construction(self):
        rc = RevisionConfig()
        assert rc.max_iterations == 5
        assert rc.max_total_calls == 15

    def test_invalid_max_iterations(self):
        with pytest.raises(ValueError, match="max_iterations"):
            RevisionConfig(max_iterations=0)

    def test_invalid_max_total_calls(self):
        with pytest.raises(ValueError, match="max_total_calls"):
            RevisionConfig(max_total_calls=2)

    def test_invalid_timeout(self):
        with pytest.raises(ValueError, match="timeout_seconds"):
            RevisionConfig(timeout_seconds=0)

    def test_serialization_roundtrip(self):
        rc = RevisionConfig(max_iterations=3, max_total_calls=9)
        d = rc.to_dict()
        rc2 = RevisionConfig.from_dict(d)
        assert rc.max_iterations == rc2.max_iterations
        assert rc.max_total_calls == rc2.max_total_calls


# ===========================================================================
# RunRecord
# ===========================================================================

class TestRunRecord:
    """Tests for eger.revision.record.RunRecord"""

    def test_valid_accepted(self):
        rc = RevisionConfig()
        rr = RunRecord(
            run_id="R-001",
            task_id="T-001",
            config=rc,
            iterations=({"iter": 1},),
            final_decision="ACCEPT",
            final_evidence_id="E-001",
            final_candidate_id="C-001",
            total_calls=3,
            duration_seconds=10.5,
            status="ACCEPTED",
            provenance={"model": "mimo-v2.5-free"},
        )
        assert rr.is_accepted is True
        assert rr.iteration_count == 1

    def test_valid_rejected(self):
        rc = RevisionConfig()
        rr = RunRecord(
            run_id="R-001", task_id="T-001", config=rc,
            iterations=(), final_decision="REJECT",
            final_evidence_id=None, final_candidate_id=None,
            total_calls=6, duration_seconds=20.0,
            status="REJECTED", provenance={},
        )
        assert rr.is_rejected is True

    def test_valid_incomplete(self):
        rc = RevisionConfig()
        rr = RunRecord(
            run_id="R-001", task_id="T-001", config=rc,
            iterations=(), final_decision="INCOMPLETE",
            final_evidence_id=None, final_candidate_id=None,
            total_calls=1, duration_seconds=5.0,
            status="INCOMPLETE", provenance={"reason": "timeout"},
        )
        assert rr.is_incomplete is True

    def test_invalid_status_rejected(self):
        rc = RevisionConfig()
        with pytest.raises(ValueError, match="status"):
            RunRecord(
                run_id="R-001", task_id="T-001", config=rc,
                iterations=(), final_decision="PENDING",
                final_evidence_id=None, final_candidate_id=None,
                total_calls=0, duration_seconds=0.0,
                status="PENDING", provenance={},
            )

    def test_negative_total_calls_rejected(self):
        rc = RevisionConfig()
        with pytest.raises(ValueError, match="total_calls"):
            RunRecord(
                run_id="R-001", task_id="T-001", config=rc,
                iterations=(), final_decision="REJECT",
                final_evidence_id=None, final_candidate_id=None,
                total_calls=-1, duration_seconds=0.0,
                status="REJECTED", provenance={},
            )

    def test_serialization_roundtrip(self):
        rc = RevisionConfig(max_iterations=3)
        rr = RunRecord(
            run_id="R-001", task_id="T-001", config=rc,
            iterations=({"iter": 1},), final_decision="ACCEPT",
            final_evidence_id="E-001", final_candidate_id="C-001",
            total_calls=3, duration_seconds=10.0,
            status="ACCEPTED", provenance={"k": "v"},
        )
        d = rr.to_dict()
        rr2 = RunRecord.from_dict(d)
        assert rr.run_id == rr2.run_id
        assert rr.status == rr2.status
        assert rr.config.max_iterations == rr2.config.max_iterations

    def test_frozen(self):
        rc = RevisionConfig()
        rr = RunRecord(
            run_id="R-001", task_id="T-001", config=rc,
            iterations=(), final_decision="ACCEPT",
            final_evidence_id=None, final_candidate_id=None,
            total_calls=0, duration_seconds=0.0,
            status="ACCEPTED", provenance={},
        )
        with pytest.raises(AttributeError):
            rr.status = "REJECTED"


# ===========================================================================
# ProvenanceTracker
# ===========================================================================

class TestProvenanceTracker:
    """Tests for eger.provenance.tracker.ProvenanceTracker"""

    def test_record_entry(self):
        pt = ProvenanceTracker()
        entry = pt.record(
            artifact_id="A-001",
            artifact_type="evidence",
            producer="oracle",
            input_hash="ih",
            output_hash="oh",
        )
        assert entry.artifact_id == "A-001"
        assert pt.entry_count == 1

    def test_append_only(self):
        pt = ProvenanceTracker()
        pt.record("A-1", "evidence", "oracle", "ih", "oh")
        pt.record("A-2", "candidate", "llm", "ih2", "oh2")
        assert pt.entry_count == 2
        # Cannot modify entries
        entries = pt.entries
        assert len(entries) == 2

    def test_get_entry(self):
        pt = ProvenanceTracker()
        pt.record("A-1", "evidence", "oracle", "ih", "oh")
        entry = pt.get_entry("A-1")
        assert entry is not None
        assert entry.artifact_id == "A-1"
        assert pt.get_entry("A-999") is None

    def test_serialization_roundtrip(self):
        pt = ProvenanceTracker()
        pt.record("A-1", "evidence", "oracle", "ih", "oh", {"key": "val"})
        d = pt.to_dict()
        pt2 = ProvenanceTracker.from_dict(d)
        assert pt2.entry_count == 1
        assert pt2.get_entry("A-1").metadata == {"key": "val"}


# ===========================================================================
# Authority Safety
# ===========================================================================

class TestAuthoritySafety:
    """Verify that authority boundaries are preserved."""

    def test_candidate_starts_unverified(self):
        """CandidateArtifact must start with verified=False."""
        from eger.engineer.candidate import build_candidate
        c = build_candidate("create_clock -name clk -period 10.0 [get_ports clk]")
        assert c.verified is False

    def test_evidence_is_frozen(self):
        """EvidenceArtifact cannot be mutated."""
        findings = (Finding(
            finding_id="F-1", severity="error", category="c", entity="e",
            message="m", source="s", expected_state="e",
            observed_state="o", remediation_hint="r",
        ),)
        summary = FindingSummary.from_findings(list(findings))
        ea = EvidenceArtifact(
            evidence_id="E-001", task_id="T-001",
            oracle_status="SUCCESS", evidence_scope="FULL",
            findings=findings, summary=summary, analysis_scope={},
        )
        with pytest.raises(AttributeError):
            ea.evidence_id = "E-002"

    def test_verification_result_is_frozen(self):
        """VerificationResult cannot be mutated."""
        vr = VerificationResult(
            decision="ACCEPT", reason="r", error_count=0,
            unresolved_findings=[], provenance={},
        )
        with pytest.raises(AttributeError):
            vr.decision = "REJECT"

    def test_run_record_is_frozen(self):
        """RunRecord cannot be mutated."""
        rc = RevisionConfig()
        rr = RunRecord(
            run_id="R-001", task_id="T-001", config=rc,
            iterations=(), final_decision="ACCEPT",
            final_evidence_id=None, final_candidate_id=None,
            total_calls=0, duration_seconds=0.0,
            status="ACCEPTED", provenance={},
        )
        with pytest.raises(AttributeError):
            rr.status = "REJECTED"
