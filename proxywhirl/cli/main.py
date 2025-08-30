"""proxywhirl/cli/main.py -- Main CLI entry point"""

from __future__ import annotations

from .app import app


def main() -> None:
    """Main CLI entry point."""
    # Import all command modules to register them with the app
    from .commands import (  # noqa: F401
        data_display,
        data_export,
        interactive,
        monitoring,
        proxy_access,
        proxy_management,
        reference,
        testing,
        validation,
    )
    
    app()


# Alias for compatibility with tests
cli = app


if __name__ == "__main__":
    main()
