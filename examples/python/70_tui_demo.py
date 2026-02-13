#!/usr/bin/env python3
"""
Example: ProxyWhirl TUI Demo

This script demonstrates the ProxyWhirl Terminal User Interface (TUI),
showcasing the beautiful, interactive dashboard for proxy management.
"""

from proxywhirl import ProxyRotator
from proxywhirl.tui import run_tui


def main() -> None:
    """Launch TUI with sample proxies."""
    # Create a rotator with some example proxies
    rotator = ProxyRotator(strategy="round-robin")

    # Add some demo proxies (these won't actually work, just for demo)
    demo_proxies = [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        "http://proxy3.example.com:3128",
        "http://proxy4.example.com:8888",
    ]

    print("🚀 Setting up demo proxies...")
    for proxy_url in demo_proxies:
        try:
            rotator.add_proxy(proxy_url)
            print(f"  ✓ Added: {proxy_url}")
        except Exception as e:
            print(f"  ✗ Failed to add {proxy_url}: {e}")

    print("\n📊 Launching TUI...")
    print("=" * 60)
    print("ProxyWhirl TUI Features:")
    print("  • Real-time proxy pool monitoring")
    print("  • Interactive request testing")
    print("  • Live metrics dashboard")
    print("  • Color-coded health status")
    print("  • Full keyboard navigation")
    print("=" * 60)
    print("\nKeyboard shortcuts:")
    print("  Ctrl+C or Q  - Quit")
    print("  R            - Refresh displays")
    print("  A            - Add proxy")
    print("  T            - Test request")
    print("  F1           - Show help")
    print("=" * 60)
    print()

    # Launch the TUI
    run_tui(rotator=rotator)


if __name__ == "__main__":
    main()
