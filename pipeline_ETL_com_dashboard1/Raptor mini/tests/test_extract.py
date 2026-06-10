from pathlib import Path

import pandas as pd

from src.etl_app.extract import extract_customers, extract_sales


def test_extract_sales_sample():
    sample_path = Path(__file__).resolve().parents[1] / "data" / "sample_sales.csv"
    df = extract_sales(sample_path)
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 10
    assert "sale_id" in df.columns


def test_extract_customers_sample():
    sample_path = Path(__file__).resolve().parents[1] / "data" / "sample_customers.json"
    df = extract_customers(sample_path)
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 7
    assert "customer_id" in df.columns
