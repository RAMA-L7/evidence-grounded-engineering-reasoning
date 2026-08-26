# EGER EvidenceOracle Contract — EGER-ORACLE-CONTRACT-001

| Field | Value |
|---|---|
| ID | EGER-ORACLE-CONTRACT-001 |
| Produced by | EGER-P007 (2026-08-26) |
| Type | Research specification — contract freeze |
| Inputs | EGER v0.2 · ARCH-002 · ORACLE-001 (static) · ORACLE-002 (runtime) |
| Status | FROZEN elements specified in §20; no implementation authorized |

> This contract defines the **EGER EvidenceOracle abstraction** (Layer B)
> that the future adapter must satisfy against the **native Ṛta interface**
> (Layer A), producing **normalized EvidenceArtifacts** (Layer C).
> It does not mirror every Ṛta feature; it exposes only what the science requires.

---

## 1. Purpose

Provide the deterministic evidence authority required by P1/P4/P6/P7
without collapsing proposal, evidence, knowledge, or authorization.
The oracle answers: *what does the deterministic checklist say about
this candidate artifact, within what declared scope, and with what
provenance?* — nothing more. It enables C0–C5 to vary only the
architectural mechanism, never the oracle semantics.

## 2. Authority Boundary

```
PROPOSAL (probabilistic, single engineer)
    ≠  EVIDENCE (deterministic EvidenceOracle — THIS CONTRACT)
    ≠  EPISTEMIC STATE (deterministic validator, L2)
    ≠  AUTHORIZATION (deterministic gate, L3)
```

The oracle MUST NOT generate hypotheses, assign final epistemic
truth, authorize commits, or convert UNKNOWN→VALIDATED. A probabilistic
component can request oracle execution; only the oracle process may
write RawEvidence/EvidenceArtifact content. The LLM must never
construct an authoritative EvidenceArtifact directly (see §22).

Core invariant (§4 restated): the adapter can **normalize evidence;
it cannot manufacture epistemic truth.**

## 3. Relationship to Ṛta

Ṛta `rta-constraint-intelligence` v1.5.11 @ `3b5c2f2` (branch `main`)
is the **external read-only oracle candidate** whose runtime surface
was characterized in ORACLE-002. EGER reaches it only through the
future adapter around its declared interface; Ṛta's source, schemas,
CLI, MCP, and .git remain untouched read-only subjects.

Pin per experiment series: `{oracle_name="Ṛta", version="1.5.11",
revision="3b5c2f2"}`. Changing any pin starts a new series.

## 4. Native Ṛta Interface vs EGER Contract

| Layer | Content | Example |
|---|---|---|
| **A — Native** | What Ṛta actually exposes | `check --json`, `analyze all --json`, MCP `tools/list` with 8 tools, `analysis_scope`, exit codes 0/1/2/3, snapshots/diffs/gate policies |
| **B — EGER Contract** | What EGER scientifically requires from any oracle | Minimal `validate` + `capabilities` + evidence schema declaration; optional enrichment ops |
| **C — EvidenceArtifact** | Normalized evidence object consumed by L2 | FindingArtifact + AnalysisScope + Provenance + OracleResult |

The adapter maps A→C through B. B must not automatically adopt every A
feature (e.g. HTML reports, lint auto-fix, `rta_generate`).

## 5. Required Operations

| Op | Required? | Definition | Why minimal |
|---|---|---|---|
| `validate(input)` | **REQUIRED** | Deterministic validation of one candidate SDC text (plus optional invocation_options: netlist/top only when the experiment declares netlist-aware mode — default off). Returns an OracleResult carrying RawEvidence OR a typed OracleFailure (never both). | The single oracle call underpinning C1–C5; all evidence originates here. Observed as `check --json` / MCP `rta_analyze` (EVID-003/006). |
| `capabilities()` | **REQUIRED** | Declaration of what the oracle CAN establish — rule catalog scope (`rta_rules()`), analysis_scope trust vocabulary, supported invocation_options. May be realized as static inputSchemas from MCP `tools/list` plus shipped catalog. | Enforces P6: without a declared scope the consumer cannot know what "no errors" did not check. |
| `evidence_schema()` | **REQUIRED (declarative)** | Machine-readable description of EvidenceArtifact / FindingArtifact / AnalysisScope shapes and `schema_version`. Not a runtime I/O call — a versioned schema document (this P007). | Lets experiments assert they consumed the same evidence vocabulary across conditions. |

`evidence_schema()` is satisfied by committing `EGER-SCHEMA-001`; a runtime
endpoint for it is optional.

## 6. Optional Operations

| Op | Status | Notes |
|---|---|---|
| `analyze_enriched` | OPTIONAL | Richer analysis (`analyze all`) producing clock_relations/interactions beyond core validation; available to C-language experiments that wish to exercise it, but not required for C0–C5 correctness. |
| `snapshot` / `diff` | OPTIONAL as oracle ops | Snapshots/diffs are **required for L3 gate** in EGER, but the gate — not the oracle contract — owns them. They may be implemented via oracle's snapshot/diff or via EGER's own RawEvidence comparison; deferred to adapter validation. |
| `gate_evaluate` | DEFERRED | Gate policy evaluation belongs to L3 authorization, not the Evidence authority. The oracle may expose gate policies; EGER's gate decides. |
| `lint --fix`, `convert`, `corners`, `web`, HTML reports | REJECTED | Not evidence-establishing for EGER's thesis; would change artifact identity or introduce presentation concerns. |

## 7. Capability Model

Capabilities describe **what the oracle can establish**, not what the design
guarantees. Minimal categories (extensible, additive only):

- `syntax_validation` — parses and structurally validates SDC
- `semantic_analysis` — rule checks (SDC-NNN catalog)
- `scope_classification` — trust-boundary assignment per construct
- `clock_analysis` — clock-relation extraction (via `analyze_enriched`)
- `constraint_readiness` — readiness signal (if gate uses it)

Unsupported: `netlist_analysis` is NOT claimed until netlist-aware mode is
explicitly exercised and ORACLE-002's remaining UNKNOWN resolved; claiming it
without evidence would violate P6. Future capability addition requires
`EGER-CHANGE-###` if it changes the science-facing vocabulary.

## 8. Evidence Scope Model

Preservation of Ṛta's trust boundary is **FROZEN**. Every EvidenceArtifact
carries a normalized `evidence_scope` derived losslessly from
`analysis_scope.status`:

| Normalized `evidence_scope` | Meaning | Source `analysis_scope.status` |
|---|---|---|
| `FULL` | Every construct fully analyzed within scope | `VALIDATED` |
| `PARTIAL` | Recognized constructs had ignored/unknown options (present but not value-analyzed) | `PARTIALLY_VALIDATED` |
| `INSUFFICIENT` | Evidence cannot be established without missing context (design/netlist) | `NETLIST_REQUIRED` |
| `UNSUPPORTED` | Input contains constructs outside oracle's recognized scope | `UNSUPPORTED` or `TCL_EXECUTION_REQUIRED` or `NOT_VALIDATED` |

Rules (FROZEN):
- Adapter MUST NOT upgrade scope (e.g. `NETLIST_REQUIRED` → `FULL`).
- `INSUFFICIENT` and `UNSUPPORTED` MUST NOT be interpreted as `FULL` or as
  engineering failure.
- `unknown_options` / `ignored_options` lists MUST be preserved alongside scope
  to satisfy P6.

## 9. Error Model

Distinct, non-overlapping categories (no silent promotion):

| OracleResult status | Meaning | Consumer handling |
|---|---|---|
| `SUCCESS` (with findings) | Oracle executed; evidence produced. `findings` may be empty (no issues). `evidence_scope` as above. | Forward to L2; may be engineering-valid or -invalid depending on findings |
| `INVALID_REQUEST` | Invocation malformed (bad input encoding, oversized, unknown policy). Corresponds to exit 2 semantics. | Do NOT treat as engineering failure; record as experiment input error |
| `ORACLE_FAILURE` | Tool crashed / engine error (exit 3, missing binary, etc.) | Do NOT treat as engineering failure or as evidence; mark `evidence_scope = null`, evidence absent |
| `INSUFFICIENT_EVIDENCE` | Sub-case of SUCCESS where `evidence_scope` ∈ {`INSUFFICIENT`,`UNSUPPORTED`} — oracle ran but cannot establish the queried property | Distinct from engineering INVALID; L2 may transition to UNKNOWN, never to VALIDATED |
| `ENGINEERING_FINDING` is not a top-level status — it is the content of findings inside `SUCCESS`. |

Invariant (FROZEN): `oracle_status = ORACLE_FAILURE` MUST NOT imply
`engineering_status = INVALID` unless independent evidence does.

## 10. Provenance Requirements

Every EvidenceArtifact (and its linked RawEvidence) MUST carry:

- REQUIRED: `oracle.name`, `oracle.version`, `oracle.revision` (commit)
- REQUIRED: `invocation` (operation, arguments, gate/policy name if any, `schema_version`)
- REQUIRED: `input_identity` (logical identifier, e.g. CandidateArtifact id / file name)
- REQUIRED: `input_hash` (SHA-256 of the exact input bytes)
- REQUIRED: `raw_output_hash` (SHA-256 of the raw oracle bytes)
- REQUIRED: `evidence_hash` (SHA-256 of the normalized EvidenceArtifact canonical JSON)
- REQUIRED: `output_path` (link to retained RawEvidence file)
- REQUIRED: `produced_at` (execution provenance timestamp — not semantic)
- OPTIONAL: runner hostname / Python version — only if needed for forensics; must not participate in semantic equality

Provenance answers: *what was checked, by what oracle, against what input,
under what invocation, what evidence was produced, what was not established,
can the evidence be independently re-identified?*

## 11. Determinism Requirements

- The oracle MUST be deterministic in the tested sense (byte-identical evidence
  for identical inputs under identical invocation and revision — EVID-005).
- The adapter MUST NOT inject nondeterminism (timestamps, random IDs, ordering)
  into normalized evidence.
- Hash equality of evidence implies byte equality of the checked input/output,
  NOT semantic correctness, NOT universal determinism, NOT engineering validity.
- Non-evidence metadata (`produced_at`, `runtime_ms` if retained) is excluded
  from canonical evidence hashing.

## 12. Normalization Rules

The future adapter MUST satisfy (scientifically justified):

| Rule | Requirement |
|---|---|
| A | Preserve evidence scope verbatim (no upgrades/downgrades). |
| B | Preserve finding `code/severity/message/line/line2/context` where emitted. |
| C | Preserve `analysis_scope` constructs, counts, unknown/ignored option lists. |
| D | Do not invent findings not present in RawEvidence. |
| E | Do not upgrade `UNKNOWN` / `INSUFFICIENT` scope to validated. |
| F | Do not convert `ORACLE_FAILURE` into engineering failure. |
| G | Preserve oracle name/version/revision on every artifact. |
| H | Preserve `input_hash` linkage to the exact checked bytes. |
| I | Preserve a link to RawEvidence (and its hash) from the normalized artifact. |
| J | Never invoke `rta_generate` from the Evidence path (DEC-006). |
| K | Never allow EvidenceOracle to authorize engineering-state commits (P7). |
| L | Never silently discard material evidence (all findings retained; filtering — if any — is an explicit L2/L3 decision with its own provenance). |

## 13. Raw Evidence Policy

```
RawEvidence (raw oracle stdout, pinned, hash-addressed)
      ↓  normalization
EvidenceArtifact (typed, hash-addressed, provenance-linked)
```

- **Both are retained** as separate artifacts under distinct hashes.
- RawEvidence is the reproducibility anchor; EvidenceArtifact is the
  consumable evidence for L2.
- RawEvidence is never destroyed because a normalized artifact exists.
- Retention cost: moderate (JSON files, compressible). Trivial relative to
  the value of being able to re-validate the normalization. Raw files are
  stored outside Ṛta (`evidence_store/` or ledger-linked paths), not inside
  the oracle repo.

## 14. rta_generate Boundary

FROZEN per EGER-DEC-006: NO EGER component on the Evidence path may invoke
`rta_generate` (or any MCP/domain tool that synthesizes SDC content). The
adapter MUST NOT expose a generation operation on this path. Any future
exception requires an `EGER-CHANGE-###` defining a labeled fourth role.

## 15. Epistemic Boundary

EvidenceArtifact ≠ EpistemicState.

- The oracle produces evidence; it does not perform epistemic transitions.
- The deterministic Epistemic State Manager (L2) decides transitions
  HYPOTHESIS → EVIDENCE_AVAILABLE → VALIDATED/REFUTED/UNKNOWN/AMBIGUOUS
  using EvidenceArtifact + scope + provenance as input.
- A failed/insufficient oracle result cannot alone author a transition;
  it can only support UNKNOWN or re-evaluation, never VALIDATED.

## 16. Authorization Boundary

EvidenceArtifact / EpistemicState ≠ Authorization.

- The oracle MUST NOT commit files, promote engineering state, or approve
  transitions.
- The deterministic gate (L3) decides commit permission from
  EvidenceArtifact + EpistemicState + RawEvidence hash + regression evidence.
- The gate is the **only** writer to the verified-engineering-state store.

## 17. C0–C5 Integration

| Condition | Oracle interaction | What changes |
|---|---|---|
| C0 | None | No feedback |
| C1 | `validate()` → RawEvidence rendered deterministically as plain text | Text serialization |
| C2 | `validate()` → EvidenceArtifact (structured) | Structured schema |
| C3 | EvidenceArtifact → L2 state journal | Externalized epistemic state ON |
| C4 | EvidenceArtifact/EpistemicState → deterministic routing table | Routing ON |
| C5 | EpistemicState → L3 gate | Authorization ON |

Oracle revision/configuration is **held constant** across C1–C5
(custom_rules OFF, same binary, same invocation defaults). Only the
architectural mechanism under study changes.

## 18. C6 Independence

The contract is **independent of agent count**: any number of future
specialized agents (C6, EGER-ARCH-002) consume the same EvidenceOracle
contract via the same adapter surface. `EvidenceArtifact ≠ agent memory.`
Adding agents must not change oracle semantics or evidence hashes.

## 19. Schema Versioning

- `schema_version` is mandatory on every EvidenceArtifact (and carried in
  Provenance).
- Initial version: `eger.evidence.v1` (frozen at P007).
- Backward compatibility: additive optional fields may be introduced as
  PROVISIONAL; required fields may not be removed without a major version bump.
- Breaking changes (required-field addition/removal, enum value change,
  semantics change) require a new major version and a migration entry in
  `EGER-SCHEMA-001`; previous artifacts remain immutable under their original
  version. Material changes require `EGER-CHANGE-###`.

## 20. Frozen / Provisional / Unknown / Deferred Matrix

| Element | Status | Evidence |
|---|---|---|
| Evidence scope levels (FULL/PARTIAL/INSUFFICIENT/UNSUPPORTED) + no-upgrade rule | **FROZEN** | ORACLE-001 trust model + EVID-006 (rta P006) |
| Exit code 0 (=evidence produced) / 1 (=validation errors in evidence) | **FROZEN** | EVID-004 runtime-observed |
| Exit 2 (=INVALID_REQUEST) / 3 (=ORACLE_FAILURE) semantics | **PROVISIONAL** | Documented in Ṛta; not triggered at runtime in P006 — not falsely upgraded |
| `rta_generate` prohibition (Rule J) and Rules A–L in §12 | **FROZEN** | DEC-006 + P7 |
| RawEvidence + normalized EvidenceArtifact dual retention (§13) | **FROZEN** | P8 reproducibility |
| Minimal ops `validate` + `capabilities` + declarative `evidence_schema` | **FROZEN** | Minimality argument against mirroring all Ṛta features |
| Hash trio (input/raw/normalized) and timestamp-as-provenance-only policy | **FROZEN** | P8 + EVID-005 |
| Enriched `analyze_enriched` / snapshot/diff / netlist-aware mode | **DEFERRED** | ORACLE-002 remaining unknowns |
| Large-design determinism beyond tested fixture | **UNKNOWN** | ORACLE-002 scope limitation (honest) |

## 21. Open Questions

1. `FindingArtifact.identity` emission paths for CLI vs MCP vs snapshot builders — is the richer `identity` field ever present on the adapter's chosen transport?
2. Exact `evidence_hash` canonicalization (ordering inside normalized JSON) — adapter must pin a canonical-json algorithm.
3. Netlist-aware `evidence_scope` resolution behavior when netlist IS supplied (P006 only exercised without-netlist path).
4. Readiness verdict enum values at runtime (key present; values not individually asserted in P006).

## 22. Non-Goals

The oracle does NOT attempt: STA/signoff equivalence; design-intent validation;
passing-judgment beyond its rule catalog; closed-form reliability scoring;
universal correctness for unsupported/partial constructs; networked/LLM reasoning.

---

*This contract will be rejected at implementation review if any element listed
as FROZEN above is violated by the future adapter without an approved
EGER-CHANGE-###.*
