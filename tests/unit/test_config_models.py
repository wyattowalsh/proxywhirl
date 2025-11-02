"""Unit tests for configuration models."""

import pytest
from datetime import datetime, timezone

from proxywhirl.config_models import (
    ConfigUpdate,
    ConfigurationSnapshot,
    ConfigurationSource,
    ProxyWhirlSettings,
    User,
    ValidationError,
    ValidationResult,
)


class TestUser:
    """Tests for User model."""
    
    def test_user_creation(self) -> None:
        """Test basic user creation."""
        user = User(id="u123", username="test_user")
        assert user.id == "u123"
        assert user.username == "test_user"
        assert user.is_admin is False
        assert user.email is None
    
    def test_admin_user(self) -> None:
        """Test admin user creation."""
        user = User(id="a123", username="admin", is_admin=True, email="admin@example.com")
        assert user.is_admin is True
        assert user.email == "admin@example.com"
    
    def test_require_admin_success(self) -> None:
        """Test require_admin for admin user."""
        user = User(id="a123", username="admin", is_admin=True)
        user.require_admin()  # Should not raise
    
    def test_require_admin_failure(self) -> None:
        """Test require_admin for non-admin user."""
        user = User(id="u123", username="user", is_admin=False)
        with pytest.raises(PermissionError, match="does not have admin privileges"):
            user.require_admin()


class TestValidationResult:
    """Tests for ValidationResult model."""
    
    def test_valid_result(self) -> None:
        """Test valid validation result."""
        result = ValidationResult(valid=True, errors=[], warnings=[])
        assert result.valid is True
        assert result.has_errors is False
        assert result.has_warnings is False
    
    def test_result_with_errors(self) -> None:
        """Test validation result with errors."""
        errors = [
            ValidationError(field="timeout", message="Too high", value=1000)
        ]
        result = ValidationResult(valid=False, errors=errors)
        assert result.valid is False
        assert result.has_errors is True
        assert len(result.errors) == 1
    
    def test_result_with_warnings(self) -> None:
        """Test validation result with warnings."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=["Timeout is very low"]
        )
        assert result.valid is True
        assert result.has_errors is False
        assert result.has_warnings is True
    
    def test_raise_if_invalid(self) -> None:
        """Test raise_if_invalid method."""
        errors = [ValidationError(field="timeout", message="Invalid", value=-1)]
        result = ValidationResult(valid=False, errors=errors)
        
        with pytest.raises(ValueError, match="Configuration validation failed"):
            result.raise_if_invalid()


class TestConfigUpdate:
    """Tests for ConfigUpdate model."""
    
    def test_config_update_creation(self) -> None:
        """Test config update creation."""
        update = ConfigUpdate(
            user_id="u123",
            username="test_user",
            timestamp=datetime.now(timezone.utc),
            changes={'timeout': 10},
            version=1
        )
        assert update.user_id == "u123"
        assert update.version == 1
        assert update.source == ConfigurationSource.RUNTIME_UPDATE
    
    def test_get_changed_keys(self) -> None:
        """Test get_changed_keys method."""
        update = ConfigUpdate(
            user_id="u123",
            username="user",
            timestamp=datetime.now(timezone.utc),
            changes={'timeout': 10, 'max_retries': 5},
            version=1
        )
        keys = update.get_changed_keys()
        assert keys == {'timeout', 'max_retries'}
    
    def test_conflicts_with(self) -> None:
        """Test conflicts_with method."""
        update1 = ConfigUpdate(
            user_id="u1",
            username="user1",
            timestamp=datetime.now(timezone.utc),
            changes={'timeout': 10, 'max_retries': 5},
            version=1
        )
        update2 = ConfigUpdate(
            user_id="u2",
            username="user2",
            timestamp=datetime.now(timezone.utc),
            changes={'timeout': 15, 'log_level': 'DEBUG'},
            version=2
        )
        
        conflicts = update1.conflicts_with(update2)
        assert conflicts == {'timeout'}


class TestProxyWhirlSettings:
    """Tests for ProxyWhirlSettings model."""
    
    def test_default_settings(self) -> None:
        """Test default configuration values."""
        config = ProxyWhirlSettings()
        assert config.timeout == 5
        assert config.max_retries == 3
        assert config.log_level == 'INFO'
        assert config.server_port == 8000
        assert config.rate_limit_requests == 100
    
    def test_custom_settings(self) -> None:
        """Test custom configuration values."""
        config = ProxyWhirlSettings(
            timeout=10,
            max_retries=5,
            log_level='DEBUG'
        )
        assert config.timeout == 10
        assert config.max_retries == 5
        assert config.log_level == 'DEBUG'
    
    def test_timeout_validation(self) -> None:
        """Test timeout field validation."""
        with pytest.raises(Exception):  # Pydantic validation error
            ProxyWhirlSettings(timeout=-1)
        
        with pytest.raises(Exception):
            ProxyWhirlSettings(timeout=500)  # Exceeds max of 300
    
    def test_max_retries_validation(self) -> None:
        """Test max_retries field validation."""
        with pytest.raises(Exception):
            ProxyWhirlSettings(max_retries=-1)
        
        with pytest.raises(Exception):
            ProxyWhirlSettings(max_retries=20)  # Exceeds max of 10
    
    def test_log_level_validation(self) -> None:
        """Test log level validation."""
        config = ProxyWhirlSettings(log_level='debug')
        assert config.log_level == 'DEBUG'  # Should be uppercased
    
    def test_database_path_validation(self) -> None:
        """Test database path validation."""
        config = ProxyWhirlSettings(database_path='mydb')
        assert config.database_path == 'mydb.db'  # .db extension added
    
    def test_server_port_validation(self) -> None:
        """Test server port validation."""
        with pytest.raises(Exception):
            ProxyWhirlSettings(server_port=80)  # Below 1024
        
        with pytest.raises(Exception):
            ProxyWhirlSettings(server_port=70000)  # Above 65535
    
    def test_is_hot_reloadable(self) -> None:
        """Test is_hot_reloadable method."""
        config = ProxyWhirlSettings()
        
        # Hot-reloadable fields
        assert config.is_hot_reloadable('timeout') is True
        assert config.is_hot_reloadable('max_retries') is True
        assert config.is_hot_reloadable('log_level') is True
        
        # Restart-required fields
        assert config.is_hot_reloadable('proxy_url') is False
        assert config.is_hot_reloadable('database_path') is False
        assert config.is_hot_reloadable('server_port') is False
    
    def test_get_restart_required_fields(self) -> None:
        """Test get_restart_required_fields method."""
        config = ProxyWhirlSettings()
        restart_fields = config.get_restart_required_fields()
        
        assert 'proxy_url' in restart_fields
        assert 'database_path' in restart_fields
        assert 'server_host' in restart_fields
        assert 'server_port' in restart_fields
        
        assert 'timeout' not in restart_fields
        assert 'max_retries' not in restart_fields


class TestConfigurationSnapshot:
    """Tests for ConfigurationSnapshot model."""
    
    def test_from_config(self) -> None:
        """Test snapshot creation from config."""
        config = ProxyWhirlSettings(timeout=10, max_retries=5)
        sources = {
            'timeout': ConfigurationSource.CLI_ARGUMENT,
            'max_retries': ConfigurationSource.YAML_FILE,
        }
        
        snapshot = ConfigurationSnapshot.from_config(config, sources)
        
        assert 'timeout' in snapshot.settings
        assert snapshot.settings['timeout'] == 10
        assert 'timeout' in snapshot.sources
        assert snapshot.sources['timeout'] == ConfigurationSource.CLI_ARGUMENT
    
    def test_credential_redaction(self) -> None:
        """Test that credentials are redacted in snapshots."""
        from pydantic import SecretStr
        
        config = ProxyWhirlSettings(
            timeout=10,
            proxy_url=SecretStr('http://user:pass@proxy.com:8080')
        )
        sources = {}
        
        snapshot = ConfigurationSnapshot.from_config(config, sources)
        
        # Credentials should be redacted
        assert snapshot.settings['proxy_url'] == "*** REDACTED ***"
    
    def test_to_yaml(self) -> None:
        """Test YAML export."""
        config = ProxyWhirlSettings(timeout=10, max_retries=5)
        sources = {
            'timeout': ConfigurationSource.CLI_ARGUMENT,
            'max_retries': ConfigurationSource.YAML_FILE,
        }
        
        snapshot = ConfigurationSnapshot.from_config(config, sources)
        yaml_output = snapshot.to_yaml()
        
        assert 'ProxyWhirl Configuration Snapshot' in yaml_output
        assert 'timeout: 10' in yaml_output
        assert 'max_retries: 5' in yaml_output
        assert 'Source: cli_argument' in yaml_output
        assert 'Source: yaml_file' in yaml_output
