"""CandidateArtifact — typed, deterministic, immutable extraction.

P150: CandidateArtifact is now frozen (immutable). The `verified` field
has been removed — verification authority belongs solely to VerificationGate.

The candidate is the LLM's unverified proposal. It is NOT evidence.
EvidenceArtifact comes only from Oracle.

INVARIANT: CandidateArtifact is immutable once created.
INVARIANT: CandidateArtifact cannot self-promote to VERIFIED/ACCEPTED.
INVARIANT: VerificationGate is the sole acceptance authority.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple

SCHEMA_CANDIDATE = "eger.candidate.v1"


@dataclass(frozen=True)
class CandidateArtifact:
    """Typed candidate — immutable once created.

    P150: frozen=True, verified field removed.
    Verification authority belongs solely to VerificationGate.

    INVARIANT: All fields are immutable (frozen=True).
    INVARIANT: Cannot self-promote to VERIFIED/ACCEPTED.
    """
    artifact_id: str
    sdc_text: str
    input_hash: str  # SHA256(sdc_text)
    candidate_hash: str  # same as input_hash for semantic identity
    provision: Dict[str, Any]  # provenance: provider, model, prompt_hash, output_hash, etc
    schema_version: str = SCHEMA_CANDIDATE
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Deterministic serialization."""
        return {
            "artifact_id": self.artifact_id,
            "schema_version": self.schema_version,
            "sdc_text": self.sdc_text,
            "input_hash": self.input_hash,
            "candidate_hash": self.candidate_hash,
            "provision": dict(self.provision),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> CandidateArtifact:
        """Deserialize from dict."""
        return cls(
            artifact_id=d["artifact_id"],
            sdc_text=d["sdc_text"],
            input_hash=d["input_hash"],
            candidate_hash=d["candidate_hash"],
            provision=dict(d.get("provision", {})),
            schema_version=d.get("schema_version", SCHEMA_CANDIDATE),
            created_at=d.get("created_at", ""),
        )


def _candidate_hash(sdc_text: str) -> str:
    return hashlib.sha256(sdc_text.encode("utf-8")).hexdigest()


def build_candidate(
    sdc_text: str,
    artifact_id: Optional[str] = None,
    provision: Optional[Dict[str, Any]] = None,
) -> CandidateArtifact:
    """Build an immutable CandidateArtifact."""
    h = _candidate_hash(sdc_text)
    aid = artifact_id or f"EGER-CAND-{h[:12].upper()}"
    return CandidateArtifact(
        artifact_id=aid,
        sdc_text=sdc_text,
        input_hash=h,
        candidate_hash=h,
        provision=provision or {},
        created_at=datetime.now(timezone.utc).isoformat(),
    )


# Deterministic extraction — no LLM, no semantic guessing
_SDC_KEYWORDS = ("create_clock", "create_generated_clock", "set_input_delay", "set_output_delay", "set_false_path", "set_multicycle_path", "set_clock_groups", "set_clock_uncertainty", "set_clock_transition")

def _extract_sdc_block(raw_output: str) -> Optional[str]:
    """Deterministically extract SDC content from model output.

    Strategy:
    1. If output contains ```sdc or ```tcl code fence, extract inside fence
    2. Otherwise, scan for lines containing SDC keywords or TCL-like constraints
    3. If no recognizable SDC content found, return None (malformed)
    """
    # Code fence extraction
    fence_match = re.search(r"```(?:sdc|tcl)?\s*\n(.*?)```", raw_output, re.DOTALL | re.IGNORECASE)
    if fence_match:
        block = fence_match.group(1).strip()
        if any(kw in block for kw in _SDC_KEYWORDS):
            return block
    # Line scan — collect consecutive SDC-like lines
    lines = raw_output.splitlines()
    sdc_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if sdc_lines:
                sdc_lines.append(line)
            continue
        if any(kw in stripped for kw in _SDC_KEYWORDS) or stripped.startswith("set ") or stripped.startswith("create_"):
            sdc_lines.append(line)
        elif sdc_lines:
            # Allow empty continuation but break on non-SDC prose after we've started
            # Only break if line is clearly prose (long, no TCL chars)
            if len(stripped) > 80 and "[" not in stripped and "-" not in stripped:
                break
    candidate = "\n".join(sdc_lines).strip()
    if candidate and any(kw in candidate for kw in _SDC_KEYWORDS):
        return candidate
    # Fallback: if raw output itself looks like SDC (contains keywords), return stripped raw
    if any(kw in raw_output for kw in _SDC_KEYWORDS):
        return raw_output.strip()
    return None


def extract_candidate(raw_output: str, provision: Optional[Dict[str, Any]] = None, artifact_id: Optional[str] = None) -> Optional[CandidateArtifact]:
    """Deterministic extraction. Returns None for malformed output."""
    block = _extract_sdc_block(raw_output)
    if block is None:
        return None
    return build_candidate(block, artifact_id=artifact_id, provision=provision)
