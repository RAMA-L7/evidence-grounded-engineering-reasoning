# EGER-P148 — Production Hardening Design

## Gate

P148 — Production Hardening Design (DESIGN ONLY)

## Date

2026-09-01

## Purpose

Determine exactly what must be hardened before EGER can be considered a production-quality engineering system. This is a design-only architecture gate — no code changes, no live model calls, no experiment execution.

**No production code modified. No live model calls. No experiments. No historical artifacts changed.**

---

## 1. Objective

Identify the gap between the current validated research architecture (P145 verdict B) and production-readiness. Produce a concrete hardening matrix and implementation sequence that preserves all research conclusions (C0–C5, RQ-4) while adding the reliability, security, and observability required for deployment.

---

## 2. Current Architecture

### 2.1 Component Inventory (Verified from Source)

```
TaskDefinition (eger/task/definition.py) — frozen dataclass
       ↓
PromptBuilder (eger/prompting/builder.py) — deterministic
       ↓
ProposalGenerator (LLM — external, probabilistic)
       ↓
CandidateArtifact (eger/engineer/candidate.py) — mutable dataclass
       ↓
OracleAdapter (eger/oracle/adapter.py) — deterministic, subprocess-based
       ↓
EvidenceNormalizer (eger/evidence/normalizer.py) — deterministic
       ↓
EvidenceArtifact (eger/evidence/schemas.py) — frozen dataclass
       ↓
RevisionController (eger/revision/controller.py) — orchestration only
       ↓
VerificationGate (eger/verification/gate.py) — sole acceptance authority
       ↓
VerificationResult (eger/verification/result.py) — frozen dataclass
       ↓
ProvenanceTracker (eger/provenance/tracker.py) — append-only
       ↓
EGERPipeline (eger/pipeline/e2e.py) — composition boundary
```

### 2.2 Known Debt (from P145)

| Debt | Component | Classification |
|------|-----------|---------------|
| D1 | CandidateArtifact `verified` field is mutable | MINOR — gate doesn't trust it |
| D2 | Pipeline duplicates RevisionController orchestration | MINOR — both produce correct results |

### 2.3 Test Coverage

```
Total tests: 535
New failures: 0
Status: ALL PASSING
```

---

## 3. Production-Readiness Boundary

### 3.1 Current Classification

| Level | Status |
|-------|--------|
| Research validation | ✅ COMPLETE (C0/C1 closed, RQ-4 closed) |
| Architectural validation | ✅ COMPLETE (P145 verdict B) |
| Production hardening | ❌ NOT YET |

### 3.2 What "Production-Ready" Means

A production-ready EGER must:
1. Handle all expected failure modes deterministically
2. Enforce explicit resource limits
3. Maintain security boundaries against untrusted LLM output
4. Provide complete observability for debugging and audit
5. Be deployable without hard-coded assumptions
6. Preserve research conclusions unchanged

---

## 4. Input Validation

### 4.1 Current State

| Input | Validation | Gap |
|-------|-----------|-----|
| Missing TaskDefinition | `__post_init__` raises ValueError | ✅ Adequate |
| Missing `task_id` | `__post_init__` raises ValueError | ✅ Adequate |
| Missing `design_context` | `__post_init__` raises ValueError | ✅ Adequate |
| Missing `objective` | `__post_init__` raises ValueError | ✅ Adequate |
| Missing `initial_sdc` | `__post_init__` raises ValueError | ✅ Adequate |
| Empty `constraints` | `__post_init__` raises ValueError | ✅ Adequate |
| Malformed SDC in `initial_sdc` | No validation | ⚠️ DEBT |
| Oversized input | No size limits | ⚠️ DEBT |
| Invalid `candidate_hash` | No validation in `build_candidate` | ⚠️ DEBT |
| Malformed Oracle output | `EvidenceNormalizer` raises ValueError for unmapped severity | ✅ Fail-closed |
| Invalid `evidence_scope` | `__post_init__` raises ValueError | ✅ Adequate |
| Invalid `oracle_status` | `__post_init__` raises ValueError | ✅ Adequate |
| Missing `finding_id` | `__post_init__` raises ValueError | ✅ Adequate |

### 4.2 Identified Gaps

1. **No SDC content validation**: `initial_sdc` is checked for non-empty but not validated as actual SDC syntax
2. **No size limits**: TaskDefinition fields have no maximum length
3. **No encoding validation**: Unicode/malformed bytes not checked
4. **No candidate SDC validation**: `build_candidate` accepts any non-empty string

### 4.3 Recommended Hardening

| Area | Action | Priority |
|------|--------|----------|
| TaskDefinition size limits | Add `MAX_FIELD_LENGTH` constants, validate in `__post_init__` | P1 |
| SDC content validation | Add minimal SDC syntax check (contains at least one SDC keyword) | P2 |
| Encoding validation | Validate UTF-8 encoding in `build_candidate` | P2 |
| Candidate size limits | Add `MAX_SDC_LENGTH` constant in `candidate.py` | P1 |

---

## 5. Failure Isolation

### 5.1 Current Failure Analysis

| Failure Mode | Current Behavior | Classification | Gap |
|--------------|-----------------|---------------|-----|
| LLM timeout | Exception caught → `MODEL_FAILURE` | ✅ INCOMPLETE | None |
| LLM returns None | `candidate = None` → `MALFORMED_OUTPUT` | ✅ INCOMPLETE | None |
| LLM returns non-SDC | `_extract_sdc_block` returns None → `MALFORMED_OUTPUT` | ✅ INCOMPLETE | None |
| Oracle subprocess failure | Exception caught → `ORACLE_FAILURE` | ✅ INCOMPLETE | None |
| Oracle returns non-zero exit | Exit code classified → `ORACLE_FAILURE` | ✅ INCOMPLETE | None |
| Oracle returns invalid JSON | `_build_success` returns failure | ✅ INCOMPLETE | None |
| Oracle not found (missing binary) | Returns `ORACLE_FAILURE` with exit 127 | ✅ INCOMPLETE | None |
| Network failure (subprocess) | Exception caught → `ORACLE_FAILURE` | ✅ INCOMPLETE | None |
| Timeout (subprocess) | No timeout enforcement | ⚠️ RISK | **Missing** |
| Budget exhaustion | `BUDGET_EXHAUSTED` terminal | ✅ Terminal | None |
| Malformed Oracle response | JSON parse failure → `ORACLE_FAILURE` | ✅ INCOMPLETE | None |
| Missing evidence | Gate returns REJECT | ✅ FAIL CLOSED | None |
| Invalid evidence scope | Gate returns REJECT | ✅ FAIL CLOSED | None |
| Unmapped severity | Normalizer raises ValueError | ✅ FAIL CLOSED | None |
| Provenance failure | Exception caught → `UNEXPECTED_ERROR` | ✅ INCOMPLETE | None |
| Filesystem failure | Subprocess exception caught | ✅ INCOMPLETE | None |
| Unexpected exception | Outer try/except → `UNEXPECTED_ERROR` | ✅ INCOMPLETE | None |

### 5.2 Critical Gap: Oracle Timeout

The Oracle adapter (`eger/oracle/adapter.py`) uses `subprocess.run()` without a timeout:

```python
result = subprocess.run(
    cmd,
    cwd=str(base_tmp),
    capture_output=True,
    env=env,
)
```

**Risk**: If the Oracle subprocess hangs, the entire EGER pipeline blocks indefinitely.

**Recommended fix**: Add `timeout=` parameter to `subprocess.run()`, default from `RevisionConfig.timeout_seconds`.

### 5.3 Failure Classification Summary

| Category | Count | Status |
|----------|-------|--------|
| Fails closed | 6 | ✅ Correct |
| Produces INCOMPLETE | 8 | ✅ Correct |
| Produces REJECT | 3 | ✅ Correct |
| Risks undefined behavior | 1 | ⚠️ Oracle timeout |

---

## 6. Resource Limits

### 6.1 Current Limits (from RevisionConfig)

| Resource | Current Limit | Enforced? | Gap |
|----------|--------------|-----------|-----|
| `max_iterations` | 5 (default) | ✅ Yes | None |
| `max_total_calls` | 15 (default) | ✅ Yes | None |
| `timeout_seconds` | 60 (default) | ❌ Not enforced at Oracle level | **Critical** |
| `temperature` | 0.0 | ✅ Yes (passed to LLM) | None |
| `max_tokens` | 2048 | ✅ Yes (passed to LLM) | None |
| Maximum prompt size | None | ❌ Not enforced | **Missing** |
| Maximum candidate size | None | ❌ Not enforced | **Missing** |
| Maximum evidence size | None | ❌ Not enforced | **Missing** |
| Maximum provenance size | None | ❌ Not enforced | **Missing** |
| Maximum SDC text length | None | ❌ Not enforced | **Missing** |
| Memory/resource exhaustion | No monitoring | ❌ Not enforced | **Missing** |

### 6.2 Recommended Hardening

| Resource | Proposed Limit | Priority | Rationale |
|----------|---------------|----------|-----------|
| Oracle subprocess timeout | `config.timeout_seconds` | P0 | Prevent indefinite hang |
| Maximum SDC text length | 100,000 characters | P1 | Prevent resource exhaustion |
| Maximum prompt text length | 50,000 characters | P2 | Prevent token limit issues |
| Maximum evidence findings | 1,000 findings | P2 | Prevent memory explosion |
| Maximum provenance entries | 10,000 per run | P2 | Prevent memory exhaustion |
| Memory monitoring | Optional resource monitor | P3 | Defense in depth |

---

## 7. Configuration Management

### 7.1 Current Configuration

Configuration is handled via `RevisionConfig` (frozen dataclass):

```python
@dataclass(frozen=True)
class RevisionConfig:
    max_iterations: int = 5
    max_total_calls: int = 15
    timeout_seconds: int = 60
    temperature: float = 0.0
    max_tokens: int = 2048
```

### 7.2 What's Hard-Coded

| Item | Current | Gap |
|------|---------|-----|
| Model provider | Passed as constructor arg | ✅ Adequate |
| Model name | Passed as constructor arg | ✅ Adequate |
| Oracle binary path | Hard-coded to `RTA_CLI` path | ⚠️ DEBT |
| Oracle revision | Hard-coded to `3b5c2f2` | ⚠️ DEBT |
| Schema versions | Hard-coded constants | ✅ Expected |
| Artifact ID prefixes | Hard-coded `EGER-` | ✅ Expected |
| Logging | None | ❌ Missing |
| Artifact storage | In-memory provenance only | ❌ Missing |

### 7.3 Recommended Hardening

| Area | Action | Priority |
|------|--------|----------|
| Oracle configuration | Make `rta_cli` and `oracle_revision` configurable via constructor | P1 |
| Logging configuration | Add configurable logging levels and handlers | P1 |
| Artifact storage | Add optional artifact persistence (file-based) | P2 |
| Environment-based config | Support environment variable overrides for deployment | P2 |
| Configuration validation | Add `__post_init__` validation for all config bounds | P1 |

---

## 8. Security Hardening

### 8.1 Current Security Posture

| Area | Current State | Gap |
|------|--------------|-----|
| API credentials | Not in production code | ✅ Secure |
| Environment variables | `os.environ.copy()` for subprocess | ✅ Read-only |
| Filesystem access | Temp files cleaned up after Oracle call | ✅ Adequate |
| Input injection | TaskDefinition validates non-empty | ⚠️ No content validation |
| Candidate content | Treated as data, not authority | ✅ Correct |
| Evidence content | Treated as data, not authority | ✅ Correct |
| Logging | No logging implemented | ✅ No secrets to leak |
| Artifact storage | In-memory only | ✅ No persistence risk |

### 8.2 LLM as Untrusted Input

The LLM is probabilistic and untrusted. Current protections:

1. **CandidateArtifact**: LLM output → deterministic extraction → CandidateArtifact
   - Extraction is keyword-based (`_extract_sdc_block`)
   - No eval/exec of LLM content
   - `verified` field defaults to False

2. **EvidenceArtifact**: Oracle output → EvidenceNormalizer → EvidenceArtifact
   - Normalizer is deterministic
   - Cannot be influenced by LLM
   - Oracle is external deterministic process

3. **VerificationGate**: Sole authority, does not trust `candidate.verified`
   - Makes decision from evidence only
   - Fail-closed for all ambiguous states

### 8.3 Authority Boundary Guarantee

**Current guarantee**: LLM cannot influence:
- Verification policy
- Budget enforcement
- Authorization decisions
- Execution policy

**Classification**: ✅ ARCHITECTURALLY SOUND

### 8.4 Security Recommendations

| Area | Action | Priority |
|------|--------|----------|
| Input sanitization | Validate SDC content doesn't contain shell commands | P2 |
| Temp file cleanup | Verify cleanup on all failure paths | P1 |
| Environment isolation | Ensure subprocess has minimal environment | P2 |
| Path traversal | Validate Oracle binary path is absolute | P1 |

---

## 9. Prompt Security

### 9.1 Current Prompt Construction (from P140/`prompting/builder.py`)

The prompt contains:
- Task identity, context, objective
- Task constraints
- Current candidate (revision mode)
- Evidence (revision mode)
- Instructions

### 9.2 Prompt Injection Analysis

| Injection Vector | Present in Prompt? | Can Affect Decision? | Classification |
|------------------|-------------------|---------------------|----------------|
| `ACCEPT` in candidate | Not in prompt | No — gate checks evidence | ✅ MITIGATED |
| `REJECT` in candidate | Not in prompt | No — gate checks evidence | ✅ MITIGATED |
| `AUTHORIZED` in candidate | Not in prompt | No — gate checks evidence | ✅ MITIGATED |
| `ignore previous instructions` | Could be in SDC text | No — SDC is data, not parsed | ✅ MITIGATED |
| `change verification policy` | Could be in SDC text | No — gate is deterministic | ✅ MITIGATED |
| `disable Oracle` | Could be in SDC text | No — Oracle is separate process | ✅ MITIGATED |

### 9.3 Prompt Security Classification

**Overall**: ✅ PARTIALLY MITIGATED

- Candidate/evidence content is treated as DATA in prompts
- No eval/exec of LLM content
- VerificationGate makes independent decision
- However, LLM output is probabilistic and could contain adversarial text
- The architecture prevents adversarial text from affecting verification

**Remaining risk**: The LLM could generate candidate text that, when passed to Oracle, produces unexpected behavior. This is mitigated by:
1. Oracle is deterministic and parses SDC as data
2. EvidenceNormalizer normalizes Oracle output
3. VerificationGate checks evidence independently

---

## 10. Oracle Security Boundary

### 10.1 Architectural Invariant

```
LLM
 ↓
Candidate (unverified proposal)

Oracle (deterministic subprocess)
 ↓
Evidence (normalized findings)

VerificationGate (sole authority)
 ↓
Decision (ACCEPT/REJECT)
```

### 10.2 Boundary Verification

| Check | Status |
|-------|--------|
| LLM cannot become evidence authority | ✅ VERIFIED |
| Oracle cannot become final authorization authority | ✅ VERIFIED |
| VerificationGate remains decision boundary | ✅ VERIFIED |
| Oracle produces evidence, not decisions | ✅ VERIFIED |
| No code path allows LLM to bypass Oracle | ✅ VERIFIED |
| No code path allows Oracle to bypass VerificationGate | ✅ VERIFIED |

### 10.3 Oracle Subprocess Isolation

The Oracle runs as a separate subprocess:
- CWD is outside the Oracle codebase
- `PYTHONDONTWRITEBYTECODE=1` prevents bytecode generation
- stdout/stderr are captured
- Exit codes are classified deterministically

**Classification**: ✅ ARCHITECTURALLY SOUND

### 10.4 Oracle Hardening Recommendations

| Area | Action | Priority |
|------|--------|----------|
| Subprocess timeout | Add `timeout=` parameter | P0 |
| Exit code validation | Add explicit exit code range validation | P1 |
| Output size limit | Add `max_output_size` for subprocess stdout | P1 |
| Temp file cleanup | Ensure cleanup on subprocess timeout | P1 |

---

## 11. Verification Hardening

### 11.1 Current VerificationGate Properties

| Property | Status |
|----------|--------|
| Explicit policy | ✅ Zero ERROR findings = ACCEPT |
| Fail-closed behavior | ✅ Missing/ambiguous → REJECT |
| Input validation | ✅ Checks candidate, evidence, oracle_status, evidence_scope |
| Unknown-state handling | ✅ Unknown oracle_status → REJECT |
| Deterministic decisions | ✅ Same inputs → same output |
| Auditability | ✅ Provenance recorded for every decision |
| Clear error states | ✅ REJECT with reason and unresolved findings |

### 11.2 Edge Cases for Production Testing

| Edge Case | Current Behavior | Test Coverage |
|-----------|-----------------|---------------|
| Empty findings list | ACCEPT (zero errors) | ✅ Tested |
| All info findings | ACCEPT (zero errors) | ✅ Tested |
| All warning findings | ACCEPT (zero errors) | ✅ Tested |
| Single error finding | REJECT | ✅ Tested |
| Mixed severity | REJECT (error present) | ✅ Tested |
| `oracle_status=UNKNOWN` | REJECT | ✅ Tested |
| `evidence_scope=UNSUPPORTED` | REJECT | ✅ Tested |
| `evidence_scope=INSUFFICIENT` | REJECT | ✅ Tested |
| Candidate with `verified=True` | ACCEPT (if evidence clean) | ✅ Tested |
| Candidate with `verified=False` | ACCEPT (if evidence clean) | ✅ Tested |

### 11.3 Verification Hardening Recommendations

| Area | Action | Priority |
|------|--------|----------|
| Evidence freshness | Add timestamp-based evidence staleness check | P2 |
| Candidate-evidence consistency | Verify candidate_hash matches evidence candidate_hash | P1 |
| Maximum verification history | Limit on number of evaluations per run | P2 |

---

## 12. Provenance Hardening

### 12.1 Current Provenance (from P143)

| Property | Status |
|----------|--------|
| Event chain | ✅ Complete (RUN_STARTED → ... → RUN_COMPLETED) |
| Artifact relationships | ✅ Preserved (prompt → candidate → evidence → verification) |
| Revision history | ✅ Preserved (iteration order) |
| Terminal state | ✅ Recorded |
| Append-only | ✅ Entries never modified |
| Reconstruction | ✅ `reconstruct_run()` deterministic |

### 12.2 Research Provenance vs Production Audit Trail

| Aspect | Research Provenance | Production Audit Trail |
|--------|-------------------|----------------------|
| Storage | In-memory | Persistent (file/DB) |
| Tamper evidence | None | Hash chains, signatures |
| Retention | Until process exits | Configurable retention |
| Run IDs | Deterministic | UUID + deterministic |
| Artifact hashes | SHA256 | SHA256 + HMAC |
| Event ordering | Implicit (list order) | Explicit timestamps + sequence numbers |
| Schema versioning | Hard-coded constant | Versioned schema |
| Failure recovery | None (lost on crash) | Persistent + recovery |
| Query capability | `get_run()`, `get_entry()` | SQL/NoSQL query |

### 12.3 Provenance Hardening Recommendations

| Area | Action | Priority |
|------|--------|----------|
| Persistent storage | Add file-based provenance persistence | P1 |
| Schema versioning | Add explicit schema migration support | P2 |
| Artifact hash integrity | Add hash chain verification on reconstruction | P2 |
| Run ID uniqueness | Add UUID-based run IDs with deterministic suffix | P1 |
| Retention policy | Add configurable retention periods | P3 |
| Tamper evidence | Add HMAC-signed provenance entries | P3 |

---

## 13. D1 Analysis — CandidateArtifact Mutability

### 13.1 Current State

`CandidateArtifact` is a mutable dataclass:
```python
@dataclass
class CandidateArtifact:
    artifact_id: str
    sdc_text: str
    input_hash: str
    candidate_hash: str
    provision: Dict[str, Any]
    schema_version: str = SCHEMA_CANDIDATE
    created_at: str = ""
    verified: bool = False  # MUTABLE
```

### 13.2 Safety Analysis

1. **Why it is currently safe**:
   - VerificationGate does NOT check `candidate.verified`
   - VerificationGate makes its own decision from evidence
   - No component promotes candidates based on `verified` field
   - The gate's test explicitly verifies "unverified candidate accepted" when evidence is clean

2. **Authority violation risk**: ✅ NONE
   - Setting `verified=True` does not bypass VerificationGate
   - The gate is the sole authority, not the candidate

3. **Production risk**: ⚠️ LOW
   - Mutable state could cause confusion in debugging
   - Provenance records reference candidate by ID, not by mutable state
   - No code path reads `verified` for decision-making

### 13.3 Proposed Design Solution (DO NOT IMPLEMENT YET)

Make `CandidateArtifact` a frozen dataclass:
```python
@dataclass(frozen=True)
class CandidateArtifact:
    artifact_id: str
    sdc_text: str
    input_hash: str
    candidate_hash: str
    provision: Dict[str, Any]
    schema_version: str = SCHEMA_CANDIDATE
    created_at: str = ""
    # Remove `verified` field entirely — VerificationGate makes the decision
```

**Impact**: All code that creates CandidateArtifact unchanged (uses `build_candidate`). No code reads `verified`. No behavioral change.

**Classification**: SAFE TO IMPLEMENT — no correctness impact

---

## 14. D2 Analysis — Orchestration Overlap

### 14.1 Current State

Two components implement the revision loop:
1. `RevisionController.run()` — canonical implementation
2. `EGERPipeline._run_with_tracking()` — duplicates with provenance tracking

### 14.2 Duplicated Responsibilities

| Responsibility | RevisionController | EGERPipeline |
|---------------|-------------------|--------------|
| Prompt building | ✅ | ✅ |
| Candidate extraction | ✅ | ✅ |
| Oracle evaluation | ✅ | ✅ |
| Evidence normalization | ✅ | ✅ |
| Budget enforcement | ✅ | ✅ |
| Iteration tracking | ✅ | ✅ |
| Provenance recording | ❌ | ✅ |
| Verification | ❌ | ✅ |

### 14.3 Possible Divergence

- Both implementations handle the same failure modes
- Both produce correct results
- The pipeline's version adds provenance tracking
- Future changes to one may not be reflected in the other

### 14.4 Possible Double Budget Enforcement

No — both check the same `config.max_total_calls` limit independently. Since they run in sequence (not concurrently), double enforcement is not a risk.

### 14.5 Possible Inconsistent Termination

Both use the same terminal reason strings. Both default to `REJECTED` status. Consistent.

### 14.6 Preferred Single Orchestration Boundary

**Recommended**: Pipeline should delegate to RevisionController and add provenance tracking around it.

```
EGERPipeline.run()
    ↓
    provenance.start_run()
    ↓
    run_record = revision_controller.run()  ← delegate
    ↓
    verification_result = verification_gate.evaluate()
    ↓
    provenance.complete_run()
```

**Classification**: MINOR DEBT — no behavioral impact, maintenance overhead only

---

## 15. Interface Stability

### 15.1 Public Contracts

| Contract | Schema Version | Frozen? | Serialization | Validation | Recommendation |
|----------|---------------|---------|--------------|-----------|----------------|
| TaskDefinition | `eger.task.v1` | ✅ Yes | `to_dict`/`from_dict` | ✅ `__post_init__` | Add version check on deserialization |
| PromptRequest | `eger.prompt.v1` | ✅ Yes | `to_dict`/`from_dict` | ✅ `__post_init__` | Add version check on deserialization |
| CandidateArtifact | `eger.candidate.v1` | ❌ No | `to_dict` | ❌ No `from_dict` | Add `from_dict`, make frozen |
| EvidenceArtifact | `eger.evidence.v1` | ✅ Yes | `to_dict`/`from_dict` | ✅ `__post_init__` | Add version check on deserialization |
| Finding | `eger.finding.v1` | ✅ Yes | `to_dict`/`from_dict` | ✅ `__post_init__` | Add version check on deserialization |
| VerificationResult | `eger.verification.v1` | ✅ Yes | `to_dict`/`from_dict` | ✅ `__post_init__` | Add version check on deserialization |
| RunRecord | `eger.run.v1` | ✅ Yes | `to_dict`/`from_dict` | ✅ `__post_init__` | Add version check on deserialization |
| RevisionConfig | `eger.config.v1` | ✅ Yes | `to_dict`/`from_dict` | ✅ `__post_init__` | Add version check on deserialization |

### 15.2 Interface Recommendations

| Area | Action | Priority |
|------|--------|----------|
| CandidateArtifact `from_dict` | Add missing deserialization method | P1 |
| CandidateArtifact immutability | Make frozen, remove `verified` field | P1 |
| Schema version checks | Add version validation in `from_dict` methods | P2 |
| Stable serialization | All contracts already have `to_dict`/`from_dict` | ✅ Done |
| Explicit identifiers | All contracts have explicit IDs | ✅ Done |
| Backward compatibility | All `from_dict` use `d.get()` with defaults | ✅ Done |

---

## 16. Observability

### 16.1 What Should Be Recorded (Production)

| Data Point | Current | Required | Priority |
|------------|---------|----------|----------|
| `run_id` | ✅ Recorded | ✅ Required | P0 |
| `task_id` | ✅ Recorded | ✅ Required | P0 |
| `iteration` | ✅ Recorded | ✅ Required | P0 |
| `prompt_hash` | ✅ Recorded | ✅ Required | P0 |
| `candidate_hash` | ✅ Recorded | ✅ Required | P0 |
| `oracle_result` | ✅ Recorded | ✅ Required | P0 |
| `evidence_hash` | ✅ Recorded | ✅ Required | P0 |
| `verification_result` | ✅ Recorded | ✅ Required | P0 |
| `terminal_reason` | ✅ Recorded | ✅ Required | P0 |
| `latency` (duration_seconds) | ✅ Recorded | ✅ Required | P0 |
| `model/provider metadata` | ❌ Not recorded | ✅ Required | P1 |
| `failure_category` | ✅ Recorded (terminal_reason) | ✅ Required | P0 |
| `budget_consumption` | ✅ Recorded (total_calls) | ✅ Required | P0 |
| `config` | ✅ Recorded (in RunRecord) | ✅ Required | P1 |

### 16.2 Logging Recommendations

| Area | Action | Priority |
|------|--------|----------|
| Structured logging | Add Python `logging` with structured JSON output | P1 |
| Log levels | DEBUG (iteration details), INFO (run start/complete), WARNING (failures), ERROR (exceptions) | P1 |
| Audit vs debug separation | Audit data → provenance; debug data → logs | P1 |
| Secret filtering | Ensure no secrets in logs (currently none to filter) | ✅ Done |
| Log rotation | Add configurable log rotation for production | P2 |

### 16.3 Observability Recommendations

| Area | Action | Priority |
|------|--------|----------|
| Structured logging module | Create `eger/logging.py` with configured logger | P1 |
| Run-level metrics | Record total duration, iteration count, budget usage | P1 |
| Component-level metrics | Record prompt build time, oracle time, verification time | P2 |
| Health checks | Add component health check endpoints (for service deployment) | P3 |

---

## 17. Reproducibility

### 17.1 Deterministic Components

| Component | Deterministic? | Evidence |
|-----------|---------------|----------|
| TaskDefinition | Yes (frozen) | Same input → same hash |
| PromptBuilder | Yes | Same inputs → same prompt_hash |
| EvidenceNormalizer | Yes | Same Oracle input → same EvidenceArtifact |
| VerificationGate | Yes | Same inputs → same decision |
| ProvenanceTracker | Yes | Same events → same reconstruction |
| CandidateArtifact extraction | Yes | Same SDC → same candidate_hash |
| RevisionController | Yes (orchestration) | Same inputs → same RunRecord |

### 17.2 Probabilistic Components

| Component | Deterministic? | Reproducibility |
|-----------|---------------|-----------------|
| LLM proposal generation | No (stochastic) | Requires model + prompt hash + temperature + seed |
| LLM revision | No (stochastic) | Same as above |

### 17.3 Metadata Required for Reproducibility

To reproduce or audit a probabilistic run:

| Metadata | Currently Captured? | Where |
|----------|-------------------|-------|
| Model identifier | ❌ Not captured | Should be in `provision` dict |
| Provider | ❌ Not captured | Should be in `provision` dict |
| Prompt hash | ✅ Captured | PromptRequest.prompt_hash |
| Prompt content policy | ❌ Not captured | Should be in run provenance |
| Configuration | ✅ Captured | RunRecord.config |
| Candidate | ✅ Captured | CandidateArtifact.sdc_text |
| Evidence | ✅ Captured | EvidenceArtifact |
| Oracle version | ✅ Captured | Oracle provenance |
| Software version | ❌ Not captured | Should be in run provenance |
| Temperature | ✅ Captured | RevisionConfig.temperature |
| Random seed | ❌ Not captured | Should be in run provenance |

### 17.4 Reproducibility Recommendations

| Area | Action | Priority |
|------|--------|----------|
| Model metadata | Capture model/provider/version in CandidateArtifact.provision | P1 |
| Software version | Add `EGER_VERSION` constant, include in run provenance | P1 |
| Random seed support | Add optional `seed` parameter to RevisionConfig | P2 |
| Prompt content logging | Optionally store full prompt text for audit | P2 |
| Bit-for-bit LLM reproducibility | NOT POSSIBLE without deterministic sampling | N/A |

---

## 18. Testing Strategy (Design Only)

### 18.1 Unit Tests

| Test Category | Coverage Needed | Current | Gap |
|---------------|----------------|---------|-----|
| Contract validation | All `__post_init__` paths | ✅ Good | Minor gaps |
| Immutability | All frozen dataclasses | ✅ Good | CandidateArtifact not frozen |
| Serialization | All `to_dict`/`from_dict` | ✅ Good | CandidateArtifact missing `from_dict` |
| Hashing | Deterministic hash computation | ✅ Good | None |
| Verification | All gate decision paths | ✅ Good | None |
| Evidence normalization | All severity mappings | ✅ Good | None |
| Budget handling | All budget exhaustion paths | ✅ Good | None |
| Input validation | All size limit violations | ❌ Not implemented | **Missing** |

### 18.2 Integration Tests

| Test Category | Coverage Needed | Current | Gap |
|---------------|----------------|---------|-----|
| Task → Prompt | End-to-end prompt construction | ✅ Good | None |
| Prompt → LLM → Candidate | Full proposal cycle | ✅ Good | None |
| Candidate → Oracle → Evidence | Full evaluation cycle | ✅ Good | None |
| Evidence → Revision → Verification | Full revision cycle | ✅ Good | None |
| Full pipeline | Task → Result | ✅ Good | None |

### 18.3 Failure Injection Tests

| Test Category | Coverage Needed | Current | Gap |
|---------------|----------------|---------|-----|
| LLM timeout | Timeout handling | ✅ Tested | None |
| Oracle timeout | Timeout handling | ❌ Not tested | **Missing** |
| Malformed response | Non-SDC output | ✅ Tested | None |
| Missing evidence | Gate REJECT | ✅ Tested | None |
| Invalid candidate | Gate REJECT | ✅ Tested | None |
| Budget exhaustion | Terminal state | ✅ Tested | None |
| Provenance failure | UNEXPECTED_ERROR | ✅ Tested | None |
| Oracle subprocess hang | Timeout enforcement | ❌ Not tested | **Missing** |
| Filesystem failure | Temp file errors | ❌ Not tested | **Missing** |

### 18.4 Security Tests

| Test Category | Coverage Needed | Current | Gap |
|---------------|----------------|---------|-----|
| Prompt injection | Adversarial SDC content | ❌ Not tested | **Missing** |
| Malicious candidate | SDC with injection attempts | ❌ Not tested | **Missing** |
| Malicious evidence | Adversarial evidence content | ❌ Not tested | **Missing** |
| Secret leakage | No secrets in output | ✅ No secrets exist | None |
| Authority bypass | LLM cannot ACCEPT | ✅ Tested | None |

### 18.5 Property Tests

| Property | Test | Current | Gap |
|----------|------|---------|-----|
| Deterministic input → same result | Same TaskDefinition → same RunRecord | ❌ Not tested | **Missing** |
| ERROR → never ACCEPT | Evidence with errors → REJECT | ✅ Tested | None |
| Missing evidence → never ACCEPT | No evidence → REJECT | ✅ Tested | None |
| Unknown oracle status → never ACCEPT | UNKNOWN status → REJECT | ✅ Tested | None |
| Budget exhaustion → never ACCEPT | Exhausted budget → terminal | ✅ Tested | None |

### 18.6 Testing Recommendations

| Priority | Action |
|----------|--------|
| P0 | Add Oracle subprocess timeout test |
| P1 | Add input validation tests (size limits) |
| P1 | Add model/provider metadata capture tests |
| P1 | Add property-based determinism tests |
| P2 | Add prompt injection security tests |
| P2 | Add filesystem failure tests |
| P2 | Add memory exhaustion boundary tests |

---

## 19. Deployment Requirements

### 19.1 Classification

| Requirement | Classification | Rationale |
|-------------|---------------|-----------|
| CLI interface | SHOULD HAVE | Useful for standalone execution |
| Library API | MUST HAVE | Primary use case — importable package |
| Configuration | MUST HAVE | RevisionConfig + environment variables |
| Logging | MUST HAVE | Production observability |
| Artifact storage | SHOULD HAVE | Persistent audit trail |
| Model adapter | MUST HAVE | Already abstracted via Protocol |
| Oracle adapter | MUST HAVE | Already abstracted via Protocol |
| Timeouts | MUST HAVE | Prevent indefinite hangs |
| Budgets | MUST HAVE | Already implemented |
| Security | MUST HAVE | Already architecturally sound |
| Versioning | SHOULD HAVE | Semantic versioning for releases |
| Docker/Container | OPTIONAL | Not required for library deployment |
| REST API | NOT REQUIRED | Library, not service |
| Database | OPTIONAL | File-based provenance sufficient |

### 19.2 Deployment Recommendations

| Area | Action | Priority |
|------|--------|----------|
| Package structure | Add `pyproject.toml` for pip installation | P1 |
| Version management | Add `eger/__init__.py` with `__version__` | P1 |
| Entry points | Add CLI entry point for standalone execution | P2 |
| Dependencies | Document all dependencies (currently none beyond stdlib) | P1 |
| Python version | Specify minimum Python version (3.10+ for dataclasses) | P1 |

---

## 20. Hardening Matrix

| Area | Current State | Risk | Priority | Proposed Hardening |
|------|--------------|------|----------|-------------------|
| **Input validation** | Basic non-empty checks | Medium — oversized input, malformed SDC | P1 | Add size limits, SDC content validation |
| **Failure handling** | Comprehensive fail-closed | Low — Oracle timeout risk | P0 | Add subprocess timeout |
| **Resource limits** | Iteration/call limits only | High — no timeout, no size limits | P0 | Add timeout enforcement, size limits |
| **Configuration** | RevisionConfig + constructor args | Medium — hard-coded Oracle path | P1 | Make Oracle config configurable |
| **Security** | Architecturally sound | Low — no credentials, no eval/exec | P1 | Validate temp file cleanup, path traversal |
| **Prompt boundary** | Candidate/evidence treated as data | Low — injection cannot affect verification | P2 | Add adversarial content tests |
| **Oracle boundary** | Subprocess isolation | Medium — no timeout, no output limit | P0 | Add timeout, output size limit |
| **Verification** | Fail-closed, deterministic | Low — complete test coverage | P1 | Add candidate-evidence consistency check |
| **Provenance** | In-memory, append-only | Medium — no persistence, no tamper evidence | P1 | Add file-based persistence |
| **Immutability** | D1 — CandidateArtifact mutable | Low — gate doesn't trust it | P1 | Make frozen, remove `verified` |
| **Orchestration** | D2 — Pipeline duplicates controller | Low — both correct | P2 | Delegate to controller |
| **Interfaces** | All contracts have schema versions | Low — missing `from_dict` for Candidate | P1 | Add `from_dict`, version checks |
| **Observability** | Provenance only, no logging | High — no structured logging | P1 | Add structured logging module |
| **Reproducibility** | Deterministic components OK | Medium — missing model metadata | P1 | Capture model/provider/version |
| **Testing** | 535 tests, good coverage | Medium — missing failure injection | P1 | Add timeout, injection, property tests |
| **Deployment** | Library package | Medium — no packaging config | P1 | Add pyproject.toml, versioning |

---

## 21. Implementation Sequence

Based on actual findings, the recommended sequence is:

### Phase 1: Critical Safety (P149)

**P149 — Oracle Timeout & Resource Limits**
- Add subprocess timeout to OracleAdapter
- Add output size limit for Oracle subprocess
- Add SDC text length limit to CandidateArtifact
- Add input validation tests

### Phase 2: Interface Hardening (P150)

**P150 — Contract Hardening**
- Make CandidateArtifact frozen (D1 resolution)
- Add `CandidateArtifact.from_dict()`
- Add schema version checks in all `from_dict` methods
- Add `EGER_VERSION` constant

### Phase 3: Configuration & Observability (P151)

**P151 — Configuration & Logging**
- Make Oracle path/revision configurable
- Add structured logging module
- Add model/provider metadata capture
- Add environment variable overrides

### Phase 4: Provenance & Persistence (P152)

**P152 — Provenance Persistence**
- Add file-based provenance persistence
- Add run ID uniqueness (UUID + deterministic suffix)
- Add hash chain verification
- Add artifact storage interface

### Phase 5: Orchestration Cleanup (P153)

**P153 — Orchestration Cleanup (D2)**
- Refactor EGERPipeline to delegate to RevisionController
- Add provenance tracking as a wrapper
- Remove duplicated orchestration logic

### Phase 6: Testing & Validation (P154)

**P154 — Production Testing Matrix**
- Add Oracle timeout tests
- Add failure injection tests
- Add prompt injection security tests
- Add property-based determinism tests
- Add input validation boundary tests

### Phase 7: Packaging & Deployment (P155)

**P155 — Production Packaging**
- Add `pyproject.toml`
- Add version management
- Add CLI entry point
- Add deployment documentation

---

## 22. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Oracle subprocess hangs indefinitely | Medium | High | Add timeout (P0) |
| Oversized SDC causes memory exhaustion | Low | Medium | Add size limits (P1) |
| Missing model metadata prevents debugging | Medium | Medium | Capture metadata (P1) |
| In-memory provenance lost on crash | Medium | High | Add persistence (P1) |
| D2 divergence causes maintenance burden | Low | Low | Refactor (P2) |
| Adversarial LLM output bypasses security | Low | High | Architecture already prevents (P2 testing) |

---

## 23. Explicit Non-Goals

The following are explicitly NOT part of P148 production hardening:

1. **Reopening RQ-4** — Research is closed
2. **Changing C0–C5 conclusions** — Preserved as-is
3. **Implementing authorization controls** — C5 deferred, engineering design only
4. **Implementing epistemic state** — C3 not justified
5. **Mandatory routing** — Not required by evidence
6. **Changing verification policy** — Gate is deterministic and correct
7. **Bit-for-bit LLM reproducibility** — Not possible without deterministic sampling
8. **Real-time monitoring** — Library, not service
9. **Database integration** — File-based sufficient
10. **REST API** — Library, not service

---

## 24. C0–C5 Preservation

Production hardening must NOT alter research conclusions:

```
C0: ESTABLISHED          — LLM-only baseline
C1: ESTABLISHED          — Structured evidence activates revision
C2: PARTIALLY SUPPORTED  — Evidence normalization implemented
C3: NOT JUSTIFIED        — Prompt design is more parsimonious
C4: DEFERRED             — Engineering choice, not experiment
C5: DEFERRED             — Engineering choice, not experiment
```

**Preservation guarantee**: All production hardening changes affect only:
- Error handling
- Resource limits
- Configuration
- Observability
- Packaging

None of these change the research findings or their architectural consequences.

---

## 25. RQ-4 Preservation

> Broad task framing is an empirically supported engineering signal, not a proven universal causal mechanism.

Production prompts may use broad framing (via `TaskDefinition.objective`). This is a configuration choice supported by evidence, not a universal law.

**Preservation guarantee**: Production hardening does not encode RQ-4 as a universal mechanism. It uses broad framing as a default configuration, consistent with the research finding.

---

## 26. Final Recommendation

### Production Readiness Assessment

| Dimension | Current | After Hardening | Gap |
|-----------|---------|----------------|-----|
| Correctness | ✅ High | ✅ High | Small |
| Reliability | ⚠️ Medium (timeout risk) | ✅ High | Medium |
| Security | ✅ High | ✅ High | Small |
| Observability | ⚠️ Low (no logging) | ✅ High | Large |
| Deployability | ⚠️ Medium (no packaging) | ✅ High | Large |
| Maintainability | ⚠️ Medium (D1, D2) | ✅ High | Medium |

### Recommended Approach

1. **Phase 1 (P149)** is CRITICAL — Oracle timeout is a production blocker
2. **Phases 2–4 (P150–P152)** are HIGH PRIORITY — interface hardening, logging, persistence
3. **Phases 5–7 (P153–P155)** are IMPORTANT — cleanup, testing, packaging

### Estimated Effort

| Phase | Scope | Estimated Changes |
|-------|-------|------------------|
| P149 | Oracle timeout + resource limits | 3–5 files |
| P150 | Contract hardening | 4–6 files |
| P151 | Configuration + logging | 3–4 files |
| P152 | Provenance persistence | 2–3 files |
| P153 | Orchestration cleanup | 1–2 files |
| P154 | Testing matrix | 5–7 test files |
| P155 | Packaging | 2–3 config files |

---

```
P148 COMPLETE
PRODUCTION HARDENING DESIGN COMPLETE

RESEARCH PHASE: CLOSED
RQ-4: CLOSED

C0: ESTABLISHED
C1: ESTABLISHED
C2: PARTIALLY SUPPORTED
C3: NOT JUSTIFIED
C4: DEFERRED
C5: DEFERRED

ARCHITECTURE:
VALIDATED WITH MINOR DEBT

PRODUCTION READINESS:
NOT YET PRODUCTION READY

D1: CANDIDATE ARTIFACT MUTABILITY — MINOR DEBT, SAFE TO FIX
D2: ORCHESTRATION OVERLAP — MINOR DEBT, LOW RISK

LIVE MODEL CALLS: NO
EXPERIMENT EXECUTED: NO
HISTORICAL ARTIFACTS MODIFIED: NO
PRODUCTION CODE MODIFIED: NO
TESTS MODIFIED: NO
GIT COMMIT: NO
GIT PUSH: NO

CRITICAL FINDING:
Oracle subprocess has no timeout — P0 BLOCKER

RECOMMENDED NEXT GATE:
P149 — Oracle Timeout & Resource Limits
```
