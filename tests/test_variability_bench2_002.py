"""Deterministic tests for P094 BENCH2-002 variability runner.

Tests:
- T113: Constants match P093 specification
- T114: Initial SDC is exactly 287 chars (frozen BENCH2-002)
- T115: NUM_RUNS is 10
- T116: Clopper-Pearson CI calculation
- T117: Namespace is DIAGNOSTIC-004
- T118: No historical artifact modification paths
- T119: Model configuration matches MODEL-005
- T120: Task ID is BENCH2-002
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.util
_mod_path = (Path(__file__).resolve().parent.parent /
             "research" / "experiments" / "EGER-EXP-001" /
             "run_variability_bench2_002.py")
_spec = importlib.util.spec_from_file_location("var_bench2", _mod_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


class TestConstants:

    def test_model_id(self):
        assert _mod.MODEL_ID == "EGER-MODEL-005"

    def test_model_name(self):
        assert _mod.MODEL_NAME == "opencode/mimo-v2.5-free"

    def test_task_id(self):
        assert _mod.TASK_ID == "BENCH2-002"

    def test_num_runs(self):
        assert _mod.NUM_RUNS == 10

    def test_oracle_revision(self):
        assert _mod.ORACLE_REVISION == "3b5c2f2"


class TestInitialSDC:

    def test_sdc_is_frozen_bench2_002(self):
        """Initial SDC must be the frozen 287-char BENCH2-002 version."""
        assert "create_generated_clock" in _mod.INITIAL_SDC
        assert "set_clock_groups" in _mod.INITIAL_SDC

    def test_sdc_length(self):
        assert len(_mod.INITIAL_SDC) == 287

    def test_sdc_no_comment(self):
        assert "#" not in _mod.INITIAL_SDC

    def test_sdc_contains_required_constructs(self):
        assert "create_clock" in _mod.INITIAL_SDC
        assert "get_ports clk" in _mod.INITIAL_SDC
        assert "clk_div2" in _mod.INITIAL_SDC


class TestClopperPearson:

    def test_zero_successes(self):
        lo, hi = _mod._clopper_pearson_ci(0, 10)
        assert lo == 0.0
        assert hi > 0.0

    def test_all_successes(self):
        lo, hi = _mod._clopper_pearson_ci(10, 10)
        assert hi == 1.0
        assert lo > 0.0

    def test_half(self):
        lo, hi = _mod._clopper_pearson_ci(5, 10)
        assert lo < 0.5 < hi

    def test_ci_contains_point_estimate(self):
        k, n = 4, 10
        lo, hi = _mod._clopper_pearson_ci(k, n)
        assert lo <= k / n <= hi


class TestNamespace:

    def test_diag4_in_main(self):
        """Runner creates DIAGNOSTIC-004 directory in main()."""
        import inspect
        source = inspect.getsource(_mod.main)
        assert "DIAGNOSTIC-004" in source


class TestHistoricalPreservation:

    def test_no_rq4_modification(self):
        import inspect
        source = inspect.getsource(_mod.run_single)
        assert "RQ4-MODEL-005" not in source

    def test_no_diag3_modification(self):
        import inspect
        source = inspect.getsource(_mod.main)
        assert "DIAGNOSTIC-003" not in source


class TestModelConfig:

    def test_task_is_bench2_002(self):
        assert _mod.TASK_ID == "BENCH2-002"

    def test_objective_mentions_generated_clock(self):
        assert "generated clock" in _mod.OBJECTIVE.lower()
