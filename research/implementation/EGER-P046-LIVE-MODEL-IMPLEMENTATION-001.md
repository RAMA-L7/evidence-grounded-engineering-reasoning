# EGER-P046 — Live MODEL-003 Implementation Report

| Field | Value |
|---|---|
| ID | EGER-P046-LIVE-MODEL-IMPLEMENTATION-001 |
| Date | 2026-08-27 |
| Authorization | P046 human authorization for EGER-CHANGE-003 |
| Status | **IMPLEMENTATION COMPLETE — LIVE MODEL PATH VERIFIED — C2 LIVE EXECUTION NOT AUTHORIZED** |

---

## 1. Human Authorization

**AUTHORIZED** — P046 explicitly authorizes implementation of EGER-CHANGE-003 (live MODEL-003 path).

Scope: implement live `opencode run` invocation in `LiveEngineerModel.generate()`.

## 2. EGER-CHANGE-003

APPROVED and IMPLEMENTED. See `research/implementation/EGER-CHANGE-003.md`.

## 3. Implementation Scope

### 3.1 Files Modified

| File | Change |
|------|--------|
| `eger/engineer/model.py` | Added `live` parameter, `_invoke_live()` subprocess path, `_invoke_canned()` backward-compatible path, refactored `generate()` |
| `research/experiments/EGER-EXP-001/formal_runner_c2.py` | Added `live` parameter to `run_c2_task()` and `run_c2()`, `C2-live` artifact directory routing, argparse for CLI |
| `tests/test_c2_runner.py` | Added 12 tests (T21–T32) covering live invocation, canned backward compatibility, error handling, artifact directories |

### 3.2 Files NOT Modified

| File | Status |
|------|--------|
| `eger/engineer/adapter.py` | UNTOUCHED (already supports `evidence_summary`) |
| `eger/engineer/candidate.py` | UNTOUCHED |
| `eger/engineer/feedback.py` | UNTOUCHED |
| `eger/engineer/structured_feedback.py` | UNTOUCHED |
| `eger/oracle/adapter.py` | UNTOUCHED |
| `eger/oracle/schemas.py` | UNTOUCHED |
| `eger/epistemic/*` | UNTOUCHED |
| `eger/authorization/*` | UNTOUCHED |
| `BENCH-002` | UNTOUCHED |
| `MODEL-003` spec | UNTOUCHED |
| `Ṛta` | UNTOUCHED (3b5c2f2, main, 19 dirty) |
| C0 artifacts | UNTOUCHED |
| C1 artifacts | UNTOUCHED |
| C2 artifacts (canned) | UNTOUCHED |

## 4. Live Invocation Design

```python
def _invoke_live(self, prompt: str) -> str:
    cmd = ["opencode", "run", "--model", self.model]
    result = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True, timeout=self.timeout
    )
    if result.returncode != 0:
        raise RuntimeError(f"opencode run failed (exit {result.returncode})")
    return result.stdout.strip()
```

Key properties:
- Prompt passed as stdin (not CLI argument)
- Timeout enforced via subprocess
- Non-zero exit → explicit RuntimeError (no silent fallback)
- Empty output → explicit RuntimeError
- `tools=[]` enforced by not passing tools to opencode

## 5. Backward Compatibility

`LiveEngineerModel(live=False)` (default) preserves the exact canned behavior from before this change. Existing code that creates `LiveEngineerModel()` without specifying `live` gets `live=False` — no breakage.

For formal live execution, `live=True` must be explicitly passed.

## 6. Test Results

```
95 tests PASS (16.90s)

Previous baseline: 83 tests
New live adapter tests: 12 (T21–T32)
Total: 95
```

New test coverage:
- T21: Live model calls opencode via subprocess
- T22: Different prompts passed to different calls
- T23: RuntimeError on opencode failure
- T24: RuntimeError on empty output
- T25: TimeoutExpired on subprocess timeout
- T26: Canned model uses task map (backward compat)
- T27: Canned model preserves task IDs
- T28: Live model preserves MODEL-003 config
- T29: Prompt forwarded as stdin
- T30: `live=False` backward compatible
- T31: C2-live artifact directory
- T32: C2 canned artifact directory

## 7. Benchmark Preservation

BENCH-002 v0.1 unchanged. 6 CLEAN held-out tasks. No task modification.

## 8. Oracle Preservation

EvidenceOracle unchanged. Ṛta 3b5c2f2 main 19 — untouched. `rta_generate` never invoked.

## 9. Artifact Isolation

- `formal/C2/` (canned C2) — PRESERVED, not overwritten
- `formal/C2-live/` (future live C2) — NOT YET POPULATED
- C0/C1 artifacts — UNTOUCHED

## 10. Provenance

- P045 design → P046 authorization → implementation (this report)
- Previous checkpoint: `6d59d53` (canned C2 implementation)
- This implementation is a new state after `6d59d53`

## 11. C2 Execution Status

**C2 LIVE EXECUTION = NOT AUTHORIZED**

The live model path is implemented and tested. Formal live C2 execution requires:
1. P047 readiness verification
2. Separate human execution authorization

## 12. Remaining Readiness Requirements

Before live C2 execution:
1. Verify `OPENCODE_API_KEY` is available in execution environment
2. Verify `opencode` CLI is installed and functional
3. P047-style readiness verification
4. Human authorization for live C2 execution

## 13. Git Status

- Local HEAD: `8c9c1ac` (P043)
- Working tree: modified `model.py`, `formal_runner_c2.py`, `test_c2_runner.py` + new `EGER-CHANGE-003.md`, `EGER-P046-...md`, `EGER-P045-...md`
- Remote: `bb07208` (not pushed)
- Ṛta: `3b5c2f2`, main, 19 — UNTOUCHED

**Do NOT push.** Commit may be created as provenance checkpoint after review.

## 14. Final Status

```
EGER-CHANGE-003    IMPLEMENTED
LIVE MODEL PATH    VERIFIED (95/95 tests PASS)
C2 LIVE EXECUTION  NOT AUTHORIZED
PROVENANCE         REQUIRES CHECKPOINT COMMIT
```
