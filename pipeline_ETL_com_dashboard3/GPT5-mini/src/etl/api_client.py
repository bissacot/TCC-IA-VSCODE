import requests
import logging
from typing import List, Dict, Any
from .config import settings

logger = logging.getLogger("sales_etl.api")


def fetch_products() -> List[Dict[str, Any]]:
    url = str(settings.PRODUCTS_API_URL) if settings.PRODUCTS_API_URL else None
    if not url:
        logger.warning("No PRODUCTS_API_URL configured; returning empty product list")
        return []
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    # Expecting a list of product dicts
    return data
