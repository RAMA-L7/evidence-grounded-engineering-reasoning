"""PromptRequest — typed, deterministic prompt metadata.

EMPIRICALLY SUPPORTED: prompt construction (framing signal).

This contract records the metadata of each prompt sent to the LLM.
The actual prompt text is not stored here — only hashes and references.

INVARIANT: prompt_hash is deterministic.
INVARIANT: objective_hash is deterministic.
INVARIANT: all fields are immutable (frozen=True).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
import hashlib

SCHEMA_PROMPT = "eger.prompt.v1"


def _deterministic_hash(text: str) -> str:
    """SHA256 hash — deterministic."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PromptRequest:
    """Prompt metadata — immutable once created.

    PRODUCER: PromptBuilder (deterministic)
    CONSUMER: ProposalGenerator
    """
    request_id: str
    task_id: str
    prompt_hash: str
    objective_hash: str
    iteration: int
    evidence_id: Optional[str] = None
    schema_version: str = SCHEMA_PROMPT

    def __post_init__(self):
        if not self.request_id:
            raise ValueError("request_id must be non-empty")
        if not self.task_id:
            raise ValueError("task_id must be non-empty")
        if not self.prompt_hash:
            raise ValueError("prompt_hash must be non-empty")
        if self.iteration < 0:
            raise ValueError("iteration must be >= 0")

    @staticmethod
    def hash_prompt(prompt_text: str) -> str:
        """Deterministic prompt hash."""
        return _deterministic_hash(prompt_text)

    @staticmethod
    def hash_objective(objective: str) -> str:
        """Deterministic objective hash."""
        return _deterministic_hash(objective)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "task_id": self.task_id,
            "prompt_hash": self.prompt_hash,
            "objective_hash": self.objective_hash,
            "iteration": self.iteration,
            "evidence_id": self.evidence_id,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> PromptRequest:
        return cls(
            request_id=d["request_id"],
            task_id=d["task_id"],
            prompt_hash=d["prompt_hash"],
            objective_hash=d["objective_hash"],
            iteration=d["iteration"],
            evidence_id=d.get("evidence_id"),
            schema_version=d.get("schema_version", SCHEMA_PROMPT),
        )
