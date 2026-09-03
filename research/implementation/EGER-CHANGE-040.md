# EGER CHANGE-040 — RQ-5 Protocol Adversarial Review & Revision (P169)

## Purpose

Adversarially review the P168 protocol and revise it to address methodological weaknesses before experimental execution.

## Baseline

- **Commit:** 1821aac12db3b4c4670fdbd1b816e776e6c9e479
- **Branch:** main
- **Prior change:** CHANGE-039 (P168 — Protocol Design)

## P168 Verdict Challenged: YES

P168 was originally `GO`. P169 revised it to address critical methodological issues.

## Major Findings

| # | Finding | Severity | Resolution |
|---|---------|----------|------------|
| 1 | N=1 per condition insufficient | CRITICAL | Increased to N=8 (2 tasks × 2 Oracles × 2 replications) |
| 2 | Task/Oracle asymmetry | HIGH | Redesigned shared task family |
| 3 | Levenshtein as primary metric | HIGH | Demoted to diagnostic; new improvement metric |
| 4 | No retry policy | MEDIUM | Added 1 bounded retry per trial |
| 5 | Fixed order | MEDIUM | Counterbalanced execution order |
| 6 | Single task | MEDIUM | Increased to 2 tasks |
| 7 | Binary outcomes too weak | LOW | 3-level completion quality |

## Protocol Changes

| Aspect | P168 | P169 (Revised) |
|--------|------|----------------|
| Trials | 2 (1 per Oracle) | 8 (2×2×2) |
| Tasks | 1 task, 2 perturbations | 2 tasks, shared design |
| Task/Oracle symmetry | Asymmetric | Both Oracles evaluate same SDC |
| Primary metric | Levenshtein | Oracle-detected improvement |
| Completion metric | Binary | 3-level (ROBUST/MARGINAL/FAILED) |
| Retry policy | None | 1 bounded retry |
| Order | Fixed (Ṛta first) | Counterbalanced |
| Maximum claim | Level 2 | Level 2 (Level 3 if qualitative evidence supports) |

## Test Results

No code changes — protocol documentation only. Full regression: 864/864 PASS (unchanged).

## Decision

GO — revised protocol addresses all 16 criteria.

## Ṛta Impact

None.

## Research Boundary

UNCHANGED — no RQ-5 execution, no Oracle comparison, no C0–C5 modification.
