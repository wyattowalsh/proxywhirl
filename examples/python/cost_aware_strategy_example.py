"""
Example demonstrating CostAwareStrategy for cost-optimized proxy selection.

This example shows how to use the CostAwareStrategy to prioritize free proxies
over paid ones, with configurable cost thresholds.
"""

from proxywhirl import (
    CostAwareStrategy,
    HealthStatus,
    Proxy,
    ProxyPool,
    StrategyConfig,
)


def main() -> None:
    """Demonstrate CostAwareStrategy usage."""
    # Create a proxy pool
    pool = ProxyPool(name="cost-aware-pool")

    # Add free proxies
    for i in range(3):
        proxy = Proxy(
            url=f"http://free{i}.example.com:8080",
            health_status=HealthStatus.HEALTHY,
        )
        proxy.cost_per_request = 0.0  # Free proxy
        pool.add_proxy(proxy)

    # Add cheap paid proxies
    for i in range(2):
        proxy = Proxy(
            url=f"http://cheap{i}.example.com:8080",
            health_status=HealthStatus.HEALTHY,
        )
        proxy.cost_per_request = 0.1  # $0.10 per request
        pool.add_proxy(proxy)

    # Add expensive paid proxies
    for i in range(2):
        proxy = Proxy(
            url=f"http://expensive{i}.example.com:8080",
            health_status=HealthStatus.HEALTHY,
        )
        proxy.cost_per_request = 1.0  # $1.00 per request
        pool.add_proxy(proxy)

    # Example 1: Basic cost-aware selection
    print("Example 1: Basic cost-aware selection")
    strategy = CostAwareStrategy()

    # Make 10 selections and observe free proxies are heavily favored
    selections = [strategy.select(pool) for _ in range(10)]
    print(f"Selected proxies: {[s.url for s in selections]}")
    free_count = sum(1 for s in selections if s.cost_per_request == 0.0)
    print(f"Free proxies selected: {free_count}/10")
    print()

    # Example 2: Configure max cost threshold
    print("Example 2: With max cost threshold of $0.5")
    config = StrategyConfig(metadata={"max_cost_per_request": 0.5})
    strategy_with_threshold = CostAwareStrategy()
    strategy_with_threshold.configure(config)

    # Now expensive proxies (cost > 0.5) will be filtered out
    selections = [strategy_with_threshold.select(pool) for _ in range(10)]
    print(f"Selected proxies: {[s.url for s in selections]}")
    max_cost = max(s.cost_per_request or 0.0 for s in selections)
    print(f"Max cost of selected proxies: ${max_cost}")
    print()

    # Example 3: Configure free proxy boost
    print("Example 3: Lower free proxy boost (5x instead of 10x)")
    config = StrategyConfig(metadata={"free_proxy_boost": 5.0})
    strategy_low_boost = CostAwareStrategy()
    strategy_low_boost.configure(config)

    selections = [strategy_low_boost.select(pool) for _ in range(20)]
    free_count = sum(1 for s in selections if s.cost_per_request == 0.0)
    cheap_count = sum(1 for s in selections if s.cost_per_request == 0.1)
    expensive_count = sum(1 for s in selections if s.cost_per_request == 1.0)
    print(f"Free: {free_count}, Cheap: {cheap_count}, Expensive: {expensive_count}")
    print()

    # Example 4: Initialize with max cost
    print("Example 4: Initialize with max cost parameter")
    strategy_init = CostAwareStrategy(max_cost_per_request=0.2)

    selections = [strategy_init.select(pool) for _ in range(10)]
    print(f"Selected proxies: {[s.url for s in selections]}")
    print("Only free and cheap proxies selected (cost <= 0.2)")
    print()

    print("Cost-aware strategy demonstration complete!")


if __name__ == "__main__":
    main()
