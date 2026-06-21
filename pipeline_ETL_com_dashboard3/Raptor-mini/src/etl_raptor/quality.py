from __future__ import annotations

import pandas as pd


def build_quality_report(
    sales: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    original_sales_count: int,
    invalid_sales_count: int,
    duplicate_count: int,
) -> dict[str, object]:
    missing_sales = sales.isna().sum().sum()
    missing_customers = customers.isna().sum().sum()
    missing_products = products.isna().sum().sum()
    total_cells = (
        len(sales) * sales.shape[1]
        + len(customers) * customers.shape[1]
        + len(products) * products.shape[1]
    )
    missing_percent = 0.0
    if total_cells > 0:
        missing_percent = (missing_sales + missing_customers + missing_products) / total_cells * 100

    return {
        "processed_records": len(sales) + len(customers) + len(products),
        "invalid_records": invalid_sales_count,
        "duplicates_removed": duplicate_count,
        "missing_values_percent": round(missing_percent, 2),
    }
