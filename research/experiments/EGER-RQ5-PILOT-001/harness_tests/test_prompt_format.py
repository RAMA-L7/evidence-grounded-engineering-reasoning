"""Tests for the P173-R repaired prompt format (file-writing directive)."""

from harness.trial_runner import _build_prompt, _format_sdc_lines
from harness.tasks import get_task


def test_format_sdc_lines_ordinals():
    sdc = (
        "create_clock -name clk -period 10.0 [get_ports clk]\n"
        "set_input_delay -clock clk 1.0 [get_ports data_in]\n"
        "set_output_delay -clock clk 1.0 [get_ports data_out]\n"
    )
    out = _format_sdc_lines(sdc)
    assert out.startswith("First line: create_clock")
    assert "Second line: set_input_delay" in out
    assert "Third line: set_output_delay" in out


def test_format_sdc_lines_empty():
    assert _format_sdc_lines("") == "(empty SDC)"


def test_build_prompt_is_file_writing_directive():
    task = get_task("T1")
    prompt = _build_prompt(task["design_context"], task["initial_sdc"], [], "Rta")
    assert "Write the file timing.sdc" in prompt
    assert "create_clock" in prompt
    assert "Overwrite the file" in prompt
    # No verbose role preamble (which switches the model to chat mode)
    assert "You are an SDC" not in prompt
    assert "OUTPUT RULES" not in prompt


def test_build_prompt_includes_feedback_after_iteration():
    task = get_task("T2")
    iterations = [
        {
            "oracle_result": {"is_success": True, "wns": -0.10},
        }
    ]
    prompt = _build_prompt(task["design_context"], task["initial_sdc"], iterations, "OpenSTA")
    assert "Oracle feedback" in prompt
    assert "wns" in prompt


def test_build_prompt_keeps_task_required_construct():
    task = get_task("T1")
    prompt = _build_prompt(task["design_context"], task["initial_sdc"], [], "Rta")
    # The prompt instructs the SDC to include the required commands
    assert "set_input_delay" in prompt
    assert "set_output_delay" in prompt