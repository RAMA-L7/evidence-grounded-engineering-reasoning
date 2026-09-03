# EGER P164 — OpenSTA Adapter Design & Implementation

## Objective

Implement a minimal **OpenSTA Oracle Adapter** that connects the validated OpenSTA v2.2.0 substrate (P163) to the existing EGER Oracle/Evidence pipeline.

## Baseline

- **Branch:** main
- **Commit:** 1821aac12db3b4c4670fdbd1b816e776e6c9e479
- **Prior gate:** P163 — OpenSTA Substrate Validation (PASS)

## Environment

- **OS:** Windows + WSL2 (Ubuntu 24.04.4 LTS)
- **OpenSTA:** v2.2.0, built from source in WSL2
- **Binary location:** `~/opensta_build/OpenSTA/app/sta` (WSL2)

## Architecture

```
EGER Task
   ↓
OpenSTAAdapter.validate(sdc_text, netlist_path, lib_path)
   ↓
WSL2 bash (file staging + subprocess)
   ↓
OpenSTA v2.2.0 (static timing analysis)
   ↓
stdout (timing report)
   ↓
Output parser (WNS, TNS, slack, findings)
   ↓
OracleResult (EvidenceArtifact | OracleFailure)
   ↓
EvidenceNormalizer → VerificationGate
```

## Implementation

### Files Created/Modified

| File | Status | Description |
|------|--------|-------------|
| `eger/oracle/opensta_adapter.py` | **NEW** | OpenSTA adapter implementation |
| `eger/oracle/__init__.py` | Modified | Added OpenSTAAdapter import |
| `tests/test_opensta_adapter.py` | **NEW** | 26 unit/integration tests |

### Adapter Interface

```python
class OpenSTAAdapter:
    def __init__(self, sta_binary: Path = None, timeout_seconds: int = 60)
    def validate(self, sdc_text: str, netlist_path: Path, lib_path: Path,
                 design_name: str = "simple_path") -> OracleResult
    def capabilities(self) -> Dict[str, Any]
```

### File Staging Strategy

OpenSTA's Tcl interpreter cannot handle paths with spaces. The adapter:

1. Converts Windows paths to WSL mount paths (`D:\foo` → `/mnt/d/foo`)
2. Generates a single bash script that:
   - Creates a staging directory in WSL home (no spaces)
   - Copies substrate files from `/mnt/` paths
   - Writes SDC and Tcl via heredocs
   - Runs OpenSTA
   - Cleans up staging directory
3. Executes the bash script via `wsl -d Ubuntu-24.04 bash -c <script>`

All file staging is done through WSL bash, not Windows Python pathlib (which cannot create directories under WSL-internal paths).

### Output Parser

Parses OpenSTA stdout for:
- **WNS** (worst negative slack) via `report_wns`
- **TNS** (total negative slack) via `report_tns`
- **Slack classification** (MET/VIOLATED) from `report_checks`
- **Path details** (startpoint, endpoint, path group, path type)

### Evidence Mapping

OpenSTA findings map to EGER EvidenceArtifact:
- WNS ≥ 0 → `timing_clean` (severity: info)
- WNS < 0 → `setup_violation` (severity: error)
- TNS < 0 → `total_negative_slack` (severity: error)
- Path-level findings from `report_checks`

### Error Handling

| Condition | Handling |
|-----------|----------|
| Missing binary | `ORACLE_FAILURE`, exit_code=127 |
| Subprocess timeout | `ORACLE_FAILURE`, exit_code=-1 |
| Non-zero exit | `ORACLE_FAILURE`, exit_code=N |
| Malformed output | Partial parse (WNS/TNS may be None) |

## Test Results

### Unit Tests (22 tests)

| Category | Tests | Status |
|----------|-------|--------|
| Configuration validation | 5 | ALL PASS |
| Output parser | 9 | ALL PASS |
| Error handling | 3 | ALL PASS |
| Evidence chain | 3 | ALL PASS |
| Determinism | 2 | ALL PASS |

### Integration Tests (4 tests)

| Test | Status | Result |
|------|--------|--------|
| PASS substrate → MET timing | PASS | WNS = 0.00 ns |
| VIOLATION substrate → VIOLATED timing | PASS | WNS = -0.10 ns |
| PASS distinguishes from VIOLATION | PASS | 0.00 ≠ -0.10 |
| PASS evidence chain | PASS | ACCEPT |

### Full EGER Regression

```
760 passed (734 original + 26 new OpenSTA tests)
```

## Manual Timing Cross-Check

### PASS Case (10.0 ns clock)

- Data arrival: 0.05 ns (DFFX1 clock-to-Q)
- Data required: 10.0 - 0.10 = 9.90 ns (external delay)
- Slack: 9.90 - 0.05 = **9.85 ns (MET)** ✓

### VIOLATION Case (0.05 ns clock)

- Data arrival: 0.05 ns
- Data required: 0.05 - 0.10 = -0.05 ns
- Slack: -0.05 - 0.05 = **-0.10 ns (VIOLATED)** ✓

## Determinism

Both PASS and VIOLATION cases produce identical results across repeated runs:
- Same WNS values
- Same TNS values
- Same finding classifications
- Same evidence hashes (for identical inputs)

## Reproducibility

- Substrate files are on the Windows filesystem (accessible via `/mnt/`)
- Staging directory uses hash-based naming (deterministic per input)
- All file operations are done through WSL bash (no Windows path ambiguity)
- OpenSTA invocation uses `-no_init -no_splash` flags

## Security Assessment

- All external components are from official sources
- OpenSTA v2.2.0 built from official The-OpenROAD-Project/OpenSTA repository
- No arbitrary binary downloads
- No system modifications beyond WSL2 installation
- Staging directories are cleaned up after execution

## Research Boundaries

### Explicitly NOT done in P164

- ❌ Modified Ṛta
- ❌ Modified historical research
- ❌ Reopened RQ-4
- ❌ Ran RQ-5 experiments
- ❌ Performed Oracle comparison
- ❌ Modified VerificationGate authority model
- ❌ Introduced epistemic-state logic
- ❌ Redesigned unrelated EGER architecture

### Research State

- C0: ESTABLISHED
- C1: ESTABLISHED
- C2: PARTIALLY SUPPORTED
- C3: NOT JUSTIFIED
- C4: DEFERRED
- C5: DEFERRED
- RQ-4: CLOSED

**P164 success does NOT establish RQ-5 or Oracle generalization.**

## Decision

**PASS**

The OpenSTA adapter is functional, produces correct timing results, maps findings into the EGER evidence contract, and passes all 26 tests plus the 734-test EGER regression.

## Recommended Next Gate

**P165 — OpenSTA Adapter Contract Validation**

Validate that the adapter correctly handles edge cases, malformed inputs, and integrates with the full EGER pipeline under controlled conditions.
