"""Deterministic unit tests for EGER end-to-end pipeline (P144).

Tests verify:
- Happy path (ACCEPT)
- Rejection path (REJECT)
- Failure scenarios
- Provenance reconstruction
- Deterministic replay
- Immutability
- Authority boundaries

No live model calls. No external dependencies. Fully deterministic.
"""

import pytest
from typing import Any, Optional, List
from dataclasses import dataclass

from eger.task.definition import TaskDefinition
from eger.evidence.schemas import Finding, EvidenceArtifact, FindingSummary
from eger.engineer.candidate import CandidateArtifact, build_candidate
from eger.prompting.builder import PromptBuilder
from eger.prompting.request import PromptRequest
from eger.evidence.normalizer import EvidenceNormalizer
from eger.revision.controller import RevisionController
from eger.revision.record import RevisionConfig, RunRecord
from eger.verification.gate import VerificationGate
from eger.verification.result import VerificationResult
from eger.provenance.tracker import ProvenanceTracker
from eger.pipeline.e2e import EGERPipeline


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_task() -> TaskDefinition:
    return TaskDefinition(
        task_id="T-001",
        design_context="Module top with ports clk, reset.",
        objective="Generate a complete, production-quality SDC.",
        initial_sdc="create_clock -name clk -period 10.0 [get_ports clk]",
        constraints=["No generated clocks"],
    )


# ---------------------------------------------------------------------------
# Fake ProposalGenerator
# ---------------------------------------------------------------------------

class FakeProposalGenerator:
    """Fake LLM that returns predetermined SDC proposals."""

    def __init__(self, responses: Optional[List[str]] = None):
        self.responses = responses or [
            "create_clock -name clk -period 10.0 [get_ports clk]",
        ]
        self.call_count = 0
        self.prompts_received: List[PromptRequest] = []

    def generate(self, prompt: PromptRequest) -> str:
        self.prompts_received.append(prompt)
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        self.call_count += 1
        return self.responses[-1] if self.responses else ""


def _sdc(text: str) -> str:
    """Ensure text is valid SDC by adding a keyword if needed."""
    if "create_clock" not in text and "set_" not in text:
        return f"create_clock -name clk -period 10.0 [get_ports clk]\n{text}"
    return text


class FailingProposalGenerator:
    """Fake LLM that raises an exception."""

    def __init__(self, error_msg: str = "Model unavailable"):
        self.error_msg = error_msg
        self.call_count = 0

    def generate(self, prompt: PromptRequest) -> str:
        self.call_count += 1
        raise RuntimeError(self.error_msg)


# ---------------------------------------------------------------------------
# Fake OracleAdapter
# ---------------------------------------------------------------------------

@dataclass
class FakeOracleEvidence:
    """Fake Oracle evidence."""
    schema_version: str = "eger.raw.v1"
    artifact_id: str = "ORA-001"
    oracle: dict = None
    provenance: dict = None
    evidence_scope: str = "VALIDATED"
    oracle_status: str = "SUCCESS"
    findings: list = None
    analysis_scope: dict = None
    raw_ref: dict = None
    evidence_hash: str = "abc123"
    produced_at: str = "2026-09-01T00:00:00Z"

    def __post_init__(self):
        if self.oracle is None:
            self.oracle = {"name": "Ṛta", "version": "1.5.11"}
        if self.provenance is None:
            self.provenance = {"oracle_version": "1.5.11"}
        if self.findings is None:
            self.findings = []
        if self.analysis_scope is None:
            self.analysis_scope = {"status": "VALIDATED"}
        if self.raw_ref is None:
            self.raw_ref = {"raw_id": "RAW-001"}


@dataclass
class FakeOracleResult:
    """Fake Oracle result."""
    is_success: bool = True
    evidence: Optional[FakeOracleEvidence] = None
    failure: Any = None


class FakeOracleAdapter:
    """Fake Oracle that returns predetermined results."""

    def __init__(self, findings_sequence: Optional[List[list]] = None):
        """Initialize with a sequence of findings per iteration.

        findings_sequence: list of findings lists, one per call.
            Example: [[error_findings], [], []] means:
            - First call: errors
            - Second call: no errors
            - Third call: no errors
        """
        self.findings_sequence = findings_sequence or [[]]
        self.call_count = 0
        self.sdc_received: List[str] = []

    def validate(self, sdc_text: str, **kwargs) -> FakeOracleResult:
        self.sdc_received.append(sdc_text)
        idx = min(self.call_count, len(self.findings_sequence) - 1)
        findings = self.findings_sequence[idx]
        self.call_count += 1

        return FakeOracleResult(
            is_success=True,
            evidence=FakeOracleEvidence(findings=findings),
        )


class FailingOracleAdapter:
    """Fake Oracle that raises an exception."""

    def __init__(self, error_msg: str = "Oracle crashed"):
        self.error_msg = error_msg
        self.call_count = 0

    def validate(self, sdc_text: str, **kwargs) -> Any:
        self.call_count += 1
        raise RuntimeError(self.error_msg)


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

class TestE2EIntegration:
    """Tests for eger.pipeline.e2e.EGERPipeline"""

    def setup_method(self):
        self.prompt_builder = PromptBuilder()
        self.normalizer = EvidenceNormalizer()
        self.verification_gate = VerificationGate()
        self.provenance = ProvenanceTracker()

    def _make_pipeline(self, pg, oracle):
        return EGERPipeline(
            proposal_generator=pg,
            oracle=oracle,
            prompt_builder=self.prompt_builder,
            normalizer=self.normalizer,
            verification_gate=self.verification_gate,
            provenance=self.provenance,
        )

    # -- Happy path --------------------------------------------------------

    def test_happy_path_accept(self):
        """Complete pipeline: generate → revise → verify → ACCEPT."""
        # Oracle: error on first call, no errors on second
        oracle = FakeOracleAdapter(findings_sequence=[
            [{"finding_id": "F-1", "code": "SDC-001", "severity": "error",
              "message": "Missing input delay", "location": {}}],
            [],
        ])
        pg = FakeProposalGenerator([
            "create_clock -name clk -period 10.0 [get_ports clk]",
            "create_clock -name clk -period 10.0 [get_ports clk]\nset_input_delay 0.5 [get_ports data_in]",
        ])
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=3, max_total_calls=6)
        result = pipeline.run(task, config)

        assert result["verification_result"].is_accepted
        assert result["run_record"].iteration_count == 2
        assert pg.call_count == 2
        assert oracle.call_count == 2

    def test_happy_path_provenance(self):
        """Happy path produces complete provenance."""
        oracle = FakeOracleAdapter(findings_sequence=[[], []])
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=1, max_total_calls=3)
        result = pipeline.run(task, config)

        provenance = result["provenance"]
        # RevisionController records REJECTED; VerificationGate decides ACCEPT
        assert provenance["status"] in ("COMPLETED", "REJECTED")
        assert provenance["final_verification_decision"] == "ACCEPT"
        assert len(provenance["prompts"]) >= 1
        assert len(provenance["candidates"]) >= 1
        assert len(provenance["evidence"]) >= 1

    # -- Rejection path ----------------------------------------------------

    def test_rejection_path(self):
        """Pipeline with persistent errors → REJECT."""
        oracle = FakeOracleAdapter(findings_sequence=[
            [{"finding_id": "F-1", "code": "SDC-001", "severity": "error",
              "message": "Error persists", "location": {}}],
            [{"finding_id": "F-2", "code": "SDC-002", "severity": "error",
              "message": "Still has errors", "location": {}}],
        ])
        pg = FakeProposalGenerator([
            "create_clock -name clk -period 10.0 [get_ports clk]",
            "create_clock -name clk -period 10.0 [get_ports clk]",
        ])
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=2, max_total_calls=6)
        result = pipeline.run(task, config)

        assert result["verification_result"].is_rejected

    # -- Failure scenarios -------------------------------------------------

    def test_model_failure_incomplete(self):
        """Model failure → INCOMPLETE status."""
        pg = FailingProposalGenerator("Model crashed")
        oracle = FakeOracleAdapter()
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=3, max_total_calls=9)
        result = pipeline.run(task, config)

        assert result["run_record"].status == "INCOMPLETE"
        assert "MODEL_FAILURE" in result["run_record"].final_decision

    def test_budget_exhaustion(self):
        """Budget exhaustion → terminal state."""
        oracle = FakeOracleAdapter(findings_sequence=[
            [{"finding_id": "F-1", "code": "C1", "severity": "error",
              "message": "error", "location": {}}],
        ] * 10)
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"] * 10)
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=10, max_total_calls=4)
        result = pipeline.run(task, config)

        assert result["run_record"].total_calls <= 4

    # -- Provenance verification -------------------------------------------

    def test_provenance_reconstruction(self):
        """Provenance reconstructs complete run history."""
        oracle = FakeOracleAdapter(findings_sequence=[
            [{"finding_id": "F-1", "code": "C1", "severity": "error",
              "message": "error", "location": {}}],
            [],
        ])
        pg = FakeProposalGenerator(["sdc_v0", "sdc_v1"])
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=2, max_total_calls=6)
        result = pipeline.run(task, config)

        provenance = result["provenance"]
        assert provenance["run_id"] == result["run_id"]
        assert provenance["task_id"] == "T-001"
        assert len(provenance["prompts"]) == 2
        assert len(provenance["candidates"]) == 2
        assert len(provenance["evidence"]) == 2

    def test_provenance_artifact_relationships(self):
        """Provenance preserves artifact relationships."""
        oracle = FakeOracleAdapter(findings_sequence=[[], []])
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=1, max_total_calls=3)
        result = pipeline.run(task, config)

        provenance = result["provenance"]
        # Verify relationships exist
        assert len(provenance["prompts"]) >= 1
        assert len(provenance["candidates"]) >= 1
        assert len(provenance["evidence"]) >= 1
        assert provenance["verification"] is not None

    # -- Deterministic replay ----------------------------------------------

    def test_deterministic_replay(self):
        """Same inputs produce equivalent results."""
        # Use separate provenance trackers to avoid duplicate run_id
        oracle1 = FakeOracleAdapter(findings_sequence=[[], []])
        oracle2 = FakeOracleAdapter(findings_sequence=[[], []])
        pg1 = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        pg2 = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])

        pipeline1 = EGERPipeline(
            proposal_generator=pg1, oracle=oracle1,
            provenance=ProvenanceTracker(),
        )
        pipeline2 = EGERPipeline(
            proposal_generator=pg2, oracle=oracle2,
            provenance=ProvenanceTracker(),
        )

        task = _make_task()
        config = RevisionConfig(max_iterations=1, max_total_calls=3)

        result1 = pipeline1.run(task, config, run_id="R-001")
        result2 = pipeline2.run(task, config, run_id="R-002")

        assert result1["verification_result"].decision == result2["verification_result"].decision
        assert result1["run_record"].iteration_count == result2["run_record"].iteration_count

    # -- Immutability ------------------------------------------------------

    def test_task_not_mutated(self):
        """Pipeline does not mutate TaskDefinition."""
        oracle = FakeOracleAdapter(findings_sequence=[[], []])
        pg = FakeProposalGenerator(["sdc"])
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        original_id = task.task_id
        config = RevisionConfig(max_iterations=1, max_total_calls=3)
        pipeline.run(task, config)

        assert task.task_id == original_id

    def test_config_not_mutated(self):
        """Pipeline does not mutate RevisionConfig."""
        oracle = FakeOracleAdapter(findings_sequence=[[], []])
        pg = FakeProposalGenerator(["sdc"])
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=3, max_total_calls=9)
        original_max = config.max_iterations
        pipeline.run(task, config)

        assert config.max_iterations == original_max

    # -- Authority boundaries ----------------------------------------------

    def test_only_gate_can_accept(self):
        """Only VerificationGate produces ACCEPT/REJECT."""
        oracle = FakeOracleAdapter(findings_sequence=[[], []])
        pg = FakeProposalGenerator(["sdc"])
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=1, max_total_calls=3)
        result = pipeline.run(task, config)

        # Verification result comes from gate
        assert result["verification_result"].provenance["gate"] == "VerificationGate"

    def test_pipeline_cannot_bypass_oracle(self):
        """Pipeline cannot bypass Oracle evaluation."""
        oracle = FakeOracleAdapter(findings_sequence=[
            [{"finding_id": "F-1", "code": "C1", "severity": "error",
              "message": "error", "location": {}}],
        ])
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=1, max_total_calls=3)
        result = pipeline.run(task, config)

        # Oracle was called
        assert oracle.call_count == 1

    def test_pipeline_cannot_bypass_verification(self):
        """Pipeline cannot bypass VerificationGate."""
        oracle = FakeOracleAdapter(findings_sequence=[[], []])
        pg = FakeProposalGenerator(["sdc"])
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=1, max_total_calls=3)
        result = pipeline.run(task, config)

        # Verification was performed
        assert result["verification_result"] is not None

    def test_pipeline_cannot_bypass_provenance(self):
        """Pipeline cannot bypass provenance recording."""
        oracle = FakeOracleAdapter(findings_sequence=[[], []])
        pg = FakeProposalGenerator(["sdc"])
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=1, max_total_calls=3)
        result = pipeline.run(task, config)

        # Provenance was recorded
        assert result["provenance"] is not None
        assert result["provenance"]["entry_count"] > 0

    # -- No external dependencies ------------------------------------------

    def test_no_network_required(self):
        """Pipeline works without network access."""
        oracle = FakeOracleAdapter(findings_sequence=[[], []])
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=1, max_total_calls=3)
        result = pipeline.run(task, config)

        assert result["verification_result"].is_accepted

    def test_no_api_key_required(self):
        """Pipeline works without API key."""
        oracle = FakeOracleAdapter(findings_sequence=[[], []])
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=1, max_total_calls=3)
        result = pipeline.run(task, config)

        assert result["verification_result"].is_accepted

    # -- Full integration scenario -----------------------------------------

    def test_full_integration_scenario(self):
        """Full end-to-end integration with multiple revisions."""
        # Scenario:
        # iteration 0: generate → Oracle finds errors
        # iteration 1: revise → Oracle finds errors
        # iteration 2: revise → Oracle no errors → ACCEPT
        oracle = FakeOracleAdapter(findings_sequence=[
            [{"finding_id": "F-1", "code": "SDC-001", "severity": "error",
              "message": "Missing input delay", "location": {}}],
            [{"finding_id": "F-2", "code": "SDC-002", "severity": "error",
              "message": "Missing output delay", "location": {}}],
            [],
        ])
        pg = FakeProposalGenerator([
            "create_clock -name clk -period 10.0 [get_ports clk]",
            "create_clock -name clk -period 10.0 [get_ports clk]\nset_input_delay 0.5 [get_ports data_in]",
            "create_clock -name clk -period 10.0 [get_ports clk]\nset_input_delay 0.5 [get_ports data_in]\nset_output_delay 0.5 [get_ports data_out]",
        ])
        pipeline = self._make_pipeline(pg, oracle)

        task = _make_task()
        config = RevisionConfig(max_iterations=5, max_total_calls=15)
        result = pipeline.run(task, config)

        # Verify complete flow
        assert result["verification_result"].is_accepted
        assert result["run_record"].iteration_count == 3
        assert oracle.call_count == 3
        assert pg.call_count == 3

        # Verify provenance has complete history
        provenance = result["provenance"]
        assert len(provenance["prompts"]) == 3
        assert len(provenance["candidates"]) == 3
        assert len(provenance["evidence"]) == 3
        assert provenance["verification"]["decision"] == "ACCEPT"
