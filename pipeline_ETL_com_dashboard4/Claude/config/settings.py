"""
Configuration settings for the sales ETL dashboard application.

This module loads configuration from environment variables and provides
centralized access to application settings.
"""

import os
from typing import Final
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT: Final[Path] = Path(__file__).parent.parent
DATA_PATH: Final[Path] = PROJECT_ROOT / "data"
REPORTS_PATH: Final[Path] = PROJECT_ROOT / "reports"
LOGS_PATH: Final[Path] = PROJECT_ROOT / "logs"
SQL_PATH: Final[Path] = PROJECT_ROOT / "sql"

# Ensure directories exist
DATA_PATH.mkdir(exist_ok=True)
REPORTS_PATH.mkdir(exist_ok=True)
LOGS_PATH.mkdir(exist_ok=True)

# Database Configuration
DB_HOST: Final[str] = os.getenv("DB_HOST", "localhost")
DB_PORT: Final[int] = int(os.getenv("DB_PORT", 5432))
DB_NAME: Final[str] = os.getenv("DB_NAME", "sales_etl_db")
DB_USER: Final[str] = os.getenv("DB_USER", "postgres")
DB_PASSWORD: Final[str] = os.getenv("DB_PASSWORD", "postgres")
DB_URL: Final[str] = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# API Configuration
API_BASE_URL: Final[str] = os.getenv("API_BASE_URL", "https://api.example.com")
API_TIMEOUT: Final[int] = int(os.getenv("API_TIMEOUT", 30))

# Logging Configuration
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: Final[str] = (
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOG_FILE: Final[Path] = LOGS_PATH / "etl.log"

# ETL Settings
BATCH_SIZE: Final[int] = int(os.getenv("BATCH_SIZE", 1000))
INCREMENTAL_PROCESSING: Final[bool] = (
    os.getenv("INCREMENTAL_PROCESSING", "true").lower() == "true"
)

# Scheduler
SCHEDULE_INTERVAL: Final[str] = os.getenv("SCHEDULE_INTERVAL", "0 2 * * *")

# Dashboard Settings
DASHBOARD_PORT: Final[int] = int(os.getenv("DASHBOARD_PORT", 8501))
DASHBOARD_HOST: Final[str] = os.getenv("DASHBOARD_HOST", "0.0.0.0")

# Data Quality Thresholds
MAX_MISSING_PERCENTAGE: Final[float] = 30.0
MIN_RECORD_COUNT: Final[int] = 100

# Date Format
DATE_FORMAT: Final[str] = "%Y-%m-%d"
ISO_DATE_FORMAT: Final[str] = "%Y-%m-%d"

# Source Files
SALES_CSV_PATH: Final[Path] = DATA_PATH / "sales.csv"
CUSTOMERS_JSON_PATH: Final[Path] = DATA_PATH / "customers.json"
PRODUCTS_API_ENDPOINT: Final[str] = f"{API_BASE_URL}/products"
