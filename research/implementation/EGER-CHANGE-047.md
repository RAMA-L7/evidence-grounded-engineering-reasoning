# EGER-CHANGE-047

- **Gate**: P175 — RQ-5 Ṛta Evaluation-Scope Protocol Resolution
- **Baseline**: `9a3cdc72552a3ae2a473b95206c02d7760bdeccf` (P174)
- **Purpose**: Resolve the P174-conditioned blocker — the Ṛta arm's
  permanent REJECT floor — so a future RQ-5 replication can validly use Ṛta.
- **Decision**: **GO** (protocol resolved; implementation delegated to a
  future gate; PILOT-002 still requires separate authorization).

## Root cause established (empirically, read-only)

The EvidenceNormalizer maps only RAW scope vocabulary
(`VALIDATED`/`PARTIALLY_VALIDATED`/`NETLIST_REQUIRED`/…) and falls back to
`UNSUPPORTED` for anything else. The Ṛta adapter stores CANONICAL
vocabulary (`INSUFFICIENT`/`FULL`/`PARTIAL`). Therefore every Ṛta
evaluation — including the P055 design-metadata elevation to FULL —
normalizes to `UNSUPPORTED` and fail-closes REJECT at the gate. The OpenSTA
adapter avoids this by storing raw `"VALIDATED"`. No test exercised the full
Ṛta→normalizer→gate chain with canonical scope, so the inconsistency was
silent.

## Option comparison (empirical)

| Option | Raw status | Adapter scope | Normalized (current) | Verdict |
| ------ | ---------- | ------------- | -------------------- | ------- |
| 1. Netlist-less (status quo) | NETLIST_REQUIRED | INSUFFICIENT | UNSUPPORTED | REJECT floor — invalid |
| 2. Netlist-augmented | VALIDATED | FULL | UNSUPPORTED | Same blocker + adapter invocation change + authority-lane blur — rejected as primary |
| 3. Netlist-less + P055 design_metadata | NETLIST_REQUIRED | FULL/PARTIAL | UNSUPPORTED | Same blocker, but otherwise harness-only — **ADOPTED** |

## Resolution decision

Adopt Option 3: keep Ṛta's FROZEN netlist-less invocation and constraint-
quality semantics; pass frozen P055 `DesignMetadata` from the harness so the
adapter elevates scope to FULL for valid-reference SDCs; align the
EvidenceNormalizer so canonical scope values pass through instead of
mapping to UNSUPPORTED.

Simulated end-to-end with real Ṛta (netlist-less + metadata + canonical
pass-through): T1/T2 incomplete → REJECT (SDC-005/006); T2 completed at
0.05 ns → REJECT (SDC-008/009, I/O delay ≥ clock period); completed/relaxed
→ ACCEPT. Both frozen tasks drive genuine revision through Ṛta's own
property; PO-3 becomes measurable; OpenSTA unaffected; VerificationGate
unchanged; authority separation preserved.

## Required implementation gate (before any PILOT-002)

1. `eger/evidence/normalizer.py` `_map_scope`: canonical pass-through
   (design in P175 §5).
2. New full-chain regression test (Ṛta FULL → gate decision on findings).
3. `harness/providers.py`: pass frozen DesignMetadata on Ṛta oracle calls.
4. Confirm 864-test regression unchanged + new Ṛta discrimination fixture.
5. Re-run the P174 Ṛta-arm readiness smoke.

## Research boundaries

```text
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: NO
C0-C5 conclusions changed: NO
Oracle comparison performed: NO
VerificationGate authority changed: NO
EGER production code modified: NO (design only)
PILOT-002 executed: NO
```

## Files

- Added: `research/implementation/EGER-P175-RQ5-RTA-EVALUATION-SCOPE-PROTOCOL-RESOLUTION-001.md`
- Added: `research/implementation/EGER-CHANGE-047.md`
