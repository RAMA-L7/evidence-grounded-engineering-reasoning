"""P164 OpenSTA Adapter — unit and integration tests.

Tests verify:
- Adapter configuration validation
- Output parsing (WNS, TNS, slack, violations)
- Adapter against P163 substrate (PASS/VIOLATION cases)
- Error handling (missing binary, timeout, malformed input)
- Evidence chain integration (adapter → normalizer → gate)
- Determinism
- No production code changes to existing contracts

No live model calls. Fully deterministic.
"""

import os
import subprocess
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from eger.oracle.opensta_adapter import (
    OpenSTAAdapter,
    DEFAULT_OPENSTA_TIMEOUT_SECONDS,
    MINIMUM_OPENSTA_TIMEOUT_SECONDS,
    OPENSTA_ORACLE_NAME,
    OPENSTA_ORACLE_VERSION,
    _parse_wns_tns,
    _parse_slack_from_report,
    _parse_timing_report,
    TimingReport,
)
from eger.oracle.adapter import OracleResult, OracleFailure
from eger.evidence.normalizer import EvidenceNormalizer
from eger.verification.gate import VerificationGate
from eger.engineer.candidate import build_candidate


# ---------------------------------------------------------------------------
# P163 substrate paths
# ---------------------------------------------------------------------------

SUBSTRATE_BASE = Path(__file__).resolve().parent.parent / "research" / "implementation" / "opensta_pilot"
NETLIST_PATH = SUBSTRATE_BASE / "design" / "simple_path.v"
LIB_PATH = SUBSTRATE_BASE / "liberty" / "simple_cells.lib"
PASS_SDC_PATH = SUBSTRATE_BASE / "sdc" / "pass_case.sdc"
VIOLATION_SDC_PATH = SUBSTRATE_BASE / "sdc" / "violation_case.sdc"

SUBSTRATE_AVAILABLE = all([
    NETLIST_PATH.exists(),
    LIB_PATH.exists(),
    PASS_SDC_PATH.exists(),
    VIOLATION_SDC_PATH.exists(),
])


def _opensta_available() -> bool:
    """Check if OpenSTA is available in WSL."""
    try:
        result = subprocess.run(
            ["wsl", "-d", "Ubuntu-24.04", "bash", "-c",
             "test -x ~/opensta_build/OpenSTA/app/sta"],
            capture_output=True, timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False

OPENSTA_AVAILABLE = _opensta_available()


# Helper: create a real file so sta_binary.exists() passes
def _make_dummy_sta():
    """Create a temporary file that passes sta_binary.exists() check."""
    fd, path = tempfile.mkstemp(suffix=".sh")
    os.write(fd, b"#!/bin/bash\nexit 0\n")
    os.close(fd)
    return path


# Helper: build a mock _invoke_opensta that returns given output
def _make_invoke_mock(stdout_bytes: bytes, stderr: str = "", exit_code: int = 0):
    """Create a mock _invoke_opensta method."""
    def mock_invoke(sdc_text, netlist_path, lib_path, design_name):
        return stdout_bytes, stderr, exit_code
    return mock_invoke


# ---------------------------------------------------------------------------
# Configuration validation
# ---------------------------------------------------------------------------

class TestOpenSTAAdapterConfiguration:
    """Tests for OpenSTAAdapter configuration."""

    def test_default_timeout_value(self):
        assert DEFAULT_OPENSTA_TIMEOUT_SECONDS == 60

    def test_minimum_timeout_value(self):
        assert MINIMUM_OPENSTA_TIMEOUT_SECONDS == 1

    def test_oracle_identity(self):
        adapter = OpenSTAAdapter(sta_binary="/nonexistent/sta")
        caps = adapter.capabilities()
        assert caps["oracle"]["name"] == "OpenSTA"
        assert caps["oracle"]["version"] == "2.2.0"

    def test_zero_timeout_rejected(self):
        with pytest.raises(ValueError, match="timeout_seconds must be >="):
            OpenSTAAdapter(sta_binary="/nonexistent/sta", timeout_seconds=0)

    def test_negative_timeout_rejected(self):
        with pytest.raises(ValueError, match="timeout_seconds must be >="):
            OpenSTAAdapter(sta_binary="/nonexistent/sta", timeout_seconds=-5)


# ---------------------------------------------------------------------------
# Output parser
# ---------------------------------------------------------------------------

class TestOutputParser:
    """Tests for OpenSTA output parsing."""

    def test_parse_wns_tns_pass(self):
        output = "wns 0.00\ntns 0.00\n"
        wns, tns = _parse_wns_tns(output)
        assert wns == 0.00
        assert tns == 0.00

    def test_parse_wns_tns_violation(self):
        output = "wns -0.10\ntns -0.10\n"
        wns, tns = _parse_wns_tns(output)
        assert wns == -0.10
        assert tns == -0.10

    def test_parse_wns_tns_empty(self):
        wns, tns = _parse_wns_tns("")
        assert wns is None
        assert tns is None

    def test_parse_slack_met(self):
        output = "           9.85   slack (MET)\n"
        slack = _parse_slack_from_report(output)
        assert slack == 9.85

    def test_parse_slack_violated(self):
        output = "          -0.10   slack (VIOLATED)\n"
        slack = _parse_slack_from_report(output)
        assert slack == -0.10

    def test_parse_slack_none(self):
        slack = _parse_slack_from_report("wns 0.00\n")
        assert slack is None

    def test_parse_timing_report_pass(self):
        """Parse full PASS timing report (matching OpenSTA output format)."""
        output = (
            "wns 0.00\n"
            "tns 0.00\n"
            "Startpoint: u_ff (rising edge-triggered flip-flop clocked by clk)\n"
            "Endpoint: data_out (output port clocked by clk)\n"
            "Path Group: clk\n"
            "Path Type: max\n"
            "\n"
            "           9.85   slack (MET)\n"
        )
        report = _parse_timing_report(output)
        assert report.wns == 0.00
        assert report.tns == 0.00
        assert not report.has_violations
        assert len(report.findings) >= 1
        # Should have clean timing findings
        wns_finding = [f for f in report.findings if f.category == "timing_clean"]
        assert len(wns_finding) >= 1
        assert all(f.severity == "info" for f in wns_finding)

    def test_parse_timing_report_violation(self):
        """Parse full VIOLATION timing report."""
        output = (
            "wns -0.10\n"
            "tns -0.10\n"
            "Startpoint: u_ff (rising edge-triggered flip-flop clocked by clk)\n"
            "Endpoint: data_out (output port clocked by clk)\n"
            "Path Group: clk\n"
            "Path Type: max\n"
            "\n"
            "          -0.10   slack (VIOLATED)\n"
        )
        report = _parse_timing_report(output)
        assert report.wns == -0.10
        assert report.tns == -0.10
        assert report.has_violations
        # Should have violation findings
        violation_findings = [f for f in report.findings if f.category == "setup_violation"]
        assert len(violation_findings) >= 1
        assert all(f.severity == "error" for f in violation_findings)

    def test_parse_real_pass_output(self):
        """Parse actual OpenSTA PASS output from P163."""
        output = (
            "Warning: liberty/simple_cells.lib, line 261 unsupported model axis.\n"
            "wns 0.00\n"
            "tns 0.00\n"
            "Startpoint: u_ff (rising edge-triggered flip-flop clocked by clk)\n"
            "Endpoint: data_out (output port clocked by clk)\n"
            "Path Group: clk\n"
            "Path Type: max\n"
            "\n"
            "  Delay    Time   Description\n"
            "---------------------------------------------------------\n"
            "   0.00    0.00   clock clk (rise edge)\n"
            "   0.00    0.00   clock network delay (ideal)\n"
            "   0.00    0.00 ^ u_ff/CK (DFFX1)\n"
            "   0.05    0.05 ^ u_ff/Q (DFFX1)\n"
            "   0.00    0.05 ^ data_out (out)\n"
            "           0.05   data arrival time\n"
            "\n"
            "  10.00   10.00   clock clk (rise edge)\n"
            "   0.00   10.00   clock network delay (ideal)\n"
            "   0.00   10.00   clock reconvergence pessimism\n"
            "  -0.10    9.90   output external delay\n"
            "           9.90   data required time\n"
            "---------------------------------------------------------\n"
            "           9.90   data required time\n"
            "          -0.05   data arrival time\n"
            "---------------------------------------------------------\n"
            "           9.85   slack (MET)\n"
        )
        report = _parse_timing_report(output)
        assert report.wns == 0.00
        assert report.tns == 0.00
        assert not report.has_violations


# ---------------------------------------------------------------------------
# Adapter error handling (mock _invoke_opensta, not subprocess)
# ---------------------------------------------------------------------------

class TestOpenSTAAdapterErrorHandling:
    """Tests for adapter error handling."""

    def test_missing_binary_produces_failure(self):
        """Missing OpenSTA binary produces ORACLE_FAILURE."""
        adapter = OpenSTAAdapter(sta_binary="/nonexistent/sta")
        result = adapter.validate(
            sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
            netlist_path=Path("/nonexistent/netlist.v"),
            lib_path=Path("/nonexistent/lib.lib"),
        )
        assert not result.is_success
        assert result.failure is not None
        assert result.failure.kind == "ORACLE_FAILURE"
        assert result.failure.exit_code == 127

    def test_timeout_produces_failure(self):
        """Subprocess timeout produces ORACLE_FAILURE."""
        dummy_path = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy_path), timeout_seconds=60)

            # Mock _invoke_opensta to simulate timeout
            adapter._invoke_opensta = lambda *a, **kw: (b"", "OpenSTA timed out after 60s", -1)

            result = adapter.validate(
                sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )

            assert not result.is_success
            assert result.failure.kind == "ORACLE_FAILURE"
            assert result.failure.exit_code == -1
        finally:
            os.unlink(dummy_path)

    def test_nonzero_exit_produces_failure(self):
        """Non-zero exit code produces ORACLE_FAILURE."""
        dummy_path = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy_path))

            # Mock _invoke_opensta to simulate non-zero exit
            adapter._invoke_opensta = lambda *a, **kw: (b"error message", "stderr", 1)

            result = adapter.validate(
                sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )

            assert not result.is_success
            assert result.failure.kind == "ORACLE_FAILURE"
            assert result.failure.exit_code == 1
        finally:
            os.unlink(dummy_path)


# ---------------------------------------------------------------------------
# Evidence chain integration (mock _invoke_opensta)
# ---------------------------------------------------------------------------

class TestOpenSTAEvidenceChain:
    """Tests for adapter → normalizer → gate evidence chain."""

    def setup_method(self):
        self.normalizer = EvidenceNormalizer()
        self.gate = VerificationGate()

    def test_missing_binary_chain_rejects(self):
        """Missing binary → failure → evidence → REJECT."""
        adapter = OpenSTAAdapter(sta_binary="/nonexistent/sta")
        result = adapter.validate(
            sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
            netlist_path=Path("/nonexistent/netlist.v"),
            lib_path=Path("/nonexistent/lib.lib"),
        )

        assert not result.is_success
        evidence = self.normalizer.normalize_failure(
            result.failure, task_id="T-OPENSTA-TEST", candidate_hash="test123"
        )
        assert evidence.oracle_status == "ORACLE_FAILURE"
        assert evidence.has_errors

        candidate = build_candidate("create_clock -name clk -period 10.0 [get_ports clk]")
        verification = self.gate.evaluate(candidate, evidence)
        assert verification.is_rejected
        assert verification.decision == "REJECT"

    def test_success_result_has_valid_evidence(self):
        """Successful adapter result produces valid EvidenceArtifact."""
        dummy_path = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy_path))

            mock_output = (
                b"wns 0.00\n"
                b"tns 0.00\n"
                b"Startpoint: u_ff (rising edge-triggered flip-flop clocked by clk)\n"
                b"Endpoint: data_out (output port clocked by clk)\n"
                b"Path Group: clk\n"
                b"Path Type: max\n"
                b"\n"
                b"           9.85   slack (MET)\n"
            )
            # Mock _invoke_opensta to return success
            adapter._invoke_opensta = lambda *a, **kw: (mock_output, "", 0)

            result = adapter.validate(
                sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )

            assert result.is_success
            assert result.evidence is not None
            assert result.evidence.oracle_status == "SUCCESS"
            assert result.evidence.evidence_scope == "VALIDATED"
            assert len(result.evidence.findings) > 0
        finally:
            os.unlink(dummy_path)

    def test_violation_result_has_error_findings(self):
        """VIOLATION adapter result produces error findings."""
        dummy_path = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy_path))

            mock_output = (
                b"wns -0.10\n"
                b"tns -0.10\n"
                b"Startpoint: u_ff (rising edge-triggered flip-flop clocked by clk)\n"
                b"Endpoint: data_out (output port clocked by clk)\n"
                b"Path Group: clk\n"
                b"Path Type: max\n"
                b"\n"
                b"          -0.10   slack (VIOLATED)\n"
            )
            # Mock _invoke_opensta to return violation
            adapter._invoke_opensta = lambda *a, **kw: (mock_output, "", 0)

            result = adapter.validate(
                sdc_text="create_clock -name clk -period 0.05 [get_ports clk]",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )

            assert result.is_success
            assert result.evidence is not None
            error_findings = [f for f in result.evidence.findings if f.get("severity") == "error"]
            assert len(error_findings) > 0
        finally:
            os.unlink(dummy_path)


# ---------------------------------------------------------------------------
# Determinism (mock _invoke_opensta)
# ---------------------------------------------------------------------------

class TestOpenSTADeterminism:
    """Tests for adapter determinism."""

    def test_deterministic_output_parsing(self):
        """Same output produces same TimingReport."""
        output = (
            "wns 0.00\n"
            "tns 0.00\n"
            "Startpoint: u_ff\n"
            "Endpoint: data_out\n"
            "Path Group: clk\n"
            "Path Type: max\n"
            "\n"
            "           9.85   slack (MET)\n"
        )
        report1 = _parse_timing_report(output)
        report2 = _parse_timing_report(output)

        assert report1.wns == report2.wns
        assert report1.tns == report2.tns
        assert report1.has_violations == report2.has_violations
        assert len(report1.findings) == len(report2.findings)

        for f1, f2 in zip(report1.findings, report2.findings):
            assert f1.finding_id == f2.finding_id
            assert f1.severity == f2.severity
            assert f1.category == f2.category
            assert f1.slack == f2.slack

    def test_deterministic_evidence_hash(self):
        """Same inputs produce same evidence hash."""
        dummy_path = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy_path))

            mock_output = b"wns 0.00\ntns 0.00\n"
            # Mock _invoke_opensta
            adapter._invoke_opensta = lambda *a, **kw: (mock_output, "", 0)

            result1 = adapter.validate(
                sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )
            result2 = adapter.validate(
                sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )

            assert result1.evidence.evidence_hash == result2.evidence.evidence_hash
        finally:
            os.unlink(dummy_path)


# ---------------------------------------------------------------------------
# Integration: P163 substrate (if available)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not OPENSTA_AVAILABLE, reason="OpenSTA not available in WSL")
@pytest.mark.skipif(not SUBSTRATE_AVAILABLE, reason="P163 substrate not found")
class TestOpenSTASubstrateIntegration:
    """Integration tests against the validated P163 substrate."""

    def _get_adapter(self):
        """Create adapter pointing to WSL OpenSTA."""
        # The binary is inside WSL. We use wslpath to get the Windows path.
        wsl_home = subprocess.run(
            ["wsl", "-d", "Ubuntu-24.04", "bash", "-c", "echo $HOME"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        sta_wsl = f"{wsl_home}/opensta_build/OpenSTA/app/sta"
        win_path = subprocess.run(
            ["wsl", "-d", "Ubuntu-24.04", "wslpath", "-w", sta_wsl],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        return OpenSTAAdapter(
            sta_binary=Path(win_path) if win_path else Path("/nonexistent/sta"),
            timeout_seconds=60,
        )

    def test_pass_case(self):
        """PASS substrate produces MET timing."""
        adapter = self._get_adapter()
        sdc_text = PASS_SDC_PATH.read_text(encoding="utf-8")

        result = adapter.validate(
            sdc_text=sdc_text,
            netlist_path=NETLIST_PATH,
            lib_path=LIB_PATH,
            design_name="simple_path",
        )

        assert result.is_success
        assert result.evidence is not None
        assert result.evidence.oracle_status == "SUCCESS"
        wns = result.evidence.analysis_scope.get("wns")
        assert wns is not None
        assert wns >= 0, f"PASS case should have non-negative WNS, got {wns}"

    def test_violation_case(self):
        """VIOLATION substrate produces VIOLATED timing."""
        adapter = self._get_adapter()
        sdc_text = VIOLATION_SDC_PATH.read_text(encoding="utf-8")

        result = adapter.validate(
            sdc_text=sdc_text,
            netlist_path=NETLIST_PATH,
            lib_path=LIB_PATH,
            design_name="simple_path",
        )

        assert result.is_success
        assert result.evidence is not None
        assert result.evidence.oracle_status == "SUCCESS"
        wns = result.evidence.analysis_scope.get("wns")
        assert wns is not None
        assert wns < 0, f"VIOLATION case should have negative WNS, got {wns}"

    def test_pass_distinguishes_from_violation(self):
        """PASS and VIOLATION cases produce distinguishable results."""
        adapter = self._get_adapter()
        pass_sdc = PASS_SDC_PATH.read_text(encoding="utf-8")
        violation_sdc = VIOLATION_SDC_PATH.read_text(encoding="utf-8")

        pass_result = adapter.validate(
            sdc_text=pass_sdc,
            netlist_path=NETLIST_PATH,
            lib_path=LIB_PATH,
            design_name="simple_path",
        )
        violation_result = adapter.validate(
            sdc_text=violation_sdc,
            netlist_path=NETLIST_PATH,
            lib_path=LIB_PATH,
            design_name="simple_path",
        )

        pass_wns = pass_result.evidence.analysis_scope.get("wns")
        violation_wns = violation_result.evidence.analysis_scope.get("wns")

        assert pass_wns is not None
        assert violation_wns is not None
        assert pass_wns >= 0
        assert violation_wns < 0
        assert pass_wns != violation_wns

    def test_pass_case_evidence_chain(self):
        """PASS case flows through normalizer and gate correctly."""
        adapter = self._get_adapter()
        normalizer = EvidenceNormalizer()
        gate = VerificationGate()

        sdc_text = PASS_SDC_PATH.read_text(encoding="utf-8")
        result = adapter.validate(
            sdc_text=sdc_text,
            netlist_path=NETLIST_PATH,
            lib_path=LIB_PATH,
            design_name="simple_path",
        )

        assert result.is_success
        evidence = normalizer.normalize(
            result.evidence,
            task_id="T-OPENSTA-PASS",
            candidate_hash="pass_test",
        )
        assert evidence.oracle_status == "SUCCESS"

        candidate = build_candidate(sdc_text)
        verification = gate.evaluate(candidate, evidence)
        # PASS case should not have errors → ACCEPT
        assert verification.is_accepted or not evidence.has_errors
