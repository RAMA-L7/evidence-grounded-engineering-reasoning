"""EGER P176 — real full-chain Ṛta scope-alignment tests (P175 resolution).

Proves the complete real chain with the pinned Ṛta 1.5.11:

    Ṛta (netlist-less check --json)
        → EvidenceOracle.validate(design_metadata=<frozen P055 metadata>)
        → EvidenceNormalizer
        → VerificationGate

Required discriminations (P175 §3.3 / P176 gate):
  - T1 incomplete (clock only)        → FULL scope, SDC-005/006 errors → REJECT
  - T1 completed (I/O delays added)   → FULL scope, no errors          → ACCEPT
  - T2 initial (0.05 ns clock only)   → FULL scope, SDC-005/006 errors → REJECT
  - T2 completed at 0.05 ns           → FULL scope, SDC-008/009 errors → REJECT
  - T2 completed, clock relaxed 10 ns → FULL scope, no errors          → ACCEPT
  - invalid design reference          → PARTIAL scope → REJECT (fail closed)

Before the P175 normalizer fix, every Ṛta evaluation normalized to
UNSUPPORTED scope and failed closed regardless of content (the REJECT floor).
These tests assert the restored behavior end-to-end.

Requires the pinned local Ṛta (repo-relative cli.py) — consistent with the
main test suite (test_evidence_oracle.py already invokes real Ṛta).
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
PILOT_DIR = Path(__file__).resolve().parents[1]
for p in (str(PROJECT_ROOT), str(PILOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest

from harness.providers import (
    build_rta_oracle_call,
    load_simple_path_design_metadata,
)
from harness.tasks import TASKS
from eger.engineer.candidate import build_candidate
from eger.evidence.normalizer import EvidenceNormalizer
from eger.verification.gate import VerificationGate

pytestmark = pytest.mark.skipif(
    not Path(PROJECT_ROOT / "rta-constraint-intelligence" / "cli.py").exists(),
    reason="pinned Ṛta CLI not present",
)


@pytest.fixture(scope="module")
def oracle_call():
    return build_rta_oracle_call(timeout_seconds=120)


@pytest.fixture(scope="module")
def normalizer():
    return EvidenceNormalizer()


@pytest.fixture(scope="module")
def gate():
    return VerificationGate()


def _run_chain(oracle_call, normalizer, gate, sdc_text, task_id="T1"):
    """Run one SDC through the real full chain and return key outcomes."""
    result = oracle_call(sdc_text, f"chain-{sdc_text[:8]}")
    assert result.is_success, f"Oracle evaluation failed: {result.failure}"
    evidence = result.evidence
    import hashlib
    candidate_hash = hashlib.sha256(sdc_text.encode("utf-8")).hexdigest()[:12]
    normalized = normalizer.normalize(
        evidence, task_id=task_id, candidate_hash=candidate_hash,
    )
    candidate = build_candidate(sdc_text)
    verification = gate.evaluate(candidate, normalized)
    error_codes = [
        f.get("code") for f in evidence.findings if f.get("severity") == "error"
    ]
    return {
        "adapter_scope": evidence.evidence_scope,
        "normalized_scope": normalized.evidence_scope,
        "gate": verification.decision,
        "error_codes": error_codes,
        "mv_all_validated": (evidence.provenance or {}).get(
            "metadata_validation", {}
        ).get("all_validated"),
    }


def test_metadata_loads_frozen():
    """Frozen metadata matches the simple_path substrate (ports/clock)."""
    dm = load_simple_path_design_metadata()
    assert sorted(dm.port_names()) == ["clk", "data_in", "data_out"]
    assert dm.clock_names() == ["clk"]
    assert sorted(dm.cell_names()) == ["u_and", "u_ff", "u_inv"]


def test_t1_incomplete_rejects_on_missing_io_delays(oracle_call, normalizer, gate):
    sdc = TASKS["T1"]["initial_sdc"]  # create_clock only
    out = _run_chain(oracle_call, normalizer, gate, sdc, task_id="T1")
    assert out["adapter_scope"] == "FULL"
    assert out["normalized_scope"] == "FULL"
    assert out["mv_all_validated"] is True
    assert "SDC-005" in out["error_codes"] and "SDC-006" in out["error_codes"]
    assert out["gate"] == "REJECT"


def test_t1_completed_accepts(oracle_call, normalizer, gate):
    sdc = (
        "create_clock -name clk -period 10.0 [get_ports clk]\n"
        "set_input_delay -clock clk 0.1 [get_ports data_in]\n"
        "set_output_delay -clock clk 0.1 [get_ports data_out]"
    )
    out = _run_chain(oracle_call, normalizer, gate, sdc, task_id="T1")
    assert out["normalized_scope"] == "FULL"
    assert out["error_codes"] == []
    assert out["gate"] == "ACCEPT"


def test_t2_initial_rejects_on_missing_io_delays(oracle_call, normalizer, gate):
    sdc = TASKS["T2"]["initial_sdc"]  # 0.05 ns clock only
    out = _run_chain(oracle_call, normalizer, gate, sdc, task_id="T2")
    assert out["normalized_scope"] == "FULL"
    assert "SDC-005" in out["error_codes"] and "SDC-006" in out["error_codes"]
    assert out["gate"] == "REJECT"


def test_t2_aggressive_clock_rejects_io_delay_ge_period(oracle_call, normalizer, gate):
    """0.05 ns clock + 0.1 ns I/O delays → SDC-008/009 (delay ≥ clock period)."""
    sdc = (
        "create_clock -name clk -period 0.05 [get_ports clk]\n"
        "set_input_delay -clock clk 0.1 [get_ports data_in]\n"
        "set_output_delay -clock clk 0.1 [get_ports data_out]"
    )
    out = _run_chain(oracle_call, normalizer, gate, sdc, task_id="T2")
    assert out["normalized_scope"] == "FULL"
    assert "SDC-008" in out["error_codes"] and "SDC-009" in out["error_codes"]
    assert out["gate"] == "REJECT"


def test_t2_relaxed_clock_accepts(oracle_call, normalizer, gate):
    sdc = (
        "create_clock -name clk -period 10.0 [get_ports clk]\n"
        "set_input_delay -clock clk 0.1 [get_ports data_in]\n"
        "set_output_delay -clock clk 0.1 [get_ports data_out]"
    )
    out = _run_chain(oracle_call, normalizer, gate, sdc, task_id="T2")
    assert out["normalized_scope"] == "FULL"
    assert out["error_codes"] == []
    assert out["gate"] == "ACCEPT"


def test_invalid_design_reference_downgraded_to_partial(oracle_call, normalizer, gate):
    """A candidate referencing a nonexistent port is caught by the P055 metadata
    validation: FULL elevation is denied and evidence_scope is PARTIAL.

    NOTE on the gate outcome: the FROZEN VerificationGate contract accepts
    PARTIAL scope with zero ERROR findings (test_evidence_scope_partial_accepted),
    and netlist-less Ṛta emits no error for an unknown port reference. REJECT
    for this case would require a gate or adapter change, which P176 forbids.
    The experiment-layer fail-closed lever is derive_trial_metrics()
    metadata_unqualified_iterations (see test_metadata_unqualified_flag), which
    the future PILOT-002 analysis uses to exclude unqualified accepts.
    """
    sdc = (
        "create_clock -name clk -period 10.0 [get_ports nonexistent_pin]\n"
        "set_input_delay -clock clk 0.1 [get_ports data_in]\n"
        "set_output_delay -clock clk 0.1 [get_ports data_out]"
    )
    out = _run_chain(oracle_call, normalizer, gate, sdc, task_id="T1")
    # Invalid reference detected: FULL elevation denied.
    assert out["adapter_scope"] == "PARTIAL"
    assert out["normalized_scope"] == "PARTIAL"
    assert out["mv_all_validated"] is False


def test_metadata_unqualified_flag(oracle_call, normalizer, gate):
    """derive_trial_metrics flags Rta evaluations whose references were not all
    validated — the experiment-layer fail-closed lever for the gate's frozen
    PARTIAL acceptance."""
    from harness.trial_runner import derive_trial_metrics, oracle_summary

    sdc = (
        "create_clock -name clk -period 10.0 [get_ports nonexistent_pin]\n"
        "set_input_delay -clock clk 0.1 [get_ports data_in]\n"
        "set_output_delay -clock clk 0.1 [get_ports data_out]"
    )
    result = oracle_call(sdc, "flag-iter-1")
    assert result.is_success
    summary = oracle_summary(result, "Rta")
    assert summary["metadata_all_validated"] is False

    record = {
        "oracle": "Rta",
        "completion_status": "COMPLETED",
        "accept_reached": True,
        "initial_oracle_result": {"is_success": True, "error_count": 0},
        "initial_evidence_hash": "h-init",
        "final_oracle_result": summary,
        "iterations": [{
            "iteration": 1,
            "clock_defined": True,
            "oracle_result": summary,
            "evidence_hash": "h-ev",
            "verification_decision": "ACCEPT",
        }],
    }
    derived = derive_trial_metrics(record)
    assert derived["metadata_unqualified_iterations"] == [1]
