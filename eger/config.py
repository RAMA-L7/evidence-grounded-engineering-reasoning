"""EgerConfig — explicit runtime configuration with environment overrides.

P151: Production hardening for configuration management.

Configuration resolution precedence:
    1. Explicit configuration (constructor arguments)
    2. Environment variable overrides (EGER_* namespace)
    3. Safe defaults

INVARIANT: EgerConfig is frozen (immutable) once created.
INVARIANT: Configuration errors fail before live execution begins.
INVARIANT: Environment overrides cannot disable resource protection.
INVARIANT: Same inputs → same resolved configuration (deterministic).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import hashlib
import json

SCHEMA_CONFIG = "eger.config.v1"

# ---------------------------------------------------------------------------
# Environment variable names
# ---------------------------------------------------------------------------

ENV_ORACLE_TIMEOUT = "EGER_ORACLE_TIMEOUT"
ENV_MAX_ITERATIONS = "EGER_MAX_ITERATIONS"
ENV_MAX_CALLS = "EGER_MAX_CALLS"
ENV_MODEL_PROVIDER = "EGER_MODEL_PROVIDER"
ENV_MODEL_NAME = "EGER_MODEL_NAME"
ENV_LOG_LEVEL = "EGER_LOG_LEVEL"
ENV_ARTIFACT_DIR = "EGER_ARTIFACT_DIR"

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_ORACLE_TIMEOUT = 60
DEFAULT_MAX_ITERATIONS = 5
DEFAULT_MAX_CALLS = 15
DEFAULT_MODEL_PROVIDER = ""
DEFAULT_MODEL_NAME = ""
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_ARTIFACT_DIR = ""

# Bounds
MIN_ORACLE_TIMEOUT = 1
MAX_ORACLE_TIMEOUT = 3600  # 1 hour
MIN_MAX_ITERATIONS = 1
MAX_MAX_ITERATIONS = 100
MIN_MAX_CALLS = 3
MAX_MAX_CALLS = 500

VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


# ---------------------------------------------------------------------------
# Environment variable parsing
# ---------------------------------------------------------------------------

def _env_int(name: str, default: int, min_val: int, max_val: int) -> int:
    """Parse an integer from environment with bounds enforcement."""
    raw = os.environ.get(name, "")
    if not raw:
        return default
    try:
        val = int(raw)
    except ValueError:
        raise ValueError(
            f"Invalid value for {name}: '{raw}' — must be an integer"
        )
    if val < min_val or val > max_val:
        raise ValueError(
            f"Invalid value for {name}: {val} — must be between {min_val} and {max_val}"
        )
    return val


def _env_str(name: str, default: str) -> str:
    """Parse a string from environment."""
    return os.environ.get(name, default) or default


def _env_log_level(name: str, default: str) -> str:
    """Parse a log level from environment with validation."""
    raw = os.environ.get(name, "")
    if not raw:
        return default
    level = raw.upper().strip()
    if level not in VALID_LOG_LEVELS:
        raise ValueError(
            f"Invalid value for {name}: '{raw}' — must be one of {VALID_LOG_LEVELS}"
        )
    return level


# ---------------------------------------------------------------------------
# EgerConfig
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EgerConfig:
    """Explicit runtime configuration — immutable.

    Resolution precedence:
        1. Constructor arguments (explicit override)
        2. Environment variables (EGER_* namespace)
        3. Safe defaults

    INVARIANT: All fields are validated at construction time.
    INVARIANT: Environment cannot set unsafe values (bounds enforced).
    INVARIANT: Deterministic — same inputs → same config.
    """
    oracle_timeout_seconds: int = DEFAULT_ORACLE_TIMEOUT
    max_iterations: int = DEFAULT_MAX_ITERATIONS
    max_total_calls: int = DEFAULT_MAX_CALLS
    model_provider: str = DEFAULT_MODEL_PROVIDER
    model_name: str = DEFAULT_MODEL_NAME
    log_level: str = DEFAULT_LOG_LEVEL
    artifact_dir: str = DEFAULT_ARTIFACT_DIR
    schema_version: str = SCHEMA_CONFIG

    def __post_init__(self):
        """Validate all fields at construction time."""
        if self.oracle_timeout_seconds < MIN_ORACLE_TIMEOUT:
            raise ValueError(
                f"oracle_timeout_seconds must be >= {MIN_ORACLE_TIMEOUT}, "
                f"got {self.oracle_timeout_seconds}"
            )
        if self.oracle_timeout_seconds > MAX_ORACLE_TIMEOUT:
            raise ValueError(
                f"oracle_timeout_seconds must be <= {MAX_ORACLE_TIMEOUT}, "
                f"got {self.oracle_timeout_seconds}"
            )
        if self.max_iterations < MIN_MAX_ITERATIONS:
            raise ValueError(
                f"max_iterations must be >= {MIN_MAX_ITERATIONS}, "
                f"got {self.max_iterations}"
            )
        if self.max_iterations > MAX_MAX_ITERATIONS:
            raise ValueError(
                f"max_iterations must be <= {MAX_MAX_ITERATIONS}, "
                f"got {self.max_iterations}"
            )
        if self.max_total_calls < MIN_MAX_CALLS:
            raise ValueError(
                f"max_total_calls must be >= {MIN_MAX_CALLS}, "
                f"got {self.max_total_calls}"
            )
        if self.max_total_calls > MAX_MAX_CALLS:
            raise ValueError(
                f"max_total_calls must be <= {MAX_MAX_CALLS}, "
                f"got {self.max_total_calls}"
            )
        if self.log_level not in VALID_LOG_LEVELS:
            raise ValueError(
                f"log_level must be one of {VALID_LOG_LEVELS}, got '{self.log_level}'"
            )

    # -- Serialization ----------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Deterministic serialization."""
        return {
            "schema_version": self.schema_version,
            "oracle_timeout_seconds": self.oracle_timeout_seconds,
            "max_iterations": self.max_iterations,
            "max_total_calls": self.max_total_calls,
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "log_level": self.log_level,
            "artifact_dir": self.artifact_dir,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> EgerConfig:
        """Deserialize from dict."""
        return cls(
            oracle_timeout_seconds=d.get("oracle_timeout_seconds", DEFAULT_ORACLE_TIMEOUT),
            max_iterations=d.get("max_iterations", DEFAULT_MAX_ITERATIONS),
            max_total_calls=d.get("max_total_calls", DEFAULT_MAX_CALLS),
            model_provider=d.get("model_provider", DEFAULT_MODEL_PROVIDER),
            model_name=d.get("model_name", DEFAULT_MODEL_NAME),
            log_level=d.get("log_level", DEFAULT_LOG_LEVEL),
            artifact_dir=d.get("artifact_dir", DEFAULT_ARTIFACT_DIR),
            schema_version=d.get("schema_version", SCHEMA_CONFIG),
        )

    # -- Config hash (deterministic identity) ----------------------------

    @property
    def config_hash(self) -> str:
        """Deterministic hash of configuration for audit trails."""
        data = self.to_dict()
        return hashlib.sha256(
            json.dumps(data, sort_keys=True).encode("utf-8")
        ).hexdigest()


# ---------------------------------------------------------------------------
# Factory: resolve from environment
# ---------------------------------------------------------------------------

def config_from_env(
    *,
    oracle_timeout_seconds: Optional[int] = None,
    max_iterations: Optional[int] = None,
    max_total_calls: Optional[int] = None,
    model_provider: Optional[str] = None,
    model_name: Optional[str] = None,
    log_level: Optional[str] = None,
    artifact_dir: Optional[str] = None,
) -> EgerConfig:
    """Create EgerConfig with environment override resolution.

    Precedence:
        1. Explicit keyword arguments (if not None)
        2. Environment variables (EGER_* namespace)
        3. Safe defaults

    Raises ValueError if any resolved value is invalid.

    Example:
        # With environment: EGER_ORACLE_TIMEOUT=120
        config = config_from_env()  # oracle_timeout_seconds=120

        # With explicit override (wins over env):
        config = config_from_env(oracle_timeout_seconds=30)  # 30, not 120
    """
    resolved_timeout = (
        oracle_timeout_seconds
        if oracle_timeout_seconds is not None
        else _env_int(ENV_ORACLE_TIMEOUT, DEFAULT_ORACLE_TIMEOUT, MIN_ORACLE_TIMEOUT, MAX_ORACLE_TIMEOUT)
    )
    resolved_iterations = (
        max_iterations
        if max_iterations is not None
        else _env_int(ENV_MAX_ITERATIONS, DEFAULT_MAX_ITERATIONS, MIN_MAX_ITERATIONS, MAX_MAX_ITERATIONS)
    )
    resolved_calls = (
        max_total_calls
        if max_total_calls is not None
        else _env_int(ENV_MAX_CALLS, DEFAULT_MAX_CALLS, MIN_MAX_CALLS, MAX_MAX_CALLS)
    )
    resolved_provider = (
        model_provider
        if model_provider is not None
        else _env_str(ENV_MODEL_PROVIDER, DEFAULT_MODEL_PROVIDER)
    )
    resolved_model = (
        model_name
        if model_name is not None
        else _env_str(ENV_MODEL_NAME, DEFAULT_MODEL_NAME)
    )
    resolved_log = (
        log_level
        if log_level is not None
        else _env_log_level(ENV_LOG_LEVEL, DEFAULT_LOG_LEVEL)
    )
    resolved_artifact = (
        artifact_dir
        if artifact_dir is not None
        else _env_str(ENV_ARTIFACT_DIR, DEFAULT_ARTIFACT_DIR)
    )

    return EgerConfig(
        oracle_timeout_seconds=resolved_timeout,
        max_iterations=resolved_iterations,
        max_total_calls=resolved_calls,
        model_provider=resolved_provider,
        model_name=resolved_model,
        log_level=resolved_log,
        artifact_dir=resolved_artifact,
    )
