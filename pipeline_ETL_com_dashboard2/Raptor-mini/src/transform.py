from datetime import datetime
from typing import Any
import pandas as pd
from pandas import DataFrame
from src.logger import logger


def standardize_date_column(df: DataFrame, date_column: str) -> DataFrame:
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    df[date_column] = df[date_column].dt.date
    return df


def validate_sales(df: DataFrame) -> tuple[DataFrame, DataFrame]:
    df = df.copy()
    initial_count = len(df)
    df = df.drop_duplicates()
    duplicates = initial_count - len(df)
    missing_before = df.isna().sum().sum()

    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["total_sale_value"] = df["quantity"] * df["unit_price"]

    df["year"] = df["sale_date"].dt.year
    df["month"] = df["sale_date"].dt.month
    df["quarter"] = df["sale_date"].dt.quarter

    valid_mask = (
        df["sale_id"].notna()
        & df["customer_id"].notna()
        & df["product_id"].notna()
        & df["sale_date"].notna()
        & df["quantity"].ge(0)
        & df["unit_price"].gt(0)
    )
    valid_df = df[valid_mask].copy()
    invalid_df = df[~valid_mask].copy()

    logger.info(
        "Validated sales: %d valid, %d invalid, %d duplicates removed, %d missing values",
        len(valid_df),
        len(invalid_df),
        duplicates,
        missing_before,
    )
    return valid_df, invalid_df


def transform_customers(df: DataFrame) -> DataFrame:
    df = df.copy()
    df = df.drop_duplicates(subset=["customer_id"])
    df["name"] = df["name"].fillna("Unknown")
    df["email"] = df["email"].fillna("")
    logger.info("Transformed %d customer records", len(df))
    return df


def transform_products(df: DataFrame) -> DataFrame:
    df = df.copy()
    df = df.drop_duplicates(subset=["product_id"])
    df["product_name"] = df["product_name"].fillna("Unknown")
    df["category"] = df["category"].fillna("Uncategorized")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
    logger.info("Transformed %d product records", len(df))
    return df


def create_quality_report(sales_df: DataFrame, invalid_df: DataFrame, customers_df: DataFrame, products_df: DataFrame, duplicates_removed: int) -> dict[str, Any]:
    missing_values = sales_df.isna().sum().sum() + customers_df.isna().sum().sum() + products_df.isna().sum().sum()
    total_processed = len(sales_df) + len(customers_df) + len(products_df)
    invalid_records = len(invalid_df)
    report = {
        "total_processed_records": total_processed,
        "invalid_records": invalid_records,
        "missing_values": int(missing_values),
        "duplicates_removed": int(duplicates_removed),
        "missing_percentage": round((missing_values / max(total_processed, 1)) * 100, 2),
    }
    logger.info("Data quality report: %s", report)
    return report
