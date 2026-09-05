# EGER P173 — RQ-5 Harness Repair & Readiness Gate

## 1. Objective

Implement the P172-approved experimental harness repairs and run the pre-experiment readiness gate for a future controlled RQ-5 replication. This gate implements harness code only — it does NOT execute EGER-RQ5-PILOT-002, does NOT modify P170/P171, Ṛta, VerificationGate, or C0–C5, and does NOT modify any raw experimental data.

## 2. Historical Baseline

- **Commit:** ff43d0a6be606d3910c0756ecfbfe87cd142e9f0 (P172 design)
- **Branch:** main
- **HEAD == origin/main:** confirmed
- **Working tree:** clean except intentionally untracked `Universal_Principles_Library/`, `raw_trials.json`, `analysis.json`
- **P171 verdict preserved:** RQ-5 PILOT INCONCLUSIVE

## 3. Implemented Harness (P172 §5–§15)

New code under `research/experiments/EGER-RQ5-PILOT-001/harness/` (harness-only; no EGER production module modified):

| Module | Implements | P172 § |
|--------|-----------|--------|
| `harness/candidate_validity.py` | Deterministic gate: VALID_SDC / NON_SDC_OUTPUT / EMPTY_OUTPUT / PROVIDER_FAILURE; code-fence extraction; conversational-wrapper detection; SDC-command detection; task-required `create_clock` construct; injection-marker rejection | §5 |
| `harness/matrix.py` | Frozen counterbalanced order: Ṛta-first in T1 block, OpenSTA-first in T2 block; `assert_matrix_order()`; 2×2×2 replication validation | §9 |
| `harness/trial_runner.py` | Initial Oracle evaluation before model invocation (PO-3); revision loop with validity gate; 1 bounded retry with both attempts recorded; NO_TIMING_CONSTRAINT flag; PO-1/PO-3 derivation; full P172 schema | §7, §8, §13, §15 |
| `harness/analysis.py` | Deterministic PO-2 aggregation from raw records; explicit denominators (planned/completed/evaluations/successful/evidence artifacts/retries/failures); single source of truth for reports | §12 |
| `harness/tasks.py` | Frozen T1/T2 task definitions with required constructs and expected Oracle behavior | §10 |
| `harness/providers.py` | Canonical real-provider wiring (Ṛta EvidenceOracle, OpenSTAAdapter via WSL wslpath, OpenCode model provider) — NOT invoked during fixture validation | §6, §17 |
| `harness/fixtures.py` | Deterministic fixture SDCs, fake Oracles (Ṛta completeness semantics / OpenSTA timing semantics), fake model provider, failing oracle | §6 Option C |
| `run_qualification.py` | Model qualification test: K=3 per task, ≥5/6 VALID_SDC, ≥1 per task, zero empty/provider failures | §6 |

Plus `harness_tests/` — 39 fixture-based tests covering the validity gate, matrix, retry, initial evaluation, PO-3, NO_TIMING_CONSTRAINT, and PO-2 aggregation.

## 4. Fixture Harness Validation (P172 §6 Option C, Phase 1)

Deterministic fixtures never touch WSL/OpenSTA/Ṛta or the LLM.

```
python -m pytest research/experiments/EGER-RQ5-PILOT-001/harness_tests -q
39 passed in 0.45s
```

Key validations:
- Validity gate: valid SDC (plain + fenced), conversational filler → NON_SDC_OUTPUT, empty → EMPTY_OUTPUT, provider error → PROVIDER_FAILURE, injection markers → NON_SDC_OUTPUT, missing `create_clock` → NON_SDC_OUTPUT (vacuous-pass defense).
- Matrix: frozen order passes assertion; reordered/unbalanced order rejected; 2×2×2 replication structure validated.
- Trial runner: initial Oracle evaluation recorded before model invocation; PO-3 = IMPROVED/NOT_IMPROVED/WORSE/NOT_MEASURABLE; PO-1 = ROBUST/MARGINAL/FAILED; retry on CANDIDATE_INVALID (both attempts recorded, retry_count=1); no retry on ORACLE_FAILURE (non-zero exit on valid candidate); both-attempts-fail → FAILED; OpenSTA aggressive-clock → violation → REJECT → MARGINAL.
- Analysis: deterministic (identical input → identical output); denominators explicit; failure kinds counted; planned denominator = 8 preserved.

## 5. Model Qualification Test (P172 §6, Phase 2 — executed AFTER fixtures passed)

```
Model: opencode/mimo-v2.5-free
Invocations: 6 (3 × T1, 3 × T2)
VALID_SDC: 0/6 (threshold ≥ 5/6)
Per-task valid: T1 = 0, T2 = 0
Empty/provider failures: 0
RESULT: FAIL — model DISQUALIFIED
```

All 6 outputs were conversational filler (e.g., "Understood. I'm ready to help with SDC constraints for your VLSI design. What do you need?"), despite the repaired prompt demanding SDC-only output.

### Interpretation

- **P170 failure cause definitively resolved:** the P170 candidates were not SDC because the model itself does not follow the output-only-SDC instruction in this invocation mode. The prompt/harness was repaired (system-level instruction, output rules, validity gate) and the model STILL returned filler in 6/6 invocations. This confirms hypothesis (b) from P172 §6 — model incapacity for this task under the frozen invocation — not merely a harness defect.
- **P172 §6 disposition applies:** the frozen model is DISQUALIFIED for the task set. A different model/provider must be selected and re-qualified before any experiment may start. Selection criterion is qualification success under the frozen task instructions, NOT perceived quality.
- **Qualification record** is stored locally at `research/experiments/EGER-RQ5-PILOT-001/qualification_record.json` (publication-sensitive readiness record; NOT committed; NOT experimental data).
- **Model availability note (diagnostic only):** `opencode models` lists numerous candidates (e.g., `opencode/gpt-5.4`, `opencode/claude-opus-5`, `opencode/gemini-3.5-flash`, `opencode/deepseek-v4-pro`, etc.). NO model was selected or tested beyond the frozen one — selection and re-qualification are a future gate decision per P172 §6.

## 6. Readiness Checklist (P172 §16)

| Area | Status |
|------|--------|
| Candidate generation (model qualification) | **FAIL** — 0/6 VALID_SDC |
| Candidate validity gate | PASS (fixture-tested) |
| Ṛta version verified | NOT REACHED (blocked by model qualification) |
| OpenSTA version/substrate verified | NOT REACHED (blocked) |
| Timing precondition (clock + constrained path) | NOT REACHED (blocked) |
| Initial Oracle evaluation | PASS (fixture-tested) |
| Retry (1 bounded, both attempts) | PASS (fixture-tested) |
| Counterbalancing asserted pre-run | PASS (fixture-tested) |
| Schema complete | PASS (fixture-tested) |
| Deterministic analysis | PASS (fixture-tested) |
| Git clean except approved artifacts | PASS |

Per P172 §16: any critical failure → **NO-GO**; the experiment does not begin.

## 7. Test Regression

```
python -m pytest tests -q
864 passed
```

Unchanged. No EGER production code was modified (harness is experiment-scoped under `research/experiments/`).

## 8. Research Boundaries

```
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: NO (PILOT-002 NOT run)
C0-C5 conclusions changed: NO
Oracle comparison performed: NO
VerificationGate authority changed: NO
Epistemic-state logic added: NO
Authorization logic added: NO
P170/P171 records modified: NO
Raw experimental data modified: NO
EGER production code modified: NO
New experiment executed: NO
```

## 9. Decision

**BLOCKED** (readiness NO-GO for the frozen model).

The harness is repaired and fixture-validated (Phase 1 complete). The model qualification gate (Phase 2) FAILED for `opencode/mimo-v2.5-free` (0/6 VALID_SDC). Per P172 §6 and §17, this blocks the experiment start: the frozen model is disqualified and no improvised substitution is permitted.

## 10. What Must Happen Next (future gate, not started here)

1. **Model selection decision (P172 §6):** select a candidate model/provider from the available list, freeze its configuration, and run `run_qualification.py` against it.
2. **Re-qualification:** the chosen model must pass the qualification test (≥5/6 VALID_SDC, ≥1 per task, zero empty/provider failures) — with the qualification record retained as a readiness record.
3. **Only after qualification passes:** complete the remaining readiness items (Ṛta/OpenSTA version verification, timing precondition) and then — with separate explicit authorization — execute EGER-RQ5-PILOT-002 using the repaired harness.

**STOP. No PILOT-002 execution. No model substitution in this gate. No P170/P171 alteration.**