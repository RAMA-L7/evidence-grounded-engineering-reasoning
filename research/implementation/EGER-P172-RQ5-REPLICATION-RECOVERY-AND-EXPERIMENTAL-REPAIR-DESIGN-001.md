# EGER P172 — RQ-5 Replication Recovery & Experimental Repair Design

## 1. Objective

Design the minimum scientifically sufficient repair required for a future controlled RQ-5 replication, given the P171 verdict that the P170 pilot is **INCONCLUSIVE**. This is a RESEARCH-DESIGN / RECOVERY GATE ONLY.

**Nothing was executed in this gate.** No new experiment, no Ṛta/OpenSTA rerun, no P170 trial retry, no raw-data modification, no code implementation.

## 2. Historical Baseline

| Item | Value |
|------|-------|
| P170 checkpoint | `624fbb5a2869099788ebc02dbaecd838c988a3bf` |
| P171 checkpoint | `49bebdf16f3036c1998e6b135db0cd1e6f5ee0e2` |
| Current HEAD | `49bebdf16f3036c1998e6b135db0cd1e6f5ee0e2` |
| origin/main | `49bebdf16f3036c1998e6b135db0cd1e6f5ee0e2` |
| Branch | main |
| Staged files | none |
| Working tree | clean except intentionally untracked `Universal_Principles_Library/`, `raw_trials.json`, `analysis.json` |

`Universal_Principles_Library/` is untouched and unstaged.

## 3. P171 Findings Accepted as Fixed (NOT reopened)

### CRITICAL
1. 0/15 evaluated candidates contained valid SDC syntax — the model returned conversational filler in every invocation.
2. OpenSTA ACCEPT results were therefore not valid evidence of timing satisfaction.
3. The T2 aggressive-clock condition was never actually exercised (candidate replaced the aggressive SDC before OpenSTA ran).

### HIGH
4. PO-3 was never measured — the initial SDC was never Oracle-evaluated.
5. P170 PO-2 report counts (7/7, 4/4, 11/11) did not reconcile with raw evaluation counts (12 Ṛta + 3 OpenSTA = 15).
6. Ṛta findings were mischaracterized in the P170 report (SDC-001 "No create_clock defined" presented as "missing input/output delays").

### MEDIUM
7. Retry was not implemented (0 retries vs. frozen 1 bounded retry).
8. Counterbalancing was not implemented as frozen (Ṛta-first in both task blocks).
9. Required schema fields (`retry_count`, `initial_oracle_result`) were absent.

## 4. RQ-5 Preservation

RQ-5 remains frozen exactly as established by P169:

> **To what extent does the evidence-grounded EGER architecture generalize across independent deterministic evaluation authorities within VLSI engineering tasks?**

Assessment: The same RQ-5 **can** be meaningfully tested after harness repair. The P170 failure was a candidate-generation failure (the LLM never produced valid SDC), not a failure of the construct. The architecture's Oracle boundary, evidence contract, and verification chain were never actually exercised against valid SDC artifacts. **REFINE is not required** — the research question is preserved unchanged.

## 5. Candidate-Validity Repair

### Problem

P170's harness sent whatever the model returned directly to the Oracle. Conversational filler passed through as if it were SDC, producing vacuous Ṛta findings (SDC-001) and vacuous OpenSTA ACCEPTs (no clock → WNS 0.0).

### Repair: Deterministic Candidate-Validity Gate

A mandatory gate BEFORE any Oracle invocation classifies the model output into exactly one of:

```
VALID_SDC          → proceed to Oracle evaluation
NON_SDC_OUTPUT     → candidate rejected (does NOT reach Oracle)
EMPTY_OUTPUT       → candidate rejected
PROVIDER_FAILURE   → candidate rejected (failure path)
```

### Minimum Objective Validity Criterion

A model response is a `VALID_SDC` candidate if and only if ALL of the following hold:

1. **Non-empty after trimming.** Stripping markdown code fences (` ``` ` if present) leaves a non-empty string.
2. **No conversational wrapper.** The response must not match conversational filler patterns (e.g., "Understood.", "I'm ready to help", "What do you need?"), sentences ending in "?" directed at the user, or prose paragraphs. Detection: reject if the text contains no SDC command at all; reject if it contains question marks or greeting phrases and fewer than N SDC commands (N = 1).
3. **Contains at least one valid SDC command** parsed as a Tcl/SDC command line: starts with a known SDC keyword (`create_clock`, `set_input_delay`, `set_output_delay`, `set_clock_uncertainty`, `set_clock_latency`, `set_units`, `set_sdc_version`, etc.) followed by valid arguments.
4. **Task-specific required construct present** (per task — see §12): e.g., for both T1 and T2, `create_clock` MUST be present. This is the direct defense against the vacuous-pass path (no clock → no constrained paths → clean).
5. **No embedded shell/Tcl injection markers** that would break the harness (reuse the existing P166 discipline: the candidate is written into the SDC file; it must not contain heredoc terminators or command-substitution artifacts). Concretely: reject candidates containing `SDCEOF`/`TCLEOF` literal delimiters or `$(` / backtick sequences (defense in depth; the single-quoted heredoc already prevents shell expansion).

Design intent: the gate does NOT attempt to semantically validate the SDC (that is the Oracle's job). It only distinguishes "this is plausibly an SDC document" from "this is not an SDC document." The criterion is deliberately objective and deterministic — no LLM judgment, no manual review.

### Failure Semantics

- `NON_SDC_OUTPUT` and `EMPTY_OUTPUT` are recorded as candidate-validity failures, distinct from `PROVIDER_FAILURE`.
- A candidate-validity failure counts as a failed attempt for retry purposes ONLY if the retry policy (see §10) says so. Default: candidate-validity failure is retryable (it is a generation-quality failure, not an engineering violation).

## 6. Model Qualification

### P170 failure analysis

`opencode/mimo-v2.5-free` returned conversational filler in 15/15 invocations. Two hypotheses are consistent with the records: (a) prompt/harness defect (instruction "Return ONLY the improved SDC text" not enforced; no system prompt), or (b) model incapacity (free model cannot follow the instruction). The records cannot distinguish these — the harness did not validate output, so both are live.

### Repair: Pre-Experiment Model Qualification Test

A mandatory readiness test executed BEFORE trial 1 of any future replication:

- **Purpose:** Establish whether the chosen model reliably produces `VALID_SDC` under the frozen task prompts.
- **Procedure:** Run the frozen task prompt (T1 and T2 contexts) K times (recommend K=3 per task = 6 invocations) WITHOUT any revision loop. Classify each output with the candidate-validity gate (§5).
- **Pass criterion:** ≥ 5/6 outputs classified `VALID_SDC`, including at least one per task, with NO empty/provider failures.
- **Status:** This is a readiness gate, NOT experimental data. Its outputs are recorded in the readiness record, not the experiment dataset. It cannot be retrofitted into the experiment.
- **On failure:** the model is disqualified for that task set; a different model/provider must be selected and re-qualified before the experiment may start. Selection is NOT made because "results look better" — it is made because qualification demonstrates the required capability (produce valid SDC under frozen instructions).

### Model options (evaluated, not decided here)

| Option | Assessment |
|--------|-----------|
| A: Keep mimo-v2.5-free, repair prompt/harness | Acceptable IF qualification passes. Requires system-prompt enforcement and output-format instruction; the harness must validate, not trust. |
| B: Different available model/provider | Acceptable IF qualification passes. Selection criterion is qualification success, not perceived quality. |
| C: Deterministic fixture for harness validation, then real-model replication | REQUIRED as a two-phase strategy regardless of A/B: first validate the harness (validity gate, retry, counterbalancing, schema, analysis) against deterministic fixture candidates (fixed SDC texts, no LLM), then run the real-model replication. |

Recommendation: **Phase 1 — deterministic fixture harness validation; Phase 2 — real-model replication gated on qualification.** This decouples "is the harness correct?" from "does the model behave?" — the two failure modes that were conflated in P170.

## 7. Initial Oracle Evaluation Repair (PO-3)

### Problem

P170 never invoked the Oracle on the initial SDC. PO-3 (frozen definition: initial vs. final Oracle evaluation) was therefore unmeasurable.

### Repair

The future trial sequence is:

```
initial SDC (frozen task artifact)
   ↓
Oracle evaluation (MANDATORY, before any model invocation)
   ↓
initial_oracle_result, initial_evidence_hash  ← recorded
   ↓
LLM revision loop (candidate → validity gate → Oracle → evidence → gate)
   ↓
final SDC
   ↓
final Oracle evaluation
   ↓
final_oracle_result, final_evidence_hash  ← recorded
```

### PO-3 computation (frozen definition preserved)

- **Ṛta:** `IMPROVED` if ERROR-finding count(final) < ERROR-finding count(initial); `NOT_IMPROVED` if equal; `WORSE` if greater. (Preserves P169 §7.)
- **OpenSTA:** `IMPROVED` if WNS(final) > WNS(initial); `NOT_IMPROVED` if equal; `WORSE` if WNS(final) < WNS(initial). (Preserves P169 §7.)
- **Missing data:** FAILED trials (both attempts fail) excluded, per frozen P169 rule.
- **Boundary case:** OpenSTA trials whose initial evaluation is `NO_TIMING_CONSTRAINT` (§13) are recorded as such and their PO-3 is classified `NOT_MEASURABLE` — they cannot enter the IMPROVED/NOT_IMPROVED/WORSE comparison because the initial state is undefined. This is a NEW explicit rule required by the vacuous-pass defense; it does not change the frozen definition, it defines its missing-data boundary.

The frozen PO-3 definition is possible and valid once the initial evaluation is recorded — **no change to the definition is required**.

## 8. Retry Repair

### Problem

P169 froze "maximum 1 bounded retry per trial." P170 executed 0.

### Repair (conceptual design, not implemented here)

| Question | Rule |
|----------|------|
| What triggers a retry? | `PROVIDER_FAILURE`, `EMPTY_OUTPUT`, `NON_SDC_OUTPUT`, Oracle timeout, infrastructure failure — i.e., generation/harness failures, NOT engineering outcomes |
| What does NOT trigger retry? | A valid SDC candidate that the Oracle evaluates and the gate REJECTs (that is an engineering result, not a failure); Oracle non-zero exit on a valid candidate (recorded as ORACLE_FAILURE, trial-level decision, not auto-retried) |
| Provider vs. malformed output | Both are retryable generation failures, but recorded with distinct `failure_kind` (`PROVIDER_FAILURE` vs `CANDIDATE_INVALID`) |
| Both attempts recorded | Yes — `attempt` field (1 or 2) on every record; attempt 2 shares `trial_id` with suffix `-A2` |
| Denominator effect | Each trial contributes at most 1 row to trial-level analysis; `oracle_call_count` counts ALL calls including retries (mirrors P169 "retries count against the call budget") |
| Both attempts fail | Trial = `FAILED` with `failure_kind` of the second attempt; counted as a failed trial, never deleted |

Required per-attempt fields: `attempt`, `retry_count`, `failure_kind`, `provider_status`.

## 9. Counterbalancing Repair

### Problem

P169 §9 froze "Trials 1-4: Ṛta first; Trials 5-8: OpenSTA first." P170 ran Ṛta-first in both task blocks.

### Repair: Exact Future Trial Matrix (frozen before trial 1)

| Order | Trial | Task | Oracle | Replication | Oracle-first |
|-------|-------|------|--------|-------------|--------------|
| 1 | T1-Rta-R1 | T1 | Ṛta | 1 | Ṛta |
| 2 | T1-OpenSTA-R1 | T1 | OpenSTA | 1 | — |
| 3 | T1-Rta-R2 | T1 | Ṛta | 2 | Ṛta |
| 4 | T1-OpenSTA-R2 | T1 | OpenSTA | 2 | — |
| 5 | T2-OpenSTA-R1 | T2 | OpenSTA | 1 | OpenSTA |
| 6 | T2-Rta-R1 | T2 | Ṛta | 1 | — |
| 7 | T2-OpenSTA-R2 | T2 | OpenSTA | 2 | OpenSTA |
| 8 | T2-Rta-R2 | T2 | Ṛta | 2 | — |

- Each Oracle runs first in exactly one task block (Ṛta first in T1, OpenSTA first in T2).
- Task allocation is unchanged from P169 (T1 and T2 both run both Oracles) — balance is achieved by ordering, not by changing the matrix.
- The execution script MUST generate and assert this exact order (or a pre-generated shuffled order with both-first representation) before trial 1, and record `execution_order` per trial. No post-hoc randomization.
- Rationale for fixed matrix over random: 8 trials is small; a fixed counterbalanced matrix guarantees both-first representation deterministically. Randomization could, by chance, produce an unbalanced order at this N.

## 10. Task Validity

Both Oracles evaluate the **same candidate SDC** for a trial. No Oracle-specific candidates. No silent harness repair of candidates.

| Task | Initial SDC | Required construct (validity gate) | Expected Ṛta relevance | Expected OpenSTA relevance | Expected PASS/VIOLATION behavior |
|------|-------------|------------------------------------|------------------------|----------------------------|----------------------------------|
| T1 | `create_clock -name clk -period 10.0 [get_ports clk]` | `create_clock` present | Incomplete: no `set_input_delay`/`set_output_delay` → ERROR/WARNING findings | With 10.0 ns clock and no I/O delays, internal path is met → likely clean (WNS ≥ 0) | T1-OpenSTA expected ACCEPT from initial (clean timing); T1-Ṛta expected REJECT (incomplete) — this asymmetry is BY DESIGN (authority-specific evidence), documented as a floor effect for OpenSTA on T1 |
| T2 | `create_clock -name clk -period 0.05 [get_ports clk]` | `create_clock` present | Aggressive period is syntactically valid → incomplete-constraint findings | 0.05 ns period → setup VIOLATION (P163: slack −0.10 ns) | T2-OpenSTA expected REJECT (violation) unless candidate relaxes the period; T2-Ṛta expected REJECT (incomplete) |

**Critical requirement restated:** the harness must pass the SAME candidate bytes to whichever Oracle the trial assigns. Candidate validity is evaluated once, before Oracle dispatch. The T2 aggressive-clock condition is only exercised if the candidate retains `create_clock -period ≤ 0.05` or otherwise produces a violation — which is exactly what the validity gate (requiring `create_clock`) now guarantees will reach OpenSTA.

**Documented floor effect:** T1-OpenSTA may show zero revision (initial already clean). This is not a harness failure — it is an authority-specific observation consistent with the shared-task design. It will be reported as such (NOT_IMPROVED with clean initial), never reframed as an OpenSTA success story.

## 11. OpenSTA Vacuous-Pass Defense

### Problem

```
no clock in SDC
   → no constrained paths
   → WNS 0.0
   → timing_clean
   → ACCEPT
```

was interpreted (in P170) as "candidate satisfied timing." It means nothing was constrained.

### Repair decision

The correct defense is a **layered combination**, with NO change to VerificationGate:

1. **Task-level validity requirement (primary):** the candidate-validity gate (§5) requires `create_clock` for T1/T2, so a no-clock candidate is rejected BEFORE it reaches OpenSTA. This structurally prevents the vacuous-pass path in the experiment.
2. **Experiment-level exclusion/qualification rule (secondary):** if, despite the gate, an OpenSTA evaluation is produced with no clock (e.g., `report_wns` yields 0.0 with no `report_checks` path output), the analysis layer classifies the evaluation as `NO_TIMING_CONSTRAINT` — recorded, excluded from PASS/VIOLATION classification, and flagged in the report. This is an experiment-level rule, not an adapter change and not a gate change.
3. **Explicit classification distinction:** every OpenSTA finding is labeled either `TIMING_CONSTRAINT_PRESENT_AND_CLEAN` (clock defined, paths constrained, WNS ≥ 0) or `NO_TIMING_CONSTRAINT` (no clock / no constrained paths). P170 historical results are NOT reclassified — the distinction applies to future runs only.

The adapter and VerificationGate are NOT modified. The rule lives at the experiment/harness layer.

## 12. PO-2 Accounting Repair

### Problem

P170 report aggregated Oracle evaluations by manual counting that did not match raw records.

### Repair: Single Authoritative Denominator + Deterministic Aggregation

The future report derives ALL aggregate numbers from raw trial records through a deterministic analysis script:

```
raw records (per-attempt, per-iteration JSON)
   ↓
deterministic aggregation script (single source of truth)
   ↓
analysis.json
   ↓
report (tables generated from analysis.json, no manually typed totals)
```

Explicit denominator definitions:

| Term | Definition |
|------|-----------|
| planned trials | 8 (2 tasks × 2 Oracles × 2 replications) |
| completed trials | trials with `completion_status = COMPLETED` (final artifact + verification) |
| Oracle evaluations | every Oracle invocation (initial + per-iteration + final), including retries |
| successful Oracle evaluations | evaluations with `is_success = True` |
| provider failures | attempts with `failure_kind = PROVIDER_FAILURE` |
| retry attempts | attempts with `attempt = 2` |
| EvidenceArtifacts | evaluations that produced a normalized EvidenceArtifact |

Every PO-2 figure states its denominator explicitly (e.g., "12/12 successful evaluations produced compatible evidence"), so the P170-style ambiguity (11/11 vs 15) cannot recur.

## 13. Corrected Data Schema

Per-trial record (fields retained + rationale):

```
experiment_id          — pilot identity (EGER-RQ5-PILOT-002 or next frozen ID)
trial_id               — T{task}-{Oracle}-R{rep}
task_id                — T1 | T2
replication_id         — 1 | 2
oracle                 — Rta | OpenSTA
execution_order        — required by counterbalancing repair (recorded before run)
attempt                — 1 | 2 (retry repair)
retry_count            — 0 | 1 (was absent in P170)
model_provider         — frozen identity
model_name             — frozen identity
model_config_hash      — hash of full model config + prompt template

initial_sdc            — task artifact (text)
initial_sdc_hash       — sha256
initial_oracle_result  — new (PO-3 repair)
initial_evidence_hash  — new (PO-3 repair)

candidate_sdc          — model output (raw, before validity gate)
candidate_sdc_hash     — sha256 of raw output
candidate_validity     — VALID_SDC | NON_SDC_OUTPUT | EMPTY_OUTPUT (validity gate)
iteration              — 1..max_iterations
oracle_result          — per-iteration result (raw + parsed summary)
evidence               — normalized EvidenceArtifact summary
evidence_hash          — sha256

verification_decision  — ACCEPT | REJECT | NO_EVIDENCE
final_sdc              — text
final_sdc_hash         — sha256
final_oracle_result    — new (PO-3 repair)

completion_status      — COMPLETED | FAILED
failure_kind           — PROVIDER_FAILURE | CANDIDATE_INVALID | ORACLE_FAILURE |
                          TIMEOUT | INFRASTRUCTURE_FAILURE | none
runtime                — seconds per attempt
timestamp              — ISO 8601
```

Rationale notes: `config_hash` is decomposed into `model_config_hash` (explicit) to remove ambiguity. `attempt`/`retry_count` are mandatory per-attempt fields (retry repair). `candidate_sdc` retains the RAW model output — never overwritten by a "cleaned" version — so the validity gate's input is auditable. `initial_oracle_result` and `final_oracle_result` are mandatory for PO-3. No field is retained without a purpose.

## 14. Provenance Requirements

Every future trial must permit reconstruction of:

```
Task (frozen artifact, hashed)
  → initial artifact (SDC text + hash)
  → initial Oracle evaluation (result + evidence hash)
  → prompt (template identity + config hash; prompt text may be large — store hash + template ID)
  → candidate (raw model output + hash + validity classification)
  → Oracle evaluation (input hash, output bytes, exit code, evidence hash)
  → evidence (normalized artifact summary + hash)
  → revision (which candidate was fed back)
  → verification (gate decision)
  → final artifact (text + hash)
```

Hashes are computed over exact bytes (no normalization before hashing). Local experimental artifacts remain publication-sensitive and untracked; no persistent production storage is introduced. The committed artifacts are: the frozen task definitions, the execution script, the analysis script, and the report. Raw per-trial JSON stays local (as with P170/P171).

## 15. Reproducibility Requirements

Frozen before trial 1 (each item is a hard prerequisite):

- model (identity + parameters, temperature 0.0 or documented equivalent)
- provider
- prompt template (full text recorded/hashed)
- task definitions (T1/T2 artifacts with required constructs)
- initial SDCs (exact text)
- Oracle versions (Ṛta revision, OpenSTA version + WSL env)
- OpenSTA environment (WSL distro, binary path via wslpath, Tcl version)
- Ṛta version + CLI path
- trial matrix (exact order from §9)
- Oracle order policy
- retry policy (§8)
- iteration limit (3) and call limit (3 per attempt; retries count)
- candidate-validity gate version
- analysis script version (deterministic aggregation)

If any prerequisite is missing or unfrozen at execution time, the replication reports **BLOCKED** — no improvised substitution.

## 16. Pre-Experiment Readiness Gate

Mandatory checklist before trial 1 (each item must PASS or the gate is **NO-GO**):

| Area | Check |
|------|-------|
| Candidate generation | Model qualification passed (≥5/6 VALID_SDC, both tasks, §6) |
| Candidate validity gate | Correctly classifies VALID/NON_SDC/EMPTY/PROVIDER_FAILURE on fixture inputs |
| Ṛta | Version verified; read-only; deterministic on fixture SDCs |
| OpenSTA | Version verified; substrate verified; PASS/VIOLATION discrimination re-confirmed (as P163/P167) |
| Timing | Valid clock present + constrained path present for OpenSTA evaluations (no vacuous pass) |
| Initial Oracle evaluation | `initial_oracle_result` recorded correctly on fixture |
| Retry | Retry triggers, records both attempts, respects call budget (fixture test) |
| Counterbalancing | Script asserts the §9 order before trial 1 (fixture test) |
| Schema | All required fields populated on a fixture trial |
| Analysis | `raw → deterministic aggregation → analysis.json` reproduces fixture numbers |
| Git | Working tree clean except approved local experiment artifacts |

Any critical failure → **NO-GO**; the experiment does not begin; the issue is documented as a new readiness finding.

## 17. Replication-Size Assessment

The frozen N = 8 (2 tasks × 2 Oracles × 2 replications) **remains sufficient** for the intended descriptive pilot after harness repair, for these reasons:

1. The P170 inconclusiveness was NOT caused by insufficient N — it was caused by candidate-generation failure. N=8 with valid candidates is a different measurement than N=8 with garbage; the failure was qualitative, not quantitative.
2. The unit of analysis (per-trial pipeline behavior) with 2 replications per cell provides within-cell consistency checks (as intended by P169).
3. Replication pairs give the replication audit its power (T1-OpenSTA R1/R2 both valid now).
4. No inferential statistics are introduced; the pilot remains descriptive (P169 §5, P168 §13).

If a later gate decides to support stronger inference, that is a separate research-design decision requiring its own gate — not a P172 decision.

## 18. Threats to Validity (revised for the repaired design)

| Threat | Risk | Mitigation (repaired) | Residual |
|--------|------|-----------------------|----------|
| Candidate-generation failure | HIGH (materialized in P170) | Validity gate + model qualification + deterministic fixture phase | Model may still fail qualification → NO-GO |
| Oracle property mismatch | HIGH | Shared-task design, same candidate per trial, authority-specific evidence | Property mismatch remains by design |
| Synthetic substrate | HIGH | Explicit bound: 3-cell substrate, technical validation only | No generalization to real VLSI |
| T1-OpenSTA floor effect | MEDIUM | Documented (§10): initial likely clean → NOT_IMPROVED is a valid observation, not reframed | T1 provides weak OpenSTA revision signal |
| Model stochasticity | MEDIUM | temperature 0.0, config hash, 2 replications | Cannot eliminate sampling variance |
| Order effects | MEDIUM (materialized in P170) | Fixed counterbalanced matrix asserted pre-run | Partially controlled |
| Provider failures | MEDIUM | 1 bounded retry, both attempts recorded | May reduce usable trials |
| PO-3 measurability | HIGH (materialized in P170) | Mandatory initial evaluation; NO_TIMING_CONSTRAINT boundary defined | Boundary case explicitly excluded from PO-3 comparison |
| PO-2 accounting | MEDIUM (materialized in P170) | Deterministic aggregation script, single denominator | Requires script fidelity (fixture-tested) |
| Vacuous pass | HIGH (materialized in P170) | create_clock requirement + NO_TIMING_CONSTRAINT classification | Requires gate + analysis both enforced |
| Retry policy interactions | LOW | Retry counted against call budget; both attempts recorded | Fixture-tested |

## 19. GO/REFINE/ABANDON Decision

**Decision: GO** — with the understanding that this GO authorizes DESIGN COMPLETENESS, not execution.

Basis:
- The construct (architecture operates with two independent deterministic authorities on valid SDC artifacts) remains validly measurable.
- Every P171 materialized failure maps to a concrete, bounded, harness/protocol repair (§5–§16). None requires EGER architecture change, VerificationGate change, Ṛta change, or RQ-5 rewording.
- The one empirical unknown (can the chosen model produce valid SDC under frozen instructions?) is handled by a mandatory pre-experiment qualification gate with an explicit NO-GO path — it is a readiness check, not an unresolved methodological question.
- No methodological blocker remains open at the design level.

Conditions attached to this GO (must hold before any future trial):
1. Model qualification passes (§6).
2. Pre-experiment readiness gate is all-PASS (§16).
3. The repaired harness is validated first against deterministic fixtures (§6 Option C phase 1).
4. The frozen task matrix, retry policy, and counterbalancing order are asserted by the execution script before trial 1.

If conditions 1–3 fail, the next step is **BLOCKED/NO-GO**, not an improvised run.

## 20. Future Replication Boundary

- P170 and P171 records remain historical and unchanged. P171 verdict **RQ-5 PILOT INCONCLUSIVE** stands.
- A future replication is a NEW controlled experiment (e.g., EGER-RQ5-PILOT-002), not a P170 retry or continuation.
- It cannot erase P170/P171 history and cannot inherit P170's outcomes.
- **RQ-5 established** may be claimed only if a future experiment independently earns that conclusion through the repaired harness and a separate research-review gate.
- No Ṛta modification. No RQ-4 reopening. No C0–C5 changes. No VerificationGate authority change.

## 21. Git / Test Status

- HEAD == origin/main == `49bebdf` at gate start.
- `python -m pytest tests -q` → **864 passed** (verified; production code untouched).
- `Universal_Principles_Library/` untouched, unstaged.
- `raw_trials.json` / `analysis.json` remain local-only, unmodified.
- This gate adds only: `EGER-P172-RQ5-REPLICATION-RECOVERY-AND-EXPERIMENTAL-REPAIR-DESIGN-001.md` and `EGER-CHANGE-043.md`.

## Research Boundary

```
Ṛta modified: NO
RQ-4 reopened: NO
RQ-5 executed: NO (design only)
C0-C5 conclusions changed: NO
Oracle comparison performed: NO
VerificationGate authority changed: NO
Epistemic-state logic added: NO
Authorization logic added: NO
Experimental data modified: NO
New experiment executed: NO
```

## Next Gate (not started here)

The next gate is an explicit **implementation/readiness gate** (harness repair + fixture validation + model qualification), followed — only if that gate passes — by a separately authorized controlled replication. Neither is started in P172.

**STOP. No P173 started. No new RQ-5 trial. No P170/P171 record altered.**