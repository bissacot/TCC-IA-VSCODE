from __future__ import annotations

import pandas as pd

from src.etl.transform import transform_customers, transform_products, transform_sales


def test_transform_customers_removes_invalid_records() -> None:
    data = [{"id": "C1", "name": "Acme", "created_at": "2024-01-01"}, {"id": "", "name": "Missing"}]
    df = pd.DataFrame(data)
    cleaned, metrics = transform_customers(df)
    assert metrics["processed_records"] == 1
    assert cleaned.iloc[0]["customer_id"] == "C1"


def test_transform_products_converts_price() -> None:
    data = [{"id": "P1", "name": "Widget", "price": "12.5", "created_at": "2024-01-01"}, {"id": "P2", "name": "Gadget", "price": "abc"}]
    df = pd.DataFrame(data)
    cleaned, metrics = transform_products(df)
    assert metrics["processed_records"] == 1
    assert float(cleaned.iloc[0]["price"]) == 12.5


def test_transform_sales_computes_total_value() -> None:
    sales_data = [{"id": "S1", "date": "2024-01-13", "customerId": "C1", "productId": "P1", "qty": 2, "price": 10}]
    customers = pd.DataFrame([{"customer_id": "C1", "customer_name": "Acme", "state": "NY"}])
    products = pd.DataFrame([{"product_id": "P1", "product_name": "Widget", "category": "Tools"}])
    sales, metrics = transform_sales(pd.DataFrame(sales_data), customers, products)
    assert metrics["processed_records"] == 1
    assert sales.iloc[0]["total_value"] == 20
