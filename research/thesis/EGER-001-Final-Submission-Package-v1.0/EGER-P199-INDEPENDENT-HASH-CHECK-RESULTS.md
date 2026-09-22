# EGER-P199 — Independent Hash Check Results — 001

**Executed:** 2026-09-15T07:32:44.199949+00:00
**Method:** Python `hashlib` SHA-256, byte-mode reads —
independent implementation of the digest, cross-checked against
the `sha256sum`-generated sidecars.
**Addressed concern:** EGER-P199-VERDICT-CORRECTION-001 §1.3.

| File | hashlib SHA-256 (first 16) | vs sidecar | Status |
|---|---|---|---|
| EGER-THESIS-001.md | 296674dd4d51a399 | 296674dd4d51a399 | OK |
| EGER-THESIS-001-SubmissionCandidate-v1.0.pdf | 9e65a5e1333f55d0 | 9e65a5e1333f55d0 | OK |
| REPRODUCIBILITY.md | c8d35f81bab35c22 | c8d35f81bab35c22 | OK |
| SUBMISSION-NOTES.md | e3c9e7c2c3a23520 | e3c9e7c2c3a23520 | OK |
| EGER-P195-SUBMISSION-READINESS-AUDIT-001.md | bed7e6bae9a7c727 | bed7e6bae9a7c727 | OK |
| COVER-PAGE-AND-DECLARATIONS.md | 1ca073e072594965 | 1ca073e072594965 | OK |
| COVER-LETTER-AND-METADATA.md | 5e885692436b7cb8 | 5e885692436b7cb8 | OK |
| README-REVIEW.md | ed0bfa7592267dfa | ed0bfa7592267dfa | OK |
| EGER-P199-EGER002-BOUNDARY-NOTE.md | cac418111e2807da | cac418111e2807da | OK |
| EGER-P199-F1-F2-F3-SUBMISSION-CONDITIONS-001.md | 60ed39b2ad607603 | 60ed39b2ad607603 | OK |
| EGER-P199-PRE-SUBMISSION-CLOSURE-001.md | b9c9f620d9946633 | b9c9f620d9946633 | OK |
| EGER-P199-CLOSURE-MANIFEST-001.md | dab4954230693c51 | dab4954230693c51 | OK |
| EGER-P199-VERDICT-CORRECTION-001.md | 86645abb9727b7ae | 86645abb9727b7ae | OK |
| EGER-P199-INDEPENDENT-HASH-CHECK.py | 7cea45a581c22a67 | 7cea45a581c22a67 | OK |
| EGER-P199-CLOSURE-MANIFEST-001.md (self-sidecar) | dab4954230693c51 | dab4954230693c51 | OK |

**Verdict: ALL VERIFIED**

---

## Scope note (appended 2026-09-15, author-verified clarification)

This check independently confirms the **bytes and hashes** of the package
files (dual-implementation digest agreement: Python `hashlib` vs
`sha256sum`). It is **not** independent scholarly review: it says nothing
about the validity of the research, the literature search, or the
conclusions. Scholarly assessment happens only through examiner/peer
review. The residual conditions F1–F3 remain open per
`EGER-P199-VERDICT-CORRECTION-001.md`.
