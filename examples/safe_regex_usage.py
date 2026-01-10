"""Example usage of safe regex pattern matching with ReDoS protection.

This example demonstrates how to use the safe_regex module to protect
CLI commands from Regular Expression Denial of Service (ReDoS) attacks.
"""

from proxywhirl.safe_regex import (
    safe_regex_compile,
    safe_regex_findall,
    safe_regex_match,
    safe_regex_search,
)


def example_safe_pattern_matching():
    """Example: Safe pattern matching with user input."""
    print("=" * 60)
    print("Example 1: Safe Pattern Matching")
    print("=" * 60)

    # User-provided pattern (could be malicious)
    user_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    test_ip = "192.168.1.1"

    # Safe matching with validation
    match = safe_regex_match(user_pattern, test_ip)
    if match:
        print(f"✓ Pattern matched: {match.group()}")
    else:
        print("✗ No match")

    print()


def example_filtering_proxy_list():
    """Example: Filter proxy list by country code."""
    print("=" * 60)
    print("Example 2: Filtering Proxy List")
    print("=" * 60)

    proxies = [
        "US:proxy1.example.com:8080",
        "UK:proxy2.example.com:8080",
        "US:proxy3.example.com:8080",
        "FR:proxy4.example.com:8080",
    ]

    # User wants to filter by country
    country_code = "US"
    pattern = f"^{country_code}:"

    # Safe filtering
    us_proxies = [p for p in proxies if safe_regex_match(pattern, p)]
    print(f"Found {len(us_proxies)} proxies for {country_code}:")
    for proxy in us_proxies:
        print(f"  - {proxy}")

    print()


def example_extract_all_ports():
    """Example: Extract all port numbers from proxy list."""
    print("=" * 60)
    print("Example 3: Extract All Ports")
    print("=" * 60)

    proxy_list = """
    http://proxy1.com:8080
    http://proxy2.com:3128
    socks5://proxy3.com:1080
    http://proxy4.com:8888
    """

    # Extract all port numbers
    pattern = r":(\d+)"
    ports = safe_regex_findall(pattern, proxy_list)

    print(f"Found {len(ports)} port numbers:")
    print(f"  Ports: {', '.join(ports)}")

    print()


def example_malicious_pattern_rejection():
    """Example: Malicious pattern is rejected."""
    print("=" * 60)
    print("Example 4: Malicious Pattern Rejection")
    print("=" * 60)

    # Attacker tries to DoS with nested quantifiers
    malicious_pattern = r"(a+)+"
    text = "aaaaa"

    print(f"Attempting to use malicious pattern: {malicious_pattern}")
    try:
        match = safe_regex_match(malicious_pattern, text)
        print(f"✗ Pattern should have been rejected!")
    except SystemExit:
        print("✓ Malicious pattern was rejected (as expected)")

    print()


def example_search_logs():
    """Example: Search logs with user-provided pattern."""
    print("=" * 60)
    print("Example 5: Search Logs")
    print("=" * 60)

    log_lines = [
        "[2024-01-01 10:00:00] INFO: Server started",
        "[2024-01-01 10:05:00] ERROR: Connection failed to 192.168.1.1:8080",
        "[2024-01-01 10:10:00] INFO: Request completed",
        "[2024-01-01 10:15:00] ERROR: Timeout connecting to proxy",
    ]

    # User wants to find all ERROR lines
    pattern = r"ERROR:"

    print("Searching for ERROR messages:")
    for line in log_lines:
        if safe_regex_search(pattern, line):
            print(f"  - {line}")

    print()


def example_compile_once_use_many():
    """Example: Compile pattern once, use many times."""
    print("=" * 60)
    print("Example 6: Compile Once, Use Many Times")
    print("=" * 60)

    # Compile pattern once for efficiency
    pattern = safe_regex_compile(r"proxy\d+\.example\.com")

    hosts = [
        "proxy1.example.com",
        "other.example.com",
        "proxy2.example.com",
        "proxy3.example.com",
    ]

    print("Finding proxy hosts:")
    matches = []
    for host in hosts:
        if safe_regex_match(pattern, host, validate=False):  # Already validated
            matches.append(host)

    print(f"Found {len(matches)} proxy hosts:")
    for match in matches:
        print(f"  - {match}")

    print()


def example_timeout_protection():
    """Example: Timeout protection on valid but slow patterns."""
    print("=" * 60)
    print("Example 7: Timeout Protection")
    print("=" * 60)

    # A pattern that's valid but could be slow on certain inputs
    # Using a very short timeout for demonstration
    pattern = r"^[a-z]+$"
    text = "a" * 10000  # Very long text

    print(f"Matching pattern against {len(text)} character string...")
    try:
        match = safe_regex_match(pattern, text, timeout=5.0)
        if match:
            print("✓ Pattern matched successfully (within timeout)")
        else:
            print("✗ No match")
    except SystemExit:
        print("✗ Operation timed out")

    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Safe Regex Pattern Matching Examples" + " " * 11 + "║")
    print("║" + " " * 14 + "ReDoS Attack Prevention" + " " * 21 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")

    # Run examples
    example_safe_pattern_matching()
    example_filtering_proxy_list()
    example_extract_all_ports()
    example_search_logs()
    example_compile_once_use_many()
    example_timeout_protection()

    # Note about malicious patterns (don't run by default as it exits)
    print("=" * 60)
    print("Note: Example 4 (Malicious Pattern Rejection)")
    print("=" * 60)
    print("Run example_malicious_pattern_rejection() separately to see")
    print("how malicious patterns are rejected with proper error messages.")
    print()

    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
    print()
