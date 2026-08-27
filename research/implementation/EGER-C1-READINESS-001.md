# EGER-C1-READINESS-001 — C1 Readiness & Experimental Freeze Review

**Prompt ID:** EGER-P017
**Date:** 2026-08-26
**Type:** Read-only readiness review — NO code changes, NO benchmark changes, NO model changes, NO C1 execution, NO Git commits, NO Ṛta modifications
**Predecessor:** EGER-C0-REVIEW-001-R1
**Next possible stage:** Human review → C1 authorization

---

## 1. Research Canon Reviewed

The following documents were inspected:

| Document | Path | Key Content |
|----------|------|-------------|
| RESEARCH.md | research/RESEARCH.md | Canonical research definition, C0–C5 ablation, authority model |
| PRINCIPLES.md | research/PRINCIPLES.md | P1–P8 operational form |
| STATE.md | research/STATE.md | Current scientific state, C0 complete, C1 requires authorization |
| RESEARCH_LEDGER.md | research/RESEARCH_LEDGER.md | Full chronological research history through P017 |
| EGER-EXP-001-PROTOCOL.md | research/experiments/EGER-EXP-001-PROTOCOL.md | Frozen experimental protocol v0.1, 30 sections |
| EGER-ARCH-002.md | research/architecture/EGER-ARCH-002.md | Architecture recommendation, condition deltas |
| EGER-MODEL-002.md | research/experiments/EGER-MODEL-002.md | Frozen live model configuration |
| EGER-C0-REVIEW-001-R1.md | research/implementation/EGER-C0-REVIEW-001-R1.md | Revised C0 review, confound status open |
| EGER-AUTH-001-C0.md | research/implementation/EGER-AUTH-001-C0.md | C0 execution report |

No document disagreements were found. No RESEARCH CANON CONFLICT or OPEN DESIGN QUESTION from document inconsistency.

---

## 2. Current Scientific State

```
C0                    ✓ COMPLETE (6/6 tasks, LLM ONLY)
C0 evidence           ✓ PRESERVED
C0 checkpoint         ✓ PRESERVED
C0 review (R1)       ✓ COMPLETE (documented limitation, confound status open)
C1–C5                 ✗ NOT EXECUTED
C6                    ✗ NOT AUTHORIZED (engineering extension, deferred)
GitHub                ✓ PUSHED (PRIVATE)
Benchmark exposure    ⚠ COMPROMISED (remediated to PRIVATE)
Ṛta                   ✓ UNTOUCHED (3b5c2f2 main 19)
```

---

## 3. C0→C1 Independent Variable

**What changes from C0 to C1:**

C1 adds exactly one capability: **textual tool feedback** (deterministic oracle output rendered as text).

Per protocol §6 and ARCH-002 condition deltas:

```
C0→C1:
  ADDED: Oracle execution; findings as plain text
  REMOVED: —
  CONTROLS: Text rendered deterministically from same JSON as C2
```

Per protocol §7 capability matrix:

```
| Capability                  | C0 | C1 |
| Candidate generation        | ✓  | ✓  |
| Text feedback               | -  | ✓  |
| Structured evidence         | -  | -  |
| Epistemic state (read-only) | -  | -  |
| Deterministic routing       | -  | -  |
| Authorization gate          | -  | -  |
```

**The sole independent variable is: text feedback from the deterministic oracle.**

Nothing else changes.

---

## 4. C1 Text Feedback Contract

### Status: **OPEN DESIGN QUESTION**

The frozen protocol (EXP-001 v0.1 §6) defines C1 as:

> "+ textual tool feedback (deterministic oracle output rendered as text)"

It does **not** define:
- The exact text format
- Which oracle fields are included/excluded
- How findings are rendered
- Whether evidence_scope is exposed in text

**This is an OPEN DESIGN QUESTION that must be resolved before C1 execution.**

### Candidate Designs (NON-BINDING OPTIONS)

The following are candidate designs for the C1 text feedback format. None is authoritative. The human researcher must select or modify before C1 authorization.

#### Option A: Full Oracle Summary

Render the complete oracle output as structured text:

```
=== Oracle Evaluation ===
Oracle execution: SUCCESS
Evidence scope: INSUFFICIENT
Findings (23):
  [ERROR] SDC-005: No set_input_delay — all input ports are unconstrained.
  [ERROR] SDC-006: No set_output_delay — all output ports are unconstrained.
  [WARNING] SDC-030: No set_propagated_clock — ideal clock model is over-optimistic.
  [INFO] SDC-100: No sdc_version declaration.
  ... (remaining info-level findings)
Evidence hash: b70475e7...
```

**Includes:** oracle execution status, evidence_scope, all findings (error/warning/info), evidence hash.
**Excludes:** raw oracle bytes, candidate hash, prompt hash, provenance metadata.

**Risk:** Exposing `evidence_scope: INSUFFICIENT` may cause the Engineer to treat the entire evaluation as unreliable, even though individual findings are deterministic and actionable.

#### Option B: Findings Only (No Scope)

Render only the findings, omitting the evidence_scope:

```
=== Oracle Findings ===
[ERROR] SDC-005: No set_input_delay — all input ports are unconstrained.
[ERROR] SDC-006: No set_output_delay — all output ports are unconstrained.
[WARNING] SDC-030: No set_propagated_clock — ideal clock model is over-optimistic.
[INFO] SDC-100: No sdc_version declaration.
...
```

**Includes:** findings (error/warning/info).
**Excludes:** evidence_scope, oracle execution status, hashes.

**Risk:** Hides the fact that the evaluation is INSUFFICIENT-scope, which may cause the Engineer to over-trust the findings.

#### Option C: Error/Warning Only (Filtered)

Render only error and warning severity findings:

```
=== Oracle Findings ===
[ERROR] SDC-005: No set_input_delay — all input ports are unconstrained.
[ERROR] SDC-006: No set_output_delay — all output ports are unconstrained.
[WARNING] SDC-030: No set_propagated_clock — ideal clock model is over-optimistic.
```

**Includes:** error and warning findings only.
**Excludes:** info-level findings, evidence_scope, hashes.

**Risk:** Reduces information available to Engineer; may prevent learning from info-level guidance.

### Recommendation

**Option A (Full Oracle Summary)** is the most scientifically honest because:
1. It preserves the ORACLE EXECUTION ≠ EVIDENCE SUFFICIENCY separation
2. It does not hide the INSUFFICIENT scope from the Engineer
3. It matches what C2 will receive (structured EvidenceArtifact with scope)
4. The format difference between C1 (text) and C2 (structured) is exactly the treatment delta

The human researcher must confirm or modify before C1 execution.

---

## 5. C1 Information Boundary

### Engineer MAY RECEIVE

| Information | Source | Justification |
|-------------|--------|---------------|
| Task design_context | BENCH-002 engineer_visible | Same as C0 |
| Task objective | BENCH-002 engineer_visible | Same as C0 |
| Task constraints | BENCH-002 engineer_visible | Same as C0 |
| Text feedback from oracle | C1-authorized text rendering | C1 treatment variable |

### Engineer MUST NOT RECEIVE

| Information | Why |
|-------------|-----|
| evaluator_only/*.expected.json | Benchmark answers — data leakage (protocol §22) |
| Hidden labels / classification | Evaluator-only metadata |
| C0 results / outcomes | Would bias C1 proposals |
| C1 results / outcomes | Not yet generated |
| research/RESEARCH.md | Research canon — not engineering context |
| research/PRINCIPLES.md | Research canon — not engineering context |
| research/STATE.md | Research canon — not engineering context |
| research/RESEARCH_LEDGER.md | Research canon — not engineering context |
| Other benchmark tasks | Task isolation (protocol §11) |
| Git history | Would expose previous runs |
| Future experiment results | Not yet generated |
| Ṛta source code | External boundary (DEC-006) |
| Ṛta tests/fixtures | External boundary |
| Research conclusions | Would bias proposals |
| Structured EvidenceArtifact | C2 treatment — not C1 |
| EpistemicState | C3 treatment — not C1 |
| Evidence-conditioned routing | C4 treatment — not C1 |
| Authorization gate | C5 treatment — not C1 |
| Candidate hash / evidence hash | Provenance metadata, not engineering feedback |
| Prompt hash / output hash | Provenance metadata |

### Boundary Enforcement

The C1 runner must:
1. Load only engineer_visible task files (same as C0 runner)
2. Render oracle findings as text (per selected option above)
3. Inject text into the Engineer prompt as feedback
4. NOT inject structured JSON, epistemic state, or authorization

---

## 6. C0 INSUFFICIENT-Scope Confound Monitoring

### Pre-Registered Indicators

The following indicators will be measured during C1 to determine whether C1 is primarily:

**(A) learning from engineering evidence** — or —
**(B) merely reacting to oracle limitations/errors**

| # | Indicator | Measures | How to interpret |
|---|-----------|----------|------------------|
| CM-1 | **Recovery from specific deterministic finding** | Engineer adds I/O delays when told SDC-005/006 | If Engineer adds delays → evidence is actionable (A). If no change → feedback may not be actionable (B). |
| CM-2 | **Correction of known SDC error** | Engineer removes clock on data port when told SDC-007 | If Engineer fixes → evidence is actionable (A). If no change → feedback not actionable (B). |
| CM-3 | **Repeated response to INSUFFICIENT feedback** | Engineer treats "INSUFFICIENT" as a signal to improve scope | If Engineer attempts scope improvement → reacting to limitation (B). If Engineer ignores scope message → scope not driving behavior. |
| CM-4 | **Unchanged behavior after non-actionable feedback** | Info-level findings (SDC-100 etc.) produce no candidate change | Expected — info findings are suggestions, not errors. No change is correct behavior. |
| CM-5 | **Candidate improvement attributable to exposed evidence** | Candidate changes between C0 and C1 that align with specific findings | If changes align with findings → evidence-driven (A). If changes are random → not evidence-driven. |
| CM-6 | **New errors introduced by feedback** | Candidate has errors in C1 that were not in C0 | If new errors → feedback may be confusing Engineer (B). If no new errors → feedback is at least not harmful. |
| CM-7 | **Convergence attempt** | Engineer iterates to try to reach VALIDATED | If iteration occurs → Engineer is using feedback constructively (A). If no iteration → feedback not driving improvement. |

### Measurement Protocol

These indicators will be measured by comparing:
- C0 raw_model_output.txt vs C1 raw_model_output.txt (per task)
- C0 evidence.json vs C1 evidence.json (per task)
- C0 candidate.json vs C1 candidate.json (per task)

**No indicator is decided in advance.** The goal is to define the measurement protocol before seeing C1 outcomes.

### Confound Verdict (Post-C1)

After C1 execution, the confound verdict will be one of:

1. **EVIDENCE-DRIVEN:** C1 shows improvement attributable to specific oracle findings → evidence is actionable
2. **LIMITATION-REACTIVE:** C1 shows behavior driven by INSUFFICIENT scope message rather than findings → confound present
3. **NO EFFECT:** C1 shows no improvement over C0 → feedback not actionable (valid falsification of H1 for C1)
4. **MIXED:** Some evidence-driven, some limitation-reactive → requires careful decomposition

**None of these verdicts is predetermined.** The measurement protocol is defined above; the verdict comes from the data.

---

## 7. Causal Isolation Audit

### Constants Between C0 and C1

| Constant | C0 Value | C1 Value | Verified |
|----------|----------|----------|----------|
| Benchmark | BENCH-002 v0.1 | BENCH-002 v0.1 | ✅ Frozen |
| Task order | BENCH2-001..006 | BENCH2-001..006 | ✅ Frozen |
| Model | MODEL-002 (opencode/muse-spark-1.2 NOT_EXPOSED) | MODEL-002 (same) | ✅ Frozen |
| Temperature | 0.0 | 0.0 | ✅ Frozen |
| Max tokens | 2048 | 2048 | ✅ Frozen |
| Prompt baseline | eger.prompt.v1 | eger.prompt.v1 | ✅ Frozen |
| Model-call budget | 5 | 5 | ✅ Frozen |
| Oracle | Ṛta v1.5.11 | Ṛta v1.5.11 | ✅ Frozen |
| Oracle configuration | custom_rules OFF | custom_rules OFF | ✅ Frozen |
| Termination budget | max_iterations=5, max_wall_clock=300s | Same | ✅ Frozen |
| Evaluator | Same scoring definitions | Same | ✅ Frozen |
| Information boundary | C0: no feedback | C1: text feedback only | ✅ Delta |
| Artifact schema | eger.candidate.v1, eger.evidence.v1 | Same | ✅ Frozen |
| Run manifest structure | Frozen schema | Same | ✅ Frozen |
| Subagents | 0 | 0 | ✅ Constant |
| Oracle call budget | 5 | 5 | ✅ Frozen |

### What Changes

| Change | C0 | C1 | Classification |
|--------|----|----|----------------|
| Text feedback | NOT PRESENT | PRESENT — oracle findings rendered as text | **SOLE INDEPENDENT VARIABLE** |

**No other changes are authorized.** If any proposed C1 implementation affects more than the declared independent variable, it REQUIRES EXPERIMENT CHANGE CONTROL (protocol §30).

---

## 8. Model Freeze Verification

### MODEL-002 Status: **FROZEN**

| Field | Value | Status |
|-------|-------|--------|
| Provider | opencode | FROZEN |
| Model | muse-spark-1.2-contributor-free | FROZEN |
| Version | NOT_EXPOSED | FROZEN (documented) |
| Temperature | 0.0 | FROZEN |
| Max tokens | 2048 | FROZEN |
| Timeout | 60s | FROZEN |
| Prompt | eger.prompt.v1 | FROZEN |
| Selection criteria | Non-performance (availability/interface) | FROZEN |

### Coding Model vs. Experimental Model

**The current OpenCode coding model (freebuff mimo 2.5) does NOT alter the C1 experimental model.**

MODEL-002 is frozen as `opencode/muse-spark-1.2-contributor-free`. The fact that the coding agent running this readiness review uses a different model is irrelevant to the experiment. The C1 Engineer model must be exactly MODEL-002.

**Do NOT modify MODEL-002.**

If MODEL-002 cannot be reproduced (e.g., provider unavailable), that is a READINESS BLOCKER — not a reason to substitute a different model.

---

## 9. Benchmark Freeze Verification

### BENCH-002 Status: **FROZEN v0.1**

| Field | Value | Status |
|-------|-------|--------|
| Tasks | BENCH2-001..006 | FROZEN |
| Task order | Frozen sequence | FROZEN |
| engineer_visible | 6 task files | FROZEN |
| evaluator_only | 6 expected answer files | FROZEN |
| Contamination | CLEAN | FROZEN |
| Held-out | true | FROZEN |

### Benchmark Exposure Record

BENCH-002 evaluator-only answers were exposed during EGER-GITHUB-001 (~8 minutes, public repository). Remediated to PRIVATE (EGER-GITHUB-002). For the current private research run, BENCH-002 retains its historical identity and exposure record.

**Do not:**
- Add tasks
- Remove tasks
- Reorder tasks
- Modify engineer-visible task definitions
- Modify evaluator-only expected answers
- Inspect evaluator-only answers

---

## 10. Oracle Boundary

### Ṛta Status: **EXTERNAL / READ-ONLY**

| Check | Status |
|-------|--------|
| Ṛta HEAD | 3b5c2f2 (unchanged) |
| Ṛta branch | main (unchanged) |
| Ṛta dirty count | 19 (unchanged) |
| EGER git ls-files rta paths | 0 |
| .gitignore excludes rta-constraint-intelligence/ | YES |
| rta_generate invoked | NO (0 hits) |

**No changes to rta-constraint-intelligence/ are authorized.**

If adapter behavior needs changing for C1:
1. Identify the change
2. Classify it
3. **DO NOT implement it in this prompt**
4. Record as EGER-CHANGE-### if material

---

## 11. Subagent Boundary

### C1 = **NO SPECIALIZED SUBAGENTS**

Per protocol §6, ARCH-002, and EGER-DEC-005:

- C0–C5 primary ablation uses exactly **one probabilistic reasoning component**
- Specialized subagents belong to **C6 engineering extension** only
- C6 is excluded from the primary causal experiment

**Do NOT introduce subagents into C1.**

---

## 12. Metrics Readiness

### Predeclared Metrics (protocol §15)

| Metric | Definition | C1 Measurability |
|--------|-----------|------------------|
| Artifact Reliability | SDC technically acceptable under deterministic oracle evaluation | ✅ Measurable — same oracle, same findings |
| Reasoning Reliability | Engineer responds appropriately to evidence | ✅ Measurable — compare C0 vs C1 candidate changes |
| Epistemic Reliability (EVR) | violations / attempted_epistemic_transitions | ⚠️ N/A for C1 — C1 has no L2 exposed; EVR measured from C3 onward |
| Convergence | VALIDATED + APPROVED within budget | ⚠️ Unlikely for C1 — INSUFFICIENT scope prevents VALIDATED; convergence requires FULL scope |
| Efficiency | model_calls, oracle_calls, wall_clock | ✅ Measurable |

### Unresolved Metric Definitions

**None.** All primary metrics are contractually defined (protocol §15). No new primary metrics are invented for C1.

### Secondary Exploratory Metrics (not primary)

If useful, the following may be recorded as SECONDARY EXPLORATORY METRICS:
- Number of findings addressed by Engineer
- Specific finding codes that drive candidate changes
- Whether INSUFFICIENT scope message appears in Engineer reasoning

These must not be promoted to primary metrics.

---

## 13. Reproducibility Readiness

### C1 Must Produce

| Artifact | Required | Schema |
|----------|----------|--------|
| Immutable run_id | ✅ | UUID per run |
| Run manifest | ✅ | Frozen schema (protocol §23) |
| Raw model output | ✅ | raw_model_output.txt |
| Candidate artifact | ✅ | eger.candidate.v1 |
| Raw oracle output | ✅ | raw_evidence.json |
| Normalized evidence | ✅ | eger.evidence.v1 |
| Deterministic hashes | ✅ | prompt_hash, output_hash, candidate_hash, evidence_hash |
| Configuration snapshot | ✅ | model config in manifest |
| Model configuration | ✅ | MODEL-002 in manifest |
| Benchmark/task identifier | ✅ | BENCH2-XXX in manifest |
| Text feedback log | ✅ | What text was injected into Engineer prompt |

### What Must NOT Happen

- No post-hoc repair
- No overwriting raw outputs
- No silent retries that alter the experiment
- No prompt tuning between tasks
- No model switching

---

## 14. Open Design Questions

| # | Question | Status | Impact |
|---|----------|--------|--------|
| ODQ-1 | **C1 text feedback format** — exact specification of what oracle output is rendered as text | **OPEN** | Must be resolved before C1 execution. See §4 for candidate designs. |
| ODQ-2 | **Text feedback injection point** — where in the prompt is text feedback inserted (after candidate? as system message? as separate turn?) | **OPEN** | Must be resolved before C1 execution. Affects prompt structure. |
| ODQ-3 | **Iteration protocol for C1** — does C1 allow multiple generate→validate cycles (like C4 routing), or is it single-shot like C0? | **OPEN** | Protocol §13 allows up to 5 iterations; C1 capability matrix doesn't explicitly add routing. Clarification needed. |
| ODQ-4 | **Whether INSUFFICIENT feedback is actionable** — the C0-R1 confound question | **OPEN** | Cannot be resolved before C1 execution. Monitored via indicators in §6. |

---

## 15. Required Change-Control Items

| Item | Classification | Action Required |
|------|---------------|-----------------|
| C1 text feedback format | OPEN DESIGN QUESTION | Must be defined before C1 execution. If material change to protocol §6, requires EGER-CHANGE-###. |
| C1 text feedback injection point | OPEN DESIGN QUESTION | Must be defined before C1 execution. |
| C1 iteration protocol | OPEN DESIGN QUESTION | Must be clarified before C1 execution. |

**No EGER-CHANGE-### records are required for this readiness review.** The open design questions are pre-execution decisions, not protocol mutations.

---

## 16. Blocking Issues

### BLOCKING

| # | Issue | Impact | Resolution |
|---|-------|--------|------------|
| B-1 | **C1 text feedback format not defined** | Cannot implement C1 runner without knowing what text to inject | Human researcher must select or define format before C1 execution |

### NON-BLOCKING

| # | Issue | Impact | Resolution |
|---|-------|--------|------------|
| NB-1 | C1 iteration protocol unclear | May affect runner implementation | Clarify before C1, but not a hard blocker if single-shot |
| NB-2 | BENCH-002 evaluator exposure | Does not affect C1 execution (private repository) | Documented; no action needed for C1 |
| NB-3 | Statistical power limited (6 tasks, 1 run) | Limits inference strength | Known limitation; documented in protocol §20, §27 |

### OPEN

| # | Issue | Impact | Resolution |
|---|-------|--------|------------|
| O-1 | INSUFFICIENT scope confound | May affect causal interpretation of C1 | Cannot be resolved before C1; monitored via §6 indicators |
| O-2 | Whether INSUFFICIENT feedback is actionable | Determines whether C1 tests evidence or limitations | Cannot be resolved before C1; monitored via §6 indicators |

---

## 17. C1 Readiness Verdict

```
C1 READINESS:    READY WITH EXPLICIT OPEN QUESTIONS

BLOCKING:        C1 text feedback format must be defined
NON-BLOCKING:    Iteration protocol, statistical power, benchmark exposure
OPEN:            Confound status, INSUFFICIENT actionability

RECOMMENDATION:  Human researcher defines C1 text feedback format,
                 then authorizes C1 execution.
```

**C1 is not ready for execution until ODQ-1 (text feedback format) is resolved.** Once resolved, C1 can proceed with the documented limitations and confound monitoring plan.

---

## Final Stop

This is a READ-ONLY readiness review. No code was changed. No benchmark was modified. No model was altered. No C1 was executed. No Git commits were made. No Ṛta was modified.

**STOP.** Awaiting human review and C1 text feedback format definition.
