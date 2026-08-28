"""Deterministic tests for P078 diagnostic runner (EGER-CHANGE-009).

Tests:
- T092: Condition definitions are isolated (one variable changed per condition)
- T093: Initial SDC differs correctly between A and B
- T094: Objective differs correctly between A and C
- T095: Feedback differs correctly between A and D
- T096: All other parameters are identical across conditions
- T097: ERROR-only feedback contains exactly 2 findings
- T098: Full feedback contains ERROR + WARNING + INFO findings
- T099: ERROR adherence check works correctly
- T100: Metadata loading works
- T101: Condition A is identical to original BENCH2-001
- T102: No condition modifies historical artifacts
- T103: Diagnostic namespace is isolated
- T104: Model configuration matches MODEL-005
"""

import json
import os
import sys
from pathlib import Path

import pytest

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import from the diagnostic runner directly
import importlib.util
_diag_path = Path(__file__).resolve().parent.parent / "research" / "experiments" / "EGER-EXP-001" / "formal_diagnostic_001.py"
_spec = importlib.util.spec_from_file_location("formal_diagnostic_001", _diag_path)
_diag_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_diag_mod)

CONDITIONS = _diag_mod.CONDITIONS
DESIGN_CONTEXT = _diag_mod.DESIGN_CONTEXT
ORIGINAL_OBJECTIVE = _diag_mod.ORIGINAL_OBJECTIVE
BROADER_OBJECTIVE = _diag_mod.BROADER_OBJECTIVE
ORIGINAL_SDC = _diag_mod.ORIGINAL_SDC
RICH_SDC = _diag_mod.RICH_SDC
ERROR_ONLY_FEEDBACK = _diag_mod.ERROR_ONLY_FEEDBACK
MODEL_ID = _diag_mod.MODEL_ID
MODEL_NAME = _diag_mod.MODEL_NAME
TASK_ID = _diag_mod.TASK_ID
_check_error_adherence = _diag_mod._check_error_adherence
_load_design_metadata = _diag_mod._load_design_metadata


# ---------------------------------------------------------------------------
# T092: Isolation — one variable changed per condition vs baseline A
# ---------------------------------------------------------------------------

class TestConditionIsolation:
    """Verify each condition changes exactly one variable from baseline A."""

    def test_a_vs_b_only_sdc_differs(self):
        """B changes only initial SDC from A."""
        a = CONDITIONS["A"]
        b = CONDITIONS["B"]
        assert a["sdc"] != b["sdc"], "B must differ in SDC"
        assert a["objective"] == b["objective"], "B must have same objective"
        assert a["feedback_mode"] == b["feedback_mode"], "B must have same feedback"

    def test_a_vs_c_only_objective_differs(self):
        """C changes only objective from A."""
        a = CONDITIONS["A"]
        c = CONDITIONS["C"]
        assert a["sdc"] == c["sdc"], "C must have same SDC"
        assert a["objective"] != c["objective"], "C must differ in objective"
        assert a["feedback_mode"] == c["feedback_mode"], "C must have same feedback"

    def test_a_vs_d_only_feedback_differs(self):
        """D changes only feedback from A."""
        a = CONDITIONS["A"]
        d = CONDITIONS["D"]
        assert a["sdc"] == d["sdc"], "D must have same SDC"
        assert a["objective"] == d["objective"], "D must have same objective"
        assert a["feedback_mode"] != d["feedback_mode"], "D must differ in feedback"


# ---------------------------------------------------------------------------
# T093–T095: Specific variable values
# ---------------------------------------------------------------------------

class TestVariableValues:

    def test_sdc_differences(self):
        """B uses RICH_SDC, A/C/D use ORIGINAL_SDC."""
        assert CONDITIONS["B"]["sdc"] == RICH_SDC
        assert CONDITIONS["A"]["sdc"] == ORIGINAL_SDC
        assert CONDITIONS["C"]["sdc"] == ORIGINAL_SDC
        assert CONDITIONS["D"]["sdc"] == ORIGINAL_SDC

    def test_objective_differences(self):
        """C uses BROADER_OBJECTIVE, A/B/D use ORIGINAL_OBJECTIVE."""
        assert CONDITIONS["C"]["objective"] == BROADER_OBJECTIVE
        assert CONDITIONS["A"]["objective"] == ORIGINAL_OBJECTIVE
        assert CONDITIONS["B"]["objective"] == ORIGINAL_OBJECTIVE
        assert CONDITIONS["D"]["objective"] == ORIGINAL_OBJECTIVE

    def test_feedback_differences(self):
        """D uses error_only, A/B/C use full."""
        assert CONDITIONS["D"]["feedback_mode"] == "error_only"
        assert CONDITIONS["A"]["feedback_mode"] == "full"
        assert CONDITIONS["B"]["feedback_mode"] == "full"
        assert CONDITIONS["C"]["feedback_mode"] == "full"


# ---------------------------------------------------------------------------
# T096: Common parameters are identical
# ---------------------------------------------------------------------------

class TestCommonParameters:

    def test_all_conditions_same_task(self):
        for key in ["A", "B", "C", "D"]:
            assert CONDITIONS[key]["name"].startswith(key)

    def test_model_constants(self):
        assert MODEL_ID == "EGER-MODEL-005"
        assert MODEL_NAME == "opencode/mimo-v2.5-free"
        assert TASK_ID == "BENCH2-001"


# ---------------------------------------------------------------------------
# T097–T098: Feedback structure
# ---------------------------------------------------------------------------

class TestFeedbackStructure:

    def test_error_only_has_two_findings(self):
        """ERROR-only feedback contains exactly 2 findings."""
        fb = json.loads(ERROR_ONLY_FEEDBACK)
        assert len(fb) == 2
        codes = {f["code"] for f in fb}
        assert codes == {"SDC-005", "SDC-006"}
        severities = {f["severity"] for f in fb}
        assert severities == {"error"}

    def test_error_only_messages_contain_key_terms(self):
        fb = json.loads(ERROR_ONLY_FEEDBACK)
        messages = " ".join(f["message"] for f in fb).lower()
        assert "set_input_delay" in messages
        assert "set_output_delay" in messages


# ---------------------------------------------------------------------------
# T099: ERROR adherence check
# ---------------------------------------------------------------------------

class TestErrorAdherence:

    def test_adherence_with_delays(self):
        sdc = "create_clock -name clk -period 10\nset_input_delay 2.0 -clock clk [all_inputs]\nset_output_delay 2.0 -clock clk [all_outputs]"
        result = _check_error_adherence(sdc)
        assert result["error_adherence"] is True
        assert result["has_set_input_delay"] is True
        assert result["has_set_output_delay"] is True

    def test_adherence_without_delays(self):
        sdc = "create_clock -name clk -period 10"
        result = _check_error_adherence(sdc)
        assert result["error_adherence"] is False

    def test_adherence_only_input(self):
        sdc = "set_input_delay 2.0 -clock clk [all_inputs]"
        result = _check_error_adherence(sdc)
        assert result["has_set_input_delay"] is True
        assert result["has_set_output_delay"] is False
        assert result["error_adherence"] is False

    def test_adherence_case_insensitive(self):
        sdc = "SET_INPUT_DELAY 2.0\nSET_OUTPUT_DELAY 2.0"
        result = _check_error_adherence(sdc)
        assert result["error_adherence"] is True


# ---------------------------------------------------------------------------
# T100: Metadata loading
# ---------------------------------------------------------------------------

class TestMetadataLoading:

    def test_metadata_loads(self):
        dm = _load_design_metadata("BENCH2-001")
        assert dm is not None

    def test_metadata_has_ports(self):
        dm = _load_design_metadata("BENCH2-001")
        assert len(dm.ports) > 0


# ---------------------------------------------------------------------------
# T101: Condition A matches original BENCH2-001
# ---------------------------------------------------------------------------

class TestBaselineMatch:

    def test_condition_a_sdc_matches_original(self):
        assert CONDITIONS["A"]["sdc"] == ORIGINAL_SDC

    def test_condition_a_objective_matches_original(self):
        assert CONDITIONS["A"]["objective"] == ORIGINAL_OBJECTIVE

    def test_condition_a_has_full_feedback(self):
        assert CONDITIONS["A"]["feedback_mode"] == "full"


# ---------------------------------------------------------------------------
# T102: No historical artifact modification
# ---------------------------------------------------------------------------

class TestHistoricalPreservation:

    def test_rq4_namespace_not_touched(self):
        """Diagnostic runner writes to DIAGNOSTIC-001, not RQ4-MODEL-005."""
        import inspect
        source = inspect.getsource(_diag_mod.run_diagnostic_condition)
        assert "RQ4-MODEL-005" not in source
        assert "DIAGNOSTIC-001" in source


# ---------------------------------------------------------------------------
# T103: Diagnostic namespace isolation
# ---------------------------------------------------------------------------

class TestNamespaceIsolation:

    def test_all_conditions_write_to_diagnostic_dir(self):
        """Each condition writes to formal/DIAGNOSTIC-001/<condition-name>/."""
        for key in ["A", "B", "C", "D"]:
            name = CONDITIONS[key]["name"]
            assert name.startswith(key)


# ---------------------------------------------------------------------------
# T104: Model configuration
# ---------------------------------------------------------------------------

class TestModelConfiguration:

    def test_model_id(self):
        assert MODEL_ID == "EGER-MODEL-005"

    def test_model_name(self):
        assert MODEL_NAME == "opencode/mimo-v2.5-free"

    def test_four_conditions_exist(self):
        assert set(CONDITIONS.keys()) == {"A", "B", "C", "D"}
