"""Tests for P155 Input Validation & Size Limits.

Deterministic tests for:
- TaskDefinition size limits
- CandidateArtifact / build_candidate size limits
- Finding size limits
- EvidenceArtifact findings count limit
- RevisionConfig max bounds
- Fail-closed behavior for oversized input
- No semantic overreach on valid SDC
- Backward compatibility for valid inputs
"""

import pytest

from eger.task.definition import TaskDefinition
from eger.engineer.candidate import CandidateArtifact, build_candidate
from eger.evidence.schemas import Finding, EvidenceArtifact, FindingSummary
from eger.revision.record import RevisionConfig
from eger.contracts import (
    MAX_TASK_ID_LENGTH,
    MAX_DESIGN_CONTEXT_LENGTH,
    MAX_OBJECTIVE_LENGTH,
    MAX_INITIAL_SDC_LENGTH,
    MAX_CONSTRAINTS_COUNT,
    MAX_CONSTRAINT_LENGTH,
    MAX_SDC_TEXT_LENGTH,
    MAX_ARTIFACT_ID_LENGTH,
    MAX_FINDINGS_COUNT,
    MAX_FINDING_MESSAGE_LENGTH,
    MAX_FINDING_ID_LENGTH,
    MAX_EVIDENCE_ID_LENGTH,
)


# ===========================================================================
# Helpers
# ===========================================================================


def _make_task(**overrides) -> TaskDefinition:
    defaults = dict(
        task_id="T-001",
        design_context="Module top with ports clk, reset.",
        objective="Generate a complete, production-quality SDC.",
        initial_sdc="create_clock -name clk -period 10.0 [get_ports clk]",
        constraints=["No generated clocks"],
    )
    defaults.update(overrides)
    return TaskDefinition(**defaults)


def _make_finding(**overrides) -> Finding:
    defaults = dict(
        finding_id="EGER-FIND-001",
        severity="error",
        category="SDC-001",
        entity="line 1",
        message="Missing input delay",
        source="oracle",
        expected_state="set_input_delay present",
        observed_state="not found",
        remediation_hint="Add set_input_delay",
    )
    defaults.update(overrides)
    return Finding(**defaults)


def _make_evidence(findings=None, **overrides) -> EvidenceArtifact:
    if findings is None:
        findings = (_make_finding(),)
    summary = FindingSummary.from_findings(list(findings))
    defaults = dict(
        evidence_id="EGER-EVID-001",
        task_id="T-001",
        oracle_status="SUCCESS",
        evidence_scope="FULL",
        findings=findings,
        summary=summary,
        analysis_scope={"status": "VALIDATED"},
    )
    defaults.update(overrides)
    return EvidenceArtifact(**defaults)


# ===========================================================================
# TaskDefinition — size limits
# ===========================================================================


class TestTaskDefinitionSizeLimits:
    """TaskDefinition rejects oversized fields."""

    def test_normal_task_accepted(self):
        task = _make_task()
        assert task.task_id == "T-001"

    def test_task_id_at_limit_accepted(self):
        task = _make_task(task_id="A" * MAX_TASK_ID_LENGTH)
        assert len(task.task_id) == MAX_TASK_ID_LENGTH

    def test_task_id_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="task_id length"):
            _make_task(task_id="A" * (MAX_TASK_ID_LENGTH + 1))

    def test_design_context_at_limit_accepted(self):
        task = _make_task(design_context="A" * MAX_DESIGN_CONTEXT_LENGTH)
        assert len(task.design_context) == MAX_DESIGN_CONTEXT_LENGTH

    def test_design_context_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="design_context length"):
            _make_task(design_context="A" * (MAX_DESIGN_CONTEXT_LENGTH + 1))

    def test_objective_at_limit_accepted(self):
        task = _make_task(objective="A" * MAX_OBJECTIVE_LENGTH)
        assert len(task.objective) == MAX_OBJECTIVE_LENGTH

    def test_objective_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="objective length"):
            _make_task(objective="A" * (MAX_OBJECTIVE_LENGTH + 1))

    def test_initial_sdc_at_limit_accepted(self):
        task = _make_task(initial_sdc="A" * MAX_INITIAL_SDC_LENGTH)
        assert len(task.initial_sdc) == MAX_INITIAL_SDC_LENGTH

    def test_initial_sdc_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="initial_sdc length"):
            _make_task(initial_sdc="A" * (MAX_INITIAL_SDC_LENGTH + 1))

    def test_constraints_count_at_limit_accepted(self):
        task = _make_task(constraints=[f"constraint {i}" for i in range(MAX_CONSTRAINTS_COUNT)])
        assert len(task.constraints) == MAX_CONSTRAINTS_COUNT

    def test_constraints_count_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="constraints count"):
            _make_task(constraints=[f"constraint {i}" for i in range(MAX_CONSTRAINTS_COUNT + 1)])

    def test_constraint_length_at_limit_accepted(self):
        task = _make_task(constraints=["A" * MAX_CONSTRAINT_LENGTH])
        assert len(task.constraints[0]) == MAX_CONSTRAINT_LENGTH

    def test_constraint_length_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="constraint.*length"):
            _make_task(constraints=["A" * (MAX_CONSTRAINT_LENGTH + 1)])


# ===========================================================================
# TaskDefinition — existing validation preserved
# ===========================================================================


class TestTaskDefinitionExistingValidation:
    """Existing non-empty validation still works."""

    def test_empty_task_id_rejected(self):
        with pytest.raises(ValueError, match="task_id must be non-empty"):
            _make_task(task_id="")

    def test_empty_design_context_rejected(self):
        with pytest.raises(ValueError, match="design_context must be non-empty"):
            _make_task(design_context="")

    def test_empty_objective_rejected(self):
        with pytest.raises(ValueError, match="objective must be non-empty"):
            _make_task(objective="")

    def test_empty_initial_sdc_rejected(self):
        with pytest.raises(ValueError, match="initial_sdc must be non-empty"):
            _make_task(initial_sdc="")

    def test_empty_constraints_rejected(self):
        with pytest.raises(ValueError, match="constraints must be non-empty"):
            _make_task(constraints=[])


# ===========================================================================
# CandidateArtifact / build_candidate — size limits
# ===========================================================================


class TestCandidateSizeLimits:
    """build_candidate rejects oversized sdc_text."""

    def test_normal_candidate_accepted(self):
        candidate = build_candidate("create_clock -name clk -period 10.0 [get_ports clk]")
        assert candidate.sdc_text.startswith("create_clock")

    def test_sdc_text_at_limit_accepted(self):
        sdc = "A" * MAX_SDC_TEXT_LENGTH
        candidate = build_candidate(sdc)
        assert len(candidate.sdc_text) == MAX_SDC_TEXT_LENGTH

    def test_sdc_text_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="sdc_text length"):
            build_candidate("A" * (MAX_SDC_TEXT_LENGTH + 1))

    def test_empty_sdc_text_accepted(self):
        """Empty string is valid — build_candidate does not require non-empty."""
        candidate = build_candidate("")
        assert candidate.sdc_text == ""

    def test_type_error_for_non_string(self):
        with pytest.raises(TypeError, match="sdc_text must be str"):
            build_candidate(123)

    def test_custom_artifact_id_at_limit_accepted(self):
        aid = "A" * MAX_ARTIFACT_ID_LENGTH
        candidate = build_candidate("create_clock -name clk -period 10 [get_ports clk]", artifact_id=aid)
        assert candidate.artifact_id == aid

    def test_custom_artifact_id_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="artifact_id length"):
            build_candidate("create_clock -name clk -period 10 [get_ports clk]", artifact_id="A" * (MAX_ARTIFACT_ID_LENGTH + 1))


# ===========================================================================
# CandidateArtifact — backward compatibility
# ===========================================================================


class TestCandidateBackwardCompatibility:
    """Existing CandidateArtifact behavior preserved."""

    def test_candidate_is_frozen(self):
        candidate = build_candidate("create_clock -name clk -period 10 [get_ports clk]")
        with pytest.raises(AttributeError):
            candidate.sdc_text = "modified"

    def test_candidate_hash_deterministic(self):
        sdc = "create_clock -name clk -period 10 [get_ports clk]"
        c1 = build_candidate(sdc)
        c2 = build_candidate(sdc)
        assert c1.candidate_hash == c2.candidate_hash

    def test_candidate_to_dict_round_trip(self):
        sdc = "create_clock -name clk -period 10 [get_ports clk]"
        candidate = build_candidate(sdc)
        d = candidate.to_dict()
        restored = CandidateArtifact.from_dict(d)
        assert restored.sdc_text == candidate.sdc_text
        assert restored.candidate_hash == candidate.candidate_hash


# ===========================================================================
# Finding — size limits
# ===========================================================================


class TestFindingSizeLimits:
    """Finding rejects oversized fields."""

    def test_normal_finding_accepted(self):
        f = _make_finding()
        assert f.finding_id == "EGER-FIND-001"

    def test_finding_id_at_limit_accepted(self):
        f = _make_finding(finding_id="F" * MAX_FINDING_ID_LENGTH)
        assert len(f.finding_id) == MAX_FINDING_ID_LENGTH

    def test_finding_id_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="finding_id length"):
            _make_finding(finding_id="F" * (MAX_FINDING_ID_LENGTH + 1))

    def test_message_at_limit_accepted(self):
        f = _make_finding(message="M" * MAX_FINDING_MESSAGE_LENGTH)
        assert len(f.message) == MAX_FINDING_MESSAGE_LENGTH

    def test_message_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="finding message length"):
            _make_finding(message="M" * (MAX_FINDING_MESSAGE_LENGTH + 1))

    def test_empty_message_accepted(self):
        f = _make_finding(message="")
        assert f.message == ""


# ===========================================================================
# Finding — existing validation preserved
# ===========================================================================


class TestFindingExistingValidation:
    """Existing Finding validation still works."""

    def test_empty_finding_id_rejected(self):
        with pytest.raises(ValueError, match="finding_id must be non-empty"):
            _make_finding(finding_id="")

    def test_invalid_severity_rejected(self):
        with pytest.raises(ValueError, match="severity must be one of"):
            _make_finding(severity="critical")

    def test_empty_source_rejected(self):
        with pytest.raises(ValueError, match="source must be non-empty"):
            _make_finding(source="")


# ===========================================================================
# EvidenceArtifact — findings count limit
# ===========================================================================


class TestEvidenceFindingsLimit:
    """EvidenceArtifact rejects excessive findings count."""

    def test_normal_evidence_accepted(self):
        evidence = _make_evidence()
        assert evidence.evidence_id == "EGER-EVID-001"

    def test_findings_at_limit_accepted(self):
        findings = tuple(_make_finding(finding_id=f"F-{i}") for i in range(MAX_FINDINGS_COUNT))
        summary = FindingSummary.from_findings(list(findings))
        evidence = _make_evidence(findings=findings, summary=summary)
        assert len(evidence.findings) == MAX_FINDINGS_COUNT

    def test_findings_exceeds_limit_rejected(self):
        findings = tuple(_make_finding(finding_id=f"F-{i}") for i in range(MAX_FINDINGS_COUNT + 1))
        summary = FindingSummary.from_findings(list(findings))
        with pytest.raises(ValueError, match="findings count"):
            _make_evidence(findings=findings, summary=summary)

    def test_evidence_id_at_limit_accepted(self):
        evidence = _make_evidence(evidence_id="E" * MAX_EVIDENCE_ID_LENGTH)
        assert len(evidence.evidence_id) == MAX_EVIDENCE_ID_LENGTH

    def test_evidence_id_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="evidence_id length"):
            _make_evidence(evidence_id="E" * (MAX_EVIDENCE_ID_LENGTH + 1))


# ===========================================================================
# EvidenceArtifact — existing validation preserved
# ===========================================================================


class TestEvidenceExistingValidation:
    """Existing EvidenceArtifact validation still works."""

    def test_empty_evidence_id_rejected(self):
        with pytest.raises(ValueError, match="evidence_id must be non-empty"):
            _make_evidence(evidence_id="")

    def test_invalid_oracle_status_rejected(self):
        with pytest.raises(ValueError, match="oracle_status must be one of"):
            _make_evidence(oracle_status="INVALID")

    def test_invalid_evidence_scope_rejected(self):
        with pytest.raises(ValueError, match="evidence_scope must be one of"):
            _make_evidence(evidence_scope="INVALID")

    def test_summary_mismatch_rejected(self):
        finding = _make_finding(severity="error")
        wrong_summary = FindingSummary(error_count=0, warning_count=0, info_count=0, total_count=0)
        with pytest.raises(ValueError, match="summary.error_count"):
            _make_evidence(findings=(finding,), summary=wrong_summary)


# ===========================================================================
# RevisionConfig — max bounds
# ===========================================================================


class TestRevisionConfigMaxBounds:
    """RevisionConfig rejects excessive values."""

    def test_normal_config_accepted(self):
        config = RevisionConfig()
        assert config.max_iterations == 5

    def test_iterations_at_limit_accepted(self):
        config = RevisionConfig(max_iterations=100)
        assert config.max_iterations == 100

    def test_iterations_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="max_iterations must be <= 100"):
            RevisionConfig(max_iterations=101)

    def test_calls_at_limit_accepted(self):
        config = RevisionConfig(max_total_calls=500)
        assert config.max_total_calls == 500

    def test_calls_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="max_total_calls must be <= 500"):
            RevisionConfig(max_total_calls=501)

    def test_temperature_at_limit_accepted(self):
        config = RevisionConfig(temperature=2.0)
        assert config.temperature == 2.0

    def test_temperature_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="temperature must be between"):
            RevisionConfig(temperature=2.1)

    def test_negative_temperature_rejected(self):
        with pytest.raises(ValueError, match="temperature must be between"):
            RevisionConfig(temperature=-0.1)

    def test_max_tokens_at_limit_accepted(self):
        config = RevisionConfig(max_tokens=128_000)
        assert config.max_tokens == 128_000

    def test_max_tokens_exceeds_limit_rejected(self):
        with pytest.raises(ValueError, match="max_tokens must be between"):
            RevisionConfig(max_tokens=128_001)

    def test_zero_max_tokens_rejected(self):
        with pytest.raises(ValueError, match="max_tokens must be between"):
            RevisionConfig(max_tokens=0)


# ===========================================================================
# RevisionConfig — existing validation preserved
# ===========================================================================


class TestRevisionConfigExistingValidation:
    """Existing RevisionConfig validation still works."""

    def test_zero_iterations_rejected(self):
        with pytest.raises(ValueError, match="max_iterations must be >= 1"):
            RevisionConfig(max_iterations=0)

    def test_two_calls_rejected(self):
        with pytest.raises(ValueError, match="max_total_calls must be >= 3"):
            RevisionConfig(max_total_calls=2)

    def test_zero_timeout_rejected(self):
        with pytest.raises(ValueError, match="timeout_seconds must be >= 1"):
            RevisionConfig(timeout_seconds=0)


# ===========================================================================
# Fail-closed: oversized input cannot become ACCEPT
# ===========================================================================


class TestFailClosed:
    """Oversized input must not bypass VerificationGate."""

    def test_oversized_candidate_rejected_before_oracle(self):
        """build_candidate rejects oversized sdc_text — Oracle is never invoked."""
        with pytest.raises(ValueError, match="sdc_text length"):
            build_candidate("A" * (MAX_SDC_TEXT_LENGTH + 1))

    def test_oversized_task_rejected_before_prompt(self):
        """TaskDefinition rejects oversized fields — prompt is never built."""
        with pytest.raises(ValueError, match="task_id length"):
            _make_task(task_id="A" * (MAX_TASK_ID_LENGTH + 1))

    def test_oversized_finding_rejected_before_verification(self):
        """Finding rejects oversized message — verification never sees it."""
        with pytest.raises(ValueError, match="finding message length"):
            _make_finding(message="M" * (MAX_FINDING_MESSAGE_LENGTH + 1))


# ===========================================================================
# Backward compatibility: valid inputs still work
# ===========================================================================


class TestBackwardCompatibility:
    """All existing valid inputs continue to work."""

    def test_typical_task_works(self):
        task = _make_task()
        assert task.task_hash is not None

    def test_typical_candidate_works(self):
        sdc = "create_clock -name clk -period 10.0 [get_ports clk]"
        candidate = build_candidate(sdc)
        assert candidate.candidate_hash is not None

    def test_typical_finding_works(self):
        f = _make_finding()
        assert f.is_error

    def test_typical_evidence_works(self):
        evidence = _make_evidence()
        assert evidence.has_errors

    def test_typical_config_works(self):
        config = RevisionConfig()
        assert config.max_iterations == 5

    def test_serialization_round_trip_task(self):
        task = _make_task()
        d = task.to_dict()
        restored = TaskDefinition.from_dict(d)
        assert restored.task_id == task.task_id

    def test_serialization_round_trip_config(self):
        config = RevisionConfig(max_iterations=10)
        d = config.to_dict()
        restored = RevisionConfig.from_dict(d)
        assert restored.max_iterations == 10
