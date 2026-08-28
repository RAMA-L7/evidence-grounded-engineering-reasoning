# EGER-P069 — MODEL-005 RQ-4 Change-Control Design

| Field | Value |
|---|---|
| ID | EGER-P069-MODEL-005-RQ4-CHANGE-DESIGN-001 |
| Date | 2026-08-28 |
| Scope | DESIGN ONLY — no execution, no implementation |
| Status | **DESIGN READY FOR HUMAN REVIEW** |

---

## 1. Executive Summary

MODEL-004 (nemotron-3-ultra-free) is provider-unavailable (502 upstream). This document designs a formal change control to introduce MODEL-005 (mimo-v2.5-free) for RQ-4 execution, preserving the controlled experimental design while changing the model identity.

---

## 2. What Changes (MODEL-004 → MODEL-005)

| Parameter | MODEL-004 (frozen) | MODEL-005 (proposed) |
|-----------|-------------------|---------------------|
| Model identity | opencode/nemotron-3-ultra-free | opencode/mimo-v2.5-free |
| Provider backend | Nvidia | Different |
| MODEL_ID | EGER-MODEL-004 | EGER-MODEL-005 |
| Responsiveness | ❌ UNAVAILABLE | ✅ VERIFIED |
| Historical C2 data | P048/P050/P051 exploratory/formal | None for RQ-4 |

---

## 3. What Must Remain Identical

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Temperature | 0.0 | Same sampling conditions |
| Max tokens | 2048 | Same generation budget |
| Tools | [] | No tool access |
| Prompt | eger.prompt.v1 | Same instruction set |
| Timeout | 60s | Same latency budget |
| Benchmark | BENCH-002 v0.1 (6 tasks) | Same held-out tasks |
| Oracle | Ṛta v1.5.11 (3b5c2f2) | Same measurement |
| Design metadata | eger.design_metadata.v1 | Same validation |
| Structured feedback | structured_feedback.py | Same treatment |
| Primary metric | ERROR-severity delta | Same outcome |
| Paired design | Same initial candidate, control vs treatment | Same causal structure |
| Information boundary | ENGINEER_VISIBLE / ORACLE_VISIBLE / EVALUATOR_ONLY | Same isolation |
| Artifact namespace | formal/RQ4/ (new) | Separate from MODEL-004 |
| Call budget | 3 model + 3 oracle per task | Same resource limit |
| Provider failure policy | Same frozen policy | Same failure semantics |

---

## 4. New Artifact Namespace

```
research/experiments/EGER-EXP-001/formal/RQ4-MODEL-005/
    ├── control/
    │   ├── manifests/
    │   └── raw/
    ├── treatment/
    │   ├── manifests/
    │   └── raw/
    └── RUN_INDEX.json
```

This is SEPARATE from:
- `formal/RQ4/` (MODEL-004 attempt — INCOMPLETE)
- `formal/C0/`, `formal/C1/`, `formal/C2/` (historical)
- `formal/C2-live/`, `formal/MODEL-004-C2/` (historical)

---

## 5. Model Configuration (Frozen)

### MODEL-005 Specification

| Parameter | Value |
|-----------|-------|
| ID | EGER-MODEL-005 |
| Provider | opencode |
| Model | opencode/mimo-v2.5-free |
| Version | NOT_EXPOSED |
| Temperature | 0.0 |
| Max tokens | 2048 |
| Tools | [] |
| Prompt | eger.prompt.v1 |
| Timeout | 60s |
| Responsiveness | Verified 2026-08-28 |

### Relationship to MODEL-003

MODEL-005 uses the same model as historical MODEL-003 (mimo-v2.5-free). However:
- MODEL-003 was used for C2 canned execution (P041-P043)
- MODEL-005 is used for RQ-4 controlled experiment (new)
- They are **separate experimental conditions** with different designs
- MODEL-003 historical results remain as background context only

---

## 6. Provenance Requirements

### MODEL-005 Must Record

| Field | Source |
|-------|--------|
| model_id | EGER-MODEL-005 |
| model_name | opencode/mimo-v2.5-free |
| model_change_justification | P068 — MODEL-004 provider unavailable |
| predecessor | EGER-MODEL-004 (nemotron-3-ultra-free) |
| predecessor_status | INCOMPLETE (provider failure) |
| change_control | EGER-CHANGE-008 (pending) |
| authorization | New AUTH required (pending) |
| benchmark | BENCH-002 v0.1 (UNCHANGED) |
| oracle | Ṛta v1.5.11 3b5c2f2 (UNCHANGED) |
| treatment | Structured EvidenceArtifact (UNCHANGED) |
| metric | ERROR-severity delta (UNCHANGED) |
| namespace | formal/RQ4-MODEL-005/ |

### Must NOT Record

- ❌ MODEL-004 results as MODEL-005 results
- ❌ MODEL-003 results as MODEL-005 results
- ❌ Combined statistics across model conditions
- ❌ Claims of improvement over historical conditions

---

## 7. Relationship to Prior Evidence

| Prior Result | Classification | MODEL-005 Relationship |
|-------------|----------------|----------------------|
| MODEL-003 C2 (P041-P043) | Historical background | Not reinterpreted as RQ-4 |
| MODEL-004 exploratory (P048) | Historical background | Not reinterpreted as RQ-4 |
| MODEL-004 formal (P050-P051) | Historical background | Not reinterpreted as RQ-4 |
| MODEL-004 RQ-4 attempt (P065) | INCOMPLETE (provider failure) | Separate condition |
| P061 RQ-4 design | Design template | Adapted for MODEL-005 |
| P062-P064 implementation | Infrastructure | Runner reused, model config changed |

### Critical Rule

> MODEL-005 RQ-4 results are a **new controlled experiment**, not a continuation of MODEL-004 RQ-4.

If MODEL-004 later becomes available, a separate execution under MODEL-004 is required for comparison.

---

## 8. Required Gates (Before Execution)

```
P069 (this design) ← YOU ARE HERE
    ↓
Human review / approval
    ↓
EGER-CHANGE-008 (change-control for MODEL-005)
    ↓
MODEL-005 specification (EGER-MODEL-005.md)
    ↓
P070 — MODEL-005 readiness verification
    ↓
P071 — MODEL-005 RQ-4 execution authorization
    ↓
Controlled RQ-4 execution with MODEL-005
    ↓
Scientific review
    ↓
RQ-4 decision
    ↓
Only then: C3
```

---

## 9. Scientific Implications

### What MODEL-005 RQ-4 Can Answer

> "Does structured evidence feedback cause an improvement in engineering proposal correctness **under mimo-v2.5-free**?"

### What MODEL-005 RQ-4 Cannot Answer

> "Does structured evidence feedback cause an improvement **under nemotron-3-ultra-free**?" (MODEL-004 unavailable)

> "Is mimo-v2.5-free better than nemotron-3-ultra-free?" (no controlled comparison)

### Generalizability

RQ-4 under MODEL-005 is valid within the BENCH-002 benchmark under mimo-v2.5-free. It does not generalize to other models without additional experiments.

---

## 10. What Must NOT Happen

- ❌ Do not silently substitute MODEL-005 into MODEL-004's execution slot
- ❌ Do not treat MODEL-005 results as MODEL-004 results
- ❌ Do not combine MODEL-004 and MODEL-005 statistics
- ❌ Do not claim MODEL-005 results answer the same question as MODEL-004 would have
- ❌ Do not modify BENCH-002, Oracle, or historical artifacts
- ❌ Do not modify Ṛta
- ❌ Do not authorize execution during this design phase

---

## 11. Verdict

**DESIGN READY FOR HUMAN REVIEW**

The change from MODEL-004 to MODEL-005 is scientifically justified by provider unavailability. The controlled experimental design is preserved. A new change-control chain (EGER-CHANGE-008 → MODEL-005 → authorization) is required before execution.
