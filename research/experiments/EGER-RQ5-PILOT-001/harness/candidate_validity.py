"""Deterministic candidate-validity gate (P172 §5).

Classifies raw model output into exactly one of:
    VALID_SDC       → eligible for Oracle evaluation
    NON_SDC_OUTPUT  → conversational/prose output, rejected before Oracle
    EMPTY_OUTPUT    → empty output, rejected before Oracle
    PROVIDER_FAILURE → model/provider error, rejected before Oracle

The gate is deliberately syntactic, not semantic: it only distinguishes
"plausibly an SDC document" from "not an SDC document". Semantic validation
is the Oracle's job. It is deterministic — no LLM, no manual judgment.

Rules (P172 §5, minimum objective validity criterion):
1. Non-empty after stripping markdown code fences.
2. No conversational wrapper (greetings / questions / prose filler).
3. Contains at least one valid SDC command line (known SDC keyword).
4. Contains the task-required construct (create_clock for T1/T2) —
   this is the primary defense against the OpenSTA vacuous-pass path.
5. No heredoc/injection markers (defense in depth; the single-quoted
   heredoc already prevents shell expansion).
"""

from __future__ import annotations

import re
from typing import Optional

# Classification values
VALID_SDC = "VALID_SDC"
NON_SDC_OUTPUT = "NON_SDC_OUTPUT"
EMPTY_OUTPUT = "EMPTY_OUTPUT"
PROVIDER_FAILURE = "PROVIDER_FAILURE"

# Known SDC command keywords (leading keyword of a command line)
_SDC_KEYWORDS = frozenset({
    "create_clock",
    "create_generated_clock",
    "set_clock_uncertainty",
    "set_clock_latency",
    "set_clock_transition",
    "set_input_delay",
    "set_output_delay",
    "set_input_transition",
    "set_load",
    "set_driving_cell",
    "set_false_path",
    "set_multicycle_path",
    "set_clock_groups",
    "set_max_delay",
    "set_min_delay",
    "set_units",
    "set_sdc_version",
    "set_operating_conditions",
    "set_case_analysis",
    "set_disable_timing",
    "set_max_fanout",
    "set_max_transition",
    "set_max_capacitance",
    "group_path",
    "set_propagated_clock",
})

# Task-required constructs. P172 §5 rule 4 / §10.
TASK_REQUIRED_CONSTRUCTS = {
    "T1": "create_clock",
    "T2": "create_clock",
}

# Conversational wrapper markers (case-insensitive substring match)
_CONVERSATIONAL_MARKERS = (
    "understood",
    "i can help",
    "i'm ready",
    "i am ready",
    "i'd be happy",
    "happy to help",
    "what do you need",
    "what would you like",
    "how can i assist",
    "please provide",
    "let me know what",
    "as an ai",
    "i'm here to help",
    "i am here to help",
)

# Injection / heredoc-delimiter markers that must never appear
_INJECTION_MARKERS = (
    "SDCEOF",
    "TCLEOF",
    "$(",
    "`",
    "; exec ",
    ";rm ",
)

# A question mark at end of a short line is a strong prose signal
_PROSE_QUESTION_RE = re.compile(r"\?\s*$")


def strip_code_fence(text: str) -> str:
    """Extract the SDC content from a ```sdc/```tcl/``` code fence if present.

    Handles a fence anywhere in the text (not only at the start): a model
    may wrap its answer in prose before/after the fenced block. If a fenced
    block is found, its content is returned; otherwise the stripped text.
    """
    stripped = text.strip()
    if "```" not in stripped:
        return stripped
    lines = stripped.splitlines()
    in_fence = False
    body: list = []
    for line in lines:
        s = line.strip()
        if s.startswith("```"):
            if not in_fence:
                in_fence = True  # opening fence (language tag ignored)
            else:
                in_fence = False  # closing fence
            continue
        if in_fence:
            body.append(line)
    if body:
        return "\n".join(body).strip()
    # No complete fence pair; fall back to whole text
    return stripped


def _has_sdc_command(text: str) -> bool:
    """True if at least one line starts with a known SDC keyword."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # First token must be a known SDC keyword (allow leading 'set ',
        # 'create_', 'group_path').
        first = stripped.split()[0]
        if first in _SDC_KEYWORDS:
            return True
    return False


def _has_task_required_construct(text: str, task_id: str) -> bool:
    required = TASK_REQUIRED_CONSTRUCTS.get(task_id)
    if required is None:
        # No task-specific requirement defined → construct rule is vacuously true
        return True
    return required in text


def _has_conversational_wrapper(text: str) -> bool:
    lowered = text.lower()
    for marker in _CONVERSATIONAL_MARKERS:
        if marker in lowered:
            return True
    # Short prose lines ending in '?' (question to the user)
    for line in text.splitlines():
        s = line.strip()
        if s and len(s) < 120 and _PROSE_QUESTION_RE.search(s):
            return True
    return False


def _has_injection_marker(text: str) -> bool:
    for marker in _INJECTION_MARKERS:
        if marker in text:
            return True
    return False


def classify_candidate(
    raw_output: str,
    task_id: str = "T1",
    provider_failure_prefix: str = "ERROR:",
) -> str:
    """Deterministically classify raw model output.

    Returns one of VALID_SDC / NON_SDC_OUTPUT / EMPTY_OUTPUT / PROVIDER_FAILURE.
    """
    if raw_output is None:
        return EMPTY_OUTPUT
    if raw_output.startswith(provider_failure_prefix):
        return PROVIDER_FAILURE

    text = strip_code_fence(raw_output)
    if not text:
        return EMPTY_OUTPUT

    if _has_injection_marker(text):
        return NON_SDC_OUTPUT

    has_cmd = _has_sdc_command(text)
    conversational = _has_conversational_wrapper(text)

    # Rule 2: conversational wrapper with no SDC command → non-SDC.
    # (Conversational preamble WITH valid SDC commands is tolerated: the
    #  command lines are the candidate; the wrapper is stripped downstream
    #  only if it does not interfere with parsing.)
    if conversational and not has_cmd:
        return NON_SDC_OUTPUT

    # Rule 3: at least one valid SDC command required
    if not has_cmd:
        return NON_SDC_OUTPUT

    # Rule 4: task-required construct (create_clock) — vacuous-pass defense
    if not _has_task_required_construct(text, task_id):
        return NON_SDC_OUTPUT

    return VALID_SDC


def extract_sdc_block(text: str) -> Optional[str]:
    """Extract the SDC command block from a valid candidate.

    Returns the SDC text to be evaluated, or None if nothing usable.
    Only called after classify_candidate returned VALID_SDC.
    """
    body = strip_code_fence(text)
    lines = body.splitlines()
    # Keep only SDC-command lines and blank/comment separators; drop any
    # prose prefix/suffix the model may have wrapped around the commands.
    kept = []
    started = False
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if started:
                kept.append(line)
            continue
        first = stripped.split()[0]
        if first in _SDC_KEYWORDS:
            started = True
            kept.append(line)
        elif started:
            # Continuation lines (e.g., wrapped get_ports lists) — keep if
            # they look like continuation content (contain [ ] { } or -flag).
            if "[" in stripped or "{" in stripped or stripped.startswith("-"):
                kept.append(line)
    if not kept:
        return None
    return "\n".join(kept).strip() or None