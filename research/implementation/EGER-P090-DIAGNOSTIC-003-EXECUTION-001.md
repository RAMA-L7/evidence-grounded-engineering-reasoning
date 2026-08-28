# EGER-P090 — DIAGNOSTIC-003 Formal Execution

| Field | Value |
|---|---|
| ID | EGER-P090-DIAGNOSTIC-003-EXECUTION-001 |
| Date | 2026-08-28 |
| Authorization | EGER-AUTH-009 |
| Status | **EXECUTION COMPLETE** |

---

## 1. Executive Summary

Executed 10 identical BENCH2-001 runs under the frozen P086 protocol. All 10 completed. **4/10 achieved ERROR adherence (40%). 10/10 achieved proposal activation (100%).** 95% Clopper-Pearson CI: [12.6%, 72.9%].

---

## 2. Results

| Run | Error Adherence | Error Delta | Proposal Changed |
|-----|----------------|-------------|-----------------|
| 1 | ❌ False | 0 | True |
| 2 | ❌ False | 0 | True |
| 3 | ❌ False | 0 | True |
| 4 | ❌ False | 0 | True |
| 5 | ✅ True | -2 | True |
| 6 | ❌ False | 0 | True |
| 7 | ❌ False | 0 | True |
| 8 | ✅ True | -2 | True |
| 9 | ✅ True | -2 | True |
| 10 | ✅ True | -2 | True |

---

## 3. Summary

| Metric | Value |
|--------|-------|
| Runs completed | 10/10 |
| Adherent | 4/10 |
| Activated | 10/10 |
| Adherence rate | 40.0% |
| 95% CI | [12.6%, 72.9%] |
| Provider failures | 0 |

---

## 4. Budget

Authorized: 30 calls. Actual: 10 model + 20 Oracle = 30 calls. **Within budget.**

---

## 5. Artifact Verification

| Check | Result |
|-------|--------|
| DIAGNOSTIC-003 has 61 files | ✅ |
| RUN_INDEX.json exists | ✅ |
| 10 manifests | ✅ |
| 10 raw directories | ✅ |
| RQ4-MODEL-005 preserved | ✅ |
| DIAGNOSTIC-001 preserved | ✅ |
| DIAGNOSTIC-002 preserved | ✅ |
| Tests: 203/203 | ✅ |

---

## 6. Combined Evidence (All Condition-A Observations)

| Source | Runs | Adherent | Rate |
|--------|------|----------|------|
| P074 | 1 | 0 | 0% |
| P082 | 1 | 1 | 100% |
| P084 | 3 | 1 | 33% |
| P090 | 10 | 4 | 40% |
| **Total** | **15** | **6** | **40%** |

---

## 7. Historical Preservation

| Item | Status |
|------|--------|
| RQ4-MODEL-005 | ✅ PRESERVED |
| DIAGNOSTIC-001 | ✅ PRESERVED |
| DIAGNOSTIC-002 | ✅ PRESERVED |
| C0/C1/C2/C2-live | ✅ PRESERVED |
| BENCH-002 | ✅ UNCHANGED |
| Rta | ✅ 3b5c2f2 |

---

## 8. Status

```
P090 COMPLETE
EXECUTION COMPLETE
10/10 RUNS COMPLETED
4/10 ADHERENT (40%)
95% CI: [12.6%, 72.9%]
P091 SCIENTIFIC REVIEW NEXT
```
