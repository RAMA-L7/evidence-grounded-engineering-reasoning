# EGER P166 — OpenSTA Adapter `design_name` Security Hardening

## Objective

Resolve P165 FINDING-004: Tcl injection via `design_name`. Validate that externally supplied design names cannot inject additional Tcl commands into the OpenSTA execution script.

## P165 Finding Being Remediated

```
FINDING-004: Tcl injection via design_name
Severity: Medium
Status: RESOLVED (P166)
```

The adapter previously interpolated `design_name` directly into the Tcl script:
```python
f"link_design {design_name}\n"
```
A malicious `design_name` like `x; exec rm -rf /` would inject a Tcl command.

## Existing `design_name` Contract

- `link_design` takes a Verilog module/cell name
- Valid Verilog identifiers: `[a-zA-Z_][a-zA-Z0-9_]*`
- Hierarchical names use `/` separator: `top/sub/leaf`
- No Tcl metacharacters are legitimately required
- Default value: `"simple_path"`

## Threat Model

```
design_name (user-controlled)
    ↓
Python validation (_validate_design_name)
    ↓  ← REJECT if invalid
Tcl generation (link_design {design_name})
    ↓
WSL/bash staging (heredoc)
    ↓
OpenSTA execution
```

Without validation, a malicious `design_name` reaches the Tcl script and executes arbitrary commands.

## Remediation

### Before (P165)
```python
# No validation — design_name flows directly to Tcl
raw_bytes, stderr_text, exit_code = self._invoke_opensta(
    sdc_text, netlist_path, lib_path, design_name
)
```

### After (P166)
```python
# P166: Validate design_name before any subprocess execution
design_error = _validate_design_name(design_name)
if design_error is not None:
    return OracleResult(
        is_success=False,
        failure=OracleFailure(kind="INVALID_REQUEST", ...),
    )
# design_name is now safe for Tcl interpolation
raw_bytes, stderr_text, exit_code = self._invoke_opensta(...)
```

### Validation Contract
```python
_DESIGN_NAME_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_/]*$")
MAX_DESIGN_NAME_LENGTH = 256
```

## Security Test Matrix

| Input Class | Example | Expected | Result |
|-------------|---------|----------|--------|
| Valid | `simple_path` | ACCEPT | PASS |
| Valid | `top/sub/leaf` | ACCEPT | PASS |
| Valid | `_top` | ACCEPT | PASS |
| Semicolon | `x; exec ...` | REJECT | PASS |
| Tcl bracket | `x [exec ...]` | REJECT | PASS |
| Dollar | `$variable` | REJECT | PASS |
| Shell parens | `$(command)` | REJECT | PASS |
| Newline | `x\nputs ...` | REJECT | PASS |
| Braces | `x { ... }` | REJECT | PASS |
| Quotes | `x " ... "` | REJECT | PASS |
| Backtick | `x\`cmd\`` | REJECT | PASS |
| Space | `my design` | REJECT | PASS |
| Empty | `""` | REJECT | PASS |
| Path traversal | `../../etc/passwd` | REJECT | PASS |
| Too long | `a` × 257 | REJECT | PASS |

## Runtime Validation

- **Valid name (`simple_path`)**: Passes validation, reaches binary check
- **Invalid name (`x; exec echo INJECTED`)**: Rejected with `INVALID_REQUEST` before subprocess
- No OpenSTA subprocess executed for invalid names (verified via spy mock)

## Regression Results

```
P166 security tests:    41/41 PASS
P164 adapter tests:     26/26 PASS
P165 contract tests:    63/63 PASS
Full regression:       864/864 PASS (734 original + 130 OpenSTA tests)
```

## Residual Risk

**No remaining Tcl injection path in the `design_name` execution path.**

The validation prevents all Tcl metacharacters from reaching the generated script. The only characters allowed are `[a-zA-Z0-9_/]`, which have no special meaning in Tcl.

## Research Boundary

```
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: NO
C0-C5 conclusions changed: NO
VerificationGate authority changed: NO
Epistemic-state logic added: NO
Authorization logic added: NO
```

## Decision

**PASS**

P165 FINDING-004 is resolved. All 864 tests pass. No unresolved security defects remain in the `design_name` execution path.

## Files Changed

| File | Change |
|------|--------|
| `eger/oracle/opensta_adapter.py` | Added `_validate_design_name()`, validation in `validate()` |
| `tests/test_opensta_security.py` | NEW — 41 security tests |
| `tests/test_opensta_adapter_contract.py` | Updated injection tests to verify rejection |
