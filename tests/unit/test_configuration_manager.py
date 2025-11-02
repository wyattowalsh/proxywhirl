"""Unit tests for ConfigurationManager."""

import tempfile
from pathlib import Path

import pytest

from proxywhirl import (
    ConfigurationManager,
    ConfigurationSource,
    ProxyWhirlSettings,
    User,
)


class TestConfigurationManager:
    """Tests for ConfigurationManager class."""
    
    def test_initialization(self) -> None:
        """Test configuration manager initialization."""
        manager = ConfigurationManager()
        assert manager.get_config() is not None
        assert isinstance(manager.get_config(), ProxyWhirlSettings)
    
    def test_initialization_with_config(self) -> None:
        """Test initialization with custom config."""
        config = ProxyWhirlSettings(timeout=10, max_retries=5)
        manager = ConfigurationManager(config=config)
        
        current = manager.get_config()
        assert current.timeout == 10
        assert current.max_retries == 5
    
    def test_get_config_thread_safe(self) -> None:
        """Test get_config is thread-safe."""
        manager = ConfigurationManager()
        config1 = manager.get_config()
        config2 = manager.get_config()
        
        # Should return consistent values
        assert config1.timeout == config2.timeout
    
    def test_get_sources(self) -> None:
        """Test get_sources method."""
        manager = ConfigurationManager()
        sources = manager.get_sources()
        
        assert isinstance(sources, dict)
        assert 'timeout' in sources
        assert sources['timeout'] == ConfigurationSource.DEFAULT
    
    def test_validate_updates_success(self) -> None:
        """Test successful validation of updates."""
        manager = ConfigurationManager()
        updates = {'timeout': 10, 'max_retries': 5}
        
        result = manager.validate_updates(updates)
        
        assert result.valid is True
        assert len(result.errors) == 0
    
    def test_validate_updates_invalid_value(self) -> None:
        """Test validation with invalid value."""
        manager = ConfigurationManager()
        updates = {'timeout': 500}  # Exceeds max of 300
        
        result = manager.validate_updates(updates)
        
        assert result.valid is False
        assert len(result.errors) > 0
    
    def test_validate_updates_restart_required(self) -> None:
        """Test validation rejects restart-required fields."""
        manager = ConfigurationManager()
        updates = {'server_port': 9000}  # Restart required
        
        result = manager.validate_updates(updates)
        
        assert result.valid is False
        assert any('restart-required' in e.message for e in result.errors)
    
    def test_validate_updates_with_warnings(self) -> None:
        """Test validation with warnings."""
        manager = ConfigurationManager()
        updates = {'timeout': 1}  # Very low value
        
        result = manager.validate_updates(updates)
        
        assert result.valid is True
        assert result.has_warnings is True
        assert any('very low' in w for w in result.warnings)
    
    def test_update_runtime_config_success(self) -> None:
        """Test successful runtime update."""
        manager = ConfigurationManager()
        admin = User(id="a1", username="admin", is_admin=True)
        
        updates = {'timeout': 10, 'max_retries': 5}
        manager.update_runtime_config(updates, admin)
        
        config = manager.get_config()
        assert config.timeout == 10
        assert config.max_retries == 5
    
    def test_update_runtime_config_authorization(self) -> None:
        """Test runtime update requires admin."""
        manager = ConfigurationManager()
        regular_user = User(id="u1", username="user", is_admin=False)
        
        updates = {'timeout': 10}
        
        with pytest.raises(PermissionError, match="admin privileges"):
            manager.update_runtime_config(updates, regular_user)
    
    def test_update_runtime_config_validation_error(self) -> None:
        """Test runtime update with invalid values."""
        manager = ConfigurationManager()
        admin = User(id="a1", username="admin", is_admin=True)
        
        updates = {'timeout': 500}  # Invalid
        
        with pytest.raises(ValueError, match="validation failed"):
            manager.update_runtime_config(updates, admin)
    
    def test_update_runtime_config_updates_sources(self) -> None:
        """Test that runtime updates update sources."""
        manager = ConfigurationManager()
        admin = User(id="a1", username="admin", is_admin=True)
        
        manager.update_runtime_config({'timeout': 10}, admin)
        
        sources = manager.get_sources()
        assert sources['timeout'] == ConfigurationSource.RUNTIME_UPDATE
    
    def test_rollback_success(self) -> None:
        """Test successful configuration rollback."""
        manager = ConfigurationManager()
        admin = User(id="a1", username="admin", is_admin=True)
        
        original_timeout = manager.get_config().timeout
        
        # Make an update
        manager.update_runtime_config({'timeout': 20}, admin)
        assert manager.get_config().timeout == 20
        
        # Rollback
        success = manager.rollback()
        assert success is True
        assert manager.get_config().timeout == original_timeout
    
    def test_rollback_no_previous_config(self) -> None:
        """Test rollback with no previous config."""
        manager = ConfigurationManager()
        
        success = manager.rollback()
        assert success is False
    
    def test_reload_from_yaml(self) -> None:
        """Test reload from YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("timeout: 15\nmax_retries: 7\n")
            config_path = f.name
        
        try:
            manager = ConfigurationManager(config_path=config_path)
            
            # Modify file
            with open(config_path, 'w') as f:
                f.write("timeout: 25\nmax_retries: 9\n")
            
            # Reload
            manager.reload()
            
            config = manager.get_config()
            assert config.timeout == 25
            assert config.max_retries == 9
        finally:
            Path(config_path).unlink()
    
    def test_reload_validation_failure(self) -> None:
        """Test reload with invalid configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("timeout: 10\n")
            config_path = f.name
        
        try:
            manager = ConfigurationManager(config_path=config_path)
            
            # Write invalid config
            with open(config_path, 'w') as f:
                f.write("timeout: 500\n")  # Invalid
            
            # Reload should fail
            with pytest.raises(ValueError, match="Invalid configuration"):
                manager.reload()
        finally:
            Path(config_path).unlink()
    
    def test_export_config(self) -> None:
        """Test configuration export."""
        config = ProxyWhirlSettings(timeout=10, max_retries=5)
        manager = ConfigurationManager(config=config)
        
        yaml_output = manager.export_config()
        
        assert 'ProxyWhirl Configuration Snapshot' in yaml_output
        assert 'timeout: 10' in yaml_output
        assert 'max_retries: 5' in yaml_output
    
    def test_export_config_to_file(self) -> None:
        """Test export to file."""
        manager = ConfigurationManager()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "export.yaml"
            manager.export_config_to_file(export_path)
            
            assert export_path.exists()
            content = export_path.read_text()
            assert 'ProxyWhirl Configuration Snapshot' in content
    
    def test_get_config_history(self) -> None:
        """Test configuration history tracking."""
        manager = ConfigurationManager()
        admin = User(id="a1", username="admin", is_admin=True)
        
        # Make multiple updates
        manager.update_runtime_config({'timeout': 10}, admin)
        manager.update_runtime_config({'max_retries': 5}, admin)
        
        history = manager.get_config_history(limit=10)
        
        assert len(history) >= 2
        assert history[0].version > history[1].version  # Most recent first
    
    def test_concurrent_conflict_detection(self) -> None:
        """Test concurrent update conflict detection."""
        manager = ConfigurationManager()
        admin1 = User(id="a1", username="admin1", is_admin=True)
        admin2 = User(id="a2", username="admin2", is_admin=True)
        
        # First update
        manager.update_runtime_config({'timeout': 10}, admin1)
        
        # Concurrent update (no error, but warning logged)
        manager.update_runtime_config({'timeout': 15}, admin2)
        
        # Should succeed with last-write-wins
        assert manager.get_config().timeout == 15
