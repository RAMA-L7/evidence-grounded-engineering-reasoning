"""P055: Read-only re-evaluation mechanism for existing artifacts.

Applies the enhanced Oracle (with design_metadata) to existing candidate SDC
artifacts without making model calls or modifying historical results.

ABSOLUTE RULE: This module MUST NEVER:
- Make model calls
- Modify candidate SDC files
- Overwrite historical manifests
- Modify BENCH-002
- Invoke rta_generate
- Introduce nondeterminism
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from .adapter import EvidenceOracle, OracleResult, _input_hash, _sha256_hex, _canonical_json
from .schemas import (
    SCHEMA_VERSIONS,
    DesignMetadata,
    SCOPE_MAP,
)

# -----------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------
EVALUATOR_CONTEXT_DIR = Path(__file__).resolve().parents[2] / "research" / "experiments" / "EGER-BENCH-002" / "evaluator_context"
RE_EVAL_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "research" / "experiments" / "EGER-EXP-001" / "formal" / "RE-EVAL"


# -----------------------------------------------------------------------
# Data types
# -----------------------------------------------------------------------

@dataclass
class ReEvalResult:
    """Result of re-evaluating one candidate artifact."""
    task_id: str
    condition: str
    run_id: str
    original_evidence_scope: str
    reeval_evidence_scope: str
    scope_changed: bool
    original_outcome: str
    reeval_outcome: str
    outcome_changed: bool
    original_findings_count: int
    reeval_findings_count: int
    metadata_validation: Optional[Dict[str, Any]]
    candidate_hash: str
    reeval_evidence_hash: str
    reevaluated_at: str


# -----------------------------------------------------------------------
# Metadata loading
# -----------------------------------------------------------------------

def load_design_metadata(task_id: str) -> Optional[DesignMetadata]:
    """Load frozen design metadata for a task from evaluator_context/."""
    metadata_path = EVALUATOR_CONTEXT_DIR / f"{task_id}.design_metadata.json"
    if not metadata_path.exists():
        return None
    with open(metadata_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return DesignMetadata.from_dict(data)


def list_available_metadata() -> List[str]:
    """List task IDs that have design metadata available."""
    if not EVALUATOR_CONTEXT_DIR.exists():
        return []
    result = []
    for p in sorted(EVALUATOR_CONTEXT_DIR.glob("*.design_metadata.json")):
        task_id = p.name.replace(".design_metadata.json", "")
        result.append(task_id)
    return result


# -----------------------------------------------------------------------
# Re-evaluation (READ-ONLY)
# -----------------------------------------------------------------------

def re_evaluate_artifact(
    oracle: EvidenceOracle,
    candidate_sdc: str,
    task_id: str,
    condition: str,
    run_id: str,
    original_evidence_scope: str,
    original_outcome: str,
    original_findings_count: int,
    original_candidate_hash: str,
) -> ReEvalResult:
    """Re-evaluate a single candidate artifact with enhanced Oracle.

    READ-ONLY: does not modify the candidate, historical manifest, or BENCH-002.
    """
    metadata = load_design_metadata(task_id)

    result = oracle.validate(
        sdc_text=candidate_sdc,
        input_identity=f"re-eval-{run_id}",
        design_metadata=metadata,
    )

    reeval_scope = "UNSUPPORTED"
    reeval_outcome = "ORACLE_FAILURE"
    metadata_validation = None

    if result.is_success and result.evidence is not None:
        reeval_scope = result.evidence.evidence_scope
        # Determine outcome from scope
        if reeval_scope == "FULL":
            reeval_outcome = "VALID_ARTIFACT"
        elif reeval_scope == "PARTIAL":
            # PARTIAL can be VALID or INVALID depending on findings
            error_findings = [f for f in result.evidence.findings if f.get("severity") == "error"]
            reeval_outcome = "VALID_ARTIFACT" if len(error_findings) == 0 else "INVALID_ARTIFACT"
        else:
            reeval_outcome = "INVALID_ARTIFACT"

        metadata_validation = result.evidence.provenance.get("metadata_validation")

    reeval_findings = len(result.evidence.findings) if result.evidence else 0

    return ReEvalResult(
        task_id=task_id,
        condition=condition,
        run_id=run_id,
        original_evidence_scope=original_evidence_scope,
        reeval_evidence_scope=reeval_scope,
        scope_changed=(reeval_scope != original_evidence_scope),
        original_outcome=original_outcome,
        reeval_outcome=reeval_outcome,
        outcome_changed=(reeval_outcome != original_outcome),
        original_findings_count=original_findings_count,
        reeval_findings_count=reeval_findings,
        metadata_validation=metadata_validation,
        candidate_hash=original_candidate_hash,
        reeval_evidence_hash=result.evidence.evidence_hash if result.evidence else "",
        reevaluated_at=datetime.now(timezone.utc).isoformat(),
    )


# -----------------------------------------------------------------------
# Batch re-evaluation
# -----------------------------------------------------------------------

def re_evaluate_condition(
    oracle: EvidenceOracle,
    condition_dir: Path,
    condition_name: str,
) -> List[ReEvalResult]:
    """Re-evaluate all artifacts in a condition directory.

    READ-ONLY: reads manifests and candidate files, produces re-evaluation results.
    """
    results = []

    manifests_dir = condition_dir / "manifests"
    raw_dir = condition_dir / "raw"

    if not manifests_dir.exists():
        return results

    for manifest_path in sorted(manifests_dir.glob("*.json")):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        task_id = manifest.get("task_id", "UNKNOWN")
        run_id = manifest.get("run_id", "UNKNOWN")

        # Read candidate SDC
        candidate_path = raw_dir / f"{run_id}_revised_candidate.sdc"
        if not candidate_path.exists():
            candidate_path = raw_dir / f"{run_id}_initial_candidate.sdc"
        if not candidate_path.exists():
            continue

        candidate_sdc = candidate_path.read_text(encoding="utf-8")
        candidate_hash = manifest.get("candidate_hash", _input_hash(candidate_sdc))

        reeval = re_evaluate_artifact(
            oracle=oracle,
            candidate_sdc=candidate_sdc,
            task_id=task_id,
            condition=condition_name,
            run_id=run_id,
            original_evidence_scope=manifest.get("evidence_scope", "UNKNOWN"),
            original_outcome=manifest.get("final_outcome", "UNKNOWN"),
            original_findings_count=len(manifest.get("findings", [])),
            original_candidate_hash=candidate_hash,
        )
        results.append(reeval)

    return results


# -----------------------------------------------------------------------
# Output
# -----------------------------------------------------------------------

def save_reeval_results(
    results: List[ReEvalResult],
    output_dir: Optional[Path] = None,
) -> Path:
    """Save re-evaluation results to a deterministic output directory.

    Does NOT modify any historical artifacts.
    """
    out = output_dir or RE_EVAL_OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    # Write index
    index = {
        "schema_version": "eger.reeval.v1",
        "produced_at": datetime.now(timezone.utc).isoformat(),
        "results_count": len(results),
        "results": [asdict(r) for r in results],
    }

    index_path = out / "RE-EVAL-INDEX.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, sort_keys=True, default=str)

    # Write individual results
    for r in results:
        result_path = out / f"{r.run_id}.reeval.json"
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(asdict(r), f, indent=2, sort_keys=True, default=str)

    return out
