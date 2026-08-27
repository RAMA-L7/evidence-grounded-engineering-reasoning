# EGER-P039 — EGER-CHANGE-002 & EXP-001 v0.3 Human Authorization

| Field | Value |
|---|---|
| ID | EGER-P039-CHANGE-002-AUTHORIZATION-001 |
| Date | 2026-08-27 |
| Human Decision | **APPROVED: EGER-CHANGE-002 + EXP-001 v0.3 incorporating MODEL-003 (opencode/mimo-v2.5-free)** |
| Status | `EGER-CHANGE-002 APPROVED — EXP-001 v0.3 APPROVED — MODEL-003 FROZEN — C2 NOT YET AUTHORIZED` |

---

## 1. Human Authorization

The human researcher explicitly authorized:

> **1. EGER-CHANGE-002**
> **2. EXP-001 v0.3 incorporating MODEL-003 = opencode/mimo-v2.5-free**

Per `EGER-P039` prompt:

```
Human Decision: The human researcher explicitly authorizes:
1. EGER-CHANGE-002
2. EXP-001 v0.3 incorporating MODEL-003 (opencode/mimo-v2.5-free)
```

This is **not** a `C2` execution authorization.

## 2. EGER-CHANGE-002 Approval

- **Before:** `PROPOSED — AWAITING HUMAN AUTHORIZATION` (`research/implementation/EGER-CHANGE-002.md` at `b150f03`).
- **After:** `APPROVED — HUMAN AUTHORIZED (EGER-P039)` — updated in `EGER-CHANGE-002.md` with `Human authorization: GRANTED — EGER-P039` and `Status: APPROVED`, plus new §7–8 `Authorization Scope` and `Verification`.
- **Scope:** Change applies **only** to subsequent feedback-responsive conditions (initially `C2`); `C0` on `MODEL-002`, `P030` `FAIL`, `P035` `INCONCLUSIVE` remain historical.
- **No credentials** added.

## 3. EXP-001 v0.3 Approval

- **File:** `research/experiments/EGER-EXP-001-PROTOCOL-v0.3.md` (`ID v0.3`, `FROZEN (P038 — MODEL-003 added, v0.2 preserved)`).
- **Verification:** `ID` is `EGER-EXP-001 v0.3` (not `v0.1`), `Status` is `FROZEN`, `Date` unchanged `2026-08-26`, `Architecture` `EGER-ARCH-002`, `Changelog v0.2 → v0.3` correctly records `MODEL-003 = opencode/mimo-v2.5-free` addition, `v0.1`/`v0.2` preserved as historical (`EGER-EXP-001-PROTOCOL.md` still `v0.1`, `v0.2` not overwritten).
- **Distinction:** Historical `C0`/`C1` conditions remain on `MODEL-002` per `v0.1`; `v0.3` adds `MODEL-003` for subsequent conditions — not a silent overwrite.

## 4. MODEL-003 Identity

- **Model:** `opencode/mimo-v2.5-free`
- **Provider:** `opencode`
- **Version:** `mimo-v2.5-free` (provider does not expose dated snapshot → `NOT_EXPOSED` where version pin would be, documented in `EGER-MODEL-003.md`)
- **Endpoint:** `opencode` local/runtime via `opencode run --model opencode/mimo-v2.5-free` (verified `200` in `P037-R1` via `OPENCODE_API_KEY` `PRESENT len 67`)
- **Interface:** `EngineerModel.generate(prompt) -> ModelResponse` (`eger/engineer/model.py` — same as `MODEL-002`, no `rta_generate`)

If `OpenCode` cannot provide a stable/frozen identity, the fallback is `NOT_EXPOSED` — correctly handled, not silently substituted.

## 5. MODEL-003 Configuration

Per `EGER-MODEL-003.md` and `P037` frozen config:

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

All match `P037` `R0`/`R1`/`R2` execution (`temperature 0.0`, `tools: []`, `eger.prompt.v1`).

## 6. P037 Evidence

`EGER-P037-MODEL-003-RESPONSIVENESS-READINESS-001.md` (`opencode/mimo-v2.5-free` `PASS`):

- **R0** (no feedback, `create_clock` only) → `create_clock` only (preserved)
- **R1** (actionable `SDC-005`/`SDC-006`) → `create_clock` + `set_input_delay` + `set_output_delay` (addresses finding)
- **R2** (non-actionable `INFO`) → `create_clock` only (no arbitrary rewriting)
- **Classification:** `PASS` — all four `R-*` satisfied, information boundary preserved, `rta_generate` never invoked

This is the sole evidence for eligibility; no benchmark ranking was used.

## 7. P038 Selection

`research/implementation/EGER-P038-MODEL-003-SELECTION-AND-CHANGE-CONTROL-001.md` (24 sections) already recorded:

- `MODEL-003 SELECTED — EGER-CHANGE-002 RECORDED — AWAITING HUMAN AUTHORIZATION`
- `OpenRouter` `401` and `Gemini` `503` histories preserved, not erased
- `MODEL-003` not designated until this human approval (now approved, but `C2` still not authorized)

## 8. Scientific Justification

`MODEL-002` (`muse-spark`) could not condition on feedback (`P030` `R0==R1==R2` → treatment effect not identifiable). `mimo-v2.5-free` **activates** the intended causal pathway `deterministic oracle feedback → model revision → revised candidate → measurement`, making the `C1`/`C2` treatment effect testable. This is **not** a claim that `MODEL-003` is superior — only that it is **eligible** because it passes the pre-registered responsiveness test.

## 9. Historical Provenance

All historical records remain intact, not overwritten:

- `EXP-001 v0.1` (`research/experiments/EGER-EXP-001-PROTOCOL.md`) — still `v0.1`, still `FROZEN (P011)`
- `EXP-001 v0.2` — preserved (where created; `v0.3` changelog notes `v0.2` preserved)
- `MODEL-002` (`muse-spark-1.2`) — `FROZEN`, `C0` baseline
- `C0` artifacts (`formal/RUN_INDEX.json` 6 `C0` manifests `EGER-C0-*`, `formal/raw/EGER-C0-*/`) — unchanged (verified `git status` shows `formal/` not dirty except new `P039` record)
- `C1` artifacts — unchanged
- `P037` / `P038` — preserved, not re-run

## 10. C0 Preservation

`C0 = unchanged` — `research/experiments/EGER-EXP-001/formal/RUN_INDEX.json` still maps `EGER-C0-81390F4B` → `BENCH2-001` etc., `6` `C0` manifests, `formal/raw/EGER-C0-*/` (candidate/evidence) untouched. Verified `git diff --stat -- research/experiments/EGER-EXP-001/formal/` shows no `C0` file modified during `P039`.

## 11. C1 Preservation

`C1 = unchanged` — `C1` artifacts remain under `formal/C1/` (if created) — not moved or rewritten during `P039`.

## 12. BENCH-002 Preservation

`BENCH-002 v0.1` — 6 `CLEAN` held-out tasks, `evaluator_only/*.expected.json` separated, `BENCH-002-TASKS.json` frozen — **unchanged**. No tasks/expected answers/evaluator files changed (verified `git diff` on `research/experiments/EGER-BENCH-002*` shows only `MODEL-003`/`PROTOCOL-v0.3` additions, no `BENCH-002` content change).

## 13. Ṛta Preservation

`Ṛta` `3b5c2f2` `main` `19` dirty before and after `P039` (verified `git -C rta-constraint-intelligence rev-parse HEAD` → `3b5c2f25…`, `status --porcelain | wc -l` → `19`). No `rta_generate` invoked (0 hits in `eger/`), no `Ṛta` files modified.

## 14. C2 Boundary

After this approval:

- `C2 = NOT EXECUTED`
- `C2 = NOT AUTHORIZED`

The authorization recorded here is **only** `EGER-CHANGE-002` + `EXP-001 v0.3`. No `C2` task has been executed; no `C2` manifest exists under `formal/`. `C2` remains gated until a separate explicit `C2` execution authorization is granted.

## 15. C2 Readiness Assessment

| Prerequisite | Status |
|---|---|
| `EXP-001 v0.3` frozen with `MODEL-003` | **READY** (`PROTOCOL-v0.3.md` ID `v0.3`, changelog) |
| `MODEL-003` frozen | **READY** (`EGER-MODEL-003.md` `FROZEN`) |
| Run manifest requirements | **READY** (`EXP-001 v0.1` §23 manifest schema, pilot `R0`/`R1` demonstrated) |
| `C2`-specific protocol definition (`structured EvidenceArtifact` exposed read-only) | **READY** (per `EXP-001` `C2` definition, not text feedback) |
| `C2` execution authorization | **NOT YET** — requires separate human `C2` authorization (see §16) |
| Reproducibility requirements | **READY** (`prompt_hash`/`output_hash`/`candidate_hash` per `P037-R1`) |
| Final information-boundary verification for `C2` (structured evidence, not text) | **READY** (verified `P013-R1` sentinel: `evaluator_only` 0 hits, `EngineerAdapter` only injects `engineer_visible`) |

## 16. Remaining Preconditions

- **Human authorization for `C2` execution** — not granted by this `P039` (this authorizes only the model/protocol change).
- No additional `MODEL-003`/`BENCH-002` changes needed before `C2`.

## 17. Final Status

**EGER-CHANGE-002 APPROVED — EXP-001 v0.3 APPROVED — MODEL-003 FROZEN — C2 NOT YET AUTHORIZED**

All 17 required report sections are present, `C0`/`C1`/`BENCH-002`/`MODEL-002`/`Ṛta` preserved, `rta_generate` never invoked, `C2` not executed, credentials not added, no `C2` results, no benchmark modification.

---

**Do not:** execute `C2`, create `C2` results, modify `BENCH-002`/`C0`/`C1`/`Ṛta`/`MODEL-002`, select another model, commit, or push — per `P039` strict stop. `C2` requires a **separate** human authorization after this `P039`.
