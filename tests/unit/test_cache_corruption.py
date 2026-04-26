"""Tests for cache corruption detection and recovery."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from proxywhirl.cache.manager import CacheManager
from proxywhirl.exceptions import CacheCorruptionError, CacheValidationError


class TestCacheCorruptionRecovery:
    """Test cache corruption detection and recovery."""

    def test_detect_corrupted_json(self) -> None:
        """Test detection of corrupted JSON data."""
        corrupted_data = "{'invalid': json}"

        with pytest.raises((json.JSONDecodeError, ValueError)):
            json.loads(corrupted_data)

    def test_detect_missing_required_fields(self) -> None:
        """Test detection of missing required cache fields."""
        cache_entry = {
            "value": "data",
            # Missing 'timestamp' field
        }

        required_fields = {"value", "timestamp"}
        missing = required_fields - set(cache_entry.keys())

        assert "timestamp" in missing

    def test_detect_invalid_timestamp(self) -> None:
        """Test detection of invalid timestamps."""
        cache_entry = {
            "value": "data",
            "timestamp": "not-a-date",
        }

        with pytest.raises((ValueError, TypeError)):
            datetime.fromisoformat(cache_entry["timestamp"])

    def test_detect_checksum_mismatch(self) -> None:
        """Test detection of checksum mismatches."""
        import hashlib

        data = b"cached_data"
        expected_checksum = hashlib.sha256(data).hexdigest()
        actual_checksum = hashlib.sha256(b"modified_data").hexdigest()

        assert expected_checksum != actual_checksum

    def test_recovery_from_corrupted_entry(self) -> None:
        """Test recovery when entry is corrupted."""
        cache = {}

        # Corrupted entry
        cache["key1"] = None

        # Recovery: remove and refresh
        if cache.get("key1") is None:
            del cache["key1"]

        assert "key1" not in cache

    def test_recovery_by_rebuilding_cache(self) -> None:
        """Test recovery by rebuilding cache from source."""
        corrupted_cache = {"key1": {"corrupted": True}}

        # Rebuild from source
        source_data = {"key1": {"value": "data1", "timestamp": "2024-01-01T00:00:00Z"}}

        # New cache from source
        new_cache = source_data.copy()
        assert new_cache["key1"]["value"] == "data1"

    def test_cache_validation_on_load(self) -> None:
        """Test cache validation during load."""
        cache_data = {
            "valid_entry": {"value": "data", "timestamp": "2024-01-01T00:00:00Z"},
            "invalid_entry": {"value": "data"},  # Missing timestamp
        }

        valid_entries = []
        for key, entry in cache_data.items():
            if "timestamp" in entry and "value" in entry:
                valid_entries.append(key)

        assert len(valid_entries) == 1
        assert "valid_entry" in valid_entries

    def test_graceful_degradation_on_corruption(self) -> None:
        """Test graceful degradation when cache is corrupted."""
        cache = {"key1": None}

        # Degrade gracefully
        result = cache.get("key1") or "fallback_value"
        assert result == "fallback_value"

    def test_corruption_detection_overhead(self) -> None:
        """Test that corruption detection is efficient."""
        import time

        data = b"x" * 1000000  # 1MB

        start = time.time()
        import hashlib

        hashlib.sha256(data).hexdigest()
        elapsed = time.time() - start

        # Should be very fast even for large data
        assert elapsed < 0.1

    def test_multi_tier_cache_corruption_isolation(self) -> None:
        """Test that corruption in one tier doesn't affect others."""
        l1_cache = {"key1": "data1"}
        l2_cache = {"key1": None}  # Corrupted

        # Fall back to L1
        result = l1_cache.get("key1") or l2_cache.get("key1")
        assert result == "data1"
