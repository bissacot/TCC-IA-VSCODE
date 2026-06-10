from __future__ import annotations

from typing import Tuple
import pandas as pd
from loguru import logger


REQUIRED_SALES_COLS = ["sale_id", "customer_id", "product_id", "quantity", "price", "sale_date", "state"]


def clean_sales(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    report: dict = {"initial_records": len(df)}

    # Deduplicate
    before_dup = len(df)
    df = df.drop_duplicates()
    after_dup = len(df)
    report["duplicates_removed"] = before_dup - after_dup

    # Ensure required columns
    missing_cols = [c for c in REQUIRED_SALES_COLS if c not in df.columns]
    if missing_cols:
        logger.warning("Missing sales columns: {}", missing_cols)
        for c in missing_cols:
            df[c] = None

    # Type conversions
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0).astype(float)

    # Parse dates
    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    df["sale_date_iso"] = df["sale_date"].dt.strftime("%Y-%m-%dT%H:%M:%S")

    # Derived metrics
    df["total_value"] = df["quantity"] * df["price"]
    df["year"] = df["sale_date"].dt.year
    df["month"] = df["sale_date"].dt.month
    df["quarter"] = df["sale_date"].dt.quarter

    # Missing values report
    report["final_records"] = len(df)
    report["missing_values_percent"] = (df.isna().sum().sum() / (df.shape[0] * df.shape[1])) * 100

    # Invalid records: where sale_date is NaT or customer_id/product_id missing
    invalid_mask = df["sale_date"].isna() | df["customer_id"].isna() | df["product_id"].isna()
    report["invalid_records"] = int(invalid_mask.sum())

    # Filter out invalid
    df = df[~invalid_mask].copy()

    return df, report


def clean_customers(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    report = {"initial_records": len(df)}
    df = df.drop_duplicates()
    report["duplicates_removed"] = report["initial_records"] - len(df)

    # Basic normalization
    if "customer_id" not in df.columns:
        df["customer_id"] = None
    report["final_records"] = len(df)
    report["missing_values_percent"] = (df.isna().sum().sum() / (df.shape[0] * df.shape[1])) * 100
    report["invalid_records"] = int(df["customer_id"].isna().sum())
    df = df[df["customer_id"].notna()].copy()
    return df, report


def clean_products(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    report = {"initial_records": len(df)}
    df = df.drop_duplicates()
    report["duplicates_removed"] = report["initial_records"] - len(df)
    report["final_records"] = len(df)
    report["missing_values_percent"] = (df.isna().sum().sum() / (df.shape[0] * df.shape[1])) * 100
    return df, report
