from __future__ import annotations

import json
from typing import List, Dict, Any
import pandas as pd
import requests
from src.config import settings
from src.utils.logging_config import configure_logging

logger = configure_logging()


def extract_sales_from_csv(path: str = None) -> pd.DataFrame:
    path = path or settings.csv_sales_path
    logger.info(f"Reading sales CSV from {path}")
    df = pd.read_csv(path)
    return df


def extract_customers_from_json(path: str = None) -> List[Dict[str, Any]]:
    path = path or settings.json_customers_path
    logger.info(f"Reading customers JSON from {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def extract_products_from_api(url: str = None) -> List[Dict[str, Any]]:
    url = url or settings.products_api_url
    logger.info(f"Fetching products from API {url}")
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()
