# EGER-P157 — Provenance Persistence Necessity Assessment

## Gate

P157 — Assessment (No Implementation)

## Date

2026-09-02

## Purpose

Determine whether persistent provenance storage is necessary at this stage, or whether the current in-memory implementation is sufficient for the current EGER research/engineering stage.

**No production code modified. No live model calls. No experiments.**

---

## 1. Executive Summary

Persistent provenance storage is **not necessary at this stage**. The current in-memory `ProvenanceTracker` provides complete run-level reconstruction while the process is alive, which is sufficient for all current research workflows (single-run analysis, controlled experiments, run comparison within a session). Persistence becomes necessary only when cross-session audit trails or cross-process experiment comparison are required — conditions that have not yet been reached. Decision: **DEFER**.

---

## 2. Baseline

| Item | Value |
|------|-------|
| Current commit | `4d60047` |
| Branch | `main` |
| Tests | 734/734 PASS |
| HEAD == origin/main | YES |

### Current Provenance Architecture

```
ProvenanceTracker (in-memory, append-only)
    ↓
Pipeline.run() returns:
    - run_record (RunRecord — frozen)
    - verification_result (VerificationResult — frozen)
    - provenance (dict from reconstruct_run())
    ↓
All artifacts available for inspection within process lifetime
```

---

## 3. Current Provenance Capability

### What is captured

| Event | Data captured | Deterministic? |
|-------|--------------|---------------|
| RUN_STARTED | run_id, task_id | ✅ |
| PROMPT_CREATED | request_id, prompt_hash, iteration, task_id | ✅ |
| CANDIDATE_CREATED | candidate_id, candidate_hash, iteration, prompt_id | ✅ |
| ORACLE_EVALUATED | oracle_artifact_id, candidate_hash, iteration | ✅ |
| EVIDENCE_RECORDED | evidence_id, evidence_hash, iteration, oracle_artifact_id | ✅ |
| VERIFICATION_COMPLETED | decision, candidate_id, evidence_id | ✅ |
| RUN_COMPLETED | status, terminal_reason, final_candidate_id, final_evidence_id | ✅ |

### What RunRecord captures

| Field | Content |
|-------|---------|
| run_id | Unique run identifier |
| task_id | Task identifier |
| config | RevisionConfig (max_iterations, max_total_calls, timeout, temperature, max_tokens) |
| iterations | Tuple of dicts: iteration, prompt_hash, candidate_id, evidence_id, oracle_status, error_count |
| final_decision | Terminal reason (NO_ERRORS, BUDGET_EXHAUSTED, ORACLE_FAILURE, etc.) |
| final_evidence_id | Last evidence artifact ID |
| final_candidate_id | Last candidate artifact ID |
| total_calls | Total model + Oracle calls |
| duration_seconds | Wall-clock duration |
| status | ACCEPTED, REJECTED, or INCOMPLETE |
| provenance | Controller metadata (model_calls, oracle_calls) |

### What Pipeline.run() returns

```python
{
    "run_id": str,
    "run_record": RunRecord,           # frozen, complete
    "verification_result": VerificationResult,  # frozen, complete
    "provenance": Dict[str, Any],       # from reconstruct_run()
}
```

---

## 4. Run Reconstruction Analysis

### Can a complete run be reconstructed while the process is alive?

**YES.** The Pipeline.run() return value contains:
- Full RunRecord with all iteration data
- VerificationResult with decision, reason, and unresolved findings
- Provenance reconstruction with prompt/candidate/evidence/verification chain

### Can revision history be reconstructed?

**YES.** RunRecord.iterations contains a tuple of dicts, each with:
- iteration number
- prompt_hash
- candidate_id
- evidence_id
- oracle_status
- error_count

### Can evidence and verification results be associated with a run?

**YES.** RunRecord.final_evidence_id and VerificationResult link evidence to verification. Provenance entries link candidates to evidence to verification.

### What information disappears when the process exits?

| Information | Lost? | Actually needed? |
|-------------|-------|-----------------|
| RunRecord objects | YES | For current research: NO — results are returned to caller |
| ProvenanceTracker entries | YES | For current research: NO — reconstruction is returned |
| Candidate SDC text | YES | For current research: can be saved by caller if needed |
| Evidence findings | YES | For current research: can be saved by caller if needed |
| LLM prompt content | YES (only hash stored) | For current research: hash is sufficient for deterministic components |
| VerificationResult | YES | For current research: returned in Pipeline.run() result |

---

## 5. Persistence Gap

### What is actually lost

After process termination, the following are lost:
1. In-memory ProvenanceTracker state
2. RunRecord objects (unless caller saves them)
3. Candidate SDC text (unless caller saves it)
4. Evidence finding details (unless caller saves them)

### What is NOT lost (deterministic reconstruction possible)

Given the same inputs, the following can be deterministically reproduced:
1. PromptBuilder output (same TaskDefinition → same prompt_hash)
2. EvidenceNormalizer output (same Oracle result → same EvidenceArtifact)
3. VerificationGate decision (same candidate + evidence → same decision)
4. CandidateArtifact hash (same SDC text → same hash)

### Gap significance

The gap is: **process-lifetime data is not automatically persisted to disk.**

However, the caller receives all results via Pipeline.run()'s return value. A caller that writes those results to disk has full persistence. EGER itself does not need to own the persistence mechanism.

---

## 6. Research Necessity

### Current research claims

| Claim | Evidence source | Needs persistence? |
|-------|----------------|-------------------|
| C0: LLM-only baseline | DIAGNOSTIC-001–003 | NO — already published |
| C1: Structured evidence activates revision | DIAGNOSTIC-004–005 | NO — already published |
| C2: Evidence normalization | P139 implementation | NO — already implemented |
| C3: Not justified | DIAGNOSTIC-006–007 | NO — negative result |
| C4: Deferred | Engineering choice | NO — not yet tested |
| C5: Deferred | Engineering choice | NO — not yet tested |
| RQ-4: Broad framing signal | DIAGNOSTIC-009 | NO — already published |

### Does any current research claim require persistent provenance?

**NO.** All current research conclusions are based on experiments that have already been completed and documented in DIAGNOSTIC-* records. The provenance system supports run reconstruction during experimentation, which is sufficient.

---

## 7. Cross-Oracle Implications

### Future configuration

```
Agent → EGER → Oracle A
Agent → EGER → Oracle B
```

### Does cross-Oracle comparison require persistent provenance?

**NO — not at the research level.** Each run returns complete results via Pipeline.run(). A research script that runs both Oracle A and Oracle B can:

1. Capture both Pipeline.run() results
2. Compare run_records, verification_results, and provenance dicts
3. Write comparison results to disk

The comparison is done by the research harness, not by EGER's provenance system. EGER's role is to produce deterministic, auditable results for each run — which it already does.

### When would persistence become necessary?

When runs need to be compared across:
- Different process invocations (e.g., "show me all Oracle-A runs from last week")
- Different machines
- Longitudinal studies over time

These are production/deployment requirements, not current research requirements.

---

## 8. Cross-Agent Implications

### Future configuration

```
Agent X → EGER → Oracle
Agent Y → EGER → Oracle
```

### Does cross-agent comparison require persistent provenance?

**NO — not at the research level.** Each agent's run returns complete results. A comparison script can:

1. Run Agent X through EGER → capture results
2. Run Agent Y through EGER → capture results
3. Compare deterministically

The comparison is external to EGER. EGER produces identical infrastructure for both agents.

---

## 9. Research vs Production Separation

| Requirement | Classification | Status |
|-------------|---------------|--------|
| Run reconstruction during experiment | Research | ✅ SUFFICIENT |
| Run comparison within session | Research | ✅ SUFFICIENT |
| Deterministic reproducibility | Research | ✅ SUFFICIENT (deterministic components) |
| Cross-session audit trail | Production | DEFERRED |
| Process-independent persistence | Production | DEFERRED |
| Longitudinal run comparison | Production | DEFERRED |
| External evaluator access | Production | DEFERRED |
| Deployment audit compliance | Production | DEFERRED |

---

## 10. Decision

### **DEFER**

Persistent provenance storage is valuable but not currently necessary. The current in-memory implementation provides complete run-level reconstruction that satisfies all current research workflows.

---

## 11. Trigger Conditions

Persistence should be reconsidered when ANY of the following conditions are met:

| Trigger | Category | Description |
|---------|----------|-------------|
| Multi-session experiment comparison | Research | Need to compare runs across different process invocations |
| Cross-Oracle replication study | Research | Need to compare Oracle-A vs Oracle-B runs across sessions |
| Cross-agent replication study | Research | Need to compare Agent-X vs Agent-Y runs across sessions |
| External evaluator requirement | Production | Third party requires process-independent audit trail |
| Deployment audit compliance | Production | Regulatory or organizational requirement for persistent logs |
| Longitudinal stability study | Research | Need to track run quality over time across sessions |

---

## 12. Minimal Future Design

When persistence is eventually needed, the minimum design should satisfy:

### What to persist

| Artifact | Format | Rationale |
|----------|--------|-----------|
| RunRecord | JSON (to_dict) | Complete run metadata |
| VerificationResult | JSON (to_dict) | Decision and reasoning |
| ProvenanceTracker | JSON (to_dict) | Full event chain |
| TaskDefinition | JSON (to_dict) | Input specification |
| CandidateArtifact(s) | JSON (to_dict) | SDC proposals |
| EvidenceArtifact(s) | JSON (to_dict) | Oracle findings |

### What NOT to persist

| Artifact | Rationale |
|----------|-----------|
| LLM prompt text | Only hash needed; prompt is deterministic from inputs |
| Raw Oracle stdout | Already captured in evidence_hash |
| Process state | Internal to EGER |

### Storage mechanism

- File-based JSON (one directory per run)
- No database dependency
- No external service dependency
- Deterministic file paths from run_id

---

## 13. Security Considerations

| Concern | Current status | Future consideration |
|---------|---------------|---------------------|
| Sensitive prompts | Not stored (only hash) | ✅ Safe |
| Candidate SDC | In-memory only | Future: persist as JSON |
| Oracle output | In-memory only | Future: persist as JSON |
| Log secrets | Redacted by EgerLogger | ✅ Safe |
| Filesystem permissions | N/A (no persistence) | Future: use restrictive permissions |
| Retention | N/A | Future: configurable retention |

---

## 14. Conclusion

P157 establishes that provenance persistence is:

- **Not necessary now** for research validity, reproducibility, or auditability
- **Useful but deferred** for production deployment and cross-session research
- **Sufficient in current form** for all active research workflows

The current in-memory ProvenanceTracker provides complete run reconstruction during process lifetime, which is all that the current research program requires.

---

```
P157 COMPLETE

PROVENANCE INSPECTION: PASS
RUN RECONSTRUCTION: SUFFICIENT (in-memory, process-lifetime)
PERSISTENCE GAP: MINOR (process-lifetime data not auto-persisted)

RESEARCH NECESSITY: NOT REQUIRED
PRODUCTION NECESSITY: DEFERRED
CROSS-ORACLE IMPLICATION: NOT REQUIRED (research-level comparison possible via caller)
CROSS-AGENT IMPLICATION: NOT REQUIRED (research-level comparison possible via caller)

DECISION: DEFER

IMPLEMENTATION CHANGES: NONE
TESTS: 734/734 PASS

ṚTA CHANGES: NONE
HISTORICAL RESEARCH CHANGES: NONE
RESEARCH STATE CHANGES: NONE
```
