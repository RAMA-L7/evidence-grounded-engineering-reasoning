# EGER Reproducibility & Data Boundaries

This page describes what can be reproduced from the repository, what requires the original local experimental artifacts or environment, and the data boundaries that keep raw experimental records separate from the public package.

## Environment

### EGER implementation

- The EGER implementation lives in `eger/` and is tested by the normal regression suite.
- Deterministic layers (contracts, verification, evidence, oracle, epistemic, authorization, engineer, revision, provenance) are implemented and tested.
- Run the regression suite to verify implementation integrity: `python -m pytest tests -q`.

### Oracle configuration (frozen)

- **Ṛta:** version 1.5.11, pinned commit `3b5c2f2`, invoked as a read-only external deterministic authority. The project does not modify Ṛta and does not invoke `rta_generate`.
- **OpenSTA:** version 2.2.0 (used under WSL2 in the relevant experimental records). OpenSTA is used as a deterministic timing authority.

### Models used in P185

- **Baseline:** `opencode/mimo-v2.5-free`
- **Comparison:** `opencode/nemotron-3.5-lightning-free`

Model identifiers, provider/runtime, and frozen invocation configuration are recorded in the P184/P185 experimental records. The repository does not expose provider API keys or payment configuration.

## Frozen experimental design

### Methodology

- P169 / P172: RQ-5 experimental methodology
- P177 / P178: matrix, identity, and trial-qualification rules
- P183: model-comparison experimental design
- P184: execution readiness gate
- P185: model-comparison execution (PILOT-003)

### Frozen matrix

- **RQ-5 / PILOT-002:** 2 tasks × 2 Oracles × 2 replications = 8 trials
- **P185 / PILOT-003:** 2 models × 2 tasks × 2 Oracles × 2 replications = 16 trials

### Trial ordering

- PILOT-002: counterbalanced (T1 Ṛta-first; T2 OpenSTA-first)
- P185: baseline model (mimo) block first, comparison model (nemotron) second; counterbalanced within blocks (T1 Ṛta-first; T2 OpenSTA-first)

### Retry policy

- Maximum 1 bounded retry per trial (per the frozen P169/P172 protocol).
- Retry only for provider failure, empty output, invalid model output, timeout, or infrastructure failure.
- If a retry occurs, both attempts are retained and `retry_count` is recorded.

### Outcome definitions

- **PO-1:** ROBUST / MARGINAL / FAILED
- **PO-2:** evidence compatibility per trial
- **PO-3:** IMPROVED / NOT_IMPROVED / WORSE / NOT_MEASURABLE (Oracle-specific)

### Qualified-accept rule

- An ACCEPT based on metadata-unqualified or PARTIAL evidence is not a fully qualified ACCEPT.
- For Ṛta: FULL evidence is expected when frozen P055 DesignMetadata references validate.
- For OpenSTA: require valid clock and meaningful constrained timing evaluation (no `NO_TIMING_CONSTRAINT` vacuous-pass condition).

## Data boundaries

The package distinguishes:

1. **Source code** — `eger/`, harness, tests — version-controlled.
2. **Protocols and research records** — `research/` implementation records, schemas, contracts, architectures — version-controlled.
3. **Evidence artifacts / analysis outputs** — the controlled, derived research outputs referenced by the experimental records.
4. **Raw experimental records** — the local, sensitive experimental datasets from PILOT-001, PILOT-002, and PILOT-003.

### Raw experimental records

Raw experimental records (for example, PILOT-002 and PILOT-003 raw trial records, analysis outputs, and execution logs) remain **local** and are **not automatically exposed by the repository package**. The published research records cite these by manifest path where needed but do not embed them.

Do not stage raw experimental JSON or execution logs unless explicitly authorized.

## What can be reproduced from the repository

From the repository alone, a reader can reproduce:

- The EGER implementation and its deterministic layers
- The contracts and schemas
- The frozen task definitions and benchmark
- The architecture recommendation (ARCH-002, pending/unvalidated)
- The experimental design, frozen matrices, retry policy, PO definitions, and qualified-accept rules
- The research conclusions, claim boundaries, and documentation gaps

What requires the original local experimental artifacts or environment:

- Exact raw trial records from PILOT-001/002/003
- Exact P185 evidence/analysis artifacts
- Model invocations (provider configuration, keys, payment/status)
- Oracle runtime environment for exact replication of OpenSTA timing runs

## What cannot be reproduced without the local artifacts/environment

- Bit-for-bit reproduction of the exact P185 raw trial records is not supported by the repository alone.
- The repository does not contain provider credentials, payment status, or the live model runtime.
- Exact OpenSTA timing numbers require the frozen substrate, the OpenSTA environment, and the specific SDC candidates from the experimental run.

## Provenance

- Hash-based provenance is implemented and tested (input/raw/evidence/candidate hashes + timestamp-as-provenance).
- Provenance rules are defined and the provenance tracker is tested.
- The package-level reproducibility page (this file) consolidates the human-readable provenance boundary.

## Claim boundary reminder

This reproducibility page is a documentation artifact. It does not change the frozen research conclusions. The research does **NOT** establish model independence, statistical superiority, universal generalization, production-scale generalization, or Oracle interchangeability.
