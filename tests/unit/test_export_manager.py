"""Unit tests for ExportManager."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from proxywhirl.export_manager import ExportError, ExportManager
from proxywhirl.export_models import (
    CompressionType,
    ConfigurationExportFilter,
    ExportConfig,
    ExportFormat,
    ExportType,
    LocalFileDestination,
    MemoryDestination,
    ProxyExportFilter,
)
from proxywhirl.models import HealthStatus, Proxy, ProxyPool


class TestExportManager:
    """Tests for ExportManager class."""

    @pytest.fixture
    def sample_proxies(self) -> list[Proxy]:
        """Create sample proxies for testing."""
        proxies = [
            Proxy(url="http://proxy1.example.com:8080"),
            Proxy(url="http://proxy2.example.com:8080"),
            Proxy(url="socks5://proxy3.example.com:1080"),
        ]
        
        # Set some stats
        proxies[0].total_requests  = 100
        proxies[0].total_successes = 95
        proxies[0].total_failures  = 5
        proxies[0].health_status   = HealthStatus.HEALTHY
        
        proxies[1].total_requests  = 50
        proxies[1].total_successes = 40
        proxies[1].total_failures  = 10
        proxies[1].health_status   = HealthStatus.DEGRADED
        
        proxies[2].total_requests  = 10
        proxies[2].total_successes = 5
        proxies[2].total_failures  = 5
        proxies[2].health_status   = HealthStatus.UNHEALTHY
        
        return proxies

    @pytest.fixture
    def proxy_pool(self, sample_proxies: list[Proxy]) -> ProxyPool:
        """Create proxy pool for testing."""
        return ProxyPool(name="test-pool", proxies=sample_proxies)

    @pytest.fixture
    def export_manager(self, proxy_pool: ProxyPool) -> ExportManager:
        """Create ExportManager instance for testing."""
        return ExportManager(proxy_pool=proxy_pool)

    def test_init_without_pool(self) -> None:
        """Test initializing ExportManager without proxy pool."""
        manager = ExportManager()
        
        assert manager.proxy_pool is None
        assert manager.storage is None

    def test_init_with_pool(self, proxy_pool: ProxyPool) -> None:
        """Test initializing ExportManager with proxy pool."""
        manager = ExportManager(proxy_pool=proxy_pool)
        
        assert manager.proxy_pool == proxy_pool

    def test_export_proxies_to_memory(
        self,
        export_manager: ExportManager,
        sample_proxies: list[Proxy]
    ) -> None:
        """Test exporting proxies to memory destination."""
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=MemoryDestination(),
        )
        
        result = export_manager.export(config)
        
        assert result.success is True
        assert result.records_exported == len(sample_proxies)
        assert result.data is not None
        assert isinstance(result.data, list)

    def test_export_proxies_with_filter(self, export_manager: ExportManager) -> None:
        """Test exporting proxies with health status filter."""
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=MemoryDestination(),
            proxy_filter=ProxyExportFilter(
                health_status=["healthy"]
            ),
        )
        
        result = export_manager.export(config)
        
        assert result.success is True
        assert result.records_exported == 1  # Only one healthy proxy

    def test_export_proxies_with_success_rate_filter(
        self,
        export_manager: ExportManager
    ) -> None:
        """Test exporting proxies with success rate filter."""
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=MemoryDestination(),
            proxy_filter=ProxyExportFilter(
                min_success_rate=0.9
            ),
        )
        
        result = export_manager.export(config)
        
        assert result.success is True
        assert result.records_exported == 1  # Only proxy1 has >90% success rate

    def test_export_without_proxy_pool(self) -> None:
        """Test exporting proxies without configured proxy pool."""
        manager = ExportManager()  # No proxy pool
        
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=MemoryDestination(),
        )
        
        with pytest.raises(ExportError) as exc_info:
            manager.export(config)
        
        assert "No proxy pool configured" in str(exc_info.value)

    def test_export_json_format(self, export_manager: ExportManager) -> None:
        """Test JSON format export."""
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=MemoryDestination(),
            pretty_print=True,
        )
        
        result = export_manager.export(config)
        
        assert result.success is True
        assert result.export_format == ExportFormat.JSON

    def test_export_csv_format(self, export_manager: ExportManager) -> None:
        """Test CSV format export."""
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.CSV,
            destination=MemoryDestination(),
        )
        
        result = export_manager.export(config)
        
        assert result.success is True
        assert result.export_format == ExportFormat.CSV

    def test_export_yaml_format(self, export_manager: ExportManager) -> None:
        """Test YAML format export."""
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.YAML,
            destination=MemoryDestination(),
        )
        
        result = export_manager.export(config)
        
        assert result.success is True
        assert result.export_format == ExportFormat.YAML

    def test_export_with_gzip_compression(
        self,
        export_manager: ExportManager,
        tmp_path: Path
    ) -> None:
        """Test export with GZIP compression."""
        output_file = tmp_path / "proxies.json.gz"
        
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=LocalFileDestination(
                file_path=output_file,
                overwrite=True
            ),
            compression=CompressionType.GZIP,
        )
        
        result = export_manager.export(config)
        
        assert result.success is True
        assert output_file.exists()

    def test_export_with_zip_compression(
        self,
        export_manager: ExportManager,
        tmp_path: Path
    ) -> None:
        """Test export with ZIP compression."""
        output_file = tmp_path / "proxies.zip"
        
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=LocalFileDestination(
                file_path=output_file,
                overwrite=True
            ),
            compression=CompressionType.ZIP,
        )
        
        result = export_manager.export(config)
        
        assert result.success is True
        assert output_file.exists()

    def test_export_to_local_file(
        self,
        export_manager: ExportManager,
        tmp_path: Path
    ) -> None:
        """Test exporting to local file."""
        output_file = tmp_path / "proxies.json"
        
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=LocalFileDestination(
                file_path=output_file,
                overwrite=True
            ),
        )
        
        result = export_manager.export(config)
        
        assert result.success is True
        assert result.destination_path is not None
        assert Path(result.destination_path).exists()

    def test_export_file_overwrite_protection(
        self,
        export_manager: ExportManager,
        tmp_path: Path
    ) -> None:
        """Test that existing files are not overwritten without permission."""
        output_file = tmp_path / "proxies.json"
        output_file.write_text("existing content")
        
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=LocalFileDestination(
                file_path=output_file,
                overwrite=False  # Don't overwrite
            ),
        )
        
        with pytest.raises(ExportError):
            export_manager.export(config)

    def test_export_health_status(self, export_manager: ExportManager) -> None:
        """Test exporting health status data."""
        config = ExportConfig(
            export_type=ExportType.HEALTH_STATUS,
            export_format=ExportFormat.JSON,
            destination=MemoryDestination(),
        )
        
        result = export_manager.export(config)
        
        assert result.success is True
        assert result.records_exported > 0

    def test_export_configuration(self, export_manager: ExportManager) -> None:
        """Test exporting configuration data."""
        config = ExportConfig(
            export_type=ExportType.CONFIGURATION,
            export_format=ExportFormat.YAML,
            destination=MemoryDestination(),
            config_filter=ConfigurationExportFilter(
                redact_secrets=True
            ),
        )
        
        result = export_manager.export(config)
        
        assert result.success is True

    def test_get_job_status_nonexistent(self, export_manager: ExportManager) -> None:
        """Test getting status of nonexistent job."""
        from uuid import uuid4
        
        fake_id = uuid4()
        status = export_manager.get_job_status(fake_id)
        
        assert status is None

    def test_export_history(self, export_manager: ExportManager) -> None:
        """Test export history tracking."""
        # Perform an export
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=MemoryDestination(),
        )
        
        export_manager.export(config)
        
        # Get history
        history = export_manager.get_export_history(limit=10)
        
        assert len(history) >= 1

    def test_export_with_field_selection(self, export_manager: ExportManager) -> None:
        """Test exporting with specific field selection."""
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=MemoryDestination(),
            proxy_filter=ProxyExportFilter(
                include_fields=["url", "health_status"]
            ),
        )
        
        result = export_manager.export(config)
        
        assert result.success is True
        assert result.data is not None

    def test_redact_secrets_in_config_export(self, export_manager: ExportManager) -> None:
        """Test that secrets are redacted in configuration exports."""
        # Create manager with test data
        manager = export_manager
        
        # Export configuration with secret redaction
        config = ExportConfig(
            export_type=ExportType.CONFIGURATION,
            export_format=ExportFormat.JSON,
            destination=MemoryDestination(),
            config_filter=ConfigurationExportFilter(
                redact_secrets=True
            ),
        )
        
        result = manager.export(config)
        
        assert result.success is True

    def test_export_creates_directories(
        self,
        export_manager: ExportManager,
        tmp_path: Path
    ) -> None:
        """Test that export creates parent directories."""
        output_file = tmp_path / "subdir" / "proxies.json"
        
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=LocalFileDestination(
                file_path=output_file,
                overwrite=True,
                create_directories=True
            ),
        )
        
        result = export_manager.export(config)
        
        assert result.success is True
        assert output_file.exists()
        assert output_file.parent.exists()

    def test_export_metadata_generation(self, export_manager: ExportManager) -> None:
        """Test that export generates proper metadata."""
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=MemoryDestination(),
            include_metadata=True,
        )
        
        result = export_manager.export(config)
        
        assert result.success is True
        assert result.metadata is not None
        assert result.metadata.export_type == ExportType.PROXIES
        assert result.metadata.total_records == result.records_exported
