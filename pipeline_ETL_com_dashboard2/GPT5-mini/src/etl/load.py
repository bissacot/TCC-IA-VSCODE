from __future__ import annotations

from typing import List, Dict, Any
from sqlalchemy import create_engine, Table, Column, MetaData, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError
from sqlalchemy import String, Integer, Numeric, DateTime
from src.config import settings
from src.utils.logging_config import configure_logging
import pandas as pd

logger = configure_logging()


def get_engine():
    return create_engine(settings.postgres_url)


def create_tables_if_not_exist(engine=None):
    engine = engine or get_engine()
    with engine.begin() as conn:
        sql = open("sql/create_tables.sql", "r", encoding="utf-8").read()
        conn.execute(text(sql))


def upsert_customers(customers: List[Dict[str, Any]], engine=None):
    engine = engine or get_engine()
    df = pd.json_normalize(customers)
    df = df.rename(columns={"id": "customer_id"})
    metadata = MetaData()
    customers_tbl = Table(
        "customers",
        metadata,
        Column("customer_id", String, primary_key=True),
    )
    with engine.begin() as conn:
        for _, row in df.iterrows():
            stmt = text(
                "INSERT INTO customers (customer_id, name, email, state, raw) VALUES (:cid, :name, :email, :state, :raw) ON CONFLICT (customer_id) DO UPDATE SET name = EXCLUDED.name, email = EXCLUDED.email, state = EXCLUDED.state, raw = EXCLUDED.raw"
            )
            conn.execute(
                stmt,
                {
                    "cid": str(row.get("customer_id", row.get("id"))),
                    "name": row.get("name"),
                    "email": row.get("email"),
                    "state": row.get("state"),
                    "raw": row.to_json(),
                },
            )


def upsert_products(products: List[Dict[str, Any]], engine=None):
    engine = engine or get_engine()
    df = pd.json_normalize(products)
    with engine.begin() as conn:
        for _, row in df.iterrows():
            stmt = text(
                "INSERT INTO products (product_id, name, category, price, raw) VALUES (:pid, :name, :category, :price, :raw) ON CONFLICT (product_id) DO UPDATE SET name = EXCLUDED.name, category = EXCLUDED.category, price = EXCLUDED.price, raw = EXCLUDED.raw"
            )
            conn.execute(
                stmt,
                {
                    "pid": str(row.get("product_id", row.get("id"))),
                    "name": row.get("name"),
                    "category": row.get("category"),
                    "price": row.get("price", 0),
                    "raw": row.to_json(),
                },
            )


def upsert_sales(df: pd.DataFrame, engine=None):
    engine = engine or get_engine()
    df = df.fillna({})
    with engine.begin() as conn:
        for _, row in df.iterrows():
            stmt = text(
                "INSERT INTO sales (sale_id, customer_id, product_id, quantity, unit_price, total_value, sale_date, year, month, quarter, state, raw) VALUES (:sid, :cid, :pid, :qty, :unit, :total, :sdate, :year, :month, :quarter, :state, :raw) ON CONFLICT (sale_id) DO UPDATE SET customer_id=EXCLUDED.customer_id, product_id=EXCLUDED.product_id, quantity=EXCLUDED.quantity, unit_price=EXCLUDED.unit_price, total_value=EXCLUDED.total_value, sale_date=EXCLUDED.sale_date, year=EXCLUDED.year, month=EXCLUDED.month, quarter=EXCLUDED.quarter, state=EXCLUDED.state, raw=EXCLUDED.raw"
            )
            conn.execute(
                stmt,
                {
                    "sid": str(row.get("sale_id")),
                    "cid": str(row.get("customer_id")),
                    "pid": str(row.get("product_id")),
                    "qty": int(row.get("quantity", 0)),
                    "unit": float(row.get("unit_price", 0.0)),
                    "total": float(row.get("total_value", 0.0)),
                    "sdate": row.get("sale_date"),
                    "year": int(row.get("year", 0)) if row.get("year") is not None else None,
                    "month": int(row.get("month", 0)) if row.get("month") is not None else None,
                    "quarter": int(row.get("quarter", 0)) if row.get("quarter") is not None else None,
                    "state": row.get("state"),
                    "raw": row.to_json(),
                },
            )


def save_etl_metadata(key: str, value: str, engine=None):
    engine = engine or get_engine()
    with engine.begin() as conn:
        stmt = text(
            "INSERT INTO etl_metadata (key, value) VALUES (:k, :v) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value"
        )
        conn.execute(stmt, {"k": key, "v": value})


def read_etl_metadata(key: str, engine=None) -> str | None:
    engine = engine or get_engine()
    with engine.begin() as conn:
        r = conn.execute(text("SELECT value FROM etl_metadata WHERE key = :k"), {"k": key}).fetchone()
        return r[0] if r else None
