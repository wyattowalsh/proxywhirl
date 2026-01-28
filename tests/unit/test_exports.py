"""Unit tests for exports module.

Tests cover parse_proxy_url, generate_rich_proxies, generate_stats_from_files,
and export_for_web functionality.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from proxywhirl.exports import (
    export_for_web,
    generate_rich_proxies,
    generate_stats_from_files,
    parse_proxy_url,
)


class TestParseProxyUrl:
    """Test parse_proxy_url function."""

    def test_http_url_with_port(self) -> None:
        """Test parsing HTTP URL with port."""
        ip, port = parse_proxy_url("http://192.168.1.1:8080")
        assert ip == "192.168.1.1"
        assert port == 8080

    def test_https_url_with_port(self) -> None:
        """Test parsing HTTPS URL with port."""
        ip, port = parse_proxy_url("https://10.0.0.1:443")
        assert ip == "10.0.0.1"
        assert port == 443

    def test_socks5_url_with_port(self) -> None:
        """Test parsing SOCKS5 URL with port."""
        ip, port = parse_proxy_url("socks5://proxy.example.com:1080")
        assert ip == "proxy.example.com"
        assert port == 1080

    def test_url_without_port_defaults_to_80(self) -> None:
        """Test that URL without port defaults to 80."""
        ip, port = parse_proxy_url("http://192.168.1.1")
        assert ip == "192.168.1.1"
        assert port == 80

    def test_url_without_hostname(self) -> None:
        """Test URL without hostname returns empty string."""
        ip, port = parse_proxy_url("http://:8080")
        assert ip == ""
        assert port == 8080


class TestGenerateRichProxies:
    """Test generate_rich_proxies function."""

    async def test_empty_storage(self) -> None:
        """Test with empty storage returns empty proxies list."""
        mock_storage = AsyncMock()
        mock_storage.load.return_value = []

        result = await generate_rich_proxies(mock_storage, max_age_hours=0)

        assert result["total"] == 0
        assert result["proxies"] == []
        assert result["aggregations"]["by_protocol"] == {}
        assert result["aggregations"]["by_status"] == {}
        assert result["aggregations"]["by_source"] == {}
        assert "generated_at" in result

    async def test_single_proxy(self) -> None:
        """Test with single proxy returns correct data."""
        # With normalized schema, load() returns dicts
        mock_proxy = {
            "url": "http://192.168.1.1:8080",
            "protocol": "http",
            "health_status": "healthy",
            "avg_response_time_ms": 150.5,
            "total_successes": 9,
            "total_checks": 10,
            "source": "free-proxy-list",
            "last_success_at": datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            "last_failure_at": None,
            "discovered_at": datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            "country_code": None,
        }

        mock_storage = AsyncMock()
        mock_storage.load.return_value = [mock_proxy]

        result = await generate_rich_proxies(mock_storage, max_age_hours=0)

        assert result["total"] == 1
        assert len(result["proxies"]) == 1
        proxy = result["proxies"][0]
        assert proxy["ip"] == "192.168.1.1"
        assert proxy["port"] == 8080
        assert proxy["protocol"] == "http"
        assert proxy["status"] == "healthy"
        assert proxy["response_time"] == 150.5
        assert proxy["success_rate"] == 90.0
        assert proxy["total_checks"] == 10
        assert proxy["source"] == "free-proxy-list"
        assert result["aggregations"]["by_protocol"]["http"] == 1
        assert result["aggregations"]["by_status"]["healthy"] == 1

    async def test_proxy_with_zero_requests(self) -> None:
        """Test proxy with zero requests has None success_rate."""
        mock_proxy = {
            "url": "http://192.168.1.1:8080",
            "protocol": "http",
            "health_status": "unknown",
            "avg_response_time_ms": None,
            "total_successes": 0,
            "total_checks": 0,
            "source": "geonode",
            "last_success_at": None,
            "last_failure_at": None,
            "discovered_at": None,
            "country_code": None,
        }

        mock_storage = AsyncMock()
        mock_storage.load.return_value = [mock_proxy]

        result = await generate_rich_proxies(mock_storage, max_age_hours=0)

        assert result["proxies"][0]["success_rate"] is None
        assert result["proxies"][0]["last_checked"] is None
        assert result["proxies"][0]["created_at"] is None

    async def test_proxy_with_only_failures(self) -> None:
        """Test proxy with only failure timestamp uses it for last_checked."""
        mock_proxy = {
            "url": "http://192.168.1.1:8080",
            "protocol": "http",
            "health_status": "unhealthy",
            "avg_response_time_ms": None,
            "total_successes": 0,
            "total_checks": 5,
            "source": "proxyscrape",
            "last_success_at": None,
            "last_failure_at": datetime(2025, 1, 2, 12, 0, 0, tzinfo=timezone.utc),
            "discovered_at": datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            "country_code": None,
        }

        mock_storage = AsyncMock()
        mock_storage.load.return_value = [mock_proxy]

        result = await generate_rich_proxies(mock_storage, max_age_hours=0)

        assert result["proxies"][0]["last_checked"] == "2025-01-02T12:00:00+00:00"
        assert result["proxies"][0]["success_rate"] == 0.0

    async def test_multiple_proxies_aggregation(self) -> None:
        """Test aggregation counts with multiple proxies."""
        proxies = []
        for i in range(3):
            mock_proxy = {
                "url": f"http://192.168.1.{i}:8080",
                "protocol": "http",
                "health_status": "healthy",
                "avg_response_time_ms": 100,
                "total_successes": 10,
                "total_checks": 10,
                "source": "free-proxy-list",
                "last_success_at": datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                "last_failure_at": None,
                "discovered_at": datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "country_code": None,
            }
            proxies.append(mock_proxy)

        # Add SOCKS5 proxy
        socks_proxy = {
            "url": "socks5://192.168.1.100:1080",
            "protocol": "socks5",
            "health_status": "degraded",
            "avg_response_time_ms": 200,
            "total_successes": 5,
            "total_checks": 10,
            "source": "spys-one",
            "last_success_at": datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            "last_failure_at": None,
            "discovered_at": datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            "country_code": None,
        }
        proxies.append(socks_proxy)

        mock_storage = AsyncMock()
        mock_storage.load.return_value = proxies

        result = await generate_rich_proxies(mock_storage, max_age_hours=0)

        assert result["total"] == 4
        assert result["aggregations"]["by_protocol"]["http"] == 3
        assert result["aggregations"]["by_protocol"]["socks5"] == 1
        assert result["aggregations"]["by_status"]["healthy"] == 3
        assert result["aggregations"]["by_status"]["degraded"] == 1
        assert result["aggregations"]["by_source"]["free-proxy-list"] == 3
        assert result["aggregations"]["by_source"]["spys-one"] == 1


class TestGenerateStatsFromFiles:
    """Test generate_stats_from_files function."""

    def test_with_metadata_and_protocol_files(self, tmp_path: Path) -> None:
        """Test generating stats with metadata and protocol files."""
        # Create metadata
        metadata = {
            "generated_at": "2025-01-01T00:00:00+00:00",
            "total_sources": 5,
            "counts": {"http": 100, "https": 50, "socks4": 25, "socks5": 25},
        }
        (tmp_path / "metadata.json").write_text(json.dumps(metadata))

        # Create protocol files
        (tmp_path / "http.txt").write_text("192.168.1.1:8080\n192.168.1.2:8080\n")
        (tmp_path / "https.txt").write_text("192.168.1.3:443\n")
        (tmp_path / "socks4.txt").write_text("192.168.1.4:1080\n192.168.1.5:1080\n")
        (tmp_path / "socks5.txt").write_text("")  # Empty file

        result = generate_stats_from_files(tmp_path)

        assert result["generated_at"] == "2025-01-01T00:00:00+00:00"
        assert result["sources"]["total"] == 5
        assert result["proxies"]["by_protocol"]["http"] == 2
        assert result["proxies"]["by_protocol"]["https"] == 1
        assert result["proxies"]["by_protocol"]["socks4"] == 2
        assert result["proxies"]["by_protocol"]["socks5"] == 0
        # Total uses unique count (http + socks4 + socks5, not https to avoid duplicates)
        assert result["proxies"]["total"] == 4

    def test_without_metadata_file(self, tmp_path: Path) -> None:
        """Test generating stats without metadata.json uses defaults."""
        (tmp_path / "http.txt").write_text("192.168.1.1:8080\n")

        result = generate_stats_from_files(tmp_path)

        assert "generated_at" in result
        assert result["sources"]["total"] == 0
        assert result["proxies"]["by_protocol"]["http"] == 1

    def test_calculates_file_sizes(self, tmp_path: Path) -> None:
        """Test that file sizes are calculated correctly."""
        content = "192.168.1.1:8080\n192.168.1.2:8080\n"
        (tmp_path / "http.txt").write_text(content)
        (tmp_path / "all.txt").write_text(content * 2)
        (tmp_path / "proxies.json").write_text('{"proxies":[]}')
        (tmp_path / "metadata.json").write_text("{}")

        result = generate_stats_from_files(tmp_path)

        assert "http.txt" in result["file_sizes"]
        assert "all.txt" in result["file_sizes"]
        assert "proxies.json" in result["file_sizes"]
        assert result["file_sizes"]["http.txt"] > 0

    def test_falls_back_to_metadata_counts(self, tmp_path: Path) -> None:
        """Test that missing protocol files fall back to metadata counts."""
        metadata = {
            "generated_at": "2025-01-01T00:00:00+00:00",
            "total_sources": 2,
            "counts": {"http": 100, "https": 50, "socks4": 0, "socks5": 0},
        }
        (tmp_path / "metadata.json").write_text(json.dumps(metadata))
        # Don't create protocol files

        result = generate_stats_from_files(tmp_path)

        assert result["proxies"]["by_protocol"]["http"] == 100
        assert result["proxies"]["by_protocol"]["https"] == 50

    def test_unique_proxy_count(self, tmp_path: Path) -> None:
        """Test that unique proxies are counted correctly."""
        (tmp_path / "metadata.json").write_text("{}")
        # Same proxy in different files
        (tmp_path / "http.txt").write_text("192.168.1.1:8080\n192.168.1.2:8080\n")
        (tmp_path / "socks4.txt").write_text("192.168.1.1:8080\n")  # Duplicate
        (tmp_path / "socks5.txt").write_text("192.168.1.3:1080\n")

        result = generate_stats_from_files(tmp_path)

        # Unique proxies: 192.168.1.1:8080, 192.168.1.2:8080, 192.168.1.3:1080 = 3
        # (socks4 has duplicate of http proxy)
        assert result["proxies"]["total"] == 3
        assert result["proxies"]["unique"] == 3

    def test_handles_empty_lines_in_files(self, tmp_path: Path) -> None:
        """Test that empty lines are skipped when counting."""
        (tmp_path / "metadata.json").write_text("{}")
        (tmp_path / "http.txt").write_text("192.168.1.1:8080\n\n\n192.168.1.2:8080\n\n")

        result = generate_stats_from_files(tmp_path)

        assert result["proxies"]["by_protocol"]["http"] == 2


class TestExportForWeb:
    """Test export_for_web function."""

    async def test_creates_output_directory(self, tmp_path: Path) -> None:
        """Test that output directory is created if it doesn't exist."""
        db_path = tmp_path / "nonexistent.db"
        output_dir = tmp_path / "output" / "nested"

        outputs = await export_for_web(
            db_path, output_dir, include_stats=True, include_rich_proxies=False
        )

        assert output_dir.exists()
        assert "stats" in outputs

    async def test_generates_stats_json(self, tmp_path: Path) -> None:
        """Test that stats.json is generated correctly."""
        db_path = tmp_path / "db.sqlite"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        (output_dir / "http.txt").write_text("192.168.1.1:8080\n")
        (output_dir / "metadata.json").write_text('{"total_sources":1}')

        outputs = await export_for_web(
            db_path, output_dir, include_stats=True, include_rich_proxies=False
        )

        assert "stats" in outputs
        stats_path = outputs["stats"]
        assert stats_path.exists()
        stats = json.loads(stats_path.read_text())
        assert stats["sources"]["total"] == 1

    async def test_generates_rich_proxies_json(self, tmp_path: Path) -> None:
        """Test that proxies-rich.json is generated when db exists."""
        db_path = tmp_path / "db.sqlite"
        db_path.touch()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "metadata.json").write_text("{}")

        mock_storage = AsyncMock()
        mock_storage.load.return_value = []

        with patch("proxywhirl.exports.SQLiteStorage", return_value=mock_storage):
            outputs = await export_for_web(
                db_path, output_dir, include_stats=False, include_rich_proxies=True
            )

        assert "proxies_rich" in outputs
        assert outputs["proxies_rich"].exists()
        mock_storage.initialize.assert_called_once()
        mock_storage.close.assert_called_once()

    async def test_skips_rich_proxies_when_db_missing(self, tmp_path: Path) -> None:
        """Test that rich proxies are skipped when database doesn't exist."""
        db_path = tmp_path / "nonexistent.db"
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "metadata.json").write_text("{}")

        outputs = await export_for_web(
            db_path, output_dir, include_stats=False, include_rich_proxies=True
        )

        assert "proxies_rich" not in outputs

    async def test_excludes_stats_when_disabled(self, tmp_path: Path) -> None:
        """Test that stats are not generated when include_stats=False."""
        db_path = tmp_path / "db.sqlite"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        outputs = await export_for_web(
            db_path, output_dir, include_stats=False, include_rich_proxies=False
        )

        assert "stats" not in outputs
        assert not (output_dir / "stats.json").exists()

    async def test_storage_closed_on_error(self, tmp_path: Path) -> None:
        """Test that storage is closed even when an error occurs."""
        db_path = tmp_path / "db.sqlite"
        db_path.touch()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "metadata.json").write_text("{}")

        mock_storage = AsyncMock()
        mock_storage.load_validated.side_effect = RuntimeError("Test error")

        with patch("proxywhirl.exports.SQLiteStorage", return_value=mock_storage):
            with pytest.raises(RuntimeError, match="Test error"):
                await export_for_web(
                    db_path, output_dir, include_stats=False, include_rich_proxies=True
                )

        mock_storage.close.assert_called_once()
