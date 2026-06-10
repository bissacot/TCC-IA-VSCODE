"""
Application Configuration Management
Centralized configuration using environment variables with defaults
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    
    # Project
    PROJECT_NAME: str = "ETL Pipeline Dashboard"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "etl_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "etl_password")
    DB_NAME: str = os.getenv("DB_NAME", "sales_db")
    
    # Database Connection String
    @classmethod
    def get_database_url(cls) -> str:
        """Get SQLAlchemy database URL"""
        return (
            f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@"
            f"{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )
    
    # API Configuration
    PRODUCT_API_URL: str = os.getenv(
        "PRODUCT_API_URL",
        "https://jsonplaceholder.typicode.com/products"
    )
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    API_RETRIES: int = int(os.getenv("API_RETRIES", "3"))
    
    # ETL Configuration
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "1000"))
    INCREMENTAL_LOAD: bool = os.getenv("INCREMENTAL_LOAD", "True").lower() == "true"
    ALLOWED_DUPLICATES: int = int(os.getenv("ALLOWED_DUPLICATES", "0"))
    
    # File Paths for Data Sources
    CSV_SALES_PATH: Path = DATA_DIR / os.getenv("CSV_SALES_FILE", "sales_data.csv")
    JSON_CUSTOMERS_PATH: Path = DATA_DIR / os.getenv("JSON_CUSTOMERS_FILE", "customers.json")
    
    # Dashboard
    DASHBOARD_PORT: int = int(os.getenv("DASHBOARD_PORT", "8501"))
    DASHBOARD_MAX_UPLOAD_SIZE: int = int(os.getenv("DASHBOARD_MAX_UPLOAD_SIZE", "200"))
    
    # Report Generation
    REPORTS_FORMAT: str = os.getenv("REPORTS_FORMAT", "pdf,excel")  # comma-separated
    PDF_ORIENTATION: str = os.getenv("PDF_ORIENTATION", "portrait")
    
    # Scheduling
    SCHEDULE_INTERVAL: str = os.getenv("SCHEDULE_INTERVAL", "0 2 * * *")  # 2 AM daily
    
    # Performance
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    
    # Data Quality Thresholds
    MISSING_VALUE_THRESHOLD: float = float(os.getenv("MISSING_VALUE_THRESHOLD", "0.1"))  # 10%
    DUPLICATE_THRESHOLD: float = float(os.getenv("DUPLICATE_THRESHOLD", "0.05"))  # 5%
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist"""
        for directory in [cls.DATA_DIR, cls.LOGS_DIR, cls.REPORTS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith("_") and key.isupper()
        }
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_vars = [
            "DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"
        ]
        
        missing = [var for var in required_vars if not getattr(cls, var, None)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
        
        return True


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    DB_NAME = "test_sales_db"
    CACHE_ENABLED = False


def get_config() -> Config:
    """Get appropriate configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)()


# Export configuration instance
config = get_config()

# Ensure directories exist
config.ensure_directories()
