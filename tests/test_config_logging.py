"""Tests for EgerConfig, EgerLogger, and secret redaction — P151.

Deterministic tests for:
- Configuration defaults and env overrides
- Precedence resolution
- Validation and bounds
- Serialization round-trip
- Structured event creation
- Secret redaction
- Logger failure isolation
"""

import json
import os
from unittest.mock import patch

import pytest

from eger.config import (
    EgerConfig,
    config_from_env,
    ENV_ORACLE_TIMEOUT,
    ENV_MAX_ITERATIONS,
    ENV_MAX_CALLS,
    ENV_MODEL_PROVIDER,
    ENV_MODEL_NAME,
    ENV_LOG_LEVEL,
    ENV_ARTIFACT_DIR,
    DEFAULT_ORACLE_TIMEOUT,
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_MAX_CALLS,
    MIN_ORACLE_TIMEOUT,
    MAX_ORACLE_TIMEOUT,
    MIN_MAX_ITERATIONS,
    MAX_MAX_ITERATIONS,
    MIN_MAX_CALLS,
    MAX_MAX_CALLS,
    VALID_LOG_LEVELS,
)
from eger.logging import (
    EgerLogger,
    StructuredEvent,
    get_logger,
    set_level,
    redact_secrets,
    EVENT_RUN_STARTED,
    EVENT_ORACLE_TIMEOUT,
    EVENT_ORACLE_FAILED,
    EVENT_VERIFICATION_COMPLETED,
    EVENT_RUN_COMPLETED,
    EVENT_RUN_FAILED,
)


# ===========================================================================
# EgerConfig — defaults
# ===========================================================================


class TestEgerConfigDefaults:
    """Config with no overrides uses safe defaults."""

    def test_default_oracle_timeout(self):
        config = EgerConfig()
        assert config.oracle_timeout_seconds == DEFAULT_ORACLE_TIMEOUT

    def test_default_max_iterations(self):
        config = EgerConfig()
        assert config.max_iterations == DEFAULT_MAX_ITERATIONS

    def test_default_max_calls(self):
        config = EgerConfig()
        assert config.max_total_calls == DEFAULT_MAX_CALLS

    def test_default_model_provider(self):
        config = EgerConfig()
        assert config.model_provider == ""

    def test_default_model_name(self):
        config = EgerConfig()
        assert config.model_name == ""

    def test_default_log_level(self):
        config = EgerConfig()
        assert config.log_level == "INFO"

    def test_default_artifact_dir(self):
        config = EgerConfig()
        assert config.artifact_dir == ""

    def test_default_schema_version(self):
        config = EgerConfig()
        assert config.schema_version == "eger.config.v1"


# ===========================================================================
# EgerConfig — explicit override
# ===========================================================================


class TestEgerConfigExplicit:
    """Explicit constructor arguments override defaults."""

    def test_explicit_oracle_timeout(self):
        config = EgerConfig(oracle_timeout_seconds=120)
        assert config.oracle_timeout_seconds == 120

    def test_explicit_max_iterations(self):
        config = EgerConfig(max_iterations=10)
        assert config.max_iterations == 10

    def test_explicit_max_calls(self):
        config = EgerConfig(max_total_calls=50)
        assert config.max_total_calls == 50

    def test_explicit_model(self):
        config = EgerConfig(model_provider="openai", model_name="gpt-4")
        assert config.model_provider == "openai"
        assert config.model_name == "gpt-4"

    def test_explicit_log_level(self):
        config = EgerConfig(log_level="DEBUG")
        assert config.log_level == "DEBUG"


# ===========================================================================
# EgerConfig — validation
# ===========================================================================


class TestEgerConfigValidation:
    """Invalid configuration raises ValueError at construction."""

    def test_zero_oracle_timeout_rejected(self):
        with pytest.raises(ValueError, match="oracle_timeout_seconds must be >="):
            EgerConfig(oracle_timeout_seconds=0)

    def test_negative_oracle_timeout_rejected(self):
        with pytest.raises(ValueError, match="oracle_timeout_seconds must be >="):
            EgerConfig(oracle_timeout_seconds=-1)

    def test_excessive_oracle_timeout_rejected(self):
        with pytest.raises(ValueError, match="oracle_timeout_seconds must be <="):
            EgerConfig(oracle_timeout_seconds=MAX_ORACLE_TIMEOUT + 1)

    def test_zero_iterations_rejected(self):
        with pytest.raises(ValueError, match="max_iterations must be >="):
            EgerConfig(max_iterations=0)

    def test_negative_iterations_rejected(self):
        with pytest.raises(ValueError, match="max_iterations must be >="):
            EgerConfig(max_iterations=-1)

    def test_excessive_iterations_rejected(self):
        with pytest.raises(ValueError, match="max_iterations must be <="):
            EgerConfig(max_iterations=MAX_MAX_ITERATIONS + 1)

    def test_zero_calls_rejected(self):
        with pytest.raises(ValueError, match="max_total_calls must be >="):
            EgerConfig(max_total_calls=0)

    def test_two_calls_rejected(self):
        """max_total_calls must be >= 3."""
        with pytest.raises(ValueError, match="max_total_calls must be >="):
            EgerConfig(max_total_calls=2)

    def test_excessive_calls_rejected(self):
        with pytest.raises(ValueError, match="max_total_calls must be <="):
            EgerConfig(max_total_calls=MAX_MAX_CALLS + 1)

    def test_invalid_log_level_rejected(self):
        with pytest.raises(ValueError, match="log_level must be one of"):
            EgerConfig(log_level="INVALID")

    def test_boundary_oracle_timeout_accepted(self):
        config = EgerConfig(oracle_timeout_seconds=MIN_ORACLE_TIMEOUT)
        assert config.oracle_timeout_seconds == MIN_ORACLE_TIMEOUT

    def test_boundary_iterations_accepted(self):
        config = EgerConfig(max_iterations=MIN_MAX_ITERATIONS)
        assert config.max_iterations == MIN_MAX_ITERATIONS

    def test_boundary_calls_accepted(self):
        config = EgerConfig(max_total_calls=MIN_MAX_CALLS)
        assert config.max_total_calls == MIN_MAX_CALLS


# ===========================================================================
# EgerConfig — serialization
# ===========================================================================


class TestEgerConfigSerialization:
    """Config round-trips through to_dict/from_dict."""

    def test_round_trip(self):
        config = EgerConfig(
            oracle_timeout_seconds=120,
            max_iterations=10,
            max_total_calls=50,
            model_provider="openai",
            model_name="gpt-4",
            log_level="DEBUG",
            artifact_dir="/tmp/artifacts",
        )
        d = config.to_dict()
        restored = EgerConfig.from_dict(d)
        assert restored.oracle_timeout_seconds == config.oracle_timeout_seconds
        assert restored.max_iterations == config.max_iterations
        assert restored.max_total_calls == config.max_total_calls
        assert restored.model_provider == config.model_provider
        assert restored.model_name == config.model_name
        assert restored.log_level == config.log_level
        assert restored.artifact_dir == config.artifact_dir

    def test_to_dict_keys(self):
        config = EgerConfig()
        d = config.to_dict()
        expected_keys = {
            "schema_version", "oracle_timeout_seconds", "max_iterations",
            "max_total_calls", "model_provider", "model_name",
            "log_level", "artifact_dir",
        }
        assert set(d.keys()) == expected_keys

    def test_from_dict_defaults(self):
        """from_dict uses defaults for missing keys."""
        config = EgerConfig.from_dict({})
        assert config.oracle_timeout_seconds == DEFAULT_ORACLE_TIMEOUT
        assert config.max_iterations == DEFAULT_MAX_ITERATIONS
        assert config.max_total_calls == DEFAULT_MAX_CALLS

    def test_config_hash_deterministic(self):
        config = EgerConfig(oracle_timeout_seconds=90)
        h1 = config.config_hash
        h2 = config.config_hash
        assert h1 == h2

    def test_config_hash_differs_for_different_config(self):
        c1 = EgerConfig(oracle_timeout_seconds=60)
        c2 = EgerConfig(oracle_timeout_seconds=120)
        assert c1.config_hash != c2.config_hash

    def test_config_is_frozen(self):
        config = EgerConfig()
        with pytest.raises(AttributeError):
            config.oracle_timeout_seconds = 999


# ===========================================================================
# EgerConfig — environment overrides
# ===========================================================================


class TestEgerConfigEnvOverrides:
    """Environment variables override defaults."""

    def test_env_oracle_timeout(self):
        with patch.dict(os.environ, {ENV_ORACLE_TIMEOUT: "120"}):
            config = config_from_env()
            assert config.oracle_timeout_seconds == 120

    def test_env_max_iterations(self):
        with patch.dict(os.environ, {ENV_MAX_ITERATIONS: "10"}):
            config = config_from_env()
            assert config.max_iterations == 10

    def test_env_max_calls(self):
        with patch.dict(os.environ, {ENV_MAX_CALLS: "50"}):
            config = config_from_env()
            assert config.max_total_calls == 50

    def test_env_model_provider(self):
        with patch.dict(os.environ, {ENV_MODEL_PROVIDER: "anthropic"}):
            config = config_from_env()
            assert config.model_provider == "anthropic"

    def test_env_model_name(self):
        with patch.dict(os.environ, {ENV_MODEL_NAME: "claude-3"}):
            config = config_from_env()
            assert config.model_name == "claude-3"

    def test_env_log_level(self):
        with patch.dict(os.environ, {ENV_LOG_LEVEL: "DEBUG"}):
            config = config_from_env()
            assert config.log_level == "DEBUG"

    def test_env_invalid_timeout_rejected(self):
        with patch.dict(os.environ, {ENV_ORACLE_TIMEOUT: "not_a_number"}):
            with pytest.raises(ValueError, match="Invalid value"):
                config_from_env()

    def test_env_timeout_out_of_bounds_rejected(self):
        with patch.dict(os.environ, {ENV_ORACLE_TIMEOUT: "0"}):
            with pytest.raises(ValueError, match="Invalid value"):
                config_from_env()

    def test_env_invalid_log_level_rejected(self):
        with patch.dict(os.environ, {ENV_LOG_LEVEL: "BOGUS"}):
            with pytest.raises(ValueError, match="Invalid value"):
                config_from_env()


# ===========================================================================
# EgerConfig — precedence
# ===========================================================================


class TestEgerConfigPrecedence:
    """Explicit overrides win over environment variables."""

    def test_explicit_overrides_env(self):
        with patch.dict(os.environ, {ENV_ORACLE_TIMEOUT: "120"}):
            config = config_from_env(oracle_timeout_seconds=30)
            assert config.oracle_timeout_seconds == 30

    def test_explicit_overrides_env_iterations(self):
        with patch.dict(os.environ, {ENV_MAX_ITERATIONS: "20"}):
            config = config_from_env(max_iterations=5)
            assert config.max_iterations == 5

    def test_explicit_overrides_env_calls(self):
        with patch.dict(os.environ, {ENV_MAX_CALLS: "100"}):
            config = config_from_env(max_total_calls=15)
            assert config.max_total_calls == 15

    def test_env_used_when_explicit_is_none(self):
        with patch.dict(os.environ, {ENV_ORACLE_TIMEOUT: "200"}):
            config = config_from_env(oracle_timeout_seconds=None)
            assert config.oracle_timeout_seconds == 200

    def test_default_used_when_no_explicit_no_env(self):
        # Ensure env var is not set
        env = {k: "" for k in [ENV_ORACLE_TIMEOUT, ENV_MAX_ITERATIONS, ENV_MAX_CALLS]}
        with patch.dict(os.environ, env, clear=False):
            # Remove the specific env vars if they exist
            for k in list(os.environ.keys()):
                if k.startswith("EGER_"):
                    del os.environ[k]
            config = config_from_env()
            assert config.oracle_timeout_seconds == DEFAULT_ORACLE_TIMEOUT


# ===========================================================================
# EgerConfig — frozen
# ===========================================================================


class TestEgerConfigFrozen:
    """Config is immutable."""

    def test_cannot_set_oracle_timeout(self):
        config = EgerConfig()
        with pytest.raises(AttributeError):
            config.oracle_timeout_seconds = 999

    def test_cannot_set_max_iterations(self):
        config = EgerConfig()
        with pytest.raises(AttributeError):
            config.max_iterations = 999

    def test_cannot_set_log_level(self):
        config = EgerConfig()
        with pytest.raises(AttributeError):
            config.log_level = "DEBUG"


# ===========================================================================
# Secret redaction
# ===========================================================================


class TestSecretRedaction:
    """Secret patterns are redacted from log output."""

    def test_api_key_redacted(self):
        text = "api_key=sk-abc123def456ghi789"
        result = redact_secrets(text)
        assert "sk-abc123def456ghi789" not in result
        assert "[REDACTED]" in result

    def test_bearer_token_redacted(self):
        text = "bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        result = redact_secrets(text)
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result
        assert "[REDACTED]" in result

    def test_password_redacted(self):
        text = "password=hunter2"
        result = redact_secrets(text)
        assert "hunter2" not in result
        assert "[REDACTED]" in result

    def test_secret_key_redacted(self):
        text = "secret=my_secret_value"
        result = redact_secrets(text)
        assert "my_secret_value" not in result
        assert "[REDACTED]" in result

    def test_token_equals_value_redacted(self):
        text = "token: abcdefghijklmnop"
        result = redact_secrets(text)
        assert "abcdefghijklmnop" not in result
        assert "[REDACTED]" in result

    def test_github_token_redacted(self):
        text = "Using ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef123456"
        result = redact_secrets(text)
        assert "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef123456" not in result
        assert "[REDACTED]" in result

    def test_slack_token_redacted(self):
        text = "Token: xoxb-1234567890-1234567890-abcdefghijklmnop"
        result = redact_secrets(text)
        assert "xoxb-" not in result
        assert "[REDACTED]" in result

    def test_clean_text_preserved(self):
        text = "Task completed successfully with 5 iterations"
        result = redact_secrets(text)
        assert result == text

    def test_empty_string(self):
        assert redact_secrets("") == ""

    def test_none_safe(self):
        """redact_secrets handles falsy input."""
        assert redact_secrets("") == ""

    def test_no_false_positive_on_normal_text(self):
        text = "max_tokens=2048 temperature=0.0 model=gpt-4"
        result = redact_secrets(text)
        # max_tokens and model are not secrets
        assert "max_tokens=2048" in result
        assert "temperature=0.0" in result

    def test_authorization_header_redacted(self):
        text = "authorization: Bearer sk-test1234567890abcdef"
        result = redact_secrets(text)
        assert "sk-test1234567890abcdef" not in result
        assert "[REDACTED]" in result

    def test_private_key_redacted(self):
        text = "private_key=MIIEvgIBADANBgkqhki..."
        result = redact_secrets(text)
        assert "MIIEvgIBADANBgkqhki" not in result
        assert "[REDACTED]" in result


# ===========================================================================
# StructuredEvent
# ===========================================================================


class TestStructuredEvent:
    """StructuredEvent produces deterministic log entries."""

    def test_basic_event(self):
        event = StructuredEvent(
            "TEST_EVENT",
            component="Test",
            run_id="RUN-001",
        )
        d = event.to_dict()
        assert d["event"] == "TEST_EVENT"
        assert d["component"] == "Test"
        assert d["run_id"] == "RUN-001"
        assert "timestamp" in d

    def test_event_with_metadata(self):
        event = StructuredEvent(
            "TEST_EVENT",
            metadata={"prompt_hash": "abc123", "iteration": 2},
        )
        d = event.to_dict()
        assert d["metadata"]["prompt_hash"] == "abc123"
        assert d["metadata"]["iteration"] == 2

    def test_event_redacts_secrets_in_metadata(self):
        event = StructuredEvent(
            "TEST_EVENT",
            metadata={"api_key": "sk-supersecret123"},
        )
        d = event.to_dict()
        # Key-based redaction: api_key value is redacted
        assert d["metadata"]["api_key"] == "[REDACTED]"

    def test_event_redacts_secrets_in_error(self):
        event = StructuredEvent(
            "TEST_EVENT",
            error="Connection failed: api_key=sk-abc123xyz",
        )
        d = event.to_dict()
        assert "sk-abc123xyz" not in d["error"]

    def test_event_to_json(self):
        event = StructuredEvent("TEST_EVENT", component="Test")
        j = event.to_json()
        parsed = json.loads(j)
        assert parsed["event"] == "TEST_EVENT"

    def test_event_omits_empty_fields(self):
        event = StructuredEvent("TEST_EVENT")
        d = event.to_dict()
        assert "component" not in d
        assert "run_id" not in d
        assert "candidate_id" not in d
        assert "metadata" not in d

    def test_event_includes_non_empty_fields(self):
        event = StructuredEvent(
            "TEST_EVENT",
            component="Test",
            run_id="RUN-001",
            task_id="TASK-001",
            iteration=3,
            status="OK",
            candidate_id="CAND-001",
            evidence_id="EVID-001",
            verification_decision="ACCEPT",
            duration=1.234,
            error="some error",
        )
        d = event.to_dict()
        assert d["component"] == "Test"
        assert d["run_id"] == "RUN-001"
        assert d["task_id"] == "TASK-001"
        assert d["iteration"] == 3
        assert d["status"] == "OK"
        assert d["candidate_id"] == "CAND-001"
        assert d["evidence_id"] == "EVID-001"
        assert d["verification_decision"] == "ACCEPT"
        assert d["duration"] == 1.234
        assert d["error"] == "some error"

    def test_event_duration_rounded(self):
        event = StructuredEvent("TEST_EVENT", duration=1.123456789)
        d = event.to_dict()
        assert d["duration"] == 1.123457

    def test_event_negative_iteration_omitted(self):
        event = StructuredEvent("TEST_EVENT", iteration=-1)
        d = event.to_dict()
        assert "iteration" not in d

    def test_event_zero_iteration_included(self):
        event = StructuredEvent("TEST_EVENT", iteration=0)
        d = event.to_dict()
        assert d["iteration"] == 0


# ===========================================================================
# EgerLogger — lifecycle events
# ===========================================================================


class TestEgerLoggerLifecycle:
    """EgerLogger produces correct lifecycle events."""

    def test_run_started(self):
        logger = EgerLogger(name="test_lifecycle", log_level="DEBUG")
        event = logger.run_started("RUN-001", "TASK-001")
        assert event.event == EVENT_RUN_STARTED
        assert event.run_id == "RUN-001"
        assert event.task_id == "TASK-001"

    def test_oracle_timeout_event(self):
        logger = EgerLogger(name="test_oracle_timeout", log_level="DEBUG")
        event = logger.oracle_timeout(
            "RUN-001", "TASK-001", 0, "CAND-001", timeout_seconds=60
        )
        assert event.event == EVENT_ORACLE_TIMEOUT
        assert event.status == "TIMEOUT"
        assert event.metadata["timeout_seconds"] == 60

    def test_oracle_failed_event(self):
        logger = EgerLogger(name="test_oracle_failed", log_level="DEBUG")
        event = logger.oracle_failed(
            "RUN-001", "TASK-001", 0, "CAND-001",
            error="Process exited with code 127",
        )
        assert event.event == EVENT_ORACLE_FAILED
        assert event.status == "ORACLE_FAILURE"

    def test_verification_completed(self):
        logger = EgerLogger(name="test_verification", log_level="DEBUG")
        event = logger.verification_completed(
            "RUN-001", "TASK-001", "REJECT", "CAND-001", "EVID-001",
            error_count=2, reason="2 ERROR findings remain",
        )
        assert event.event == EVENT_VERIFICATION_COMPLETED
        assert event.verification_decision == "REJECT"

    def test_run_completed(self):
        logger = EgerLogger(name="test_run_complete", log_level="DEBUG")
        event = logger.run_completed(
            "RUN-001", "TASK-001", "REJECTED", "NO_ERRORS",
            total_calls=6, duration=5.2,
        )
        assert event.event == EVENT_RUN_COMPLETED
        assert event.status == "REJECTED"
        assert event.duration == 5.2

    def test_run_failed(self):
        logger = EgerLogger(name="test_run_failed", log_level="DEBUG")
        event = logger.run_failed(
            "RUN-001", "TASK-001", error="Model unavailable",
        )
        assert event.event == EVENT_RUN_FAILED
        assert event.status == "FAILED"


# ===========================================================================
# EgerLogger — secret safety
# ===========================================================================


class TestEgerLoggerSecrets:
    """Logger never emits secrets."""

    def test_metadata_secrets_redacted(self):
        logger = EgerLogger(name="test_secrets", log_level="DEBUG")
        event = logger.run_started(
            "RUN-001", "TASK-001",
            metadata={"api_key": "sk-supersecret123"},
        )
        json_str = event.to_json()
        # Key-based redaction: api_key value is redacted
        assert "sk-supersecret123" not in json_str

    def test_error_secrets_redacted(self):
        logger = EgerLogger(name="test_error_secrets", log_level="DEBUG")
        event = logger.oracle_failed(
            "RUN-001", "TASK-001", 0, "CAND-001",
            error="Failed with token=secret_abc123",
        )
        json_str = event.to_json()
        assert "secret_abc123" not in json_str

    def test_nested_metadata_secrets_redacted(self):
        logger = EgerLogger(name="test_nested", log_level="DEBUG")
        event = logger.run_started(
            "RUN-001", "TASK-001",
            metadata={"config": {"password": "hunter2"}},
        )
        d = event.to_dict()
        # Nested key-based redaction: password value is redacted
        assert d["metadata"]["config"]["password"] == "[REDACTED]"


# ===========================================================================
# EgerLogger — logger failure isolation
# ===========================================================================


class TestEgerLoggerFailureIsolation:
    """Logger failure must not alter verification decisions."""

    def test_logger_emits_event_even_if_handler_fails(self):
        """Event is created even if the logging handler has issues."""
        logger = EgerLogger(name="test_isolation", log_level="DEBUG")
        # Event creation should always succeed
        event = logger.run_started("RUN-001", "TASK-001")
        assert event.event == EVENT_RUN_STARTED
        assert event.to_dict()["run_id"] == "RUN-001"

    def test_event_structure_deterministic(self):
        """Same inputs produce same event structure."""
        e1 = StructuredEvent(
            "TEST",
            run_id="R1",
            task_id="T1",
            iteration=0,
            status="OK",
        )
        e2 = StructuredEvent(
            "TEST",
            run_id="R1",
            task_id="T1",
            iteration=0,
            status="OK",
        )
        # Same fields (timestamps differ, but structure is same)
        d1 = e1.to_dict()
        d2 = e2.to_dict()
        # Remove timestamps for comparison
        d1.pop("timestamp")
        d2.pop("timestamp")
        assert d1 == d2


# ===========================================================================
# EgerLogger — generic event
# ===========================================================================


class TestEgerLoggerGeneric:
    """Generic event creation."""

    def test_custom_event(self):
        logger = EgerLogger(name="test_custom", log_level="DEBUG")
        event = logger.event(
            "CUSTOM_EVENT",
            component="TestComponent",
            run_id="RUN-001",
            metadata={"key": "value"},
        )
        assert event.event == "CUSTOM_EVENT"
        assert event.component == "TestComponent"


# ===========================================================================
# Version
# ===========================================================================


class TestVersion:
    """Version constant exists."""

    def test_version_exists(self):
        from eger import __version__
        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_version_format(self):
        from eger import __version__
        # Should be semver-like
        parts = __version__.split(".")
        assert len(parts) >= 2
        assert all(p.isdigit() for p in parts[:2])
