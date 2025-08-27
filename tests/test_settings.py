"""Tests for proxywhirl.settings module.

Comprehensive unit tests for APISettings and ProxyWhirlSettings models,
environment-based configuration, field validation, security settings,
and configuration helpers with full coverage.
"""

import os
from unittest.mock import patch

import pytest
from pydantic import SecretStr, ValidationError

from proxywhirl.settings import (
    APISettings,
    ProxyWhirlSettings,
    get_api_settings,
    get_proxywhirl_settings,
    is_development,
    is_production,
    is_testing,
)


class TestAPISettings:
    """Comprehensive tests for APISettings model with all validation scenarios."""

    def test_default_api_settings_creation(self):
        """Test APISettings creation with default values."""
        settings = APISettings()

        assert settings.app_name == "ProxyWhirl API"
        assert settings.version == "1.0.0"
        assert (
            settings.description == "Comprehensive REST API for ProxyWhirl rotating proxy service"
        )
        assert len(settings.secret_key.get_secret_value()) >= 32
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes == 30
        assert settings.environment == "development"
        assert settings.debug is True  # Auto-set from environment
        assert settings.cors_origins == []
        assert settings.cors_credentials is True
        assert settings.rate_limit_enabled is True
        assert settings.enable_metrics is True
        assert settings.log_level == "INFO"

    def test_api_settings_with_custom_values(self):
        """Test APISettings creation with custom values."""
        custom_secret = "this-is-a-very-long-custom-secret-key-for-testing-purposes"

        settings = APISettings(
            app_name="Custom API",
            version="2.0.0",
            secret_key=SecretStr(custom_secret),
            access_token_expire_minutes=60,
            environment="production",
            cors_origins=["https://example.com", "https://api.example.com"],
            rate_limit_enabled=False,
            log_level="ERROR",
        )

        assert settings.app_name == "Custom API"
        assert settings.version == "2.0.0"
        assert settings.secret_key.get_secret_value() == custom_secret
        assert settings.access_token_expire_minutes == 60
        assert settings.environment == "production"
        assert settings.debug is False  # Auto-set from production environment
        assert settings.cors_origins == ["https://example.com", "https://api.example.com"]
        assert settings.rate_limit_enabled is False
        assert settings.log_level == "ERROR"

    def test_debug_field_validator(self):
        """Test debug field validator auto-sets based on environment."""
        # Development environment should set debug=True
        dev_settings = APISettings(environment="development", debug=False)  # Explicitly set False
        assert dev_settings.debug is True  # Should be overridden to True

        # Production environment should set debug=False
        prod_settings = APISettings(environment="production", debug=True)  # Explicitly set True
        assert prod_settings.debug is False  # Should be overridden to False

        # Testing environment should set debug=False
        test_settings = APISettings(environment="testing", debug=True)  # Explicitly set True
        assert test_settings.debug is False  # Should be overridden to False

    def test_cors_origins_validator_string_parsing(self):
        """Test CORS origins validator parses comma-separated strings."""
        # Use model_validate to test the validator behavior
        data = {
            "cors_origins": "https://example.com,https://api.example.com, https://app.example.com"
        }
        settings = APISettings.model_validate(data)

        expected_origins = [
            "https://example.com",
            "https://api.example.com",
            "https://app.example.com",
        ]
        assert settings.cors_origins == expected_origins

    def test_cors_origins_validator_empty_string(self):
        """Test CORS origins validator handles empty strings."""
        data = {"cors_origins": ""}
        settings = APISettings.model_validate(data)
        assert settings.cors_origins == []

        data = {"cors_origins": ",,,"}
        settings = APISettings.model_validate(data)
        assert settings.cors_origins == []

    def test_cors_origins_validator_list_input(self):
        """Test CORS origins validator handles list input."""
        origins = ["https://example.com", "https://api.example.com"]
        settings = APISettings(cors_origins=origins)
        assert settings.cors_origins == origins

    def test_secret_key_validator_production(self):
        """Test secret key validator enforces minimum length in production."""
        short_key = "short"

        # Should raise validation error in production
        with pytest.raises(ValidationError) as exc_info:
            APISettings(environment="production", secret_key=SecretStr(short_key))

        error_message = str(exc_info.value)
        assert "SECRET_KEY must be at least 32 characters in production" in error_message

    def test_secret_key_validator_development(self):
        """Test secret key validator allows shorter keys in development."""
        short_key = "short"

        # Should not raise error in development
        settings = APISettings(environment="development", secret_key=SecretStr(short_key))
        assert settings.secret_key.get_secret_value() == short_key

    def test_environment_field_validation(self):
        """Test environment field validation with valid and invalid values."""
        # Valid environments
        for env in ["development", "production", "testing"]:
            settings = APISettings(environment=env)
            assert settings.environment == env

        # Invalid environment should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            APISettings(environment="invalid")

        assert "String should match pattern" in str(exc_info.value)

    def test_log_level_field_validation(self):
        """Test log level field validation with valid and invalid values."""
        # Valid log levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = APISettings(log_level=level)
            assert settings.log_level == level

        # Invalid log level should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            APISettings(log_level="INVALID")

        assert "String should match pattern" in str(exc_info.value)

    def test_numeric_field_constraints(self):
        """Test numeric field constraints and validation."""
        # Valid values
        settings = APISettings(
            access_token_expire_minutes=60,
            database_pool_size=20,
            max_request_size=5242880,  # 5MB
            max_concurrent_requests=200,
        )
        assert settings.access_token_expire_minutes == 60
        assert settings.database_pool_size == 20
        assert settings.max_request_size == 5242880
        assert settings.max_concurrent_requests == 200

        # Test boundary values
        with pytest.raises(ValidationError):
            APISettings(access_token_expire_minutes=4)  # Below minimum

        with pytest.raises(ValidationError):
            APISettings(access_token_expire_minutes=10081)  # Above maximum

    def test_environment_detection_properties(self):
        """Test environment detection properties."""
        # Development environment
        dev_settings = APISettings(environment="development")
        assert dev_settings.is_development is True
        assert dev_settings.is_production is False
        assert dev_settings.is_testing is False

        # Production environment
        prod_settings = APISettings(environment="production")
        assert prod_settings.is_development is False
        assert prod_settings.is_production is True
        assert prod_settings.is_testing is False

        # Testing environment
        test_settings = APISettings(environment="testing")
        assert test_settings.is_development is False
        assert test_settings.is_production is False
        assert test_settings.is_testing is True

    def test_get_cors_config_development(self):
        """Test CORS configuration for development environment."""
        settings = APISettings(environment="development", cors_origins=[])
        cors_config = settings.get_cors_config()

        assert cors_config["allow_origins"] == ["http://localhost:3000", "http://127.0.0.1:3000"]
        assert cors_config["allow_credentials"] is True
        assert "GET" in cors_config["allow_methods"]
        assert cors_config["allow_headers"] == ["*"]

    def test_get_cors_config_production(self):
        """Test CORS configuration for production environment."""
        origins = ["https://example.com", "https://api.example.com"]
        settings = APISettings(environment="production", cors_origins=origins)
        cors_config = settings.get_cors_config()

        assert cors_config["allow_origins"] == origins
        assert cors_config["allow_credentials"] is True

    def test_get_cors_config_production_empty_origins(self):
        """Test CORS configuration for production with empty origins."""
        settings = APISettings(environment="production", cors_origins=[])
        cors_config = settings.get_cors_config()

        # In production with no origins, should return empty list (not wildcard)
        assert cors_config["allow_origins"] == []

    @patch.dict(
        os.environ,
        {
            "PROXYWHIRL_SECRET_KEY": "test-secret-key-for-environment-variable-testing",
            "PROXYWHIRL_ENVIRONMENT": "production",
            "PROXYWHIRL_DEBUG": "false",
            "PROXYWHIRL_CORS_ORIGINS": "https://prod.example.com,https://api.prod.example.com",
            "PROXYWHIRL_LOG_LEVEL": "WARNING",
        },
    )
    def test_environment_variable_loading(self):
        """Test loading configuration from environment variables."""
        settings = APISettings()

        assert (
            settings.secret_key.get_secret_value()
            == "test-secret-key-for-environment-variable-testing"
        )
        assert settings.environment == "production"
        assert settings.cors_origins == ["https://prod.example.com", "https://api.prod.example.com"]
        assert settings.log_level == "WARNING"


class TestProxyWhirlSettings:
    """Comprehensive tests for ProxyWhirlSettings model."""

    def test_default_proxywhirl_settings_creation(self):
        """Test ProxyWhirlSettings creation with default values."""
        settings = ProxyWhirlSettings()

        assert settings.cache_type == "memory"
        assert settings.cache_path is None
        assert settings.cache_ttl == 3600
        assert settings.validation_timeout == 10.0
        assert settings.validation_concurrency == 10
        assert settings.circuit_breaker_threshold == 10
        assert settings.max_fetch_proxies is None
        assert settings.auto_validate is True
        assert settings.rotation_strategy == "round_robin"
        assert settings.health_check_interval == 300
        assert settings.proxy_health_threshold == 0.7

    def test_proxywhirl_settings_with_custom_values(self):
        """Test ProxyWhirlSettings creation with custom values."""
        settings = ProxyWhirlSettings(
            cache_type="sqlite",
            cache_path="/tmp/proxies.db",
            cache_ttl=7200,
            validation_timeout=30.0,
            validation_concurrency=20,
            circuit_breaker_threshold=5,
            max_fetch_proxies=1000,
            auto_validate=False,
            rotation_strategy="random",
            health_check_interval=600,
            proxy_health_threshold=0.8,
        )

        assert settings.cache_type == "sqlite"
        assert settings.cache_path == "/tmp/proxies.db"
        assert settings.cache_ttl == 7200
        assert settings.validation_timeout == 30.0
        assert settings.validation_concurrency == 20
        assert settings.circuit_breaker_threshold == 5
        assert settings.max_fetch_proxies == 1000
        assert settings.auto_validate is False
        assert settings.rotation_strategy == "random"
        assert settings.health_check_interval == 600
        assert settings.proxy_health_threshold == 0.8

    def test_cache_type_field_validation(self):
        """Test cache type field validation."""
        # Valid cache types
        for cache_type in ["memory", "json", "sqlite"]:
            settings = ProxyWhirlSettings(cache_type=cache_type)
            assert settings.cache_type == cache_type

        # Invalid cache type should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            ProxyWhirlSettings(cache_type="invalid")

        assert "String should match pattern" in str(exc_info.value)

    def test_numeric_field_constraints_proxywhirl(self):
        """Test numeric field constraints for ProxyWhirl settings."""
        # Test boundary values
        with pytest.raises(ValidationError):
            ProxyWhirlSettings(cache_ttl=59)  # Below minimum

        with pytest.raises(ValidationError):
            ProxyWhirlSettings(cache_ttl=86401)  # Above maximum

        with pytest.raises(ValidationError):
            ProxyWhirlSettings(validation_timeout=0.5)  # Below minimum

        with pytest.raises(ValidationError):
            ProxyWhirlSettings(validation_timeout=61.0)  # Above maximum

        with pytest.raises(ValidationError):
            ProxyWhirlSettings(proxy_health_threshold=0.05)  # Below minimum

        with pytest.raises(ValidationError):
            ProxyWhirlSettings(proxy_health_threshold=1.1)  # Above maximum

    @patch.dict(
        os.environ,
        {
            "PROXYWHIRL_CACHE_TYPE": "sqlite",
            "PROXYWHIRL_CACHE_PATH": "/var/lib/proxywhirl/cache.db",
            "PROXYWHIRL_VALIDATION_TIMEOUT": "25.0",
            "PROXYWHIRL_AUTO_VALIDATE": "false",
        },
    )
    def test_proxywhirl_environment_variable_loading(self):
        """Test loading ProxyWhirl configuration from environment variables."""
        settings = ProxyWhirlSettings()

        assert settings.cache_type == "sqlite"
        assert settings.cache_path == "/var/lib/proxywhirl/cache.db"
        assert settings.validation_timeout == 25.0
        assert settings.auto_validate is False


class TestGlobalSettingsInstances:
    """Tests for global settings instances and helper functions."""

    def test_get_api_settings_returns_instance(self):
        """Test get_api_settings returns APISettings instance."""
        settings = get_api_settings()
        assert isinstance(settings, APISettings)
        assert settings.app_name == "ProxyWhirl API"

    def test_get_proxywhirl_settings_returns_instance(self):
        """Test get_proxywhirl_settings returns ProxyWhirlSettings instance."""
        settings = get_proxywhirl_settings()
        assert isinstance(settings, ProxyWhirlSettings)
        assert settings.cache_type == "memory"

    def test_environment_detection_helpers(self):
        """Test global environment detection helper functions."""
        # Mock the global api_settings for testing
        with patch("proxywhirl.settings.api_settings") as mock_settings:
            mock_settings.is_development = True
            mock_settings.is_production = False
            mock_settings.is_testing = False

            assert is_development() is True
            assert is_production() is False
            assert is_testing() is False

    def test_settings_instances_are_singletons(self):
        """Test that settings instances behave like singletons."""
        settings1 = get_api_settings()
        settings2 = get_api_settings()

        # Should return the same instance
        assert settings1 is settings2

        pw_settings1 = get_proxywhirl_settings()
        pw_settings2 = get_proxywhirl_settings()

        # Should return the same instance
        assert pw_settings1 is pw_settings2


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_cors_origins_string_handling(self):
        """Test handling of empty CORS origins string."""
        data = {"cors_origins": "   ,  ,   "}
        settings = APISettings.model_validate(data)
        assert settings.cors_origins == []

    def test_secret_key_with_exactly_32_characters(self):
        """Test secret key with exactly minimum required length."""
        key_32_chars = "a" * 32
        settings = APISettings(environment="production", secret_key=SecretStr(key_32_chars))
        assert len(settings.secret_key.get_secret_value()) == 32

    def test_secret_key_with_31_characters_fails_production(self):
        """Test secret key with 31 characters fails in production."""
        key_31_chars = "a" * 31
        with pytest.raises(ValidationError):
            APISettings(environment="production", secret_key=SecretStr(key_31_chars))

    def test_maximum_values_validation(self):
        """Test maximum boundary values."""
        # Should work at maximum
        settings = APISettings(
            access_token_expire_minutes=10080,  # Maximum 1 week
            max_concurrent_requests=1000,
        )
        assert settings.access_token_expire_minutes == 10080
        assert settings.max_concurrent_requests == 1000

        # Should work at minimum
        settings = APISettings(
            access_token_expire_minutes=5,  # Minimum 5 minutes
        )
        assert settings.access_token_expire_minutes == 5

    def test_floating_point_precision(self):
        """Test floating point values are handled correctly."""
        settings = ProxyWhirlSettings(
            validation_timeout=10.5,
            proxy_health_threshold=0.75,
        )
        assert settings.validation_timeout == 10.5
        assert settings.proxy_health_threshold == 0.75

    def test_case_insensitive_environment_variables(self):
        """Test that environment variables are case insensitive."""
        with patch.dict(
            os.environ,
            {
                "proxywhirl_log_level": "debug",  # lowercase
                "PROXYWHIRL_ENVIRONMENT": "TESTING",  # uppercase
            },
        ):
            settings = APISettings()
            assert settings.log_level == "DEBUG"  # normalized to uppercase
            assert settings.environment == "testing"  # normalized to lowercase
