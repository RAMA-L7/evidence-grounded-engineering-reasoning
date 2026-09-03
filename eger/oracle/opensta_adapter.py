"""OpenSTA Oracle Adapter — connects OpenSTA timing analysis to EGER evidence pipeline.

P164: Implements a minimal adapter that invokes OpenSTA v2.2.0, parses timing
reports, and maps findings into the existing EGER EvidenceArtifact contract.

P166: Added design_name validation to prevent Tcl command injection.

Architecture:
    EGER Task
       ↓
    OpenSTAAdapter.validate(sdc_text, netlist_path, lib_path)
       ↓
    OpenSTA (subprocess via WSL2)
       ↓
    OracleResult (success with EvidenceArtifact | failure with OracleFailure)

INVARIANT: Same inputs → same OracleResult (deterministic).
INVARIANT: Adapter cannot invent findings.
INVARIANT: Adapter cannot reinterpret Oracle truth.
INVARIANT: Adapter cannot decide ACCEPT/REJECT.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from .adapter import (
    OracleResult,
    OracleFailure,
    EvidenceArtifact,
    RawEvidence,
    _sha256_hex,
    _canonical_json,
    _input_hash,
    SCHEMA_VERSIONS,
)
from .schemas import SCOPE_MAP

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OPENSTA_ORACLE_NAME = "OpenSTA"
OPENSTA_ORACLE_VERSION = "2.2.0"
OPENSTA_ORACLE_REVISION = "02b129d48fbefb57d08f4bc412700ddfa24a159b"

# Default OpenSTA executable path (WSL2 Ubuntu 24.04, WSL-internal path)
DEFAULT_OPENSTA_BINARY = Path.home() / "opensta_build" / "OpenSTA" / "app" / "sta"

DEFAULT_OPENSTA_TIMEOUT_SECONDS = 60
MINIMUM_OPENSTA_TIMEOUT_SECONDS = 1

# Exit code semantics for OpenSTA
# 0 = success (analysis completed)
# non-zero = failure (various reasons)
OPENSTA_EXIT_SUCCESS = 0

# P166: design_name validation contract
# Valid Verilog module/cell names: start with letter or underscore,
# contain only alphanumeric characters, underscores, and forward slashes
# (for hierarchical names like top/sub/leaf).
# This prevents Tcl command injection via semicolons, brackets, $, etc.
_DESIGN_NAME_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_/]*$")
MAX_DESIGN_NAME_LENGTH = 256


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class TimingFinding:
    """A single timing finding parsed from OpenSTA output."""
    finding_id: str
    severity: str  # "error" | "warning" | "info"
    category: str  # "setup_violation" | "hold_violation" | "timing_clean" | ...
    entity: str  # path description
    message: str
    slack: Optional[float] = None
    path_group: Optional[str] = None
    path_type: Optional[str] = None  # "max" | "min"


@dataclass
class TimingReport:
    """Parsed timing report from OpenSTA."""
    wns: Optional[float] = None
    tns: Optional[float] = None
    findings: List[TimingFinding] = field(default_factory=list)
    raw_output: str = ""
    has_violations: bool = False


# ---------------------------------------------------------------------------
# P166: design_name validation
# ---------------------------------------------------------------------------

def _validate_design_name(design_name: str) -> Optional[str]:
    """Validate design_name against the safe identifier contract.

    Valid names match: ^[a-zA-Z_][a-zA-Z0-9_/]*$
    Maximum length: 256 characters.

    This prevents Tcl command injection by rejecting names containing
    semicolons, brackets, dollar signs, backticks, quotes, braces,
    newlines, or other Tcl metacharacters.

    Returns:
        None if valid, or an error message string if invalid.
    """
    if not design_name:
        return "design_name must not be empty"
    if len(design_name) > MAX_DESIGN_NAME_LENGTH:
        return f"design_name must not exceed {MAX_DESIGN_NAME_LENGTH} characters"
    if not _DESIGN_NAME_RE.match(design_name):
        return (
            f"design_name contains invalid characters: {design_name!r}. "
            f"Valid names match [a-zA-Z_][a-zA-Z0-9_/]* (Verilog identifier "
            f"with optional hierarchical / separators)"
        )
    return None


# ---------------------------------------------------------------------------
# Output parser
# ---------------------------------------------------------------------------

def _parse_wns_tns(text: str) -> Tuple[Optional[float], Optional[float]]:
    """Extract WNS and TNS from OpenSTA output."""
    wns = None
    tns = None
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"^wns\s+([-\d.]+)$", line)
        if m:
            wns = float(m.group(1))
        m = re.match(r"^tns\s+([-\d.]+)$", line)
        if m:
            tns = float(m.group(1))
    return wns, tns


def _parse_slack_from_report(text: str) -> Optional[float]:
    """Extract slack value from report_checks output."""
    for line in text.splitlines():
        line = line.strip()
        # Match lines like "           9.85   slack (MET)"
        m = re.match(r"^([-\d.]+)\s+slack\s+\((\w+)\)$", line)
        if m:
            return float(m.group(1))
    return None


def _parse_timing_report(output: str) -> TimingReport:
    """Parse OpenSTA output into a TimingReport."""
    wns, tns = _parse_wns_tns(output)
    slack = _parse_slack_from_report(output)

    findings: List[TimingFinding] = []
    has_violations = False

    # Determine classification from WNS
    if wns is not None:
        if wns < 0:
            has_violations = True
            findings.append(TimingFinding(
                finding_id="OPENSTA-WNS-VIOLATION",
                severity="error",
                category="setup_violation",
                entity="design",
                message=f"Worst negative slack: {wns} ns",
                slack=wns,
                path_type="max",
            ))
        else:
            findings.append(TimingFinding(
                finding_id="OPENSTA-WNS-CLEAN",
                severity="info",
                category="timing_clean",
                entity="design",
                message=f"Worst slack: {wns} ns (MET)",
                slack=wns,
                path_type="max",
            ))

    # Add TNS finding if available and different from WNS
    if tns is not None and tns != wns:
        if tns < 0:
            findings.append(TimingFinding(
                finding_id="OPENSTA-TNS-VIOLATION",
                severity="error" if tns < 0 else "info",
                category="total_negative_slack",
                entity="design",
                message=f"Total negative slack: {tns} ns",
                slack=tns,
            ))

    # Parse path details from report_checks output
    # Look for Startpoint/Endpoint pairs
    current_path = {}
    for line in output.splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith("Startpoint:"):
            current_path["startpoint"] = line_stripped[len("Startpoint:"):].strip()
        elif line_stripped.startswith("Endpoint:"):
            current_path["endpoint"] = line_stripped[len("Endpoint:"):].strip()
        elif line_stripped.startswith("Path Group:"):
            current_path["path_group"] = line_stripped[len("Path Group:"):].strip()
        elif line_stripped.startswith("Path Type:"):
            current_path["path_type"] = line_stripped[len("Path Type:"):].strip()
        elif "slack (" in line_stripped:
            m = re.search(r"([-\d.]+)\s+slack\s+\((\w+)\)", line_stripped)
            if m and current_path:
                slack_val = float(m.group(1))
                classification = m.group(2)
                sp = current_path.get("startpoint", "?")
                ep = current_path.get("endpoint", "?")
                pg = current_path.get("path_group", "?")
                pt = current_path.get("path_type", "?")

                if classification == "VIOLATED":
                    sev = "error"
                    cat = f"{'setup' if pt == 'max' else 'hold'}_violation"
                else:
                    sev = "info"
                    cat = "timing_clean"

                findings.append(TimingFinding(
                    finding_id=f"OPENSTA-PATH-{len(findings):03d}",
                    severity=sev,
                    category=cat,
                    entity=f"{sp} -> {ep}",
                    message=f"Path {sp} -> {ep}: slack = {slack_val} ns ({classification})",
                    slack=slack_val,
                    path_group=pg,
                    path_type=pt,
                ))
                current_path = {}

    return TimingReport(
        wns=wns,
        tns=tns,
        findings=findings,
        raw_output=output,
        has_violations=has_violations,
    )


# ---------------------------------------------------------------------------
# OpenSTA Adapter
# ---------------------------------------------------------------------------

class OpenSTAAdapter:
    """Minimal OpenSTA Oracle adapter.

    Invokes OpenSTA v2.2.0 via WSL2 subprocess, parses timing output,
    and maps findings into EGER EvidenceArtifact contract.

    File staging: All substrate files are copied to a WSL-native staging
    directory (no spaces in path) via a bash command, because Windows
    Python's pathlib/shutil cannot reliably access WSL-internal paths.

    P166: design_name is validated against a safe identifier contract
    before reaching the Tcl script, preventing command injection.
    """

    def __init__(
        self,
        sta_binary: Optional[Path] = None,
        timeout_seconds: int = DEFAULT_OPENSTA_TIMEOUT_SECONDS,
    ):
        self.sta_binary = Path(sta_binary) if sta_binary else DEFAULT_OPENSTA_BINARY
        if timeout_seconds < MINIMUM_OPENSTA_TIMEOUT_SECONDS:
            raise ValueError(
                f"timeout_seconds must be >= {MINIMUM_OPENSTA_TIMEOUT_SECONDS}, "
                f"got {timeout_seconds}"
            )
        self.timeout_seconds = timeout_seconds

    def validate(
        self,
        sdc_text: str,
        netlist_path: Path,
        lib_path: Path,
        design_name: str = "simple_path",
        input_identity: str = "candidate",
        evidence_store: Optional[Path] = None,
    ) -> OracleResult:
        """Validate SDC constraints using OpenSTA timing analysis.

        Args:
            sdc_text: SDC constraint text to evaluate
            netlist_path: Path to gate-level Verilog netlist
            lib_path: Path to Liberty timing library
            design_name: Name of the top-level design module (validated)
            input_identity: Identifier for this input
            evidence_store: Optional directory to persist raw evidence

        Returns:
            OracleResult with timing evidence or failure
        """
        input_h = _input_hash(sdc_text)
        produced_at = datetime.now(timezone.utc).isoformat()

        # P166: Validate design_name before any subprocess execution
        design_error = _validate_design_name(design_name)
        if design_error is not None:
            raw_bytes = b""
            stderr_text = design_error
            exit_code = 1  # INVALID_REQUEST-like
            raw_hash = _sha256_hex(raw_bytes)
            raw_id = f"EGER-RAW-{input_h[:12]}"

            return OracleResult(
                is_success=False,
                raw_evidence=RawEvidence(
                    schema_version=SCHEMA_VERSIONS["raw"],
                    raw_id=raw_id,
                    oracle={"name": OPENSTA_ORACLE_NAME, "version": OPENSTA_ORACLE_VERSION,
                            "revision": OPENSTA_ORACLE_REVISION},
                    invocation={"operation": "validate", "args": {"input_identity": input_identity}},
                    input_hash=input_h,
                    raw_bytes=raw_bytes,
                    raw_hash=raw_hash,
                    exit_code=exit_code,
                    captured_at=produced_at,
                    stderr=stderr_text,
                ),
                failure=OracleFailure(
                    kind="INVALID_REQUEST",
                    exit_code=exit_code,
                    message=stderr_text,
                    raw_ref={"raw_id": raw_id, "raw_hash": raw_hash},
                ),
            )

        # Early check: missing executable
        if not self.sta_binary.exists():
            raw_bytes = b""
            stderr_text = f"OpenSTA binary not found: {self.sta_binary}"
            exit_code = 127
            raw_hash = _sha256_hex(raw_bytes)
            raw_id = f"EGER-RAW-{input_h[:12]}"

            return OracleResult(
                is_success=False,
                raw_evidence=RawEvidence(
                    schema_version=SCHEMA_VERSIONS["raw"],
                    raw_id=raw_id,
                    oracle={"name": OPENSTA_ORACLE_NAME, "version": OPENSTA_ORACLE_VERSION,
                            "revision": OPENSTA_ORACLE_REVISION},
                    invocation={"operation": "validate", "args": {"input_identity": input_identity}},
                    input_hash=input_h,
                    raw_bytes=raw_bytes,
                    raw_hash=raw_hash,
                    exit_code=exit_code,
                    captured_at=produced_at,
                    stderr=stderr_text,
                ),
                failure=OracleFailure(
                    kind="ORACLE_FAILURE",
                    exit_code=exit_code,
                    message=stderr_text,
                    raw_ref={"raw_id": raw_id, "raw_hash": raw_hash},
                ),
            )

        # Invoke OpenSTA
        raw_bytes, stderr_text, exit_code = self._invoke_opensta(
            sdc_text, netlist_path, lib_path, design_name
        )

        raw_hash = _sha256_hex(raw_bytes)
        raw_id = f"EGER-RAW-{input_h[:12]}"
        artifact_id = f"EGER-EVID-{input_h[:12]}"

        # Optionally persist raw evidence
        raw_path: Optional[str] = None
        if evidence_store is not None:
            store = Path(evidence_store)
            store.mkdir(parents=True, exist_ok=True)
            raw_path = str(store / f"{raw_id}.txt")
            Path(raw_path).write_bytes(raw_bytes)
        else:
            raw_path = f"<memory>/{raw_id}.txt"

        raw_evidence = RawEvidence(
            schema_version=SCHEMA_VERSIONS["raw"],
            raw_id=raw_id,
            oracle={"name": OPENSTA_ORACLE_NAME, "version": OPENSTA_ORACLE_VERSION,
                    "revision": OPENSTA_ORACLE_REVISION},
            invocation={
                "operation": "validate",
                "args": {
                    "input_identity": input_identity,
                    "design_name": design_name,
                    "netlist": str(netlist_path),
                    "lib": str(lib_path),
                },
            },
            input_hash=input_h,
            raw_bytes=raw_bytes,
            raw_hash=raw_hash,
            exit_code=exit_code,
            captured_at=produced_at,
            raw_path=raw_path,
            stderr=stderr_text,
        )

        # Handle subprocess failure
        if exit_code == -1:
            return OracleResult(
                is_success=False,
                raw_evidence=raw_evidence,
                failure=OracleFailure(
                    kind="ORACLE_FAILURE",
                    exit_code=exit_code,
                    message=stderr_text or f"OpenSTA timed out after {self.timeout_seconds}s",
                    raw_ref={"raw_id": raw_id, "raw_hash": raw_hash},
                ),
            )

        if exit_code != OPENSTA_EXIT_SUCCESS:
            return OracleResult(
                is_success=False,
                raw_evidence=raw_evidence,
                failure=OracleFailure(
                    kind="ORACLE_FAILURE",
                    exit_code=exit_code,
                    message=stderr_text or f"OpenSTA failed (exit {exit_code})",
                    raw_ref={"raw_id": raw_id, "raw_hash": raw_hash},
                ),
            )

        # Parse timing output
        output_text = raw_bytes.decode("utf-8", errors="replace")
        report = _parse_timing_report(output_text)

        # Map findings to EGER contract
        findings = []
        for tf in report.findings:
            findings.append({
                "finding_id": tf.finding_id,
                "code": tf.category,
                "severity": tf.severity,
                "message": tf.message,
                "location": {},
                "related_location": None,
                "context": {"slack": tf.slack, "path_group": tf.path_group, "path_type": tf.path_type},
                "affected_object": tf.entity,
                "finding_identity": None,
            })

        # Build analysis_scope
        analysis_scope = {
            "status": "VALIDATED" if not report.has_violations else "VIOLATIONS_FOUND",
            "wns": report.wns,
            "tns": report.tns,
            "has_violations": report.has_violations,
        }

        # Determine evidence_scope (raw value — normalizer maps to canonical scope)
        evidence_scope = "VALIDATED"

        # Build evidence for hashing
        evidence_dict_for_hash = {
            "schema_version": SCHEMA_VERSIONS["evidence"],
            "artifact_id": artifact_id,
            "oracle": {"name": OPENSTA_ORACLE_NAME, "version": OPENSTA_ORACLE_VERSION,
                       "revision": OPENSTA_ORACLE_REVISION},
            "evidence_scope": evidence_scope,
            "oracle_status": "SUCCESS",
            "findings": findings,
            "analysis_scope": analysis_scope,
            "raw_ref": {"raw_id": raw_id, "raw_hash": raw_hash},
            "input_hash": input_h,
        }
        evidence_hash = _sha256_hex(_canonical_json(evidence_dict_for_hash))

        provenance = {
            "oracle_name": OPENSTA_ORACLE_NAME,
            "oracle_version": OPENSTA_ORACLE_VERSION,
            "oracle_revision": OPENSTA_ORACLE_REVISION,
            "invocation_operation": "validate",
            "invocation_args": {
                "input_identity": input_identity,
                "design_name": design_name,
            },
            "schema_version": SCHEMA_VERSIONS["evidence"],
            "input_hash": input_h,
            "raw_hash": raw_hash,
            "evidence_hash": evidence_hash,
            "produced_at": produced_at,
            "raw_path": raw_path,
            "wns": report.wns,
            "tns": report.tns,
        }

        artifact = EvidenceArtifact(
            schema_version=SCHEMA_VERSIONS["evidence"],
            artifact_id=artifact_id,
            oracle={"name": OPENSTA_ORACLE_NAME, "version": OPENSTA_ORACLE_VERSION,
                    "revision": OPENSTA_ORACLE_REVISION},
            provenance=provenance,
            evidence_scope=evidence_scope,
            oracle_status="SUCCESS",
            findings=findings,
            analysis_scope=analysis_scope,
            raw_ref={"raw_id": raw_id, "raw_hash": raw_hash},
            evidence_hash=evidence_hash,
            produced_at=produced_at,
        )

        return OracleResult(
            is_success=True,
            evidence=artifact,
            raw_evidence=raw_evidence,
        )

    def _invoke_opensta(
        self,
        sdc_text: str,
        netlist_path: Path,
        lib_path: Path,
        design_name: str,
    ) -> Tuple[bytes, str, int]:
        """Invoke OpenSTA via subprocess with a generated Tcl script.

        All file staging is done through WSL bash commands, because Windows
        Python pathlib cannot create directories under WSL-internal paths.
        Substrate files are copied from the Windows mount (/mnt/X/...) to a
        staging directory with no spaces in its path.

        NOTE: design_name is validated by _validate_design_name() before
        reaching this method. It is safe to interpolate into the Tcl script.

        Returns:
            (stdout_bytes, stderr_text, exit_code)
            exit_code == -1 indicates timeout
        """
        input_h = _input_hash(sdc_text)

        # WSL staging directory (no spaces)
        staging_dir = f"~/eger_sta_{input_h[:12]}"

        # Convert paths for WSL
        sta_wsl = self._to_wsl_path(self.sta_binary)
        netlist_wsl = self._to_wsl_path(netlist_path)
        lib_wsl = self._to_wsl_path(lib_path)

        # Build a single bash script that:
        # 1. Creates staging dir
        # 2. Copies substrate files from /mnt/ paths
        # 3. Writes SDC and Tcl script (via heredoc)
        # 4. Runs OpenSTA
        # 5. Cleans up
        # SDC content is written via single-quoted heredoc to avoid shell expansion.

        bash_script = (
            f"set -e\n"
            f"mkdir -p {staging_dir}\n"
            f"cp '{lib_wsl}' {staging_dir}/simple_cells.lib\n"
            f"cp '{netlist_wsl}' {staging_dir}/simple_path.v\n"
        )

        # Write SDC file
        bash_script += (
            f"cat > {staging_dir}/candidate.sdc << 'SDCEOF'\n"
            f"{sdc_text}\n"
            f"SDCEOF\n"
        )

        # Write Tcl script
        # design_name is pre-validated: only [a-zA-Z0-9_/] — safe for Tcl interpolation
        tcl_script = (
            f"read_liberty simple_cells.lib\n"
            f"read_verilog simple_path.v\n"
            f"link_design {design_name}\n"
            f"read_sdc candidate.sdc\n"
            f"report_wns\n"
            f"report_tns\n"
            f"report_checks\n"
            f"exit\n"
        )
        bash_script += (
            f"cat > {staging_dir}/run.tcl << 'TCLEOF'\n"
            f"{tcl_script}\n"
            f"TCLEOF\n"
        )

        # Run OpenSTA
        bash_script += (
            f"cd {staging_dir}\n"
            f"{sta_wsl} -no_init -no_splash run.tcl\n"
        )

        # Cleanup
        bash_script += f"rm -rf {staging_dir}\n"

        cmd = ["wsl", "-d", "Ubuntu-24.04", "bash", "-c", bash_script]

        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                env=env,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            self._cleanup_wsl(staging_dir)
            stdout = exc.stdout if exc.stdout else b""
            stderr_text = (
                exc.stderr.decode("utf-8", errors="replace")
                if exc.stderr
                else f"OpenSTA timed out after {self.timeout_seconds}s"
            )
            return stdout, stderr_text, -1

        stdout = result.stdout or b""
        stderr = (result.stderr or b"").decode("utf-8", errors="replace")
        exit_code = int(result.returncode)

        self._cleanup_wsl(staging_dir)

        return stdout, stderr, exit_code

    @staticmethod
    def _to_wsl_path(path: Path) -> str:
        """Convert a Windows path to WSL mount path.

        Handles two cases:
        1. Standard Windows paths (D:\\foo) -> /mnt/d/foo
        2. WSL2 UNC paths (//wsl.localhost/Ubuntu-24.04/foo) -> /foo
        """
        path = Path(path).resolve()
        path_str = str(path).replace("\\", "/")
        # Check if this is already a WSL UNC path
        if path_str.startswith("//wsl.localhost/") or path_str.startswith("//wsl$/"):
            # Extract the path after the distribution name
            # Format: //wsl.localhost/DistributionName/path/to/file
            parts = path_str.split("/")
            # Find the distribution name segment and take everything after it
            for i, part in enumerate(parts):
                if part in ("wsl.localhost", "wsl$"):
                    # Next part is distribution name, rest is the path
                    if i + 2 < len(parts):
                        return "/" + "/".join(parts[i + 2:])
            # Fallback: return as-is
            return path_str
        # Standard Windows path
        drive = path.drive[0].lower() if path.drive else "c"
        rest = path_str
        # Remove drive letter and colon (e.g., "D:" -> "")
        rest = rest[2:] if len(rest) > 1 and rest[1] == ":" else rest
        return f"/mnt/{drive}{rest}"

    @staticmethod
    def _cleanup_wsl(staging_dir: str) -> None:
        """Clean up WSL staging directory."""
        try:
            subprocess.run(
                ["wsl", "-d", "Ubuntu-24.04", "bash", "-c",
                 f"rm -rf {staging_dir}"],
                capture_output=True, timeout=10,
            )
        except Exception:
            pass

    def capabilities(self) -> Dict[str, Any]:
        """Declarative capability descriptor."""
        return {
            "oracle": {
                "name": OPENSTA_ORACLE_NAME,
                "version": OPENSTA_ORACLE_VERSION,
                "revision": OPENSTA_ORACLE_REVISION,
            },
            "capabilities": {
                "timing_analysis": "static timing analysis (setup/hold violations)",
                "wns_tns": "worst/total negative slack reporting",
                "path_reporting": "timing path analysis",
            },
            "scope_vocabulary": sorted(SCOPE_MAP.keys()),
            "normalized_scope_values": ["FULL", "PARTIAL", "INSUFFICIENT", "UNSUPPORTED"],
            "exit_code_semantics": {
                "0": "SUCCESS — timing analysis completed",
                "non-zero": "ORACLE_FAILURE — analysis failed",
                "-1": "ORACLE_FAILURE — subprocess timeout",
            },
            "input_requirements": {
                "sdc_text": "SDC timing constraints",
                "netlist_path": "gate-level Verilog netlist",
                "lib_path": "Liberty timing library",
                "design_name": "Verilog module identifier (validated)",
            },
        }
