# EGER-MODEL-003 — Feedback-Responsive Model

| Field | Value |
|---|---|
| ID | EGER-MODEL-003 |
| Status | **FROZEN** (P038, responsiveness-eligible) |
| Date | 2026-08-27 |
| Previous | EGER-MODEL-002 (muse-spark-1.2, non-responsive) |

## 1. Identity

- **Model:** `opencode/mimo-v2.5-free`
- **Provider:** `opencode`
- **Version:** `mimo-v2.5-free` (provider does not expose dated snapshot → `NOT_EXPOSED` where version pin would be, documented)
- **Endpoint:** `opencode` local/runtime via `opencode run --model opencode/mimo-v2.5-free` (verified `200` in P037-R1 via `OPENCODE_API_KEY` `PRESENT len 67`)
- **Interface:** `EngineerModel.generate(prompt) -> ModelResponse` (`eger/engineer/model.py` — same as `MODEL-002`, no `rta_generate`)

## 2. Configuration

| Parameter | Value |
|---|---|
| temperature | `0.0` |
| top_p | `1.0` (or `NOT_SUPPORTED` if provider ignores) |
| max_tokens | `2048` |
| tools | `[]` (no web, retrieval, grounding) |
| prompt | `eger.prompt.v1` (EGER-PROMPT-001) |
| timeout | `60s` |
| model-call budget | `5` per `EXP-001` |
| seed | `NOT_SUPPORTED` |

## 3. Responsiveness Evidence

`P037-R1` (`EGER-P037-MODEL-003-RESPONSIVENESS-READINESS-001.md`):

- **R0** (no feedback, `create_clock` only) → `create_clock` only (preserved)
- **R1** (actionable `SDC-005`/`SDC-006`) → `create_clock` + `set_input_delay` + `set_output_delay` (addresses finding)
- **R2** (non-actionable `INFO`) → `create_clock` only (no arbitrary rewriting)
- **Classification:** `PASS` — all four `R-*` satisfied, information boundary preserved, `rta_generate` never invoked

This is the sole evidence for `MODEL-003` eligibility; no benchmark ranking was used.

## 4. Freeze

`MODEL-003` is frozen at this commit for subsequent `C2` (and later `C1` re-evaluation) — `C0` remains on `MODEL-002` as historical control.

## 5. Limitations

- `mimo-v2.5-free` alias, not dated snapshot — reproducibility limited to `provider/model/prompt_version/sampling` record, not provider snapshot date.
- `temperature 0.0` not guaranteeing byte identity (provider note) — will record `prompt_hash`/`output_hash` per run and repeat where needed.

## 6. Provenance

- P030 `FAIL` (muse-spark not responsive), P031 Route A, P032 candidate record (`EGER-CANDIDATE-001` originally `gpt-4o` via `openrouter` → `401`), P034 `GEMINI` 503, P037-R1 `mimo-v2.5-free` `PASS`.
- No `C0`/`C1`/`BENCH-002`/`Ṛta` modified to obtain this model.
