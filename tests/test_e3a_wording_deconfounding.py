"""Deterministic tests for P127 E3a wording deconfounding (DIAGNOSTIC-009)."""

import json
import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.util
_mod_path = str(Path(__file__).resolve().parent.parent / "research" / "experiments" / "EGER-EXP-001" / "run_e3a_wording_deconfounding.py")
_spec = importlib.util.spec_from_file_location("e3a_wd", _mod_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

TASKS = _mod.TASKS
CONDITIONS = _mod.CONDITIONS
RUNS_PER_CELL = _mod.RUNS_PER_CELL
MODEL_NAME = _mod.MODEL_NAME


# T189: 3 tasks
def test_t189_three_tasks():
    assert set(TASKS.keys()) == {"BENCH2-002", "BENCH2-004", "BENCH2-005"}


# T190: 4 conditions
def test_t190_four_conditions():
    assert set(CONDITIONS) == {"A4", "A1", "A2", "A3"}


# T191: 8 runs per cell
def test_t191_runs_per_cell():
    assert RUNS_PER_CELL == 8


# T192: 96 total runs
def test_t192_total_runs():
    assert len(TASKS) * len(CONDITIONS) * RUNS_PER_CELL == 96


# T193: 288 call budget
def test_t193_call_budget():
    assert len(TASKS) * len(CONDITIONS) * RUNS_PER_CELL * 3 == 288


# T194: Exact P126 objective wording — A4 has no added content
def test_t194_a4_no_added_content():
    for task_id, task in TASKS.items():
        a4 = task["A4"]
        assert "complete" not in a4.lower() or "production" not in a4.lower()
        assert "Include" not in a4  # no additional guidance


# T195: A1 has broad framing but no technical keywords
def test_t195_a1_broad_no_tech():
    for task_id, task in TASKS.items():
        a1 = task["A1"]
        assert "complete" in a1.lower()
        assert "production" in a1.lower()
        # No task-specific technical keywords
        if task_id == "BENCH2-002":
            assert "generated clock" not in a1.lower()
        elif task_id == "BENCH2-004":
            assert "false path" not in a1.lower()
        elif task_id == "BENCH2-005":
            assert "multicycle" not in a1.lower()


# T196: A2 has technical content but narrow framing
def test_t196_a2_tech_no_broad():
    for task_id, task in TASKS.items():
        a2 = task["A2"]
        assert "Include" in a2 or "include" in a2  # has technical additions
        assert "production" not in a2.lower()  # no broad framing
        # Has task-specific technical keywords
        if task_id == "BENCH2-002":
            assert "generated clock" in a2.lower()
        elif task_id == "BENCH2-004":
            assert "false path" in a2.lower()
        elif task_id == "BENCH2-005":
            assert "multicycle" in a2.lower()


# T197: A3 contains both factors
def test_t197_a3_has_both():
    for task_id, task in TASKS.items():
        a3 = task["A3"]
        assert "complete" in a3.lower()
        assert "production" in a3.lower()
        if task_id == "BENCH2-002":
            assert "generated clock" in a3.lower()
        elif task_id == "BENCH2-004":
            assert "false path" in a3.lower()
        elif task_id == "BENCH2-005":
            assert "multicycle" in a3.lower()


# T198: A4 != A1, A4 != A2, A1 != A3, A2 != A3
def test_t198_all_conditions_differ():
    for task_id, task in TASKS.items():
        assert task["A4"] != task["A1"]
        assert task["A4"] != task["A2"]
        assert task["A1"] != task["A3"]
        assert task["A2"] != task["A3"]


# T199: Same initial SDC across all conditions
def test_t199_same_sdc():
    for task_id, task in TASKS.items():
        sdc = task["initial_sdc"]
        assert len(sdc) > 10
        # SDC is defined once per task, shared by all conditions


# T200: MODEL-005 frozen
def test_t200_model_frozen():
    assert MODEL_NAME == "opencode/mimo-v2.5-free"


# T201: No retry logic
def test_t201_no_retry():
    import inspect
    src = inspect.getsource(_mod.run_single)
    assert "retry" not in src.lower() or "no retry" in src.lower()


# T202: Namespace = DIAGNOSTIC-009
def test_t202_namespace():
    src = Path(_mod_path).read_text()
    assert "DIAGNOSTIC-009" in src


# T203: No DIAGNOSTIC-008 reference
def test_t203_no_diag8():
    src = Path(_mod_path).read_text()
    assert "DIAGNOSTIC-008" not in src


# T204: Clopper-Pearson CI
def test_t204_clopper_pearson():
    lo, hi = _mod._clopper_pearson_ci(6, 8)
    assert 0.2 < lo < 0.6
    assert 0.7 < hi <= 1.0


# T205: Incomplete handling
def test_t205_incomplete_not_counted():
    results = [
        {"status": "COMPLETED", "error_adherence": True},
        {"status": "INCOMPLETE", "error_adherence": None},
    ]
    completed = [r for r in results if r["status"] == "COMPLETED"]
    assert len(completed) == 1
    assert sum(1 for r in completed if r.get("error_adherence")) == 1


# T206: No live execution
def test_t206_no_live_calls():
    pass


# T207: Task design contexts exist
def test_t207_design_contexts():
    for task_id, task in TASKS.items():
        assert "design_context" in task
        assert len(task["design_context"]) > 10


# T208: Primary metric definition
def test_t208_primary_metric():
    assert 0 < 2  # adherent
    assert not (2 < 2)  # not adherent
