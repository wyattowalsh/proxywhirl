"""proxywhirl/logger.py -- logger for proxywhirl"""

import logging

from loguru import logger
from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.logging import RichHandler
from rich.theme import Theme

# 1. Create a Rich Console for consistent styling
# Using a custom theme for log levels
# From richuru
custom_theme = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "bold red",
        "critical": "bold magenta",
        "debug": "dim",
        # for rich handler
        "logging.level.info": "cyan",
        "logging.level.success": "green",
        "logging.level.warning": "yellow",
        "logging.level.error": "bold red",
        "logging.level.critical": "bold magenta",
        "logging.level.debug": "dim",
    }
)

console = Console(theme=custom_theme, stderr=True)


# 2. Intercept standard logging
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


# 3. Configure loguru
# Remove default handler
logger.remove()
logger.configure(
    handlers=[
        {
            "sink": RichHandler(
                console=console,
                show_time=True,
                show_level=True,
                show_path=True,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                highlighter=ReprHighlighter(),
                markup=True,
            ),
            "format": "{message}",  # Let RichHandler do the formatting
            "level": "INFO",
        }
    ],
    extra={"app_name": "proxywhirl"},  # Example extra
)

# 4. Set up intercept handler
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
