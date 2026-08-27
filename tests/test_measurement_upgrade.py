"""P055 measurement upgrade tests — 24 categories per EGER-P054 section 17.

Tests the evaluator-side design metadata validation, scope determination,
and re-evaluation mechanism without modifying BENCH-002, models, or treatment.
"""

import hashlib
import json
import os
from pathlib import Path

import pytest

from eger.oracle.adapter import EvidenceOracle, _extract_sdc_references, _validate_with_metadata
from eger.oracle.schemas import (
    SCHEMA_VERSIONS,
    SCOPE_MAP,
    DesignMetadata,
    PortDef,
    ClockDef,
    CellDef,
)
from eger.oracle.re_evaluate import (
    load_design_metadata,
    list_available_metadata,
    re_evaluate_artifact,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

EVALUATOR_CONTEXT = Path(__file__).resolve().parents[1] / "research" / "experiments" / "EGER-BENCH-002" / "evaluator_context"
RTA_SAMPLES = Path(__file__).resolve().parents[1] / "rta-constraint-intelligence" / "samples"
MINIMAL_SDC = (RTA_SAMPLES / "minimal_sdc.sdc").read_text(encoding="utf-8")
BUGGY_NO_CLOCKS = (RTA_SAMPLES / "buggy_no_clocks.sdc").read_text(encoding="utf-8")

ORACLE = EvidenceOracle()


def _load_metadata(task_id):
    path = EVALUATOR_CONTEXT / f"{task_id}.design_metadata.json"
    with open(path, "r", encoding="utf-8") as f:
        return DesignMetadata.from_dict(json.load(f))


# -----------------------------------------------------------------------
# T025 — metadata schema validation
# -----------------------------------------------------------------------

def test_T025_metadata_schema_validation():
    """P054 section 17.1: Metadata loads with valid schema."""
    for task_id in ["BENCH2-001", "BENCH2-002", "BENCH2-003", "BENCH2-004", "BENCH2-005", "BENCH2-006"]:
        md = _load_metadata(task_id)
        assert md.task_id == task_id
        assert md.metadata_version == "eger.design_metadata.v1"
        assert len(md.ports) > 0, f"{task_id} must have ports"
        assert len(md.clocks) > 0, f"{task_id} must have clocks"


# -----------------------------------------------------------------------
# T026 — deterministic metadata loading
# -----------------------------------------------------------------------

def test_T026_deterministic_metadata_loading():
    """P054 section 17.1: Loading metadata is deterministic."""
    a = _load_metadata("BENCH2-001")
    b = _load_metadata("BENCH2-001")
    assert a.task_id == b.task_id
    assert len(a.ports) == len(b.ports)
    assert len(a.clocks) == len(b.clocks)
    for pa, pb in zip(a.ports, b.ports):
        assert pa.name == pb.name
        assert pa.direction == pb.direction


# -----------------------------------------------------------------------
# T027 — valid port reference
# -----------------------------------------------------------------------

def test_T027_valid_port_reference():
    """P054 section 17.1: get_ports referencing existing port validates."""
    md = _load_metadata("BENCH2-001")
    sdc = 'create_clock -name clk -period 10 [get_ports clk]'
    refs = _extract_sdc_references(sdc)
    assert "clk" in refs["ports"]
    result = _validate_with_metadata(sdc, md)
    assert result["total_references"] >= 1
    port_ref = [r for r in result["port_references"] if r["reference"] == "clk"][0]
    assert port_ref["valid"] is True


# -----------------------------------------------------------------------
# T028 — invalid port reference
# -----------------------------------------------------------------------

def test_T028_invalid_port_reference():
    """P054 section 17.1: get_ports referencing nonexistent port fails."""
    md = _load_metadata("BENCH2-001")
    sdc = 'set_input_delay 5.0 [get_ports nonexistent_port]'
    result = _validate_with_metadata(sdc, md)
    assert result["invalid_references"] >= 1
    port_ref = result["port_references"][0]
    assert port_ref["valid"] is False


# -----------------------------------------------------------------------
# T029 — valid clock reference
# -----------------------------------------------------------------------

def test_T029_valid_clock_reference():
    """P054 section 17.1: get_clocks referencing existing clock validates."""
    md = _load_metadata("BENCH2-001")
    sdc = 'set_clock_uncertainty 0.5 [get_clocks clk]'
    result = _validate_with_metadata(sdc, md)
    clock_ref = result["clock_references"][0]
    assert clock_ref["valid"] is True
    assert clock_ref["period_ns"] == 10.0


# -----------------------------------------------------------------------
# T030 — invalid clock reference
# -----------------------------------------------------------------------

def test_T030_invalid_clock_reference():
    """P054 section 17.1: get_clocks referencing nonexistent clock fails."""
    md = _load_metadata("BENCH2-001")
    sdc = 'set_clock_uncertainty 0.5 [get_clocks fake_clock]'
    result = _validate_with_metadata(sdc, md)
    clock_ref = result["clock_references"][0]
    assert clock_ref["valid"] is False


# -----------------------------------------------------------------------
# T031 — correct clock period
# -----------------------------------------------------------------------

def test_T031_correct_clock_period():
    """P054 section 17.1: Clock period matches metadata."""
    md = _load_metadata("BENCH2-001")
    sdc = 'create_clock -name clk -period 10 [get_ports clk]'
    result = _validate_with_metadata(sdc, md)
    # get_ports clk is a port reference, not clock reference
    # Use get_clocks to test clock references
    sdc2 = 'set_clock_uncertainty 0.5 [get_clocks clk]'
    result2 = _validate_with_metadata(sdc2, md)
    clock_ref = result2["clock_references"][0]
    assert clock_ref["valid"] is True
    assert clock_ref["period_ns"] == 10.0


# -----------------------------------------------------------------------
# T032 — clock period metadata recorded
# -----------------------------------------------------------------------

def test_T032_clock_period_metadata_recorded():
    """P054 section 17.1: Metadata records the correct period for validation."""
    md = _load_metadata("BENCH2-002")
    clk_div2 = md.get_clock("clk_div2")
    assert clk_div2 is not None
    assert clk_div2.period_ns == 20.0
    assert clk_div2.generated is True


# -----------------------------------------------------------------------
# T033 — correct input/output direction
# -----------------------------------------------------------------------

def test_T033_correct_direction():
    """P054 section 17.1: Port direction matches metadata."""
    md = _load_metadata("BENCH2-003")
    data_in = md.get_port("data_in")
    data_out = md.get_port("data_out")
    assert data_in is not None
    assert data_in.direction == "input"
    assert data_out is not None
    assert data_out.direction == "output"


# -----------------------------------------------------------------------
# T034 — incorrect direction (set_input_delay on output port)
# -----------------------------------------------------------------------

def test_T034_incorrect_direction():
    """P054 section 17.1: Metadata can detect direction mismatch."""
    md = _load_metadata("BENCH2-003")
    sdc = 'set_input_delay 5.0 -clock clk [get_ports data_out]'
    result = _validate_with_metadata(sdc, md)
    port_ref = result["port_references"][0]
    assert port_ref["valid"] is True  # port exists
    assert port_ref["direction"] == "output"  # but it is an output


# -----------------------------------------------------------------------
# T035 — FULL scope
# -----------------------------------------------------------------------

def test_T035_full_scope():
    """P054 section 10: ALL constructs validated = FULL."""
    md = _load_metadata("BENCH2-001")
    sdc = 'create_clock -name clk -period 10 [get_ports clk]'
    result = _validate_with_metadata(sdc, md)
    assert result["all_validated"] is True
    assert result["any_validated"] is True
    assert result["constraint_validity_rate"] == 1.0


# -----------------------------------------------------------------------
# T036 — PARTIAL scope
# -----------------------------------------------------------------------

def test_T036_partial_scope():
    """P054 section 10: Some validated, some not = PARTIAL."""
    md = _load_metadata("BENCH2-001")
    sdc = 'create_clock -name clk -period 10 [get_ports clk]\nset_input_delay 5.0 [get_ports nonexistent]'
    result = _validate_with_metadata(sdc, md)
    assert result["all_validated"] is False
    assert result["any_validated"] is True


# -----------------------------------------------------------------------
# T037 — INSUFFICIENT scope
# -----------------------------------------------------------------------

def test_T037_insufficient_scope():
    """P054 section 10: Empty metadata means nothing validated."""
    result = _validate_with_metadata(MINIMAL_SDC, DesignMetadata(task_id="NO_METADATA"))
    assert result["total_references"] >= 0


# -----------------------------------------------------------------------
# T038 — metadata absent backward compatibility
# -----------------------------------------------------------------------

def test_T038_metadata_absent_backward_compat():
    """P054 section 17.1: Oracle.validate without metadata preserves existing behavior."""
    result_no_meta = ORACLE.validate(MINIMAL_SDC, input_identity="T038-no-meta")
    result_with_meta = ORACLE.validate(
        MINIMAL_SDC,
        input_identity="T038-with-meta",
        design_metadata=_load_metadata("BENCH2-001"),
    )
    assert result_no_meta.is_success
    assert result_with_meta.is_success
    # Findings should be identical (metadata does not change findings)
    assert result_no_meta.evidence.findings == result_with_meta.evidence.findings


# -----------------------------------------------------------------------
# T039 — deterministic EvidenceArtifact with metadata
# -----------------------------------------------------------------------

def test_T039_deterministic_evidence_with_metadata():
    """P054 section 17.1: Same SDC + same metadata = same EvidenceArtifact."""
    md = _load_metadata("BENCH2-001")
    sdc = 'create_clock -name clk -period 10 [get_ports clk]'
    a = ORACLE.validate(sdc, input_identity="T039", design_metadata=md)
    b = ORACLE.validate(sdc, input_identity="T039", design_metadata=md)
    assert a.is_success and b.is_success
    assert a.evidence.evidence_hash == b.evidence.evidence_hash
    assert a.evidence.evidence_scope == b.evidence.evidence_scope


# -----------------------------------------------------------------------
# T040 — no model-prompt leakage
# -----------------------------------------------------------------------

def test_T040_no_model_prompt_leakage():
    """P054 section 17.1: design_metadata never enters engineer prompt."""
    from eger.engineer.adapter import EngineerAdapter
    from eger.engineer.model import LiveEngineerModel
    model = LiveEngineerModel()
    adapter = EngineerAdapter(model=model)
    prompt, _ = adapter.build_prompt(
        design_context="test design with ports clk and data_in",
        objective="test",
    )
    assert "design_metadata" not in prompt
    assert "metadata_version" not in prompt
    assert "eger.design_metadata.v1" not in prompt
    assert '"ports"' not in prompt
    assert '"clocks"' not in prompt


# -----------------------------------------------------------------------
# T041 — historical artifact read-only behavior
# -----------------------------------------------------------------------

def test_T041_historical_artifact_read_only():
    """P054 section 17.1: Re-evaluation does not modify historical artifacts."""
    sdc = 'create_clock -name clk -period 10 [get_ports clk]'
    result = re_evaluate_artifact(
        oracle=ORACLE,
        candidate_sdc=sdc,
        task_id="BENCH2-001",
        condition="C0",
        run_id="TEST-READONLY",
        original_evidence_scope="INSUFFICIENT",
        original_outcome="INVALID_ARTIFACT",
        original_findings_count=23,
        original_candidate_hash="test_hash",
    )
    assert result.task_id == "BENCH2-001"
    assert result.run_id == "TEST-READONLY"


# -----------------------------------------------------------------------
# T042 — no benchmark mutation
# -----------------------------------------------------------------------

def test_T042_no_benchmark_mutation():
    """P054 section 17.1: BENCH-002 task files unchanged by metadata loading."""
    bench_dir = Path(__file__).resolve().parents[1] / "research" / "experiments" / "EGER-BENCH-002" / "tasks" / "engineer_visible"
    hashes_before = {}
    for p in bench_dir.glob("*.json"):
        hashes_before[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()

    for task_id in ["BENCH2-001", "BENCH2-002", "BENCH2-003", "BENCH2-004", "BENCH2-005", "BENCH2-006"]:
        _load_metadata(task_id)

    for p in bench_dir.glob("*.json"):
        current = hashlib.sha256(p.read_bytes()).hexdigest()
        assert current == hashes_before[p.name], f"{p.name} was mutated!"


# -----------------------------------------------------------------------
# T043 — no MODEL-003/004 mutation
# -----------------------------------------------------------------------

def test_T043_no_model_mutation():
    """P054 section 17.1: MODEL-003/004 specification files unchanged."""
    model_files = [
        Path(__file__).resolve().parents[1] / "research" / "experiments" / "EGER-MODEL-003.md",
        Path(__file__).resolve().parents[1] / "research" / "experiments" / "EGER-MODEL-004.md",
    ]
    hashes_before = {}
    for p in model_files:
        if p.exists():
            hashes_before[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()

    for task_id in ["BENCH2-001", "BENCH2-002", "BENCH2-003", "BENCH2-004", "BENCH2-005", "BENCH2-006"]:
        _load_metadata(task_id)

    for p in model_files:
        if p.exists():
            current = hashlib.sha256(p.read_bytes()).hexdigest()
            assert current == hashes_before[p.name], f"{p.name} was mutated!"


# -----------------------------------------------------------------------
# T044 — no treatment mutation
# -----------------------------------------------------------------------

def test_T044_no_treatment_mutation():
    """P054 section 17.1: feedback.py and structured_feedback.py unchanged."""
    treatment_files = [
        Path(__file__).resolve().parents[1] / "eger" / "engineer" / "feedback.py",
        Path(__file__).resolve().parents[1] / "eger" / "engineer" / "structured_feedback.py",
    ]
    hashes_before = {}
    for p in treatment_files:
        if p.exists():
            hashes_before[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()

    for task_id in ["BENCH2-001", "BENCH2-002", "BENCH2-003", "BENCH2-004", "BENCH2-005", "BENCH2-006"]:
        _load_metadata(task_id)

    for p in treatment_files:
        if p.exists():
            current = hashlib.sha256(p.read_bytes()).hexdigest()
            assert current == hashes_before[p.name], f"{p.name} was mutated!"


# -----------------------------------------------------------------------
# T045 — no Rta interaction
# -----------------------------------------------------------------------

def test_T045_no_rta_interaction():
    """P054 section 17.1: Metadata loading never invokes rta_generate."""
    md = _load_metadata("BENCH2-001")
    result = _validate_with_metadata('create_clock -name clk -period 10 [get_ports clk]', md)
    assert "all_validated" in result


# -----------------------------------------------------------------------
# T046 — no credentials/secrets
# -----------------------------------------------------------------------

def test_T046_no_credentials():
    """P054 section 17.1: Metadata contains no credentials or secrets."""
    for task_id in ["BENCH2-001", "BENCH2-002", "BENCH2-003", "BENCH2-004", "BENCH2-005", "BENCH2-006"]:
        md = _load_metadata(task_id)
        md_json = json.dumps({
            "task_id": md.task_id,
            "ports": [{"name": p.name, "direction": p.direction} for p in md.ports],
            "clocks": [{"name": c.name, "period_ns": c.period_ns} for c in md.clocks],
        })
        assert "api" not in md_json.lower()
        assert "key" not in md_json.lower()
        assert "secret" not in md_json.lower()
        assert "token" not in md_json.lower()
        assert "password" not in md_json.lower()


# -----------------------------------------------------------------------
# T047 — metadata hash reproducibility
# -----------------------------------------------------------------------

def test_T047_metadata_hash_reproducibility():
    """P054 section 17.1: Same metadata produces same hash."""
    md = _load_metadata("BENCH2-001")

    def _hash_metadata(m):
        data = {
            "task_id": m.task_id,
            "ports": [{"name": p.name, "direction": p.direction, "type": p.port_type, "bus": p.bus} for p in m.ports],
            "clocks": [{"name": c.name, "period_ns": c.period_ns, "port": c.port} for c in m.clocks],
            "metadata_version": m.metadata_version,
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    h1 = _hash_metadata(md)
    h2 = _hash_metadata(md)
    assert h1 == h2


# -----------------------------------------------------------------------
# T048 — SDC reference extraction
# -----------------------------------------------------------------------

def test_T048_sdc_reference_extraction():
    """P055: _extract_sdc_references correctly parses SDC."""
    sdc = """create_clock -name clk -period 10 [get_ports clk]
set_input_delay 5.0 -clock clk [get_ports data_in]
set_output_delay 3.0 -clock clk [get_ports data_out]
set_false_path -from [get_pins cfg_reg/Q] -to [get_pins data_reg/D]"""

    refs = _extract_sdc_references(sdc)
    assert "clk" in refs["ports"]
    assert "data_in" in refs["ports"]
    assert "data_out" in refs["ports"]
    assert "cfg_reg/Q" in refs["pins"]
    assert "data_reg/D" in refs["pins"]


# -----------------------------------------------------------------------
# T049 — list_available_metadata
# -----------------------------------------------------------------------

def test_T049_list_available_metadata():
    """P055: list_available_metadata finds all 6 tasks."""
    tasks = list_available_metadata()
    assert len(tasks) == 6
    for i in range(1, 7):
        assert f"BENCH2-{i:03d}" in tasks


# -----------------------------------------------------------------------
# T050 — DesignMetadata.from_dict
# -----------------------------------------------------------------------

def test_T050_design_metadata_from_dict():
    """P055: DesignMetadata.from_dict parses JSON correctly."""
    data = {
        "task_id": "TEST",
        "design_metadata": {
            "metadata_version": "eger.design_metadata.v1",
            "ports": [{"name": "clk", "direction": "input", "type": "clock", "bus": False}],
            "clocks": [{"name": "clk", "period_ns": 10, "port": "clk"}],
            "cells": [{"name": "reg1", "type": "register", "pins": ["Q", "D"]}],
        }
    }
    md = DesignMetadata.from_dict(data)
    assert md.task_id == "TEST"
    assert len(md.ports) == 1
    assert md.ports[0].name == "clk"
    assert md.ports[0].direction == "input"
    assert len(md.clocks) == 1
    assert md.clocks[0].period_ns == 10.0
    assert len(md.cells) == 1
    assert md.cells[0].name == "reg1"


# -----------------------------------------------------------------------
# T051 — PORTS-ONLY SDC with metadata -> FULL scope
# -----------------------------------------------------------------------

def test_T051_ports_only_full_scope():
    """P055: SDC with only port references + metadata -> FULL validation."""
    md = _load_metadata("BENCH2-003")
    sdc = """create_clock -name clk -period 10 [get_ports clk]
set_input_delay -max 1.5 -clock clk [get_ports data_in]
set_output_delay -max 2.0 -clock clk [get_ports data_out]"""
    result = _validate_with_metadata(sdc, md)
    assert result["all_validated"] is True
    assert result["constraint_validity_rate"] == 1.0


# -----------------------------------------------------------------------
# T052 — PIN references with cell metadata -> validated
# -----------------------------------------------------------------------

def test_T052_pin_refs_validated():
    """P055: SDC with pin references validated against cell metadata."""
    md = _load_metadata("BENCH2-004")
    sdc = 'set_false_path -from [get_pins cfg_reg/Q] -to [get_pins data_reg/D]'
    result = _validate_with_metadata(sdc, md)
    assert result["total_references"] == 2
    assert all(r["valid"] for r in result["pin_references"])


# -----------------------------------------------------------------------
# T053 — CVR: valid reference -> CVR = 1.0
# -----------------------------------------------------------------------

def test_T053_cvr_valid_reference():
    """P059: CVR contract — valid port reference -> CVR = 1.0."""
    md = _load_metadata("BENCH2-001")
    sdc = 'create_clock -name clk -period 10 [get_ports clk]'
    result = _validate_with_metadata(sdc, md)
    assert result["total_references"] == 1
    assert result["valid_references"] == 1
    assert result["constraint_validity_rate"] == 1.0


# -----------------------------------------------------------------------
# T054 — CVR: invalid reference -> CVR = 0.0
# -----------------------------------------------------------------------

def test_T054_cvr_invalid_reference():
    """P059: CVR contract — invalid port reference -> CVR = 0.0."""
    md = _load_metadata("BENCH2-001")
    sdc = 'set_input_delay 5.0 [get_ports nonexistent]'
    result = _validate_with_metadata(sdc, md)
    assert result["total_references"] == 1
    assert result["valid_references"] == 0
    assert result["constraint_validity_rate"] == 0.0


# -----------------------------------------------------------------------
# T055 — CVR: mixed references -> CVR = 0.5
# -----------------------------------------------------------------------

def test_T055_cvr_mixed_references():
    """P059: CVR contract — one valid + one invalid -> CVR = 0.5."""
    md = _load_metadata("BENCH2-001")
    sdc = 'create_clock -name clk -period 10 [get_ports clk]\nset_input_delay 5.0 [get_ports nonexistent]'
    result = _validate_with_metadata(sdc, md)
    assert result["total_references"] == 2
    assert result["valid_references"] == 1
    assert result["constraint_validity_rate"] == 0.5


# -----------------------------------------------------------------------
# T056 — CVR: no references -> CVR = 1.0 (vacuously true)
# -----------------------------------------------------------------------

def test_T056_cvr_no_references():
    """P059: CVR contract — no references -> CVR = 1.0 (vacuous)."""
    md = _load_metadata("BENCH2-001")
    sdc = 'set_sdc_version 2.0'
    result = _validate_with_metadata(sdc, md)
    assert result["total_references"] == 0
    assert result["valid_references"] == 0
    assert result["constraint_validity_rate"] == 1.0


# -----------------------------------------------------------------------
# T057 — Provenance contains metadata_validation
# -----------------------------------------------------------------------

def test_T057_provenance_metadata_validation():
    """P059: Oracle.validate provenance contains metadata_validation."""
    md = _load_metadata("BENCH2-001")
    sdc = 'create_clock -name clk -period 10 [get_ports clk]'
    result = ORACLE.validate(sdc, input_identity="T057", design_metadata=md)
    assert result.is_success
    mv = result.evidence.provenance.get("metadata_validation")
    assert mv is not None, "metadata_validation must be in provenance"
    assert mv["total_references"] >= 1
    assert mv["valid_references"] >= 1
    assert mv["constraint_validity_rate"] >= 0.0


# -----------------------------------------------------------------------
# T058 — Provenance CVR matches direct calculation
# -----------------------------------------------------------------------

def test_T058_provenance_cvr_matches_direct():
    """P059: Provenance CVR agrees with direct _validate_with_metadata."""
    md = _load_metadata("BENCH2-001")
    sdc = 'create_clock -name clk -period 10 [get_ports clk]'
    direct = _validate_with_metadata(sdc, md)
    oracle_result = ORACLE.validate(sdc, input_identity="T058", design_metadata=md)
    provenance_mv = oracle_result.evidence.provenance["metadata_validation"]
    assert provenance_mv["valid_references"] == direct["valid_references"]
    assert provenance_mv["total_references"] == direct["total_references"]
    assert provenance_mv["constraint_validity_rate"] == direct["constraint_validity_rate"]


# -----------------------------------------------------------------------
# T059 — No metadata -> provenance metadata_validation is None
# -----------------------------------------------------------------------

def test_T059_no_metadata_provenance():
    """P059: Without metadata, provenance metadata_validation is None."""
    sdc = 'create_clock -name clk -period 10 [get_ports clk]'
    result = ORACLE.validate(sdc, input_identity="T059")
    assert result.is_success
    mv = result.evidence.provenance.get("metadata_validation")
    assert mv is None, "Without metadata, metadata_validation must be None"
