"""EGER P177 — orchestrator + qualified-accept tests (fixtures only).

Verifies the repaired matrix orchestrator mechanically:
- frozen 8-trial matrix in counterbalanced order with pre-run assertion,
- bounded retry with both attempts retained,
- PO-1/PO-2/PO-3 and qualified_accept derived deterministically,
- no real Oracle / model / WSL involvement.

Fixtures mirror run_dryrun_matrix.py; NOT experimental data.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
PILOT_DIR = Path(__file__).resolve().parents[1]
for p in (str(PROJECT_ROOT), str(PILOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from harness.orchestrator import run_matrix
from harness.matrix import frozen_matrix, assert_matrix_order
from harness.fixtures import (
    FakeOracle,
    FakeModelProvider,
    build_pipeline,
    CONVERSATIONAL_FILLER,
    SDC_T1_VALID,
    SDC_T2_AGGRESSIVE,
    SDC_T2_RELAXED,
)
from harness.trial_runner import derive_trial_metrics

_FIXTURE_MODEL_OUTPUTS = {
    "T1-Rta-R1": [SDC_T1_VALID],
    "T1-Rta-R2": [SDC_T1_VALID],
    "T1-OpenSTA-R1": [SDC_T1_VALID],
    "T1-OpenSTA-R2": [SDC_T1_VALID],
    "T2-Rta-R1": [SDC_T2_RELAXED],
    "T2-Rta-R2": [SDC_T2_RELAXED],
    "T2-OpenSTA-R1": [SDC_T2_AGGRESSIVE, SDC_T2_RELAXED],
    "T2-OpenSTA-R2": [CONVERSATIONAL_FILLER, SDC_T2_RELAXED],
}


def _fixture_callables(row: dict):
    oracle = FakeOracle(oracle_name=row["oracle"])
    model = FakeModelProvider(_FIXTURE_MODEL_OUTPUTS[row["trial_id"]])
    return oracle.validate, model.invoke


class TestFrozenMatrix:
    def test_matrix_is_frozen_and_counterbalanced(self):
        trials = frozen_matrix()
        assert len(trials) == 8
        # Counterbalancing: Rta first in T1 block, OpenSTA first in T2 block.
        t1_first = [t for t in trials if t["task_id"] == "T1"][0]
        t2_first = [t for t in trials if t["task_id"] == "T2"][0]
        assert t1_first["oracle"] == "Rta"
        assert t2_first["oracle"] == "OpenSTA"
        assert_matrix_order(trials)  # must not raise


class TestOrchestratorDryRun:
    def setup_method(self):
        self.normalizer, self.gate = build_pipeline()

    def test_runs_eight_trials_in_frozen_order(self):
        result = run_matrix(_fixture_callables, self.normalizer, self.gate)
        records = result["records"]
        assert len(records) == 8
        ids = [r["trial_id"] for r in records]
        assert ids == [t["trial_id"] for t in frozen_matrix()]

    def test_all_completed_with_initial_evaluation(self):
        result = run_matrix(_fixture_callables, self.normalizer, self.gate)
        for rec in result["records"]:
            assert rec["completion_status"] == "COMPLETED"
            assert rec.get("initial_oracle_result", {}).get("is_success") is True
            assert rec.get("initial_sdc_hash")

    def test_bounded_retry_records_both_attempts(self):
        result = run_matrix(_fixture_callables, self.normalizer, self.gate)
        retried = [r for r in result["records"] if r["trial_id"] == "T2-OpenSTA-R2"][0]
        assert retried["retry_count"] == 1
        assert len(retried["attempts"]) == 2
        # Attempt 1 failed with a retryable generation failure.
        assert retried["attempts"][0]["completion_status"] == "FAILED"
        assert retried["attempts"][0]["failure_kind"] == "CANDIDATE_INVALID"
        # Attempt 2 completed.
        assert retried["attempts"][1]["completion_status"] == "COMPLETED"

    def test_analysis_derives_counts_from_raw_records(self):
        result = run_matrix(_fixture_callables, self.normalizer, self.gate)
        a = result["analysis"]
        assert a["planned_trials"] == 8
        assert a["completed_trials"] == 8
        assert a["retry_attempts"] == 1
        assert a["evidence_artifacts"] == a["oracle_evaluations"]
        # Every condition cell has 2 trials and 2 qualified accepts (fixtures).
        for cond, c in a["per_condition"].items():
            assert c["count"] == 2
            assert c["qualified_accept"] == 2


class TestQualifiedAcceptRule:
    def test_qualified_accept_true_for_clean_accept(self):
        record = {
            "oracle": "OpenSTA",
            "completion_status": "COMPLETED",
            "accept_reached": True,
            "initial_oracle_result": {"is_success": True, "wns": 0.0},
            "final_oracle_result": {"is_success": True, "wns": 0.0},
            "iterations": [{
                "iteration": 1,
                "verification_decision": "ACCEPT",
                "oracle_result": {"is_success": True, "metadata_all_validated": None, "wns": 0.0},
            }],
        }
        m = derive_trial_metrics(record)
        assert m["qualified_accept"] is True

    def test_unqualified_accept_is_not_qualified_and_caps_po1(self):
        """An Rta ACCEPT resting on metadata-unqualified (PARTIAL) evidence is
        not a qualified accept and can never be ROBUST (P177 §13)."""
        record = {
            "oracle": "Rta",
            "completion_status": "COMPLETED",
            "accept_reached": True,
            "initial_oracle_result": {"is_success": True, "error_count": 1},
            "final_oracle_result": {"is_success": True, "error_count": 0},
            "iterations": [{
                "iteration": 1,
                "verification_decision": "ACCEPT",
                "oracle_result": {
                    "is_success": True,
                    "metadata_all_validated": False,
                    "error_count": 0,
                },
            }],
        }
        m = derive_trial_metrics(record)
        assert m["metadata_unqualified_iterations"] == [1]
        assert m["qualified_accept"] is False
        # PO-3 measured IMPROVED → naive PO-1 ROBUST, but capped to MARGINAL.
        assert m["oracle_detected_improvement"] == "IMPROVED"
        assert m["completion_quality"] == "MARGINAL"
