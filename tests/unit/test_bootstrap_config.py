"""Unit tests for BootstrapConfig model and bootstrap helper functions.

Tests cover:
- BootstrapConfig model validation, defaults, and frozen behavior
- _sample_sources() random sampling logic
- _should_show_progress() TTY auto-detection
- Constructor acceptance in ProxyWhirl and AsyncProxyWhirl (including bool shortcut)
- enabled=False skips bootstrap entirely
- extra="forbid" rejects unknown fields
- max_proxies field acceptance and enforcement
- Context-aware error messages
- Logger.info always emitted
- Summary line includes validated count
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import BootstrapConfig, ProxySourceConfig
from proxywhirl.rotator._bootstrap import (
    _raise_bootstrap_empty_error,
    _sample_sources,
    _should_show_progress,
)
from proxywhirl.sources import ALL_SOURCES


class TestBootstrapConfigModel:
    """Test BootstrapConfig Pydantic model."""

    def test_defaults(self):
        """Test default values for BootstrapConfig."""
        config = BootstrapConfig()
        assert config.enabled is True
        assert config.sources is None
        assert config.sample_size == 10
        assert config.validate_proxies is True
        assert config.timeout == 10
        assert config.max_concurrent == 100
        assert config.show_progress is None
        assert config.max_proxies is None

    def test_frozen(self):
        """Test that BootstrapConfig is immutable (frozen)."""
        config = BootstrapConfig()
        with pytest.raises(ValidationError):
            config.enabled = False  # type: ignore[misc]

    def test_custom_values(self):
        """Test creating BootstrapConfig with custom values."""
        sources = [ProxySourceConfig(url="https://example.com/proxies.txt", format="plain_text")]
        config = BootstrapConfig(
            enabled=True,
            sources=sources,
            sample_size=5,
            validate_proxies=False,
            timeout=30,
            max_concurrent=50,
            show_progress=True,
        )
        assert config.sources == sources
        assert config.sample_size == 5
        assert config.validate_proxies is False
        assert config.timeout == 30
        assert config.max_concurrent == 50
        assert config.show_progress is True

    def test_disabled(self):
        """Test creating a disabled BootstrapConfig."""
        config = BootstrapConfig(enabled=False)
        assert config.enabled is False

    @pytest.mark.parametrize(
        "field,value",
        [
            ("sample_size", 0),
            ("timeout", 0),
            ("max_concurrent", 0),
        ],
    )
    def test_field_minimum_values(self, field: str, value: int):
        """Test that numeric fields enforce minimum >= 1."""
        with pytest.raises(ValidationError):
            BootstrapConfig(**{field: value})


class TestSampleSources:
    """Test _sample_sources() function."""

    def test_explicit_sources_returned_as_is(self):
        """When explicit sources are provided, return them unchanged."""
        sources = [
            ProxySourceConfig(url="https://example.com/a.txt", format="plain_text"),
            ProxySourceConfig(url="https://example.com/b.txt", format="plain_text"),
        ]
        result = _sample_sources(sources, sample_size=10)
        assert result == sources

    def test_none_sources_samples_from_all(self):
        """When sources is None, randomly sample from ALL_SOURCES."""
        result = _sample_sources(None, sample_size=5)
        assert len(result) == 5
        # All results should be from ALL_SOURCES
        all_urls = {str(s.url) for s in ALL_SOURCES}
        for s in result:
            assert str(s.url) in all_urls

    def test_sample_size_capped_at_available(self):
        """Sample size is capped at the number of enabled sources."""
        enabled_count = sum(1 for s in ALL_SOURCES if s.enabled)
        result = _sample_sources(None, sample_size=999)
        assert len(result) == enabled_count

    def test_randomness(self):
        """Multiple calls return different subsets (probabilistic test)."""
        results = [frozenset(str(s.url) for s in _sample_sources(None, 5)) for _ in range(10)]
        # With 10 attempts sampling 5 from 100+ sources, we expect at least 2 different sets
        unique_sets = set(results)
        assert len(unique_sets) >= 2

    def test_only_enabled_sources(self):
        """Only enabled sources are included in the sample."""
        result = _sample_sources(None, sample_size=5)
        for source in result:
            assert source.enabled is True


class TestShouldShowProgress:
    """Test _should_show_progress() function."""

    def test_explicit_true(self):
        """Explicit True is respected."""
        assert _should_show_progress(True) is True

    def test_explicit_false(self):
        """Explicit False is respected."""
        assert _should_show_progress(False) is False

    def test_none_auto_detects_tty(self):
        """None auto-detects TTY on stderr."""
        with patch("sys.stderr") as mock_stderr:
            mock_stderr.isatty.return_value = True
            assert _should_show_progress(None) is True

        with patch("sys.stderr") as mock_stderr:
            mock_stderr.isatty.return_value = False
            assert _should_show_progress(None) is False


class TestConstructorAcceptance:
    """Test that rotator constructors accept BootstrapConfig."""

    def test_sync_rotator_accepts_bootstrap(self):
        """ProxyWhirl accepts bootstrap parameter."""
        from proxywhirl import ProxyWhirl

        config = BootstrapConfig(enabled=False)
        rotator = ProxyWhirl(bootstrap=config)
        assert rotator._bootstrap_config is config

    def test_sync_rotator_default_bootstrap(self):
        """ProxyWhirl creates default BootstrapConfig when None."""
        from proxywhirl import ProxyWhirl

        rotator = ProxyWhirl()
        assert isinstance(rotator._bootstrap_config, BootstrapConfig)
        assert rotator._bootstrap_config.enabled is True

    def test_async_rotator_accepts_bootstrap(self):
        """AsyncProxyWhirl accepts bootstrap parameter."""
        from proxywhirl import AsyncProxyWhirl

        config = BootstrapConfig(enabled=False)
        rotator = AsyncProxyWhirl(bootstrap=config)
        assert rotator._bootstrap_config is config

    def test_async_rotator_default_bootstrap(self):
        """AsyncProxyWhirl creates default BootstrapConfig when None."""
        from proxywhirl import AsyncProxyWhirl

        rotator = AsyncProxyWhirl()
        assert isinstance(rotator._bootstrap_config, BootstrapConfig)
        assert rotator._bootstrap_config.enabled is True


class TestBootstrapDisabled:
    """Test that enabled=False skips bootstrap entirely."""

    def test_sync_bootstrap_disabled_returns_zero(self):
        """Sync bootstrap returns 0 when disabled."""
        from proxywhirl.models import ProxyPool
        from proxywhirl.rotator._bootstrap import bootstrap_pool_if_empty_sync

        pool = ProxyPool(name="test", proxies=[])
        config = BootstrapConfig(enabled=False)
        added = bootstrap_pool_if_empty_sync(
            pool=pool,
            add_proxy=lambda p: None,
            config=config,
        )
        assert added == 0

    @pytest.mark.asyncio
    async def test_async_bootstrap_disabled_returns_zero(self):
        """Async bootstrap returns 0 when disabled."""
        from proxywhirl.models import ProxyPool
        from proxywhirl.rotator._bootstrap import bootstrap_pool_if_empty_async

        pool = ProxyPool(name="test", proxies=[])
        config = BootstrapConfig(enabled=False)
        added = await bootstrap_pool_if_empty_async(
            pool=pool,
            add_proxy=lambda p: None,  # type: ignore[arg-type, return-value]
            config=config,
        )
        assert added == 0


class TestBootstrapBoolShortcut:
    """Test bootstrap=False / bootstrap=True shortcut in rotator constructors."""

    def test_sync_bootstrap_false(self):
        """ProxyWhirl(bootstrap=False) disables bootstrap."""
        from proxywhirl import ProxyWhirl

        rotator = ProxyWhirl(bootstrap=False)
        assert rotator._bootstrap_config.enabled is False

    def test_sync_bootstrap_true(self):
        """ProxyWhirl(bootstrap=True) uses default enabled config."""
        from proxywhirl import ProxyWhirl

        rotator = ProxyWhirl(bootstrap=True)
        assert rotator._bootstrap_config.enabled is True

    def test_async_bootstrap_false(self):
        """AsyncProxyWhirl(bootstrap=False) disables bootstrap."""
        from proxywhirl import AsyncProxyWhirl

        rotator = AsyncProxyWhirl(bootstrap=False)
        assert rotator._bootstrap_config.enabled is False

    def test_async_bootstrap_true(self):
        """AsyncProxyWhirl(bootstrap=True) uses default enabled config."""
        from proxywhirl import AsyncProxyWhirl

        rotator = AsyncProxyWhirl(bootstrap=True)
        assert rotator._bootstrap_config.enabled is True


class TestExtraForbid:
    """Test that BootstrapConfig rejects unknown fields."""

    def test_unknown_field_rejected(self):
        """Unknown fields raise ValidationError (extra='forbid')."""
        with pytest.raises(ValidationError):
            BootstrapConfig(unknown_field="oops")  # type: ignore[call-arg]


class TestMaxProxies:
    """Test max_proxies field on BootstrapConfig."""

    def test_max_proxies_accepted(self):
        """max_proxies=50 is accepted."""
        config = BootstrapConfig(max_proxies=50)
        assert config.max_proxies == 50

    def test_max_proxies_none_default(self):
        """max_proxies defaults to None (unlimited)."""
        config = BootstrapConfig()
        assert config.max_proxies is None

    def test_max_proxies_minimum(self):
        """max_proxies must be >= 1."""
        with pytest.raises(ValidationError):
            BootstrapConfig(max_proxies=0)


class TestContextAwareErrors:
    """Test _raise_bootstrap_empty_error produces context-aware messages."""

    def test_empty_explicit_sources(self):
        """Empty explicit sources produce helpful message about configuration."""
        with pytest.raises(ProxyPoolEmptyError, match="No proxy sources configured"):
            _raise_bootstrap_empty_error(sources_count=0, sources_were_explicit=True)

    def test_default_sources_failed(self):
        """Default sources failure produces message about availability."""
        with pytest.raises(ProxyPoolEmptyError, match="temporarily unavailable"):
            _raise_bootstrap_empty_error(sources_count=10, sources_were_explicit=False)

    def test_message_includes_source_count(self):
        """Error message includes the number of sources tried."""
        with pytest.raises(ProxyPoolEmptyError, match="from 15 sources"):
            _raise_bootstrap_empty_error(sources_count=15, sources_were_explicit=False)

    def test_disabled_bootstrap_error_sync(self):
        """Sync rotator produces actionable error when bootstrap disabled and pool empty."""
        from proxywhirl import ProxyWhirl

        rotator = ProxyWhirl(bootstrap=False)
        with pytest.raises(ProxyPoolEmptyError, match="auto-bootstrap is disabled"):
            rotator._ensure_bootstrap_for_empty_pool()

    @pytest.mark.asyncio
    async def test_disabled_bootstrap_error_async(self):
        """Async rotator produces actionable error when bootstrap disabled and pool empty."""
        from proxywhirl import AsyncProxyWhirl

        rotator = AsyncProxyWhirl(bootstrap=False)
        with pytest.raises(ProxyPoolEmptyError, match="auto-bootstrap is disabled"):
            await rotator._ensure_request_bootstrap()


class TestBootstrapSummaryAndLogging:
    """Test summary line and logger.info emission."""

    @pytest.mark.asyncio
    async def test_logger_info_always_emitted(self):
        """logger.info is always called after bootstrap, regardless of TTY."""
        from proxywhirl.rotator._bootstrap import _fetch_bootstrap_candidates

        config = BootstrapConfig(show_progress=False, validate_proxies=False)

        async def mock_fetch(**kwargs):
            return [{"url": "http://203.0.113.1:8080"}]

        with (
            patch(
                "proxywhirl.rotator._bootstrap.fetch_all_sources",
                new=mock_fetch,
            ),
            patch("proxywhirl.rotator._bootstrap.logger") as mock_logger,
        ):
            await _fetch_bootstrap_candidates(config=config)
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert "Bootstrap complete" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_summary_includes_validated_count(self):
        """Summary shows validated count when validation is enabled."""
        from proxywhirl.rotator._bootstrap import _fetch_bootstrap_candidates

        config = BootstrapConfig(show_progress=True, validate_proxies=True)

        async def mock_fetch(**kwargs):
            # Simulate callbacks
            fetch_cb = kwargs.get("fetch_progress_callback")
            validate_cb = kwargs.get("validate_progress_callback")
            if fetch_cb:
                fetch_cb(1, 1, 100)
            if validate_cb:
                validate_cb(50, 100, 50)
            return [{"url": "http://203.0.113.1:8080"}]

        mock_stderr = MagicMock()
        mock_stderr.isatty.return_value = True

        with (
            patch(
                "proxywhirl.rotator._bootstrap.fetch_all_sources",
                new=mock_fetch,
            ),
            patch("proxywhirl.rotator._bootstrap.sys.stderr", mock_stderr),
            patch("proxywhirl.rotator._bootstrap.logger"),
        ):
            await _fetch_bootstrap_candidates(config=config)
            # Check that stderr.write was called with validated count
            write_calls = [str(c) for c in mock_stderr.write.call_args_list]
            summary_text = "".join(write_calls)
            assert "fetched" in summary_text
            assert "validated" in summary_text
