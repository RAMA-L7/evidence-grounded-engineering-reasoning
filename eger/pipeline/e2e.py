"""EGERPipeline — end-to-end integration of EGER components.

ENGINEERING DESIGN CHOICE: composition/orchestration boundary.

This module connects all EGER components into one coherent pipeline:
TaskDefinition → PromptBuilder → ProposalGenerator → CandidateArtifact
→ OracleAdapter → EvidenceNormalizer → EvidenceArtifact
→ RevisionController → VerificationGate → VerificationResult
→ ProvenanceTracker → Complete Auditable Run

INVARIANT: Pipeline is composition/orchestration ONLY.
INVARIANT: Cannot independently decide ACCEPT/REJECT.
INVARIANT: Cannot bypass Oracle, EvidenceNormalizer, or VerificationGate.
INVARIANT: Cannot modify TaskDefinition, CandidateArtifact, or EvidenceArtifact.

PRODUCER: EGERPipeline (composition)
CONSUMER: External system, audit
"""

from __future__ import annotations

from typing import Optional, Any, Dict
import hashlib
import time

from eger.task.definition import TaskDefinition
from eger.prompting.builder import PromptBuilder
from eger.evidence.normalizer import EvidenceNormalizer
from eger.revision.controller import RevisionController
from eger.verification.gate import VerificationGate
from eger.verification.result import VerificationResult
from eger.provenance.tracker import ProvenanceTracker
from eger.revision.record import RevisionConfig, RunRecord
from eger.engineer.candidate import CandidateArtifact, build_candidate
from eger.evidence.schemas import EvidenceArtifact


def _deterministic_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class EGERPipeline:
    """End-to-end EGER pipeline — composition boundary.

    Connects all components into one coherent flow:
    1. TaskDefinition → PromptBuilder → PromptRequest
    2. PromptRequest → ProposalGenerator → CandidateArtifact
    3. CandidateArtifact → OracleAdapter → OracleResult
    4. OracleResult → EvidenceNormalizer → EvidenceArtifact
    5. RevisionController orchestrates the loop
    6. VerificationGate makes final ACCEPT/REJECT
    7. ProvenanceTracker records everything

    INVARIANT: Composition ONLY — no independent decisions.
    """

    def __init__(
        self,
        proposal_generator: Any,
        oracle: Any,
        prompt_builder: Optional[PromptBuilder] = None,
        normalizer: Optional[EvidenceNormalizer] = None,
        verification_gate: Optional[VerificationGate] = None,
        provenance: Optional[ProvenanceTracker] = None,
    ):
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.normalizer = normalizer or EvidenceNormalizer()
        self.verification_gate = verification_gate or VerificationGate()
        self.provenance = provenance or ProvenanceTracker()
        self.proposal_generator = proposal_generator
        self.oracle = oracle
        self.revision_controller = RevisionController(
            prompt_builder=self.prompt_builder,
            proposal_generator=proposal_generator,
            oracle=oracle,
            normalizer=self.normalizer,
        )
        # Store actual artifacts for verification
        self._candidate_history: List[CandidateArtifact] = []
        self._evidence_history: List[EvidenceArtifact] = []

    def run(
        self,
        task: TaskDefinition,
        config: RevisionConfig,
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute the complete EGER pipeline.

        Args:
            task: Task definition
            config: Revision configuration
            run_id: Optional explicit run ID

        Returns:
            Dict containing run_record, verification_result, and provenance
        """
        if not run_id:
            run_id = f"EGER-PIPELINE-{_deterministic_hash(task.task_id)[:12].upper()}"

        # Reset artifact histories
        self._candidate_history = []
        self._evidence_history = []

        # --- Start provenance ---
        self.provenance.start_run(run_id, task.task_id)

        # --- Execute revision loop with artifact tracking ---
        run_record = self._run_with_tracking(task, config, run_id)

        # --- Get final candidate and evidence ---
        final_candidate = self._candidate_history[-1] if self._candidate_history else None
        final_evidence = self._evidence_history[-1] if self._evidence_history else None

        # --- VerificationGate — sole acceptance authority ---
        verification_result = self.verification_gate.evaluate(
            final_candidate, final_evidence
        )

        # --- Record verification ---
        self.provenance.record_verification(
            run_id,
            verification_result.decision,
            final_candidate.artifact_id if final_candidate else "",
            final_evidence.evidence_id if final_evidence else "",
        )

        # --- Complete provenance ---
        self.provenance.complete_run(
            run_id,
            status=run_record.status,
            terminal_reason=run_record.final_decision,
            final_candidate_id=run_record.final_candidate_id,
            final_evidence_id=run_record.final_evidence_id,
        )

        return {
            "run_id": run_id,
            "run_record": run_record,
            "verification_result": verification_result,
            "provenance": self.provenance.reconstruct_run(run_id),
        }

    def _run_with_tracking(
        self,
        task: TaskDefinition,
        config: RevisionConfig,
        run_id: str,
    ) -> RunRecord:
        """Execute revision loop while tracking actual artifacts."""
        import time
        from eger.revision.controller import _OracleFailure

        start_time = time.time()
        model_calls = 0
        oracle_calls = 0
        total_calls = 0
        iterations = []
        terminal_reason = ""

        try:
            for iteration in range(config.max_iterations):
                if total_calls >= config.max_total_calls:
                    terminal_reason = "BUDGET_EXHAUSTED"
                    break

                # Build prompt
                if iteration == 0:
                    prompt_request = self.prompt_builder.build(task, iteration=iteration)
                else:
                    prev_candidate = self._candidate_history[-1]
                    prev_evidence = self._evidence_history[-1]
                    prompt_request = self.prompt_builder.build(
                        task, candidate=prev_candidate, evidence=prev_evidence, iteration=iteration
                    )
                model_calls += 1
                total_calls += 1

                # Record provenance
                self.provenance.record_prompt(
                    run_id, prompt_request.prompt_hash, prompt_request.request_id, iteration, task.task_id
                )

                # Generate candidate
                try:
                    raw_output = self.proposal_generator.generate(prompt_request)
                except Exception as e:
                    terminal_reason = f"MODEL_FAILURE: {str(e)}"
                    break

                candidate = self._extract_candidate(raw_output, prompt_request)
                if candidate is None:
                    terminal_reason = "MALFORMED_OUTPUT"
                    break

                self._candidate_history.append(candidate)
                self.provenance.record_candidate(
                    run_id, candidate.artifact_id, candidate.candidate_hash, iteration, prompt_request.request_id
                )

                # Check oracle budget
                if total_calls >= config.max_total_calls:
                    terminal_reason = "BUDGET_EXHAUSTED"
                    break

                # Oracle evaluation
                try:
                    oracle_result = self.oracle.validate(candidate.sdc_text)
                except Exception as e:
                    terminal_reason = f"ORACLE_FAILURE: {str(e)}"
                    oracle_calls += 1
                    total_calls += 1
                    break

                oracle_calls += 1
                total_calls += 1
                self.provenance.record_oracle_evaluation(
                    run_id, f"ORA-{iteration}", candidate.candidate_hash, iteration
                )

                # Normalize evidence
                if not oracle_result.is_success:
                    failure_evidence = self.normalizer.normalize_failure(
                        oracle_result.failure, task.task_id, candidate_hash=candidate.candidate_hash
                    )
                    self._evidence_history.append(failure_evidence)
                    self.provenance.record_evidence(
                        run_id, failure_evidence.evidence_id, failure_evidence.evidence_hash, iteration
                    )
                    terminal_reason = f"ORACLE_FAILURE: {oracle_result.failure.kind}"
                    break

                evidence = self.normalizer.normalize(
                    oracle_result.evidence, task.task_id, candidate_hash=candidate.candidate_hash
                )
                self._evidence_history.append(evidence)
                self.provenance.record_evidence(
                    run_id, evidence.evidence_id, evidence.evidence_hash, iteration
                )

                iterations.append({
                    "iteration": iteration,
                    "prompt_hash": prompt_request.prompt_hash,
                    "candidate_id": candidate.artifact_id,
                    "evidence_id": evidence.evidence_id,
                    "oracle_status": evidence.oracle_status,
                    "error_count": evidence.summary.error_count,
                    "status": "COMPLETED",
                })

                if not evidence.has_errors:
                    terminal_reason = "NO_ERRORS"
                    break

            else:
                terminal_reason = "MAX_ITERATIONS"

        except Exception as e:
            terminal_reason = f"UNEXPECTED_ERROR: {str(e)}"

        duration = time.time() - start_time
        final_candidate_id = self._candidate_history[-1].artifact_id if self._candidate_history else None
        final_evidence_id = self._evidence_history[-1].evidence_id if self._evidence_history else None

        if terminal_reason.startswith(("MODEL_FAILURE", "MALFORMED_OUTPUT", "ORACLE_FAILURE", "UNEXPECTED_ERROR")):
            status = "INCOMPLETE"
        else:
            status = "REJECTED"

        return RunRecord(
            run_id=run_id, task_id=task.task_id, config=config,
            iterations=tuple(iterations), final_decision=terminal_reason,
            final_evidence_id=final_evidence_id, final_candidate_id=final_candidate_id,
            total_calls=total_calls, duration_seconds=duration, status=status,
            provenance={"controller": "EGERPipeline", "model_calls": model_calls, "oracle_calls": oracle_calls},
        )

    def _extract_candidate(self, raw_output: Any, prompt_request: PromptRequest) -> Optional[CandidateArtifact]:
        """Extract CandidateArtifact from raw model output."""
        if raw_output is None:
            return None
        if isinstance(raw_output, str):
            return build_candidate(raw_output, provision={"prompt_hash": prompt_request.prompt_hash})
        if hasattr(raw_output, "text"):
            return build_candidate(raw_output.text, provision={"prompt_hash": prompt_request.prompt_hash})
        if isinstance(raw_output, dict):
            text = raw_output.get("text") or raw_output.get("output") or ""
            if text:
                return build_candidate(text, provision={"prompt_hash": prompt_request.prompt_hash})
        return None
