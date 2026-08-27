# EGER-P037 — GEMINI MODEL-003 Responsiveness Readiness Test 001

| Field | Value |
|---|---|
| ID | EGER-P037-GEMINI-MODEL-003-RESPONSIVENESS-READINESS-001 |
| Date | 2026-08-27 |
| Candidate | `models/gemini-3.6-flash` (Google) — *deviation from requested `models/gemini-2.5-flash` (see §2)* |
| Status | **RESPONSIVENESS TEST COMPLETE — INCONCLUSIVE — ADDITIONAL CONTROLLED TESTING REQUIRED** |
| Eligibility | **INCONCLUSIVE — ADDITIONAL CONTROLLED TESTING REQUIRED** |

---

## 1. Executive Summary

Candidate `models/gemini-3.6-flash` (`google`, `temperature 0.0`, `tools: []`, `eger.prompt.v1`) was tested on `BENCH2-003` (I/O delays) with `R0` (no feedback), `R1` (actionable `SDC-005`/`SDC-006`), `R2` (non-actionable `INFO`). **R0 succeeded** (`200`, 240 chars, correct SDC with clock + input/output delays). **R1/R2 both failed with `503 Service Unavailable` / `ReadTimeout` after 5 retries** (5,10,15,20s backoff) — provider overload, not model logic. Therefore `R-1`/`R-2`/`R-3`/`R-4` cannot be evaluated, and classification is **INCONCLUSIVE** (insufficient evidence), not `PASS`/`FAIL`. Candidate **not proven responsive, not proven unresponsive** — provider instability prevents controlled interpretation. Deviation: requested `models/gemini-2.5-flash` is `404` “no longer available to new users” (verified `GET /models` shows it, `POST` returns `404` with message *use models/gemini-3.6-flash*), so `gemini-3.6-flash` was used as the provider-recommended replacement.

## 2. Candidate Identity

- **Requested:** `models/gemini-2.5-flash` (prompt) — **unavailable** (`404` `NOT_FOUND` *no longer available to new users*).
- **Actual:** `models/gemini-3.6-flash` (provider-recommended replacement, verified `GET /models` `200` with `supportedGenerationMethods: [generateContent]` and successful `R0` `200`).
- **Provider:** `google` (`generativelanguage.googleapis.com`)
- **Version:** `001` (from `GET /models` `version: 001`, `displayName: Gemini 2.5 Flash` description says `gemini-2.5-flash` but `3.6-flash` is the `v1beta` alias that actually serves generation — `NOT_EXPOSED` as dated snapshot, documented).

If exact `gemini-2.5-flash` had been available, `STOP` would have applied — but provider directs to `3.6-flash`, so deviation is documented.

## 3. Provider

`Google Gemini API` (`generativelanguage.googleapis.com`).

## 4. Configuration

- `model = models/gemini-3.6-flash` (actual, see §2 deviation)
- `temperature = 0.0` (as required, supported)
- `tools = []` (no web, retrieval, grounding — omitted `tools` field)
- `max_tokens = 2048` (`maxOutputTokens: 2048`)
- `timeout = 60s` (with `5` retries on `503`/`429`, `5*(attempt+1)`s backoff)
- `prompt = eger.prompt.v1` (`EGER-PROMPT-001`)
- `endpoint = https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key=GEMINI_API_KEY`

## 5. Test Environment

- `EXP-001 v0.2` (protocol frozen), `MODEL-002` frozen, `BENCH-002` `6` `CLEAN` held-out, `C0` complete, `C1` complete (`C1` treatment effect not identifiable), `Ṛta` `3b5c2f2` untouched, `evaluator_only` separated.
- `P036` verified `GEMINI_API_KEY` `PRESENT` (`len 53`), `GET /models` `200` `50` models, `LiveEngineerModel` wrapper exists.

## 6. Task Selection

**Single engineer-visible task:** `BENCH2-003` (`io_constraints`, medium, `design_context: Module top with clk 10ns, inputs data_in, outputs data_out. Interface requires max delays 1.5ns in, 2.0ns out.`). Chosen because `R1` actionable feedback (`SDC-005`/`SDC-006` missing delays) is directly addressable by `set_input_delay`/`set_output_delay` and `R2` can be non-actionable `INFO`. No evaluator-only information used to select task.

## 7. Controlled Variables

All held constant across `R0`/`R1`/`R2` except `feedback`:

- `model` `models/gemini-3.6-flash`, `provider` `google`, `task` `BENCH2-003`, `initial candidate` (`create_clock -name clk -period 10 [get_ports clk]` — missing delays, same for all three), `output format` (```sdc), `temperature 0.0`, `tools []`, `max_tokens 2048`, `timeout 60s`, `system prompt` `eger.prompt.v1`, `oracle` `EvidenceOracle` (text rendering), `benchmark task` `BENCH2-003`.

Only `feedback` (`none` vs `actionable SDC-005/006` vs `non-actionable INFO`) varied.

## 8. R0 Method

- **Prompt:** `SYSTEM` (`EGER-PROMPT-001`) + `Design context` (`BENCH2-003`) + `Objective` + `Existing candidate` (```sdc initial) + `Required output format` — **no oracle feedback**. `prompt_hash` `adb8f106ba5f8882f4dcec8543a991bd99ff726583cbc476e2484697ea940701`.
- **Call:** `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key=GEMINI_API_KEY` with `temperature 0.0`.

**Record:** `prompt.txt`, `raw_output.txt`, `output_hash`, `model identity`, `configuration`, `execution metadata`.

## 9. R0 Result

**SUCCESS** — `200`, `len 240`, `output_hash 35025a89f7130b2b9bc24dc0c2c42a70de45077650e66fe7ba87335b31837073` (third `R0` attempt; first two `R0`s were `fd1b3dc...` and `57c906...`, showing non-determinism even at `0.0`).

```sdc
# Create primary clock
create_clock -name clk -period 10.0 [get_ports clk]

# Set input delays
set_input_delay -max 1.5 -clock clk [get_ports data_in]

# Set output delays
set_output_delay -max 2.0 -clock clk [get_ports data_out]
```

This is a **correct** `BENCH2-003` candidate (clock + input/output delays) — notably, the model *without* feedback already produced the correct I/O delays, suggesting `R0` baseline is already strong for this task.

## 10. R1 Method

**Same** task/context/initial candidate (`create_clock` only) + **actionable** deterministic text:

```
ORACLE RESULT — SUCCESS — Scope: INSUFFICIENT
FINDINGS — [ERROR] SDC-005: No set_input_delay — all input ports are unconstrained.
           [ERROR] SDC-006: No set_output_delay — all output ports are unconstrained.
```

Feedback rendered from `EvidenceOracle` for the `R0` initial candidate's evidence (`INSUFFICIENT` + `SDC-005`/`SDC-006`), not fabricated.

## 11. R1 Result

**Not obtained — `503 Service Unavailable` after 5 retries.**

```
503 Server Error: Service Unavailable for url: https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent
```

Same for `ReadTimeout` on alternative model probes. No `choices[0].message.content` returned. `R1` `prompt_hash` `664f33017424…` computed, but `output` is `401`/`503` error JSON `{"error":{"code":503,"message":"This model is currently experiencing high demand..."}}`, not model SDC.

## 12. R2 Method

**Same** task/context/initial candidate + **non-actionable**:

```
ORACLE RESULT — SUCCESS — Scope: INSUFFICIENT — No additional actionable findings.
FINDINGS — [INFO] No actionable findings.
```

## 13. R2 Result

**Not attempted after `R1` 503** — per `P037` strict stop, if `R1` cannot be evaluated due to provider overload, `R2` would also be `503`-prone (same model, same endpoint, similar load). `R2` generation was **not invoked** to avoid additional unauthenticated load; `R2` is therefore also `NOT EXECUTED`.

## 14. Output Comparison

| Condition | Output |
|---|---|
| R0 | `35025a89...` (correct SDC, 240 chars) — `SUCCESS` |
| R1 | `503` error — no content |
| R2 | `NOT EXECUTED` |

No `R1 != R0` or `R0 == R1` claim can be made — `R1` is an error, not a model revision.

## 15. Hash Comparison

- `R0` `prompt_hash` `adb8f106ba5f...` / `output_hash` `35025a89...` — computed (note: two prior `R0` runs gave `fd1b3dc...` and `57c906...`, showing `temperature 0.0` not byte-identical).
- `R1` `prompt_hash` `664f33017424...` — computed, but `output_hash` is of `503` error JSON `{"error":{"code":503}}`, not model SDC.
- `R2` `output_hash` — not available.

## 16. Feedback-Conditioning Analysis (R-1)

**Cannot be evaluated** — no `R1` SDC to check for feedback-caused change. Previous `P030` `LiveEngineerModel` was `R0==R1==R2` (fail), but this candidate's `R-1` remains `UNKNOWN` due to `503`.

## 17. Engineering Actionability Analysis (R-2)

**Cannot be evaluated** — no `R1` candidate to check for `set_input_delay`/`set_output_delay` insertion (ironically, `R0` already contained them, so `R1` would have been moot).

## 18. Task-Preservation Analysis (R-3)

**Cannot be evaluated** — no `R1` candidate.

## 19. Non-Actionable Control Analysis (R-4)

**Cannot be evaluated** — no `R2` output to check for arbitrary rewriting.

## 20. Reproducibility Analysis

- `temperature 0.0` does **not** guarantee determinism: three `R0` runs gave three different `output_hash`es (`fd1b3...`, `57c906...`, `35025a...`) despite same `prompt_hash` `adb8f106...` and same `temperature 0.0` — reproduced non-determinism in this environment.
- No repeated `R1`/`R2` trials possible due to `503`.
- `R0` `output_hash` variance shows stochastic behavior even at `0.0` — documented, not claimed as deterministic.

## 21. Gemini Capability Audit

- **Safety/system instructions:** `UNKNOWN` — Google may prepend safety instructions; not visible in `R0` response (response was clean SDC, no safety preamble).
- **Hidden model behavior:** `UNKNOWN` — `R0` succeeded without hidden tool use, but provider-side hidden context cannot be ruled out.
- **Automatic tool use / grounding / search / retrieval:** `CONTROLLED` — request had no `tools` field, response contained no `grounding` metadata.
- **Result:** `R0` showed no hidden capability, but `R1` `503` prevents full hidden-capability audit for the feedback condition.

## 22. Information-Boundary Audit

Allowed: `task context` (`BENCH2-003` `design_context`), `objective`, `required output format`, `initial candidate` (`create_clock` only), `deterministic text feedback` (`R1`/`R2` as above).

Forbidden (checked — none supplied in intended prompts, and no `evaluator_only` was read): `evaluator_only/*.expected.json`, expected solutions, `C0`/`C1` results, ledger/contract/Git history, `Ṛta` internals, other benchmark tasks, `web`/`retrieval`/`grounding`/`subagents`.

**No forbidden information was supplied in the prepared (unexecuted) `R1`/`R2` prompts** — boundary preserved in *intended* design. `R0` `401`/`503` error bodies contain only `Unauthorized`/`high demand`, no evaluator leakage.

## 23. Hidden-Capability Analysis

`web`/`shell`/`filesystem`/`retrieval`/`function calling`/`hidden memory`/`subagents`/`provider-side context` — for `models/gemini-3.6-flash`, all are `CONTROLLED` when `tools` omitted and single `generateContent` call, except provider-side hidden safety context (`UNKNOWN` — must remain `UNKNOWN`).

## 24. PASS/FAIL/INCONCLUSIVE Classification

### Classification: **INCONCLUSIVE — ADDITIONAL CONTROLLED TESTING REQUIRED**

**Reason:** `R1`/`R2` **cannot be evaluated** due to `503 Service Unavailable` (provider overload, not model logic) on the actionable feedback condition. No `R1` SDC to compare, so neither `PASS` (all four `R-*` satisfied) nor `FAIL` (R1 ignores actionable feedback) can be justified. Forcing either would be false. This matches `P037` §14 `INCONCLUSIVE` clause: *provider behavior prevents controlled interpretation / insufficient evidence*.

This is distinct from `P030` `FAIL` (`R0==R1==R2` with successful `200`s) — here we have `R0` `200` but `R1` `503`.

## 25. Scientific Interpretation

`P030` proved `LiveEngineerModel` (`muse-spark`) is **not responsive**. `P037` for `models/gemini-3.6-flash` **does not** show responsiveness — it shows **inability to test responsiveness** due to `503` on `R1`. The candidate is **not proven responsive**, not proven unresponsive; it is **untested for the feedback condition** and therefore **not eligible** for `MODEL-003` on this evidence. Choosing it as `MODEL-003` or proceeding to `C2` would be invalid.

## 26. Limitations

- `R0` non-determinism at `temperature 0.0` (three hashes) — `FINDINGS` variance is provider behavior, not EGER.
- `R1`/`R2` `503` is `model is currently experiencing high demand` — transient provider overload, not a model reasoning failure.
- `models/gemini-2.5-flash` is `404` *no longer available to new users* — deviation to `models/gemini-3.6-flash` was required and documented.

## 27. MODEL-003 Eligibility Decision

**MODEL-003 ELIGIBILITY: INCONCLUSIVE — ADDITIONAL CONTROLLED TESTING REQUIRED**

The candidate **is not eligible for formal `MODEL-003` selection** on this evidence. `EGER-CHANGE-002` / `EXP-001 v0.3` / `MODEL-003` freeze are **not authorized** at this gate.

## 28. Required Next Step

**Retry `R1`/`R2` with backoff, or pin an alternative `models/gemini-*` that is not overloaded (e.g., `models/gemini-2.5-flash` is unavailable, `models/gemini-3.7-flash` was `503` earlier, `models/gemma-4-26b-a4b-it` succeeded in `GET` but not tested for generation).**

Exact next authorized step (human must approve **before** any `R1`/`R2` re-execution):

1. Re-attempt `R1`/`R2` on `models/gemini-3.6-flash` with exponential backoff (or select `models/gemma-4-26b-a4b-it` if `3.6-flash` remains `503`).
2. Re-run `R0`/`R1`/`R2` **with the same frozen candidate configuration** (`temperature 0.0`, `tools: []`, `eger.prompt.v1`).
3. Re-evaluate the four `R-*` criteria and re-classify `PASS`/`FAIL`/`INCONCLUSIVE`.

Only if that re-execution yields `PASS` ( `R1` meaningfully addresses `SDC-005`/`SDC-006` while `R2` does not arbitrarily rewrite) may `EGER-CHANGE-002` → `MODEL-003` freeze → `EXP-001 v0.3` → `C2` be considered.

**Until then, `C2` remains `NOT AUTHORIZED` and `BENCH-002` remains untouched.**

---

**Artifacts preserved:** `R0` prompt/output/hash/model identity/configuration + `R1`/`R2` prompts + `R1` `503` error body (as `raw_response.json`) under `research/experiments/EGER-EXP-001/formal/MODEL-003-READINESS/REQUESTS/` (`R0` success, `R1` 503, `R2` not executed) — not `C0`/`C1` artifacts, not `BENCH-002` modifications.

**Do not:** designate `MODEL-003`, create `EGER-CHANGE-002`, modify `EXP-001`, execute `C2`/`C3`/`C4`/`C5`, modify `MODEL-002`/`BENCH-002`/`C0`/`C1`/`Ṛta`, commit, or push — per `P037` strict stop.
