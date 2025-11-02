"""Integration tests for export API endpoints."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestExportAPIEndpoints:
    """Integration tests for /api/v1/exports endpoints."""

    @pytest.fixture
    def api_client(self) -> TestClient:
        """Create FastAPI test client."""
        from proxywhirl.api import app
        
        return TestClient(app)

    @pytest.fixture
    def setup_test_proxies(self, api_client: TestClient) -> None:
        """Add test proxies to the pool."""
        # Add some test proxies
        proxies = [
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080",
            "socks5://proxy3.example.com:1080",
        ]
        
        for proxy_url in proxies:
            response = api_client.post(
                "/api/v1/proxies",
                json={"url": proxy_url}
            )
            assert response.status_code in [200, 201]

    def test_export_proxies_to_memory(
        self,
        api_client: TestClient,
        setup_test_proxies: None
    ) -> None:
        """Test exporting proxies to memory via API."""
        request_data = {
            "export_type": "proxies",
            "export_format": "json",
            "destination_type": "memory",
            "pretty_print": True,
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["status"] == "success"
        assert data["data"]["status"] == "completed"
        assert data["data"]["export_type"] == "proxies"
        assert data["data"]["records_exported"] >= 0

    def test_export_proxies_to_file(
        self,
        api_client: TestClient,
        setup_test_proxies: None,
        tmp_path: Path
    ) -> None:
        """Test exporting proxies to file via API."""
        output_file = tmp_path / "proxies_export.json"
        
        request_data = {
            "export_type": "proxies",
            "export_format": "json",
            "destination_type": "local_file",
            "file_path": str(output_file),
            "overwrite": True,
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["status"] == "success"
        assert output_file.exists()

    def test_export_with_health_status_filter(
        self,
        api_client: TestClient,
        setup_test_proxies: None
    ) -> None:
        """Test exporting proxies with health status filter."""
        request_data = {
            "export_type": "proxies",
            "export_format": "json",
            "destination_type": "memory",
            "health_status": ["healthy", "unknown"],
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 201

    def test_export_csv_format(
        self,
        api_client: TestClient,
        setup_test_proxies: None
    ) -> None:
        """Test exporting in CSV format."""
        request_data = {
            "export_type": "proxies",
            "export_format": "csv",
            "destination_type": "memory",
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["data"]["export_format"] == "csv"

    def test_export_yaml_format(
        self,
        api_client: TestClient,
        setup_test_proxies: None
    ) -> None:
        """Test exporting in YAML format."""
        request_data = {
            "export_type": "proxies",
            "export_format": "yaml",
            "destination_type": "memory",
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["data"]["export_format"] == "yaml"

    def test_export_with_gzip_compression(
        self,
        api_client: TestClient,
        setup_test_proxies: None,
        tmp_path: Path
    ) -> None:
        """Test exporting with GZIP compression."""
        output_file = tmp_path / "proxies.json.gz"
        
        request_data = {
            "export_type": "proxies",
            "export_format": "json",
            "destination_type": "local_file",
            "file_path": str(output_file),
            "compression": "gzip",
            "overwrite": True,
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 201
        assert output_file.exists()

    def test_export_with_zip_compression(
        self,
        api_client: TestClient,
        setup_test_proxies: None,
        tmp_path: Path
    ) -> None:
        """Test exporting with ZIP compression."""
        output_file = tmp_path / "proxies.zip"
        
        request_data = {
            "export_type": "proxies",
            "export_format": "json",
            "destination_type": "local_file",
            "file_path": str(output_file),
            "compression": "zip",
            "overwrite": True,
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 201
        assert output_file.exists()

    def test_export_health_status(
        self,
        api_client: TestClient,
        setup_test_proxies: None
    ) -> None:
        """Test exporting health status data."""
        request_data = {
            "export_type": "health_status",
            "export_format": "json",
            "destination_type": "memory",
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["data"]["export_type"] == "health_status"

    def test_export_configuration(self, api_client: TestClient) -> None:
        """Test exporting configuration data."""
        request_data = {
            "export_type": "configuration",
            "export_format": "yaml",
            "destination_type": "memory",
            "redact_secrets": True,
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["data"]["export_type"] == "configuration"

    def test_export_metrics_requires_time_range(self, api_client: TestClient) -> None:
        """Test that metrics export requires time range."""
        request_data = {
            "export_type": "metrics",
            "export_format": "json",
            "destination_type": "memory",
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        # Should fail without start_time and end_time
        assert response.status_code == 400

    def test_export_metrics_with_time_range(self, api_client: TestClient) -> None:
        """Test exporting metrics with time range."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)
        
        request_data = {
            "export_type": "metrics",
            "export_format": "json",
            "destination_type": "memory",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 201

    def test_export_logs_with_filter(self, api_client: TestClient) -> None:
        """Test exporting logs with filtering."""
        request_data = {
            "export_type": "logs",
            "export_format": "json",
            "destination_type": "memory",
            "log_levels": ["ERROR", "CRITICAL"],
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 201

    def test_export_invalid_type(self, api_client: TestClient) -> None:
        """Test exporting with invalid export type."""
        request_data = {
            "export_type": "invalid_type",
            "export_format": "json",
            "destination_type": "memory",
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 400

    def test_export_invalid_format(self, api_client: TestClient) -> None:
        """Test exporting with invalid format."""
        request_data = {
            "export_type": "proxies",
            "export_format": "invalid_format",
            "destination_type": "memory",
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 400

    def test_export_missing_file_path(self, api_client: TestClient) -> None:
        """Test export to file without file_path."""
        request_data = {
            "export_type": "proxies",
            "export_format": "json",
            "destination_type": "local_file",
            # Missing file_path
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 400

    def test_get_export_status_invalid_job_id(self, api_client: TestClient) -> None:
        """Test getting status with invalid job ID."""
        response = api_client.get("/api/v1/exports/invalid-uuid")
        
        assert response.status_code == 400

    def test_get_export_status_nonexistent(self, api_client: TestClient) -> None:
        """Test getting status of nonexistent export."""
        from uuid import uuid4
        
        fake_id = str(uuid4())
        response = api_client.get(f"/api/v1/exports/{fake_id}")
        
        assert response.status_code == 404

    def test_get_export_history(self, api_client: TestClient) -> None:
        """Test getting export history."""
        response = api_client.get("/api/v1/exports/history")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "total_exports" in data["data"]
        assert "exports" in data["data"]

    def test_export_history_with_limit(self, api_client: TestClient) -> None:
        """Test getting export history with limit."""
        response = api_client.get("/api/v1/exports/history?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]["exports"]) <= 5

    def test_export_multiple_formats(
        self,
        api_client: TestClient,
        setup_test_proxies: None,
        tmp_path: Path
    ) -> None:
        """Test exporting to multiple formats sequentially."""
        formats = ["json", "csv", "yaml", "markdown"]
        
        for fmt in formats:
            output_file = tmp_path / f"proxies.{fmt}"
            
            request_data = {
                "export_type": "proxies",
                "export_format": fmt,
                "destination_type": "local_file",
                "file_path": str(output_file),
                "overwrite": True,
            }
            
            response = api_client.post("/api/v1/exports", json=request_data)
            
            assert response.status_code == 201
            assert output_file.exists()

    def test_export_with_protocol_filter(
        self,
        api_client: TestClient,
        setup_test_proxies: None
    ) -> None:
        """Test exporting with protocol filter."""
        request_data = {
            "export_type": "proxies",
            "export_format": "json",
            "destination_type": "memory",
            "protocol": ["http"],
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 201

    def test_export_with_min_success_rate(
        self,
        api_client: TestClient,
        setup_test_proxies: None
    ) -> None:
        """Test exporting with minimum success rate filter."""
        request_data = {
            "export_type": "proxies",
            "export_format": "json",
            "destination_type": "memory",
            "min_success_rate": 0.9,
        }
        
        response = api_client.post("/api/v1/exports", json=request_data)
        
        assert response.status_code == 201
