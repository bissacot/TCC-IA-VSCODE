import pandas as pd
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger("sales_etl.transform")


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates(subset=["customer_id"]) if "customer_id" in df.columns else df.drop_duplicates()
    df["name"] = df.get("name").fillna("")
    df["email"] = df.get("email").fillna("")
    df["state"] = df.get("state").fillna("")
    return df


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates(subset=["product_id"]) if "product_id" in df.columns else df.drop_duplicates()
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
    return df


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Standardize column names
    df.columns = [c.strip() for c in df.columns]
    # Drop duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["sale_id"]) if "sale_id" in df.columns else df.drop_duplicates()
    removed = before - len(df)
    # Handle numeric fields
    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    if "unit_price" in df.columns:
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0)
    # Parse dates to ISO
    if "sale_date" in df.columns:
        df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    # Derived metrics
    df["total_value"] = df.get("quantity", 0) * df.get("unit_price", 0)
    df["year"] = df["sale_date"].dt.year
    df["month"] = df["sale_date"].dt.month
    df["quarter"] = df["sale_date"].dt.quarter
    logger.info("Cleaned sales: removed %d duplicates", removed)
    return df


def validate_sales(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = df.copy()
    invalid = pd.DataFrame()
    # Simple validation rules
    if "sale_id" in df.columns:
        invalid = df[df["sale_id"].isna()]
        df = df[~df["sale_id"].isna()]
    return df, invalid
