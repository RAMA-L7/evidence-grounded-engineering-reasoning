# EGER Research STATE

Last updated: 2026-08-26 (EGER-P007)

| Item | Status |
|---|---|
| Current contract | EGER Research Contract v0.2 (canonical docx; now version-controlled @ baseline `6be2314`; formal freeze acceptance still to be confirmed — see Open Questions) |
| Current phase | Phase 0 closing: traceability foundation + version-controlled baseline + **Ṛta runtime characterization + EvidenceOracle contract & schema freeze complete**. Phase 1 preparation. |
| Research memory | **VERSION-CONTROLLED** (baseline commit `6be2314`, branch `main`) |
| Git | **INITIALIZED** at `D:\Research on EGER` (EGER_ROOT); Ṛta excluded via `.gitignore` |
| Research baseline | **ESTABLISHED** (`6be23141785dce7c4a6b8bce0f390bad99b13c87`, 2026-08-26) |
| Current architecture | **EGER-ARCH-002** (recommended; pending formal implementation authorization) |
| Primary experiment | C0–C5 controlled ablation — defined, not run |
| Engineering extension | C6 specialized subagents — deferred until after C0–C5 evaluation |
| Oracle | External deterministic Ṛta v1.5.11 (`rta-constraint-intelligence`), **runtime characterization complete** (EGER-ORACLE-002); CLI/MCP byte-determinism & scope live at runtime verified; adapter NOT built |
| Oracle runtime evidence | Raw outputs at `research/oracle/runtime/` (untracked pending retention policy) |
| Implementation status | **Not implemented** (no agents, no adapter, no epistemic runtime, no gate) |
| Subagent status | Not implemented |
| Experiment status | Not started |
| Benchmark status | Not frozen (does not exist yet) |
| Research ledger | Established by EGER-P004; version-controlled since P005; P006–P007 recorded |
| Git / version control | INITIALIZED (EGER_ROOT, branch `main`, baseline `6be2314`); Ṛta explicitly excluded |
| EvidenceOracle contract | **EGER-ORACLE-CONTRACT-001** FROZEN/PROVISIONAL per matrix (see §20 of contract doc) |
| Typed artifact schemas | **EGER-SCHEMA-001** FROZEN v1 family (`eger.candidate.v1`/`raw.v1`/`evidence.v1`) — additive extensions provisional |
| Provenance / determinism | Hash trio (input/raw/evidence) + timestamp-as-provenance FROZEN; byte-identical determinism observed (EVID-005) |

## Two memories — explicit separation

- RESEARCH MEMORY: being established NOW (this directory).
- ENGINEERING EPISTEMIC MEMORY: NOT IMPLEMENTED (no runtime exists).

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

Await external review of EGER-ORACLE-CONTRACT-001 and EGER-SCHEMA-001.
The single recommended next action after review: authorize the first
implementation prompt — a deterministic EvidenceOracle adapter skeleton
(with no epistemic/gate logic yet) validated only against the frozen
schemas and the pinned Ṛta runtime — as the implementation gate to C0–C5.
