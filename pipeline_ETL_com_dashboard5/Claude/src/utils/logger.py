"""
Logging configuration for the ETL pipeline.
"""

import logging
import logging.handlers
from pathlib import Path
from src.utils.config import Config


class LoggerSetup:
    """Setup logging configuration."""

    _logger = None

    @classmethod
    def setup(cls) -> logging.Logger:
        """Setup and return logger."""
        if cls._logger is not None:
            return cls._logger

        # Create logs directory
        log_file = Path(Config.LOG_FILE)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create logger
        logger = logging.getLogger('etl_pipeline')
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, Config.LOG_LEVEL))

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            Config.LOG_FILE,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        cls._logger = logger
        return logger

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get logger instance."""
        if cls._logger is None:
            return cls.setup()
        return cls._logger


def get_logger() -> logging.Logger:
    """Get logger instance."""
    return LoggerSetup.get_logger()
