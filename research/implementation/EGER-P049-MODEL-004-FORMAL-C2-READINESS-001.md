# EGER-P049 — MODEL-004 Formal C2 Readiness Verification

| Field | Value |
|---|---|
| ID | EGER-P049-MODEL-004-FORMAL-C2-READINESS-001 |
| Date | 2026-08-27 |
| Scope | READINESS AUDIT ONLY — no execution |
| Status | **READY — FORMAL C2 EXECUTION AUTHORIZATION REQUIRED** |

---

## 1. Executive Verdict

**MODEL-004 FORMAL C2 READY.** All implementation, boundary, preservation, and test criteria satisfied. The single remaining requirement is a provider failure policy for rate-limited tasks, which can be frozen before execution.

---

## 2. Model Identity

| Property | MODEL-003 | MODEL-004 |
|----------|-----------|-----------|
| Model | opencode/mimo-v2.5-free | opencode/nemotron-3-ultra-free |
| Family | mimo | nemotron |
| Frozen | YES (P038) | YES (CHANGE-004) |
| Status | FROZEN (rate-limited) | FROZEN (available) |

**They are distinct.** MODEL-004 cannot inherit MODEL-003 authorization.

---

## 3. MODEL-004 Freeze

| Property | Value | Frozen? |
|----------|-------|---------|
| provider | opencode | ✅ |
| model | opencode/nemotron-3-ultra-free | ✅ |
| version | NOT_EXPOSED | ✅ (documented) |
| temperature | 0.0 | ✅ |
| max_tokens | 2048 | ✅ |
| tools | [] | ✅ |
| prompt | eger.prompt.v1 | ✅ |
| timeout | 60s | ✅ |
| execution interface | opencode run via subprocess | ✅ |

**MODEL-004 is sufficiently frozen for formal execution.**

---

## 4. Live Implementation

| Check | Status | Evidence |
|-------|--------|----------|
| `live=True` → actual opencode | ✅ | `_invoke_live()` at model.py:78 |
| `live=False` → canned | ✅ | `_invoke_canned()` at model.py:110 |
| No silent fallback | ✅ | RuntimeError on failure, no try/except fallback |
| Windows shell support | ✅ | `shell=True` on Windows, `opencode.cmd` |
| Timeout enforcement | ✅ | `timeout=self.timeout` on subprocess |
| Error surfacing | ✅ | Non-zero exit → RuntimeError, empty output → RuntimeError |

---

## 5. Information Boundary

| Check | Status |
|-------|--------|
| Call 1: task context + objective only | ✅ (adapter.py:68-69) |
| Call 2: + initial candidate + structured feedback | ✅ (adapter.py:96-98) |
| No evaluator answers | ✅ (grep: 0 hits for evaluator in adapter) |
| No research canon | ✅ |
| No epistemic state | ✅ (not passed to adapter) |
| No authorization metadata | ✅ |

---

## 6. Treatment Definition

C2 treatment remains: **structured EvidenceArtifact feedback**

Model identity change (MODEL-003 → MODEL-004) does NOT redefine C2. The treatment is the same; only the model condition differs.

---

## 7. Oracle

| Check | Status |
|-------|--------|
| EvidenceOracle unchanged | ✅ |
| Ṛta 3b5c2f2 | ✅ |
| NETLIST_REQUIRED limitation | NON-BLOCKING — treatment activation observable regardless |
| rta_generate | ✅ 0 hits |

---

## 8. Budget

| Limit | Value | Enforced? |
|-------|-------|-----------|
| Model calls per task | ≤ 2 | ✅ (formal_runner_c2.py:57) |
| Oracle calls per task | ≤ 2 | ✅ (formal_runner_c2.py:58) |
| Routing calls | 0 | ✅ |
| Global model budget | ≤ 5 | ✅ |
| Global oracle budget | ≤ 5 | ✅ |

---

## 9. Provider Failure Policy (Recommended)

For formal execution, define before running:

| Failure | Classification | Behavior |
|---------|---------------|----------|
| Rate limit (MODEL_UNAVAILABLE) | INCOMPLETE_TREATMENT | Record as missing data, do not retry beyond budget |
| Timeout (60s) | INCOMPLETE_TREATMENT | Record, do not retry |
| Authentication failure | PROPOSAL_FAILURE | Record, stop |
| Empty response | PROPOSAL_FAILURE | Record, stop |
| Provider outage | INCOMPLETE_TREATMENT | Record, stop |

**Critical rule:** Failed tasks are **missing data**, NOT negative treatment results. They must NOT be counted as "unchanged proposals."

---

## 10. Artifact Separation

| Directory | Contents | Status |
|-----------|----------|--------|
| `formal/C2/` | Previous canned C2 (6 manifests) | ✅ PRESERVED |
| `formal/C2-live/` | Exploratory MODEL-004 run (4 manifests) | ✅ PRESERVED |
| `formal/C2-formal/` (proposed) | New formal MODEL-004 execution | NOT YET CREATED |

The formal MODEL-004 run must use a distinct namespace (e.g., `formal/C2-formal/` or `formal/MODEL-004-C2/`) to avoid confusion with the exploratory run.

---

## 11. Historical Preservation

| Artifact | Status |
|----------|--------|
| C0 (6 manifests) | ✅ UNTOUCHED |
| C1 (6 manifests) | ✅ UNTOUCHED |
| C2 canned (6 manifests) | ✅ UNTOUCHED |
| C2-live exploratory (4 manifests) | ✅ PRESERVED |
| BENCH-002 | ✅ UNTOUCHED |
| MODEL-003 | ✅ UNTOUCHED |
| EXP-001 v0.3 | ✅ UNTOUCHED |
| Ṛta | ✅ 3b5c2f2 unchanged |

---

## 12. Tests

```
95 passed in 15.96s
```

All tests pass. Live adapter tests verified.

---

## 13. Provenance

P048 classification preserved:
- Previous 4/6 run = EXPLORATORY VALID
- New formal run = separate, clean, fully authorized

---

## 14. GO/NO-GO

| Criterion | Status |
|-----------|--------|
| MODEL-004 identity frozen | ✅ |
| Live implementation frozen | ✅ |
| Information boundary verified | ✅ |
| Treatment definition frozen | ✅ |
| Oracle unchanged | ✅ |
| Provider failure policy | ⚠️ RECOMMENDED (define before execution) |
| Execution budget frozen | ✅ |
| Six-task scope defined | ✅ |
| Artifact namespace defined | ✅ |
| Provenance separation verified | ✅ |
| Benchmark untouched | ✅ |
| C0/C1/C2 preserved | ✅ |
| Ṛta untouched | ✅ |
| No blocking implementation gap | ✅ |

**READY** — One non-blocking recommendation (provider failure policy) can be frozen at execution authorization time.

---

## 15. Final Status

```
P049 COMPLETE
MODEL-004 FORMAL C2 READY
FORMAL EXECUTION AUTHORIZATION REQUIRED
```

---

**STOP.** Do not execute C2. Do not execute C3. Await P050 human authorization.
