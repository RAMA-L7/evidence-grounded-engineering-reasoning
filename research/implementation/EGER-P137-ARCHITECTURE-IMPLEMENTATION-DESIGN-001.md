# EGER-P137 — EGER Architecture Implementation Design

## Phase
P137 — Design-Only Architecture Gate

## Date
2026-09-01

## Status
**ARCHITECTURE IMPLEMENTATION DESIGN COMPLETE**

---

## 1. Executive Summary

This document translates P136 (Evidence-to-Architecture Synthesis) into a concrete implementation blueprint for EGER. The architecture is designed around **what the evidence actually supports**: structured evidence feedback, broader task framing, deterministic verification, and authority separation.

The design preserves the existing `eger/` module structure where possible and introduces new components where the evidence requires them. Every component is classified as **EMPIRICALLY SUPPORTED**, **ENGINEERING DESIGN CHOICE**, or **FUTURE HYPOTHESIS**.

**No production code is written in P137.** This is a design gate.

---

## 2. Evidence Boundary

| Finding | Classification | Source |
|---------|---------------|--------|
| Structured evidence causes revision | **ESTABLISHED** | C1/C2 |
| ERROR adherence is task-dependent | **ESTABLISHED** | P090–P131 |
| Broader framing improves adherence | **STRONG SIGNAL** | DIAGNOSTIC-009 A1 |
| Technical content improves adherence | **SUPPORTED SIGNAL** | DIAGNOSTIC-009 A2 |
| Deterministic verification is authoritative | **ESTABLISHED** | P1/P4 principles |
| Authority separation is necessary | **ESTABLISHED** | P7 principle |
| Causality of framing | NOT ESTABLISHED | — |
| Generalization beyond MODEL-005 | NOT ESTABLISHED | — |
| C3 epistemic-state intervention | NOT JUSTIFIED | — |

---

## 3. Architecture Principles

| Principle | Source | Architecture Implication |
|-----------|--------|------------------------|
| P1: No Unverified State Transition | Contract v0.2 | Verification gate required |
| P3: Evidence-Conditioned Reasoning | Contract v0.2 | Routing table maps findings to procedures |
| P4: Executable Engineering Checklist | Contract v0.2 | Oracle provides executable checks |
| P7: Authority Separation | Contract v0.2 | LLM proposes; Oracle verifies; System decides |
| Broad framing signal | RQ-4/DIAGNOSTIC-009 | Task definition uses production-quality framing |

---

## 4. Minimal Evidence-Grounded Architecture

Only components justified by current evidence:

```
┌─────────────────────────────────────────────────────────┐
│                    eger/task/                             │
│  TaskDefinition                                          │
│  - task_id, design_context, objective                    │
│  - broad_objective_template (from RQ-4)                  │
│  EMPIRICALLY SUPPORTED (framing signal)                  │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    eger/prompting/                        │
│  PromptBuilder                                           │
│  - Constructs LLM prompt from TaskDefinition             │
│  - Applies broad framing template                        │
│  - Separates objective from evidence                     │
│  EMPIRICALLY SUPPORTED (framing signal)                  │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    eger/engineer/                         │
│  ProposalGenerator (existing: adapter.py, model.py)      │
│  - Single probabilistic component                       │
│  - Generates CandidateArtifact                          │
│  - PROPOSAL AUTHORITY ONLY                               │
│  EMPIRICALLY SUPPORTED (100% activation)                 │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    eger/oracle/                           │
│  OracleAdapter (existing: adapter.py, schemas.py)        │
│  - Deterministic verification                           │
│  - Produces EvidenceArtifact                            │
│  - EVIDENCE AUTHORITY                                    │
│  EMPIRICALLY SUPPORTED (P1/P4 principles)                │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    eger/evidence/                         │
│  EvidenceNormalizer (NEW)                                │
│  - Raw oracle result → normalized findings               │
│  - Severity classification                              │
│  - Scope assignment                                     │
│  - Deterministic transformation                         │
│  EMPIRICALLY SUPPORTED (structured feedback)             │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    eger/revision/                         │
│  RevisionController (NEW)                                │
│  - Controls generate→verify→revise loop                  │
│  - Budget enforcement                                   │
│  - Termination conditions                               │
│  - Checkpoint/resume                                    │
│  EMPIRICALLY SUPPORTED (C1 revision behavior)            │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    eger/verification/                     │
│  VerificationGate (NEW)                                  │
│  - Deterministic acceptance criteria                    │
│  - All ERROR findings resolved?                         │
│  - AUTHORIZATION AUTHORITY                               │
│  ENGINEERING DESIGN CHOICE (P1 principle)                │
└───────────────────────┬─────────────────────────────────┘
                        ↓
                ACCEPT / REJECT
```

---

## 5. Extended EGER Architecture

Includes optional components not experimentally validated:

```
MINIMAL ARCHITECTURE (above)
        +
┌─────────────────────────────────────────────────────────┐
│                    eger/routing/ (OPTIONAL)               │
│  EvidenceRouter (C4-style)                               │
│  - Deterministic routing table                           │
│  - Maps finding codes to procedures                      │
│  ENGINEERING DESIGN CHOICE — not experimentally tested   │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    eger/policy/ (OPTIONAL)                │
│  PolicyEngine (C5-style)                                 │
│  - Non-bypassable authorization rules                   │
│  - State transition enforcement                         │
│  ENGINEERING DESIGN CHOICE — not experimentally tested   │
└───────────────────────┬─────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    eger/epistemic/ (EXCLUDED)             │
│  EpistemicState (C3-style)                               │
│  - Explicit validated/refuted/unknown states             │
│  NOT INCLUDED — C3 NOT JUSTIFIED                         │
│  INTERFACE POINT: could be inserted here if justified    │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Component Specifications

### 6.1 TaskDefinition (`eger/task/`)

**Responsibility:** Define the engineering task with broad, production-quality framing.

**Inputs:** Task ID, design context, engineering constraints.

**Outputs:** `TaskDefinition` object.

**Authority:** READ-ONLY configuration. No runtime modification.

**Failure modes:** Missing required fields → reject at construction.

**Interface:**
```python
@dataclass
class TaskDefinition:
    task_id: str
    design_context: str
    objective: str  # broad, production-quality framing
    initial_sdc: str
    constraints: List[str]  # task-specific engineering constraints
    schema_version: str = "eger.task.v1"
```

**Classification:** EMPIRICALLY SUPPORTED (framing signal).

### 6.2 PromptBuilder (`eger/prompting/`)

**Responsibility:** Construct LLM prompt from TaskDefinition and evidence.

**Inputs:** `TaskDefinition`, `EvidenceArtifact` (optional, for revision).

**Outputs:** Prompt string.

**Authority:** PRESENTATION ONLY. No interpretation.

**Failure modes:** Missing objective → use default broad template.

**Interface:**
```python
class PromptBuilder:
    def build_initial(self, task: TaskDefinition) -> str:
        """Build initial prompt with broad framing."""
        
    def build_revision(self, task: TaskDefinition, evidence: EvidenceArtifact) -> str:
        """Build revision prompt with structured evidence."""
```

**Classification:** EMPIRICALLY SUPPORTED (framing signal).

### 6.3 ProposalGenerator (`eger/engineer/`)

**Responsibility:** Generate candidate SDC from LLM.

**Inputs:** Prompt string.

**Outputs:** `CandidateArtifact`.

**Authority:** PROPOSAL ONLY. Cannot verify, authorize, or modify evidence.

**Existing implementation:** `eger/engineer/adapter.py`, `eger/engineer/model.py`, `eger/engineer/candidate.py`.

**Failure modes:** Timeout → INCOMPLETE. Empty output → INCOMPLETE. Malformed → INCOMPLETE.

**Classification:** EMPIRICALLY SUPPORTED (100% activation).

### 6.4 OracleAdapter (`eger/oracle/`)

**Responsibility:** Deterministic verification of SDC proposals.

**Inputs:** `CandidateArtifact` + `TaskDefinition`.

**Outputs:** `OracleResult` (raw findings).

**Authority:** EVIDENCE AUTHORITY. Cannot generate proposals.

**Existing implementation:** `eger/oracle/adapter.py`, `eger/oracle/schemas.py`.

**Failure modes:** Oracle unavailable → ORACLE_FAILURE. Invalid input → INVALID_REQUEST.

**Classification:** EMPIRICALLY SUPPORTED (P1/P4 principles).

### 6.5 EvidenceNormalizer (`eger/evidence/`)

**Responsibility:** Transform raw oracle results into normalized evidence.

**Inputs:** `OracleResult`.

**Outputs:** `EvidenceArtifact`.

**Authority:** PRESENTATION ONLY. No interpretation or authorization.

**Failure modes:** Malformed oracle output → INCOMPLETE_MEASUREMENT.

**Interface:**
```python
@dataclass
class Finding:
    finding_id: str
    severity: str  # "error" | "warning" | "info"
    category: str
    entity: str  # object/port/constraint affected
    message: str
    source: str  # oracle rule that produced this
    expected_state: str
    observed_state: str
    remediation_hint: str
    provenance: Dict[str, Any]

@dataclass
class EvidenceArtifact:
    evidence_id: str
    task_id: str
    oracle_status: str
    evidence_scope: str
    findings: List[Finding]
    summary: Dict[str, int]  # error_count, warning_count, info_count
    analysis_scope: Dict[str, Any]
    schema_version: str = "eger.evidence.v1"
    created_at: str = ""
```

**Classification:** EMPIRICALLY SUPPORTED (structured feedback).

### 6.6 RevisionController (`eger/revision/`)

**Responsibility:** Control the generate→verify→revise loop.

**Inputs:** `TaskDefinition`, `ProposalGenerator`, `OracleAdapter`, `EvidenceNormalizer`.

**Outputs:** `RunRecord` with full provenance.

**Authority:** FLOW CONTROL only. Cannot generate proposals, verify, or authorize.

**Failure modes:** Budget exceeded → REJECT. Provider failure → INCOMPLETE. Max iterations → REJECT.

**Interface:**
```python
@dataclass
class RevisionConfig:
    max_iterations: int = 5
    max_total_calls: int = 15
    timeout_seconds: int = 60
    temperature: float = 0.0
    max_tokens: int = 2048

class RevisionController:
    def __init__(self, config: RevisionConfig):
        self.config = config
        
    def execute(self, task: TaskDefinition) -> RunRecord:
        """Execute the revision loop."""
        
    def _check_termination(self, evidence: EvidenceArtifact, iteration: int) -> str:
        """Return: 'continue' | 'accept' | 'reject'"""
```

**Classification:** EMPIRICALLY SUPPORTED (C1 revision behavior).

### 6.7 VerificationGate (`eger/verification/`)

**Responsibility:** Deterministic acceptance/rejection of final proposal.

**Inputs:** `EvidenceArtifact`, `CandidateArtifact`, `RunRecord`.

**Outputs:** `VerificationResult`.

**Authority:** AUTHORIZATION AUTHORITY. Final decision.

**Failure modes:** Ambiguous evidence → REJECT (fail closed).

**Interface:**
```python
@dataclass
class VerificationResult:
    decision: str  # "ACCEPT" | "REJECT"
    reason: str
    error_count: int
    unresolved_findings: List[str]
    provenance: Dict[str, Any]
    schema_version: str = "eger.verification.v1"

class VerificationGate:
    def verify(self, evidence: EvidenceArtifact, 
               candidate: CandidateArtifact) -> VerificationResult:
        """Deterministic verification. No LLM. No probabilistic component."""
```

**Classification:** ENGINEERING DESIGN CHOICE (P1 principle).

---

## 7. Authority Model

```
┌─────────────────────────────────────────────────────────┐
│                 AUTHORITY HIERARCHY                       │
│                                                          │
│  PROPOSAL          EVIDENCE          AUTHORIZATION        │
│  (LLM only)        (Oracle only)     (Gate only)         │
│                                                          │
│  • Generate SDC    • Execute checks  • Accept proposal   │
│  • Revise SDC      • Produce findings • Reject proposal  │
│                    • Normalize evidence                   │
│                                                          │
│  CANNOT:           CANNOT:           CANNOT:             │
│  • Verify output   • Generate SDC    • Generate SDC      │
│  • Authorize       • Authorize       • Verify output     │
│  • Modify evidence • Modify SDC      • Modify evidence   │
│                                                          │
│  CORE INVARIANT:                                          │
│  NO PROBABILISTIC COMPONENT CAN PROMOTE A                │
│  PROPOSITION INTO VERIFIED ENGINEERING STATE             │
│  BY ITSELF.                                              │
└─────────────────────────────────────────────────────────┘
```

---

## 8. Evidence Contract

### Raw Oracle Result → Normalized Evidence → Model-Facing Feedback

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  RAW ORACLE      │     │  NORMALIZED      │     │  MODEL-FACING    │
│  RESULT          │ →   │  EVIDENCE        │ →   │  FEEDBACK        │
│                  │     │                  │     │                  │
│  - findings[]    │     │  - Finding[]     │     │  - Text render   │
│  - scope         │     │  - severity      │     │  - Structured    │
│  - status        │     │  - category      │     │    evidence      │
│                  │     │  - entity        │     │                  │
│  AUTHORITATIVE   │     │  - message       │     │  PRESENTATION    │
│  SOURCE          │     │  - expected      │     │  ONLY            │
│                  │     │  - observed      │     │                  │
│                  │     │  - remediation   │     │  NOT             │
│                  │     │  - provenance    │     │  AUTHORITATIVE   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

### Finding Schema

```json
{
  "finding_id": "F-001",
  "severity": "error",
  "category": "missing_constraint",
  "entity": "port data_in[7:0]",
  "message": "No input delay constraint found for port data_in",
  "source": "SDC-NNN",
  "expected_state": "set_input_delay defined for data_in",
  "observed_state": "No set_input_delay found",
  "remediation_hint": "Add set_input_delay constraint for data_in",
  "provenance": {
    "oracle_version": "1.5.11",
    "oracle_commit": "3b5c2f2",
    "evaluation_timestamp": "2026-09-01T00:00:00Z"
  }
}
```

---

## 9. Revision Loop Design

```
┌─────────────────────────────────────────────────────────┐
│              REVISION LOOP STATE MACHINE                  │
│                                                          │
│  INITIAL                                                 │
│    │                                                     │
│    ↓                                                     │
│  GENERATE (LLM)                                          │
│    │                                                     │
│    ↓                                                     │
│  VERIFY (Oracle)                                         │
│    │                                                     │
│    ↓                                                     │
│  EVALUATE findings                                       │
│    │                                                     │
│    ├── ERROR count == 0 ──→ ACCEPT                       │
│    │                                                     │
│    ├── iteration >= max ──→ REJECT                       │
│    │                                                     │
│    ├── calls >= budget ──→ REJECT                        │
│    │                                                     │
│    ├── provider fail ──→ INCOMPLETE                      │
│    │                                                     │
│    └── ERROR count > 0 ──→ REVISE (LLM)                 │
│           │                                             │
│           ↓                                             │
│         VERIFY (Oracle)                                 │
│           │                                             │
│           ↓                                             │
│         EVALUATE findings                               │
│           │                                             │
│           └── (loop)                                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Termination Conditions

| Condition | Action | Classification |
|-----------|--------|---------------|
| All ERROR findings resolved | ACCEPT | Deterministic |
| Max iterations reached | REJECT | Deterministic |
| Call budget exhausted | REJECT | Deterministic |
| Provider timeout | INCOMPLETE | Recorded, no retry |
| Empty model output | INCOMPLETE | Recorded, no retry |
| Oracle failure | INCOMPLETE_MEASUREMENT | Recorded, no retry |
| Unchanged proposal | REJECT | Deterministic |
| Malformed proposal | INCOMPLETE | Recorded, no retry |

---

## 10. Deterministic Boundary

```
┌─────────────────────────────────────────────────────────┐
│              NONDETERMINISM BOUNDARY                      │
│                                                          │
│  PROBABILISTIC:                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ LLM proposal generation                            │ │
│  │ (temperature, provider, model version)              │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ═══════════════════════════════════════════════════════ │
│                                                          │
│  DETERMINISTIC:                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ SDC parsing / extraction                           │ │
│  │ Oracle evaluation                                  │ │
│  │ Evidence normalization                             │ │
│  │ Prompt construction                                │ │
│  │ Revision loop control                              │ │
│  │ Verification gate                                  │ │
│  │ Policy checks                                      │ │
│  │ Audit logging                                      │ │
│  │ Provenance recording                               │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  INVARIANT:                                              │
│  Every component below the boundary line must produce    │
│  identical output for identical input, always.           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 11. Prompt Construction

### Broad Framing Template (from RQ-4)

```python
BROAD_OBJECTIVE_TEMPLATE = (
    "Generate a complete, production-quality SDC for this design. "
    "Include all required timing constraints: clock definitions, "
    "input/output delays, and any applicable exceptions."
)
```

### Task-Specific Information

```python
TASK_PROMPT_TEMPLATE = """
Task: {task_id}

Design Context:
{design_context}

Objective:
{objective}

{evidence_section}

Generate the complete SDC.
"""
```

### Revision Prompt

```python
REVISION_PROMPT_TEMPLATE = """
Task: {task_id}

Design Context:
{design_context}

Objective:
{objective}

Previous SDC:
{previous_sdc}

Oracle Findings:
{findings_text}

Please revise the SDC to address the above findings.
"""
```

**Classification:** EMPIRICALLY SUPPORTED (framing signal). The broad objective template is the default because A1 = 24/24 = 100% in DIAGNOSTIC-009.

**Caveat:** This is a strong behavioral signal, not proven causality. The effect may be model-specific.

---

## 12. Provenance Model

```
┌─────────────────────────────────────────────────────────┐
│              PROVENANCE CHAIN                             │
│                                                          │
│  TaskDefinition                                          │
│    │  task_id, design_context, objective                 │
│    ↓                                                     │
│  PromptRequest                                           │
│    │  prompt_hash, objective_hash                        │
│    ↓                                                     │
│  ModelRequest                                            │
│    │  model_id, temperature, timeout                     │
│    ↓                                                     │
│  ModelResponse                                           │
│    │  raw_output, output_hash, duration                  │
│    ↓                                                     │
│  CandidateArtifact                                       │
│    │  artifact_id, sdc_hash, input_hash                  │
│    ↓                                                     │
│  OracleInvocation                                        │
│    │  oracle_version, oracle_commit                      │
│    ↓                                                     │
│  OracleResult                                            │
│    │  findings_hash, scope, status                       │
│    ↓                                                     │
│  EvidenceArtifact                                        │
│    │  evidence_id, findings[], summary                   │
│    ↓                                                     │
│  RevisionRequest                                         │
│    │  iteration, previous_evidence_id                    │
│    ↓                                                     │
│  ... (loop) ...                                          │
│    ↓                                                     │
│  VerificationResult                                      │
│    │  decision, reason, provenance                       │
│    ↓                                                     │
│  RunRecord                                               │
│    │  complete provenance chain                          │
│    ↓                                                     │
│  PERSISTED TO DISK                                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### What Must Be Persisted

| Artifact | Persistence | Format |
|----------|-------------|--------|
| TaskDefinition | Per-run | JSON |
| PromptRequest | Per-run | JSON (hash only) |
| ModelRequest | Per-run | JSON |
| ModelResponse | Per-run | JSON (raw output) |
| CandidateArtifact | Per-run | JSON |
| OracleResult | Per-run | JSON |
| EvidenceArtifact | Per-run | JSON |
| VerificationResult | Per-run | JSON |
| RunRecord | Per-run | JSON (complete chain) |
| Checkpoint | Per-experiment | JSON (resume state) |

---

## 13. Failure and Safety Model

### Model Failure

| Failure | Detection | Response | Classification |
|---------|-----------|----------|---------------|
| Timeout | exit code / elapsed time | INCOMPLETE, no retry | Deterministic |
| Empty output | len(response) == 0 | INCOMPLETE, no retry | Deterministic |
| Malformed SDC | extract_candidate returns None | INCOMPLETE, no retry | Deterministic |
| Provider error | HTTP status / exit code | INCOMPLETE, no retry | Deterministic |

### Oracle Failure

| Failure | Detection | Response | Classification |
|---------|-----------|----------|---------------|
| Parser failure | exit code != 0 | INCOMPLETE_MEASUREMENT | Deterministic |
| Tool unavailable | FileNotFoundError | INCOMPLETE_MEASUREMENT | Deterministic |
| Invalid input | stderr content | INCOMPLETE_MEASUREMENT | Deterministic |

### Evidence Failure

| Failure | Detection | Response | Classification |
|---------|-----------|----------|---------------|
| Missing findings | findings == [] | Treat as no errors found | Deterministic |
| Inconsistent evidence | schema validation | INCOMPLETE_MEASUREMENT | Deterministic |
| Malformed schema | JSON parse error | INCOMPLETE_MEASUREMENT | Deterministic |

### Revision Failure

| Failure | Detection | Response | Classification |
|---------|-----------|----------|---------------|
| Unchanged proposal | sdc_hash unchanged | REJECT | Deterministic |
| Repeated failure | same ERROR across iterations | REJECT after max | Deterministic |
| Regression | ERROR count increases | REJECT | Deterministic |

### Fail-Closed Rule

**Where correctness cannot be established, the system rejects.**

```
Acceptance requires:
  - All ERROR findings resolved
  - No unresolved warnings that could affect correctness
  - Complete provenance chain
  - Deterministic verification passed

If any condition is ambiguous → REJECT
```

---

## 14. C3/C4/C5 Treatment

### C3 — Epistemic State

```text
STATUS: NOT JUSTIFIED
INCLUDED IN ARCHITECTURE: NO
INTERFACE POINT: eger/epistemic/ (existing, not used in core flow)
```

The existing `eger/epistemic/state.py` and `eger/epistemic/transitions.py` remain in the repository but are NOT part of the core architecture flow. They could be activated if future evidence justifies C3.

**Extension point:** If C3 is ever justified, the interface would be:

```python
# FUTURE HYPOTHESIS — NOT CURRENTLY USED
class EpistemicState:
    def update(self, evidence: EvidenceArtifact) -> None:
        """Update epistemic state based on evidence."""
    
    def get_state(self, claim_id: str) -> str:
        """Return: HYPOTHESIS | VALIDATED | REFUTED | UNKNOWN | AMBIGUOUS"""
```

### C4 — Evidence-Conditioned Routing

```text
STATUS: DEFERRED
INCLUDED IN ARCHITECTURE: OPTIONAL
MODULE: eger/routing/ (NEW, optional)
```

**Extension point:** If routing is desired, the interface would be:

```python
# ENGINEERING DESIGN CHOICE — NOT EXPERIMENTALLY TESTED
class EvidenceRouter:
    def route(self, finding: Finding) -> str:
        """Return procedure name for this finding type."""
        
    ROUTING_TABLE = {
        "missing_input_delay": "revision_with_specific_guidance",
        "missing_output_delay": "revision_with_specific_guidance",
        "missing_generated_clock": "revision_with_specific_guidance",
        "unknown_finding": "log_and_escalate",
    }
```

### C5 — Authorization Gate

```text
STATUS: DEFERRED
INCLUDED IN ARCHITECTURE: OPTIONAL
MODULE: eger/verification/ (contains gate logic)
```

The verification gate (Section 6.7) implements C5-style authorization as an engineering design choice. It is NOT experimentally validated but is included because P1 (No Unverified State Transition) requires it.

---

## 15. Repository/Module Structure

```
eger/
├── __init__.py
├── task/                    # NEW — Task definition
│   ├── __init__.py
│   └── definition.py        # TaskDefinition dataclass
├── prompting/               # NEW — Prompt construction
│   ├── __init__.py
│   └── builder.py           # PromptBuilder
├── engineer/                # EXISTING — LLM proposal
│   ├── __init__.py
│   ├── adapter.py           # EngineerAdapter (existing)
│   ├── model.py             # FakeEngineerModel (existing)
│   ├── candidate.py         # CandidateArtifact (existing)
│   ├── feedback.py          # Text feedback renderer (existing)
│   └── structured_feedback.py  # Structured feedback (existing)
├── oracle/                  # EXISTING — Deterministic verification
│   ├── __init__.py
│   ├── adapter.py           # OracleAdapter (existing)
│   ├── schemas.py           # Evidence schemas (existing)
│   └── re_evaluate.py       # Re-evaluation (existing)
├── evidence/                # NEW — Evidence normalization
│   ├── __init__.py
│   └── normalizer.py        # EvidenceNormalizer
├── revision/                # NEW — Revision loop control
│   ├── __init__.py
│   └── controller.py        # RevisionController
├── verification/            # NEW — Verification gate
│   ├── __init__.py
│   └── gate.py              # VerificationGate
├── routing/                 # OPTIONAL — Evidence-conditioned routing
│   ├── __init__.py
│   └── router.py            # EvidenceRouter (C4-style)
├── policy/                  # OPTIONAL — Policy enforcement
│   ├── __init__.py
│   └── engine.py            # PolicyEngine (C5-style)
├── epistemic/               # EXISTING — NOT USED in core flow
│   ├── __init__.py
│   ├── state.py             # EpistemicState (existing, deferred)
│   └── transitions.py       # Transitions (existing, deferred)
├── authorization/           # EXISTING — NOT USED in core flow
│   ├── __init__.py
│   └── gate.py              # AuthorizationGate (existing, deferred)
└── provenance/              # NEW — Provenance tracking
    ├── __init__.py
    └── tracker.py           # ProvenanceTracker
```

### New Modules

| Module | Purpose | Classification |
|--------|---------|---------------|
| `eger/task/` | Task definition | EMPIRICALLY SUPPORTED |
| `eger/prompting/` | Prompt construction | EMPIRICALLY SUPPORTED |
| `eger/evidence/` | Evidence normalization | EMPIRICALLY SUPPORTED |
| `eger/revision/` | Revision loop control | EMPIRICALLY SUPPORTED |
| `eger/verification/` | Verification gate | ENGINEERING DESIGN CHOICE |
| `eger/provenance/` | Provenance tracking | ENGINEERING DESIGN CHOICE |

### Existing Modules (Reused)

| Module | Purpose | Status |
|--------|---------|--------|
| `eger/engineer/` | LLM proposal generation | REUSED |
| `eger/oracle/` | Deterministic verification | REUSED |
| `eger/epistemic/` | Epistemic state | DEFERRED (not used) |
| `eger/authorization/` | Authorization gate | DEFERRED (not used) |

---

## 16. Interface Contracts

### TaskDefinition

```python
@dataclass
class TaskDefinition:
    task_id: str                    # REQUIRED
    design_context: str             # REQUIRED
    objective: str                  # REQUIRED — broad framing
    initial_sdc: str                # REQUIRED
    constraints: List[str]          # REQUIRED
    schema_version: str = "eger.task.v1"
    
    # INVARIANT: objective must use broad/production-quality framing
    # INVARIANT: initial_sdc must be non-empty
    # PRODUCER: Configuration / benchmark
    # CONSUMER: PromptBuilder
    # AUTHORITY: READ-ONLY
```

### PromptRequest

```python
@dataclass
class PromptRequest:
    request_id: str
    task_id: str
    prompt_hash: str                # SHA256 of prompt text
    objective_hash: str             # SHA256 of objective
    iteration: int
    evidence_id: Optional[str]      # None for initial
    schema_version: str = "eger.prompt.v1"
    
    # INVARIANT: prompt_hash is deterministic
    # PRODUCER: PromptBuilder
    # CONSUMER: ProposalGenerator
```

### CandidateArtifact

```python
@dataclass
class CandidateArtifact:
    artifact_id: str
    sdc_text: str
    input_hash: str                 # SHA256(sdc_text)
    candidate_hash: str             # same as input_hash
    provision: Dict[str, Any]       # model, provider, temperature
    schema_version: str = "eger.candidate.v1"
    created_at: str = ""
    verified: bool = False          # ALWAYS False until gate accepts
    
    # INVARIANT: verified is False until VerificationGate accepts
    # PRODUCER: ProposalGenerator (via extract_candidate)
    # CONSUMER: OracleAdapter, VerificationGate
    # AUTHORITY: PROPOSAL ONLY
```

### EvidenceArtifact

```python
@dataclass
class Finding:
    finding_id: str
    severity: str                   # "error" | "warning" | "info"
    category: str
    entity: str
    message: str
    source: str
    expected_state: str
    observed_state: str
    remediation_hint: str
    provenance: Dict[str, Any]

@dataclass
class EvidenceArtifact:
    evidence_id: str
    task_id: str
    oracle_status: str
    evidence_scope: str
    findings: List[Finding]
    summary: Dict[str, int]         # error_count, warning_count, info_count
    analysis_scope: Dict[str, Any]
    schema_version: str = "eger.evidence.v1"
    created_at: str = ""
    
    # INVARIANT: summary.error_count == len([f for f in findings if f.severity == "error"])
    # PRODUCER: EvidenceNormalizer
    # CONSUMER: RevisionController, VerificationGate, PromptBuilder
    # AUTHORITY: EVIDENCE — not modifiable by LLM
```

### VerificationResult

```python
@dataclass
class VerificationResult:
    decision: str                   # "ACCEPT" | "REJECT"
    reason: str
    error_count: int
    unresolved_findings: List[str]
    provenance: Dict[str, Any]
    schema_version: str = "eger.verification.v1"
    
    # INVARIANT: decision is deterministic given evidence
    # PRODUCER: VerificationGate
    # CONSUMER: RunRecord, external system
    # AUTHORITY: AUTHORIZATION — final decision
```

### RunRecord

```python
@dataclass
class RunRecord:
    run_id: str
    task_id: str
    config: Dict[str, Any]
    iterations: List[Dict[str, Any]]  # per-iteration artifacts
    final_decision: str
    final_evidence_id: Optional[str]
    final_candidate_id: Optional[str]
    total_calls: int
    duration_seconds: float
    status: str                       # "ACCEPTED" | "REJECTED" | "INCOMPLETE"
    provenance: Dict[str, Any]
    schema_version: str = "eger.run.v1"
    
    # INVARIANT: complete provenance chain
    # PRODUCER: RevisionController
    # CONSUMER: External system, audit
```

---

## 17. Testing Strategy

### Unit Tests

| Module | Test Focus | Deterministic? |
|--------|-----------|---------------|
| `eger/task/` | TaskDefinition construction, validation | YES |
| `eger/prompting/` | Prompt construction, template rendering | YES |
| `eger/evidence/` | Evidence normalization, Finding extraction | YES |
| `eger/verification/` | Gate logic, acceptance criteria | YES |
| `eger/provenance/` | Provenance chain completeness | YES |
| `eger/engineer/` | SDC extraction, candidate building | YES |
| `eger/oracle/` | Oracle adapter, schema validation | YES |

### Contract Tests

| Contract | Focus |
|----------|-------|
| Oracle → Evidence | OracleResult normalizes to EvidenceArtifact |
| Evidence → Revision | EvidenceArtifact feeds into PromptBuilder |
| Revision → Oracle | Revised SDC feeds into OracleAdapter |
| Task → Prompt | TaskDefinition produces valid prompt |

### Integration Tests

| Integration | Focus |
|-------------|-------|
| Full cycle | Task → LLM → Oracle → Evidence → Revision → Gate |
| Checkpoint/resume | RevisionController persists and resumes |
| Failure handling | Provider timeout, oracle failure, malformed output |

### Safety Tests

| Safety | Focus |
|--------|-------|
| Bypass prevention | LLM cannot modify evidence |
| Fail-closed | Ambiguous evidence → REJECT |
| Provenance completeness | Every artifact has provenance |
| Budget enforcement | Cannot exceed call budget |

### Existing Tests (Preserved)

| Test | Status |
|------|--------|
| `test_c1_feedback.py` (16/16) | PRESERVED |
| `test_evidence_oracle.py` | PRESERVED |
| `test_llm_proposal.py` | PRESERVED |
| `test_epistemic_authorization.py` | PRESERVED |
| `test_base_rate_stabilization.py` (16/16) | PRESERVED |
| `test_cross_task_e3a_replication.py` (19/19) | PRESERVED |
| `test_e3a_wording_deconfounding.py` (20/20) | PRESERVED |

---

## 18. Implementation Sequence

```
P137 — Architecture Implementation Design ← WE ARE HERE
  ↓
P138 — Core Contracts (TaskDefinition, EvidenceArtifact, CandidateArtifact)
  ↓
P139 — Evidence Pipeline (OracleAdapter → EvidenceNormalizer)
  ↓
P140 — Prompt Construction (PromptBuilder with broad framing)
  ↓
P141 — Revision Controller (loop control, budget, checkpoint)
  ↓
P142 — Verification Gate (acceptance/rejection logic)
  ↓
P143 — Provenance Tracker (chain recording)
  ↓
P144 — Integration (full cycle test)
  ↓
P145 — Architecture Validation (deterministic tests pass)
```

### Dependencies

| Phase | Depends On |
|-------|-----------|
| P138 | P137 |
| P139 | P138 |
| P140 | P138 |
| P141 | P139, P140 |
| P142 | P139 |
| P143 | P138 |
| P144 | P139, P140, P141, P142, P143 |
| P145 | P144 |

---

## 19. Scientific Classification

| Component | Classification |
|-----------|---------------|
| Broad task framing | **EMPIRICALLY SUPPORTED BEHAVIORAL SIGNAL** |
| LLM proposal generation | **EMPIRICALLY SUPPORTED** |
| Structured evidence feedback | **EMPIRICALLY SUPPORTED** |
| Deterministic Oracle boundary | **ENGINEERING DESIGN CHOICE / EGER PRINCIPLE** |
| Evidence normalization | **EMPIRICALLY SUPPORTED** |
| Revision loop | **EMPIRICALLY SUPPORTED** |
| Verification gate | **ENGINEERING DESIGN CHOICE / EGER PRINCIPLE** |
| Provenance tracking | **ENGINEERING DESIGN CHOICE** |
| Evidence-conditioned routing (C4) | **ENGINEERING DESIGN CHOICE / DEFERRED** |
| Authorization gate (C5) | **ENGINEERING DESIGN CHOICE / DEFERRED** |
| Epistemic state (C3) | **FUTURE HYPOTHESIS / NOT INCLUDED** |

---

## 20. Architectural Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Framing effect is MODEL-005-specific | Medium | Acknowledge limitation; test on new models if deployed |
| Oracle scope insufficient for some designs | Low | Ṛta provides SDC-specific checks; scope documented |
| Revision loop doesn't converge | Medium | Budget enforcement; max iteration limit |
| Provider instability | High | Checkpoint/resume; no retry policy |
| Authority separation violated | High | Deterministic enforcement; no LLM access to evidence/authorization |
| False acceptance | Medium | Fail-closed rule; all ERRORs must be resolved |
| False rejection | Low | Conservative by design; better to reject than accept incorrect SDC |
| Provenance gaps | Medium | Mandatory provenance chain; reject incomplete records |
| Specification drift | Low | Schema versioning; frozen contracts |
| Benchmark overfitting | Medium | Anti-gaming principles; unseen designs in benchmark |

---

## 21. Recommended Next Gate

**P138 — Core Contracts Implementation**

Implement the foundational data contracts:
- `TaskDefinition`
- `EvidenceArtifact`
- `CandidateArtifact`
- `Finding`
- `RunRecord`

These contracts define the interfaces between all components and can be implemented and tested independently.

---

```
P137 COMPLETE
ARCHITECTURE IMPLEMENTATION DESIGN COMPLETE

EMPIRICAL PHASE: COMPLETE
RQ-4: CLOSED

C0: ESTABLISHED
C1: ESTABLISHED
C2: PARTIALLY SUPPORTED
C3: NOT JUSTIFIED
C4: DEFERRED
C5: DEFERRED

CORE ARCHITECTURE:
STRUCTURED EVIDENCE
+
BROAD TASK FRAMING SIGNAL
+
LLM PROPOSAL
+
DETERMINISTIC ORACLE
+
CONTROLLED REVISION
+
VERIFICATION GATE

CAUSALITY: NOT ESTABLISHED

NEXT GATE: P138 Core Contracts Implementation

NO MODEL CALLS
NO EXPERIMENT EXECUTED
```
