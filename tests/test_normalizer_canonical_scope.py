"""EGER P176 — canonical evidence-scope pass-through tests (P175 resolution).

Guards the production change in eger/evidence/normalizer.py _map_scope:

- Canonical scope values (FULL/PARTIAL/INSUFFICIENT/UNSUPPORTED) pass
  through unchanged. The Ṛta adapter stores canonical evidence_scope on its
  EvidenceArtifact; before P175 these normalized to UNSUPPORTED, silently
  forcing every Ṛta evaluation to fail-closed scope at the VerificationGate.
- Raw scope-status vocabulary (VALIDATED, PARTIALLY_VALIDATED,
  NETLIST_REQUIRED, UNSUPPORTED, ...) continues to map per the FROZEN
  raw→canonical _SCOPE_MAP (OpenSTA adapter stores raw "VALIDATED").

No live model calls. No external dependencies. Deterministic.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from eger.evidence.normalizer import EvidenceNormalizer, _map_scope, _SCOPE_MAP


# ---------------------------------------------------------------------------
# Mock Oracle evidence (canonical-scope producer, i.e. the Ṛta adapter)
# ---------------------------------------------------------------------------

@dataclass
class _MockOracleEvidence:
    """Mimics the Ṛta EvidenceOracle EvidenceArtifact (canonical scope)."""
    oracle_status: str = "SUCCESS"
    evidence_scope: Optional[str] = "INSUFFICIENT"
    findings: List[Dict[str, Any]] = field(default_factory=list)
    analysis_scope: Optional[Dict[str, Any]] = None
    artifact_id: str = "ORA-CANON-001"
    provenance: Dict[str, Any] = field(default_factory=dict)


class TestMapScopeCanonicalPassThrough:
    """_map_scope: canonical values pass through unchanged."""

    def test_full_passes_through(self):
        assert _map_scope("FULL") == "FULL"

    def test_partial_passes_through(self):
        assert _map_scope("PARTIAL") == "PARTIAL"

    def test_insufficient_passes_through(self):
        assert _map_scope("INSUFFICIENT") == "INSUFFICIENT"

    def test_unsupported_passes_through(self):
        assert _map_scope("UNSUPPORTED") == "UNSUPPORTED"


class TestMapScopeRawVocabularyUnchanged:
    """_map_scope: raw scope-status vocabulary still maps per frozen _SCOPE_MAP."""

    def test_validated_maps_to_full(self):
        assert _map_scope("VALIDATED") == _SCOPE_MAP["VALIDATED"] == "FULL"

    def test_partially_validated_maps_to_partial(self):
        assert _map_scope("PARTIALLY_VALIDATED") == _SCOPE_MAP["PARTIALLY_VALIDATED"] == "PARTIAL"

    def test_netlist_required_maps_to_insufficient(self):
        assert _map_scope("NETLIST_REQUIRED") == _SCOPE_MAP["NETLIST_REQUIRED"] == "INSUFFICIENT"

    def test_not_validated_maps_to_unsupported(self):
        assert _map_scope("NOT_VALIDATED") == "UNSUPPORTED"

    def test_tcl_execution_required_maps_to_unsupported(self):
        assert _map_scope("TCL_EXECUTION_REQUIRED") == "UNSUPPORTED"

    def test_unknown_maps_to_unsupported(self):
        assert _map_scope("NOT_A_SCOPE") == "UNSUPPORTED"


class TestNormalizeCanonicalScope:
    """EvidenceNormalizer.normalize preserves canonical evidence_scope."""

    def setup_method(self):
        self.normalizer = EvidenceNormalizer()

    def test_canonical_full_survives_normalization(self):
        """A Ṛta adapter artifact with evidence_scope=FULL normalizes to FULL
        (P175 fix — previously remapped to UNSUPPORTED)."""
        evidence = _MockOracleEvidence(
            oracle_status="SUCCESS",
            evidence_scope="FULL",
            analysis_scope={"status": "NETLIST_REQUIRED"},
            provenance={"metadata_validation": {"all_validated": True}},
        )
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.evidence_scope == "FULL"

    def test_canonical_partial_survives_normalization(self):
        evidence = _MockOracleEvidence(
            oracle_status="SUCCESS",
            evidence_scope="PARTIAL",
            analysis_scope={"status": "NETLIST_REQUIRED"},
        )
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.evidence_scope == "PARTIAL"

    def test_canonical_insufficient_survives_normalization(self):
        evidence = _MockOracleEvidence(
            oracle_status="SUCCESS",
            evidence_scope="INSUFFICIENT",
            analysis_scope={"status": "NETLIST_REQUIRED"},
        )
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.evidence_scope == "INSUFFICIENT"

    def test_findings_preserved_under_canonical_scope(self):
        """Findings are untouched by the scope fix."""
        evidence = _MockOracleEvidence(
            oracle_status="SUCCESS",
            evidence_scope="FULL",
            findings=[{
                "finding_id": "F-1", "code": "SDC-005", "severity": "error",
                "message": "No Input Delay", "location": {"line": 1},
            }],
        )
        result = self.normalizer.normalize(evidence, task_id="T-001")
        assert result.evidence_scope == "FULL"
        assert len(result.findings) == 1
        assert result.findings[0].category == "SDC-005"
        assert result.findings[0].severity == "error"
        assert result.has_errors is True
