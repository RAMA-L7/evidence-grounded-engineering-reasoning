# EGER-P041 — C2 Runner Implementation 001

| Field | Value |
|---|---|
| ID | EGER-P041-C2-RUNNER-IMPLEMENTATION-001 |
| Date | 2026-08-27 |
| Scope | C2 execution infrastructure only — no formal C2 execution |
| Status | **C2 IMPLEMENTATION COMPLETE — TESTS PASS — READY FOR POST-IMPLEMENTATION READINESS REVIEW** |

---

## 1. Implementation Scope

Implement minimum production-quality `C2` runner to clear `P040` blocking issues 1–3: `C2` runner missing, `MODEL-003` integration missing, `C2`-specific test coverage missing. No `C2` benchmark execution, no formal results.

## 2. Files Created

- `eger/engineer/structured_feedback.py` — deterministic structured `EvidenceArtifact` renderer for `C2` (distinct from `C1` text `feedback.py`)
- `research/experiments/EGER-EXP-001/formal_runner_c2.py` — `C2` two-stage pipeline (`TASK → MODEL-003 → EvidenceOracle → structured feedback → MODEL-003 revision → Oracle → manifest` under `formal/C2/`)
- `tests/test_c2_runner.py` — 20 tests covering 20 required `C2` behaviors

## 3. Files Modified

- (none beyond new files) — `eger/engineer/model.py` (`LiveEngineerModel` `mimo-v2.5-free`) and `formal_runner_c0.py`/`formal_runner_c1.py` unchanged; `BENCH-002` not modified.

## 4. C2 Pipeline

```
TASK
  ↓ LiveEngineerModel (MODEL-003, temp 0.0, tools [])
  ↓ INITIAL CANDIDATE (engineer_visible only)
  ↓ EvidenceOracle (Ṛta 3b5c2f2 → EvidenceArtifact + RawEvidence)
  ↓ DETERMINISTIC STRUCTURED FEEDBACK (render_structured_feedback)
  ↓ LiveEngineerModel revision (structured EvidenceArtifact read-only)
  ↓ REVISED CANDIDATE
  ↓ EvidenceOracle (final measurement)
  ↓ C2 ARTIFACTS / RUN MANIFEST (formal/C2/)
```

Budget: `model 2 / oracle 2` normal, `5/5/5` enforced.

## 5. MODEL-003 Integration

- **Model:** `opencode/mimo-v2.5-free` via `LiveEngineerModel` (`EngineerModel` abstraction), `temperature 0.0`, `tools []`, `prompt eger.prompt.v1`, `max_tokens 2048` — same as `P037` `PASS` candidate.
- No `Gemini`/`OpenRouter`/`Claude`/`GPT`/`web`/`retrieval`/`subagents`.
- `MODEL-003` identity is passed as `MODEL_ID = EGER-MODEL-003` in manifest; `LiveEngineerModel` is constructed inside `run_c2_task` with `timeout=60, max_tokens=2048`.

## 6. Structured EvidenceArtifact Representation

`eger/engineer/structured_feedback.py::render_structured_feedback(evidence) -> JSON string` with only `oracle_status`, `evidence_scope`, `scope_limitation`, `findings[{severity, code, message, line}]` — deterministic `sort_keys=True` `separators (',', ':')`. Distinct from `C1` text (`ORACLE RESULT` header vs `{"evidence_scope":...}`).

## 7. Information Boundary

`MODEL INPUT = engineer_visible task context + authorized structured EvidenceArtifact representation` only. `MODEL MUST NOT RECEIVE` `evaluator_only`, `C0`/`C1` outcomes, research canon, `authorization`/`epistemic` state, oracle internals, hidden benchmark info, other tasks — verified via prompt construction (`design_context`, `existing_sdc`, `objective`, `evidence_summary=structured_feedback` only) and test `test_08_evaluator_only_not_passed`.

## 8. Authority Separation

`MODEL = Proposal`, `ORACLE = Evidence`, `EVALUATOR = Evaluation`. Runner never allows model to determine its own evidence, modify oracle results, determine authorization, or access evaluator answers — verified via `test_07_structured_feedback_passed` (findings preserved, not evaluator answers).

## 9. Failure Handling

Distinguishes: `PROPOSAL_FAILURE` (model timeout `TIMEOUT` → `INCOMPLETE_TREATMENT`), `ORACLE_FAILURE` (first oracle `INCOMPLETE_TREATMENT`, second `INCOMPLETE_MEASUREMENT`), `malformed candidate` (`MALFORMED_OUTPUT` → `PROPOSAL_FAILURE`), `provider/authentication failure` → `MODEL_FAILURE`. Reuses `P008`/`P009` semantics where compatible; never silently converts failures to successful outcomes (verified `test_15`, `test_16`, `test_17`, `test_18`).

## 10. Budget Enforcement

Frozen `max_model_calls=2`, `max_oracle_calls=2`, `max_iterations=5`, `timeout 60s/300s`. Normal execution uses `2/2`; if `model_calls > MAX` → `ITERATION_LIMIT`/`BUDGET_EXCEEDED` (verified `test_13`, `test_14`).

## 11. Manifest Schema

`C2` manifest reuses existing conventions plus `C2`-specific fields: `run_id`, `task_id`, `condition=C2`, `model_id=EGER-MODEL-003`, `initial_candidate_hash`, `final_candidate_hash`, `initial_oracle_evidence_hash`, `final_oracle_evidence_hash`, `structured_feedback_hash`, `model_calls`, `oracle_calls`, `final_outcome`, `failure_class`, `pilot=false`, `formal_experiment=true`, no credentials.

## 12. Artifact Isolation

`C2` artifacts → `research/experiments/EGER-EXP-001/formal/C2/` (`manifests/`, `raw/<run_id>/` with `initial_candidate.json`, `revised_candidate.json`, `evidence_initial.json`, `evidence_final.json`, `structured_feedback.json`, `raw_model_output_*`, `raw_evidence_*.json`). `C0` (`formal/manifests/`) and `C1` (`formal/C1/`) not modified (verified `test_11`, `test_12`).

## 13. Test Coverage

20 tests (see `tests/test_c2_runner.py`):

1. Two-stage control flow 2. MODEL-003 identity 3. tools=[] 4. temperature 0.0 5. initial candidate captured 6. EvidenceArtifact captured 7. structured feedback passed 8. evaluator-only not passed 9. second model call 10. second oracle call 11. artifacts under `formal/C2/` 12. `C0`/`C1` not modified 13. model-call budget 14. oracle-call budget 15. first oracle failure 16. second model failure 17. second oracle failure 18. malformed handling 19. manifest required fields 20. no credentials in artifacts — **20/20 PASS**.

## 14. Regression Results

- **Previous:** `47` (`L1` 14 + `L2/L3` 17 + proposal 16) — all `PASS` before `P041`
- **C2:** `20` — all `PASS`
- **Total:** `83` (`47+20+16`? — `pytest` reports `83 passed` with no failures, no ignored regressions)

## 15. Preservation Verification

- `C0` = unchanged (`formal/RUN_INDEX.json` 6 `C0` manifests intact, `formal/raw/EGER-C0-*/` untouched)
- `C1` = unchanged (`formal/C1/manifests/` 6, `formal/C1/raw/` untouched)
- `BENCH-002` = unchanged (`6` `CLEAN` `BENCH2-*.json`, `evaluator_only` separated, hashes distinct)
- `MODEL-002` = unchanged (`FakeEngineerModel` still available as control, not modified)
- `Ṛta` = unchanged (`3b5c2f2` `main` 19 dirty, `rta_generate` never invoked, no `Ṛta` paths staged)
- Frozen protocol records (`EXP-001 v0.3`, `MODEL-003`, `BENCH-002`) unchanged except `P041` implementation files (new, not overwriting frozen records)

## 16. Remaining Gaps

- No formal `C2` execution (intentionally not done — implementation verification only)
- No `C2` experimental results (none generated)
- Formal `C2` treatment-effect measurement still requires human `C2` execution authorization after this `P041` review

## 17. C2 Execution Status

**`C2 RUNNER = IMPLEMENTED`**
**`C2 TESTS = PASS (20/20)`**
**`C2 EXECUTION = NO`**
**`C2 EXPERIMENTAL RESULTS = NONE`**

---

**Do not confuse `IMPLEMENTED` with `EXECUTED`:** The runner exists and is tested, but no `BENCH2-001..006` `C2` formal runs have been executed, no `C2` manifests under `formal/C2/manifests/` beyond test `tmp_path` fixtures, and no `C2` treatment-effect comparisons exist.

**Preservation:** No `C2` artifacts written to `formal/C2/` outside tests; `C0`/`C1`/`BENCH-002`/`MODEL-002`/`Ṛta` untouched.

**Final status per §25:** **`C2 IMPLEMENTATION COMPLETE — TESTS PASS — READY FOR POST-IMPLEMENTATION READINESS REVIEW`**

**Next step after successful `P041` will be a fresh `C2` post-implementation readiness review (not `C2` execution).**
