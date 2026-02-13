"""
Demo script for ProxyWhirl TUI.

Shows the full-featured terminal interface with all capabilities.
"""

from proxywhirl import ProxyRotator
from proxywhirl.tui import run_tui

def main():
    """Run TUI demo."""
    # Create rotator with demo proxies
    rotator = ProxyRotator()

    # Add some demo proxies
    demo_proxies = [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        "http://proxy3.example.com:3128",
    ]

    for proxy_url in demo_proxies:
        rotator.add_proxy(proxy_url)

    print("\n🚀 Launching ProxyWhirl TUI...")
    print("\nFeatures:")
    print("  • Overview - Real-time metrics and proxy table")
    print("  • Fetch & Validate - Auto-fetch from 64+ sources")
    print("  • Export - Save to CSV, JSON, YAML, or Text")
    print("  • Test - Send HTTP requests through proxies")
    print("  • Analytics - View statistics and insights")
    print("\nKeyboard Shortcuts:")
    print("  • Ctrl+C - Quit")
    print("  • Ctrl+R - Refresh all data")
    print("  • Ctrl+F - Go to Fetch tab")
    print("  • Ctrl+E - Go to Export tab")
    print("  • Ctrl+T - Go to Test tab")
    print("  • F1 - Show help")
    print("\nPress Ctrl+C to exit the TUI.\n")

    # Launch TUI
    run_tui(rotator=rotator)

if __name__ == "__main__":
    main()
