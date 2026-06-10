from __future__ import annotations

import json
from typing import Any
import pandas as pd
import requests
from loguru import logger

from app.utils.config import settings


def extract_sales_csv(path: str | None = None) -> pd.DataFrame:
    path = path or settings.SALES_CSV
    logger.info("Extracting sales CSV from {}", path)
    df = pd.read_csv(path)
    return df


def extract_customers_json(path: str | None = None) -> pd.DataFrame:
    path = path or settings.CUSTOMERS_JSON
    logger.info("Extracting customers JSON from {}", path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.json_normalize(data)
    return df


def extract_products_api(api_url: str | None = None) -> pd.DataFrame:
    api_url = api_url or settings.API_URL
    logger.info("Fetching products from API {}", api_url)
    resp = requests.get(api_url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    df = pd.json_normalize(data)
    return df
