# EGER-ARCH-001 — Initial Minimum-Sufficient Subagent Architecture

| Field | Value |
|---|---|
| ID | EGER-ARCH-001 |
| Produced by | EGER-P001 (~2026-08-26) |
| Type | Architecture proposal |
| Status | **SUPERSEDED FOR C0–C5** by EGER-ARCH-002 (challenged by EGER-P003). Preserved per P8 / Integrity Rule 4. |
| Classification | ARCHITECTURE DECISION — never an experimental result |

## Summary

Original topology: **3 LLM subagents + 3 deterministic layers.**

```
supervisor (LLM, orchestration)
    ├── proposer  (LLM: hypotheses + candidate SDC)
    ├── analyst   (LLM: evidence interpretation → proposed EpistemicUpdates)
    ├── [L1] eger-oracle adapter (deterministic, wraps Ṛta CLI)
    ├── [L2] eger-state validator + JSON journal (deterministic)
    └── [L3] eger-gate commit gate (deterministic)
```

Design axiom: *every authority that can be deterministic must be deterministic.*
Only Proposal required an LLM; Evidence/State/Authorization were realized as
tooling from the start.

## What survived the P003 challenge unchanged

- Deterministic three-layer decomposition (L1/L2/L3) — now the backbone of ARCH-002
- Per-condition config variants c0–c5 as ablation toggles
- Typed artifact protocol idea and append-only epistemic journal
- Adopting Ṛta `AnalysisScope` trust statuses as EGER's scope vocabulary
- Adapter-only Ṛta boundary; Critic deferral; permission-matrix discipline

## What was superseded, and why

The supervisor and analyst LLM roles. EGER-P003 found they test **no declared
C0–C5 independent variable**: agent count is not among contract §10 variables,
and ORACLE-001 showed structured evidence + machine-readable scope let a single
LLM consume evidence directly while deterministic layers retain final authority.
Three prompt systems and inter-agent channels constituted uncontrolled
confounders (compound treatment).

## Historical significance

ARCH-001 is the origin of EGER's central implementation insight (authorities
that can be deterministic should be). Its supersession demonstrates the
project's falsification discipline: an architecture proposed by the same
process was challenged and reduced when it failed the minimization standard.

Full original text lives in the EGER-P001 conversation transcript (not archived
verbatim in-repo); this record preserves the material content.
