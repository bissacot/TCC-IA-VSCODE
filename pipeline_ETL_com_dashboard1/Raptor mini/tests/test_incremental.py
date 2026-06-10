from datetime import datetime

import pandas as pd

from src.etl_app.incremental import filter_incremental_sales


def test_filter_incremental_sales_uses_timestamp():
    data = pd.DataFrame(
        {
            "sale_id": ["S1", "S2", "S3"],
            "sale_date": [
                pd.Timestamp("2024-01-01"),
                pd.Timestamp("2024-02-01"),
                pd.Timestamp("2024-03-01"),
            ],
        }
    )
    last_run = datetime(2024, 2, 1)
    filtered = filter_incremental_sales(data, last_run)
    assert len(filtered) == 1
    assert filtered.iloc[0]["sale_id"] == "S3"
