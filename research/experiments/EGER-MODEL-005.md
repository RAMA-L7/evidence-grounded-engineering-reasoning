# EGER-MODEL-005 — RQ-4 Controlled Experiment Model (mimo)

| Field | Value |
|---|---|
| ID | EGER-MODEL-005 |
| Status | **FROZEN** (CHANGE-008, responsiveness verified) |
| Date | 2026-08-28 |
| Previous | EGER-MODEL-004 (nemotron-3-ultra-free, provider unavailable) |

---

## 1. Identity

- **Model:** `opencode/mimo-v2.5-free`
- **Provider:** `opencode`
- **Version:** `NOT_EXPOSED`
- **Endpoint:** `opencode` local/runtime via `opencode run --model opencode/mimo-v2.5-free`
- **Interface:** `EngineerModel.generate(prompt) -> ModelResponse`

---

## 2. Configuration

| Parameter | Value |
|---|---|
| temperature | `0.0` |
| top_p | `1.0` |
| max_tokens | `2048` |
| tools | `[]` |
| prompt | `eger.prompt.v1` |
| timeout | `60s` |
| seed | `NOT_SUPPORTED` |

---

## 3. Responsiveness Evidence

Verified 2026-08-28:
- Test: `opencode run --model opencode/mimo-v2.5-free <<< "Say OK"` → "OK"
- SDC generation: verified with clock/I/O constraint prompt
- Classification: **RESPONSIVE**

---

## 4. Relationship to MODEL-003

MODEL-005 uses the same model as historical MODEL-003 (mimo-v2.5-free). They are separate experimental conditions:
- MODEL-003: C2 canned execution (P041-P043)
- MODEL-005: RQ-4 controlled experiment (new)

MODEL-003 historical results remain as background context only.

---

## 5. Relationship to MODEL-004

MODEL-004 (nemotron-3-ultra-free) is provider-unavailable. MODEL-005 is introduced to enable RQ-4 execution. MODEL-004 results remain as historical background.

---

## 6. Limitations

- Free-tier model — subject to rate limits
- `temperature 0.0` not guaranteeing byte identity
- `version NOT_EXPOSED` — reproducibility limited to model/prompt/sampling record
- Results specific to BENCH-002 v0.1 under mimo-v2.5-free
