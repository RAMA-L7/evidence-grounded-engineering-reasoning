# EGER-CHANGE-019 — Prompt Construction Implementation

## Date
2026-09-01

## Status
**IMPLEMENTED**

## Reason for Change

P137 (Architecture Implementation Design) identified the need for a
PromptBuilder that constructs deterministic prompts from TaskDefinition.
P140 implements this component.

## Affected Modules

| Module | Change |
|--------|--------|
| `eger/prompting/builder.py` | NEW — PromptBuilder |
| `eger/prompting/__init__.py` | Updated — exports PromptBuilder |

## PromptBuilder Architecture

```
TaskDefinition
    ↓
PromptBuilder.build()
    ↓
PromptRequest
```

### Modes

| Mode | Inputs | Output |
|------|--------|--------|
| Initial proposal | TaskDefinition | PromptRequest |
| Revision | TaskDefinition + CandidateArtifact + EvidenceArtifact | PromptRequest |

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
    summary
    findings (sorted: error → warning → info)

INSTRUCTION
    produce/revise SDC
    address evidence
```

### Deterministic Behavior

- Same inputs → same prompt text, always
- Findings sorted by severity (error→warning→info) then finding_id
- No random values, timestamps, or hidden state
- Deterministic prompt hash (SHA256)

### Authority Boundaries

- PromptBuilder is PRESENTATION ONLY
- Cannot mutate TaskDefinition, CandidateArtifact, or EvidenceArtifact
- Cannot create ACCEPT/REJECT decisions
- Candidate/evidence text is DATA, not instructions

## Tests

- 32 new deterministic unit tests
- All 438 tests pass (32 new + 406 existing)

## Historical Preservation

- All DIAGNOSTIC artifacts: UNCHANGED
- All AUTH records: UNCHANGED
- All P090–P139 records: UNCHANGED

## Rollback

Remove `eger/prompting/builder.py` and `tests/test_prompt_builder.py`.
Revert `eger/prompting/__init__.py` to P138 version.
