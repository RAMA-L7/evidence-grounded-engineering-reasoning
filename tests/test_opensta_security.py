"""P166 — OpenSTA Adapter design_name Security Hardening: validation tests.

Verifies that _validate_design_name correctly rejects Tcl injection vectors
and accepts valid Verilog identifiers. No subprocess execution required.
"""

import os
import tempfile
import pytest
from pathlib import Path

from eger.oracle.opensta_adapter import (
    OpenSTAAdapter,
    _validate_design_name,
    _DESIGN_NAME_RE,
    MAX_DESIGN_NAME_LENGTH,
)
from eger.oracle.adapter import OracleResult


# ---------------------------------------------------------------------------
# _validate_design_name unit tests
# ---------------------------------------------------------------------------

class TestValidateDesignName:
    """Unit tests for the _validate_design_name function."""

    # --- Valid names ---

    def test_simple_path(self):
        assert _validate_design_name("simple_path") is None

    def test_alphanumeric(self):
        assert _validate_design_name("design123") is None

    def test_underscore_start(self):
        assert _validate_design_name("_top") is None

    def test_hierarchical(self):
        assert _validate_design_name("top/sub/leaf") is None

    def test_single_char(self):
        assert _validate_design_name("x") is None

    def test_underscore_only(self):
        assert _validate_design_name("_") is None

    def test_mixed_case(self):
        assert _validate_design_name("MyDesign_v2") is None

    def test_long_valid_name(self):
        name = "a" * MAX_DESIGN_NAME_LENGTH
        assert _validate_design_name(name) is None

    # --- Invalid names: Tcl injection vectors ---

    def test_semicolon_injection(self):
        err = _validate_design_name("x; exec rm -rf /")
        assert err is not None
        assert "invalid characters" in err.lower()

    def test_tcl_command_substitution(self):
        err = _validate_design_name("x [exec whoami]")
        assert err is not None

    def test_dollar_substitution(self):
        err = _validate_design_name("$variable")
        assert err is not None

    def test_shell_parens(self):
        err = _validate_design_name("$(command)")
        assert err is not None

    def test_newline_injection(self):
        err = _validate_design_name("x\nputs INJECTED")
        assert err is not None

    def test_braces(self):
        err = _validate_design_name("x {injected}")
        assert err is not None

    def test_double_quotes(self):
        err = _validate_design_name('x "injected"')
        assert err is not None

    def test_single_quotes(self):
        err = _validate_design_name("x' injected")
        assert err is not None

    def test_backticks(self):
        err = _validate_design_name("x`whoami`")
        assert err is not None

    def test_space(self):
        err = _validate_design_name("my design")
        assert err is not None

    def test_tab(self):
        err = _validate_design_name("my\tdesign")
        assert err is not None

    def test_empty_string(self):
        err = _validate_design_name("")
        assert err is not None
        assert "empty" in err.lower()

    def test_whitespace_only(self):
        err = _validate_design_name("   ")
        assert err is not None

    def test_leading_whitespace(self):
        err = _validate_design_name(" simple_path")
        assert err is not None

    def test_trailing_whitespace(self):
        err = _validate_design_name("simple_path ")
        assert err is not None

    def test_leading_digit(self):
        err = _validate_design_name("123design")
        assert err is not None

    def test_dot(self):
        err = _validate_design_name("top.module")
        assert err is not None

    def test_dash(self):
        err = _validate_design_name("my-design")
        assert err is not None

    def test_pipe(self):
        err = _validate_design_name("x | whoami")
        assert err is not None

    def test_ampersand(self):
        err = _validate_design_name("x & whoami")
        assert err is not None

    def test_greater_than(self):
        err = _validate_design_name("x > /tmp/pwned")
        assert err is not None

    def test_less_than(self):
        err = _validate_design_name("x < /etc/passwd")
        assert err is not None

    def test_path_traversal(self):
        err = _validate_design_name("../../etc/passwd")
        assert err is not None

    def test_excessively_long_name(self):
        err = _validate_design_name("a" * (MAX_DESIGN_NAME_LENGTH + 1))
        assert err is not None
        assert "exceed" in err.lower()

    def test_null_byte(self):
        err = _validate_design_name("x\x00y")
        assert err is not None

    def test_unicode(self):
        err = _validate_design_name("design\u00e9")
        assert err is not None


# ---------------------------------------------------------------------------
# Integration: validate() rejects invalid design_name before subprocess
# ---------------------------------------------------------------------------

class TestDesignNameRejection:
    """Verify that validate() rejects invalid design_name without subprocess."""

    def test_semicolon_rejected_no_subprocess(self):
        """Semicolon injection is rejected before _invoke_opensta is called."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            invoke_called = []
            original_invoke = adapter._invoke_opensta
            def spy_invoke(*args, **kwargs):
                invoke_called.append(True)
                return original_invoke(*args, **kwargs)
            adapter._invoke_opensta = spy_invoke

            result = adapter.validate(
                sdc_text="create_clock -name clk -period 10.0 [get_ports clk]",
                netlist_path=Path("/tmp/netlist.v"),
                lib_path=Path("/tmp/lib.lib"),
                design_name="x; exec echo INJECTED",
            )
            assert not result.is_success
            assert result.failure.kind == "INVALID_REQUEST"
            assert len(invoke_called) == 0  # _invoke_opensta was NOT called
        finally:
            os.unlink(dummy)

    def test_bracket_injection_rejected_no_subprocess(self):
        """Tcl bracket injection is rejected before subprocess."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            invoke_called = []
            def spy_invoke(*args, **kwargs):
                invoke_called.append(True)
                return b"", "", 0
            adapter._invoke_opensta = spy_invoke

            result = adapter.validate(
                sdc_text="test",
                netlist_path=Path("/tmp/v"),
                lib_path=Path("/tmp/l"),
                design_name="x [exec whoami]",
            )
            assert not result.is_success
            assert result.failure.kind == "INVALID_REQUEST"
            assert len(invoke_called) == 0
        finally:
            os.unlink(dummy)

    def test_dollar_injection_rejected_no_subprocess(self):
        """Dollar substitution is rejected before subprocess."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            invoke_called = []
            def spy_invoke(*args, **kwargs):
                invoke_called.append(True)
                return b"", "", 0
            adapter._invoke_opensta = spy_invoke

            result = adapter.validate(
                sdc_text="test",
                netlist_path=Path("/tmp/v"),
                lib_path=Path("/tmp/l"),
                design_name="$injected",
            )
            assert not result.is_success
            assert result.failure.kind == "INVALID_REQUEST"
            assert len(invoke_called) == 0
        finally:
            os.unlink(dummy)

    def test_valid_name_passes_through(self):
        """Valid design_name passes validation and reaches _invoke_opensta."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            invoke_called = []
            def spy_invoke(*a, **kw):
                invoke_called.append(kw.get("design_name") or (a[3] if len(a) > 3 else None))
                return b"wns 0.00\ntns 0.00\n", "", 0
            adapter._invoke_opensta = spy_invoke

            result = adapter.validate(
                sdc_text="test",
                netlist_path=Path("/tmp/v"),
                lib_path=Path("/tmp/l"),
                design_name="simple_path",
            )
            assert result.is_success
            assert len(invoke_called) == 1
        finally:
            os.unlink(dummy)

    def testHierarchical_name_passes_through(self):
        """Hierarchical design_name (with /) passes validation."""
        dummy = _make_dummy_sta()
        try:
            adapter = OpenSTAAdapter(sta_binary=Path(dummy))
            invoke_called = []
            def spy_invoke(*a, **kw):
                invoke_called.append(True)
                return b"wns 0.00\ntns 0.00\n", "", 0
            adapter._invoke_opensta = spy_invoke

            result = adapter.validate(
                sdc_text="test",
                netlist_path=Path("/tmp/v"),
                lib_path=Path("/tmp/l"),
                design_name="top/sub/leaf",
            )
            assert result.is_success
            assert len(invoke_called) == 1
        finally:
            os.unlink(dummy)


# ---------------------------------------------------------------------------
# P166 security test matrix
# ---------------------------------------------------------------------------

class TestSecurityMatrix:
    """Comprehensive security test matrix for design_name."""

    VALID_NAMES = [
        "simple_path",
        "my_design",
        "top",
        "design_123",
        "_top",
        "x",
        "top/sub/leaf",
        "MyDesign_v2",
    ]

    INVALID_NAMES = [
        # Tcl injection
        ("x; exec echo INJECTED", "semicolon"),
        ("x; puts INJECTED", "semicolon puts"),
        ("x [exec whoami]", "bracket command"),
        ("x [clock seconds]", "bracket clock"),
        ("$variable", "dollar variable"),
        ("$(command)", "dollar parens"),
        ("x\nputs INJECTED", "newline"),
        ("x {braces}", "braces"),
        ('x "quotes"', "double quotes"),
        ("x' quote", "single quote"),
        ("x`backtick`", "backtick"),
        # Shell injection
        ("x | whoami", "pipe"),
        ("x & whoami", "ampersand"),
        ("x > /tmp/pwned", "redirect out"),
        ("x < /etc/passwd", "redirect in"),
        # Format violations
        ("", "empty"),
        ("   ", "whitespace only"),
        (" simple_path", "leading space"),
        ("simple_path ", "trailing space"),
        ("123design", "leading digit"),
        ("my design", "space in name"),
        ("my\tdesign", "tab in name"),
        ("top.module", "dot"),
        ("my-design", "dash"),
        ("../../etc/passwd", "path traversal"),
        ("x\x00y", "null byte"),
        ("design\u00e9", "unicode"),
        ("a" * (MAX_DESIGN_NAME_LENGTH + 1), "too long"),
    ]

    def test_all_valid_names_accepted(self):
        for name in self.VALID_NAMES:
            assert _validate_design_name(name) is None, f"Valid name rejected: {name!r}"

    def test_all_invalid_names_rejected(self):
        for name, desc in self.INVALID_NAMES:
            err = _validate_design_name(name)
            assert err is not None, f"Invalid name accepted ({desc}): {name!r}"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_dummy_sta():
    fd, path = tempfile.mkstemp(suffix=".sh")
    os.write(fd, b"#!/bin/bash\nexit 0\n")
    os.close(fd)
    return path
