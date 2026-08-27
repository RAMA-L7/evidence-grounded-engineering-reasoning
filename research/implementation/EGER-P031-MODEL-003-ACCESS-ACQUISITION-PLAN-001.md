# EGER-P031 — MODEL-003 Access & Candidate Acquisition Plan 001

| Field | Value |
|---|---|
| ID | EGER-P031-MODEL-003-ACCESS-ACQUISITION-PLAN-001 |
| Date | 2026-08-27 |
| Status | ACCESS PLAN COMPLETE — ROUTE RECOMMENDED — HUMAN DECISION REQUIRED |
| Prior | P030 — NO ELIGIBLE MODEL-003 (LiveEngineerModel failed responsiveness: R0==R1==R2) |
| Scope | Access & acquisition plan only — no MODEL-003 selection, no model execution |

---

## 1. Executive Summary

P030 established that the only available `LiveEngineerModel` (opencode/muse-spark-1.2-contributor-free) is **not feedback-responsive** and therefore **not eligible for MODEL-003**. P031 defines a controlled path to obtain a candidate that can later be evaluated under P029. **Recommended route: Route A — External API (controlled, provider-pinned) as primary, with Route B — Local Open-Weight as scientifically strongest alternative if hardware/weights can be provisioned.** No candidate is selected here; next stage is `MODEL CANDIDATE ACQUISITION → RESPONSIVENESS READINESS TEST → ELIGIBILITY`.

## 2. Current Environment

**Verified read-only (P030 factual starting point):**
- `LiveEngineerModel` available (`eger/engineer/model.py`) — tested in P030 across R0 (no feedback), R1 (actionable feedback), R2 (no actionable issue): `R0==R1==R2` → Responsiveness = FAIL.
- `openai` package **installed** (importable), `anthropic` package **installed** — `pip list` verified pre-P031.
- No API credentials configured (no `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` in env; no `.env` with secrets — read-only `os.environ` check, no file read beyond `.gitignore` + `env` scan that found none).
- No local model server running (`GET http://localhost:11434` / `8000` not probed by network call; instead read-only check: no `ollama`/`vllm`/`llama.cpp` server process or config file in repo — none found).
- No eligible MODEL-003 candidate; `MODEL-002` remains frozen (`opencode/muse-spark-1.2`); `BENCH-002` frozen; `C0/C1` complete (`C1` treatment effect not identifiable per C1 review); `C2` not authorized; `Ṛta` untouched; `EXP-001 v0.2` frozen.

No installation, download, or external call was performed for this plan.

## 3. Scientific Purpose

Establish a **reproducible path to a feedback-responsive candidate** that can be evaluated as possible `MODEL-003` — not to find the most powerful LLM, and not to claim performance. Maintain the gate sequence:

```
MODEL ACCESS → MODEL CANDIDATE → RESPONSIVENESS READINESS TEST (P029/P030)
  → MODEL-003 ELIGIBILITY → MODEL-003 FREEZE (EGER-CHANGE-002) → FORMAL EXPERIMENT
```

Skipping a gate would contaminate `C2`.

## 4. Access Route Analysis

### Route A — External API (hosted LLM via provider API)

- **Model identity:** Provider (e.g., Anthropic, OpenAI) + model name + version/snapshot (e.g., `claude-4-5-sonnet-20241022`) — **must be provider-pinned**. Version availability varies: Anthropic exposes dated snapshots; OpenAI exposes `gpt-4o-2024-08-06` style.
- **API reproducibility:** Snapshot pin gives reproducibility of *identity*; output reproducibility limited (temperature 0 not byte-identical, provider notes). Trial repetition can distinguish treatment effect from noise.
- **Provider drift:** Possible (provider updates fingerprint, deprecations) — mitigated by pinning snapshot + recording `model_version` + `system_fingerprint` per run.
- **Hidden capabilities:** `web_search`, `code execution`, `file search`, `function calling` must be **disabled** (provider `tools: []`); system prompt must be only `EGER-PROMPT-001`.
- **Network dependency:** Requires internet + credentials; rate limits apply.
- **Cost:** Per-token API cost (unknown exact price until provider/model chosen — see §12).
- **Data handling:** Prompt contains only `BENCH-002` design context (6 tasks) — not sensitive PII, but provider data-use policy must be reviewed.

**Do not call an API at P031.**

### Route B — Local Open-Weight Model

- **Hardware:** Requires GPU RAM for 7–70B quantized models (e.g., 7B ~8GB, 14B ~16GB, 70B ~40GB+); CPU fallback possible but slow.
- **Runtime:** `ollama` / `vLLM` / `llama.cpp` — not currently running; would need weight download.
- **Versioning:** Model weights versioned by HF repo + commit hash — strong reproducibility.
- **Determinism:** Local `temperature 0 + seed` can be closer to deterministic than API, depending on backend.
- **Reproducibility:** **Strongest** — fully local, no provider drift, no network.
- **Cost:** One-time download + local compute (no per-token fee).
- **Tradeoff:** Requires hardware not verified available in this Windows workspace.

**Do not download or run a model at P031.**

### Route C — Existing Accessible Runtime

- Definition: an already-running local server or approved endpoint in the environment.
- **Finding:** None identified — no server process, no `docker` model container, no `ollama` config found in repo read-only scan.
- **Assessment:** `INCONCLUSIVE` — would be `CLEAN` if one existed, but none does; would still require identity/tool audit before use.

**Do not start services at P031.**

### Route D — Other Controlled Provider/Runtime

- Any other legitimate provider (e.g., institutional API gateway, Azure-hosted model) — must be explicitly characterized with same fields as Route A. No such route is currently documented in this environment; would require new characterization before use.

## 5. Mandatory Requirements

| # | Requirement | Route A (API) | Route B (Local) | Route C (Existing) |
|---|---|---|---|---|
| 1 | Feedback responsiveness can be tested | YES | YES | UNKNOWN (none) |
| 2 | Model identity can be recorded | YES (provider/model/snapshot) | YES (HF repo+hash) | NO |
| 3 | Model/version can be frozen | YES (pin snapshot) | YES (weight hash) | NO |
| 4 | EngineerModel interface can be satisfied | YES | YES | NO |
| 5 | Task context can be supplied | YES | YES | — |
| 6 | Existing candidate can be supplied | YES | YES | — |
| 7 | Deterministic text feedback can be supplied | YES | YES | — |
| 8 | Output can be captured verbatim | YES | YES | — |
| 9 | Information boundary can be enforced | YES (prompt only `engineer_visible`) | YES | UNKNOWN |
| 10 | Evaluator-only excluded | YES | YES | UNKNOWN |
| 11 | Hidden tools can be audited | AUDITABLE (tools: []) | CONTROLLED (no tools by default) | UNKNOWN |
| 12 | Subagents can be excluded/identified | YES (single call) | YES | UNKNOWN |
| 13 | Configuration can be recorded | YES | YES | NO |
| 14 | Repeated evaluation possible | YES | YES | NO |
| 15 | Results can be preserved | YES | YES | NO |

## 6. Model Access vs Model Selection

**Access** = obtaining a runtime that can satisfy the 15 mandatory requirements above. **Selection** = promoting a *candidate* that passes the P029 responsiveness readiness test to `MODEL-003` via `EGER-CHANGE-002`.

Sequence `ACCESS → CANDIDATE → TEST → ELIGIBILITY → FREEZE` must not be collapsed; access alone does not make a model `MODEL-003`.

## 7. Selection-Bias Controls

All candidate eligibility criteria come from **P029/P030 before candidate selection**:

- Responsiveness: `R1` must differ from `R0` when feedback is actionable, and `R2` must not change when no actionable issue exists — all three `R0==R1==R2` would fail `LiveEngineerModel`.
- No model chosen because preliminary output *looked* better on `BENCH-002`, no benchmark tweaking to suit a candidate, no post-selection criterion change, no reporting only the winner.

## 8. Model Identity Requirements

Future candidate record must contain (unknown → `UNKNOWN`/`NOT_EXPOSED`/`NOT_SUPPORTED`, not invented):

`candidate ID`, `provider`, `model name`, `exact version/snapshot`, `runtime`, `endpoint or local runtime`, `system prompt` (`EGER-PROMPT-001`), `experiment prompt` (`eger.prompt.v1`), `temperature`, `top_p`, `max_tokens`, `seed`, `timeout`, `context length`, `tool configuration` (tools: `[]`), `external network status`, `model-call budget (5)`.

## 9. Information Governance

For **both** Route A and B, the model **must NOT** receive:

- `evaluator_only/*.expected.json`, hidden `SDC-007` expectation
- other benchmark tasks (only the current `task_id`'s `design_context` + `objective`)
- research results, `C0`/`C1` conclusions, research ledger/contract, Git history, `Ṛta` implementation, oracle internals, future `C2–C5` conditions, other held-out tasks

**Provider/runtime ambiguity:** Route A provider may add hidden `system` instructions — must be documented (provider `system` = `EGER system prompt` only, no hidden preamble). Route B has no provider hidden context.

## 10. Hidden-Capability Audit

| Capability | Route A (API) | Route B (Local) |
|---|---|---|
| web access | CONTROLLED (disable) | CONTROLLED (no network) |
| shell | CONTROLLED (no tool) | CONTROLLED |
| filesystem | CONTROLLED | CONTROLED |
| retrieval | CONTROLLED (no retrieval tool) | CONTROLLED |
| external tools / function calling | CONTROLLED (tools: `[]`) | CONTROLLED |
| hidden memory | AUDITABLE (per-call stateless) | CONTROLLED |
| subagents | CONTROLLED (single `generate` call) | CONTROLLED |
| provider-side context | UNKNOWN (provider may inject) → must be documented as `UNKNOWN` if not auditable | CONTROLLED |
| system-level instructions | AUDITABLE (must be `EGER-PROMPT-001` only) | CONTROLLED |

`UNKNOWN` is never treated as `CONTROLLED`.

## 11. Reproducibility

- **Deterministic candidate:** Can identical inputs produce identical outputs? Route A: **not guaranteed** even at `temperature 0` (provider note); Route B: **closer** (local `temperature 0 + seed`).
- **Stochastic candidate:** Can randomness be controlled/seeded/recorded/repeated? Route A: seed often `NOT_SUPPORTED`; Route B: seed `SUPPORTED` on many runtimes.
- **Treatment-conditioned effect vs noise:** Requires repeated trials per condition (`R0`/`R1`/`R2` each repeated N≥3) — feasible on both routes.
- Do not claim `temperature 0` guarantees determinism.
- **OPEN DESIGN QUESTION:** Statistical threshold for “responsive” (e.g., `R1 != R0` rate > chance) — defined in `P029` (e.g., ≥2/3 responsive revisions), not invented here.

## 12. Cost/Practicality

| Route | Setup effort | Execution cost | Latency | Hardware | Operational complexity |
|---|---|---|---|---|---|
| **A — External API** | Low (add API key + `LiveEngineerModel` HTTP adapter) | Per-token (UNKNOWN until model chosen — do not invent) | 1–3s per call | None local | Low |
| **B — Local** | **High** (download 10–40GB weights, install `ollama`/`vLLM`, verify GPU) | Local compute only | 2–10s per call (GPU) / higher (CPU) | **Unverified** in this workspace (no GPU probe performed) | Medium-High |

Cost is practical, not a reason to select a model for performance.

## 13. MODEL-002 Comparability

**Constant:** `BENCH-002` (6 tasks), task structure, oracle `3b5c2f2`, evidence renderer (`evidence_scope` mapping), information boundary (`engineer_visible` only), metrics (`artifact/reasoning/epistemic`, `EVR`/`AVR`), objectives.
**Changes:** `model identity` (`MODEL-002` = `opencode/muse-spark-1.2` → `MODEL-003` = new candidate), `model behavior` (responsive vs not), `stochastic characteristics`, `inference environment` (potentially API vs local).
**Explicit:** `MODEL-003` will **not** be directly identical to `MODEL-002` — `MODEL-002` remains frozen as `BENCH-001`/`C0`/`C1` baseline control; `MODEL-003` is a new condition only for `C2+` responsiveness testing.

## 14. Change-Control Requirements

After a candidate passes `P029` readiness:

1. `EGER-CHANGE-002` — proposed `MODEL-003` freeze
2. `MODEL-003` specification (`research/experiments/EGER-MODEL-003.md`, 19 sections)
3. `EXP-001 v0.3` — protocol bump (new model condition, not benchmark change)
4. Implementation record (`EGER-P0XX-MODEL-003-FREEZE.md`)
5. Responsiveness-test record (`EGER-P030-R1-*.md`)
6. Readiness verification (25-check style)
7. **Human authorization** before formal `C2`
8. Formal `C2` authorization (separate gate)

None created at `P031`.

## 15. Recommended Access Strategy

**Primary: Route A — External API (controlled, provider-pinned).**

Rationale (not performance):
- **Scientific control:** Provider snapshot pin + `EngineerModel` interface gives sufficient reproducibility for evaluation; version/config can be frozen.
- **Boundary enforcement:** `tools: []`, single `generate(prompt)` call, no retrieval — auditable.
- **Practical feasibility:** `openai`/`anthropic` packages already installed, no local GPU verified, no existing runtime (Route C empty) — Route A requires only credentials, not weight download/hardware provisioning.
- **Cost:** Lower setup effort than local.

**Strongest alternative:** Route B — Local Open-Weight (most reproducible, no provider drift, no network) — recommended if `P031` human decision prefers maximal control and hardware can be provisioned.

**Not recommended:** Route C (none available), Route D (uncharacterized).

No specific model selected at `P031`.

## 16. GO/NO-GO Access Gate

### GO TO CANDIDATE EVALUATION

Only if:
- Model access is legitimate (non-performance criteria)
- Model identity can be recorded (or `NOT_EXPOSED` where provider does not expose)
- Interface `EngineerModel.generate()` can be controlled
- Information boundary (`evaluator_only` exclusion) can be enforced
- Hidden capabilities are `CONTROLLED`/`AUDITABLE` (no `UNCONTROLLED`)
- Output can be captured verbatim (`raw_output`, `prompt_hash`, `output_hash`)
- Reproducibility is adequate (configuration + repeated trials can distinguish responsiveness from noise)

**Route A:** `GO` — meets all, with documented `UNKNOWN` for provider hidden context (acceptable with audit).

**Route B:** `GO` (conditional on hardware provisioning) — meets all, stronger on hidden-capability control.

### NO-GO

If: evaluator leakage possible, identity cannot be established, uncontrolled tools, hidden context `UNCONTROLLED`, output not capturable, access unstable, or configuration not recordable.

**Neither route is NO-GO at P031** (both can be made `GO` with proper implementation).

### INCONCLUSIVE

If: access exists but critical reproducibility info unavailable (e.g., provider does not expose seed and candidate is highly stochastic). Then mark `INCONCLUSIVE` and resolve before `MODEL-003` freeze.

## 17. Next-Step Boundary

After `P031`, the next step is **NOT** `C2`.

```
P031 (this plan)
  ↓ Human decisions (1–7 below)
  ↓ MODEL CANDIDATE ACQUISITION (obtain runtime, no test)
  ↓ RESPONSIVENESS READINESS TEST (P029 rerun, R0/R1/R2)
  ↓ CANDIDATE CLASSIFICATION (P030 criteria: responsive vs not)
  ↓ If pass → MODEL-003 SELECTION → EGER-CHANGE-002 → MODEL-003 FREEZE → EXP-001 v0.3 → Human auth → FORMAL C2
  ↓ If fail → NO MODEL-003 → remain on MODEL-002 → document, do not proceed to C2 with incapable model
```

## 18. Human Decisions Required

| # | Decision | Default | Approver |
|---|---|---|---|
| 1 | Approve this access-route evaluation framework? | — | Human |
| 2 | Approve recommended **Route A** (primary) with Route B as alternative? | — | Human |
| 3 | Authorize acquisition/configuration of a candidate model runtime? | **NO** until approved | Human |
| 4 | Authorize responsiveness readiness testing (`R0/R1/R2`) on that candidate? | **NO** until 3 approved | Human |
| 5 | Require local/open-weight preference over API? | — | Human |
| 6 | Permit controlled external API access if necessary? | — | Human |
| 7 | Require additional privacy/security review before external API use? | — | Human |

None automatically approved.

## 19. Exact Next Authorized Step

**After `P031`, no step is automatically authorized.**

- If human approves Route A (or B) and authorizes acquisition (Decision 3): next is **`MODEL CANDIDATE ACQUISITION`** (obtain/configure runtime, no model execution).
- If human then authorizes testing (Decision 4): next is **`RESPONSIVENESS READINESS TEST`** (`R0`/`R1`/`R2` per `P029`, non-formal).
- Only after a candidate passes and human approves `EGER-CHANGE-002` may `C2` be authorized.

Until those human decisions, **`C2` remains NOT AUTHORIZED** and `MODEL-003` remains `NOT SELECTED`.

---

**Do not:** obtain credentials, install packages, download weights, start servers, invoke external APIs, test models, select `MODEL-003`, modify `MODEL-002`/`BENCH-002`/`Ṛta`/`C0`/`C1`/`EXP-001`, create `EGER-CHANGE-002`, commit, or push — per `P031` strict stop.

