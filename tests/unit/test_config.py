"""Unit tests for CLI configuration module.

Tests cover ProxyConfig, CLIConfig, and configuration file operations.
"""

import os
import stat
from pathlib import Path
from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet
from pydantic import SecretStr

from proxywhirl.config import (
    CLIConfig,
    ProxyConfig,
    decrypt_credentials,
    discover_config,
    encrypt_credentials,
    get_encryption_key,
    load_config,
    save_config,
)


class TestProxyConfig:
    """Test ProxyConfig validation."""

    def test_valid_http_url(self) -> None:
        """Test valid HTTP proxy URL."""
        config = ProxyConfig(url="http://proxy.example.com:8080")
        assert config.url == "http://proxy.example.com:8080"

    def test_valid_https_url(self) -> None:
        """Test valid HTTPS proxy URL."""
        config = ProxyConfig(url="https://secure-proxy.com:443")
        assert config.url == "https://secure-proxy.com:443"

    def test_valid_socks4_url(self) -> None:
        """Test valid SOCKS4 proxy URL."""
        config = ProxyConfig(url="socks4://socks.example.com:1080")
        assert config.url == "socks4://socks.example.com:1080"

    def test_valid_socks5_url(self) -> None:
        """Test valid SOCKS5 proxy URL."""
        config = ProxyConfig(url="socks5://socks.example.com:1080")
        assert config.url == "socks5://socks.example.com:1080"

    def test_invalid_url_scheme(self) -> None:
        """Test that invalid URL scheme raises ValueError."""
        with pytest.raises(ValueError, match="Invalid proxy URL scheme"):
            ProxyConfig(url="ftp://proxy.example.com:8080")

    def test_url_without_scheme(self) -> None:
        """Test that URL without scheme raises ValueError."""
        with pytest.raises(ValueError, match="Invalid proxy URL scheme"):
            ProxyConfig(url="proxy.example.com:8080")

    def test_with_credentials(self) -> None:
        """Test proxy with username and password."""
        config = ProxyConfig(
            url="http://proxy.example.com:8080",
            username=SecretStr("user"),
            password=SecretStr("pass"),
        )
        assert config.username.get_secret_value() == "user"
        assert config.password.get_secret_value() == "pass"


class TestCLIConfig:
    """Test CLIConfig validation."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = CLIConfig()
        assert config.rotation_strategy == "round-robin"
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.default_format == "text"
        assert config.color is True

    def test_valid_rotation_strategies(self) -> None:
        """Test all valid rotation strategies."""
        for strategy in ["round-robin", "random", "weighted", "least-used"]:
            config = CLIConfig(rotation_strategy=strategy)
            assert config.rotation_strategy == strategy

    def test_invalid_rotation_strategy(self) -> None:
        """Test that invalid rotation strategy raises ValueError."""
        with pytest.raises(ValueError, match="Invalid rotation strategy"):
            CLIConfig(rotation_strategy="invalid-strategy")

    def test_valid_output_formats(self) -> None:
        """Test all valid output formats."""
        for fmt in ["text", "json", "csv"]:
            config = CLIConfig(default_format=fmt)
            assert config.default_format == fmt

    def test_invalid_output_format(self) -> None:
        """Test that invalid output format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid output format"):
            CLIConfig(default_format="xml")

    def test_deprecated_format_aliases(self) -> None:
        """Test that deprecated format names are accepted with alias mapping."""
        config_human = CLIConfig(default_format="human")
        assert config_human.default_format == "text"

        config_table = CLIConfig(default_format="table")
        assert config_table.default_format == "text"

    def test_config_init_defaults(self) -> None:
        """Test that CLIConfig(encrypt_credentials=False) produces valid defaults.

        Regression test for config init bug where hardcoded values
        disagreed with field defaults/validators.
        """
        config = CLIConfig(encrypt_credentials=False)
        assert config.rotation_strategy == "round-robin"
        assert config.default_format == "text"
        assert config.storage_backend == "file"
        assert config.encrypt_credentials is False
        assert config.timeout == 30
        assert config.max_retries == 3

    def test_invalid_storage_backend(self) -> None:
        """Test that invalid storage_backend is rejected."""
        with pytest.raises(ValueError):
            CLIConfig(storage_backend="redis")


class TestDiscoverConfig:
    """Test configuration file discovery."""

    def test_explicit_path_exists(self, tmp_path: Path) -> None:
        """Test discovery with explicit path that exists."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("[tool.proxywhirl]\ntimeout = 60\n")

        result = discover_config(explicit_path=config_file)
        assert result == config_file

    def test_explicit_path_not_exists(self, tmp_path: Path) -> None:
        """Test discovery with explicit path that doesn't exist."""
        missing_file = tmp_path / "missing.toml"

        with pytest.raises(FileNotFoundError, match="Config file not found"):
            discover_config(explicit_path=missing_file)

    def test_no_config_found(self, tmp_path: Path, monkeypatch) -> None:
        """Test discovery when no config file exists."""
        monkeypatch.chdir(tmp_path)

        with patch("proxywhirl.config.user_config_dir", return_value=str(tmp_path / "config")):
            result = discover_config()
            assert result is None

    def test_project_local_pyproject(self, tmp_path: Path, monkeypatch) -> None:
        """Test discovery finds pyproject.toml with proxywhirl section."""
        monkeypatch.chdir(tmp_path)
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.proxywhirl]\ntimeout = 45\n")

        result = discover_config()
        assert result == pyproject

    def test_project_local_pyproject_no_section(self, tmp_path: Path, monkeypatch) -> None:
        """Test discovery skips pyproject.toml without proxywhirl section."""
        monkeypatch.chdir(tmp_path)
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[tool.other]\nkey = "value"\n')

        with patch("proxywhirl.config.user_config_dir", return_value=str(tmp_path / "config")):
            result = discover_config()
            assert result is None

    def test_user_global_config(self, tmp_path: Path, monkeypatch) -> None:
        """Test discovery finds user global config."""
        monkeypatch.chdir(tmp_path)
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        user_config = config_dir / "config.toml"
        user_config.write_text("timeout = 30\n")

        with patch("proxywhirl.config.user_config_dir", return_value=str(config_dir)):
            result = discover_config()
            assert result == user_config


class TestLoadConfig:
    """Test configuration loading."""

    def test_load_defaults_when_path_none(self) -> None:
        """Test that defaults are returned when path is None."""
        config = load_config(None)
        assert config.timeout == 30
        assert config.rotation_strategy == "round-robin"

    def test_load_from_toml_file(self, tmp_path: Path) -> None:
        """Test loading from a TOML file."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            "timeout = 60\nrotation_strategy = 'random'\nencrypt_credentials = false\n"
        )

        config = load_config(config_file)
        assert config.timeout == 60
        assert config.rotation_strategy == "random"

    def test_load_from_pyproject_toml(self, tmp_path: Path) -> None:
        """Test loading from pyproject.toml with tool.proxywhirl section."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("[tool.proxywhirl]\ntimeout = 90\nencrypt_credentials = false\n")

        config = load_config(config_file)
        assert config.timeout == 90


class TestSaveConfig:
    """Test configuration saving."""

    def test_save_basic_config(self, tmp_path: Path) -> None:
        """Test saving basic configuration."""
        config_file = tmp_path / "config.toml"
        config = CLIConfig(timeout=45, encrypt_credentials=False)

        save_config(config, config_file)

        assert config_file.exists()
        content = config_file.read_text()
        assert "timeout = 45" in content

    def test_save_to_pyproject_toml(self, tmp_path: Path) -> None:
        """Test saving to pyproject.toml wraps in tool.proxywhirl."""
        pyproject = tmp_path / "pyproject.toml"
        config = CLIConfig(timeout=55, encrypt_credentials=False)

        save_config(config, pyproject)

        assert pyproject.exists()
        content = pyproject.read_text()
        assert "[tool.proxywhirl]" in content
        assert "timeout = 55" in content

    def test_save_merges_with_existing_pyproject(self, tmp_path: Path) -> None:
        """Test saving merges with existing pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[tool.other]\nkey = "value"\n')

        config = CLIConfig(timeout=60, encrypt_credentials=False)
        save_config(config, pyproject)

        content = pyproject.read_text()
        assert "[tool.other]" in content
        assert "[tool.proxywhirl]" in content

    def test_save_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test saving creates parent directories if needed."""
        nested_path = tmp_path / "nested" / "dir" / "config.toml"
        config = CLIConfig(encrypt_credentials=False)

        save_config(config, nested_path)

        assert nested_path.exists()


class TestEncryptionKey:
    """Test encryption key management."""

    def test_get_key_from_environment(self) -> None:
        """Test getting encryption key from environment."""
        test_key = Fernet.generate_key().decode()
        config = CLIConfig(encryption_key_env="TEST_PROXY_KEY")

        with patch.dict(os.environ, {"TEST_PROXY_KEY": test_key}):
            key = get_encryption_key(config)
            assert key == test_key.encode()

    def test_generate_and_persist_key_when_missing(self, tmp_path: Path) -> None:
        """Test generating and persisting new key when not in environment."""
        config = CLIConfig(encryption_key_env="MISSING_KEY_12345")

        with patch.dict(os.environ, {}, clear=False):
            # Ensure the key doesn't exist
            if "MISSING_KEY_12345" in os.environ:
                del os.environ["MISSING_KEY_12345"]

            # Mock Path.home() to use tmp_path
            with patch("proxywhirl.config.Path.home", return_value=tmp_path):
                key = get_encryption_key(config)

        # Should return a valid Fernet key
        assert len(key) == 44  # Fernet keys are 44 bytes when base64 encoded

        # Key should be persisted to file
        expected_key_file = tmp_path / ".config" / "proxywhirl" / "key.enc"
        assert expected_key_file.exists()
        assert expected_key_file.read_bytes() == key

        # File should have proper permissions (owner read/write only)
        file_mode = expected_key_file.stat().st_mode
        assert stat.S_IMODE(file_mode) == 0o600

    def test_load_persisted_key(self, tmp_path: Path) -> None:
        """Test loading a previously persisted key."""
        config = CLIConfig(encryption_key_env="MISSING_KEY_67890")
        test_key = Fernet.generate_key()

        # Create a persisted key file
        key_file = tmp_path / ".config" / "proxywhirl" / "key.enc"
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key_file.write_bytes(test_key)

        with patch.dict(os.environ, {}, clear=False):
            # Ensure the key doesn't exist in environment
            if "MISSING_KEY_67890" in os.environ:
                del os.environ["MISSING_KEY_67890"]

            # Mock Path.home() to use tmp_path
            with patch("proxywhirl.config.Path.home", return_value=tmp_path):
                key = get_encryption_key(config)

        # Should return the persisted key
        assert key == test_key

    def test_environment_takes_precedence_over_file(self, tmp_path: Path) -> None:
        """Test that environment variable takes precedence over persisted file."""
        env_key = Fernet.generate_key().decode()
        file_key = Fernet.generate_key()
        config = CLIConfig(encryption_key_env="ENV_PRECEDENCE_KEY")

        # Create a persisted key file
        key_file = tmp_path / ".config" / "proxywhirl" / "key.enc"
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key_file.write_bytes(file_key)

        with (
            patch.dict(os.environ, {"ENV_PRECEDENCE_KEY": env_key}),
            patch("proxywhirl.config.Path.home", return_value=tmp_path),
        ):
            key = get_encryption_key(config)

        # Should return the environment key, not the file key
        assert key == env_key.encode()
        assert key != file_key


class TestCredentialEncryption:
    """Test credential encryption and decryption."""

    def test_encrypt_no_proxies(self) -> None:
        """Test encryption with no proxies does nothing."""
        config = CLIConfig()
        result = encrypt_credentials(config)
        assert result.proxies == []

    def test_decrypt_no_proxies(self) -> None:
        """Test decryption with no proxies does nothing."""
        config = CLIConfig()
        result = decrypt_credentials(config)
        assert result.proxies == []

    def test_encrypt_decrypt_roundtrip(self) -> None:
        """Test that encrypt then decrypt returns original values."""
        test_key = Fernet.generate_key().decode()
        config = CLIConfig(
            encryption_key_env="ROUNDTRIP_KEY",
            proxies=[
                ProxyConfig(
                    url="http://proxy.example.com:8080",
                    username=SecretStr("testuser"),
                    password=SecretStr("testpass"),
                )
            ],
        )

        with patch.dict(os.environ, {"ROUNDTRIP_KEY": test_key}):
            encrypted = encrypt_credentials(config)
            # Verify encrypted values are different
            assert encrypted.proxies[0].username.get_secret_value() != "testuser"
            assert encrypted.proxies[0].password.get_secret_value() != "testpass"

            decrypted = decrypt_credentials(encrypted)
            # Verify decrypted values match original
            assert decrypted.proxies[0].username.get_secret_value() == "testuser"
            assert decrypted.proxies[0].password.get_secret_value() == "testpass"

    def test_decrypt_handles_unencrypted_values(self) -> None:
        """Test that decryption gracefully handles unencrypted values."""
        test_key = Fernet.generate_key().decode()
        config = CLIConfig(
            encryption_key_env="DECRYPT_KEY",
            proxies=[
                ProxyConfig(
                    url="http://proxy.example.com:8080",
                    username=SecretStr("plainuser"),  # Not encrypted
                    password=SecretStr("plainpass"),  # Not encrypted
                )
            ],
        )

        with patch.dict(os.environ, {"DECRYPT_KEY": test_key}):
            # Should not raise, should return values as-is
            decrypted = decrypt_credentials(config)
            assert decrypted.proxies[0].username.get_secret_value() == "plainuser"
            assert decrypted.proxies[0].password.get_secret_value() == "plainpass"

    def test_decrypt_with_wrong_key(self) -> None:
        """Test that decryption gracefully handles wrong encryption key."""
        encrypt_key = Fernet.generate_key().decode()
        decrypt_key = Fernet.generate_key().decode()  # Different key
        config = CLIConfig(
            encryption_key_env="ENCRYPT_KEY",
            proxies=[
                ProxyConfig(
                    url="http://proxy.example.com:8080",
                    username=SecretStr("testuser"),
                    password=SecretStr("testpass"),
                )
            ],
        )

        # Encrypt with one key
        with patch.dict(os.environ, {"ENCRYPT_KEY": encrypt_key}):
            encrypted = encrypt_credentials(config)
            encrypted_username = encrypted.proxies[0].username.get_secret_value()
            encrypted_password = encrypted.proxies[0].password.get_secret_value()

        # Try to decrypt with a different key
        with patch.dict(os.environ, {"ENCRYPT_KEY": decrypt_key}):
            decrypted = decrypt_credentials(encrypted)
            # Should not raise, should keep encrypted values as-is
            assert decrypted.proxies[0].username.get_secret_value() == encrypted_username
            assert decrypted.proxies[0].password.get_secret_value() == encrypted_password

    def test_encrypt_without_credentials(self) -> None:
        """Test encryption with proxy that has no credentials."""
        test_key = Fernet.generate_key().decode()
        config = CLIConfig(
            encryption_key_env="ENCRYPT_KEY",
            proxies=[
                ProxyConfig(url="http://proxy.example.com:8080")  # No username/password
            ],
        )

        with patch.dict(os.environ, {"ENCRYPT_KEY": test_key}):
            encrypted = encrypt_credentials(config)
            assert encrypted.proxies[0].username is None
            assert encrypted.proxies[0].password is None


class TestKeyPersistence:
    """Test encryption key persistence edge cases."""

    def test_key_file_created_with_correct_permissions(self, tmp_path: Path) -> None:
        """Test that key file is created with 0600 permissions."""
        config = CLIConfig(encryption_key_env="PERM_TEST_KEY")

        with patch.dict(os.environ, {}, clear=False):
            if "PERM_TEST_KEY" in os.environ:
                del os.environ["PERM_TEST_KEY"]

            with patch("proxywhirl.config.Path.home", return_value=tmp_path):
                get_encryption_key(config)

        key_file = tmp_path / ".config" / "proxywhirl" / "key.enc"
        assert key_file.exists()

        file_mode = key_file.stat().st_mode
        assert stat.S_IMODE(file_mode) == 0o600

    def test_key_file_read_failure_fallback(self, tmp_path: Path) -> None:
        """Test fallback when key file exists but cannot be read."""
        config = CLIConfig(encryption_key_env="READ_FAIL_KEY")
        key_file = tmp_path / ".config" / "proxywhirl" / "key.enc"
        key_file.parent.mkdir(parents=True, exist_ok=True)

        # Create a key file with content
        original_key = Fernet.generate_key()
        key_file.write_bytes(original_key)

        with patch.dict(os.environ, {}, clear=False):
            if "READ_FAIL_KEY" in os.environ:
                del os.environ["READ_FAIL_KEY"]

            # Mock read_bytes to raise an exception
            with (
                patch("proxywhirl.config.Path.home", return_value=tmp_path),
                patch.object(Path, "read_bytes", side_effect=PermissionError("Cannot read")),
            ):
                key = get_encryption_key(config)

        # Should generate a new key since reading failed
        assert key != original_key
        assert len(key) == 44

    def test_key_file_write_failure_warning(self, tmp_path: Path) -> None:
        """Test warning logged when key cannot be persisted."""
        config = CLIConfig(encryption_key_env="WRITE_FAIL_KEY")

        with patch.dict(os.environ, {}, clear=False):
            if "WRITE_FAIL_KEY" in os.environ:
                del os.environ["WRITE_FAIL_KEY"]

            # Mock write_bytes to raise an exception
            with (
                patch("proxywhirl.config.Path.home", return_value=tmp_path),
                patch.object(Path, "write_bytes", side_effect=PermissionError("Cannot write")),
            ):
                key = get_encryption_key(config)

        # Should still return a key even though it couldn't be persisted
        assert len(key) == 44


class TestAtomicWrites:
    """Test atomic configuration file writes."""

    def test_save_creates_parent_dirs_atomically(self, tmp_path: Path) -> None:
        """Test that parent directories are created before writing."""
        nested_path = tmp_path / "a" / "b" / "c" / "config.toml"
        config = CLIConfig(timeout=100, encrypt_credentials=False)

        save_config(config, nested_path)

        assert nested_path.parent.exists()
        assert nested_path.exists()
        assert nested_path.read_text().count("timeout = 100") == 1

    def test_save_sets_file_permissions(self, tmp_path: Path) -> None:
        """Test that saved config file has 0600 permissions."""
        config_file = tmp_path / "config.toml"
        config = CLIConfig(timeout=45, encrypt_credentials=False)

        save_config(config, config_file)

        file_mode = config_file.stat().st_mode
        assert stat.S_IMODE(file_mode) == 0o600

    def test_atomic_write_no_temp_files_left_behind(self, tmp_path: Path) -> None:
        """Test that atomic writes don't leave temporary files behind."""
        config_file = tmp_path / "config.toml"
        config = CLIConfig(timeout=45, encrypt_credentials=False)

        save_config(config, config_file)

        # Check that no .tmp.* files remain
        temp_files = list(tmp_path.glob("*.tmp.*"))
        assert len(temp_files) == 0

    def test_atomic_write_preserves_existing_file_on_error(self, tmp_path: Path) -> None:
        """Test that write errors don't corrupt existing file."""
        config_file = tmp_path / "config.toml"

        # Create existing valid config
        original_config = CLIConfig(timeout=30, encrypt_credentials=False)
        save_config(original_config, config_file)
        original_content = config_file.read_text()

        # Try to save with a mocked write failure
        from unittest.mock import MagicMock, patch

        new_config = CLIConfig(timeout=99, encrypt_credentials=False)

        # Mock open to fail during write
        mock_open = MagicMock(side_effect=OSError("Simulated write error"))

        with (
            patch("builtins.open", mock_open),
            pytest.raises(OSError),
        ):
            save_config(new_config, config_file)

        # Original file should still have original content
        # (atomic_write cleans up temp file on error)
        assert config_file.exists()
        assert config_file.read_text() == original_content

    def test_atomic_write_fsync_called(self, tmp_path: Path) -> None:
        """Test that fsync is called to ensure data is on disk."""
        from unittest.mock import patch

        config_file = tmp_path / "config.toml"
        config = CLIConfig(timeout=45, encrypt_credentials=False)

        # Mock os.fsync to verify it's called
        with patch("os.fsync") as mock_fsync:
            save_config(config, config_file)
            # fsync should be called at least once (in atomic_write)
            assert mock_fsync.call_count >= 1

        # File should still be written correctly
        assert config_file.exists()
        loaded = load_config(config_file)
        assert loaded.timeout == 45


class TestInvalidConfigFiles:
    """Test handling of malformed TOML files."""

    def test_load_invalid_toml(self, tmp_path: Path) -> None:
        """Test that loading invalid TOML raises appropriate error."""
        config_file = tmp_path / "invalid.toml"
        config_file.write_text("this is not valid TOML ][[[")

        with pytest.raises(Exception):  # tomllib.TOMLDecodeError or similar
            load_config(config_file)

    def test_load_empty_file(self, tmp_path: Path) -> None:
        """Test loading an empty TOML file."""
        config_file = tmp_path / "empty.toml"
        config_file.write_text("")

        # Should load with defaults
        config = load_config(config_file)
        assert config.timeout == 30
        assert config.rotation_strategy == "round-robin"

    def test_load_with_invalid_field_types(self, tmp_path: Path) -> None:
        """Test loading config with invalid field types."""
        config_file = tmp_path / "invalid_types.toml"
        config_file.write_text('timeout = "not_a_number"\n')

        with pytest.raises(Exception):  # Pydantic validation error
            load_config(config_file)

    def test_load_with_extra_unknown_fields(self, tmp_path: Path) -> None:
        """Test loading config with unknown fields (should be ignored)."""
        config_file = tmp_path / "extra_fields.toml"
        config_file.write_text(
            "timeout = 60\nunknown_field = 'ignored'\nencrypt_credentials = false\n"
        )

        # Should load successfully, ignoring unknown fields
        config = load_config(config_file)
        assert config.timeout == 60


class TestDataStorageConfig:
    """Test DataStorageConfig persistence toggles."""

    def test_default_data_storage_config(self) -> None:
        """Test default values for data storage configuration."""
        config = CLIConfig()
        ds = config.data_storage

        # Storage backend - async by default
        assert ds.async_driver is True

        # Request timing - enabled by default
        assert ds.persist_latency_percentiles is True
        assert ds.persist_response_time_stats is True

        # Error tracking - enabled by default
        assert ds.persist_error_types is True
        assert ds.persist_error_messages is True
        assert ds.max_error_history == 20

        # Geographic - disabled by default (privacy)
        assert ds.persist_geo_data is False
        assert ds.persist_ip_intelligence is False
        assert ds.persist_coordinates is False

        # Protocol - enabled by default
        assert ds.persist_protocol_details is True
        assert ds.persist_capabilities is True

        # Health - enabled by default
        assert ds.persist_health_transitions is True
        assert ds.persist_consecutive_streaks is True
        assert ds.max_health_transitions == 50

        # Source - enabled by default
        assert ds.persist_source_metadata is True
        assert ds.persist_fetch_duration is True

        # Advanced - disabled by default (expensive)
        assert ds.persist_request_logs is False
        assert ds.persist_daily_aggregates is False

    def test_data_storage_config_customization(self, tmp_path: Path) -> None:
        """Test customizing data storage settings via TOML."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """encrypt_credentials = false

[data_storage]
persist_geo_data = true
persist_ip_intelligence = true
persist_coordinates = true
persist_request_logs = true
max_error_history = 50
"""
        )

        config = load_config(config_file)
        ds = config.data_storage

        assert ds.persist_geo_data is True
        assert ds.persist_ip_intelligence is True
        assert ds.persist_coordinates is True
        assert ds.persist_request_logs is True
        assert ds.max_error_history == 50

    def test_data_storage_config_validation_error_history(self) -> None:
        """Test that max_error_history is constrained to 0-100."""
        from proxywhirl.config import DataStorageConfig

        # Valid values
        config = DataStorageConfig(max_error_history=0)
        assert config.max_error_history == 0

        config = DataStorageConfig(max_error_history=100)
        assert config.max_error_history == 100

        # Invalid values
        with pytest.raises(Exception):  # Pydantic validation error
            DataStorageConfig(max_error_history=101)

        with pytest.raises(Exception):  # Pydantic validation error
            DataStorageConfig(max_error_history=-1)

    def test_data_storage_config_validation_health_transitions(self) -> None:
        """Test that max_health_transitions is constrained to 0-500."""
        from proxywhirl.config import DataStorageConfig

        # Valid values
        config = DataStorageConfig(max_health_transitions=0)
        assert config.max_health_transitions == 0

        config = DataStorageConfig(max_health_transitions=500)
        assert config.max_health_transitions == 500

        # Invalid values
        with pytest.raises(Exception):  # Pydantic validation error
            DataStorageConfig(max_health_transitions=501)

        with pytest.raises(Exception):  # Pydantic validation error
            DataStorageConfig(max_health_transitions=-1)

    def test_data_storage_config_forbids_extra_fields(self) -> None:
        """Test that DataStorageConfig forbids extra fields."""
        from proxywhirl.config import DataStorageConfig

        with pytest.raises(Exception):  # Pydantic validation error
            DataStorageConfig(unknown_field=True)

    def test_save_and_load_data_storage_config(self, tmp_path: Path) -> None:
        """Test round-trip save/load of DataStorageConfig."""
        from proxywhirl.config import DataStorageConfig

        config_file = tmp_path / "config.toml"
        ds_config = DataStorageConfig(
            persist_geo_data=True,
            persist_coordinates=True,
            max_error_history=30,
            max_health_transitions=100,
        )
        config = CLIConfig(
            data_storage=ds_config,
            encrypt_credentials=False,
            timeout=120,
        )

        save_config(config, config_file)

        # Load it back
        loaded = load_config(config_file)

        assert loaded.data_storage.persist_geo_data is True
        assert loaded.data_storage.persist_coordinates is True
        assert loaded.data_storage.max_error_history == 30
        assert loaded.data_storage.max_health_transitions == 100
        assert loaded.timeout == 120

    def test_async_driver_config_enabled(self) -> None:
        """Test async_driver configuration when enabled (default)."""
        from proxywhirl.config import DataStorageConfig

        config = DataStorageConfig(async_driver=True)
        assert config.async_driver is True

    def test_async_driver_config_disabled(self) -> None:
        """Test async_driver configuration when disabled."""
        from proxywhirl.config import DataStorageConfig

        config = DataStorageConfig(async_driver=False)
        assert config.async_driver is False

    def test_async_driver_config_via_toml(self, tmp_path: Path) -> None:
        """Test configuring async_driver via TOML file."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """encrypt_credentials = false

[data_storage]
async_driver = false
persist_geo_data = true
"""
        )

        config = load_config(config_file)
        assert config.data_storage.async_driver is False
        assert config.data_storage.persist_geo_data is True

    def test_async_driver_save_and_load(self, tmp_path: Path) -> None:
        """Test round-trip save/load of async_driver setting."""
        from proxywhirl.config import DataStorageConfig

        config_file = tmp_path / "config.toml"
        ds_config = DataStorageConfig(async_driver=False)
        config = CLIConfig(data_storage=ds_config, encrypt_credentials=False)

        save_config(config, config_file)
        loaded = load_config(config_file)

        assert loaded.data_storage.async_driver is False


class TestConfigFilePermissions:
    """Test handling of permission errors."""

    def test_load_config_permission_denied(self, tmp_path: Path) -> None:
        """Test loading config when file is not readable."""
        config_file = tmp_path / "unreadable.toml"
        config_file.write_text("timeout = 60\n")
        config_file.chmod(0o000)  # No permissions

        try:
            with pytest.raises(PermissionError):
                load_config(config_file)
        finally:
            # Restore permissions for cleanup
            config_file.chmod(0o600)

    def test_save_config_to_readonly_directory(self, tmp_path: Path) -> None:
        """Test saving config when directory is read-only."""
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only

        config_file = readonly_dir / "config.toml"
        config = CLIConfig(timeout=45, encrypt_credentials=False)

        try:
            with pytest.raises(PermissionError):
                save_config(config, config_file)
        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(0o755)


class TestCacheConfiguration:
    """Test cache-related configuration fields."""

    def test_cache_config_defaults(self) -> None:
        """Test default cache configuration values."""
        config = CLIConfig()
        assert config.cache_enabled is True
        assert config.cache_l1_max_entries == 1000
        assert config.cache_l2_max_entries == 5000
        assert config.cache_l3_max_entries is None
        assert config.cache_default_ttl == 3600
        assert config.cache_cleanup_interval == 60
        assert config.cache_l2_dir == ".cache/proxies"
        assert config.cache_l3_db_path == ".cache/db/proxywhirl.db"
        assert config.cache_encryption_key_env == "PROXYWHIRL_CACHE_ENCRYPTION_KEY"
        assert config.cache_health_invalidation is True
        assert config.cache_failure_threshold == 3

    def test_cache_ttl_validation(self) -> None:
        """Test that cache_default_ttl is constrained to minimum 60 seconds."""
        # Valid value
        config = CLIConfig(cache_default_ttl=60)
        assert config.cache_default_ttl == 60

        config = CLIConfig(cache_default_ttl=3600)
        assert config.cache_default_ttl == 3600

        # Invalid value
        with pytest.raises(Exception):  # Pydantic validation error
            CLIConfig(cache_default_ttl=30)

    def test_cache_cleanup_interval_validation(self) -> None:
        """Test that cache_cleanup_interval is constrained to minimum 10 seconds."""
        # Valid value
        config = CLIConfig(cache_cleanup_interval=10)
        assert config.cache_cleanup_interval == 10

        config = CLIConfig(cache_cleanup_interval=120)
        assert config.cache_cleanup_interval == 120

        # Invalid value
        with pytest.raises(Exception):  # Pydantic validation error
            CLIConfig(cache_cleanup_interval=5)

    def test_cache_failure_threshold_validation(self) -> None:
        """Test that cache_failure_threshold is constrained to minimum 1."""
        # Valid value
        config = CLIConfig(cache_failure_threshold=1)
        assert config.cache_failure_threshold == 1

        config = CLIConfig(cache_failure_threshold=10)
        assert config.cache_failure_threshold == 10

        # Invalid value
        with pytest.raises(Exception):  # Pydantic validation error
            CLIConfig(cache_failure_threshold=0)

    def test_save_and_load_cache_config(self, tmp_path: Path) -> None:
        """Test round-trip save/load of cache configuration."""
        config_file = tmp_path / "config.toml"
        config = CLIConfig(
            cache_enabled=False,
            cache_l1_max_entries=500,
            cache_default_ttl=7200,
            cache_cleanup_interval=30,
            encrypt_credentials=False,
        )

        save_config(config, config_file)

        loaded = load_config(config_file)
        assert loaded.cache_enabled is False
        assert loaded.cache_l1_max_entries == 500
        assert loaded.cache_default_ttl == 7200
        assert loaded.cache_cleanup_interval == 30
