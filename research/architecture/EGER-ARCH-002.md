# EGER-ARCH-002 — Current Architecture Recommendation (Option C)

| Field | Value |
|---|---|
| ID | EGER-ARCH-002 |
| Produced by | EGER-P003 (2026-08-26), incorporating EGER-ORACLE-001 |
| Type | Architecture decision/recommendation — **NOT an experimental result** |
| Status | RECOMMENDED / PENDING FORMAL IMPLEMENTATION AUTHORIZATION |
| Supersedes | EGER-ARCH-001 for C0–C5 topology |

## Selected option

**Option C:** single probabilistic component for C0–C5; specialized subagents
introduced only in C6.

## C0–C5 architecture

```
EXPERIMENT DRIVER (deterministic script/fixed protocol; owns budgets, stopping)
      ▼
┌─ OpenCode runtime ────────────────────────────────────────────────┐
│ SINGLE PROBABILISTIC COMPONENT                                    │
│   "eger-engineer": one agent definition, one frozen system        │
│   prompt, frozen model+parameters across ALL conditions           │
│      │ emits Hypothesis / CandidateSDC typed artifacts            │
│      ▼                                                            │
│ [L1] ORACLE ADAPTER  deterministic subprocess wrapper around      │
│      pinned Ṛta v1.5.11; archives raw output; refuses exit 2/3    │
│      ▼                                                            │
│ [L2] STATE VALIDATOR  deterministic legal-transition table;       │
│      append-only journal; Evidence-ref + scope enforcement        │
│      (adopts Ṛta AnalysisScope statuses)                          │
│      ▼                                                            │
│ [L3] COMMIT GATE  deterministic; requires covering Evidence +     │
│      regression-clean Ṛta baseline diff; sole writer to verified  │
│      baselines                                                    │
│ PERMISSIONS: engineer has NO oracle exec, NO state-store write,   │
│ NO gate bypass, NO baseline write, NO rta_generate, NO git        │
└───────────────────────────────────────────────────────────────────┘
```

## Core rationale

1. **Agent count is not a declared C0–C5 independent variable.** Introducing
   multi-agent coordination would be an uncontrolled compound treatment.
2. **Deterministic authority boundaries are stronger than LLM identities:**
   a permission system cannot be persuaded; personas can. P7 survives with one
   probabilistic component because Proposal/Evidence/State/Authorization
   separation is enforced at tool boundaries.
3. **ORACLE-001 evidence:** Ṛta's structured JSON findings, stable identity,
   and trust scopes make an interpreter-agent unnecessary for C2–C5.

## Condition deltas (causal isolation)

| Transition | Added | Removed | Controls |
|---|---|---|---|
| C0→C1 | Oracle execution; findings as plain text | — | Text rendered deterministically from same JSON as C2 |
| C1→C2 | Structured JSON evidence | Text rendering | Same payload source; format-only difference |
| C2→C3 | [L2] state store ON + size-capped state digest in context | — | Digest cap fixed across C3–C5; memory OFF below C3 by config |
| C3→C4 | Frozen deterministic routing table (finding_code → procedure) | Next-action improvisation | Table versioned; derived only from `rta_rules()` catalog |
| C4→C5 | [L3] gate ON; all alternative baseline-write paths permission-denied | Direct write capability | Negative pre-test: unauthorized write must fail |

Constants across all conditions: model id/version, sampling settings, byte-frozen
system prompt, task instructions, benchmark version, oracle binary+version,
oracle flags (custom_rules OFF), token & tool-call budgets, retry policy,
stopping criteria, evaluation procedure, artifact schemas.

## Advantages

Cleanest variable isolation; one auditable prompt; lowest cost/latency variance;
centralized journal → EVR-computable observability; perfect phase separation
from C6; authority separation enforced structurally.

## Known limitations

- No context-isolation effect measurable before C6 (not a C0–C5 variable)
- Self-evaluation bias possible (single LLM interprets evidence about its own
  candidates); mitigated by validator finality, quantifiable at C6
- Single component = single point of sampling variance (mitigate: n≥3 per cell,
  frozen seeds where supported)

## Confounders registered

Sampling nondeterminism; prompt drift; context-length asymmetry from treatments
(intrinsic); oracle/benchmark drift; stopping-criteria gaming; routing-table
quality as hidden variable; environment variance. Full list + controls in the
P003 response §20.

## Open questions

See STATE.md (claim-registration mechanism, digest cap, seed policy, adapter
transport, contract freeze confirmation).

## Relationship to ARCH-001

Direct descendant: keeps ARCH-001's deterministic layers, artifact protocol,
config-variant strategy; removes two of three LLM roles; adds driver-owned
orchestration. Challenge history preserved in `EGER-ARCH-001.md`.

## Validation status

**Not validated.** This is a design recommendation grounded in architectural
analysis and static oracle reconnaissance. C0–C5 have not been executed. No
reliability claim is made or implied.
