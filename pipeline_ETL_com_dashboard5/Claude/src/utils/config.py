"""
Configuration management for the ETL pipeline.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
ENV_FILE = Path(__file__).parent.parent.parent / '.env'
load_dotenv(ENV_FILE)


class Config:
    """Configuration class for ETL pipeline."""

    # Database Configuration
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '5432'))
    DB_NAME: str = os.getenv('DB_NAME', 'sales_etl_db')
    DB_USER: str = os.getenv('DB_USER', 'etl_user')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    DB_SCHEMA: str = os.getenv('DB_SCHEMA', 'public')

    # API Configuration
    API_BASE_URL: str = os.getenv('API_BASE_URL', 'https://api.example.com')
    API_TIMEOUT: int = int(os.getenv('API_TIMEOUT', '30'))
    API_RETRY_ATTEMPTS: int = int(os.getenv('API_RETRY_ATTEMPTS', '3'))

    # Data Paths
    CSV_SALES_PATH: str = os.getenv('CSV_SALES_PATH', 'data/input/sales.csv')
    JSON_CUSTOMERS_PATH: str = os.getenv('JSON_CUSTOMERS_PATH', 'data/input/customers.json')
    API_PRODUCTS_ENDPOINT: str = os.getenv('API_PRODUCTS_ENDPOINT', '/api/v1/products')

    # Processing Configuration
    BATCH_SIZE: int = int(os.getenv('BATCH_SIZE', '1000'))
    CHUNK_SIZE: int = int(os.getenv('CHUNK_SIZE', '10000'))
    INCREMENTAL_MODE: bool = os.getenv('INCREMENTAL_MODE', 'true').lower() == 'true'
    LAST_RUN_TIMESTAMP_FILE: str = os.getenv('LAST_RUN_TIMESTAMP_FILE', 'data/.last_run')

    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/etl.log')

    # Dashboard Configuration
    DASHBOARD_PORT: int = int(os.getenv('DASHBOARD_PORT', '8501'))
    DASHBOARD_HOST: str = os.getenv('DASHBOARD_HOST', '0.0.0.0')

    # Report Configuration
    REPORT_OUTPUT_DIR: str = os.getenv('REPORT_OUTPUT_DIR', 'data/output/reports')
    EXCEL_EXPORT_DIR: str = os.getenv('EXCEL_EXPORT_DIR', 'data/output/exports')
    PDF_REPORT_ENABLED: bool = os.getenv('PDF_REPORT_ENABLED', 'true').lower() == 'true'

    # Environment
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'

    @classmethod
    def get_database_url(cls) -> str:
        """Get PostgreSQL connection URL."""
        return (
            f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@"
            f"{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist."""
        directories = [
            Path(cls.REPORT_OUTPUT_DIR),
            Path(cls.EXCEL_EXPORT_DIR),
            Path(cls.LOG_FILE).parent,
            Path(cls.CSV_SALES_PATH).parent,
            Path(cls.JSON_CUSTOMERS_PATH).parent,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
