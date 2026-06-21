from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pandas as pd

from .config import PRODUCT_API_URL, SALES_CSV_PATH, CUSTOMERS_JSON_PATH, logger


def extract_sales(csv_path: Path = SALES_CSV_PATH) -> pd.DataFrame:
    logger.info("Extracting sales data from CSV %s", csv_path)
    return pd.read_csv(csv_path)


def extract_customers(json_path: Path = CUSTOMERS_JSON_PATH) -> pd.DataFrame:
    logger.info("Extracting customer data from JSON %s", json_path)
    with open(json_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return pd.DataFrame(data)


def extract_products(api_url: str = PRODUCT_API_URL) -> pd.DataFrame:
    logger.info("Fetching product data from API %s", api_url)
    with httpx.Client(timeout=30) as client:
        response = client.get(api_url)
        response.raise_for_status()
        results = response.json()
    return pd.DataFrame(results)
