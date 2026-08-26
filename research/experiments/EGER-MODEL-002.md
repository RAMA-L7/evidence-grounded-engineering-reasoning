# EGER-MODEL-002 — Live Model Configuration

| Field | Value |
|---|---|
| ID | EGER-MODEL-002 |
| Status | **NOT FROZEN — BLOCKED** (P014 gate) |
| Date | 2026-08-26 |
| Previous | EGER-MODEL-001 (FakeEngineerModel control, frozen) |
| Related | `eger/engineer/model.py` (`EngineerModel` interface) |

> This document records the investigation outcome for the live model required for formal C0–C5. It does **not** invent unavailable values. Per P011 §72 and P014 §16, critical UNKNOWN → NOT FROZEN.

---

## 1. Model ID

`EGER-MODEL-002` (intended live-model freeze — not yet assigned a live instance).

## 2. Provider

**UNKNOWN** — provisional candidates inspected:

- This session runs under **opencode / muse-spark-1.2-contributor-free** (`opencode/muse-spark-1.2-contributor-free`, 2026-08-26, win32).
- The `EngineerModel` abstraction (`eger/engineer/model.py`) is provider-neutral; it can wrap any provider that exposes a `generate(prompt) -> ModelResponse` call.
- No live provider has been **selected by documented non-performance criteria** and configured for identical use across C0–C5.

Recording `provider = opencode / muse-spark-...` as the formal experimental provider without explicit stability, version, and reproducibility guarantees would be fabrication.

## 3. Model Name

**UNKNOWN** — no live model name frozen for formal experiment. Session model (`muse-spark-1.2-contributor-free`) is a research-agent runtime, not a pinned experimental model.

## 4. Version

**NOT_EXPOSED** for this session's runtime (no provider-exposed version pin for `muse-spark-1.2`). Formal `model_version` requires a provider that exposes a version/snapshot date (e.g., `claude-4.5-sonnet-20241022`, `gpt-4o-2024-08-06`). Not yet selected.

## 5. Interface

- **EngineerModel interface:** `generate(prompt, **kwargs) -> ModelResponse` — frozen in `eger/engineer/model.py`, replaceable.
- **Live invocation mechanism:** **NOT FROZEN** — no live adapter (e.g., Anthropic API, OpenAI API, opencode model bridge) has been implemented and recorded with endpoint/interface details. The pilot used in-process `FakeEngineerModel` only.

## 6. Sampling

| Parameter | Status |
|---|---|
| temperature | **UNKNOWN** (proposed 0.0 for reproducibility, not frozen) |
| top_p | **UNKNOWN** (proposed 1.0, not frozen) |
| max output tokens | **UNKNOWN** (proposed cap 2048, not frozen) |
| seed (if supported) | **UNKNOWN** (provider-dependent, not frozen) |

No formal value invented.

## 7. Context

| Field | Status |
|---|---|
| Context limit | UNKNOWN (provider-dependent, not recorded) |
| Maximum prompt size used | UNKNOWN (will be prompt + design context per BENCH-002 task) |
| Output budget | UNKNOWN (proposed `max_tokens` above) |
| Tool-call budget | `max_model_calls = 5` per protocol — frozen, but model to which it applies is not |

## 8. Output Budget

See §6/7 — `max output tokens` UNKNOWN (proposed 2048).

## 9. Retry Policy

Per protocol: **infrastructure retry only** (transient network/provider 5xx, transport failure); reasoning failures (invalid SDC) are experimental attempts, not retries. Count/conditions frozen in protocol, but live retry behavior against an actual provider not yet documented with a live endpoint.

## 10. Timeout

**UNKNOWN** — proposed `request timeout 60s`, `overall run timeout 300s` per protocol, but not frozen against a live provider's actual timeout semantics.

## 11. Tool Access

- **Engineer allowlist:** same as `FakeEngineerModel` control (no arbitrary shell/filesystem, no RTA source write, no Git write, no `rta_generate`, no ledger write).
- **Live model tool access:** **UNKNOWN** — depends on chosen provider's tool-use mechanism; must be inspected and documented before freeze (P014 §13).

## 12. Prompt

`EGER-PROMPT-001` `eger.prompt.v1` — frozen neutral prompt, same as control. No tuning.

## 13. Reproducibility

- `FakeEngineerModel`: fully deterministic (already proven, 47/47).
- Live model: **NOT FROZEN** — reproducibility limited by provider sampling determinism (temperature 0 does not guarantee byte-identical outputs); would record `provider/model/version/sampling/pro prompt_hash/output_hash` per run, but cannot be frozen until provider selected and infrastructure test performed.

Infrastructure test (P014 §15) for live model: **NOT EXECUTED** — non-formal model_infrastructure_test would require a live endpoint; none selected, so no test run, correctly labeled `model_infrastructure_test = not executed, formal_experiment = false`.

## 14. Selection Criteria

Per protocol §16 and P014 §6, permitted criteria: availability, reproducibility, API stability, context capacity, output capacity, structured-output feasibility, tool/API compatibility, cost, rate-limit, operational reliability, ability to execute frozen proposal interface. **Not** “best preliminary EGER result”.

## 15. Selection Rationale

No live model selected — therefore no rationale to record beyond: selection must be by the non-performance criteria above, **before** any formal C0–C5 outcome is observed. Selecting now on the basis of pilot `INSUFFICIENT` artifacts would violate §1.

## 16. Non-performance Selection Evidence

No comparative performance experiments run. No benchmark outcomes used to select a model. Pilot used only `FakeEngineerModel`.

## 17. Known Limitations

- Session model `muse-spark-1.2-contributor-free` is a research-agent runtime, not a pinned experimental provider; using it as formal provider without version/API stability would not be reproducible.
- No live adapter implemented; invoking a live provider would require new code (`LiveEngineerModel`) with endpoint/auth handling — not yet built, so cannot be frozen.
- Live-model reproducibility claims must be scoped to provider documentation, not to EGER.

## 18. Freeze Status

**NOT FROZEN — BLOCKED.**

Per P014 §16, critical items remain `UNKNOWN`/`NOT_EXPOSED`/`NOT FROZEN` (provider, model, version, sampling, context, timeout, tool access). Fabrication would be worse than a blocked gate.

## 19. Hash / Identity Record

- **Control model hash:** `FakeEngineerModel v1.0` — deterministic, hash of `eger/engineer/model.py` at `6ae8275`.
- **Live model identity:** **NONE** — nothing to hash yet. Formal `MODEL-002` hash will be of this document + `model.py` live adapter at freeze time.

## 20. What Remains to Freeze MODEL-002

Select a provider by non-performance criteria, implement `LiveEngineerModel` adapter, record all fields above with `NOT_SUPPORTED`/`NOT_EXPOSED` where genuinely unavailable, perform a non-formal infrastructure test (model can be invoked, output captured, timeout works), and commit `EGER-MODEL-002.md` with status **FROZEN**. Until then, **P014 remains BLOCKED**.
