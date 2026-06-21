from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from .config import Settings
from .logger import get_logger

logger = get_logger(__name__)


def load_sales_csv(path: Path) -> pd.DataFrame:
    logger.info("Loading sales data from CSV: %s", path)
    return pd.read_csv(path)


def load_customers_json(path: Path) -> pd.DataFrame:
    logger.info("Loading customer data from JSON: %s", path)
    with open(path, "r", encoding="utf-8") as buffer:
        data = json.load(buffer)
    return pd.json_normalize(data)


def fetch_products_api(config: Settings) -> pd.DataFrame:
    logger.info("Fetching product data from API: %s", config.product_api_url)
    response = requests.get(config.product_api_url, timeout=20)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict) and "products" in data:
        data = data["products"]
    return pd.json_normalize(data)


def extract_data(config: Settings) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sales_df = load_sales_csv(config.source_csv_path)
    customers_df = load_customers_json(config.source_json_path)
    products_df = fetch_products_api(config)
    return sales_df, customers_df, products_df
