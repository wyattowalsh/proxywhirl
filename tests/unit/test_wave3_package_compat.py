"""Import compatibility tests for Wave 3 package splits."""

from __future__ import annotations

import warnings


def test_strategies_package_flat_imports() -> None:
    from proxywhirl.strategies import (
        CompositeStrategy,
        RoundRobinStrategy,
        StrategyRegistry,
        resolve_builtin_strategy,
    )

    assert resolve_builtin_strategy("round-robin").__class__ is RoundRobinStrategy
    assert CompositeStrategy(selector=RoundRobinStrategy()).selector.__class__ is RoundRobinStrategy
    assert StrategyRegistry() is StrategyRegistry()


def test_fetchers_package_flat_imports() -> None:
    from proxywhirl.fetchers import (
        JSONParser,
        ProxyFetcher,
        ProxySourceConfig,
        ProxyValidator,
        deduplicate_proxies,
        validate_proxy_url_safety,
    )

    assert JSONParser is not None
    assert ProxyFetcher is not None
    assert ProxyValidator is not None
    assert callable(deduplicate_proxies)
    assert callable(validate_proxy_url_safety)
    assert ProxySourceConfig is not None


def test_models_package_flat_imports() -> None:
    from proxywhirl.models import HealthStatus, Proxy, ProxyPool, SelectionContext

    assert HealthStatus.HEALTHY
    assert Proxy(url="http://8.8.8.8:8080")
    assert ProxyPool(name="t")
    assert SelectionContext()


def test_cli_thin_entry_preserves_released_command_symbols() -> None:
    from proxywhirl.cli import (
        app,
        config,
        export,
        fetch,
        health,
        import_proxies,
        pool,
        request,
        sources,
        validate_proxy,
    )

    assert app is not None
    assert all(
        callable(command)
        for command in (
            request,
            pool,
            config,
            export,
            fetch,
            sources,
            health,
            validate_proxy,
            import_proxies,
        )
    )


def test_lazy_public_api_and_ratelimiter_compatibility() -> None:
    import proxywhirl

    assert proxywhirl.ProxyWhirl is not None
    assert proxywhirl.RoundRobinStrategy is not None

    # Force the lazy path even if a prior test already cached the export.
    proxywhirl.__dict__.pop("RateLimiter", None)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        limiter = proxywhirl.RateLimiter
    assert limiter is not None
    assert not caught
