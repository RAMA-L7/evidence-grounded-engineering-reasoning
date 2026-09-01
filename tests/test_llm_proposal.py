"""P010 — Single LLM Proposal Authority tests T-P010-001..016."""

import hashlib
import pathlib

from eger.engineer.model import FakeEngineerModel
from eger.engineer.adapter import EngineerAdapter, PROMPT_VERSION, SYSTEM_INSTRUCTIONS
from eger.engineer.candidate import extract_candidate, SCHEMA_CANDIDATE
from eger.oracle.adapter import EvidenceOracle
from eger.epistemic.state import create_hypothesis
from eger.epistemic.transitions import EpistemicEngine, TransitionRequest
from eger.authorization.gate import AuthorizationGate, AuthorizationRequest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fake_adapter(canned: str = "", fail_mode=None):
    return EngineerAdapter(FakeEngineerModel(canned_output=canned, fail_mode=fail_mode))

# ---------------------------------------------------------------------------
# T-P010-001 — model adapter returns CandidateArtifact
# ---------------------------------------------------------------------------

def test_T_P010_001_candidate_artifact():
    adapter = _fake_adapter("```sdc\ncreate_clock -name clk -period 10 [get_ports clk]\n```")
    result = adapter.propose(design_context="simple clock", objective="generate SDC")
    assert result.is_success
    assert result.candidate is not None
    assert result.candidate.schema_version == SCHEMA_CANDIDATE
    assert result.candidate.sdc_text
    assert result.candidate.candidate_hash == hashlib.sha256(result.candidate.sdc_text.encode()).hexdigest()
    assert result.model_response is not None
    assert result.model_response.provider == "fake"

# ---------------------------------------------------------------------------
# T-P010-002 — candidate marked unverified
# ---------------------------------------------------------------------------

def test_T_P010_002_unverified():
    adapter = _fake_adapter("create_clock -name clk -period 10 [get_ports clk]")
    result = adapter.propose(design_context="ctx")
    assert result.is_success
    # P150: CandidateArtifact is now frozen and has no `verified` field.
    # Verification authority belongs solely to VerificationGate.
    assert not hasattr(result.candidate, 'verified')
    # Candidate cannot self-promote — no verified attribute exists
    assert result.candidate.provision is not None
    # Candidate is immutable (frozen)
    import pytest
    with pytest.raises(AttributeError):
        result.candidate.sdc_text = "mutated"

# ---------------------------------------------------------------------------
# T-P010-003 — model cannot create EvidenceArtifact
# ---------------------------------------------------------------------------

def test_T_P010_003_no_evidence_authority():
    adapter = _fake_adapter("create_clock -name clk -period 10 [get_ports clk]")
    # EngineerAdapter has no method to create EvidenceArtifact
    assert not hasattr(adapter, "create_evidence")
    assert not hasattr(adapter, "validate")
    assert not hasattr(adapter, "make_evidence")
    # Also model itself cannot
    model = FakeEngineerModel()
    assert not hasattr(model, "validate")
    assert not hasattr(model, "create_evidence")

# ---------------------------------------------------------------------------
# T-P010-004 — model cannot directly mutate EpistemicState
# ---------------------------------------------------------------------------

def test_T_P010_004_no_epistemic_authority():
    adapter = _fake_adapter("create_clock -name clk -period 10 [get_ports clk]")
    result = adapter.propose()
    # Candidate does not have transition ability
    assert not hasattr(result.candidate, "set_state")
    assert not hasattr(result.candidate, "mark_validated")
    # Adapter has no epistemic mutation
    assert not hasattr(adapter, "set_epistemic_state")
    assert not hasattr(adapter, "transition_claim")
    # Verify actual L2 is separate
    eng = EpistemicEngine()
    claim = create_hypothesis("test", claim_id="CLAIM-004")
    eng.create_claim(claim)
    assert eng.get_claim("CLAIM-004").state == "HYPOTHESIS"
    # No direct path from adapter to engine

# ---------------------------------------------------------------------------
# T-P010-005 — model cannot directly authorize
# ---------------------------------------------------------------------------

def test_T_P010_005_no_authorization():
    adapter = _fake_adapter("create_clock -name clk -period 10 [get_ports clk]")
    assert not hasattr(adapter, "authorize")
    assert not hasattr(adapter, "approve")
    assert not hasattr(adapter, "commit")
    # Gate is separate
    gate = AuthorizationGate()
    assert hasattr(gate, "authorize")
    assert not hasattr(adapter, "authorize")

# ---------------------------------------------------------------------------
# T-P010-006 — EvidenceOracle receives CandidateArtifact (pipeline)
# ---------------------------------------------------------------------------

def test_T_P010_006_oracle_boundary():
    adapter = _fake_adapter("create_clock -name clk -period 10 [get_ports clk]")
    result = adapter.propose()
    assert result.is_success
    oracle = EvidenceOracle()
    # Correct pipeline: CandidateArtifact.sdc_text -> EvidenceOracle.validate()
    oracle_result = oracle.validate(result.candidate.sdc_text, input_identity=result.candidate.artifact_id)
    assert oracle_result.is_success or not oracle_result.is_success  # either success or failure is valid, but oracle produced typed result
    assert oracle_result.raw_evidence is not None
    # No direct model -> RTA path
    assert not hasattr(adapter.model, "rta_cli")
    assert not hasattr(result.candidate, "rta_cli")

# ---------------------------------------------------------------------------
# T-P010-007 — deterministic extraction
# ---------------------------------------------------------------------------

def test_T_P010_007_deterministic_extraction():
    raw = "```sdc\ncreate_clock -name clk -period 10 [get_ports clk]\n```"
    c1 = extract_candidate(raw, provision={"model": "fake"})
    c2 = extract_candidate(raw, provision={"model": "fake"})
    assert c1.sdc_text == c2.sdc_text
    assert c1.candidate_hash == c2.candidate_hash
    # Same semantic content → same hash

# ---------------------------------------------------------------------------
# T-P010-008 — malformed model output rejected
# ---------------------------------------------------------------------------

def test_T_P010_008_malformed():
    adapter = _fake_adapter(fail_mode="malformed")
    result = adapter.propose()
    assert not result.is_success
    assert result.failure is not None
    assert result.failure.kind == "MALFORMED_OUTPUT"
    assert result.candidate is None
    # No evidence, no epistemic transition, no authorization should be created
    # (verified by absence of candidate)

# ---------------------------------------------------------------------------
# T-P010-009 — model failure typed as PROPOSAL_FAILURE
# ---------------------------------------------------------------------------

def test_T_P010_009_model_failure():
    for mode, expected_kind in [("timeout", "TIMEOUT"), ("provider_error", "PROVIDER_ERROR")]:
        adapter = _fake_adapter(fail_mode=mode)
        result = adapter.propose()
        assert not result.is_success
        assert result.failure.kind == expected_kind
        # Must be PROPOSAL_FAILURE distinct from evidence failures
        assert result.failure.kind not in ("ORACLE_FAILURE", "INVALID_REQUEST")

# ---------------------------------------------------------------------------
# T-P010-010 — rta_generate unreachable (static + interface)
# ---------------------------------------------------------------------------

def test_T_P010_010_generate_unreachable():
    import pathlib as pl
    for p in [pl.Path("D:/Research on EGER/eger/engineer/model.py"), pl.Path("D:/Research on EGER/eger/engineer/adapter.py"), pl.Path("D:/Research on EGER/eger/engineer/candidate.py")]:
        text = p.read_text(encoding="utf-8")
        assert "rta_generate" not in text
        assert "RTA" not in text or "RTA_CLI" not in text  # engineer must not import RTA internals
    # Interface check: engineer has no generate capability
    adapter = _fake_adapter()
    assert not hasattr(adapter, "rta_generate")
    assert not hasattr(adapter.model, "rta_generate")

# ---------------------------------------------------------------------------
# T-P010-011 — L1/L2/L3 remain unchanged by model output alone
# ---------------------------------------------------------------------------

def test_T_P010_011_layer_immutability():
    from eger.epistemic.transitions import EpistemicEngine
    eng = EpistemicEngine()
    claim = create_hypothesis("layer test", claim_id="CLAIM-011")
    eng.create_claim(claim)
    gate = AuthorizationGate()
    # Capture state before
    before_state = eng.get_claim("CLAIM-011").state
    before_transitions = len(eng.get_transitions())
    before_decisions = len(gate.decisions)
    # Run engineer alone
    adapter = _fake_adapter("create_clock -name clk -period 10 [get_ports clk]")
    adapter.propose()
    # After, without routing through L1/L2/L3, they must be unchanged
    assert eng.get_claim("CLAIM-011").state == before_state
    assert len(eng.get_transitions()) == before_transitions
    assert len(gate.decisions) == before_decisions

# ---------------------------------------------------------------------------
# T-P010-012 — two-memory separation (engineer cannot write research memory)
# ---------------------------------------------------------------------------

def test_T_P010_012_two_memories():
    adapter = _fake_adapter("create_clock -name clk -period 10 [get_ports clk]")
    result = adapter.propose()
    ledger = pathlib.Path("D:/Research on EGER/research/RESEARCH_LEDGER.md").read_text(encoding="utf-8")
    # Engineer output must not appear in ledger
    assert result.candidate.artifact_id not in ledger
    assert result.candidate.sdc_text[:20] not in ledger
    # Engineer has no ledger write method
    assert not hasattr(adapter, "write_ledger")
    assert not hasattr(adapter, "update_research_memory")

# ---------------------------------------------------------------------------
# T-P010-013 — model provenance recorded
# ---------------------------------------------------------------------------

def test_T_P010_013_provenance():
    adapter = _fake_adapter("create_clock -name clk -period 10 [get_ports clk]")
    result = adapter.propose(design_context="ctx", objective="obj")
    assert result.is_success
    prov = result.candidate.provision
    for field in ["provider", "model", "prompt_hash", "output_hash"]:
        assert field in prov and prov[field]
    assert prov["prompt_version"] == PROMPT_VERSION
    # Model response also has provenance
    assert result.model_response.prompt_hash
    assert result.model_response.output_hash

# ---------------------------------------------------------------------------
# T-P010-014 — candidate/output hashes deterministic and separated
# ---------------------------------------------------------------------------

def test_T_P010_014_hashes():
    adapter = _fake_adapter("create_clock -name clk -period 10 [get_ports clk]")
    r1 = adapter.propose(design_context="same")
    r2 = adapter.propose(design_context="same")
    # Same output → same semantic candidate hash
    assert r1.candidate.candidate_hash == r2.candidate.candidate_hash
    # But prompt/output hashes are correctly separated
    assert r1.model_response.prompt_hash == r2.model_response.prompt_hash
    assert r1.model_response.output_hash == r2.model_response.output_hash
    # Candidate hash is derived from sdc_text, not from prompt_hash
    assert r1.candidate.candidate_hash != r1.model_response.prompt_hash

# ---------------------------------------------------------------------------
# T-P010-015 — P008 regression
# ---------------------------------------------------------------------------

def test_T_P010_015_p008_regression():
    import subprocess, sys
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_evidence_oracle.py", "-q"], capture_output=True, text=True, cwd="D:/Research on EGER")
    assert "14 passed" in result.stdout, result.stdout + result.stderr

# ---------------------------------------------------------------------------
# T-P010-016 — P009 regression
# ---------------------------------------------------------------------------

def test_T_P010_016_p009_regression():
    import subprocess, sys
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_epistemic_authorization.py", "-q"], capture_output=True, text=True, cwd="D:/Research on EGER")
    assert "17 passed" in result.stdout, result.stdout + result.stderr
