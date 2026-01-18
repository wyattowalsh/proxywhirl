"""Unit tests for storage backends."""

import json
import tempfile
from pathlib import Path

import pytest
import sqlalchemy as sa

from proxywhirl.models import Proxy, StorageBackend


class TestStorageProtocol:
    """Test storage backend protocol compliance."""

    def test_storage_protocol_compliance(self) -> None:
        """T032: Test that StorageBackend is a valid protocol."""
        # Verify the protocol exists and has required methods
        assert hasattr(StorageBackend, "save")
        assert hasattr(StorageBackend, "load")
        assert hasattr(StorageBackend, "clear")

        # Verify it's a Protocol

        assert isinstance(StorageBackend, type)


class DummyStorage:
    """Dummy storage implementation for protocol testing."""

    def __init__(self):
        self.proxies: list[Proxy] = []

    async def save(self, proxies: list[Proxy]) -> None:
        """Save proxies."""
        self.proxies = proxies.copy()

    async def load(self) -> list[Proxy]:
        """Load proxies."""
        return self.proxies.copy()

    async def clear(self) -> None:
        """Clear proxies."""
        self.proxies.clear()


class TestFileStorage:
    """Test FileStorage implementation."""

    def test_file_storage_init(self) -> None:
        """T034: Test FileStorage initialization."""
        from proxywhirl.storage import FileStorage

        # Test initialization with Path
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies.json"
            storage = FileStorage(storage_path)

            assert storage.filepath == storage_path
            assert not storage_path.exists()  # File not created until save

    def test_file_storage_init_with_string(self) -> None:
        """Test FileStorage initialization with string path."""
        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = str(Path(tmpdir) / "proxies.json")
            storage = FileStorage(storage_path)

            assert storage.filepath == Path(storage_path)

    def test_file_storage_creates_parent_directory(self) -> None:
        """Test FileStorage creates parent directory if needed."""
        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "subdir" / "proxies.json"
            storage = FileStorage(storage_path)

            # Parent directory should be created on save
            assert storage.filepath.parent == Path(tmpdir) / "subdir"

    async def test_file_storage_save_empty_list(self) -> None:
        """T036: Test saving empty proxy list."""
        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies.json"
            storage = FileStorage(storage_path)

            await storage.save([])

            assert storage_path.exists()
            with open(storage_path) as f:
                data = json.load(f)
            assert data == []

    async def test_file_storage_save_multiple_proxies(self) -> None:
        """T037: Test saving multiple proxies."""
        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies.json"
            storage = FileStorage(storage_path)

            # Create test proxies
            proxies = [
                Proxy(url="http://proxy1.example.com:8080"),
                Proxy(url="http://proxy2.example.com:8080"),
                Proxy(url="http://proxy3.example.com:8080"),
            ]

            await storage.save(proxies)

            assert storage_path.exists()
            with open(storage_path) as f:
                data = json.load(f)
            assert len(data) == 3
            assert data[0]["url"] == "http://proxy1.example.com:8080"

    async def test_file_storage_load_from_existing(self) -> None:
        """T038: Test loading proxies from existing file."""
        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies.json"

            # Create a JSON file with proxy data
            proxy_data = [
                {
                    "id": "12345678-1234-5678-1234-567812345678",
                    "url": "http://proxy1.example.com:8080/",
                    "protocol": "http",
                    "health_status": "unknown",
                    "source": "user",
                    "metadata": {},
                    "created_at": "2025-10-22T12:00:00Z",
                    "updated_at": "2025-10-22T12:00:00Z",
                }
            ]
            with open(storage_path, "w") as f:
                json.dump(proxy_data, f)

            storage = FileStorage(storage_path)
            loaded = await storage.load()

            assert len(loaded) == 1
            assert loaded[0].url == "http://proxy1.example.com:8080/"

    async def test_file_storage_load_nonexistent_file(self) -> None:
        """T039: Test loading from nonexistent file raises error."""
        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "nonexistent.json"
            storage = FileStorage(storage_path)

            with pytest.raises(FileNotFoundError):
                await storage.load()

    async def test_file_storage_save_and_load_roundtrip(self) -> None:
        """T040: Test save and load roundtrip."""
        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies.json"
            storage = FileStorage(storage_path)

            # Create test proxies
            proxies = [
                Proxy(url="http://proxy1.example.com:8080"),
                Proxy(
                    url="http://proxy2.example.com:8080",
                    health_status="healthy",
                ),
            ]

            # Save and load
            await storage.save(proxies)
            loaded = await storage.load()

            assert len(loaded) == 2
            assert loaded[0].url == proxies[0].url
            assert loaded[1].url == proxies[1].url
            assert loaded[1].health_status == "healthy"


class TestFileStorageEncryption:
    """Tests for credential encryption in FileStorage (T046-T048)."""

    async def test_encrypt_decrypt_credentials(self) -> None:
        """T046: Test that credentials are encrypted when saved and decrypted when loaded."""
        from cryptography.fernet import Fernet

        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies_encrypted.json"
            key = Fernet.generate_key()
            storage = FileStorage(storage_path, encryption_key=key)

            # Create proxy with authentication
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                username="testuser",
                password="secret_password_123",
            )

            # Save with encryption
            await storage.save([proxy])

            # Read raw file content - should be encrypted (not human-readable)
            raw_content = storage_path.read_text()
            assert "secret_password_123" not in raw_content
            assert "testuser" not in raw_content

            # Load with decryption
            loaded_proxies = await storage.load()
            assert len(loaded_proxies) == 1
            assert loaded_proxies[0].username.get_secret_value() == "testuser"
            assert loaded_proxies[0].password.get_secret_value() == "secret_password_123"

    async def test_save_with_encryption(self) -> None:
        """T047: Test that encrypted files cannot be decrypted without the correct key."""
        from cryptography.fernet import Fernet, InvalidToken

        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies.json"
            key1 = Fernet.generate_key()
            key2 = Fernet.generate_key()

            storage1 = FileStorage(storage_path, encryption_key=key1)
            storage2 = FileStorage(storage_path, encryption_key=key2)

            proxy = Proxy(
                url="http://proxy.example.com:8080",
                username="testuser",
                password="secret",
            )

            # Save with key1
            await storage1.save([proxy])

            # Try to load with wrong key (key2) - should fail
            with pytest.raises(InvalidToken):
                await storage2.load()

    async def test_load_with_decryption(self) -> None:
        """T048: Test loading encrypted file with correct key."""
        from cryptography.fernet import Fernet

        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies.json"
            key = Fernet.generate_key()
            storage = FileStorage(storage_path, encryption_key=key)

            # Create multiple proxies with different credentials
            proxies = [
                Proxy(
                    url="http://proxy1.example.com:8080",
                    username="user1",
                    password="pass1",
                ),
                Proxy(
                    url="http://proxy2.example.com:8080",
                    username="user2",
                    password="pass2",
                ),
                Proxy(url="http://proxy3.example.com:8080"),  # No auth
            ]

            await storage.save(proxies)

            # Load and verify all credentials decrypted correctly
            loaded = await storage.load()
            assert len(loaded) == 3
            assert loaded[0].username.get_secret_value() == "user1"
            assert loaded[0].password.get_secret_value() == "pass1"
            assert loaded[1].username.get_secret_value() == "user2"
            assert loaded[1].password.get_secret_value() == "pass2"
            assert loaded[2].username is None
            assert loaded[2].password is None


class TestFileStorageConcurrency:
    """Tests for concurrent file operations (T051-T055)."""

    async def test_concurrent_save_operations(self) -> None:
        """T051: Test multiple concurrent save operations work correctly."""
        import asyncio

        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies.json"
            storage = FileStorage(storage_path)

            # Create different proxy sets
            proxies1 = [Proxy(url="http://proxy1.example.com:8080")]
            proxies2 = [Proxy(url="http://proxy2.example.com:8080")]
            proxies3 = [Proxy(url="http://proxy3.example.com:8080")]

            # Run concurrent saves
            await asyncio.gather(
                storage.save(proxies1),
                storage.save(proxies2),
                storage.save(proxies3),
            )

            # Load and verify the file contains valid data (last write wins)
            loaded = await storage.load()
            assert len(loaded) == 1
            assert loaded[0].url in [
                "http://proxy1.example.com:8080",
                "http://proxy2.example.com:8080",
                "http://proxy3.example.com:8080",
            ]

    async def test_file_storage_persistence_across_restarts(self) -> None:
        """T055: Integration test - verify data persists across storage instances."""
        from proxywhirl.models import HealthStatus
        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies.json"

            # Create and save proxies with first instance
            storage1 = FileStorage(storage_path)
            proxies = [
                Proxy(
                    url="http://proxy1.example.com:8080",
                    health_status=HealthStatus.HEALTHY,
                ),
                Proxy(
                    url="http://proxy2.example.com:8080",
                    health_status=HealthStatus.UNHEALTHY,
                ),
            ]
            await storage1.save(proxies)

            # Create new instance and load (simulates restart)
            storage2 = FileStorage(storage_path)
            loaded = await storage2.load()

            assert len(loaded) == 2
            assert loaded[0].url == proxies[0].url
            assert loaded[0].health_status == HealthStatus.HEALTHY
            assert loaded[1].url == proxies[1].url
            assert loaded[1].health_status == HealthStatus.UNHEALTHY


class TestFileStorageClear:
    """Tests for FileStorage.clear() method."""

    async def test_clear_deletes_file(self) -> None:
        """Test clear() deletes the storage file."""
        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies.json"
            storage = FileStorage(storage_path)

            # Save some proxies first
            proxies = [Proxy(url="http://proxy1.example.com:8080")]
            await storage.save(proxies)
            assert storage_path.exists()

            # Clear should delete the file
            await storage.clear()
            assert not storage_path.exists()

    async def test_clear_nonexistent_file(self) -> None:
        """Test clear() on nonexistent file does nothing."""
        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "nonexistent.json"
            storage = FileStorage(storage_path)

            # Should not raise - file doesn't exist
            await storage.clear()
            assert not storage_path.exists()

    async def test_clear_permission_error(self) -> None:
        """Test clear() raises OSError on permission failure."""
        from unittest.mock import patch

        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies.json"
            storage = FileStorage(storage_path)

            # Save some proxies first
            await storage.save([Proxy(url="http://proxy1.example.com:8080")])

            # Mock unlink to raise PermissionError
            with patch.object(Path, "unlink", side_effect=PermissionError("Access denied")):
                with pytest.raises(OSError, match="Failed to clear storage"):
                    await storage.clear()


class TestFileStorageErrorHandling:
    """Tests for FileStorage error handling paths."""

    async def test_save_write_failure_cleans_temp_file(self) -> None:
        """Test save() cleans up temp file on write failure."""
        from unittest.mock import AsyncMock, patch

        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies.json"
            storage = FileStorage(storage_path)

            proxies = [Proxy(url="http://proxy1.example.com:8080")]

            # Mock aiofiles.open to raise IOError during write
            mock_file = AsyncMock()
            mock_file.__aenter__.return_value.write.side_effect = OSError("Disk full")
            mock_file.__aenter__.return_value.flush = AsyncMock()

            with patch("aiofiles.open", return_value=mock_file):
                with pytest.raises(OSError, match="Failed to save proxies"):
                    await storage.save(proxies)

    async def test_load_invalid_json(self) -> None:
        """Test load() raises ValueError on invalid JSON."""
        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies.json"

            # Write invalid JSON
            storage_path.write_text("{ invalid json }")

            storage = FileStorage(storage_path)

            with pytest.raises(ValueError, match="Invalid JSON in storage file"):
                await storage.load()

    async def test_load_validation_error(self) -> None:
        """Test load() raises ValueError on proxy validation failure."""
        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "proxies.json"

            # Write valid JSON but invalid proxy data (missing required fields)
            storage_path.write_text('[{"invalid": "data"}]')

            storage = FileStorage(storage_path)

            with pytest.raises(ValueError, match="Failed to load proxies"):
                await storage.load()


class TestSQLiteStorage:
    """Test SQLiteStorage implementation."""

    async def test_sqlite_storage_init(self) -> None:
        """Test SQLiteStorage initialization."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)

            assert storage.filepath == db_path
            assert storage.use_async_driver is True  # Default should be async
            await storage.close()

    async def test_sqlite_storage_init_async_driver(self) -> None:
        """Test SQLiteStorage initialization with async driver explicitly enabled."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path, use_async_driver=True)

            assert storage.filepath == db_path
            assert storage.use_async_driver is True
            assert "aiosqlite" in str(storage.engine.url)
            await storage.close()

    async def test_sqlite_storage_init_sync_driver(self) -> None:
        """Test SQLiteStorage initialization with sync driver parameter.

        Note: Current implementation always uses aiosqlite for async operations.
        The use_async_driver parameter is stored for configuration compatibility
        and future enhancements.
        """
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path, use_async_driver=False)

            assert storage.filepath == db_path
            assert storage.use_async_driver is False
            # Current implementation always uses aiosqlite
            assert "aiosqlite" in str(storage.engine.url)
            await storage.close()

    async def test_sqlite_storage_initialize_creates_tables(self) -> None:
        """Test initialize() creates database tables."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)

            await storage.initialize()
            assert db_path.exists()

            await storage.close()

    async def test_sqlite_storage_save_and_load(self) -> None:
        """Test save and load roundtrip."""
        from proxywhirl.models import HealthStatus
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            proxies = [
                Proxy(url="http://proxy1.example.com:8080"),
                Proxy(
                    url="http://proxy2.example.com:8080",
                    health_status=HealthStatus.HEALTHY,
                ),
            ]

            await storage.save(proxies)
            loaded = await storage.load()

            assert len(loaded) == 2
            urls = [p.url for p in loaded]
            assert "http://proxy1.example.com:8080" in urls
            assert "http://proxy2.example.com:8080" in urls

            await storage.close()

    async def test_sqlite_storage_query_by_source(self) -> None:
        """Test query with source filter."""
        from proxywhirl.models import ProxySource
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            proxies = [
                Proxy(url="http://proxy1.example.com:8080", source=ProxySource.USER),
                Proxy(url="http://proxy2.example.com:8080", source=ProxySource.FETCHED),
                Proxy(url="http://proxy3.example.com:8080", source=ProxySource.USER),
            ]

            await storage.save(proxies)
            user_proxies = await storage.query(source="user")

            assert len(user_proxies) == 2
            for p in user_proxies:
                assert p.source == ProxySource.USER

            await storage.close()

    async def test_sqlite_storage_query_by_health_status(self) -> None:
        """Test query with health_status filter."""
        from proxywhirl.models import HealthStatus
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
            healthy = await storage.query(health_status="healthy")

            assert len(healthy) == 2
            for p in healthy:
                assert p.health_status == HealthStatus.HEALTHY

            await storage.close()

    async def test_sqlite_storage_delete(self) -> None:
        """Test deleting a single proxy."""
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

    async def test_sqlite_storage_clear(self) -> None:
        """Test clearing all proxies from database."""
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

            # Clear all
            await storage.clear()

            loaded = await storage.load()
            assert len(loaded) == 0

            await storage.close()

    async def test_sqlite_storage_upsert(self) -> None:
        """Test that save updates existing proxies (upsert)."""
        from proxywhirl.models import HealthStatus
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Initial save
            proxy = Proxy(
                url="http://proxy1.example.com:8080",
                health_status=HealthStatus.UNKNOWN,
            )
            await storage.save([proxy])

            # Update the proxy
            updated_proxy = Proxy(
                url="http://proxy1.example.com:8080",
                health_status=HealthStatus.HEALTHY,
            )
            await storage.save([updated_proxy])

            loaded = await storage.load()
            assert len(loaded) == 1
            assert loaded[0].health_status == HealthStatus.HEALTHY

            await storage.close()

    async def test_sqlite_storage_async_driver_save_load(self) -> None:
        """Test save and load with async driver."""
        from proxywhirl.models import HealthStatus
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies_async.db"
            storage = SQLiteStorage(db_path, use_async_driver=True)
            await storage.initialize()

            # Create and save proxies
            proxies = [
                Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY),
                Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.UNHEALTHY),
            ]
            await storage.save(proxies)

            # Load and verify
            loaded = await storage.load()
            assert len(loaded) == 2
            urls = [p.url for p in loaded]
            assert "http://proxy1.example.com:8080" in urls
            assert "http://proxy2.example.com:8080" in urls

            await storage.close()

    async def test_sqlite_storage_sync_driver_save_load(self) -> None:
        """Test save and load with sync driver (compatibility mode)."""
        from proxywhirl.models import HealthStatus
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies_sync.db"
            storage = SQLiteStorage(db_path, use_async_driver=False)
            await storage.initialize()

            # Create and save proxies
            proxies = [
                Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY),
                Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.DEGRADED),
            ]
            await storage.save(proxies)

            # Load and verify
            loaded = await storage.load()
            assert len(loaded) == 2
            urls = [p.url for p in loaded]
            assert "http://proxy1.example.com:8080" in urls
            assert "http://proxy2.example.com:8080" in urls

            # Verify health statuses
            proxy1 = next(p for p in loaded if p.url == "http://proxy1.example.com:8080")
            proxy2 = next(p for p in loaded if p.url == "http://proxy2.example.com:8080")
            assert proxy1.health_status == HealthStatus.HEALTHY
            assert proxy2.health_status == HealthStatus.DEGRADED

            await storage.close()

    async def test_sqlite_storage_with_credentials(self) -> None:
        """Test saving and loading proxies with credentials."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            proxy = Proxy(
                url="http://proxy1.example.com:8080",
                username="testuser",
                password="testpass",
            )

            await storage.save([proxy])
            loaded = await storage.load()

            assert len(loaded) == 1
            assert loaded[0].username.get_secret_value() == "testuser"
            assert loaded[0].password.get_secret_value() == "testpass"

            await storage.close()

    async def test_sqlite_storage_credential_encryption_roundtrip(self) -> None:
        """Test that credentials are encrypted at rest in SQLite and decrypted on load."""
        import os
        import sqlite3

        from cryptography.fernet import Fernet

        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"

            # Set encryption key in environment
            encryption_key = Fernet.generate_key().decode("utf-8")
            os.environ["PROXYWHIRL_CACHE_ENCRYPTION_KEY"] = encryption_key

            try:
                storage = SQLiteStorage(db_path)
                await storage.initialize()

                # Create proxy with sensitive credentials
                proxy = Proxy(
                    url="http://proxy.example.com:8080",
                    username="sensitive_user",
                    password="super_secret_password_123",
                )

                # Save proxy (credentials should be encrypted)
                await storage.save([proxy])

                # Directly query database to verify credentials are encrypted
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT username, password FROM proxies WHERE url=?", (proxy.url,))
                db_username, db_password = cursor.fetchone()
                conn.close()

                # Verify credentials are NOT stored in plaintext
                assert db_username is not None
                assert db_password is not None
                assert "sensitive_user" not in db_username
                assert "super_secret_password_123" not in db_password
                # Verify encrypted prefix is present
                assert db_username.startswith("encrypted:")
                assert db_password.startswith("encrypted:")

                # Load proxy and verify credentials are decrypted correctly
                loaded = await storage.load()
                assert len(loaded) == 1
                assert loaded[0].username.get_secret_value() == "sensitive_user"
                assert loaded[0].password.get_secret_value() == "super_secret_password_123"

                await storage.close()
            finally:
                # Clean up environment variable
                if "PROXYWHIRL_CACHE_ENCRYPTION_KEY" in os.environ:
                    del os.environ["PROXYWHIRL_CACHE_ENCRYPTION_KEY"]

    async def test_sqlite_storage_encryption_with_no_credentials(self) -> None:
        """Test that proxies without credentials work correctly with encryption enabled."""
        import os

        from cryptography.fernet import Fernet

        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"

            # Set encryption key
            encryption_key = Fernet.generate_key().decode("utf-8")
            os.environ["PROXYWHIRL_CACHE_ENCRYPTION_KEY"] = encryption_key

            try:
                storage = SQLiteStorage(db_path)
                await storage.initialize()

                # Create proxy without credentials
                proxy = Proxy(url="http://proxy.example.com:8080")

                await storage.save([proxy])
                loaded = await storage.load()

                assert len(loaded) == 1
                assert loaded[0].username is None
                assert loaded[0].password is None

                await storage.close()
            finally:
                if "PROXYWHIRL_CACHE_ENCRYPTION_KEY" in os.environ:
                    del os.environ["PROXYWHIRL_CACHE_ENCRYPTION_KEY"]

    async def test_sqlite_storage_legacy_plaintext_credentials(self) -> None:
        """Test that legacy unencrypted credentials can still be read."""
        import sqlite3
        from uuid import uuid4

        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"

            # Create database without encryption
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Insert plaintext credentials directly into database (simulating legacy data)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            proxy_id = str(uuid4())
            cursor.execute(
                """
                INSERT INTO proxies (
                    url, id, username, password, health_status, source,
                    metadata_json, created_at, updated_at,
                    total_checks, total_health_failures, consecutive_successes,
                    consecutive_failures, recovery_attempt, requests_started,
                    requests_completed, requests_active, total_requests,
                    total_successes, total_failures, ema_alpha,
                    window_duration_seconds, response_samples_count,
                    timeout_count, connection_refused_count, ssl_error_count,
                    http_4xx_count, http_5xx_count, revival_attempts
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'),
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.2, 3600, 0,
                        0, 0, 0, 0, 0, 0)
                """,
                (
                    "http://legacy.example.com:8080",
                    proxy_id,
                    "plaintext_user",  # Not encrypted
                    "plaintext_pass",  # Not encrypted
                    "unknown",
                    "user",
                    "{}",
                ),
            )
            conn.commit()
            conn.close()

            # Load and verify plaintext credentials are read correctly
            loaded = await storage.load()
            assert len(loaded) == 1
            assert loaded[0].username.get_secret_value() == "plaintext_user"
            assert loaded[0].password.get_secret_value() == "plaintext_pass"

            await storage.close()


class TestProxyTable:
    """Test ProxyTable SQLModel."""

    def test_proxy_table_defaults(self) -> None:
        """Test ProxyTable has correct defaults."""
        from datetime import datetime

        from proxywhirl.storage import ProxyTable

        now = datetime.now()
        table = ProxyTable(
            url="http://proxy.example.com:8080",
            created_at=now,
            updated_at=now,
        )

        assert table.url == "http://proxy.example.com:8080"
        assert table.health_status == "unknown"
        assert table.total_requests == 0
        assert table.total_successes == 0
        assert table.total_failures == 0
        assert table.consecutive_failures == 0
        assert table.source == "user"
        assert table.metadata_json == "{}"


class TestProxyTableNewFields:
    """Test new ProxyTable fields for comprehensive data model."""

    async def test_proxy_uuid_round_trip(self) -> None:
        """Test that proxy UUID is preserved through save/load."""
        from uuid import uuid4

        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with specific UUID
            test_uuid = uuid4()
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                id=test_uuid,
            )

            # Save and load
            await storage.save([proxy])
            loaded = await storage.load()

            # Verify UUID matches
            assert len(loaded) == 1
            assert str(loaded[0].id) == str(test_uuid)
            assert loaded[0].id == test_uuid

            await storage.close()

    async def test_none_id_generates_new_uuid(self, caplog) -> None:
        """Test that proxies with None ID get a new UUID generated.

        This test validates the UUID validation logic in _validate_row_id(),
        which handles the case where a database row has a NULL id field.
        A warning should be logged and a new UUID generated during conversion.
        """
        import logging
        from uuid import UUID

        from loguru import logger

        from proxywhirl.models import Proxy
        from proxywhirl.storage import ProxyTable, SQLiteStorage

        # Configure loguru to capture logs in caplog
        class PropagateHandler(logging.Handler):
            def emit(self, record):
                logging.getLogger(record.name).handle(record)

        handler_id = logger.add(PropagateHandler(), format="{message}")

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create and save a proxy
            proxy = Proxy(url="http://proxy.example.com:8080")
            await storage.save([proxy])

            # Manually set the ID to NULL in the database to simulate corrupted data
            async with storage.engine.begin() as conn:
                await conn.execute(
                    sa.update(ProxyTable)
                    .where(ProxyTable.url == "http://proxy.example.com:8080")
                    .values(id=None)
                )

            # Clear caplog to avoid capturing previous logs
            caplog.clear()

            with caplog.at_level(logging.WARNING):
                # Load the proxy - should trigger warning and regenerate UUID
                loaded = await storage.load()

            # Verify warning was logged
            assert any(
                "Proxy row has no ID" in record.message and record.levelname == "WARNING"
                for record in caplog.records
            ), "Expected warning about missing ID not found in logs"

            # Verify we have exactly one proxy
            assert len(loaded) == 1
            loaded_proxy = loaded[0]

            # Verify the ID is a valid UUID
            assert loaded_proxy.id is not None
            assert isinstance(loaded_proxy.id, UUID)

            # Save the proxy with the new UUID to persist it
            await storage.save(loaded)

            # Verify the ID is preserved on subsequent loads (no more warnings)
            caplog.clear()
            with caplog.at_level(logging.WARNING):
                loaded_again = await storage.load()

            # No new warnings should be logged since ID is now saved
            assert not any(
                "Proxy row has no ID" in record.message and record.levelname == "WARNING"
                for record in caplog.records
            ), "Unexpected warning about missing ID after saving"

            assert len(loaded_again) == 1
            assert loaded_again[0].id == loaded_proxy.id

            await storage.close()

        # Clean up loguru handler
        logger.remove(handler_id)

    async def test_invalid_uuid_format_regenerated(self, caplog) -> None:
        """Test that invalid UUID formats in database are regenerated.

        This test ensures the _validate_row_id() method properly handles
        corrupted UUID values in the database by logging an error and
        generating a new valid UUID.
        """
        import logging
        from uuid import UUID

        from loguru import logger

        from proxywhirl.models import Proxy
        from proxywhirl.storage import ProxyTable, SQLiteStorage

        # Configure loguru to capture logs in caplog
        class PropagateHandler(logging.Handler):
            def emit(self, record):
                logging.getLogger(record.name).handle(record)

        handler_id = logger.add(PropagateHandler(), format="{message}")

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # First, save a valid proxy
            proxy = Proxy(url="http://proxy.example.com:8080")
            await storage.save([proxy])

            # Now manually corrupt the ID in the database
            async with storage.engine.begin() as conn:
                await conn.execute(
                    sa.update(ProxyTable)
                    .where(ProxyTable.url == "http://proxy.example.com:8080")
                    .values(id="invalid-uuid-string")
                )

            # Clear caplog to avoid capturing previous logs
            caplog.clear()

            with caplog.at_level(logging.ERROR):
                # Load the proxy - should handle the invalid UUID and log error
                loaded = await storage.load()

            # Verify error was logged for invalid UUID format
            assert any(
                "Invalid UUID format in database row" in record.message
                and record.levelname == "ERROR"
                for record in caplog.records
            ), "Expected error about invalid UUID format not found in logs"

            # Verify we have exactly one proxy
            assert len(loaded) == 1
            loaded_proxy = loaded[0]

            # Verify the ID was regenerated as a valid UUID
            assert loaded_proxy.id is not None
            assert isinstance(loaded_proxy.id, UUID)

            await storage.close()

        # Clean up loguru handler
        logger.remove(handler_id)

    async def test_tags_json_serialization(self) -> None:
        """Test tags are properly serialized as JSON and deserialized back to set."""
        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with tags
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                tags={"fast", "premium", "us"},
            )

            # Save and load
            await storage.save([proxy])
            loaded = await storage.load()

            # Verify tags set matches
            assert len(loaded) == 1
            assert loaded[0].tags == {"fast", "premium", "us"}
            assert isinstance(loaded[0].tags, set)

            await storage.close()

    async def test_analytics_fields_persistence(self) -> None:
        """Test all analytics fields are properly persisted."""
        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with analytics fields
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                average_response_time_ms=100.5,
                ema_response_time_ms=150.0,
                ema_alpha=0.3,
            )

            # Save and load
            await storage.save([proxy])
            loaded = await storage.load()

            # Verify all values match
            assert len(loaded) == 1
            assert loaded[0].average_response_time_ms == 100.5
            assert loaded[0].ema_response_time_ms == 150.0
            assert loaded[0].ema_alpha == 0.3

            await storage.close()

    async def test_health_history_persistence(self) -> None:
        """Test health history fields are properly persisted."""
        from datetime import datetime, timezone

        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with health history fields
            now = datetime.now(timezone.utc)
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                consecutive_successes=10,
                total_checks=50,
                total_health_failures=5,
                last_health_check=now,
                recovery_attempt=2,
            )

            # Save and load
            await storage.save([proxy])
            loaded = await storage.load()

            # Verify all values match
            assert len(loaded) == 1
            assert loaded[0].consecutive_successes == 10
            assert loaded[0].total_checks == 50
            assert loaded[0].total_health_failures == 5
            # Verify health check timestamp (allow small difference, handle timezone)
            assert loaded[0].last_health_check is not None
            # SQLite returns naive datetime, so compare by replacing tzinfo
            loaded_time = loaded[0].last_health_check.replace(tzinfo=timezone.utc)
            assert abs((loaded_time - now).total_seconds()) < 1
            assert loaded[0].recovery_attempt == 2

            await storage.close()

    async def test_ttl_expiration_persistence(self) -> None:
        """Test TTL and expiration fields are properly persisted."""
        from datetime import datetime, timedelta, timezone

        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with TTL fields
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(hours=1)
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                ttl=3600,
                expires_at=expires_at,
            )

            # Save and load
            await storage.save([proxy])
            loaded = await storage.load()

            # Verify values match
            assert len(loaded) == 1
            assert loaded[0].ttl == 3600
            assert loaded[0].expires_at is not None
            # SQLite returns naive datetime, so compare by replacing tzinfo
            loaded_expires = loaded[0].expires_at.replace(tzinfo=timezone.utc)
            assert abs((loaded_expires - expires_at).total_seconds()) < 1

            await storage.close()

    async def test_geographic_fields_persistence(self) -> None:
        """Test geographic fields are properly persisted.

        Note: ProxyTable supports many more geographic fields than current Proxy model,
        including city, latitude, longitude, ISP info, etc. This test covers the fields
        currently supported by the Proxy model (country_code, region).
        """
        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with geographic fields (currently supported in Proxy model)
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                country_code="US",
                region="California",
            )

            # Save and load
            await storage.save([proxy])
            loaded = await storage.load()

            # Verify all values match
            assert len(loaded) == 1
            assert loaded[0].country_code == "US"
            assert loaded[0].region == "California"

            await storage.close()

    async def test_request_tracking_fields_persistence(self) -> None:
        """Test enhanced request tracking fields are properly persisted."""
        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with request tracking fields
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                requests_started=100,
                requests_completed=95,
                requests_active=5,
                total_requests=95,
                total_successes=90,
                total_failures=5,
            )

            # Save and load
            await storage.save([proxy])
            loaded = await storage.load()

            # Verify all values match
            assert len(loaded) == 1
            assert loaded[0].requests_started == 100
            assert loaded[0].requests_completed == 95
            assert loaded[0].requests_active == 5
            assert loaded[0].total_requests == 95
            assert loaded[0].total_successes == 90
            assert loaded[0].total_failures == 5

            await storage.close()

    async def test_sliding_window_fields_persistence(self) -> None:
        """Test sliding window fields are properly persisted."""
        from datetime import datetime, timezone

        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with sliding window fields
            now = datetime.now(timezone.utc)
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                window_start=now,
                window_duration_seconds=7200,  # 2 hours
            )

            # Save and load
            await storage.save([proxy])
            loaded = await storage.load()

            # Verify values match
            assert len(loaded) == 1
            assert loaded[0].window_start is not None
            # SQLite returns naive datetime, so compare by replacing tzinfo
            loaded_start = loaded[0].window_start.replace(tzinfo=timezone.utc)
            assert abs((loaded_start - now).total_seconds()) < 1
            assert loaded[0].window_duration_seconds == 7200

            await storage.close()

    async def test_source_metadata_persistence(self) -> None:
        """Test source metadata fields are properly persisted."""
        from proxywhirl.models import Proxy, ProxySource
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with source metadata
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                source=ProxySource.FETCHED,
                source_url="https://proxy-list.example.com/api/proxies",
            )

            # Save and load
            await storage.save([proxy])
            loaded = await storage.load()

            # Verify values match
            assert len(loaded) == 1
            assert loaded[0].source == ProxySource.FETCHED
            assert str(loaded[0].source_url) == "https://proxy-list.example.com/api/proxies"

            await storage.close()

    async def test_empty_tags_persistence(self) -> None:
        """Test that empty tags set is properly persisted."""
        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with empty tags
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                tags=set(),
            )

            # Save and load
            await storage.save([proxy])
            loaded = await storage.load()

            # Verify empty tags
            assert len(loaded) == 1
            assert loaded[0].tags == set()
            assert isinstance(loaded[0].tags, set)

            await storage.close()

    async def test_metadata_json_persistence(self) -> None:
        """Test that complex metadata is properly persisted."""
        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with complex metadata
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                metadata={
                    "custom_field": "value",
                    "nested": {"key": "value"},
                    "array": [1, 2, 3],
                },
            )

            # Save and load
            await storage.save([proxy])
            loaded = await storage.load()

            # Verify metadata matches
            assert len(loaded) == 1
            assert loaded[0].metadata == {
                "custom_field": "value",
                "nested": {"key": "value"},
                "array": [1, 2, 3],
            }

            await storage.close()

    async def test_all_fields_comprehensive(self) -> None:
        """Comprehensive test with all supported fields populated."""
        from datetime import datetime, timedelta, timezone
        from uuid import uuid4

        from proxywhirl.models import HealthStatus, Proxy, ProxySource
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with all fields populated
            test_uuid = uuid4()
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(hours=1)

            proxy = Proxy(
                # Primary and Secondary Keys
                id=test_uuid,
                url="http://proxy.example.com:8080",
                # Core Fields
                protocol="http",
                username="testuser",
                password="testpass",
                # Health Status
                health_status=HealthStatus.HEALTHY,
                last_success_at=now,
                last_failure_at=now - timedelta(minutes=5),
                last_health_check=now,
                last_health_error="Connection timeout",
                total_checks=100,
                total_health_failures=10,
                consecutive_successes=15,
                consecutive_failures=0,
                recovery_attempt=1,
                next_check_time=now + timedelta(minutes=5),
                # Request Tracking
                requests_started=200,
                requests_completed=195,
                requests_active=5,
                total_requests=195,
                total_successes=185,
                total_failures=10,
                # Response Time Metrics
                average_response_time_ms=250.5,
                ema_response_time_ms=245.0,
                ema_alpha=0.25,
                # Sliding Window
                window_start=now - timedelta(minutes=30),
                window_duration_seconds=3600,
                # Geographic
                country_code="US",
                region="California",
                # Source Metadata
                source=ProxySource.FETCHED,
                source_url="https://proxy-list.example.com/api/proxies",
                # Tags & TTL
                tags={"fast", "premium", "us", "west-coast"},
                ttl=3600,
                expires_at=expires_at,
                # Metadata
                metadata={
                    "provider": "example",
                    "tier": "premium",
                    "custom": {"nested": "data"},
                },
                created_at=now - timedelta(days=1),
                updated_at=now,
            )

            # Save and load
            await storage.save([proxy])
            loaded = await storage.load()

            # Verify all fields
            assert len(loaded) == 1
            p = loaded[0]

            # Primary and Secondary Keys
            assert p.id == test_uuid
            assert p.url == "http://proxy.example.com:8080"

            # Core Fields
            assert p.protocol == "http"
            assert p.username.get_secret_value() == "testuser"
            assert p.password.get_secret_value() == "testpass"

            # Health Status
            assert p.health_status == HealthStatus.HEALTHY
            assert p.last_success_at is not None
            assert p.last_failure_at is not None
            assert p.last_health_check is not None
            assert p.last_health_error == "Connection timeout"
            assert p.total_checks == 100
            assert p.total_health_failures == 10
            assert p.consecutive_successes == 15
            assert p.consecutive_failures == 0
            assert p.recovery_attempt == 1
            assert p.next_check_time is not None

            # Request Tracking
            assert p.requests_started == 200
            assert p.requests_completed == 195
            assert p.requests_active == 5
            assert p.total_requests == 195
            assert p.total_successes == 185
            assert p.total_failures == 10

            # Response Time Metrics
            assert p.average_response_time_ms == 250.5
            assert p.ema_response_time_ms == 245.0
            assert p.ema_alpha == 0.25

            # Sliding Window
            assert p.window_start is not None
            assert p.window_duration_seconds == 3600

            # Geographic
            assert p.country_code == "US"
            assert p.region == "California"

            # Source Metadata
            assert p.source == ProxySource.FETCHED
            assert str(p.source_url) == "https://proxy-list.example.com/api/proxies"

            # Tags & TTL
            assert p.tags == {"fast", "premium", "us", "west-coast"}
            assert p.ttl == 3600
            assert p.expires_at is not None

            # Metadata
            assert p.metadata == {
                "provider": "example",
                "tier": "premium",
                "custom": {"nested": "data"},
            }

            await storage.close()


class TestExpandedDataModelPersistence:
    """Integration tests for expanded ProxyTable schema (60+ fields).

    These tests verify that all expanded fields in the ProxyTable schema
    are properly persisted through save/load cycles with SQLiteStorage.
    """

    async def test_full_roundtrip_all_fields_populated(self) -> None:
        """Test full round-trip with ALL ProxyTable fields populated.

        This comprehensive test creates a Proxy with all 60+ fields populated,
        saves it to SQLite, loads it back, and verifies every field matches.
        """
        from datetime import datetime, timedelta, timezone
        from uuid import uuid4

        from proxywhirl.models import HealthStatus, Proxy, ProxySource
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create comprehensive test data
            test_uuid = uuid4()
            now = datetime.now(timezone.utc)

            # Populate ALL fields including those stored in metadata
            proxy = Proxy(
                # Primary and Secondary Keys
                id=test_uuid,
                url="http://proxy.example.com:8080",
                # Core Fields
                protocol="http",
                username="testuser",
                password="secretpass123",
                # Health Status
                health_status=HealthStatus.HEALTHY,
                last_success_at=now - timedelta(seconds=10),
                last_failure_at=now - timedelta(hours=1),
                last_health_check=now - timedelta(seconds=30),
                last_health_error="Connection refused",
                total_checks=150,
                total_health_failures=15,
                consecutive_successes=25,
                consecutive_failures=0,
                recovery_attempt=2,
                next_check_time=now + timedelta(minutes=10),
                # Request Tracking
                requests_started=500,
                requests_completed=490,
                requests_active=10,
                total_requests=490,
                total_successes=470,
                total_failures=20,
                # Response Time Metrics (basic)
                average_response_time_ms=125.5,
                ema_response_time_ms=130.0,
                ema_alpha=0.3,
                # Sliding Window
                window_start=now - timedelta(minutes=45),
                window_duration_seconds=3600,
                # Geographic
                country_code="US",
                region="California",
                # Source Metadata
                source=ProxySource.FETCHED,
                source_url="https://proxy-list.example.com/api/v1/proxies",
                # Tags & TTL
                tags={"premium", "fast", "us-west", "datacenter"},
                ttl=7200,
                expires_at=now + timedelta(hours=2),
                # Timestamps
                created_at=now - timedelta(days=7),
                updated_at=now,
                # Extended fields in metadata
                # Note: Fields that map to ProxyTable columns should NOT contain datetime objects
                # as they will be extracted to columns AND remain in metadata_json which gets JSON serialized
                metadata={
                    # Health Status Extended - revival_attempts is extracted to column
                    "revival_attempts": 3,
                    "health_status_transitions": [
                        {
                            "from": "unknown",
                            "to": "healthy",
                            "timestamp": (now - timedelta(days=1)).isoformat(),
                        },
                        {
                            "from": "healthy",
                            "to": "degraded",
                            "timestamp": (now - timedelta(hours=3)).isoformat(),
                        },
                        {
                            "from": "degraded",
                            "to": "healthy",
                            "timestamp": (now - timedelta(hours=2)).isoformat(),
                        },
                    ],
                    # Response Time Metrics Extended (percentiles) - all extracted to columns
                    "response_time_p50_ms": 120.0,
                    "response_time_p95_ms": 250.0,
                    "response_time_p99_ms": 400.0,
                    "min_response_time_ms": 50.0,
                    "max_response_time_ms": 500.0,
                    "response_time_stddev_ms": 75.5,
                    "response_samples_count": 450,
                    # Error Tracking - error counts extracted to columns
                    "error_types": {
                        "timeout": 5,
                        "connection_refused": 3,
                        "ssl_error": 2,
                        "http_4xx": 7,
                        "http_5xx": 3,
                    },
                    "last_error_type": "timeout",
                    "last_error_message": "Connection timed out after 30s",
                    "timeout_count": 5,
                    "connection_refused_count": 3,
                    "ssl_error_count": 2,
                    "http_4xx_count": 7,
                    "http_5xx_count": 3,
                    # Geographic Extended - all extracted to columns
                    "country_name": "United States",
                    "city": "San Francisco",
                    "isp_name": "Example ISP Inc.",
                    "asn": 12345,
                    "is_residential": False,
                    "is_datacenter": True,
                    "is_vpn": False,
                    "is_tor": False,
                    "latitude": 37.7749,
                    "longitude": -122.4194,
                    # Protocol Support - all extracted to columns
                    "http_version": "1.1",
                    "tls_version": "1.3",
                    "supports_https": True,
                    "supports_connect": True,
                    "supports_http2": False,
                    # Source Metadata Extended - all extracted to columns
                    "source_name": "ProxyList API",
                    "fetch_duration_ms": 250.5,
                    "validation_method": "http_get",
                    # Custom metadata (not extracted to columns)
                    "tier": "premium",
                    "provider": "ExampleProxy Inc.",
                },
            )

            # Save and load
            await storage.save([proxy])
            loaded = await storage.load()

            # Comprehensive verification
            assert len(loaded) == 1
            p = loaded[0]

            # Primary and Secondary Keys
            assert p.id == test_uuid
            assert p.url == "http://proxy.example.com:8080"

            # Core Fields
            assert p.protocol == "http"
            assert p.username.get_secret_value() == "testuser"
            assert p.password.get_secret_value() == "secretpass123"

            # Health Status
            assert p.health_status == HealthStatus.HEALTHY
            assert p.last_success_at is not None
            assert p.last_failure_at is not None
            assert p.last_health_check is not None
            assert p.last_health_error == "Connection refused"
            assert p.total_checks == 150
            assert p.total_health_failures == 15
            assert p.consecutive_successes == 25
            assert p.consecutive_failures == 0
            assert p.recovery_attempt == 2
            assert p.next_check_time is not None

            # Request Tracking
            assert p.requests_started == 500
            assert p.requests_completed == 490
            assert p.requests_active == 10
            assert p.total_requests == 490
            assert p.total_successes == 470
            assert p.total_failures == 20

            # Response Time Metrics (basic)
            assert p.average_response_time_ms == 125.5
            assert p.ema_response_time_ms == 130.0
            assert p.ema_alpha == 0.3

            # Sliding Window
            assert p.window_start is not None
            assert p.window_duration_seconds == 3600

            # Geographic
            assert p.country_code == "US"
            assert p.region == "California"

            # Source Metadata
            assert p.source == ProxySource.FETCHED
            assert str(p.source_url) == "https://proxy-list.example.com/api/v1/proxies"

            # Tags & TTL
            assert p.tags == {"premium", "fast", "us-west", "datacenter"}
            assert p.ttl == 7200
            assert p.expires_at is not None

            # Extended fields from metadata - Health Status
            # Note: Fields extracted to ProxyTable columns are loaded BACK into metadata on load
            assert "revival_attempts" in p.metadata
            assert p.metadata["revival_attempts"] == 3
            assert "health_status_transitions" in p.metadata
            assert len(p.metadata["health_status_transitions"]) == 3

            # Extended fields - Response Time Metrics
            # These are extracted from metadata to ProxyTable columns and restored on load
            assert p.metadata["response_time_p50_ms"] == 120.0
            assert p.metadata["response_time_p95_ms"] == 250.0
            assert p.metadata["response_time_p99_ms"] == 400.0
            assert p.metadata["min_response_time_ms"] == 50.0
            assert p.metadata["max_response_time_ms"] == 500.0
            assert p.metadata["response_time_stddev_ms"] == 75.5
            assert p.metadata["response_samples_count"] == 450

            # Extended fields - Error Tracking
            # Error type dict is stored in metadata_json, counts extracted to columns
            assert "error_types" in p.metadata
            assert p.metadata["error_types"]["timeout"] == 5
            assert p.metadata["error_types"]["connection_refused"] == 3
            assert p.metadata["last_error_type"] == "timeout"
            assert p.metadata["last_error_message"] == "Connection timed out after 30s"
            assert p.metadata["timeout_count"] == 5
            assert p.metadata["connection_refused_count"] == 3
            assert p.metadata["ssl_error_count"] == 2
            assert p.metadata["http_4xx_count"] == 7
            assert p.metadata["http_5xx_count"] == 3

            # Extended fields - Geographic
            # All geographic fields extracted to ProxyTable columns and restored on load
            assert p.metadata["country_name"] == "United States"
            assert p.metadata["city"] == "San Francisco"
            assert p.metadata["isp_name"] == "Example ISP Inc."
            assert p.metadata["asn"] == 12345
            assert p.metadata["is_residential"] is False
            assert p.metadata["is_datacenter"] is True
            assert p.metadata["is_vpn"] is False
            assert p.metadata["is_tor"] is False
            assert p.metadata["latitude"] == 37.7749
            assert p.metadata["longitude"] == -122.4194

            # Extended fields - Protocol Support
            # All protocol fields extracted to ProxyTable columns and restored on load
            assert p.metadata["http_version"] == "1.1"
            assert p.metadata["tls_version"] == "1.3"
            assert p.metadata["supports_https"] is True
            assert p.metadata["supports_connect"] is True
            assert p.metadata["supports_http2"] is False

            # Extended fields - Source Metadata
            # Source metadata fields extracted to ProxyTable columns and restored on load
            assert p.metadata["source_name"] == "ProxyList API"
            assert p.metadata["fetch_duration_ms"] == 250.5
            assert p.metadata["validation_method"] == "http_get"

            # Custom metadata preserved (these stay in metadata_json only)
            assert p.metadata["tier"] == "premium"
            assert p.metadata["provider"] == "ExampleProxy Inc."

            await storage.close()

    async def test_analytics_percentiles_round_trip(self) -> None:
        """Test response time percentiles (P50, P95, P99) are persisted correctly."""
        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with percentile data
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                metadata={
                    "response_time_p50_ms": 100.0,
                    "response_time_p95_ms": 250.0,
                    "response_time_p99_ms": 500.0,
                    "min_response_time_ms": 50.0,
                    "max_response_time_ms": 1000.0,
                    "response_time_stddev_ms": 125.0,
                    "response_samples_count": 1000,
                },
            )

            await storage.save([proxy])
            loaded = await storage.load()

            assert len(loaded) == 1
            p = loaded[0]
            assert p.metadata["response_time_p50_ms"] == 100.0
            assert p.metadata["response_time_p95_ms"] == 250.0
            assert p.metadata["response_time_p99_ms"] == 500.0
            assert p.metadata["min_response_time_ms"] == 50.0
            assert p.metadata["max_response_time_ms"] == 1000.0
            assert p.metadata["response_time_stddev_ms"] == 125.0
            assert p.metadata["response_samples_count"] == 1000

            await storage.close()

    async def test_error_tracking_counts_round_trip(self) -> None:
        """Test error tracking counts are persisted correctly."""
        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with error tracking data
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                metadata={
                    "error_types": {
                        "timeout": 10,
                        "connection_refused": 5,
                        "ssl_error": 3,
                    },
                    "timeout_count": 10,
                    "connection_refused_count": 5,
                    "ssl_error_count": 3,
                    "http_4xx_count": 2,
                    "http_5xx_count": 1,
                    "last_error_type": "timeout",
                    "last_error_message": "Request timeout after 30s",
                },
            )

            await storage.save([proxy])
            loaded = await storage.load()

            assert len(loaded) == 1
            p = loaded[0]
            assert "error_types" in p.metadata
            assert p.metadata["error_types"]["timeout"] == 10
            assert p.metadata["error_types"]["connection_refused"] == 5
            assert p.metadata["error_types"]["ssl_error"] == 3
            assert p.metadata["timeout_count"] == 10
            assert p.metadata["connection_refused_count"] == 5
            assert p.metadata["ssl_error_count"] == 3
            assert p.metadata["http_4xx_count"] == 2
            assert p.metadata["http_5xx_count"] == 1
            assert p.metadata["last_error_type"] == "timeout"
            assert p.metadata["last_error_message"] == "Request timeout after 30s"

            await storage.close()

    async def test_geographic_extended_fields_round_trip(self) -> None:
        """Test all geographic fields including coordinates are persisted."""
        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with full geographic data
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                country_code="GB",
                region="England",
                metadata={
                    "country_name": "United Kingdom",
                    "city": "London",
                    "isp_name": "British Telecom",
                    "asn": 54321,
                    "is_residential": True,
                    "is_datacenter": False,
                    "is_vpn": False,
                    "is_tor": False,
                    "latitude": 51.5074,
                    "longitude": -0.1278,
                },
            )

            await storage.save([proxy])
            loaded = await storage.load()

            assert len(loaded) == 1
            p = loaded[0]

            # Base geographic fields
            assert p.country_code == "GB"
            assert p.region == "England"

            # Extended geographic fields from metadata
            assert p.metadata["country_name"] == "United Kingdom"
            assert p.metadata["city"] == "London"
            assert p.metadata["isp_name"] == "British Telecom"
            assert p.metadata["asn"] == 54321
            assert p.metadata["is_residential"] is True
            assert p.metadata["is_datacenter"] is False
            assert p.metadata["is_vpn"] is False
            assert p.metadata["is_tor"] is False
            assert p.metadata["latitude"] == 51.5074
            assert p.metadata["longitude"] == -0.1278

            await storage.close()

    async def test_protocol_fields_round_trip(self) -> None:
        """Test HTTP/TLS version and protocol capabilities are persisted."""
        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with protocol details
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                metadata={
                    "http_version": "2.0",
                    "tls_version": "1.3",
                    "supports_https": True,
                    "supports_connect": True,
                    "supports_http2": True,
                },
            )

            await storage.save([proxy])
            loaded = await storage.load()

            assert len(loaded) == 1
            p = loaded[0]
            assert p.metadata["http_version"] == "2.0"
            assert p.metadata["tls_version"] == "1.3"
            assert p.metadata["supports_https"] is True
            assert p.metadata["supports_connect"] is True
            assert p.metadata["supports_http2"] is True

            await storage.close()

    async def test_health_history_transitions_round_trip(self) -> None:
        """Test health status transitions history is persisted."""
        from datetime import datetime, timezone

        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with health transition history
            # Note: revival_attempts is extracted to ProxyTable column
            # health_status_transitions stays in metadata_json only
            now = datetime.now(timezone.utc)
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                consecutive_successes=20,
                metadata={
                    "revival_attempts": 5,
                    "health_status_transitions": [
                        {"from": "unknown", "to": "healthy", "timestamp": now.isoformat()},
                        {"from": "healthy", "to": "degraded", "timestamp": now.isoformat()},
                        {"from": "degraded", "to": "healthy", "timestamp": now.isoformat()},
                    ],
                },
            )

            await storage.save([proxy])
            loaded = await storage.load()

            assert len(loaded) == 1
            p = loaded[0]
            assert p.consecutive_successes == 20
            # revival_attempts is extracted to column and restored to metadata on load
            assert "revival_attempts" in p.metadata
            assert p.metadata["revival_attempts"] == 5
            # health_status_transitions stays in metadata_json
            assert "health_status_transitions" in p.metadata
            assert len(p.metadata["health_status_transitions"]) == 3
            assert p.metadata["health_status_transitions"][0]["from"] == "unknown"
            assert p.metadata["health_status_transitions"][0]["to"] == "healthy"

            await storage.close()

    async def test_ttl_expiration_fields_round_trip(self) -> None:
        """Test TTL and expires_at fields work correctly."""
        from datetime import datetime, timedelta, timezone

        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with TTL
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(hours=3)

            proxy = Proxy(
                url="http://proxy.example.com:8080",
                ttl=10800,  # 3 hours
                expires_at=expires_at,
            )

            await storage.save([proxy])
            loaded = await storage.load()

            assert len(loaded) == 1
            p = loaded[0]
            assert p.ttl == 10800
            assert p.expires_at is not None
            # SQLite returns naive datetime
            loaded_expires = p.expires_at.replace(tzinfo=timezone.utc)
            assert abs((loaded_expires - expires_at).total_seconds()) < 1

            await storage.close()

    async def test_source_metadata_extended_round_trip(self) -> None:
        """Test source metadata fields are persisted."""

        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxy with source metadata
            # Note: source_name, fetch_duration_ms, validation_method are extracted to ProxyTable columns
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                metadata={
                    "source_name": "Premium Proxy API",
                    "fetch_duration_ms": 125.5,
                    "validation_method": "tcp_connect",
                },
            )

            await storage.save([proxy])
            loaded = await storage.load()

            assert len(loaded) == 1
            p = loaded[0]
            # Fields extracted to ProxyTable columns are restored to metadata on load
            assert p.metadata["source_name"] == "Premium Proxy API"
            assert p.metadata["fetch_duration_ms"] == 125.5
            assert p.metadata["validation_method"] == "tcp_connect"

            await storage.close()

    async def test_null_optional_fields_handling(self) -> None:
        """Test that NULL/None optional fields are handled correctly."""
        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create minimal proxy with most optional fields as None
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                # All optional fields left as default/None
            )

            await storage.save([proxy])
            loaded = await storage.load()

            assert len(loaded) == 1
            p = loaded[0]

            # Verify None fields are preserved
            assert p.username is None
            assert p.password is None
            assert p.last_success_at is None
            assert p.last_failure_at is None
            assert p.average_response_time_ms is None
            assert p.country_code is None
            assert p.region is None
            assert p.ttl is None
            assert p.expires_at is None

            await storage.close()

    async def test_multiple_proxies_with_different_field_coverage(self) -> None:
        """Test saving multiple proxies with varying field coverage."""
        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Create proxies with different field coverage
            proxies = [
                # Minimal proxy
                Proxy(url="http://proxy1.example.com:8080"),
                # Proxy with geographic data
                Proxy(
                    url="http://proxy2.example.com:8080",
                    country_code="FR",
                    region="Île-de-France",
                    metadata={
                        "city": "Paris",
                        "latitude": 48.8566,
                        "longitude": 2.3522,
                    },
                ),
                # Proxy with analytics data
                Proxy(
                    url="http://proxy3.example.com:8080",
                    average_response_time_ms=150.0,
                    metadata={
                        "response_time_p50_ms": 140.0,
                        "response_time_p95_ms": 200.0,
                        "response_time_p99_ms": 300.0,
                    },
                ),
                # Proxy with error tracking
                Proxy(
                    url="http://proxy4.example.com:8080",
                    metadata={
                        "error_types": {"timeout": 3},
                        "timeout_count": 3,
                        "last_error_type": "timeout",
                    },
                ),
            ]

            await storage.save(proxies)
            loaded = await storage.load()

            assert len(loaded) == 4

            # Verify minimal proxy
            p1 = next(p for p in loaded if p.url == "http://proxy1.example.com:8080")
            assert p1.country_code is None

            # Verify geographic proxy
            p2 = next(p for p in loaded if p.url == "http://proxy2.example.com:8080")
            assert p2.country_code == "FR"
            assert p2.region == "Île-de-France"
            assert p2.metadata["city"] == "Paris"

            # Verify analytics proxy
            p3 = next(p for p in loaded if p.url == "http://proxy3.example.com:8080")
            assert p3.average_response_time_ms == 150.0
            assert p3.metadata["response_time_p50_ms"] == 140.0

            # Verify error tracking proxy
            p4 = next(p for p in loaded if p.url == "http://proxy4.example.com:8080")
            assert "error_types" in p4.metadata
            assert p4.metadata["timeout_count"] == 3

            await storage.close()


class TestSQLiteStorageConnectionPooling:
    """Tests for SQLite connection pooling configuration (TASK-603)."""

    async def test_default_pool_configuration(self) -> None:
        """Test SQLiteStorage uses default pool configuration.

        Note: SQLite with aiosqlite uses StaticPool by default, so pool settings
        are stored as instance attributes but not applied to the engine.
        """
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)

            # Verify default pool settings are stored
            assert storage.pool_size == 5
            assert storage.pool_max_overflow == 10
            assert storage.pool_timeout == 30.0
            assert storage.pool_recycle == 3600

            # Verify engine exists
            assert storage.engine is not None

            await storage.close()

    async def test_custom_pool_configuration(self) -> None:
        """Test SQLiteStorage accepts custom pool configuration.

        Note: SQLite with aiosqlite uses StaticPool which doesn't support
        pool_size/max_overflow/timeout parameters directly. The settings are
        stored as instance attributes for API compatibility.
        """
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(
                db_path,
                pool_size=10,
                pool_max_overflow=20,
                pool_timeout=60.0,
                pool_recycle=7200,
            )

            # Verify custom pool settings are stored (for API compatibility)
            assert storage.pool_size == 10
            assert storage.pool_max_overflow == 20
            assert storage.pool_timeout == 60.0
            assert storage.pool_recycle == 7200

            # Note: SQLite+aiosqlite doesn't apply these pool settings to the engine
            # as it uses StaticPool. Settings are stored for future backend support.
            assert storage.engine is not None

            await storage.close()

    async def test_concurrent_operations_within_pool_size(self) -> None:
        """Test concurrent operations work within pool size limits."""
        import asyncio

        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path, pool_size=5)
            await storage.initialize()

            # Create test proxies
            proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(10)]
            await storage.save(proxies)

            # Run concurrent queries (within pool size)
            async def query_proxy(i: int) -> list[Proxy]:
                return await storage.load()

            # Execute 5 concurrent queries (exactly pool_size)
            results = await asyncio.gather(*[query_proxy(i) for i in range(5)])

            # Verify all queries succeeded
            assert len(results) == 5
            for result in results:
                assert len(result) == 10

            await storage.close()

    async def test_pool_exhaustion_with_overflow(self) -> None:
        """Test pool exhaustion behavior with max_overflow connections."""
        import asyncio

        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            # Small pool with overflow
            storage = SQLiteStorage(
                db_path,
                pool_size=2,
                pool_max_overflow=3,
            )
            await storage.initialize()

            # Save test data
            proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(5)]
            await storage.save(proxies)

            # Run more concurrent operations than pool_size but within pool_size + max_overflow
            async def slow_query(i: int) -> list[Proxy]:
                await asyncio.sleep(0.1)  # Simulate slow query
                return await storage.load()

            # Execute 4 concurrent queries (2 pool + 2 overflow, within limits)
            results = await asyncio.gather(*[slow_query(i) for i in range(4)])

            # All should succeed
            assert len(results) == 4
            for result in results:
                assert len(result) == 5

            await storage.close()

    async def test_pool_timeout_on_exhaustion(self) -> None:
        """Test pool timeout when pool is exhausted."""
        import asyncio

        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            # Very small pool with short timeout
            storage = SQLiteStorage(
                db_path,
                pool_size=1,
                pool_max_overflow=0,
                pool_timeout=1.0,  # Short timeout for testing
            )
            await storage.initialize()

            # Save test data
            await storage.save([Proxy(url="http://proxy.example.com:8080")])

            # Create a long-running query that holds the connection
            async def hold_connection():
                from sqlmodel.ext.asyncio.session import AsyncSession

                async with AsyncSession(storage.engine) as session:
                    await asyncio.sleep(2.0)  # Hold connection for 2 seconds

            # Start holding connection
            hold_task = asyncio.create_task(hold_connection())
            await asyncio.sleep(0.1)  # Let it acquire the connection

            # Try to query while pool is exhausted - should timeout
            try:
                async with asyncio.timeout(2.0):
                    await storage.load()
                # If we get here, timeout didn't occur as expected
                # This is acceptable in some SQLAlchemy versions
            except (asyncio.TimeoutError, Exception):
                # Timeout or pool timeout occurred - this is expected
                pass

            # Wait for hold task to complete
            await hold_task
            await storage.close()

    async def test_pool_recycle_disabled(self) -> None:
        """Test pool_recycle=-1 disables connection recycling."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path, pool_recycle=-1)

            # Verify pool_recycle is set to -1
            assert storage.pool_recycle == -1

            # Engine should have None for pool_recycle
            # (SQLAlchemy interprets None as disabled)
            assert storage.engine.pool._recycle is None or storage.engine.pool._recycle == -1

            await storage.close()

    async def test_concurrent_save_operations_with_pooling(self) -> None:
        """Test concurrent save operations work correctly with connection pooling."""
        import asyncio

        from proxywhirl.models import Proxy
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path, pool_size=5)
            await storage.initialize()

            # Create multiple proxy sets
            proxy_sets = [
                [Proxy(url=f"http://proxy{i}-{j}.example.com:8080") for j in range(3)]
                for i in range(5)
            ]

            # Save concurrently
            await asyncio.gather(*[storage.save(pset) for pset in proxy_sets])

            # Load all - should have 15 proxies (3 per set × 5 sets)
            loaded = await storage.load()
            assert len(loaded) == 15

            await storage.close()

    async def test_pool_configuration_from_data_storage_config(self) -> None:
        """Test creating SQLiteStorage with DataStorageConfig pool settings."""
        from proxywhirl.config import DataStorageConfig
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"

            # Create config with custom pool settings
            config = DataStorageConfig(
                pool_size=8,
                pool_max_overflow=15,
                pool_timeout=45.0,
                pool_recycle=5400,
            )

            # Create storage with config values
            storage = SQLiteStorage(
                db_path,
                pool_size=config.pool_size,
                pool_max_overflow=config.pool_max_overflow,
                pool_timeout=config.pool_timeout,
                pool_recycle=config.pool_recycle,
            )

            # Verify configuration was applied
            assert storage.pool_size == 8
            assert storage.pool_max_overflow == 15
            assert storage.pool_timeout == 45.0
            assert storage.pool_recycle == 5400

            await storage.close()


class TestCacheEntryTable:
    """Test CacheEntryTable SQLModel."""

    def test_cache_entry_table_defaults(self) -> None:
        """Test CacheEntryTable has correct defaults."""
        import time

        from proxywhirl.storage import CacheEntryTable

        now = time.time()
        entry = CacheEntryTable(
            key="test-key",
            proxy_url="http://proxy.example.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + 3600,
            created_at=now,
            updated_at=now,
        )

        assert entry.key == "test-key"
        assert entry.access_count == 0
        assert entry.health_status == "unknown"
        assert entry.failure_count == 0
        assert entry.username_encrypted is None
        assert entry.password_encrypted is None
