# EGER-CHANGE-002 — Introduce MODEL-003 for Feedback-Responsive Conditions

| Field | Value |
|-------|-------|
| ID | EGER-CHANGE-002 |
| Date | 2026-08-27 |
| Type | Model condition addition (experimental, not historical rewrite) |
| Status | **APPROVED — HUMAN AUTHORIZED (EGER-P039)** |
| Trigger | P037 PASS (opencode/mimo-v2.5-free responsive: R0 minimal → R1 adds delays, R2 preserved) + P030 FAIL (LiveEngineerModel muse-spark not responsive) |
| Human authorization | **GRANTED — EGER-P039: Human explicitly authorizes EGER-CHANGE-002 and EXP-001 v0.3 incorporating MODEL-003 (opencode/mimo-v2.5-free) — 2026-08-27** |

---

## 1. Change

Add a **new experimental model condition** for subsequent treatment-effect testing where feedback responsiveness is required:

```
MODEL-003 = opencode/mimo-v2.5-free
  provider: opencode
  model: mimo-v2.5-free
  temperature: 0.0
  tools: []
  prompt: eger.prompt.v1
  max_tokens: 2048
  timeout: 60s
  version: NOT_EXPOSED (provider does not expose dated snapshot; documented)
```

This condition will be used **only** for `C1`/`C2` (and later `C2+`) where `P037` responsiveness is required. `MODEL-002` (`muse-spark-1.2`) remains frozen as the `BENCH-001`/`C0` baseline control.

## 2. Reason

`MODEL-002` (`muse-spark-1.2-contributor-free`) could not condition on feedback (`P030`: `R0==R1==R2`). Without a responsive model, `C1`/`C2` treatment effects are **not identifiable** — the intended causal pathway `deterministic oracle feedback → model revision → revised candidate → measurement` is blocked.

`P037` (`mimo-v2.5-free`) demonstrated: `R0` minimal `create_clock` only → `R1` adds `set_input_delay` + `set_output_delay` exactly addressing `SDC-005`/`SDC-006` while preserving `create_clock`, and `R2` preserves minimal candidate (no arbitrary rewriting). Responsiveness criteria `R-1`/`R-2`/`R-3`/`R-4` all **PASS**.

## 3. Scientific Justification

Without a responsive model, `C1`/`C2` cannot test the hypothesis — the treatment (feedback) has no mechanism to act. `mimo-v2.5-free` **activates** the intended mechanism, making the treatment effect testable. This is not a claim that `MODEL-003` is superior; it is that `MODEL-003` is **eligible** because it passes the pre-registered responsiveness test.

## 4. Scope

- Applies **only** to subsequent conditions requiring feedback responsiveness (initially `C2` structured evidence, later `C1` text-feedback re-evaluation if needed).
- Does **not** rewrite history: `C0` remains on `MODEL-002`, `P030` remains `FAIL`, `P035` remains `INCONCLUSIVE` for `gpt-4o` via `OMNIROUTE` (401), `P037` Gemini `INCONCLUSIVE` (503).
- Does **not** modify `C0` artifacts (`formal/RUN_INDEX.json` 6 `C0` manifests), `C1` artifacts, `BENCH-002`, `Ṛta`, or `research ledger` history.

## 5. EXP-001 Impact

Requires `EXP-001 v0.3` to formally record the new model condition (see `EGER-EXP-001-PROTOCOL-v0.3.md`). `v0.2` remains historical provenance (preserved, not overwritten).

## 6. Human Authorization

`EGER-CHANGE-002 = APPROVED — HUMAN AUTHORIZED (EGER-P039)` — Authorization recorded 2026-08-27 per explicit human decision:

> EGER-CHANGE-002 and EXP-001 v0.3 incorporating MODEL-003 (opencode/mimo-v2.5-free) are approved.

`C2` remains `NOT EXECUTED` / `NOT YET AUTHORIZED` — this approval authorizes the model/protocol change only, not C2 execution.

## 7. Authorization Scope

- **Approved:** `MODEL-003 = opencode/mimo-v2.5-free` (`temperature 0.0`, `tools []`, `prompt eger.prompt.v1`) for subsequent feedback-responsive conditions (`C2` initially, later `C1` re-evaluation if needed).
- **Preserved:** `MODEL-002` remains frozen as `C0` baseline; `C0`/`C1` artifacts, `BENCH-002`, `Ṛta`, and ledger history remain untouched.
- **Not authorized:** `C2` execution — requires separate explicit authorization after this change.

## 8. Verification

- `MODEL-003` identity: `opencode/mimo-v2.5-free` — matches `P037` responsiveness evidence.
- `EXP-001 v0.3` correctly records `MODEL-003` (verified `EGER-EXP-001-PROTOCOL-v0.3.md` ID `v0.3` + changelog).
- `C0`/`C1`/`BENCH-002`/`MODEL-002`/`Ṛta` unchanged (verified `git status` — no `rta-constraint-intelligence` paths staged, no formal results modified).
