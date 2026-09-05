"""Repaired trial runner (P172 §7, §8, §10, §13, §15).

Implements the P172 repairs over the P170 harness:

1. Initial Oracle evaluation on the initial SDC BEFORE any model invocation
   (PO-3 repair, P172 §7) — records initial_oracle_result + initial_evidence_hash.
2. Candidate-validity gate before every Oracle evaluation (P172 §5).
3. One bounded retry for generation/harness failures (P172 §8).
4. NO_TIMING_CONSTRAINT protection at the experiment layer (P172 §13).
5. Complete per-attempt records (P172 §15 schema).

Both attempts of a trial are recorded; a retry reuses the identical
configuration. No methodology decisions are made after seeing results.
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from . import candidate_validity as cv
from .candidate_validity import (
    classify_candidate,
    extract_sdc_block,
    VALID_SDC,
    NON_SDC_OUTPUT,
    EMPTY_OUTPUT,
    PROVIDER_FAILURE,
)

MAX_RETRIES = 1  # P169/P172: 1 bounded retry per trial

# Failure kinds that trigger a bounded retry (P172 §8)
RETRYABLE_FAILURE_KINDS = {
    "PROVIDER_FAILURE",
    "EMPTY_OUTPUT",
    "CANDIDATE_INVALID",
    "TIMEOUT",
    "INFRASTRUCTURE_FAILURE",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Oracle result summary helpers
# ---------------------------------------------------------------------------

def _error_count(result) -> Optional[int]:
    if not result.is_success or result.evidence is None:
        return None
    findings = getattr(result.evidence, "findings", None) or []
    return sum(1 for f in findings if (f.get("severity") if isinstance(f, dict) else getattr(f, "severity", "")) == "error")


def _wns(result) -> Optional[float]:
    if not result.is_success or result.evidence is None:
        return None
    scope = getattr(result.evidence, "analysis_scope", None) or {}
    if isinstance(scope, dict):
        return scope.get("wns")
    return getattr(scope, "wns", None)


def oracle_summary(result, oracle_name: str) -> Dict[str, Any]:
    """Compact, deterministic summary of an OracleResult for the record."""
    if not result.is_success:
        failure = result.failure
        return {
            "is_success": False,
            "oracle_status": "FAILURE",
            "failure_kind": getattr(failure, "kind", "ORACLE_FAILURE"),
            "exit_code": getattr(failure, "exit_code", -1),
            "message": getattr(failure, "message", ""),
        }
    ev = result.evidence
    findings = getattr(ev, "findings", None) or []
    # P176: expose the P055 metadata-validation outcome so the experiment
    # layer can flag evaluations whose references were not all validated
    # (metadata PARTIAL — e.g., a candidate referencing a nonexistent port).
    # Present only for evaluations run with design_metadata (the Ṛta arm).
    provenance = getattr(ev, "provenance", None) or {}
    metadata_validation = provenance.get("metadata_validation") if isinstance(provenance, dict) else None
    metadata_all_validated = (
        bool(metadata_validation.get("all_validated"))
        if isinstance(metadata_validation, dict) and metadata_validation.get("total_references", 0) > 0
        else None
    )
    return {
        "is_success": True,
        "oracle_status": getattr(ev, "oracle_status", "SUCCESS"),
        "evidence_scope": getattr(ev, "evidence_scope", None),
        "evidence_hash": getattr(ev, "evidence_hash", None),
        "error_count": _error_count(result),
        "wns": _wns(result),
        "metadata_all_validated": metadata_all_validated,
        "analysis_scope_status": (
            (getattr(ev, "analysis_scope", None) or {}).get("status")
            if isinstance(getattr(ev, "analysis_scope", None), dict)
            else None
        ),
        "finding_count": len(findings),
    }


def _classify_attempt_failure(
    validity: str,
    result,
) -> Optional[str]:
    """Map an attempt outcome to a failure kind, or None if not failed.

    P172 §8: retryable = generation/harness failures (PROVIDER_FAILURE,
    EMPTY_OUTPUT, CANDIDATE_INVALID, Oracle timeout). Not retryable =
    Oracle non-zero exit on a valid candidate (ORACLE_FAILURE).
    """
    if validity == PROVIDER_FAILURE:
        return "PROVIDER_FAILURE"
    if validity == EMPTY_OUTPUT:
        return "EMPTY_OUTPUT"
    if validity == NON_SDC_OUTPUT:
        return "CANDIDATE_INVALID"
    if result is not None and not result.is_success:
        kind = getattr(result.failure, "kind", "ORACLE_FAILURE")
        exit_code = getattr(result.failure, "exit_code", -1)
        if kind == "ORACLE_FAILURE" and exit_code == -1:
            return "TIMEOUT"
        return "ORACLE_FAILURE"
    return None


# ---------------------------------------------------------------------------
# Single attempt
# ---------------------------------------------------------------------------

def _run_attempt(
    *,
    trial_id: str,
    task_id: str,
    oracle_name: str,
    replication_id: int,
    execution_order: int,
    attempt: int,
    initial_sdc: str,
    design_context: str,
    oracle_call: Callable[[str, str], Any],
    model_call: Callable[[str], str],
    normalizer,
    gate,
    max_iterations: int = 3,
    provider_failure_prefix: str = "ERROR:",
) -> Dict[str, Any]:
    """Execute one attempt of a trial (P172 §7 sequence)."""
    start = time.time()
    attempt_record: Dict[str, Any] = {
        "trial_id": trial_id,
        "task_id": task_id,
        "oracle": oracle_name,
        "replication_id": replication_id,
        "execution_order": execution_order,
        "attempt": attempt,
        "retry_count": attempt - 1,
        "initial_sdc": initial_sdc,
        "initial_sdc_hash": sha256_text(initial_sdc),
    }

    # ---- 1. Initial Oracle evaluation (PO-3 repair, P172 §7) ----
    initial_result = oracle_call(initial_sdc, f"{trial_id}-initial")
    attempt_record["initial_oracle_result"] = oracle_summary(initial_result, oracle_name)
    if initial_result.is_success and initial_result.evidence is not None:
        attempt_record["initial_evidence_hash"] = getattr(initial_result.evidence, "evidence_hash", None)
    else:
        attempt_record["initial_evidence_hash"] = None

    # Initial evaluation failure is a trial-level failure (harness/oracle
    # problem), retryable if it is a timeout; recorded, never fabricated.
    initial_failure = _classify_attempt_failure("", initial_result) if not initial_result.is_success else None
    if initial_failure is not None:
        attempt_record["completion_status"] = "FAILED"
        attempt_record["failure_kind"] = initial_failure
        attempt_record["iterations"] = []
        attempt_record["oracle_call_count"] = 1
        attempt_record["iteration_count"] = 0
        attempt_record["runtime_seconds"] = round(time.time() - start, 3)
        return attempt_record

    # ---- 2. Revision loop ----
    iterations: List[Dict[str, Any]] = []
    current_sdc = initial_sdc
    oracle_call_count = 1  # initial evaluation counted
    completed_with_accept = False
    final_sdc = initial_sdc
    final_oracle_result = None

    for iteration in range(1, max_iterations + 1):
        iter_record: Dict[str, Any] = {"iteration": iteration}

        # 2a. Generate candidate
        prompt = _build_prompt(design_context, current_sdc, iterations, oracle_name)
        raw_output = model_call(prompt)
        validity = classify_candidate(raw_output, task_id=task_id, provider_failure_prefix=provider_failure_prefix)
        iter_record["candidate_raw"] = raw_output
        iter_record["candidate_raw_hash"] = sha256_text(raw_output or "")
        iter_record["candidate_validity"] = validity

        if validity != VALID_SDC:
            # Generation failure → this attempt fails here (retry policy
            # handled at the attempt wrapper level, P172 §8).
            iter_record["oracle_result"] = None
            iterations.append(iter_record)
            attempt_record["iterations"] = iterations
            attempt_record["completion_status"] = "FAILED"
            attempt_record["failure_kind"] = _classify_attempt_failure(validity, None)
            attempt_record["oracle_call_count"] = oracle_call_count
            attempt_record["iteration_count"] = len(iterations)
            attempt_record["runtime_seconds"] = round(time.time() - start, 3)
            return attempt_record

        sdc_block = extract_sdc_block(raw_output)
        if sdc_block is None:
            iter_record["candidate_validity"] = NON_SDC_OUTPUT
            iterations.append(iter_record)
            attempt_record["iterations"] = iterations
            attempt_record["completion_status"] = "FAILED"
            attempt_record["failure_kind"] = "CANDIDATE_INVALID"
            attempt_record["oracle_call_count"] = oracle_call_count
            attempt_record["iteration_count"] = len(iterations)
            attempt_record["runtime_seconds"] = round(time.time() - start, 3)
            return attempt_record

        iter_record["candidate_sdc"] = sdc_block
        iter_record["candidate_sdc_hash"] = sha256_text(sdc_block)
        # NO_TIMING_CONSTRAINT protection: record whether the candidate
        # defines the required clock (P172 §13 layer 1 already enforced by
        # the validity gate; this is the auditable experiment-layer flag).
        iter_record["clock_defined"] = "create_clock" in sdc_block

        # 2b. Oracle evaluation
        result = oracle_call(sdc_block, f"{trial_id}-iter-{iteration}")
        oracle_call_count += 1
        iter_record["oracle_result"] = oracle_summary(result, oracle_name)

        failure_kind = _classify_attempt_failure("", result)
        if failure_kind is not None:
            iterations.append(iter_record)
            attempt_record["iterations"] = iterations
            attempt_record["completion_status"] = "FAILED"
            attempt_record["failure_kind"] = failure_kind
            attempt_record["oracle_call_count"] = oracle_call_count
            attempt_record["iteration_count"] = len(iterations)
            attempt_record["runtime_seconds"] = round(time.time() - start, 3)
            return attempt_record

        # 2c. Normalize evidence + verification (existing EGER chain)
        candidate = _build_candidate(sdc_block)
        evidence = normalizer.normalize(
            result.evidence,
            task_id=task_id,
            candidate_hash=sha256_text(sdc_block)[:12],
        )
        verification = gate.evaluate(candidate, evidence)
        iter_record["evidence_hash"] = evidence.evidence_hash
        iter_record["verification_decision"] = verification.decision
        iter_record["verification_reason"] = verification.reason
        iterations.append(iter_record)

        final_sdc = sdc_block
        final_oracle_result = iter_record["oracle_result"]

        if verification.decision == "ACCEPT":
            completed_with_accept = True
            break

        current_sdc = sdc_block

    # ---- 3. Final Oracle evaluation (PO-3 repair, P172 §7) ----
    # If the trial reached ACCEPT, the last iteration evaluation IS the final
    # evaluation (same SDC, deterministic Oracle) — reuse it to avoid a
    # redundant call. Otherwise, evaluate the final SDC explicitly.
    if completed_with_accept:
        final_oracle_result = final_oracle_result or oracle_summary(oracle_call(final_sdc, f"{trial_id}-final"), oracle_name)
        if final_oracle_result is None:
            fr = oracle_call(final_sdc, f"{trial_id}-final")
            final_oracle_result = oracle_summary(fr, oracle_name)
    else:
        fr = oracle_call(final_sdc, f"{trial_id}-final")
        oracle_call_count += 1
        final_oracle_result = oracle_summary(fr, oracle_name)

    attempt_record["iterations"] = iterations
    attempt_record["completion_status"] = "COMPLETED"
    attempt_record["failure_kind"] = None
    attempt_record["final_sdc"] = final_sdc
    attempt_record["final_sdc_hash"] = sha256_text(final_sdc)
    attempt_record["final_oracle_result"] = final_oracle_result
    attempt_record["oracle_call_count"] = oracle_call_count
    attempt_record["iteration_count"] = len(iterations)
    attempt_record["accept_reached"] = completed_with_accept
    attempt_record["runtime_seconds"] = round(time.time() - start, 3)
    return attempt_record


_ORDINALS = [
    "First", "Second", "Third", "Fourth", "Fifth",
    "Sixth", "Seventh", "Eighth", "Ninth", "Tenth",
]


def _format_sdc_lines(sdc_text: str) -> str:
    """Format SDC text as numbered lines for the file-writing prompt.

    The model (opencode/mimo-v2.5-free) reliably follows a directive
    "Write the file timing.sdc. First line: ... Second line: ..."
    instruction (P173-R diagnostic), so the current SDC is presented
    line-by-line rather than as a raw block.
    """
    lines = [ln.rstrip() for ln in sdc_text.splitlines() if ln.strip()]
    if not lines:
        return "(empty SDC)"
    parts = []
    for i, line in enumerate(lines):
        if i < len(_ORDINALS):
            parts.append(f"{_ORDINALS[i]} line: {line}")
        else:
            parts.append(f"Line {i + 1}: {line}")
    return ". ".join(parts) + "."


def _build_prompt(design_context: str, current_sdc: str, iterations: List[Dict[str, Any]], oracle_name: str) -> str:
    """Frozen prompt template (P172 §6 Option A: repaired prompt/harness).

    P173-R invocation repair: the model (opencode/mimo-v2.5-free) is a
    file-writing agent. Diagnostic testing (P173-R) showed it reliably writes
    timing.sdc when prompted with a TERSE directive ("Write the file timing.sdc."
    + numbered SDC lines + feedback + overwrite instruction), but switches to
    conversational mode when given a verbose role preamble ("You are an SDC
    author...") or a long REQUIRED CONTENT / OUTPUT RULES block. The prompt is
    therefore terse and file-based. The validity gate still enforces compliance
    regardless of the model's behavior.
    """
    if iterations:
        last = iterations[-1]
        feedback = json.dumps(last.get("oracle_result", {}), indent=2)
        feedback_str = f"Oracle feedback: {feedback}"
    else:
        feedback_str = "Oracle feedback: None (first iteration)"

    numbered = _format_sdc_lines(current_sdc)

    return (
        "Write the file timing.sdc. "
        f"{numbered} "
        f"{feedback_str} "
        f"Overwrite the file with a complete, correct SDC for the design simple_path "
        "(ports clk, data_in, data_out). "
        "The SDC must include create_clock, set_input_delay, and set_output_delay commands. "
        "Do not create any other files."
    )


def _build_candidate(sdc_text: str):
    from eger.engineer.candidate import build_candidate
    return build_candidate(sdc_text)


# ---------------------------------------------------------------------------
# Attempt wrapper with bounded retry (P172 §8)
# ---------------------------------------------------------------------------

def run_trial(
    *,
    trial_id: str,
    task_id: str,
    oracle_name: str,
    replication_id: int,
    execution_order: int,
    initial_sdc: str,
    design_context: str,
    oracle_call: Callable[[str, str], Any],
    model_call: Callable[[str], str],
    normalizer,
    gate,
    max_iterations: int = 3,
    max_retries: int = MAX_RETRIES,
) -> Dict[str, Any]:
    """Run a trial with up to `max_retries` bounded retries.

    Both attempts are recorded. If attempt 1 fails with a retryable
    failure kind, attempt 2 runs with identical configuration. If attempt 2
    also fails, the trial is FAILED with attempt 2's failure kind.

    Retry policy (P172 §8):
    - Retryable: PROVIDER_FAILURE, EMPTY_OUTPUT, CANDIDATE_INVALID, TIMEOUT,
      INFRASTRUCTURE_FAILURE
    - NOT retryable: ORACLE_FAILURE (non-zero exit on valid candidate);
      REJECT on a valid candidate (an engineering outcome, not a failure)
    """
    attempts: List[Dict[str, Any]] = []
    last = None
    for attempt in range(1, max_retries + 2):
        last = _run_attempt(
            trial_id=trial_id,
            task_id=task_id,
            oracle_name=oracle_name,
            replication_id=replication_id,
            execution_order=execution_order,
            attempt=attempt,
            initial_sdc=initial_sdc,
            design_context=design_context,
            oracle_call=oracle_call,
            model_call=model_call,
            normalizer=normalizer,
            gate=gate,
            max_iterations=max_iterations,
        )
        attempts.append(last)
        if last["completion_status"] == "COMPLETED":
            break
        if last["failure_kind"] not in RETRYABLE_FAILURE_KINDS:
            break  # non-retryable failure (P172 §8)

    record = dict(last)
    record["attempts"] = attempts
    record["retry_count"] = len(attempts) - 1
    return record


# ---------------------------------------------------------------------------
# Post-trial derivation (PO-1 / PO-3)
# ---------------------------------------------------------------------------

def compute_po3(initial_oracle_result: Dict[str, Any], final_oracle_result: Dict[str, Any], oracle_name: str) -> str:
    """PO-3 per frozen P169 §7 definition, with P172 §13 boundary rule.

    - Ṛta: IMPROVED if ERROR count(final) < ERROR count(initial);
           NOT_IMPROVED if equal; WORSE if greater.
    - OpenSTA: IMPROVED if WNS(final) > WNS(initial); NOT_IMPROVED if equal;
               WORSE if WNS(final) < WNS(initial).
    - Missing data: FAILED trials excluded (caller handles).
    - NO_TIMING_CONSTRAINT boundary (P172 §13): if the initial OpenSTA
      evaluation is not a qualified timing evaluation, PO-3 is
      NOT_MEASURABLE (initial state undefined).
    """
    if initial_oracle_result is None or final_oracle_result is None:
        return "NOT_MEASURABLE"
    if not initial_oracle_result.get("is_success") or not final_oracle_result.get("is_success"):
        return "NOT_MEASURABLE"

    if oracle_name == "Rta":
        init_err = initial_oracle_result.get("error_count")
        final_err = final_oracle_result.get("error_count")
        if init_err is None or final_err is None:
            return "NOT_MEASURABLE"
        if final_err < init_err:
            return "IMPROVED"
        if final_err > init_err:
            return "WORSE"
        return "NOT_IMPROVED"

    # OpenSTA
    init_wns = initial_oracle_result.get("wns")
    final_wns = final_oracle_result.get("wns")
    # NO_TIMING_CONSTRAINT boundary: initial evaluation must have a defined
    # clock AND a measured WNS for the comparison to be meaningful.
    if init_wns is None:
        return "NOT_MEASURABLE"
    if final_wns is None:
        return "NOT_MEASURABLE"
    if final_wns > init_wns:
        return "IMPROVED"
    if final_wns < init_wns:
        return "WORSE"
    return "NOT_IMPROVED"


def compute_po1(completion_status: str, po3: str) -> str:
    """PO-1 completion quality per P169 §7.

    ROBUST: pipeline completes + final candidate differs from initial +
            Oracle evaluation improves.
    MARGINAL: completes without improvement.
    FAILED: does not complete.
    """
    if completion_status != "COMPLETED":
        return "FAILED"
    if po3 == "IMPROVED":
        return "ROBUST"
    return "MARGINAL"


def derive_trial_metrics(record: Dict[str, Any]) -> Dict[str, Any]:
    """Derive PO-1/PO-3/evidence-compatibility for a trial record.

    Deterministic given the raw record. No manual judgment.
    """
    initial = record.get("initial_oracle_result")
    final = record.get("final_oracle_result")
    oracle_name = record.get("oracle", "")
    po3 = compute_po3(initial, final, oracle_name)
    po1 = compute_po1(record.get("completion_status", "FAILED"), po3)

    # PO-2: evidence compatibility = every successful Oracle evaluation
    # produced a normalized EvidenceArtifact that entered the contract.
    evidence_compatible = True
    evaluations = 0
    if initial and initial.get("is_success") and record.get("initial_evidence_hash"):
        evaluations += 1
    for it in record.get("iterations", []):
        ores = it.get("oracle_result")
        if ores and ores.get("is_success"):
            evaluations += 1
            if not it.get("evidence_hash"):
                evidence_compatible = False
    # Final evaluation is a separate invocation only when ACCEPT was not
    # reached (accept path reuses the last iteration's result).
    if (
        final
        and final.get("is_success")
        and not record.get("accept_reached", False)
        and record.get("completion_status") == "COMPLETED"
    ):
        evaluations += 1

    # NO_TIMING_CONSTRAINT flags (P172 §13): an OpenSTA evaluation is
    # unqualified if the candidate did not define the required clock.
    no_timing_constraint = []
    if oracle_name == "OpenSTA":
        for it in record.get("iterations", []):
            if it.get("oracle_result", {}).get("is_success") and not it.get("clock_defined", False):
                no_timing_constraint.append(it.get("iteration"))

    # P176 metadata-unqualified flags (Ṛta arm, mirroring the
    # NO_TIMING_CONSTRAINT precedent): an evaluation is unqualified when the
    # P055 metadata validation did NOT validate every referenced object
    # (evidence scope PARTIAL — e.g., a candidate referencing a nonexistent
    # port). The FROZEN VerificationGate accepts PARTIAL-with-zero-errors by
    # contract, so this experiment-layer flag is the fail-closed lever the
    # future PILOT-002 analysis uses to exclude unqualified accepts.
    metadata_unqualified = []
    if oracle_name == "Rta":
        for it in record.get("iterations", []):
            ores = it.get("oracle_result", {}) or {}
            if ores.get("is_success") and ores.get("metadata_all_validated") is False:
                metadata_unqualified.append(it.get("iteration"))

    return {
        "completion_quality": po1,
        "oracle_detected_improvement": po3,
        "evidence_compatible": evidence_compatible,
        "evaluation_count": evaluations,
        "no_timing_constraint_iterations": no_timing_constraint,
        "metadata_unqualified_iterations": metadata_unqualified,
    }