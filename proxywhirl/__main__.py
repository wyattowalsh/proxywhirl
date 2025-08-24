"""Allow running TUI with python -m proxywhirl"""


def run_tui():
    """Run the TUI application."""
    try:
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        app.run()
    except ImportError:
        from proxywhirl.cli import main

        print("TUI not available, falling back to CLI")
        main()


if __name__ == "__main__":
    from proxywhirl.cli import main

    main()
