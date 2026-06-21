from typing import Tuple
import pandas as pd
import json
import requests
from .config import get_settings
from .logger import logger


def extract_sales() -> pd.DataFrame:
    settings = get_settings()
    logger.info(f"Reading sales CSV: {settings.csv_sales_file}")
    df = pd.read_csv(settings.csv_sales_file)
    return df


def extract_customers() -> pd.DataFrame:
    settings = get_settings()
    logger.info(f"Reading customers JSON: {settings.json_customers_file}")
    with open(settings.json_customers_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return pd.DataFrame(data)


def extract_products() -> pd.DataFrame:
    settings = get_settings()
    url = settings.products_api_url
    logger.info(f"Fetching products from API: {url}")
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return pd.DataFrame(data)
