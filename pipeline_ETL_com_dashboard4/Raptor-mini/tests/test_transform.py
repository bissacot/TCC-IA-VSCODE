from __future__ import annotations

import pandas as pd

from etl.transform import clean_sales_data, validate_data_types


def test_clean_sales_data_creates_derived_fields() -> None:
    df = pd.DataFrame(
        {
            "sale_id": ["1"],
            "sale_date": ["2024-01-01"],
            "customer_id": ["C1"],
            "product_id": ["P1"],
            "quantity": [2],
            "unit_price": [10.5],
        }
    )

    cleaned = clean_sales_data(df)

    assert cleaned["total_sale_value"].iloc[0] == 21.0
    assert cleaned["year"].iloc[0] == 2024
    assert cleaned["month"].iloc[0] == 1
    assert cleaned["quarter"].iloc[0] == 1


def test_validate_data_types_casts_values() -> None:
    df = pd.DataFrame(
        {
            "sale_id": ["1"],
            "quantity": ["3"],
            "unit_price": ["4.5"],
        }
    )

    validated = validate_data_types(df, {"quantity": float, "unit_price": float})

    assert validated["quantity"].dtype == float
    assert validated["unit_price"].dtype == float
