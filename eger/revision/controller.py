"""RevisionController — deterministic orchestration of the revision loop.

EMPIRICALLY SUPPORTED: revision loop behavior (C1).

This module orchestrates the generate→verify→revise cycle. It coordinates
PromptBuilder, ProposalGenerator, OracleAdapter, and EvidenceNormalizer
while enforcing budget constraints and failure policies.

INVARIANT: RevisionController is orchestration authority ONLY.
INVARIANT: Cannot invent evidence, modify Oracle findings, or decide ACCEPT/REJECT.
INVARIANT: Cannot mutate TaskDefinition, CandidateArtifact, or EvidenceArtifact.
INVARIANT: Budget enforcement is deterministic and fail-closed.

PRODUCER: RevisionController
CONSUMER: RunRecord (authoritative record)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol, Optional, Any, List, Dict
import hashlib
import time

from eger.task.definition import TaskDefinition
from eger.evidence.schemas import EvidenceArtifact
from eger.engineer.candidate import CandidateArtifact, build_candidate
from eger.prompting.builder import PromptBuilder
from eger.prompting.request import PromptRequest
from eger.evidence.normalizer import EvidenceNormalizer
from .record import RunRecord, RevisionConfig


# ---------------------------------------------------------------------------
# Protocols (interfaces for external components)
# ---------------------------------------------------------------------------

class ProposalGenerator(Protocol):
    """Interface for LLM proposal generation."""

    def generate(self, prompt: PromptRequest) -> Any:
        """Generate a proposal from a prompt. Returns raw model output."""
        ...


class OracleAdapter(Protocol):
    """Interface for Oracle evaluation."""

    def validate(self, sdc_text: str, **kwargs: Any) -> Any:
        """Validate SDC text. Returns OracleResult."""
        ...


# ---------------------------------------------------------------------------
# RevisionController
# ---------------------------------------------------------------------------

class RevisionController:
    """Deterministic orchestration of the revision loop.

    Coordinates:
    1. PromptBuilder → PromptRequest
    2. ProposalGenerator → raw model output
    3. CandidateArtifact extraction
    4. OracleAdapter → OracleResult
    5. EvidenceNormalizer → EvidenceArtifact
    6. Budget enforcement
    7. RunRecord creation

    INVARIANT: Orchestration authority ONLY.
    INVARIANT: Cannot decide ACCEPT/REJECT.
    """

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        proposal_generator: ProposalGenerator,
        oracle: OracleAdapter,
        normalizer: EvidenceNormalizer,
    ):
        self.prompt_builder = prompt_builder
        self.proposal_generator = proposal_generator
        self.oracle = oracle
        self.normalizer = normalizer

    def run(
        self,
        task: TaskDefinition,
        config: RevisionConfig,
        run_id: Optional[str] = None,
    ) -> RunRecord:
        """Execute the revision loop.

        Args:
            task: Task definition
            config: Revision configuration (budgets, limits)
            run_id: Optional explicit run ID

        Returns:
            RunRecord with complete provenance
        """
        start_time = time.time()
        if not run_id:
            run_id = f"EGER-RUN-{hashlib.sha256(task.task_id.encode()).hexdigest()[:12].upper()}"

        # Budget tracking
        model_calls = 0
        oracle_calls = 0
        total_calls = 0

        # History
        iterations: List[Dict[str, Any]] = []
        candidate_history: List[CandidateArtifact] = []
        evidence_history: List[EvidenceArtifact] = []

        # Terminal state
        terminal_reason = ""
        final_candidate_id = None
        final_evidence_id = None

        try:
            for iteration in range(config.max_iterations):
                # --- Check budget before iteration ---
                if total_calls >= config.max_total_calls:
                    terminal_reason = "BUDGET_EXHAUSTED"
                    break

                # --- Step 1: Build prompt ---
                if iteration == 0:
                    # Initial proposal
                    prompt_request = self.prompt_builder.build(
                        task, iteration=iteration
                    )
                else:
                    # Revision — need previous candidate and evidence
                    prev_candidate = candidate_history[-1]
                    prev_evidence = evidence_history[-1]
                    prompt_request = self.prompt_builder.build(
                        task,
                        candidate=prev_candidate,
                        evidence=prev_evidence,
                        iteration=iteration,
                    )
                model_calls += 1
                total_calls += 1

                # --- Step 2: Generate candidate ---
                try:
                    raw_output = self.proposal_generator.generate(prompt_request)
                except Exception as e:
                    terminal_reason = f"MODEL_FAILURE: {str(e)}"
                    # Record iteration
                    iterations.append({
                        "iteration": iteration,
                        "prompt_hash": prompt_request.prompt_hash,
                        "status": "MODEL_FAILURE",
                        "error": str(e),
                    })
                    break

                # --- Step 3: Extract candidate ---
                candidate = self._extract_candidate(raw_output, task, prompt_request)
                if candidate is None:
                    terminal_reason = "MALFORMED_OUTPUT"
                    iterations.append({
                        "iteration": iteration,
                        "prompt_hash": prompt_request.prompt_hash,
                        "status": "MALFORMED_OUTPUT",
                    })
                    break

                candidate_history.append(candidate)
                final_candidate_id = candidate.artifact_id

                # --- Step 4: Check Oracle budget ---
                if total_calls >= config.max_total_calls:
                    terminal_reason = "BUDGET_EXHAUSTED"
                    iterations.append({
                        "iteration": iteration,
                        "prompt_hash": prompt_request.prompt_hash,
                        "candidate_id": candidate.artifact_id,
                        "status": "BUDGET_EXHAUSTED_BEFORE_ORACLE",
                    })
                    break

                # --- Step 5: Evaluate with Oracle ---
                try:
                    oracle_result = self.oracle.validate(candidate.sdc_text)
                except Exception as e:
                    terminal_reason = f"ORACLE_FAILURE: {str(e)}"
                    # Create failure evidence
                    oracle_calls += 1
                    total_calls += 1
                    failure_evidence = self.normalizer.normalize_failure(
                        _OracleFailure("EXCEPTION", -1, str(e)),
                        task.task_id,
                        candidate_hash=candidate.candidate_hash,
                    )
                    evidence_history.append(failure_evidence)
                    final_evidence_id = failure_evidence.evidence_id
                    iterations.append({
                        "iteration": iteration,
                        "prompt_hash": prompt_request.prompt_hash,
                        "candidate_id": candidate.artifact_id,
                        "evidence_id": failure_evidence.evidence_id,
                        "status": "ORACLE_EXCEPTION",
                        "error": str(e),
                    })
                    break

                oracle_calls += 1
                total_calls += 1

                # --- Step 6: Normalize evidence ---
                if not oracle_result.is_success:
                    # Oracle failure
                    failure_evidence = self.normalizer.normalize_failure(
                        oracle_result.failure,
                        task.task_id,
                        candidate_hash=candidate.candidate_hash,
                    )
                    evidence_history.append(failure_evidence)
                    final_evidence_id = failure_evidence.evidence_id
                    terminal_reason = f"ORACLE_FAILURE: {oracle_result.failure.kind}"
                    iterations.append({
                        "iteration": iteration,
                        "prompt_hash": prompt_request.prompt_hash,
                        "candidate_id": candidate.artifact_id,
                        "evidence_id": failure_evidence.evidence_id,
                        "status": "ORACLE_FAILURE",
                    })
                    break

                # Oracle success — normalize evidence
                evidence = self.normalizer.normalize(
                    oracle_result.evidence,
                    task.task_id,
                    candidate_hash=candidate.candidate_hash,
                )
                evidence_history.append(evidence)
                final_evidence_id = evidence.evidence_id

                # --- Step 7: Record iteration ---
                iterations.append({
                    "iteration": iteration,
                    "prompt_hash": prompt_request.prompt_hash,
                    "candidate_id": candidate.artifact_id,
                    "evidence_id": evidence.evidence_id,
                    "oracle_status": evidence.oracle_status,
                    "error_count": evidence.summary.error_count,
                    "warning_count": evidence.summary.warning_count,
                    "status": "COMPLETED",
                })

                # --- Step 8: Check if no errors (natural termination) ---
                if not evidence.has_errors:
                    terminal_reason = "NO_ERRORS"
                    break

                # Continue to next iteration

            else:
                # Exhausted iterations without terminal condition
                terminal_reason = "MAX_ITERATIONS"

        except Exception as e:
            terminal_reason = f"UNEXPECTED_ERROR: {str(e)}"

        # --- Build RunRecord ---
        duration = time.time() - start_time

        # Determine status from terminal reason
        if terminal_reason.startswith("MODEL_FAILURE") or \
           terminal_reason.startswith("MALFORMED_OUTPUT") or \
           terminal_reason.startswith("ORACLE_FAILURE") or \
           terminal_reason.startswith("UNEXPECTED_ERROR"):
            status = "INCOMPLETE"
        elif terminal_reason in ("NO_ERRORS", "BUDGET_EXHAUSTED", "MAX_ITERATIONS"):
            # These are terminal states — controller does NOT decide ACCEPT/REJECT
            # It records the state for P142 to decide
            status = "REJECTED"  # Default — P142 will make the actual decision
        else:
            status = "INCOMPLETE"

        provenance = {
            "controller": "RevisionController",
            "controller_version": "1.0.0",
            "model_calls": model_calls,
            "oracle_calls": oracle_calls,
            "terminal_reason": terminal_reason,
            "iteration_count": len(iterations),
        }

        return RunRecord(
            run_id=run_id,
            task_id=task.task_id,
            config=config,
            iterations=tuple(iterations),
            final_decision=terminal_reason,
            final_evidence_id=final_evidence_id,
            final_candidate_id=final_candidate_id,
            total_calls=total_calls,
            duration_seconds=duration,
            status=status,
            provenance=provenance,
        )

    def _extract_candidate(
        self,
        raw_output: Any,
        task: TaskDefinition,
        prompt_request: PromptRequest,
    ) -> Optional[CandidateArtifact]:
        """Extract CandidateArtifact from raw model output."""
        if raw_output is None:
            return None

        # Handle string output
        if isinstance(raw_output, str):
            return build_candidate(
                raw_output,
                provision={"prompt_hash": prompt_request.prompt_hash},
            )

        # Handle ModelResponse-like objects
        if hasattr(raw_output, "text"):
            return build_candidate(
                raw_output.text,
                provision={"prompt_hash": prompt_request.prompt_hash},
            )

        # Handle dict-like objects
        if isinstance(raw_output, dict):
            text = raw_output.get("text") or raw_output.get("output") or ""
            if text:
                return build_candidate(
                    text,
                    provision={"prompt_hash": prompt_request.prompt_hash},
                )

        return None


# ---------------------------------------------------------------------------
# Internal helper for Oracle failure
# ---------------------------------------------------------------------------

@dataclass
class _OracleFailure:
    """Internal Oracle failure representation."""
    kind: str
    exit_code: int
    message: str
    raw_ref: Optional[Dict[str, str]] = None
