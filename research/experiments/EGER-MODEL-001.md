# EGER-MODEL-001 — Model Configuration

| Field | Value |
|---|---|
| ID | EGER-MODEL-001 |
| Status | **CONTROL FROZEN** (FakeEngineerModel) / **LIVE MODEL PROVISIONAL** (not frozen for formal experiment) |
| Date | 2026-08-26 |
| Related | `eger/engineer/model.py` |

## Purpose

Freeze the model configuration identity so every run manifest can resolve to an exact provider/model/configuration. Separate the deterministic control model (always frozen) from the live experimental model (to be frozen as MODEL-002).

## Control Model (frozen, for P008–P010 gates and dry-runs)

- **Provider:** `fake`
- **Model:** `fake-engineer-v1`
- **Version:** `1.0`
- **Interface:** `EngineerModel` (`eger/engineer/model.py`)
- **Sampling:** deterministic (no temperature/top-p; canned output or injected `fail_mode`)
- **Endpoint:** in-process Python (no network)
- **Max tokens / timeout / retry:** N/A — in-process, instantaneous
- **Tool budget:** not applicable (control)
- **Context config:** neutral prompt `eger.prompt.v1` only
- **Reproducibility:** fully deterministic; `prompt_hash` + `output_hash` deterministic per prompt; gate passes without network

This is the **control** for all deterministic-layer tests (47/47 PASS). P011 freezes it.

## Live Experimental Model (NOT FROZEN at P011 — documented as provisional)

P011 does **not** claim to have frozen the live model for formal C0–C5. The following are **REQUIRED but UNKNOWN at v0.1**:

| Field | Status at v0.1 |
|---|---|
| Provider (e.g. anthropic/openai) | UNKNOWN — provisional |
| Model name (e.g. claude-4.5-sonnet, gpt-4o) | UNKNOWN |
| Model version / snapshot date | UNKNOWN |
| Endpoint / API interface | UNKNOWN |
| Temperature | UNKNOWN |
| Top-p | UNKNOWN |
| Max output tokens | UNKNOWN (proposed cap: 2048) |
| Timeout | UNKNOWN (proposed: 60s) |
| Retry policy (technical) | per §14 of protocol: network 5xx only, otherwise no retry |
| Tool-call budget (per run) | per §13: `max_model_calls = 5` |
| Context configuration (max context, truncation) | UNKNOWN |

**Why not frozen now:** P011 is a scientific freeze gate; selecting a live provider on the basis of preliminary performance would violate model selection rule (§16). The interface (`EngineerModel`) is frozen; the concrete provider will be selected by documented criteria (availability, reproducibility, API stability, context capacity, cost) **before** any formal run, as `EGER-MODEL-002`, without changing L1/L2/L3/prompt/benchmark.

## Reproducibility Notes

- For `FakeEngineerModel`: fully reproducible by construction.
- For any future live model: reproducibility is limited by provider sampling determinism (temperature 0 does not guarantee byte-identical outputs on all providers); the experiment records all sampling parameters and prompt/output hashes so post-hoc analysis can quantify variance.

## Limitations

- Fake model cannot speak to real LLM reliability — it is a control, not a proxy.
- Live-model reproducibility claims must be scoped to provider documentation, not to EGER.

## Versioning

`MODEL-001` (this document) is immutable. A live-model freeze will be `MODEL-002` with its own hashes; runs must state which MODEL version they used. Silent provider switching between conditions is prohibited (anti-gaming).
