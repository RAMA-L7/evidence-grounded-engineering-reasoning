# EGER-P068 — RQ-4 Model Availability & Change Decision

| Field | Value |
|---|---|
| ID | EGER-P068-RQ4-MODEL-AVAILABILITY-DECISION-001 |
| Date | 2026-08-28 |
| Status | **RQ-4 REMAINS BLOCKED — NEW MODEL CHANGE CONTROL REQUIRED** |

---

## 1. Model Availability Snapshot

| Model | Status | Evidence |
|-------|--------|----------|
| nemotron-3-ultra-free (MODEL-004) | ❌ UNAVAILABLE | Timeout after 60s, no response, 502 upstream errors in logs |
| mimo-v2.5-free (MODEL-003) | ✅ RESPONSIVE | Returns "ALIVE" within 60s, SDC generation verified |

---

## 2. AUTH-006 Permit Analysis

AUTH-006 explicitly states:

> "This authorization does NOT authorize: changing MODEL-004"
> "Model: opencode/nemotron-3-ultra-free"

**AUTH-006 does NOT permit switching to mimo-v2.5-free.** A new change control and authorization would be required.

---

## 3. Scientific Implications of Model Switch

### What Would Change

| Parameter | MODEL-004 (frozen) | mimo-v2.5-free |
|-----------|-------------------|----------------|
| Model identity | nemotron-3-ultra-free | mimo-v2.5-free |
| Provider backend | Nvidia | Different |
| Model behavior | Unknown for RQ-003 | Demonstrated responsive in P037 |

### Why This Matters

RQ-4 asks: "Does structured evidence feedback cause an improvement in engineering proposal correctness?"

The answer depends on holding the model constant. If the model changes:
- The treatment effect could be due to the model, not the feedback
- The comparison with historical MODEL-003 C2 results becomes invalid
- The controlled design is broken

### Conclusion

Switching models mid-experiment introduces a **model confound**. The RQ-4 design specifically requires the same model in both branches AND across attempts to maintain scientific validity.

---

## 4. Decision Options

### Option A: Continue Waiting for MODEL-004

- **Pros:** Preserves frozen design, no change control needed
- **Cons:** Provider may remain unavailable indefinitely
- **Risk:** No guarantee nemotron recovers

### Option B: Create MODEL-005 / Change Control

- **Pros:** Uses available model, gets RQ-4 executed
- **Cons:** Breaks frozen design, requires new authorization chain (P061-P064 equivalent for new model)
- **Risk:** MODEL-005 responsiveness may also be temporary

### Option C: Preserve RQ-4 as Blocked

- **Pros:** Honest scientific record, no forced results
- **Cons:** RQ-4 remains unanswered
- **Risk:** Indefinite deferral

---

## 5. Recommendation

**RQ-4 REMAINS BLOCKED — NEW MODEL CHANGE CONTROL REQUIRED**

The scientifically correct action is Option B: create a formal change control to introduce a new MODEL-005 (mimo-v2.5-free) with its own authorization chain.

This is NOT a simple model substitution. It requires:
1. New MODEL-005 specification
2. New change control (EGER-CHANGE-008)
3. New readiness verification
4. New execution authorization
5. New formal execution

The historical MODEL-004 RQ-4 attempt (P065/P066) remains classified as INCOMPLETE (provider failure).

---

## 6. What Must NOT Happen

- ❌ Do not silently substitute mimo-v2.5-free into the existing RQ-4 runner
- ❌ Do not treat MODEL-003 results as MODEL-004 results
- ❌ Do not claim RQ-4 results from a different model
- ❌ Do not combine MODEL-004 and MODEL-003 results

---

## 7. Verdict

**RQ-4 REMAINS BLOCKED — NEW MODEL CHANGE CONTROL REQUIRED**

AUTH-006 does not permit model substitution. A formal change control chain (EGER-CHANGE-008 → MODEL-005 → new authorization) is required before RQ-4 can be executed with mimo-v2.5-free.
