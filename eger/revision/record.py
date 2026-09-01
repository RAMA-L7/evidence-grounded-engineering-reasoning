"""RunRecord — typed, deterministic run metadata.

EMPIRICALLY SUPPORTED: revision loop behavior (C1).

This contract records the complete provenance chain for a single
revision loop execution. It is the authoritative record of what happened.

INVARIANT: status must be one of: ACCEPTED, REJECTED, INCOMPLETE
INVARIANT: total_calls must be >= 0
INVARIANT: duration_seconds must be >= 0
INVARIANT: all fields are immutable (frozen=True)

PRODUCER: RevisionController
CONSUMER: External system, audit
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

SCHEMA_RUN = "eger.run.v1"
SCHEMA_CONFIG = "eger.config.v1"

VALID_STATUSES = {"ACCEPTED", "REJECTED", "INCOMPLETE"}


@dataclass(frozen=True)
class RevisionConfig:
    """Configuration for revision loop — immutable.

    INVARIANT: max_iterations must be >= 1
    INVARIANT: max_total_calls must be >= 3 (at least 1 cycle)
    INVARIANT: timeout_seconds must be >= 1
    """
    max_iterations: int = 5
    max_total_calls: int = 15
    timeout_seconds: int = 60
    temperature: float = 0.0
    max_tokens: int = 2048
    schema_version: str = SCHEMA_CONFIG

    def __post_init__(self):
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")
        if self.max_total_calls < 3:
            raise ValueError("max_total_calls must be >= 3")
        if self.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be >= 1")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "max_iterations": self.max_iterations,
            "max_total_calls": self.max_total_calls,
            "timeout_seconds": self.timeout_seconds,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> RevisionConfig:
        return cls(
            max_iterations=d.get("max_iterations", 5),
            max_total_calls=d.get("max_total_calls", 15),
            timeout_seconds=d.get("timeout_seconds", 60),
            temperature=d.get("temperature", 0.0),
            max_tokens=d.get("max_tokens", 2048),
            schema_version=d.get("schema_version", SCHEMA_CONFIG),
        )


@dataclass(frozen=True)
class RunRecord:
    """Complete run record — immutable once created.

    INVARIANT: status must be ACCEPTED, REJECTED, or INCOMPLETE.
    INVARIANT: total_calls must be >= 0.
    INVARIANT: duration_seconds must be >= 0.
    INVARIANT: The LLM cannot produce this — only the RevisionController can.
    """
    run_id: str
    task_id: str
    config: RevisionConfig
    iterations: tuple  # Tuple[Dict[str, Any], ...] — immutable
    final_decision: str
    final_evidence_id: Optional[str]
    final_candidate_id: Optional[str]
    total_calls: int
    duration_seconds: float
    status: str
    provenance: Dict[str, Any]
    schema_version: str = SCHEMA_RUN

    def __post_init__(self):
        if self.status not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}, got '{self.status}'")
        if self.total_calls < 0:
            raise ValueError("total_calls must be >= 0")
        if self.duration_seconds < 0:
            raise ValueError("duration_seconds must be >= 0")

    @property
    def is_accepted(self) -> bool:
        return self.status == "ACCEPTED"

    @property
    def is_rejected(self) -> bool:
        return self.status == "REJECTED"

    @property
    def is_incomplete(self) -> bool:
        return self.status == "INCOMPLETE"

    @property
    def iteration_count(self) -> int:
        return len(self.iterations)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "task_id": self.task_id,
            "config": self.config.to_dict(),
            "iterations": list(self.iterations),
            "final_decision": self.final_decision,
            "final_evidence_id": self.final_evidence_id,
            "final_candidate_id": self.final_candidate_id,
            "total_calls": self.total_calls,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> RunRecord:
        config_data = d.get("config", {})
        config = RevisionConfig.from_dict(config_data) if config_data else RevisionConfig()
        return cls(
            run_id=d["run_id"],
            task_id=d["task_id"],
            config=config,
            iterations=tuple(d.get("iterations", [])),
            final_decision=d["final_decision"],
            final_evidence_id=d.get("final_evidence_id"),
            final_candidate_id=d.get("final_candidate_id"),
            total_calls=d.get("total_calls", 0),
            duration_seconds=d.get("duration_seconds", 0.0),
            status=d["status"],
            provenance=dict(d.get("provenance", {})),
            schema_version=d.get("schema_version", SCHEMA_RUN),
        )
