# EGER-ORACLE-001 — Preliminary Ṛta Oracle Assessment

| Field | Value |
|---|---|
| ID | EGER-ORACLE-001 |
| Produced by | EGER-P002 (2026-08-26) |
| Type | Oracle reconnaissance record |
| Method | **Strictly read-only static inspection.** No execution, no modification; pre-existing dirty git state documented and untouched |
| Subject | `D:\Research on EGER\rta-constraint-intelligence` — Ṛta v1.5.11, branch main @ 3b5c2f2, remote github.com/RAMA-L7/rta-constraint-intelligence |
| Status | ACCEPTED AS ORACLE RECONNAISSANCE |

## Classification key

OBS = observed implementation · DOC = document claim only · INF = agent
inference · UNK = unknown (runtime verification required).

## Major observations

### Interface surface [OBS]
- **MCP server** (`rta/api/mcp_server.py`, protocol 2024-11-05, stdio JSON-RPC):
  tools `rta_analyze`, `rta_lint`, `rta_convert`, `rta_generate`,
  `rta_snapshot`, `rta_diff`, `rta_corners`, `rta_rules`; schemas via
  `tools/list`; docstring contract: "backend modules are AUTHORITY… never
  modified here"; "same input ⇒ same tool output".
- **CLI** (`rta/cli/cli.py`): check/generate/diff/corners/analyze/rules/
  whats-new/web/coverage/report/lint/convert/batch; exit codes PASS=0,
  GATE_FAILED=1, INVALID=2, ENGINE_FAILURE=3.
- **Python JSON layer** (`rta/api/api_server.py`) behind both.

### Evidence formats [OBS]
Findings serialized as `{sev, code(SDC-NNN/CHG-XXX-NNN), msg, line, line2,
identity, context}`; centralized catalog in `rules_registry.py`
(APP_VERSION 1.5.11); versioned semantic FindingIdentity separated from
presentation and provenance (`rta/engine/diff/finding_identity.py`);
analyze payload keys: issues/stats/scope/coverage/interactions/readiness/
clock_relations/baseline.

### Capability/trust boundary [OBS]
`rta/engine/trust/support_boundary.py`: per-construct trust levels FULL /
PARTIAL / NETLIST_REQUIRED / UNSUPPORTED / TCL_EXECUTION_REQUIRED; aggregate
statuses VALIDATED / PARTIALLY_VALIDATED / NETLIST_REQUIRED / UNSUPPORTED /
TCL_EXECUTION_REQUIRED / NOT_VALIDATED; standard-vs-interpreted option audit;
Tcl never executed; "no errors" never equals "proven correct".

### Determinism / LLM independence [OBS, path-scoped]
Dependencies: pyyaml (+optional streamlit/pytest) only. No LLM/network imports
in engine paths; urllib confined to localhost test/UI harnesses; clean-room
release audit rejects network+LLM imports; policy engine is inert data (no
eval/exec). Self-declaration: `"engine": "deterministic — local-first —
offline-capable — no LLM"` (api_server.py:731). Byte-level runtime determinism:
UNK.

### Baseline/regression/gating [OBS structure]
Snapshot → readiness_diff (NEW/RESOLVED/CHANGED) → declarative policies
(BLOCKERS_ONLY / NO_READINESS_REGRESSION / STRICT / CUSTOM v1 schema);
trust_regression and coverage_regression categories map directly onto EGER
I5/P1 needs. Run-history management as first-class concept: not observed.

## What Ṛta proves vs does not prove (P6)

Proves: structural/semantic SDC properties within its interpreted-option
subset; scoped object resolution vs supplied netlist; constraint-version deltas;
readiness/regression categories — each trust-stamped.
Does NOT prove: STA/signoff closure; correctness of PARTIAL/UNSUPPORTED/TCL_
EXECUTION_REQUIRED constructs; design intent; anything universal about a design.
EGER rule: every Evidence artifact must carry `AnalysisScope.status` + ignored-
options; validator rejects out-of-scope promotion.

## rta_generate decision

Generation capability exists [OBS] but is **forbidden to all EGER components**
(EGER-DEC-006): Evidence authority must not silently become Proposal authority.
No exception recommended; future exception requires EGER-CHANGE record.

## Possible adapter (INF — not implemented)

| Contract §12 concept | Ṛta actual source |
|---|---|
| validate() | `rta_analyze` / CLI analyze |
| capabilities() | `tools/list` schemas + AnalysisScope trust model + `rta_rules()` |
| evidence_schema() | inputSchemas + serialized issue/scope/diff shapes |
| regression | snapshot + diff + gate policy |

Transport: subprocess-first (clean provenance capture), MCP deferred to C6
decision. Adapter must refuse exit codes 2/3 as evidence sources.

## Unresolved runtime questions (all UNK)

CLI end-to-end output shapes; byte-level determinism of repeated runs; MCP
handshake with OpenCode; emitted readiness verdict strings; large-design
performance; custom-rules effect on identity stability. Also: pre-existing
dirty working tree means inspected bytes ≠ committed HEAD for some fixtures —
pin hygiene required before any series.
