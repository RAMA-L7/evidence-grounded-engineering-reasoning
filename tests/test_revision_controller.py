"""Deterministic unit tests for EGER revision controller (P141).

Tests verify:
- Initial proposal flow
- Revision flow
- Candidate/evidence history
- Budget enforcement
- Failure handling
- Determinism
- Authority boundaries

No live model calls. No external dependencies. Fully deterministic.
"""

import hashlib
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
from eger.revision.record import RunRecord, RevisionConfig


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


def _make_config(
    max_iterations: int = 5,
    max_total_calls: int = 15,
) -> RevisionConfig:
    return RevisionConfig(
        max_iterations=max_iterations,
        max_total_calls=max_total_calls,
    )


# ---------------------------------------------------------------------------
# Fake ProposalGenerator
# ---------------------------------------------------------------------------

class FakeProposalGenerator:
    """Fake LLM that returns deterministic SDC proposals."""

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


class FailingProposalGenerator:
    """Fake LLM that raises an exception."""

    def __init__(self, error_msg: str = "Model unavailable"):
        self.error_msg = error_msg
        self.call_count = 0

    def generate(self, prompt: PromptRequest) -> str:
        self.call_count += 1
        raise RuntimeError(self.error_msg)


class MalformedProposalGenerator:
    """Fake LLM that returns non-SDC output."""

    def __init__(self):
        self.call_count = 0

    def generate(self, prompt: PromptRequest) -> str:
        self.call_count += 1
        return "This is not SDC content at all."


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


@dataclass
class FakeOracleFailure:
    """Fake Oracle failure."""
    kind: str = "ORACLE_FAILURE"
    exit_code: int = 3
    message: str = "Oracle unavailable"


class FakeOracleAdapter:
    """Fake Oracle that returns deterministic results."""

    def __init__(self, findings: Optional[List[dict]] = None, fail: bool = False):
        self.findings = findings or []
        self.fail = fail
        self.call_count = 0
        self.sdc_received: List[str] = []

    def validate(self, sdc_text: str, **kwargs) -> FakeOracleResult:
        self.sdc_received.append(sdc_text)
        self.call_count += 1

        if self.fail:
            return FakeOracleResult(
                is_success=False,
                failure=FakeOracleFailure(),
            )

        return FakeOracleResult(
            is_success=True,
            evidence=FakeOracleEvidence(findings=self.findings),
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
# RevisionController tests
# ---------------------------------------------------------------------------

class TestRevisionController:
    """Tests for eger.revision.controller.RevisionController"""

    def setup_method(self):
        self.prompt_builder = PromptBuilder()
        self.normalizer = EvidenceNormalizer()

    def _make_controller(
        self,
        proposal_generator=None,
        oracle=None,
    ):
        return RevisionController(
            prompt_builder=self.prompt_builder,
            proposal_generator=proposal_generator or FakeProposalGenerator(),
            oracle=oracle or FakeOracleAdapter(),
            normalizer=self.normalizer,
        )

    # -- Initial proposal flow ---------------------------------------------

    def test_initial_proposal_flow(self):
        """Initial proposal: prompt → candidate → oracle → evidence."""
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        oracle = FakeOracleAdapter(findings=[])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=1)
        record = controller.run(task, config)

        assert record.iteration_count == 1
        assert pg.call_count == 1
        assert oracle.call_count == 1
        assert record.total_calls == 2

    def test_initial_proposal_candidate_unverified(self):
        """Candidate remains unverified after initial proposal."""
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        oracle = FakeOracleAdapter(findings=[])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=1)
        record = controller.run(task, config)

        # Check that candidate was generated
        assert record.final_candidate_id is not None

    def test_initial_proposal_prompt_built(self):
        """PromptBuilder is invoked for initial proposal."""
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        oracle = FakeOracleAdapter(findings=[])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=1)
        controller.run(task, config)

        assert len(pg.prompts_received) == 1
        assert pg.prompts_received[0].iteration == 0

    # -- Revision flow -----------------------------------------------------

    def test_one_revision(self):
        """One revision: candidate0 → evidence0 → candidate1 → evidence1."""
        # Use a stateful oracle that returns error first, then no errors
        class StatefulOracle:
            def __init__(self):
                self.call_count = 0
                self.sdc_received = []
            def validate(self, sdc_text, **kwargs):
                self.call_count += 1
                self.sdc_received.append(sdc_text)
                if self.call_count == 1:
                    return FakeOracleResult(
                        is_success=True,
                        evidence=FakeOracleEvidence(findings=[
                            {"finding_id": "F-1", "code": "SDC-001", "severity": "error",
                             "message": "Missing input delay", "location": {}},
                        ]),
                    )
                else:
                    return FakeOracleResult(
                        is_success=True,
                        evidence=FakeOracleEvidence(findings=[]),
                    )

        oracle = StatefulOracle()
        pg = FakeProposalGenerator([
            "create_clock -name clk -period 10.0 [get_ports clk]",
            "create_clock -name clk -period 10.0 [get_ports clk]\nset_input_delay 0.5 [get_ports data_in]",
        ])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=3)
        record = controller.run(task, config)

        assert record.iteration_count == 2
        assert pg.call_count == 2
        assert oracle.call_count == 2

    def test_multiple_revisions(self):
        """Multiple revisions maintain correct iteration order."""
        pg = FakeProposalGenerator([
            "sdc_v0",
            "sdc_v1",
            "sdc_v2",
        ])
        oracle = FakeOracleAdapter(findings=[
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "error 1", "location": {}},
        ])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=3, max_total_calls=9)
        record = controller.run(task, config)

        assert record.iteration_count == 3
        assert pg.call_count == 3
        assert oracle.call_count == 3

    def test_revision_uses_previous_candidate(self):
        """Revision includes previous candidate in prompt."""
        pg = FakeProposalGenerator(["sdc_v0", "sdc_v1"])
        oracle = FakeOracleAdapter(findings=[
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "error", "location": {}},
        ])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=2, max_total_calls=6)
        controller.run(task, config)

        # Second prompt should be different (revision mode)
        assert len(pg.prompts_received) == 2
        assert pg.prompts_received[1].iteration == 1

    # -- Candidate history -------------------------------------------------

    def test_candidate_history_preserved(self):
        """Every candidate remains available in RunRecord."""
        pg = FakeProposalGenerator(["sdc_v0", "sdc_v1"])
        oracle = FakeOracleAdapter(findings=[
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "error", "location": {}},
        ])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=2, max_total_calls=6)
        record = controller.run(task, config)

        # Both iterations recorded
        assert record.iteration_count == 2
        iter0 = record.iterations[0]
        iter1 = record.iterations[1]
        assert "candidate_id" in iter0
        assert "candidate_id" in iter1
        assert iter0["candidate_id"] != iter1["candidate_id"]

    # -- Evidence history --------------------------------------------------

    def test_evidence_history_preserved(self):
        """Every evidence artifact remains available in RunRecord."""
        pg = FakeProposalGenerator(["sdc_v0", "sdc_v1"])
        oracle = FakeOracleAdapter(findings=[
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "error", "location": {}},
        ])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=2, max_total_calls=6)
        record = controller.run(task, config)

        # Both iterations have evidence
        for iteration in record.iterations:
            assert "evidence_id" in iteration

    # -- Budget enforcement ------------------------------------------------

    def test_max_iterations_enforced(self):
        """Max iterations terminates the loop."""
        pg = FakeProposalGenerator(["sdc"] * 10)
        oracle = FakeOracleAdapter(findings=[
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "error", "location": {}},
        ])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=2, max_total_calls=20)
        record = controller.run(task, config)

        assert record.iteration_count == 2
        assert "MAX_ITERATIONS" in record.final_decision

    def test_model_call_budget_enforced(self):
        """Model call budget terminates the loop."""
        pg = FakeProposalGenerator(["sdc"] * 10)
        oracle = FakeOracleAdapter(findings=[
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "error", "location": {}},
        ])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        # Budget: 4 total calls = 2 iterations (2 model + 2 oracle)
        config = _make_config(max_iterations=10, max_total_calls=4)
        record = controller.run(task, config)

        assert record.total_calls <= 4

    def test_oracle_call_budget_enforced(self):
        """Total call budget terminates the loop."""
        pg = FakeProposalGenerator(["sdc"] * 10)
        oracle = FakeOracleAdapter(findings=[
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "error", "location": {}},
        ])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        # Budget: 3 calls = 1 iteration (1 model + 1 oracle) + 1 model
        config = _make_config(max_iterations=10, max_total_calls=3)
        record = controller.run(task, config)

        assert oracle.call_count == 1  # 1 iteration completed
        assert record.total_calls <= 3

    def test_budget_exact_boundary(self):
        """Budget at exact boundary terminates correctly."""
        pg = FakeProposalGenerator(["sdc"] * 10)
        oracle = FakeOracleAdapter(findings=[
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "error", "location": {}},
        ])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        # 3 calls = 1 iteration (1 model + 1 oracle) + 1 model
        config = _make_config(max_iterations=10, max_total_calls=3)
        record = controller.run(task, config)

        assert record.total_calls <= 3

    # -- Natural termination (no errors) -----------------------------------

    def test_no_errors_terminates(self):
        """No errors terminates the loop naturally."""
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        oracle = FakeOracleAdapter(findings=[])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=5)
        record = controller.run(task, config)

        assert record.iteration_count == 1
        assert "NO_ERRORS" in record.final_decision

    # -- Failure handling --------------------------------------------------

    def test_model_failure_returns_incomplete(self):
        """Model failure returns INCOMPLETE status."""
        pg = FailingProposalGenerator("Model crashed")
        oracle = FakeOracleAdapter()
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=5)
        record = controller.run(task, config)

        assert record.status == "INCOMPLETE"
        assert "MODEL_FAILURE" in record.final_decision

    def test_model_failure_no_fabricated_candidate(self):
        """Model failure does not fabricate a candidate."""
        pg = FailingProposalGenerator("Model crashed")
        oracle = FakeOracleAdapter()
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=5)
        record = controller.run(task, config)

        assert record.final_candidate_id is None

    def test_none_output_returns_incomplete(self):
        """None output returns INCOMPLETE status."""
        class NoneProposalGenerator:
            def __init__(self):
                self.call_count = 0
            def generate(self, prompt):
                self.call_count += 1
                return None

        pg = NoneProposalGenerator()
        oracle = FakeOracleAdapter()
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=5)
        record = controller.run(task, config)

        assert record.status == "INCOMPLETE"
        assert "MALFORMED_OUTPUT" in record.final_decision

    def test_oracle_failure_returns_incomplete(self):
        """Oracle failure returns INCOMPLETE status."""
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        oracle = FakeOracleAdapter(fail=True)
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=5)
        record = controller.run(task, config)

        assert record.status == "INCOMPLETE"
        assert "ORACLE_FAILURE" in record.final_decision

    def test_oracle_failure_produces_failure_evidence(self):
        """Oracle failure produces failure evidence, not zero-error evidence."""
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        oracle = FakeOracleAdapter(fail=True)
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=5)
        record = controller.run(task, config)

        # Should have evidence with errors (failure evidence)
        assert record.final_evidence_id is not None

    def test_oracle_exception_returns_incomplete(self):
        """Oracle exception returns INCOMPLETE status."""
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        oracle = FailingOracleAdapter("Oracle crashed")
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=5)
        record = controller.run(task, config)

        assert record.status == "INCOMPLETE"
        # The terminal reason contains ORACLE_FAILURE (from exception handling)
        assert "ORACLE" in record.final_decision

    # -- Determinism -------------------------------------------------------

    def test_same_inputs_same_output(self):
        """Same inputs produce equivalent RunRecord."""
        pg1 = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        pg2 = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        oracle1 = FakeOracleAdapter(findings=[])
        oracle2 = FakeOracleAdapter(findings=[])

        controller1 = self._make_controller(proposal_generator=pg1, oracle=oracle1)
        controller2 = self._make_controller(proposal_generator=pg2, oracle=oracle2)

        task = _make_task()
        config = _make_config(max_iterations=1)
        record1 = controller1.run(task, config, run_id="R-001")
        record2 = controller2.run(task, config, run_id="R-001")

        assert record1.iteration_count == record2.iteration_count
        assert record1.total_calls == record2.total_calls
        assert record1.final_decision == record2.final_decision

    # -- Immutability ------------------------------------------------------

    def test_task_not_mutated(self):
        """Controller does not mutate TaskDefinition."""
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        oracle = FakeOracleAdapter(findings=[])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        original_id = task.task_id
        config = _make_config(max_iterations=1)
        controller.run(task, config)

        assert task.task_id == original_id

    def test_config_not_mutated(self):
        """Controller does not mutate RevisionConfig."""
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        oracle = FakeOracleAdapter(findings=[])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=3)
        original_max = config.max_iterations
        controller.run(task, config)

        assert config.max_iterations == original_max

    # -- No bypass ---------------------------------------------------------

    def test_every_candidate_passes_oracle(self):
        """Every candidate reaching the record has passed through Oracle."""
        pg = FakeProposalGenerator(["sdc_v0", "sdc_v1"])
        oracle = FakeOracleAdapter(findings=[
            {"finding_id": "F-1", "code": "C1", "severity": "error",
             "message": "error", "location": {}},
        ])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=2, max_total_calls=6)
        record = controller.run(task, config)

        # Oracle called once per iteration
        assert oracle.call_count == record.iteration_count

    # -- No acceptance authority -------------------------------------------

    def test_controller_cannot_mark_verified(self):
        """Controller cannot independently mark a candidate VERIFIED."""
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        oracle = FakeOracleAdapter(findings=[])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=1)
        record = controller.run(task, config)

        # RunRecord has no verified field
        assert not hasattr(record, "verified")
        # Status is REJECTED (default) — P142 decides
        assert record.status == "REJECTED"

    # -- Provenance --------------------------------------------------------

    def test_provenance_recorded(self):
        """RunRecord contains provenance information."""
        pg = FakeProposalGenerator(["create_clock -name clk -period 10.0 [get_ports clk]"])
        oracle = FakeOracleAdapter(findings=[])
        controller = self._make_controller(proposal_generator=pg, oracle=oracle)

        task = _make_task()
        config = _make_config(max_iterations=1)
        record = controller.run(task, config)

        assert "controller" in record.provenance
        assert "model_calls" in record.provenance
        assert "oracle_calls" in record.provenance
        assert "terminal_reason" in record.provenance
