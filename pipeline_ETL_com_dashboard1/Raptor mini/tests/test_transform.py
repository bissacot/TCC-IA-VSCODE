import pandas as pd

from src.etl_app.transform import transform_sales


def test_transform_sales_derived_metrics():
    df = pd.DataFrame(
        [
            {
                "sale_id": "S100",
                "customer_id": "C100",
                "product_id": "P100",
                "sale_date": "2024-07-01",
                "quantity": "3",
                "unit_price": "10.5",
                "state": "ca",
            }
        ]
    )
    valid, invalid_count, duplicates_removed = transform_sales(df)
    assert invalid_count == 0
    assert duplicates_removed == 0
    assert valid.iloc[0]["total_sale_value"] == 31.5
    assert valid.iloc[0]["year"] == 2024
    assert valid.iloc[0]["month"] == 7
    assert valid.iloc[0]["quarter"] == 3
    assert valid.iloc[0]["state"] == "Ca"
