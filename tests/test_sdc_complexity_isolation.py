"""Deterministic tests for P100 SDC complexity isolation runner.

Tests:
- T121: 4 conditions exist (W, X, Y, Z)
- T122: Condition isolation — W vs X differs only in SDC
- T123: Condition isolation — W vs Y differs only in context
- T124: Condition isolation — X vs Z differs only in context
- T125: Condition isolation — Y vs Z differs only in SDC
- T126: Minimal SDC is 51 chars
- T127: Rich SDC is 287 chars
- T128: NUM_RUNS_PER_CONDITION is 5
- T129: Total runs is 20
- T130: Budget is 61 calls
- T131: Namespace is DIAGNOSTIC-005
- T132: No historical artifact modification paths
- T133: Model configuration matches MODEL-005
- T134: Metadata task IDs are correct
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.util
_mod_path = (Path(__file__).resolve().parent.parent /
             "research" / "experiments" / "EGER-EXP-001" /
             "run_sdc_complexity_isolation.py")
_spec = importlib.util.spec_from_file_location("sdc_iso", _mod_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


class TestConditions:

    def test_four_conditions_exist(self):
        assert set(_mod.CONDITIONS.keys()) == {"W", "X", "Y", "Z"}

    def test_condition_names(self):
        assert _mod.CONDITIONS["W"]["name"] == "W-bench2-001-baseline"
        assert _mod.CONDITIONS["X"]["name"] == "X-bench2-001-rich-sdc"
        assert _mod.CONDITIONS["Y"]["name"] == "Y-bench2-002-minimal-sdc"
        assert _mod.CONDITIONS["Z"]["name"] == "Z-bench2-002-baseline"


class TestIsolation:

    def test_w_vs_x_only_sdc_differs(self):
        """W and X differ only in SDC."""
        w, x = _mod.CONDITIONS["W"], _mod.CONDITIONS["X"]
        assert w["sdc"] != x["sdc"]
        assert w["design_context"] == x["design_context"]
        assert w["objective"] == x["objective"]
        assert w["task_id_for_metadata"] == x["task_id_for_metadata"]

    def test_w_vs_y_only_context_differs(self):
        """W and Y differ only in context."""
        w, y = _mod.CONDITIONS["W"], _mod.CONDITIONS["Y"]
        assert w["sdc"] == y["sdc"]
        assert w["design_context"] != y["design_context"]
        assert w["objective"] != y["objective"]
        assert w["task_id_for_metadata"] != y["task_id_for_metadata"]

    def test_y_vs_z_only_sdc_differs(self):
        """Y and Z differ only in SDC."""
        y, z = _mod.CONDITIONS["Y"], _mod.CONDITIONS["Z"]
        assert y["sdc"] != z["sdc"]
        assert y["design_context"] == z["design_context"]
        assert y["objective"] == z["objective"]
        assert y["task_id_for_metadata"] == z["task_id_for_metadata"]

    def test_x_vs_z_only_context_differs(self):
        """X and Z differ only in context."""
        x, z = _mod.CONDITIONS["X"], _mod.CONDITIONS["Z"]
        assert x["sdc"] == z["sdc"]
        assert x["design_context"] != z["design_context"]
        assert x["objective"] != z["objective"]
        assert x["task_id_for_metadata"] != z["task_id_for_metadata"]


class TestSDC:

    def test_minimal_sdc_length(self):
        assert len(_mod.MINIMAL_SDC) == 51

    def test_rich_sdc_length(self):
        assert len(_mod.RICH_SDC) == 287

    def test_rich_sdc_has_generated_clock(self):
        assert "create_generated_clock" in _mod.RICH_SDC

    def test_rich_sdc_has_clock_groups(self):
        assert "set_clock_groups" in _mod.RICH_SDC


class TestConfiguration:

    def test_runs_per_condition(self):
        assert _mod.RUNS_PER_CONDITION == 5

    def test_total_runs(self):
        assert _mod.RUNS_PER_CONDITION * 4 == 20

    def test_budget(self):
        assert _mod.RUNS_PER_CONDITION * 4 * 3 + 1 == 61

    def test_model_name(self):
        assert _mod.MODEL_NAME == "opencode/mimo-v2.5-free"

    def test_metadata_task_ids(self):
        assert _mod.CONDITIONS["W"]["task_id_for_metadata"] == "BENCH2-001"
        assert _mod.CONDITIONS["X"]["task_id_for_metadata"] == "BENCH2-001"
        assert _mod.CONDITIONS["Y"]["task_id_for_metadata"] == "BENCH2-002"
        assert _mod.CONDITIONS["Z"]["task_id_for_metadata"] == "BENCH2-002"


class TestNamespace:

    def test_diag5_in_main(self):
        import inspect
        source = inspect.getsource(_mod.main)
        assert "DIAGNOSTIC-005" in source


class TestHistoricalPreservation:

    def test_no_rq4_paths(self):
        import inspect
        source = inspect.getsource(_mod.run_single)
        assert "RQ4-MODEL-005" not in source

    def test_no_diag3_or_diag4(self):
        import inspect
        source = inspect.getsource(_mod.main)
        assert "DIAGNOSTIC-003" not in source
        assert "DIAGNOSTIC-004" not in source
