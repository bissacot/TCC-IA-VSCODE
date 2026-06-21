from __future__ import annotations

import pandas as pd
import psycopg

from .config import DATABASE_CONFIG, logger


def load_table(df: pd.DataFrame, table_name: str, key_columns: list[str]) -> None:
    logger.info("Loading %s rows into %s", len(df), table_name)
    with psycopg.connect(DATABASE_CONFIG.dsn()) as conn:
        with conn.cursor() as cur:
            cols = ", ".join(df.columns)
            placeholders = ", ".join([f"%({col})s" for col in df.columns])
            sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders}) ON CONFLICT ({', '.join(key_columns)}) DO UPDATE SET "
            sql += ", ".join([f"{col}=EXCLUDED.{col}" for col in df.columns if col not in key_columns])
            cur.executemany(sql, df.to_dict(orient="records"))
        conn.commit()


def load_sales(df: pd.DataFrame) -> None:
    load_table(df, "sales", ["sale_id"])


def load_customers(df: pd.DataFrame) -> None:
    load_table(df, "customers", ["customer_id"])


def load_products(df: pd.DataFrame) -> None:
    load_table(df, "products", ["product_id"])
