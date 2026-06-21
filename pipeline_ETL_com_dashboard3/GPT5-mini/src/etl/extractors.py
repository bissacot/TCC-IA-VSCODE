import pandas as pd
import json
from typing import Tuple
from .config import settings
import logging
from .api_client import fetch_products

logger = logging.getLogger("sales_etl.extractors")


def extract_sales_csv(path: str = None) -> pd.DataFrame:
    path = path or settings.SALES_CSV
    df = pd.read_csv(path)
    logger.info("Extracted %d sales rows from CSV", len(df))
    return df


def extract_customers_json(path: str = None) -> pd.DataFrame:
    path = path or settings.CUSTOMERS_JSON
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    df = pd.DataFrame(data)
    logger.info("Extracted %d customers from JSON", len(df))
    return df


def extract_products_api() -> pd.DataFrame:
    products = fetch_products()
    df = pd.DataFrame(products)
    logger.info("Extracted %d products from API", len(df))
    return df
