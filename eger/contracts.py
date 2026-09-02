"""EGER Contracts — shared size limits and validation constants.

P155: Input validation and resource-boundary hardening.

These constants define explicit, deterministic, documented bounds for
externally reachable engineering interfaces. They prevent resource
exhaustion without imposing semantic restrictions on valid SDC content.

INVARIANT: All limits are explicit and documented.
INVARIANT: Same inputs → same validation behavior (deterministic).
INVARIANT: Validation fails before expensive operations (Oracle, LLM).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# TaskDefinition limits
# ---------------------------------------------------------------------------

MAX_TASK_ID_LENGTH = 1_000
MAX_DESIGN_CONTEXT_LENGTH = 50_000
MAX_OBJECTIVE_LENGTH = 50_000
MAX_INITIAL_SDC_LENGTH = 100_000
MAX_CONSTRAINTS_COUNT = 100
MAX_CONSTRAINT_LENGTH = 5_000

# ---------------------------------------------------------------------------
# CandidateArtifact limits
# ---------------------------------------------------------------------------

MAX_SDC_TEXT_LENGTH = 100_000
MAX_ARTIFACT_ID_LENGTH = 1_000
MAX_PROVISION_DEPTH = 10  # max nesting depth for provision dict

# ---------------------------------------------------------------------------
# Evidence limits
# ---------------------------------------------------------------------------

MAX_FINDINGS_COUNT = 1_000
MAX_FINDING_MESSAGE_LENGTH = 10_000
MAX_FINDING_ID_LENGTH = 1_000
MAX_EVIDENCE_ID_LENGTH = 1_000

# ---------------------------------------------------------------------------
# RevisionConfig limits (max bounds)
# ---------------------------------------------------------------------------

MAX_MAX_ITERATIONS = 100
MAX_MAX_TOTAL_CALLS = 500
MAX_TEMPERATURE = 2.0
MAX_MAX_TOKENS = 128_000

# ---------------------------------------------------------------------------
# RunRecord limits
# ---------------------------------------------------------------------------

MAX_RUN_ID_LENGTH = 1_000
MAX_ITERATIONS_HISTORY = 1_000  # max recorded iteration dicts
