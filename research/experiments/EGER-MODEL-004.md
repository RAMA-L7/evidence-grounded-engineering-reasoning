# EGER-MODEL-004 — Feedback-Responsive Model (nemotron)

| Field | Value |
|---|---|
| ID | EGER-MODEL-004 |
| Status | **FROZEN** (CHANGE-004, responsiveness PASS) |
| Date | 2026-08-27 |
| Previous | EGER-MODEL-003 (mimo-v2.5-free, rate-limited) |

## 1. Identity

- **Model:** `opencode/nemotron-3-ultra-free`
- **Provider:** `opencode`
- **Version:** `NOT_EXPOSED` (provider does not expose dated snapshot)
- **Endpoint:** `opencode` local/runtime via `opencode run --model opencode/nemotron-3-ultra-free`
- **Interface:** `EngineerModel.generate(prompt) -> ModelResponse`

## 2. Configuration

| Parameter | Value |
|---|---|
| temperature | `0.0` (default) |
| top_p | `1.0` |
| max_tokens | `2048` |
| tools | `[]` |
| prompt | `eger.prompt.v1` |
| timeout | `60s` |
| seed | `NOT_SUPPORTED` |

## 3. Responsiveness Evidence

R0/R1/R2 test (2026-08-27):
- **R0** (no feedback): `create_clock` + `set_clock_uncertainty` → preserved
- **R1** (actionable SDC-005/SDC-006): Adds `set_input_delay` + `set_output_delay` → **addresses findings**
- **R2** (non-actionable): Same as R0 → **no arbitrary rewriting**
- **Classification:** PASS — responsive to actionable feedback, preserves under non-actionable

## 4. Limitations

- Free-tier model — subject to rate limits
- `temperature 0.0` not guaranteeing byte identity
- `version NOT_EXPOSED` — reproducibility limited to model/prompt/sampling record

## 5. Relationship to MODEL-003

MODEL-004 is introduced because MODEL-003 (mimo-v2.5-free) is rate-limited. Both are free-tier OpenCode models. MODEL-003 remains frozen as historical. MODEL-004 is used for this live C2 execution.
