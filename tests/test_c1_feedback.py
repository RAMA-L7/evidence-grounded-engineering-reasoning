"""C1 feedback renderer and runner tests — T-C1-001..T-C1-011.

Tests the deterministic text feedback renderer and C1 pipeline components.
Does NOT execute formal C1 experiments. Uses mocks/stubs where appropriate.
"""

import hashlib
import json
from pathlib import Path
from unittest.mock import MagicMock

from eger.engineer.feedback import render_text_feedback
from eger.oracle.adapter import EvidenceOracle


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_evidence(
    oracle_status: str = "SUCCESS",
    evidence_scope: str = "INSUFFICIENT",
    findings=None,
    analysis_scope=None,
    evidence_hash: str = None,
):
    """Create a minimal EvidenceArtifact-like object for renderer tests."""
    h = evidence_hash or hashlib.sha256(evidence_scope.encode()).hexdigest()
    findings = findings or []
    analysis_scope = analysis_scope or {
        "status": "NETLIST_REQUIRED",
        "normalized_scope": "INSUFFICIENT",
        "commands_found": 2,
        "fully_analyzed": 0,
        "partially_analyzed": 0,
        "netlist_required": 2,
        "unsupported": 0,
    }

    class Ev:
        pass

    ev = Ev()
    ev.oracle_status = oracle_status
    ev.evidence_scope = evidence_scope
    ev.findings = findings
    ev.analysis_scope = analysis_scope
    ev.evidence_hash = h
    ev.artifact_id = f"EGER-EVID-{h[:12]}"
    return ev


# ---------------------------------------------------------------------------
# T-C1-001 — Renderer output structure
# ---------------------------------------------------------------------------

def test_T_C1_001_output_structure():
    """Renderer output contains required sections."""
    ev = _mock_evidence()
    text = render_text_feedback(ev)
    assert "ORACLE RESULT" in text
    assert "Oracle execution:" in text
    assert "EVIDENCE SCOPE" in text
    assert "Scope:" in text
    assert "Scope limitation:" in text


# ---------------------------------------------------------------------------
# T-C1-002 — Deterministic rendering
# ---------------------------------------------------------------------------

def test_T_C1_002_deterministic():
    """Same input → same output, always."""
    ev = _mock_evidence()
    t1 = render_text_feedback(ev)
    t2 = render_text_feedback(ev)
    assert t1 == t2
    assert hashlib.sha256(t1.encode()).hexdigest() == hashlib.sha256(t2.encode()).hexdigest()


# ---------------------------------------------------------------------------
# T-C1-003 — Finding severity ordering
# ---------------------------------------------------------------------------

def test_T_C1_003_severity_ordering():
    """Findings ordered: ERROR → WARNING → INFO."""
    findings = [
        {"finding_id": "F3", "code": "SDC-100", "severity": "info", "message": "info msg", "location": {"line": 0}},
        {"finding_id": "F1", "code": "SDC-005", "severity": "error", "message": "error msg", "location": {"line": 0}},
        {"finding_id": "F2", "code": "SDC-030", "severity": "warning", "message": "warning msg", "location": {"line": 0}},
    ]
    ev = _mock_evidence(findings=findings)
    text = render_text_feedback(ev)
    lines = text.split("\n")
    finding_lines = [l for l in lines if l.startswith("[")]
    assert len(finding_lines) == 3
    assert "[ERROR]" in finding_lines[0]
    assert "[WARNING]" in finding_lines[1]
    assert "[INFO]" in finding_lines[2]


# ---------------------------------------------------------------------------
# T-C1-004 — Finding code ordering
# ---------------------------------------------------------------------------

def test_T_C1_004_code_ordering():
    """Same severity → alphabetical by code."""
    findings = [
        {"finding_id": "F2", "code": "SDC-030", "severity": "warning", "message": "msg2", "location": {"line": 0}},
        {"finding_id": "F1", "code": "SDC-005", "severity": "warning", "message": "msg1", "location": {"line": 0}},
    ]
    ev = _mock_evidence(findings=findings)
    text = render_text_feedback(ev)
    lines = text.split("\n")
    finding_lines = [l for l in lines if l.startswith("[")]
    assert len(finding_lines) == 2
    assert "SDC-005" in finding_lines[0]
    assert "SDC-030" in finding_lines[1]


# ---------------------------------------------------------------------------
# T-C1-005 — Line number rendering
# ---------------------------------------------------------------------------

def test_T_C1_005_line_rendering():
    """Line 0 → 'N/A', positive line → number."""
    findings = [
        {"finding_id": "F1", "code": "SDC-005", "severity": "error", "message": "msg", "location": {"line": 0}},
        {"finding_id": "F2", "code": "SDC-006", "severity": "error", "message": "msg2", "location": {"line": 42}},
    ]
    ev = _mock_evidence(findings=findings)
    text = render_text_feedback(ev)
    assert "Line: N/A" in text
    assert "Line: 42" in text


# ---------------------------------------------------------------------------
# T-C1-006 — INSUFFICIENT scope rendering
# ---------------------------------------------------------------------------

def test_T_C1_006_insufficient_scope():
    """INSUFFICIENT scope renders correctly."""
    ev = _mock_evidence(evidence_scope="INSUFFICIENT")
    text = render_text_feedback(ev)
    assert "Scope: INSUFFICIENT" in text
    assert "Netlist-dependent" in text


# ---------------------------------------------------------------------------
# T-C1-007 — Oracle execution status rendering
# ---------------------------------------------------------------------------

def test_T_C1_007_oracle_status():
    """Oracle status renders correctly for all values."""
    for status in ["SUCCESS", "INVALID_REQUEST", "ORACLE_FAILURE"]:
        ev = _mock_evidence(oracle_status=status)
        text = render_text_feedback(ev)
        assert f"Oracle execution: {status}" in text


# ---------------------------------------------------------------------------
# T-C1-008 — No epistemic-state leakage
# ---------------------------------------------------------------------------

def test_T_C1_008_no_epistemic_leakage():
    """Feedback contains no epistemic state words as fields."""
    ev = _mock_evidence()
    text = render_text_feedback(ev)
    # These words may appear in scope limitation text but NOT as field values
    assert "VALIDATED" not in text.split("Scope:")[1].split("\n")[0] if "Scope:" in text else True
    assert "REFUTED" not in text.split("Scope:")[1].split("\n")[0] if "Scope:" in text else True
    # The word "HYPOTHESIS" should not appear at all
    assert "HYPOTHESIS" not in text


# ---------------------------------------------------------------------------
# T-C1-009 — No authorization leakage
# ---------------------------------------------------------------------------

def test_T_C1_009_no_authorization_leakage():
    """Feedback contains no authorization decisions."""
    ev = _mock_evidence()
    text = render_text_feedback(ev)
    assert "APPROVED" not in text
    assert "REJECTED" not in text
    assert "PERMITTED" not in text


# ---------------------------------------------------------------------------
# T-C1-010 — No evaluator-only leakage
# ---------------------------------------------------------------------------

def test_T_C1_010_no_evaluator_leakage():
    """Feedback contains no evaluator-only data."""
    ev = _mock_evidence()
    text = render_text_feedback(ev)
    # Should not contain expected answer patterns
    assert "expected_artifact_validity" not in text
    assert "expected_findings" not in text
    # Should not contain hash/provenance metadata
    assert "evidence_hash" not in text
    assert "input_hash" not in text
    assert "raw_hash" not in text
    assert "provenance" not in text


# ---------------------------------------------------------------------------
# T-C1-011 — Feedback contains no expected solution
# ---------------------------------------------------------------------------

def test_T_C1_011_no_expected_solution():
    """Feedback does not contain expected SDC solutions."""
    ev = _mock_evidence()
    text = render_text_feedback(ev)
    # Should not contain SDC command suggestions
    assert "create_clock -name clk -period 10" not in text
    assert "set_input_delay" not in text
    assert "set_output_delay" not in text


# ---------------------------------------------------------------------------
# T-C1-012 — Empty findings section
# ---------------------------------------------------------------------------

def test_T_C1_012_empty_findings():
    """No findings → FINDINGS section omitted."""
    ev = _mock_evidence(findings=[])
    text = render_text_feedback(ev)
    assert "FINDINGS" not in text
    # The only section separators are from ORACLE RESULT and EVIDENCE SCOPE
    sections = text.split("\n\n")
    section_names = [s.split("\n")[0] for s in sections if s.strip()]
    assert "FINDINGS" not in section_names


# ---------------------------------------------------------------------------
# T-C1-013 — Multiple findings with mixed severity
# ---------------------------------------------------------------------------

def test_T_C1_013_mixed_findings():
    """Complex finding set renders correctly."""
    findings = [
        {"finding_id": "F4", "code": "SDC-100", "severity": "info", "message": "info", "location": {"line": 0}},
        {"finding_id": "F1", "code": "SDC-005", "severity": "error", "message": "err1", "location": {"line": 0}},
        {"finding_id": "F3", "code": "SDC-030", "severity": "warning", "message": "warn", "location": {"line": 5}},
        {"finding_id": "F2", "code": "SDC-006", "severity": "error", "message": "err2", "location": {"line": 0}},
    ]
    ev = _mock_evidence(findings=findings)
    text = render_text_feedback(ev)
    lines = text.split("\n")
    finding_lines = [l for l in lines if l.startswith("[")]
    assert len(finding_lines) == 4
    # Error first (SDC-005 before SDC-006 alphabetically), then warning, then info
    assert "[ERROR] SDC-005" in finding_lines[0]
    assert "[ERROR] SDC-006" in finding_lines[1]
    assert "[WARNING] SDC-030" in finding_lines[2]
    assert "[INFO] SDC-100" in finding_lines[3]


# ---------------------------------------------------------------------------
# T-C1-014 — Real oracle integration (deterministic rendering)
# ---------------------------------------------------------------------------

def test_T_C1_014_real_oracle_rendering():
    """Real oracle output renders deterministically."""
    oracle = EvidenceOracle()
    sdc = "create_clock -name clk -period 10 [get_ports clk]"
    r1 = oracle.validate(sdc, input_identity="T-C1-014")
    r2 = oracle.validate(sdc, input_identity="T-C1-014")
    assert r1.is_success and r2.is_success
    t1 = render_text_feedback(r1.evidence)
    t2 = render_text_feedback(r2.evidence)
    assert t1 == t2
    # Same evidence_hash → same text
    assert r1.evidence.evidence_hash == r2.evidence.evidence_hash


# ---------------------------------------------------------------------------
# T-C1-015 — No evidence_hash in rendered text
# ---------------------------------------------------------------------------

def test_T_C1_015_no_hash_in_text():
    """Rendered text contains no hash values."""
    ev = _mock_evidence()
    text = render_text_feedback(ev)
    # Hashes are 64-char hex strings — should not appear
    import re
    hashes = re.findall(r'[a-f0-9]{64}', text)
    assert len(hashes) == 0


# ---------------------------------------------------------------------------
# T-C1-016 — Line endings are LF
# ---------------------------------------------------------------------------

def test_T_C1_016_line_endings():
    """Output uses \\n (LF) line endings."""
    ev = _mock_evidence()
    text = render_text_feedback(ev)
    assert "\r\n" not in text
    assert "\r" not in text
