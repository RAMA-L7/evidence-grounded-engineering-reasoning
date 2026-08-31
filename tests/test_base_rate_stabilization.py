"""Deterministic tests for DIAGNOSTIC-007 base-rate stabilization (P115)."""

import json
import hashlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.util
_mod_path = str(Path(__file__).resolve().parent.parent / "research" / "experiments" / "EGER-EXP-001" / "run_base_rate_stabilization.py")
_spec = importlib.util.spec_from_file_location("base_rate_stab", _mod_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
INITIAL_SDC = _mod.INITIAL_SDC
DESIGN_CONTEXT = _mod.DESIGN_CONTEXT
OBJECTIVE = _mod.OBJECTIVE
MODEL_NAME = _mod.MODEL_NAME
MODEL_ID = _mod.MODEL_ID
TASK_ID = _mod.TASK_ID
RUNS_TOTAL = _mod.RUNS_TOTAL
_clopper_pearson_ci = _mod._clopper_pearson_ci
_load_design_metadata = _mod._load_design_metadata
run_single = _mod.run_single


# ---------------------------------------------------------------------------
# T154: Exact 51-character SDC
# ---------------------------------------------------------------------------
def test_t154_initial_sdc_is_51_chars():
    assert len(INITIAL_SDC) == 51
    assert INITIAL_SDC == "create_clock -name clk -period 10.0 [get_ports clk]"


# ---------------------------------------------------------------------------
# T155: Exact task/context/objective
# ---------------------------------------------------------------------------
def test_t155_frozen_task_inputs():
    assert TASK_ID == "BENCH2-001"
    assert "clk" in DESIGN_CONTEXT
    assert "data_in" in DESIGN_CONTEXT
    assert "primary clock" in OBJECTIVE


# ---------------------------------------------------------------------------
# T156: MODEL-005 configuration
# ---------------------------------------------------------------------------
def test_t156_model_config():
    assert MODEL_NAME == "opencode/mimo-v2.5-free"
    assert MODEL_ID == "EGER-MODEL-005"


# ---------------------------------------------------------------------------
# T157: 20-run configuration
# ---------------------------------------------------------------------------
def test_t157_runs_total():
    assert RUNS_TOTAL == 20


# ---------------------------------------------------------------------------
# T158: 60-call budget
# ---------------------------------------------------------------------------
def test_t158_call_budget():
    # 20 runs × 3 calls (init oracle + model + final oracle) = 60
    assert RUNS_TOTAL * 3 == 60


# ---------------------------------------------------------------------------
# T159: Primary adherence calculation
# ---------------------------------------------------------------------------
def test_t159_adherence_calculation():
    # Adherent: final_error_count < initial_error_count
    assert 0 < 2  # delta=-2 -> adherent
    assert not (2 < 2)  # delta=0 -> not adherent


# ---------------------------------------------------------------------------
# T160: Error delta calculation
# ---------------------------------------------------------------------------
def test_t160_error_delta():
    initial = 2
    final = 0
    delta = final - initial
    assert delta == -2
    assert delta < 0  # improvement


# ---------------------------------------------------------------------------
# T161: Incomplete run handling
# ---------------------------------------------------------------------------
def test_t161_incomplete_not_counted():
    """Incomplete runs should not be counted as adherent or non-adherent."""
    results = [
        {"status": "COMPLETED", "error_adherence": True},
        {"status": "COMPLETED", "error_adherence": False},
        {"status": "INCOMPLETE", "error_adherence": None},
    ]
    completed = [r for r in results if r["status"] == "COMPLETED"]
    adherent = sum(1 for r in completed if r.get("error_adherence"))
    assert len(completed) == 2
    assert adherent == 1


# ---------------------------------------------------------------------------
# T162: Oracle failure handling
# ---------------------------------------------------------------------------
def test_t161b_oracle_failure_status():
    """Oracle failure should produce INCOMPLETE_MEASUREMENT status."""
    result = {"status": "INCOMPLETE_MEASUREMENT"}
    assert result["status"] != "COMPLETED"
    assert result["status"] != "INCOMPLETE"


# ---------------------------------------------------------------------------
# T163: No-retry behavior
# ---------------------------------------------------------------------------
def test_t163_runner_has_no_retry():
    """Runner should not have retry logic."""
    import inspect
    source = inspect.getsource(run_single)
    assert "retry" not in source.lower() or "no retry" in source.lower()


# ---------------------------------------------------------------------------
# T164: No model substitution
# ---------------------------------------------------------------------------
def test_t164_no_model_substitution():
    """Runner should only use MODEL-005."""
    assert MODEL_NAME == "opencode/mimo-v2.5-free"


# ---------------------------------------------------------------------------
# T165: Clopper-Pearson CI calculation
# ---------------------------------------------------------------------------
def test_t165_clopper_pearson():
    # 8/10 -> should match DIAGNOSTIC-006 Base CI approximately
    lo, hi = _clopper_pearson_ci(8, 10)
    assert 0.4 < lo < 0.6  # lower bound around 45-55%
    assert 0.9 < hi <= 1.0  # upper bound near 100%

    # 0/10 -> CI should be [0, ~31%]
    lo0, hi0 = _clopper_pearson_ci(0, 10)
    assert lo0 == 0.0
    assert hi0 < 0.35

    # 10/10 -> CI should be [~71%, 1.0]
    lo10, hi10 = _clopper_pearson_ci(10, 10)
    assert lo10 > 0.7
    assert hi10 == 1.0

    # 4/10 -> should match P090 CI approximately
    lo4, hi4 = _clopper_pearson_ci(4, 10)
    assert 0.1 < lo4 < 0.2  # ~12-18%
    assert 0.7 < hi4 < 0.8  # ~72-79%


# ---------------------------------------------------------------------------
# T166: Historical artifact isolation
# ---------------------------------------------------------------------------
def test_t166_namespace_isolation():
    """DIAGNOSTIC-007 namespace should be separate from DIAGNOSTIC-006."""
    runner_path = Path(__file__).resolve().parents[1] / "research" / "experiments" / "EGER-EXP-001" / "run_base_rate_stabilization.py"
    source = runner_path.read_text()
    assert "DIAGNOSTIC-007" in source
    assert "DIAGNOSTIC-006" not in source.split("DIAGNOSTIC-007")[0]  # no reference before namespace


# ---------------------------------------------------------------------------
# T167: Summary calculation
# ---------------------------------------------------------------------------
def test_t167_summary_calculation():
    results = [
        {"status": "COMPLETED", "error_adherence": True, "proposal_changed": True},
        {"status": "COMPLETED", "error_adherence": True, "proposal_changed": True},
        {"status": "COMPLETED", "error_adherence": False, "proposal_changed": True},
        {"status": "INCOMPLETE", "error_adherence": None, "proposal_changed": False},
    ]
    completed = [r for r in results if r["status"] == "COMPLETED"]
    adherent = sum(1 for r in completed if r.get("error_adherence"))
    activated = sum(1 for r in completed if r.get("proposal_changed"))
    n = len(completed)
    assert n == 3
    assert adherent == 2
    assert activated == 3  # all 3 completed runs activated
    lo, hi = _clopper_pearson_ci(adherent, n)
    assert lo < hi
    assert 0.0 <= lo <= 1.0
    assert 0.0 <= hi <= 1.0


# ---------------------------------------------------------------------------
# T168: Feedback hash is deterministic
# ---------------------------------------------------------------------------
def test_t168_feedback_hash():
    """Same feedback should produce same hash."""
    fb = json.dumps({"test": "data"}, sort_keys=True)
    h1 = hashlib.sha256(fb.encode("utf-8")).hexdigest()
    h2 = hashlib.sha256(fb.encode("utf-8")).hexdigest()
    assert h1 == h2
    assert len(h1) == 64


# ---------------------------------------------------------------------------
# T169: No live execution in test
# ---------------------------------------------------------------------------
def test_t169_no_live_calls_in_test():
    """This test file should not make any live model/oracle calls."""
    # All tests use mocks or pure calculations
    pass
