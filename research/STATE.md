# EGER Research STATE

Last updated: 2026-08-26 (EGER-P005)

| Item | Status |
|---|---|
| Current contract | EGER Research Contract v0.2 (canonical docx; now version-controlled @ baseline `6be2314`; formal freeze acceptance still to be confirmed — see Open Questions) |
| Current phase | Phase 0 closing: traceability foundation + version-controlled baseline established. Phase 1 preparation. |
| Research memory | **VERSION-CONTROLLED** (baseline commit `6be2314`, branch `main`) |
| Git | **INITIALIZED** at `D:\Research on EGER` (EGER_ROOT); Ṛta excluded via `.gitignore` |
| Research baseline | **ESTABLISHED** (`6be23141785dce7c4a6b8bce0f390bad99b13c87`, 2026-08-26) |
| Current architecture | **EGER-ARCH-002** (recommended; pending formal implementation authorization) |
| Primary experiment | C0–C5 controlled ablation — defined, not run |
| Engineering extension | C6 specialized subagents — deferred until after C0–C5 evaluation |
| Oracle | External deterministic Ṛta v1.5.11 (`rta-constraint-intelligence`), read-only copy in workspace; adapter NOT built |
| Implementation status | **Not implemented** (no agents, no adapter, no runtime, no gate) |
| Subagent status | Not implemented |
| Experiment status | Not started |
| Benchmark status | Not frozen (does not exist yet) |
| Research ledger | Established by EGER-P004; version-controlled since P005 |
| Git / version control | INITIALIZED (EGER_ROOT, branch `main`, baseline `6be2314`); Ṛta explicitly excluded |

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
3. Runtime verification of Ṛta CLI/MCP behavior still outstanding (ORACLE-001 §17).
4. Benchmark corpus selection and freezing.
5. Model/sampling-parameter freeze policy per condition sweep.
6. Claim-registration enforcement mechanism (reject vs flag unstructured claims) — affects future EVR denominator.
7. Adapter transport: subprocess-first chosen; revisit MCP at C6.
8. Git initialization authorization.

## Known risks

- Ṛta actively developed → version drift; pin commit+version per series.
- Single-LLM design carries self-evaluation bias (validator finality mitigates; C6 can quantify).
- All research history prior to P004 lives only in chat transcripts (backfilled now with retrospective IDs; marked as such).
- Windows path/locale fragility around non-ASCII "Ṛta" characters in tooling.

## Next authorized step

Await external review of the version-controlled baseline. The single
recommended next action after review: authorize the first implementation-phase
prompt (runtime verification of Ṛta CLI + typed-artifact schema freeze), which
are the two remaining prerequisites before any C0–C5 machinery is built.
