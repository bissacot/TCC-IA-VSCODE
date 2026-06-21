from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


def fetch_product_data(api_base_url: str, timeout: int = 15) -> list[dict[str, Any]]:
    try:
        response = requests.get(api_base_url, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict) and "products" in payload:
            payload = payload["products"]
        if not isinstance(payload, list):
            raise ValueError("Unexpected product payload format")
        return payload
    except Exception as error:
        logger.warning("Product API failed, returning empty list: %s", error)
        return []
