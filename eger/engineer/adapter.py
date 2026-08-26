"""EngineerAdapter — proposal authority integration (P010).

Separates model invocation from EGER scientific protocol.
The adapter is responsible for prompt construction, model invocation,
response capture, candidate extraction, and model metadata.

It is NOT responsible for validation, evidence interpretation,
epistemic transitions, or authorization.

Exactly one probabilistic component exists (EGER-DEC-005).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from .model import EngineerModel, ModelResponse
from .candidate import CandidateArtifact, extract_candidate, build_candidate, SCHEMA_CANDIDATE

PROMPT_VERSION = "eger.prompt.v1"
SYSTEM_INSTRUCTIONS = (
    "You are an SDC generation assistant. Given the engineering context, "
    "produce a candidate SDC. Output SDC inside a ```sdc code block. "
    "Do not claim the candidate is validated."
)


@dataclass
class ProposalFailure:
    """Typed proposal failure — distinct from evidence/engineering failures."""
    kind: str  # MODEL_UNAVAILABLE | TIMEOUT | PROVIDER_ERROR | MALFORMED_OUTPUT | MISSING_CANDIDATE
    message: str
    prompt_hash: str = ""
    raw_output_hash: str = ""


@dataclass
class ProposalResult:
    """Union: Success(CandidateArtifact + ModelResponse) | Failure(ProposalFailure)."""
    is_success: bool
    candidate: Optional[CandidateArtifact] = None
    model_response: Optional[ModelResponse] = None
    failure: Optional[ProposalFailure] = None


class EngineerAdapter:
    """Proposal authority only. No evidence/epistemic/authorization capability."""

    def __init__(self, model: EngineerModel):
        self.model = model

    def capabilities(self) -> Dict[str, Any]:
        return {
            "role": "proposal",
            "model": self.model.describe(),
            "prompt_version": PROMPT_VERSION,
            "schema_version": SCHEMA_CANDIDATE,
            "authorities": ["proposal"],
            "forbidden_authorities": ["evidence", "epistemic", "authorization"],
        }

    def build_prompt(
        self,
        design_context: str = "",
        existing_sdc: str = "",
        objective: str = "",
        evidence_summary: Optional[str] = None,
        epistemic_state: Optional[str] = None,
    ) -> tuple[str, str]:
        """Build prompt deterministically. Returns (prompt, prompt_hash).

        Input context is minimal per P010 §14 — no research ledger dumps.
        Evidence/epistemic info is read-only context when provided.
        """
        parts = [SYSTEM_INSTRUCTIONS]
        if design_context:
            parts.append(f"Design context:\n{design_context}")
        if existing_sdc:
            parts.append(f"Existing SDC:\n{existing_sdc}")
        if objective:
            parts.append(f"Objective:\n{objective}")
        if evidence_summary:
            parts.append(f"Deterministic evidence (read-only, not authoritative):\n{evidence_summary}")
        if epistemic_state:
            parts.append(f"Epistemic state (read-only):\n{epistemic_state}")
        prompt = "\n\n".join(parts)
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        return prompt, prompt_hash

    def propose(
        self,
        design_context: str = "",
        existing_sdc: str = "",
        objective: str = "",
        evidence_summary: Optional[str] = None,
        epistemic_state: Optional[str] = None,
    ) -> ProposalResult:
        """Full proposal cycle: prompt -> model -> extraction -> typed candidate.

        No validation, no epistemic transition, no authorization inside this method.
        """
        prompt, prompt_hash = self.build_prompt(
            design_context=design_context,
            existing_sdc=existing_sdc,
            objective=objective,
            evidence_summary=evidence_summary,
            epistemic_state=epistemic_state,
        )
        try:
            response: ModelResponse = self.model.generate(prompt, prompt_version=PROMPT_VERSION)
        except TimeoutError as e:
            return ProposalResult(
                is_success=False,
                failure=ProposalFailure(kind="TIMEOUT", message=str(e), prompt_hash=prompt_hash),
            )
        except RuntimeError as e:
            return ProposalResult(
                is_success=False,
                failure=ProposalFailure(kind="PROVIDER_ERROR", message=str(e), prompt_hash=prompt_hash),
            )
        except Exception as e:
            return ProposalResult(
                is_success=False,
                failure=ProposalFailure(kind="MODEL_UNAVAILABLE", message=str(e), prompt_hash=prompt_hash),
            )

        # Hash separation: prompt/input hash vs output hash vs candidate hash are distinct
        if not response.prompt_hash:
            response.prompt_hash = prompt_hash
        if not response.prompt_version:
            response.prompt_version = PROMPT_VERSION
        # Ensure output_hash computed
        raw_hash = hashlib.sha256(response.raw_output.encode("utf-8")).hexdigest()
        response.output_hash = response.output_hash or raw_hash

        provision = {
            "provider": response.provider,
            "model": response.model,
            "model_version": response.model_version,
            "sampling_params": response.sampling_params,
            "request_id": response.request_id,
            "prompt_hash": prompt_hash,
            "prompt_version": PROMPT_VERSION,
            "output_hash": response.output_hash,
            "produced_at": response.produced_at,
        }

        candidate = extract_candidate(response.raw_output, provision=provision)
        if candidate is None:
            return ProposalResult(
                is_success=False,
                model_response=response,
                failure=ProposalFailure(
                    kind="MALFORMED_OUTPUT",
                    message="model output contained no extractable SDC",
                    prompt_hash=prompt_hash,
                    raw_output_hash=raw_hash,
                ),
            )
        # Candidate is typed and explicitly unverified
        return ProposalResult(is_success=True, candidate=candidate, model_response=response)

    # ------------------------------------------------------------------
    # Explicitly forbidden operations — no evidence/epistemic/authorization
    # ------------------------------------------------------------------

    def _forbidden(self, name: str):
        raise AttributeError(f"EngineerAdapter has no '{name}' — proposal authority only")

    # These would violate P7 if they existed; we ensure they don't.
