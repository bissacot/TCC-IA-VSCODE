from sqlalchemy.engine import Engine
import logging
from .db import upsert_table
from typing import List, Dict

logger = logging.getLogger("sales_etl.load")


def load_customers(engine: Engine, df) -> int:
    rows = df.to_dict(orient="records")
    return upsert_table(engine, "customers", rows, pk="customer_id")


def load_products(engine: Engine, df) -> int:
    rows = df.to_dict(orient="records")
    return upsert_table(engine, "products", rows, pk="product_id")


def load_sales(engine: Engine, df) -> int:
    rows = df.to_dict(orient="records")
    return upsert_table(engine, "sales", rows, pk="sale_id")
