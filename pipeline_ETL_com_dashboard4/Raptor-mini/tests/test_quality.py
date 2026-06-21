from __future__ import annotations

import pandas as pd

from etl.quality import calculate_quality_report


def test_calculate_quality_report_counts() -> None:
    sales = pd.DataFrame(
        {
            "sale_id": ["1", "1"],
            "sale_date": ["2024-01-01", "2024-01-01"],
            "customer_id": ["C1", "C1"],
            "product_id": ["P1", "P1"],
            "quantity": [2, 2],
            "unit_price": [10.0, 10.0],
        }
    )
    customers = pd.DataFrame(
        {"customer_id": ["C1"], "customer_name": ["Alice"], "email": ["alice@example.com"], "state": ["CA"]}
    )
    products = pd.DataFrame(
        {"product_id": ["P1"], "product_name": ["Widget"], "category": ["Tools"], "price": [10.0]}
    )

    report = calculate_quality_report(sales, customers, products)

    assert report["sales"]["processed_records"] == 2
    assert report["sales"]["duplicates_removed"] == 1
    assert report["customers"]["processed_records"] == 1
