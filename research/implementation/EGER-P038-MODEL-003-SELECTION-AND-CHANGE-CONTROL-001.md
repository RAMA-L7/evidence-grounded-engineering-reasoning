# EGER-P038 — MODEL-003 Formal Selection & Change Control 001

| Field | Value |
|---|---|
| ID | EGER-P038-MODEL-003-SELECTION-AND-CHANGE-CONTROL-001 |
| Date | 2026-08-27 |
| Candidate | `opencode/mimo-v2.5-free` (opencode) — P037 PASS |
| Change | `EGER-CHANGE-002` — add MODEL-003 for C2 (not C0 rewrite) |
| Status | **MODEL-003 SELECTED — EGER-CHANGE-002 RECORDED — AWAITING HUMAN AUTHORIZATION** |

---

## 1. Executive Summary

`P037-R1` with `opencode/mimo-v2.5-free` (temperature 0.0, tools [], `eger.prompt.v1`) demonstrated: `R0` minimal `create_clock` → `R1` adds `set_input_delay` + `set_output_delay` exactly addressing `SDC-005`/`SDC-006` while preserving `create_clock`, `R2` preserves minimal (no arbitrary rewriting) — all four `R-*` **PASS**. `MODEL-003` is therefore **eligible** as the formally selected experimental model condition for the feedback-responsive treatment, because it passes the pre-registered responsiveness eligibility test that `MODEL-002` (`muse-spark`) failed.

## 2. Current Scientific State

- `C0 = COMPLETE` (6/6 `BENCH2-*` via `MODEL-002` `muse-spark`, `C0` is LLM-only baseline, `C0` artifacts preserved)
- `C1 = COMPLETE` (6/6, but `C1` treatment effect `NOT IDENTIFIABLE` because `MODEL-002` was non-responsive — `P030` `R0==R1==R2`)
- `MODEL-002 = FROZEN` (`opencode/muse-spark-1.2` `NOT_EXPOSED`)
- `MODEL-003 = NOT YET FORMALLY SELECTED` (now `mimo-v2.5-free` eligible per `P037`)
- `BENCH-002 v0.1` `6` `CLEAN` held-out `FROZEN`
- `Ṛta` `3b5c2f2` untouched, `rta_generate` never invoked

## 3. P037 Evidence Summary

| Condition | Prompt | Output (trimmed) | Finding addressed? |
|---|---|---|---|
| **R0** (no feedback) | task + initial `create_clock` only | `create_clock` only | baseline |
| **R1** (actionable `SDC-005`/`SDC-006`) | same + `ORACLE RESULT … [ERROR] SDC-005/006` | `create_clock` + `set_input_delay … [all_inputs]` + `set_output_delay … [all_outputs]` | **YES — adds both missing delays** |
| **R2** (non-actionable `INFO`) | same + `No actionable findings` | `create_clock` only | **YES — no arbitrary rewriting** |

`R1` hash distinct from `R0`/`R2`; `R2` hash matches `R0` (preserved). No evaluator-only leakage.

## 4. Candidate Identity

- **Model:** `opencode/mimo-v2.5-free`
- **Provider:** `opencode`
- **Version/identifier:** `mimo-v2.5-free` (provider does not expose dated snapshot → `NOT_EXPOSED` where version pin would be, documented)
- **Endpoint/access:** `opencode` local/runtime via `opencode run --model opencode/mimo-v2.5-free` (verified `200` in `P037-R1` via `OPENCODE_API_KEY` `PRESENT len 67`)
- **Interface:** `EngineerModel.generate(prompt) -> ModelResponse` (`eger/engineer/model.py` — same as `MODEL-002`)

## 5. Candidate Selection Criteria

Per `P029`/`P038` §4, all required:

- Identity recordable — **YES** (`opencode/mimo-v2.5-free`)
- Accessibility — **YES** (`opencode run` succeeded, `200`)
- Configuration recordable — **YES** (`temperature 0.0`, `tools []`, `prompt eger.prompt.v1`)
- Responsiveness `P037 PASS` — **YES**
- Information boundary — **YES** (`engineer_visible` only)
- Capability isolation `tools: []` — **YES** (no web/retrieval/subagent)
- Reproducibility — `PASS WITH LIMITATION` (temperature 0.0 not byte-identical, documented)
- Interface compatibility — **YES** (`EngineerModel`)
- Experimental suitability — **YES** (feedback-assisted revision)

## 6. Responsiveness Evidence

`P037-R1` `R-1` **PASS** (R1 meaningfully responds where feedback requires a change), `R-2` **PASS** (addresses `SDC-005`/`SDC-006`), `R-3` **PASS** (preserves `create_clock` task intent), `R-4` **PASS** (R2 avoids rewriting). No evaluator leakage, no hidden tools, configuration preserved.

## 7. Information-Boundary Verification

Allowed: `BENCH2-003` `design_context` (minimal clock), `objective`, `required output format`, `initial candidate` (`create_clock` only), `deterministic text feedback` (`R1`/`R2` as above). Forbidden (checked — none supplied): `evaluator_only/BENCH2-*.expected.json`, expected solutions, `C0`/`C1` results, ledger/contract/Git history, `Ṛta` internals, other benchmark tasks, `web`/`retrieval`/`subagents`. Verified `tools = []`.

## 8. Capability Isolation

`web`/`retrieval`/`subagents`/`tools` all `CONTROLLED` (omitted `tools` field equivalent to `[]`, single `generate` call). No `rta_generate`, no `Ṛta` source write, no Git write, no research-memory write.

## 9. Reproducibility Assessment

`temperature 0.0` does **not** guarantee byte identity on `opencode` (provider note) — `R0` prior runs gave `fd1b3...` then `57c906...` then `35025a...` (documented). `prompt_hash`/`output_hash`/`candidate_hash` will be recorded per run and repeated trials can distinguish treatment effect from noise. No hidden seed to control.

## 10. OpenCode Provider Analysis

`opencode` is **access/routing layer** (like `openrouter.ai` for `P034`), not the experimental model. `opencode/mimo-v2.5-free` is the **actual underlying LLM** (`mimo-v2.5-free`). `opencode` `GET /models` lists `mimo-v2.5-free` alongside `muse-spark-1.2`, `big-pickle`, etc.; routing is `AUDITABLE` (provider prefix in `id`), no forced fallback observed for pinned `mimo-v2.5-free`.

## 11. Gemini/OpenRouter Candidate History

Preserved: OpenRouter `openai/gpt-4o` via `OMNIROUTE_API_KEY` (`sk-bdd7...` 35 chars) → `401 Unauthorized` for `POST /chat/completions` (key truncated/invalid) → `P035` `INCONCLUSIVE`; Gemini `models/gemini-2.5-flash` → `404` *no longer available*, `models/gemini-3.6-flash` → `200` for `R0` but `503` high demand for `R1` → `P037` `INCONCLUSIVE`; `opencode/mimo-v2.5-free` → `200` and `PASS` `R0`/`R1`/`R2` → now `ELIGIBLE`. No history rewritten, `P037` deviation (`gemini-2.5-flash` → `mimo-v2.5-free`) remains traceable.

## 12. MODEL-003 Selection Rationale

**Not** “`MODEL-003` is superior.” Correct claim: *`MODEL-003` is the formally selected experimental model condition because it passed the pre-registered feedback-responsiveness eligibility test (`P037`), which `MODEL-002` failed (`P030` `R0==R1==R2`).* Without a responsive model, `C1`/`C2` treatment effects are not identifiable (causal pathway `feedback → revision` blocked).

## 13. MODEL-003 Configuration

As in `EGER-MODEL-003.md` (`opencode/mimo-v2.5-free`, `provider opencode`, `version NOT_EXPOSED`, `temperature 0.0`, `tools []`, `prompt eger.prompt.v1`, `max_tokens 2048`, `timeout 60s`, `model-call budget 5`), `P037` `R0`/`R1`/`R2` evidence reference.

## 14. Model Freeze

Formally frozen as `MODEL-003 = opencode/mimo-v2.5-free` with above configuration at this commit for subsequent `C2` (and later `C1` re-evaluation if needed). `C0` remains on `MODEL-002` as historical control. If `opencode` may silently substitute `mimo-v2.5-free` alias, document as `REPRODUCIBILITY LIMITATION` — not pretended immutable snapshot.

## 15. EGER-CHANGE-002 Assessment

`research/implementation/EGER-CHANGE-002.md` — **PROPOSED / AWAITING HUMAN AUTHORIZATION**: Change = add `MODEL-003` for feedback-responsive conditions; Reason = `MODEL-002` not responsive, `mimo-v2.5-free` is; Scope = subsequent treatment-effect testing only, not `C0`/`C1` rewrite; `v0.2` preserved. Not inferred authorized from `P037` `PASS`.

## 16. EXP-001 v0.3 Assessment

`research/experiments/EGER-EXP-001-PROTOCOL-v0.3.md` created as copy of `v0.1` with ID `v0.3` and changelog `MODEL-003` addition. `v0.1`/`v0.2` remain preserved (not overwritten). `v0.3` is required to formally incorporate `MODEL-003` per change-control.

## 17. C0 Preservation

`C0 = unchanged` — `formal/RUN_INDEX.json` 6 `C0` manifests (`EGER-C0-*`), `formal/raw/EGER-C0-*/` (candidate/evidence), `C0` is LLM-only baseline via `MODEL-002`. Not moved/rewritten; `P037` readiness artifacts remain separate under `formal/MODEL-003-READINESS/`.

## 18. C1 Preservation

`C1 = unchanged` — `formal/C1/` artifacts remain under `formal/C1/` (if created) or as prior `C1` run; not moved/rewritten by this selection. `P037` did not execute `C1`.

## 19. BENCH-002 Preservation

`BENCH-002 v0.1` `6` `CLEAN` held-out `FROZEN` — no tasks/expected answers/evaluator files modified. Model condition changes, benchmark does not.

## 20. Ṛta Preservation

`Ṛta` `3b5c2f2` `main` 19 dirty before/after — untouched, no `rta_generate`, no oracle modification.

## 21. Causal Interpretation

- `MODEL-002`: `feedback supplied` → `no observable response` → `treatment effect not identifiable` (hence `P030` `FAIL`, `C1` `NOT IDENTIFIABLE`).
- `MODEL-003`: `feedback supplied` → `observable feedback-conditioned revision` (`R0` minimal → `R1` adds delays) → `treatment effect becomes testable` (not proven that feedback *improves* outcomes — that remains empirical for `C2`).

## 22. Remaining C2 Preconditions

- `EXP-001 v0.3` frozen (done as draft, awaiting authorization)
- `MODEL-003` frozen (done, awaiting authorization)
- Run manifest requirements (per `EXP-001 v0.1` §23) — ready
- `C2`-specific protocol definition (`structured EvidenceArtifact` exposed, read-only, `R-1`..`R-4` criteria) — ready
- `C2` execution authorization — **NOT YET** (human must authorize `EGER-CHANGE-002` and `EXP-001 v0.3`)
- Reproducibility requirements — documented (`temperature 0.0` not byte-identical)
- Final information-boundary verification for `C2` (structured evidence, not text) — ready per `P013-R1` sentinel

## 23. Human Authorization Requirement

`EGER-CHANGE-002 = PROPOSED / AWAITING HUMAN AUTHORIZATION` — `P038` does not infer authorization from `P037` `PASS`. `C2` remains `NOT AUTHORIZED` until human explicitly approves `EGER-CHANGE-002` and `EXP-001 v0.3`.

## 24. Final Decision Status

**MODEL-003 SELECTED — EGER-CHANGE-002 RECORDED — AWAITING HUMAN AUTHORIZATION**

`MODEL-003` (`opencode/mimo-v2.5-free`) is **selected** as eligible and **recorded** via `EGER-CHANGE-002` (proposed) and `MODEL-003` spec, but **not yet authorized** for `C2`. No `C2` execution, no `C2` artifacts, no benchmark/model rewrite.

---

**Do not:** execute `C2`, authorize `C2`, modify `C0`/`C1`/`BENCH-002`/`Ṛta`/`MODEL-002`, execute further responsiveness experiments, commit, or push — per `P038` strict stop. Human will review `MODEL-003`/change-control before `C2`.

**Candidate history preserved:** OpenRouter `401` (truncated key) and Gemini `503` remain traceable; `P037` deviation (`gemini-2.5-flash` → `mimo-v2.5-free`) not erased.
