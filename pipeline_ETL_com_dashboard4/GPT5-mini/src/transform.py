from typing import Tuple
import pandas as pd
import numpy as np
from datetime import datetime
from .logger import logger


def standardize_date(series: pd.Series) -> pd.Series:
    def parse(v):
        if pd.isna(v):
            return pd.NaT
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", None):
            try:
                if fmt:
                    return pd.to_datetime(v, format=fmt)
                return pd.to_datetime(v, errors='coerce')
            except Exception:
                continue
        return pd.NaT

    return series.map(parse)


def transform_sales(sales: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    report = {}
    before = len(sales)
    # Drop exact duplicates
    sales = sales.drop_duplicates()
    after_dedup = len(sales)
    report['duplicates_removed'] = before - after_dedup

    # Standardize date
    if 'sale_date' in sales.columns:
        sales['sale_date'] = standardize_date(sales['sale_date'])

    # Ensure numeric fields
    for col in ['quantity', 'unit_price']:
        if col in sales.columns:
            sales[col] = pd.to_numeric(sales[col], errors='coerce')

    # Derived metrics
    sales['quantity'] = sales['quantity'].fillna(1).astype(int)
    sales['unit_price'] = sales['unit_price'].fillna(0.0)
    sales['total_value'] = sales['quantity'] * sales['unit_price']

    # Year, month, quarter
    sales['year'] = sales['sale_date'].dt.year
    sales['month'] = sales['sale_date'].dt.month
    sales['quarter'] = sales['sale_date'].dt.quarter

    # Missing values report
    missing = sales.isna().sum().to_dict()
    report['missing_values'] = missing
    report['processed_records'] = len(sales)

    # Simple invalid records (missing essential fields)
    invalid_mask = sales['sale_date'].isna() | sales['customer_id'].isna() | sales['product_id'].isna()
    invalid_count = int(invalid_mask.sum())
    report['invalid_records'] = invalid_count

    sales_valid = sales[~invalid_mask].copy()

    return sales_valid, report
