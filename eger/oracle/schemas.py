"""EGER-SCHEMA-001 — schema versions and declarative evidence_schema.

Extended P055: DesignMetadata for evaluator-side validation.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

SCHEMA_VERSIONS = {
    "candidate": "eger.candidate.v1",
    "raw": "eger.raw.v1",
    "evidence": "eger.evidence.v1",
    "finding": "eger.finding.v1",
    "scope": "eger.scope.v1",
    "design_metadata": "eger.design_metadata.v1",
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


# ---------------------------------------------------------------------------
# Design Metadata — P055 evaluator-side validation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PortDef:
    """Single port definition for evaluator-side validation."""
    name: str
    direction: str  # "input" | "output" | "inout"
    port_type: str  # "clock" | "reset" | "data" | "control" | "power"
    bus: bool = False
    range_str: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PortDef":
        return cls(
            name=d["name"],
            direction=d["direction"],
            port_type=d.get("type", "data"),
            bus=d.get("bus", False),
            range_str=d.get("range"),
        )


class ClockDef:
    """Single clock definition for evaluator-side validation."""
    def __init__(self, name: str, period_ns: float, port: str,
                 generated: bool = False, source_port: Optional[str] = None,
                 divide_by: Optional[int] = None, source_pin: Optional[str] = None):
        self.name = name
        self.period_ns = period_ns
        self.port = port
        self.generated = generated
        self.source_port = source_port
        self.divide_by = divide_by
        self.source_pin = source_pin

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ClockDef":
        return cls(
            name=d["name"],
            period_ns=float(d["period_ns"]),
            port=d["port"],
            generated=d.get("generated", False),
            source_port=d.get("source_port"),
            divide_by=d.get("divide_by"),
            source_pin=d.get("source_pin"),
        )


class CellDef:
    """Single cell definition for evaluator-side validation."""
    def __init__(self, name: str, cell_type: str = "", pins: Optional[List[str]] = None):
        self.name = name
        self.cell_type = cell_type
        self.pins = pins or []

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CellDef":
        return cls(
            name=d["name"],
            cell_type=d.get("type", ""),
            pins=d.get("pins", []),
        )


class DesignMetadata:
    """Evaluator-side design metadata for Oracle validation.

    P054 §5: Level C (ports + clocks + cells).
    This metadata is NEVER exposed to the model.
    """
    METADATA_VERSION = "eger.design_metadata.v1"

    def __init__(self, task_id: str, ports: Optional[List[PortDef]] = None,
                 clocks: Optional[List[ClockDef]] = None,
                 cells: Optional[List[CellDef]] = None,
                 metadata_version: str = METADATA_VERSION):
        self.task_id = task_id
        self.ports = ports or []
        self.clocks = clocks or []
        self.cells = cells or []
        self.metadata_version = metadata_version

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DesignMetadata":
        """Load from evaluator_context JSON structure."""
        dm = d.get("design_metadata", d)
        return cls(
            task_id=d.get("task_id", "UNKNOWN"),
            ports=[PortDef.from_dict(p) for p in dm.get("ports", [])],
            clocks=[ClockDef.from_dict(c) for c in dm.get("clocks", [])],
            cells=[CellDef.from_dict(c) for c in dm.get("cells", [])],
            metadata_version=dm.get("metadata_version", cls.METADATA_VERSION),
        )

    def port_names(self) -> List[str]:
        return [p.name for p in self.ports]

    def clock_names(self) -> List[str]:
        return [c.name for c in self.clocks]

    def cell_names(self) -> List[str]:
        return [c.name for c in self.cells]

    def get_port(self, name: str) -> Optional[PortDef]:
        for p in self.ports:
            if p.name == name:
                return p
        return None

    def get_clock(self, name: str) -> Optional[ClockDef]:
        for c in self.clocks:
            if c.name == name:
                return c
        return None

    def get_cell(self, name: str) -> Optional[CellDef]:
        for c in self.cells:
            if c.name == name:
                return c
        return None
