"""Deterministic text feedback renderer for C1 feedback-assisted revision.

Converts EvidenceArtifact to deterministic text feedback per the C1 Text
Feedback Contract (EGER-C1-TEXT-FEEDBACK-CONTRACT-001-R1).

This is a PRESENTATION LAYER. It does NOT:
- interpret evidence epistemically
- make authorization decisions
- expose evaluator-only information
- expose hashes/provenance metadata
- become an epistemic engine

Same input → same output, always. No LLM, no probabilistic component.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Severity ordering (frozen per contract)
# ---------------------------------------------------------------------------
_SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


def _severity_sort_key(finding: Dict[str, Any]) -> tuple:
    """Sort key: severity (error→warning→info) → code (alphabetical) → source order."""
    sev = (finding.get("severity") or "info").lower()
    sev_rank = _SEVERITY_ORDER.get(sev, 99)
    code = finding.get("code") or ""
    # Use finding_id as source-order tie-breaker
    fid = finding.get("finding_id") or ""
    return (sev_rank, code, fid)


def _format_line(location: Dict[str, Any]) -> str:
    """Format line number. 0 or missing → 'N/A'."""
    line = location.get("line") if isinstance(location, dict) else None
    if line and line != 0:
        return str(line)
    return "N/A"


def _scope_limitation_text(analysis_scope: Optional[Dict[str, Any]]) -> str:
    """Derive scope limitation text from analysis_scope."""
    if not analysis_scope:
        return "No analysis scope information available."
    status = analysis_scope.get("status", "NOT_VALIDATED")
    limitations = []
    netlist = analysis_scope.get("netlist_required", 0) or 0
    unsupported = analysis_scope.get("unsupported", 0) or 0
    tcl = analysis_scope.get("tcl_execution_required") or 0
    if netlist > 0:
        limitations.append("Netlist-dependent checks could not be evaluated without design context.")
    if unsupported > 0:
        limitations.append("Some constructs are unsupported by the current oracle scope.")
    if tcl > 0:
        limitations.append("TCL execution required for full analysis.")
    if not limitations:
        if status == "VALIDATED":
            return "All constructs fully analyzed within oracle scope."
        elif status == "PARTIALLY_VALIDATED":
            return "Some constructs partially analyzed."
        else:
            return f"Analysis scope status: {status}."
    return " ".join(limitations)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_text_feedback(evidence: Any) -> str:
    """Deterministic rendering of EvidenceArtifact to C1 text feedback.

    Args:
        evidence: EvidenceArtifact (or compatible object with attributes:
                  oracle_status, evidence_scope, analysis_scope, findings)

    Returns:
        Deterministic text string per C1 Text Feedback Contract.

    Determinism guarantee:
        Same evidence attributes → same text output, always.
        Finding order: severity (error→warning→info) → code (alphabetical) → source order.
        Line endings: \\n (LF).
    """
    # --- Oracle execution status ---
    oracle_status = getattr(evidence, "oracle_status", None) or "UNKNOWN"

    # --- Evidence scope ---
    evidence_scope = getattr(evidence, "evidence_scope", None) or "UNSUPPORTED"

    # --- Scope limitation ---
    analysis_scope = getattr(evidence, "analysis_scope", None)
    scope_limitation = _scope_limitation_text(analysis_scope)

    # --- Findings ---
    raw_findings = getattr(evidence, "findings", []) or []
    sorted_findings = sorted(raw_findings, key=_severity_sort_key)

    # --- Build output ---
    parts = []

    # ORACLE RESULT section
    parts.append("ORACLE RESULT")
    parts.append("─────────────")
    parts.append(f"Oracle execution: {oracle_status}")
    parts.append("")

    # EVIDENCE SCOPE section
    parts.append("EVIDENCE SCOPE")
    parts.append("──────────────")
    parts.append(f"Scope: {evidence_scope}")
    parts.append(f"Scope limitation: {scope_limitation}")
    parts.append("")

    # FINDINGS section (only if findings exist)
    if sorted_findings:
        parts.append("FINDINGS")
        parts.append("────────")
        for f in sorted_findings:
            sev = (f.get("severity") or "info").upper()
            code = f.get("code") or ""
            msg = f.get("message") or ""
            loc = f.get("location") or {}
            line_str = _format_line(loc)
            parts.append(f"[{sev}] {code}: {msg} (Line: {line_str})")

    return "\n".join(parts)
