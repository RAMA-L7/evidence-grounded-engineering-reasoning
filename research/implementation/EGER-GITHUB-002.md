# EGER-GITHUB-002 — Benchmark Exposure Remediation

**Prompt ID:** EGER-GITHUB-002
**Date:** 2026-08-26
**Incident Type:** Process failure — evaluator-only benchmark answers exposed to public repository
**Remediation:** Repository made PRIVATE immediately

---

## 1. Incident Summary

During EGER-GITHUB-001 (public GitHub release), the `gh repo create --push` command executed `git push` automatically before the evaluator-only audit could gate the push. This resulted in **6 evaluator-only benchmark answer files** being exposed to a PUBLIC repository.

**The EGER research project itself is not ruined. BENCH-002's public held-out status is compromised.**

## 2. Timeline

| Time (approx) | Event |
|---------------|-------|
| EGER-GITHUB-001 authorized | Human researcher authorizes GitHub push |
| `gh repo create --push` | Repository created and ALL committed files pushed automatically |
| Push completes | All 14 commits on main pushed to public repository |
| Audit discovers exposure | Evaluator-only files identified as public |
| EGER-GITHUB-002 authorized | Human researcher authorizes remediation |
| `gh repo edit --visibility private` | Repository made PRIVATE immediately |

## 3. Root Cause

The `gh repo create --push` flag combines repository creation and push into a single atomic operation. The protocol (EGER-GITHUB-001 §13) specified that evaluator-only files should be excluded from public release, but:

1. The push was not gated on the evaluator-only audit
2. The `--push` flag executed before the audit could complete
3. No pre-push check existed to block if evaluator-only files were tracked

**This is a process failure, not an experimental result.**

## 4. Exposed Files (During Public Window)

| File | Content | Exposure Duration |
|------|---------|-------------------|
| `research/experiments/EGER-BENCH-002/evaluator_only/BENCH2-001.expected.json` | Expected benchmark answer | ~8 minutes |
| `research/experiments/EGER-BENCH-002/evaluator_only/BENCH2-002.expected.json` | Expected benchmark answer | ~8 minutes |
| `research/experiments/EGER-BENCH-002/evaluator_only/BENCH2-003.expected.json` | Expected benchmark answer | ~8 minutes |
| `research/experiments/EGER-BENCH-002/evaluator_only/BENCH2-004.expected.json` | Expected benchmark answer | ~8 minutes |
| `research/experiments/EGER-BENCH-002/evaluator_only/BENCH2-005.expected.json` | Expected benchmark answer | ~8 minutes |
| `research/experiments/EGER-BENCH-002/evaluator_only/BENCH2-006.expected.json` | Expected benchmark answer | ~8 minutes |

**Exposure window:** Approximately 8 minutes (from push to private change).

**Risk assessment:** Low-to-moderate. The repository had no external watchers at the time of exposure. However, the exposure cannot be fully reversed without history rewriting.

## 5. Remediation Actions Taken

| Action | Status | Method |
|--------|--------|--------|
| Repository made PRIVATE | ✅ COMPLETE | `gh repo edit --visibility private --accept-visibility-change-consequences` |
| Public access revoked | ✅ COMPLETE | Verified via API: `"visibility":"private"` |
| Local evaluator files preserved | ✅ COMPLETE | No local files deleted or modified |
| Git history preserved | ✅ COMPLETE | No `git filter-repo`, `git reset`, or force push |
| EGER-GITHUB-002 documentation | ✅ COMPLETE | This file |
| RESEARCH_LEDGER update | ✅ COMPLETE | Incident recorded |
| STATE.md update | ✅ COMPLETE | Status reflects remediation |

## 6. What Was NOT Done (By Design)

| Action | Reason |
|--------|--------|
| `git filter-repo` | History rewriting requires separate explicit authorization; the exposure itself is part of provenance |
| `git reset --hard` | Destructive; forbidden by protocol §18 |
| `git push --force` | Forbidden by protocol §17 |
| Delete evaluator files from local workspace | Must preserve complete research history |
| Delete evaluator files from git history | Requires deliberate decision about history rewriting |

## 7. Current Repository State

| Item | Value |
|------|-------|
| Repository | https://github.com/RAMA-L7/evidence-grounded-engineering-reasoning |
| Visibility | **PRIVATE** |
| Remote HEAD | 0c4eccc (matches local) |
| Local HEAD | 0c4eccc |
| Branch | main |
| Total commits | 14 |
| Evaluator-only files | Present in git history (private repository) |

## 8. Impact Assessment

### BENCH-002 Integrity

| Aspect | Status |
|--------|--------|
| Held-out answers | Exposed during public window |
| Future public benchmark use | **COMPROMISED** — answers are in git history |
| Current private benchmark use | **INTACT** — answers still available for research |
| Remediation options | See Section 9 |

### Research Integrity

| Aspect | Status |
|--------|--------|
| C0 experimental results | **INTACT** — not affected by publication incident |
| C0 evidence | **INTACT** — preserved in git history |
| C0 checkpoint | **INTACT** — EGER-GIT-001 preserved |
| Scientific conclusions | **NOT AFFECTED** — publication incident is orthogonal to experimental results |

### Ṛta Boundary

| Aspect | Status |
|--------|--------|
| Ṛta HEAD | 3b5c2f2 (unchanged) |
| Ṛta paths in EGER | 0 (unchanged) |
| Ṛta contamination | NONE |

## 9. Remediation Options for BENCH-002

### Option A: Keep Repository Private (RECOMMENDED — CURRENT STATE)

- Repository remains private
- Evaluator-only answers available for research
- No history rewriting needed
- Future public release requires deliberate sanitization

### Option B: History Rewriting + Public Release

- Remove evaluator-only files from git history
- Force push to rewrite history
- Make repository public
- **Requires separate explicit authorization**
- **Risk:** Destroys provenance; may break collaborators' clones

### Option C: Fork Strategy (RECOMMENDED LONG-TERM)

```
PRIVATE EGER RESEARCH REPOSITORY (current)
├── full research history
├── evaluator_only/
├── raw experimental evidence
├── complete benchmark
└── unpublished research material
             │
             │ deliberate publication process
             ▼
PUBLIC EGER RESEARCH/CODE REPOSITORY (future)
├── research methodology
├── architecture
├── implementation
├── public benchmark inputs
├── sanitized aggregate results
└── NO evaluator answers
```

### Option D: Accept Exposure + New Benchmark

- Accept that BENCH-002 answers are in git history
- Design BENCH-003 with assumption that evaluator-only data may leak
- **Not recommended** — weakens benchmark integrity precedent

## 10. Scientific State

```
C0                    ✓ COMPLETE
C0 evidence           ✓ PRESERVED
C0 checkpoint         ✓ PRESERVED
GitHub                ✓ PUSHED (PRIVATE)
Benchmark exposure    ⚠ COMPROMISED (remediated to PRIVATE)
C0 review             ⏸ PAUSED
C1                    ⏸ NOT AUTHORIZED
Ṛta                   ✓ UNTOUCHED
```

## 11. Lessons Learned

1. **Never use `--push` flag with `gh repo create` for sensitive repositories.** The atomic operation bypasses pre-push safety gates.
2. **Pre-push audits must be completed BEFORE any push command is executed.** The protocol should require explicit staging verification before push.
3. **Evaluator-only files should be excluded from git tracking entirely** (via .gitignore) if the repository may ever become public.
4. **The push gate should be a separate, audited step** — not combined with repository creation.

## 12. Recommended Future Protocol Changes

1. Add `.gitignore` entry for `evaluator_only/` in any repository intended for potential public release
2. Require explicit `git push` (not `--push` flag) after full audit
3. Add pre-push hook that blocks if evaluator-only files are staged
4. Maintain separate private/public repositories from the start

## 13. Documentation

- EGER-GITHUB-001.md — Original release documentation (includes exposure incident)
- EGER-GITHUB-002.md — This remediation document
- RESEARCH_LEDGER.md — Updated with incident entry
- STATE.md — Updated with remediation status

## 14. FINAL STATUS

**REMEDIATION COMPLETE — REPOSITORY PRIVATE — BENCHMARK EXPOSURE CONTAINED**

The incident is recoverable. The important thing is that the protocol violation was caught immediately and remediated before external access could be exploited.

**Next research action:** EGER-C0-REVIEW-001 (separate step, after human review).
