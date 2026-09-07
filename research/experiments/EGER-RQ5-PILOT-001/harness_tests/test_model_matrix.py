"""EGER P185 — model-comparison matrix + orchestrator tests (fixtures only).

Verifies the frozen 16-trial model-comparison matrix mechanically:
- 16 trials, 8 per model, baseline block first, comparison second,
- counterbalancing within each model block (T1 Rta-first, T2 OpenSTA-first),
- pre-run order assertion passes and rejects reordered lists,
- model label propagation through run_model_matrix records and per_model
  analysis aggregation.

Fixtures mirror the PILOT-002 dry-run pattern; NOT experimental data.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
PILOT_DIR = Path(__file__).resolve().parents[1]
for p in (str(PROJECT_ROOT), str(PILOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from harness.model_matrix import (
    frozen_model_matrix,
    assert_model_matrix_order,
    validate_model_matrix_row_count,
    MODEL_IDS,
    MODEL_TIMEOUTS,
)
from harness.orchestrator import run_model_matrix, audit_candidate_identity
from harness.matrix import frozen_matrix
from harness.fixtures import (
    FakeOracle,
    FakeModelProvider,
    build_pipeline,
    SDC_T1_VALID,
    SDC_T2_AGGRESSIVE,
    SDC_T2_RELAXED,
    CONVERSATIONAL_FILLER,
)
from harness.tasks import TASKS
from harness.trial_runner import sha256_text


class TestModelMatrixFrozen:
    def test_16_trials_8_per_model(self):
        m = frozen_model_matrix()
        assert len(m) == 16
        assert [r["model"] for r in m].count("mimo") == 8
        assert [r["model"] for r in m].count("nemotron") == 8

    def test_baseline_block_first(self):
        m = frozen_model_matrix()
        assert m[0]["model"] == "mimo"
        assert m[8]["model"] == "nemotron"
        # Blocks are contiguous.
        assert [r["model"] for r in m][:8] == ["mimo"] * 8
        assert [r["model"] for r in m][8:] == ["nemotron"] * 8

    def test_counterbalancing_within_model_blocks(self):
        m = frozen_model_matrix()
        for model in ("mimo", "nemotron"):
            block = [r for r in m if r["model"] == model]
            t1_first = [r for r in block if r["task_id"] == "T1"][0]
            t2_first = [r for r in block if r["task_id"] == "T2"][0]
            assert t1_first["oracle"] == "Rta"
            assert t2_first["oracle"] == "OpenSTA"

    def test_assert_passes_on_frozen_and_rejects_reordered(self):
        assert_model_matrix_order(frozen_model_matrix())
        m = frozen_model_matrix()
        m[0], m[1] = m[1], m[0]  # swap first two trials
        try:
            assert_model_matrix_order(m)
            raised = False
        except AssertionError:
            raised = True
        assert raised

    def test_validate_2x2x2x2_replication(self):
        validate_model_matrix_row_count(frozen_model_matrix())

    def test_trial_ids_match_p183_convention(self):
        m = frozen_model_matrix()
        ids = [r["trial_id"] for r in m]
        # P183 convention: T<task>-<model>-R<rep> for Rta, explicit Oracle otherwise.
        assert ids[:4] == [
            "T1-mimo-R1", "T1-mimo-OpenSTA-R1", "T1-mimo-R2", "T1-mimo-OpenSTA-R2",
        ]
        assert ids[4:8] == [
            "T2-mimo-OpenSTA-R1", "T2-mimo-R1", "T2-mimo-OpenSTA-R2", "T2-mimo-R2",
        ]
        assert ids[8] == "T1-nemotron-R1"
        assert ids[15] == "T2-nemotron-R2"

    def test_model_ids_and_timeouts_frozen(self):
        assert MODEL_IDS["mimo"] == "opencode/mimo-v2.5-free"
        assert MODEL_IDS["nemotron"] == "opencode/nemotron-3.5-lightning-free"
        assert MODEL_TIMEOUTS["mimo"] == 180
        assert MODEL_TIMEOUTS["nemotron"] == 300


# Fixture output plan per trial (deterministic). Nemotron block mirrors the
# mimo block (same task semantics); retry path exercised on one trial.
_FIXTURE_MODEL_OUTPUTS = {}
for model in ("mimo", "nemotron"):
    _FIXTURE_MODEL_OUTPUTS[f"T1-{model}-R1"] = [SDC_T1_VALID]
    _FIXTURE_MODEL_OUTPUTS[f"T1-{model}-R2"] = [SDC_T1_VALID]
    _FIXTURE_MODEL_OUTPUTS[f"T1-{model}-OpenSTA-R1"] = [SDC_T1_VALID]
    _FIXTURE_MODEL_OUTPUTS[f"T1-{model}-OpenSTA-R2"] = [SDC_T1_VALID]
    _FIXTURE_MODEL_OUTPUTS[f"T2-{model}-OpenSTA-R1"] = [SDC_T2_AGGRESSIVE, SDC_T2_RELAXED]
    _FIXTURE_MODEL_OUTPUTS[f"T2-{model}-R1"] = [SDC_T2_RELAXED]
    _FIXTURE_MODEL_OUTPUTS[f"T2-{model}-OpenSTA-R2"] = [SDC_T2_AGGRESSIVE, SDC_T2_RELAXED]
    _FIXTURE_MODEL_OUTPUTS[f"T2-{model}-R2"] = [SDC_T2_RELAXED]
# Retry path: nemotron T1-OpenSTA-R2 first output is conversational filler.
_FIXTURE_MODEL_OUTPUTS["T1-nemotron-OpenSTA-R2"] = [CONVERSATIONAL_FILLER, SDC_T1_VALID]


def _fixture_callables(row: dict):
    oracle = FakeOracle(oracle_name=row["oracle"])
    model = FakeModelProvider(_FIXTURE_MODEL_OUTPUTS[row["trial_id"]])
    return oracle.validate, model.invoke


class TestModelOrchestrator:
    def setup_method(self):
        self.normalizer, self.gate = build_pipeline()

    def test_runs_sixteen_trials_with_model_propagation(self):
        result = run_model_matrix(_fixture_callables, self.normalizer, self.gate)
        records = result["records"]
        assert len(records) == 16
        ids = [r["trial_id"] for r in records]
        assert ids == [t["trial_id"] for t in frozen_model_matrix()]
        # Model label recorded on every trial.
        assert all(r.get("model") in ("mimo", "nemotron") for r in records)
        assert all(r.get("initial_oracle_result", {}).get("is_success") for r in records)

    def test_all_completed_with_initial_evaluation(self):
        result = run_model_matrix(_fixture_callables, self.normalizer, self.gate)
        for rec in result["records"]:
            assert rec["completion_status"] == "COMPLETED"
            assert rec.get("initial_sdc_hash")
            assert rec.get("final_sdc_hash")

    def test_retry_path_with_both_attempts_retained(self):
        result = run_model_matrix(_fixture_callables, self.normalizer, self.gate)
        retried = [r for r in result["records"] if r["trial_id"] == "T1-nemotron-OpenSTA-R2"][0]
        assert retried["retry_count"] == 1
        assert len(retried["attempts"]) == 2
        assert retried["attempts"][0]["completion_status"] == "FAILED"
        assert retried["attempts"][0]["failure_kind"] == "CANDIDATE_INVALID"
        assert retried["attempts"][1]["completion_status"] == "COMPLETED"

    def test_analysis_per_model_aggregation(self):
        result = run_model_matrix(_fixture_callables, self.normalizer, self.gate)
        a = result["analysis"]
        assert a["planned_trials"] == 16
        assert a["total_trials"] == 16
        assert a["completed_trials"] == 16
        assert set(a["per_model"].keys()) == {"mimo", "nemotron"}
        for model in ("mimo", "nemotron"):
            pm = a["per_model"][model]
            assert pm["trials"] == 8
            assert pm["completed_trials"] == 8
            assert sum(pm["po1"].values()) == 8
            assert sum(pm["po3"].values()) == 8
        # Per (model, task, oracle) condition cells: 2 models × 2 tasks ×
        # 2 Oracles = 8 cells, each with 2 replications (16 trials total).
        assert len(a["per_model_condition"]) == 8
        assert all(v["count"] == 2 for v in a["per_model_condition"].values())
        assert sum(v["count"] for v in a["per_model_condition"].values()) == 16

    def test_identity_audit_ok_across_models(self):
        result = run_model_matrix(_fixture_callables, self.normalizer, self.gate)
        audit = result["identity_audit"]
        assert audit["ok"] is True
        assert audit["shared_initial_across_arms"] is True
        # One shared initial hash per task across BOTH models and both arms.
        for task, hashes in audit["shared_task_initial_hashes"].items():
            assert len(hashes) == 1
            assert hashes[0] == sha256_text(TASKS[task]["initial_sdc"])