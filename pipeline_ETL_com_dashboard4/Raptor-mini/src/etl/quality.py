from __future__ import annotations

import pandas as pd


def calculate_quality_report(
    sales_df: pd.DataFrame, customers_df: pd.DataFrame, products_df: pd.DataFrame
) -> dict[str, object]:
    datasets = {
        "sales": sales_df,
        "customers": customers_df,
        "products": products_df,
    }
    report: dict[str, object] = {}

    for name, df in datasets.items():
        total_rows = len(df)
        duplicate_rows = df.duplicated().sum()
        missing_percentage = float(df.isna().sum().sum()) / (df.size or 1) * 100
        invalid_rows = df.isnull().any(axis=1).sum()

        report[name] = {
            "processed_records": total_rows,
            "invalid_records": int(invalid_rows),
            "duplicates_removed": int(duplicate_rows),
            "missing_percentage": round(missing_percentage, 2),
        }

    return report
