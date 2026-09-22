#!/usr/bin/env python3
"""EGER-P199 independent hash check.

Verifies the submission package with Python's hashlib implementation of
SHA-256 — independent of the `sha256sum` tool that produced
PACKAGE-CHECKSUMS.sha256 and EGER-P199-CLOSURE-MANIFEST-001.sha256.

Process concern being addressed (EGER-P199-VERDICT-CORRECTION-001 §1.3):
a publication gate must not claim a clean PASS after a checksum-like
value was fabricated in a draft, without an independent final hash
verification. This script IS that verification step.

Usage:
    python EGER-P199-INDEPENDENT-HASH-CHECK.py [--write-results]

Exit codes: 0 = all verified, 1 = mismatch/missing file, 2 = setup error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Every file in the submission package (draft extras + gate records +
# thesis + checksum sidecars). Checksum sidecars are verified too: their
# own content is compared against the hashes of the files they cover.
PACKAGE_FILES = [
    "EGER-THESIS-001.md",
    "EGER-THESIS-001-SubmissionCandidate-v1.0.pdf",
    "REPRODUCIBILITY.md",
    "SUBMISSION-NOTES.md",
    "EGER-P195-SUBMISSION-READINESS-AUDIT-001.md",
    "COVER-PAGE-AND-DECLARATIONS.md",
    "COVER-LETTER-AND-METADATA.md",
    "README-REVIEW.md",
    "EGER-P199-EGER002-BOUNDARY-NOTE.md",
    "EGER-P199-F1-F2-F3-SUBMISSION-CONDITIONS-001.md",
    "EGER-P199-PRE-SUBMISSION-CLOSURE-001.md",
    "EGER-P199-CLOSURE-MANIFEST-001.md",
    "EGER-P199-VERDICT-CORRECTION-001.md",
    "EGER-P199-INDEPENDENT-HASH-CHECK.py",
]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:  # byte-mode: no newline translation
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_sha256sum_file(p: Path) -> dict:
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, _, name = line.partition(" ")
        name = name.lstrip("*").strip()
        out[name] = digest.lower()
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="EGER-P199 independent hash check")
    ap.add_argument("--write-results", action="store_true",
                    help="write EGER-P199-INDEPENDENT-HASH-CHECK-RESULTS.md")
    args = ap.parse_args(argv)

    results = []
    failures = []

    # 1. cross-implementation check: hashlib vs the two sidecar files
    sidecars = {}
    for sidecar in ("PACKAGE-CHECKSUMS.sha256",
                    "EGER-P199-CLOSURE-MANIFEST-001.sha256"):
        p = HERE / sidecar
        if not p.is_file():
            failures.append(f"sidecar missing: {sidecar}")
            continue
        sidecars.update(parse_sha256sum_file(p))

    for name in PACKAGE_FILES:
        p = HERE / name
        if not p.is_file():
            failures.append(f"missing file: {name}")
            results.append({"file": name, "status": "MISSING"})
            continue
        actual = sha256_of(p)
        if name in sidecars:
            expected = sidecars[name]
            status = "OK" if actual == expected else "MISMATCH"
            if status != "OK":
                failures.append(
                    f"{name}: hashlib {actual[:16]}… != sidecar {expected[:16]}…")
            results.append({"file": name, "hashlib": actual,
                            "sidecar": expected, "status": status})
        else:
            results.append({"file": name, "hashlib": actual,
                            "status": "NO-SIDECAR-ENTRY"})
            failures.append(f"{name}: not covered by either sidecar — "
                            "regenerate sidecars")

    # 2. sidecar self-coverage: the manifest's .sha256 must match the
    #    manifest file as it exists now
    mp = HERE / "EGER-P199-CLOSURE-MANIFEST-001.md"
    sp = HERE / "EGER-P199-CLOSURE-MANIFEST-001.sha256"
    if mp.is_file() and sp.is_file():
        claimed = parse_sha256sum_file(sp).get(mp.name, "")
        actual = sha256_of(mp)
        ok = claimed == actual
        results.append({"file": f"{mp.name} (self-sidecar)", "hashlib": actual,
                        "sidecar": claimed, "status": "OK" if ok else "MISMATCH"})
        if not ok:
            failures.append("manifest sidecar does not match manifest content")

    verdict = "ALL VERIFIED" if not failures else "FAILURES PRESENT"
    print("=== EGER-P199 INDEPENDENT HASH CHECK (Python hashlib) ===")
    for r in results:
        mark = {"OK": "OK  ", "MISMATCH": "FAIL", "MISSING": "MISS",
                "NO-SIDECAR-ENTRY": "UNCOV"}.get(r["status"], "????")
        print(f"[{mark}] {r['file']}  {r.get('hashlib', '')[:16]}")
    print(f"VERDICT: {verdict}")

    if args.write_results:
        doc = [
            "# EGER-P199 — Independent Hash Check Results — 001",
            "",
            "**Executed:** " + datetime.now(timezone.utc).isoformat(),
            "**Method:** Python `hashlib` SHA-256, byte-mode reads —",
            "independent implementation of the digest, cross-checked against",
            "the `sha256sum`-generated sidecars.",
            "**Addressed concern:** EGER-P199-VERDICT-CORRECTION-001 §1.3.",
            "",
            "| File | hashlib SHA-256 (first 16) | vs sidecar | Status |",
            "|---|---|---|---|",
        ]
        for r in results:
            doc.append(f"| {r['file']} | {r.get('hashlib','')[:16]} | "
                       f"{r.get('sidecar','—')[:16]} | {r['status']} |")
        doc += ["", f"**Verdict: {verdict}**", ""]
        if failures:
            doc += ["Failures:", ""] + [f"- {f}" for f in failures] + [""]
        (HERE / "EGER-P199-INDEPENDENT-HASH-CHECK-RESULTS.md").write_text(
            "\n".join(doc), encoding="utf-8")
        print("results written: EGER-P199-INDEPENDENT-HASH-CHECK-RESULTS.md")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
