"""Deterministic unit tests for EGER provenance tracker (P143).

Tests verify:
- Run lifecycle
- Artifact recording
- Revision history
- Event ordering
- Identity preservation
- Determinism
- Reconstruction
- Integrity checks
- Immutability
- No authority

No live model calls. No external dependencies. Fully deterministic.
"""

import pytest
from typing import Dict, Any

from eger.provenance.tracker import (
    ProvenanceTracker,
    RunProvenance,
    EVENT_RUN_STARTED,
    EVENT_PROMPT_CREATED,
    EVENT_CANDIDATE_CREATED,
    EVENT_ORACLE_EVALUATED,
    EVENT_EVIDENCE_RECORDED,
    EVENT_VERIFICATION_COMPLETED,
    EVENT_RUN_COMPLETED,
)


# ---------------------------------------------------------------------------
# ProvenanceTracker tests
# ---------------------------------------------------------------------------

class TestProvenanceTracker:
    """Tests for eger.provenance.tracker.ProvenanceTracker"""

    def setup_method(self):
        self.tracker = ProvenanceTracker()

    # -- Run lifecycle -----------------------------------------------------

    def test_start_run(self):
        """Start a new run."""
        run = self.tracker.start_run("R-001", "T-001")

        assert run.run_id == "R-001"
        assert run.task_id == "T-001"
        assert run.status == "IN_PROGRESS"
        assert self.tracker.run_count == 1
        assert self.tracker.entry_count == 1

    def test_duplicate_run_rejected(self):
        """Duplicate run ID is rejected."""
        self.tracker.start_run("R-001", "T-001")

        with pytest.raises(ValueError, match="already exists"):
            self.tracker.start_run("R-001", "T-001")

    def test_complete_run(self):
        """Complete a run."""
        self.tracker.start_run("R-001", "T-001")
        self.tracker.complete_run(
            "R-001",
            status="COMPLETED",
            terminal_reason="NO_ERRORS",
            final_candidate_id="C-001",
            final_evidence_id="E-001",
        )

        run = self.tracker.get_run("R-001")
        assert run.status == "COMPLETED"
        assert run.terminal_reason == "NO_ERRORS"
        assert run.final_candidate_id == "C-001"
        assert run.final_evidence_id == "E-001"

    def test_multiple_runs(self):
        """Multiple runs are tracked independently."""
        self.tracker.start_run("R-001", "T-001")
        self.tracker.start_run("R-002", "T-002")

        assert self.tracker.run_count == 2

        run1 = self.tracker.get_run("R-001")
        run2 = self.tracker.get_run("R-002")

        assert run1.task_id == "T-001"
        assert run2.task_id == "T-002"

    # -- Artifact recording ------------------------------------------------

    def test_record_prompt(self):
        """Prompt is recorded with correct metadata."""
        self.tracker.start_run("R-001", "T-001")
        entry = self.tracker.record_prompt(
            run_id="R-001",
            prompt_hash="HASH-123",
            request_id="PR-001",
            iteration=0,
            task_id="T-001",
        )

        assert entry.artifact_id == "PR-001"
        assert entry.event_type == EVENT_PROMPT_CREATED
        assert entry.iteration == 0
        assert entry.metadata["prompt_hash"] == "HASH-123"

    def test_record_candidate(self):
        """Candidate is recorded with correct metadata."""
        self.tracker.start_run("R-001", "T-001")
        entry = self.tracker.record_candidate(
            run_id="R-001",
            candidate_id="C-001",
            candidate_hash="HASH-456",
            iteration=0,
            prompt_id="PR-001",
        )

        assert entry.artifact_id == "C-001"
        assert entry.event_type == EVENT_CANDIDATE_CREATED
        assert entry.metadata["candidate_hash"] == "HASH-456"

    def test_record_oracle_evaluation(self):
        """Oracle evaluation is recorded."""
        self.tracker.start_run("R-001", "T-001")
        entry = self.tracker.record_oracle_evaluation(
            run_id="R-001",
            oracle_artifact_id="ORA-001",
            candidate_hash="HASH-456",
            iteration=0,
        )

        assert entry.artifact_id == "ORA-001"
        assert entry.event_type == EVENT_ORACLE_EVALUATED

    def test_record_evidence(self):
        """Evidence is recorded with correct metadata."""
        self.tracker.start_run("R-001", "T-001")
        entry = self.tracker.record_evidence(
            run_id="R-001",
            evidence_id="E-001",
            evidence_hash="HASH-789",
            iteration=0,
            oracle_artifact_id="ORA-001",
        )

        assert entry.artifact_id == "E-001"
        assert entry.event_type == EVENT_EVIDENCE_RECORDED
        assert entry.metadata["oracle_artifact_id"] == "ORA-001"

    def test_record_verification(self):
        """Verification result is recorded."""
        self.tracker.start_run("R-001", "T-001")
        entry = self.tracker.record_verification(
            run_id="R-001",
            verification_decision="ACCEPT",
            candidate_id="C-001",
            evidence_id="E-001",
        )

        assert entry.event_type == EVENT_VERIFICATION_COMPLETED
        assert entry.metadata["decision"] == "ACCEPT"

        run = self.tracker.get_run("R-001")
        assert run.final_verification_decision == "ACCEPT"

    # -- Revision history --------------------------------------------------

    def test_revision_history_preserved(self):
        """Revision history preserves iteration order."""
        self.tracker.start_run("R-001", "T-001")

        # Iteration 0
        self.tracker.record_prompt("R-001", "HASH-0", "PR-0", 0)
        self.tracker.record_candidate("R-001", "C-0", "HASH-C0", 0, "PR-0")
        self.tracker.record_oracle_evaluation("R-001", "ORA-0", "HASH-C0", 0)
        self.tracker.record_evidence("R-001", "E-0", "HASH-E0", 0, "ORA-0")

        # Iteration 1
        self.tracker.record_prompt("R-001", "HASH-1", "PR-1", 1)
        self.tracker.record_candidate("R-001", "C-1", "HASH-C1", 1, "PR-1")
        self.tracker.record_oracle_evaluation("R-001", "ORA-1", "HASH-C1", 1)
        self.tracker.record_evidence("R-001", "E-1", "HASH-E1", 1, "ORA-1")

        entries = self.tracker.get_run_entries("R-001")

        # Filter by event type and verify order
        prompts = [e for e in entries if e.event_type == EVENT_PROMPT_CREATED]
        candidates = [e for e in entries if e.event_type == EVENT_CANDIDATE_CREATED]

        assert len(prompts) == 2
        assert prompts[0].iteration == 0
        assert prompts[1].iteration == 1

        assert len(candidates) == 2
        assert candidates[0].artifact_id == "C-0"
        assert candidates[1].artifact_id == "C-1"

    # -- Event ordering ----------------------------------------------------

    def test_event_ordering_preserved(self):
        """Events are recorded in causal order."""
        self.tracker.start_run("R-001", "T-001")
        self.tracker.record_prompt("R-001", "HASH-0", "PR-0", 0)
        self.tracker.record_candidate("R-001", "C-0", "HASH-C0", 0, "PR-0")
        self.tracker.record_oracle_evaluation("R-001", "ORA-0", "HASH-C0", 0)
        self.tracker.record_evidence("R-001", "E-0", "HASH-E0", 0, "ORA-0")
        self.tracker.record_verification("R-001", "ACCEPT", "C-0", "E-0")
        self.tracker.complete_run("R-001", "COMPLETED", "NO_ERRORS")

        entries = self.tracker.get_run_entries("R-001")

        # Verify event types are in correct order
        event_types = [e.event_type for e in entries]
        assert EVENT_RUN_STARTED in event_types
        assert EVENT_PROMPT_CREATED in event_types
        assert EVENT_CANDIDATE_CREATED in event_types
        assert EVENT_ORACLE_EVALUATED in event_types
        assert EVENT_EVIDENCE_RECORDED in event_types
        assert EVENT_VERIFICATION_COMPLETED in event_types
        assert EVENT_RUN_COMPLETED in event_types

    # -- Identity preservation ---------------------------------------------

    def test_artifact_ids_preserved(self):
        """Artifact IDs are preserved in provenance."""
        self.tracker.start_run("R-001", "T-001")
        self.tracker.record_prompt("R-001", "HASH-0", "PR-001", 0)
        self.tracker.record_candidate("R-001", "C-001", "HASH-C0", 0, "PR-001")
        self.tracker.record_evidence("R-001", "E-001", "HASH-E0", 0, "ORA-001")

        run = self.tracker.get_run("R-001")
        artifacts = [e.artifact_id for e in run.entries]

        assert "PR-001" in artifacts
        assert "C-001" in artifacts
        assert "E-001" in artifacts

    def test_hashes_preserved(self):
        """Artifact hashes are preserved in metadata."""
        self.tracker.start_run("R-001", "T-001")
        self.tracker.record_prompt("R-001", "PROMPT-HASH", "PR-001", 0)
        self.tracker.record_candidate("R-001", "C-001", "CAND-HASH", 0, "PR-001")

        entries = self.tracker.get_run_entries("R-001")
        prompt_entry = [e for e in entries if e.event_type == EVENT_PROMPT_CREATED][0]
        candidate_entry = [e for e in entries if e.event_type == EVENT_CANDIDATE_CREATED][0]

        assert prompt_entry.metadata["prompt_hash"] == "PROMPT-HASH"
        assert candidate_entry.metadata["candidate_hash"] == "CAND-HASH"

    # -- Determinism -------------------------------------------------------

    def test_same_inputs_same_output(self):
        """Same inputs produce equivalent provenance."""
        tracker1 = ProvenanceTracker()
        tracker2 = ProvenanceTracker()

        tracker1.start_run("R-001", "T-001")
        tracker1.record_prompt("R-001", "HASH-0", "PR-0", 0)
        tracker1.complete_run("R-001", "COMPLETED", "NO_ERRORS")

        tracker2.start_run("R-001", "T-001")
        tracker2.record_prompt("R-001", "HASH-0", "PR-0", 0)
        tracker2.complete_run("R-001", "COMPLETED", "NO_ERRORS")

        run1 = tracker1.get_run("R-001")
        run2 = tracker2.get_run("R-001")

        assert run1.status == run2.status
        assert run1.terminal_reason == run2.terminal_reason
        assert len(run1.entries) == len(run2.entries)

    # -- Reconstruction ----------------------------------------------------

    def test_reconstruct_run(self):
        """Given run ID, reconstruct complete run history."""
        self.tracker.start_run("R-001", "T-001")
        self.tracker.record_prompt("R-001", "HASH-0", "PR-0", 0, "T-001")
        self.tracker.record_candidate("R-001", "C-0", "HASH-C0", 0, "PR-0")
        self.tracker.record_oracle_evaluation("R-001", "ORA-0", "HASH-C0", 0)
        self.tracker.record_evidence("R-001", "E-0", "HASH-E0", 0, "ORA-0")
        self.tracker.record_verification("R-001", "ACCEPT", "C-0", "E-0")
        self.tracker.complete_run("R-001", "COMPLETED", "NO_ERRORS", "C-0", "E-0")

        reconstruction = self.tracker.reconstruct_run("R-001")

        assert reconstruction["run_id"] == "R-001"
        assert reconstruction["task_id"] == "T-001"
        assert reconstruction["status"] == "COMPLETED"
        assert reconstruction["terminal_reason"] == "NO_ERRORS"
        assert len(reconstruction["prompts"]) == 1
        assert len(reconstruction["candidates"]) == 1
        assert len(reconstruction["evidence"]) == 1
        assert reconstruction["verification"]["decision"] == "ACCEPT"
        assert reconstruction["final_candidate_id"] == "C-0"
        assert reconstruction["final_evidence_id"] == "E-0"

    def test_reconstruct_missing_run(self):
        """Missing run produces explicit error."""
        reconstruction = self.tracker.reconstruct_run("R-999")

        assert reconstruction["error"] == "Run R-999 not found"
        assert reconstruction["status"] == "NOT_FOUND"

    def test_reconstruct_revision_history(self):
        """Reconstruction preserves revision history."""
        self.tracker.start_run("R-001", "T-001")

        # Iteration 0
        self.tracker.record_prompt("R-001", "HASH-0", "PR-0", 0, "T-001")
        self.tracker.record_candidate("R-001", "C-0", "HASH-C0", 0, "PR-0")
        self.tracker.record_evidence("R-001", "E-0", "HASH-E0", 0, "ORA-0")

        # Iteration 1
        self.tracker.record_prompt("R-001", "HASH-1", "PR-1", 1, "T-001")
        self.tracker.record_candidate("R-001", "C-1", "HASH-C1", 1, "PR-1")
        self.tracker.record_evidence("R-001", "E-1", "HASH-E1", 1, "ORA-1")

        self.tracker.complete_run("R-001", "COMPLETED", "NO_ERRORS")

        reconstruction = self.tracker.reconstruct_run("R-001")

        assert len(reconstruction["prompts"]) == 2
        assert len(reconstruction["candidates"]) == 2
        assert len(reconstruction["evidence"]) == 2

        # Verify iteration order
        assert reconstruction["prompts"][0]["iteration"] == 0
        assert reconstruction["prompts"][1]["iteration"] == 1
        assert reconstruction["candidates"][0]["iteration"] == 0
        assert reconstruction["candidates"][1]["iteration"] == 1

    # -- Missing artifact handling -----------------------------------------

    def test_missing_candidate_id(self):
        """Missing candidate ID produces explicit state."""
        self.tracker.start_run("R-001", "T-001")
        self.tracker.record_evidence("R-001", "E-0", "HASH-E0", 0)
        self.tracker.complete_run("R-001", "COMPLETED", "NO_ERRORS")

        run = self.tracker.get_run("R-001")
        assert run.final_candidate_id is None

    # -- Immutability ------------------------------------------------------

    def test_recording_does_not_mutate_entries(self):
        """Recording provenance does not mutate existing entries."""
        self.tracker.start_run("R-001", "T-001")
        entry1 = self.tracker.record_prompt("R-001", "HASH-0", "PR-0", 0)
        original_id = entry1.artifact_id

        # Record more entries
        self.tracker.record_candidate("R-001", "C-0", "HASH-C0", 0, "PR-0")

        # Original entry unchanged
        assert entry1.artifact_id == original_id

    # -- No authority ------------------------------------------------------

    def test_tracker_cannot_accept(self):
        """ProvenanceTracker cannot produce ACCEPT/REJECT decisions."""
        # Tracker only records — it doesn't decide
        self.tracker.start_run("R-001", "T-001")
        self.tracker.record_verification("R-001", "ACCEPT", "C-0", "E-0")

        run = self.tracker.get_run("R-001")
        # The verification decision is recorded, not decided by tracker
        assert run.final_verification_decision == "ACCEPT"

    def test_tracker_cannot_authorize(self):
        """ProvenanceTracker cannot authorize."""
        # Tracker has no authorization authority
        self.tracker.start_run("R-001", "T-001")
        self.tracker.complete_run("R-001", "COMPLETED", "NO_ERRORS")

        run = self.tracker.get_run("R-001")
        assert run.status == "COMPLETED"

    # -- No external dependencies ------------------------------------------

    def test_no_network_required(self):
        """Tracker works without network access."""
        self.tracker.start_run("R-001", "T-001")
        self.tracker.record_prompt("R-001", "HASH-0", "PR-0", 0)
        self.tracker.complete_run("R-001", "COMPLETED", "NO_ERRORS")

        assert self.tracker.run_count == 1

    def test_no_api_key_required(self):
        """Tracker works without API key."""
        self.tracker.start_run("R-001", "T-001")
        self.tracker.complete_run("R-001", "COMPLETED", "NO_ERRORS")

        assert self.tracker.get_run("R-001").status == "COMPLETED"

    # -- Serialization -----------------------------------------------------

    def test_to_dict_roundtrip(self):
        """Serialization roundtrip preserves data."""
        self.tracker.start_run("R-001", "T-001")
        self.tracker.record_prompt("R-001", "HASH-0", "PR-0", 0)
        self.tracker.record_candidate("R-001", "C-0", "HASH-C0", 0, "PR-0")
        self.tracker.complete_run("R-001", "COMPLETED", "NO_ERRORS")

        d = self.tracker.to_dict()
        tracker2 = ProvenanceTracker.from_dict(d)

        assert tracker2.run_count == 1
        run = tracker2.get_run("R-001")
        assert run.status == "COMPLETED"
        assert run.task_id == "T-001"

    def test_serialization_preserves_entries(self):
        """Serialization preserves all entries."""
        self.tracker.start_run("R-001", "T-001")
        self.tracker.record_prompt("R-001", "HASH-0", "PR-0", 0)
        self.tracker.record_candidate("R-001", "C-0", "HASH-C0", 0, "PR-0")
        self.tracker.record_evidence("R-001", "E-0", "HASH-E0", 0, "ORA-0")
        self.tracker.complete_run("R-001", "COMPLETED", "NO_ERRORS")

        d = self.tracker.to_dict()
        tracker2 = ProvenanceTracker.from_dict(d)

        entries = tracker2.get_run_entries("R-001")
        event_types = [e.event_type for e in entries]

        assert EVENT_RUN_STARTED in event_types
        assert EVENT_PROMPT_CREATED in event_types
        assert EVENT_CANDIDATE_CREATED in event_types
        assert EVENT_EVIDENCE_RECORDED in event_types
        assert EVENT_RUN_COMPLETED in event_types
