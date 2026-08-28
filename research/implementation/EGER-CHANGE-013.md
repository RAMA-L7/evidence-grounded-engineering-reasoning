# EGER-CHANGE-013 — Mechanism Investigation Runner

## Change Identifier
EGER-CHANGE-013

## Phase
P108 — RQ-4 Adherence Mechanism Investigation Implementation

## Parent Design
P107 — RQ-4 Adherence Mechanism Investigation Design

## Governing Principal
Do not assume epistemic uncertainty is the cause. The investigation must test which
prompt components influence ERROR adherence, without presupposing the mechanism.

## Scope
Add a 4-condition mechanism investigation runner to determine which prompt components
influence ERROR-feedback adherence in BENCH2-001.

## Conditions
- Base: BENCH2-001 + minimal SDC + full feedback (baseline)
- E2b: Base + irrelevant SDC constructs (SDC content test)
- E3a: Base + broader task objective (framing test)
- E4a: Base + ERROR-only feedback (overload test)

## Configuration
- Model: MODEL-005 (opencode/mimo-v2.5-free)
- Runs per condition: 10
- Total runs: 40
- Budget: 120 calls (40 × 3)
- Namespace: formal/DIAGNOSTIC-006/

## Files Modified/Created
- research/experiments/EGER-EXP-001/run_mechanism_investigation.py (NEW)
- tests/test_mechanism_investigation.py (NEW)

## Test Results
19/19 mechanism-investigation tests PASS
258/258 full regression PASS

## Constraints
- No live model execution during implementation
- Historical RQ-4 and DIAGNOSTIC-001–005 artifacts preserved
- C3 remains unauthorized
- Do not encode "no prompt effect = provider nondeterminism" as a conclusion

## Verification
- 4 condition isolation verified programmatically
- Budget verified at 120 calls
- Namespace isolation verified
- Historical preservation verified
