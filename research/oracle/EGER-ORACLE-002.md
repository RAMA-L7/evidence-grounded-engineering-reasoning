# EGER-ORACLE-002 — Ṛta Runtime Characterization

| Field | Value |
|---|---|
| ID | EGER-ORACLE-002 |
| Produced by | EGER-P006 (2026-08-26) |
| Type | Runtime characterization record (controlled, non-mutating) |
| Subject | Ṛta v1.5.11 @ `rta-constraint-intelligence`, HEAD `3b5c2f2`, branch `main` |
| Relationship | Extends EGER-ORACLE-001 (static); supersedes nothing; ARCH-002 unchanged |
| Raw outputs | `research/oracle/runtime/` (untracked; see Evidence Artifacts) |
| Execution safety protocol | All commands run with cwd OUTSIDE Ṛta and `PYTHONDONTWRITEBYTECODE=1`; outputs redirected to the runtime dir; fixtures consumed read-only from `samples/` |

## Pre-run state (verified against P002/P005 baseline)

HEAD `3b5c2f2` · branch `main` · dirty entries 19 — **match**, proceeded.
Post-run: identical. Python 3.10.11, Windows/win32.

## Test table

| Test ID | Purpose | Command (abbrev) | Result | Classification |
|---|---|---|---|---|
| EGER-EVID-002 | CLI discoverability + version/help | `python <RTA>\cli.py --help` / `--version` | exit 0; full usage text; "Ṛta v1.5.11"; 13 subcommands incl. check/analyze/diff/rules; `check --json/--junit/--save-baseline/--gate {BLOCKERS_ONLY,NO_READINESS_REGRESSION,STRICT,CUSTOM}` confirmed in help | OBSERVED RUNTIME |
| EGER-EVID-003 | Structured evidence on valid input | `cli.py check samples\minimal_sdc.sdc --json` | exit 0; 20,678-byte JSON; keys: version/file/errors/warnings/info/stats/summary/analysis_scope/constraint_coverage/constraint_interactions/constraint_readiness | OBSERVED RUNTIME |
| EGER-EVID-004 | Exit code semantics | valid → exit 0; malformed sample (`edge_case_malformed.sdc`) → exit 1 with structured errors (e.g. SDC-002 duplicate clock, line 14) | meaningful pass/fail codes confirmed for these two cases; INVALID=2/ENGINE_FAILURE=3 not triggered — remain UNTESTED-RUNTIME | OBSERVED RUNTIME (partial) |
| EGER-EVID-005 | Determinism | identical `check --json` run twice (A/B) | SHA256 A == B — **byte-identical** output | OBSERVED RUNTIME |
| EGER-EVID-006 | Full pipeline + trust scope | `cli.py analyze all minimal_sdc.sdc --json`; scope inspection of EVID-003 payload | exit 0; keys version/file/check/coverage/clock_relations/constraint_interactions/constraint_readiness; `analysis_scope.status="NETLIST_REQUIRED"` with per-construct levels (`create_clock/set_input_delay/set_output_delay`=NETLIST_REQUIRED, `set_units/set_sdc_version`=FULL) — trust model live at runtime | OBSERVED RUNTIME |
| EGER-EVID-007 | Repository mutation verification | git HEAD/branch/status before & after every operation | unchanged throughout: `3b5c2f2`/`main`/19 | OBSERVED RUNTIME |
| EGER-EVID-008 | MCP interface | initialize + ping via stdio to `python -m rta.api.mcp_server`; earlier tools/list call | initialize → protocolVersion echo, serverInfo name/version 1.5.11; ping OK; tools/list → all 8 tools with schemas | OBSERVED RUNTIME |

Note (process honesty): first MCP probe accidentally piped only `tools/list`
(initialize line went to console); probe was corrected and re-run — recorded
here as part of the trace, not hidden.

## Findings by prompt question

### CLI runtime findings [OBSERVED RUNTIME]
Entry point works from outside Ṛta via root shim `cli.py` with script-dir on
sys.path. Documented vs observed CLI match on all inspected surfaces
(check/analyze flags, gate policy enum values).

### Structured evidence fields [OBSERVED RUNTIME]
Per-finding: `code` (SDC-NNN), `msg`, `line`, `line2`, `context`.
NOT present in these payloads: `identity` field (static analysis says it is
attached only on richer paths — constraint interactions/design-aware; snapshot
builders derive identity separately). FindingIdentity therefore remains
OBSERVED STATIC at runtime, not yet exercised via CLI here.

### Trust/scope behavior [OBSERVED RUNTIME]
`analysis_scope.status` + per-construct levels emitted as documented. The
minimal sample correctly classified NETLIST_REQUIRED (3 collection refs) —
scope machinery discriminates, does not rubber-stamp VALIDATED.

### Exit codes [OBSERVED RUNTIME partial]
0 (clean/warnings-only) and 1 (errors found) confirmed. Codes 2/3 not
triggered by safe tests → UNKNOWN (runtime), low adapter risk (documented +
statically consistent).

### Determinism [OBSERVED RUNTIME]
Byte-level equality across repeated identical invocations on tested path/input.
Scope: one command, one fixture, one machine, one session. Not a universal proof.

### Output/caching behavior [OBSERVED RUNTIME]
With PYTHONDONTWRITEBYTECODE=1 and external cwd: no writes inside Ṛta (dirty
count constant, no new untracked entries). Default behavior without these
precautions was NOT characterized (would risk mutation); adapters must retain
the precautions.

### LLM/probabilistic dependency [OBSERVED RUNTIME + STATIC]
No LLM/probabilistic dependency observed in the inspected execution paths
(check/analyze/MCP). Scoped claim — not a mathematical determinism proof.

### rta_generate boundary
Not invoked. EGER-DEC-006 stands unweakened. No change proposed.

## P001 ORACLE unknowns resolution

| ORACLE-001 UNKNOWN | Status after P006 |
|---|---|
| CLI end-to-end output formats | RESOLVED for check/analyze (--json) |
| Byte determinism of repeated runs | RESOLVED for tested path (byte-identical) |
| MCP handshake behavior | RESOLVED (initialize/ping/tools/list verified) |
| Readiness verdict strings at runtime | PARTIAL — readiness key present; verdict enum values not individually asserted |
| Performance on large designs | OPEN (out of P006 scope by design) |
| Custom-rules effect on identity stability | OPEN (excluded by frozen-config rule) |

## Remaining unknowns

Exit codes 2/3 at runtime; identity-field emission paths; netlist-aware mode;
baseline/gate invocation end-to-end; large-design performance; multi-run
determinism across sessions/machines. None block adapter design; the last four
belong to adapter validation, not characterization.

## Evidence artifacts

Raw outputs preserved at `research/oracle/runtime/`:
t1_help_stdout.txt, t2_check_help.txt, t2_analyze_help.txt,
t3_check_minimal_A.json, t3_check_minimal_B.json, t3_analyze_all.json,
t5_check_malformed.json (+err logs), t11_mcp_probe.jsonl,
t11_mcp_handshake.jsonl.
Recommendation: treat as **research evidence** (reproducibility anchors);
keep untracked until an artifact-retention policy exists, then commit a
pruned manifest set. They are not implementation artifacts.

## Safety verification

Ṛta modified NO · HEAD changed NO · branch changed NO · dirty count changed NO
(19→19) · files created inside Ṛta NO · configuration changes NO ·
EGER implementation modified NO · adapter created NO · contract modified NO.
