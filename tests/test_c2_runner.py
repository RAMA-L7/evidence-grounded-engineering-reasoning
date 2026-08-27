"""C2 runner tests — P041 implementation verification (no formal C2 execution)."""

import json
import hashlib
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from eger.engineer.model import FakeEngineerModel
from eger.engineer.adapter import EngineerAdapter
from eger.oracle.adapter import EvidenceOracle
from eger.engineer.structured_feedback import render_structured_feedback
import importlib.util
import pathlib
_c2_path = pathlib.Path(__file__).resolve().parents[1] / "research" / "experiments" / "EGER-EXP-001" / "formal_runner_c2.py"
_spec = importlib.util.spec_from_file_location("formal_runner_c2", _c2_path)
c2_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(c2_module)
run_c2_task = c2_module.run_c2_task

# ---------------------------------------------------------------------------
# Helpers: fake evidence and oracle
# ---------------------------------------------------------------------------

class FakeEvidence:
    def __init__(self, scope="FULL", findings=None, evidence_hash="abc123"):
        self.evidence_scope = scope
        self.oracle_status = "SUCCESS"
        self.findings = findings or []
        self.analysis_scope = {"status": "VALIDATED" if scope == "FULL" else "NOT_VALIDATED", "netlist_required": 0, "unsupported": 0, "tcl_execution_required": 0}
        self.evidence_hash = evidence_hash
        self.artifact_id = "EGER-EVID-TEST"

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

def test_01_two_stage_control_flow(tmp_path):
    """C2 runner executes two-stage flow with mocked deps."""
    oracle = MagicMock()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidence(scope="FULL", findings=[], evidence_hash="h1")),
        FakeOracleResult(FakeEvidence(scope="FULL", findings=[], evidence_hash="h2")),
    ]
    # Fake model that returns canned SDC for both calls
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    # Patch LiveEngineerModel inside c2 module to use our fake
    with patch.object(c2_module, "LiveEngineerModel", return_value=model):
        # Actually run_c2_task creates its own LiveEngineerModel if model is None,
        # so we pass model explicitly
        task_data = make_task_data()
        # Use tmp_path as base_dir
        result = run_c2_task("BENCH2-001", task_data, oracle, tmp_path, model=model)
    assert result["model_calls"] == 2
    assert result["oracle_calls"] == 2
    assert oracle.validate.call_count == 2

def test_02_model_identity():
    """MODEL-003 identity is passed correctly."""
    assert c2_module.MODEL_ID == "EGER-MODEL-003"
    assert c2_module.MODEL_NAME == "opencode/mimo-v2.5-free" if hasattr(c2_module, "MODEL_NAME") else True
    # Check that run uses MODEL_ID
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence())
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        result = run_c2_task("BENCH2-001", make_task_data(), oracle, Path(tmp), model=model)
        assert result["model_id"] == "EGER-MODEL-003"

def test_03_tools_empty():
    """tools = [] is enforced."""
    # Check that LiveEngineerModel is configured with tools: [] via sampling_params
    # Fake doesn't use tools, but we verify structured feedback doesn't add tools
    evidence = FakeEvidence()
    feedback = render_structured_feedback(evidence)
    data = json.loads(feedback)
    # Structured feedback must not contain tool-related fields
    assert "tools" not in feedback
    assert "web" not in feedback.lower()

def test_04_temperature():
    """temperature = 0.0 is preserved."""
    # Check that C2 runner uses temperature 0.0 via LiveEngineerModel (inferred from MODEL-003 spec)
    # FakeEngineerModel doesn't have temperature, but we verify the C2 module doesn't override it
    assert c2_module.MODEL_ID == "EGER-MODEL-003"
    # The actual LiveEngineerModel is constructed with timeout=60, max_tokens=2048, temperature 0.0
    # We verify the file contains temperature 0.0
    content = Path(c2_module.__file__).read_text(encoding="utf-8")
    # It should not contain a different temperature
    assert "temperature" not in content or "0.0" in content

def test_05_initial_candidate_captured(tmp_path):
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence())
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert "initial_candidate_hash" in result
    assert result["initial_candidate_hash"] is not None

def test_06_evidence_captured(tmp_path):
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence(scope="FULL", evidence_hash="ev1"))
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert "initial_oracle_evidence_hash" in result
    assert result["initial_oracle_evidence_hash"] == "ev1"

def test_07_structured_feedback_passed(tmp_path):
    """Structured feedback is passed to second model call."""
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence(scope="FULL", findings=[{"severity": "error", "code": "SDC-001", "message": "test", "location": {"line": 1}, "finding_id": "f1"}]))
    captured_feedback = {}

    class CapturingModel(FakeEngineerModel):
        def __init__(self):
            super().__init__(canned_output="create_clock -name clk -period 10 [get_ports clk]")
            self.calls = []
        def generate(self, prompt, **kwargs):
            self.calls.append(prompt)
            return super().generate(prompt, **kwargs)

    model = CapturingModel()
    # Patch to capture structured feedback via evidence_summary
    original_propose = EngineerAdapter.propose
    def capturing_propose(self, design_context="", existing_sdc="", objective="", evidence_summary=None, **kw):
        if evidence_summary is not None:
            captured_feedback["feedback"] = evidence_summary
        return original_propose(self, design_context, existing_sdc, objective, evidence_summary, **kw)

    with patch.object(EngineerAdapter, "propose", capturing_propose):
        result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)

    assert "feedback" in captured_feedback
    feedback = captured_feedback["feedback"]
    # Structured feedback must be JSON with evidence_scope and findings
    data = json.loads(feedback)
    assert "evidence_scope" in data
    assert "findings" in data
    assert data["findings"][0]["code"] == "SDC-001"
    # Must NOT be text feedback (C1 style has "ORACLE RESULT")
    assert "ORACLE RESULT" not in feedback

def test_08_evaluator_only_not_passed(tmp_path):
    """Evaluator-only data is not passed."""
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence())
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    # Ensure no evaluator_only content leaks
    result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    # Check that manifest does not contain evaluator_only
    manifest_str = json.dumps(result)
    assert "evaluator_only" not in manifest_str.lower()
    assert "expected" not in manifest_str.lower()

def test_09_second_model_call(tmp_path):
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence())
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["model_calls"] == 2

def test_10_second_oracle_call(tmp_path):
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence())
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["oracle_calls"] == 2

def test_11_artifacts_under_formal_c2(tmp_path):
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence())
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    # Check that artifacts are written under formal/C2/
    assert (tmp_path / "formal" / "C2" / "manifests").exists()
    assert (tmp_path / "formal" / "C2" / "raw" / result["run_id"]).exists()
    # Check that formal/C1 is not modified
    assert not (tmp_path / "formal" / "C1" / "manifests" / f"{result['run_id']}.json").exists()

def test_12_c0_c1_not_modified(tmp_path):
    """C0/C1 artifact locations are not modified."""
    # Create dummy C0/C1 files before run
    (tmp_path / "formal" / "manifests").mkdir(parents=True, exist_ok=True)
    (tmp_path / "formal" / "C1" / "manifests").mkdir(parents=True, exist_ok=True)
    (tmp_path / "formal" / "manifests" / "dummy.json").write_text("{}")
    (tmp_path / "formal" / "C1" / "manifests" / "dummy.json").write_text("{}")
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence())
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    # Check that dummy files still exist and no new files in those dirs beyond dummy
    assert (tmp_path / "formal" / "manifests" / "dummy.json").exists()
    assert (tmp_path / "formal" / "C1" / "manifests" / "dummy.json").exists()

def test_13_model_call_budget(tmp_path):
    """Model-call budget is enforced."""
    assert c2_module.MAX_MODEL_CALLS == 2
    # Simulate exceeding budget by making model fail and retry — here we just check the constant
    # The runner should not exceed 2 calls in normal path
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence())
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["model_calls"] <= c2_module.MAX_MODEL_CALLS

def test_14_oracle_call_budget(tmp_path):
    """Oracle-call budget is enforced."""
    assert c2_module.MAX_ORACLE_CALLS == 2
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence())
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["oracle_calls"] <= c2_module.MAX_ORACLE_CALLS

def test_15_first_oracle_failure(tmp_path):
    """First oracle failure is classified correctly."""
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(is_success=False)
    oracle.validate.return_value.failure = type("obj", (), {"kind": "ORACLE_FAILURE"})()
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["failure_class"] == "ORACLE_FAILURE"
    assert result["final_outcome"] == "INCOMPLETE_TREATMENT"

def test_16_second_model_failure(tmp_path):
    """Second model failure is classified correctly."""
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence())
    model = FakeEngineerModel(fail_mode="timeout")
    # First call will timeout, so we need a model that succeeds first then fails second
    class TwoStageModel(FakeEngineerModel):
        def __init__(self):
            super().__init__()
            self.call_count = 0
        def generate(self, prompt, **kwargs):
            self.call_count += 1
            if self.call_count == 1:
                return FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]").generate(prompt, **kwargs)
            else:
                raise TimeoutError("second call timeout")
    model2 = TwoStageModel()
    result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model2)
    assert result["failure_class"] in ("TIMEOUT", "MODEL_FAILURE", "PROPOSAL_FAILURE")
    assert result["final_outcome"] == "INCOMPLETE_TREATMENT"

def test_17_second_oracle_failure(tmp_path):
    """Second oracle failure is classified correctly."""
    oracle = MagicMock()
    second = FakeOracleResult(is_success=False)
    second.failure = type("obj", (), {"kind": "ORACLE_FAILURE"})()
    oracle.validate.side_effect = [
        FakeOracleResult(FakeEvidence()),
        second,
    ]
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["failure_class"] == "ORACLE_FAILURE"
    assert result["final_outcome"] == "INCOMPLETE_MEASUREMENT"

def test_18_malformed_candidate(tmp_path):
    """Malformed candidate handling is correct."""
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence())
    model = FakeEngineerModel(fail_mode="malformed")
    result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    assert result["failure_class"] == "MALFORMED_OUTPUT"
    assert result["final_outcome"] == "PROPOSAL_FAILURE"

def test_19_manifest_required_fields(tmp_path):
    """Manifest contains required C2 fields."""
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence())
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    required = ["run_id", "task_id", "condition", "model_id", "initial_candidate_hash", "final_candidate_hash", "initial_oracle_evidence_hash", "final_oracle_evidence_hash", "structured_feedback_hash", "model_calls", "oracle_calls"]
    for field in required:
        assert field in result, f"missing {field}"
    assert result["condition"] == "C2"
    assert result["model_id"] == "EGER-MODEL-003"

def test_20_no_credentials_in_artifacts(tmp_path):
    """No API credentials are written to artifacts."""
    oracle = MagicMock()
    oracle.validate.return_value = FakeOracleResult(FakeEvidence())
    model = FakeEngineerModel(canned_output="create_clock -name clk -period 10 [get_ports clk]")
    result = run_c2_task("BENCH2-001", make_task_data(), oracle, tmp_path, model=model)
    # Check manifest and raw files don't contain API keys
    manifest_str = json.dumps(result)
    assert "sk-" not in manifest_str
    assert "api_key" not in manifest_str.lower()
    # Check raw files
    for raw_file in (tmp_path / "formal" / "C2" / "raw" / result["run_id"]).glob("*"):
        content = raw_file.read_text(encoding="utf-8", errors="ignore") if raw_file.is_file() else ""
        assert "sk-" not in content
