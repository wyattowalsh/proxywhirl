"""Integration tests for storage backends (SQLite in-memory and file-based)."""

import pytest
import sqlite3
from datetime import datetime
from pathlib import Path

from proxywhirl.models import Proxy
from proxywhirl.storage import SQLiteStorage


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary SQLite database."""
    db_path = tmp_path / "test_proxies.db"
    return str(db_path)


class TestSQLiteStorageBasic:
    """Test basic SQLite storage operations."""

    def test_storage_create_and_store_proxy(self, temp_db):
        """Test creating storage and storing a proxy."""
        storage = SQLiteStorage(filepath=temp_db)
        
        proxy = Proxy(url="http://proxy1.example.com:8080")
        storage.add_proxy(proxy)
        
        # Verify stored
        proxies = storage.get_all_proxies()
        assert len(proxies) > 0

    def test_storage_retrieve_proxy(self, temp_db):
        """Test retrieving a stored proxy."""
        storage = SQLiteStorage(filepath=temp_db)
        
        proxy = Proxy(url="http://proxy2.example.com:8080")
        storage.add_proxy(proxy)
        
        # Retrieve
        retrieved = storage.get(str(proxy.id))
        assert retrieved is not None
        assert retrieved.url == proxy.url

    def test_storage_update_proxy(self, temp_db):
        """Test updating a stored proxy."""
        storage = SQLiteStorage(filepath=temp_db)
        
        proxy = Proxy(url="http://proxy3.example.com:8080")
        storage.add_proxy(proxy)
        
        # Update
        proxy.consecutive_failures = 5
        storage.add_proxy(proxy)
        
        retrieved = storage.get(str(proxy.id))
        assert retrieved.consecutive_failures == 5

    def test_storage_delete_proxy(self, temp_db):
        """Test deleting a stored proxy."""
        storage = SQLiteStorage(filepath=temp_db)
        
        proxy = Proxy(url="http://proxy4.example.com:8080")
        storage.add_proxy(proxy)
        
        # Delete
        storage.remove(str(proxy.id))
        
        # Verify deleted
        retrieved = storage.get(str(proxy.id))
        assert retrieved is None

    def test_storage_list_all_proxies(self, temp_db):
        """Test listing all stored proxies."""
        storage = SQLiteStorage(filepath=temp_db)
        
        # Add multiple proxies
        for i in range(5):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            storage.add_proxy(proxy)
        
        # List all
        proxies = storage.get_all_proxies()
        assert len(proxies) >= 5


class TestSQLiteStorageBulkOperations:
    """Test bulk storage operations."""

    def test_save_multiple_proxies(self, temp_db):
        """Test saving multiple proxies efficiently."""
        storage = SQLiteStorage(filepath=temp_db)
        
        proxies = [
            Proxy(url=f"http://bulk-proxy{i}.example.com:8080")
            for i in range(20)
        ]
        
        for proxy in proxies:
            storage.add_proxy(proxy)
        
        stored = storage.get_all_proxies()
        assert len(stored) >= 20

    def test_storage_consistency_across_operations(self, temp_db):
        """Test storage consistency after multiple ops."""
        storage = SQLiteStorage(filepath=temp_db)
        
        # Add
        p1 = Proxy(url="http://consistency1.example.com:8080")
        storage.add_proxy(p1)
        
        # Update
        p1.consecutive_failures = 3
        storage.add_proxy(p1)
        
        # Retrieve
        retrieved = storage.get(str(p1.id))
        
        # Verify
        assert retrieved.consecutive_failures == 3
        assert retrieved.url == p1.url


class TestSQLiteStorageMetadataPreservation:
    """Test that all proxy metadata is preserved."""

    def test_health_status_preserved(self, temp_db):
        """Test health status is preserved."""
        from proxywhirl.models import HealthStatus
        
        storage = SQLiteStorage(filepath=temp_db)
        
        proxy = Proxy(
            url="http://health-proxy.example.com:8080",
            health_status=HealthStatus.DEGRADED
        )
        storage.add_proxy(proxy)
        
        retrieved = storage.get(str(proxy.id))
        assert retrieved.health_status == HealthStatus.DEGRADED

    def test_tags_preserved(self, temp_db):
        """Test tags are preserved."""
        storage = SQLiteStorage(filepath=temp_db)
        
        proxy = Proxy(
            url="http://tags-proxy.example.com:8080",
            tags={"fast", "reliable", "stable"}
        )
        storage.add_proxy(proxy)
        
        retrieved = storage.get(str(proxy.id))
        assert "fast" in retrieved.tags
        assert "reliable" in retrieved.tags

    def test_metadata_preserved(self, temp_db):
        """Test custom metadata is preserved."""
        storage = SQLiteStorage(filepath=temp_db)
        
        meta = {"tier": "premium", "region": "EU", "api_version": 2}
        proxy = Proxy(
            url="http://metadata-proxy.example.com:8080",
            metadata=meta
        )
        storage.add_proxy(proxy)
        
        retrieved = storage.get(str(proxy.id))
        assert retrieved.metadata["tier"] == "premium"
        assert retrieved.metadata["region"] == "EU"

    def test_request_stats_preserved(self, temp_db):
        """Test request statistics are preserved."""
        storage = SQLiteStorage(filepath=temp_db)
        
        proxy = Proxy(
            url="http://stats-proxy.example.com:8080",
            total_successes=50,
            total_failures=5,
            requests_completed=55,
            total_requests=100
        )
        storage.add_proxy(proxy)
        
        retrieved = storage.get(str(proxy.id))
        assert retrieved.total_successes == 50
        assert retrieved.total_failures == 5


class TestSQLiteStorageCredentialHandling:
    """Test credential storage security."""

    def test_credentials_stored_and_retrieved(self, temp_db):
        """Test credentials are properly stored."""
        storage = SQLiteStorage(filepath=temp_db)
        
        proxy = Proxy(
            url="http://creds-proxy.example.com:8080",
            username="testuser",
            password="testpass"
        )
        storage.add_proxy(proxy)
        
        retrieved = storage.get(str(proxy.id))
        assert retrieved.username is not None
        assert retrieved.password is not None
