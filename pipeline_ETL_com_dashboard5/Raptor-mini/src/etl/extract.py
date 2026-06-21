from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .api.product_service import fetch_product_data
from .config import Config


def extract_sales() -> pd.DataFrame:
    path = Path(Config.EXTRACT_SALES_FILE)
    return pd.read_csv(path)


def extract_customers() -> pd.DataFrame:
    path = Path(Config.EXTRACT_CUSTOMERS_FILE)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return pd.DataFrame(data)


def extract_products() -> pd.DataFrame:
    products = fetch_product_data(Config.API_BASE_URL)
    if products:
        return pd.DataFrame(products)

    fallback_path = Path(Config.PRODUCTS_FALLBACK_FILE)
    if fallback_path.exists():
        with fallback_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return pd.DataFrame(data)

    return pd.DataFrame()
