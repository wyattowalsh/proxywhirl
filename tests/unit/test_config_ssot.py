"""Convergence tests for config SSOT (Wave 2G).

Asserts CLI TOML, env settings, and API ConfigurationSettings share the same
canonical defaults for timeouts, retries, health interval, logging, and rate
limits — sourced from ``proxywhirl.config_core``.
"""

from __future__ import annotations

import os
from unittest.mock import patch

from proxywhirl.api.models import ConfigurationSettings, RateLimitConfig
from proxywhirl.config import CLIConfig
from proxywhirl.config_core import (
    DEFAULT_CLI_STORAGE_BACKEND,
    DEFAULT_FOLLOW_REDIRECTS,
    DEFAULT_HEALTH_CHECK_INTERVAL_SECONDS,
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOG_REDACT_CREDENTIALS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RATE_LIMIT,
    DEFAULT_RATE_LIMIT_DEFAULT,
    DEFAULT_RATE_LIMIT_REQUEST_ENDPOINT,
    DEFAULT_ROTATION_STRATEGY,
    DEFAULT_STORAGE_BACKEND,
    DEFAULT_TIMEOUT,
    DEFAULT_VERIFY_SSL,
    SharedRuntimeConfig,
    configuration_settings_defaults,
    shared_runtime_defaults,
)
from proxywhirl.settings import APISettings, LoggingSettings, ProxyConfiguration


class TestSharedRuntimeConfig:
    """Core model exposes the canonical defaults."""

    def test_shared_defaults_match_constants(self) -> None:
        shared = shared_runtime_defaults()
        assert shared.timeout == DEFAULT_TIMEOUT
        assert shared.max_retries == DEFAULT_MAX_RETRIES
        assert shared.verify_ssl is DEFAULT_VERIFY_SSL
        assert shared.follow_redirects is DEFAULT_FOLLOW_REDIRECTS
        assert shared.health_check_interval_seconds == DEFAULT_HEALTH_CHECK_INTERVAL_SECONDS
        assert shared.rotation_strategy == DEFAULT_ROTATION_STRATEGY
        assert shared.log_level == DEFAULT_LOG_LEVEL
        assert shared.log_format == DEFAULT_LOG_FORMAT
        assert shared.log_redact_credentials is DEFAULT_LOG_REDACT_CREDENTIALS
        assert shared.storage_backend == DEFAULT_STORAGE_BACKEND
        assert shared.rate_limit == DEFAULT_RATE_LIMIT
        assert shared.rate_limit_default == DEFAULT_RATE_LIMIT_DEFAULT
        assert shared.rate_limit_request_endpoint == DEFAULT_RATE_LIMIT_REQUEST_ENDPOINT

    def test_shared_model_is_frozen(self) -> None:
        shared = SharedRuntimeConfig()
        assert shared.model_config.get("frozen") is True


class TestAdapterDefaultConvergence:
    """CLI / env / API adapters converge on shared knobs."""

    def test_timeout_and_retries_converge(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            cli = CLIConfig()
            runtime = ProxyConfiguration()
            api = APISettings()
            api_model = ConfigurationSettings()

        assert cli.timeout == runtime.timeout == api.timeout == api_model.timeout == DEFAULT_TIMEOUT
        assert (
            cli.max_retries
            == runtime.max_retries
            == api.max_retries
            == api_model.max_retries
            == DEFAULT_MAX_RETRIES
        )

    def test_ssl_and_redirect_converge(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            cli = CLIConfig()
            runtime = ProxyConfiguration()

        assert cli.verify_ssl is runtime.verify_ssl is DEFAULT_VERIFY_SSL
        assert cli.follow_redirects is runtime.follow_redirects is DEFAULT_FOLLOW_REDIRECTS

    def test_health_check_interval_converge(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            cli = CLIConfig()
            runtime = ProxyConfiguration()

        assert cli.health_check_interval == DEFAULT_HEALTH_CHECK_INTERVAL_SECONDS
        assert runtime.health_check_interval_seconds == DEFAULT_HEALTH_CHECK_INTERVAL_SECONDS

    def test_rotation_strategy_converge(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            cli = CLIConfig()
            api = APISettings()
            api_model = ConfigurationSettings()

        assert (
            cli.rotation_strategy
            == api.strategy
            == api_model.rotation_strategy
            == DEFAULT_ROTATION_STRATEGY
        )

    def test_logging_defaults_converge(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            runtime = ProxyConfiguration()
            logging = LoggingSettings()

        assert runtime.log_level == logging.level == DEFAULT_LOG_LEVEL
        assert runtime.log_format == logging.format == DEFAULT_LOG_FORMAT
        assert (
            runtime.log_redact_credentials
            is logging.redact_credentials
            is DEFAULT_LOG_REDACT_CREDENTIALS
        )

    def test_rate_limit_defaults_converge(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            cli = CLIConfig()
            api = APISettings()
            rate_limits = RateLimitConfig()

        assert cli.rate_limit_per_key == api.rate_limit == DEFAULT_RATE_LIMIT
        assert cli.rate_limit_per_ip == DEFAULT_RATE_LIMIT
        assert rate_limits.default_limit == DEFAULT_RATE_LIMIT_DEFAULT
        assert rate_limits.request_endpoint_limit == DEFAULT_RATE_LIMIT_REQUEST_ENDPOINT

    def test_storage_backend_ssot_vs_cli_override(self) -> None:
        """Library/env default is memory; CLI intentionally defaults to file."""
        with patch.dict(os.environ, {}, clear=True):
            runtime = ProxyConfiguration()
            cli = CLIConfig()

        assert runtime.storage_backend == DEFAULT_STORAGE_BACKEND == "memory"
        assert cli.storage_backend == DEFAULT_CLI_STORAGE_BACKEND == "file"

    def test_cors_defaults_converge_empty(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            api = APISettings()
            api_model = ConfigurationSettings()

        assert api.cors_origins == []
        assert api_model.cors_origins == []


class TestWave1AApiSettingsPreserved:
    """Wave 1A security fields remain on APISettings and keep behavior."""

    def test_require_auth_bind_expose_docs_present(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            api = APISettings()

        assert api.require_auth is False
        assert api.bind_host == "127.0.0.1"
        assert api.expose_docs is None
        assert api.docs_enabled is True  # unset + auth off → docs on

    def test_docs_gated_when_require_auth(self) -> None:
        with patch.dict(
            os.environ,
            {"PROXYWHIRL_REQUIRE_AUTH": "true", "PROXYWHIRL_API_KEY": "k"},
            clear=True,
        ):
            api = APISettings()

        assert api.require_auth is True
        assert api.docs_enabled is False


class TestConfigurationSettingsMapping:
    """API ConfigurationSettings maps from config_core SSOT."""

    def test_from_defaults_matches_constructor(self) -> None:
        from_factory = ConfigurationSettings.from_defaults()
        direct = ConfigurationSettings()
        assert from_factory.model_dump() == direct.model_dump()

    def test_from_defaults_accepts_overrides(self) -> None:
        settings = ConfigurationSettings.from_defaults(
            timeout=45,
            rate_limits={"default_limit": 20},
        )
        assert settings.timeout == 45
        assert settings.max_retries == DEFAULT_MAX_RETRIES
        assert settings.rate_limits.default_limit == 20
        assert settings.rate_limits.request_endpoint_limit == DEFAULT_RATE_LIMIT_REQUEST_ENDPOINT

    def test_configuration_settings_defaults_dict(self) -> None:
        payload = configuration_settings_defaults()
        assert payload["timeout"] == DEFAULT_TIMEOUT
        assert payload["max_retries"] == DEFAULT_MAX_RETRIES
        assert payload["rotation_strategy"] == DEFAULT_ROTATION_STRATEGY
        assert payload["cors_origins"] == []
        assert payload["rate_limits"]["default_limit"] == DEFAULT_RATE_LIMIT_DEFAULT
