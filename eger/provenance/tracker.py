"""ProvenanceTracker — deterministic provenance chain recording.

ENGINEERING DESIGN CHOICE: provenance tracking (P137).

This module records the complete provenance chain for each artifact
in the revision loop. It is deterministic and append-only.

INVARIANT: provenance entries are append-only (no modification).
INVARIANT: every artifact must have a provenance entry.
INVARIANT: provenance is separate from authorization.
INVARIANT: ProvenanceTracker has zero decision authority.

PRODUCER: All components record their provenance here
CONSUMER: Audit, RunRecord, reconstruction
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import hashlib
import json

SCHEMA_PROVENANCE = "eger.provenance.v1"

# Event types
EVENT_RUN_STARTED = "RUN_STARTED"
EVENT_PROMPT_CREATED = "PROMPT_CREATED"
EVENT_CANDIDATE_CREATED = "CANDIDATE_CREATED"
EVENT_ORACLE_EVALUATED = "ORACLE_EVALUATED"
EVENT_EVIDENCE_RECORDED = "EVIDENCE_RECORDED"
EVENT_REVISION_STARTED = "REVISION_STARTED"
EVENT_VERIFICATION_COMPLETED = "VERIFICATION_COMPLETED"
EVENT_RUN_COMPLETED = "RUN_COMPLETED"

# Valid event ordering
_VALID_ORDER = {
    EVENT_RUN_STARTED: 0,
    EVENT_PROMPT_CREATED: 1,
    EVENT_CANDIDATE_CREATED: 2,
    EVENT_ORACLE_EVALUATED: 3,
    EVENT_EVIDENCE_RECORDED: 4,
    EVENT_REVISION_STARTED: 5,
    EVENT_VERIFICATION_COMPLETED: 6,
    EVENT_RUN_COMPLETED: 7,
}


def _deterministic_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ProvenanceEntry:
    """Single provenance entry — append-only."""
    artifact_id: str
    artifact_type: str
    producer: str
    input_hash: str
    output_hash: str
    timestamp: str
    event_type: str = ""
    run_id: str = ""
    iteration: int = -1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunProvenance:
    """Complete provenance for a single run."""
    run_id: str
    task_id: str
    entries: List[ProvenanceEntry] = field(default_factory=list)
    status: str = "IN_PROGRESS"
    terminal_reason: str = ""
    final_candidate_id: Optional[str] = None
    final_evidence_id: Optional[str] = None
    final_verification_decision: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "task_id": self.task_id,
            "entries": [
                {
                    "artifact_id": e.artifact_id,
                    "artifact_type": e.artifact_type,
                    "producer": e.producer,
                    "input_hash": e.input_hash,
                    "output_hash": e.output_hash,
                    "timestamp": e.timestamp,
                    "event_type": e.event_type,
                    "run_id": e.run_id,
                    "iteration": e.iteration,
                    "metadata": dict(e.metadata),
                }
                for e in self.entries
            ],
            "status": self.status,
            "terminal_reason": self.terminal_reason,
            "final_candidate_id": self.final_candidate_id,
            "final_evidence_id": self.final_evidence_id,
            "final_verification_decision": self.final_verification_decision,
            "entry_count": len(self.entries),
        }


class ProvenanceTracker:
    """Deterministic provenance chain — append-only.

    Records the complete provenance for each EGER run, including:
    - Run lifecycle (start, complete)
    - Artifact relationships (prompt → candidate → evidence → verification)
    - Revision history (iteration order)
    - Terminal state

    INVARIANT: Entries are append-only.
    INVARIANT: ProvenanceTracker has zero decision authority.
    INVARIANT: Cannot ACCEPT/REJECT/VERIFY/AUTHORIZE.
    """

    def __init__(self):
        self._entries: List[ProvenanceEntry] = []
        self._runs: Dict[str, RunProvenance] = {}

    @property
    def entries(self) -> List[ProvenanceEntry]:
        """Read-only access to entries."""
        return list(self._entries)

    @property
    def entry_count(self) -> int:
        return len(self._entries)

    @property
    def run_count(self) -> int:
        return len(self._runs)

    def start_run(self, run_id: str, task_id: str) -> RunProvenance:
        """Start a new run and record the RUN_STARTED event."""
        if run_id in self._runs:
            raise ValueError(f"Run {run_id} already exists")

        run = RunProvenance(run_id=run_id, task_id=task_id)
        self._runs[run_id] = run

        entry = self.record(
            artifact_id=run_id,
            artifact_type="run",
            producer="RevisionController",
            input_hash="",
            output_hash=_deterministic_hash(run_id.encode()),
            event_type=EVENT_RUN_STARTED,
            run_id=run_id,
            iteration=0,
            metadata={"task_id": task_id},
        )
        run.entries.append(entry)
        return run

    def record_prompt(
        self,
        run_id: str,
        prompt_hash: str,
        request_id: str,
        iteration: int,
        task_id: str = "",
    ) -> ProvenanceEntry:
        """Record a PROMPT_CREATED event."""
        entry = self.record(
            artifact_id=request_id,
            artifact_type="prompt",
            producer="PromptBuilder",
            input_hash=prompt_hash,
            output_hash=prompt_hash,
            event_type=EVENT_PROMPT_CREATED,
            run_id=run_id,
            iteration=iteration,
            metadata={"task_id": task_id, "prompt_hash": prompt_hash},
        )
        if run_id in self._runs:
            self._runs[run_id].entries.append(entry)
        return entry

    def record_candidate(
        self,
        run_id: str,
        candidate_id: str,
        candidate_hash: str,
        iteration: int,
        prompt_id: str = "",
    ) -> ProvenanceEntry:
        """Record a CANDIDATE_CREATED event."""
        entry = self.record(
            artifact_id=candidate_id,
            artifact_type="candidate",
            producer="ProposalGenerator",
            input_hash=prompt_id,
            output_hash=candidate_hash,
            event_type=EVENT_CANDIDATE_CREATED,
            run_id=run_id,
            iteration=iteration,
            metadata={"prompt_id": prompt_id, "candidate_hash": candidate_hash},
        )
        if run_id in self._runs:
            self._runs[run_id].entries.append(entry)
        return entry

    def record_oracle_evaluation(
        self,
        run_id: str,
        oracle_artifact_id: str,
        candidate_hash: str,
        iteration: int,
    ) -> ProvenanceEntry:
        """Record an ORACLE_EVALUATED event."""
        entry = self.record(
            artifact_id=oracle_artifact_id,
            artifact_type="oracle_evaluation",
            producer="OracleAdapter",
            input_hash=candidate_hash,
            output_hash=_deterministic_hash(oracle_artifact_id.encode()),
            event_type=EVENT_ORACLE_EVALUATED,
            run_id=run_id,
            iteration=iteration,
            metadata={"candidate_hash": candidate_hash},
        )
        if run_id in self._runs:
            self._runs[run_id].entries.append(entry)
        return entry

    def record_evidence(
        self,
        run_id: str,
        evidence_id: str,
        evidence_hash: str,
        iteration: int,
        oracle_artifact_id: str = "",
    ) -> ProvenanceEntry:
        """Record an EVIDENCE_RECORDED event."""
        entry = self.record(
            artifact_id=evidence_id,
            artifact_type="evidence",
            producer="EvidenceNormalizer",
            input_hash=oracle_artifact_id,
            output_hash=evidence_hash,
            event_type=EVENT_EVIDENCE_RECORDED,
            run_id=run_id,
            iteration=iteration,
            metadata={"oracle_artifact_id": oracle_artifact_id},
        )
        if run_id in self._runs:
            self._runs[run_id].entries.append(entry)
        return entry

    def record_verification(
        self,
        run_id: str,
        verification_decision: str,
        candidate_id: str,
        evidence_id: str,
    ) -> ProvenanceEntry:
        """Record a VERIFICATION_COMPLETED event."""
        entry = self.record(
            artifact_id=f"VERIF-{run_id}",
            artifact_type="verification",
            producer="VerificationGate",
            input_hash=candidate_id,
            output_hash=_deterministic_hash(verification_decision.encode()),
            event_type=EVENT_VERIFICATION_COMPLETED,
            run_id=run_id,
            iteration=-1,
            metadata={
                "decision": verification_decision,
                "candidate_id": candidate_id,
                "evidence_id": evidence_id,
            },
        )
        if run_id in self._runs:
            run = self._runs[run_id]
            run.entries.append(entry)
            run.final_verification_decision = verification_decision
        return entry

    def complete_run(
        self,
        run_id: str,
        status: str = "COMPLETED",
        terminal_reason: str = "",
        final_candidate_id: Optional[str] = None,
        final_evidence_id: Optional[str] = None,
    ) -> ProvenanceEntry:
        """Record a RUN_COMPLETED event."""
        entry = self.record(
            artifact_id=run_id,
            artifact_type="run",
            producer="RevisionController",
            input_hash="",
            output_hash=_deterministic_hash(run_id.encode()),
            event_type=EVENT_RUN_COMPLETED,
            run_id=run_id,
            iteration=-1,
            metadata={
                "status": status,
                "terminal_reason": terminal_reason,
            },
        )
        if run_id in self._runs:
            run = self._runs[run_id]
            run.entries.append(entry)
            run.status = status
            run.terminal_reason = terminal_reason
            run.final_candidate_id = final_candidate_id
            run.final_evidence_id = final_evidence_id
        return entry

    def get_run(self, run_id: str) -> Optional[RunProvenance]:
        """Retrieve complete run provenance."""
        return self._runs.get(run_id)

    def get_run_entries(self, run_id: str) -> List[ProvenanceEntry]:
        """Get all entries for a specific run, in order."""
        if run_id not in self._runs:
            return []
        return list(self._runs[run_id].entries)

    def get_entry(self, artifact_id: str) -> Optional[ProvenanceEntry]:
        """Look up entry by artifact_id."""
        for entry in self._entries:
            if entry.artifact_id == artifact_id:
                return entry
        return None

    def get_chain(self, artifact_id: str) -> List[ProvenanceEntry]:
        """Get the provenance chain leading to an artifact."""
        chain = []
        for entry in self._entries:
            if entry.artifact_id == artifact_id:
                chain.append(entry)
                # Follow output_hash → input_hash links
                for e2 in self._entries:
                    if e2.output_hash == entry.input_hash:
                        chain.append(e2)
        return chain

    def reconstruct_run(self, run_id: str) -> Dict[str, Any]:
        """Deterministic reconstruction of a complete run.

        Returns a dict containing all artifacts in order:
        - task_id
        - prompts
        - candidates
        - evidence artifacts
        - verification result
        - terminal state
        """
        run = self._runs.get(run_id)
        if run is None:
            return {"error": f"Run {run_id} not found", "status": "NOT_FOUND"}

        prompts = []
        candidates = []
        evidence_list = []
        verification = None

        for entry in run.entries:
            if entry.event_type == EVENT_PROMPT_CREATED:
                prompts.append({
                    "artifact_id": entry.artifact_id,
                    "iteration": entry.iteration,
                    "prompt_hash": entry.metadata.get("prompt_hash", ""),
                })
            elif entry.event_type == EVENT_CANDIDATE_CREATED:
                candidates.append({
                    "artifact_id": entry.artifact_id,
                    "iteration": entry.iteration,
                    "candidate_hash": entry.metadata.get("candidate_hash", ""),
                })
            elif entry.event_type == EVENT_EVIDENCE_RECORDED:
                evidence_list.append({
                    "artifact_id": entry.artifact_id,
                    "iteration": entry.iteration,
                    "oracle_artifact_id": entry.metadata.get("oracle_artifact_id", ""),
                })
            elif entry.event_type == EVENT_VERIFICATION_COMPLETED:
                verification = {
                    "decision": entry.metadata.get("decision", ""),
                    "candidate_id": entry.metadata.get("candidate_id", ""),
                    "evidence_id": entry.metadata.get("evidence_id", ""),
                }

        return {
            "run_id": run.run_id,
            "task_id": run.task_id,
            "status": run.status,
            "terminal_reason": run.terminal_reason,
            "prompts": prompts,
            "candidates": candidates,
            "evidence": evidence_list,
            "verification": verification,
            "final_candidate_id": run.final_candidate_id,
            "final_evidence_id": run.final_evidence_id,
            "final_verification_decision": run.final_verification_decision,
            "entry_count": len(run.entries),
        }

    # -- Base methods (preserve backward compatibility) --------------------

    def record(
        self,
        artifact_id: str,
        artifact_type: str,
        producer: str,
        input_hash: str,
        output_hash: str,
        metadata: Optional[Dict[str, Any]] = None,
        event_type: str = "",
        run_id: str = "",
        iteration: int = -1,
    ) -> ProvenanceEntry:
        """Append a provenance entry — deterministic, append-only."""
        entry = ProvenanceEntry(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            producer=producer,
            input_hash=input_hash,
            output_hash=output_hash,
            timestamp=_now_iso(),
            event_type=event_type,
            run_id=run_id,
            iteration=iteration,
            metadata=metadata or {},
        )
        self._entries.append(entry)
        return entry

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": SCHEMA_PROVENANCE,
            "entries": [
                {
                    "artifact_id": e.artifact_id,
                    "artifact_type": e.artifact_type,
                    "producer": e.producer,
                    "input_hash": e.input_hash,
                    "output_hash": e.output_hash,
                    "timestamp": e.timestamp,
                    "event_type": e.event_type,
                    "run_id": e.run_id,
                    "iteration": e.iteration,
                    "metadata": dict(e.metadata),
                }
                for e in self._entries
            ],
            "runs": {
                run_id: run.to_dict()
                for run_id, run in self._runs.items()
            },
            "entry_count": len(self._entries),
            "run_count": len(self._runs),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ProvenanceTracker:
        tracker = cls()
        for e in d.get("entries", []):
            tracker._entries.append(ProvenanceEntry(
                artifact_id=e["artifact_id"],
                artifact_type=e["artifact_type"],
                producer=e["producer"],
                input_hash=e["input_hash"],
                output_hash=e["output_hash"],
                timestamp=e["timestamp"],
                event_type=e.get("event_type", ""),
                run_id=e.get("run_id", ""),
                iteration=e.get("iteration", -1),
                metadata=dict(e.get("metadata", {})),
            ))
        # Reconstruct runs from entries
        for run_id, run_data in d.get("runs", {}).items():
            run = RunProvenance(
                run_id=run_data["run_id"],
                task_id=run_data["task_id"],
                status=run_data.get("status", "COMPLETED"),
                terminal_reason=run_data.get("terminal_reason", ""),
                final_candidate_id=run_data.get("final_candidate_id"),
                final_evidence_id=run_data.get("final_evidence_id"),
                final_verification_decision=run_data.get("final_verification_decision"),
            )
            # Re-link entries to run
            for entry in tracker._entries:
                if entry.run_id == run_id:
                    run.entries.append(entry)
            tracker._runs[run_id] = run
        return tracker
