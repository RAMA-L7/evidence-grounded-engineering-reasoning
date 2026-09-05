# EGER-P176 — Ṛta Scope-Alignment Implementation & Validation Gate

- **Gate**: P176 — Ṛta Scope-Alignment Implementation & Validation
- **Governing design**: P175 (`EGER-P175-RQ5-RTA-EVALUATION-SCOPE-PROTOCOL-RESOLUTION-001.md`) + CHANGE-047
- **Date**: 2026-09-05
- **Baseline**: `5c34b7ed0c958eeaa7b9b72b7780779985ac9552` (P175)
- **Decision**: **PASS**

---

## 1. Objective

Implement the approved P175 resolution and prove the complete real chain
end-to-end:

- One minimal production change: canonical evidence-scope values pass
  through `EvidenceNormalizer._map_scope` unchanged (raw vocabulary keeps
  mapping per the frozen SCOPE_MAP).
- Harness wiring: frozen P055 `DesignMetadata` on every Ṛta `validate()` call.
- Full-chain validation with real Ṛta for both frozen tasks, invalid
  references, OpenSTA stability, and raw-mapping stability.
- No Ṛta / VerificationGate / C0–C5 / historical-record changes.
- No PILOT-002 execution.

## 2. Changes

### 2.1 Production (single, P175-scoped change)

**`eger/evidence/normalizer.py` — `_map_scope`**

```text
BEFORE:
    return _SCOPE_MAP.get(raw_scope, "UNSUPPORTED")

AFTER:
    if raw_scope in VALID_EVIDENCE_SCOPE:
        return raw_scope
    return _SCOPE_MAP.get(raw_scope, "UNSUPPORTED")
```

`VALID_EVIDENCE_SCOPE` = {FULL, PARTIAL, INSUFFICIENT, UNSUPPORTED} — already
imported. Raw vocabulary (VALIDATED → FULL, PARTIALLY_VALIDATED → PARTIAL,
NETLIST_REQUIRED → INSUFFICIENT, NOT_VALIDATED / TCL_EXECUTION_REQUIRED →
UNSUPPORTED) is unchanged. OpenSTA (stores raw "VALIDATED") is unaffected.

### 2.2 Harness wiring (P175 §5)

- **`harness/simple_path.design_metadata.json`** (new): frozen P055
  DesignMetadata for the P163 substrate — ports `clk` (clock input),
  `data_in` (data input), `data_out` (data output); clock `clk`; cells
  `u_inv`/`u_and`/`u_ff` (from the actual netlist). Format mirrors the
  BENCH-002 `evaluator_context` convention.
- **`harness/providers.py`**: `load_simple_path_design_metadata()` loads the
  JSON; `build_rta_oracle_call()` now passes `design_metadata=` on every
  `EvidenceOracle.validate()` call (default: the frozen metadata). The
  metadata is never exposed to the model.

### 2.3 Experiment-layer fail-closed lever (invalid references)

Real-chain testing showed the FROZEN VerificationGate **accepts PARTIAL
scope with zero ERROR findings** (existing contract —
`test_evidence_scope_partial_accepted`), and netlist-less Ṛta emits no
error for an unknown port reference. The P055 metadata validation still
detects the invalid reference (FULL elevation denied → PARTIAL). Rejecting
that case at the gate would require a gate change, which P176 forbids.
Per the P172 §13 layered-defense precedent (NO_TIMING_CONSTRAINT), the
fail-closed lever is therefore at the experiment layer:

- **`harness/trial_runner.py`**: `oracle_summary` exposes
  `metadata_all_validated` (from the adapter provenance's P055
  `metadata_validation` block); `derive_trial_metrics` returns
  `metadata_unqualified_iterations` (Ṛta iterations whose successful
  evaluation had `all_validated == False`). The future PILOT-002 analysis
  uses this flag to exclude unqualified accepts.

## 3. Full-Chain Validation (real Ṛta 1.5.11 @ 3b5c2f2)

`harness_tests/test_rta_full_chain.py` (new, 8 tests) runs the complete real
chain per trial:

```
Ṛta (netlist-less check --json)
  → EvidenceOracle.validate(design_metadata=…)
  → EvidenceNormalizer
  → VerificationGate
```

| Case | Adapter scope | Metadata all_validated | Ṛta error findings | Normalized | Gate |
| ---- | ------------- | ---------------------- | ------------------ | ---------- | ---- |
| T1 incomplete (clock only)        | FULL | True  | SDC-005, SDC-006 | FULL | **REJECT** |
| T1 completed (I/O delays added)   | FULL | True  | none              | FULL | **ACCEPT** |
| T2 initial (0.05 ns clock only)   | FULL | True  | SDC-005, SDC-006 | FULL | **REJECT** |
| T2 completed at 0.05 ns           | FULL | True  | SDC-008, SDC-009 | FULL | **REJECT** |
| T2 completed, relaxed to 10 ns    | FULL | True  | none              | FULL | **ACCEPT** |
| Invalid reference (`nonexistent_pin`) | **PARTIAL** | **False** | none | PARTIAL | ACCEPT (frozen PARTIAL contract; flag test asserts experiment-layer lever) |

Before the P175/P176 fix, every row normalized to UNSUPPORTED and gated
REJECT regardless of content (the floor). The Ṛta arm now discriminates both
frozen tasks through Ṛta's own constraint-quality rules.

## 4. Stability Guards

**`tests/test_normalizer_canonical_scope.py`** (new, 14 tests):

- Canonical pass-through: FULL/PARTIAL/INSUFFICIENT/UNSUPPORTED →
  themselves (4).
- Raw mappings unchanged: VALIDATED→FULL, PARTIALLY_VALIDATED→PARTIAL,
  NETLIST_REQUIRED→INSUFFICIENT, NOT_VALIDATED→UNSUPPORTED,
  TCL_EXECUTION_REQUIRED→UNSUPPORTED, unknown→UNSUPPORTED (6).
- Normalize() of canonical-scope artifacts (mock Ṛta adapter output)
  preserves FULL/PARTIAL/INSUFFICIENT and preserves findings/severity (4).

OpenSTA stability: unchanged behavior confirmed by the existing 864-test
suite (OpenSTA adapter tests, pipeline tests, smoke re-run: VALIDATED →
FULL, WNS 0.0, ACCEPT).

## 5. Regression

| Suite | Command | Result |
| ----- | ------- | ------ |
| EGER full suite | `python -m pytest tests -q` | **878 passed** (864 baseline + 14 new) |
| Harness suite | `python -m pytest research/experiments/EGER-RQ5-PILOT-001/harness_tests -q` | **52 passed** (44 baseline + 8 new full-chain/flag) |

No existing assertion changed — confirming the alignment is behavior-neutral
for raw vocabulary and for OpenSTA.

## 6. Runtime Smoke (P174 readiness re-run)

Re-ran `run_smoke_readiness.py` (real model + real Oracles):

- **Ṛta arm (T1)**: initial incomplete SDC → FULL scope, 2 error findings
  (SDC-005/006), metadata all-validated; model candidate (VALID_SDC, clock
  defined) → FULL scope, 0 errors → VerificationGate **ACCEPT**. The P174
  REJECT-on-scope floor is gone; the Ṛta arm now exercises genuine
  REJECT→ACCEPT revision behavior.
- **OpenSTA arm (T1)**: unchanged — VALIDATED → FULL, WNS 0.0 measured,
  ACCEPT.

Model artifacts cleaned after the run; readiness record kept local.

## 7. Files Changed

| File | Change |
| ---- | ------ |
| `eger/evidence/normalizer.py` | `_map_scope` canonical pass-through (the only production change) |
| `harness/providers.py` | metadata loader + `design_metadata=` wiring in `build_rta_oracle_call` |
| `harness/trial_runner.py` | `metadata_all_validated` in `oracle_summary`; `metadata_unqualified_iterations` in `derive_trial_metrics` |
| `harness/simple_path.design_metadata.json` | NEW frozen P055 metadata |
| `harness_tests/test_rta_full_chain.py` | NEW 8 real-chain tests |
| `tests/test_normalizer_canonical_scope.py` | NEW 14 stability tests |

## 8. Research Boundary

```text
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: NO
C0-C5 conclusions changed: NO
Oracle comparison performed: NO
VerificationGate authority changed: NO
Epistemic-state logic added: NO
Authorization logic added: NO
PILOT-002 executed: NO
```

## 9. Residual Risk (documented, out of P176 scope)

- A candidate referencing a nonexistent port reaches PARTIAL evidence scope
  (invalid reference detected by metadata) but the FROZEN gate accepts
  PARTIAL-with-zero-errors. The experiment-layer
  `metadata_unqualified_iterations` flag is the fail-closed lever; whether
  PILOT-002 counts such accepts is a future-experiment-design decision.
- The synthetic substrate, WSL2 requirement, agent-mode model prompt
  sensitivity, and OpenSTA T1 floor effect remain as previously recorded.

## 10. Decision

```text
PASS
```

All validation items pass: T1/T2 discriminations proven on the real chain,
invalid references detectable (PARTIAL) with an experiment-layer flag,
OpenSTA unchanged, raw mappings unchanged, full regression green (878/878
EGER + 52/52 harness), runtime smoke shows the Ṛta arm reaching ACCEPT at
FULL scope. No research boundary crossed. PILOT-002 not executed.

## 11. Git

- Commit: `(P176 commit, see git log)`
- HEAD == origin/main: YES
- `Universal_Principles_Library/` untouched
- Local-only: `raw_trials.json`, `analysis.json`, `qualification_record.json`,
  `smoke_readiness_record.json`
