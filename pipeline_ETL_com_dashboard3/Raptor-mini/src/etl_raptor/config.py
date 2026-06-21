from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
SALES_CSV_PATH = Path(os.getenv("SALES_CSV_PATH", "data/sales.csv"))
CUSTOMERS_JSON_PATH = Path(os.getenv("CUSTOMERS_JSON_PATH", "data/customers.json"))
PRODUCT_API_URL = os.getenv("PRODUCT_API_URL", "http://localhost:8000/products")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "etl_raptor")
POSTGRES_USER = os.getenv("POSTGRES_USER", "etl_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "etl_password")
ETL_BATCH_SIZE = int(os.getenv("ETL_BATCH_SIZE", "1000"))
ETL_LAST_RUN_FILE = Path(os.getenv("ETL_LAST_RUN_FILE", "data/last_run.txt"))

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("etl_raptor")

@dataclass(frozen=True)
class PostgresConfig:
    host: str = POSTGRES_HOST
    port: int = POSTGRES_PORT
    dbname: str = POSTGRES_DB
    user: str = POSTGRES_USER
    password: str = POSTGRES_PASSWORD

    def dsn(self) -> str:
        return (
            f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
        )

DATABASE_CONFIG = PostgresConfig()
