from typing import Tuple
import pandas as pd
from .logger import get_logger

logger = get_logger(__name__)


def transform_sales(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    original = len(df)
    # Standardize column names
    df = df.rename(columns=lambda x: x.strip())

    # Convert dates
    if 'sale_date' in df.columns:
        df['sale_date'] = pd.to_datetime(df['sale_date'], errors='coerce')
        df['sale_date'] = df['sale_date'].dt.strftime('%Y-%m-%d')
    # Numeric conversions
    for col in ['quantity', 'unit_price']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Derived fields
    if 'quantity' in df.columns and 'unit_price' in df.columns:
        df['total_value'] = df['quantity'] * df['unit_price']
    else:
        df['total_value'] = pd.NA

    # Date parts
    try:
        df['year'] = pd.to_datetime(df['sale_date']).dt.year
        df['month'] = pd.to_datetime(df['sale_date']).dt.month
        df['quarter'] = pd.to_datetime(df['sale_date']).dt.quarter
    except Exception:
        df['year'] = pd.NA
        df['month'] = pd.NA
        df['quarter'] = pd.NA

    # Dedupe
    before_dupe = len(df)
    df = df.drop_duplicates()
    duplicates_removed = before_dupe - len(df)

    # Missing
    missing = df.isna().sum().to_dict()

    # Invalid records: rows with null in required fields
    required = ['sale_id', 'customer_id', 'product_id', 'sale_date']
    invalid = df[df[required].isna().any(axis=1)]
    invalid_count = len(invalid)

    quality = {
        'original_count': original,
        'processed_count': len(df),
        'invalid_count': int(invalid_count),
        'duplicates_removed': int(duplicates_removed),
        'missing_values': missing
    }

    # Drop invalid rows
    df = df.drop(index=invalid.index)

    return df, quality


def transform_customers(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    original = len(df)
    df = df.rename(columns=lambda x: x.strip())
    # Basic required fields
    if 'customer_id' not in df.columns:
        df['customer_id'] = df.get('id')
    df = df.drop_duplicates(subset=['customer_id'])
    duplicates_removed = original - len(df)
    missing = df.isna().sum().to_dict()
    quality = {'original_count': original, 'processed_count': len(df), 'duplicates_removed': int(duplicates_removed), 'missing_values': missing}
    return df, quality


def transform_products(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    original = len(df)
    df = df.rename(columns=lambda x: x.strip())
    if 'id' in df.columns and 'product_id' not in df.columns:
        df['product_id'] = df['id'].astype(str)
    df = df.drop_duplicates(subset=['product_id'])
    duplicates_removed = original - len(df)
    missing = df.isna().sum().to_dict()
    quality = {'original_count': original, 'processed_count': len(df), 'duplicates_removed': int(duplicates_removed), 'missing_values': missing}
    return df, quality
