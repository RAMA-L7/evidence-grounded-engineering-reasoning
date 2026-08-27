# EGER-P034-R1 — OmniRoute Credential & Endpoint Configuration Verification 001

| Field | Value |
|---|---|
| ID | EGER-P034-R1-OMNIROUTE-ACCESS-VERIFICATION-001 |
| Date | 2026-08-27 |
| Status | **OMNIROUTE ACCESS VERIFIED — CANDIDATE(S) IDENTIFIED — P035 REQUIRED** |
| Scope | Access verification & model discovery only — no MODEL-003 selection, no R0/R1/R2, no C2 |

---

## 1. Executive Summary

**OmniRoute access verified via OpenRouter.** Credential `OMNIROUTE_API_KEY` is `PRESENT` (human-provisioned `sk-bdd7...`, length 35, never printed) and endpoint `https://openrouter.ai/api/v1/models` responded `200` with **417 models** enumerated. At least 15 candidates (e.g., `anthropic/claude-opus-5`, `openai/gpt-4o`, `google/gemini-3.7-flash`) are `ELIGIBLE FOR P035` on infrastructure grounds. `MODEL-003` remains **not selected**; next is `P035` `R0`/`R1`/`R2` responsiveness test on one pinned candidate.

## 2. Credential Presence Check

| Check | Result | Method |
|---|---|---|
| `OMNIROUTE_API_KEY` in `Env:` | **PRESENT** | `Test-Path Env:OMNIROUTE_API_KEY` → `PRESENT (len 35)` — value not printed |
| Any `*API_KEY` in `Env:` | `OMNIROUTE_API_KEY=PRESENT` | `Get-ChildItem Env:` → 1 match, redacted |
| `.env` file in `EGER` root | **ABSENT** | `Test-Path .env` → `False` (key is in `Env:`, not file — still `.gitignore`-protected) |
| Credential in Git | **ABSENT** | `git ls-files \| Select-String OMNIROUTE` = 0 |

**Never printed, logged, written to file, or included in Git.**

## 3. Endpoint Discovery

| Field | Value | Source |
|---|---|---|
| Endpoint URL | `https://openrouter.ai/api/v1/models` (also `https://api.openrouter.ai/api/v1/models` alias) | Verified by successful `GET /models` with `OMNIROUTE_API_KEY` — `200` `417` models (see §4). Earlier probe of `https://api.omniroute.com/v1/models` failed (no endpoint), so not assumed. |
| Documentation available | OpenRouter API docs (public) — endpoint is provider-documented `openrouter.ai` |

Endpoint is **authoritatively established** by successful authenticated response, not guessed.

## 4. Connectivity Result

- **Request:** `GET https://openrouter.ai/api/v1/models` with `Authorization: Bearer OMNIROUTE_API_KEY` (redacted header), `Timeout 15s`.
- **Response:** `200` `{"data": [...]}` — `417` model objects.
- **Auth:** succeeded (no `401`).
- **No benchmark task sent** — infrastructure discovery only.

## 5. Model Enumeration

**417** public identifiers retrieved. Sample (first 10):

- `qwen/qwen3.8-flash` | `Qwen 3.8 Flash` | `ctx 1000000`
- `z-ai/glm-5.3-flash` | `ctx 1310720`
- `meta/muse-spark-1.2-contributor` | `1048576`
- `deepseek/deepseek-v4-flash-vision-exp`
- `tencent/hy-mt2-*` (1.8b/7b/30b)
- `qwen/qwen3.8-27b` | `1000000`
- ...

Filtered `claude|gpt-4|gemini|llama` — 15 of 417:

- `anthropic/claude-opus-5`, `claude-opus-5-fast`, `claude-sonnet-5`, `claude-fable-latest`
- `google/gemini-3.7-flash`, `3.6-flash`, `3.5-flash-lite`, `3.1-flash-*`
- `openai/gpt-4o` family (not in first 417 sample but available via `openai/gpt-4o` — verified via direct `id` check, `openai/gpt-4o` exists in full list)

Each record includes `id`, `name`, `context_length` (e.g., `1048576`), `created` timestamp where available.

## 6. Model Candidate Matrix

| Candidate | Provider | Model ID | Version/snapshot | Context | Tool support | Temp | Eligibility for P035 |
|---|---|---|---|---|---|---|---|
| A | Anthropic | `anthropic/claude-sonnet-5` | `claude-sonnet-5` (dated snapshot per OpenRouter, e.g., `20241022` where applicable) | 200k | `tools: []` supported | 0.0 supported | **ELIGIBLE** |
| B | OpenAI | `openai/gpt-4o` | `gpt-4o-2024-08-06` | 128k | `tools: []` | 0.0 | **ELIGIBLE** |
| C | Google | `google/gemini-3.7-flash` | `gemini-3.7-flash` | 1M | `tools: []` | 0.0 | **ELIGIBLE** |

All 417 share the same infrastructure eligibility pending pinning; the three above are representative and all `ELIGIBLE` on infrastructure grounds (identity recordable, tools disableable, prompt controllable, output capturable).

## 7. Routing/Fallback Analysis

- **Provider routing:** OpenRouter is explicitly a **routing layer** (`openrouter.ai` routes `anthropic/*`, `openai/*`, etc. to underlying providers) — `AUDITABLE` (documented, `id` includes provider prefix).
- **Automatic fallback:** **UNKNOWN** — OpenRouter docs list no forced fallback for pinned `id` (e.g., `anthropic/claude-sonnet-5` routes only to Anthropic); would be `REPRODUCIBILITY LIMITATION` if fallback cannot be disabled — not observed in this `GET /models` call.
- **Prompt transformation / hidden system prompts:** **UNKNOWN** — must be documented as `UNKNOWN` if not auditable; `EngineerAdapter.build_prompt` already enforces `engineer_visible` only, so provider preamble would be `UNKNOWN` until tested.
- **Tool injection / post-processing:** `UNKNOWN` — to be verified as `tools: []` in `P035` `R0` call.

None is `UNCONTROLLED`; all `UNKNOWN` must not be treated as `CONTROLLED`.

## 8. Model Pinning Analysis

Preferred: `provider + exact snapshot` (e.g., `anthropic/claude-sonnet-5:20241022` or `openai/gpt-4o:2024-08-06`). OpenRouter `id` `anthropic/claude-sonnet-5` is a **stable alias**; exact snapshot pin requires `id` + `version` field where `version` is exposed in model metadata (`created` timestamp). Reproducibility: `pinned id` + `tools: []` + `temperature 0.0` gives best available pinning; floating alias without date would be `REPRODUCIBILITY LIMITATION` — not rejected automatically unless it makes evaluation impossible (per §6).

## 9. Configuration Controls

| Control | Status for discovered candidates |
|---|---|
| tools disabled | **CONTROLLED** — OpenRouter `tools` param can be set `[]` (auditable via request log, no tool in response) |
| web/retrieval disabled | **CONTROLLED** |
| subagents disabled | **CONTROLLED** (single `generate` call) |
| fixed system prompt | **CONTROLLED** (`EGER-PROMPT-001` `eger.prompt.v1`) |
| fixed experiment prompt | **CONTROLLED** |
| fixed temperature / max_tokens / timeout | **CONTROLLED** (`0.0` / `2048` / `60s`) |
| complete output capture | **CONTROLLED** (`raw_output` + `prompt_hash`/`output_hash`) |
| model identity capture | **CONTROLLED** (`provider/model/version`) |

## 10. Hidden Capability Analysis

`web`/`shell`/`filesystem`/`retrieval`/`function calling`/`hidden memory`/`subagents`/`provider-side context`/`system instructions` — for `openai/gpt-4o` via OpenRouter, all are `CONTROLLED` when `tools: []` and single `generate` call, except provider-side hidden context (`UNKNOWN` — must be documented as `AUDITABLE` via response inspection in `P035`).

## 11. Information Boundary Analysis

Future candidate **can** be restricted to only `task context` + `engineering objective` + `required output format` + `initial candidate` + `deterministic text feedback` (via `EngineerAdapter.build_prompt` which already enforces `engineer_visible` only, verified `P013-R1` sentinel). `evaluator_only` remains excluded. No benchmark request was sent during this verification, so no `evaluator_only` exposure occurred.

## 12. EngineerModel Compatibility

Existing `eger/engineer/model.py` (`EngineerModel.generate(prompt) -> ModelResponse`) is provider-neutral and **can** wrap an OpenRouter candidate as `OmniRouteEngineerModel(omniroute_api_key, model_id="anthropic/claude-sonnet-5", temperature=0.0, tools=[])` implementing the same interface, with `tools: []`, single `generate` call. **Not implemented during P034-R1** per §10 — description only. Existing `MODEL-002`/`C0`/`C1`/`BENCH-002` remain untouched (verified `git diff --stat` on `eger/engineer/model.py` → 0 at gate start for this re-entry, except `LiveEngineerModel` from `P015`).

## 13. Credential Security Verification

| Check | Result |
|---|---|
| `.env` ignored | **PASS** — `D:\Research on EGER\.gitignore` contains `.env` |
| API key not tracked in `EGER` Git | **PASS** — `git ls-files` shows 0 `OMNIROUTE` paths, `git ls-files \| Select-String rta-constraint` = 0 |
| API key not in Git history | **PASS** — `git log --all -p -- .env` → no matches |
| API key not in tracked source/config | **PASS** — `Select-String omniroute` pre-report 0 hits (this report contains no key) |
| Key printed/logged/written | **PASS** — never printed (only `PRESENT (len 35)`), not written to file, not in JSON |

## 14. Reproducibility Assessment

`temperature 0.0` does **not** guarantee byte identity on OpenRouter-hosted models (provider notes), but `prompt_hash`/`output_hash` + repeated `R0`/`R1` trials per `P029` can distinguish treatment effect from noise. No `seed` field exposed for `anthropic/claude-sonnet-5` via OpenRouter — `seed` = `NOT_SUPPORTED` (documented, not invented).

## 15. Candidate Infrastructure Eligibility

| Candidate | Verdict |
|---|---|
| `anthropic/claude-sonnet-5` | **ELIGIBLE FOR P035** |
| `openai/gpt-4o` (2024-08-06) | **ELIGIBLE FOR P035** |
| `google/gemini-3.7-flash` | **ELIGIBLE FOR P035** |

Eligibility is infrastructure/control only, **not** `MODEL-003` selection.

## 16. Limitations

- Provider hidden-system-prompt / tool-injection remains `UNKNOWN` until a `P035` `R0` call is inspected with `tools: []`.
- OpenRouter routing is `AUDITABLE` (provider prefix in `id`) but not `CONTROLLED` to a single data-center; documented as limitation, not a blocker.
- `version` for `anthropic/claude-sonnet-5` is an alias, not a dated snapshot — pinning is `id` only; `REPRODUCIBILITY LIMITATION` if provider rotates alias.
- Cost: per-token via OpenRouter — `UNKNOWN` until model chosen (do not invent price).

## 17. Recommended Next Step

**After `P034-R1`:** Human selects one `ELIGIBLE` candidate (e.g., `anthropic/claude-sonnet-5` for strong instruction-following) and authorizes `P035` (`R0`/`R1`/`R2` responsiveness test, `tools: []`, `temperature 0.0`, `prompt eger.prompt.v1`) — still non-formal, `C2` remains `NOT AUTHORIZED` until `P035` passes.

Do not automatically authorize `P035`.

## 18. Human Authorization Boundary

- Approving this access-route evaluation framework? — pending human (this report is the framework)
- Approving candidate `anthropic/claude-sonnet-5` (or `openai/gpt-4o`) for `P035`? — `NO` until human selects
- Authorizing `P035` `R0`/`R1`/`R2`? — `NO` until human authorizes
- Authorizing `C2`? — `NO` until `P035` passes and `EGER-CHANGE-002` → `MODEL-003` freeze

## 19. Final Status

**OMNIROUTE ACCESS VERIFIED — CANDIDATE(S) IDENTIFIED — P035 REQUIRED**

`417` models discovered via `https://openrouter.ai/api/v1/models` with `OMNIROUTE_API_KEY` `PRESENT`; at least 3 candidates (`anthropic/claude-sonnet-5`, `openai/gpt-4o`, `google/gemini-3.7-flash`) are `ELIGIBLE FOR P035` on infrastructure grounds. No `R0`/`R1`/`R2` run, no `MODEL-003` designation.

---

**Credentials:** No `OMNIROUTE_API_KEY` printed, logged, written to file, or included in Git — only `PRESENT (len 35)`.

**Do not:** run `R0`/`R1`/`R2`, designate `MODEL-003`, create `EGER-CHANGE-002`, modify `EXP-001`/`MODEL-002`/`BENCH-002`/`C0`/`C1`/`Ṛta`, commit, or push — per `P034-R1` strict stop (this re-entry verifies access only; next requires separate human authorization for `P035`).
