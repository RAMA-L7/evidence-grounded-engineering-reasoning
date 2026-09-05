# EGER P173-R — Model Qualification Resolution (Harness Invocation Repair)

## 1. Objective

Resolve the P173 BLOCKED readiness outcome. P173 recorded a model-qualification FAIL (0/6 VALID_SDC) for `opencode/mimo-v2.5-free`. The user reported the model works. This record documents the diagnostic finding — the failure was a harness invocation-protocol mismatch, not model incapacity — and the repair that qualified the model 6/6.

**No experiment executed. No PILOT-002 run. No Ṛta/OpenSTA invocation. No raw experimental data modified.**

## 2. Historical Baseline

- **Commit:** ba51359 (P173 checkpoint, BLOCKED)
- **Branch:** main
- **P173 verdict preserved:** harness READY (fixture-validated), model qualification FAILED → BLOCKED

## 3. Root-Cause Diagnosis

Reproducing the P173 qualification against the model with the frozen chat-style prompt produced conversational filler in every invocation. Systematic probing revealed the actual behavior:

| Probe | Prompt style | Model behavior |
|-------|-------------|----------------|
| A | "Reply with exactly: QUALIFICATION_SANITY_OK" | Correct exact echo |
| B | Long role-preamble prompt ("You are an SDC author..." + REQUIRED CONTENT + OUTPUT RULES), request to return text | Conversational filler ("Understood. I'm ready to help...") |
| C | Directive file-writing ("Write the file timing.sdc. First line: ...") | Wrote timing.sdc with requested content (3/3) |
| D | Directive file-writing + Oracle feedback ("setup violation, clock too aggressive... overwrite") | Wrote corrected SDC (period relaxed 0.05 → 0.1) |
| E | Directive file-writing with design-context preamble | Went off-task (wrote simple_path.v Verilog instead) |
| F | Verbose OUTPUT-RULES block appended | Switched back to conversational mode |

**Conclusion:** `opencode run` invokes the model as a file-writing agent (workspace = git root). The model reliably produces SDC content when the prompt is a TERSE directive to write/overwrite `timing.sdc` with numbered SDC lines + Oracle feedback. Verbose role-preamble prompts or "return text on stdout" instructions switch it to chat mode, which produces filler. This was the P170/P173 failure mechanism — not model incapacity.

## 4. Harness Repair (P172 §6 Option A: keep model, repair prompt/harness)

| File | Change |
|------|--------|
| `harness/providers.py` | `OpenCodeModelProvider` now runs the model in its workspace and reads `timing.sdc` back after the run (falling back to stdout only if no file produced). Model-call timeout raised 60s → 180s (agent-mode model performs file ops and can exceed 60s; this is the model-call timeout, distinct from the frozen 60s Oracle-call timeout of P169). |
| `harness/trial_runner.py` | `_build_prompt` rewritten to the terse file-writing directive: "Write the file timing.sdc. First line: ... Second line: ... . Oracle feedback: ... . Overwrite the file with a complete, correct SDC ... The SDC must include create_clock, set_input_delay, set_output_delay. Do not create any other files." No role preamble, no OUTPUT RULES block. Added `_format_sdc_lines()` ordinal formatter. |
| `run_qualification.py` | Uses the repaired prompt; qualification timeout 60s → 180s. |
| `harness_tests/test_prompt_format.py` | NEW — 5 tests asserting the repaired prompt is a file-writing directive with no chat-mode triggers. |

Validity gate, matrix, retry, initial-Oracle-evaluation, NO_TIMING_CONSTRAINT, and PO-2 analysis are unchanged from P173.

## 5. Re-Qualification Result

```
Model: opencode/mimo-v2.5-free
Invocations: 6 (3 × T1, 3 × T2)
VALID_SDC: 6/6 (threshold ≥ 5/6)
Per-task valid: T1 = 3, T2 = 3
Empty/provider failures: 0
RESULT: PASS — model QUALIFIED
```

Sample qualified outputs (all contain create_clock + set_input_delay + set_output_delay):
- T1: "create_clock -name clk -period 10.0 [get_ports clk]\nset_input_delay -clock clk 2.0 [get_ports data_in]\nset_output_delay ..."
- T2: "create_clock -name clk -period 0.05 [get_ports clk]\nset_input_delay -clock clk 0.01 [get_ports data_in]\nset_output_delay ..."

Qualification record (updated, local-only, NOT experimental data): `research/experiments/EGER-RQ5-PILOT-001/qualification_record.json`.

## 6. Test Regression

```
Harness tests:  44 passed (39 P173 + 5 P173-R prompt-format)
EGER regression: 864 passed
```

No EGER production code modified.

## 7. Updated Readiness Position

| Area | P173 | P173-R |
|------|------|--------|
| Candidate validity gate | PASS | PASS (unchanged) |
| Model qualification | FAIL (0/6) | **PASS (6/6)** |
| Initial Oracle evaluation | PASS (fixture) | PASS (fixture) |
| Retry / counterbalancing / schema / analysis | PASS (fixture) | PASS (fixture) |
| Model-call timeout | 60s (too tight) | 180s |
| Invocation protocol | stdout text (wrong) | file-writing + read-back (correct) |

The single blocking prerequisite from P172 §6 is now satisfied. Remaining pre-experiment readiness items not yet executed in this gate (per P172 §16): Ṛta version verification, OpenSTA version/substrate verification, timing precondition (clock + constrained path present), and a git-clean check with real-provider wiring — these belong to the experiment-readiness confirmation immediately before any authorized PILOT-002 run.

## 8. Research Boundaries

```
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: NO (PILOT-002 NOT run)
C0-C5 conclusions changed: NO
Oracle comparison performed: NO
VerificationGate authority changed: NO
Epistemic-state / authorization logic added: NO
P170/P171/P173 records modified: NO (this is a new resolution record)
Raw experimental data modified: NO
EGER production code modified: NO
New experiment executed: NO
Model invoked: YES — qualification only (readiness gate, not experimental data)
```

## 9. Decision

**QUALIFIED** — `opencode/mimo-v2.5-free` passes the P172 §6 model-qualification test under the repaired file-writing invocation protocol (6/6 VALID_SDC).

P173's BLOCKED verdict is hereby resolved at the model-qualification item. The harness is READY at the fixture level and the model is QUALIFIED. Full experiment readiness (remaining P172 §16 items + real-provider smoke) must be confirmed by the explicit gate that is authorized to run PILOT-002.

**STOP. No PILOT-002 execution. No further model probing beyond qualification. No P170/P171/P173 alteration.**