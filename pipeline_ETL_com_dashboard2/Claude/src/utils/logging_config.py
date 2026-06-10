"""
Logging configuration for the entire application.
Provides structured logging with file and console handlers.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from src.config import LoggingConfig


def setup_logging(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Configure logging for a specific module.

    Args:
        name: Logger name (typically __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if not level:
        level = LoggingConfig.LEVEL

    if not log_file:
        log_file = LoggingConfig.FILE

    logger.setLevel(getattr(logging, level))

    # Create formatters
    formatter = logging.Formatter(LoggingConfig.FORMAT)

    # File handler
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10485760, backupCount=10  # 10MB per file
    )
    file_handler.setLevel(getattr(logging, level))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Create module logger
logger = setup_logging(__name__)
