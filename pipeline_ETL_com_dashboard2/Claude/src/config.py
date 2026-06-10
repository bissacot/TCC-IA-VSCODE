"""
Configuration management for ETL and Dashboard application.
Handles environment variables and default configurations.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "data"
LOGS_DIR: Path = BASE_DIR / "logs"
REPORTS_DIR: Path = BASE_DIR / "reports"
SQL_DIR: Path = BASE_DIR / "sql"

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class DatabaseConfig:
    """Database configuration."""

    HOST: str = os.getenv("DB_HOST", "localhost")
    PORT: int = int(os.getenv("DB_PORT", 5432))
    NAME: str = os.getenv("DB_NAME", "sales_db")
    USER: str = os.getenv("DB_USER", "etl_user")
    PASSWORD: str = os.getenv("DB_PASSWORD", "secure_password_here")

    @property
    def connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return (
            f"postgresql://{self.USER}:{self.PASSWORD}@"
            f"{self.HOST}:{self.PORT}/{self.NAME}"
        )

    @property
    def engine_url(self) -> str:
        """Generate SQLAlchemy engine URL."""
        return self.connection_string


class APIConfig:
    """API configuration."""

    BASE_URL: str = os.getenv("API_BASE_URL", "https://api.example.com")
    API_KEY: str = os.getenv("API_KEY", "your_api_key_here")
    TIMEOUT: int = int(os.getenv("API_TIMEOUT", 30))


class LoggingConfig:
    """Logging configuration."""

    LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    FILE: Path = LOGS_DIR / "etl.log"
    FORMAT: str = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "[%(filename)s:%(lineno)d] - %(message)s"
    )


class ETLConfig:
    """ETL configuration."""

    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", 1000))
    INCREMENTAL_MODE: bool = os.getenv("INCREMENTAL_MODE", "true").lower() == "true"
    LAST_RUN_FILE: Path = BASE_DIR / os.getenv("LAST_RUN_FILE", "data/last_run.txt")


class SchedulerConfig:
    """Scheduler configuration."""

    SCHEDULE_INTERVAL: str = os.getenv("SCHEDULE_INTERVAL", "daily")
    SCHEDULE_TIME: str = os.getenv("SCHEDULE_TIME", "02:00")
    TIMEZONE: str = "UTC"


class DashboardConfig:
    """Dashboard configuration."""

    PORT: int = int(os.getenv("DASHBOARD_PORT", 8501))
    DEBUG: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"


class EmailConfig:
    """Email configuration for reports."""

    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
    SENDER_PASSWORD: str = os.getenv("SENDER_PASSWORD", "your_app_password")
    RECIPIENTS: list[str] = (
        os.getenv("REPORT_RECIPIENTS", "admin@example.com").split(",")
    )


# Consolidated configuration object
config = {
    "database": DatabaseConfig,
    "api": APIConfig,
    "logging": LoggingConfig,
    "etl": ETLConfig,
    "scheduler": SchedulerConfig,
    "dashboard": DashboardConfig,
    "email": EmailConfig,
}
