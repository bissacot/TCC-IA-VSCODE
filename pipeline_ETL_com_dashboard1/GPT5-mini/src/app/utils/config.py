from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "salesdb")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    API_URL: str = os.getenv("API_URL", "http://localhost:8000/products")
    SALES_CSV: str = os.getenv("SALES_CSV", "./data/sales.csv")
    CUSTOMERS_JSON: str = os.getenv("CUSTOMERS_JSON", "./data/customers.json")


settings = Settings()
