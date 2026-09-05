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
from eger.oracle.schemas import DesignMetadata
from eger.evidence.normalizer import EvidenceNormalizer
from eger.verification.gate import VerificationGate

# Frozen P055 DesignMetadata for the P163 simple_path substrate (P175 §5).
# Kept as a declarative JSON next to this module, mirroring the
# BENCH-002 evaluator_context convention.
SIMPLE_PATH_METADATA_PATH = Path(__file__).resolve().parent / "simple_path.design_metadata.json"


def load_simple_path_design_metadata() -> DesignMetadata:
    """Load the frozen design metadata for the RQ-5 substrate.

    Deterministic; the JSON is versioned with the harness. Used to elevate
    Ṛta's NETLIST_REQUIRED scope to FULL/PARTIAL via the FROZEN P055
    evaluator-side reference validation (EGER P175 resolution). The metadata
    is NEVER exposed to the model.
    """
    if not SIMPLE_PATH_METADATA_PATH.exists():
        raise FileNotFoundError(
            f"design metadata not found: {SIMPLE_PATH_METADATA_PATH}"
        )
    import json
    with open(SIMPLE_PATH_METADATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return DesignMetadata.from_dict(data)

DEFAULT_MODEL = "opencode/mimo-v2.5-free"
DEFAULT_DISTRO = "Ubuntu-24.04"
# P173-R: the agent-mode model can exceed 60s on some invocations (it
# performs file operations in its workspace). 180s is the model-call
# timeout (distinct from the frozen 60s Oracle-call timeout in P169).
DEFAULT_TIMEOUT_SECONDS = 180


# ---------------------------------------------------------------------------
# OpenSTA binary resolution (canonical runtime config, P167)
# ---------------------------------------------------------------------------

def resolve_opensta_binary_wsl(distro: str = DEFAULT_DISTRO) -> Path:
    """Resolve the WSL OpenSTA binary path via wslpath (P167 canonical config)."""
    r = subprocess.run(
        ["wsl", "-d", distro, "bash", "-c", "echo $HOME"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=10,
    )
    wsl_home = r.stdout.strip()
    sta_wsl = f"{wsl_home}/opensta_build/OpenSTA/app/sta"
    r = subprocess.run(
        ["wsl", "-d", distro, "wslpath", "-w", sta_wsl],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=10,
    )
    return Path(r.stdout.strip())


# ---------------------------------------------------------------------------
# Oracle call builders
# ---------------------------------------------------------------------------

def build_rta_oracle_call(
    rta_cli: Optional[Path] = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    design_metadata: Optional[DesignMetadata] = None,
) -> Callable[[str, str], Any]:
    """Build the Ṛta oracle callable for the RQ-5 harness.

    P175 §5: the harness passes the frozen P055 DesignMetadata on every
    Ṛta validate() call (initial and candidate evaluations) so that
    NETLIST_REQUIRED evaluations elevate to FULL/PARTIAL evidence scope via
    evaluator-side reference validation. Without it, every Ṛta evaluation
    normalizes to UNSUPPORTED and the VerificationGate fail-closes REJECT.
    """
    if design_metadata is None:
        design_metadata = load_simple_path_design_metadata()
    oracle = EvidenceOracle(rta_cli=rta_cli, timeout_seconds=timeout_seconds)
    return lambda sdc_text, input_identity: oracle.validate(
        sdc_text=sdc_text, input_identity=input_identity,
        design_metadata=design_metadata,
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
    """Invokes the frozen model via `opencode.cmd run` (P172 §6).

    P173-R invocation repair: the model (opencode/mimo-v2.5-free) behaves
    as a file-writing agent. It reliably produces SDC content when prompted
    with a directive file-writing instruction ("Write the file timing.sdc."
    with the current SDC as numbered lines) and writes the result to
    timing.sdc in its working directory. It does NOT reliably return SDC
    text on stdout for chat-style prompts.

    This provider therefore:
    1. Runs opencode in a scratch working directory (no spaces).
    2. Prompts the model to write/overwrite timing.sdc.
    3. Reads timing.sdc back after the run; falls back to stdout if no
       file was produced (e.g., the model returned text instead).
    """

    SDC_FILENAME = "timing.sdc"

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        provider_failure_prefix: str = "ERROR:",
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        cwd: Optional[Path] = None,
        workdir: Optional[Path] = None,
    ):
        self.model = model
        self.provider_failure_prefix = provider_failure_prefix
        self.timeout_seconds = timeout_seconds
        self.cwd = cwd
        # Scratch working directory for the model's file operations.
        # If not given, derive one from the process cwd; ensure no spaces.
        # P173-R finding: `opencode run` resolves its workspace to the git
        # repository root of the process cwd and writes files THERE, not to
        # the subprocess cwd. The provider therefore reads timing.sdc from
        # the workspace root (the project root when running inside the repo).
        if cwd is not None:
            self.workdir = Path(cwd)
        elif workdir is not None:
            self.workdir = Path(workdir)
        else:
            import tempfile
            self.workdir = Path(tempfile.gettempdir()) / "eger_model_scratch"
        self.workdir.mkdir(parents=True, exist_ok=True)

    def _clean(self) -> None:
        sdc = self.workdir / self.SDC_FILENAME
        if sdc.exists():
            sdc.unlink()

    def invoke(self, prompt: str) -> str:
        self._clean()
        try:
            # P179: opencode emits UTF-8 agent output; decode robustly
            # instead of using the locale codec (cp1252 on Windows), which
            # crashes on non-ASCII bytes.
            result = subprocess.run(
                ["opencode.cmd", "run", "--model", self.model, prompt],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=self.timeout_seconds,
                cwd=str(self.workdir),
            )
            stdout = result.stdout or ""
        except subprocess.TimeoutExpired:
            return f"{self.provider_failure_prefix}timeout after {self.timeout_seconds}s"
        except Exception as e:  # pragma: no cover - defensive
            return f"{self.provider_failure_prefix}{e}"

        sdc = self.workdir / self.SDC_FILENAME
        if sdc.exists():
            content = sdc.read_text(encoding="utf-8", errors="replace")
            return content.strip()
        # Fall back to stdout text (some models reply directly).
        return stdout.strip()


def build_model_call(
    model: str = DEFAULT_MODEL,
    cwd: Optional[Path] = None,
    workdir: Optional[Path] = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> Callable[[str], str]:
    provider = OpenCodeModelProvider(
        model=model, timeout_seconds=timeout_seconds, cwd=cwd, workdir=workdir,
    )
    return provider.invoke


# ---------------------------------------------------------------------------
# EGER pipeline components
# ---------------------------------------------------------------------------

def build_pipeline_components() -> Dict[str, Any]:
    normalizer = EvidenceNormalizer()
    gate = VerificationGate()
    return {"normalizer": normalizer, "gate": gate}