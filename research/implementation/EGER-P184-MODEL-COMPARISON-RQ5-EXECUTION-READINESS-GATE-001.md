# EGER — P184: Model-Comparison RQ-5 Execution Readiness Gate

## 1. Objective

Validate the frozen P183 model-comparison setup without collecting the 16 experimental trials. Verify model availability, run qualification, audit the harness, and determine READY / REFINE / BLOCKED.

**Pre-execution readiness gate only.** No experimental data was collected. No comparison model was invoked for experimental trials.

## 2. Frozen Protocol Verification

P183's protocol was verified against the current harness:

| Item | Frozen Value | Status |
| ---- | ------------ | ------ |
| 2 models | mimo-v2.5-free, deepseek-v4-flash | VERIFIED (identifiers frozen) |
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

### Comparison: opencode/deepseek-v4-flash

| Property | Value |
| -------- | ----- |
| Provider | DeepSeek |
| CLI | `opencode run --model opencode/deepseek-v4-flash <prompt>` |
| Expected | Free tier |
| Actual | **REQUIRES PAYMENT METHOD** |
| Error | `"No payment method. Add a payment method here: https://opencode.ai/workspace/.../billing"` |
| Status | **UNAVAILABLE** |

## 4. Model Availability Survey

Every non-mimo model was tested. Results:

| Model | Error | Status |
| ----- | ----- | ------ |
| opencode/mimo-v2.5-free | — | AVAILABLE |
| opencode/deepseek-v4-flash | No payment method | UNAVAILABLE |
| opencode-go/deepseek-v4-flash | Invalid API key | UNAVAILABLE |
| opencode/gpt-5-nano | No payment method | UNAVAILABLE |
| opencode/gemini-3.5-flash-lite | Unauthorized | UNAVAILABLE |
| opencode/gemini-3.5-flash | Unauthorized | UNAVAILABLE |
| opencode/glm-5 | No payment method | UNAVAILABLE |
| opencode/glm-5.3-flash | No payment method | UNAVAILABLE |
| opencode-go/mimo-v2.5 | Invalid API key | UNAVAILABLE |
| opencode-go/mimo-v2.5-pro | Invalid API key | UNAVAILABLE |

**Only `opencode/mimo-v2.5-free` is available in the current environment.** All other models require either a payment method or a valid API key that is not configured.

## 5. Model Qualification

### Baseline (mimo-v2.5-free)

| Metric | Result |
| ------ | ------ |
| Invocations | 6 |
| Valid count | 6/6 |
| Per-task valid | T1: 3/3, T2: 3/3 |
| Empty/provider failures | 0 |
| **Qualification** | **PASSED (6/6)** |

### Comparison (deepseek-v4-flash)

| Metric | Result |
| ------ | ------ |
| Invocations | 6 |
| Valid count | 0/6 |
| Per-task valid | T1: 0/3, T2: 0/3 |
| Empty/provider failures | 6/6 |
| **Qualification** | **FAILED (0/6 — model unavailable)** |

**Per P183: "If either model fails qualification: STOP. Do not begin experimental trials."**

## 6. BLOCKED Decision

```text
P184: BLOCKED

Reason: The frozen comparison model (opencode/deepseek-v4-flash) is not
available in the current environment. It requires a payment method that
is not configured. All alternative non-mimo models also require payment
or API keys. Only the baseline model (opencode/mimo-v2.5-free) is
available.

Per P183: "If the comparison model is unavailable, do not choose a
replacement. Return BLOCKED/REFINE and document the reason."

Per P184: "If the comparison model is unavailable, do not choose a
replacement. Return BLOCKED/REFINE and document the reason."
```

## 7. What Would Unblock

The experiment can proceed when one of:

1. **A payment method is added** to the opencode account, enabling deepseek-v4-flash or another non-mimo model
2. **An API key is configured** for an alternative provider (e.g., DeepSeek, OpenAI, Google)
3. **A different free-tier model** becomes available through the opencode CLI
4. **The comparison model is changed** via a new P182/P183 research-design gate (not permitted in P184)

## 8. Remaining Readiness (Not Blocked by Model Availability)

The following items were verified and PASS, but cannot be exercised until a comparison model is available:

- Harness supports model parameterization (`build_model_call(model=...)`)
- 16-cell matrix can be constructed from frozen protocol
- Fixture dry-run can be executed with deterministic fixtures
- Prompt-equivalence audit can be performed once both models are available
- Experimental-data firewall is structurally in place

## 9. Research Boundary

```text
RQ-4: CLOSED (unchanged)
RQ-5: CLOSED (unchanged)
C0-C5: UNCHANGED
Rta: UNCHANGED
VerificationGate: UNCHANGED
New experiment executed: NO
New model invoked: NO (qualification attempted but blocked)
```

## 10. Tests

- EGER full suite: 878/878 PASS (no code changes)
- Harness suite: 62/62 PASS

## 11. Git

- P184 committed as: `4de3cab` (see CHANGE-056)
- HEAD == origin/main (after push)
- No code changes; research records only
- Universal_Principles_Library/ untouched

## 12. Artifacts

- `research/implementation/EGER-P184-MODEL-COMPARISON-RQ5-EXECUTION-READINESS-GATE-001.md`
- `research/implementation/EGER-CHANGE-056.md`

## STOP

P184 is BLOCKED. The frozen comparison model is not available. No experimental trials were executed. The research-design gate (P183) remains valid; the execution-readiness gate must be re-run when a comparison model becomes available.
