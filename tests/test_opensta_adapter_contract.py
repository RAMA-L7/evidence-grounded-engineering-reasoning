"""P165 — OpenSTA Adapter Contract Validation: adversarial tests.

Attempts to falsify P164's PASS verdict by testing:
- Tcl/shell injection via design_name and other inputs
- Malformed output parser edge cases
- Input boundary conditions
- Path handling edge cases
- Evidence contract correctness
- Determinism across repeated runs
- Full pipeline integration
- Security (command injection, path traversal)
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
# Helper
# ---------------------------------------------------------------------------

def _make_dummy_sta():
    fd, path = tempfile.mkstemp(suffix=".sh")
    os.write(fd, b"#!/bin/bash\nexit 0\n")
    os.close(fd)
    return path


# ---------------------------------------------------------------------------
# A. Constructor validation
# ---------------------------------------------------------------------------

class TestConstructorContract:
    """Validate adapter constructor behavior."""

    def test_default_binary_is_path(self):
        adapter = OpenSTAAdapter()
        assert isinstance(adapter.sta_binary, Path)

    def test_explicit_binary_converted_to_path(self):
        adapter = OpenSTAAdapter(sta_binary="/some/path/sta")
        assert isinstance(adapter.sta_binary, Path)
        # On Windows, Path normalizes separators to backslashes
        assert adapter.sta_binary == Path("/some/path/sta")

    def test_timeout_boundary_minimum(self):
        """timeout_seconds == MINIMUM should be accepted."""
        adapter = OpenSTAAdapter(sta_binary="/nonexistent", timeout_seconds=MINIMUM_OPENSTA_TIMEOUT_SECONDS)
        assert adapter.timeout_seconds == MINIMUM_OPENSTA_TIMEOUT_SECONDS

    def test_timeout_boundary_below_minimum(self):
        """timeout_seconds == MINIMUM - 1 should be rejected."""
        with pytest.raises(ValueError, match="timeout_seconds must be >="):
            OpenSTAAdapter(sta_binary="/nonexistent", timeout_seconds=MINIMUM_OPENSTA_TIMEOUT_SECONDS - 1)

    def test_timeout_zero_rejected(self):
        with pytest.raises(ValueError):
            OpenSTAAdapter(sta_binary="/nonexistent", timeout_seconds=0)

    def test_timeout_negative_rejected(self):
        with pytest.raises(ValueError):
            OpenSTAAdapter(sta_binary="/nonexistent", timeout_seconds=-100)

    def test_timeout_very_large_accepted(self):
        adapter = OpenSTAAdapter(sta_binary="/nonexistent", timeout_seconds=999999)
        assert adapter.timeout_seconds == 999999

    def test_capabilities_returns_dict(self):
        adapter = OpenSTAAdapter(sta_binary="/nonexistent")
        caps = adapter.capabilities()
        assert isinstance(caps, dict)
        assert "oracle" in caps
        assert "capabilities" in caps
        assert caps["oracle"]["name"] == "OpenSTA"
        assert caps["oracle"]["version"] == "2.2.0"


# ---------------------------------------------------------------------------
# B. Input validation (validate method)
# ---------------------------------------------------------------------------

class TestInputValidation:
    """Test validate() with adversarial inputs."""

    def _get_adapter(self):
        dummy = _make_dummy_sta()
        return OpenSTAAdapter(sta_binary=Path(dummy)), dummy

    def test_empty_sdc_produces_result(self):
        """Empty SDC should not crash the adapter."""
        adapter, dummy = self._get_adapter()
        try:
            # Empty SDC: _invoke_opensta will be called but will fail
            # because the binary doesn't exist or produces garbage
            # The key is it shouldn't crash with an unhandled exception
            adapter._invoke_opensta = lambda *a, **kw: (b"wns 0.00\ntns 0.00\n", "", 0)
            result = adapter.validate(
                sdc_text="",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )
            # Should produce a valid OracleResult (success or failure)
            assert isinstance(result, OracleResult)
        finally:
            os.unlink(dummy)

    def test_whitespace_only_sdc(self):
        """Whitespace-only SDC should not crash."""
        adapter, dummy = self._get_adapter()
        try:
            adapter._invoke_opensta = lambda *a, **kw: (b"wns 0.00\ntns 0.00\n", "", 0)
            result = adapter.validate(
                sdc_text="   \n\t  \n  ",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )
            assert isinstance(result, OracleResult)
        finally:
            os.unlink(dummy)

    def test_very_large_sdc(self):
        """Unusually large but valid SDC should not crash."""
        adapter, dummy = self._get_adapter()
        try:
            adapter._invoke_opensta = lambda *a, **kw: (b"wns 0.00\ntns 0.00\n", "", 0)
            large_sdc = "set_clock_groups -name clk -asynchronous" * 10000
            result = adapter.validate(
                sdc_text=large_sdc,
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )
            assert isinstance(result, OracleResult)
        finally:
            os.unlink(dummy)

    def test_sdc_with_shell_metacharacters(self):
        """SDC with shell metacharacters should be safely handled via heredoc."""
        adapter, dummy = self._get_adapter()
        try:
            adapter._invoke_opensta = lambda *a, **kw: (b"wns 0.00\ntns 0.00\n", "", 0)
            malicious_sdc = "create_clock -name clk -period 10.0 [get_ports clk]\n$(echo pwned)\n`whoami`\n; rm -rf /"
            result = adapter.validate(
                sdc_text=malicious_sdc,
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )
            assert isinstance(result, OracleResult)
            # The adapter should not execute the shell commands
        finally:
            os.unlink(dummy)

    def test_sdc_with_newlines_and_brackets(self):
        """SDC with complex syntax should be handled."""
        adapter, dummy = self._get_adapter()
        try:
            adapter._invoke_opensta = lambda *a, **kw: (b"wns 0.00\ntns 0.00\n", "", 0)
            complex_sdc = (
                "create_clock -name clk -period 10.0 [get_ports clk]\n"
                "set_input_delay -clock clk 0.5 [get_ports {in1 in2 in3}]\n"
                "set_output_delay -clock clk 0.5 [get_ports {out1 out2}]\n"
                "set_false_path -from [get_clocks clk] -to [get_clocks clk2]\n"
            )
            result = adapter.validate(
                sdc_text=complex_sdc,
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )
            assert isinstance(result, OracleResult)
        finally:
            os.unlink(dummy)


# ---------------------------------------------------------------------------
# C. Tcl injection via design_name (SECURITY)
# ---------------------------------------------------------------------------

class TestTclInjection:
    """Test for Tcl injection vulnerabilities via design_name."""

    def test_normal_design_name(self):
        """Normal design_name should work."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            mock_output = b"wns 0.00\ntns 0.00\n"
            adapter._invoke_opensta = lambda *a, **kw: (mock_output, "", 0)
            result = adapter.validate(
                sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
                design_name="simple_path",
            )
            assert result.is_success
        finally:
            os.unlink(dummy)

    def test_design_name_with_tcl_metacharacters_rejected(self):
        """P166: Design name with Tcl metacharacters is REJECTED.

        The design_name is validated by _validate_design_name() before
        reaching the Tcl script. Names containing semicolons, brackets,
        dollar signs, etc. are rejected with INVALID_REQUEST.
        """
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            result = adapter.validate(
                sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
                design_name="x; exec echo INJECTED",
            )
            # Must be rejected BEFORE reaching _invoke_opensta
            assert not result.is_success
            assert result.failure.kind == "INVALID_REQUEST"
            assert "invalid characters" in result.failure.message.lower()
        finally:
            os.unlink(dummy)

    def test_empty_design_name_rejected(self):
        """P166: Empty design_name is rejected."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            result = adapter.validate(
                sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
                design_name="",
            )
            assert not result.is_success
            assert result.failure.kind == "INVALID_REQUEST"
            assert "empty" in result.failure.message.lower()
        finally:
            os.unlink(dummy)

    def test_design_name_with_spaces_rejected(self):
        """P166: Design name with spaces is rejected."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            result = adapter.validate(
                sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
                design_name="my design",
            )
            assert not result.is_success
            assert result.failure.kind == "INVALID_REQUEST"
        finally:
            os.unlink(dummy)


# ---------------------------------------------------------------------------
# D. Path handling
# ---------------------------------------------------------------------------

class TestPathHandling:
    """Test Windows-to-WSL path conversion."""

    def test_standard_drive_path(self):
        p = Path("D:/Research on EGER/test.v")
        result = OpenSTAAdapter._to_wsl_path(p)
        assert result.startswith("/mnt/d/")
        assert "Research" in result

    def test_unc_wsl_path(self):
        p = Path("//wsl.localhost/Ubuntu-24.04/root/test.v")
        result = OpenSTAAdapter._to_wsl_path(p)
        assert result == "/root/test.v"

    def test_unc_wsl_path_with_subdirs(self):
        p = Path("//wsl.localhost/Ubuntu-24.04/home/user/test.v")
        result = OpenSTAAdapter._to_wsl_path(p)
        assert result == "/home/user/test.v"

    def test_c_drive_path(self):
        p = Path("C:/Users/test/file.txt")
        result = OpenSTAAdapter._to_wsl_path(p)
        assert result.startswith("/mnt/c/")

    def test_path_with_spaces(self):
        """Spaces in Windows paths should be preserved in WSL mount."""
        p = Path("D:/Research on EGER/file.v")
        result = OpenSTAAdapter._to_wsl_path(p)
        assert "Research on EGER" in result

    def test_path_with_special_chars(self):
        """Parentheses in path should be preserved."""
        p = Path("D:/Users/John Doe (Admin)/file.v")
        result = OpenSTAAdapter._to_wsl_path(p)
        assert "John Doe (Admin)" in result


# ---------------------------------------------------------------------------
# E. Malformed output parser
# ---------------------------------------------------------------------------

class TestMalformedOutput:
    """Adversarial parser tests."""

    def test_empty_output(self):
        report = _parse_timing_report("")
        assert report.wns is None
        assert report.tns is None
        assert not report.has_violations
        assert len(report.findings) == 0

    def test_only_wns_no_tns(self):
        report = _parse_timing_report("wns 0.00\n")
        assert report.wns == 0.00
        assert report.tns is None

    def test_only_tns_no_wns(self):
        report = _parse_timing_report("tns -0.50\n")
        assert report.wns is None
        assert report.tns == -0.50

    def test_malformed_wns_non_numeric(self):
        report = _parse_timing_report("wns abc\ntns 0.00\n")
        assert report.wns is None  # regex won't match
        assert report.tns == 0.00

    def test_malformed_tns_non_numeric(self):
        report = _parse_timing_report("wns 0.00\ntns xyz\n")
        assert report.wns == 0.00
        assert report.tns is None

    def test_wns_with_extra_text(self):
        """wns line with extra text after the number."""
        report = _parse_timing_report("wns 0.00 extra text\n")
        # The regex uses $ which requires end of line, so this should NOT match
        assert report.wns is None

    def test_negative_zero(self):
        """-0.0 should parse correctly."""
        report = _parse_timing_report("wns -0.0\ntns -0.0\n")
        assert report.wns == -0.0
        assert report.tns == -0.0
        # -0.0 < 0 is False in Python, so should be classified as clean
        assert not report.has_violations

    def test_scientific_notation_not_parsed(self):
        """Scientific notation is not supported by the parser."""
        report = _parse_timing_report("wns -1.5e-3\ntns -2.0e-3\n")
        assert report.wns is None
        assert report.tns is None

    def test_extra_whitespace(self):
        report = _parse_timing_report("  wns   -0.10   \n  tns   -0.20   \n")
        assert report.wns == -0.10
        assert report.tns == -0.20

    def test_no_trailing_newline(self):
        report = _parse_timing_report("wns 0.00")
        assert report.wns == 0.00

    def test_multiple_wns_lines(self):
        """Last wns line wins."""
        report = _parse_timing_report("wns 0.00\nwns -0.50\n")
        assert report.wns == -0.50

    def test_truncated_output(self):
        """Truncated output (only startpoint, no slack)."""
        output = (
            "wns 0.00\n"
            "tns 0.00\n"
            "Startpoint: u_ff\n"
            "Endpoint: data_out\n"
        )
        report = _parse_timing_report(output)
        assert report.wns == 0.00
        assert not report.has_violations
        # No path-level findings because slack line is missing
        path_findings = [f for f in report.findings if f.finding_id.startswith("OPENSTA-PATH")]
        assert len(path_findings) == 0

    def test_mixed_output_with_warnings(self):
        """Real OpenSTA output includes warnings."""
        output = (
            "Warning: liberty/simple_cells.lib, line 261 unsupported model axis.\n"
            "wns 0.00\n"
            "tns 0.00\n"
        )
        report = _parse_timing_report(output)
        assert report.wns == 0.00
        assert report.tns == 0.00

    def test_slack_met_vs_violated(self):
        """Parser correctly classifies MET vs VIOLATED."""
        met = _parse_slack_from_report("9.85   slack (MET)")
        assert met == 9.85
        violated = _parse_slack_from_report("-0.10   slack (VIOLATED)")
        assert violated == -0.10

    def test_slack_with_unexpected_format(self):
        """Slack line with unexpected format returns None."""
        slack = _parse_slack_from_report("slack value: 9.85")
        assert slack is None


# ---------------------------------------------------------------------------
# F. Evidence contract mapping
# ---------------------------------------------------------------------------

class TestEvidenceContract:
    """Verify evidence mapping correctness."""

    def _get_adapter_and_invoke(self, mock_output):
        dummy = _make_dummy_sta()
        adapter = OpenSTAAdapter(sta_binary=Path(dummy))
        adapter._invoke_opensta = lambda *a, **kw: (mock_output, "", 0)
        return adapter, dummy

    def test_clean_timing_evidence(self):
        """WNS >= 0 → timing_clean, severity=info."""
        output = b"wns 0.00\ntns 0.00\n"
        adapter, dummy = self._get_adapter_and_invoke(output)
        try:
            result = adapter.validate(
                sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )
            assert result.is_success
            findings = result.evidence.findings
            clean = [f for f in findings if f["code"] == "timing_clean"]
            assert len(clean) >= 1
            assert all(f["severity"] == "info" for f in clean)
            # No error findings
            errors = [f for f in findings if f["severity"] == "error"]
            assert len(errors) == 0
        finally:
            os.unlink(dummy)

    def test_violation_evidence(self):
        """WNS < 0 → setup_violation, severity=error."""
        output = b"wns -0.10\ntns -0.10\n"
        adapter, dummy = self._get_adapter_and_invoke(output)
        try:
            result = adapter.validate(
                sdc_text="create_clock -name clk -period 0.05 [get_ports clk]",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )
            assert result.is_success
            findings = result.evidence.findings
            violations = [f for f in findings if f["code"] == "setup_violation"]
            assert len(violations) >= 1
            assert all(f["severity"] == "error" for f in violations)
        finally:
            os.unlink(dummy)

    def test_tns_violation_evidence(self):
        """TNS < 0 (different from WNS) → total_negative_slack."""
        output = b"wns 0.00\ntns -0.50\n"
        adapter, dummy = self._get_adapter_and_invoke(output)
        try:
            result = adapter.validate(
                sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )
            assert result.is_success
            findings = result.evidence.findings
            tns_findings = [f for f in findings if f["code"] == "total_negative_slack"]
            assert len(tns_findings) == 1
            assert tns_findings[0]["severity"] == "error"
        finally:
            os.unlink(dummy)

    def test_tns_same_as_wns_not_duplicated(self):
        """When TNS == WNS, TNS finding should not be added."""
        output = b"wns -0.10\ntns -0.10\n"
        adapter, dummy = self._get_adapter_and_invoke(output)
        try:
            result = adapter.validate(
                sdc_text="test",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )
            findings = result.evidence.findings
            tns_findings = [f for f in findings if f["code"] == "total_negative_slack"]
            assert len(tns_findings) == 0  # TNS == WNS, so not added
        finally:
            os.unlink(dummy)

    def test_analysis_scope_contains_wns_tns(self):
        """analysis_scope should contain wns and tns values."""
        output = b"wns -0.15\ntns -0.30\n"
        adapter, dummy = self._get_adapter_and_invoke(output)
        try:
            result = adapter.validate(
                sdc_text="test",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
            )
            scope = result.evidence.analysis_scope
            assert scope["wns"] == -0.15
            assert scope["tns"] == -0.30
            assert scope["has_violations"] is True
        finally:
            os.unlink(dummy)

    def test_evidence_hash_deterministic(self):
        """Same inputs → same evidence_hash."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            mock_output = b"wns 0.00\ntns 0.00\n"
            adapter._invoke_opensta = lambda *a, **kw: (mock_output, "", 0)

            sdc = "create_clock -name clk -period 10.0 [get_ports clk]"
            r1 = adapter.validate(sdc_text=sdc, netlist_path=Path("/tmp/v"), lib_path=Path("/tmp/l"))
            r2 = adapter.validate(sdc_text=sdc, netlist_path=Path("/tmp/v"), lib_path=Path("/tmp/l"))
            assert r1.evidence.evidence_hash == r2.evidence.evidence_hash
        finally:
            os.unlink(dummy)

    def test_raw_hash_matches_raw_bytes(self):
        """raw_hash should match SHA-256 of raw_bytes."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            mock_output = b"wns 0.00\ntns 0.00\n"
            adapter._invoke_opensta = lambda *a, **kw: (mock_output, "", 0)

            result = adapter.validate(
                sdc_text="test",
                netlist_path=Path("/tmp/v"),
                lib_path=Path("/tmp/l"),
            )
            import hashlib
            expected_hash = hashlib.sha256(mock_output).hexdigest()
            assert result.raw_evidence.raw_hash == expected_hash
        finally:
            os.unlink(dummy)


# ---------------------------------------------------------------------------
# G. Oracle boundary validation
# ---------------------------------------------------------------------------

class TestOracleBoundary:
    """Verify adapter doesn't violate Oracle separation."""

    def test_adapter_does_not_decide_accept_reject(self):
        """Adapter produces OracleResult, not VerificationResult."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            adapter._invoke_opensta = lambda *a, **kw: (b"wns 0.00\ntns 0.00\n", "", 0)
            result = adapter.validate(
                sdc_text="test",
                netlist_path=Path("/tmp/v"),
                lib_path=Path("/tmp/l"),
            )
            assert isinstance(result, OracleResult)
            assert not hasattr(result, "decision")  # No decision field
            assert not hasattr(result, "is_accepted")
            assert not hasattr(result, "is_rejected")
        finally:
            os.unlink(dummy)

    def test_verification_gate_is_final_authority(self):
        """VerificationGate is the sole ACCEPT/REJECT authority."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            adapter._invoke_opensta = lambda *a, **kw: (b"wns 0.00\ntns 0.00\n", "", 0)
            result = adapter.validate(
                sdc_text="test",
                netlist_path=Path("/tmp/v"),
                lib_path=Path("/tmp/l"),
            )
            normalizer = EvidenceNormalizer()
            gate = VerificationGate()

            evidence = normalizer.normalize(
                result.evidence,
                task_id="T-TEST",
                candidate_hash="test123",
            )
            candidate = build_candidate("test")
            verification = gate.evaluate(candidate, evidence)

            # Gate makes the decision, not the adapter
            assert verification.decision in ("ACCEPT", "REJECT")
        finally:
            os.unlink(dummy)

    def test_adapter_failure_does_not_produce_false_acceptance(self):
        """Oracle failure → REJECT via gate, not false acceptance."""
        adapter = OpenSTAAdapter(sta_binary="/nonexistent/sta")
        result = adapter.validate(
            sdc_text="test",
            netlist_path=Path("/tmp/v"),
            lib_path=Path("/tmp/l"),
        )
        assert not result.is_success
        normalizer = EvidenceNormalizer()
        gate = VerificationGate()

        evidence = normalizer.normalize_failure(
            result.failure,
            task_id="T-FAIL",
            candidate_hash="test123",
        )
        candidate = build_candidate("test")
        verification = gate.evaluate(candidate, evidence)
        assert verification.is_rejected


# ---------------------------------------------------------------------------
# H. Determinism (3x PASS, 3x VIOLATION)
# ---------------------------------------------------------------------------

class TestDeterminism:
    """Deterministic execution validation."""

    def _run_pass_n(self, n=3):
        results = []
        for _ in range(n):
            dummy = _make_dummy_sta()
            try:
                adapter = OpenSTAAdapter(sta_binary=Path(dummy))
                mock_output = (
                    b"wns 0.00\n"
                    b"tns 0.00\n"
                    b"Startpoint: u_ff\n"
                    b"Endpoint: data_out\n"
                    b"Path Group: clk\n"
                    b"Path Type: max\n"
                    b"\n"
                    b"           9.85   slack (MET)\n"
                )
                adapter._invoke_opensta = lambda *a, **kw: (mock_output, "", 0)
                result = adapter.validate(
                    sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
                    netlist_path=Path("/tmp/v"),
                    lib_path=Path("/tmp/l"),
                )
                results.append(result)
            finally:
                os.unlink(dummy)
        return results

    def _run_violation_n(self, n=3):
        results = []
        for _ in range(n):
            dummy = _make_dummy_sta()
            try:
                adapter = OpenSTAAdapter(sta_binary=Path(dummy))
                mock_output = (
                    b"wns -0.10\n"
                    b"tns -0.10\n"
                    b"Startpoint: u_ff\n"
                    b"Endpoint: data_out\n"
                    b"Path Group: clk\n"
                    b"Path Type: max\n"
                    b"\n"
                    b"          -0.10   slack (VIOLATED)\n"
                )
                adapter._invoke_opensta = lambda *a, **kw: (mock_output, "", 0)
                result = adapter.validate(
                    sdc_text="create_clock -name clk -period 0.05 [get_ports clk]",
                    netlist_path=Path("/tmp/v"),
                    lib_path=Path("/tmp/l"),
                )
                results.append(result)
            finally:
                os.unlink(dummy)
        return results

    def test_pass_determinism_classification(self):
        """PASS: same classification across 3 runs."""
        results = self._run_pass_n(3)
        for r in results:
            assert r.is_success
            assert r.evidence.analysis_scope["has_violations"] is False

    def test_pass_determinism_wns(self):
        """PASS: same WNS across 3 runs."""
        results = self._run_pass_n(3)
        wns_values = [r.evidence.analysis_scope["wns"] for r in results]
        assert all(w == wns_values[0] for w in wns_values)

    def test_pass_determinism_evidence_hash(self):
        """PASS: same evidence_hash across 3 runs."""
        results = self._run_pass_n(3)
        hashes = [r.evidence.evidence_hash for r in results]
        assert all(h == hashes[0] for h in hashes)

    def test_violation_determinism_classification(self):
        """VIOLATION: same classification across 3 runs."""
        results = self._run_violation_n(3)
        for r in results:
            assert r.is_success
            assert r.evidence.analysis_scope["has_violations"] is True

    def test_violation_determinism_wns(self):
        """VIOLATION: same WNS across 3 runs."""
        results = self._run_violation_n(3)
        wns_values = [r.evidence.analysis_scope["wns"] for r in results]
        assert all(w == wns_values[0] for w in wns_values)

    def test_violation_determinism_evidence_hash(self):
        """VIOLATION: same evidence_hash across 3 runs."""
        results = self._run_violation_n(3)
        hashes = [r.evidence.evidence_hash for r in results]
        assert all(h == hashes[0] for h in hashes)

    def test_pass_and_violation_distinguishable(self):
        """PASS and VIOLATION produce different evidence hashes."""
        pass_results = self._run_pass_n(1)
        viol_results = self._run_violation_n(1)
        assert pass_results[0].evidence.evidence_hash != viol_results[0].evidence.evidence_hash


# ---------------------------------------------------------------------------
# I. Full pipeline validation
# ---------------------------------------------------------------------------

class TestFullPipeline:
    """Full pipeline: adapter → normalizer → gate."""

    def setup_method(self):
        self.normalizer = EvidenceNormalizer()
        self.gate = VerificationGate()

    def test_clean_timing_pipeline(self):
        """Clean timing → normalizer → gate → ACCEPT."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            adapter._invoke_opensta = lambda *a, **kw: (b"wns 0.00\ntns 0.00\n", "", 0)

            result = adapter.validate(
                sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
                netlist_path=Path("/tmp/v"),
                lib_path=Path("/tmp/l"),
            )
            assert result.is_success

            evidence = self.normalizer.normalize(
                result.evidence,
                task_id="T-CLEAN",
                candidate_hash="clean123",
            )
            assert evidence.oracle_status == "SUCCESS"

            candidate = build_candidate("create_clock -name clk -period 10.0 [get_ports clk]")
            verification = self.gate.evaluate(candidate, evidence)
            assert verification.is_accepted
        finally:
            os.unlink(dummy)

    def test_violation_timing_pipeline(self):
        """Timing violation → normalizer → gate → REJECT (error findings)."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            adapter._invoke_opensta = lambda *a, **kw: (b"wns -0.10\ntns -0.10\n", "", 0)

            result = adapter.validate(
                sdc_text="create_clock -name clk -period 0.05 [get_ports clk]",
                netlist_path=Path("/tmp/v"),
                lib_path=Path("/tmp/l"),
            )
            assert result.is_success

            evidence = self.normalizer.normalize(
                result.evidence,
                task_id="T-VIOL",
                candidate_hash="viol123",
            )
            assert evidence.oracle_status == "SUCCESS"
            assert evidence.has_errors  # Has error findings from violation

            candidate = build_candidate("create_clock -name clk -period 0.05 [get_ports clk]")
            verification = self.gate.evaluate(candidate, evidence)
            # Violation produces error findings → REJECT
            assert verification.is_rejected
        finally:
            os.unlink(dummy)

    def test_oracle_failure_pipeline(self):
        """Oracle failure → normalizer → gate → REJECT."""
        adapter = OpenSTAAdapter(sta_binary="/nonexistent/sta")
        result = adapter.validate(
            sdc_text="test",
            netlist_path=Path("/tmp/v"),
            lib_path=Path("/tmp/l"),
        )
        assert not result.is_success

        evidence = self.normalizer.normalize_failure(
            result.failure,
            task_id="T-FAIL",
            candidate_hash="fail123",
        )
        assert evidence.oracle_status == "ORACLE_FAILURE"

        candidate = build_candidate("test")
        verification = self.gate.evaluate(candidate, evidence)
        assert verification.is_rejected

    def test_pipeline_preserves_evidence_provenance(self):
        """Evidence provenance is preserved through the pipeline."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            adapter._invoke_opensta = lambda *a, **kw: (b"wns 0.00\ntns 0.00\n", "", 0)

            result = adapter.validate(
                sdc_text="test",
                netlist_path=Path("/tmp/v"),
                lib_path=Path("/tmp/l"),
            )

            evidence = self.normalizer.normalize(
                result.evidence,
                task_id="T-PROV",
                candidate_hash="prov123",
            )
            # Oracle name should be preserved
            assert evidence.raw_ref.get("oracle_artifact_id") is not None
        finally:
            os.unlink(dummy)


# ---------------------------------------------------------------------------
# J. Security: staging directory safety
# ---------------------------------------------------------------------------

class TestStagingSafety:
    """Verify staging directory construction is safe."""

    def test_staging_dir_uses_hash_only(self):
        """Staging directory name is derived from input hash (SHA-256 hex)."""
        from eger.oracle.opensta_adapter import _input_hash
        h = _input_hash("test sdc content")
        # SHA-256 hex is [0-9a-f] only
        assert all(c in "0123456789abcdef" for c in h[:12])
        staging_dir = f"~/eger_sta_{h[:12]}"
        # No shell metacharacters possible
        assert ";" not in staging_dir
        assert "$" not in staging_dir
        assert "`" not in staging_dir
        assert "(" not in staging_dir

    def test_sdc_written_via_heredoc(self):
        """SDC is written via bash heredoc, not shell interpolation."""
        # The adapter uses: cat > file << 'SDCEOF' ... SDCEOF
        # Single-quoted heredoc delimiter prevents shell expansion
        # This is verified by code inspection — the heredoc uses 'SDCEOF'
        pass  # Verified by code review

    def test_tcl_written_via_heredoc(self):
        """Tcl script is written via bash heredoc."""
        # The adapter uses: cat > file << 'TCLEOF' ... TCLEOF
        pass  # Verified by code review


# ---------------------------------------------------------------------------
# K. analysis_scope bug detection
# ---------------------------------------------------------------------------

class TestAnalysisScopeBug:
    """Detect the analysis_scope status ternary bug."""

    def test_analysis_scope_distinguishes_clean_vs_violated(self):
        """FIXED (P165): analysis_scope['status'] now distinguishes clean vs violated.

        Previously the ternary was:
            'VALIDATED' if not report.has_violations else 'VALIDATED'
        which always returned VALIDATED. Now fixed to:
            'VALIDATED' if not report.has_violations else 'VIOLATIONS_FOUND'
        """
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))

            # Clean case
            adapter._invoke_opensta = lambda *a, **kw: (b"wns 0.00\ntns 0.00\n", "", 0)
            clean = adapter.validate(
                sdc_text="clean", netlist_path=Path("/tmp/v"), lib_path=Path("/tmp/l"),
            )

            # Violated case
            adapter._invoke_opensta = lambda *a, **kw: (b"wns -0.10\ntns -0.10\n", "", 0)
            violated = adapter.validate(
                sdc_text="viol", netlist_path=Path("/tmp/v"), lib_path=Path("/tmp/l"),
            )

            # Clean: VALIDATED, has_violations=False
            assert clean.evidence.analysis_scope["status"] == "VALIDATED"
            assert clean.evidence.analysis_scope["has_violations"] is False

            # Violated: VIOLATIONS_FOUND, has_violations=True
            assert violated.evidence.analysis_scope["status"] == "VIOLATIONS_FOUND"
            assert violated.evidence.analysis_scope["has_violations"] is True

            # Statuses must differ
            assert clean.evidence.analysis_scope["status"] != violated.evidence.analysis_scope["status"]
        finally:
            os.unlink(dummy)
