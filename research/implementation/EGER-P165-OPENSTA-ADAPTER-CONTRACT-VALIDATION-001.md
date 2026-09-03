# EGER P165 — OpenSTA Adapter Contract Validation

## Objective

Adversarially validate the OpenSTA adapter (P164) against existing EGER contracts, error semantics, evidence pipeline, determinism requirements, and repository boundaries. Attempt to falsify P164's PASS verdict.

## Baseline

- **Commit:** 1821aac12db3b4c4670fdbd1b816e776e6c9e479
- **Branch:** main
- **Prior gate:** P164 — OpenSTA Adapter Implementation (PASS)

## Contract Surface Reviewed

| Area | Tests | Result |
|------|-------|--------|
| Constructor | 8 | ALL PASS |
| Input validation | 5 | ALL PASS |
| Tcl injection | 4 | PASS (documented, not exploitable in normal flow) |
| Path handling | 6 | ALL PASS |
| Malformed output parser | 14 | ALL PASS |
| Evidence contract mapping | 7 | ALL PASS |
| Oracle boundary | 3 | ALL PASS |
| Determinism | 7 | ALL PASS |
| Full pipeline | 4 | ALL PASS |
| Staging safety | 3 | ALL PASS |
| analysis_scope bug | 1 | PASS (bug fixed) |

## Adversarial Findings

### FINDING-001: evidence_scope Contract Mismatch (FIXED)

**Severity:** High (would cause all OpenSTA evidence to be rejected by gate)

**Description:** The OpenSTA adapter set `evidence_scope = "FULL"` directly, but the normalizer expects raw scope values (`"VALIDATED"`) and maps them to canonical values (`"FULL"`). When the normalizer received `"FULL"`, it mapped it to `"UNSUPPORTED"` (default), causing the VerificationGate to reject all OpenSTA evidence.

**Impact:** The full pipeline test `test_clean_timing_pipeline` failed — clean timing evidence was rejected as UNSUPPORTED.

**Fix:** Changed adapter to set `evidence_scope = "VALIDATED"` (the raw value), letting the normalizer handle the mapping.

**Regression:** P164 test `test_success_result_has_valid_evidence` updated to assert `"VALIDATED"` instead of `"FULL"`.

### FINDING-002: analysis_scope Status Ternary Bug (FIXED)

**Severity:** Low (misleading but doesn't affect pipeline)

**Description:** The adapter contained:
```python
"status": "VALIDATED" if not report.has_violations else "VALIDATED"
```
Both branches returned the same value. Clean and violated timing both reported `status = "VALIDATED"`.

**Fix:** Changed to:
```python
"status": "VALIDATED" if not report.has_violations else "VIOLATIONS_FOUND"
```

### FINDING-003: Unused sdc_escaped Variable (FIXED)

**Severity:** Low (dead code)

**Description:** The adapter computed `sdc_escaped` but never used it (heredoc was used instead).

**Fix:** Removed the unused variable.

### FINDING-004: Tcl Injection via design_name (DOCUMENTED)

**Severity:** Medium (requires attacker-controlled design_name)

**Description:** The `design_name` parameter is interpolated into the Tcl script without escaping:
```python
f"link_design {design_name}\n"
```
A malicious design_name like `x; exec rm -rf /` would inject a Tcl command.

**Mitigation:** In normal EGER operation, `design_name` is controlled by the pipeline, not user input. The vulnerability is documented but not exploitable in the current architecture. A future gate should add input validation for `design_name`.

**Status:** Documented, not fixed (out of scope for P165 — would require design_name validation which is a contract change).

## Security Assessment

| Vector | Result |
|--------|--------|
| Shell injection via SDC | SAFE — heredoc with single-quoted delimiter prevents shell expansion |
| Shell injection via paths | SAFE — paths are single-quoted in cp commands |
| Tcl injection via design_name | DOCUMENTED — not exploitable in normal flow |
| Path traversal | SAFE — staging dir uses SHA-256 hex (no metacharacters) |
| Staging directory collision | SAFE — input hash makes directory name deterministic and unique per input |
| Command substitution | SAFE — no backtick or $() expansion in generated bash |

## Regression Results

```
Original baseline:     734 passed
P164 tests:            26 passed
P165 tests:            63 passed
Total:                823 passed
Failures:               0
Skipped:                0
```

## Research Boundary Check

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

Three contract defects were found and fixed:
1. evidence_scope mismatch (High) — fixed
2. analysis_scope ternary bug (Low) — fixed
3. Unused variable (Low) — cleaned

One documented vulnerability:
4. Tcl injection via design_name (Medium) — documented, not exploitable in normal flow

No critical/high-severity defects remain unresolved. All 823 tests pass.

## Production Changes

| File | Change |
|------|--------|
| `eger/oracle/opensta_adapter.py` | Fixed evidence_scope, analysis_scope, removed dead code |
| `tests/test_opensta_adapter.py` | Updated evidence_scope assertion |
| `tests/test_opensta_adapter_contract.py` | NEW — 63 adversarial contract tests |

## Recommended Next Gate

P166 — OpenSTA Oracle Integration Readiness (or proceed to controlled Oracle comparison experiment when ready).
