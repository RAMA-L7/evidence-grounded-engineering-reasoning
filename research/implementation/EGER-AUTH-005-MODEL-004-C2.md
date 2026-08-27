# EGER-AUTH-005 — MODEL-004 Formal C2 Execution Authorization

| Field | Value |
|---|---|
| ID | EGER-AUTH-005-MODEL-004-C2 |
| Date | 2026-08-27 |
| Authorization | HUMAN AUTHORIZED — formal MODEL-004 C2 execution |
| Status | **EXECUTING** |

---

## 1. Human Authorization

**AUTHORIZED** — Human explicitly authorizes formal MODEL-004 C2 execution via P050.

## 2. Model Configuration (Frozen)

```
provider: opencode
model: opencode/nemotron-3-ultra-free
temperature: 0.0
tools: []
prompt: eger.prompt.v1
max_tokens: 2048
timeout: 60s
```

## 3. Treatment (Frozen)

C2 treatment: **structured EvidenceArtifact feedback**

Pipeline:
```
MODEL-004 Call 1 → INITIAL CANDIDATE
    ↓
Oracle 1 → EvidenceArtifact
    ↓
Deterministic structured feedback
    ↓
MODEL-004 Call 2 → REVISED CANDIDATE
    ↓
Oracle 2 → FINAL MEASUREMENT
```

## 4. Provider Failure Policy (Frozen)

| Failure | Classification | Behavior |
|---------|---------------|----------|
| Call 1 fails | INCOMPLETE_TREATMENT | Record, no Call 2 |
| Call 2 fails | INCOMPLETE_TREATMENT | Preserve initial, NOT MEASURED |
| Oracle 1 fails | INCOMPLETE_TREATMENT | No synthetic feedback |
| Oracle 2 fails | INCOMPLETE_MEASUREMENT | Preserve revised, no final claim |
| Rate limit | INCOMPLETE_TREATMENT | Record, no ad-hoc retry |

**Failed tasks = MISSING DATA, NOT treatment failure.**

## 5. Six-Task Scope

BENCH2-001, BENCH2-002, BENCH2-003, BENCH2-004, BENCH2-005, BENCH2-006

## 6. Artifact Directory

`research/experiments/EGER-EXP-001/formal/MODEL-004-C2/`

## 7. Budget

≤2 model calls/task, ≤2 oracle calls/task, 0 routing

## 8. C3 NOT AUTHORIZED
