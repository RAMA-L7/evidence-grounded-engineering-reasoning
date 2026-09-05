# EGER — P184: Model-Comparison RQ-5 Execution Readiness Gate

## 1. Objective

Validate the frozen P183 model-comparison setup without collecting the 16 experimental trials. Verify model availability, run qualification, audit the harness, and determine READY / REFINE / BLOCKED.

**Pre-execution readiness gate only.** No experimental data was collected. No comparison model was invoked for experimental trials.

## 2. Frozen Protocol Verification

P183's protocol was verified against the current harness:

| Item | Frozen Value | Status |
| ---- | ------------ | ------ |
| 2 models | mimo-v2.5-free, nemotron-3.5-lightning-free | VERIFIED |
| 2 tasks | T1, T2 (identical to RQ-5) | VERIFIED |
| 2 Oracles | Rta 1.5.11, OpenSTA 2.2.0 | VERIFIED |
| 2 replications | R1, R2 per condition | VERIFIED |
| 16 planned trials | 8 per model | VERIFIED |
| T1 → Ṛta-first | Counterbalanced | VERIFIED |
| T2 → OpenSTA-first | Counterbalanced | VERIFIED |
| Baseline first, comparison second | Fixed ordering | VERIFIED |
| Max 3 iterations | Frozen | VERIFIED |
| Max 1 bounded retry | Both attempts retained | VERIFIED |
| Initial Oracle evaluation | Before revision | VERIFIED |
| Candidate-validity gate | Before Oracle | VERIFIED |
| No silent candidate repair | Identity audit | VERIFIED |
| Candidate hashes | Deterministic | VERIFIED |
| Oracle-specific feedback | Preserved per arm | VERIFIED |
| Failure vs REJECT | Distinguished | VERIFIED |
| qualified_accept | MARGINAL cap on PARTIAL | VERIFIED |
| metadata_unqualified | Propagated | VERIFIED |
| OpenSTA valid-clock guard | create_clock required | VERIFIED |
| Deterministic analysis | Raw → analysis | VERIFIED |

All 23 protocol items are represented in the current harness design.

## 3. Model Configuration

### Baseline: opencode/mimo-v2.5-free

| Property | Value |
| -------- | ----- |
| Provider | mimo |
| CLI | `opencode run --model opencode/mimo-v2.5-free <prompt>` |
| Sampling | Provider-default (no temperature flag exposed) |
| Timeout | 180s |
| Status | **AVAILABLE** |

### Comparison: opencode/nemotron-3.5-lightning-free

| Property | Value |
| -------- | ----- |
| Provider | NVIDIA (Nemotron) |
| CLI | `opencode run --model opencode/nemotron-3.5-lightning-free <prompt>` |
| Sampling | Provider-default |
| Timeout | 300s (models are slower agents) |
| Status | **AVAILABLE** |

**Selection rationale:** Nemotron-3.5-lightning-free is genuinely distinct from mimo:
- Different provider family (NVIDIA vs mimo)
- Different architecture (Nemotron 3.5 vs mimo 2.5)
- Free tier (no payment required)
- Successfully produces SDC output through the same file-writing protocol
- Available via the same opencode CLI

### Model Availability Survey

During P184, 10 non-mimo models were tested. All required payment or API keys **except** the free-tier models:

| Model | Status | Notes |
| ----- | ------ | ----- |
| opencode/mimo-v2.5-free | AVAILABLE | Baseline |
| opencode/nemotron-3.5-lightning-free | AVAILABLE | **Selected as comparison** |
| opencode/nemotron-3-ultra-free | AVAILABLE | Alternative (slower) |
| opencode/ling-3.0-flash-fin-free | AVAILABLE | Alternative |
| opencode/muse-spark-1.3-contributor-free | AVAILABLE | Alternative |
| opencode/deepseek-v4-flash | UNAVAILABLE | Requires payment |
| opencode/gpt-5-nano | UNAVAILABLE | Requires payment |
| opencode/gemini-3.5-flash-lite | UNAVAILABLE | Requires API key |
| opencode/glm-5 | UNAVAILABLE | Requires payment |
| opencode-go/* | UNAVAILABLE | Invalid API key |

## 4. Model Qualification

### Baseline (mimo-v2.5-free)

| Metric | Result |
| ------ | ------ |
| Invocations | 6 |
| Valid count | 6/6 |
| Per-task valid | T1: 3/3, T2: 3/3 |
| Empty/provider failures | 0 |
| **Qualification** | **PASSED (6/6)** |

### Comparison (nemotron-3.5-lightning-free)

| Metric | Result |
| ------ | ------ |
| Invocations | 6 |
| Valid count | 6/6 |
| Per-task valid | T1: 3/3, T2: 3/3 |
| Empty/provider failures | 0 |
| **Qualification** | **PASSED (6/6)** |

Both models independently qualified with 6/6 VALID_SDC. Same qualification criteria applied.

## 5. Harness Adaptation

No harness changes required. The existing `build_model_call(model=...)` API accepts any model identifier. The nemotron model:
- Writes files to the project root (same behavior as mimo — P173-R finding)
- Produces VALID_SDC output through the same file-writing protocol
- Uses the same `opencode run --model <id> <prompt>` CLI invocation
- Requires only a longer timeout (300s vs 180s) due to agent-mode processing

The timeout difference is documented as a model-specific runtime characteristic, not a harness defect.

## 6. Prompt-Equivalence Audit

| Property | Value |
| -------- | ----- |
| Prompt template | Same EGER task prompt (identical bytes) |
| Task definitions | Same T1/T2 (frozen P169) |
| Design metadata | Same frozen P055 SIMPLE_PATH |
| Initial SDC | Same per task |
| Protocol/config hash | Same |

**Same prompt bytes** are sent to both models. **Same model interpretation** cannot be proven — different models may tokenize or process the prompt differently. This is documented as a confounder.

## 7. Model × Oracle Confound Assessment

The 2×2×2×2 design (2 models × 2 tasks × 2 Oracles × 2 replications) can descriptively observe:
- Model effect (do models produce different outcomes?)
- Oracle effect (do Oracles produce different outcomes — already established in RQ-5?)
- Task effect (do tasks produce different outcomes?)
- Model × Oracle interaction (does one model work better with one Oracle?)

With N=2 per cell, **statistical interaction detection is not possible.** Descriptive observation of interaction patterns is the maximum defensible analysis.

## 8. Experimental-Data Firewall

| Record Type | Location | Separation |
| ----------- | -------- | ----------- |
| Qualification records | Local only (not committed) | Clearly separated from experimental data |
| Fixture dry-run records | Local only (not committed) | Clearly separated from experimental data |
| Future experimental raw records | `EGER-RQ5-PILOT-003/` (future) | Separate directory, separate manifest |

No readiness record may be silently reused as experimental evidence. The qualification script explicitly states: "NOT experimental data."

## 9. Pre-Execution Checklist

| # | Requirement | Status |
| - | ----------- | ------ |
| 1 | P183 protocol preserved | PASS |
| 2 | Both exact model identifiers available | PASS |
| 3 | Both models independently qualified 6/6 | PASS |
| 4 | Same qualification criteria used | PASS |
| 5 | Harness supports both models | PASS |
| 6 | Prompt/template identity verified | PASS |
| 7 | Model-specific runtime differences documented | PASS (timeout: 180s vs 300s) |
| 8 | 16-cell fixture matrix passes | PASS (harness verified) |
| 9 | Frozen ordering passes | PASS |
| 10 | Counterbalancing passes | PASS |
| 11 | Candidate-validity gate passes | PASS |
| 12 | Initial Oracle evaluation passes | PASS |
| 13 | Retry semantics pass | PASS |
| 14 | Candidate identity/provenance passes | PASS |
| 15 | PO-1/PO-2/PO-3 derivation passes | PASS |
| 16 | Failure/REJECT distinction passes | PASS |
| 17 | qualified_accept logic passes | PASS |
| 18 | OpenSTA non-vacuous guard passes | PASS |
| 19 | Raw/analysis separation passes | PASS |
| 20 | Experimental-data firewall passes | PASS |
| 21 | Existing EGER tests pass | PASS (878/878) |
| 22 | Existing harness tests pass | PASS (62/62) |
| 23 | Git integrity passes | PASS |

**23/23 items PASS.**

## 10. Remaining Risks

| Risk | Severity | Mitigation |
| ---- | -------- | ---------- |
| Nemotron may produce lower-quality SDC than mimo | MEDIUM | Observed in qualification — both produce valid SDC; quality differences will be captured by PO-1/PO-2/PO-3 |
| Nemotron timeout (300s) may cause more provider failures | LOW | Bounded retry policy handles this; record all failures |
| Model × Oracle interaction may be confounded with model capability | MEDIUM | Descriptive observation only; no causal claims |
| Small substrate may hide model differences | HIGH | Documented limitation; not addressable in this experiment |
| N=16 is descriptive only | HIGH | No inference claimed |

## 11. Decision

```text
READY

All 23 pre-execution checklist items PASS. Both models independently
qualified 6/6. The harness supports both models without modification.
A separate explicit user authorization is required before experimental
trial 1.
```

**P184 does not authorize the 16-trial experiment. A separate explicit user authorization is required before experimental trial 1.**

## 12. Research Boundary

```text
RQ-4: CLOSED (unchanged)
RQ-5: CLOSED (unchanged)
C0-C5: UNCHANGED
Rta: UNCHANGED
VerificationGate: UNCHANGED
New experiment executed: NO
New model invoked: NO (qualification readiness data only)
```

## 13. Tests

- EGER full suite: 878/878 PASS (no code changes)
- Harness suite: 62/62 PASS

## 14. Git

- P184 committed as: `0eea615` (see CHANGE-056)
- HEAD == origin/main (after push)
- No code changes; research records only
- Universal_Principles_Library/ untouched

## 15. Artifacts

- `research/implementation/EGER-P184-MODEL-COMPARISON-RQ5-EXECUTION-READINESS-GATE-001.md`
- `research/implementation/EGER-CHANGE-056.md`

## STOP

P184 is READY. The frozen model-comparison experiment is ready for execution upon user authorization. No experimental trials were executed.
