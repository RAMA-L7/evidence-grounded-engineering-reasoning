"""EgerLogger — structured logging with secret redaction.

P151: Production hardening for observability.

Provides a lightweight structured logging mechanism with:
- Machine-readable event fields
- Secret redaction (API keys, tokens, credentials)
- Lifecycle event tracking aligned with provenance
- Configurable log levels
- Component-level logger namespacing

INVARIANT: Logging is observability only — never authority.
INVARIANT: Logger failure must never alter verification decisions.
INVARIANT: Secrets are never logged.
INVARIANT: Same inputs → same log event structure (deterministic fields).
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

# ---------------------------------------------------------------------------
# Event types (aligned with provenance lifecycle)
# ---------------------------------------------------------------------------

EVENT_RUN_STARTED = "RUN_STARTED"
EVENT_PROMPT_CREATED = "PROMPT_CREATED"
EVENT_CANDIDATE_CREATED = "CANDIDATE_CREATED"
EVENT_ORACLE_STARTED = "ORACLE_STARTED"
EVENT_ORACLE_COMPLETED = "ORACLE_COMPLETED"
EVENT_ORACLE_FAILED = "ORACLE_FAILED"
EVENT_ORACLE_TIMEOUT = "ORACLE_TIMEOUT"
EVENT_EVIDENCE_RECORDED = "EVIDENCE_RECORDED"
EVENT_REVISION_STARTED = "REVISION_STARTED"
EVENT_REVISION_COMPLETED = "REVISION_COMPLETED"
EVENT_VERIFICATION_COMPLETED = "VERIFICATION_COMPLETED"
EVENT_RUN_COMPLETED = "RUN_COMPLETED"
EVENT_RUN_FAILED = "RUN_FAILED"
EVENT_CONFIG_LOADED = "CONFIG_LOADED"

# ---------------------------------------------------------------------------
# Secret redaction
# ---------------------------------------------------------------------------

# Patterns that indicate secrets — must never appear in logs
_SECRET_PATTERNS = [
    # Key=value patterns (config strings, env dumps)
    re.compile(r"api[_-]?key\s*[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"token\s*[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"password\s*[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"secret\s*[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"private[_-]?key\s*[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"authorization\s*[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"bearer\s+\S+", re.IGNORECASE),
    # Standalone secret tokens (prefix-based detection)
    re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE),  # OpenAI-style keys
    re.compile(r"ghp_[a-zA-Z0-9]{20,}", re.IGNORECASE),  # GitHub tokens
    re.compile(r"xox[bpsa]-[a-zA-Z0-9-]+", re.IGNORECASE),  # Slack tokens
    # Dict-style key detection (for sanitized metadata values)
    re.compile(r'"?api[_-]?key"?\s*:\s*"\S+"', re.IGNORECASE),
    re.compile(r'"?token"?\s*:\s*"\S+"', re.IGNORECASE),
    re.compile(r'"?password"?\s*:\s*"\S+"', re.IGNORECASE),
    re.compile(r'"?secret[_-]?key"?\s*:\s*"\S+"', re.IGNORECASE),
]

_REDACTED = "[REDACTED]"


def redact_secrets(text: str) -> str:
    """Redact potential secrets from a string.

    This is a best-effort heuristic. It catches common secret patterns
    but cannot guarantee catching every possible secret format.

    Returns the input string with secrets replaced by [REDACTED].
    """
    if not text:
        return text
    result = text
    for pattern in _SECRET_PATTERNS:
        result = pattern.sub(_REDACTED, result)
    return result


def _sanitize_value(value: Any) -> Any:
    """Recursively sanitize a value for safe logging.

    Handles both flat strings and structured data.
    For dict keys that look like secret names, the values are redacted.
    """
    if isinstance(value, str):
        return redact_secrets(value)
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            # If the key itself looks like a secret name, redact the value
            key_lower = k.lower().replace("_", "").replace("-", "")
            secret_keys = {"apikey", "api_key", "token", "password", "secret", "secretkey", "secret_key", "privatekey", "private_key", "authorization", "auth"}
            if key_lower in secret_keys and isinstance(v, str):
                result[k] = _REDACTED
            else:
                result[k] = _sanitize_value(v)
        return result
    if isinstance(value, (list, tuple)):
        return [_sanitize_value(v) for v in value]
    return value


# ---------------------------------------------------------------------------
# Structured log event
# ---------------------------------------------------------------------------

class StructuredEvent:
    """A single structured log event with machine-readable fields.

    Fields are deterministic — same inputs produce same structure.
    Timestamps are UTC ISO format.
    """

    def __init__(
        self,
        event: str,
        *,
        component: str = "",
        run_id: str = "",
        task_id: str = "",
        iteration: int = -1,
        status: str = "",
        candidate_id: str = "",
        evidence_id: str = "",
        verification_decision: str = "",
        duration: Optional[float] = None,
        error: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.event = event
        self.component = component
        self.run_id = run_id
        self.task_id = task_id
        self.iteration = iteration
        self.status = status
        self.candidate_id = candidate_id
        self.evidence_id = evidence_id
        self.verification_decision = verification_decision
        self.duration = duration
        self.error = error
        self.metadata = _sanitize_value(metadata or {})
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Deterministic serialization (secrets redacted)."""
        d: Dict[str, Any] = {
            "timestamp": self.timestamp,
            "event": self.event,
        }
        if self.component:
            d["component"] = self.component
        if self.run_id:
            d["run_id"] = self.run_id
        if self.task_id:
            d["task_id"] = self.task_id
        if self.iteration >= 0:
            d["iteration"] = self.iteration
        if self.status:
            d["status"] = self.status
        if self.candidate_id:
            d["candidate_id"] = self.candidate_id
        if self.evidence_id:
            d["evidence_id"] = self.evidence_id
        if self.verification_decision:
            d["verification_decision"] = self.verification_decision
        if self.duration is not None:
            d["duration"] = round(self.duration, 6)
        if self.error:
            d["error"] = redact_secrets(self.error)
        if self.metadata:
            d["metadata"] = self.metadata
        return d

    def to_json(self) -> str:
        """JSON serialization for structured logging."""
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)


# ---------------------------------------------------------------------------
# EgerLogger
# ---------------------------------------------------------------------------

class EgerLogger:
    """Structured logger for EGER pipeline events.

    Provides:
    - Component-scoped loggers
    - Structured event creation
    - Secret redaction on all outputs
    - Configurable log level
    - Lifecycle event helpers

    INVARIANT: Logging is observability only — never authority.
    INVARIANT: Logger failure never alters verification decisions.
    """

    def __init__(
        self,
        name: str = "eger",
        log_level: str = "INFO",
    ):
        self._logger = logging.getLogger(name)
        self._level = getattr(logging, log_level.upper(), logging.INFO)
        self._logger.setLevel(self._level)

        # Add handler if none exists (avoid duplicate handlers)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(self._level)
            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

        self._level_name = log_level.upper()

    @property
    def level(self) -> str:
        return self._level_name

    def _emit(self, event: StructuredEvent, level: int = logging.INFO) -> None:
        """Emit a structured event if level is enabled."""
        if level >= self._level:
            self._logger.log(level, event.to_json())

    # -- Lifecycle events -------------------------------------------------

    def run_started(
        self,
        run_id: str,
        task_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StructuredEvent:
        """Record RUN_STARTED event."""
        event = StructuredEvent(
            EVENT_RUN_STARTED,
            component="Pipeline",
            run_id=run_id,
            task_id=task_id,
            status="STARTED",
            metadata=metadata,
        )
        self._emit(event, logging.INFO)
        return event

    def prompt_created(
        self,
        run_id: str,
        task_id: str,
        iteration: int,
        prompt_hash: str,
        request_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StructuredEvent:
        """Record PROMPT_CREATED event."""
        event = StructuredEvent(
            EVENT_PROMPT_CREATED,
            component="PromptBuilder",
            run_id=run_id,
            task_id=task_id,
            iteration=iteration,
            metadata={"prompt_hash": prompt_hash, "request_id": request_id, **(metadata or {})},
        )
        self._emit(event, logging.DEBUG)
        return event

    def candidate_created(
        self,
        run_id: str,
        task_id: str,
        iteration: int,
        candidate_id: str,
        candidate_hash: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StructuredEvent:
        """Record CANDIDATE_CREATED event."""
        event = StructuredEvent(
            EVENT_CANDIDATE_CREATED,
            component="ProposalGenerator",
            run_id=run_id,
            task_id=task_id,
            iteration=iteration,
            candidate_id=candidate_id,
            metadata={"candidate_hash": candidate_hash, **(metadata or {})},
        )
        self._emit(event, logging.DEBUG)
        return event

    def oracle_started(
        self,
        run_id: str,
        task_id: str,
        iteration: int,
        candidate_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StructuredEvent:
        """Record ORACLE_STARTED event."""
        event = StructuredEvent(
            EVENT_ORACLE_STARTED,
            component="Oracle",
            run_id=run_id,
            task_id=task_id,
            iteration=iteration,
            candidate_id=candidate_id,
            status="STARTED",
            metadata=metadata,
        )
        self._emit(event, logging.DEBUG)
        return event

    def oracle_completed(
        self,
        run_id: str,
        task_id: str,
        iteration: int,
        candidate_id: str,
        evidence_id: str,
        oracle_status: str,
        duration: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StructuredEvent:
        """Record ORACLE_COMPLETED event."""
        event = StructuredEvent(
            EVENT_ORACLE_COMPLETED,
            component="Oracle",
            run_id=run_id,
            task_id=task_id,
            iteration=iteration,
            candidate_id=candidate_id,
            evidence_id=evidence_id,
            status=oracle_status,
            duration=duration,
            metadata=metadata,
        )
        self._emit(event, logging.INFO)
        return event

    def oracle_failed(
        self,
        run_id: str,
        task_id: str,
        iteration: int,
        candidate_id: str,
        error: str,
        oracle_status: str = "ORACLE_FAILURE",
        duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StructuredEvent:
        """Record ORACLE_FAILED event."""
        event = StructuredEvent(
            EVENT_ORACLE_FAILED,
            component="Oracle",
            run_id=run_id,
            task_id=task_id,
            iteration=iteration,
            candidate_id=candidate_id,
            status=oracle_status,
            error=error,
            duration=duration,
            metadata=metadata,
        )
        self._emit(event, logging.WARNING)
        return event

    def oracle_timeout(
        self,
        run_id: str,
        task_id: str,
        iteration: int,
        candidate_id: str,
        timeout_seconds: int,
        duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StructuredEvent:
        """Record ORACLE_TIMEOUT event."""
        event = StructuredEvent(
            EVENT_ORACLE_TIMEOUT,
            component="Oracle",
            run_id=run_id,
            task_id=task_id,
            iteration=iteration,
            candidate_id=candidate_id,
            status="TIMEOUT",
            duration=duration,
            metadata={"timeout_seconds": timeout_seconds, **(metadata or {})},
        )
        self._emit(event, logging.WARNING)
        return event

    def evidence_recorded(
        self,
        run_id: str,
        task_id: str,
        iteration: int,
        evidence_id: str,
        evidence_hash: str,
        oracle_status: str,
        error_count: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StructuredEvent:
        """Record EVIDENCE_RECORDED event."""
        event = StructuredEvent(
            EVENT_EVIDENCE_RECORDED,
            component="EvidenceNormalizer",
            run_id=run_id,
            task_id=task_id,
            iteration=iteration,
            evidence_id=evidence_id,
            status=oracle_status,
            metadata={
                "evidence_hash": evidence_hash,
                "error_count": error_count,
                **(metadata or {}),
            },
        )
        self._emit(event, logging.INFO)
        return event

    def verification_completed(
        self,
        run_id: str,
        task_id: str,
        decision: str,
        candidate_id: str,
        evidence_id: str,
        error_count: int,
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StructuredEvent:
        """Record VERIFICATION_COMPLETED event."""
        event = StructuredEvent(
            EVENT_VERIFICATION_COMPLETED,
            component="VerificationGate",
            run_id=run_id,
            task_id=task_id,
            candidate_id=candidate_id,
            evidence_id=evidence_id,
            verification_decision=decision,
            status=decision,
            metadata={
                "error_count": error_count,
                "reason": redact_secrets(reason),
                **(metadata or {}),
            },
        )
        self._emit(event, logging.INFO)
        return event

    def run_completed(
        self,
        run_id: str,
        task_id: str,
        status: str,
        terminal_reason: str,
        total_calls: int = 0,
        duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StructuredEvent:
        """Record RUN_COMPLETED event."""
        event = StructuredEvent(
            EVENT_RUN_COMPLETED,
            component="Pipeline",
            run_id=run_id,
            task_id=task_id,
            status=status,
            duration=duration,
            metadata={
                "terminal_reason": terminal_reason,
                "total_calls": total_calls,
                **(metadata or {}),
            },
        )
        self._emit(event, logging.INFO)
        return event

    def run_failed(
        self,
        run_id: str,
        task_id: str,
        error: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StructuredEvent:
        """Record RUN_FAILED event."""
        event = StructuredEvent(
            EVENT_RUN_FAILED,
            component="Pipeline",
            run_id=run_id,
            task_id=task_id,
            status="FAILED",
            error=error,
            metadata=metadata,
        )
        self._emit(event, logging.ERROR)
        return event

    def config_loaded(
        self,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StructuredEvent:
        """Record CONFIG_LOADED event."""
        # Redact any potentially sensitive config values
        safe_meta = _sanitize_value(metadata or {})
        event = StructuredEvent(
            EVENT_CONFIG_LOADED,
            component="Config",
            status="LOADED",
            metadata=safe_meta,
        )
        self._emit(event, logging.INFO)
        return event

    # -- Generic event ----------------------------------------------------

    def event(
        self,
        event_type: str,
        *,
        component: str = "",
        level: int = logging.INFO,
        **kwargs: Any,
    ) -> StructuredEvent:
        """Emit a custom structured event."""
        safe_kwargs = _sanitize_value(kwargs)
        e = StructuredEvent(event_type, component=component, **safe_kwargs)
        self._emit(e, level)
        return e


# ---------------------------------------------------------------------------
# Module-level singleton (lazy init)
# ---------------------------------------------------------------------------

_default_logger: Optional[EgerLogger] = None


def get_logger(
    name: str = "eger",
    log_level: str = "INFO",
) -> EgerLogger:
    """Get or create the default EGER logger.

    Returns a singleton logger that can be reconfigured via set_level().
    """
    global _default_logger
    if _default_logger is None:
        _default_logger = EgerLogger(name=name, log_level=log_level)
    return _default_logger


def set_level(level: str) -> None:
    """Change the log level of the default logger."""
    global _default_logger
    if _default_logger is not None:
        _default_logger._level = getattr(logging, level.upper(), logging.INFO)
        _default_logger._level_name = level.upper()
        for handler in _default_logger._logger.handlers:
            handler.setLevel(_default_logger._level)
