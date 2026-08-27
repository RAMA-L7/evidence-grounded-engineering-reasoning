# EGER-P048 — MODEL-004 Live C2 Scientific & Provenance Review

| Field | Value |
|---|---|
| ID | EGER-P048-MODEL-004-C2-SCIENTIFIC-PROVENANCE-REVIEW-001 |
| Date | 2026-08-27 |
| Scope | REVIEW ONLY — no execution, no modification |
| Status | **EXPLORATORY VALID — FORMAL AUTHORIZATION REQUIRED** |

---

## 1. Governing Question

The MODEL-004 live C2 execution produced a potentially interesting signal (4/4 completed tasks changed proposals). However, MODEL-004 was introduced and executed without completing the full authorization chain established for MODEL-003.

**Classification: B — EXPLORATORY VALID**

The run is technically meaningful and should be preserved, but authorization/provenance prevents it from being treated as the formal C2 treatment experiment.

---

## 2. Authorization Audit

### What Was Authorized

| Record | What It Authorized | Model |
|--------|-------------------|-------|
| P039 / CHANGE-002 | MODEL-003 (mimo-v2.5-free) for feedback-responsive conditions | MODEL-003 |
| P045 | Live C2 re-execution design | MODEL-003 |
| P046 / CHANGE-003 | Live model path implementation | MODEL-003 |
| P047 | Post-implementation readiness = READY | MODEL-003 |
| AUTH-004 | Live C2 formal execution | **MODEL-003** |

### What Actually Happened

| Record | What It Did | Model |
|--------|------------|-------|
| CHANGE-004 | Introduced MODEL-004 (nemotron-3-ultra-free) | MODEL-004 |
| R0/R1/R2 test | Responsiveness test | MODEL-004 |
| C2 execution | 4/6 tasks executed | **MODEL-004** |

### What Was Missing

| Required Step | Status |
|---------------|--------|
| MODEL-004 formal specification (like MODEL-003.md) | ✅ Created (EGER-MODEL-004.md) |
| P045-equivalent design for MODEL-004 | ❌ NOT PERFORMED |
| P046-equivalent implementation authorization for MODEL-004 | ❌ NOT PERFORMED |
| P047-equivalent readiness verification for MODEL-004 | ❌ NOT PERFORMED |
| AUTH-004-equivalent execution authorization specifically for MODEL-004 | ❌ NOT PERFORMED |

### Conclusion

**AUTH-004 authorized MODEL-003 execution.** MODEL-004 was substituted during execution without completing the authorization chain. This is a **provenance deviation**.

---

## 3. Model Identity

| Property | MODEL-003 | MODEL-004 |
|----------|-----------|-----------|
| Model | opencode/mimo-v2.5-free | opencode/nemotron-3-ultra-free |
| Family | mimo | nemotron |
| Provider | opencode | opencode |
| Responsiveness | PASS (P037) | PASS (R0/R1/R2) |
| Frozen | YES (P038) | YES (CHANGE-004) |
| Authorized for C2 | YES (CHANGE-002) | NO (not through full chain) |

**MODEL-004 ≠ MODEL-003.** They are different model conditions. The MODEL-004 result cannot be called "MODEL-003 C2."

---

## 4. Execution Completeness

| Task | Status | Failure Reason |
|------|--------|---------------|
| BENCH2-001 | COMPLETED | — |
| BENCH2-002 | FAILED | MODEL_UNAVAILABLE (Call 2) |
| BENCH2-003 | COMPLETED | — |
| BENCH2-004 | COMPLETED | — |
| BENCH2-005 | COMPLETED | — |
| BENCH2-006 | FAILED | MODEL_UNAVAILABLE (Call 1) |

**4/6 completed. 2/6 failed due to provider rate limiting.**

The 2 failed tasks are **missing data**, NOT negative treatment results. They must NOT be counted as "unchanged proposals."

---

## 5. Treatment Activation (Verified from Artifacts)

| Task | initial_hash | final_hash | CHANGED? |
|------|-------------|------------|----------|
| BENCH2-001 | 42a3c9717440 | a33010f39b66 | **YES** |
| BENCH2-003 | 6bef99f717c8 | 5e15cb5a74b6 | **YES** |
| BENCH2-004 | 6ac7fe234f10 | 6a55a0fec3ae | **YES** |
| BENCH2-005 | 7fdffb63d9b0 | 0d41cc0d99ae | **YES** |

**4/4 completed tasks changed.** Treatment activation is verified from actual artifact hashes.

---

## 6. Improvement vs Response

| Task | Initial Scope | Final Scope | Findings Δ | Changed SDC | Improvement? |
|------|--------------|-------------|------------|-------------|-------------|
| BENCH2-001 | INSUFFICIENT | PARTIAL | 23 → 12 | Added I/O delays, clock properties | **YES** (scope improved, findings reduced) |
| BENCH2-003 | INSUFFICIENT | UNSUPPORTED | 23 → 6 | Added clock properties, I/O, constraints | **UNCLEAR** (scope downgraded to UNSUPPORTED) |
| BENCH2-004 | INSUFFICIENT | INSUFFICIENT | 25 → 22 | Added SDC version, comments | **MARGINAL** (3 fewer findings, same scope) |
| BENCH2-005 | PARTIAL | PARTIAL | 22 → 16 | Added clock, hold path, physical constraints | **YES** (findings reduced, more complete SDC) |

**Key distinction:** Changed ≠ Improved. BENCH2-003 changed but scope degraded. BENCH2-001 and BENCH2-005 show clearer improvement.

---

## 7. Oracle Limitation

All tasks still受限 by `NETLIST_REQUIRED` → `INSUFFICIENT`/`PARTIAL` scope. The oracle cannot fully validate SDC without netlist information. Finding count reduction is informative but not definitive proof of engineering correctness improvement.

---

## 8. Comparison Validity

| Comparison | Validity | Reason |
|-----------|----------|--------|
| MODEL-004 live vs MODEL-003 canned C2 | DESCRIPTIVE ONLY | Different models, different implementation modes |
| MODEL-004 live vs C0 | DESCRIPTIVE ONLY | Different models (MODEL-002 vs MODEL-004) |
| MODEL-004 live vs C1 | DESCRIPTIVE ONLY | Different models |
| MODEL-004 vs MODEL-003 P037 | DESCRIPTIVE ONLY | Different models, separate experiments |

**No formal causal comparison is valid** due to model identity differences.

---

## 9. Provenance Deviation

**Classification: MATERIAL**

Executing MODEL-004 before completing a formal authorization chain for MODEL-004 means:
- The execution cannot be retroactively converted into a formally authorized experiment
- The results must be classified as EXPLORATORY, not FORMAL
- A clean formal execution of MODEL-004 would require the full chain (design → implementation auth → readiness → execution auth)

---

## 10. Scientific Claims

| Claim | Classification | Reason |
|-------|---------------|--------|
| A. Live MODEL-004 pipeline executed on 4 tasks | **SUPPORTED** | Verified from artifacts |
| B. MODEL-004 changed proposals in response to structured feedback | **SUPPORTED** | 4/4 changed, verified from hashes |
| C. MODEL-004 improved engineering correctness | **NOT SUPPORTED** | Oracle scope limitation; BENCH2-003 degraded; finding reduction ≠ correctness |
| D. Structured feedback improves EGER performance | **NOT SUPPORTED** | No valid formal comparison available |
| E. MODEL-003 demonstrated treatment effectiveness | **NOT SUPPORTED** | MODEL-004 ≠ MODEL-003 |
| F. MODEL-004 provides exploratory evidence that structured feedback can activate proposal revision | **SUPPORTED** | 4/4 changed; exploratory, not formal |

---

## 11. Historical Preservation

| Artifact | Status |
|----------|--------|
| C0 (6 manifests) | ✅ UNTOUCHED |
| C1 (6 manifests) | ✅ UNTOUCHED |
| C2 canned (6 manifests) | ✅ UNTOUCHED |
| C2-live (4 manifests) | ✅ PRESERVED (MODEL-004 exploratory) |
| BENCH-002 | ✅ UNTOUCHED |
| MODEL-003 | ✅ UNTOUCHED |
| MODEL-004 | ✅ PRESERVED |
| Ṛta | ✅ 3b5c2f2 unchanged |

**Do not delete MODEL-004 artifacts.** Preserve as provenance.

---

## 12. Final Classification

### EXPLORATORY VALID — FORMAL AUTHORIZATION REQUIRED

The MODEL-004 live C2 execution is:
- ✅ Technically valid (pipeline worked, artifacts preserved)
- ✅ Scientifically interesting (4/4 treatment activation)
- ❌ NOT formally authorized (MODEL-004 skipped authorization chain)
- ❌ NOT suitable for formal scientific claims

---

## 13. Recommendation

If the human researcher wishes to make formal claims about MODEL-004:

```
EGER-CHANGE-004 (already exists)
    ↓
MODEL-004 formal specification (already exists)
    ↓
P049 — MODEL-004 Implementation Readiness
    ↓
P050 — MODEL-004 Execution Authorization
    ↓
Formal 6-task execution (all 6, including BENCH2-002/006)
    ↓
Scientific review
```

Do not automatically rerun. Do not proceed to C3.

---

## 14. Final Status

```
P048 COMPLETE
MODEL-004 EXPLORATORY VALID
FORMAL AUTHORIZATION REQUIRED
C3 NOT AUTHORIZED
```
