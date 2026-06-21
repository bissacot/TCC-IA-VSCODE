from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd


def remove_duplicates(df: pd.DataFrame, subset: list[str]) -> tuple[pd.DataFrame, int]:
    count_before = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep="first")
    return df_clean, count_before - len(df_clean)


def standardize_date(date_value: Any) -> datetime | None:
    if pd.isna(date_value):
        return None
    return pd.to_datetime(date_value, errors="coerce").normalize()


def transform_customers(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int] | None]:
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(columns={"id": "customer_id", "name": "customer_name"})
    initial = len(df)
    df = df.dropna(subset=["customer_id", "customer_name"])
    df["created_at"] = df["created_at"].apply(standardize_date)
    df, duplicates = remove_duplicates(df, ["customer_id"])
    metrics = {
        "processed_records": len(df),
        "invalid_records": initial - len(df),
        "duplicates_removed": duplicates,
        "missing_values": int(df.isna().sum().sum()),
    }
    return df, metrics


def transform_products(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int] | None]:
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(columns={"id": "product_id", "name": "product_name"})
    initial = len(df)
    df = df.dropna(subset=["product_id", "product_name", "price"])
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    df["created_at"] = df["created_at"].apply(standardize_date)
    df, duplicates = remove_duplicates(df, ["product_id"])
    metrics = {
        "processed_records": len(df),
        "invalid_records": initial - len(df),
        "duplicates_removed": duplicates,
        "missing_values": int(df.isna().sum().sum()),
    }
    return df, metrics


def transform_sales(df: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int] | None]:
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(
        columns={
            "id": "sale_id",
            "date": "sale_date",
            "customerid": "customer_id",
            "productid": "product_id",
            "qty": "quantity",
            "price": "unit_price",
            "state": "state",
        }
    )
    initial = len(df)
    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").astype("Int64")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["total_value"] = df["quantity"] * df["unit_price"]
    df = df.dropna(subset=["sale_id", "sale_date", "customer_id", "product_id", "quantity", "unit_price"])
    df["year"] = df["sale_date"].dt.year
    df["month"] = df["sale_date"].dt.month
    df["quarter"] = df["sale_date"].dt.quarter
    df = df.merge(products[["product_id", "category"]], on="product_id", how="left")
    df = df.merge(customers[["customer_id", "state"]], on="customer_id", how="left")
    df, duplicates = remove_duplicates(df, ["sale_id"])
    metrics = {
        "processed_records": len(df),
        "invalid_records": initial - len(df),
        "duplicates_removed": duplicates,
        "missing_values": int(df.isna().sum().sum()),
    }
    return df, metrics
