"""Deterministic EvidenceOracle adapter — P008.

Implements FROZEN contract EGER-ORACLE-CONTRACT-001 and schemas
EGER-SCHEMA-001 against pinned Ṛta revision 3b5c2f2.

Allowed invocation discipline: cwd OUTSIDE Ṛta, PYTHONDONTWRITEBYTECODE=1,
captured stdout/stderr/exit_code, pinned revision in provenance.

ABSOLUTE RULE: This module MUST NEVER invoke the oracle generation
capability on the Evidence path. No code path may reference generation.
(EGER-DEC-006, Rule J)
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from .schemas import (
    SCHEMA_VERSIONS,
    SCOPE_MAP,
    CAPABILITIES,
    evidence_schema as _evidence_schema_fn,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ORACLE_NAME = "Ṛta"
ORACLE_VERSION = "1.5.11"
ORACLE_REVISION = "3b5c2f2"  # pinned for P008 series
RTA_CLI = Path(__file__).resolve().parents[2] / "rta-constraint-intelligence" / "cli.py"

EVIDENCE_SCOPE_VALUES = {"FULL", "PARTIAL", "INSUFFICIENT", "UNSUPPORTED"}
ORACLE_STATUS_VALUES = {"SUCCESS", "INVALID_REQUEST", "ORACLE_FAILURE"}

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class RawEvidence:
    schema_version: str
    raw_id: str
    oracle: Dict[str, str]
    invocation: Dict[str, Any]
    input_hash: str
    raw_bytes: bytes  # kept in memory; file also written if evidence_store given
    raw_hash: str
    exit_code: int
    captured_at: str
    raw_path: Optional[str] = None
    stderr: str = ""


@dataclass
class FindingArtifact:
    finding_id: str
    code: str
    severity: str
    message: str
    location: Dict[str, Any]
    related_location: Optional[Dict[str, Any]]
    context: Optional[Any]
    affected_object: Optional[str]
    finding_identity: Optional[Any]


@dataclass
class AnalysisScope:
    status: str
    normalized_scope: str
    commands_found: int
    fully_analyzed: int
    partially_analyzed: int
    netlist_required: int
    unsupported: int
    tcl_execution_required: Optional[int]
    unknown_options: List[str]
    ignored_options: List[str]
    constructs: List[Dict[str, Any]]


@dataclass
class Provenance:
    oracle_name: str
    oracle_version: str
    oracle_revision: str
    invocation_operation: str
    invocation_args: Dict[str, Any]
    schema_version: str
    input_hash: str
    raw_hash: str
    evidence_hash: str
    produced_at: str
    raw_path: str


@dataclass
class EvidenceArtifact:
    schema_version: str
    artifact_id: str
    oracle: Dict[str, str]
    provenance: Dict[str, Any]
    evidence_scope: Optional[str]
    oracle_status: str
    findings: List[Dict[str, Any]]
    analysis_scope: Optional[Dict[str, Any]]
    raw_ref: Dict[str, str]
    evidence_hash: str
    produced_at: str


@dataclass
class OracleFailure:
    kind: str  # INVALID_REQUEST | ORACLE_FAILURE
    exit_code: int
    message: str
    raw_ref: Optional[Dict[str, str]] = None


@dataclass
class OracleResult:
    """Typed union: either Success(EvidenceArtifact+RawEvidence) or Failure(OracleFailure)."""
    is_success: bool
    evidence: Optional[EvidenceArtifact] = None
    raw_evidence: Optional[RawEvidence] = None
    failure: Optional[OracleFailure] = None


# ---------------------------------------------------------------------------
# Helpers: hashing & canonical JSON
# ---------------------------------------------------------------------------

def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _input_hash(sdc_text: str) -> str:
    return _sha256_hex(sdc_text.encode("utf-8"))


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def _map_scope(raw_status: str) -> str:
    return SCOPE_MAP.get(raw_status, "UNSUPPORTED")


def _normalize_findings(raw_payload: Dict[str, Any], input_hash: str) -> List[Dict[str, Any]]:
    """Collect errors/warnings/info into FindingArtifacts (preserving code/msg/line/line2/context)."""
    findings: List[Dict[str, Any]] = []
    counter = 0
    for bucket, severity in [("errors", "error"), ("warnings", "warning"), ("info", "info")]:
        for item in raw_payload.get(bucket, []) or []:
            counter += 1
            finding_id = f"EGER-FIND-{input_hash[:8]}-{counter:03d}"
            # Preserve identity if present (richer paths); otherwise null — never synthesize from message
            identity = item.get("identity")
            findings.append({
                "finding_id": finding_id,
                "code": item.get("code", ""),
                "severity": item.get("sev") or severity,
                "message": item.get("msg", ""),
                "location": {"line": int(item.get("line", 0) or 0), "col": None},
                "related_location": {"line": int(item.get("line2", 0))} if item.get("line2") else None,
                "context": item.get("context"),
                "affected_object": None,
                "finding_identity": identity,
            })
    return findings


def _normalize_scope(raw_scope: Dict[str, Any]) -> Dict[str, Any]:
    if not raw_scope:
        return None
    status = raw_scope.get("status", "NOT_VALIDATED")
    return {
        "status": status,
        "normalized_scope": _map_scope(status),
        "commands_found": int(raw_scope.get("commands_found", 0) or 0),
        "fully_analyzed": int(raw_scope.get("fully_analyzed", 0) or 0),
        "partially_analyzed": int(raw_scope.get("partially_analyzed", 0) or 0),
        "netlist_required": int(raw_scope.get("netlist_required", 0) or 0),
        "unsupported": int(raw_scope.get("unsupported", 0) or 0),
        "tcl_execution_required": raw_scope.get("tcl_execution_required"),
        "unknown_options": list(raw_scope.get("unknown_options", []) or []),
        "ignored_options": list(raw_scope.get("ignored_options", []) or []),
        "constructs": list(raw_scope.get("constructs", []) or []),
    }


# ---------------------------------------------------------------------------
# EvidenceOracle
# ---------------------------------------------------------------------------

class EvidenceOracle:
    """Deterministic adapter. No LLM, no epistemic state, no authorization."""

    def __init__(self, rta_cli: Optional[Path] = None, oracle_revision: str = ORACLE_REVISION):
        self.rta_cli = Path(rta_cli) if rta_cli else RTA_CLI
        self.oracle_revision = oracle_revision

    # -- public API -------------------------------------------------------

    def capabilities(self) -> Dict[str, Any]:
        """Declarative capability descriptor (FROZEN per contract §7)."""
        return {
            "oracle": {"name": ORACLE_NAME, "version": ORACLE_VERSION, "revision": self.oracle_revision},
            "capabilities": dict(CAPABILITIES),
            "scope_vocabulary": sorted(SCOPE_MAP.keys()),
            "normalized_scope_values": sorted(EVIDENCE_SCOPE_VALUES),
            "exit_code_semantics": {
                "0": "SUCCESS — evidence produced (may contain warnings)",
                "1": "SUCCESS — evidence produced with validation findings",
                "2": "INVALID_REQUEST — documented, PROVISIONAL (not runtime-triggered in P006)",
                "3": "ORACLE_FAILURE — documented, PROVISIONAL",
            },
            "schema_versions": dict(SCHEMA_VERSIONS),
        }

    def evidence_schema(self) -> Dict[str, Any]:
        return _evidence_schema_fn()

    def validate(
        self,
        sdc_text: str,
        input_identity: str = "candidate",
        invocation_options: Optional[Dict[str, Any]] = None,
        evidence_store: Optional[Path] = None,
    ) -> OracleResult:
        """Validate one candidate SDC text.

        - Writes sdc_text to a temp file OUTSIDE Ṛta.
        - Invokes: python <RTA_CLI> check <file> --json  (cwd outside Ṛta, PYTHONDONTWRITEBYTECODE=1)
        - Captures RawEvidence and deterministically normalizes to EvidenceArtifact.
        """
        invocation_options = invocation_options or {}
        input_h = _input_hash(sdc_text)
        produced_at = datetime.now(timezone.utc).isoformat()

        # -- invoke RTA ---------------------------------------------------
        # Early check: missing oracle binary is ORACLE_FAILURE, not INVALID_REQUEST
        if not self.rta_cli.exists():
            raw_bytes = b""
            stderr_text = f"oracle not found: {self.rta_cli}"
            exit_code = 127
            # Build a minimal RawEvidence for provenance then return failure directly
            raw_hash_tmp = _sha256_hex(raw_bytes)
            raw_id_tmp = f"EGER-RAW-{input_h[:12]}"
            raw_path_tmp = f"<memory>/{raw_id_tmp}.json"
            raw_evidence_tmp = RawEvidence(
                schema_version=SCHEMA_VERSIONS["raw"],
                raw_id=raw_id_tmp,
                oracle={"name": ORACLE_NAME, "version": ORACLE_VERSION, "revision": self.oracle_revision},
                invocation={
                    "operation": "validate",
                    "args": {"input_identity": input_identity, **invocation_options},
                    "schema_version": SCHEMA_VERSIONS["evidence"],
                    "cli": "check --json (exit 127)",
                },
                input_hash=input_h,
                raw_bytes=raw_bytes,
                raw_hash=raw_hash_tmp,
                exit_code=exit_code,
                captured_at=produced_at,
                raw_path=raw_path_tmp,
                stderr=stderr_text,
            )
            return OracleResult(
                is_success=False,
                raw_evidence=raw_evidence_tmp,
                failure=OracleFailure(kind="ORACLE_FAILURE", exit_code=exit_code, message=stderr_text, raw_ref={"raw_id": raw_id_tmp, "raw_hash": raw_hash_tmp}),
            )

        raw_bytes, stderr_text, exit_code = self._invoke_rta(sdc_text)

        raw_hash = _sha256_hex(raw_bytes)
        raw_id = f"EGER-RAW-{input_h[:12]}"
        artifact_id = f"EGER-EVID-{input_h[:12]}"

        invocation = {
            "operation": "validate",
            "args": {"input_identity": input_identity, **invocation_options},
            "schema_version": SCHEMA_VERSIONS["evidence"],
            "cli": f"check --json (exit {exit_code})",
        }

        # Optionally persist raw evidence outside Ṛta
        raw_path: Optional[str] = None
        if evidence_store is not None:
            store = Path(evidence_store)
            store.mkdir(parents=True, exist_ok=True)
            raw_path = str(store / f"{raw_id}.json")
            # Write raw bytes deterministically (no extra metadata)
            Path(raw_path).write_bytes(raw_bytes)
        else:
            # Still produce a deterministic path string for provenance even if not written
            raw_path = f"<memory>/{raw_id}.json"

        raw_evidence = RawEvidence(
            schema_version=SCHEMA_VERSIONS["raw"],
            raw_id=raw_id,
            oracle={"name": ORACLE_NAME, "version": ORACLE_VERSION, "revision": self.oracle_revision},
            invocation=invocation,
            input_hash=input_h,
            raw_bytes=raw_bytes,
            raw_hash=raw_hash,
            exit_code=exit_code,
            captured_at=produced_at,
            raw_path=raw_path,
            stderr=stderr_text,
        )

        # -- classify exit code ------------------------------------------
        if exit_code in (0, 1):
            return self._build_success(raw_evidence, input_h, artifact_id, produced_at, invocation)
        elif exit_code == 2:
            # Exit 2 is documented as INVALID_REQUEST, but only when the oracle
            # actually produced structured output. If raw output is not valid
            # evidence (e.g. missing file, no JSON), treat as ORACLE_FAILURE.
            try:
                payload = json.loads(raw_bytes.decode("utf-8"))
                if isinstance(payload, dict) and "analysis_scope" in payload:
                    return OracleResult(
                        is_success=False,
                        raw_evidence=raw_evidence,
                        failure=OracleFailure(kind="INVALID_REQUEST", exit_code=exit_code, message=stderr_text or "invalid request (exit 2)", raw_ref={"raw_id": raw_id, "raw_hash": raw_hash}),
                    )
            except Exception:
                pass
            return OracleResult(
                is_success=False,
                raw_evidence=raw_evidence,
                failure=OracleFailure(kind="ORACLE_FAILURE", exit_code=exit_code, message=stderr_text or "oracle failure (exit 2 — no valid evidence)", raw_ref={"raw_id": raw_id, "raw_hash": raw_hash}),
            )
        elif exit_code == 3:
            return OracleResult(
                is_success=False,
                raw_evidence=raw_evidence,
                failure=OracleFailure(kind="ORACLE_FAILURE", exit_code=exit_code, message=stderr_text or "oracle failure (exit 3)", raw_ref={"raw_id": raw_id, "raw_hash": raw_hash}),
            )
        else:
            # Unknown non-zero -> treat as ORACLE_FAILURE (failure containment)
            # But if raw_bytes is valid JSON with evidence, prefer SUCCESS path?
            # Conservative: treat as failure to avoid silent promotion.
            try:
                payload = json.loads(raw_bytes.decode("utf-8"))
                if isinstance(payload, dict) and "analysis_scope" in payload:
                    return self._build_success(raw_evidence, input_h, artifact_id, produced_at, invocation)
            except Exception:
                pass
            return OracleResult(
                is_success=False,
                raw_evidence=raw_evidence,
                failure=OracleFailure(kind="ORACLE_FAILURE", exit_code=exit_code, message=stderr_text or f"oracle failure (exit {exit_code})", raw_ref={"raw_id": raw_id, "raw_hash": raw_hash}),
            )

    # -- internal ---------------------------------------------------------

    def _invoke_rta(self, sdc_text: str):
        # Deterministic invocation: file path derived from input hash so that
        # the oracle's "file" field in raw JSON is deterministic. This preserves
        # byte-identical evidence for identical inputs (P006 EVID-005) and keeps
        # evidence_hash stable. Still OUTSIDE Ṛta.
        input_h = _input_hash(sdc_text)
        base_tmp = Path(tempfile.gettempdir()) / f"eger_oracle_{input_h[:12]}"
        base_tmp.mkdir(parents=True, exist_ok=True)
        candidate_path = base_tmp / "candidate.sdc"
        candidate_path.write_text(sdc_text, encoding="utf-8")

        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        cmd = [sys.executable, str(self.rta_cli), "check", str(candidate_path), "--json"]
        result = subprocess.run(
            cmd,
            cwd=str(base_tmp),
            capture_output=True,
            env=env,
        )
        stdout = result.stdout or b""
        stderr = (result.stderr or b"").decode("utf-8", errors="replace")
        exit_code = int(result.returncode)

        # Clean up candidate file but keep deterministic dir (empty) for reuse;
        # do not leave candidate content behind.
        try:
            candidate_path.unlink(missing_ok=True)
            # Remove dir only if empty and not reused concurrently
            try:
                base_tmp.rmdir()
            except OSError:
                pass
        except Exception:
            pass

        return stdout, stderr, exit_code

    def _build_success(self, raw_evidence: RawEvidence, input_h: str, artifact_id: str, produced_at: str, invocation: Dict[str, Any]) -> OracleResult:
        try:
            payload = json.loads(raw_evidence.raw_bytes.decode("utf-8"))
        except Exception as exc:
            return OracleResult(
                is_success=False,
                raw_evidence=raw_evidence,
                failure=OracleFailure(kind="ORACLE_FAILURE", exit_code=raw_evidence.exit_code, message=f"raw output not valid JSON: {exc}", raw_ref={"raw_id": raw_evidence.raw_id, "raw_hash": raw_evidence.raw_hash}),
            )

        findings = _normalize_findings(payload, input_h)
        analysis_scope = _normalize_scope(payload.get("analysis_scope") or {})
        evidence_scope = _map_scope(analysis_scope.get("status", "NOT_VALIDATED")) if analysis_scope else "UNSUPPORTED"

        # Build normalized evidence dict for hashing (excluding produced_at)
        evidence_dict_for_hash = {
            "schema_version": SCHEMA_VERSIONS["evidence"],
            "artifact_id": artifact_id,
            "oracle": {"name": ORACLE_NAME, "version": ORACLE_VERSION, "revision": self.oracle_revision},
            "evidence_scope": evidence_scope,
            "oracle_status": "SUCCESS",
            "findings": findings,
            "analysis_scope": analysis_scope,
            "raw_ref": {"raw_id": raw_evidence.raw_id, "raw_hash": raw_evidence.raw_hash},
            "input_hash": input_h,
        }
        evidence_hash = _sha256_hex(_canonical_json(evidence_dict_for_hash))

        provenance = {
            "oracle_name": ORACLE_NAME,
            "oracle_version": ORACLE_VERSION,
            "oracle_revision": self.oracle_revision,
            "invocation_operation": "validate",
            "invocation_args": invocation["args"],
            "schema_version": SCHEMA_VERSIONS["evidence"],
            "input_hash": input_h,
            "raw_hash": raw_evidence.raw_hash,
            "evidence_hash": evidence_hash,
            "produced_at": produced_at,
            "raw_path": raw_evidence.raw_path,
        }

        artifact = EvidenceArtifact(
            schema_version=SCHEMA_VERSIONS["evidence"],
            artifact_id=artifact_id,
            oracle={"name": ORACLE_NAME, "version": ORACLE_VERSION, "revision": self.oracle_revision},
            provenance=provenance,
            evidence_scope=evidence_scope,
            oracle_status="SUCCESS",
            findings=findings,
            analysis_scope=analysis_scope,
            raw_ref={"raw_id": raw_evidence.raw_id, "raw_hash": raw_evidence.raw_hash},
            evidence_hash=evidence_hash,
            produced_at=produced_at,
        )

        return OracleResult(is_success=True, evidence=artifact, raw_evidence=raw_evidence)
