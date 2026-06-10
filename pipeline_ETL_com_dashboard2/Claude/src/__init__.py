"""
ETL and Dashboard package initialization.
"""

__version__ = "1.0.0"
__author__ = "Data Engineering Team"
__description__ = "Complete ETL and Dashboard solution for sales analysis"

# Configure package-level logging
from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)
logger.info(f"ETL Dashboard v{__version__} initialized")
