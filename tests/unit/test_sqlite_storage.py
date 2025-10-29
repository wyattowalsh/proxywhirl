"""Tests for SQLite storage backend (T056-T075)."""

import tempfile
from pathlib import Path

import pytest

from proxywhirl.models import HealthStatus, Proxy, ProxySource


class TestSQLiteStorage:
    """Tests for SQLiteStorage backend."""

    @pytest.mark.asyncio
    async def test_sqlite_create_tables(self) -> None:
        """T058: Test that tables are created on initialization."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)

            # Initialize should create tables
            await storage.initialize()

            # Database file should exist
            assert db_path.exists()

            # Clean up
            await storage.close()

    @pytest.mark.asyncio
    async def test_sqlite_save_single_proxy(self) -> None:
        """T061: Test saving a single proxy."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            proxy = Proxy(url="http://proxy1.example.com:8080")
            await storage.save([proxy])

            # Load and verify
            loaded = await storage.load()
            assert len(loaded) == 1
            assert loaded[0].url == proxy.url

            await storage.close()

    @pytest.mark.asyncio
    async def test_sqlite_save_multiple_proxies(self) -> None:
        """T062: Test saving multiple proxies."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            proxies = [
                Proxy(url="http://proxy1.example.com:8080"),
                Proxy(url="http://proxy2.example.com:8080"),
                Proxy(url="http://proxy3.example.com:8080"),
            ]
            await storage.save(proxies)

            loaded = await storage.load()
            assert len(loaded) == 3

            await storage.close()

    @pytest.mark.asyncio
    async def test_sqlite_load_all_proxies(self) -> None:
        """T063: Test loading all proxies."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Save proxies
            proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(10)]
            await storage.save(proxies)

            # Load all
            loaded = await storage.load()
            assert len(loaded) == 10

            await storage.close()

    @pytest.mark.asyncio
    async def test_sqlite_query_by_source(self) -> None:
        """T064: Test querying proxies by source."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            proxies = [
                Proxy(url="http://proxy1.example.com:8080", source=ProxySource.USER),
                Proxy(url="http://proxy2.example.com:8080", source=ProxySource.API),
                Proxy(url="http://proxy3.example.com:8080", source=ProxySource.USER),
            ]
            await storage.save(proxies)

            # Query by source
            user_proxies = await storage.query(source="user")
            assert len(user_proxies) == 2
            assert all(p.source == ProxySource.USER for p in user_proxies)

            await storage.close()

    @pytest.mark.asyncio
    async def test_sqlite_query_by_health_status(self) -> None:
        """T065: Test querying proxies by health status."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            proxies = [
                Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY),
                Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.UNHEALTHY),
                Proxy(url="http://proxy3.example.com:8080", health_status=HealthStatus.HEALTHY),
            ]
            await storage.save(proxies)

            # Query by health status
            healthy = await storage.query(health_status="healthy")
            assert len(healthy) == 2
            assert all(p.health_status == HealthStatus.HEALTHY for p in healthy)

            await storage.close()

    @pytest.mark.asyncio
    async def test_sqlite_delete_proxy(self) -> None:
        """T066: Test deleting a proxy by URL."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            proxies = [
                Proxy(url="http://proxy1.example.com:8080"),
                Proxy(url="http://proxy2.example.com:8080"),
            ]
            await storage.save(proxies)

            # Delete one proxy
            await storage.delete("http://proxy1.example.com:8080")

            loaded = await storage.load()
            assert len(loaded) == 1
            assert loaded[0].url == "http://proxy2.example.com:8080"

            await storage.close()

    @pytest.mark.asyncio
    async def test_sqlite_update_existing_proxy(self) -> None:
        """Test updating an existing proxy (upsert)."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Save initial proxy
            proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.UNKNOWN)
            await storage.save([proxy1])

            # Update same proxy with new health status
            proxy2 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
            await storage.save([proxy2])

            # Should have only 1 proxy with updated status
            loaded = await storage.load()
            assert len(loaded) == 1
            assert loaded[0].health_status == HealthStatus.HEALTHY

            await storage.close()

    @pytest.mark.asyncio
    async def test_sqlite_concurrent_access(self) -> None:
        """T072: Test concurrent read/write operations."""
        import asyncio

        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Concurrent writes
            async def save_proxy(i: int) -> None:
                proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
                await storage.save([proxy])

            await asyncio.gather(*[save_proxy(i) for i in range(5)])

            # Verify all saved
            loaded = await storage.load()
            assert len(loaded) == 5

            await storage.close()
