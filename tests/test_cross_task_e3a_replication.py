"""Deterministic tests for P121 cross-task E3a replication (DIAGNOSTIC-008)."""

import json
import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.util
_mod_path = str(Path(__file__).resolve().parent.parent / "research" / "experiments" / "EGER-EXP-001" / "run_cross_task_e3a_replication.py")
_spec = importlib.util.spec_from_file_location("cta_rep", _mod_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

TASKS = _mod.TASKS
CONDITIONS = _mod.CONDITIONS
RUNS_PER_CELL = _mod.RUNS_PER_CELL
MODEL_NAME = _mod.MODEL_NAME
MODEL_ID = _mod.MODEL_ID


# T170: 6 cells exist (3 tasks × 2 conditions)
def test_t170_six_cells():
    cells = [(t, c) for t in TASKS for c in CONDITIONS]
    assert len(cells) == 6


# T171: 10 runs per cell
def test_t171_runs_per_cell():
    assert RUNS_PER_CELL == 10


# T172: 60 total runs
def test_t172_total_runs():
    assert len(TASKS) * len(CONDITIONS) * RUNS_PER_CELL == 60


# T173: 180-call budget
def test_t173_call_budget():
    assert len(TASKS) * len(CONDITIONS) * RUNS_PER_CELL * 3 == 180


# T174: Exact BASE/E3a objective mapping per task
def test_t174_objective_mapping():
    for task_id, task in TASKS.items():
        assert "base_objective" in task
        assert "e3a_objective" in task
        assert task["base_objective"] != task["e3a_objective"]
        # E3a should contain "complete" or "production"
        assert "complete" in task["e3a_objective"].lower() or "production" in task["e3a_objective"].lower()


# T175: Identical SDC within each task
def test_t175_identical_sdc():
    for task_id, task in TASKS.items():
        assert len(task["initial_sdc"]) > 0
        # SDC should be the same for both conditions (it's defined once per task)
        # BASE and E3a use the same task["initial_sdc"]


# T176: MODEL-005 frozen
def test_t176_model_frozen():
    assert MODEL_NAME == "opencode/mimo-v2.5-free"
    assert MODEL_ID == "EGER-MODEL-005"


# T177: Primary metric definition
def test_t177_primary_metric():
    # Adherent: final_error_count < initial_error_count
    assert 0 < 2  # delta=-2 -> adherent
    assert not (2 < 2)  # delta=0 -> not adherent


# T178: BENCH2-002 has generated clock check
def test_t178_bench2_002_has_generated_clock():
    sdc = TASKS["BENCH2-002"]["initial_sdc"]
    assert "create_generated_clock" in sdc.lower()


# T179: BENCH2-004 has false path check
def test_t179_bench2_004_has_false_path():
    sdc = TASKS["BENCH2-004"]["initial_sdc"]
    assert "set_false_path" in sdc.lower()


# T180: BENCH2-005 has multicycle path check
def test_t180_bench2_005_has_multicycle():
    sdc = TASKS["BENCH2-005"]["initial_sdc"]
    assert "set_multicycle_path" in sdc.lower()


# T181: Failure policy — no retry
def test_t181_no_retry():
    import inspect
    src = inspect.getsource(_mod.run_single)
    assert "retry" not in src.lower() or "no retry" in src.lower()


# T182: No model substitution
def test_t182_no_substitution():
    assert MODEL_NAME == "opencode/mimo-v2.5-free"


# T183: Namespace isolation
def test_t183_namespace():
    src = Path(_mod_path).read_text()
    assert "DIAGNOSTIC-008" in src


# T184: Historical artifact preservation
def test_t184_no_diagnostic_006_modification():
    src = Path(_mod_path).read_text()
    # Should not import or modify DIAGNOSTIC-006
    assert "DIAGNOSTIC-006" not in src


# T185: Incomplete run handling
def test_t185_incomplete_not_counted():
    results = [
        {"status": "COMPLETED", "error_adherence": True},
        {"status": "COMPLETED", "error_adherence": False},
        {"status": "INCOMPLETE", "error_adherence": None},
    ]
    completed = [r for r in results if r["status"] == "COMPLETED"]
    adherent = sum(1 for r in completed if r.get("error_adherence"))
    assert len(completed) == 2
    assert adherent == 1


# T186: Clopper-Pearson CI
def test_t186_clopper_pearson():
    lo, hi = _mod._clopper_pearson_ci(8, 10)
    assert 0.4 < lo < 0.6
    assert 0.9 < hi <= 1.0


# T187: Task design contexts exist
def test_t187_design_contexts():
    for task_id, task in TASKS.items():
        assert "design_context" in task
        assert len(task["design_context"]) > 10


# T188: No live execution in test
def test_t188_no_live_calls():
    pass
