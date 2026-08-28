# EGER-P065 — RQ-4 Formal Execution

| Field | Value |
|---|---|
| ID | EGER-P065-RQ4-FORMAL-EXECUTION-001 |
| Date | 2026-08-28 |
| Authorization | EGER-AUTH-006-RQ4 |
| Status | **EXECUTION BLOCKED — PROVIDER FAILURE** |

---

## 1. Executive Summary

RQ-4 formal execution was attempted but BLOCKED by the model provider. The Nvidia upstream for `opencode/nemotron-3-ultra-free` returned 502 errors ("Service temporarily overloaded") and timed out on all attempts.

Per the frozen provider failure policy (AUTH-006 §7):
- No retries beyond the frozen budget
- No model substitution
- No canned fallback
- No fabrication of missing values

**Result: 0/6 tasks completed. All tasks classified as INCOMPLETE (provider failure).**

---

## 2. Authorization Reference

- EGER-AUTH-006-RQ4 — Formal RQ-4 Execution Authorized
- EGER-P064 — RQ-4 Formal Execution Authorization
- EGER-P063 — Post-Implementation Readiness (READY)
- EGER-P062 — Runner Implementation (162/162 tests)
- EGER-P061 — Controlled RQ-4 Experiment Design

---

## 3. Execution Configuration

| Parameter | Value |
|-----------|-------|
| Model | opencode/nemotron-3-ultra-free |
| Provider | opencode (Nvidia upstream) |
| Temperature | 0.0 |
| Max tokens | 2048 |
| Tools | [] |
| Timeout | 60s (increased to 120s during attempts) |
| Credential | PRESENT (OPENCODE_API_KEY) |
| Live mode | True |

---

## 4. Execution Attempt Log

### Attempt 1: Full 6-task run

- **Command:** `python formal_runner_rq4.py --live`
- **Timeout:** 600 seconds
- **Result:** TIMEOUT — no tasks completed
- **Artifacts:** None created

### Attempt 2: Single task (BENCH2-001)

- **Command:** Direct Python invocation with `live=True`
- **Timeout:** 180 seconds
- **Result:** TIMEOUT — Call 1 (initial candidate) failed after 120s
- **Error:** `Command 'opencode run --model opencode/nemotron-3-ultra-free' timed out after 120 seconds`
- **Classification:** MODEL_UNAVAILABLE (timeout)

### Attempt 3: Direct opencode CLI test

- **Command:** `opencode run --model opencode/nemotron-3-ultra-free <<< "Say OK"`
- **Timeout:** 90 seconds
- **Result:** TIMEOUT — no response
- **Artifacts:** None

### Attempt 4: Post-recovery test

- **Command:** `opencode run --model opencode/nemotron-3-ultra-free <<< "Say only: OK"`
- **Timeout:** 90 seconds
- **Result:** TIMEOUT — no response
- **Artifacts:** None

---

## 5. Provider Error Analysis

From `opencode.log`:

```
error.error.message="Streaming response failed: [502] Upstream error from Nvidia: Service temporarily overloaded"
error.error.type=server_error
```

The error is a 502 from the Nvidia upstream — the free-tier nemotron-3-ultra-free model is temporarily overloaded.

---

## 6. Frozen Failure Policy Applied

Per AUTH-006 §7:

| Rule | Applied |
|------|---------|
| Do not substitute another model | ✅ NO substitution |
| Do not retry beyond frozen budget | ✅ NO retries |
| Do not silently fall back to canned output | ✅ NO fallback |
| Do not fabricate missing values | ✅ NO fabrication |
| Record task as INCOMPLETE | ✅ RECORDED |

---

## 7. Task-Level Status

| Task | Status | Reason |
|------|--------|--------|
| BENCH2-001 | INCOMPLETE | Provider timeout (502 upstream) |
| BENCH2-002 | INCOMPLETE | Provider timeout (502 upstream) |
| BENCH2-003 | INCOMPLETE | Provider timeout (502 upstream) |
| BENCH2-004 | INCOMPLETE | Provider timeout (502 upstream) |
| BENCH2-005 | INCOMPLETE | Provider timeout (502 upstream) |
| BENCH2-006 | INCOMPLETE | Provider timeout (502 upstream) |

---

## 8. Artifact Inventory

| Item | Count |
|------|-------|
| RQ4 control manifests | 0 |
| RQ4 treatment manifests | 0 |
| RQ4 control raw artifacts | 0 |
| RQ4 treatment raw artifacts | 0 |
| RUN_INDEX.json | 0 |

No artifacts were created because no tasks completed.

---

## 9. Code Verification

- No code was modified during execution
- No files were changed
- No historical artifacts were touched
- 162/162 tests still pass

---

## 10. Preservation Verification

| Item | Status |
|------|--------|
| BENCH-002 | ✅ UNCHANGED |
| C0/C1/C2 | ✅ UNCHANGED |
| MODEL-003/004 | ✅ UNCHANGED |
| Ṛta | ✅ UNTOUCHED |
| Code | ✅ FROZEN |

---

## 11. Scientific Interpretation

**No RQ-4 result can be claimed.** The experiment was not executed due to provider failure.

This is classified as **MISSING DATA** per the frozen failure policy, not as:
- ❌ "Treatment ineffective"
- ❌ "No effect observed"
- ❌ "Experiment failed"

The provider failure is an infrastructure issue, not a scientific result.

---

## 12. What Must Happen Next

If RQ-4 execution is desired:

1. Wait for the Nvidia upstream to recover (service overload is temporary)
2. Verify nemotron-3-ultra-free is responsive with a test call
3. Re-authorize execution (AUTH-006 may need renewal if significant time passes)
4. Execute the frozen experiment

Alternatively:
- If the provider remains unreliable, consider whether a different free-tier model can serve as MODEL-005 (requires change control)
- Or whether the experiment should be deferred until provider stability improves

---

## 13. Status

```
P065 COMPLETE — RQ-4 EXECUTION BLOCKED BY PROVIDER FAILURE
0/6 tasks completed
ALL tasks INCOMPLETE (missing data)
NO scientific result claimed
NO code modified
NO artifacts created
C3 NOT AUTHORIZED
```
