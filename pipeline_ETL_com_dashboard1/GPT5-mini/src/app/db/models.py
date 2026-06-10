from __future__ import annotations

from typing import Any
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    create_engine,
)
from sqlalchemy.dialects.postgresql import JSONB

metadata = MetaData()

customers = Table(
    "customers",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("customer_id", String, unique=True, nullable=False),
    Column("name", String),
    Column("email", String),
    Column("state", String),
    Column("extra", JSONB),
)

products = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("product_id", String, unique=True, nullable=False),
    Column("name", String),
    Column("category", String),
    Column("price", Float),
    Column("extra", JSONB),
)

sales = Table(
    "sales",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sale_id", String, unique=True, nullable=False),
    Column("customer_id", String, ForeignKey("customers.customer_id")),
    Column("product_id", String, ForeignKey("products.product_id")),
    Column("quantity", Integer),
    Column("price", Float),
    Column("total_value", Float),
    Column("sale_date", DateTime),
    Column("state", String),
    Column("year", Integer),
    Column("month", Integer),
    Column("quarter", Integer),
)
