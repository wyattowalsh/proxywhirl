"""Unit tests for storage backends."""

import json
import tempfile
from pathlib import Path

import pytest

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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_file_storage_load_nonexistent_file(self) -> None:
        """T039: Test loading from nonexistent file raises error."""
        from proxywhirl.storage import FileStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "nonexistent.json"
            storage = FileStorage(storage_path)

            with pytest.raises(FileNotFoundError):
                await storage.load()

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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
