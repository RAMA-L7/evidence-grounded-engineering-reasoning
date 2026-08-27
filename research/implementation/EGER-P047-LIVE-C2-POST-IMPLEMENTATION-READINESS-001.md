# EGER-P047 — Live C2 Post-Implementation Readiness Verification

| Field | Value |
|---|---|
| ID | EGER-P047-LIVE-C2-POST-IMPLEMENTATION-READINESS-001 |
| Date | 2026-08-27 |
| Scope | READINESS AUDIT ONLY — no execution |
| Status | **READY — C2 LIVE EXECUTION NOT AUTHORIZED — HUMAN EXECUTION AUTHORIZATION REQUIRED** |

---

## 1. Executive Verdict

**READY WITH ONE NON-BLOCKING ENVIRONMENTAL GAP.**

All implementation, separation, boundary, preservation, and test criteria pass. The single gap is `OPENCODE_API_KEY: ABSENT` in the current shell environment — this is an execution-environment issue, not an implementation defect. The live model path is correctly implemented and tested; the credential must be available at execution time.

---

## 2. Governing State

| Item | Status | Verified |
|------|--------|----------|
| EGER-CHANGE-002 | APPROVED (P039) | ✅ |
| MODEL-003 | FROZEN (mimo-v2.5-free) | ✅ |
| EXP-001 v0.3 | FROZEN | ✅ |
| P037 | Responsiveness PASS | ✅ |
| P045 | Live C2 design complete | ✅ |
| P046 | CHANGE-003 implementation authorized + completed | ✅ |
| Previous C2 | VALID EXECUTION / TREATMENT EFFECT NOT IDENTIFIABLE | ✅ Preserved |

---

## 3. Live Model Implementation

**Verified by code inspection of `eger/engineer/model.py`:**

| Property | Expected | Actual | Status |
|----------|----------|--------|--------|
| `live=True` path | `_invoke_live()` | `_invoke_live()` at line ~78 | ✅ |
| `live=False` path | `_invoke_canned()` | `_invoke_canned()` at line ~96 | ✅ |
| Command | `["opencode", "run", "--model", self.model]` | Matches | ✅ |
| Prompt delivery | `input=prompt` (stdin) | Matches | ✅ |
| Timeout | `timeout=self.timeout` | Matches | ✅ |
| Provider | `opencode` | `"opencode"` class attr | ✅ |
| Model | `opencode/mimo-v2.5-free` | Matches | ✅ |
| model_version | `NOT_EXPOSED` | Matches | ✅ |
| temperature | `0.0` | `sampling_params["temperature"] = 0.0` | ✅ |
| tools | `[]` | Not passed to subprocess (no tools) | ✅ |
| max_tokens | `2048` | `self.max_tokens = 2048` | ✅ |
| timeout | `60s` | `self.timeout = 60` | ✅ |

---

## 4. Canned/Live Separation

**Verified:**

- `LiveEngineerModel(live=False)` → `_invoke_canned()` → deterministic task-map lookup
- `LiveEngineerModel(live=True)` → `_invoke_live()` → `subprocess.run(["opencode", "run", ...])`
- `generate()` method: `if self.live: raw = self._invoke_live(prompt) else: raw = self._invoke_canned(prompt)`
- **No silent fallback:** `_invoke_live()` raises `RuntimeError` on non-zero exit or empty output
- **No try/except wrapping** that would catch and fallback to canned
- Default is `live=False` (backward compatible)

---

## 5. C2 Runner

**Verified by code inspection of `formal_runner_c2.py`:**

| Property | Expected | Actual | Status |
|----------|----------|--------|--------|
| `run_c2_task(live=False)` | `formal/C2/` | `artifact_condition = "C2"` | ✅ |
| `run_c2_task(live=True)` | `formal/C2-live/` | `artifact_condition = "C2-live"` | ✅ |
| Model construction | `LiveEngineerModel(..., live=live)` | Matches | ✅ |
| CLI argparse | `--live` flag | `parser.add_argument("--live", ...)` | ✅ |

---

## 6. Call Boundary

**Verified by code inspection:**

**Call 1** (`engine_adapter.propose(design_context, objective)`):
- Contains: task context, objective
- Does NOT contain: feedback, evidence, existing_sdc

**Call 2** (`engine_adapter.propose(design_context, existing_sdc=..., objective=..., evidence_summary=...)`):
- Contains: task context, objective, initial candidate (`existing_sdc`), structured feedback (`evidence_summary`)
- Does NOT contain: evaluator answers, C0/C1/C2 outcomes, research ledger, authorization state, epistemic state, oracle internals, hidden benchmark information, web/retrieval/subagents

**Information boundary: VERIFIED** — same structure as previous C2, no new data channels introduced.

---

## 7. Capability Isolation

- `tools = []` — no tools passed to opencode subprocess
- No web, browsing, retrieval, subagents, tool calls in `LiveEngineerModel`
- `rta_generate`: **0 hits** in `eger/` (verified via grep)
- Provider-side hidden context: **UNKNOWN** (cannot verify provider internals)

---

## 8. Test Results

```
95 passed in 17.16s
```

| Suite | Tests | Status |
|-------|-------|--------|
| test_evidence_oracle.py | 14 | ✅ PASS |
| test_epistemic_authorization.py | 17 | ✅ PASS |
| test_llm_proposal.py | 16 | ✅ PASS |
| test_c1_feedback.py | 16 | ✅ PASS |
| test_c2_runner.py | 32 | ✅ PASS |
| **Total** | **95** | **95/95 PASS** |

Live adapter test coverage (T21–T32):
- T21: Live model calls opencode via subprocess ✅
- T22: Different prompts forwarded to different calls ✅
- T23: RuntimeError on opencode failure ✅
- T24: RuntimeError on empty output ✅
- T25: TimeoutExpired on subprocess timeout ✅
- T26: Canned model uses task map ✅
- T27: Canned model preserves task IDs ✅
- T28: Live model preserves MODEL-003 config ✅
- T29: Prompt forwarded as stdin ✅
- T30: `live=False` backward compatible ✅
- T31: C2-live artifact directory ✅
- T32: C2 canned artifact directory ✅

---

## 9. Credential State

```
OPENCODE_API_KEY: ABSENT
```

**Classification: NON-BLOCKING ENVIRONMENTAL GAP**

The credential is not available in the current shell. This is expected — the implementation audit verifies code correctness, not runtime environment. The credential must be available when live C2 is actually executed. P037-R1 verified the credential was present at that time (`OPENCODE_API_KEY` `PRESENT len 67`).

---

## 10. Model Reproducibility

| Field | Value |
|-------|-------|
| provider | opencode |
| model | opencode/mimo-v2.5-free |
| version | NOT_EXPOSED |
| temperature | 0.0 |
| tools | [] |
| prompt | eger.prompt.v1 |
| max_tokens | 2048 |
| timeout | 60s |

**Known limitation:** `temperature 0.0` does not guarantee byte-identical output (observed in P037). Reproducibility metadata (prompt_hash, output_hash, candidate_hash) captured per run.

---

## 11. Benchmark Preservation

```
git diff --stat -- research/experiments/EGER-BENCH-002/ → empty
```

BENCH-002 v0.1 UNCHANGED. 6 CLEAN held-out tasks. No modification.

---

## 12. Oracle Preservation

```
Ṛta HEAD: 3b5c2f25c48d6b6b1d4809f0d5d69fc467d387ea
Ṛta branch: main
Ṛta dirty: 19 (pre-existing)
rta_generate hits in eger/: 0
```

EvidenceOracle UNTOUCHED. Ṛta UNTOUCHED.

---

## 13. Historical Artifact Preservation

| Artifact | Manifests | Status |
|----------|-----------|--------|
| C0 (`formal/manifests/`) | 6 | ✅ PRESERVED |
| C1 (`formal/C1/manifests/`) | 6 | ✅ PRESERVED |
| C2 canned (`formal/C2/manifests/`) | 6 | ✅ PRESERVED |
| C2-live (`formal/C2-live/manifests/`) | 0 | ✅ EMPTY (correct — no execution yet) |

---

## 14. C2-live Artifact State

`formal/C2-live/` is **empty** — no experimental manifests, no raw artifacts. Correct: C2 live execution has not occurred.

---

## 15. Provenance

```
6d59d53 → EGER-CHANGE-003 → P046 implementation → P047 readiness
```

The live implementation is a new state after `6d59d53`. Do not associate it with the previous canned C2 checkpoint.

---

## 16. Oracle Scope Limitation

**NON-BLOCKING.** All 6 BENCH-002 tasks produce `INSUFFICIENT` scope (`NETLIST_REQUIRED`). This was the same in the previous C2 execution and does not prevent measuring the primary outcome:

```
proposal_changed = initial_candidate_hash != final_candidate_hash
```

This is observable regardless of oracle scope.

---

## 17. Scientific Identifiability

The live implementation enables three-way distinction:

```
A. No model response:      initial_hash == final_hash
B. Responds, no improve:   initial_hash != final_hash, same/worse oracle
C. Responds, improves:     initial_hash != final_hash, better oracle
```

This was impossible with the canned model (only A observable).

---

## 18. Blocking Issues

**None.**

---

## 19. Non-Blocking Issues

| # | Issue | Classification |
|---|-------|---------------|
| 1 | `OPENCODE_API_KEY` absent in current shell | Environmental — must be present at execution |
| 2 | `temperature 0.0` not byte-identical | Known limitation — documented in MODEL-003 |
| 3 | `model_version = NOT_EXPOSED` | Provider limitation — documented |

---

## 20. GO/NO-GO

### READY

All implementation criteria satisfied:
- ✅ Live model path implemented correctly
- ✅ Canned/live separation verified
- ✅ No silent fallback
- ✅ Information boundary verified
- ✅ Capability isolation verified
- ✅ Failure semantics verified (explicit errors, no silent recovery)
- ✅ Benchmark preserved
- ✅ Oracle preserved
- ✅ C0/C1/C2 preserved
- ✅ Artifact isolation verified (C2-live empty)
- ✅ 95/95 tests PASS
- ✅ Provenance recorded
- ✅ Change control complete (CHANGE-003)
- ✅ No blocking issues

**C2 LIVE EXECUTION = NOT AUTHORIZED**

Readiness does NOT equal experiment authorization. Separate human authorization required.

---

## 21. Required Human Authorization

Before live C2 execution, the human researcher must authorize:

**EGER-AUTH-004 — LIVE C2 FORMAL EXECUTION**

This authorization must verify:
1. `OPENCODE_API_KEY` is available in the execution environment
2. `opencode` CLI is installed and functional
3. P047 readiness is accepted
4. Explicit execution scope (6 tasks, BENCH2-001..006)

---

## 22. Final Status

```
P047 COMPLETE
LIVE C2 IMPLEMENTATION READY
C2 LIVE EXECUTION NOT AUTHORIZED
HUMAN EXECUTION AUTHORIZATION REQUIRED
```

---

**STOP after this document.**

Do not execute live C2. Do not call BENCH-002. Do not populate formal/C2-live/. Do not modify benchmark/oracle/Rta/MODEL-003. Do not push.
