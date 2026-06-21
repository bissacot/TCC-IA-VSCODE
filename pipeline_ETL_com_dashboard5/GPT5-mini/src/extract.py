from typing import Tuple
import pandas as pd
import json
import requests
from .config import settings
from .logger import get_logger

logger = get_logger(__name__)


def extract_sales_from_csv(path: str = None) -> pd.DataFrame:
    path = path or settings.csv_path
    logger.info('Reading sales CSV from %s', path)
    df = pd.read_csv(path)
    return df


def extract_customers_from_json(path: str = None) -> pd.DataFrame:
    path = path or settings.customers_json
    logger.info('Reading customers JSON from %s', path)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.json_normalize(data)
    return df


def extract_products_from_api(url: str = None) -> pd.DataFrame:
    url = url or settings.products_api_url
    logger.info('Fetching products from API %s', url)
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    df = pd.json_normalize(data)
    return df
