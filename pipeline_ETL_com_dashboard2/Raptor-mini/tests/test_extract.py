import json
import pandas as pd
from pathlib import Path
from src.extract import extract_customers, extract_sales, extract_products
from unittest.mock import patch, mock_open


def test_extract_customers_from_json(tmp_path):
    data = [{"customer_id": "C1", "name": "Alice", "email": "alice@example.com", "state": "CA"}]
    file_path = tmp_path / "customers.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    with patch("src.config.settings.customers_json_path", str(file_path)):
        df = extract_customers()
    assert len(df) == 1
    assert df.iloc[0]["customer_id"] == "C1"
