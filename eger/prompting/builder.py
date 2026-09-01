"""PromptBuilder — deterministic prompt construction.

EMPIRICALLY SUPPORTED: broad framing signal (A1 = 24/24 = 100%).

This module constructs deterministic prompts from TaskDefinition,
CandidateArtifact, and EvidenceArtifact. It is a PRESENTATION LAYER
that does NOT interpret evidence, make authorization decisions, or
modify any artifacts.

INVARIANT: Same inputs → same prompt text, always.
INVARIANT: PromptBuilder cannot mutate TaskDefinition, CandidateArtifact, or EvidenceArtifact.
INVARIANT: PromptBuilder cannot create ACCEPT/REJECT decisions.
INVARIANT: Candidate/evidence text is treated as DATA, not instructions.

PRODUCER: PromptBuilder (deterministic)
CONSUMER: ProposalGenerator (LLM)
"""

from __future__ import annotations

from typing import Optional
import hashlib

from eger.task.definition import TaskDefinition
from eger.evidence.schemas import EvidenceArtifact, Finding
from eger.engineer.candidate import CandidateArtifact
from .request import PromptRequest


def _deterministic_hash(text: str) -> str:
    """SHA256 hash — deterministic."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Severity ordering for deterministic display
# ---------------------------------------------------------------------------

_SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


def _sort_findings(findings):
    """Deterministic sort: severity (error→warning→info) → finding_id."""
    return sorted(findings, key=lambda f: (_SEVERITY_ORDER.get(f.severity, 99), f.finding_id))


# ---------------------------------------------------------------------------
# PromptBuilder
# ---------------------------------------------------------------------------

class PromptBuilder:
    """Deterministic prompt construction from TaskDefinition.

    Supports two modes:
    1. Initial proposal: TaskDefinition → prompt
    2. Revision: TaskDefinition + CandidateArtifact + EvidenceArtifact → prompt

    INVARIANT: Same inputs → same prompt text, always.
    INVARIANT: Cannot mutate input artifacts.
    """

    def build(
        self,
        task: TaskDefinition,
        *,
        candidate: Optional[CandidateArtifact] = None,
        evidence: Optional[EvidenceArtifact] = None,
        iteration: int = 0,
        request_id: Optional[str] = None,
    ) -> PromptRequest:
        """Build a PromptRequest from task and optional revision context.

        Args:
            task: Task definition with broad framing
            candidate: Previous candidate SDC (for revision mode)
            evidence: Oracle evidence (for revision mode)
            iteration: Current revision iteration (0 = initial)
            request_id: Optional explicit request ID

        Returns:
            PromptRequest with deterministic prompt hash
        """
        # Build prompt text deterministically
        prompt_text = self._build_prompt_text(task, candidate, evidence)

        # Compute deterministic hashes
        prompt_hash = PromptRequest.hash_prompt(prompt_text)
        objective_hash = task.objective_hash

        # Generate request ID
        if not request_id:
            request_id = f"EGER-PR-{prompt_hash[:12].upper()}"

        # Determine evidence ID
        evidence_id = evidence.evidence_id if evidence else None

        return PromptRequest(
            request_id=request_id,
            task_id=task.task_id,
            prompt_hash=prompt_hash,
            objective_hash=objective_hash,
            iteration=iteration,
            evidence_id=evidence_id,
        )

    def build_prompt_text(
        self,
        task: TaskDefinition,
        *,
        candidate: Optional[CandidateArtifact] = None,
        evidence: Optional[EvidenceArtifact] = None,
    ) -> str:
        """Build the actual prompt text (for inspection/debugging).

        This is a deterministic rendering of the prompt structure.
        """
        return self._build_prompt_text(task, candidate, evidence)

    def _build_prompt_text(
        self,
        task: TaskDefinition,
        candidate: Optional[CandidateArtifact],
        evidence: Optional[EvidenceArtifact],
    ) -> str:
        """Internal deterministic prompt construction."""
        sections = []

        # --- TASK section ---
        sections.append("TASK")
        sections.append("────")
        sections.append(f"Task ID: {task.task_id}")
        sections.append("")
        sections.append("Design Context:")
        sections.append(task.design_context)
        sections.append("")
        sections.append("Objective:")
        sections.append(task.objective)
        sections.append("")

        # --- CONSTRAINTS section ---
        if task.constraints:
            sections.append("Constraints:")
            for c in task.constraints:
                sections.append(f"  - {c}")
            sections.append("")

        # --- CURRENT CANDIDATE section (revision mode) ---
        if candidate is not None:
            sections.append("CURRENT CANDIDATE")
            sections.append("─────────────────")
            sections.append(f"Candidate ID: {candidate.artifact_id}")
            sections.append("")
            sections.append("Current SDC:")
            sections.append(candidate.sdc_text)
            sections.append("")

        # --- EVIDENCE section (revision mode) ---
        if evidence is not None:
            sections.append("EVIDENCE")
            sections.append("────────")
            sections.append(f"Evidence ID: {evidence.evidence_id}")
            sections.append(f"Oracle Status: {evidence.oracle_status}")
            sections.append(f"Evidence Scope: {evidence.evidence_scope}")
            sections.append("")

            # Summary
            sections.append("Summary:")
            sections.append(f"  Errors: {evidence.summary.error_count}")
            sections.append(f"  Warnings: {evidence.summary.warning_count}")
            sections.append(f"  Info: {evidence.summary.info_count}")
            sections.append("")

            # Findings (sorted deterministically)
            sorted_findings = _sort_findings(evidence.findings)
            if sorted_findings:
                sections.append("Findings:")
                for f in sorted_findings:
                    sev = f.severity.upper()
                    sections.append(f"  [{sev}] {f.category}: {f.message}")
                    if f.entity:
                        sections.append(f"    Entity: {f.entity}")
                    if f.expected_state:
                        sections.append(f"    Expected: {f.expected_state}")
                    if f.observed_state:
                        sections.append(f"    Observed: {f.observed_state}")
                    if f.remediation_hint:
                        sections.append(f"    Hint: {f.remediation_hint}")
                sections.append("")

        # --- INSTRUCTION section ---
        sections.append("INSTRUCTION")
        sections.append("───────────")
        if candidate is not None and evidence is not None:
            # Revision mode
            if evidence.has_errors:
                sections.append(
                    "Revise the SDC to address the evidence findings above. "
                    "Preserve valid existing constraints and fix all ERROR findings."
                )
            else:
                sections.append(
                    "The current SDC has no ERROR findings. "
                    "Return the current SDC as-is if it is correct."
                )
        else:
            # Initial proposal mode
            sections.append(
                "Generate the complete SDC for this design."
            )
        sections.append("")
        sections.append("Return only the SDC content, no explanation.")

        return "\n".join(sections)
