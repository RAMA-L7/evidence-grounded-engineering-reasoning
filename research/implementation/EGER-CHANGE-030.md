# EGER-CHANGE-030 — OpenSTA Oracle Feasibility Assessment

## Change ID

EGER-CHANGE-030

## Date

2026-09-03

## Gate

P160 — OpenSTA Oracle Feasibility & Adapter Design

## Summary

Feasibility and adapter-design gate only. Determined that OpenSTA is architecturally feasible through ADAPTER-ONLY changes, but three prerequisite conditions must be satisfied before implementation. Decision: REFINE.

---

## Baseline Commit

`1821aac` (P158 checkpoint)

## Files Inspected

| File | Purpose |
|------|---------|
| `eger/oracle/adapter.py` | EvidenceOracle — current Oracle boundary |
| `eger/oracle/schemas.py` | Oracle schemas and evidence format |
| `eger/evidence/schemas.py` | EvidenceArtifact, Finding contracts |
| `eger/evidence/normalizer.py` | EvidenceNormalizer — Oracle-to-evidence translation |
| `eger/verification/gate.py` | VerificationGate — sole authority |
| `eger/pipeline/e2e.py` | EGERPipeline — production orchestrator |
| `eger/revision/controller.py` | RevisionController — revision loop |
| `eger/contracts.py` | Shared size-limit constants |
| `eger/config.py` | EgerConfig — runtime configuration |
| `eger/logging.py` | EgerLogger — structured logging |

## Environment Assessment

| Check | Result |
|-------|--------|
| OpenSTA installed | NO |
| OpenSTA in PATH | NO |
| Verilog files in repo | NONE |
| Liberty files in repo | NONE |
| SDC files in repo | YES (in tests/experiments) |

## OpenSTA Suitability

**CONDITIONALLY SUITABLE** — architecturally feasible but prerequisites not met.

### Adapter Feasibility

**ADAPTER-ONLY** — no core EGER architecture changes required.

The EGER Oracle boundary (`OracleAdapter` → `OracleResult` → `EvidenceNormalizer` → `EvidenceArtifact`) is NOT Ṛta-specific. OpenSTA findings (timing violations) map cleanly to the existing Finding schema (error/warning/info severity).

## Decision

**REFINE** — Three conditions must be satisfied:

1. Install OpenSTA in the execution environment
2. Create minimal synthetic netlist + Liberty library for pilot tasks
3. Extend task configuration to carry netlist/library paths

## Implementation Changes

**NONE.** This is a feasibility and design gate. No OpenSTA adapter or experimental implementation was authorized or performed.

## Test Result

734/734 PASS (unchanged — no code modifications)

## Security Considerations

- No new attack surface
- No new secrets exposure
- Authority boundaries verified — OpenSTA is evidence-only

## Research-State Impact

NONE — no research conclusions changed.

## Ṛta Impact

NONE — Ṛta remains Oracle A (baseline). OpenSTA would be Oracle B (independent). Neither modifies the other.

## Future Recommendation

Proceed to P161 — OpenSTA Adapter Implementation after refinement conditions are met. If conditions cannot be met, reassess Oracle candidacy.

---

> P160 is a feasibility and adapter-design gate. No OpenSTA adapter or experimental implementation was authorized or performed.
