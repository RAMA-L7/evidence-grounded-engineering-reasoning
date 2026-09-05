"""Tests for deterministic PO-2 aggregation (P172 §12)."""

from harness.trial_runner import run_trial
from harness.analysis import analyze_trials
from harness.fixtures import (
    FakeOracle,
    build_model_call,
    build_pipeline,
    SDC_T1_VALID_IMPROVED,
    CONVERSATIONAL_FILLER,
)
from harness.tasks import get_task


def _make_trial(trial_id, task_id, oracle_name, replication_id, execution_order, model_outputs, oracle=None, max_retries=1):
    normalizer, gate = build_pipeline()
    task = get_task(task_id)
    o = oracle or FakeOracle(oracle_name=oracle_name)
    return run_trial(
        trial_id=trial_id,
        task_id=task_id,
        oracle_name=oracle_name,
        replication_id=replication_id,
        execution_order=execution_order,
        initial_sdc=task["initial_sdc"],
        design_context=task["design_context"],
        oracle_call=o.validate,
        model_call=build_model_call(model_outputs),
        normalizer=normalizer,
        gate=gate,
        max_iterations=3,
        max_retries=max_retries,
    )


def test_analysis_derives_counts_from_records():
    trials = [
        _make_trial("T1-Rta-R1", "T1", "Rta", 1, 1, [SDC_T1_VALID_IMPROVED]),
        _make_trial("T1-Rta-R2", "T1", "Rta", 2, 2, [CONVERSATIONAL_FILLER]),  # fails (candidate invalid)
    ]
    analysis = analyze_trials(trials)
    assert analysis["total_trials"] == 2
    assert analysis["completed_trials"] == 1
    assert analysis["failed_trials"] == 1
    assert analysis["failure_kinds"] == {"CANDIDATE_INVALID": 1}


def test_analysis_denominators_explicit():
    trials = [
        _make_trial("T1-Rta-R1", "T1", "Rta", 1, 1, [SDC_T1_VALID_IMPROVED]),
        _make_trial("T1-OpenSTA-R1", "T1", "OpenSTA", 1, 2, [SDC_T1_VALID_IMPROVED]),
    ]
    analysis = analyze_trials(trials)
    # Per-oracle denominators
    assert analysis["per_oracle"]["Rta"]["oracle_evaluations"] > 0
    assert analysis["per_oracle"]["OpenSTA"]["oracle_evaluations"] > 0
    # Successful evaluations ≤ total
    for oracle in ("Rta", "OpenSTA"):
        po = analysis["per_oracle"][oracle]
        assert po["successful_evaluations"] <= po["oracle_evaluations"]


def test_analysis_deterministic():
    t1 = _make_trial("T1-Rta-R1", "T1", "Rta", 1, 1, [SDC_T1_VALID_IMPROVED])
    a1 = analyze_trials([t1])
    t2 = _make_trial("T1-Rta-R1", "T1", "Rta", 1, 1, [SDC_T1_VALID_IMPROVED])
    a2 = analyze_trials([t2])
    assert a1 == a2  # identical inputs → identical analysis


def test_analysis_po1_counts():
    trials = [
        _make_trial("T1-Rta-R1", "T1", "Rta", 1, 1, [SDC_T1_VALID_IMPROVED]),
        _make_trial("T2-Rta-R1", "T2", "Rta", 1, 2, [SDC_T1_VALID_IMPROVED]),
    ]
    analysis = analyze_trials(trials)
    for key in ("T1-Rta", "T2-Rta"):
        cond = analysis["per_condition"][key]
        # T1: initial incomplete (1 ERROR) -> improved (0) = ROBUST
        # T2: initial aggressive (violation for Rta? no - Rta semantics: incomplete = 1 ERROR)
        assert cond["po1"]["ROBUST"] + cond["po1"]["MARGINAL"] + cond["po1"]["FAILED"] == cond["count"]


def test_analysis_evidence_artifacts_consistent():
    trials = [
        _make_trial("T1-Rta-R1", "T1", "Rta", 1, 1, [SDC_T1_VALID_IMPROVED]),
    ]
    analysis = analyze_trials(trials)
    # The completed trial has initial + 1 iteration + final(reused on accept) evidence
    assert analysis["evidence_artifacts"] >= 1
    # Successful evaluations should produce evidence artifacts
    assert analysis["successful_oracle_evaluations"] >= analysis["evidence_artifacts"] - 1  # accept-path final reuses


def test_analysis_planned_denominator():
    trials = [
        _make_trial("T1-Rta-R1", "T1", "Rta", 1, 1, [SDC_T1_VALID_IMPROVED]),
    ]
    analysis = analyze_trials(trials, planned=8)
    assert analysis["planned_trials"] == 8
    assert analysis["total_trials"] == 1