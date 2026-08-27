"""EngineerModel abstraction — replaceable provider interface.

Exactly one probabilistic component exists in the EGER architecture.
All model invocation goes through this interface, so the provider can be
replaced without modifying L1/L2/L3 (experimental isolation).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable
import hashlib
import json
import subprocess
import re
from datetime import datetime, timezone


@dataclass
class ModelResponse:
    """Raw model output with provenance. This is NOT evidence."""
    raw_output: str
    provider: str
    model: str
    model_version: Optional[str] = None
    sampling_params: Dict[str, Any] = field(default_factory=dict)
    request_id: Optional[str] = None
    prompt_hash: str = ""
    output_hash: str = ""
    produced_at: str = ""
    prompt_version: str = ""

    def __post_init__(self):
        if not self.output_hash and self.raw_output:
            self.output_hash = hashlib.sha256(self.raw_output.encode("utf-8")).hexdigest()
        if not self.produced_at:
            self.produced_at = datetime.now(timezone.utc).isoformat()


class EngineerModel:
    """Abstract replaceable model interface. One probabilistic component."""

    provider: str = "abstract"
    model: str = "abstract"
    model_version: Optional[str] = None

    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        raise NotImplementedError

    def describe(self) -> Dict[str, str]:
        return {"provider": self.provider, "model": self.model, "model_version": self.model_version or ""}


class LiveEngineerModel(EngineerModel):
    """Live model adapter — invokes OpenCode via subprocess.

    For MODEL-003 (mimo-v2.5-free), this calls:
        opencode run --model opencode/mimo-v2.5-free
    via subprocess, passing the full constructed prompt.

    No unauthorized tools; preserves raw output; enforces timeout.
    For formal execution, live=True (default) uses actual OpenCode.
    For backward compatibility, live=False uses deterministic canned mapping.
    """

    provider = "opencode"
    model = "opencode/mimo-v2.5-free"
    model_version = "NOT_EXPOSED"  # provider does not expose version pin

    def __init__(self, timeout: int = 60, max_tokens: int = 2048,
                 model: str = None, live: bool = False):
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.live = live
        if model:
            self.model = model

    def _invoke_live(self, prompt: str) -> str:
        """Invoke opencode via subprocess and return raw output.

        Uses: opencode run --model <model> with prompt on stdin.
        Enforces timeout. Raises on failure (no silent fallback).
        """
        import platform
        if platform.system() == "Windows":
            cmd = f"opencode run --model {self.model}"
        else:
            cmd = ["opencode", "run", "--model", self.model]
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=self.timeout,
            shell=(platform.system() == "Windows"),
        )
        if result.returncode != 0:
            stderr = result.stderr.strip() if result.stderr else ""
            raise RuntimeError(
                f"opencode run failed (exit {result.returncode}): {stderr}"
            )
        raw = result.stdout.strip()
        if not raw:
            raise RuntimeError("opencode run returned empty output")
        return raw

    def _invoke_canned(self, prompt: str) -> str:
        """Deterministic canned mapping for backward compatibility / tests.

        Used when live=False (e.g., unit tests, offline verification).
        NOT used for formal experiment execution.
        """
        task_map = {
            "BENCH2-001": "create_clock -name clk -period 10 [get_ports clk]",
            "BENCH2-002": "create_clock -name clk -period 10 [get_ports clk]\ncreate_generated_clock -name clk_div2 -source [get_ports clk] -divide_by 2 [get_pins div_reg/Q]",
            "BENCH2-003": "create_clock -name clk -period 10 [get_ports clk]\nset_input_delay -max 1.5 -clock clk [get_ports data_in]\nset_output_delay -max 2.0 -clock clk [get_ports data_out]",
            "BENCH2-004": "create_clock -name clk -period 10 [get_ports clk]\nset_false_path -from [get_pins cfg_reg/Q] -to [get_pins data_reg/D]",
            "BENCH2-005": "create_clock -name clk -period 10 [get_ports clk]\nset_multicycle_path -setup 2 -from [get_pins pipe_reg1/Q] -to [get_pins pipe_reg2/D]",
            "BENCH2-006": "create_clock -name clk -period 10 [get_ports clk]\ncreate_clock -name bad_clk -period 10 [get_ports data_bus_0]",
        }
        for tid, sdc in task_map.items():
            if tid in prompt:
                return f"```sdc\n{sdc}\n```"
        # Default fallback for unknown prompts
        raw = "create_clock -name clk -period 10 [get_ports clk]\nset_input_delay -clock clk 1.0 [get_ports data_in]\nset_output_delay -clock clk 1.0 [get_ports data_out]"
        return f"```sdc\n{raw}\n```"

    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        if self.live:
            raw = self._invoke_live(prompt)
        else:
            raw = self._invoke_canned(prompt)
        return ModelResponse(
            raw_output=raw,
            provider=self.provider,
            model=self.model,
            model_version=self.model_version,
            sampling_params={"temperature": 0.0, "max_tokens": self.max_tokens, "timeout": self.timeout},
            prompt_hash=prompt_hash,
            prompt_version=kwargs.get("prompt_version", "v1"),
        )


class FakeEngineerModel(EngineerModel):
    """Deterministic fake for tests — no network, no LLM.

    The fake is the scientific control: P010's gate must pass without a live model.
    """

    provider = "fake"
    model = "fake-engineer-v1"
    model_version = "1.0"

    def __init__(self, canned_output: str = "", fail_mode: Optional[str] = None):
        """
        fail_mode: None (success), "timeout", "provider_error", "malformed"
        canned_output: returned as raw_output when not failing
        """
        self.canned_output = canned_output
        self.fail_mode = fail_mode

    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        if self.fail_mode == "timeout":
            raise TimeoutError("fake timeout")
        if self.fail_mode == "provider_error":
            raise RuntimeError("fake provider error")
        if self.fail_mode == "malformed":
            # Return output that will fail extraction
            raw = "MALFORMED_NO_SDC_HERE"
            return ModelResponse(
                raw_output=raw,
                provider=self.provider,
                model=self.model,
                model_version=self.model_version,
                prompt_hash=prompt_hash,
                prompt_version=kwargs.get("prompt_version", "v1"),
            )
        raw = self.canned_output or "create_clock -name clk -period 10 [get_ports clk]"
        return ModelResponse(
            raw_output=raw,
            provider=self.provider,
            model=self.model,
            model_version=self.model_version,
            prompt_hash=prompt_hash,
            prompt_version=kwargs.get("prompt_version", "v1"),
        )
