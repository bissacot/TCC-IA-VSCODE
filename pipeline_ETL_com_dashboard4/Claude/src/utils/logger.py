"""
Logging configuration and utilities for the ETL application.

Provides structured logging with both console and file output.
"""

import logging
from pathlib import Path
from typing import Optional

from config.settings import LOG_LEVEL, LOG_FORMAT, LOG_FILE


class LoggerConfig:
    """Configures application logging."""

    _logger: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get or create a logger with the specified name.

        Args:
            name: Logger name (typically __name__ from calling module)

        Returns:
            Configured logger instance
        """
        if cls._logger is None:
            cls._setup_logging()

        return logging.getLogger(name)

    @classmethod
    def _setup_logging(cls) -> None:
        """Configure logging for the application."""
        # Create logs directory if it doesn't exist
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(LOG_LEVEL)

        # Remove existing handlers
        root_logger.handlers.clear()

        # Formatter
        formatter = logging.Formatter(LOG_FORMAT)

        # File handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(LOG_LEVEL)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOG_LEVEL)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        cls._logger = root_logger
