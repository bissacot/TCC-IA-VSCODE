from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from .exceptions import DataValidationException
from .logger import get_logger
from .utils import standardize_date

logger = get_logger(__name__)

REQUIRED_SALES_COLUMNS = [
    "sale_id",
    "customer_id",
    "product_id",
    "sale_date",
    "quantity",
    "unit_price",
    "state",
]

REQUIRED_CUSTOMER_COLUMNS = ["customer_id", "customer_name", "state", "email", "phone"]
REQUIRED_PRODUCT_COLUMNS = ["product_id", "product_name", "category", "unit_price"]


def validate_columns(df: pd.DataFrame, required: list[str], source_name: str) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise DataValidationException(
            f"Missing required columns for {source_name}: {', '.join(missing)}"
        )


def normalize_string(value: Any) -> str | None:
    if pd.isna(value):
        return None
    return str(value).strip()


def transform_sales(df: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
    validate_columns(df, REQUIRED_SALES_COLUMNS, "sales")
    logger.info("Transforming sales records: %s", len(df))

    df = df.copy()
    df = df.replace({"": np.nan, "null": np.nan, "None": np.nan})

    for column in REQUIRED_SALES_COLUMNS:
        if column in ["sale_id", "customer_id", "product_id", "state"]:
            df[column] = df[column].astype(str).str.strip()

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").astype("Int64")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["sale_date"] = df["sale_date"].apply(lambda value: standardize_date(value) if not pd.isna(value) else None)
    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")

    invalid = df[
        df[REQUIRED_SALES_COLUMNS].isna().any(axis=1)
        | df["quantity"].isna()
        | df["unit_price"].isna()
        | df["sale_date"].isna()
    ]

    valid = df.drop(invalid.index).copy()
    duplicates_before = len(valid)
    valid = valid.drop_duplicates(subset=["sale_id"])
    duplicates_removed = duplicates_before - len(valid)

    valid["total_sale_value"] = valid["quantity"].astype(int) * valid["unit_price"]
    valid["year"] = valid["sale_date"].dt.year
    valid["month"] = valid["sale_date"].dt.month
    valid["quarter"] = valid["sale_date"].dt.quarter

    valid["state"] = valid["state"].astype(str).str.title()

    logger.info(
        "Sales transformation complete: %s valid records, %s invalid, %s duplicates removed",
        len(valid),
        len(invalid),
        duplicates_removed,
    )

    return valid, len(invalid), duplicates_removed


def transform_customers(df: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
    validate_columns(df, REQUIRED_CUSTOMER_COLUMNS, "customers")
    logger.info("Transforming customer records: %s", len(df))

    df = df.copy()
    df = df.replace({"": np.nan, "null": np.nan, "None": np.nan})
    df["customer_id"] = df["customer_id"].astype(str).str.strip()
    df["customer_name"] = df["customer_name"].astype(str).str.strip()
    df["state"] = df["state"].astype(str).str.title()
    df["email"] = df["email"].astype(str).str.strip()
    df["phone"] = df["phone"].astype(str).str.strip()

    invalid = df[df[REQUIRED_CUSTOMER_COLUMNS].isna().any(axis=1)]
    valid = df.drop(invalid.index).drop_duplicates(subset=["customer_id"])
    duplicates_removed = len(df) - len(valid)

    logger.info(
        "Customer transformation complete: %s valid records, %s invalid, %s duplicates removed",
        len(valid),
        len(invalid),
        duplicates_removed,
    )

    return valid, len(invalid), duplicates_removed


def transform_products(df: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
    validate_columns(df, REQUIRED_PRODUCT_COLUMNS, "products")
    logger.info("Transforming product records: %s", len(df))

    df = df.copy()
    df = df.replace({"": np.nan, "null": np.nan, "None": np.nan})
    df["product_id"] = df["product_id"].astype(str).str.strip()
    df["product_name"] = df["product_name"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.title()
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    invalid = df[df[REQUIRED_PRODUCT_COLUMNS].isna().any(axis=1)]
    valid = df.drop(invalid.index).drop_duplicates(subset=["product_id"])
    duplicates_removed = len(df) - len(valid)

    logger.info(
        "Product transformation complete: %s valid records, %s invalid, %s duplicates removed",
        len(valid),
        len(invalid),
        duplicates_removed,
    )

    return valid, len(invalid), duplicates_removed


def compile_quality_report(
    sales_raw: pd.DataFrame,
    customer_raw: pd.DataFrame,
    product_raw: pd.DataFrame,
    sales_invalid: int,
    customer_invalid: int,
    product_invalid: int,
    duplicates_removed: int,
) -> dict[str, Any]:
    report = {
        "sales_processed": len(sales_raw),
        "customers_processed": len(customer_raw),
        "products_processed": len(product_raw),
        "invalid_records": sales_invalid + customer_invalid + product_invalid,
        "duplicates_removed": duplicates_removed,
        "missing_values_percentage": float(
            (
                sales_raw.isna().sum().sum()
                + customer_raw.isna().sum().sum()
                + product_raw.isna().sum().sum()
            )
            / max(1, sales_raw.size + customer_raw.size + product_raw.size)
            * 100
        ),
    }
    logger.info("Compiled quality report: %s", report)
    return report
