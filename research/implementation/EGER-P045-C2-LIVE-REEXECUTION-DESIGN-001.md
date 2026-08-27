# EGER-P045 — C2 Live-Model Re-Execution Change-Control Design

| Field | Value |
|---|---|
| ID | EGER-P045-C2-LIVE-REEXECUTION-DESIGN-001 |
| Date | 2026-08-27 |
| Scope | DESIGN + CHANGE CONTROL ONLY — no execution, no implementation |
| Status | **DESIGN COMPLETE — IMPLEMENTATION AUTHORIZATION REQUIRED** |

---

## 1. Executive Summary

The previous formal C2 execution (EGER-AUTH-003) produced **VALID EXECUTION / TREATMENT EFFECT NOT IDENTIFIABLE** because the `LiveEngineerModel` used a deterministic canned per-task mapping — it returned the same SDC for both Call 1 and Call 2 regardless of structured feedback. P037 separately proved that `opencode/mimo-v2.5-free` **can** respond to feedback when called live via `opencode run`.

This document designs a controlled live C2 re-execution that replaces the canned model path with actual live `opencode/mimo-v2.5-free` invocations. The purpose is to make the C2 treatment effect **identifiable** — distinguishing "feedback delivered but model didn't respond" from "model responded but didn't improve."

**This is design only. No code changes, no execution, no commit/push.**

---

## 2. Previous C2 Finding

```
C2 formal execution (EGER-AUTH-003):
  6/6 tasks completed
  initial_candidate_hash == final_candidate_hash: 6/6
  treatment delivered: YES (structured_feedback.json present)
  treatment activated: NO (6/6 UNCHANGED)
  treatment effect: NOT IDENTIFIABLE
  classification: B — VALID EXECUTION / INFRASTRUCTURE RESULT
```

The previous C2 execution must remain preserved as historical evidence. It will NOT be overwritten.

---

## 3. P037 Relationship

P037 established MODEL-003 responsiveness capability:

```
R0 (no feedback):     create_clock only         → preserved
R1 (actionable):      create_clock + delays     → addresses SDC-005/SDC-006
R2 (non-actionable):  create_clock only         → no arbitrary rewriting
All R-*: PASS
```

P037 proves MODEL-003 **can** respond. It does NOT prove the formal C2 experiment produced a treatment effect. These are separate claims.

---

## 4. Scientific Objective

> Determine whether structured deterministic EvidenceArtifact feedback causes a feedback-responsive MODEL-003 to revise its engineering proposal in a controlled C2 re-execution.

The experiment must distinguish:

```
feedback delivered
    ↓
model conditions on feedback
    ↓
candidate changes
    ↓
oracle outcome changes
```

Do NOT assume that a candidate change automatically means improvement.

---

## 5. Classification: Revision, New Condition, or New Experiment?

### Analysis

| Dimension | Previous C2 | Proposed Live C2 |
|-----------|------------|-----------------|
| Model identity | MODEL-003 (mimo-v2.5-free) | MODEL-003 (mimo-v2.5-free) |
| Model configuration | temperature 0.0, tools [] | temperature 0.0, tools [] |
| Treatment | Structured EvidenceArtifact | Structured EvidenceArtifact |
| Pipeline | C2 two-stage | C2 two-stage |
| Benchmark | BENCH-002 v0.1 | BENCH-002 v0.1 |
| Oracle | EvidenceOracle (3b5c2f2) | EvidenceOracle (3b5c2f2) |
| Model implementation | Canned task-map | Live opencode run |
| Artifact directory | formal/C2/ | formal/C2-live/ |

### Classification

**This is a RE-EXECUTION of the same C2 condition with a different model implementation mode.**

- The model identity (MODEL-003) is unchanged.
- The treatment (C2 = structured EvidenceArtifact) is unchanged.
- The experimental condition (C2) is unchanged.
- Only the model's actual execution mechanism changes (canned → live).

It is NOT:
- A new experimental condition (condition is still C2)
- A new experiment version (EXP-001 v0.3 already authorizes MODEL-003 for C2)
- A model change (MODEL-003 identity is the same)

It IS:
- An implementation-mode change (how MODEL-003 is invoked)
- Requiring change control (EGER-CHANGE-003) because model.py changes
- Producing a new artifact set (formal/C2-live/) for comparison

### Provenance Implications

- Previous C2 (formal/C2/) preserved as "C2 v0.1" historical evidence
- Live C2 (formal/C2-live/) is "C2 v0.2" or "C2-live" — new artifacts
- Both can be compared descriptively
- C0/C1 artifacts remain untouched

---

## 6. Change Control: EGER-CHANGE-003

### 6.1 Identifier

`EGER-CHANGE-003` (next after CHANGE-002, per repository ledger convention)

### 6.2 Reason

Previous C2 used deterministic canned `LiveEngineerModel` (task-map lookup), making `initial == final` for all 6 tasks. Treatment delivered but not activated. P037 proved live `mimo-v2.5-free` can respond. Live re-execution is required for treatment-effect identifiability.

### 6.3 Affected Component

`eger/engineer/model.py` — `LiveEngineerModel.generate()` method

### 6.4 Change Description

Replace the deterministic canned task-map lookup with an actual live `opencode run --model opencode/mimo-v2.5-free` invocation. The canned path is retained as a fallback for tests only.

### 6.5 Model Identity (Unchanged)

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

### 6.6 Live Execution Requirement

The model must be invoked through the verified OpenCode interface:

```bash
opencode run --model opencode/mimo-v2.5-free
```

With environment variable `OPENCODE_API_KEY` present (verified in P037-R1).

Do NOT use:
- Canned task mapping (except test fallback)
- MODEL-002 (muse-spark)
- Gemini / OpenRouter / fallback models
- Web / retrieval / subagents / tools

### 6.7 Artifact Preservation

| Artifact | Status |
|----------|--------|
| formal/C2/ (previous) | PRESERVED — not overwritten |
| formal/C2-live/ (new) | CREATED — new artifacts |
| C0 artifacts | UNTOUCHED |
| C1 artifacts | UNTOUCHED |
| BENCH-002 | UNTOUCHED |
| MODEL-002 | UNTOUCHED |
| Ṛta | UNTOUCHED |

### 6.8 Information Boundary (Unchanged)

Call 1: task context + objective + required output format
Call 2: task context + objective + required output format + initial candidate + structured feedback

Call 2 must NOT receive: evaluator answers, C0/C1/C2 outcomes, research ledger, authorization state, epistemic state, oracle internals, hidden benchmark information, web/retrieval/subagents.

### 6.9 Budget (Unchanged)

Per run: ≤2 model calls, ≤2 oracle calls, 0 routing calls
Global: ≤5 model calls, ≤5 oracle calls

### 6.10 Failure Semantics (Unchanged from P024)

- Oracle 1 failure → INCOMPLETE_TREATMENT
- Model 2 failure → INCOMPLETE_TREATMENT
- Oracle 2 failure → INCOMPLETE_MEASUREMENT
- Authentication failure → PROPOSAL_FAILURE
- Provider unavailable → PROPOSAL_FAILURE
- Timeout → PROPOSAL_FAILURE
- Malformed output → PROPOSAL_FAILURE

### 6.11 Human Authorization Status

**NOT YET AUTHORIZED** — this document is the design proposal. Authorization required before implementation.

---

## 7. Live Adapter Design

### 7.1 Current State

`LiveEngineerModel.generate()` at `eger/engineer/model.py`:

```python
def generate(self, prompt: str, **kwargs) -> ModelResponse:
    # Deterministic canned mapping
    for tid, sdc in task_map.items():
        if tid in prompt:
            raw = f"```sdc\n{sdc}\n```"
            break
    # ... return ModelResponse
```

**Problem:** Returns identical output regardless of prompt content (same task ID → same SDC).

### 7.2 Proposed Architecture

```
LiveEngineerModel.generate(prompt)
        ↓
    [1] Check if live opencode is available
        ↓
    [2a] If available: subprocess.run(["opencode", "run", "--model", "opencode/mimo-v2.5-free"], prompt)
        ↓
    [2b] If unavailable: fall back to canned task-map (tests only)
        ↓
    ModelResponse(raw_output=..., provider="opencode", model="opencode/mimo-v2.5-free", ...)
```

### 7.3 Key Implementation Requirements

1. **Live path:** `subprocess.run()` calling `opencode run --model opencode/mimo-v2.5-free` with the full prompt as input
2. **Timeout enforcement:** `timeout=self.timeout` (60s) on the subprocess
3. **Output capture:** Capture stdout, strip any CLI preamble, extract SDC from ```sdc code fence
4. **Error handling:** If `opencode` not installed or `OPENCODE_API_KEY` missing → raise clear error (NOT fallback silently for formal execution)
5. **Test fallback:** Canned path retained only for unit tests using `FakeEngineerModel` — formal execution must use live path
6. **No hidden tools:** `tools=[]` — no web, retrieval, grounding
7. **Prompt identity:** Full prompt passed to `opencode run` — same prompt that `EngineerAdapter.build_prompt()` constructs

### 7.4 What Does NOT Change

| Component | Change? |
|-----------|---------|
| `EngineerAdapter` (adapter.py) | NO — already supports `evidence_summary` |
| `CandidateArtifact` (candidate.py) | NO |
| `structured_feedback.py` | NO |
| `formal_runner_c2.py` | NO — already calls `engine_adapter.propose()` correctly |
| `EvidenceOracle` (oracle adapter) | NO |
| `feedback.py` (C1 renderer) | NO |
| Test suite (83 tests) | NO — `FakeEngineerModel` used in tests, not `LiveEngineerModel` |

### 7.5 Minimal Change Scope

**Only `eger/engineer/model.py` `LiveEngineerModel.generate()` changes.**

The C2 runner (`formal_runner_c2.py`) already:
- Calls `engine_adapter.propose(design_context, objective)` for Call 1
- Calls `engine_adapter.propose(..., existing_sdc=..., evidence_summary=structured_feedback)` for Call 2
- Preserves initial/final candidates separately
- Writes to `formal/C2-live/` (with base_dir parameter)

The only change needed in `formal_runner_c2.py` would be the output directory (`C2` → `C2-live`), which could be a parameter rather than a code change.

---

## 8. Oracle Scope Limitation

### 8.1 Current State

All 6 BENCH-002 tasks produce `evidence_scope = INSUFFICIENT` because:
- `get_ports` without netlist → `NETLIST_REQUIRED` → `INSUFFICIENT` (per `support_boundary.py` and contract `SCOPE_MAP`)

### 8.2 Blocking Classification

**NON-BLOCKING** for the live C2 re-execution.

### 8.3 Rationale

The primary outcome of the live C2 re-execution is:

```
proposal_changed = initial_candidate_hash != final_candidate_hash
```

This is **independent of oracle scope**. The model's response to feedback is observable regardless of whether the oracle achieves FULL scope.

The oracle scope limitation means:
- `VALIDATED` outcomes remain unattainable (requires FULL scope)
- Convergence measurement is limited
- But treatment activation (did the model respond?) and treatment delivery (was feedback provided?) are fully observable

### 8.4 Scientific Consequences

| Measurement | Observable? | Reason |
|-------------|------------|--------|
| Feedback delivered | YES | structured_feedback_hash in manifest |
| Model responded | YES | initial_hash != final_hash |
| Candidate changed | YES | hash comparison |
| Error count changed | YES | findings comparison |
| VALIDATED reached | NO | INSUFFICIENT scope prevents FULL |
| Convergence | LIMITED | Requires VALIDATED |

The live C2 re-execution can answer its primary question (did the model respond to structured feedback?) even under INSUFFICIENT scope.

---

## 9. Primary Outcome

```
proposal_changed = initial_candidate_hash != final_candidate_hash
```

**Descriptive measure only.** `changed` does NOT mean `improved`.

Secondary outcome: oracle outcome comparison (initial vs final evidence scope, findings).

---

## 10. Secondary Outcomes

| Outcome | Measurement |
|---------|-------------|
| Candidate validity | final_outcome (INVALID/INSUFFICIENT/VALID) |
| Oracle outcome change | evidence_scope_1 vs evidence_scope_2 |
| Error count change | len(findings_1) vs len(findings_2) |
| Finding resolution | Specific findings present/absent in final |
| Task preservation | Final candidate still addresses task objective |
| Format preservation | Final candidate still in ```sdc format |
| Unauthorized modification | No evaluator data in model prompt |
| Capability leakage | No web/retrieval/subagents in model call |

---

## 11. Causal Identifiability

The live re-execution enables three-way distinction:

```
[1] Model does not respond:     initial_hash == final_hash (same as canned)
[2] Model responds, no improve: initial_hash != final_hash, same/worse oracle outcome
[3] Model responds, improves:   initial_hash != final_hash, better oracle outcome
```

This distinction was impossible with the canned model (only [1] was observable).

**Do not pre-register "improvement" as the expected outcome.** The experiment is designed to identify which of [1]/[2]/[3] occurs.

---

## 12. Reproducibility

### 12.1 Known Limitation

`temperature 0.0` does NOT guarantee byte-identical output from `opencode/mimo-v2.5-free` (observed in P037: three different R0 hashes with same prompt).

### 12.2 Reproducibility Metadata

Per run, capture:
- provider, model, model_version (NOT_EXPOSED)
- temperature, tools, max_tokens, timeout
- prompt_version (eger.prompt.v1)
- task_id, run_id
- prompt_hash, output_hash, candidate_hash
- evidence_hash, structured_feedback_hash
- timestamps (start, end)
- model_calls, oracle_calls
- raw_model_output (Call 1 and Call 2)
- oracle execution metadata

### 12.3 Determinism Classification

- **Deterministic:** feedback rendering, oracle evaluation, artifact serialization, hashing
- **Non-deterministic:** LLM output (even at temperature 0.0)

The non-determinism of the LLM is a known limitation, not a protocol defect. The experiment measures whether the model **responds to feedback**, not whether it produces identical output.

---

## 13. Budget

Per run (same as frozen):
- Model calls: 2 (initial + revision)
- Oracle calls: 2 (initial evaluation + final measurement)
- Routing calls: 0

Absolute limits: ≤5 model calls, ≤5 oracle calls, ≤300s wall clock

---

## 14. Failure Semantics

| Failure | Classification | Behavior |
|---------|---------------|----------|
| OPENCODE_API_KEY missing | PROPOSAL_FAILURE | Abort run, do not fallback to canned |
| opencode not installed | PROPOSAL_FAILURE | Abort run, do not fallback to canned |
| Provider 5xx | PROPOSAL_FAILURE | Record, may retry per §14 (technical retry) |
| Timeout (60s) | PROPOSAL_FAILURE | Record, do not fallback |
| Empty response | PROPOSAL_FAILURE | Record as MALFORMED_OUTPUT |
| Malformed SDC | PROPOSAL_FAILURE | Record as MALFORMED_OUTPUT |
| Model call 1 failure | INCOMPLETE_TREATMENT | Preserve partial artifacts |
| Oracle call 1 failure | INCOMPLETE_TREATMENT | Preserve initial candidate |
| Model call 2 failure | INCOMPLETE_TREATMENT | Preserve initial + evidence_1 |
| Oracle call 2 failure | INCOMPLETE_MEASUREMENT | Preserve revised candidate |

**Critical:** For formal live execution, do NOT silently fall back to canned output. If the live model is unavailable, the run must fail explicitly.

---

## 15. Artifact Separation

### 15.1 Directory Structure

```
formal/C2-live/
├── manifests/
│   ├── EGER-C2L-*.json (one per task)
├── raw/
│   ├── EGER-C2L-<RUN_ID>/
│   │   ├── raw_model_output_call1.txt
│   │   ├── initial_candidate.json
│   │   ├── raw_evidence_initial.json
│   │   ├── evidence_initial.json
│   │   ├── structured_feedback.json
│   │   ├── raw_model_output_call2.txt
│   │   ├── revised_candidate.json
│   │   ├── raw_evidence_final.json
│   │   └── evidence_final.json
└── RUN_INDEX.json
```

### 15.2 Naming Convention

- Run IDs: `EGER-C2L-<8-hex>` (C2L = C2-Live, distinct from C2 canned `EGER-C2-<8-hex>`)
- Manifests: `EGER-C2L-<RUN_ID>.json`
- Raw dirs: `EGER-C2L-<RUN_ID>/`

### 15.3 Preservation

Previous C2 artifacts at `formal/C2/` remain untouched. Live C2 artifacts go to `formal/C2-live/`. No overwriting, no merging.

---

## 16. Comparability

### 16.1 Comparison Matrix

| Comparison | Valid? | Reason |
|-----------|--------|--------|
| C2-live vs C2-canned | DESCRIPTIVE | Same condition, different implementation mode — shows whether live model activates treatment |
| C2-live vs C0 | DESCRIPTIVE ONLY | Different models (MODEL-003 vs MODEL-002), different conditions — cannot attribute differences to treatment alone |
| C2-live vs C1 | DESCRIPTIVE ONLY | Different models for C1 (MODEL-002 canned) vs C2-live (MODEL-003 live) — confounded by model identity |
| C2-live initial vs C2-live final | VALID | Within-condition treatment responsiveness — same model, same task, feedback is the only variable |
| C2-live vs future live C1 | POTENTIALLY VALID | If C1 is also re-run with live MODEL-003, C1 vs C2 becomes a clean text-vs-structured comparison |

### 16.2 Key Insight

The most scientifically meaningful comparison from the live C2 re-execution is:

**C2-live initial vs C2-live final** (within-condition, feedback responsiveness)

This is the primary treatment-response diagnostic. Cross-condition comparisons (C0/C1 vs C2-live) are confounded by model identity differences and should be treated as descriptive only.

---

## 17. Sample Size

Same 6 held-out tasks (BENCH2-001..006). Reusing the same tasks:
- ✅ Enables direct comparison with C0/C1/C2-canned (same task context)
- ⚠️ Model has now "seen" these tasks in C2-canned execution (but canned output was identical, so minimal learning)
- ⚠️ n=6 is small for statistical inference
- ✅ Sufficient for treatment-response diagnostic (did model change? yes/no per task)

---

## 18. Implementation Requirements (If Authorized)

### 18.1 Code Changes

| File | Change | Scope |
|------|--------|-------|
| `eger/engineer/model.py` | Add live `opencode run` path in `LiveEngineerModel.generate()` | ~30 lines |
| `research/experiments/EGER-EXP-001/formal_runner_c2.py` | Add `base_dir` parameter or `C2-live` output path | ~5 lines |

### 18.2 New Files

| File | Purpose |
|------|---------|
| `research/implementation/EGER-CHANGE-003.md` | Change-control record |
| `research/implementation/EGER-AUTH-004-C2-LIVE.md` | Execution authorization (after implementation + readiness) |

### 18.3 Test Impact

- Existing 83 tests use `FakeEngineerModel` — no impact from `LiveEngineerModel` changes
- New test: verify `LiveEngineerModel` raises clear error when `OPENCODE_API_KEY` missing (formal mode)
- New test: verify `LiveEngineerModel` calls `opencode run` with correct arguments (mock subprocess)
- Full test suite should remain 83/83 PASS after changes

---

## 19. GO/NO-GO

### READY FOR IMPLEMENTATION AUTHORIZATION

All design requirements satisfied:

- ✅ Scientific objective defined
- ✅ Classification determined (re-execution, not new condition)
- ✅ Change control designed (EGER-CHANGE-003)
- ✅ Live adapter architecture specified
- ✅ Information boundary preserved
- ✅ Artifact separation designed (formal/C2-live/)
- ✅ Oracle scope limitation assessed (NON-BLOCKING)
- ✅ Comparability defined
- ✅ Failure semantics specified
- ✅ Budget preserved
- ✅ Reproducibility metadata defined
- ✅ No blocking scientific issues

---

## 20. Required Human Authorization

Before implementation, the human researcher must authorize:

1. **EGER-CHANGE-003** — live MODEL-003 implementation mode change
2. **Implementation scope** — model.py changes + runner adjustment
3. **Live C2 execution** — separate authorization after implementation + readiness verification

---

## 21. Research Chain

```
P045 design (this document)
    ↓
Human authorization of CHANGE-003
    ↓
Implementation (model.py live path)
    ↓
Readiness verification (P046-style)
    ↓
Human authorization of live C2 execution
    ↓
Live C2 execution (formal/C2-live/)
    ↓
Scientific review
    ↓
Comparability analysis (C2-live vs C0/C1/C2-canned)
```

---

## 22. Git Status

```
M eger/engineer/model.py           (unstaged, from previous session)
M research/RESEARCH_LEDGER.md      (unstaged, from previous updates)
M research/STATE.md                (unstaged, from previous updates)
?? (many untracked implementation records)
```

**Do NOT commit, push, stage, amend, reset, or clean.**

---

## 23. Final Status

**P045 COMPLETE — LIVE C2 RE-EXECUTION DESIGN READY — IMPLEMENTATION AUTHORIZATION REQUIRED**

Design is complete. The live-model adapter architecture is specified. EGER-CHANGE-003 is designed. The next step is human review and, if approved, implementation authorization.

---

**Do NOT implement, execute, modify code, modify benchmark, modify oracle, modify model configuration, commit, or push.**

**STOP after this document.**
