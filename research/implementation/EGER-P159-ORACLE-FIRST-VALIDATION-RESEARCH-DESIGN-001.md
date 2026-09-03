# EGER-P159 — Oracle-First Validation Research Design

## Gate

P159 — Research Design / Assessment (No Implementation)

## Date

2026-09-03

## Purpose

Design and bound the next research phase: Oracle-first validation. Determine whether and how the EGER architecture's evidence-grounded revision pattern generalizes across independent deterministic evaluation authorities.

**No production code modified. No live model calls. No experiments. No historical artifacts changed.**

---

## 1. Executive Summary

P159 designs a research program to test whether EGER's evidence-grounded architecture generalizes beyond a single deterministic Oracle. The proposed research question (RQ-5) asks whether the architecture's revision pattern remains effective when the evaluation authority changes — not whether the same property is measured differently, but whether the architecture itself works across different engineering authorities.

The design identifies **OpenSTA** as a realistic second Oracle candidate: it is open-source, deterministic, evaluates a fundamentally different engineering property (timing closure vs. constraint quality), and can be invoked through the existing `OracleAdapter` abstraction with a new adapter implementation. The experiment would compare architecture behavior (revision convergence, evidence utilization, verification correctness) across Oracle A (Ṛta — constraint quality) and Oracle B (OpenSTA — timing analysis), using the same tasks, same agent, same EGER architecture.

The key scientific advantage of Oracle-first validation is that it separates **architecture quality** from **agent quality** — a finding that generalizes across evaluation authorities demonstrates that the architecture pattern is not an artifact of one specific Oracle's behavior.

Decision: **PROCEED TO ORACLE PILOT** — with bounded scope.

---

## 2. Research Motivation

The EGER project has completed:

- Architecture discovery (C0–C1/C2, RQ-4)
- Architecture implementation (P138–P144)
- Architecture validation (P145)
- Engineering hardening (P149–P158)

The natural next question is whether the architecture **generalizes**. The project is transitioning from:

```
architecture discovery
        ↓
architecture implementation
        ↓
engineering hardening
        ↓
research generalization
```

The important conceptual distinction is:

```
Agent quality
    ≠
Oracle quality
    ≠
EGER architecture quality
```

The experiment must be designed so these factors are not accidentally conflated.

---

## 3. Existing Research State — Frozen

```
C0: ESTABLISHED          — LLM-only baseline
C1: ESTABLISHED          — Structured evidence activates revision
C2: PARTIALLY SUPPORTED  — Evidence normalization implemented
C3: NOT JUSTIFIED        — Prompt design is more parsimonious
C4: DEFERRED             — Engineering choice, not experiment
C5: DEFERRED             — Engineering choice, not experiment

RQ-4: CLOSED             — Broad framing is a behavioral signal, not proven causality
```

These conclusions are NOT under review. The next research phase must build on existing evidence rather than revisit it.

---

## 4. Candidate RQ-5

### Proposed Research Question

> **RQ-5: To what extent does the evidence-grounded EGER architecture generalize across independent deterministic evaluation authorities within VLSI engineering tasks?**

### RQ-5 Validity Assessment

| Criterion | Assessment |
|-----------|-----------|
| Sufficiently precise? | YES — specifies architecture generalization, not agent performance |
| Experimentally testable? | YES — requires at least two independent Oracles with compatible adapters |
| Distinct from RQ-4? | YES — RQ-4 addressed task framing; RQ-5 addresses Oracle independence |
| Supported by existing architecture? | YES — OracleAdapter abstraction already supports Oracle substitution |
| Meaningful claim? | YES — architecture generalization is a prerequisite for multi-Oracle deployment |
| What it could NOT support? | Claims about agent quality, specific Oracle performance, or domain generalization beyond VLSI |

### Refined RQ-5 (if needed)

The proposed RQ-5 is sufficiently precise as stated. No refinement needed for the pilot design.

---

## 5. Primary Research Objective

Design an experiment that changes the **evaluation authority** while keeping the rest of the EGER process as stable as practical.

Conceptually:

```
Same task
Same agent
Same EGER architecture
Same revision protocol
Same verification policy
        ↓
Oracle A (Ṛta — constraint quality)
```

versus:

```
Same task
Same agent
Same EGER architecture
Same revision protocol
Same verification policy
        ↓
Oracle B (OpenSTA — timing analysis)
```

The objective is to determine whether the architecture's evidence-grounded revision pattern remains useful when the deterministic evaluation authority changes.

---

## 6. Oracle Selection Criteria

### Required Properties

| Criterion | Description |
|-----------|------------|
| Determinism | Given the same relevant inputs and environment, the Oracle produces reproducible results |
| Independence | The Oracle does not simply reproduce Ṛta's implementation or logic |
| Authority clarity | The Oracle answers a clearly defined engineering question |
| Evidence production | The Oracle produces structured or structurally normalizable findings that EGER can consume |
| Boundary compatibility | The Oracle can be used through OracleAdapter without changing the EGER core architecture |
| Failure observability | Oracle execution failures are distinguishable from valid engineering findings |
| Reproducibility | The experiment records enough information to reproduce or audit results |

### Important Constraint

Different Oracles are NOT interchangeable correctness authorities. The architecture should generalize at the **Oracle boundary**, not by pretending all Oracles produce one common notion of correctness.

---

## 7. Oracle Candidate Assessment

### Oracle A — Ṛta (Baseline)

| Property | Assessment |
|----------|-----------|
| What it evaluates | SDC constraint quality: syntax, semantics, completeness, best practices |
| What evidence it produces | ERROR/WARNING/INFO findings with severity, code, message, location |
| Authority boundary | Deterministic subprocess, produces EvidenceArtifact |
| Why it serves as baseline | Established, validated, 734 tests pass, architecture proven |
| Status | **READY** |

### Oracle B — OpenSTA (Candidate)

| Property | Assessment |
|----------|-----------|
| What it evaluates | Static timing analysis: setup/hold violations, clock relationships, path timing |
| What evidence it produces | Timing violations, slack values, path reports — normalizable to ERROR/WARNING/INFO |
| Authority boundary | Deterministic (given same netlist + constraints + libraries), CLI-invocable |
| Independence from Ṛta | FUNDAMENTALLY DIFFERENT — evaluates timing closure, not constraint syntax/semantics |
| Input requirements | Synthesized netlist (Verilog), SDC constraints, technology library (.lib/.lef) |
| Determinism | DETERMINISTIC for same inputs (same netlist + same .lib + same SDC → same timing) |
| Determinism caveat | Requires technology library files — environment-dependent but controllable |
| Status | **CONDITIONALLY SUITABLE** — requires netlist + technology library for each task |

### Oracle C — Synthesis/Elaboration Checker (Future Option)

| Property | Assessment |
|----------|-----------|
| What it evaluates | RTL elaboration, structural correctness, design rule compliance |
| Candidate tools | Yosys (open-source), commercial synthesis tools |
| Independence from Ṛta | DIFFERENT — evaluates design structure, not timing or constraints |
| Status | **FUTURE OPTION** — viable but less accessible than OpenSTA for pilot |

### Oracle D — Formal Property Checker (Future Option)

| Property | Assessment |
|----------|-----------|
| What it evaluates | Formal verification of design properties (assertions, invariants) |
| Candidate tools | SymbiYosys (open-source), commercial formal tools |
| Independence from Ṛta | FUNDAMENTALLY DIFFERENT — formal verification vs. constraint checking |
| Status | **FUTURE OPTION** — requires formal property specifications, higher barrier |

### Oracle E — Lint/Static Analysis (Future Option)

| Property | Assessment |
|----------|-----------|
| What it evaluates | Code quality, naming conventions, structural lint rules |
| Candidate tools | Verilator lint, commercial lint tools |
| Independence from Ṛta | DIFFERENT but adjacent — both are static checks, not behavioral analysis |
| Status | **FUTURE OPTION** — lower scientific value for generalization study (too similar to Ṛta in nature) |

### Recommendation

**Use Oracle A (Ṛta) as baseline and Oracle B (OpenSTA) as the independent Oracle for the pilot.** This pairing maximizes:
- Property independence (constraint quality vs. timing closure)
- Open-source availability
- Deterministic execution
- Evidence normalizability
- Scientific clarity (clearly different evaluation authorities)

---

## 8. Oracle Authority Separation

### Critical Invariant

Different Oracles are not interchangeable correctness authorities. The architecture should generalize at the **Oracle boundary**, not by pretending all Oracles produce one common notion of correctness.

For example:

```
Ṛta → constraint-quality evidence
OpenSTA → timing-analysis evidence
Synthesis tool → elaboration/structural evidence
Formal tool → property-verification evidence
```

These are different engineering authorities. The research question is whether the **architecture pattern** (proposal → evidence → revision → verification) works across these different authorities — not whether they agree on correctness.

### What Generalization Means Here

The architecture generalizes if:
1. The same revision loop works with a different Oracle
2. Evidence from a different Oracle still activates meaningful revision
3. VerificationGate still makes correct decisions given different evidence types
4. Provenance still captures the complete run trace
5. No architectural changes are required beyond Oracle-specific adaptation

The architecture does NOT generalize if:
1. The revision loop requires Oracle-specific modifications
2. Evidence from a different Oracle cannot be normalized
3. VerificationGate requires Oracle-specific policy changes
4. Provenance tracking breaks with different evidence types
5. Core EGER contracts must change

---

## 9. Experimental Variables

### Controlled Variables

| Variable | Control Method |
|----------|---------------|
| Task definition | Same TaskDefinition for both Oracles |
| Initial candidate | Same initial SDC for both Oracles |
| Agent/model | Same LLM, same temperature, same provider |
| Prompt protocol | Same PromptBuilder, same templates |
| Revision budget | Same RevisionConfig (max_iterations, max_total_calls) |
| EGER architecture | Identical code path (only Oracle changes) |
| EvidenceNormalizer | Same normalizer (Oracle-specific adapter produces compatible input) |
| VerificationGate | Same gate policy (all ERROR findings resolved → ACCEPT) |
| ProvenanceTracker | Same tracking |
| Evaluation metrics | Same metrics for both conditions |

### Manipulated Variable

| Variable | Values |
|----------|--------|
| Oracle identity | Oracle A (Ṛta — constraint quality) vs. Oracle B (OpenSTA — timing analysis) |

### Observed Variables

| Variable | Measurement |
|----------|------------|
| Initial proposal validity | ERROR count from Oracle before revision |
| Number of Oracle findings | Total findings per iteration |
| Finding severity distribution | ERROR / WARNING / INFO counts |
| Revision success | ERROR count reduction per iteration |
| Final acceptance | ACCEPT / REJECT / INCOMPLETE |
| Number of iterations | Iterations before termination |
| Number of model calls | Total LLM invocations |
| Unresolved findings | Findings remaining at termination |
| Oracle failures | ORACLE_FAILURE / TIMEOUT count |
| Verification outcome | VerificationResult for each run |
| Evidence utilization | Whether evidence findings were addressed by LLM |
| Failure mode | Terminal reason distribution |

---

## 10. Experimental Unit

The appropriate unit of analysis is:

```
task × Oracle × run
```

### Pilot Design

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Number of tasks | 3–5 | Minimum for observing pattern; pilot scope |
| Repeated runs per task | 1 (deterministic Oracle) | Oracle is deterministic; LLM is stochastic but temperature=0.0 |
| Oracle evaluations per task | 2 (Ṛta + OpenSTA) | Primary comparison |
| Total runs | 6–10 | 3–5 tasks × 2 Oracles |
| LLM repetitions | Optional (same task, same Oracle, different LLM samples) | If needed to assess LLM stochasticity |

### Task Selection Criteria

Tasks should:
- Have a clear engineering objective (produce a valid SDC)
- Produce a candidate artifact (SDC text)
- Be evaluatable by both Oracles (Ṛta checks constraint quality; OpenSTA checks timing)
- Expose meaningful failure evidence from both Oracles
- Permit controlled revision
- Avoid dependence on undocumented human judgment

### Critical Distinction: Same-Property vs. Cross-Property Tasks

**Same-property tasks**: Tasks where both Oracles evaluate the same property (e.g., both check constraint quality). This is NOT the primary research design — it tests Oracle interchangeability, not architecture generalization.

**Cross-property tasks**: Tasks where each Oracle evaluates a different property (Ṛta checks constraints, OpenSTA checks timing). This IS the primary design — it tests whether the architecture pattern works across different evaluation authorities.

The pilot should use **cross-property tasks** as the primary design, with same-property tasks as a secondary comparison if feasible.

---

## 11. Task Selection Framework

### VLSI Task Categories

| Category | Description | Ṛta Evaluates | OpenSTA Evaluates | Suitable? |
|----------|------------|--------------|-------------------|-----------|
| Simple clock + I/O | Single clock, basic I/O delays | Constraint completeness | Setup/hold timing | YES |
| Multi-clock | Multiple clock domains | Clock relationship constraints | Cross-domain timing | YES |
| Generated clocks | PLL/divider-derived clocks | Generated clock constraints | Derived clock timing | CONDITIONAL — requires netlist |
| False paths | Multi-cycle paths, async crossings | False path constraints | Timing exceptions | CONDITIONAL — requires netlist |
| Complex datapath | Multi-stage pipelines | Pipeline constraints | Path timing analysis | CONDITIONAL — requires netlist |

### Netlist Requirement

OpenSTA requires a synthesized netlist (Verilog) and technology library (.lib/.lef). This is a significant practical constraint.

**Options for the pilot:**
1. Use simple designs with freely available netlists (e.g., OpenCores)
2. Create minimal synthetic netlists (small Verilog modules + generic .lib)
3. Use OpenSTA in a mode that evaluates constraint structure without full timing (if available)

**Recommended**: Option 2 — minimal synthetic netlists. This ensures:
- Deterministic execution
- Controlled complexity
- Freely available (no licensing issues)
- Reproducible

---

## 12. Experimental Protocol

### Phase 1: Oracle Adapter Development (Implementation Gate)

Before the experiment, develop:

1. **OpenSTAAdapter** — implements the OracleAdapter interface for OpenSTA
   - Takes: SDC text (candidate) + netlist + technology library
   - Produces: OracleResult (success with timing findings, or failure)
   - Deterministic: given same inputs, produces same output

2. **OpenSTA EvidenceNormalizer** — or extend existing normalizer
   - Maps OpenSTA timing violations to Finding severity (ERROR for violations, WARNING for near-miss, INFO for clean paths)
   - Produces compatible EvidenceArtifact

3. **OpenSTA TaskDefinition extension** — or use separate task configuration
   - Adds: netlist_path, technology_library_path, clock_port, clock_period
   - These are task-level configuration, not model-facing

### Phase 2: Pilot Execution (Experiment Gate)

For each task × Oracle combination:
1. Create TaskDefinition (with Oracle-specific config)
2. Run EGERPipeline with Oracle A (Ṛta)
3. Capture full results (run_record, verification_result, provenance)
4. Run EGERPipeline with Oracle B (OpenSTA)
5. Capture full results
6. Compare architecture behavior metrics

### Phase 3: Analysis (Analysis Gate)

Analyze:
- Architecture behavior across Oracles
- Revision convergence patterns
- Evidence utilization
- Verification correctness
- Failure modes
- Provenance completeness

---

## 13. Metrics

### Agent Behavior Metrics

| Metric | Description | Measurement |
|--------|------------|------------|
| Initial proposal quality | ERROR count before revision | Oracle findings at iteration 0 |
| Revision behavior | ERROR count change per iteration | Δ(ERROR) per iteration |
| Revision convergence | Whether ERROR count decreases monotonically | Boolean per run |
| Number of attempts | Iterations before termination | Integer |

### Oracle Behavior Metrics

| Metric | Description | Measurement |
|--------|------------|------------|
| Deterministic execution | Same inputs → same outputs | Hash comparison across repeated runs |
| Finding completeness | Whether Oracle identifies relevant issues | Manual assessment per task |
| Oracle failure rate | ORACLE_FAILURE / TIMEOUT count | Count per condition |
| Evidence structure | Normalizability of Oracle output | Success rate of EvidenceNormalizer |

### EGER Architecture Metrics

| Metric | Description | Measurement |
|--------|------------|------------|
| Evidence-to-revision linkage | Whether LLM addresses Oracle findings | Finding addressed / finding total |
| Revision convergence | Whether iterations reduce ERROR count | Δ(ERROR) across iterations |
| Verification correctness | Whether VerificationGate decision matches evidence | Decision vs. evidence agreement |
| Fail-closed behavior | Whether ambiguous states produce REJECT | Count of REJECT for ambiguous evidence |
| Provenance completeness | Whether run trace is reconstructable | Provenance chain completeness check |
| Architecture compatibility | Whether EGER works without code changes | Boolean: same EGER path for both Oracles |

### Do NOT Use These Metrics

| Metric | Why Not |
|--------|---------|
| "EGER score" | Collapses agent/oracle/architecture into one number — confounds variables |
| "Agent improvement" | Not the research question — architecture generalization is |
| "Oracle agreement" | Oracles evaluate different properties — agreement is meaningless |
| "Task completion rate" | Depends on Oracle definition of "complete" — not comparable |

---

## 14. Success / Failure Criteria

### Strong Generalization

The same architecture pattern works across substantially different deterministic evaluation authorities with only Oracle-specific adapter/normalization changes.

**Evidence**: EGER pipeline runs successfully with both Oracles. Revision loop converges for both. VerificationGate makes correct decisions for both. No architectural changes required beyond Oracle adapter.

### Partial Generalization

The architecture works, but substantial Oracle-specific adaptation is required.

**Evidence**: EGER pipeline runs with both Oracles, but requires Oracle-specific changes to EvidenceNormalizer, VerificationGate, or revision-loop logic.

### Limited Generalization

The architecture works only for a narrow class of deterministic Oracles.

**Evidence**: EGER works with OpenSTA but not with a third Oracle, or works only when the Oracle produces evidence in a format very similar to Ṛta's.

### Failure to Generalize

The architecture's core contracts or control flow require fundamental changes for independent Oracles.

**Evidence**: Core EGER contracts (EvidenceArtifact, Finding, VerificationResult) must change. Revision loop requires Oracle-specific branching. VerificationGate requires Oracle-specific policy.

---

## 15. Reproducibility Requirements

### Minimum Research Artifact Package

For each experimental run, capture:

| Artifact | Format | Required? |
|----------|--------|----------|
| TaskDefinition | JSON (to_dict) | YES |
| Initial candidate SDC | Text | YES |
| Oracle identity/version | String | YES |
| Oracle input artifacts | File paths + hashes | YES (netlist, .lib for OpenSTA) |
| RevisionConfig | JSON (to_dict) | YES |
| PromptRequest metadata | prompt_hash, iteration | YES |
| CandidateArtifact(s) | JSON (to_dict) per iteration | YES |
| EvidenceArtifact(s) | JSON (to_dict) per iteration | YES |
| VerificationResult | JSON (to_dict) | YES |
| RunRecord | JSON (to_dict) | YES |
| Provenance reconstruction | JSON (from reconstruct_run()) | YES |
| Model/provider metadata | From CandidateArtifact.provision | YES |
| Software version | EGER commit hash | YES |
| Oracle version | From Oracle provenance | YES |
| Environment metadata | Python version, OS | YES |

### What NOT to Capture (per P157)

| Artifact | Rationale |
|----------|-----------|
| LLM prompt text | Deterministic from inputs; only hash needed |
| Raw Oracle stdout | Already captured in evidence_hash |
| Process state | Internal to EGER |

### Cross-Oracle Comparison Package

For comparing Oracle A vs Oracle B runs on the same task:

| Comparison | Method |
|-----------|--------|
| Same initial candidate | Identical CandidateArtifact for both Oracles |
| Same revision protocol | Identical RevisionConfig |
| Same agent behavior | Same LLM, same temperature |
| Oracle-specific evidence | Different EvidenceArtifact (different findings, different severity distribution) |
| Architecture behavior | Same pipeline path, same verification logic |
| Result comparison | RunRecord comparison (iterations, calls, termination) |

---

## 16. Security and Authority Boundaries

### Proposal Authority

- LLM proposes candidates
- LLM must not self-verify, declare acceptance, override Oracle evidence, or bypass VerificationGate
- **Status**: PRESERVED — no change from current architecture

### Evidence Authority

- Oracle produces engineering evidence
- EGER must not turn Oracle output into model authority
- **Status**: PRESERVED — OracleAdapter → EvidenceNormalizer → EvidenceArtifact

### Decision Authority

- VerificationGate makes acceptance/rejection decisions
- VerificationGate must remain the sole authority regardless of Oracle identity
- **Status**: PRESERVED — gate.py is the only ACCEPT/REJECT location

### Provenance

- Records what happened but does not authorize decisions
- **Status**: PRESERVED — ProvenanceTracker unchanged

### No Future Oracle May Bypass the Verification Boundary

无论 Oracle B produces什么evidence, VerificationGate remains the sole decision authority. This is an architectural invariant that must hold across all Oracles.

---

## 17. Threats to Validity

### Construct Validity

**Are we actually measuring Oracle-independent architectural generalization?**

| Threat | Mitigation |
|--------|-----------|
| Different Oracles produce different difficulty levels | Measure revision convergence independently of absolute performance |
| Task design favors one Oracle | Use tasks where both Oracles can produce meaningful evidence |
| Evidence normalization masks Oracle differences | Compare raw Oracle findings separately from normalized evidence |

### Internal Validity

**Could differences be caused by confounding factors?**

| Threat | Mitigation |
|--------|-----------|
| Oracle difficulty differences | Control: same task, same initial candidate |
| Task difficulty differences | Control: same task for both Oracles |
| Prompt wording differences | Control: same PromptBuilder, same templates |
| Model behavior differences | Control: same LLM, same temperature, same provider |
| Tool failures | Record and classify all failures |
| Environment differences | Same environment for both Oracles |
| Netlist availability | Use minimal synthetic netlists for OpenSTA |

### External Validity

**Does a small number of VLSI Oracles support claims beyond the studied domain?**

| Threat | Mitigation |
|--------|-----------|
| VLSI-specific architecture | Acknowledge limitation; claim is about VLSI engineering tasks |
| Limited Oracle count | Pilot uses 2 Oracles; future work can add more |
| Synthetic netlists | Acknowledge limitation; real designs may behave differently |

### Confounding

**Especially distinguish:**

| Factor | How Distinguished |
|--------|------------------|
| Oracle differences | Same task, different Oracle → Oracle-specific effects |
| Task differences | Different tasks, same Oracle → task-specific effects |
| Agent differences | Same task, same Oracle, different LLM → agent-specific effects |
| EGER architecture effects | Same task, same Oracle, same LLM, different architecture → architecture effects (not tested in pilot) |

### Tool/Version Effects

| Factor | Control |
|--------|---------|
| Oracle version | Pin versions: Ṛta 3b5c2f2, OpenSTA specific commit |
| Libraries | Pin technology library version |
| Runtime environment | Same Python, same OS, same machine |
| Configuration | Same RevisionConfig for both Oracles |
| Deterministic settings | temperature=0.0, no random seed needed |

---

## 18. Architectural Impact Assessment

### Current Architecture Support for Oracle Substitution

The existing architecture already supports Oracle substitution through:

```
OracleAdapter (eger/oracle/adapter.py)
    ↓
OracleResult (success + EvidenceArtifact | failure + OracleFailure)
    ↓
EvidenceNormalizer (eger/evidence/normalizer.py)
    ↓
EvidenceArtifact (eger/evidence/schemas.py)
```

### What a New Oracle Requires

| Component | Change Required? | Description |
|-----------|-----------------|-------------|
| TaskDefinition | EXTEND (optional) | Add Oracle-specific config (netlist_path, .lib_path) — not core contract change |
| OracleAdapter | NEW IMPLEMENTATION | OpenSTAAdapter implementing same interface |
| EvidenceNormalizer | EXTEND or ADAPT | Map OpenSTA findings to Finding schema |
| EvidenceArtifact | NO CHANGE | Same contract — findings, summary, scope |
| Finding | NO CHANGE | Same severity vocabulary (error/warning/info) |
| RevisionController | NO CHANGE | Same loop logic |
| VerificationGate | NO CHANGE | Same policy (zero ERROR findings → ACCEPT) |
| ProvenanceTracker | NO CHANGE | Same event chain |
| PromptBuilder | NO CHANGE | Same prompt construction |
| CandidateArtifact | NO CHANGE | Same contract |

### Desired Result

> New deterministic Oracles should primarily require Oracle-specific adapter/normalization, not redesign of the EGER control architecture.

### If the Current Design Does NOT Support It

Document the gap. Specific failure modes to watch for:

1. EvidenceNormalizer cannot normalize OpenSTA output → evidence format issue, not architecture issue
2. VerificationGate rejects valid OpenSTA evidence → policy issue, not architecture issue
3. RevisionController requires Oracle-specific logic → architecture generalization failure
4. ProvenanceTracker breaks with different evidence types → architecture generalization failure

---

## 19. Future Cross-Agent Extension

### Why Oracle-First Before Agent-First

The scientific advantage of Oracle-first validation:

1. **Controls agent quality**: Same LLM for both Oracles eliminates agent as a confound
2. **Tests architecture directly**: If the architecture works across Oracles with the same agent, the architecture pattern is validated independently of agent behavior
3. **Simpler experiment**: One agent, two Oracles is simpler than two agents, one Oracle
4. **Clearer claim**: "Architecture generalizes across evaluation authorities" is a cleaner claim than "Architecture works with different agents"

### Desired Sequence

```
Phase 1
Same agent + different Oracles
    ↓
Phase 2
Different agents + same Oracle(s)
```

Phase 2 would test whether the architecture benefits different agents equally — a separate and complementary research question.

---

## 20. Decision Gate

### **DECISION A — PROCEED TO ORACLE PILOT**

**Rationale:**

1. RQ-5 is sufficiently precise and experimentally testable
2. At least one independent Oracle (OpenSTA) is realistically available and open-source
3. Experimental variables are controllable (same task, same agent, different Oracle)
4. Evidence can be normalized (OpenSTA output is structured, normalizable to Finding schema)
5. The architecture can be tested without major redesign (OracleAdapter abstraction already exists)
6. The pilot is bounded (3–5 tasks, 2 Oracles, ~10 runs)
7. The scientific value is clear (architecture generalization across evaluation authorities)

**Conditions for proceeding:**

- Develop OpenSTAAdapter (implementation gate)
- Create minimal synthetic netlist + technology library for pilot tasks
- Execute pilot with bounded scope
- Analyze results before scaling

---

## 21. Recommended Next Gate

**P160 — OpenSTA Oracle Adapter Design**

Before implementing the adapter, design:
- OpenSTAAdapter interface
- OpenSTA evidence normalization strategy
- OpenSTA task configuration extension
- Minimal netlist/library requirements
- Deterministic execution verification plan

This is an implementation design gate before any code changes.

---

## 22. Explicit Non-Goals

The following are explicitly NOT part of P159 or the Oracle-first validation:

1. **Reopening RQ-4** — Research is closed
2. **Changing C0–C5 conclusions** — Preserved as-is
3. **Implementing cross-agent experiments** — Phase 2, not now
4. **Testing agent quality** — Architecture generalization, not agent performance
5. **Creating a universal engineering score** — Different Oracles measure different things
6. **Proving Oracle interchangeability** — Oracles are NOT interchangeable; architecture should work across different authorities
7. **Modifying the EGER core architecture** — Test existing architecture, don't redesign it
8. **Implementing provenance persistence** — Deferred per P157
9. **Commercial tool integration** — Open-source only for reproducibility
10. **Scaling beyond pilot** — Bounded scope first

---

## 23. C0–C5 Preservation

```
C0: ESTABLISHED          — Unchanged
C1: ESTABLISHED          — Unchanged
C2: PARTIALLY SUPPORTED  — Unchanged
C3: NOT JUSTIFIED        — Unchanged
C4: DEFERRED             — Unchanged
C5: DEFERRED             — Unchanged

RQ-4: CLOSED             — Unchanged
```

The Oracle-first validation study does not alter any research conclusions. It tests a new research question (RQ-5) that is independent of the C0–C5 program.

---

## 24. Ṛta Boundary

```
Ṛta = external deterministic Oracle
```

| Check | Status |
|-------|--------|
| Ṛta remains Oracle A (baseline) | PRESERVED |
| OpenSTA is Oracle B (independent) | NEW — does not modify Ṛta |
| EGER invokes both Oracles through adapter | PRESERVED — same abstraction |
| Neither Oracle modifies EGER | PRESERVED |
| EGER does not embed AI into either Oracle | PRESERVED |
| Oracle authority boundary preserved | PRESERVED |

---

```
P159 COMPLETE

RESEARCH-DESIGN SCOPE: PASS
RQ-5 ASSESSMENT: SUFFICIENTLY PRECISE, EXPERIMENTALLY TESTABLE
ORACLE SELECTION ASSESSMENT: OpenSTA — CONDITIONALLY SUITABLE
ARCHITECTURE GENERALIZATION: TESTABLE WITHOUT MAJOR REDESIGN
EXPERIMENTAL DESIGN: PASS
REPRODUCIBILITY DESIGN: PASS
AUTHORITY BOUNDARY: PASS
THREATS-TO-VALIDITY REVIEW: PASS

DECISION: PROCEED TO ORACLE PILOT

IMPLEMENTATION CHANGES: NONE

TESTS: 734/734 PASS (no changes)

ṚTA CHANGES: NONE
HISTORICAL RESEARCH CHANGES: NONE
RESEARCH STATE CHANGES: NONE

RQ-4: CLOSED

PRIMARY RECORD: research/implementation/EGER-P159-ORACLE-FIRST-VALIDATION-RESEARCH-DESIGN-001.md
CHANGE-CONTROL RECORD: research/implementation/EGER-CHANGE-029.md

NEXT GATE: P160 — OpenSTA Oracle Adapter Design

STOP: NO EXPERIMENTAL IMPLEMENTATION PERFORMED
```
