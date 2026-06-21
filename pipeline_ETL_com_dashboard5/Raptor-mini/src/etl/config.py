from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL: str = str(Path().resolve() / "db.sqlite")
    API_BASE_URL: str = "https://api.example.com/products"
    PRODUCTS_FALLBACK_FILE: str = "data/products.json"
    EXTRACT_SALES_FILE: str = "data/sales.csv"
    EXTRACT_CUSTOMERS_FILE: str = "data/customers.json"
    LOG_LEVEL: str = "INFO"

    @classmethod
    def load(cls) -> type["Config"]:
        import os

        cls.DATABASE_URL = os.getenv("DATABASE_URL", cls.DATABASE_URL)
        cls.API_BASE_URL = os.getenv("API_BASE_URL", cls.API_BASE_URL)
        cls.PRODUCTS_FALLBACK_FILE = os.getenv("PRODUCTS_FALLBACK_FILE", cls.PRODUCTS_FALLBACK_FILE)
        cls.EXTRACT_SALES_FILE = os.getenv("EXTRACT_SALES_FILE", cls.EXTRACT_SALES_FILE)
        cls.EXTRACT_CUSTOMERS_FILE = os.getenv("EXTRACT_CUSTOMERS_FILE", cls.EXTRACT_CUSTOMERS_FILE)
        cls.LOG_LEVEL = os.getenv("LOG_LEVEL", cls.LOG_LEVEL)
        return cls
