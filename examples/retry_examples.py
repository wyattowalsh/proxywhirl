"""
Examples demonstrating retry and failover functionality in ProxyWhirl.

This file contains runnable code examples showing how to use:
- Automatic retries with exponential backoff
- Circuit breakers for failing proxies
- Intelligent proxy selection
- Configurable retry policies
- Metrics and observability

Run this file directly to see the examples in action.
"""

from proxywhirl import (
    BackoffStrategy,
    CircuitBreakerState,
    Proxy,
    ProxyRotator,
    RetryPolicy,
)


def example_1_basic_retry():
    """Example 1: Enable automatic retries (default behavior)."""
    print("\n=== Example 1: Basic Automatic Retry ===\n")

    # Create rotator with retry enabled by default
    proxies = [
        Proxy(url="http://proxy1.example.com:8080"),
        Proxy(url="http://proxy2.example.com:8080"),
        Proxy(url="http://proxy3.example.com:8080"),
    ]

    rotator = ProxyRotator(proxies=proxies)

    print("Retry policy (default):")
    print(f"  Max attempts: {rotator.retry_policy.max_attempts}")
    print(f"  Backoff strategy: {rotator.retry_policy.backoff_strategy.value}")
    print(f"  Base delay: {rotator.retry_policy.base_delay}s")
    print(f"  Multiplier: {rotator.retry_policy.multiplier}")
    print(f"  Retry status codes: {rotator.retry_policy.retry_status_codes}")

    # Make request (would automatically retry on failure)
    # response = rotator.get("https://api.example.com/data")
    print("\nRequests will automatically retry with exponential backoff:")
    print("  1st retry: wait 1 second")
    print("  2nd retry: wait 2 seconds")
    print("  3rd retry: wait 4 seconds")


def example_2_custom_retry_policy():
    """Example 2: Custom retry policy configuration."""
    print("\n=== Example 2: Custom Retry Policy ===\n")

    # Create custom retry policy
    policy = RetryPolicy(
        max_attempts=5,                          # Try up to 5 times
        backoff_strategy=BackoffStrategy.LINEAR, # Linear backoff (2s, 4s, 6s, 8s)
        base_delay=2.0,                          # Base delay 2 seconds
        retry_status_codes=[502, 503, 504],       # Only 5xx status codes allowed
        jitter=True,                             # Add random jitter to delays
    )

    proxies = [Proxy(url="http://proxy1.example.com:8080")]
    rotator = ProxyRotator(proxies=proxies, retry_policy=policy)

    print("Custom retry policy:")
    print(f"  Max attempts: {policy.max_attempts}")
    print(f"  Backoff strategy: {policy.backoff_strategy.value}")
    print(f"  Base delay: {policy.base_delay}s")
    print(f"  Jitter enabled: {policy.jitter}")
    print(f"  Retry status codes: {policy.retry_status_codes}")

    # Make request with custom policy
    # response = rotator.get("https://api.example.com/data")


def example_3_per_request_override():
    """Example 3: Per-request policy override."""
    print("\n=== Example 3: Per-Request Policy Override ===\n")

    # Global policy: retry 3 times
    rotator = ProxyRotator(
        proxies=[Proxy(url="http://proxy1.example.com:8080")],
        retry_policy=RetryPolicy(max_attempts=3),
    )

    print("Global policy: 3 attempts")

    # Override for specific request: only 1 retry
    per_request_policy = RetryPolicy(max_attempts=1, base_delay=0.5)

    print("Per-request override: 1 attempt, 0.5s delay")

    # response = rotator._make_request(
    #     "GET",
    #     "https://api.example.com/critical",
    #     retry_policy=per_request_policy,
    # )

    # Or disable retries for this request
    print("\nDisable retries for specific request:")
    # response = rotator._make_request(
    #     "GET",
    #     "https://api.example.com/no-retry",
    #     retry_policy=None,  # No retries
    # )


def example_4_circuit_breaker_monitoring():
    """Example 4: Circuit breaker state monitoring."""
    print("\n=== Example 4: Circuit Breaker Monitoring ===\n")

    proxies = [
        Proxy(url="http://proxy1.example.com:8080"),
        Proxy(url="http://proxy2.example.com:8080"),
        Proxy(url="http://proxy3.example.com:8080"),
    ]

    rotator = ProxyRotator(proxies=proxies)

    # Check circuit breaker states
    states = rotator.get_circuit_breaker_states()

    print("Circuit breaker states:")
    for proxy_id, circuit_breaker in states.items():
        print(f"\nProxy: {proxy_id}")
        print(f"  State: {circuit_breaker.state.value}")
        print(
            f"  Failures: {circuit_breaker.failure_count}/"
            f"{circuit_breaker.failure_threshold}"
        )
        print(f"  Window duration: {circuit_breaker.window_duration}s")
        print(f"  Timeout duration: {circuit_breaker.timeout_duration}s")

        if circuit_breaker.state == CircuitBreakerState.OPEN:
            print(f"  Next test time: {circuit_breaker.next_test_time}")

    print("\nCircuit breaker states:")
    print("  CLOSED: Proxy working normally")
    print("  OPEN: Proxy excluded (too many failures)")
    print("  HALF_OPEN: Testing recovery")


def example_5_retry_metrics():
    """Example 5: Retry metrics and observability."""
    print("\n=== Example 5: Retry Metrics ===\n")

    rotator = ProxyRotator(
        proxies=[
            Proxy(url="http://proxy1.example.com:8080"),
            Proxy(url="http://proxy2.example.com:8080"),
        ]
    )

    # Get retry statistics
    metrics = rotator.get_retry_metrics()
    summary = metrics.get_summary()

    print("Retry metrics:")
    print(f"  Total retries: {summary['total_retries']}")
    print(f"  Success by attempt: {summary['success_by_attempt']}")
    print("    (Example output: {0: 850, 1: 120, 2: 25, 3: 5})")
    print("    - 850 succeeded on first try")
    print("    - 120 succeeded on second retry")
    print("    - 25 succeeded on third retry")
    print("    - 5 succeeded on fourth retry")
    print(
        f"  Circuit breaker events: "
        f"{summary['circuit_breaker_events_count']}"
    )


def example_6_non_idempotent_requests():
    """Example 6: Handling non-idempotent requests (POST/PUT)."""
    print("\n=== Example 6: Non-Idempotent Requests ===\n")

    rotator = ProxyRotator(
        proxies=[Proxy(url="http://proxy1.example.com:8080")],
        retry_policy=RetryPolicy(max_attempts=3),
    )

    print("By default, POST/PUT requests don't retry (not idempotent)")
    # response = rotator.post("https://api.example.com/create", json=data)
    # No retries unless explicitly enabled

    print("\nEnable retries for non-idempotent request (use with caution):")
    policy = RetryPolicy(retry_non_idempotent=True)
    # response = rotator._make_request(
    #     "POST",
    #     "https://api.example.com/create",
    #     json=data,
    #     retry_policy=policy,
    # )


def example_7_backoff_strategies():
    """Example 7: Different backoff strategies."""
    print("\n=== Example 7: Backoff Strategies ===\n")

    proxies = [Proxy(url="http://proxy1.example.com:8080")]

    # Exponential backoff (default)
    policy_exp = RetryPolicy(
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        base_delay=1.0,
        multiplier=2.0,
    )
    print("Exponential backoff: 1s, 2s, 4s, 8s, 16s, ...")

    # Linear backoff
    policy_linear = RetryPolicy(
        backoff_strategy=BackoffStrategy.LINEAR,
        base_delay=2.0,
    )
    print("Linear backoff: 2s, 4s, 6s, 8s, 10s, ...")

    # Fixed backoff
    policy_fixed = RetryPolicy(
        backoff_strategy=BackoffStrategy.FIXED,
        base_delay=3.0,
    )
    print("Fixed backoff: 3s, 3s, 3s, 3s, 3s, ...")

    # With jitter (randomization)
    policy_jitter = RetryPolicy(
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        base_delay=1.0,
        jitter=True,  # Adds ?50% randomness
    )
    print("\nWith jitter: 1s?50%, 2s?50%, 4s?50%, ...")
    print("(Prevents thundering herd problem)")


def example_8_geo_targeted_retry():
    """Example 8: Geo-targeted proxy retry selection."""
    print("\n=== Example 8: Geo-Targeted Retry Selection ===\n")

    # Create proxies with region metadata
    proxies = [
        Proxy(
            url="http://proxy-us.example.com:8080",
            metadata={"region": "US-EAST"},
        ),
        Proxy(
            url="http://proxy-eu.example.com:8080",
            metadata={"region": "EU-WEST"},
        ),
    ]

    rotator = ProxyRotator(proxies=proxies)

    print("Proxies with region metadata:")
    print("  - proxy-us: US-EAST")
    print("  - proxy-eu: EU-WEST")

    print("\nWhen retry is needed:")
    print("  - System prioritizes proxies in the same region")
    print("  - 10% bonus for matching region")
    print("  - Improves latency and success rates")


def example_9_manual_circuit_breaker_reset():
    """Example 9: Manually reset circuit breaker."""
    print("\n=== Example 9: Manual Circuit Breaker Reset ===\n")

    proxies = [Proxy(url="http://proxy1.example.com:8080")]
    rotator = ProxyRotator(proxies=proxies)

    proxy_id = list(rotator.circuit_breakers.keys())[0]

    print(f"Proxy ID: {proxy_id}")
    print(f"State before: {rotator.circuit_breakers[proxy_id].state.value}")

    # Manually reset circuit breaker
    # rotator.reset_circuit_breaker(proxy_id)

    print("State after reset: CLOSED")
    print("Failure count: 0")


def example_10_timeout_management():
    """Example 10: Total timeout management."""
    print("\n=== Example 10: Timeout Management ===\n")

    # Set total timeout (including all retries)
    policy = RetryPolicy(
        max_attempts=5,
        base_delay=2.0,
        timeout=15.0,  # Total timeout: 15 seconds
    )

    rotator = ProxyRotator(
        proxies=[Proxy(url="http://proxy1.example.com:8080")],
        retry_policy=policy,
    )

    print("Retry policy with timeout:")
    print(f"  Max attempts: {policy.max_attempts}")
    print(f"  Base delay: {policy.base_delay}s")
    print(f"  Total timeout: {policy.timeout}s")
    print("\nIf retries would exceed 15s, stops early")


def main():
    """Run all examples."""
    print("=" * 70)
    print("ProxyWhirl Retry & Failover Examples")
    print("=" * 70)

    example_1_basic_retry()
    example_2_custom_retry_policy()
    example_3_per_request_override()
    example_4_circuit_breaker_monitoring()
    example_5_retry_metrics()
    example_6_non_idempotent_requests()
    example_7_backoff_strategies()
    example_8_geo_targeted_retry()
    example_9_manual_circuit_breaker_reset()
    example_10_timeout_management()

    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)
    print("\nFor more information:")
    print("  - Documentation: /docs/RETRY_FAILOVER_GUIDE.md")
    print("  - API Reference: /specs/014-retry-failover-logic/contracts/retry-api.yaml")
    print("  - Tests: /tests/integration/test_retry_integration.py")


if __name__ == "__main__":
    main()
