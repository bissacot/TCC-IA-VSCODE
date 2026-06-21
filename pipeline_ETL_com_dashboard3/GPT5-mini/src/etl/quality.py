import pandas as pd
from typing import Dict, Any


def generate_quality_report(sales_df: pd.DataFrame, invalid_df: pd.DataFrame, before_count: int, duplicates_removed: int) -> Dict[str, Any]:
    total = before_count
    processed = len(sales_df)
    invalid = len(invalid_df)
    missing_pct = sales_df.isna().mean().to_dict()
    return {
        "total_records": total,
        "processed_records": processed,
        "invalid_records": invalid,
        "duplicates_removed": duplicates_removed,
        "missing_percentage_by_column": missing_pct,
    }
