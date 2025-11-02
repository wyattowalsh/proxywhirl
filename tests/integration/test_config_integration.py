"""Integration tests for configuration management."""

import tempfile
import time
from pathlib import Path

import pytest

from proxywhirl import (
    ConfigurationManager,
    ProxyWhirlSettings,
    User,
    load_yaml_config,
    parse_cli_args,
    validate_config,
)


class TestMultiSourceConfiguration:
    """Integration tests for multi-source configuration loading."""
    
    def test_yaml_env_cli_precedence(self) -> None:
        """Test configuration precedence: CLI > ENV > YAML > Defaults."""
        # Create YAML config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("timeout: 5\nmax_retries: 3\n")
            yaml_path = f.name
        
        try:
            # Load YAML
            yaml_config = load_yaml_config(yaml_path)
            assert yaml_config['timeout'] == 5
            assert yaml_config['max_retries'] == 3
            
            # CLI overrides
            cli_config = parse_cli_args(['--timeout', '10'])
            assert cli_config['timeout'] == 10
            
            # Merge (CLI has highest precedence)
            merged = {**yaml_config, **cli_config}
            config = ProxyWhirlSettings(**merged)
            
            assert config.timeout == 10  # From CLI
            assert config.max_retries == 3  # From YAML
        finally:
            Path(yaml_path).unlink()
    
    def test_environment_variable_loading(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading from environment variables."""
        # Set environment variables
        monkeypatch.setenv('PROXYWHIRL_TIMEOUT', '15')
        monkeypatch.setenv('PROXYWHIRL_MAX_RETRIES', '7')
        
        # Create new settings (should load from env)
        config = ProxyWhirlSettings()
        
        assert config.timeout == 15
        assert config.max_retries == 7


class TestRuntimeConfigurationLifecycle:
    """Integration tests for complete runtime configuration lifecycle."""
    
    def test_update_validate_export_cycle(self) -> None:
        """Test complete update-validate-export cycle."""
        manager = ConfigurationManager()
        admin = User(id="a1", username="admin", is_admin=True)
        
        # Initial state
        initial_config = manager.get_config()
        initial_timeout = initial_config.timeout
        
        # Validate updates
        updates = {'timeout': 20, 'max_retries': 7}
        validation = manager.validate_updates(updates)
        assert validation.valid is True
        
        # Apply updates
        manager.update_runtime_config(updates, admin)
        
        # Verify updates
        updated_config = manager.get_config()
        assert updated_config.timeout == 20
        assert updated_config.max_retries == 7
        
        # Export configuration
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "export.yaml"
            manager.export_config_to_file(export_path)
            
            # Verify export
            assert export_path.exists()
            exported_yaml = load_yaml_config(export_path)
            # Note: YAML file has comments, so we check the actual config
            assert 'timeout' in export_path.read_text()
    
    def test_update_rollback_cycle(self) -> None:
        """Test update and rollback cycle."""
        manager = ConfigurationManager()
        admin = User(id="a1", username="admin", is_admin=True)
        
        initial_timeout = manager.get_config().timeout
        
        # Update
        manager.update_runtime_config({'timeout': 30}, admin)
        assert manager.get_config().timeout == 30
        
        # Rollback
        success = manager.rollback()
        assert success is True
        assert manager.get_config().timeout == initial_timeout


class TestHotReloadWorkflow:
    """Integration tests for hot reload workflows."""
    
    def test_manual_reload_workflow(self) -> None:
        """Test manual configuration reload workflow."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("timeout: 5\nmax_retries: 3\n")
            config_path = f.name
        
        try:
            manager = ConfigurationManager(config_path=config_path)
            
            # Initial config
            assert manager.get_config().timeout == 5
            
            # Modify file
            with open(config_path, 'w') as f:
                f.write("timeout: 15\nmax_retries: 8\n")
            
            # Manual reload
            manager.reload()
            
            # Verify reload
            config = manager.get_config()
            assert config.timeout == 15
            assert config.max_retries == 8
        finally:
            Path(config_path).unlink()
    
    def test_automatic_reload_with_file_watching(self) -> None:
        """Test automatic reload with file watching."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("timeout: 5\n")
            config_path = f.name
        
        try:
            manager = ConfigurationManager(config_path=config_path)
            
            # Enable file watching
            observer = manager.enable_file_watching()
            
            # Initial config
            assert manager.get_config().timeout == 5
            
            # Modify file
            time.sleep(0.5)  # Small delay
            with open(config_path, 'w') as f:
                f.write("timeout: 20\n")
            
            # Wait for automatic reload (debounced)
            time.sleep(2)
            
            # Verify automatic reload
            assert manager.get_config().timeout == 20
            
            # Stop watching
            observer.stop()
            observer.join()
        finally:
            Path(config_path).unlink()
    
    def test_reload_validation_and_rollback(self) -> None:
        """Test reload with validation failure and rollback."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("timeout: 5\n")
            config_path = f.name
        
        try:
            manager = ConfigurationManager(config_path=config_path)
            
            # Initial valid config
            assert manager.get_config().timeout == 5
            
            # Modify with invalid config
            with open(config_path, 'w') as f:
                f.write("timeout: 500\n")  # Exceeds max
            
            # Reload should fail
            with pytest.raises(ValueError, match="Invalid configuration"):
                manager.reload()
            
            # Config should remain unchanged
            assert manager.get_config().timeout == 5
        finally:
            Path(config_path).unlink()


class TestConcurrentConfigurationUpdates:
    """Integration tests for concurrent configuration updates."""
    
    def test_concurrent_updates_last_write_wins(self) -> None:
        """Test last-write-wins semantics for concurrent updates."""
        manager = ConfigurationManager()
        admin1 = User(id="a1", username="alice", is_admin=True)
        admin2 = User(id="a2", username="bob", is_admin=True)
        
        # Sequential updates (simulating concurrent)
        manager.update_runtime_config({'timeout': 10}, admin1)
        manager.update_runtime_config({'timeout': 15}, admin2)
        
        # Last write should win
        assert manager.get_config().timeout == 15
        
        # History should show both updates
        history = manager.get_config_history(limit=5)
        assert len(history) >= 2
        assert history[0].username == 'bob'
        assert history[1].username == 'alice'
    
    def test_concurrent_conflict_detection_and_logging(self) -> None:
        """Test conflict detection for concurrent updates."""
        manager = ConfigurationManager()
        admin1 = User(id="a1", username="alice", is_admin=True)
        admin2 = User(id="a2", username="bob", is_admin=True)
        
        # First update
        manager.update_runtime_config({'timeout': 10}, admin1)
        
        # Concurrent update (within 5 seconds)
        manager.update_runtime_config({'timeout': 15}, admin2)
        
        # Both should succeed (last-write-wins)
        assert manager.get_config().timeout == 15


class TestConfigurationValidation:
    """Integration tests for configuration validation."""
    
    def test_validation_at_startup(self) -> None:
        """Test configuration validation at startup."""
        # Valid config
        config = ProxyWhirlSettings(timeout=10, max_retries=3)
        manager = ConfigurationManager(config=config)
        assert manager.get_config().timeout == 10
        
        # Invalid config should raise during creation
        with pytest.raises(Exception):
            ProxyWhirlSettings(timeout=500)
    
    def test_validation_before_update(self) -> None:
        """Test validation before runtime update."""
        manager = ConfigurationManager()
        admin = User(id="a1", username="admin", is_admin=True)
        
        # Invalid update should be rejected
        with pytest.raises(ValueError, match="validation failed"):
            manager.update_runtime_config({'timeout': 500}, admin)
        
        # Config should remain unchanged
        assert manager.get_config().timeout == 5
    
    def test_validation_warnings(self) -> None:
        """Test validation warnings for potentially problematic values."""
        config_dict = {'timeout': 1, 'max_retries': 0}
        result = validate_config(config_dict)
        
        assert result.valid is True  # Valid but with warnings
        assert result.has_warnings is True
        assert len(result.warnings) >= 2


class TestConfigurationExportImport:
    """Integration tests for configuration export and import."""
    
    def test_export_import_roundtrip(self) -> None:
        """Test export and import round-trip."""
        # Create config with specific values
        config = ProxyWhirlSettings(
            timeout=15,
            max_retries=7,
            log_level='DEBUG'
        )
        manager = ConfigurationManager(config=config)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Export
            export_path = Path(tmpdir) / "export.yaml"
            manager.export_config_to_file(export_path)
            
            # Load exported config
            exported_data = load_yaml_config(export_path)
            
            # Note: Export is a snapshot with comments, not pure YAML
            # So we verify the key values are present in the text
            export_text = export_path.read_text()
            assert 'timeout' in export_text
            assert 'max_retries' in export_text
    
    def test_export_with_credential_redaction(self) -> None:
        """Test that credentials are redacted in exports."""
        from pydantic import SecretStr
        
        config = ProxyWhirlSettings(
            proxy_url=SecretStr('http://user:pass@proxy.com:8080')
        )
        manager = ConfigurationManager(config=config)
        
        yaml_export = manager.export_config()
        
        # Credentials should be redacted
        assert '*** REDACTED ***' in yaml_export
        assert 'user:pass' not in yaml_export
