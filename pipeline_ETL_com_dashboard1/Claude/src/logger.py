"""
Structured Logging Configuration
Centralized logging setup with rotating file handlers and console output
"""

import logging
import logging.handlers
from typing import Optional
from pathlib import Path

from src.config import config


class LoggerSetup:
    """Configure application logging"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get or create logger with specified name
        
        Args:
            name: Logger name (typically __name__)
            
        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.LOG_LEVEL))
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Create formatters
        formatter = logging.Formatter(config.LOG_FORMAT)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File Handler with rotation
        log_file = config.LOGS_DIR / f"{name.split('.')[-1]}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10_485_760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Error File Handler
        error_log = config.LOGS_DIR / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log,
            maxBytes=10_485_760,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        
        cls._loggers[name] = logger
        return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return LoggerSetup.get_logger(name)
