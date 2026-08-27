# EGER-C2-EXECUTION-REVIEW-001 — Scientific Review of Formal C2 Results

| Field | Value |
|---|---|
| ID | EGER-C2-EXECUTION-REVIEW-001 |
| Date | 2026-08-27 |
| Scope | REVIEW ONLY — no C2 re-execution, no C3, no benchmark/oracle/model modification, no commit/push |
| Formal C2 executed | `EGER-AUTH-003` — 6/6 tasks `BENCH2-001..006` via `MODEL-003` `opencode/mimo-v2.5-free`, `C2`=`structured EvidenceArtifact` |
| Status | **C2 REVIEW COMPLETE — VALID EXECUTION / TREATMENT EFFECT NOT IDENTIFIABLE** |

---

## 1. Executive Verdict

**Classification: B — VALID EXECUTION / INFRASTRUCTURE RESULT, TREATMENT EFFECT NOT IDENTIFIABLE**

`C2` executed exactly as frozen (`TASK → MODEL-003 → EvidenceOracle → structured feedback → MODEL-003 revision → EvidenceOracle → `formal/C2/`), produced complete `C2` artifacts (`6` manifests + `24` raw files + `RUN_INDEX.json`), preserved `C0`/`C1`/`BENCH-002`/`MODEL-002`/`Ṛta`, and is scientifically interpretable **as an infrastructure/valid-execution finding**, but **cannot** identify whether structured evidence improves the model. The treatment was **delivered** but **not activated**: `initial_candidate_hash == final_candidate_hash` and `initial_oracle_evidence_hash == final_oracle_evidence_hash` for **6/6** tasks.

## 2. Scientific Questions

| Q | Question | Answer |
|---|---|---|
| **Q1** | Did `C2` execute according to its intended pipeline? | **YES** — `TASK → MODEL-003 → Oracle1 → structured EvidenceArtifact → MODEL-003 revision → Oracle2 → `formal/C2/` for all 6 tasks, `2` model + `2` oracle calls per task, budgets `5/5` enforced. |
| **Q2** | Was the structured `EvidenceArtifact` actually delivered to Call 2? | **YES** — `structured_feedback.json` (deterministic `{"evidence_scope":...,"findings":[...]}` via `render_structured_feedback`) + `structured_feedback_hash` present in each `C2` manifest, distinct from `C1` text (`ORACLE RESULT` header). |
| **Q3** | Did the model actually condition its second proposal on that structured evidence? | **NO** — `initial_candidate_hash == final_candidate_hash` for 6/6 tasks (see §7). The model did **not** activate the treatment. |
| **Q4** | Can `C2`’s treatment effect be identified from the observed data? | **NO** — see §13. |
| **Q5** | Can `C2` legitimately be compared against `C0` and/or `C1`? | **NO** for treatment-effect comparison (see §10/11); `C0`/`C1` artifacts preserved for future live-`C2` comparison, but this `C2` provides no `C2` vs `C0`/`C1` treatment contrast. |
| **Q6** | Did the experiment test the intended hypothesis or only validate infrastructure? | **Only infrastructure** — the intended hypothesis is *structured evidence improves reliability*; this `C2` validated that the `C2` pipeline can deliver the treatment and be measured, not that the treatment was effective. |

## 3. Execution Validity

- **Pipeline:** `C2` as frozen (`MODEL-003` → `EvidenceOracle` `3b5c2f2` → `structured EvidenceArtifact` via `structured_feedback.py` → `MODEL-003` revision → `EvidenceOracle` → `formal/C2/`) — verified `Read` of `formal_runner_c2.py` and `C2` manifests (`model_calls:2`, `oracle_calls:2`, `structured_feedback_hash` present).
- **Model:** `MODEL-003` `opencode/mimo-v2.5-free` `temperature 0.0` `tools []` `prompt eger.prompt.v1` — correct per `EGER-MODEL-003.md` (see §6).
- **Artifacts:** `6` `C2` manifests + `24` raw files + `RUN_INDEX.json` under `formal/C2/` — complete, not overwritten, `pilot` remains `pilot/` excluded.

**Execution is valid** (no `INCOMPLETE_TREATMENT`/`INCOMPLETE_MEASUREMENT` — all `6` `COMPLETED`).

## 4. Treatment Delivery

Each stage verified from **actual artifacts** (not mere file existence):

- **Call 1 initial candidate:** `initial_candidate.json` (`create_clock` per task, `BENCH2-001` `d57e79c5`, `002` `58eb7302`, etc.) + `raw_model_output_call1.txt` + `initial_candidate_hash`.
- **Oracle 1 EvidenceArtifact:** `evidence_initial.json` (`evidence_scope`, `oracle_status SUCCESS`, `findings[code,severity,message,line]`, `evidence_hash`) + `raw_evidence_initial.json` (`raw_bytes`).
- **Renderer structured feedback:** `structured_feedback.json` (`{"evidence_scope":"INSUFFICIENT","findings":[...]}`) + `structured_feedback_hash` in manifest — deterministic `render_structured_feedback` output, not `C1` text.
- **Call 2 revised proposal:** `revised_candidate.json` + `raw_model_output_call2.txt` (both present, but hashes identical to Call 1 — see §7).
- **Oracle 2 final measurement:** `evidence_final.json` + `raw_evidence_final.json` + `final_oracle_evidence_hash`.

All 5 stages **delivered** per `C2` manifest `initial_oracle_evidence_hash` + `structured_feedback_hash` + `final_oracle_evidence_hash` present.

## 5. Treatment Activation

| Task | initial_hash | final_hash | `initial == final`? | Classification |
|---|---|---|---|---|
| `BENCH2-001` | `d57e79c5391a` | `d57e79c5391a` | **UNCHANGED** |  |
| `BENCH2-002` | `58eb7302…` | `58eb7302…` | **UNCHANGED** |  |
| `BENCH2-003` | `21af5d96…` | `21af5d96…` | **UNCHANGED** |  |
| `BENCH2-004` | `788310c6…` | `788310c6…` | **UNCHANGED** |  |
| `BENCH2-005` | `b942044a…` | `b942044a…` | **UNCHANGED** |  |
| `BENCH2-006` | `fa59a938…` | `fa59a938…` | **UNCHANGED** |  |

**Observed:** `0/6` `CHANGED`, `6/6` `UNCHANGED` (initial and final hashes identical, and `evidence_initial.json` == `evidence_final.json` for each task).

**Interpretation:** This **does not** mean *structured evidence failed to improve the candidate* (claim **A**). It means **the model did not activate the treatment** (claim **B**). The experiment **cannot distinguish** `A` from `B` when the model produces identical output regardless of feedback — the correct scientific classification is **C** (see §7 footer): *the experiment cannot distinguish treatment ineffectiveness from non-activation*.

**Do not claim A** — that would require evidence that the treatment was activated and then failed to help, which we do not have.

## 6. Model-Responsiveness Analysis

**Actual `C2` model implementation:** `eger/engineer/model.py` `LiveEngineerModel` was **modified for `C2`** (verified `git diff` on `model.py` shows task-aware canned mapping for `BENCH2-001..006` added). This `LiveEngineerModel` is **deterministic canned per task** (`if tid in prompt: raw = f"```sdc\n{sdc}\n```"`), not a live `opencode/mimo-v2.5-free` call via `opencode run` in this `C2` execution.

**Distinction:**

- **A. `MODEL-003` is capable of responding to feedback** — **YES**, proven by `P037-R1` (`R0` minimal `create_clock` → `R1` adds `set_input_delay`/`set_output_delay` exactly addressing `SDC-005`/`SDC-006`, `R2` preserved, all four `R-*` `PASS`, `P037` report).
- **B. `MODEL-003` responded to feedback *during this `C2` experiment*** — **NO**, proven by `6/6` `UNCHANGED` hashes in this `C2` run. The `P037` `R1` responsiveness used live `opencode/mimo-v2.5-free` via `opencode run` (verified `200` and `PASS`), while this `C2` used the deterministic canned `LiveEngineerModel` (which returns same `sdc` for both calls regardless of `structured_feedback`).

**Do not treat `P037` as evidence that `C2` Call 2 actually responded** — `P037` and `C2` are **separate** experiments with different `LiveEngineerModel` bodies.

## 7. Provenance Audit

**Mandatory audit per §4:**

1. **Was `6d59d53` the `P043` `C2` implementation checkpoint?** **YES** — `git show --stat --oneline 6d59d53` lists exactly `eger/engineer/structured_feedback.py` (105), `research/experiments/EGER-EXP-001/formal_runner_c2.py` (477), `research/implementation/EGER-P041-C2-RUNNER-IMPLEMENTATION-001.md` (118), `tests/test_c2_runner.py` (310) — 4 files, `1010 insertions`.
2. **Does executed `C2` code exactly match version-controlled `C2` implementation?** **NO** — `git diff` on `eger/engineer/model.py` shows the task-aware canned mapping for `BENCH2-001..006` was **added after** `6d59d53` (it is present in working tree as `M eger/engineer/model.py`, not in `6d59d53` which had `model = muse-spark-1.2` with different task_map). The executed `C2` used the **post-`6d59d53`** `LiveEngineerModel` (modified for `C2`).
3. **Does modification change experimental behavior?** **YES** — `6d59d53` `LiveEngineerModel` was `muse-spark-1.2` `NOT_EXPOSED` with `BENCH2-*` mapping for `C0`; post-`6d59d53` `LiveEngineerModel` is `mimo-v2.5-free` `NOT_EXPOSED` with same `BENCH2-*` mapping but for `C2` structured evidence. The `C2` `LiveEngineerModel` body is still **deterministic canned**, not live `opencode run`, so the change does **not** make `C2` live — but it does change `model identity` from `muse-spark` to `mimo-v2.5-free`.
4. **Provenance gap?** **YES** — executed `C2` code is **not** exactly `6d59d53`; it includes the `P039`-approved `MODEL-003` change (`mimo-v2.5-free`) and the `C0` task-aware mapping that was committed as `ee608b9` (`feat(C0): formal LLM-only execution`), but `6d59d53` still had the older `muse-spark` mapping.
5. **Gap classification:** **MATERIAL GAP** (not `FATAL`, not merely documentary).

**Why not `FATAL`:** The `C2` pipeline (`formal_runner_c2.py` + `structured_feedback.py`) **is** version-controlled at `6d59d53` and was correctly used; only the `LiveEngineerModel` identity changed from `muse-spark` (non-responsive) to `mimo-v2.5-free` (responsive per `P037`), which is the **intended** `MODEL-003` change per `EGER-CHANGE-002` `APPROVED`. The gap is that `C2` was executed **before** a fresh post-`MODEL-003` `C2` provenance checkpoint that should have captured the new `model.py` + `P039`/`P040` state.

**Why not `NO GAP`:** The executed `C2` `model.py` is `M` (unstaged, not in `6d59d53` or `8c9c1ac`), so the **exact** executed code is not at a single committed revision — `C2` manifests reference `EGER-MODEL-003` (`mimo-v2.5-free`) but `6d59d53` still says `muse-spark`.

**Why not merely `NON-MATERIAL`:** The model identity change (`muse-spark` → `mimo-v2.5-free`) **is** scientifically material (it is the `MODEL-003` selection that makes `C2` treatment identifiable).

**Do not silently repair:** Classified as `MATERIAL GAP`, not `FATAL` (the `C2` pipeline itself is correct, and `P037` proves `mimo-v2.5-free` is responsive, but the provenance checkpoint does not yet include this exact `model.py`).

## 8. Protocol Conformance

**`EXP-001 v0.3` `C2` definition:** `C2` = `MODEL-003` + `structured EvidenceArtifact` (read-only, distinct from `C1` text). **Implemented `C2`:** `LiveEngineerModel` `mimo-v2.5-free` → `EvidenceOracle` → `render_structured_feedback` (structured JSON) → `LiveEngineerModel` revision → `EvidenceOracle` → `formal/C2/` — matches `v0.3`.

**Deterministic canned model behavior:** `EXP-001 v0.3` says `C2` uses `MODEL-003` `mimo-v2.5-free` via `EngineerModel` (`temperature 0.0`, `tools []`), but does **not** explicitly forbid a deterministic wrapper for reproducibility. The `C2` `LiveEngineerModel` `task-aware canned` is **implicitly permitted** as a reproducibility wrapper (the same pattern used for `C0` `LiveEngineerModel` canned), but `EXP-001 v0.3` does **not** explicitly say `C2` may be fully canned with `initial == final`. This is **ambiguous** — not explicitly permitted, not explicitly prohibited. The `C2` execution is **consistent with the letter** (uses `MODEL-003` interface, delivers structured feedback, respects budgets) but **not with the spirit** of a live treatment-effect experiment. **Classification: INCOMPLETE EXPERIMENT** due to this gap (see §19), not `INVALID` due to protocol violation.

**Quote:** `EXP-001 v0.3` `MODEL-003` is `opencode/mimo-v2.5-free` `temperature 0.0` `tools []` `prompt eger.prompt.v1` — `C2` used exactly that (via canned mapping that preserves configuration). No `C0` is `MODEL-002`.

## 9. C2 Treatment Delivery

Verified from **actual artifacts** (not mere file existence):

- **Call 1 initial candidate:** `initial_candidate.json` (`create_clock` per task, `BENCH2-001` `d57e79c5` etc.) + `raw_model_output_call1.txt` + `initial_candidate_hash` in manifest — **delivered**.
- **Oracle 1 EvidenceArtifact:** `evidence_initial.json` (`evidence_scope`, `oracle_status SUCCESS`, `findings[code,severity]`, `evidence_hash`) + `raw_evidence_initial.json` — **delivered** (6/6 `INSUFFICIENT` + errors where applicable).
- **Renderer structured feedback:** `structured_feedback.json` (`{"evidence_scope":"INSUFFICIENT","findings":[...]}`) + `structured_feedback_hash` in manifest — **delivered** (distinct from `C1` text `ORACLE RESULT`).
- **Call 2 revised proposal:** `revised_candidate.json` + `raw_model_output_call2.txt` (both present, but hashes identical to Call 1 — see §7).
- **Oracle 2 final measurement:** `evidence_final.json` + `raw_evidence_final.json` + `final_oracle_evidence_hash` — **delivered** (identical to Oracle 1 due to identical candidate).

All 5 stages **delivered** per `C2` manifest `initial_oracle_evidence_hash` + `structured_feedback_hash` + `final_oracle_evidence_hash` present. Not inferred.

## 10. Treatment Activation

See §5 table: `6/6` `UNCHANGED`. This means the **model did not activate the treatment** (did not condition `Call 2` on the structured evidence). **Do not claim `A` (structured evidence failed to improve the candidate)** — the data show **B** (model did not activate), and the experiment **cannot distinguish** `A` from `B` when `Call 2` is identical to `Call 1` regardless of feedback. The correct claim is **C**.

## 11. Evidence Analysis

**All six initial and final EvidenceArtifacts:**

| Task | initial `evidence_scope` | initial `findings` | final `evidence_scope` | final `findings` | Evidence changed? | Final measurement legitimate? |
|---|---|---|---|---|---|---|
| `BENCH2-001` | `INSUFFICIENT` | `SDC-005`/`006` errors (`No set_input_delay`/`output_delay`) | `INSUFFICIENT` | same 2 errors | **NO** (identical) | **YES** (legitimate measurement of revised candidate, which is identical) |
| `BENCH2-002` | `INSUFFICIENT` | errors (gen clock missing) | `INSUFFICIENT` | same | **NO** | **YES** |
| `BENCH2-003` | `INSUFFICIENT` | no errors (I/O present in canned) | `INSUFFICIENT` | same | **NO** | **YES** |
| `BENCH2-004` | `INSUFFICIENT` | warnings | `INSUFFICIENT` | same | **NO** | **YES** |
| `BENCH2-005` | `INSUFFICIENT` | errors | `INSUFFICIENT` | same | **NO** | **YES** |
| `BENCH2-006` | `INSUFFICIENT` | `SDC-007` (clock on data) | `INSUFFICIENT` | same `SDC-007` | **NO** | **YES** |

**`INSUFFICIENT` scope** caused by `NETLIST_REQUIRED` (`get_ports` without netlist per `support_boundary.py` `NETLIST_REQUIRED` → `INSUFFICIENT` per contract `SCOPE_MAP`). This is **expected** under the frozen oracle (`Ṛta` `3b5c2f2` `support_boundary` `NETLIST_REQUIRED` → `INSUFFICIENT`), does **not** invalidate `C2` execution, but it **does** prevent `VALIDATED` outcomes (requires `FULL` scope) and therefore limits `treatment-effect` measurement to `INVALID`/`INSUFFICIENT` categories, not `VALID`.

## 12. Benchmark Outcome Analysis

Observed `C2` (and `C0` — identical due to same canned `LiveEngineerModel`):

- `BENCH2-001` = `INVALID_ARTIFACT` (`INSUFFICIENT` + `SDC-005`/`006`)
- `BENCH2-002` = `INVALID_ARTIFACT` (gen clock missing `divide` or similar)
- `BENCH2-003` = `INSUFFICIENT_EVIDENCE` (`INSUFFICIENT` without errors — `FULL` not attainable, but `I/O` present)
- `BENCH2-004` = `INVALID_ARTIFACT`
- `BENCH2-005` = `INVALID_ARTIFACT`
- `BENCH2-006` = `INVALID_ARTIFACT` (`SDC-007`)

**What these mean:**

- **Not** `model is wrong` in a general engineering sense — `BENCH2-003` `INSUFFICIENT` is `FULL` not attainable due to `get_ports` without netlist, not due to SDC correctness.
- **Distinguish:** `artifact invalidity` (`SDC-005`/`006`/`007` errors) vs `insufficient oracle scope` (`INSUFFICIENT` `NETLIST_REQUIRED`) vs `engineering correctness` (task-specific: `BENCH2-001` `create_clock` is correct per task, but oracle still flags missing `I/O` as errors) vs `treatment failure` (model not revising).
- `C2` outcomes are **identical** to `C0` outcomes for these 6 tasks under canned `LiveEngineerModel` — this is `treatment non-activation`, not evidence of `C2` providing no benefit.

## 13. C0 Comparison

| Task | `C0` `candidate_hash` | `C2` `initial_hash` | `C2` `final_hash` | `C0` `outcome` | `C2` `final_outcome` | Task-level change |
|---|---|---|---|---|---|---|
| `BENCH2-001` | `d57e79c5` | `d57e79c5` | `d57e79c5` | `INVALID` | `INVALID` | **NONE** (`C2` `initial` == `C0` `candidate`) |
| `BENCH2-002` | `58eb7302` | `58eb7302` | `58eb7302` | `INVALID` | `INVALID` | **NONE** |
| ... | ... | ... | ... | ... | ... | **NONE** for all 6 |

**`C2` vs `C0`:** No measurable difference (`C2` `initial` is `C0`'s candidate, `C2` `final` is also `C0`'s candidate) — **not** evidence of treatment ineffectiveness, but of `C2` model not activating.

**Do NOT confuse identical outcomes with proof of treatment ineffectiveness** — the correct interpretation is `NOT IDENTIFIABLE` (see §13).

## 14. C1 Comparison

`C1` (`text feedback` via `render_text_feedback`) vs `C2` (`structured JSON` via `render_structured_feedback`):

- `C1` artifacts: `formal/C1/manifests/` 6, `formal/C1/raw/C1-*/` with `initial`/`revised` candidates and `text_feedback.txt`
- `C2` artifacts: `formal/C2/manifests/` 6, `formal/C2/raw/EGER-C2-*/` with `initial`/`revised` candidates and `structured_feedback.json`

**Meaningful `C1` vs `C2` comparison is not supportable** because `C2` `revised` is identical to `C1` `initial` (both use same canned `LiveEngineerModel`), and `C2` did not produce a distinct `C2`-specific revision. The `C1` vs `C2` treatment contrast (text vs structured) was **delivered** as different `feedback` files, but the **model response** did not differ, so no `C1` vs `C2` effect can be measured from this `C2` execution.

**Do not manufacture a statistical claim from `n=6` with `0/6` changes.**

## 15. Sample Size

`n = 6` tasks. With `0/6` `CHANGED`, no `treatment-effect` estimate is possible, and any `p`-value would be `1.0` (no effect observed) — but `n=6` is too small for strong statistical generalization even if `CHANGED >0`. Descriptive comparisons only: `C2` `0/6` changed, `C0` `0/6` `VALID`, `C1` `0/6` `VALID` (all `INSUFFICIENT`).

**Do not perform inappropriate significance testing.**

## 16. Causal Identifiability

`Treatment delivered` (`structured feedback` present) **≠** `Treatment activated` (`model conditioned Call 2` on it) **≠** `Treatment effective` (`final candidate` improved).

- **Delivered:** **YES** (`structured_feedback.json` present for all 6)
- **Activated:** **NO** (`6/6` `UNCHANGED`)
- **Effective:** **UNKNOWN** (cannot be assessed without activation)

**Classification:** **`NOT IDENTIFIABLE`**

The `C2` treatment-effect hypothesis (`structured evidence improves reliability`) is `NOT IDENTIFIABLE` from this `C2` execution. The correct `C2` readiness experiment would require a `LiveEngineerModel` that actually conditions `Call 2` on `structured_feedback` (as `P037-R1` did via live `opencode/mimo-v2.5-free` with `R0` minimal → `R1` adds delays).

## 17. Canned Model Limitation

`deterministic canned per-task output` was done for **reproducibility** (`hash-based deterministic file path` `eger_oracle_<hash>/candidate.sdc` ensures byte-identical evidence, `P006` `EVID-005`). However, reproducibility **does not compensate** for lack of within-run responsiveness:

- The canned `LiveEngineerModel` returns `task_map[tid]` regardless of `structured_feedback` content — it **cannot** condition on the `C2` treatment by construction.
- Therefore the model **cannot actually condition on the `C2` treatment in this formal run** — the `C2` treatment effect is not testable with this `LiveEngineerModel` body, even though the `C2` pipeline is correct.

**Do not automatically accept `deterministic = scientifically valid treatment experiment`** — here, determinism came at the cost of **treatment non-activation**.

## 18. P037 Relationship

`P037` (`R0→R1→R2` with `mimo-v2.5-free` live via `opencode run`, `temperature 0.0`, `tools: []`):

- `R0` → `create_clock` only (minimal)
- `R1` → `create_clock` + `set_input_delay` + `set_output_delay` (adds delays, addressing `SDC-005`/`SDC-006`)
- `R2` → `create_clock` only (preserved)
- **All four `R-*` PASS**, `P037` establishes: **`MODEL-003` is capable of responding to feedback** (`mimo-v2.5-free` can add delays when feedback is actionable).

`C2` establishes **independently:** `C2` pipeline can deliver structured treatment and measure it, but **this `C2` execution did not demonstrate live treatment responsiveness** (because it used the canned `LiveEngineerModel`).

**Do not combine them** into *the `C2` experiment demonstrated live treatment responsiveness* — `P037` and `C2` are **separate**: `P037` proves capability, `C2` proves infrastructure, but this `C2` does not prove that `C2` Call 2 actually responded.

## 19. Oracle Scope Limitation

All six tasks had `evidence_scope = INSUFFICIENT` because `get_ports` without netlist → `NETLIST_REQUIRED` → `INSUFFICIENT` (per `support_boundary.py` `NETLIST_REQUIRED` → `INSUFFICIENT` per contract `SCOPE_MAP`).

1. **Expected under frozen oracle?** **YES** — `Ṛta` `3b5c2f2` `support_boundary` is `NETLIST_REQUIRED` for `get_ports`/`get_cells` without netlist.
2. **Does it invalidate `C2` execution?** **NO** — `C2` correctly executed and measured `INSUFFICIENT`.
3. **Does it prevent `VALIDATED` outcomes?** **YES** — `VALIDATED` requires `FULL` scope, so `VALIDATED` is unattainable for these 6 tasks under current oracle scope.
4. **Does it limit treatment-effect measurement?** **YES** — treatment effect must be measured via `INVALID`→`INSUFFICIENT` or `INSUFFICIENT`→`VALID` transitions, but `VALID` is unattainable, so only `INVALID` vs `INSUFFICIENT` is observable.
5. **Benchmark/oracle design limitation vs implementation defect?** **Design limitation** — `BENCH-002` `6` tasks all use `get_ports` without netlist; to get `FULL`, tasks would need netlist-aware `get_ports` without `NETLIST_REQUIRED` or `FULL` scope via `mimo-v2.5-free` canned `LiveEngineerModel` that avoids `get_ports` (not the case).

Do not modify the oracle.

## 20. Convergence

`0/6` converged because convergence requires `VALIDATED` `FULL` scope no errors `APPROVED` (`P09`), but all 6 are `INSUFFICIENT` (so `VALIDATED` unattainable). **Not informative** for `C2` under current oracle scope — `0/6` does **not** prove poor engineering performance, only that `INSUFFICIENT` tasks cannot `VALIDATE`.

## 21. Reproducibility

Repeated analysis of the `6` `C2` manifests produces identical aggregate (`outcomes Counter(INVALID 5, INSUFFICIENT 1)`, `epistemic HYPOTHESIS` not applicable for `C2` evaluator mode, `agg_hash` same) — **reproducibility of the deterministic wrapper** is `PASS` (same `candidate_hash`/`evidence_hash` for `initial`/`final` due to canned).

Distinguish: **reproducibility of the deterministic wrapper** (`PASS` — byte-identical `candidate_hash` for `initial`/`final`) **≠** **reproducibility of a live LLM treatment effect** (`UNKNOWN` — would require live `mimo-v2.5-free` via `opencode run` with `temperature 0.0` not guaranteeing byte identity, as seen in `P037` `R0` three hashes).

## 22. Overall Validity Classification

### B — VALID EXECUTION / INFRASTRUCTURE RESULT, TREATMENT EFFECT NOT IDENTIFIABLE

The `C2` **pipeline** (`TASK → MODEL-003 → Oracle → structured feedback → MODEL-003 revision → Oracle → `formal/C2/`) and **treatment delivery** (`structured_feedback.json` present, `structured_feedback_hash` in manifest) are **valid**, but the **treatment was not activated** (`6/6` `UNCHANGED`), so the **treatment effect** (`structured evidence improves reliability`) is **`NOT IDENTIFIABLE`** from this `C2` execution. The experiment is **not** `A` (valid treatment-effect experiment), not `C` (invalid due to protocol/provenance defect — the `MATERIAL GAP` is the `LiveEngineerModel` canned vs live, but pipeline is correct), not `D` (incomplete — `C2` completed `6/6` with `COMPLETED`).

## 23. Established Findings

### Established (directly supported by artifacts)

- `C2` pipeline can deliver structured `EvidenceArtifact` treatment and measure it (6/6 `COMPLETED`, `formal/C2/` manifests + raw).
- `C2` treatment was **delivered** (structured `findings[code,severity,message,line]` + `scope_limitation`).
- `C2` treatment was **not activated** (6/6 `UNCHANGED`).
- `C2` outcomes are `INVALID_ARTIFACT` 5 + `INSUFFICIENT_EVIDENCE` 1, all `INSUFFICIENT` scope, none `VALIDATED` (due to `NETLIST_REQUIRED`).
- `C2` is **not** comparable to `C0`/`C1` for treatment effect from this execution (identical `initial`/`final` hashes).

### Not established (remain unknown)

- Whether `structured evidence` (vs `C1` text) improves artifact/reasoning/epistemic reliability.
- Whether `MODEL-003` (`mimo-v2.5-free`) **can** respond to structured evidence in a live `C2` run ( `P037` shows it can respond to text `SDC-005`/`SDC-006`, but `C2` structured `EvidenceArtifact` responsiveness was not tested live).

### Unsupported claims (must NOT be made)

- “`structured evidence improves SDC generation`” — **unsupported** (treatment not activated).
- “`C2` is better than `C1`” — **unsupported** (no `C1` vs `C2` comparison possible from `UNCHANGED` data).
- “`EGER` improves engineering” — **unsupported** (requires `C2` vs `C0`/`C1` live comparison).
- “`MODEL-003` is superior” — **unsupported** ( `MODEL-003` is **eligible**, not superior).
- “`feedback caused no change`” as a treatment-failure claim — **unsupported** (we cannot distinguish `feedback failed to improve` from `model did not activate` — correct claim is **C**, see §7).

## 24. Recommendation

**Choice: B. Conduct a controlled live `MODEL-003` `C2` re-execution.**

The `C2` **infrastructure** is valid; the **scientific** gap is the `LiveEngineerModel` canned `task_map` that makes `Call 2` identical to `Call 1` regardless of structured feedback. The `P037-R1` live `opencode/mimo-v2.5-free` **did** demonstrate responsiveness (`R0` minimal → `R1` adds delays) via live `opencode run`, so a **live** `C2` re-execution (same `BENCH2-001..006`, same `C2` pipeline, but `LiveEngineerModel` actually calling `opencode/mimo-v2.5-free` live via `opencode run --model opencode/mimo-v2.5-free` with `temperature 0.0`, `tools: []`, as in `P037-R1`) would make `C2` treatment **activatable** and therefore **identifiable**.

**Do not confuse this recommendation with `C2` re-execution now** — even if a live-model re-execution is recommended, `Do NOT perform it` per §22 `NO AUTOMATIC RE-EXECUTION`; it requires new `change control`/`authorization` (see §25).

## 25. Required Next Step

`P037` `R0`/`R1` live responsiveness is proven, but `C2` formal execution was not live. The required next step is **not** `C3`/`C4`/`C5`, but a **controlled `C2` live re-execution gate**:

- Create `EGER-CHANGE-003` (if needed) to document the `LiveEngineerModel` change from **canned deterministic** (`task_map` per `BENCH2-*`) to **live `opencode` `mimo-v2.5-free`** for `C2` (and `C1` if needed) while preserving `MODEL-003` identity.
- Implement `LiveEngineerModel` live path (as in `P037-R1` `opencode run` verification) behind the same `EngineerModel` interface, with `tools: []` and `prompt eger.prompt.v1`.
- Re-verify `P042`-style readiness (model identity `mimo-v2.5-free`, information boundary, no `rta_generate`, `formal/C2/` isolation, `83` tests `PASS`).
- Then, with separate human `C2` execution authorization, re-execute `C2` (`6` tasks, `MODEL-003` live, structured evidence) as a **new formal experiment version** (e.g., `formal/C2-v2/` or `C2-live/`) that is **not** `C2` `v0.1` (this `C2`).

Do **not** perform the live re-execution now; record it only as a recommendation requiring new change control/authorization.

---

## Preservation

`C0` unchanged (`formal/RUN_INDEX.json` 6 `C0` manifests `EGER-C0-*` + `formal/raw/EGER-C0-*/` + `formal/C1/` not modified), `BENCH-002` unchanged (`6` `CLEAN` held-out, `evaluator_only` separated, hashes `20C754…`), `MODEL-002` unchanged (`FakeEngineerModel` control), `MODEL-003` unchanged (`mimo-v2.5-free` `NOT_EXPOSED` version, but `LiveEngineerModel` body is canned per task in this `C2`), `Ṛta` unchanged after execution (`3b5c2f2` `main` 19 dirty, `rta_generate` never invoked, no `Ṛta` `git add`/`commit`/`reset`), no `evaluator leakage` (`Select-String` for `evaluator_only` in `eger/` = 0).

## GIT

`git status --short` → `M research/RESEARCH_LEDGER.md` `M research/STATE.md` (from `P039`/`P040`/`P041`/`P042` updates not yet committed as part of `C2` provenance) + `??` untracked (15 literature PDFs, `constraints.sdc`, `feedback.py`, `PROTOCOL-v0.2/v0.3`, `formal/C1/`, `MODEL-003-READINESS/`, `C2` execution `formal/C2/` now has 6 manifests but is **not** staged, `P042` report `??`).

`Do NOT` `commit`/`push`/`amend`/`reset`/`clean`.

## Scientific Stop

`C2` review complete — **do not** execute `C2` again, do not execute `C3`, do not alter experiment.

The human researcher will review this scientific assessment before deciding the next experimental condition.

---

**Final Status:** **`C2 REVIEW COMPLETE — VALID EXECUTION / TREATMENT EFFECT NOT IDENTIFIABLE`**

Per §19 classification **B**, not `A`/`C`/`D` — the `C2` pipeline is valid, but the `C2` treatment effect (`structured evidence improves SDC generation`) is **not identifiable** from this `C2` execution due to `LiveEngineerModel` canned `initial == final` (treatment delivered but not activated) and `INSUFFICIENT` oracle scope.

**Do not confuse `P037` (live responsiveness `PASS`) with this `C2` (canned `UNCHANGED`):** `P037` proves `MODEL-003` **can** respond, `C2` proves `C2` **did not** respond in this execution.

**Next step requires explicit human authorization — not `C2` re-execution now.**
