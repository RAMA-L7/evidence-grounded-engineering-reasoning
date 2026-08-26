# EGER Typed Artifact Schemas — EGER-SCHEMA-001

| Field | Value |
|---|---|
| ID | EGER-SCHEMA-001 |
| Produced by | EGER-P007 (2026-08-26) |
| Type | Research specification — schema freeze |
| Contract dependency | EGER-ORACLE-CONTRACT-001 |
| Oracle evidence | ORACLE-001 (static), ORACLE-002 (runtime) |
| Status | FROZEN/PROVISIONAL per §14; examples are ILLUSTRATIVE — NOT RUNTIME DATA |

---

## 1. Schema Design Principles

1. **Evidence over assertion** — every state claim references an EvidenceArtifact hash.
2. **Scope honesty (P6)** — every artifact carries its evidence_scope; no silent promotion.
3. **Failure containment** — oracle failure and engineering invalidity are distinct types, never overloaded.
4. **Provenance before convenience** — provenance fields are REQUIRED; omission invalidates the artifact.
5. **Minimality** — only fields required by the science; optional fields are explicitly marked.
6. **Authority separation (P7)** — no probabilistic component constructs an authoritative EvidenceArtifact.
7. **Determinism** — canonical byte representation + content hashing; timestamps excluded from semantic equality.
8. **Version explicitness** — every artifact carries `schema_version`; changes version the schema.

## 2. CandidateArtifact

The probabilistic component's output under study (SDC text).

| Field | `type` | Required | Notes |
|---|---|---|---|
| `schema_version` | string | REQUIRED | `eger.candidate.v1` |
| `artifact_id` | string | REQUIRED | e.g. `EGER-CAND-001`; stable within run |
| `run_id` | string | REQUIRED | ties to manifest/condition |
| `sdc_text` | string | REQUIRED | exact candidate text (raw, not "cleaned") |
| `input_hash` | string (hex) | REQUIRED (derived) | SHA-256(sdc_text), canonical UTF-8 bytes |
| `provenance.model` | string | REQUIRED | model id used to produce candidate |
| `provenance.produced_at` | ISO8601 | REQUIRED | generation provenance timestamp |

CandidateArtifact never implies correctness; it is what will be validated.

## 3. RawEvidence

Pinned, uninterpreted oracle stdout as captured.

| Field | type | Required | Notes |
|---|---|---|---|
| `schema_version` | string | REQUIRED | `eger.raw.v1` |
| `raw_id` | string | REQUIRED | `EGER-RAW-###` |
| `oracle` | {name, version, revision} | REQUIRED | pinned per series |
| `invocation` | object | REQUIRED | operation + args (e.g. `check --json`) + schema_version |
| `input_hash` | hex | REQUIRED | SHA-256 of checked sdc_text bytes (links to CandidateArtifact) |
| `raw_bytes` | bytes/file-ref | REQUIRED | either embedded or file path under `evidence_store/` |
| `raw_hash` | hex | REQUIRED (derived) | SHA-256(raw_bytes) |
| `exit_code` | int | REQUIRED | oracle process exit code (0/1/2/3) |
| `captured_at` | ISO8601 | REQUIRED | provenance timestamp (excluded from semantic equality) |

RawEvidence is immutable and retained even after normalization (contract §13).

## 4. EvidenceArtifact

Normalized, typed evidence derived from RawEvidence by the deterministic adapter.

| Field | type | Required | Notes |
|---|---|---|---|
| `schema_version` | string | REQUIRED | `eger.evidence.v1` |
| `artifact_id` | string | REQUIRED | `EGER-EVID-###` |
| `oracle` | {name, version, revision} | REQUIRED | |
| `provenance` | object | REQUIRED | see §7; includes `input_hash`, `raw_hash`, `evidence_hash` |
| `evidence_scope` | enum | REQUIRED | `FULL` \| `PARTIAL` \| `INSUFFICIENT` \| `UNSUPPORTED` (lossless mapping of `analysis_scope.status`; see contract §8) |
| `oracle_status` | enum | REQUIRED | `SUCCESS` \| `INVALID_REQUEST` \| `ORACLE_FAILURE` |
| `findings` | FindingArtifact[] | REQUIRED | may be empty; never null when `oracle_status=SUCCESS` |
| `analysis_scope` | AnalysisScope | REQUIRED | when `oracle_status=SUCCESS`; null otherwise |
| `raw_ref` | {raw_id, raw_hash} | REQUIRED | link to RawEvidence |
| `evidence_hash` | hex | REQUIRED (derived) | SHA-256(canonical JSON of normalized artifact excluding `produced_at`) |
| `produced_at` | ISO8601 | REQUIRED | provenance timestamp |

Invariants (FROZEN):
- `oracle_status=ORACLE_FAILURE` ⇒ `evidence_scope=null`, `findings=[]`, `analysis_scope=null`.
- `evidence_scope∈{INSUFFICIENT,UNSUPPORTED}` ⇒ never warrants a VALIDATED epistemic transition.
- `oracle_status=SUCCESS` with empty findings + `evidence_scope=FULL` ⇒ "no issues within scope" (not universal design correctness).

## 5. FindingArtifact

Normalized per-issue structure.

| Field | type | Required | Notes |
|---|---|---|---|
| `finding_id` | string | REQUIRED | `EGER-FIND-###` stable within artifact; not cross-run stable unless identity present |
| `code` | string | REQUIRED | e.g. `SDC-028`, `SDC-002`; from `rules_registry.py` catalog |
| `severity` | enum | REQUIRED | `error` \| `warning` \| `info` (from catalog at emit time) |
| `message` | string | REQUIRED | human-readable `msg` from oracle (not authoritative for identity) |
| `location` | {line:int, col:int?} | REQUIRED (`line` ≥0; `col` nullable) | `line` from oracle `line`; 0 = unknown |
| `related_location` | {line:int} | OPTIONAL (nullable) | oracle `line2` when present (conflict pair) |
| `context` | object? | OPTIONAL | oracle `context` when present (e.g. construct-aware fields) |
| `affected_object` | string? | OPTIONAL | object name when context identifies it |
| `rule` | {code, severity, added_version?} | DERIVED | catalog lookup at emit time for traceability |
| `finding_identity` | object? | OPTIONAL (preserved when present) | versioned semantic identity fields when oracle emits `identity`; otherwise null — never synthesized from message text |

The adapter never invents findings (Rule C) and never derives identity from `message`.

## 6. AnalysisScope

Normalized from `analysis_scope` JSON (runtime-observed shape per EVID-006).

| Field | type | Required | Notes |
|---|---|---|---|
| `status` | enum (raw) | REQUIRED | `VALIDATED` \| `PARTIALLY_VALIDATED` \| `NETLIST_REQUIRED` \| `UNSUPPORTED` \| `TCL_EXECUTION_REQUIRED` \| `NOT_VALIDATED` (original oracle vocabulary, preserved) |
| `normalized_scope` | enum | REQUIRED (derived) | equals `EvidenceArtifact.evidence_scope` (duplicated for convenience) |
| `commands_found` | int | REQUIRED | |
| `fully_analyzed` | int | REQUIRED | |
| `partially_analyzed` | int | REQUIRED | |
| `netlist_required` | int | REQUIRED | |
| `unsupported` | int | REQUIRED (aggregate of UNSUPPORTED + TCL_EXECUTION_REQUIRED counts if split) |
| `tcl_execution_required` | int | OPTIONAL | kept distinct when observable |
| `unknown_options` | string[] | REQUIRED (may be []) | never value-analyzed options |
| `ignored_options` | string[] | REQUIRED (may be []) | standard options present but not value-analyzed |
| `constructs` | ConstructLevel[] | REQUIRED | per-construct `{command, level, count, netlist_refs, ignored_options, unknown_options}` |

No numeric confidence scores introduced — scope is categorical.

## 7. Provenance

Shared shape carried by EvidenceArtifact (and referenced by RawEvidence):

| Field | type | Required |
|---|---|---|
| `oracle.name` | string | REQUIRED |
| `oracle.version` | string | REQUIRED |
| `oracle.revision` | string (commit) | REQUIRED |
| `invocation.operation` | enum | REQUIRED (`validate` / `validate_enriched` etc.) |
| `invocation.args` | object | REQUIRED |
| `invocation.schema_version` | string | REQUIRED |
| `input_hash` | hex | REQUIRED |
| `raw_hash` | hex | REQUIRED |
| `evidence_hash` | hex | REQUIRED |
| `schema_version` | string | REQUIRED |
| `produced_at` | ISO8601 | REQUIRED |
| `raw_path` | string (path) | REQUIRED |

Provenance answers §11 of the contract's "Where did this evidence come from?" No
secret or credential fields exist; environment data beyond the above is forbidden.

## 8. OracleResult / Error Model

```
OracleResult = Success(EvidenceArtifact) | Failure(OracleFailure)
OracleFailure = { kind: INVALID_REQUEST | ORACLE_FAILURE, exit_code, raw_ref?, message }
INSUFFICIENT is not a top-level failure — it is `Success` with evidence_scope ∈ {INSUFFICIENT,UNSUPPORTED}.
```

Distinguishing table (contract §9 restated):

- `ENGINEERING_FINDING` (a finding inside `Success`) ≠ `INVALID_REQUEST`
- `ENGINEERING_FINDING` ≠ `ORACLE_FAILURE`
- `INSUFFICIENT` ≠ `INVALID` (the former is about missing context, not wrong engineering)
- All share the same top envelope only in typed-union form — an agent cannot confuse a missing-evidence `null` branch with a finding branch.

## 9. EpistemicState Boundary

EvidenceArtifact is **input** to the epistemic layer, never the state itself.
The deterministic Epistemic State Manager (L2) consumes EvidenceArtifact and
produces a separate `EpistemicState` record (out of scope for P007 schema freeze
except to declare the boundary: L2 owns transitions VALIDATED/REFUTED/UNKNOWN/
AMBIGUOUS; oracle never authorizes them). EvidenceArtifact's `evidence_scope`
is a necessary input for L2's transition legality check.

## 10. Authorization Boundary

EvidenceArtifact and EpistemicState are **inputs** to L3; L3 is the only
authority that may write the verified-engineering-state store. The oracle
MUST NOT gate, commit, or approve. EvidenceArtifact contains no "approve: true"
field; approval lives only in L3's typed `AuthorizationDecision`.

## 11. Hash Policy

- `input_hash` = SHA-256(CandidateArtifact.sdc_text as UTF-8 bytes). Proves which exact input was checked.
- `raw_hash` = SHA-256(RawEvidence bytes). Proves the oracle's uninterpreted output as captured.
- `evidence_hash` = SHA-256(canonical JSON of normalized EvidenceArtifact **excluding** `produced_at` and any non-semantic fields). Proves the normalized evidence content.

What hashes do NOT prove: semantic correctness, engineering validity, or
universal determinism beyond the pinned revision/invocation (EVID-005 scope).

## 12. Timestamp Policy

- `produced_at` exists on every artifact as **execution provenance**, never as semantic content.
- `produced_at` is excluded from canonical forms used for `evidence_hash` / `input_hash` computation.
- Oracle-emitted timestamps (none observed on the tested path; harness `runtime_ms` observed only in tests) are not normalized into semantic fields if they appear in future.
- Semantic equality of evidence is defined by canonical hash equality, not timestamp distance.

## 13. Schema Versioning

- Every artifact carries `schema_version` (`eger.candidate.v1`, `eger.raw.v1`, `eger.evidence.v1`, etc.).
- Initial versions are **FROZEN** at P007 (see §14).
- Additive optional fields: minor bump (PROVISIONAL until adopted by an experiment series).
- Breaking change (required field change, enum semantics change): **major version bump** + migration note in this doc + `EGER-CHANGE-###` if scientific meaning shifts. Old-version artifacts remain immutable and interpretable.
- Schema changes never silently invalidate prior research evidence.

## 14. Required vs Optional Fields

| Artifact | REQUIRED summary | OPTIONAL/nullable summary |
|---|---|---|
| CandidateArtifact | schema_version, artifact_id, run_id, sdc_text, input_hash, provenance.model, produced_at | (none beyond listed — minimal) |
| RawEvidence | all fields in §3 | — |
| EvidenceArtifact | schema_version, artifact_id, oracle{3}, provenance, evidence_scope, oracle_status, findings, analysis_scope, raw_ref, evidence_hash, produced_at | — (findings empty array allowed; scope null only on failure) |
| FindingArtifact | finding_id, code, severity, message, location.line | related_location, context, affected_object, finding_identity (preserved when present), col |
| AnalysisScope | §6 REQUIRED rows | tcl_execution_required (distinction optional) |

## 15. Forbidden Fields / States

- `trusted: true` / `validated: true` / `approve: true` booleans anywhere on the EvidenceArtifact — approval lives in L3 only.
- Numeric confidence/score synthesized from scope — prohibited (scope is categorical).
- `finding_identity` derived from `message` text — prohibited.
- `oracle_status=ORACLE_FAILURE` coexisting with non-empty `findings` or `evidence_scope=FULL` — prohibited combination.
- `evidence_scope=null` coexisting with `oracle_status=SUCCESS` — prohibited.
- LLM-provenance fields (model completions) inside EvidenceArtifact — forbidden (that provenance lives on CandidateArtifact only).

## 16. Example Shapes

> **ILLUSTRATIVE — NOT RUNTIME DATA.** These shapes demonstrate field
> placement; values are synthetic and MUST NOT be cited as observed evidence
> from ORACLE-001/002.

### CandidateArtifact (illustrative)

```json
{
  "schema_version": "eger.candidate.v1",
  "artifact_id": "EGER-CAND-001",
  "run_id": "C2-run-07",
  "sdc_text": "create_clock -name clk -period 10 [get_ports clk]\n",
  "input_hash": "abc123...",
  "provenance": {"model": "model-a:2026-08-01", "produced_at": "2026-08-26T19:00:00+05:30"}
}
```

### EvidenceArtifact — SUCCESS with findings (illustrative)

```json
{
  "schema_version": "eger.evidence.v1",
  "artifact_id": "EGER-EVID-010",
  "oracle": {"name": "Ṛta", "version": "1.5.11", "revision": "3b5c2f2"},
  "provenance": {
    "input_hash": "abc123...",
    "raw_hash": "def456...",
    "evidence_hash": "789...",
    "schema_version": "eger.evidence.v1",
    "produced_at": "2026-08-26T19:05:00+05:30",
    "raw_path": "evidence_store/EGER-RAW-010.json"
  },
  "evidence_scope": "FULL",
  "oracle_status": "SUCCESS",
  "findings": [{
    "finding_id": "EGER-FIND-010-01",
    "code": "SDC-002",
    "severity": "error",
    "message": "Duplicate clock name ...",
    "location": {"line": 14},
    "related_location": null,
    "context": null
  }],
  "analysis_scope": {
    "status": "VALIDATED",
    "normalized_scope": "FULL",
    "commands_found": 5,
    "fully_analyzed": 5,
    "partially_analyzed": 0,
    "netlist_required": 0,
    "unsupported": 0,
    "unknown_options": [],
    "ignored_options": [],
    "constructs": []
  },
  "raw_ref": {"raw_id": "EGER-RAW-010", "raw_hash": "def456..."}
}
```

### OracleFailure — ORACLE_FAILURE (illustrative)

```json
{
  "schema_version": "eger.evidence.v1",
  "kind": "ORACLE_FAILURE",
  "exit_code": 3,
  "message": "engine failure (see raw log)",
  "raw_ref": {"raw_id": "EGER-RAW-011", "raw_hash": "fff..."}
}
```
