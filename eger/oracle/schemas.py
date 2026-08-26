"""EGER-SCHEMA-001 — schema versions and declarative evidence_schema."""

SCHEMA_VERSIONS = {
    "candidate": "eger.candidate.v1",
    "raw": "eger.raw.v1",
    "evidence": "eger.evidence.v1",
    "finding": "eger.finding.v1",
    "scope": "eger.scope.v1",
}

# Valid enums per contracts
EVIDENCE_SCOPE_VALUES = {"FULL", "PARTIAL", "INSUFFICIENT", "UNSUPPORTED"}
ORACLE_STATUS_VALUES = {"SUCCESS", "INVALID_REQUEST", "ORACLE_FAILURE"}
FINDING_SEVERITY_VALUES = {"error", "warning", "info"}
RAW_SCOPE_STATUS_VALUES = {
    "VALIDATED",
    "PARTIALLY_VALIDATED",
    "NETLIST_REQUIRED",
    "UNSUPPORTED",
    "TCL_EXECUTION_REQUIRED",
    "NOT_VALIDATED",
}

# Scope mapping FROZEN per contract §8
SCOPE_MAP = {
    "VALIDATED": "FULL",
    "PARTIALLY_VALIDATED": "PARTIAL",
    "NETLIST_REQUIRED": "INSUFFICIENT",
    "UNSUPPORTED": "UNSUPPORTED",
    "TCL_EXECUTION_REQUIRED": "UNSUPPORTED",
    "NOT_VALIDATED": "UNSUPPORTED",
}

CAPABILITIES = {
    "syntax_validation": "parses and structurally validates SDC",
    "semantic_analysis": "rule checks (SDC-NNN catalog)",
    "scope_classification": "trust-boundary assignment per construct",
    "clock_analysis": "clock-relation extraction (via analyze_enriched)",
    "constraint_readiness": "readiness signal (if gate uses it)",
}


def evidence_schema():
    """Declarative schema descriptor per EGER-ORACLE-CONTRACT-001 §5."""
    return {
        "schema_versions": SCHEMA_VERSIONS,
        "evidence_scope_values": sorted(EVIDENCE_SCOPE_VALUES),
        "oracle_status_values": sorted(ORACLE_STATUS_VALUES),
        "finding_severity_values": sorted(FINDING_SEVERITY_VALUES),
        "raw_scope_status_values": sorted(RAW_SCOPE_STATUS_VALUES),
        "scope_map": dict(SCOPE_MAP),
        "capabilities": dict(CAPABILITIES),
    }
