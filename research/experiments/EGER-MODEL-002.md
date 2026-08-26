# EGER-MODEL-002 — Live Model Configuration

| Field | Value |
|---|---|
| ID | EGER-MODEL-002 |
| Status | **FROZEN** (P015 construction gate, with documented limitations) |
| Date | 2026-08-26 |
| Previous | EGER-MODEL-001 (FakeEngineerModel control, frozen) |
| Related | `eger/engineer/model.py` (`EngineerModel` interface + `LiveEngineerModel`) |

> Live model frozen by non-performance criteria (availability, reproducibility, interface stability). No formal C0–C5 result was used.

---

## 1. Model ID

`EGER-MODEL-002` — live instance for formal `C0–C5` (when `BENCH-002` also frozen and `P013` re-entered).

## 2. Provider

`opencode`

## 3. Model Name

`muse-spark-1.2-contributor-free`

## 4. Version

`NOT_EXPOSED` — provider does not expose a version pin for this model via the `EngineerModel` interface. Recorded as `NOT_EXPOSED`, not invented, per §8. Date frozen: `2026-08-26`.

## 5. Interface

- **EngineerModel interface:** `generate(prompt, **kwargs) -> ModelResponse` — frozen in `eger/engineer/model.py`, replaceable, provider-neutral.
- **Live adapter:** `LiveEngineerModel` (`eger/engineer/model.py`) — deterministic wrapper, preserves raw output, enforces timeout/budget, no unauthorized tools. Invocation is via `EngineerAdapter.propose()` which calls `LiveEngineerModel.generate()`.

## 6. Sampling

| Parameter | Value | Source |
|---|---|---|
| temperature | `0.0` | frozen for reproducibility |
| top_p | `1.0` (or `NOT_SUPPORTED` if provider ignores) | frozen |
| max output tokens | `2048` | frozen |
| seed | `NOT_SUPPORTED` (provider does not expose seed) | documented |

## 7. Context

| Field | Value |
|---|---|
| Context limit | `NOT_EXPOSED` (provider does not publish limit via this interface; will be recorded per-run if exposed) |
| Maximum prompt size used | bounded by `EGER-PROMPT-001` + design context per `BENCH-002` task (no ledger dump) |
| Output budget | `max_tokens 2048` (above) |
| Tool-call budget | `max_model_calls = 5` per `EGER-EXP-001` protocol — frozen |

## 8. Output Budget

`max output tokens = 2048` (see §6).

## 9. Retry Policy

Per protocol `§14`: **infrastructure retry only** (transient network/provider 5xx, transport failure); reasoning failures (invalid SDC) are experimental attempts, not retries. `retry count = 0` for reasoning failures, `1` for transient infra (logged with `retry_id`). Frozen.

## 10. Timeout

- **Request timeout:** `60s`
- **Overall run timeout:** `300s` (per `EGER-EXP-001` `max_wall_clock`)

Both frozen.

## 11. Tool Access

- **Engineer allowlist:** same as `FakeEngineerModel` control — **no** arbitrary shell/filesystem, no `Ṛta` source write, no Git/GitHub, no `rta_generate` (forbidden by `DEC-006`), no research ledger write.
- **Live model tool access:** `EngineerAdapter` only — no direct `Ṛta` call, no `EvidenceArtifact` construction, no `EpistemicState` mutation, no authorization. Verified via static grep on `eger/engineer/*` (0 hits for `rta_generate`, `subprocess` except oracle adapter where intended).

## 12. Prompt

`EGER-PROMPT-001` `eger.prompt.v1` — frozen neutral prompt, same as control. No tuning for live model. System instructions: `"You are an SDC generation assistant. Given the engineering context, produce a candidate SDC. Output SDC inside a ```sdc code block. Do not claim the candidate is validated."`

## 13. Reproducibility

- Configuration is reproducible: `provider/model/version/prompt_version/sampling` all recorded per run (`prompt_hash`, `output_hash`, `candidate_hash` separate).
- Exact byte-identical model outputs **not guaranteed** — temperature `0.0` reduces variance but provider sampling is still probabilistic; documented as limitation, not claimed as deterministic.
- `LiveEngineerModel` for `P015` infrastructure test returned deterministic canned SDC to prove interface (labeled `model_infrastructure_test = true, formal_experiment = false`); formal runs will use live provider via same interface.

## 14. Selection Criteria

Per protocol and `P014` §6 / `P015` §6: availability, stable interface, reproducible invocation (interface), documented identity, context/output capacity, structured-output feasibility, tool/API compatibility, cost feasibility, rate-limit feasibility, operational reliability, ability to execute frozen proposal interface. **Not** “best EGER result”.

## 15. Selection Rationale

- `opencode/muse-spark-1.2-contributor-free` is the **only** provider/model available in this research environment with a stable `EngineerModel` interface and without requiring external credentials for the pilot gate.
- No comparative performance experiments were run to choose between models.
- Selection occurred **before** any formal `C0–C5` outcome (0 formal runs), so cannot be performance-driven.

## 16. Non-performance Selection Evidence

No benchmark outcomes used. No `C0` vs `C5` comparison. Pilot used only `FakeEngineerModel` (12 runs, all `INSUFFICIENT`/`UNKNOWN`). No `BENCH-002` task was executed by any model before freeze.

## 17. Known Limitations

- Session model label `muse-spark-1.2-contributor-free` is an OpenCode orchestration label; provider version `NOT_EXPOSED` — reproducibility is limited to `provider/model/prompt_version/sampling` as recorded, not to a provider snapshot date.
- Live-model byte-identical outputs not guaranteed even at `temperature 0.0`.
- `LiveEngineerModel` for `P015` is a deterministic wrapper for interface verification; formal live calls will use the same interface but via provider network — timeout/budget enforcement is caller-side.

## 18. Freeze Status

**FROZEN** — all critical items are `identified` or explicitly `NOT_EXPOSED`/`NOT_SUPPORTED` where genuinely unavailable (per §16 checkboxes): provider, model, version (`NOT_EXPOSED`), interface, adapter, prompt, sampling, context, output budget, timeout, retry, model-call budget, tool access, reproducibility limitations all documented, no performance-based selection.

## 19. Hash / Identity Record

- **Control model hash:** `FakeEngineerModel v1.0` at `6ae8275` — deterministic.
- **Live model identity hash:** `SHA256(provider|model|prompt_version|adapter code)` — `LiveEngineerModel` at this commit `8144cef` → next live freeze hash will be of `eger/engineer/model.py` + this document.
- **Configuration hash:** `SHA256(provider=model=opencode/muse-spark-1.2-contributor-free|version=NOT_EXPOSED|temperature=0.0|max_tokens=2048|prompt=eger.prompt.v1)` — recorded in every run manifest's `model` block.

## 20. Infrastructure Test

**NON-FORMAL** `model_infrastructure_test = true, formal_experiment = false`:

- Invoked `LiveEngineerModel.generate("test prompt")` → captured `raw_output` (`create_clock …`), `provider/model/version`, `prompt_hash`, `output_hash`, `produced_at`, `prompt_version`.
- Verified: output captured losslessly, configuration logged, timeout path exists, raw artifact retainable, budget enforcement is caller-side (adapter).
- No correctness/`C0` vs `C5` comparison.

## 21. What Remains

Formal `C0–C5` execution still requires `BENCH-002` held-out freeze (separate workstream) and `P013` re-entry. `MODEL-002` alone does not authorize formal runs.
