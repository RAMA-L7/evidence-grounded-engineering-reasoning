# Adapted Subagents — Research on EGER (freebuff-style)

> Source: `D:\freebuff\rta-constraint-intelligence\.claude\agents/` holds 5 freebuff agents (`code-reviewer`, `test-writer`, `security-reviewer`, `docs-generator`, `refactor-helper`), adapted here for EGER, Evidence-Grounded Engineering Reasoning (`eger/` 13 modules + `research/` + `tests/` 30 files).
> Installed at `D:\Research on EGER\.opencode\agents/` (7 for OpenCode, `mode: subagent`, `color: #RRGGBB`) and `D:\Research on EGER\.claude\agents/` (7 for Claude Code, `model: auto/best-coding`, `tools: [...]`). The logic is identical; only the frontmatter differs between the two hosts. `humanizer` is included as a cross-project addition.
> Verified: `opencode agent list | Select-String "(subagent)"` shows `eger-code-reviewer (subagent)`, `humanizer (subagent)`, and the rest. The freebuff pattern `tools: [Read, Grep, Glob, Bash]` is preserved in the `.claude` variants.
> Research invariant: `README.md:9` gives the LLM proposal authority only, and `VerificationGate` `eger/verification/gate.py:9` is the sole ACCEPT/REJECT authority. The adapted agents enforce this separation.

## Pipeline (for mapping)
`TaskDefinition eger/task/definition.py` → `PromptBuilder eger/prompting/builder.py:eager.prompt.v1` → `ProposalGenerator eger/engineer/adapter.py` (LiveEngineerModel `opencode/muse-spark-1.2`) → `CandidateArtifact eger/engineer/candidate.py` → `OracleAdapter eger/oracle/adapter.py (Ṛta 1.5.11 @ 3b5c2f2 / OpenSTA)` → `EvidenceNormalizer eger/evidence/normalizer.py` deterministic `same input→same EvidenceArtifact` → `EvidenceArtifact eger/evidence/schemas.py` → `RevisionController eger/revision/controller.py` → `VerificationGate eger/verification/gate.py:43 evaluate() → ACCEPT/REJECT` → `ProvenanceTracker eger/provenance/tracker.py:113 append-only` → `RunProvenance` + `research/STATE.md` frozen `C0 ESTABLISHED` etc.

---

## How many are required: 5 adapted + 1 EGER extension + Humanizer = 7

Freebuff provides 5 generic SDC agents. EGER needs those 5 re-domained, plus 1 research-specific provenance auditor with no freebuff equivalent, plus `humanizer` (user block, cross-project). A minimum of 5 works; 7 is the recommended set for auditable research with humanized prose.

| # | Adapted slug | Freebuff source `D:\freebuff\...\agents\<name>.md:1` | File `D:\Research on EGER\.opencode\agents/<slug>.md:1` / `.claude` | Why required for EGER (gap → value) |
|---|---|---|---|---|
| 1 | `eger-code-reviewer` | `code-reviewer.md:1` `Reviews Python code for bugs, cross-module impacts` `tools: [Read,Grep,Glob,Bash]` | `.opencode/eger-code-reviewer.md:1` `.claude/eger-code-reviewer.md:1` | Owns `eger/` 13 modules + 30 tests cross-impact. SDC `checker.py 40 rules` → EGER `EvidenceNormalizer` fail-closed `eger/evidence/normalizer.py:10` + `VerificationGate` sole authority `eger/verification/gate.py:9` + `EGER-DEC-006` no `rta_generate` on Evidence path. Prevents `CandidateArtifact` mutation `eger/contracts.py:30` `MAX_SDC_TEXT_LENGTH 100k` bypass. |
| 2 | `eger-evidence-reviewer` | `security-reviewer.md:1` `Reviews SDC Tools code for safety, silicon failure` | `eger-evidence-reviewer.md:1` | Owns deterministic evidence path. Freebuff `missing clock → silicon failure` → EGER `missing ERROR → false ACCEPT` `eger/verification/gate.py:93` if `error_count>0`. Checks `OracleAdapter` byte-determinism `stdout/stderr/exit_code` pinned `Ṛta @ 3b5c2f2` `eger/oracle/adapter.py:1`, scope mapping `VALIDATED→FULL` `eger/evidence/normalizer.py:63`, authority separation `README.md:72` LLM≠Gate. |
| 3 | `eger-test-writer` | `test-writer.md:1` `Generates pytest tests following project conventions` | `eger-test-writer.md:1` | Owns deterministic-layer tests. Freebuff `conftest.py buggy_sdc` → EGER `eger/contracts.py:16` `MAX_*` bounds + `EgerConfig` frozen `eger/config.py:106` validation before Oracle/LLM. Generates `tests/test_evidence_oracle.py` 14/14, `test_verification_gate.py` `SUCCESS+FULL+0→ACCEPT` vs `ORACLE_FAILURE→INCOMPLETE_MEASUREMENT`. Preserves `47/47` (P010) / `63/63` (P025) regression. |
| 4 | `eger-docs-generator` | `docs-generator.md:1` `Generates README, docstrings, inline comments` | `eger-docs-generator.md:1` | Owns research ledger. Freebuff `README` → EGER `research/STATE.md` frozen `C0 ESTABLISHED C1 ESTABLISHED C3 NOT JUSTIFIED` `research/STATE.md:141`, `README.md:98` limitations verbatim, `research/implementation/EGER-CHANGE-*.md` 60 records. Enforces no overclaim (`model independence` not established `README.md:104`), docstring `INVARIANT:` + `PRODUCER/CONSUMER` `eger/verification/gate.py:1`. |
| 5 | `eger-refactor-helper` | `refactor-helper.md:1` `Helps refactor — renames, extracts, restructures while preserving behavior` | `eger-refactor-helper.md:1` | Owns composition boundaries `eger/pipeline/e2e.py:14` — cannot bypass Oracle→Evidence→Gate. Freebuff `grep before rename` → EGER `grep` before moving `VerificationGate` decision out of `eger/verification/gate.py:29` or mutating `Ṛta @ 3b5c2f2` (`.gitignore` excluded). Preserves `config_hash` `eger/config.py:196` determinism. |
| 6 | `eger-provenance-auditor` | **No freebuff equivalent — EGER-specific** | `eger-provenance-auditor.md:1` | **Beyond freebuff 5:** research requires auditable proof LLM did not decide ACCEPT. Freebuff has no `ProvenanceTracker` concept. Owns `eger/provenance/tracker.py:113` append-only `record()` `tracker.py:414`, hash trio `hashlib.sha256` `tracker.py:50`, lifecycle `EVENT_RUN_STARTED→RUN_COMPLETED` `tracker.py:37` `_VALID_ORDER`, `reconstruct_run()` `tracker.py:351` deterministic. Zero decision authority `tracker.py:123`. |
| 7 | `humanizer` | **User block — cross-project** | `humanizer.md:1` | **New per user request:** removes AI tells (Zero-Tolerance em dashes, `tapestry/delve/crucial`, `serves as→is`, triads) from `research/STATE.md` + `eger/` docstrings without inventing `Ṛta 1.5.11 @ 3b5c2f2` `README.md:98` or `p=0.162` `research/STATE.md:156`. See `AGENTS.md:1` + `D:\Research on EGER\.opencode\agents/humanizer.md:1`. |
| — | `Unselected` | freebuff SDC `wildcard_analyzer`, `sdc-tools` streamlit | — | Out-of-scope for EGER frozen `BENCH-002 v0.1` 6 CLEAN tasks. |

Count: 5 direct adaptations cover code, evidence, tests, docs, and refactoring. The 6th, `provenance-auditor`, is mandatory for research auditability; without it, the RQ-4 `behavioral-association` finding versus causality `README.md:22` cannot be defended. The 7th, `humanizer`, is a user-supplied cross-project editor.

---

## How freebuff uses subagents, and how EGER now does

### freebuff original (`D:\freebuff\rta-constraint-intelligence\.claude\agents/*.md:1`)
```yaml
---
name: code-reviewer
description: Reviews Python code for bugs, cross-module impacts...
model: auto/best-coding
tools: [Read, Grep, Glob, Bash]
---
```
- Location: `.claude/agents/` (Claude Code). SDC Tools is stdlib-only, with optional `pyyaml`/`streamlit`.
- Invocation (Claude Code): the primary model (Sonnet/Opus) auto-delegates when the prompt matches `description` (“review this SDC checker change”), or the user forces it with `> code-reviewer review checker.py`. The subagent runs with only the listed `tools`, returns ranked `🔴 Critical / 🟡 Warning / 🔵 Info`, and the primary merges the result.
- Output: `✅ Code looks clean`, or a ranked list `### 🔴 Critical 1. [file:line] bug` (`code-reviewer.md:85`).
- Workflow: `git diff`, then `grep` imports, then `pytest`, then report (`code-reviewer.md:100`).

### EGER adapted (dual install for freebuff compatibility)
| Tool | Location | Frontmatter | Invoke | Example |
|---|---|---|---|---|
| **Claude Code** (freebuff-native) | `D:\Research on EGER\.claude\agents/eger-*.md:1` | `model: auto/best-coding` `tools: [Read,Grep,Glob,Bash(,Write,Edit)]` (same as freebuff) | Auto on `description` match or `> eger-code-reviewer review eger/evidence/normalizer.py` | `> eger-evidence-reviewer check Oracle scope mapping` → subagent runs, primary shows `🔴` |
| **OpenCode** (this project’s `freebuff` use) | `D:\Research on EGER\.opencode\agents/eger-*.md:1` | `name: 'EGER Code Reviewer'` `description: ...` `mode: subagent` `color: '#3498DB'` (converted — `tools` stripped, hex added per `agency-agents` `scripts/convert.sh:242 resolve_opencode_color`) | OpenCode TUI: `@eger-code-reviewer review eger/verification/gate.py` or auto-delegate when you say “review EGER gate authority” | `@eger-test-writer generate test for EgerConfig bounds` → subagent writes `tests/test_config_logging.py` |

Key difference: the 5 freebuff agents are generic SDC reviewers, while the 7 EGER agents are authority-aware (`VerificationGate` sole decider `eger/verification/gate.py:9`, `EvidenceNormalizer` cannot invent `eger/evidence/normalizer.py:10`, `ProvenanceTracker` zero authority `eger/provenance/tracker.py:123`), with `humanizer` in Wikipedia style. Same `tools` discipline, different checklists.

---

## How to verify they work (observable)

```powershell
# 1. Freebuff source still there
Get-ChildItem D:\freebuff\rta-constraint-intelligence\.claude\agents | Format-Table Name

# 2. EGER adapted installed (both tools)
Get-ChildItem D:\Research on EGER\.opencode\agents | Format-Table Name  # 7
Get-ChildItem D:\Research on EGER\.claude\agents | Format-Table Name   # 7
Get-Content D:\Research on EGER\.opencode\agents\eger-code-reviewer.md -TotalCount 6
Get-Content D:\Research on EGER\.claude\agents\eger-code-reviewer.md -TotalCount 6

# 3. Registered in OpenCode (mode: subagent)
opencode agent list | Select-String "eger-"

# 4. Trigger in TUI (visible header shows subagent name)
# In OpenCode TUI: @eger-code-reviewer review eger/verification/gate.py
# In Claude Code: > eger-evidence-reviewer check evidence_scope mapping

# 5. API emulation (this chat): I `read .opencode/agents/eger-*.md` and embody — say `use @eger-test-writer to write test for EgerConfig MAX` to see file write in tests/
```

The full freebuff 5 to EGER 7 mapping is kept at `D:\Research on EGER\.opencode\agents/` and `D:\Research on EGER\.claude\agents/`; trim it via `opencode agent list` if you hit future caps.

Update this file when `eger/contracts.py:16` limits or `research/STATE.md:141` statuses change.
