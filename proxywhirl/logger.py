"""proxywhirl/logger.py -- logger for proxywhirl"""

import logging
import sys
from typing import Optional

from loguru import logger
from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.logging import RichHandler
from rich.theme import Theme

# 1. Create a Rich Console for consistent styling
# Using a custom theme for log levels with optimized compact styling
custom_theme = Theme(
    {
        "info": "cyan",
        "success": "bold green",
        "warning": "yellow",
        "error": "bold red",
        "critical": "bold magenta",
        "debug": "dim cyan",
        # for rich handler
        "logging.level.info": "cyan",
        "logging.level.success": "bold green",
        "logging.level.warning": "yellow",
        "logging.level.error": "bold red",
        "logging.level.critical": "bold magenta",
        "logging.level.debug": "dim cyan",
        # compact level styles
        "level.info": "cyan",
        "level.success": "bold green",
        "level.warning": "yellow",
        "level.error": "bold red",
        "level.critical": "bold magenta",
        "level.debug": "dim cyan",
    }
)

# Optimized console with width optimization and compact output
console = Console(
    theme=custom_theme,
    stderr=True,
    width=120,  # Optimal width for most terminals
    force_terminal=True,  # Ensure colors in various environments
    highlight=False,  # Reduce visual noise for compact output
)


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


# 3. Configure loguru with compact, optimized settings
logger.remove()
logger.add(
    RichHandler(
        console=console,
        show_time=False,  # Compact: Time shown in format string
        show_level=False,  # Compact: Level shown in format string
        show_path=False,  # Compact: Hide file paths
        rich_tracebacks=True,
        tracebacks_show_locals=False,  # Compact: Reduce traceback verbosity
        highlighter=ReprHighlighter(),
        markup=True,
        keywords=[],  # Reduce highlighting noise
    ),
    # Compact format with inline time and level styling
    format="<dim>{time:HH:mm:ss}</dim> <level>{level: <8}</level> <cyan>|</cyan> {message}",
    level="INFO",
    colorize=True,  # Enable loguru color support
)

# 4. Set up intercept handler
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


def setup_logger(
    level: str = "INFO", file_path: Optional[str] = None, rich_enabled: bool = True
) -> None:
    """Setup logger with configurable options for compact, well-styled output."""
    logger.remove()

    if rich_enabled:
        logger.add(
            RichHandler(
                console=console,
                show_time=False,  # Compact: Time shown in format string
                show_level=False,  # Compact: Level shown in format string
                show_path=False,  # Compact: Remove file paths for cleaner output
                rich_tracebacks=True,
                tracebacks_show_locals=False,  # Compact: Reduce local variable verbosity
                highlighter=ReprHighlighter(),
                markup=True,
                keywords=[],  # Reduce highlighting noise
            ),
            # Compact format: short time, styled level, clean message
            format="<dim>{time:HH:mm:ss}</dim> <level>{level: <8}</level> <cyan>|</cyan> {message}",
            level=level,
            colorize=True,
        )

    if file_path:
        logger.add(
            file_path,
            # File format can be more verbose since it's for debugging
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=level,
            colorize=False,
        )


def get_logger(name: Optional[str] = None):
    """Get a logger instance."""
    return logger.bind(name=name) if name else logger


def configure_rich_logging(enabled: bool = True) -> None:
    """Configure Rich logging integration with compact styling."""
    if enabled:
        setup_logger(rich_enabled=True)
    else:
        # Simple non-rich logger for compact output
        logger.remove()
        logger.add(
            sys.stderr,
            format="<dim>{time:HH:mm:ss}</dim> <level>{level: <8}</level> <cyan>|</cyan> {message}",
            level="INFO",
            colorize=False,
        )
