# EGER-CHANGE-008 — MODEL-005 Introduction for RQ-4

| Field | Value |
|---|---|
| ID | EGER-CHANGE-008 |
| Date | 2026-08-28 |
| Governing Decision | P068, P069, P070 |
| Status | **IMPLEMENTED** |

---

## 1. Justification

MODEL-004 (nemotron-3-ultra-free) is provider-unavailable (Nvidia502 upstream). MODEL-005 (mimo-v2.5-free) is verified responsive. RQ-4 cannot be executed with MODEL-004. A formal model change is required.

---

## 2. Scope

### INCLUDED

| What | Description |
|------|-------------|
| Runner constants | MODEL_ID, MODEL_NAME updated to MODEL-005 |
| Model specification | EGER-MODEL-005.md created |
| Tests | Updated for MODEL-005 identity |

### EXCLUDED (must not change)

| What | Status |
|------|--------|
| BENCH-002 | UNCHANGED |
| Oracle | UNCHANGED |
| Treatment | UNCHANGED |
| Metrics | UNCHANGED |
| Information boundary | UNCHANGED |
| C0/C1/C2 artifacts | PRESERVED |
| MODEL-004 artifacts | PRESERVED |
| Ṛta | UNTOUCHED |

---

## 3. Model Change

| Parameter | MODEL-004 (old) | MODEL-005 (new) |
|-----------|----------------|----------------|
| Model ID | EGER-MODEL-004 | EGER-MODEL-005 |
| Model name | opencode/nemotron-3-ultra-free | opencode/mimo-v2.5-free |
| Namespace | formal/RQ4/ | formal/RQ4-MODEL-005/ |

---

## 4. What Remains Identical

Temperature (0.0), max tokens (2048), tools ([]), prompt (eger.prompt.v1), timeout (60s), benchmark (BENCH-002), Oracle (3b5c2f2), metadata (eger.design_metadata.v1), treatment (structured feedback), metric (ERROR-severity delta), paired design, information boundary, call budget (3+3), failure policy.
