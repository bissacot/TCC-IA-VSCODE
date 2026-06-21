import pandas as pd
from src.transform import transform_customers, transform_products, validate_sales


def test_transform_customers_removes_duplicates() -> None:
    df = pd.DataFrame([
        {"customer_id": "C1", "name": "Alice", "email": "alice@example.com", "state": "CA"},
        {"customer_id": "C1", "name": "Alice", "email": "alice@example.com", "state": "CA"},
    ])
    transformed = transform_customers(df)
    assert len(transformed) == 1


def test_transform_products_standardizes_fields() -> None:
    df = pd.DataFrame([
        {"product_id": "P1", "product_name": None, "category": None, "unit_price": "12.34"}
    ])
    transformed = transform_products(df)
    assert transformed.iloc[0]["product_name"] == "Unknown"
    assert transformed.iloc[0]["category"] == "Uncategorized"
    assert transformed.iloc[0]["unit_price"] == 12.34


def test_validate_sales_filters_invalid_rows() -> None:
    df = pd.DataFrame([
        {"sale_id": "S1", "customer_id": "C1", "product_id": "P1", "sale_date": "2026-01-01", "quantity": 2, "unit_price": 10},
        {"sale_id": None, "customer_id": "C2", "product_id": "P2", "sale_date": "invalid", "quantity": -1, "unit_price": 0},
    ])
    valid, invalid = validate_sales(df)
    assert len(valid) == 1
    assert len(invalid) == 1
