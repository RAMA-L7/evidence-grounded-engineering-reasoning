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
