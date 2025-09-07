"""proxywhirl/cli/theme.py -- Rich theme configuration for CLI"""

from rich.theme import Theme

# Enhanced ProxyWhirl theme for better UX
PROXYWHIRL_THEME = Theme(
    {
        "proxy": "cyan bold",
        "success": "green bold",
        "warning": "yellow bold",
        "error": "red bold",
        "info": "blue",
        "accent": "magenta",
        "dim": "dim white",
    }
)
