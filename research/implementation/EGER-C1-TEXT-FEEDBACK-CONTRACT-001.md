# EGER-C1-TEXT-FEEDBACK-CONTRACT-001 — C1 Text Feedback Contract

| Field | Value |
|-------|-------|
| ID | EGER-C1-TEXT-FEEDBACK-CONTRACT-001 |
| Produced by | EGER-P018 (2026-08-26) |
| Type | Protocol definition — NOT implementation |
| Status | PROPOSED FOR HUMAN REVIEW — not yet frozen for experimental execution |
| Predecessor | EGER-C1-READINESS-001 (B-1 blocker resolved) |
| Purpose | Define the exact text feedback format for C1 = C0 + deterministic oracle text feedback |

---

## 1. Purpose

This contract defines the deterministic text rendering of oracle output that the Engineer receives in C1. It resolves the C1 readiness blocker B-1 ("C1 text feedback format not defined").

C1 tests:

> Does adding deterministic-oracle TEXT FEEDBACK improve the Engineer's artifact/reasoning reliability relative to C0?

The sole declared C0→C1 capability addition is TEXT FEEDBACK. This contract defines exactly what that feedback contains.

---

## 2. Relationship to C0 and C1

```
C0 pipeline:
  Engineer → candidate → oracle → [evidence NOT shown to Engineer]

C1 pipeline:
  Engineer → candidate → oracle → TEXT FEEDBACK → Engineer
```

The text feedback is derived **only** from the deterministic EvidenceArtifact produced by the oracle. No other source contributes to the feedback.

---

## 3. Authority Separation

The text feedback is an **EVIDENCE COMMUNICATION** mechanism. It is NOT:

- An epistemic state transition (that belongs to L2, activated in C3)
- An authorization decision (that belongs to L3, activated in C5)
- An evaluator answer (that belongs to evaluator_only)
- An LLM-generated interpretation (the renderer is deterministic)

The four-layer separation must be preserved in the rendered text:

```
ORACLE EXECUTION STATUS
        ≠
EVIDENCE SUFFICIENCY / SCOPE
        ≠
FINDINGS (engineering diagnostics)
        ≠
EPISTEMIC STATE (not exposed in C1)
        ≠
AUTHORIZATION STATE (not exposed in C1)
```

---

## 4. Agent Information Boundary

### Engineer MAY RECEIVE (C1)

| Information | Source | Justification |
|-------------|--------|---------------|
| Task design_context | BENCH-002 engineer_visible | Same as C0 |
| Task objective | BENCH-002 engineer_visible | Same as C0 |
| Task constraints | BENCH-002 engineer_visible | Same as C0 |
| Text feedback from oracle | This contract | C1 treatment variable |

### Engineer MUST NOT RECEIVE (C1)

| Information | Why |
|-------------|-----|
| evaluator_only/*.expected.json | Benchmark answers — data leakage |
| Expected solution text | Would bias proposals |
| Ground-truth candidate | Would bias proposals |
| C0 results / outcomes | Would bias C1 proposals |
| Other benchmark tasks | Task isolation |
| research/RESEARCH.md | Research canon |
| research/PRINCIPLES.md | Research canon |
| research/STATE.md | Research canon |
| research/RESEARCH_LEDGER.md | Research canon |
| Git history | Would expose previous runs |
| Oracle source code | External boundary |
| Structured EvidenceArtifact | C2 treatment |
| EpistemicState | C3 treatment |
| Authorization decisions | C5 treatment |
| Evidence hash | Provenance metadata, not engineering feedback |
| Raw hash | Provenance metadata |
| Input hash | Provenance metadata |
| produced_at timestamp | Provenance metadata |
| Provenance identifier | Audit metadata, not engineering feedback |

---

## 5. Feedback Schema

### Conceptual Structure

```
ORACLE RESULT
─────────────
Oracle execution: <status>

EVIDENCE SCOPE
──────────────
Scope: <scope>
Scope limitation: <limitation description>

FINDINGS
────────
[SEVERITY] CODE: Message. (Line N)
[SEVERITY] CODE: Message. (Line N)
...
```

### Fields

| # | Field | Source | Exposed | Deterministic | Required |
|---|-------|--------|---------|---------------|----------|
| F1 | Oracle execution status | EvidenceArtifact.oracle_status | YES | YES | YES |
| F2 | Evidence scope | EvidenceArtifact.evidence_scope | YES | YES | YES |
| F3 | Scope limitation text | Derived from scope + analysis_scope | YES | YES | YES |
| F4 | Findings | EvidenceArtifact.findings[] | YES | YES | YES (may be empty) |
| F5 | Finding severity | FindingArtifact.severity | YES | YES | YES |
| F6 | Finding code | FindingArtifact.code | YES | YES | YES |
| F7 | Finding message | FindingArtifact.message | YES | YES | YES |
| F8 | Finding location | FindingArtifact.location.line | YES | YES | YES (0 = unknown) |
| F9 | Provenance identifier | EvidenceArtifact.provenance | NO | — | — |
| F10 | Evidence hash | EvidenceArtifact.evidence_hash | NO | — | — |
| F11 | Raw hash | EvidenceArtifact.raw_ref.raw_hash | NO | — | — |
| F12 | produced_at | EvidenceArtifact.produced_at | NO | — | — |

---

## 6. Oracle Execution Status

### Permitted Values

| Status | Rendering | Source |
|--------|-----------|--------|
| `SUCCESS` | `Oracle execution: SUCCESS` | EvidenceArtifact.oracle_status = SUCCESS |
| `INVALID_REQUEST` | `Oracle execution: INVALID_REQUEST` | EvidenceArtifact.oracle_status = INVALID_REQUEST |
| `ORACLE_FAILURE` | `Oracle execution: FAILURE` | EvidenceArtifact.oracle_status = ORACLE_FAILURE |

### Rules

- Rendering is **literal** — the status word is reproduced exactly
- `SUCCESS` must NOT be rendered as `VALIDATED` (P6/P7 separation)
- `ORACLE_FAILURE` must NOT be rendered as `INVALID` (contract §9 separation)
- If oracle_status is not one of the three defined values: render as `Oracle execution: UNKNOWN (<value>)`

---

## 7. Evidence Scope

### Permitted Values

| Scope | Rendering | Scope Limitation Text | Source |
|-------|-----------|----------------------|--------|
| `FULL` | `Scope: FULL` | `Scope limitation: All constructs fully analyzed within declared scope.` | evidence_scope = FULL |
| `PARTIAL` | `Scope: PARTIAL` | `Scope limitation: Some constructs were recognized but not fully value-analyzed.` | evidence_scope = PARTIAL |
| `INSUFFICIENT` | `Scope: INSUFFICIENT` | `Scope limitation: Netlist-dependent checks could not be evaluated without design context.` | evidence_scope = INSUFFICIENT |
| `UNSUPPORTED` | `Scope: UNSUPPORTED` | `Scope limitation: Input contains constructs outside the oracle's recognized scope.` | evidence_scope = UNSUPPORTED |

### Rules

- The scope word is reproduced exactly from the EvidenceArtifact
- `INSUFFICIENT` must NOT be rendered as `INCORRECT` or `FAILED` — it means missing context, not wrong engineering
- `FULL` must NOT be rendered as `VALIDATED` — scope is about what the oracle checked, not whether the candidate is correct
- The scope limitation text is a **deterministic, frozen description** of what each scope means — it is NOT an LLM interpretation

### When Scope is Null

If `evidence_scope` is null (only possible with ORACLE_FAILURE):
- Do NOT render the EVIDENCE SCOPE section
- The feedback ends after the execution status

---

## 8. Findings

### Finding Rendering Format

Each finding is rendered as a single line:

```
[SEVERITY] CODE: Message. (Line N)
```

Where:
- `SEVERITY` = uppercase severity (ERROR / WARNING / INFO)
- `CODE` = the finding code (e.g., SDC-005)
- `Message` = the deterministic message from the oracle
- `Line N` = the line number from location.line (omitted if line = 0)

### Example

```
[ERROR] SDC-005: No set_input_delay — all input ports are unconstrained. (Line 0)
[WARNING] SDC-030: No set_propagated_clock — ideal clock model is over-optimistic for post-layout correlation. (Line 0)
[INFO] SDC-100: No sdc_version declaration. Add 'set sdc_version 2.2' at the top. (Line 0)
```

### Rules

- Each finding is rendered independently — no summarization
- No LLM-generated interpretation is added
- The renderer must NOT add "therefore fix X" unless that text is itself the oracle's deterministic message
- The renderer must NOT collapse multiple findings into a paragraph
- Finding codes are reproduced exactly
- Messages are reproduced exactly (no truncation, no paraphrase)
- If `location.line` is 0, render as `(Line N)` where N=0, or omit the line reference — both are acceptable as long as consistent
- Finding ordering follows the severity-based order defined in §12

---

## 9. Provenance

### Decision: NOT EXPOSED TO ENGINEER

Provenance fields (oracle name, version, revision, input hash, raw hash, evidence hash, produced_at, raw path) are **audit metadata**. They improve auditability but do not improve engineering reasoning.

The Engineer has no use for:
- `evidence_hash` — the Engineer cannot compare hashes
- `raw_hash` — the Engineer cannot interpret raw oracle bytes
- `input_hash` — the Engineer already knows the candidate text
- `produced_at` — timestamp is not engineering feedback
- `oracle.revision` — the Engineer cannot act on revision information

These fields remain in the EvidenceArtifact and run manifest for reproducibility and audit. They are NOT rendered in the C1 text feedback.

**If a future condition requires provenance visibility, it must be authorized via EGER-CHANGE-###.**

---

## 10. Hash / Integrity Metadata

### Decision: NOT EXPOSED TO ENGINEER

Hashes (evidence_hash, raw_hash, input_hash) are integrity verification tools. The Engineer cannot use hashes to improve engineering reasoning. They remain in the EvidenceArtifact for auditor verification.

---

## 11. Deterministic Rendering Rules

### Core Requirement

The same EvidenceArtifact MUST produce the same C1 text feedback, every time, across all runs, tasks, and conditions.

### Field Order

The text feedback is rendered in this exact order:

```
1. ORACLE RESULT header
2. Oracle execution status line
3. (blank line)
4. EVIDENCE SCOPE header
5. Scope line
6. Scope limitation line
7. (blank line)
8. FINDINGS header
9. Finding lines (in order per §12)
10. (blank line — only if findings exist)
```

### Finding Order

Findings are sorted by:
1. **Severity** (descending): error → warning → info
2. **Diagnostic code** (ascending alphabetical): SDC-001 before SDC-002
3. **Stable source order** (for same severity + same code): original order from oracle

### Whitespace Policy

- Sections separated by a single blank line
- No trailing whitespace on lines
- No trailing blank line at end of feedback
- Line endings: `\n` (Unix)
- Indentation: none (flat rendering)

### Empty Fields

| Scenario | Rendering |
|----------|-----------|
| No findings | `FINDINGS` header present, followed by nothing (no "no findings" message) |
| No scope limitation | Scope limitation line omitted |
| line = 0 | `(Line 0)` rendered as-is |
| severity is unexpected value | Render as `[SEVERITY_VALUE]` literally |

### Multiple Findings

Each finding is rendered as a separate line. No summarization. No information loss. No grouping.

### Evidence Artifact is ORACLE_FAILURE

```
ORACLE RESULT
─────────────
Oracle execution: FAILURE
```

No EVIDENCE SCOPE section. No FINDINGS section. The feedback ends.

---

## 12. Finding Sort Algorithm

```python
SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}

def sort_findings(findings):
    return sorted(findings, key=lambda f: (
        SEVERITY_ORDER.get(f["severity"], 99),
        f["code"],
    ))
```

This is deterministic and reproducible. The same set of findings always produces the same order.

---

## 13. Empty / Missing Fields

| Field | Empty State | Rendering |
|-------|-------------|-----------|
| findings = [] | No findings | `FINDINGS` header only, no lines below |
| scope_limitation = null | No limitation | Scope limitation line omitted |
| location.line = 0 | Unknown location | `(Line 0)` |
| analysis_scope = null | Only on ORACLE_FAILURE | Entire EVIDENCE SCOPE section omitted |

---

## 14. Multiple Findings

Multiple findings are rendered as independent lines, one per finding. No summarization. No LLM-generated paragraph. No information loss.

The Engineer receives every finding the oracle produced, in the deterministic order defined by §12.

---

## 15. Protocol Examples

### Example A: SUCCESS + FULL + No Errors

**Input:** EvidenceArtifact with oracle_status=SUCCESS, evidence_scope=FULL, findings=[]

```
ORACLE RESULT
─────────────
Oracle execution: SUCCESS

EVIDENCE SCOPE
──────────────
Scope: FULL
Scope limitation: All constructs fully analyzed within declared scope.

FINDINGS
────────
```

**Interpretation:** Oracle ran successfully. All constructs fully analyzed. No issues found. The candidate may still be incorrect — FULL scope with no errors means "no issues within declared scope," not "universally correct."

### Example B: SUCCESS + INSUFFICIENT + Diagnostic Findings

**Input:** EvidenceArtifact with oracle_status=SUCCESS, evidence_scope=INSUFFICIENT, findings=[SDC-005 error, SDC-006 error, SDC-030 warning, SDC-100 info]

```
ORACLE RESULT
─────────────
Oracle execution: SUCCESS

EVIDENCE SCOPE
──────────────
Scope: INSUFFICIENT
Scope limitation: Netlist-dependent checks could not be evaluated without design context.

FINDINGS
────────
[ERROR] SDC-005: No set_input_delay — all input ports are unconstrained. (Line 0)
[ERROR] SDC-006: No set_output_delay — all output ports are unconstrained. (Line 0)
[WARNING] SDC-030: No set_propagated_clock — ideal clock model is over-optimistic for post-layout correlation. (Line 0)
[INFO] SDC-100: No sdc_version declaration. Add 'set sdc_version 2.2' at the top. (Line 0)
```

**Interpretation:** Oracle ran successfully. Could not fully validate due to missing netlist. Found 2 errors (missing I/O delays), 1 warning (missing propagated clock), 1 info (missing sdc_version).

### Example C: SUCCESS + PARTIAL + Findings

**Input:** EvidenceArtifact with oracle_status=SUCCESS, evidence_scope=PARTIAL, findings=[SDC-005 error, SDC-006 error, SDC-021 warning]

```
ORACLE RESULT
─────────────
Oracle execution: SUCCESS

EVIDENCE SCOPE
──────────────
Scope: PARTIAL
Scope limitation: Some constructs were recognized but not fully value-analyzed.

FINDINGS
────────
[ERROR] SDC-005: No set_input_delay — all input ports are unconstrained. (Line 0)
[ERROR] SDC-006: No set_output_delay — all output ports are unconstrained. (Line 0)
[WARNING] SDC-021: Multicycle path -setup 2 has no -hold fix. Add -hold 1. (Line 2)
```

**Interpretation:** Oracle ran successfully. Partial analysis possible. Found 2 errors (missing I/O delays) and 1 warning (missing hold fix on multicycle path).

### Example D: ORACLE_FAILURE

**Input:** OracleResult with is_success=False, failure.kind=ORACLE_FAILURE

```
ORACLE RESULT
─────────────
Oracle execution: FAILURE
```

**Interpretation:** Oracle failed to execute. No evidence produced. The Engineer receives no diagnostic information. This is NOT an engineering failure — it is an infrastructure failure.

### Example E: Adversarial/Error Finding (SDC-007)

**Input:** EvidenceArtifact with oracle_status=SUCCESS, evidence_scope=INSUFFICIENT, findings=[SDC-005 error, SDC-006 error, SDC-007 error, SDC-024 warning]

```
ORACLE RESULT
─────────────
Oracle execution: SUCCESS

EVIDENCE SCOPE
──────────────
Scope: INSUFFICIENT
Scope limitation: Netlist-dependent checks could not be evaluated without design context.

FINDINGS
────────
[ERROR] SDC-005: No set_input_delay — all input ports are unconstrained. (Line 0)
[ERROR] SDC-006: No set_output_delay — all output ports are unconstrained. (Line 0)
[ERROR] SDC-007: create_clock on likely data port "data_bus_0" — use dedicated clock ports only. (Line 2)
[WARNING] SDC-024: 2 clocks defined but no set_clock_groups — CDC paths may be analyzed as synchronous. (Line 0)
```

**Interpretation:** Oracle ran successfully. Found 3 errors including the adversarial SDC-007 (clock on data port). The Engineer should remove the clock on data_bus_0.

---

## 16. C0→C1 Causal Isolation

### What C0 Engineer Receives

```
[design_context]
[objective]
```

### What C1 Engineer Receives

```
[design_context]
[objective]

<text feedback from this contract>
```

### What Changes

| Element | C0 | C1 |
|---------|----|----|
| Task context | design_context + objective | design_context + objective (SAME) |
| Oracle feedback | NOT PRESENT | TEXT FEEDBACK (this contract) |
| Structured evidence | NOT PRESENT | NOT PRESENT (C2) |
| Epistemic state | NOT PRESENT | NOT PRESENT (C3) |
| Routing | NOT PRESENT | NOT PRESENT (C4) |
| Authorization | NOT PRESENT | NOT PRESENT (C5) |

### What Must Remain Constant

- Model: MODEL-002 (opencode/muse-spark-1.2 NOT_EXPOSED)
- Temperature: 0.0
- Max tokens: 2048
- Prompt baseline: eger.prompt.v1
- Model-call budget: 5
- Oracle: Ṛta v1.5.11 (3b5c2f2)
- Oracle configuration: custom_rules OFF
- Termination budget: max_iterations=5, max_wall_clock=300s
- Benchmark: BENCH-002 v0.1 (6 tasks, frozen order)
- Artifact schemas: eger.candidate.v1, eger.evidence.v1
- Run manifest schema: frozen

---

## 17. Confound Monitoring Compatibility

The text feedback contract preserves the ability to observe the seven pre-registered C0→C1 confound indicators (CM-1 through CM-7):

| Indicator | Observable via C1 feedback? |
|-----------|---------------------------|
| CM-1: Recovery from specific finding | YES — Engineer can see SDC-005/006 and add I/O delays |
| CM-2: Correction of known SDC error | YES — Engineer can see SDC-007 and remove clock on data |
| CM-3: Repeated response to INSUFFICIENT | YES — Engineer sees "Scope: INSUFFICIENT" and may react |
| CM-4: Unchanged behavior after non-actionable feedback | YES — info findings produce no change (expected) |
| CM-5: Candidate improvement from evidence | YES — compare C0 vs C1 candidates |
| CM-6: New errors introduced | YES — compare C0 vs C1 evidence |
| CM-7: Convergence attempt | YES — observe iteration count |

The contract does not prevent any confound indicator from being measured.

---

## 18. Explicit Exclusions

The following are **explicitly excluded** from C1 text feedback:

| Excluded | Reason |
|----------|--------|
| Expected solution text | Benchmark answer — data leakage |
| Ground-truth candidate | Would bias proposals |
| Evaluation labels | Evaluator-only metadata |
| Research conclusions | Would bias proposals |
| Epistemic state (HYPOTHESIS/VALIDATED/etc.) | C3 treatment |
| Authorization decisions (APPROVED/REJECTED) | C5 treatment |
| Structured EvidenceArtifact | C2 treatment |
| Evidence hash | Audit metadata |
| Raw hash | Audit metadata |
| Input hash | Audit metadata |
| produced_at | Provenance metadata |
| Oracle revision | Audit metadata |
| Analysis scope constructs array | Detailed scope data (not needed for engineering reasoning) |
| Analysis scope counts | Detailed scope data |
| Unknown/ignored options lists | Detailed scope data |

---

## 19. Open Design Questions

| # | Question | Status | Impact |
|---|----------|--------|--------|
| ODQ-1 | **Text injection point** — where in the prompt is feedback inserted (after design_context/objective? as a separate section? as a new turn?) | OPEN | Affects prompt structure; must be defined before C1 |
| ODQ-2 | **Iteration protocol** — does C1 allow multiple generate→validate cycles, or single-shot? | OPEN | Protocol §13 allows up to 5 iterations; clarification needed |
| ODQ-3 | **Line reference rendering** — should line=0 be rendered as "(Line 0)" or omitted? | OPEN | Minor formatting; must be consistent |

---

## 20. Contract / Principle References

| Contract/Principle | Relevance |
|-------------------|-----------|
| P6 — Explicit Epistemic Boundaries | Scope is never upgraded; INSUFFICIENT ≠ FALSE |
| P7 — Authority Separation | Feedback is evidence communication, not epistemic/authorization |
| Contract §8 — Evidence Scope | Scope levels and no-upgrade rule |
| Contract §9 — Error Model | ORACLE_FAILURE ≠ INVALID |
| Contract §12 — Normalization Rules | Findings preserved exactly |
| Protocol §6 — C0–C5 Definitions | C1 = text feedback only |
| Protocol §7 — Capability Matrix | Text feedback is C1's sole addition |
| Protocol §12 — Failure Taxonomy | No collapsed FAILED classes |
| Protocol §22 — Data Leakage Controls | No evaluator answers in prompts |

---

## 21. Final C1 Feedback Contract

### ACCEPTED PROTOCOL DEFINITION

| Element | Definition |
|---------|------------|
| Feedback fields | Oracle execution status, Evidence scope, Scope limitation text, Findings (severity/code/message/line) |
| Field order | Status → Scope → Findings |
| Finding order | Severity (error→warning→info) → Code (alphabetical) → Source order |
| Rendering syntax | Flat text, `\n` line endings, no indentation |
| Scope representation | Literal scope word + frozen limitation description |
| Execution status representation | Literal status word (SUCCESS/INVALID_REQUEST/FAILURE) |
| Multiple findings | One line per finding, no summarization |
| Empty findings | Header only, no lines |
| Provenance visibility | NOT exposed (audit metadata only) |
| Hash visibility | NOT exposed |
| Determinism rule | Same EvidenceArtifact → same text, always |
| Information-boundary rule | Only oracle findings + scope; no evaluator answers, no research canon |
| C0→C1 causal-isolation rule | Only text feedback added; all other constants frozen |

### PROPOSED BUT NON-BINDING

| Element | Proposal |
|---------|----------|
| Text injection point | After design_context/objective, separated by blank line |
| Line reference when line=0 | Render as "(Line 0)" |

### OPEN DESIGN QUESTIONS

| # | Question |
|---|----------|
| ODQ-1 | Text injection point (final) |
| ODQ-2 | Iteration protocol |
| ODQ-3 | Line=0 rendering |

---

## 22. Non-Decisions

This contract does NOT:

- Execute C1
- Modify the benchmark
- Modify MODEL-002
- Modify Ṛta
- Implement runtime code
- Create subagents
- Authorize C1 execution
- Freeze the contract (requires human review)

---

*This contract is PROPOSED FOR HUMAN REVIEW. It becomes frozen only after explicit human authorization. The C1 text feedback format must be confirmed before C1 implementation begins.*
