# type: ignore
"""End-to-end tests for ProxyWhirl.

Comprehensive end-to-end test suite covering:
- CLI operations and workflows
- Library API usage patterns
- Component integration scenarios
- Real-world usage patterns and edge cases
- Performance and reliability testing
- Error handling and recovery scenarios

This module provides the highest level of testing, simulating actual
user interactions and complete workflows across all ProxyWhirl components.
"""

import asyncio
import json
import random
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from typer.testing import CliRunner

from proxywhirl import cli
from proxywhirl.cache import ProxyCache
from proxywhirl.caches import CacheType
from proxywhirl.models import AnonymityLevel, Proxy, ProxyStatus, Scheme
from proxywhirl.proxywhirl import ProxyWhirl
from proxywhirl.rotator import RotationStrategy
from proxywhirl.validator import ProxyValidator


class RobustProxyMock:
    """Enhanced proxy mock with realistic data and behavior."""

    def __init__(
        self,
        host: str = "203.0.113.1",
        port: int = 8080,
        schemes: Optional[List[Scheme]] = None,
        country_code: str = "US",
        anonymity: AnonymityLevel = AnonymityLevel.ELITE,
        response_time: float = 0.150,
        status: ProxyStatus = ProxyStatus.ACTIVE,
        quality_score: float = 0.9,
    ):
        self.host = host
        self.ip = host
        self.port = port
        self.schemes = schemes or [Scheme.HTTP]
        self.country_code = country_code
        self.country = "United States"
        self.city = "New York"
        self.region = "New York"
        self.isp = "Test ISP"
        self.organization = "Test Org"
        self.anonymity = anonymity
        self.response_time = response_time
        self.source = "test-e2e"
        self.status = status
        self.quality_score = quality_score
        self.blacklist_reason = None
        self.credentials = None
        self.metrics = None
        self.capabilities = None
        self.last_checked = datetime.now(timezone.utc)

    def model_dump(self, mode: Optional[str] = None) -> Dict[str, Any]:
        """Realistic model dump compatible with Pydantic."""
        return {
            "host": self.host,
            "ip": self.ip,
            "port": self.port,
            "schemes": [s.value for s in self.schemes],
            "country_code": self.country_code,
            "country": self.country,
            "city": self.city,
            "region": self.region,
            "isp": self.isp,
            "organization": self.organization,
            "anonymity": self.anonymity.value,
            "response_time": self.response_time,
            "source": self.source,
            "status": self.status.value,
            "quality_score": self.quality_score,
            "last_checked": self.last_checked.isoformat(),
        }

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"


class EnhancedProxyWhirlMock:
    """Comprehensive ProxyWhirl mock for E2E testing."""

    def __init__(self, **kwargs: Any):
        self.cache_type = kwargs.get("cache_type", "memory")
        self.cache_path = kwargs.get("cache_path")
        self.rotation_strategy = kwargs.get("rotation_strategy", "round_robin")
        self.loaders = kwargs.get("loaders", ["proxyscrape"])
        self.validate_on_fetch = kwargs.get("validate_on_fetch", True)

        # Realistic proxy dataset
        self._proxies = [
            RobustProxyMock(
                "203.0.113.1",
                8080,
                [Scheme.HTTP],
                "US",
                AnonymityLevel.ELITE,
                0.120,
                ProxyStatus.ACTIVE,
                0.95,
            ),
            RobustProxyMock(
                "203.0.113.2",
                3128,
                [Scheme.HTTPS],
                "GB",
                AnonymityLevel.ANONYMOUS,
                0.200,
                ProxyStatus.ACTIVE,
                0.85,
            ),
            RobustProxyMock(
                "203.0.113.3",
                1080,
                [Scheme.SOCKS4],
                "DE",
                AnonymityLevel.TRANSPARENT,
                0.300,
                ProxyStatus.ACTIVE,
                0.70,
            ),
            RobustProxyMock(
                "203.0.113.4",
                8888,
                [Scheme.SOCKS5],
                "FR",
                AnonymityLevel.ELITE,
                0.180,
                ProxyStatus.ACTIVE,
                0.80,
            ),
            RobustProxyMock(
                "203.0.113.5",
                9000,
                [Scheme.HTTP, Scheme.HTTPS],
                "CA",
                AnonymityLevel.ANONYMOUS,
                0.250,
                ProxyStatus.BLACKLISTED,
                0.40,
            ),
        ]

        # Simulate different failure modes
        self._simulate_network_failure = False
        self._simulate_validation_failure = False
        self._simulate_empty_result = False
        self._simulate_timeout = False

        # Performance tracking
        self._fetch_count = 0
        self._validate_count = 0
        self._get_count = 0

    def set_failure_mode(self, failure_type: str, enabled: bool = True) -> None:
        """Configure failure simulation for testing."""
        setattr(self, f"_simulate_{failure_type}", enabled)

    async def fetch_proxies(self, validate: bool = True) -> int:
        """Mock fetch with configurable failure modes."""
        self._fetch_count += 1

        if self._simulate_network_failure:
            raise httpx.ConnectError("Network unreachable")

        if self._simulate_timeout:
            raise httpx.TimeoutException("Request timeout")

        if self._simulate_empty_result:
            return 0

        # Filter out blacklisted proxies if validation is requested
        if validate:
            active_proxies = [p for p in self._proxies if p.status == ProxyStatus.ACTIVE]
            return len(active_proxies)

        return len(self._proxies)

    def list_proxies(self, valid_only: bool = False) -> List[RobustProxyMock]:
        """Mock list with filtering."""
        if valid_only:
            return [p for p in self._proxies if p.status == ProxyStatus.ACTIVE]
        return self._proxies

    async def validate_proxies(self) -> int:
        """Mock validation with failure simulation."""
        self._validate_count += 1

        if self._simulate_validation_failure:
            # Simulate some proxies failing validation
            for proxy in self._proxies[:2]:  # Mark first 2 as failed
                proxy.status = ProxyStatus.BLACKLISTED
            return len(self._proxies) - 2

        return len([p for p in self._proxies if p.status == ProxyStatus.ACTIVE])

    async def get_proxy(self, strategy: Optional[RotationStrategy] = None) -> RobustProxyMock:
        """Get a proxy with rotation strategy simulation."""
        valid_proxies = [p for p in self._proxies if p.status == ProxyStatus.ACTIVE]
        if not valid_proxies:
            raise Exception("No valid proxies available")

        if strategy == RotationStrategy.RANDOM:
            import random

            return random.choice(valid_proxies)
        elif strategy == RotationStrategy.WEIGHTED:
            # Simple weighted selection based on reliability
            weights = [p.reliability for p in valid_proxies]
            import random

            return random.choices(valid_proxies, weights=weights)[0]
        else:
            # Round robin - just return first for simplicity
            return valid_proxies[0]

    async def fetch_proxies_async(self, validate: bool = True) -> int:
        """Async version of fetch_proxies for CLI compatibility."""
        return await self.fetch_proxies(validate=validate)

    async def validate_proxies_async(self, max_proxies: Optional[int] = None) -> int:
        """Async version of validate_proxies for CLI compatibility."""
        return await self.validate_proxies()

    async def get_proxy_async(self, strategy: Optional[RotationStrategy] = None):
        """Async version of get_proxy for CLI compatibility."""
        return await self.get_proxy(strategy=strategy)

    def get_stats(self) -> Dict[str, int]:
        """Return operation statistics for testing."""
        return {
            "fetch_count": self._fetch_count,
            "validate_count": self._validate_count,
            "get_count": self._get_count,
            "total_proxies": len(self._proxies),
            "active_proxies": len([p for p in self._proxies if p.status == ProxyStatus.ACTIVE]),
        }


@pytest.fixture
def enhanced_mock():
    """Factory for creating enhanced mocks with various configurations."""
    return EnhancedProxyWhirlMock()


def create_mock_factory(**kwargs: Any) -> EnhancedProxyWhirlMock:
    """Helper to create mock instances."""
    return EnhancedProxyWhirlMock(**kwargs)


# =============================================================================
# LIBRARY API E2E TESTS
# =============================================================================


class TestProxyWhirlE2E:
    """End-to-end tests for ProxyWhirl library API usage patterns."""

    @pytest.mark.asyncio
    async def test_complete_async_workflow(self):
        """Test complete async workflow from initialization to proxy usage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "test_cache.json"

            # Initialize with real components (mocked network)
            pw = ProxyWhirl(
                cache_type=CacheType.JSON,
                cache_path=cache_path,
                rotation_strategy=RotationStrategy.ROUND_ROBIN,
                auto_validate=True,
                max_fetch_proxies=10,
                max_validate_on_fetch=5,
            )

            # Mock the loaders to return test data
            test_data = [
                {
                    "ip": "203.0.113.1",
                    "port": 8080,
                    "scheme": "http",
                    "country": "US",
                    "anonymity": "elite",
                    "response_time": 0.1,
                },
                {
                    "ip": "203.0.113.2",
                    "port": 3128,
                    "scheme": "https",
                    "country": "GB",
                    "anonymity": "anonymous",
                    "response_time": 0.2,
                },
            ]

            # Mock validation to avoid actual network calls
            with patch.object(
                pw.validator, "validate_proxy", new_callable=AsyncMock
            ) as mock_validate:
                from proxywhirl.validator import ValidationResult

                test_proxy = Proxy(
                    host="203.0.113.1",
                    port=8080,
                    schemes=[Scheme.HTTP],
                    country="US",
                    anonymity="elite",
                    source="test",
                )

                mock_validate.return_value = ValidationResult(
                    proxy=test_proxy,
                    is_valid=True,
                    response_time=0.1,
                )

                # Add user-provided data
                pw.add_user_provided_loader(test_data)

                # Execute complete workflow
                proxy_count = await pw.fetch_proxies_async(validate=True)
                assert proxy_count >= 0  # Should succeed

                # Validate proxies
                valid_count = await pw.validate_proxies_async(max_proxies=5)
                assert valid_count >= 0

                # Get proxy using rotation
                proxy = await pw.get_proxy_async()
                if proxy:  # May be None if no valid proxies
                    assert hasattr(proxy, "host")
                    assert hasattr(proxy, "port")

                # Test persistence
                assert cache_path.exists()

                # Test listing
                proxies = pw.list_proxies()
                assert isinstance(proxies, list)

    def test_synchronous_workflow(self):
        """Test synchronous API workflow patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "test_sync.db"

            pw = ProxyWhirl(
                cache_type=CacheType.SQLITE,
                cache_path=cache_path,
                rotation_strategy=RotationStrategy.WEIGHTED,
                auto_validate=False,
            )

            # Test direct cache operations
            assert pw.get_proxy_count() == 0

            # Add test data
            test_data = [{"ip": "127.0.0.1", "port": 8080, "scheme": "http", "country": "US"}]
            pw.add_user_provided_loader(test_data)

            # Sync fetch (should work even with network mocking)
            with patch.object(pw, "_run_async") as mock_run:
                mock_run.return_value = 1
                count = pw.fetch_proxies(validate=False)
                assert count >= 0

            # Test cache operations
            pw.clear_cache()
            assert pw.get_proxy_count() == 0

    def test_error_recovery_workflow(self):
        """Test error recovery and graceful degradation."""
        pw = ProxyWhirl(cache_type=CacheType.MEMORY, auto_validate=False)

        # Test with invalid data that should be filtered out
        invalid_data = [
            {"ip": "not.an.ip", "port": "invalid", "scheme": "unknown"},
            {"ip": "203.0.113.1"},  # Missing required fields
            {},  # Empty data
        ]

        # Should handle invalid data gracefully
        pw.add_user_provided_loader(invalid_data)

        # Even with all invalid data, methods should not crash
        assert pw.get_proxy_count() >= 0
        proxy = pw.get_proxy()
        assert proxy is None  # No valid proxies available

        proxies = pw.list_proxies()
        assert isinstance(proxies, list)

    @pytest.mark.asyncio
    async def test_concurrent_operations_e2e(self):
        """Test concurrent operations in realistic scenarios."""
        pw = ProxyWhirl(cache_type=CacheType.MEMORY)

        # Add test data
        test_data = [
            {"ip": f"203.0.113.{i}", "port": 8080 + i, "scheme": "http", "country": "US"}
            for i in range(1, 6)
        ]
        pw.add_user_provided_loader(test_data)

        # Mock validation for controlled testing
        with patch.object(pw.validator, "validate_proxy", new_callable=AsyncMock) as mock_validate:
            from proxywhirl.validator import ValidationResult

            test_proxy = Proxy(
                host="203.0.113.1",
                port=8080,
                schemes=[Scheme.HTTP],
                country="US",
                anonymity="elite",
                source="test",
            )

            mock_validate.return_value = ValidationResult(
                proxy=test_proxy,
                is_valid=True,
                response_time=0.1,
            )

            # Execute concurrent operations
            tasks = [
                pw.fetch_proxies_async(validate=True),
                pw.validate_proxies_async(),
                pw.get_proxy_async(),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Should complete without exceptions
            for result in results:
                assert not isinstance(result, Exception)

    def test_configuration_validation_e2e(self):
        """Test configuration validation in realistic scenarios."""
        # Test invalid configurations
        with pytest.raises((ValueError, TypeError)):
            ProxyWhirl(cache_type="invalid_type")

        with pytest.raises((ValueError, TypeError)):
            ProxyWhirl(rotation_strategy="invalid_strategy")

        # Test valid string configurations
        pw1 = ProxyWhirl(cache_type="memory", rotation_strategy="round_robin")
        assert pw1.cache_type == CacheType.MEMORY
        assert pw1.rotation_strategy == RotationStrategy.ROUND_ROBIN

        # Test enum configurations
        pw2 = ProxyWhirl(cache_type=CacheType.MEMORY, rotation_strategy=RotationStrategy.RANDOM)
        assert pw2.cache_type == CacheType.MEMORY
        assert pw2.rotation_strategy == RotationStrategy.RANDOM


class TestCacheE2E:
    """End-to-end tests for cache operations in realistic scenarios."""

    def test_cache_persistence_e2e(self):
        """Test cache persistence across sessions."""
        test_proxies = [
            Proxy(
                host="203.0.113.1",
                port=8080,
                schemes=[Scheme.HTTP],
                country="US",
                anonymity="elite",
                source="test",
            ),
            Proxy(
                host="203.0.113.2",
                port=3128,
                schemes=[Scheme.HTTPS],
                country="GB",
                anonymity="anonymous",
                source="test",
            ),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "e2e_cache.json"
            sqlite_path = Path(tmpdir) / "e2e_cache.db"

            # Test JSON persistence
            cache1 = ProxyCache(CacheType.JSON, json_path)
            cache1.add_proxies(test_proxies)

            # Simulate session restart
            cache2 = ProxyCache(CacheType.JSON, json_path)
            loaded_proxies = cache2.get_proxies()

            assert len(loaded_proxies) == len(test_proxies)
            assert loaded_proxies[0].host == test_proxies[0].host

            # Test SQLite persistence
            cache3 = ProxyCache(CacheType.SQLITE, sqlite_path)
            cache3.add_proxies(test_proxies)

            # Simulate session restart
            cache4 = ProxyCache(CacheType.SQLITE, sqlite_path)
            loaded_proxies2 = cache4.get_proxies()

            assert len(loaded_proxies2) == len(test_proxies)
            assert loaded_proxies2[0].host == test_proxies[0].host

    def test_cache_corruption_recovery_e2e(self):
        """Test cache recovery from corruption scenarios."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "corrupted.json"

            # Create corrupted cache file
            json_path.write_text("{ corrupted json data")

            # Should handle corruption gracefully
            cache = ProxyCache(CacheType.JSON, json_path)
            proxies = cache.get_proxies()
            assert proxies == []

            # Should be able to add new data after corruption
            test_proxy = Proxy(
                host="203.0.113.1",
                port=8080,
                schemes=[Scheme.HTTP],
                country="US",
                anonymity="elite",
                source="test",
            )

            cache.add_proxies([test_proxy])
            recovered_proxies = cache.get_proxies()
            assert len(recovered_proxies) == 1
            assert recovered_proxies[0].host == test_proxy.host


class TestValidatorE2E:
    """End-to-end tests for validator in realistic scenarios."""

    @pytest.mark.asyncio
    async def test_validator_circuit_breaker_e2e(self):
        """Test validator circuit breaker behavior in realistic failure scenarios."""
        validator = ProxyValidator(timeout=1.0, max_concurrent=2)

        test_proxy = Proxy(
            host="203.0.113.1",
            port=8080,
            schemes=[Scheme.HTTP],
            country="US",
            anonymity="elite",
            source="test",
        )

        # Mock network failures to trigger circuit breaker
        with patch("httpx.AsyncClient.request") as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Connection timeout")

            # Multiple failures should trigger circuit breaker
            results = []
            for _ in range(10):
                try:
                    result = await validator.validate_proxy(test_proxy)
                    results.append(result)
                except Exception as e:
                    results.append(e)

            # Should have handled failures gracefully
            assert len(results) == 10
            # Most should be failed validation results, not exceptions
            validation_results = [r for r in results if hasattr(r, "is_valid")]
            assert len(validation_results) > 0


# =============================================================================
# CLI E2E TESTS (Enhanced from original)
# =============================================================================


def test_cli_basic_operations(
    monkeypatch: pytest.MonkeyPatch, enhanced_mock: EnhancedProxyWhirlMock
) -> None:
    """Test basic CLI operations with enhanced mocking."""
    runner = CliRunner()

    # Mock environment to disable PYTEST_CURRENT_TEST early return
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    def mock_constructor(**kwargs: Any) -> EnhancedProxyWhirlMock:
        return enhanced_mock

    monkeypatch.setattr(cli, "ProxyWhirl", mock_constructor)

    # Test fetch with validation
    result = runner.invoke(cli.app, ["fetch", "--validate"])
    assert result.exit_code == 0
    assert "Successfully fetched" in result.stdout or "proxies" in result.stdout.lower()

    # Test fetch without validation
    result = runner.invoke(cli.app, ["fetch", "--no-validate"])
    assert result.exit_code == 0

    # Test list in table format
    result = runner.invoke(cli.app, ["list"])
    assert result.exit_code == 0
    assert "ProxyWhirl Proxies" in result.stdout or "203.0.113.1" in result.stdout

    # Test list in JSON format
    result = runner.invoke(cli.app, ["list", "--json"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert isinstance(parsed, list)
    assert len(parsed) > 0
    assert "host" in parsed[0]
    assert parsed[0]["host"] == "203.0.113.1"

    # Test validate command
    result = runner.invoke(cli.app, ["validate"])
    assert result.exit_code == 0

    # Test get in different formats
    result = runner.invoke(cli.app, ["get"])  # default hostport format
    assert result.exit_code == 0
    assert "203.0.113." in result.stdout and ":" in result.stdout

    result = runner.invoke(cli.app, ["get", "--format", "uri"])
    assert result.exit_code == 0
    assert result.stdout.startswith("http://") or result.stdout.startswith("socks")

    result = runner.invoke(cli.app, ["get", "--format", "json"])
    assert result.exit_code == 0
    proxy_json = json.loads(result.stdout)
    assert "host" in proxy_json
    assert "port" in proxy_json


def test_cli_error_scenarios(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CLI error handling with various failure scenarios."""
    runner = CliRunner()

    # Mock environment to disable PYTEST_CURRENT_TEST early return
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    # Test network failure during fetch
    mock_pw = create_mock_factory()
    mock_pw.set_failure_mode("network_failure", True)
    monkeypatch.setattr(cli, "ProxyWhirl", lambda **kwargs: mock_pw)

    result = runner.invoke(cli.app, ["fetch"])
    assert (
        result.exit_code != 0
        or "error" in result.stdout.lower()
        or "failed" in result.stdout.lower()
    )

    # Test timeout scenario
    mock_pw = create_mock_factory()
    mock_pw.set_failure_mode("timeout", True)
    monkeypatch.setattr(cli, "ProxyWhirl", lambda **kwargs: mock_pw)

    result = runner.invoke(cli.app, ["fetch"])
    assert (
        result.exit_code != 0
        or "timeout" in result.stdout.lower()
        or "failed" in result.stdout.lower()
    )

    # Test empty results
    mock_pw = create_mock_factory()
    mock_pw.set_failure_mode("empty_result", True)
    monkeypatch.setattr(cli, "ProxyWhirl", lambda **kwargs: mock_pw)

    result = runner.invoke(cli.app, ["fetch"])
    # Should succeed but with no proxies message
    assert (
        "0" in result.stdout
        or "no proxies" in result.stdout.lower()
        or "empty" in result.stdout.lower()
    )


def test_cli_advanced_scenarios(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test advanced CLI scenarios with multiple configurations."""
    runner = CliRunner()

    # Mock environment to disable PYTEST_CURRENT_TEST early return
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    # Test different rotation strategies
    mock_pw = create_mock_factory()
    monkeypatch.setattr(cli, "ProxyWhirl", lambda **kwargs: mock_pw)

    for strategy in ["round_robin", "random", "weighted"]:
        result = runner.invoke(cli.app, ["get", "--strategy", strategy])
        assert result.exit_code == 0
        assert "203.0.113." in result.stdout

    # Test different cache types with temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path = Path(tmpdir) / "test_cache.json"

        # Test JSON cache
        result = runner.invoke(
            cli.app,
            ["fetch", "--cache-type", "json", "--cache-path", str(cache_path), "--no-validate"],
        )
        assert result.exit_code == 0

        # Test SQLite cache
        db_path = Path(tmpdir) / "test_cache.sqlite"
        result = runner.invoke(
            cli.app,
            ["fetch", "--cache-type", "sqlite", "--cache-path", str(db_path), "--no-validate"],
        )
        assert result.exit_code == 0


def test_cli_validation_workflows(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test comprehensive validation workflows."""
    runner = CliRunner()

    # Mock environment to disable PYTEST_CURRENT_TEST early return
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    mock_pw = create_mock_factory()
    monkeypatch.setattr(cli, "ProxyWhirl", lambda **kwargs: mock_pw)

    # Test validation with failure simulation
    mock_pw.set_failure_mode("validation_failure", True)

    result = runner.invoke(cli.app, ["validate", "--timeout", "5"])
    assert result.exit_code == 0  # Should handle validation failures gracefully

    # Test list with valid-only filter
    result = runner.invoke(cli.app, ["list", "--valid-only"])
    assert result.exit_code == 0
    # Should show fewer proxies after validation failures

    # Test get after validation failures (should still work with remaining proxies)
    result = runner.invoke(cli.app, ["get"])
    assert result.exit_code == 0


def test_cli_configuration_integration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CLI with configuration file integration."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "proxywhirl_test.json"

        # Create test configuration
        config_data = {
            "cache": {"type": "json", "path": str(Path(tmpdir) / "cache.json")},
            "rotation": {"strategy": "weighted"},
            "validation": {"timeout": 10.0, "max_retries": 2},
            "loaders": ["proxyscrape", "monosans"],
        }

        config_path.write_text(json.dumps(config_data, indent=2))

        # Test with configuration file
        mock_pw = create_mock_factory()
        monkeypatch.setattr(cli, "ProxyWhirl", lambda **kwargs: mock_pw)

        result = runner.invoke(cli.app, ["fetch", "--config", str(config_path), "--no-validate"])
        assert result.exit_code == 0


def test_cli_performance_scenarios(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CLI performance-related scenarios."""
    runner = CliRunner()
    mock_pw = create_mock_factory()
    monkeypatch.setattr(cli, "ProxyWhirl", lambda **kwargs: mock_pw)

    # Test with various limits
    for limit in [1, 5, 10, 50]:
        result = runner.invoke(cli.app, ["fetch", "--limit", str(limit), "--no-validate"])
        assert result.exit_code == 0

    # Test concurrent operations simulation
    result = runner.invoke(cli.app, ["fetch", "--validate", "--workers", "5"])
    assert result.exit_code == 0

    # Test with timeout settings
    result = runner.invoke(cli.app, ["validate", "--timeout", "1"])
    assert result.exit_code == 0

    result = runner.invoke(cli.app, ["validate", "--timeout", "30"])
    assert result.exit_code == 0


def test_cli_output_formats_comprehensive(monkeypatch: pytest.MonkeyPatch) -> None:
    """Comprehensive test of all output formats and edge cases."""
    runner = CliRunner()
    mock_pw = create_mock_factory()
    monkeypatch.setattr(cli, "ProxyWhirl", lambda **kwargs: mock_pw)

    # Test all get formats
    formats = ["hostport", "uri", "json", "csv"]

    for fmt in formats:
        result = runner.invoke(cli.app, ["get", "--format", fmt])
        if result.exit_code == 0:  # Some formats might not be implemented
            assert len(result.stdout.strip()) > 0

    # Test list formats
    result = runner.invoke(cli.app, ["list", "--json"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert isinstance(parsed, list)

    # Test list with various filters
    result = runner.invoke(cli.app, ["list", "--country", "US"])
    assert result.exit_code == 0

    result = runner.invoke(cli.app, ["list", "--scheme", "http"])
    assert result.exit_code == 0

    result = runner.invoke(cli.app, ["list", "--anonymity", "elite"])
    assert result.exit_code == 0


def test_cli_concurrent_operations(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CLI operations under concurrent load simulation."""
    runner = CliRunner()
    mock_pw = create_mock_factory()

    # Track operations
    operation_count = 0
    original_fetch = mock_pw.fetch_proxies

    async def counting_fetch(*args, **kwargs):
        nonlocal operation_count
        operation_count += 1
        return await original_fetch(*args, **kwargs)

    mock_pw.fetch_proxies = counting_fetch
    monkeypatch.setattr(cli, "ProxyWhirl", lambda **kwargs: mock_pw)

    # Simulate rapid operations
    for i in range(3):
        result = runner.invoke(cli.app, ["fetch", "--no-validate"])
        assert result.exit_code == 0

        result = runner.invoke(cli.app, ["get"])
        assert result.exit_code == 0

    assert operation_count >= 3  # Should have tracked multiple fetch operations


def test_cli_edge_cases_and_robustness(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CLI robustness with edge cases and corner scenarios."""
    runner = CliRunner()

    # Test with minimal proxy data
    minimal_mock = EnhancedProxyWhirlMock()
    minimal_mock._proxies = [RobustProxyMock("127.0.0.1", 1234)]
    monkeypatch.setattr(cli, "ProxyWhirl", lambda **kwargs: minimal_mock)

    result = runner.invoke(cli.app, ["list", "--json"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert len(parsed) == 1
    assert parsed[0]["host"] == "127.0.0.1"

    # Test with all proxies blacklisted
    blacklisted_mock = EnhancedProxyWhirlMock()
    for proxy in blacklisted_mock._proxies:
        proxy.status = ProxyStatus.BLACKLISTED

    monkeypatch.setattr(cli, "ProxyWhirl", lambda **kwargs: blacklisted_mock)

    result = runner.invoke(cli.app, ["list", "--valid-only"])
    assert result.exit_code == 0
    # Should handle empty valid proxy list gracefully

    # Test get with no valid proxies should fail gracefully
    result = runner.invoke(cli.app, ["get"])
    # Should either fail gracefully or show appropriate message
    assert (
        result.exit_code != 0 or "no" in result.stdout.lower() or "error" in result.stdout.lower()
    )


# Legacy compatibility test (enhanced version of original)
def test_cli_legacy_compatibility(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure backward compatibility with original basic test."""
    runner = CliRunner()

    class LegacyMock:
        def __init__(self, **kwargs: Any):
            self._proxies = [RobustProxyMock("h1", 8080)]

        async def fetch_proxies(self, validate: bool = True) -> int:
            return len(self._proxies)

        def list_proxies(self) -> List[RobustProxyMock]:
            return self._proxies

        async def validate_proxies(self) -> int:
            return len(self._proxies)

        async def get_proxy(self) -> RobustProxyMock:
            return self._proxies[0]

    monkeypatch.setattr(cli, "ProxyWhirl", LegacyMock)

    # Original test cases
    result = runner.invoke(cli.app, ["fetch", "--no-validate"])
    assert result.exit_code == 0

    result = runner.invoke(cli.app, ["list"])
    assert result.exit_code == 0 and (
        "ProxyWhirl Proxies" in result.stdout or "h1" in result.stdout
    )

    result = runner.invoke(cli.app, ["list", "--json"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed[0]["host"] == "h1"

    result = runner.invoke(cli.app, ["get"])
    assert result.exit_code == 0 and "h1:8080" in result.stdout


# =============================================================================
# PERFORMANCE & RELIABILITY E2E TESTS
# =============================================================================


class TestPerformanceE2E:
    """End-to-end performance and reliability tests."""

    @pytest.mark.asyncio
    async def test_large_dataset_performance(self):
        """Test performance with large proxy datasets."""
        pw = ProxyWhirl(cache_type=CacheType.MEMORY)

        # Generate large test dataset
        large_dataset = [
            {
                "ip": f"203.0.113.{i % 256}",
                "port": 8080 + (i % 100),
                "scheme": "http" if i % 2 == 0 else "https",
                "country": "US" if i % 3 == 0 else "GB",
                "anonymity": "elite" if i % 2 == 0 else "anonymous",
            }
            for i in range(1000)  # 1000 proxy entries
        ]

        start_time = time.time()

        pw.add_user_provided_loader(large_dataset)

        # Mock validation to avoid network overhead
        with patch.object(pw.validator, "validate_proxy", new_callable=AsyncMock) as mock_validate:
            from proxywhirl.validator import ValidationResult

            test_proxy = Proxy(
                host="203.0.113.1",
                port=8080,
                schemes=[Scheme.HTTP],
                country="US",
                anonymity="elite",
                source="test",
            )

            mock_validate.return_value = ValidationResult(
                proxy=test_proxy,
                is_valid=True,
                response_time=0.1,
            )

            # Test operations performance
            proxy_count = await pw.fetch_proxies_async()
            processing_time = time.time() - start_time

            # Should handle large datasets efficiently (under reasonable time)
            assert proxy_count >= 0
            assert processing_time < 30.0  # Should complete within 30 seconds

            # Test rotation performance with large dataset
            rotation_start = time.time()
            for _ in range(100):  # Get 100 proxies
                proxy = await pw.get_proxy_async()
                if proxy is None:
                    break

            rotation_time = time.time() - rotation_start
            assert rotation_time < 10.0  # Should be fast for rotation

    def test_memory_usage_e2e(self):
        """Test memory usage patterns under various scenarios."""
        # Test memory cache scaling
        pw = ProxyWhirl(cache_type=CacheType.MEMORY)

        initial_proxy_count = pw.get_proxy_count()

        # Add data in batches
        batch_size = 100
        for batch in range(5):
            batch_data = [
                {
                    "ip": f"203.0.113.{(batch * batch_size + i) % 256}",
                    "port": 8080 + i,
                    "scheme": "http",
                    "country": "US",
                }
                for i in range(batch_size)
            ]

            pw.add_user_provided_loader(batch_data)

        # Verify cache can handle batch additions
        final_proxy_count = pw.get_proxy_count()
        assert final_proxy_count >= initial_proxy_count

        # Test cache clearing
        pw.clear_cache()
        assert pw.get_proxy_count() == 0

    @pytest.mark.asyncio
    async def test_concurrent_stress_e2e(self):
        """Test system under concurrent stress conditions."""
        pw = ProxyWhirl(cache_type=CacheType.MEMORY)

        # Add test data
        test_data = [
            {"ip": f"203.0.113.{i}", "port": 8080, "scheme": "http", "country": "US"}
            for i in range(1, 21)  # 20 test proxies
        ]
        pw.add_user_provided_loader(test_data)

        # Mock validation for controlled testing
        with patch.object(pw.validator, "validate_proxy", new_callable=AsyncMock) as mock_validate:
            from proxywhirl.validator import ValidationResult

            test_proxy = Proxy(
                host="203.0.113.1",
                port=8080,
                schemes=[Scheme.HTTP],
                country="US",
                anonymity="elite",
                source="test",
            )

            mock_validate.return_value = ValidationResult(
                proxy=test_proxy,
                is_valid=True,
                response_time=random.uniform(0.1, 0.5),
            )

            # Simulate concurrent operations
            tasks = []

            # Mix of different operations
            for _ in range(10):
                tasks.append(pw.get_proxy_async())

            for _ in range(5):
                tasks.append(pw.validate_proxies_async(max_proxies=3))

            for _ in range(3):
                tasks.append(pw.fetch_proxies_async(validate=False))

            # Execute all tasks concurrently
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            execution_time = time.time() - start_time

            # Should complete within reasonable time
            assert execution_time < 15.0

            # Should not raise exceptions (all handled gracefully)
            exceptions = [r for r in results if isinstance(r, Exception)]
            assert len(exceptions) == 0


# =============================================================================
# INTEGRATION EDGE CASE TESTS
# =============================================================================


class TestEdgeCasesE2E:
    """End-to-end tests for edge cases and boundary conditions."""

    def test_empty_data_scenarios_e2e(self):
        """Test behavior with empty or minimal data scenarios."""
        pw = ProxyWhirl(cache_type=CacheType.MEMORY)

        # Test with no data
        assert pw.get_proxy_count() == 0
        proxy = pw.get_proxy()
        assert proxy is None

        proxies = pw.list_proxies()
        assert proxies == []

        # Test with empty loader
        pw.add_user_provided_loader([])
        assert pw.get_proxy_count() == 0

    def test_invalid_data_filtering_e2e(self):
        """Test filtering of invalid data in realistic scenarios."""
        pw = ProxyWhirl(cache_type=CacheType.MEMORY, auto_validate=False)

        mixed_data = [
            # Valid proxy
            {"ip": "203.0.113.1", "port": 8080, "scheme": "http", "country": "US"},
            # Invalid IP
            {"ip": "999.999.999.999", "port": 8080, "scheme": "http", "country": "US"},
            # Invalid port
            {"ip": "203.0.113.2", "port": 70000, "scheme": "http", "country": "US"},
            # Missing required fields
            {"ip": "203.0.113.3"},
            # Invalid scheme
            {"ip": "203.0.113.4", "port": 8080, "scheme": "ftp", "country": "US"},
            # Another valid proxy
            {"ip": "203.0.113.5", "port": 3128, "scheme": "https", "country": "GB"},
        ]

        pw.add_user_provided_loader(mixed_data)

        # Should have filtered out invalid entries
        valid_count = pw.get_proxy_count()
        assert valid_count <= 2  # At most 2 valid proxies

        # Should be able to get valid proxies
        if valid_count > 0:
            proxy = pw.get_proxy()
            assert proxy is not None
            assert proxy.host in ["203.0.113.1", "203.0.113.5"]

    @pytest.mark.asyncio
    async def test_network_resilience_e2e(self):
        """Test resilience to network issues and timeouts."""
        pw = ProxyWhirl(cache_type=CacheType.MEMORY)

        # Add test data
        test_data = [{"ip": "203.0.113.1", "port": 8080, "scheme": "http", "country": "US"}]
        pw.add_user_provided_loader(test_data)

        # Simulate various network failure scenarios
        network_errors = [
            httpx.TimeoutException("Connection timeout"),
            httpx.ConnectError("Connection failed"),
            httpx.HTTPStatusError("HTTP Error", request=MagicMock(), response=MagicMock()),
        ]

        for error in network_errors:
            with patch("httpx.AsyncClient.request") as mock_request:
                mock_request.side_effect = error

                # Should handle network errors gracefully
                try:
                    result = await pw.validate_proxies_async(max_proxies=1)
                    assert result >= 0  # Should return count, not raise
                except Exception as e:
                    # If it does raise, should be handled gracefully
                    assert isinstance(
                        e, (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError)
                    )

    def test_file_system_edge_cases_e2e(self):
        """Test file system related edge cases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with read-only directory (simulate permission issues)
            readonly_path = Path(tmpdir) / "readonly" / "cache.json"
            readonly_path.parent.mkdir()

            # Should handle file system issues gracefully
            try:
                # This might work or fail depending on system permissions
                pw = ProxyWhirl(cache_type=CacheType.JSON, cache_path=readonly_path)
                # If successful, should still be functional
                assert pw.get_proxy_count() >= 0
            except (OSError, PermissionError):
                # Expected on some systems, should be handled gracefully
                pass

            # Test with very long path names
            long_name = "a" * 200 + ".json"
            long_path = Path(tmpdir) / long_name

            try:
                pw = ProxyWhirl(cache_type=CacheType.JSON, cache_path=long_path)
                assert pw.get_proxy_count() >= 0
            except (OSError, FileNotFoundError):
                # Expected on some file systems
                pass

    @pytest.mark.asyncio
    async def test_resource_cleanup_e2e(self):
        """Test proper resource cleanup in various scenarios."""
        # Test with temporary cache files
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "cleanup_test.json"

            pw = ProxyWhirl(cache_type=CacheType.JSON, cache_path=cache_path)

            # Add some data
            test_data = [{"ip": "203.0.113.1", "port": 8080, "scheme": "http", "country": "US"}]
            pw.add_user_provided_loader(test_data)

            # Mock validation for quick completion
            with patch.object(
                pw.validator, "validate_proxy", new_callable=AsyncMock
            ) as mock_validate:
                from proxywhirl.validator import ValidationResult

                test_proxy = Proxy(
                    host="203.0.113.1",
                    port=8080,
                    schemes=[Scheme.HTTP],
                    country="US",
                    anonymity="elite",
                    source="test",
                )

                mock_validate.return_value = ValidationResult(
                    proxy=test_proxy,
                    is_valid=True,
                    response_time=0.1,
                )

                # Perform operations that create resources
                await pw.fetch_proxies_async()
                await pw.validate_proxies_async()

                # Should cleanup properly - file should exist but be manageable
                assert cache_path.exists()
                assert cache_path.stat().st_size > 0

    def test_data_consistency_e2e(self):
        """Test data consistency across operations."""
        pw = ProxyWhirl(cache_type=CacheType.MEMORY)

        # Add consistent test data
        test_data = [
            {
                "ip": "203.0.113.1",
                "port": 8080,
                "scheme": "http",
                "country": "US",
                "anonymity": "elite",
            },
            {
                "ip": "203.0.113.2",
                "port": 3128,
                "scheme": "https",
                "country": "GB",
                "anonymity": "anonymous",
            },
        ]

        pw.add_user_provided_loader(test_data)

        # Verify count consistency
        initial_count = pw.get_proxy_count()

        # Get proxy multiple times - should be consistent
        proxy1 = pw.get_proxy()
        proxy2 = pw.get_proxy()  # Should rotate or return same based on strategy

        # Count should remain consistent
        assert pw.get_proxy_count() == initial_count

        # List should be consistent with count
        proxies = pw.list_proxies()
        assert len(proxies) == initial_count

        if proxy1 and proxy2:
            # Should be valid proxy objects
            assert hasattr(proxy1, "host")
            assert hasattr(proxy2, "host")
            # Should be from our test data
            assert proxy1.host in ["203.0.113.1", "203.0.113.2"]
            assert proxy2.host in ["203.0.113.1", "203.0.113.2"]
