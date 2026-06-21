from __future__ import annotations

import pandas as pd

from .config import logger


def standardize_dates(df: pd.DataFrame, date_columns: list[str]) -> pd.DataFrame:
    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


def validate_and_clean_sales(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    logger.info("Validating sales data")
    before = len(df)
    duplicates = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    invalid_date = df["sale_date"].isna()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    invalid_amount = df["quantity"].isna() | df["price"].isna()
    invalid_rows = df[invalid_date | invalid_amount].copy()
    df = df[~(invalid_date | invalid_amount)].copy()
    df["sale_date"] = df["sale_date"].dt.strftime("%Y-%m-%d")
    df["total_sale_value"] = df["quantity"] * df["price"]
    df["sale_year"] = pd.to_datetime(df["sale_date"]).dt.year
    df["sale_month"] = pd.to_datetime(df["sale_date"]).dt.month
    df["sale_quarter"] = pd.to_datetime(df["sale_date"]).dt.quarter
    invalid_records = len(invalid_rows)
    logger.info(
        "Sales records before=%d after=%d duplicates=%d invalid=%d",
        before,
        len(df),
        duplicates,
        invalid_records,
    )
    return df, invalid_rows, duplicates


def validate_and_clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Validating customer data")
    df = df.drop_duplicates(subset=["customer_id"])
    df["state"] = df["state"].fillna("Unknown")
    return df


def validate_and_clean_products(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Validating product data")
    df = df.drop_duplicates(subset=["product_id"])
    df["category"] = df["category"].fillna("Unknown")
    return df
