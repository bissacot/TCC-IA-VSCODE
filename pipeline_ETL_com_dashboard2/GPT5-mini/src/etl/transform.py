from __future__ import annotations

import pandas as pd
from typing import Tuple
import numpy as np
from datetime import datetime


def standardize_dates(df: pd.DataFrame, date_col: str = "sale_date") -> pd.DataFrame:
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    return df


def derive_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # total value
    if "quantity" in df.columns and "unit_price" in df.columns:
        df["total_value"] = df["quantity"].fillna(0) * df["unit_price"].fillna(0)
    # year, month, quarter
    if "sale_date" in df.columns:
        df["year"] = df["sale_date"].dt.year
        df["month"] = df["sale_date"].dt.month
        df["quarter"] = df["sale_date"].dt.quarter
    return df


def handle_missing_and_types(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = df.copy()
    # simple type coercion
    df["quantity"] = pd.to_numeric(df.get("quantity", pd.Series()), errors="coerce").fillna(0).astype(int)
    df["unit_price"] = pd.to_numeric(df.get("unit_price", pd.Series()), errors="coerce").fillna(0.0)
    # drop rows with missing sale_id
    invalid = df[df["sale_id"].isna()]
    df = df[df["sale_id"].notna()]
    return df, invalid


def remove_duplicates(df: pd.DataFrame, subset: list = None) -> Tuple[pd.DataFrame, int]:
    subset = subset or ["sale_id"]
    before = len(df)
    df2 = df.drop_duplicates(subset=subset)
    removed = before - len(df2)
    return df2, removed


def transform_sales(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    df = standardize_dates(df)
    df, invalid = handle_missing_and_types(df)
    df = derive_metrics(df)
    df, removed = remove_duplicates(df, subset=["sale_id"])
    report = {
        "processed": int(len(df) + len(invalid)),
        "invalid": int(len(invalid)),
        "duplicates_removed": int(removed),
        "missing_pct": float(df.isna().mean().mean()),
    }
    return df, report
