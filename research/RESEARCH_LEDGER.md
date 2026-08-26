# EGER RESEARCH LEDGER

Chronological spine of EGER research. Every material entry: ID, type,
context/date (approximate where exact timestamps unavailable), purpose,
previous state, observation/decision, evidence, relationships, status.

**Classification tags used below** (contract §15): SDC=SOURCE-DERIVED CLAIM ·
AI=AGENT INFERENCE · RH=RESEARCH HYPOTHESIS · OBS=OBSERVATION ·
ER=EXPERIMENTAL RESULT (none exist yet) · C=CONCLUSION.
No ER entries exist as of EGER-P004. No experimental claims are made anywhere
in this ledger.

---

## 0. Provenance / Traceability Map

```
EGER Research Contract v0.1 → v0.2   (pre-history; canonical docx in workspace root)
    │
    ├── EGER-P001 (architecture discovery)
    │      └── EGER-ARCH-001  [SUPERSEDED for C0–C5]
    │             ├── EGER-DEC-001…004 (assigned in transcript; historical refs)
    │             ├── EGER-HYP-001     (retrospective ID)
    │             └── EGER-HYP-002     (retrospective ID)
    │
    ├── EGER-P002 (Ṛta read-only reconnaissance)
    │      ├── EGER-ORACLE-001
    │      ├── EGER-EVID-001 (static implementation evidence)
    │      └── EGER-GAP-001  (no run-provenance layer; runtime unverified)
    │
    ├── EGER-P003 (scientific architecture challenge)
    │      ├── EGER-ARCH-002  [CURRENT RECOMMENDATION]
    │      ├── EGER-DEC-005 (one probabilistic component C0–C5)
    │      ├── EGER-DEC-006 (rta_generate forbidden)
    │      └── EGER-DEC-007 (deterministic routing for C4)
    │
    └── EGER-P004 (traceability foundation)
           └── research/ canonical documents (this file set)
```

Reading path for a new researcher: `RESEARCH.md` → `PRINCIPLES.md` → this
ledger → `STATE.md` → supporting records (`architecture/`, `oracle/`,
`LITERATURE.md`).

---

## 1. Pre-history

| Field | Value |
|---|---|
| Artifact | EGER Research Contract v0.1 → v0.2 |
| Type | Scientific contract |
| Context | Authored before EGER-P001; v0.2 present in workspace as docx |
| Content | Working thesis, primary question, P1–P8, authority model, C0–C5, C6, integrity rules, freeze clause |
| Status | CANONICAL. Freeze acceptance not yet formally confirmed (open question). |

Literature synthesis that preceded the contract is recorded in
[`LITERATURE.md`](LITERATURE.md) (metadata verification pending).

---

## 2. EGER-P001 — Architecture Discovery

| Field | Value |
|---|---|
| ID / Date | EGER-P001 · ~2026-08-26 (exact time not recorded) |
| Type | Prompt / architecture discovery |
| Purpose | Determine minimum-sufficient OpenCode subagent architecture implementing EGER without violating contract v0.2 |
| Previous state | Contract only; no code, no config, no research docs; Ṛta known from proposal documents only [OBS] |
| Observation | Workspace contained literature PDFs + contracts only; no git; no OpenCode config [OBS]. Contract v0.2 extracted and read in full. |
| Decision | Produced **EGER-ARCH-001**: determinize Evidence/State/Authorization as non-LLM layers; three LLM roles (supervisor/proposer/analyst); typed artifact protocol; per-condition configs c0–c5; adapter-only Ṛta access |
| Evidence | Repository inspection findings recorded in the P001 response |
| Successor | Superseded FOR C0–C5 by EGER-ARCH-002 (see P003). Core deterministic-layer insight retained. |
| Status | COMPLETE; architecture SUPERSEDED FOR C0–C5 |

### Retrospectively assigned sub-records (canonical detail lives in chat transcript only)

- **EGER-DEC-001** [historical ref] Determinize-everything-possible axiom. Still in force; instantiation revised by DEC-005.
- **EGER-DEC-002** [historical ref] Ṛta accessed strictly via adapter. In force.
- **EGER-DEC-003** [historical ref] Per-condition config variants c0–c5. In force.
- **EGER-DEC-004** [historical ref] Critic agent deferred to C6. Extended by DEC-005 (analyst/supervisor also deferred).
- **EGER-HYP-001** [RH] Three of four authorities need no LLM to satisfy P7. Supported by design analysis; not experimentally tested.
- **EGER-HYP-002** [RH] Deterministic state validator catches most corruption classes without an LLM critic. Untested.

---

## 3. EGER-P002 — Ṛta Read-Only Reconnaissance

| Field | Value |
|---|---|
| ID / Date | EGER-P002 · 2026-08-26 |
| Type | Prompt / read-only oracle reconnaissance |
| Purpose | Verify actual Ṛta implementation vs proposal-document claims; identify EvidenceOracle interface candidates |
| Previous state | Ṛta known only from proposal docs (P001) |
| Constraint honored | Strictly read-only; no execution; no modification; pre-existing dirty git state documented and left untouched |
| Major observations | See [`oracle/EGER-ORACLE-001.md`](oracle/EGER-ORACLE-001.md): real Python implementation v1.5.11; frozen MCP server (8 tools); CLI with exit codes 0/1/2/3; structured JSON findings w/ stable rule codes + versioned semantic identity; machine-readable trust/scope model; declarative gate policies; no LLM dependency found in engine paths [OBS]; runtime behavior UNKNOWN |
| Decision | None (inspection). Produced EGER-ORACLE-001, EGER-EVID-001, EGER-GAP-001 |
| Status | ACCEPTED AS ORACLE RECONNAISSANCE. Ṛta modified: NO. |

---

## 4. EGER-P003 — Scientific Architecture Challenge

| Field | Value |
|---|---|
| ID / Date | EGER-P003 · 2026-08-26 |
| Type | Prompt / adversarial self-review |
| Purpose | Falsify and minimize EGER-ARCH-001; find smallest scientifically clean C0–C5 system using ORACLE-001 evidence |
| Previous state | ARCH-001 recommended as working architecture |
| Challenge outcome | ARCH-001 judged unnecessarily complex for C0–C5: analyst & supervisor LLM roles test no declared independent variable; agent count is not a contract §10 variable [AI→accepted on review criteria] |
| Decision | **Option C selected → EGER-ARCH-002**: ONE probabilistic component for C0–C5 + deterministic layers; specialized agents deferred to C6. Decisions DEC-005/006/007 recorded. |
| Evidence | Option A/B/C evaluation across 12 criteria; Ṛta capability mapping showing deterministic layers absorb analyst functions [OBS+AI] |
| Successor | EGER-ARCH-002 (current recommendation) |
| Status | RECOMMENDED / PENDING FORMAL IMPLEMENTATION AUTHORIZATION |

### EGER-DEC-005 — One probabilistic component for C0–C5

| Field | Value |
|---|---|
| Decision | C0–C5 uses exactly one LLM component ("eger-engineer"); Evidence (L1), Epistemic State (L2), Authorization (L3) are deterministic layers; specialized subagents appear only in C6 |
| Motivation | Variable isolation: conditions must differ ONLY in the manipulated mechanism; multi-agent coordination would be an uncontrolled compound treatment; I8 parsimony |
| Evidence | ORACLE-001: structured evidence + scope model make an interpreter-agent unnecessary; contract §10 independent variables exclude agent count [SDC+OBS] |
| Affected | EGER-ARCH-001 (superseded for C0–C5), all future c0–c5 configs |
| Supersedes | Instantiation of EGER-DEC-001's topology; extends EGER-DEC-004 |
| Status | ACCEPTED (as recommendation; pending review) |

### EGER-DEC-006 — rta_generate forbidden

| Field | Value |
|---|---|
| Decision | No EGER component may invoke Ṛta's generation capability; Evidence authority must not become Proposal authority |
| Motivation | P7 category purity; provenance laundering risk; C0 must be pure-LLM generation |
| Evidence | ORACLE-001 §15 analysis [AI] |
| Exceptions | None. Future exception requires EGER-CHANGE record defining a labeled fourth role |
| Status | ACCEPTED |

### EGER-DEC-007 — C4 routing is deterministic

| Field | Value |
|---|---|
| Decision | Evidence-conditioned routing (C4) = frozen versioned table keyed by finding codes (derived from `rta_rules()` catalog); driver consults table; LLM receives routed procedure as input |
| Motivation | An LLM router would inject a probabilistic decision layer inside the condition meant to isolate architectural routing |
| Evidence | Design analysis against contract variable list [AI] |
| Residual | LLM discretion in *executing* a routed procedure = bounded confounder, recorded per run |
| Status | ACCEPTED |

---

## 5. EGER-P004 — Research Traceability Foundation

| Field | Value |
|---|---|
| ID / Date | EGER-P004 · 2026-08-26 |
| Type | Prompt / controlled documentation implementation |
| Purpose | Convert chat-transcript research history into persistent, version-controllable research memory |
| Previous state | All P001–P003 history existed only as agent responses [GAP] |
| Action | Created `research/` canon: RESEARCH.md, PRINCIPLES.md, STATE.md, RESEARCH_LEDGER.md, LITERATURE.md + supporting records `architecture/EGER-ARCH-001.md`, `architecture/EGER-ARCH-002.md`, `oracle/EGER-ORACLE-001.md` |
| Constraints honored | No runtime implementation; no Ṛta modification; no scientific-contract change; no git initialization (not authorized); retrospective IDs explicitly marked |
| Limitation | Backfilled content derived from conversation transcripts; original prompts/responses not archived verbatim in-repo (recommended future improvement) |
| Status | COMPLETE within authorization scope |

---

## 5b. EGER-P005 — Version-Controlled Research Baseline

| Field | Value |
|---|---|
| ID / Date | EGER-P005 · 2026-08-26 19:12 IST |
| Type | Prompt / controlled repository initialization |
| Purpose | Establish first version-controlled research baseline; protect repo from Ṛta contamination |
| Pre-operation state | EGER_ROOT not a git repo; no `.gitignore`; research canon existed untracked; RTA_ROOT (`rta-constraint-intelligence/`) had own git repo (branch main @ 3b5c2f2, dirty) — untouched |
| Git initialization | `git init -b main` executed ONLY at EGER_ROOT after roots were identified |
| Boundary | `.gitignore` created with rule `rta-constraint-intelligence/` (exact discovered path); staged set verified free of any Ṛta path before commit |
| Secret check | One keyword hit verified false positive ("token & tool-call budgets" in ARCH-002); no secrets staged |
| Baseline commit | `6be23141785dce7c4a6b8bce0f390bad99b13c87` — "research: establish EGER v0.2 traceability baseline" — 11 files, 803 insertions |
| Files included | .gitignore; both contract DOCX (canonical authority, version-controlled); full research/ canon (5 canonical + ARCH-001 + ARCH-002 + ORACLE-001) |
| Files excluded | Entire Ṛta tree incl. its .git (ignored); 15 literature PDFs (untracked by design decision — sources not yet bibliographically verified; revisit under LIT work) |
| Safety verification | Ṛta modified NO · contract modified NO · implementation created NO · secrets committed NO · Ṛta tracked NO |
| Important distinction | **Version control established for research provenance. NOT EGER implementation completed.** No runtime exists. |
| Status | COMPLETE within authorization scope |

## 6. Standing rules for future entries

1. New material action ⇒ new ledger entry before or at the time of action.
2. Never delete or rewrite superseded entries; append status changes.
3. Tag every claim with a classification (SDC/AI/RH/OBS/ER/C).
4. Experiments (EXP-###) require manifests; results (RES-###) cite them;
   failures (FAIL-###) are mandatory, never optional.
5. Contract changes only via EGER-CHANGE-### with status PROPOSED until reviewed.
