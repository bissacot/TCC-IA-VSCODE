import json
from typing import Any
import pandas as pd
import requests
from src.config import settings
from src.logger import logger


def extract_sales() -> pd.DataFrame:
    try:
        df = pd.read_csv(settings.sales_csv_path)
        logger.info("Extracted %d sales records from CSV", len(df))
        return df
    except Exception as exc:
        logger.exception("Failed to extract sales CSV")
        raise


def extract_customers() -> pd.DataFrame:
    try:
        with open(settings.customers_json_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        df = pd.DataFrame(data)
        logger.info("Extracted %d customer records from JSON", len(df))
        return df
    except Exception as exc:
        logger.exception("Failed to extract customers JSON")
        raise


def extract_products() -> pd.DataFrame:
    try:
        response = requests.get(settings.product_api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        logger.info("Extracted %d product records from API", len(df))
        return df
    except Exception as exc:
        logger.exception("Failed to extract products from API")
        raise
