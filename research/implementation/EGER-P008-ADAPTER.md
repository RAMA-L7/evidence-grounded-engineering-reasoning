# EGER-P008 — EvidenceOracle Adapter Implementation Record

| Field | Value |
|---|---|
| ID | EGER-P008 |
| Implementation gate | Evidence layer only |
| Contracts | EGER-ORACLE-CONTRACT-001, EGER-SCHEMA-001 |
| RTA revision | 3b5c2f2 (v1.5.11, branch main) |
| EGER baseline before | caa0c39 |
| Adapter files | `eger/oracle/adapter.py`, `eger/oracle/schemas.py`, `eger/__init__.py`, `eger/oracle/__init__.py` |
| Tests | `tests/test_evidence_oracle.py` (T001–T012 + 2 schema tests = 14 tests) |
| Status | PASS (14/14) |

## Implementation Scope

Deterministic EvidenceOracle adapter only. Implements `validate()`, `capabilities()`, `evidence_schema()` as specified in P007 contracts. No LLM, no epistemic state, no authorization, no agents, no C0–C5/C6 machinery.

## Architecture

```
CandidateArtifact (sdc_text)
      ↓
EvidenceOracle.validate()
      ↓  _invoke_rta  (cwd OUTSIDE Ṛta, PYTHONDONTWRITEBYTECODE=1, deterministic file path)
   RawEvidence  { raw_bytes, raw_hash, exit_code, input_hash, invocation, captured_at }
      ↓  _build_success / _normalize_*
   EvidenceArtifact  { evidence_scope, findings[], analysis_scope, provenance, evidence_hash }
      ↓
OracleResult  Success | Failure(INVALID_REQUEST | ORACLE_FAILURE)
```

Components (minimal, no unnecessary abstraction):
- **OracleInvoker**: `_invoke_rta` — single responsibility, side-effect free beyond capturing
- **EvidenceNormalizer**: `_normalize_findings`, `_normalize_scope`, `_map_scope`
- **EvidenceArtifactBuilder**: `_build_success` — deterministic hashing, provenance assembly

All normalization is deterministic, side-effect free, reproducible, schema-conforming. No probabilistic logic.

## Files Created

- `eger/__init__.py` — package marker
- `eger/oracle/__init__.py` — public re-exports
- `eger/oracle/schemas.py` — SCHEMA_VERSIONS, SCOPE_MAP, CAPABILITIES, `evidence_schema()` declarative descriptor
- `eger/oracle/adapter.py` — EvidenceOracle class, types (RawEvidence, EvidenceArtifact, FindingArtifact, AnalysisScope, Provenance, OracleResult, OracleFailure), hashing helpers, scope mapping, normalization rules A–L
- `tests/test_evidence_oracle.py` — 14 tests

No files created inside `rta-constraint-intelligence/`. RawEvidence file retention writes only to caller-provided `evidence_store` outside Ṛta, or remains in-memory with deterministic path string.

## Frozen Contracts Used

- EGER-ORACLE-CONTRACT-001 §8 scope mapping (FROZEN): VALIDATED→FULL etc, no-upgrade rule
- §9 error model (FROZEN): SUCCESS vs INVALID_REQUEST vs ORACLE_FAILURE vs INSUFFICIENT
- §12 Rules A–L (FROZEN): scope preservation, finding preservation, no invention, no upgrade, provenance retention, generation prohibition
- §13 dual retention, §14 generation boundary (EGER-DEC-006, Rule J), §15/16 authority boundaries
- EGER-SCHEMA-001 v1 family (`eger.candidate.v1`, `eger.raw.v1`, `eger.evidence.v1`)

## Test Strategy & Results

| Test | Description | Result |
|---|---|---|
| T001 | valid/minimal SDC → success, provenance, hashes | PASS |
| T002 | validation finding → engineering finding ≠ oracle failure | PASS |
| T003 | INSUFFICIENT (NETLIST_REQUIRED) → success with INSUFFICIENT scope | PASS |
| T004 | oracle invocation failure (missing binary) → ORACLE_FAILURE | PASS |
| T005 | deterministic normalization (A vs B, byte+semantic identical) | PASS |
| T006 | hash stability (same input → same hash, different input → different hash) | PASS |
| T007 | provenance completeness (all required fields, pinned revision) | PASS |
| T008 | scope preservation (no upgrade path) | PASS |
| T009 | generation unreachability (no rta_generate string in Evidence path) | PASS |
| T010 | schema compliance (required/forbidden fields, enum validity) | PASS |
| T011 | raw evidence retention (file write, hash match, linkage) | PASS |
| T012 | timestamp/hash separation (different produced_at → same evidence_hash) | PASS |
| +capabilities | declarative capability descriptor | PASS |
| +evidence_schema | schema versions descriptor | PASS |

Total: 14/14 PASS.

## Determinism Notes

- RTA invocation uses deterministic temp path `gettempdir()/eger_oracle_<input_hash[:12]>/candidate.sdc` so the oracle's "file" field in raw JSON is deterministic per input content.
- Raw hash = SHA256(raw_bytes as captured); evidence_hash = SHA256(canonical JSON excluding produced_at) per P007 hash policy.
- `produced_at` excluded from evidence_hash → identical semantic evidence → identical hash across runs (T012).

## Known Limitations & Remaining UNKNOWNs (honest)

- Exit 2/3 paths documented as PROVISIONAL (not runtime-triggered with valid evidence in P006); T004 exercises ORACLE_FAILURE via missing binary path, not via oracle's own exit 2/3 with structured output.
- `finding_identity` field: preserved when present in raw payload; not observed on `check --json` path used here (richer identity lives on constraint-interaction/design-aware paths — UNKNOWN).
- Netlist-aware mode, snapshot/diff, large-design perf, multi-session determinism beyond tested fixture — all out-of-scope for P008 by design.

## Deviations from P007

NONE. Implementation follows frozen schemas and contract verbatim. No additional operations added beyond `validate`, `capabilities`, `evidence_schema`. No science-facing schema decisions made during implementation (canonical JSON ordering choice was `sort_keys=True, separators=(',', ':')` — mechanical, not scientific, and documented here).

## RTA Integrity

Before adapter tests: HEAD `3b5c2f2`, branch `main`, dirty count 19.
After all integration tests: HEAD `3b5c2f2`, branch `main`, dirty count 19.
No files created/modified/deleted inside `rta-constraint-intelligence/`. Invocation discipline: cwd OUTSIDE Ṛta, PYTHONDONTWRITEBYTECODE=1.

## Hash Canonicalization Choice

`_canonical_json` = `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`.
Choice is deterministic, side-effect free, and does not change scientific semantics (field set and values remain frozen). Recorded here for reproducibility.

## Non-Goals Preserved

LLM: NO. Epistemic state (HYPOTHESIS/VALIDATED etc): NO. Authorization gates: NO. Agents/subagents: NO. C0–C5/C6: NO. Scientific contract v0.2: unchanged.
