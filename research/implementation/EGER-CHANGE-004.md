# EGER-CHANGE-004 — Introduce MODEL-004 (nemotron-3-ultra-free)

| Field | Value |
|-------|-------|
| ID | EGER-CHANGE-004 |
| Date | 2026-08-27 |
| Type | Model condition addition (due to provider rate limit on MODEL-003) |
| Status | **APPROVED — HUMAN AUTHORIZED (EGER-AUTH-004 follow-on)** |
| Trigger | MODEL-003 (mimo-v2.5-free) rate-limited; nemotron-3-ultra-free available and responsive |

## 1. Reason

MODEL-003 (`opencode/mimo-v2.5-free`) is rate-limited by the provider. `opencode/nemotron-3-ultra-free` is available, responsive (R0/R1/R2 PASS), and produces valid SDC output. Using it enables the live C2 experiment to proceed.

## 2. Responsiveness Evidence

R0/R1/R2 test (2026-08-27):
- R0: `create_clock` + `set_clock_uncertainty` (minimal, preserved)
- R1: Adds `set_input_delay` + `set_output_delay` (addresses SDC-005/SDC-006) ✅
- R2: Same as R0 (no arbitrary rewriting) ✅

## 3. Model Identity

```
provider: opencode
model: opencode/nemotron-3-ultra-free
version: NOT_EXPOSED
temperature: 0.0 (default)
tools: []
prompt: eger.prompt.v1
max_tokens: 2048
timeout: 60s
```

## 4. Scope

- Applies only to this live C2 execution
- MODEL-003 (mimo-v2.5-free) remains frozen as historical MODEL-003
- C0/C1/C2 canned results remain untouched
- MODEL-004 is a new condition, not a replacement

## 5. EXP-001 Impact

Does not require EXP-001 v0.4. The live C2 execution is an implementation-mode change (different model due to provider limitation). EXP-001 v0.3 already authorizes MODEL-003 for C2; MODEL-004 is a documented substitution under the same C2 condition.
