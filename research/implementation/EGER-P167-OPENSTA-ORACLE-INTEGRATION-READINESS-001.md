# EGER P167 — OpenSTA Oracle Integration Readiness

## Objective

Determine whether the current OpenSTA integration is sufficiently stable, reproducible, contract-safe, and operationally documented to support a future controlled Oracle-validation experiment.

This is a **readiness assessment**, not evidence that Oracle generalization has been established.

## Actual Baseline

- **Commit:** 1821aac12db3b4c4670fdbd1b816e776e6c9e479
- **Branch:** main

## Runtime Environment

| Component | Value |
|-----------|-------|
| OS | Windows 10 |
| Python | 3.10.11 |
| WSL | Ubuntu 24.04.4 LTS (Noble Numbat) |
| WSL Linux | 6.6.87.2-microsoft-standard-WSL2 (x86_64) |
| OpenSTA | 2.2.0 (built from source) |
| Tcl | 8.6.14 |
| Binary (WSL) | `/root/opensta_build/OpenSTA/app/sta` |
| Binary (Win) | `\\wsl.localhost\Ubuntu-24.04\root\opensta_build\OpenSTA\app\sta` |

### Canonical Runtime Configuration

The adapter requires the WSL-resolved binary path (via `wslpath -w`), not the default `Path.home()` path. The default path points to the Windows home directory, which does not contain the WSL-installed OpenSTA binary.

```
Windows host
    ├── EGER repository (Windows filesystem)
    └── WSL2 / Ubuntu 24.04
         └── OpenSTA v2.2.0 (built from source)
```

## OpenSTA Runtime Smoke Tests

### Case A — PASS

```
is_success: True
oracle_status: SUCCESS
evidence_scope: VALIDATED
wns: 0.0
has_violations: False
findings: 2 (timing_clean)
gate decision: ACCEPT
```

### Case B — VIOLATION

```
is_success: True
oracle_status: SUCCESS
evidence_scope: VALIDATED
wns: -0.1
has_violations: True
findings: 2 (setup_violation)
gate decision: REJECT
```

### Case C — INVALID DESIGN NAME

```
is_success: False
failure.kind: INVALID_REQUEST
failure.message: design_name contains invalid characters: 'x; exec echo INJECTED'
```

### Case D — ORACLE FAILURE

```
is_success: False
failure.kind: ORACLE_FAILURE
failure.exit_code: 127
gate decision: REJECT
(oracle failure → REJECT, not timing violation)
```

## Contract Validation

| Contract | Expected | Actual | Status |
|----------|----------|--------|--------|
| evidence_scope (raw) | `VALIDATED` | `VALIDATED` | ✓ |
| evidence_scope (normalized) | `FULL` | `FULL` | ✓ |
| analysis_scope.status (clean) | `VALIDATED` | `VALIDATED` | ✓ |
| analysis_scope.status (violation) | `VIOLATIONS_FOUND` | `VIOLATIONS_FOUND` | ✓ |
| design_name valid | reaches Tcl | reaches Tcl | ✓ |
| design_name invalid | `INVALID_REQUEST` | `INVALID_REQUEST` | ✓ |
| Oracle authority | no ACCEPT/REJECT | no ACCEPT/REJECT | ✓ |
| VerificationGate | sole authority | sole authority | ✓ |

## Security Regression

| Input | Expected | Result |
|-------|----------|--------|
| `simple_path` | ACCEPT | ✓ |
| `my_design` | ACCEPT | ✓ |
| `top/sub/leaf` | ACCEPT | ✓ |
| `x; puts ...` | REJECT | ✓ |
| `x [exec ...]` | REJECT | ✓ |
| `$variable` | REJECT | ✓ |
| `x { ... }` | REJECT | ✓ |
| `""` (empty) | REJECT | ✓ |

## Determinism Results

### 3× PASS

| Run | WNS | Hash |
|-----|-----|------|
| 1 | 0.0 | `6cec044c78b21c50` |
| 2 | 0.0 | `6cec044c78b21c50` |
| 3 | 0.0 | `6cec044c78b21c50` |

**Result: SERIALIZATION-BITWISE DETERMINISTIC**

### 3× VIOLATION

| Run | WNS | Hash |
|-----|-----|------|
| 1 | -0.1 | `e93d94c0531d81ae` |
| 2 | -0.1 | `e93d94c0531d81ae` |
| 3 | -0.1 | `e93d94c0531d81ae` |

**Result: SERIALIZATION-BITWISE DETERMINISTIC**

### Cross-Case

PASS hash (`6cec044c78b21c50`) ≠ VIOLATION hash (`e93d94c0531d81ae`)

## Failure Semantics

| Failure | Kind | Gate Decision | Correct? |
|---------|------|---------------|----------|
| Missing binary | ORACLE_FAILURE | REJECT | ✓ |
| Timeout | ORACLE_FAILURE | REJECT | ✓ |
| Non-zero exit | ORACLE_FAILURE | REJECT | ✓ |
| Invalid design_name | INVALID_REQUEST | REJECT | ✓ |
| Oracle failure → normalizer | ORACLE_FAILURE | REJECT | ✓ |

Oracle failure never silently becomes valid timing evidence.

## Substrate Assessment

| Aspect | Status |
|--------|--------|
| Verilog ↔ Liberty cells | Compatible (INVX1, AND2X1, DFFX1) |
| Liberty syntax | Valid for OpenSTA |
| SDC applied | Yes (clock period manipulation) |
| PASS ≠ VIOLATION | Yes (WNS 0.0 vs -0.1) |
| Tcl script loads design | Yes (`link_design simple_path`) |
| Hidden dependencies | None |

The substrate is a minimal synthetic 3-cell circuit. It is suitable as a technical validation substrate but NOT representative of production VLSI workloads.

## Evidence-Chain Validation

```
OpenSTA (PASS)
  → OracleResult (is_success=True, evidence_scope=VALIDATED)
  → EvidenceNormalizer (oracle_status=SUCCESS, evidence_scope=FULL)
  → VerificationGate (zero errors → ACCEPT)

OpenSTA (VIOLATION)
  → OracleResult (is_success=True, evidence_scope=VALIDATED)
  → EvidenceNormalizer (oracle_status=SUCCESS, has_errors=True)
  → VerificationGate (error findings → REJECT)

OpenSTA (FAILURE)
  → OracleResult (is_success=False, failure=ORACLE_FAILURE)
  → EvidenceNormalizer.normalize_failure (oracle_status=ORACLE_FAILURE)
  → VerificationGate (ORACLE_FAILURE → REJECT)
```

All three paths are contract-correct.

## Readiness Assessment

| Criterion | Result | Evidence | Limitation |
|-----------|--------|----------|------------|
| Runtime availability | ✓ | OpenSTA 2.2.0 in WSL2 | Requires WSL2 installation |
| PASS execution | ✓ | WNS=0.0, gate=ACCEPT | Minimal 3-cell substrate |
| VIOLATION execution | ✓ | WNS=-0.1, gate=REJECT | Minimal 3-cell substrate |
| Failure semantics | ✓ | ORACLE_FAILURE → REJECT | — |
| Evidence normalization | ✓ | VALIDATED → FULL | — |
| VerificationGate integration | ✓ | Sole ACCEPT/REJECT authority | — |
| Security | ✓ | design_name validated | — |
| Determinism | ✓ | Bit-for-bit identical hashes | — |
| Reproducibility | ✓ | Same substrate + same binary | Environment-dependent |
| Substrate validity | ✓ | Cells match Liberty | Synthetic only |

## Known Limitations

1. **Minimal synthetic substrate** — 3 cells (INVX1, AND2X1, DFFX1). Not representative of production VLSI.
2. **WSL2 dependency** — Requires WSL2 with Ubuntu 24.04 and OpenSTA built from source.
3. **Binary-path configuration** — Default `Path.home()` path does not resolve to WSL OpenSTA. Must use `wslpath -w` to resolve.
4. **OpenSTA scope** — Static timing analysis only (setup/hold violations). No power, area, or other metrics.
5. **Parser limitations** — Does not support scientific notation in WNS/TNS. Acceptable since OpenSTA outputs standard decimal.
6. **Environment assumptions** — Windows host + WSL2. Not tested on native Linux or macOS.

## Research Boundary

```
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: NO
C0-C5 conclusions changed: NO
Oracle comparison performed: NO
VerificationGate authority changed: NO
Epistemic-state logic added: NO
Authorization logic added: NO
```

## Decision

**READY WITH CONDITIONS**

The OpenSTA integration is technically ready for a controlled Oracle-validation experiment. All runtime, contract, security, and determinism checks pass.

**Conditions for the future RQ-5 pilot:**
1. Experimental protocol must be designed and frozen before execution
2. Substrate must be explicitly documented as minimal/synthetic
3. Confounders must be identified and controlled
4. The experiment must not modify Ṛta, RQ-4, or C0–C5 conclusions
5. Results must be interpreted within the narrow scope of the pilot

## Full Regression

```
864/864 passed (734 original + 26 P164 + 63 P165 + 41 P166)
```
