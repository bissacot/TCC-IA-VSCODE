from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    database_host: str = os.getenv("DATABASE_HOST", "localhost")
    database_port: int = int(os.getenv("DATABASE_PORT", "5432"))
    database_name: str = os.getenv("DATABASE_NAME", "salesdb")
    database_user: str = os.getenv("DATABASE_USER", "sales_user")
    database_password: str = os.getenv("DATABASE_PASSWORD", "sales_password")
    sales_csv_path: Path = Path(os.getenv("SALES_CSV_PATH", "data/sample_sales.csv"))
    customer_json_path: Path = Path(os.getenv("CUSTOMER_JSON_PATH", "data/sample_customers.json"))
    product_api_url: str = os.getenv("PRODUCT_API_URL", "http://localhost:5000/api/products")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    last_processed_file: Path = Path(os.getenv("LAST_PROCESSED_FILE", "data/last_processed_timestamp.txt"))

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.database_user}:{self.database_password}@"
            f"{self.database_host}:{self.database_port}/{self.database_name}"
        )

settings = Settings()
