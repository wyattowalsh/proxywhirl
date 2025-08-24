"""proxywhirl/logger.py -- logger for proxywhirl"""

import logging
from typing import Optional

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


def setup_logger(
    level: str = "INFO", file_path: Optional[str] = None, rich_enabled: bool = True
) -> None:
    """Setup logger with configurable options."""
    logger.remove()

    handlers = []
    if rich_enabled:
        handlers.append(
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
                "format": "{message}",
                "level": level,
            }
        )

    if file_path:
        handlers.append(
            {
                "sink": file_path,
                "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
                "level": level,
            }
        )

    logger.configure(handlers=handlers, extra={"app_name": "proxywhirl"})


def get_logger(name: Optional[str] = None):
    """Get a logger instance."""
    return logger.bind(name=name) if name else logger


def configure_rich_logging(enabled: bool = True) -> None:
    """Configure Rich logging integration."""
    if enabled:
        setup_logger(rich_enabled=True)
    else:
        setup_logger(rich_enabled=False)
