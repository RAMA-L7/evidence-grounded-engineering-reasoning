# EGER-P058 — Measurement Re-Evaluation Scientific Audit & CVR Validation

| Field | Value |
|---|---|
| ID | EGER-P058-MEASUREMENT-REEVALUATION-SCIENTIFIC-AUDIT-001 |
| Date | 2026-08-27 |
| Scope | STRICT READ-ONLY scientific audit of P057 |
| Status | **MEASUREMENT NOT YET VALIDATED — CVR IMPLEMENTATION DEFECT** |

---

## 1. Executive Verdict

**MEASUREMENT NOT YET VALIDATED — CVR IMPLEMENTATION DEFECT.**

The scope enrichment (INSUFFICIENT → FULL/PARTIAL) works correctly. However, the CVR metric has an implementation defect: `metadata_validation` is not propagated to the `provenance` dict, so external consumers (including P057's re-evaluation) cannot access the CVR data.

This is a **fixable implementation gap**, not a scientific design flaw. The scope improvement is real and verified. The CVR metric needs a one-line fix to propagate `metadata_validation` to provenance.

---

## 2. CVR Implementation Audit

### 2.1 Root Cause

In `eger/oracle/adapter.py` line ~450, `metadata_validation` is included in the hash dict:

```python
evidence_dict_for_hash = {
    ...
    "metadata_validation": metadata_validation,  # ← IN HASH
}
```

But it is NOT included in the provenance dict:

```python
provenance = {
    "oracle_name": ORACLE_NAME,
    ...
    "raw_path": raw_evidence.raw_path,
    # ← metadata_validation MISSING HERE
}
```

### 2.2 Consequence

- `result.evidence.provenance.get('metadata_validation')` returns `None`
- P057's re-evaluation script reads `cvr = 0.0` (default when `metadata_validation` is `None`)
- `valid_refs = 0, total_refs = 0` (same reason)
- The scope enrichment IS working (hashes differ, scope changes from INSUFFICIENT to FULL)

### 2.3 Direct Verification

| Test | Result |
|------|--------|
| `_validate_with_metadata(sdc, md)` direct call | CVR = 1.0, valid_refs = 1, total_refs = 1 |
| `Oracle.validate(sdc, design_metadata=md)` with metadata | scope = FULL ✅ |
| `Oracle.validate(sdc)` without metadata | scope = INSUFFICIENT ✅ |
| `result.evidence.provenance.get('metadata_validation')` | None ❌ (BUG) |

### 2.4 Classification

**PARTIALLY IMPLEMENTED** — The core validation logic works, but the result is not accessible through the EvidenceArtifact provenance interface.

### 2.5 Fix Required

Add `metadata_validation` to the provenance dict in `adapter.py`. This is a one-line change:

```python
provenance = {
    ...
    "metadata_validation": metadata_validation,  # ADD THIS
}
```

**P058 does NOT make this fix.** It documents the defect for P059.

---

## 3. Scope vs Correctness Distinction

### 3.1 What FULL Means

| Dimension | Meaning |
|-----------|---------|
| `evidence_scope = FULL` | All required metadata was available for validation |
| `evidence_scope = FULL` | Does NOT mean "all constraints are correct" |
| `evidence_scope = FULL` | Does NOT mean "SDC is complete" |
| `evidence_scope = FULL` | Means "Oracle can now evaluate these constructs" |

### 3.2 What FULL Enables

With FULL scope, the Oracle can now:
- Validate port references (get_ports X → X exists in metadata)
- Validate clock references (get_clocks X → X exists in metadata)
- Check clock periods against metadata
- Apply semantic rules (SDC-005, SDC-006, etc.) with confidence

### 3.3 What FULL Does NOT Enable

- Complete engineering correctness (requires timing analysis tools)
- Physical validation (requires P&R tools)
- Power validation (requires power analysis)

### 3.4 Correct Scope Interpretation

```
INSUFFICIENT → FULL = "Oracle can now evaluate this construct"
                    ≠ "The SDC is correct"
                    ≠ "The model improved"
                    ≠ "Engineering correctness established"
```

---

## 4. Finding Semantics

### 4.1 Error Findings (Severity = error)

| Finding | Meaning | Correctness Implication |
|---------|---------|----------------------|
| SDC-005 | No set_input_delay — input ports unconstrained | **Real defect** — missing required constraint |
| SDC-006 | No set_output_delay — output ports unconstrained | **Real defect** — missing required constraint |
| SDC-007 | create_clock on data port | **Real defect** — invalid clock definition |

These are **independently defined rule violations** — not inferred from finding count.

### 4.2 Warning Findings (Severity = warning)

| Finding | Meaning | Correctness Implication |
|---------|---------|----------------------|
| SDC-020 | set_false_path — confirm this is intended | **Advisory** — not necessarily wrong |
| SDC-021 | Multicycle path has no -hold fix | **Advisory** — best practice |
| SDC-028 | No set_input_delay -min | **Advisory** — hold timing unchecked |
| SDC-029 | No set_output_delay -min | **Advisory** — hold timing unchecked |
| SDC-030 | No set_propagated_clock | **Advisory** — ideal clock model |

These are **advisory recommendations**, not correctness defects.

### 4.3 Info Findings (Severity = info)

These are **informational observations** — not defects or recommendations.

### 4.4 Critical Distinction

- **Errors** = correctness defects (SDC-005, SDC-006, SDC-007)
- **Warnings** = best practice advisories (SDC-020, SDC-021, SDC-028, SDC-029, SDC-030)
- **Info** = informational observations

**Finding count alone does NOT indicate correctness.** A task with 23 findings and 2 errors is less correct than a task with 8 findings and 0 errors, but a task with 23 findings and 0 errors may be perfectly valid.

---

## 5. VALID_ARTIFACT Semantics

### 5.1 Current Definition

In P057's re-evaluation, `VALID_ARTIFACT` was determined by:

```python
if new_scope in ('FULL', 'PARTIAL'):
    new_outcome = 'VALID_ARTIFACT' if error_count == 0 else 'INVALID_ARTIFACT'
```

### 5.2 What This Means

| Outcome | Meaning |
|---------|---------|
| VALID_ARTIFACT | No error-severity findings under the upgraded Oracle |
| INVALID_ARTIFACT | At least one error-severity finding under the upgraded Oracle |

### 5.3 What This Does NOT Mean

| Claim | Supported? |
|-------|-----------|
| Syntactically valid | PARTIALLY — syntax errors would be caught |
| Structurally valid | PARTIALLY — structure checked by Oracle |
| Semantically correct | PARTIALLY — semantic rules applied |
| Fully correct against benchmark | NO — benchmark requirements not fully encoded |
| Timing correct | NO — requires STA tools |

### 5.4 P057's VALID_ARTIFACT Classification

P057's classification is **PARTIALLY SUPPORTED**. The error-count-based classification is reasonable but should be explicitly stated as "no error-severity findings" rather than "valid artifact."

---

## 6. Historical Claim Audit

### 6.1 Claim: "Measurement bottleneck confirmed"

**SUPPORTED.** The scope improvement from INSUFFICIENT to FULL/PARTIAL for 25/26 results confirms that the previous measurement limitation was real.

### 6.2 Claim: "C0/C1/C2 errors now visible"

**SUPPORTED.** Under FULL scope, the Oracle detects SDC-005 and SDC-006 (missing I/O delays) as errors. These were invisible under INSUFFICIENT scope.

### 6.3 Claim: "MODEL-004 candidates validated"

**PARTIALLY SUPPORTED.** MODEL-004 candidates have fewer error findings than C0/C1/C2 candidates. However:
- Different models produce different SDC
- Missing tasks (003, 006) prevent complete comparison
- Cross-model comparison is descriptive, not causal

### 6.4 Claim: "Treatment improves correctness partially answerable"

**NOT SUPPORTED.** The comparison is between different models (MODEL-002 vs MODEL-004), not a clean treatment comparison. A causal claim requires same-model, same-task, with-vs-without-feedback under the upgraded Oracle.

### 6.5 Claim: "MODEL-004 candidates have fewer errors"

**PARTIALLY SUPPORTED as descriptive observation.** Not valid as a causal claim because:
- Different model identities
- Different candidate generation (canned vs live)
- Missing tasks create selection bias
- No controlled comparison

---

## 7. Model Comparison Validity

P057 compared MODEL-002 (canned) vs MODEL-004 (live) candidates. This comparison is:

| Aspect | Validity |
|--------|----------|
| Descriptive | VALID — different candidates have different error counts |
| Causal | INVALID — different models, different implementation modes |
| Treatment effect | INVALID — not a controlled comparison |
| Generalization | INVALID — single benchmark, single model pair |

**P057 should not have claimed "MODEL-004 candidates have fewer errors" as evidence of treatment effectiveness.** It is a descriptive observation about different model outputs.

---

## 8. Missing Data

### 8.1 BENCH2-003 and BENCH2-006

| Task | C0 | C1 | C2 canned | C2 live exploratory | MODEL-004 formal |
|------|----|----|-----------|--------------------|--------------------|
| BENCH2-003 | ✅ | ✅ | ✅ | ❌ RATE LIMIT | ❌ RATE LIMIT |
| BENCH2-006 | ✅ | ✅ | ✅ | ❌ RATE LIMIT | ❌ RATE LIMIT |

### 8.2 Missingness Mechanism

Missingness is **UNKNOWN** (could be MCAR, MAR, or MNAR). Rate limits may correlate with:
- Execution time
- Model behavior
- Provider load

**Do not assume rate-limited tasks are random.**

### 8.3 Impact

The 2/6 missing tasks prevent:
- Complete treatment comparison
- Full sample analysis
- Reliable generalization

---

## 9. Measurement Validation Status

### 9.1 Controls Tested

| Control | Expected | Actual | Status |
|---------|----------|--------|--------|
| Valid port reference | valid=True | valid=True | ✅ |
| Invalid port reference | valid=False | valid=False | ✅ |
| Valid clock reference | valid=True | valid=True | ✅ |
| Invalid clock reference | valid=False | valid=False | ✅ |
| Correct clock period | valid=True | valid=True | ✅ |
| Metadata absent | scope=INSUFFICIENT | scope=INSUFFICIENT | ✅ |
| Scope enrichment | INSUFFICIENT→FULL | INSUFFICIENT→FULL | ✅ |
| Determinism | same input → same output | verified | ✅ |

### 9.2 Controls NOT Tested

| Control | Status |
|---------|--------|
| Known correct complete SDC | NOT TESTED |
| Known incorrect period | NOT TESTED |
| Known missing required constraint | NOT TESTED (SDC-005/006 serve this role) |
| Known correct I/O delays | NOT TESTED |

### 9.3 Validation Status

**PARTIALLY VALIDATED.** The reference validation and scope enrichment are verified. The semantic rule validation (SDC-005, SDC-006, etc.) is inherited from Ṛta and was validated in P008/P006. However, the complete measurement pipeline (scope enrichment → CVR → provenance) has the CVR propagation defect.

---

## 10. Causal Readiness

### 10.1 Is the measurement system ready for a causal experiment?

**NOT READY.** Two issues must be resolved first:

1. **CVR propagation defect** — `metadata_validation` not in provenance
2. **No clean treatment comparison** — need same-model, same-task, with-vs-without-feedback

### 10.2 What Would Make It READY

1. Fix CVR propagation (one-line change in adapter.py)
2. Run a controlled MODEL-004 C2 re-execution with the fixed Oracle
3. Compare same-task, same-model, with-vs-without-feedback under FULL scope

---

## 11. RQ-4 Decision

> Does structured EvidenceArtifact feedback improve engineering correctness?

**Classification: INCONCLUSIVE**

Reasons:
1. The comparison in P057 is cross-model (MODEL-002 vs MODEL-004), not causal
2. The CVR metric is not accessible (implementation defect)
3. Missing tasks prevent complete analysis
4. A clean treatment comparison has not been conducted under the upgraded Oracle

**The measurement improvement is real (scope enrichment works), but the causal question remains unanswered.**

---

## 12. C3 Gate

**C3 REMAINS BLOCKED.**

Reasons:
1. RQ-4 is not answered
2. The measurement system has a defect (CVR propagation)
3. A clean treatment comparison under the upgraded Oracle has not been conducted
4. C3 requires reliable correctness measurement, which is not yet established

---

## 13. Recommended Next Path

```
P058 (this audit) — identified CVR propagation defect
    ↓
P059 — Fix CVR propagation (one-line change)
    ↓
P060 — Readiness verification
    ↓
Controlled MODEL-004 C2 re-execution under upgraded Oracle
    ↓
Scientific review
    ↓
RQ-4 decision
    ↓
Only then: C3 design/authorization
```

---

## 14. Files Created

| File | Content |
|------|---------|
| `research/implementation/EGER-P058-MEASUREMENT-REEVALUATION-SCIENTIFIC-AUDIT-001.md` | This audit |

---

## 15. Final Status

```
MEASUREMENT NOT YET VALIDATED
CVR IMPLEMENTATION DEFECT IDENTIFIED
SCOPE ENRICHMENT: VERIFIED WORKING
FIX REQUIRED: metadata_validation → provenance dict
C3: REMAINS BLOCKED
RQ-4: INCONCLUSIVE
```

---

## 16. Strict Stop

After P058:

STOP.

No code changes.
No Oracle changes.
No benchmark changes.
No model changes.
No treatment changes.
No new model calls.
No C2 execution.
No C3 execution.
No Ṛta changes.
No commit.
No push.
