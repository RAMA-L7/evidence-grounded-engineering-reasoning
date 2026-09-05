# EGER CHANGE-045 — Model Qualification Resolution (P173-R)

## Baseline

- **Commit:** ba5135958e90ff25369b54e67bfa38b4c19fc660
- **Branch:** main
- **Prior change:** CHANGE-044 (P173 — Harness Repair & Readiness Gate, BLOCKED)

## Purpose

Resolve P173's BLOCKED outcome. Diagnosis showed the model-qualification failure was a harness invocation-protocol mismatch (chat-style stdout prompts vs. the model's file-writing agent behavior), not model incapacity. Repaired the invocation protocol per P172 §6 Option A and re-qualified: 6/6 VALID_SDC.

## Root Cause

`opencode run` runs the model as a file-writing agent (workspace = git root). Verbose role-preamble/"return text" prompts produce conversational filler; terse "Write the file timing.sdc. First line: ..." directives reliably produce SDC content, including revision responses to Oracle feedback.

## Changes

| File | Change |
|------|--------|
| `harness/providers.py` | OpenCodeModelProvider reads `timing.sdc` from the model workspace after run; stdout fallback; model-call timeout 60s → 180s |
| `harness/trial_runner.py` | `_build_prompt` rewritten to terse file-writing directive; added `_format_sdc_lines()`; no role preamble / OUTPUT RULES block |
| `run_qualification.py` | Uses repaired prompt; timeout 180s |
| `harness_tests/test_prompt_format.py` | NEW — 5 tests (file-writing directive, no chat triggers, feedback inclusion, required constructs) |
| `EGER-P173R-MODEL-QUALIFICATION-RESOLUTION-001.md` | NEW |
| `EGER-CHANGE-045.md` | NEW (this file) |

## Re-Qualification

- Model: `opencode/mimo-v2.5-free`
- 6 invocations: **6/6 VALID_SDC** (threshold ≥ 5/6), T1 = 3, T2 = 3, 0 empty/provider failures
- Record: `qualification_record.json` (local-only, not experimental data)

## Test Results

- Harness tests: 44/44 PASS (39 P173 + 5 new)
- EGER regression: 864/864 PASS

## Decision

**QUALIFIED** — model passes P172 §6 qualification under the repaired protocol. P173 BLOCKED resolved at the model-qualification item. Harness READY (fixture) + model QUALIFIED. Full experiment readiness (remaining P172 §16 items, real-provider smoke) confirmed by the gate authorized to run PILOT-002.

## Research Boundaries

- RQ-5 executed: NO (PILOT-002 not run)
- New experiment executed: NO
- P170/P171/P173 records altered: NO
- Raw experimental data modified: NO
- Ṛta modified: NO
- RQ-4 reopened: NO
- C0–C5 conclusions changed: NO
- Oracle comparison performed: NO
- VerificationGate authority changed: NO
- EGER production code modified: NO
- Model invoked: YES — qualification only (readiness gate)