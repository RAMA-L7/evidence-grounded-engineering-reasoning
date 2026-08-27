# EGER-CHANGE-003 — Live MODEL-003 C2 Re-Execution Implementation

| Field | Value |
|-------|-------|
| ID | EGER-CHANGE-003 |
| Date | 2026-08-27 |
| Type | Model execution mode change (implementation, not historical rewrite) |
| Status | **APPROVED — HUMAN AUTHORIZED (P046) — IMPLEMENTED** |
| Trigger | P045 design + P046 human authorization: previous formal C2 used deterministic canned model, treatment effect not identifiable |
| Human authorization | **GRANTED — P046: Human explicitly authorizes EGER-CHANGE-003 implementation** |

---

## 1. Change

Replace the **deterministic canned per-task `LiveEngineerModel` mapping** with an **actual live `opencode run --model opencode/mimo-v2.5-free` invocation** via subprocess.

### Before

```python
# LiveEngineerModel.generate() — canned task-map
for tid, sdc in task_map.items():
    if tid in prompt:
        raw = f"```sdc\n{sdc}\n```"
        break
```

### After

```python
# LiveEngineerModel.generate() — live opencode
if self.live:
    raw = self._invoke_live(prompt)  # subprocess.run(["opencode", "run", ...])
else:
    raw = self._invoke_canned(prompt)  # backward-compatible canned path
```

## 2. Reason

Previous C2 (EGER-AUTH-003) demonstrated treatment **delivery** but not treatment **activation** — `initial_candidate_hash == final_candidate_hash` for 6/6 tasks because the canned model returned identical output regardless of feedback. P037 proved live `mimo-v2.5-free` can respond. Live re-execution is required for treatment-effect identifiability.

## 3. Scientific Justification

Without live execution, C2 cannot distinguish "feedback delivered but model didn't respond" from "model responded but didn't improve." The live path enables the three-way distinction: [1] no response, [2] responds no improve, [3] responds improves.

## 4. Model Identity (Unchanged)

```
provider: opencode
model: opencode/mimo-v2.5-free
version: NOT_EXPOSED
temperature: 0.0
tools: []
prompt: eger.prompt.v1
max_tokens: 2048
timeout: 60s
```

## 5. Files Changed

| File | Change | Lines |
|------|--------|-------|
| `eger/engineer/model.py` | Added `live` parameter, `_invoke_live()`, `_invoke_canned()`, refactored `generate()` | ~80 lines changed |
| `research/experiments/EGER-EXP-001/formal_runner_c2.py` | Added `live` parameter, `C2-live` artifact directory | ~30 lines changed |
| `tests/test_c2_runner.py` | Added 12 live adapter tests (T21–T32) | ~150 lines added |

## 6. Information Boundary (Unchanged)

Call 2 receives ONLY: task context + objective + output format + initial candidate + structured feedback.

Call 2 does NOT receive: evaluator answers, C0/C1/C2 outcomes, research ledger, authorization state, epistemic state, oracle internals.

## 7. Artifact Separation

| Directory | Contents |
|-----------|----------|
| `formal/C2/` | Previous canned C2 execution (PRESERVED) |
| `formal/C2-live/` | Future live C2 execution (NOT YET POPULATED) |

## 8. C2 Execution Status

**C2 LIVE EXECUTION = NOT AUTHORIZED**

This change-control record authorizes implementation only. Live C2 execution requires separate human authorization after readiness verification (P047).

## 9. Test Results

```
95 tests PASS (83 previous + 12 new live adapter tests)
```

## 10. Provenance

- P045 (design) → P046 (authorization) → implementation (this record)
- Previous C2 checkpoint: `6d59d53` (canned implementation)
- This implementation is a new state after `6d59d53`
- Do not pretend the live implementation existed at `6d59d53`
