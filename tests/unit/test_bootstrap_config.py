"""Unit tests for BootstrapConfig model and bootstrap helper functions.

Tests cover:
- BootstrapConfig model validation, defaults, and frozen behavior
- _sample_sources() source selection logic
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

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import BootstrapConfig, Proxy, ProxyPool, ProxySourceConfig
from proxywhirl.rotator._bootstrap import (
    _coerce_proxy,
    _fetch_bootstrap_candidates,
    _raise_bootstrap_empty_error,
    _run_async_from_sync,
    _sample_sources,
    _should_show_progress,
    bootstrap_pool_if_empty_async,
    bootstrap_pool_if_empty_sync,
)
from proxywhirl.sources import ALL_SOURCES


class TestBootstrapConfigModel:
    """Test BootstrapConfig Pydantic model."""

    def test_defaults(self):
        """Test default values for BootstrapConfig."""
        config = BootstrapConfig()
        assert config.enabled is True
        assert config.sources is None
        assert config.sample_size is None
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

    def test_none_sources_returns_all_enabled_sources_by_default(self):
        """When sources and sample_size are None, return all enabled built-in sources."""
        result = _sample_sources(None, sample_size=None)
        enabled_count = sum(1 for s in ALL_SOURCES if s.enabled)
        assert len(result) == enabled_count
        all_urls = {str(s.url) for s in ALL_SOURCES}
        for s in result:
            assert str(s.url) in all_urls

    def test_sample_size_opt_in_samples_from_all(self):
        """When sample_size is set, randomly sample from ALL_SOURCES."""
        result = _sample_sources(None, sample_size=5)
        assert len(result) == 5
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

    @pytest.mark.asyncio
    async def test_summary_without_validated_count(self):
        """Summary omits validated count when validation is disabled."""
        config = BootstrapConfig(show_progress=True, validate_proxies=False)

        async def mock_fetch(**kwargs):
            return [{"url": "http://45.33.32.156:8080"}]

        mock_stderr = MagicMock()
        mock_stderr.isatty.return_value = True

        with (
            patch("proxywhirl.rotator._bootstrap.fetch_all_sources", new=mock_fetch),
            patch("proxywhirl.rotator._bootstrap.sys.stderr", mock_stderr),
            patch("proxywhirl.rotator._bootstrap.logger"),
        ):
            await _fetch_bootstrap_candidates(config=config)
            write_calls = [str(c) for c in mock_stderr.write.call_args_list]
            summary_text = "".join(write_calls)
            assert "validated" not in summary_text
            assert "Ready: 1 proxies from" in summary_text

    @pytest.mark.asyncio
    async def test_stderr_write_oserror_is_swallowed(self):
        """A broken stderr (e.g. closed pipe) should not crash bootstrap."""
        config = BootstrapConfig(show_progress=True, validate_proxies=False)

        async def mock_fetch(**kwargs):
            return [{"url": "http://45.33.32.156:8080"}]

        mock_stderr = MagicMock()
        mock_stderr.isatty.return_value = True
        mock_stderr.write.side_effect = OSError("broken pipe")

        with (
            patch("proxywhirl.rotator._bootstrap.fetch_all_sources", new=mock_fetch),
            patch("proxywhirl.rotator._bootstrap.sys.stderr", mock_stderr),
            patch("proxywhirl.rotator._bootstrap.logger") as mock_logger,
        ):
            candidates, count = await _fetch_bootstrap_candidates(config=config)
            assert len(candidates) == 1
            mock_logger.info.assert_called_once()


class TestCoerceProxy:
    """Test _coerce_proxy() edge cases."""

    def test_missing_url_returns_none(self):
        """A payload without a 'url' key returns None."""
        assert _coerce_proxy({}) is None

    def test_non_string_url_returns_none(self):
        """A non-string 'url' value returns None."""
        assert _coerce_proxy({"url": 12345}) is None

    def test_empty_string_url_returns_none(self):
        """An empty string 'url' returns None."""
        assert _coerce_proxy({"url": ""}) is None

    def test_invalid_url_format_returns_none(self):
        """A malformed proxy URL that fails validation returns None."""
        assert _coerce_proxy({"url": "not-a-valid-proxy-url"}) is None

    def test_valid_url_returns_proxy(self):
        """A well-formed proxy URL returns a Proxy instance."""
        result = _coerce_proxy({"url": "http://45.33.32.156:8080"})
        assert isinstance(result, Proxy)


class TestSampleSourcesAllDisabled:
    """Test _sample_sources() when no built-in sources are enabled."""

    def test_returns_empty_list_when_none_enabled(self):
        """No enabled sources yields an empty list rather than raising."""
        with patch("proxywhirl.rotator._bootstrap.ALL_SOURCES", []):
            result = _sample_sources(None, sample_size=None)
            assert result == []


class TestFetchBootstrapCandidatesNoSources:
    """Test _fetch_bootstrap_candidates() when source selection is empty."""

    @pytest.mark.asyncio
    async def test_empty_explicit_sources_short_circuits(self):
        """An explicit empty source list returns immediately without fetching."""
        config = BootstrapConfig(sources=[], validate_proxies=False, show_progress=False)

        with patch("proxywhirl.rotator._bootstrap.fetch_all_sources") as mock_fetch:
            candidates, count = await _fetch_bootstrap_candidates(config=config)
            assert candidates == []
            assert count == 0
            mock_fetch.assert_not_called()


class TestShowProgressImportError:
    """Test graceful degradation when the optional `rich` dependency is unavailable."""

    @pytest.mark.asyncio
    async def test_missing_rich_disables_progress_bars(self):
        """ImportError while importing rich should not crash bootstrap fetch."""
        config = BootstrapConfig(show_progress=True, validate_proxies=False)

        async def mock_fetch(**kwargs):
            return [{"url": "http://45.33.32.156:8080"}]

        mock_stderr = MagicMock()
        mock_stderr.isatty.return_value = True

        with (
            patch.dict("sys.modules", {"rich.console": None, "rich.progress": None}),
            patch("proxywhirl.rotator._bootstrap.fetch_all_sources", new=mock_fetch),
            patch("proxywhirl.rotator._bootstrap.sys.stderr", mock_stderr),
            patch("proxywhirl.rotator._bootstrap.logger"),
        ):
            candidates, _count = await _fetch_bootstrap_candidates(config=config)
            assert len(candidates) == 1


class TestRunAsyncFromSync:
    """Test _run_async_from_sync() bridging behavior."""

    def test_no_running_loop_uses_asyncio_run(self):
        """When no event loop is running, asyncio.run() is used directly."""

        async def factory():
            return 42

        assert _run_async_from_sync(factory) == 42

    def test_running_loop_uses_worker_thread_sync_call_site(self):
        """Direct call from a coroutine on a running loop delegates to a worker thread."""
        loop = asyncio.new_event_loop()

        async def factory():
            return "from-thread"

        async def runner():
            # Invoking the sync bridge from inside a running coroutine means
            # asyncio.get_running_loop() succeeds, forcing the worker-thread branch.
            return _run_async_from_sync(factory)

        try:
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(runner())
            assert result == "from-thread"
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    def test_running_loop_propagates_exceptions_sync_call_site(self):
        """Exceptions raised in the worker thread propagate to the caller."""
        loop = asyncio.new_event_loop()

        async def factory():
            raise ValueError("boom")

        try:
            asyncio.set_event_loop(loop)

            async def runner():
                return _run_async_from_sync(factory)

            with pytest.raises(ValueError, match="boom"):
                loop.run_until_complete(runner())
        finally:
            loop.close()
            asyncio.set_event_loop(None)


class TestBootstrapPoolPartialFailures:
    """Test bootstrap_pool_if_empty_{async,sync}() partial add_proxy failures."""

    @pytest.mark.asyncio
    async def test_async_skips_failed_proxies_but_returns_added_count(self):
        """Proxies that fail add_proxy are skipped; successful ones are counted."""
        pool = ProxyPool(name="test", proxies=[])
        added_proxies: list[Proxy] = []
        call_count = 0

        async def flaky_add_proxy(proxy: Proxy) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("simulated failure")
            added_proxies.append(proxy)

        async def mock_fetch(**kwargs):
            return [
                {"url": "http://45.33.32.156:8080"},
                {"url": "http://45.33.32.157:8080"},
            ]

        with patch("proxywhirl.rotator._bootstrap.fetch_all_sources", new=mock_fetch):
            added = await bootstrap_pool_if_empty_async(
                pool=pool,
                add_proxy=flaky_add_proxy,
                validate=False,
                sources=[ProxySourceConfig(url="https://example.com/a.txt", format="plain_text")],
            )
        assert added == 1

    @pytest.mark.asyncio
    async def test_async_raises_when_all_adds_fail(self):
        """All add_proxy failures should raise ProxyPoolEmptyError."""
        pool = ProxyPool(name="test", proxies=[])

        async def always_fail_add_proxy(proxy: Proxy) -> None:
            raise RuntimeError("simulated failure")

        async def mock_fetch(**kwargs):
            return [{"url": "http://45.33.32.156:8080"}]

        with patch("proxywhirl.rotator._bootstrap.fetch_all_sources", new=mock_fetch):
            with pytest.raises(ProxyPoolEmptyError):
                await bootstrap_pool_if_empty_async(
                    pool=pool,
                    add_proxy=always_fail_add_proxy,
                    validate=False,
                    sources=[
                        ProxySourceConfig(url="https://example.com/a.txt", format="plain_text")
                    ],
                )

    def test_sync_skips_failed_proxies_but_returns_added_count(self):
        """Sync variant: proxies that fail add_proxy are skipped."""
        pool = ProxyPool(name="test", proxies=[])
        added_proxies: list[Proxy] = []

        def flaky_add_proxy(proxy: Proxy) -> None:
            if len(added_proxies) == 0:
                added_proxies.append(proxy)
                raise RuntimeError("simulated failure")
            added_proxies.append(proxy)

        async def mock_fetch(**kwargs):
            return [
                {"url": "http://45.33.32.156:8080"},
                {"url": "http://45.33.32.157:8080"},
            ]

        with patch("proxywhirl.rotator._bootstrap.fetch_all_sources", new=mock_fetch):
            added = bootstrap_pool_if_empty_sync(
                pool=pool,
                add_proxy=flaky_add_proxy,
                validate=False,
                sources=[ProxySourceConfig(url="https://example.com/a.txt", format="plain_text")],
            )
        assert added == 1

    def test_sync_raises_when_all_adds_fail(self):
        """Sync variant: all add_proxy failures should raise ProxyPoolEmptyError."""
        pool = ProxyPool(name="test", proxies=[])

        def always_fail_add_proxy(proxy: Proxy) -> None:
            raise RuntimeError("simulated failure")

        async def mock_fetch(**kwargs):
            return [{"url": "http://45.33.32.156:8080"}]

        with patch("proxywhirl.rotator._bootstrap.fetch_all_sources", new=mock_fetch):
            with pytest.raises(ProxyPoolEmptyError):
                bootstrap_pool_if_empty_sync(
                    pool=pool,
                    add_proxy=always_fail_add_proxy,
                    validate=False,
                    sources=[
                        ProxySourceConfig(url="https://example.com/a.txt", format="plain_text")
                    ],
                )

    @pytest.mark.asyncio
    async def test_async_noop_when_pool_already_populated(self):
        """A non-empty pool short-circuits bootstrap and returns 0."""
        pool = ProxyPool(name="test", proxies=[Proxy(url="http://45.33.32.156:8080")])

        with patch("proxywhirl.rotator._bootstrap.fetch_all_sources") as mock_fetch:
            added = await bootstrap_pool_if_empty_async(
                pool=pool, add_proxy=AsyncMock(), config=BootstrapConfig()
            )
        assert added == 0
        mock_fetch.assert_not_called()

    def test_sync_noop_when_pool_already_populated(self):
        """A non-empty pool short-circuits bootstrap and returns 0 (sync)."""
        pool = ProxyPool(name="test", proxies=[Proxy(url="http://45.33.32.156:8080")])

        with patch("proxywhirl.rotator._bootstrap.fetch_all_sources") as mock_fetch:
            added = bootstrap_pool_if_empty_sync(
                pool=pool, add_proxy=MagicMock(), config=BootstrapConfig()
            )
        assert added == 0
        mock_fetch.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_raises_when_max_proxies_truncates_to_empty(self):
        """max_proxies=0 truncates all candidates, triggering the empty-pool error."""
        pool = ProxyPool(name="test", proxies=[])

        async def mock_fetch(**kwargs):
            return [{"url": "http://45.33.32.156:8080"}]

        with patch("proxywhirl.rotator._bootstrap.fetch_all_sources", new=mock_fetch):
            with pytest.raises(ProxyPoolEmptyError):
                await bootstrap_pool_if_empty_async(
                    pool=pool,
                    add_proxy=AsyncMock(),
                    validate=False,
                    max_proxies=0,
                    sources=[
                        ProxySourceConfig(url="https://example.com/a.txt", format="plain_text")
                    ],
                )

    def test_sync_raises_when_max_proxies_truncates_to_empty(self):
        """Sync: max_proxies=0 truncates all candidates, triggering the empty-pool error."""
        pool = ProxyPool(name="test", proxies=[])

        async def mock_fetch(**kwargs):
            return [{"url": "http://45.33.32.156:8080"}]

        with patch("proxywhirl.rotator._bootstrap.fetch_all_sources", new=mock_fetch):
            with pytest.raises(ProxyPoolEmptyError):
                bootstrap_pool_if_empty_sync(
                    pool=pool,
                    add_proxy=MagicMock(),
                    validate=False,
                    max_proxies=0,
                    sources=[
                        ProxySourceConfig(url="https://example.com/a.txt", format="plain_text")
                    ],
                )

    def test_sync_legacy_kwargs_build_config_and_apply_max_proxies(self):
        """Legacy kwargs (config=None) construct a BootstrapConfig and respect max_proxies."""
        pool = ProxyPool(name="test", proxies=[])
        added_proxies: list[Proxy] = []

        async def mock_fetch(**kwargs):
            return [
                {"url": "http://45.33.32.156:8080"},
                {"url": "http://45.33.32.157:8080"},
                {"url": "http://45.33.32.158:8080"},
            ]

        with patch("proxywhirl.rotator._bootstrap.fetch_all_sources", new=mock_fetch):
            added = bootstrap_pool_if_empty_sync(
                pool=pool,
                add_proxy=added_proxies.append,
                validate=False,
                timeout=5,
                max_concurrent=10,
                max_proxies=2,
                sources=[ProxySourceConfig(url="https://example.com/a.txt", format="plain_text")],
            )
        assert added == 2
        assert len(added_proxies) == 2
