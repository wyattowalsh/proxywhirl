"""
Pytest configuration and shared fixtures for ProxyWhirl tests.
"""

import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import httpx
import pytest

from proxywhirl.logging_config import (
    LogConfiguration,
    LogHandlerConfig,
    LogHandlerType,
    LogLevel,
)


@pytest.fixture
def sample_proxy_urls() -> list[str]:
    """Sample proxy URLs for testing."""
    return [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        "http://proxy3.example.com:8080",
    ]


@pytest.fixture
def sample_authenticated_proxy_urls() -> list[str]:
    """Sample authenticated proxy URLs for testing."""
    return [
        "http://user1:pass1@proxy1.example.com:8080",
        "http://user2:pass2@proxy2.example.com:8080",
    ]


@pytest.fixture
def mock_httpx_client() -> Generator[httpx.Client, None, None]:
    """Mock httpx client for testing."""
    client = httpx.Client()
    yield client
    client.close()


@pytest.fixture
def mock_async_httpx_client() -> Generator[httpx.AsyncClient, None, None]:
    """Mock async httpx client for testing."""
    client = httpx.AsyncClient()
    yield client
    # Note: In actual async tests, we'd use async context manager


# ============================================================================
# LOGGING FIXTURES (Feature 007: Structured Logging System)
# ============================================================================


@pytest.fixture
def temp_log_dir() -> Generator[Path, None, None]:
    """Create temporary directory for log files during tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        yield log_dir


@pytest.fixture
def temp_log_file(temp_log_dir: Path) -> Path:
    """Create temporary log file path."""
    return temp_log_dir / "test.log"


@pytest.fixture
def basic_log_config() -> LogConfiguration:
    """Basic logging configuration for testing."""
    return LogConfiguration(
        level=LogLevel.INFO,
        async_logging=False,  # Sync for simpler testing
        redact_credentials=True,
    )


@pytest.fixture
def console_handler_config() -> LogHandlerConfig:
    """Console handler configuration for testing."""
    return LogHandlerConfig(
        type=LogHandlerType.CONSOLE,
        level=LogLevel.INFO,
        format="json",
    )


@pytest.fixture
def file_handler_config(temp_log_file: Path) -> LogHandlerConfig:
    """File handler configuration for testing."""
    return LogHandlerConfig(
        type=LogHandlerType.FILE,
        path=str(temp_log_file),
        level=LogLevel.DEBUG,
        format="json",
        rotation="1 MB",
        retention="3 days",
    )


@pytest.fixture
def multi_handler_log_config(
    temp_log_file: Path,
) -> LogConfiguration:
    """Logging configuration with multiple handlers for testing."""
    return LogConfiguration(
        level=LogLevel.DEBUG,
        async_logging=False,
        handlers=[
            LogHandlerConfig(
                type=LogHandlerType.CONSOLE,
                level=LogLevel.WARNING,
                format="default",
            ),
            LogHandlerConfig(
                type=LogHandlerType.FILE,
                path=str(temp_log_file),
                level=LogLevel.DEBUG,
                format="json",
            ),
        ],
    )


@pytest.fixture
def captured_logs() -> list[dict[str, Any]]:
    """Fixture to capture structured log entries during tests."""
    return []


@pytest.fixture
def mock_log_sink(captured_logs: list[dict[str, Any]]) -> Generator[Any, None, None]:
    """Mock log sink that captures log entries for verification."""
    
    def sink(message: Any) -> None:
        """Capture log message."""
        if hasattr(message, "record"):
            captured_logs.append(message.record)
    
    yield sink


pytest_plugins = ["pytest_asyncio"]
