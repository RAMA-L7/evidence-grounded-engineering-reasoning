"""Deterministic tests for P108 mechanism investigation runner.

Tests:
- T135: 4 conditions exist (Base, E2b, E3a, E4a)
- T136: Base condition isolation — no changes from baseline
- T137: E2b isolation — only SDC changed from base
- T138: E3a isolation — only objective changed from base
- T139: E4a isolation — only feedback changed from base
- T140: Base SDC is minimal 51-char
- T141: E2b SDC has added constructs
- T142: E3a objective is broader
- T143: E4a feedback is ERROR-only
- T144: RUNS_PER_CONDITION is 10
- T145: Total runs is 40
- T146: Budget is 120 calls
- T147: Namespace is DIAGNOSTIC-006
- T148: Model configuration matches MODEL-005
- T149: No historical artifact modification paths
- T150: ERROR-only feedback has exactly 2 findings
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.util
_mod_path = (Path(__file__).resolve().parent.parent /
             "research" / "experiments" / "EGER-EXP-001" /
             "run_mechanism_investigation.py")
_spec = importlib.util.spec_from_file_location("mech_inv", _mod_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


class TestConditions:

    def test_four_conditions_exist(self):
        assert set(_mod.CONDITIONS.keys()) == {"Base", "E2b", "E3a", "E4a"}

    def test_condition_names(self):
        assert _mod.CONDITIONS["Base"]["name"] == "base-bench2-001"
        assert _mod.CONDITIONS["E2b"]["name"] == "E2b-added-constructs"
        assert _mod.CONDITIONS["E3a"]["name"] == "E3a-broader-objective"
        assert _mod.CONDITIONS["E4a"]["name"] == "E4a-error-only-feedback"


class TestIsolation:

    def test_base_is_baseline(self):
        b = _mod.CONDITIONS["Base"]
        assert b["sdc"] == _mod.BASELINE_SDC
        assert b["objective"] == _mod.BASELINE_OBJECTIVE
        assert b["feedback_mode"] == "full"

    def test_e2b_only_sdc_differs(self):
        b, e = _mod.CONDITIONS["Base"], _mod.CONDITIONS["E2b"]
        assert b["sdc"] != e["sdc"]
        assert b["design_context"] == e["design_context"]
        assert b["objective"] == e["objective"]
        assert b["feedback_mode"] == e["feedback_mode"]

    def test_e3a_only_objective_differs(self):
        b, e = _mod.CONDITIONS["Base"], _mod.CONDITIONS["E3a"]
        assert b["sdc"] == e["sdc"]
        assert b["design_context"] == e["design_context"]
        assert b["objective"] != e["objective"]
        assert b["feedback_mode"] == e["feedback_mode"]

    def test_e4a_only_feedback_differs(self):
        b, e = _mod.CONDITIONS["Base"], _mod.CONDITIONS["E4a"]
        assert b["sdc"] == e["sdc"]
        assert b["design_context"] == e["design_context"]
        assert b["objective"] == e["objective"]
        assert b["feedback_mode"] != e["feedback_mode"]


class TestSDC:

    def test_base_sdc_is_minimal(self):
        assert _mod.BASELINE_SDC == "create_clock -name clk -period 10.0 [get_ports clk]"
        assert len(_mod.BASELINE_SDC) == 51

    def test_e2b_has_added_constructs(self):
        e = _mod.CONDITIONS["E2b"]["sdc"]
        assert "set_max_fanout" in e
        assert "set_max_transition" in e
        assert "set sdc_version" in e or "set_sdc_version" in e
        assert "create_clock" in e

    def test_e3a_objective_is_broader(self):
        e = _mod.CONDITIONS["E3a"]["objective"]
        assert "production-quality" in e.lower() or "complete" in e.lower()

    def test_e4a_feedback_is_error_only(self):
        assert _mod.CONDITIONS["E4a"]["feedback_mode"] == "error_only"


class TestFeedback:

    def test_error_only_has_two_findings(self):
        import json
        fb = json.loads(_mod.ERROR_ONLY_FEEDBACK)
        assert len(fb) == 2
        codes = {f["code"] for f in fb}
        assert codes == {"SDC-005", "SDC-006"}


class TestConfiguration:

    def test_runs_per_condition(self):
        assert _mod.RUNS_PER_CONDITION == 10

    def test_total_runs(self):
        assert _mod.RUNS_PER_CONDITION * 4 == 40

    def test_budget(self):
        assert _mod.RUNS_PER_CONDITION * 4 * 3 == 120

    def test_model_name(self):
        assert _mod.MODEL_NAME == "opencode/mimo-v2.5-free"

    def test_task_id(self):
        assert _mod.TASK_ID == "BENCH2-001"


class TestNamespace:

    def test_diag6_in_main(self):
        import inspect
        source = inspect.getsource(_mod.main)
        assert "DIAGNOSTIC-006" in source


class TestHistoricalPreservation:

    def test_no_rq4_paths(self):
        import inspect
        source = inspect.getsource(_mod.run_single)
        assert "RQ4-MODEL-005" not in source

    def test_no_diag3_to_diag5(self):
        import inspect
        source = inspect.getsource(_mod.main)
        assert "DIAGNOSTIC-003" not in source
        assert "DIAGNOSTIC-004" not in source
        assert "DIAGNOSTIC-005" not in source
