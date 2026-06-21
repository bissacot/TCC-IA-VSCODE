import pandas as pd
from src.etl.transform import transform_sales


def test_transform_sales_basic():
    df = pd.DataFrame([
        {"sale_id": "S1", "quantity": 2, "unit_price": 10, "sale_date": "2023-01-05", "customer_id": "C1", "product_id": "P1"},
        {"sale_id": "S2", "quantity": 1, "unit_price": 20, "sale_date": "2023-02-10", "customer_id": "C2", "product_id": "P2"},
    ])
    transformed, report = transform_sales(df)
    assert report["processed"] == 2
    assert "total_value" in transformed.columns
