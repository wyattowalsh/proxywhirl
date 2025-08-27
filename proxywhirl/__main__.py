"""Allow running TUI with python -m proxywhirl"""

try:
    from .tui import run_tui
except ImportError:

    def run_tui():
        print("TUI not available. Please use the CLI instead:")
        print("python -m proxywhirl.cli --help")


if __name__ == "__main__":
    run_tui()
