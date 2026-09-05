"""Provider construction for the future replication (EGER-RQ5-PILOT-002).

Builds oracle_call / model_call callables used by the trial runner.
This module is NOT invoked during P173 fixture validation (fixtures are
deterministic and never touch WSL/OpenSTA/Ṛta or the LLM). It is the
canonical wiring for the real run, frozen here so the readiness gate and
future execution gate share identical construction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Optional
import subprocess

from eger.oracle.adapter import EvidenceOracle
from eger.oracle.opensta_adapter import OpenSTAAdapter
from eger.evidence.normalizer import EvidenceNormalizer
from eger.verification.gate import VerificationGate

DEFAULT_MODEL = "opencode/mimo-v2.5-free"
DEFAULT_DISTRO = "Ubuntu-24.04"
DEFAULT_TIMEOUT_SECONDS = 60


# ---------------------------------------------------------------------------
# OpenSTA binary resolution (canonical runtime config, P167)
# ---------------------------------------------------------------------------

def resolve_opensta_binary_wsl(distro: str = DEFAULT_DISTRO) -> Path:
    """Resolve the WSL OpenSTA binary path via wslpath (P167 canonical config)."""
    r = subprocess.run(
        ["wsl", "-d", distro, "bash", "-c", "echo $HOME"],
        capture_output=True, text=True, timeout=10,
    )
    wsl_home = r.stdout.strip()
    sta_wsl = f"{wsl_home}/opensta_build/OpenSTA/app/sta"
    r = subprocess.run(
        ["wsl", "-d", distro, "wslpath", "-w", sta_wsl],
        capture_output=True, text=True, timeout=10,
    )
    return Path(r.stdout.strip())


# ---------------------------------------------------------------------------
# Oracle call builders
# ---------------------------------------------------------------------------

def build_rta_oracle_call(
    rta_cli: Optional[Path] = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> Callable[[str, str], Any]:
    oracle = EvidenceOracle(rta_cli=rta_cli, timeout_seconds=timeout_seconds)
    return lambda sdc_text, input_identity: oracle.validate(
        sdc_text=sdc_text, input_identity=input_identity,
    )


def build_opensta_oracle_call(
    sta_binary: Optional[Path] = None,
    netlist_path: Optional[Path] = None,
    lib_path: Optional[Path] = None,
    design_name: str = "simple_path",
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> Callable[[str, str], Any]:
    adapter = OpenSTAAdapter(sta_binary=sta_binary, timeout_seconds=timeout_seconds)
    if netlist_path is None or lib_path is None:
        raise ValueError("netlist_path and lib_path are required for OpenSTA")
    return lambda sdc_text, input_identity: adapter.validate(
        sdc_text=sdc_text,
        netlist_path=netlist_path,
        lib_path=lib_path,
        design_name=design_name,
        input_identity=input_identity,
    )


# ---------------------------------------------------------------------------
# Model provider (LLM)
# ---------------------------------------------------------------------------

class OpenCodeModelProvider:
    """Invokes the frozen model via `opencode.cmd run` (P172 §6)."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        provider_failure_prefix: str = "ERROR:",
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        cwd: Optional[Path] = None,
    ):
        self.model = model
        self.provider_failure_prefix = provider_failure_prefix
        self.timeout_seconds = timeout_seconds
        self.cwd = cwd

    def invoke(self, prompt: str) -> str:
        try:
            result = subprocess.run(
                ["opencode.cmd", "run", "--model", self.model, prompt],
                capture_output=True, text=True, timeout=self.timeout_seconds,
                cwd=str(self.cwd) if self.cwd else None,
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return f"{self.provider_failure_prefix}timeout after {self.timeout_seconds}s"
        except Exception as e:  # pragma: no cover - defensive
            return f"{self.provider_failure_prefix}{e}"


def build_model_call(
    model: str = DEFAULT_MODEL,
    cwd: Optional[Path] = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> Callable[[str], str]:
    provider = OpenCodeModelProvider(
        model=model, timeout_seconds=timeout_seconds, cwd=cwd,
    )
    return provider.invoke


# ---------------------------------------------------------------------------
# EGER pipeline components
# ---------------------------------------------------------------------------

def build_pipeline_components() -> Dict[str, Any]:
    normalizer = EvidenceNormalizer()
    gate = VerificationGate()
    return {"normalizer": normalizer, "gate": gate}