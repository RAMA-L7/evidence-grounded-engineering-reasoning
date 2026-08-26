# EGER-PROMPT-001 — Prompt & Template Freeze

| Field | Value |
|---|---|
| ID | EGER-PROMPT-001 |
| Status | FROZEN v1 |
| Date | 2026-08-26 |
| Implementation | `eger/engineer/adapter.py` (`PROMPT_VERSION = "eger.prompt.v1"`) |

## Prompt Identifier

`eger.prompt.v1` (PROMPT_VERSION constant in `eger/engineer/adapter.py`).

## Version & Hash

- `PROMPT_VERSION = "eger.prompt.v1"`
- System instructions hash: `SHA256(SYSTEM_INSTRUCTIONS)` — compute at build time and record in every `ModelResponse.prompt_hash` / `CandidateArtifact.provision.prompt_hash`
- Template change → new version `eger.prompt.v2` + `EGER-CHANGE-###`

## System Instructions (exact, frozen)

```
You are an SDC generation assistant. Given the engineering context, produce a candidate SDC. Output SDC inside a ```sdc code block. Do not claim the candidate is validated.
```

This neutral prompt is the **control prompt** for all conditions in P011. No C0–C5-specific wording is present at this version.

## Task Prompt Template (frozen structure)

```
{SYSTEM_INSTRUCTIONS}

Design context:
{design_context}

Existing SDC:
{existing_sdc}

Objective:
{objective}

Deterministic evidence (read-only, not authoritative):
{evidence_summary}        // only in C1–C5 per capability matrix

Epistemic state (read-only):
{epistemic_state}         // only in C3–C5 per capability matrix
```

Fields not applicable to a condition are **omitted entirely** (not blank placeholders).

## Variable Fields

- `design_context` — minimal RTL/design text per benchmark task (never research ledger/STATE dumps)
- `existing_sdc` — prior candidate when revising (may be empty on first attempt)
- `objective` — per-task engineering objective string
- `evidence_summary` — deterministic `EvidenceArtifact` rendered as controlled text (only C1–C5 as per matrix)
- `epistemic_state` — deterministic read-only state snapshot (only C3–C5)

## Input Context Specification

Per §14 of the protocol: only task-relevant engineering context is supplied. `RESEARCH_LEDGER.md` / `STATE.md` / literature PDFs are **never** included as hidden context.

## Output Format

- Expected: SDC inside ```sdc (or ```tcl) fenced block, or lines containing SDC keywords.
- Extraction: deterministic `eger/engineer/candidate.py` (`_extract_sdc_block`) — code fence → keyword line scan → fallback raw, no LLM, no semantic guessing.

## Evidence/Epistemic/Authorization Presentation Templates

Frozen as deterministic renderers (not separate prompts) that convert typed artifacts to read-only text for the Engineer where the capability matrix allows:

- **Evidence:** `EvidenceArtifact.evidence_scope`, `findings[code/msg/line]`, `analysis_scope.status` rendered verbatim.
- **Epistemic:** `EpistemicClaim.state`, `supporting_evidence_ids`.
- **Authorization:** `APPROVED`/`REJECTED` decision text.

These templates are versioned with `eger.prompt.v1`; changing them → `v2`.

## Hash

- `prompt_hash = SHA256(full prompt as composed for the run)` — stored in `ModelResponse.prompt_hash` and `CandidateArtifact.provision.prompt_hash`
- `PROMPT_VERSION` stored in both as well — a hash collision without version bump is not silently accepted

## Change Policy

No prompt/template modifications after formal execution begins without new protocol version (`v0.2`) and `EGER-CHANGE-###`. This includes evidence/epistemic presentation wording.

## Condition-Specific Content

No C0–C5-specific content is present at `v1`. Future condition-specific prompts will be explicit condition branches with their own versioned templates, not silent edits to `v1`.
