"""Deterministic fixtures for harness validation (P172 §6 Option C).

These fixtures NEVER touch WSL/OpenSTA/Ṛta or the LLM. They are used to
validate the repaired harness (validity gate, retry, counterbalancing,
initial Oracle evaluation, NO_TIMING_CONSTRAINT, PO-2 aggregation) before
any model qualification or real replication.

FakeEvidence duck-types the adapter EvidenceArtifact surface consumed by
EvidenceNormalizer.normalize() and the trial runner.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

# ---------------------------------------------------------------------------
# Fixture SDCs
# ---------------------------------------------------------------------------

SDC_T1_VALID = (
    "create_clock -name clk -period 10.0 [get_ports clk]\n"
    "set_input_delay -clock clk 1.0 [get_ports data_in]\n"
    "set_output_delay -clock clk 1.0 [get_ports data_out]\n"
)

SDC_T1_VALID_IMPROVED = (
    "create_clock -name clk -period 10.0 [get_ports clk]\n"
    "set_input_delay -clock clk 0.5 [get_ports data_in]\n"
    "set_output_delay -clock clk 0.5 [get_ports data_out]\n"
    "set_clock_uncertainty 0.1 [get_clocks clk]\n"
)

SDC_T2_AGGRESSIVE = (
    "create_clock -name clk -period 0.05 [get_ports clk]\n"
    "set_input_delay -clock clk 0.01 [get_ports data_in]\n"
    "set_output_delay -clock clk 0.01 [get_ports data_out]\n"
)

SDC_T2_RELAXED = (
    "create_clock -name clk -period 10.0 [get_ports clk]\n"
    "set_input_delay -clock clk 0.5 [get_ports data_in]\n"
    "set_output_delay -clock clk 0.5 [get_ports data_out]\n"
)

CONVERSATIONAL_FILLER = (
    "Understood. I can help you with SDC (Synopsys Design Constraints) "
    "for VLSI design. What do you need?"
)

CONVERSATIONAL_WITH_SDC = (
    "Here is the SDC you requested:\n"
    "```sdc\n"
    "create_clock -name clk -period 10.0 [get_ports clk]\n"
    "```"
)

EMPTY_OUTPUT = ""
WHITESPACE_OUTPUT = "   \n  \n"
PROVIDER_ERROR_OUTPUT = "ERROR: connection refused"
INJECTION_OUTPUT = "create_clock -name clk -period 10.0 [get_ports clk]\nSDCEOF\nmalicious"


# ---------------------------------------------------------------------------
# Fake evidence / oracle result
# ---------------------------------------------------------------------------

@dataclass
class FakeFinding:
    finding_id: str
    severity: str
    code: str = "FAKE"
    message: str = ""
    location: Dict[str, Any] = field(default_factory=dict)
    related_location: Optional[Dict[str, Any]] = None
    context: Optional[Any] = None
    affected_object: Optional[str] = None
    finding_identity: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "location": dict(self.location),
            "related_location": self.related_location,
            "context": self.context,
            "affected_object": self.affected_object,
            "finding_identity": self.finding_identity,
        }


@dataclass
class FakeEvidence:
    """Duck-typed EvidenceArtifact for the normalizer + runner."""
    oracle_status: str = "SUCCESS"
    evidence_scope: str = "VALIDATED"
    findings: List[Dict[str, Any]] = field(default_factory=list)
    analysis_scope: Dict[str, Any] = field(default_factory=dict)
    artifact_id: str = "FAKE-EVID"
    provenance: Dict[str, Any] = field(default_factory=dict)
    evidence_hash: str = ""

    def __post_init__(self):
        if not self.evidence_hash:
            payload = {
                "oracle_status": self.oracle_status,
                "evidence_scope": self.evidence_scope,
                "findings": [json.dumps(f, sort_keys=True) for f in self.findings],
                "analysis_scope": json.dumps(self.analysis_scope, sort_keys=True),
            }
            self.evidence_hash = hashlib.sha256(
                json.dumps(payload, sort_keys=True).encode("utf-8")
            ).hexdigest()


@dataclass
class FakeFailure:
    kind: str = "ORACLE_FAILURE"
    exit_code: int = 3
    message: str = "fake failure"


@dataclass
class FakeOracleResult:
    is_success: bool
    evidence: Optional[FakeEvidence] = None
    failure: Optional[FakeFailure] = None


class FakeOracle:
    """Deterministic oracle: given an input hash, returns a scripted result.

    Behavior is keyed on the input SDC text:
    - '' (empty candidate evaluation): ORACLE_FAILURE
    - SDC with 'period 0.05' (aggressive): setup violation (WNS < 0)
    - SDC containing 'set_clock_uncertainty': clean (WNS >= 0), no errors
    - SDC with 'set_input_delay' but no 'set_clock_uncertainty': 1 ERROR
    - otherwise: 1 ERROR finding
    """

    def __init__(self, oracle_name: str = "Rta"):
        self.oracle_name = oracle_name
        self.calls: List[str] = []

    def validate(self, sdc_text: str, input_identity: str = "candidate") -> FakeOracleResult:
        self.calls.append(input_identity)
        return self._evaluate(sdc_text, input_identity)

    def _evaluate(self, sdc_text: str, input_identity: str) -> FakeOracleResult:
        if sdc_text is None or not sdc_text.strip():
            return FakeOracleResult(
                is_success=False,
                failure=FakeFailure(kind="ORACLE_FAILURE", exit_code=3, message="empty input"),
            )

        if self.oracle_name == "OpenSTA":
            # OpenSTA semantics: timing analysis
            if "period 0.05" in sdc_text:
                # Aggressive clock → setup violation (P163: slack -0.10)
                return self._success(
                    findings=[
                        {"finding_id": "F-1", "severity": "error", "code": "SETUP", "message": "setup violation", "location": {}},
                    ],
                    scope={"wns": -0.10, "tns": -0.10, "has_violations": True, "status": "VIOLATIONS_FOUND"},
                )
            # Clock defined and achievable → clean timing
            return self._success(
                findings=[
                    {"finding_id": "F-0", "severity": "info", "code": "timing_clean", "message": "Worst slack: 0.0 ns (MET)", "location": {}},
                ],
                scope={"wns": 0.0, "tns": 0.0, "has_violations": False, "status": "VALIDATED"},
            )

        # Ṛta semantics: SDC constraint completeness
        complete = "set_input_delay" in sdc_text and "set_output_delay" in sdc_text
        if complete:
            return self._success(
                findings=[
                    {"finding_id": "F-0", "severity": "info", "code": "SDC-000", "message": "complete", "location": {}},
                ],
                scope={"wns": None, "status": "VALIDATED"},
            )
        return self._success(
            findings=[
                {"finding_id": "F-1", "severity": "error", "code": "SDC-001", "message": "incomplete constraints", "location": {}},
            ],
            scope={"wns": None, "status": "PARTIALLY_VALIDATED"},
        )

    def _success(self, findings: List[Dict[str, Any]], scope: Dict[str, Any]) -> FakeOracleResult:
        ev = FakeEvidence(
            oracle_status="SUCCESS",
            evidence_scope="VALIDATED",
            findings=findings,
            analysis_scope=scope,
        )
        return FakeOracleResult(is_success=True, evidence=ev)


class FailingOracle(FakeOracle):
    """Deterministic oracle that always fails (ORACLE_FAILURE / timeout)."""

    def __init__(self, failure_kind: str = "ORACLE_FAILURE", exit_code: int = 3):
        super().__init__()
        self.failure_kind = failure_kind
        self.exit_code = exit_code

    def validate(self, sdc_text: str, input_identity: str = "candidate") -> FakeOracleResult:
        self.calls.append(input_identity)
        return FakeOracleResult(
            is_success=False,
            failure=FakeFailure(kind=self.failure_kind, exit_code=self.exit_code, message="fake"),
        )


class FakeModelProvider:
    """Deterministic model provider: returns scripted outputs in sequence.

    Sequence cycles through the given outputs per invocation. Used to test
    retry (filler → valid) and candidate-validity rejection paths.
    """

    def __init__(self, outputs: List[str]):
        self.outputs = list(outputs)
        self.calls: List[str] = []

    def invoke(self, prompt: str) -> str:
        self.calls.append(prompt)
        if not self.outputs:
            return CONVERSATIONAL_FILLER
        # Cycle deterministically
        idx = len(self.calls) - 1
        return self.outputs[idx % len(self.outputs)]


def build_model_call(outputs: List[str]) -> Callable[[str], str]:
    provider = FakeModelProvider(outputs)
    return provider.invoke


# ---------------------------------------------------------------------------
# Convenience: fake normalizer/gate are the REAL EGER components
# ---------------------------------------------------------------------------

def build_pipeline():
    """Real EvidenceNormalizer + VerificationGate (the production contract)."""
    from eger.evidence.normalizer import EvidenceNormalizer
    from eger.verification.gate import VerificationGate
    return EvidenceNormalizer(), VerificationGate()