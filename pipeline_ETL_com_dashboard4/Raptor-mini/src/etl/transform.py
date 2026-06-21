from __future__ import annotations

import pandas as pd
from pandas import DataFrame

from .logger import get_logger

logger = get_logger(__name__)


def standardize_dates(df: DataFrame, column: str) -> DataFrame:
    logger.debug("Standardizing dates for %s", column)
    df[column] = pd.to_datetime(df[column], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


def clean_sales_data(sales_df: DataFrame) -> DataFrame:
    logger.info("Cleaning sales data")
    sales_df = sales_df.copy()
    sales_df = sales_df.drop_duplicates()
    sales_df = standardize_dates(sales_df, "sale_date")
    sales_df["quantity"] = pd.to_numeric(sales_df["quantity"], errors="coerce")
    sales_df["unit_price"] = pd.to_numeric(sales_df["unit_price"], errors="coerce")
    sales_df["total_sale_value"] = sales_df["quantity"] * sales_df["unit_price"]
    sales_df["year"] = pd.to_datetime(sales_df["sale_date"], errors="coerce").dt.year
    sales_df["month"] = pd.to_datetime(sales_df["sale_date"], errors="coerce").dt.month
    sales_df["quarter"] = pd.to_datetime(sales_df["sale_date"], errors="coerce").dt.quarter
    return sales_df


def clean_customers_data(customers_df: DataFrame) -> DataFrame:
    logger.info("Cleaning customer data")
    customers_df = customers_df.copy()
    customers_df = customers_df.drop_duplicates(subset=["customer_id"])
    customers_df["customer_id"] = customers_df["customer_id"].astype(str)
    return customers_df


def clean_products_data(products_df: DataFrame) -> DataFrame:
    logger.info("Cleaning product data")
    products_df = products_df.copy()
    products_df = products_df.drop_duplicates(subset=["product_id"])
    products_df["product_id"] = products_df["product_id"].astype(str)
    return products_df


def validate_data_types(df: DataFrame, column_types: dict[str, type]) -> DataFrame:
    for column, dtype in column_types.items():
        logger.debug("Validating %s type as %s", column, dtype.__name__)
        if column in df.columns:
            df[column] = df[column].astype(dtype, errors="ignore")
    return df


def create_derived_metrics(sales_df: DataFrame) -> DataFrame:
    logger.info("Creating derived metrics")
    dframe = sales_df.copy()
    if "quantity" in dframe.columns and "unit_price" in dframe.columns:
        dframe["total_sale_value"] = dframe["quantity"] * dframe["unit_price"]
    dframe["sale_date"] = pd.to_datetime(dframe["sale_date"], errors="coerce")
    dframe["year"] = dframe["sale_date"].dt.year
    dframe["month"] = dframe["sale_date"].dt.month
    dframe["quarter"] = dframe["sale_date"].dt.quarter
    dframe["sale_date"] = dframe["sale_date"].dt.strftime("%Y-%m-%d")
    return dframe


def transform_data(
    sales_df: DataFrame, customers_df: DataFrame, products_df: DataFrame
) -> tuple[DataFrame, DataFrame, DataFrame]:
    sales_clean = clean_sales_data(sales_df)
    customers_clean = clean_customers_data(customers_df)
    products_clean = clean_products_data(products_df)
    sales_clean = validate_data_types(
        sales_clean,
        {
            "sale_id": str,
            "customer_id": str,
            "product_id": str,
            "quantity": float,
            "unit_price": float,
        },
    )
    sales_clean = create_derived_metrics(sales_clean)
    return sales_clean, customers_clean, products_clean
