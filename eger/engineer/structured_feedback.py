"""Deterministic structured feedback renderer for C2.

Converts EvidenceArtifact to a deterministic structured JSON representation
per EGER-EXP-001 v0.3 C2 definition.

This is distinct from C1 text feedback (eger/engineer/feedback.py).

C1: text rendering
C2: structured EvidenceArtifact representation

Deterministic: same evidence attributes → same JSON output, always.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

_SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}

def _severity_sort_key(finding: Dict[str, Any]) -> tuple:
    sev = (finding.get("severity") or "info").lower()
    sev_rank = _SEVERITY_ORDER.get(sev, 99)
    code = finding.get("code") or ""
    fid = finding.get("finding_id") or ""
    return (sev_rank, code, fid)

def render_structured_feedback(evidence: Any) -> str:
    """Deterministic rendering of EvidenceArtifact to C2 structured feedback.

    Returns a JSON string with only protocol-authorized evidence fields:
    - evidence_scope
    - oracle_status
    - findings: severity, code, message, line information
    - scope_limitation (derived from analysis_scope)

    Does NOT include:
    - evaluator-only answers
    - hashes/provenance metadata
    - internal oracle state
    - authorization/epistemic state

    Determinism:
        Findings sorted by severity (error→warning→info) → code → source order.
        JSON keys sorted, separators (',', ':'), ensure_ascii=False.
    """
    oracle_status = getattr(evidence, "oracle_status", None) or "UNKNOWN"
    evidence_scope = getattr(evidence, "evidence_scope", None) or "UNSUPPORTED"
    analysis_scope = getattr(evidence, "analysis_scope", None)

    # Scope limitation (same derivation as text feedback, but as structured field)
    scope_limitation = None
    if analysis_scope:
        # Use same logic as feedback.py for consistency
        netlist = analysis_scope.get("netlist_required", 0) or 0
        unsupported = analysis_scope.get("unsupported", 0) or 0
        tcl = analysis_scope.get("tcl_execution_required") or 0
        limitations = []
        if netlist > 0:
            limitations.append("Netlist-dependent checks could not be evaluated without design context.")
        if unsupported > 0:
            limitations.append("Some constructs are unsupported by the current oracle scope.")
        if tcl > 0:
            limitations.append("TCL execution required for full analysis.")
        if not limitations:
            status = analysis_scope.get("status", "NOT_VALIDATED")
            if status == "VALIDATED":
                scope_limitation = "All constructs fully analyzed within oracle scope."
            elif status == "PARTIALLY_VALIDATED":
                scope_limitation = "Some constructs partially analyzed."
            else:
                scope_limitation = f"Analysis scope status: {status}."
        else:
            scope_limitation = " ".join(limitations)
    else:
        scope_limitation = "No analysis scope information available."

    raw_findings = getattr(evidence, "findings", []) or []
    sorted_findings = sorted(raw_findings, key=_severity_sort_key)

    structured_findings: List[Dict[str, Any]] = []
    for f in sorted_findings:
        sev = (f.get("severity") or "info").lower()
        code = f.get("code") or ""
        msg = f.get("message") or f.get("msg") or ""
        loc = f.get("location") or {}
        line = loc.get("line") if isinstance(loc, dict) else None
        line_val = line if line and line != 0 else None
        # Preserve only authorized fields
        structured_findings.append({
            "severity": sev,
            "code": code,
            "message": msg,
            "line": line_val,
        })

    structured = {
        "oracle_status": oracle_status,
        "evidence_scope": evidence_scope,
        "scope_limitation": scope_limitation,
        "findings": structured_findings,
    }

    # Deterministic JSON serialization
    return json.dumps(structured, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
