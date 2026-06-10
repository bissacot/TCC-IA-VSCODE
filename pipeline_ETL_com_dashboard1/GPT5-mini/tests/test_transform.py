from app.etl.transform import clean_sales
import pandas as pd


def test_clean_sales():
    df = pd.DataFrame([
        {"sale_id": "S1", "customer_id": "C1", "product_id": "P1", "quantity": 2, "price": 10.0, "sale_date": "2023-01-01 10:00:00", "state": "CA"},
        {"sale_id": "S2", "customer_id": "C2", "product_id": "P2", "quantity": 1, "price": 20.0, "sale_date": "invalid", "state": "NY"},
    ])
    cleaned, report = clean_sales(df)
    assert report["initial_records"] == 2
    assert report["invalid_records"] == 1
    assert len(cleaned) == 1
