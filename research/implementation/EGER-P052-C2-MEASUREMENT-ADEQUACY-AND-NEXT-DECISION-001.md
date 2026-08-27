# EGER-P052 — C2 Measurement Adequacy & Next-Experiment Decision

| Field | Value |
|---|---|
| ID | EGER-P052-C2-MEASUREMENT-ADEQUACY-AND-NEXT-DECISION-001 |
| Date | 2026-08-27 |
| Scope | SCIENTIFIC DECISION ANALYSIS ONLY — no execution |
| Status | **MEASUREMENT ADEQUACY: CONDITIONAL — IMPROVE BEFORE C3** |

---

## 1. Executive Verdict

**C2 has answered the treatment-activation question. The measurement layer is the current bottleneck.** Before proceeding to C3 (epistemic state), EGER should strengthen its correctness-measurement capability. The oracle's `NETLIST_REQUIRED` limitation and the 2/6 missing tasks prevent definitive improvement claims.

---

## 2. Research Question Status

| RQ | Question | Answered By | Status |
|----|----------|-------------|--------|
| RQ-1 | Can EGER deliver evidence? | C0 (oracle execution), C1/C2 (feedback delivery) | **SUPPORTED** |
| RQ-2 | Can a model respond to evidence? | P037 (responsiveness test), C2/MODEL-004 (4/4 changed) | **SUPPORTED** |
| RQ-3 | Does evidence cause proposal revision? | C2/MODEL-004 (4/4 changed, 3/4 clearly conditioned) | **SUPPORTED** |
| RQ-4 | Does revision improve engineering correctness? | C2/MODEL-004 (2/4 scope improved, but oracle limitation) | **INCONCLUSIVE** |
| RQ-5 | Does epistemic state improve evidence-conditioned reasoning? | Not yet tested | **OPEN** |

---

## 3. Measurement Gap Analysis

### What the Oracle CAN Establish

| Capability | Evidence |
|-----------|----------|
| Finding detection | ✅ Findings identified per SDC rule |
| Finding severity classification | ✅ ERROR/WARNING/INFO |
| Scope assessment | ✅ FULL/PARTIAL/INSUFFICIENT/UNSUPPORTED |
| Evidence delivery | ✅ Deterministic EvidenceArtifact |

### What the Oracle CANNOT Establish

| Limitation | Consequence |
|-----------|-------------|
| NETLIST_REQUIRED → INSUFFICIENT | Cannot validate SDC correctness without netlist |
| PARTIAL scope | Can detect some issues but cannot fully validate |
| No ground-truth comparison | Cannot measure "correctness" directly |
| Finding reduction ≠ correctness | Fewer findings detected doesn't mean fewer errors exist |

### Critical Distinction

```
finding reduction ≠ correctness improvement
scope improvement ≠ correctness improvement
INVALID → VALID = oracle claims fewer issues detected
```

The oracle measures **what it can detect**, not **engineering truth**. Under `INSUFFICIENT` scope, it cannot detect most issues, so `VALID_ARTIFACT` under `PARTIAL` scope means "fewer issues detected" — not "correct SDC."

---

## 4. Outcome Progression

| Condition | INVALID | INSUFFICIENT | VALID | Total |
|-----------|---------|-------------|-------|-------|
| C0 (MODEL-002) | 5 | 1 | 0 | 6 |
| C2 canned (MODEL-003) | 5 | 1 | 0 | 6 |
| MODEL-004 formal | 2 | 0 | 2 | 4 |

**Observation:** MODEL-004 produced 2 VALID_ARTIFACT outcomes where C0/C2 canned had 0. This is **descriptively interesting** but not a formal causal claim (different models, different implementation modes).

---

## 5. Missing Data Analysis

| Task | Status | Could Affect Conclusion? |
|------|--------|------------------------|
| BENCH2-003 | MODEL_UNAVAILABLE | Unknown — could be VALID or INVALID |
| BENCH2-006 | MODEL_UNAVAILABLE | Unknown — could be VALID or INVALID |

**Missingness is NOT random.** Rate limits may correlate with execution time, which could correlate with model behavior. The 2/6 missing tasks cannot be assumed to follow the same pattern as the 4/4 completed.

**Impact:** The 4/4 activation rate is calculated from completed tasks only. If missing tasks would have shown different behavior, the conclusion changes.

---

## 6. P048/P050 Replication

| Run | Completed | Changed | Scope Improved |
|-----|-----------|---------|---------------|
| P048 exploratory | 4/6 | 4/4 | 2/4 |
| P050 formal | 4/6 | 4/4 | 2/4 |

**Qualitative signal replicated.** Both runs show:
- Same completion rate (4/6)
- Same activation rate (4/4)
- Same scope improvement pattern (BENCH2-001/002 improved, BENCH2-004/005 didn't)

**Not fully independent** — same model, same benchmark, same rate-limit issues. But the consistency strengthens confidence in the treatment-activation finding.

---

## 7. C3 Gate Analysis

> Is it scientifically useful to add epistemic state before we can reliably determine whether the simpler C2 feedback treatment improves engineering outcomes?

**NO.** C3 introduces epistemic state (hypothesis/validated/refuted/unknown). But:

1. We cannot yet determine whether C2's feedback improves outcomes (RQ-4 is INCONCLUSIVE)
2. Adding epistemic state on top of an incompletely-measured C2 creates a compounding measurement problem
3. C3's epistemic transitions require the oracle to establish VALIDATED/REFUTED — which requires FULL scope — which the current oracle cannot provide for these tasks
4. The scientific question "does epistemic state improve reasoning?" presupposes that we can measure reasoning quality — which we currently cannot

**C3 is premature until measurement is adequate.**

---

## 8. Oracle Options (Conceptual)

| Option | Scientific Value | Risk | Cost | Answers RQ-4? |
|--------|-----------------|------|------|---------------|
| A. Improve oracle evidence availability | HIGH | Low — extends existing oracle | Medium | Partially |
| B. Provide netlist/design context | HIGH | Low — task augmentation | Low | Yes |
| C. Add independent correctness oracle | VERY HIGH | Medium — new validation path | High | Yes |
| D. Repeat C2 with existing oracle | LOW — same measurement limitation | Low | Low | No |
| E. Proceed to C3 | LOW — measurement bottleneck remains | High — compounds unknowns | Low | No |

---

## 9. Next-Step Decision Matrix

| Option | Description | Scientific Value | Recommended? |
|--------|-------------|-----------------|-------------|
| 1 | Accept C2 and proceed to C3 | LOW — measurement bottleneck | NO |
| 2 | Re-run missing C2 tasks only | LOW — same measurement limitation | NO |
| 3 | Improve oracle/measurement before further treatment experiments | **HIGH** — addresses root cause | **YES** |
| 4 | Design a stronger correctness-measurement experiment | HIGH — long-term value | SECONDARY |
| 5 | Stop C2 research — current evidence sufficient | MEDIUM — treatment activation established | NO (premature) |

---

## 10. Recommendation

**Option 3: Improve oracle/measurement before further treatment experiments.**

### Rationale

1. **Treatment activation is established** (RQ-3 SUPPORTED)
2. **Correctness measurement is the bottleneck** (RQ-4 INCONCLUSIVE)
3. **C3 cannot answer its question without adequate measurement** (RQ-5 requires RQ-4 to be resolvable)
4. **The oracle limitation is the single biggest scientific blocker**

### Specific Improvement Path

The most impactful improvement would be:

**Provide netlist/design context to the oracle** so that `get_ports`/`get_cells` can achieve `FULL` scope instead of `INSUFFICIENT`. This would:
- Enable the oracle to fully validate SDC
- Allow `VALIDATED` outcomes
- Make correctness measurement possible
- Not require modifying the oracle itself (just the benchmark task inputs)

### What This Is NOT

- This is NOT a recommendation to modify Ṛta
- This is NOT a recommendation to change the oracle engine
- This IS a recommendation to augment the benchmark task inputs with required context

---

## 11. C2 Summary

C2 has successfully established:

| Finding | Status |
|---------|--------|
| Feedback delivery works | ✅ SUPPORTED |
| Model can receive structured evidence | ✅ SUPPORTED |
| Model revises proposals in response | ✅ SUPPORTED |
| Revisions correspond to findings | ✅ SUPPORTED (3/4 clearly) |
| Revisions improve engineering correctness | ⚠️ INCONCLUSIVE (oracle limitation) |
| C2 treatment is universally effective | ❌ NOT SUPPORTED (n=4, single model) |

---

## 12. Final Status

```
P052 COMPLETE
MEASUREMENT ADEQUACY: CONDITIONAL
C3: NOT RECOMMENDED (premature)
NEXT: Improve measurement layer
TREATMENT ACTIVATION: ESTABLISHED (C2 complete)
CORRECTNESS: INCONCLUSIVE (oracle limitation)
```
