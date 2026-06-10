from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from .config import settings
from .exceptions import ExtractionException
from .logger import get_logger

logger = get_logger(__name__)


def extract_sales(csv_path: Path | str = settings.sales_csv_path) -> pd.DataFrame:
    try:
        logger.info("Extracting sales data from %s", csv_path)
        df = pd.read_csv(csv_path, dtype=str)
        return df
    except Exception as error:
        logger.exception("Failed to extract sales data")
        raise ExtractionException(error)


def extract_customers(json_path: Path | str = settings.customer_json_path) -> pd.DataFrame:
    try:
        logger.info("Extracting customer data from %s", json_path)
        with open(json_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if isinstance(payload, dict):
            payload = payload.get("customers", [])

        return pd.DataFrame(payload)
    except Exception as error:
        logger.exception("Failed to extract customer data")
        raise ExtractionException(error)


def extract_products(api_url: str = settings.product_api_url) -> pd.DataFrame:
    try:
        logger.info("Extracting product data from API %s", api_url)
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        payload = response.json()

        if isinstance(payload, dict) and "products" in payload:
            payload = payload["products"]

        if not isinstance(payload, list):
            raise ExtractionException("Product API response is not a list")

        return pd.DataFrame(payload)
    except Exception as error:
        logger.exception("Failed to extract product data")
        raise ExtractionException(error)
