"""Tests for the candidate-validity gate (P172 §5)."""

from harness.candidate_validity import (
    classify_candidate,
    extract_sdc_block,
    VALID_SDC,
    NON_SDC_OUTPUT,
    EMPTY_OUTPUT,
    PROVIDER_FAILURE,
)

from harness import fixtures as fx


def test_valid_sdc_t1():
    assert classify_candidate(fx.SDC_T1_VALID, task_id="T1") == VALID_SDC


def test_valid_sdc_t2_aggressive():
    assert classify_candidate(fx.SDC_T2_AGGRESSIVE, task_id="T2") == VALID_SDC


def test_valid_sdc_with_code_fence():
    fenced = "```sdc\n" + fx.SDC_T1_VALID + "```"
    assert classify_candidate(fenced, task_id="T1") == VALID_SDC


def test_conversational_filler_rejected():
    assert classify_candidate(fx.CONVERSATIONAL_FILLER, task_id="T1") == NON_SDC_OUTPUT


def test_conversational_wrapper_with_sdc_tolerated():
    # Conversational preamble WITH valid SDC commands is tolerated (rule 2)
    assert classify_candidate(fx.CONVERSATIONAL_WITH_SDC, task_id="T1") == VALID_SDC
    block = extract_sdc_block(fx.CONVERSATIONAL_WITH_SDC)
    assert block is not None
    assert "create_clock" in block


def test_empty_output_rejected():
    assert classify_candidate(fx.EMPTY_OUTPUT, task_id="T1") == EMPTY_OUTPUT
    assert classify_candidate(fx.WHITESPACE_OUTPUT, task_id="T1") == EMPTY_OUTPUT


def test_provider_failure_detected():
    assert classify_candidate(fx.PROVIDER_ERROR_OUTPUT, task_id="T1") == PROVIDER_FAILURE


def test_injection_marker_rejected():
    assert classify_candidate(fx.INJECTION_OUTPUT, task_id="T1") == NON_SDC_OUTPUT


def test_missing_task_required_construct_rejected():
    # SDC command present but no create_clock → NON_SDC (vacuous-pass defense)
    no_clock = "set_input_delay -clock clk 1.0 [get_ports data_in]"
    assert classify_candidate(no_clock, task_id="T1") == NON_SDC_OUTPUT


def test_prose_without_commands_rejected():
    prose = "The SDC should include a clock with a period of 10 ns for the clk port."
    assert classify_candidate(prose, task_id="T1") == NON_SDC_OUTPUT


def test_extract_sdc_block_returns_commands_only():
    block = extract_sdc_block(fx.SDC_T1_VALID)
    assert block is not None
    assert block.startswith("create_clock")
    assert "set_input_delay" in block


def test_deterministic():
    r1 = classify_candidate(fx.CONVERSATIONAL_FILLER, task_id="T1")
    r2 = classify_candidate(fx.CONVERSATIONAL_FILLER, task_id="T1")
    assert r1 == r2 == NON_SDC_OUTPUT