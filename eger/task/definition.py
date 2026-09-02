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

# P155: Size limits for input validation
from eger.contracts import (
    MAX_TASK_ID_LENGTH,
    MAX_DESIGN_CONTEXT_LENGTH,
    MAX_OBJECTIVE_LENGTH,
    MAX_INITIAL_SDC_LENGTH,
    MAX_CONSTRAINTS_COUNT,
    MAX_CONSTRAINT_LENGTH,
)


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
        # P155: Size limits
        if len(self.task_id) > MAX_TASK_ID_LENGTH:
            raise ValueError(
                f"task_id length ({len(self.task_id)}) exceeds maximum ({MAX_TASK_ID_LENGTH})"
            )
        if len(self.design_context) > MAX_DESIGN_CONTEXT_LENGTH:
            raise ValueError(
                f"design_context length ({len(self.design_context)}) exceeds maximum ({MAX_DESIGN_CONTEXT_LENGTH})"
            )
        if len(self.objective) > MAX_OBJECTIVE_LENGTH:
            raise ValueError(
                f"objective length ({len(self.objective)}) exceeds maximum ({MAX_OBJECTIVE_LENGTH})"
            )
        if len(self.initial_sdc) > MAX_INITIAL_SDC_LENGTH:
            raise ValueError(
                f"initial_sdc length ({len(self.initial_sdc)}) exceeds maximum ({MAX_INITIAL_SDC_LENGTH})"
            )
        if len(self.constraints) > MAX_CONSTRAINTS_COUNT:
            raise ValueError(
                f"constraints count ({len(self.constraints)}) exceeds maximum ({MAX_CONSTRAINTS_COUNT})"
            )
        for i, c in enumerate(self.constraints):
            if len(c) > MAX_CONSTRAINT_LENGTH:
                raise ValueError(
                    f"constraint[{i}] length ({len(c)}) exceeds maximum ({MAX_CONSTRAINT_LENGTH})"
                )

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
