from __future__ import annotations

import pandas as pd

from src.etl_raptor.transform import (
    standardize_dates,
    validate_and_clean_customers,
    validate_and_clean_products,
    validate_and_clean_sales,
)


def test_standardize_dates() -> None:
    df = pd.DataFrame({"sale_date": ["2024-01-01", "01/02/2024", "2024.03.01"]})
    result = standardize_dates(df, ["sale_date"])
    assert result["sale_date"].tolist() == ["2024-01-01", "2024-01-02", "2024-03-01"]


def test_validate_and_clean_customers() -> None:
    df = pd.DataFrame([
        {"customer_id": 1, "name": "Alice", "state": None},
        {"customer_id": 1, "name": "Alice", "state": "CA"},
    ])
    cleaned = validate_and_clean_customers(df)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["state"] == "Unknown"


def test_validate_and_clean_products() -> None:
    df = pd.DataFrame([
        {"product_id": 1, "name": "Widget", "category": None, "price": 10.0},
        {"product_id": 1, "name": "Widget", "category": "Widgets", "price": 10.0},
    ])
    cleaned = validate_and_clean_products(df)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["category"] == "Unknown"


def test_validate_and_clean_sales() -> None:
    df = pd.DataFrame([
        {"sale_id": 1, "customer_id": 1, "product_id": 1, "sale_date": "2024-01-01", "quantity": 2, "price": 10.0},
        {"sale_id": 2, "customer_id": 1, "product_id": 1, "sale_date": "2024-01-02", "quantity": "invalid", "price": 15.0},
    ])
    cleaned, _ = validate_and_clean_sales(df)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["total_sale_value"] == 20.0
