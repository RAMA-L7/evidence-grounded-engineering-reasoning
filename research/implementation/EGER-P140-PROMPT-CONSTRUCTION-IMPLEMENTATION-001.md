# EGER-P140 — Prompt Construction Implementation

## Phase
P140 — Implementation + Deterministic Testing

## Date
2026-09-01

## Status
**PROMPT CONSTRUCTION IMPLEMENTED — ALL TESTS PASS**

---

## 1. Implementation Scope

Implemented the PromptBuilder that constructs deterministic prompts from
TaskDefinition, CandidateArtifact, and EvidenceArtifact:

```
TaskDefinition
    ↓
PromptBuilder.build()
    ↓
PromptRequest
```

---

## 2. Files Created/Modified

| File | Change |
|------|--------|
| `eger/prompting/builder.py` | NEW — PromptBuilder |
| `eger/prompting/__init__.py` | Updated — exports PromptBuilder |
| `tests/test_prompt_builder.py` | NEW — 32 deterministic tests |

---

## 3. PromptBuilder Design

### Two Modes

| Mode | Inputs | When |
|------|--------|------|
| Initial proposal | TaskDefinition only | First iteration |
| Revision | TaskDefinition + CandidateArtifact + EvidenceArtifact | After oracle evaluation |

### Prompt Structure

```
TASK
    task identity
    design context
    objective

CONSTRAINTS
    task-specific constraints

CURRENT CANDIDATE (revision only)
    candidate SDC
    candidate identity
    verification state

EVIDENCE (revision only)
    oracle status
    evidence scope
    summary (errors/warnings/info)
    findings (sorted: error → warning → info)

INSTRUCTION
    produce/revise SDC
    address evidence findings
```

### Deterministic Behavior

- Same inputs → same prompt text, always
- Findings sorted by severity (error→warning→info) then finding_id
- No random values, timestamps, or hidden state
- Deterministic prompt hash (SHA256)
- Deterministic request ID from prompt hash

### Broad Framing Configuration

The default objective template uses broader, production-quality framing:

```
Generate a complete, production-quality SDC for this design.
```

This is an engineering configuration/default, not a causal guarantee.

---

## 4. Invariants Enforced

- Same inputs → same prompt hash ✅
- Task identity preserved ✅
- Objective preserved ✅
- Design context preserved ✅
- Constraints preserved ✅
- Candidate identity preserved ✅
- Evidence identity preserved ✅
- ERROR/WARNING/INFO preserved ✅
- Findings sorted deterministically ✅
- Candidate not mutated ✅
- Evidence not mutated ✅
- No ACCEPT/REJECT in prompt ✅
- Injection resistance verified ✅

---

## 5. Deterministic Tests

```
New tests: 32/32 PASS
Full regression: 438/438 PASS
```

### Test Categories

| Category | Count | Tests |
|----------|-------|-------|
| Task handling | 5 | id, objective, context, constraints, ordering |
| Initial proposal | 4 | no candidate, no evidence, deterministic, iteration |
| Revision | 12 | candidate, evidence, summary, findings, entity, expected/observed, hints, instructions, IDs, verified |
| Determinism | 2 | same hash, different tasks |
| Empty evidence | 1 | no findings |
| Multiple findings | 1 | sorted |
| Candidate immutability | 1 | not mutated |
| Evidence immutability | 1 | not mutated |
| Authority boundary | 2 | no decisions, no decision field |
| Injection resistance | 3 | comments, messages, entities |

---

## 6. Compatibility Assessment

| Item | Status |
|------|--------|
| Existing eger/prompting/request.py | UNCHANGED |
| Existing eger/task/definition.py | UNCHANGED |
| Existing eger/evidence/schemas.py | UNCHANGED |
| Existing eger/engineer/ | UNCHANGED |
| Existing tests | ALL PASS |
| Historical artifacts | UNCHANGED |

---

## 7. Security Assessment

| Check | Result |
|-------|--------|
| API keys | NONE found |
| Credentials | NONE found |
| Secrets | NONE found |
| Evaluator-only material | NONE modified |

---

## 8. Historical Preservation

| Item | Status |
|------|--------|
| DIAGNOSTIC-001 through DIAGNOSTIC-009 | UNCHANGED |
| RQ4-MODEL-005 | UNCHANGED |
| All AUTH records | UNCHANGED |
| All P090–P139 records | UNCHANGED |

---

## 9. Scientific Boundary

P140 is an architecture implementation step. It does NOT prove:
- Framing causality
- Cross-model generalization
- C3 validity
- C4 effectiveness
- C5 effectiveness

Current research state remains:
```
C0: ESTABLISHED
C1: ESTABLISHED
C2: PARTIALLY SUPPORTED
C3: NOT JUSTIFIED
C4: DEFERRED
C5: DEFERRED

RQ-4: CLOSED
```

---

```
P140 COMPLETE
PROMPT CONSTRUCTION IMPLEMENTED

NO LIVE MODEL CALLS
NO EXPERIMENT EXECUTED

TASK → PROMPTREQUEST CONTRACT VERIFIED

DETERMINISTIC PROMPT GENERATION VERIFIED

NEW TESTS: 32/32 PASS
FULL REGRESSION: 438/438 PASS

HISTORICAL ARTIFACTS PRESERVED

C0: ESTABLISHED
C1: ESTABLISHED
C2: PARTIALLY SUPPORTED
C3: NOT JUSTIFIED
C4: DEFERRED
C5: DEFERRED

RQ-4: CLOSED

NEXT GATE: P141 — Revision Controller Implementation
```
