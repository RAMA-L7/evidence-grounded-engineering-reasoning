"""P009 deterministic L2/L3 tests — T-E001..T-E016."""

import hashlib
import json
import pathlib
from eger.epistemic.state import create_hypothesis, VALID_STATES, SCHEMA_EPISTEMIC
from eger.epistemic.transitions import EpistemicEngine, TransitionRequest
from eger.authorization.gate import AuthorizationGate, AuthorizationRequest
from eger.oracle.adapter import EvidenceOracle
from eger.oracle.schemas import SCHEMA_VERSIONS

# ---------------------------------------------------------------------------
# Helpers: mock evidence (deterministic, no RTA call needed for most tests)
# ---------------------------------------------------------------------------

def _mock_evidence(scope: str, has_error: bool = False, evidence_hash: str = None, oracle_status: str = "SUCCESS"):
    """Create minimal EvidenceArtifact-like object for engine tests."""
    h = evidence_hash or hashlib.sha256(scope.encode()).hexdigest()
    findings = []
    if has_error:
        findings = [{"finding_id": "EGER-FIND-001", "code": "SDC-002", "severity": "error", "message": "mock error", "location": {"line": 1}}]
    # Minimal EvidenceArtifact-like namespace
    class Ev:
        pass
    ev = Ev()
    ev.evidence_scope = scope
    ev.oracle_status = oracle_status
    ev.findings = findings
    ev.evidence_hash = h
    ev.analysis_scope = {"status": {"FULL":"VALIDATED","PARTIAL":"PARTIALLY_VALIDATED","INSUFFICIENT":"NETLIST_REQUIRED","UNSUPPORTED":"UNSUPPORTED"}[scope]}
    return ev

def _mock_failure(kind="ORACLE_FAILURE"):
    class Fail:
        pass
    f = Fail()
    f.kind = kind
    f.evidence_scope = None
    f.oracle_status = kind
    f.findings = []
    f.evidence_hash = hashlib.sha256(kind.encode()).hexdigest()
    return f

# Use real oracle for one integration path to ensure no EvidenceOracle modification
REAL_ORACLE = EvidenceOracle()
REAL_MINIMAL_SDC = pathlib.Path("D:/Research on EGER/rta-constraint-intelligence/samples/minimal_sdc.sdc").read_text(encoding="utf-8", errors="replace")
REAL_MALFORMED_SDC = pathlib.Path("D:/Research on EGER/rta-constraint-intelligence/samples/edge_case_malformed.sdc").read_text(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# T-E001 — initial hypothesis
# ---------------------------------------------------------------------------

def test_T_E001_initial_hypothesis():
    eng = EpistemicEngine()
    claim = create_hypothesis("SDC candidate X is valid", claim_id="CLAIM-T-E001")
    eng.create_claim(claim)
    stored = eng.get_claim("CLAIM-T-E001")
    assert stored.state == "HYPOTHESIS"
    assert stored.supporting_evidence_ids == []
    assert stored.schema_version == SCHEMA_EPISTEMIC
    # no authorization exists yet (gate not invoked)

# ---------------------------------------------------------------------------
# T-E002 — validated with sufficient evidence (FULL, no errors)
# ---------------------------------------------------------------------------

def test_T_E002_validated():
    eng = EpistemicEngine()
    claim = create_hypothesis("valid SDC", claim_id="CLAIM-T-E002")
    eng.create_claim(claim)
    ev = _mock_evidence("FULL", has_error=False, evidence_hash="a"*64)
    res = eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E002", target_state="VALIDATED", evidence=ev, evidence_ids=["EVID-a"], reason="sufficient evidence"))
    assert res.accepted, res.reason
    assert eng.get_claim("CLAIM-T-E002").state == "VALIDATED"
    assert res.transition is not None
    assert res.transition.evidence_ids == ["EVID-a"]

# ---------------------------------------------------------------------------
# T-E003 — refuted with contradictory evidence
# ---------------------------------------------------------------------------

def test_T_E003_refuted():
    eng = EpistemicEngine()
    claim = create_hypothesis("invalid SDC", claim_id="CLAIM-T-E003")
    eng.create_claim(claim)
    ev = _mock_evidence("FULL", has_error=True, evidence_hash="b"*64)
    res = eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E003", target_state="REFUTED", evidence=ev, evidence_ids=["EVID-b"], reason="error findings"))
    assert res.accepted
    assert eng.get_claim("CLAIM-T-E003").state == "REFUTED"
    assert eng.get_claim("CLAIM-T-E003").contradicting_evidence_ids == ["EVID-b"]

# ---------------------------------------------------------------------------
# T-E004 — insufficient evidence remains unknown (HYPOTHESIS -> UNKNOWN)
# ---------------------------------------------------------------------------

def test_T_E004_insufficient():
    eng = EpistemicEngine()
    claim = create_hypothesis("needs netlist", claim_id="CLAIM-T-E004")
    eng.create_claim(claim)
    ev = _mock_evidence("INSUFFICIENT", has_error=False, evidence_hash="c"*64)
    # Attempt VALIDATED must be rejected
    res_fail = eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E004", target_state="VALIDATED", evidence=ev, evidence_ids=["EVID-c"]))
    assert not res_fail.accepted
    assert res_fail.violation is not None
    assert eng.get_claim("CLAIM-T-E004").state == "HYPOTHESIS"  # unchanged
    # Transition to UNKNOWN should succeed
    res_unknown = eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E004", target_state="UNKNOWN", evidence=ev, evidence_ids=["EVID-c"]))
    assert res_unknown.accepted
    assert eng.get_claim("CLAIM-T-E004").state == "UNKNOWN"

# ---------------------------------------------------------------------------
# T-E005 — oracle failure cannot validate
# ---------------------------------------------------------------------------

def test_T_E005_oracle_failure():
    eng = EpistemicEngine()
    claim = create_hypothesis("oracle broke", claim_id="CLAIM-T-E005")
    eng.create_claim(claim)
    fail = _mock_failure("ORACLE_FAILURE")
    res = eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E005", target_state="VALIDATED", evidence=fail, evidence_ids=["EVID-fail"]))
    assert not res.accepted
    assert res.violation.violation_type == "ORACLE_FAILURE"

# ---------------------------------------------------------------------------
# T-E006 — unsupported cannot validate
# ---------------------------------------------------------------------------

def test_T_E006_unsupported():
    eng = EpistemicEngine()
    claim = create_hypothesis("unsupported construct", claim_id="CLAIM-T-E006")
    eng.create_claim(claim)
    ev = _mock_evidence("UNSUPPORTED", evidence_hash="d"*64)
    res = eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E006", target_state="VALIDATED", evidence=ev, evidence_ids=["EVID-d"]))
    assert not res.accepted
    assert res.violation.violation_type == "UNSUPPORTED_SCOPE"

# ---------------------------------------------------------------------------
# T-E007 — missing evidence rejected, violation detectable
# ---------------------------------------------------------------------------

def test_T_E007_missing_evidence():
    eng = EpistemicEngine()
    claim = create_hypothesis("no evidence", claim_id="CLAIM-T-E007")
    eng.create_claim(claim)
    res = eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E007", target_state="VALIDATED", evidence=None, evidence_ids=[]))
    assert not res.accepted
    assert res.violation is not None
    assert res.violation.violation_type == "NO_EVIDENCE_TO_VALIDATED"

# ---------------------------------------------------------------------------
# T-E008 — REFUTED -> VALIDATED requires new evidence
# ---------------------------------------------------------------------------

def test_T_E008_refuted_to_validated():
    eng = EpistemicEngine()
    claim = create_hypothesis("re-validate", claim_id="CLAIM-T-E008")
    eng.create_claim(claim)
    # First refute
    ev_refute = _mock_evidence("FULL", has_error=True, evidence_hash="e1"*32)
    r1 = eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E008", target_state="REFUTED", evidence=ev_refute, evidence_ids=["EVID-e1"]))
    assert r1.accepted
    # Attempt without new evidence -> rejected
    ev_same = _mock_evidence("FULL", has_error=False, evidence_hash="e1"*32)  # same hash as refuting
    # Use same evidence_ids as before
    r2 = eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E008", target_state="VALIDATED", evidence=ev_same, evidence_ids=["EVID-e1"]))
    assert not r2.accepted
    assert r2.violation.violation_type == "REFUTED_TO_VALIDATED_WITHOUT_NEW_EVIDENCE"
    # With new evidence -> accepted
    ev_new = _mock_evidence("FULL", has_error=False, evidence_hash="e2"*32)
    r3 = eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E008", target_state="VALIDATED", evidence=ev_new, evidence_ids=["EVID-e2"]))
    assert r3.accepted
    assert eng.get_claim("CLAIM-T-E008").state == "VALIDATED"

# ---------------------------------------------------------------------------
# T-E009 — validated immutability (baseline cannot be silently replaced)
# ---------------------------------------------------------------------------

def test_T_E009_validated_immutability():
    eng = EpistemicEngine()
    claim = create_hypothesis("baseline", claim_id="CLAIM-T-E009")
    eng.create_claim(claim)
    ev1 = _mock_evidence("FULL", has_error=False, evidence_hash="f1"*32)
    r1 = eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E009", target_state="VALIDATED", evidence=ev1, evidence_ids=["EVID-f1"]))
    assert r1.accepted
    baseline = eng.get_claim("CLAIM-T-E009").baseline_evidence_hash
    assert baseline == "f1"*32
    # Attempt to replace with insufficient evidence while staying VALIDATED -> rejected
    ev_ins = _mock_evidence("INSUFFICIENT", evidence_hash="f2"*32)
    r2 = eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E009", target_state="VALIDATED", evidence=ev_ins, evidence_ids=["EVID-f2"]))
    assert not r2.accepted
    assert r2.violation.violation_type == "BASELINE_REPLACEMENT"
    assert eng.get_claim("CLAIM-T-E009").baseline_evidence_hash == baseline  # unchanged

# ---------------------------------------------------------------------------
# T-E010 — deterministic transition (same inputs -> same decision)
# ---------------------------------------------------------------------------

def test_T_E010_deterministic():
    def run_once():
        eng = EpistemicEngine()
        claim = create_hypothesis("deterministic", claim_id="CLAIM-T-E010")
        eng.create_claim(claim)
        ev = _mock_evidence("FULL", has_error=False, evidence_hash="g"*64)
        return eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E010", target_state="VALIDATED", evidence=ev, evidence_ids=["EVID-g"]))
    r1 = run_once()
    r2 = run_once()
    assert r1.accepted == r2.accepted == True
    assert r1.reason == r2.reason

# ---------------------------------------------------------------------------
# T-E011 — authorization approved
# ---------------------------------------------------------------------------

def test_T_E011_authorization_approved():
    eng = EpistemicEngine()
    claim = create_hypothesis("for commit", claim_id="CLAIM-T-E011")
    eng.create_claim(claim)
    ev = _mock_evidence("FULL", has_error=False, evidence_hash="h"*64)
    eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E011", target_state="VALIDATED", evidence=ev, evidence_ids=["EVID-h"]))
    gate = AuthorizationGate()
    req = AuthorizationRequest(request_id="REQ-011", claim_id="CLAIM-T-E011", proposed_action="commit", epistemic_state="VALIDATED", evidence_ids=["EVID-h"], evidence_scope="FULL", oracle_status="SUCCESS")
    dec = gate.authorize(req)
    assert dec.decision == "APPROVED"

# ---------------------------------------------------------------------------
# T-E012 — authorization rejected
# ---------------------------------------------------------------------------

def test_T_E012_authorization_rejected():
    gate = AuthorizationGate()
    # HYPOTHESIS state should be rejected for commit
    req = AuthorizationRequest(request_id="REQ-012", claim_id="CLAIM-T-E012", proposed_action="commit", epistemic_state="HYPOTHESIS", evidence_ids=[], evidence_scope="INSUFFICIENT", oracle_status="SUCCESS")
    dec = gate.authorize(req)
    assert dec.decision == "REJECTED"

# ---------------------------------------------------------------------------
# T-E013 — authorization cannot override evidence (INSUFFICIENT -> APPROVED must fail)
# ---------------------------------------------------------------------------

def test_T_E013_no_override():
    eng = EpistemicEngine()
    claim = create_hypothesis("insufficient for auth", claim_id="CLAIM-T-E013")
    eng.create_claim(claim)
    ev = _mock_evidence("INSUFFICIENT", evidence_hash="i"*64)
    # Engine will be UNKNOWN, not VALIDATED
    eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E013", target_state="UNKNOWN", evidence=ev, evidence_ids=["EVID-i"]))
    gate = AuthorizationGate()
    # Attempt to authorize commit despite INSUFFICIENT scope
    req = AuthorizationRequest(request_id="REQ-013", claim_id="CLAIM-T-E013", proposed_action="commit", epistemic_state="UNKNOWN", evidence_ids=["EVID-i"], evidence_scope="INSUFFICIENT", oracle_status="SUCCESS")
    dec = gate.authorize(req)
    assert dec.decision == "REJECTED"
    # Even if someone force-approves, violation recorded
    gate2 = AuthorizationGate()
    gate2.authorize_or_record_violation(req, force_approve=True)
    assert len(gate2.violations) == 1

# ---------------------------------------------------------------------------
# T-E014 — two memories separate
# ---------------------------------------------------------------------------

def test_T_E014_two_memories():
    # Engineering memory is EpistemicEngine; research memory is research/RESEARCH_LEDGER.md — they must not mix.
    # Verify engineering state never writes to research ledger path, and no ledger entry becomes a claim.
    import pathlib
    eng = EpistemicEngine()
    claim = create_hypothesis("engineering fact", claim_id="CLAIM-T-E014")
    eng.create_claim(claim)
    # Research ledger path should not be touched by engine
    ledger = pathlib.Path("D:/Research on EGER/research/RESEARCH_LEDGER.md")
    # Ensure ledger does not contain this claim id
    assert "CLAIM-T-E014" not in ledger.read_text(encoding="utf-8")
    # And engineering store does not contain ledger content
    assert ledger.read_text(encoding="utf-8") not in str(eng.claims)

# ---------------------------------------------------------------------------
# T-E015 — schema compliance
# ---------------------------------------------------------------------------

def test_T_E015_schema_compliance():
    from eger.epistemic.state import SCHEMA_EPISTEMIC, SCHEMA_TRANSITION
    from eger.authorization.gate import SCHEMA_AUTH_REQUEST, SCHEMA_AUTH_DECISION
    assert SCHEMA_EPISTEMIC == "eger.epistemic.v1"
    assert SCHEMA_TRANSITION == "eger.transition.v1"
    assert SCHEMA_AUTH_REQUEST == "eger.authorization.request.v1"
    assert SCHEMA_AUTH_DECISION == "eger.authorization.decision.v1"
    # Claim has required fields
    claim = create_hypothesis("schema", claim_id="CLAIM-T-E015")
    assert claim.schema_version == SCHEMA_EPISTEMIC
    assert claim.claim_id and claim.proposition and claim.state
    # Transition has schema
    eng = EpistemicEngine()
    eng.create_claim(claim)
    ev = _mock_evidence("FULL", has_error=False, evidence_hash="j"*64)
    res = eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E015", target_state="VALIDATED", evidence=ev, evidence_ids=["EVID-j"]))
    assert res.transition.schema_version == SCHEMA_TRANSITION

# ---------------------------------------------------------------------------
# T-E016 — epistemic violation detection (machine-readable)
# ---------------------------------------------------------------------------

def test_T_E016_violation_detection():
    eng = EpistemicEngine()
    claim = create_hypothesis("violations", claim_id="CLAIM-T-E016")
    eng.create_claim(claim)
    # Trigger several violations
    eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E016", target_state="VALIDATED", evidence=None, evidence_ids=[]))
    eng.request_transition(TransitionRequest(claim_id="CLAIM-T-E016", target_state="VALIDATED", evidence=_mock_evidence("INSUFFICIENT"), evidence_ids=["EVID-x"]))
    violations = eng.get_violations()
    assert len(violations) >= 2
    assert all(v.violation_type for v in violations)
    assert all(v.detected_at for v in violations)
    # EVR raw counts available
    evr = eng.evr()
    assert "attempted_transitions" in evr and "violations" in evr and "evr" in evr
    assert evr["violations"] == len(violations)

# ---------------------------------------------------------------------------
# Real oracle integration sanity (ensures EvidenceOracle not modified)
# ---------------------------------------------------------------------------

def test_real_oracle_still_works():
    result = REAL_ORACLE.validate(REAL_MINIMAL_SDC, input_identity="REAL-INTEGRATION")
    assert result.is_success
    assert result.evidence.evidence_scope in {"FULL", "PARTIAL", "INSUFFICIENT", "UNSUPPORTED"}
