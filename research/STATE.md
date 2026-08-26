# EGER Research STATE

Last updated: 2026-08-26 (EGER-P010)

| Item | Status |
|---|---|
| Current contract | EGER Research Contract v0.2 (canonical docx; now version-controlled @ baseline `6be2314`; formal freeze acceptance still to be confirmed — see Open Questions) |
| Current phase | **Phase 1 — Deterministic reference system (L1/L2/L3) + single LLM proposal layer complete** — ready for experimental freeze (P011) before C0–C5. |
| Research memory | **VERSION-CONTROLLED** (baseline commit `6be2314`, branch `main`) |
| Git | **INITIALIZED** at `D:\Research on EGER` (EGER_ROOT); Ṛta excluded via `.gitignore` |
| Research baseline | **ESTABLISHED** (`6be23141785dce7c4a6b8bce0f390bad99b13c87`, 2026-08-26) |
| Current architecture | **EGER-ARCH-002** (recommended; pending formal implementation authorization) |
| Primary experiment | C0–C5 controlled ablation — defined, not run |
| Engineering extension | C6 specialized subagents — deferred until after C0–C5 evaluation |
| Oracle | External deterministic Ṛta v1.5.11 (`rta-constraint-intelligence`), **runtime characterization complete** (EGER-ORACLE-002); CLI/MCP byte-determinism & scope live at runtime verified; adapter **IMPLEMENTED (P008)** |
| Oracle runtime evidence | Raw outputs at `research/oracle/runtime/` (untracked pending retention policy) |
| Implementation status | **L1/L2/L3 + single LLM proposal layer IMPLEMENTED** (P008+P009+P010); no C0–C5/C6 yet |
| Subagent status | Not implemented — single Engineer only (fake), C6 deferred |
| Experiment status | Not started (awaiting P011 benchmark + manifest freeze) |
| Benchmark status | Not frozen (does not exist yet) |
| Research ledger | Established by EGER-P004; version-controlled since P005; P006–P010 recorded |
| Git / version control | INITIALIZED (EGER_ROOT, branch `main`, baseline `6be2314`); Ṛta explicitly excluded |
| EvidenceOracle contract | **EGER-ORACLE-CONTRACT-001** FROZEN/PROVISIONAL per matrix (see §20 of contract doc) — **IMPLEMENTED** |
| Typed artifact schemas | **EGER-SCHEMA-001** FROZEN v1 family (`eger.candidate.v1`/`raw.v1`/`evidence.v1`) — **IMPLEMENTED** |
| EvidenceOracle adapter | **IMPLEMENTED — PASS (14/14 tests)** (`eger/oracle/adapter.py`, `eger/oracle/schemas.py`; tests `tests/test_evidence_oracle.py`) |
| Adapter tests | PASS (14/14); RTA integrity verified (3b5c2f2 main 19 unchanged) |
| Epistemic state (L2) | **IMPLEMENTED — PASS (17/17 tests)** (`eger/epistemic/state.py`, `eger/epistemic/transitions.py`; deterministic engine, immutable baseline, EVR raw counts) |
| Authorization (L3) | **IMPLEMENTED — PASS (17/17 tests)** (`eger/authorization/gate.py`; hard gate VALIDATED+FULL+SUCCESS) |
| L2/L3 schemas | **EGER-EPISTEMIC-001** FROZEN (`eger.epistemic.v1`, `eger.transition.v1`, `eger.authorization.*`) — EGER-SCHEMA-001 unchanged |
| L2/L3 tests | PASS (17/17) + regression 14/14 = 31/31 overall; RTA 3b5c2f2 main 19 unchanged; EvidenceOracle not modified |
| LLM proposal layer | **IMPLEMENTED — PASS (16/16 tests)** (`eger/engineer/*`; `FakeEngineerModel` + `EngineerAdapter` + `CandidateArtifact`; `tests/test_llm_proposal.py`); 47/47 total |
| LLM tests | PASS (16/16) + full regression 31/31 = 47/47 overall; RTA 3b5c2f2 main 19 unchanged; deterministic layers not modified |
| Violation metrics | `EpistemicEngine.evr()` + `AuthorizationGate.violation_stats()` PROVISIONAL — machine-readable |
| Provenance / determinism | Hash trio (input/raw/evidence/candidate) + timestamp-as-provenance FROZEN and implemented; deterministic file path `eger_oracle_<hash>/candidate.sdc`; transitions + extraction deterministic |

## Two memories — explicit separation

- RESEARCH MEMORY: version-controlled in `research/` (ledger, state, implementation records).
- ENGINEERING EPISTEMIC MEMORY: deterministic engine (`eger/epistemic`, `eger/authorization`) + single LLM Engineer proposals — proposal authority only, verified separate (T-P010-012).

## Accepted decisions

| ID | Decision | Status |
|---|---|---|
| EGER-DEC-005 | C0–C5 uses exactly one probabilistic component; Evidence/State/Authorization are deterministic layers | ACCEPTED as architecture recommendation (pending implementation review) |
| EGER-DEC-006 | `rta_generate` forbidden to all EGER components | ACCEPTED |
| EGER-DEC-007 | C4 routing is deterministic (frozen table); LLM-controlled routing rejected | ACCEPTED |

## Superseded decisions / artifacts

| ID | Content | Superseded by | Note |
|---|---|---|---|
| EGER-ARCH-001 | Three-LLM-role topology (supervisor/proposer/analyst) + 3 deterministic layers | EGER-ARCH-002 for C0–C5 | Preserved at [`architecture/EGER-ARCH-001.md`](architecture/EGER-ARCH-001.md). Deterministic-layer core survives unchanged. |
| EGER-DEC-001…004 (P001-era) | Determinize-everything axiom; adapter boundary; per-condition configs; Critic deferral | Partially absorbed into ARCH-002 | Original full records exist only in chat transcript (P001 response); canonical detail unavailable — recorded as historical references in LEDGER. |

## Open questions

1. Formal confirmation that contract v0.2 is accepted/frozen.
2. Ṛta pinned-commit hygiene: P002 observed a dirty working tree; confirm inspected bytes == intended baseline before any series.
3. Runtime verification — **core unknowns now RESOLVED** (CLI formats, byte determinism, trust scope, exit 0/1, MCP handshake per ORACLE-002); remaining: exit codes 2/3 paths, finding-identity emission contexts, netlist-aware mode, baseline/gate E2E, large-design perf.
4. Benchmark corpus selection and freezing.
5. Model/sampling-parameter freeze policy per condition sweep.
6. Claim-registration enforcement mechanism (reject vs flag unstructured claims) — affects future EVR denominator.
7. Adapter transport: subprocess-first chosen; revisit MCP at C6.
8. Runtime artifact retention policy for `research/oracle/runtime/` outputs (evidence vs temp).

## Known risks

- Ṛta actively developed → version drift; pin commit+version per series.
- Single-LLM design carries self-evaluation bias (validator finality mitigates; C6 can quantify).
- All research history prior to P004 lives only in chat transcripts (backfilled now with retrospective IDs; marked as such).
- Windows path/locale fragility around non-ASCII "Ṛta" characters in tooling.

## Next authorized step

Await external review of EGER-P010 (full L1/L2/L3 + single LLM proposal layer, 47/47 PASS).
The single recommended next action after review: authorize P011 — benchmark + run-manifest freeze
(model/sampling/benchmark/oracle pinning) as the experimental preparation gate before C0–C5 execution.

## Implementation Records

- `research/implementation/EGER-P008-ADAPTER.md`
- `research/implementation/EGER-P009-EPISTEMIC-AUTHORIZATION.md`
- `research/implementation/EGER-P010-LLM-PROPOSAL.md`
- `research/schemas/EGER-EPISTEMIC-SCHEMAS.md`
- `research/schemas/EGER-ARTIFACT-SCHEMAS.md` (unchanged)

## Verification (P010)

- RTA before: 3b5c2f2 main 19 dirty — after: 3b5c2f2 main 19 (no mutation)
- EvidenceOracle: validate(), capabilities(), evidence_schema() — NOT MODIFIED (git diff empty, 14/14 still PASS)
- L2: EpistemicState + deterministic transitions + immutable baseline + EVR — 17/17 PASS
- L3: Authorization gate (hard, no prompts) — 17/17 PASS
- LLM Engineer: proposal authority only (FakeEngineerModel + EngineerAdapter + CandidateArtifact) — 16/16 PASS
- Overall: 47/47 PASS; no agents/subagents, no C0–C5/C6, no rta_generate
- Two memories verified separate (ledger ≠ engine; T-P010-012)
