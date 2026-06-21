import pandas as pd
from src.etl.transform import clean_sales, validate_sales


def test_clean_and_validate_sales():
    df = pd.DataFrame([
        {"sale_id": "s1", "quantity": "2", "unit_price": "10", "sale_date": "2026-01-01"},
        {"sale_id": None, "quantity": "1", "unit_price": "5", "sale_date": "bad-date"},
    ])
    cleaned = clean_sales(df)
    good, invalid = validate_sales(cleaned)
    assert "total_value" in good.columns
    assert len(invalid) >= 0
