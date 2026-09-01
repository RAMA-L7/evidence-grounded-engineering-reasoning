"""TaskDefinition — typed, deterministic task specification.

EMPIRICALLY SUPPORTED: broad framing signal (A1 = 24/24 = 100%).

The task definition uses broader, production-quality framing rather than
narrow, specific constraints. This is the default because DIAGNOSTIC-009
showed that broader framing achieved 100% adherence vs 67% for narrow framing.

Caveat: This is a strong behavioral signal, not proven causality.
The effect may be model-specific (MODEL-005 only).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import hashlib
import json

SCHEMA_TASK = "eger.task.v1"


def _deterministic_hash(text: str) -> str:
    """SHA256 hash — deterministic."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TaskDefinition:
    """Typed task definition — read-only configuration.

    INVARIANT: task_id must be non-empty.
    INVARIANT: design_context must be non-empty.
    INVARIANT: objective must use broad/production-quality framing.
    INVARIANT: initial_sdc must be non-empty.
    INVARIANT: constraints must be a non-empty collection.
    INVARIANT: all fields are immutable (frozen=True).
    """
    task_id: str
    design_context: str
    objective: str
    initial_sdc: str
    constraints: List[str]
    schema_version: str = SCHEMA_TASK

    def __post_init__(self):
        """Validate invariants at construction time."""
        if not self.task_id:
            raise ValueError("task_id must be non-empty")
        if not self.design_context:
            raise ValueError("design_context must be non-empty")
        if not self.objective:
            raise ValueError("objective must be non-empty")
        if not self.initial_sdc:
            raise ValueError("initial_sdc must be non-empty")
        if not self.constraints:
            raise ValueError("constraints must be non-empty")

    @property
    def task_hash(self) -> str:
        """Deterministic hash of task definition."""
        data = {
            "task_id": self.task_id,
            "design_context": self.design_context,
            "objective": self.objective,
            "initial_sdc": self.initial_sdc,
            "constraints": sorted(self.constraints),
        }
        return _deterministic_hash(json.dumps(data, sort_keys=True))

    @property
    def sdc_hash(self) -> str:
        """Deterministic hash of initial SDC."""
        return _deterministic_hash(self.initial_sdc)

    @property
    def objective_hash(self) -> str:
        """Deterministic hash of objective."""
        return _deterministic_hash(self.objective)

    def to_dict(self) -> Dict[str, Any]:
        """Deterministic serialization."""
        return {
            "schema_version": self.schema_version,
            "task_id": self.task_id,
            "design_context": self.design_context,
            "objective": self.objective,
            "initial_sdc": self.initial_sdc,
            "constraints": list(self.constraints),
            "task_hash": self.task_hash,
            "sdc_hash": self.sdc_hash,
            "objective_hash": self.objective_hash,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> TaskDefinition:
        """Deserialize from dict."""
        return cls(
            task_id=d["task_id"],
            design_context=d["design_context"],
            objective=d["objective"],
            initial_sdc=d["initial_sdc"],
            constraints=list(d["constraints"]),
            schema_version=d.get("schema_version", SCHEMA_TASK),
        )
