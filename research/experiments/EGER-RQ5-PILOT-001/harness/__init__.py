"""P173 repaired RQ-5 experimental harness.

Harness-only code for the future controlled replication (EGER-RQ5-PILOT-002).
Does NOT modify any EGER production module, Ṛta, VerificationGate, or
historical research records.

Components:
- candidate_validity: deterministic VALID_SDC / NON_SDC_OUTPUT / EMPTY_OUTPUT
  classification gate (P172 §5)
- matrix: frozen counterbalanced trial order (P172 §9)
- trial_runner: trial execution with initial Oracle evaluation (PO-3),
  bounded retry, NO_TIMING_CONSTRAINT protection (P172 §7-13)
- analysis: deterministic PO-2 aggregation from raw records (P172 §12)
"""