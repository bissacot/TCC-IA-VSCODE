from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    postgres_url: str = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/salesdb")
    csv_sales_path: str = os.getenv("CSV_SALES_PATH", "data/sales.csv")
    json_customers_path: str = os.getenv("JSON_CUSTOMERS_PATH", "data/customers.json")
    products_api_url: str = os.getenv("PRODUCTS_API_URL", "http://localhost:5000/products")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    etl_batch_size: int = int(os.getenv("ETL_BATCH_SIZE", "1000"))
    last_processed_key: str = os.getenv("LAST_PROCESSED_KEY", "last_processed")


settings = Settings()
