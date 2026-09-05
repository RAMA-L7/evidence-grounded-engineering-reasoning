# EGER-P174 — RQ-5 Final Experiment Readiness Gate

- **Gate**: P174 — RQ-5 Final Experiment Readiness
- **Predecessor**: P173 (harness repair + readiness; BLOCKED on model) → P173-R (model qualification resolution; model QUALIFIED 6/6)
- **Date**: 2026-09-05
- **Baseline**: `6df39ea28343c9ac5b4320a0f1531c7f98cd2ce1` (P173-R checkpoint)
- **Decision**: **READY** (PILOT-002 still requires separate explicit authorization)

---

## 1. Objective

Verify only the remaining P172 §16 prerequisites before any future
EGER-RQ5-PILOT-002 run. No experiment, no new trials, no Oracle comparisons,
no modifications to Ṛta, VerificationGate, C0–C5, or historical records.

## 2. Actual Baseline

| Item            | Value                                                        |
| --------------- | ------------------------------------------------------------ |
| Branch          | `main`                                                       |
| HEAD            | `6df39ea28343c9ac5b4320a0f1531c7f98cd2ce1` (P173-R)          |
| origin/main     | in sync (HEAD == origin/main)                                |
| Working tree    | clean except intentionally untracked artifacts (UPL, raw/analysis/qualification records) |
| `Universal_Principles_Library/` | untouched, unstaged                                    |

## 3. Runtime Environment

| Item             | Verified value                                              |
| ---------------- | ----------------------------------------------------------- |
| Windows host     | Windows (Git Bash); OpenSTA reachable only via WSL          |
| WSL distribution | Ubuntu-24.04 (`wsl -d Ubuntu-24.04`; default user root)     |
| WSL version      | WSL2 (per P163–P167 records)                                |
| OpenSTA version  | **2.2.0** — `$HOME/opensta_build/OpenSTA/app/sta` (`/root/...`) |
| OpenSTA binary   | `/root/opensta_build/OpenSTA/app/sta` (canonical per P167)  |
| Ṛta version      | **1.5.11** (JSON `version` field from `check --json`)        |
| Ṛta revision     | `3b5c2f2` — adapter pin (EGER-ORACLE-CONTRACT-001) == nested-repo HEAD |
| Substrate        | `research/implementation/opensta_pilot/` (P163)             |
| Invocation       | Rta: `python cli.py check <sdc> --json` (cwd outside Ṛta, `PYTHONDONTWRITEBYTECODE=1`); OpenSTA: staged run.tcl in WSL, full binary path, `-no_init -no_splash` |

## 4. Ṛta Read-Only Verification (P172 §16)

- Pinned revision `3b5c2f2` confirmed at the nested repo HEAD.
- `cli.py check --json` executed successfully from cwd **outside** Ṛta on the
  P163 `pass_case.sdc`: version 1.5.11, no errors, 3 SDC commands found,
  1 clock, `analysis_scope.status = NETLIST_REQUIRED` (pre-existing
  netlist-less constraint check contract — unchanged).
- The nested Ṛta working tree shows modified `engineer_test_kit/` artifacts
  dated **2026-08-16** — pre-existing, predating this series (P164–P174);
  not caused by this gate. The outer EGER repo ignores the nested repo.
- No generation capability invoked; check-only discipline preserved.

## 5. OpenSTA + Substrate Discrimination (P172 §16)

Staged the P163 substrate into WSL `/tmp` and ran both SDC cases with the
canonical binary (adapter-equivalent run.tcl with fixed filenames):

| Case      | Exit | WNS    | TNS    | Slack  | Path                              |
| --------- | ---- | ------ | ------ | ------ | --------------------------------- |
| PASS      | 0    | 0.00   | 0.00   | 9.85 MET  | `u_ff` → `data_out` (clk)     |
| VIOLATION | 0    | −0.10  | −0.10  | −0.10 VIOLATED | `u_ff` → `data_out` (clk) |

Discrimination confirmed: PASS and VIOLATION differ by the clock period
(10.0 ns vs 0.05 ns) and produce the expected MET/VIOLATED slacks.

## 6. Timing Precondition (P172 §16)

Verified on both substrate cases:

- Valid clock present: `create_clock -name clk ...` accepted; STA reports
  paths "clocked by clk".
- Constrained timing path present: startpoint `u_ff` → endpoint `data_out`
  with reported slack in both cases.

Consequence for the OpenSTA vacuous-pass defense (P172 §13): a candidate
**with** `create_clock` yields a measured WNS on this substrate; the
NO_TIMING_CONSTRAINT guard only triggers when a candidate omits the clock,
which the candidate-validity gate already rejects before Oracle invocation.

## 7. Real-Provider Harness Smoke Test (P172 §16 — NEW this gate)

Executed `run_smoke_readiness.py` (new readiness driver, fixture-validated
wiring reused from P173-R qualification). One bounded smoke per Oracle path
on T1, exercising the full chain:

```
initial Oracle eval (PO-3)
  → real model call (opencode/mimo-v2.5-free, file-writing protocol)
  → candidate-validity gate
  → Oracle (Rta | OpenSTA)
  → EvidenceNormalizer
  → VerificationGate
```

| Step | Ṛta (T1)                                    | OpenSTA (T1)                            |
| ---- | ------------------------------------------- | --------------------------------------- |
| Initial eval | SUCCESS, evidence hash recorded     | SUCCESS, **WNS 0.0 measured**, VALIDATED |
| Model output | VALID_SDC (`create_clock` present)  | VALID_SDC (`create_clock` present)      |
| Candidate eval | SUCCESS, 23 findings, scope INSUFFICIENT (NETLIST_REQUIRED) | SUCCESS, **WNS 0.0 measured**, VALIDATED |
| Evidence | normalized (hash recorded)          | normalized (hash recorded)              |
| Gate    | **REJECT** (fail-closed: evidence scope not sufficient) | **ACCEPT** (zero ERROR findings) |
| Status  | CHAIN_COMPLETE                      | CHAIN_COMPLETE                          |

Both chains completed end-to-end with real providers. No crash, no
fabrication, no vacuous OpenSTA result (WNS measured with clock defined in
both OpenSTA evaluations), VerificationGate remained the sole decision
authority.

### Known limitation surfaced (retained, not fixed here)

The Ṛta arm evaluates netlist-less at `INSUFFICIENT` evidence scope and the
VerificationGate **fail-closes REJECT** on every evaluation. This is the
pre-existing Ṛta adapter contract (recorded in P171: "Ṛta at UNSUPPORTED
scope — pre-existing contract"); P170 and P171 already documented the Ṛta
arm as showing REJECT under this contract. The harness behaves exactly as
the contract dictates. A future PILOT-002's Ṛta condition will exhibit a
reject floor **unless the future experiment gate explicitly resolves the
Ṛta evaluation scope question** (e.g., netlist-augmented check) — that is a
protocol-design decision for the future authorized experiment, out of scope
for this readiness gate, and does not block harness readiness.

## 8. Fixture-Validated Items (P172 §5–§15) — Confirmed

`python -m pytest research/experiments/EGER-RQ5-PILOT-001/harness_tests -q`
→ **44 passed**:

- Candidate-validity gate: VALID_SDC / NON_SDC_OUTPUT / EMPTY_OUTPUT /
  PROVIDER_FAILURE, code-fence extraction, `create_clock` requirement,
  injection rejection.
- Frozen counterbalanced matrix + `assert_matrix_order` pre-run assertion.
- Initial Oracle evaluation (PO-3) recording + `initial_evidence_hash`.
- Bounded retry (1) with both attempts recorded; retryable vs non-retryable
  failure classification.
- NO_TIMING_CONSTRAINT classification at the experiment layer.
- Deterministic PO-2 aggregation (raw records → analysis; no manual totals).

## 9. Regression

`python -m pytest tests -q` → **864 passed** (production code untouched;
no EGER source modified in this gate).

## 10. Code Changes in This Gate

| File | Change |
| ---- | ------ |
| `research/experiments/EGER-RQ5-PILOT-001/run_smoke_readiness.py` | NEW readiness smoke-test driver (real providers; records kept local) |

No EGER production code, no Ṛta, no VerificationGate, no evidence contract
changes. `smoke_readiness_record.json` is kept local (readiness
observation, not experimental data), consistent with raw-data policy.

## 11. P172 §16 Pre-Experiment Readiness Checklist — Result

| Item | Result |
| ---- | ------ |
| Model returns valid SDC (qualification) | PASS — 6/6 (P173-R) |
| Ṛta version verified, read-only | PASS — 1.5.11 @ 3b5c2f2, check-only |
| OpenSTA version verified | PASS — 2.2.0 |
| Substrate PASS/VIOLATION discrimination | PASS — WNS 0.00 vs −0.10 |
| Valid clock present | PASS |
| Constrained path present | PASS |
| Initial Oracle evaluation works | PASS (fixture + real smoke) |
| Retry works | PASS (fixture-validated) |
| Counterbalancing works | PASS (fixture-asserted frozen matrix) |
| Schema complete | PASS (fixture-validated) |
| Deterministic raw → analysis | PASS (fixture-validated) |
| Git clean except approved local artifacts | PASS |
| PILOT-002 executed | **NO** (not authorized by this gate) |

## 12. Known Limitations / Confounders (carried forward)

1. Minimal 3-cell synthetic substrate — not production-representative.
2. WSL2 + full OpenSTA binary path required (canonical config documented;
   default Windows `Path.home()` resolution remains non-canonical).
3. Model is an agent-mode file-writing model; prompt must stay in the terse
   directive form (P173-R); stochastic (temperature 0.0 ≠ deterministic),
   bounded retry covers generation failures.
4. Ṛta arm fail-closes REJECT at INSUFFICIENT scope under the netlist-less
   contract (see §7) — must be resolved by the future experiment design.
5. OpenSTA T1 floor effect (10 ns clock ⇒ clean from the start) is by
   design; T2 exercises the violation → revision path.

## 13. Research Boundary

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

## 14. Decision

```text
READY
```

All P172 §16 prerequisites verified. **READY does not authorize execution**:
EGER-RQ5-PILOT-002 requires a separate, explicit experiment-authorization
gate, and the future experiment gate must resolve the §7 Ṛta-scope
protocol question before any trial.

## 15. Git

- Commit: `(P174 commit, see git log)`
- HEAD == origin/main: YES
- `Universal_Principles_Library/` untouched
- Local-only (not committed): `raw_trials.json`, `analysis.json`,
  `qualification_record.json`, `smoke_readiness_record.json`
