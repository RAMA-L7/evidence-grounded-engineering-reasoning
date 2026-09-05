# EGER-P175 — RQ-5 Ṛta Evaluation-Scope Protocol Resolution

- **Gate**: P175 — RQ-5 Ṛta Evaluation-Scope Protocol Resolution
- **Predecessor**: P174 (readiness — READY, conditioned on resolving the Ṛta scope question)
- **Date**: 2026-09-05
- **Baseline**: `9a3cdc72552a3ae2a473b95206c02d7760bdeccf` (P174 checkpoint)
- **Decision**: **GO** — the Ṛta evaluation-scope blocker is resolved at the
  protocol-design level. Implementation (a minimal normalizer alignment plus
  harness metadata wiring) must occur in a dedicated implementation gate
  before any PILOT-002 run; PILOT-002 itself still requires separate
  authorization.

---

## 1. Objective

Determine whether a future RQ-5 experiment can validly use Ṛta under its
netlist-less `INSUFFICIENT`-scoped evaluation, and resolve how the Ṛta
condition should produce FULL-scope, gate-evaluable evidence. Compare the
three candidate approaches empirically and read-only. No experiment, no
Ṛta/VerificationGate modification, no implementation.

## 2. Problem Restatement

P174's real-provider smoke showed the Ṛta arm reaching the VerificationGate
with `UNSUPPORTED` normalized scope on every evaluation, fail-closing to
REJECT regardless of candidate content. This is a permanent REJECT floor:
PO-3 is unmeasurable, the revision loop cannot demonstrate improvement, and
the Ṛta condition cannot contribute to RQ-5.

## 3. Empirical Investigation (all read-only)

### 3.1 Options probed on the frozen task SDCs

Probed with the pinned Ṛta 1.5.11 CLI (`check --json`, cwd outside Ṛta)
and through the FROZEN EGER adapter (`EvidenceOracle.validate`) on the
P163 substrate:

| Option | Ṛta raw `analysis_scope.status` | Adapter `evidence_scope` | Current normalized scope | Gate (current) |
| ------ | ------------------------------- | ------------------------ | ------------------------ | -------------- |
| **1. Netlist-less `check --json` (status quo)** | `NETLIST_REQUIRED` | `INSUFFICIENT` (SCOPE_MAP) | **`UNSUPPORTED`** | REJECT always |
| **2. Netlist-augmented (`--netlist simple_path.v --top simple_path`)** | `VALIDATED` | `FULL` (SCOPE_MAP) | **`UNSUPPORTED`** | REJECT always |
| **3. Netlist-less + P055 `design_metadata`** | `NETLIST_REQUIRED` | `FULL`/`PARTIAL` (elevated) | **`UNSUPPORTED`** | REJECT always |

All three raw CLI behaviors are deterministic and reproducible.

### 3.2 Root cause — latent vocabulary inconsistency in the evidence chain

The `EvidenceNormalizer._map_scope` maps only **raw** scope-status
vocabulary (`VALIDATED`, `PARTIALLY_VALIDATED`, `NETLIST_REQUIRED`,
`UNSUPPORTED`, …) and returns `UNSUPPORTED` for anything else. The Ṛta
adapter stores **canonical** vocabulary (`INSUFFICIENT`, `FULL`, `PARTIAL`,
`UNSUPPORTED`) on `EvidenceArtifact.evidence_scope` (it applies `SCOPE_MAP`
itself in `_build_success`). Therefore **every** Ṛta evaluation — including
the P055 design-metadata elevation to FULL — normalizes to `UNSUPPORTED`
and fail-closes REJECT.

Evidence for the inconsistency:

- `test_evidence_oracle.py` asserts the Ṛta **adapter** emits canonical
  scope (`evidence_scope == SCOPE_MAP[analysis_scope["status"]]`) and stops
  there — no full-chain assertion.
- `test_evidence_pipeline.py` asserts the **normalizer** only against raw
  vocabulary inputs.
- No test exercises the full Ṛta-adapter → normalizer → gate chain with
  canonical scope — the integration gap is untested and silent.
- The OpenSTA adapter avoids the trap by storing **raw** `"VALIDATED"`,
  which the normalizer maps to FULL (P164-era tests cover this path).

### 3.3 Discrimination restored (simulated end-to-end)

Simulated the designed fix (canonical values pass through `_map_scope`),
then ran the full chain with real Ṛta (netlist-less) + frozen P055
`design_metadata` (ports `clk/data_in/data_out`, clock `clk`, cells
`u_inv/u_and/u_ff`) + EvidenceNormalizer + VerificationGate:

| Candidate | Metadata | Adapter scope | Ṛta error findings | Gate |
| --------- | -------- | ------------- | ------------------- | ---- |
| T1 initial (clock only)          | all_validated | FULL | SDC-005, SDC-006 (no input/output delay) | **REJECT** |
| T1 completed (I/O delays added)  | all_validated | FULL | none                              | **ACCEPT** |
| T2 initial (0.05 clock only)     | all_validated | FULL | SDC-005, SDC-006                  | **REJECT** |
| T2 completed at 0.05 ns          | all_validated | FULL | **SDC-008, SDC-009** (I/O delay ≥ clock period) | **REJECT** |
| T2 completed, clock relaxed to 10 ns | all_validated | FULL | none                          | **ACCEPT** |

Findings decoded from the Ṛta rules registry: SDC-005 = "No Input Delay",
SDC-006 = "No Output Delay", SDC-008 = "Input Delay ≥ Clock Period",
SDC-009 = "Output Delay ≥ Clock Period".

**Result:** with netlist-less Ṛta + design_metadata + canonical pass-through,
the Ṛta condition discriminates BOTH frozen tasks:

- T1: the model must add the missing I/O delays (SDC-005/006 → 0 errors).
- T2: the model must relax the aggressive 0.05 ns clock (SDC-008/009 → 0
  errors) — the SAME revision gradient OpenSTA drives via negative slack,
  detected through Ṛta's own constraint-quality property.

PO-3 (initial vs final Oracle error count) becomes measurable for Ṛta.

## 4. Option Assessment

### Option 1 — status quo netlist-less check, no metadata

Invalid for RQ-5: permanent REJECT floor, no discrimination, PO-3
impossible. Rejected.

### Option 2 — netlist-augmented Ṛta evaluation

Mechanically works at the raw level (`VALIDATED` → FULL) but **still hits
the same normalizer blocker** (adapter maps raw→canonical; normalizer
remaps canonical→UNSUPPORTED). Additionally it would require changing the
FROZEN Ṛta invocation discipline (`check <file> --json`, per
EGER-ORACLE-CONTRACT-001) to add `--netlist`/`--top`, and feeding Ṛta a
netlist adds structural/timing-relevant context that edges Ṛta toward
OpenSTA's evaluation lane, weakening the authority-property separation that
the RQ-5 design depends on. Rejected as the primary approach; documented as
the fallback only if a future gate prefers Ṛta's netlist mode.

### Option 3 — scope-preserving: netlist-less Ṛta + FROZEN P055 design_metadata — **ADOPTED**

- Ṛta invocation stays netlist-less and FROZEN (`check <file> --json`).
- The harness passes frozen `DesignMetadata` for the substrate (ports,
  clock, cells) to the existing `EvidenceOracle.validate(design_metadata=…)`
  — the FROZEN P055 mechanism already used by the RQ-4-era runner (per
  `test_rq4_runner.py`, which asserts FULL/PARTIAL adapter scopes with
  design_metadata). No Ṛta change; no adapter change.
- ONE minimal production change is required: the EvidenceNormalizer must
  accept canonical scope values instead of remapping them to UNSUPPORTED
  (fixing the latent vocabulary inconsistency — see §5).

Authority separation is preserved: Ṛta continues to evaluate the SDC as
constraint text against its rule catalog (SDC-005/006/008/009 …) plus
evaluator-side reference metadata; it does no timing computation and
receives no netlist. OpenSTA remains the timing authority. The shared-
candidate design is unchanged (both authorities evaluate the identical SDC
bytes per trial).

## 5. Minimal Production-Change Design (implement in a future gate — NOT this gate)

**File:** `eger/evidence/normalizer.py`, function `_map_scope`.

```text
BEFORE:
    def _map_scope(raw_scope: str) -> str:
        return _SCOPE_MAP.get(raw_scope, "UNSUPPORTED")

AFTER:
    _CANONICAL_SCOPES = {"FULL", "PARTIAL", "INSUFFICIENT", "UNSUPPORTED"}
    def _map_scope(raw_scope: str) -> str:
        # Canonical values pass through; raw statuses map per the frozen SCOPE_MAP.
        if raw_scope in _CANONICAL_SCOPES:
            return raw_scope
        return _SCOPE_MAP.get(raw_scope, "UNSUPPORTED")
```

Impact analysis (verified against the existing test suite):

- Raw-vocabulary mappings are unchanged: VALIDATED→FULL,
  PARTIALLY_VALIDATED→PARTIAL, NETLIST_REQUIRED→INSUFFICIENT,
  UNSUPPORTED→UNSUPPORTED (the four scope tests in `test_evidence_pipeline.py`
  all feed raw vocabulary — unaffected).
- `normalize_failure` sets `UNSUPPORTED` directly (not via `_map_scope`) —
  unaffected.
- OpenSTA adapter stores raw `VALIDATED` — unaffected.
- Only canonical input to the normalizer (the Ṛta adapter) changes behavior:
  from UNSUPPORTED to the true canonical scope. No existing test asserts
  the full Ṛta→normalizer chain with canonical scope, so no existing
  assertion is expected to change — the implementation gate must confirm
  this against the full 864-test suite and add the missing regression test
  (Ṛta FULL → normalized FULL → gate decision driven by findings).

**Harness wiring (also future gate):** `harness/providers.py`
`build_rta_oracle_call` must accept a frozen `DesignMetadata` for the
simple_path substrate and pass it as `design_metadata=` on every
`validate()` call (initial and candidate evaluations). The metadata is the
same object as used in §3.3.

## 6. Effects on the RQ-5 Design

| Criterion | Assessment |
| --------- | ---------- |
| Evidence scope | FULL for valid-reference SDCs (was UNSUPPORTED — floor removed) |
| Deterministic behavior | Unchanged — Ṛta and the P055 path are deterministic |
| Evidence-contract compatibility | Uses the FROZEN P055 design_metadata contract; one aligned normalizer |
| PO-2 (evidence compatibility) | Unchanged — both authorities enter the same contract |
| PO-3 (Oracle-detected improvement) | Becomes measurable: initial vs final Ṛta error count |
| Authority independence | Preserved — netlist-less constraint-quality (Ṛta) vs timing (OpenSTA) |
| Shared-candidate design | Preserved — same SDC bytes evaluated by both authorities |
| Task discrimination | T1 (SDC-005/006) and T2 (SDC-008/009) both drive revision |

## 7. Verification Performed

- Pinned Ṛta 1.5.11 @ `3b5c2f2`; read-only `check --json` only.
- Raw CLI probes for Options 1/2 across T1-initial, T2-initial, and a
  complete SDC.
- Adapter-level probes (Option 3) through `EvidenceOracle.validate` with
  `design_metadata`, including a bad-port-reference negative case
  (PARTIAL scope, gate fail-closed).
- End-to-end simulation of the designed normalizer fix (canonical
  pass-through) over the full real-Ṛta chain (see §3.3 table).
- Full regression: `python -m pytest tests -q` → **864 passed** (no
  production change made in this gate; probes wrote only to /tmp).

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
EGER production code modified: NO (design only)
PILOT-002 executed: NO
```

## 9. Decision

```text
GO
```

The Ṛta evaluation-scope blocker is resolved with a concrete, empirically
verified protocol: netlist-less Ṛta + frozen P055 design_metadata + a
minimal, well-bounded normalizer alignment (canonical pass-through). No
unresolved methodological blocker remains.

**Required next gate (implementation, not experiment):**

1. Implement the §5 normalizer alignment + add the missing full-chain
   regression test (Ṛta FULL → gate decision on findings).
2. Wire frozen `DesignMetadata` into `harness/providers.py`'s Ṛta oracle
   call.
3. Confirm the full 864-test regression (no expectation drift) plus a new
   Ṛta discrimination fixture (T1/T2 incomplete REJECT, completed ACCEPT).
4. Re-run the P174 readiness smoke for the Ṛta arm (now expecting genuine
   REJECT→ACCEPT revision behavior).
5. Only then — with separate explicit authorization — may EGER-RQ5-PILOT-002
   be designed to start.

## 10. Git

- Commit: `(P175 commit, see git log)`
- HEAD == origin/main: YES
- `Universal_Principles_Library/` untouched
- No experiment data collected or committed
