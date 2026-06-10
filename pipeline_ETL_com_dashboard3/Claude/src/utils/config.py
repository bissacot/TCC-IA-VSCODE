"""Configuration management."""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import json


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str
    port: int
    database: str
    user: str
    password: str
    
    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class APIConfig:
    """REST API configuration."""
    base_url: str
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 5


@dataclass
class ETLConfig:
    """ETL configuration."""
    csv_path: str
    json_path: str
    api_config: APIConfig
    db_config: DatabaseConfig
    batch_size: int = 1000
    log_level: str = "INFO"
    incremental: bool = False


def load_config_from_env() -> ETLConfig:
    """Load configuration from environment variables."""
    db_config = DatabaseConfig(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "sales_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "password")
    )
    
    api_config = APIConfig(
        base_url=os.getenv("API_BASE_URL", "https://api.example.com"),
        timeout=int(os.getenv("API_TIMEOUT", "30")),
        retry_attempts=int(os.getenv("API_RETRY_ATTEMPTS", "3")),
        retry_delay=int(os.getenv("API_RETRY_DELAY", "5"))
    )
    
    return ETLConfig(
        csv_path=os.getenv("CSV_PATH", "data/input/sales.csv"),
        json_path=os.getenv("JSON_PATH", "data/input/customers.json"),
        api_config=api_config,
        db_config=db_config,
        batch_size=int(os.getenv("BATCH_SIZE", "1000")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        incremental=os.getenv("INCREMENTAL", "false").lower() == "true"
    )


def load_config_from_file(config_file: str) -> ETLConfig:
    """Load configuration from JSON file."""
    with open(config_file, 'r') as f:
        config_dict = json.load(f)
    
    db_config = DatabaseConfig(**config_dict['database'])
    api_config = APIConfig(**config_dict['api'])
    
    return ETLConfig(
        csv_path=config_dict['csv_path'],
        json_path=config_dict['json_path'],
        api_config=api_config,
        db_config=db_config,
        batch_size=config_dict.get('batch_size', 1000),
        log_level=config_dict.get('log_level', 'INFO'),
        incremental=config_dict.get('incremental', False)
    )
