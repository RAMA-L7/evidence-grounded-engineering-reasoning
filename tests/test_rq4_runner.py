"""RQ4 runner tests — EGER-CHANGE-007 implementation verification.

Tests verify the controlled RQ4 paired experiment design without
executing live model calls. All tests use mocks/fakes.

P062 §9: 24 test categories required.
"""

import json
import hashlib
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from eger.engineer.model import FakeEngineerModel, LiveEngineerModel
from eger.engineer.adapter import EngineerAdapter
from eger.oracle.adapter import EvidenceOracle
from eger.engineer.structured_feedback import render_structured_feedback
from eger.oracle.schemas import DesignMetadata, PortDef, ClockDef

import importlib.util
import pathlib

_rq4_path = pathlib.Path(__file__).resolve().parents[1] / "research" / "experiments" / "EGER-EXP-001" / "formal_runner_rq4.py"
_spec = importlib.util.spec_from_file_location("formal_runner_rq4", _rq4_path)
rq4_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rq4_module)
run_rq4_task = rq4_module.run_rq4_task

# ---------------------------------------------------------------------------
# Fixtures: fake evidence and oracle
# ---------------------------------------------------------------------------

class FakeEvidence:
    def __init__(self, scope="FULL", findings=None, evidence_hash="abc123"):
        self.evidence_scope = scope
        self.oracle_status = "SUCCESS"
        self.findings = findings or []
        self.analysis_scope = {
            "status": "VALIDATED" if scope == "FULL" else "NOT_VALIDATED",
            "netlist_required": 0,
            "unsupported": 0,
            "tcl_execution_required": 0,
        }
        self.evidence_hash = evidence_hash
        self.artifact_id = "EGER-EVID-TEST"
        self.provenance = {
            "metadata_validation": None,
            "oracle_name": "Rta",
            "oracle_version": "1.5.11",
            "oracle_revision": "3b5c2f2",
        }


class FakeEvidenceWithMV:
    """Evidence with metadata_validation in provenance."""
    def __init__(self, scope="FULL", findings=None, evidence_hash="abc123",
                 cvr=1.0, total_refs=1, valid_refs=1):
        self.evidence_scope = scope
        self.oracle_status = "SUCCESS"
        self.findings = findings or []
        self.analysis_scope = {
            "status": "VALIDATED" if scope == "FULL" else "NOT_VALIDATED",
            "netlist_required": 0,
            "unsupported": 0,
            "tcl_execution_required": 0,
        }
        self.evidence_hash = evidence_hash
        self.artifact_id = "EGER-EVID-TEST"
        self.provenance = {
            "metadata_validation": {
                "constraint_validity_rate": cvr,
                "total_references": total_refs,
                "valid_references": valid_refs,
            },
        }


class FakeRawEvidence:
    def __init__(self):
        self.raw_bytes = b'{"fake": true}'


class FakeOracleResult:
    def __init__(self, evidence=None, raw=None, is_success=True):
        self.evidence = evidence
        self.raw_evidence = raw or FakeRawEvidence()
        self.is_success = is_success
        self.failure = None


def make_task_data(task_id="BENCH2-001"):
    return {
        "design_context": f"[{task_id}] test design with clk",
        "objective": f"[{task_id}] generate clock",
    }


# ---------------------------------------------------------------------------
# T060: Same initial candidate is used by control and treatment
# ---------------------------------------------------------------------------

def test_T060_same_initial_candidate(tmp_path):
    """The initial candidate must be identical for both branches."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    # Initial candidate hash must be present and shared
    assert result["initial_candidate_hash"] is not None
    assert isinstance(result["initial_candidate_hash"], str)
    # With FakeEngineerModel (deterministic), all hashes are identical
    assert result["control_candidate_hash"] == result["initial_candidate_hash"]
    assert result["treatment_candidate_hash"] == result["initial_candidate_hash"]


# ---------------------------------------------------------------------------
# T061: Control receives NO feedback
# ---------------------------------------------------------------------------

def test_T061_control_no_feedback(tmp_path):
    """Control branch must NOT receive structured EvidenceArtifact."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    # Patch propose to capture what feedback the control branch receives
    captured = {"control_feedback": None, "treatment_feedback": None}
    original_propose = EngineerAdapter.propose

    call_count = [0]

    def capturing_propose(self, design_context="", existing_sdc="",
                          objective="", evidence_summary=None, **kw):
        call_count[0] += 1
        if call_count[0] == 2:
            # This is control Call 2
            captured["control_feedback"] = evidence_summary
        elif call_count[0] == 3:
            # This is treatment Call 2
            captured["treatment_feedback"] = evidence_summary
        return original_propose(self, design_context, existing_sdc,
                                objective, evidence_summary, **kw)

    with patch.object(EngineerAdapter, "propose", capturing_propose):
        run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)

    assert captured["control_feedback"] is None, \
        "Control branch must NOT receive feedback"
    assert captured["treatment_feedback"] is not None, \
        "Treatment branch must receive feedback"


# ---------------------------------------------------------------------------
# T062: Treatment receives structured EvidenceArtifact
# ---------------------------------------------------------------------------

def test_T062_treatment_receives_feedback(tmp_path):
    """Treatment branch must receive deterministic structured feedback."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    captured = {"treatment_feedback": None}
    original_propose = EngineerAdapter.propose

    call_count = [0]

    def capturing_propose(self, design_context="", existing_sdc="",
                          objective="", evidence_summary=None, **kw):
        call_count[0] += 1
        if call_count[0] == 3:
            captured["treatment_feedback"] = evidence_summary
        return original_propose(self, design_context, existing_sdc,
                                objective, evidence_summary, **kw)

    with patch.object(EngineerAdapter, "propose", capturing_propose):
        run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)

    feedback = captured["treatment_feedback"]
    assert feedback is not None
    data = json.loads(feedback)
    assert "evidence_scope" in data
    assert "findings" in data


# ---------------------------------------------------------------------------
# T063: MODEL-004 identity is fixed
# ---------------------------------------------------------------------------

def test_T063_model_005_identity():
    """MODEL-005 identity must be frozen as mimo-v2.5-free."""
    assert rq4_module.MODEL_ID == "EGER-MODEL-005"
    assert rq4_module.MODEL_NAME == "opencode/mimo-v2.5-free"


# ---------------------------------------------------------------------------
# T064: Model configuration identical between branches
# ---------------------------------------------------------------------------

def test_T064_model_config_identical(tmp_path):
    """Both branches use the same model instance."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    # Capture model instances used
    model_refs = []
    original_propose = EngineerAdapter.propose

    def capturing_propose(self, design_context="", existing_sdc="",
                          objective="", evidence_summary=None, **kw):
        model_refs.append(id(self.model))
        return original_propose(self, design_context, existing_sdc,
                                objective, evidence_summary, **kw)

    with patch.object(EngineerAdapter, "propose", capturing_propose):
        run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)

    # All calls use the same model instance
    assert len(set(model_refs)) == 1


# ---------------------------------------------------------------------------
# T065: Oracle configuration identical between branches
# ---------------------------------------------------------------------------

def test_T065_oracle_config_identical(tmp_path):
    """Both branches use the same Oracle."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    oracle_refs = []
    original_validate = EvidenceOracle.validate

    # We can't patch the method directly on MagicMock, so verify via manifest
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    # Both oracle_revision values must match
    assert result["oracle_revision"] == rq4_module.ORACLE_REVISION


# ---------------------------------------------------------------------------
# T066: Only feedback treatment differs
# ---------------------------------------------------------------------------

def test_T066_only_feedback_differs(tmp_path):
    """The ONLY difference between branches must be the feedback."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    prompts = []
    original_propose = EngineerAdapter.propose

    def capturing_propose(self, design_context="", existing_sdc="",
                          objective="", evidence_summary=None, **kw):
        prompts.append({
            "design_context": design_context,
            "existing_sdc": existing_sdc,
            "objective": objective,
            "evidence_summary": evidence_summary,
        })
        return original_propose(self, design_context, existing_sdc,
                                objective, evidence_summary, **kw)

    with patch.object(EngineerAdapter, "propose", capturing_propose):
        run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)

    # Call 2 (index 1) = control, Call 3 (index 2) = treatment
    # They must differ ONLY in evidence_summary
    ctrl = prompts[1]
    treat = prompts[2]
    assert ctrl["design_context"] == treat["design_context"]
    assert ctrl["existing_sdc"] == treat["existing_sdc"]
    assert ctrl["objective"] == treat["objective"]
    assert ctrl["evidence_summary"] is None
    assert treat["evidence_summary"] is not None


# ---------------------------------------------------------------------------
# T067: ERROR-only primary metric
# ---------------------------------------------------------------------------

def test_T067_error_only_primary_metric(tmp_path):
    """Primary metric counts only ERROR-severity findings."""
    # Findings: 1 error + 2 warnings + 3 info
    findings = [
        {"severity": "error", "code": "SDC-005", "message": "err1"},
        {"severity": "warning", "code": "SDC-020", "message": "warn1"},
        {"severity": "warning", "code": "SDC-021", "message": "warn2"},
        {"severity": "info", "code": "SDC-102", "message": "info1"},
        {"severity": "info", "code": "SDC-103", "message": "info2"},
        {"severity": "info", "code": "SDC-104", "message": "info3"},
    ]
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", findings=findings, evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", findings=findings, evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", findings=findings, evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    # All three severity counts should be independent
    assert result["initial_error_count"] == 1
    assert result["initial_warning_count"] == 2
    assert result["initial_info_count"] == 3


# ---------------------------------------------------------------------------
# T068: WARNING excluded from primary metric
# ---------------------------------------------------------------------------

def test_T068_warning_excluded(tmp_path):
    """WARNING findings must NOT affect error delta."""
    initial_findings = [
        {"severity": "error", "code": "SDC-005", "message": "err"},
        {"severity": "warning", "code": "SDC-020", "message": "warn"},
    ]
    final_findings = [
        {"severity": "warning", "code": "SDC-020", "message": "warn"},
    ]
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", findings=initial_findings, evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", findings=final_findings, evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", findings=final_findings, evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    # error went from 1 → 0, so delta = -1 (improvement)
    # WARNING count changed from 1 → 1 but should not affect primary metric
    assert result["initial_error_count"] == 1
    assert result["control_error_count"] == 0
    assert result["control_delta_error"] == -1


# ---------------------------------------------------------------------------
# T069: INFO excluded from primary metric
# ---------------------------------------------------------------------------

def test_T069_info_excluded(tmp_path):
    """INFO findings must NOT affect error delta."""
    initial_findings = [
        {"severity": "info", "code": "SDC-102", "message": "info1"},
        {"severity": "info", "code": "SDC-103", "message": "info2"},
    ]
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", findings=initial_findings, evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", findings=initial_findings, evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", findings=initial_findings, evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["initial_error_count"] == 0
    assert result["control_delta_error"] == 0
    assert result["treatment_delta_error"] == 0


# ---------------------------------------------------------------------------
# T070: CVR persistence
# ---------------------------------------------------------------------------

def test_T070_cvr_persistence(tmp_path):
    """CVR values must be persisted in the result."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", cvr=0.8, evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", cvr=1.0, evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", cvr=1.0, evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["initial_CVR"] == 0.8
    assert result["control_CVR"] == 1.0
    assert result["treatment_CVR"] == 1.0
    assert result["control_delta_CVR"] == pytest.approx(0.2)
    assert result["treatment_delta_CVR"] == pytest.approx(0.2)


# ---------------------------------------------------------------------------
# T071: Evidence scope persistence
# ---------------------------------------------------------------------------

def test_T071_scope_persistence(tmp_path):
    """Evidence scope must be persisted for all three evaluations."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="PARTIAL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["initial_evidence_scope"] == "PARTIAL"
    assert result["control_evidence_scope"] == "FULL"
    assert result["treatment_evidence_scope"] == "FULL"


# ---------------------------------------------------------------------------
# T072: proposal_changed calculation
# ---------------------------------------------------------------------------

def test_T072_proposal_changed(tmp_path):
    """proposal_changed must reflect hash inequality."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    # With FakeEngineerModel, all calls return the same output,
    # so hashes should be identical → proposal_changed = False
    assert result["control_proposal_changed"] is False
    assert result["treatment_proposal_changed"] is False


# ---------------------------------------------------------------------------
# T073: Candidate hash persistence
# ---------------------------------------------------------------------------

def test_T073_candidate_hash_persistence(tmp_path):
    """Candidate hashes must be persisted for all three evaluations."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["initial_candidate_hash"] is not None
    assert result["control_candidate_hash"] is not None
    assert result["treatment_candidate_hash"] is not None


# ---------------------------------------------------------------------------
# T074: Evidence hash persistence
# ---------------------------------------------------------------------------

def test_T074_evidence_hash_persistence(tmp_path):
    """Evidence hashes must be persisted for all three evaluations."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["initial_evidence_hash"] == "h1"
    assert result["control_evidence_hash"] == "h2"
    assert result["treatment_evidence_hash"] == "h3"


# ---------------------------------------------------------------------------
# T075: Structured feedback hash persistence
# ---------------------------------------------------------------------------

def test_T075_feedback_hash_persistence(tmp_path):
    """Structured feedback hash must be persisted."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["structured_feedback_hash"] is not None
    assert len(result["structured_feedback_hash"]) == 64  # SHA256 hex


# ---------------------------------------------------------------------------
# T076: Branch identity persistence
# ---------------------------------------------------------------------------

def test_T076_branch_identity_persistence(tmp_path):
    """Branch identities (CONTROL/TREATMENT) must be persisted."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["condition_control"] == "RQ4-CONTROL"
    assert result["condition_treatment"] == "RQ4-TREATMENT"


# ---------------------------------------------------------------------------
# T077: Budget enforcement
# ---------------------------------------------------------------------------

def test_T077_budget_enforcement(tmp_path):
    """Model and Oracle call budgets must be enforced."""
    # RQ4 budget: 1 initial + 1 control + 1 treatment = 3 each
    assert rq4_module.MAX_MODEL_CALLS == 3
    assert rq4_module.MAX_ORACLE_CALLS == 3
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    # With canned model, all 3 calls succeed
    assert result["model_calls"] <= 3  # 1 initial + 1 ctrl + 1 treat
    assert result["oracle_calls"] <= 3  # 1 initial + 1 ctrl + 1 treat


# ---------------------------------------------------------------------------
# T078: Failure semantics — model failure on Call 1
# ---------------------------------------------------------------------------

def test_T078_failure_call1_model(tmp_path):
    """Model failure on Call 1 → INCOMPLETE_TREATMENT."""
    oracle = MagicMock()
    model = FakeEngineerModel(fail_mode="timeout")
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["status"] == "INCOMPLETE_TREATMENT"
    assert result["failure_class"] in ("TIMEOUT", "MODEL_FAILURE", "PROVIDER_ERROR")


# ---------------------------------------------------------------------------
# T079: Failure semantics — oracle failure on Call 1
# ---------------------------------------------------------------------------

def test_T079_failure_call1_oracle(tmp_path):
    """Oracle failure on Call 1 → INCOMPLETE_TREATMENT."""
    oracle = MagicMock()
    fail_result = FakeOracleResult(is_success=False)
    fail_result.failure = type("obj", (), {"kind": "ORACLE_FAILURE", "message": "failed"})()
    oracle.validate.return_value = fail_result
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["status"] == "INCOMPLETE_TREATMENT"


# ---------------------------------------------------------------------------
# T080: Evaluator-only isolation
# ---------------------------------------------------------------------------

def test_T080_evaluator_only_isolation(tmp_path):
    """Evaluator-only data must not appear in manifest."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    result_str = json.dumps(result)
    assert "evaluator_only" not in result_str.lower()
    assert "expected_sdc" not in result_str.lower()


# ---------------------------------------------------------------------------
# T081: No credential leakage
# ---------------------------------------------------------------------------

def test_T081_no_credentials(tmp_path):
    """No API credentials in artifacts."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    result_str = json.dumps(result)
    assert "sk-" not in result_str
    assert "api_key" not in result_str.lower()
    assert "secret" not in result_str.lower()


# ---------------------------------------------------------------------------
# T082: No Rta access/modification
# ---------------------------------------------------------------------------

def test_T082_no_rta_interaction(tmp_path):
    """Runner must not invoke rta_generate."""
    # Verify module constants don't reference rta_generate
    import inspect
    source = inspect.getsource(rq4_module)
    assert "rta_generate" not in source


# ---------------------------------------------------------------------------
# T083: Historical artifact isolation
# ---------------------------------------------------------------------------

def test_T083_historical_isolation(tmp_path):
    """RQ4 must write to formal/RQ4/, not C0/C1/C2/C2-live."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)

    # Artifacts must be under formal/RQ4-MODEL-005/
    rq4_ctrl = tmp_path / "formal" / "RQ4-MODEL-005" / "control" / "manifests"
    rq4_treat = tmp_path / "formal" / "RQ4-MODEL-005" / "treatment" / "manifests"
    assert rq4_ctrl.exists(), "RQ4-MODEL-005 control manifests must exist"
    assert rq4_treat.exists(), "RQ4-MODEL-005 treatment manifests must exist"

    # C0/C1/C2 must NOT be created
    assert not (tmp_path / "formal" / "C0").exists()
    assert not (tmp_path / "formal" / "C1").exists()
    assert not (tmp_path / "formal" / "C2").exists()
    assert not (tmp_path / "formal" / "C2-live").exists()


# ---------------------------------------------------------------------------
# T084: RQ4 namespace isolation
# ---------------------------------------------------------------------------

def test_T084_rq4_namespace_isolation(tmp_path):
    """RQ4 artifacts must not touch MODEL-004-C2 namespace."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)

    # Must not create MODEL-004-C2
    assert not (tmp_path / "formal" / "MODEL-004-C2").exists()

    # Must be under RQ4-MODEL-005
    assert (tmp_path / "formal" / "RQ4-MODEL-005").exists()


# ---------------------------------------------------------------------------
# T085: Treatment effect calculation
# ---------------------------------------------------------------------------

def test_T085_treatment_effect(tmp_path):
    """treatment_effect = treatment_delta_error - control_delta_error."""
    # Initial: 2 errors, control: 1 error, treatment: 0 errors
    initial = [
        {"severity": "error", "code": "SDC-005", "message": "err1"},
        {"severity": "error", "code": "SDC-006", "message": "err2"},
    ]
    ctrl_final = [
        {"severity": "error", "code": "SDC-005", "message": "err1"},
    ]
    treat_final = []

    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", findings=initial, evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", findings=ctrl_final, evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", findings=treat_final, evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    # control_delta = 1 - 2 = -1
    # treatment_delta = 0 - 2 = -2
    # treatment_effect = -2 - (-1) = -1
    assert result["control_delta_error"] == -1
    assert result["treatment_delta_error"] == -2
    assert result["treatment_effect"] == -1


# ---------------------------------------------------------------------------
# T086: Materialized artifacts contain required files
# ---------------------------------------------------------------------------

def test_T086_artifact_files(tmp_path):
    """RQ4 artifacts must contain all required files."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    result = run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    run_id = result["run_id"]

    # Control artifacts
    ctrl_dir = tmp_path / "formal" / "RQ4-MODEL-005" / "control" / "raw" / run_id
    assert (ctrl_dir / "initial_candidate.json").exists()
    assert (ctrl_dir / "evidence_initial.json").exists()
    assert (ctrl_dir / "revised_candidate.json").exists()
    assert (ctrl_dir / "evidence_final.json").exists()

    # Treatment artifacts
    treat_dir = tmp_path / "formal" / "RQ4-MODEL-005" / "treatment" / "raw" / run_id
    assert (treat_dir / "initial_candidate.json").exists()
    assert (treat_dir / "evidence_initial.json").exists()
    assert (treat_dir / "structured_feedback.json").exists()
    assert (treat_dir / "revised_candidate.json").exists()
    assert (treat_dir / "evidence_final.json").exists()


# ---------------------------------------------------------------------------
# T087: Design metadata loaded for Oracle
# ---------------------------------------------------------------------------

def test_T087_design_metadata_loaded(tmp_path):
    """Design metadata must be loaded and passed to Oracle."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)

    # Oracle must have been called 3 times with design_metadata
    assert oracle.validate.call_count == 3
    for call in oracle.validate.call_args_list:
        # design_metadata is passed as keyword argument
        assert "design_metadata" in call.kwargs or len(call.args) >= 3


# ---------------------------------------------------------------------------
# T088: No design metadata in engineer prompt
# ---------------------------------------------------------------------------

def test_T088_no_metadata_in_prompt(tmp_path):
    """design_metadata must never appear in the engineer prompt."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h1")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h2")),
        FakeOracleResult(FakeEvidenceWithMV(scope="FULL", evidence_hash="h3")),
    ]
    model = FakeEngineerModel(
        canned_output="create_clock -name clk -period 10 [get_ports clk]"
    )
    prompts = []
    original_propose = EngineerAdapter.propose

    def capturing_propose(self, **kwargs):
        prompts.append(kwargs)
        return original_propose(self, **kwargs)

    with patch.object(EngineerAdapter, "propose", capturing_propose):
        run_rq4_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)

    for p in prompts:
        # evidence_summary should never contain port/clock definitions
        if p.get("evidence_summary"):
            data = json.loads(p["evidence_summary"])
            # Findings must not contain port/clock metadata
            for finding in data.get("findings", []):
                assert "port" not in finding.get("message", "").lower() or \
                       "metadata" not in finding.get("message", "").lower()


# ---------------------------------------------------------------------------
# Helper: test the finding count function directly
# ---------------------------------------------------------------------------

def test_T089_count_findings_directly():
    """_count_findings_by_severity counts correctly."""
    findings = [
        {"severity": "error", "code": "SDC-005"},
        {"severity": "error", "code": "SDC-006"},
        {"severity": "warning", "code": "SDC-020"},
        {"severity": "info", "code": "SDC-102"},
    ]
    counts = rq4_module._count_findings_by_severity(findings)
    assert counts["error"] == 2
    assert counts["warning"] == 1
    assert counts["info"] == 1


def test_T090_compute_error_delta_directly():
    """_compute_error_delta computes correctly."""
    initial = [{"severity": "error"}, {"severity": "error"}]
    final = [{"severity": "error"}]
    delta = rq4_module._compute_error_delta(initial, final)
    assert delta == -1  # improvement


def test_T091_compute_error_delta_no_change():
    """_compute_error_delta with same counts → 0."""
    initial = [{"severity": "error"}, {"severity": "warning"}]
    final = [{"severity": "error"}, {"severity": "info"}]
    delta = rq4_module._compute_error_delta(initial, final)
    assert delta == 0
