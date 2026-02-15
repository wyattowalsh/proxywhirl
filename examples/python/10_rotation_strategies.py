"""
Rotation strategy showcase for ProxyWhirl.

Each example is deterministic, works offline, and highlights when to reach
for a given strategy. Run with:

    uv run python examples/python/10_rotation_strategies.py
"""

from __future__ import annotations

import random
from typing import Iterable

from proxywhirl import (
    CompositeStrategy,
    GeoTargetedStrategy,
    LeastUsedStrategy,
    PerformanceBasedStrategy,
    Proxy,
    ProxyPool,
    ProxyWhirl,
    RandomStrategy,
    RoundRobinStrategy,
    SessionPersistenceStrategy,
    StrategyRegistry,
    WeightedStrategy,
)
from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import HealthStatus, SelectionContext, StrategyConfig

# Make weighted/random picks reproducible for the example output
random.seed(42)


def _healthy_proxies() -> list[Proxy]:
    """Seed proxies with consistent metadata for all demos."""
    proxies = [
        Proxy(
            url="http://alpha.proxy.local:8000",
            country_code="US",
            region="us-east-1",
            metadata={"tier": "gold"},
        ),
        Proxy(
            url="http://bravo.proxy.local:8000",
            country_code="DE",
            region="eu-central-1",
            metadata={"tier": "silver"},
        ),
        Proxy(
            url="http://charlie.proxy.local:8000",
            country_code="SG",
            region="ap-southeast-1",
            metadata={"tier": "silver"},
        ),
    ]
    for proxy in proxies:
        proxy.health_status = HealthStatus.HEALTHY
    return proxies


def _print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def _pick(
    rotator: ProxyWhirl,
    *,
    context: SelectionContext | None = None,
    success: bool = True,
    response_time_ms: float = 120.0,
) -> Proxy:
    """Select a proxy via the active strategy and record the result."""
    proxy = rotator.strategy.select(rotator.pool, context=context)
    rotator.strategy.record_result(proxy, success=success, response_time_ms=response_time_ms)
    return proxy


def _print_sequence(label: str, proxies: Iterable[Proxy]) -> None:
    urls = [proxy.url for proxy in proxies]
    print(f"{label}: {' -> '.join(urls)}")


def round_robin_demo() -> None:
    _print_header("Round-robin for fair distribution")
    rotator = ProxyWhirl(
        proxies=[p.model_copy(deep=True) for p in _healthy_proxies()],
        strategy=RoundRobinStrategy(),
    )
    picks = [_pick(rotator) for _ in range(6)]
    _print_sequence("Rotation order", picks)
    print("Even spread keeps traffic balanced across the pool.")


def random_and_weighted_demo() -> None:
    _print_header("Random vs. weighted selection")
    proxies = _healthy_proxies()

    print("Random strategy (uniform chance):")
    random_rotator = ProxyWhirl(
        proxies=[p.model_copy(deep=True) for p in proxies],
        strategy=RandomStrategy(),
    )
    random_picks = [_pick(random_rotator) for _ in range(4)]
    _print_sequence("Random picks", random_picks)

    # Pretend alpha is healthiest, bravo is catching up, charlie is flaky
    proxies[0].total_requests = proxies[0].total_successes = 50
    proxies[1].total_requests = 40
    proxies[1].total_successes = 30
    proxies[2].total_requests = 40
    proxies[2].total_successes = 10

    weighted_strategy = WeightedStrategy()
    weighted_strategy.configure(
        StrategyConfig(
            weights={
                proxies[0].url: 5.0,  # gold
                proxies[1].url: 3.0,  # silver
                proxies[2].url: 1.0,  # degraded
            }
        )
    )
    weighted_rotator = ProxyWhirl(
        proxies=[p.model_copy(deep=True) for p in proxies],
        strategy=weighted_strategy,
    )
    weighted_picks = [_pick(weighted_rotator) for _ in range(6)]
    _print_sequence("Weighted picks", weighted_picks)
    print("Weights bias selection toward higher-performing proxies.")


def least_used_demo() -> None:
    _print_header("Least-used for load shedding")
    proxies = _healthy_proxies()
    proxies[0].requests_completed = 12
    proxies[1].requests_completed = 6
    proxies[2].requests_completed = 9

    rotator = ProxyWhirl(
        proxies=[p.model_copy(deep=True) for p in proxies],
        strategy=LeastUsedStrategy(),
    )
    picks = [_pick(rotator) for _ in range(4)]
    _print_sequence("Least-used picks", picks)
    print("Least-used pulls lagging proxies forward to smooth the request curve.")


def performance_based_demo() -> None:
    _print_header("Performance-based selection (EMA latency)")
    proxies = _healthy_proxies()
    proxies[0].ema_response_time_ms = 45.0
    proxies[1].ema_response_time_ms = 90.0
    proxies[2].ema_response_time_ms = 180.0

    rotator = ProxyWhirl(
        proxies=[p.model_copy(deep=True) for p in proxies],
        strategy=PerformanceBasedStrategy(),
    )
    picks = [_pick(rotator, response_time_ms=proxy.ema_response_time_ms or 120.0) for proxy in proxies]
    _print_sequence("Fastest-first preference", picks)
    print("Choose this for low-latency APIs; faster proxies get reused more often.")


def session_persistence_demo() -> None:
    _print_header("Session persistence for sticky sessions")
    rotator = ProxyWhirl(
        proxies=[p.model_copy(deep=True) for p in _healthy_proxies()],
        strategy=SessionPersistenceStrategy(),
    )
    session_id = "user-session-42"
    context = SelectionContext(session_id=session_id)
    picks = [_pick(rotator, context=context) for _ in range(5)]
    _print_sequence("Sticky session picks", picks)
    print("All requests for the same session stay anchored to one proxy.")


def geo_targeted_demo() -> None:
    _print_header("Geo-targeted routing")
    rotator = ProxyWhirl(
        proxies=[p.model_copy(deep=True) for p in _healthy_proxies()],
        strategy=GeoTargetedStrategy(),
    )
    eu_pick = _pick(rotator, context=SelectionContext(target_country="DE"))
    us_pick = _pick(rotator, context=SelectionContext(target_country="US"))
    print(f"EU request -> {eu_pick.url} ({eu_pick.country_code})")
    print(f"US request -> {us_pick.url} ({us_pick.country_code})")
    print("Geo strategy filters to matching countries before selecting.")


def composition_demo() -> None:
    _print_header("Composed strategies (filter + selector)")
    proxies = _healthy_proxies()
    proxies[0].ema_response_time_ms = 40.0
    proxies[1].ema_response_time_ms = 120.0
    proxies[2].ema_response_time_ms = 85.0

    composite = CompositeStrategy(
        filters=[GeoTargetedStrategy()],
        selector=PerformanceBasedStrategy(),
    )
    rotator = ProxyWhirl(
        proxies=[p.model_copy(deep=True) for p in proxies],
        strategy=composite,
    )
    context = SelectionContext(target_country="SG")
    pick = _pick(rotator, context=context)
    print(f"Filtered to SG -> selected fastest: {pick.url} ({pick.ema_response_time_ms} ms)")
    print("Compose filters + selectors for complex routing rules.")


def hot_swap_demo() -> None:
    _print_header("Hot-swapping strategies at runtime")
    rotator = ProxyWhirl(
        proxies=[p.model_copy(deep=True) for p in _healthy_proxies()],
        strategy=RoundRobinStrategy(),
    )
    first = _pick(rotator)
    print(f"Start with round-robin -> {first.url}")

    rotator.set_strategy(RandomStrategy())
    swapped = _pick(rotator)
    print(f"Swapped to random -> {swapped.url}")

    rotator.set_strategy("least-used")
    third = _pick(rotator)
    print(f"Swapped via name ('least-used') -> {third.url}")
    print("Swaps are atomic; in-flight requests keep their original strategy.")


def custom_strategy_demo() -> None:
    _print_header("Registering a custom strategy plugin")

    class AlwaysFirstStrategy:
        """Minimal plugin: always returns the first healthy proxy."""

        def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
            proxies = pool.get_healthy_proxies()
            if not proxies:
                raise ProxyPoolEmptyError("No healthy proxies available")
            return proxies[0]

        def record_result(
            self, proxy: Proxy, success: bool, response_time_ms: float | None = None
        ) -> None:
            # Could push telemetry or update custom stats here
            proxy.total_requests += 1
            if success:
                proxy.total_successes += 1
            else:
                proxy.total_failures += 1

    registry = StrategyRegistry()
    registry.register_strategy("always-first", AlwaysFirstStrategy)
    strategy_cls = registry.get_strategy("always-first")

    rotator = ProxyWhirl(
        proxies=[p.model_copy(deep=True) for p in _healthy_proxies()],
        strategy=strategy_cls(),
    )
    picks = [_pick(rotator) for _ in range(3)]
    _print_sequence("Custom plugin picks", picks)
    print("Plugins let teams codify bespoke routing logic behind a simple name.")


def main() -> None:
    round_robin_demo()
    random_and_weighted_demo()
    least_used_demo()
    performance_based_demo()
    session_persistence_demo()
    geo_targeted_demo()
    composition_demo()
    hot_swap_demo()
    custom_strategy_demo()


if __name__ == "__main__":
    main()
