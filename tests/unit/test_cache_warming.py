"""Unit tests for cache warming functionality.

Tests cover:
- T078-T082: Cache warming from various file formats (JSON, JSONL, CSV)
- Error handling and metadata validation
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import SecretStr

from proxywhirl.cache import CacheManager
from proxywhirl.cache_crypto import CredentialEncryptor
from proxywhirl.cache_models import CacheConfig


@pytest.fixture
def cache_config(tmp_path: Path) -> CacheConfig:
    """Fixture for cache configuration."""
    encryptor = CredentialEncryptor()
    return CacheConfig(
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=SecretStr(encryptor.key.decode("utf-8")),
    )


@pytest.fixture
def cache_manager(cache_config: CacheConfig) -> CacheManager:
    """Fixture for cache manager."""
    return CacheManager(cache_config)


class TestCacheWarming:
    """Test cache warming from JSON file format.

    T078: Unit test for warm_from_file with JSON format.
    """

    def test_warm_from_json_file(self, cache_manager: CacheManager, tmp_path: Path) -> None:
        """Test warming cache from JSON file."""
        # Create JSON file with proxy data
        json_file = tmp_path / "proxies.json"
        proxies = [
            {
                "proxy_url": "http://proxy1.example.com:8080",
                "username": "user1",
                "password": "pass1",
                "source": "json_import",
            },
            {
                "proxy_url": "http://proxy2.example.com:8080",
                "username": None,
                "password": None,
                "source": "json_import",
            },
        ]
        json_file.write_text(json.dumps(proxies))

        # Warm cache
        count = cache_manager.warm_from_file(str(json_file))

        # Verify loaded
        assert count == 2, "Should load 2 proxies"
        assert cache_manager.l1_tier.size() == 2, "L1 should have 2 entries"

    def test_warm_from_json_with_credentials(
        self, cache_manager: CacheManager, tmp_path: Path
    ) -> None:
        """Test that credentials are properly encrypted during warming."""
        json_file = tmp_path / "proxies.json"
        proxies = [
            {
                "proxy_url": "http://secure-proxy.example.com:8080",
                "username": "secret_user",
                "password": "secret_pass",
                "source": "json_import",
            }
        ]
        json_file.write_text(json.dumps(proxies))

        cache_manager.warm_from_file(str(json_file))

        # Retrieve and verify credentials are protected
        key = CacheManager.generate_cache_key("http://secure-proxy.example.com:8080")
        entry = cache_manager.get(key)
        assert entry is not None
        assert entry.username is not None
        assert entry.username.get_secret_value() == "secret_user"
        assert entry.password is not None
        assert entry.password.get_secret_value() == "secret_pass"


class TestCacheWarmingJSONL:
    """Test cache warming from JSONL file format.

    T079: Unit test for warm_from_file with JSONL format.
    """

    def test_warm_from_jsonl_file(self, cache_manager: CacheManager, tmp_path: Path) -> None:
        """Test warming cache from JSONL (newline-delimited JSON) file."""
        jsonl_file = tmp_path / "proxies.jsonl"
        lines = [
            json.dumps(
                {
                    "proxy_url": "http://proxy1.example.com:8080",
                    "source": "jsonl_import",
                }
            ),
            json.dumps(
                {
                    "proxy_url": "http://proxy2.example.com:8080",
                    "source": "jsonl_import",
                }
            ),
            json.dumps(
                {
                    "proxy_url": "http://proxy3.example.com:8080",
                    "source": "jsonl_import",
                }
            ),
        ]
        jsonl_file.write_text("\n".join(lines))

        count = cache_manager.warm_from_file(str(jsonl_file))

        assert count == 3, "Should load 3 proxies"
        assert cache_manager.l1_tier.size() == 3, "L1 should have 3 entries"


class TestCacheWarmingCSV:
    """Test cache warming from CSV file format.

    T080: Unit test for warm_from_file with CSV format.
    """

    def test_warm_from_csv_file(self, cache_manager: CacheManager, tmp_path: Path) -> None:
        """Test warming cache from CSV file."""
        csv_file = tmp_path / "proxies.csv"
        csv_content = """proxy_url,username,password,source
http://proxy1.example.com:8080,user1,pass1,csv_import
http://proxy2.example.com:8080,,,csv_import
http://proxy3.example.com:8080,user3,pass3,csv_import
"""
        csv_file.write_text(csv_content)

        count = cache_manager.warm_from_file(str(csv_file))

        assert count == 3, "Should load 3 proxies"
        assert cache_manager.l1_tier.size() == 3, "L1 should have 3 entries"

    def test_warm_from_csv_with_header(self, cache_manager: CacheManager, tmp_path: Path) -> None:
        """Test CSV warming skips header row."""
        csv_file = tmp_path / "proxies.csv"
        csv_content = """proxy_url,username,password,source
http://proxy1.example.com:8080,user1,pass1,csv_import
"""
        csv_file.write_text(csv_content)

        count = cache_manager.warm_from_file(str(csv_file))

        assert count == 1, "Should load 1 proxy (not header)"
        # Verify header not loaded as proxy
        entry = cache_manager.get("proxy_url")
        assert entry is None, "Header should not be loaded as entry"


class TestCacheWarmingErrors:
    """Test error handling during cache warming.

    T081: Unit test for warm_from_file with invalid entries skipped.
    """

    def test_warm_skips_invalid_entries(self, cache_manager: CacheManager, tmp_path: Path) -> None:
        """Test that invalid entries are skipped and logged."""
        json_file = tmp_path / "mixed_proxies.json"
        proxies = [
            {
                "proxy_url": "http://valid1.example.com:8080",
                "source": "test",
            },
            {
                "invalid_field": "no_proxy_url",  # Invalid: missing proxy_url
            },
            {
                "proxy_url": "http://valid2.example.com:8080",
                "source": "test",
            },
        ]
        json_file.write_text(json.dumps(proxies))

        count = cache_manager.warm_from_file(str(json_file))

        # Should load only valid entries
        assert count == 2, "Should load 2 valid proxies, skip 1 invalid"
        assert cache_manager.l1_tier.size() == 2

    def test_warm_handles_malformed_json(self, cache_manager: CacheManager, tmp_path: Path) -> None:
        """Test that malformed JSON is handled gracefully."""
        json_file = tmp_path / "bad.json"
        json_file.write_text("{invalid json")

        count = cache_manager.warm_from_file(str(json_file))

        assert count == 0, "Should load 0 proxies from malformed JSON"
        assert cache_manager.l1_tier.size() == 0

    def test_warm_handles_missing_file(self, cache_manager: CacheManager, tmp_path: Path) -> None:
        """Test that missing file is handled gracefully."""
        missing_file = tmp_path / "nonexistent.json"

        count = cache_manager.warm_from_file(str(missing_file))

        assert count == 0, "Should return 0 for missing file"


class TestCacheWarmingMetadata:
    """Test cache warming sets TTL and metadata correctly.

    T082: Unit test for warm_from_file TTL and metadata handling.
    """

    def test_warm_uses_default_ttl(self, cache_manager: CacheManager, tmp_path: Path) -> None:
        """Test that warmed entries use default TTL."""
        json_file = tmp_path / "proxies.json"
        proxies = [{"proxy_url": "http://proxy1.example.com:8080", "source": "test"}]
        json_file.write_text(json.dumps(proxies))

        cache_manager.warm_from_file(str(json_file))

        key = CacheManager.generate_cache_key("http://proxy1.example.com:8080")
        entry = cache_manager.get(key)
        assert entry is not None
        assert entry.ttl_seconds == cache_manager.config.default_ttl_seconds

    def test_warm_with_custom_ttl(self, cache_manager: CacheManager, tmp_path: Path) -> None:
        """Test warming with custom TTL override."""
        json_file = tmp_path / "proxies.json"
        proxies = [{"proxy_url": "http://proxy1.example.com:8080", "source": "test"}]
        json_file.write_text(json.dumps(proxies))

        custom_ttl = 7200
        cache_manager.warm_from_file(str(json_file), ttl_override=custom_ttl)

        key = CacheManager.generate_cache_key("http://proxy1.example.com:8080")
        entry = cache_manager.get(key)
        assert entry is not None
        assert entry.ttl_seconds == custom_ttl

    def test_warm_sets_fetch_time(self, cache_manager: CacheManager, tmp_path: Path) -> None:
        """Test that warmed entries have fetch_time set."""
        json_file = tmp_path / "proxies.json"
        proxies = [{"proxy_url": "http://proxy1.example.com:8080", "source": "test"}]
        json_file.write_text(json.dumps(proxies))

        before = datetime.now(timezone.utc)
        cache_manager.warm_from_file(str(json_file))
        after = datetime.now(timezone.utc)

        key = CacheManager.generate_cache_key("http://proxy1.example.com:8080")
        entry = cache_manager.get(key)
        assert entry is not None
        assert before <= entry.fetch_time <= after

    def test_warm_sets_expires_at(self, cache_manager: CacheManager, tmp_path: Path) -> None:
        """Test that warmed entries have expires_at calculated."""
        json_file = tmp_path / "proxies.json"
        proxies = [{"proxy_url": "http://proxy1.example.com:8080", "source": "test"}]
        json_file.write_text(json.dumps(proxies))

        cache_manager.warm_from_file(str(json_file))

        key = CacheManager.generate_cache_key("http://proxy1.example.com:8080")
        entry = cache_manager.get(key)
        assert entry is not None
        assert entry.expires_at > datetime.now(timezone.utc)
        # Should expire roughly default_ttl_seconds in the future
        expected_expiry = datetime.now(timezone.utc) + timedelta(
            seconds=cache_manager.config.default_ttl_seconds
        )
        # Allow 10 second tolerance
        assert abs((entry.expires_at - expected_expiry).total_seconds()) < 10
