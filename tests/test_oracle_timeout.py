"""P149 Oracle Timeout Hardening — deterministic tests.

Tests verify:
- Timeout configuration validation
- Timeout behavior (subprocess.TimeoutExpired → ORACLE_FAILURE)
- Failure propagation through the chain
- No false acceptance on timeout
- Backward compatibility
- Configuration boundaries

No live model calls. No external dependencies. Fully deterministic.
"""

import os
import subprocess
import tempfile
import pytest
from dataclasses import dataclass
from typing import Optional
from unittest.mock import patch, MagicMock

from eger.oracle.adapter import (
    EvidenceOracle,
    OracleResult,
    OracleFailure,
    DEFAULT_ORACLE_TIMEOUT_SECONDS,
    MINIMUM_ORACLE_TIMEOUT_SECONDS,
)
from eger.evidence.normalizer import EvidenceNormalizer
from eger.evidence.schemas import EvidenceArtifact, FindingSummary
from eger.verification.gate import VerificationGate
from eger.engineer.candidate import build_candidate


# ---------------------------------------------------------------------------
# Helper: create a real file path that passes rta_cli.exists() check
# ---------------------------------------------------------------------------

_DUMMY_CLI = None


def _get_dummy_cli():
    """Return a path to a real file that passes exists() check."""
    global _DUMMY_CLI
    if _DUMMY_CLI is None:
        fd, path = tempfile.mkstemp(suffix=".py")
        os.write(fd, b"# dummy oracle placeholder\n")
        os.close(fd)
        _DUMMY_CLI = path
    return _DUMMY_CLI


# ---------------------------------------------------------------------------
# Configuration validation
# ---------------------------------------------------------------------------

class TestOracleTimeoutConfiguration:
    """Tests for EvidenceOracle timeout_seconds configuration."""

    def test_default_timeout_value(self):
        """Default timeout is 60 seconds."""
        assert DEFAULT_ORACLE_TIMEOUT_SECONDS == 60

    def test_minimum_timeout_value(self):
        """Minimum allowed timeout is 1 second."""
        assert MINIMUM_ORACLE_TIMEOUT_SECONDS == 1

    def test_default_timeout_applied(self):
        """EvidenceOracle uses default timeout when not specified."""
        oracle = EvidenceOracle(rta_cli="/nonexistent/cli.py")
        assert oracle.timeout_seconds == DEFAULT_ORACLE_TIMEOUT_SECONDS

    def test_custom_timeout_applied(self):
        """EvidenceOracle accepts custom timeout."""
        oracle = EvidenceOracle(rta_cli="/nonexistent/cli.py", timeout_seconds=30)
        assert oracle.timeout_seconds == 30

    def test_minimum_timeout_accepted(self):
        """EvidenceOracle accepts timeout_seconds == 1 (minimum)."""
        oracle = EvidenceOracle(rta_cli="/nonexistent/cli.py", timeout_seconds=1)
        assert oracle.timeout_seconds == 1

    def test_large_timeout_accepted(self):
        """EvidenceOracle accepts large timeout values."""
        oracle = EvidenceOracle(rta_cli="/nonexistent/cli.py", timeout_seconds=3600)
        assert oracle.timeout_seconds == 3600

    def test_zero_timeout_rejected(self):
        """EvidenceOracle rejects timeout_seconds == 0."""
        with pytest.raises(ValueError, match="timeout_seconds must be >="):
            EvidenceOracle(rta_cli="/nonexistent/cli.py", timeout_seconds=0)

    def test_negative_timeout_rejected(self):
        """EvidenceOracle rejects negative timeout."""
        with pytest.raises(ValueError, match="timeout_seconds must be >="):
            EvidenceOracle(rta_cli="/nonexistent/cli.py", timeout_seconds=-5)


# ---------------------------------------------------------------------------
# Timeout behavior — via subprocess mock on real path
# ---------------------------------------------------------------------------

class TestOracleTimeoutBehavior:
    """Tests for timeout behavior in EvidenceOracle."""

    def test_timeout_produces_oracle_failure(self):
        """When subprocess times out, OracleResult is failure with kind=ORACLE_FAILURE."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=60)

        with patch('eger.oracle.adapter.subprocess.run',
                   side_effect=subprocess.TimeoutExpired(
                       cmd="test", timeout=60,
                       output=b"", stderr=b"timed out"
                   )):
            result = oracle.validate("create_clock -name clk -period 10 [get_ports clk]")

        assert not result.is_success
        assert result.failure is not None
        assert result.failure.kind == "ORACLE_FAILURE"
        assert result.failure.exit_code == -1
        assert "timed out" in result.failure.message.lower()

    def test_timeout_not_success(self):
        """Timeout must NEVER produce is_success=True."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=60)

        with patch('eger.oracle.adapter.subprocess.run',
                   side_effect=subprocess.TimeoutExpired(
                       cmd="test", timeout=60, output=b"", stderr=b""
                   )):
            result = oracle.validate("create_clock -name clk -period 10 [get_ports clk]")

        assert result.is_success is False

    def test_timeout_evidence_not_usable(self):
        """Timeout failure has no usable evidence artifact."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=60)

        with patch('eger.oracle.adapter.subprocess.run',
                   side_effect=subprocess.TimeoutExpired(
                       cmd="test", timeout=60, output=b"", stderr=b""
                   )):
            result = oracle.validate("create_clock -name clk -period 10 [get_ports clk]")

        # Raw evidence exists for provenance, but evidence artifact is None
        assert result.raw_evidence is not None
        assert result.evidence is None

    def test_timeout_preserves_raw_evidence(self):
        """Timeout preserves raw_evidence for provenance tracking."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=60)

        with patch('eger.oracle.adapter.subprocess.run',
                   side_effect=subprocess.TimeoutExpired(
                       cmd="test", timeout=60,
                       output=b"partial", stderr=b"running"
                   )):
            result = oracle.validate("create_clock -name clk -period 10 [get_ports clk]")

        assert result.raw_evidence is not None
        assert result.raw_evidence.exit_code == -1
        assert result.raw_evidence.raw_bytes == b"partial"

    def test_timeout_stderr_captured(self):
        """Timeout captures stderr for diagnostics."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=60)

        with patch('eger.oracle.adapter.subprocess.run',
                   side_effect=subprocess.TimeoutExpired(
                       cmd="test", timeout=60,
                       output=b"", stderr=b"timed out"
                   )):
            result = oracle.validate("create_clock -name clk -period 10 [get_ports clk]")

        assert "timed out" in result.failure.message.lower()

    def test_timeout_custom_message(self):
        """Timeout message includes configured timeout value when no stderr."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=30)

        # When TimeoutExpired has no stderr, default message with timeout value is used
        with patch('eger.oracle.adapter.subprocess.run',
                   side_effect=subprocess.TimeoutExpired(
                       cmd="test", timeout=30,
                       output=b"", stderr=None
                   )):
            result = oracle.validate("create_clock -name clk -period 10 [get_ports clk]")

        assert "30s" in result.failure.message

    def test_timeout_message_uses_stderr_when_available(self):
        """Timeout uses stderr text when TimeoutExpired provides it."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=30)

        with patch('eger.oracle.adapter.subprocess.run',
                   side_effect=subprocess.TimeoutExpired(
                       cmd="test", timeout=30,
                       output=b"", stderr=b"custom error from subprocess"
                   )):
            result = oracle.validate("create_clock -name clk -period 10 [get_ports clk]")

        assert result.failure.message == "custom error from subprocess"


# ---------------------------------------------------------------------------
# Failure propagation
# ---------------------------------------------------------------------------

class TestTimeoutFailurePropagation:
    """Tests for timeout → failure → evidence → verification chain."""

    def setup_method(self):
        self.normalizer = EvidenceNormalizer()
        self.gate = VerificationGate()

    def _make_timeout_result(self):
        """Helper: simulate timeout and return OracleResult."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=60)
        with patch('eger.oracle.adapter.subprocess.run',
                   side_effect=subprocess.TimeoutExpired(
                       cmd="test", timeout=60,
                       output=b"", stderr=b"Oracle subprocess timed out after 60s"
                   )):
            return oracle.validate("create_clock -name clk -period 10 [get_ports clk]")

    def test_timeout_to_failure_evidence(self):
        """Timeout Oracle failure produces ERROR evidence."""
        oracle_result = self._make_timeout_result()

        assert oracle_result.failure is not None
        evidence = self.normalizer.normalize_failure(
            oracle_result.failure,
            task_id="T-TIMEOUT",
            candidate_hash="hash123",
        )

        assert evidence.oracle_status == "ORACLE_FAILURE"
        assert evidence.evidence_scope == "UNSUPPORTED"
        assert evidence.has_errors is True
        assert evidence.summary.error_count == 1

    def test_timeout_failure_evidence_rejects(self):
        """Timeout evidence causes VerificationGate to REJECT."""
        oracle_result = self._make_timeout_result()

        evidence = self.normalizer.normalize_failure(
            oracle_result.failure,
            task_id="T-TIMEOUT",
            candidate_hash="hash123",
        )

        candidate = build_candidate("create_clock -name clk -period 10 [get_ports clk]")
        verification = self.gate.evaluate(candidate, evidence)

        assert verification.is_rejected
        assert verification.decision == "REJECT"
        assert "ORACLE_FAILURE" in verification.reason

    def test_timeout_never_accepts(self):
        """Full chain: timeout → failure → evidence → REJECT. Never ACCEPT."""
        oracle_result = self._make_timeout_result()

        evidence = self.normalizer.normalize_failure(
            oracle_result.failure,
            task_id="T-TIMEOUT",
            candidate_hash="hash123",
        )

        candidate = build_candidate("create_clock -name clk -period 10 [get_ports clk]")
        verification = self.gate.evaluate(candidate, evidence)

        assert verification.is_accepted is False
        assert verification.is_rejected is True

    def test_timeout_error_count_in_verification(self):
        """Timeout evidence carries error_count into verification result."""
        oracle_result = self._make_timeout_result()

        evidence = self.normalizer.normalize_failure(
            oracle_result.failure,
            task_id="T-TIMEOUT",
            candidate_hash="hash123",
        )

        candidate = build_candidate("create_clock -name clk -period 10 [get_ports clk]")
        verification = self.gate.evaluate(candidate, evidence)

        assert verification.error_count == 1


# ---------------------------------------------------------------------------
# _invoke_rta timeout behavior (subprocess boundary)
# ---------------------------------------------------------------------------

class TestInvokeRtaTimeout:
    """Tests for the _invoke_rta timeout boundary."""

    def test_invoke_rta_returns_timeout_exit_code(self):
        """_invoke_rta returns exit_code=-1 on timeout."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=60)

        with patch('eger.oracle.adapter.subprocess.run',
                   side_effect=subprocess.TimeoutExpired(
                       cmd="test", timeout=60,
                       output=b"partial output", stderr=b"still running..."
                   )):
            stdout, stderr, exit_code = oracle._invoke_rta("test sdc")

        assert exit_code == -1
        assert stdout == b"partial output"
        assert "still running" in stderr.lower()

    def test_invoke_rta_timeout_with_no_output(self):
        """_invoke_rta handles timeout with no stdout/stderr."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=60)

        with patch('eger.oracle.adapter.subprocess.run',
                   side_effect=subprocess.TimeoutExpired(
                       cmd="test", timeout=60,
                       output=None, stderr=None
                   )):
            stdout, stderr, exit_code = oracle._invoke_rta("test sdc")

        assert exit_code == -1
        assert stdout == b""
        assert "timed out" in stderr.lower()

    def test_invoke_rta_normal_execution_not_affected(self):
        """Normal execution (no timeout) is not affected by timeout_seconds."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=60)

        mock_run_result = MagicMock()
        mock_run_result.stdout = b'{"errors": [], "warnings": []}'
        mock_run_result.stderr = b""
        mock_run_result.returncode = 0

        with patch('eger.oracle.adapter.subprocess.run', return_value=mock_run_result):
            stdout, stderr, exit_code = oracle._invoke_rta("test sdc")

        assert exit_code == 0
        assert stdout == b'{"errors": [], "warnings": []}'

    def test_timeout_seconds_passed_to_subprocess(self):
        """timeout_seconds is passed as timeout= to subprocess.run."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=42)

        mock_run_result = MagicMock()
        mock_run_result.stdout = b""
        mock_run_result.stderr = b""
        mock_run_result.returncode = 0

        with patch('eger.oracle.adapter.subprocess.run', return_value=mock_run_result) as mock_run:
            oracle._invoke_rta("test sdc")

        # Verify timeout was passed to subprocess.run
        _, kwargs = mock_run.call_args
        assert kwargs.get('timeout') == 42


# ---------------------------------------------------------------------------
# Backward compatibility
# ---------------------------------------------------------------------------

class TestBackwardCompatibility:
    """Tests for backward compatibility with existing callers."""

    def test_existing_oracle_api_unchanged(self):
        """Existing EvidenceOracle() call (no timeout arg) still works."""
        oracle = EvidenceOracle(rta_cli="/nonexistent/cli.py")
        assert oracle.timeout_seconds == DEFAULT_ORACLE_TIMEOUT_SECONDS
        assert hasattr(oracle, 'validate')
        assert hasattr(oracle, 'capabilities')
        assert hasattr(oracle, 'evidence_schema')

    def test_existing_validate_api_unchanged(self):
        """validate() signature unchanged — no new required parameters."""
        oracle = EvidenceOracle(rta_cli="/nonexistent/cli.py")
        with patch.object(oracle, '_invoke_rta', return_value=(b"", "", 127)):
            result = oracle.validate(
                "test sdc",
                input_identity="test",
                invocation_options={"key": "val"},
            )
            assert result is not None

    def test_existing_test_evidence_oracle_passes(self):
        """Existing T004 (missing oracle binary) still works."""
        oracle = EvidenceOracle(rta_cli="/nonexistent/cli.py")
        result = oracle.validate("create_clock -name clk -period 10 [get_ports clk]")
        assert not result.is_success
        assert result.failure.kind == "ORACLE_FAILURE"
        assert result.failure.exit_code == 127


# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

class TestTimeoutSecurity:
    """Security checks for timeout hardening."""

    def test_no_credential_leakage_in_timeout_message(self):
        """Timeout message does not leak credentials."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=60)

        with patch('eger.oracle.adapter.subprocess.run',
                   side_effect=subprocess.TimeoutExpired(
                       cmd="test", timeout=60, output=b"", stderr=b"timed out"
                   )):
            result = oracle.validate("test sdc")

        msg = result.failure.message.lower()
        assert "api_key" not in msg
        assert "token" not in msg
        assert "password" not in msg
        assert "secret" not in msg

    def test_no_shell_injection_in_timeout(self):
        """Timeout handling does not use shell=True."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=60)

        with patch('eger.oracle.adapter.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout=b"", stderr=b"", returncode=0)
            oracle._invoke_rta("test sdc")
            call_kwargs = mock_run.call_args
            assert call_kwargs.kwargs.get('shell') is not True

    def test_timeout_does_not_escalate_privilege(self):
        """Timeout does not change oracle authority."""
        oracle = EvidenceOracle(rta_cli=_get_dummy_cli(), timeout_seconds=60)

        with patch('eger.oracle.adapter.subprocess.run',
                   side_effect=subprocess.TimeoutExpired(
                       cmd="test", timeout=60, output=b"", stderr=b"timed out"
                   )):
            result = oracle.validate("test sdc")

        assert result.is_success is False
        assert result.failure.kind == "ORACLE_FAILURE"
