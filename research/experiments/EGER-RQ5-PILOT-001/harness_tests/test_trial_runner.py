"""Tests for the repaired trial runner (P172 §7, §8, §13)."""

from harness.trial_runner import (
    run_trial,
    compute_po3,
    compute_po1,
    derive_trial_metrics,
)
from harness.fixtures import (
    FakeOracle,
    FailingOracle,
    build_model_call,
    build_pipeline,
    SDC_T1_VALID,
    SDC_T1_VALID_IMPROVED,
    SDC_T2_AGGRESSIVE,
    CONVERSATIONAL_FILLER,
)
from harness.tasks import get_task


def _run(trial_id, oracle_name, model_outputs, oracle=None, max_retries=1):
    normalizer, gate = build_pipeline()
    task = get_task("T1")
    o = oracle or FakeOracle(oracle_name=oracle_name)
    record = run_trial(
        trial_id=trial_id,
        task_id="T1",
        oracle_name=oracle_name,
        replication_id=1,
        execution_order=1,
        initial_sdc=task["initial_sdc"],
        design_context=task["design_context"],
        oracle_call=o.validate,
        model_call=build_model_call(model_outputs),
        normalizer=normalizer,
        gate=gate,
        max_iterations=3,
        max_retries=max_retries,
    )
    return record, o


# ---------------------------------------------------------------------------
# Initial Oracle evaluation (PO-3 repair)
# ---------------------------------------------------------------------------

def test_initial_oracle_evaluation_recorded():
    record, o = _run("T1-Rta-R1", "Rta", [SDC_T1_VALID_IMPROVED])
    assert record["initial_oracle_result"] is not None
    assert record["initial_oracle_result"]["is_success"] is True
    assert record["initial_evidence_hash"] is not None
    # initial SDC (clock only) is incomplete → 1 ERROR
    assert record["initial_oracle_result"]["error_count"] == 1
    assert o.calls[0] == "T1-Rta-R1-initial"


def test_final_oracle_evaluation_recorded():
    record, _ = _run("T1-Rta-R1", "Rta", [SDC_T1_VALID_IMPROVED])
    assert record["final_oracle_result"] is not None
    assert record["final_sdc_hash"] is not None


# ---------------------------------------------------------------------------
# PO-3 / PO-1 derivation
# ---------------------------------------------------------------------------

def test_po3_rta_improved():
    initial = {"is_success": True, "error_count": 1}
    final = {"is_success": True, "error_count": 0}
    assert compute_po3(initial, final, "Rta") == "IMPROVED"


def test_po3_rta_not_improved():
    initial = {"is_success": True, "error_count": 1}
    final = {"is_success": True, "error_count": 1}
    assert compute_po3(initial, final, "Rta") == "NOT_IMPROVED"


def test_po3_rta_worse():
    initial = {"is_success": True, "error_count": 0}
    final = {"is_success": True, "error_count": 2}
    assert compute_po3(initial, final, "Rta") == "WORSE"


def test_po3_opensta_improved():
    initial = {"is_success": True, "wns": -0.10}
    final = {"is_success": True, "wns": 0.0}
    assert compute_po3(initial, final, "OpenSTA") == "IMPROVED"


def test_po3_opensta_no_timing_constraint_not_measurable():
    # P172 §13 boundary: initial WNS undefined (NO_TIMING_CONSTRAINT)
    initial = {"is_success": True, "wns": None}
    final = {"is_success": True, "wns": 0.0}
    assert compute_po3(initial, final, "OpenSTA") == "NOT_MEASURABLE"


def test_po3_missing_data_not_measurable():
    assert compute_po3(None, {"is_success": True, "wns": 0.0}, "OpenSTA") == "NOT_MEASURABLE"


def test_po1_robust_marginal_failed():
    assert compute_po1("COMPLETED", "IMPROVED") == "ROBUST"
    assert compute_po1("COMPLETED", "NOT_IMPROVED") == "MARGINAL"
    assert compute_po1("FAILED", "NOT_MEASURABLE") == "FAILED"


def test_full_run_rta_improved_robust():
    record, _ = _run("T1-Rta-R1", "Rta", [SDC_T1_VALID_IMPROVED])
    assert record["completion_status"] == "COMPLETED"
    assert record["retry_count"] == 0
    metrics = derive_trial_metrics(record)
    assert metrics["oracle_detected_improvement"] == "IMPROVED"
    assert metrics["completion_quality"] == "ROBUST"
    assert metrics["evidence_compatible"] is True


# ---------------------------------------------------------------------------
# Retry policy (P172 §8)
# ---------------------------------------------------------------------------

def test_retry_on_conversational_filler_then_success():
    # Attempt 1: filler (CANDIDATE_INVALID) → retry; attempt 2: valid SDC
    normalizer, gate = build_pipeline()
    task = get_task("T1")
    o = FakeOracle(oracle_name="Rta")
    record = run_trial(
        trial_id="T1-Rta-R2",
        task_id="T1",
        oracle_name="Rta",
        replication_id=2,
        execution_order=3,
        initial_sdc=task["initial_sdc"],
        design_context=task["design_context"],
        oracle_call=o.validate,
        model_call=build_model_call([CONVERSATIONAL_FILLER, SDC_T1_VALID_IMPROVED]),
        normalizer=normalizer,
        gate=gate,
        max_iterations=3,
        max_retries=1,
    )
    assert len(record["attempts"]) == 2
    assert record["attempts"][0]["completion_status"] == "FAILED"
    assert record["attempts"][0]["failure_kind"] == "CANDIDATE_INVALID"
    assert record["attempts"][1]["completion_status"] == "COMPLETED"
    assert record["completion_status"] == "COMPLETED"
    assert record["retry_count"] == 1


def test_no_retry_on_non_retryable_oracle_failure():
    # ORACLE_FAILURE (non-zero exit on valid candidate) is NOT retried
    normalizer, gate = build_pipeline()
    task = get_task("T1")
    failing = FailingOracle(failure_kind="ORACLE_FAILURE", exit_code=3)
    record = run_trial(
        trial_id="T1-Rta-R3",
        task_id="T1",
        oracle_name="Rta",
        replication_id=3,
        execution_order=1,
        initial_sdc=task["initial_sdc"],
        design_context=task["design_context"],
        oracle_call=failing.validate,
        model_call=build_model_call([SDC_T1_VALID_IMPROVED]),
        normalizer=normalizer,
        gate=gate,
        max_iterations=3,
        max_retries=1,
    )
    assert record["completion_status"] == "FAILED"
    assert record["failure_kind"] == "ORACLE_FAILURE"
    assert record["retry_count"] == 0  # non-retryable → no second attempt


def test_both_attempts_fail_after_retry():
    normalizer, gate = build_pipeline()
    task = get_task("T1")
    record = run_trial(
        trial_id="T1-Rta-R4",
        task_id="T1",
        oracle_name="Rta",
        replication_id=4,
        execution_order=1,
        initial_sdc=task["initial_sdc"],
        design_context=task["design_context"],
        oracle_call=FakeOracle(oracle_name="Rta").validate,
        model_call=build_model_call([CONVERSATIONAL_FILLER]),
        normalizer=normalizer,
        gate=gate,
        max_iterations=3,
        max_retries=1,
    )
    assert record["completion_status"] == "FAILED"
    assert record["failure_kind"] == "CANDIDATE_INVALID"
    assert record["retry_count"] == 1


# ---------------------------------------------------------------------------
# NO_TIMING_CONSTRAINT (P172 §13)
# ---------------------------------------------------------------------------

def test_no_timing_constraint_iterations_empty_when_clock_defined():
    record, _ = _run("T1-OpenSTA-R1", "OpenSTA", [SDC_T1_VALID], oracle=FakeOracle(oracle_name="OpenSTA"))
    metrics = derive_trial_metrics(record)
    assert metrics["no_timing_constraint_iterations"] == []
    # candidate kept the clock → clock_defined True
    for it in record["iterations"]:
        assert it.get("clock_defined") is True


def test_opensta_aggressive_violation_rejected():
    normalizer, gate = build_pipeline()
    task = get_task("T2")
    o = FakeOracle(oracle_name="OpenSTA")
    record = run_trial(
        trial_id="T2-OpenSTA-R1",
        task_id="T2",
        oracle_name="OpenSTA",
        replication_id=1,
        execution_order=5,
        initial_sdc=task["initial_sdc"],
        design_context=task["design_context"],
        oracle_call=o.validate,
        model_call=build_model_call([SDC_T2_AGGRESSIVE]),
        normalizer=normalizer,
        gate=gate,
        max_iterations=3,
        max_retries=1,
    )
    # Aggressive clock → setup violation → REJECT at gate; loop continues;
    # model keeps returning aggressive SDC → ends MARGINAL (completed, no improvement)
    assert record["completion_status"] == "COMPLETED"
    metrics = derive_trial_metrics(record)
    assert metrics["completion_quality"] == "MARGINAL"
    assert record["iterations"][-1]["verification_decision"] == "REJECT"