# EGER-P032 — Candidate Model Acquisition & Controlled Setup

| Field | Value |
|---|---|
| ID | EGER-P032 |
| Date | 2026-08-27 |
| Status | CANDIDATE ACQUIRED AND CONFIGURATION RECORDED — RESPONSIVENESS TEST PENDING |
| Authorization | P031 Route A (External API) approved by human |
| Candidate | OpenAI `gpt-4o` (candidate, not MODEL-003) |
| Previous | P031 access plan, P030 FAIL (LiveEngineerModel not responsive) |

## 1. Acquisition Objective

Obtain ONE external-API candidate model, configured for the frozen `EngineerModel` interface, with all identity/configuration recorded, information boundary enforced, and reproducibility preserved — **without** running `R0/R1/R2` responsiveness tests, **without** designating as `MODEL-003`, **without** `EGER-CHANGE-002`, **without** `C2`.

## 2. Selected Candidate (Route A)

- **Provider:** OpenAI
- **Model:** `gpt-4o` (snapshot `gpt-4o-2024-08-06` — pinned)
- **Version:** `2024-08-06`
- **Interface:** `EngineerModel.generate(prompt)` via `LiveEngineerModel` adapter (same as `MODEL-002` interface)
- **Endpoint:** `https://api.openai.com/v1/chat/completions` (OpenAI API)
- **Library:** `openai` package (installed, verified `pip show openai`)
- **System prompt:** `EGER-PROMPT-001` `eger.prompt.v1` (unchanged)
- **Config:** `temperature: 0.0`, `top_p: 1.0`, `max_tokens: 2048`, `seed: NOT_SUPPORTED` (OpenAI does not guarantee seed determinism at 0), `timeout: 60s`, `model-call budget: 5`, `tools: []` (no function calling), `web: disabled`, `retrieval: disabled`, `memory: disabled`, `subagents: disabled`
- **Candidate ID:** `EGER-CANDIDATE-001`

This candidate was selected by **Route A non-performance criteria** (availability of `openai` package, stable versioned API, `tools: []` auditable) per P031, not by benchmark performance.

**Not yet verified live:** No API credentials configured in this environment (`OPENAI_API_KEY` not set — read-only `os.environ` check). Candidate is **acquired as configuration**, not yet live-tested. Actual network call will be performed only in P033 with separate human authorization.

## 3. Configuration Record

Frozen for this candidate:

```
provider: openai
model: gpt-4o
model_version: gpt-4o-2024-08-06
endpoint: https://api.openai.com/v1/chat/completions
system_prompt: eger.prompt.v1 (EGER-PROMPT-001)
experiment_prompt: eger.prompt.v1 (same)
temperature: 0.0
top_p: 1.0
max_tokens: 2048
seed: NOT_SUPPORTED
timeout: 60
context length: provider-documented (128k for gpt-4o, not enforced by EGER)
tool configuration: tools: [] (no web, no retrieval, no function calling, no code execution)
external network: required (OPENAI_API_KEY)
model-call budget: 5
```

## 4. Information Boundary

Verified for this candidate:

- **Receives:** `engineer_visible` task data (`BENCH2-00*.json` design_context/objective), allowed prompt/context (`eger.prompt.v1`), allowed deterministic text feedback (`R1` will be deterministic oracle text) — same as `LiveEngineerModel` in P015.
- **Does NOT receive:** `evaluator_only/*.expected.json`, hidden labels, other benchmark tasks, `C0`/`C1` conclusions, research ledger/contract, Git history, `Ṛta` source/test fixtures, hidden oracle internals, future `C2` conditions.
- **Enforcement:** `EngineerAdapter.build_prompt()` only injects `engineer_visible` context; no wildcard workspace read; `LiveEngineerModel` has no file-read.

## 5. Hidden Capability Audit

| Capability | Status |
|---|---|
| web access | CONTROLLED (disabled, `tools: []`) |
| shell | CONTROLLED (no tool) |
| filesystem | CONTROLLED |
| retrieval | CONTROLLED (disabled) |
| external tools / function calling | CONTROLLED (`tools: []`) |
| hidden memory | AUDITABLE (per-call stateless, no conversation memory) |
| subagents | CONTROLLED (single `generate` call) |
| provider-side system instructions | AUDITABLE (must be `EGER-PROMPT-001` only, no hidden preamble) |

## 6. Reproducibility

- `temperature 0.0` does not guarantee byte-identical outputs (OpenAI note) — will record `prompt_hash`/`output_hash`/`candidate_hash` per run and repeat `R0/R1/R2` N≥3 to distinguish treatment effect from noise.
- `seed` NOT_SUPPORTED — documented as limitation, not invented.
- No `rta_generate`, no `Ṛta` modification, no research-memory modification.

## 7. Preservation of Existing Frozen Artifacts

- `MODEL-002` (`opencode/muse-spark-1.2`) remains **frozen and untouched** — not modified.
- `BENCH-002 v0.1` (6 tasks) remains frozen, hidden answers separated — not modified.
- `Ṛta` `3b5c2f2` untouched, `rta_generate` never invoked.
- `C0`/`C1` artifacts untouched.
- `EXP-001 v0.1` unchanged.
- No subagents, no `C1` re-execution, no `C2` execution, no `EGER-CHANGE-002`.

## 8. What Was NOT Done

- No `R0/R1/R2` responsiveness test (pending P033).
- No candidate designated as `MODEL-003`.
- No `EGER-CHANGE-002` created or approved.
- No `C2` executed.
- No credentials obtained/installed (candidate is configuration-only at this gate).
- No formal experiment, no push.

## 9. Next Step

**Responsiveness test pending human/separate authorization:** `P033 — Responsiveness Readiness Test (R0/R1/R2)` per `P029` criteria, using this `EGER-CANDIDATE-001` configuration. Only if `R1 != R0` when feedback is actionable (and `R2 == R0` when not) does candidate become eligible for `MODEL-003` selection.

## 10. Human Decisions Required

1. Authorize `R0/R1/R2` responsiveness testing on this candidate?
2. Approve API credential provisioning for `openai`?
3. Authorize `P033` execution?
